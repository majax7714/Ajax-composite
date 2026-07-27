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

Frozen at commit `120f995`, **before** any Phase-21 generation ran. Entrypoint at `e11fb99`,
also before spend. Verifier `8702557` and the §4 search plan `dcd0cbe` were both committed
mid-run, before any result existed. Raw artifact committed unread at `4ab79a0`.

---

## 4. Step-9a search plan — *committed mid-run, before any arm was adjudicated*

*Appended while arms 4–8 were still generating. Amendment 5 requires a literature check at
the finding; a search run **after** seeing the result can be steered, unconsciously, toward
whatever confirms it. So the queries are fixed here, while the answer is still unknown. Under
§1(c)'s practice, anything returned at snippet level only is marked as such and not treated
as source-verified.*

| if the branch is | queries, in this order | a hit that would change the reading |
|---|---|---|
| **A** — both sink | "degradation self-correction base models code"; "small language model conditioning worse than sampling"; "in-context exemplar quality regression code generation" | any paper reporting the effect as **general across base families** would move this from our finding to a **replication**, and §0.2's Qwen-pathology framing would have to be withdrawn as a claim of novelty |
| **B** — both clean | "Qwen2.5 base model in-context degradation"; "family-specific self-repair failure code LLM"; "pretraining data code repair sensitivity" | a **pretraining-corpus** account of Qwen-family behaviour would supply the mechanism this record cannot reach, and the finding would have to be stated as consistent-with rather than evidence-for |
| **C** — DeepSeek exceptional | "deepseek-coder fill-in-the-middle repair robustness"; "DeepSeek-Coder pretraining repository-level objective"; "model-specific robustness to low-information feedback" | DeepSeek's **repo-level / FIM pretraining objective** is the obvious candidate mechanism; if it is documented as producing exemplar-independence, that becomes the leading explanation and this phase's result is its prediction, not a discovery |

**Applies to every branch:** re-check the general null (Huang et al., §11) against whatever
is found, and record — as §1(c) did — what the search **failed** to find, not only what it
returned. A null search result is evidence about novelty and belongs in the write-up.

---

## 5. RESULT — **BRANCH D: KILLED by a frozen kill criterion. No adjudication.**

*Closed 2026-07-26. Raw artifact `artifacts/h21_fourway.json` committed **unread** at `4ab79a0`
before any analysis. Independent verifier (`scripts/j21_verify.py`, committed at `8702557`
before any result existed) agrees on **every quantity and on the branch**.*

**The gate that fired:** `INSTRUMENT FAILURE ⟺ any arm's parse rate < 0.95`.
`starcoder2_3b_iid` parsed at **0.9308**. The other seven arms all parsed ≥ 0.9814.

| gate | value | verdict |
|---|---|---|
| OFF-TARGET (all \|Δ_art\| ≤ 0.020) | −0.0060 / −0.0045 / −0.0033 / −0.0023 | **passes** |
| UNDERPOWERED (n ≥ 30) | **n = 56**, four-way held; no fallback | **passes** |
| INSTRUMENT FAILURE (all parse ≥ 0.95) | **starcoder2_3b_iid = 0.9308** | **FIRES** |

**The branch expression consulted its own gates.** This is the first live test of the fix for
§8 entry 11, where Phase 18 printed `parse_ok false` and then adjudicated a substantive
branch above it. Here the kill criterion was evaluated *inside* the branch expression, fired,
and suppressed adjudication. The defect is fixed, demonstrated under conditions that would
have rewarded the bug.

### 5.1 Measured, NOT adjudicated

Recorded because the numbers exist and the raw artifact is committed; **none of it is a
finding**, and no claim status moves on it. n = 56, k = 24, seed 367.

| model | i.i.d. | cond | artifact | cond−iid [CI95] | cond−art [CI95] | below both nulls |
|---|---|---|---|---|---|---|
| Coder-1.5B | 0.3188 | 0.2732 | 0.3241 | **−0.0456** [−0.0717,−0.0202] | −0.0509 [−0.0710,−0.0318] | true |
| general-Qwen-1.5B | 0.2836 | 0.2471 | 0.2689 | **−0.0365** [−0.0566,−0.0170] | −0.0219 [−0.0370,−0.0064] | true |
| DeepSeek-1.3B | 0.2443 | 0.2443 | 0.2522 | **+0.0000** [−0.0161,+0.0160] | −0.0079 [−0.0152,−0.0014] | false |
| StarCoder2-3B | 0.2567 | 0.2350 | 0.2443 | −0.0217 [−0.0487,+0.0075] | −0.0094 [−0.0336,+0.0260] | false |

