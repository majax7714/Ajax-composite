"""Phase 6 P1 — the five-point size curve + free-rider fidelity/blend geometry,
and the pre-registered origin-branch call ([PHASE_6.md] P1). Pure CPU; reads the
committed D2c/language cells + raw pools. Runs incrementally (missing cells are
skipped with a note), so it can be re-run as the Modal battery lands.

Points (all Modal L4/bf16 — same stack, no re-baseline per the P1 decision):
  0.5B / 3B / general-1.5B : artifacts/h6_pathology_origin_<name>.json  (NEW)
  1.5B  : artifacts/dmeasure_d2c_partial_credit.json + h2_manip_check.json (record)
  7B    : artifacts/h5_7b_pathology.json                                   (record)

Code channel is normalised to (cond, iid, copy). The discriminating axis is
sink_margin = cond - copy: < 0 = SINK (below the artifact it conditions on),
> 0 = BLEND (pulled up toward own quality, the friendly regime). Free rider:
copy_fidelity = mean SequenceMatcher(E1 gen, artifact).ratio() (matches the 1.5B
method). Branch per the frozen P1 rule: SLOPE / STEP-OPEN / NON-MONOTONE /
0.5B-UNINFORMATIVE (code) x RECIPE-DEEP / CODER-STAGE (general-1.5B) -> MIXED if
code and language disagree.
"""
import difflib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

# order: (short, label, params_B, is_coder_line)
POINTS = [
    ("qwen05b", "Coder-0.5B", 0.5, True),
    ("qwen15b", "Coder-1.5B", 1.5, True),
    ("qwen3b", "Coder-3B", 3.0, True),
    ("qwen7b", "Coder-7B", 7.0, True),
    ("qwen15b_general", "general-1.5B", 1.5, False),
]


def _art(name):
    p = REPO / f"artifacts/{name}"
    return json.loads(p.read_text()) if p.exists() else None


def _fidelity_from_pool(pool_path):
    """mean SequenceMatcher(E1 gen, artifact code).ratio() over the E1 half."""
    from modal_h1 import _d2c_artifacts  # noqa: E402  (local import; needs `modal`)
    pool = _art_path(pool_path)
    if pool is None:
        return None
    arts = _d2c_artifacts()
    n = len(arts)
    e1 = pool[n:]
    sims = []
    for a, item in zip(arts, e1):
        for c in item["codes"]:
            if c:
                sims.append(difflib.SequenceMatcher(None, c, a["code"]).ratio())
    return sum(sims) / len(sims) if sims else None


def _art_path(rel):
    p = REPO / rel
    return json.loads(p.read_text()) if p.exists() else None


def _fidelity(name):
    """Uniform copy-fidelity; 1.5B uses its stored value (raw pool retired)."""
    if name == "qwen15b":
        d = _art("dmeasure_d2c_partial_credit.json")
        return d.get("copy_fidelity_mean_similarity") if d else None
    pool_rel = ("runs/modal/j5_q1a_cand.json" if name == "qwen7b"
                else f"runs/modal/j6_q1a_cand_{name}.json")
    try:
        return _fidelity_from_pool(pool_rel)
    except Exception:
        return None  # `modal` import or missing pool — fidelity is a free rider


def _load_point(name):
    """-> dict(cond, iid, copy, p_below_iid, p_below_copy, lang_e0, lang_hint,
    lang_uplift) or None if the cell has not landed."""
    if name == "qwen15b":
        c = _art("dmeasure_d2c_partial_credit.json")
        lang = _art("h2_manip_check.json")
        if not c:
            return None
        d = {"cond": c["mean_frac_generated"], "iid": c["mean_iid_null"],
             "copy": c["mean_copy_null"],
             "p_below_copy": c["p_one_sided_sink"],
             "p_below_iid": 1.0 - c["p_one_sided_vs_iid_null"]}
    else:
        art = (_art("h5_7b_pathology.json") if name == "qwen7b"
               else _art(f"h6_pathology_origin_{name}.json"))
        if not art:
            return None
        q = art["q1a_d2c"]
        d = {"cond": q["e1_mean_frac_cond"], "iid": q["e0_mean_frac_iid"],
             "copy": q["copy_null_mean"],
             "p_below_copy": q["p_one_sided_cond_below_copy"],
             "p_below_iid": q["p_one_sided_cond_below_iid"]}
        lang = {"e0_mean_pass": art["q1b_language"]["e0_mean_pass"],
                "hint_mean_pass": art["q1b_language"]["hint_mean_pass"],
                "mean_uplift": art["q1b_language"]["mean_uplift"]} if "q1b_language" in art else None
    d["sink_margin"] = d["cond"] - d["copy"]
    d["delta_iid"] = d["cond"] - d["iid"]
    d["below_both"] = (d["cond"] < d["copy"]) and (d["cond"] < d["iid"])
    d["sink_sig"] = d["p_below_copy"] < 0.05 and d["p_below_iid"] < 0.05
    d["klass"] = ("SINK" if d["below_both"] and d["sink_sig"] else
                  "BLEND" if d["cond"] < max(d["copy"], d["iid"]) else "CLIMB")
    if lang:
        d["lang_e0"] = lang["e0_mean_pass"]
        d["lang_hint"] = lang["hint_mean_pass"]
        d["lang_uplift"] = lang["mean_uplift"]
    d["fidelity"] = _fidelity(name)
    return d


