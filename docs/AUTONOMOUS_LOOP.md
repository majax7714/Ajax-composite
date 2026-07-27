# The autonomous phase loop — operating spec

*Frozen 2026-07-24, before its first iteration. Author sign-off recorded below.
This document is pre-registered the same way a run is: the process is committed
in writing before it executes, so drift in **how** the record is produced is
visible against a frozen statement, exactly as drift in what it claims is.*

## 0. Why this document exists

Phases 0–9 were driven turn-by-turn with the author in the loop for every
decision and every dollar. From Phase 10 the loop runs unattended between
author check-ins (hours, not minutes). The methodology (§10 of the journal) is
unchanged and non-negotiable; what changes is only who advances the cursor.

The failure mode this creates is named up front, per §10's practice of naming
the drift risk of any reframe: **an unattended agent is both the experimenter
and the author of the verdict.** Nothing in this document eliminates that. What
it does is make the ordering auditable — rules committed to git before the data
exists — so the conflict is constrained by public timestamps rather than by
good intentions.

## 1. The loop

Each iteration is one phase.

1. **State read** — journal §0 index, §0.4 open successors, the previous phase
   gate, `git status` clean.
2. **Question selection** — from §0.4, or forced by the previous phase's open
   confound. The charter states the question *and why it is next*.
3. **P0 free amendments** — corrections that need no GPU. Landed and committed
   first (the pattern established in Phases 7–9).
4. **Pre-registration** — predictions, explicit **odds**, decision rules, branch
   interpretations, n and power, kill criteria, cost estimate. Frozen.
   **Committed before any spend.** The phase doc records the pre-registration
   commit hash; each artifact records the hash it ran under. Ordering is
   therefore verifiable from `git log` by a third party.
5. **Smoke** — cheapest possible cell first: template/prompt format, context
   length, judge semantics, one family. (Phase 8's phi failure was a 2048-ctx
   config mismatch caught exactly here.)
6. **Launch** — `modal run --detach`, `PYTHONUNBUFFERED=1`, volume-first
   checkpointing, plain background execution (never `nohup … &`).
7. **Retrieve** — pull artifacts from the volume; **commit raw JSON before
   analysis**, so the data commit precedes the verdict commit.
8. **Analyse** — strictly under the frozen rules. Mandatory checks: achieved
   vs target Δ_art (the Phase-8 measured-relation rule), rerun stability,
   distinct-seed on any arm described as a fresh draw.
9. **Write up** — phase doc RESULT; journal §9.x addendum; §0 index rows; §0.3
   evidence rows; abstract banner if a claim's status moves; §8 ledger entry if
   an operational failure occurred.
10. **Gate** — close with prediction accounting (which branch fired, at what
    odds), measured cost, and what is now open.
11. **Commit** — the author pushes. Return to 1.

## 2. Standing rules the loop is bound by

Inherited from §10 and the operational ledger (§8); restated here because an
unattended loop cannot rely on being reminded.

- No tuning past a failed gate. A fired kill criterion is final.
- Never edit a frozen spec. Append, never revise; retracted text keeps its
  place under a dated banner.
- Match on the **measured** relation, not the mined proxy.
- Judge grade matched to the analysis — short-circuit for any-pass contrasts,
  all-cases only for per-test enrichment.
- Right-sized containers; per-case timeouts 3–4 s for 1.5B-class checks.
- An invalid run is recorded **as invalid** and then re-run — never silently
  redone (the Phase-9 run-1 precedent).
- Exploratory diagnostics stay separated from confirmatory gates and may never
  reopen a verdict.
- Commits carry no AI co-authorship trailer.

## 3. Halt-and-report conditions

The loop stops and waits for the author when:

1. **A result directly refutes a LIVE claim 1:1.** Freeze, write it up, stop.
2. Cumulative spend under this loop reaches **$90** (report) or **$110**
   (hard stop).
3. Modal authentication fails or a token expires.
4. Two consecutive invalid runs on the same cell — that indicates the loop's
   understanding is wrong, not the data.
5. Anything that would require *revising* rather than appending.
6. A new toolchain, new dependency, or a model download beyond ~15 GB.

**Everything short of a 1:1 refutation is inspected, not halted.** Evidence that
merely pressures a live claim is promoted from caveat to named hypothesis and a
discriminating cell is designed — the Phase 8 → 9 move, which is the loop's most
valuable behaviour and must not be suppressed by caution.

## 4. Budget

Author-set envelope: **$90 report / $110 hard stop**, cumulative from
2026-07-24, against a $200/month workspace cap. Month-to-date workspace spend is
checked with `modal billing report` **before each phase launch**, and a phase is
not launched if its estimate would bring the month within $30 of the workspace
cap — a mid-battery cap failure would corrupt a phase, which costs more than it
saves.

