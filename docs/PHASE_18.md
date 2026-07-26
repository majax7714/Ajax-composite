# Phase 18 — the coverage channel: intervening on it, after finding out what it is

*Charter opened 2026-07-25. Ninth iteration of the unattended loop
([AUTONOMOUS_LOOP.md], Amendments 1–4). Author instruction: "youre good to continue the
loop targeting coverage channel." Append-only; pre-registration frozen before spend.*

---

## 0. What the author asked for, and what the free work did to it

The instruction named the target: the **coverage channel**, which §0.4 carried as *"the
strongest live pointer in the record"* after Phase 16's free decomposition found the SINK
dominated by coverage loss (Coder-1.5B 0.636 → 0.205 pass@8, −0.432, against a mean-frac
drop of −0.064) with **no phase having intervened on it**.

Loop step 3 lands free amendments before spend. Seven of them landed here, and they did
not leave the pointer as they found it. **Three of §0.4's load-bearing statements about
coverage are wrong or unlicensed, and one hypothesis the loop generated in the middle of
this very phase was refuted by the record's own standard control within the hour.** The
paid cell below is designed against what survived, not against what was written yesterday.

That is the reason a phase does P0 first. It is also the reason this charter's §1 is
longer than its §3.

---

## 1. P0 — free, landed and committed before this charter (commit `f581337`)

Seven analyses over already-committed pools. Artifacts: `h18_p0_coverage.json`,
`h18_p0_compress.json`, `h18_p0_compress_battery.json`, `h18_p0_predict.json`,
`h18_p0_coverage_model.json`.

### P0.1 — the coverage effect finally has an error bar *(and it is real)*

The −0.432 was quoted from one seed at k=8 with no interval. Recomputed on **matched-k**
arms the record already owned — the Phase-11 powered targeting sweep is a k=24 i.i.d. arm
covering all 44 cell problems — using the unbiased pass@k estimator, with a
case-resampling bootstrap over problems:

| k | i.i.d. | cond | Δ | CI95 | |
|---|---|---|---|---|---|
| 1 | 0.2377 | 0.0653 | −0.1723 | [−0.2348, −0.1127] | *** |
| 2 | 0.3594 | 0.1142 | −0.2451 | [−0.3283, −0.1673] | *** |
| 4 | 0.4796 | 0.1851 | −0.2945 | [−0.3976, −0.1979] | *** |
| 8 | 0.5735 | 0.2792 | −0.2942 | [−0.4085, −0.1824] | *** |
| 16 | 0.6329 | 0.3921 | −0.2407 | [−0.3819, −0.1011] | *** |
| 24 | 0.6591 | 0.4545 | −0.2045 | [−0.3636, −0.0455] | *** |

The effect is significant at every k. It also **peaks near k = 4–8 and narrows after**, so
"conditioning costs the model half its coverage" is a statement about small candidate
budgets; at k = 24 the model recovers about a third of the gap. Mean frac over the same
arms: 0.4573 → 0.3960, **−0.0614**, CI95 [−0.1185, −0.0038].

### P0.2 — the coverage currency is noisier across seeds than the record assumed

The same cell, same problems, same prompt (Phase 16 VERB-A is asserted byte-identical to
`_d2c_context`), at three independent seeds, at matched k = 8:

| seed | source | cov@8 | mean frac |
|---|---|---|---|
| 173 | Phase 11 cell | 0.2045 | 0.4067 |
| 233 | Phase 16 VERB-A | 0.3182 | 0.4292 |
| 239 | Phase 17 VERB-A (subsampled) | 0.2786 | 0.3960 |

Spread **0.1137** on coverage against 0.0332 on mean frac. As a fraction of each
currency's own effect that is 26% vs 52%, so coverage is not *relatively* noisier — but
the absolute swing is large, and **§0.4 quoted the single most extreme of the three**
without saying so. Any future coverage number is quoted with its seed.

### P0.3 — the damage is a *compression*, not a slide

