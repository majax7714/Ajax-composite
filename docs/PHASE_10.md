# Phase 10 — the sign/band question, and the criterion that would have answered it wrong

*Charter opened 2026-07-24. First iteration of the unattended loop
([AUTONOMOUS_LOOP.md]). Append-only; every run pre-registered with odds and
decision rules committed before it launches. This document is the Phase-10
pre-registration and result log.*

## 0. The question as inherited

§0.4 carries the **sign/band question** as an open successor: *"A clean model
below Δ_art 0"* — no non-Coder model had ever been measured conditioned on
artifacts **worse** than its own i.i.d. Phase 8's C2 tried and missed (subset
i.i.d. drift put it at +0.035 instead of −0.04); Phase 8's D2 therefore fit the
non-Coder response curve only over [+0.033, +0.170] and flagged everything below
as **extrapolated and unreliable** — the fit "turns the penalty positive at
−0.15, an extrapolation artifact."

The charter question was going to be: place DeepSeek genuinely below zero and
see whether it sinks. **The state read changed the phase before it cost
anything.** Both findings below are free — they come from re-reading committed
artifacts — and both are landed as P0 before any GPU spend.

---

## P0 — Free amendments *(no GPU; landed before the pre-registration below)*

### P0.1 — The cost record was anchored to an inferred number, not a bill

**The record's costs are wrong, and wrong in a way §10 already has a name for.**
§8 ledger entry 5 states "one W4 app billed ≈$31," and every phase from 5 onward
priced its envelope against that scale. The $31 was never read from a bill: the
entry itself shows the arithmetic — "≈6.5 h of judging on a cpu=32/64 GiB
container (**≈$5.5–6/h**)" — an inference from an assumed container rate. Pulled
from Modal's billing API on 2026-07-24 (`modal billing report`, 140 line items,
2026-06-25 → 2026-07-24):

| | |
|---|---|
| **True all-in spend, entire project** | **$78.04** |
| Largest single app (`rgr-lcb`, 07-16) | **$13.84** — not $31 |
| `rgr-lcb` (Phase 3a/3b LCB era, all apps) | $34.13 |
| `rgr-h1` (Phases 4–9, all apps) | $18.80 |
| `rgr-phase3a` | $12.58 |
| `rgr-phasek` | $11.87 |
| `rgr-phasem` | $0.66 |

Per-day: the entire Phase 6–9 science (07-17 → 07-19) cost **$15.86**, against
phase-doc claims of ~$9–13 (P6) + ~$18 (P7) + ~$22 (P8) + ~$26 (P9) ≈ **$75–79**.
**The recent phases were over-estimated by roughly 5×.** The assumed
$5.5–6/h container rate was itself ~2.3× high.

**The error class is the record's own.** §10 rule 2: *"a decision is not a claim;
a claim is not a finding."* An inferred quantity was recorded in the operational
ledger in the same register as a measured one, then became the anchor every later
phase reasoned from — the identical structure as the fixed-stimulus confound
(Phases 4/6) and the mined-proxy confound (Phase 8), one level up: a *proxy for
cost* was held constant while the thing it proxied drifted. Ledger entry 5's
**methodological** content (judge-grade mismatch is a real cost blind spot;
short-circuit vs all-cases matters) is unaffected and stands — only its magnitude
was inferred. §8 receives a dated addendum; the entry's original text stays.

**Consequence, and it is not cosmetic.** §0.4 shelves the **internals probe** —
the *only* remaining instrument for the positive mechanism — as "outside this
record's toolchain/budget." That gate was set against a phantom price. Re-pricing
it is carried into Phase 11 rather than assumed here.

### P0.2 — The sink criterion drifted, and it breaks exactly where Phase 10 was headed

The D2c **SINK** was defined (§9.7, claim 8) as conditioning landing **below both
nulls** — below the model's own i.i.d. *and* below the artifact it was shown.
The matched-battery signature used from Phase 7 onward
(`matched_sink_signature`) tests only:

> `mean_cond < mean_iid` **and** one-sided `p < 0.05` **and** `Δ_cond ≤ −0.05`

**The copy null was dropped.** While Δ_art ≥ 0 the two criteria agree, because an
artifact at or above the model's own level makes "below i.i.d." the binding
condition. **Below zero they come apart**: a model that faithfully imitates an
artifact worse than itself will land below its own i.i.d. *by construction* —
scoring a "sink" while doing nothing pathological at all. Every cell in Phases
7–9 sat at Δ_art ≥ −0.065, so the drift never bit. Phase 10's whole purpose is to
go below zero, which is precisely where it does.

