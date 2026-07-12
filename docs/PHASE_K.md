# Phase K — lift-and-shift Kaggle → Modal (SAME stack, T4)

*Written 2026-07-12. Purpose: get off the Kaggle GPU-quota wall **without changing
the stack**, so the remaining diagnostics run on the exact configuration that
produced Phases 0–2 and their numbers connect to the results they diagnose.*

---

## 0. Platform ≠ stack — the distinction Phase M got wrong

**Modal is a platform. fp16+vLLM is a stack.** These are independent choices, and
[PHASE_M.md] wrongly bundled them. The remaining diagnostics were never
Kaggle-specific — they are **stack**-specific: they must run on the same
`HF generate()` + bitsandbytes NF4 + Qwen2.5-Coder-1.5B-Instruct configuration
that produced Phases 0–2.

Modal offers **T4** — the same Turing sm75 silicon Kaggle gives. So Phase K runs
the **exact old stack on rented Modal T4**: no fp16, no vLLM, no precision change,
no new generation backend, no broken lock.

> **Phase K = lift-and-shift. Zero science change. Same stack, different rented GPU.**

If you find yourself editing model loading, precision, or the generation backend,
**you have left Phase K** — that is Phase M (fp16 + vLLM + L4, a separate later
task; do not begin any part of it here). Modal is arguably *safer* than Kaggle for
this: Modal images are defined in code and cached, so pinning is more reliable,
where Kaggle's base image mutates underneath you.

Auth verified 2026-07-12: `rgr-modal.txt` (token-id `ak-…` + token-secret `as-…`)
authenticates (`modal app list` → 0); file is git-ignored (`rgr-modal*`).

---

## 1. Env capture — before Kaggle's image rolls out from under us

You cannot pin what you did not record. Repo check (2026-07-12): **no complete
spec exists** — no `env/`, no lockfile, no `requirements.txt`; committed logs show
only "Torch 2.9"; `pyproject` carries loose lower bounds; the kernel runner adds
`daytona peft -U bitsandbytes>=0.46.1` on top of Kaggle's base image. So a capture
is required.

**Capture (free Kaggle CPU session — no GPU quota):** `pip freeze` (full);
`torch.__version__` / `torch.version.cuda` / cuDNN; transformers, bitsandbytes,
accelerate, peft, datasets; `nvidia-smi` driver+CUDA; Python version; base image
tag/date; **the exact Qwen2.5-Coder-1.5B-Instruct revision SHA** (pin the
revision, not just the repo).

**Fidelity caveat (flag, do not paper over):** a Kaggle *CPU* session ships a
CPU-only torch build, so its `torch` line will not match the GPU stack's
`torch 2.9+cuXX`. The Python-level packages (transformers/bnb/accelerate/peft/
datasets/python) are shared; take `torch`+CUDA from the GPU logs ("Torch 2.9") and
the GPU driver from a prior GPU run's `nvidia-smi` if recoverable. The Modal image
is pinned to that reconstruction; **GATE K1 is the arbiter** of whether the pin is
faithful enough (see §2). This matches K1's own design, which tolerates small
numeric divergence for mechanistic diagnostics.

**Output:** `env/kaggle_phase0_2.lock` + `env/CAPTURE.md` (date, method, the
CPU/GPU caveat). Commit it — this artifact is the bridge; everything downstream
depends on it.

---

## 2. Modal image + GATE K1

**Image.** Pinned to `env/kaggle_phase0_2.lock` (same CUDA/torch/bnb).
`@app.function(gpu="T4")`. Model weights + HF cache on a **persistent Volume**
(kills the 3 GB per-session re-download Kaggle forced). **Preemptible** (default;
non-preemptible is a 3× multiplier and buys nothing for batch research).

**GATE K1 — partial Phase-0 replay (hard gate, ~0.7 T4-hr ≈ $0.40).** Replay ~20
Phase-0 lock problems on Modal T4; compare **byte-for-byte** against `lock_a`.

| K1 outcome | meaning | action |
|---|---|---|
| **Byte-identical** | stack transferred cleanly | all diagnostics valid; proceed |
| **Small tail divergence** (a few tokens deep; cuBLAS/driver numerics) | does **not** block — DIAG-2/3/4/5 are mechanistic measurements, not gate replays | document precisely; log the **first amendment** in [COMPUTE_ACCOUNTING.md]; proceed |
| **Systematic divergence** (differs at tokens 1–3, or obvious quality shift) | the image is wrong | **STOP**, fix the pin. Do not proceed "to save time" |

