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

### H0a RESULT (2026-07-16) — **branch (a): the law hardens; escape is structural**

Implementation validated (classic ZS example = 2; C kernel ≡ pure-Python reference on
200 random tree pairs). 23,400 distances; exclusions 512 parse-fail + 74 cap (~2.5%),
714 no-code. [artifacts/h0a_ast_distance.json].

| cell | AST-PULL | lexical PULL | | cell | AST-PULL | lexical PULL |
|---|---|---|---|---|---|---|
| E0 anchor @0 | **0.232** | 0.409 | | E5 @0 | 0.001 | 0.020 |
| E0 anchor @0.8 | **0.275** | 0.491 | | E5 @0.8 | 0.027 | 0.066 |
| E0 anchor @1.2 | **0.328** | 0.594 | | E5 @1.2 | 0.100 | 0.168 |
| E0 anchor @1.5 | **0.328** | 0.740 | | E7 @0.8 | 0.148 | 0.196 |
| E1 @0 | 0.046 | 0.075 | | E7 @1.2 | 0.252 | 0.357 |
| E1 @0.8 | 0.114 | 0.176 | | E1 @1.5 | 0.289 | 0.560 |
| E1 @1.2 | 0.209 | 0.309 | | R3-med B1 | 0.374 | 0.841 |
| E2 @0 | 0.017 | 0.043 | | R3-med ANCHOR | 0.144 | 0.399 |
| E2 @0.8 | 0.033 | 0.068 | | R3-med TRACE | 0.391 | 0.860 |
| E2 @1.2 | 0.086 | 0.157 | | R3-med MODELABS | 0.355 | 0.845 |

**Leg verdicts against the pre-registration:**

- **L1 HOLDS** (80% ✓): every conditioned cell sits below the E0 anchor at matched T.
- **L1b MISS (75% odds — wrong), and the miss is a specification error, recorded:**
  E1-vs-E2 differ in the instruction verb as well as provenance, so the registered
  test conflated the two axes. Post-hoc follow-up (unregistered, labeled —
  [artifacts/h0a_d2a_ast_followup.json]) on the correct instrument, the D2a 2×2:
  max provenance Δ 0.007/0.013/0.034 vs max verb Δ 0.023/0.076/0.127 at T=0/0.8/1.2 —
  **provenance-irrelevance survives structurally** (verb ~3–4× provenance, the same
  shape as lexical D2a). Both the miss and the correction stay on the page.
- **L2 HOLDS** (65% ✓): Spearman ρ(coverage, AST-PULL) = **0.952** over the frozen
  8-cell set — *identical* to the lexical ρ (0.952). The monotonicity is
  metric-invariant.
- **L3 MISS** (60% odds — wrong, narrowly): E1@1.2 / anchor = **0.636** > 0.60. The
  stretch is smaller structurally than lexically (52%): E1@1.2 has closed ~64% of the
  *structural* escape distance. The elimination argument's unclaimed room narrows
  (~36% of the axis) but does not close; nothing measured reaches the anchor.
- **L4 HOLDS** (80% ✓): E7 stays inside copy territory structurally (0.148/0.252 <
  0.275/0.328).
- **L5: iid_survives** (55% favourite ✓): TRACE/B1 = **1.048** — "generated at
  i.i.d. distance" is a structural fact, not a token illusion; the §9.3.1/§9.7
  mechanism sentences stand. ANCHOR deep-copies structurally (0.144 ≈ 0.38× B1).

**Two findings beyond the registered legs (stated, not narrativized):**

1. **The competence cliff is structurally empty motion.** E0@1.5's AST anchor equals
   E0@1.2's exactly (0.328 = 0.328) while lexical PULL grew 0.594 → 0.740: past the
   temperature boundary the extra token-distance buys **zero structural movement** —
   broken surfaces over unchanged structures. The law's temperature-bounded domain
   (W1/W2) sharpens: beyond T ≈ 1.2, lexical escape is noise, not exploration.
