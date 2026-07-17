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
comes from.

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

## How to read

Start with the journal, in its designed order: **§10** (the working method —
the document's thesis), then **§0** (Claims & Scope Index — what the project
currently believes, claim by claim, with status and pointers), then **§9.5**
(live status). Historical section numbering is preserved; the reading order
10 → 0 → 1 is intentional.

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
