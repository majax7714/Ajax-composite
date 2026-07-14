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
sys.path.insert(0, str(REPO / "src"))  # local entrypoints import pure-stdlib rgr.evals

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
    "runs/kaggle/lock_a/runs/phase0/lock_a.jsonl": "artifacts/lock_a.jsonl",
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
        "daytona",  # sandbox execution for DIAG-2/3 pass labels (matches Kaggle runner)
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


def _load_config_and_gen():
    import os

    os.chdir("/root/rgr")
    import torch

    from rgr.config import load_config
    from rgr.generator.model import Generator
    config = load_config("configs/phase2_register.toml")
    torch.manual_seed(config.run.seed)
    gen = Generator(config.generator)
    print(f"loading {config.generator.model_name} (4bit={config.generator.load_4bit}) ...", flush=True)
    gen.load()
    return config, gen


def _build_register_modules(config, gen, trained: bool):
    """Trained (from register_modules.pt) or untrained (seed-17 init, == training
    base_val). Mirrors load_register_stack / stage_train construction exactly."""
    import torch

    from rgr.generator.injection import RegisterInjector
    from rgr.register.encoder import ProblemRegisterEncoder
    from rgr.register.update import RegisterUpdate
    d_r, k_soft, d_model = config.register.d_r, config.register.k_soft_tokens, gen.d_model
    torch.manual_seed(config.run.seed)  # deterministic init (== stage_train base_val)
    inj = RegisterInjector(d_r, k_soft, d_model).to(gen.device).float()
    enc = ProblemRegisterEncoder(d_r, d_model, embed_problem=gen.embed_problem).to(gen.device).float()
    upd = RegisterUpdate(d_r, d_model, rms_normalize=config.register.rms_normalize,
                         max_update_norm=config.register.max_update_norm).to(gen.device).float()
    if trained:
        ck = torch.load("artifacts/register_modules.pt", weights_only=True, map_location=gen.device)
        inj.load_state_dict(ck["modules"]["injector"])
        enc.proj.load_state_dict(ck["modules"]["w0"])
        upd.load_state_dict(ck["modules"]["updater"])
    for m in (inj, enc, upd):
        m.eval()
    return inj, enc, upd


@app.function(image=IMAGE, gpu="T4", volumes={"/cache": VOL}, timeout=5400)
def nll_diag(cap: int = 200):
    """DIAG-5 (transfer) + DIAG-4 item 3 (entropy split). r_0 (k=0) teacher-forced
    per-token NLL of passing candidates under trained vs untrained soft prompt, on
    MBPP-val and HumanEval. Forward passes only — no generation, no execution."""
    import json

    import numpy as np
    import torch

    from rgr.data.humaneval import load_humaneval
    from rgr.data.mbpp import load_mbpp
    from rgr.generator.formatting import SYSTEM_PROMPT, build_prompt
    from rgr.types import SplitRole

    config, gen = _load_config_and_gen()
    model, tok = gen._model, gen._tokenizer
    device = gen.device
    embed_layer = model.get_input_embeddings()
    inj_t, enc_t, _ = _build_register_modules(config, gen, trained=True)
    inj_u, enc_u, _ = _build_register_modules(config, gen, trained=False)
    max_new = config.generator.max_new_tokens

    def chat_ids(prompt_text):
        msgs = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_prompt(prompt_text)}]
        enc = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt")
        return getattr(enc, "input_ids", enc)[0].to(device)

    @torch.no_grad()
    def per_token_nll(problem, target_text, inj, enc):
        r0 = enc.init(problem)  # (d_r,)  r_0 = W_0·phi(problem)
        soft = inj(r0.unsqueeze(0)).to(model.dtype)[0]  # (k_soft, d_model)
        p_ids = chat_ids(problem.prompt)
        t_ids = tok(target_text, return_tensors="pt", add_special_tokens=False,
                    truncation=True, max_length=max_new).input_ids[0].to(device)
        if len(t_ids) < 2:
            return None
        ids = torch.cat([p_ids, t_ids])
        embeds = torch.cat([soft, embed_layer(ids)]).unsqueeze(0)
        logits = model(inputs_embeds=embeds).logits[0].float()
        start = soft.shape[0] + len(p_ids)          # first target position
        pred = logits[start - 1:start - 1 + len(t_ids)]  # logits predicting each target token
        logp = torch.log_softmax(pred, -1)
        return (-logp[range(len(t_ids)), t_ids]).cpu().numpy()

    # ---- candidate pools ----
    mbpp = {p.problem_id: p for p in load_mbpp().problems}
    val_pids = set()
    mbpp_targets = []  # (problem, text)
    for line in open("artifacts/phase1_labels.jsonl"):
        r = json.loads(line)
        if str(r["split"]) == "val" and (r["passed"] is True or str(r["passed"]).lower() == "true") and r.get("text"):
            mbpp_targets.append((mbpp[r["problem_id"]], r["text"]))
            val_pids.add(r["problem_id"])
    he = {p.problem_id: p for p in load_humaneval().checkout(SplitRole.HELDOUT_EVAL)}
    he_targets = []
    for line in open("artifacts/lock_a.jsonl"):
        r = json.loads(line)
        for s in r["steps"]:
            if s["execution"]["passed"] and s.get("text"):
                he_targets.append((he[r["problem_id"]], s["text"]))

    def collect(targets):
        rng = np.random.RandomState(config.run.seed)
        idx = rng.permutation(len(targets))[:cap]
        trained_tok, untr_tok = [], []
        for i in idx:
            problem, text = targets[i]
            nt = per_token_nll(problem, text, inj_t, enc_t)
            nu = per_token_nll(problem, text, inj_u, enc_u)
            if nt is None or nu is None:
                continue
            trained_tok.append(nt); untr_tok.append(nu)
        return trained_tok, untr_tok

    out = {"cap": cap, "n_mbpp": len(mbpp_targets), "n_he": len(he_targets)}
    for name, targets in (("mbpp_val", mbpp_targets), ("humaneval", he_targets)):
        tr, un = collect(targets)
        mean_tr = float(np.mean([t.mean() for t in tr]))
        mean_un = float(np.mean([u.mean() for u in un]))
        # implied seq-prob multiplier at mean length
        mean_len = float(np.mean([len(t) for t in tr]))
        mult = float(np.exp((mean_un - mean_tr) * mean_len))
        out[name] = {"n": len(tr), "mean_len": mean_len,
                     "mean_nll_untrained": mean_un, "mean_nll_trained": mean_tr,
                     "per_token_mult": float(np.exp(mean_un - mean_tr)),
                     "seq_prob_mult_at_mean_len": mult}
        # DIAG-4 item 3 (MBPP val only): entropy split by untrained per-token NLL
        if name == "mbpp_val":
            all_un = np.concatenate(un); all_tr = np.concatenate(tr)
            improve = all_un - all_tr                 # per-token NLL improvement
            med = float(np.median(all_un))
            low = all_un <= med                       # low-entropy (boilerplate) tokens
            tot = float(improve.sum())
            out["diag4_item3"] = {
                "entropy_proxy": "untrained per-token NLL (low = boilerplate)",
                "median_untrained_nll": med,
                "total_improvement": tot,
                "share_on_low_entropy": float(improve[low].sum() / tot) if tot else None,
                "share_on_high_entropy": float(improve[~low].sum() / tot) if tot else None,
                "n_tokens": int(all_un.size),
            }
    return out


