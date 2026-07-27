# Phase 22 — the same question, properly instrumented

*Charter opened 2026-07-26. Thirteenth iteration of the unattended loop ([AUTONOMOUS_LOOP.md],
Amendments 1–6). Opened out of a **kill**: Phase 21 fired its own instrument gate and
adjudicated nothing. Append-only; frozen before spend.*

---

## 0. Why re-run rather than re-score

Phase 21 placed four models at their own true match on one shared set — n=56, every cell
within ±0.006 of match, per-model artifact selection verified non-collapsing — and then
`starcoder2_3b_iid` parsed at 0.9308 against a frozen ≥0.95 gate. **Branch D fired; nothing
was adjudicated** ([PHASE_21.md] §5).

Those numbers exist and are committed. **This phase does not cite them and does not re-score
them.** Re-adjudicating a killed phase by dropping the arm that killed it is a post-hoc
rescue, and the author who would write the corrected criterion has already seen the result it
would license. The only clean route is a fresh draw under a criterion frozen in advance.

> **The question, unchanged from Phase 21:** at true match, on shared problems, which models
> fail to beat the copy null — and does the pattern follow **size** (the general null),
> **architecture family**, or **DeepSeek alone**?

**What changed is the instrument, and one prior.** Phase 21's free desk-check ([PHASE_21.md]
§6) established that a between-arm parse asymmetry biases raw `cond − iid` **upward** by
≈ `parse gap × mean frac` — verified at 0.0086 predicted / 0.0082 observed on an independent
cell — while leaving the compression-law *intercept* untouched (Δa = δ_cond − δ_iid·(1−b);
at b≈0.88 only 12% survives). Applied to StarCoder2's arm that predicts a corrected effect
near **−0.036** rather than the −0.021 the intercept table carried. **That is design input
only and is not citable as a result** — but it changes the power arithmetic, because −0.036 is
resolvable at n=56 while −0.021 is not.

---

## 1. Step 2a — literature check *(Amendment 5; performed before this charter was frozen)*

**(a) The general-effect null still stands and must still be beaten:** Huang et al., *LLMs
Cannot Self-Correct Reasoning Yet* (arXiv 2310.01798, ICLR 2024) — §11. Branch A below is
written so the null can win.

