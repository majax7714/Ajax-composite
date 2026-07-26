"""P0 (free) — put an error bar on the coverage channel, and ask where it lives.

Phase 16's free decomposition (h16_p0_diversity.json) reported that the SINK, which
has been measured as MEAN FRAC since D2c, is dominated by COVERAGE: Coder-1.5B
0.636 -> 0.205 pass@8, a -0.432 drop against a mean-frac drop of -0.064. Section 0.4
carries that as "the strongest live pointer in the record."

It carries it WITHOUT AN ERROR BAR, from a single seed, at k=8. Before a phase is
built on it, three free things are owed:

  P0.1  a CI. Bootstrap over problems, on the matched-k=24 arms the record already
        has committed (the i.i.d. targeting sweep at k=24 covers all 44 cell
        problems), using the unbiased pass@k estimator rather than a point count.

  P0.2  a seed check. The conditioned arm at k=8 exists at THREE independent seeds
        (173 P11 cell, 233 Phase 16 VERB-A, 239 Phase 17 VERB-A subsampled). VERB-A
        is byte-identical to _d2c_context, asserted in modal_h1.py, so these are
        replications of one cell and not three different cells. If coverage swings
        across seeds by an appreciable fraction of -0.432, the pointer needs the
        spread quoted with it.

  P0.3  a location. Mean frac and coverage can only diverge this hard if conditioning
        moves candidate mass off the frac == 1.0 point without moving the mean much.
        That is a checkable statement about the per-candidate distribution, and it is
        the difference between "the sink is a coverage effect" and "the sink is a
        near-miss effect that pass@k reads as coverage."

Free: reads committed pools, spends nothing.
"""
import json
import math
import pathlib
import random
import statistics as st
from collections import Counter

REPO = pathlib.Path(__file__).resolve().parents[1]
RUNS = REPO / "runs/modal"

SEED = 251
BOOT = 4000
KMAX = 24


def load(tag):
    p = RUNS / f"{tag}.json"
    return json.loads(p.read_text()) if p.exists() else None


def arm(ctag, rtag, lo=0, hi=None):
    """-> {qid: [frac per candidate]} for a committed (candidates, results) pair."""
    c, r = load(ctag), load(rtag)
    assert c and r, f"missing {ctag}/{rtag}"
    c, r = c[lo:hi], r[lo:hi]
    return {x["qid"]: [y["frac"] for y in row] for x, row in zip(c, r)}


def pass_at_k(fracs, k):
    """Unbiased pass@k (Chen et al. 2021): 1 - C(n-c,k)/C(n,k), c = #fully-correct."""
    n = len(fracs)
    c = sum(1 for f in fracs if f >= 1.0)
    if n - c < k:
        return 1.0
    return 1.0 - math.comb(n - c, k) / math.comb(n, k)


def boot_ci(vals_by_q, qs, rng, stat, b=BOOT):
    """Case-resampling bootstrap over PROBLEMS (the unit the record pairs on)."""
    acc = []
    for _ in range(b):
        s = [qs[rng.randrange(len(qs))] for _ in qs]
        acc.append(stat([vals_by_q[q] for q in s]))
    acc.sort()
    return acc[int(0.025 * b)], acc[int(0.975 * b)]


print("=" * 78)
print("P0 — the coverage channel, with an error bar  [PHASE_18.md P0]")
print("=" * 78)

rng = random.Random(SEED)
out = {}

# ---------------------------------------------------------------- arms
IID24 = arm("j11_sweep_cand_coder1p5b", "j11_sweep_res_coder1p5b")   # seed 151, k=24
CND24 = arm("j17_coder1p5b_A_cand", "j17_coder1p5b_A_res")           # seed 239, k=24
IID8 = arm("j8_cand_P11_coder1p5b", "j8_res_P11_coder1p5b", 0, 44)   # seed 173, k=8
CND8_173 = arm("j8_cand_P11_coder1p5b", "j8_res_P11_coder1p5b", 44, 88)
CND8_233 = arm("j16_coder1p5b_A_cand", "j16_coder1p5b_A_res")        # seed 233, k=8

QS = sorted(set(CND24) & set(IID24))
assert len(QS) == 44, len(QS)
assert all(len(IID24[q]) == 24 and len(CND24[q]) == 24 for q in QS)
print(f"\ncell: Qwen2.5-Coder-1.5B at match, n={len(QS)} problems")
print("  i.i.d. k=24  = j11 powered targeting sweep (seed 151), 44 of its 80 problems")
print("  cond  k=24  = j17 VERB-A (seed 239); VERB-A == _d2c_context byte-for-byte")

