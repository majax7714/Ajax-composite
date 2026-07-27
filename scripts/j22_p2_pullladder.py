"""Phase 22 P2 (free, $0) — string-space PULL across EIGHT committed cells, including the
scale ladder, where the sinking/clean contrast lives INSIDE one family.

EXPLORATORY per §10. Committed BEFORE running, with its predictions.

WHY THIS AND NOT MORE FAMILIES. §6 found PULL orders four models exactly as copy-identity
does; §7 killed the per-problem mechanism and left the between-model correlation standing on
four points. Adding families would add points to the same weak design. The Coder scale ladder
does something better: **Coder-7B is CLEAN (cond-art -0.008) while Coder-1.5B and Coder-3B
SINK (-0.052, -0.051)** — same family, same continued-pretraining diet, same prompt, same
harness. Any account in which copying produces cleanliness must therefore say that Coder-7B
copies harder than its smaller siblings. Family cannot do the explaining here.

CELLS (all committed; artifact selection reconstructed from the frozen targeting records):
  P11  coder1p5b / coder3b / general1p5b   at match, k=8  (h11_targeting_*.json)
  R5   coder7b                             at match, k=8  (h10_r5_targeting.json)
  C3   phi1                                at match, k=8  (h8_c3_phi_matched_set.json)
  P22  coder1p5b / general1p5b / deepseek1p3b / starcoder2_3b  at match, k=24

PREDICTIONS, committed before running:

  (R1) THE DECISIVE ONE. PULL(Coder-7B) > PULL(Coder-1.5B) and PULL(Coder-7B) > PULL(Coder-3B).
       If FALSE, then within a single family the clean rung does NOT copy harder than the
       sinking rungs, and the between-model correlation of §6 cannot be a copying-causes-
       cleanliness story at all — it would have to be a family-level coincidence across four
       points, and §6 should be reported as such permanently.
  (R2) Spearman(PULL, cond-artifact) across all non-void cells >= +0.5, i.e. harder copying
       goes with landing nearer the artifact.
  (R3) PULL is positive in every cell.

CAVEATS, stated up front. (a) k differs: 8 for the historical cells, 24 for Phase 22 — this
affects the noise on each cell's mean, not its expectation, since PULL is a within-cell
contrast. (b) Cells come from different phases, seeds and problem subsets; PULL is computed
cond-vs-iid WITHIN each cell, which is what makes them comparable at all. (c) StarCoder2's
Phase-22 cell is VOID and is reported but excluded from R2. (d) phi-1 is sub-threshold rather
than adjudicated, and is marked.
"""
import difflib
import json
import pathlib
import statistics as st
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
RUNS = REPO / "runs/modal"
ART = REPO / "artifacts"
sys.path.insert(0, str(REPO / "scripts"))
import modal_h1 as M  # noqa: E402

# committed cond-artifact values, for R2
COND_ART = {"P11 coder1p5b": -0.052, "P11 coder3b": -0.051, "P11 general1p5b": -0.019,
            "R5 coder7b": -0.008, "C3 phi1": -0.042,
            "P22 coder1p5b": -0.0377, "P22 general1p5b": -0.0240,
            "P22 deepseek1p3b": -0.0124, "P22 starcoder2_3b": -0.0322}
VOID = {"P22 starcoder2_3b"}
SUBTHRESHOLD = {"C3 phi1"}


def sim(a, b):
    return difflib.SequenceMatcher(None, a.splitlines(), b.splitlines(),
                                   autojunk=False).ratio()


def pull_from(codes_iid, codes_cond, arts):
    """arts: {qid: artifact_code}. Returns mean sims and PULL."""
    si, sc, pulls = [], [], []
    for q, art in arts.items():
        if not art or q not in codes_iid or q not in codes_cond:
            continue
        a = [sim(c, art) for c in codes_iid[q] if c]
        b = [sim(c, art) for c in codes_cond[q] if c]
        if not a or not b:
            continue
        mi, mc = st.mean(a), st.mean(b)
        si.append(mi)
        sc.append(mc)
        if mi < 1.0:
            pulls.append((mc - mi) / (1 - mi))
    return (st.mean(si), st.mean(sc), st.mean(pulls),
            st.stdev(pulls) / len(pulls) ** 0.5, len(pulls))


def split_arms(tag):
    """j8_* cells store iid rows first, then cond rows, same qid order."""
    g = json.loads((RUNS / f"{tag}.json").read_text())
    n = len(g) // 2
    return ({x["qid"]: x["codes"] for x in g[:n]},
            {x["qid"]: x["codes"] for x in g[n:]})


qids, pool = M._r3_donor_pool()
cells = {}

# ---- P11 rungs + R5: reconstruct selection from the frozen targeting records ----
for label, cand_tag, targ, sweep_cell in (
        ("P11 coder1p5b", "j8_cand_P11_coder1p5b", "h11_targeting_coder1p5b", "coder1p5b"),
        ("P11 coder3b", "j8_cand_P11_coder3b", "h11_targeting_coder3b", "coder3b"),
        ("P11 general1p5b", "j8_cand_P11_general1p5b", "h11_targeting_general1p5b", "general1p5b"),
        ("R5 coder7b", "j8_cand_R5_coder7b_truematch0", "h10_r5_targeting", None)):
    ch = json.loads((ART / f"{targ}.json").read_text())["chosen"]
    if sweep_cell:
        g = json.loads((RUNS / f"j11_sweep_cand_{sweep_cell}.json").read_text())
        r = json.loads((RUNS / f"j11_sweep_res_{sweep_cell}.json").read_text())
        powered = {x["qid"]: st.mean(c["frac"] for c in row) for x, row in zip(g, r)}
    else:
        powered, _ = M._r4_powered_map()
    sel = M._r3_select(pool, qids, powered, ch["target"], ch["hw"])
    arts = {q: c[2] for q, c in sel.items()}
    I, C = split_arms(cand_tag)
    cells[label] = pull_from(I, C, arts)