**This would have produced a false positive as the phase's headline result.**

### P0.3 — The sign/band question is partly already answered, in Phase 9's own artifacts

The premise "no clean model has been measured at Δ_art ≤ 0" is **stale**. Phase
9's G1a/G1b cells landed at Δ_art **−0.065** and **−0.056** — below zero. Phase 9
read them correctly against its own 2×2 branch logic (which consumes only the
sink boolean) and moved on; the *effect sizes* were never examined. Re-expressed
against the copy null:

| cell | Δ_art | Δ_cond | **cond − artifact** | ratio Δ_cond/Δ_art |
|---|---|---|---|---|
| M1 DeepSeek (P7, at match) | +0.050 | +0.050 | **−0.000** | 1.00 |
| G1a DeepSeek self (P9) | −0.065 | −0.062 | **+0.003** | 0.95 |
| G1b DeepSeek foreign (P9) | −0.056 | −0.061 | **−0.005** | 1.09 |
| G1c Coder self (P9) | −0.044 | −0.200 | **−0.156** | 4.55 |
| G1d Coder foreign (P9) | −0.045 | −0.238 | **−0.193** | 5.29 |

DeepSeek lands within **0.005 of the artifact it was shown, three times**, across
a Δ_art range from +0.050 to −0.065. That is not "no sink" — it is a **gain of
≈ 1**: conditioned output tracks artifact quality one-for-one, up *and* down.
Coder undershoots the artifact by **0.156–0.193**.

**This sharpens rather than threatens the diet claim, and the sharpening
matters.** The defensible statement is not "non-Coder families do not degrade"
(they do, below zero, proportionally) but **"non-Coder families track the
artifact with gain ≈ 1; the Coder diet produces excess degradation of ~0.17
beyond what the artifact warrants."** Under [AUTONOMOUS_LOOP.md] §3 this is
*inspected, not halted*: it pressures the phrasing of claims 8/11 without
refuting either 1:1 — both are scoped **at match**, where they are untouched.

**The natural invariant is already in the record.** `Δ_cond − Δ_art` is
identically `cond − copy_null`, which the Phase-7 cells already report as
`delta_cond_minus_copy` (M1: **−0.0002**). The quantity was being computed and
not being read.

---

## 1. Standing rules

Unchanged: append-only; pre-register odds and decision rules before launch; no
learned verifier; reconciliation-ledger entries; §8 ledger + stack fingerprint;
distinct-seed protocol; the matched-relation rule with the iterative-targeting
amendment (target a **measured** Δ_art, never a mined proxy); Index current at
close. Plus [AUTONOMOUS_LOOP.md]: pre-registration commits before spend, raw data
commits before analysis, 1:1 refutation halts the loop.

## 2. The question, restated

Not "does a clean model sink below zero" — P0.2 shows that question is
ill-posed under the drifted criterion, and P0.3 shows the raw form is already
answered. The real question:

> **Is the Coder pathology a difference in *gain* (a quantitative
> over-response present in every family) or a difference in *kind* (excess
> degradation unique to the Coder diet)? And does the non-Coder gain of ≈ 1 hold
> further below zero, or does it break down at larger deficits?**

### R1 — the free re-analysis *(no GPU, runs first)*

Re-express **every** conditioning cell in the record — Phases 3b, 4, 6, 7, 8, 9 —
on the residual `cond − artifact` and the gain `Δ_cond/Δ_art`, with the Δ_art at
which each was measured. Output: `artifacts/h10_gain_reanalysis.json` +
`scripts/j10_gain_reanalysis.py`.

**Pre-registered predictions (committed before the analysis runs):**

| # | prediction | odds |
|---|---|---|
| 1 | Coder cells separate from non-Coder cells on residual with **no overlap** | **70%** |
| 2 | Non-Coder residuals cluster at 0 ± 0.03 across **all** families (DeepSeek, StarCoder2, general-Qwen), not just DeepSeek | **55%** |
| 3 | Coder residual is **not** constant — it varies with Δ_art (position-gating survives the reframe) | **60%** |
| 4 | phi-1's residual sits **between** the clean cluster and Coder (the "distinctly Coder-like" lean, now on a continuous axis) | **45%** |

