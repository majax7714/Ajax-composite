#!/usr/bin/env python3
"""DIAG-9 — semantic anchoring & refinement trajectory in the B2 text channel.

Pre-registered in docs/DIAGNOSTICS.md (committed 2026-07-13, before this ran).
EXPLORATORY / POST-HOC re-analysis of committed artifacts only. Does NOT reopen the
H2 gate.

DIAG-8 tests anchoring at the surface (edit distance). DIAG-9 tests it semantically
and asks whether the text channel refines at all, from B2's per-step error_type and
frac_tests.

- error-type persistence: among ADJACENT step pairs where BOTH fail, the observed
  rate that error_type[i] == error_type[i-1], vs two baselines: the independence
  rate sum_t p_t^2 (correct chance that two independent failing steps share a type)
  and the modal-type share max_t p_t (loose reference). Excess over independence =>
  B2 stuck on the same failure mode.
- refinement trajectory: pass rate (frac_tests is binary here == passed) by step
  index 0..7. Rising => genuine refinement; flat/declining => net-harm.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).parents[1]
sys.path.insert(0, str(REPO / "src"))
from rgr.results import read_jsonl  # noqa: E402

B2 = REPO / "runs/phase2/b2.jsonl"
OUT = REPO / "artifacts/diag9_error_persistence.json"


def main() -> None:
    recs = [r for r in read_jsonl(B2) if r["condition"] == "b2"]
    n_steps = len(recs[0]["steps"])

    # marginal error-type distribution among failing steps
    et = Counter()
    for r in recs:
        for s in r["steps"]:
            if not s["execution"]["passed"]:
                et[s["execution"]["error_type"]] += 1
    total_fail = sum(et.values())
    p = {k: v / total_fail for k, v in et.items()}
    indep_match = sum(v * v for v in p.values())  # sum p_t^2
    modal_share = max(p.values())

    # observed adjacent-failing-pair error-type match
    match, adj_fail_pairs = 0, 0
    for r in recs:
        st = r["steps"]
        for i in range(1, len(st)):
            a, b = st[i - 1]["execution"], st[i]["execution"]
            if (not a["passed"]) and (not b["passed"]):
                adj_fail_pairs += 1
                if a["error_type"] == b["error_type"]:
                    match += 1
    obs_match = match / adj_fail_pairs if adj_fail_pairs else float("nan")

    # pass rate by step index (frac_tests binary == passed here)
    pass_by_step = []
    for k in range(n_steps):
        pr = sum(r["steps"][k]["execution"]["passed"] for r in recs) / len(recs)
        pass_by_step.append(pr)
    step0 = pass_by_step[0]
    rest = sum(pass_by_step[1:]) / (n_steps - 1)
    slope_0_to_last = pass_by_step[-1] - pass_by_step[0]

    persistence_above_chance = obs_match > indep_match
    refines = rest > step0 + 0.02  # >2 pts lift after the un-anchored step 0

    result = {
        "_label": "EXPLORATORY / POST-HOC — does not reopen the H2 gate",
        "n_problems": len(recs), "n_steps": n_steps,
        "error_type_marginals_failing": dict(et),
        "total_failing_steps": total_fail,
        "obs_adjacent_failing_match_rate": obs_match,
        "chance_independence_sum_pt2": indep_match,
        "modal_type_share": modal_share,
        "excess_over_independence": obs_match - indep_match,
        "n_adjacent_failing_pairs": adj_fail_pairs,
        "pass_rate_by_step": pass_by_step,
        "pass_step0_unanchored": step0,
        "pass_mean_steps_1_to_last": rest,
        "pass_slope_step0_to_last": slope_0_to_last,
        "predicted": "persistence modestly above independence; pass rate flat across steps",
        "verdict_semantic_anchoring": persistence_above_chance,
        "verdict_refines": refines,
    }
    OUT.write_text(json.dumps(result, indent=2))

    print(f"=== DIAG-9 semantic anchoring & refinement ({len(recs)} problems) ===")
    print(f"error types (failing): {dict(et)}")
    print(f"adjacent-failing-pair error-type match:  {obs_match:.3f}")
    print(f"  vs independence sum(p^2): {indep_match:.3f}   vs modal share: {modal_share:.3f}")
    print(f"  excess over independence: {obs_match - indep_match:+.3f}  "
          f"({'ABOVE chance' if persistence_above_chance else 'at/below chance'})")
    print(f"pass rate by step: {[round(x, 3) for x in pass_by_step]}")
    print(f"  step0 (un-anchored) {step0:.3f}  vs mean(steps 1..{n_steps-1}) {rest:.3f}  "
          f"slope 0->last {slope_0_to_last:+.3f}")
    print(f"  refines across steps? {refines}")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
