"""J5 Q2 step 2 — W0c floor fit on the 7B medium stratum + power envelope.

The instrument's FOURTH out-of-sample test: E[fresh B1-50 recoveries] is
committed to PHASE_5.md before any arm runs. Identical fit machinery to
W0c / J4 (w0_recomputes._fit_mixture); identical power envelope to J4
(exact one-sided McNemar, floor ~ 0 -> reject at b >= 5 discordant
recoveries since 0.5^5 = 0.031 <= 0.05; power(r) = P(Binom(n, r) >= 5)).
Validated by reproducing J4's recorded n=76 numbers before computing n=46.
"""
import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
from w0_recomputes import _fit_mixture, _log_beta  # noqa: E402


def _binom_sf(n, p, k):
    """P(X >= k), X ~ Binom(n, p)."""
    if p <= 0:
        return 0.0 if k > 0 else 1.0
    return sum(math.comb(n, x) * p**x * (1 - p) ** (n - x) for x in range(k, n + 1))


def _mcnemar_threshold(alpha=0.05):
    """Min b with 0.5^b <= alpha (floor ~ 0: all discordants are arm-only)."""
    b = 1
    while 0.5**b > alpha:
        b += 1
    return b


def floor_and_power(counts, n_draws=50):
    n_zero = sum(1 for x in counts if x == 0)
    fits = {}
    for tag, wpm in (("mixture", True), ("pure_beta_upper_bound", False)):
        f = _fit_mixture(counts, n_draws, with_point_mass=wpm)
        a, b, pi0 = f["alpha"], f["beta"], f["pi0"]
        bb0 = math.exp(_log_beta(a, b + n_draws) - _log_beta(a, b))
        p_reach = (1 - pi0) * bb0 / (pi0 + (1 - pi0) * bb0)
        rec_if_reach = 1.0 - math.exp(
            _log_beta(a, b + 2 * n_draws) - _log_beta(a, b + n_draws))
        per_prob = p_reach * rec_if_reach
        fits[tag] = {**f, "P_reachable_given_zero": p_reach,
                     "fresh50_recovery_prob_per_zero_problem": per_prob,
                     "expected_B1_50_recoveries_in_stratum": per_prob * n_zero}
    thr = _mcnemar_threshold()
    power = {f"r={r:.2f}": _binom_sf(n_zero, r, thr)
             for r in (0.10, 0.15, 0.20)}
    return n_zero, fits, thr, power


def main():
    # -- validation leg: reproduce J4's recorded power envelope (n=76, floor 0)
    thr = _mcnemar_threshold()
    j4 = {r: _binom_sf(76, r, thr) for r in (0.10, 0.15, 0.20)}
    print(f"validation (J4, n=76, b>={thr}): "
          f"r=0.10 {j4[0.10]:.3f} (recorded 0.890)  "
          f"r=0.15 {j4[0.15]:.3f} (recorded 0.994)  "
          f"r=0.20 {j4[0.20]:.3f} (recorded ~1.00)")
    assert abs(j4[0.10] - 0.890) < 0.005 and abs(j4[0.15] - 0.994) < 0.005, \
        "power formula does not reproduce the J4 instrument — STOP"

    # -- 7B screen counts (same question order as the medium population file)
    med = json.loads(
        (REPO / "runs/modal/lcb_res_lcb_r2_base_medium_T08.json").read_text())
    qids = med["question_ids"]
    res = json.loads((REPO / "runs/modal/j5_q2_screen_res.json").read_text())
    assert len(res) == len(qids) == 78
    counts = [sum(1 for c in row if c["passed"]) for row in res]

    scr = json.loads((REPO / "artifacts/h5_7b_medium_screen.json").read_text())
    stratum = [q for q, x in zip(qids, counts) if x == 0]
    assert sorted(stratum) == sorted(scr["stratum_qids"]), \
        "recomputed stratum disagrees with the screen artifact — STOP"

    n_zero, fits, b_thr, power = floor_and_power(counts)
    m, u = fits["mixture"], fits["pure_beta_upper_bound"]
    out = {
        "_label": "J5 Q2 step 2 — W0c floor fit on the 7B medium stratum "
                  "[PHASE_5.md J5; instrument's 4th out-of-sample test]",
        "model": "Qwen/Qwen2.5-Coder-7B",
        "counts": counts,
        "n_zero": n_zero,
        "near_x1_x2": {"1": sum(1 for x in counts if x == 1),
                       "2": sum(1 for x in counts if x == 2)},
        "fits": {"mixture": m, "pure_beta_upper": u},
        "power_envelope": {"mcnemar_reject_at_b": b_thr, **power},
    }
    (REPO / "artifacts/h5_7b_floor_fit.json").write_text(json.dumps(out, indent=2))
    print(f"=== J5 7B floor: stratum {n_zero}/78  "
          f"x=1:{out['near_x1_x2']['1']} x=2:{out['near_x1_x2']['2']}  "
          f"pi0 {m['pi0']:.3f}  P(reach|0) {m['P_reachable_given_zero']:.3f}  "
          f"E[B1-50 recoveries] {m['expected_B1_50_recoveries_in_stratum']:.3f} "
          f"(upper {u['expected_B1_50_recoveries_in_stratum']:.3f}) ===")
    print(f"=== power (b>={b_thr}): " +
          "  ".join(f"{k} {v:.3f}" for k, v in power.items()) + " ===")


if __name__ == "__main__":
    main()
