"""P0.5 (free) — the decisive cut: is COMPRESSION sink-specific, or universal?

P0.4 found that on the flagship sink cell, conditioning obeys a strikingly tight law:

    shift(q) = -0.0624 + 0.6559 * gap(q)          R^2 = 0.756, n = 44
    shift = mean_cond(q) - mean_iid(q)      gap = artifact_frac(q) - mean_iid(q)

i.e. the model is pulled ~66% of the way from its own quality toward the artifact's,
PLUS a constant -0.062 penalty. At matched Delta_art the gap term averages to nothing
and what is left IS the sink: -0.0624 + 0.6559*0.0015 = -0.0614, the observed value.

That decomposition is only interesting if it DISCRIMINATES. Two readings, opposite
consequences, and the record already holds the data to separate them:

  H-COMPRESS  the SLOPE is what differs. Sinking models are pulled toward the artifact
              and clean models are not. Compression would then be the positive
              mechanism — the first candidate to survive, after OOD/surprise (P9),
              attention magnitude (P12) and attention concentration (P15) were each
              excluded by measurement.

  H-OFFSET    the slope is UNIVERSAL — every model tracks the artifact it is shown,
              because that is what conditioning does — and only the INTERCEPT differs.
              The sink is then a constant cost of conditioning, compression is a shared
              and unremarkable regression-to-the-stimulus, and "coverage" is downstream
              of the offset rather than of any pull.

EVERY matched-artifact cell this record has ever committed is used — eight of them,
because all five Phase-7 cells and both Phase-11 rungs and Phase-10 R5 kept their
pools. That matters for two reasons beyond sample size:

  * it includes the ARCHITECTURE TWIN (general-Qwen-1.5B, Phase 7 M2) — same base,
    same 28L x 12H, same scale as Coder-1.5B, differing only in the Coder
    continued-pretraining stage, and measured clean. Phase 15 showed this is the cell
    that kills confounded internal claims. If the intercept is the diet's signature,
    the twin must sit at zero while its Coder sibling sits at -0.056;

  * it includes Coder-0.5B (M5), the record's OPEN lower bound on the ladder — §0.4
    carries 0.5B as unplaceable at its own straddle by mining, so anything measured
    there is new, and free.

Sink status is not collinear with size across this set (1.3B clean, 1.5B sink and
1.5B clean in the twin pair, 3B sink and 3B clean in StarCoder2, 7B clean).

Free: reads committed pools and reconstructs each committed artifact set with the
frozen selector, asserting each reproduces its committed mean before use.
"""
import json
import math
import pathlib
import random
import statistics as st
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
RUNS = REPO / "runs/modal"
SEED = 263
BOOT = 4000

sys.path.insert(0, str(REPO / "scripts"))
import modal_h1 as M  # noqa: E402


def load(tag):
    p = RUNS / f"{tag}.json"
    return json.loads(p.read_text()) if p.exists() else None


def arms(ctag, rtag):
    """A committed matched cell stores [i.i.d. arm | conditioned arm], n rows each."""
    c, r = load(ctag), load(rtag)
    assert c and r, f"missing {ctag}/{rtag}"
    n = len(c) // 2
    assert len(c) == 2 * n, f"{ctag}: {len(c)} rows, not an even split"
    iid = {x["qid"]: [y["frac"] for y in row] for x, row in zip(c[:n], r[:n])}
    cnd = {x["qid"]: [y["frac"] for y in row] for x, row in zip(c[n:], r[n:])}
    assert set(iid) == set(cnd), f"{ctag}: arms cover different problems"
    return iid, cnd


def pass_at_k(fracs, k):
    n = len(fracs)
    c = sum(1 for f in fracs if f >= 1.0)
    if n - c < k:
        return 1.0
    return 1.0 - math.comb(n - c, k) / math.comb(n, k)


def reconstruct(targeting_file, powered_fn):
    """Rebuild a cell's artifact set with the frozen selector; verify against commit."""
    ch = json.loads((REPO / targeting_file).read_text())["chosen"]
    qids, pool = M._r3_donor_pool()
    sel = M._r3_select(pool, qids, powered_fn(), ch["target"], ch["hw"])
    arts = {q: c[1] for q, c in sel.items()}
    assert len(arts) == ch["n"], f"{targeting_file}: n {len(arts)} != {ch['n']}"
    got = round(st.mean(arts.values()), 4)
    assert got == ch["mean_art"], f"{targeting_file}: mean {got} != {ch['mean_art']}"
    return arts, ch


