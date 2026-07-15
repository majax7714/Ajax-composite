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
def m5_gen(seed: int = 17, n_problems: int = 164, n_samples: int = 2, greedy: bool = False):
    """M5 re-lock generation — one independent run on the vLLM/bf16 stack. Seeded
    (engine + sampling) so two runs with the same seed should reproduce. Returns
    per-problem candidate texts for byte comparison. greedy=True → temp 0 (the
    deterministic-by-construction fallback lock)."""
    import os

    os.chdir("/root/rgr")
    from transformers import AutoTokenizer

    from rgr.config import load_config
    from rgr.data.humaneval import load_humaneval
    from rgr.generator.formatting import SYSTEM_PROMPT, build_prompt
    from rgr.types import SplitRole
    from vllm import LLM, SamplingParams

    g = load_config("configs/phase0_harness.toml").generator
    tok = AutoTokenizer.from_pretrained(MODEL)
    problems = load_humaneval().checkout(SplitRole.HELDOUT_EVAL)[:n_problems]
    prompts = [tok.apply_chat_template(
        [{"role": "system", "content": SYSTEM_PROMPT},
         {"role": "user", "content": build_prompt(p.prompt)}],
        add_generation_prompt=True, tokenize=False) for p in problems]
    llm = LLM(model=MODEL, dtype="bfloat16", gpu_memory_utilization=0.85,
              max_model_len=2048, seed=seed)
    if greedy:
        sp = SamplingParams(n=1, temperature=0.0, max_tokens=g.max_new_tokens)
    else:
        sp = SamplingParams(n=n_samples, temperature=g.temperature, top_p=g.top_p,
                            max_tokens=g.max_new_tokens, seed=seed)
    outs = llm.generate(prompts, sp)
    return {"problem_ids": [p.problem_id for p in problems],
            "texts": [[o.text for o in req.outputs] for req in outs]}


@app.local_entrypoint()
def m5_main(n_problems: int = 164, n_samples: int = 2):
    """M5 gate. Two independent seeded runs → byte compare (the new lock_a/lock_b).
    Also a greedy pair as the deterministic-by-construction check. Writes the new
    lock artifacts + the COMPUTE_ACCOUNTING second-amendment note."""
    def cmp(a, b):
        prob_ids = a["problem_ids"]
        cand_tot = sum(len(t) for t in a["texts"])
        cand_match = sum(x == y for ta, tb in zip(a["texts"], b["texts"])
                         for x, y in zip(ta, tb))
        prob_match = sum(ta == tb for ta, tb in zip(a["texts"], b["texts"]))
        return prob_match, len(prob_ids), cand_match, cand_tot

    a = m5_gen.remote(17, n_problems, n_samples, False)
    b = m5_gen.remote(17, n_problems, n_samples, False)
    pm, pt, cm, ct = cmp(a, b)

    ga = m5_gen.remote(17, n_problems, 1, True)
    gb = m5_gen.remote(17, n_problems, 1, True)
    gpm, gpt, gcm, gct = cmp(ga, gb)

    (REPO / "artifacts/lock_a_bf16.jsonl").write_text(
        "\n".join(json.dumps({"problem_id": p, "texts": t})
                  for p, t in zip(a["problem_ids"], a["texts"])))
    (REPO / "artifacts/lock_b_bf16.jsonl").write_text(
        "\n".join(json.dumps({"problem_id": p, "texts": t})
                  for p, t in zip(b["problem_ids"], b["texts"])))

    stoch_bit = cm == ct
    greedy_bit = gcm == gct
    result = {"_label": "M5 — re-lock on vLLM/bf16/L4 (new lock_a/lock_b)",
              "seed": 17, "n_problems": pt,
              "seeded_stochastic": {"candidate_match": cm, "candidate_total": ct,
                                    "problem_match": pm, "byte_identical": stoch_bit},
              "greedy": {"candidate_match": gcm, "candidate_total": gct,
                         "byte_identical": greedy_bit},
              "verdict": ("PASS — seeded stochastic byte-identical" if stoch_bit
                          else "PASS (greedy-locked) — stochastic reproduces statistically, "
                               "greedy byte-identical (vLLM kernel nondeterminism, cf. K1)"
                          if greedy_bit else "FAIL — not reproducible")}
    (REPO / "artifacts/m5_relock.json").write_text(json.dumps(result, indent=2))

    print(f"\n=== M5 — re-lock (vLLM/bf16/L4, {pt} problems, seed 17) ===")
    print(f"seeded stochastic: {cm}/{ct} candidates byte-identical "
          f"({pm}/{pt} problems)  → {'BYTE-IDENTICAL' if stoch_bit else 'not bit-identical'}")
    print(f"greedy (temp 0):   {gcm}/{gct} candidates byte-identical "
          f"→ {'BYTE-IDENTICAL' if greedy_bit else 'not bit-identical'}")
    print(f"\nM5 verdict: {result['verdict']}")
    print("wrote artifacts/lock_a_bf16.jsonl, lock_b_bf16.jsonl, m5_relock.json")


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


