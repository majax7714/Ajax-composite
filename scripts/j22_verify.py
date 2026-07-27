"""Independent re-derivation of Phase 22's cells, per-cell gates and branch.

Written and committed while the arms were still generating, BEFORE any Phase-22 result
existed and without inspecting a single arm number. It rebuilds the selection, the arms,
the per-cell statistics, every gate and the branch tree from the raw pools WITHOUT
importing j22_fourway's analysis block, then cross-checks artifacts/h22_fourway.json.

Independence is partial and the limit is stated rather than glossed: this shares the raw
generation pools, the donor pool, and the _r3_donor_pool/_d2c_context definitions with the
entrypoint. What it does NOT share is the selection loop, the arm assembly, the per-problem
effect construction, the bootstrap (different RNG and seed, plus a normal-approximation
cross-check), the void logic, the gate evaluation, or the branch tree.

THREE CHECKS THE ENTRYPOINT DOES NOT MAKE:

1. THE FRESH-DRAW PREMISE. Phase 22's entire justification for re-running rather than
   re-scoring Phase 21 is that seed 401 gives an independent draw of the same quantity. If
   vLLM's seeding produced generations identical to Phase 21's seed 367, that premise is
   FALSE and the phase is a re-score wearing a new number. This compares the two runs'
   candidate strings per (model, arm, problem) and reports the identical-generation rate.
   Reading Phase 21's raw generations for this purpose is an instrument check on generation
   identity — it is NOT citing that killed phase's results, and nothing here feeds the
   branch.

2. ARTIFACT DISTINCTNESS, pairwise across all four models. The design rests on per-model
   artifact selection; a collapse to a shared artifact would leave every downstream number
   looking entirely plausible. (Selection is deterministic given the committed sweeps, so
   this should reproduce Phase 21's counts exactly — which is itself the check.)

3. THE UNINFORMATIVE-NULL GUARD, applied symmetrically to every non-sinking model. A clean
   verdict is a null like any other: under the charter's MDE (0.039), a null whose CI on
   cond-iid reaches past that is not evidence of absence. It cannot and does not change the
   frozen branch — it reports, so that a branch surviving on an unchallenged null says so.
"""
import ast
import json
import math
import pathlib
import random
import statistics as st
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
RUNS = REPO / "runs/modal"
sys.path.insert(0, str(REPO / "scripts"))
import modal_h1 as M  # noqa: E402

TOL = 0.10
ON_TARGET = 0.020
MIN_N = 30
MDE = 0.039
GAP = 0.020          # between-arm parse gap that voids a cell
PARSE = 0.95         # absolute per-arm parse floor
VALID = 0.040        # reference reproduction band
REF = -0.048         # committed at-match reference, Coder-1.5B
RUNGS = ("coder1p5b", "general1p5b", "deepseek1p3b", "starcoder2_3b")
PRED = {"coder1p5b": -0.048, "general1p5b": -0.037,
        "deepseek1p3b": +0.011, "starcoder2_3b": -0.036}


def sweep(r):
    g = json.loads((RUNS / f"j11_sweep_cand_{r}.json").read_text())
    res = json.loads((RUNS / f"j11_sweep_res_{r}.json").read_text())
    return {x["qid"]: st.mean(c["frac"] for c in row) for x, row in zip(g, res)}


def arm(r, kind, phase="j22"):
    c, v = RUNS / f"{phase}_{r}_{kind}_cand.json", RUNS / f"{phase}_{r}_{kind}_res.json"
    if not (c.exists() and v.exists()):
        return None
    cc, rr = json.loads(c.read_text()), json.loads(v.read_text())
    fr, fl, codes = {}, {}, {}
    ok = tot = empty = 0
    for x, row in zip(cc, rr):
        flags = []
        for code in x["codes"]:
            tot += 1
            p = False
            if code:
                try:
                    ast.parse(code)
                    p = True
                except SyntaxError:
                    pass
            else:
                empty += 1
            ok += p
            flags.append(p)
        fr[x["qid"]] = [y["frac"] for y in row]
        fl[x["qid"]] = flags
        codes[x["qid"]] = x["codes"]
    return {"frac": fr, "parse_flags": fl, "codes": codes,
            "rate": ok / tot if tot else 0.0, "empty": empty / tot if tot else 0.0,
            "meta": [m for x in cc if "meta" in x for m in x["meta"]]}


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
print("independent re-derivation of Phase 22")
print("=" * 84)
print(f"selection rebuilt: n={len(QS)}")

