# Phase 19 — the architecture twin at true match: is the DIET attribution position-confounded?

*Charter opened 2026-07-26. Tenth iteration of the unattended loop ([AUTONOMOUS_LOOP.md],
Amendments 1–4a). Selected by full-record review, not as Phase 18's sequel. Append-only;
pre-registration frozen before spend.*

---

## 0. How this question arose

Phase 18's free work produced the **compression law**: every model, sinking or clean, is
pulled **47–90%** of the way from its own quality toward the artifact it is shown
(R² to 0.92, eight committed cells). Nothing in that law is about the sink — it was carried
as a descriptive regularity.

But it has a consequence nobody had drawn. If a cell's shift depends on its **position**
(Δ_art = artifact frac − own i.i.d.) at a coefficient of 0.5–0.9, then **any comparison
between cells at different positions is confounded at that rate** — and the record's
central causal claim is exactly such a comparison.

So the state read for this phase asked a question the record has never asked in this form:
*are the cells being compared at the same position?* They are not.

---

## 1. P0 — free, landed and committed before this charter (`scripts/j19_p0_position_audit.py`,
`h19_p0_position_audit.json`)

### 1.1 Phase 7's family battery is position-confounded

| cell | group | phase | instrument | Δ_art | verdict |
|---|---|---|---|---|---|
| Coder-1.5B | Coder | P11 | **k=24 powered** | +0.0016 | SINK |
| Coder-3B | Coder | P11 | **k=24 powered** | −0.0005 | SINK |
| Coder-7B (R5) | Coder | P10 | **k=24 powered** | +0.0023 | clean |
| Coder-7B (M4) | Coder | P7 | k=8 | **−0.0393** | SINK *(later retracted)* |
| Coder-0.5B | Coder | P7 | k=8 | **+0.0814** | clean |
| DeepSeek-1.3B | non-Coder | P7 | k=8 | **+0.0499** | clean |
| **general-Qwen-1.5B (TWIN)** | non-Coder | P7 | k=8 | **+0.0642** | clean |
| StarCoder2-3B | non-Coder | P7 | k=8 | **+0.0326** | clean |

**Within Phase 7's own battery, sink status separates perfectly on *position* as well as on
diet.** Every cell that did not sink sits at **positive** Δ_art (+0.033 to +0.081); the one
that did sits at **negative** Δ_art (−0.039).

Quantified at the cells' own measured compression slopes (mean 0.761 over the non-Coder
cells): the +0.0882 position difference buys those cells **+0.0672 of shift** — **1.3× the
≈ −0.05 effect it is being used to attribute to diet.**

There is a second asymmetry in the same table: **all three powered-instrument cells are
Coder cells.** The non-Coder side of the family contrast has *never* been measured with the
k=24 instrument that Phase 10 R3 built after finding the k=8 instrument's SE was 0.028 —
larger than the effect. The record compares **powered at-match Coder cells** against
**unpowered off-match non-Coder cells** and concludes "diet."

### 1.2 Position-adjusted, the group difference shrinks by about a third

Each cell's fitted shift **at gap = 0** (its compression intercept):

| | intercept | CI95 | excludes 0 |
|---|---|---|---|
| Coder-1.5B | −0.0564 | [−0.089, −0.022] | yes |
| Coder-3B | −0.0577 | [−0.095, −0.020] | yes |
| Coder-0.5B | −0.0293 | [−0.052, −0.009] | yes |
| DeepSeek-1.3B | +0.0105 | [−0.015, +0.033] | no |
| **general-Qwen-1.5B (TWIN)** | **−0.0398** | **[−0.079, −0.002]** | **yes** |
| StarCoder2-3B | −0.0208 | [−0.067, +0.022] | no |

Coder ≤3B mean **−0.0478**, non-Coder mean **−0.0167**, difference **−0.0311** — against the
−0.05 to −0.10 the record reports for the raw contrast.

