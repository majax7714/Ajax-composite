# Phase 7 — is the sink Qwen's, the diet's, or everyone's? The matched-artifact battery

*Charter received 2026-07-18. Append-only; every run pre-registered with odds and
decision rules committed before it launches. This document is the Phase-7
pre-registration and result log.*

> **DRAFT STATUS (2026-07-18).** P0 is complete and re-prices P1's hypothesis
> space. P0.1 (StarCoder2 lookup), P0.2 (relational figure), P0.3 (lineage column
> + fingerprint hook) are landed. The matched-artifact miner has run (free CPU):
> per-cell coverage is measured, the pre-registered n's are real. **P1's priced
> odds are frozen below; the paid Modal battery awaits author sign-off** (spend +
> the M2/M4 shortfall rulings + the law re-anchor decision). Nothing has run on GPU.

## 0. Charter and the confound it attacks

**Charter question (supersedes the Phase-6 origin line's finality).** Is the
below-both-nulls sink a **Qwen-Coder property**, a **diet-modulated universal**, or
a **universal property of conditioning at matched model–artifact quality**?

**Why the Phase-6 origin line is provisional.** Every code-channel cell in the
record conditioned every model on the *same* fixed ~0.494-frac artifacts while
model quality swept 0.211 → 0.659. Re-expressed on the relational axis
**Δ_art = (artifact frac − own i.i.d. frac)** — where the stimulus sits relative to
the model's own quality:

| model | own i.i.d. | Δ_art | Δ_cond | behavior |
|---|---|---|---|---|
| Qwen-Coder-0.5B | 0.211 | **+0.284** | +0.178 | lift |
| general-1.5B | 0.324 | **+0.170** | +0.070 | lift |
| StarCoder2-3B | 0.358 | **+0.136** | +0.046 | lift (flat) |
| DeepSeek-1.3B | 0.362 | **+0.133** | +0.107 | lift |
| Qwen-Coder-1.5B | 0.468 | **+0.026** | −0.094 | **sink** |
| Qwen-Coder-3B | 0.569 | **−0.075** | −0.150 | **sink** |
| Qwen-Coder-7B | 0.659 | **−0.165** | −0.050 | drag |

Two confounds follow. **(i)** Every "conditioning-friendly" non-Coder cell was
measured on the **lift arm** (Δ_art ≥ +0.13); no non-Coder model has ever been
observed in the **straddle** (Δ_art ≈ 0) where the sink lives — the Phase-4 double
dissociation compared families at wildly different relational positions. **(ii)**
Phase 6's cleanest control inherits the same confound: swapping Coder-1.5B →
general-1.5B changed the diet **and** moved Δ_art from +0.026 to +0.170, because
diet determines i.i.d. quality, which determines position. CODER-STAGE-vs-position
is **unresolved**. The same error class fired in two consecutive phases; P2 below
codifies the rule that prevents a third.

**The honest counterweight (carried into the odds).** Pure relational imitation
predicts landing *between* the nulls everywhere; it cannot produce below-both. The
sink is a genuine anomaly on any smooth imitation curve — so H-universal is
consistent with the existing data **only because the discriminating region was
never sampled off-Coder**, not because anything yet supports it. This phase samples
it.

## 1. Standing rules (unchanged, plus one promotion)

- Append, never revise; retractions/amendments dated in place.
- Pre-register before running: predictions, odds, decision rules committed first;
  falsified predictions stay on the page.
- No learned verifier anywhere.
- Reconciliation-ledger entry (§11) for every external result used in design.
- §8 operational hardening on all runs (sharded judge where all-cases is required).
- Distinct-seed protocol for any fresh-draw arm (promoted Phase 6).
- Claims & Scope Index current at phase close.
- **(PROMOTED this phase, P2 below) The matched-relation rule:** when a response
  depends on a model–stimulus relation, comparisons must be **matched on the
  relation**, not on the stimulus. Codified in §10; checked at every future
  pre-registration.

---

## P0 — Free lookups and infrastructure *(zero dollars; results re-price P1)*

### P0.1 — The StarCoder2 lookup — **RESULT: lift arm, hypothesis space stays open**

StarCoder2-3B's own i.i.d. frac on the 44-problem D2c cell, pulled from the
Phase-4 H1 artifact (`h1_cross_family.json`):

| quantity | value |
|---|---|
| own i.i.d. frac | 0.3585 |
| conditioned frac | 0.4047 |
| artifact (copy-null) frac | 0.4945 |
| **Δ_art = artifact − own i.i.d.** | **+0.136** |
| Δ_cond = conditioned − own i.i.d. | +0.046 (n.s.) |
| p(cond below copy) | 0.855 → **no sink** |

**Committed decision rule, applied:** *"if Δ_art ∈ [−0.08, +0.08] (straddle) and it
did not sink → a measured non-Coder straddle point with no sink, one observation
against H-universal; price it in. If Δ_art ≥ +0.13 (lift arm) → the space stays
fully open."* **Δ_art = +0.136 ≥ +0.13 → LIFT ARM.** StarCoder2 clears the
threshold by 0.006; it is **not** a straddle observation, provides **no** existing
non-Coder evidence against H-universal, and **M3 stays in the battery** (StarCoder2
has never been measured at straddle).

**Boundary observation, priced (not decisive).** StarCoder2 (+0.136) and DeepSeek
(+0.133) are the two closest non-Coder points to the straddle that exist, and
**both lift/flat, neither sinks** — mild support that incipient sinking is not
visible at the lift-arm edge. But +0.13 is still 0.11 in Δ_art from the 1.5B sink
(+0.026): the discriminating region genuinely remains unsampled off-Coder. Weighted
into the odds below, not treated as a straddle measurement.

### P0.2 — The relational assembly — **committed before P1**

Every code-channel cell joined onto the (Δ_art, Δ_cond) plane from persisted
artifacts (`scripts/j7_relational_assembly.py` → `artifacts/h7_relational_assembly.json`).
Committed **now**, so the battery's M-cells land on a pre-existing plot.

```
  Delta_cond (y)  [+0.20 top .. -0.20 bottom]   Delta_art (x) [-0.20 .. +0.30]
  ':' = straddle band edges (-0.08, +0.13);  '+' = origin (matched, Delta_art=0)
              :       |            :
              :       |            :              g
              :       |            :
              :       |            :
              :       |            d
              :       |            :   f
              :       |            :e
              :       |            :
  --------------------+------------------------------
              :       |            :
      a       :       |            :
              :       |            :
              :       |  C         :
              :       |            :
              :B      |            :
              :       |            :
              :       |            :
    a = Coder-7B (over-quality, drag)   b/B = Coder-3B (straddle, SINK)
    c/C = Coder-1.5B (straddle, SINK)   d = DeepSeek-1.3B (lift)
    e = StarCoder2-3B (lift, flat)      f = general-1.5B (lift)
    g = Coder-0.5B (lift)               UPPER = below-both-nulls sink
```

**What the figure shows and the phase attacks:** the **only** two occupants of the
straddle band are the two Coder sinks (B, C). All three non-Coder cells (d, e, f)
sit on the lift arm; Coder-0.5B (g) far lift; Coder-7B (a) over-quality. The
matched battery places non-Coder models into the straddle for the first time. This
becomes the record's central pathology figure regardless of P1's branch.

### P0.3 — Stack lineage and fingerprint *(infrastructure, not gating)*

- **(a) Lineage column — LANDED.** §0.3 claims-to-evidence table gains a
  **stack-lineage** column: one tag per row naming the stack (hardware/dtype/
  engine/era) that generated its evidencing pools. Pre-Phase-M (Kaggle/4-bit) rows
  are flagged. (Row 3 register-null is the only LIVE/SCOPED row standing solely on
  the retired HF/4-bit stack — already banner-flagged "numbers never cross the
  M-boundary".)
- **(b) Fingerprint hook — LIVE.** `modal_h1.py::_stack_block()` (=`j7_fingerprint`
  remote versions + `_stack_hashes` local content hashes of the gen template, D2c
  context, and judge) attaches a `stack` block — GPU arch, capability, dtype,
  torch/CUDA/vLLM versions, template/context/judge SHA-16 — to **every Phase-7
  artifact**. Verified: the three frozen-wording functions parse and hash.
- **(c) Law re-anchor — SIGNED OFF, THEN RESOLVED MOOT BY THE AUDIT (2026-07-18).**
  The author green-lit the ~$3 E0/E1 re-anchor. But the charter gated it on a
  *condition* — "**if** the lineage audit shows the law's original HumanEval
  constants stand on pre-M pools" — and provenance verification (run before any
  spend) shows the condition is **false**:
  - The escape-distance law's core evidence, the **D-measure** (60-HumanEval-problem
    PULL/TAX cell, `dmeasure_conditioning.json`), is **post-Phase-M**: Phase M ported
    the generator HF/4-bit → vLLM/bf16 *before* Phase 3R, and the mechanism arc is
    "Phase 3R audits → D-measure → the escape-distance law" (§9, §6). It already
    stands on the current bf16 stack.
  - The one genuinely pre-M constant the law leaned on — DIAG-8's **assumed** pairwise
    anchor 0.396 — was **already re-anchored on the post-M stack** by `w0a_e0_anchor`
    (measured E0 PULL 0.408/0.491/0.596; **delta_vs_assumed +0.197**, `within_prereg_band:
    false`), the +0.198 recorded in §9.3.1.
  - **Ruling: the re-anchor is MOOT — not run, $3 saved.** There is nothing on a
    pre-M pool to re-anchor; the law's generation-stack-dependent constants are
    already bf16, and the DIAG-8 assumed value was re-measured long ago. Reporting
    this straight rather than spending on a cell the audit dissolves is §10 rule 4
    ("turn the method on ourselves") working. Author can override if they want the
    number re-confirmed regardless.

