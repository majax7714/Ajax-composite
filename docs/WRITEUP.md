# Register-Gated Refinement: an execution-grounded verifier carries load; a learned cross-step register does not

*Draft v1 — 2026-07-12. All numbers trace to committed artifacts and run
records; sources cited inline as `[file]`. B2 (in-context refinement baseline)
is now complete: pass@1 0.6220, it does not beat B1 (Branch A; §5.3,
[artifacts/h2_b2_result.json]) and does not change the H2 FAIL verdict.*

---

## Abstract

We test one claim in isolation: that an explicit internal state vector — a
*register* — updated across refinement steps and gating generation improves
correctness beyond what verification-plus-iteration already provides. We
built the minimal falsifiable version: a frozen 1.5B code generator, an
execution-trained verifier, and a 2.4M-parameter register stack (soft-prompt
injector, problem-conditioned initializer, GRU update) that is *the only
channel carrying information between refinement steps*. The design makes the
central ablation exact: freezing the register collapses the loop, by
construction, into verifier-reranked best-of-n — so the ablation and the
baseline are the same object.

Two pre-registered results. **H1 (positive):** a verifier fine-tuned on
sandboxed execution labels beats the generator's own token likelihood as a
confidence signal on held-out problems — AUROC 0.795 vs 0.696
(Δ = +0.099, 95% CI [+0.044, +0.153]) — and lifts best-of-8 selection from
0.628 to 0.671 pass@1. **H2 (negative, the novel claim):** register-gated
refinement ties the frozen-register baseline *exactly* at matched compute —
pass@1 0.6829 vs 0.6829 (Δ = 0.000, CI [−0.049, +0.055]). Diagnostics close
the mundane escapes: register dynamics were healthy, the verifier was not
stale, and imitation training verifiably steered teacher-forced likelihood
(−10.7% validation loss) — the steering simply did not survive sampling.
Under the pre-committed kill criterion, the register claim is dead at this
scale and training regime. We report the negative with its full causal
localization: every link in the chain worked except the last one.

---

## 1. The claim and its kill criteria

Three hypotheses were pre-registered with kill criteria before any
comparison ran ([build-brief.md] §1, [PHASES.md]):

- **H1** — external consistency beats self-fluency as a confidence signal.
  *Kill:* verifier AUROC fails to clear likelihood AUROC by a pre-registered
  margin (ΔAUROC ≥ 0.05 with 95% problem-level bootstrap CI excluding 0,
  [METRICS.md]) on held-out problems.
- **H2** — the register carries functional load: register-gated iterative
  refinement beats verifier-reranked best-of-n (B1) *and* in-context
  refinement (B2) at matched compute. *Kill:* FULL ties either within noise.
- **H3** — settling depth tracks difficulty under early stopping. Gated
  behind H2; not run (§5.4).

Gate order was enforced: H1 gated H2; a failed gate was never tuned past
(two verifier attempts failed or were disqualified *before* H1 passed — §4.2
— and the H2 verdict below was recorded without post-hoc iteration).

## 2. Architecture

Four components ([ARCHITECTURE.md]; decisions D1–D10 in [DECISIONS.md]):

- **G (generator):** Qwen2.5-Coder-1.5B-Instruct, 4-bit NF4, frozen
  throughout (D6). Sampling: temperature 0.8, top-p 0.95, max 512 new
  tokens, seed 17 ([configs/base.toml]).
- **r (register):** d_r = 128 (D1). Problem-conditioned initialization
  (D4): r₀ = W₀ · φ(problem), where φ is the mean-pooled last-layer hidden
  state of frozen G and W₀ is a learned 1536→128 projection.
- **U (update):** GRUCell over [φ(candidate); v] → r, with RMS
  normalization of r and a max-norm clip (1.0) on each delta. r is updated
  by U and by nothing else.
- **V (verifier):** register-blind (D3). Final form (V-v2b, D9): the same
  1.5B base model fine-tuned as a cross-encoder classifier via 4-bit QLoRA
  (LoRA r=16, α=32, dropout 0.05 on attention projections + trainable
  1-logit head) over raw `(problem, candidate code)` text with execution
  labels.
- **Injection:** r → 8 soft-prompt embeddings (learned 128→8×1536
  projection) prepended to G's context (D1). This is the only way r touches
  G.