Do not skip K1 — every diagnostic below inherits its validity from it.

---

## 3. Remaining diagnostics on Modal T4 (specs unchanged)

Per [PRE-B2-HANDOFF.md] §4 and the DIAG-5 addendum — **no spec changes**.
Held-out hygiene stands: DIAG-2 and DIAG-3 run on **MBPP val**, not HumanEval.
Run order and pre-registered predictions are unchanged (predictions stand; append
outcomes only).

| diagnostic | what it settles | est. cost |
|---|---|---|
| **DIAG-4 item 3** | entropy split of the −10.7% teacher-forced gain: boilerplate vs decision tokens? | ~$0.10 |
| **DIAG-5** | does the 1.7× teacher-forced gain transfer to HumanEval? domain/length shift vs teacher-forced→sampled gap. Forward passes on already-labeled Phase-0 candidates — no new generation, no new peek. | ~$0.10 |
| **DIAG-2** | register probes (MBPP val): is v/passed/error_type decodable from r_t? encoding vs transmission. Include the `t` control (clock). | ~$0.35 |
| **DIAG-3** | control authority (MBPP val): does r move G's sampling? edit distance within-r₀/within-r₇/across, token KL, pass-rate Δ. Report within-set diversity — the pre-registered **entropy-killer** hypothesis (DIAG-7 already corroborates it from pool stats). | ~$0.70 |

DIAG-6 is **descoped** ([DECISIONS.md] D12) → Phase 3 benchmark selection.

---

## 4. Budget

| item | est. |
|---|---|
| DIAG-7 (local CPU) | $0 (done) |
| Env capture (Kaggle CPU) | $0 |
| GATE K1 replay | ~$0.40 |
| DIAG-4 item 3 + DIAG-5 | ~$0.20 |
| DIAG-2 | ~$0.35 |
| DIAG-3 | ~$0.70 |
| **Total** | **< $2** |

Entirely inside Modal's $30/month free credit. Kaggle leaves the critical path
permanently. [COMPUTE_ACCOUNTING.md]: budgeted unit ("one candidate generation")
is **unchanged** — only the rented hardware changed; note it in the amendment log
(written at K1, with the byte-diff outcome).

---

## 5. Do NOT start Phase 3 or Phase M in parallel

Not an infra rule — a **dependency** rule. DIAG-3 and DIAG-7 determine what Phase 3
should test: if the diversity-tax hypothesis holds, Phase 3 must **not** condition
on the failed candidate at all — it must condition on an *abstraction* of the error
(which test failed, what class) precisely to avoid anchoring the model to its own
mistake. That is a materially different architecture from "put the traceback in the
loop," and you only know to build it if the diagnostics land first. Building Phase 3
now assumes the diagnostics come back as hoped — exactly the move gate discipline
exists to prevent. **Phase 3 design begins when the diagnostic record is closed.
Not before.** Phase M (fp16+vLLM+L4) is later still, after Phase 3 design, as its
own no-science-change refactor with its own re-lock.

---

## 6. Sequence & deliverables

1. **[done]** DIAG-7 (local CPU). B2 log entry corrected.
2. Capture Kaggle env spec (free CPU). Commit `env/`.
3. Build Modal T4 image → **GATE K1** (Phase-0 replay).
4. DIAG-4 item 3 → DIAG-5 → DIAG-2 → DIAG-3 on Modal T4.
5. Close [DIAGNOSTICS.md]: procedure, number, prediction-held for each.
6. Then Phase 3 design (informed by DIAG-3 + DIAG-7); then Phase M.

**Deliverables:** `env/kaggle_phase0_2.lock` + `env/CAPTURE.md`; this PHASE_K.md
gate log (K1 verdict, date, byte-diff); `artifacts/diag{4item3,5,2,3}_*.json`; a
closed [DIAGNOSTICS.md]; first amendment entry in [COMPUTE_ACCOUNTING.md];
DIAG-6 descope recorded ([DECISIONS.md] D12, done).

### K1 gate log

| Date | Replay N | Byte-diff vs lock_a | Verdict | Notes |
|---|---|---|---|---|
| _pending_ | ~20 | _pending_ | _pending_ | Modal T4, image pinned to env lock |