@app.local_entrypoint()
def nll_main(cap: int = 200):
    import json as _json
    r = nll_diag.remote(cap)
    (REPO / "artifacts/diag5_transfer.json").write_text(_json.dumps({
        "_label": "EXPLORATORY / POST-HOC (Modal T4, Phase K). r_0(k=0) teacher-forced steering.",
        "mbpp_val": r["mbpp_val"], "humaneval": r["humaneval"],
        "note": "per_token_mult / seq_prob_mult_at_mean_len are untrained->trained. "
                "Transfer = compare mbpp_val vs humaneval multipliers.",
    }, indent=2))
    (REPO / "artifacts/diag4_item3_entropy_split.json").write_text(_json.dumps({
        "_label": "EXPLORATORY / POST-HOC (Modal T4, Phase K). DIAG-4 item 3.",
        **r["diag4_item3"],
    }, indent=2))
    print("\n=== DIAG-5 transfer (r_0 steering, untrained->trained) ===")
    for d in ("mbpp_val", "humaneval"):
        s = r[d]
        print(f"  {d:10s} n={s['n']:4d} len~{s['mean_len']:.0f}  NLL {s['mean_nll_untrained']:.4f}->{s['mean_nll_trained']:.4f}"
              f"  per-tok x{s['per_token_mult']:.3f}  seq x{s['seq_prob_mult_at_mean_len']:.2f}")
    e = r["diag4_item3"]
    print(f"=== DIAG-4 item 3: {e['share_on_low_entropy']*100:.1f}% of the NLL improvement on low-entropy (boilerplate) tokens ===")
    print("wrote artifacts/diag5_transfer.json + artifacts/diag4_item3_entropy_split.json")


