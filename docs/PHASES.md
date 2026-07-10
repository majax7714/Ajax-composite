# Phase plan and gates

Operational checklist version of brief §10–§11. A phase is done when every box
is checked and its gate verdict is recorded here (date + numbers). **Do not
proceed past a failed gate by tuning until it passes.**

---

## Phase 0 — Harness (no learning)

- [ ] Model pinned: Qwen2.5-Coder-1.5B-Instruct, 4-bit inference confirmed on
      target GPU (Kaggle T4/P100).
- [ ] Format-discipline layer: clean, executable code extracted on 20 MBPP
      problems inspected *by hand* (brief §11.1). Record the extraction rate.
- [ ] Daytona execution wrapper live: `(problem, candidate) → {passed,
      frac_tests, error_type}`, with timeout and clean sandbox teardown.
- [ ] Dataset splits wired: MBPP train/val, HumanEval strictly held out,
      split-discipline guard tested.
- [ ] B0 (single-shot) locked on HumanEval.
- [ ] B1 (best-of-n, likelihood-reranked for now — no V yet) locked at N = 8.
- [ ] Numbers frozen on the dashboard; per-problem B0 pass rates saved (they are
      the H3 difficulty proxy).

**Gate:** reproducible baseline pass@1 (two runs, same seed policy, matching
numbers). — *verdict: pending*

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
| — | — | — | — | — |
