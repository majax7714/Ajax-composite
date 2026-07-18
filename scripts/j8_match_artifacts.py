"""Phase 8 C-cell artifact miner ([PHASE_8.md] C2, C4).

Same fixed donor pool + mining protocol as Phase 7 (Qwen2.5-Coder-1.5B-base
LCB-easy), custom targets/bands per confound cell:
  C2  DeepSeek-1.3B at Delta_art = -0.04  -> donor artifacts ~ (iid 0.362 - 0.04) = 0.322
  C4  Qwen2.5-Coder-7B at match, WIDER band +/-0.10 (n>=40 unreachable; ceiling ~37)

C3 (phi) is two-phase (its i.i.d. is measured first, then mined) and is emitted by the
Modal entrypoint, not here. Emits artifacts/h8_c_artifacts.json (C2, C4).
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# (cell, model, target_artifact_frac, band_halfwidth, note)
CELLS = [
    ("C2_deepseek_below0", "deepseek-ai/deepseek-coder-1.3b-base", 0.322, 0.05,
     "DeepSeek at Delta_art=-0.04 (iid 0.362): closes the band asymmetry (no clean "
     "model measured at Delta_art<=0)"),
    ("C4_coder7b_widerN", "Qwen/Qwen2.5-Coder-7B", 0.659, 0.10,
     "Coder-7B at match, wider band +/-0.10 -> n~37 (40 unreachable from this donor); "
     "confirms/bounds the n=20 Phase-7 sink"),
]


def _load_donor():
    cand = json.loads((REPO / "runs/modal/lcb_cand_lcb_r2_base_T08.json").read_text())
    res = json.loads((REPO / "runs/modal/lcb_res_lcb_r2_base_T08.json").read_text())
    qids = res["question_ids"]
    return qids, dict(zip(qids, cand["codes"])), dict(zip(qids, res["results"]))


def _mine(target, band, qids, codes_by_qid, rows_by_qid):
    lo, hi = target - band, target + band
    arts, dropped = [], []
    for qid in qids:
        rows, codes = rows_by_qid[qid], codes_by_qid[qid]
        inb = [(i, r) for i, r in enumerate(rows) if lo <= r["frac"] <= hi and codes[i]]
        if not inb:
            dropped.append(qid)
            continue
        i, r = min(inb, key=lambda ir: (abs(ir[1]["frac"] - target), ir[0]))
        arts.append({"qid": qid, "cand_idx": i, "code": codes[i], "frac": r["frac"],
                     "n_tests": r["n_tests"], "n_failed": r["n_tests"] - r["n_passed"]})
    return arts, dropped


def main():
    qids, cb, rb = _load_donor()
    out = {"_label": "Phase 8 C-cell matched sets [PHASE_8.md C2/C4]",
           "donor": "runs/modal/lcb_cand_lcb_r2_base_T08.json (Qwen2.5-Coder-1.5B-base)",
           "cells": {}}
    print(f"{'cell':22s} {'model':40s} {'tgt':>6s} {'band':>5s} {'n':>4s} {'mean_art':>9s}")
    print("-" * 92)
    for key, model, target, band, note in CELLS:
        arts, dropped = _mine(target, band, qids, cb, rb)
        n = len(arts)
        ma = sum(a["frac"] for a in arts) / n if n else float("nan")
        print(f"{key:22s} {model:40s} {target:6.3f} {band:5.2f} {n:4d} {ma:9.3f}")
        out["cells"][key] = {"model": model, "target_artifact_frac": target,
                             "band": [round(target - band, 4), round(target + band, 4)],
                             "band_halfwidth": band, "note": note, "n": n,
                             "mean_artifact_frac": round(ma, 4) if n else None,
                             "dropped_count": len(dropped), "artifacts": arts}
    (REPO / "artifacts/h8_c_artifacts.json").write_text(json.dumps(out, indent=2))
    print("\nwrote artifacts/h8_c_artifacts.json")


if __name__ == "__main__":
    main()
