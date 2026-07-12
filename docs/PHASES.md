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

- [x] V training set: 6,832 labeled candidates (427 MBPP problems × 16, temps
      0.2/0.8/1.0), pass rate 0.584, **0 sandbox faults**; phi features for
      train and for the frozen HumanEval eval set. *(2026-07-11, kernel
      rgr-phase1-data, batched sampling + 4-way pooled execution)*
- [x] V-v1 trained (pooled-feature MLP + aux heads, register-blind per D3).
      MBPP-val AUROC 0.7498.
- [x] Head-to-head on held-out problems: AUROC(V) vs AUROC(likelihood), plus
      ECE/Brier.
      - **Attempt 1 (V-v1, pooled-phi MLP): FAILED the margin.** Pooled AUROC
        V 0.708 vs likelihood 0.696; Δ = 0.012, CI [−0.046, +0.070].
        Diagnostics: macro *within-problem* AUROC only 0.579 vs 0.568 — and an
        in-domain linear probe on the same features (0.642) loses to
        likelihood (0.678), i.e. **feature ceiling**: mean-pooled frozen-G
        states don't carry the signal. Escalated per D7.
      - **Attempt 2a (codebert-base cross-encoder): disqualified on val**
        (0.665 < v1's 0.750); its held-out scores were never opened.
      - **Attempt 2b (V-v2b, QLoRA cross-encoder on Qwen2.5-Coder-1.5B):
        PASSED.** Val 0.7814 (epoch 2 of 3). Held-out: **V 0.7951 vs
        likelihood 0.6961, Δ = 0.0991, CI [0.0441, 0.1531]**. Secondaries all
        favor V — ECE 0.162 vs 0.221, Brier 0.212 vs 0.267, and macro
        within-problem AUROC **0.719 vs 0.568** (the reranking-relevant
        signal). Held-out peeks spent: 2 total (v1, v2b) — logged honestly.
- [x] B1 re-locked with V-v2b reranking: **pass@1 = 0.6707** (vs 0.6280
      likelihood-reranked, B0 0.5922, oracle pass@8 0.8415 — 17 points of
      selection headroom remain for iteration to claim in H2).
      Verifier of record: runs/kaggle/phase1_v2b/.../lora (adapter, epoch 2).

**Gate:** ΔAUROC ≥ 0.05, bootstrap CI excluding 0 (METRICS.md). —
**verdict: PASS (2026-07-11, V-v2b).** Confidence can be made trustworthy;
the register loop is earned (brief §11).

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
is dead; write the negative result up honestly. —
**verdict: FAILED (2026-07-12) — FULL ties B1 exactly.**
FULL 0.6829 vs B1 0.6829 at N=8 matched compute (164 HumanEval problems);
Δ = 0.0000, CI [−0.049, +0.055]. Not an artifact: register dynamics healthy
(mean step Δ 1.76, no collapse/blow-up), verifier not stale (0.792 vs 0.795),
per-step pass rates flat (no within-loop improvement), paired disagreements
symmetric (9 vs 9), best-step position uniform. The D10 imitation signal
(−11% val teacher-forced loss) did not survive sampling. B1′ control: 0.6707
(different sampling run — the +1.2pt static-r₀ effect is within run noise,
not claimable). B2 run pending quota completes the kill-criterion record
("ties both") but cannot change the gate verdict: the claim requires beating
both. Per brief §1: the register is dead as stated; this is the clean,
publishable negative the design was built to produce.

### Post-gate work — pre-registered 2026-07-12 (does NOT reopen the gate)

Full plan and committed predictions: [PRE-B2-HANDOFF.md]. This is B2 + four
exploratory diagnostics that decide *what the null means*, not whether it holds.
The post-mortem there argues the null was likely over-determined upstream of the
register (§1); DIAG-1/DIAG-4 adjudicate that. Nothing below is a rescue or a
retune.

- [ ] **B2** (in-context refinement, N=8, frozen spec) run on HumanEval; Δ(B2−B1)
      with CI; branch verdict recorded. **Pre-registered branch (committed before
      the number):** *Branch A* — B2 also ties B1 ⇒ no iteration headroom at this
      scale, task redesign next; *Branch B* — B2 beats B1 ⇒ register is
      architecturally parasitic to in-context text, architecture rethink next.
      **Standing prediction: Branch A, ~65/35.**
- [x] **DIAG-1** (CPU, 2026-07-12) oracle stratification. FULL's 9 wins = 8
      reselection + 1 B1-pool-empty; symmetry control B1 = 2; oracle-empty solves
      FULL 3 vs **B1 5**. Register generative effect **non-positive** (B1 ≥ FULL
      everywhere). *Prediction partly held:* "0–1 pool-empty" ✓, "FULL solves 0
      oracle-empty" ✗ (3) — but conclusion strengthened. → `artifacts/diag1_*.json`
- [x] **DIAG-4** (CPU, 2026-07-12, items 1–2) objective units. 0.1713/0.1530 =
      mean per-token NLL confirmed. **Prediction REFUTED:** real targets median
      28 tok (not 156), median trained seq-prob 1.4e-2, 97.8% > 1e-9 — samplable.
      Refutes §1.3 arithmetic but **opens the 1.7×-teacher-forced → 0.000-sampled
      contradiction**: reframed as a wrong-object failure (imitation raises
      P(specific string), goal is P(passing class)) → indicts D2(a) vs RL. Item 3
      (entropy split) pending GPU. → `artifacts/diag4_*.json`

  *After B2, run order (pre-registered 2026-07-12): DIAG-5 → DIAG-3 → DIAG-2 →
  DIAG-4 item 3 → DIAG-6.*
- [ ] **DIAG-5** (HumanEval re-analysis, GPU, **first after B2**) does the 1.7×
      teacher-forced gain transfer to HumanEval? *Prediction:* shrinks/vanishes →
      domain/length transfer failure (28-tok MBPP → 156-tok HumanEval). Survives →
      teacher-forced/sampled gap, DIAG-3 decisive.
- [ ] **DIAG-3** (MBPP val, GPU) control authority: does r move G's sampling?
      *Prediction:* KL < 0.05 nats, pass-rate CI straddles 0 → ~zero authority.
      **Directional hypothesis (pre-committed):** within-r_7 diversity <
      within-r_0 ⇒ register is an *entropy killer* (narrows reach).
- [ ] **DIAG-2** (MBPP val, GPU) register-probe: encoding vs transmission
      failure. *Prediction:* weak `passed` probe, decodable clock → encoding.
- [ ] **DIAG-6** (HumanEval gen, GPU, lowest) pass@50 on the 26 oracle-empty to
      bound headroom. *Prediction:* pass@50 ≥ 0.8 → genuine target ~5%, task
      redesign mandatory with a number.

Predictions are on the record so they can be wrong; outcomes get appended to
[PRE-B2-HANDOFF.md] §3–4, [DIAGNOSTICS.md], and the gate log below (one line per
run). The H2 verdict above stands regardless.

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

## Phase M — stack migration (GATED; infra refactor, no science change)

Kaggle/HF/4-bit → Modal/vLLM/fp16. Full plan and M0–M5 gates: [PHASE_M.md].
**HARD PRECONDITION (do not start):** the current record must be closed on the
old stack first — B2 + `h2_b2_result.json` + Branch verdict, and DIAG-2/3/5 +
DIAG-4 item 3 (and DIAG-6 if run on the old stack). Rationale: migrating changes
sampling numerics and permanently destroys the bit-for-bit Phase-0 lock; migrate
at a clean boundary, never mid-comparison. Precision call reserved as **D11
(open)**, settled at M0. Gates below (unchecked until M runs):

- [ ] M0 precondition + repo tag + D11 · [ ] M1 vLLM≡HF soft-prompt (greedy
      token-match) · [ ] M2 throughput ≥ 20× · [ ] M3 stat-equivalent re-baseline
      (fp16 shift stated/sized) · [ ] M4 V-v2b revalidation on fp16 candidates ·
      [ ] M5 new lock_a/lock_b + COMPUTE_ACCOUNTING amendment.

---

## Gate log

| Date | Phase | Verdict | Numbers | Notes |
|---|---|---|---|---|
| 2026-07-12 | 2 — Register loop (H2) | **FAIL** | FULL 0.6829 ≡ B1 0.6829, Δ 0.0000 CI [−0.049, +0.055]; register healthy, V not stale, per-step rates flat | The core claim's pre-registered kill fired on FULL-vs-B1; B2 pending for the complete record; do not tune past the gate |
| 2026-07-11 | 1 — Verifier (H1) | **PASS** | V-v2b heldout AUROC 0.7951 vs lik 0.6961, Δ 0.0991 CI [0.044, 0.153] · within-problem 0.719 vs 0.568 · B1(V) 0.6707 | QLoRA cross-encoder on Qwen2.5-Coder-1.5B, val-selected epoch 2; v1 failed (Δ 0.012), codebert DQ'd on val; 2 held-out peeks total |
| 2026-07-11 | 0 — Harness | **PASS** | B0 pass@1 0.5922 · B1(lik) 0.6280 · pass@8 0.8415 · format 99.1% | lock_a ≡ lock_b byte-identical (164/164); T4, seed 17, N=8, temp 0.8; difficulty proxy in artifacts/ |