@app.function(image=IMAGE, gpu="L4", volumes={"/cache": VOL}, timeout=3600)
def m3_generate(n_problems: int = 164):
    """M3 generation stage (L4, vLLM bf16). Reproduce the Phase-0 candidate pool:
    n=t_max i.i.d. samples/problem, plain base model (no register), temp 0.8 /
    top_p 0.95 / max 512 — the exact Phase-0 sampling. Returns per-problem
    candidates with mean_logprob (for the likelihood rerank). Execution is
    decoupled to the local entrypoint (Daytona), per [PHASE_M.md] §1.1."""
    import os

    os.chdir("/root/rgr")
    from rgr.config import load_config
    from rgr.data.humaneval import load_humaneval
    from rgr.generator.formatting import SYSTEM_PROMPT, build_prompt, extract_code
    from rgr.types import SplitRole
    from vllm import LLM, SamplingParams

    config = load_config("configs/phase0_harness.toml")
    g = config.generator
    n_samples = config.loop.t_max
    problems = load_humaneval().checkout(SplitRole.HELDOUT_EVAL)[:n_problems]
    print(f"M3: {len(problems)} problems × {n_samples} samples, temp {g.temperature}", flush=True)

    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(MODEL)

    def prompt_text(p):
        msgs = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_prompt(p.prompt)}]
        return tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False)

    prompts = [prompt_text(p) for p in problems]
    llm = LLM(model=MODEL, dtype="bfloat16", gpu_memory_utilization=0.85, max_model_len=2048)
    # logprobs=1 populates cumulative_logprob (the sampled-token logprobs) so the
    # likelihood rerank (B1) has real scores.
    sp = SamplingParams(n=n_samples, temperature=g.temperature, top_p=g.top_p,
                        max_tokens=g.max_new_tokens, logprobs=1)
    outs = llm.generate(prompts, sp)

    def mean_logprob(o):
        ntok = len(o.token_ids)
        if not ntok:
            return None
        if o.cumulative_logprob is not None:
            return o.cumulative_logprob / ntok
        if o.logprobs:  # fallback: sum the sampled tokens' logprobs
            tot = 0.0
            for i, tid in enumerate(o.token_ids):
                d = o.logprobs[i]
                if d and tid in d:
                    tot += d[tid].logprob
            return tot / ntok
        return None

    cands = []
    for req in outs:
        cands.append([{"text": o.text, "code": extract_code(o.text),
                       "mean_logprob": mean_logprob(o)} for o in req.outputs])
    return {"problem_ids": [p.problem_id for p in problems], "n_samples": n_samples,
            "candidates": cands}


@app.local_entrypoint()
def m3_main(n_problems: int = 164):
    """M3 gate. Generate on L4 (vLLM bf16), execute locally via Daytona (same
    backend as Phase-0 → the only variable is the generation stack), compute
    B0/B1-likelihood/pass@k, compare to the recorded old-stack numbers."""
    import os

    os.chdir(str(REPO))
    r = m3_generate.remote(n_problems)
    (REPO / "runs/modal").mkdir(parents=True, exist_ok=True)
    (REPO / "runs/modal/m3_candidates.json").write_text(json.dumps(r))

    from rgr.config import load_config
    from rgr.data.humaneval import load_humaneval
    from rgr.evals.passk import mean_pass_at_k
    from rgr.execution.sandbox import DaytonaBackend
    from rgr.training.labels import ExecutionPool
    from rgr.types import Candidate, SplitRole

    config = load_config("configs/phase0_harness.toml")
    problems = {p.problem_id: p for p in load_humaneval().checkout(SplitRole.HELDOUT_EVAL)}
    pool = ExecutionPool(lambda: DaytonaBackend(config.execution.timeout_seconds), size=8)

    counts, b1_lik_pass, labels = [], 0, []
    try:
        for pid, row in zip(r["problem_ids"], r["candidates"]):
            problem = problems[pid]
            cs = [Candidate(text=c["text"], code=c["code"]) for c in row]
            passed = [e.passed for e in pool.execute_all(problem, cs)]
            labels.append([bool(x) for x in passed])
            counts.append((len(passed), sum(passed)))
            lps = [c["mean_logprob"] if c["mean_logprob"] is not None else -1e9 for c in row]
            b1_lik_pass += passed[max(range(len(lps)), key=lambda i: lps[i])]
    finally:
        pool.close()
    # persist labels aligned to m3_candidates.json so M4 reuses them (no re-exec)
    (REPO / "runs/modal/m3_labels.json").write_text(json.dumps(
        {"problem_ids": r["problem_ids"], "labels": labels}))

    n = len(counts)
    new = {"B0_pass1": mean_pass_at_k(counts, 1),
           "B1_likelihood_pass1": b1_lik_pass / n,
           "pass@2": mean_pass_at_k(counts, 2), "pass@4": mean_pass_at_k(counts, 4),
           "oracle_pass@8": mean_pass_at_k(counts, 8)}
    OLD = {"B0_pass1": 0.5922, "B1_likelihood_pass1": 0.6280,
           "pass@2": 0.6997, "pass@4": 0.7804, "oracle_pass@8": 0.8415}

    result = {"_label": "M3 — B0/B1 statistical re-baseline on vLLM/bf16/L4 vs old HF/4-bit/T4",
              "n_problems": n, "new_bf16": new, "old_4bit_documented": OLD,
              "delta_new_minus_old": {k: new[k] - OLD[k] for k in OLD}}
    (REPO / "artifacts/m3_rebaseline.json").write_text(json.dumps(result, indent=2))

    print(f"\n=== M3 — statistical re-baseline ({n} HumanEval problems) ===")
    print(f"{'metric':<22}{'old 4-bit':>11}{'new bf16':>11}{'Δ':>9}")
    for k in ("B0_pass1", "B1_likelihood_pass1", "pass@2", "pass@4", "oracle_pass@8"):
        print(f"{k:<22}{OLD[k]:>11.4f}{new[k]:>11.4f}{new[k]-OLD[k]:>+9.4f}")
    up = all(new[k] - OLD[k] >= -0.03 for k in OLD)  # bf16 should not degrade G
    big = max(abs(new[k] - OLD[k]) for k in OLD)
    verdict = ("PASS (shifts modest & explained by bf16 lift)" if up and big <= 0.10
               else "INSPECT" if big <= 0.15 else "FAIL (unexplained divergence)")
    print(f"\nmax |Δ| = {big:.3f}; all metrics ≥ old−0.03: {up}")
    print(f"M3 verdict: {verdict}")
    print("wrote artifacts/m3_rebaseline.json")


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


