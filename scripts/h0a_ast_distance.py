#!/usr/bin/env python3
"""H0a — AST-distance robustness of the escape-distance law ([PHASE_4.md] H0a).

Frozen metric: AST-PULL(gen, art) = ZS-TED(canon(gen), canon(art)) / (|g|+|a|).
Canonicalization: Name/arg/def-names/import-asname -> _v; Constant -> type name;
Attribute.attr and import module names kept. Unit costs. Parse failures and
trees > 3000 nodes excluded + counted.

Legs: A dmeasure cells, B E7 cells, C R3 arms (medium + easy), D destination
geometry (pairwise, <=12 codes/problem, seed 17). Lexical PULL recomputed from
the same records, side by side. Pure CPU over committed pools.

Output: artifacts/h0a_ast_distance.json
"""
from __future__ import annotations

import ast
import ctypes
import difflib
import json
import math
import os
import random
import statistics as st
import subprocess
import sys
import tempfile
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

REPO = Path(__file__).parents[1]
NODE_CAP = 3000
sys.setrecursionlimit(100000)  # module level: workers re-import under forkserver

# ---------------------------------------------------------------- canonical AST


def canon_tree(code):
    """-> (label, children) tree or None on parse failure."""
    try:
        t = ast.parse(code)
    except (SyntaxError, ValueError, MemoryError, RecursionError):
        return None

    def build(node):
        label = type(node).__name__
        if isinstance(node, ast.Attribute):
            label += ":" + node.attr
        elif isinstance(node, (ast.Name, ast.arg)):
            label += ":_v"
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            label += ":_v"
        elif isinstance(node, ast.Constant):
            label += ":" + type(node.value).__name__
        elif isinstance(node, ast.alias):
            label += ":" + node.name  # module/symbol name kept; asname dropped
        return (label, [build(c) for c in ast.iter_child_nodes(node)])

    try:
        return build(t)
    except RecursionError:
        return None


def flatten(tree):
    """Postorder (labels, lmld, keyroots). Iterative to dodge recursion limits."""
    labels, lmld = [], []
    result_stack = []
    stack = [(tree, False)]
    while stack:
        node, visited = stack.pop()
        label, children = node
        if not visited:
            stack.append((node, True))
            for c in reversed(children):
                stack.append((c, False))
        else:
            if children:
                child_lmls = result_stack[-len(children):]
                del result_stack[-len(children):]
                my_lml = child_lmls[0]
            else:
                my_lml = len(labels)
            labels.append(label)
            lmld.append(my_lml)
            result_stack.append(my_lml)
    last = {}
    for i, l in enumerate(lmld):
        last[l] = i
    keyroots = sorted(last.values())
    return labels, lmld, keyroots


# ---------------------------------------------------------------- ZS-TED (C kernel)

C_SRC = r"""
#include <stdlib.h>
static int min3(int a, int b, int c){int m=a<b?a:b;return m<c?m:c;}
int ted(const int*al,const int*alm,const int*akr,int ank,int an,
        const int*bl,const int*blm,const int*bkr,int bnk,int bn){
    int *TD = malloc(sizeof(int)*an*bn);
    int maxm = an+2, maxn = bn+2;
    int *fd = malloc(sizeof(int)*maxm*maxn);
    for(int ki=0;ki<ank;ki++){
        int i = akr[ki];
        for(int kj=0;kj<bnk;kj++){
            int j = bkr[kj];
            int m = i - alm[i] + 2, n = j - blm[j] + 2;
            for(int x=0;x<m;x++) fd[x*maxn+0]=x;
            for(int y=0;y<n;y++) fd[0*maxn+y]=y;
            for(int x=1;x<m;x++){
                int xi = x + alm[i] - 1;
                for(int y=1;y<n;y++){
                    int yj = y + blm[j] - 1;
                    if(alm[xi]==alm[i] && blm[yj]==blm[j]){
                        int cost = (al[xi]==bl[yj])?0:1;
                        int v = min3(fd[(x-1)*maxn+y]+1, fd[x*maxn+(y-1)]+1,
                                     fd[(x-1)*maxn+(y-1)]+cost);
                        fd[x*maxn+y]=v;
                        TD[xi*bn+yj]=v;
                    } else {
                        int p = alm[xi]-alm[i], q = blm[yj]-blm[j];
                        fd[x*maxn+y] = min3(fd[(x-1)*maxn+y]+1, fd[x*maxn+(y-1)]+1,
                                            fd[p*maxn+q]+TD[xi*bn+yj]);
                    }
                }
            }
        }
    }
    int r = TD[(an-1)*bn+(bn-1)];
    free(TD); free(fd);
    return r;
}
"""

