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


def _collect_matched():
    """Overlay: the Phase-7 matched cells, once landed. Each conditions its model
    at Delta_art ~ 0; the point is (actual_delta_art, delta_cond_minus_iid). Placed
    on the same plane so the sink's region is finally sampled off-Coder. Returns []
    until the h7_matched_<cell>.json files exist (pre-P1 the figure shows 7 points)."""
    order = [("M1_deepseek1p3b", "M1 DeepSeek*"), ("M2_general1p5b", "M2 general*"),
             ("M3_starcoder2_3b", "M3 StarCoder2*"), ("M4_coder7b", "M4 Coder-7B*"),
             ("M5_coder0p5b", "M5 Coder-0.5B*")]
    rows = []
    for key, label in order:
        d = _art(f"artifacts/h7_matched_{key}.json")
        if not d:
            continue
        d_art = d["actual_delta_art"]
        d_cond = d["delta_cond_minus_iid"]
        arm = ("LIFT-ARM" if d_art >= 0.13 else
               "OVER-QUALITY" if d_art <= -0.08 else "STRADDLE")
        beh = ("SINK" if d.get("matched_sink_signature") else
               "DRAG" if d_cond <= -0.05 else "LIFT" if d_cond >= 0.05 else "FLAT")
        rows.append({"label": label, "params_B": None, "diet": d.get("diet"),
                     "iid": round(d["mean_iid_e0"], 4), "cond": round(d["mean_cond_e1"], 4),
                     "copy": round(d["mean_copy_null"], 4),
                     "delta_art": round(d_art, 4), "delta_cond": round(d_cond, 4),
                     "arm": arm, "behavior": beh,
                     "below_both": bool(d.get("matched_sink_signature")),
                     "source": "matched", "n": d.get("n_problems")})
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
            "arm": arm, "behavior": beh, "below_both": below_both, "source": "record"}


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
    # points: record cells = letters (UPPER if below-both); matched overlay = digits
    marks = []
    li = di = 0
    for r in rows:
        if r.get("source") == "matched":
            di += 1
            ch = str(di)
        else:
            ch = chr(ord("a") + li)
            li += 1
        i, j = cy(r["delta_cond"]), cx(r["delta_art"])
        cell = (ch.upper() if r["below_both"] and ch.isalpha() else ch)
        grid[i][j] = cell
        marks.append((cell, r))
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
    base = _collect()
    matched = _collect_matched()
    rows = sorted(base + matched, key=lambda r: r["delta_art"])
    if matched:
        print(f"[overlay: {len(matched)} matched M-cell(s) placed — the sink region "
              f"sampled off-Coder]\n")
    print(f"{'label':16s} {'B':>4s} {'diet':>8s} {'iid':>6s} {'cond':>6s} "
          f"{'copy':>6s} {'d_art':>7s} {'d_cond':>7s} {'arm':>12s} {'beh':>5s}")
    print("-" * 92)
    for r in rows:
        pb = f"{r['params_B']:4.1f}" if r.get("params_B") is not None else "   ·"
        print(f"{r['label']:16s} {pb} {(r['diet'] or '—'):>8s} "
              f"{r['iid']:6.3f} {r['cond']:6.3f} {r['copy']:6.3f} "
              f"{r['delta_art']:+7.3f} {r['delta_cond']:+7.3f} {r['arm']:>12s} "
              f"{r['behavior']:>5s}")

    # the confound, stated numerically — over the RECORD (fixed-0.494) cells
    rec_non_coder = [r for r in base if r["diet"] in ("organic", "general")]
    rec_straddle = [r for r in base if r["arm"] == "STRADDLE"]
    print("\n=== THE CONFOUND (record cells, fixed-0.494 artifacts) ===")
    print("  non-Coder record cells (organic/general), and their arm:")
    for r in rec_non_coder:
        print(f"    {r['label']:14s} d_art {r['delta_art']:+.3f}  -> {r['arm']}")
    print(f"  record straddle-region cells: {[r['label'] for r in rec_straddle]}")
    print("  -> in the record, every non-Coder cell sits on the LIFT ARM; the straddle "
          "(where the\n     sink lives) is occupied ONLY by Coder-diet models.")
    # the matched overlay, once landed — the region finally sampled off-Coder
    if matched:
        m_straddle = [r for r in matched if r["arm"] == "STRADDLE"]
        m_sinks = [r for r in matched if r["below_both"]]
        print("\n=== MATCHED OVERLAY (Delta_art ~ 0, sink region sampled off-Coder) ===")
        for r in matched:
            print(f"    {r['label']:16s} d_art {r['delta_art']:+.3f}  d_cond "
                  f"{r['delta_cond']:+.3f}  {r['arm']:>10s}/{r['behavior']:<5s}"
                  f"{'  <-- MATCHED SINK' if r['below_both'] else ''}")
        print(f"  -> {len(m_straddle)}/{len(matched)} matched cells landed in the "
              f"straddle; matched sinks: {[r['label'] for r in m_sinks] or 'none'}")

    print("\n=== RELATIONAL PLANE (P0.2 figure) ===")
    print(_ascii_scatter(rows))

    out = {
        "_label": "Phase 7 P0.2 relational assembly [PHASE_7.md P0.2]",
        "axes": {"x": "delta_art = copy_null - own_iid",
                 "y": "delta_cond = conditioned - own_iid"},
        "straddle_band": [-0.08, 0.13],
        "rows": rows,
        "n_matched_overlaid": len(matched),
        "confound": {
            "record_non_coder_arms": {r["label"]: r["arm"] for r in rec_non_coder},
            "record_straddle_occupants": [r["label"] for r in rec_straddle],
            "matched_straddle_occupants": [r["label"] for r in matched
                                           if r["arm"] == "STRADDLE"],
            "matched_sinks": [r["label"] for r in matched if r["below_both"]],
            "note": ("in the record every non-Coder cell is on the lift arm "
                     "(d_art>=+0.13); the straddle where the sink lives is Coder-only. "
                     "The matched battery places non-Coder models into the straddle "
                     "(matched overlay rows, once landed)."),
        },
    }
    (REPO / "artifacts/h7_relational_assembly.json").write_text(
        json.dumps(out, indent=2))
    print("\nwrote artifacts/h7_relational_assembly.json")


if __name__ == "__main__":
    main()
