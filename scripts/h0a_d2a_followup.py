#!/usr/bin/env python3
"""H0a follow-up (POST-HOC, unregistered — [PHASE_4.md] H0a RESULT).

The pre-registered L1b tested provenance-irrelevance on E1-vs-E2, which conflates
the instruction verb with provenance (the cells differ in both). The correct
instrument is the D2a 2x2 (verb x provenance, same artifact). This recomputes the
2x2 under the frozen AST metric. Labeled post-hoc; corrects the mis-specification,
does not replace the recorded L1b miss.
"""
import json
import sys
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import h0a_ast_distance as h


def main():
    m3 = json.loads((h.REPO / "runs/modal/m3_candidates.json").read_text())
    labels = json.loads((h.REPO / "runs/modal/m3_labels.json").read_text())["labels"]
    arts = {}
    for pid, row, lab in zip(m3["problem_ids"], m3["candidates"], labels):
        fail = next((c["code"] for c, p in zip(row, lab) if not p and c["code"]), None)
        good = next((c["code"] for c, p in zip(row, lab) if p and c["code"]), None)
        if fail and good:
            arts[pid] = fail
        if len(arts) >= 60:
            break

    g = json.load(open(h.REPO / "runs/modal/dmeasure_d2a_gen.json"))["results"]
    cells = defaultdict(list)
    for r in g:
        if r["pid"] in arts:
            cells[(r["cond"], r["temp"])].append((arts[r["pid"]], r["codes"]))

    pool = Pool(10)
    out = {}
    for k in sorted(cells):
        out[f"{k[0]}@{k[1]}"] = h.agg(pool.map(h.dists_for_record, cells[k]))
    pool.close()
    pool.join()

    deltas = {}
    for T in (0.0, 0.8, 1.2):
        e1, e1p, e2p, e2 = (out[f"{c}@{T}"]["ast_pull_mean"]
                            for c in ("E1", "E1p", "E2p", "E2"))
        deltas[str(T)] = {
            "cells_ast": {"E1": e1, "E1p": e1p, "E2p": e2p, "E2": e2},
            "max_provenance_delta": max(abs(e1 - e2p), abs(e1p - e2)),
            "max_verb_delta": max(abs(e1 - e1p), abs(e2p - e2)),
        }
        print(f"T={T}: AST E1 {e1:.3f} E1p {e1p:.3f} E2p {e2p:.3f} E2 {e2:.3f} | "
              f"prov Δ {deltas[str(T)]['max_provenance_delta']:.4f} | "
              f"verb Δ {deltas[str(T)]['max_verb_delta']:.4f}")

    json.dump({"_label": "H0a follow-up (POST-HOC, unregistered) — D2a 2x2 under AST; "
                         "corrects the mis-specified L1b",
               "cells": {c: {"ast": v["ast_pull_mean"], "lex": v["lex_pull_mean"]}
                         for c, v in out.items()},
               "deltas": deltas},
              open(h.REPO / "artifacts/h0a_d2a_ast_followup.json", "w"), indent=2)
    print("wrote artifacts/h0a_d2a_ast_followup.json")


if __name__ == "__main__":
    main()
