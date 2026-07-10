# Compute accounting (frozen)

§8 of the brief: *"Matched-compute accounting is fiddly and easy to get wrong in
a way that flatters FULL. Decide the accounting rule before running, write it
down, don't touch it."* This document is that rule. It was written before any
comparison run. Changes after the first H2 run are prohibited except to fix an
arithmetic error, and any such fix must be logged at the bottom with the date and
the effect on already-reported numbers.

---

## Primary unit: candidate generations

**One unit of compute = one candidate generation by G** (one sampled completion,
up to `max_new_tokens`). A comparison is matched-compute when every condition
consumes the same number of candidate generations per problem, N.

| Condition | Generations per problem |
|---|---|
| B0 | 1 |
| B1 (best-of-n) | N |
| B1′ (no injection) | N |
| B2 (in-context refine) | N (initial attempt + N−1 revisions) |
| FULL (fixed-K) | N (K = N steps) |
| FULL (adaptive, H3) | mean ≤ N — matched on **mean** generations per problem, per the brief |

Rationale: generation dominates wall-clock and FLOPs at this scale; it is the
unit least gameable by implementation detail, and it is identical in kind across
all conditions.

## What is counted, what is reported, what is ignored

**Counted against the budget:** candidate generations, including candidates that
fail code extraction (a malformed candidate consumed a generation; dropping it
from the count would flatter whichever condition produces more garbage).

**Reported alongside every result (audit columns), but not budgeted:**

1. **Verifier forward passes.** FULL, B1, B1′, and B2 all use N verifier calls
   per problem; B0 uses 0 or 1. V is ~10⁴× cheaper than a generation; we report
   the count so the claim "V is negligible" is checkable, not assumed.
2. **Prompt tokens processed per condition.** This is the honest cost asymmetry:
   B2's context grows each round (previous candidate + feedback in prompt), so
   at equal generation counts B2 consumes *more* attention FLOPs than FULL —an
   asymmetry that favors B2, i.e. conservative for our claim. FULL's k=8 soft
   tokens add negligible prompt length. If FULL beats B2 at equal generations,
   it beats it a fortiori at equal FLOPs; if FULL *loses* to B2 at equal
   generations, the token report lets us say whether the FLOPs gap could explain
   it — but the headline verdict uses generations, full stop.
3. **U updates and r_0 encodings** (vector-sized ops; report count only).
4. **Wall-clock per problem** on fixed hardware, as the sanity cross-check the
   brief asks for (§5 "equal wall-clock").

**Ignored:** tokenization, pooling reads of hidden states already produced by
generation, logging.

## Fixed parameters for comparisons

- Decoding: identical sampling parameters (temperature, top-p, `max_new_tokens`)
  across all conditions. Recorded in the run config; a comparison across
  differing decode params is invalid.
- N (the budget) is set per experiment in configs (`loop.t_max` /
  `baselines.n`); headline H2 comparisons use one pre-registered N (default 8),
  with the pass@k-vs-budget curve reported at N ∈ {1, 2, 4, 8, 16} as secondary.
- H3 matching: adaptive FULL is compared to fixed-K at K = ⌈mean adaptive
  generations⌉ **and** the compute–accuracy Pareto curve is reported, so the
  verdict doesn't hinge on a single rounding.

## Enforcement

`rgr.loop.budget.ComputeLedger` records generations, verifier calls, update
calls, prompt tokens, and generated tokens per trajectory. Evaluation code
refuses to compare trajectories whose generation counts are unequal
(`rgr.evals` matched-compute assertion) unless explicitly comparing on the mean
(H3 mode). The ledger is written into every results file; audits never require
a rerun.

---

*Amendment log: (empty — and it should stay that way).*
