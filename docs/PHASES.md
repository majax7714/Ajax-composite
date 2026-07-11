# Phase plan and gates

Operational checklist version of brief §10–§11. A phase is done when every box
is checked and its gate verdict is recorded here (date + numbers). **Do not
proceed past a failed gate by tuning until it passes.**

---

## Phase 0 — Harness (no learning)

- [x] Model pinned: Qwen2.5-Coder-1.5B-Instruct, 4-bit inference confirmed on
      Kaggle **T4** (P100 is dead: Kaggle's torch build dropped sm_60 —
      kernels pin machine_shape=NvidiaTeslaT4). *(2026-07-10)*
- [x] Format-discipline layer: 20 MBPP completions inspected by hand
      (runs/kaggle/handcheck/stdout.txt). **Extraction 20/20**, all single
      fenced blocks, no narration; 12/20 passed execution (single-shot,
      failures are genuine model errors); partial-credit frac_tests values
      hand-verified. *(2026-07-10)*
- [x] Daytona execution wrapper live: `(problem, candidate) → {passed,
      frac_tests, error_type}`, with timeout and clean sandbox teardown.
      *(2026-07-10: driver + SDK backend; canonical solutions 8/8 pass;
      wrong/partial/hanging candidates map to wrong_answer / frac_tests /
      timeout correctly; sandbox survives hung candidates)*
- [x] Dataset splits wired: MBPP train/val, HumanEval strictly held out,
      split-discipline guard tested. *(2026-07-10: sanitized MBPP 427 +
      HumanEval 164, checksum-pinned; guard raises on contamination)*
- [x] B0 (single-shot) locked on HumanEval: **pass@1 = 0.5922** (unbiased over
      8 samples/problem, temp 0.8). *(2026-07-11, runs lock_a/lock_b)*
- [x] B1 (best-of-8, likelihood-reranked — no V yet) locked:
      **pass@1 = 0.6280**; pass@2/4/8 = 0.6997 / 0.7804 / 0.8415.
      Format discipline 1300/1312 (99.1%). Ledger: 1312 generations exactly,
      3 sandbox faults (0.2%). Note the headline gap for H1: oracle-rerank
      ceiling (pass@8) is 0.8415 vs likelihood's 0.6280 — ~21 points of
      selection headroom for the verifier to claim.
- [x] Numbers frozen; per-problem B0 pass rates (H3 difficulty proxy) committed
      at artifacts/phase0_difficulty_proxy.csv; full records in Kaggle kernel
      output (rgr-lock-a / rgr-lock-b) and runs/kaggle/.

**Gate:** reproducible baseline pass@1 (two runs, same seed policy, matching
numbers). — **verdict: PASS (2026-07-11).** lock_a vs lock_b: byte-identical
candidates on 164/164 problems, identical (n, c) everywhere, identical token
totals (204,553). Effectively a bit-for-bit replay.

## Phase 1 — Verifier (H1)

- [ ] V training set: candidates per MBPP-train problem across temperatures,
      executed and labeled. Budget the sandbox time — labels are the expensive
      line item (brief §7).
- [ ] V-v1 trained (pooled-feature MLP + aux heads, register-blind per D3).
- [ ] Head-to-head on held-out problems: AUROC(V) vs AUROC(likelihood), plus
      ECE/Brier.
- [ ] B1 re-locked with V reranking (replacing likelihood reranking).

**Gate:** ΔAUROC ≥ 0.05, bootstrap CI excluding 0 (METRICS.md). If marginal:
escalate to V-v2 (fine-tuned encoder, D7) **once**; if still flat, H1 is dead —
stop, per the kill criterion. — *verdict: pending*

## Phase 2 — Register loop (H2, the core)

- [ ] r_0 encoder, injector, U implemented; register diagnostics logging on.
- [ ] Imitation dataset: loop rollouts with untrained/random U; keep
      trajectories reaching a pass; train U + injector + encoder (G, V frozen).
- [ ] Verifier staleness check after U training; refresh V if AUROC dropped
      > 0.05 on current-policy rollouts.
- [ ] FULL vs B1 vs B1′ vs B2 on HumanEval at matched compute (N = 8
      pre-registered; curve at N ∈ {1,2,4,8,16} secondary).
- [ ] Register dynamics reviewed: is r moving without blowing up? (Expect to
      spend most debugging time here — brief §8.)

**Gate:** FULL beats **both** B1 and B2, CIs excluding 0. Tie either → register
is dead; write the negative result up honestly. — *verdict: pending*

## Phase 3 — Adaptive compute (H3)

- [ ] τ swept on MBPP validation, fixed value frozen (D5).
- [ ] Early-stopping runs on HumanEval; steps-to-stop vs difficulty proxy.
- [ ] Adaptive vs fixed-K at matched mean generations; Pareto curve.

**Gate:** positive depth–difficulty correlation *and* adaptive ≥ fixed-K at
matched mean compute. Weaker gate: failure doesn't sink H2. — *verdict: pending*

## Post-H3 (only after all three gates)

Scale to 4B QLoRA · FiLM / cross-attention injection · RL register training ·
register-conditioned V (flip `verifier.sees_register`, retrain V) · d_r and k
sweeps.

---

## Gate log

| Date | Phase | Verdict | Numbers | Notes |
|---|---|---|---|---|
| 2026-07-11 | 0 — Harness | **PASS** | B0 pass@1 0.5922 · B1(lik) 0.6280 · pass@8 0.8415 · format 99.1% | lock_a ≡ lock_b byte-identical (164/164); T4, seed 17, N=8, temp 0.8; difficulty proxy in artifacts/ |
