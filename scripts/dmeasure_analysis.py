#!/usr/bin/env python3
"""D2b — fix the D-measure metric confound ([PHASE_3R.md] Addendum III §3, §6-D2b).

The published D-measure coverage mixes two quantities: greedy (T=0) used ns=1, so its
"coverage" is pass@1, while T>0 used ns=8, so its "coverage" is pass@8. They are not
comparable, which is what corrupted the TAX-vs-temperature reading (§4).

Free fix (committed data, CPU/Daytona only — no regeneration): re-execute the persisted
generations in runs/modal/dmeasure_gen.json and report **mean per-sample pass rate** at
every T, alongside pass@ns. mean-pass is one consistent metric across all temperatures
and is the precondition for the §3 temperature dose-response claim.

Also emits, from the fixed metric:
  * the escape-distance table (§2): failure-conditioned cells sorted by PULL vs coverage;
  * the temperature dose-response (§3): T=0.8 → T=1.2 change, per condition, ns=8 only.
Appends a "per_sample" block to artifacts/dmeasure_conditioning.json.
"""
from __future__ import annotations

import json
import os
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).parents[1]
os.chdir(str(REPO))

GEN = REPO / "runs/modal/dmeasure_gen.json"
COND_JSON = REPO / "artifacts/dmeasure_conditioning.json"
EXEC_OUT = REPO / "runs/modal/dmeasure_exec.json"
CONDS = ["E0", "E1", "E2", "E5"]
TEMPS = [0.0, 0.8, 1.2]


def execute_all():
    """Re-execute every persisted generation via the same backend the original run used
    (Daytona), returning passed-bool per (pid,cond,temp) sample."""
    import sys
    sys.path.insert(0, str(REPO / "src"))
    from rgr.config import load_config
    from rgr.data.humaneval import load_humaneval
    from rgr.execution.sandbox import DaytonaBackend
    from rgr.training.labels import ExecutionPool
    from rgr.types import Candidate, SplitRole

    cfg = load_config("configs/phase0_harness.toml")
    he = {p.problem_id: p for p in load_humaneval().checkout(SplitRole.HELDOUT_EVAL)}
    gen = json.loads(GEN.read_text())["results"]

    passed = {}
    pool = ExecutionPool(lambda: DaytonaBackend(cfg.execution.timeout_seconds), size=8)
    try:
        for r in gen:
            prob = he[r["pid"]]
            cands = [Candidate(text="", code=cd) for cd in r["codes"]]
            ex = pool.execute_all(prob, cands)
            passed[(r["pid"], r["cond"], r["temp"])] = [bool(e.passed) for e in ex]
    finally:
        pool.close()
    # persist per-sample (json keys must be strings)
    EXEC_OUT.write_text(json.dumps(
        {f"{p}|{c}|{t}": v for (p, c, t), v in passed.items()}))
    return passed


def main():
    passed = execute_all()

    # aggregate per (cond,temp): mean per-sample pass, pass@ns (any), n_samples
    meanpass = defaultdict(list)   # per-problem mean-pass -> averaged
    cover = defaultdict(list)      # per-problem any-pass (the published coverage)
    nsamp = defaultdict(int)
    for (pid, c, t), ps in passed.items():
        if not ps:
            continue
        meanpass[(c, t)].append(sum(ps) / len(ps))
        cover[(c, t)].append(1.0 if any(ps) else 0.0)
        nsamp[(c, t)] = len(ps)

    def avg(d, k):
        return (sum(d[k]) / len(d[k])) if d[k] else None

    summary = json.loads(COND_JSON.read_text())
    pull = {k: v["pull"] for k, v in summary["summary"].items()}  # published PULL

    per_sample = {}
    for c in CONDS:
        for t in TEMPS:
            k = (c, t)
            per_sample[f"{c}@{t}"] = {
                "ns": nsamp[k],
                "mean_per_sample_pass": avg(meanpass, k),
                "coverage_any_pass": avg(cover, k),
                "pull": pull.get(f"{c}@{t}"),
            }
    summary["per_sample_D2b"] = {
        "_note": "D2b (Add.III §6): mean per-sample pass = one consistent metric across T "
                 "(greedy ns=1, T>0 ns=8; coverage_any_pass is the confounded published number). "
                 "Re-executed committed runs/modal/dmeasure_gen.json via Daytona.",
        "cells": per_sample,
    }
    COND_JSON.write_text(json.dumps(summary, indent=2))

    # ---- reports ----
    print("\n=== D2b — confound-free metric (mean per-sample pass) ===")
    print(f"{'cell':<9}{'ns':>4}{'PULL':>8}{'mean_pass':>11}{'cov(any)':>10}")
    for c in CONDS:
        for t in TEMPS:
            s = per_sample[f"{c}@{t}"]
            pl = f"{s['pull']:.3f}" if s['pull'] is not None else "  -  "
            mp = f"{s['mean_per_sample_pass']:.3f}" if s['mean_per_sample_pass'] is not None else "  -  "
            print(f"{c+'@'+str(t):<9}{s['ns']:>4}{pl:>8}{mp:>11}{s['coverage_any_pass']:>10.3f}")

    # §2 escape-distance law: failure-conditioned cells sorted by PULL
    print("\n=== §2 escape-distance law (failure-conditioned, sorted by PULL) ===")
    print(f"{'cell':<9}{'PULL':>8}{'mean_pass':>11}{'cov(any)':>10}")
    fails = [(f"{c}@{t}", per_sample[f"{c}@{t}"]) for c in ("E1", "E2") for t in TEMPS]
    for name, s in sorted(fails, key=lambda kv: kv[1]["pull"]):
        print(f"{name:<9}{s['pull']:>8.3f}{s['mean_per_sample_pass']:>11.3f}{s['coverage_any_pass']:>10.3f}")

    # §3 temperature dose-response: ns=8 only, T=0.8 -> T=1.2
    print("\n=== §3 temperature dose-response (ns=8 clean: T=0.8 -> 1.2) ===")
    print(f"{'cond':<6}{'mean_pass Δ':>14}{'cov(any) Δ':>13}")
    for c in CONDS:
        a, b = per_sample[f"{c}@0.8"], per_sample[f"{c}@1.2"]
        if a["mean_per_sample_pass"] is None or b["mean_per_sample_pass"] is None:
            continue
        dmp = b["mean_per_sample_pass"] - a["mean_per_sample_pass"]
        dcov = b["coverage_any_pass"] - a["coverage_any_pass"]
        print(f"{c:<6}{dmp:>+14.3f}{dcov:>+13.3f}")
    print(f"\nwrote per-sample -> {EXEC_OUT}")
    print(f"appended per_sample_D2b -> {COND_JSON}")


if __name__ == "__main__":
    main()
