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

---

## W3 — THE FROZEN 3b PRE-REGISTRATION (2026-07-15; committed before any W4 run)

*Everything below is fixed. W4 runs it without new design decisions; deviations require
an appended amendment with its own date and rationale, never an edit.*

### 0. Config freeze

**Generator:** Qwen/Qwen2.5-Coder-1.5B (base, fenced-completion path, smoke-validated
in R2), **T = 0.8, top_p = 1.0, seed 17, max_tokens 1536**. **Judge:** the hardened
all-case subprocess judge (unchanged from R2/W2). **No learned verifier anywhere**
(H1-kill propagation): every selection is likelihood-free — execution frac_tests
(oracle-first where stated) or nothing. **Benchmarks:** LCB-easy base T=0.8 pool
(coverage-dominant cell: pass@8 0.566 / headroom +0.197 — D2c/E6, BEST-SO-FAR, R3
exploratory arm) + LCB-medium base T=0.8 (R3 primary stratum, n=68). **The flagged
config tension is resolved by W2's power check:** no easy stratum is viable as a
primary instrument at any temperature (power ≤ 0.25 at r = 0.40), so the smallest-easy-
stratum objection to base T=0.8 is moot; the medium stratum from the *same* frozen
config is the primary instrument.

### 1. R3 — conditional reachability, four arms (the Olausson decomposition)

**Strata.** Primary: medium-stratum, **n = 68** (pass@50 = 0 in the committed base
T=0.8 medium pool). Exploratory (unpowered, reported as such): easy-stratum, **n = 19**.
Analyzed separately; **no pooling** (pooling was not pre-registered and stays out).

**Per-problem artifact** (fixed rule): the committed pool candidate with the highest
frac_tests (ties → lowest candidate index). Problems whose candidates are all
frac = 0 use candidate index 0. **Trace capture** (one re-execution of the 87
artifacts, remote): first failing test case → (case index, stdin, expected output,
actual output/error), each field truncated to 512 chars.

