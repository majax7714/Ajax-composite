# Phase 8 — the mechanism of the sink, and closing the confounds the matched battery left open

*Charter received 2026-07-18. Append-only; every run pre-registered with odds and
decision rules committed before it launches. This document is the Phase-8
pre-registration and result log.*

## 0. The claim ladder (recorded at the top, per the charter — the phase climbs it honestly)

1. **MEASURED:** the Qwen2.5-Coder line sinks at match (Δ_art ≈ 0) at 1.5B, 3B, 7B;
   three non-Qwen-Coder models (DeepSeek-Coder-1.3B, StarCoder2-3B, general-Qwen-1.5B)
   sit flat-to-positive at comparable positions. *(Phase 7.)*
2. **ATTRIBUTED** (one rung up, licensed by the general-1.5B contrast): the Coder
   continued-pretraining stage causes it.
3. **HYPOTHESIZED** (two rungs up, n = 1 at the family level): the synthetic-heavy
   data in that stage is the cause.
4. **UNLICENSED:** "code diets do this" — two of the three clean models are code
   models. **The phrase "coding-model diet phenomenon" must not appear** in the Index
   or any extraction. Current honest scope: **one code family's diet**, attribution
   pending a second synthetic-code family (C3).

Phase 8's product is an origin line that is either a **mechanism sentence with
independent evidence under it** or an **honestly broken one, one level deeper**.

**Charter question:** what is the mechanism of the Coder-line sink, and does the
finding survive the four confounds Phase 7 left standing (provenance, band
asymmetry, family-n = 1, 7B n = 20)?

## 1. Standing rules (unchanged, plus one addition landed in P0)

Append-only; pre-register predictions/odds/decision rules before any run; no learned
verifier; reconciliation-ledger entries for external results; §8 ops ledger + stack
fingerprint on every artifact; distinct-seed protocol; **matched-relation rule (every
comparison stated in Δ_art terms in its pre-registration)**; Index current at close.

## P0 — Free checks that reshape the phase *(zero dollars; landed first)*

**P0.a — H-diet-modulated power caveat (landed in §9.9 P7 addendum + here).** The
Phase-7 rejection of H-diet-modulated stands **as stated** — the clean cells show no
*visible* negative pressure — but their CIs (M1 [−0.021, +0.116], M3 [−0.075, +0.088],
M2 [−0.066, +0.059]) **exclude Coder-magnitude sinks (≤ −0.09) but not a shallow
universal pressure of −0.02…−0.05**. The shallow-diet-modulated variant is
**OPEN-at-current-n**, not excluded. No downstream text may over-read the rejection.

**P0.b — The donor is Qwen2.5-Coder-1.5B-base, not general Qwen (a mislabel,
corrected).** The fixed donor pool (`lcb_cand_lcb_r2_base_T08.json`) has `model` =
`Qwen/Qwen2.5-Coder-1.5B`; Phase-7 docs + `j7_match_artifacts.py` had mislabeled it
"Qwen2.5-1.5B-base." Corrected in place (mined sets byte-identical). **Consequence
(sharpens C1):** every sink cell was conditioned on **diet-matched** (Coder)
artifacts and every clean cell on **diet-mismatched** artifacts — so the dissociation
is confounded with **artifact provenance**, and even P6's general-1.5B "clean control"
saw *foreign-diet* artifacts. The provenance confound is not a side issue; it touches
the attribution rung directly.

**P0.c — Coverage reality for the C-cells (measured before pre-registering them),
so no un-runnable cell is chartered as runnable:**

| cell | need | measured coverage | status |
|---|---|---|---|
| **C1** DeepSeek self @ match (0.362) | self-pool in-band | **4/80** (±0.05), 9 (±0.10), 11 (±0.13) | **BLOCKED by mining** — needs generated self-artifacts |
| **C1-mirror** Coder-1.5B on DeepSeek arts @ 0.468 | DeepSeek pool in-band | **2/80** (any band) | **BLOCKED** |
| **C2** DeepSeek @ Δ_art −0.04 (donor ~0.322) | donor pool in-band | **29/80** (±0.05), 45 (±0.07) | **runnable** |
| **C4** Coder-7B @ 0.659, wider band | donor pool in-band | 20 (±0.05), 34 (±0.07), **37 (±0.10)** | runnable to **n ≈ 37** (short of 40 — flag) |

