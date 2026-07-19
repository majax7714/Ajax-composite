# Phase 9 — diet or provenance? The generated 2×2, and the self-conditioning question

*Charter received 2026-07-18. Append-only; every run pre-registered with odds and
decision rules committed before it launches. This document is the Phase-9
pre-registration and result log.*

## 0. The question and the confound

**Charter question:** is the sink caused by the **Coder diet**, or by conditioning a
model on its **own (self/family) near-quality output** — and does the mechanism call
survive a provenance-clean look?

**The two stories the record cannot yet distinguish:**
- **H-DIET** (the standing origin line): Coder-stage training → sink at match; artifact
  provenance irrelevant.
- **H-SELF** (newly live): models sink when conditioned on their **own** near-quality
  output; the clean models were clean because the fixed-donor rule fed every one of them
  **foreign** code (Qwen-Coder-1.5B-base), and the Coder cells sank because every one saw
  **self/family** code.

**Every Phase-7/8 cell sits on the confounded diagonal:** Coder × self-family = sink;
clean × foreign = clean. The off-diagonal was never sampled. The **one** point off the
pattern is the P0.1 anomaly — **Coder-1.5B conditioned on its own base output
(unsurprising, D3 ratio 0.94) sinks anyway** — and it sat in a Phase-8 table labeled as
a caveat, not a hypothesis. (general-1.5B being clean on Coder-1.5B-base artifacts means
that if H-SELF fires it is **self-model**, not base-family — general's own output ≠
Coder-1.5B-base output, so general saw foreign and stayed clean, consistent with both.)

**The stakes if H-SELF fires** (priced as the *bigger* branch, not the ugly one):
self-conditioning at near-match quality is what the record's entire refinement arc was —
BEST-SO-FAR conditioned Qwen on its own best output; the D2c sink, the anchor-poisoning,
the conditioning-hostility findings all ran the self-ish diagonal. A fired H-SELF makes
the Phase-3b–5 refinement nulls **retroactively reinterpretable** as instances of one
self-conditioning hazard, unifying the journal's two threads. Scope pre-declared (§0.3
P0.3 cross-references).

## 1. Standing rules

Unchanged: append-only; pre-register odds/decision rules first; no learned verifier;
reconciliation-ledger entries; §8 ledger + stack fingerprint; distinct-seed protocol;
**matched-relation rule with the iterative-targeting amendment — every cell targets a
*measured* Δ_art (i.i.d. measured on the cell's own problem subset first, band set from
that), never a mined proxy**; Index current at close.

## P0 — Free amendments — **LANDED**

- **P0.1 — mechanism label OOD-leaning → OPEN.** The one provenance-clean D3 point
  (Coder-1.5B, ratio 0.94, self-donor) is unsurprising yet sinks, contradicting the OOD
  lean (which rode on the smaller-sibling-donor cells). Amended in PHASE_8 mechanism
  call, §9.9 P8 addendum, Index rows 8/11, §0.2, §0.4. The pricing below inherits this
  honest prior.
- **P0.2 — the self-conditioning fact indexed** (§0.3): Coder-1.5B sinks on its own base
  generations at its own level — evidence for **both** H-DIET and H-SELF; the 2×2
  assigns it.
- **P0.3 — BSF/D2c cross-references placed** (§0.3): Phase-3b BEST-SO-FAR + the D2c sink
  ran self-provenance near-match conditioning; reinterpretation contingent on H-SELF,
  scope pre-declared, no conclusion drawn.

---

## G1 — The generated 2×2 *(centerpiece; 4 cells ~$20; the D3 sweep rides free)*

**PRE-REGISTRATION (2026-07-18 — FROZEN pending sign-off).**

**Design principle: provenance and generation-method must not move together.** Phase-8's
C1-reframe would have compared generated-self against mined-foreign history — the exact
trap the §10 amendment codifies. So **all four cells use generated artifacts, one
transform, one selection rule, both generators.** The generated-artifact variable is held
constant and **cancels in every within-model contrast**.