2. **The lexical axis does run hot on stdin/stdout pools, as suspected** (B1 lexical
   0.841 vs AST 0.374 — boilerplate compression is real in absolute terms), but every
   relative claim — ordering, monotonicity, arm geometry — is preserved under the
   structural metric. Branch (a) as pre-registered.

**Leg D (destination geometry, opportunistic).** Within-set pairwise AST distance
(≤12 codes/problem, seed 17): E1@1.2 pairwise 0.264, mean 4.85 clusters/problem, max
cluster fraction 0.47 (moderately concentrated — attractor + spread); E7@1.2
0.307/5.5/0.39; TRACE-medium 0.407/10.1/**0.20** (near-uniform spread — **no second
attractor**; escaped mass genuinely spreads). Flagged for any future mechanism work;
no claim rests on this.

**Writeup:** §9.3 "The law under structural distance" appended (same numbers,
condensed); the two prediction misses stand there with these odds.

---

## H0b — reconciliation-ledger additions + one amendment (2026-07-16, DONE)

Landed in WRITEUP §11: **Olausson entry AMENDED in place** (the outcome clause had
imported their bottleneck localization one rung past our arms — trace ≠ their human
conceptual-explanation oracle; the decomposition separated feedback *production* from
the *trace channel*, and did not reach "use"; H2a is the missing rung). **Four new
entries:** Chen et al. 2021 Codex alignment appendix (+ arXiv 2306.03438) → SINK as
replication-plus-extension; the inverse-scaling reading of Codex → H3's
opposite-directions prediction; Spurious Rewards 2506.10947 + 2507.10532 → H1's
existence (family transfer as mandatory audit); AlphaCode → the H1 cell-(i)
hypothesis (BCB flatness possibly Qwen-pipeline-scoped). Reference-list bullets added
for the three new works.

## H0c — writeup scoping corrections (2026-07-16, DONE)

- Every claim-bearing "at this scale" in the abstract, §5, §7, §9 now reads "on
  Qwen2.5-Coder at this scale"; a dated scope-correction banner opens the abstract
  and documents the edit class (nothing silent).
- SINK repositioned (§9.7 + abstract banner): quantified replication-plus-extension
  of the Codex buggy-prompt phenomenon; dual-hypothesis paragraph added
  (capacity vs distribution-matching; H3 discriminates).
- Elimination argument scoped to **in-context channels** (§9.3.1 channel-scope
  append): weight-space (TTT — named successor experiment, outside this record) and
  search-space (feedback-guided search; multi-model sampling) were never enumerated.
- §9.3.1 closing + §9.7 mechanism sentence amended: the R3 null bounds the bottleneck
  at the **trace channel**, not at "use" (per the Olausson amendment).
- MODELABS note at §9.7: 3 vs TRACE 1 is floor noise (p = 0.875); no
  compression-helps reading.

## H3 — cross-scale pre-registration (2026-07-16, FROZEN; running is a separate sign-off)

**Basis:** §11 ledger entries (Codex inverse-scaling; "How Many Tries" scale trend).

**Pre-registered prediction (directional only, no magnitudes licensed):** above 1.5B,
the two channel categories move in **opposite directions** —

- **Anchor-conditioning channels** (BEST / LAST / ANCHOR / BEST+ABSTRACT / D2c-style):
  conditioned-quality delta vs i.i.d. **worsens** with scale (imitation /
  distribution-matching: predicting continuation-of-buggy-code improves as the model
  gets better at distribution-matching).
- **Direction channels** (TRACE / HINT): recovery delta vs matched-compute B1
  **improves** with scale ("How Many Tries": ≤ +5.5pp at 70B).

**What it discriminates:** SINK-as-capacity predicts anchor channels *improve* with
scale; SINK-as-distribution-matching predicts they *degrade*. The two readings are
indistinguishable at a single scale by construction.

**Design sketch for the optional spot check (NOT authorized by this pre-reg; cost
gate + user sign-off required after H1/H2 report):** Qwen2.5-Coder-7B bf16 on L4
(verify KV headroom at our context lengths), one D2c cell (44 problems) + one TRACE
cell (medium stratum), same judge, seed 17, k matched to the 1.5B reference cells.
Combined with H1 this de-confounds scale from family within one design.

**Writeup:** §9.7 addendum (condensed) landed with H0c.

---

## H1 — cross-family battery (the catastrophic-loss test)

**PRE-REGISTRATION (2026-07-16, frozen before any generation).**

**Question:** which of the record's structural findings are properties of models at
0.5–3B, and which are properties of Qwen2.5-Coder?

**Models:** `deepseek-ai/deepseek-coder-1.3b-base` and `bigcode/starcoder2-3b` —
bracketing 1.5B, both trained on substantially organic code corpora (StarCoder2 on
The Stack v2) against Qwen2.5-Coder's synthetic-heavy pipeline. **Confounds recorded
honestly:** StarCoder2-3B is 2× parameters; neither is a Qwen-minus-synthetic-data
counterfactual; training cutoffs differ from Qwen2.5's, so LCB contest-date exposure
differs (families with earlier cutoffs may be *disadvantaged* on 2024 problems —
noted, not corrected). This battery **scopes findings; it does not isolate the
synthetic-data variable.** DeepSeek-Coder-1.3B-**instruct** is *not* run: the
suppressor ordering already inverted on medium (W2) and is not one of the four
headline findings — suppressor transfer stays untested in H1 (recorded limitation).

**Smoke gate (per family, before any screening cell counts):** 8 LCB-easy problems ×
8 samples, T=0.8, top_p 1.0, seed 17, the frozen R2 fenced-completion scaffold.
Gate: well-formed ≥ 0.85, degenerate ≤ 0.10 (R3-smoke thresholds), judged mean frac
and pass stats printed. A failing family gets **one** recorded template fix and one
re-smoke; still failing → excluded, failure recorded, battery proceeds one-family.

**Cells (per family; seed 17, top_p 1.0, T=0.8, frozen judges):**

| cell | design | Qwen reference |
|---|---|---|
| (i) BCB-Complete | n=200 (the committed seed-17 shuffle subset), k=50, base completion on `complete_prompt`, `_BASE_STOP`; frozen bcb_exec semantics (container right-sized per §8-5, recorded) | pass@8 0.328 / pass@50 0.425 / headroom +0.097 |
| (ii) LCB-easy | full 80, k=50, frozen fenced scaffold; lcb_exec **short-circuit variant** (pass/fail identical, frac unused — §8-5 cost rule; the committed all-cases judge is reserved for frac cells) | pass@8 0.566 / pass@50 0.763 / headroom +0.197 |
| (iii)+(iv) merged | the frozen 44 D2c artifacts (W3 §2 rule) × {E0 no-context, E1 = frozen D2C context}, k=8; **all-cases** judge (frac is the analysis); PULL vs artifact both arms | E1 PULL 0.430 / E0 anchor 0.774 (recomputed from committed pools, this pre-reg); frac: conditioned 0.374 vs copy-null 0.494 / Qwen-iid 0.468 |

*(Merge rationale, recorded: the committed D2c cell was k=8, and the family's honest
i.i.d. null must be the family's own E0 frac on the same 44 problems — cell (iv)'s E0
arm supplies it; a separate k=50 conditioning cell would duplicate generation without
adding a pre-registered contrast. Deviation from the charter table's "(iii) 44
problems [k=50]": k matched to the committed cell instead.)*

*(Artifact provenance, recorded: both families condition on the same Qwen-generated
artifacts — everything held fixed except the model. Provenance-inertness was measured
on Qwen only (D2a); if a family reacts to foreign-provenance artifacts differently,
that shows up as a SINK-form anomaly and is reported, not silently absorbed.)*

**Pre-registered branches and odds:**

- **F1-rescoped (BCB shallow tail).** Informativeness gate, pre-declared: pass@8 <
  0.15 → the family's BCB cell is competence-limited, F1 transfer **UNRESOLVED** for
  that family (evidence for neither branch). Informative cells: headroom ≥ 0.15 at
  in-band coverage (pass@8 ∈ [0.30, 0.60]) → **F1 is Qwen-scoped** (retract the
  "task-family property" language in place); cap ≈ 0.09–0.12 reproduced → hardens.
  Odds: both informative families reproduce the cap **60%**; exactly one shows
  headroom ≥ 0.15 **30%**; both **10%**.
- **Feasible region (LCB-easy runway).** Informativeness gate: pass@8 < 0.05 →
  UNRESOLVED for that family. Branches: headroom ≥ 0.15 off-Qwen → the runway
  finding generalizes; else Qwen-scoped (and the Phase-3b platform inherits the
  scope). Odds: at least one family ≥ 0.15 **55%**; both **25%**.
- **SINK.** The one cell where the literature makes the call (Codex precedent):
  conditioned mean frac < family's own E0 mean frac (paired, one-sided MC Wilcoxon
  as committed). Odds: directional in both families **85%**; significant (p < 0.05)
  per family **70%**. A non-replication is the surprise worth chasing.
- **Law form (constants expected to vary — pre-declared; no numeric transfer
  claimed).** Form under test: E1 PULL < 0.8 × family E0 anchor (conditioning pulls
  generations toward the artifact) — odds both families **75%**. Form breaking on
  another family is a major rescope of the law.

**Decision rule for the record (binding):** each finding gets an explicit post-H1
scope line in the writeup — **GENERALIZES** (both new families reproduce) /
**QWEN-SCOPED** (neither, cells informative) / **MIXED** (split or ≥1 uninformative,
stated per family). No finding keeps an unscoped "at this scale."

**Ops:** new `scripts/modal_h1.py` (self-contained app; judge code duplicated from
the frozen implementations, marked); model download via a hub-online function
(images stay hub-offline); per-cell volume persistence + resume; `--detach`; est.
$8–15 total. Cost note per §8-5: LCB pass@k judging short-circuits; all-cases
judging only on the 44 × 16 cell.

### H1 RESULT (2026-07-16) — **the catastrophic-loss test fired: the platform
negatives were Qwen properties; the mechanism's form generalizes**

Smoke gates: both families PASS on the frozen scaffold, zero template fixes
(deepseek wf 1.00/dg 0.00/frac 0.334; starcoder2 1.00/0.00/0.331).
[artifacts/h1_smoke_{deepseek,starcoder2}.json].

| cell | Qwen2.5-Coder-1.5B | DeepSeek-Coder-1.3B | StarCoder2-3B |
|---|---|---|---|
| LCB-easy pass@8 → pass@50 (headroom) | 0.566 → 0.763 (+0.197) | 0.401 → 0.638 (**+0.236**) | 0.468 → 0.700 (**+0.232**) |
| BCB pass@8 → pass@50 (headroom) | 0.328 → 0.425 (+0.097) | 0.358 → 0.535 (**+0.177**) | 0.158 → 0.410 (**+0.252**) |
| D2c conditioned vs own-iid (Δ, p_sink) | 0.374 vs 0.468 (**−0.095**, p≈5e-5 SINK) | 0.468 vs 0.362 (**+0.107**, p_sink 0.997) | 0.405 vs 0.358 (+0.046, p_sink 0.855) |
| E1 PULL vs E0 anchor | 0.430 / 0.774 | 0.181 / 0.815 | 0.314 / 0.825 |

**Per-finding scope lines (binding; the writeup carries each):**

1. **F1 (BCB shallow tail): QWEN-SCOPED — retraction branch fired exactly as
   registered.** DeepSeek shows headroom 0.177 ≥ 0.15 *at in-band coverage*
   (pass@8 0.358 ∈ [0.30, 0.60]) — the pre-committed retraction condition
   verbatim; StarCoder2 adds headroom 0.252 (below band, pass@8 0.158, marginally
   informative). The ~0.09–0.12 cap reproduces on **neither** family. Prediction
   accounting: the 60% favourite (cap reproduces on both) was **wrong**; the 10%
   both-families branch hit. F1's "task-family property" language is retracted in
   place (§7.3); on DeepSeek-1.3B, BCB-Complete would have **passed** the
   Phase-3a gate.
2. **Feasible region: GENERALIZES** — both families clear headroom ≥ 0.15 on
   LCB-easy, each *wider* than Qwen's. The 25% both-families branch hit. The
   runway finding is real and family-general; Qwen has the *least* of it.
3. **SINK: QWEN-SCOPED — and it INVERTS.** The one cell where the literature made
   the call went the other way: conditioning on the same ~0.49-frac artifacts
   *lifts* both families above their own i.i.d. (DeepSeek +0.107 — a significant
   CLIMB, p ≈ 0.003; StarCoder2 +0.046 n.s.), landing between own-iid and the
   artifact. The 85% directional-replication prediction was **wrong** — the
   pre-named "surprise worth chasing." Mechanistic re-read, stated carefully:
   what is universal is the **blend** — conditioned generation is pulled toward
   the artifact (form line below) and lands near a mixture of own-ability and
   artifact quality. For families whose i.i.d. sits *below* the artifact
   (0.36 < 0.49), imitation is an upgrade — exactly the Codex quality-matching
   story. For Qwen, whose i.i.d. (0.468) ≈ artifact (0.494), quality-matching
   predicts *no change*; instead Qwen landed **below both nulls** (0.374). **The
   sink is not explained by distribution-matching; it is a Qwen2.5-Coder-specific
   degradation** — which partially pre-empts H3's fork: the imitation story
   explains the cross-family blend, but Qwen's sink needs something else (an
   interference/instability of conditioning specific to this family's training).
4. **Law form: GENERALIZES** (75% ✓) — conditioning pulls generations deep into
   the artifact's neighborhood on every family (E1 PULL ≤ 0.38 × anchor in all
   three); constants vary as pre-declared (copy strength Qwen 0.43 > StarCoder2
   0.31 > DeepSeek 0.18, anchors ~0.77–0.83).

**Confounds, restated:** StarCoder2-3B is 2× parameters; training cutoffs differ
(the new families' LCB numbers may be *understated* on 2024 problems); the
battery scopes findings, it does not isolate the synthetic-data variable. The
suppressor decomposition remains untested off-Qwen (recorded limitation).

**One line: the record's negative platform claims (shallow tails, no headroom,
conditioning-sinks) were a portrait of Qwen2.5-Coder; the anchoring mechanism's
form (pull toward the artifact) is family-general.** The Spurious-Rewards
precaution was warranted in full. [artifacts/h1_cross_family.json].

---

## H2 — completing the direction decomposition: hint arm + near-miss band

**DRAFTED 2026-07-16 pre-H1-verdicts; FROZEN only after the H1 scope line is
inserted (charter: H2's interpretation inherits H1's scope from the start).**

### H2a — the hint arm (the missing Olausson rung)

**Channel:** HINT = an approach-level description in natural language. **Deviation
recorded:** LCB carries no reference solutions (dataset metadata empty), so the
charter's "oracle-derived from the reference solution" adapts to: frontier-model
worked approach derived from the problem statement alone, hand-audited. Hint set
**frozen pre-H1-results** at commit `48987b8` ([artifacts/h2_hints_frozen.json]):
125 hints (68 medium-stratum, 39 near-miss, 20 manipulation-check + 2 overlap),
leakage protocol binding (words only; no identifiers; no numerals/code tokens —
automated screen 125/125 clean; ~2 sentences; idea, never implementation). One
drafting error caught by the hand audit and corrected before freeze (abc341_a,
written from memory, did not match the statement — the audit protocol exists for
exactly this).

**Manipulation check (gate; runs before any stratum arm):** the frozen 20-problem
mid-p̂ set (easy base T=0.8, x nearest 25/50), arms **HINT-25 vs E0-25**, both
fresh, frozen config (base, T=0.8, top_p 1.0, seed 17). Gate: per-problem
mean-pass uplift (HINT − E0), one-sided MC Wilcoxon p < 0.05 **and** mean delta >
0. If hints do not lift solvable problems, the channel is broken and the stratum
run is **postponed, not interpreted**. Harm guard: mean delta < −0.05 → hints
actively sink (reported as its own finding). Odds: **gate passes 70%**.

**Stratum run (fires only on gate pass):** HINT-50 on the medium 0/50 stratum
(n=68), against a **fresh B1-50 control** (same batch, same config; the committed
R3 B1-50 and its floor-2 result stand as the calibration reference). Paired exact
McNemar, α=0.05 one-sided; the W2 power envelope carries over: a null forecloses
r ≳ 0.15; r ∈ [0.05, 0.13) pre-declared unresolvable. PULL and AST-PULL recorded
per generation; full recovery-validation protocol (judge rerun + contamination
audit + error-type stratification).

**Pre-registered branches (odds):**
- **(a) HINT recovery significantly above floor** → "capacity to use direction"
  is retracted-as-overclaim in place; the constraint was feedback *content*; a
  richness gradient exists above traces; the paper's headline changes — **20%**.
- **(b) HINT ≈ floor** → the competence-boundary thesis hardens dramatically: a
  stated correct approach does not cross the boundary — the darker, stronger
  claim, now licensed — **55%**.
- **(c) positive-unresolvable** (above floor, p ≥ 0.05, inside the declared
  unresolvable band) — reported as such, not spun — **25%**.

### H2b — the near-miss band (where the refinement question is live)

**Set:** the frozen 39-problem near-miss enumeration (x ∈ {1,2} of 50 in any of
the four easy cells + medium T=0.8; [artifacts/h2_hints_frozen.json]
near_miss_cells; per-tier reporting by min-x). Run config: the frozen base T=0.8
(easy problems on the easy scaffold, medium on medium). **Caveat recorded:**
problems enumerated at other temperatures may have lower p at T=0.8; all arms are
equally affected and the contrast is unbiased. **All three arms fresh** (B1-25 /
TRACE-25 / HINT-25, same batch, seed 17) — a committed-pool subsample for B1 would
inherit the selection's luck (regression-to-the-mean asymmetry); fresh arms keep
the contrast clean.

**Artifact rule for TRACE:** per problem, highest-frac *failing* candidate from
the committed run-config pool (the R3 rule restricted to failures); trace = the
frozen first-failing-case capture (stdin/expected/actual, 512-char cap).

**Power envelope (computed from the pooled p̂ enumeration, MC over exact paired
one-sided McNemar, α=0.05; k=25 chosen):** a doubling of per-sample rate is
resolvable at power **0.64**, a tripling at **0.97**; a 1.5× effect is
**pre-declared unresolvable** (0.29); false-alarm rate at null 0.034.

**Pre-registered prediction (the competence-boundary thesis's own falsifiable
consequence):** direction works *inside* the boundary. Odds: **HINT > B1
significant 55%**; TRACE > B1 significant 30%; **neither 35%** — if direction
fails even on near-misses, "cannot use direction" hardens beyond R3, and the
Self-Debug reconciliation sharpens (their regime is near-correct; ours shows even
near-reachable does not respond at 1.5B). Either branch is a paper-grade sentence.

**Writeup:** H2a + H2b land as §9.8 ("completing the decomposition"), with the
§9.7 headline amended in place per the branch taken.

*(H1 scope-inheritance line inserted at freeze; H2 RESULTS land below after the runs.)*

---
