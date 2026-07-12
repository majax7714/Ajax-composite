#!/usr/bin/env python3
"""DIAG-1 — oracle stratification of the H2 FULL/B1 disagreements.

Pre-registered in docs/PRE-B2-HANDOFF.md §4. EXPLORATORY / POST-HOC re-analysis
of committed artifacts only (runs/phase2/full_b1.jsonl, artifacts/lock_a.jsonl).
Does NOT reopen the H2 gate (PHASES.md Phase-2: FAIL, register dead).

Question: are FULL's 9 wins real generative steering, or reselection among
candidates B1 also sampled? "Win" is defined identically to the H2 gate —
verifier-selected (best_index) candidate passes.

Committed prediction: FULL-only wins with B1's pool empty = 0 or 1; FULL solves
0 of the ~26 Phase-0-oracle-empty (pass@8=0) problems -> generative effect zero.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).parents[1]
sys.path.insert(0, str(REPO / "src"))
from rgr.results import read_jsonl, selected_passed  # noqa: E402

FULL_B1 = REPO / "runs/phase2/full_b1.jsonl"
LOCK_A = REPO / "artifacts/lock_a.jsonl"
OUT = REPO / "artifacts/diag1_oracle_stratification.json"


def pool_covered(rec: dict) -> bool:
    """Did ANY of the record's candidates pass? (Oracle pool coverage.)"""
    return any(s["execution"]["passed"] for s in rec["steps"])


def main() -> None:
    rows = read_jsonl(FULL_B1)
    full = {r["problem_id"]: r for r in rows if r["condition"] == "full"}
    b1 = {r["problem_id"]: r for r in rows if r["condition"] == "b1"}
    pids = sorted(full)
    assert set(full) == set(b1), "FULL/B1 problem sets differ"

    # Phase-0 oracle pool from lock_a (8 i.i.d. samples, no register).
    lock = {r["problem_id"]: r for r in read_jsonl(LOCK_A)}
    p0_covered = {pid: pool_covered(lock[pid]) for pid in pids}

    full_only = [p for p in pids if selected_passed(full[p]) and not selected_passed(b1[p])]
    b1_only = [p for p in pids if selected_passed(b1[p]) and not selected_passed(full[p])]

    def strat(wins: list[str], loser: dict) -> tuple[int, int]:
        """Of these wins, (loser-pool-covered, loser-pool-empty)."""
        empty = [p for p in wins if not pool_covered(loser[p])]
        return len(wins) - len(empty), len(empty)

    fo_cov, fo_empty = strat(full_only, b1)  # FULL-only: did B1's own pool contain a pass?
    bo_cov, bo_empty = strat(b1_only, full)  # B1-only (symmetry control)

    oracle_empty = [p for p in pids if not p0_covered[p]]
    full_solved_empty = [p for p in oracle_empty if selected_passed(full[p])]
    b1_solved_empty = [p for p in oracle_empty if selected_passed(b1[p])]
    full_pool_into_empty = [p for p in oracle_empty if pool_covered(full[p])]
    b1_pool_into_empty = [p for p in oracle_empty if pool_covered(b1[p])]

    result = {
        "_label": "EXPLORATORY / POST-HOC — does not reopen the H2 gate",
        "n_problems": len(pids),
        "phase0_oracle_covered": sum(p0_covered.values()),
        "phase0_oracle_empty": len(oracle_empty),
        "full_only_wins": len(full_only),
        "b1_only_wins": len(b1_only),
        # The decisive stratification:
        "full_only_where_b1_pool_covered": fo_cov,
        "full_only_where_b1_pool_empty": fo_empty,  # FULL reached what B1's pool could not
        "b1_only_where_full_pool_covered": bo_cov,
        "b1_only_where_full_pool_empty": bo_empty,  # symmetry / noise floor
        "full_selected_solved_of_oracle_empty": len(full_solved_empty),
        "b1_selected_solved_of_oracle_empty": len(b1_solved_empty),
        "full_pool_reached_oracle_empty": len(full_pool_into_empty),
        "b1_pool_reached_oracle_empty": len(b1_pool_into_empty),
        "detail": {
            "full_only_b1_pool_empty_pids": [p for p in full_only if not pool_covered(b1[p])],
            "b1_only_full_pool_empty_pids": [p for p in b1_only if not pool_covered(full[p])],
            "full_solved_oracle_empty_pids": full_solved_empty,
            "b1_solved_oracle_empty_pids": b1_solved_empty,
        },
    }
    OUT.write_text(json.dumps(result, indent=2))

    print(f"=== DIAG-1 oracle stratification ({len(pids)} problems) ===")
    print(f"Phase-0 oracle: {result['phase0_oracle_covered']} covered / "
          f"{result['phase0_oracle_empty']} empty  (pass@8 sanity: "
          f"{result['phase0_oracle_covered'] / len(pids):.4f})")
    print(f"disagreements: {len(full_only)} FULL-only, {len(b1_only)} B1-only\n")
    hdr = f"{'stratum':<48}{'count':>6}"
    print(hdr); print("-" * len(hdr))
    print(f"{'FULL-only wins, B1 pool HAD a pass (reselect)':<48}{fo_cov:>6}")
    print(f"{'FULL-only wins, B1 pool EMPTY (FULL generated)':<48}{fo_empty:>6}")
    print(f"{'B1-only wins, FULL pool EMPTY (symmetry ctrl)':<48}{bo_empty:>6}")
    print(f"{'FULL solved / oracle-empty problems':<48}"
          f"{len(full_solved_empty):>6}")
    print(f"{'B1 solved / oracle-empty problems':<48}{len(b1_solved_empty):>6}")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
