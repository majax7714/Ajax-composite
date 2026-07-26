# Phase 21 — is the sink general, Qwen-specific, or is DeepSeek simply the exception?

*Charter opened 2026-07-26. Twelfth iteration of the unattended loop ([AUTONOMOUS_LOOP.md],
Amendments 1–5). Opened out of a **halt**: Phase 20 refuted a live claim 1:1 and the author
reviewed and cleared the loop to proceed. First charter written under **Amendment 5**, so it
carries a step-2a literature record. Append-only; frozen before spend.*

---

## 0. Why this question, and why not the one first proposed

Phase 20 measured the architecture twin at true match, paired against its Coder sibling on
shared problems: **both sink, indistinguishably** (−0.0372 vs −0.0460, difference
+0.0088 ± 0.0157, p 0.57). The family-contrast leg of claims 8 and 11 is dead as stated.

The first stub proposed *"do DeepSeek-1.3B and StarCoder2-3B sink at true match?"* — a
**family** question. That framing presumes the axis Phase 20 just falsified. Put every
committed cell on a common footing instead, using the compression intercept **validated
out-of-sample by Phase 20** (predicted −0.0398 for the twin, measured −0.0372):

| model | size | family | intercept at match | measured at match? |
|---|---|---|---|---|
| Coder-0.5B | 0.5B | Qwen-Coder | −0.029 | no |
| **DeepSeek-1.3B** | 1.3B | DeepSeek | **+0.011** | **no** |
| Coder-1.5B | 1.5B | Qwen-Coder | −0.056 | yes (−0.046 / −0.064) |
| general-Qwen-1.5B | 1.5B | Qwen | −0.040 | yes (−0.037) |
| **StarCoder2-3B** | 3B | StarCoder2 | −0.021 | **no** |
| Coder-3B | 3B | Qwen-Coder | −0.058 | yes (−0.051) |
| Coder-7B | 7B | Qwen-Coder | −0.020 | yes (−0.008) |

**This is a gradient, and "non-Coder" is not the seam.** Both Qwen models sink; StarCoder2 is
intermediate with a CI spanning zero; **DeepSeek is the only model with a positive
intercept**. Within Coder the effect is non-monotone in size, peaking at 1.5–3B. **DeepSeek
has been carrying the entire "non-Coder families are clean" generalisation on its own**, and
it has never been measured at its own match.

> **The question:** at true match, on shared problems, which models fail to beat the copy
> null — and does the pattern follow **size** (the general null), **architecture family**, or
> **DeepSeek alone**?

---

## 1. Step 2a — literature check *(Amendment 5; performed before this charter was frozen)*

**(a) The general-effect null this phase must beat**, now §11: Huang et al., *LLMs Cannot
Self-Correct Reasoning Yet* (arXiv 2310.01798, ICLR 2024) — intrinsic self-correction fails
and *sometimes degrades*, worst in small models, with apparent gains attributable to sampling
and selection rather than critique content. §9.3 already established that this record's ~2-bit
feedback supplies no direction, so our setting is nearer *intrinsic* than *fed-back*.
**Under Amendment 5 this charter may not claim a family- or model-specific cause without
beating that null, and branch A below is written so that the null can win.**

**(b) A direct tension the search surfaced, and it cuts against us.** Public repair
benchmarks put **Qwen2.5-Coder ahead of DeepSeek-Coder at code repair** — 73.7 Aider, 75.2
MdEval — i.e. **the opposite ordering to this record's**, which has Qwen-Coder degrading under
repair-style conditioning while DeepSeek does not. Two scope differences reconcile them and
both are real: those results are **32B instruct-tuned** models, whereas every cell here is a
**base model at 0.5–7B**; and Aider/MdEval supply **rich feedback** (error text, diffs) where
our prompt supplies a **pass count**. *Consequence for this charter:* a "Qwen-base effect"
finding could **not** be stated as a property of Qwen models generally — it would have to be
scoped to *small base models under near-zero-information feedback*, and the tension recorded.
This is exactly the kind of over-reach Amendment 5 exists to catch **before** the run.

**(c) What the search did not find,** after three queries: any **quantified**
regression-toward-exemplar-quality coefficient. Statements that exemplar quality matters and
that models are demonstration-sensitive are abundant and qualitative. The compression law
(b ≈ 0.60–0.70, eight cells, two families) still appears to be this record's novel product.
*Snippet-level only; not source-verified, and marked as such.*

---

## 2. Design