@app.function(image=IMAGE, gpu="L4", volumes={"/cache": VOL}, timeout=7200)
def r1b2d_gen_mbpp(k: int = 8):
    """R1b.2d — regenerate Phase-1 V training candidates from the BF16 generator on
    MBPP (seed-17 385/42 split). Returns per-candidate {problem_id, split, prompt,
    code, mean_logprob}; execution/labels done by the local entrypoint. [PHASE_3R.md] R1b.2d."""
    import os
    import random as _rnd

    os.chdir("/root/rgr")
    from transformers import AutoTokenizer

    from rgr.config import load_config
    from rgr.data.mbpp import load_mbpp
    from rgr.generator.formatting import SYSTEM_PROMPT, build_prompt, extract_code
    from vllm import LLM, SamplingParams

    g = load_config("configs/phase2_register.toml").generator
    probs = load_mbpp().problems
    ids = sorted(p.problem_id for p in probs)
    _rnd.Random(17).shuffle(ids)
    split = {pid: ("train" if i < 385 else "validation") for i, pid in enumerate(ids)}
    tok = AutoTokenizer.from_pretrained(MODEL)

    def chat(p):
        return tok.apply_chat_template(
            [{"role": "system", "content": SYSTEM_PROMPT},
             {"role": "user", "content": build_prompt(p.prompt)}],
            add_generation_prompt=True, tokenize=False)

    prompts = [chat(p) for p in probs]
    llm = LLM(model=MODEL, dtype="bfloat16", gpu_memory_utilization=0.90,
              max_model_len=2048, seed=17)
    sp = SamplingParams(n=k, temperature=g.temperature, top_p=g.top_p,
                        max_tokens=g.max_new_tokens, seed=17, logprobs=1)
    outs = llm.generate(prompts, sp)
    rows = []
    for p, req in zip(probs, outs):
        for o in req.outputs:
            nt = len(o.token_ids)
            rows.append({"problem_id": p.problem_id, "split": split[p.problem_id],
                         "prompt": p.prompt, "code": extract_code(o.text),
                         "mean_logprob": (o.cumulative_logprob / nt) if nt else None})
    return {"rows": rows, "k": k}


@app.local_entrypoint()
def r1b2d_gen_main(k: int = 8):
    """Generate BF16 MBPP candidates (L4) → execute locally via Daytona for labels →
    save runs/modal/r1b2d_mbpp_labeled.json. Then run modal_rgr.py::r1b2d_train_main."""
    import os

    os.chdir(str(REPO))
    from rgr.config import load_config
    from rgr.data.mbpp import load_mbpp
    from rgr.execution.sandbox import DaytonaBackend
    from rgr.training.labels import ExecutionPool
    from rgr.types import Candidate

    gen = r1b2d_gen_mbpp.remote(k)
    rows = gen["rows"]
    probs = {p.problem_id: p for p in load_mbpp().problems}
    cfg = load_config("configs/phase0_harness.toml")
    pool = ExecutionPool(lambda: DaytonaBackend(cfg.execution.timeout_seconds), size=8)
    # group by problem for execute_all
    from collections import defaultdict
    idx_by_pid = defaultdict(list)
    for i, r in enumerate(rows):
        idx_by_pid[r["problem_id"]].append(i)
    try:
        for pid, idxs in idx_by_pid.items():
            cands = [Candidate(text="", code=rows[i]["code"]) for i in idxs]
            for i, e in zip(idxs, pool.execute_all(probs[pid], cands)):
                rows[i]["passed"] = bool(e.passed)
    finally:
        pool.close()
    import json as _json
    (REPO / "runs/modal").mkdir(parents=True, exist_ok=True)
    (REPO / "runs/modal/r1b2d_mbpp_labeled.json").write_text(_json.dumps({"rows": rows, "k": k}))
    tr = sum(1 for r in rows if r["split"] == "train")
    va = len(rows) - tr
    pas = sum(1 for r in rows if r.get("passed"))
    print(f"R1b.2d gen: {len(rows)} MBPP candidates (train {tr}, val {va}), "
          f"passed {pas} ({pas/len(rows):.3f}). wrote runs/modal/r1b2d_mbpp_labeled.json")


