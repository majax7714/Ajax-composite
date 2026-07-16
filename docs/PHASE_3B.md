# PHASE 3B — design cycle: harden the elimination argument, size R3, freeze the pre-registration

*Charter committed 2026-07-15, before any W-item ran. This document holds the cycle's
pre-registrations and, per the append-only rule, their outcomes. The frozen 3b
pre-registration (W3) lands here once W0–W2 are in.*

## Charter

The elimination argument (§9.3.1) is now the project's central claim. Before the 3b
pre-registration freezes, it gets the same audit treatment H1 and F2 got: three of its
joints are unmeasured, and all three attacks are cheap. Work items, strictly in order:

- **W0** — free CPU recomputes from committed pools: (a) the E0 anchor measured on the
  same PULL metric as every conditioned cell; (b) the D2c copy-expectation null;
  (c) per-problem solve-rate distribution + the false-zero rate of the pass@50 = 0
  stratum label.
- **W1** — E7, the repelled-conditioning arm: the elimination argument excludes
  repulsive conditioning a priori; populate the region and test the asymptote.
- **W2** — LCB-medium base-model screen: size R3 before pre-registering it; power
  check before any kill criterion is frozen.
- **W3** — freeze the 3b pre-registration (R3 four-arm with the Olausson
  decomposition, D2c/E6 with W0b's null, BEST-SO-FAR, recovery validation protocol).
- **W4** — execute D2c/E6 → R3 → BEST-SO-FAR.

**Standing rules.** Append, never revise; pre-register before running (predictions with
odds, kill criteria, decision rules — committed before the run; falsified predictions
stay on the page). **No learned verifier anywhere** — H1's kill propagates: every
selection/ranking stage in 3b/R3/BEST-SO-FAR uses likelihood or execution feedback
only. **Literature-engagement rule (now explicit):** no external conclusion is imported
as a general truth or design constant; for each external result leaned on, extract
baseline type, scale, error-type mix, feedback source, and task regime, and record what
their *mechanism* predicts for our cells before use — maintained as a reconciliation
ledger appended to [WRITEUP-rgr.md §11], one entry per reference per design decision it
influenced. The elimination argument is not protected because it is ours: W1 branch (c)
or a moved W0a anchor triggers the same in-place retraction/rescope treatment F2 got.

**Verdict-first summary of what this cycle decides.** By the end of W3 the project has
either (a) a hardened elimination argument with a measured anchor and a closed
repulsion escape-hatch, a powered R3 with an interpretable null, and a frozen pre-reg —
or (b) a retracted/rescoped central claim and a redirected design, recorded with the
same honesty as H1 and F2. Both are progress; only silent drift is failure.

---

## W0 pre-registrations *(committed before computing; all pure CPU over committed artifacts)*

### W0a — the honest E0 anchor

**The hole.** The central figure ([§9.3.1] item 3) anchors E0 at (0.396, ~0.90), where
x = 0.396 is DIAG-8's B1 i.i.d. **within-set pairwise** edit distance — while every
conditioned cell's x is **PULL = distance-to-the-specific-artifact**. Two different
metrics share one axis; the "approach from below" reading (E1@T1.2 PULL 0.309 < anchor
0.396) rests on the unmeasured assumption that the two are commensurate.

**Method.** For each of the 60 shared problems (one identical subset across all
conditions — [artifacts/dmeasure_subset_control.json]), compute PULL of every committed
E0 generation ([runs/modal/dmeasure_gen.json], cond=E0, T ∈ {0.0, 0.8, 1.2}) against
the **same failed artifact E1/E2 conditioned on** (first failed candidate per pid from
the m3 pool — the committed selection rule, reconstruction verified in the Addendum-IV
control). Identical estimator: PULL = 1 − `SequenceMatcher.ratio(gen, fail)`, empty
generations excluded, per-problem mean then unweighted mean across problems, reported
per temperature ± sd. The T=1.2 row is the figure's anchor row (E0 coverage 0.90).

**Pre-registered prediction (before computing): E0-PULL lands within ±0.05 of 0.396 —
odds ~70/30.** If it lands materially elsewhere, the figure's anchor moves and the gap
to E1@T1.2's 0.309 changes size; either way the anchor becomes measured, not assumed.
Secondary expectation (no odds): E0-PULL ≳ every failure-conditioned PULL at matched T
(an i.i.d. generation should sit at least as far from an arbitrary failed candidate as
a generation conditioned on it) — a violation would mean the anchor is *below* some
conditioned cells and the figure's geometry inverts.

**Writeup destination:** §9.3.1 append, "E0 anchor, measured." Artifact:
`artifacts/w0a_e0_anchor.json`.

### W0b — the D2c copy-expectation null

**The hole.** Copy fidelity under conditioning is 83–98%, so the null for a generation
conditioned on a partial-credit artifact (frac_tests = f) is **frac ≈ f — not zero**.
A D2c that scores "any nonzero frac" as climbing would be theater.

**Method.** From the enriched base T=0.8 LCB-easy pool
([runs/modal/lcb_res_lcb_r2_base_T08.json] + candidates), enumerate partial-credit
candidates (0 < frac < 1), report the distribution (count, per-problem spread, the
40–60% band that D2c's artifact selection draws from), and pre-commit **per-artifact
null lines**: for artifact a with frac f_a, (i) **copy-null** E[frac(gen)] = f_a;
(ii) **i.i.d.-null** = that problem's pool mean frac (what unconditioned sampling
already yields). "Climbing" in D2c/E6 = paired mean(frac(gen) − f_a) > 0 across
artifacts **and** frac(gen) > i.i.d.-null (beating copying *and* beating resampling);
formal test frozen at W3. Artifact: `artifacts/w0b_copy_null.json`.

### W0c — stratum characterization: per-problem p̂ and the false-zero rate

**The hole.** A problem with true per-sample solve rate p = 0.01 survives 50 draws with
probability (1−0.01)⁵⁰ ≈ 0.605 — the pass@50 = 0 label has a **false-zero rate**, so a
fresh B1-50 control arm will produce nonzero "recoveries" by luck alone. R3's bar must
be ABSTRACT > B1-50 **paired**, never ABSTRACT > 0.

**Method.** Per feasible cell (base T0.8/T1.0/T1.2, instruct T1.2;
[runs/modal/lcb_res_lcb_r2_*.json]), per-problem solve counts x_i/50 → p̂ distribution.
Fit a two-component prior over true p — point mass π₀ at p = 0 plus (1−π₀)·Beta(α,β) —
by maximum likelihood on the 80 count observations (grid/EM; binomial likelihood).
For the observed-zero stratum: posterior P(p > 0 | 0/50) and posterior expected fresh-50
recovery probability E[1−(1−p)⁵⁰ | x=0]. **Output: expected B1-50 recovery count per
stratum per cell** — this number goes directly into R3's decision rule as the stated
null floor. Nonparametric sanity check alongside: the histogram mass at x ∈ {1, 2}
(problems one lucky draw from the stratum). Sensitivity: report the fit with and
without the point mass (a pure-Beta fit bounds the false-zero rate from above).
Artifact: `artifacts/w0c_stratum_falsezero.json`. Writeup destination: new §9.6
(stratum characterization), which W2 extends.

---

## W0 RESULTS (2026-07-15) — [artifacts/w0a_e0_anchor.json, w0b_copy_null.json, w0c_stratum_falsezero.json]

**W0a — the anchor MOVED; the 70/30 prediction was WRONG.** E0-PULL against the same
failed artifacts every conditioned cell used: **0.4085 ± 0.319 (T=0, n=59) / 0.4910 ±
0.212 (T=0.8) / 0.5935 ± 0.178 (T=1.2)**. The T=1.2 anchor is **+0.198 from the
assumed 0.396** — far outside the pre-registered ±0.05 band. The assumed value was
within-set pairwise diversity; the measured value is distance-to-a-failed-candidate,
and an i.i.d. sample sits substantially farther from a failed candidate than two
i.i.d. samples sit from each other. **The secondary expectation holds** (E0-PULL ≥
every conditioned PULL at matched T: 0.491 > 0.176/0.068; 0.594 > 0.309/0.157), so the
figure's geometry does not invert — it **stretches**: the honest anchor puts E1@T1.2
(PULL 0.309, cov 0.62) not near the anchor but **barely past half the escape distance**
to i.i.d. (0.594, cov 0.90). Two consequences, recorded: (i) the "approach from below"
gap is ~3× larger than the old figure implied — undirected escape at the hottest
measured temperature has closed only ~52% of the distance; the "can only approach
i.i.d." asymptote has far more unclaimed room than assumed, and nothing measured
crosses it. (ii) A calibration fact: even greedy i.i.d. sits only ~0.41 from an
arbitrary failed candidate (same problem, same model → ~59% natural token overlap), so
conditioned PULLs of 0.04–0.31 are *deep* inside copy territory. The elimination
argument survives W0a with its anchor now measured; §9.3.1 item 1's specific "0.396"
sentence is superseded in place.

**W0b — the copy-expectation null, computed.** Base T=0.8 LCB-easy enriched pool:
**77/80 problems** hold partial-credit candidates — **1,602 total** (far richer than
the 360 earlier quoted, which is exactly the 40–60% band: **360 in [0.4, 0.6]**).
Partial frac mean/median 0.384/0.333, median 15 tests/problem. Per-artifact null lines
persisted: copy-null = f_a, i.i.d.-null = problem pool mean frac. D2c/E6's "climbing"
must clear **both** (beat copying and beat resampling); formal test frozen at W3.

**W0c — the false-zero floor is large; the easy strata alone are unpowered.**
Two-component fit (π₀ point mass + Beta, ML; pure-Beta fit as upper bound):

| cell | stratum (0/50) | x=1 / x=2 | E[B1-50 lucky recoveries] (upper) |
|---|---|---|---|
| base T=0.8 | 19/80 | 10 / 5 | **3.59** (3.91) |
| base T=1.0 | 26/80 | 5 / 4 | 2.30 (5.31) |
| base T=1.2 | 35/80 | 10 / 5 | 5.01 (6.89) |
| instruct T=1.2 | 32/80 | 10 / 3 | 4.55 (5.45) |

The mixture split (π₀ vs Beta shape) is fit-unstable cell-to-cell — P(reachable|0)
ranges 0.22–0.81 — but the expected-recovery floor is stable at **~2–5 per stratum**
and bounded above by the pure-Beta fit. Read against R3's pre-registered 5–20% recovery
prediction (1–7 recoveries on 19–35 problems): **the noise floor is the same size as
the signal.** ABSTRACT > 0 was already banned; W0c shows even ABSTRACT > B1-50 paired
is unpowered on the easy strata alone. W2 (LCB-medium stratum) is promoted from
contingency to **prerequisite**, exactly as chartered.

---

## W1 pre-registration — E7, the repelled-conditioning arm *(committed before running)*

**The hole.** The elimination argument's asymptote ("undirected failure-conditioning can
only approach i.i.d.") excludes a third limit a priori: **repulsive conditioning**. A
model anti-correlated with the artifact samples from i.i.d.-restricted-to-the-complement
of the failed basin — on a peaked distribution where the failed mode holds mass and zero
solutions, that beats i.i.d. at matched compute by not re-wasting draws. Our data show
attraction dominates in-range (max PULL 0.309 vs measured anchor 0.594), but the
decisive region (PULL ≳ anchor) is unpopulated.

**Design.** Identical D-measure protocol (instruct generator, vLLM bf16 L4, top_p 0.95,
seed 17, max_tokens 512, ns=8, the same 60-problem first-60-mixed subset, the same
per-problem failed artifacts, Daytona execution). New cells:

- **E7 @ T ∈ {0.8, 1.2}** — explicit-avoidance framing: *"A previous attempt that
  FAILED: [artifact]. Do not repeat this approach. Take a substantially different
  approach and write a correct complete solution as a single fenced Python code
  block."* One framing, strong avoidance verb — the verb is the live lever (D2a: 3–4×
  provenance), and the Tsui ledger entry licenses treating this as a verb intervention
  (no attribution variant needed).