Per-candidate frac distribution, i.i.d. vs conditioned, k = 24, pooled over the 44
problems:

| band | i.i.d. | cond | shift |
|---|---|---|---|
| correct (1.0) | 0.2377 | 0.0653 | **−0.1723** |
| near [0.75,1.0) | 0.0795 | 0.0341 | −0.0455 |
| partial [0.25,0.75) | 0.2907 | 0.6316 | **+0.3409** |
| weak (0,0.25) | 0.1117 | 0.0587 | −0.0530 |
| zero (0.0) | 0.2803 | 0.2102 | **−0.0701** |

Conditioning **destroys the top of the distribution and improves the bottom**. The
fully-correct rate falls 72.5% relative; the zero rate *falls too*. Mean frac moves only
−13.4% **because these two effects partially cancel inside it** — the currency every sink
number in this record is quoted in is the one statistic that hides this.

Per problem at k = 24: conditioning **loses 12 problems outright and recovers 3**. On the
12 it loses, mean frac only falls 0.4623 → 0.3727. *The model still scores. It stops
finishing.*

### P0.4 — ⚠ **the below-both-nulls criterion does not survive the change of currency**

The SINK is defined as below **both** nulls — the model's own i.i.d. *and* the copy null.
Phase 10 P0.2 restored that definition after it had silently drifted once. It must not be
allowed to drift again by a change of units, so it was evaluated in both:

| currency | i.i.d. null | copy null | cond | < i.i.d. | < copy | **SINK** |
|---|---|---|---|---|---|---|
| mean frac | 0.4573 | 0.4589 | 0.3960 | yes | yes | **TRUE** |
| coverage@24 | 0.6591 | **0.0000** | 0.4545 | yes | **no** | **FALSE** |

**0 of 44 artifacts fully pass** — and, checked in P0.5, 0 of the artifacts in *all eight*
committed matched cells fully pass. So the copy null scores coverage **0.0000 by
construction** everywhere in this record, and the conditioned arm beats it enormously.

> **Consequence, and a correction to §0.4:** *"the sink's dominant channel is coverage"* is
> **not licensed** as a restatement of claim 8. Claim 8 is a **mean-frac** statement and it
> cannot be re-expressed in a currency where its own second null is degenerate. What is
> licensed: conditioning's damage is **concentrated in coverage, measured against the
> i.i.d. null alone** — a different and weaker sentence than the one §0.4 carries.

### P0.5 — a compression law, universal across all eight committed matched cells

Per problem, with gap = artifact frac − own i.i.d. and shift = conditioned − own i.i.d.,
fit `shift = a + b·gap`:

| cell | status | n | slope b [CI95] | intercept a [CI95] | R² |
|---|---|---|---|---|---|
| Coder-1.5B (P11) | SINKS | 44 | +0.637 [+0.47,+0.79] | −0.0564 [−0.089,−0.022] | 0.697 |
| Coder-3B (P11) | SINKS | 39 | +0.787 [+0.62,+0.96] | −0.0577 [−0.095,−0.020] | 0.775 |
| Coder-7B (R5 true match) | clean | 29 | +0.555 [+0.34,+0.80] | −0.0197 [−0.076,+0.033] | 0.453 |
| DeepSeek-1.3B (P7 M1) | clean | 39 | +0.784 [+0.69,+0.91] | +0.0105 [−0.015,+0.032] | 0.916 |
| **general-Qwen-1.5B (P7 M2) — TWIN** | clean | 28 | +0.619 [+0.48,+0.80] | **−0.0398 [−0.079,−0.002]** | 0.715 |
| StarCoder2-3B (P7 M3) | clean | 39 | +0.881 [+0.70,+1.10] | −0.0208 [−0.067,+0.022] | 0.756 |
| Coder-7B (P7 M4, retracted) | clean | 20 | +0.470 [+0.33,+0.74] | −0.1101 [−0.177,−0.039] | 0.399 |
| Coder-0.5B (P7 M5) — OPEN rung | unadj. | 43 | +0.905 [+0.79,+1.05] | −0.0293 [−0.052,−0.009] | 0.919 |