def sweep_powered(rung):
    g, r = load(f"j11_sweep_cand_{rung}"), load(f"j11_sweep_res_{rung}")
    return {x["qid"]: st.mean(c["frac"] for c in row) for x, row in zip(g, r)}


def fit(x, y, rng):
    mx, my = st.mean(x), st.mean(y)
    sxx = sum((xi - mx) ** 2 for xi in x)
    b = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / sxx
    a = my - b * mx
    sse = sum((yi - (a + b * xi)) ** 2 for xi, yi in zip(x, y))
    sst = sum((yi - my) ** 2 for yi in y)
    se_b = math.sqrt(sse / (len(x) - 2) / sxx)
    se_a = se_b * math.sqrt(sum(xi ** 2 for xi in x) / len(x))
    bs, as_ = [], []
    for _ in range(BOOT):
        idx = [rng.randrange(len(x)) for _ in x]
        bx, by = [x[i] for i in idx], [y[i] for i in idx]
        bmx, bmy = st.mean(bx), st.mean(by)
        bsxx = sum((xi - bmx) ** 2 for xi in bx)
        if bsxx <= 0:
            continue
        bb = sum((xi - bmx) * (yi - bmy) for xi, yi in zip(bx, by)) / bsxx
        bs.append(bb)
        as_.append(bmy - bb * bmx)
    bs.sort()
    as_.sort()
    q = lambda v, p: v[int(p * len(v))]  # noqa: E731
    return {"slope": b, "se_slope": se_b, "slope_ci": [q(bs, .025), q(bs, .975)],
            "intercept": a, "se_intercept": se_a,
            "intercept_ci": [q(as_, .025), q(as_, .975)],
            "r2": 1 - sse / sst, "n": len(x)}


# --------------------------------------------------------------- the four cells
print("=" * 84)
print("P0.5 — compression across sinking and clean cells  [PHASE_18.md P0]")
print("=" * 84)

m7 = json.loads((REPO / "artifacts/h7_matched_artifacts.json").read_text())
CELLS = []

# --- Phase 11 rungs (the powered at-match ladder): the two committed SINKS
for rung, tag, tfile in (("coder1p5b", "P11_coder1p5b", "artifacts/h11_targeting_coder1p5b.json"),
                         ("coder3b", "P11_coder3b", "artifacts/h11_targeting_coder3b.json")):
    a, ch = reconstruct(tfile, lambda r=rung: sweep_powered(r))
    lab = "Coder-1.5B" if rung == "coder1p5b" else "Coder-3B"
    CELLS.append((f"{lab} (P11)", "SINKS", "Coder",
                  *arms(f"j8_cand_{tag}", f"j8_res_{tag}"), a, ch["mean_art"]))

# --- Phase 10 R5: Coder-7B at TRUE match, where the sink is measured ABSENT
a7, ch7 = reconstruct("artifacts/h10_r5_targeting.json", lambda: M._r4_powered_map()[0])
CELLS.append(("Coder-7B (R5 true match)", "clean", "Coder",
              *arms("j8_cand_R5_coder7b_truematch0", "j8_res_R5_coder7b_truematch0"),
              a7, ch7["mean_art"]))

# --- Phase 7 matched-artifact battery: all five cells kept their pools
P7 = [("M1_deepseek1p3b", "DeepSeek-1.3B (P7 M1)", "clean", "non-Coder"),
      ("M2_general1p5b", "general-Qwen-1.5B (P7 M2) *TWIN*", "clean", "non-Coder"),
      ("M3_starcoder2_3b", "StarCoder2-3B (P7 M3)", "clean", "non-Coder"),
      ("M4_coder7b", "Coder-7B (P7 M4, retracted)", "clean", "Coder"),
      ("M5_coder0p5b", "Coder-0.5B (P7 M5) *OPEN*", "unadjudicated", "Coder")]
for key, lab, status, diet in P7:
    a = {x["qid"]: x["frac"] for x in m7["cells"][key]["artifacts"]}
    CELLS.append((lab, status, diet, *arms(f"j7_cand_{key}", f"j7_res_{key}"),
                  a, round(st.mean(a.values()), 4)))

rng = random.Random(SEED)
out, kcov = {}, 8