# ---------------------------------------------------------------- P0.1
print("\n" + "-" * 78)
print("P0.1 — matched-k pass@k curves with bootstrap CIs over problems")
print("-" * 78)
print(f"  {'k':>3} {'iid':>8} {'cond':>8} {'delta':>9} {'CI95 on delta':>22} {'sig':>4}")
curve = {}
for k in (1, 2, 4, 8, 16, 24):
    d_by_q = {q: pass_at_k(CND24[q], k) - pass_at_k(IID24[q], k) for q in QS}
    mi = st.mean(pass_at_k(IID24[q], k) for q in QS)
    mc = st.mean(pass_at_k(CND24[q], k) for q in QS)
    d = st.mean(d_by_q.values())
    lo, hi = boot_ci(d_by_q, QS, rng, st.mean)
    sig = "***" if hi < 0 or lo > 0 else ""
    print(f"  {k:>3} {mi:>8.4f} {mc:>8.4f} {d:>+9.4f}   [{lo:+.4f}, {hi:+.4f}] {sig:>4}")
    curve[str(k)] = {"iid": round(mi, 4), "cond": round(mc, 4), "delta": round(d, 4),
                     "ci95": [round(lo, 4), round(hi, 4)]}

mf_i = st.mean(st.mean(IID24[q]) for q in QS)
mf_c = st.mean(st.mean(CND24[q]) for q in QS)
mf_by_q = {q: st.mean(CND24[q]) - st.mean(IID24[q]) for q in QS}
mf_lo, mf_hi = boot_ci(mf_by_q, QS, rng, st.mean)
print(f"\n  mean frac (the currency every sink number is quoted in):")
print(f"      iid {mf_i:.4f}  cond {mf_c:.4f}  delta {mf_c - mf_i:+.4f}  "
      f"CI95 [{mf_lo:+.4f}, {mf_hi:+.4f}]")

# ---------------------------------------------------------------- P0.2
print("\n" + "-" * 78)
print("P0.2 — seed replication of the coverage number at matched k=8")
print("-" * 78)
reps = {"173 (P11 cell)": CND8_173, "233 (P16 VERB-A)": CND8_233}
cov8 = {}
for lab, A in reps.items():
    qs = sorted(set(A) & set(IID8))
    c = st.mean(pass_at_k(A[q], 8) for q in qs)
    i = st.mean(pass_at_k(IID8[q], 8) for q in qs)
    m = st.mean(st.mean(A[q]) for q in qs)
    cov8[lab] = {"cov": round(c, 4), "delta_cov": round(c - i, 4),
                 "mean_frac": round(m, 4), "n": len(qs)}
    print(f"  seed {lab:<18} cov@8 {c:.4f}  delta {c - i:+.4f}   mean_frac {m:.4f}")
# seed 239 at k=8, by subsampling the committed k=24 pool
sub = []
for _ in range(200):
    sub.append(st.mean(pass_at_k(rng.sample(CND24[q], 8), 8) for q in QS))
i8 = st.mean(pass_at_k(IID8[q], 8) for q in QS)
cov8["239 (P17 VERB-A, subsampled)"] = {"cov": round(st.mean(sub), 4),
                                        "delta_cov": round(st.mean(sub) - i8, 4),
                                        "mean_frac": round(mf_c, 4), "n": len(QS)}
print(f"  seed {'239 (P17, sub k=8)':<18} cov@8 {st.mean(sub):.4f}  "
      f"delta {st.mean(sub) - i8:+.4f}   mean_frac {mf_c:.4f}")
spread_c = max(v["cov"] for v in cov8.values()) - min(v["cov"] for v in cov8.values())
spread_m = max(v["mean_frac"] for v in cov8.values()) - min(v["mean_frac"] for v in cov8.values())
print(f"\n  across-seed SPREAD  coverage {spread_c:.4f}   mean_frac {spread_m:.4f}")
print(f"  as a fraction of the reported effect: coverage {spread_c / 0.4318:.1%}  "
      f"mean_frac {spread_m / 0.0638:.1%}")

# ---------------------------------------------------------------- P0.3
print("\n" + "-" * 78)
print("P0.3 — where the loss lives: the per-candidate frac distribution")
print("-" * 78)


