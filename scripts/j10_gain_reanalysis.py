#!/usr/bin/env python3
"""Phase 10 R1 — the gain re-analysis (free; no GPU).

Re-expresses every conditioning cell in the record on the residual

    residual = cond - artifact  ==  Δ_cond - Δ_art  ==  delta_cond_minus_copy

i.e. how far the conditioned output lands below the artifact it was shown, and on
the gain Δ_cond/Δ_art. Pre-registered in docs/PHASE_10.md §R1 at commit 08870fe;
predictions frozen BEFORE this ran.

Writes artifacts/h10_gain_reanalysis.json.
"""
import glob
import json
import os
import statistics as st
from pathlib import Path

REPO = Path(__file__).parents[1]
CLEAN_BAND = 0.03   # prediction 2's band around 0

# ---- diet classification (frozen; from the record's own scope lines) ----
def diet_of(model: str, recorded: str | None) -> str:
    m = (model or "").lower()
    if "qwen2.5-coder" in m or "qwen2_5-coder" in m:
        return "coder"
    if "phi-1" in m or "phi1" in m:
        return "synthetic"
    if "deepseek-coder" in m or "starcoder" in m or "qwen2.5-1.5b" in m:
        return "noncoder"
    return recorded or "unknown"


def family_of(model: str) -> str:
    m = (model or "").lower()
    for tag, name in (("deepseek", "DeepSeek"), ("starcoder", "StarCoder2"),
                      ("phi", "phi-1")):
        if tag in m:
            return name
    if "qwen2.5-coder" in m:
        for s in ("0.5b", "1.5b", "3b", "7b"):
            if s in m:
                return f"Qwen-Coder-{s.upper()}"
        return "Qwen-Coder"
    if "qwen" in m:
        return "Qwen-general"
    return model or "?"


def collect():
    """Harvest every cell carrying iid + cond + a copy/artifact null."""
    cells = []
    for f in sorted(glob.glob(str(REPO / "artifacts" / "*.json"))):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        base = os.path.basename(f)
        if not isinstance(d, dict):
            continue
        iid = d.get("mean_iid_e0")
        cond = d.get("mean_cond_e1")
        copy = d.get("mean_copy_null", d.get("mean_artifact"))
        if iid is None or cond is None or copy is None:
            continue
        dart = d.get("actual_delta_art", d.get("achieved_delta_art"))
        if dart is None:
            dart = copy - iid
        cells.append({
            "source": base,
            "cell": d.get("cell", base.replace(".json", "")),
            "model": d.get("model", "?"),
            "family": family_of(d.get("model", "")),
            "diet": diet_of(d.get("model", ""), d.get("diet")),
            "n": d.get("n", d.get("n_problems")),
            "mean_iid": round(iid, 4),
            "mean_cond": round(cond, 4),
            "mean_artifact": round(copy, 4),
            "delta_art": round(dart, 4),
            "delta_cond": round(d.get("delta_cond_minus_iid", cond - iid), 4),
            "residual": round(cond - copy, 4),
            "gain": round((cond - iid) / dart, 3) if abs(dart) >= 0.02 else None,
            "sink_flag": d.get("matched_sink_signature"),
        })

    # The original D2c cell (Phase 3b) uses the older field names.
    p = REPO / "artifacts" / "dmeasure_d2c_partial_credit.json"
    if p.exists():
        d = json.load(open(p))
        iid, cond, copy = d["mean_iid_null"], d["mean_frac_generated"], d["mean_copy_null"]
        cells.append({
            "source": p.name, "cell": "D2c_original", "model": "Qwen2.5-Coder-1.5B",
            "family": "Qwen-Coder-1.5B", "diet": "coder", "n": d.get("n_artifacts"),
            "mean_iid": round(iid, 4), "mean_cond": round(cond, 4),
            "mean_artifact": round(copy, 4), "delta_art": round(copy - iid, 4),
            "delta_cond": round(cond - iid, 4), "residual": round(cond - copy, 4),
            "gain": round((cond - iid) / (copy - iid), 3) if abs(copy - iid) >= 0.02 else None,
            "sink_flag": d.get("verdict") == "SINK",
        })
    return cells


