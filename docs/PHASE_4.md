# Phase 4 — claim hardening: de-confound family from scale, complete the direction decomposition, reposition SINK

*Charter received 2026-07-16. Append-only; every item pre-registered before running.*

## 0. Charter (verbatim intent)

The record's two headline sentences are each one cheap experiment away from being wrong:

1. **"At this scale" is unlicensed.** Every finding was measured on exactly one model
   family (Qwen2.5-Coder). Scale and family are confounded in every claim. Precedent:
   the Spurious Rewards line (arXiv 2506.10947) — RLVR gains on Qwen2.5-Math from
   *random* rewards, driven by Qwen-specific pretraining priors, failing outright on
   Llama3/OLMo2; follow-up (2507.10532) attributes much of the surge to
   contamination/memorization. If our structural claims (peaked solution
   distributions, the suppressor decomposition, the attractor constants) are
   Qwen2.5-Coder properties rather than scale properties, that is a catastrophic
   scoping loss.
2. **"The constraint is the model's ability to use direction" over-reads our own
   decomposition.** Olausson's bottleneck localization came from a *human conceptual
   explanation* arm. Our ceiling arm was a verbatim execution trace — near-zero
   direction for pass@50 = 0 structural failures (output 17 ≠ expected 42 does not say
   which algorithmic idea is wrong). TRACE and MODELABS nulling together leaves the R3
   null ambiguous between "1.5B cannot use direction" and "no arm ever contained
   direction." The missing rung is an approach-level hint arm.

**Order: H0 (free CPU + writing) → H1 (cross-family battery) → H2 (hint arm +
near-miss band) → H3 (cross-scale pre-registration; run is a separate sign-off).**
Cheapest/highest-stakes first. Standing rules unchanged: append-never-revise;
pre-register with odds before running; **no learned verifier anywhere**; the
reconciliation ledger governs every external result used in design (and applies to our
own entries); §8 operational hardening applies to all runs.

**Phase gate:** Phase 4 closes when every headline claim in the abstract carries either
a cross-family scope line (H1) or a completed-decomposition basis (H2), and the
SINK/elimination-argument positioning is corrected (H0). Only then the rethink (paper
structure, TTT successor, scale escalation).

---

## H0a — AST-distance robustness of the escape-distance law

**PRE-REGISTRATION (2026-07-16, frozen before any distance is computed).**

**Why.** PULL is lexical (1 − `difflib.SequenceMatcher.ratio`). On stdin/stdout
problems every solution shares boilerplate (read loop, parse, print), which compresses
lexical distances; conversely, algorithmically identical solutions can be lexically
distant. "TRACE generated at i.i.d. distance (0.85)" is currently a claim about
tokens, not approaches.

### Frozen metric

- **AST-PULL(gen, art)** = ZhangShasha-TED(canon(gen), canon(art)) / (|canon(gen)| + |canon(art)|) ∈ [0, 1].
- **Canonicalization** `canon`: parse with `ast.parse`; every `Name` id, `arg` name,
  function/class def name, and import alias → the placeholder `_v`; every `Constant`
  → its type name (`int`/`str`/`float`/`bool`/`NoneType`/…). `Attribute.attr` and
  imported module names are **kept** (API surface is structure). Node label = AST
  class name (+ kept attr/name where applicable); children in field order.
- **Tree edit distance**: Zhang–Shasha, unit costs (insert 1, delete 1, relabel 1 if
  labels differ, 0 if equal). Implementation validated against hand-checked examples
  (identity → 0; the classic ZS paper example → 2); validation recorded in the artifact.
- **Exclusions, counted per cell**: candidates that fail `ast.parse`; canonicalized
  trees > 3,000 nodes. Destination-geometry pairwise sets subsample ≤ 12
  codes/problem (seed 17).
- Absolute AST-PULL values are **not commensurate** with lexical PULL; every claim
  under test is an ordering, a monotonicity, or a ratio. Lexical values recomputed
  from the same records and reported side by side.

### Legs (exact pools; all committed, no new generation)

