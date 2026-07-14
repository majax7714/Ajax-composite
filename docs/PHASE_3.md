# Phase 3 — When does cross-step conditioning pay?

*Written 2026-07-13, after the diagnostic record closed (DIAG-1..10). This is the
next experiment — not a rescue of the register (the H2 verdict stands), the
experiment the diagnostics earned. Pre-registration: predictions, gates, and kill
criteria are committed here **before** each run; they stay standing whether they
hold or not.*

---

## 0. The corrected premise — read before anything else

DIAG-10 was over-read in its first write-up ("Phase 3 bet confirmed"). The error was
in the **decision rule**, not the run. The rule used *flatness* as the bar; the
correct control is **B1**.

| condition | step7 | slope |
|---|---|---|
| B1 (no cross-step channel at all) | 0.762 | +0.062 |
| ABSTRACT | 0.787 | +0.088 |

0.025 apart at ~0.05 SE — **half a standard error.** B1 rises too; both are noise
around flat. Against B1, ABSTRACT shows **no benefit. It shows no harm.**

**What DIAG-10 established:**
- ✅ **The candidate anchor causes the refinement collapse.** ABSTRACT vs B2+fb carry
  identical execution feedback and differ only in the candidate text: +0.088 vs
  −0.162, gap **+0.225**, several SE, same stack/problems/step-0. A clean causal
  intervention — this justifies Phase 3's design.
- ❌ **That feedback provides positive benefit.** Untested. The trajectory metric
  detects *harm* without headroom but **cannot detect benefit** without headroom (on
  a 0.70-coverage subset most step-0 failures are unsolvable at this scale). Second
  handicap: binary `frac_tests` + no per-test names → ABSTRACT got only a 5-way
  `error_type` ≈ **2 bits**. The null has two sufficient explanations (no headroom,
  no signal) and cannot separate them.

**Therefore: "the abstraction channel pays" is Phase 3's HYPOTHESIS, not its
premise.** The anchoring finding licenses the design; the benefit claim must be
earned. (Corrected in [DIAGNOSTICS.md] DIAG-10 verdict + roll-up, 2026-07-13,
append-not-revise.)

---

## 1. DIAG-11 — conditional recovery (free, CPU, non-blocking)

Pure re-analysis of the committed DIAG-10 rollouts (`runs/modal/diag10_feedback_2x2.json`)
— the only benefit signal extractable from data already on disk. Stratify the 80 dev
problems by step-0 outcome; on the **step-0-failed** subset (24 problems, shared
step-0 so the subset is identical across conditions) compute the fraction **recovered**
(any of steps 1–7 passes):

- **B1** — recovery by i.i.d. resampling (the chance rate).
- **ABSTRACT** — recovery with feedback, no anchor.
- **B2+fb** — recovery with feedback and anchor.

Question: *given that you failed and were told why, do you recover more often than by
simply drawing again?*

**Pre-registered prediction:** ABSTRACT recovery exceeds B1's by a **modest margin (a
few points), not significant at n≈24.** Direction informative, magnitude not. **If
ABSTRACT < B1, that is a red flag** worth knowing before spending Phase 3's budget.
Cannot change Phase 3's design (§4 gate is mandatory regardless); it sets the **H1
prior**. Output: `artifacts/diag11_conditional_recovery.json`.

**RESULT (done 2026-07-13):** recover-any B1 **0.917** = ABSTRACT **0.917** (Δ+0.000),
B2+fb 0.542 (Δ−0.375); sustained@step7 B1 0.500, ABSTRACT 0.583 (+0.083, <1 SE),
B2+fb 0.167. **No benefit signal, no red flag** — the recover-any metric is
ceiling-saturated (22/24 recover by resampling alone → these failures are
low-probability draws, not hard problems, so benefit is untestable here, per §0). The
**anchor prevents recovery** (B2+fb 13/24 vs B1 22/24) — replicates the DIAG-10 harm.
**H1 prior stays ~50/50.** Full write-up: [DIAGNOSTICS.md] DIAG-11.