**Arms** (each: 50 fresh draws/problem at the frozen sampling config; context inserted
before the final ` ```python ` fence of the base prompt):

- **B1-50** — no context (fresh i.i.d. control; the W0c/W2 floor: E ≈ 2.0 lucky
  recoveries on the medium stratum, ≈ 3.6 on easy).
- **ANCHOR** — "A previous attempt:" + artifact code + "This attempt failed {n_failed}
  of {n_tests} tests. Write a corrected complete program."
- **ABSTRACT-trace** — *no code.* "A previous attempt failed {n_failed} of {n_tests}
  tests. First failing test: input / expected output / actual output" (verbatim
  templated trace) + "Write a correct complete program." The feedback **ceiling**: no
  model in the loop.
- **ABSTRACT-model** — *no code.* The same trace given to
  Qwen2.5-Coder-1.5B-**Instruct** (same family — deployable, no oracle) with: "In 2–4
  sentences, state what is wrong with the approach and what a correct approach must do
  differently. Do not write code." (T=0, ≤160 tokens, code fences stripped); its output
  replaces the raw trace in the prompt. The **deployable channel**: measures whether
  1.5B-generated direction retains the trace's value (Olausson ledger entry).

**Smoke gate (pre-registered, before the full run):** 8 medium-stratum problems × 4
arms × 8 draws — well-formed code ≥ 85%, degenerate ≤ 10%; formatting fixes are
plumbing and re-smoke; any semantic change is an amendment.

**Recovery** = ≥ 1 of the 50 draws passes all tests. **PULL is recorded for every R3
generation** (edit-similarity vs the artifact code, all four arms including B1-50 —
B1-50's PULL is the stratum's i.i.d. anchor), so the off-the-curve prediction is
placeable either way.

**Decision rules (frozen):**
- **Primary:** ABSTRACT-trace > B1-50, **paired one-sided exact McNemar on the
  medium stratum, α = 0.05**. Null floor stated: ≈ 2.0 lucky B1-50 recoveries (3%/
  problem). **Power envelope declared: 80% power only at r ≳ 0.17 (73% at r = 0.15,
  92% at r = 0.20). A null forecloses r ≳ 0.15 at this scale/config; r ∈ [0.05, 0.13)
  is unresolvable by this design — pre-declared, not spun.**
- **Secondary:** ABSTRACT-model vs ABSTRACT-trace (paired; the "can the model make its
  own direction" gap); ABSTRACT-* vs ANCHOR (the law's prediction: direction beats
  proximity); all four arms' PULL/coverage points placed on the central figure.
- **Off-the-curve mechanism prediction:** on a pass@50 = 0 stratum, spread cannot land
  where i.i.d. never lands — R3 success requires **relocating per-sample mass**
  (breaking D2b flatness). A *successful* ABSTRACT-trace sits **off** the
  coverage-vs-PULL curve: PULL comparable to E1/E2 cells, coverage above the law's
  line.
- **Recovery validation protocol** (every stratum recovery): (a) judge **rerun**
  (flakiness exclusion); (b) **contamination audit** — LCB contest date vs the base
  model's plausible training window (flag pre-2025 problems as contamination-possible;
  LCB's own control is dated against instruct releases, not our exposure) + AST-level
  dissimilarity of the recovery vs the problem's 50 failed pool draws (a recovery
  shaped like the failures is in-distribution generation, not memorization); classify
  "memorization-unlocked-by-feedback" separately — reportable, different claim;
  (c) **error-type stratification** (How-Many-Tries ledger check): classify each
  stratum artifact wrong_answer vs runtime; prediction below.

**Predictions with odds (recorded at freeze):**
- ABSTRACT-trace significant at α = 0.05 on medium (r ≳ 0.15): **15%**;
  positive-but-unresolvable (net delta > 0, p ≥ 0.05): **45%**; ≈ 0 or negative:
  **40%**. (The trace is oracle-grade, but the binding constraint is 1.5B competence
  on medium — W2 measured pass@8 0.048.)
- ANCHOR ≤ B1-50 on medium (the law: proximity without direction buys nothing on a
  0/50 stratum): **75%**.
- ABSTRACT-model ≤ ABSTRACT-trace: **80%** (1.5B interpretation degrades the raw
  signal).
- Conditional: *if* ABSTRACT-trace fires significant, its point sits off the curve:
  **70%**.
- Error-type check: recoveries (any arm) skew toward runtime-error artifacts over
  wrong_answer artifacts: **60%**.

### 2. D2c/E6 — partial-credit conditioning (the BEST-SO-FAR premise test; runs first)

**Problem set (fixed):** the **44** easy-pool problems holding ≥ 1 candidate in the
40–60% frac band ([artifacts/w0b_copy_null.json]). **Artifact:** the band candidate
with frac closest to 0.5 (ties → lowest index). **Generation:** 8 draws/problem,
frozen sampling config, framing: "A previous attempt:" + code + "This attempt passed
{n_passed} of {n_tests} tests. Improve it so that all tests pass."

**Metrics & nulls (from W0b):** paired per-problem mean frac(gen) vs (i) **copy-null**
f_a and (ii) **i.i.d.-null** (that problem's pool mean frac). Copy-fidelity
(PULL vs artifact) is recorded — the 83–98% fidelity regime was measured on
HumanEval/instruct, not LCB/base; if fidelity here is materially lower, that is
reported alongside (the nulls stand as frozen; the fidelity number contextualizes).

**Verdict branches (frozen):** **CLIMB** — Wilcoxon one-sided p < 0.05 over copy-null
AND over i.i.d.-null → the attractor does more than copy; BEST-alone is alive and
BEST-SO-FAR is a bigger result than scoped (**~20%**). **FLAT** — neither cleared →
BEST-alone dead (hold-at-best confirmed); BEST+ABSTRACT carries the phase (**~65%**).
**SINK** — significantly below copy-null → conditioning on partials is actively
harmful (**~15%**).

### 3. BEST-SO-FAR — aim the attractor at a success (runs last)

**Problem set (fixed):** the **30** easy-pool problems whose first-8 committed
candidates contain no pass and ≥ 1 partial (the refinement regime, selection from the
committed pool only). **Conditions** (single-step, 8 fresh draws each, matched
compute; history = the problem's first-8 committed candidates): **B1** (no context) /
**LAST** (candidate #8) / **BEST** (highest-frac of first 8, oracle-selected by
frac_tests) / **ABSTRACT** (trace of BEST's first failing test, no code) /
**BEST+ABSTRACT** (BEST's code + that trace). **Metrics:** primary any-pass coverage
of the 8 draws, paired vs B1; secondary mean frac(gen). **Predictions** (Addendum III
§5 revised table, stands): BEST > LAST **80%**; BEST ≈ B1 hold-at-best; ABSTRACT >
BEST **60%**; BEST+ABSTRACT the top condition **55%**. D2c gates interpretation, not
execution: if D2c lands FLAT/SINK, BEST-alone's null is *expected*, and BEST+ABSTRACT
is the phase's live condition. Recoveries validated per the R3 protocol (rerun +
contamination; these are 0-of-8 problems, not 0-of-50, so the false-zero caveat is
stated with the result).

### 4. W4 execution order, budget, and hygiene

Smoke gate → **D2c/E6** (44 × 8 = 352 gens) → **R3** (4 arms × 87 problems × 50 =
17,400 gens + 87 trace captures + 87 abstractions) → **BEST-SO-FAR** (5 × 30 × 8 =
1,200 gens). Judging via the hardened judge; every stage persists its generation pool
before judging (outage insurance); all launches `modal run --detach` per the §8
operational ledger. Estimated GPU: ~2–4 L4-hours total. Artifacts:
`artifacts/r3_smoke.json`, `artifacts/dmeasure_d2c_partial_credit.json`,
`artifacts/r3_conditional_reachability.json`, `artifacts/bestsofar.json`; pools under
`runs/modal/r3_*`, `runs/modal/d2c_*`, `runs/modal/bsf_*`.

**Writeup destinations:** D2c → §9.3.1/§9.4 append; R3 → new §9.7 (the phase verdict);
BEST-SO-FAR → §9.4 append; every outcome with its prediction accounting.
