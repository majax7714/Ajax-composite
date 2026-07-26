"""Independent re-derivation of Phase 21's four cells, gates and branch.

Written and committed while the arms were still generating, BEFORE any Phase-21 result
existed and without inspecting a single arm number, so it cannot be shaped by the answer.
It rebuilds the selection, the arms, the per-cell statistics, every gate and the branch
tree from the raw pools WITHOUT importing j21_fourway's analysis block, then cross-checks
against artifacts/h21_fourway.json.

Why this exists: §8 entry 11 records Phase 18 shipping an artifact whose every *quantity*
was right and whose *branch logic* was independently wrong — the branch expression never
consulted the kill criteria it printed. A verifier that only re-adds the numbers would have
passed that artifact. So this one re-derives the branch as well.

Independence is partial, and the limit is stated rather than glossed: this shares the raw
generation pools, the donor pool, and the _r3_donor_pool/_d2c_context definitions with the
entrypoint. What it does NOT share is the selection loop, the arm assembly, the per-problem
effect construction, the bootstrap (different RNG, different seed, plus a second CI by
normal approximation as a cross-method check), the gate evaluation, or the branch tree.

TWO CHECKS THE ENTRYPOINT DOES NOT MAKE:

1. Artifact distinctness, pairwise across all four models. The design rests on per-model
   artifact selection. If a bug handed every model the same artifact, the cell would
   silently collapse into the shared-artifact design Phase 7 was built to escape, and every
   downstream number would still look entirely plausible.

2. The uninformative-null guard, applied SYMMETRICALLY. The entrypoint prints its guard for
   StarCoder2 only. But branches B and C both hinge on DeepSeek being "clean," and a clean
   verdict is a null like any other: under the charter's own power statement (MDE 0.039), a
   null whose CI on cond−iid is wide enough to contain effects past the MDE is not evidence
   of absence. This applies that test to every non-sinking model. It cannot and does not
   change the frozen branch — the entrypoint's adjudication stands as pre-registered — but a
   branch that survives here only because a null went unchallenged must be reported that way.
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

TOL = 0.10          # per-problem |artifact - own iid|, charter §2
ON_TARGET = 0.020   # aggregate Δ_art band, charter §2 kill criterion
MIN_N = 30          # charter §2 UNDERPOWERED criterion
MDE = 0.039         # charter §2 power statement
RUNGS = ("coder1p5b", "general1p5b", "deepseek1p3b", "starcoder2_3b")
INTERCEPT = {"coder1p5b": -0.056, "general1p5b": -0.040,
             "deepseek1p3b": +0.011, "starcoder2_3b": -0.021}


def sweep(r):
    g = json.loads((RUNS / f"j11_sweep_cand_{r}.json").read_text())
    res = json.loads((RUNS / f"j11_sweep_res_{r}.json").read_text())
    return {x["qid"]: st.mean(c["frac"] for c in row) for x, row in zip(g, res)}


def arm(r, kind):
    c, v = RUNS / f"j21_{r}_{kind}_cand.json", RUNS / f"j21_{r}_{kind}_res.json"
    if not (c.exists() and v.exists()):
        return None, None
    cc, rr = json.loads(c.read_text()), json.loads(v.read_text())
    fr = {x["qid"]: [y["frac"] for y in row] for x, row in zip(cc, rr)}
    ok = tot = 0
    for x in cc:
        for code in x["codes"]:
            tot += 1
            if code:
                try:
                    ast.parse(code)
                    ok += 1
                except SyntaxError:
                    pass
    return fr, (ok / tot if tot else 0.0)


# ---- rebuild the selection independently of _p21_select ----------------------
qids, pool = M._r3_donor_pool()
SW = {r: sweep(r) for r in RUNGS}


def select(rungs):
    out = {}
    for q in qids:
        cands = pool.get(q) or []
        if not cands:
            continue
        pick = {}
        for r in rungs:
            b = min(cands, key=lambda c: abs(c[1] - SW[r][q]))
            if abs(b[1] - SW[r][q]) > TOL:
                pick = None
                break
            pick[r] = b
        if pick:
            out[q] = pick
    return out


print("=" * 84)
print("independent re-derivation of Phase 21")
print("=" * 84)

sel = select(RUNGS)
rungs = list(RUNGS)
mode = "four-way"
if len(sel) < MIN_N:
    print(f"four-way n={len(sel)} < {MIN_N} — pre-registered fallback path")
    rungs = ["coder1p5b", "deepseek1p3b"]
    sel = select(rungs)
    mode = "pairwise-fallback"
QS = sorted(sel)
print(f"selection rebuilt: mode={mode}  n={len(QS)}  rungs={rungs}")

# ---- design-integrity check 1: are the artifacts actually different? ---------
print("\nartifact distinctness (per-model selection must not collapse):")
collapsed = []
for i, a in enumerate(rungs):
    for b in rungs[i + 1:]:
        d = sum(1 for q in QS if sel[q][a][0] != sel[q][b][0])
        flag = "  *** COLLAPSED ***" if d == 0 else ""
        if d == 0:
            collapsed.append((a, b))
        print(f"  {a:<15} vs {b:<15} different on {d:>3}/{len(QS)}{flag}")
if collapsed:
    print("  *** FATAL: per-model artifact selection collapsed to a shared artifact ***")

for r in rungs:
    d = st.mean(sel[q][r][1] - SW[r][q] for q in QS)
    print(f"  {r:<15} aggregate Δ_art {d:+.4f}   within ±{ON_TARGET}: {abs(d) <= ON_TARGET}")

arms, parse = {}, {}
for r in rungs:
    for k in ("iid", "cond"):
        arms[(r, k)], parse[(r, k)] = arm(r, k)
missing = [f"{r}_{k}" for (r, k), v in arms.items() if v is None]
if missing:
    print(f"\narms not yet landed: {', '.join(missing)} — rerun after completion")
    sys.exit(0)

qs = sorted(set(QS) & set.intersection(*(set(v) for v in arms.values())))
n = len(qs)
rng = random.Random(991)          # deliberately NOT the entrypoint's 373


def boot(v, b=8000):
    a = sorted(st.mean([v[rng.randrange(len(v))] for _ in v]) for _ in range(b))
    return a[int(.025 * b)], a[int(.975 * b)]


def normal(v):
    m, s = st.mean(v), st.stdev(v) / math.sqrt(len(v))
    return m - 1.96 * s, m + 1.96 * s


cells, eff = {}, {}
print(f"\nn = {n}")
print(f"{'model':<15} {'cond-iid':>9} {'CI95 (boot)':>20} {'CI95 (normal)':>20} "
      f"{'cond-art':>9} {'SINK':>6} {'pred hit':>9}")
for r in rungs:
    I, C = arms[(r, "iid")], arms[(r, "cond")]
    de = [st.mean(C[q]) - st.mean(I[q]) for q in qs]
    da = [st.mean(C[q]) - sel[q][r][1] for q in qs]
    l1, h1 = boot(de)
    nl, nh = normal(de)
    l2, h2 = boot(da)
    sink = bool(h1 < 0 and h2 < 0)
    eff[r] = de
    cells[r] = {"cond_minus_iid": st.mean(de), "ci_iid": (l1, h1),
                "cond_minus_artifact": st.mean(da), "ci_art": (l2, h2),
                "below_both_nulls": sink,
                "prediction_hit": bool(l1 <= INTERCEPT[r] <= h1)}
    if abs(l1 - nl) > 0.005 or abs(h1 - nh) > 0.005:
        print(f"  ! {r}: bootstrap and normal CIs disagree by >0.005 — check the tail")
    print(f"{r:<15} {st.mean(de):>+9.4f} [{l1:+.4f},{h1:+.4f}] [{nl:+.4f},{nh:+.4f}] "
          f"{st.mean(da):>+9.4f} {str(sink):>6} {str(cells[r]['prediction_hit']):>9}")

# ---- gates, re-evaluated independently --------------------------------------
on_target = all(abs(st.mean(sel[q][r][1] - SW[r][q] for q in QS)) <= ON_TARGET
                for r in rungs)
parse_ok = all(v >= 0.95 for v in parse.values())
powered = n >= MIN_N
print(f"\n[gates] on_target {on_target}  parse_ok {parse_ok}  n>={MIN_N} {powered}")
for (r, k), v in sorted(parse.items()):
    if v < 0.95:
        print(f"  ! parse {r}_{k} = {v:.4f} < 0.95")

# ---- design-integrity check 2: the null guard, applied to EVERY clean model --
print("\nuninformative-null audit (charter MDE 0.039; a null is not evidence of absence)")
uninformative = []
for r in rungs:
    if cells[r]["below_both_nulls"]:
        continue
    lo, hi = cells[r]["ci_iid"]
    if lo < -MDE:
        uninformative.append(r)
        print(f"  {r:<15} NOT clean — CI [{lo:+.4f},{hi:+.4f}] reaches past −{MDE}; "
              f"predicted {INTERCEPT[r]:+.3f}. This null is UNINFORMATIVE.")
    else:
        print(f"  {r:<15} null is informative — CI [{lo:+.4f},{hi:+.4f}] "
              f"excludes effects past −{MDE}")
if "starcoder2_3b" not in uninformative and "deepseek1p3b" in uninformative:
    print("  NOTE: the entrypoint prints its guard for StarCoder2 only. Here it is "
          "DeepSeek whose null is unsupported, and branches B and C both rest on it.")

# ---- the branch tree, re-derived (§8 entry 11: quantities can agree while
#      the branch logic is independently wrong) --------------------------------
ds = cells.get("deepseek1p3b", {}).get("below_both_nulls")
sc = cells.get("starcoder2_3b", {}).get("below_both_nulls")
if not (on_target and parse_ok and powered):
    mine = "D"
elif ds and sc:
    mine = "A"
elif ds is False and sc is False:
    mine = "B"
elif ds is False and sc:
    mine = "C"
else:
    mine = "UNCLASSIFIED"
print(f"\nindependent branch: {mine}")

art = REPO / "artifacts/h21_fourway.json"
if not art.exists():
    print("\n(result artifact not written yet — rerun after the phase completes)")
    sys.exit(0)

a = json.loads(art.read_text())
print("\n" + "-" * 84)
print("cross-check vs artifacts/h21_fourway.json")
print("-" * 84)
bad = 0
for r in rungs:
    e = a["cells"][r]
    for key, mine_v in (("cond_minus_iid", cells[r]["cond_minus_iid"]),
                        ("cond_minus_artifact", cells[r]["cond_minus_artifact"])):
        if abs(e[key] - mine_v) >= 5e-4:
            bad += 1
            print(f"  MISMATCH {r}.{key}: entrypoint {e[key]:+.4f} vs mine {mine_v:+.4f}")
    if e["below_both_nulls"] != cells[r]["below_both_nulls"]:
        bad += 1
        print(f"  MISMATCH {r}.below_both_nulls: entrypoint {e['below_both_nulls']} "
              f"vs mine {cells[r]['below_both_nulls']}")
if a["n"] != n:
    bad += 1
    print(f"  MISMATCH n: entrypoint {a['n']} vs mine {n}")
if a["mode"] != mode:
    bad += 1
    print(f"  MISMATCH mode: entrypoint {a['mode']} vs mine {mode}")
if not a["branch"].startswith(mine):
    bad += 1
    print(f"  MISMATCH branch: entrypoint {a['branch'][:40]!r} vs mine {mine}")
print(f"  {'ALL QUANTITIES AND THE BRANCH AGREE' if not bad else 'MISMATCHES — DO NOT ADJUDICATE'}")
print(f"  entrypoint branch: {a['branch']}")
if uninformative:
    print(f"  CAVEAT: null(s) unsupported at the pre-registered MDE: "
          f"{', '.join(uninformative)} — the branch must be reported with this attached.")
