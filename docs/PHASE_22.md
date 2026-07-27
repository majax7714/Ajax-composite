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

## 2.1 Pre-spend addendum — the diagnostic answered itself by code inspection

*Appended while building the entrypoint, **before any Phase-22 generation ran**. Recorded now
so it cannot later be mistaken for a post-result rationalisation.*

§2 pre-registered a two-way decision on whether StarCoder2's empty completions were a **model**
failure or an **extraction** failure. Reading `h1_gen_lcb` settles it without spending:

- the prompt already **ends with an opening ` ```python ` fence**, and
- sampling stops at `"```"`, and
- `code = o.text.strip() or None`.

**There is no fence-searching extraction step that could fail.** `code` *is* the raw generated
text. An empty code therefore means the model emitted nothing — or immediately closed the
fence — before the stop token. **Branch (i) of §2's decision (extraction fallback) cannot
fire, and is dead.** The live reading is branch (ii): the empties are genuine model behaviour,
and StarCoder2 is heading for a **void cell / outside-the-instrument's-domain** verdict unless
the fresh seed changes its behaviour materially, which nothing predicts it will.

**Consequence for the frozen odds, stated and NOT acted on.** This makes branch **E** —
StarCoder2 void, DeepSeek adjudicates — mechanically more likely than the 15% it was priced
at, probably substantially. **The odds are not being re-priced**: they were frozen, the
information arrived after the freeze, and quietly re-pricing a pre-registration on new
reasoning is how pre-registrations stop meaning anything. This is recorded instead as a
**miss in the charter's own design analysis** — the code path was available to read before the
odds were written, and was not read — to be scored as such at close.

**What the phase still buys at $2.12,** with E as the likely outcome: a fresh-seed, clean-
instrument adjudication of **DeepSeek against both Qwen models** — which is the core of the
question (*is DeepSeek exceptional?*). StarCoder2 was always the weaker leg. And a model
declared out of domain is a result, not a gap: Phase 18 set that precedent for T > 1.0.

The entrypoint retains the `emit_meta` diagnostic anyway — per-candidate `finish_reason`,
`stop_reason` and token counts — because it converts "the model emitted nothing" from an
inference into a measurement, at zero marginal cost.

---

## 3. Pre-registration freeze

Frozen at commit `ace9984`, **before** any Phase-22 generation ran. Entrypoint at the commit
below, also before spend. §2.1 appended pre-spend.

---

## 4. Step-9a search plan — *committed with this charter, before any result*

| if the branch is | queries | a hit that would change the reading |
|---|---|---|
| **A** | "conditioning degradation base code models across families"; "in-context partial solution harms code generation small models" | a family-general **inference-time** result would make this a replication rather than a finding; retraining results (§1c) do **not** count |
| **C** | "deepseek-coder pretraining fill-in-the-middle repository-level objective robustness"; "why is deepseek-coder robust to partial code context" | a documented pretraining-objective account would make this phase's result a *prediction of known architecture*, not a discovery |
| **E** | "base model empty generation rate unconditioned prompt code benchmark" | prior documentation of StarCoder2-class models failing to emit code unconditioned would turn our instrument note into a known limitation with a citation |

**Every branch:** re-check Huang et al.; re-check the DeepSeek-infilling tension in §1(b)
against whatever is found; and record what the search **failed** to find.

---

## 5. RESULT — **BRANCH E: PARTIAL.** StarCoder2 void; DeepSeek "clean" by 0.0008, and the reading is not the one the charter favoured

*Closed 2026-07-27. Raw artifact `artifacts/h22_fourway.json` committed **unread** at `08bef20`.
Independent verifier (`scripts/j22_verify.py`, committed `adca663` before any result existed)
agrees on **every quantity and on the branch**.*

### 5.1 Gates

| gate | value | verdict |
|---|---|---|
| n ≥ 30 | **n = 56** | passes |
| **instrument validation** — Coder-1.5B reproduces −0.048 within ±0.040 | **−0.0450** | **passes** |
| per-cell OFF-TARGET (all abs(Δ_art) ≤ 0.020) | −0.0060 / −0.0045 / −0.0033 / −0.0023 | passes |
| per-cell parse ≥0.95 and gap ≤2.0pp | **StarCoder2: 0.9167, gap +5.51pp** | **VOIDS THAT CELL ONLY** |

**The per-cell correction (§8 entry 13) did its job.** In Phase 21 the identical StarCoder2
failure voided the entire phase. Here it voids one cell and three cells adjudicate. That is
the whole content of the ledger entry, working.

### 5.2 Cells

| model | i.i.d. | cond | cond−iid [CI95] | cond−art [CI95] | below both nulls | parse i/c | gap | pred | hit |
|---|---|---|---|---|---|---|---|---|---|
| Coder-1.5B | 0.3314 | 0.2864 | **−0.0450** [−0.0716,−0.0185] | −0.0377 [−0.0560,−0.0183] | **true** | .9896/.9940 | +0.45pp | −0.048 | ✓ |
| general-Qwen-1.5B | 0.2838 | 0.2449 | **−0.0388** [−0.0606,−0.0184] | −0.0240 [−0.0431,−0.0069] | **true** | .9844/.9836 | −0.07pp | −0.037 | ✓ |
| DeepSeek-1.3B | 0.2600 | 0.2398 | **−0.0201** [−0.0437,**+0.0008**] | −0.0124 [−0.0215,−0.0041] | false | .9851/.9955 | +1.04pp | +0.011 | **✗ MISS** |
| StarCoder2-3B | 0.2549 | 0.2122 | −0.0427 [−0.0760,−0.0051] | −0.0322 [−0.0607,+0.0056] | false | **.9167/.9717** | **+5.51pp** | −0.036 | ✓ (VOID) |

### 5.3 DeepSeek is "clean" by one part in twelve hundred, and three things say don't lean on it

Branch C — *DeepSeek is the exception* — was the charter's favourite at **55%**. **It did not
fire**, and the reason is worth stating precisely rather than rounding off:

1. **The margin is 0.0008.** DeepSeek fails `below_both_nulls` only because its cond−iid
   interval's upper end sits at **+0.0008**. One part in ~1250 the other way and this phase
   reads as branch A.
2. **It IS below the copy null.** cond−artifact = **−0.0124, CI [−0.0215,−0.0041]**, which
   **excludes zero**. DeepSeek fails the conjunction on the i.i.d. leg alone; against the
   artifact it is unambiguously down.
3. **The pre-registered secondary scoring flips it.** Under parse-only scoring — committed in
   §2 *before* the run, for every model, precisely so this could not be a post-hoc choice —
   DeepSeek reads **−0.0223, CI [−0.0454, −0.0006]**, which **excludes zero**. Combined with
   (2), under parse-only scoring **DeepSeek is below both nulls, i.e. it sinks.**

**And the null is uninformative anyway.** The symmetric guard fires: CI reaches **−0.0437**,
past the pre-registered MDE of 0.039. A verdict of "clean" here is **not evidence of absence**;
the data is consistent with a −0.04 effect.

**Verdict, stated at the strength the evidence supports:** the frozen rule returns *clean*, and
the frozen rule is what governs. But "DeepSeek is exceptional" is now a **much weaker claim
than before this phase**, resting on a 0.0008 margin, one scoring convention out of two
pre-registered, and an interval that cannot exclude the effect it is being used to deny.

### 5.4 A falsified prediction — the intercept table's first miss

**Predicted +0.011 for DeepSeek; measured −0.0201, CI [−0.0437,+0.0008].** The interval does
**not** contain the prediction. Three of four predictions hit (Coder −0.048/−0.0450; general
−0.037/−0.0388; StarCoder2 −0.036/−0.0427, on a void cell and so excluded from the accounting);
DeepSeek misses.

**The cause was on the page in advance.** §0.4 already recorded that DeepSeek's intercept was
an **extrapolation**: its Phase-7 cell sat at Δ_art **+0.0499**, well off match, so the
intercept was projected to a gap of zero the cell never occupied. The one intercept derived
furthest from its cell's own centre is the one that failed. That is the predicted failure mode
of the method failing exactly where predicted — which supports the compression law's *slope*
while marking its *intercept* as unreliable under extrapolation.

### 5.5 StarCoder2 is outside this instrument's domain — now a measurement, and a known limitation

`emit_meta` converts Phase 21's inference into evidence. In the i.i.d. arm: **13 raw-empty
generations** and — the real finding — **36 candidates stopped at `"\nProblem:"`**, against 11
in the conditioned arm. StarCoder2 given a bare problem statement does not fail to write code
so much as **wander off and begin inventing a new problem**. Given an artifact, it complies.

**Step 9a fired its branch-E hit condition.** The pre-registered query returned prior
documentation of exactly this, so our instrument note is **not a novel observation — it is a
known limitation with a citation**:

- StarCoder2 base models *"perform very poorly when given an instruction prompt, which
  motivates using a different prompt format"* ([StarCoder2 and The Stack v2](https://arxiv.org/pdf/2402.19173));
  for the base model *"one-third of the code generated is incomplete."*
- StarCoder produces *"effectively empty solutions, e.g. `pass` or a comment 'Insert code
  here'"* on HumanEval ([StarCoder](https://arxiv.org/pdf/2305.06161)) — noted there as
  occurring in **every model evaluated**, which is why the *differential* rather than the level
  is the right gate (§8 entry 13).

*Snippet-level, not source-verified.* **Consequence:** the honest statement is that this record
applied a prompt format the StarCoder2 authors document as unsuitable for their base model.
StarCoder2 is not evidence about the sink; it is evidence about the harness. Removing it from
the family question is now a **cited** decision rather than a convenient one.

### 5.6 Exploratory — conditioning collapses generation diversity, and DeepSeek collapses hardest

*Not pre-registered. Fell out of the verifier's fresh-draw check. Exploratory per §10 — it
moves no claim.*

The fresh-draw check compared seed 367 and seed 401 candidate strings per model/arm/problem,
to confirm the re-run is a genuinely independent draw. It is, for the unconditioned arms. But
the **conditioned** arms tell a second story:

| model | i.i.d. identical | **cond identical** | ratio |
|---|---|---|---|
| Coder-1.5B | 0.15% | **3.27%** | 22× |
| general-Qwen-1.5B | 0.15% | **6.40%** | 43× |
| StarCoder2-3B | 0.00% | **13.76%** | — |
| DeepSeek-1.3B | 0.15% | **29.02%** | **195×** |

Two independent seeds agree on the *exact string* 0.15% of the time unconditioned, and up to
**29%** of the time once an artifact is in the prompt. **Showing a model an artifact collapses
its output entropy by up to two orders of magnitude.** This is the compression phenomenon in a
currency the record has never used — string identity rather than pass-rate — and it came free.

**And it inverts the natural reading of DeepSeek.** DeepSeek shows the *highest* copy-identity
(29%) and the *smallest* distance below the artifact null (cond−art −0.0124, against −0.0377,
−0.0240, −0.0322 for the others). Those two facts fit one account: **DeepSeek does not resist
the artifact — it copies it more completely**, converging toward the artifact's score instead
of degrading past it. On that reading "DeepSeek is clean" would mean *more* captured by the
conditioning, not less. That is the opposite interpretation of the same data, it is a
**hypothesis and not a measurement**, and the cheap test is direct: measure per-candidate edit
distance to the artifact across families at match.

### 5.7 Fresh-draw premise — verified, and a caveat the verifier's own label got wrong

The premise holds where it matters: unconditioned arms are **0.00–0.15% identical** across
seeds, so this is an independent draw and not a re-score. Conditioned arms are correlated by
the mechanism under study (§5.6), which is a finding rather than a defect — but it does mean
**the conditioned arms are less independent between Phases 21 and 22 than the i.i.d. arms**,
and any future comparison of the two phases must say so.

*A correction to my own tooling.* The verifier prints `mismatch -> extraction, not the model`
for StarCoder2's conditioned arm (empty codes 0.0074, raw-empty 0.0000). **That label is
wrong.** The gap is whitespace-only output — `code = o.text.strip() or None`, so text that is
non-empty but all whitespace becomes an empty candidate. That is still the model, not the
extractor. The check is right; its message is misleading and is recorded here rather than
silently edited.

### 5.8 Cost — measured, and the streak restored

**Cost $2.0621** — MTD **$89.7364 → $91.7985**, snapshot taken **in the launching shell before
the run**, which is §8 entry 14's practice fix now operating rather than merely written down.
Against a pre-registered **$1.70–2.90** with a $2.12 central estimate: **inside the band, 2.7%
under central.** MTD $91.80 against Amendment 6's $130 report / $200 hard stop.

### 5.9 Scoring the charter's own calibration

- **Branch odds: badly wrong, and flagged as contaminated in advance.** C was priced 55% and
  did not fire; E was priced 15% and did. §2.1 — written pre-spend — said E was mechanically
  likelier than its frozen price and declined to re-price it. So the miss is recorded twice:
  once as the odds being wrong, once as the design analysis that should have caught it before
  the odds were written.
- **Point predictions: 3 of 4 hit** (one void-excluded), with the miss falling on the single
  intercept derived by extrapolation — the failure mode §0.4 had already named.
- **The instrument-validation gate passed**, so the phase's numbers sit on an instrument that
  demonstrably reproduces a known cell.

### 5.10 What this settles

**Settles:** the per-cell criterion works (§5.1); StarCoder2 is outside the harness's domain,
with citations (§5.5); the compression law's slope survives while its intercept is unreliable
under extrapolation (§5.4).

**Does not settle:** whether DeepSeek is exceptional. The frozen rule says clean; the margin is
0.0008, the pre-registered alternate scoring says *sink*, and the interval cannot exclude −0.04.
**The family question is now genuinely open in a way it was not before** — the "Qwen-base"
shape that survived Phase 20 rested on DeepSeek being clean, and DeepSeek is now clean only in
the most technical sense available.

**Successor.** Two candidates, and the second is cheaper and better. (i) Power DeepSeek
properly: at MDE ≈0.020 it needs n ≈ 200, i.e. a larger donor pool — expensive, and it answers
one question. (ii) **Test the §5.6 hypothesis directly:** measure per-candidate edit distance
to the artifact across all four models at match, on committed data, at **$0**. If DeepSeek's
apparent cleanliness is more faithful copying rather than more resistance, that reframes the
family question instead of merely re-powering it — and the data to check it is already on disk.

---

## 6. P0 RESULT ($0) — the family difference in *sinking* may be a family difference in *copying*

*Exploratory per §10; moves no claim. Script and both competing predictions committed at
`6b6cb57` **before** it ran. Artifact `artifacts/h22_p0_editdist.json`.*

Per problem, line-level similarity between each candidate and that model's own selected
artifact, both arms. The i.i.d. arm is the baseline — what the model writes without having
seen the artifact. **PULL = (sim_cond − sim_iid) / (1 − sim_iid)**: the fraction of available
string distance that conditioning closes. The compression law's *b*, in string space.

| model | sim i.i.d. | sim cond | **PULL** | cond−art (§5.2) |
|---|---|---|---|---|
| Coder-1.5B | 0.1359 | 0.4936 | **+0.418 ± 0.030** | −0.0377 |
| general-Qwen-1.5B | 0.1386 | 0.5154 | **+0.435 ± 0.035** | −0.0240 |
| **DeepSeek-1.3B** | 0.1177 | **0.7882** | **+0.764 ± 0.019** | **−0.0124** |
| StarCoder2-3B *(void)* | 0.0940 | 0.6533 | +0.623 ± 0.021 | −0.0322 |

**The prediction that came from the incidental observation won outright.** PULL reproduces the
**copy-identity ordering exactly** — Spearman **+1.000** — and correlates with the committed
compression slopes at **+0.600**, clearing the pre-registered ≥ +0.5. P3 holds: every PULL is
positive and both non-Qwen models exceed both Qwen models.

**DeepSeek copies nearly twice as hard as its Coder counterpart.** +0.764 vs +0.418, a gap of
**+0.346 ≈ 9.7 SE**. Its conditioned output is **79% line-similar to the artifact it was
shown**; Coder-1.5B's is 49%.

### 6.1 Why this reframes the whole family question

The sink criterion requires a model to fall below **both** nulls — its own i.i.d. *and* the
artifact. **A model that copies the artifact faithfully lands AT the artifact**, so its
cond−artifact distance goes to zero and it cannot be "below both" almost by construction.

Among the three non-void cells the relationship is monotone with no exceptions: PULL 0.418 /
0.435 / 0.764 against cond−art −0.0377 / −0.0240 / −0.0124. **The harder a model copies, the
less it sinks** — and DeepSeek, the record's one persistently "clean" family, is the hardest
copier in the set by a wide margin.

So the live hypothesis is no longer *"DeepSeek resists the pathology."* It is:

> **DeepSeek is not resisting the artifact — it is copying it. Its "clean" verdict is a
> consequence of copying fidelity, not of robustness.**

That is the **opposite** reading of the same data, and it dissolves the family question rather
than answering it: "which families sink" may have been measuring "which families copy," a
property with no obvious bearing on reasoning degradation at all.

### 6.2 What would kill this, stated now

The account is coherent, large, and **exploratory on n = 3–4 models**. It is a correlation
across four points measured on one set of runs, and four points can be ordered by many things.
It does not establish that copying *causes* the clean verdict. Two cheap tests would move it:

1. **Within-model, across problems.** If the account is right, problems where a model copies
   harder should be problems where it sinks less — a per-problem correlation inside each cell,
   available on committed data at **$0**. A null there would be strong evidence against.
2. **Force the copy.** Condition on an artifact while instructing divergence, or vary artifact
   quality: if cleanliness tracks copying rather than family, a high-copy Qwen cell should look
   as clean as DeepSeek.

Until at least (1) runs, this is the most interesting thing on the page and it is **not a
finding.**

### 6.3 A note on the generation-template hash

`gen_template_hash` moved from `1e43a51cdc2cc3b5` (Phase 21) to `808966428bb668ad` (Phase 22).
**The prompt and sampling parameters are byte-identical** — verified by diff: the only changes
to `h1_gen_lcb` are the `emit_meta` parameter, a comment, and the metadata return branch. The
hash covers the function source, so it moved for a reason unrelated to what the model sees.
Recorded because a future reader comparing two hashes would otherwise be right to suspect an
undocumented instrument change, and this record's whole defence against silent drift is that
such things are written down rather than noticed later.

---

## 7. P1 RESULT ($0) — the killing test does NOT support §6, and my own threshold was mis-specified

*Exploratory per §10. Script and predictions committed at the previous commit, before running.
Artifact `artifacts/h22_p1_copysplit.json`.*

Each model's 56 problems split at its own median conditioned-similarity; `shift = a + b·gap`
fitted separately on each half.

| model | median sim | intercept HIGH-copy | intercept LOW-copy | closer to 0? | slope H / L |
|---|---|---|---|---|---|
| Coder-1.5B | 0.4989 | −0.0370 | −0.0459 | ✓ (Δ 0.0089) | 0.879 / 0.573 |
| general-Qwen-1.5B | 0.5139 | **−0.0435** | **−0.0147** | **✗ reversed** (Δ −0.0288) | 0.662 / 0.639 |
| DeepSeek-1.3B | 0.8100 | −0.0120 | −0.0123 | ✓ **(Δ 0.0003)** | 1.061 / 0.924 |
| StarCoder2-3B *(VOID)* | 0.6709 | −0.0281 | −0.0495 | ✓ (Δ 0.0214) | 0.806 / 0.384 |

**The script prints "SUPPORTS §6" at 3/4. That verdict is wrong, and the fault is in the
prediction I wrote.** Q1's threshold was "at least 3 of **4** models" — but this phase's own
frozen rule voids StarCoder2's cell, and a void cell must not count toward adjudication. I
wrote a threshold over four models while one was **already known to be void**. Read under the
phase's own rule the live count is **2 of 3**, which does not meet the bar. Logged as **§8
entry 15**.

**And the 2 of 3 does not survive inspection either.** DeepSeek's difference is **0.0003** —
its intercept is flat across the split, i.e. within the model that the entire copying account
is *about*, copying harder does **not** reduce sinking. General-Qwen runs **backwards** by
0.0288, the largest live magnitude in the table. Only Coder-1.5B shows the predicted effect
with a real magnitude.

**Q3 fires.** The pre-registered null reading applies: string similarity and pass-rate
degradation behave as **largely independent axes** that happen to order four models alike.

### 7.1 What survives, and what I am withdrawing

**Withdrawn:** §6.1's proposed mechanism — *"a model's cleanliness is produced by its copying
fidelity"* — as a per-problem mechanism. Its own designed test does not support it, and the
model it was invented to explain shows no gradient at all.

**Survives, and is still unexplained:**

- **The between-model correlation is real and large.** PULL orders the models exactly as
  copy-identity does (ρ +1.000) and DeepSeek copies nearly twice as hard as Coder-1.5B
  (+0.764 vs +0.418, ≈9.7 SE). That is not noise — but it is four points, and Q1 now says it
  is not mediated problem-by-problem, so it may be a family-level coincidence or a property
  operating at a level this design cannot see.
- **Conditioning collapses output entropy** (§5.6): 0.15% → up to 29% seed-to-seed string
  identity. Untouched by this result.
- **DeepSeek's slope at true match is ≈1.0** (1.061 high-copy / 0.924 low-copy), far above the
  0.784 the committed battery carries from a cell at Δ_art +0.0499. A model with b ≈ 1 lands
  *on* the artifact, which is a cleaner statement of what makes it look clean than the
  mechanism I withdrew — and it is a **measurement**, not an inference. It also corroborates
  §5.4: the battery's DeepSeek row is unreliable because it was extrapolated.

**Time from hypothesis to withdrawal: under an hour, at $0.** The account was the most
interesting thing on the page, I designed the test that could kill it and stated the null
reading in advance, and it fired. That is the practice working, and it is worth more than the
hypothesis was.

### 7.2 Write-up surfaces — Amendment 4a compliance

| # | surface | disposition |
|---|---|---|
| 1 | phase doc RESULT | **updated** — §5, §6, §7 |
| 2 | §9.x addendum | **deliberately unchanged** — no claim status moved; the durable content is methodological and landed in §8 entry 15 and §0.4 |
| 3 | §0 index rows | **deliberately unchanged** — branch E adjudicates no status change; DeepSeek's verdict is weakened, not reversed |
| 4 | §0.3 evidence rows | **updated** — rows 8 and 11 carry the P22 marker, including that no claim may rest on DeepSeek being clean |
| 5 | §0.4 open successors | **updated** — three new items, one of them now the top open item |
| 6 | living-record line | **updated** — Phase 22 banner |
| 7 | abstract banner chain | **deliberately unchanged** — no claim status moved. Recorded so the skip is visible |
| 8 | `README.md` | **updated** — row 22 and the status block |
| 9 | §8 ledger entry | **updated** — entry **15** (threshold counted a voided cell) |

---

## 8. P2 RESULT ($0) — the copying account is dead, and the four-point correlation was a coincidence

*Exploratory per §10. Script and predictions committed before running. Artifact
`artifacts/h22_p2_pullladder.json`.*

| cell | sim i.i.d. | sim cond | **PULL** | n | cond−art | status |
|---|---|---|---|---|---|---|
| P11 Coder-1.5B | 0.1323 | 0.5668 | **+0.506 ± 0.035** | 44 | −0.052 | SINKS |
| P11 Coder-3B | 0.1476 | 0.6281 | **+0.564 ± 0.036** | 39 | −0.051 | SINKS |
| **R5 Coder-7B** | 0.1540 | 0.4977 | **+0.408 ± 0.041** | 29 | −0.008 | **CLEAN** |
| P11 general-Qwen-1.5B | 0.1180 | 0.5557 | +0.502 ± 0.037 | 54 | −0.019 | |
| C3 phi-1 | 0.0800 | 0.2286 | **+0.163 ± 0.027** | 47 | −0.042 | sub-threshold sink |
| P22 Coder-1.5B | 0.1359 | 0.4936 | +0.418 ± 0.030 | 56 | −0.038 | SINKS |
| P22 general-Qwen-1.5B | 0.1386 | 0.5154 | +0.435 ± 0.035 | 56 | −0.024 | SINKS |
| P22 DeepSeek-1.3B | 0.1177 | 0.7882 | **+0.764 ± 0.019** | 56 | −0.012 | clean by 0.0008 |
| P22 StarCoder2-3B *(void)* | 0.0940 | 0.6533 | +0.623 ± 0.021 | 56 | −0.032 | VOID |

### 8.1 R1 fails inside the family, in the wrong direction

**Coder-7B is the clean rung, and it copies LEAST of the three.**

> Coder-1.5B **+0.506** (sinks) · Coder-3B **+0.564** (sinks) · **Coder-7B +0.408 (clean)**

Same family, same continued-pretraining diet, same prompt, same harness — the only clean rung
copies **less** than both sinking rungs. The copying account predicts the opposite, and family
cannot absorb the result because there is no family difference here.

**phi-1 makes the same point from the other end:** the *lowest* PULL in the record (+0.163,
less than a quarter of DeepSeek's) and it still sinks, sub-threshold, at −0.042. Weak copying
with degradation; strong copying without it. The two axes come apart in both directions.

### 8.2 R2 — the +1.000 correlation does not survive contact with more cells

Over the four Phase-22 cells, PULL ordered the models **exactly** as copy-identity did
(ρ +1.000) and tracked the committed compression slopes at +0.600. Over **eight** cells,
Spearman(PULL, cond−artifact) = **−0.119** — no relationship, and if anything the wrong sign.

**§7's Q3 said this in advance:** *"similarity and degradation behave as largely independent
axes that happen to order four models alike."* Four points can be ordered by many things. This
is what it looks like when a beautiful correlation is a small-n coincidence, and the record
now has it measured rather than argued.

### 8.3 What survives, and it is not nothing

**R3 holds in every cell: PULL is positive everywhere, from +0.163 to +0.764.** Across eight
cells, five model families and 0.5B–7B, **conditioning always drags output toward the artifact
in string space** — models rewrite from ~0.08–0.15 similarity to ~0.23–0.79. That is the
compression law's phenomenon in a currency the record had never used, and it is **universal**,
exactly as the pass-rate version is.

**What is now established is a dissociation:**

> **Conditioning pulls every model toward the artifact in string space, and how hard it pulls
> does not predict whether the model degrades.** String-space copying and pass-rate
> degradation are separate axes.

That is a real finding, it is negative in the useful sense, and it closes §0.4's "why does
copying order the models" item with *it doesn't — n was 4*.

### 8.4 Consequence for the family question

DeepSeek's PULL is the highest measured (+0.764) and Coder-3B at +0.564 sinks hard. So
**DeepSeek's near-clean verdict cannot be attributed to copying fidelity** — the explanation
offered in §6.1, tested in §7, and now buried in §8. DeepSeek's status stays exactly where
§5.3 left it: clean by 0.0008, below the copy null, flipped by the pre-registered alternate
scoring, and uninformative at the pre-registered MDE. **The record has no mechanism for it,
and now has one fewer candidate than it did this morning.**
