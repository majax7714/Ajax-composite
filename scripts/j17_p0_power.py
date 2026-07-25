"""P0 (free) — power the verb contrast from its MEASURED k-scaling, not a model.

Phase 16 closed INCONCLUSIVE because a validity threshold was a round number
against a quantity whose committed CI is 0.123 wide (§8 entry 9). Its substantive
contrast near-missed: Coder-1.5B Delta(B-A) = -0.0336 +/- 0.0176, p 0.0562 (n=44, k=8).

A first attempt at this analysis decomposed var(d_q) into between-problem and
candidate-sampling terms analytically, assuming the two verb arms are independent
given the problem. THAT ASSUMPTION IS FALSE and the arithmetic said so: the implied
within-problem term came out at 123% (Coder) and 347% (DeepSeek) of the observed
variance. Both arms were generated at the SAME seed (233) from prompts differing in
one clause, and §8's seed-policy caveat records that same-seed vLLM regeneration
reproduces 45-50% of a pool byte-for-byte. The arms are positively correlated, which
is exactly what pairing is for -- but it invalidates the independent decomposition.

So measure the k-dependence directly instead: subsample k' of the 8 committed
candidates per arm, recompute the paired SE, and fit SE^2(k) = a + b/k on real data.
No independence assumption is needed because the subsamples inherit whatever
correlation the arms actually have.

Free: reads the committed Phase 16 arms, spends nothing.
"""
import json
import math
import pathlib
import random
import statistics as st

REPO = pathlib.Path(__file__).resolve().parents[1]
RUNS = REPO / "runs/modal"

CELLS = [("coder1p5b", "SINKS"), ("deepseek1p3b", "clean")]
SEED = 241
REPS = 400
Z_A, Z_B = 1.959963985, 0.8416212336      # alpha .05 two-sided, 80% power


def load(tag):
    p = RUNS / f"{tag}.json"
    return json.loads(p.read_text()) if p.exists() else None


def arm(rung, verb):
    c, r = load(f"j16_{rung}_{verb}_cand"), load(f"j16_{rung}_{verb}_res")
    assert c and r, f"missing j16_{rung}_{verb}_*"
    return {x["qid"]: [y["frac"] for y in row] for x, row in zip(c, r)}


def se_at_k(A, B, qs, kk, rng, reps=REPS):
    """Empirical paired SE using kk of the 8 committed candidates per arm."""
    acc = []
    for _ in range(reps):
        d = [st.mean(rng.sample(B[q], kk)) - st.mean(rng.sample(A[q], kk)) for q in qs]
        acc.append(st.variance(d) / len(qs))
    return math.sqrt(st.mean(acc))


print("=" * 80)
print("P0 — empirical k-scaling of the verb contrast (Phase 16 committed arms)")
print("=" * 80)

out = {}
for rung, status in CELLS:
    A, B = arm(rung, "A"), arm(rung, "B")
    qs = sorted(set(A) & set(B))
    n = len(qs)
    rng = random.Random(SEED)
    d8 = [st.mean(B[q]) - st.mean(A[q]) for q in qs]
    eff = st.mean(d8)
    se8 = math.sqrt(st.variance(d8) / n)
    print(f"\n--- {rung} ({status})  n={n} ---")
    print(f"  observed at k=8: mean d {eff:+.4f}  SE {se8:.4f}  "
          f"p {math.erfc(abs(eff / se8) / math.sqrt(2)):.4f}")

    ks = [2, 3, 4, 6, 8]
    ses = [se_at_k(A, B, qs, kk, rng) for kk in ks]
    print(f"  measured SE by candidates-per-problem (subsampled, {REPS} reps):")
    for kk, s in zip(ks, ses):
        print(f"      k={kk:<2d}  SE {s:.4f}")

    # least squares on SE^2 = a + b*(1/k)
    x = [1.0 / kk for kk in ks]
    y = [s ** 2 for s in ses]
    mx, my = st.mean(x), st.mean(y)
    b = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / sum((xi - mx) ** 2 for xi in x)
    a = my - b * mx
    a = max(a, 0.0)
    print(f"  fit SE^2 = {a:.6f} + {b:.6f}/k   "
          f"(irreducible SE as k->inf: {math.sqrt(a):.4f})")

    def se_kn(kk, nn):
        return math.sqrt((a + b / kk) * n / nn)

    print(f"  projected SE and power for the observed effect {eff:+.4f}:")
    print(f"      {'k':>4} {'SE@n=' + str(n):>12} {'|t|':>7} {'n for 80%':>11}")
    proj = {}
    for kk in (8, 16, 24, 32, 48):
        s = se_kn(kk, n)
        need = math.ceil(((Z_A + Z_B) ** 2) * (a + b / kk) * n / (eff ** 2))
        feas = "  <-- feasible at n=%d" % n if need <= n else ""
        print(f"      {kk:>4} {s:>12.4f} {abs(eff) / s:>7.2f} {need:>11d}{feas}")
        proj[str(kk)] = {"se_at_n": round(s, 5), "abs_t": round(abs(eff) / s, 3),
                         "n_for_80pct": need}
    out[rung] = {"n": n, "effect_k8": round(eff, 5), "se_k8": round(se8, 5),
                 "measured_se_by_k": {str(kk): round(s, 5) for kk, s in zip(ks, ses)},
                 "fit": {"a": round(a, 8), "b": round(b, 8),
                         "irreducible_se": round(math.sqrt(a), 5)},
                 "projection": proj}

print("\n" + "=" * 80)
print("CI-referenced validity conditions (replacing Phase 16's round number)")
print("=" * 80)
p11 = json.loads((REPO / "artifacts/h11_coder1p5b.json").read_text())["cell"]
m1 = json.loads((REPO / "artifacts/h7_matched_M1_deepseek1p3b.json").read_text())
h16 = json.loads((REPO / "artifacts/h16_verb_battery.json").read_text())
ci = {"coder1p5b": p11["delta_cond_minus_iid_ci95"],
      "deepseek1p3b": m1["delta_cond_minus_iid_ci95"]}
for rung in ("coder1p5b", "deepseek1p3b"):
    v = h16["cells"][rung]["verbs"]["A"]["sink_vs_iid"]
    lo, hi = ci[rung]
    print(f"  {rung:14s} committed CI95 [{lo:+.4f},{hi:+.4f}] width {hi - lo:.4f}   "
          f"P16 VERB-A {v:+.4f} -> inside? {'YES' if lo <= v <= hi else 'NO'}")

(REPO / "artifacts/h17_p0_power.json").write_text(json.dumps(
    {"_label": "P0 free — empirical k-scaling + power for the verb contrast [PHASE_17.md P0]",
     "_method": ("subsample k of 8 committed candidates per arm, recompute paired SE, "
                 "fit SE^2 = a + b/k; no independence assumption between arms"),
     "_superseded": ("an earlier analytic decomposition assuming independent arms was "
                     "discarded: it implied within-problem shares of 123%/347%, which is "
                     "impossible and reflects same-seed correlation between the arms"),
     "seed": SEED, "reps": REPS, "cells": out, "committed_ci": ci}, indent=2))
print("\nwrote artifacts/h17_p0_power.json")