---

## 2. The reframe — what the paper is now about

**Not the register.** The data does not support a register paper. It supports a paper
about **when cross-step conditioning pays**, with a sharp, novel, measured mechanism:

> Conditioning on the failed *candidate* anchors the model to its own mistake and
> makes refinement anti-refine (DIAG-8: adjacent candidates 0.35× as far apart as
> i.i.d.; DIAG-10: −0.225 vs the same feedback without the candidate). Conditioning
> on an *abstraction* of the failure removes the harm. Whether it adds benefit
> depends on **pool coverage** — at coverage ≈0.85 there is nothing to add and
> everything to lose.

This explains why the self-correction literature contradicts itself: different papers
sit at different points on the same coverage curve, in different anchoring regimes,
without knowing it. The register becomes **one mechanism tested inside that frame**,
not the thesis.

---

## 3. Prerequisite — Phase M ✅ COMPLETE (2026-07-13)

Phase 3 is materially bigger (more conditions, harder benchmark, longer solutions, a
large-k screen), so throughput was load-bearing. [PHASE_M.md] is **done** — vLLM +
bf16 + L4, `prompt_embeds` register path validated (M1), decoupled CPU execution,
100× throughput (M2), baselines re-based with an explained bf16 lift (M3). Two
outcomes bind Phase 3: **(a) V-v2b must be retrained on the deployment distribution**
— its within-problem reranking edge collapsed on bf16 (M4) — folded into 3b on the
selected benchmark; **(b) reproducibility is now statistical, not bit-for-bit** (M5 /
[DECISIONS.md] D14) — Phase-3's bootstrap-CI gates already assume this. No Phase-3
number may be compared to any pre-migration number ([COMPUTE_ACCOUNTING.md]; §8).

---

## 4. Phase 3a — Benchmark screen. GATE, mandatory.

We have tested a refinement mechanism on a saturated benchmark **twice**; both nulls
were uninformative for the same reason. Never again. Select the task on its **pass@k
curve**, not by name.

**Screen (migrated stack):** per-problem pass@k at **k=50** for the generator across
candidates — LiveCodeBench (contamination-controlled), CodeContests, APPS
(interview/competition), BigCodeBench. Also viable: same benchmarks with a smaller
generator (0.5B) to push coverage down deliberately.

**Two pre-registered selection criteria — both must pass:**
1. **Coverage band.** pass@8 ∈ **[0.30, 0.60]** *and* **pass@50 − pass@8 ≥ 0.15**.
   Reachable but improbable. Too high (our 0.85) → nothing to add, pool to lose; too
   low (pass@50 ≈ 0) → no foothold. Headroom must be *reachable*, not merely absent.
2. **Feedback richness.** Many tests per problem (**≫3**), so execution yields "k/n
   tests passing, failing: [names]" not a binary. DIAG-10's ABSTRACT got ~2 bits —
   co-equal criterion, not a nicety. It is also the most faithful to the
   energy-landscape idea: partial credit is the gradient to descend. MBPP/HumanEval
   are flat with a delta spike at "correct" — nothing to descend.

**GATE 3a:** a benchmark satisfying **both** exists. **If none does at 1.5B:** the
program is dead at this model scale — report it (itself a real finding about where
refinement can live). **Do not proceed to 3b on a benchmark that fails the screen —
that is the exact error that produced the H2 null.** Select on criteria, run the
*full* benchmark, difficulty-stratified results as secondary (no cherry-picked
subset). (Absorbs DIAG-6, descoped at [DECISIONS.md] D12.)

### 4.1 Screen execution plan + pre-registration (committed 2026-07-13, before running)

The reference stack has HumanEval 0.902 / MBPP-ish saturated and **test-poor**
(HumanEval binary-executed; MBPP median 3 asserts) — both fail criterion 2. So the
screen must reach for richer, harder benchmarks. **Two-part screen:**

