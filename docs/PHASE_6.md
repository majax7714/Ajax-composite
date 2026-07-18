# Phase 6 — where the pathology comes from, and making the record extraction-ready

*Charter received 2026-07-17. Append-only; every run pre-registered with odds and
decision rules committed before it launches. This document is the Phase-6
pre-registration and result log.*

> **DRAFT STATUS (2026-07-17).** P0 is complete and its result reshapes P1's
> hypothesis space (H-tie demoted — see below). P1's priced odds and the H-tie
> ruling await author sign-off before this file is committed and frozen. P2's
> floor prediction is computed and committed here. Nothing has run on GPU.

## 0. Charter

**Charter question:** where does the small-Qwen conditioning pathology come from,
and is the record referee-hard at every point an extraction would lean on?

**Framing note (from the author, governing this phase).** There is no "mechanism
paper" and this phase does not create one. The journal is the artifact;
extractions are projections of journal state, made when the Index says a
claim-set is ripe — not targets the experiments serve. Phase 6 therefore contains
**no work item called "write the paper."** It contains: one origin question with
a live fork (**P1**), one verification that converts a computed defense into a
measured one (**P2**), and journal work that makes any future extraction — the
pathology-note revision included — a transcription job rather than a research job
(**P3**). We structure with everything in mind; nothing below exists to prove a
claim.

**State entering the phase (Phase 5 / J5 CLOSE, 2026-07-17).** The conditioning
pathology is a Qwen2.5-Coder-1.5B property (7B blends on code, language harm
vanishes); self-production does not switch on by 7B (branch (a); production-adequacy
scale curve 0/68 → 1/76 → 5/101; the cascade remains the deployable shape). The
false-zero floor instrument stands at **4-for-5**, its one falsification having
exposed a same-seed harness confound (≈ 45–50% screen-pool regeneration in
same-seed "fresh" B1 arms) — now a record-wide §8 caveat with a *computed*, not
yet *measured*, survival argument for every affected conclusion.

## 1. Standing rules (unchanged, plus one promotion)

- Append, never revise; retractions/amendments dated and in place.
- Pre-register before running: predictions, odds, decision rules committed first;
  falsified predictions stay on the page.
- No learned verifier anywhere.
- Reconciliation-ledger entry (§11) for every external result used in design.
- §8 operational hardening applies to all runs — including the **sharded-judge**
  pattern from the J5 hard screen where all-cases judging is required.
- Claims & Scope Index updated as part of every item; the phase does not close
  with the Index stale.
- **(PROMOTED this phase, from the J5 diagnostic) Distinct-seed protocol is now
  mandatory:** any arm described as a *fresh draw* uses a seed distinct from the
  seed that built the population it is compared against. Codified in §8 and §10
  as part of P2's writeup — the protocol exists because a committed floor test
  caught its absence. **P2 is its inaugural application, on the single number
  that matters most.**

---

## P0 — Config gates and free checks *(zero dollars; done first; results gate P1)*

**RESULT (2026-07-17).** All flags pulled from HF `config.json` / safetensors
headers; nothing generated. [scripts — the pulls are one-shot `curl`/header reads,
recorded here rather than persisted as an artifact.]

### P0.1 Tie flags + architecture + revision pins

| model | `tie_word_embeddings` | hidden / layers / kv-heads | behavior in record | revision (main) |
|---|---|---|---|---|
| Qwen2.5-Coder-0.5B | **true** | 896 / 24 / 2 | untested (P1 left anchor) | `8123ea2e9354afb7ffcc6c8641d1b2f5ecf18301` |
| Qwen2.5-Coder-1.5B | **true** | 1536 / 28 / 2 | **pathological** (SINK; language harm) | `df3ce67c0e24480f20468b6ef2894622d69eb73b` |
| Qwen2.5-Coder-3B | **true** | 2048 / 36 / 2 | untested (**P1 crux**) | `09d9bc5d376b0cfa0100a0694ea7de7232525803` |
| Qwen2.5-Coder-7B | **false** | 3584 / 28 / 4 | friendly (blend; harm vanishes) | `0396a76181e127dfc13e5c5ec48a8cee09938b02` |
| Qwen2.5-1.5B (general) | **true** | 1536 / 28 / 2 | untested (**P1 recipe split**) | `8faed761d45a263340a0528343f099c05c9a4323` |
| deepseek-coder-1.3b-base | **false** | 2048 / 24 / 16 | friendly (SINK inverts) | `c919139c3a9b4070729c8b2cca4847ab29ca8d94` |
| starcoder2-3b | **true** *(field absent; header-confirmed: single `model.safetensors`, 484 tensors, only `model.embed_tokens.weight`, no separate `lm_head`)* | 3072 / 30 / 2 | friendly, **code channel** (SINK inverts, +0.046 n.s.); language channel untested | `733247c55e3f73af49ce8e9c7949bf14af205928` |