@app.function(image=IMAGE, gpu="L4", volumes={"/cache": VOL}, timeout=7200)
def dmeasure_gen(artifacts: list, n: int = 8):
    """D-measure — single-step conditioning. For each problem × condition × temp,
    generate samples and compute PULL (edit distance to the conditioned artifact).
    Execution/TAX done by the local entrypoint. [PHASE_3R Addendum II §3]."""
    import difflib
    import os

    os.chdir("/root/rgr")
    from transformers import AutoTokenizer

    from rgr.generator.formatting import SYSTEM_PROMPT, build_prompt, extract_code
    from vllm import LLM, SamplingParams

    tok = AutoTokenizer.from_pretrained(MODEL)
    llm = LLM(model=MODEL, dtype="bfloat16", gpu_memory_utilization=0.90,
              max_model_len=4096, seed=17)

    def chat(user):
        return tok.apply_chat_template(
            [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user}],
            add_generation_prompt=True, tokenize=False)

    def user_prompt(a, cond):
        base = build_prompt(a["prompt"])
        if cond == "E0":
            return base
        if cond == "E1":
            return (base + f"\n\nYour previous attempt:\n```python\n{a['fail']}\n```\n"
                    "Write an improved complete solution as a single fenced Python code block.")
        if cond == "E2":
            return (base + f"\n\nA submission from another programmer:\n```python\n{a['fail']}\n```\n"
                    "Write a correct complete solution as a single fenced Python code block.")
        if cond == "E5":
            return (base + f"\n\nA previous attempt:\n```python\n{a['correct']}\n```\n"
                    "Write a complete solution as a single fenced Python code block.")

    conds = ["E0", "E1", "E2", "E5"]
    temps = [0.0, 0.8, 1.2]
    out = []
    for T in temps:
        ns = 1 if T == 0.0 else n
        items = [(a, c) for a in artifacts for c in conds]
        prompts = [chat(user_prompt(a, c)) for a, c in items]
        sp = SamplingParams(n=ns, temperature=T, top_p=0.95, max_tokens=512,
                            seed=17, logprobs=None)
        outs = llm.generate(prompts, sp)
        for (a, c), req in zip(items, outs):
            codes = [extract_code(o.text) for o in req.outputs]
            art = a["fail"] if c in ("E1", "E2") else (a["correct"] if c == "E5" else None)
            pulls = [1.0 - difflib.SequenceMatcher(None, cd, art).ratio()
                     for cd in codes if cd and art] if art else []
            out.append({"pid": a["pid"], "cond": c, "temp": T, "codes": codes,
                        "pull": (sum(pulls) / len(pulls)) if pulls else None})
    return {"results": out}


