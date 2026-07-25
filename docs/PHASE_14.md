# Phase 14 — head ablation, dose-response: is there a *targeted* effect at matched capability cost?

*Charter opened 2026-07-25. Fifth iteration of the unattended loop
([AUTONOMOUS_LOOP.md], Amendment 1). Append-only; pre-registration frozen before spend.*

## 0. What Phase 13 left, and the confound it exposed

Phase 13 S2 ablated K = 16 of Coder-1.5B's 336 heads and destroyed the model
(conditioned 0.022 top-K / 0.159 random-K against an i.i.d. arm of 0.472). Branch C:
instrument miss, K deliberately **not** retuned in-phase.

The confound it exposed is the real content: **ablating any important head costs general
capability**, and capability loss moves the sink on its own. Comparing top-K against
random-K **at matched K** therefore compares two different capability levels. The
comparison has to be made **at matched capability cost**.

Phase 13 S1 supplies the motivation: artifact attention is more *concentrated* in
sinking models (Gini +0.05–0.06 across both pairs). If that concentration is
load-bearing, removing the concentrated heads should move the sink **beyond** what their
capability cost explains. If it is incidental, it should not.

## 1. Design — a dose-response in (capability, sink) space

**Model:** Coder-1.5B, HF path — validated in Phase 13 (B1 reproduced the sink at
−0.0613 against vLLM's −0.0522, same problems and artifacts).

**Sweep:** K ∈ **{1, 2, 4, 8}**, two arms per K:

- **TOP-K** — the K highest artifact-attention heads from the S1 ranking.
- **RND-K** — K heads sampled from the complement of the top-16, seed-fixed (191),
  **nested** so RND-1 ⊂ RND-2 ⊂ RND-4 ⊂ RND-8 (as TOP-K is by construction), making the
  two curves comparable dose-for-dose.

**Anchors reused, free:** Phase 13's `B0_iid` (0.4723) and `B1_cond` (0.3976, sink
−0.0613) are the cached K = 0 points for both curves. Same problems (n = 44), same
artifacts, same seed, same `max_new_tokens`.

**The analysis.** Each run yields a point `(conditioned mean frac, sink = cond −
artifact)`. Plot both arms in that plane. Ablation that acts *only* through general
capability puts both arms on **one** curve. A targeted effect puts TOP-K **off** it.

Adjudication compares the arms **at matched conditioned performance**, not at matched K:
for each TOP-K point, linearly interpolate the RND curve at the same conditioned mean
frac and take `Δ = sink(TOP) − sink(RND_interpolated)`. Reported as the mean of the
interpolable points and their signs.

## 2. Pre-registered predictions

| # | branch | reading | odds |
|---|---|---|---|
| **A** | TOP-K sits **above** the RND curve (less sink at matched capability), mean Δ ≥ +0.02 with consistent sign | the concentrated artifact heads carry the degradation **beyond** their capability cost — a **targeted causal contribution**, the first in this record | **30%** |
| **A′** | TOP-K sits **below** the RND curve (more sink at matched capability), mean Δ ≤ −0.02 | the concentrated heads *protect against* the sink; degradation worsens when they are removed — surprising, and would invert the S1 reading | **10%** |
| **B** | the curves are indistinguishable (\|mean Δ\| < 0.02, or signs inconsistent) | ablation moves the sink **only** through general capability; S1's concentration is real but not load-bearing. Consistent with P12's magnitude null | **45%** |
| **C** | curves do not overlap in conditioned performance, so no interpolation is possible | infeasible at this dose grid; recorded, K grid revised in a successor, **not** re-gridded in-phase | **10%** |
| **D** | technical failure | recorded | **5%** |

**B remains the favourite**, for the same reason it was in Phase 13: P12 showed
attention *magnitude* does not distinguish sinking from clean models, and S1's
concentration finding — while it fired — is correlational, rests on four models with one
per cell, and carries an unresolved head-count caveat.

**Validity conditions, frozen.** At least **two** TOP-K points must fall inside the RND
curve's conditioned-performance range (otherwise branch C). Any arm whose conditioned
mean frac falls below **0.05** is excluded from interpolation as degenerate and recorded
as such. n = 44 throughout; all-cases judge; sink reported as `cond − artifact`
throughout.

