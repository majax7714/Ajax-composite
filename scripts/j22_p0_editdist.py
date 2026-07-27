"""Phase 22 P0 (free, $0) — does conditioning pull output toward the artifact IN STRING SPACE?

EXPLORATORY per §10: it moves no claim. Committed BEFORE being run, with its predictions
below, because an exploratory check with a stated prediction is worth more than one without.

THE HYPOTHESIS ([PHASE_22.md] §5.6). Phase 22's verifier found that two independent seeds
agree on the exact candidate string 0.15% of the time unconditioned and up to 29% of the
time once an artifact is in the prompt — and that DeepSeek, the model that looks "clean" on
pass-rate, shows BOTH the highest copy-identity (29.0%) and the smallest distance below the
artifact null (cond-art -0.0124). That fits an account in which DeepSeek does not RESIST the
artifact but COPIES it more completely, converging to the artifact's score rather than
degrading past it. If true, "DeepSeek is clean" means more captured by conditioning, not less.

WHAT IS MEASURED. Per problem, per model: line-level similarity (difflib ratio) between each
candidate and that model's own selected artifact, for both arms. The i.i.d. arm is the
baseline — what the model writes for this problem WITHOUT having seen the artifact. Then

    PULL = (sim_cond - sim_iid) / (1 - sim_iid)

the fraction of the available string distance that conditioning closes. This is the
compression law's b, in string space instead of pass-rate space. It is free: all eight arms
and the selection are already committed.

TWO COMPETING PREDICTIONS, AND THEY DISAGREE — which is what makes this a test.

  (P1) copy-identity ordering  : deepseek > starcoder2 > general > coder
  (P2) compression-slope order : starcoder2 (0.881) > deepseek (0.784) > coder (0.637)
                                 > general (0.619)

They agree that the two non-Qwen models pull harder than the two Qwen models, and disagree
on which is top. If PULL reproduces either ordering, string space and pass-rate space are
measuring one phenomenon. If it reproduces NEITHER, §5.6's account is wrong and the
copy-identity result is about output entropy only, not about anchoring strength.

  (P3) Every model's PULL is > 0 and the two non-Qwen models exceed the two Qwen models.
  (P4) Spearman correlation between PULL and committed b >= +0.5.

CAVEAT, stated up front: StarCoder2's cell is VOID for adjudication (parse 0.9167, gap
5.51pp) and its i.i.d. arm carries 13 empty and 36 wandered-off generations. Its PULL
baseline is therefore contaminated in the direction of LOWER sim_iid, which INFLATES its
PULL. It is reported and marked, never used to rank against the others without that note.
"""
import difflib
import json
import pathlib
import statistics as st
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
RUNS = REPO / "runs/modal"
sys.path.insert(0, str(REPO / "scripts"))
import modal_h1 as M  # noqa: E402

RUNGS = ("coder1p5b", "general1p5b", "deepseek1p3b", "starcoder2_3b")
TOL = 0.10
SLOPE = {"coder1p5b": 0.6366, "general1p5b": 0.6187,
         "deepseek1p3b": 0.7844, "starcoder2_3b": 0.8814}   # committed battery fits
IDENT = {"coder1p5b": 0.0327, "general1p5b": 0.0640,
         "deepseek1p3b": 0.2902, "starcoder2_3b": 0.1376}   # Phase 22 verifier
VOID = {"starcoder2_3b"}


def sweep(r):
    g = json.loads((RUNS / f"j11_sweep_cand_{r}.json").read_text())
    res = json.loads((RUNS / f"j11_sweep_res_{r}.json").read_text())
    return {x["qid"]: st.mean(c["frac"] for c in row) for x, row in zip(g, res)}


def codes(r, kind):
    g = json.loads((RUNS / f"j22_{r}_{kind}_cand.json").read_text())
    return {x["qid"]: x["codes"] for x in g}


def sim(a, b):
    """Line-level similarity, code-appropriate and fast."""
    return difflib.SequenceMatcher(None, a.splitlines(), b.splitlines(),
                                   autojunk=False).ratio()


qids, pool = M._r3_donor_pool()
SW = {r: sweep(r) for r in RUNGS}
sel = {}
for q in qids:
    cands = pool.get(q) or []
    if not cands:
        continue
    pick = {}
    for r in RUNGS:
        b = min(cands, key=lambda c: abs(c[1] - SW[r][q]))
        if abs(b[1] - SW[r][q]) > TOL:
            pick = None
            break
        pick[r] = b
    if pick:
        sel[q] = pick
