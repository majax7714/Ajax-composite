"""Phase 6 P2 — the distinct-seed floor prediction on the Qwen 1.5B medium stratum.

The flagship contrast (Qwen HINT 13 vs floor ~2, p = 4.9e-4, §9.8) rests on a
same-seed B1-50 control whose "fresh draw" premise the J5 diagnostic showed is
~50% violated (same-seed vLLM regenerates ~half the pool byte-for-byte, §8
harness caveat). P2 runs a *distinct-seed* B1-50 on the same 68-problem medium
stratum, genuinely satisfying the fresh-draw premise, as the floor instrument's
SIXTH out-of-sample test.

This script commits the prediction BEFORE that run: it reproduces the W0c
two-component fit on the frozen 1.5B medium screen pool (identical machinery to
w0_recomputes / j5_floor_fit) and derives E[fresh B1-50 recoveries] + the ~94%
predictive band + falsification thresholds. Because the distinct seed makes the
effective fresh-draw count the full 50, the "corrected E under true-fresh draws"
IS the fit's native E (the J5 same-seed suppression that pulled the observed
same-seed number down no longer applies) — stated explicitly so the premise is
on the page.

Run: python3 scripts/j6_p2_floor_predict.py   (pure CPU, no network, no Pool)
"""
import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
from w0_recomputes import _fit_mixture, _log_beta  # noqa: E402

POOL = REPO / "runs/modal/lcb_res_lcb_r2_base_medium_T08.json"
N_DRAWS = 50


def per_problem_recovery_prob(a, b, pi0, n=N_DRAWS):
    """Fresh-n recovery prob for a problem observed at 0/n, under the fit.

    P(reachable | 0/n) * P(>=1 pass in a fresh n | reachable) — identical to the
    W0c / j5_floor_fit derivation.
    """
    bb0 = math.exp(_log_beta(a, b + n) - _log_beta(a, b))          # P(x=0 | reachable)
    p_reach = (1 - pi0) * bb0 / (pi0 + (1 - pi0) * bb0)
    rec_if_reach = 1.0 - math.exp(_log_beta(a, b + 2 * n) - _log_beta(a, b + n))
    return p_reach, rec_if_reach, p_reach * rec_if_reach


def binom_pmf(n, p):
    return [math.comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(n + 1)]


def central_band(pmf, mass=0.94):
    """Smallest contiguous [lo, hi] with cumulative pmf >= mass, grown from the
    mode outward (ties -> add the larger-pmf side first)."""
    mode = max(range(len(pmf)), key=lambda k: pmf[k])
    lo = hi = mode
    total = pmf[mode]
    while total < mass:
        left = pmf[lo - 1] if lo > 0 else -1.0
        right = pmf[hi + 1] if hi + 1 < len(pmf) else -1.0
        if right >= left:
            hi += 1
            total += pmf[hi]
        else:
            lo -= 1
            total += pmf[lo]
    return lo, hi, total


def main():
    pool = json.loads(POOL.read_text())
    res, qids = pool["results"], pool["question_ids"]
    assert len(res) == len(qids) == 78, "medium population is not 78 problems"
    counts = [sum(1 for c in row if c.get("passed")) for row in res]
    n_zero = sum(1 for x in counts if x == 0)
    assert n_zero == 68, f"stratum {n_zero} != 68 (frozen Qwen medium stratum)"

    fits = {}
    for tag, wpm in (("mixture", True), ("pure_beta_upper_bound", False)):
        f = _fit_mixture(counts, N_DRAWS, with_point_mass=wpm)
        a, b, pi0 = f["alpha"], f["beta"], f["pi0"]
        p_reach, rec_if_reach, q = per_problem_recovery_prob(a, b, pi0)
        fits[tag] = {**f, "P_reachable_given_zero": p_reach,
                     "fresh50_recovery_prob_per_zero_problem": q,
                     "expected_B1_50_recoveries_in_stratum": q * n_zero}

    m = fits["mixture"]
    q = m["fresh50_recovery_prob_per_zero_problem"]
    E = m["expected_B1_50_recoveries_in_stratum"]
    # All 68 observed-zero problems share the same posterior recovery prob q
    # (exchangeable given x=0), so the recovery count ~ Binomial(68, q).
    pmf = binom_pmf(n_zero, q)
    lo, hi, cov = central_band(pmf, 0.94)
    point = max(range(len(pmf)), key=lambda k: pmf[k])
    p_at_least = lambda k: sum(pmf[k:])
    p_at_most = lambda k: sum(pmf[:k + 1])

    out = {
        "_label": "Phase 6 P2 — committed distinct-seed floor prediction, "
                  "Qwen2.5-Coder-1.5B medium stratum (instrument's 6th "
                  "out-of-sample test; first under a satisfied fresh-draw premise)",
        "pool": str(POOL.relative_to(REPO)),
        "stratum_n": n_zero,
        "near_x1_x2": {"1": sum(1 for x in counts if x == 1),
                       "2": sum(1 for x in counts if x == 2)},
        "fits": fits,
        "prediction_true_fresh": {
            "note": "distinct seed => effective fresh draws = full 50 => corrected "
                    "E under true-fresh draws == the fit's native E; the J5 same-seed "
                    "suppression does not apply.",
            "per_problem_recovery_prob_q": q,
            "E_recoveries": E,
            "point_prediction": point,
            "band_94pct": [lo, hi],
            "band_actual_mass": cov,
            "P(X<=1)": p_at_most(1),
            "P(X>=hi+1)": p_at_least(hi + 1),
            "falsifies_high": hi + 1,
            "falsifies_low": lo - 1 if lo > 0 else None,
        },
    }
    print(json.dumps(out, indent=2))
    return out


if __name__ == "__main__":
    main()
