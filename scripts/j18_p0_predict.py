"""P0.6 (free) — fit the predictor that Phase 18's paid cells will be scored against,
and derive the HIT tolerance from MEASURED spread rather than from a round number.

Two errors in this record came from thresholds chosen as round numbers against
quantities whose spread was never looked at: Phase 10 R3's +/-0.03 band against an
instrument SE of 0.028, and Phase 16's `<= -0.03` validity gate against a committed CI
0.123 wide, which fired by 0.0004 and cost the phase (§8 entry 9). Phase 17 fixed this
by referencing committed CIs. This script does the same job in advance: every gate
Phase 18 freezes is expressed in units of a prediction SD computed here, before the
prediction is made and long before any data exists to compare it to.

It also checks the one assumption the two-band design rests on — that the law is
symmetric about gap = 0. If compression is materially stronger downward than upward,
a linear extrapolation to +/-0.17 is the wrong instrument and the charter must say so
before it spends.

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
SEED = 269
BOOT = 8000

sys.path.insert(0, str(REPO / "scripts"))
import modal_h1 as M  # noqa: E402


def load(tag):
    return json.loads((RUNS / f"{tag}.json").read_text())


def armof(ctag, rtag, lo=0, hi=None):
    c, r = load(ctag), load(rtag)
    return {x["qid"]: [y["frac"] for y in row] for x, row in zip(c[lo:hi], r[lo:hi])}


IID = armof("j11_sweep_cand_coder1p5b", "j11_sweep_res_coder1p5b")   # k=24, seed 151
CND = armof("j17_coder1p5b_A_cand", "j17_coder1p5b_A_res")           # k=24, seed 239

_qids, _pool = M._r3_donor_pool()
POWERED = {q: st.mean(IID[q]) for q in IID}
_ch = json.loads((REPO / "artifacts/h11_targeting_coder1p5b.json").read_text())["chosen"]
_sel = M._r3_select(_pool, _qids, POWERED, _ch["target"], _ch["hw"])
ART = {q: c[1] for q, c in _sel.items()}
assert round(st.mean(ART.values()), 4) == _ch["mean_art"]

QS = sorted(set(CND) & set(ART))
X = [ART[q] - POWERED[q] for q in QS]
Y = [st.mean(CND[q]) - POWERED[q] for q in QS]
rng = random.Random(SEED)

print("=" * 80)
print("P0.6 — the committed predictor and its tolerance  [PHASE_18.md P0]")
print("=" * 80)
print(f"fit cell: Coder-1.5B at match, n={len(QS)}, k=24 both arms")
print(f"  i.i.d.  j11 sweep (seed 151)      conditioned  j17 VERB-A (seed 239)")
print(f"  per-problem gap range observed: [{min(X):+.4f}, {max(X):+.4f}]")


def ols(x, y):
    mx, my = st.mean(x), st.mean(y)
    sxx = sum((xi - mx) ** 2 for xi in x)
    b = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / sxx
    return my - b * mx, b


A, B = ols(X, Y)
resid = [yi - (A + B * xi) for xi, yi in zip(X, Y)]
sd_resid = st.stdev(resid)
print(f"\n  LAW  shift = {A:+.4f} {B:+.4f} * gap     residual SD {sd_resid:.4f}")

# ---------------------------------------------------------------- symmetry check
print("\n" + "-" * 80)
print("symmetry: is compression the same above and below match?")
print("-" * 80)
lo_i = [i for i in range(len(QS)) if X[i] < 0]
hi_i = [i for i in range(len(QS)) if X[i] > 0]
for lab, idx in (("gap < 0 (artifact worse)", lo_i), ("gap > 0 (artifact better)", hi_i)):
    a_, b_ = ols([X[i] for i in idx], [Y[i] for i in idx])
    print(f"  {lab:<26} n={len(idx):>3}  slope {b_:+.4f}  intercept {a_:+.4f}")
bs_gap = []
for _ in range(BOOT):
    ii = [rng.randrange(len(QS)) for _ in QS]
    l_ = [i for i in ii if X[i] < 0]
    h_ = [i for i in ii if X[i] > 0]
    if len(l_) < 5 or len(h_) < 5:
        continue
    try:
        _, bl = ols([X[i] for i in l_], [Y[i] for i in l_])
        _, bh = ols([X[i] for i in h_], [Y[i] for i in h_])
        bs_gap.append(bh - bl)
    except ZeroDivisionError:
        continue
bs_gap.sort()
gl, gh = bs_gap[int(.025 * len(bs_gap))], bs_gap[int(.975 * len(bs_gap))]
print(f"  slope difference (above - below): CI95 [{gl:+.4f}, {gh:+.4f}]  "
      f"{'includes 0 -> symmetric enough to extrapolate' if gl <= 0 <= gh else 'EXCLUDES 0 -> asymmetric'}")

# ---------------------------------------------------------------- predictions
print("\n" + "-" * 80)
print("committed predictions at two out-of-sample bands")
print("-" * 80)
grid = json.loads((REPO / "artifacts/h11_targeting_coder1p5b.json").read_text())["grid"]


def band(target, hw):
    r = next(x for x in grid if x["target"] == target and x["hw"] == hw)
    sel = M._r3_select(_pool, _qids, POWERED, target, hw)
    assert len(sel) == r["n"], f"{target}/{hw}: {len(sel)} != {r['n']}"
    return r, {q: c[1] for q, c in sel.items()}


BANDS = [("LOW", 0.20, 0.10), ("HIGH", 0.67, 0.08)]
out = {}
for name, t, hw in BANDS:
    r, arts = band(t, hw)
    qs = sorted(arts)
    gaps = [arts[q] - POWERED[q] for q in qs]
    mg = st.mean(gaps)
    n = len(qs)

    # parameter uncertainty: bootstrap the fit, evaluate the mean prediction at mg
    preds = []
    for _ in range(BOOT):
        ii = [rng.randrange(len(QS)) for _ in QS]
        try:
            a_, b_ = ols([X[i] for i in ii], [Y[i] for i in ii])
        except ZeroDivisionError:
            continue
        preds.append(a_ + b_ * mg)
    se_param = st.stdev(preds)
    # cell noise: SE of a mean of n per-problem shifts with the fit's residual spread
    se_cell = sd_resid / math.sqrt(n)
    se_tot = math.hypot(se_param, se_cell)

    pred_shift = A + B * mg
    iid_mean = st.mean(POWERED[q] for q in qs)
    pred_cond = iid_mean + pred_shift
    out[name] = {"target": t, "hw": hw, "n": n,
                 "mean_art": round(st.mean(arts.values()), 4),
                 "mean_iid_powered": round(iid_mean, 4),
                 "mean_gap": round(mg, 4),
                 "gap_range": [round(min(gaps), 4), round(max(gaps), 4)],
                 "pred_shift": round(pred_shift, 4),
                 "pred_cond": round(pred_cond, 4),
                 "se_param": round(se_param, 4), "se_cell": round(se_cell, 4),
                 "se_total": round(se_tot, 4),
                 "hit_band_2sd": [round(pred_shift - 2 * se_tot, 4),
                                  round(pred_shift + 2 * se_tot, 4)]}
    print(f"\n  {name}: target {t} +/-{hw}   n={n}   artifacts {out[name]['mean_art']:.4f}"
          f"   own i.i.d. {iid_mean:.4f}")
    print(f"     mean gap {mg:+.4f}  (fit was observed over [{min(X):+.3f},{max(X):+.3f}];"
          f" this band spans [{min(gaps):+.3f},{max(gaps):+.3f}])")
    print(f"     PREDICTED shift {pred_shift:+.4f}  -> conditioned mean frac "
          f"{pred_cond:.4f}")
    print(f"     SE  parameter {se_param:.4f}  cell {se_cell:.4f}  total {se_tot:.4f}")
    print(f"     HIT band (+/-2 SD): shift in [{out[name]['hit_band_2sd'][0]:+.4f}, "
          f"{out[name]['hit_band_2sd'][1]:+.4f}]")

print(f"\n  generations required: "
      f"{sum(out[n]['n'] for n in out)} problems x 24 = "
      f"{sum(out[n]['n'] for n in out) * 24} (i.i.d. arms already committed — the k=24"
      f" sweep covers all 80 donor problems)")

(REPO / "artifacts/h18_p0_predict.json").write_text(json.dumps(
    {"_label": "P0.6 free — committed predictor + tolerances [PHASE_18.md P0]",
     "_law": "shift(q) = a + b*gap(q), fit on the at-match cell, k=24 both arms",
     "seed": SEED, "boot": BOOT,
     "fit": {"intercept": round(A, 4), "slope": round(B, 4),
             "residual_sd": round(sd_resid, 4), "n": len(QS),
             "gap_range_fit": [round(min(X), 4), round(max(X), 4)]},
     "symmetry_slope_diff_ci95": [round(gl, 4), round(gh, 4)],
     "bands": out}, indent=2))
print("\nwrote artifacts/h18_p0_predict.json")