- **Part A — feedback richness (criterion 2), cheap, no generation.** Load each
  candidate's metadata and report tests-per-problem + execution paradigm
  (function-call vs stdin/stdout). Pure dataset property.
- **Part B — coverage (criterion 1), GPU.** For the feedback-rich, tractable
  candidate(s): generate **k=50** on a representative subset with vLLM bf16, execute,
  compute pass@8 and pass@50.

Tractability note: function-call benchmarks (BigCodeBench, EvalPlus MBPP+/HumanEval+)
reuse an assert/unittest driver; stdin/stdout benchmarks (APPS, CodeContests,
LiveCodeBench) need a separate I/O-comparison harness. Screen the tractable
feedback-rich candidates first; expand only if none qualifies.

**Pre-registered predictions:**
- *Criterion 2:* BigCodeBench (unittest, many methods) and EvalPlus MBPP+/HumanEval+
  (dozens–hundreds of augmented tests) and APPS/CodeContests/LiveCodeBench (many I/O
  cases) all **pass ≫3**; plain MBPP (3) / HumanEval (binary) **fail** (already shown).
- *Criterion 1:* **BigCodeBench is the most likely qualifier** — Qwen2.5-Coder-1.5B
  bf16 pass@8 predicted **≈ 0.40–0.55** (in-band), with pass@50 − pass@8 ≥ 0.15.
  EvalPlus MBPP+/HumanEval+ likely **too easy** (pass@8 > 0.60 — same easy problems,
  just more tests). APPS/CodeContests likely **too hard** (pass@50 ≈ low → no
  foothold). **Prediction: the gate PASSES with BigCodeBench.** Genuine uncertainty:
  BigCodeBench-Complete may land a hair above 0.60 (Qwen2.5-Coder is strong for 1.5B);
  if so, **BigCodeBench-Hard** is the in-band fallback.
- If BigCodeBench also exceeds 0.60, the 0.5B generator (push coverage down) or the
  Hard split is the next lever before declaring the program dead at 1.5B.

Output: `artifacts/phase3a_screen.json`, `scripts/modal_phase3a.py`.

---

## 5. Phase 3b — the refinement channel study

Selected benchmark; matched compute throughout (unchanged budgeted unit,
[COMPUTE_ACCOUNTING.md]).

| channel | conditioning | role |
|---|---|---|
| **B1** | none (i.i.d. + verifier rerank) | control |
| **ANCHOR** | previous candidate + rich feedback | the known-bad channel |
| **ABSTRACT-text** | rich feedback as text, no candidate | the Phase-3 bet |
| **REG+** | same feedback, through a learned register | the register's last stand |