- **E1 @ T=1.5 and E0 @ T=1.5** — extends the attraction curve toward the anchor, with
  its matched i.i.d. baseline; E0@1.5's PULL extends the measured anchor row.

PULL is measured for **every** cell (E0/E7 included) against the same failed artifact.

**Decision rule (paired vs committed E0 at matched T, n=60; band pre-committed):**
- **(a)** E7 coverage ≤ E0 − 0.05 → **elimination argument strengthened**: the
  asymptote holds even under explicit repulsion; "strictly dominated" stands as
  written.
- **(b)** |Δcoverage| < 0.05 → argument **stands, restated**: "≤ i.i.d." — drop
  "strictly".
- **(c)** E7 coverage ≥ E0 + 0.05 **and** McNemar p < 0.10 → **a bigger result than
  the one being defended**: cheap mode-exclusion beats resampling; the elimination
  argument is **retracted-as-overclaim in place**.

**Odds (recorded before running): (a) 55% / (b) 40% / (c) 5%.**

**Power caveat (recorded).** E0 is near-saturated on this subset (coverage 0.92/0.90 at
T=0.8/1.2), so branch (c)'s detectable region is compressed to +0.08–0.10 max headroom.
A branch-(b) landing with E7-PULL ≥ the anchor is still decisive for the design
question: repulsion that reaches vacuous-conditioning distance and buys nothing over
i.i.d. is the asymptote observed from the far side.