def main():
    rows = {}
    for name, label, pb, coder in POINTS:
        d = _load_point(name)
        rows[name] = (label, pb, coder, d)

    print(f"{'checkpoint':16s} {'cond':>6s} {'iid':>6s} {'copy':>6s} "
          f"{'sink_m':>7s} {'class':>6s} {'fidel':>6s} {'lang_dpass':>10s}")
    print("-" * 74)
    coder = []
    for name, (label, pb, is_coder, d) in rows.items():
        if d is None:
            print(f"{label:16s}  (cell not landed)")
            continue
        lang = f"{d.get('lang_uplift'):+.3f}" if d.get("lang_uplift") is not None else "  n/a"
        fid = f"{d['fidelity']:.3f}" if d.get("fidelity") is not None else "  n/a"
        print(f"{label:16s} {d['cond']:6.3f} {d['iid']:6.3f} {d['copy']:6.3f} "
              f"{d['sink_margin']:+7.3f} {d['klass']:>6s} {fid:>6s} {lang:>10s}")
        if is_coder:
            coder.append((pb, name, d))

    # --- branch determination over the Coder line (0.5/1.5/3/7B) ---
    coder.sort()
    landed = [(pb, n, d) for pb, n, d in coder if d is not None]
    verdict = {"code_branch": "INCOMPLETE (need all Coder cells)"}
    if len(landed) == 4:
        margins = [d["sink_margin"] for _, _, d in landed]  # 0.5,1.5,3,7
        klasses = [d["klass"] for _, _, d in landed]
        mono = all(margins[i] <= margins[i + 1] + 1e-9 for i in range(3))
        three_interm = margins[1] < margins[2] < margins[3]  # 1.5 < 3 < 7
        step = (klasses[0] == klasses[1] == klasses[2] == "SINK"
                and klasses[3] != "SINK")
        b05_ok = rows["qwen05b"][3] is not None
        if not b05_ok:
            code = "0.5B-UNINFORMATIVE"
        elif mono and three_interm:
            code = "SLOPE -> H-capacity x diet (the synthetic tax)"
        elif step:
            code = "STEP-OPEN (H-tie demoted at P0; bundled 3B->7B discontinuity)"
        elif not mono:
            code = "NON-MONOTONE (checkpoint-specific)"
        else:
            code = "AMBIGUOUS (monotone but 3B not clearly intermediate)"
        verdict["code_branch"] = code
        verdict["coder_sink_margins_0.5_1.5_3_7"] = [round(m, 4) for m in margins]
        verdict["coder_classes"] = klasses

    # --- recipe locus (general-1.5B vs Coder-1.5B) ---
    g = rows["qwen15b_general"][3]
    c15 = rows["qwen15b"][3]
    if g and c15:
        verdict["recipe_branch"] = (
            "RECIPE-DEEP (general-1.5B sinks like Coder-1.5B)" if g["klass"] == "SINK"
            else "CODER-STAGE (general-1.5B blends; the Coder diet did it)")
        verdict["general_vs_coder_1.5B_class"] = [g["klass"], c15["klass"]]

    # --- cross-channel MIXED check ---
    code_sink = [d for _, _, d in landed if d["klass"] == "SINK"]
    lang_harm = [n for n, (_, _, _, d) in rows.items()
                 if d and d.get("lang_uplift") is not None and d["lang_uplift"] < -0.05]
    verdict["note_channels"] = (
        f"code SINK at {len(code_sink)} coder pts; language harm (<-0.05) at "
        f"{lang_harm} — inspect for MIXED if they disagree on the boundary")

    print("\n=== BRANCH ===")
    for k, v in verdict.items():
        print(f"  {k}: {v}")
    out = {"_label": "Phase 6 P1 size curve + origin branch [PHASE_6.md P1]",
           "points": {n: (rows[n][3] or "not landed") for n, *_ in
                      [(p[0],) for p in POINTS]},
           "verdict": verdict}
    (REPO / "artifacts/h6_size_curve.json").write_text(json.dumps(out, indent=2, default=str))
    print("\nwrote artifacts/h6_size_curve.json")


if __name__ == "__main__":
    main()