_LIB = None


def _lib():
    global _LIB
    if _LIB is None:
        so = Path(tempfile.gettempdir()) / f"h0a_ted_{os.getpid()}.so"
        csrc = Path(tempfile.gettempdir()) / f"h0a_ted_{os.getpid()}.c"
        csrc.write_text(C_SRC)
        subprocess.run(["cc", "-O2", "-shared", "-fPIC", "-o", str(so), str(csrc)],
                       check=True)
        _LIB = ctypes.CDLL(str(so))
        _LIB.ted.restype = ctypes.c_int
    return _LIB


def _arr(xs):
    return (ctypes.c_int * len(xs))(*xs)


def ted_c(fa, fb):
    la, ma, ka = fa
    lb, mb, kb = fb
    interned = {}
    def ints(ls):
        return [interned.setdefault(x, len(interned)) for x in ls]
    return _lib().ted(_arr(ints(la)), _arr(ma), _arr(ka), len(ka), len(la),
                      _arr(ints(lb)), _arr(mb), _arr(kb), len(kb), len(lb))


def ted_py(fa, fb):
    """Pure-python reference for validation."""
    la, ma, ka = fa
    lb, mb, kb = fb
    an, bn = len(la), len(lb)
    TD = [[0] * bn for _ in range(an)]
    for i in ka:
        for j in kb:
            m, n = i - ma[i] + 2, j - mb[j] + 2
            fd = [[0] * n for _ in range(m)]
            for x in range(1, m):
                fd[x][0] = x
            for y in range(1, n):
                fd[0][y] = y
            for x in range(1, m):
                xi = x + ma[i] - 1
                for y in range(1, n):
                    yj = y + mb[j] - 1
                    if ma[xi] == ma[i] and mb[yj] == mb[j]:
                        cost = 0 if la[xi] == lb[yj] else 1
                        fd[x][y] = min(fd[x - 1][y] + 1, fd[x][y - 1] + 1,
                                       fd[x - 1][y - 1] + cost)
                        TD[xi][yj] = fd[x][y]
                    else:
                        p, q = ma[xi] - ma[i], mb[yj] - mb[j]
                        fd[x][y] = min(fd[x - 1][y] + 1, fd[x][y - 1] + 1,
                                       fd[p][q] + TD[xi][yj])
    return TD[an - 1][bn - 1]


def validate():
    """Classic ZS example + identity + C==py on random trees."""
    def mk(s):  # tiny lisp-ish parser: f(d(a,c(b)),e)
        s = s.replace(" ", "")
        pos = [0]
        def parse():
            lab = ""
            while pos[0] < len(s) and s[pos[0]] not in "(),":
                lab += s[pos[0]]; pos[0] += 1
            ch = []
            if pos[0] < len(s) and s[pos[0]] == "(":
                pos[0] += 1
                while True:
                    ch.append(parse())
                    if s[pos[0]] == ",":
                        pos[0] += 1
                    else:
                        break
                assert s[pos[0]] == ")"; pos[0] += 1
            return (lab, ch)
        return parse()

    t1, t2 = mk("f(d(a,c(b)),e)"), mk("f(c(d(a,b)),e)")
    f1, f2 = flatten(t1), flatten(t2)
    assert ted_py(f1, f2) == 2, ted_py(f1, f2)
    assert ted_c(f1, f2) == 2, ted_c(f1, f2)
    assert ted_c(f1, f1) == 0 and ted_py(f2, f2) == 0

    rng = random.Random(17)
    def rand_tree(depth=0):
        lab = rng.choice("abcdef")
        n = 0 if depth > 3 or rng.random() < 0.3 else rng.randint(1, 3)
        return (lab, [rand_tree(depth + 1) for _ in range(n)])
    for _ in range(200):
        fa, fb = flatten(rand_tree()), flatten(rand_tree())
        assert ted_c(fa, fb) == ted_py(fa, fb)
    return True