def hist(A):
    b = Counter()
    tot = 0
    for q in QS:
        for f in A[q]:
            tot += 1
            if f >= 1.0:
                b["correct (1.0)"] += 1
            elif f >= 0.75:
                b["near [0.75,1.0)"] += 1
            elif f >= 0.25:
                b["partial [0.25,0.75)"] += 1
            elif f > 0.0:
                b["weak (0,0.25)"] += 1
            else:
                b["zero (0.0)"] += 1
    return {k: v / tot for k, v in b.items()}, tot


hi_, ni = hist(IID24)
hc_, nc = hist(CND24)
bands = ["correct (1.0)", "near [0.75,1.0)", "partial [0.25,0.75)",
         "weak (0,0.25)", "zero (0.0)"]
print(f"  {'band':<22} {'iid':>8} {'cond':>8} {'shift':>9}")
for b in bands:
    print(f"  {b:<22} {hi_.get(b, 0):>8.4f} {hc_.get(b, 0):>8.4f} "
          f"{hc_.get(b, 0) - hi_.get(b, 0):>+9.4f}")

# the counterfactual: mean frac drop alone, with the correct-rate held at iid
p_corr_i = hi_.get("correct (1.0)", 0.0)
p_corr_c = hc_.get("correct (1.0)", 0.0)
print(f"\n  per-candidate CORRECT rate  iid {p_corr_i:.4f} -> cond {p_corr_c:.4f}  "
      f"({(p_corr_c / p_corr_i - 1) * 100:+.1f}% relative)")
print(f"  per-candidate MEAN frac     iid {mf_i:.4f} -> cond {mf_c:.4f}  "
      f"({(mf_c / mf_i - 1) * 100:+.1f}% relative)")

# per-problem solved/unsolved 2x2 at k=24
tt = sum(1 for q in QS if pass_at_k(IID24[q], 24) > 0 and pass_at_k(CND24[q], 24) > 0)
tf = sum(1 for q in QS if pass_at_k(IID24[q], 24) > 0 and pass_at_k(CND24[q], 24) == 0)
ft = sum(1 for q in QS if pass_at_k(IID24[q], 24) == 0 and pass_at_k(CND24[q], 24) > 0)
ff = sum(1 for q in QS if pass_at_k(IID24[q], 24) == 0 and pass_at_k(CND24[q], 24) == 0)
print(f"\n  per-problem solvedness at k=24 (>=1 correct in 24):")
print(f"      both {tt:>3}   iid-only {tf:>3}   cond-only {ft:>3}   neither {ff:>3}")
print(f"      conditioning LOSES {tf} problems outright and RECOVERS {ft}")

# on the problems conditioning loses outright, what happened to their mean frac?
lost = [q for q in QS if pass_at_k(IID24[q], 24) > 0 and pass_at_k(CND24[q], 24) == 0]
if lost:
    li = st.mean(st.mean(IID24[q]) for q in lost)
    lc = st.mean(st.mean(CND24[q]) for q in lost)
    print(f"      on those {len(lost)} lost problems: mean frac {li:.4f} -> {lc:.4f} "
          f"({lc - li:+.4f}) — the model still scores, it stops finishing")

out = {"_label": "P0 free — coverage channel with error bars [PHASE_18.md P0]",
       "_estimator": "unbiased pass@k (Chen et al. 2021) over the committed k=24 pools",
       "seed": SEED, "boot": BOOT, "n": len(QS),
       "cell": "Qwen2.5-Coder-1.5B at match (P11 problem set)",
       "arms": {"iid_k24": "j11_sweep_*_coder1p5b (seed 151)",
                "cond_k24": "j17_coder1p5b_A_* (seed 239, VERB-A == _d2c_context)"},
       "p0_1_passk_curve": curve,
       "p0_1_mean_frac": {"iid": round(mf_i, 4), "cond": round(mf_c, 4),
                          "delta": round(mf_c - mf_i, 4),
                          "ci95": [round(mf_lo, 4), round(mf_hi, 4)]},
       "p0_2_seed_replication": cov8,
       "p0_2_spread": {"coverage": round(spread_c, 4), "mean_frac": round(spread_m, 4)},
       "p0_3_candidate_bands": {"iid": {k: round(v, 4) for k, v in hi_.items()},
                                "cond": {k: round(v, 4) for k, v in hc_.items()}},
       "p0_3_solvedness_k24": {"both": tt, "iid_only": tf, "cond_only": ft,
                               "neither": ff}}
(REPO / "artifacts/h18_p0_coverage.json").write_text(json.dumps(out, indent=2))
print("\nwrote artifacts/h18_p0_coverage.json")
