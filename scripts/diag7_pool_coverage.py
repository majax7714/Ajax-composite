#!/usr/bin/env python3
"""DIAG-7 — oracle pool coverage by cross-step channel.

Pre-registered in docs/DIAGNOSTICS.md (committed 2026-07-12, before this ran).
EXPLORATORY / POST-HOC re-analysis of committed artifacts only. Does NOT reopen
the H2 gate.

The sharp test: if every cross-step channel is net-harmful (each anchors the model
onto prior failed attempts), pool coverage should degrade monotonically in channel
bandwidth — B1 (i.i.d., no cross-step) > FULL (128-dim latent register) > B2 (full
previous-candidate text).

Pool coverage = fraction of problems with >=1 passing candidate among the 8.
Prediction: B1 > FULL > B2; B1 ~0.84, FULL ~0.82-0.84, B2 ~0.72-0.78.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).parents[1]
sys.path.insert(0, str(REPO / "src"))
from rgr.results import read_jsonl, selected_passed  # noqa: E402

FULL_B1 = REPO / "runs/phase2/full_b1.jsonl"
B2 = REPO / "runs/phase2/b2.jsonl"
OUT = REPO / "artifacts/diag7_oracle_coverage.json"


def pool_covered(rec: dict) -> bool:
    return any(s["execution"]["passed"] for s in rec["steps"])


def n_pass(rec: dict) -> int:
    return sum(1 for s in rec["steps"] if s["execution"]["passed"])


def summarize(records: dict[str, dict], n_problems: int) -> dict:
    covered = sum(pool_covered(r) for r in records.values())
    selected = sum(selected_passed(r) for r in records.values())
    total_pass = sum(n_pass(r) for r in records.values())
    return {
        "pool_coverage_pass_at_8": covered / n_problems,
        "pool_covered_count": covered,
        "selected_pass_at_1": selected / n_problems,
        "selected_pass_count": selected,
        "mean_passing_per_problem": total_pass / n_problems,  # pool richness
    }


def main() -> None:
    rows = read_jsonl(FULL_B1)
    full = {r["problem_id"]: r for r in rows if r["condition"] == "full"}
    b1 = {r["problem_id"]: r for r in rows if r["condition"] == "b1"}
    b2 = {r["problem_id"]: r for r in read_jsonl(B2) if r["condition"] == "b2"}
    pids = sorted(full)
    assert set(full) == set(b1) == set(b2), "condition problem sets differ"
    n = len(pids)

    conds = {"B1": b1, "FULL": full, "B2": b2}
    stats = {name: summarize(recs, n) for name, recs in conds.items()}

    cov = {name: s["pool_coverage_pass_at_8"] for name, s in stats.items()}
    ordering_holds = cov["B1"] >= cov["FULL"] >= cov["B2"]
    strict = cov["B1"] > cov["FULL"] > cov["B2"]

    result = {
        "_label": "EXPLORATORY / POST-HOC — does not reopen the H2 gate",
        "n_problems": n,
        "channel_bandwidth_order": ["B1 (none/i.i.d.)", "FULL (128-dim latent)",
                                    "B2 (prev-candidate text)"],
        "conditions": stats,
        "pool_coverage": cov,
        "predicted": {"B1": "~0.84", "FULL": "~0.82-0.84", "B2": "~0.72-0.78",
                      "ordering": "B1 > FULL > B2"},
        "ordering_B1_ge_FULL_ge_B2": ordering_holds,
        "ordering_strict_B1_gt_FULL_gt_B2": strict,
    }
    OUT.write_text(json.dumps(result, indent=2))

    print(f"=== DIAG-7 oracle pool coverage ({n} problems) ===")
    hdr = f"{'condition':<8}{'cross-step channel':<26}{'pass@8':>8}{'pass@1':>8}{'mean#pass':>11}"
    print(hdr); print("-" * len(hdr))
    labels = {"B1": "none (i.i.d.)", "FULL": "128-dim latent register",
              "B2": "prev-candidate text"}
    for name in ("B1", "FULL", "B2"):
        s = stats[name]
        print(f"{name:<8}{labels[name]:<26}"
              f"{s['pool_coverage_pass_at_8']:>8.4f}{s['selected_pass_at_1']:>8.4f}"
              f"{s['mean_passing_per_problem']:>11.3f}")
    print(f"\nordering B1 >= FULL >= B2: {ordering_holds}  (strict >: {strict})")
    print(f"predicted B1~0.84, FULL~0.82-0.84, B2~0.72-0.78")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
