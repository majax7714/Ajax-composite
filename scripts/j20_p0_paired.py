"""P0 (free) — the paired twin-vs-sibling comparison ALREADY EXISTS on 37 problems,
and the power arithmetic for extending it is free too.

Phase 19 closed with the twin CLEAN at true match (-0.0027) and its Coder sibling at
-0.0638, but the comparison was UNPAIRED (different problem subsets, each model matched
to its own quality) and underpowered: difference +0.0610 +/- 0.0424, p 0.150, MDE 0.080
against a separation of ~0.04. Section 8 entry 12 records the charter's failure to compute
that in advance.

The author's direction for this phase is a PAIRED twin-vs-sibling design. Before spending
anything on one, two free facts:

  (1) The two committed cells SHARE 37 PROBLEMS. Both were run at their own true match
      through the same code path. So a paired estimate of the difference is available
      right now, at zero cost, on 37 of the 44/54 problems.

  (2) Whether a LARGER paired design can reach the precision the question needs is an
      arithmetic question, answerable from the same committed data by decomposing the
      per-problem effect variance into a between-problem component and a
      candidate-sampling component (Phase 17's P0 method: subsample k' of the committed
      candidates, refit, watch SE scale). The donor pool has only 80 problems, so if the
      between-problem component alone puts the required n above 80, THE QUESTION CANNOT
      BE RESOLVED WITH THIS POOL and that is the finding — before any spend, not after.

This script does both, and it recomputes each cell's achieved Delta_art ON THE SHARED
SUBSET, because restricting to shared problems is itself a re-selection and may move
either model off the match its cell was targeted to. That check gates everything else.

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
SEED = 317
BOOT = 8000
REPS = 400

sys.path.insert(0, str(REPO / "scripts"))
import modal_h1 as M  # noqa: E402


def cell(tag):
    """A committed matched cell: [i.i.d. arm | conditioned arm], n rows each."""
    c = json.loads((RUNS / f"j8_cand_P11_{tag}.json").read_text())
    r = json.loads((RUNS / f"j8_res_P11_{tag}.json").read_text())
    n = len(c) // 2
    iid = {x["qid"]: [y["frac"] for y in row] for x, row in zip(c[:n], r[:n])}
    cnd = {x["qid"]: [y["frac"] for y in row] for x, row in zip(c[n:], r[n:])}
    return iid, cnd


def sweep(rung):
    g = json.loads((RUNS / f"j11_sweep_cand_{rung}.json").read_text())
    r = json.loads((RUNS / f"j11_sweep_res_{rung}.json").read_text())
    return {x["qid"]: st.mean(c["frac"] for c in row) for x, row in zip(g, r)}


def arts(rung):
    ch = json.loads((REPO / f"artifacts/h11_targeting_{rung}.json").read_text())["chosen"]
    qids, pool = M._r3_donor_pool()
    sel = M._r3_select(pool, qids, sweep(rung), ch["target"], ch["hw"])
    a = {q: c[1] for q, c in sel.items()}
    assert round(st.mean(a.values()), 4) == ch["mean_art"], "artifact set mismatch"
    return a


TW_I, TW_C = cell("general1p5b")
SB_I, SB_C = cell("coder1p5b")
TW_A, SB_A = arts("general1p5b"), arts("coder1p5b")
TW_P, SB_P = sweep("general1p5b"), sweep("coder1p5b")
SH = sorted(set(TW_I) & set(SB_I))
rng = random.Random(SEED)

print("=" * 84)
print("P0 — the paired comparison that already exists  [PHASE_20.md P0]")
print("=" * 84)
print(f"twin cell n={len(TW_I)}   sibling cell n={len(SB_I)}   SHARED n={len(SH)}")

# ------------------------------------------------- (0) is the shared subset still at match?
print("\n" + "-" * 84)
print("(0) GATE — does restricting to the shared subset keep each model at its match?")
print("-" * 84)
ok = True
for lab, P, A in (("twin", TW_P, TW_A), ("sibling", SB_P, SB_A)):
    full = st.mean(A[q] - P[q] for q in A)
    sub = st.mean(A[q] - P[q] for q in SH if q in A)
    drift = sub - full
    good = abs(sub) <= 0.020          # P11_ON_TARGET, the record's own band
    ok &= good
    print(f"  {lab:<9} Δ_art full cell {full:+.4f}   on shared subset {sub:+.4f}   "
          f"drift {drift:+.4f}   |subset| <= 0.020: {good}")
print(f"  -> shared-subset comparison is {'VALID' if ok else 'OFF-TARGET — do not use'}")

# ------------------------------------------------- (1) the free paired estimate
print("\n" + "-" * 84)
print("(1) the paired difference, on committed data, at zero cost")
print("-" * 84)
te = {q: st.mean(TW_C[q]) - st.mean(TW_I[q]) for q in SH}
se_ = {q: st.mean(SB_C[q]) - st.mean(SB_I[q]) for q in SH}
d = [te[q] - se_[q] for q in SH]
n = len(SH)
mt, ms = st.mean(te.values()), st.mean(se_.values())
md = st.mean(d)
sd = st.stdev(d) / math.sqrt(n)
acc = sorted(st.mean([d[rng.randrange(n)] for _ in range(n)]) for _ in range(BOOT))
lo, hi = acc[int(.025 * BOOT)], acc[int(.975 * BOOT)]
p = math.erfc(abs(md / sd) / math.sqrt(2))
r = st.correlation(list(te.values()), list(se_.values()))

print(f"  twin effect on shared    {mt:+.4f}")
print(f"  sibling effect on shared {ms:+.4f}")
print(f"  PAIRED difference        {md:+.4f}  SE {sd:.4f}  "
      f"CI95 [{lo:+.4f},{hi:+.4f}]  p {p:.3f}")
print(f"  per-problem correlation between the two models' effects: r = {r:+.3f}")
unp = math.hypot(st.stdev(te.values()) / math.sqrt(n), st.stdev(se_.values()) / math.sqrt(n))
print(f"  unpaired SE on the same n would be {unp:.4f}  -> pairing buys "
      f"{(1 - sd / unp) * 100:.0f}%")
print(f"  (Phase 19's cross-cell unpaired SE was 0.0424 at n=54/44)")

# ------------------------------------------------- (2) variance decomposition
print("\n" + "-" * 84)
print("(2) where the variance lives — can more k help, or is it between-problem?")
print("-" * 84)


def se_at_k(kk, reps=REPS):
    acc = []
    for _ in range(reps):
        dd = [(st.mean(rng.sample(TW_C[q], kk)) - st.mean(rng.sample(TW_I[q], kk)))
              - (st.mean(rng.sample(SB_C[q], kk)) - st.mean(rng.sample(SB_I[q], kk)))
              for q in SH]
        acc.append(st.variance(dd) / len(SH))
    return math.sqrt(st.mean(acc))


ks = [2, 3, 4, 6, 8]
ses = [se_at_k(k) for k in ks]
print(f"  {'k':>3} {'paired SE at n=' + str(n):>20}")
for k, s in zip(ks, ses):
    print(f"  {k:>3} {s:>20.4f}")
x = [1 / k for k in ks]
y = [s ** 2 for s in ses]
mx, my = st.mean(x), st.mean(y)
b = sum((a - mx) * (c - my) for a, c in zip(x, y)) / sum((a - mx) ** 2 for a in x)
a0 = max(my - b * mx, 0.0)
print(f"\n  fit SE^2(k) = {a0:.6f} + {b:.6f}/k   at n={n}")
print(f"  irreducible SE as k -> infinity, at n={n}: {math.sqrt(a0):.4f}")


def se_nk(nn, kk):
    return math.sqrt((a0 + b / kk) * n / nn)


# ------------------------------------------------- (3) what would it take?
print("\n" + "-" * 84)
print("(3) what n and k would resolve the difference? (80 problems exist in the pool)")
print("-" * 84)
POOL = 80
for target in (0.061, 0.040, 0.016):
    need = 2.8  # z(.975)+z(.80)
    print(f"\n  to detect a difference of {target:+.4f} at 80% power:")
    print(f"      {'k':>4} {'n needed':>10} {'feasible in an 80-problem pool?':>34}")
    for kk in (8, 24, 48, 96):
        v = a0 + b / kk
        nn = v * n / (target / need) ** 2
        feas = "YES" if nn <= POOL else f"no (needs {math.ceil(nn)})"
        print(f"      {kk:>4} {math.ceil(nn):>10} {feas:>34}")

print("\n  reference effect sizes:")
print(f"      Phase 19 observed twin-vs-sibling (unpaired, cross-cell)  +0.0610")
print(f"      this paired estimate on shared problems                   {md:+.4f}")
print(f"      the compression law's predicted intercept difference       +0.0166")

best = se_nk(POOL, 96)
print(f"\n  BEST ACHIEVABLE with the whole pool (n={POOL}) at k=96: SE {best:.4f}"
      f"  -> MDE {2.8 * best:.4f}")

(REPO / "artifacts/h20_p0_paired.json").write_text(json.dumps(
    {"_label": "P0 free — paired twin-vs-sibling on shared problems + power [PHASE_20.md]",
     "seed": SEED, "boot": BOOT, "n_shared": n,
     "subset_on_target": bool(ok),
     "twin_effect_shared": round(mt, 4), "sibling_effect_shared": round(ms, 4),
     "paired_difference": round(md, 4), "se": round(sd, 4),
     "ci95": [round(lo, 4), round(hi, 4)], "p": round(p, 4),
     "correlation": round(r, 4),
     "unpaired_se_same_n": round(unp, 4),
     "variance_fit": {"a": round(a0, 8), "b": round(b, 8),
                      "irreducible_se_at_n": round(math.sqrt(a0), 4)},
     "measured_se_by_k": {str(k): round(s, 4) for k, s in zip(ks, ses)},
     "best_achievable_pool80_k96": {"se": round(best, 4), "mde": round(2.8 * best, 4)},
     "pool_size": POOL}, indent=2))
print("\nwrote artifacts/h20_p0_paired.json")
