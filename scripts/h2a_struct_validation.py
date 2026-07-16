#!/usr/bin/env python3
"""H2a amended-run validation: arm PULL/AST columns, structural novelty of
recoveries vs the failure pool, error-type stratification ([PHASE_4.md] H2a part 2)."""
import json
import random
import statistics as st
import sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import h0a_ast_distance as h


def main():
    cand = json.load(open("runs/modal/lcb_cand_lcb_r2_base_medium_T08.json"))
    resp = json.load(open("runs/modal/lcb_res_lcb_r2_base_medium_T08.json"))
    arts, fails = {}, {}
    for qid, crow, rrow in zip(resp["question_ids"], cand["codes"], resp["results"]):
        if any(r["passed"] for r in rrow):
            continue
        best_i, best_f = None, -1.0
        for i, (c, r) in enumerate(zip(crow, rrow)):
            if c and r["frac"] > best_f:
                best_i, best_f = i, r["frac"]
        if best_i is not None:
            arts[qid] = crow[best_i]
            fails[qid] = [c for c in crow if c]

    gen = json.load(open("runs/modal/h2a_cand.json"))
    res = json.load(open("runs/modal/h2a_res.json"))
    n = 68
    pool = Pool(10)

    def arm_stats(rows):
        tasks = [(arts[g["qid"]], g["codes"]) for g in rows if g["qid"] in arts]
        out = pool.map(h.dists_for_record, tasks)
        ast = [st.mean([r["ast"] for r in rec if r.get("status") == "ok"])
               for rec in out if any(r.get("status") == "ok" for r in rec)]
        lex = [st.mean([r["lex"] for r in rec if "lex" in r])
               for rec in out if any("lex" in r for r in rec)]
        return st.mean(ast), st.mean(lex)

    b1_ast, b1_lex = arm_stats(gen[:n])
    hi_ast, hi_lex = arm_stats(gen[n:])
    print(f"B1-50:   AST-PULL {b1_ast:.3f} / lex {b1_lex:.3f}")
    print(f"HINT-50: AST-PULL {hi_ast:.3f} / lex {hi_lex:.3f}")

    rec = json.load(open("artifacts/h2a_hint_arm.json"))["recovered_qids"]["hint"]
    first = {g["qid"]: (g, row) for g, row in zip(gen[n:], res[n:])}
    rng = random.Random(17)
    nov = {}
    for qid in rec:
        g, row = first[qid]
        passing = [c for c, r in zip(g["codes"], row) if r["passed"] and c]
        fl = fails[qid]
        fl = fl if len(fl) <= 12 else rng.sample(fl, 12)
        ds = []
        for pc in passing[:3]:
            out = pool.map(h.dists_for_record, [(pc, fl)])[0]
            ds += [r["ast"] for r in out if r.get("status") == "ok"]
        nov[qid] = round(min(ds), 3) if ds else None
    print("min AST-dist of recovered solution vs failure pool:", nov)
    pool.close()
    pool.join()

    tr = {t["qid"]: t["err"] for t in json.load(open("runs/modal/r3_traces_medium.json"))}
    base = Counter(tr.values())
    recc = Counter(tr[q] for q in rec if q in tr)
    print("stratum error base:", dict(base), "| recovered:", dict(recc))
    json.dump({"arm_pull": {"B1": {"ast": b1_ast, "lex": b1_lex},
                            "HINT": {"ast": hi_ast, "lex": hi_lex}},
               "novelty_min_ast_vs_failpool": nov,
               "error_type": {"stratum_base": dict(base), "recovered": dict(recc)}},
              open("artifacts/h2a_validation_struct.json", "w"), indent=1)
    print("wrote artifacts/h2a_validation_struct.json")


if __name__ == "__main__":
    main()