**Inference loop.** r ← r₀(problem); repeat: candidate ← G(problem, r);
v ← V(problem, candidate); r ← U(r, φ(candidate), v). Refinement means
*regenerate under the updated register* — G never sees a previous candidate
(that is baseline B2). Therefore the register is the sole cross-step
channel, and freezing it makes the steps i.i.d. — **the ablated FULL is
literally the B1 baseline** (same function, one flag; [rgr/loop/refine.py]).
Because r₀ is problem-conditioned, B1 also conditions on the frozen r₀, so
FULL−B1 isolates exactly the register *updates* (D4). A secondary control
B1′ (no injection at all) isolates the static value of r₀.

## 3. Experimental setup

**Task and data.** Code generation, because execution gives ground truth.
Training/validation: sanitized MBPP, 427 problems (385 train / 42 val,
seed-17 split), checksum-pinned. Held-out evaluation: HumanEval, 164
problems, checksum-pinned, and guarded in code — the data layer raises on
any training-tagged access to HumanEval ([rgr/data/splits.py]). Two
held-out evaluations ("peeks") were spent in total across all verifier
iterations, logged in [PHASES.md].

**Execution.** All candidates run in Daytona cloud sandboxes via a
self-contained driver returning {passed, frac_tests, error_type} with
per-test granularity and alarm-based timeouts. Ground-truth validation:
8/8 canonical MBPP/HumanEval solutions pass end-to-end; hanging, partial,
and malformed candidates map to timeout / fractional credit / automatic
failure respectively ([tests/test_driver.py], live smoke 2026-07-10).

**Matched compute.** Frozen before any comparison ([COMPUTE_ACCOUNTING.md]):
the budgeted unit is one candidate generation; every H2 condition consumes
exactly N = 8 generations per problem, ledger-enforced (comparisons across
unequal ledgers raise). Verifier calls (a ~1.5B forward each under V-v2b,
D9), update calls, and token counts are reported as audit columns; all
conditions use identical decoding parameters. Candidates whose output
contains no extractable code block still consume budget and score as
automatic failures.

**Reproducibility.** The Phase-0 baseline was locked twice with the same
seed policy: runs lock_a and lock_b produced byte-identical candidate code
on 164/164 problems and identical token totals (204,553 generated tokens)
— a bit-for-bit replay ([PHASES.md] Phase-0 gate).

## 4. Results

### 4.1 Baselines (Phase 0)

164 HumanEval problems × 8 samples (1,312 generations; mean 156 generated
tokens/candidate; format discipline 1300/1312 = 99.1% extractable; 3
sandbox faults = 0.2%) [runs lock_a/lock_b; PHASES.md]:

| Quantity | Value |
|---|---|
| B0 pass@1 (unbiased, n=8) | **0.5922** |
| B1 pass@1, likelihood-reranked | **0.6280** |
| pass@2 / pass@4 / pass@8 | 0.6997 / 0.7804 / 0.8415 |

The gap that frames everything: a correct candidate exists in the 8-sample
pool 84.15% of the time, but self-fluency selection recovers only 62.80% —
~21 points of selection headroom.

### 4.2 H1: execution-grounded confidence beats self-fluency — PASS

Evaluation set: the frozen Phase-0 candidates (1,312 held-out HumanEval
candidates with execution labels and stored mean token log-probabilities).

Three verifier iterations, selected purely on MBPP validation
([PHASES.md] Phase 1):

1. **V-v1** — MLP over pooled frozen-G features [φ(problem); φ(candidate)]
   (D7). MBPP-val AUROC 0.7498. Held-out: 0.7082 vs likelihood 0.6961,
   Δ = +0.0121, CI [−0.0460, +0.0700] → **failed the margin**
   [artifacts/h1_result.json]. Diagnosis: a feature ceiling — a linear
   probe trained *in-domain on HumanEval itself* with these features
   reaches only 0.642, losing to raw likelihood (0.678) on the same split,
   and within-problem macro AUROC was near chance (0.579 vs 0.568).
2. **codebert-base cross-encoder** — MBPP-val AUROC 0.665 < v1's 0.750 →
   disqualified on validation; its held-out scores were never opened.
