"""P0.7 (free) — is coverage loss DOWNSTREAM of compression, or its own channel?

P0.5 established, across all eight committed matched cells, that conditioning pulls a
model 47-90% of the way from its own quality toward the artifact's — sinking models and
clean ones alike — and that coverage falls in every cell but one. Two questions remain,
and both are answerable without spending.

(a) THE 7B ZERO. Section 0.4 quotes "Coder-7B at true match loses exactly 0.000" as the
    sharp end of a scale separation. Exactly zero is a suspicious number. It is a
    difference of COUNTS: if conditioning loses three problems and gains three others,
    the count is unchanged and the effect is not. Checking which problems are solved,
    not how many, settles it in one line.

(b) WHAT KIND OF DAMAGE IS IT. The compression law is a statement about per-problem
    MEANS and says nothing about spread. Two spread hypotheses make very different
    coverage predictions from the same measured law:

      S1 LOCATION   the whole candidate distribution slides by (a + b*gap), spread intact.
                    Coverage falls only as far as the slide carries the top below 1.0.
      S2 SHRINKAGE  candidates contract toward the artifact by the same factor b.
                    Coverage collapses, because pass@k lives on the top of the
                    distribution and shrinkage attacks exactly that.

    Both are simulated here from each cell's own committed i.i.d. candidates and its own
    fitted (a, b), then scored against that cell's OBSERVED conditioned coverage. If S2
    predicts and S1 does not, coverage loss is derived — a consequence of compression,
    not an independent channel, and the "coverage channel" successor closes as answered
    rather than as open.

*** RESULT, AND A DEFECT IN THIS SCRIPT'S OWN DESIGN (recorded, not deleted) ***

S2 AS SPECIFIED IS ILL-POSED AND ITS 0/8 IS NOT EVIDENCE. It maps every candidate to
art(q) + (1-b)*(f - mean_iid(q)) + a. Since no artifact in any of the eight cells fully
passes (P0.5: 0 of 44/39/29/39/28/39/20/43) and the deviation term is small, NO simulated
candidate can ever reach frac = 1.0 — so S2 predicts coverage exactly 0.0000 in every
cell by construction, for any input. That is the same defect class as Phase 14's
identically-zero adjudication statistic (§8 entry 8): a decision rule that cannot vary
with the data. It is left in the script and the artifact, labelled, because deleting a
degenerate arm is how the record would stop being able to see this pattern recurring —
this is its third instance.

S1 is a genuine prediction and it FAILS: mean absolute error 0.2418, and it fails in a
consistent direction — it UNDER-predicts coverage in 7 of 8 cells, badly at Coder-7B
(predicts 0.241, observes 0.793). Reading: conditioning is not a uniform downward slide
of the candidate distribution. Real candidates escape the pull; the location model has
no way to represent that, which is precisely the escape-distance law's subject matter.

What DOES survive from this script is part (a), which is a clean measurement.

Free: reads committed pools, spends nothing.
"""
import json
import math
import pathlib
import random
import statistics as st
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
RUNS = REPO / "runs/modal"
SEED = 271
REPS = 300

sys.path.insert(0, str(REPO / "scripts"))
import modal_h1 as M  # noqa: E402


def load(tag):
    return json.loads((RUNS / f"{tag}.json").read_text())


def arms(ctag, rtag):
    c, r = load(ctag), load(rtag)
    n = len(c) // 2
    return ({x["qid"]: [y["frac"] for y in row] for x, row in zip(c[:n], r[:n])},
            {x["qid"]: [y["frac"] for y in row] for x, row in zip(c[n:], r[n:])})


def cov(fr_by_q, qs, k):
    def pk(f):
        n = len(f)
        c = sum(1 for v in f if v >= 1.0)
        return 1.0 if n - c < k else 1.0 - math.comb(n - c, k) / math.comb(n, k)
    return st.mean(pk(fr_by_q[q]) for q in qs)


def ols(x, y):
    mx, my = st.mean(x), st.mean(y)
    sxx = sum((xi - mx) ** 2 for xi in x)
    b = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / sxx
    return my - b * mx, b


