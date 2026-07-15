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
