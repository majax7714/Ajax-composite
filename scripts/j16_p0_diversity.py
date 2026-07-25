"""P0.2 (free) — decompose committed sink cells into per-sample quality vs diversity.

Two things this settles, both on data already committed, with no GPU:

(1) The record states claim 6 (escape law) as a coverage/diversity effect and claim 8
    (the SINK) as a mean-frac effect. An outside charter read these as contradictory.
    They are not — D2b's "flat ~0.20" is flat across TEMPERATURE within a conditioned
    arm (E0 i.i.d. 0.65 -> E1 conditioned 0.20 is a large per-sample drop) — but the
    record has still never decomposed a SINK cell on the coverage/diversity axis.

(2) H-COLLAPSE (the Coder diet narrowed the conditional distribution; the sink is
    support contraction) vs H-ARB (two comparably-weighted policies interfere; the
    mixture spreads) dissociate on candidate-set diversity in the conditioned arm:
    H-COLLAPSE predicts diversity << i.i.d., H-ARB predicts diversity >= i.i.d.

Structural canonicalization via Python's own ast (normalized dump, attributes off),
falling back to whitespace/comment-stripped text when a candidate does not parse —
which is itself reported, since parse rate is a quality signal.
"""
import ast
import json
import pathlib
import statistics as st

REPO = pathlib.Path(__file__).resolve().parents[1]
RUNS = REPO / "runs/modal"

# (label, sink status, cand tag, res tag, n_problems)
CELLS = [
    ("Coder-1.5B (P11)", "SINKS", "j8_cand_P11_coder1p5b", "j8_res_P11_coder1p5b", 44),
    ("Coder-3B (P11)", "SINKS", "j8_cand_P11_coder3b", "j8_res_P11_coder3b", 39),
    ("Coder-7B (R5 true match)", "clean",
     "j8_cand_R5_coder7b_truematch0", "j8_res_R5_coder7b_truematch0", 29),
    ("DeepSeek-1.3B (P7 M1)", "clean",
     "j7_cand_M1_deepseek1p3b", "j7_res_M1_deepseek1p3b", 39),
]


def load(tag):
    p = RUNS / f"{tag}.json"
    return json.loads(p.read_text()) if p.exists() else None


def canon(code):
    """Structural key for a candidate; (key, parsed?)."""
    if not code:
        return "", False
    try:
        return ast.dump(ast.parse(code), annotate_fields=True,
                        include_attributes=False), True
    except SyntaxError:
        lines = [ln.split("#")[0].rstrip() for ln in code.splitlines()]
        return "\n".join(ln for ln in lines if ln.strip()), False


def arm_stats(cand, res):
    """Per-arm: mean frac, coverage, distinct/8, max-cluster share, parse rate."""
    fracs, cov, distinct, maxclus, parsed = [], 0, [], [], []
    for c, row in zip(cand, res):
        f = [x["frac"] for x in row]
        fracs.append(st.mean(f))
        cov += 1 if any(x.get("passed") for x in row) else 0
        keys, ok = [], 0
        for code in c["codes"]:
            k, p = canon(code or "")
            keys.append(k)
            ok += p
        parsed.append(ok / len(c["codes"]))
        counts = {}
        for k in keys:
            counts[k] = counts.get(k, 0) + 1
        distinct.append(len(counts))
        maxclus.append(max(counts.values()) / len(keys))
    n = len(fracs)
    return {"n": n, "mean_frac": st.mean(fracs), "coverage": cov / n,
            "distinct_mean": st.mean(distinct), "max_cluster_share": st.mean(maxclus),
            "parse_rate": st.mean(parsed)}


print("=" * 96)
print("P0.2 — sink cells decomposed: per-sample quality vs diversity (i.i.d. arm vs conditioned arm)")
print("=" * 96)
print(f"{'cell':>26} {'arm':>5} {'meanfrac':>9} {'cover':>7} {'distinct/8':>11} "
      f"{'maxclust':>9} {'parse':>7}")

out = {}
for label, status, ctag, rtag, n in CELLS:
    cand, res = load(ctag), load(rtag)
    if not cand or not res:
        print(f"{label:>26}  -- caches missing ({ctag}) --")
        continue
    if len(cand) < 2 * n:
        print(f"{label:>26}  -- pool shorter than 2x{n} ({len(cand)}) --")
        continue
    iid = arm_stats(cand[:n], res[:n])
    cond = arm_stats(cand[n:2 * n], res[n:2 * n])
    out[label] = {"status": status, "iid": iid, "cond": cond,
                  "delta_distinct": round(cond["distinct_mean"] - iid["distinct_mean"], 4),
                  "delta_coverage": round(cond["coverage"] - iid["coverage"], 4),
                  "delta_mean_frac": round(cond["mean_frac"] - iid["mean_frac"], 4)}
    for arm, s in (("iid", iid), ("cond", cond)):
        print(f"{label if arm == 'iid' else '':>26} {arm:>5} {s['mean_frac']:>9.4f} "
              f"{s['coverage']:>7.3f} {s['distinct_mean']:>11.2f} "
              f"{s['max_cluster_share']:>9.3f} {s['parse_rate']:>7.3f}")

print("\n" + "=" * 96)
print("The discriminator — conditioned-minus-i.i.d. change in candidate diversity")
print("  H-COLLAPSE predicts strongly NEGATIVE in sink cells; H-ARB predicts >= 0")
print("=" * 96)
print(f"{'cell':>26} {'status':>7} {'d mean_frac':>12} {'d coverage':>11} {'d distinct/8':>13}")
for label, v in out.items():
    print(f"{label:>26} {v['status']:>7} {v['delta_mean_frac']:>+12.4f} "
          f"{v['delta_coverage']:>+11.3f} {v['delta_distinct']:>+13.2f}")

(REPO / "artifacts/h16_p0_diversity.json").write_text(json.dumps(
    {"_label": "P0.2 free — sink cells decomposed on quality vs diversity [PHASE_16.md P0.2]",
     "_canon": "python ast.dump(annotate_fields=True, include_attributes=False)",
     "cells": out}, indent=2))
print("\nwrote artifacts/h16_p0_diversity.json")