# ---------------------------------------------------------------- distance workers

def dists_for_record(task):
    """(art_code, [codes]) -> per-code {ast_pull, lex_pull, status}."""
    art_code, codes = task
    fa_tree = canon_tree(art_code)
    out = []
    fa = None
    if fa_tree is not None:
        la = flatten(fa_tree)
        if len(la[0]) <= NODE_CAP:
            fa = la
    for cd in codes:
        if not cd:
            out.append({"status": "no_code"})
            continue
        lex = 1.0 - difflib.SequenceMatcher(None, cd, art_code).ratio()
        tr = canon_tree(cd)
        if tr is None:
            out.append({"status": "parse_fail", "lex": lex})
            continue
        fb = flatten(tr)
        if len(fb[0]) > NODE_CAP or fa is None:
            out.append({"status": "cap_or_art_fail", "lex": lex})
            continue
        d = ted_c(fa, fb)
        out.append({"status": "ok", "lex": lex,
                    "ast": d / (len(fa[0]) + len(fb[0]))})
    return out


def pairwise_for_problem(task):
    """(codes subsampled) -> condensed pairwise ast-dist list (or None entries skipped)."""
    codes = task
    flats = []
    for cd in codes:
        tr = canon_tree(cd) if cd else None
        if tr is None:
            continue
        f = flatten(tr)
        if len(f[0]) <= NODE_CAP:
            flats.append(f)
    ds = []
    for i in range(len(flats)):
        for j in range(i + 1, len(flats)):
            d = ted_c(flats[i], flats[j])
            ds.append(d / (len(flats[i][0]) + len(flats[j][0])))
    return {"n_used": len(flats), "pairs": ds}


# ---------------------------------------------------------------- aggregation

def agg(rows_of_dicts):
    """list of per-record lists -> cell stats. Record mean first (matches committed
    aggregation), then across records."""
    per_rec_ast, per_rec_lex = [], []
    counts = defaultdict(int)
    for rec in rows_of_dicts:
        asts = [r["ast"] for r in rec if r.get("status") == "ok"]
        lexs = [r["lex"] for r in rec if "lex" in r]
        for r in rec:
            counts[r["status"]] += 1
        if asts:
            per_rec_ast.append(sum(asts) / len(asts))
        if lexs:
            per_rec_lex.append(sum(lexs) / len(lexs))
    return {
        "n_records": len(rows_of_dicts),
        "ast_pull_mean": st.mean(per_rec_ast) if per_rec_ast else None,
        "ast_pull_sd": st.stdev(per_rec_ast) if len(per_rec_ast) > 1 else None,
        "lex_pull_mean": st.mean(per_rec_lex) if per_rec_lex else None,
        "exclusions": dict(counts),
    }


def spearman(xs, ys):
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    rx, ry = ranks(xs), ranks(ys)
    mx, my = st.mean(rx), st.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else 0.0


# ---------------------------------------------------------------- main