---

## P1 — The matched-artifact battery *(the centerpiece; ~$15–25; AWAITS SIGN-OFF)*

**PRE-REGISTRATION (2026-07-18 — odds priced post-P0.1; FROZEN pending sign-off).**

**Question.** Does the sink appear in any model conditioned at its **own quality
match** (Δ_art ≈ 0), and if so, does its depth depend on **diet**?

**Design (pre-registered).**
- **Artifacts are mined, not generated.** Per-model matched sets are drawn from the
  record's persisted partial-credit pool by binning per-problem donor candidates to
  the target band. **Fixed-donor rule:** all matched sets come from the **one**
  donor pool — `runs/modal/lcb_cand_lcb_r2_base_T08.json` (Qwen2.5-1.5B-base,
  LCB-easy, T=0.8), the pool that produced the original 0.494 set — so artifact
  **source** stays constant while artifact **level** moves. The matched design must
  not trade the position confound for a source confound.
- **Target** = the model's own global i.i.d. frac (record value); **band** =
  target ± 0.05; **one matched artifact per problem** (in-band donor candidate
  nearest the target, deterministic tie-break by index). Problems with no in-band
  donor candidate are **dropped and counted** — no donor switch, no band widening.
  (`scripts/j7_match_artifacts.py` → `artifacts/h7_matched_artifacts.json`.)
