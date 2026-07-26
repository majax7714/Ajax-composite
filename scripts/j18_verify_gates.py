"""Independent re-derivation of Phase 18's gates from the raw pools.

Written while the run was still generating, BEFORE any result existed, so it cannot be
shaped by the answer. It recomputes every adjudicated quantity from `runs/modal/j18_*`
without importing modal_h1, then compares against `artifacts/h18_temperature.json`.

Why this exists. This record's recurring failure is not drift — the frozen rules have
been honoured every time — it is adjudication arithmetic that nobody checked:

  §8 entry 8   Phase 14's matched-performance statistic was identically zero for any
               data, and Phase 13 S2 had shipped the same defect undetected.
  §8 entry 9   Phase 16's validity threshold was a round number inside a 0.123-wide CI.
  §8 entry 10  Phase 18 P0.4's own finding: a criterion valid in one currency and
               silently invalid in another. Plus P0.7's S2 arm, which returned exactly
               0.0000 for any input — the third instance of entry 8's class, and it was
               written by this loop hours ago.

Three of those were caught by re-deriving a number a second way. So: a second
implementation, by a different route, of every gate the phase turns on.

The independence is partial and the limit is stated rather than glossed: this shares the
raw pools and the unbiased pass@k definition with the entrypoint. What it does NOT share
is the arm-assembly, the bootstrap, the gate comparisons, or the branch tree — which is
where all three recorded defects actually lived.
"""
import json
import math
import pathlib
import random
import statistics as st

REPO = pathlib.Path(__file__).resolve().parents[1]
RUNS = REPO / "runs/modal"
TEMPS = (0.8, 1.0, 1.2)

# frozen references, transcribed by hand from the charter — NOT imported from the
# entrypoint, so a typo there shows up here as a mismatch rather than being inherited
REF_DCOV = (-0.3636, -0.0455)
REF_SINK = (-0.1258, -0.0028)
REF_COV_IID_LO = 0.5227


def tag(kind, T):
    return f"j18_{kind}_T{str(T).replace('.', 'p')}"


def load(name):
    p = RUNS / f"{name}.json"
    if not p.exists():
        return None
    return json.loads(p.read_text())


def fracs(kind, T):
    c, r = load(f"{tag(kind, T)}_cand"), load(f"{tag(kind, T)}_res")
    if not c or not r:
        return None
    return {x["qid"]: [y["frac"] for y in row] for x, row in zip(c, r)}


def passk(fs, k=24):
    n = len(fs)
    c = sum(1 for f in fs if f >= 1.0)
    return 1.0 if n - c < k else 1.0 - math.comb(n - c, k) / math.comb(n, k)


def boot(vals, seed, b=4000):
    rng = random.Random(seed)
    acc = sorted(st.mean([vals[rng.randrange(len(vals))] for _ in vals])
                 for _ in range(b))
    return acc[int(0.025 * b)], acc[int(0.975 * b)]


print("=" * 78)
print("independent re-derivation of Phase 18's gates")
print("=" * 78)

got = {}
for T in TEMPS:
    fi, fc = fracs("iid", T), fracs("cond", T)
    if not fi or not fc:
        print(f"\nT={T}: arms not yet landed — skipped")
        continue
    qs = sorted(set(fi) & set(fc))
    cvi = [passk(fi[q]) for q in qs]
    cvc = [passk(fc[q]) for q in qs]
    dcov = [b - a for a, b in zip(cvi, cvc)]
    mfi = [st.mean(fi[q]) for q in qs]
    mfc = [st.mean(fc[q]) for q in qs]
    dmf = [b - a for a, b in zip(mfi, mfc)]
    lo, hi = boot(dcov, 991)
    got[T] = {"n": len(qs), "cov_iid": st.mean(cvi), "cov_cond": st.mean(cvc),
              "dcov": st.mean(dcov), "dcov_ci": (lo, hi),
              "mean_iid": st.mean(mfi), "mean_cond": st.mean(mfc),
              "sink": st.mean(dmf)}
    g = got[T]
    print(f"\nT={T}  n={g['n']}")
    print(f"  coverage@24  iid {g['cov_iid']:.4f}  cond {g['cov_cond']:.4f}  "
          f"Δ {g['dcov']:+.4f}  CI95 [{lo:+.4f},{hi:+.4f}]")
    print(f"  mean frac    iid {g['mean_iid']:.4f}  cond {g['mean_cond']:.4f}  "
          f"sink {g['sink']:+.4f}")

if 0.8 in got:
    b = got[0.8]
    v1 = REF_DCOV[0] <= b["dcov"] <= REF_DCOV[1]
    v2 = REF_SINK[0] <= b["sink"] <= REF_SINK[1]
    print(f"\n[VALIDITY]  Δcov(0.8) {b['dcov']:+.4f} in {REF_DCOV}: {v1}")
    print(f"            sink(0.8)  {b['sink']:+.4f} in {REF_SINK}: {v2}")
    print(f"            -> {'REPLICATES' if v1 and v2 else 'NON-REPLICATION'}")

if 1.0 in got:
    o = got[1.0]
    resc = o["dcov"] > REF_DCOV[1]
    unmv = REF_SINK[0] <= o["sink"] <= REF_SINK[1]
    coll = o["cov_iid"] < REF_COV_IID_LO
    print(f"\n[T=1.0]     rescued (Δcov > {REF_DCOV[1]:+.4f}): {resc}")
    print(f"            sink unmoved (in {REF_SINK}): {unmv}")
    print(f"            collapsed (cov_iid < {REF_COV_IID_LO}): {coll}")

# ------------------------------------------------- cross-check the committed artifact
art = REPO / "artifacts/h18_temperature.json"
if art.exists():
    a = json.loads(art.read_text())
    print("\n" + "-" * 78)
    print("cross-check vs artifacts/h18_temperature.json")
    print("-" * 78)
    bad = 0
    for T, g in got.items():
        c = a["cells"].get(str(T))
        if not c:
            continue
        for key, mine in (("cov_iid", g["cov_iid"]), ("cov_cond", g["cov_cond"]),
                          ("delta_cov", g["dcov"]), ("mean_iid", g["mean_iid"]),
                          ("mean_cond", g["mean_cond"]), ("sink_vs_iid", g["sink"])):
            theirs = c[key]
            ok = abs(theirs - mine) < 5e-4
            bad += 0 if ok else 1
            if not ok:
                print(f"  MISMATCH T={T} {key}: entrypoint {theirs:+.4f} "
                      f"vs independent {mine:+.4f}")
    print(f"  {'ALL QUANTITIES AGREE' if not bad else f'{bad} MISMATCHES — DO NOT ADJUDICATE'}")
else:
    print("\n(result artifact not written yet — rerun after the phase completes)")
