"""Phase 8 D1 — inherited-error analysis ([PHASE_8.md] D1).

Discriminates M-RECLASS (the model inherits the conditioning artifact's SPECIFIC
bugs) from M-OOD (degradation uncorrelated with the artifact's particular errors).

Metric (committed before computing, [PHASE_8.md] D1): for each problem with n tests,
artifact failing-set A, and a generation's failing-set G,
    excess = |G ∩ A| - |G|*|A|/n          (observed minus chance-expected overlap)
Per problem: mean excess over the 8 conditioned (E1) gens vs over the unconditioned
(E0) gens. Paired one-sided test across problems (E1 > E0). RECLASS => E1 excess
significantly above E0; OOD => E1 ~ E0. Clean control (M1) ~ null under either.

Validity: artifact-source and gen pools must report the same n_tests for a problem
(same suite / indexing — the two judges are verbatim copies, modal_h1.py header), else
the problem is dropped and counted.

Pure CPU; reads committed pools. Emits artifacts/h8_d1_inherited_error.json.
"""
import difflib
import json
import random
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RNG = random.Random(17)


def _j(p):
    return json.loads((REPO / p).read_text())


def _d2c44():
    """Replicate modal_h1._d2c_artifacts (the frozen 44 set) without importing modal."""
    w0b = _j("artifacts/w0b_copy_null.json")
    cand = _j("runs/modal/lcb_cand_lcb_r2_base_T08.json")
    res = _j("runs/modal/lcb_res_lcb_r2_base_T08.json")
    codes_by_qid = dict(zip(res["question_ids"], cand["codes"]))
    rows_by_qid = dict(zip(res["question_ids"], res["results"]))
    arts = []
    for qid, v in w0b["per_problem"].items():
        band = v["band_40_60_idx"]
        if not band:
            continue
        fr = {a["cand_idx"]: a["copy_null_frac"] for a in v["partial_artifacts"]}
        for bi in sorted(band, key=lambda i: (abs(fr[i] - 0.5), i)):
            if codes_by_qid[qid][bi]:
                row = rows_by_qid[qid][bi]
                arts.append({"qid": qid, "cand_idx": bi, "code": codes_by_qid[qid][bi],
                             "n_tests": row["n_tests"]})
                break
    assert len(arts) == 44, len(arts)
    return arts


def _donor_by_qid():
    res = _j("runs/modal/lcb_res_lcb_r2_base_T08.json")
    cand = _j("runs/modal/lcb_cand_lcb_r2_base_T08.json")
    rb = dict(zip(res["question_ids"], res["results"]))
    cb = dict(zip(res["question_ids"], cand["codes"]))
    return rb, cb


def _excess(G, A, n):
    G, A = set(G), set(A)
    return len(G & A) - len(G) * len(A) / n if n else 0.0


def _jacc(G, A):
    G, A = set(G), set(A)
    u = len(G | A)
    return len(G & A) / u if u else 0.0


def _perm_p_one_sided(diffs, iters=20000):
    """P(mean of sign-flipped diffs >= observed mean) — paired sign-flip permutation."""
    diffs = [d for d in diffs]
    obs = sum(diffs) / len(diffs)
    ge = 0
    for _ in range(iters):
        m = sum(d if RNG.random() < 0.5 else -d for d in diffs) / len(diffs)
        if m >= obs - 1e-12:
            ge += 1
    return (ge + 1) / (iters + 1)


def _cell_rows(cell, arts, e1_rows, e0_rows, donor_rb, e1_codes, art_codes):
    """Return per-problem (e1_excess, e0_excess, e1_jacc, e0_jacc), + elaboration ratios.
    e0_rows: list aligned to arts of lists-of-gen-results (each with failing,n_tests);
             for the 1.5B cell E0 is the donor base gens (artifact cand excluded)."""
    out, dropped = [], 0
    elab = []  # (ratio, gen_fails_artifact_test)
    for i, a in enumerate(arts):
        qid, ci, n = a["qid"], a["cand_idx"], a["n_tests"]
        A = donor_rb[qid][ci]["failing"]
        e1 = e1_rows[i]
        e0 = e0_rows[i]
        # validity: every contributing gen must match n_tests
        gens = e1 + e0
        if any(g.get("n_tests") != n for g in gens):
            dropped += 1
            continue
        e1x = sum(_excess(g["failing"], A, n) for g in e1) / len(e1)
        e0x = sum(_excess(g["failing"], A, n) for g in e0) / len(e0)
        e1j = sum(_jacc(g["failing"], A) for g in e1) / len(e1)
        e0j = sum(_jacc(g["failing"], A) for g in e0) / len(e0)
        out.append((e1x, e0x, e1j, e0j))
        # elaboration: among E1 gens failing >=1 of the artifact's tests
        acode = art_codes[i]
        for j, g in enumerate(e1):
            if set(g["failing"]) & set(A):
                gc = e1_codes[i][j]
                if gc and acode:
                    elab.append(difflib.SequenceMatcher(None, gc, acode).ratio())
    return out, dropped, elab


