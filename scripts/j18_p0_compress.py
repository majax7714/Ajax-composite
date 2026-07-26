"""P0.4 (free) — is the coverage channel a NEW effect, or the copy null in disguise?

P0.3 found the conditioned candidate distribution does not shift down uniformly. It
COMPRESSES: fully-correct candidates collapse -72.5% relative (0.238 -> 0.065) while
the [0.25,0.75) band gains +0.341 and the ZERO band SHRINKS (0.280 -> 0.210). The
bottom of the distribution improves and the top is destroyed, which is precisely why
mean frac — the currency every sink number in this record is quoted in — moves only
-13.4%: the two effects partially cancel inside it.

Two things must be settled before a phase is built on that, and both are free.

(1) THE CRITERION IS CURRENCY-DEPENDENT, and nobody has checked. The SINK is defined
    as below BOTH nulls: the model's own i.i.d. AND the copy null. The copy null is
    "just emit the artifact." In MEAN FRAC that null scores 0.4589 and the conditioned
    arm is below it. But these are partial-credit artifacts — if none of them fully
    passes, the copy null's COVERAGE is 0.000 by construction, and the conditioned arm
    beats it enormously. Re-expressing the sink in the coverage currency would then
    NOT satisfy below-both-nulls, and "the sink is a coverage effect" would be a
    claim the sink's own definition does not support. Phase 10 P0.2 restored this
    criterion after it had silently drifted once; it must not be allowed to drift
    again by a change of units.

(2) A POSITIVE MECHANISM IS NOW TESTABLE ON COMMITTED DATA. If conditioning pulls the
    candidate distribution TOWARD THE ARTIFACT'S QUALITY, then per problem the shift
    (cond - iid) should scale with the gap (artifact - iid) and the slope should be
    positive. Every excluded mechanism so far (OOD/surprise, attention magnitude,
    attention concentration) was excluded by measurement; this one can at least be
    checked for free before anything is spent on it.

Free: reads committed pools and the committed artifact set, spends nothing.
"""
import json
import math
import pathlib
import random
import sys
import statistics as st

REPO = pathlib.Path(__file__).resolve().parents[1]
RUNS = REPO / "runs/modal"
SEED = 257
BOOT = 4000


def load(tag):
    p = RUNS / f"{tag}.json"
    return json.loads(p.read_text()) if p.exists() else None


def arm(ctag, rtag, lo=0, hi=None):
    c, r = load(ctag), load(rtag)
    assert c and r, f"missing {ctag}/{rtag}"
    return {x["qid"]: [y["frac"] for y in row]
            for x, row in zip(c[lo:hi], r[lo:hi])}


def pass_at_k(fracs, k):
    n = len(fracs)
    c = sum(1 for f in fracs if f >= 1.0)
    if n - c < k:
        return 1.0
    return 1.0 - math.comb(n - c, k) / math.comb(n, k)


IID = arm("j11_sweep_cand_coder1p5b", "j11_sweep_res_coder1p5b")
CND = arm("j17_coder1p5b_A_cand", "j17_coder1p5b_A_res")

# The P11 cell's per-artifact fracs are not carried standalone in artifacts/ — the
# targeting file records only the chosen band. Reconstruct the exact selection with
# the same committed pool and the same frozen selector the cell used, then ASSERT it
# reproduces the committed mean (0.4589) before anything is computed from it.
sys.path.insert(0, str(REPO / "scripts"))
import modal_h1 as M  # noqa: E402

_qids, _pool = M._r3_donor_pool()
_powered = {q: st.mean(IID[q]) for q in IID}
_ch = json.loads((REPO / "artifacts/h11_targeting_coder1p5b.json").read_text())["chosen"]
_sel = M._r3_select(_pool, _qids, _powered, _ch["target"], _ch["hw"])
ARTS = {q: {"qid": q, "frac": c[1], "n_tests": c[3]} for q, c in _sel.items()}
assert len(ARTS) == _ch["n"], f"reconstructed n={len(ARTS)} != committed {_ch['n']}"
_mr = round(st.mean(a["frac"] for a in ARTS.values()), 4)
assert _mr == _ch["mean_art"], f"reconstructed mean_art {_mr} != committed {_ch['mean_art']}"
print(f"[artifact set reconstructed and verified: n={len(ARTS)}, "
      f"mean_art {_mr:.4f} == committed {_ch['mean_art']:.4f}]")

QS = sorted(set(CND) & set(IID) & set(ARTS))
rng = random.Random(SEED)

print("=" * 78)
print("P0.4 — currency-dependence of the criterion, and a testable compression")
print("=" * 78)
print(f"cell: Qwen2.5-Coder-1.5B at match, n={len(QS)}")

# --------------------------------------------------------- (1) the copy null
art = {q: ARTS[q]["frac"] for q in QS}
n_perfect = sum(1 for q in QS if art[q] >= 1.0)
cov_copy = n_perfect / len(QS)
mf_i = st.mean(st.mean(IID[q]) for q in QS)
mf_c = st.mean(st.mean(CND[q]) for q in QS)
mf_a = st.mean(art[q] for q in QS)
cov_i = st.mean(pass_at_k(IID[q], 24) for q in QS)
cov_c = st.mean(pass_at_k(CND[q], 24) for q in QS)

print("\n" + "-" * 78)
print("(1) below-BOTH-nulls, evaluated in each currency")
print("-" * 78)
print(f"  artifacts fully passing: {n_perfect}/{len(QS)}  -> copy-null coverage "
      f"{cov_copy:.4f}")
