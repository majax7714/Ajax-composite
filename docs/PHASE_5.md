# Phase 5 — the journal turn, and where direction comes from

*Charter received 2026-07-16. Append-only; every run pre-registered.*

## 0. Charter

**Two jobs.** (1) **J0, the reframe:** the record stops being scaffolding for a
claim and becomes the primary artifact — an experimental journal. The history is
the argument: the register claim nulled; both audited successor claims (H1, F2)
fell; the central mechanism claim reversed under its own missing arm — and at
every step the retraction was more informative than the claim it replaced. Papers
become *extractions from journal state*, not the thing the journal serves.
(2) **The direction tranche:** every run in this phase points at one question the
Phase-4 results opened — **where does direction come from, and is its absence
Qwen's or universal?**

**Order:** J0/J1/J2 (writing + free) → J3 (Qwen self-hint; rides the existing
stratum) → J4 (DeepSeek four-arm battery; the centerpiece) → J5 (7B sign-off
decision — costed, presented, **not run**).

**The reframe's failure mode, named in advance (lands as a §10 addendum):** the
journal turn relaxes nothing. Without a claim as organizing pressure, the drift
risk is wandering — running whatever is fun and narrating it afterward. The
counter-pressure stays exactly what it has been: every run pre-registered against
a named question with predictions, odds, and decision rules; every phase
chartered; every verdict appended and dated. The unit of progress changes from
"claim defended" to "question closed with scope." Chasing meaning in failures
only works if the failures are failures of something specific.

**Standing rules:** unchanged (append-never-revise; pre-register with odds; no
learned verifier anywhere; reconciliation ledger for every external result used
in design; §8 ops hardening), **plus one new rule from J0: every phase's writeup
work includes updating the Claims & Scope Index; a phase is not closed with the
index stale.**

**Phase gate:** Phase 5 closes when the reframe is landed (J0, index seeded and
current); the production question has a measured answer on two families (J3,
J4); the trace-content claim carries a cross-family scope line (J4); the hint
dose-response is graded (J2); and the 7B decision is costed and presented (J5).
Then the extraction decision is made with the Index in front of us.

---

## J0 — the reframe (writing; landed in WRITEUP-rgr.md)

Deliverables: retitle + journal header; abstract framing paragraph (the composite
nature, stated); §10 physically promoted to directly after the abstract
(numbering retained so every existing §10 cross-reference stays valid; move
noted in place); **Claims & Scope Index** seeded as §0 (every claim the record
has made — status, scope line, pointer); **Instruments** (§0.1) and **Extraction
candidates** (§0.2) subsections; §10 addendum (the failure mode above); the new
index-maintenance standing rule.

**J0 DONE (2026-07-16).** Retitle landed (original title preserved in place);
journal-identity header + one-breath arc; abstract framing paragraph; §10
physically moved to directly after the abstract with a promotion note (numbering
retained; reading order 10 → 0 → 1 stated); §0 Claims & Scope Index seeded with
15 claims (statuses: 2 KILLED, 2 RETRACTED, 1 SCOPED+INVERTED, 1
REVERSED-AS-REFINED, 9 LIVE incl. 1 LIVE-BUT-INFERRED — the J3/J4 target); §0.1
Instruments (7 entries); §0.2 Extraction candidates (3, each with its missing
Phase-5 data named); §10 addendum (wandering failure mode + the index rule).

---

## J1 — ledger entries (2026-07-16, DONE)

Self-planning (Jiang et al.), PlanSearch (2409.03733), and the HMT/Codex 7B-fork
amendment landed in §11 (list + ledger). Commit `81324e2`.

## J2 — hint-informativeness grading

**PRE-REGISTRATION (2026-07-16, frozen before any grading).**

**Question:** the direction-richness dose-response on the channel that works — do
the 13 stratum recoveries concentrate in fully-specified strategies, or do nudges
suffice?

**Rubric (frozen):** each hint graded, seeing only the problem statement and the
hint, as exactly one of —
- **COMPLETE** — names a full solution strategy: following it mechanically
  (algorithm plus its key decisions) suffices to write a correct program; no
  essential idea is missing.
