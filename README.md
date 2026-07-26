# Ajax Composite

A public, append-only record of machine-learning experiments run under one
discipline. The product here is not any single result — most of the headline
claims this project has produced were subsequently killed by their own
pre-registered gates, and the record says so on the page. **The product is the
method**, applied repeatedly until the record itself became the primary
artifact: pre-registered questions, scoped verdicts, calibrated instruments,
and meaning extracted from failures, in chronological truth.

The canonical document is **[docs/WRITEUP-rgr.md](docs/WRITEUP-rgr.md)** — the
journal. Everything else in the repository exists to make the journal's numbers
traceable: phase charters holding the pre-registrations, committed result
artifacts, and the runner scripts that produced them.

## The method

Every experiment in the composite runs under the same rules:

- **Pre-register before running.** Predictions, odds, decision rules, and
  branch interpretations are committed to the phase document *before* the run.
  Falsified predictions stay on the page with their odds; the record keeps a
  running account of where our priors were wrong.
- **Append, never revise.** Documents grow by dated addenda. Retracted claims
  keep their original text under a dated banner. There is no silent editing of
  history — "the only failure mode is silent drift."
- **Gates are binding.** Each claim carries a pre-committed kill criterion.
  A failed gate is a recorded negative, not a tuning target; nothing proceeds
  past a failed gate by tuning until it passes.
- **Instruments are calibrated out-of-sample.** Measurement tools (judges,
  floor models, graders) are frozen before use and tested by committed
  prediction on data they have not seen; instrument failures are recorded the
  same way claim failures are.
- **Verdicts are scoped.** No finding keeps an unscoped "at this scale" or
  "for this model" — cross-family and cross-scale checks assign each claim
  GENERALIZES / single-family-scoped / MIXED.
- **External results enter through a ledger.** Any outside paper used in a
  design decision gets a reconciliation-ledger entry: what it claims, what we
  measured, and how the two square.

The full statement of the method, with the history that forced each rule, is
§10 of the journal — deliberately placed directly after the abstract.

## The arc, in one breath

An execution-grounded verifier seemed to carry load (it didn't — quantization
artifact); a learned cross-step register carried none; the null, fully
localized, reframed the question to "where can refinement pay at all"; the
search for that answer produced an anchoring/escape-distance law, an
elimination argument, a false-zero floor model that predicts to the decimal,
and a cross-family audit that retracted our platform negatives as one family's
pathology — and finally an existence proof that approach-level direction
crosses the competence boundary, moving the open question to where direction
comes from. That pathology's origin was then measured — a
continued-pretraining-diet effect inside a narrow competence window — and
immediately turned on itself: the origin line was found to rest on a confound
(every family had been compared at a different model–artifact quality relation),
so the next phase re-measured the sink with each model matched to its own quality
— confirming the effect is diet-specific (non-Coder families do not sink at match)
while catching that its apparent disappearance at larger scale had been the same
confound all along — and then two more phases pressed on the *why*: a mechanism phase that
characterized the sink and, crucially, caught its own over-reach when the one
provenance-clean data point contradicted the tidy story; and a factorial phase
that drew the 2×2 nobody had drawn and found the effect follows the training diet,
not the provenance of the code being conditioned on — the origin line standing, at
last, on ground no remaining confound can shift, with the deeper question of *why*
that diet does it left honestly open.

Chasing that *why* is what the unattended loop has been doing since, and it has mostly
been a demolition. An audit found the adjudication criterion had silently drifted and
**retracted the effect's largest number**, after which a powered ladder — every rung
measured at its own matched relation — established the shape that survives: present at
1.5B and 3B, **absent at 7B**. Then the mechanism candidates fell one at a time.
Artifact-attention magnitude: excluded, by an instrument that proved it could see by
resolving two larger effects on the same sequences. Attention *concentration*: it tracked
the sink across three model pairs and died to the fourth — the one that holds architecture
fixed — so it is a property of the architecture, not of the pathology. Head ablation:
attempted twice, informative about neither, the second attempt caught by algebra rather
than by data when its adjudication statistic turned out to be **identically zero for any
input**. And most recently the sink was shown to be **framing-invariant** — inert to the
largest lever the record's own anchoring law possesses — which dissociates it from that
law and rules out the cheapest deflationary reading of it. Then the one remaining pointer —
that measured in the escape law's own currency the sink looks like a loss of **coverage**
rather than of per-sample quality — was taken up, and it did not survive being examined: the
sink's own adjudication criterion **does not transfer to that currency** (the copy null
scores coverage zero by construction), and coverage loss turns out to be **universal** across
every family and diet at this scale rather than specific to the pathology. The attempt to
intervene on it with temperature then failed as an instrument, because temperature degrades
the model faster than it releases the anchor. What is left standing is a sharply-scoped,
provenance-controlled, framing-invariant, scale-bounded effect with **no surviving positive
mechanism** — and, from the same free work, one robust and entirely unexplained regularity:
**every model tested, sinking or clean, is pulled 47–90% of the way from its own quality
toward whatever artifact it is shown.**

