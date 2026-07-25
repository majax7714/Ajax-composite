"""P0 (free) — is Phase 13 S1's concentration finding a head-count artifact?

S1 reported that artifact attention is more CONCENTRATED in sinking models
(top-5% head share and Gini, tracking sink status across both size pairs) and
flagged its own caveat: the four architectures have different head counts
(12H / 16H / 28H per layer; 336 / 576 / 784 / 384 heads total) and neither
statistic is obviously invariant to how many heads it is computed over.

The caveat is worth taking seriously because head count is ALIGNED with the
contrast: the clean model has more heads than the sinking model in BOTH pairs
(1.5B 336 sink vs 1.3B 384 clean; 3B 576 sink vs 7B 784 clean). If either
statistic drifts downward with n, that alone could manufacture "tracks sink
status across both pairs."

This tests it on the committed matrices, with no new spend:
  (1) reproduce S1's published numbers;
  (2) subsample every model to a COMMON total head count and recompute;
  (3) subsample every model to a COMMON heads-per-layer and recompute;
  (4) re-apply S1's frozen both-pairs decision rule to each controlled variant.

Nothing here adjudicates a new claim; it audits an existing one on its own data.
"""
import json
import pathlib
import random
import statistics as st

REPO = pathlib.Path(__file__).resolve().parents[1]
S1 = json.loads((REPO / "artifacts/h13_s1_heads.json").read_text())

SINK = {"coder1p5b": True, "coder3b": True, "coder7b": False, "deepseek1p3b": False}
PAIRS = [("small", "coder1p5b", "deepseek1p3b"), ("large", "coder3b", "coder7b")]
SEED = 211
B = 2000


def gini(xs):
    xs = sorted(abs(x) for x in xs)
    n = len(xs)
    tot = sum(xs)
    if n == 0 or tot == 0:
        return 0.0
    cum = sum((i + 1) * x for i, x in enumerate(xs))
    return (2 * cum) / (n * tot) - (n + 1) / n


def top_share(xs, pct=0.05):
    xs = sorted(xs, reverse=True)
    k = max(1, int(round(len(xs) * pct)))
    tot = sum(xs)
    return sum(xs[:k]) / tot if tot else 0.0


mats = {k: v for k, v in S1["matrices"].items()}
flat = {k: [h for layer in v for h in layer] for k, v in mats.items()}

print("=" * 74)
print("(1) reproduce S1 as published (all heads)")
print("=" * 74)
print(f"{'model':>14} {'sink':>5} {'L':>3} {'H':>3} {'heads':>6} {'top5%':>8} {'gini':>8}")
pub = {}
for m, xs in flat.items():
    L, H = len(mats[m]), len(mats[m][0])
    g, t5 = gini(xs), top_share(xs)
    pub[m] = (t5, g)
    print(f"{m:>14} {str(SINK[m]):>5} {L:>3} {H:>3} {len(xs):>6} {t5:>8.4f} {g:>8.4f}")
    s1m = S1["models"][m]
    assert abs(s1m["gini"] - g) < 5e-3, (m, s1m["gini"], g)
    assert abs(s1m["top5pct_share"] - t5) < 5e-3, (m, s1m["top5pct_share"], t5)
print("  [reproduced S1's committed numbers to <0.005]")


def verdict(stat_by_model, label):
    """S1's frozen rule: an effect counts only if it tracks sink status in BOTH pairs."""
    deltas = {}
    for name, sink_m, clean_m in PAIRS:
        deltas[name] = stat_by_model[sink_m] - stat_by_model[clean_m]
    tracks = all(d > 0 for d in deltas.values())
    print(f"    {label:<26} small Δ {deltas['small']:+.4f}   large Δ {deltas['large']:+.4f}"
          f"   tracks: {'YES' if tracks else 'NO'}")
    return {"small": round(deltas["small"], 4), "large": round(deltas["large"], 4),
            "tracks": tracks}


print("\n  S1's decision rule on the published numbers:")
res = {"published": {
    "top5pct_share": verdict({m: pub[m][0] for m in pub}, "top-5% share"),
    "gini": verdict({m: pub[m][1] for m in pub}, "Gini"),
}}

