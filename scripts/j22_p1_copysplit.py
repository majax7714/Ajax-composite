"""Phase 22 P1 (free, $0) — the killing test for §6's copying account.

EXPLORATORY per §10. Committed BEFORE running, with its prediction.

THE SHARPENED QUESTION. §6 found that string-space PULL orders the models exactly as
copy-identity does and correlates with the committed compression slopes. But the compression
law already separates the two quantities: in shift = a + b*gap, **b is how much the model
moves toward the artifact (copying) and a is how far it falls at zero gap (sinking)**. The
committed battery is consistent with §6's account — DeepSeek b 0.784 / a +0.011, Coder-1.5B
b 0.637 / a -0.056 — but that is four points again.

This tests it WITHIN each model, across problems, where n is 56 rather than 4 and where a
family story cannot do the work.

METHOD. Per problem: sim_cond(q) = line-level similarity of that problem's conditioned
candidates to the artifact. Split each model's problems at its own median sim_cond. Fit
shift = a + b*gap separately on each half. Compare the two intercepts.

PREDICTION, committed before running:

  (Q1) In at least 3 of 4 models, the HIGH-copy half has an intercept CLOSER TO ZERO than
       the low-copy half. If copying is what makes a model look clean, the problems where it
       copies hardest are the problems where it sinks least.
  (Q2) The high-copy half also shows the larger slope b (copying and slope are the same
       thing measured two ways).
  (Q3) A null on Q1 — intercepts equal within noise across the split — is strong evidence
       AGAINST §6's account, and would mean string similarity and pass-rate degradation are
       independent axes that merely happen to order four models alike.

WHY THIS IS NOT TAUTOLOGICAL. Copying the artifact exactly forces cond = artifact, hence
shift = gap, hence a = 0 and b = 1 — so the test would be circular if similarity were near 1.
It is not: conditioned similarity runs 0.49-0.79, so candidates are substantially rewritten,
and the intercept retains room to be non-zero at any copy level. The question is whether the
residual degradation at zero gap shrinks as copying rises, which is an empirical matter.

CAVEAT: StarCoder2's cell is VOID (parse 0.9167, gap 5.51pp); reported and marked.
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
VOID = {"starcoder2_3b"}


def sweep(r):
    g = json.loads((RUNS / f"j11_sweep_cand_{r}.json").read_text())
    res = json.loads((RUNS / f"j11_sweep_res_{r}.json").read_text())
    return {x["qid"]: st.mean(c["frac"] for c in row) for x, row in zip(g, res)}


def arm(r, kind):
    g = json.loads((RUNS / f"j22_{r}_{kind}_cand.json").read_text())
    v = json.loads((RUNS / f"j22_{r}_{kind}_res.json").read_text())
    return ({x["qid"]: x["codes"] for x in g},
            {x["qid"]: [y["frac"] for y in row] for x, row in zip(g, v)})


def sim(a, b):
    return difflib.SequenceMatcher(None, a.splitlines(), b.splitlines(),
                                   autojunk=False).ratio()


def fit(xs, ys):
    n = len(xs)
    mx, my = st.mean(xs), st.mean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return None, None, 0
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    a = my - b * mx
    ss = sum((y - my) ** 2 for y in ys)
    res = sum((y - (a + b * x)) ** 2 for x, y in zip(xs, ys))
    return a, b, (1 - res / ss if ss else 0)


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
print("Phase 22 P1 — does copying explain cleanliness WITHIN a model? (exploratory, $0)")
print("=" * 84)

out = {}
for r in RUNGS:
    (Ic, If), (Cc, Cf) = arm(r, "iid"), arm(r, "cond")
    recs = []
    for q in QS:
        art_code, art_frac = sel[q][r][2], sel[q][r][1]
        if not art_code or q not in Cf or q not in If:
            continue
        s = [sim(c, art_code) for c in Cc.get(q, []) if c]
        if not s:
            continue
        iid, cond = st.mean(If[q]), st.mean(Cf[q])
        recs.append({"q": q, "sim": st.mean(s),
                     "shift": cond - iid, "gap": art_frac - iid})
    med = st.median(x["sim"] for x in recs)
    hi = [x for x in recs if x["sim"] >= med]
    lo = [x for x in recs if x["sim"] < med]
    a_h, b_h, r2h = fit([x["gap"] for x in hi], [x["shift"] for x in hi])
    a_l, b_l, r2l = fit([x["gap"] for x in lo], [x["shift"] for x in lo])
    closer = abs(a_h) < abs(a_l)
    out[r] = {"median_sim": round(med, 4), "n_high": len(hi), "n_low": len(lo),
              "intercept_high": round(a_h, 4), "intercept_low": round(a_l, 4),
              "slope_high": round(b_h, 4), "slope_low": round(b_l, 4),
              "r2_high": round(r2h, 3), "r2_low": round(r2l, 3),
              "high_intercept_closer_to_zero": bool(closer),
              "high_slope_larger": bool(b_h > b_l), "void": r in VOID}
    print(f"\n{r}{'  [CELL VOID]' if r in VOID else ''}   median sim {med:.4f}")
    print(f"  HIGH-copy (n={len(hi)}):  intercept {a_h:+.4f}  slope {b_h:+.4f}  R² {r2h:.3f}")
    print(f"  LOW-copy  (n={len(lo)}):  intercept {a_l:+.4f}  slope {b_l:+.4f}  R² {r2l:.3f}")
    print(f"  → high-copy intercept closer to zero: {closer}   "
          f"high-copy slope larger: {b_h > b_l}")

live = [r for r in RUNGS if r not in VOID]
q1_all = sum(out[r]["high_intercept_closer_to_zero"] for r in RUNGS)
q1_live = sum(out[r]["high_intercept_closer_to_zero"] for r in live)
q2_all = sum(out[r]["high_slope_larger"] for r in RUNGS)
print("\n" + "=" * 84)
print(f"Q1 (predicted >=3 of 4): high-copy intercept closer to zero in "
      f"{q1_all}/4 models  [{q1_live}/3 excluding the void cell]")
print(f"Q2 (predicted): high-copy slope larger in {q2_all}/4 models")
print(f"VERDICT: {'SUPPORTS §6' if q1_all >= 3 else 'DOES NOT SUPPORT §6 — Q3 fires'}")

(REPO / "artifacts/h22_p1_copysplit.json").write_text(json.dumps(
    {"_label": "Phase 22 P1 — within-model copy split (exploratory) [PHASE_22.md] §7",
     "_exploratory": True, "n_problems": len(QS),
     "predictions": {"Q1_high_copy_intercept_closer_to_zero_in_at_least": 3,
                     "Q2_high_copy_slope_larger": True},
     "cells": out, "q1_hits": q1_all, "q1_hits_excluding_void": q1_live,
     "q2_hits": q2_all,
     "verdict": "supports" if q1_all >= 3 else "does not support"}, indent=2))
print("\nwrote artifacts/h22_p1_copysplit.json")