@app.local_entrypoint()
def dmeasure_main(n_problems: int = 60):
    """Build artifacts from the bf16 M3 pool (a failed + a correct candidate per
    problem), generate conditioned samples (L4), execute locally (Daytona) → TAX +
    pass, aggregate PULL/TAX per condition × temperature."""
    import json as _json
    import os
    import statistics as _st
    from collections import defaultdict

    os.chdir(str(REPO))
    from rgr.config import load_config
    from rgr.data.humaneval import load_humaneval
    from rgr.execution.sandbox import DaytonaBackend
    from rgr.training.labels import ExecutionPool
    from rgr.types import Candidate, SplitRole

    m3 = _json.loads((REPO / "runs/modal/m3_candidates.json").read_text())
    labels = _json.loads((REPO / "runs/modal/m3_labels.json").read_text())["labels"]
    he = {p.problem_id: p for p in load_humaneval().checkout(SplitRole.HELDOUT_EVAL)}
    arts = []
    for pid, row, lab in zip(m3["problem_ids"], m3["candidates"], labels):
        fail = next((c["code"] for c, p in zip(row, lab) if not p and c["code"]), None)
        good = next((c["code"] for c, p in zip(row, lab) if p and c["code"]), None)
        if fail and good:
            arts.append({"pid": pid, "prompt": he[pid].prompt, "fail": fail, "correct": good})
        if len(arts) >= n_problems:
            break

    gen = dmeasure_gen.remote(arts)
    (REPO / "runs/modal").mkdir(parents=True, exist_ok=True)
    (REPO / "runs/modal/dmeasure_gen.json").write_text(_json.dumps(gen))

    # execute all generated samples locally (Daytona) for pass/coverage
    cfg = load_config("configs/phase0_harness.toml")
    pool = ExecutionPool(lambda: DaytonaBackend(cfg.execution.timeout_seconds), size=8)
    passed = {}  # (pid,cond,temp) -> [bool per sample]
    try:
        for r in gen["results"]:
            prob = he[r["pid"]]
            cands = [Candidate(text="", code=cd) for cd in r["codes"]]
            passed[(r["pid"], r["cond"], r["temp"])] = [e.passed for e in pool.execute_all(prob, cands)]
    finally:
        pool.close()

    # aggregate: PULL (mean) and coverage per (cond,temp); TAX = cov(E0) - cov(cond)
    pull = defaultdict(list)
    cov = defaultdict(list)  # (cond,temp) -> per-problem covered(0/1)
    for r in gen["results"]:
        key = (r["cond"], r["temp"])
        if r["pull"] is not None:
            pull[key].append(r["pull"])
        ps = passed[(r["pid"], r["cond"], r["temp"])]
        cov[key].append(1.0 if any(ps) else 0.0)

    summary = {}
    for c in ["E0", "E1", "E2", "E5"]:
        for T in [0.0, 0.8, 1.2]:
            k = (c, T)
            summary[f"{c}@{T}"] = {
                "pull": (sum(pull[k]) / len(pull[k])) if pull[k] else None,
                "coverage": (sum(cov[k]) / len(cov[k])) if cov[k] else None,
                "tax_vs_E0": ((sum(cov[('E0', T)]) / len(cov[('E0', T)])) -
                              (sum(cov[k]) / len(cov[k]))) if (cov[k] and cov[('E0', T)]) else None,
            }
    result = {"_label": "D-measure — single-step conditioning; PULL + TAX by condition×temp",
              "n_problems": len(arts), "summary": summary}
    (REPO / "artifacts/dmeasure_conditioning.json").write_text(_json.dumps(result, indent=2))
    print(f"\n=== D-measure ({len(arts)} problems) — PULL (edit-dist to artifact) / coverage / TAX ===")
    print(f"{'cond@T':<10}{'PULL':>8}{'coverage':>10}{'TAX_vs_E0':>11}")
    for c in ["E0", "E1", "E2", "E5"]:
        for T in [0.0, 0.8, 1.2]:
            s = summary[f"{c}@{T}"]
            pl = f"{s['pull']:.3f}" if s['pull'] is not None else "  -  "
            tx = f"{s['tax_vs_E0']:+.3f}" if s['tax_vs_E0'] is not None else "  -  "
            print(f"{c+'@'+str(T):<10}{pl:>8}{s['coverage']:>10.3f}{tx:>11}")
    print("\nkey: E1≈E2 → provenance irrelevant; E5 pull≈E1 but high coverage → neutral attractor;")
    print("     TAX rising in T, ~0 at greedy → Self-Debug reconciliation.")
    print("wrote artifacts/dmeasure_conditioning.json")


# ---- D2a: verb × provenance 2×2 [PHASE_3R Addendum III §6-D2a] ----
# E1/E2 confound attribution ("your"/"someone else's") with verb ("improve"/"write
# correct"). All four cells condition on the SAME failed artifact; only the prompt
# changes. E1 vs E2' isolates PROVENANCE (same verb); E1 vs E1' isolates the VERB.
_D2A = {  # cond -> (attribution_line, instruction)
    "E1":  ("Your previous attempt:",                "Write an improved complete solution as a single fenced Python code block."),
    "E1p": ("Your previous attempt:",                "Write a correct complete solution as a single fenced Python code block."),
    "E2p": ("A submission from another programmer:",  "Write an improved complete solution as a single fenced Python code block."),
    "E2":  ("A submission from another programmer:",  "Write a correct complete solution as a single fenced Python code block."),
}


@app.function(image=IMAGE, gpu="L4", volumes={"/cache": VOL}, timeout=7200)
def dmeasure_d2a_gen(artifacts: list, n: int = 8):
    """Generate the verb×provenance 2×2, all conditioned on a['fail']. PULL = edit
    distance to that (single, shared) failed artifact — directly comparable across cells."""
    import difflib
    import os

    os.chdir("/root/rgr")
    from transformers import AutoTokenizer

    from rgr.generator.formatting import SYSTEM_PROMPT, build_prompt, extract_code
    from vllm import LLM, SamplingParams

    tok = AutoTokenizer.from_pretrained(MODEL)
    llm = LLM(model=MODEL, dtype="bfloat16", gpu_memory_utilization=0.90,
              max_model_len=4096, seed=17)

    def chat(user):
        return tok.apply_chat_template(
            [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user}],
            add_generation_prompt=True, tokenize=False)

    def user_prompt(a, cond):
        attrib, instr = _D2A[cond]
        return (build_prompt(a["prompt"]) + f"\n\n{attrib}\n```python\n{a['fail']}\n```\n" + instr)

    conds = ["E1", "E1p", "E2p", "E2"]
    temps = [0.0, 0.8, 1.2]
    out = []
    for T in temps:
        ns = 1 if T == 0.0 else n
        items = [(a, c) for a in artifacts for c in conds]
        prompts = [chat(user_prompt(a, c)) for a, c in items]
        sp = SamplingParams(n=ns, temperature=T, top_p=0.95, max_tokens=512,
                            seed=17, logprobs=None)
        outs = llm.generate(prompts, sp)
        for (a, c), req in zip(items, outs):
            codes = [extract_code(o.text) for o in req.outputs]
            art = a["fail"]  # every cell conditions on the same failed artifact
            pulls = [1.0 - difflib.SequenceMatcher(None, cd, art).ratio()
                     for cd in codes if cd]
            out.append({"pid": a["pid"], "cond": c, "temp": T, "codes": codes,
                        "pull": (sum(pulls) / len(pulls)) if pulls else None})
    return {"results": out}