## 5. What the author reads

The record itself: phase charters and the journal, as before. Commit messages
carry the headline verdict. No separate reporting channel.

---

**Sign-off (2026-07-24).** Loop, rules, halt conditions, and the $90/$110
envelope approved by the author; first iteration is Phase 10. Commit authority
granted, push authority retained by the author.

---

## Amendment 1 (2026-07-25) — **decision authority: take the recommendation and document**

*Author instruction, verbatim: "when presented with a decision again go for the
recommended approach and document."*

**What changes.** Where the loop previously stopped to present options and wait, it
now **takes its own recommended option and proceeds**, recording in the phase document
(a) the options that were live, (b) which was taken, (c) why it was recommended, and
(d) what would have been done otherwise. The decision is a *documented* step, not a
silent one — a reader must be able to see the fork and disagree with it after the fact.

**What does NOT change — the halt list in §3 stands unaltered.** This amendment covers
*choices between approaches*; it does not dissolve the conditions under which the loop
stops regardless of having a recommendation. Specifically still halting:

1. a result that **directly refutes a LIVE claim 1:1** (the author's separate and
   explicit carve-out, 2026-07-24);
2. cumulative spend at **$90** (report) / **$110** (hard stop);
3. auth failure; two consecutive invalid runs on one cell; anything requiring
   *revision* rather than appending; new toolchain or a >15 GB download.

The distinction is between *"which of these should we do?"* — now the loop's call — and
*"the record's public claims may be wrong"* or *"this spends real money past the
envelope"* — still the author's.

**Failure mode this creates, named so it can be caught.** Self-recommendation plus
self-execution removes the one external check that was catching over-reach at the fork.
The counter-pressure is that recommendations must be written *before* the outcome is
known and left standing: a documented fork whose stated rationale is later falsified
stays on the page next to what happened, exactly as a pre-registered prediction does.
Phase 10's own record is the calibration data — on its first day the loop's 70% and 65%
favourites both missed and a 5%-priced branch fired, which is the reason this amendment
carries a visible accounting requirement rather than a promise of good judgement.

## Amendment 2 (2026-07-25) — **cost figures are read, and their provenance is labelled**

Following §8 ledger entry 7 (the inferred-$31 correction), and its immediate
recurrence: Phase 10 R3 was estimated at **$2–5** and cost **≈$0.27** — the loop
reproduced, in its own first pre-registration, the ~5–10× over-estimation it had just
corrected in the record. Practice, now binding on the loop:

- Every cost stated in the record is **read from `modal billing report`** with its query
  date, or explicitly labelled **estimate** / **aggregate delta** / **inferred**.
- Modal's per-app daily lines lag by more than a day. A run's cost may only be
  available as a **month-to-date aggregate delta** at write-up time; that is a legitimate
  figure and is labelled as such, never silently promoted to a line item.
- **Forward cost estimates are recorded and then reconciled against the bill at phase
  close**, so the estimator's bias is measured rather than assumed. The record's
  estimates have run high every time they have been checked.

## Amendment 3 (2026-07-25) — **envelope raised to $100 report / $120 hard stop, on the month-to-date figure**

*Author instruction, verbatim: "were at 82.82 current spend, you can push to 100/120
since ive checked in."*

**Which number this governs, stated because the two differ by ~17×.** At the time of the
instruction, **loop** spend since 2026-07-24 was **$4.76** (the figure §4's $90/$110
governed) while **month-to-date workspace** spend was **$82.82** (the figure the $200 cap
governs). The author quoted the month-to-date figure, so the new thresholds are applied to
**month-to-date workspace spend**: **$100 report / $120 hard stop**.

**Why this reading and not the other.** Applied to the *loop* envelope, $120 would put
month-to-date at ≈$198 against a $200 cap — through §4's standing guard that a phase is
not launched if its estimate would bring the month within $30 of the cap. Applied to
month-to-date, $120 leaves the guard intact ($120 + $30 < $200). The conservative reading
is also the one consistent with the frozen spec, and it costs nothing operationally: it
leaves ≈$17 before report and ≈$37 before hard stop, which is 8+ phases at the measured
burn rate (Phases 12–16: $0.02–$2.15 each).

**Unchanged:** §4's within-$30-of-cap launch guard; §3's halt list, including the 1:1
refutation rule. If the author intended the loop envelope rather than the month-to-date
figure, that is a one-line re-amendment — it would not change behaviour for many phases.

