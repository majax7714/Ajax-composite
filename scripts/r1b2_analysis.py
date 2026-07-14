#!/usr/bin/env python3
"""R1b.2a/2b/2c — free CPU checks on the mechanism behind H1 ([PHASE_3R.md] R1b.2).

Selection Efficiency (SE) is the stack-invariant metric:
    SE = (selected_pass@1 − random_pass@1) / (oracle_pass@8 − random_pass@1)

R1b.2b (the smoking gun): did V learn *correctness*, or "does this code look broken"?
Stratify problems by failure type and compute V vs likelihood within-problem AUROC on
the SUBTLE stratum (failures are only wrong_answer) vs the OBVIOUS stratum (contains a
syntax/no_code/runtime failure). If V is near-chance on subtle, it learned brokenness.

4-bit pool = artifacts/lock_a.jsonl (error_type, mean_logprob, passed) merged with
artifacts/heldout_scores.json (v2b_score). This is the pool where V *had* its edge, so
the 4-bit stratification alone can settle the mechanism — free, committed data.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).parents[1]
sys.path.insert(0, str(REPO / "src"))
from rgr.evals.calibration import auroc  # noqa: E402

OBVIOUS = {"syntax", "no_code", "runtime", "timeout", "sandbox"}
OUT = REPO / "artifacts/r1b2b_stratified_auroc.json"


def load_4bit():
    """Per problem: list of candidates with {v, lik, passed, err}."""
    lock = [json.loads(l) for l in open(REPO / "artifacts/lock_a.jsonl")]
    hz = json.load(open(REPO / "artifacts/heldout_scores.json"))
    # group heldout_scores by problem_id, in order
    by_pid_scores: dict[str, list] = {}
    for r in hz:
        by_pid_scores.setdefault(r["problem_id"], []).append(r)
    problems = []
    misaligned = 0
    for rec in lock:
        pid = rec["problem_id"]
        steps = rec["steps"]
        scores = by_pid_scores.get(pid, [])
        cands = []
        for i, s in enumerate(steps):
            v = scores[i]["v2b_score"] if i < len(scores) else None
            # alignment sanity: mean_logprob should match
            if i < len(scores) and s["mean_logprob"] is not None:
                if abs((scores[i]["mean_logprob"] or -1e9) - s["mean_logprob"]) > 1e-6:
                    misaligned += 1
            cands.append({"v": v, "lik": s["mean_logprob"],
                          "passed": s["execution"]["passed"],
                          "err": s["execution"]["error_type"]})
        problems.append({"pid": pid, "cands": cands})
    return problems, misaligned


def within_auroc(problems, score_key):
    per = []
    for p in problems:
        s = [c[score_key] if c[score_key] is not None else -1e9 for c in p["cands"]]
        y = [bool(c["passed"]) for c in p["cands"]]
        if len(set(y)) == 2:
            per.append(auroc(s, y))
    return (sum(per) / len(per) if per else float("nan")), len(per)


def stratify(problems):
    """subtle = two-class problem whose failing candidates are ALL wrong_answer;
    obvious = two-class problem with any obvious-broken failure."""
    subtle, obvious = [], []
    for p in problems:
        ys = [bool(c["passed"]) for c in p["cands"]]
        if len(set(ys)) != 2:
            continue
        fails = [c["err"] for c in p["cands"] if not c["passed"]]
        if any(e in OBVIOUS for e in fails):
            obvious.append(p)
        elif all(e == "wrong_answer" for e in fails):
            subtle.append(p)
    return subtle, obvious


def r1b2c_length_bias():
    """R1b.2c — is bf16 likelihood's advantage a length artifact? On the bf16 M3 pool
    (m3_candidates mean_logprob + code + m3_labels passed): correlate length with
    mean_logprob and correctness; recompute likelihood selection under a
    length-controlled variant (sum-logprob proxy = mean_logprob × char-length) and vs
    length-stratified. Length is char-length of extracted code (token-count proxy)."""
    import statistics as st

    m3 = json.load(open(REPO / "runs/modal/m3_candidates.json"))
    lab = json.load(open(REPO / "runs/modal/m3_labels.json"))
    B0, ORACLE = 0.6479, 0.9024  # bf16 random pass@1, oracle pass@8 (M3)

    def se(sel):
        return (sel - B0) / (ORACLE - B0)

    rows = []  # per-problem list of (mean_logprob, length, passed)
    for cand_row, lab_row in zip(m3["candidates"], lab["labels"]):
        pr = []
        for c, p in zip(cand_row, lab_row):
            lp = c["mean_logprob"]
            ln = len(c["code"]) if c["code"] else 0
            pr.append((lp if lp is not None else -1e9, ln, bool(p)))
        rows.append(pr)

    flat = [(lp, ln, ps) for pr in rows for lp, ln, ps in pr if lp > -1e8 and ln > 0]
    lps, lens, ps = [x[0] for x in flat], [x[1] for x in flat], [1.0 if x[2] else 0.0 for x in flat]

    def corr(a, b):
        n = len(a)
        ma, mb = sum(a) / n, sum(b) / n
        cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
        da = (sum((x - ma) ** 2 for x in a)) ** 0.5
        db = (sum((y - mb) ** 2 for y in b)) ** 0.5
        return cov / (da * db) if da and db else 0.0

    def bestof(key, kk):
        hit = 0
        for pr in rows:
            sub = pr[:kk]
            idx = max(range(len(sub)), key=key(sub))
            hit += sub[idx][2]
        return hit / len(rows)

    res = {
        "pool": "bf16 M3", "length_proxy": "char length of extracted code",
        "corr_length_meanlogprob": corr(lens, lps),   # does likelihood favor short?
        "corr_length_correctness": corr(lens, ps),     # are short candidates correct?
        "likelihood_SE": se(bestof(lambda s: (lambda i: s[i][0]), 8)),
        "sumlogprob_SE": se(bestof(lambda s: (lambda i: s[i][0] * s[i][1]), 8)),
        "shortest_SE": se(bestof(lambda s: (lambda i: -s[i][1]), 8)),
        "stale_V_SE_ref": 0.067,
    }
    Path(REPO / "artifacts/r1b2c_length_bias.json").write_text(json.dumps(res, indent=2))
    print("\n=== R1b.2c — length-bias check on bf16 likelihood ===")
    print(f"corr(length, mean_logprob) = {res['corr_length_meanlogprob']:+.3f}  "
          f"(negative → likelihood favors short)")
    print(f"corr(length, correctness)  = {res['corr_length_correctness']:+.3f}")
    print(f"SE  best-of-8: likelihood(mean_lp) {res['likelihood_SE']:.3f}  "
          f"sum-logprob {res['sumlogprob_SE']:.3f}  shortest {res['shortest_SE']:.3f}  "
          f"(stale V {res['stale_V_SE_ref']:.3f})")
    print("wrote artifacts/r1b2c_length_bias.json")


def main():
    from collections import Counter
    problems, misaligned = load_4bit()
    print(f"4-bit pool: {len(problems)} problems; alignment mismatches: {misaligned}")

    # R1b.2a (4-bit side) — error_type distribution over failing candidates
    errs = Counter(c["err"] for p in problems for c in p["cands"] if not c["passed"])
    tot = sum(errs.values())
    print("\n=== R1b.2a — 4-bit failing-candidate error_type shares ===")
    for e, n in errs.most_common():
        print(f"  {e:<12} {n:>4}  ({n/tot:.3f})")

    # R1b.2b — stratified within-problem AUROC
    subtle, obvious = stratify(problems)
    res = {"pool": "4-bit (lock_a + heldout_scores)", "n_problems": len(problems),
           "alignment_mismatches": misaligned,
           "error_shares": {e: errs[e] / tot for e in errs},
           "strata": {}}
    print(f"\n=== R1b.2b — stratified within-problem AUROC (4-bit) ===")
    print(f"subtle (wrong_answer-only) problems: {len(subtle)} | "
          f"obvious (any broken) problems: {len(obvious)}")
    print(f"{'stratum':<10}{'V AUROC':>10}{'lik AUROC':>11}{'edge':>9}{'n':>5}")
    for name, strat in [("subtle", subtle), ("obvious", obvious), ("all", subtle + obvious)]:
        va, nv = within_auroc(strat, "v")
        la, _ = within_auroc(strat, "lik")
        res["strata"][name] = {"V_auroc": va, "lik_auroc": la, "edge": va - la, "n": nv}
        print(f"{name:<10}{va:>10.4f}{la:>11.4f}{va-la:>+9.4f}{nv:>5}")

    OUT.write_text(json.dumps(res, indent=2))
    print(f"\nwrote {OUT}")

    r1b2c_length_bias()


if __name__ == "__main__":
    main()