@app.local_entrypoint()
def dmeasure_d2a_main(n_problems: int = 60):
    """Verb×provenance 2×2 on the committed bf16 M3 pool. Reports PULL, coverage, and
    mean per-sample pass for E1/E1'/E2'/E2, plus the two isolating contrasts."""
    import json as _json
    import os
    from collections import defaultdict

    os.chdir(str(REPO))
    from rgr.config import load_config
    from rgr.data.humaneval import load_humaneval
    from rgr.execution.sandbox import DaytonaBackend
    from rgr.training.labels import ExecutionPool
    from rgr.types import Candidate, SplitRole

    m3 = _json.loads((REPO / "runs/modal/m3_candidates.json").read_text())
    labels = _json.loads((REPO / "runs/modal/m3_labels.json").read_text())["labels"]
    he = {p.problem_id: p for p in load_humaneval().checkout(SplitRole.HELDOUT_EVAL)}
    arts = []
    for pid, row, lab in zip(m3["problem_ids"], m3["candidates"], labels):
        fail = next((c["code"] for c, p in zip(row, lab) if not p and c["code"]), None)
        good = next((c["code"] for c, p in zip(row, lab) if p and c["code"]), None)
        if fail and good:
            arts.append({"pid": pid, "prompt": he[pid].prompt, "fail": fail, "correct": good})
        if len(arts) >= n_problems:
            break

    gen = dmeasure_d2a_gen.remote(arts)
    (REPO / "runs/modal").mkdir(parents=True, exist_ok=True)
    (REPO / "runs/modal/dmeasure_d2a_gen.json").write_text(_json.dumps(gen))

    cfg = load_config("configs/phase0_harness.toml")
    pool = ExecutionPool(lambda: DaytonaBackend(cfg.execution.timeout_seconds), size=8)
    passed = {}
    try:
        for r in gen["results"]:
            prob = he[r["pid"]]
            cands = [Candidate(text="", code=cd) for cd in r["codes"]]
            passed[(r["pid"], r["cond"], r["temp"])] = [bool(e.passed) for e in pool.execute_all(prob, cands)]
    finally:
        pool.close()

    pull = defaultdict(list)
    cover = defaultdict(list)
    meanp = defaultdict(list)
    for r in gen["results"]:
        k = (r["cond"], r["temp"])
        if r["pull"] is not None:
            pull[k].append(r["pull"])
        ps = passed[(r["pid"], r["cond"], r["temp"])]
        if ps:
            cover[k].append(1.0 if any(ps) else 0.0)
            meanp[k].append(sum(ps) / len(ps))

    def avg(d, k):
        return (sum(d[k]) / len(d[k])) if d[k] else None

    conds, temps = ["E1", "E1p", "E2p", "E2"], [0.0, 0.8, 1.2]
    cells = {}
    for c in conds:
        for T in temps:
            k = (c, T)
            cells[f"{c}@{T}"] = {"pull": avg(pull, k), "coverage": avg(cover, k),
                                 "mean_pass": avg(meanp, k), "ns": 1 if T == 0.0 else 8}
    result = {"_label": "D2a — verb×provenance 2×2, all on a['fail']",
              "legend": {"E1": "self+improve", "E1p": "self+write-correct",
                         "E2p": "other+improve", "E2": "other+write-correct"},
              "n_problems": len(arts), "cells": cells}
    (REPO / "artifacts/dmeasure_d2a_verb_provenance.json").write_text(_json.dumps(result, indent=2))

    print("\n=== D2a — verb × provenance 2×2 (all conditioned on the SAME failed artifact) ===")
    print(f"{'cell':<8}{'attrib+verb':<22}{'PULL':>8}{'mean_pass':>11}{'cov':>7}")
    for c in conds:
        for T in temps:
            s = cells[f"{c}@{T}"]
            pl = f"{s['pull']:.3f}" if s['pull'] is not None else "  -  "
            mp = f"{s['mean_pass']:.3f}" if s['mean_pass'] is not None else "  -  "
            lab = result["legend"][c] if T == 0.0 else ""
            print(f"{c+'@'+str(T):<8}{lab:<22}{pl:>8}{mp:>11}{s['coverage']:>7.2f}")

    def cmp(a, b, T):
        sa, sb = cells[f"{a}@{T}"], cells[f"{b}@{T}"]
        if None in (sa["pull"], sb["pull"]):
            return
        print(f"  T={T}: {a} PULL {sa['pull']:.3f} mean_pass {sa['mean_pass']:.3f}  vs  "
              f"{b} PULL {sb['pull']:.3f} mean_pass {sb['mean_pass']:.3f}   "
              f"ΔPULL {sa['pull']-sb['pull']:+.3f} Δpass {sa['mean_pass']-sb['mean_pass']:+.3f}")

    print("\n-- PROVENANCE (E1 vs E2', same 'improve' verb, self vs other) --")
    for T in temps:
        cmp("E1", "E2p", T)
    print("-- VERB (E1 vs E1', same 'your' attribution, improve vs write-correct) --")
    for T in temps:
        cmp("E1", "E1p", T)
    print("\nprediction: verb explains most; provenance little. E1≈E2' → provenance "
          "near-irrelevant, distinct from Tsui. wrote artifacts/dmeasure_d2a_verb_provenance.json")