print("\n" + "=" * 74)
print(f"(2) CONTROL A — common TOTAL head count (n={min(len(v) for v in flat.values())}"
      f", {B} subsamples, seed {SEED})")
print("=" * 74)
n_common = min(len(v) for v in flat.values())
rng = random.Random(SEED)
ctrlA = {}
print(f"{'model':>14} {'sink':>5} {'top5% mean':>11} {'[95% CI]':>18} {'gini mean':>10} {'[95% CI]':>18}")
for m, xs in flat.items():
    gs, ts = [], []
    for _ in range(B):
        s = rng.sample(xs, n_common)
        gs.append(gini(s))
        ts.append(top_share(s))
    gs.sort(); ts.sort()
    ctrlA[m] = (st.mean(ts), st.mean(gs))
    lo, hi = int(0.025 * B), int(0.975 * B)
    print(f"{m:>14} {str(SINK[m]):>5} {st.mean(ts):>11.4f} "
          f"[{ts[lo]:.4f},{ts[hi]:.4f}] {st.mean(gs):>10.4f} [{gs[lo]:.4f},{gs[hi]:.4f}]")
print("\n  S1's decision rule under CONTROL A:")
res["control_a_common_total"] = {
    "n_heads": n_common,
    "top5pct_share": verdict({m: ctrlA[m][0] for m in ctrlA}, "top-5% share"),
    "gini": verdict({m: ctrlA[m][1] for m in ctrlA}, "Gini"),
}

print("\n" + "=" * 74)
h_common = min(len(v[0]) for v in mats.values())
print(f"(3) CONTROL B — common HEADS PER LAYER (H={h_common}, {B} subsamples, seed {SEED})")
print("=" * 74)
rng = random.Random(SEED)
ctrlB = {}
print(f"{'model':>14} {'sink':>5} {'top5% mean':>11} {'[95% CI]':>18} {'gini mean':>10} {'[95% CI]':>18}")
for m, mat in mats.items():
    gs, ts = [], []
    for _ in range(B):
        s = [h for layer in mat for h in rng.sample(layer, h_common)]
        gs.append(gini(s))
        ts.append(top_share(s))
    gs.sort(); ts.sort()
    ctrlB[m] = (st.mean(ts), st.mean(gs))
    lo, hi = int(0.025 * B), int(0.975 * B)
    print(f"{m:>14} {str(SINK[m]):>5} {st.mean(ts):>11.4f} "
          f"[{ts[lo]:.4f},{ts[hi]:.4f}] {st.mean(gs):>10.4f} [{gs[lo]:.4f},{gs[hi]:.4f}]")
print("\n  S1's decision rule under CONTROL B:")
res["control_b_common_per_layer"] = {
    "heads_per_layer": h_common,
    "top5pct_share": verdict({m: ctrlB[m][0] for m in ctrlB}, "top-5% share"),
    "gini": verdict({m: ctrlB[m][1] for m in ctrlB}, "Gini"),
}

print("\n" + "=" * 74)
print("(4) does head count alone predict the statistic? (across all four models)")
print("=" * 74)
order = sorted(flat, key=lambda m: len(flat[m]))
print("  by total heads: " + "  ".join(
    f"{m}({len(flat[m])}) g={pub[m][1]:.4f}" for m in order))
mono = all(pub[order[i]][1] >= pub[order[i + 1]][1] for i in range(len(order) - 1))
print(f"  Gini monotonically decreasing in head count? {'YES' if mono else 'NO'}")
res["headcount_monotone_gini"] = mono

(REPO / "artifacts/h15_s1_headcount_control.json").write_text(json.dumps(
    {"_label": "P0 free — head-count control on Phase 13 S1 concentration [PHASE_15.md]",
     "_source": "artifacts/h13_s1_heads.json (committed per-head matrices)",
     "seed": SEED, "n_subsamples": B, "results": res}, indent=2))
print("\nwrote artifacts/h15_s1_headcount_control.json")