**Decision rule.** If prediction 1 holds, the residual is adopted as the
record's reporting axis alongside Δ_cond, and the §0 claim-8/11 scope lines gain
the gain-vs-kind distinction. If it fails — if some Coder cell has a residual
inside the clean cluster, or some clean cell outside it — the reframe is
**dropped**, not rescued, and the phase reports the negative.

### R2 — the paid cell *(GPU; launches only if R1's prediction 1 holds)*

**Design.** DeepSeek-1.3B conditioned at Δ_art ≈ **−0.15** (roughly 2.5× deeper
than G1a/G1b), self-provenance, reusing Phase 9's cached high-T pools
(`j9_pool_*`, `j9_iid_*` — verified present locally and on the volume, so only
the conditioning generation and judging are paid for). Band re-centered by the
iterative-targeting procedure on the **measured** covered-subset i.i.d.

**Positive control.** Qwen-Coder-1.5B at the same Δ_art ≈ −0.15. Phase 8's D2
puts the Coder trough at Δ_art ≈ −0.092 with LOO range [−0.12, −0.03], so −0.15
is past the trough on the far side: the position-gated model predicts Coder's
**residual shrinks** relative to G1c/G1d. If the control shows no excess
degradation at all, the machinery is suspect and the phase reads INCONCLUSIVE on
instrument, not on question.

**Primary outcome: the residual `cond − artifact`, not `Δ_cond`.** The sink
boolean is reported for continuity and explicitly **not** used for adjudication
below zero (P0.2).

| # | branch | prediction | odds |
|---|---|---|---|
| A | **GAIN-1 HOLDS** — DeepSeek residual stays within ±0.03 at −0.15 | imitation is faithful arbitrarily far down; the Coder effect is a difference **in kind**; sign/band question **closes** | **45%** |
| B | **GAIN BREAKS DOWN** — DeepSeek residual goes clearly negative (≤ −0.05) at −0.15 | every family over-degrades once the artifact is far enough below it; Coder's diet lowers the *threshold* — a difference **in degree**. Claims 8/11 need re-scoping (inspect, not halt) | **30%** |
| C | **GAIN OVERSHOOTS UP** — DeepSeek residual goes **positive** (≥ +0.05) | the model partially ignores a bad artifact — a floor effect; would mean below-zero conditioning is bounded by the model's own competence | **20%** |
| D | UGLY — coverage collapse, off-target Δ_art, or control failure | phase reports INCONCLUSIVE on instrument | **5%** |

**Frozen parameters.** Band half-width 0.08; conditioning seed 17 (distinct from
the i.i.d. seed 101 and the generation seed 202); n ≥ 15 required per cell, and a
cell with n < 15 is reported as underpowered rather than pooled; on-target =
|achieved Δ_art − (−0.15)| ≤ 0.05 on the measured subset i.i.d.; Wilcoxon
one-sided, same implementation as Phases 7–9.

**Cost estimate: $3–6** (conditioning + judging only; pools reused). Checked
against the $90/$110 envelope and the month-to-date workspace figure before
launch.

---

*(Results append below. R1 first — free — then R2 conditional on it.)*

---

## R1 RESULT (2026-07-24) — **the reframe is DROPPED: 1/4 predictions hit, the 70% favourite MISSED** *(`h10_gain_reanalysis.json`, `scripts/j10_gain_reanalysis.py`)*

14 cells harvested (6 Coder, 6 non-Coder, 2 synthetic), every conditioning cell in
the record carrying an i.i.d., a conditioned mean, and a copy null.

