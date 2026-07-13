#!/usr/bin/env python3
"""DIAG-11 — conditional recovery on step-0 failures.

Pre-registered in docs/PHASE_3.md §1 + docs/DIAGNOSTICS.md (committed 2026-07-13,
before this ran). Pure re-analysis of the committed DIAG-10 rollouts — the only
benefit signal extractable from data already on disk. EXPLORATORY; does NOT reopen
the H2 gate. Sets the H1 prior; cannot change Phase-3's design.

Step 0 is shared across conditions (same candidates), so the "step-0 failed" subset
is identical for B1 / ABSTRACT / B2+fb — a clean paired comparison. On that subset,
recovery = fraction of problems where ANY of steps 1..7 passes.

Question: given you failed and were told why, do you recover more often than by
simply drawing again (B1)?
Prediction: ABSTRACT > B1 by a few points, not significant at n~24. ABSTRACT < B1 =
red flag.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).parents[1]
RAW = REPO / "runs/modal/diag10_feedback_2x2.json"
OUT = REPO / "artifacts/diag11_conditional_recovery.json"


def main() -> None:
    if not RAW.exists():
        sys.exit(f"missing {RAW} (DIAG-10 raw per-problem rollouts)")
    d = json.loads(RAW.read_text())
    conds = d["conditions"]
    N = d["n_problems"]

    # shared step-0 outcome (identical across conditions) -> the failed subset
    ref = conds["b1"]
    step0_failed = [j for j in range(N) if not ref[j][0]["passed"]]
    n_fail = len(step0_failed)

    def recovered_any(traj_j) -> bool:
        return any(traj_j[s]["passed"] for s in range(1, len(traj_j)))

    def recovered_last(traj_j) -> bool:
        return traj_j[-1]["passed"]

    results = {}
    for c, traj in conds.items():
        any_rec = sum(recovered_any(traj[j]) for j in step0_failed)
        last_rec = sum(recovered_last(traj[j]) for j in step0_failed)
        results[c] = {
            "recovered_any_step_1_7": any_rec,
            "recovery_rate_any": any_rec / n_fail if n_fail else float("nan"),
            "recovered_at_step7": last_rec,
            "recovery_rate_at_step7": last_rec / n_fail if n_fail else float("nan"),
        }

    b1_any = results["b1"]["recovery_rate_any"]
    result = {
        "_label": "EXPLORATORY / POST-HOC (re-analysis of DIAG-10). Sets H1 prior; "
                  "does not reopen H2 or change Phase-3 design.",
        "n_step0_failures": n_fail,
        "n_problems_total": N,
        "recovery": results,
        "abstract_minus_b1_recovery_any": results["abstract"]["recovery_rate_any"] - b1_any,
        "b2fb_minus_b1_recovery_any": results["b2_fb"]["recovery_rate_any"] - b1_any,
        "predicted": "ABSTRACT > B1 by a few pts, n.s. at n~24; ABSTRACT < B1 = red flag",
    }
    OUT.write_text(json.dumps(result, indent=2))

    print(f"=== DIAG-11 — conditional recovery ({n_fail} step-0 failures of {N}) ===")
    print(f"{'condition':<10}{'recover(any 1-7)':>18}{'recover(@step7)':>18}")
    for c in ("b1", "abstract", "b2_fb"):
        r = results[c]
        print(f"{c:<10}{r['recovery_rate_any']:>10.3f} ({r['recovered_any_step_1_7']:>2}/{n_fail}) "
              f"{r['recovery_rate_at_step7']:>10.3f} ({r['recovered_at_step7']:>2}/{n_fail})")
    print(f"\nABSTRACT − B1 (recover any): {result['abstract_minus_b1_recovery_any']:+.3f}")
    print(f"B2+fb    − B1 (recover any): {result['b2fb_minus_b1_recovery_any']:+.3f}")
    print(f"(prediction: ABSTRACT > B1 by a few pts, n.s. at n~{n_fail}; ABSTRACT < B1 = red flag)")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
