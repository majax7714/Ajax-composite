"""Phase 8 D2 — per-diet response curves ([PHASE_8.md] D2).

Fits Delta_cond = f(Delta_art) separately over the Coder points and the non-Coder
points from h7_relational_assembly.json. Primary read: the COder curve's own shape
(non-monotone interior trough = position-gated penalty). Secondary: the difference
curve (diet penalty), with the non-Coder curve EXTRAPOLATED below its measured range
[+0.033, +0.170] (C2 will measure it directly) — every penalty at Delta_art <= 0
carries that caveat. With 6 points/group this is a SHAPE read, not a parameter fit;
leave-one-out leverage is reported.

Pure CPU. Emits artifacts/h8_d2_response_curves.json.
"""
import json
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent


def _points():
    d = json.loads((REPO / "artifacts/h7_relational_assembly.json").read_text())
    coder, noncoder = [], []
    for r in d["rows"]:
        pt = (r["delta_art"], r["delta_cond"], r["label"])
        (coder if r["diet"] == "coder" else noncoder).append(pt)
    return sorted(coder), sorted(noncoder)


def _fit(pts, deg):
    x = np.array([p[0] for p in pts])
    y = np.array([p[1] for p in pts])
    c = np.polyfit(x, y, deg)
    yhat = np.polyval(c, x)
    ss_res = float(np.sum((y - yhat) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot else float("nan")
    return c, r2


def _trough(coef_quad):
    a, b, _ = coef_quad
    if a <= 1e-9:
        return None  # not convex → no interior minimum
    return float(-b / (2 * a))


def main():
    coder, noncoder = _points()
    print("Coder points   (Δ_art, Δ_cond):", [(round(a, 3), round(b, 3)) for a, b, _ in coder])
    print("NonCoder points(Δ_art, Δ_cond):", [(round(a, 3), round(b, 3)) for a, b, _ in noncoder])

    cq, cq_r2 = _fit(coder, 2)
    cl, cl_r2 = _fit(coder, 1)
    nq, nq_r2 = _fit(noncoder, 2)
    nl, nl_r2 = _fit(noncoder, 1)
    trough = _trough(cq)

    # primary: interior trough? deepest sink at an interior Δ_art, not an endpoint
    xs = [p[0] for p in coder]
    ys = [p[1] for p in coder]
    imin = int(np.argmin(ys))
    interior = 0 < imin < len(coder) - 1
    print(f"\nCoder quadratic: {np.round(cq,4)} R²={cq_r2:.3f}; trough(vertex) Δ_art="
          f"{trough:.3f}" if trough is not None else "\nCoder quadratic: not convex")
    print(f"Coder deepest point: Δ_cond={ys[imin]:+.3f} at Δ_art={xs[imin]:+.3f} "
          f"(INTERIOR={interior})")
    print(f"NonCoder quadratic: {np.round(nq,4)} R²={nq_r2:.3f}; linear slope {nl[0]:+.3f}")

    # secondary: difference (penalty) curve
    grid = [-0.15, -0.10, -0.05, 0.0, 0.05, 0.10, 0.15]
    nc_lo = min(p[0] for p in noncoder)
    print("\nPenalty = Coder_quad − NonCoder_quad (E=extrapolated non-Coder):")
    penalty = {}
    for g in grid:
        pen = float(np.polyval(cq, g) - np.polyval(nq, g))
        extrap = " [E]" if g < nc_lo else ""
        penalty[g] = pen
        print(f"  Δ_art {g:+.2f}: penalty {pen:+.3f}{extrap}")

    # LOO leverage on the trough location
    loo = []
    for i in range(len(coder)):
        sub = coder[:i] + coder[i + 1:]
        c, _ = _fit(sub, 2)
        t = _trough(c)
        loo.append(round(t, 3) if t is not None else None)
    print(f"\nLOO trough locations (drop each Coder point): {loo}")

    # branch determination
    if interior and trough is not None and -0.12 < trough < 0.06:
        branch = ("POSITION-GATED (penalty peaks near match, shrinks toward both arms) "
                  "— consistent with RECLASS's ambiguity-at-match story")
    elif not interior:
        branch = "MONOTONE/OFFSET — deepest point at an endpoint; re-examine"
    else:
        branch = "AMBIGUOUS interior trough outside [-0.12,0.06]"
    print("\nD2 SHAPE BRANCH:", branch)
    print("Note: 6 points/group — a shape read, not a parameter estimate; the non-Coder "
          "curve below Δ_art +0.033 is extrapolated (C2 measures it).")

    out = {"_label": "Phase 8 D2 per-diet response curves [PHASE_8.md D2]",
           "coder_points": [[a, b, l] for a, b, l in coder],
           "noncoder_points": [[a, b, l] for a, b, l in noncoder],
           "coder_quad": [round(float(x), 5) for x in cq], "coder_quad_r2": round(cq_r2, 3),
           "coder_linear_slope": round(float(cl[0]), 4),
           "noncoder_quad": [round(float(x), 5) for x in nq], "noncoder_quad_r2": round(nq_r2, 3),
           "noncoder_linear_slope": round(float(nl[0]), 4),
           "coder_trough_dart": round(trough, 4) if trough is not None else None,
           "coder_deepest": {"dart": round(xs[imin], 4), "dcond": round(ys[imin], 4),
                             "interior": interior},
           "penalty_curve": {str(k): round(v, 4) for k, v in penalty.items()},
           "noncoder_measured_min_dart": round(nc_lo, 4),
           "loo_trough_dart": loo, "shape_branch": branch}
    (REPO / "artifacts/h8_d2_response_curves.json").write_text(json.dumps(out, indent=2))
    print("\nwrote artifacts/h8_d2_response_curves.json")


if __name__ == "__main__":
    main()
