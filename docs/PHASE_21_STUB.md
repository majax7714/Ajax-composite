# Phase 21 — **STUB, NOT CHARTERED.** Written at the halt; awaiting author decision.

*Created 2026-07-26 at the Phase-20 halt ([AUTONOMOUS_LOOP.md] §3.1 — a result refuted a
LIVE claim 1:1). Author instruction on leaving: "if brought to a stopping point stub and
propose a different phase." This is that stub. **No spend has occurred against it and no
pre-registration is frozen.***

---

## Why the loop stopped

Phase 20 measured the architecture twin (`Qwen2.5-1.5B`, **non-Coder**) at true match,
paired against `Qwen2.5-Coder-1.5B` on the same 61 problems. **It sinks** — below both
nulls, both CIs excluding zero — and is **indistinguishable from its Coder sibling**
(+0.0088 ± 0.0157, p 0.57). The family-contrast leg of claims 8 and 11 is refuted as
stated. Under §3.1 that is a halt, not a hand-off.

---

## The recommended next phase — **the two missing at-match cells**

**Question:** do **DeepSeek-1.3B** and **StarCoder2-3B** sink at *true* match, measured the
way Phase 20 measured the twin?

**Why this and not something else.** It is the only cell that distinguishes the two
surviving shapes, and both are currently live:

| shape | prediction |
|---|---|
| **Qwen-base effect** — something in the Qwen base, not the Coder stage | DeepSeek and StarCoder2 stay **clean** at true match while both Qwen models sink |
| **Universal ≤3B effect** — the family axis collapses entirely | both **sink**, like the twin did |

Neither has *ever* been measured at its own straddle. Their committed cells sit at
Δ_art **+0.050** and **+0.033** — the same cancellation zone that made the twin read clean
at +0.064, where a model's compression toward its artifact offsets the sink almost exactly.
**Their clean verdicts are suspect on identical grounds**, and until this runs, nothing
should be rewritten into claims 8 or 11 in either direction.

**Design** — reuse Phase 20's machinery unchanged (`_p20_select`, per-problem per-model
artifact matched to each model's own committed k=24 i.i.d.; paired against the Coder
sibling on a shared problem set; four arms per pair at k=48; all gates evaluated inside the
branch expression). Two pairings: {DeepSeek-1.3B, Coder-1.5B} and {StarCoder2-3B,
Coder-1.5B}. **Owed before freezing:** a k=24 i.i.d. sweep for each new model (the pool
sweep exists only for `coder1p5b`, `coder3b`, `general1p5b`), the per-problem feasibility
count at ±0.10, and — per §8 entry 12 — the achieved-SE projection and implied MDE stated
in the charter *before* the run, with an explicit statement of what it cannot resolve.

**Estimated $1.20–2.00 for both pairings.** MTD stands at **$86.83** against Amendment 3's
$100 report / $120 hard stop, so it is affordable, and §4's within-$30-of-cap guard is
satisfied.

---

## Alternatives considered, and why they rank below it

- **Re-measure the twin to confirm.** Phase 20 already carries an independent verifier that
  agreed on every quantity, the sibling replicated its committed value, and the CI is
  narrow. Confirmation is cheap but adds little; the *scope* question is what is open.
- **Chase the mechanism** (head ablation with the corrected design, ~$2). Premature — the
  phenomenon's boundaries just moved, and a mechanism phase aimed at "the Coder diet" would
  be aimed at something the record no longer believes.
- **The compression law's origin** (why every model tracks its artifact at 0.6–0.7). Now the
  record's most robust unexplained regularity, and Phase 21's P0 material is already
  computed and committed (`h21_p0_eiv.json`: the slope survives shared-noise and
  errors-in-variables correction at +0.60/+0.70/+0.64). Genuinely interesting, but it is a
  *new* thread while a central claim sits refuted and unrepaired.
- **Coverage channel via nucleus/top-k.** Still open, still un-intervened, but downstream of
  a claim whose scope is currently unknown.

---

## Already landed and committed at the halt (free, no spend)

`scripts/j21_p0_eiv.py` → `artifacts/h21_p0_eiv.json`. The compression law was fit with the
**same estimated i.i.d. on both axes**, which biases the slope upward through shared noise
for any data. Corrected with two independent i.i.d. estimates, then de-attenuated for
errors-in-variables (the two biases run in opposite directions, so correcting only one would
have been its own error):

| cell | published | decorrelated | **EIV-corrected** |
|---|---|---|---|
| Coder-1.5B | +0.6366 | +0.5812 | **+0.6030** |
| Coder-3B | +0.7871 | +0.6672 | **+0.7048** |
| general-Qwen-1.5B | +0.6585 | +0.6212 | **+0.6437** |

**The law survives**, overstated by a mean of +0.044 (~6% relative); every corrected CI
excludes zero. Phase 19's position-confound argument moves from "1.34× the effect" to
"1.26×" — conclusion unchanged. This is carried here rather than in a charter because it is
an audit of a published number, not a phase.

---
