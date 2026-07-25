"""P0.1 (free) — does a vertex claim survive on the SINKING models alone?

Phase 10 R6 refit the Coder response curve and reported vertex Δ_art = -0.1428
(R^2 0.817, n=9). [PHASE_11.md] then read the at-match effects as "the shoulder of
the curve, not its bottom", and an outside charter proposes to build on that offset.

But R6's 9 points POOL the sinking models (1.5B/3B) with Coder-7B, which the record
has since established shows NO sink anywhere measured (four cells spanning Δ_art
-0.101 -> +0.002, all in [-0.010, -0.003]). §0.4 already flags this: "7B residuals
span [-0.037,-0.003] while <=3B span [-0.121,-0.076], non-overlapping. R6's own
pre-registered test for scale-pooling MISSED, so nothing is built on this."

So: refit on <=3B ONLY, with every committed Coder <=3B cell -- including the two
P11 powered cells and the two P9 G1 cells, which post-date the R6 fit and were never
in it -- and put a bootstrap CI on the vertex. Free, no GPU.
"""
import json
import pathlib
import random

import numpy as np

REPO = pathlib.Path(__file__).resolve().parents[1]

# (delta_art, delta_cond_minus_iid, label, n, source)
PTS = [
    (-0.0744, -0.1502, "Coder-3B (D2, Phase 8)", None, "h8_d2_response_curves"),
    (-0.0449, -0.2381, "G1d Coder-1.5B foreign", 10, "h9_2x2_G1d"),
    (-0.0444, -0.1999, "G1c Coder-1.5B self", 10, "h9_2x2_G1c"),
    (-0.0005, -0.0840, "P11 Coder-3B (powered)", 39, "h11_coder3b"),
    (+0.0016, -0.0638, "P11 Coder-1.5B (powered)", 44, "h11_coder1p5b"),
    (+0.0260, -0.0947, "Coder-1.5B (D2, Phase 8)", None, "h8_d2_response_curves"),
    (+0.0814, +0.0443, "M5 Coder-0.5B", 43, "h7_matched_M5_coder0p5b"),
    (+0.2837, +0.1781, "Coder-0.5B (D2, Phase 8)", None, "h8_d2_response_curves"),
]
SEED = 229
B = 4000


def fit(pts):
    x = np.array([p[0] for p in pts], float)
    y = np.array([p[1] for p in pts], float)
    if len(pts) < 4:
        return None
    c = np.polyfit(x, y, 2)
    yh = np.polyval(c, x)
    ss_res = float(((y - yh) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    vx = float(-c[1] / (2 * c[0])) if c[0] != 0 else float("nan")
    return {"vertex": vx, "r2": r2, "convex": bool(c[0] > 0),
            "interior": bool(x.min() < vx < x.max()),
            "n": len(pts), "x_range": [float(x.min()), float(x.max())]}


def boot_vertex(pts, b=B, seed=SEED):
    """Case-resampling bootstrap over cells."""
    rng = random.Random(seed)
    out = []
    n = len(pts)
    for _ in range(b):
        s = [pts[rng.randrange(n)] for _ in range(n)]
        if len({p[0] for p in s}) < 3:
            continue
        f = fit(s)
        if f and np.isfinite(f["vertex"]):
            out.append(f["vertex"])
    out.sort()
    return out


def report(label, pts):
    f = fit(pts)
    if not f:
        print(f"\n{label}: too few points to fit ({len(pts)})")
        return None
    bv = boot_vertex(pts)
    lo, hi = bv[int(0.025 * len(bv))], bv[int(0.975 * len(bv))]
    frac0 = sum(1 for v in bv if v > 0) / len(bv)
    print(f"\n--- {label} (n={f['n']}, x in [{f['x_range'][0]:+.4f},{f['x_range'][1]:+.4f}]) ---")
    print(f"  vertex {f['vertex']:+.4f}   R^2 {f['r2']:.3f}   convex {f['convex']}   "
          f"interior {f['interior']}")
    print(f"  bootstrap vertex CI95 [{lo:+.4f}, {hi:+.4f}]  "
          f"(width {hi - lo:.3f}; {frac0:.1%} of resamples put it above 0)")
    covers0 = lo <= 0 <= hi
    print(f"  -> CI covers Delta_art = 0? {'YES — no vertex offset is established' if covers0 else 'NO'}")
    return {"vertex": round(f["vertex"], 4), "r2": round(f["r2"], 4),
            "convex": f["convex"], "interior": f["interior"], "n": f["n"],
            "boot_ci95": [round(lo, 4), round(hi, 4)], "covers_zero": bool(covers0),
            "x_range": [round(v, 4) for v in f["x_range"]]}


print("=" * 74)
print("P0.1 — vertex audit on the SINKING scales only (Coder <=3B)")
print("=" * 74)
print(f"{'Delta_art':>10} {'Delta_cond':>11} {'n':>4}  label")
for p in sorted(PTS):
    print(f"{p[0]:>+10.4f} {p[1]:>+11.4f} {str(p[3]):>4}  {p[2]}")

res = {}
res["all_le3b"] = report("ALL Coder <=3B cells", PTS)
res["le3b_no_n10"] = report("Coder <=3B, EXCLUDING the two n=10 G1 cells",
                            [p for p in PTS if not (p[3] and p[3] <= 10)])
res["le3b_powered_only"] = report("Coder <=3B, powered/n>=39 cells only",
                                  [p for p in PTS if p[3] and p[3] >= 39])

r6 = json.loads((REPO / "artifacts/h10_r6_d2_refit.json").read_text())
print("\n" + "=" * 74)
print("For contrast — R6 as published (POOLS 7B, which has no sink anywhere):")
print(f"  vertex {r6['fits']['m4_removed_plus_new_7b']['vertex_dart']:+.4f}  "
      f"R^2 {r6['fits']['m4_removed_plus_new_7b']['r2']:.3f}  "
      f"n={r6['fits']['m4_removed_plus_new_7b']['n_points']}")
print("=" * 74)

(REPO / "artifacts/h16_p0_vertex_audit.json").write_text(json.dumps(
    {"_label": "P0.1 free — vertex audit on Coder <=3B only [PHASE_16.md P0.1]",
     "_note": ("R6's -0.1428 vertex pools 7B (no sink at any measured position) with "
               "the sinking scales. This refits <=3B alone and bootstraps the vertex."),
     "seed": SEED, "n_bootstrap": B,
     "points": [{"delta_art": p[0], "delta_cond": p[1], "label": p[2],
                 "n": p[3], "source": p[4]} for p in PTS],
     "fits": res,
     "r6_pooled_for_contrast": r6["fits"]["m4_removed_plus_new_7b"]}, indent=2))
print("\nwrote artifacts/h16_p0_vertex_audit.json")