Reference expectation (Qwen2.5 Technical Report, Table 1) confirmed: Qwen2.5
0.5B/1.5B/3B tie embeddings, 7B unties. The tie boundary in the Coder line falls
**exactly at 3B → 7B**, co-incident with a GQA/width discontinuity (kv-heads 2→4,
hidden 2048→3584) — the two are confounded at that boundary and this battery
does not isolate them.

### P0.2 Admission-rule resolution — **H-tie demoted to an interaction term**

The committed admission rule: *"if DeepSeek-Coder-1.3B ties embeddings, H-tie is
inadmissible as a standalone explanation — a tied, organically-trained,
conditioning-friendly model at 1.3B falsifies 'tying ⇒ pathology' before a dollar
is spent."*

- **Literal trigger (DeepSeek):** did **not** fire — DeepSeek-Coder-1.3B is
  **untied** (false). By the letter, H-tie is not demoted.
- **The rule's stated logic:** is nonetheless satisfied — by **StarCoder2-3B**,
  which is **tied**, organically trained (The Stack), and conditioning-**friendly**
  on the code channel (Phase 4 H1: no below-both-nulls sink; +0.046). That is
  exactly the falsifier the rule describes, in a model already in the record.
- **Resolution (recorded, recommended to the author):** apply the rule by its
  **stated logic**. "Tying ⇒ pathology" as a **sufficient** cause is **falsified**
  — a tied, organic, friendly 3B model exists. H-tie survives only as a possible
  **necessary condition / interaction term** (every pathological model observed so
  far is tied, but n = 1, and tying alone does not produce the pathology).

**Cross-tab that forces it** (behavior from Phase 4/5; tie from P0):

| | tied | untied |
|---|---|---|
| **pathological** | Qwen-Coder-1.5B | — (none observed) |
| **friendly** | **StarCoder2-3B**, (Qwen general/0.5/3B untested) | Qwen-Coder-7B, DeepSeek-1.3B |

Tie is **not sufficient** (StarCoder2 counterexample). It may still be necessary
(all pathological-so-far are tied) but the record cannot yet claim that at n = 1.

**Consequence for P1's branch semantics (per the charter's own pre-written
clause):** a **step** at the tie boundary can no longer *promote* H-tie — "if P0
demoted it, a step becomes an **open anomaly** recorded as such — do not resurrect
a falsified hypothesis to explain a convenient shape." A step would then point at
the *bundled* 3B→7B discontinuity (tie + GQA + width), not at tying specifically.

### P0.3 License note (repro-repo, costs nothing at run time)

**Qwen2.5-Coder-3B is Qwen-Research-licensed, not Apache-2.0.** Irrelevant to
running the P1 cells; relevant to what a future reproduction repo may
redistribute. Recorded here so it costs nothing at repo-extension time. (All other
record models: Apache-2.0 / bigcode-openrail-m for StarCoder2 / deepseek license.)

---

## P1 — The pathology-origin discriminator battery *(~$20–30; the phase centerpiece)*

**PRE-REGISTRATION (2026-07-17 — odds priced post-P0; FROZEN pending sign-off).**