C1 hits **exactly the mining wall Phase 7 recorded and deferred** (self-pools too
bimodal in the mid-band). Its pre-registration below is reframed around generated
self-artifacts; **author decision required** (run generated, or defer with the
provenance confound recorded OPEN).

---

## D — Mechanism discriminators *(free/cheap; pre-registered here BEFORE computing)*

**Mechanism frame.** Δ_cond ≈ **imitation pull** (∝ Δ_art; family-general; the Codex
baseline) **+ a diet-specific conditioning penalty**. Live penalty candidates:
- **M-RECLASS** (exemplar reclassification): synthetic pedagogy's document grammar is
  problem→authoritative-solution only; a matched artifact is maximally ambiguous, is
  trusted as an exemplar, and its bugs are inherited and elaborated.
- **M-OOD** (repair-scarcity / off-manifold): matched conditioning is
  out-of-distribution and degrades generation, unmasked at match where pull is zero.
- **M-INSTRUCT** (semi-instruct base misfiring): **DEAD** — killed by M2 (general-1.5B
  shares the base property, clean at match).

### D1 — Inherited-error analysis *(free; CPU over persisted pools; cleanest single discriminator)*

**Cells.** Sink: Coder-1.5B (`d2c_res`), Coder-3B (`j6_q1a_res_qwen3b`), M4
(`j7_res_M4_coder7b`). Clean control: M1 (`j7_res_M1_deepseek1p3b`).

**Metric (committed before computing).** For each problem, with `n` = its test count:
- artifact failing-set A = the conditioning artifact's failed test-ids (from the donor
  res at that `(qid, cand_idx)`).
- For each generation g (E1 conditioned; and E0 unconditioned as the null),
  G = its failed test-ids.
- **excess overlap** = `|G ∩ A| − |G|·|A|/n` (observed minus chance-expected overlap,
  which controls for both set sizes within-problem). Per problem: mean excess over the
  8 E1 gens, and over the 8 E0 gens.
- **Validity gate:** the artifact-source pool and the gen pool must report the same
  `n_tests` for a problem (same test suite / indexing) or the problem is dropped and
  counted.

**Test + threshold (committed).** Paired one-sided Wilcoxon across problems, E1-excess
> E0-excess.
- **M-RECLASS predicts:** sink cells show E1-excess **significantly >** E0-excess
  (p < 0.05) — conditioned gens fail the artifact's *specific* tests beyond chance and
  beyond the unconditioned base rate (bugs propagated).
- **M-OOD predicts:** E1-excess ≈ E0-excess (n.s.) — degradation uncorrelated with the
  artifact's particular errors.
- **Control:** M1 (clean) shows E1-excess ≈ E0-excess under **either** mechanism.