def sweep_powered(rung):
    g, r = load(f"j11_sweep_cand_{rung}"), load(f"j11_sweep_res_{rung}")
    return {x["qid"]: st.mean(c["frac"] for c in row) for x, row in zip(g, r)}


def reconstruct(tfile, powered):
    ch = json.loads((REPO / tfile).read_text())["chosen"]
    qids, pool = M._r3_donor_pool()
    sel = M._r3_select(pool, qids, powered, ch["target"], ch["hw"])
    a = {q: c[1] for q, c in sel.items()}
    assert round(st.mean(a.values()), 4) == ch["mean_art"]
    return a


m7 = json.loads((REPO / "artifacts/h7_matched_artifacts.json").read_text())
CELLS = []
for rung, tag, tf, lab in (("coder1p5b", "P11_coder1p5b", "artifacts/h11_targeting_coder1p5b.json", "Coder-1.5B (P11)"),
                           ("coder3b", "P11_coder3b", "artifacts/h11_targeting_coder3b.json", "Coder-3B (P11)")):
    CELLS.append((lab, "SINKS", *arms(f"j8_cand_{tag}", f"j8_res_{tag}"),
                  reconstruct(tf, sweep_powered(rung))))
CELLS.append(("Coder-7B (R5 true match)", "clean",
              *arms("j8_cand_R5_coder7b_truematch0", "j8_res_R5_coder7b_truematch0"),
              reconstruct("artifacts/h10_r5_targeting.json", M._r4_powered_map()[0])))
for key, lab, status in (("M1_deepseek1p3b", "DeepSeek-1.3B (P7 M1)", "clean"),
                         ("M2_general1p5b", "general-Qwen-1.5B (TWIN)", "clean"),
                         ("M3_starcoder2_3b", "StarCoder2-3B (P7 M3)", "clean"),
                         ("M4_coder7b", "Coder-7B (P7 M4, retr.)", "clean"),
                         ("M5_coder0p5b", "Coder-0.5B (P7 M5)", "unadj.")):
    CELLS.append((lab, status, *arms(f"j7_cand_{key}", f"j7_res_{key}"),
                  {x["qid"]: x["frac"] for x in m7["cells"][key]["artifacts"]}))

rng = random.Random(SEED)
print("=" * 92)
print("P0.7 — is coverage loss downstream of compression?  [PHASE_18.md P0]")
print("=" * 92)

# ------------------------------------------------------------------ (a) the 7B zero
print("\n" + "-" * 92)
print("(a) the 7B 'exactly 0.000': same COUNT, or the same PROBLEMS?")
print("-" * 92)
seven = {}
for name, status, iid, cnd, art in CELLS:
    qs = sorted(set(iid) & set(cnd) & set(art))
    k = min(len(iid[qs[0]]), len(cnd[qs[0]]))
    si = {q for q in qs if any(f >= 1.0 for f in iid[q])}
    sc = {q for q in qs if any(f >= 1.0 for f in cnd[q])}
    churn = len(si ^ sc)
    seven[name] = {"n": len(qs), "solved_iid": len(si), "solved_cond": len(sc),
                   "lost": len(si - sc), "gained": len(sc - si), "churn": churn,
                   "net": len(sc) - len(si)}
    print(f"  {name:<26} n={len(qs):>3}  solved iid {len(si):>3} -> cond {len(sc):>3}"
          f"   NET {len(sc) - len(si):>+3}   lost {len(si - sc):>2} gained "
          f"{len(sc - si):>2}   churn {churn:>2}")
print("\n  'net' is what the record has been quoting. 'churn' is how much actually moved.")

# ------------------------------------------------- (b) location vs shrinkage
print("\n" + "-" * 92)
print("(b) simulating conditioned coverage from each cell's own compression law")
print("-" * 92)
print(f"  {'cell':<26} {'k':>2} {'observed':>9} {'S1 loc':>8} {'S2 shrink':>10} "
      f"{'iid':>7}  {'winner':>9}")
