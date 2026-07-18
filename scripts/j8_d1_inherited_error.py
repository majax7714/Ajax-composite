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
    out, dropped, contrasts = [], 0, []
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
        # D1' induced-failure enrichment: per test t, P(E1 fails t) - P(E0 fails t);
        # contrast = mean induced on artifact's failing tests A minus mean on non-A.
        Aset = set(A)
        e1f = [set(g["failing"]) for g in e1]
        e0f = [set(g["failing"]) for g in e0]
        def _induced(t):
            return (sum(t in s for s in e1f) / len(e1f)
                    - sum(t in s for s in e0f) / len(e0f))
        indA = [_induced(t) for t in range(n) if t in Aset]
        indN = [_induced(t) for t in range(n) if t not in Aset]
        if indA and indN:
            contrasts.append(sum(indA) / len(indA) - sum(indN) / len(indN))
        # elaboration: among E1 gens failing >=1 of the artifact's tests
        acode = art_codes[i]
        for j, g in enumerate(e1):
            if set(g["failing"]) & set(A):
                gc = e1_codes[i][j]
                if gc and acode:
                    elab.append(difflib.SequenceMatcher(None, gc, acode).ratio())
    return out, dropped, elab, contrasts


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

    rows, dropped, elab, contrasts = _cell_rows(name, arts, e1_rows, e0_rows, donor_rb,
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
    # D1' induced-failure enrichment
    mean_c = sum(contrasts) / len(contrasts) if contrasts else None
    p_c = _perm_p_one_sided(contrasts) if contrasts else None
    n_pos_c = sum(1 for c in contrasts if c > 1e-9)
    prime_verdict = ("RECLASS (induced failures enriched on artifact's tests, p<0.05)"
                     if p_c is not None and p_c < 0.05 and mean_c > 0
                     else "OOD (induced failures uniform)")
    return {"cell": name, "kind": kind, "n_problems": len(rows), "dropped": dropped,
            "mean_e1_excess": round(mean_e1, 4), "mean_e0_excess": round(mean_e0, 4),
            "delta_e1_minus_e0": round(mean_e1 - mean_e0, 4),
            "mean_e1_jaccard": round(sum(r[2] for r in rows) / len(rows), 4),
            "mean_e0_jaccard": round(sum(r[3] for r in rows) / len(rows), 4),
            "p_one_sided_e1_gt_e0": round(p, 4),
            "n_problems_e1_gt_e0": f"{n_pos}/{len(diffs)}",
            "elaboration_ratio_mean": round(sum(elab) / len(elab), 4) if elab else None,
            "elaboration_n": len(elab), "verdict": verdict,
            "prime_n": len(contrasts),
            "prime_mean_contrast": round(mean_c, 4) if mean_c is not None else None,
            "prime_p_one_sided": round(p_c, 4) if p_c is not None else None,
            "prime_n_pos": f"{n_pos_c}/{len(contrasts)}" if contrasts else None,
            "prime_verdict": prime_verdict}


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

    print(f"\n=== D1' induced-failure enrichment (sink-specific) ===")
    print(f"{'cell':22s} {'n':>4s} {'contrast':>9s} {'p':>7s} {'>0':>7s}  verdict")
    print("-" * 80)
    for r in results:
        if r.get("prime_mean_contrast") is not None:
            print(f"{r['cell']:22s} {r['prime_n']:4d} {r['prime_mean_contrast']:+9.4f} "
                  f"{r['prime_p_one_sided']:7.4f} {r['prime_n_pos']:>7s}  {r['prime_verdict']}")

    sinks = [r for r in results if r["cell"] != "M1_deepseek1p3b" and r.get("n_problems")]
    ctrl = next(r for r in results if r["cell"] == "M1_deepseek1p3b")
    ctrl_c = ctrl["prime_mean_contrast"]
    # Clean discrimination would require the sink cells to EXCEED the clean control.
    sinks_exceed_ctrl = all(r["prime_mean_contrast"] > ctrl_c for r in sinks)
    sink_fid = "/".join(f"{r['elaboration_ratio_mean']:.2f}" for r in sinks)
    if sinks_exceed_ctrl:
        call = "D1' => M-RECLASS (sink cells exceed the clean control on artifact-specific induced failures)"
    else:
        call = ("D1'/D1 => INCONCLUSIVE for RECLASS-vs-OOD. Artifact-imitation is "
                f"FAMILY-GENERAL: the clean control M1 shows the STRONGEST inheritance "
                f"(excess {ctrl['delta_e1_minus_e0']:+.2f}) AND artifact-specificity "
                f"(contrast {ctrl_c:+.3f}) of all cells — it copies the above-its-level "
                f"artifact (fidelity {ctrl['elaboration_ratio_mean']:.2f}) and lands AT "
                f"it (lift). The only SINK-SPECIFIC signal is fidelity: sink cells "
                f"ELABORATE (fidelity {sink_fid}) and land BELOW the artifact; the clean "
                f"cell COPIES and lands at it. D1 leans 'elaboration-degrades' but "
                f"cannot assign RECLASS vs OOD.")
    print("\nD1 CALL:", call)
    out = {"_label": "Phase 8 D1 inherited-error [PHASE_8.md D1]",
           "metric": "excess = |G∩A| - |G|*|A|/n; paired one-sided E1>E0 across problems",
           "d1_note": "as-pre-registered excess metric is INCONCLUSIVE (control M1 not "
                      "at null — inheritance is family-general imitation)",
           "prime_metric": "induced(t)=P(E1 fails t)-P(E0 fails t); contrast = mean "
                           "induced on artifact-failing tests minus non-artifact tests",
           "cells": results, "d1_prime_call": call}
    (REPO / "artifacts/h8_d1_inherited_error.json").write_text(json.dumps(out, indent=2))
    print("wrote artifacts/h8_d1_inherited_error.json")


if __name__ == "__main__":
    main()