@app.function(image=IMAGE, gpu="T4", volumes={"/cache": VOL}, timeout=5400)
def entropy_full():
    """DIAG-4 item 3, FAITHFUL: reproduce the full k~U val_loss (should recover
    0.1713->0.1530) per-token, trained vs untrained, then split the improvement by
    token entropy. Exact stage_train construction (stored phi/v_scores/labels)."""
    import json

    import numpy as np
    import torch

    from rgr.data.mbpp import load_mbpp
    from rgr.generator.formatting import SYSTEM_PROMPT, build_prompt
    from rgr.training.imitation import build_examples

    config, gen = _load_config_and_gen()
    model, tok = gen._model, gen._tokenizer
    device = gen.device
    embed_layer = model.get_input_embeddings()
    inj_t, enc_t, upd_t = _build_register_modules(config, gen, trained=True)
    inj_u, enc_u, upd_u = _build_register_modules(config, gen, trained=False)
    tcfg = config.extra["register_train"]
    per_problem, k_max = int(tcfg.get("examples_per_problem", 12)), int(tcfg.get("k_max", 7))
    max_new = config.generator.max_new_tokens

    def fn(pid):
        return pid.replace("/", "__") + ".npy"
    records = [json.loads(l) for l in open("artifacts/phase1_labels.jsonl")]
    by_pid = {}
    for r in records:
        by_pid.setdefault(r["problem_id"], []).append(r)
    for rows in by_pid.values():
        rows.sort(key=lambda r: int(r["idx"]))
    v_scores = json.load(open("artifacts/v_scores.json"))
    problems = {p.problem_id: p for p in load_mbpp().problems}
    val_pids = {r["problem_id"] for r in records if str(r["split"]) == "val"}
    passed = {pid: [(x["passed"] is True or str(x["passed"]).lower() == "true") for x in by_pid[pid]]
              for pid in val_pids}
    examples = build_examples(passed, per_problem=per_problem, k_max=k_max, seed=config.run.seed)
    phi = {pid: torch.tensor(np.load(f"artifacts/phase1_phi/{fn(pid)}").astype(np.float32)) for pid in val_pids}
    phi_p = {pid: torch.tensor(np.load(f"artifacts/phase1_phi_problems/{fn(pid)}").astype(np.float32)) for pid in val_pids}

    def chat_ids(prompt_text):
        msgs = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_prompt(prompt_text)}]
        e = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt")
        return getattr(e, "input_ids", e)[0].to(device)

    @torch.no_grad()
    def per_token(ex, inj, enc, upd):
        pid = ex.problem_id
        r = enc.proj(phi_p[pid].to(device))  # r_0 = W_0·phi(problem)
        for i in ex.prefix_idx:
            r = upd.forward(r.unsqueeze(0), phi[pid][i].unsqueeze(0).to(device),
                            torch.tensor([float(v_scores[pid][i])], device=device))[0]
        soft = inj(r.unsqueeze(0)).to(model.dtype)[0]
        p_ids = chat_ids(problems[pid].prompt)
        t_ids = tok(by_pid[pid][ex.target_idx]["text"], return_tensors="pt", add_special_tokens=False,
                    truncation=True, max_length=max_new).input_ids[0].to(device)
        if len(t_ids) < 2:
            return None
        ids = torch.cat([p_ids, t_ids])
        logits = model(inputs_embeds=torch.cat([soft, embed_layer(ids)]).unsqueeze(0)).logits[0].float()
        start = soft.shape[0] + len(p_ids)
        logp = torch.log_softmax(logits[start - 1:start - 1 + len(t_ids)], -1)
        return (-logp[range(len(t_ids)), t_ids]).cpu().numpy()

    un_all, tr_all = [], []
    for ex in examples:
        nu = per_token(ex, inj_u, enc_u, upd_u)
        nt = per_token(ex, inj_t, enc_t, upd_t)
        if nu is None or nt is None:
            continue
        un_all.append(nu); tr_all.append(nt)
    mean_un = float(np.mean([u.mean() for u in un_all]))
    mean_tr = float(np.mean([t.mean() for t in tr_all]))
    un = np.concatenate(un_all); tr = np.concatenate(tr_all)
    improve = un - tr
    med = float(np.median(un))
    low = un <= med
    tot = float(improve.sum())
    return {
        "n_examples": len(un_all), "n_tokens": int(un.size),
        "val_mean_nll_untrained": mean_un, "val_mean_nll_trained": mean_tr,
        "reproduces_0.1713_0.1530": [round(mean_un, 4), round(mean_tr, 4)],
        "median_untrained_nll": med, "total_improvement": tot,
        "share_low_entropy": float(improve[low].sum() / tot) if tot else None,
        "share_high_entropy": float(improve[~low].sum() / tot) if tot else None,
        "mean_improve_low": float(improve[low].mean()), "mean_improve_high": float(improve[~low].mean()),
    }


@app.local_entrypoint()
def entropy_main():
    import json as _json
    r = entropy_full.remote()
    (REPO / "artifacts/diag4_item3_entropy_split.json").write_text(_json.dumps(
        {"_label": "EXPLORATORY / POST-HOC (Modal T4, Phase K). DIAG-4 item 3, faithful full k~U val_loss.",
         **r}, indent=2))
    print("\n=== DIAG-4 item 3 (faithful full-prefix) ===")
    print(f"  reproduced val NLL: {r['val_mean_nll_untrained']:.4f} -> {r['val_mean_nll_trained']:.4f} "
          f"(training reported 0.1713 -> 0.1530)")
    print(f"  total improvement {r['total_improvement']:.3f} over {r['n_tokens']} tokens")
    print(f"  share on LOW-entropy (boilerplate) tokens: {r['share_low_entropy']*100:.1f}%")
    print(f"  share on HIGH-entropy (decision) tokens:   {r['share_high_entropy']*100:.1f}%")
    print("wrote artifacts/diag4_item3_entropy_split.json")


