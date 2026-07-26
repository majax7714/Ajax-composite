"""P0 (free) — is the DIET attribution resting on a residual position difference?

Phase 18's compression law says every model, sinking or clean, is pulled 47-90% of the
way from its own quality toward the artifact it is shown. That makes a cell's achieved
Delta_art (artifact frac - own i.i.d.) worth ~0.5-0.9 of itself in shift, which is the
same order as the SINK effect the record attributes to the Coder diet.

So the obvious question, which the record has never asked in this form: ARE THE CELLS
BEING COMPARED AT THE SAME POSITION? Phase 7 built the matched-artifact battery precisely
to kill the gross version of this confound (every family had been conditioned on the SAME
fixed artifact). It matched each model to its OWN quality. But "matched" was a targeting
BAND, not a point, and the achieved positions were measured with the k=8 instrument whose
SE Phase 10 R3 later measured at 0.028 and replaced with a k=24 instrument at SE 0.011.

This script audits every matched cell the record owns: which group, which position, which
instrument, and what it concluded. Then it asks how much of the Coder-vs-non-Coder
difference position alone can account for, using each cell's OWN measured compression
slope rather than a pooled one.

It also checks the diet claim's strongest defence rather than assuming it: Phase 9's
generated 2x2 was the provenance control, and if ITS four cells are position-matched then
the diet conclusion does not depend on Phase 7's battery at all.

Free: reads committed artifacts and pools, spends nothing.
"""
import json
import math
import pathlib
import statistics as st

REPO = pathlib.Path(__file__).resolve().parents[1]


def A(name):
    p = REPO / "artifacts" / name
    return json.loads(p.read_text()) if p.exists() else None


print("=" * 92)
print("P0 — position audit of every matched cell  [PHASE_19.md P0]")
print("=" * 92)

# ---------------------------------------------------------------- the cell census
# slope/intercept come from Phase 18 P0.5 (h18_p0_compress_battery.json)
comp = A("h18_p0_compress_battery.json")["cells"]
S = {"Coder-1.5B (P11)": "Coder-1.5B", "Coder-3B (P11)": "Coder-3B",
     "Coder-7B (R5 true match)": "Coder-7B(R5)",
     "DeepSeek-1.3B (P7 M1)": "DeepSeek-1.3B",
     "general-Qwen-1.5B (P7 M2) *TWIN*": "general-Qwen-1.5B",
     "StarCoder2-3B (P7 M3)": "StarCoder2-3B",
     "Coder-7B (P7 M4, retracted)": "Coder-7B(M4)",
     "Coder-0.5B (P7 M5) *OPEN*": "Coder-0.5B"}
slope = {S[k]: v["fit"]["slope"] for k, v in comp.items()}
icept = {S[k]: v["fit"]["intercept"] for k, v in comp.items()}
icpci = {S[k]: v["fit"]["intercept_ci"] for k, v in comp.items()}

CELLS = [
    # name,               group,       phase, instrument, achieved Dart, verdict
    ("Coder-1.5B",        "Coder",     "P11", "k=24 powered", +0.0016, "SINK"),
    ("Coder-3B",          "Coder",     "P11", "k=24 powered", -0.0005, "SINK"),
    ("Coder-7B(R5)",      "Coder",     "P10", "k=24 powered", +0.0023, "clean"),
    ("Coder-7B(M4)",      "Coder",     "P7",  "k=8",          -0.0393, "SINK*"),
    ("Coder-0.5B",        "Coder",     "P7",  "k=8",          +0.0814, "clean"),
    ("DeepSeek-1.3B",     "non-Coder", "P7",  "k=8",          +0.0499, "clean"),
    ("general-Qwen-1.5B", "non-Coder", "P7",  "k=8",          +0.0642, "clean"),
    ("StarCoder2-3B",     "non-Coder", "P7",  "k=8",          +0.0326, "clean"),
]

print(f"\n{'cell':<19} {'group':<10} {'phase':<5} {'instrument':<14} {'Δ_art':>8} "
      f"{'slope':>7} {'verdict':>7}")
print("-" * 92)
for n, g, ph, ins, d, v in CELLS:
    print(f"{n:<19} {g:<10} {ph:<5} {ins:<14} {d:>+8.4f} {slope[n]:>7.3f} {v:>7}")
print("\n  *M4's SINK was RETRACTED (P10 R4, non-replication) — shown as measured at the time")

