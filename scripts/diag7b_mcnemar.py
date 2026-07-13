#!/usr/bin/env python3
"""DIAG-7 correction — McNemar significance on paired pool coverage.

Pre-registered in docs/DIAGNOSTICS.md (committed 2026-07-13, before this ran) after
external review flagged that DIAG-7's "the register updates cost 2.4 pts of pool
coverage / actively shrink the reachable pool" over-reads a 4-problem paired diff
(FULL 135/164 vs B1 139/164) — the same evidence DIAG-1 refused to call "harm".

EXPLORATORY / POST-HOC re-analysis of already-revealed DIAG-7 coverage. Does NOT
reopen the H2 gate and does NOT revise the held DIAG-7 ordering prediction; it puts
a significance test under the interpretive prose only.

McNemar with the exact two-sided binomial (small discordant counts): given a pair
of conditions, per problem classify (covered_by_X, covered_by_Y); the discordant
cells b = X-covered-not-Y and c = Y-covered-not-X carry all the information; under
H0 each discordant problem is a fair coin, so p = 2 * P(Bin(b+c, 0.5) <= min(b,c)).
"""
from __future__ import annotations

import json
import sys
from math import comb
from pathlib import Path

REPO = Path(__file__).parents[1]
sys.path.insert(0, str(REPO / "src"))
from rgr.results import read_jsonl  # noqa: E402

FULL_B1 = REPO / "runs/phase2/full_b1.jsonl"
B2 = REPO / "runs/phase2/b2.jsonl"
OUT = REPO / "artifacts/diag7b_mcnemar.json"


def pool_covered(rec: dict) -> bool:
    return any(s["execution"]["passed"] for s in rec["steps"])


def mcnemar_exact(covered_x: dict[str, bool], covered_y: dict[str, bool]) -> dict:
    pids = sorted(set(covered_x) & set(covered_y))
    b = sum(covered_x[p] and not covered_y[p] for p in pids)  # X yes, Y no
    c = sum(covered_y[p] and not covered_x[p] for p in pids)  # Y yes, X no
    both = sum(covered_x[p] and covered_y[p] for p in pids)
    neither = sum(not covered_x[p] and not covered_y[p] for p in pids)
    n = b + c
    k = min(b, c)
    # two-sided exact binomial on the discordant pairs
    tail = sum(comb(n, i) for i in range(k + 1)) * (0.5 ** n) if n else 1.0
    p = min(1.0, 2.0 * tail)
    return {
        "discordant_x_only": b, "discordant_y_only": c,
        "concordant_both": both, "concordant_neither": neither,
        "n_discordant": n, "p_exact_two_sided": p,
        "significant_at_0.05": p < 0.05,
    }


def main() -> None:
    rows = read_jsonl(FULL_B1)
    full = {r["problem_id"]: r for r in rows if r["condition"] == "full"}
    b1 = {r["problem_id"]: r for r in rows if r["condition"] == "b1"}
    b2 = {r["problem_id"]: r for r in read_jsonl(B2) if r["condition"] == "b2"}
    assert set(full) == set(b1) == set(b2), "condition problem sets differ"

    cov = {name: {p: pool_covered(r) for p, r in recs.items()}
           for name, recs in {"B1": b1, "FULL": full, "B2": b2}.items()}
    counts = {name: sum(v.values()) for name, v in cov.items()}

    pairs = {
        "FULL_vs_B1": mcnemar_exact(cov["FULL"], cov["B1"]),
        "B1_vs_B2": mcnemar_exact(cov["B1"], cov["B2"]),
        "FULL_vs_B2": mcnemar_exact(cov["FULL"], cov["B2"]),
    }
    result = {
        "_label": "EXPLORATORY / POST-HOC correction — does not reopen the H2 gate "
                  "or revise the held DIAG-7 ordering prediction",
        "n_problems": len(cov["B1"]),
        "pool_covered_counts": counts,
        "test": "McNemar exact two-sided binomial on discordant pairs",
        "predicted": "FULL_vs_B1 non-significant (p>=0.2); B2 pairs significant",
        "pairs": pairs,
    }
    OUT.write_text(json.dumps(result, indent=2))

    print("=== DIAG-7b — McNemar on paired pool coverage ===")
    print(f"covered: B1 {counts['B1']}  FULL {counts['FULL']}  B2 {counts['B2']}  (/{len(cov['B1'])})\n")
    for name, r in pairs.items():
        x, y = name.split("_vs_")
        print(f"{name:<12} discordant {x}-only={r['discordant_x_only']:>2} "
              f"{y}-only={r['discordant_y_only']:>2}  "
              f"p={r['p_exact_two_sided']:.4f}  "
              f"{'SIGNIFICANT' if r['significant_at_0.05'] else 'n.s.'}")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