@app.function(image=IMAGE, gpu="T4", volumes={"/cache": VOL}, timeout=7200)
def rollout_diag(n_problems: int = 42, m: int = 8):
    """DIAG-2 (register probes) + DIAG-3 (control authority) on MBPP val.
    FULL rollout capturing r_0..r_7 + v; paired r_0/r_7 sampling for edit/KL/
    diversity; inline Daytona execution for pass labels. Trained modules + V-v2b."""
    import difflib
    import json

    import numpy as np
    import torch

    from rgr.data.mbpp import load_mbpp
    from rgr.execution.sandbox import DaytonaBackend
    from rgr.generator.formatting import build_prompt
    from rgr.training.labels import ExecutionPool
    from rgr.verifier.qlora import QloraVerifier

    config, gen = _load_config_and_gen()
    inj, enc, upd = _build_register_modules(config, gen, trained=True)
    gen.injector = inj
    verifier = QloraVerifier(str(REPO_A := "artifacts/v2b_lora"))
    print("loading V-v2b ...", flush=True)
    verifier.load()

    val_pids = [r["problem_id"] for r in map(json.loads, open("artifacts/phase1_labels.jsonl"))
                if str(r["split"]) == "val"]
    val_pids = sorted(set(val_pids))[:n_problems]
    problems = {p.problem_id: p for p in load_mbpp().problems}
    val = [problems[pid] for pid in val_pids if pid in problems]
    print(f"MBPP val: {len(val)} problems", flush=True)

    T = config.loop.t_max
    rows = []           # DIAG-2 probe rows: r_t -> v_{t-1}, passed_{t-1}, t
    d3 = []             # DIAG-3 per-problem
    pool = ExecutionPool(lambda: DaytonaBackend(config.execution.timeout_seconds), size=4)

    @torch.no_grad()
    def kl_first32(problem, r0, r7):
        """KL(P_r0 || P_r7) over first 32 next-token positions, teacher-forced on a
        greedy-ish reference (the r0 sample tokens)."""
        model, tok = gen._model, gen._tokenizer
        emb = model.get_input_embeddings()
        p_ids = tok(build_prompt(problem.prompt), return_tensors="pt").input_ids[0].to(gen.device)

        def logits_for(r):
            soft = inj(r.unsqueeze(0)).to(model.dtype)[0]
            ids = p_ids
            embeds = torch.cat([soft, emb(ids)]).unsqueeze(0)
            lg = model(inputs_embeds=embeds).logits[0].float()
            return lg[-32:]  # last 32 positions' next-token logits (prompt-conditioned)
        a = torch.log_softmax(logits_for(r0), -1)
        b = torch.log_softmax(logits_for(r7), -1)
        kl = (a.exp() * (a - b)).sum(-1)  # per-position KL
        return float(kl.mean())

    try:
        for pi, problem in enumerate(val):
            # ---- FULL rollout, capture r_t + v_t + candidates ----
            r = enc.init(problem)
            regs, vs, cands = [r.detach().float().cpu().numpy()], [], []
            for t in range(T):
                cand = gen.generate(problem, r)
                v = verifier.score(problem, cand, None)
                vs.append(v); cands.append(cand)
                if t < T - 1:
                    r = upd.update(r, cand, v)
                    regs.append(r.detach().float().cpu().numpy())
            passed = [e.passed for e in pool.execute_all(problem, cands)]
            for t in range(1, T):  # probe r_t from previous step's v/passed
                rows.append({"r": regs[t].tolist(), "v_prev": vs[t - 1],
                             "passed_prev": int(passed[t - 1]), "t": t})

            # ---- DIAG-3: paired r_0 vs r_7 sampling ----
            r0 = enc.init(problem)
            r7 = torch.tensor(regs[-1], device=gen.device)
            s0 = gen.sample_batch(build_prompt(problem.prompt), m, register=r0)
            s7 = gen.sample_batch(build_prompt(problem.prompt), m, register=r7)
            p0 = [e.passed for e in pool.execute_all(problem, s0)]
            p7 = [e.passed for e in pool.execute_all(problem, s7)]

            def div(cands_):
                codes = [c.code or c.text for c in cands_]
                sims = [difflib.SequenceMatcher(None, codes[i], codes[j]).ratio()
                        for i in range(len(codes)) for j in range(i + 1, len(codes))]
                return 1.0 - (sum(sims) / len(sims) if sims else 1.0)  # mean normalized edit distance

            def cross(a, b):
                ca = [c.code or c.text for c in a]; cb = [c.code or c.text for c in b]
                sims = [difflib.SequenceMatcher(None, x, y).ratio() for x in ca for y in cb]
                return 1.0 - sum(sims) / len(sims)
            d3.append({
                "within_r0": div(s0), "within_r7": div(s7), "across": cross(s0, s7),
                "pass_r0": sum(p0) / m, "pass_r7": sum(p7) / m,
                "kl_r0_r7": kl_first32(problem, r0, r7),
            })
            if (pi + 1) % 10 == 0:
                print(f"  {pi+1}/{len(val)} problems", flush=True)
    finally:
        pool.close()
    return {"probe_rows": rows, "diag3": d3, "n_problems": len(val), "T": T, "m": m}