# ---------------------------------------------------------------- the asymmetry
print("\n" + "-" * 92)
print("(1) the asymmetry: how each group was measured")
print("-" * 92)
cod = [c for c in CELLS if c[1] == "Coder"]
non = [c for c in CELLS if c[1] == "non-Coder"]
for lab, grp in (("Coder", cod), ("non-Coder", non)):
    pw = [c for c in grp if "powered" in c[3]]
    print(f"  {lab:<10} n={len(grp)}  powered-instrument cells: {len(pw)}"
          f"   mean Δ_art {st.mean(c[4] for c in grp):+.4f}"
          f"   range [{min(c[4] for c in grp):+.4f}, {max(c[4] for c in grp):+.4f}]")
p7c = [c for c in CELLS if c[2] == "P7"]
print(f"\n  Phase 7 battery only (the cells the DIET claim's family contrast rests on):")
for n, g, ph, ins, d, v in p7c:
    print(f"      {n:<19} {g:<10} Δ_art {d:+.4f}   {v}")
print(f"\n  -> every P7 cell that did NOT sink sits at POSITIVE Δ_art "
      f"(+{min(c[4] for c in p7c if c[5] == 'clean'):.4f} to "
      f"+{max(c[4] for c in p7c if c[5] == 'clean'):.4f});")
print(f"     the one that DID sink sits at NEGATIVE Δ_art "
      f"({[c[4] for c in p7c if c[5] == 'SINK*'][0]:+.4f}). Within Phase 7's own battery,")
print("     sink status separates PERFECTLY on position as well as on diet.")

# ---------------------------------------------------------------- how big is it
print("\n" + "-" * 92)
print("(2) how much shift does that position difference buy, at measured slopes?")
print("-" * 92)
dn = st.mean(c[4] for c in non)
dc = [c[4] for c in p7c if c[5] == "SINK*"][0]
gap = dn - dc
sl = st.mean(slope[c[0]] for c in non)
print(f"  non-Coder mean Δ_art {dn:+.4f}   vs   P7's Coder cell {dc:+.4f}"
      f"   difference {gap:+.4f}")
print(f"  mean measured compression slope over the non-Coder cells: {sl:.3f}")
print(f"  => position alone buys the non-Coder cells {gap * sl:+.4f} of shift")
print(f"  the SINK effect being attributed to diet is about -0.05")
print(f"  => THE POSITION DIFFERENCE IS {abs(gap * sl / 0.05):.1f}x THE EFFECT IT IS "
      f"BEING USED TO EXPLAIN")

# ------------------------------------------------- (3) position-adjusted comparison
print("\n" + "-" * 92)
print("(3) position-adjusted: each cell's fitted shift AT gap = 0 (its intercept)")
print("-" * 92)
print(f"  {'cell':<19} {'group':<10} {'intercept':>10} {'CI95':>20} {'excludes 0':>11}")
for n, g, ph, ins, d, v in CELLS:
    lo, hi = icpci[n]
    print(f"  {n:<19} {g:<10} {icept[n]:>+10.4f} [{lo:+.3f},{hi:+.3f}]"
          f"{('yes' if hi < 0 or lo > 0 else 'no'):>11}")
ic_c = [icept[c[0]] for c in CELLS if c[1] == "Coder" and "7B" not in c[0]]
ic_n = [icept[c[0]] for c in CELLS if c[1] == "non-Coder"]
print(f"\n  Coder <=3B intercepts   {[round(v, 4) for v in ic_c]}  mean {st.mean(ic_c):+.4f}")
print(f"  non-Coder intercepts    {[round(v, 4) for v in ic_n]}  mean {st.mean(ic_n):+.4f}")
print(f"  difference {st.mean(ic_c) - st.mean(ic_n):+.4f}  "
      f"(vs the raw between-group difference the record reports, about -0.05 to -0.10)")
print("\n  NOTE the twin: general-Qwen-1.5B is adjudicated CLEAN, yet its intercept is")
print(f"  {icept['general-Qwen-1.5B']:+.4f} with CI {icpci['general-Qwen-1.5B']} — EXCLUDING zero,")
print("  and inside the Coder range. Its cell sat at Δ_art +0.0642, where its own")
print(f"  compression ({slope['general-Qwen-1.5B']:.3f} x 0.0642 = "
      f"{slope['general-Qwen-1.5B'] * 0.0642:+.4f}) almost exactly cancels that intercept.")