**Secondary predictions:** E7-PULL > E1-PULL at matched T (~85%); E7-PULL lands between
E1 and the measured anchor (~60%) vs above the anchor (~15%; above-anchor + coverage
≈ E0 reads "over-repulsion is still just resampling"); E1@T1.5 continues the monotone
coverage-vs-PULL curve (PULL ~0.35–0.45, coverage between E1@1.2's 0.62 and E0@1.5's)
(~70%).

**Writeup destination:** §9.3.1 append with the branch outcome; central-figure spec
gains the E7 and T=1.5 points. Artifacts: `runs/modal/dmeasure_e7_gen.json`,
`artifacts/dmeasure_e7.json`.

---

## W2 pre-registration — LCB-medium base screen *(committed before running)*

**Purpose.** Size R3 before pre-registering it. W0c showed the easy strata alone are
unpowered (false-zero floor ~2–5 lucky recoveries ≈ the predicted signal). The medium
stratum is the candidate fix.

**Design.** Base completion path (the smoke-validated fenced-completion prompt from
R2), LiveCodeBench code_generation **medium** stdin population (78 problems — the full
population, no sampling), **top_p 1.0, T ∈ {0.8, 1.2}, k=50, seed 17**, fixed hardened
judge; enriched per-test pools persisted under distinct tags
(`lcb_r2_base_medium_T08/T12` — the tag now carries difficulty so landed easy pools
cannot be overwritten). The W0c false-zero fit is recomputed on the medium pools with
the same method — that floor enters R3's medium-arm null.