@app.local_entrypoint()
def rollout_main(n_problems: int = 42, m: int = 8):
    import json as _json

    import numpy as np

    from rgr.evals.calibration import auroc

    r = rollout_diag.remote(n_problems, m)
    (REPO / "runs/modal").mkdir(parents=True, exist_ok=True)
    (REPO / "runs/modal/rollout_diag.json").write_text(_json.dumps(r))

    # ---- DIAG-2 probes: 5-fold CV ridge r_t -> target ----
    rows = r["probe_rows"]
    X = np.array([row["r"] for row in rows], float)
    X = (X - X.mean(0)) / (X.std(0) + 1e-8)
    n = len(X)
    rng = np.random.RandomState(17)
    folds = rng.permutation(n) % 5

    def cv_predict(y, lam=10.0):
        pred = np.zeros(n)
        for f in range(5):
            tr, te = folds != f, folds == f
            Xt, yt = X[tr], y[tr]
            w = np.linalg.solve(Xt.T @ Xt + lam * np.eye(X.shape[1]), Xt.T @ yt)
            pred[te] = X[te] @ w
        return pred

    def r2(y, p):
        return float(1 - ((y - p) ** 2).sum() / (((y - y.mean()) ** 2).sum() + 1e-12))

    v_prev = np.array([row["v_prev"] for row in rows], float)
    passed_prev = np.array([row["passed_prev"] for row in rows], float)
    tvar = np.array([row["t"] for row in rows], float)
    diag2 = {
        "n_probe_rows": n,
        "v_prev_R2_cv": r2(v_prev, cv_predict(v_prev)),
        "passed_prev_AUROC_cv": (auroc(list(cv_predict(passed_prev)), [bool(x) for x in passed_prev])
                                 if len(set(passed_prev)) == 2 else None),
        "t_R2_cv": r2(tvar, cv_predict(tvar)),
        "base_rate_passed_prev": float(passed_prev.mean()),
    }
    (REPO / "artifacts/diag2_register_probes.json").write_text(_json.dumps(
        {"_label": "EXPLORATORY / POST-HOC (Modal T4, Phase K). 5-fold CV ridge probes r_t->target.",
         **diag2}, indent=2))

    # ---- DIAG-3 aggregate ----
    d3 = r["diag3"]
    def mean(k): return float(np.mean([x[k] for x in d3]))
    from rgr.evals.bootstrap import bootstrap_ci
    pr = [(x["pass_r7"], x["pass_r0"]) for x in d3]
    dpass = bootstrap_ci(pr, lambda s: sum(a - b for a, b in s) / len(s))
    diag3 = {
        "n_problems": len(d3),
        "within_r0_diversity": mean("within_r0"), "within_r7_diversity": mean("within_r7"),
        "across_diversity": mean("across"), "mean_kl_r0_r7_nats": mean("kl_r0_r7"),
        "pass_r0": mean("pass_r0"), "pass_r7": mean("pass_r7"),
        "delta_pass_r7_minus_r0": {"point": dpass.point, "lo": dpass.lo, "hi": dpass.hi},
        "entropy_killer": mean("within_r7") < mean("within_r0"),
    }
    (REPO / "artifacts/diag3_control_authority.json").write_text(_json.dumps(
        {"_label": "EXPLORATORY / POST-HOC (Modal T4, Phase K).", **diag3}, indent=2))

    print("\n=== DIAG-2 register probes (5-fold CV) ===")
    print(f"  v_prev R2 {diag2['v_prev_R2_cv']:.3f} | passed_prev AUROC {diag2['passed_prev_AUROC_cv']} "
          f"(base {diag2['base_rate_passed_prev']:.2f}) | t R2 {diag2['t_R2_cv']:.3f}")
    print("=== DIAG-3 control authority ===")
    print(f"  diversity within-r0 {diag3['within_r0_diversity']:.3f} vs within-r7 {diag3['within_r7_diversity']:.3f} "
          f"| across {diag3['across_diversity']:.3f} | KL {diag3['mean_kl_r0_r7_nats']:.4f} nats")
    print(f"  pass r0 {diag3['pass_r0']:.3f} vs r7 {diag3['pass_r7']:.3f} "
          f"| Δ {diag3['delta_pass_r7_minus_r0']['point']:+.3f} CI [{diag3['delta_pass_r7_minus_r0']['lo']:+.3f},{diag3['delta_pass_r7_minus_r0']['hi']:+.3f}]")
    print(f"  entropy-killer (r7 diversity < r0): {diag3['entropy_killer']}")
    print("wrote artifacts/diag2_register_probes.json + artifacts/diag3_control_authority.json")


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


# ---------------------------------------------------------------------------
# DIAG-10 — does execution feedback help? The 2x2 (feedback x candidate).
# HumanEval-as-dev (D13). Prompt-level only, base generator, NO register, NO
# verifier. Conditions run on Modal: b1 (i.i.d.), abstract (feedback, no
# candidate), b2_fb (feedback + candidate). b2-raw comes from committed data.
# Pre-registered docs/DIAGNOSTICS.md DIAG-10 (before this ran).
# ---------------------------------------------------------------------------

_DIAG10_ERR = {
    "wrong_answer": "it ran but returned wrong answers on some tests.",
    "runtime": "it raised a runtime error.",
    "syntax": "it had a syntax error.",
    "timeout": "it ran too long (likely an infinite loop or inefficiency).",
    "no_code": "no Python code block could be found in the response.",
    "sandbox": "it could not be evaluated.",
    "": "it passed the tests.",
}