# ---- E7: repelled conditioning [PHASE_3B.md W1] ----
# The elimination argument excludes repulsive conditioning a priori; populate the
# region. Same protocol as dmeasure_gen (instruct, top_p 0.95, seed 17, ns=8, the
# committed 60-problem subset). Cells: E7@{0.8,1.2} explicit avoidance; E1@1.5 +
# E0@1.5 extend the attraction curve and the measured anchor. PULL for EVERY cell
# is distance to the same failed artifact (so E0@1.5's PULL extends W0a's anchor row).
_E7_INSTR = ("Do not repeat this approach. Take a substantially different approach "
             "and write a correct complete solution as a single fenced Python code block.")


@app.function(image=IMAGE, gpu="L4", volumes={"/cache": VOL}, timeout=7200)
def dmeasure_e7_gen(artifacts: list, n: int = 8):
    import difflib
    import os

    os.chdir("/root/rgr")
    from transformers import AutoTokenizer

    from rgr.generator.formatting import SYSTEM_PROMPT, build_prompt, extract_code
    from vllm import LLM, SamplingParams

    tok = AutoTokenizer.from_pretrained(MODEL)
    llm = LLM(model=MODEL, dtype="bfloat16", gpu_memory_utilization=0.90,
              max_model_len=4096, seed=17)

    def chat(user):
        return tok.apply_chat_template(
            [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user}],
            add_generation_prompt=True, tokenize=False)

    def user_prompt(a, cond):
        base = build_prompt(a["prompt"])
        if cond == "E0":
            return base
        if cond == "E1":
            return (base + f"\n\nYour previous attempt:\n```python\n{a['fail']}\n```\n"
                    "Write an improved complete solution as a single fenced Python code block.")
        if cond == "E7":
            return (base + f"\n\nA previous attempt that FAILED:\n```python\n{a['fail']}\n```\n"
                    + _E7_INSTR)

    cells = [("E7", 0.8), ("E7", 1.2), ("E1", 1.5), ("E0", 1.5)]
    out = []
    for cond, T in cells:
        prompts = [chat(user_prompt(a, cond)) for a in artifacts]
        sp = SamplingParams(n=n, temperature=T, top_p=0.95, max_tokens=512,
                            seed=17, logprobs=None)
        outs = llm.generate(prompts, sp)
        for a, req in zip(artifacts, outs):
            codes = [extract_code(o.text) for o in req.outputs]
            pulls = [1.0 - difflib.SequenceMatcher(None, cd, a["fail"]).ratio()
                     for cd in codes if cd]
            out.append({"pid": a["pid"], "cond": cond, "temp": T, "codes": codes,
                        "pull": (sum(pulls) / len(pulls)) if pulls else None})
    return {"results": out}