## Amendment 4 (2026-07-25) — **the README is a maintained surface, updated every pass**

*Author instruction, verbatim: "add to the loop to update readme going forward with every
pass."* Context given in the same message: the author reads results **on mobile, after
pushing**. That is the operative fact — the README is the repository's landing page and the
first thing a phone renders, so it is the one document whose staleness is *invisible from
inside the loop* and *maximally visible from outside it*.

**What changes — §1 step 9 gains a fourth surface.** Step 9 (*Write up*) currently names
the phase doc, the journal (§9.x / §0 / §0.3 / abstract / §8), and nothing else. It now
reads: phase doc RESULT; journal addenda and index rows; **`README.md`**; gate. Concretely,
at every phase close the README must carry:

- a **row in the "Map of the composite" table** for the phase that just closed, in the same
  one-sentence-verdict register as the existing rows;
- a **current-status line** naming the phase number, its verdict, and what is now open, so a
  reader who never opens `docs/` still knows where the record stands;
- the **arc paragraph** brought current *if and only if* a claim's status moved. Phases that
  close INCONCLUSIVE or as instrument misses get a table row, not an arc rewrite — the arc is
  the record's thesis line, not its changelog.

**What does NOT change.** The README is a *pointer*, never a source. No number appears there
that is not already in the journal with its artifact, and the README is never the place a
result is first written down — that ordering (data commit → verdict commit → summary) is what
§1 steps 7–9 exist to enforce. Append-only does **not** apply to the README: it is explicitly
a rendered view of current state, and it may be rewritten freely, because git history holds
its prior versions and the journal holds the append-only record. That distinction is stated
here so a later reader does not mistake a rewritten README line for a silent revision.

**Failure mode this creates, named so it can be caught.** A summary surface maintained by the
same agent that produces the results is where over-claiming is cheapest — the README has no
odds, no CIs, no scope column, and no gate. The counter-pressure is the sourcing rule above:
every README sentence must be checkable against a journal row, and the table's existing rows
already model the tone (they name what was *retracted* as prominently as what was found).

**Backfill (2026-07-25).** The README's map table stopped at Phase 9 and its arc paragraph
ended at Phase 9's diet-vs-provenance result — eight phases stale at the moment this
amendment was written, which is itself the evidence that the surface needed a rule. Phases
10–17 were backfilled in the same commit as this amendment, before Phase 18's spend.

### Amendment 4a (2026-07-25, same day) — **it was never only the README**

Written after the backfill above, because fixing the README exposed that the diagnosis was
too narrow. The journal has **two more summary surfaces with the identical failure**, both
found stale during Phase 18's state read:

- the **living-record line** at the top of `WRITEUP-rgr.md` — the line the README explicitly
  directs readers to for current status — last updated **2026-07-18, at Phase 9**;
- the **abstract's banner chain** — which §1 step 9 already required ("abstract banner if a
  claim's status moves") — last extended at **Phase 10 R4**, with Phases 11–17 missing,
  including four movements that *did* change claim status: the scale question being answered
  (P11), attention magnitude excluded (P12), concentration retired (P15), and
  framing-invariance established (P17).

**The pattern, stated because it is the useful part.** These surfaces drift for a structural
reason, not a lazy one: **a phase's own documents are where its work naturally lands**, and
every summary surface is by definition somebody else's document. The detailed record —
phase charters, §0.3 rows, §0.4 successors — stayed current throughout, because each phase
had a reason to touch them. Nothing gave any phase a reason to touch the abstract, so seven
in a row did not. **Compliance with step 9 was not partial; it was invisible.**

**What changes.** Step 9's write-up set is now enumerated explicitly, and a phase does not
close until each is either updated or *recorded as deliberately unchanged*:

1. the phase doc RESULT; 2. the §9.x addendum; 3. §0 index rows; 4. §0.3 evidence rows;
5. **§0.4 open successors**; 6. **the living-record line**; 7. **the abstract banner chain**
(when a claim's status moved); 8. **`README.md`** (Amendment 4); 9. §8 ledger entry (when an
operational failure occurred).

"Recorded as deliberately unchanged" is a real option and the common one — most phases move
no claim status and owe the abstract nothing. The requirement is that the *decision* is
visible, not that every surface is edited. A gate that is silent when skipped is how seven
phases skipped it.

**Related defect found in the same pass, and why it belongs here.** §0.3 rows 8 and 11 had
**contradicted each other about the 7B sink since Phase 10** — row 8 carrying the retraction,
row 11 still asserting the retracted claim in its evidence, scope, *and* caveat cells. The
claims-to-evidence layer exists precisely so that an extraction is *selecting rows rather
than re-deriving support*; two rows disagreeing about one fact defeats its entire purpose,
and it survived eight phases because no phase's own work required reading row 11. Same
structural cause as the stale surfaces, so it is recorded against the same amendment rather
than as an isolated slip.