That regularity then turned on the record itself. If a cell's outcome depends that strongly
on *where* it sits relative to its artifact, then comparing cells at different positions is
confounded — and the family contrast underpinning the diet claim turned out to be exactly
such a comparison, with every clean non-Coder cell sitting at a favourable position and
every powered at-match cell belonging to the Coder side. Audited rather than assumed, **the
diet conclusion survived**, because it rests on a later, position-matched design whose
residual confound runs *against* it. The missing cell was then run: the architecture twin,
at true match, measures **clean** — directionally right, but at a precision the charter had
promised and not checked, so the phase closed by grading its own pre-registration down.

**Current status (2026-07-26):** Phase 19 closed. The architecture twin measures
**clean at true match**, which is directionally what the diet claim predicts — but the cell
was underpowered for the comparison its own charter promised, and the write-up says so and
grades the charter accordingly. The record now has its **first powered at-match non-Coder
cell**, closing an instrument asymmetry that had gone unnoticed for twelve phases.
**Nothing is running.** The map table above is current through the last closed phase;
[the journal's §0](docs/WRITEUP-rgr.md) is the authority on what is believed and at what
scope.

## Map of the composite

| Phase | Charter | What it was |
|---|---|---|
| 0–2 | [build-brief.md](docs/build-brief.md), [PHASES.md](docs/PHASES.md) | The original RGR experiment: register-gated refinement. H1 passed (later killed as artifact), H2 killed clean — the register is dead |
| Diagnostics | [DIAGNOSTICS.md](docs/DIAGNOSTICS.md), [PRE-B2-HANDOFF.md](docs/PRE-B2-HANDOFF.md) | What the H2 null means; predictions committed before B2 ran |
| K, M | [PHASE_K.md](docs/PHASE_K.md), [PHASE_M.md](docs/PHASE_M.md) | Kaggle → Modal lift-and-shift, then the vLLM/bf16 stack rebuild (100× throughput) with re-baselined gates |
| 3, 3R | [PHASE_3.md](docs/PHASE_3.md), [PHASE_3R.md](docs/PHASE_3R.md) | Reframe: "when does cross-step conditioning pay?" — then three audits that killed H1-as-artifact and retracted F2 |
| 3b | [PHASE_3B.md](docs/PHASE_3B.md) | The mechanism arc: escape-distance law, elimination argument, trace null at declared power, false-zero floor instrument |
| 4 | [PHASE_4.md](docs/PHASE_4.md) | Claim hardening: cross-family battery (DeepSeek, StarCoder2), F1/SINK retracted as one-family-scoped, oracle hints cross the competence boundary |
| 5 | [PHASE_5.md](docs/PHASE_5.md) | The journal turn (the record becomes the primary artifact) + where direction comes from: models execute direction they cannot manufacture |
| 6 | [PHASE_6.md](docs/PHASE_6.md) | Where the pathology comes from + extraction-readiness: origin measured (a Coder-continued-pretraining diet × a competence window, MIXED across code/language channels; the tie hypothesis demoted); the flagship floor verified on a distinct-seed control (instrument 5-for-6); the claims-to-evidence layer (§0.3) built |
| 7 | [PHASE_7.md](docs/PHASE_7.md) | Is the sink Qwen's, the diet's, or everyone's? The matched-artifact battery mined artifacts to each model's own quality and sampled the sink's region off-Coder for the first time: the sink is **Coder-diet-specific** (non-Coder families flat at match) — and the battery **reversed** Phase 6's "vanishes at 7B", which was itself a position artifact (7B sinks at match). The "competence window" becomes a diet × relational-position rule |
| 8 | [PHASE_8.md](docs/PHASE_8.md) | The mechanism of the sink + closing the confounds. Mechanism read (later amended): matched conditioning lands off a Coder model's manifold, so it elaborates rather than copies the artifact and degrades — position-gated. The **7B sink is confirmed** (n=37). Three confounds left honestly **open** (provenance, the sign/below-zero question, a second synthetic-code family) — each cheap, each named, none papered over |
| 9 | [PHASE_9.md](docs/PHASE_9.md) | Diet or provenance? A Phase-8 data point sitting in a caveat (a Coder model sinking on its *own unsurprising* output) was promoted to a rival hypothesis: maybe models sink on their own near-quality output, not because of any diet. The **generated 2×2** (model × self/foreign provenance, generation held flat) settled it: **the Coder model sinks on foreign code too, the non-Coder model on neither → the diet causes it, provenance-controlled; the self-conditioning hypothesis is refuted.** The mechanism read is corrected in the same motion — the sink is decoupled from surprise, so the earlier "off-manifold" story is disfavored; *why* the diet does it stays open |

*From Phase 10 the loop runs unattended between author check-ins, under a spec that is
itself pre-registered — [AUTONOMOUS_LOOP.md](docs/AUTONOMOUS_LOOP.md), frozen before its
first iteration, with its amendments dated on the page.*

| Phase | Charter | What it was |
|---|---|---|
| 10 | [PHASE_10.md](docs/PHASE_10.md) | The audit that cost the record its biggest number. Chartered to measure a clean model *below* match, it instead found that the sink criterion had silently drifted — the original "below **both** nulls" had become a signature that dropped the copy null, which scores a false sink by construction wherever the artifact is worse than the model. Restoring it **withdrew one 7B confirmation and pre-empted a second**; a replication at a fresh seed then failed outright, and the 7B sink — cited across the journal — was retracted with **no surviving support**. Its absence was then *measured* at true match. Also priced the targeting instrument that every matched cell had been aimed with (SE 0.028 → 0.011) and killed a phantom $31 line item |
| 11 | [PHASE_11.md](docs/PHASE_11.md) | The ladder at match, powered. The first scale statement in this record resting on cells matched on the **measured relation** rather than the raw stimulus — every rung at its own Δ_art ≈ 0: sink at 1.5B (−0.052, n=44) and 3B (−0.051, n=39), **absent at 7B** (−0.008, n=29). The sink **is** scale-bounded, on ground the earlier "scale-bounded" reading never had. Also discharged the small-n exposure under the flagship claim |
| 12 | [PHASE_12.md](docs/PHASE_12.md) | The first non-vLLM instrument: a probe that teacher-forces a model over its own committed generation and splits attention across the artifact / problem / generated spans. **Artifact-attention magnitude is excluded as the mechanism** — all four models sit near 10%, the two pairs disagree in sign, both deltas < 1 SE. A strong null rather than a blind one: the same measurement resolves a monotone size effect and a family effect 5–10× larger, so the instrument was demonstrably looking |
| 13 | [PHASE_13.md](docs/PHASE_13.md) | Head-level structure, and the record's first **intervention**. S1 (correlational): artifact attention is more *concentrated* in sinking models — the 30% underdog fired. S2 (causal): ablating 16 heads destroyed the model, a recorded instrument miss with K deliberately **not** retuned in-phase |
| 14 | [PHASE_14.md](docs/PHASE_14.md) | The ablation dose-response — and a **design-level miss caught mid-run by algebra**. Ablating only the conditioned arm makes `sink = cond − artifact` a difference of the same variable, so the adjudication statistic was **identically zero for any data** and the 45% favourite fired *vacuously*. Scored a miss, not a hit; the corrected design is named on the page. Salvage: the S1-selected heads are genuinely more load-bearing than random heads at matched dose (p 1.3e-17) |
| 15 | [PHASE_15.md](docs/PHASE_15.md) | The **architecture twin**. Phase 13's concentration finding survived a size control and a head-count control, then died to one cell that holds architecture fixed: general-Qwen-1.5B vs Coder-1.5B — same base, verified same 28L×12H, one clean and one sinking, **indistinguishable in concentration** (and the clean model carries the record's *highest*). Concentration is architecture-linked, not sink-linked. The decisive cell had been committed since Phase 7 and never looked at |
| 16 | [PHASE_16.md](docs/PHASE_16.md) | Is the sink **framing**-sensitive? Originated in an outside-reader charter that asked for its own load-bearing claims to be checked first — two of three did not survive, and the charter was reshaped on the page. Closed **INCONCLUSIVE on instrument**: a frozen validity gate returned −0.0296 against a ≤ −0.03 threshold and failed **by 0.0004**. Honoured, not retuned. Its free decomposition found what became the next question: the sink's dominant channel is **coverage** |
| 17 | [PHASE_17.md](docs/PHASE_17.md) | The verb question, powered and **closed**. The instruction verb is the largest anchoring lever this record has measured (moves PULL ≤0.127, against ≤0.028 for provenance) and had never been applied to a sink cell — every sink number in the journal used one fixed clause. Substituting an independent framing moves the sink by **+0.0004 ± 0.0096** (n=44, k=24), a CI that **excludes** Phase 16's near-miss. The sink is **framing-invariant**: it is dissociated from the escape-distance law's dominant lever, and the cheapest deflationary account of it is excluded |
| 18 | [PHASE_18.md](docs/PHASE_18.md) | The coverage channel — and a phase whose paid cell bought less than its free one. Seven free analyses **corrected the target before a dollar was spent**: the sink's adjudication criterion **does not survive the change of currency** (no artifact in any of the eight committed cells fully passes, so the copy null scores coverage zero *by construction*), coverage loss turns out **universal at ≤3B across every family and diet** and so is not the sink's mechanism, and the headline −0.432 was the most extreme of three seeds with no error bar. It also found a **compression law** — every model pulled 47–90% of the way toward the artifact it is shown, R² to 0.92 — then built a hypothesis on it and **watched the architecture twin refute it within the hour**. The paid cell tried temperature and closed an **instrument failure, no branch adjudicated**: two frozen kill criteria fired, and the branch tree had ignored both. Temperature **moves the null as hard as the treatment** |
| 19 | [PHASE_19.md](docs/PHASE_19.md) | The architecture twin at **true match** — and a phase that graded its own charter down. Its free P0 found the record's central family contrast (Phase 7) is **position-confounded**: every non-Coder cell that stayed clean sat at a *favourable* position, worth more shift than the effect being attributed to diet — and every powered at-match cell in the record was a Coder cell. Checked rather than assumed, the **diet claim survived**, because it rests on Phase 9's position-matched 2×2 rather than on Phase 7. The paid cell then measured the twin — same base, same 28L×12H, differing only in the Coder pretraining stage — at true match: **clean** (−0.0027), the 45% favourite. But the charter had claimed the cell could separate two predictions 0.04 apart, and its actual **MDE was 0.080** — so both predictions sit inside the interval and twin-vs-sibling is p 0.150. The instrument asymmetry is fixed; the inference is not |