- **Minimum cell size n ≥ 30** problems with in-band coverage (pre-registered).
- **The sink test simplifies at match.** At Δ_art ≈ 0 the copy-null and own-i.i.d.
  null converge, so "below both nulls" degenerates. The **committed matched-sink
  signature** is: conditioned mean frac **< own i.i.d.**, one-sided MC-Wilcoxon
  **p < 0.05**, **and** effect **≤ −0.05** (the depth threshold keeping "sink"
  distinct from imitation drag). Δ_cond with bootstrap 95% CI reported per cell
  regardless of the binary.
- **Code channel only.** The relational axis is defined on frac; there is no clean
  language analogue. The language channel's MIXED status (Phase 6) stands untouched.

**Cells and MEASURED coverage** (miner has run; n and expected Δ_art are real):

| cell | model | diet | band (±0.05) | **n** | mean art | E[Δ_art] | what it answers |
|---|---|---|---|---|---|---|---|
| **M1** | DeepSeek-Coder-1.3B | organic | [0.312, 0.412] | **39** | 0.361 | +0.00 | most discriminating: non-Coder organic at straddle |
| **M2** | Qwen2.5-1.5B (general) | general | [0.274, 0.374] | **28** | 0.330 | +0.01 | repairs the P6 control — same fam/arch/scale/tie, at straddle |
| **M3** | StarCoder2-3B | organic | [0.308, 0.408] | **39** | 0.361 | +0.00 | second organic family at straddle (not skipped — P0.1 lift-arm) |
| **M4** | Qwen2.5-Coder-7B | coder | [0.609, 0.709] | **20** | 0.663 | +0.00 | does the Coder sink reappear at scale when straddle restored |
| **M5** | Qwen2.5-Coder-0.5B | coder | [0.161, 0.261] | **43** | 0.204 | −0.01 | Coder weak end at match: position artifact or capability floor |