**Decision rule (pre-committed).**
- Medium pass@50 = 0 stratum **≥ ~60 problems with feedback richness intact** (per-test
  signal present: a majority of stratum problems show ≥1 partial-credit candidate in
  the k=50 pool) → R3 runs on **easy-stratum + medium-stratum, analyzed separately**,
  pooled only if pre-registered at W3.
- If medium coverage is so low the problems are plausibly **unreachable-at-any-k**
  rather than improbable (pass@50 near zero AND stratum partial-credit signal near
  zero), record the regime difference: recovery there tests something *stronger*, and
  a null there does not kill the easy-stratum question.
- **Power check before the W3 freeze:** with final stratum sizes and the recomputed
  false-zero floor, compute the minimum detectable recovery delta (exact
  binomial/McNemar, α=0.05 one-sided, power 0.8). If the design cannot resolve the
  pre-registered 5–20% recovery prediction, the pre-reg says so explicitly and adjusts
  n — no kill criterion that is theater.

**Predictions (recorded before running).** Base > instruct on the tail at matched T
(the R2 suppressor ordering carries over): base T=0.8 medium pass@8 ∈ [0.08, 0.20]
(~60%), pass@50 ∈ [0.20, 0.35] (~55%; instruct T=0.8 was 0.067/0.154). Stratum size at
T=0.8: ≥60 (~40%), 45–59 (~40%), <45 (~20%). T=1.2: pass@8 lower (~0.05–0.12), stratum
larger. Feedback richness intact on the stratum: ~70%.