**Every model is pulled 47–90% of the way from its own quality toward the artifact's**,
sinking or clean, Coder-diet or not, at R² up to 0.92. That is the record's first
quantified statement of a relationship D2a/D2b described only qualitatively ("conditioning
relocates the distribution").

**And a hypothesis of this loop's own making, refuted inside the hour it was born.** On the
first four cells run, the intercept looked like the diet's signature: SINKS at −0.056 and
−0.058, both CI-excluding zero; clean cells including zero. The reading written down was
*H-OFFSET — compression is universal, the sink is a constant offset on it.* Adding the
remaining four committed cells **kills it**: the **architecture twin**, general-Qwen-1.5B —
same base, verified same 28L × 12H, same scale as Coder-1.5B, and measured **clean** —
also excludes zero, at −0.0398. So does Coder-0.5B. So does the retracted M4, at −0.110,
the *largest* magnitude in the table.

> This is the **Phase 15 lesson, recurring**: a cross-model quantity claimed to track a
> behavioural property survived a four-cell cut and died to the pair that differs only in
> the variable the claim names. It cost nothing this time only because the twin's pool was
> already committed. **The intercept is not a diet signature; it is a re-parameterisation
> of each cell's own at-match `cond − iid`, and it inherits everything that number
> inherits — including M4's failure to replicate.**

### P0.6 — the predictor and its tolerances, in units of measured spread

Fit on the at-match cell with both arms at k = 24: `shift = −0.0624 + 0.6559·gap`,
residual SD 0.0960. Symmetry of compression above vs below match: slope difference CI95
**[−0.4966, +0.3526]** — *includes zero, but this check is **underpowered**, not passed;
it does not license an assumption of symmetry, only fails to refute one.* Two candidate
out-of-sample bands were priced and then **not chartered**: their problem sets overlap the
fit cell by 58% and 84%, so they would not have been out-of-sample in the way that matters.
Recorded so the reasoning is auditable rather than invisible.

### P0.7 — the 7B zero is real; two distributional models fail, one of them void

**(a) The 7B "exactly 0.000" is not a coincidence of counts.** A net-zero coverage delta
can hide arbitrary churn. It does not here:

| cell | solved i.i.d. → cond | net | lost | gained | **churn** |
|---|---|---|---|---|---|
| Coder-1.5B | 28 → 9 | −19 | 21 | 2 | 23 |
| Coder-3B | 31 → 15 | −16 | 16 | 0 | 16 |
| **Coder-7B (R5 true match)** | 23 → 23 | **+0** | **1** | **1** | **2** |
| DeepSeek-1.3B (clean) | 15 → 7 | −8 | 9 | 1 | 10 |
| general-Qwen-1.5B (TWIN, clean) | 11 → 5 | −6 | 7 | 1 | 8 |
| StarCoder2-3B (clean) | 17 → 9 | −8 | 9 | 1 | 10 |
| **Coder-7B (M4, retracted)** | 16 → 14 | −2 | 2 | 0 | **2** |
| Coder-0.5B | 6 → 1 | −5 | 5 | 0 | 5 |

Two problems moved at 7B, out of 29. It replicates at the *second* 7B cell (churn 2/20).
**7B is genuinely untouched in coverage, not merely net-neutral.**

**(b) Both simulations fail, and one was ill-posed by construction — recorded, not
deleted.** Predicting conditioned coverage from each cell's own fitted (a, b): S1
(location shift, spread preserved) has MAE 0.2418 and **under-predicts coverage in 7 of 8
cells** — models *retain* more coverage than a uniform downward slide permits, i.e.
candidates escape the pull. S2 (shrinkage toward the artifact) returns **exactly 0.0000 for
every cell, for any input**, because no artifact fully passes anywhere: a rule that cannot
vary with the data. **Third instance of that defect class in this record** (Phase 13 S2,
Phase 14, §8 entry 8). It is kept in the script and artifact under a `_S2_VOID` label
because deleting degenerate arms is how a record loses the ability to see the pattern.

### What P0 leaves standing

1. Coverage loss under conditioning is **large, real, and CI-backed** at the flagship cell.
2. It is **universal at ≤3B across every family and diet measured** — clean DeepSeek −0.205,
   clean architecture twin −0.215, clean StarCoder2 −0.205 — and **absent at 7B in both**
   committed 7B cells.
3. It therefore **does not track the Coder diet, and is not the sink's mechanism.** It is a
   *different phenomenon* that had been conflated with the sink by a shared measurement.
4. It has still **never been intervened on.** That part of §0.4 stands.

---

## 2. The question, and why it is next

> **Does temperature — the record's one validated lever on coverage — restore the coverage
> that conditioning destroys? And if it does, does the SINK follow?**

Three reasons this is the phase, chosen by full-record review rather than as Phase 17's
sequel (§10 practice; the author's standing instruction on phase selection):

**(a) It is the intervention the author asked for, aimed at what P0 found rather than at
what §0.4 said.** Coverage is now a characterised, error-barred, cross-family phenomenon
with no manipulation behind it. Claim 13 — *"temperature is a dose-responsive
anti-anchoring intervention"* — is the only validated coverage lever this record owns.

**(b) Claim 13's evidence does not reach this cell, and that gap is exactly the size of a
phase.** D2b measured T 0.8 → 1.2 lifting coverage **only for anchored conditions**
(E0 −0.02 flat, E1 **+0.10**, E2 +0.18, the more-anchored condition benefiting ~2×). That
was on **HumanEval**, on **fail-conditioned** artifacts, **without a matched i.i.d. null at
each temperature**, and **never on a sink cell**. The sink cells are LCB, at matched
partial-credit artifacts. The novel statistic here is not coverage(T) — it is
**Δcov(T) = cond(T) − iid(T)**, with the null re-measured at every temperature, which D2b
never carried.

**(c) It is the direct successor to Phase 17 on the other lever.** P17 took the escape
law's *largest* lever (the instruction verb, PULL ≤0.127) and found it **inert on the
sink**. Temperature is the escape law's *other* lever and the only one shown to move
coverage. If temperature moves coverage but not the sink, the dissociation Phase 17 opened
is closed on both levers and the two claims are mechanically separate objects. If it moves
both, P17's null becomes the anomaly and the record has to explain why one lever works and
the larger one does not.

**Rival readings that this cell can return, and which are not failures:** temperature may
fail to lift conditioned coverage on LCB at all, which is a **scope restriction on a LIVE
claim** (13) whose evidence is HumanEval-only. Or both arms may collapse, which locates the
LCB temperature boundary below 1.0 — tighter than §9.3.1 W2's read.

### The domain caveat, pre-registered rather than discovered afterwards

§9.3 bounds the escape law to **T ≲ 1.2 on HumanEval** and states that *"the boundary
descends with difficulty — T = 1.2 already collapses on LCB-medium."* **This cell is LCB.**
So **T = 1.2 is an explicitly out-of-domain probe here**, frozen as such before the run:
if T = 1.2 degrades *both* arms it is a **confirmation of the frozen domain bound**, not a
failed intervention, and adjudication rests on **T = 1.0**. This is written down now so it
cannot be used as an excuse later.

---

## 3. Design

**Cell.** Qwen2.5-Coder-1.5B (`df3ce67c…`), the P11 problem set — n = 44 — with the P11
matched artifact set (mean 0.4589, Δ_art ≈ 0), reconstructed by the frozen selector and
asserted against the committed `mean_art` before use. The flagship sink cell: the most
measured cell in the record, and the one all of P0 is fitted on.

**Arms.** 2 × 3 = **6 arms**: {conditioned, i.i.d.} × T ∈ {**0.8**, **1.0**, **1.2**},
k = 24 candidates per problem. 6 × 44 × 24 = **6336 generations**.

**Conditioned prompt** is `_d2c_context` unchanged — the same clause behind every sink
number in this journal, and asserted byte-identical in code (the Phase 16/17 assert is
reused). Only temperature varies. `top_p = 1.0` throughout, as in every prior cell.

**All six arms are generated fresh at one new seed (`P18_SEED = 281`).** The T = 0.8 arms
are *re-generated* rather than taken from cache even though committed arms exist, because
**P0.2 measured a 0.114 seed-to-seed swing in coverage** — larger than several of the
effects this phase is trying to resolve. Mixing a cached T = 0.8 with fresh T = 1.0/1.2
would confound the temperature contrast with seed noise. The cost of that decision is
~2112 generations, ≈ $0.30, and it buys a seed-internally-matched ladder plus a
**rerun-stability check** on the record's flagship cell, which loop step 8 requires anyway.

**Primary statistic:** Δcov(T) = coverage@24(cond, T) − coverage@24(i.i.d., T), unbiased
pass@k estimator, bootstrap CI over problems (seed 283, B = 4000).
**Secondary, reported at every T:** mean frac cond − i.i.d.; below-both-nulls in mean frac;
achieved Δ_art at each T (**the matched-relation rule: raising T moves the model's own
i.i.d. quality, therefore moves the cell's relational position — this is measured and
reported, not assumed away**); parse rate; per-candidate band distribution (P0.3's table).

### Frozen decision rules — CI-referenced, no round numbers

Three phases have now been damaged by thresholds set as round numbers against unexamined
spread (Phase 10 R3's ±0.03 vs SE 0.028; Phase 16's ≤ −0.03 vs a CI 0.123 wide, failing by
0.0004 and costing the phase; §8 entry 9). Every gate below is expressed against an
interval **measured in P0 and frozen in code before the run**:

```
committed references (h18_p0_coverage.json, artifacts/h11_coder1p5b.json), k=24, n=44:
    cov_iid@24    0.6591   CI95 [0.5227, 0.7955]
    cov_cond@24   0.4545   CI95 [0.3182, 0.6136]
    Δcov@24      -0.2045   CI95 [-0.3636, -0.0455]
    meanfrac cond-iid  -0.0614  CI95 [-0.1185, -0.0038]
    P11 committed sink CI95  [-0.1258, -0.0028]
```

- **VALIDITY (replication) gate.** The fresh **T = 0.8** arms must reproduce the committed
  cell: Δcov(0.8) inside [−0.3636, −0.0455] **and** mean-frac cond−iid inside
  [−0.1258, −0.0028]. If either falls outside, the run is a **non-replication**, no branch
  is adjudicated, and it is recorded as such. *(Unlike Phase 16's gate this one cannot fail
  by a hair against an arbitrary number: it is the committed interval itself.)*
- **COVERAGE RESCUED** at temperature T ⟺ Δcov(T) lies **above** −0.0455, the upper bound of
  the committed Δcov CI95 — i.e. outside the interval on the rescue side.
- **SINK UNMOVED** at T ⟺ mean-frac cond−iid at T lies **inside** P11's committed
  [−0.1258, −0.0028].
- **BOTH ARMS COLLAPSED** at T ⟺ i.i.d. coverage at T falls **below 0.5227**, the lower
  bound of the committed i.i.d. coverage CI95. *(Pre-registered as the out-of-domain
  signature, expected at T = 1.2 and not at T = 1.0.)*

### Branches, with odds committed before the run

| | branch | reading | odds |
|---|---|---|---|
| **A** | coverage RESCUED at T=1.0 **and** sink moves out of its committed CI | coverage loss and the sink are one object; temperature moves both; P17's verb null becomes the anomaly to explain | **15%** |
| **B** | coverage RESCUED at T=1.0 **and** sink UNMOVED | the two dissociate **under intervention**, not just under measurement — claim 6's lever governs coverage, claim 8 is untouched by either escape lever | **40%** |
| **C** | coverage NOT rescued and sink unmoved (both inside committed intervals) | **scope restriction on claim 13** — temperature's dose-response was measured on HumanEval fail-conditioning and does not reach LCB at match | **30%** |
| **D** | BOTH ARMS COLLAPSED at T=1.0 | the LCB temperature boundary sits below 1.0, tighter than §9.3.1 W2; instrument/domain result, adjudication void at 1.0 | **15%** |

B is the favourite because P17 established that the *larger* escape lever is inert on the
sink while D2b established that temperature *does* move anchored coverage; B is simply both
of those being true at once. C is priced high — nearly as high — because D2b's dose-response
is HumanEval-only and this record has twice found a cross-benchmark generalisation fail.
A is priced low and deliberately *not* at 5%: if it fires it is the most informative
outcome in the phase, and Phase 10 already taught this loop that its 5%-priced branches
fire (§ AUTONOMOUS_LOOP Amendment 1).

**T = 1.2 is not in the branch table.** It is a domain probe, pre-registered as out-of-domain
per §2, and reported for its own sake.

### Kill criteria

- Any arm's **parse rate below 0.95** (committed cells run 0.99–1.00) → that temperature is
  an instrument failure, reported as invalid and **not** retuned in-phase.
- **Achieved Δ_art at T = 1.0 outside ±0.05** of its T = 0.8 value → the temperature change
  has moved the cell off its relational position enough that the comparison is confounded;
  reported as a position confound, with the measured drift, and the coverage comparison is
  carried as descriptive only.
- Validity gate failure (above) → non-replication, no adjudication, no retune.

### The smoke step, and why it is skipped here *(documented fork, Amendment 1)*

Loop step 5 requires the cheapest possible cell first — template, context length, judge
semantics. **Every one of those is byte-identical to Phase 17's**, which ran three days'
worth of cells on this exact model, problem set, k, and judge: the conditioned prompt is
`_d2c_context` with an in-code assert, the context length and `max_tokens` are unchanged,
and `h1_lcb_exec` is the same all-cases judge. **The only new variable in this phase is a
single float passed to `SamplingParams`.**

What a smoke *would* have caught is the one genuine unknown — whether higher temperature
produces longer outputs that hit `max_tokens = 1536` or degrade parse rates. Two things
bound that instead: the pre-registered **parse-rate kill criterion (< 0.95)**, and
**per-arm volume-first persistence**, so each of the six arms is checkpointed as it lands
and the exposure of a bad temperature is one arm (≈ $0.15), not the phase.

*Alternative considered and rejected:* a k = 4, n = 10 smoke at T = 1.2 first (≈ $0.02).
Rejected because at n = 10 × k = 4 the parse-rate estimate has a half-width wider than
the 0.05 the kill criterion turns on, so it could not have fired the gate it exists to
pre-test. A smoke that cannot fail its own gate is the Phase-14 defect in miniature.

### Cost

**Estimate $0.70–1.40.** Basis: Phase 17 ran 3984 generations of the same model class,
same k, same judge, for a **read** $0.551; 6336 generations is 1.59× that, giving ≈$0.88
central, with the band widened for the two higher-temperature arms producing longer
outputs. Month-to-date workspace spend read **$83.81** (`modal billing report`,
2026-07-25) against Amendment 3's **$100 report / $120 hard stop**; §4's guard
($estimate + $30 < $200 cap) is satisfied with wide margin. Loop total to date $5.77.

**Estimator accountability (Amendment 2):** the last seven generation estimates have all
landed inside their bands. This one is reconciled against the bill at close like the rest.

---

## 4. Pre-registration freeze

Frozen at commit `4abb0b1`, **before** any Phase-18 generation
ran. P0 was committed separately and earlier, at `f581337`.

---