out = {}
for name, status, iid, cnd, art in CELLS:
    qs = sorted(set(iid) & set(cnd) & set(art))
    k = min(min(len(iid[q]) for q in qs), min(len(cnd[q]) for q in qs))
    mi = {q: st.mean(iid[q]) for q in qs}
    a, b = ols([art[q] - mi[q] for q in qs], [st.mean(cnd[q]) - mi[q] for q in qs])
    obs = cov(cnd, qs, k)
    base = cov(iid, qs, k)

    s1, s2 = [], []
    for _ in range(REPS):
        p1, p2 = {}, {}
        for q in qs:
            shift = a + b * (art[q] - mi[q])
            p1[q] = [min(1.0, max(0.0, f + shift)) for f in iid[q]]
            p2[q] = [min(1.0, max(0.0, art[q] + (1 - b) * (f - mi[q]) + a))
                     for f in iid[q]]
        s1.append(cov(p1, qs, k))
        s2.append(cov(p2, qs, k))
        break  # both maps are deterministic given the committed pool
    m1, m2 = st.mean(s1), st.mean(s2)
    e1, e2 = abs(m1 - obs), abs(m2 - obs)
    win = "S2 shrink" if e2 < e1 else "S1 loc"
    out[name] = {"status": status, "k": k, "n": len(qs), "a": round(a, 4),
                 "b": round(b, 4), "observed": round(obs, 4), "iid": round(base, 4),
                 "S1_location": round(m1, 4), "S2_shrinkage": round(m2, 4),
                 "err_S1": round(e1, 4), "err_S2": round(e2, 4), "winner": win,
                 **seven[name]}
    print(f"  {name:<26} {k:>2} {obs:>9.4f} {m1:>8.4f} {m2:>10.4f} {base:>7.4f}  "
          f"{win:>9}")

nS2 = sum(1 for v in out.values() if v["winner"] == "S2 shrink")
mae1 = st.mean(v["err_S1"] for v in out.values())
mae2 = st.mean(v["err_S2"] for v in out.values())
under = sum(1 for v in out.values() if v["S1_location"] < v["observed"])
degenerate = len({v["S2_shrinkage"] for v in out.values()}) == 1
print(f"\n  S1 location  MAE {mae1:.4f}   under-predicts observed coverage in "
      f"{under}/{len(out)} cells")
print(f"  S2 shrinkage MAE {mae2:.4f}   all-cells-identical prediction: {degenerate}")
if degenerate:
    print("\n  *** S2 IS DEGENERATE AND ITS SCORE IS VOID. No artifact in any cell fully")
    print("  passes, so shrinkage toward the artifact can never reach frac = 1.0 and S2")
    print("  returns exactly 0.0000 for ANY input. A rule that cannot vary with the data")
    print("  is not a test — the third instance of this class in the record (§8 entry 8).")
print("\n  S1 IS a real prediction and it fails, in one direction: models RETAIN more")
print("  coverage than a uniform downward slide allows. Candidates escape the pull.")

(REPO / "artifacts/h18_p0_coverage_model.json").write_text(json.dumps(
    {"_label": "P0.7 free — coverage as a consequence of compression [PHASE_18.md P0]",
     "_S1": "f' = f + (a + b*gap)            location shift, spread preserved",
     "_S2": "f' = art + (1-b)*(f - mean_iid) + a   shrinkage toward the artifact",
     "_S2_VOID": ("S2 is DEGENERATE and its score carries no information: no artifact in "
                  "any of the 8 cells fully passes, so shrinkage toward the artifact can "
                  "never reach frac 1.0 and S2 returns exactly 0.0000 for any input. "
                  "Retained and labelled rather than deleted — same defect class as "
                  "Phase 14's identically-zero statistic (WRITEUP §8 entry 8)."),
     "seed": SEED, "cells": out,
     "summary": {"S2_wins": nS2, "S2_degenerate": bool(degenerate), "cells": len(out),
                 "mae_S1": round(mae1, 4), "mae_S2_VOID": round(mae2, 4),
                 "S1_under_predicts_in": under}}, indent=2))
print("\nwrote artifacts/h18_p0_coverage_model.json")