- **PARTIAL** — names the core technique or one key observation but leaves at
  least one essential design decision unstated (data structure, case split,
  second phase, critical edge handling).
- **NUDGE** — orientation only: restates or reframes the problem, flags a
  pitfall, or names a generic technique without problem-specific instantiation.

**Blindness protocol, with the exposure stated honestly:** the orchestrating
session has seen the recovery outcomes, so it does **not** grade. Grading is
performed by a **fresh model instance** (same model family that drafted the
hints; recorded) whose entire input is the frozen rubric plus the 125
(problem statement, hint) pairs in **shuffled order (seed 17), with all group
labels and any outcome information stripped**. Grades are returned per qid;
the orchestrator only then joins grades to outcomes.

**Analysis (frozen):** primary test — COMPLETE-share among the 13 recovered
stratum problems vs the 55 non-recovered stratum problems, Fisher exact,
one-sided (recoveries richer). Ceiling guard, pre-declared: if > 80% of the 68
stratum hints grade COMPLETE, the test is **ceiling-limited / UNINFORMATIVE**
and is reported as such (the drafter wrote full strategies where it could — a
property of the hint set, not of the channel).

**Pre-registered readings (odds):** **(a) concentration** (p < 0.05) → the
channel needs full strategies; the cascade is hard — the hint-producer must
essentially solve the problem at approach level — **35%**. **(b) no
concentration** → nudges suffice; the production bar drops substantially —
**40%**. **(c) ceiling-uninformative** — **25%**.

**Outputs:** [artifacts/h5_hint_grades.json]; §9.8 addendum; Index row 10 gains
the dose-response line; the grade joins the J3/J4 cross-tabulations.

### J2 RESULT, first instrument (2026-07-16) — **branch (c): ceiling-limited, as pre-declared (the 25% branch)**

The blind grader (fresh model instance, shuffled label-free input) returned
**COMPLETE for 125/125 hints** — zero variance; the > 80% ceiling guard fires and
the concentration test is UNINFORMATIVE as registered. Two readings are
indistinguishable in this grade: a true ceiling (the drafter deliberately wrote
full strategies) and grader leniency (no calibration anchors in the rubric).
[runs/h2/grades_raw.json — grader agent a33b46e0d34374b2b.]

### J2 amended instrument (registered 2026-07-16 BEFORE any regrade ran)

