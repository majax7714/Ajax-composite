"""P0 (free) — is the compression law real, or shared-noise regression to the mean?

Phase 18 P0.5 fit, per problem and per cell:

    shift(q) = a + b * gap(q),   shift = cond(q) - iid(q),   gap = art(q) - iid(q)

and reported b in [0.47, 0.90] across eight committed cells, R^2 up to 0.92. Section 0.1
carries it as "the record's most robust unexplained regularity," and Phase 19's P0 used
the slopes to argue that Phase 7's family battery was position-confounded.

**BOTH AXES CONTAIN THE SAME iid(q).** That is a textbook shared-noise construction: if
iid is estimated with error e, then gap carries -e and shift carries -e, so Cov(gap,
shift) picks up +Var(e) and the slope is biased UPWARD for any data, including data with
no true relationship at all. Nobody checked this, and the loop published the slope twice
and reasoned from it once.

Two corrections are applied here, and they pull in OPPOSITE directions:

  (1) SHARED-NOISE INFLATION -- removed by using two INDEPENDENT iid estimates, one for
      each axis. The record happens to have them for the Phase-11 cells: the k=24
      powered targeting sweep and the cell's own k=8 i.i.d. arm are separate draws.

  (2) ERRORS-IN-VARIABLES ATTENUATION -- the decorrelated estimate is still biased
      DOWNWARD, because gap's x-axis noise attenuates any OLS slope by the classic
      factor Var(gap_true)/Var(gap_observed). Correcting (1) without (2) would
      over-deflate and would be its own error.

So the honest quantity is the reliability-corrected slope, with the noise variance
measured from the two independent estimates rather than assumed.

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
SEED = 353
BOOT = 4000

sys.path.insert(0, str(REPO / "scripts"))
import modal_h1 as M  # noqa: E402


def load(t):
    p = RUNS / f"{t}.json"
    return json.loads(p.read_text()) if p.exists() else None


def cell_arms(tag):
    c, r = load(f"j8_cand_{tag}"), load(f"j8_res_{tag}")
    n = len(c) // 2
    return ({x["qid"]: [y["frac"] for y in row] for x, row in zip(c[:n], r[:n])},
            {x["qid"]: [y["frac"] for y in row] for x, row in zip(c[n:], r[n:])})


def sweep(rung):
    g, r = load(f"j11_sweep_cand_{rung}"), load(f"j11_sweep_res_{rung}")
    if not g:
        return None
    return {x["qid"]: [c["frac"] for c in row] for x, row in zip(g, r)}


def ols(x, y):
    mx, my = st.mean(x), st.mean(y)
    sxx = sum((a - mx) ** 2 for a in x)
    b = sum((a - mx) * (c - my) for a, c in zip(x, y)) / sxx
    return my - b * mx, b


def arts(rung):
    ch = json.loads((REPO / f"artifacts/h11_targeting_{rung}.json").read_text())["chosen"]
    qids, pool = M._r3_donor_pool()
    pw = {q: st.mean(v) for q, v in sweep(rung).items()}
    sel = M._r3_select(pool, qids, pw, ch["target"], ch["hw"])
    return {q: c[1] for q, c in sel.items()}


print("=" * 86)
print("P0 — the compression law under shared-noise and errors-in-variables correction")
print("=" * 86)

# Cells with TWO independent i.i.d. estimates of the same problems: the P11-family rungs.
CELLS = [("Coder-1.5B", "P11_coder1p5b", "coder1p5b"),
         ("Coder-3B", "P11_coder3b", "coder3b"),
         ("general-Qwen-1.5B (TWIN)", "P11_general1p5b", "general1p5b")]

rng = random.Random(SEED)
out = {}
print(f"\n{'cell':<26} {'n':>3} {'published':>10} {'decorrelated':>13} "
      f"{'EIV-corrected':>14} {'noise SD':>9}")
print("-" * 86)
for name, tag, rung in CELLS:
    ia, ca = cell_arms(tag)
    sw = sweep(rung)
    ART = arts(rung)
    qs = sorted(set(ca) & set(ART) & set(sw))
    m8 = {q: st.mean(ia[q]) for q in qs}          # cell's own k=8 i.i.d. arm
    m24 = {q: st.mean(sw[q]) for q in qs}         # powered k=24 sweep — independent draw
    mc = {q: st.mean(ca[q]) for q in qs}

    # published: shared iid (the cell's own arm) on both axes
    _, b_pub = ols([ART[q] - m8[q] for q in qs], [mc[q] - m8[q] for q in qs])

    # decorrelated: gap from the k=24 sweep, shift from the k=8 arm (independent noises)
    a_dec, b_dec = ols([ART[q] - m24[q] for q in qs], [mc[q] - m8[q] for q in qs])

    # measure the i.i.d. estimation noise from the two independent estimates.
    # Var(m8 - m24) = Var(e8) + Var(e24);  the gap axis here carries e24 only.
    dd = [m8[q] - m24[q] for q in qs]
    var_diff = st.variance(dd)
    # k=24 has 3x the candidates of k=8, so Var(e8) ~ 3*Var(e24) => Var(e24) = var_diff/4
    var_e24 = var_diff / 4.0
    var_gap = st.variance([ART[q] - m24[q] for q in qs])
    reliability = max(1e-9, (var_gap - var_e24) / var_gap)
    b_eiv = b_dec / reliability

    bs = []
    for _ in range(BOOT):
        ii = [rng.randrange(len(qs)) for _ in qs]
        gx = [ART[qs[i]] - m24[qs[i]] for i in ii]
        gy = [mc[qs[i]] - m8[qs[i]] for i in ii]
        try:
            _, bb = ols(gx, gy)
        except ZeroDivisionError:
            continue
        vg = st.variance(gx)
        bs.append(bb / max(1e-9, (vg - var_e24) / vg))
    bs.sort()
    lo, hi = bs[int(.025 * len(bs))], bs[int(.975 * len(bs))]

    out[name] = {"n": len(qs), "slope_published_shared_noise": round(b_pub, 4),
                 "slope_decorrelated": round(b_dec, 4),
                 "slope_eiv_corrected": round(b_eiv, 4),
                 "eiv_ci95": [round(lo, 4), round(hi, 4)],
                 "intercept_decorrelated": round(a_dec, 4),
                 "iid_noise_sd_k24": round(math.sqrt(var_e24), 4),
                 "reliability": round(reliability, 4),
                 "inflation_published_vs_eiv": round(b_pub - b_eiv, 4)}
    print(f"{name:<26} {len(qs):>3} {b_pub:>+10.4f} {b_dec:>+13.4f} "
          f"{b_eiv:>+14.4f} {math.sqrt(var_e24):>9.4f}")

print("\n  published      = shared i.i.d. on both axes (Phase 18 P0.5, as reported)")
print("  decorrelated   = gap from the k=24 sweep, shift from the k=8 arm — removes the")
print("                   shared-noise inflation but keeps errors-in-variables attenuation")
print("  EIV-corrected  = decorrelated / reliability, the estimate with BOTH biases removed")

infl = [v["inflation_published_vs_eiv"] for v in out.values()]
print(f"\n  net published-minus-corrected: {[round(v, 4) for v in infl]}")
print(f"  mean {st.mean(infl):+.4f}")
survives = all(v["eiv_ci95"][0] > 0 for v in out.values())
print(f"  every corrected slope's CI95 excludes zero: {survives}")

print("\n" + "-" * 86)
print("consequence for Phase 19's position-confound argument")
print("-" * 86)
print("  Phase 19 P0 used a mean non-Coder slope of 0.761 to compute that the +0.0882")
print("  position difference in Phase 7's battery bought +0.0672 of shift, '1.3x' the")
print("  ~0.05 effect. Those cells have only ONE i.i.d. estimate each, so they cannot be")
print("  corrected directly; the correction measured here is the best available proxy.")
for lab, adj in (("published slope 0.761", 0.761),
                 ("scaled by this phase's mean correction", None)):
    if adj is None:
        corr = st.mean(out[k]["slope_eiv_corrected"] / out[k]["slope_published_shared_noise"]
                       for k in out)
        adj = 0.761 * corr
        lab = f"{lab} (x{corr:.3f})"
    print(f"    {lab:<48} shift {0.0882 * adj:+.4f}   "
          f"ratio to 0.05 effect {abs(0.0882 * adj / 0.05):.2f}x")

(REPO / "artifacts/h21_p0_eiv.json").write_text(json.dumps(
    {"_label": "P0 free — compression law corrected for shared noise + EIV [PHASE_21.md]",
     "_issue": ("Phase 18 P0.5 fit shift = a + b*gap with the SAME estimated iid on both "
                "axes; shared noise biases b upward for any data. Corrected here with two "
                "independent iid estimates, then de-attenuated for x-axis noise."),
     "seed": SEED, "boot": BOOT, "cells": out,
     "all_corrected_slopes_exclude_zero": bool(survives)}, indent=2))
print("\nwrote artifacts/h21_p0_eiv.json")