Paired against Coder-1.5B on the shared set: general +0.0091 ± 0.0159 (p 0.57);
DeepSeek **+0.0456 ± 0.0175 (p 0.0091)**; StarCoder2 +0.0239 ± 0.0187 (p 0.20).

**Design integrity held.** Per-model artifact selection did not collapse: every model pair
drew different artifacts on 23–40 of 56 problems. All four cells landed within ±0.006 of
true match — the tightest simultaneous positioning in the record.

### 5.2 Why the gate was RIGHT to fire — the diagnosis

A parse gate could be pedantry. It was not. Inspecting the 93 failing generations:

- **50 are empty completions**, all in the unconditioned arm;
- **~43 are indentation-loss** syntax errors — otherwise-coherent Python with every line
  flush-left.

**A decode-corruption hypothesis was tested and REJECTED.** If StarCoder2's tokenizer or the
decode path were dropping whitespace, indentation prevalence would be depressed across its
output. It is not: 0.7701 (iid) vs 0.7679 (cond), against 0.7783 for Coder-1.5B. Nothing is
stripping whitespace. The cause is the model.

**The real quantity is the between-arm parse differential, not the absolute level:**

| model | parse iid | parse cond | **gap** |
|---|---|---|---|
| Coder-1.5B | 0.9836 | 0.9948 | +1.1pp |
| general-Qwen-1.5B | 0.9866 | 0.9814 | −0.5pp |
| DeepSeek-1.3B | 0.9851 | 0.9963 | +1.1pp |
| **StarCoder2-3B** | **0.9308** | 0.9874 | **+5.7pp** |

StarCoder2 given only a problem statement often emits nothing extractable; given an artifact
to format from, it complies. **Empty generations score 0**, so they depress the i.i.d. arm and
bias `cond − iid` **upward — toward "clean."** The kill therefore protected branch C, the
charter's own 35% favourite, from being handed a win by a formatting asymmetry rather than by
reasoning. A gate that only ever fires against your disfavoured hypothesis is not doing work;
this one fired against the favoured one.

### 5.3 Prediction accounting

The compression-law intercept predicted all four cells, and all four intervals contain the
prediction. **Three of the four sit on clean arms** (Coder −0.056 pred / −0.0456 meas;
general −0.040 / −0.0365; DeepSeek +0.011 / +0.0000). The fourth, StarCoder2 (−0.021 /
−0.0217), sits on the **gated** arm and is **excluded from the accounting** — its apparent
near-exactness is not evidence, because the arm that produced it failed the instrument test.

**A downstream exposure this opens, and it is not small.** StarCoder2's committed intercept
of −0.021 was itself estimated from earlier cells that used the same unconditioned prompting.
If those cells carried the same empty-completion deficit, their i.i.d. arms were likewise
depressed and **the −0.021 intercept is biased toward zero** — i.e. StarCoder2 may sink harder
than the law records. Every StarCoder2 number in this journal inherits the question. Logged to
§0.4 as an open item; not investigated here.

### 5.4 Step 9a — literature *(Amendment 5)*

**The §4 branch queries were NOT run.** No branch was adjudicated, so the pre-registered A/B/C
query sets do not apply; they carry forward unspent to the phase that adjudicates. Recording
this because a search plan that gets run anyway, against whatever happened, is not a
pre-registration.

What was searched instead is the finding that *did* occur — conditioning-induced format
compliance as an evaluation confound. Two relevant results, **snippet-level only, not
source-verified**, per §1(c)'s practice:

- *The Format Tax* (arXiv 2604.03616) — grammar-constrained decoding lifts format compliance
  55.7% → 92.2% while reasoning accuracy stays 5–7pp *below* the freeform baseline.
  **Compliance and reasoning are separable**, which is exactly why a conditioning-induced
  compliance gain must not be read as a reasoning gain.
- *Cascaded Information Disclosure* (arXiv 2507.23776) — brittle answer extraction distorts
  cross-model comparison (90%+ parse failure for Phi-4 on GPQA under lm-evaluation-harness).