| cell | family | diet | n | Δ_art | Δ_cond | **residual** | gain |
|---|---|---|---|---|---|---|---|
| C4_coder7b_widerN | Qwen-Coder-7B | coder | 37 | −0.101 | −0.103 | **−0.003** | 1.03 |
| G1d | Qwen-Coder-1.5B | coder | 10 | −0.045 | −0.238 | **−0.193** | 5.30 |
| G1c | Qwen-Coder-1.5B | coder | 10 | −0.044 | −0.200 | **−0.155** | 4.50 |
| M4_coder7b | Qwen-Coder-7B | coder | 20 | −0.039 | −0.129 | **−0.089** | 3.27 |
| D2c_original | Qwen-Coder-1.5B | coder | 44 | +0.026 | −0.095 | **−0.121** | — |
| M5_coder0p5b | Qwen-Coder-0.5B | coder | 43 | +0.081 | +0.044 | **−0.037** | 0.54 |
| G1a | DeepSeek | non-coder | 19 | −0.065 | −0.062 | **+0.003** | 0.95 |
| G1b | DeepSeek | non-coder | 19 | −0.056 | −0.061 | **−0.004** | 1.08 |
| M3_starcoder2_3b | StarCoder2 | non-coder | 39 | +0.033 | +0.008 | **−0.025** | 0.25 |
| C2_deepseek_below0 | DeepSeek | non-coder | 29 | +0.035 | +0.043 | **+0.009** | 1.26 |
| M1_deepseek1p3b | DeepSeek | non-coder | 39 | +0.050 | +0.050 | **−0.000** | 0.99 |
| M2_general1p5b | Qwen-general | non-coder | 28 | +0.064 | −0.000 | **−0.064** | −0.00 |
| G2_phi_truematch | phi-1 | synthetic | 24 | +0.032 | −0.042 | **−0.073** | — |
| C3_phi1_match | phi-1 | synthetic | 47 | +0.042 | −0.033 | **−0.075** | — |

**Prediction accounting:**

| # | prediction | odds | result |
|---|---|---|---|
| 1 | Coder/non-Coder separate on residual, no overlap | 70% | **MISS** — ranges overlap heavily: Coder [−0.193, −0.003], non-Coder [−0.064, +0.009]; gap **−0.062** |
| 2 | non-Coder cluster at 0 ± 0.03 across ≥ 3 families | 55% | **MISS** — `M2_general1p5b` at −0.064 |
| 3 | Coder residual varies with Δ_art (range ≥ 0.05) | 60% | **HIT** — range 0.191 |
| 4 | phi between the clusters | 45% | **MISS** — phi (−0.073, −0.075) sits *inside* the Coder range; the clusters overlap, so "between" is undefined |

**Verdict: the residual reframe is DROPPED, per the pre-committed decision rule
("if it fails the reframe is dropped, not rescued").** The gain-of-≈1 pattern that
motivated it is real for DeepSeek across three cells but is **not diet-diagnostic**:
a Coder cell (C4, gain 1.03) sits inside the clean cluster and a non-Coder cell
(M2 general-Qwen, −0.064) sits inside the Coder range. "Non-Coder models track the
artifact with gain ≈ 1" is **false as a family claim**.

This is the failure mode §10 names as *treading into our own water* — a law
derived post-hoc from five hand-picked cells, dying on the full set of fourteen.
It is recorded as a negative and not rescued. Prediction 3's hit is noted but
carries no weight on its own: position-dependence of the Coder residual is already
the Phase-8 D2 finding on a different axis.

### R1's real result — **P0.2's criterion drift, instantiated on the record's flagship 7B confirmation**

The one thing the re-analysis found is not the reframe; it is the cell that broke
it. **`C4_coder7b_widerN` is the record's "7B sink CONFIRMED at n = 37."**

```
iid 0.7490   artifact 0.6483   cond 0.6457
Δ_art  −0.1007        Δ_cond  −0.1033        cond − artifact  −0.0026
```

The artifact was **0.10 below the model's own level**, and the model produced
output **0.003 below that artifact** — it tracked the artifact essentially
exactly. Under the **original D2c SINK definition (below *both* nulls, §9.7,
claim 8)** C4 **does not sink**: it is not below the copy null. It scored
`matched_sink_signature = True` only because the Phase-7+ signature tests
`cond < iid`, which at Δ_art = −0.101 is near-automatic for any faithful imitator
(P0.2, pre-registered before this analysis ran).

**How it happened, from the record's own text.** [PHASE_8.md] C4 was chartered as
"Coder-7B **at match**" (target i.i.d. 0.659). Reaching n = 37 required widening
the band to **±0.10**, and the widening carried the achieved position out of the
straddle onto the below-zero arm — [PHASE_8.md]'s result table records
`Δ_art −0.101` in a row whose position column still reads "match." This is the
**matched-relation rule (§10) failing on its own amendment**: the band was widened
for power, and the *relation* moved while the label did not.

**Scope of the correction, stated precisely — the phenomenon is not refuted:**

- **M4** (Coder-7B, n = 20, Δ_art **−0.039**, residual **−0.089**, p 0.0024)
  satisfies below-both-nulls and **stands**. The 7B sink is real.