print(f"\n{'cell':<34} {'status':<14} {'n':>3} {'slope':>17} {'intercept':>19} {'R2':>6}")
print("-" * 100)
for name, status, diet, iid, cnd, art, mart in CELLS:
    qs = sorted(set(iid) & set(cnd) & set(art))
    x = [art[q] - st.mean(iid[q]) for q in qs]
    y = [st.mean(cnd[q]) - st.mean(iid[q]) for q in qs]
    f = fit(x, y, rng)
    ci, cc = (st.mean(pass_at_k(iid[q], kcov) for q in qs),
              st.mean(pass_at_k(cnd[q], kcov) for q in qs))
    n_perf = sum(1 for q in qs if art[q] >= 1.0)
    out[name] = {"status": status, "diet": diet, "n": len(qs), "mean_art": mart,
                 "mean_iid": round(st.mean(st.mean(iid[q]) for q in qs), 4),
                 "mean_cond": round(st.mean(st.mean(cnd[q]) for q in qs), 4),
                 "delta_art": round(st.mean(x), 4),
                 "fit": {k: ([round(z, 4) for z in v] if isinstance(v, list)
                             else round(v, 4)) for k, v in f.items()},
                 "coverage_k8": {"iid": round(ci, 4), "cond": round(cc, 4),
                                 "delta": round(cc - ci, 4)},
                 "artifacts_fully_passing": n_perf,
                 "copy_null_coverage": round(n_perf / len(qs), 4)}
    star = "  <" if "*" in name else ""
    print(f"{name:<34} {status:<14} {len(qs):>3} "
          f"{f['slope']:>+7.4f} [{f['slope_ci'][0]:+.2f},{f['slope_ci'][1]:+.2f}] "
          f"{f['intercept']:>+8.4f} [{f['intercept_ci'][0]:+.3f},{f['intercept_ci'][1]:+.3f}] "
          f"{f['r2']:>6.3f}{star}")

print("\nSLOPE  = how far conditioning pulls the model toward the artifact (1 = copy)")
print("INTERCEPT = the shift that remains when the artifact sits at the model's own")
print("            quality — i.e. the SINK, read off the law at gap = 0")

sinks = [n for n in out if out[n]["status"] == "SINKS"]
cleans = [n for n in out if out[n]["status"] == "clean"]
sink_s = [out[n]["fit"]["slope"] for n in sinks]
clean_s = [out[n]["fit"]["slope"] for n in cleans]
sink_i = [out[n]["fit"]["intercept"] for n in sinks]
clean_i = [out[n]["fit"]["intercept"] for n in cleans]
print(f"\n  slopes      SINKS {[round(v, 3) for v in sink_s]}   "
      f"clean {[round(v, 3) for v in clean_s]}")
print(f"  intercepts  SINKS {[round(v, 3) for v in sink_i]}   "
      f"clean {[round(v, 3) for v in clean_i]}")

sep_slope = min(sink_s) > max(clean_s) or max(sink_s) < min(clean_s)
sep_icept = max(sink_i) < min(clean_i) or min(sink_i) > max(clean_i)
print(f"\n  slope separates SINKS from clean:      {sep_slope}")
print(f"  intercept separates SINKS from clean:  {sep_icept}")

# the honest version: does each cell's own CI exclude zero?
print("\n  intercept CI95 vs zero, per cell (the claim is about SIGN, so test the sign):")
for n_, v in out.items():
    lo, hi = v["fit"]["intercept_ci"]
    verdict = "BELOW zero" if hi < 0 else "ABOVE zero" if lo > 0 else "includes zero"
    print(f"    {n_:<34} {v['fit']['intercept']:>+8.4f} "
          f"[{lo:+.3f},{hi:+.3f}]  {verdict}")

# copy-null coverage, all four cells: is the currency problem general?
print("\n" + "-" * 84)
print("copy-null coverage by cell (a partial-credit artifact scores 0 by construction)")
print("-" * 84)
for n_, v in out.items():
    print(f"  {n_:<26} artifacts fully passing {v['artifacts_fully_passing']:>2}/{v['n']:<3}"
          f" -> copy-null coverage {v['copy_null_coverage']:.4f}   "
          f"cov@8 iid {v['coverage_k8']['iid']:.3f} cond {v['coverage_k8']['cond']:.3f}")

(REPO / "artifacts/h18_p0_compress_battery.json").write_text(json.dumps(
    {"_label": "P0.5 free — compression law across 4 committed cells [PHASE_18.md P0]",
     "_model": "shift(q) = a + b*gap(q); shift = cond-iid, gap = artifact-iid, per problem",
     "seed": SEED, "boot": BOOT, "cells": out}, indent=2))
print("\nwrote artifacts/h18_p0_compress_battery.json")
