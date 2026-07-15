# Register-Gated Refinement, and When Cross-Step Conditioning Pays — a full experimental record

*An execution-grounded verifier carries load; a learned cross-step register does
not; the register null, once fully localized, reframes the question — from "does
this architecture work" to "on what task can iterative refinement pay at all" — and
that reframing drives a stack rebuild (Phase M) and a pre-registered benchmark search
(Phase 3) whose first hard result is itself a negative worth publishing.*

*Living record — last updated 2026-07-15 (Phase-3R audits **RESOLVED**: **H1
killed-as-artifact** by the landed R1b.2d retrain, **F2 retracted-as-structural** by the
completed R2 grid, E5/E1 subset confound closed clean). All numbers trace to committed artifacts and
run records; sources cited inline as `[file]`. This is the canonical results document for
the whole experiment. **New conversation: start with §10 (working method) and §9.5 (live
status + restart ordering).** §§1–5 are the register experiment (Phases 0–2 + diagnostic
teardown, complete and frozen); §6 is the throughput/stack rebuild (Phase M, complete);
§7 is Phase 3 (reframe + benchmark screen: gate NEGATIVE/F2 as originally scoped — **the
R2 audit retracted F2's structural reading 2026-07-15; see §9.2**); §9 is the
**current phase (Phase 3R** — auditing the two live claims H1 and F2, pinning the
anchoring→escape mechanism; **R1 and R2 both resolved 2026-07-15 — both audited claims
fell** (H1 artifact §9.1, F2 retracted §9.2); §9.3.1 is the current frontier of
thought). §10
is the durable **working method**; §11 is external **references** (Tsui, Olausson,
Self-Debug, "How Many Tries", Kamoi). Every §4.2/§7.4 claim carries a Phase-3R audit
banner pointing into §9.*

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
localization (§5.3): a **two-component** failure — the static injection is a
transfer failure, the update dynamics a mechanism failure from input starvation.

**Beyond the register (§§6–7).** Eleven diagnostics turn the bare null into a
positive question: cross-step conditioning can only pay where the task has
*reachable-but-improbable* headroom, and it must condition on an **abstraction** of
the error, not the failed candidate (conditioning on the candidate anchors the model
to its own mistake — measured, DIAG-8/10). Pursuing that question required a stack
rebuild — **Phase M** ports the generator from HF/4-bit to vLLM/bf16 for a **100×
throughput** gain (validated register path, re-based baselines, and two carry-forward
findings: the verifier must be retrained on the new candidate distribution, and
bit-for-bit reproducibility gives way to a statistical standard) — and a
pre-registered **Phase 3** benchmark screen. Phase 3's first hard result is a
documented negative that generalizes. Across **two benchmark families** (BigCodeBench,
LiveCodeBench), two execution paradigms (unit test, stdin/stdout), three difficulty
tiers, and two model scales, **no configuration offers the reachable tail refinement
needs — pass@50 − pass@8 is capped at ~0.09–0.12, never the required ≥0.15** (Finding
F2). The gate returns a **negative**, and it is structural: a code model at this scale
solves a problem within a few samples or not at all (a peaked, not heavy-tailed,
per-problem solution distribution), so pass@k saturates and sample-based refinement
has almost no runway — the same "solve-within-8-or-not" shape that sank HumanEval,
now shown to be a property of the whole task family, not an unlucky choice. **That
negative — a precise statement of where iterative refinement can and cannot live — is
the substantive Phase-3 result**, and it redirects the next experiment toward
feedback-driven recovery (does an error abstraction let the model reach solutions it
could not i.i.d.-sample?) rather than a search for a heavy-tailed code benchmark that
may not exist. A methodological result falls out too: subset screening on the *first
n* problems was ~2× optimistic vs random — caught by the confirmation step before any
training was built on it.

**Phase 3R (§9, in progress).** Before H1 and F2 are called final, both are audited
against the Phase-0 choices they inherit. **R1** asks whether H1 is a *quantization
artifact*: on bf16 the stack-invariant Selection-Efficiency metric shows likelihood
alone (SE 0.305) nearly reproduces the 4-bit verifier benefit (SE 0.315) — the decider
is a bf16 verifier retrain (interrupted by a 2026-07-14 power outage before its verdict
computed — rerun pending; see §9.5). **R2** asks whether F2's shallow tail is
*decoding-induced* (top-p 0.95 + T 0.8 + Instruct all suppress the improbable tail);
it re-screens with a base completion model, top-p 1.0, and a temperature sweep — base
path validated, base T=0.8/1.0/1.2 screened, instruct arm partial (same outage). Spun
off from the DIAG-8 anchoring finding, **D-measure**
converts "conditioning on a failure is harmful" into a law: repair is governed by
**escape distance** (how far a generation diverges from the failed artifact), the
benefit is a **coverage/diversity** effect not a per-sample-quality one (D2b), the
attractor is **content-blind** and **provenance-independent** — distinct from Tsui's
self-anchoring blind spot (D2a) — and the reconciliation with the self-refinement
literature is that **escape requires direction, and direction requires rich feedback**.
That last statement is the hypothesis R3 (conditional reachability) now tests directly.
The law's sharpest consequence (§9.3.1) is an **elimination argument**: undirected
failure-conditioning asymptotes toward i.i.d. sampling (full escape = the artifact
discarded = resampling), so it is *strictly dominated by resampling at matched compute*;
the only mechanism that can beat i.i.d. is **directed** escape, which makes R3 the sole
surviving refinement hypothesis rather than one option among several. This converges,
from a mechanism, on the compute-matched conclusion of Olausson et al. (2024). One
confound of our own (E5's subset overlap; §9.3.1) is flagged for a free matched-control
recompute before the content-blindness/neutral-attractor claim is called final.
**Resolved 2026-07-15:** the R2 grid completed and the gate **fired on its retraction
branch — F2 is retracted-as-structural**: with the tail un-suppressed, LiveCodeBench-easy
has a feasible *region* (the whole base arm plus instruct T=1.2; headroom up to +0.25
at in-band coverage) while BigCodeBench stays infeasible at every cell — the shallow
tail was a property of benchmark-family × decoding, not of code at this scale, and
Phase 3b now has a qualifying task (§9.2). The E5/E1 recompute closed clean (all
conditions shared one identical subset; claims stand with a scope note — §9.3.1).
**Resolved 2026-07-15, completing the audit:** the R1b.2d retrain landed and the
**kill line fired — H1 is a quantization artifact** (retrained-V bf16 SE **0.090** vs
likelihood 0.305, inside the registered artifact band). The SE matrix *inverts* across
pools: the same retrained verifier scores **0.364** on the old 4-bit pool — better than
the original — so the selection edge belonged to the quantization-corrupted candidate
pool (corrupted likelihood + easy-to-discriminate failures), never to the verifier.
**Both audited claims have now fallen** — H1 killed-as-artifact (§9.1), F2
retracted-as-structural (§9.2); what survives Phase 3R is the register null, the
escape-distance law, and the LCB-easy feasible region.

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

### 4.2 H1: execution-grounded confidence beats self-fluency — PASS on the retired 4-bit stack; **KILLED by audit 2026-07-15 (R1b.2d: quantization artifact — §9.1)**

> **⚠ Under audit ([PHASE_3R.md] R1; full detail §9.1).** R1a cleared H1 of the vLLM
> logprob bug (port-introduced, never touched the HF Phase-1 likelihood arm; Phase-0
> lock 0/1312 null `mean_logprob`). **R1b is the open, high-stakes leg:** on the
> stack-invariant Selection-Efficiency metric (SE = (selected−random)/(oracle−random)),
> bf16 *likelihood alone* reaches SE 0.305 — nearly the entire 4-bit V benefit
> (SE 0.315) — so H1's edge may have been "V beats *quantization-corrupted* likelihood."
> Free checks closed the mundane escapes (R1b.2b: V does discriminate subtle
> wrong_answer-only failures, within-AUROC 0.751; R1b.2c: not a length artifact). **The
> decider is R1b.2d — a bf16 verifier retrain; kill line: retrained-V bf16
> SE ≤ 0.305 → H1 does not survive de-quantization.** No H1 claim is final until it
> lands — and it has **not** landed: the retrain was killed by a 2026-07-14 power
> outage at epoch 3/3 (~step 450) with no checkpoint persisted, so the verdict never
> computed and a full rerun is required (§9.5). Numbers below stand as originally
> computed on the retired 4-bit stack.

> **AUDIT RESOLVED (2026-07-15): H1 KILLED — quantization artifact.** The R1b.2d
> retrain landed (fifth attempt; run-loss ledger §8) and the pre-committed kill line
> **fired**: retrained-on-bf16 V reaches SE **0.090** on the bf16 pool vs likelihood's
> **0.305** — inside the registered artifact band (0.05–0.10), against a registered
> prediction of 0.33–0.38 (wrong, and recorded as such). The decomposition is an
> **inversion** that localizes the artifact in the *pool*, not the verifier: the same
> bf16-retrained V scores SE **0.364** on the old 4-bit pool (better than the original
> Phase-1 V's 0.315), while likelihood there manages only 0.144. The 4-bit pool was
> doubly special — corrupted likelihood (weak opponent) and easy-to-discriminate
> failures (within-AUROC 0.7189 there vs 0.6377 on bf16). The table below therefore
> stands as a correct measurement of the retired stack, but its transferable content is
> a negative: **at 1.5B on a clean generator, an execution-trained cross-encoder does
> not beat the generator's own token likelihood as a selection signal.** No
> verifier-selection stage carries into any bf16-stack design
> ([artifacts/r1b2d_verifier_retrain.json]; [PHASE_3R.md] R1b.2d RESOLUTION; §9.1).

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
itself does **not** beat B1 (Δ(B2 − B1) = −0.0610, CI [−0.1341, +0.0122]).
B2's cross-step channel was the **previous candidate plus a scalar
verifier-confidence estimate, with no execution feedback** (intrinsic
self-refinement — distinct from execution-grounded self-correction, which B2 does
not test). Conditioning on the previous attempt — higher-bandwidth than FULL's
register, at ~2× the prompt-token cost (566,712 vs 281,064) — buys nothing; the
pass@1 point estimate sits below B1 though its CI crosses 0. The Branch-A reading
(§5.3) follows: cross-step conditioning of any kind buys nothing at this scale.

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
4. **Pool coverage falls with cross-step bandwidth; the text channel's harm
   is real, the register's is null.** Oracle pool coverage (pass@8) is ordered
   **B1 0.848 > FULL 0.823 > B2 0.707** by how much each condition conditions
   on prior failed attempts (none / 128-dim latent / full previous-candidate
   text; DIAG-7, [DIAGNOSTICS.md]). Paired McNemar (DIAG-7b) shows the register
   step (FULL vs B1, a 4-problem gap) is **not significant** (exact p = 0.39);
   only B2's 23-problem crash is established (p < 1e-3). So the register is
   **null on coverage, not a demonstrated shrinker** — the point estimate is on
   the harm side but within paired noise. The text channel's harm, however, is
   **content anchoring**, not a formatting artifact: conditioning on the failed
   candidate makes B2's consecutive candidates only **0.35× as diverse** as
   i.i.d. draws (DIAG-8, a format-matched contrast) while pass rate *declines*
   0.61→0.40 across steps, with a local error-echo (DIAG-9b: adjacent-failure
   error-type match 0.85 vs 0.66 non-adjacent, +0.19 over the correct
   within-problem baseline; part of the decline is also no_code output-collapse)
   — G locally loops on its own mistake. This was structurally primed: at ~0.85 i.i.d. pool coverage
   there is almost nothing for cross-step conditioning to add and much for
   anchoring on a *shown-wrong* candidate to subtract. The null is therefore not
   "the register did nothing" but "on a saturated task, conditioning on prior
   *failures* is at best inert (latent register) and at worst actively harmful
   (raw text), scaling with channel bandwidth."

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
the point estimate and most of the CI mass put it below, though the CI crosses 0
so we make no significance claim on pass@1. **What B2's channel was:** the
previous candidate plus a scalar verifier-confidence estimate, with **no execution
feedback** — intrinsic self-refinement, which is distinct from execution-grounded
self-correction (feeding the actual error); B2 is evidence about the former only.
Conditioning on the previous attempt — higher-bandwidth than FULL's register, at
~2× the prompt-token cost (566,712 vs 281,064) — buys nothing. Direction is
corroborated not by the pass@1 CI but by the *direct* pool-coverage measurement
(DIAG-7: B2 0.707 vs B1 0.848). The H2 null is therefore uninformative about
registers *per se* and informative about the task. **Why redesign:** the ceiling
(pass@8 = 0.842, minus the 3–5 problems DIAG-1 shows dissolve under resampling) is
*channel-independent* — the argument is the ceiling, not "iteration is dead."
Prediction left standing as written.

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

The full diagnostic record is now **closed** (10 diagnostics, [DIAGNOSTICS.md]
synthesis). The null is not a flat over-determination but a **two-component**
failure, one per learned part. **W₀ (static injection) is a *transfer* failure:**
its trained steering is ×1.33 in-domain but *reverses* to ×0.28 out-of-domain
(DIAG-5) — a learned prompt overfit to MBPP length, with the objective itself sound
(DIAG-4: samplable targets, 99.7% of the gain on the right decision tokens). **U
(the update dynamics — the actual RGR hypothesis) is a *mechanism* failure,
in-domain:** on MBPP val (U's training domain) r₀→r₇ moves pass rate by exactly
0.000, and the reason is a closed causal chain — φ near-chance → r_t barely encodes
correctness (DIAG-2, passed AUROC 0.558, no clock) → uninformative updates → KL
0.117 nats of *directionless* perturbation (DIAG-3; entropy-killer refuted) → Δpass
0.000. One word: **input starvation.** The outcome frame explains why neither could
have won: the task is saturated (DIAG-1/7), and conditioning on a failed candidate
anchors G to its own mistake (DIAG-8: consecutive candidates 0.35× as diverse as
i.i.d.; DIAG-9b: local error-echo +0.19 adjacent-vs-non-adjacent, pass 0.61→0.40
partly no_code collapse), while the register's own coverage effect is null not
harmful (DIAG-7b: FULL−B1 p = 0.39). The "every link
worked except the last" phrasing is retired. **The prioritization this hands
Phase 3:** in-domain/length-matched training fixes only W₀ (U already fails
in-domain); the single lever that touches U is **enriching what it conditions on —
a compact abstraction of *why* the last attempt failed, explicitly not the failed
candidate text** — and **DIAG-10 shows removing the candidate removes the *harm***:
with identical execution feedback, the candidate-anchored channel anti-refines while
the abstraction channel does not (ABSTRACT +0.088 vs B2+fb −0.162, +0.225 late-step
gap, several SE). Whether the abstraction adds *benefit* is untested — ABSTRACT ties
the B1 control on this saturated subset, a null that is uninformative (no headroom,
~2-bit signal). So feedback-benefit is Phase 3's **hypothesis** (its H1 gate), not an
established result. That, an on-policy set-membership objective, and a task with
genuine headroom are Phase-3 design, not extensions of this record.

### 5.4 The conceptual mapping, honestly closed

The brief's framing ([build-brief.md] §3) mapped chemical-state gating to
the register, the consistency manifold to the execution-trained verifier,
and Hamiltonian settling to inference-as-relaxation. The functional test
splits that mapping: the *external grounding* leg is supported (H1); the
*state-gated memory* leg is not (H2), in its minimal functional form; the
*settling* leg was never reached. No substrate claim was made and none is.

## 6. Phase M — the stack rebuild that made Phase 3 feasible

Phase 3 is materially larger than Phases 0–2 (more conditions, a large-k pass@k
screen, on-policy training), so throughput stopped being a convenience and became a
prerequisite. Phase M ([PHASE_M.md]) is a **no-science-change** port of the stack —
HF `generate()` + bitsandbytes 4-bit NF4 on Kaggle/Modal T4 → **vLLM continuous
batching + bf16 on Modal L4** ([DECISIONS.md] D11) — done at a clean phase boundary,
with the old stack tagged (`pre-phase-m-hf-nf4`) so every pre-migration number stays
a historical result, never cross-compared (§8). Five sequential gates, each passed
before the next:

- **M1 — the register path survives vLLM.** vLLM's `prompt_embeds` reproduces HF's
  soft-prompt injection: 19/20 problems byte-identical greedy over 48 tokens, 0/20
  diverging in the first 3 (the chat-template-splice failure signature). The
  make-or-break gate for any future register work; it passes.
- **M2 — throughput.** Same L4, same workload: HF bf16 batch-1 **28 tok/s** → vLLM
  bf16 continuous batching **2809 tok/s** = **100×** (281× over the old 4-bit/T4
  effective rate). The quota wall is gone; a DIAG-10-scale study now runs in minutes.
- **M3 — statistical re-baseline.** Reproduced the Phase-0 pool on bf16, execution
  held to Daytona so only the generation stack varies. All metrics shift **uniformly
  up and grow with k** — B0 0.5922→0.6479, B1-likelihood 0.6280→0.7256, oracle pass@8
  0.8415→**0.9024** — a modest, coherent, fully explained bf16 quality lift
  ([artifacts/m3_rebaseline.json]). (A logprob-population bug that would have
  corrupted the likelihood-rerank number was caught and fixed here.)
- **M4 — verifier revalidation → retrain required.** V-v2b scored on the *new* bf16
  candidate distribution keeps its global AUROC (0.772) but its within-problem
  reranking edge over likelihood **collapses from +0.15 to +0.016**
  ([artifacts/m4_verifier_revalidation.json]). The substrate change staled V's
  decision boundary; a verifier retrain on the deployment distribution is required
  and folds into Phase 3.
- **M5 — reproducibility becomes statistical.** vLLM's throughput kernels are **not
  bit-deterministic** run-to-run (greedy 143/164 byte-identical across two seeded
  runs). The Phase-0 bit-lock cannot be reconstructed; it is retired for a
  **statistical** standard — aggregate pass@k/AUROC reproduce within sampling noise
  (M3's two independent draws agreed to ~1 pt), which the CI-gated comparisons already
  assume ([DECISIONS.md] D14). An honest reduction in rigor, accepted as the cost of
  100× throughput.

Phase M is complete; total spend a few dollars inside Modal's free credit.

## 7. Phase 3 — when does cross-step conditioning pay?

### 7.1 The reframe

The register null is not the end of a question but the start of a sharper one. The
diagnostics (§5.3) establish two things the design of any refinement experiment must
respect: (i) conditioning on a *failed candidate* is actively harmful — it anchors
the generator to its own mistake (DIAG-8: consecutive candidates 0.35× as diverse as
i.i.d.; DIAG-10: the candidate-anchored channel anti-refines while the same feedback
*without* the candidate does not, a +0.225 late-step gap); so a refinement channel
must carry an **abstraction of the error**, not the attempt. And (ii) whether such a
channel adds *benefit* is untestable on a saturated task — DIAG-10/11 could measure
harm but not benefit, because a task with pass@8 ≈ 0.9 has no headroom to add to.
Phase 3 therefore stops asking about the register specifically and asks the general
question the record has earned: **on what task, at what scale, can cross-step
conditioning pay — and what task *structure* is required for the question to even be
answerable?** The register becomes one mechanism to be tested *inside* that frame,
after a qualifying task is found.

### 7.2 The benchmark screen (a mandatory pre-registered gate)

We have twice run a refinement mechanism on a saturated task and twice gotten an
uninformative null. Never again: Phase 3a selects the task on its **pass@k curve**,
not by name, against three pre-registered criteria ([PHASE_3.md] §4) — **coverage
band** pass@8 ∈ [0.30, 0.60], **reachable headroom** pass@50 − pass@8 ≥ 0.15, and
**feedback richness** ≫3 tests/problem (so execution yields a gradient, not a binary
— the same partial-credit signal the register was starved of). A task clearing all
three has correct-but-improbable solutions the model can be *steered* toward, and a
rich enough error signal to steer with.

### 7.3 Finding F1 — function-call benchmarks have a shallow reachable tail

BigCodeBench (1140 problems, ~5 unittest methods each — the richest feedback of the
function-call benchmarks) was the lead candidate. It fails, and the failure is
precise and structural. On **random** samples (see the method note below), across
every difficulty × scale point:

| config (random, k=50) | pass@8 | pass@50 − pass@8 |
|---|---|---|
| Complete @ 1.5B | 0.302 | +0.108 |
| Complete @ 0.5B | 0.161 | +0.092 |
| Hard @ 1.5B (all 148) | 0.118 | +0.112 |

**The binding failure is headroom, not coverage** — it is structurally ~0.09–0.11
everywhere, never ≥0.15, *even where coverage lands in the band* (Complete@1.5B).
Whatever Qwen-Coder can solve on BigCodeBench it reaches within ~8 i.i.d. samples;
50 samples add only ~0.10. This is the **same "solve-within-8-or-not" shape that made
HumanEval useless for refinement** — one coverage level down, same structure — so it
is not a scale problem a different model fixes; it is a property of function-call
benchmarks with deterministic unit tests. **F1** ([DECISIONS.md] D16): refinement
needs a task whose **pass@k keeps climbing with k** — a deep tail of
reachable-but-improbable solutions — which the function-call family structurally
lacks. The result is negative but load-bearing: it converts "we couldn't find a task"
into "here is the *structural property* a task must have," and points directly at
competitive (stdin/stdout) benchmarks, where a model stumbles onto a correct approach
only occasionally over many samples.

**Method note (a second finding).** The initial screens used the *first n* problems
of each split; the full-benchmark confirmation showed first-n is **~2× easier than a
random draw** — (Complete, 0.5B) fell from pass@8 0.340 (first-40) to 0.161
(random-400). The premature "gate PASS + benchmark selected" that rested on the biased
subset was withdrawn (D15 retracted); all screening is **random-sample only** now.
The confirmation step caught the bias *before* Phase 3b was built on it — which is the
entire reason a confirmation step exists.

### 7.4 Finding F2 — sample-based refinement has almost no runway on code at 0.5–1.5B

> **⚠ Under audit ([PHASE_3R.md] R2; full detail §9.2).** F2's ≤0.12 headroom was
> measured under three inherited tail-suppressors — top-p 0.95 (nucleus truncates the
> improbable tail), temperature 0.8 (never swept), and Instruct tuning (entropy-collapsed
> vs a base model's deeper pass@k tail). Its honest current scope is "*instruct* Qwen at
> T=0.8/top-p=0.95 has a shallow tail." R2 re-screens with the tail un-suppressed
> (base completion model, top-p 1.0, T∈{0.8,1.0,1.2}); **base sweep complete: T=0.8
> (pass@8 0.328, headroom +0.097), T=1.0 (0.241, +0.149), T=1.2 (0.092, +0.133). The
> pre-registered trade-off is confirmed and has NO feasible base point — pass@8 needs
> T≤0.8 (only T=0.8 clears the band), headroom needs T≥1.0; they never co-occur.** If any
> config clears pass@8∈[0.30,0.60] ∧ headroom≥0.15, F2 narrows to the frozen config and
> the gate flips to PASS; if none does across base+instruct × 3 temps un-truncated, F2 is
> *strengthened* (structural, decoding confound ruled out). **Gate still open**, but every
> landed cell fails: base is exhausted with no feasible point, and instruct T=0.8 (pass@8
> 0.269, headroom +0.086) fails the band *from below* — base beats instruct at matched
> T=0.8 on both axes, the deeper-base-tail direction R2 predicted. Only instruct T=1.0/1.2
> remain (need regen after the 2026-07-14 outage, §9.5), and since instruct pass@8 already
> sits below the band at its coolest temp and falls with T, they cannot open a feasible
> cell. Evidence strongly trends **F2 strengthened-as-structural**.
>
> **AUDIT RESOLVED (2026-07-15, full grid landed — §9.2): F2 RETRACTED-AS-STRUCTURAL.**
> The trend statement above was written inside the BCB-only evidence window and did not
> survive the LiveCodeBench arm: **four LCB-easy cells clear both criteria** (base
> T=0.8/1.0/1.2 and instruct T=1.2; best headroom +0.250 in-band), so the pre-registered
> decision rule fires on its retraction branch and the Phase-3a gate flips to **PASS,
> scope narrowed to the qualifying configs**. What survives is F1 rescoped: the
> *function-call family* (BigCodeBench) stays infeasible at every un-suppressed cell.
> F2's tables and reasoning below stand as the historical record of the *suppressed*
> regime (instruct, T=0.8, top-p 0.95).

F1's implication was pursued to **LiveCodeBench** (contamination-controlled; 400
problems, ~27 test cases each; easy/medium/hard) via a new hardened stdin/stdout judge
(per-case run, short-circuit on first failure, process-group-kill + rlimit sandboxing,
normalized comparison — validated). Competitive benchmarks were the best hope: a deep
pass@k tail is their characteristic structure. They are deeper — but not enough. The
**complete Phase-3a sweep** (random samples, k=50):

| benchmark / tier | scale | pass@8 | pass@50 − pass@8 |
|---|---|---|---|
| BigCodeBench-Complete | 0.5B | 0.161 | +0.092 |
| BigCodeBench-Complete | 1.5B | 0.302 *(in band)* | +0.108 |
| BigCodeBench-Hard | 1.5B | 0.118 | +0.112 |
| LiveCodeBench-easy | 1.5B | 0.541 *(in band)* | +0.122 |
| LiveCodeBench-medium | 1.5B | 0.067 | +0.087 |

**FINDING F2 ([DECISIONS.md] D16): no configuration provides the reachable headroom
the gate requires (pass@50 − pass@8 ≥ 0.15); across the whole sweep it is capped at
~0.09–0.12** — two benchmark families, two execution paradigms (unittest and
stdin/stdout), three difficulty tiers, two model scales. The configs that land *in*
the coverage band (BigCodeBench-Complete@1.5B, LiveCodeBench-easy@1.5B) have shallow
tails; the ones with any more depth are below the band. **The gate returns a
NEGATIVE.**

The interpretation is structural and, we think, the real result of Phase 3. For a
code model at this scale, a problem is largely **gettable-or-not within a few
samples** — the solution distribution per problem is peaked, not heavy-tailed — so
pass@k **saturates fast** (pass@50 ≈ pass@8 + ~0.1 everywhere). Iterative refinement
needs the opposite: *reachable-but-improbable* solutions to steer a model toward. That
regime barely exists on code benchmarks here. And it does **not** yield to scale in
the obvious direction: a larger generator raises coverage (more saturation → *less*
headroom, BigCodeBench 0.5B→1.5B moved coverage +0.14 but headroom only +0.02), so
"use a bigger model" makes it worse, not better. This closes the loop on the original
register null: HumanEval had no headroom (pass@8 0.85) — and it turns out *no* tested
code benchmark at 0.5–1.5B has enough. The register experiment was starved of runway
not by an unlucky benchmark choice but by a property of the whole task family.

**The fork (a decision for the next stage), and why F2 is the useful output.** Per the
pre-registration, a benchmark clearing the gate does not exist at this scale, so 3b/3c
do not proceed on a task that fails the screen (the exact error that produced the H2
null). The documented failure sharpens the next experiment far more than a forced pass
would: it says the refinement paradigm, to be testable, needs a task whose per-problem
**solution distribution is heavy-tailed** — e.g. genuinely open-ended generation
(agentic/multi-file, proof search, program synthesis with many valid targets), or an
*intermediate*-reward signal that creates a gradient where pass/fail is flat — not
another unit-tested function benchmark. Options on the table: (i) an intermediate model
scale / a benchmark with a heavier tail (untested — but the cap looks structural);
(ii) redefine the "reachable" axis away from i.i.d. resampling toward *feedback-driven*
recovery (does the model reach a solution it could not i.i.d.-sample, given an error
abstraction — the DIAG-10 direction — which does not require i.i.d. headroom); (iii)
accept F2 as the Phase-3 result and write the register/refinement story as *where and
why sample-based refinement has runway on code, and where it does not*. **Direction
(ii) is the most promising** — it is the one path the diagnostics actively support and
the one that does not depend on finding a heavy-tailed code benchmark that may not
exist. Pre-registration of the 3b redesign around it is the next step; it is a design
decision, not an extension of this record.

*Phase 3a is complete: gate outcome NEGATIVE (F2). Phase 3b/3c are held pending the
redesign the fork above describes.*

## 8. Reproducibility

Everything needed to reproduce is committed: pinned datasets (SHA256),
frozen configs ([configs/]), the compute-accounting rule (frozen before any run;
its **amendment log** now records two stack moves — Kaggle→Modal T4, then the Phase-M
rebuild to vLLM/bf16/L4 — with the budgeted unit "one candidate generation" unchanged
through both), seed policy (17 throughout), per-record compute ledgers, and the full
gate log with dates and both failed verifier attempts ([PHASES.md]).

**Two reproducibility regimes, by stack.** On the retired HF/4-bit stack the Phase-0
reproduction was **exact** — byte-identical candidates on 164/164 problems across
independent runs (the bit-lock). On the current vLLM/bf16 stack that is unattainable
(M5): the throughput kernels are not bit-deterministic, so reproducibility is
**statistical** — aggregate pass@k/AUROC reproduce within sampling noise ([DECISIONS.md]
D14). **Numbers never cross the stack boundary:** every Phase-0/1/2 figure is a
historical result of the retired stack (recoverable at tag `pre-phase-m-hf-nf4`), never
compared to a post-migration number; Phase M's M3 re-baseline established a *new*
reference, not a correction of the old.

Infrastructure: Kaggle then Modal T4 for Phases 0–2 and the diagnostics (~25+
T4-hours), Modal L4 (vLLM) for Phase M and Phase 3, Daytona sandboxes for Phase-0–2
execution (12,100 runs; sandbox-fault rates 0.2% / 0.0% / 0.3%, faults scored as
failures), and hardened subprocess judges (process-group kill + rlimits) for the
Phase-3 benchmark screens ([scripts/modal_phase3a.py], [scripts/modal_lcb.py]).

**Operational reproducibility — designing runs against the platform's failure
semantics *(appended 2026-07-15)*.** "Question the underlying system" applies to the
compute platform, not just the science: pre-registration protects claims from us;
this ledger protects runs from the infrastructure. The R1b.2d retrain (a ~4.5 h
single-function T4 job) was lost four times in two days, each to a *different*
failure mode, before one hardened design closed all of them. The ledger, kept for
consistency of practice on any managed-compute service:

1. **Client-tied ephemeral apps.** Modal tears down a non-detached `modal run` app
   ~3 minutes after the local client disconnects. Two local power outages
   (2026-07-14, 2026-07-15 ~04:09 EDT) each killed ~2 h of remote GPU work this
   way. *Practice:* long runs launch with `modal run --detach`, which keeps the
   remote alive through client death (caveat: detach preserves only the
   last-triggered function — sufficient for single-`.remote()` entrypoints, not
   for chained remote calls).
2. **Function timeout below true workload.** The remote cap (3 h) sat under the
   measured ~4.5 h workload and killed a run mid-epoch-3. *Practice:* measure the
   workload before capping, set headroom (now 6 h), and checkpoint so a timeout is
   a resume, not a loss.
3. **Worker preemption restarts from scratch.** Modal reclaims workers and re-runs
   the function on the same input with no memory of prior progress. Two
   consecutive preemptions landed ~70 min in — both inside the ~15-minute
   post-epoch pool-scoring window that preceded the old end-of-epoch checkpoint —
   so each cycle billed a full epoch and persisted nothing; at that hazard rate a
   4.5 h monolith never completes while still spending. *Practice:* checkpoint
   within seconds of each epoch boundary (trainable params + full optimizer state
   + progress JSON keyed by a `run_id` nonce to reject stale state from earlier
   attempts), defer long scoring to a single resumable post-training pass, and
   resume on `run_id` match so a restart forfeits at most one epoch or one scoring
   pass.
4. **Result loss at the finish line.** The final artifact was computed by the
   *local* entrypoint from the remote's return value — a dead client would lose a
   completed run's payload. *Practice:* the remote persists the complete scored
   payload to the volume before returning; the verdict is recomputable from the
   volume plus `modal app logs` alone, with no live client required.

Two footnotes for honesty. *Recipe fidelity under resume:* restarts restore the
exact AdamW state dict, so a stitched trajectory differs from an uninterrupted one
only in the unseeded shuffle order — which D14 already leaves uncontrolled between
runs; resume is therefore a draw from the same run distribution, not a recipe
deviation. *Cost:* every one of these failure modes bills before it loses the work —
the un-hardened design converted an overnight outage plus a preemption cycle into
roughly half the project's remaining compute budget with zero scientific output.
Run-loss modes are spend-loss modes; hardening is cheaper than any single recurrence
([scripts/modal_rgr.py] `r1b2d_train_eval`, commit `7e4ea2f`).

## 9. Phase 3R — auditing the two live claims, and the anchoring mechanism

Phase 3 published two load-bearing results on *inherited* Phase-0 choices: **H1** (an
execution verifier beats likelihood) and **F2** (no code benchmark here has a reachable
tail). Phase 3R ([PHASE_3R.md]) refuses to call either final until the unexamined
assumption each rests on is tested, and — spun off from the DIAG-8 anchoring finding —
pins down the *mechanism* of refinement harm. Order: **R1 → R2 → R3** (cheapest/highest-
stakes first). Standing rule unchanged: **append, never revise**; pre-register before
running; honest negatives. A judge fix predates all of it: the Phase-3a stdin/stdout and
BigCodeBench executors short-circuited on the first failing test, destroying the per-test
`frac_tests` signal R3/BEST-SO-FAR need; both now run all cases and emit
`{passed, n_tests, n_passed, frac, failing[], err, exc}` (committed `d6cbf37`).

### 9.1 R1 — is H1 a quantization artifact? *(the H1 audit)*

M4's flag (§6): V-v2b's within-problem edge over likelihood collapses +0.15 → +0.016 on
bf16. The audit reframes H1 on a **stack-invariant** metric — **Selection Efficiency**,
SE = (selected pass@1 − random pass@1) / (oracle pass@8 − random pass@1):

- **R1a (closed — bug-clear).** The vLLM `cumulative_logprob` bug was port-only; the HF
  Phase-1 likelihood arm was never touched (lock_a 0/1312 null). H1's number is not a
  logprob-population artifact.
- **R1b (open — the real question).** On bf16, **likelihood alone reaches SE 0.305**,
  nearly the whole 4-bit verifier benefit (**SE 0.315**) — H1 may have measured "V beats
  *quantization-corrupted* likelihood." Free CPU checks closed the mundane escapes:
  **R1b.2b** — V is not just a brokenness detector (it discriminates *subtle*,
  wrong_answer-only failures at within-AUROC **0.751**); **R1b.2c** — the bf16 likelihood
  advantage is not a length artifact (sum-logprob / shortest-candidate do not rescue it).
- **R1b.2d (the decider — RERUN PENDING).** Retrain V on the bf16 MBPP distribution and
  re-score. **Pre-committed kill line: retrained-V bf16 SE ≤ 0.305 → H1 does not survive
  de-quantization.** Predicted SE ~0.33–0.38 (partial survival). **Verdict not yet
  computed:** the retrain was killed by a 2026-07-14 power outage at epoch 3/3 (~step
  450); `r1b2d_train_eval` never commits the adapter to a volume, so the weights died with
  the container and no verdict was written. Labeled input (`r1b2d_mbpp_labeled.json`)
  survived, so the rerun repeats only the ~3-epoch T4 retrain. Last-known training signal
  (bf16, informational, *not* the verdict): epoch-1 val AUROC 0.7009, epoch-2 0.7410.
  [artifacts/r1b2b_stratified_auroc.json, r1b2c_length_bias.json].

**RESOLUTION (2026-07-15) — the kill line FIRED: H1 is a quantization artifact.** The
retrain landed on the fifth attempt (the four losses were infrastructure — the §8
operational ledger); val AUROC 0.6872 / **0.7069** / 0.6999, epoch 2 selected. The full
SE matrix, both pools × three rankers:

| SE | 4-bit pool | bf16 pool |
|---|---|---|
| likelihood (free) | 0.144 | **0.305** |
| V trained on 4-bit distribution | **0.315** | 0.067 |
| V retrained on bf16 distribution | **0.364** | **0.090** |

Retrained-V bf16 SE **0.090** ≤ 0.305 — the kill line fires inside the registered
artifact band (0.05–0.10); the registered prediction (0.33–0.38, partial survival) was
**wrong**. The matrix reads as an **inversion**: on the 4-bit pool any execution-trained
V beats likelihood (the bf16-retrained V, which never saw a 4-bit candidate, ranks it
*better than the original*); on the bf16 pool no V comes close, and on-distribution
retraining moved SE just +0.023. The edge was a property of the quantization-corrupted
candidate pool — corrupted likelihood (SE 0.144) plus easier-to-discriminate failures
(within-AUROC 0.7189 vs 0.6377) — not of the verifier. **H1 is retired**; likelihood is
the strong free selection baseline on the clean stack, and no verifier-selection stage
carries into 3b / R3 / BEST-SO-FAR (all execution-conditioned designs are unaffected).
Full decomposition and consequences: [PHASE_3R.md] R1b.2d RESOLUTION;
[artifacts/r1b2d_verifier_retrain.json].

### 9.2 R2 — is F2's shallow tail structural or decoding-induced? *(the F2 audit)*

F2 was measured under three independent **tail-suppressors**: `top_p=0.95` (nucleus
truncates the improbable tail — the exact thing refinement hunts), `temperature=0.8`
(never swept), and **Instruct** tuning (SFT/RLHF collapse generation entropy; base
completion models have far deeper pass@k tails — the Codex/AlphaCode reason to sample
from base models). R2 re-screens **BigCodeBench-Complete + LiveCodeBench-easy** across
generator {**base**, Instruct} × `top_p=1.0` × T ∈ {0.8, 1.0, 1.2}, random samples, fixed
judge. **Decision rule:** any config with pass@8 ∈ [0.30,0.60] **and** pass@50−pass@8 ≥
0.15 → F2 retracted-as-structural, scope narrowed to the frozen config, **gate PASSES**;
no config clears across base+instruct × 3 temps un-truncated → **F2 strengthened**
(structural, decoding confound ruled out). **Base completion path validated** (smoke:
64/64 well-formed modules, 0 degenerate, mean `frac_tests` 0.269, 44% pass ≥1 test —
graded feedback present). Base BigCodeBench sweep (n=200, k=50) **complete**: **T=0.8**
pass@8 **0.328** / pass@50 0.425 / headroom +0.097 (band ✓ — the only config to clear it);
**T=1.0** pass@8 0.241 / pass@50 0.390 / headroom **+0.149**; **T=1.2** pass@8 0.092 /
0.225 / +0.133. The **pre-registered trade-off curve is confirmed and has no feasible base
point**: pass@8 clears the [0.30,0.60] band only at T=0.8, headroom clears ≥0.15 only at
T≥1.0, and the two never co-occur (they move oppositely along temperature). This is the
"clean trade-off, no feasible point" branch — the pre-registered second-most-likely and
most-informative outcome. The **instruct comparison arm** (T=0.8 recovered exec-only after
the 2026-07-14 outage; T=1.0/1.2 need regen — §9.5) is the last input before F2 resolves.
**Gate still open**, trending **F2-strengthened-as-structural**. **Prediction (recorded
before running):** a trade-off curve (base + hotter T deepens the tail but drops pass@8);
most-likely one base point clears → F2 retracted-as-structural, with real uncertainty —
**outcome: partially falsified** (the curve is confirmed, but *no* base point clears both,
the more-informative branch). **Instruct comparison** T=0.8: pass@8 0.269 / pass@50 0.355
/ headroom +0.086 — fails the band *from below*; base beats instruct at matched T=0.8 on
both axes (0.328/+0.097 vs 0.269/+0.086), confirming the deeper base tail. Instruct
T=1.0/1.2 (killed by the outage, need regen) cannot open a feasible cell — instruct pass@8
already sits below the band at its coolest temp and falls with T. **Gate formally open
pending those two cells; evidence strongly trends F2-strengthened-as-structural.**

**RESOLUTION (2026-07-15) — the completed grid retracts F2.** The regenerated BCB
instruct cells landed as the trend required (T=1.0: pass@8 0.256 / +0.104; T=1.2:
0.167 / +0.103 — no BCB cell feasible anywhere in the 2×3 grid). But the
**LiveCodeBench-easy arm** — run on a newly built, smoke-validated base completion path
(fenced-completion prompt; 64/64 well-formed) over the full 80-problem stdin-easy
population, k=50, top_p=1.0 — **contains a feasible region**:

| LCB-easy cell | pass@8 | pass@50 | headroom | gate |
|---|---|---|---|---|
| base T=0.8 | **0.566** | **0.762** | +0.197 | **PASS** |
| base T=1.0 | 0.505 | 0.675 | +0.170 | **PASS** |
| base T=1.2 | 0.312 | 0.562 | **+0.250** | **PASS** |
| instruct T=0.8 | 0.525 | 0.637 | +0.112 | ✗ |
| instruct T=1.0 | 0.509 | 0.637 | +0.128 | ✗ |
| instruct T=1.2 | 0.391 | 0.600 | +0.209 | **PASS** |

The pre-registered rule fires on its first branch: **F2 retracted-as-structural; the
Phase-3a gate flips to PASS.** Suppressor decomposition at matched cells: architecture
is the biggest lever (base +0.197 vs instruct +0.112 at T=0.8, base dominating both
axes), temperature second (instruct +0.112→+0.209 across T), top-p alone nearly nil
(instruct T=0.8: 0.525/+0.112 at top-p 1.0 vs 0.541/+0.122 at 0.95). **What survives,
rescoped:** F1 — the function-call family's shallow tail — is now *decoding-controlled*
(BigCodeBench infeasible even fully un-suppressed); the honest replacement statement is
*"reachable headroom at 0.5–1.5B exists on competitive stdin/stdout benchmarks under
un-suppressed sampling, and does not exist for function-call benchmarks at any tested
decoding."* Prediction accounting: the pre-registered phase-level call ("at least one
point clears → F2 retracted") was **correct**; the named clearing point (base BCB
~T=1.0) was **wrong** — BCB's trade-off has no feasible point, and the clearing came on
LCB-easy, whose higher coverage floor lets temperature buy tail depth without leaving
the band. The interim "trending strengthened" reads (recorded in the BCB-only window)
are superseded and stand with this outcome note. **Consequence:** Phase 3b has a
qualifying task; the config choice (recommend base T=0.8 — coverage-dominant, +0.197
headroom, cleanest error profile) is a 3b pre-registration decision, and R3's
pass@50 = 0 stratum is computable from the persisted enriched pools
[artifacts/phase3a_screen_lcb_r2_*.json; runs/modal/lcb_res_lcb_r2_*.json].

### 9.3 The anchoring mechanism — D-measure *(the DIAG-8 spin-off, closed)*

DIAG-8 showed conditioning on a failed candidate halves diversity. D-measure asks *what
that anchoring is*: single-step conditioning on committed HumanEval pools, conditions
E0 (i.i.d.) / E1 (self-fail) / E2 (foreign-fail) / E5 (correct), temps {0, 0.8, 1.2},
measuring **PULL** = 1 − edit-similarity to the conditioned artifact. All pre-registered,
append-only ([PHASE_3R.md] Addenda II/III):

- **The escape-distance law.** Conditioned on a failure, the single variable that
  predicts repair is **PULL** — how far the generation *escapes* the artifact. Coverage
  is monotone in PULL across conditions × temperatures (0.043→0.62). Provenance and
  framing are downstream of escape distance; the law absorbs DIAG-7/8/9b (all *low
  escape*, measured three ways).
- **It is a coverage/diversity law, not per-sample quality (D2b).** On the confound-free
  **mean-per-sample-pass** metric (greedy pass@1 vs T>0 pass@8 had corrupted the earlier
  read), escape is **flat** — E1 sits ~0.20 at every T. Escape buys pass@8 by *spreading*
  the samples so one lands, not by improving each; conditioning **relocates** the
  distribution. [artifacts/dmeasure_conditioning.json → per_sample_D2b].
- **Temperature is an anti-anchoring intervention, dose-responsive.** ns=8 clean:
  T 0.8→1.2 lifts coverage only for anchored conditions (E0 −0.02 flat, E1 +0.10,
  E2 +0.18), and the *more*-anchored condition benefits ~2×.
- **The attractor is content-blind (E5).** Conditioning strength is invariant to whether
  the target is correct: E5 PULL (0.020/0.066/0.168) ≈ E2 PULL — the mechanism does not
  know what it points at. *(The earlier "E5 = empirical charter for BEST-SO-FAR" was
  **retracted**: E5-on-a-correct-artifact is answer-leakage, 98% copy; the partial-credit
  premise test is D2c/E6, pending R2's pools.)*
- **Provenance is near-irrelevant — distinct from Tsui (D2a).** A verb×provenance 2×2
  on the *same* failed artifact: "self vs other" moves PULL ≤0.028 (→+0.006 pass), while
  the instruction verb ("improve it" vs "write a correct solution") moves it **3–4×**.
  The mechanism is **provenance-independent distributional conditioning** — not Tsui's
  *self*-anchoring blind spot; orthogonal to it (whose-output is inert, escape distance
  is live). [artifacts/dmeasure_d2a_verb_provenance.json].
- **Self-Debug reconciliation: escape needs direction.** Prediction (c) (TAX→0 at greedy)
  was falsified *backwards* — greedy is the *worst* case for anchoring (PULL 0.04–0.08 =
  near-total copy). Corrected: rich execution feedback supplies the **direction** to
  escape; undirected escape (raw resample, or a ~2-bit `error_class`) does not.
  **Escape requires direction; direction requires rich feedback** — R3's thesis with a
  mechanism, and it explains the split B2 (no feedback, copies) vs B2+fb (2 bits, still
  declines) vs Self-Debug (traces, works).

### 9.3.1 What the escape-distance law forces — the elimination argument *(the current frontier of thought)*

Three consequences follow from D2b's refinement that the law is a **coverage/diversity**
effect (mean-per-sample-pass is flat, ~0.20 at every T for E1). They are the sharpest
things we currently believe, and they set R3's bar.

1. **Undirected failure-conditioning cannot exceed i.i.d. sampling; it can only approach
   it.** If escape buys coverage by spreading samples (not by lifting per-sample quality),
   then the *ceiling* of escape is the point where the generation has diverged so far that
   the conditioning is **vacuous** — i.e. full escape *is* i.i.d. E0's natural position on
   the escape axis is its own within-set diversity (DIAG-8 measured B1 i.i.d. pairwise edit
   distance **0.396**) *[ANCHOR SUPERSEDED 2026-07-15 — that number was pairwise diversity,
   a different metric than the conditioned cells' PULL; the measured commensurate anchor is
   **0.594 at T=1.2 / 0.491 at T=0.8** — see "E0 anchor, measured" below]*; E1 at T=1.2
   reaches only PULL 0.309 / coverage 0.62 against E0's
   ~0.90. So every undirected refinement scheme is **strictly dominated by resampling at
   matched compute** — a mechanism-level derivation of Olausson et al. (2024)'s empirical
   compute-matched conclusion, and consistent with our own DIAG-1/H2 record.
2. **Therefore the only escape hatch is *directed* escape.** The lone way to beat i.i.d. is
   feedback that tells the model *where* to go, not merely how far. This is not one option
   among several for R3 — it is, by elimination, the **sole surviving refinement
   hypothesis.** It also **retro-reframes DIAG-10**: ABSTRACT ≈ B1 (0.787 vs 0.762) was
   never an uninformative null — it was *complete escape with near-zero direction* (~2-bit
   error_class), landing exactly where the law says undirected escape must. R3's pre-
   registered success bar is therefore **strict**: ABSTRACT with *rich* feedback must
   **exceed** B1's coverage, not merely match it (matching is free from resampling).
3. **The paper's central figure is already computable.** Coverage vs PULL, every failure-
   conditioned cell, with E0 anchored at (0.396, ~0.90) *[superseded — measured anchor
   (0.594, 0.90) at T=1.2; see "E0 anchor, measured" below]*. Every measured point sits strictly
   under the i.i.d. anchor. R3 then either places a point *above* that line (directed escape
   beats resampling) or the sample-based refinement paradigm is, at this scale, finished.

**Tsui orthogonality, stated at the mechanism level (for related work).** Tsui's blind spot
is a **detection** failure (can the model *notice* an error is present); ours is an
**escape** failure (can the model *leave* an error it already knows about). In our setup
detection is never required — the failure is announced — so the blind spot has nothing to
bite on. The two axes coexist rather than compete; the "opposite-to-Tsui" read from the
first D-measure pass is retired (§9.3), superseded by "orthogonal, because we removed the
variable Tsui measures."

**A confound of our own, flagged before the claim is final.** The content-blindness /
neutral-attractor result (E5) and the "conditioning drops mean_pass" magnitude both depend
on **which problems each condition ran on.** E1/E2 require a *failed* artifact to condition
on; E5 requires a *correct* one. If those were populated by filtering the pool, then E1/E2
ran on a hard-biased subset and E5 on an easy-biased subset, and E0's own baseline on those
same subsets is the only fair comparison. **The escape-distance law itself is safe** (it
lives entirely within failure-conditioned cells and D2a replicated it on a fixed-artifact
2×2), and the temperature dose-response is safe (within-condition). **At risk and pending a
free matched-control recompute:** (i) the absolute size of the "conditioning drops per-
sample pass" drop — E1's subset excludes always-solved problems, which alone depresses
mean_pass; (ii) E5's coverage-1.00 / negative-TAX, which could be near-tautological if E5's
subset is "problems that have a correct candidate." **Action (committed, §9.5):** recompute
E0's mean_pass and coverage on E1's subset and on E5's subset before publishing the neutral-
attractor claim. This is the append-only method applied to *our own* new finding, not just
inherited ones.

**Resolution (2026-07-14, [artifacts/dmeasure_subset_control.json]; [PHASE_3R.md]
Addendum IV) — the feared confound is structurally absent.** All four D-measure
conditions, and all four D2a cells, ran on **one identical 60-problem subset** (the
first 60 M3-pool problems with both a failed and a correct candidate — verified by
pid-set equality and selection reconstruction), so E0-on-E1's-subset = E0-on-E5's-subset
= the published E0, and no cross-condition contrast ever crossed a subset boundary.
Claim (i) stands as measured (E0 0.5875 → E1 0.2375 at T=0.8, on identical problems);
claim (ii)'s tautology worry is real but bounded — every subset problem is
solvable-within-8 by construction, and the matched E0 is already near-saturated
(coverage 0.92/0.90 at T=0.8/1.2), so E5's margin over its fair baseline is small,
consistent with the answer-leakage retraction already in place. What remains is a
**scope note**, not a confound: the shared subset is mixed-outcome-only and first-60
(not random), ~8 pts harder than the full pool (M3 mean-pass 0.565 vs 0.648) — absolute
magnitudes are scoped to mixed problems; every within-subset contrast, the
escape-distance law, content-blindness, and the dose-response are unchanged.

**E0 anchor, measured (2026-07-15 — [PHASE_3B.md] W0a; the pre-registered 70/30
prediction was WRONG).** The figure's i.i.d. anchor had been *assumed* commensurate with
the conditioned cells' PULL axis: 0.396 was DIAG-8's within-set pairwise diversity, a
different metric. Measured directly — PULL of every committed E0 generation against the
same failed artifact each conditioned cell used — the anchor is **0.409 ± 0.319 (T=0) /
0.491 ± 0.212 (T=0.8) / 0.594 ± 0.178 (T=1.2)**, +0.198 from the assumed value at the
figure's anchor row, far outside the pre-registered ±0.05 band (odds were 70/30 the
other way; recorded). The secondary check holds — E0-PULL exceeds every conditioned
PULL at matched T — so the geometry does not invert; it **stretches**: E1@T1.2
(PULL 0.309) has closed only **~52% of the escape distance** to the honest i.i.d.
position, not the ~78% the assumed anchor implied. Two consequences. (i) The
"undirected escape can only approach i.i.d." asymptote has far more unclaimed room than
the old figure suggested, and nothing measured comes near it — the elimination
argument survives its first audit leg with a *larger* unexplained gap, not a smaller
one. (ii) Calibration: an i.i.d. sample sits only ~0.41–0.59 from an arbitrary failed
candidate on the same problem (natural same-problem token overlap), so conditioned
PULLs of 0.04–0.31 are deep inside copy territory — "escape" as measured has never yet
left the artifact's neighborhood. The central-figure spec now uses the measured anchor
per temperature; the 0.396 mentions above carry supersede markers in place.
[artifacts/w0a_e0_anchor.json].

**The repulsion escape-hatch, closed (2026-07-15 — [PHASE_3B.md] W1/E7; branch (a),
the pre-registered 55% favourite).** The elimination argument had excluded a third
limit *a priori*: **repulsive conditioning** (a model anti-correlated with the failed
artifact would sample i.i.d.-restricted-to-the-complement and could beat resampling by
not re-wasting draws on the failed basin). E7 populated the region: same protocol,
explicit-avoidance framing, T ∈ {0.8, 1.2}. Outcome — **repulsion loses to i.i.d. by
15–27 coverage points at matched compute** (E7 0.65/0.75 vs committed E0 0.92/0.90;
paired: E7-only 1 and 4 problems vs E0-only 17 and 13), and the sharper mechanism
finding is that **prompt-level repulsion is unachievable at this scale**: the
avoidance instruction moved PULL just +0.02/+0.05 over plain "improve it" (0.196/0.357
vs anchor 0.491/0.594) — told explicitly to leave the failed basin, the model
generates inside copy territory anyway. The exclusion is now measured, not assumed;
"strictly dominated by resampling" stands as written. One secondary prediction was
**wrong, informatively**: E1@T=1.5 did not continue the coverage-vs-PULL curve — it
fell off a **competence cliff** (PULL 0.560 but coverage 0.18, mean_pass 0.035; E0@1.5
itself degrades to 0.37/0.067). **The escape-distance law's domain is
temperature-bounded (T ≲ 1.2):** past the boundary, escape is bought with broken
samples and coverage inverts. So the undirected route to i.i.d. is doubly closed —
asymptotically (the anchor is never reached) and practically (the temperature needed
to force the distance destroys the samples first). Figure spec: points carry
temperature labels; anchor row extends to T=1.5 (PULL 0.409/0.491/0.594/0.740,
coverage 0.65/0.92/0.90/0.37). [artifacts/dmeasure_e7.json].

### 9.4 R3 + BEST-SO-FAR *(pre-registered; ride R2's enriched pools)*

- **R3 — conditional reachability (the central claim).** On the **pass@50 = 0** stratum
  (problems i.i.d. sampling provably fails in 50 tries), does an
  **error-abstraction-conditioned** model reach a solution i.i.d. cannot? Channels
  B1-50 / ANCHOR / ABSTRACT, matched compute, absolute recovery *count*. Add-on
  (Addendum III §4): cross **feedback-richness × temperature** — predicted substitutes at
  the margin, complements in the limit (rich-feedback × high-T = directed escape;
  2-bit × high-T ≈ resampling). Prediction: ABSTRACT > 0 and > ANCHOR. Kill: ABSTRACT ≈ 0
  forecloses the refinement direction.
- **BEST-SO-FAR — aim the attractor at a success.** Channels B1 / LAST / BEST /
  ABSTRACT / BEST+ABSTRACT on R2's feedback-rich pool, **oracle-first** ranking, matched
  compute. **Deflated by the escape-distance law** (Addendum III §5): since conditioning
  reproduces at 83–98% fidelity, BEST-alone ≈ **hold-at-best** (copying an 11/27 candidate
  yields ~11/27 — no repair); **BEST+ABSTRACT is the only condition with a mechanism**
  (best candidate = start point, abstraction = escape direction). **D2c/E6** is the
  premise test: condition on a ~40–60%-tests artifact, measure the generated candidate's
  `frac_tests` — flat → BEST-alone dead; climbing → a bigger result than scoped.

### 9.5 Live status (2026-07-15, post-R1b.2d — **the Phase-3R audits are complete**)

**Closed:** judge fix; R1a; R1b.2a/b/c; D-measure incl. Addendum II (judge/D-measure
pre-reg) and Addendum III (escape-distance law, temperature dose-response,
content-blindness, D2a provenance/Tsui, D2b metric fix); the 2026-07-14 outage record
(PHASE_3R.md "CRASH RECOVERY") and the full run-loss/hardening ledger (§8 operational
reproducibility — five R1b.2d attempts, four distinct infrastructure failure modes,
closed by detach + checkpoint/resume, commit `7e4ea2f`); **the E5/E1 subset
matched-control recompute** (§9.3.1 — confound structurally absent, claims stand with a
scope note; [artifacts/dmeasure_subset_control.json], [PHASE_3R.md] Addendum IV);
**R2 COMPLETE — the F2 gate FIRED on its retraction branch** (§9.2): BigCodeBench zero
feasible cells, LiveCodeBench-easy **four** (base T=0.8/1.0/1.2, instruct T=1.2; best
in-band headroom +0.250); **F2 retracted-as-structural, Phase-3a gate PASS, scope
narrowed**; enriched per-test pools persisted for all 12 cells (`bcb_res_*`,
`lcb_res_*`); **R1 COMPLETE — the H1 kill line FIRED** (§9.1, [PHASE_3R.md] R1b.2d
RESOLUTION): retrained-V bf16 SE 0.090 vs likelihood 0.305, registered artifact band;
the SE matrix inverts across pools (retrained V scores 0.364 on the 4-bit pool) — **H1
killed-as-artifact; the edge lived in the corrupted candidate pool, not the verifier.**

**Running:** nothing. No GPU job is required by any closed item.

**Phase-3R outcome, one line: both audited claims fell** — H1 killed-as-artifact, F2
retracted-as-structural — and what survives is the register null (H2), the
escape-distance law + elimination argument, and the LCB-easy feasible region. No claim
was reversed silently; every prediction stands with its recorded outcome, including the
two audit-prediction misses (R1b.2d predicted partial-survival 0.33–0.38, landed 0.090
artifact; R2 named base BCB ~T=1.0, the feasible region landed on LCB-easy).

**Pending (unstarted — design decisions, not run work):** 3b pre-registration on the
qualifying LCB-easy config (recommend **base T=0.8**: pass@8 0.566 / headroom +0.197;
note the H1 consequence — selection/ranking stages in any 3b design use likelihood or
execution feedback, never a learned verifier); **D2c/E6** (partial-credit conditioning —
premise test for BEST-SO-FAR; enriched pools ready, 360 partial-credit candidates);
**R3** (conditional reachability on the pass@50 = 0 stratum of the chosen config;
stratum sizes 19/26/35/32 across the four feasible cells — small, consider LCB-medium
extension if the 5–20% recovery prediction needs resolution); **BEST-SO-FAR**.

**Restart ordering for a fresh conversation:**
1. **3b pre-registration** — pick + freeze the qualifying config (§9.2 recommendation:
   base T=0.8), write predictions/kill criteria for R3, D2c/E6, BEST-SO-FAR before any
   run. Inherit the H1 verdict: no verifier-selection stage on the bf16 stack.
2. **D2c/E6 → R3 → BEST-SO-FAR** in that order on the frozen config's enriched pools.

**Ordering superseded (2026-07-15, same day):** the Phase-3b design-cycle charter
([PHASE_3B.md]) inserts a hardening pass **before** the 3b freeze — the elimination
argument (§9.3.1), now the central claim, gets the same audit treatment H1 and F2 got.
New order: **W0** (free CPU: measured E0 anchor, D2c copy-null, stratum false-zero
rate) → **W1** (E7 repelled-conditioning arm — the asymptote's unpopulated third limit)
→ **W2** (LCB-medium base screen — size R3, power check) → **W3** (freeze the 3b
pre-reg: R3 four-arm with ABSTRACT-trace ceiling, recovery validation protocol) →
**W4** (execute D2c/E6 → R3 → BEST-SO-FAR). A reconciliation ledger (§11) now governs
every external result used in design.

### 9.6 Stratum characterization — the pass@50 = 0 label has a false-zero floor *(2026-07-15, W0c; W2 extends)*

R3's target stratum ("problems i.i.d. provably fails in 50 tries") is not a clean
label: a problem with true per-sample rate p = 0.01 survives 50 draws with probability
~0.60. From the persisted k=50 pools of the four feasible cells, a two-component
maximum-likelihood fit (point mass at p = 0 + Beta over reachable p; pure-Beta fit as
upper bound) gives the **expected lucky-recovery count a fresh B1-50 control arm
produces on the stratum by chance alone**:

| cell | stratum (0/50) | x=1 / x=2 near-misses | E[B1-50 lucky recoveries] (upper) |
|---|---|---|---|
| base T=0.8 | 19/80 | 10 / 5 | **3.6** (3.9) |
| base T=1.0 | 26/80 | 5 / 4 | 2.3 (5.3) |
| base T=1.2 | 35/80 | 10 / 5 | 5.0 (6.9) |
| instruct T=1.2 | 32/80 | 10 / 3 | 4.6 (5.4) |

The mixture split is fit-unstable cell-to-cell (P(reachable | 0/50) ranges 0.22–0.81),
but the floor is stable: **~2–5 lucky recoveries per stratum**, the same order as the
pre-registered 5–20% recovery prediction (1–7 recoveries on 19–35 problems). Two design
consequences, both binding on W3: (i) R3's primary contrast must be **ABSTRACT >
B1-50, paired** — ABSTRACT > 0 is theater, and this floor goes into the stated null;
(ii) **the easy strata alone are unpowered** — the signal and the noise floor are the
same size — so the LCB-medium screen (W2) is a prerequisite, not a contingency.
[artifacts/w0c_stratum_falsezero.json].

---

## 10. Working method — how this project reasons *(read first in any new conversation)*

This section is not results. It is the **operating method** that produced them, written
down so a fresh conversation continues in the same key rather than reverting to default
LLM habits (agreeing, refuting, declaring). The method is the reason a mostly-negative
record is worth publishing.

**The core loop: a failure is a pointer, not a verdict.** Every dead result in this
project spawned the next question rather than closing the book. H2's null → "what would
have to be true for *any* refinement to pay?" → the coverage/headroom frame. F2's negative
→ "is the tail structural or decoding-induced?" → R2. DIAG-8's anchoring → "is this about
*self* or about *conditioning*?" → D-measure → the escape-distance law → the elimination
argument. A refutation is treated as *information about our specifics*, not as a general
truth to adopt or a decision that settles the matter.

**Four rules that operationalize it:**

1. **Question what a refutation means *for our specifics*, don't import it as truth.** When
   a paper (or our own diagnostic) contradicts us, the first move is mechanistic: *why*
   does their setup produce that result, and does the mechanism even apply to ours? This is
   how Self-Debug (improves without execution feedback) and "How Many Tries" (universally
   effective repair) were reconciled rather than fought — different baselines (greedy vs
   compute-matched), different regimes (near-correct candidate vs structural failure),
   different scale. Neither is wrong; both are measuring where our effect is invisible.
2. **A decision is not a claim; a claim is not a finding.** Our own past suggestions,
   drafts, and pre-registrations are *hypotheses*, not results, until a committed artifact
   says otherwise. Prior-session enthusiasm ("BEST-SO-FAR is the charter") gets deflated by
   the next measurement (E5 = answer leakage) without ceremony. Provenance is tracked per
   claim: what is measured, what is inferred, what is still a bet.
3. **Pre-register, then append — never revise.** Predictions and kill criteria are written
   *before* the run, with odds where possible, and left standing whether they hold or not.
   Two D-measure predictions were falsified (one *backwards*); both stay on the page next to
   the corrected mechanism, because the correction is only trustworthy if the error is
   visible. Retractions are marked `[SUPERSEDED]`/`[retracted]` in place, not deleted.
4. **Turn the method on ourselves.** The same scrutiny applied to the field applies to our
   own new findings — hence the E5 subset-confound flag (§9.3.1) raised against our *own*
   freshest result before it is claimed, and the DIAG-2 problem-grouped-CV catch that killed
   a false 0.87 that our own pipeline produced. The failure mode we actively guard against is
   "treading into our own water": deriving a law post-hoc from a handful of cells and then
   fitting everything to it. The defense is out-of-sample replication (D2a's fresh 12 cells)
   and a standing generalization test (R2's benchmark family) with the law's predictions
   pre-committed.

**What this means for a new conversation.** Do not open by agreeing, and do not open by
declaring a result final. Open by asking what the newest number *means for our specific
system* and what question it opens. Peer-level pushback is expected and wanted; hedging and
diplomatic softening are noise. When new evidence could alter a fundamental, question the
fundamental — but remember the system under question need not be the one we started on
(the register died; the live system is now anchoring/escape, and that migration is the
point, not a detour).

## 11. References *(external work this record engages; formal citations to be fitted at paper stage)*

- **Tsui et al. (2025), "Self-Correction Bench" (NeurIPS 2025).** The **Self-Correction
  Blind Spot**: LLMs fail to correct errors in their own output while fixing identical
  errors from external sources (~64.5% failure across 14 models); a minimal "Wait" prompt
  reduces it ~89%. *Our relation:* orthogonal, mechanism-level (§9.3.1) — Tsui's axis is
  *detection*/provenance, ours is *escape*/distributional-conditioning; D2a shows provenance
  near-inert in our setup (ΔPULL ≤ 0.028), so the blind spot does not bite where the failure
  is announced.
- **Olausson et al. (2024), "Is Self-Repair a Silver Bullet for Code Generation?" (ICLR
  2024).** Compute-matched, self-repair is often ≤ i.i.d. sampling, especially at small
  budgets; the bottleneck is the model's inability to produce accurate feedback about *why*
  code is wrong. *Our relation:* the **methodological anchor** and the closest ally — our
  escape-distance elimination argument (§9.3.1) is a mechanism-level derivation of their
  empirical result, and their "feedback is the bottleneck" is our "direction requires rich
  feedback."
- **Chen et al., "Teaching Large Language Models to Self-Debug" (Self-Debug).** GPT-4
  improves MBPP ~+3.6% and TransCoder/Spider substantially *without* unit-test execution —
  the strongest published support for "the candidate itself helps." *Our relation:* the
  reconciliation is baseline + regime — Self-Debug measures against **greedy** (not compute-
  matched best-of-n), and its largest gains are on **near-correct-by-construction** tasks
  (code translation, text-to-SQL) where the candidate is scaffolding and errors are *local*
  — our "point the attractor at a near-success" regime. Not a contradiction; a different
  point on the coverage/locality surface.
- **"How Many Tries Does It Take?" (2026).** Self-repair reported universally effective
  across 7 models on HumanEval + MBPP-Sanitized — *our exact benchmarks*; also reports name
  errors repair easily while **assertion errors are hardest**, and gains grow with scale
  (≤ +5.5pp at 70B). *Our relation:* the **direct challenge** to address head-on, and the
  reconciliation is inside it — our failure mix is ~50% assertion-class (structural), 2%
  syntax, and we run 1.5B; they average over easy (local) error types at large scale. The
  local-vs-structural error axis is the reconciling variable and a Phase-3 stratification
  target.
- **Kamoi et al. (2024), TACL — survey of LLM self-correction.** Concludes no prior work
  demonstrates successful *intrinsic* self-correction (from the model's own feedback alone)
  on reasoning. *Our relation:* consistent with our B2 result (intrinsic self-refinement
  buys nothing); we extend it to code with execution ground truth and give the *mechanism*
  (undirected escape → resampling).
- **Cross-Context Review line (2026)** and an **information-theoretic self-correction
  preprint (2026):** fresh-context / external-channel framings escape the correlated-error-
  mode problem. *Our relation:* corroborating context for "directed external signal" over
  "self-review"; cite as convergent, not foundational.

*Note on independence (to state honestly at paper stage):* the anchoring/escape line was
reached from our own DIAG-8 spin-off before we surveyed Tsui/Olausson; we position as
**convergent corroboration from an independent experimental path**, not priority, and cite
prominently.

### Reconciliation ledger *(appended 2026-07-15; one entry per reference per design decision it influenced)*

Rule ([PHASE_3B.md] charter): no external conclusion is imported as a general truth or a
design constant. Each entry states (a) their setup specifics, (b) the delta to ours,
(c) what their result does and does not license here.

- **Olausson et al. (2024) → R3's four-arm decomposition (W3).** (a) Their feedback
  decomposition uses **human/oracle feedback arms vs self-generated feedback** on
  GPT-3.5/GPT-4, compute-matched, on APPS-class problems; the bottleneck localization
  ("the model cannot produce accurate feedback") comes from the oracle arm beating the
  self arm. (b) Ours is a 1.5B base model, execution-trace feedback (templated, no
  model in the loop) vs model-generated abstraction, on a pass@50 = 0 stratum.
  (c) **Licenses:** the *decomposition logic* — without a feedback-ceiling arm, a
  repair null is ambiguous between "direction doesn't help" and "this model can't
  produce direction"; hence R3's ABSTRACT-trace arm exists. **Does not license:** any
  magnitude expectation — their gap sizes were measured at 100–1000× our scale with
  human-quality feedback; nothing transfers numerically.
- **Self-Debug (Chen et al.) → ABSTRACT-trace arm framing (W3).** (a) Gains measured
  against **greedy** (not compute-matched best-of-n), largest on
  near-correct-by-construction tasks (TransCoder, Spider) where errors are local; the
  "explanation" channel is model-generated. (b) Our control is compute-matched i.i.d.
  (B1-50), our stratum is structural failure (0/50), our trace channel is verbatim
  execution output. (c) **Licenses:** trace-style feedback as the *strongest known
  candidate* for the direction channel — worth a dedicated arm. **Does not license:**
  any expectation that repair beats resampling here — their baseline never asked that
  question, and their regime (near-correct) is the one D2c/E6 tests separately.
- **"How Many Tries" (2026) → R3 recovery stratification (W3/W4).** (a) Self-repair
  universally effective across 7 models on HumanEval/MBPP-Sanitized — our exact
  benchmarks — with gains growing with scale (≤ +5.5pp at 70B); **name errors repair
  easily, assertion errors are hardest**. (b) Our failure mix is ~50% assertion-class
  at 1.5B, and R3's stratum is by construction the hardest tail. (c) **Licenses:** a
  pre-committed *check*: their error-type axis predicts which stratum problems are
  recoverable — R3 recoveries (if any) should skew toward non-assertion error classes;
  we stratify recoveries by error type and test that prediction. **Does not license:**
  the "universally effective" headline — averaged over easy error types at scales
  where the mechanism has capacity we don't have.
- **Tsui et al. (2025) → E7 prompt design (W1) — formalizing the existing
  reconciliation.** (a) Detection-axis result: models fail to notice their own errors;
  "Wait"-style prompts recover ~89% of the gap; instruct models, natural-language
  reasoning tasks. (b) Our failures are announced (detection removed); D2a measured
  provenance ΔPULL ≤ 0.028 — inert. (c) **Licenses:** treating E7's avoidance framing
  as a *verb/instruction* intervention (the live 3–4× lever per D2a), not an
  attribution one; predicts "someone else's failed attempt" framing adds nothing to
  E7. **Does not license:** any expectation about escape magnitude — Tsui never
  measures distance-to-artifact.

*Appendix pointers. Architecture [ARCHITECTURE.md]; decision log **D1–D16**
[DECISIONS.md] (D11 precision, D14 statistical reproducibility, D15 retracted, D16 =
Finding F1); phase/gate log [PHASES.md]; metric estimators [METRICS.md].
Plans: [PHASE_M.md] (stack rebuild), [PHASE_3.md] (benchmark screen + 3b/3c design),
[PHASE_3R.md] (the H1/F2 audits + D-measure, Addenda I–III), [DIAGNOSTICS.md]
(DIAG-1..11). Verdict artifacts: Phases 0–2
[artifacts/h1_result.json, h1_v2b_result.json, h2_result.json, h2_b2_result.json];
diagnostics [artifacts/diag{1..11}_*.json]; Phase M
[artifacts/m3_rebaseline.json, m4_verifier_revalidation.json, m5_relock.json];
Phase 3a [artifacts/phase3a_screen_{complete,c05b,confirm,confirm15,confirmhard,
lcb_easy,lcb_med}.json, phase3a_characterization.json]; Phase 3R
[artifacts/r1b2b_stratified_auroc.json, r1b2c_length_bias.json,
dmeasure_conditioning.json (incl. per_sample_D2b), dmeasure_d2a_verb_provenance.json,
phase3a_screen_r2_base_T10.json, phase3a_screen_r2_base_T12.json; intact pools awaiting
exec-only: runs/modal/bcb_cand_r2_{base,instruct}_T08.json; crash-recovery record in
PHASE_3R.md "CRASH RECOVERY (2026-07-14)"; pending rerun: r1b2d retrain, r2 instruct
T=1.0/1.2 + LCB arm, dmeasure_d2c_partial_credit.json].
Scripts: [scripts/modal_rgr.py] (T4 verifier/retrain), [scripts/modal_phasem.py]
(L4 gates + D-measure/D2a), [scripts/modal_phase3a.py] (BigCodeBench screen + R2),
[scripts/modal_lcb.py] (LiveCodeBench), [scripts/dmeasure_analysis.py] (D2b),
[scripts/r1b2_analysis.py] (R1b.2a/b/c). Difficulty proxies
[artifacts/phase0_difficulty_proxy.csv].*