@app.local_entrypoint()
def dmeasure_e7_main(n_problems: int = 60):
    """W1 — repelled-conditioning arm. Generate E7@{0.8,1.2} + E1/E0@1.5 on the
    committed subset, execute locally (Daytona), apply the pre-registered branch
    rule vs the committed E0 cells. [PHASE_3B.md W1]."""
    import json as _json
    import math as _math
    import os
    from collections import defaultdict

    os.chdir(str(REPO))
    from rgr.config import load_config
    from rgr.data.humaneval import load_humaneval
    from rgr.execution.sandbox import DaytonaBackend
    from rgr.training.labels import ExecutionPool
    from rgr.types import Candidate, SplitRole

    m3 = _json.loads((REPO / "runs/modal/m3_candidates.json").read_text())
    labels = _json.loads((REPO / "runs/modal/m3_labels.json").read_text())["labels"]
    he = {p.problem_id: p for p in load_humaneval().checkout(SplitRole.HELDOUT_EVAL)}
    arts = []
    for pid, row, lab in zip(m3["problem_ids"], m3["candidates"], labels):
        fail = next((c["code"] for c, p in zip(row, lab) if not p and c["code"]), None)
        good = next((c["code"] for c, p in zip(row, lab) if p and c["code"]), None)
        if fail and good:
            arts.append({"pid": pid, "prompt": he[pid].prompt, "fail": fail, "correct": good})
        if len(arts) >= n_problems:
            break

    gen = dmeasure_e7_gen.remote(arts)
    (REPO / "runs/modal/dmeasure_e7_gen.json").write_text(_json.dumps(gen))

    cfg = load_config("configs/phase0_harness.toml")
    pool = ExecutionPool(lambda: DaytonaBackend(cfg.execution.timeout_seconds), size=8)
    passed = {}
    try:
        for r in gen["results"]:
            prob = he[r["pid"]]
            cands = [Candidate(text="", code=cd) for cd in r["codes"]]
            passed[(r["pid"], r["cond"], r["temp"])] = [bool(e.passed) for e in pool.execute_all(prob, cands)]
    finally:
        pool.close()

    # committed E0 per-problem coverage at matched T (dmeasure_exec.json)
    ex = _json.loads((REPO / "runs/modal/dmeasure_exec.json").read_text())
    e0_cov = {}  # (pid, "0.8"/"1.2") -> 0/1
    for key, v in ex.items():
        pid, cond, temp = key.rsplit("|", 2)
        if cond == "E0" and temp in ("0.8", "1.2") and v:
            e0_cov[(pid, temp)] = 1 if any(v) else 0

    pull, cover, meanp = defaultdict(list), defaultdict(list), defaultdict(list)
    e7_cov = {}
    for r in gen["results"]:
        k = (r["cond"], r["temp"])
        if r["pull"] is not None:
            pull[k].append(r["pull"])
        ps = passed[(r["pid"], r["cond"], r["temp"])]
        if ps:
            cover[k].append(1.0 if any(ps) else 0.0)
            meanp[k].append(sum(ps) / len(ps))
            if r["cond"] == "E7":
                e7_cov[(r["pid"], str(r["temp"]))] = 1 if any(ps) else 0

    def avg(d, k):
        return (sum(d[k]) / len(d[k])) if d[k] else None

    cells = {}
    for cond, T in (("E7", 0.8), ("E7", 1.2), ("E1", 1.5), ("E0", 1.5)):
        k = (cond, T)
        cells[f"{cond}@{T}"] = {"pull": avg(pull, k), "coverage": avg(cover, k),
                                "mean_pass": avg(meanp, k)}

    # pre-registered branch rule: paired E7 vs committed E0, per temp
    def paired(temp):
        pids = [p for (p, t) in e7_cov if t == temp and (p, temp) in e0_cov]
        b = sum(1 for p in pids if e7_cov[(p, temp)] and not e0_cov[(p, temp)])
        c = sum(1 for p in pids if e0_cov[(p, temp)] and not e7_cov[(p, temp)])
        n, delta = len(pids), (sum(e7_cov[(p, temp)] for p in pids)
                               - sum(e0_cov[(p, temp)] for p in pids)) / max(len(pids), 1)
        ptail = sum(_math.comb(b + c, k) for k in range(b, b + c + 1)) / (2 ** (b + c)) if b + c else 1.0
        return {"n": n, "delta_cov": delta, "wins_E7": b, "wins_E0": c,
                "one_sided_p_E7_gt_E0": ptail}

    contrasts = {t: paired(t) for t in ("0.8", "1.2")}
    fires_c = any(v["delta_cov"] >= 0.05 and v["one_sided_p_E7_gt_E0"] < 0.10
                  for v in contrasts.values())
    all_a = all(v["delta_cov"] <= -0.05 for v in contrasts.values())
    branch = "c_retract_overclaim" if fires_c else ("a_strengthened" if all_a else "b_restate_leq_iid")

    result = {"_label": "W1/E7 — repelled conditioning; branch rule pre-registered PHASE_3B.md",
              "aggregation_rule": "(c) if any temp fires; (a) if all temps <= -0.05; else (b)",
              "n_problems": len(arts), "cells": cells,
              "paired_vs_committed_E0": contrasts, "branch": branch}
    (REPO / "artifacts/dmeasure_e7.json").write_text(_json.dumps(result, indent=2))

    print(f"\n=== W1/E7 — repelled conditioning ({len(arts)} problems) ===")
    print(f"{'cell':<10}{'PULL':>8}{'mean_pass':>11}{'cov':>7}")
    for name, s in cells.items():
        pl = f"{s['pull']:.3f}" if s['pull'] is not None else "  -  "
        mp = f"{s['mean_pass']:.3f}" if s['mean_pass'] is not None else "  -  "
        print(f"{name:<10}{pl:>8}{mp:>11}{s['coverage']:>7.2f}")
    for t, v in contrasts.items():
        print(f"E7@{t} vs committed E0@{t}: dcov {v['delta_cov']:+.3f} "
              f"(E7-only {v['wins_E7']}, E0-only {v['wins_E0']}, one-sided p {v['one_sided_p_E7_gt_E0']:.3f})")
    print(f"BRANCH: {branch}")
    print("wrote artifacts/dmeasure_e7.json")