def main():
    cells = collect()
    coder = [c for c in cells if c["diet"] == "coder"]
    clean = [c for c in cells if c["diet"] == "noncoder"]
    synth = [c for c in cells if c["diet"] == "synthetic"]

    print(f"{len(cells)} cells: {len(coder)} coder / {len(clean)} non-coder / "
          f"{len(synth)} synthetic\n")
    hdr = f"{'cell':28s} {'family':16s} {'diet':10s} {'n':>3s} {'Δart':>7s} {'Δcond':>7s} {'resid':>7s} {'gain':>6s}"
    print(hdr); print("-" * len(hdr))
    for c in sorted(cells, key=lambda x: (x["diet"], x["delta_art"])):
        g = f"{c['gain']:6.2f}" if c["gain"] is not None else "     -"
        print(f"{c['cell'][:28]:28s} {c['family'][:16]:16s} {c['diet']:10s} "
              f"{str(c['n'] or '?'):>3s} {c['delta_art']:+7.3f} {c['delta_cond']:+7.3f} "
              f"{c['residual']:+7.3f} {g}")

    cr = [c["residual"] for c in coder]
    nr = [c["residual"] for c in clean]
    sr = [c["residual"] for c in synth]

    # --- prediction 1: no overlap on residual ---
    p1 = bool(cr and nr and max(cr) < min(nr))
    gap = round(min(nr) - max(cr), 4) if (cr and nr) else None

    # --- prediction 2: every non-coder cell within 0 ± CLEAN_BAND, all families ---
    outside = [(c["cell"], c["residual"]) for c in clean if abs(c["residual"]) > CLEAN_BAND]
    fams = sorted({c["family"] for c in clean})
    p2 = bool(not outside and len(fams) >= 3)

    # --- prediction 3: coder residual varies with Δ_art (not a constant offset) ---
    p3 = bool(cr and (max(cr) - min(cr)) >= 0.05)

    # --- prediction 4: phi between the clusters ---
    p4 = bool(sr and cr and nr and all(max(cr) < s < min(nr) for s in sr))

    print(f"\n{'='*72}\nPRE-REGISTERED PREDICTIONS (frozen at 08870fe, before this ran)\n{'='*72}")
    print(f"1 (70%) coder/non-coder separate on residual, no overlap : "
          f"{'HIT' if p1 else 'MISS'}")
    print(f"      coder residuals    [{min(cr):+.3f}, {max(cr):+.3f}]  n={len(cr)}")
    print(f"      non-coder residuals[{min(nr):+.3f}, {max(nr):+.3f}]  n={len(nr)}")
    print(f"      separation gap     {gap:+.4f}" if gap is not None else "")
    print(f"2 (55%) non-coder within 0±{CLEAN_BAND}, >=3 families       : "
          f"{'HIT' if p2 else 'MISS'}")
    print(f"      families: {', '.join(fams)}")
    if outside:
        print(f"      outside band: {outside}")
    print(f"3 (60%) coder residual varies with Δ_art (range >= 0.05) : "
          f"{'HIT' if p3 else 'MISS'}  (range {max(cr)-min(cr):.3f})")
    print(f"4 (45%) phi between the clusters                        : "
          f"{'HIT' if p4 else 'MISS'}  (phi residuals {sr})")

    hits = sum([p1, p2, p3, p4])
    rule = ("ADOPT residual as a reporting axis; R2 authorized" if p1
            else "DROP the reframe (decision rule: not rescued) — report the negative")
    print(f"\n{hits}/4 predictions hit. Decision rule → {rule}")

    out = {
        "_label": "Phase 10 R1 — gain re-analysis [PHASE_10.md R1]",
        "prereg_commit": "08870fe",
        "clean_band": CLEAN_BAND,
        "cells": cells,
        "summary": {
            "coder_residuals": {"min": min(cr), "max": max(cr), "median": st.median(cr),
                                "n": len(cr)},
            "noncoder_residuals": {"min": min(nr), "max": max(nr), "median": st.median(nr),
                                   "n": len(nr), "families": fams},
            "synthetic_residuals": sr,
            "separation_gap": gap,
        },
        "predictions": {
            "p1_no_overlap": {"odds": 0.70, "hit": p1, "gap": gap},
            "p2_clean_cluster_at_zero": {"odds": 0.55, "hit": p2, "outside": outside,
                                         "families": fams},
            "p3_coder_varies_with_dart": {"odds": 0.60, "hit": p3,
                                          "range": round(max(cr) - min(cr), 4)},
            "p4_phi_between": {"odds": 0.45, "hit": p4, "phi_residuals": sr},
        },
        "hits": hits,
        "decision": rule,
    }
    (REPO / "artifacts" / "h10_gain_reanalysis.json").write_text(json.dumps(out, indent=2))
    print("\nwrote artifacts/h10_gain_reanalysis.json")


if __name__ == "__main__":
    main()