# ---- C3 phi-1: artifact set stored directly ----
ps = json.loads((ART / "h8_c3_phi_matched_set.json").read_text())
arts = {a["qid"]: a["code"] for a in ps["artifacts"]}
I, C = split_arms("j8_cand_C3_phi1_match")
cells["C3 phi1"] = pull_from(I, C, arts)

# ---- P22 cells: selection is the committed four-way set ----
SW = {}
for r in ("coder1p5b", "general1p5b", "deepseek1p3b", "starcoder2_3b"):
    g = json.loads((RUNS / f"j11_sweep_cand_{r}.json").read_text())
    res = json.loads((RUNS / f"j11_sweep_res_{r}.json").read_text())
    SW[r] = {x["qid"]: st.mean(c["frac"] for c in row) for x, row in zip(g, res)}
sel4 = {}
for q in qids:
    cands = pool.get(q) or []
    if not cands:
        continue
    pick = {}
    for r in SW:
        b = min(cands, key=lambda c: abs(c[1] - SW[r][q]))
        if abs(b[1] - SW[r][q]) > 0.10:
            pick = None
            break
        pick[r] = b
    if pick:
        sel4[q] = pick
for r in SW:
    I = {x["qid"]: x["codes"] for x in
         json.loads((RUNS / f"j22_{r}_iid_cand.json").read_text())}
    C = {x["qid"]: x["codes"] for x in
         json.loads((RUNS / f"j22_{r}_cond_cand.json").read_text())}
    cells[f"P22 {r}"] = pull_from(I, C, {q: sel4[q][r][2] for q in sel4})

print("=" * 88)
print("Phase 22 P2 — string-space PULL across eight committed cells (exploratory, $0)")
print("=" * 88)
print(f"{'cell':<22} {'sim_iid':>8} {'sim_cond':>9} {'PULL':>17} {'n':>4} {'cond-art':>9}")
for k, (mi, mc, p, se, n) in cells.items():
    note = "  [VOID]" if k in VOID else ("  [sub-threshold]" if k in SUBTHRESHOLD else "")
    print(f"{k:<22} {mi:>8.4f} {mc:>9.4f} {p:>+10.4f} ± {se:.4f} {n:>4} "
          f"{COND_ART[k]:>+9.4f}{note}")

lad = {k: cells[k][2] for k in ("P11 coder1p5b", "P11 coder3b", "R5 coder7b")}
r1 = lad["R5 coder7b"] > lad["P11 coder1p5b"] and lad["R5 coder7b"] > lad["P11 coder3b"]
print("\n" + "-" * 88)
print("R1 — THE DECISIVE TEST (inside one family; only the 7B rung is clean)")
print(f"  Coder-1.5B (SINKS) PULL {lad['P11 coder1p5b']:+.4f}")
print(f"  Coder-3B   (SINKS) PULL {lad['P11 coder3b']:+.4f}")
print(f"  Coder-7B   (CLEAN) PULL {lad['R5 coder7b']:+.4f}")
print(f"  R1 (7B copies hardest): {r1}")


def spearman(x, y):
    def rank(v):
        s = sorted(range(len(v)), key=lambda i: v[i])
        rr = [0] * len(v)
        for i, j in enumerate(s):
            rr[j] = i + 1
        return rr
    rx, ry = rank(x), rank(y)
    n = len(x)
    return 1 - 6 * sum((a - b) ** 2 for a, b in zip(rx, ry)) / (n * (n * n - 1))


live = [k for k in cells if k not in VOID]
rho = spearman([cells[k][2] for k in live], [COND_ART[k] for k in live])
r3 = all(cells[k][2] > 0 for k in cells)
print(f"\nR2 Spearman(PULL, cond-artifact) over {len(live)} live cells = {rho:+.3f} "
      f"(predicted >= +0.5)")
print(f"R3 PULL positive in every cell: {r3}")
print(f"\nVERDICT on the copying account: "
      f"{'SURVIVES R1' if r1 else 'R1 FAILS — copying does not explain cleanliness'}")

(ART / "h22_p2_pullladder.json").write_text(json.dumps(
    {"_label": "Phase 22 P2 — PULL across eight committed cells (exploratory) [PHASE_22.md] §8",
     "_exploratory": True,
     "predictions": {"R1_coder7b_pulls_hardest_in_family": True,
                     "R2_spearman_pull_vs_cond_art_at_least": 0.5,
                     "R3_all_pull_positive": True},
     "cells": {k: {"sim_iid": round(v[0], 4), "sim_cond": round(v[1], 4),
                   "pull": round(v[2], 4), "pull_se": round(v[3], 4), "n": v[4],
                   "cond_artifact": COND_ART[k], "void": k in VOID,
                   "sub_threshold": k in SUBTHRESHOLD}
               for k, v in cells.items()},
     "R1_ladder": {k: round(v, 4) for k, v in lad.items()}, "R1_pass": bool(r1),
     "R2_spearman": round(rho, 3), "R3_pass": bool(r3)}, indent=2))
print("\nwrote artifacts/h22_p2_pullladder.json")