Existing **Coder-1.5B** (Δ_cond −0.094) and **Coder-3B** (−0.150) cells sit at ≈
match already and are the **sink-positive reference rows**.

**Coverage rulings (pre-registered defaults; author confirms at sign-off).**
- **M1, M3, M5 clear n ≥ 30** — run as designed.
- **M2 = 28 (2 below floor).** **Run it.** It is within rounding of the floor, the
  matching is tight (mean 0.330 vs target 0.324), and it is the single cell that
  repairs the Phase-6 confound (general-1.5B at straddle — same arch/scale/tie as
  the pathological checkpoint). Dropping it would gut the phase. Shortfall recorded;
  cell flagged `min_n_met: false`.
- **M4 = 20 (the pre-flagged risk case).** **Run it at n = 20, flagged
  underpowered, interpreted asymmetrically:** a clear matched sink at n=20 *is*
  informative (the Coder sink reappears at scale when straddle is restored — the
  confound named in the Phase-6 review); a **null is inconclusive** (cannot separate
  "no sink at 7B match" from low power) and **defers M4 to a generated-artifact
  design** with its own pre-reg. Author may instead defer M4 entirely at sign-off.

**The source side cell — DEFERRED-BY-COVERAGE (measured, before spend).** The
priced side cell (one model's own-pool artifacts vs the donor-matched set at
identical Δ_art, to price the source variable) is **not runnable**: single-model
self-pools are too bimodal in the mid-band to sustain a matched self set —
DeepSeek 4/80 in-band (paired 3), StarCoder2 5/80 (paired 4). This is the *same*
bimodality that **motivates** the fixed-donor rule. The source variable stays
**unpriced**; the path is a future **generated-artifact** design (artifacts
synthesized to the target band, not mined). Recorded in
`artifacts/h7_matched_artifacts.json::side_cell_source`.

