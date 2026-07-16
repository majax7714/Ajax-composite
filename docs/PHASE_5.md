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

*(J3 RESULT lands below.)*

---

*(J4–J5 pre-registrations and results append below as they land.)*