A zero-variance grade contains no outcome information (there is nothing to
join), so amending the instrument now cannot be outcome-tuning. Amendment: same
three levels, plus (i) two calibration anchors per level written into the
grader prompt, (ii) the marginal-doubt rule — *when in doubt between two grades,
choose the lower*, (iii) an explicit calibration expectation stated to the
grader ("hints are two-sentence summaries; full mechanical sufficiency should be
uncommon"), (iv) a different fresh grader instance. Same frozen analysis and
ceiling guard. **Amended odds: concentration 30% / no concentration 40% /
ceiling again 30%.**

### J2 amended RESULT (2026-07-16) — **ceiling again (30% branch), and now it is a measured property of the hint set**

The anchored instrument (calibration anchors, marginal-doubt rule, fresh grader)
returned **123 COMPLETE / 2 PARTIAL / 0 NUDGE**, with the grader reporting after
item-by-item stress-testing that the hints "did not genuinely vary — nearly all
specify the named algorithm plus loop structure, state definitions, case splits,
and essential edge handling in full." **Verdict: true ceiling.** The
dose-response question (do nudges suffice?) is **UNMEASURABLE on this hint set**
— the drafter wrote complete strategies essentially everywhere. Three
consequences, recorded:

1. **Scope sharpening for the §9.8 result (Index row 10):** what crossed the
   boundary was **complete-strategy-grade** direction — 13/68 is a statement
   about full approach specifications, and says nothing yet about weaker
   direction. A deliberately richness-varied hint set (COMPLETE / degraded /
   nudge arms) is the future dose-response instrument; **not run this phase**
   (named, not chartered).
2. **The instrument works and is kept:** the anchored rubric discriminates when
   variance exists (it found the two genuinely thinner hints and defended every
   COMPLETE with the stress-test). It is the frozen grader for J3/J4 self-hints,
   where variance is expected.
3. **A real hint defect surfaced, recorded, not edited:** the frozen abc321_c
   hint mechanically includes the zero subset (rank off-by-one hazard); the
   abc334_c hint leaves the pairing-parity DP uninstantiated. The frozen set
   stays frozen; both defects stand on the page.

Grades: [runs/h2/grades_amended.json] → committed as
[artifacts/h5_hint_grades.json] (both instruments + protocol notes).
Prediction accounting: first instrument branch (c) at 25%; amended branch (c) at
30% — the ceiling was the truth both times; the drafter's own registered odds
underweighted it both times.

---

## J3 — the self-hint arm on Qwen (measure the production gap; stop inferring it)

**PRE-REGISTRATION (2026-07-16, frozen before any generation).**

**Question:** Index row 12 ("the model cannot produce hint-grade direction") is
LIVE-BUT-INFERRED, resting on MODELABS (trace *compression*, not approach
generation) and BSF nulls. Measure it directly.

**Channel (frozen):** SELFHINT — Qwen2.5-Coder-1.5B-**Instruct** (matching
MODELABS generator practice) writes its own approach hint from the problem
statement alone (no trace, no artifact, no oracle), T = 0, ≤ 120 tokens, code
fences stripped. Frozen prompt: *"Problem:\n{statement[:2500]}\n\nIn at most two
sentences, state the algorithmic approach a correct solution must take. Describe
the idea only — no code, no variable names."* The base model then generates
conditioned via the **identical** frozen hint-context block; the only variable vs
§9.8's HINT arm is who wrote the hint. Self-hints are persisted verbatim; the
leakage screen is run post-hoc for characterization only (the channel is whatever
the model produces under the frozen prompt).

**Run:** SELFHINT-50 on the same 68-problem medium stratum, frozen config.
Controls: the same-day fresh **B1-50 = 2** (the twice-calibrated floor) and
**HINT-50 = 13** (§9.8), both same config, same session — stated, not rerun.

**Grading (the decisive cross-tabulation, frozen):** every self-hint graded by a
fresh blind instance under the J2 **anchored** instrument, extended with a second
registered dimension — approach judgment: CORRECT / DOUBTFUL / WRONG.
"Production-adequate" := COMPLETE **and** CORRECT. Grading completes before any
join with recovery outcomes.

**Branches (odds):**
- **(a) production failure measured** — SELFHINT ≤ 4 recoveries (p ≥ 0.05 vs B1)
  AND production-adequate share < 30% → Olausson completed at both rungs; the
  cascade is the only deployable shape at this scale — **45%**.
- **(b) use failure reappears** — SELFHINT ≈ floor despite production-adequate
  share ≥ 30% → the Qwen pathology may act on self-generated context; its own
  follow-up — **10%**.
- **(c) self-refinement partially exists** — SELFHINT > B1, McNemar p < 0.05 →
  §9.8's closing and Index row 12 amended; tension with both our nulls and
  PlanSearch-scale intuitions — **20%**.
- **(d) positive-unresolvable** (above floor, p ≥ 0.05) — reported as such —
  **25%**.

**Analysis:** paired exact McNemar vs B1-50 (primary); vs HINT-50 (secondary —
the production gap in recoveries); cross-tab recovery × production-adequacy.
**Artifacts:** h5_selfhint_qwen.json, h5_selfhint_grades.json. **Writeup:** §9.8
extension + Index rows 10/12.

### J3 RESULT (2026-07-16) — **branch (a), the 45% favourite: the production failure is measured, and it is total**

**Recoveries:** SELFHINT-50 = **3** vs B1-50 = 2 (p = 0.5 — on the floor) vs
HINT-50 = 13; the production gap HINT-vs-SELFHINT is 11/1, **p = 0.0032**.
[artifacts/h5_selfhint_qwen.json].

**The cross-tabulation (blind anchored grading + registered correctness
dimension):** informativeness **0 COMPLETE / 37 PARTIAL / 31 NUDGE**; correctness
**14 CORRECT / 29 DOUBTFUL / 25 WRONG**; **production-adequate (COMPLETE ∧
CORRECT) = 0/68 — 0%**, far under the 30% branch line. The same instrument-class
graded the oracle set 123/125 COMPLETE — the discrimination is real (and
retroactively confirms J2's ceiling was the hint set, not grader leniency).
Channel shape, recorded: the instruct model ignores the two-sentence constraint
and emits tutorial preambles that the frozen cap truncates (median 90 words);
what reached the base model never once contained a complete correct strategy,
and was outright wrong 37% of the time. The three recoveries grade
PARTIAL/PARTIAL/NUDGE — floor-consistent, not direction-driven.
[artifacts/h5_selfhint_grades.json].

**Verdict:** at 1.5B on Qwen, the direction decomposition is now closed at both
rungs, both measured: the model **uses** complete-strategy direction (13/68,
§9.8) and **cannot produce** it (0/68 production-adequate; recovery on-floor).
Olausson's localization — feedback production is the bottleneck — confirmed at
1/70th their scale with a direct arm. Index row 12: LIVE-BUT-INFERRED →
**LIVE-MEASURED (one family; J4 adds the second)**. The deployable shape at this
scale is the cascade (a stronger producer feeding a small executor) — exactly
the Self-planning ledger entry's structure, now with both rungs quantified.

---

## J4 — the DeepSeek four-arm stratum contrast (the phase centerpiece)

**PRE-REGISTRATION, step 1 — the screen (2026-07-16, frozen before the run).**

**Why J4 leads the GPU budget:** the Qwen conditioning pathology retroactively
contaminates every conditioning-based null in the record — R3's trace null,
BSF's zero, "the anchor poisons the direction" were all measured on the one
family where conditioning is toxic. "Traces carry no direction for structural
failures" is written as a *content* claim but evidenced only on Qwen.

**Screen (step 1):** DeepSeek-Coder-1.3B-base on the full 78-problem LCB-medium
stdin population (the W2 population), k = 50, T = 0.8, top_p 1.0, seed 17, the
frozen all-cases judge (frac is consumed: artifact selection + richness),
right-sized container. Derive DeepSeek's own pass@50 = 0 stratum; fit the W0c
two-component floor. **The floor's E[fresh B1-50 recoveries] prediction is
committed to this file BEFORE any arm runs — the instrument's third out-of-sample
test.** Screen predictions (odds 60%): pass@8 ∈ [0.02, 0.08], pass@50 ∈
[0.08, 0.18], stratum 60–72/78.

**Power rule (frozen):** compute the W2 exact-McNemar power envelope from the
observed stratum size and floor. If power at r = 0.20 is < 70%, arms do NOT
launch on this stratum alone — an extension (LCB-hard screen or second
temperature pooling) gets its own pre-registration first. No improvisation.

**Hint coverage:** 75/78 medium problems carry frozen audited hints; the three
uncovered (abc343_c, abc327_c, abc339_c — all off-stratum for Qwen) get fresh
hints drafted under the identical protocol + automated screen + blind audit,
frozen in [artifacts/h5_hints_extension.json] before arms run.

### J4 step-1 RESULT (2026-07-17) + the committed floor prediction

Screen: pass@1 0.005 / pass@8 0.022 / **pass@50 0.026** — DeepSeek's medium tail
is nearly flat; **stratum 76/78** (a strict superset of Qwen's 68; zero
near-misses; the two solved problems solved at x = 9 and 12); richness 71/76
with partial credit. **Screen prediction accounting: WRONG overall** (pass@8 in
range at 0.022, but pass@50 0.026 far below [0.08, 0.18] and stratum 76 above
60–72 — the 60% odds were misplaced; DeepSeek trades Qwen's thin medium tail for
none at all). [artifacts/h5_deepseek_medium_screen.json].

**Floor prediction, committed before any arm runs (the instrument's third
out-of-sample test):** two-component fit π₀ = 0.975, **E[fresh B1-50 recoveries
on the 76-problem stratum] = 0.00** (pure-Beta upper bound 0.35). Point
prediction: **B1 recovers 0** (acceptable band 0–1; ≥2 falsifies the fit).
[artifacts/h5_deepseek_floor_fit.json].

**Power (frozen rule):** 0.890 at r = 0.10, 0.994 at r = 0.15, ~1.00 at
r = 0.20 — clears the ≥ 0.70 @ r = 0.20 rule with room; **arms launch on this
stratum alone**; r < 0.08 pre-declared unresolvable.

### J4 step 2 — four-arm pre-registration (2026-07-17, FROZEN before arms)

**Arms (76 problems, DeepSeek-Coder-1.3B-base, frozen config, one generation
batch):** B1-50 / TRACE-50 (artifact = highest-frac candidate from the
DeepSeek-native screen pool, frozen R3 rule; frozen trace-capture) / HINT-50
(the frozen 125 + 3-extension hints — complete-strategy grade per J2) /
SELFHINT-50 (deepseek-coder-1.3b-instruct writes its own, J3 frozen prompt;
graded blind post-run, correctness dimension included). Judge: short-circuit
(recovery is the analysis). Full recovery validation on every recovery.

**Forks (odds):**
- **TRACE > B1 significant** → the trace null was Qwen-scoped; "traces carry no
  direction" retracts to a Qwen fact; the pathology note gains its sharpest line
  — **25%**.
- **TRACE ≈ floor AND HINT fires** → the content localization (§9.8 item 5)
  generalizes across families and hardens enormously — **40%** (my favourite).
- **HINT ≈ floor on DeepSeek** → §9.8's hint result takes a family scope — the
  phase's biggest possible surprise; **pre-committed contingency:** the
  gate-misfire joint then requires a fresh-stratum Qwen replication — **20%**
  (HINT significant 55% / unresolvable 25% / floor 20%).
- **SELFHINT:** floor **70%** / significant 10% / unresolvable 20%;
  production-adequate share < 30%: **85%**.
- Cross-arm: HINT > TRACE significant — **50%**; HINT > SELFHINT significant —
  **55%**.

### J4 arms RESULT (2026-07-17) — **the 40% favourite fork fired: content localization generalizes; the floor hits a third time**

| arm | recoveries /76 | vs B1 (McNemar) |
|---|---|---|
| B1-50 | **1** (floor predicted **0**, band 0–1 — **third consecutive out-of-sample hit**) | — |
| TRACE-50 | 2 | p = 0.50 — **floor** |
| HINT-50 | **9** | 8/0, **p = 0.0039** |
| SELFHINT-50 | 3 | p = 0.31 — floor-consistent |

Cross-arm: HINT > TRACE p = 0.020 (50% odds ✓); HINT > SELFHINT p = 0.055
(the 55%-significant prediction **missed narrowly** — direction consistent,
line not crossed). [artifacts/h5_deepseek_fourarm.json].

**Fork accounting:** fork 2 — TRACE ≈ floor AND HINT fires — was the registered
40% favourite and **fired**. TRACE-significant (25%) and HINT-floor (20%,
with its Qwen-replication contingency) did not. SELFHINT-floor 70% ✓;
production-adequate < 30% at 85% ✓ (measured **1/76 = 1.3%**; 1 COMPLETE / 30
PARTIAL / 45 NUDGE; 34 WRONG — the 1.3B-instruct producer is *worse* than
Qwen's; the three SELFHINT recoveries grade PARTIAL/NUDGE — not
complete-strategy-driven). [artifacts/h5_deepseek_selfhint_grades.json].

**Validation (all passed):** 15/15 recovered rows across all four arms
rerun-stable [artifacts/h5_deepseek_rerun.json]; every HINT recovery ≥ 0.162
normalized-AST from *every* candidate in its 50-failure pool (range
0.162–0.372 — novel structures, not repairs); error-type: timeout-class
enriched again (3/9 = 33% vs 12% base — the HMT pattern, second family).
[artifacts/h5_deepseek_validation_struct.json].

**What J4 settles, cross-family:**
1. **"Traces carry no usable direction for structural failures" is a CONTENT
   fact, not a Qwen fact** — trace arms sit on the floor on both families (Qwen
   1/68, DeepSeek 2/76), including on the family that conditioning helps. The
   retro-contamination worry (the pathology poisoning R3's null) is resolved:
   the trace null survives on the pathology-free family.
2. **The hint result GENERALIZES:** complete-strategy direction crosses the
   competence boundary on both families (Qwen 13/68 r≈0.19; DeepSeek 9/76
   r≈0.12, p = 0.0039).
3. **The production failure GENERALIZES:** self-hint arms on the floor on both
   families with production-adequacy 0/68 and 1/76 — the cascade is the
   deployable shape at 1.3–1.5B regardless of family.
4. **The floor instrument is 3-for-3** across two families and two stratum
   shapes (2.01→2, 2.01→2, 0.00→1-in-band).

---

## PHASE GATE — CLOSED (2026-07-17)

**Gate conditions, audited:** J0 landed, Index seeded and **current** (rows 9,
10, 12, 15 updated with Phase-5 outcomes; instruments and extractions
refreshed) ✓. Production question measured on two families (J3: 0/68; J4: 1/76
production-adequate; self-hint arms on-floor both) ✓. Trace-content claim
carries its cross-family scope line (Index row 9; §9.9) ✓. Hint dose-response
graded (J2: true ceiling, scope note in place) ✓. 7B decision costed and
presented (J5) ✓. **Phase prediction accounting:** J2 ceiling under-priced
twice (25%, 30%); J3 branch (a) favourite ✓ (45%); J4 screen prediction WRONG
(pass@50 and stratum size); J4 fork-2 favourite ✓ (40%); HINT>SELFHINT-significant
missed narrowly (p = 0.055 vs 55% odds); floor prediction ✓ third time.

**The extraction decision now sits with the user, Index in hand:** the mechanism
paper and the pathology note are extraction-ready; the methods record needs only
writing. The one measurement between our floor and the frontier is J5's Q2.

## J5 — the 7B fork: costed and presented (2026-07-16). **NOT RUN — sign-off required.**

**Re-scoped questions (per the J1 ledger amendment):**
1. **Does the Qwen conditioning pathology persist at 7B?** One D2c-style cell
   (44 problems × {E0, E1} × k=8) + one hint-conditioning cell (the 20-problem
   manip set × {E0, HINT} × k=25) on Qwen2.5-Coder-7B. Persists → family
   property (the pathology note strengthens materially); vanishes → small-Qwen
   property (scoped).
2. **Does direction self-production switch on by 7B?** Requires a 7B-derived
   medium stratum (78 × 50 screen, all-cases judge) then SELFHINT-50 + B1-50 on
   that stratum (7B-Instruct writes the hints, J3 protocol) — the first data
   point between our 1.5B floor and PlanSearch's frontier ceiling.

**Feasibility (arithmetic; a ~$0.30 smoke would confirm before commitment):**
Qwen2.5-Coder-7B bf16 ≈ 15.2 GB weights; L4 = 24 GB; at gpu_mem_util 0.90 the KV
budget is ≈ 6 GB. With GQA (4 KV heads × 28 layers × 128 dim, fp16) KV ≈ 57
KB/token → ≈ 105k tokens of KV ≈ ~12 concurrent 8k-context sequences — **fits on
L4** with reduced batching (expect 3–5× slower generation than the 1.5B cells).
L40S (48 GB) doubles throughput headroom at ~2× the rate.

**Cost estimate:**
| item | est. |
|---|---|
| 7B + 7B-Instruct download to volume | ~30 GB, one-off, ≈ $0 compute |
| Q1 pathology cells (gen ~1.7k seqs + judging) | **$3–5** |
| Q2 screen (3.9k gens + all-cases judge) | **$6–10** |
| Q2 arms (2 × 50 × stratum ≈ 40–55 + selfhint gen) | **$5–9** |
| **Total** | **≈ $15–25 on L4** (Q1 alone: $3–5) |

**Recommendation, for the decision:** Q1 (pathology persistence) is the cheap,
high-leverage half — it directly upgrades the Qwen-pathology extraction and
stands alone. Q2 is the forward-looking half and roughly 4× Q1's cost. They can
be authorized independently. Awaiting sign-off; nothing runs under this charter.

**SIGN-OFF (2026-07-17): the user authorized BOTH questions** ("run both j5 to
question 7b evidence"). Budget envelope as costed (~$15–25).

### J5 run pre-registration (2026-07-17, frozen before any 7B generation)

**Models:** Qwen/Qwen2.5-Coder-7B (base; all conditioning cells and arms) and
Qwen/Qwen2.5-Coder-7B-Instruct (self-hint producer only). Per-family smoke gate
first (8 × 8 on the frozen scaffold, wf ≥ 0.85 / dg ≤ 0.10) — doubles as the KV
feasibility check.

**Q1a — D2c-style cell:** the frozen 44 artifacts × {E0, E1-D2C} × k = 8,
all-cases judge. **Decision rule, sharpened for a stronger model (frozen):** the
pathology signature is **below-both-nulls** — conditioned mean frac < copy-null
(0.494) AND < 7B's own E0 i.i.d. null, paired one-sided MC Wilcoxon p < 0.05
against each. A conditioned value *between* artifact and own-iid is the **blend**
(what the other families do — with a strong model, imitation alone predicts
being pulled *down* toward a 0.49 artifact, so "conditioned < iid" alone is NOT
the pathology; below-both is). **Odds: pathology persists (below-both) 35% /
blend (between; pathology vanishes into imitation) 45% / conditioned ≥ iid
(conditioning neutral-or-helps) 20%.**

**Q1b — language-channel cell:** the frozen 20-problem manip set × {E0, HINT} ×
k = 25, frozen hints, per-sample mean pass. **Odds: harm vanishes (mean Δ >
−0.02) 60% / harm persists (Δ < −0.05) 25% / middle 15%.** (Saturation caveat
pre-declared: if E0 mean pass > 0.9 the cell is compressed and reported as
such.)

**Q2 — the switch-on measurement:**
1. 7B medium screen (78 × 50, frozen config, all-cases judge). Prediction:
   stratum ∈ [35, 55] of 78, odds 55%.
2. Floor fit (W0c model); **E[fresh B1-50 recoveries] committed here before
   arms — the instrument's fourth out-of-sample test.** Power rule: arms launch
   only if power ≥ 0.70 at r = 0.20 on the observed stratum; else extension by
   further pre-registration.
3. Arms: **B1-50 / SELFHINT-50** on the 7B stratum (7B-Instruct writes its own
   hints, J3 frozen prompt; persisted; blind-graded with the anchored
   instrument + correctness dimension before any join).
4. **Branches (odds):** **(a) floor + production-inadequate hints** (< 30%
   adequate) → switch-on lies above 7B; the cascade remains the only deployable
   shape through 7B — **40%**. **(b) floor despite adequate hints (≥ 30%)** →
   a use-failure at 7B on its own stratum — **10%**. **(c) SELFHINT > B1
   significant** (McNemar p < 0.05) → **self-refinement switches on at-or-below
   7B** — the forward-looking headline; Index row 12 rescoped — **25%**.
   **(d) positive-unresolvable** — **25%**. Production-adequate share ≥ 30%:
   **45%**.

**Not run (out of authorization):** an oracle-HINT arm on the 7B stratum (would
measure 7B's direction-use ceiling; noted as the natural companion if ever
wanted).

**Ops:** detach + volume-first persistence + short-circuit judging except where
frac is the analysis (Q1a, Q2 screen); ~3–5× slower generation expected at 7B.

*(J5 RESULTS land below.)*