**Writeup destination:** §9.6 extension. Artifacts:
`artifacts/phase3a_screen_lcb_r2_base_medium_T{08,12}.json`, enriched pools
`runs/modal/lcb_{cand,res}_lcb_r2_base_medium_T{08,12}.json`.

---

## W1 RESULTS (2026-07-15) — BRANCH (a): the elimination argument is STRENGTHENED — [artifacts/dmeasure_e7.json]

| cell | PULL | mean_pass | coverage | vs committed E0 |
|---|---|---|---|---|
| E7 @ T=0.8 | 0.196 | 0.285 | 0.65 | **−0.267** (E7-only 1, E0-only 17, p≈1.0) |
| E7 @ T=1.2 | 0.357 | 0.244 | 0.75 | **−0.150** (E7-only 4, E0-only 13, p=0.99) |
| E1 @ T=1.5 | 0.560 | 0.035 | 0.18 | (E0@1.5: 0.37) |
| E0 @ T=1.5 | 0.740 | 0.067 | 0.37 | — |

**Branch (a) fires exactly as pre-registered (the 55% favourite):** both E7 temps land
≤ E0 − 0.05. Explicit repulsive conditioning loses to i.i.d. by 15–27 coverage points
at matched compute; **"strictly dominated" stands as written.**

**The sharper finding: repulsion is unachievable by prompting at this scale.** The
avoidance instruction ("do not repeat this approach; take a substantially different
approach") moved PULL only **+0.020/+0.048** over E1's plain "improve it" (0.196 vs
0.176; 0.357 vs 0.309) — both still far below the measured anchor (0.491/0.594). The
decisive region (PULL ≥ anchor) stays unpopulated **because the model cannot reach
it**: told explicitly to leave the failed basin, a 1.5B generates *inside copy
territory anyway*. The elimination argument's exclusion of repulsive conditioning is
no longer a priori — it is measured: there is no prompt-level anti-correlated sampler
to build the "sample the complement" scheme out of. (E7 does sit on the escape-coverage
ordering — its extra escape bought coverage 0.65/0.75 vs E1's 0.52/0.62, the best
failure-conditioned cells yet — but the ceiling claim is untouched: the best repelled
cell is still 15 points under resampling.)

**Prediction accounting.** Primary: (a) at 55% — **CORRECT**. Secondary: E7-PULL >
E1-PULL at matched T (~85%) — held, marginally; E7-PULL between E1 and the anchor
(~60%) — held; **E1@T1.5 continues the monotone curve (~70%) — WRONG, informatively.**