**Secondary (report, don't gate).** Among E1 gens failing the artifact's tests:
elaborated (novel code extending the approach — mid SequenceMatcher-ratio band to the
artifact) vs copied (near-verbatim, high ratio). Elaboration is the RECLASS signature
and is what the fidelity free-rider (sink at matched fidelity) predicts.

### D2 — Per-diet response curves *(free; from `h7_relational_assembly.json`)*

**Data.** 6 Coder points {Coder-0.5B, 1.5B, 3B, 7B (record), M4, M5} and 6 non-Coder
points {DeepSeek, StarCoder2, general (record), M1, M2, M3} on the (Δ_art, Δ_cond)
plane.

**Fit (committed).** Primary read = **the Coder curve's own shape**: Δ_cond as a
function of Δ_art, is it **non-monotone with a trough near match** (position-gated) or
monotone? Secondary = the **difference curve** Coder_fit − nonCoder_fit, fit as a
**quadratic** per group (3 params on 6 points — a shape read, stated as such), with a
**monotone-linear** conservative baseline and **leave-one-out leverage** reported. The
non-Coder curve is measured only on Δ_art ∈ [+0.033, +0.170]; below that it is
**extrapolated** (C2 measures it directly) — every penalty number at Δ_art ≤ 0 carries
that caveat explicitly.

**Shape branches (committed).**
- **position-gated** (penalty peaks near Δ_art ≈ 0, shrinks toward both arms) →
  consistent with RECLASS's ambiguity story.
- **constant offset** → strained by the fixed-7B drag (−0.050 at Δ_art −0.165); would
  force re-examination of that cell.
- **sign-gated** (penalty only for Δ_art ≤ 0) → the sign story resurfaces and **C2
  becomes the phase's most important cell**.

### D3 — Artifact perplexity probe *(cheap GPU; pre-registered here, RUN WITH SIGN-OFF)*

**Design.** Mean per-token loss of each model on: (a) its matched artifacts, (b) the
fixed 0.494 set, (c) its own E0 generations (self-baseline). One forward pass per model.

**Prediction (committed).** **M-RECLASS:** Coder models find their matched artifacts
**unsurprising** (near self-baseline — credible exemplars) yet sink. **M-OOD:**
**elevated** surprise on matched artifacts for Coder models relative to non-Coder
models on theirs. A **null/ambiguous** read is priced (perplexity is a blunt proxy for
"recognized as exemplar"); D3 **corroborates, it does not decide alone**.

### D-item joint decision rule

The mechanism call requires **agreement of D1 and D2** (D3 corroborating). D1 and D2
disagreeing → **MIXED**, recorded not harmonized — and the C-cells still run, because
the confounds are independent of the mechanism call.

*(D1 and D2 results + the mechanism call are appended below after they run; D3 and the
C-cells await the GPU sign-off gate.)*

### D1 RESULT (2026-07-18) — **as-pre-registered: INCONCLUSIVE (control not at null); corrected D1′ below**

`h8_d1_inherited_error.json`. All three sink cells show E1 excess-overlap ≫ E0:
Coder-1.5B +1.50 vs +0.18 (p < 1e-4), Coder-3B +1.68 vs +0.15 (p < 1e-4), M4 +0.70 vs
+0.23 (p = 0.0018). **But the clean control M1 shows the *largest* effect** — E1 +2.52
vs E0 +0.29 (p < 1e-4), fidelity **0.84** (near-copy). M1 *lifts* (+0.050) yet inherits
the artifact's failing tests most strongly, because it **copies up** to an
above-its-level artifact. **The pre-registered control assumption (M1 at null) is
FALSIFIED.** Inheritance-of-failing-tests is **imitation pull** — family-general,
maximal in the clean copying cell — so the excess-overlap metric conflates imitation
with the sink and is **inconclusive as a discriminator**. (Recorded straight; the
falsified control is itself informative — it confirms the mechanism frame's
"imitation pull" term is family-general, the Codex baseline.)

### D1′ — corrected, sink-specific discriminator *(pre-registered here BEFORE computing)*

The sink is the **E1-vs-E0 marginal degradation**, not total inheritance. Isolate it:
per test t, `induced(t) = P(E1 fails t) − P(E0 fails t)` (positive = conditioning
*breaks* t). Metric per problem: **mean induced on the artifact's failing tests A minus
mean induced on non-A tests**. Paired one-sided (contrast > 0) across problems.
- **M-RECLASS:** Coder sink cells show contrast **> 0** (p < 0.05) — conditioning
  breaks the **same** tests the artifact fails (its specific bugs propagate).
- **M-OOD:** contrast **≈ 0** — the induced failures are uniform across tests,
  uncorrelated with the artifact's particular errors.
- **Control M1:** ≈ 0 (it lifts; little induced failure to distribute) — under D1′ the
  control is *expected* near-null by construction, repairing D1's flaw.

### D1′ RESULT (2026-07-18) — **still INCONCLUSIVE; the discriminator is swamped by family-general imitation**

Contrast (induced on artifact-tests − non-artifact tests): Coder-1.5B +0.374, Coder-3B
+0.448, M4 +0.153 — all p < 0.05, all RECLASS-*shaped*. **But the clean control M1 is
+0.713 — the LARGEST.** The correction did not repair the flaw: any model that imitates
the artifact concentrates its induced failures on the artifact's failing tests
(inheriting its bugs) while sparing its passing tests — whether it copies *up* (M1,
fidelity 0.84, lift) or elaborates *down* (Coder, fidelity 0.57–0.64, sink). Artifact-
imitation is **family-general**; D1 cannot assign RECLASS vs OOD. **The one sink-specific
signal is fidelity/elaboration:** sink cells elaborate (0.57–0.64) and land *below* the
artifact; the clean cell copies (0.84) and lands *at* it. The sink is **downward
elaboration of a matched artifact** — but that phenomenology is shared by RECLASS
(trusts+extends an exemplar) and OOD (off-manifold degradation). **D1 verdict:
INCONCLUSIVE, leans "elaboration-degrades," does not decide RECLASS/OOD.**

### D2 RESULT (2026-07-18) — **POSITION-GATED** *(`h8_d2_response_curves.json`)*

The Coder curve Δ_cond = f(Δ_art) is **non-monotone with an interior trough**: quadratic
R² = 0.835, convex, vertex at Δ_art ≈ **−0.092**; the deepest point (−0.150) is at an
**interior** Δ_art (−0.074), not an endpoint; LOO trough stays in [−0.12, −0.03]. The
non-Coder curve is **monotone-increasing** (linear slope +0.49, quadratic R² only 0.50)
— pure imitation pull, no trough. The **penalty** (Coder − non-Coder) in the *measured*
overlap [+0.033, +0.170] is ≈ **−0.05 to −0.08**; below Δ_art +0.033 it is
**extrapolated** and unreliable (the non-Coder fit turns the penalty positive at −0.15
— an extrapolation artifact, flagged; **C2 measures this region directly**). **D2 branch:
POSITION-GATED** — the diet penalty peaks near match and shrinks toward both arms,
consistent with RECLASS's ambiguity-at-match story (and with OOD-at-match, where pull is
zero and only degradation remains). *(6 points/group — a shape read, not a parameter
estimate.)*

