#!/usr/bin/env python3
"""Modal T4 runner for Phase K — the SAME stack Phases 0–2 ran on (HF + bnb NF4 +
Qwen2.5-Coder-1.5B), lifted onto rented Modal T4. NO fp16, NO vLLM (that is Phase M).

Usage (token from rgr-modal.txt, set as env vars by the caller):
  modal run scripts/modal_rgr.py --stage           # build .modal_stage/ then no-op
  modal run scripts/modal_rgr.py::k1 --n 20         # GATE K1 replay -> compare locally

Image pinned to env/kaggle_phase0_2.lock (reconciled: torch 2.9 for GPU numerics;
env/CAPTURE.md). GATE K1 verifies the pin faithfulness against lock_a.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import modal

REPO = Path(__file__).parents[1]
STAGE = REPO / ".modal_stage"

# Artifacts the Modal container needs, staged under .modal_stage/ mirroring repo layout.
NEED = {
    "src": "src",
    "configs": "configs",
    "data/cache": "data/cache",
    "rgb-daytona.txt": "rgb-daytona.txt",
    "runs/kaggle/phase1_v2b/runs/phase1_v2b/lora": "artifacts/v2b_lora",
    "runs/kaggle/phase2_train/runs/phase2/register_modules.pt": "artifacts/register_modules.pt",
    "runs/kaggle/phase1_data/runs/phase1/phi": "artifacts/phase1_phi",
    "runs/kaggle/phase1_data/runs/phase1/phi_problems": "artifacts/phase1_phi_problems",
    "runs/kaggle/phase1_data/runs/phase1/labels.jsonl": "artifacts/phase1_labels.jsonl",
    "runs/kaggle/phase2_score/runs/phase2/v_scores.json": "artifacts/v_scores.json",
    "runs/kaggle/phase1_v2b/runs/phase1_v2b/heldout_scores.json": "artifacts/heldout_scores.json",
}


def stage() -> None:
    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)
    for src, dst in NEED.items():
        s, d = REPO / src, STAGE / dst
        if not s.exists():
            raise SystemExit(f"missing staging source: {src}")
        d.parent.mkdir(parents=True, exist_ok=True)
        (shutil.copytree if s.is_dir() else shutil.copy)(s, d)
    print(f"staged -> {STAGE} ({sum(f.stat().st_size for f in STAGE.rglob('*') if f.is_file())/1e6:.1f} MB)")


# Stage before defining the image (add_local_dir reads .modal_stage at build).
if any(a in sys.argv for a in ("run", "k1", "--stage")) or __name__ == "__main__":
    if not STAGE.exists():
        stage()

# Reconciled pins (env/CAPTURE.md): torch 2.9 = GPU-stack numerics (capture was CPU 2.10).
IMAGE = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install(
        "torch==2.9.0",
        "transformers==5.0.0",
        "bitsandbytes==0.49.2",
        "accelerate==1.13.0",
        "peft==0.19.1",
        "numpy==2.0.2",
        "datasets==5.0.0",
        "tokenizers==0.22.2",
        "safetensors==0.7.0",
        "huggingface_hub==1.11.0",
    )
    .env({"PYTHONPATH": "/root/rgr/src", "HF_HOME": "/cache/hf", "TOKENIZERS_PARALLELISM": "false"})
    .add_local_dir(str(STAGE), "/root/rgr")
)

VOL = modal.Volume.from_name("rgr-hf-cache", create_if_missing=True)
app = modal.App("rgr-phasek")


@app.function(image=IMAGE, gpu="T4", volumes={"/cache": VOL}, timeout=3600)
def k1(n: int = 20) -> list[dict]:
    """Replay the first n Phase-0 HumanEval problems on Modal T4, EXACT phase0
    code path (set_seed 17 → run_refine, freeze_register, null register, t_max=8).
    Returns per-problem candidate texts/codes for byte comparison vs lock_a.
    No execution — generation only."""
    import os
    import random

    os.chdir("/root/rgr")
    import torch

    from rgr.config import load_config
    from rgr.data.humaneval import load_humaneval
    from rgr.generator.model import Generator
    from rgr.loop.interfaces import NoRegister
    from rgr.loop.refine import run_refine
    from rgr.types import SplitRole
    from rgr.verifier.likelihood import LikelihoodScorer

    config = load_config("configs/phase0_harness.toml")
    random.seed(config.run.seed)
    torch.manual_seed(config.run.seed)  # exactly set_seed()

    gen = Generator(config.generator)
    print(f"loading {config.generator.model_name} (4bit={config.generator.load_4bit}) on T4 ...", flush=True)
    gen.load()
    scorer = LikelihoodScorer()
    null = NoRegister()
    problems = load_humaneval().checkout(SplitRole.HELDOUT_EVAL)[:n]

    out = []
    for i, p in enumerate(problems):
        traj = run_refine(p, gen, scorer, null, null,
                          t_max=config.loop.t_max, freeze_register=True,
                          condition="b1_likelihood")
        out.append({
            "problem_id": p.problem_id,
            "texts": [s.candidate.text for s in traj.steps],
            "codes": [s.candidate.code for s in traj.steps],
        })
        print(f"  {i+1}/{n} {p.problem_id}", flush=True)
    return out


@app.local_entrypoint()
def main(n: int = 20):
    """Run K1 on Modal, save, and compare byte-for-byte to lock_a locally."""
    records = k1.remote(n)
    outdir = REPO / "runs" / "modal"
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "k1_replay.json").write_text(json.dumps(records, indent=2))

    lock = {r["problem_id"]: r for r in
            (json.loads(l) for l in open(REPO / "artifacts/lock_a.jsonl"))}
    print(f"\n=== GATE K1 — byte comparison vs lock_a ({len(records)} problems) ===")
    exact = 0
    first_div = []
    for r in records:
        pid = r["problem_id"]
        old = lock.get(pid)
        if not old:
            print(f"  {pid}: NOT IN lock_a"); continue
        old_texts = [s["text"] for s in old["steps"]]
        match = r["texts"] == old_texts
        exact += match
        if not match:
            # locate first diverging (step, char)
            for si, (a, b) in enumerate(zip(r["texts"], old_texts)):
                if a != b:
                    j = next((k for k in range(min(len(a), len(b))) if a[k] != b[k]), min(len(a), len(b)))
                    first_div.append((pid, si, j))
                    break
    print(f"byte-identical problems: {exact}/{len(records)}")
    if first_div:
        chars = sorted(j for _, _, j in first_div)
        print("first divergences (problem, step, char-index):")
        for pid, si, j in first_div[:10]:
            print(f"  {pid} step{si} @char {j}")
        print(f"divergence char-index: min {chars[0]}, median {chars[len(chars)//2]}, max {chars[-1]}")
    # NOTE: byte-for-byte across non-bit-identical stacks diverges under temp>0
    # sampling by construction. The gate call is drift-vs-systematic, and needs
    # INSPECTION of the divergent text (coherent code = drift; garbage/quality
    # collapse or all-diverge-at-token-1 = systematic). >=1 full-problem match is
    # strong evidence of near-identical numerics (8 stochastic candidates aligned).
    print(f"K1: {exact}/{len(records)} byte-identical, {len(first_div)} coherent-drift "
          f"candidates (INSPECT divergent text before ruling drift vs systematic).")
