# The RGR Journal — an experimental record of refinement, anchoring, and where direction comes from

*(Retitled 2026-07-16, Phase 5 J0. Original title, kept for the record:
"Register-Gated Refinement, and When Cross-Step Conditioning Pays — a full
experimental record.")*

**This document is an experimental journal, and the journal is the primary
artifact.** It is not scaffolding for a claim: the original claim (the register)
nulled; both audited successor claims (H1, F2) fell; the central mechanism claim
reversed under its own missing arm — and at every step the retraction was more
informative than the claim it replaced. What the project produces is the
composite recorded here: a working method (§10) applied repeatedly, generating
pre-registered questions, scoped verdicts, calibrated instruments, and meaning
extracted from failures — in chronological truth, appended and never revised.
Papers, if written, are *extractions from journal state* (§0.2), re-derived from
the record — not the thing the record exists to serve.

*The arc so far, one breath: an execution-grounded verifier seemed to carry load
(it didn't — quantization artifact); a learned cross-step register carried none;
the null, fully localized, reframed the question to "where can refinement pay at
all"; the search for that answer produced the anchoring/escape law, an
elimination argument, a false-zero floor that predicts to the decimal, a
cross-family audit that retracted our platform negatives as one family's
pathology — and finally an existence proof that approach-level direction crosses
the competence boundary, moving the open question to where direction comes from.*

*Living record — last updated 2026-07-18 (**PHASE 6 CLOSED — where the pathology
comes from + extraction-readiness, [PHASE_6.md]**: the small-Qwen conditioning
pathology's origin is **measured** — a **Coder-continued-pretraining-diet ×
competence-window** effect (general-1.5B, same arch/tie/scale, is clean; the code
sink is 1.5B–3B, absent at the 0.5B floor and 7B; the language harm is 1.5B-only
→ **MIXED** across channels), so it is neither architecture/tie (H-tie demoted at
P0 by StarCoder2, tied-yet-friendly) nor base recipe. The flagship
HINT-13-vs-floor number now stands on a **distinct-seed measured control** (P2:
fresh B1 = 2, floor instrument 5-for-6; §8 caveat computed → measured; §10
distinct-seed protocol codified), and every LIVE/SCOPED claim carries a
claims-to-evidence row (§0.3). En route, a Kaggle re-baseline was retired at its
smoke — free T4s can't run bf16 — a recorded dead-end. §9.9 P1 addendum, §9.5.
Previously **J5 CLOSED — the 7B fork,
[PHASE_5.md] J5**: Q1 — **the conditioning pathology is a small-Qwen (1.5B)
property**: at 7B the code channel *blends* (0.609 between the nulls) and the
language harm vanishes (Δ −0.018, ns); both frozen favourites hit. Q2 —
**self-production does not switch on by 7B**: branch (a) at 40% (the
favourite); the self-hint arm is floor-equivalent and only **5/101 (5%)** of
7B self-hints are production-adequate (vs 0/68 at 1.5B, 1/76 DeepSeek); the
cascade remains the only deployable shape through 7B. En route the record
gained structure: the 7B medium stratum is a **live tail, not a false-zero
floor** (π₀ = 0; the medium power gate fired; the pre-registered hard
extension restored the substrate, π₀ = 0.76, pooled gate passed 0.816); the
floor instrument went **4-for-5**, and its one falsification exposed a
measured harness confound — same-seed vLLM regeneration makes "fresh" B1 arms
≈ 50% screen-identical (§8 caveat; it also dissolves the apparent SELFHINT
trend) — §9.9 J5 addendum, §9.5. Earlier same day: **Phase 5 complete — the
journal turn + where direction comes from, [PHASE_5.md]**: the record reframed
as the primary artifact (§0 Claims & Scope Index); the production question
answered on two families — 1.3–1.5B models execute complete-strategy direction
they cannot manufacture (§9.9); the trace null shown to be a content fact
cross-family; the false-zero floor 3-for-3; the 7B fork costed and sign-off
gated. Previously
2026-07-16: **Phase 4 complete — claim hardening, [PHASE_4.md]**: the cross-family battery retracted F1 and the SINK as
Qwen2.5-Coder-scoped — the SINK *inverts* off-Qwen — while the feasible region and
the anchoring law generalize (and the law survives structural-AST recomputation);
the completed decomposition **reversed the use-capacity claim**: oracle-grade
approach hints recover 13/68 on the pass@50 = 0 stratum vs the calibrated floor of
2, p = 4.9 × 10⁻⁴ — §9.8, §7.3 banner, abstract scope banner. Earlier same day:
Phase 3b W0–W4 complete: elimination argument hardened, **R3 NULL at declared
power** [now read as a trace-channel null — §9.8], D2c SINK, BEST+ABSTRACT zero —
§9.7, [PHASE_3B.md]; Phase-3R audits resolved 2026-07-15: H1 killed-as-artifact, F2
retracted-as-structural, E5/E1 closed clean). All numbers trace to committed artifacts and
run records; sources cited inline as `[file]`. This is the canonical document for the
whole project. **New conversation: read §10 (working method — the document's thesis,
now directly after the abstract), then §0 (Claims & Scope Index — what the project
currently believes), then §9.5 (live status).** §§1–5 are the register experiment
(Phases 0–2 + diagnostic teardown, complete and frozen); §6 is the stack rebuild
(Phase M); §7 is Phase 3 (reframe + benchmark screen; F1/F2 both since retracted —
banners in place); §8 is reproducibility + the operational ledger; §9 is the
mechanism arc (Phase 3R audits → D-measure → the escape-distance law → the
elimination argument → Phase 3b's trace null → Phase 4's reversal, §9.8); §11 is
references + the reconciliation ledger. Historical section numbering is preserved
(reading order 10 → 0 → 1 is by design, J0); every retracted claim keeps its
original text under a dated banner.*

---

## Abstract

*(Framing, 2026-07-16 J0: what follows is a **composite** — a sequence of
pre-registered questions, verdicts, retractions, and instruments, kept in
chronological truth. The abstract accretes dated paragraphs as phases close;
banners carry corrections backward. For the current belief state in one table,
see §0.)*

> **Scope correction (2026-07-16, Phase 4 H0c — [PHASE_4.md]).** Every finding in
> this record was measured on **one model family** (Qwen2.5-Coder, 0.5–1.5B, base +
> instruct); scale and family are confounded in every "at this scale" sentence.
> After the Spurious-Rewards precedent (§11 ledger — an entire sub-literature's
> conclusions turned out to be one family's pretraining priors), family transfer is
> treated as a **mandatory audit, not a limitation paragraph**: claim-bearing "at
> this scale" phrases now read "on Qwen2.5-Coder at this scale" throughout (abstract,
> §5, §7, §9), and the H1 cross-family battery (DeepSeek-Coder-1.3B, StarCoder2-3B)
> either widens each scope back with a measurement or narrows it permanently. Two
> companion corrections land with this: **D2c's SINK** is repositioned as a
> quantified replication-plus-extension of the Codex buggy-prompt imitation
> phenomenon (§11 ledger), currently ambiguous between a capacity limit and faithful
> distribution-matching — H3 (§9.7 addendum) pre-registers the cross-scale fork that
> discriminates; and the **elimination argument** (§9.3.1) is scoped to *in-context
> conditioning channels* — weight-space (test-time training) and search-space
> (feedback-guided search, multi-model sampling) channels were never in its
> enumeration.
>
> **H1 verdicts (2026-07-16, same day — the battery ran; [PHASE_4.md] H1 RESULT).**
> The audit **fired**. Per-finding scope lines, now measured: **F1 (BCB shallow
> tail): QWEN-SCOPED, retracted** — DeepSeek-Coder-1.3B shows headroom +0.177 at
> in-band coverage (the pre-committed retraction condition verbatim; it would have
> *passed* the Phase-3a gate), StarCoder2-3B +0.252; the ~0.10 cap reproduces on
> neither family (§7.3). **Feasible region: GENERALIZES** — both families exceed
> Qwen's LCB-easy headroom (+0.236/+0.232 vs +0.197; §9.2). **SINK: QWEN-SCOPED
> and INVERTED** — the same artifacts *lift* both families above their own i.i.d.
> (+0.107 significant / +0.046 n.s.); what generalizes is the *blend toward the
> artifact*; Qwen's below-both-nulls sink is a family-specific degradation that
> distribution-matching does not explain (§9.7). **The anchoring law's form:
> GENERALIZES** — conditioning pulls generations deep into the artifact's
> neighborhood on all three families. One line: the negative *platform* claims
> were a portrait of Qwen2.5-Coder; the *mechanism* is family-general.
> *(2026-07-17, J5 Q1: the sink is also scale-bounded within the family — at
> Qwen-7B it vanishes into the family-general blend, and the language-channel
> harm vanishes with it; §9.9 J5 addendum, Index rows 8/11.)*

We test one claim in isolation: that an explicit internal state vector — a
*register* — updated across refinement steps and gating generation improves
correctness beyond what verification-plus-iteration already provides. We
built the minimal falsifiable version: a frozen 1.5B code generator, an
execution-trained verifier, and a 2.4M-parameter register stack (soft-prompt
injector, problem-conditioned initializer, GRU update) that is *the only
channel carrying information between refinement steps*. The design makes the
central ablation exact: freezing the register collapses the loop, by
construction, into verifier-reranked best-of-n — so the ablation and the
baseline are the same object.

Two pre-registered results. **H1 (positive):** a verifier fine-tuned on
sandboxed execution labels beats the generator's own token likelihood as a
confidence signal on held-out problems — AUROC 0.795 vs 0.696
(Δ = +0.099, 95% CI [+0.044, +0.153]) — and lifts best-of-8 selection from
0.628 to 0.671 pass@1. **H2 (negative, the novel claim):** register-gated
refinement ties the frozen-register baseline *exactly* at matched compute —
pass@1 0.6829 vs 0.6829 (Δ = 0.000, CI [−0.049, +0.055]). Diagnostics close
the mundane escapes: register dynamics were healthy, the verifier was not
stale, and imitation training verifiably steered teacher-forced likelihood
(−10.7% validation loss) — the steering simply did not survive sampling.
Under the pre-committed kill criterion, the register claim is dead at this
scale and training regime. We report the negative with its full causal
localization (§5.3): a **two-component** failure — the static injection is a
transfer failure, the update dynamics a mechanism failure from input starvation.

**Beyond the register (§§6–7).** Eleven diagnostics turn the bare null into a
positive question: cross-step conditioning can only pay where the task has
*reachable-but-improbable* headroom, and it must condition on an **abstraction** of
the error, not the failed candidate (conditioning on the candidate anchors the model
to its own mistake — measured, DIAG-8/10). Pursuing that question required a stack
rebuild — **Phase M** ports the generator from HF/4-bit to vLLM/bf16 for a **100×
throughput** gain (validated register path, re-based baselines, and two carry-forward
findings: the verifier must be retrained on the new candidate distribution, and
bit-for-bit reproducibility gives way to a statistical standard) — and a
pre-registered **Phase 3** benchmark screen. Phase 3's first hard result is a
documented negative that generalizes. Across **two benchmark families** (BigCodeBench,
LiveCodeBench), two execution paradigms (unit test, stdin/stdout), three difficulty
tiers, and two model scales, **no configuration offers the reachable tail refinement
needs — pass@50 − pass@8 is capped at ~0.09–0.12, never the required ≥0.15** (Finding
F2). The gate returns a **negative**, and it is structural: a Qwen2.5-Coder model at this
scale solves a problem within a few samples or not at all (a peaked, not heavy-tailed,
per-problem solution distribution), so pass@k saturates and sample-based refinement
has almost no runway — the same "solve-within-8-or-not" shape that sank HumanEval,
now shown to be a property of the whole task family, not an unlucky choice. **That
negative — a precise statement of where iterative refinement can and cannot live — is
the substantive Phase-3 result**, and it redirects the next experiment toward
feedback-driven recovery (does an error abstraction let the model reach solutions it
could not i.i.d.-sample?) rather than a search for a heavy-tailed code benchmark that
may not exist. A methodological result falls out too: subset screening on the *first
n* problems was ~2× optimistic vs random — caught by the confirmation step before any
training was built on it.

**Phase 3R (§9, in progress).** Before H1 and F2 are called final, both are audited
against the Phase-0 choices they inherit. **R1** asks whether H1 is a *quantization
artifact*: on bf16 the stack-invariant Selection-Efficiency metric shows likelihood
alone (SE 0.305) nearly reproduces the 4-bit verifier benefit (SE 0.315) — the decider
is a bf16 verifier retrain (interrupted by a 2026-07-14 power outage before its verdict
computed — rerun pending; see §9.5). **R2** asks whether F2's shallow tail is
*decoding-induced* (top-p 0.95 + T 0.8 + Instruct all suppress the improbable tail);
it re-screens with a base completion model, top-p 1.0, and a temperature sweep — base
path validated, base T=0.8/1.0/1.2 screened, instruct arm partial (same outage). Spun
off from the DIAG-8 anchoring finding, **D-measure**
converts "conditioning on a failure is harmful" into a law: repair is governed by
**escape distance** (how far a generation diverges from the failed artifact), the
benefit is a **coverage/diversity** effect not a per-sample-quality one (D2b), the
attractor is **content-blind** and **provenance-independent** — distinct from Tsui's
self-anchoring blind spot (D2a) — and the reconciliation with the self-refinement
literature is that **escape requires direction, and direction requires rich feedback**.
That last statement is the hypothesis R3 (conditional reachability) now tests directly.
The law's sharpest consequence (§9.3.1) is an **elimination argument**: undirected
failure-conditioning asymptotes toward i.i.d. sampling (full escape = the artifact
discarded = resampling), so it is *strictly dominated by resampling at matched compute*;
the only mechanism that can beat i.i.d. is **directed** escape, which makes R3 the sole
surviving refinement hypothesis rather than one option among several. This converges,
from a mechanism, on the compute-matched conclusion of Olausson et al. (2024). One
confound of our own (E5's subset overlap; §9.3.1) is flagged for a free matched-control
recompute before the content-blindness/neutral-attractor claim is called final.
**Resolved 2026-07-15:** the R2 grid completed and the gate **fired on its retraction
branch — F2 is retracted-as-structural**: with the tail un-suppressed, LiveCodeBench-easy
has a feasible *region* (the whole base arm plus instruct T=1.2; headroom up to +0.25
at in-band coverage) while BigCodeBench stays infeasible at every cell — the shallow
tail was a property of benchmark-family × decoding, not of code on Qwen2.5-Coder at
this scale, and Phase 3b now has a qualifying task (§9.2). The E5/E1 recompute closed clean (all
conditions shared one identical subset; claims stand with a scope note — §9.3.1).
**Resolved 2026-07-15, completing the audit:** the R1b.2d retrain landed and the
**kill line fired — H1 is a quantization artifact** (retrained-V bf16 SE **0.090** vs
likelihood 0.305, inside the registered artifact band). The SE matrix *inverts* across
pools: the same retrained verifier scores **0.364** on the old 4-bit pool — better than
the original — so the selection edge belonged to the quantization-corrupted candidate
pool (corrupted likelihood + easy-to-discriminate failures), never to the verifier.
**Both audited claims have now fallen** — H1 killed-as-artifact (§9.1), F2
retracted-as-structural (§9.2); what survives Phase 3R is the register null, the
escape-distance law, and the LCB-easy feasible region.
**Phase 3b executed 2026-07-16 (§9.7, [PHASE_3B.md]):** the elimination argument
survived its own audit (measured anchor, closed repulsion hatch, temperature-bounded
domain), and the frozen four-arm R3 returned a **powered, validated null** — with
oracle-grade execution traces supplied verbatim, a 1.5B base model recovers nothing
beyond the false-zero floor on a pass@50 = 0 stratum (floor predicted 2.0, observed
2), conditioning on code *sinks* quality below the artifact it aims at, and adding
the code anchor to trace feedback destroys the trace arm's small coverage.
Sample-based refinement at this scale is closed: **escape requires direction, and
direction requires capacity the model does not have — the constraint is not the
feedback channel but the model's ability to use it.** Open: r ∈ [0.05, 0.13)
(pre-declared unresolvable), and scales above 1.5B. *[AMENDED 2026-07-16, Phase 4
H0b/H0c: two over-reads in the last sentence, scoped rather than deleted. (i) "The
constraint is the model's ability to use it" reaches one rung past the arms — the
ceiling arm was an execution trace, which carries near-zero approach-level direction
for a structural failure, so the null localizes the bottleneck no deeper than the
trace channel; "capacity to use direction" is decided by the hint arm (H2a,
[PHASE_4.md]). (ii) "Closed" holds for in-context conditioning channels on
Qwen2.5-Coder at 0.5–1.5B; weight-space (test-time training) and search-space
channels were never enumerated, and family transfer is under audit (H1).]*
**Phase 4 executed (2026-07-16, [PHASE_4.md]) — the two exposures closed in
opposite directions.** The cross-family battery fired the retraction branches:
F1's shallow tail and D2c's SINK are **Qwen2.5-Coder properties** — the SINK
*inverts* on DeepSeek-Coder-1.3B and StarCoder2-3B, which benefit from the very
conditioning that degrades Qwen on both the code and the natural-language
channels (a measured double dissociation) — while the feasible region and the
anchoring law's form generalize (the law is also metric-robust: it survives
recomputation under structural AST distance). And the completed decomposition
**reversed the capacity claim**: given approach-level hints (the missing Olausson
rung; frozen and leakage-audited before any run), the same 1.5B model recovers
**13 of 68** provably-unreachable problems against a calibrated floor of 2
(p = 4.9 × 10⁻⁴, all recoveries validated), generating *off* the
coverage-vs-distance curve — **the constraint was feedback content, not
use-capacity**: traces carry no usable direction; stated approaches do.
Deployability caveat, stated plainly: the hint is oracle-derived, and R3/BSF
showed the model cannot produce hint-grade direction for itself — the bottleneck
moves from "use" back to "production," which is Olausson's original localization,
confirmed at 1/70th their scale.
**J5 (2026-07-17, running):** the 7B fork's first cell **rescopes the pathology
to 1.5B** — at 7B both the code-channel sink and the language-channel harm
vanish and the family rejoins DeepSeek/StarCoder2 (both frozen favourites hit);
the switch-on question met a pre-registered power gate en route — 7B's medium
stratum is a *live tail* (π₀ = 0), not a false-zero floor — so the
hard-difficulty extension is running under its own pre-registration. §9.9 J5
addendum, [PHASE_5.md] J5.

---

## 10. Working method — how this project reasons *(read first in any new conversation)*

*(Promoted to directly after the abstract, 2026-07-16 — Phase 5 J0: this section
is the document's actual thesis. The section number is retained so every existing
"§10" cross-reference in the record stays valid; the numbering below therefore
runs 10 → 0 → 1 by design.)*

This section is not results. It is the **operating method** that produced them, written
down so a fresh conversation continues in the same key rather than reverting to default
LLM habits (agreeing, refuting, declaring). The method is the reason a mostly-negative
record is worth publishing.

**The core loop: a failure is a pointer, not a verdict.** Every dead result in this
project spawned the next question rather than closing the book. H2's null → "what would
have to be true for *any* refinement to pay?" → the coverage/headroom frame. F2's negative
→ "is the tail structural or decoding-induced?" → R2. DIAG-8's anchoring → "is this about
*self* or about *conditioning*?" → D-measure → the escape-distance law → the elimination
argument. A refutation is treated as *information about our specifics*, not as a general
truth to adopt or a decision that settles the matter.

**Four rules that operationalize it:**

1. **Question what a refutation means *for our specifics*, don't import it as truth.** When
   a paper (or our own diagnostic) contradicts us, the first move is mechanistic: *why*
   does their setup produce that result, and does the mechanism even apply to ours? This is
   how Self-Debug (improves without execution feedback) and "How Many Tries" (universally
   effective repair) were reconciled rather than fought — different baselines (greedy vs
   compute-matched), different regimes (near-correct candidate vs structural failure),
   different scale. Neither is wrong; both are measuring where our effect is invisible.
2. **A decision is not a claim; a claim is not a finding.** Our own past suggestions,
   drafts, and pre-registrations are *hypotheses*, not results, until a committed artifact
   says otherwise. Prior-session enthusiasm ("BEST-SO-FAR is the charter") gets deflated by
   the next measurement (E5 = answer leakage) without ceremony. Provenance is tracked per
   claim: what is measured, what is inferred, what is still a bet.
3. **Pre-register, then append — never revise.** Predictions and kill criteria are written
   *before* the run, with odds where possible, and left standing whether they hold or not.
   Two D-measure predictions were falsified (one *backwards*); both stay on the page next to
   the corrected mechanism, because the correction is only trustworthy if the error is
   visible. Retractions are marked `[SUPERSEDED]`/`[retracted]` in place, not deleted.
4. **Turn the method on ourselves.** The same scrutiny applied to the field applies to our
   own new findings — hence the E5 subset-confound flag (§9.3.1) raised against our *own*
   freshest result before it is claimed, and the DIAG-2 problem-grouped-CV catch that killed
   a false 0.87 that our own pipeline produced. The failure mode we actively guard against is
   "treading into our own water": deriving a law post-hoc from a handful of cells and then
   fitting everything to it. The defense is out-of-sample replication (D2a's fresh 12 cells)
   and a standing generalization test (R2's benchmark family) with the law's predictions
   pre-committed.

**What this means for a new conversation.** Do not open by agreeing, and do not open by
declaring a result final. Open by asking what the newest number *means for our specific
system* and what question it opens. Peer-level pushback is expected and wanted; hedging and
diplomatic softening are noise. When new evidence could alter a fundamental, question the
fundamental — but remember the system under question need not be the one we started on
(the register died; the live system is now anchoring/escape, and that migration is the
point, not a detour).

**Addendum (2026-07-16, Phase 5 J0 — the journal turn relaxes nothing).** This
record is now organized as an experimental journal rather than as scaffolding for
a single claim (see the header and §0). The reframe's failure mode is named here
so it can be caught: without a claim as organizing pressure, the drift risk is
**wandering** — running whatever is fun and narrating it afterward. The
counter-pressure stays exactly what it has been: every run is pre-registered
against a *named question* with predictions, odds, and decision rules; every
phase has a charter; every verdict lands appended and dated. The unit of progress
changes from "claim defended" to **"question closed with scope"** — the
discipline that closes questions is unchanged. Chasing meaning in failures only
works if the failures are failures of something specific. One rule is added:
**every phase's writeup work includes updating the Claims & Scope Index (§0); a
phase is not closed with the index stale.**

**Addendum (2026-07-17, Phase 6 P2 — the distinct-seed protocol, codified).** A
committed floor test (J5 medium 4th) falsified because same-seed vLLM
regeneration reproduces ≈ 45–50% of a screen pool byte-for-byte, silently
suppressing every "fresh" control drawn with the screen's own seed. The rule that
follows is now part of the method: **any arm described as a fresh draw uses a seed
distinct from the seed that built the population it is compared against.** Phase 6
P2 was its inaugural *measured* application — a distinct-seed B1 (screen overlap
0.27 vs ~0.50 same-seed) verified the flagship floor on a genuinely-independent
control. The protocol is recorded operationally in §8; the general lesson is the
methodological one — a committed prediction, by falsifying, exposed a record-wide
bias that had sat invisible under every near-zero-floor arm.

## 0. Claims & Scope Index *(the journal's map — seeded 2026-07-16, Phase 5 J0; maintained at every phase close)*

Every claim this record has ever made, its current status, and the scope the
evidence actually supports. **This is the single place to check what the project
currently believes.** Statuses: LIVE / KILLED / RETRACTED / REVERSED / SCOPED.

| # | claim | status | current scope | where |
|---|---|---|---|---|
| 1 | Register-gated refinement beats verifier best-of-n | **KILLED** (exact tie, pre-committed kill) | Qwen2.5-Coder-1.5B, HumanEval, imitation regime | §4.3, §5 |
| 2 | Execution-trained verifier beats likelihood (H1) | **KILLED-AS-ARTIFACT** (quantization; SE matrix inverts across pools) | edge belonged to the corrupted 4-bit pool | §4.2, §9.1 |
| 3 | Register-null causal localization (injection = transfer failure; update = input starvation) | LIVE (frozen) | that stack, that regime | §5.3 |
| 4 | F1: function-call benchmarks have a shallow reachable tail | **RETRACTED-AS-QWEN-SCOPED** | true of Qwen2.5-Coder 0.5–1.5B; false of DeepSeek-1.3B (+0.177 in-band) and StarCoder2-3B (+0.252) | §7.3 banner |
| 5 | F2: no code benchmark offers refinement runway at this scale | **RETRACTED twice** (structural reading → R2; family reading → H1) | LCB-easy feasible on Qwen; runway wider off-Qwen (both families > Qwen) | §7.4, §9.2 |
| 6 | Escape-distance law (coverage monotone in escape distance; conditioning is a coverage effect, D2b) | **LIVE** | form: 3 families + lexical + structural-AST metrics; constants: family parameters; domain T ≲ 1.2, boundary descends with difficulty; in-context channels | §9.3, §9.3.1 |
| 7 | Elimination argument (undirected ≤ i.i.d.; repulsion inexpressible; direction the sole surviving channel) | **LIVE, completed** — direction now has an existence proof | measured on Qwen-1.5B; in-context channels only; weight-/search-space never enumerated | §9.3.1, §9.8 |
| 8 | D2c SINK (conditioning on partial-credit code degrades below both nulls) | **SCOPED + INVERTED**; scale-bounded (J5 Q1: vanishes at Qwen-7B); **origin measured (P6): CODER-STAGE diet, competence-windowed** | Qwen2.5-Coder-**1.5B–3B** code sink (deepest vs-iid at 3B); absent at 0.5B (competence floor) and 7B; general-1.5B (non-Coder) *not* pathological → the Coder continued-pretraining diet, not architecture/tie | §9.7 markers, §9.9 J5/P1, [PHASE_4.md] H1, [PHASE_6.md] P1 |
| 9 | R3 null — "1.5B cannot use direction" | **REVERSED-AS-REFINED** | a *trace-channel* null, now **cross-family**: traces sit on the floor on Qwen (1/68) and DeepSeek (2/76) — a content fact, not the Qwen pathology; content, not capacity, was the variable | §9.7, §9.8, §9.9 |
| 10 | Hint result — approach-level direction crosses the competence boundary (13/68 vs floor 2, p = 4.9e-4) | **LIVE — GENERALIZES** (J4: DeepSeek 9/76, p = 0.0039; **P2: floor distinct-seed verified**) | both families, medium strata, oracle-derived **complete-strategy-grade** hints (J2: dose-response unmeasurable on this set — weaker direction untested); the flagship contrast stands on a measured distinct-seed control (P2, fresh B1 = 2) | §9.8, §9.9, [PHASE_6.md] P2 |
| 11 | Qwen conditioning pathology (double dissociation: code and language channels degrade Qwen, lift DeepSeek) | **LIVE — SCOPED-TO-1.5B**; **origin measured (P6 P1): CODER-STAGE diet, competence-windowed, MIXED channels** | code sink 1.5B–3B (absent 0.5B/7B); language harm **1.5B-only** (3B hint-conditioning already helps +0.076) → the two channels disagree (MIXED); general-1.5B (non-Coder) clean on both → Coder continued-pretraining, not base recipe/tie | §9.8, §9.9 J5/P1, [PHASE_5.md] J5, [PHASE_6.md] P1 |
| 12 | Production bottleneck — "the model cannot produce hint-grade direction for itself" | **LIVE-MEASURED, cross-family + cross-scale** (J5 Q2 branch (a), the 40% favourite: floor-equivalent self-hint arm at 7B; production-adequate 0/68 Qwen-1.5B, 1/76 DeepSeek, **5/101 Qwen-7B**) | 1.3B–7B; **switch-on lies above 7B** — the cascade is the deployable shape through 7B; the open bracket is 7B–frontier (PlanSearch frame) | §9.9 J5 addendum, [PHASE_5.md] J5 |
| 13 | Temperature is a dose-responsive anti-anchoring intervention | LIVE | Qwen, HumanEval cells, within the law's domain | §9.3 |
| 14 | Provenance near-irrelevance (instruction verb ≫ provenance) | LIVE | Qwen; holds under lexical and AST metrics | §9.3, H0a follow-up |
| 15 | False-zero floor model (two-component mixture over k=50 pools) | LIVE — **5 for 6** (2.01→2, 2.01→2, 0.00→1-in-band, hard 2.09→1-in-band, **P2 distinct-seed 2.01→2-in-band**; **medium 4th test FALSIFIED**, 5.11→1 — traced to the same-seed harness confound, §8 caveat, not the Beta-binomial component: corrected E 3.02, P(X≤1) ≈ 0.20) | two families, three stratum shapes; structural discovery: π₀ = 0 at 7B-medium (live tail), π₀ = 0.76 at 7B-hard (the floor returns with difficulty) | §9.6, §9.9 J5 addendum, [PHASE_5.md] J5, [PHASE_6.md] P2 |

### 0.1 Instruments *(journal products independent of any claim)*

- **The false-zero floor model** (§9.6) — **3-for-3** across two families and two
  stratum shapes (2.01→2, 2.01→2, 0.00→1-in-band); turns "pass@50 = 0" from a
  label into an instrument with a stated noise floor. *(2026-07-17, J5 close:
  now **4-for-5** — hard 5th test hit (2.09 → 1-in-band); the medium 4th test
  (5.11 → 1, **falsified**) was traced to the same-seed harness confound, not
  the model component (§8 seed-policy caveat) — the falsification that found a
  record-wide bias. Structural discoveries: π₀ = 0 at 7B-medium (live tail),
  π₀ = 0.76 at 7B-hard. [PHASE_5.md] J5.)*
- **The reconciliation ledger** (§11) — no external result imported as truth;
  setup/delta/licenses per entry; it has caught *our own* overclaims twice
  (Olausson rung; Codex "replication" framing).
- **The hint leakage-audit protocol** ([artifacts/h2_hints_frozen.json]) — words
  only, no identifiers/numerals/code tokens, automated screen + hand audit; caught
  a real drafting error before freeze.
- **The AST-distance stack** ([scripts/h0a_ast_distance.py]) — canonicalized
  Zhang–Shasha with a validated C kernel; makes every lexical distance claim
  re-checkable structurally.
- **The per-family smoke gate** (H1 practice) — no family is screened broken;
  template validated before any cell counts.
- **The first-n bias lesson** (§7.2) — subset screens on *random* samples only;
  first-n was ~2× optimistic, caught by the confirmation step.
- **Hardened judges + ops ledger** (§8) — short-circuit vs all-cases matched to
  the analysis; detach/checkpoint/volume-first persistence; six recorded failure
  modes with fixes.

### 0.2 Extraction candidates *(papers are extractions from journal state, not the frame)*

No commitment implied; the journal decides when an extraction is ripe.

1. **The mechanism paper** — escape-distance law + elimination argument + the
   hint existence proof + the production gap (§9.3–9.9). *Phase-5 data landed:*
   J2 (complete-strategy scope note; dose-response needs a future varied set),
   J4 (cross-family trace/hint scope lines). **Extraction-ready.**
2. **The Qwen pathology note** — the double dissociation + SINK inversion
   ([PHASE_4.md]) + J4's four-arm table (traces null on the pathology-free
   family). Fastest to publishable, audience primed post-Spurious-Rewards.
   **Extraction-ready.** *(Spec updated 2026-07-18, Phase 6 P3 — the note is now a
   transcription of journal state; no paper is written under this record.)*
   The transcription-ready spec, with each claim's evidence in §0.3 rows 8/11:
   - **Title/scope:** a **Qwen2.5-Coder-small** conditioning pathology, and
     specifically a **Coder-continued-pretraining-diet** one — *not* a family
     claim, *not* architecture/tie (P0 + P1). general-1.5B (same arch/tie/scale,
     general Qwen2.5) is clean.
   - **Three dissociation axes:** (i) *channel* — code + language both degrade
     Qwen-1.5B, both lift DeepSeek (§9.8); (ii) *family* — Qwen-Coder-1.5B vs
     DeepSeek-1.3B / StarCoder2-3B (§9.7/H1); (iii) *within-family scale/competence*
     — sink at 1.5B–3B, absent at 0.5B (competence floor) and 7B (blends up), and
     the language harm is **1.5B-only** (P1, §9.9 P1 addendum). Axis (iii) is the
     new P6 contribution; the two-channel boundary mismatch is a **MIXED** result,
     stated as such, not smoothed.
   - **The §5 "mechanism" slot** = the measured origin line: **Coder-stage diet ×
     a competence window**; copy-fidelity does not track the sink (degradation at
     matched fidelity). No causal isolation of the synthetic-data variable is
     claimed (see limitations).
   - **Spurious-Rewards relationship, corrected:** their effect is on Qwen2.5-**Math-7B**
     (random-reward RLVR surfacing pretraining priors); **ours vanishes at
     Coder-7B** and lives at 1.5B–3B. Two *distinct* Qwen phenomena — related only
     as "family-specific pretraining artifacts," stated as such; do not conflate.
   - **Limitations to print on the tin:** Coder-3B is Qwen-Research-licensed (P0);
     the synthetic-data *mechanism* is not isolated (H1's confound, standing); the
     scale where the window closes (3B→7B) is unbracketed; StarCoder2's language
     channel is untested; fp16/other-stack replication is open (the Kaggle T4
     dead-end).
3. **The methods record** — §10 + §0.1 + the prediction-accounting trail (now
   including three floor hits and the J2/J3 grading instruments); needs no new
   data, only extraction.

### 0.3 Claims-to-evidence — the extraction transcription layer *(Phase 6 P3, 2026-07-17; maintained with §0)*

*(The purpose stated plainly, [PHASE_6.md] P3: after this table, extracting a
paper/talk/cited sentence is **selecting rows, not re-deriving support**. One row
per LIVE/SCOPED §0 claim, with the exact artifact, the test + number, the scope
line, and the §8 caveat that attaches. KILLED/RETRACTED rows (1, 2, 4, 5) are
excluded — their evidence lives in their retraction banners. Rows carrying a
Phase-6 "pending" gain their line when P1/P2 land.)*

| # | claim (tag) | evidencing artifact(s) | key test + number | scope line | §8 caveat / pending |
|---|---|---|---|---|---|
| 3 | register-null localization | `h2_result.json`, `diag2/3/5_*.json` | Δ(FULL−B1) = 0.000, CI [−0.049, +0.055]; W₀ transfer ×1.33→×0.28 (DIAG-5); U starvation: φ passed-AUROC 0.558, KL 0.117 nats directionless, Δpass 0.000 in-domain | that stack (d_r 128, 8 soft tokens, GRU), imitation regime, 1.5B frozen G | retired HF/4-bit stack — numbers never cross the M-boundary |
| 6 | escape-distance law | `dmeasure_conditioning.json` (`per_sample_D2b`), `h0a_ast_distance.json` | coverage monotone in PULL, Spearman **0.952** under AST = lexical; D2b mean-per-sample-pass flat ~0.20 at every T | form: 3 families + lexical + AST; constants: family params; domain T ≲ 1.2 (descends with difficulty); in-context channels | — |
| 7 | elimination argument | `dmeasure_e7.json`, `w0a_e0_anchor.json`, `h2a_hint_arm.json` | E7 repulsion loses **15–27 coverage pts** to i.i.d. (0.65/0.75 vs 0.92/0.90); direction existence proof HINT 13 vs floor 2, p = 4.9e-4 | Qwen-1.5B; in-context channels only; weight-/search-space never enumerated | — |
| 8 | D2c SINK (scoped+inverted, scale-bounded) | `dmeasure_d2c_partial_credit.json`, `h1_cross_family.json`, `h5_7b_pathology.json`, `h6_size_curve.json` | Qwen-1.5B cond **0.374** < copy 0.494 & < iid 0.468 (below-both, p ≈ 5e-5); DeepSeek inverts 0.468 vs iid 0.362 (p ≈ 0.003); **Qwen-7B 0.609 blend**; **P6 size curve: sink at 1.5B (−0.094 vs iid) + 3B (−0.150), absent 0.5B (+0.178) / 7B / general (+0.070)** | Qwen2.5-Coder **1.5B–3B**; origin = Coder-stage diet, competence-windowed (P6) | all-cases judge (frac consumed) |
| 9 | R3 trace null (reversed-as-refined; content fact) | `r3_conditional_reachability.json`, `h5_deepseek_fourarm.json` | TRACE floor: Qwen **1/68** (p = 0.875 vs B1), DeepSeek **2/76** (p = 0.50); generated at i.i.d. PULL 0.85 | cross-family (both), structural failures, **trace channel** (not "use") | near-zero-floor strata — same-seed confound cannot move it |
| 10 | hint result (generalizes) | `h2a_hint_arm.json`, `h2a_rerun_stability.json`, `h2a_validation_struct.json`, `h5_deepseek_fourarm.json`, `h6_p2_distinct_seed_b1.json` | Qwen **13/68** (11 hint-only/0, p = 4.9e-4, r ≈ 0.19); DeepSeek **9/76** (8/0, p = 0.0039, r ≈ 0.12); all rerun-stable; ≥ 0.16 AST-novel; timeout-class enriched | both families, medium strata, **complete-strategy-grade** hints (dose-response unmeasured — J2 ceiling 123/125 COMPLETE) | same-seed B1 control suppressed → contrast conservative; **P2 measured it: distinct-seed fresh B1 = 2** (overlap 0.27 vs ~0.50) — the 13-vs-2 contrast stands on a measured control ([PHASE_6.md] P2) |
| 11 | Qwen pathology / double dissociation (scoped-to-1.5B) | `h1_cross_family.json`, `h2_manip_check.json`, `h2_manip_check_deepseek.json`, `h5_7b_pathology.json`, `h6_size_curve.json` | Qwen code −0.095, language −0.096; DeepSeek +0.107 / +0.088 (double dissociation); Qwen-7B blends, harm vanishes; **P6: general-1.5B (non-Coder) clean — code +0.070, language +0.160 — so Coder-stage diet; language harm 1.5B-only (3B +0.076) = MIXED** | Qwen2.5-Coder **1.5B–3B** vs DeepSeek-1.3B; origin = **Coder-stage diet, competence-windowed, MIXED channels** (P6 P1) | 7B language near-saturation (E0 → 0.9); origin line now **measured** ([PHASE_6.md] P1) |
| 12 | production bottleneck (cross-family + cross-scale) | `h5_selfhint_qwen.json` + `_grades`, `h5_deepseek_selfhint_grades.json`, `h5_7b_selfhint_grades.json` | production-adequate self-hints **0/68** (Qwen-1.5B), **1/76** (DeepSeek-1.3B), **5/101** (Qwen-7B); self-hint arms floor-equivalent all three | 1.3B–7B; switch-on above 7B; cascade is the deployable shape through 7B | 7B arm read under same-seed confound (branch (a) adjudicated on the neutral-draw correction) |
| 13 | temperature dose-response | `dmeasure_conditioning.json` | T 0.8→1.2 coverage: E0 −0.02 (flat), E1 +0.10, E2 +0.18 (more-anchored ~2×) | Qwen, HumanEval cells, within the law's domain (T ≲ 1.2) | — |
| 14 | provenance near-irrelevance | `dmeasure_d2a_verb_provenance.json`, `h0a_d2a_ast_followup.json` | provenance ΔPULL ≤ 0.028 (lexical) / ≤ 0.034 (AST) vs verb up to +0.127 (3–4×) | Qwen; holds under lexical and AST | — |
| 15 | false-zero floor model (5-for-6) | `w0c_stratum_falsezero.json`, `h5_deepseek_floor_fit.json`, `h5_7b_floor_fit.json`, `h5_7b_hard_floor_fit.json`, `scripts/j6_p2_floor_predict.py`, `h6_p2_distinct_seed_b1.json` | hits 2.01→2, 2.01→2, 0.00→1, hard 2.09→1, **P2 distinct-seed 2.01→2**; miss medium 5.11→1 (harness confound; corrected E 3.02, P(X≤1) ≈ 0.20) | two families, three stratum shapes; π₀ = 0 at 7B-medium (live tail), 0.76 at 7B-hard | the same-seed confound is the miss that found it; distinct-seed now mandatory; **P2 6th test HIT** (distinct-seed B1 = 2 ∈ [0,4]; overlap 0.27 vs ~0.50) |

### 0.4 Open successors *(named, not chartered — [PHASE_6.md] P3; carried without commitment)*

Recorded here so the Index is also the map of what is *deliberately not being run*.

- **Origin of the small-Qwen pathology** — Phase 6 P1's live question (INTERACTION /
  DISCONTINUITY-OPEN / RECIPE-DEEP / CODER-STAGE); H-tie demoted to an interaction
  term at P0 (StarCoder2-3B is tied yet friendly).
- **The dose-response hint set** — J2's ceiling (123/125 COMPLETE) left the
  richness threshold unmeasured; a deliberately-varied COMPLETE/degraded/nudge set
  is the instrument. Disclosed wherever the 13/68 result is cited.
- **The 7B→72B switch-on bracket** — self-production is absent through 7B (0/68 →
  1/76 → 5/101); the switch-on lies above (PlanSearch frame). A phase of its own if
  ever chartered.
- **Weight-space / search-space channels (TTT, feedback-guided search, multi-model
  sampling)** — never in the elimination argument's in-context enumeration;
  recorded as outside scope since Phase 4, not as closed.

## 1. The claim and its kill criteria

Three hypotheses were pre-registered with kill criteria before any
comparison ran ([build-brief.md] §1, [PHASES.md]):

- **H1** — external consistency beats self-fluency as a confidence signal.
  *Kill:* verifier AUROC fails to clear likelihood AUROC by a pre-registered
  margin (ΔAUROC ≥ 0.05 with 95% problem-level bootstrap CI excluding 0,
  [METRICS.md]) on held-out problems.
- **H2** — the register carries functional load: register-gated iterative
  refinement beats verifier-reranked best-of-n (B1) *and* in-context
  refinement (B2) at matched compute. *Kill:* FULL ties either within noise.
- **H3** — settling depth tracks difficulty under early stopping. Gated
  behind H2; not run (§5.4).

Gate order was enforced: H1 gated H2; a failed gate was never tuned past
(two verifier attempts failed or were disqualified *before* H1 passed — §4.2
— and the H2 verdict below was recorded without post-hoc iteration).

## 2. Architecture

Four components ([ARCHITECTURE.md]; decisions D1–D10 in [DECISIONS.md]):

- **G (generator):** Qwen2.5-Coder-1.5B-Instruct, 4-bit NF4, frozen
  throughout (D6). Sampling: temperature 0.8, top-p 0.95, max 512 new
  tokens, seed 17 ([configs/base.toml]).
- **r (register):** d_r = 128 (D1). Problem-conditioned initialization
  (D4): r₀ = W₀ · φ(problem), where φ is the mean-pooled last-layer hidden
  state of frozen G and W₀ is a learned 1536→128 projection.
- **U (update):** GRUCell over [φ(candidate); v] → r, with RMS
  normalization of r and a max-norm clip (1.0) on each delta. r is updated
  by U and by nothing else.
- **V (verifier):** register-blind (D3). Final form (V-v2b, D9): the same
  1.5B base model fine-tuned as a cross-encoder classifier via 4-bit QLoRA
  (LoRA r=16, α=32, dropout 0.05 on attention projections + trainable
  1-logit head) over raw `(problem, candidate code)` text with execution
  labels.
- **Injection:** r → 8 soft-prompt embeddings (learned 128→8×1536
  projection) prepended to G's context (D1). This is the only way r touches
  G.

**Inference loop.** r ← r₀(problem); repeat: candidate ← G(problem, r);
v ← V(problem, candidate); r ← U(r, φ(candidate), v). Refinement means
*regenerate under the updated register* — G never sees a previous candidate
(that is baseline B2). Therefore the register is the sole cross-step
channel, and freezing it makes the steps i.i.d. — **the ablated FULL is
literally the B1 baseline** (same function, one flag; [rgr/loop/refine.py]).
Because r₀ is problem-conditioned, B1 also conditions on the frozen r₀, so
FULL−B1 isolates exactly the register *updates* (D4). A secondary control
B1′ (no injection at all) isolates the static value of r₀.

## 3. Experimental setup

**Task and data.** Code generation, because execution gives ground truth.
Training/validation: sanitized MBPP, 427 problems (385 train / 42 val,
seed-17 split), checksum-pinned. Held-out evaluation: HumanEval, 164
problems, checksum-pinned, and guarded in code — the data layer raises on
any training-tagged access to HumanEval ([rgr/data/splits.py]). Two
held-out evaluations ("peeks") were spent in total across all verifier
iterations, logged in [PHASES.md].

**Execution.** All candidates run in Daytona cloud sandboxes via a
self-contained driver returning {passed, frac_tests, error_type} with
per-test granularity and alarm-based timeouts. Ground-truth validation:
8/8 canonical MBPP/HumanEval solutions pass end-to-end; hanging, partial,
and malformed candidates map to timeout / fractional credit / automatic
failure respectively ([tests/test_driver.py], live smoke 2026-07-10).

**Matched compute.** Frozen before any comparison ([COMPUTE_ACCOUNTING.md]):
the budgeted unit is one candidate generation; every H2 condition consumes
exactly N = 8 generations per problem, ledger-enforced (comparisons across
unequal ledgers raise). Verifier calls (a ~1.5B forward each under V-v2b,
D9), update calls, and token counts are reported as audit columns; all
conditions use identical decoding parameters. Candidates whose output
contains no extractable code block still consume budget and score as
automatic failures.

**Reproducibility.** The Phase-0 baseline was locked twice with the same
seed policy: runs lock_a and lock_b produced byte-identical candidate code
on 164/164 problems and identical token totals (204,553 generated tokens)
— a bit-for-bit replay ([PHASES.md] Phase-0 gate).

## 4. Results

### 4.1 Baselines (Phase 0)

164 HumanEval problems × 8 samples (1,312 generations; mean 156 generated
tokens/candidate; format discipline 1300/1312 = 99.1% extractable; 3
sandbox faults = 0.2%) [runs lock_a/lock_b; PHASES.md]:

| Quantity | Value |
|---|---|
| B0 pass@1 (unbiased, n=8) | **0.5922** |
| B1 pass@1, likelihood-reranked | **0.6280** |
| pass@2 / pass@4 / pass@8 | 0.6997 / 0.7804 / 0.8415 |

The gap that frames everything: a correct candidate exists in the 8-sample
pool 84.15% of the time, but self-fluency selection recovers only 62.80% —
~21 points of selection headroom.

### 4.2 H1: execution-grounded confidence beats self-fluency — PASS on the retired 4-bit stack; **KILLED by audit 2026-07-15 (R1b.2d: quantization artifact — §9.1)**

> **⚠ Under audit ([PHASE_3R.md] R1; full detail §9.1).** R1a cleared H1 of the vLLM
> logprob bug (port-introduced, never touched the HF Phase-1 likelihood arm; Phase-0
> lock 0/1312 null `mean_logprob`). **R1b is the open, high-stakes leg:** on the
> stack-invariant Selection-Efficiency metric (SE = (selected−random)/(oracle−random)),
> bf16 *likelihood alone* reaches SE 0.305 — nearly the entire 4-bit V benefit
> (SE 0.315) — so H1's edge may have been "V beats *quantization-corrupted* likelihood."
> Free checks closed the mundane escapes (R1b.2b: V does discriminate subtle
> wrong_answer-only failures, within-AUROC 0.751; R1b.2c: not a length artifact). **The
> decider is R1b.2d — a bf16 verifier retrain; kill line: retrained-V bf16
> SE ≤ 0.305 → H1 does not survive de-quantization.** No H1 claim is final until it
> lands — and it has **not** landed: the retrain was killed by a 2026-07-14 power
> outage at epoch 3/3 (~step 450) with no checkpoint persisted, so the verdict never
> computed and a full rerun is required (§9.5). Numbers below stand as originally
> computed on the retired 4-bit stack.

> **AUDIT RESOLVED (2026-07-15): H1 KILLED — quantization artifact.** The R1b.2d
> retrain landed (fifth attempt; run-loss ledger §8) and the pre-committed kill line
> **fired**: retrained-on-bf16 V reaches SE **0.090** on the bf16 pool vs likelihood's
> **0.305** — inside the registered artifact band (0.05–0.10), against a registered
> prediction of 0.33–0.38 (wrong, and recorded as such). The decomposition is an
> **inversion** that localizes the artifact in the *pool*, not the verifier: the same
> bf16-retrained V scores SE **0.364** on the old 4-bit pool (better than the original
> Phase-1 V's 0.315), while likelihood there manages only 0.144. The 4-bit pool was
> doubly special — corrupted likelihood (weak opponent) and easy-to-discriminate
> failures (within-AUROC 0.7189 there vs 0.6377 on bf16). The table below therefore
> stands as a correct measurement of the retired stack, but its transferable content is
> a negative: **at 1.5B on a clean generator, an execution-trained cross-encoder does
> not beat the generator's own token likelihood as a selection signal.** No
> verifier-selection stage carries into any bf16-stack design
> ([artifacts/r1b2d_verifier_retrain.json]; [PHASE_3R.md] R1b.2d RESOLUTION; §9.1).

Evaluation set: the frozen Phase-0 candidates (1,312 held-out HumanEval
candidates with execution labels and stored mean token log-probabilities).

Three verifier iterations, selected purely on MBPP validation
([PHASES.md] Phase 1):

1. **V-v1** — MLP over pooled frozen-G features [φ(problem); φ(candidate)]
   (D7). MBPP-val AUROC 0.7498. Held-out: 0.7082 vs likelihood 0.6961,
   Δ = +0.0121, CI [−0.0460, +0.0700] → **failed the margin**
   [artifacts/h1_result.json]. Diagnosis: a feature ceiling — a linear
   probe trained *in-domain on HumanEval itself* with these features
   reaches only 0.642, losing to raw likelihood (0.678) on the same split,
   and within-problem macro AUROC was near chance (0.579 vs 0.568).
2. **codebert-base cross-encoder** — MBPP-val AUROC 0.665 < v1's 0.750 →
   disqualified on validation; its held-out scores were never opened.
3. **V-v2b (QLoRA cross-encoder)** — MBPP-val AUROC by epoch:
   0.7727 / **0.7814** / 0.7589; epoch 2 selected. Held-out (the single
   remaining pre-registered peek):

| Metric (held-out, n=1,312 candidates, 164 problems) | V-v2b | Likelihood |
|---|---|---|
| AUROC (pooled) | **0.7951** | 0.6961 |
| Δ AUROC, 95% problem-bootstrap CI | **+0.0991 [+0.0441, +0.1531]** | — |
| Within-problem macro AUROC (90 mixed problems) | **0.7189** | 0.5680 |
| ECE (likelihood min-max normalized) | **0.1616** | 0.2207 |
| Brier | **0.2117** | 0.2671 |
| B1 pass@1 when reranking with it | **0.6707** | 0.6280 |

[artifacts/h1_v2b_result.json; PHASES.md]. **H1 passes at double the
pre-registered margin.** Note the mechanistically important split: pooled
AUROC mixes cross-problem difficulty signal, but the *within-problem*
number — what selection actually uses — moves from near-chance (0.568) to
0.719 only when the representation is fine-tuned end-to-end on execution
labels. Frozen-feature probes cannot get there (v1's ceiling), and generic
code encoders are too weak (codebert). Execution grounding works, but only
through the representation.

### 4.3 H2: the register carries no measurable load — FAIL (the core negative)

**Register training (D10).** With V register-blind there is no
differentiable V→register path, so imitation was implemented as *likelihood
steering on synthesized prefixes*: sample k failed candidates
(k ~ U{0..7}) from the Phase-1 label set, unroll r_k through U over their
(φ, v) pairs, and minimize teacher-forced −log P_G(passing candidate |
prompt, soft(r_k)); G frozen. 2,628 train / 240 val examples from problems
with both outcomes; 2,422,016 trainable parameters; batch 4, lr 1e-4,
3 epochs. **The objective itself trained successfully**: val teacher-forced
loss 0.1713 untrained → 0.1530 at the selected epoch (−10.7% relative;
epochs: 0.1592 / **0.1530** / 0.1566) [kernel rgr-phase2-train; PHASES.md].
Prefix v-scores came from V-v2b (integrity check: re-scoring reproduced val
AUROC 0.7802 vs the 0.7814 reported at training).

**The comparison.** 164 HumanEval problems, N = 8 generations per
condition, ledger-verified [runs/phase2/full_b1.jsonl,
artifacts/h2_result.json]:

| Condition | Cross-step channel | pass@1 |
|---|---|---|
| FULL (register updating) | learned register only | **0.6829** |
| B1 (register frozen at r₀) — *the ablation* | none | **0.6829** |
| B1′ (no injection; frozen Phase-1 artifact) | none | 0.6707 |
| B2 (in-context refinement) | prev. candidate in prompt | **0.6220** |

**Δ(FULL − B1) = 0.0000, 95% CI [−0.0488, +0.0549]** (10,000 problem-level
bootstrap resamples). The pre-committed kill criterion — FULL failing to
beat B1 — fired. The kill record is now complete: **FULL does not beat B2
either** (Δ(FULL − B2) = +0.0610, CI [−0.0122, +0.1341], includes 0), and B2
itself does **not** beat B1 (Δ(B2 − B1) = −0.0610, CI [−0.1341, +0.0122]).
B2's cross-step channel was the **previous candidate plus a scalar
verifier-confidence estimate, with no execution feedback** (intrinsic
self-refinement — distinct from execution-grounded self-correction, which B2 does
not test). Conditioning on the previous attempt — higher-bandwidth than FULL's
register, at ~2× the prompt-token cost (566,712 vs 281,064) — buys nothing; the
pass@1 point estimate sits below B1 though its CI crosses 0. The Branch-A reading
(§5.3) follows: cross-step conditioning of any kind buys nothing on Qwen2.5-Coder at
this scale *(family scope pending H1 — [PHASE_4.md])*.

**Why this null is attributable, not ambiguous.** Every mundane explanation
was measured and excluded:

- *The register was not degenerate.* Mean ‖r‖ 12.12 (RMS-normalized scale
  √128 ≈ 11.3), mean per-step delta 1.757; no collapse, no blow-up
  ([rgr/register/diagnostics.py] on the FULL trajectories).
- *The verifier was not stale.* AUROC 0.7919 on FULL's own rollouts vs
  0.7951 at training time (threshold for refresh was a 0.05 drop).
- *Training was not a no-op.* The −10.7% teacher-forced val improvement
  above.
- *The tie is not aggregation hiding structure.* Paired per-problem
  outcomes: 103 both-pass, 43 both-fail, 9 FULL-only, 9 B1-only —
  perfectly symmetric disagreement. FULL's per-step pass rate is flat
  (0.60, 0.62, 0.61, 0.61, 0.57, 0.58, 0.60, 0.62 across steps 0–7), its
  mean verifier score shows no upward trend (0.693 → 0.705, non-monotone),
  and the argmax candidate's position is near-uniform over steps
  (29/18/22/18/21/12/21/23).

The causal chain therefore breaks at exactly one link: **likelihood
steering that is real under teacher forcing does not survive sampling.**
Eight soft-prompt embeddings driven by a 128-dim state can tilt token-level
log-probabilities of a designated target, but do not redirect which
solutions a 1.5B model actually samples.

The B1′ control (0.6707) sits 1.2 points below B1/FULL (0.6829), which
would suggest a small static benefit from r₀-conditioned injection alone —
but B1′ comes from a different sampling run (the frozen Phase-1
candidates), so this difference is within run-to-run noise and is *not
claimed*.

### 4.4 H3 — not run

H2 gated H3 ([build-brief.md] §1); with the register dead, "settling depth"
has no register semantics. A spin-off question survives — verifier-gated
adaptive *sampling* (early-stop best-of-n when v ≥ τ) vs fixed-n at matched
mean compute — and is future work, explicitly outside the original gates.

## 5. Discussion

### 5.1 What the experiment establishes

1. **The verification layer is where the load is.** The single largest
   correctness gain in the whole system came from replacing self-fluency
   with an execution-trained scorer (+4.3 pass@1 points at n=8; +15 AUROC
   points within-problem), and that gain required fine-tuning the
   representation, not probing frozen features.
2. **A learned cross-step latent, in its minimal honest form, added
   nothing** at 1.5B under an imitation regime — despite operating
   mechanically as designed and demonstrably steering teacher-forced
   likelihood. Because the register was the *only* cross-step channel and
   the ablation was the baseline, the null is attributable to the register
   updates specifically, not to confounds in the loop.
3. **Selection headroom remains large** (0.671 achieved vs 0.842 oracle at
   n=8): better verifiers still have ~17 points to claim, independent of
   any iteration mechanism.
4. **Pool coverage falls with cross-step bandwidth; the text channel's harm
   is real, the register's is null.** Oracle pool coverage (pass@8) is ordered
   **B1 0.848 > FULL 0.823 > B2 0.707** by how much each condition conditions
   on prior failed attempts (none / 128-dim latent / full previous-candidate
   text; DIAG-7, [DIAGNOSTICS.md]). Paired McNemar (DIAG-7b) shows the register
   step (FULL vs B1, a 4-problem gap) is **not significant** (exact p = 0.39);
   only B2's 23-problem crash is established (p < 1e-3). So the register is
   **null on coverage, not a demonstrated shrinker** — the point estimate is on
   the harm side but within paired noise. The text channel's harm, however, is
   **content anchoring**, not a formatting artifact: conditioning on the failed
   candidate makes B2's consecutive candidates only **0.35× as diverse** as
   i.i.d. draws (DIAG-8, a format-matched contrast) while pass rate *declines*
   0.61→0.40 across steps, with a local error-echo (DIAG-9b: adjacent-failure
   error-type match 0.85 vs 0.66 non-adjacent, +0.19 over the correct
   within-problem baseline; part of the decline is also no_code output-collapse)
   — G locally loops on its own mistake. This was structurally primed: at ~0.85 i.i.d. pool coverage
   there is almost nothing for cross-step conditioning to add and much for
   anchoring on a *shown-wrong* candidate to subtract. The null is therefore not
   "the register did nothing" but "on a saturated task, conditioning on prior
   *failures* is at best inert (latent register) and at worst actively harmful
   (raw text), scaling with channel bandwidth."

### 5.2 Honest bounds on the negative

The kill criterion is scoped: *this* register (d_r=128, 8 soft tokens,
GRU), *this* training signal (likelihood-steering imitation; no RL), *this*
scale (1.5B, frozen G), *this* domain (short Python functions). Any of the
following could in principle revive the mechanism and none is tested here:
RL over the loop with execution reward (regime (b) of D2), gradient paths
through a register-conditioned verifier (D3's deferred coupling),
higher-bandwidth injection (FiLM / cross-attention), or a generator scale
where soft-prompt control is stronger. These are future experiments, not
rescues of the present claim.

### 5.3 B2 and the pre-registered branch verdict

The B2 run (in-context iterative refinement, N=8) completes the pre-registered
record: the kill statement was "FULL ties B1 *and* B2." B2 cannot change the
gate verdict — passing required beating both — but it answers whether *any* form
of cross-step information (even raw text feedback) beats parallel sampling in
this setting, which decides how the null should be read. The interpretation is
committed here **before B2's number is known** (full statement in
[PRE-B2-HANDOFF.md] §3):

- **Branch A — B2 also ties B1.** Cross-step information of any kind, including
  raw text, buys nothing here. The null then says nothing about registers; it
  says this task on this model at this scale has no iteration headroom, as pass@8 = 0.842
  predicts. The experiment was uninformative about the hypothesis, and the next
  step is task redesign, not architecture.
- **Branch B — B2 beats B1.** Iteration pays, and a 128-dim latent through 8 soft
  tokens lost to putting the previous attempt in the context window: the register
  is architecturally parasitic to the in-context channel the transformer already
  optimizes for. The next step is an architecture rethink, not a task change.

**Standing prediction (recorded 2026-07-12, before the run): Branch A, ~65/35**
— pass@8 = 0.84 leaves little for iteration to do, and models do not reliably
self-correct without external feedback, which B2 as specified does not receive.

**Outcome (2026-07-12): Branch A — prediction held.** B2 pass@1 = 0.6220 (102/164)
vs B1 0.6829; Δ(B2 − B1) = −0.0610, CI [−0.1341, +0.0122]. B2 does not beat B1;
the point estimate and most of the CI mass put it below, though the CI crosses 0
so we make no significance claim on pass@1. **What B2's channel was:** the
previous candidate plus a scalar verifier-confidence estimate, with **no execution
feedback** — intrinsic self-refinement, which is distinct from execution-grounded
self-correction (feeding the actual error); B2 is evidence about the former only.
Conditioning on the previous attempt — higher-bandwidth than FULL's register, at
~2× the prompt-token cost (566,712 vs 281,064) — buys nothing. Direction is
corroborated not by the pass@1 CI but by the *direct* pool-coverage measurement
(DIAG-7: B2 0.707 vs B1 0.848). The H2 null is therefore uninformative about
registers *per se* and informative about the task. **Why redesign:** the ceiling
(pass@8 = 0.842, minus the 3–5 problems DIAG-1 shows dissolve under resampling) is
*channel-independent* — the argument is the ceiling, not "iteration is dead."
Prediction left standing as written.

*Caveat under active test.* The abstract's and §4.3's framing — "every link in
the chain worked except the last one" — was challenged by the post-mortem in
[PRE-B2-HANDOFF.md] §1, which argued three links (refinement headroom, the
register's near-chance φ input, and the proxy training objective) were likely
broken upstream. Two diagnostics have now reported ([DIAGNOSTICS.md]):

- **DIAG-4 refutes the post-mortem's arithmetic and opens a genuine
  contradiction.** The imitation targets are short (median 28 tokens, not the
  156-token HumanEval average the post-mortem imported); trained target seq-prob
  is ~1.4e-2, samplable. But 1.4e-2 vs untrained 8.3e-3 is a **1.7× gain** in the
  probability of sampling the target — which, had it transferred, forbids a
  0.0000 pass@1 move. The resolution is that both calculations measured the wrong
  object: the imitation loss raises P(*this specific* passing string), while the
  goal is P(*any* passing program), a set of enormous cardinality. The null is a
  **generalization failure from strings to the correctness manifold** — which
  indicts starting with imitation (D2(a)) rather than execution-reward RL, a
  set-membership objective. "Training was not a no-op" stands; *what it bought*
  is the open question.
- **DIAG-1 sharpens the null.** FULL's 9 wins are 8 reselection + 1 within the
  resampling-noise floor set by B1's 2 symmetric wins; B1 (frozen register)
  reaches *more* oracle-empty solutions than FULL (5 vs 3). The register's
  *generative* contribution is non-positive — strictly stronger than the
  aggregate tie. And since 3–5 of the 26 "oracle-empty" problems dissolve under
  resampling, they were low-probability, not unreachable: the genuine generative
  headroom on this benchmark is even smaller than 16%.

The full diagnostic record is now **closed** (10 diagnostics, [DIAGNOSTICS.md]
synthesis). The null is not a flat over-determination but a **two-component**
failure, one per learned part. **W₀ (static injection) is a *transfer* failure:**
its trained steering is ×1.33 in-domain but *reverses* to ×0.28 out-of-domain
(DIAG-5) — a learned prompt overfit to MBPP length, with the objective itself sound
(DIAG-4: samplable targets, 99.7% of the gain on the right decision tokens). **U
(the update dynamics — the actual RGR hypothesis) is a *mechanism* failure,
in-domain:** on MBPP val (U's training domain) r₀→r₇ moves pass rate by exactly
0.000, and the reason is a closed causal chain — φ near-chance → r_t barely encodes
correctness (DIAG-2, passed AUROC 0.558, no clock) → uninformative updates → KL
0.117 nats of *directionless* perturbation (DIAG-3; entropy-killer refuted) → Δpass
0.000. One word: **input starvation.** The outcome frame explains why neither could
have won: the task is saturated (DIAG-1/7), and conditioning on a failed candidate
anchors G to its own mistake (DIAG-8: consecutive candidates 0.35× as diverse as
i.i.d.; DIAG-9b: local error-echo +0.19 adjacent-vs-non-adjacent, pass 0.61→0.40
partly no_code collapse), while the register's own coverage effect is null not
harmful (DIAG-7b: FULL−B1 p = 0.39). The "every link
worked except the last" phrasing is retired. **The prioritization this hands
Phase 3:** in-domain/length-matched training fixes only W₀ (U already fails
in-domain); the single lever that touches U is **enriching what it conditions on —
a compact abstraction of *why* the last attempt failed, explicitly not the failed
candidate text** — and **DIAG-10 shows removing the candidate removes the *harm***:
with identical execution feedback, the candidate-anchored channel anti-refines while
the abstraction channel does not (ABSTRACT +0.088 vs B2+fb −0.162, +0.225 late-step
gap, several SE). Whether the abstraction adds *benefit* is untested — ABSTRACT ties
the B1 control on this saturated subset, a null that is uninformative (no headroom,
~2-bit signal). So feedback-benefit is Phase 3's **hypothesis** (its H1 gate), not an
established result. That, an on-policy set-membership objective, and a task with
genuine headroom are Phase-3 design, not extensions of this record.

### 5.4 The conceptual mapping, honestly closed

The brief's framing ([build-brief.md] §3) mapped chemical-state gating to
the register, the consistency manifold to the execution-trained verifier,
and Hamiltonian settling to inference-as-relaxation. The functional test
splits that mapping: the *external grounding* leg is supported (H1); the
*state-gated memory* leg is not (H2), in its minimal functional form; the
*settling* leg was never reached. No substrate claim was made and none is.

## 6. Phase M — the stack rebuild that made Phase 3 feasible

Phase 3 is materially larger than Phases 0–2 (more conditions, a large-k pass@k
screen, on-policy training), so throughput stopped being a convenience and became a
prerequisite. Phase M ([PHASE_M.md]) is a **no-science-change** port of the stack —
HF `generate()` + bitsandbytes 4-bit NF4 on Kaggle/Modal T4 → **vLLM continuous
batching + bf16 on Modal L4** ([DECISIONS.md] D11) — done at a clean phase boundary,
with the old stack tagged (`pre-phase-m-hf-nf4`) so every pre-migration number stays
a historical result, never cross-compared (§8). Five sequential gates, each passed
before the next:

- **M1 — the register path survives vLLM.** vLLM's `prompt_embeds` reproduces HF's
  soft-prompt injection: 19/20 problems byte-identical greedy over 48 tokens, 0/20
  diverging in the first 3 (the chat-template-splice failure signature). The
  make-or-break gate for any future register work; it passes.
- **M2 — throughput.** Same L4, same workload: HF bf16 batch-1 **28 tok/s** → vLLM
  bf16 continuous batching **2809 tok/s** = **100×** (281× over the old 4-bit/T4
  effective rate). The quota wall is gone; a DIAG-10-scale study now runs in minutes.
- **M3 — statistical re-baseline.** Reproduced the Phase-0 pool on bf16, execution
  held to Daytona so only the generation stack varies. All metrics shift **uniformly
  up and grow with k** — B0 0.5922→0.6479, B1-likelihood 0.6280→0.7256, oracle pass@8
  0.8415→**0.9024** — a modest, coherent, fully explained bf16 quality lift
  ([artifacts/m3_rebaseline.json]). (A logprob-population bug that would have
  corrupted the likelihood-rerank number was caught and fixed here.)
- **M4 — verifier revalidation → retrain required.** V-v2b scored on the *new* bf16
  candidate distribution keeps its global AUROC (0.772) but its within-problem
  reranking edge over likelihood **collapses from +0.15 to +0.016**
  ([artifacts/m4_verifier_revalidation.json]). The substrate change staled V's
  decision boundary; a verifier retrain on the deployment distribution is required
  and folds into Phase 3.
- **M5 — reproducibility becomes statistical.** vLLM's throughput kernels are **not
  bit-deterministic** run-to-run (greedy 143/164 byte-identical across two seeded
  runs). The Phase-0 bit-lock cannot be reconstructed; it is retired for a
  **statistical** standard — aggregate pass@k/AUROC reproduce within sampling noise
  (M3's two independent draws agreed to ~1 pt), which the CI-gated comparisons already
  assume ([DECISIONS.md] D14). An honest reduction in rigor, accepted as the cost of
  100× throughput.

Phase M is complete; total spend a few dollars inside Modal's free credit.

## 7. Phase 3 — when does cross-step conditioning pay?

### 7.1 The reframe

The register null is not the end of a question but the start of a sharper one. The
diagnostics (§5.3) establish two things the design of any refinement experiment must
respect: (i) conditioning on a *failed candidate* is actively harmful — it anchors
the generator to its own mistake (DIAG-8: consecutive candidates 0.35× as diverse as
i.i.d.; DIAG-10: the candidate-anchored channel anti-refines while the same feedback
*without* the candidate does not, a +0.225 late-step gap); so a refinement channel
must carry an **abstraction of the error**, not the attempt. And (ii) whether such a
channel adds *benefit* is untestable on a saturated task — DIAG-10/11 could measure
harm but not benefit, because a task with pass@8 ≈ 0.9 has no headroom to add to.
Phase 3 therefore stops asking about the register specifically and asks the general
question the record has earned: **on what task, at what scale, can cross-step
conditioning pay — and what task *structure* is required for the question to even be
answerable?** The register becomes one mechanism to be tested *inside* that frame,
after a qualifying task is found.

### 7.2 The benchmark screen (a mandatory pre-registered gate)

We have twice run a refinement mechanism on a saturated task and twice gotten an
uninformative null. Never again: Phase 3a selects the task on its **pass@k curve**,
not by name, against three pre-registered criteria ([PHASE_3.md] §4) — **coverage
band** pass@8 ∈ [0.30, 0.60], **reachable headroom** pass@50 − pass@8 ≥ 0.15, and
**feedback richness** ≫3 tests/problem (so execution yields a gradient, not a binary
— the same partial-credit signal the register was starved of). A task clearing all
three has correct-but-improbable solutions the model can be *steered* toward, and a
rich enough error signal to steer with.

### 7.3 Finding F1 — function-call benchmarks have a shallow reachable tail **[RETRACTED-AS-QWEN-SCOPED 2026-07-16 — Phase 4 H1]**

> **Retraction (2026-07-16, [PHASE_4.md] H1 RESULT).** The pre-registered
> cross-family retraction branch fired **verbatim**: on the same 200-problem
> BCB-Complete subset, same judge, seed 17, DeepSeek-Coder-1.3B-base shows
> pass@8 0.358 → pass@50 0.535 (**headroom +0.177 at in-band coverage** — it
> would have *passed* the Phase-3a gate this section says nothing can pass), and
> StarCoder2-3B shows 0.158 → 0.410 (headroom +0.252, below-band coverage). The
> ~0.09–0.12 cap reproduces on neither family. Everything measured below stands
> **as a fact about Qwen2.5-Coder (0.5–1.5B)**: its function-call tail is
> shallow; the task family's is not. The "property of the whole task family"
> reading — and the AlphaCode tension it created — is resolved against F1's
> general form (§11 ledger).

BigCodeBench (1140 problems, ~5 unittest methods each — the richest feedback of the
function-call benchmarks) was the lead candidate. It fails, and the failure is
precise and structural. On **random** samples (see the method note below), across
every difficulty × scale point:

| config (random, k=50) | pass@8 | pass@50 − pass@8 |
|---|---|---|
| Complete @ 1.5B | 0.302 | +0.108 |
| Complete @ 0.5B | 0.161 | +0.092 |
| Hard @ 1.5B (all 148) | 0.118 | +0.112 |

**The binding failure is headroom, not coverage** — it is structurally ~0.09–0.11
everywhere, never ≥0.15, *even where coverage lands in the band* (Complete@1.5B).
Whatever Qwen-Coder can solve on BigCodeBench it reaches within ~8 i.i.d. samples;
50 samples add only ~0.10. This is the **same "solve-within-8-or-not" shape that made
HumanEval useless for refinement** — one coverage level down, same structure — so it
is not a scale problem a different model fixes; it is a property of function-call
benchmarks with deterministic unit tests. **F1** ([DECISIONS.md] D16): refinement
needs a task whose **pass@k keeps climbing with k** — a deep tail of
reachable-but-improbable solutions — which the function-call family structurally
lacks. The result is negative but load-bearing: it converts "we couldn't find a task"
into "here is the *structural property* a task must have," and points directly at
competitive (stdin/stdout) benchmarks, where a model stumbles onto a correct approach
only occasionally over many samples.

**Method note (a second finding).** The initial screens used the *first n* problems
of each split; the full-benchmark confirmation showed first-n is **~2× easier than a
random draw** — (Complete, 0.5B) fell from pass@8 0.340 (first-40) to 0.161
(random-400). The premature "gate PASS + benchmark selected" that rested on the biased
subset was withdrawn (D15 retracted); all screening is **random-sample only** now.
The confirmation step caught the bias *before* Phase 3b was built on it — which is the
entire reason a confirmation step exists.

### 7.4 Finding F2 — sample-based refinement has almost no runway on code at 0.5–1.5B *[scope: Qwen2.5-Coder — H0c 2026-07-16, pending H1]*

> **⚠ Under audit ([PHASE_3R.md] R2; full detail §9.2).** F2's ≤0.12 headroom was
> measured under three inherited tail-suppressors — top-p 0.95 (nucleus truncates the
> improbable tail), temperature 0.8 (never swept), and Instruct tuning (entropy-collapsed
> vs a base model's deeper pass@k tail). Its honest current scope is "*instruct* Qwen at
> T=0.8/top-p=0.95 has a shallow tail." R2 re-screens with the tail un-suppressed
> (base completion model, top-p 1.0, T∈{0.8,1.0,1.2}); **base sweep complete: T=0.8
> (pass@8 0.328, headroom +0.097), T=1.0 (0.241, +0.149), T=1.2 (0.092, +0.133). The
> pre-registered trade-off is confirmed and has NO feasible base point — pass@8 needs
> T≤0.8 (only T=0.8 clears the band), headroom needs T≥1.0; they never co-occur.** If any
> config clears pass@8∈[0.30,0.60] ∧ headroom≥0.15, F2 narrows to the frozen config and
> the gate flips to PASS; if none does across base+instruct × 3 temps un-truncated, F2 is
> *strengthened* (structural, decoding confound ruled out). **Gate still open**, but every
> landed cell fails: base is exhausted with no feasible point, and instruct T=0.8 (pass@8
> 0.269, headroom +0.086) fails the band *from below* — base beats instruct at matched
> T=0.8 on both axes, the deeper-base-tail direction R2 predicted. Only instruct T=1.0/1.2
> remain (need regen after the 2026-07-14 outage, §9.5), and since instruct pass@8 already
> sits below the band at its coolest temp and falls with T, they cannot open a feasible
> cell. Evidence strongly trends **F2 strengthened-as-structural**.
>
> **AUDIT RESOLVED (2026-07-15, full grid landed — §9.2): F2 RETRACTED-AS-STRUCTURAL.**
> The trend statement above was written inside the BCB-only evidence window and did not
> survive the LiveCodeBench arm: **four LCB-easy cells clear both criteria** (base
> T=0.8/1.0/1.2 and instruct T=1.2; best headroom +0.250 in-band), so the pre-registered
> decision rule fires on its retraction branch and the Phase-3a gate flips to **PASS,
> scope narrowed to the qualifying configs**. What survives is F1 rescoped: the
> *function-call family* (BigCodeBench) stays infeasible at every un-suppressed cell.
> F2's tables and reasoning below stand as the historical record of the *suppressed*
> regime (instruct, T=0.8, top-p 0.95).

F1's implication was pursued to **LiveCodeBench** (contamination-controlled; 400
problems, ~27 test cases each; easy/medium/hard) via a new hardened stdin/stdout judge
(per-case run, short-circuit on first failure, process-group-kill + rlimit sandboxing,
normalized comparison — validated). Competitive benchmarks were the best hope: a deep
pass@k tail is their characteristic structure. They are deeper — but not enough. The
**complete Phase-3a sweep** (random samples, k=50):

| benchmark / tier | scale | pass@8 | pass@50 − pass@8 |
|---|---|---|---|
| BigCodeBench-Complete | 0.5B | 0.161 | +0.092 |
| BigCodeBench-Complete | 1.5B | 0.302 *(in band)* | +0.108 |
| BigCodeBench-Hard | 1.5B | 0.118 | +0.112 |
| LiveCodeBench-easy | 1.5B | 0.541 *(in band)* | +0.122 |
| LiveCodeBench-medium | 1.5B | 0.067 | +0.087 |

**FINDING F2 ([DECISIONS.md] D16): no configuration provides the reachable headroom
the gate requires (pass@50 − pass@8 ≥ 0.15); across the whole sweep it is capped at
~0.09–0.12** — two benchmark families, two execution paradigms (unittest and
stdin/stdout), three difficulty tiers, two model scales. The configs that land *in*
the coverage band (BigCodeBench-Complete@1.5B, LiveCodeBench-easy@1.5B) have shallow
tails; the ones with any more depth are below the band. **The gate returns a
NEGATIVE.**

The interpretation is structural and, we think, the real result of Phase 3. For a
Qwen2.5-Coder model at this scale, a problem is largely **gettable-or-not within a few
samples** — the solution distribution per problem is peaked, not heavy-tailed — so
pass@k **saturates fast** (pass@50 ≈ pass@8 + ~0.1 everywhere). Iterative refinement
needs the opposite: *reachable-but-improbable* solutions to steer a model toward. That
regime barely exists on code benchmarks here. And it does **not** yield to scale in
the obvious direction: a larger generator raises coverage (more saturation → *less*
headroom, BigCodeBench 0.5B→1.5B moved coverage +0.14 but headroom only +0.02), so
"use a bigger model" makes it worse, not better. This closes the loop on the original
register null: HumanEval had no headroom (pass@8 0.85) — and it turns out *no* tested
code benchmark at 0.5–1.5B (Qwen2.5-Coder) has enough. The register experiment was
starved of runway not by an unlucky benchmark choice but by a property of the whole
task family *(as sampled by this family — the AlphaCode tension and the cross-family
check are [PHASE_4.md] H1 cell (i))*. *[H1 RESOLVED 2026-07-16: the check fired —
"property of the whole task family" is **retracted**; it is a property of
Qwen2.5-Coder. Both audit families show headroom ≥ 0.15 on BCB and ≥ 0.23 on
LCB-easy; the starved-runway account of the register null stands for the stack the
register ran on, but the task family itself has runway off-Qwen (§7.3 banner,
[PHASE_4.md] H1).]*

**The fork (a decision for the next stage), and why F2 is the useful output.** Per the
pre-registration, a benchmark clearing the gate does not exist at this scale, so 3b/3c
do not proceed on a task that fails the screen (the exact error that produced the H2
null). The documented failure sharpens the next experiment far more than a forced pass
would: it says the refinement paradigm, to be testable, needs a task whose per-problem
**solution distribution is heavy-tailed** — e.g. genuinely open-ended generation
(agentic/multi-file, proof search, program synthesis with many valid targets), or an
*intermediate*-reward signal that creates a gradient where pass/fail is flat — not
another unit-tested function benchmark. Options on the table: (i) an intermediate model
scale / a benchmark with a heavier tail (untested — but the cap looks structural);
(ii) redefine the "reachable" axis away from i.i.d. resampling toward *feedback-driven*
recovery (does the model reach a solution it could not i.i.d.-sample, given an error
abstraction — the DIAG-10 direction — which does not require i.i.d. headroom); (iii)
accept F2 as the Phase-3 result and write the register/refinement story as *where and
why sample-based refinement has runway on code, and where it does not*. **Direction
(ii) is the most promising** — it is the one path the diagnostics actively support and
the one that does not depend on finding a heavy-tailed code benchmark that may not
exist. Pre-registration of the 3b redesign around it is the next step; it is a design
decision, not an extension of this record.

*Phase 3a is complete: gate outcome NEGATIVE (F2). Phase 3b/3c are held pending the
redesign the fork above describes.* *[SUPERSEDED 2026-07-16 — the redesign happened
and ran: F2 was retracted-as-structural by the R2 audit (§9.2), the 3b
pre-registration was frozen and executed as the Phase-3b design cycle ([PHASE_3B.md]),
and direction (ii) — feedback-driven recovery — returned a **powered NULL** at 1.5B:
§9.7.]*

## 8. Reproducibility

Everything needed to reproduce is committed: pinned datasets (SHA256),
frozen configs ([configs/]), the compute-accounting rule (frozen before any run;
its **amendment log** now records two stack moves — Kaggle→Modal T4, then the Phase-M
rebuild to vLLM/bf16/L4 — with the budgeted unit "one candidate generation" unchanged
through both), seed policy (17 throughout), per-record compute ledgers, and the full
gate log with dates and both failed verifier attempts ([PHASES.md]).

**Two reproducibility regimes, by stack.** On the retired HF/4-bit stack the Phase-0
reproduction was **exact** — byte-identical candidates on 164/164 problems across
independent runs (the bit-lock). On the current vLLM/bf16 stack that is unattainable
(M5): the throughput kernels are not bit-deterministic, so reproducibility is
**statistical** — aggregate pass@k/AUROC reproduce within sampling noise ([DECISIONS.md]
D14). **Numbers never cross the stack boundary:** every Phase-0/1/2 figure is a
historical result of the retired stack (recoverable at tag `pre-phase-m-hf-nf4`), never
compared to a post-migration number; Phase M's M3 re-baseline established a *new*
reference, not a correction of the old.

**Seed-policy caveat (2026-07-17, J5 — a measured harness property).** Seed 17
throughout has a cost the record only saw when a floor prediction falsified:
**same-seed vLLM regeneration of the same prompt reproduces ≈ 45–50% of a
50-sample pool byte-for-byte** (measured on Qwen-7B medium/hard arms and a J4
DeepSeek control). Any "fresh B1-50" drawn with the screen's seed is therefore
≈ half-correlated with the screen pool — and since strata are *defined* by
zero passes on that pool, the fresh arm's recovery expectation is suppressed,
while differently-prompted arms (HINT/SELFHINT: 1/2300 identical) are not.
On near-zero floors this bias is invisible (halving E ≈ 0–2 moves nothing, and
it works *against* the hint results, not for them); on the 7B live tail it
falsified the committed 4th floor test and manufactured an apparent
SELFHINT-vs-B1 trend that dissolves under the neutral-draw correction
([PHASE_5.md] J5 arms RESULT). Standing rule going forward: **fresh-draw
control arms use a distinct seed from the screen that defined their stratum.**

**Measured, not computed (2026-07-17, Phase 6 P2 — [PHASE_6.md]).** The survival
argument above was a computation; for the flagship number it is now a
measurement. A distinct-seed (41) fresh B1-50 on the Qwen 68-problem medium
stratum recovered **2** — the committed floor prediction (E 2.01, band [0, 4])
hit on a genuinely-fresh control whose byte-identical overlap with the screen
pool was **0.27** (vs the same-seed ~0.50). Same-seed suppression is thereby
*shown* invisible at this near-zero floor (same-seed and distinct-seed both gave
2), so the **HINT-13-vs-floor-2** contrast (§9.8) stands on a **measured**
control. The floor instrument goes **5-for-6**. [artifacts/h6_p2_distinct_seed_b1.json].

Infrastructure: Kaggle then Modal T4 for Phases 0–2 and the diagnostics (~25+
T4-hours), Modal L4 (vLLM) for Phase M and Phase 3, Daytona sandboxes for Phase-0–2
execution (12,100 runs; sandbox-fault rates 0.2% / 0.0% / 0.3%, faults scored as
failures), and hardened subprocess judges (process-group kill + rlimits) for the
Phase-3 benchmark screens ([scripts/modal_phase3a.py], [scripts/modal_lcb.py]).

**Operational reproducibility — designing runs against the platform's failure
semantics *(appended 2026-07-15)*.** "Question the underlying system" applies to the
compute platform, not just the science: pre-registration protects claims from us;
this ledger protects runs from the infrastructure. The R1b.2d retrain (a ~4.5 h
single-function T4 job) was lost four times in two days, each to a *different*
failure mode, before one hardened design closed all of them. The ledger, kept for
consistency of practice on any managed-compute service:

1. **Client-tied ephemeral apps.** Modal tears down a non-detached `modal run` app
   ~3 minutes after the local client disconnects. Two local power outages
   (2026-07-14, 2026-07-15 ~04:09 EDT) each killed ~2 h of remote GPU work this
   way. *Practice:* long runs launch with `modal run --detach`, which keeps the
   remote alive through client death (caveat: detach preserves only the
   last-triggered function — sufficient for single-`.remote()` entrypoints, not
   for chained remote calls).
2. **Function timeout below true workload.** The remote cap (3 h) sat under the
   measured ~4.5 h workload and killed a run mid-epoch-3. *Practice:* measure the
   workload before capping, set headroom (now 6 h), and checkpoint so a timeout is
   a resume, not a loss.
3. **Worker preemption restarts from scratch.** Modal reclaims workers and re-runs
   the function on the same input with no memory of prior progress. Two
   consecutive preemptions landed ~70 min in — both inside the ~15-minute
   post-epoch pool-scoring window that preceded the old end-of-epoch checkpoint —
   so each cycle billed a full epoch and persisted nothing; at that hazard rate a
   4.5 h monolith never completes while still spending. *Practice:* checkpoint
   within seconds of each epoch boundary (trainable params + full optimizer state
   + progress JSON keyed by a `run_id` nonce to reject stale state from earlier
   attempts), defer long scoring to a single resumable post-training pass, and
   resume on `run_id` match so a restart forfeits at most one epoch or one scoring
   pass.
4. **Result loss at the finish line.** The final artifact was computed by the
   *local* entrypoint from the remote's return value — a dead client would lose a
   completed run's payload. *Practice:* the remote persists the complete scored
   payload to the volume before returning; the verdict is recomputable from the
   volume plus `modal app logs` alone, with no live client required.

Two footnotes for honesty. *Recipe fidelity under resume:* restarts restore the
exact AdamW state dict, so a stitched trajectory differs from an uninterrupted one
only in the unseeded shuffle order — which D14 already leaves uncontrolled between
runs; resume is therefore a draw from the same run distribution, not a recipe
deviation. *Cost:* every one of these failure modes bills before it loses the work —
the un-hardened design converted an overnight outage plus a preemption cycle into
roughly half the project's remaining compute budget with zero scientific output.
Run-loss modes are spend-loss modes; hardening is cheaper than any single recurrence
([scripts/modal_rgr.py] `r1b2d_train_eval`, commit `7e4ea2f`).

5. **Judge-grade mismatch — a cost blind spot, not a run-loss mode *(appended
   2026-07-16, from the W4 spend audit)*.** One W4 app billed ≈$31 against a ~$1
   ephemeral-app baseline. Forensics (file-mtime stage timing + per-candidate error
   records): ~6.5 h of judging on a cpu=32/64 GiB container (≈$5.5–6/h), trivial GPU.
   The cause is a *grade mismatch*, not a runaway: the hardened judge deliberately
   runs **all ~15 test cases per candidate, no short-circuit** (the enrichment design
   — per-test frac, failing-case ids — that D2c/BEST-SO-FAR/W2 pools genuinely need),
   but the R3 arms inherited it while their analysis reads only `passed`; and R3's
   input is the worst case for all-cases mode — 13,600 candidates that are ~100%
   failing **by construction** (50,650 case executions per arm; every failing case
   run to completion; every TLE case burning the full 8 s; 202,600 one-case CPython
   launches). A short-circuit-on-first-fail judge for the R3 arms would have cut
   ~90% of case executions with zero loss to the frozen analysis: ≈$31 → ≈$4–6.
   *Practice:* (a) match judge grade to the analysis need — any-pass contrasts get a
   short-circuit judge, enrichment pools get the all-cases judge; (b) treat the
   pool's failure rate as a cost input — an all-failing pool maximizes judge cost
   exactly when all-cases mode is on; (c) size per-case timeouts to the model class
   (8 s is generous for a 1.5B correctness check; 3–4 s loses nothing on a TLE-heavy
   stratum); (d) batch a candidate's cases into one interpreter where isolation
   allows; (e) right-size judge containers — cpu=32/64 GiB bills for the full wall
   time whether saturated or not.
6. **External-hub dependency at runtime *(appended 2026-07-16)*.** A HuggingFace Hub
   outage (504s on the model API) killed a W4 R3 arm mid-chain — vLLM's loader
   file-list check failed after retries even though every byte it needed was already
   in the volume cache. Per-stage persistence limited the loss to one arm's restart.
   *Practice:* once a project's models/datasets are cached, run images
   **hub-offline** (`HF_HUB_OFFLINE=1`, `HF_DATASETS_OFFLINE=1`) so loads are
   cache-only and immune to upstream outages; remove the flag only when a genuinely
   new asset must be fetched ([scripts/modal_lcb.py] image env, commit `cc716f5`).

## 9. Phase 3R — auditing the two live claims, and the anchoring mechanism

Phase 3 published two load-bearing results on *inherited* Phase-0 choices: **H1** (an
execution verifier beats likelihood) and **F2** (no code benchmark here has a reachable
tail). Phase 3R ([PHASE_3R.md]) refuses to call either final until the unexamined
assumption each rests on is tested, and — spun off from the DIAG-8 anchoring finding —
pins down the *mechanism* of refinement harm. Order: **R1 → R2 → R3** (cheapest/highest-
stakes first). Standing rule unchanged: **append, never revise**; pre-register before
running; honest negatives. A judge fix predates all of it: the Phase-3a stdin/stdout and
BigCodeBench executors short-circuited on the first failing test, destroying the per-test
`frac_tests` signal R3/BEST-SO-FAR need; both now run all cases and emit
`{passed, n_tests, n_passed, frac, failing[], err, exc}` (committed `d6cbf37`).

### 9.1 R1 — is H1 a quantization artifact? *(the H1 audit)*

M4's flag (§6): V-v2b's within-problem edge over likelihood collapses +0.15 → +0.016 on
bf16. The audit reframes H1 on a **stack-invariant** metric — **Selection Efficiency**,
SE = (selected pass@1 − random pass@1) / (oracle pass@8 − random pass@1):

- **R1a (closed — bug-clear).** The vLLM `cumulative_logprob` bug was port-only; the HF
  Phase-1 likelihood arm was never touched (lock_a 0/1312 null). H1's number is not a
  logprob-population artifact.
- **R1b (open — the real question).** On bf16, **likelihood alone reaches SE 0.305**,
  nearly the whole 4-bit verifier benefit (**SE 0.315**) — H1 may have measured "V beats
  *quantization-corrupted* likelihood." Free CPU checks closed the mundane escapes:
  **R1b.2b** — V is not just a brokenness detector (it discriminates *subtle*,
  wrong_answer-only failures at within-AUROC **0.751**); **R1b.2c** — the bf16 likelihood
  advantage is not a length artifact (sum-logprob / shortest-candidate do not rescue it).
- **R1b.2d (the decider — RERUN PENDING).** Retrain V on the bf16 MBPP distribution and
  re-score. **Pre-committed kill line: retrained-V bf16 SE ≤ 0.305 → H1 does not survive
  de-quantization.** Predicted SE ~0.33–0.38 (partial survival). **Verdict not yet
  computed:** the retrain was killed by a 2026-07-14 power outage at epoch 3/3 (~step
  450); `r1b2d_train_eval` never commits the adapter to a volume, so the weights died with
  the container and no verdict was written. Labeled input (`r1b2d_mbpp_labeled.json`)
  survived, so the rerun repeats only the ~3-epoch T4 retrain. Last-known training signal
  (bf16, informational, *not* the verdict): epoch-1 val AUROC 0.7009, epoch-2 0.7410.
  [artifacts/r1b2b_stratified_auroc.json, r1b2c_length_bias.json].

**RESOLUTION (2026-07-15) — the kill line FIRED: H1 is a quantization artifact.** The
retrain landed on the fifth attempt (the four losses were infrastructure — the §8
operational ledger); val AUROC 0.6872 / **0.7069** / 0.6999, epoch 2 selected. The full
SE matrix, both pools × three rankers:

| SE | 4-bit pool | bf16 pool |
|---|---|---|
| likelihood (free) | 0.144 | **0.305** |
| V trained on 4-bit distribution | **0.315** | 0.067 |
| V retrained on bf16 distribution | **0.364** | **0.090** |

Retrained-V bf16 SE **0.090** ≤ 0.305 — the kill line fires inside the registered
artifact band (0.05–0.10); the registered prediction (0.33–0.38, partial survival) was
**wrong**. The matrix reads as an **inversion**: on the 4-bit pool any execution-trained
V beats likelihood (the bf16-retrained V, which never saw a 4-bit candidate, ranks it
*better than the original*); on the bf16 pool no V comes close, and on-distribution
retraining moved SE just +0.023. The edge was a property of the quantization-corrupted
candidate pool — corrupted likelihood (SE 0.144) plus easier-to-discriminate failures
(within-AUROC 0.7189 vs 0.6377) — not of the verifier. **H1 is retired**; likelihood is
the strong free selection baseline on the clean stack, and no verifier-selection stage
carries into 3b / R3 / BEST-SO-FAR (all execution-conditioned designs are unaffected).
Full decomposition and consequences: [PHASE_3R.md] R1b.2d RESOLUTION;
[artifacts/r1b2d_verifier_retrain.json].

### 9.2 R2 — is F2's shallow tail structural or decoding-induced? *(the F2 audit)*

F2 was measured under three independent **tail-suppressors**: `top_p=0.95` (nucleus
truncates the improbable tail — the exact thing refinement hunts), `temperature=0.8`
(never swept), and **Instruct** tuning (SFT/RLHF collapse generation entropy; base
completion models have far deeper pass@k tails — the Codex/AlphaCode reason to sample
from base models). R2 re-screens **BigCodeBench-Complete + LiveCodeBench-easy** across
generator {**base**, Instruct} × `top_p=1.0` × T ∈ {0.8, 1.0, 1.2}, random samples, fixed
judge. **Decision rule:** any config with pass@8 ∈ [0.30,0.60] **and** pass@50−pass@8 ≥
0.15 → F2 retracted-as-structural, scope narrowed to the frozen config, **gate PASSES**;
no config clears across base+instruct × 3 temps un-truncated → **F2 strengthened**
(structural, decoding confound ruled out). **Base completion path validated** (smoke:
64/64 well-formed modules, 0 degenerate, mean `frac_tests` 0.269, 44% pass ≥1 test —
graded feedback present). Base BigCodeBench sweep (n=200, k=50) **complete**: **T=0.8**
pass@8 **0.328** / pass@50 0.425 / headroom +0.097 (band ✓ — the only config to clear it);
**T=1.0** pass@8 0.241 / pass@50 0.390 / headroom **+0.149**; **T=1.2** pass@8 0.092 /
0.225 / +0.133. The **pre-registered trade-off curve is confirmed and has no feasible base
point**: pass@8 clears the [0.30,0.60] band only at T=0.8, headroom clears ≥0.15 only at
T≥1.0, and the two never co-occur (they move oppositely along temperature). This is the
"clean trade-off, no feasible point" branch — the pre-registered second-most-likely and
most-informative outcome. The **instruct comparison arm** (T=0.8 recovered exec-only after
the 2026-07-14 outage; T=1.0/1.2 need regen — §9.5) is the last input before F2 resolves.
**Gate still open**, trending **F2-strengthened-as-structural**. **Prediction (recorded
before running):** a trade-off curve (base + hotter T deepens the tail but drops pass@8);
most-likely one base point clears → F2 retracted-as-structural, with real uncertainty —
**outcome: partially falsified** (the curve is confirmed, but *no* base point clears both,
the more-informative branch). **Instruct comparison** T=0.8: pass@8 0.269 / pass@50 0.355
/ headroom +0.086 — fails the band *from below*; base beats instruct at matched T=0.8 on
both axes (0.328/+0.097 vs 0.269/+0.086), confirming the deeper base tail. Instruct
T=1.0/1.2 (killed by the outage, need regen) cannot open a feasible cell — instruct pass@8
already sits below the band at its coolest temp and falls with T. **Gate formally open
pending those two cells; evidence strongly trends F2-strengthened-as-structural.**

**RESOLUTION (2026-07-15) — the completed grid retracts F2.** The regenerated BCB
instruct cells landed as the trend required (T=1.0: pass@8 0.256 / +0.104; T=1.2:
0.167 / +0.103 — no BCB cell feasible anywhere in the 2×3 grid). But the
**LiveCodeBench-easy arm** — run on a newly built, smoke-validated base completion path
(fenced-completion prompt; 64/64 well-formed) over the full 80-problem stdin-easy
population, k=50, top_p=1.0 — **contains a feasible region**:

| LCB-easy cell | pass@8 | pass@50 | headroom | gate |
|---|---|---|---|---|
| base T=0.8 | **0.566** | **0.762** | +0.197 | **PASS** |
| base T=1.0 | 0.505 | 0.675 | +0.170 | **PASS** |
| base T=1.2 | 0.312 | 0.562 | **+0.250** | **PASS** |
| instruct T=0.8 | 0.525 | 0.637 | +0.112 | ✗ |
| instruct T=1.0 | 0.509 | 0.637 | +0.128 | ✗ |
| instruct T=1.2 | 0.391 | 0.600 | +0.209 | **PASS** |

The pre-registered rule fires on its first branch: **F2 retracted-as-structural; the
Phase-3a gate flips to PASS.** Suppressor decomposition at matched cells: architecture
is the biggest lever (base +0.197 vs instruct +0.112 at T=0.8, base dominating both
axes), temperature second (instruct +0.112→+0.209 across T), top-p alone nearly nil
(instruct T=0.8: 0.525/+0.112 at top-p 1.0 vs 0.541/+0.122 at 0.95). **What survives,
rescoped:** F1 — the function-call family's shallow tail — is now *decoding-controlled*
(BigCodeBench infeasible even fully un-suppressed); the honest replacement statement is
*"reachable headroom at 0.5–1.5B (Qwen2.5-Coder — H0c scope, pending H1) exists on
competitive stdin/stdout benchmarks under un-suppressed sampling, and does not exist
for function-call benchmarks at any tested decoding."* *[H1 RESOLVED 2026-07-16: the
first clause **GENERALIZES** — DeepSeek-Coder-1.3B and StarCoder2-3B both clear
headroom ≥ 0.15 on LCB-easy (+0.236/+0.232), each wider than Qwen's +0.197; Qwen has
the least runway of the three. The second clause is **QWEN-SCOPED** — both families
show BCB headroom ≥ 0.177 (§7.3 retraction banner). [PHASE_4.md] H1.]* Prediction accounting: the pre-registered phase-level call ("at least one
point clears → F2 retracted") was **correct**; the named clearing point (base BCB
~T=1.0) was **wrong** — BCB's trade-off has no feasible point, and the clearing came on
LCB-easy, whose higher coverage floor lets temperature buy tail depth without leaving
the band. The interim "trending strengthened" reads (recorded in the BCB-only window)
are superseded and stand with this outcome note. **Consequence:** Phase 3b has a
qualifying task; the config choice (recommend base T=0.8 — coverage-dominant, +0.197
headroom, cleanest error profile) is a 3b pre-registration decision, and R3's
pass@50 = 0 stratum is computable from the persisted enriched pools
[artifacts/phase3a_screen_lcb_r2_*.json; runs/modal/lcb_res_lcb_r2_*.json].

### 9.3 The anchoring mechanism — D-measure *(the DIAG-8 spin-off, closed)*

DIAG-8 showed conditioning on a failed candidate halves diversity. D-measure asks *what
that anchoring is*: single-step conditioning on committed HumanEval pools, conditions
E0 (i.i.d.) / E1 (self-fail) / E2 (foreign-fail) / E5 (correct), temps {0, 0.8, 1.2},
measuring **PULL** = 1 − edit-similarity to the conditioned artifact. All pre-registered,
append-only ([PHASE_3R.md] Addenda II/III):

- **The escape-distance law.** Conditioned on a failure, the single variable that
  predicts repair is **PULL** — how far the generation *escapes* the artifact. Coverage
  is monotone in PULL across conditions × temperatures (0.043→0.62). Provenance and
  framing are downstream of escape distance; the law absorbs DIAG-7/8/9b (all *low
  escape*, measured three ways). *[Domain bounded 2026-07-15/16: the law holds within
  the competence regime (T ≲ 1.2 on HumanEval; the boundary descends with difficulty —
  T = 1.2 already collapses on LCB-medium) and inverts past it, where escape is bought
  with broken samples — §9.3.1 W1 append, [PHASE_3B.md] W1/W2.]*
- **It is a coverage/diversity law, not per-sample quality (D2b).** On the confound-free
  **mean-per-sample-pass** metric (greedy pass@1 vs T>0 pass@8 had corrupted the earlier
  read), escape is **flat** — E1 sits ~0.20 at every T. Escape buys pass@8 by *spreading*
  the samples so one lands, not by improving each; conditioning **relocates** the
  distribution. [artifacts/dmeasure_conditioning.json → per_sample_D2b].
- **Temperature is an anti-anchoring intervention, dose-responsive.** ns=8 clean:
  T 0.8→1.2 lifts coverage only for anchored conditions (E0 −0.02 flat, E1 +0.10,
  E2 +0.18), and the *more*-anchored condition benefits ~2×.
- **The attractor is content-blind (E5).** Conditioning strength is invariant to whether
  the target is correct: E5 PULL (0.020/0.066/0.168) ≈ E2 PULL — the mechanism does not
  know what it points at. *(The earlier "E5 = empirical charter for BEST-SO-FAR" was
  **retracted**: E5-on-a-correct-artifact is answer-leakage, 98% copy; the partial-credit
  premise test is D2c/E6, pending R2's pools.)* *[D2c/E6 resolved 2026-07-16: **SINK** —
  conditioning on a partial-credit artifact lands significantly below both copying it
  and resampling; copy fidelity on LCB/base is only 0.57, a degraded blend, not a
  copy — §9.7.]*
- **Provenance is near-irrelevant — distinct from Tsui (D2a).** A verb×provenance 2×2
  on the *same* failed artifact: "self vs other" moves PULL ≤0.028 (→+0.006 pass), while
  the instruction verb ("improve it" vs "write a correct solution") moves it **3–4×**.
  The mechanism is **provenance-independent distributional conditioning** — not Tsui's
  *self*-anchoring blind spot; orthogonal to it (whose-output is inert, escape distance
  is live). [artifacts/dmeasure_d2a_verb_provenance.json].
- **Self-Debug reconciliation: escape needs direction.** Prediction (c) (TAX→0 at greedy)
  was falsified *backwards* — greedy is the *worst* case for anchoring (PULL 0.04–0.08 =
  near-total copy). Corrected: rich execution feedback supplies the **direction** to
  escape; undirected escape (raw resample, or a ~2-bit `error_class`) does not.
  **Escape requires direction; direction requires rich feedback** — R3's thesis with a
  mechanism, and it explains the split B2 (no feedback, copies) vs B2+fb (2 bits, still
  declines) vs Self-Debug (traces, works).

**The law under structural distance (2026-07-16, Phase 4 H0a — pre-registered branch
(a) fired, the 65% favourite; [PHASE_4.md] H0a, [artifacts/h0a_ast_distance.json]).**
PULL is lexical, and stdin/stdout boilerplate compresses lexical distances — so every
core plot was recomputed under a frozen structural metric (normalized Zhang–Shasha
tree edit distance on canonicalized Python ASTs; identifiers/constants canonicalized,
parse failures excluded and counted). **The law survives: escape is structural, not a
token artifact.** Coverage-vs-distance monotonicity is metric-invariant (Spearman
0.952 under AST, identical to lexical); every conditioned cell sits below the E0
anchor at matched T (AST anchor row 0.232/0.275/0.328 at T=0/0.8/1.2 vs E1
0.046/0.114/0.209); E7's repulsion stays inside copy territory; and the R3 trace arms'
"generated at i.i.d. distance" is a structural fact (TRACE/B1 AST ratio 1.048 —
ANCHOR, by contrast, structurally deep-copies at 0.38× B1). Two pre-registered misses
stand: **L1b** (provenance test, 75% odds) failed as *mis-specified* — E1-vs-E2
conflates verb with provenance; the correct instrument (D2a 2×2 under AST, post-hoc,
labeled — [artifacts/h0a_d2a_ast_followup.json]) shows provenance Δ ≤ 0.034 vs verb
Δ up to 0.127, so provenance-irrelevance survives structurally; and **L3** (60% odds)
missed narrowly — E1@1.2 closes ~64% of the *structural* escape distance (vs 52%
lexical), so the elimination argument's unclaimed room narrows to ~36% of the axis
without closing. One sharpening beyond the registered legs: **E0@1.5's AST anchor
equals E0@1.2's exactly (0.328 = 0.328) while lexical grew 0.594 → 0.740 — past the
temperature boundary, extra token-distance is structurally empty motion** (broken
surfaces over unchanged structures), tightening the law's temperature-bounded domain.
Destination geometry (opportunistic, no claim rests on it): TRACE-medium's escaped
mass spreads near-uniformly (max cluster fraction 0.20 — no second attractor);
E1@1.2 stays moderately concentrated (0.47).

### 9.3.1 What the escape-distance law forces — the elimination argument *(the current frontier of thought)*

Three consequences follow from D2b's refinement that the law is a **coverage/diversity**
effect (mean-per-sample-pass is flat, ~0.20 at every T for E1). They are the sharpest
things we currently believe, and they set R3's bar.

1. **Undirected failure-conditioning cannot exceed i.i.d. sampling; it can only approach
   it.** If escape buys coverage by spreading samples (not by lifting per-sample quality),
   then the *ceiling* of escape is the point where the generation has diverged so far that
   the conditioning is **vacuous** — i.e. full escape *is* i.i.d. E0's natural position on
   the escape axis is its own within-set diversity (DIAG-8 measured B1 i.i.d. pairwise edit
   distance **0.396**) *[ANCHOR SUPERSEDED 2026-07-15 — that number was pairwise diversity,
   a different metric than the conditioned cells' PULL; the measured commensurate anchor is
   **0.594 at T=1.2 / 0.491 at T=0.8** — see "E0 anchor, measured" below]*; E1 at T=1.2
   reaches only PULL 0.309 / coverage 0.62 against E0's
   ~0.90. So every undirected refinement scheme is **strictly dominated by resampling at
   matched compute** — a mechanism-level derivation of Olausson et al. (2024)'s empirical
   compute-matched conclusion, and consistent with our own DIAG-1/H2 record.
2. **Therefore the only escape hatch is *directed* escape.** The lone way to beat i.i.d. is
   feedback that tells the model *where* to go, not merely how far. This is not one option
   among several for R3 — it is, by elimination, the **sole surviving refinement
   hypothesis.** It also **retro-reframes DIAG-10**: ABSTRACT ≈ B1 (0.787 vs 0.762) was
   never an uninformative null — it was *complete escape with near-zero direction* (~2-bit
   error_class), landing exactly where the law says undirected escape must. R3's pre-
   registered success bar is therefore **strict**: ABSTRACT with *rich* feedback must
   **exceed** B1's coverage, not merely match it (matching is free from resampling).
3. **The paper's central figure is already computable.** Coverage vs PULL, every failure-
   conditioned cell, with E0 anchored at (0.396, ~0.90) *[superseded — measured anchor
   (0.594, 0.90) at T=1.2; see "E0 anchor, measured" below]*. Every measured point sits strictly
   under the i.i.d. anchor. R3 then either places a point *above* that line (directed escape
   beats resampling) or the sample-based refinement paradigm is, at this scale, finished
   *[H0c 2026-07-16: "finished" scoped — in-context channels, on Qwen2.5-Coder; see the
   channel-scope append at the end of this section]*.

**Tsui orthogonality, stated at the mechanism level (for related work).** Tsui's blind spot
is a **detection** failure (can the model *notice* an error is present); ours is an
**escape** failure (can the model *leave* an error it already knows about). In our setup
detection is never required — the failure is announced — so the blind spot has nothing to
bite on. The two axes coexist rather than compete; the "opposite-to-Tsui" read from the
first D-measure pass is retired (§9.3), superseded by "orthogonal, because we removed the
variable Tsui measures."

**A confound of our own, flagged before the claim is final.** The content-blindness /
neutral-attractor result (E5) and the "conditioning drops mean_pass" magnitude both depend
on **which problems each condition ran on.** E1/E2 require a *failed* artifact to condition
on; E5 requires a *correct* one. If those were populated by filtering the pool, then E1/E2
ran on a hard-biased subset and E5 on an easy-biased subset, and E0's own baseline on those
same subsets is the only fair comparison. **The escape-distance law itself is safe** (it
lives entirely within failure-conditioned cells and D2a replicated it on a fixed-artifact
2×2), and the temperature dose-response is safe (within-condition). **At risk and pending a
free matched-control recompute:** (i) the absolute size of the "conditioning drops per-
sample pass" drop — E1's subset excludes always-solved problems, which alone depresses
mean_pass; (ii) E5's coverage-1.00 / negative-TAX, which could be near-tautological if E5's
subset is "problems that have a correct candidate." **Action (committed, §9.5):** recompute
E0's mean_pass and coverage on E1's subset and on E5's subset before publishing the neutral-
attractor claim. This is the append-only method applied to *our own* new finding, not just
inherited ones.

**Resolution (2026-07-14, [artifacts/dmeasure_subset_control.json]; [PHASE_3R.md]
Addendum IV) — the feared confound is structurally absent.** All four D-measure
conditions, and all four D2a cells, ran on **one identical 60-problem subset** (the
first 60 M3-pool problems with both a failed and a correct candidate — verified by
pid-set equality and selection reconstruction), so E0-on-E1's-subset = E0-on-E5's-subset
= the published E0, and no cross-condition contrast ever crossed a subset boundary.
Claim (i) stands as measured (E0 0.5875 → E1 0.2375 at T=0.8, on identical problems);
claim (ii)'s tautology worry is real but bounded — every subset problem is
solvable-within-8 by construction, and the matched E0 is already near-saturated
(coverage 0.92/0.90 at T=0.8/1.2), so E5's margin over its fair baseline is small,
consistent with the answer-leakage retraction already in place. What remains is a
**scope note**, not a confound: the shared subset is mixed-outcome-only and first-60
(not random), ~8 pts harder than the full pool (M3 mean-pass 0.565 vs 0.648) — absolute
magnitudes are scoped to mixed problems; every within-subset contrast, the
escape-distance law, content-blindness, and the dose-response are unchanged.

**E0 anchor, measured (2026-07-15 — [PHASE_3B.md] W0a; the pre-registered 70/30
prediction was WRONG).** The figure's i.i.d. anchor had been *assumed* commensurate with
the conditioned cells' PULL axis: 0.396 was DIAG-8's within-set pairwise diversity, a
different metric. Measured directly — PULL of every committed E0 generation against the
same failed artifact each conditioned cell used — the anchor is **0.409 ± 0.319 (T=0) /
0.491 ± 0.212 (T=0.8) / 0.594 ± 0.178 (T=1.2)**, +0.198 from the assumed value at the
figure's anchor row, far outside the pre-registered ±0.05 band (odds were 70/30 the
other way; recorded). The secondary check holds — E0-PULL exceeds every conditioned
PULL at matched T — so the geometry does not invert; it **stretches**: E1@T1.2
(PULL 0.309) has closed only **~52% of the escape distance** to the honest i.i.d.
position, not the ~78% the assumed anchor implied. Two consequences. (i) The
"undirected escape can only approach i.i.d." asymptote has far more unclaimed room than
the old figure suggested, and nothing measured comes near it — the elimination
argument survives its first audit leg with a *larger* unexplained gap, not a smaller
one. (ii) Calibration: an i.i.d. sample sits only ~0.41–0.59 from an arbitrary failed
candidate on the same problem (natural same-problem token overlap), so conditioned
PULLs of 0.04–0.31 are deep inside copy territory — "escape" as measured has never yet
left the artifact's neighborhood. The central-figure spec now uses the measured anchor
per temperature; the 0.396 mentions above carry supersede markers in place.
[artifacts/w0a_e0_anchor.json].

**The repulsion escape-hatch, closed (2026-07-15 — [PHASE_3B.md] W1/E7; branch (a),
the pre-registered 55% favourite).** The elimination argument had excluded a third
limit *a priori*: **repulsive conditioning** (a model anti-correlated with the failed
artifact would sample i.i.d.-restricted-to-the-complement and could beat resampling by
not re-wasting draws on the failed basin). E7 populated the region: same protocol,
explicit-avoidance framing, T ∈ {0.8, 1.2}. Outcome — **repulsion loses to i.i.d. by
15–27 coverage points at matched compute** (E7 0.65/0.75 vs committed E0 0.92/0.90;
paired: E7-only 1 and 4 problems vs E0-only 17 and 13), and the sharper mechanism
finding is that **prompt-level repulsion is unachievable on Qwen2.5-Coder at this
scale**: the
avoidance instruction moved PULL just +0.02/+0.05 over plain "improve it" (0.196/0.357
vs anchor 0.491/0.594) — told explicitly to leave the failed basin, the model
generates inside copy territory anyway. The exclusion is now measured, not assumed;
"strictly dominated by resampling" stands as written. One secondary prediction was
**wrong, informatively**: E1@T=1.5 did not continue the coverage-vs-PULL curve — it
fell off a **competence cliff** (PULL 0.560 but coverage 0.18, mean_pass 0.035; E0@1.5
itself degrades to 0.37/0.067). **The escape-distance law's domain is
temperature-bounded (T ≲ 1.2):** past the boundary, escape is bought with broken
samples and coverage inverts. So the undirected route to i.i.d. is doubly closed —
asymptotically (the anchor is never reached) and practically (the temperature needed
to force the distance destroys the samples first). Figure spec: points carry
temperature labels; anchor row extends to T=1.5 (PULL 0.409/0.491/0.594/0.740,
coverage 0.65/0.92/0.90/0.37). [artifacts/dmeasure_e7.json].

**The sole surviving hypothesis, tested (2026-07-16) — and it nulled.** Item 2 above
made directed escape "the sole surviving refinement hypothesis by elimination"; the
frozen four-arm R3 (§9.7, [PHASE_3B.md] W3/W4) tested it at both ends of the
deployability spectrum — verbatim execution traces (no model in the loop) and
model-generated abstraction — on a 68-problem pass@50 = 0 stratum with the false-zero
floor stated in the null. **Every arm landed on the floor** (B1 2 — the W0c
prediction was 2.01 — ANCHOR 2, TRACE 1, MODELABS 3); the trace arms generated at
i.i.d. distance from the artifact (PULL 0.85), i.e. *full escape with direction
supplied*, and recovered nothing. The elimination argument's arc closes at this
scale: undirected escape approaches i.i.d. from below (item 1), repulsion cannot be
expressed (W1), and **direction — the one surviving channel — requires a capacity to
use it that 1.5B does not have.** r ≥ 0.15 is foreclosed; r ∈ [0.05, 0.13) and
scales above 1.5B remain open, stated in §9.7. *[AMENDED 2026-07-16, Phase 4 H0b
(Olausson ledger amendment): the bolded clause reaches one rung past the arms. The
trace carries near-zero approach-level direction for a pass@50 = 0 structural
failure, and MODELABS compresses the trace, so the arms bound the null at the
**trace channel**, not at "use." The honest closing: direction *as any tested arm
could carry it* went unused; whether stated approach-level direction (the Olausson
oracle rung) crosses the boundary is H2a's hint arm ([PHASE_4.md]), the missing rung
of this decomposition.]* *[RESOLVED 2026-07-16 — it crosses: HINT-50 recovered
13/68 against the calibrated floor of 2 (p = 4.9 × 10⁻⁴), generating off the
coverage-vs-distance curve (§9.8). The elimination arc's true ending: direction
works when it carries approach content; traces do not carry it; and the model
cannot yet produce that content for itself.]*

**The elimination argument's channel scope, stated (2026-07-16, Phase 4 H0c).**
Undirected escape (E0/E1/E2), repulsive escape (E7), and directed escape (R3's
arms) are all **prompt-space conditioning** — the enumeration lives entirely inside
the in-context category. Two channel categories were never in it: **weight-space**
(test-time training on the failure — the one mechanism whose literature claims
competence *extension*, not redistribution) and **search-space** (feedback-guided
tree search over partial programs; multi-model sampling, where a different model's
decorrelated errors are directed escape by construction). "Sample-based refinement
at this scale is closed" therefore holds **within the in-context category on
Qwen2.5-Coder at 0.5–1.5B** — that is the measured statement. TTT-on-the-stratum is
the named successor experiment, explicitly outside this record.

### 9.4 R3 + BEST-SO-FAR *(pre-registered; ride R2's enriched pools)* — **RESOLVED 2026-07-16 (§9.7)**

> **RESOLVED (2026-07-16 — the sketches below were superseded by the frozen
> [PHASE_3B.md] W3 design and executed as W4; full verdicts §9.7).** R3 ran as four
> arms (the Olausson decomposition added ABSTRACT-trace as the feedback ceiling) on
> the medium stratum this section did not yet know it needed (§9.6): **NULL at
> declared power** — every arm on the false-zero floor, the kill branch ("ABSTRACT ≈
> 0 forecloses the refinement direction") fired in its floor-aware form. The
> feedback-richness × temperature add-on was overtaken by W1/W2's harder finding:
> temperature is not an unbounded escape knob (competence cliff), so the "substitutes
> at the margin" cell grid was not run — recorded as superseded, not skipped
> silently. BEST-SO-FAR ran as five conditions: **the deflation below was right in
> direction and too gentle in degree** — BEST is not hold-at-best but **SINK**
> (generations land below the artifact conditioned on; fidelity 0.57), and
> BEST+ABSTRACT, "the only condition with a mechanism," scored **zero coverage**: the
> anchor does not complement the direction, it poisons it. D2c/E6, the premise test:
> **SINK** — BEST-alone dead exactly as the escape-distance law predicted, one branch
> darker.

- **R3 — conditional reachability (the central claim).** On the **pass@50 = 0** stratum
  (problems i.i.d. sampling provably fails in 50 tries), does an
  **error-abstraction-conditioned** model reach a solution i.i.d. cannot? Channels
  B1-50 / ANCHOR / ABSTRACT, matched compute, absolute recovery *count*. Add-on
  (Addendum III §4): cross **feedback-richness × temperature** — predicted substitutes at
  the margin, complements in the limit (rich-feedback × high-T = directed escape;
  2-bit × high-T ≈ resampling). Prediction: ABSTRACT > 0 and > ANCHOR. Kill: ABSTRACT ≈ 0
  forecloses the refinement direction.
- **BEST-SO-FAR — aim the attractor at a success.** Channels B1 / LAST / BEST /
  ABSTRACT / BEST+ABSTRACT on R2's feedback-rich pool, **oracle-first** ranking, matched
  compute. **Deflated by the escape-distance law** (Addendum III §5): since conditioning
  reproduces at 83–98% fidelity, BEST-alone ≈ **hold-at-best** (copying an 11/27 candidate
  yields ~11/27 — no repair); **BEST+ABSTRACT is the only condition with a mechanism**
  (best candidate = start point, abstraction = escape direction). **D2c/E6** is the
  premise test: condition on a ~40–60%-tests artifact, measure the generated candidate's
  `frac_tests` — flat → BEST-alone dead; climbing → a bigger result than scoped.

### 9.5 Live status (2026-07-16, post-W4 — **Phase 3b is executed and closed; see §9.7 verdicts**)

> **Status supersession (2026-07-16).** Everything below this banner describes the
> state at Phase-3R close (2026-07-15) and stands as the historical record. Current
> state: the Phase-3b design cycle ([PHASE_3B.md]) ran W0→W4 to completion — W0a
> anchor measured (prediction wrong, argument stretched), W1/E7 branch (a)
> strengthened + the law's temperature-bounded domain, W2 medium stratum 68/78
> (power: medium primary, easy demoted), W3 frozen, W4 executed: **D2c SINK, R3 NULL
> at declared power, BEST+ABSTRACT zero (anchor poisons direction)** — §9.7. Nothing
> is running. Open decisions (the user's, not run work): paper stage vs a scale
> escalation (the only axis the null does not foreclose), and whether to spend on
> the unresolvable band r ∈ [0.05, 0.13) with a larger stratum.
>
> **Phase 4 opened (2026-07-16 — claim hardening, [PHASE_4.md]).** H0 landed: AST
> robustness branch (a) — the law is structural (§9.3 append); Olausson amendment +
> four ledger entries (§11); the global Qwen2.5-Coder scope correction, SINK
> repositioning, elimination-argument channel scope (abstract banner, §9.3.1, §9.7);
> H3 cross-scale fork pre-registered (§9.7 addendum). Next in order: H1 cross-family
> battery (DeepSeek-Coder-1.3B, StarCoder2-3B) → H2 hint arm + near-miss band.
>
> **H1 executed (same day).** Verdicts: F1 QWEN-SCOPED (retracted, §7.3 banner);
> feasible region GENERALIZES (§9.2); SINK QWEN-SCOPED and inverted (§9.7); law
> form GENERALIZES. Full table + prediction accounting [PHASE_4.md] H1 RESULT.
> H2 (hint arm + near-miss band) frozen and running behind its manipulation gate.
>
> **H2 executed; PHASE 4 CLOSED (same day).** Gate HARM (hints depress Qwen
> per-sample — Qwen-scoped per E-H2's DeepSeek dissociation); H2b: HINT > B1
> inside the boundary (24→34, p = 0.015), TRACE null; amended stratum run:
> **HINT crosses the boundary — 13 vs floor 2, p = 4.9 × 10⁻⁴, validated** —
> "cannot use direction" retracted-as-overclaim (§9.8). Nothing is running.
> Open decisions (the user's): paper stage; the H3 cross-scale fork + 7B spot
> check (pre-registered, sign-off gated); TTT-on-the-stratum (named successor,
> outside this record); self-generated-hint experiments (the production
> bottleneck, §9.8); the r ∈ [0.05, 0.13) band.
>
> **PHASE 5 CLOSED (2026-07-16/17 — the journal turn + the direction tranche,
> [PHASE_5.md]).** J0: this record is now the primary artifact (title, §0 index,
> §10 promoted). J2: the oracle hints grade at a true COMPLETE ceiling
> (dose-response unmeasurable on that set — scope note on §9.8). J3/J4: **the
> production question is answered on two families** — models at 1.3–1.5B execute
> supplied complete-strategy direction (Qwen 13/68; DeepSeek 9/76, p = 0.0039)
> and cannot manufacture it (self-hint arms on the floor; production-adequacy
> 0/68 and 1/76); **the trace null is a content fact, not the Qwen pathology**
> (floor on both families); the false-zero floor is **3-for-3** (§9.9). J5: the
> 7B fork is costed (Q1 pathology $3–5, Q2 switch-on $11–19, independently
> authorizable) and awaits sign-off. Nothing is running. The extraction decision
> is open with the Index current: the mechanism paper and the Qwen pathology
> note both have their Phase-5 data.
>
> **J5 RUNNING (2026-07-17 — both questions signed off, [PHASE_5.md] J5).**
> Smoke PASS (L4 bf16; 7B ≈ 3× the 1.5B easy pass rate). **Q1 landed, both
> frozen favourites hit: the conditioning pathology is a small-Qwen (1.5B)
> property.** Code channel: conditioned 0.609 sits *between* copy-null 0.494
> and own-iid 0.659 — the blend, not the below-both-nulls signature (p = 0.075
> vs iid, p ≈ 1.0 vs copy); language channel: Δ −0.018 (ns), harm vanished
> (near-saturation caveat reported). Index row 11 rescoped; the pathology-note
> extraction gains a scale boundary. **Q2 in flight, one gate already fired:**
> the medium screen hit its committed band (stratum 46/78, 55% favourite) but
> the floor fit found a **live tail, not a false-zero floor** (π₀ = 0, eleven
> 1/50 near-misses, E[fresh B1-50] = 5.11 — committed as the instrument's
> fourth out-of-sample test, band [2, 9]); the floor-aware power envelope gave
> 0.22–0.70 at r = 0.20, under the frozen ≥ 0.70 rule — **arms did not launch
> on the medium stratum alone**; the pre-registered LCB-hard extension
> (identical selection rule, its own committed odds, a fifth floor test before
> arms, pooled power gate) is running. If the pooled gate also fails, Q2
> closes as structurally unresolvable at 7B under this budget. §9.9 J5
> addendum; results land in [PHASE_5.md].
>
> **J5 CLOSED (same day).** The hard extension restored the substrate
> (π₀ = 0.76; screen 2/3 predictions hit, floor-character missed at E 2.09 >
> 1.5) and the pooled gate passed (0.816 at r = 0.20, marginal). Arms: B1 2 /
> SELFHINT 5, p = 0.125 — **branch (a), the 40% favourite: self-production
> does not switch on by 7B** (blind grades: 5/101 production-adequate — the
> 45%-priced ≥ 30% prediction missed; the join shows recoveries do not
> concentrate on adequate hints). Floor instrument 4-for-5: hard 5th test hit
> (1 ∈ [0, 4]); medium 4th test **falsified** (1 vs [2, 9]) — diagnosed to the
> same-seed regeneration confound (§8 seed-policy caveat: "fresh" B1 arms are
> ≈ 50% screen-identical; the correction also dissolves the +3/−0 SELFHINT
> trend into the neutral-draw expectation). **Nothing is running; J5 and
> Phase 5 are fully closed.** Open decisions (the user's): extraction (both
> candidate papers now have their 7B data); the 7B–frontier switch-on bracket;
> the dose-response hint set; the distinct-seed protocol is a standing rule,
> not a decision.
>
> **PHASE 6 OPENED (2026-07-17 — where the pathology comes from + extraction-
> readiness, [PHASE_6.md]).** Pre-registration frozen; **nothing running (no
> GPU)**. **P0 done (free config gates):** tie flags pulled for all record
> models — the tie boundary in the Qwen-Coder line falls at 3B→7B (0.5/1.5/3B
> tied, 7B untied), and **H-tie is demoted to an interaction term** because
> **StarCoder2-3B is tied yet conditioning-friendly** (the falsifier the
> committed admission rule described; DeepSeek's literal trigger was untied and
> did not fire). Revision pins + the Coder-3B license note recorded. **P1**
> (pathology-origin discriminator battery: the two cheap cells on
> Qwen-Coder-0.5B/3B + general-1.5B; 3B is the slope-vs-open-step crux) and
> **P2** (distinct-seed verification of the flagship HINT-13-vs-floor number —
> the floor instrument's **6th** out-of-sample test) are pre-registered with
> odds and decision rules; **P2's floor prediction is committed: E = 2.01,
> point 2, 94% band [0, 4], ≥ 5 falsifies** ([scripts/j6_p2_floor_predict.py],
> reproducing §9.6's 2.01). **P3** (claims-to-evidence tables + the pathology-
> note revision) is journal work. Results land in [PHASE_6.md]; the Index and
> §8/§9.9 update as they do.
>
> **P2 landed (2026-07-17, Modal): in-band — the flagship floor is measured.**
> The distinct-seed (41) fresh B1-50 recovered **2** (committed point 2, band
> [0, 4]); the floor instrument goes **5-for-6**, and its first genuinely-fresh
> draw (screen overlap 0.27 vs same-seed ~0.50) confirms same-seed suppression
> is invisible at this near-zero floor — the **HINT-13-vs-floor-2** contrast now
> stands on a *measured* control (§8 caveat computed → measured; §10 distinct-seed
> protocol codified; Index rows 10/15). **P1 CLOSED (Modal bf16):** the Kaggle
> re-baseline was retired at its smoke — Kaggle's free T4 (sm_75) cannot run bf16,
> and fp16 would be a precision change the centerpiece shouldn't carry (recorded
> dead-end, [PHASE_6.md]); P1 ran on the existing Modal stack instead (no
> re-baseline). **Origin measured: CODER-STAGE diet** (general-1.5B clean),
> **competence-windowed** code sink (1.5–3B; absent at the 0.5B floor and 7B), and
> **MIXED** across channels (language harm 1.5B-only) — §9.9 P1 addendum, Index
> rows 8/11.
>
> **PHASE 6 CLOSED (2026-07-18).** All five gate conditions met: origin line
> (rows 8/11), flagship on a distinct-seed measured control (§8 computed →
> measured), distinct-seed protocol codified (§8/§10), claims-to-evidence tables
> (§0.3, 11 rows), pathology-note spec respec'd (§0.2). **Nothing running.** Open
> (author's, Index in hand): the extraction decision (pathology note is
> transcription-ready); §0.4 successors (dose-response set; 3B→7B window-close +
> 7B–72B switch-on; TTT) — named, not chartered.

*(historical, 2026-07-15)*

**Closed:** judge fix; R1a; R1b.2a/b/c; D-measure incl. Addendum II (judge/D-measure
pre-reg) and Addendum III (escape-distance law, temperature dose-response,
content-blindness, D2a provenance/Tsui, D2b metric fix); the 2026-07-14 outage record
(PHASE_3R.md "CRASH RECOVERY") and the full run-loss/hardening ledger (§8 operational
reproducibility — five R1b.2d attempts, four distinct infrastructure failure modes,
closed by detach + checkpoint/resume, commit `7e4ea2f`); **the E5/E1 subset
matched-control recompute** (§9.3.1 — confound structurally absent, claims stand with a
scope note; [artifacts/dmeasure_subset_control.json], [PHASE_3R.md] Addendum IV);
**R2 COMPLETE — the F2 gate FIRED on its retraction branch** (§9.2): BigCodeBench zero
feasible cells, LiveCodeBench-easy **four** (base T=0.8/1.0/1.2, instruct T=1.2; best
in-band headroom +0.250); **F2 retracted-as-structural, Phase-3a gate PASS, scope
narrowed**; enriched per-test pools persisted for all 12 cells (`bcb_res_*`,
`lcb_res_*`); **R1 COMPLETE — the H1 kill line FIRED** (§9.1, [PHASE_3R.md] R1b.2d
RESOLUTION): retrained-V bf16 SE 0.090 vs likelihood 0.305, registered artifact band;
the SE matrix inverts across pools (retrained V scores 0.364 on the 4-bit pool) — **H1
killed-as-artifact; the edge lived in the corrupted candidate pool, not the verifier.**

**Running:** nothing. No GPU job is required by any closed item.

**Phase-3R outcome, one line: both audited claims fell** — H1 killed-as-artifact, F2
retracted-as-structural — and what survives is the register null (H2), the
escape-distance law + elimination argument, and the LCB-easy feasible region. No claim
was reversed silently; every prediction stands with its recorded outcome, including the
two audit-prediction misses (R1b.2d predicted partial-survival 0.33–0.38, landed 0.090
artifact; R2 named base BCB ~T=1.0, the feasible region landed on LCB-easy).

**Pending (unstarted — design decisions, not run work):** 3b pre-registration on the
qualifying LCB-easy config (recommend **base T=0.8**: pass@8 0.566 / headroom +0.197;
note the H1 consequence — selection/ranking stages in any 3b design use likelihood or
execution feedback, never a learned verifier); **D2c/E6** (partial-credit conditioning —
premise test for BEST-SO-FAR; enriched pools ready, 360 partial-credit candidates);
**R3** (conditional reachability on the pass@50 = 0 stratum of the chosen config;
stratum sizes 19/26/35/32 across the four feasible cells — small, consider LCB-medium
extension if the 5–20% recovery prediction needs resolution); **BEST-SO-FAR**.

**Restart ordering for a fresh conversation:**
1. **3b pre-registration** — pick + freeze the qualifying config (§9.2 recommendation:
   base T=0.8), write predictions/kill criteria for R3, D2c/E6, BEST-SO-FAR before any
   run. Inherit the H1 verdict: no verifier-selection stage on the bf16 stack.
2. **D2c/E6 → R3 → BEST-SO-FAR** in that order on the frozen config's enriched pools.

**Ordering superseded (2026-07-15, same day):** the Phase-3b design-cycle charter
([PHASE_3B.md]) inserts a hardening pass **before** the 3b freeze — the elimination
argument (§9.3.1), now the central claim, gets the same audit treatment H1 and F2 got.
New order: **W0** (free CPU: measured E0 anchor, D2c copy-null, stratum false-zero
rate) → **W1** (E7 repelled-conditioning arm — the asymptote's unpopulated third limit)
→ **W2** (LCB-medium base screen — size R3, power check) → **W3** (freeze the 3b
pre-reg: R3 four-arm with ABSTRACT-trace ceiling, recovery validation protocol) →
**W4** (execute D2c/E6 → R3 → BEST-SO-FAR). A reconciliation ledger (§11) now governs
every external result used in design.

### 9.6 Stratum characterization — the pass@50 = 0 label has a false-zero floor *(2026-07-15, W0c; W2 extends)*

R3's target stratum ("problems i.i.d. provably fails in 50 tries") is not a clean
label: a problem with true per-sample rate p = 0.01 survives 50 draws with probability
~0.60. From the persisted k=50 pools of the four feasible cells, a two-component
maximum-likelihood fit (point mass at p = 0 + Beta over reachable p; pure-Beta fit as
upper bound) gives the **expected lucky-recovery count a fresh B1-50 control arm
produces on the stratum by chance alone**:

| cell | stratum (0/50) | x=1 / x=2 near-misses | E[B1-50 lucky recoveries] (upper) |
|---|---|---|---|
| base T=0.8 | 19/80 | 10 / 5 | **3.6** (3.9) |
| base T=1.0 | 26/80 | 5 / 4 | 2.3 (5.3) |
| base T=1.2 | 35/80 | 10 / 5 | 5.0 (6.9) |
| instruct T=1.2 | 32/80 | 10 / 3 | 4.6 (5.4) |

The mixture split is fit-unstable cell-to-cell (P(reachable | 0/50) ranges 0.22–0.81),
but the floor is stable: **~2–5 lucky recoveries per stratum**, the same order as the
pre-registered 5–20% recovery prediction (1–7 recoveries on 19–35 problems). Two design
consequences, both binding on W3: (i) R3's primary contrast must be **ABSTRACT >
B1-50, paired** — ABSTRACT > 0 is theater, and this floor goes into the stated null;
(ii) **the easy strata alone are unpowered** — the signal and the noise floor are the
same size — so the LCB-medium screen (W2) is a prerequisite, not a contingency.
[artifacts/w0c_stratum_falsezero.json].

**W2 extension (2026-07-15) — the medium stratum is the R3 instrument.** Base
completion, top_p 1.0, full 78-problem medium-stdin population, k=50: **T=0.8** pass@8
0.048 / pass@50 0.128 → **stratum 68/78 with feedback richness intact** (66/68 problems
hold partial-credit candidates; 1,400 partial candidates; median 15 tests) and a
false-zero floor of only **~2.0 expected lucky B1-50 recoveries** (floor *rate* 3% vs
the easy stratum's 19%). The pre-committed rule fires: R3 runs on easy + medium,
analyzed separately. Power (exact paired McNemar, α=0.05 one-sided): medium n=68
reaches 73%/92% power at recovery rate 0.15/0.20; the easy stratum has power 0.25
*even at r=0.40* and is demoted to exploratory. **A medium null forecloses r ≳ 0.15;
r ∈ [0.05, 0.13) is pre-declared unresolvable.** Two prediction misses recorded in
[PHASE_3B.md]: the base-beats-instruct suppressor ordering **inverts on medium** (base
0.048/0.128 vs instruct 0.067/0.154 — the base-tail advantage is an easy-tier
phenomenon), and T=1.2 medium collapses outright (pass@50 0.026, stratum 76/78,
richness 64%) — the competence cliff W1 met at T=1.5 on HumanEval arrives at T=1.2 on
medium: **the escape-distance law's temperature boundary descends with difficulty.**
[artifacts/phase3a_screen_lcb_r2_base_medium_T{08,12}.json].

**Floor model validated out-of-sample (2026-07-16).** R3's fresh B1-50 control arm
recovered **exactly 2** problems on the 68-problem medium stratum — the two-component
fit's prediction was **2.01**. The false-zero characterization is not just a caveat;
it is a calibrated instrument, and R3's null rests on it (§9.7).

### 9.7 Phase 3b — the frozen pre-registration *(W3, 2026-07-15; verdicts land here as W4 executes)*

The full frozen text is [PHASE_3B.md] W3; the load-bearing content: **Config** — base
Qwen2.5-Coder-1.5B, fenced completion, T=0.8, top_p 1.0, seed 17, hardened judge, no
learned verifier anywhere. **R3** — four arms on the medium stratum (n=68; easy n=19
exploratory-only): B1-50 / ANCHOR / **ABSTRACT-trace** (templated execution feedback,
no model in the loop — the ceiling arm without which a null is ambiguous, per the
Olausson ledger entry) / **ABSTRACT-model** (1.5B-Instruct compresses the same trace —
the deployable channel). Primary contrast: ABSTRACT-trace > B1-50, paired exact
McNemar, α=0.05, null floor ≈2.0 lucky recoveries stated; **power envelope declared:
a null forecloses r ≳ 0.15, r ∈ [0.05, 0.13) pre-declared unresolvable.** PULL
recorded for every generation; a *successful* trace arm must sit **off** the
coverage-vs-PULL curve (relocated mass, not spread — the only mechanism a 0/50 stratum
admits). Every recovery: judge rerun + contamination audit (contest-date vs base-model
exposure + AST dissimilarity vs the failure pool) + error-type stratification.
**Key odds:** ABSTRACT-trace significant 15% / positive-unresolvable 45% / null 40%;
ANCHOR ≤ B1-50 75%; ABSTRACT-model ≤ ABSTRACT-trace 80%. **D2c/E6** (runs first): 44
problems, artifact = band candidate nearest frac 0.5, verdict = CLIMB ~20% / FLAT ~65%
/ SINK ~15% against the W0b copy-null and i.i.d.-null. **BEST-SO-FAR** (runs last): 30
refinement-regime problems, five conditions, oracle-first by frac_tests; Addendum III
§5 predictions stand.

**VERDICTS (2026-07-16 — W4 executed; full detail + prediction accounting
[PHASE_3B.md] W4 RESULTS).** **D2c/E6: SINK** (the 15% branch) — conditioning on a
~0.49-frac artifact yields mean frac 0.374, significantly below copying (p ≈ 5×10⁻⁵)
and below i.i.d. (0.468); copy fidelity on LCB/base is only 0.57 (the 0.83–0.98
HumanEval/instruct regime does not transfer) — conditioning produces a *degraded
blend*. *[Repositioned 2026-07-16, H0c: SINK is a quantified
replication-plus-extension of the Codex buggy-prompt imitation phenomenon (§11
ledger) — the extension is the compute-matched, execution-quantified below-both-nulls
result. Two causal stories fit it — SINK-as-capacity ("cannot use the anchor") and
SINK-as-distribution-matching ("faithfully continues the quality register") — with
opposite scale predictions; this record cannot distinguish them; the H3 addendum
below pre-registers the discriminating fork.]* *[AMENDED same day — H1 measured it
across families and the SINK **INVERTED**: on the same 44 artifacts, same judge,
conditioning lifts DeepSeek-Coder-1.3B **above** its own i.i.d. (0.468 vs 0.362,
a significant climb, p ≈ 0.003) and StarCoder2-3B likewise (+0.046 n.s.), both
landing between own-iid and the artifact — the imitation/blend story, working as
Codex predicts. Qwen alone lands **below both nulls**. So the "replication" framing
over-credited the precedent: quality-matching explains the cross-family *blend*,
not Qwen's sink — for Qwen, whose i.i.d. (0.468) ≈ artifact (0.494), imitation
predicts *no change*, yet it degraded to 0.374. **SINK is a Qwen2.5-Coder-specific
conditioning degradation**, and H3's fork is partially pre-empted: the
distribution-matching account already fails to explain the one family that sinks.
[PHASE_4.md] H1 RESULT.]* **R3: NULL at declared power** (medium, primary): B1-50 recovered exactly 2 —
the W0c floor prediction to the decimal — and every arm sits on the floor (ANCHOR 2,
TRACE 1, MODELABS 3; TRACE vs B1 p = 0.875 — and **MODELABS 3 vs TRACE 1 is floor
noise, p = 0.875: it supports no compression-helps reading**). The PULL column
carries the mechanism: TRACE/MODELABS generated at i.i.d. distance (0.85 ≈ B1's
0.84; structural per H0a — AST ratio 1.048) — *full escape with direction supplied*
— and recovered nothing; at 1.5B the model cannot **use** direction on problems
beyond its competence, at either end of the deployability spectrum. *[AMENDED
2026-07-16, H0b: "cannot use direction" over-reads — the arms bound the null at the
trace channel (near-zero approach-level direction for structural failures); the
use-capacity question is decided by H2a's hint arm ([PHASE_4.md]), the missing
Olausson rung.]* *[DECIDED same day, §9.8: the hint arm crossed the boundary
(B1 2 → HINT 13, p = 4.9 × 10⁻⁴, validated) — the null was the trace channel's;
"cannot use direction" is retracted-as-overclaim.]* r ≥ 0.15 is foreclosed *[for
the trace arms; the hint arm resolved it at r ≈ 0.19 — §9.8]*; r ∈ [0.05, 0.13)
stands unresolvable as pre-declared. All 19 recovery events rerun-stable; contamination date-flag uniform
(global LCB-vs-Qwen2.5 scope caveat, no arm-specific unlock pattern); the
repeated-qid recoveries (abc314_a by all four easy arms) are the false-zero mechanism
in the raw. **BEST-SO-FAR: the attractor cannot be aimed on this stack** — BEST
conditioning lands at 0.255 mean frac against its own artifacts' 0.408 (the SINK
replicated); LAST inherits its artifact's badness (0.086); the only coverage anywhere
is ABSTRACT trace-only (2/30, p = 0.25 n.s.); and **BEST+ABSTRACT — the pre-registered
favourite at 55% — got zero: adding the code anchor destroyed the trace arm's
coverage.** The anchor poisons the direction. Phase verdict: sample-based refinement
at 0.5–1.5B is closed with a powered, validated null — conditioning on code degrades,
direction without code adds nothing over the floor, and their combination is worse
than either; open remainders stated plainly: r ∈ [0.05, 0.13) on medium, and scales
above 1.5B. *[H0c scope: "closed" = in-context conditioning channels, on
Qwen2.5-Coder — §9.3.1 channel-scope append; family transfer under audit (H1).]*

**Addendum (2026-07-16, Phase 4 H3) — the cross-scale fork, pre-registered; running
it is a separate sign-off decision.** Basis: the Codex inverse-scaling and "How Many
Tries" ledger entries (§11). **Prediction: above 1.5B the two channel categories move
in opposite directions** — anchor-conditioning channels (BEST / LAST / ANCHOR /
BEST+ABSTRACT) *worsen* with scale (imitation: buggy code is followed by more buggy
code in pretraining data, so matching the artifact's quality register improves as
distribution-matching improves), while direction channels (TRACE / HINT) *improve*
(the "How Many Tries" scale trend). This converts "scales above 1.5B remain open"
from a shrug into a falsifiable fork, and it discriminates the two SINK readings:
**capacity** predicts anchor channels improve with scale (more capacity to exploit
the anchor); **distribution-matching** predicts they degrade. Optional spot check
(not authorized by this pre-registration; costed separately): Qwen2.5-Coder-7B bf16
on L4, one D2c cell + one TRACE cell — combined with H1 this de-confounds scale from
family within one design. [PHASE_4.md] H3.


### 9.8 Completing the decomposition — the hint arm and the near-miss band *(Phase 4 H2, 2026-07-16; [PHASE_4.md] H2)*

The R3 null left an ambiguity the Olausson amendment (§11) named: no tested arm
ever carried *approach-level* direction — traces are near-zero-direction for
structural failures. H2 filled the missing rung with a **hint channel**: 125
two-sentence approach hints, frontier-model-derived from problem statements alone
(LCB has no reference solutions — deviation recorded), leakage-audited (no
identifiers, no numerals, no code tokens; one drafting error caught by the hand
audit), **frozen before the H1 battery reported** (commit `48987b8`).

**The five results, in run order:**

1. **Manipulation gate: HARM (the 70% pass-prediction was wrong).** On 20
   mid-p̂ solvable problems, hints *depress* Qwen's per-sample pass 0.540 → 0.444
   (p ≈ 0.007). Per pre-registration the stratum run was postponed, not
   interpreted.
2. **E-H2 (exploratory, pre-registered): the harm is Qwen's, not the channel's.**
   The same hints, same scaffold, lift DeepSeek-Coder-1.3B 0.306 → 0.394
   (p = 0.019). With H1's D2c inversion this completes a **double dissociation**:
   Qwen degrades under conditioning of either kind (code −0.095, language −0.096)
   on the same problems where DeepSeek benefits from both (+0.107, +0.088).
   **Qwen2.5-Coder-specific conditioning degradation, now shown on two channels.**
   *(Scope sharpened 2026-07-17, J5 Q1: the pathology is a **1.5B** property —
   at 7B the code channel blends and the language harm vanishes, both frozen
   favourites hit; §9.9 J5 addendum, Index row 11.)*
3. **Near-miss band (H2b): direction works inside the boundary — the 55%
   favourite hit.** On 39 problems at x ∈ {1,2}/50, HINT-25 recovers **34 vs
   B1's 24** (p = 0.015); TRACE-25 nulls (23, p = 0.77). The apparent
   gate-contradiction resolved by a free decomposition: the manipulation set is
   coverage-saturated (20/20 both arms) — the gate metric (per-sample quality)
   was mis-specified against our own D2b law; on Qwen, hint-conditioning trades
   per-sample quality for **directed coverage**.
4. **Amended stratum run (new pre-registration, gate misfire documented):
   branch (a), against the 45% on-floor favourite — approach-level direction
   CROSSES the boundary.** On the 68-problem pass@50 = 0 stratum: **B1-50
   recovered 2 (the W0c floor prediction, 2.01, hit exactly a second time);
   HINT-50 recovered 13** (11 hint-only / 0 b1-only, p = 4.9 × 10⁻⁴; r ≈ 0.19,
   above the declared 0.15 power line). Validation: 13/13 rerun-stable; 11/13
   structurally novel vs the entire failure pool (≥ 0.17 normalized-AST);
   recoveries skew to timeout-class failures (31% vs 13% base — hints fix
   efficiency errors); and the mechanism is the one the frozen R3 spec demanded —
   **HINT generated off the coverage-vs-PULL curve** (AST-PULL 0.427, beyond
   B1's 0.375, at 6.5× floor coverage): relocated mass, not spread.
5. **The trace channel works nowhere:** floor on the stratum (R3), null inside
   the boundary (H2b) — while the hint channel works both sides. The direction
   variable is **feedback content**, not use-capacity.

**What this reverses, and what it doesn't.** The Phase-3b closing line — "the
constraint is not the feedback channel but the model's ability to use it" — is
**retracted-as-overclaim** (markers in §9.3.1/§9.7): at 1.5B, Qwen *uses*
approach-level direction to reach a fifth of a stratum it provably cannot
i.i.d.-sample. Olausson's bottleneck localization ("the model cannot produce
accurate feedback") is confirmed one rung deeper and 70× smaller: what a 1.5B
model cannot do is *produce* hint-grade direction from traces; given the
direction, it executes. What does **not** reverse: the elimination argument's
structure (undirected ≤ i.i.d.; repulsion inexpressible; direction the sole
surviving channel — now with its existence proof), the register null, and every
Qwen scope line from H1. The hint channel is oracle-fed by construction —
deployable self-refinement still requires something that *generates* the hint,
and R3/BSF showed this model cannot generate it for itself.

**Addendum (2026-07-16, Phase 5 J3 — the production gap, measured; [PHASE_5.md]
J3).** "The model cannot produce hint-grade direction for itself" was inferred
from MODELABS/BSF; the direct arm now exists. Qwen2.5-Coder-1.5B-Instruct wrote
its own approach hints from the statements alone (frozen prompt), and the base
model ran SELFHINT-50 on the same 68-problem stratum: **3 recoveries — on the
floor** (B1 2, p = 0.5) — against HINT's 13 (production gap p = 0.0032). Blind
anchored grading with a registered correctness dimension explains it completely:
**0 of 68 self-hints were production-adequate** (COMPLETE ∧ CORRECT; 0 COMPLETE,
25 outright WRONG; cap-truncated tutorial preambles instead of two-sentence
strategies), where the same instrument-class graded the oracle set 123/125
COMPLETE. Both rungs of the Olausson decomposition are now measured at 1.5B:
**uses complete-strategy direction (13/68); cannot produce it (0/68)**. The
deployable shape at this scale is a cascade — a stronger producer feeding a
small executor.

**Addendum (2026-07-16, Phase 5 J2 — what grade of direction crossed the
boundary).** All 125 frozen hints were graded by blind fresh-instance graders
under a frozen three-level rubric (COMPLETE / PARTIAL / NUDGE), twice — a bare
instrument, then an anchored one registered before its regrade. Both hit the
pre-declared ceiling guard: **123–125/125 grade COMPLETE** ("the hints read like
reference-solution summaries" — the anchored grader, after item-by-item
stress-testing). Verdict: **true ceiling — the drafter wrote complete strategies
essentially everywhere, so the direction-richness dose-response is unmeasurable
on this set.** The sharpening this buys: the 13/68 result is a
**complete-strategy-grade** direction result; whether weaker direction (nudges,
partial observations) crosses the boundary is open and would need a
deliberately-varied hint set — named as a future instrument, not chartered.
Two hint defects the anchored grader surfaced (abc321_c zero-subset rank hazard;
abc334_c DP left uninstantiated) stand recorded in the frozen set.
[artifacts/h5_hint_grades.json; PHASE_5.md J2.]

### 9.9 Where direction comes from — the production question, answered on two families *(Phase 5 J3/J4, 2026-07-16/17; [PHASE_5.md])*

Phase 4 left one claim inferred rather than measured ("the model cannot produce
hint-grade direction for itself") and one worry unresolved (the Qwen conditioning
pathology retroactively contaminates every conditioning-based null — was the
trace null Qwen's toxicity rather than the trace's emptiness?). Phase 5 measured
both, on both families.

**J3 — Qwen self-hint arm.** Qwen-1.5B-Instruct wrote its own approach hints
(frozen prompt); the base ran SELFHINT-50 on the 68-problem stratum: **3
recoveries, on the floor** (B1 2, p = 0.5), vs oracle-HINT's 13 (gap p = 0.0032).
Blind anchored grading with a correctness dimension: **0/68 self-hints
production-adequate** (0 COMPLETE; 25 WRONG; cap-truncated tutorial preambles).
The same instrument-class graded the oracle set 123/125 COMPLETE.

**J4 — the DeepSeek four-arm contrast** (its own screen → floor → power → arms,
each step pre-registered). DeepSeek's medium tail is nearly flat (pass@50 0.026;
stratum 76/78; the committed floor prediction was **0**, band 0–1 — **B1
observed 1: the instrument's third consecutive out-of-sample hit**). Arms:
**B1 1 / TRACE 2 / HINT 9 / SELFHINT 3.** HINT vs B1 p = 0.0039; TRACE on the
floor (p = 0.5); SELFHINT floor-consistent with **1/76 production-adequate**
self-hints (34 WRONG). All 15 recoveries rerun-stable; every HINT recovery
structurally novel vs its entire failure pool (≥ 0.162 normalized-AST);
timeout-class failures enriched among recoveries again (33% vs 12% base).

**What two families settle (the registered 40% favourite fork):**

1. **The trace null is a content fact, not a Qwen fact.** Traces sit on the
   floor on the family conditioning *helps* — the pathology never explains it.
   "Verbatim execution feedback carries no usable direction for structural
   failures" now holds cross-family, and the retro-contamination worry over
   R3/BSF is resolved in the record's favor.
2. **The hint result generalizes:** complete-strategy direction crosses the
   competence boundary on both families (r ≈ 0.19 Qwen, r ≈ 0.12 DeepSeek).
3. **The production failure generalizes:** 0/68 and 1/76 production-adequate
   self-hints; self-hint arms on the floor both times. At 1.3–1.5B, models
   **execute** direction they **cannot manufacture** — Olausson's localization,
   measured at both rungs on two families. The deployable shape at this scale is
   the **cascade** (a stronger producer feeding a small executor); the open
   question above it is the **minimum scale of self-production** (PlanSearch
   ledger frame; the J5 7B cell is the first data point between our floor and
   the frontier ceiling, awaiting sign-off).

**J5 addendum (2026-07-17) — the 7B fork *(CLOSED same day; full accounting in
[PHASE_5.md] J5)*.** Both questions signed off, run, and closed on
Qwen2.5-Coder-7B (base; 7B-Instruct writes the Q2 self-hints).

- **Q1 — the pathology is a small-Qwen property (both frozen favourites
  hit).** On the same 44 artifacts, 7B conditioned frac 0.609 sits *between*
  copy-null 0.494 and its own i.i.d. 0.659 — decisively above copying
  (p ≈ 1.0 against below-copy), marginally below own-iid (p = 0.075): the
  **blend** the other families show, not the below-both-nulls sink. The
  language-channel harm vanishes (E0 0.842 → HINT 0.824, Δ −0.018, p = 0.70;
  near-saturation caveat pre-declared and reported). The §9.8 double
  dissociation's Qwen side is therefore a **Qwen2.5-Coder-1.5B** phenomenon:
  at 7B the family rejoins DeepSeek/StarCoder2. Index row 11 rescoped;
  [artifacts/h5_7b_pathology.json].
- **Q2 — the switch-on measurement; a pre-registered gate fired en route.**
  The medium screen hit its committed band (stratum 46/78, the 55% favourite;
  pass@50 0.410). But the W0c fit found **no false-zero floor at 7B-medium**:
  π₀ = 0, every stratum problem reachable, eleven 1/50 near-misses,
  **E[fresh B1-50 recoveries] = 5.11** — committed before any arm as the
  floor instrument's **fourth out-of-sample test** (point 5, band [2, 9]; the
  first non-degenerate test of its Beta-binomial component). The floor-aware
  exact-McNemar envelope then gave power 0.223 (marginal) / 0.695 (uplift) at
  r = 0.20 — under the frozen ≥ 0.70 rule — so **arms did not launch on the
  medium stratum alone**. The pre-registered extension (LCB-hard screen,
  identical selection rule, committed odds, a fifth floor test before arms,
  pooled power gate governed by the stricter marginal reading) is in flight.
  Two things are already scientific content regardless of the arms outcome:
  the 7B "hard problem" set at medium difficulty is a **live tail** (the
  substrate that made the 1.5B switch-on question clean does not exist at 7B
  on this difficulty), and the floor instrument now has a committed prediction
  in genuinely new territory. [artifacts/h5_7b_medium_screen.json],
  [artifacts/h5_7b_floor_fit.json], [scripts/j5_floor_fit.py].
- **Q2 closed — branch (a), the 40% favourite: self-production does not switch
  on by 7B.** The hard extension restored the floor substrate (61 hard stdin
  problems; stratum 55/61; **π₀ = 0.76** — the point mass returns with
  difficulty; fifth floor test committed: E = 2.09, band [0, 4]); the pooled
  gate passed (0.816 at r = 0.20). Arms on the pooled 101: **B1 2 / SELFHINT
  5, p = 0.125** — floor-equivalent; blind anchored grades: **5/101 (5%)
  production-adequate** (0% at Qwen-1.5B, 1.3% at DeepSeek — production climbs
  with scale but stays an order of magnitude under the bar), and recoveries do
  not concentrate on adequate hints. **The cascade remains the only deployable
  shape through 7B; the switch-on bracket moves to 7B–frontier.**
  [artifacts/h5_7b_hard_screen.json], [artifacts/h5_7b_hard_floor_fit.json],
  [artifacts/h5_7b_switchon.json], [artifacts/h5_7b_selfhint_grades.json].
- **The falsified floor test paid for itself.** The medium 4th test failed
  (B1 1 vs band [2, 9]) and the mandated diagnosis found a harness confound
  invisible to every previous arm: **same-seed vLLM regeneration reproduces
  ≈ 50% of a pool byte-for-byte**, suppressing "fresh" B1 arms relative to
  differently-prompted arms (§8 seed-policy caveat, with the J4 control at
  45%). The correction (corrected E[B1] 3.02/1.31; neutral-draw E[SELFHINT]
  7.20 vs observed 5) simultaneously de-falsifies the model's *component*
  (the miss was operational) and dissolves the apparent SELFHINT trend —
  one committed prediction caught a record-wide bias and prevented a false
  positive in the same stroke. Prior near-zero-floor results are unaffected
  (the bias works against the hint results, not for them). Standing rule:
  fresh-draw arms use a distinct seed henceforth.

**P1 addendum (2026-07-18) — where the small-Qwen pathology comes from
([PHASE_6.md] P1).** The origin battery ran the two cheap conditioning cells on a
five-point size curve (Qwen-Coder 0.5/1.5/3/7B + general-1.5B, all Modal L4/bf16 —
same stack as the reference, so no re-baseline). Three results, each a scoped fact:

- **Recipe = CODER-STAGE, not base-recipe/tie (the clean control).** general-1.5B —
  same architecture, tie, and scale as Coder-1.5B but *general* Qwen2.5
  pretraining — is **not pathological**: conditioning *helps* it on code
  (+0.070 vs iid) and language (+0.160). The pathology is a property of the **Coder
  continued-pretraining diet** (synthetic-heavy code — "the synthetic tax"), not
  the base recipe or architecture. (H-tie, demoted at P0 by StarCoder2, is now
  doubly refuted: 0.5B and general-1.5B are tied yet clean.)
- **The code sink is a competence WINDOW, not a slope or step.** Below-both-nulls
  at **1.5B and 3B only**; at 0.5B conditioning helps (i.i.d. frac 0.211 sits below
  the 0.494 artifact — too weak to sink below its own floor), at 7B it blends up
  (own-iid 0.659, strong enough to imitate upward). Harm-vs-iid is *deepest at 3B*
  (−0.150), still tied and Coder. The sink lives where the model's i.i.d. quality
  straddles the artifact's.
- **MIXED across channels — the disagreement is the finding.** The code sink
  persists to **3B**, but the language harm is **1.5B-only** (3B hint-conditioning
  already helps, +0.076). The two conditioning channels have different competence
  boundaries; recorded MIXED, not harmonized. Free rider: copy-fidelity does *not*
  track the sink (0.5B copies hardest at 0.818 yet does not sink) — degradation at
  matched fidelity, not a copy effect.

Branch accounting: code **NON-MONOTONE** (15% underdog) + recipe **CODER-STAGE**
(55% favourite) + **MIXED** channels. Index rows 8/11 carry the measured origin
line. [artifacts/h6_size_curve.json, h6_pathology_origin_*.json].

---

## 11. References *(external work this record engages; formal citations to be fitted at paper stage)*

- **Tsui et al. (2025), "Self-Correction Bench" (NeurIPS 2025).** The **Self-Correction
  Blind Spot**: LLMs fail to correct errors in their own output while fixing identical
  errors from external sources (~64.5% failure across 14 models); a minimal "Wait" prompt
  reduces it ~89%. *Our relation:* orthogonal, mechanism-level (§9.3.1) — Tsui's axis is
  *detection*/provenance, ours is *escape*/distributional-conditioning; D2a shows provenance
  near-inert in our setup (ΔPULL ≤ 0.028), so the blind spot does not bite where the failure
  is announced.
- **Olausson et al. (2024), "Is Self-Repair a Silver Bullet for Code Generation?" (ICLR
  2024).** Compute-matched, self-repair is often ≤ i.i.d. sampling, especially at small
  budgets; the bottleneck is the model's inability to produce accurate feedback about *why*
  code is wrong. *Our relation:* the **methodological anchor** and the closest ally — our
  escape-distance elimination argument (§9.3.1) is a mechanism-level derivation of their
  empirical result, and their "feedback is the bottleneck" is our "direction requires rich
  feedback."
- **Chen et al., "Teaching Large Language Models to Self-Debug" (Self-Debug).** GPT-4
  improves MBPP ~+3.6% and TransCoder/Spider substantially *without* unit-test execution —
  the strongest published support for "the candidate itself helps." *Our relation:* the
  reconciliation is baseline + regime — Self-Debug measures against **greedy** (not compute-
  matched best-of-n), and its largest gains are on **near-correct-by-construction** tasks
  (code translation, text-to-SQL) where the candidate is scaffolding and errors are *local*
  — our "point the attractor at a near-success" regime. Not a contradiction; a different
  point on the coverage/locality surface.
- **"How Many Tries Does It Take?" (2026).** Self-repair reported universally effective
  across 7 models on HumanEval + MBPP-Sanitized — *our exact benchmarks*; also reports name
  errors repair easily while **assertion errors are hardest**, and gains grow with scale
  (≤ +5.5pp at 70B). *Our relation:* the **direct challenge** to address head-on, and the
  reconciliation is inside it — our failure mix is ~50% assertion-class (structural), 2%
  syntax, and we run 1.5B; they average over easy (local) error types at large scale. The
  local-vs-structural error axis is the reconciling variable and a Phase-3 stratification
  target.
- **Kamoi et al. (2024), TACL — survey of LLM self-correction.** Concludes no prior work
  demonstrates successful *intrinsic* self-correction (from the model's own feedback alone)
  on reasoning. *Our relation:* consistent with our B2 result (intrinsic self-refinement
  buys nothing); we extend it to code with execution ground truth and give the *mechanism*
  (undirected escape → resampling).
- **Cross-Context Review line (2026)** and an **information-theoretic self-correction
  preprint (2026):** fresh-context / external-channel framings escape the correlated-error-
  mode problem. *Our relation:* corroborating context for "directed external signal" over
  "self-review"; cite as convergent, not foundational.
- **Chen et al. (2021), Codex — alignment appendix; and the buggy-code-completion line
  (arXiv 2306.03438).** Subtly buggy prompts induce more bugs than clean or no prompts,
  though the model is capable of better; the gap *grows with scale* (an inverse-scaling
  candidate, mechanism: imitation/distribution-matching). *Our relation:* the precedent
  D2c's SINK replicates and extends (compute-matched, execution-quantified, below-both-nulls
  — ledger below); the inverse-scaling reading is the basis of H3's cross-scale fork.
- **Spurious Rewards (arXiv 2506.10947) + contamination follow-up (2507.10532).** Random-
  reward RLVR gains on Qwen2.5-Math driven by Qwen-specific priors; failed on Llama3/OLMo2;
  follow-up implicates contamination. *Our relation:* the cautionary precedent that
  motivates Phase 4's cross-family battery (H1) — our record is single-family until H1
  reports, and is scoped accordingly (ledger below).
- **AlphaCode (Li et al., 2022).** Deep pass@k tails on competitive programming at scale on
  organically-trained models. *Our relation:* tension with F1's shallow-tail reading if
  universal; basis for H1's hypothesis that BCB flatness may be Qwen-pipeline-scoped
  (ledger below).
- **Self-planning code generation (Jiang et al.).** Plan-then-implement with
  code-davinci-002; includes a ground-truth-planning arm (plans supplied, implementation
  only). *Our relation:* the structural precedent for the hint channel at ~100× our
  scale; we compute-match and extend downward (ledger below).
- **PlanSearch (arXiv 2409.03733).** Search over natural-language plans lifts pass@200 on
  LiveCodeBench for frontier models; gains track idea-space diversity. *Our relation:*
  the deployable ceiling of the direction channel; frames the record's open question as
  the minimum scale of direction self-production (ledger below).

*Note on independence (to state honestly at paper stage):* the anchoring/escape line was
reached from our own DIAG-8 spin-off before we surveyed Tsui/Olausson; we position as
**convergent corroboration from an independent experimental path**, not priority, and cite
prominently.

### Reconciliation ledger *(appended 2026-07-15; one entry per reference per design decision it influenced)*

Rule ([PHASE_3B.md] charter): no external conclusion is imported as a general truth or a
design constant. Each entry states (a) their setup specifics, (b) the delta to ours,
(c) what their result does and does not license here.

- **Olausson et al. (2024) → R3's four-arm decomposition (W3).** (a) Their feedback
  decomposition uses **human/oracle feedback arms vs self-generated feedback** on
  GPT-3.5/GPT-4, compute-matched, on APPS-class problems; the bottleneck localization
  ("the model cannot produce accurate feedback") comes from the oracle arm beating the
  self arm. (b) Ours is a 1.5B base model, execution-trace feedback (templated, no
  model in the loop) vs model-generated abstraction, on a pass@50 = 0 stratum.
  (c) **Licenses:** the *decomposition logic* — without a feedback-ceiling arm, a
  repair null is ambiguous between "direction doesn't help" and "this model can't
  produce direction"; hence R3's ABSTRACT-trace arm exists. **Does not license:** any
  magnitude expectation — their gap sizes were measured at 100–1000× our scale with
  human-quality feedback; nothing transfers numerically. *Outcome (2026-07-16): the
  decomposition paid — both channels nulled together (TRACE 1, MODELABS 3, floor 2),
  which converts an ambiguous null into a specific one: the bottleneck at 1.5B is not
  feedback production (their result) but feedback* use *(§9.7).*
  **[AMENDED 2026-07-16, Phase 4 H0b — the ledger applied to our own entry.]** The
  outcome clause above imports Olausson's localization **one rung further than our
  arms support**. Their bottleneck call came from a **human conceptual-explanation
  arm** beating self-generated feedback; our ceiling arm was a **verbatim execution
  trace**, which sits *below* their oracle rung and carries near-zero direction for a
  pass@50 = 0 structural failure (output 17 ≠ expected 42 does not say which
  algorithmic idea is wrong). MODELABS compresses the trace and cannot add direction
  the trace lacks, so TRACE and MODELABS nulling together does **not** localize the
  bottleneck at "use." Honest current statement: the decomposition separated feedback
  *production* from the *trace channel*; it did not reach "use." The R3 null is
  ambiguous between "1.5B cannot use direction" and "no arm ever contained
  direction" until an approach-level hint arm (H2a, [PHASE_4.md]) fills the missing
  rung. The "cannot use direction" sentences in §9.3.1/§9.7 are scoped accordingly
  (H0c). *Second outcome (2026-07-16, §9.8): the rung ran — hint-grade direction
  recovers 13/68 against the calibrated floor of 2 (p = 4.9 × 10⁻⁴). Their
  localization is confirmed one rung deeper and ~70× smaller: feedback*
  production*, not use, is the bottleneck; the amendment above was the correct
  call, made before the data.*
- **Self-Debug (Chen et al.) → ABSTRACT-trace arm framing (W3).** (a) Gains measured
  against **greedy** (not compute-matched best-of-n), largest on
  near-correct-by-construction tasks (TransCoder, Spider) where errors are local; the
  "explanation" channel is model-generated. (b) Our control is compute-matched i.i.d.
  (B1-50), our stratum is structural failure (0/50), our trace channel is verbatim
  execution output. (c) **Licenses:** trace-style feedback as the *strongest known
  candidate* for the direction channel — worth a dedicated arm. **Does not license:**
  any expectation that repair beats resampling here — their baseline never asked that
  question, and their regime (near-correct) is the one D2c/E6 tests separately.
  *Outcome (2026-07-16): trace feedback was the only channel to show any coverage
  anywhere (BSF ABSTRACT 2/30 n.s.; R3-easy TRACE 3/19 ≈ floor) — the "strongest
  known candidate" ranking held, and it still never beat resampling (§9.7).*
- **"How Many Tries" (2026) → R3 recovery stratification (W3/W4).** (a) Self-repair
  universally effective across 7 models on HumanEval/MBPP-Sanitized — our exact
  benchmarks — with gains growing with scale (≤ +5.5pp at 70B); **name errors repair
  easily, assertion errors are hardest**. (b) Our failure mix is ~50% assertion-class
  at 1.5B, and R3's stratum is by construction the hardest tail. (c) **Licenses:** a
  pre-committed *check*: their error-type axis predicts which stratum problems are
  recoverable — R3 recoveries (if any) should skew toward non-assertion error classes;
  we stratify recoveries by error type and test that prediction. **Does not license:**
  the "universally effective" headline — averaged over easy error types at scales
  where the mechanism has capacity we don't have. *Outcome (2026-07-16): held
  directionally at uninterpretably small n — medium recovery events under-represent
  wrong_answer artifacts (50% vs 76% stratum base) and over-represent runtime/timeout
  (50% vs 24%); their scale trend (≤ +5.5pp at 70B) is now the main reason the R3
  null is scoped to ≤ 1.5B rather than read as universal ([PHASE_3B.md] W4).*
  *Second outcome (2026-07-16, §9.8): their error-type axis held with real n —
  the hint arm's 13 stratum recoveries over-represent timeout-class failures
  (31% vs 13% base): approach-level hints preferentially fix efficiency errors,
  the class their taxonomy predicts responds to algorithmic guidance.*
- **Tsui et al. (2025) → E7 prompt design (W1) — formalizing the existing
  reconciliation.** (a) Detection-axis result: models fail to notice their own errors;
  "Wait"-style prompts recover ~89% of the gap; instruct models, natural-language
  reasoning tasks. (b) Our failures are announced (detection removed); D2a measured
  provenance ΔPULL ≤ 0.028 — inert. (c) **Licenses:** treating E7's avoidance framing
  as a *verb/instruction* intervention (the live 3–4× lever per D2a), not an
  attribution one; predicts "someone else's failed attempt" framing adds nothing to
  E7. **Does not license:** any expectation about escape magnitude — Tsui never
  measures distance-to-artifact. *Outcome (2026-07-16): the verb-lever framing was
  the right call and still nearly inert — the strongest avoidance instruction moved
  PULL only +0.02/+0.05 over "improve it" ([PHASE_3B.md] W1); token gravity dominates
  instruction at this scale.*

*The following entries added 2026-07-16 (Phase 4 H0b — [PHASE_4.md]).*

- **Chen et al. (2021), "Evaluating Large Language Models Trained on Code" (Codex),
  alignment appendix → SINK positioning (H0c).** (a) They prompted Codex with subtly
  buggy code and observed higher bug frequency in completions than with clean or no
  prompts, framing it as the model *matching prompt quality while capable of better*
  — a misalignment-by-imitation observation, qualitative, at Codex scale. Related
  supporting line: buggy-code-completion (arXiv 2306.03438) — potential-bug prefixes
  systematically depress pass rates across code LLMs. (b) Ours is compute-matched
  against i.i.d., execution-quantified (frac_tests), on partial-credit artifacts, at
  1.5B. (c) **Licenses:** repositioning D2c's SINK as a **replication-plus-extension
  of a known phenomenon** — the extension being that the conditioned blend lands
  *below both* the artifact's own frac and the i.i.d. baseline, quantified with a
  copy-null. **Does not license:** treating SINK as novel, or importing their
  "capable of better" interpretation — that is exactly the capacity-vs-
  distribution-matching ambiguity H3 pre-registers (§9.7 addendum). *Outcome
  (2026-07-16, H1): the precedent predicted the wrong thing for the wrong family —
  quality-matching explains the cross-family **blend** (both audit families climb
  toward the artifact's quality), but not Qwen's below-both-nulls sink; the SINK
  repositioning is amended in §9.7 — Qwen-specific degradation, not replication.*
- **The inverse-scaling reading of Codex's buggy-prompt result → H3's cross-scale
  pre-registration.** (a) The buggy-vs-clean completion-quality gap *grows with model
  size*; proposed mechanism is imitation — in pretraining data, buggy code is
  followed by more buggy code, so predicting bugs is better distribution-matching.
  (b) Directly applicable to our anchor channels (BEST/LAST/ANCHOR/BEST+ABSTRACT):
  every one conditions generation on a code artifact of known (poor) quality.
  (c) **Licenses:** a pre-registered *directional* prediction — anchor-conditioning
  channels **worsen** with scale while direction channels (TRACE/HINT) **improve**
  (per "How Many Tries"' scale trend); the two open-scale axes point in opposite
  directions, which is the discriminating test between SINK-as-capacity and
  SINK-as-distribution-matching. **Does not license:** any magnitude, or running the
  test without a sign-off (H3 is pre-registration-only in Phase 4). *Outcome note
  (2026-07-16, H1): partially pre-empted — the cross-family D2c cell already shows
  distribution-matching failing to explain Qwen's sink (it predicts no-change for
  Qwen, which sank; it predicts the blend elsewhere, which held). The H3 fork
  stands for the scale axis; its SINK-discrimination leg now tests a narrower
  question: whether Qwen's anomalous sink deepens or dissolves with scale.*
- **Spurious Rewards (arXiv 2506.10947) + contamination follow-up (2507.10532) →
  H1's existence.** (a) RLVR on Qwen2.5-Math with *random* rewards nearly matched
  ground-truth rewards — driven by Qwen-specific pretraining priors (code-reasoning
  strategies the reward merely surfaces); the same signals **failed outright on
  Llama3 and OLMo2**; the authors explicitly recommend validating on diverse
  families; the follow-up attributes much of Qwen's surge to
  contamination/memorization. An entire sub-literature's conclusions turned out to
  be properties of one model family. (b) Our entire record — the attractor
  constants, the suppressor decomposition, the shallow BCB tail, the feasible
  region — is measured on exactly one family (Qwen2.5-Coder), with scale and family
  confounded in every claim. (c) **Licenses:** treating family-transfer as a
  **mandatory audit** (H1's cross-family battery), not a limitation paragraph; and
  H0c's interim rescoping of every "at this scale" to "on Qwen2.5-Coder at this
  scale" until H1 reports. **Does not license:** assuming our findings *fail* to
  transfer — that is what H1 measures, with per-finding branches and odds. *Outcome
  (2026-07-16, H1): the precaution was warranted in full — two of four findings
  (F1's shallow tail, D2c's SINK) were Qwen properties, one inverted outright; the
  feasible region and the anchoring law's form generalize. The record avoided
  exactly the Spurious-Rewards failure it feared, by measuring instead of assuming.*
- **AlphaCode (Li et al., 2022) → tail-structure scoping (H1 cell (i)).** (a) Deep
  pass@k tails on competitive programming with large-scale sampling: solve rates
  climb steadily with k (to k = 10⁵–10⁶) and with scale, on organically-trained
  models. (b) Consistent with our LCB-easy feasible region (headroom exists, k=50);
  in tension with BCB's flatness (F1) *if* flatness is read as universal.
  (c) **Licenses:** the hypothesis H1 cell (i) tests — that BCB's shallow tail may
  be partly a property of Qwen2.5-Coder's synthetic-heavy training pipeline
  (peaked solution distributions), not of the task family; hence the
  organic-corpus families (StarCoder2 on The Stack; DeepSeek-Coder) as the
  comparison points. **Does not license:** expecting AlphaCode-scale tails at 1.3–3B,
  or reading a Qwen-scoped F1 as a training-data *mechanism* claim — H1 scopes
  findings; it does not isolate the synthetic-data variable (confounds recorded in
  the H1 pre-registration). *Outcome (2026-07-16, H1): the tension resolved in
  AlphaCode's favor — both organic-corpus families show deep reachable tails on
  BCB (headroom +0.177/+0.252) and LCB-easy; F1 retracted-as-Qwen-scoped (§7.3).
  The synthetic-data *mechanism* remains unisolated, as pre-declared.*

*The following entries added 2026-07-16 (Phase 5 J1 — [PHASE_5.md]; they inform
the direction tranche's designs before any of it runs).*

- **Self-planning code generation (Jiang et al.) → the hint channel's precedent
  (J3/J4 design).** (a) Their setup: code-davinci-002 (175B-class),
  HumanEval/MBPP, plan-then-implement prompting; baselines are Direct and
  Code-CoT — **not compute-matched sampling**; critically, they ran a
  **Ground-truth Planning arm** — supplying the model with plans and running
  implementation only — which is structurally our HINT arm at ~100× scale.
  (b) Our delta: 1.5B, compute-matched B1 controls, a pass@50 = 0 stratum,
  leakage-audited two-sentence hints, execution-quantified. (c) **Licenses:**
  the plan/implement decomposition as established territory we extend *downward*
  and *compute-match* — §9.8's result is their ground-truth-planning arm asked
  the question they never asked (does it beat resampling?). **Does not
  license:** any expectation that *self*-planning works at 1.5B — their planner
  was the same 175B-class model; J3 asks the compute-matched self-planning
  question at 1/100th scale. *Outcome (2026-07-16/17, §9.9): asked and answered
  on two families — supplied plans work (their ground-truth-planning arm,
  compute-matched, beats resampling decisively at 1.3–1.5B), self-planning does
  not (production-adequacy 0/68 and 1/76). Their decomposition survives scaling
  down; their self-planning result does not.*
- **PlanSearch (arXiv 2409.03733) → the deployable ceiling of the direction
  channel (J3/J5 framing).** (a) Searching over natural-language plans before
  implementing yields large pass@200 gains on LiveCodeBench with frontier
  models; the driver is **diversity in idea space**, and search gains are
  predictable from that diversity. (b) Ours is the opposite corner: direction
  *supplied*, tiny model, provably-unreachable stratum. (c) **Licenses:**
  framing the record's open question as **minimum scale of direction
  self-production** — frontier models manufacture their own direction by
  plan-space search; our 1.5B provably executes supplied direction (§9.8) and
  provably fails to produce it (R3/BSF — J3 measures this directly). Somewhere
  between is a switch-on point; J5's 7B cell would be the first data point
  between the ends. **Does not license:** magnitudes, or assuming the switch-on
  is smooth (idea-space diversity may be emergent, not gradual). *Outcome
  (2026-07-17, §9.9): the floor end of the frame is now measured twice —
  self-production is absent at 1.3B and 1.5B (production-adequacy ≈ 0 with
  instruct-variant producers); the switch-on lies above; J5's 7B cell remains
  the next data point, sign-off gated.*
- **"How Many Tries" + Codex entries, amended for the re-scoped 7B fork
  (J5).** The original H3 fork (anchor channels worsen with scale, direction
  channels improve) was framed to discriminate SINK-as-capacity from
  SINK-as-distribution-matching; H1's inversion already broke that tie
  (distribution-matching fails to explain Qwen's sink). *Amendment: the
  7B-relevant questions are now (i) does the **Qwen conditioning pathology
  persist at 7B** (family property vs small-Qwen property), and (ii) does
  **direction self-production switch on by 7B** (the PlanSearch-frame minimum-
  scale question). The HMT scale trend and Codex inverse-scaling readings remain
  the priors for (i); neither speaks to (ii).*

*Appendix pointers. Architecture [ARCHITECTURE.md]; decision log **D1–D16**
[DECISIONS.md] (D11 precision, D14 statistical reproducibility, D15 retracted, D16 =
Finding F1); phase/gate log [PHASES.md]; metric estimators [METRICS.md].
Plans: [PHASE_M.md] (stack rebuild), [PHASE_3.md] (benchmark screen + 3b/3c design),
[PHASE_3R.md] (the H1/F2 audits + D-measure, Addenda I–III), [DIAGNOSTICS.md]
(DIAG-1..11). Verdict artifacts: Phases 0–2
[artifacts/h1_result.json, h1_v2b_result.json, h2_result.json, h2_b2_result.json];
diagnostics [artifacts/diag{1..11}_*.json]; Phase M
[artifacts/m3_rebaseline.json, m4_verifier_revalidation.json, m5_relock.json];
Phase 3a [artifacts/phase3a_screen_{complete,c05b,confirm,confirm15,confirmhard,
lcb_easy,lcb_med}.json, phase3a_characterization.json]; Phase 3R
[artifacts/r1b2b_stratified_auroc.json, r1b2c_length_bias.json,
dmeasure_conditioning.json (incl. per_sample_D2b), dmeasure_d2a_verb_provenance.json,
phase3a_screen_r2_base_T10.json, phase3a_screen_r2_base_T12.json; intact pools awaiting
exec-only: runs/modal/bcb_cand_r2_{base,instruct}_T08.json; crash-recovery record in
PHASE_3R.md "CRASH RECOVERY (2026-07-14)"; pending rerun: r1b2d retrain, r2 instruct
T=1.0/1.2 + LCB arm, dmeasure_d2c_partial_credit.json — *all listed reruns landed
2026-07-15/16: [artifacts/r1b2d_verifier_retrain.json,
phase3a_screen_r2_instruct_T{10,12}.json, phase3a_screen_lcb_r2_*.json]*];
**Phase 3R resolutions** [artifacts/r1b2d_verifier_retrain.json (H1 kill),
dmeasure_subset_control.json (E5/E1 closure)]; **Phase 3B** ([PHASE_3B.md] — charter,
W0–W3 pre-registrations, W4 verdicts) [artifacts/w0a_e0_anchor.json,
w0b_copy_null.json, w0c_stratum_falsezero.json, dmeasure_e7.json (W1 branch (a)),
phase3a_screen_lcb_r2_base_medium_T{08,12}.json (W2), r3_smoke.json,
dmeasure_d2c_partial_credit.json (SINK), r3_conditional_reachability.json (NULL +
recovery validation), bestsofar.json]; **Phase 4** ([PHASE_4.md] — charter,
H0a/H1/H2 pre-registrations + results, E-H2, the amended H2a part 2, H3 frozen
fork) [artifacts/h0a_ast_distance.json, h0a_d2a_ast_followup.json,
h1_smoke_{deepseek,starcoder2}.json, h1_cross_family.json, h2_hints_frozen.json,
h2_manip_check.json, h2_manip_check_deepseek.json, h2b_near_miss.json,
h2a_hint_arm.json, h2a_rerun_stability.json, h2a_validation_struct.json];
**Phase 5** ([PHASE_5.md] — J0 reframe, J1–J5)
[artifacts/h5_hint_grades.json, h5_selfhint_qwen.json, h5_selfhint_grades.json,
h5_deepseek_medium_screen.json, h5_deepseek_floor_fit.json,
h5_hints_extension.json, h5_deepseek_fourarm.json, h5_deepseek_rerun.json,
h5_deepseek_selfhint_grades.json, h5_deepseek_validation_struct.json].
Scripts: [scripts/modal_rgr.py] (T4 verifier/retrain), [scripts/modal_phasem.py]
(L4 gates + D-measure/D2a/E7), [scripts/modal_phase3a.py] (BigCodeBench screen + R2),
[scripts/modal_lcb.py] (LiveCodeBench + Phase-3b W4: p3b_* entrypoints),
[scripts/dmeasure_analysis.py] (D2b), [scripts/r1b2_analysis.py] (R1b.2a/b/c),
[scripts/w0_recomputes.py] (W0a/b/c), [scripts/dmeasure_subset_control.py] (Addendum
IV), [scripts/h0a_ast_distance.py] + [scripts/h0a_d2a_followup.py] (H0a),
[scripts/modal_h1.py] (Phase 4 runner: H1 battery + H2 arms),
[scripts/h2a_struct_validation.py] (H2a validation). Difficulty proxies
[artifacts/phase0_difficulty_proxy.csv].*

---

**Record-integrity note [2026-07-17].** The repository was published to
GitHub (github.com/majax7714/Ajax-composite) and its git history rewritten
once, on this date, to strip AI co-author trailers from commit messages
(`filter-branch --msg-filter`, force-push). No tracked file content, commit
subjects, author identities, or dates changed — only message trailer lines.
Commit hashes cited in this journal and the phase documents before this date
refer to the pre-rewrite history; per append-never-revise the inline citations
stand, and this mapping resolves them in the published history:

| pre-rewrite | published | subject |
|---|---|---|
| 7e4ea2f | d07d5be | R1b.2d: preemption-proof checkpoint/resume plumbing |
| d6cbf37 | b8f0989 | Addendum II SS1: fix the judge — run ALL tests |
| eec132e | 1398eb5 | R2 executor: guard sandbox output read |
| 86c48ea | 3a3d217 | Phase 1: batched sampling, label pipeline, verifier training |
| 00ddc84 | 510223d | Phase M — M4 DONE (V retrain required) + fix M3 logprob bug |
| cc716f5 | e743069 | Plumbing: run LCB images hub-offline |
| 48987b8 | 3e37d16 | H2 hint set frozen (125 hints, leakage-screened) |
| 81324e2 | 41cb119 | J1: ledger entries — Self-planning, PlanSearch, HMT/Codex |

(`2e1fd397` in PHASE_K.md is a HuggingFace model-revision hash, not a repo
commit; it is unaffected.) Hashes cited after this date refer to the published
history directly.
