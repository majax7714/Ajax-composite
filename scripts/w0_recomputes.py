#!/usr/bin/env python3
"""W0 — free CPU recomputes from committed pools ([PHASE_3B.md] W0a/W0b/W0c).

W0a: the honest E0 anchor — PULL of committed E0 generations against the same failed
     artifact E1/E2 conditioned on (pre-reg: within ±0.05 of 0.396, 70/30).
W0b: the D2c copy-expectation null — per-artifact copy-null (f_a) and i.i.d.-null
     (problem pool mean frac) from the enriched base T=0.8 LCB-easy pool.
W0c: stratum false-zero rate — two-component prior (point mass at p=0 + Beta) fit by
     ML to per-problem solve counts; expected fresh-B1-50 recovery count per stratum.

Pure CPU over committed artifacts. No generation, no re-execution.
Outputs: artifacts/w0a_e0_anchor.json, w0b_copy_null.json, w0c_stratum_falsezero.json
"""
from __future__ import annotations

import difflib
import json
import math
import statistics as st
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).parents[1]


# ---------------------------------------------------------------- W0a
def w0a():
    m3 = json.loads((REPO / "runs/modal/m3_candidates.json").read_text())
    labels = json.loads((REPO / "runs/modal/m3_labels.json").read_text())["labels"]
    fail_art = {}
    for pid, row, lab in zip(m3["problem_ids"], m3["candidates"], labels):
        fail = next((c["code"] for c, p in zip(row, lab) if not p and c["code"]), None)
        good = next((c["code"] for c, p in zip(row, lab) if p and c["code"]), None)
        if fail and good:
            fail_art[pid] = fail

    gen = json.loads((REPO / "runs/modal/dmeasure_gen.json").read_text())["results"]
    per_t = defaultdict(list)          # temp -> per-problem mean E0-PULL
    cond_pull = defaultdict(list)      # (cond,temp) -> per-record mean pull (recompute)
    for r in gen:
        art = fail_art.get(r["pid"])
        if r["cond"] == "E0" and art:
            pulls = [1.0 - difflib.SequenceMatcher(None, cd, art).ratio()
                     for cd in r["codes"] if cd]
            if pulls:
                per_t[r["temp"]].append(sum(pulls) / len(pulls))
        if r["cond"] in ("E1", "E2") and r["pull"] is not None:
            cond_pull[(r["cond"], r["temp"])].append(r["pull"])

    rows = {f"E0_PULL@{t}": {"n": len(v), "mean": st.mean(v), "sd": st.stdev(v)}
            for t, v in sorted(per_t.items())}
    cond = {f"{c}@{t}": st.mean(v) for (c, t), v in sorted(cond_pull.items())}
    anchor = rows["E0_PULL@1.2"]["mean"]
    out = {
        "_label": "W0a — E0 anchor measured on the conditioned-cell PULL metric",
        "prereg_prediction": "E0-PULL within ±0.05 of 0.396 (odds 70/30); "
                             "secondary: E0-PULL ≥ every conditioned PULL at matched T",
        "diag8_pairwise_anchor_assumed": 0.396,
        "E0_PULL_vs_E1_artifact": rows,
        "conditioned_PULL_recomputed": cond,
        "anchor_row_T1.2": anchor,
        "delta_vs_assumed": anchor - 0.396,
        "within_prereg_band": abs(anchor - 0.396) <= 0.05,
        "secondary_holds_T0.8": rows["E0_PULL@0.8"]["mean"] >= max(
            cond["E1@0.8"], cond["E2@0.8"]),
        "secondary_holds_T1.2": rows["E0_PULL@1.2"]["mean"] >= max(
            cond["E1@1.2"], cond["E2@1.2"]),
    }
    (REPO / "artifacts/w0a_e0_anchor.json").write_text(json.dumps(out, indent=2))
    print("=== W0a — E0 anchor, measured ===")
    for k, v in rows.items():
        print(f"  {k}: {v['mean']:.4f} ± {v['sd']:.4f} (n={v['n']})")
    print(f"  conditioned (recomputed): " +
          ", ".join(f"{k} {v:.3f}" for k, v in cond.items()))
    print(f"  anchor row (T=1.2): {anchor:.4f}  vs assumed 0.396  "
          f"(delta {anchor-0.396:+.4f})  within ±0.05: {out['within_prereg_band']}")
    print(f"  secondary (E0 ≥ all conditioned): T0.8 {out['secondary_holds_T0.8']}, "
          f"T1.2 {out['secondary_holds_T1.2']}")