## How to read

Start with the journal, in its designed order: **§10** (the working method —
the document's thesis), then **§0** (Claims & Scope Index — what the project
currently believes, claim by claim, with status and pointers). For the current
status, read the dated **living-record line** at the very top of the journal —
it names the current phase and where it stands (the §9.5 "live status" section
is an older, phase-3b-era snapshot, kept in place under append-only). Within §0,
**§0.3** is the claims-to-evidence layer — each live claim mapped to its
artifact, test, number, scope line, and stack lineage — so that an extraction is
*selecting rows, not re-deriving support*. Historical section numbering is
preserved; the reading order 10 → 0 → 1 is intentional.

## Repository map

```
docs/               The record: the journal (WRITEUP-rgr.md), phase charters
                    with pre-registrations and results, frozen design docs of
                    the original experiment (brief, architecture, decisions,
                    metrics, compute accounting)
artifacts/          Committed result JSONs — every number in the journal
                    traces to a file here or a run record
scripts/            Runners and analysis: Modal apps (modal_*.py) for
                    generation/execution/battery runs, plus local analysis
                    scripts (floor fits, AST distance, validations)
src/rgr/            The original register experiment's codebase (frozen since
                    Phase 2): loop, baselines, verifier, register, sandbox
                    execution, pure-stdlib metrics
tests/              Stdlib-runnable tests for the pure-logic modules
configs/            TOML experiment configs from the original experiment
runs/               (gitignored) raw generation/execution pools — kept locally
                    and on the Modal volume; artifacts/ carries the numbers
```

## Reproducibility

Frozen sampling configs (temperature, seed, stop sequences), frozen judges,
and volume-first persistence are specified per phase in the charters; §8 of
the journal is the operational ledger. Exact bit-reproducibility was retired
for a statistical standard when the stack moved to vLLM (decision D14, Phase
M) — reruns are compared distributionally, and rerun-stability checks are part
of each result's validation. Raw pools are not in git; the committed
`artifacts/` files are the numbers of record.

## Provenance

The repository began as **RGR — Register-Gated Refinement**, a single
falsifiable experiment whose claim was killed by its own pre-registered gate
(H2, 2026-07-12). The original README, brief, and design docs are preserved
unrevised (see `docs/`, and git history for the pre-composite README). The
package name `rgr` is kept for continuity; what the repository *is* now is the
composite record described above.