- **C4 does not confirm M4.** It measured a *different position* (−0.101 vs
  −0.039) and, on the stricter criterion, found no excess degradation there.
  "CONFIRMED at n = 37, robust to n and seed" is not supported by this cell;
  the 7B sink rests on **n = 20**, as it did before Phase 8.
- The affected cell is **C4 alone**. Every other below-zero cell (G1c −0.155,
  G1d −0.193, M4 −0.089) shows genuine excess degradation and is unaffected.
- Read forward, C4 is still *informative*: Coder-7B at Δ_art −0.101 shows **no
  excess degradation**, which is evidence about the far side of the position
  curve — the trough shrinking toward the arms, consistent with D2's shape.

**[ADJUDICATED 2026-07-24 — author authorized both actions: append the correction
across the record, and re-run the cell honestly. The correction pass is committed
(`cb1a1a9`); R3 below is the re-run, pre-registered before spend.]**

**Author adjudication required — the loop halts here.** This contradicts a
specific committed sub-claim ("7B sink CONFIRMED at n = 37, C4") that is carried
in the abstract's Phases 8–9 banner, §0 Index rows 8 and 11, §0.3 row 8, and
[PHASE_8.md]'s gate item 4, and it touches the extraction gating ("the phenomenon
is transcription-ready and 7B-confirmed"). Under [AUTONOMOUS_LOOP.md] §3.1/§3.5
the loop does not revise claim status or abstract banners on its own authority.
**No Index, abstract, or PHASE_8 text has been edited.** R2 is **not authorized**
(its gate was R1 prediction 1, which missed) and **nothing was spent**.


---

## R3 — the honest 7B confirmation at true match *(pre-registered 2026-07-24, BEFORE spend)*

**Question.** Does Qwen2.5-Coder-7B show a genuine **below-both-nulls** sink at
**true match** (Δ_art ≈ 0), at **n > 20** — i.e. can the confirmation withdrawn
from C4 be earned back at the position the claim is actually about?

**Why C4 could not answer it.** C4 targeted a fixed artifact frac (0.659) and
widened the band to ±0.10 for power; the covered subset's i.i.d. rose to 0.749 and
the achieved relation fell to −0.101. The proxy was held, the relation was not —
the Phase-8 §10 refinement, unapplied.

### Design

**Select on one seed, measure on another.** The selection stage and the
measurement stage draw independently, so the subset cannot be selected on the same
noise it is later scored against. This is the distinct-seed protocol (§10, Phase-6
P2) applied for the first time to *artifact selection* rather than to a control arm.

- **Step 1 — selection sweep (seed 71).** Coder-7B i.i.d., 8 candidates, over all
  **80** problems of the fixed donor pool (`lcb_cand_lcb_r2_base_T08`), giving a
  per-problem i.i.d. map independent of the measurement draw.
- **Step 2 — offline targeting (free).** Over that map, choose the (target, band)
  maximising **n** subject to **|predicted Δ_art| ≤ 0.01**, where predicted
  Δ_art = mean(selected artifact frac) − mean(step-1 i.i.d. on the covered subset).
  One artifact per problem, in-band candidate nearest target, deterministic
  tie-break by index — the frozen Phase-7 miner rule, unchanged.
- **Step 3 — the cell (seed 89).** `_matched_cell`: E0 and E1 measured fresh in one
  batch on the selected problems. Achieved Δ_art is computed from *this* draw.

Model pinned as in C4: `Qwen/Qwen2.5-Coder-7B`, revision `0396a761…`. Seeds 71 and
89 are distinct from 17 (M4), 43 (C4), and 101/202 (Phase 9).

### Frozen criterion — the ORIGINAL definition

**Primary: below both nulls** (§9.7, Index claim 8) —

> `mean_cond < mean_iid` **and** `mean_cond < mean_artifact` **and**
> one-sided `p < 0.05` on cond-vs-artifact **and** `cond − artifact ≤ −0.05`

The Phase-7+ `matched_sink_signature` is computed and reported **for continuity
only; it does not adjudicate** (P0.2).

**On-target:** `|achieved Δ_art| ≤ 0.03`. **Minimum n = 20** — the cell must at
least match M4's n to constitute a higher-n confirmation; below that it is reported
**underpowered**, not pooled. **A miss on either is reported as a miss and NOT
re-run to fit** — re-targeting after seeing the outcome is tuning past a gate.

### Pre-registered predictions