def main():
    print("validating TED implementation ...")
    validate()
    print("  ok (classic example = 2; C == py on 200 random tree pairs)")

    m3 = json.loads((REPO / "runs/modal/m3_candidates.json").read_text())
    labels = json.loads((REPO / "runs/modal/m3_labels.json").read_text())["labels"]
    arts = {}
    for pid, row, lab in zip(m3["problem_ids"], m3["candidates"], labels):
        fail = next((c["code"] for c, p in zip(row, lab) if not p and c["code"]), None)
        good = next((c["code"] for c, p in zip(row, lab) if p and c["code"]), None)
        if fail and good:
            arts[pid] = {"fail": fail, "correct": good}
        if len(arts) >= 60:
            break

    pool = Pool(max(1, os.cpu_count() - 2))

    # ---- Leg A + B: dmeasure + e7 cells
    cells = defaultdict(list)   # (cond,temp) -> list of (art, codes) tasks
    for fname, tag in (("dmeasure_gen.json", "A"), ("dmeasure_e7_gen.json", "B")):
        gen = json.loads((REPO / "runs/modal" / fname).read_text())["results"]
        for r in gen:
            a = arts.get(r["pid"])
            if not a:
                continue
            art = a["correct"] if r["cond"] == "E5" else a["fail"]
            cells[(tag, r["cond"], r["temp"])].append((art, r["codes"]))

    cell_stats = {}
    for key in sorted(cells):
        res = pool.map(dists_for_record, cells[key])
        cell_stats[f"{key[1]}@{key[2]}" + ("_e7run" if key[0] == "B" else "")] = agg(res)
        print(f"  leg A/B cell {key} done ({len(res)} records)")

    # ---- Leg C: R3 arms
    def stratum_artifacts(cand_f, res_f):
        cand = json.loads((REPO / "runs/modal" / cand_f).read_text())
        res = json.loads((REPO / "runs/modal" / res_f).read_text())
        out = {}
        for qid, crow, rrow in zip(res["question_ids"], cand["codes"], res["results"]):
            if any(r["passed"] for r in rrow):
                continue
            best_i, best_f = None, -1.0
            for i, (c, r) in enumerate(zip(crow, rrow)):
                if c and r["frac"] > best_f:
                    best_i, best_f = i, r["frac"]
            if best_i is not None:
                out[qid] = crow[best_i]
        return out

    r3_arts = {
        "medium": stratum_artifacts("lcb_cand_lcb_r2_base_medium_T08.json",
                                    "lcb_res_lcb_r2_base_medium_T08.json"),
        "easy": stratum_artifacts("lcb_cand_lcb_r2_base_T08.json",
                                  "lcb_res_lcb_r2_base_T08.json"),
    }
    r3_stats = {}
    r3_pools = {}
    for stratum in ("medium", "easy"):
        for arm in ("B1", "ANCHOR", "TRACE", "MODELABS"):
            rows = json.loads(
                (REPO / f"runs/modal/r3_cand_{stratum}_{arm}.json").read_text())
            tasks = [(r3_arts[stratum][r["qid"]], r["codes"]) for r in rows
                     if r["qid"] in r3_arts[stratum]]
            res = pool.map(dists_for_record, tasks)
            r3_stats[f"{stratum}_{arm}"] = agg(res)
            r3_pools[(stratum, arm)] = rows
            print(f"  leg C {stratum}/{arm} done ({len(tasks)} problems x <=50)")

    # ---- Leg D: destination geometry (pairwise, <=12 codes/problem, seed 17)
    rng = random.Random(17)

    def subsample(codes, k=12):
        ok = [c for c in codes if c]
        return ok if len(ok) <= k else rng.sample(ok, k)

    legd_sets = {}
    e1_12 = [(a, c) for (a, c) in cells[("A", "E1", 1.2)]]
    legd_sets["E1@1.2"] = [subsample(codes, 12) for _, codes in e1_12]
    legd_sets["E7@1.2"] = [subsample(codes, 12) for _, codes in cells[("B", "E7", 1.2)]]
    legd_sets["TRACE_medium"] = [
        subsample(r["codes"], 12) for r in r3_pools[("medium", "TRACE")]
        if r["qid"] in r3_arts["medium"]]

    legd = {}
    for name, sets in legd_sets.items():
        res = pool.map(pairwise_for_problem, sets)
        all_pairs = [d for r in res for d in r["pairs"]]
        # single-linkage cluster count per problem at 0.5 x set mean pairwise
        thr = 0.5 * st.mean(all_pairs) if all_pairs else None
        n_clusters, max_frac = [], []
        for sset, r in zip(sets, res):
            n = r["n_used"]
            if n < 3 or not r["pairs"]:
                continue
            # rebuild condensed index
            parent = list(range(n))
            def find(x):
                while parent[x] != x:
                    parent[x] = parent[parent[x]]
                    x = parent[x]
                return x
            idx = 0
            for i in range(n):
                for j in range(i + 1, n):
                    if r["pairs"][idx] <= thr:
                        parent[find(i)] = find(j)
                    idx += 1
            comps = defaultdict(int)
            for i in range(n):
                comps[find(i)] += 1
            n_clusters.append(len(comps))
            max_frac.append(max(comps.values()) / n)
        legd[name] = {
            "mean_within_set_pairwise_ast": st.mean(all_pairs) if all_pairs else None,
            "n_pairs": len(all_pairs),
            "cluster_threshold": thr,
            "mean_n_clusters_per_problem": st.mean(n_clusters) if n_clusters else None,
            "mean_max_cluster_fraction": st.mean(max_frac) if max_frac else None,
            "n_problems_clustered": len(n_clusters),
        }
        print(f"  leg D {name} done ({len(all_pairs)} pairs)")

    pool.close()
    pool.join()

    # ---- verdict assembly (committed coverage; frozen 8-cell monotonicity set)
    cov = json.loads((REPO / "artifacts/dmeasure_conditioning.json").read_text())
    e7 = json.loads((REPO / "artifacts/dmeasure_e7.json").read_text())
    cover = {k: v["coverage_any_pass"] for k, v in cov["per_sample_D2b"]["cells"].items()}
    cover["E7@0.8"] = e7["cells"]["E7@0.8"]["coverage"]
    cover["E7@1.2"] = e7["cells"]["E7@1.2"]["coverage"]

    mono_cells = ["E1@0.0", "E1@0.8", "E1@1.2", "E2@0.0", "E2@0.8", "E2@1.2",
                  "E7@0.8", "E7@1.2"]
    def cellkey(c):
        return c + ("_e7run" if c.startswith("E7") else "")
    xs_ast = [cell_stats[cellkey(c)]["ast_pull_mean"] for c in mono_cells]
    xs_lex = [cell_stats[cellkey(c)]["lex_pull_mean"] for c in mono_cells]
    ys = [cover[c] for c in mono_cells]
    rho_ast = spearman(xs_ast, ys)
    rho_lex = spearman(xs_lex, ys)

    anchor = {t: cell_stats[f"E0@{t}"]["ast_pull_mean"] for t in (0.0, 0.8, 1.2)}
    anchor[1.5] = cell_stats["E0@1.5_e7run"]["ast_pull_mean"]
    L1 = all(
        max(cell_stats[f"{c}@{t}"]["ast_pull_mean"] for c in ("E1", "E2", "E5"))
        < anchor[t] for t in (0.8, 1.2))
    gap = {t: anchor[t] - max(cell_stats[f"{c}@{t}"]["ast_pull_mean"]
                              for c in ("E1", "E2")) for t in (0.8, 1.2)}
    L1b = all(abs(cell_stats[f"E1@{t}"]["ast_pull_mean"]
                  - cell_stats[f"E2@{t}"]["ast_pull_mean"]) < 0.15 * gap[t]
              for t in (0.8, 1.2))
    L2 = rho_ast >= 0.8
    L3_ratio = cell_stats["E1@1.2"]["ast_pull_mean"] / anchor[1.2]
    L3 = L3_ratio <= 0.60
    L4 = all(cell_stats[f"E7@{t}_e7run"]["ast_pull_mean"] < anchor[t]
             for t in (0.8, 1.2))
    tr, b1 = (r3_stats["medium_TRACE"]["ast_pull_mean"],
              r3_stats["medium_B1"]["ast_pull_mean"])
    L5_ratio = tr / b1
    L5 = ("iid_survives" if 0.8 <= L5_ratio <= 1.2 else
          "token_illusion" if L5_ratio < 0.8 else "above_b1")
    branch = "a" if (L1 and L2) else "b"

    out = {
        "_label": "H0a — the law under structural distance [PHASE_4.md H0a]",
        "metric": "ZS-TED(canonicalized AST)/(n1+n2); unit costs; Name/arg/def/"
                  "asname->_v, Constant->typename, Attribute.attr+import names kept;"
                  f" parse-fails excluded+counted; node cap {NODE_CAP}",
        "validation": "classic ZS example == 2; C kernel == pure-python on 200 random pairs",
        "cells": cell_stats,
        "r3_arms": r3_stats,
        "destination_geometry": legd,
        "monotonicity": {
            "cell_set": mono_cells,
            "coverage": dict(zip(mono_cells, ys)),
            "ast_pull": dict(zip(mono_cells, xs_ast)),
            "lex_pull": dict(zip(mono_cells, xs_lex)),
            "spearman_ast": rho_ast, "spearman_lex": rho_lex,
        },
        "anchor_ast": {str(k): v for k, v in anchor.items()},
        "verdicts": {
            "L1_attractor_holds": L1,
            "L1b_provenance_irrelevance": L1b,
            "L2_monotonicity": L2,
            "L3_stretch_ratio_E1_12_over_anchor": L3_ratio, "L3_holds": L3,
            "L4_repulsion_in_copy_territory": L4,
            "L5_trace_over_b1_ratio": L5_ratio, "L5_branch": L5,
            "branch": branch,
        },
    }
    (REPO / "artifacts/h0a_ast_distance.json").write_text(json.dumps(out, indent=2))

    print("\n=== H0a — the law under structural distance ===")
    print(f"  anchors (E0 vs fail): " +
          ", ".join(f"T{k} {v:.3f}" for k, v in anchor.items()))
    for c in ("E1", "E2", "E5"):
        print(f"  {c}: " + ", ".join(
            f"T{t} ast {cell_stats[f'{c}@{t}']['ast_pull_mean']:.3f}/"
            f"lex {cell_stats[f'{c}@{t}']['lex_pull_mean']:.3f}"
            for t in (0.0, 0.8, 1.2)))
    print(f"  E7: " + ", ".join(
        f"T{t} ast {cell_stats[f'E7@{t}_e7run']['ast_pull_mean']:.3f}/"
        f"lex {cell_stats[f'E7@{t}_e7run']['lex_pull_mean']:.3f}" for t in (0.8, 1.2)))
    print(f"  E1@1.5: ast {cell_stats['E1@1.5_e7run']['ast_pull_mean']:.3f}")
    print("  R3 medium arms (ast/lex): " + ", ".join(
        f"{a} {r3_stats[f'medium_{a}']['ast_pull_mean']:.3f}/"
        f"{r3_stats[f'medium_{a}']['lex_pull_mean']:.3f}"
        for a in ("B1", "ANCHOR", "TRACE", "MODELABS")))
    print(f"  monotonicity: Spearman ast {rho_ast:.3f} vs lex {rho_lex:.3f}")
    print(f"  verdicts: L1 {L1}  L1b {L1b}  L2 {L2}  L3 {L3} (ratio {L3_ratio:.3f})  "
          f"L4 {L4}  L5 {L5} (ratio {L5_ratio:.3f})  → branch ({branch})")
    print("wrote artifacts/h0a_ast_distance.json")


if __name__ == "__main__":
    main()
