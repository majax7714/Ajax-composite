# Phase 17 — closing the verb question, powered

*Charter opened 2026-07-25. Eighth iteration of the unattended loop. Author instruction:
"finish out verb question and write up." Append-only; pre-registration frozen before spend.*

## 0. What Phase 16 left, and the two errors it logged

Phase 16 asked whether the SINK is framing-sensitive and closed **INCONCLUSIVE on
instrument**: a frozen validity condition (`cond_A − artifact ≤ −0.03`) returned −0.0296
and failed by 0.0004, so no branch was adjudicated. The gate was honoured and not retuned.

Its substantive contrast also near-missed: Coder-1.5B **Δ(B−A) = −0.0336 ± 0.0176,
p 0.0562** at n = 44, k = 8. Two near-misses in one phase, both traceable to thresholds
and sample sizes chosen without reference to measured spread — the error class now written
into §8 as entry 9. **This phase fixes both properly rather than re-running the same
design and hoping.**

## P0 (free, landed before the charter) — power measured, not assumed *(`h17_p0_power.json`)*

**A first attempt at this analysis was wrong and is recorded as such.** It decomposed the
paired variance analytically into between-problem and candidate-sampling terms, assuming
the two verb arms are independent given the problem. The arithmetic refuted the assumption
immediately: the implied within-problem share came out at **123%** (Coder) and **347%**
(DeepSeek) of the observed variance, which is impossible. Both arms were generated at the
**same seed 233** from prompts differing in one clause, and §8's seed-policy caveat already
records that same-seed vLLM regeneration reproduces 45–50% of a pool byte-for-byte. The
arms are positively correlated — which is exactly what pairing exploits, and exactly what
invalidates the independent decomposition.

Measured directly instead ([scripts/j17_p0_power.py], subsample k of the 8 committed
candidates per arm, recompute the paired SE, fit `SE² = a + b/k`; no independence
assumption survives into the estimate):

| k | Coder-1.5B SE | DeepSeek SE |
|---|---|---|
| 2 | 0.0382 | 0.0225 |
| 3 | 0.0311 | 0.0173 |
| 4 | 0.0264 | 0.0142 |
| 6 | 0.0209 | 0.0097 |
| 8 | 0.0176 | 0.0067 |

Both fit **`SE² = b/k` with a ≈ 0** (Coder b = 0.003067, DeepSeek b = 0.001229): the
residual noise is **entirely candidate sampling**, and problem-to-problem variation in the
verb effect is negligible. So **k is the lever, not n** — which the Phase-16 design got
backwards by implicitly treating n = 44 as the binding constraint.

| | Coder-1.5B (n = 44) | DeepSeek-1.3B (n = 39) |
|---|---|---|
| effect at k = 8 | **−0.0336** | +0.0071 |
| projected SE at k = 24 | **0.0113** | 0.0072 |
| projected \|t\| at k = 24 | **2.98** | 0.99 |
| **n needed for 80% power at k = 24** | **39 — feasible at 44** | **312 — not feasible** |

**Coder-1.5B is powerable on the cell that already exists. DeepSeek is not**, and no
budget available to this loop fixes that: its own effect would need n ≈ 312 problems.
Pre-registering a significance test on ΔD would manufacture a third near-miss, so this
phase does not pre-register one.

**What *is* powerable is the family difference.** ΔC − ΔD = −0.0407 with
SE = √(0.0113² + 0.0072²) = **0.0134**, |t| ≈ **3.0**. That is the comparison that answers
"is the verb effect specific to the sinking family," and it is a better question than two
separate one-family tests.

## 1. Design

**Same two committed cells, same problems, same artifacts, same frozen prompts** — only
the candidate count and the seed change.

| | Phase 16 | **Phase 17** |
|---|---|---|
| candidates per problem | 8 | **24** |
| seed | 233 | **239** (distinct-seed protocol, §10 P2) |
| cells | Coder-1.5B n=44, DeepSeek-1.3B n=39 | unchanged |
| verbs | A `Improve it so that all tests pass.` / B `Write a correct program that passes all tests.` | unchanged, byte-identical |

Phase 16's k = 8 / seed-233 arms are **not** pooled in. They stay on the page as an
independent prior measurement, so Phase 17 is a genuine replication at higher precision
rather than an extension of the same draw.

**Validity condition, CI-referenced — the Phase-16 fix.** VERB-A's
`delta_cond_minus_iid` must fall **inside the committed CI95 of the cell it is
replicating**:

| cell | committed CI95 | width | P16 VERB-A landed |
|---|---|---|---|
| Coder-1.5B (P11) | **[−0.1258, −0.0028]** | 0.1230 | −0.0412 ✓ inside |
| DeepSeek (P7 M1) | **[−0.0207, +0.1164]** | 0.1371 | +0.0468 ✓ inside |

This is stated in units of the quantity's measured spread, as §8 entry 9 now requires. It
is a real gate — an arm that failed to replicate would land outside — but it cannot fire
on a faithful replication, which is precisely what −0.03 could and did.

