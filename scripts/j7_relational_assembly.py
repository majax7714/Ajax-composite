"""Phase 7 P0.2 — the relational assembly ([PHASE_7.md] P0.2).

Joins EVERY code-channel cell in the record onto the relational plane
(Delta_art, Delta_cond), where

    Delta_art  = artifact_frac (copy-null) - own i.i.d. frac   (x: where the
                 conditioning stimulus sits relative to the model's own quality)
    Delta_cond = conditioned frac - own i.i.d. frac            (y: the response)

The whole point of Phase 7 is visible on this plane: every non-Coder "friendly"
cell was measured on the LIFT ARM (Delta_art >= +0.13); the sink lives in the
STRADDLE (Delta_art ~ 0), which no non-Coder model has ever occupied. This figure
is committed BEFORE the matched-artifact battery (P1) so the new M-cells land on a
pre-existing plot rather than a post-hoc one.

Pure CPU; reads only committed artifacts. Emits artifacts/h7_relational_assembly.json
and prints an ASCII scatter. Re-run after each M-cell lands to place it.
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def _art(rel):
    p = REPO / rel
    return json.loads(p.read_text()) if p.exists() else None


# --- the record's code-channel cells, from committed artifacts ---
# Each row: (key, label, params_B, diet, source_of_iid_cond_copy)
def _collect():
    rows = []
    sc = _art("artifacts/h6_size_curve.json")
    h1 = _art("artifacts/h1_cross_family.json")

    # 5 Coder-line + general points (h6_size_curve.json)
    scmap = {
        "qwen05b": ("Coder-0.5B", 0.5, "coder"),
        "qwen15b": ("Coder-1.5B", 1.5, "coder"),
        "qwen3b": ("Coder-3B", 3.0, "coder"),
        "qwen7b": ("Coder-7B", 7.0, "coder"),
        "qwen15b_general": ("general-1.5B", 1.5, "general"),
    }
    if sc:
        for k, (label, pb, diet) in scmap.items():
            d = sc["points"].get(k)
            if not isinstance(d, dict):
                continue
            rows.append(_row(label, pb, diet, d["iid"], d["cond"], d["copy"],
                             below_both=d["below_both"], sink_sig=d["sink_sig"]))

    # DeepSeek-1.3B + StarCoder2-3B (h1_cross_family.json, same 44 artifacts)
    if h1:
        for fam, label, pb, diet in [
            ("deepseek", "DeepSeek-1.3B", 1.3, "organic"),
            ("starcoder2", "StarCoder2-3B", 3.0, "organic"),
        ]:
            f = h1["families"][fam]["d2c"]
            iid = f["e0_mean_frac_iid_null"]
            cond = f["e1_mean_frac_conditioned"]
            copy = f["copy_null_artifact_frac"]
            # p_one_sided_sink here is P(cond >= copy) style; below-both needs cond<both
            below_both = (cond < copy) and (cond < iid)
            rows.append(_row(label, pb, diet, iid, cond, copy,
                             below_both=below_both, sink_sig=below_both and False))
    return rows


def _row(label, pb, diet, iid, cond, copy, below_both, sink_sig):
    d_art = copy - iid
    d_cond = cond - iid
    # relational region on the x-axis
    if d_art >= 0.13:
        arm = "LIFT-ARM"
    elif d_art <= -0.08:
        arm = "OVER-QUALITY"
    else:
        arm = "STRADDLE"
    # behavior on the y-axis
    if d_cond <= -0.05:
        beh = "SINK" if below_both else "DRAG"
    elif d_cond >= 0.05:
        beh = "LIFT"
    else:
        beh = "FLAT"
    return {"label": label, "params_B": pb, "diet": diet,
            "iid": round(iid, 4), "cond": round(cond, 4), "copy": round(copy, 4),
            "delta_art": round(d_art, 4), "delta_cond": round(d_cond, 4),
            "arm": arm, "behavior": beh, "below_both": below_both}


def _ascii_scatter(rows):
    """Delta_art (x, -0.20..+0.30) vs Delta_cond (y, -0.20..+0.20)."""
    W, H = 51, 17
    xlo, xhi = -0.20, 0.30
    ylo, yhi = -0.20, 0.20
    grid = [[" "] * W for _ in range(H)]

    def cx(x):
        return min(W - 1, max(0, round((x - xlo) / (xhi - xlo) * (W - 1))))

    def cy(y):
        return min(H - 1, max(0, round((yhi - y) / (yhi - ylo) * (H - 1))))

    # axes
    y0 = cy(0.0)
    x0 = cx(0.0)
    for j in range(W):
        grid[y0][j] = "-"
    for i in range(H):
        grid[i][x0] = "|"
    grid[y0][x0] = "+"
    # straddle band edges (x = -0.08 and +0.13)
    for xe in (-0.08, 0.13):
        c = cx(xe)
        for i in range(H):
            if grid[i][c] == " ":
                grid[i][c] = ":"
    # points (letter markers)
    marks = []
    for idx, r in enumerate(rows):
        ch = chr(ord("a") + idx)
        i, j = cy(r["delta_cond"]), cx(r["delta_art"])
        grid[i][j] = ch.upper() if r["below_both"] else ch
        marks.append((ch, r))
    lines = ["".join(row) for row in grid]
    out = []
    out.append(f"  Delta_cond (y)  [+{yhi:.2f} top .. {ylo:.2f} bottom]   "
               f"Delta_art (x) [{xlo:.2f} .. +{xhi:.2f}]")
    out.append("  ':' = straddle band edges (-0.08, +0.13);  '+' = origin (matched, Delta_art=0)")
    for ln in lines:
        out.append("  " + ln)
    out.append("  legend (UPPER = below-both-nulls sink):")
    for ch, r in marks:
        out.append(f"    {ch}/{ch.upper()} = {r['label']:14s} "
                   f"art {r['delta_art']:+.3f}  cond {r['delta_cond']:+.3f}  "
                   f"[{r['arm']}, {r['behavior']}]")
    return "\n".join(out)


def main():
    rows = _collect()
    rows.sort(key=lambda r: r["delta_art"])
    print(f"{'label':16s} {'B':>4s} {'diet':>8s} {'iid':>6s} {'cond':>6s} "
          f"{'copy':>6s} {'d_art':>7s} {'d_cond':>7s} {'arm':>12s} {'beh':>5s}")
    print("-" * 92)
    for r in rows:
        print(f"{r['label']:16s} {r['params_B']:4.1f} {r['diet']:>8s} "
              f"{r['iid']:6.3f} {r['cond']:6.3f} {r['copy']:6.3f} "
              f"{r['delta_art']:+7.3f} {r['delta_cond']:+7.3f} {r['arm']:>12s} "
              f"{r['behavior']:>5s}")

    # the confound, stated numerically
    non_coder_lift = [r for r in rows if r["diet"] in ("organic", "general")]
    straddle = [r for r in rows if r["arm"] == "STRADDLE"]
    print("\n=== THE CONFOUND (why the origin line is provisional) ===")
    print("  non-Coder cells (organic/general), and their arm:")
    for r in non_coder_lift:
        print(f"    {r['label']:14s} d_art {r['delta_art']:+.3f}  -> {r['arm']}")
    print(f"  straddle-region cells (d_art in (-0.08,+0.13)): "
          f"{[r['label'] for r in straddle]}")
    print("  -> every non-Coder cell sits on the LIFT ARM; the straddle (where the "
          "sink lives)\n     is occupied ONLY by Coder-diet models. P1 samples it off-Coder.")

    print("\n=== RELATIONAL PLANE (P0.2 figure) ===")
    print(_ascii_scatter(rows))

    out = {
        "_label": "Phase 7 P0.2 relational assembly [PHASE_7.md P0.2]",
        "axes": {"x": "delta_art = copy_null - own_iid",
                 "y": "delta_cond = conditioned - own_iid"},
        "straddle_band": [-0.08, 0.13],
        "rows": rows,
        "confound": {
            "non_coder_arms": {r["label"]: r["arm"] for r in non_coder_lift},
            "straddle_occupants": [r["label"] for r in straddle],
            "note": ("every non-Coder cell is on the lift arm (d_art>=+0.13); the "
                     "straddle where the sink lives is Coder-only. The matched "
                     "battery places non-Coder models into the straddle."),
        },
    }
    (REPO / "artifacts/h7_relational_assembly.json").write_text(
        json.dumps(out, indent=2))
    print("\nwrote artifacts/h7_relational_assembly.json")


if __name__ == "__main__":
    main()
