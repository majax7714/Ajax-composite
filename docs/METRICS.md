# Metrics

> **Status note (2026-07-17, appended — content below unrevised):** The
> estimators here (unbiased pass@k, AUROC/ECE/Brier, bootstrap) remain the
> spec for their implementations. Later-phase instruments — PULL/AST-PULL,
> the false-zero floor model, exact McNemar, the hint-grading rubric — are
> specified in the phase charters and journal §0.1 (Instruments).

Definitions and estimators, fixed before any run. Implementations live in
`rgr/evals/` (pure stdlib, unit-tested); this file is the spec they implement.

---

## Correctness

**pass@1** — fraction of problems whose evaluated candidate passes all tests.
For multi-candidate conditions, "the" candidate is the verifier's argmax
(that is the deployment story for every condition that has a verifier).

**pass@k** — unbiased estimator (Chen et al., 2021):
`pass@k = E_problems[ 1 − C(n−c, k) / C(n, k) ]`
with n candidates per problem of which c pass. Requires n ≥ k; the
implementation raises rather than silently truncating.

All correctness numbers are reported **at matched compute** per
[COMPUTE_ACCOUNTING.md](COMPUTE_ACCOUNTING.md), with the ledger columns
alongside.

## Calibration (H1)

Head-to-head, same candidates, two scorers: V's probability vs G's mean token
log-likelihood of the candidate.

- **AUROC** (primary) — probability a random correct candidate outscores a
  random incorrect one; ties count ½ (Mann–Whitney). Computed over the pooled
  (problem, candidate) set and, as a check, macro-averaged per problem over
  problems that have both classes.
- **ECE** (secondary) — 10 equal-width bins on [0,1], weighted |acc − conf|.
  Likelihood is min-max normalized per dataset before binning (AUROC needs no
  normalization; ECE for likelihood is reported with this caveat).
- **Brier** (secondary) — mean squared error of probability vs {0,1} label.

**H1 margin:** pre-registered as ΔAUROC ≥ 0.05 on held-out problems with the
95% bootstrap CI excluding 0. Below that, H1 is failed or marginal → stop and
fix confidence (brief §11).

## Register load (H2)

- Δpass@1 and Δpass@k: FULL − B1 and FULL − B2 at matched compute.
- **CIs by problem-level bootstrap** (resample problems with replacement,
  10 000 resamples, percentile 95% CI, fixed seed). Bootstrap is over problems,
  not candidates — candidates within a problem are correlated.
- **H2 verdict:** both deltas positive with CIs excluding 0 → H2 supported.
  Either CI containing 0 → tie → the register is dead per the kill criterion.
- B1′ reported alongside to attribute how much of B1's level is r_0 injection
  vs the vanilla model (diagnostic, not a gate).

## Adaptive compute (H3)

- Spearman correlation between steps-to-stop and difficulty proxy
  (per-problem B0 pass rate from Phase 0), with bootstrap CI.
- Adaptive vs fixed-K pass@1 at matched **mean** generations.
- Compute–accuracy Pareto: pass@1 vs mean generations, adaptive curve
  (τ swept on MBPP validation only) overlaid on fixed-K points.

## Standing diagnostics (logged every Phase ≥ 2 run)

- Register trajectory: per-step ‖r_t‖, ‖r_{t+1} − r_t‖, variance of final r
  across problems (collapse/blow-up detection, brief §8).
- Steps-to-settle distribution.
- Verifier staleness: V AUROC on a fresh current-policy rollout sample vs its
  training-time AUROC; a drop > 0.05 triggers a V refresh before further H2 runs.
- Format-discipline rate: fraction of generations with extractable code, per
  condition (a shift here confounds everything downstream — watch it).