## 2. Pre-registered predictions

Primary quantities: **ΔC** = mean paired (cond_B − cond_A) on Coder-1.5B; **ΔD** the same
on DeepSeek; **ΔC − ΔD** the family difference (independent samples). α = 0.05 two-sided.

| # | branch | reading | odds |
|---|---|---|---|
| **A** | **ΔC significant AND (ΔC − ΔD) significant** | the verb moves the conditioned arm of the sinking family and does so **more than** it moves the clean family — a framing effect that is diet-linked. The sink's magnitude is partly a property of the instruction | **35%** |
| **B** | **ΔC significant, family difference NOT** | framing moves conditioned performance generally; nothing about it is specific to the Coder diet | **20%** |
| **C** | **ΔC not significant** | Phase 16's −0.0336 does **not** survive powering — regression to the mean on a p = 0.056 estimate. The sink is **framing-invariant** on a properly powered test, and claim 6's dominant lever is inert on claim 8's phenomenon: a first-class dissociation | **35%** |
| **D** | validity fails on either cell, or technical failure | instrument miss, recorded; no adjudication | **10%** |

**A and C are priced level.** Phase 16's estimate is a single draw with SE 0.0176 from a
p = 0.056 test; the true effect plausibly lies anywhere in roughly [−0.068, 0.000], and a
true effect near −0.02 would leave |t| ≈ 1.8 at k = 24. Publication-style optimism about a
near-miss replicating is exactly the bias this record has been burned by (M4 died at
re-run; the Phase-10 gain law died on 14 cells).

**ΔD is reported with its CI as a bound and is NOT significance-tested** — pre-registered
here so that no post-hoc test on it can be introduced later. Its projected CI half-width at
k = 24 is ≈ 0.014, which is itself informative: an interval that excludes Coder's −0.034
supports a family difference even though ΔD alone is unresolvable.

**Reachability check (§8 entry 8).** ΔC is a paired mean of differences between two
independently generated arms; the artifact null cancels (`sink_B − sink_A = cond_B −
cond_A`) leaving a free quantity, and ΔC − ΔD is a difference of two such free quantities.
No shared constant pins either to a fixed value; both can take any sign or none. Branches
A, B and C partition the (ΔC significant?, family-difference significant?) outcomes
exhaustively and disjointly. **Verified symbolically before freezing.**

**Threshold-in-units-of-spread check (§8 entry 9, first application).** Every threshold in
this phase is derived from a measured quantity: the validity gate references committed
bootstrap CIs; significance uses α on empirically measured SEs; k = 24 was chosen because
the measured k-scaling puts the required n at 39 ≤ 44. **No round numbers are used as
gates.**

**What a hit would and would not license.** A or B would license *"the conditioned
degradation depends on the instruction framing"* and, for A, *"more so in the sinking
family."* Neither would license "the sink is just prompting" — the i.i.d. and copy nulls
are untouched and the below-both-nulls classification was verb-invariant in Phase 16 — nor
would either disturb the diet attribution, which rests on a cross-family contrast at fixed
framing.

**Cost estimate: $0.40–0.90.** Four arms at k = 24: (44 + 39) × 2 × 24 ≈ 3,984 generations
on 1.5B/1.3B-class models, plus judging; i.i.d. arms cached and unchanged. Calibrated from
P11's measured $0.68 for ≈4,900 generations — the generation estimator, accurate six times
running. **Labelled estimate**, reconciled at close per Amendment 2. Loop spend before this
phase: **$5.22**; month-to-date **$83.26** against the Amendment-3 envelope of $100 report
/ $120 hard stop.

---

*(Results append below.)*

---

## RESULT (2026-07-25) — **BRANCH C: the SINK is FRAMING-INVARIANT. Phase 16's near-miss does not survive powering.** *(`h17_verb_powered.json`)*

Four arms, k = 24, seed 239, n = 44 / 39. **Both CI-referenced validity gates passed.**

| model | verb | cond | vs artifact | vs i.i.d. | below both nulls | coverage@24 |
|---|---|---|---|---|---|---|
| **Coder-1.5B** | A `Improve it…` | 0.3960 | −0.0629 | **−0.0744** ✓ in CI | **yes** | 0.455 |
| **Coder-1.5B** | B `Write a correct program…` | 0.3963 | −0.0625 | −0.0741 | **yes** | 0.455 |
| DeepSeek-1.3B | A `Improve it…` | 0.3618 | +0.0011 | **+0.0509** ✓ in CI | no | 0.205 |
| DeepSeek-1.3B | B `Write a correct program…` | 0.3652 | +0.0045 | +0.0543 | no | 0.205 |

| quantity | estimate | SE | 95% CI | p |
|---|---|---|---|---|
| **ΔC** (Coder verb effect) | **+0.0004** | 0.0096 | **[−0.0184, +0.0191]** | **0.970** |
| ΔD (DeepSeek) — *bound only, not tested* | +0.0034 | 0.0037 | [−0.0039, +0.0107] | — |
| **ΔC − ΔD** (family difference) | **−0.0030** | 0.0102 | [−0.0231, +0.0170] | **0.766** |