**What a hit would license.** A would license *"removing these specific heads degrades
conditioned performance beyond what their general-capability cost explains."* It would
**not** license any claim about what those heads compute, nor that they are the *only*
route to the sink. Lesions localise contribution, not function — restated from Phase 13
because a positive result is exactly when that gets forgotten.

**Cost estimate: $1.80–3.00.** Eight new arms; Phase 13 measured ≈$0.28 per
44-problem × 8-candidate HF arm on 1.5B, and the K = 0 anchors are cached. Loop spend
before this phase: **$2.58** of the $90/$110 envelope; month-to-date **$80.62** of $200.

---

*(Results append below.)*

---

## RESULT (2026-07-25) — **BRANCH B FIRED VACUOUSLY. The adjudication statistic is degenerate; this phase could not have answered its own question.** *(`h14_dose_response.json`)*

All eight arms ran cleanly (exit 0, n = 44, no technical failure). The printed verdict was:

```
K=1  perf 0.3843  TOP -0.0746 vs RND(interp) -0.0746  Δ +0.0000
K=2  perf 0.3627  TOP -0.0962 vs RND(interp) -0.0962  Δ -0.0000
K=4  perf 0.3451  TOP -0.1138 vs RND(interp) -0.1138  Δ -0.0000
P14 BRANCH: B — curves indistinguishable; ablation acts only via capability
```

**That sentence is a vacuous truth and is not recorded as a finding.** Δ is zero by
construction, for every possible dataset.

### The algebra

The charter froze (§1, and the validity clause) `sink = cond − artifact`, where the
artifact null is a **single scalar** — a property of the stimulus pool, identical for
both arms and every K:

```python
art = st.mean(art_frac[q] for q in qs)            # one constant
curves[arm].append({"K": K, "perf": m, "sink": m - art})   # both arms
```

So in the (perf, sink) plane the RND "curve" is not a curve: it is the straight line
`y = x − art`, slope 1, and so is the TOP curve. Linear interpolation of a straight line
at `x = perf_TOP` returns `perf_TOP − art`, which **is** `sink_TOP`. Hence

```
Δ = sink(TOP) − sink(RND_interp) = (perf_TOP − art) − (perf_TOP − art) ≡ 0
```

The design's central idea — "ablation acting only through capability puts both arms on
one curve; a targeted effect puts TOP off it" — is unrealisable in this parameterisation,
because **both arms are algebraically pinned to the same line no matter what the model
does.** The measured Δ of ±0.0000 at all three interpolable K is that identity, not an
empirical null.

### The root cause is deeper than the statistic

**Phase 14 has no ablated i.i.d. arm.** The record's sink is a contrast between a
conditioned arm and baselines; here only the *conditioned* arm was ablated, while the
comparison baseline stayed a constant. Under that setup "sink" is just conditioned
performance shifted by a fixed offset, so **sink and capability are the same variable**
and no amount of interpolation can separate them.

Phase 13's S2 had the identical hole. It was masked there because branch C (capability
collapse at K = 16) fired first and the arms were never compared at matched capability.
Phase 14 was designed to fix S2's *dose*, and inherited S2's *structure* unexamined.

### What this says about pre-registration — a failure mode §10 does not yet name

Pre-registration is the record's main instrument against post-hoc tuning, and it worked
exactly as designed here: the rule was frozen at commit `980091a`, the run was executed
against it, and the result was accepted without adjustment. **But freezing a rule does
not check that the rule is falsifiable.** A statistic that cannot discriminate is not a
constraint on the experimenter; it is a null instrument that produces a publishable-looking
sentence from any data whatsoever — and it produced this record's pre-registered
**45% favourite**, which would have read as confirmation.

The check the loop lacked, and which is cheap: **before spending, evaluate the decision
rule symbolically on the quantities it consumes and confirm that at least two branches
are reachable.** Here, one line of algebra on the definition of `sink` would have shown
that A and A′ had probability **zero** under the design, and that the odds table was
therefore ill-posed rather than merely wrong.

### Prediction accounting — the phase is scored as a MISS, not a B hit