### MECHANISM CALL (D-rule: D1 + D2, D3 corroborating) — **phenomenology characterized; RECLASS-vs-OOD OPEN, D3-pending**

D1 and D2 **agree on the phenomenology**: the sink is a **position-gated,
downward-elaboration** effect — a Coder model conditioned near its own quality (straddle)
elaborates the matched artifact and lands below it, deepest near Δ_art ≈ −0.09, shrinking
toward both arms. **But they do not resolve RECLASS vs OOD:** D1's discriminating
prediction (artifact-*specific* bug inheritance) was **swamped by family-general
imitation** (the clean control inherits most strongly), and D2's position-gating is
consistent with *both* candidates. **The RECLASS/OOD label is OPEN.** D3 (perplexity —
does a Coder model find its matched artifact **unsurprising**, i.e. exemplar-credible →
RECLASS, or **elevated-surprise**, off-manifold → OOD?) is now the **decisive** remaining
discriminator, not merely corroborating. It is pre-registered above and awaits the GPU
sign-off. **Recorded call: phenomenology = position-gated elaboration-degradation;
mechanism label = OPEN (D3-pending).**

---

## C — Confound closures *(pre-registered here; each ~$4–10; AWAIT SIGN-OFF)*

### C1 — Provenance (the missing Phase-7 side cell) — **REFRAMED: mining-blocked, needs generated artifacts**

The fixed-donor rule conditioned every Coder cell on **Coder-diet** artifacts and
every clean cell on **foreign-diet** artifacts (P0.b). C1 was to run DeepSeek-1.3B on
its **own** (DeepSeek-diet) matched artifacts. **Mining cannot reach it** (P0.c:
4–11/80). Reframe: **generate** DeepSeek self-artifacts at its 0.36 band (high-temp
DeepSeek sampling on the cell problems, select frac ∈ [0.31, 0.41]; documented
transform — introduces a generated-artifact variable, scoped like C5), then condition
DeepSeek on them.
- **clean** → the donor-family/diet-provenance confound dies; the diet dissociation
  stands on provenance-controlled ground.
- **sinks** → the finding reframes to **self-conditioning** (a model sinks on its own
  near-quality output regardless of diet) — a *larger, stranger* claim; the Coder
  story would need re-decomposition (Coder cells were always diet-matched). Priced as
  the **bigger** branch, not the ugly one.
- **Mirror** (Coder-1.5B on foreign-diet artifacts): also mining-blocked (2/80);
  deferred unless generated.
- **AUTHOR DECISION:** run C1-generated, or defer C1 with the provenance confound
  recorded OPEN. (The generated-artifact scope means C1's Δ_cond is **not** numerically
  comparable to the mined cells — only its sink/clean binary is.)

### C2 — One non-Coder cell below zero *(closes the band asymmetry; runnable)*