**The wrong prediction is a regime boundary: the escape-distance law has a bounded
domain.** At T=1.5, escape distance jumps (E1 PULL 0.560 — past the T=1.2 anchor
neighborhood) but coverage **collapses** (0.18, far below E1@1.2's 0.62), because
per-sample competence collapses (mean_pass 0.035; E0@1.5 likewise degrades to 0.37
coverage / 0.067 mean_pass). The law — coverage monotone in PULL — holds **within the
competence regime (T ≲ 1.2)** and inverts past it: escape bought with temperature
beyond the boundary produces broken code, and spreading broken samples lands nothing.
Consequences: (i) temperature is not an unbounded escape knob — the undirected-escape
route to i.i.d. is closed not only asymptotically (W0a: never gets there) but
*practically* (pushing T hard enough to escape destroys the samples first);
(ii) the central figure's points must carry temperature labels and the law's stated
domain; (iii) the E0 anchor row extends to T=1.5: PULL 0.409/0.491/0.594/**0.740**,
coverage 0.65/0.92/0.90/**0.37** — i.i.d. itself falls off the same cliff.

---

## W2 RESULTS (2026-07-15) — the medium stratum is the R3 instrument; the easy strata are formally retired from primary analysis

**Screens** ([artifacts/phase3a_screen_lcb_r2_base_medium_T{08,12}.json]; enriched
pools persisted): base medium **T=0.8**: pass@1 0.013 / pass@8 0.048 / pass@50 0.128
(headroom +0.080); **T=1.2**: 0.001 / 0.006 / 0.026 (+0.020). Neither qualifies as a
3b training cell — irrelevant; W2's job was stratum sizing.

| cell | stratum (0/50) | x=1 / x=2 | richness (≥1 partial-credit) | E[B1-50 lucky] |
|---|---|---|---|---|
| medium T=0.8 | **68/78** | 5 / 2 | **66/68 (97%)**, 1,400 partial cands, median 15 tests | **2.01** (pure-Beta 2.13) |
| medium T=1.2 | 76/78 | 1 / 1 | 49/76 (64%) | 0.82 (fit-unstable) |

Stratum overlap T0.8 ∩ T1.2 = 67.

**The pre-committed first branch fires on T=0.8 medium:** stratum 68 ≥ 60 **and**
feedback richness intact (97%). R3 runs on easy + medium strata, analyzed separately.
The T=1.2 medium cell is **not** an instrument (near-total failure + degraded
richness) — and it independently corroborates W1's bounded-domain finding: the
competence cliff that appears at T=1.5 on HumanEval-easy arrives at **T=1.2 on
LCB-medium**; the boundary descends with difficulty.

**Power check (pre-committed; Monte-Carlo exact paired McNemar, one-sided α=0.05,
20k trials).** Minimum detectable ABSTRACT recovery rate r:

| stratum | floor rate | r=0.05 | 0.08 | 0.10 | 0.13 | 0.15 | 0.20 |
|---|---|---|---|---|---|---|---|
| medium n=68 | 0.030 | 0.05 | 0.21 | 0.36 | 0.59 | **0.73** | **0.92** |
| easy n=19 | 0.189 | — | — | 0.00 (r=.10) | — | 0.02 (r=.20) | 0.10 (r=.30) / 0.25 (r=.40) |

Consequences, binding on W3: (i) **primary analysis = medium stratum only** — the easy
stratum cannot resolve any effect in the plausible range (power 0.25 at r=0.40) and is
demoted to exploratory, reported unpowered; (ii) the design resolves the **upper half**
of the pre-registered 5–20% band — a null at α=0.05 forecloses r ≳ 0.15; **r ∈ [0.05,
0.13) is pre-declared unresolvable by this design** (stated, not spun); (iii) the W3
config tension dissolves — base T=0.8 keeps the coverage-dominant easy cell for
D2c/BEST-SO-FAR *and* supplies the 68-problem medium stratum for R3 from the same
frozen config.

**Prediction accounting (all recorded in the W2 pre-reg above).** pass@8 band **WRONG**
(0.048 < [0.08, 0.20]); pass@50 band **WRONG** (0.128 < [0.20, 0.35]); base > instruct
at matched T on medium **WRONG — the suppressor ordering inverts on medium** (base
0.048/0.128 vs instruct 0.067/0.154): the base-tail advantage is an easy-tier
phenomenon, and on harder problems instruct's SFT structure outweighs its entropy
collapse — a mechanism note feeding the "what does instruct-tuning suppress"
want-to-see. Stratum ≥ 60 (~40% odds) **CORRECT** (68); richness intact (~70%)
**CORRECT** (97%); T=1.2 direction **CORRECT**, magnitude far beyond expectation
(competence cliff).