**Question:** is the small-Qwen conditioning pathology a **capacity × diet**
interaction (the "synthetic tax"), an **architectural discontinuity**, or
**recipe-deep**? *(H-tie, the sharp architectural hypothesis, was demoted at P0;
"discontinuity" now denotes the bundled tie+GQA+width change at 3B→7B and is a
low-odds open branch, not a promotable hypothesis.)*

**Design.** The two established cheap cells — **CELL A**, the 44-frozen-artifact
code-conditioning cell (E0 i.i.d. vs E1 conditioned, k=8, all-cases judge, mean
`frac_tests`), and **CELL B**, the 20-problem hint/language-manipulation cell
({E0, HINT} × k=25, per-sample mean pass) — run on three new checkpoints, each
behind a per-checkpoint smoke gate first (8×8 on the frozen scaffold, wf ≥ 0.85 /
dg ≤ 0.10). Both cells' frozen inputs are model-independent and present (the
44-artifact triplet; `artifacts/h2_hints_frozen.json`, 20 manip qids + 125 hints).

| checkpoint | what it discriminates |
|---|---|
| **Qwen2.5-Coder-3B** (tied) | the **crux**: capacity×diet predicts partial attenuation (a **slope**, 3B intermediate between 1.5B and 7B); a **step** (3B fully pathological, cliff to 7B) is now an **open anomaly** — the two live readings disagree here and nowhere else this cheaply |
| **Qwen2.5-Coder-0.5B** (tied) | anchors the curve's left end; capacity×diet predicts **worse-than-1.5B** |
| **Qwen2.5-1.5B** (general, tied) | splits **diet** from **recipe**: sinks → base-recipe-deep; clean → the Coder continued-pretraining stage did it. *(Also a second, independent test of H-tie: a tied non-Coder model — clean here reinforces P0's demotion.)* |

Existing 1.5B and 7B Coder cells complete a **five-point size curve** (0.5 / 1.5 /
3 / 7B Coder + general-1.5B off-axis).

**Free riders (compute nothing extra; analyze from the same pools):**
(a) **copy-fidelity-vs-size** curve — if fidelity recovers exactly where the sink
vanishes, that is a zero-cost mechanism fingerprint; (b) **blend-geometry** position
(conditioned frac relative to the copy-null and own-iid) per checkpoint, so every
cell lands on the same figure as J5 Q1a.

**Pre-registered branches + odds (code channel — the 3B crux + 0.5B anchor).**
The branch set includes the ugly ones by design.

- **Slope** (0.5B ≤ 1.5B, 1.5B > 3B > 7B, monotone attenuation, 3B clearly
  intermediate) → **H-capacity×diet ("the synthetic tax") promoted**; the note's
  §5 rewrites around the interaction with the size curve as its evidence — **50%**.
- **Step** (0.5B ≈ 1.5B ≈ 3B all pathological; cliff at 3B→7B) → **OPEN anomaly**,
  recorded as such (H-tie stays demoted; the bundled 3B→7B discontinuity is the
  suspect, un-isolable here) — **20%**.
- **Non-monotone** (0.5B not worse than 1.5B, or 3B worse than 1.5B) →
  checkpoint-specific; low odds, but priced not discovered — **15%**.
- **0.5B uninformative** (near-degenerate: everything floored / smoke marginal, no
  readable contrast) — reported as such — **15%**.

**Recipe locus (general-1.5B cell).**
- **general-1.5B clean** (conditioned within the blend band, no below-both-nulls) →
  **Coder-stage diet**; the synthetic-code-data story regains standing as one
  factor of the interaction, scoped honestly — **55%**.
- **general-1.5B sinks** (below both nulls, the 1.5B-Coder signature) →
  **recipe-deep**; the note's title and the Index rescope from "Coder" to
  "Qwen2.5-small" — **30%**.
- **middle / ambiguous** — **15%**.

**Language channel (CELL B, per checkpoint).** Each checkpoint carries its own
vanish/harm bands mirrored from the J5 Q1b registration: **harm vanishes**
(mean Δ > −0.02) / **harm persists** (Δ < −0.05) / middle. Prior (shared across
checkpoints, not per-cell odds): the language harm attenuates with scale as the
code sink does — present at 1.5B (Δ −0.096), gone at 7B; 3B expected intermediate.
Saturation caveat pre-declared per cell (if E0 mean pass > 0.9, the cell is
compressed and reported as such).

**Decision rule for the record.** The pathology's Index row (row 8/11) gains a
**measured origin line**: INTERACTION (slope) / DISCONTINUITY-OPEN (step) /
RECIPE-DEEP or CODER-STAGE (general-1.5B cell) / OPEN (non-monotone or
conflicting). The note's §5 is rewritten to state exactly what the battery
measured **and no more**. If the branches **conflict across channels** (code says
slope, language says step) → record **MIXED** and resist harmonizing; a two-channel
disagreement would itself be the finding.

**Artifacts (planned):** `h6_pathology_origin_{0p5b,3b,qwen15b_general}.json`
(one per checkpoint, both cells + free riders); `h6_size_curve.json` (the joined
five-point figure). **Writeup:** §9.9 P1 addendum; Index rows 8/11 origin line; the
P3 note revision.

---

## P2 — Distinct-seed verification of the flagship number *(~$2–3; the floor instrument's SIXTH out-of-sample test)*

**PRE-REGISTRATION (2026-07-17 — the prediction is COMPUTED AND COMMITTED below,
before any arm runs).**

**Why.** The §8 harness caveat currently defends the record's single most positive
result — **Qwen HINT-50 = 13 vs floor ≈ 2, p = 4.9 × 10⁻⁴** (§9.8) — with a
*computed* argument: the same-seed B1 control is suppressed, so the contrast is
conservative. A hostile reader who stops at "the control arms were ~50% replays"
will not read the computation. **One run converts the defense from argued to
measured**, and inaugurates the mandatory distinct-seed protocol on the exact
number that matters most.

**Design.** A fresh **B1-50 on the frozen Qwen 68-problem medium stratum**,
**distinct seed** (recorded), frozen config (base Qwen2.5-Coder-1.5B, T=0.8,
top_p 1.0, fenced completion, hardened judge — short-circuit, recovery is the
analysis).

**Committed floor prediction** (reproduced from the frozen 1.5B medium screen pool
via the exact W0c machinery — `scripts/j6_p2_floor_predict.py`,
`w0_recomputes._fit_mixture`; stratum 68/78, near-misses x=1:5 / x=2:2, mixture
α 0.045 / β 3.32 / π₀ 0, reproducing §9.6's recorded 2.01 to the decimal):

> Because the distinct seed makes the **effective fresh-draw count the full 50**,
> the "corrected E under true-fresh draws" **is** the fit's native E — the J5
> same-seed suppression (which pulled the observed same-seed B1 down toward ~1)
> no longer applies. Premise stated on the page.
>
> **E[fresh B1-50 recoveries] = 2.01; point prediction 2; ~94% band [0, 4]
> (Binomial(68, q=0.0296), actual mass 0.949); ≥ 5 falsifies the fit
> (P(X≥5) = 0.051).** The band is **one-sided** (floor-bounded at 0): P(X≤1) =
> 0.398, so no low-end falsifier exists and the "below-band / over-correction"
> outcome is **not reachable** for this near-floor E — recorded so the branch set
> is honest.

**Scoring (committed):**
- **in-band [0, 4]** → the corrected floor reading is **verified on a measured
  control**; the 13-vs-floor contrast stands measured; Index row 10 (HINT) gains
  "distinct-seed verified"; §8 caveat amended **computed → measured**.
- **above-band (≥ 5)** → the original floor was **under-stated**; record it
  straight, recompute the HINT contrast against the measured control (paired
  McNemar, HINT-13 vs the distinct-seed B1), and let the number be what it is.
- **below-band** → not reachable (see above); if a future two-sided near-floor
  case arises, below-band would read as fit over-correction (instrument info).

**Writeup:** §8 caveat amended (computed → measured, or the converse per branch);
§10 addendum codifying the distinct-seed protocol; Index rows 10/15 updated.
**Artifacts:** `scripts/j6_p2_floor_predict.py` (committed prediction, this file);
`h6_p2_distinct_seed_b1.json` (the run result, planned).

### P2 RESULT (2026-07-17) — **in-band; the flagship floor is now measured, not argued**

Distinct-seed (41) fresh B1-50 on the Qwen 68-problem medium stratum recovered
**2** — the committed point prediction exactly (E 2.01, band [0, 4]). **The floor
instrument's 6th out-of-sample test HITS → 5-for-6** (its first genuinely-fresh
draw on the flagship stratum). [artifacts/h6_p2_distinct_seed_b1.json].

- **Decorrelation confirmed:** the distinct-seed arm is **0.27** byte-identical to
  the screen pool, vs the same-seed **~0.50** the J5 diagnostic measured — the
  distinct seed did its job (a genuinely-independent control, not a half-replay).
- **The §8 caveat converts computed → measured.** Same-seed suppression is now
  *shown* invisible at this near-zero floor: same-seed and distinct-seed B1 both
  recovered 2, exactly as §8 argued ("halving E ≈ 0–2 moves nothing"). So the
  flagship **HINT-13-vs-floor-2** contrast (p = 4.9e-4) stands on a **measured
  distinct-seed control**, not a computed one — the referee objection ("the control
  was ~50% replays") is answered with a number.
- **No below-band branch was reachable** (one-sided floor), and none occurred.

Writeup landed: §8 caveat amended (computed → measured); §10 addendum codifying
the distinct-seed protocol; Index rows 10 (HINT: distinct-seed verified) and 15
(floor: 5-for-6); §0.3 rows 10/15 updated.

---

## P3 — Extraction-readiness *(journal work; no paper is written under this handoff)*

1. **Claims-to-evidence tables (journal infrastructure).** For each Index row with
   status LIVE or SCOPED, extend the row (or an appendix table) with: the exact
   artifacts/sections evidencing it, the statistical test + number, the scope
   line, and any §8 caveat that attaches. Index maintenance one level deeper — the
   table any future extraction transcribes. After P3, extracting means **selecting
   rows, not re-deriving support**. *(Startable immediately; independent of P1.)*
2. **The pathology-note revision** (the one extraction that already exists as a
   draft) — rewritten around P1's fired branch: title rescoped per J5-Q1
   (small-Qwen, not family); the **third dissociation axis** added (within-family
   **scale**: 1.5B pathological, 7B clean); §5 replaced by the **measured origin
   line**; the Spurious-Rewards relationship corrected (their effect is at
   Math-7B; ours **vanishes** at Coder-7B — two distinct Qwen phenomena, stated as
   such); limitations updated (3B license note; whatever P1 leaves open).
   Submission decisions held for the author; the revision itself is P3 work.
   *(Waits on P1's branch.)*
3. **Successor questions — named, not chartered, carried forward without
   commitment:** the **dose-response hint set** (J2's ceiling-limited instrument;
   the richness threshold remains unmeasured, disclosed wherever cited); the
   **7B–72B switch-on bracket** (PlanSearch ledger frame; a phase of its own if
   ever chartered); **TTT / weight-space channels** (outside the elimination
   argument's scope, recorded as such since Phase 4). **None run under this
   handoff.**

---

## Sequencing and phase gate

**Order:** P0 ✓ → **P1 pre-registration frozen** (odds priced post-P0 — this file,
pending sign-off) → **P2 committed and run** (independent of P1, cheaper; interleave
once its prediction is committed — it is) → **P1 cells** → **P3** (items 1 and 3
startable now; item 2 waits on P1's branch).

**Phase gate — Phase 6 closes when:**
1. the pathology's Index row carries a **measured origin line** (or an honest
   OPEN / MIXED);
2. the flagship HINT contrast stands on a **distinct-seed measured control**, §8
   caveat amended accordingly;
3. the **distinct-seed protocol** is codified in §8/§10;
4. every LIVE/SCOPED Index row carries its **claims-to-evidence extension**;
5. the **note revision** reflects P1's branch.

Extraction decisions — whether, what, where — are then made by the author with the
Index in front of them.

## Readiness / plumbing notes (2026-07-17)

- **CELL A / CELL B frozen inputs:** present and model-independent (the 44-artifact
  triplet — `w0b_copy_null.json`, `lcb_cand/res_lcb_r2_base_T08.json`, recomputed to
  exactly 44; and `h2_hints_frozen.json`, 20 manip qids + 125 hints). **No data work.**
- **Runner gap (small refactor, not data):** the J5 template `modal_h1.py::j5_q1`
  (+`j5_smoke`, `j5_prefetch`) **hardcodes** `QWEN7B` and uses **un-namespaced**
  cache tags + a fixed output path (`h5_7b_pathology.json`) — re-running it on a new
  checkpoint would silently hit the 7B cache and collide on output. Phase 6 needs:
  (i) a `model_id`/short-name arg on those entrypoints; (ii) every volume/local tag
  suffixed by model; (iii) output path `h6_pathology_origin_{name}.json`; (iv)
  `revision=` pins threaded into `snapshot_download` / `LLM` / `AutoTokenizer`
  (**currently absent everywhere** — required by P0's revision-pin standard). The
  suffix idiom already exists in-file (`h2_manip` `suf`, `h1_smoke`/`h1_battery`
  `{family}`) — copy it. This is prep work, not a run.
- **Judge:** CELL A needs the **all-cases** judge (frac consumed); CELL B is
  short-circuit. Right-size containers per the §8 cost rule; shard if a screen
  exceeds a container ceiling.

*(Revision pins in P0.1 are the exact `main` SHAs resolved 2026-07-17; pin these in
the runner and the repro standard.)*

---

## P1 amendment — Kaggle re-baseline of the battery *(2026-07-17, before any P1 run)*

**Trigger.** Free Kaggle GPU quota (reset). The author chose to move P1's spend
there; P2 stays on Modal (the flagship number is not worth a stack confound —
[decision recorded 2026-07-17]). Kaggle is a **new stack boundary**
(Modal-L4/vLLM → Kaggle-T4/vLLM), and P1 is a comparison against the
Modal-generated 1.5B/7B reference cells. Per §8/D14 (*"numbers never cross the
stack boundary"*) and the **Phase-M precedent** (M3 *re-baselined* on the new
stack rather than cross-comparing), the disciplined move is to re-baseline, not
to graft Kaggle cells onto a Modal curve.

**What changes:** the *substrate* only. The scientific question, the branches
(Slope / Step-OPEN / Non-monotone / recipe-locus), the odds, the frozen cell
inputs (44-artifact triplet, 20-problem hint set — model-independent), the smoke
gate, and the revision pins are **unchanged**. What moves is where the
conditioned generations are drawn.

**T4 constraint (measured from `kaggle_launch.py`: `machine_shape` is pinned to a
single `NvidiaTeslaT4`, 16 GB).** 7B bf16 (15.2 GB weights) does **not** fit a
single T4 with any KV budget. So the re-baseline covers the **four T4-feasible
points** — Qwen2.5-Coder **0.5B / 1.5B / 3B** and **Qwen2.5-1.5B (general)** — run
fresh on Kaggle, forming a self-consistent within-stack sub-curve over exactly the
range where the slope-vs-step decision lives (0.5 → 3B). The **7B** "friendly
blend" endpoint (`h5_7b_pathology.json`, cond 0.609) **stays the
Modal-established result**; it is not re-run.

**Committed stack-comparability anchor (pre-registered here, before the run).**
The Kaggle **1.5B** cell is the anchor. It passes iff, on the same 44 frozen
artifacts, seed 17:
1. the **below-both-nulls signature reproduces** — conditioned mean frac < copy-null
   (0.494) **and** < own-iid, one-sided MC-Wilcoxon p < 0.05 vs copy (the Modal
   result was p ≈ 5e-5), matching Modal's qualitative pathology; **and**
2. the conditioned mean frac lands **within ±0.05 of Modal's 0.374**.

- **Anchor passes** → the Kaggle T4 stack is comparable to the Modal L4 reference;
  the Kaggle sub-curve is interpretable against the record, and the
  3B(Kaggle)-vs-7B(Modal) blend comparison is **licensed** (reported with the
  cross-stack flag). The origin call proceeds on the five-point view.
- **Anchor fails** (signature flips, or |Δ| > 0.05) → **the stack matters**, which
  is itself a recorded finding. The Kaggle curve then stands **internally**
  (0.5/1.5/3B + general, one stack) for the slope-vs-step call, the Modal-7B
  cross-comparison is **dropped** (not fudged), and the origin line is scoped to
  "≤ 3B on Kaggle-T4" with the stack sensitivity noted.

**Ops.** New self-contained kernel `scripts/j6_kaggle_pathology.py` (vLLM bf16 gen
+ the `h1_lcb_exec` judge, wording duplicated verbatim from `modal_h1.py` with a
sync note — the kernel image has no `modal` import); wired into
`scripts/kaggle_launch.py` (bundle carries the two frozen R2 pools via
`BUNDLE_EXTRAS`; per-checkpoint MODES; a vLLM install variant). Internet-enabled
kernel, revision-pinned model download, seed 17 (same config as Modal — only the
GPU/stack differs). Per-checkpoint smoke gate first (wf ≥ 0.85 / dg ≤ 0.10).
Outputs `runs/kaggle/<mode>/` → `artifacts/h6_pathology_origin_kaggle_<name>.json`.
The five-point join + free-rider curves land in a local CPU analysis
(`j6_size_curve.py`) once cells return.

### P1 Kaggle smoke — FAILED (2026-07-17): the T4 cannot run bf16

The qwen3b smoke (`rgr-j6-qwen3b-smoke`) reached the GPU and failed at engine
init with a **hard, informative** error:
`ValueError: Bfloat16 is only supported on GPUs with compute capability ≥ 8.0.
Your Tesla T4 GPU has compute capability 7.5. You can use float16 instead.`
[runs/kaggle/j6_qwen3b_smoke/rgr-j6-qwen3b-smoke.log].

**The free-Kaggle re-baseline's premise is broken.** Kaggle's free accelerators —
T4 (sm_75) and P100 (sm_60) — are both **pre-Ampere** and cannot run bf16 under
vLLM; the launcher already pins T4 (P100's sm_60 is dropped by Kaggle's torch).
The record's stack is **bf16** (D11). So Kaggle can only run **fp16**, which is a
**precision** boundary, not just the GPU boundary the amendment assumed — a bigger
stack change, and one the record has never crossed. The smoke gate did exactly its
job: caught the wall before any battery spend.

**Options, decision pending (author's call):**
- **(A) Kaggle fp16, anchor-gated** — set the kernel `dtype="float16"`, run the
  1.5B cell first (free) as combined smoke + *precision* anchor. If fp16-1.5B
  reproduces the bf16 signature (below-both-nulls, 0.374 ± 0.05) → free fp16
  battery, scoped "fp16, anchored to bf16"; if it drifts → fp16 changes the
  measurement and we fall back. Free if precision transfers; self-correcting.
- **(B) Modal bf16** — run the battery on the **already-built** Modal j6
  entrypoints (`j6_prefetch/j6_smoke/j6_pathology`, L4/bf16). Exact record stack →
  **no re-baseline and no anchor needed** (new cells compare directly to the
  existing Modal 1.5B/7B); zero new work; ~$20–30. The original frozen P1 design.

**DECISION (2026-07-17): (B) Modal bf16** [author's call]. The Kaggle re-baseline
(and its fp16 workaround) is **retired** — the T4 bf16 wall makes free Kaggle a
precision change the phase centerpiece shouldn't carry. P1 runs on the existing
Modal j6 entrypoints, same L4/bf16 stack as the 1.5B/7B reference, so **the
ORIGINAL frozen P1 pre-registration applies unchanged**: no re-baseline, no stack
anchor, branches/odds as frozen. Only the **three new checkpoints**
(Qwen-Coder-0.5B, 3B, general-1.5B) are generated; the 1.5B (`dmeasure_d2c_partial_credit.json`)
and 7B (`h5_7b_pathology.json`) cells are the existing Modal results. The Kaggle
kernel + launch integration stay in the tree (unused) as the recorded
infrastructure of a measured dead-end.
