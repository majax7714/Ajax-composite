"""Phase 7 P1 — matched-artifact miner ([PHASE_7.md] P1).

Mines per-model matched artifact sets from the FIXED donor pool (the
Qwen2.5-Coder-1.5B-base LCB-easy enriched pool that produced the original 0.494 set;
its `model` field is Qwen/Qwen2.5-Coder-1.5B — note it is Coder-diet, not general
Qwen: relevant to the Phase-8 provenance confound) so that each model is
conditioned at its OWN quality match (Delta_art ~ 0), holding artifact SOURCE
constant while artifact LEVEL moves. This repairs the position confound named in
[PHASE_7.md] section 0: the fixed-0.494 design conditioned every model on the same
stimulus while model quality swept 0.21 -> 0.66, so "diet" and "position" were
never separated.

Design rules (pre-registered, [PHASE_7.md] P1):
  - Fixed donor: runs/modal/lcb_cand_lcb_r2_base_T08.json (+ _res_) ONLY. Source
    never switches; only the mined LEVEL moves per model.
  - Target = the model's own global i.i.d. frac (record value). Band = target +/- 0.05.
  - One matched artifact per problem: the in-band donor candidate nearest the target
    (deterministic tie-break by candidate index). Problems with no in-band candidate
    are DROPPED and counted (no donor switch, no band widening under this script).
  - n >= 30 in-band problems is the pre-registered minimum cell size. Cells below it
    are emitted and FLAGGED, not silently dropped.
  - Emits matched sets in the exact _d2c_artifacts() schema so the Modal runner
    consumes them unchanged.

Pure CPU; reads only committed pools. Emits artifacts/h7_matched_artifacts.json.
The Modal j7 battery reads that file; own-iid (E0) and conditioned (E1) are measured
per cell on the run, and actual Delta_art (copy_null - measured E0) is reported then.
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BAND = 0.05          # +/- half-width around the target
MIN_N = 30           # pre-registered minimum cell size

# Target = model's own global i.i.d. frac on the record (the level we match TO).
# Sources: h6_size_curve.json (Coder line + general), h1_cross_family.json (organic).
CELLS = [
    ("M5_coder0p5b", "Qwen2.5-Coder-0.5B", 0.21082, "coder",   "Coder, weak end — matched"),
    ("M2_general1p5b", "Qwen2.5-1.5B",      0.32411, "general", "non-Coder diet, same fam/arch/scale — repairs P6 control"),
    ("M3_starcoder2_3b", "bigcode/starcoder2-3b", 0.35850, "organic", "second organic family at straddle"),
    ("M1_deepseek1p3b", "deepseek-ai/deepseek-coder-1.3b-base", 0.36180, "organic", "MOST DISCRIMINATING: non-Coder organic at straddle"),
    ("M4_coder7b", "Qwen2.5-Coder-7B",      0.65902, "coder",   "does the Coder sink reappear at scale when straddle restored"),
]


def _load_donor():
    cand = json.loads((REPO / "runs/modal/lcb_cand_lcb_r2_base_T08.json").read_text())
    res = json.loads((REPO / "runs/modal/lcb_res_lcb_r2_base_T08.json").read_text())
    qids = res["question_ids"]
    codes_by_qid = dict(zip(qids, cand["codes"]))
    rows_by_qid = dict(zip(qids, res["results"]))
    return qids, codes_by_qid, rows_by_qid


def _mine_cell(target, qids, codes_by_qid, rows_by_qid):
    lo, hi = target - BAND, target + BAND
    arts, dropped = [], []
    for qid in qids:
        rows = rows_by_qid[qid]
        codes = codes_by_qid[qid]
        # in-band candidates with non-empty code
        inb = [(i, r) for i, r in enumerate(rows)
               if lo <= r["frac"] <= hi and codes[i]]
        if not inb:
            dropped.append(qid)
            continue
        # nearest to target; deterministic tie-break by candidate index
        i, r = min(inb, key=lambda ir: (abs(ir[1]["frac"] - target), ir[0]))
        arts.append({"qid": qid, "cand_idx": i, "code": codes[i],
                     "frac": r["frac"], "n_tests": r["n_tests"],
                     "n_failed": r["n_tests"] - r["n_passed"]})
    return arts, dropped


def main():
    qids, codes_by_qid, rows_by_qid = _load_donor()
    out = {"_label": "Phase 7 P1 matched artifact sets [PHASE_7.md P1]",
           "donor": "runs/modal/lcb_cand_lcb_r2_base_T08.json (Qwen2.5-Coder-1.5B-base, LCB-easy, T=0.8)",
           "band_halfwidth": BAND, "min_n": MIN_N, "cells": {}}

    print(f"{'cell':20s} {'model':40s} {'target':>7s} {'n':>4s} {'mean_art':>9s} "
          f"{'dropped':>8s} {'status':>10s}")
    print("-" * 108)
    for key, model, target, diet, note in CELLS:
        arts, dropped = _mine_cell(target, qids, codes_by_qid, rows_by_qid)
        n = len(arts)
        mean_art = sum(a["frac"] for a in arts) / n if n else float("nan")
        status = "OK" if n >= MIN_N else f"SHORT({n})"
        print(f"{key:20s} {model:40s} {target:7.3f} {n:4d} {mean_art:9.3f} "
              f"{len(dropped):8d} {status:>10s}")
        out["cells"][key] = {
            "model": model, "target_iid": target, "diet": diet, "note": note,
            "band": [round(target - BAND, 4), round(target + BAND, 4)],
            "n": n, "min_n_met": n >= MIN_N,
            "mean_artifact_frac": round(mean_art, 4) if n else None,
            "expected_delta_art": round(mean_art - target, 4) if n else None,
            "dropped_count": len(dropped),
            "artifacts": arts,   # exact _d2c_artifacts() schema
        }

    # --- P1 source side cell feasibility (self-artifacts vs donor at fixed Delta_art) ---
    # A model's OWN pool mined at its OWN match, paired against the donor-mined set.
    # Measured here so the pre-reg records whether it is runnable BEFORE any spend.
    side = {}
    donor_by_qid = {q: rows_by_qid[q] for q in qids}
    for fam, tgt in [("deepseek", 0.36180), ("starcoder2", 0.35850)]:
        try:
            sres = json.loads((REPO / f"runs/modal/h1_res_lcb_{fam}.json").read_text())
            scand = json.loads((REPO / f"runs/modal/h1_cand_lcb_{fam}.json").read_text())
        except FileNotFoundError:
            side[fam] = {"self_pool": "absent"}
            continue
        lo, hi = tgt - BAND, tgt + BAND
        sqids = [c["qid"] for c in scand]
        self_cov = [sqids[i] for i, prob in enumerate(sres)
                    if any(lo <= r["frac"] <= hi for r in prob)]
        paired = [q for q in self_cov if q in donor_by_qid
                  and any(lo <= r["frac"] <= hi for r in donor_by_qid[q])]
        side[fam] = {"target": tgt, "self_in_band": len(self_cov),
                     "paired_self_and_donor": len(paired)}
    out["side_cell_source"] = {
        "purpose": "price self-vs-donor artifact source at identical Delta_art",
        "coverage": side,
        "ruling": ("DEFERRED-BY-COVERAGE: single-model self-pools are too bimodal "
                   "in the mid-band to sustain a matched self-artifact set (paired "
                   "n = 3-4). The source variable stays unpriced; a future "
                   "generated-artifact design (artifacts synthesized to the target "
                   "band, not mined) is the path. This is the same bimodality that "
                   "MOTIVATES the fixed-donor rule."),
    }
    print("\n--- side cell (source variable) feasibility ---")
    for fam, d in side.items():
        print(f"  {fam}: {d}")
    print("  -> DEFERRED-BY-COVERAGE (paired n = 3-4; source stays unpriced)")

    (REPO / "artifacts/h7_matched_artifacts.json").write_text(json.dumps(out, indent=2))
    print("\nnote: mean_art ~ target by construction => expected Delta_art ~ 0 (matched).")
    print("      actual Delta_art (copy_null - MEASURED own-iid) is reported after the run.")
    print("wrote artifacts/h7_matched_artifacts.json")


if __name__ == "__main__":
    main()
