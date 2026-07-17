"""J5 Q2 extension step 2 — W0c floor fit on the 7B HARD stratum + pooled power.

The instrument's FIFTH out-of-sample test: the hard stratum's E[fresh B1-50
recoveries] is committed to PHASE_5.md before any arm runs. Pooled power gate
(frozen): floor-aware exact-McNemar envelope over the pooled stratum
(medium 46 at its fitted floor + hard at this fit's floor), governed by the
stricter marginal-r reading; arms launch iff power >= 0.70 at r = 0.20.
Exact computation: per-group trinomial (arm-only / B1-only / concordant)
convolved into the joint (b, c) pmf; reject where one-sided binomial
P(X >= b | b+c, 1/2) <= 0.05.
"""
import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
from j5_floor_fit import floor_and_power  # noqa: E402


def _pval(b, m):
    return sum(math.comb(m, x) for x in range(b, m + 1)) / 2**m if m else 1.0


def _joint_bc(groups):
    """Joint pmf over (b, c) for independent per-problem trinomials.
    groups: [(n, p_arm_only, p_b1_only), ...]"""
    pmf = {(0, 0): 1.0}
    for n, pb, pc in groups:
        pn = 1.0 - pb - pc
        for _ in range(n):
            nxt = {}
            for (b, c), p in pmf.items():
                for db, dc, pp in ((1, 0, pb), (0, 1, pc), (0, 0, pn)):
                    k = (b + db, c + dc)
                    nxt[k] = nxt.get(k, 0.0) + p * pp
            pmf = nxt
    return pmf


def pooled_power(r, strata, reading="marginal"):
    """strata: [(n, f), ...]; arm rate = r (marginal) or min(f+r, 1) (uplift)."""
    groups = []
    for n, f in strata:
        a = r if reading == "marginal" else min(f + r, 1.0)
        groups.append((n, a * (1 - f), f * (1 - a)))
    pmf = _joint_bc(groups)
    return sum(p for (b, c), p in pmf.items() if _pval(b, b + c) <= 0.05)


def main():
    qids = json.loads((REPO / "runs/modal/j5_hard_qids.json").read_text())
    res = json.loads((REPO / "runs/modal/j5_hard_screen_res.json").read_text())
    assert len(res) == len(qids) == 61
    counts = [sum(1 for c in row if c["passed"]) for row in res]

    scr = json.loads((REPO / "artifacts/h5_7b_hard_screen.json").read_text())
    stratum = [q for q, x in zip(qids, counts) if x == 0]
    assert sorted(stratum) == sorted(scr["stratum_qids"]), \
        "recomputed stratum disagrees with the screen artifact — STOP"

    n_zero, fits, b_thr, _ = floor_and_power(counts)
    m, u = fits["mixture"], fits["pure_beta_upper_bound"]
    e_hard = m["expected_B1_50_recoveries_in_stratum"]
    f_hard = m["fresh50_recovery_prob_per_zero_problem"]

    med = json.loads((REPO / "artifacts/h5_7b_floor_fit.json").read_text())
    f_med = med["fits"]["mixture"]["fresh50_recovery_prob_per_zero_problem"]
    n_med = med["n_zero"]
    strata = [(n_med, f_med), (n_zero, f_hard)]

    power = {}
    for r in (0.10, 0.15, 0.20):
        power[f"r={r:.2f}"] = {
            "marginal": pooled_power(r, strata, "marginal"),
            "uplift": pooled_power(r, strata, "uplift")}
    gate_pass = power["r=0.20"]["marginal"] >= 0.70

    # committed-prediction band for the hard stratum: shortest >=90% central
    # mass of Binomial(n_zero, f_hard) (same construction as the medium band)
    pmf = [math.comb(n_zero, k) * f_hard**k * (1 - f_hard) ** (n_zero - k)
           for k in range(n_zero + 1)]
    best = None
    for lo in range(n_zero + 1):
        acc = 0.0
        for hi in range(lo, n_zero + 1):
            acc += pmf[hi]
            if acc >= 0.90:
                if best is None or hi - lo < best[1] - best[0]:
                    best = (lo, hi, acc)
                break
    band = {"lo": best[0], "hi": best[1], "mass": best[2]}

    out = {
        "_label": "J5 Q2 extension step 2 — W0c floor fit on the 7B hard stratum "
                  "[PHASE_5.md J5; instrument's 5th out-of-sample test] + pooled power",
        "model": "Qwen/Qwen2.5-Coder-7B",
        "counts": counts,
        "n_zero": n_zero,
        "near_x1_x2": {"1": sum(1 for x in counts if x == 1),
                       "2": sum(1 for x in counts if x == 2)},
        "fits": {"mixture": m, "pure_beta_upper": u},
        "committed_band_90pct": band,
        "pooled_power": {"strata": [{"n": n, "f": f} for n, f in strata],
                         **power, "gate_rule": "marginal r=0.20 >= 0.70",
                         "gate_pass": gate_pass},
    }
    (REPO / "artifacts/h5_7b_hard_floor_fit.json").write_text(json.dumps(out, indent=2))
    print(f"=== J5 hard floor: stratum {n_zero}/61  "
          f"x=1:{out['near_x1_x2']['1']} x=2:{out['near_x1_x2']['2']}  "
          f"pi0 {m['pi0']:.3f}  P(reach|0) {m['P_reachable_given_zero']:.3f}  "
          f"E[B1-50] {e_hard:.3f} (upper "
          f"{u['expected_B1_50_recoveries_in_stratum']:.3f})  "
          f"band [{band['lo']},{band['hi']}] ({band['mass']:.3f}) ===")
    for k, v in power.items():
        print(f"    pooled {k}: marginal {v['marginal']:.3f}  uplift {v['uplift']:.3f}")
    print(f"=== pooled gate (marginal r=0.20 >= 0.70): "
          f"{'PASS' if gate_pass else 'FAIL'} ===")


if __name__ == "__main__":
    main()