> **Verifier note (from Phase M / M4, 2026-07-13).** V-v2b does **not** survive the
> bf16 substrate change: its within-problem reranking edge over likelihood collapsed
> from +0.15 to +0.016 (global AUROC still holds, 0.772). So **B1's verifier-rerank
> and any V-dependent selection require a verifier retrained on the *selected
> benchmark's* bf16 candidates** — this retrain folds into 3b (do not reuse V-v2b as
> a reranker on the new stack without revalidating). On a headroom-bearing benchmark
> (pass rate ~0.3–0.6, vs HumanEval's 0.65) reranking matters more, so a good
> verifier is worth more there than the M4 numbers on saturated HumanEval suggest.

### 3b-lite (NO training — prompt-level; runs first)

B1 / ANCHOR / ABSTRACT-text answer the decisive questions for a few dollars before
any engineering:

- **H1 (the bet, and the gate): ABSTRACT-text > B1 at matched compute.** The claim
  DIAG-10 could not test. Primary: pass@1 at matched compute; secondary: per-step
  trajectory, conditional recovery on step-0 failures. **Kill:** ties B1 within CI →
  refinement does not pay even with headroom, rich feedback, and no anchor. The
  inference-as-relaxation direction is dead at this scale — **publish the negative**
  (strong, mechanistic, well-characterized).
- **H2 (replication): ANCHOR < B1.** Confirms the anchoring tax survives on a task
  with headroom (DIAG-8/10 established it only on a saturated one). If ANCHOR *helps*
  here, the anchoring story is coverage-dependent — itself a finding, reframes 3c.

### 3b-full (only if H1 passes) — REG+, carrying all three measured fixes

Anything less repeats a known failure:
1. **Rich input into U** — failing tests + error class, not φ(candidate). DIAG-2:
   current input at passed_{t−1} AUROC 0.558 (starved). The only lever that touches U.
2. **On-policy, set-membership objective** (GRPO, execution reward) — not imitation.
   D2(a) was the wrong call; DIAG-4·3 showed imitation moved the right decision tokens
   TF (99.7%) and still gave zero sampled effect.
3. **In-domain, length-matched training.** DIAG-5: r₀ steering ×1.33 in-domain, ×0.28
   (reversed) out of domain.

- **H3 (the register's last stand): REG+ ≥ ABSTRACT-text.** Its only remaining case,
  handed to us by DIAG-7/8/10: a 128-dim latent is *structurally incapable* of
  anchoring (it cannot reproduce a failed candidate; text can and does), so it may
  carry the diagnostic signal with immunity to the exact failure that sinks text.
  **Kill:** REG+ ties or loses to ABSTRACT-text → the register is dead for good, and
  the paper is the anchoring/abstraction/coverage result (novel regardless).

---

## 6. Phase 3c — the coverage sweep (only if H1 passes)

The general claim: **refinement benefit is a function of pool coverage, and the
anchoring tax is paid at every coverage level.** Make coverage the independent
variable (model size 0.5B/1.5B/3B and/or difficulty stratum); plot
gain-from-refinement vs coverage per channel. **Predicted shape: inverted U** — zero
at high coverage, zero at zero coverage, peaked between. Existing results are already
one point (coverage 0.85: latent gain 0.000, text gain −0.061, anchoring tax
measured) — the negative becomes *data*. **That is the paper.**

---

## 7. Honest priors, on the record

- **H1: ~50/50.** DIAG-11 (done) left it there — recover-any was ceiling-saturated
  (no signal either way), no red flag. Rich feedback + headroom + no anchor is
  refinement's best shot; if it fails there it fails everywhere.
- **H2: ~85% ANCHOR < B1.** Mechanism measured; no reason it vanishes with headroom.
- **H3: ~30%.** The register must justify a 128-dim bottleneck against raw text in an
  architecture built to condition on text. Expect to kill it — and be glad to, because
  by then the paper does not need it.

---

## 8. Out of scope

- Any comparison to pre-migration numbers (re-lock first, M5).
- Rescuing the H2 verdict (it stands).
- Running 3b on a benchmark that fails the 3a gate (**the cardinal sin — how we got
  here**).
- Building REG+ before H1 passes.
- Any claim that DIAG-10 established feedback benefit (§0).

---

## 9. Sequence

1. **DIAG-11** (free, CPU, non-blocking) — sets the H1 prior. *[done — see §1 / [DIAGNOSTICS.md]]*
2. **Correct the DIAG-10 verdict + roll-up row** per §0 (append, not revise). *[done 2026-07-13]*
3. **Phase M** ✅ — stack migration, gates M0–M5 done (vLLM/bf16/L4, 100×; V-retrain
   + statistical-lock outcomes carried into 3b / D14).
4. **Phase 3a** ← NEXT — benchmark screen. GATE: both criteria.
5. **Phase 3b-lite** — B1 / ANCHOR / ABSTRACT-text. No training. GATE: H1.
6. **Phase 3b-full** — REG+, all three fixes. Only if H1 passed. H3.
7. **Phase 3c** — coverage sweep. Only if H1 passed.

Pre-register predictions and kill criteria at each gate, before each run. That
discipline is why this project's negative result is worth more than most positive
ones.