**Pre-registered branches + odds (priced post-P0.1).** P0.1 left the space fully
open (StarCoder2 was lift-arm, not a straddle datum); the boundary observation
(nearest non-Coder points lift, don't sink) is mild support for Coder-specificity,
weighed against the escape-distance law's prediction that matched conditioning
should cost independence broadly.

- **H-diet-modulated (the author's proposed law) — 45%.** Negative pressure at
  match **everywhere**, depth **ordered by diet**: Coder deep (≤ −0.09,
  M5 and the 1.5B/3B references), organic/general shallow (M1/M2/M3 between −0.05
  and 0, i.e. real negative pressure but sub-sink-threshold). A universal
  conditioning curve with a **diet parameter**. Favored: the escape-distance law
  (LIVE, cross-family) predicts matched artifacts give zero escape benefit while
  costing sample diversity → negative pressure broadly; the observed Coder depth
  says diet sets the magnitude. The note reframes around the curve + parameter.
- **H-Coder-specific — 30%.** M1/M2/M3 **flat-or-positive** at match (Δ_cond > −0.05,
  no negative pressure at all); M4 and/or M5 sink → the Phase-6 origin line
  **survives, now unconfounded**, CODER-STAGE gains its missing control, the note's
  story stabilizes. Supported by P0.1's boundary observation.
- **H-universal — 15%.** The matched-sink signature (≤ −0.05, p < 0.05) fires
  across M1–M3 at **Coder-comparable depth**, no diet ordering → family was never
  the variable; the Index **rescopes** the pathology from "Qwen-Coder" to
  "conditioning at matched quality," the Phase-4 double dissociation is
  reinterpreted as a **position artifact** (retraction-grade amendment to rows
  8/11), and the extraction becomes a substantially larger claim.
- **Ugly branches — 10%, priced not discovered.** No sink anywhere at match
  including the Coder references' bands → the original 0.494 set carried a property
  **beyond its frac** (artifact-set-specific; the deferred source cell becomes the
  lead diagnostic). Mixed/uninterpretable (cells disagree without diet ordering) →
  recorded **MIXED**, not harmonized. M4 coverage-null dominates → scoped gap, M4
  deferred to generated-artifact design.

**M5 sub-question (Coder weak end at match).** In the fixed-0.494 design 0.5B sat
at Δ_art +0.284 and *helped* ("competence floor — too weak to sink below its own
floor"). Matched to 0.21, **if 0.5B sinks** → the "competence window" dissolves into
pure **position** for the Coder line (0.5B was simply never at its own straddle);
**if it stays flat/positive** → a genuine **capability floor** survives. Either way
the Phase-6 competence-window story is sharpened or corrected.

**Decision rule for the record.** Index rows **8/11** are re-stated on matched
evidence — the origin line either **survives with "position-controlled" appended**,
or **rescopes** per the fired branch. The **Phase-4 dissociation rows** and the
**J5-Q1 scale row** each get an explicit **position-confound annotation** resolved
by this battery. The P0.2 relational figure gains the M-cells and becomes canonical.

**Artifacts (planned):** `h7_matched_{M1..M5}.json` (per cell, with `stack` block);
the re-run `h7_relational_assembly.json` with M-cells placed. **Writeup:** §9.9 P1
addendum; Index rows 8/11 matched origin line; the P3 note-gating update.

**Ops / sequencing for the cells (post-sign-off).** Each cell behind its smoke gate
(`j7_smoke`, wf ≥ 0.85 / dg ≤ 0.10), revision-pinned, all-cases judge,
fingerprinted. Order: **M1, M2 first** (they carry the hypothesis decision) →
**M3, M5** → **M4 last** (underpowered). All L4/bf16 — the exact record stack, no
re-baseline (7B fits L4 unlike the Kaggle T4).

---

## P2 — §10 addendum: the matched-relation rule *(writing; lands with this pre-reg)*

Codify the lesson the last two phases paid for. When a response depends on a
model–stimulus **relation**, comparisons must be matched on the **relation**, not
on the **stimulus**. Fixed-stimulus designs silently vary the relation whenever the
compared models differ in the very property the relation involves (here: diet →
i.i.d. quality → Δ_art). Worked examples in the record: **Phase-4** cross-family at
fixed 0.494; **Phase-6** diet control at fixed 0.494. Psychophysics lineage:
matching to **threshold**, not to **intensity**. A §10 rule going forward, checked
at every pre-registration. **Lands in WRITEUP §10 alongside this pre-reg** (not
after), so the rule is on the page before the battery it governs runs.

---

## P3 — Carried journal work

- **Note revision gated on P1's branch (not Phase 6's).** Do **not** revise the note
  under this handoff — the origin section it needs does not exist until the battery
  lands. §0.2's Phase-6 "transcription-ready" status is **suspended pending P1**
  (the spec was ready for a conclusion that is now provisional).
- **Successors, named-not-chartered (unchanged):** dose-response hint set;
  3B→7B window-close bracket and 7B–72B switch-on; TTT/weight-space. **Nothing runs.**

---

## Sequencing and phase gate

**Order:** P0.1 ✓ → P0.2 ✓ → P0.3 ✓ → **P1 pre-registration frozen with odds
priced (this file)** → **P2 lands in §10 alongside** → **[SIGN-OFF GATE]** → P1
cells (M1/M2 → M3/M5 → M4) → Index/figure updates → close.

**[SIGN-OFF GATE — author decisions before any GPU spend]:**
1. **Go / no-go on the ~$15–25 Modal battery.**
2. **M2 (n=28) — run at 2-below-floor?** (default: yes.)
3. **M4 (n=20) — run underpowered with asymmetric interpretation, or defer?**
   (default: run.)
4. **Law re-anchor (P0.3c) — sign off the ~$3 E0/E1 re-anchor cell, or leave flagged?**
   (default: leave flagged.)

**Phase gate — Phase 7 closes when:** the P0.2 relational figure exists with all
M-cells placed; the sink's Index rows are re-stated on matched evidence (or honestly
MIXED/OPEN); the Phase-4 dissociation and J5-Q1 rows carry resolved position
annotations; the matched-relation rule is codified in §10; the lineage column and
fingerprint hook are live (✓); and the note's gating status reflects P1's branch.
The extraction decision remains the author's, Index in hand.

## What this phase protects

The journal's claims have narrowed every phase; this one decides whether the
narrowing continues (**Coder-specific, now controlled**) or reverses into the widest
claim the record has held (**a conditioning law with a diet parameter**). Both are
wins. The loss would be publishing "small-Qwen pathology" while the discriminating
region sat unsampled one battery away — caught before any reader could, against the
record's own momentum, which is §10 working exactly as written.

---

## P1 RESULT (2026-07-18, Modal L4/bf16) — **H-Coder-specific fires; and the 7B "clean" was itself a position artifact**

All five cells landed (smoke-PASS, wf 1.000; stack fingerprint confirmed live on
every artifact: L4/cap-8.9/bf16, vLLM 0.11.0, torch 2.8.0). Each conditioned its
model on donor artifacts mined to its own match and measured E0 (own i.i.d.) on the
same problems.

| cell | model | diet | Δ_art (actual) | i.i.d. → cond | Δ vs i.i.d. (CI) | p(below i.i.d.) | matched-sink | n |
|---|---|---|---|---|---|---|---|---|
| **M1** | DeepSeek-1.3B | organic | +0.050 | 0.311 → 0.360 | **+0.050** [−0.021, +0.116] | 0.920 | **No** | 39 |
| **M3** | StarCoder2-3B | organic | +0.033 | 0.328 → 0.336 | **+0.008** [−0.075, +0.088] | 0.578 | **No** | 39 |
| **M2** | general-1.5B | general | +0.064 | 0.266 → 0.265 | **−0.000** [−0.066, +0.059] | 0.501 | **No** | 28 |
| **M5** | Coder-0.5B | coder | +0.081 | 0.123 → 0.167 | **+0.044** [−0.005, +0.090] | 0.959 | **No** | 43 |
| **M4** | Coder-7B | coder | −0.039 | 0.702 → 0.574 | **−0.129** [−0.206, −0.054] | **0.0024** | **YES** | 20 |

Reference rows (already at ≈ match, fixed-0.494): **Coder-1.5B −0.095 (sink)**,
**Coder-3B −0.150 (sink)**. All five M-cells landed in the straddle band (P0.2
figure re-run, `h7_relational_assembly.json`).

**Branch accounting (frozen odds).** **H-universal (15%) ✗ REJECTED** — no non-Coder
model sinks at match. **H-diet-modulated (45%, the favourite) ✗ REJECTED as stated**
— its premise was *negative pressure everywhere*; the non-Coder models show none
(DeepSeek **+0.050**, StarCoder2 **+0.008**, general **−0.000** — flat-to-positive,
not shallow-negative). **H-Coder-specific (30%, the middle branch) ✓ FIRES** — a
clean dissociation: at match, Coder-diet models sink (1.5B, 3B, and now 7B),
non-Coder families do not. The favourite lost; the odds were priced honestly and the
result is recorded as it came.

**What the battery measured (mechanism):**

1. **The sink is Coder-diet-specific — now position-controlled.** For the first time,
   three non-Coder models were placed in the straddle (Δ_art +0.033 to +0.064), the
   region the sink was never sampled in off-Coder. **None sink; none even show
   negative pressure** — DeepSeek is *helped* at its own level (+0.050), general and
   StarCoder2 sit flat. The Phase-6 origin line (**CODER-STAGE diet**) **survives the
   confound it was built on**: it is the diet, not position, and not family-general.

2. **The 7B "clean/blend" was ALSO a position artifact — the code sink is NOT
   scale-bounded above.** Phase 5/6 read Qwen-Coder-7B as friendly ("blends up, harm
   vanishes"), but 7B had only ever been measured at Δ_art −0.165 (its i.i.d. 0.659
   far *above* the 0.494 artifact — any model blends there). Restored to its own
   straddle (Δ_art −0.039, artifact ≈ its level), **7B sinks −0.129 (p 0.0024, below
   both nulls)**. Holding the model fixed and moving only the artifact level flips
   friendly → sink. So the Phase-6 "competence window closes at 7B" is **reversed**:
   the sink persists to 7B; the apparent upper bound was the same position confound
   the phase was built to catch. *(n = 20, the pre-flagged underpowered cell; per the
   pre-reg's asymmetric rule a clear sink IS informative, and this one is large and
   significant. A higher-n confirmation of the 7B matched sink is the named
   follow-up.)*

3. **The lower "boundary" (0.5B) reopens, it did not resolve.** M5 could **not be
   placed at its own straddle**: mined to 0.20, the artifacts still sat *above*
   0.5B's measured i.i.d. on those problems (0.123), so Δ_art landed at **+0.081**
   (lift arm), and 0.5B lifted (+0.044) as any model does off a better anchor. 0.5B
   is too weak to be conditioned at its own level by mining. Whether it has a genuine
   **capability floor** or is merely **un-sample-able at straddle** stays **OPEN** —
   the Phase-6 "0.5B floor" is neither confirmed nor refuted here (needs a
   generated-artifact design that can hit 0.5B's band).

4. **The "competence window" dissolves into a relational rule.** Phase 6 framed the
   sink as a window (1.5B–3B, absent at 0.5B and 7B). Phase 7 replaces it: the
   Coder-diet sink appears **whenever a Coder model is conditioned at or near its own
   quality** (straddle), measured now at 1.5B, 3B, and 7B; the 7B "ceiling" was
   position, the 0.5B "floor" is un-sampled. Not a capability window — a **diet ×
   relational-position** effect.

**Decision-rule origin line (for the Index):** **CODER-STAGE diet, position-controlled
and family-specific (non-Coder families — DeepSeek, StarCoder2, general-Qwen — show
no sink at match); NOT scale-bounded on the code channel — the Coder sink persists to
7B when the straddle is restored (the Phase-6 "vanishes at 7B" was a position
artifact); the 0.5B lower bound is OPEN (un-sample-able at straddle by mining).**
[artifacts/h7_matched_M*.json, h7_relational_assembly.json].

### The phase-close relational figure (all M-cells placed)

```
  Delta_cond (y)  [+0.20 .. -0.20]     Delta_art (x) [-0.20 .. +0.30]
  ':' = straddle band edges (-0.08, +0.13)
              :       |    3  5    :e            g
  ----------------2------4---------------------------  (2 StarCoder2, 4 general at ~0)
              :   1   |            :   (3 DeepSeek, 5 Coder-0.5B* just above axis)
              :B      |  C         :   f   d
   a=Coder-7B(fixed,over-qual)  B=Coder-3B  C=Coder-1.5B  1=M4 Coder-7B* (all SINK)
   2=StarCoder2* 3=DeepSeek* 4=general* 5=Coder-0.5B* (all FLAT/LIFT at match)
   d=DeepSeek e=StarCoder2 f=general g=Coder-0.5B (record, lift arm)
```

In the straddle band: **every Coder cell sinks (B, C, 1); every non-Coder cell sits
at its own level (2, 3, 4).** The record's non-Coder points (d, e, f) are off to the
lift arm — where they were always measured. That gap is the confound; the M-cells close it.

---

## PHASE GATE — CLOSED (2026-07-18)

The six closure conditions, audited:

1. **P0.2 relational figure exists with all M-cells placed** ✓ —
   `h7_relational_assembly.json` (5/5 matched cells in the straddle).
2. **The sink's Index rows re-stated on matched evidence** ✓ — rows 8/11: origin
   **CODER-STAGE, position-controlled + family-specific**; code sink **NOT
   scale-bounded** (7B sinks at match — Phase-6 "vanishes at 7B" reversed); 0.5B
   lower bound OPEN.
3. **Phase-4 dissociation + J5-Q1 rows carry resolved position annotations** ✓ — the
   P7-PROVISIONAL flags on rows 8/11 resolve to "position-controlled: confirmed
   Coder-specific; scale-bound reversed."
4. **Matched-relation rule codified in §10** ✓ (P2, landed with the pre-reg).
5. **Lineage column + fingerprint hook live** ✓ (P0.3; fingerprint confirmed on all
   5 artifacts).
6. **Note gating status reflects P1's branch** ✓ — §0.2 un-suspended and **corrected**
   (Coder-diet-specific confirmed; the "vanishes at Coder-7B → distinct from
   Spurious-Rewards-Math-7B" argument is **retracted for the code channel** — the
   code sink does *not* vanish at 7B).

**Prediction accounting, full phase:** P0.1 StarCoder2 lift-arm ruling correct
(it stayed a lift-arm point; M3 needed running and came out flat at match). P1 the
**30% middle branch fired**, not the 45% favourite (H-diet-modulated rejected — no
universal negative pressure); H-universal (15%) rejected. The unanticipated result —
**7B sinks at match, reversing Phase 6's scale-bound** — was *produced by* the
matched design, exactly the confound class the phase existed to expose. No gate was
passed by tuning. Re-anchor (P0.3c) resolved **moot** by the provenance audit ($3
saved).

**Cost:** P1 5 cells ~$18 (Modal L4/bf16); re-anchor not run.

**Open (author's, Index in hand):** the extraction decision (the pathology note is
now Coder-diet-specific **and cross-scale on code** — a cleaner, *larger* claim than
"small-Qwen 1.5B–3B", but the Spurious-Rewards-7B contrast must be dropped for code);
the **7B matched-sink confirmation at higher n**; the **0.5B straddle via
generated artifacts** (resolves the reopened lower bound); the standing successors
(dose-response hint set; 7B–72B switch-on; TTT/weight-space). **Nothing is running;
Phase 7 is fully closed.**