**Cell.** One shared problem set, **four models** measured on it simultaneously, each at
**its own** true match via per-problem per-model artifact selection — Phase 20's
`_p20_select` rule, extended from two rungs to four:

| | model | revision | role |
|---|---|---|---|
| 1 | `Qwen/Qwen2.5-Coder-1.5B` | `df3ce67c…` | the reference sink |
| 2 | `Qwen/Qwen2.5-1.5B` | `8faed761…` | architecture twin (Phase 20: sinks) |
| 3 | `deepseek-ai/deepseek-coder-1.3b-base` | *as pinned in `J7_MODELS`* | **the only clean intercept** |
| 4 | `bigcode/starcoder2-3b` | `733247c5…` | intermediate intercept |

**Steps.** (i) k=24 i.i.d. sweeps over the 80-problem donor pool for models 3 and 4 (models 1
and 2 already have committed sweeps) — 2 × 80 × 24 = **3,840** generations. (ii) Four-way
feasibility at per-problem tolerance ±0.10. (iii) Eight arms — 4 models × {i.i.d.,
conditioned} — at **k = 24**, one seed (**367**), on the common set.

**Fallback, pre-registered.** The four-way constraint is tighter than Phase 20's two-way
(61/80). **If four-way n < 30, fall back to two independent pairwise cells** (DeepSeek vs
Coder-1.5B; StarCoder2 vs Coder-1.5B), each built exactly as Phase 20's, and say so. The
fallback is chosen in advance so it is not a post-hoc rescue.

**Primary statistics, per model:** cond − i.i.d. and cond − artifact, each with a bootstrap
CI over problems (seed 373, B = 8000); **below-both-nulls** requires both CIs to exclude
zero. **Secondary:** paired differences against Coder-1.5B on the shared set.

**Power, stated in advance (§8 entry 12).** Projected from Phase 20's achieved per-arm
spread: at n ≈ 45 and k = 24, per-model SE ≈ **0.014**, MDE ≈ **0.039**. That resolves an
effect the size of the twin's (−0.037) at roughly 80% power and the Coder reference's
(−0.046) comfortably. **It cannot resolve an effect of −0.02** — so a null on StarCoder2,
whose intercept estimate is −0.021, would be **genuinely uninformative** and must be reported
as such rather than as "clean." Stated now, before the data.

### Frozen decision rules and kill criteria — *evaluated inside the branch expression (§8 entry 11)*

- **OFF-TARGET** ⟺ any model's achieved aggregate Δ_art outside **±0.020**.
- **INSTRUMENT FAILURE** ⟺ any arm's parse rate **< 0.95**.
- **UNDERPOWERED** ⟺ n < 30 in the four-way *and* the pairwise fallback also yields n < 30.

### Branches, with odds committed before the run

| | branch | reading | odds |
|---|---|---|---|
| **A** | **DeepSeek AND StarCoder2 both sink** | **the general null wins.** Degradation under weak-feedback conditioning is a general small-base-model effect; the family axis collapses entirely and §0.2's Qwen-pathology extraction is dead as a family claim | **30%** |
| **B** | **both clean** | a **Qwen-base** effect — but scoped, per §1(b), to small base models under ~2-bit feedback, *not* to Qwen models generally, since public repair benchmarks order Qwen above DeepSeek | **25%** |
| **C** | **DeepSeek clean, StarCoder2 sinks (or is uninformative)** | **DeepSeek is the exception, not a family class.** The live question becomes what DeepSeek does differently — its compression slope is among the highest measured (0.78), i.e. it imitates the artifact most faithfully | **35%** |
| **D** | a kill criterion fires | no adjudication | **10%** |

C is the narrow favourite because it is what the intercept table already predicts (+0.011
vs −0.021) and because the intercept method has one out-of-sample validation. A is priced
substantially because it is the literature's prior and this record has just been burned for
not carrying it. B is priced lowest of the three substantive branches because it now requires
a scope caveat that public benchmarks impose on it.

### Cost

**Estimate $1.60–2.80.** Basis: Phase 18 ran 6,336 generations of 1.5B-class models on this
judge for a read $1.06; this is ~12,500 including sweeps, i.e. ~2.0×, giving ≈$2.10 central,
band widened for StarCoder2-3B being larger than the 1.5B class. MTD read **$86.83**
(2026-07-26) against **$100 report / $120 hard stop**; §4's within-$30-of-cap guard holds.
Loop total to date $8.79.

---

## 3. Pre-registration freeze

Frozen at commit `PENDING` (stamped at close), **before** any Phase-21 generation ran.

---
