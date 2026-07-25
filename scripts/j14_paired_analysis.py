"""Phase 14 salvage analysis — the matched-K capability contrast.

The phase's pre-registered adjudication statistic is degenerate (see PHASE_14.md
RESULT): sink = perf - art with a single constant `art` shared by both arms, so
the RND curve in (perf, sink) space is the line y = x - art and interpolating it
at a TOP point's perf returns that point's own sink. Delta == 0 identically.

What is NOT degenerate is the comparison the curves were built from:
TOP-K vs RND-K *general capability* at matched dose K, paired by problem.
That is a capability result, not a sink result, and it is computed here with
paired SEs rather than eyeballed from the arm means.

Free/local: reads the cached run outputs, spends nothing.
"""
import json
import math
import pathlib
import statistics as st

REPO = pathlib.Path(__file__).resolve().parents[1]
RUNS = REPO / "runs/modal"


def load(name):
    return json.loads((RUNS / f"{name}.json").read_text())


def per_problem(cand_tag, res_tag):
    """qid -> mean pass-fraction over the arm's 8 candidates."""
    cand, res = load(cand_tag), load(res_tag)
    return {x["qid"]: st.mean(c["frac"] for c in row) for x, row in zip(cand, res)}


def paired(a, b, qids):
    """b - a over shared problems: mean, paired SE, t, two-sided p."""
    d = [b[q] - a[q] for q in qids]
    n = len(d)
    m = st.mean(d)
    sd = st.stdev(d) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n > 1 else float("nan")
    t = m / se if se else float("nan")
    # normal approximation; n=44 so the t/z difference is immaterial here
    p = math.erfc(abs(t) / math.sqrt(2)) if se else float("nan")
    return m, se, t, p, n


anchor = per_problem("j13_B1_cond_cand", "j13_B1_cond_res")
qids = sorted(anchor)

print(f"n = {len(qids)} problems, Coder-1.5B, HF path, seed 191\n")
print(f"{'K':>3} {'TOP':>8} {'RND':>8} {'RND-TOP':>9} {'SE':>7} {'t':>6} {'p':>9}")
print("-" * 54)

rows = []
for K in (1, 2, 4, 8):
    top = per_problem(f"j14_TOP{K}_cand", f"j14_TOP{K}_res")
    rnd = per_problem(f"j14_RND{K}_cand", f"j14_RND{K}_res")
    qs = [q for q in qids if q in top and q in rnd]
    m, se, t, p, n = paired(top, rnd, qs)
    tm, rm = st.mean(top[q] for q in qs), st.mean(rnd[q] for q in qs)
    rows.append((K, tm, rm, m, se, t, p, n))
    print(f"{K:>3} {tm:>8.4f} {rm:>8.4f} {m:>9.4f} {se:>7.4f} {t:>6.2f} {p:>9.2e}")

print("\nEach arm vs the unablated K=0 anchor (paired):")
print(f"{'arm':>7} {'mean':>8} {'vs K=0':>9} {'SE':>7} {'t':>6} {'p':>9}")
print("-" * 50)
a0 = st.mean(anchor[q] for q in qids)
print(f"{'K=0':>7} {a0:>8.4f}")
for arm in ("TOP", "RND"):
    for K in (1, 2, 4, 8):
        d = per_problem(f"j14_{arm}{K}_cand", f"j14_{arm}{K}_res")
        qs = [q for q in qids if q in d]
        m, se, t, p, n = paired(anchor, d, qs)
        print(f"{arm+str(K):>7} {st.mean(d[q] for q in qs):>8.4f} "
              f"{m:>9.4f} {se:>7.4f} {t:>6.2f} {p:>9.2e}")

out = {
    "_label": "Phase 14 salvage — matched-K capability contrast (paired) [PHASE_14.md]",
    "_note": ("The phase's pre-registered sink statistic is degenerate by construction; "
              "this file reports ONLY the general-capability contrast, which is not."),
    "n_problems": len(qids),
    "anchor_K0_perf": round(a0, 4),
    "matched_K": [
        {"K": K, "top_perf": round(tm, 4), "rnd_perf": round(rm, 4),
         "rnd_minus_top": round(m, 4), "paired_se": round(se, 4),
         "t": round(t, 2), "p": p, "n": n}
        for (K, tm, rm, m, se, t, p, n) in rows
    ],
}
(REPO / "artifacts/h14_matched_k_capability.json").write_text(json.dumps(out, indent=2))
print("\nwrote artifacts/h14_matched_k_capability.json")