### This is a powered null, not another ambiguous result

The achieved SE (0.0096) **beat** the projected 0.0113, so an effect of Phase 16's size
would have registered at |t| ≈ 3.5. It did not. **ΔC's 95% CI excludes Phase 16's point
estimate of −0.0336** — the powered measurement does not merely fail to confirm the
near-miss, it rules out an effect of that magnitude. DeepSeek's bound is tighter still and
also excludes it.

The verb moves **nothing**: not mean frac (ΔC = +0.0004), not coverage (0.455 vs 0.455 on
Coder, 0.205 vs 0.205 on DeepSeek), and not the below-both-nulls classification, which was
already verb-invariant in Phase 16 and remains so at four times the precision. And the two
families do not differ in their (non-)response, p 0.77.

### The finding

**The instruction verb — the largest single anchoring lever this record has measured, worth
up to 0.127 of PULL in the D-measure frame against ≤0.028 for provenance — is inert on the
SINK.** Substituting an independent framing (`write a correct program`) for the
continuation framing (`improve it`) that produced every sink number in this journal changes
the conditioned arm by 0.0004 ± 0.0096.

That is a **dissociation between claim 6 and claim 8**. The escape-distance law is an
anchoring phenomenon whose dominant lever is the instruction verb; the SINK is not moved by
that lever at all. They are mechanically distinct objects, and the record can now say so
from a powered measurement rather than from the observation that they were studied on
different benchmarks.

It also closes off the cheapest remaining deflationary explanation of the sink. "The Coder
models are just over-responding to an *improve* instruction" was a live, plausible,
never-tested story — the outside charter's §1.3 identified precisely this gap — and it is
now **excluded** to within ±0.019.

### Scope, stated tightly

**One** verb contrast (`improve` → `write-correct`, mirroring D2a's own E1-vs-E1p),
at **one** relational position (Δ_art ≈ 0), on **two** models, with provenance framing and
every other prompt element held byte-identical. This does **not** license "the sink is
invariant to all framings" — a framing that removed the artifact, changed its presentation,
or altered the pass-count sentence is untested. What is licensed is that the specific lever
the record had already calibrated as its largest does nothing here.

### Phase 16 in retrospect

| | Phase 16 (k=8, seed 233) | **Phase 17 (k=24, seed 239)** |
|---|---|---|
| ΔC | −0.0336 ± 0.0176, p 0.056 | **+0.0004 ± 0.0096, p 0.970** |
| ΔD | +0.0071 ± 0.0067, p 0.286 | +0.0034 ± 0.0037 |
| validity | **failed** (−0.0296 vs a round −0.03) | **passed** (CI-referenced, both cells) |

Phase 16's −0.0336 was one draw from a wide distribution, and priced as such: A and C were
deliberately set level at 35% rather than betting on the near-miss. **Had Phase 16's gate
passed by 0.0004 instead of failing by it, this record would now contain a marginal framing
effect that does not exist.** The gate that cost a phase also prevented a false positive —
which is the argument for honouring thresholds that fire inconveniently, made concrete.

## PHASE GATE — CLOSED (2026-07-25)

1. **P0 landed free, including its own error** — the analytic variance decomposition was
   wrong (it assumed independent arms; the arithmetic said 123%/347%), was discarded, and
   was replaced by a direct empirical measurement of the k-scaling. Both are on the page. ✓
2. **Power derived from measurement**, and it held: projected SE 0.0113, achieved 0.0096. ✓
3. **No significance test was run on ΔD**, exactly as pre-registered; it is reported as a
   bound. ✓
4. **Both validity gates were CI-referenced and both passed** — the §8 entry 9 fix working
   as intended on its first application. ✓
5. **Branch recorded as frozen; verb question CLOSED.** ✓

**Prediction accounting.** **C (35%) HIT.** A (35%), B (20%) and D (10%) did not fire.
A and C were priced level on the stated reasoning — that a p = 0.056 estimate is one draw
and regression to the mean is the record's most repeated lesson (M4, the Phase-10 gain
law) — and that reasoning was correct.

**Cost.** Phase 17 **$0.551** (`modal billing report`, queried 2026-07-25 19:47 EDT;
month-to-date aggregate delta $83.26 → $83.81) against a $0.40–0.90 estimate — **inside the
band**, the seventh consecutive calibrated generation estimate. Loop total **$5.77**;
month-to-date **$83.81** against $100 report / $120 hard stop.

**What is open.** The verb question is **closed**. What P0.2 opened in Phase 16 is not:
the sink's **dominant channel is coverage** (Coder-1.5B −0.432 pass@8, Coder-7B 0.000), and
**no phase has yet manipulated coverage directly**. That is the strongest live pointer in
the record. **Nothing is running; Phase 17 is closed.**
