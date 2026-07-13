#!/usr/bin/env python3
"""Phase M — the throughput STACK rebuild: vLLM + bf16 on Modal L4.

SEPARATE from scripts/modal_rgr.py (the frozen HF/NF4/T4 diagnostic stack) by
design — Phase M is a new stack at a clean phase boundary ([PHASE_M.md] §0, tag
`pre-phase-m-hf-nf4`). D11: half precision (bf16 on L4).

Gates ([PHASE_M.md] §5):
  M1 — vLLM prompt_embeds reproduces HF soft-prompt semantics (this file, m1).
  M2 — throughput >= 20x.  M3 — B0/B1 statistical equivalence.
  M4 — V-v2b revalidation.  M5 — re-lock.

Usage (tokens from rgr-modal.txt as env vars):
  modal run scripts/modal_phasem.py::m1 --n 20
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import modal

REPO = Path(__file__).parents[1]
STAGE = REPO / ".modal_stage_m"
sys.path.insert(0, str(REPO / "src"))

MODEL = "Qwen/Qwen2.5-Coder-1.5B-Instruct"

# Minimal staging for the vLLM stack (no Daytona key — M1..M3 do no execution).
NEED = {
    "src": "src",
    "configs": "configs",
    "data/cache": "data/cache",
    "runs/kaggle/phase2_train/runs/phase2/register_modules.pt": "artifacts/register_modules.pt",
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
    print(f"staged -> {STAGE}")


if any(a in sys.argv for a in ("run", "--stage")) or __name__ == "__main__":
    if not STAGE.exists():
        stage()

# vLLM 0.11.0 is incompatible with transformers 5.0 (Qwen2Tokenizer lost
# all_special_tokens_extended); pin the tested-compatible transformers 4.57.0.
IMAGE = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("vllm==0.11.0", "transformers==4.57.0")
    .env({"PYTHONPATH": "/root/rgr/src", "HF_HOME": "/cache/hf",
          "TOKENIZERS_PARALLELISM": "false", "VLLM_LOGGING_LEVEL": "WARNING"})
    .add_local_dir(str(STAGE), "/root/rgr")
)

VOL = modal.Volume.from_name("rgr-hf-cache", create_if_missing=True)
app = modal.App("rgr-phasem")


@app.function(image=IMAGE, gpu="L4", volumes={"/cache": VOL}, timeout=3600)
def m1(n: int = 20, max_new: int = 48):
    """M1 correctness gate. Fix one register r → soft prompt (k, d_model). For n
    HumanEval problems build [soft ++ embed(templated_prompt)] and greedy-decode
    under (a) HF bf16 inputs_embeds, (b) vLLM bf16 prompt_embeds. Compare token ids.
    Identical/long-prefix match ⇒ prompt_embeds migrates the register path faithfully;
    divergence at token 1–3 ⇒ chat template spliced wrong (§2 trap 1)."""
    import os

    os.chdir("/root/rgr")
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    from rgr.config import load_config
    from rgr.data.humaneval import load_humaneval
    from rgr.generator.formatting import SYSTEM_PROMPT, build_prompt
    from rgr.generator.injection import RegisterInjector
    from rgr.types import SplitRole

    config = load_config("configs/phase2_register.toml")
    d_r, k_soft = config.register.d_r, config.register.k_soft_tokens

    tok = AutoTokenizer.from_pretrained(MODEL)
    eos = tok.eos_token_id
    print("loading HF bf16 reference ...", flush=True)
    hf = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.bfloat16).to("cuda").eval()
    d_model = hf.config.hidden_size
    emb = hf.get_input_embeddings()

    # fixed reference register r (seed 17) -> trained injector -> soft (k, d_model)
    torch.manual_seed(config.run.seed)
    inj = RegisterInjector(d_r, k_soft, d_model).to("cuda").float()
    ck = torch.load("artifacts/register_modules.pt", weights_only=True, map_location="cuda")
    inj.load_state_dict(ck["modules"]["injector"])
    inj.eval()
    r = torch.randn(d_r, device="cuda")
    with torch.no_grad():
        soft = inj(r).to(torch.bfloat16)               # (k_soft, d_model)
    assert soft.shape == (k_soft, d_model), soft.shape

    problems = load_humaneval().checkout(SplitRole.HELDOUT_EVAL)[:n]

    def templated_ids(problem):
        msgs = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_prompt(problem.prompt)}]
        enc = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt")
        return getattr(enc, "input_ids", enc)[0].to("cuda")

    pe_list = []
    for p in problems:
        ids = templated_ids(p)
        with torch.no_grad():
            te = emb(ids).to(torch.bfloat16)           # (L, d_model)
        pe_list.append(torch.cat([soft, te], dim=0).detach())   # (k_soft+L, d_model)

    def strip_eos(ids):
        out = []
        for t in ids:
            if t == eos:
                break
            out.append(int(t))
        return out

    print("HF greedy ...", flush=True)
    hf_out = []
    for pe in pe_list:
        with torch.no_grad():
            o = hf.generate(inputs_embeds=pe.unsqueeze(0),
                            attention_mask=torch.ones(1, pe.shape[0], dtype=torch.long, device="cuda"),
                            do_sample=False, max_new_tokens=max_new, pad_token_id=eos)
        hf_out.append(strip_eos(o[0].tolist()))        # inputs_embeds => generated tokens only

    del hf, emb, inj
    torch.cuda.empty_cache()

    print("loading vLLM bf16 + prompt_embeds ...", flush=True)
    from vllm import LLM, SamplingParams
    llm = LLM(model=MODEL, enable_prompt_embeds=True, dtype="bfloat16",
              gpu_memory_utilization=0.55, max_model_len=2048, enforce_eager=True)
    sp = SamplingParams(temperature=0.0, max_tokens=max_new)
    vout = llm.generate([{"prompt_embeds": pe.cpu()} for pe in pe_list], sp)
    vllm_out = [list(o.outputs[0].token_ids) for o in vout]

    results, exact_n, prefix_ge8 = [], 0, 0
    for i, p in enumerate(problems):
        a, b = hf_out[i], vllm_out[i]
        L = min(len(a), len(b))
        first_div = next((j for j in range(L) if a[j] != b[j]), L)
        is_exact = a == b
        exact_n += is_exact
        prefix_ge8 += first_div >= 8
        results.append({"problem_id": p.problem_id, "hf_len": len(a), "vllm_len": len(b),
                        "match_prefix": first_div, "exact": is_exact})
    return {"n": len(problems), "max_new": max_new, "exact": exact_n,
            "prefix_ge8": prefix_ge8, "results": results}


@app.function(image=IMAGE, gpu="L4", volumes={"/cache": VOL}, timeout=3600)
def m2(n_vllm: int = 64, gen_tokens: int = 256):
    """M2 throughput gate. Same L4, same workload (plain HumanEval prompts — the
    3a/3b-lite generation mode, no register): HF bf16 batch-1 `generate` vs vLLM
    bf16 continuous batching. Reports aggregate tok/s and the multiple. Isolates the
    stack win on identical hardware; also validates plain vLLM generation."""
    import os
    import time

    os.chdir("/root/rgr")
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    from rgr.data.humaneval import load_humaneval
    from rgr.generator.formatting import SYSTEM_PROMPT, build_prompt
    from rgr.types import SplitRole

    tok = AutoTokenizer.from_pretrained(MODEL)
    eos = tok.eos_token_id
    problems = load_humaneval().checkout(SplitRole.HELDOUT_EVAL)[:n_vllm]

    def prompt_text(p):
        msgs = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_prompt(p.prompt)}]
        return tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False)

    prompts = [prompt_text(p) for p in problems]

    # --- HF bf16 batch-1 baseline (force exactly gen_tokens for a fair rate) ---
    print("HF bf16 batch-1 ...", flush=True)
    hf = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.bfloat16).to("cuda").eval()
    ids = tok(prompts[0], return_tensors="pt").input_ids.to("cuda")
    with torch.no_grad():
        hf.generate(ids, max_new_tokens=16, do_sample=False, pad_token_id=eos)  # warmup
        torch.cuda.synchronize()
        t0 = time.time()
        hf.generate(ids, min_new_tokens=gen_tokens, max_new_tokens=gen_tokens,
                    do_sample=False, pad_token_id=eos)
        torch.cuda.synchronize()
        hf_dt = time.time() - t0
    hf_tok_s = gen_tokens / hf_dt
    del hf
    torch.cuda.empty_cache()

    # --- vLLM continuous batching (force gen_tokens via ignore_eos for a fair rate) ---
    print("vLLM bf16 continuous batching ...", flush=True)
    from vllm import LLM, SamplingParams
    llm = LLM(model=MODEL, dtype="bfloat16", gpu_memory_utilization=0.85,
              max_model_len=2048, enforce_eager=False)
    llm.generate(prompts[:2], SamplingParams(temperature=0.0, max_tokens=16))  # warmup
    sp = SamplingParams(temperature=0.0, max_tokens=gen_tokens, ignore_eos=True)
    t0 = time.time()
    out = llm.generate(prompts, sp)
    vllm_dt = time.time() - t0
    total = sum(len(o.outputs[0].token_ids) for o in out)
    vllm_tok_s = total / vllm_dt

    return {"hf_batch1_tok_s": hf_tok_s, "vllm_agg_tok_s": vllm_tok_s,
            "multiple_vs_hf_batch1": vllm_tok_s / hf_tok_s,
            "n_vllm": n_vllm, "gen_tokens": gen_tokens, "vllm_total_tokens": total,
            "vllm_wall_s": vllm_dt, "hf_wall_s": hf_dt,
            "old_stack_effective_tok_s_documented": 10.0}


@app.local_entrypoint()
def m2_main(n_vllm: int = 64, gen_tokens: int = 256):
    r = m2.remote(n_vllm, gen_tokens)
    (REPO / "runs/modal").mkdir(parents=True, exist_ok=True)
    (REPO / "runs/modal/m2_throughput.json").write_text(json.dumps(r, indent=2))
    print(f"\n=== M2 — throughput ({n_vllm} prompts × {gen_tokens} tok, L4) ===")
    print(f"HF bf16 batch-1:        {r['hf_batch1_tok_s']:.1f} tok/s")
    print(f"vLLM bf16 aggregate:    {r['vllm_agg_tok_s']:.1f} tok/s "
          f"({r['vllm_total_tokens']} tok in {r['vllm_wall_s']:.1f}s)")
    print(f"multiple vs HF batch-1: {r['multiple_vs_hf_batch1']:.1f}×")
    print(f"multiple vs old 4-bit/T4 effective (~10 tok/s): {r['vllm_agg_tok_s']/10:.0f}×")
    gate = r["multiple_vs_hf_batch1"] >= 20 or r["vllm_agg_tok_s"] / 10 >= 20
    print(f"\nM2 gate (≥20×): {'PASS' if gate else 'INVESTIGATE (<20×)'}")
    print("wrote runs/modal/m2_throughput.json")


@app.local_entrypoint()
def m1_main(n: int = 20, max_new: int = 48):
    r = m1.remote(n, max_new)
    (REPO / "runs/modal").mkdir(parents=True, exist_ok=True)
    (REPO / "runs/modal/m1_correctness.json").write_text(json.dumps(r, indent=2))

    res = r["results"]
    prefixes = sorted(x["match_prefix"] for x in res)
    med = prefixes[len(prefixes) // 2]
    early = [x for x in res if x["match_prefix"] < 3]
    print(f"\n=== M1 — vLLM prompt_embeds vs HF soft-prompt ({r['n']} problems, greedy, max_new={r['max_new']}) ===")
    print(f"exact token-id match: {r['exact']}/{r['n']}")
    print(f"prefix match >= 8 tokens: {r['prefix_ge8']}/{r['n']}")
    print(f"match-prefix: min {prefixes[0]}, median {med}, max {prefixes[-1]}")
    print(f"early divergence (<3 tokens, = chat-template/splice bug signature): {len(early)}/{r['n']}")
    for x in res[:8]:
        print(f"  {x['problem_id']:<22} prefix {x['match_prefix']:>3}  exact {x['exact']}  (hf {x['hf_len']} / vllm {x['vllm_len']})")
    verdict = ("PASS (faithful)" if len(early) == 0 and r["prefix_ge8"] >= 0.8 * r["n"]
               else "INSPECT" if len(early) <= 0.1 * r["n"] else "FAIL (systematic — chat template?)")
    print(f"\nM1 verdict: {verdict}")
    print("wrote runs/modal/m1_correctness.json")
