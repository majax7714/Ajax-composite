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
