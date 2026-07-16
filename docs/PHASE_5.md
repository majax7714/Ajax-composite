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

*(J2 RESULT lands below.)*

---

*(J3–J5 pre-registrations and results append below as they land.)*
