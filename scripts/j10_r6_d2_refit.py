#!/usr/bin/env python3
"""Phase 10 R6 — refit Phase 8's D2 Coder response curve after the M4 retraction.

M4 is one of the six Coder points in `h8_d2_response_curves.json`
(`[-0.0393, -0.1286, 'M4 Coder-7B*']`), sitting beside the deepest point that sets the
trough. Its retraction ([PHASE_10.md] R4) therefore reaches D2's vertex, its
interior-trough reading, and Phase 8's POSITION-GATED mechanism call.

Pre-registered [PHASE_10.md] R6 at commit f66632d, BEFORE this ran. Free, no GPU.
Writes artifacts/h10_r6_d2_refit.json.
"""
import json
from pathlib import Path

import numpy as np

REPO = Path(__file__).parents[1]

# Well-powered 7B cells measured after D2 was fit. (delta_art, delta_cond, label)
NEW_7B = [
    ("h8_matched_C4_coder7b_widerN.json", "C4 Coder-7B n=37"),
    ("h10_r3_coder7b_truematch.json", "R3 Coder-7B n=30"),
    ("h10_r4_coder7b_m4replication.json", "R4 Coder-7B n=37"),
    ("h10_r5_coder7b_truematch0.json", "R5 Coder-7B (true match)"),
]


def load_cell(fn):
    p = REPO / "artifacts" / fn
    if not p.exists():
        return None
    top = json.loads(p.read_text())
    d = top["cell"] if isinstance(top.get("cell"), dict) else top
    dart = top.get("achieved_delta_art_powered", d.get("actual_delta_art"))
    return (round(dart, 4), round(d["delta_cond_minus_iid"], 4))


def fit(points):
    """Quadratic fit; returns vertex, R^2, and whether the vertex is interior."""
    if len(points) < 4:
        return None
    x = np.array([p[0] for p in points], float)
    y = np.array([p[1] for p in points], float)
    c = np.polyfit(x, y, 2)
    yh = np.polyval(c, x)
    ss_res = float(((y - yh) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    vertex = float(-c[1] / (2 * c[0])) if c[0] != 0 else float("nan")
    lin = np.polyfit(x, y, 1)
    return {"quad": [round(v, 4) for v in c], "r2": round(r2, 4),
            "vertex_dart": round(vertex, 4),
            "vertex_interior": bool(x.min() < vertex < x.max()),
            "convex": bool(c[0] > 0), "linear_slope": round(float(lin[0]), 4),
            "n_points": len(points), "x_range": [round(float(x.min()), 4),
                                                 round(float(x.max()), 4)]}


def main():
    d2 = json.loads((REPO / "artifacts/h8_d2_response_curves.json").read_text())
    orig = [(p[0], p[1], p[2]) for p in d2["coder_points"]]
    m4 = [p for p in orig if "M4" in p[2]]
    kept = [p for p in orig if "M4" not in p[2]]

    new = []
    for fn, label in NEW_7B:
        c = load_cell(fn)
        if c:
            new.append((c[0], c[1], label))
    augmented = kept + new

    fits = {
        "original_as_published": fit([(p[0], p[1]) for p in orig]),
        "m4_removed": fit([(p[0], p[1]) for p in kept]),
        "m4_removed_plus_new_7b": fit([(p[0], p[1]) for p in augmented]),
    }

    # --- prediction 1: 7B near-match points on the imitation line, small models below
    def resid(p):
        return round(p[1] - p[0], 4)   # delta_cond - delta_art == cond - artifact

    is7b = lambda lab: "7B" in lab
    near = lambda dart: -0.12 <= dart <= 0.03
    sevens = [(p, resid(p)) for p in augmented if is7b(p[2]) and near(p[0])]
    smalls = [(p, resid(p)) for p in augmented if not is7b(p[2]) and near(p[0])]
    p1_hit = bool(sevens and smalls
                  and max(abs(r) for _, r in sevens) < 0.03
                  and max(r for _, r in smalls) <= -0.05)

    f_aug = fits["m4_removed_plus_new_7b"]
    p2_hit = bool(f_aug and f_aug["vertex_interior"] and f_aug["r2"] >= 0.6
                  and f_aug["convex"])
    p3_hit = not (p1_hit or p2_hit)

    print("=== D2 Coder points ===")
    for p in orig:
        tag = "  <-- RETRACTED (P10 R4)" if "M4" in p[2] else ""
        print(f"  Δart {p[0]:+.4f}  Δcond {p[1]:+.4f}  resid {resid(p):+.4f}  {p[2]}{tag}")
    print("  --- added (well-powered, post-D2) ---")
    for p in new:
        print(f"  Δart {p[0]:+.4f}  Δcond {p[1]:+.4f}  resid {resid(p):+.4f}  {p[2]}")

    print("\n=== fits ===")
    for k, v in fits.items():
        if v is None:
            print(f"  {k}: too few points")
            continue
        print(f"  {k}: vertex {v['vertex_dart']:+.4f} interior={v['vertex_interior']} "
              f"convex={v['convex']} R2={v['r2']} n={v['n_points']}")

    print("\n=== residual separation (cond - artifact), near-match window ===")
    print(f"  7B cells      : {[r for _, r in sevens]}")
    print(f"  <=3B cells    : {[r for _, r in smalls]}")

    print(f"\nP1 (55%) no single Coder trough / scale-pooled : {'HIT' if p1_hit else 'MISS'}")
    print(f"P2 (30%) trough survives, shifted vertex       : {'HIT' if p2_hit else 'MISS'}")
    print(f"P3 (15%) underdetermined                       : {'HIT' if p3_hit else 'MISS'}")

    out = {
        "_label": "Phase 10 R6 — D2 refit after the M4 retraction [PHASE_10.md R6]",
        "prereg_commit": "f66632d",
        "retracted_point": m4,
        "original_points": orig, "added_points": new,
        "fits": fits,
        "residuals_near_match": {
            "window_dart": [-0.12, 0.03],
            "coder_7b": [{"label": p[2], "dart": p[0], "resid": r} for p, r in sevens],
            "coder_le_3b": [{"label": p[2], "dart": p[0], "resid": r} for p, r in smalls],
        },
        "predictions": {"p1_scale_pooled": {"odds": 0.55, "hit": p1_hit},
                        "p2_trough_survives": {"odds": 0.30, "hit": p2_hit},
                        "p3_underdetermined": {"odds": 0.15, "hit": p3_hit}},
        "d2_as_published": {"vertex": d2["coder_trough_dart"],
                            "deepest": d2["coder_deepest"],
                            "r2": d2["coder_quad_r2"]},
    }
    (REPO / "artifacts/h10_r6_d2_refit.json").write_text(json.dumps(out, indent=2))
    print("\nwrote artifacts/h10_r6_d2_refit.json")


if __name__ == "__main__":
    main()