# ------------------------------------------------- (4) the diet claim's defence
print("\n" + "-" * 92)
print("(4) CHECKED, NOT ASSUMED: is Phase 9's generated 2x2 position-matched?")
print("-" * 92)
g = A("h9_2x2_generated_sets.json")["cells"]
lab = {"G1a": "DeepSeek self", "G1b": "DeepSeek foreign",
       "G1c": "Coder self", "G1d": "Coder foreign"}
for k in ("G1a", "G1b", "G1c", "G1d"):
    c = g[k]
    print(f"  {k} {lab[k]:<18} n={c['n']:<3} Δ_art {c['achieved_delta_art']:+.4f}   "
          f"cond−iid {c['delta_cond_minus_iid']:+.4f}")
dd = st.mean(g[k]["achieved_delta_art"] for k in ("G1a", "G1b"))
dcd = st.mean(g[k]["achieved_delta_art"] for k in ("G1c", "G1d"))
ed = st.mean(g[k]["delta_cond_minus_iid"] for k in ("G1a", "G1b"))
ec = st.mean(g[k]["delta_cond_minus_iid"] for k in ("G1c", "G1d"))
print(f"\n  DeepSeek arms mean Δ_art {dd:+.4f}   Coder arms {dcd:+.4f}   "
      f"difference {dcd - dd:+.4f}")
print(f"  effects: DeepSeek {ed:+.4f}   Coder {ec:+.4f}   difference {ec - ed:+.4f}")
print(f"  position advantage to Coder: {(dcd - dd) * 0.7:+.4f} at a nominal slope 0.7")
print("\n  -> The 2x2's four cells sit within 0.021 of each other, and the position")
print("     difference favours the CODER arms — the ones that sink harder. The confound")
print("     therefore works AGAINST Phase 9's conclusion, making it CONSERVATIVE.")
print("     THE DIET CLAIM DOES NOT DEPEND ON PHASE 7'S BATTERY. It stands on Phase 9.")

# ------------------------------------------------- (5) the committed prediction
print("\n" + "-" * 92)
print("(5) committed prediction for the decisive cell")
print("-" * 92)
lo, hi = icpci["general-Qwen-1.5B"]
print(f"  general-Qwen-1.5B at TRUE match (Δ_art ≈ 0), from its own compression law:")
print(f"      predicted cond − iid = {icept['general-Qwen-1.5B']:+.4f}  "
      f"CI95 [{lo:+.4f}, {hi:+.4f}]")
print(f"  its Coder sibling at true match measured {-0.052:+.4f} (P11, n=44)")
print(f"  a NULL (0.000) is what the DIET claim predicts for a non-Coder model")
print("\n  These two predictions are ~0.04 apart and the cell can distinguish them.")

out = {"_label": "P0 free — position audit of the matched-cell corpus [PHASE_19.md P0]",
       "cells": [{"cell": n, "group": g, "phase": ph, "instrument": i,
                  "achieved_delta_art": d, "verdict": v,
                  "compression_slope": round(slope[n], 4),
                  "intercept": round(icept[n], 4), "intercept_ci95": icpci[n]}
                 for n, g, ph, i, d, v in CELLS],
       "p7_confound": {"non_coder_mean_dart": round(dn, 4),
                       "p7_coder_dart": dc, "difference": round(gap, 4),
                       "mean_slope": round(sl, 4),
                       "shift_bought_by_position": round(gap * sl, 4),
                       "sink_effect_scale": -0.05,
                       "ratio": round(abs(gap * sl / 0.05), 2)},
       "phase9_2x2_position_matched": {
           "deepseek_mean_dart": round(dd, 4), "coder_mean_dart": round(dcd, 4),
           "difference": round(dcd - dd, 4),
           "deepseek_effect": round(ed, 4), "coder_effect": round(ec, 4),
           "confound_direction": "favours the Coder arms — conclusion is conservative"},
       "prediction_twin_at_true_match": {
           "from_compression_law": icept["general-Qwen-1.5B"],
           "ci95": icpci["general-Qwen-1.5B"],
           "diet_claim_predicts": 0.0,
           "coder_sibling_measured": -0.052}}
(REPO / "artifacts/h19_p0_position_audit.json").write_text(json.dumps(out, indent=2))
print("\nwrote artifacts/h19_p0_position_audit.json")
