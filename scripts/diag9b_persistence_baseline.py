#!/usr/bin/env python3
"""DIAG-9b — correct chance baseline for DIAG-9's error-type persistence.

Pre-registered in docs/DIAGNOSTICS.md (committed 2026-07-13, before this ran) after
external review flagged that DIAG-9's Sum(p_t^2)=0.422 baseline ignores WITHIN-PROBLEM
error-type clustering — the same class of error as DIAG-2's random-row CV leakage. A
problem with a runtime edge case triggers runtime errors across every sample, anchored
or not, so the pooled-marginal baseline understates chance.

The correct baseline is on disk: the within-problem same-error-type agreement of B1's
i.i.d. samples — the true chance that two failures OF THE SAME PROBLEM share a type.
FULL (register, no text anchor) and B2 (text anchor) get the same treatment.

Metrics per condition (over problems with >=2 failing candidates):
- within-problem mean pairwise same-error-type agreement among failing candidates.
For B2 additionally: adjacent-pair agreement (reproduces DIAG-9's 0.851) vs
non-adjacent-pair agreement — isolating the SPECIFIC shown candidate from problem
homogeneity. Plus no_code rate by step index (output-discipline collapse check).

EXPLORATORY / POST-HOC. Does NOT reopen the H2 gate.
"""
from __future__ import annotations

import json
import sys
from itertools import combinations
from pathlib import Path

REPO = Path(__file__).parents[1]
sys.path.insert(0, str(REPO / "src"))
from rgr.results import read_jsonl  # noqa: E402

FULL_B1 = REPO / "runs/phase2/full_b1.jsonl"
B2 = REPO / "runs/phase2/b2.jsonl"
OUT = REPO / "artifacts/diag9b_persistence_baseline.json"


def fail_types(rec: dict) -> list:
    """(step_index, error_type) for each failing step."""
    return [(s["step"], s["execution"]["error_type"])
            for s in rec["steps"] if not s["execution"]["passed"]]


def within_problem_agreement(recs: dict) -> dict:
    """Mean over problems (>=2 failing) of pairwise same-error-type rate."""
    per_problem = []
    for rec in recs.values():
        ft = fail_types(rec)
        if len(ft) < 2:
            continue
        types = [t for _, t in ft]
        pairs = list(combinations(types, 2))
        per_problem.append(sum(a == b for a, b in pairs) / len(pairs))
    return {"agreement": sum(per_problem) / len(per_problem) if per_problem else float("nan"),
            "n_problems_ge2_fail": len(per_problem)}


def b2_adjacent_vs_not(recs: dict) -> dict:
    adj_m = adj_n = non_m = non_n = 0
    for rec in recs.values():
        ft = {s: t for s, t in fail_types(rec)}
        steps = sorted(ft)
        for a, b in combinations(steps, 2):
            same = ft[a] == ft[b]
            if b - a == 1:
                adj_n += 1; adj_m += same
            else:
                non_n += 1; non_m += same
    return {"adjacent": adj_m / adj_n if adj_n else float("nan"), "n_adjacent": adj_n,
            "non_adjacent": non_m / non_n if non_n else float("nan"), "n_non_adjacent": non_n}


def no_code_by_step(recs: dict, n_steps: int) -> list:
    out = []
    for k in range(n_steps):
        c = sum(1 for r in recs.values() if r["steps"][k]["execution"]["error_type"] == "no_code")
        out.append(c / len(recs))
    return out


def main() -> None:
    rows = read_jsonl(FULL_B1)
    b1 = {r["problem_id"]: r for r in rows if r["condition"] == "b1"}
    full = {r["problem_id"]: r for r in rows if r["condition"] == "full"}
    b2 = {r["problem_id"]: r for r in read_jsonl(B2) if r["condition"] == "b2"}
    n_steps = len(next(iter(b1.values()))["steps"])

    agree = {name: within_problem_agreement(recs)
             for name, recs in {"B1": b1, "FULL": full, "B2": b2}.items()}
    b2_adj = b2_adjacent_vs_not(b2)
    b1_chance = agree["B1"]["agreement"]
    b2_within = agree["B2"]["agreement"]

    result = {
        "_label": "EXPLORATORY / POST-HOC — corrects DIAG-9 chance baseline; no H2 reopen",
        "within_problem_error_type_agreement": agree,
        "diag9_pooled_baseline_sum_pt2": 0.422,   # the WRONG baseline being replaced
        "diag9_observed_b2_adjacent": 0.851,
        "b2_adjacent_vs_nonadjacent": b2_adj,
        "correct_chance_baseline_B1_within_problem": b1_chance,
        "b2_excess_over_correct_baseline": b2_within - b1_chance,
        "no_code_rate_by_step": {name: no_code_by_step(recs, n_steps)
                                 for name, recs in {"B1": b1, "FULL": full, "B2": b2}.items()},
        "predicted": "B1 ~0.60-0.70, FULL ~= B1; B2 excess shrinks but stays positive",
    }
    OUT.write_text(json.dumps(result, indent=2))

    print("=== DIAG-9b — corrected persistence baseline ===")
    print(f"within-problem same-error agreement (the TRUE chance rate):")
    for name in ("B1", "FULL", "B2"):
        a = agree[name]
        print(f"  {name:<5} {a['agreement']:.3f}  (n={a['n_problems_ge2_fail']} problems >=2 fail)")
    print(f"\nDIAG-9 pooled baseline (WRONG): 0.422   observed B2 adjacent: 0.851")
    print(f"B2 adjacent {b2_adj['adjacent']:.3f} vs B2 non-adjacent {b2_adj['non_adjacent']:.3f} "
          f"(specific-anchor control)")
    print(f"corrected chance (B1 within-problem): {b1_chance:.3f}")
    print(f"B2 within-problem excess over corrected baseline: {b2_within - b1_chance:+.3f}")
    print(f"\nno_code rate by step (output-discipline check):")
    for name in ("B1", "B2"):
        print(f"  {name:<5} {[round(x, 3) for x in result['no_code_rate_by_step'][name]]}")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