No clean model has been measured at Δ_art ≤ 0. Place **DeepSeek-1.3B at Δ_art ≈ −0.04**
(donor artifacts mined ~0.322, just below its i.i.d.; coverage 29/80 at ±0.05).
Matched-sink signature as Phase 7 (cond < iid, one-sided p < 0.05, effect ≤ −0.05).
- **flat / mild-drag** → the sign story dies; the 1.5B-sink-vs-M3-flat near-tie
  (+0.026 vs +0.033) is reinforced from the other side.
- **sinks** → the sign variable re-enters; the diet story must be re-decomposed
  against it.

### C3 — Second synthetic-code family: phi at match *(moves attribution past n = 1)*

**phi-1.5** (1.3B) — "Textbooks Are All You Need," synthetic code pedagogy by
construction. Smoke gate (phi's prompt format differs — template work budgeted; a
failed smoke is reported, not forced), measure its i.i.d. on the cell problems, mine
donor artifacts to its band, run at match.
- **phi sinks** → synthetic-diet attribution gains its **second family**;
  "synthetic-heavy code pretraining produces the sink" becomes a **licensed
  generalization** — the extraction upgrades materially (ladder rung 3 licensed).
- **phi clean** → attribution falls back to "something in **Qwen's** Coder stage" —
  still a finding, the narrower and honest one.
- **phi un-smokeable** → OPEN, reported.
- **Ledger entry required before the run (rule 4):** phi's training-data documentation
  — textbook-style synthetic pedagogy vs Qwen-Coder's LLM-generated pairs; the delta
  matters for interpreting either branch.

### C4 — M4 confirmation at higher n *(mandatory before any extraction touches 7B)*

The 7B matched sink (n = 20, donor-easy selection, reversed a closed gate) is confirmed
or bounded. Deeper mining at 0.60–0.66 (**±0.10 band → n ≈ 37**, the measured ceiling;
40 unreachable from this donor — recorded), fresh distinct-seed E0 + conditioned arms.
- **replicates (Δ ≤ −0.08)** → the 7B row is confirmed.
- **halves/vanishes** → the 7B row reverts to **OPEN**, Phase-7's 7B result scoped to
  its selection.
- Record the cell's problem-difficulty profile (donor-easy selection is a scope, named
  in the row).

### C5 — 0.5B straddle via generated artifacts *(resolves the reopened lower bound; run last, drop first)*

Mining cannot reach 0.5B's band (M5: artifacts sat above its 0.123). Generate at its
band (donor high-temp sampling / documented degradation, select frac ∈ [0.08, 0.17]),
run 0.5B conditioned + E0. **Scoped cell** ("0.5B at straddle, generated artifacts") —
resolves OPEN → measured **for this rung only**; its Δ_cond is **not** compared
numerically against mined cells.

---

## Sequencing and phase gate

**Order:** P0 ✓ → **D1/D2 (free, run now)** → mechanism call recorded → **[SIGN-OFF
GATE]** → D3 + C-cells: **C2 → C4 → C3 → (C1-generated?) → C5** (drop-first if budget
binds: C5, then the C1 mirror). Index/figure/ledger updates → close.

**[SIGN-OFF GATE — author decisions before GPU spend]:**
1. Go/no-go on the C-cell battery (~$20–40) + D3 (~$3).
2. **C1:** run via generated self-artifacts (scoped), or defer (provenance OPEN)?
3. **C4:** accept n ≈ 37 ceiling (±0.10 band), or defer 7B confirmation?
4. **C3:** phi-1.5 the second-family pick — confirm, and the ledger entry lands first.

**Phase gate — Phase 8 closes when:** the mechanism call is recorded (RECLASS / OOD /
MIXED, D1+D2 agreement stated, D3 noted); the provenance (C1) and band-asymmetry (C2)
confounds are resolved or explicitly reframed; the diet attribution carries family-n =
2 (C3) or an honest fallback to "Qwen-Coder-stage-specific"; the 7B sink is confirmed
at higher n or reverted to OPEN (C4); the Index claim ladder states the current rung
explicitly and the relational figure carries every new cell; the note's gating status
reflects the outcome.

## What this phase protects

Phase 7 turned a five-phase-narrowing claim into the widest the record has held — a
cross-scale, diet-specific conditioning failure. Phase 8 decides whether that claim
gets a **why** (a mechanism with independent evidence lines, provenance-controlled,
replicated in a second synthetic family) or **breaks again one level deeper**. The
only unacceptable exit is an origin line whose confounds were known, named, and cheap
to close — and left open for momentum.