- **Leg A — D-measure cells** (`runs/modal/dmeasure_gen.json`; artifacts
  reconstructed by the frozen first-60 rule from `m3_candidates.json` +
  `m3_labels.json`; E1/E2 → the shared `fail` artifact, E5 → `correct`, E0 measured
  vs `fail` = the anchor, per W0a). Per-cell mean AST-PULL, conds × T ∈ {0, 0.8, 1.2}.
- **Leg B — E7 cells** (`runs/modal/dmeasure_e7_gen.json`): E7@{0.8, 1.2}, E1@1.5,
  E0@1.5, all vs `fail`.
- **Leg C — R3 arms, medium** (`runs/modal/r3_cand_medium_{B1,ANCHOR,TRACE,MODELABS}.json`
  vs the frozen highest-frac artifact from the committed medium T=0.8 pool). Per-arm
  mean AST-PULL. (Easy strata exploratory, reported if cheap.)
- **Leg D — destination geometry** *(opportunistic, non-load-bearing)*: within-set
  pairwise AST distance for high-escape sets (E1@1.2, E7@1.2, R3-TRACE medium) vs
  their distance-to-artifact; per-problem single-linkage clustering at a fixed
  threshold (0.5 × set mean pairwise distance). Report whether escaped mass
  re-concentrates (second attractor) or spreads. Flag structure; do not narrativize.

### Coverage pairing

Coverage per cell is **not recomputed** — committed values from
`artifacts/dmeasure_conditioning.json`, `dmeasure_e7.json`,
`r3_conditional_reachability.json`. Only the distance axis is re-measured.
Monotonicity cell set (frozen): the failure-conditioned, in-domain cells
E1@{0, 0.8, 1.2}, E2@{0, 0.8, 1.2}, E7@{0.8, 1.2} — 8 cells, coverage vs mean
AST-PULL, Spearman ρ.

### Pre-registered branches and odds

Leg-level predictions (each recorded, each stands whether it holds or not):

- **L1 (attractor holds structurally)**: max(E1, E2, E5 AST-PULL) < E0 AST-anchor at
  matched T, for T ∈ {0.8, 1.2} — **80%**.
- **L1b (provenance irrelevance survives)**: |E1 − E2| AST-PULL < 15% of the
  (anchor − conditioned) gap at matched T — **75%**.
- **L2 (monotonicity survives)**: Spearman ρ(coverage, AST-PULL) ≥ 0.8 over the
  8-cell set (lexical ρ reported side by side) — **65%**.
- **L3 (the stretch survives)**: E1@1.2 closes ≤ 60% of the AST escape distance
  (AST-PULL(E1@1.2) / AST-anchor(E0@1.2) ≤ 0.60) — **60%**.
- **L4 (repulsion stays in copy territory)**: E7 AST-PULL < E0 AST-anchor at matched
  T — **80%**.
- **L5 (R3 arms; interpretive, can reverse a mechanism sentence)**: TRACE mean
  AST-PULL within ±20% of B1's → "generated at i.i.d. distance" survives
  structurally — **55%**; TRACE < 0.8 × B1 → the "full escape with direction
  supplied" reading was a token illusion; §9.3.1/§9.7 mechanism sentences amended in
  place — **30%**; TRACE > 1.2 × B1 — **15%**.

**Branch rule (headline, decided by L1 + L2):**

- **(a)** L1 holds at both matched temps AND L2 holds → monotonicity and anchor
  ordering survive; **the law hardens — escape is structural.** Odds: **65%**.
- **(b)** otherwise → the law is substantially lexical. This is the sharper mechanism
  statement, not a loss: "token gravity" becomes literal surface copying (connect to
  the induction-head/copying literature), and figure axes are relabeled honestly.
  Odds: **35%**.

L5 is resolved separately from the branch rule either way.

**Artifact:** `artifacts/h0a_ast_distance.json`. Writeup: appended to §9.3 as **"The
law under structural distance."**

*(H0a RESULT lands below this line after the run.)*