def _run_cell(name, kind):
    donor_rb, donor_cb = _donor_by_qid()
    if kind in ("coder3b", "coder1p5b"):
        arts = _d2c44()
        art_codes = [a["code"] for a in arts]
    else:  # h7 matched cells
        m = _j("artifacts/h7_matched_artifacts.json")["cells"][name]
        arts = [{"qid": a["qid"], "cand_idx": a["cand_idx"], "n_tests": a["n_tests"]}
                for a in m["artifacts"]]
        art_codes = [donor_cb[a["qid"]][a["cand_idx"]] for a in m["artifacts"]]
    n = len(arts)

    if kind == "coder3b":
        res = _j("runs/modal/j6_q1a_res_qwen3b.json")
        cand = _j("runs/modal/j6_q1a_cand_qwen3b.json")
        e0_rows, e1_rows = res[:n], res[n:]
        e1_codes = [cand[n + i]["codes"] for i in range(n)]
    elif kind == "coder1p5b":
        # E1 = conditioned d2c pool; E0 = base-model donor gens (artifact cand excluded)
        d2c_res = _j("runs/modal/d2c_res.json")["results"]
        d2c_cand = _j("runs/modal/d2c_cand.json")
        # d2c order must match arts order (both from the w0b iteration)
        assert [c["qid"] for c in d2c_cand] == [a["qid"] for a in arts], "d2c order mismatch"
        e1_rows = d2c_res
        e1_codes = [c["codes"] for c in d2c_cand]
        e0_rows = []
        for a in arts:
            rows = [r for k, r in enumerate(donor_rb[a["qid"]]) if k != a["cand_idx"]]
            e0_rows.append(rows)
    else:  # M-cells (j7)
        res = _j(f"runs/modal/j7_res_{name}.json")
        cand = _j(f"runs/modal/j7_cand_{name}.json")
        e0_rows, e1_rows = res[:n], res[n:]
        e1_codes = [cand[n + i]["codes"] for i in range(n)]

    rows, dropped, elab = _cell_rows(name, arts, e1_rows, e0_rows, donor_rb,
                                     e1_codes, art_codes)
    if not rows:
        return {"cell": name, "n": 0, "note": "all problems dropped (n_tests mismatch)"}
    e1x = [r[0] for r in rows]
    e0x = [r[1] for r in rows]
    diffs = [a - b for a, b in zip(e1x, e0x)]
    mean_e1, mean_e0 = sum(e1x) / len(e1x), sum(e0x) / len(e0x)
    p = _perm_p_one_sided(diffs)
    n_pos = sum(1 for d in diffs if d > 1e-9)
    verdict = ("RECLASS-consistent (E1 excess > E0, p<0.05)" if p < 0.05 and mean_e1 > mean_e0
               else "OOD-consistent (E1 ~ E0)")
    return {"cell": name, "kind": kind, "n_problems": len(rows), "dropped": dropped,
            "mean_e1_excess": round(mean_e1, 4), "mean_e0_excess": round(mean_e0, 4),
            "delta_e1_minus_e0": round(mean_e1 - mean_e0, 4),
            "mean_e1_jaccard": round(sum(r[2] for r in rows) / len(rows), 4),
            "mean_e0_jaccard": round(sum(r[3] for r in rows) / len(rows), 4),
            "p_one_sided_e1_gt_e0": round(p, 4),
            "n_problems_e1_gt_e0": f"{n_pos}/{len(diffs)}",
            "elaboration_ratio_mean": round(sum(elab) / len(elab), 4) if elab else None,
            "elaboration_n": len(elab), "verdict": verdict}


def main():
    cells = [("coder1p5b_sink", "coder1p5b"), ("qwen3b_sink", "coder3b"),
             ("M4_coder7b", "m4"), ("M1_deepseek1p3b", "m1")]
    results = []
    print(f"{'cell':22s} {'n':>4s} {'E1_exc':>7s} {'E0_exc':>7s} {'Δ':>7s} "
          f"{'p':>7s} {'E1>E0':>7s} {'elab':>6s}  verdict")
    print("-" * 100)
    for name, kind in cells:
        r = _run_cell(name, kind)
        results.append(r)
        if r.get("n_problems"):
            el = f"{r['elaboration_ratio_mean']:.3f}" if r["elaboration_ratio_mean"] is not None else "  n/a"
            print(f"{name:22s} {r['n_problems']:4d} {r['mean_e1_excess']:+7.3f} "
                  f"{r['mean_e0_excess']:+7.3f} {r['delta_e1_minus_e0']:+7.3f} "
                  f"{r['p_one_sided_e1_gt_e0']:7.4f} {r['n_problems_e1_gt_e0']:>7s} "
                  f"{el:>6s}  {r['verdict']}")
        else:
            print(f"{name:22s}  {r.get('note')}")

    sinks = [r for r in results if r["cell"] != "M1_deepseek1p3b" and r.get("n_problems")]
    sink_reclass = all("RECLASS" in r["verdict"] for r in sinks)
    ctrl = next(r for r in results if r["cell"] == "M1_deepseek1p3b")
    call = ("D1 => M-RECLASS (all sink cells show E1 excess > E0; control at null)"
            if sink_reclass and "OOD" in ctrl.get("verdict", "")
            else "D1 => M-OOD or MIXED (see per-cell)")
    print("\nD1 CALL:", call)
    out = {"_label": "Phase 8 D1 inherited-error [PHASE_8.md D1]",
           "metric": "excess = |G∩A| - |G|*|A|/n; paired one-sided E1>E0 across problems",
           "cells": results, "d1_call": call}
    (REPO / "artifacts/h8_d1_inherited_error.json").write_text(json.dumps(out, indent=2))
    print("wrote artifacts/h8_d1_inherited_error.json")


if __name__ == "__main__":
    main()