@app.function(image=IMAGE, gpu="T4", volumes={"/cache": VOL}, timeout=14400)
def feedback_2x2(n_problems: int = 164, chunk: int = 24):
    """The 2x2. Per condition, an 8-step columnar rollout with batched distinct-
    prompt generation (input_ids path, register=None) + concurrent Daytona exec.
    Returns per-condition per-problem step trajectories (passed, error_type, code)."""
    import os

    os.chdir("/root/rgr")
    from concurrent.futures import ThreadPoolExecutor

    import torch

    from rgr.data.humaneval import load_humaneval
    from rgr.execution.sandbox import DaytonaBackend
    from rgr.generator.formatting import SYSTEM_PROMPT, build_prompt, extract_code
    from rgr.types import Candidate, SplitRole

    config, gen = _load_config_and_gen()          # base Qwen 4-bit, no register
    tok, model = gen._tokenizer, gen._model
    tok.padding_side = "left"
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    gcfg = gen.config
    T = config.loop.t_max
    problems = load_humaneval().checkout(SplitRole.HELDOUT_EVAL)[:n_problems]
    N = len(problems)
    print(f"DIAG-10: {N} HumanEval-dev problems, T={T}, temp={gcfg.temperature}", flush=True)

    @torch.no_grad()
    def gen_batch(prompts: list[str]) -> list[str]:
        texts: list[str] = []
        for i in range(0, len(prompts), chunk):
            sub = prompts[i:i + chunk]
            msgs = [[{"role": "system", "content": SYSTEM_PROMPT},
                     {"role": "user", "content": pr}] for pr in sub]
            enc = tok.apply_chat_template(
                msgs, add_generation_prompt=True, return_tensors="pt",
                padding=True, return_dict=True,
            ).to(gen.device)
            out = model.generate(
                **enc, do_sample=gcfg.temperature > 0, temperature=gcfg.temperature or None,
                top_p=gcfg.top_p, max_new_tokens=gcfg.max_new_tokens,
                pad_token_id=tok.eos_token_id,
            )
            gen_only = out[:, enc["input_ids"].shape[1]:]
            texts.extend(tok.decode(row, skip_special_tokens=True) for row in gen_only)
        return texts

    K = 8
    backends = [DaytonaBackend(config.execution.timeout_seconds) for _ in range(K)]
    tp = ThreadPoolExecutor(max_workers=K)

    def execute_pairs(probs, cands):
        def run(args):
            idx, prob, cand = args
            return backends[idx % K].execute(prob, cand)
        jobs = [(i, probs[i], cands[i]) for i in range(len(cands))]
        results = [None] * len(jobs)
        for start in range(0, len(jobs), K):
            chunk_jobs = jobs[start:start + K]
            for off, res in enumerate(tp.map(run, chunk_jobs)):
                results[start + off] = res
        return results

    def abstract_prompt(problem, prev_code, err):
        base = build_prompt(problem.prompt)
        return (base + "\n\nYour previous attempt was executed against the tests: "
                + _DIAG10_ERR.get(err, _DIAG10_ERR["sandbox"])
                + " Write a corrected, complete solution as a single fenced Python code block.")

    def b2fb_prompt(problem, prev_code, err):
        base = build_prompt(problem.prompt)
        if prev_code is None:
            body = ("Your previous response contained no code block. "
                    + "Write a complete solution as a single fenced Python code block.")
        else:
            body = ("Your previous attempt:\n```python\n" + prev_code + "\n```\n"
                    + "It was executed against the tests: " + _DIAG10_ERR.get(err, _DIAG10_ERR["sandbox"])
                    + " Write an improved complete solution as a single fenced Python code block.")
        return base + "\n\n" + body

    def run_step(prompts):
        cands = [Candidate(text=t, code=extract_code(t)) for t in gen_batch(prompts)]
        results = execute_pairs(problems, cands)
        recs = [{"passed": bool(e.passed), "error_type": e.error_type, "code": c.code}
                for c, e in zip(cands, results)]
        return recs

    # Shared step 0 (un-conditioned build_prompt) — identical start for all
    # conditions, per the pre-registered design.
    print("--- shared step 0 ---", flush=True)
    step0 = run_step([build_prompt(p.prompt) for p in problems])
    for j in range(N):
        step0[j]["step"] = 0
    print(f"  [step0] pass {sum(r['passed'] for r in step0)/N:.3f}", flush=True)

    def rollout(condition):
        traj = [[dict(step0[j])] for j in range(N)]
        prev_code = [step0[j]["code"] for j in range(N)]
        prev_err = [step0[j]["error_type"] for j in range(N)]
        for step in range(1, T):
            if condition == "b1":
                prompts = [build_prompt(p.prompt) for p in problems]
            elif condition == "abstract":
                prompts = [abstract_prompt(problems[j], prev_code[j], prev_err[j]) for j in range(N)]
            elif condition == "b2_fb":
                prompts = [b2fb_prompt(problems[j], prev_code[j], prev_err[j]) for j in range(N)]
            recs = run_step(prompts)
            for j in range(N):
                recs[j]["step"] = step
                traj[j].append(recs[j])
                prev_code[j], prev_err[j] = recs[j]["code"], recs[j]["error_type"]
            print(f"  [{condition}] step {step}: pass {sum(r['passed'] for r in recs)/N:.3f}", flush=True)
        return traj

    out = {}
    try:
        for cond in ("b1", "abstract", "b2_fb"):
            print(f"--- condition {cond} ---", flush=True)
            out[cond] = rollout(cond)
    finally:
        for b in backends:
            try:
                b._teardown()
            except Exception:
                pass
        tp.shutdown(wait=False)
    return {"conditions": out, "n_problems": N, "T": T,
            "problem_ids": [p.problem_id for p in problems]}


@app.local_entrypoint()
def feedback_main(n_problems: int = 164, chunk: int = 24):
    import json as _json

    r = feedback_2x2.remote(n_problems, chunk)
    (REPO / "runs/modal").mkdir(parents=True, exist_ok=True)
    (REPO / "runs/modal/diag10_feedback_2x2.json").write_text(_json.dumps(r))

    conds = r["conditions"]
    T, N = r["T"], r["n_problems"]

    def pass_by_step(traj):
        return [sum(traj[j][k]["passed"] for j in range(len(traj))) / len(traj) for k in range(T)]

    def no_code_by_step(traj):
        return [sum(traj[j][k]["error_type"] == "no_code" for j in range(len(traj))) / len(traj)
                for k in range(T)]

    traj_pass = {c: pass_by_step(conds[c]) for c in conds}
    traj_nocode = {c: no_code_by_step(conds[c]) for c in conds}
    # slope step0 -> last, and mean(steps 1..last) vs step0 (refinement lift)
    summary = {}
    for c, pr in traj_pass.items():
        summary[c] = {"step0": pr[0], "last": pr[-1], "slope_0_to_last": pr[-1] - pr[0],
                      "mean_1_to_last": sum(pr[1:]) / (T - 1)}

    result = {
        "_label": "DIAG-10 — feedback x candidate 2x2 (Modal T4, HumanEval-dev D13). "
                  "EXPLORATORY; does not reopen H2. b2-raw reference is committed (0.61->0.40).",
        "n_problems": N, "T": T,
        "pass_by_step": traj_pass,
        "no_code_by_step": traj_nocode,
        "summary": summary,
        "b2_raw_committed_reference": [0.610, 0.494, 0.457, 0.451, 0.433, 0.402, 0.390, 0.402],
    }
    (REPO / "artifacts/diag10_feedback_2x2.json").write_text(_json.dumps(result, indent=2))

    print(f"\n=== DIAG-10 — feedback x candidate 2x2 ({N} HumanEval-dev problems) ===")
    print(f"{'step':<6}" + "".join(f"{k:>8}" for k in range(T)))
    for c in ("b1", "abstract", "b2_fb"):
        print(f"{c:<10}" + "".join(f"{v:>8.3f}" for v in traj_pass[c]))
    print(f"{'b2-raw*':<10}" + "".join(f"{v:>8.3f}" for v in result["b2_raw_committed_reference"]))
    print("  (* committed reference, cross-stack — anchor via b1 flatness + shared step-0)")
    print("\nslope step0->last:  " + "  ".join(f"{c} {summary[c]['slope_0_to_last']:+.3f}" for c in conds))
    print("no_code by step (abstract / b2_fb):")
    print(f"  abstract {[round(x,3) for x in traj_nocode['abstract']]}")
    print(f"  b2_fb    {[round(x,3) for x in traj_nocode['b2_fb']]}")
    print("wrote artifacts/diag10_feedback_2x2.json")


