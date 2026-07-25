# Phase 14 — head ablation, dose-response: is there a *targeted* effect at matched capability cost?

*Charter opened 2026-07-25. Fifth iteration of the unattended loop
([AUTONOMOUS_LOOP.md], Amendment 1). Append-only; pre-registration frozen before spend.*

## 0. What Phase 13 left, and the confound it exposed

Phase 13 S2 ablated K = 16 of Coder-1.5B's 336 heads and destroyed the model
(conditioned 0.022 top-K / 0.159 random-K against an i.i.d. arm of 0.472). Branch C:
instrument miss, K deliberately **not** retuned in-phase.

The confound it exposed is the real content: **ablating any important head costs general
capability**, and capability loss moves the sink on its own. Comparing top-K against
random-K **at matched K** therefore compares two different capability levels. The
comparison has to be made **at matched capability cost**.

Phase 13 S1 supplies the motivation: artifact attention is more *concentrated* in
sinking models (Gini +0.05–0.06 across both pairs). If that concentration is
load-bearing, removing the concentrated heads should move the sink **beyond** what their
capability cost explains. If it is incidental, it should not.

## 1. Design — a dose-response in (capability, sink) space

**Model:** Coder-1.5B, HF path — validated in Phase 13 (B1 reproduced the sink at
−0.0613 against vLLM's −0.0522, same problems and artifacts).

**Sweep:** K ∈ **{1, 2, 4, 8}**, two arms per K:

- **TOP-K** — the K highest artifact-attention heads from the S1 ranking.
- **RND-K** — K heads sampled from the complement of the top-16, seed-fixed (191),
  **nested** so RND-1 ⊂ RND-2 ⊂ RND-4 ⊂ RND-8 (as TOP-K is by construction), making the
  two curves comparable dose-for-dose.

**Anchors reused, free:** Phase 13's `B0_iid` (0.4723) and `B1_cond` (0.3976, sink
−0.0613) are the cached K = 0 points for both curves. Same problems (n = 44), same
artifacts, same seed, same `max_new_tokens`.

**The analysis.** Each run yields a point `(conditioned mean frac, sink = cond −
artifact)`. Plot both arms in that plane. Ablation that acts *only* through general
capability puts both arms on **one** curve. A targeted effect puts TOP-K **off** it.

Adjudication compares the arms **at matched conditioned performance**, not at matched K:
for each TOP-K point, linearly interpolate the RND curve at the same conditioned mean
frac and take `Δ = sink(TOP) − sink(RND_interpolated)`. Reported as the mean of the
interpolable points and their signs.

## 2. Pre-registered predictions

| # | branch | reading | odds |
|---|---|---|---|
| **A** | TOP-K sits **above** the RND curve (less sink at matched capability), mean Δ ≥ +0.02 with consistent sign | the concentrated artifact heads carry the degradation **beyond** their capability cost — a **targeted causal contribution**, the first in this record | **30%** |
| **A′** | TOP-K sits **below** the RND curve (more sink at matched capability), mean Δ ≤ −0.02 | the concentrated heads *protect against* the sink; degradation worsens when they are removed — surprising, and would invert the S1 reading | **10%** |
| **B** | the curves are indistinguishable (\|mean Δ\| < 0.02, or signs inconsistent) | ablation moves the sink **only** through general capability; S1's concentration is real but not load-bearing. Consistent with P12's magnitude null | **45%** |
| **C** | curves do not overlap in conditioned performance, so no interpolation is possible | infeasible at this dose grid; recorded, K grid revised in a successor, **not** re-gridded in-phase | **10%** |
| **D** | technical failure | recorded | **5%** |

**B remains the favourite**, for the same reason it was in Phase 13: P12 showed
attention *magnitude* does not distinguish sinking from clean models, and S1's
concentration finding — while it fired — is correlational, rests on four models with one
per cell, and carries an unresolved head-count caveat.

**Validity conditions, frozen.** At least **two** TOP-K points must fall inside the RND
curve's conditioned-performance range (otherwise branch C). Any arm whose conditioned
mean frac falls below **0.05** is excluded from interpolation as degenerate and recorded
as such. n = 44 throughout; all-cases judge; sink reported as `cond − artifact`
throughout.

**What a hit would license.** A would license *"removing these specific heads degrades
conditioned performance beyond what their general-capability cost explains."* It would
**not** license any claim about what those heads compute, nor that they are the *only*
route to the sink. Lesions localise contribution, not function — restated from Phase 13
because a positive result is exactly when that gets forgotten.

**Cost estimate: $1.80–3.00.** Eight new arms; Phase 13 measured ≈$0.28 per
44-problem × 8-candidate HF arm on 1.5B, and the K = 0 anchors are cached. Loop spend
before this phase: **$2.58** of the $90/$110 envelope; month-to-date **$80.62** of $200.

---

*(Results append below.)*