print("\nartifact distinctness (per-model selection must not collapse):")
for i, a in enumerate(RUNGS):
    for b in RUNGS[i + 1:]:
        d = sum(1 for q in QS if sel[q][a][0] != sel[q][b][0])
        print(f"  {a:<15} vs {b:<15} different on {d:>3}/{len(QS)}"
              f"{'  *** COLLAPSED ***' if d == 0 else ''}")
for r in RUNGS:
    d = st.mean(sel[q][r][1] - SW[r][q] for q in QS)
    print(f"  {r:<15} aggregate Δ_art {d:+.4f}   within ±{ON_TARGET}: {abs(d) <= ON_TARGET}")

arms = {(r, k): arm(r, k) for r in RUNGS for k in ("iid", "cond")}
missing = [f"{r}_{k}" for (r, k), v in arms.items() if v is None]
if missing:
    print(f"\narms not yet landed: {', '.join(missing)} — rerun after completion")
    sys.exit(0)

# ---- CHECK 1: is the draw actually fresh? -----------------------------------
print("\nfresh-draw check vs Phase 21 (seed 367 -> 401); high identity would VOID the premise")
any_prior = False
for r in RUNGS:
    for k in ("iid", "cond"):
        prior = arm(r, k, phase="j21")
        if prior is None:
            continue
        any_prior = True
        same = tot = 0
        for q in set(arms[(r, k)]["codes"]) & set(prior["codes"]):
            for a, b in zip(arms[(r, k)]["codes"][q], prior["codes"][q]):
                tot += 1
                same += (a == b)
        frac = same / tot if tot else float("nan")
        flag = "  *** PREMISE VOID — draw is not fresh ***" if frac > 0.50 else ""
        print(f"  {r:<15} {k:<5} identical generations {same}/{tot} = {frac:.4f}{flag}")
if not any_prior:
    print("  (no Phase 21 pools found to compare against)")

qs = sorted(set(QS) & set.intersection(*(set(v["frac"]) for v in arms.values())))
n = len(qs)
rng = random.Random(977)          # deliberately NOT the entrypoint's 409


def boot(v, b=8000):
    a = sorted(st.mean([v[rng.randrange(len(v))] for _ in v]) for _ in range(b))
    return a[int(.025 * b)], a[int(.975 * b)]


def normal(v):
    m, s = st.mean(v), st.stdev(v) / math.sqrt(len(v))
    return m - 1.96 * s, m + 1.96 * s


cells = {}
print(f"\nn = {n}")
print(f"{'model':<15} {'cond-iid':>9} {'CI95 (boot)':>20} {'cond-art':>9} "
      f"{'SINK':>6} {'parse i/c':>16} {'gap':>8} {'VOID':>6}")
for r in RUNGS:
    I, C = arms[(r, "iid")], arms[(r, "cond")]
    de = [st.mean(C["frac"][q]) - st.mean(I["frac"][q]) for q in qs]
    da = [st.mean(C["frac"][q]) - sel[q][r][1] for q in qs]
    l1, h1 = boot(de)
    nl, nh = normal(de)
    l2, h2 = boot(da)
    sink = bool(h1 < 0 and h2 < 0)
    gap = C["rate"] - I["rate"]
    void_parse = bool(min(I["rate"], C["rate"]) < PARSE or abs(gap) > GAP)
    dart = st.mean(sel[q][r][1] - SW[r][q] for q in QS)
    void_pos = bool(abs(dart) > ON_TARGET)
    cells[r] = {"cond_minus_iid": st.mean(de), "ci_iid": (l1, h1),
                "cond_minus_artifact": st.mean(da), "ci_art": (l2, h2),
                "below_both_nulls": sink, "void": bool(void_parse or void_pos),
                "parse_gap": gap, "prediction_hit": bool(l1 <= PRED[r] <= h1)}
    if abs(l1 - nl) > 0.005 or abs(h1 - nh) > 0.005:
        print(f"  ! {r}: bootstrap and normal CIs disagree by >0.005")
    print(f"{r:<15} {st.mean(de):>+9.4f} [{l1:+.4f},{h1:+.4f}] {st.mean(da):>+9.4f} "
          f"{str(sink):>6} {I['rate']:>7.4f}/{C['rate']:.4f} {gap:>+8.4f} "
          f"{str(cells[r]['void']):>6}")