**What the search did NOT find:** any treatment of a *between-arm* parse asymmetry biasing a
conditioned-vs-unconditioned contrast specifically. The general hazard is established; this
particular instance of it appears unpre-empted.

### 5.5 Cost, and an honest gap

Generations: 3,840 (two k=24 sweeps) + 10,752 (eight arms × 56 × 24) = **14,592**. The charter
projected ~12,500 assuming n ≈ 45; the four-way held at n = 56, **17% above plan**.

**Cost $2.87** — MTD aggregate delta **$86.83 → $89.70** (Amendment 2's standing convention,
the same method every prior phase used), against a pre-registered **$1.60–2.80**.

**This is an OVERRUN, the first in eleven phases**, by $0.07 / 2.5% above the top of the band.
Cause is identified and was visible in the run: the charter sized the estimate at n ≈ 45 and
the four-way feasibility held at **n = 56**, putting 17% more generations through the arms
than planned. The estimate was right about the per-generation economics and wrong about the
design's own success — a cell that clears its feasibility bar by more than expected costs
more than expected. Worth stating because ten calibrated estimates in a row is exactly the
condition under which one stops sanity-checking the input assumptions.

*Cross-check.* Author-reported spend for 2026-07-26 is **$5.80**; Phase 20 measured $1.43 and
Phase 21 $2.87 = $4.30, leaving ~$1.50 for the same-day Phase-20 prerequisites (the
general-Qwen k=24 sweep and the j8 arms, 11:04–11:55). Consistent.

*An initial claim in this section was wrong and is corrected rather than removed.* This phase
first recorded the cost as **unmeasurable** (≈$2.44 derived from Phase 18's per-generation
rate) on the grounds that `modal billing report` needs workspace credentials the analysis
shell does not hold. That was a real limitation and an irrelevant one: **Amendment 2 defines
this record's cost measurement as the MTD aggregate delta**, which needs a single MTD figure,
not a per-run billing query. The tool was missing; the method was not. See §8 entry 14, which
is rewritten around that distinction.

### 5.6 What this phase settles, and what it does not

**Settles:** nothing about the sink. Branch D means no adjudication, and the temptation to
read §5.1 as "branch C, with an asterisk" is precisely what the criterion exists to refuse.
Three models were measured at true match on a shared set with clean instruments — that data is
committed and re-usable — but the phase's own question is **unanswered**.

**Does not settle, and must not be quietly claimed:** whether DeepSeek is exceptional. Its
cell is clean (parse 0.9851/0.9963) and its null is *informative* — the verifier's symmetric
guard confirms CI [−0.0158,+0.0159] excludes effects past the MDE, so this is a real bound,
not an underpowered shrug. But it was gathered inside a phase that failed its instrument test,
and re-adjudicating a killed phase by dropping the arm that killed it is a post-hoc rescue.
The successor must **pre-register** the re-adjudication.

**The successor.** The cheapest correct move is a three-model re-run of the *criterion*, not
the data: pre-register that (a) the parse gate is evaluated **per-cell**, so one model's
instrument failure voids that cell rather than the phase, and (b) a **between-arm parse gap
> 2pp** is itself a kill for that cell, since it is the differential — not the level — that
biases the contrast. StarCoder2 then needs an instrument that gets it to emit code
unconditioned before it can be measured at all; absent that, it is **outside this
instrument's domain**, the same verdict Phase 18 reached for T > 1.0. Note the awkward part
plainly: the author writing that criterion has now seen the numbers it would license.

### 5.7 Write-up surfaces — Amendment 4a compliance

*Each of the nine is updated **or** recorded as deliberately unchanged. The requirement is
that the decision is visible; a gate that is silent when skipped is how seven phases skipped
it.*