| # | branch | reading | odds |
|---|---|---|---|
| **A** | **SINK CONFIRMED at match** — below both nulls, p < 0.05, cond − artifact ≤ −0.05 | the withdrawn confirmation is **earned back** at the right position and n > 20; claims 8/11 restore a higher-n 7B leg, now criterion-clean | **55%** |
| **B** | **SUB-THRESHOLD** — negative but > −0.05, or p ≥ 0.05 | the 7B sink holds at M4's position (−0.039) but not demonstrably at true match; scope narrows to a **position band**, not "at match" generally | **25%** |
| **C** | **NO SINK at match** — cond − artifact ≈ 0 or positive | the 7B sink is specific to Δ_art ≈ −0.04 and absent at 0; a real narrowing of claims 8/11 — inspect, do not halt (M4 still stands at its own position) | **15%** |
| **D** | off-target (\|Δ_art\| > 0.03) or n < 20 | no adjudication; reported as an instrument miss | **5%** |

**Methodological prediction (separate, committed):** achieved Δ_art will land within
**±0.03 of predicted**, because selection and measurement use independent draws.
Under the old same-draw design the expected failure was regression to the mean
pulling the measured i.i.d. down and Δ_art positive. **65%.**

**Cost estimate: $2–5** (≈640 selection-sweep generations + ≈2 × n × 8 cell
generations on 7B, plus judging; donor pool reused, no artifact generation).
Month-to-date workspace spend checked before launch: **$78.04 of the $200 cap**,
leaving ample headroom; cumulative loop spend before this run: **$0**.

---

## R3 RESULT (2026-07-24) — **BRANCH D: OFF-TARGET.** The at-match question is not answered, and the reason is the instrument *(`h10_r3_coder7b_truematch.json`, `h10_r3_targeting.json`, `h10_r3_instrument.json`)*

**Step 1** (seed 71, all 80 donor-pool problems): Coder-7B i.i.d. **0.6574** — well below
the 0.7490 that C4's 37-problem subset showed, independently confirming that C4's
band-widening had selected a systematically *easier* subset.

**Step 2** (offline targeting): chose **target 0.72 ±0.09, n = 30**, artifact mean
0.7075 against a selection-sweep subset i.i.d. of 0.7157 → **predicted Δ_art −0.0082**,
inside the ≤ 0.01 constraint, with n = 30 > M4's 20.

**Step 3** (seed 89, the cell):

| | n | Δ_art | i.i.d. | artifact | cond | **cond − artifact** | p(cond<artifact) |
|---|---|---|---|---|---|---|---|
| **R3** | 30 | **−0.0396** | 0.7471 | 0.7075 | 0.6978 | **−0.0097** | 0.378 |

**Achieved Δ_art −0.0396 against a predicted −0.0082 — a miss of 0.0314, outside the
frozen ±0.03 on-target tolerance. Branch D fired. The cell does not adjudicate the
at-match question, and per the pre-registration it is NOT re-run to fit.**

### Prediction accounting — a bad day for the priors, recorded as such

| prediction | odds | outcome |
|---|---|---|
| R1 #1 — residual separates the diets | **70%** | **MISS** |
| R1 #2 — clean cluster at 0 ± 0.03 | 55% | MISS |
| R1 #3 — Coder residual varies with Δ_art | 60% | HIT |
| R1 #4 — phi between clusters | 45% | MISS |
| R3 branch | A 55 / B 25 / C 15 / **D 5** | **D — the 5% branch fired** |
| R3 methodological — achieved Δ_art within ±0.03 of predicted | **65%** | **MISS** (0.0314) |

Two favourites at 70% and 65% both fell, and the 5% branch fired. Recorded without
softening; the odds stay on the page.

### Why it missed — the fix was right and insufficient

The selection/measurement split did what it was designed to do: it removed
selection-on-noise. It cannot remove sampling noise in the *measurement*. Both draws
cover the same 30 problems, so the noise is directly measurable — and free:

| quantity | value |
|---|---|
| per-problem i.i.d. difference between seeds, sd | **0.1516** |
| per-problem mean \|difference\| | 0.1158 (max 0.375) |
| **SE of the 30-problem subset mean** | **0.0277** |
| on-target tolerance used | 0.03 = **1.08 SE** |
| observed miss | 0.0314 ≈ **1.1 SE** |