QS = sorted(sel)

print("=" * 84)
print("Phase 22 P0 — anchoring in STRING space (exploratory, $0)")
print("=" * 84)
print(f"n = {len(QS)} problems, k = 24, Phase 22 arms (seed 401)\n")

rows = {}
for r in RUNGS:
    I, C = codes(r, "iid"), codes(r, "cond")
    si, sc, pulls = [], [], []
    for q in QS:
        art = sel[q][r][2]
        if not art:
            continue
        a = [sim(c, art) for c in I.get(q, []) if c]
        b = [sim(c, art) for c in C.get(q, []) if c]
        if not a or not b:
            continue
        mi, mc = st.mean(a), st.mean(b)
        si.append(mi)
        sc.append(mc)
        if mi < 1.0:
            pulls.append((mc - mi) / (1 - mi))
    rows[r] = {"sim_iid": st.mean(si), "sim_cond": st.mean(sc),
               "pull": st.mean(pulls), "n": len(pulls),
               "pull_se": st.stdev(pulls) / (len(pulls) ** 0.5)}
    m = rows[r]
    print(f"{r:<15} sim_iid {m['sim_iid']:.4f}  sim_cond {m['sim_cond']:.4f}  "
          f"PULL {m['pull']:+.4f} ± {m['pull_se']:.4f}  (n={m['n']})"
          f"{'   [CELL VOID — baseline contaminated, PULL inflated]' if r in VOID else ''}")

order = sorted(RUNGS, key=lambda r: -rows[r]["pull"])
print(f"\nPULL ordering (highest first): {' > '.join(order)}")
print(f"  P1 copy-identity   : deepseek1p3b > starcoder2_3b > general1p5b > coder1p5b")
print(f"  P2 compression b   : starcoder2_3b > deepseek1p3b > coder1p5b > general1p5b")


def spearman(x, y):
    def rank(v):
        s = sorted(range(len(v)), key=lambda i: v[i])
        rr = [0] * len(v)
        for i, j in enumerate(s):
            rr[j] = i + 1
        return rr
    rx, ry = rank(x), rank(y)
    n = len(x)
    d2 = sum((a - b) ** 2 for a, b in zip(rx, ry))
    return 1 - 6 * d2 / (n * (n * n - 1))


P = [rows[r]["pull"] for r in RUNGS]
print(f"\nSpearman(PULL, committed b)        = {spearman(P, [SLOPE[r] for r in RUNGS]):+.3f}"
      f"   (P4 predicted ≥ +0.5)")
print(f"Spearman(PULL, copy-identity)      = {spearman(P, [IDENT[r] for r in RUNGS]):+.3f}")

qwen = [rows[r]["pull"] for r in ("coder1p5b", "general1p5b")]
nonq = [rows[r]["pull"] for r in ("deepseek1p3b", "starcoder2_3b")]
print(f"\nP3: all PULL > 0 : {all(p > 0 for p in P)}   "
      f"non-Qwen > Qwen : {min(nonq) > max(qwen)}   "
      f"(Qwen {max(qwen):.4f} vs non-Qwen {min(nonq):.4f})")
print(f"\nDeepSeek vs Coder-1.5B pull difference: "
      f"{rows['deepseek1p3b']['pull'] - rows['coder1p5b']['pull']:+.4f}")

(REPO / "artifacts/h22_p0_editdist.json").write_text(json.dumps(
    {"_label": "Phase 22 P0 — anchoring in string space (exploratory) [PHASE_22.md] §6",
     "_exploratory": True, "n": len(QS), "source_arms": "j22_* (seed 401)",
     "metric": "line-level difflib ratio to own selected artifact; "
               "PULL = (sim_cond - sim_iid) / (1 - sim_iid)",
     "predictions": {"P1_copy_identity_order":
                     ["deepseek1p3b", "starcoder2_3b", "general1p5b", "coder1p5b"],
                     "P2_compression_b_order":
                     ["starcoder2_3b", "deepseek1p3b", "coder1p5b", "general1p5b"],
                     "P3_all_positive_and_nonqwen_above_qwen": True,
                     "P4_spearman_pull_vs_b_at_least": 0.5},
     "cells": rows, "pull_order": order,
     "spearman_pull_vs_b": spearman(P, [SLOPE[r] for r in RUNGS]),
     "spearman_pull_vs_identity": spearman(P, [IDENT[r] for r in RUNGS]),
     "void_cells": sorted(VOID)}, indent=2))
print("\nwrote artifacts/h22_p0_editdist.json")