**And the twin is the anomaly.** general-Qwen-1.5B is adjudicated **clean**, yet its
intercept excludes zero and sits *inside* the Coder range. Its cell sat at Δ_art +0.0642,
where its own compression (0.619 × 0.0642 = **+0.0397**) almost exactly cancels an intercept
of **−0.0398** — producing the observed shift of **−0.0001**. Its "no sink" verdict is,
arithmetically, a cancellation.

### 1.3 ✅ Checked, not assumed: **the DIET claim does not rest on Phase 7**

Before treating §1.1 as damaging, the claim's strongest support was audited. Phase 9's
**generated 2×2** — the provenance control — is **position-matched**:

| cell | | n | Δ_art | cond − iid |
|---|---|---|---|---|
| G1a | DeepSeek self | 19 | −0.0652 | −0.0621 |
| G1b | DeepSeek foreign | 19 | −0.0564 | −0.0607 |
| G1c | Coder self | 10 | −0.0444 | **−0.1999** |
| G1d | Coder foreign | 10 | −0.0449 | **−0.2381** |

All four within **0.021** of each other, and the residual difference (+0.0161, worth ≈+0.011
of shift) **favours the Coder arms — the ones that sink harder.** The confound runs
*against* Phase 9's conclusion, making it **conservative**.

> **So the DIET attribution stands.** It stands on Phase 9's 2×2, not on Phase 7's battery.
> What §1.1 damages is the **family-contrast evidence in §0.3 rows 8/11 and the §0.2
> extraction spec**, which cite Phase 7's "non-Coder families show no sink at match" as if
> it were position-controlled. It is less controlled than presented, and that caveat is owed
> to the record whatever this phase returns.

---

## 2. The question

> **Does the architecture twin — `Qwen2.5-1.5B`, same base, verified same 28L × 12H, same
> scale as `Qwen2.5-Coder-1.5B`, differing only in the Coder continued-pretraining stage —
> sink when measured at TRUE match with the powered instrument, exactly as its Coder sibling
> was in Phase 11?**

