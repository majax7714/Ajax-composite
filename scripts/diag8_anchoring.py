#!/usr/bin/env python3
"""DIAG-8 — anchoring (content) vs prompt degradation (format) in the B2 text channel.

Pre-registered in docs/DIAGNOSTICS.md (committed 2026-07-13, before this ran).
EXPLORATORY / POST-HOC re-analysis of committed artifacts only. Does NOT reopen the
H2 gate.

DIAG-7 found pool coverage degrades monotonically in channel bandwidth but couldn't
separate two mechanisms: (a) anchoring — G produces variations on the failed
candidate it was shown; (b) prompt degradation — G just generates worse under the
unfamiliar longer prompt, regardless of content. Edit distance separates them:

  d_consec  = B2 adjacent pairs dist(code[i], code[i-1]), i=1..7  (anchored transitions)
  d_b2_all  = B2 all C(8,2) pairs      (B2 intrinsic-diversity control)
  d_b1_all  = B1 all C(8,2) pairs      (i.i.d. baseline)

Anchoring  <=> d_consec < d_b1_all AND d_consec < d_b2_all.
Degradation <=> d_consec ~= d_b2_all ~= d_b1_all (no extra clustering), B2 just worse.

Metric = 1 - difflib.SequenceMatcher(None,a,b).ratio(), identical to DIAG-3.
"""
from __future__ import annotations

import difflib
import json
import sys
from itertools import combinations
from pathlib import Path

REPO = Path(__file__).parents[1]
sys.path.insert(0, str(REPO / "src"))
from rgr.results import read_jsonl  # noqa: E402

FULL_B1 = REPO / "runs/phase2/full_b1.jsonl"
B2 = REPO / "runs/phase2/b2.jsonl"
OUT = REPO / "artifacts/diag8_anchoring.json"


def dist(a: str, b: str) -> float:
    return 1.0 - difflib.SequenceMatcher(None, a, b).ratio()


def codes(rec: dict) -> list:
    # None for no_code steps (model emitted no extractable code); kept as None so
    # the primary metric can drop degenerate empty-string pairs.
    return [s["code"] for s in rec["steps"]]


def mean(xs: list) -> float:
    return sum(xs) / len(xs) if xs else float("nan")


def consec_dists(cs: list, coerce: bool) -> list:
    out = []
    for i in range(1, len(cs)):
        a, b = cs[i], cs[i - 1]
        if coerce:
            out.append(dist(a or "", b or ""))
        elif a is not None and b is not None:
            out.append(dist(a, b))
    return out


def pair_dists(cs: list, coerce: bool) -> list:
    out = []
    for a, b in combinations(cs, 2):
        if coerce:
            out.append(dist(a or "", b or ""))
        elif a is not None and b is not None:
            out.append(dist(a, b))
    return out


def main() -> None:
    rows = read_jsonl(FULL_B1)
    b1 = {r["problem_id"]: r for r in rows if r["condition"] == "b1"}
    b2 = {r["problem_id"]: r for r in read_jsonl(B2) if r["condition"] == "b2"}
    pids = sorted(set(b1) & set(b2))

    def aggregate(coerce: bool) -> dict:
        consec, b2_all, b1_all = [], [], []       # per-problem means
        consec_lt_b2 = 0                          # problems where adjacent < B2 all-pairs
        n_c = 0
        for p in pids:
            cb2, cb1 = codes(b2[p]), codes(b1[p])
            dc, d2, d1 = consec_dists(cb2, coerce), pair_dists(cb2, coerce), pair_dists(cb1, coerce)
            m_c = mean(dc) if dc else None
            m_2 = mean(d2) if d2 else None
            m_1 = mean(d1) if d1 else None
            if m_c is not None:
                consec.append(m_c); n_c += 1
            if m_2 is not None:
                b2_all.append(m_2)
            if m_1 is not None:
                b1_all.append(m_1)
            if m_c is not None and m_2 is not None and m_c < m_2:
                consec_lt_b2 += 1
        d_consec, d_b2_all, d_b1_all = mean(consec), mean(b2_all), mean(b1_all)
        anchoring = d_consec < d_b1_all and d_consec < d_b2_all
        return {
            "d_consec_B2_adjacent": d_consec,
            "d_b2_all_pairs": d_b2_all,
            "d_b1_all_pairs_iid": d_b1_all,
            "ratio_consec_over_b1_iid": d_consec / d_b1_all if d_b1_all else None,
            "ratio_consec_over_b2_all": d_consec / d_b2_all if d_b2_all else None,
            "problems_consec_tighter_than_b2_allpairs": consec_lt_b2,
            "problems_with_valid_consec": n_c,
            "verdict_anchoring": anchoring,
        }

    primary = aggregate(coerce=False)   # drop degenerate empty (no_code) pairs
    coerced = aggregate(coerce=True)    # None -> "" sensitivity (no_code stays in)
    result = {
        "_label": "EXPLORATORY / POST-HOC — does not reopen the H2 gate",
        "n_problems": len(pids),
        "metric": "1 - difflib.SequenceMatcher(None,a,b).ratio() on extracted code (== DIAG-3)",
        "predicted": "partial anchoring: d_consec ~= 0.75 * d_b1_all, < d_b2_all",
        "primary_real_code_only": primary,
        "sensitivity_coerce_no_code_to_empty": coerced,
        "verdict": ("anchoring (content)" if primary["verdict_anchoring"]
                    else "prompt degradation (format) or mixed"),
    }
    OUT.write_text(json.dumps(result, indent=2))

    print(f"=== DIAG-8 anchoring vs degradation ({len(pids)} problems) ===")
    for tag, r in [("PRIMARY (real code only)", primary),
                   ("SENSITIVITY (no_code->'')", coerced)]:
        print(f"\n-- {tag} --")
        print(f"d_consec (B2 adjacent)   = {r['d_consec_B2_adjacent']:.3f}")
        print(f"d_b2_all (B2 all-pairs)  = {r['d_b2_all_pairs']:.3f}   (DIAG-3 within-r0 0.252 / within-r7 0.297 ref)")
        print(f"d_b1_all (B1 i.i.d.)     = {r['d_b1_all_pairs_iid']:.3f}")
        print(f"ratio consec/b1_iid      = {r['ratio_consec_over_b1_iid']:.3f}  (pred ~0.75)")
        print(f"ratio consec/b2_all      = {r['ratio_consec_over_b2_all']:.3f}")
        print(f"B2 adjacent tighter than its own all-pairs in "
              f"{r['problems_consec_tighter_than_b2_allpairs']}/{r['problems_with_valid_consec']} problems")
    print(f"\nVERDICT (primary): {result['verdict']}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