# ---------------------------------------------------------------- W0b
def w0b():
    res = json.loads((REPO / "runs/modal/lcb_res_lcb_r2_base_T08.json").read_text())
    qids, results = res["question_ids"], res["results"]
    per_problem, n_partial, n_band = {}, 0, 0
    for qid, row in zip(qids, results):
        fracs = [c["frac"] for c in row]
        partial = [(i, c["frac"], c["n_tests"]) for i, c in enumerate(row)
                   if 0.0 < c["frac"] < 1.0]
        band = [(i, f, nt) for i, f, nt in partial if 0.4 <= f <= 0.6]
        n_partial += len(partial)
        n_band += len(band)
        if partial:
            per_problem[qid] = {
                "iid_null_pool_mean_frac": sum(fracs) / len(fracs),
                "n_partial": len(partial),
                "partial_artifacts": [
                    {"cand_idx": i, "copy_null_frac": f, "n_tests": nt}
                    for i, f, nt in partial],
                "band_40_60_idx": [i for i, _, _ in band],
            }
    all_partial_fracs = [a["copy_null_frac"] for v in per_problem.values()
                         for a in v["partial_artifacts"]]
    all_tests = [a["n_tests"] for v in per_problem.values()
                 for a in v["partial_artifacts"]]
    out = {
        "_label": "W0b — D2c/E6 copy-expectation null (base T=0.8 LCB-easy enriched pool)",
        "null_definition": "climbing = paired mean(frac(gen) − copy_null f_a) > 0 AND "
                           "frac(gen) > iid_null (beats copying AND resampling); "
                           "formal test frozen at W3",
        "n_problems_with_partial": len(per_problem),
        "n_partial_candidates": n_partial,
        "n_in_40_60_band": n_band,
        "partial_frac_mean": st.mean(all_partial_fracs),
        "partial_frac_median": st.median(all_partial_fracs),
        "median_n_tests": st.median(all_tests),
        "per_problem": per_problem,
    }
    (REPO / "artifacts/w0b_copy_null.json").write_text(json.dumps(out, indent=2))
    print("\n=== W0b — D2c copy-expectation null ===")
    print(f"  problems with partial credit: {len(per_problem)}/80; "
          f"partial candidates {n_partial} (40–60% band: {n_band})")
    print(f"  partial frac mean/median: {out['partial_frac_mean']:.3f}/"
          f"{out['partial_frac_median']:.3f}; median tests {out['median_n_tests']}")


# ---------------------------------------------------------------- W0c
def _log_beta(a, b):
    return math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)


def _bb_logpmf_table(n, a, b):
    """log BetaBinomial(x; n, a, b) for x = 0..n."""
    lb = _log_beta(a, b)
    return [math.lgamma(n + 1) - math.lgamma(x + 1) - math.lgamma(n - x + 1)
            + _log_beta(x + a, n - x + b) - lb for x in range(n + 1)]