# ---------------------------------------------------------------------------
# Phase M — M4 verifier revalidation. The verifier stack is UNCHANGED (this T4
# QLoRA image); only its INPUT candidate distribution shifted (4-bit → bf16, the
# M3 pool). Score the M3 bf16 candidates with V-v2b and compare AUROC to the
# recorded 0.7951 (global) / 0.7189 (within-problem). [PHASE_M.md] §5 M4.
# ---------------------------------------------------------------------------

@app.function(image=IMAGE, gpu="T4", volumes={"/cache": VOL}, timeout=5400)
def m4_score(payload: dict) -> dict:
    """Score bf16 (M3) candidates with the unchanged V-v2b. payload = {problem_ids,
    codes: [[code|None × 8] per problem]}. Returns per-candidate V scores, with the
    deployment rule code=None → 0.0 (matches QloraVerifier.score)."""
    import os

    os.chdir("/root/rgr")
    from rgr.data.humaneval import load_humaneval
    from rgr.types import SplitRole
    from rgr.verifier.qlora import QloraVerifier

    problems = {p.problem_id: p for p in load_humaneval().checkout(SplitRole.HELDOUT_EVAL)}
    verifier = QloraVerifier("artifacts/v2b_lora")
    print("loading V-v2b ...", flush=True)
    verifier.load()

    out = []
    for pid, row in zip(payload["problem_ids"], payload["codes"]):
        prob = problems[pid]
        valid = [(i, cd) for i, cd in enumerate(row) if cd is not None]
        vs = [0.0] * len(row)
        if valid:
            scored = verifier.score_texts([(prob.prompt, cd) for _, cd in valid])
            for (i, _), s in zip(valid, scored):
                vs[i] = s
        out.append(vs)
    return {"problem_ids": payload["problem_ids"], "v_scores": out}


@app.local_entrypoint()
def m4_main():
    """M4 gate. Score the M3 bf16 pool with V-v2b (T4); reuse M3's saved labels
    (runs/modal/m3_labels.json — no re-execution). Compute global + within-problem
    AUROC for BOTH V and likelihood, vs the recorded V 0.7951/0.7189 & likelihood
    within 0.568 — so we see whether V still beats likelihood on the new pool (H1)."""
    import json as _json
    import os

    os.chdir(str(REPO))
    from rgr.evals.calibration import auroc

    m3 = _json.loads((REPO / "runs/modal/m3_candidates.json").read_text())
    lab = _json.loads((REPO / "runs/modal/m3_labels.json").read_text())
    assert m3["problem_ids"] == lab["problem_ids"], "candidates/labels misaligned — re-run m3"
    codes = [[c["code"] for c in row] for row in m3["candidates"]]
    logp = [[c["mean_logprob"] for c in row] for row in m3["candidates"]]
    labels = lab["labels"]

    scored = m4_score.remote({"problem_ids": m3["problem_ids"], "codes": codes})
    vscores = scored["v_scores"]

    def clean(row):
        return [s if s is not None else -1e9 for s in row]

    def glob(scores):
        fs = [s for row in scores for s in clean(row)]
        fl = [bool(x) for row in labels for x in row]
        return auroc(fs, fl)

    def within(scores):
        per = [auroc(clean(sv), [bool(x) for x in lb])
               for sv, lb in zip(scores, labels) if len({bool(x) for x in lb}) == 2]
        return (sum(per) / len(per) if per else float("nan")), len(per)

    v_g, l_g = glob(vscores), glob(logp)
    v_w, ntwo = within(vscores)
    l_w, _ = within(logp)
    pos = sum(x for row in labels for x in row) / sum(len(row) for row in labels)

    OLD = {"V_global": 0.7951, "V_within": 0.7189, "lik_within": 0.568}
    material = 0.05
    v_holds = v_w >= OLD["V_within"] - material
    beats_lik = v_w > l_w + 0.03
    if v_holds:
        verdict = "PASS — V-v2b reranking survives the substrate change"
    elif beats_lik:
        verdict = ("DEGRADED-BUT-BEATS-LIKELIHOOD — V within-problem dropped but still "
                   "outranks likelihood; retrain on bf16 to restore the margin (H1 edge survives)")
    else:
        verdict = "RETRAIN — V lost its reranking edge on bf16 candidates"

    result = {"_label": "M4 — V-v2b revalidation on the bf16 (M3) candidate pool",
              "positive_rate_bf16": pos, "n_two_class_problems": ntwo,
              "n_candidates": sum(len(r) for r in labels),
              "V": {"global_auroc": v_g, "within_problem_auroc": v_w},
              "likelihood": {"global_auroc": l_g, "within_problem_auroc": l_w},
              "recorded_old_4bit": OLD, "verdict": verdict}
    (REPO / "artifacts/m4_verifier_revalidation.json").write_text(_json.dumps(result, indent=2))

    print(f"\n=== M4 — V-v2b revalidation on bf16 candidates ===")
    print(f"positive (pass) rate on bf16 pool: {pos:.3f} (old 4-bit ≈ 0.28); "
          f"two-class problems {ntwo}/{len(labels)}")
    print(f"{'':<16}{'V (new)':>10}{'lik (new)':>11}{'V (old)':>10}{'lik (old)':>11}")
    print(f"{'global AUROC':<16}{v_g:>10.4f}{l_g:>11.4f}{OLD['V_global']:>10.4f}{0.6961:>11.4f}")
    print(f"{'within-problem':<16}{v_w:>10.4f}{l_w:>11.4f}{OLD['V_within']:>10.4f}{OLD['lik_within']:>11.4f}")
    print(f"\nM4 verdict: {verdict}")
    print("wrote artifacts/m4_verifier_revalidation.json")