# ---- empty-completion attribution, from emit_meta ---------------------------
print("\nempty-candidate attribution (emit_meta): raw length 0 confirms the model emitted "
      "nothing")
for r in RUNGS:
    for k in ("iid", "cond"):
        mm = arms[(r, k)]["meta"]
        if not mm:
            continue
        raw0 = sum(1 for m in mm if m["rawlen"] == 0)
        print(f"  {r:<15} {k:<5} empty codes {arms[(r,k)]['empty']:.4f}   "
              f"raw-empty {raw0}/{len(mm)} = {raw0/len(mm):.4f}"
              f"{'   (mismatch -> extraction, not the model)' if abs(raw0/len(mm) - arms[(r,k)]['empty']) > 0.002 else ''}")

# ---- gates ------------------------------------------------------------------
ref = cells["coder1p5b"]
ref_reproduces = bool(not ref["void"] and abs(ref["cond_minus_iid"] - REF) <= VALID)
powered = n >= MIN_N
live = [r for r in RUNGS if r != "coder1p5b" and not cells[r]["void"]]
print(f"\n[gates] n>={MIN_N} {powered}   reference reproduces "
      f"(|{ref['cond_minus_iid']:+.4f} − {REF}| ≤ {VALID}) {ref_reproduces}   live {live}")

print("\nuninformative-null audit (MDE 0.039; a null is not evidence of absence)")
uninformative = []
for r in RUNGS:
    if cells[r]["below_both_nulls"] or cells[r]["void"]:
        continue
    lo, hi = cells[r]["ci_iid"]
    if lo < -MDE:
        uninformative.append(r)
        print(f"  {r:<15} NOT clean — CI [{lo:+.4f},{hi:+.4f}] reaches past −{MDE}; "
              f"predicted {PRED[r]:+.3f}. UNINFORMATIVE.")
    else:
        print(f"  {r:<15} null is informative — CI [{lo:+.4f},{hi:+.4f}]")

ds = cells["deepseek1p3b"]["below_both_nulls"] if not cells["deepseek1p3b"]["void"] else None
sc = cells["starcoder2_3b"]["below_both_nulls"] if not cells["starcoder2_3b"]["void"] else None
if not powered or ref["void"] or not ref_reproduces or not live:
    mine = "D"
elif ds is not None and sc is None:
    mine = "E"
elif ds and sc:
    mine = "A"
elif ds is False and sc is False:
    mine = "B"
elif ds is False and sc:
    mine = "C"
else:
    mine = "UNCLASSIFIED"
print(f"\nindependent branch: {mine}")

art = REPO / "artifacts/h22_fourway.json"
if not art.exists():
    print("\n(result artifact not written yet — rerun after the phase completes)")
    sys.exit(0)

a = json.loads(art.read_text())
print("\n" + "-" * 84)
print("cross-check vs artifacts/h22_fourway.json")
print("-" * 84)
bad = 0
for r in RUNGS:
    e = a["cells"][r]
    for key, mine_v in (("cond_minus_iid", cells[r]["cond_minus_iid"]),
                        ("cond_minus_artifact", cells[r]["cond_minus_artifact"])):
        if abs(e[key] - mine_v) >= 5e-4:
            bad += 1
            print(f"  MISMATCH {r}.{key}: entrypoint {e[key]:+.4f} vs mine {mine_v:+.4f}")
    for key, mine_v in (("below_both_nulls", cells[r]["below_both_nulls"]),
                        ("void", cells[r]["void"])):
        if e[key] != mine_v:
            bad += 1
            print(f"  MISMATCH {r}.{key}: entrypoint {e[key]} vs mine {mine_v}")
if a["n"] != n:
    bad += 1
    print(f"  MISMATCH n: entrypoint {a['n']} vs mine {n}")
if not a["branch"].startswith(mine):
    bad += 1
    print(f"  MISMATCH branch: entrypoint {a['branch'][:40]!r} vs mine {mine}")
print(f"  {'ALL QUANTITIES AND THE BRANCH AGREE' if not bad else 'MISMATCHES — DO NOT ADJUDICATE'}")
print(f"  entrypoint branch: {a['branch']}")
if uninformative:
    print(f"  CAVEAT: null(s) unsupported at the pre-registered MDE: "
          f"{', '.join(uninformative)} — report the branch with this attached.")