| branch | odds | outcome |
|---|---|---|
| **A** (targeted effect) | 30% | **unreachable by construction** — could not fire on any data |
| **A′** (heads protect) | 10% | **unreachable by construction** |
| **B** (indistinguishable) | 45% | fired with certainty, independent of the data — **not counted as a hit** |
| **C** (no overlap) | 10% | did not fire (3 of 4 TOP points interpolable; TOP-8 at 0.1498 fell below the RND range and was correctly dropped) |
| **D** (technical failure) | 5% | did not fire — the code ran correctly; the *design* failed |

Claiming the 45% favourite here would be the most misleading entry this record could
make. **Phase 14's substantive question is untouched and remains open.**

### What survives: the matched-**K** capability contrast *(`h14_matched_k_capability.json`)*

The comparison the curves were built from is **not** degenerate — TOP-K vs RND-K
*general capability* at matched dose, paired by problem (`scripts/j14_paired_analysis.py`,
free, local):

| K | TOP perf | RND perf | RND − TOP | paired SE | t | p |
|---|---|---|---|---|---|---|
| 1 | 0.3843 | 0.4017 | +0.0174 | 0.0183 | 0.95 | 0.34 |
| 2 | 0.3627 | 0.4042 | +0.0414 | 0.0220 | 1.88 | 0.060 |
| 4 | 0.3451 | 0.3863 | +0.0412 | 0.0228 | 1.80 | 0.071 |
| **8** | **0.1498** | **0.3253** | **+0.1755** | 0.0205 | **8.55** | **1.3e-17** |

Against the unablated K = 0 anchor (0.3976), the RND arm is statistically flat until
K = 8 (+0.0041, +0.0066, −0.0113, then −0.0723) while the TOP arm falls monotonically
(−0.0133, −0.0349, −0.0525, −0.2478).

**Reading, scoped.** The S1-selected heads are **more load-bearing for general capability**
than random heads — consistent in sign at every K and decisive at K = 8. This turns
Phase 13's single K = 16 observation into a dose curve with paired statistics, and it is a
genuine **positive control on the S1 selection**: the concentration ranking picks
functionally important heads rather than noise.

**What it does not license, stated flatly.** This is a statement about **general
capability**, not about the sink, and not about artifact processing. The TOP heads were
selected as the highest *artifact*-attention heads, but heads carrying large attention
mass to one span plausibly carry large mass generally, so "these heads matter" does not
establish "these heads matter *for the artifact*." Discriminating those requires the
ablated-i.i.d. design below. No mechanism claim is made, and **no Index or abstract row
changes on the strength of this phase.**

## PHASE GATE — CLOSED (2026-07-25)

1. **All eight arms ran; raw data committed before analysis** (`6ece2f2`), with the
   degeneracy recorded in that commit message *before* the verdict was written. ✓
2. **Branch B recorded as vacuous and explicitly not counted as a hit.** ✓
3. **Design defect named, with its algebra, and traced back to Phase 13 S2.** ✓
4. **Not retuned in-phase.** No ablated-i.i.d. arm was bolted on to rescue the result;
   the corrected design goes to a successor charter. ✓
5. **No claim made** — the capability contrast is recorded and scoped, and moves nothing
   in §0. ✓

**Cost.** Phase 14 **$2.15** (`modal billing report`, queried 2026-07-25 16:17 EDT;
app line `ap-yWAHavRNQP6zp` $2.1531, month-to-date delta $80.62 → $82.77) against a
$1.80–3.00 estimate — **inside the band**, the fourth consecutive calibrated generation
estimate. Loop total **$4.73** of the $90/$110 envelope; month-to-date **$82.77** of $200.

*The money was not wasted in the ordinary sense — it bought the capability dose curve and
the discovery of a structural defect that Phase 13 had already shipped undetected — but
it did not buy an answer to the question the phase was chartered to ask.*

**What is open.** The targeted-effect question, **unanswered**. The corrected design is
stated here for whichever successor takes it: ablate the **i.i.d. arm under the same head
set**, so that `sink(K) = cond_ablated(K) − iid_ablated(K)` and each ablation is scored
against its own capability baseline. That is eight further arms at ≈$2. **Nothing is
running; Phase 14 is closed.**