@app.local_entrypoint()
def r1b_h2h():
    """R1b part 1 — full H1 head-to-head on the bf16 M3 pool with the EXISTING
    (stale, 4-bit-trained) V-v2b. Within-problem macro AUROC (primary) + pooled
    (secondary) + best-of-8 and best-of-50 pass@1 for V and likelihood. Compared to
    the retired-4-bit H1 numbers. R1b part 2 (retrain V on bf16) fills the retrained
    column. [PHASE_3R.md] R1b."""
    import json as _json
    import os

    os.chdir(str(REPO))
    from rgr.evals.calibration import auroc

    m3 = _json.loads((REPO / "runs/modal/m3_candidates.json").read_text())
    lab = _json.loads((REPO / "runs/modal/m3_labels.json").read_text())
    assert m3["problem_ids"] == lab["problem_ids"]
    codes = [[c["code"] for c in row] for row in m3["candidates"]]
    logp = [[c["mean_logprob"] for c in row] for row in m3["candidates"]]
    labels = lab["labels"]
    vsc = m4_score.remote({"problem_ids": m3["problem_ids"], "codes": codes})["v_scores"]

    def clean(row):
        return [s if s is not None else -1e9 for s in row]

    def within(scores):
        per = [auroc(clean(sv), [bool(x) for x in lb])
               for sv, lb in zip(scores, labels) if len({bool(x) for x in lb}) == 2]
        return sum(per) / len(per)

    def pooled(scores):
        fs = [s for row in scores for s in clean(row)]
        fl = [bool(x) for row in labels for x in row]
        return auroc(fs, fl)

    def best_of(scores, kk):
        # pass@1 of the argmax-score candidate among the first kk samples, per problem
        hit = 0
        for sv, lb in zip(scores, labels):
            idx = max(range(min(kk, len(sv))), key=lambda i: clean(sv)[i])
            hit += bool(lb[idx])
        return hit / len(labels)

    tbl = {
        "V": {"within": within(vsc), "pooled": pooled(vsc),
              "bo8": best_of(vsc, 8), "bo50": best_of(vsc, 50)},
        "likelihood": {"within": within(logp), "pooled": pooled(logp),
                       "bo8": best_of(logp, 8), "bo50": best_of(logp, 50)},
    }
    tbl["edge_within_V_minus_lik"] = tbl["V"]["within"] - tbl["likelihood"]["within"]
    tbl["edge_bo8_V_minus_lik"] = tbl["V"]["bo8"] - tbl["likelihood"]["bo8"]
    tbl["_stack"] = "bf16 M3 pool, STALE 4-bit-trained V-v2b (R1b part 1)"
    tbl["_retired_4bit_H1"] = {"V_within": 0.7189, "lik_within": 0.5680,
                               "V_bo8": 0.6707, "lik_bo8": 0.6280, "edge_within": 0.151}
    (REPO / "artifacts/r1b_h2h_stale_v.json").write_text(_json.dumps(tbl, indent=2))

    print("\n=== R1b.1 — H1 head-to-head on bf16 pool (STALE 4-bit-trained V) ===")
    print(f"{'metric':<22}{'V':>10}{'likelihood':>12}{'edge (V−lik)':>14}")
    print(f"{'within-problem AUROC':<22}{tbl['V']['within']:>10.4f}{tbl['likelihood']['within']:>12.4f}"
          f"{tbl['edge_within_V_minus_lik']:>+14.4f}")
    print(f"{'pooled AUROC':<22}{tbl['V']['pooled']:>10.4f}{tbl['likelihood']['pooled']:>12.4f}")
    print(f"{'best-of-8 pass@1':<22}{tbl['V']['bo8']:>10.4f}{tbl['likelihood']['bo8']:>12.4f}"
          f"{tbl['edge_bo8_V_minus_lik']:>+14.4f}")
    print(f"{'best-of-50 pass@1':<22}{tbl['V']['bo50']:>10.4f}{tbl['likelihood']['bo50']:>12.4f}")
    print(f"\nretired 4-bit H1: V within 0.7189 vs lik 0.5680 (edge +0.151); "
          f"bo8 V 0.6707 vs lik 0.6280")
    print("wrote artifacts/r1b_h2h_stale_v.json")