**Why this cell and not another.** It is the *only* measurement that puts the two sides of
the record's central causal claim on the same footing: same donor pool, same targeting
instrument, same selector, same seeds, same adjudication code — differing in one variable,
which is the variable the claim names. Phase 15 established that this pair is the
load-bearing control when a cross-model quantity is claimed to track a behavioural property;
it has since been decisive twice (retiring the concentration finding in P15, refuting the
loop's own intercept hypothesis in P18 §P0.5).

It is also a **committed out-of-sample test of the compression law's intercept**. At
Δ_art ≈ 0 the compression term vanishes, so the cell measures the intercept *directly* —
the quantity §1.2 could only reach by extrapolating from +0.064.

**Two predictions, ~0.04 apart, and the cell distinguishes them:**

- the **compression law** predicts **−0.0398**, CI95 [−0.0790, −0.0021] — the twin sinks;
- the **DIET claim** predicts **≈ 0.000** — a non-Coder model is clean at match;
- for calibration, the Coder sibling measured **−0.052** (P11, n = 44).

---

## 3. Design

**Maximal parallelism is the design.** `j11_ladder` is already fully parameterised by rung,
so the twin is added to `P11_MODELS` and run through the **byte-identical code path** that
produced the Coder rungs — same donor pool (`_r3_donor_pool`, 80 problems), same selector
(`_r3_select`), same **sweep seed 151** and **cell seed 173**, same k=24 powered targeting,
same k=8 cell arms, same `_matched_cell`, same adjudication block. Reusing the seeds is
deliberate: the models differ, so the generations differ regardless, and holding the seeds
fixed removes one more difference between the twin and its sibling.

- **Model:** `Qwen/Qwen2.5-1.5B`, revision `8faed761d45a263340a0528343f099c05c9a4323`
  (the revision already pinned in `J7_MODELS`/`P15_MODELS` — the same weights Phase 7 and
  Phase 15 measured).
- **Step 1:** k=24 i.i.d. sweep over the 80 donor problems → the powered map (SE 0.011).
- **Step 2:** targeting grid; choose the band with |pred Δ_art| ≤ 0.010 at n ≥ 30.
- **Step 3:** the matched cell, both arms at k=8, cell seed 173.

**Generations:** 80 × 24 = 1920 (sweep) + 2 × n × 8 (cell) ≈ **2400–2640**.

### Frozen decision rules

**Primary statistic — the sibling comparison, not a threshold call.** The twin's
`cond − iid` is compared against the Coder sibling's **committed CI95 [−0.1258, −0.0028]**
(P11 `h11_coder1p5b.json`) and against zero, with a bootstrap CI over problems:

- **TWIN SINKS** ⟺ the twin's cond − iid CI95 **excludes zero** on the negative side.
- **TWIN CLEAN** ⟺ that CI **includes zero**.
- **INDISTINGUISHABLE FROM THE SIBLING** ⟺ the twin's point estimate lies **inside**
  [−0.1258, −0.0028].

*(These are deliberately separable: a twin could sink and still be far shallower than the
sibling, which is a different result from either "clean" or "same as Coder.")*

**Inherited round number, declared rather than silently used.** `j11_ladder`'s verdict
string uses `resid ≤ −0.05` — a round number of exactly the kind §8 entry 9 forbids. It is
**kept for the sibling comparison** (the Coder rungs were adjudicated by it, and changing it
would break the parallelism this phase exists for) and reported as
`verdict_legacy_p11_rule`, **but it does not adjudicate.** The CI-referenced rules above do.
The sibling cleared it at −0.0522, i.e. by 0.0022, which is itself the demonstration.

### Kill criteria — *evaluated inside the branch expression, per §8 entry 11*

Phase 18 computed its kill criteria, printed them, and let its branch tree ignore them. The
entrypoint here evaluates every criterion in the same expression that selects the branch.

- **Targeting infeasible** (no band with |pred Δ_art| ≤ 0.010 at n ≥ 30) → **branch D**, no
  retune.
- **Achieved powered Δ_art outside ±0.020** → OFF-TARGET; no adjudication. *(P11's own
  `P11_ON_TARGET`, reused for parallelism; it is 1.8× the powered instrument's measured
  SE of 0.011 — derived from spread, not chosen round.)*
- **n < 30** → underpowered; no adjudication.
- **Parse rate < 0.95 on either arm** → instrument failure (the Phase 18 lesson).

### Branches, with odds committed before the run

| | branch | reading | odds |
|---|---|---|---|
| **A** | **TWIN CLEAN** at true match | the DIET attribution finally rests on symmetric evidence — a powered at-match non-Coder cell. §1.1's confound is real but did not change the answer. The compression intercept is refuted as a predictor, consistent with P0.5's own finding that it is not a diet signature | **45%** |
| **B** | **TWIN SINKS** at true match | the family contrast in rows 8/11 was doing work that **position** was doing. The diet claim survives on Phase 9's 2×2 but its *scope* narrows sharply — "non-Coder families do not sink at match" becomes false as stated. The compression law's intercept is validated out-of-sample | **40%** |
| **C** | sinks on cond − iid but **fails the copy null** | ambiguous; at Δ_art ≈ 0 the two nulls nearly coincide, so this needs the achieved position to interpret | **5%** |
| **D** | **targeting infeasible** at n ≥ 30 | the twin cannot be placed at its own straddle by mining — the same wall the 0.5B rung hit (§0.4) | **10%** |

A is the narrow favourite because the diet claim has independent, position-matched support
(§1.3) and because the twin's intercept is the *weakest* kind of estimate — an extrapolation
to gap = 0 from a cell centred at +0.064, exactly the caveat §0.1 records. B is priced
almost level because that intercept is nonetheless a real measurement whose CI excludes
zero, and because the twin is the most negative of the three non-Coder cells.

**This phase can damage a LIVE claim's scope.** Per §3 of the loop spec that is a reason to
run it, not to avoid it: evidence that pressures a live claim is promoted to a named
hypothesis and given a discriminating cell. It is **not** a 1:1 refutation — §1.3 verified
that Phase 9 carries the attribution independently — so the loop proceeds rather than halts.

### Cost

**Estimate $0.30–0.70.** Basis: Phase 17 ran 3984 generations of a 1.5B-class model on the
same judge for a read **$0.551**; this is ~2500, i.e. ~0.63×, giving ≈$0.35 central with the
band widened for the sweep's longer i.i.d. completions. Month-to-date read **$84.87**
(`modal billing report`, 2026-07-26) against Amendment 3's **$100 report / $120 hard stop**;
§4's within-$30-of-cap guard is satisfied with wide margin. Loop total to date $6.83.

---

## 4. Pre-registration freeze

Frozen at commit `2bf474d`, **before** any Phase-19 generation ran.
P0 was committed separately and earlier.

---

## 5. RESULT — **BRANCH A fires, and the charter over-claimed its own power**

### 5.1 The cell

All frozen gates pass: **n = 54** (≥ 30), achieved powered **Δ_art −0.0040** (|·| ≤ 0.020),
**parse 0.9896** (≥ 0.95). Targeting was feasible at 14 bands, so branch D never applied.

| | i.i.d. | cond | artifact | **cond − iid** | CI95 |
|---|---|---|---|---|---|
| **twin** general-Qwen-1.5B, n=54 | 0.3037 | 0.3010 | 0.3075 | **−0.0027** | [−0.0588, +0.0533] |
| sibling Coder-1.5B, n=44 *(P11)* | 0.4704 | 0.4067 | 0.4589 | **−0.0638** | [−0.1250, −0.0025] |

**BRANCH A — TWIN CLEAN at true match.** The pre-registered rule was *"TWIN CLEAN ⟺ the
cond − iid CI95 includes zero."* It does. The 45% favourite fired, on a rule frozen at
`2bf474d`.

`verdict_legacy_p11_rule` reads **NO SINK** and `below_both_nulls_p11_rule` **False**, in
agreement — but the precise reason matters and is not "the twin is above the nulls." The
twin is **nominally below both** (−0.0027 vs its i.i.d., −0.0065 vs the artifact); it fails
the sink criterion because neither margin is significant or material. **The twin is
indistinguishable from its nulls, not above them.**

### 5.2 ⚠ The charter asserted discriminating power it did not have

§2 said: *"Two predictions, ~0.04 apart, and the cell distinguishes them."* **It does not,
and no power calculation was done before the run.**

| hypothesis | value | inside the twin's CI? |
|---|---|---|
| DIET claim | 0.0000 | **yes** (\|t\| 0.10) |
| compression law | −0.0398 | **yes** (\|t\| 1.30) |
| Coder sibling | −0.0638 | no (\|t\| 2.14) |

Achieved SE **0.0286** → **minimum detectable effect at 80% power = 0.0800**. The
separation the phase was built to resolve is **0.04 — half the MDE.** Both candidate
predictions sit inside the interval; the cell could not have chosen between them whatever
it returned.

**And the twin-vs-sibling comparison is not significant either.** The correct test is the
difference of the two estimates, not whether one point lies outside the other's interval:

> **twin − sibling = +0.0610 ± 0.0424, CI95 [−0.0220, +0.1440], \|t\| 1.44, p 0.150.**

So the `inside_sibling_ci: false` flag in the artifact — which turns on −0.0027 vs a bound
of −0.0028, a margin of **0.0001** — is a point-against-interval comparison and must not be
read as a demonstration that the twin differs from its Coder sibling. **It does not
establish that.**

### 5.3 What the phase does and does not establish

**Does:**
- **A powered, on-target, at-match non-Coder cell now exists** — n = 54, Δ_art −0.0040,
  k = 24 targeting, parse 0.99, run through the byte-identical path as the Coder rungs.
  §1.1's *instrument* asymmetry — every powered at-match cell being a Coder cell — **is
  fixed.** That was half the P0 complaint and it is discharged.
- The twin's point estimate (−0.0027) is **an order of magnitude closer to zero** than its
  sibling's (−0.0638), which is **directionally** what the DIET claim predicts.
- The compression law's **point** prediction of −0.0398 **missed by 0.037** — the observed
  effect is 93% closer to zero than predicted. Its *interval* contains the observation by
  **0.0006** at the extreme edge; that is a boundary artifact and **nothing is built on
  it in either direction.**

**Does not:**
- It does **not** show the twin differs from the Coder sibling (p 0.150).
- It does **not** discriminate DIET from the compression law (both inside the CI).
- It therefore does **not** close §1.1's *inferential* complaint, only its instrumental one.

**Net effect on the record:** the DIET attribution is **unchanged and still rests on Phase 9's
position-matched 2×2** (§1.3). Phase 19 adds a properly-instrumented non-Coder at-match cell
that is directionally consistent with it, and removes the excuse that no such cell existed.
The §0.2 / §0.3 position caveat landed at `6d34068` **stands as written** — it was owed on
P7's evidence quality regardless of this result, and this phase does not repair P7.

### 5.4 §8 ledger entry 12 — a discriminating-power claim asserted, not computed

Phase 17 fixed exactly this failure: it **measured** the k-scaling empirically in P0 rather
than assuming power, and its charter carried an explicit MDE. **Phase 19, one phase later,
asserted "the cell distinguishes them" from the fact that two predictions were numerically
0.04 apart — without computing the SE a 54-problem cell would achieve.** The arithmetic was
free, available before the run from any committed cell's per-problem spread, and would have
shown the design needed roughly **4× the problems** (SE 0.0143 for an MDE of 0.04) or a
paired design against the sibling on shared problems.

*Practice:* **any charter claiming that a cell discriminates between two hypotheses states
the achieved-SE estimate and the implied MDE, and compares the MDE to the separation, in
the pre-registration.** "The predictions are X apart" is not a power claim.

*Class:* this is the **fourth** distinct way this record has mis-specified a decision
quantity — entry 8 (a rule that cannot fire), entry 9 (a threshold not in units of spread),
entry 10 (a criterion that does not survive a change of units), entry 11 (kill criteria not
wired into the branch), and now entry 12 (power asserted, not computed). All five are free
desk checks. All five belong in every pre-registration.

---

## 6. GATE

**Branch A fired at 45% — the favourite, on a frozen rule — but is weaker than the charter
claimed, and the charter's error is recorded as §8 entry 12.**

**Prediction accounting.** A 45% / B 40% / C 5% / D 10%. **A fires.** It is counted as a
hit, with the annotation that the cell's MDE (0.080) was twice the separation it was built
to resolve (0.04), so the hit constrains less than the charter implied. B is *not* excluded
by this cell — −0.0398 sits inside the observed CI.

**Cost. $0.53**, read as a month-to-date aggregate delta ($84.87 → $85.40,
`modal billing report`, 2026-07-26) and labelled as such per Amendment 2. Against a
$0.30–0.70 estimate: **inside the band — the ninth consecutive calibrated generation
estimate.** Loop total **$7.36**; MTD **$85.40** against $100 report / $120 hard stop.

**What is now open.**

- **The twin at adequate power.** The single cheapest high-value cell in the record is now a
  *repeat* of this one at n ≈ 200, or better, a **paired** twin-vs-sibling design on shared
  problems, which would cut the difference SE substantially. The question — does a
  non-Coder model at true match sink? — remains genuinely open at ±0.06.
- **The compression law's slope**, still the record's most robust unexplained regularity
  (eight cells, R² to 0.92), and still not separating sinking from clean models.
- **The coverage channel**, un-intervened-on, with temperature excluded as an instrument
  (Phase 18) and nucleus/top-k or candidate-budget scaling named as successors.
- **The sink's positive mechanism**, still absent after six excluded candidates.
- **Nothing is running. Phase 19 is closed.**

---
