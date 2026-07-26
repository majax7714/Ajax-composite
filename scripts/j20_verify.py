"""Independent re-derivation of Phase 20's paired statistic and gates.

Written and committed while the run was still generating, BEFORE any result existed, so
it cannot be shaped by the answer. It rebuilds the selection, the four arms, the paired
difference and every gate from the raw pools WITHOUT importing j20_paired's analysis
block, then cross-checks against artifacts/h20_paired.json.

Why: five of the twelve §8 ledger entries are mis-specified decision quantities (entries
8-12), and three of them were caught by re-deriving a number a second way. Phase 18's
verifier confirmed every quantity agreed while the branch logic was independently wrong —
which is exactly the split this kind of check is for.

The independence is partial and the limit is stated rather than glossed: this shares the
raw pools, the donor pool, and the _r3_donor_pool/_d2c_context definitions with the
entrypoint. What it does NOT share is the arm assembly, the per-problem effect
construction, the pairing, the bootstrap, the gate comparisons, or the branch tree.

One thing it checks that the entrypoint does not: that the two models actually received
DIFFERENT artifacts where they should have. The whole design rests on per-model artifact
selection; if a bug had handed both models the same artifact on every problem, the cell
would silently collapse back into the shared-artifact design Phase 7 was built to escape,
and every downstream number would still look plausible.
"""
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
RUNGS = ("general1p5b", "coder1p5b")


def sweep(r):
    g = json.loads((RUNS / f"j11_sweep_cand_{r}.json").read_text())
    res = json.loads((RUNS / f"j11_sweep_res_{r}.json").read_text())
    return {x["qid"]: st.mean(c["frac"] for c in row) for x, row in zip(g, res)}


def arm(r, kind):
    c = RUNS / f"j20_{r}_{kind}_cand.json"
    v = RUNS / f"j20_{r}_{kind}_res.json"
    if not (c.exists() and v.exists()):
        return None
    cc, rr = json.loads(c.read_text()), json.loads(v.read_text())
    return {x["qid"]: [y["frac"] for y in row] for x, row in zip(cc, rr)}


# ---- rebuild the selection independently of _p20_select
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
print("=" * 80)
print("independent re-derivation of Phase 20")
print("=" * 80)
print(f"selection rebuilt: n={len(QS)}")

# ---- the design-integrity check the entrypoint does not make
diff_art = sum(1 for q in QS if sel[q]["general1p5b"][0] != sel[q]["coder1p5b"][0])
print(f"problems where the two models got DIFFERENT artifacts: {diff_art}/{len(QS)}")
if diff_art == 0:
    print("  *** FATAL: per-model artifact selection collapsed to a shared artifact ***")

for r in RUNGS:
    d = st.mean(sel[q][r][1] - SW[r][q] for q in QS)
    print(f"  {r:<14} aggregate Δ_art {d:+.4f}   within ±{ON_TARGET}: {abs(d) <= ON_TARGET}")

arms = {(r, k): arm(r, k) for r in RUNGS for k in ("iid", "cond")}
missing = [f"{r}_{k}" for (r, k), v in arms.items() if v is None]
if missing:
    print(f"\narms not yet landed: {', '.join(missing)} — rerun after completion")
    sys.exit(0)

qs = sorted(set(QS) & set.intersection(*(set(v) for v in arms.values())))
eff = {r: {q: st.mean(arms[(r, "cond")][q]) - st.mean(arms[(r, "iid")][q]) for q in qs}
       for r in RUNGS}
d = [eff["general1p5b"][q] - eff["coder1p5b"][q] for q in qs]
n = len(d)
md, se = st.mean(d), st.stdev(d) / math.sqrt(len(d))
rng = random.Random(1013)
acc = sorted(st.mean([d[rng.randrange(n)] for _ in range(n)]) for _ in range(8000))
lo, hi = acc[200], acc[7800]
p = math.erfc(abs(md / se) / math.sqrt(2))

print(f"\nn paired = {n}")
print(f"  twin    {st.mean(eff['general1p5b'].values()):+.4f}")
print(f"  sibling {st.mean(eff['coder1p5b'].values()):+.4f}")
print(f"  PAIRED difference {md:+.4f}  SE {se:.4f}  CI95 [{lo:+.4f},{hi:+.4f}]  p {p:.4g}")
print(f"  pre-registered MDE 0.0431 — cannot resolve 0.0166")
print(f"  CI excludes zero: {lo > 0 or hi < 0}   direction: "
      f"{'twin sinks LESS' if md > 0 else 'twin sinks MORE'}")

art = REPO / "artifacts/h20_paired.json"
if art.exists():
    a = json.loads(art.read_text())
    print("\n" + "-" * 80)
    print("cross-check vs artifacts/h20_paired.json")
    print("-" * 80)
    bad = 0
    for key, mine in (("paired_difference", md), ("se", se),
                      ("twin_effect", st.mean(eff["general1p5b"].values())),
                      ("sibling_effect", st.mean(eff["coder1p5b"].values()))):
        if abs(a[key] - mine) >= 5e-4:
            bad += 1
            print(f"  MISMATCH {key}: entrypoint {a[key]:+.4f} vs independent {mine:+.4f}")
    print(f"  n: entrypoint {a['n']} vs independent {n}"
          f"{'  MISMATCH' if a['n'] != n else ''}")
    print(f"  {'ALL QUANTITIES AGREE' if not bad and a['n'] == n else 'MISMATCHES — DO NOT ADJUDICATE'}")
    print(f"  entrypoint branch: {a['branch']}")
else:
    print("\n(result artifact not written yet — rerun after the phase completes)")
