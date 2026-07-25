#!/usr/bin/env python3
"""Phase 10 R3 instrument diagnostic — why the Δ_art target was missed.

R3 selected on seed 71 and measured on seed 89, so the SAME 30 problems carry two
independent 8-candidate i.i.d. estimates. That gives a direct, free measurement of
the seed-to-seed noise in the quantity every matched cell is targeted against.

Exploratory/diagnostic, explicitly separated from the confirmatory gate (§10): it
explains an instrument miss and reopens no verdict.

Writes artifacts/h10_r3_instrument.json.
"""
import json
import statistics as st
from pathlib import Path

REPO = Path(__file__).parents[1]
R = REPO / "runs/modal"


def main():
    g71 = json.loads((R / "j10_r3_selsweep_cand.json").read_text())
    r71 = json.loads((R / "j10_r3_selsweep_res.json").read_text())
    iid71 = {x["qid"]: st.mean(c["frac"] for c in row) for x, row in zip(g71, r71)}

    adj = json.loads((REPO / "artifacts/h10_r3_coder7b_truematch.json").read_text())
    cand89 = json.loads((R / "j8_cand_R3_coder7b_truematch.json").read_text())
    res89 = json.loads((R / "j8_res_R3_coder7b_truematch.json").read_text())
    n = adj["n"]
    qids = [g["qid"] for g in cand89[:n]]
    iid89 = {q: st.mean(x["frac"] for x in row) for q, row in zip(qids, res89[:n])}

    common = [q for q in qids if q in iid71]
    d = [iid89[q] - iid71[q] for q in common]
    sd = st.stdev(d)
    se = sd / len(d) ** 0.5

    m4 = json.loads((REPO / "artifacts/h7_matched_M4_coder7b.json").read_text())
    c = adj["cell"]

    out = {
        "_label": "Phase 10 R3 instrument diagnostic [PHASE_10.md R3]",
        "kind": "exploratory diagnostic — separated from the confirmatory gate",
        "n_problems": len(common),
        "candidates_per_problem": 8,
        "iid_seed71_mean": round(st.mean(iid71[q] for q in common), 4),
        "iid_seed89_mean": round(st.mean(iid89[q] for q in common), 4),
        "subset_mean_shift": round(st.mean(d), 4),
        "per_problem_abs_diff_mean": round(st.mean(abs(x) for x in d), 4),
        "per_problem_abs_diff_max": round(max(abs(x) for x in d), 4),
        "per_problem_diff_sd": round(sd, 4),
        "se_of_subset_mean": round(se, 4),
        "on_target_tolerance_used": 0.03,
        "tolerance_in_SE": round(0.03 / se, 2),
        "predicted_delta_art": adj["predicted_delta_art"],
        "achieved_delta_art": adj["achieved_delta_art"],
        "targeting_miss": round(abs(adj["achieved_delta_art"]
                                    - adj["predicted_delta_art"]), 4),
        "finding": (
            "The i.i.d. estimate at 8 candidates/problem carries a per-problem sd of "
            f"{sd:.3f}, so the subset mean has SE ~{se:.4f}. The on-target tolerance "
            "(0.03) was therefore ~1 SE of the very quantity being targeted, and the "
            f"observed miss ({abs(adj['achieved_delta_art'] - adj['predicted_delta_art']):.4f}) "
            "is ~1 SE. The independent selection/measurement split is still correct — "
            "it removes selection-on-noise — but it cannot remove sampling noise in "
            "the measurement itself. Hitting a Δ_art target to +/-0.03 requires more "
            "candidates per problem for the i.i.d. estimate, not a different seed scheme."
        ),
        "record_wide_implication": (
            "Every matched cell's relational position (Phases 7-10) is known only to "
            f"about +/-{se:.2f} at 8 candidates/problem. 'On-target' bands used in the "
            "record (+/-0.05 in Phase 7/8, +/-0.08 in Phase 9) are 2-3 SE wide, so "
            "differences in Δ_art below ~0.06 between cells are not resolvable, and the "
            "D2 trough location (-0.092, LOO [-0.12,-0.03]) is fit on points each "
            "carrying this positional uncertainty."
        ),
        "post_hoc_observation_NOT_a_result": {
            "note": ("R3 landed at Δ_art -0.0396, near-identical to M4's -0.0393, but "
                     "R3 was pre-registered to test Δ_art ~ 0 and is OFF-TARGET (branch "
                     "D). The comparison below is a POINTER requiring its own "
                     "pre-registered test; it is not an adjudication and no claim is "
                     "drawn from it."),
            "M4": {"n": m4["n_problems"], "seed": 17,
                   "delta_art": m4["actual_delta_art"],
                   "iid": m4["mean_iid_e0"], "artifact": m4["mean_copy_null"],
                   "cond": m4["mean_cond_e1"],
                   "cond_minus_artifact": round(m4["mean_cond_e1"] - m4["mean_copy_null"], 4),
                   "p_below_iid": m4["p_one_sided_cond_below_iid"]},
            "R3": {"n": c["n_problems"], "seed": 89,
                   "delta_art": c["actual_delta_art"],
                   "iid": c["mean_iid_e0"], "artifact": c["mean_copy_null"],
                   "cond": c["mean_cond_e1"],
                   "cond_minus_artifact": adj["residual_cond_minus_artifact"],
                   "p_below_artifact": adj["p_one_sided_cond_below_artifact"]},
            "confounds_preventing_adjudication": [
                "different problem subsets",
                "different absolute levels (M4 artifact 0.663 vs R3 0.708)",
                "R3 off its own pre-registered target",
            ],
        },
    }
    (REPO / "artifacts/h10_r3_instrument.json").write_text(json.dumps(out, indent=2))
    print(json.dumps({k: v for k, v in out.items()
                      if not isinstance(v, dict)}, indent=2))
    print("\nwrote artifacts/h10_r3_instrument.json")


if __name__ == "__main__":
    main()