3. **V-v2b (QLoRA cross-encoder)** — MBPP-val AUROC by epoch:
   0.7727 / **0.7814** / 0.7589; epoch 2 selected. Held-out (the single
   remaining pre-registered peek):

| Metric (held-out, n=1,312 candidates, 164 problems) | V-v2b | Likelihood |
|---|---|---|
| AUROC (pooled) | **0.7951** | 0.6961 |
| Δ AUROC, 95% problem-bootstrap CI | **+0.0991 [+0.0441, +0.1531]** | — |
| Within-problem macro AUROC (90 mixed problems) | **0.7189** | 0.5680 |
| ECE (likelihood min-max normalized) | **0.1616** | 0.2207 |
| Brier | **0.2117** | 0.2671 |
| B1 pass@1 when reranking with it | **0.6707** | 0.6280 |

[artifacts/h1_v2b_result.json; PHASES.md]. **H1 passes at double the
pre-registered margin.** Note the mechanistically important split: pooled
AUROC mixes cross-problem difficulty signal, but the *within-problem*
number — what selection actually uses — moves from near-chance (0.568) to
0.719 only when the representation is fine-tuned end-to-end on execution
labels. Frozen-feature probes cannot get there (v1's ceiling), and generic
code encoders are too weak (codebert). Execution grounding works, but only
through the representation.

### 4.3 H2: the register carries no measurable load — FAIL (the core negative)

**Register training (D10).** With V register-blind there is no
differentiable V→register path, so imitation was implemented as *likelihood
steering on synthesized prefixes*: sample k failed candidates
(k ~ U{0..7}) from the Phase-1 label set, unroll r_k through U over their
(φ, v) pairs, and minimize teacher-forced −log P_G(passing candidate |
prompt, soft(r_k)); G frozen. 2,628 train / 240 val examples from problems
with both outcomes; 2,422,016 trainable parameters; batch 4, lr 1e-4,
3 epochs. **The objective itself trained successfully**: val teacher-forced
loss 0.1713 untrained → 0.1530 at the selected epoch (−10.7% relative;
epochs: 0.1592 / **0.1530** / 0.1566) [kernel rgr-phase2-train; PHASES.md].
Prefix v-scores came from V-v2b (integrity check: re-scoring reproduced val
AUROC 0.7802 vs the 0.7814 reported at training).

**The comparison.** 164 HumanEval problems, N = 8 generations per
condition, ledger-verified [runs/phase2/full_b1.jsonl,
artifacts/h2_result.json]:

| Condition | Cross-step channel | pass@1 |
|---|---|---|
| FULL (register updating) | learned register only | **0.6829** |
| B1 (register frozen at r₀) — *the ablation* | none | **0.6829** |
| B1′ (no injection; frozen Phase-1 artifact) | none | 0.6707 |
| B2 (in-context refinement) | prev. candidate in prompt | **0.6220** |

**Δ(FULL − B1) = 0.0000, 95% CI [−0.0488, +0.0549]** (10,000 problem-level
bootstrap resamples). The pre-committed kill criterion — FULL failing to
beat B1 — fired. The kill record is now complete: **FULL does not beat B2
either** (Δ(FULL − B2) = +0.0610, CI [−0.0122, +0.1341], includes 0), and B2
itself does **not** beat B1 (Δ(B2 − B1) = −0.0610, CI [−0.1341, +0.0122]) —
in-context text feedback, at ~2× the prompt-token cost (566,712 vs 281,064),
lands *below* parallel sampling. The Branch-A reading (§5.3) follows:
cross-step information of any kind buys nothing at this scale.

**Why this null is attributable, not ambiguous.** Every mundane explanation
was measured and excluded:

- *The register was not degenerate.* Mean ‖r‖ 12.12 (RMS-normalized scale
  √128 ≈ 11.3), mean per-step delta 1.757; no collapse, no blow-up
  ([rgr/register/diagnostics.py] on the FULL trajectories).
- *The verifier was not stale.* AUROC 0.7919 on FULL's own rollouts vs
  0.7951 at training time (threshold for refresh was a 0.05 drop).
- *Training was not a no-op.* The −10.7% teacher-forced val improvement
  above.
- *The tie is not aggregation hiding structure.* Paired per-problem
  outcomes: 103 both-pass, 43 both-fail, 9 FULL-only, 9 B1-only —
  perfectly symmetric disagreement. FULL's per-step pass rate is flat
  (0.60, 0.62, 0.61, 0.61, 0.57, 0.58, 0.60, 0.62 across steps 0–7), its
  mean verifier score shows no upward trend (0.693 → 0.705, non-monotone),
  and the argmax candidate's position is near-uniform over steps
  (29/18/22/18/21/12/21/23).

The causal chain therefore breaks at exactly one link: **likelihood
steering that is real under teacher forcing does not survive sampling.**
Eight soft-prompt embeddings driven by a 128-dim state can tilt token-level
log-probabilities of a designated target, but do not redirect which
solutions a 1.5B model actually samples.

The B1′ control (0.6707) sits 1.2 points below B1/FULL (0.6829), which
would suggest a small static benefit from r₀-conditioned injection alone —
but B1′ comes from a different sampling run (the frozen Phase-1
candidates), so this difference is within run-to-run noise and is *not
claimed*.

### 4.4 H3 — not run

H2 gated H3 ([build-brief.md] §1); with the register dead, "settling depth"
has no register semantics. A spin-off question survives — verifier-gated
adaptive *sampling* (early-stop best-of-n when v ≥ τ) vs fixed-n at matched
mean compute — and is future work, explicitly outside the original gates.

## 5. Discussion

### 5.1 What the experiment establishes

1. **The verification layer is where the load is.** The single largest
   correctness gain in the whole system came from replacing self-fluency
   with an execution-trained scorer (+4.3 pass@1 points at n=8; +15 AUROC
   points within-problem), and that gain required fine-tuning the
   representation, not probing frozen features.
2. **A learned cross-step latent, in its minimal honest form, added
   nothing** at 1.5B under an imitation regime — despite operating
   mechanically as designed and demonstrably steering teacher-forced
   likelihood. Because the register was the *only* cross-step channel and
   the ablation was the baseline, the null is attributable to the register
   updates specifically, not to confounds in the loop.
3. **Selection headroom remains large** (0.671 achieved vs 0.842 oracle at
   n=8): better verifiers still have ~17 points to claim, independent of
   any iteration mechanism.

### 5.2 Honest bounds on the negative

The kill criterion is scoped: *this* register (d_r=128, 8 soft tokens,
GRU), *this* training signal (likelihood-steering imitation; no RL), *this*
scale (1.5B, frozen G), *this* domain (short Python functions). Any of the
following could in principle revive the mechanism and none is tested here:
RL over the loop with execution reward (regime (b) of D2), gradient paths
through a register-conditioned verifier (D3's deferred coupling),
higher-bandwidth injection (FiLM / cross-attention), or a generator scale
where soft-prompt control is stronger. These are future experiments, not
rescues of the present claim.

### 5.3 B2 and the pre-registered branch verdict

The B2 run (in-context iterative refinement, N=8) completes the pre-registered
record: the kill statement was "FULL ties B1 *and* B2." B2 cannot change the
gate verdict — passing required beating both — but it answers whether *any* form
of cross-step information (even raw text feedback) beats parallel sampling in
this setting, which decides how the null should be read. The interpretation is
committed here **before B2's number is known** (full statement in
[PRE-B2-HANDOFF.md] §3):

- **Branch A — B2 also ties B1.** Cross-step information of any kind, including
  raw text, buys nothing here. The null then says nothing about registers; it
  says this task at this scale has no iteration headroom, as pass@8 = 0.842
  predicts. The experiment was uninformative about the hypothesis, and the next
  step is task redesign, not architecture.
- **Branch B — B2 beats B1.** Iteration pays, and a 128-dim latent through 8 soft
  tokens lost to putting the previous attempt in the context window: the register
  is architecturally parasitic to the in-context channel the transformer already
  optimizes for. The next step is an architecture rethink, not a task change.

**Standing prediction (recorded 2026-07-12, before the run): Branch A, ~65/35**
— pass@8 = 0.84 leaves little for iteration to do, and models do not reliably
self-correct without external feedback, which B2 as specified does not receive.

**Outcome (2026-07-12): Branch A — prediction held.** B2 pass@1 = 0.6220 (102/164)
vs B1 0.6829; Δ(B2 − B1) = −0.0610, CI [−0.1341, +0.0122]. B2 does not beat B1;
the point estimate and most of the CI mass put it *below* B1. So cross-step
information of any kind — including raw text feedback at ~2× the attention-FLOPs
(566,712 vs 281,064 prompt tokens) — buys nothing here, and in-context revision
on a scalar score if anything mildly hurt (the self-correction-without-external-
feedback pattern). The H2 null is therefore uninformative about registers *per se*
and informative about the task: no iteration headroom at this scale, corroborated
by DIAG-1 (the genuine unreachable set is < 26 of 164). **The next step is task
redesign (§5.2 / [PRE-B2-HANDOFF.md] §5), not an architecture change.** Prediction
left standing as written.

*Caveat under active test.* The abstract's and §4.3's framing — "every link in
the chain worked except the last one" — was challenged by the post-mortem in
[PRE-B2-HANDOFF.md] §1, which argued three links (refinement headroom, the
register's near-chance φ input, and the proxy training objective) were likely
broken upstream. Two diagnostics have now reported ([DIAGNOSTICS.md]):

- **DIAG-4 refutes the post-mortem's arithmetic and opens a genuine
  contradiction.** The imitation targets are short (median 28 tokens, not the
  156-token HumanEval average the post-mortem imported); trained target seq-prob
  is ~1.4e-2, samplable. But 1.4e-2 vs untrained 8.3e-3 is a **1.7× gain** in the
  probability of sampling the target — which, had it transferred, forbids a
  0.0000 pass@1 move. The resolution is that both calculations measured the wrong
  object: the imitation loss raises P(*this specific* passing string), while the
  goal is P(*any* passing program), a set of enormous cardinality. The null is a
  **generalization failure from strings to the correctness manifold** — which
  indicts starting with imitation (D2(a)) rather than execution-reward RL, a
  set-membership objective. "Training was not a no-op" stands; *what it bought*
  is the open question.
- **DIAG-1 sharpens the null.** FULL's 9 wins are 8 reselection + 1 within the
  resampling-noise floor set by B1's 2 symmetric wins; B1 (frozen register)
  reaches *more* oracle-empty solutions than FULL (5 vs 3). The register's
  *generative* contribution is non-positive — strictly stronger than the
  aggregate tie. And since 3–5 of the 26 "oracle-empty" problems dissolve under
  resampling, they were low-probability, not unreachable: the genuine generative
  headroom on this benchmark is even smaller than 16%.

What remains open is where the 1.7× teacher-forced gain dies. **DIAG-5** (does it
transfer to HumanEval at all?) forks it: a domain/length transfer failure vs a
teacher-forced/sampled gap the register cannot bridge (DIAG-3 control authority,
carrying a pre-registered entropy-killer hypothesis). The "every link worked
except the last" phrasing is retired in favor of this account.

### 5.4 The conceptual mapping, honestly closed

The brief's framing ([build-brief.md] §3) mapped chemical-state gating to
the register, the consistency manifold to the execution-trained verifier,
and Hamiltonian settling to inference-as-relaxation. The functional test
splits that mapping: the *external grounding* leg is supported (H1); the
*state-gated memory* leg is not (H2), in its minimal functional form; the
*settling* leg was never reached. No substrate claim was made and none is.

## 6. Reproducibility

Everything needed to reproduce is committed: pinned datasets (SHA256),
frozen configs ([configs/]), the compute-accounting rule (frozen before
any run, amendment log empty), seed policy (17 throughout), per-record
compute ledgers embedded in every result file, and the full gate log with
dates and both failed verifier attempts ([PHASES.md]). The Phase-0
reproduction was exact: byte-identical candidates across independent runs.
Infrastructure: Kaggle T4 kernels for all GPU stages (~25 T4-hours total),
Daytona sandboxes for all execution (12,100 sandboxed runs across
Phases 0–2; per-run sandbox-fault rates 0.2% / 0.0% / 0.3%, faults scored
as failures).

---

*Appendix pointers: architecture detail [ARCHITECTURE.md]; decision log
D1–D10 [DECISIONS.md]; metric estimators [METRICS.md]; verdict artifacts
[artifacts/h1_result.json, artifacts/h1_v2b_result.json,
artifacts/h2_result.json]; per-problem difficulty proxies
[artifacts/phase0_difficulty_proxy.csv].*