**(b) A tension that cuts directly against this phase's favourite, and it is new.** A public
result reports **DeepSeek-Coder-1.3B with the largest degradation in its comparison set on
HumanEval Infilling — −61.10% relative** ([Assessing Small Language Models for Code
Generation](https://arxiv.org/html/2507.03160v4)). Our DeepSeek-1.3B is the model this record
keeps finding *clean* under conditioning. Infilling is a different task format (FIM, with
right-context) from our repair-style conditioning on a partial-credit artifact, so the two are
not in direct contradiction — but the existence of a documented regime where this exact model
degrades badly on partial code means **branch C may not be stated as "DeepSeek is robust to
code conditioning."** It would have to be scoped to *repair-style conditioning on a
partial-credit artifact at 1.3B*, with the infilling result recorded alongside. *Snippet-level
only, not source-verified, marked as such per [PHASE_21.md] §1(c).*

**(c) A near-neighbour that must not be conflated with our claim.** *Recursive Self-Training
Collapse in Code LLMs* (arXiv 2606.28438) reports that **all model families degrade
substantially** from baseline — a family-general degradation result, which is the shape branch
A predicts. But its mechanism is **retraining on self-generated code**, not inference-time
conditioning; it changes weights, we change only the prompt. If branch A fires, this paper is
**not** a prior claim to the same finding and must not be cited as one — nor may our result be
presented as independent of it without naming the distinction. Adjacent in the same genre:
*Lost in the Flow with Code Talkers* (arXiv 2606.08676) documents an "instruction-tuning tax"
degrading across two families — inapplicable here, since every model in this cell is a **base**
model.

**(d) What the search did not find:** any report of a *conditioned-vs-unconditioned parse-rate
asymmetry* biasing a code-generation contrast, and any quantified regression-toward-exemplar
coefficient. Both remain, as of this phase, unpre-empted so far as searching reveals.

---

## 2. Design

**Cell.** Identical to Phase 21's: the same 56-problem four-way set, the same per-model
artifact selection (deterministic given the committed k=24 sweeps, so it reproduces exactly),
four models each at **its own** true match. **Fresh generation seed `P22_SEED = 401`.**

**Why not a fresh problem set, stated rather than glossed.** The donor pool holds 80 problems;
56 cleared four-way feasibility. The remaining 24 are *exactly the ones that failed it*, so
they are not a fresh sample — they are a systematically infeasible one. A genuinely fresh
problem set requires mining new donors, which changes the instrument mid-question. The seed is
therefore the only clean source of a fresh draw, and it is a real one: sampling error is
independent across seeds, so this is a new estimate of the same quantity, not a re-score.

**The instrument change, and it is a diagnostic rather than a fix.** Phase 21 could not tell
whether StarCoder2's 50 empty completions were *the model emitting nothing* or *the extractor
returning nothing*, because raw completions were never persisted. Phase 22 **persists raw
completions alongside extracted code**, and pre-registers the decision both ways:

- **If the empties carry non-empty raw text** → this was an **extraction** failure, not a model
  property. The pre-registered fallback applies: **where no code fence is found, the full
  completion is taken as the candidate**, applied uniformly to all four models and both arms.
  Both scorings are reported.
- **If the raw text is genuinely empty** → the model emits nothing unconditioned, StarCoder2 is
  **outside this instrument's domain**, and its cell is voided and reported as such — the same
  verdict Phase 18 reached for T > 1.0. Not a failure to be worked around.

**The prompt is byte-identical to Phase 21's.** No primer, no scaffold. Comparability with
every historical cell is worth more than a convenient parse rate, and a prompt change would
put this cell on the far side of a boundary the record would then have to police forever.

**Arms.** 4 models × {i.i.d., conditioned} at **k = 24** on the common set = **10,752**
generations. No new sweeps: both k=24 sweeps are committed.

**Primary statistics, per model:** cond − i.i.d. and cond − artifact, bootstrap CI over
problems (seed 409, B = 8000); **below-both-nulls** requires both CIs to exclude zero.
**Secondary, pre-registered:** the same statistics under parse-only scoring, reported always
and for every model, so the sensitivity is visible whether or not it matters.

### Frozen decision rules and kill criteria — *evaluated inside the branch expression (§8 entry 11)*

Kill criteria are now **per-cell**, which is the correction §8 entry 13 demands:

- **CELL VOID** ⟺ that cell's parse rate < 0.95 **or** its **between-arm parse gap > 2.0pp**.
  The differential is the operative quantity: it is what biases the contrast (§8 entry 13).
  A void cell is excluded from adjudication; **other cells are unaffected.**
- **CELL OFF-TARGET** ⟺ that model's achieved aggregate Δ_art outside **±0.020**.
- **PHASE KILLED** ⟺ the **Coder-1.5B reference cell** voids, **or** n < 30, **or** every
  non-reference cell voids.
- **INSTRUMENT VALIDATION** ⟺ Coder-1.5B lands within **±0.040** of its committed at-match
  reference (**−0.048**, the mean of the two committed at-match measurements). The band is
  2 SE of a seed-to-seed difference (per-cell SE ≈0.014, difference SE ≈0.020) — wide enough
  not to fire on noise, narrow enough to catch real drift. **Failing it kills the phase**, on
  the grounds that an instrument that cannot reproduce a known cell cannot adjudicate an
  unknown one.

### Committed point predictions *(scored at close)*

| model | predicted cond−iid | basis |
|---|---|---|
| Coder-1.5B | **−0.048** | committed at-match reference |
| general-Qwen-1.5B | **−0.037** | Phase 20 paired measurement |
| DeepSeek-1.3B | **+0.011** | compression-law intercept (unchanged) |
| StarCoder2-3B | **−0.036** | intercept −0.021 plus the desk-check's bias correction |

### Branches, with odds committed before the run

| | branch | reading | odds |
|---|---|---|---|
| **A** | DeepSeek **and** StarCoder2 both sink | **the general null wins**; the family axis collapses and the effect is a general small-base-model property. Must be distinguished from arXiv 2606.28438, which is retraining, not conditioning (§1c) | **20%** |
| **B** | both clean | a **Qwen-base** effect, scoped to small base models under ~2-bit feedback | **5%** |
| **C** | DeepSeek clean, StarCoder2 sinks | **DeepSeek is the exception, not a family class** — and per §1(b) this may be stated only as robustness to *repair-style conditioning at 1.3B*, never as general robustness to code conditioning | **55%** |
| **E** | StarCoder2's cell voids again, DeepSeek adjudicates | partial result: DeepSeek reported, the family question stays half-open, and StarCoder2 is declared outside the instrument's domain | **15%** |
| **D** | phase killed (reference cell voids, n<30, or validation fails) | no adjudication | **5%** |

**⚠ These odds are NOT clean priors, and saying so is the point.** I have seen Phase 21's
un-adjudicated numbers. C is priced at 55% partly because that killed phase pointed there and
because the desk-check's bias correction points there. A pre-registration whose odds are
informed by data it refuses to cite is in an awkward position, and the honest resolution is to
**flag it rather than fake a clean prior**: these odds are worth little as evidence of
calibration for this phase, and the prediction accounting at close must be scored with that
caveat attached. The *decision rules* are uncontaminated — they were written to a standard
(per-cell, differential-based) derived from the failure mode, not from the result.

### Power, stated in advance

n = 56, k = 24 → per-cell SE ≈ **0.014**, MDE ≈ **0.039** at 80%. Against the committed
targets: Coder (−0.048) and general (−0.037) resolve comfortably; **StarCoder2 (−0.036) sits
right at the boundary — roughly 75% power**, so a null there is *weak* evidence, not clean.
DeepSeek's clean verdict does not need an MDE: it needs its CI to exclude effects past 0.039,
which the instrument achieves.

### Cost

**Estimate $1.70–2.90.** Basis: Phase 21 measured $2.87 for 14,592 generations = **$0.000197
per generation**, the record's most recent and most directly comparable rate; 10,752
generations gives **$2.12** central, band widened for judge variance. No sweeps needed.
MTD **$89.70** (2026-07-26) against **$130 report / $200 hard stop** (Amendment 6). Loop total
to date $11.66.

---

## 3. Pre-registration freeze

Frozen at commit `PENDING` (stamped at close), **before** any Phase-22 generation ran.

---

## 4. Step-9a search plan — *committed with this charter, before any result*

| if the branch is | queries | a hit that would change the reading |
|---|---|---|
| **A** | "conditioning degradation base code models across families"; "in-context partial solution harms code generation small models" | a family-general **inference-time** result would make this a replication rather than a finding; retraining results (§1c) do **not** count |
| **C** | "deepseek-coder pretraining fill-in-the-middle repository-level objective robustness"; "why is deepseek-coder robust to partial code context" | a documented pretraining-objective account would make this phase's result a *prediction of known architecture*, not a discovery |
| **E** | "base model empty generation rate unconditioned prompt code benchmark" | prior documentation of StarCoder2-class models failing to emit code unconditioned would turn our instrument note into a known limitation with a citation |

**Every branch:** re-check Huang et al.; re-check the DeepSeek-infilling tension in §1(b)
against whatever is found; and record what the search **failed** to find.