print(f"\n  {'currency':<14} {'iid null':>10} {'copy null':>11} {'cond':>10} "
      f"{'< iid':>7} {'< copy':>7} {'SINK':>6}")
rows = {}
for lab, ni, nc_, c in (("mean frac", mf_i, mf_a, mf_c),
                        ("coverage@24", cov_i, cov_copy, cov_c)):
    b1, b2 = c < ni, c < nc_
    rows[lab] = {"iid_null": round(ni, 4), "copy_null": round(nc_, 4),
                 "cond": round(c, 4), "below_iid": bool(b1), "below_copy": bool(b2),
                 "below_both_nulls": bool(b1 and b2)}
    print(f"  {lab:<14} {ni:>10.4f} {nc_:>11.4f} {c:>10.4f} "
          f"{str(b1):>7} {str(b2):>7} {str(b1 and b2):>6}")

print("\n  READ: the SINK is a MEAN-FRAC statement. In the coverage currency the")
print("  conditioned arm is far ABOVE the copy null (copying a partial-credit artifact")
print("  scores zero coverage by construction), so below-both-nulls does NOT hold there.")
print("  'The sink is a coverage effect' is therefore NOT licensed as a restatement of")
print("  claim 8. What IS licensed: conditioning's damage is concentrated in coverage,")
print("  measured against the i.i.d. null only.")

# ----------------------------------------------- (2) compression toward artifact
print("\n" + "-" * 78)
print("(2) does conditioning pull candidates toward the ARTIFACT'S quality?")
print("-" * 78)
x = [art[q] - st.mean(IID[q]) for q in QS]          # gap: artifact minus own iid
y = [st.mean(CND[q]) - st.mean(IID[q]) for q in QS]  # shift: conditioned minus iid
mx, my = st.mean(x), st.mean(y)
sxx = sum((xi - mx) ** 2 for xi in x)
slope = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / sxx
icept = my - slope * mx
resid = [yi - (icept + slope * xi) for xi, yi in zip(x, y)]
sse = sum(r ** 2 for r in resid)
sst = sum((yi - my) ** 2 for yi in y)
r2 = 1 - sse / sst
se_slope = math.sqrt(sse / (len(QS) - 2) / sxx)

bs = []
for _ in range(BOOT):
    idx = [rng.randrange(len(QS)) for _ in QS]
    bx = [x[i] for i in idx]
    by = [y[i] for i in idx]
    bmx, bmy = st.mean(bx), st.mean(by)
    bsxx = sum((xi - bmx) ** 2 for xi in bx)
    if bsxx > 0:
        bs.append(sum((xi - bmx) * (yi - bmy) for xi, yi in zip(bx, by)) / bsxx)
bs.sort()
slo, shi = bs[int(0.025 * len(bs))], bs[int(0.975 * len(bs))]

print(f"  regression  shift = {icept:+.4f} + {slope:+.4f} * gap")
print(f"     slope {slope:+.4f}  SE {se_slope:.4f}  bootstrap CI95 "
      f"[{slo:+.4f}, {shi:+.4f}]   R^2 {r2:.3f}")
print(f"     mean gap {mx:+.4f}   mean shift {my:+.4f}")
print(f"  a pure copy predicts slope +1.00 and intercept 0; no pull predicts slope 0.")

# split: does the sign of the gap predict the sign of the shift?
up = [q for q in QS if art[q] > st.mean(IID[q])]
dn = [q for q in QS if art[q] < st.mean(IID[q])]
su = st.mean(st.mean(CND[q]) - st.mean(IID[q]) for q in up)
sd = st.mean(st.mean(CND[q]) - st.mean(IID[q]) for q in dn)
print(f"\n  artifact ABOVE own iid ({len(up)} problems): mean shift {su:+.4f}")
print(f"  artifact BELOW own iid ({len(dn)} problems): mean shift {sd:+.4f}")
print(f"  -> both arms shift DOWN" if su < 0 and sd < 0
      else "  -> shift follows the gap's sign (compression)")

# coverage cost of the same split
cu = st.mean(pass_at_k(CND[q], 24) - pass_at_k(IID[q], 24) for q in up)
cd = st.mean(pass_at_k(CND[q], 24) - pass_at_k(IID[q], 24) for q in dn)
print(f"  coverage@24 delta: artifact-above {cu:+.4f}   artifact-below {cd:+.4f}")

out = {"_label": "P0.4 free — currency-dependence + compression test [PHASE_18.md P0]",
       "seed": SEED, "boot": BOOT, "n": len(QS),
       "copy_null_coverage": round(cov_copy, 4),
       "artifacts_fully_passing": n_perfect,
       "below_both_nulls_by_currency": rows,
       "compression": {"slope": round(slope, 4), "se": round(se_slope, 4),
                       "ci95": [round(slo, 4), round(shi, 4)],
                       "intercept": round(icept, 4), "r2": round(r2, 4),
                       "mean_gap": round(mx, 4), "mean_shift": round(my, 4),
                       "shift_artifact_above": round(su, 4),
                       "shift_artifact_below": round(sd, 4),
                       "n_above": len(up), "n_below": len(dn),
                       "cov_delta_above": round(cu, 4),
                       "cov_delta_below": round(cd, 4)}}
(REPO / "artifacts/h18_p0_compress.json").write_text(json.dumps(out, indent=2))
print("\nwrote artifacts/h18_p0_compress.json")
