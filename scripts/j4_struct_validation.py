#!/usr/bin/env python3
"""J4 validation: error-type stratification + AST novelty of HINT recoveries
vs the DeepSeek failure pool ([PHASE_5.md] J4)."""
import json
import random
import sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import h0a_ast_distance as h


def main():
    scr = json.load(open("artifacts/h5_deepseek_medium_screen.json"))
    qids = scr["stratum_qids"]
    out4 = json.load(open("artifacts/h5_deepseek_fourarm.json"))
    cand = json.load(open("runs/modal/j4_screen_cand.json"))
    fails = {g["qid"]: [c for c in g["codes"] if c] for g in cand}
    gen = json.load(open("runs/modal/j4_arms_cand.json"))
    res = json.load(open("runs/modal/j4_arms_res.json"))
    n, na = len(qids), out4["n_trace_arm"]
    hint_gen, hint_res = gen[n + na:2 * n + na], res[n + na:2 * n + na]
    first = {g["qid"]: (g, row) for g, row in zip(hint_gen, hint_res)}
    rng = random.Random(17)
    pool = Pool(10)
    nov = {}
    for qid in out4["recovered_qids"]["HINT"]:
        g, row = first[qid]
        passing = [c for c, r in zip(g["codes"], row) if r["passed"] and c]
        fl = fails[qid]
        fl = fl if len(fl) <= 12 else rng.sample(fl, 12)
        ds = []
        for pc in passing[:3]:
            o = pool.map(h.dists_for_record, [(pc, fl)])[0]
            ds += [r["ast"] for r in o if r.get("status") == "ok"]
        nov[qid] = round(min(ds), 3) if ds else None
    pool.close(); pool.join()
    tr = {t["qid"]: t["err"] for t in json.load(open("runs/modal/j4_traces.json"))}
    base = Counter(tr.values())
    recc = Counter(tr[q] for q in out4["recovered_qids"]["HINT"] if q in tr)
    out = {"novelty_min_ast_vs_failpool": nov,
           "error_type": {"stratum_base": dict(base), "hint_recovered": dict(recc)}}
    json.dump(out, open("artifacts/h5_deepseek_validation_struct.json", "w"), indent=1)
    print("novelty:", nov)
    print("error base:", dict(base), "| hint-recovered:", dict(recc))


if __name__ == "__main__":
    main()