| # | surface | disposition |
|---|---|---|
| 1 | phase doc RESULT | **updated** — §5 above |
| 2 | §9.x addendum | **deliberately unchanged** — no claim moved, and the phase's durable content is methodological, so it landed in §8 entries 13–14 and §0.4 rather than in a claim narrative |
| 3 | §0 index rows | **deliberately unchanged** — branch D adjudicates nothing; no status moves |
| 4 | §0.3 evidence rows | **updated** — rows 8 and 11 carry a P21 marker recording that the at-match four-way was *attempted and killed*, so a later reader does not mistake this for untried ground |
| 5 | §0.4 open successors | **updated** — the top open item marked ATTEMPTED-AND-KILLED / STILL OPEN with the corrected-criterion successor; **one new open item added** (StarCoder2's intercept possibly biased toward zero) |
| 6 | living-record line | **updated** — Phase 21 banner replaces the Phase-20 halt |
| 7 | abstract banner chain | **deliberately unchanged** — Amendment 4a requires a banner "when a claim's status moved." None did. Recorded here so the skip is visible rather than invisible |
| 8 | `README.md` | **updated** — row 21, and the status block rewritten from HALTED to the kill |
| 9 | §8 ledger entry | **updated** — entries **13** (criterion granularity + wrong quantity) and **14** (cost measurement lost) |

---

## 6. Free desk-check ($0) — is StarCoder2's compression intercept biased toward zero?

*Appended 2026-07-26 after the close, on committed data only. No compute. §5.3 raised the
exposure; this settles it, and the answer is more useful than either outcome I expected.*

**Target.** The −0.0208 intercept comes from the Phase 7 M3 cell (n=39, `j7_*_M3_starcoder2_3b`).
If that cell carried the same unconditioned-arm deficit Phase 21 found, its i.i.d. arm was
depressed and the intercept biased **toward zero**.

**The asymmetry is real there, and smaller.** Zero empty completions in either arm — the
Phase-21 empty-completion mode does **not** appear. But the parse asymmetry does:

| arm | parse | mean frac |
|---|---|---|
| i.i.d. (A) | 0.9679 | 0.3281 |
| conditioned (B) | 0.9936 | 0.3362 |

**gap 2.56pp**, same direction as Phase 21's +5.7pp, under half the size. (Arm identity is
confirmed, not assumed: 0.3281 / 0.3362 reproduce the battery's committed `mean_iid` /
`mean_cond` exactly.) All **12** non-parsing generations score frac **0.0000** — the
assumption behind the whole concern, now verified rather than asserted.

**Result — the raw statistic is badly biased; the intercept is not.**

| | i.i.d. | cond | shift | gap |
|---|---|---|---|---|
| as-run | 0.3281 | 0.3362 | **+0.0080** | +0.0327 |
| parse-only | 0.3373 | 0.3372 | **−0.0001** | +0.0235 |

**Intercept: −0.0208 → −0.0208. It moves by 0.0000, i.e. 0.00 SE.**

**Why, and this is the part worth keeping.** Depressing the i.i.d. arm enters *both* axes of
the law: it lowers `shift = cond − iid` and lowers `gap = artifact − iid` by the same amount.
With `a = shift − b·gap`,

> **Δa = δ_cond − δ_iid·(1 − b)**

so at b ≈ 0.88 only **12%** of an i.i.d.-side bias survives into the intercept, and here even
that is cancelled by the conditioned arm's own small correction (δ_iid 0.0092, δ_cond 0.0010
→ Δa −0.0001). **The compression law's intercept is self-insulating against arm-asymmetric
quality loss.** The raw `cond − iid` statistic has no such protection — it moved 0.0081, from
positive to zero, on a 2.56pp gap.

The bias is also *predictable*: `parse gap × mean frac of parsing generations` = 0.0256 ×
0.337 = **0.0086**, against 0.0082 observed.

**Disposition.** The §5.3 exposure is **closed for the intercept** — StarCoder2's −0.021 needs
no correction and the eight-cell battery is unaffected. It is **confirmed for the raw
statistic**, which independently corroborates §5.2's account of why the kill was right: a
parse asymmetry moves `cond − iid` toward zero, measured here in a cell nobody chose for the
purpose.

**One consequence for the successor, stated as design input and NOT as a result.** Applying
the same predictor to Phase 21's StarCoder2 arm (gap 5.66pp, i.i.d. 0.2567) gives ≈**0.014**
of upward bias, i.e. a corrected shift near **−0.036** rather than the −0.0217 observed. **This
is not an adjudication and must never be cited as one** — it is an uninstrumented arm run
through a two-point extrapolation. Its only legitimate use is **powering the successor**: if
StarCoder2's true effect is ≈−0.036 rather than the −0.021 the intercept table predicted, then
the MDE needed is ≈0.036, which **n = 56 already achieves**. §0.4's note that separating
StarCoder2 would need n ≈ 155 and was therefore "unresolvable in this instrument" was computed
against the wrong target effect. **The cell is feasible — the instrument, not the power, is
what has to be fixed.**

---