def _fit_mixture(counts, n, with_point_mass=True):
    """ML fit of pi0*delta(p=0) + (1-pi0)*BetaBinomial over a coarse-to-fine grid."""
    hist = defaultdict(int)
    for x in counts:
        hist[x] += 1

    def profile_ll(a, b):
        tab = _bb_logpmf_table(n, a, b)
        best = (-1e18, 0.0)
        pis = [i / 200 for i in range(199)] if with_point_mass else [0.0]
        for pi0 in pis:
            ll = 0.0
            for x, c in hist.items():
                if x == 0:
                    ll += c * math.log(pi0 + (1 - pi0) * math.exp(tab[0]))
                else:
                    ll += c * (math.log(1 - pi0) + tab[x])
            if ll > best[0]:
                best = (ll, pi0)
        return best

    grid = [math.exp(math.log(0.01) + i * (math.log(200) - math.log(0.01)) / 29)
            for i in range(30)]
    best = (-1e18, None)
    for a in grid:
        for b in grid:
            ll, pi0 = profile_ll(a, b)
            if ll > best[0]:
                best = (ll, (a, b, pi0))
    a0, b0, _ = best[1]
    fine_a = [a0 * math.exp(d / 10) for d in range(-10, 11)]
    fine_b = [b0 * math.exp(d / 10) for d in range(-10, 11)]
    for a in fine_a:
        for b in fine_b:
            ll, pi0 = profile_ll(a, b)
            if ll > best[0]:
                best = (ll, (a, b, pi0))
    ll, (a, b, pi0) = best
    return {"loglik": ll, "alpha": a, "beta": b, "pi0": pi0}


def w0c():
    cells = {"base_T0.8": "lcb_res_lcb_r2_base_T08.json",
             "base_T1.0": "lcb_res_lcb_r2_base_T10.json",
             "base_T1.2": "lcb_res_lcb_r2_base_T12.json",
             "instruct_T1.2": "lcb_res_lcb_r2_instruct_T12.json"}
    out = {"_label": "W0c — per-problem p̂ + false-zero rate of the pass@50=0 stratum",
           "model": "ML fit of pi0*delta(p=0) + (1-pi0)*Beta(a,b); posterior for an "
                    "observed-zero problem: P(reachable|0/50) and fresh-50 recovery "
                    "prob 1 − B(a,b+100)/B(a,b+50); pure-Beta fit (pi0=0) reported as "
                    "the upper bound on the false-zero rate",
           "cells": {}}
    print("\n=== W0c — stratum false-zero characterization ===")
    for cell, fname in cells.items():
        res = json.loads((REPO / "runs/modal" / fname).read_text())
        counts = [sum(1 for c in row if c["passed"]) for row in res["results"]]
        n_zero = sum(1 for x in counts if x == 0)
        near = {1: sum(1 for x in counts if x == 1), 2: sum(1 for x in counts if x == 2)}
        fits = {}
        for tag, wpm in (("mixture", True), ("pure_beta_upper_bound", False)):
            f = _fit_mixture(counts, 50, with_point_mass=wpm)
            a, b, pi0 = f["alpha"], f["beta"], f["pi0"]
            bb0 = math.exp(_log_beta(a, b + 50) - _log_beta(a, b))  # P(x=0 | reachable)
            p_reach = (1 - pi0) * bb0 / (pi0 + (1 - pi0) * bb0)
            rec_if_reach = 1.0 - math.exp(_log_beta(a, b + 100) - _log_beta(a, b + 50))
            per_prob = p_reach * rec_if_reach
            fits[tag] = {**f, "P_reachable_given_zero": p_reach,
                         "fresh50_recovery_prob_per_zero_problem": per_prob,
                         "expected_B1_50_recoveries_in_stratum": per_prob * n_zero}
        out["cells"][cell] = {"n_problems": len(counts), "stratum_size_pass50_eq_0": n_zero,
                              "n_at_1_of_50": near[1], "n_at_2_of_50": near[2],
                              "fits": fits}
        m, u = fits["mixture"], fits["pure_beta_upper_bound"]
        print(f"  {cell:<14} stratum {n_zero:>2}/{len(counts)}  near-zero x=1:{near[1]} "
              f"x=2:{near[2]}  P(reach|0) {m['P_reachable_given_zero']:.2f}  "
              f"E[B1-50 recoveries] {m['expected_B1_50_recoveries_in_stratum']:.2f} "
              f"(upper {u['expected_B1_50_recoveries_in_stratum']:.2f})")
    (REPO / "artifacts/w0c_stratum_falsezero.json").write_text(json.dumps(out, indent=2))
    print("wrote artifacts/w0a_e0_anchor.json, w0b_copy_null.json, w0c_stratum_falsezero.json")


if __name__ == "__main__":
    w0a()
    w0b()
    w0c()