## Amendment 5 (2026-07-26) — **literature is checked at the charter and at the finding, not only at the ledger**

*Author instruction, verbatim: "if you can use web to search for relational literature upon
findings. could save a phase run always worth the check."*

**What this replaces.** The standing practice was narrower than the author intended: web
verification was performed **before writing a §11 reconciliation-ledger entry**, i.e. only
once the loop had already decided some outside work was relevant. That ordering means the
literature can only ever *confirm or correct* a connection the loop already made. It can
never *supply* one, and it can never prevent a run.

**The failure that forced this.** Phases 6–19 attributed the D2c SINK to a
Coder-continued-pretraining diet. The competing general explanation — *intrinsic
self-correction degrades, worst in small models* (Huang et al., arXiv 2310.01798, ICLR 2024)
— is prior, well-known, and directly applicable, since §9.3 had already concluded this
record's ~2-bit feedback supplies no direction. **It was never on the page.** The
reconciliation ledger held three entries at the time and none of them was the one that
competed with the central claim. Phase 20 refuted the family leg empirically at a cost of
roughly a dozen phases of attribution built on an unposed null. A ten-minute search at
Phase 6 would have made the general effect the hypothesis to beat.

**What changes — two new checkpoints in §1.**

- **Step 2a (question selection, BEFORE any spend).** Before a charter is frozen, search for
  (i) whether the question is already answered, (ii) whether a **general-effect null** exists
  that the proposed finding would be an instance of, and (iii) whether the design has a known
  failure mode. Record the search in the charter — **including when it returns nothing
  useful**, which is itself information and is the common case. A charter may not claim a
  model-, family-, or scale-specific cause without naming the general null it intends to beat.
- **Step 9a (on a finding).** When a phase produces a result, search for related work before
  the verdict is written, and record what squares and what does not. A finding that turns out
  to be a known effect is not thereby worthless — but it must be *labelled* as a replication
  with a scope extension, not presented as a discovery.

**Both checkpoints are cheap and neither is a gate.** Nothing halts because a search returns
results; the obligation is to *record* them. The failure mode being prevented is silence, not
disagreement.

**Failure mode this creates, named so it can be caught.** Search results are summaries and
can be wrong, stale, or mismatched to our setting; treating them as authority would be its
own drift. So: a literature claim only becomes load-bearing after the **source itself** has
been checked, not a search snippet — the practice already in force for §11 entries, now
extended to these checkpoints. Where only snippet-level evidence exists, it is labelled as
such. (Recorded honestly: the Huang et al. entry was grounded by fetching the paper's own
abstract page and a second failed fetch is on the record — the Self-Refine abstract does
**not** contain the small-model limitation the search summary implied, so that half of the
claim rests on secondary summaries and is marked accordingly.)

---

### Amendment 6 (2026-07-26) — the budget ceiling, corrected by the author

**Author instruction, verbatim in substance:** the $100 report / $120 hard stop were *"a
sanity check for you"*, not a real constraint; *"the only actual hard stop is the $200 for
the Modal account,"* with authority to raise the working ceiling to **$110–130**.

**What changes.**

- **Working report threshold: $130.** At or above it, report to the author before further
  paid spend.
- **Hard stop: $200** — the Modal account limit. This one is external and real; it is not
  raiseable by the loop under any circumstance, including a phase mid-flight.
- **§4's within-$30-of-cap guard now measures against $200**, not $120.
- Amendment 2's cost method is **unchanged and reaffirmed**: cost is the **MTD aggregate
  delta**, which needs one month-to-date figure. See §8 entry 14 — the loop declared a cost
  unmeasurable on the same day this amendment was written, while that method sat in this
  document unconsulted.

**What does not change, and why it is worth saying.** A raised ceiling is not a licence to
spend more per phase. Every phase still pre-registers a cost estimate and reconciles the
measured figure against it, and an overrun is still a recorded miss — Phase 21 posted the
first one in eleven phases ($2.87 against $1.60–2.80) *in the same close that raised this
ceiling*. The estimate discipline is what makes the ceiling almost never bind; loosening the
ceiling while loosening the estimates would remove the only mechanism that has kept twelve
phases inside roughly $12 total.

**Standing carve-out retained (Amendment 1 / the flag-over-literal rule).** Real money still
gets author sign-off when a phase's estimate exceeds **$10**, regardless of headroom.
