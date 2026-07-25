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