**The tolerance was set at one standard error of the very quantity being targeted.**
No targeting procedure, however clean, could hit it reliably. The miss is not
regression to the mean and not a design flaw in the seed split — it is the i.i.d.
estimator at 8 candidates/problem being too noisy for the job. Hitting Δ_art to ±0.03
requires **more candidates per problem for the i.i.d. estimate**, not a different seed
scheme.

### The record-wide implication *(the phase's real product)*

Every matched cell's relational position, Phases 7–10, is known only to about
**±0.03** at 8 candidates/problem. The "on-target" bands the record has used —
±0.05 (Phases 7/8), ±0.08 (Phase 9) — are **2–3 SE wide**. Consequences, stated
without exaggeration:

- Differences in Δ_art **below ~0.06** between two cells are **not resolvable**.
  Cells described as sitting at different positions may not be.
- The **D2 trough** (vertex −0.092, LOO [−0.12, −0.03]) is a quadratic fit over six
  points each carrying ±0.03 of *horizontal* uncertainty, which the fit does not model.
  The trough's *existence* is not challenged here; its *location* is softer than the
  three-decimal figure suggests.
- Phase 8's "recurring methodological finding" attributed Δ_art drift to **subset
  composition**. That is real, but it is not the only cause: **plain sampling noise in
  the i.i.d. estimate contributes ~±0.03 on its own**, and it does not go away by
  iterating the targeting.

### Post-hoc observation — flagged as a pointer, **not a result**

R3 landed at Δ_art **−0.0396**; M4 sits at **−0.0393**. Near-identical relational
position, R3 with higher n and a distinct seed:

| | n | seed | Δ_art | i.i.d. | artifact | cond | cond − artifact | p |
|---|---|---|---|---|---|---|---|---|
| **M4** (Phase 7) | 20 | 17 | −0.0393 | 0.7023 | 0.6631 | 0.5738 | **−0.0893** | 0.0024 |
| **R3** | 30 | 89 | −0.0396 | 0.7471 | 0.7075 | 0.6978 | **−0.0097** | 0.378 |

**R3 does not reproduce M4's effect.** This is recorded because it bears on a LIVE
claim, and it is **explicitly not adjudicated**, for three reasons: R3 is off its own
pre-registered target (branch D); the subsets differ; and the absolute levels differ
(M4's artifacts at 0.663, R3's at 0.708), so "same Δ_art" does not mean "same
stimulus." Two readings survive and this cell cannot separate them — (a) the 7B effect
at this position is not robust, or (b) the response depends on absolute level as well
as relational position, which the whole matched-artifact program assumes it does not.

**Standing of the 7B sink after today, stated plainly.** The C4 confirmation was
withdrawn this morning (criterion drift); the leg now rests on **M4, n = 20, alone**;
and the one higher-n cell near that position did not reproduce it. **No claim is
retracted on this basis** — R3 was off-target and cannot carry a retraction. But the
7B leg is weaker than the record currently states, and the discriminating test is
named below.

### What this phase licenses next *(named, not run)*

1. **A powered targeting instrument.** Raise the i.i.d. estimate to ≥ 24
   candidates/problem (SE ≈ 0.016) before any further matched cell. Without it, no
   cell can be placed to ±0.03, and the position-gating story cannot be read finer
   than ~0.06.
2. **The M4-vs-R3 discriminator.** One pre-registered cell holding *absolute level*
   fixed at M4's (artifact ≈ 0.663) with n ≥ 30 and the powered instrument decides
   between readings (a) and (b) — and, with it, whether the 7B sink survives.

**Cost:** R3 ran to completion, exit 0, app `ap-oeWV3hCy9soeQW5amTPZ3F`. *(Filled
2026-07-25: **≈ $0.27**, from the month-to-date aggregate rising $78.04 → $78.31 across
the run. Modal's per-app daily line still had not posted, so this is an **aggregate
delta, not a line item**, and is labelled as such per §8 entry 7.)* **The estimate was
$2–5; the bill was ≈$0.27 — the loop over-estimated by ~10×, reproducing in its own
first pre-registration the exact bias it had corrected in the record hours earlier
(P0.1).** Recorded, and the reconciliation practice is codified as
[AUTONOMOUS_LOOP.md] Amendment 2.

**Phase 10 does not close here.** R1 is closed (reframe dropped). R3 is closed as an
instrument miss with the diagnostic as its product. The at-match 7B question is
**re-opened and unanswered**, and the loop halts for author direction: item 1 above is
a prerequisite for anything further in this line.
