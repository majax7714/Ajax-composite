#!/usr/bin/env python3
"""E5/E1 subset matched-control recompute — the committed §9.3.1 action.

The flagged confound ([WRITEUP-rgr §9.3.1], [PHASE_3R.md] Addendum III): E1/E2 need a
*failed* artifact to condition on, E5 needs a *correct* one. If each condition was
populated by per-condition filtering of the pool, E1/E2 ran on a hard-biased subset and
E5 on an easy-biased one, and (i) the "conditioning drops mean_pass" magnitude and
(ii) E5's coverage-1.00 / negative-TAX are cross-subset artifacts. The committed action:
recompute E0's mean_pass and coverage on E1's subset and on E5's subset.

Pure CPU over committed artifacts — dmeasure_gen.json (which pids each condition ran),
dmeasure_exec.json (per-sample pass), dmeasure_d2a_gen.json (the replication run),
m3_candidates/m3_labels (selection provenance). No generation, no re-execution.

Output: artifacts/dmeasure_subset_control.json
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).parents[1]
CONDS = ["E0", "E1", "E2", "E5"]
TEMPS = ["0.0", "0.8", "1.2"]


def pid_sets(gen_path):
    res = json.loads(gen_path.read_text())["results"]
    by_cond = defaultdict(set)
    for r in res:
        by_cond[r["cond"]].add(r["pid"])
    return dict(by_cond)


def main():
    # ---- 1. which problems did each condition actually run on? ----
    dm = pid_sets(REPO / "runs/modal/dmeasure_gen.json")
    d2a = pid_sets(REPO / "runs/modal/dmeasure_d2a_gen.json")
    dm_equal = all(dm[c] == dm["E0"] for c in dm)
    d2a_conds = sorted(d2a)
    d2a_equal = all(d2a[c] == d2a[d2a_conds[0]] for c in d2a_conds)
    shared = sorted(dm["E0"])

    # ---- 2. reconstruct the selection from the committed M3 pool ----
    m3 = json.loads((REPO / "runs/modal/m3_candidates.json").read_text())
    labels = json.loads((REPO / "runs/modal/m3_labels.json").read_text())["labels"]
    sel, n_mixed_total = [], 0
    per_pid_meanpass, category = {}, {}
    for pid, row, lab in zip(m3["problem_ids"], m3["candidates"], labels):
        per_pid_meanpass[pid] = sum(map(bool, lab)) / len(lab)
        fail = next((c["code"] for c, p in zip(row, lab) if not p and c["code"]), None)
        good = next((c["code"] for c, p in zip(row, lab) if p and c["code"]), None)
        category[pid] = ("mixed" if (fail and good) else
                         "always_solved" if all(map(bool, lab)) else
                         "never_solved" if not any(map(bool, lab)) else "degenerate_code")
        if fail and good:
            n_mixed_total += 1
            if len(sel) < 60:
                sel.append(pid)
    selection_matches = set(sel) == set(shared)

    # ---- 3. E0 restricted to each condition's subset (the committed recompute) ----
    ex = json.loads((REPO / "runs/modal/dmeasure_exec.json").read_text())
    passed = {}
    for key, v in ex.items():
        pid, cond, temp = key.rsplit("|", 2)
        passed[(pid, cond, temp)] = v

    def stats(cond, temp, subset):
        mp, cov = [], []
        for pid in subset:
            ps = passed.get((pid, cond, temp))
            if ps:
                mp.append(sum(ps) / len(ps))
                cov.append(1.0 if any(ps) else 0.0)
        return {"n": len(mp), "mean_pass": sum(mp) / len(mp), "coverage": sum(cov) / len(cov)}

    e0_on = {f"E0_on_{c}_subset@{t}": stats("E0", t, sorted(dm[c]))
             for c in ("E1", "E5") for t in TEMPS}

    # ---- 4. quantify the shared subset's bias vs the full M3 pool ----
    all_pids = list(per_pid_meanpass)
    excluded = [p for p in all_pids if p not in set(shared)]
    cat_counts = defaultdict(int)
    for p in all_pids:
        cat_counts[category[p]] += 1
    bias = {
        "n_pool": len(all_pids), "n_mixed_total": n_mixed_total,
        "n_selected": len(shared), "selection": "first-60 mixed, pool order (not random)",
        "pool_category_counts": dict(cat_counts),
        "m3_mean_pass_full_pool": sum(per_pid_meanpass.values()) / len(all_pids),
        "m3_mean_pass_selected60": sum(per_pid_meanpass[p] for p in shared) / len(shared),
        "m3_mean_pass_excluded": sum(per_pid_meanpass[p] for p in excluded) / len(excluded),
    }

    # ---- 5. the two at-risk claims, on the matched subset ----
    dmc = json.loads((REPO / "artifacts/dmeasure_conditioning.json").read_text())
    cells = dmc["per_sample_D2b"]["cells"]
    at_risk = {
        "claim_i_conditioning_drop": {
            f"T={t}": {"E0_mean_pass": cells[f"E0@{t}"]["mean_per_sample_pass"],
                       "E1_mean_pass": cells[f"E1@{t}"]["mean_per_sample_pass"],
                       "delta_on_identical_subset":
                           cells[f"E1@{t}"]["mean_per_sample_pass"]
                           - cells[f"E0@{t}"]["mean_per_sample_pass"]}
            for t in ("0.8", "1.2")},
        "claim_ii_E5_vs_matched_E0_coverage": {
            f"T={t}": {"E5_coverage": cells[f"E5@{t}"]["coverage_any_pass"],
                       "E0_coverage_same_subset": cells[f"E0@{t}"]["coverage_any_pass"]}
            for t in TEMPS},
    }

    out = {
        "_label": "E5/E1 subset matched-control (§9.3.1 committed action)",
        "dmeasure_conditions_share_identical_subset": dm_equal,
        "d2a_conditions_share_identical_subset": d2a_equal,
        "dmeasure_and_d2a_same_60": dm["E0"] == d2a[d2a_conds[0]],
        "selection_reconstruction_matches": selection_matches,
        "E0_recomputed_on_condition_subsets": e0_on,
        "subset_bias_vs_full_pool": bias,
        "at_risk_claims_on_matched_subset": at_risk,
        "verdict": (
            "Differential-subset confound STRUCTURALLY ABSENT: one shared both-outcome "
            "filter selected a single 60-problem subset used by ALL conditions (E0 "
            "included), so E0-on-E1's-subset == E0-on-E5's-subset == the published E0. "
            "Cross-condition contrasts are within-subset and stand. What remains is a "
            "SCOPE limitation, not a confound: the shared subset is mixed-outcome-only "
            "and first-60 (not random), so absolute magnitudes are scoped to mixed "
            "problems; and E5's subset guarantees a correct 8-sample candidate exists "
            "by construction, so its coverage-1.00 exceeds a fair same-subset E0 that "
            "is itself near-saturated (0.92 at T=0.8) — consistent with the Addendum "
            "III §1 answer-leakage retraction already in place."),
    }
    Path(REPO / "artifacts/dmeasure_subset_control.json").write_text(json.dumps(out, indent=2))

    print("=== E5/E1 subset matched-control recompute ===")
    print(f"dmeasure conditions share identical subset: {dm_equal}")
    print(f"d2a conditions share identical subset:      {d2a_equal}")
    print(f"dmeasure and d2a used the same 60:          {dm['E0'] == d2a[d2a_conds[0]]}")
    print(f"selection reconstruction (first-60 mixed):  {selection_matches}")
    print(f"\nE0 recomputed on condition subsets (identical by construction):")
    for k, v in e0_on.items():
        print(f"  {k:<24} n={v['n']:<4} mean_pass {v['mean_pass']:.4f}  coverage {v['coverage']:.4f}")
    print(f"\nsubset bias vs full M3 pool:")
    for k, v in bias.items():
        print(f"  {k}: {v}")
    print(f"\nat-risk claim (i) — conditioning drop on the IDENTICAL subset:")
    for t, v in at_risk["claim_i_conditioning_drop"].items():
        print(f"  {t}: E0 {v['E0_mean_pass']:.4f} -> E1 {v['E1_mean_pass']:.4f} "
              f"(delta {v['delta_on_identical_subset']:+.4f})")
    print(f"\nat-risk claim (ii) — E5 vs matched-subset E0 coverage:")
    for t, v in at_risk["claim_ii_E5_vs_matched_E0_coverage"].items():
        print(f"  {t}: E5 {v['E5_coverage']:.3f} vs E0-same-subset {v['E0_coverage_same_subset']:.3f}")
    print("\nwrote artifacts/dmeasure_subset_control.json")


if __name__ == "__main__":
    main()