| cell | conditioned model | artifact provenance | band (position) |
|---|---|---|---|
| **G1a** | DeepSeek-1.3B | **self** (DeepSeek-generated) | DeepSeek's measured match |
| **G1b** | DeepSeek-1.3B | **foreign** (Coder-1.5B-generated) | same (DeepSeek's match) |
| **G1c** | Qwen-Coder-1.5B | **self** (Coder-1.5B-generated) | Coder's measured match |
| **G1d** | Qwen-Coder-1.5B | **foreign** (DeepSeek-generated) | same (Coder's match) |

**Protocol (frozen):**
1. **Fix the problem set first**: the 44 D2c problems, minus any where *either* generator
   cannot band-cover *any* of the four cells' bands (one shared subset for all four —
   reported, with the dropped list).
2. **Iterative targeting** (§10 amendment): measure each conditioned model's i.i.d. on the
   subset with a **distinct seed**; set each model's band = subset-i.i.d. ± 0.05.
3. **Generate** (same transform): high-T (T = 1.2) sampling of each generator on the
   subset, k = 50; judge all-cases for per-candidate frac; per problem select the
   nearest-frac candidate **in the conditioned model's band**.
4. **Report achieved Δ_art per cell** (= mean artifact frac − conditioned model's i.i.d.
   on the *covered* subset). **If any cell's achieved Δ_art is outside ±0.08 of 0,
   re-target once** (recompute band from the covered-subset i.i.d.), then report honestly
   — a cell that missed its straddle is **not** called matched.
5. **Condition** each model (E0 + E1, k = 8, seed 17, all-cases judge, stack fingerprint).
   **Sink signature** (Phase-7 committed): cond < subset-i.i.d., one-sided p < 0.05,
   effect ≤ −0.05, per cell. The generated-artifact scope (C5) applies to **absolute
   Δ_cond**; the **within-phase factorial contrasts are the results.**

**Branches + odds (priced post-P0; neither main effect a favourite):**
- **DIET main effect — 38%** (G1c, G1d sink; G1a, G1b clean): Coder sinks on *both* self
  and foreign artifacts; DeepSeek clean on both → **H-DIET stands, provenance-controlled
  at last**; rung-2's confound closes; the origin line survives its final named confound.
- **PROVENANCE main effect — 30%** (G1a, G1c sink; G1b, G1d clean): each model sinks on
  its **own** output, clean on foreign → **H-SELF fires**; the pathology reframes to
  self-conditioning; the Index rescopes rungs 2–3, the P0.3 cross-references **activate**,
  and the close carries the Phase-4-dissociation re-decomposition plan (it becomes a
  provenance artifact) — retraction-grade, priced now.
- **INTERACTION — 20%** (only G1c — self × Coder — sinks): the sink needs **both**; the
  narrowest claim yet, both stories partially survive, the note narrows again. (The one
  existing clean point *is* self × Coder and sinks — this branch has direct support.)
- **UGLY — 12%** (all four sink / none sink): generated artifacts behave categorically
  unlike mined ones (the generation variable dominates — the C5-scope warning realized);
  the mined-vs-generated delta becomes its own finding. Priced, not hidden.

**Free D3 sweep** (one forward pass per cell — each model's perplexity on its self set,
its foreign set, and its own-E0 baseline — crossing surprise × provenance for two
models). **Two pre-registered readings** (the mechanism question's first provenance-clean
look):
- **OOD refuted** — the **self column is unsurprising** (self = on-manifold: surprise
  ratio ≲ 1 for G1a-self and G1c-self) **yet sinks** → the sink is **decoupled from
  surprise**; the P0.1 anomaly generalizes and OOD loses its remaining ground.
- **OOD supported** — surprise **co-varies with the sink** across the grid (the sinking
  cells are the more-surprising ones; foreign > self in surprise *and* the sinks fall on
  the surprising cells) → OOD regains clean footing.

**Artifacts (planned):** `h9_2x2_G1{a,b,c,d}.json` (per cell + stack block),
`h9_2x2_generated_sets.json` (subset, i.i.d.s, bands, achieved Δ_art, coverage),
`h9_d3_sweep.json`. **Writeup:** §9.9 P9 addendum; Index rows 8/11 branch; relational
figure gains the four G-cells (marked generated, C5-visually-distinct).

---

## G2 — Contingent cells *(pre-registered now, launched per G1's branch; ~$10–15)*

- **If DIET main effect:** **phi-1 at its true match** (iterative targeting) — the
  Phase-8 sub-threshold lean (−0.033, lift-excluding CI) converts to a decision; the
  family-n = 2 question becomes the last open rung, this cell make-or-break. (Ledger note
  from Phase 8 carries over.)
- **If PROVENANCE main effect:** **StarCoder2-3B × self-generated at match** — the third
  family on the self column; H-SELF's generality is the new rung-2; one more family
  decides two-model-fact vs general. (phi defers; its lean gets reinterpreted first.)
- **If INTERACTION:** both defer; the interaction's **replication** — a second Coder
  checkpoint (Coder-3B) on the self/foreign pair — takes the slot.
- **The below-zero clean cell** (C2's sign question) stays queued behind everything,
  iterative-targeted, launched only if budget remains (three points already; a fourth is
  polish, not load-bearing).

---

## Journal work + sequencing + gate

**Journal:** origin-line + claim-ladder re-stated with the branch (rung-2
provenance-controlled / rescoped-to-self / narrowed-to-conjunction); mechanism line
carries the D3-sweep reading; relational figure gains the G-cells; **note stays gated**
(§0.2 — fourth gate, and the right one: its central dissociation is on trial; if H-DIET
fires, the next revision is plausibly its last before the extraction decision — stated as
status, not promise). Successors named (internals probe — now sharpened to self-vs-foreign
attention; 0.5B generated; dose-response; 7B–72B; TTT).

**Order:** P0 ✓ → **G1 pre-reg frozen (this file)** → **[SIGN-OFF GATE]** → subset fixed +
subset-i.i.d.s measured (distinct seeds) → artifacts generated + banded → 4 cells → D3
sweep → branch recorded → G2 per branch → Index/figure/ladder → close.

**[SIGN-OFF GATE — author decisions before GPU spend]:**
1. Go/no-go on the generated 2×2 (~$20) + free D3 sweep.
2. Generation transform: T = 1.2, k = 50, per-problem nearest-frac-in-band — confirm.
3. G2 pre-authorized to launch on its fired branch (~$10–15), or pause for a second
   sign-off after G1's branch is known?

**Phase gate — Phase 9 closes when:** the P0 amendments are landed (✓); the 2×2's branch
is recorded with **achieved Δ_art per cell**; the mechanism line carries the
provenance-clean D3 reading; the G2 contingency for the fired branch is resolved or
deferred-with-reason; the claim ladder states the post-2×2 rung; the note's gating
reflects the outcome.

## What this phase protects

Every Phase-7/8 cell sat on one diagonal of a 2×2 nobody had drawn; the one point off the
pattern sat in a table labeled as a caveat instead of a hypothesis. This phase draws the
square and samples all four corners with the generation variable held flat. If H-DIET
survives it survives everything and the origin line stands on unshiftable ground; if
H-SELF fires, the pathology thread and the refinement thread collapse into one
phenomenon — making five phases of conditioning nulls not a detour from the original
refinement question but its answer, from the direction nobody registered.

---

## G1 run 1 — INVALID (recorded straight; re-run with fixes)

The first launch produced garbage and is discarded, for three named reasons — two bugs
and one design infeasibility the run itself exposed:
1. **nmk type bug** (mine): the E0-baseline key was computed as `mid == DS_MODEL`,
   comparing a *string* to a *tuple* → always False → every cell used **Coder's** i.i.d.
   as its E0 baseline (wrong for the DeepSeek cells) and was mislabeled.
2. **4-way shared subset collapses to n = 2.** Requiring one problem set covered by all
   four cells is infeasible with generated **bimodal** pools (most candidates are 0.0 or
   1.0). **Fix (flagged deviation from the charter's "one shared subset"):** per-model-pair
   subsets — the DeepSeek pair (G1a/G1b) on problems both pools cover at DeepSeek's band;
   the Coder pair (G1c/G1d) at Coder's band. The within-model provenance contrast (the
   actual read) is preserved; only the cross-pair sharing is dropped.
3. **i.i.d. drift, exactly as the §10 amendment predicts.** The Coder pair's covered
   subset is systematically *easier* for Coder (subset i.i.d. 0.645 vs global 0.485), so
   a band set from the global proxy lands the artifacts at Δ_art −0.16 (off-target).
   **Fix:** the pre-registered **iterative-targeting loop** — re-center each pair's band
   on the model's i.i.d. *measured on the covered subset*. Converges: DeepSeek band 0.336
   (0 re-targets, n = 19, Δ_art ≈ −0.065); Coder band 0.645 (1 re-target, n = 10,
   Δ_art ≈ −0.038) — both on-target (±0.08).

The expensive step (both high-T pools + i.i.d. measurement) is **cached and correct**;
the re-run reuses it and re-does only selection + conditioning + the D3 sweep (fresh
`_v2` tags so the broken n = 2 volume cache is not hit). ~$3–5. **Coverage note carried
into the read:** Coder pair n = 10 is thin (a clear sink shows at that n — cf. C4 n = 20,
p = 0.003 — but a null is under-powered); DeepSeek pair n = 19. Reported per cell.

---

## G1 RESULT (2026-07-18, Modal L4/bf16) — **DIET main effect; H-SELF refuted; H-DIET survives its final named confound**

Iterative targeting converged (DeepSeek band 0.336, n=19, 0 re-targets, Δ_art −0.065;
Coder band 0.645, n=10, 1 re-target, Δ_art −0.044/−0.045 — both on-target).

| cell | conditioned model | provenance | i.i.d.→cond | Δ vs i.i.d. | p | n | **sink** |
|---|---|---|---|---|---|---|---|
| **G1a** | DeepSeek-1.3B | **self** (DS-gen) | 0.403→0.341 | −0.062 | 0.111 | 19 | **No** |
| **G1b** | DeepSeek-1.3B | foreign (Coder-gen) | 0.403→0.342 | −0.061 | 0.145 | 19 | **No** |
| **G1c** | Qwen-Coder-1.5B | **self** (Coder-gen) | 0.682→0.482 | **−0.200** | 0.005 | 10 | **YES** |
| **G1d** | Qwen-Coder-1.5B | foreign (DS-gen) | 0.682→0.444 | **−0.238** | 0.002 | 10 | **YES** |

**BRANCH: DIET main effect → H-DIET** (the 38% pre-registered favourite). Coder sinks on
**both** self and foreign artifacts — the crux cell **G1d (Coder on DeepSeek-generated
foreign output) sinks *hardest* (−0.238, p 0.002)**; DeepSeek sinks on **neither** (mild
−0.06, n.s., on both). **H-SELF is refuted**: it predicted G1a-sink + G1d-clean; the
exact opposite fired. **The provenance confound closes — the Coder-stage attribution
(ladder rung 2) is now provenance-controlled.** The P0.1 self-conditioning anomaly
resolves: Coder-1.5B sank on its own output because it is **Coder (diet)**, not because
the output was self. The journal's pathology and refinement threads stay **distinct** —
the H-SELF unification branch does not fire (the P0.3 cross-references do **not**
activate; recorded, not deleted).

**The provenance-clean D3-sweep read — OOD refuted.** Surprise (mean NLL) does **not**
track the sink: **DeepSeek's *self* artifacts are the most surprising of all
(1.33 vs own-E0 0.78, ratio 1.71) yet DeepSeek does not sink**; Coder sinks on both its
self (1.08) and foreign (1.45) artifacts. The sink is **diet-gated and decoupled from
surprise** — the OOD story loses its remaining ground (as P0.1 already showed on the one
clean point; now shown across the grid). *(Caveat: the D3 sweep is confounded by
generation temperature — all four artifact sets are T=1.2, so surprise ratios are
inflated vs own-E0; the qualitative decoupling read is robust, the magnitudes are not.)*

**Scope carried on the read (honest):** the Coder pair is **n=10** (thin) but the sinks
are deep and highly significant (−0.20/−0.24, p ≤ 0.005) — robust despite n; a *null*
would have been under-powered, a clear sink is not. Absolute Δ_cond values are on
**generated** artifacts (C5 scope — deeper than the mined −0.095; not numerically
comparable to mined-cell history); the **within-phase factorial contrast** is the
result. DeepSeek's mild −0.06 (n.s.) on both is weakly consistent with the P0
shallow-universal-pressure variant (still OPEN-at-this-n), not a sink.

**Mechanism update:** OOD is now **firmly disfavored** (provenance-clean, grid-wide:
surprise decoupled from sink); RECLASS-as-self-exemplar-trust is **excluded** (Coder
sinks on foreign output it never produced). What survives: a **Coder-diet-intrinsic
conditioning fragility** — the diet makes the model degrade *any* near-quality
partial-credit artifact under "improve this," independent of provenance and surprise.
The positive mechanism (why the diet does this) remains **OPEN** — the named internals
probe (self-vs-foreign attention) is the instrument.

**Post-2×2 claim ladder:** rung 1 (Coder sinks at match, cross-scale) confirmed; **rung 2
(Coder-stage attribution) now PROVENANCE-CONTROLLED — the confound closes, H-DIET stands
on its strongest ground**; rung 3 (synthetic-data) still weak (phi sub-threshold — the G2
question); "code-diet" still UNLICENSED; mechanism OPEN (OOD disfavored, self-exemplar
excluded). **[Artifacts: h9_2x2_G1{a,b,c,d}.json, h9_2x2_generated_sets.json,
h9_d3_sweep.json.]**

**G2 (per the DIET branch): phi-1 at its true match** — the family-n=2 question, now the
last open attribution rung. **Awaiting the second sign-off** (author chose to pause here).

---

## G2 RESULT (2026-07-18) — **phi sub-threshold again (replicated); family-n stays 1**

phi-1 iterative-targeted to its true match (band 0.134, subset i.i.d. 0.101, artifacts
selected nearest the subset i.i.d.; **achieved Δ_art +0.032**, on-target, n=24):

| | i.i.d.→cond | Δ vs i.i.d. | p | sink (p<0.05 **and** ≤−0.05)? |
|---|---|---|---|---|
| **G2 phi-1 true-match** | 0.101→0.059 | **−0.042** | **0.0513** | **No** (both criteria missed by a hair) |

**phi does NOT cross the committed sink threshold** — but it is **negative**, and the
result is **remarkably consistent** with Phase-8 C3 (−0.033, p 0.054): two independent
measurements, both **sub-threshold negative at p ≈ 0.05**. phi shows more negative
pressure than the organic/general clean models (which *lift* at comparable positions:
DeepSeek +0.050, general −0.000, StarCoder +0.008) — its response is **distinctly
Coder-like** — but it never formally sinks. **Verdict: family-n stays 1** (Qwen-Coder
only); the **synthetic-code-diet attribution (rung 3) is a replicated, robust *lean*,
still sub-threshold and UNLICENSED.** *(Scope, honest: phi's i.i.d. (~0.10) sits near
the LCB-easy floor, so it cannot be conditioned at the over-quality side where the sink
is deepest — a position limitation like 0.5B's; phi's true response *at* or *below*
match is unreachable with non-degenerate artifacts. Its consistent sub-threshold lean is
the most the record can say.)*

## PHASE GATE — CLOSED (2026-07-18)

1. **P0 amendments landed** ✓ (mechanism → OPEN; self-conditioning fact indexed; BSF/D2c
   cross-references placed).
2. **The 2×2's branch recorded with achieved Δ_art per cell** ✓ — **DIET main effect →
   H-DIET**; H-SELF refuted; all four cells on-target (run 1 discarded as invalid).
3. **Mechanism line carries the provenance-clean D3 reading** ✓ — sink decoupled from
   surprise → **OOD firmly disfavored**; self-exemplar RECLASS excluded (Coder sinks on
   foreign); mechanism narrowed to **Coder-diet-intrinsic conditioning fragility**,
   positive mechanism OPEN (internals probe).
4. **G2 resolved** ✓ — phi sub-threshold (replicated); family-n = 1; rung-3 unlicensed.
5. **Claim ladder stated** ✓ (below); relational figure gains the G-cells; note gating
   updated.

**Post-phase claim ladder:** **rung 1** (Coder sinks at match, cross-scale) CONFIRMED +
7B robust; **rung 2** (Coder-stage attribution) **PROVENANCE-CONTROLLED — the confound
closes; H-DIET stands on its strongest ground** (Coder sinks on foreign artifacts too;
non-Coder don't sink on anything); **rung 3** (synthetic-data cause) **replicated lean,
sub-threshold, UNLICENSED** (phi ×2); **"code-diet" UNLICENSED**; **mechanism OPEN**
(OOD disfavored, self-exemplar excluded).

**Prediction accounting:** the **38% favourite (DIET) fired**; H-SELF (30%) refuted;
interaction (20%) and ugly (12%) did not. No gate passed by tuning; run 1's invalidity
(two bugs + coverage) recorded straight, re-run clean.

**Cost:** G1 ~$22 (incl. the cached-and-reused pools) + G2 ~$4; run-1 re-do $0 extra
(cached pools). 

**Open (author's, Index in hand):** the **internals probe** (self-vs-foreign attention
— now the *only* instrument left for the positive mechanism, and the 2×2 sharpened it);
0.5B / phi at true over-quality match via generated-degraded artifacts (both floor-capped
by weakness); the standing successors (dose-response hints; 7B–72B switch-on;
TTT/weight-space). **The note's phenomenon + Coder-diet cause are now transcription-ready
(provenance-controlled); the synthetic-data sub-claim and the positive mechanism stay
gated.** Nothing is running; Phase 9 is fully closed.
