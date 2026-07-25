# Phase 16 — is the SINK framing-sensitive? The verb lever, never applied

*Charter opened 2026-07-25. Seventh iteration of the unattended loop
([AUTONOMOUS_LOOP.md], Amendment 1). Originates in an **outside-reader charter** supplied
by the author, which proposed an arbitration-interference hypothesis (H-ARB) and asked, in
its own §6, that its load-bearing claims be verified against the phase docs and artifacts
before anything was frozen. They were. Two of three did not survive, and the charter is
reshaped accordingly — see §1. Append-only; pre-registration frozen before spend.*

## 0. Provenance of this phase, stated plainly

The proposal was written by a reader working from the journal alone, without the phase
docs or artifacts. That is a genuinely useful vantage — it produced the one observation
this phase is built on, which nobody inside the loop had noticed in nine phases. It also
produced two claims about the record that are wrong, which is exactly why its own
instruction to verify first was the right instruction. Both outcomes are recorded here
because the loop's value depends on treating an outside proposal the same way it treats
its own: as a hypothesis, not a finding (§10 rule 2).

## 1. Verification of the proposal's three load-bearing claims *(free, no GPU)*

### 1.1 "The sink and the escape law contradict each other on per-sample quality" — **FALSE**

The proposal held that claim 6 says conditioning does not touch per-sample quality
(D2b "flat ~0.20") while claim 8 measures a per-sample-quality drop, and that the record
never reconciled them. `dmeasure_conditioning.json`, `per_sample_D2b.cells`:

| arm | T = 0.0 | T = 0.8 | T = 1.2 |
|---|---|---|---|
| **E0 (i.i.d.)** | 0.650 | 0.588 | 0.406 |
| **E1 (conditioned)** | 0.200 | 0.238 | 0.200 |

Conditioning drops mean per-sample pass **0.65 → 0.20**. The record's phrase is "flat
~0.20 **at every T**" — flat across *temperature* within the conditioned arm, which is
what makes temperature a coverage lever (E1 coverage 0.200 → 0.517 → 0.617) rather than a
quality lever. The proposal read "flat across T" as "flat across conditioning." **No
tension exists and none needed resolving.**

### 1.2 "The trough vertex sits ~0.14 below match, and the incumbent has no story for it" — **NOT ESTABLISHED** *(`h16_p0_vertex_audit.json`)*

R6's published vertex is **−0.1428**, and it is real as arithmetic. But its 9 points
**pool Coder-7B** — a model the record has since measured as having *no sink at any
position* (four cells spanning Δ_art −0.101 → +0.002, all within [−0.010, −0.003]) — with
the two scales that do sink. §0.4 already flags this and says nothing is built on it.

Refitting on the sinking scales alone, using **every committed Coder ≤3B cell** including
the two P11 powered cells and two P9 G1 cells that post-date R6's fit
([scripts/j16_p0_vertex_audit.py], 4,000-resample case bootstrap, seed 229):

| fit | n | vertex | shape | interior? | vertex CI95 |
|---|---|---|---|---|---|
| R6 as published (pools 7B) | 9 | −0.1428 | convex | yes | *never computed* |
| **Coder ≤3B only** | **8** | **+0.4147** | **concave** | **no** | **[−1.526, +2.030]** |
| ≤3B excluding the two n = 10 cells | 6 | +0.8432 | concave | no | [−1.094, +2.109] |

On the models that actually sink the quadratic is **concave** — the extremum is a maximum,
outside the measured range — and the vertex is unidentified, CI width 3.56, comfortably
covering zero. The interior trough is an artifact of pooling a non-sinking model into a
curve fit to find a trough.

The proposal set its own kill condition here: *"If the CI covers 0, H-ARB loses its
retrodiction and the charter weakens materially. Say so in the phase doc if that
happens."* **It covers 0.** H-ARB's one retrodiction — the only empirical support it had
that the incumbent lacked — is withdrawn before any spend, and H-ARB is therefore **not**
this phase's organising hypothesis.

*(What the ≤3B points do show, flagged exploratory and not adjudicated: the deepest
measured cells sit at Δ_art ≈ −0.045 and are the two **n = 10** G1 cells. Whether the
response is monotone or troughed below match is genuinely unmeasured — the leftmost ≤3B
cell is at −0.074 and nothing exists below it.)*

### 1.3 "D2a's verb lever has never been applied to a sink cell" — **TRUE, and it is the phase**

Verified against the frozen prompt builder. **Every sink measurement this record has ever
made** — D2c, P7, P8, P9, P11, P13, P14, P15 — uses one fixed framing, `_d2c_context`:

> `This attempt passed {npass} of {n_tests} tests.` **`Improve it so that all tests pass.`**

Meanwhile D2a (`dmeasure_d2a_verb_provenance.json`) measured the **instruction verb** as
the largest anchoring lever in the record: PULL up to **0.127**, against **≤0.028**
(lexical) / **≤0.034** (AST) for provenance — the 3–4× ratio that claim 14 rests on. The
record has spent nine phases varying model, scale, family, provenance, position, seed and
inference stack, and has held the instruction constant throughout. **That is a real gap
and it does not depend on any hypothesis being right.**

## 2. What P0.2 found for free, which reshapes the measurement *(`h16_p0_diversity.json`)*

Since §1.1's tension was illusory but its underlying instinct — nobody has decomposed a
sink cell on the coverage axis — was correct, that decomposition was run
([scripts/j16_p0_diversity.py], structural canonicalization via `ast.dump`):

| cell | status | Δ mean_frac | **Δ coverage (pass@8)** | Δ distinct/8 | max-cluster share |
|---|---|---|---|---|---|
| Coder-1.5B (P11) | **SINKS** | −0.064 | **−0.432** | −1.18 | 0.156 → 0.301 |
| Coder-3B (P11) | **SINKS** | −0.084 | **−0.410** | −2.03 | 0.131 → 0.356 |
| Coder-7B (R5 true match) | clean | −0.034 | **0.000** | −0.69 | 0.155 → 0.237 |
| DeepSeek-1.3B (P7 M1) | clean | **+0.050** | −0.205 | **−3.56** | 0.131 → **0.564** |

**Two results, both new, both free.**

**(a) The sink's dominant channel is coverage, not per-sample quality.** Coder-1.5B loses
**43 points of pass@8** against a 6-point mean-frac drop; Coder-3B loses 41. Coder-7B at
true match loses **exactly zero**. Parse rates are 0.99–1.00 in every arm, so this is not
syntactic breakage. The record has measured this phenomenon on mean frac for nine phases
while the larger effect — and a sharper separation of 1.5B/3B from 7B than the headline
number gives — sat unexamined in the committed pools.

**(b) H-COLLAPSE is disfavoured.** The rival hypothesis (the diet narrowed the conditional
distribution; the sink is support contraction) predicts diversity contraction tracking
sink status. Diversity contracts in **every** cell and contracts **most** in the clean
DeepSeek cell (distinct 7.95 → 4.38, max-cluster 0.13 → **0.56**) — which *gains* quality
(+0.050). That is faithful imitation: collapse onto the artifact, mean frac rises to the
artifact's level. The sinking models collapse **less** and sink anyway. Contraction does
not track the sink.

**Consequence for this phase's measurement:** coverage is reported as a co-primary
throughout, with its own paired test. The **branch is still decided on conditioned mean
frac**, which is the record's frozen sink currency and keeps every number comparable to
every prior cell.

## 3. The question

**Is the sink framing-sensitive?** Every sink number in this record was produced under a
continuation-framed instruction. D2a's own contrast — *improve* (E1) versus *write a
correct program* (E1p), provenance held fixed — halved PULL (0.176 → 0.080 at T = 0.8).
That manipulation has never been run on a sink cell.

This is worth running whichever way it lands, and it is **not** a test of H-ARB. Under any
hypothesis, a phenomenon that survives model, scale, family, provenance, position, seed
and inference stack but dissolves under a one-clause instruction change is a different
object from one that does not.

## 4. Design

**Manipulate only the final instruction clause**, mirroring D2a's own E1-vs-E1p contrast
so the lever is the one the record already calibrated. Provenance framing, the artifact,
the pass-count sentence and everything else are byte-identical.

| arm | final clause |
|---|---|
| **VERB-A** (incumbent) | `Improve it so that all tests pass.` |
| **VERB-B** (independent) | `Write a correct program that passes all tests.` |

**Both verbs are generated fresh at the same new seed (233).** The incumbent conditioned
arms were drawn at seed 173 (P11) and 17 (P7 M1); reusing them would confound verb with
seed. Regenerating both costs one extra arm per model and buys a **rerun-stability check
on the incumbent** for free — the §10 P2 distinct-seed protocol applied to a comparison
rather than to a control.

**Cells** (i.i.d. arms reused from the committed cells — the verb does not apply to them,
so they are free and unchanged):

| model | committed position | incumbent behaviour |
|---|---|---|
| **Coder-1.5B** (P11) | Δ_art +0.0016, n = 44 | **SINKS**, cond − artifact −0.052 |
| **DeepSeek-Coder-1.3B** (P7 M1) | Δ_art +0.0499, n = 39 | **clean**, cond − iid +0.050 |

Four new conditioned arms (2 verbs × 2 models), same problems, same artifacts, all at
seed 233. Judge, criterion and reporting unchanged: all-cases judge, adjudication on the
original **below-both-nulls** definition, legacy signature reported only.

## 5. Pre-registered predictions

Let **ΔC = cond(VERB-B) − cond(VERB-A)** on Coder-1.5B and **ΔD** the same on
DeepSeek-1.3B, each a paired per-problem difference tested at p < 0.05.

| # | branch | reading | odds |
|---|---|---|---|
| **A** | **both** ΔC and ΔD significant | framing moves conditioned performance in both families → the sink is partly a property of the instruction, not of the diet alone; rung 2 is reinterpreted, no committed number is refuted | **30%** |
| **B** | **neither** significant | the sink is **framing-invariant**. The escape law's dominant lever is inert on it → claim 6 and claim 8 are about mechanically distinct things, and the sink's robustness extends to the one axis that could most plausibly have dissolved it. A first-class dissociation, valuable on its own | **20%** |
| **C** | **ΔC only** | diet-gated framing sensitivity — the Coder model's conditioned behaviour depends on the instruction where the clean family's does not | **35%** |
| **D** | **ΔD only** | framing moves only the clean family; surprising, and would invert the natural reading | **10%** |
| **E** | technical failure | recorded | **5%** |

**C is the favourite** because D2a's own numbers show the verb is a real lever *and* that
`write-correct` was not simply better: it halved PULL but also **lowered** coverage
(0.517 → 0.317 at T = 0.8) and mean pass (0.229 → 0.133). De-anchoring did not help there,
so "VERB-B rescues the sink" is not the expected shape; "VERB-B moves the Coder model
somewhere" is.

**Reachability check (§10 addendum 2026-07-25, mandatory since Phase 14).** The adjudicated
quantity is `ΔC = cond_B − cond_A`, a paired difference between **two independently
generated arms** of the same model on the same problems. Writing the sink form out:
`sink_B − sink_A = (cond_B − art) − (cond_A − art) = cond_B − cond_A` — the constant
artifact null **cancels and leaves a free quantity**, unlike Phase 14 where interpolating
a shared-constant line made the difference identically zero. ΔC and ΔD can each take
either sign or none; branches A–D partition the (significant?, significant?) square
exhaustively and disjointly, and each cell is attainable. **Verified symbolically before
freezing.**

**Validity conditions, frozen.** VERB-A must reproduce the incumbent sink at the new seed
(`cond_A − artifact ≤ −0.03` for Coder-1.5B); if it does not, the phase reports
**INCONCLUSIVE on instrument** — a verb comparison against a baseline that failed to
replicate is uninterpretable — and the rerun-stability failure is itself recorded as the
result. n ≥ 30 per arm. Prompts are frozen in the pre-registration commit and audited for
leakage (no test content, no identifiers beyond the incumbent's).

**What a hit would and would not license.** A or C would license *"the conditioned
degradation depends on the instruction framing"* and nothing about *why*. It would **not**
license any claim that the sink is "just prompting" — the i.i.d. and copy nulls are
unchanged and the below-both-nulls criterion still has to be met — nor would it refute the
diet attribution, which rests on a cross-family contrast this phase does not disturb.

**Cost estimate: $0.20–0.60.** Four conditioned arms, ~1,300 generations total on
1.5B/1.3B-class models plus judging; i.i.d. arms cached. Calibrated from P11's measured
$0.68 for ~4,900 generations — the **generation** estimator, accurate five times running.
**Labelled estimate**, reconciled at close per Amendment 2. Loop spend before this phase:
**$4.76** of the $90/$110 envelope; month-to-date **$82.80** of the $200 cap.

## 6. Reconciliation ledger — entries drafted only after verification

Per the [PHASE_3B.md] rule, no external result enters as truth or as a design constant.
All six works proposed by the outside charter were checked against the actual papers
before drafting; **two carried inaccuracies and are entered with the error named.** None
is load-bearing for §4 — the design would be identical if all six were withdrawn.

1. **Yue et al., "Does Reinforcement Learning Really Incentivize Reasoning Capacity in
   LLMs Beyond the Base Model?" (arXiv 2504.13837).** *Verified:* title, authors and the
   central claim — RLVR models beat base at small k, base wins at large k, so RLVR
   abilities are bounded by the base model. *Setup delta:* their axis is a **training**
   intervention on the policy; ours is an **inference-time** conditioning operation on a
   frozen model. *Licenses:* the *shape* — "better at k = 1, worse at large k" is a named,
   published failure mode, so P0.2's finding that our sink is dominated by **coverage**
   loss while mean frac moves little is not exotic. *Does not license:* the entropy story.
   **⚠ The proposal attributed to this paper a temperature/entropy-matching result that is
   not in its abstract; that attribution is unverified and is not used.**
2. **Zhou, "When RLVR Shrinks the Reasoning Boundary: Diagnosing Pass@k Inversion"
   (arXiv 2607.20543).** *Verified:* exists, title and framing as described — pass@k
   inversion localised to **boundary prompts** where the base model holds rare correct
   solutions, with a per-problem anchoring remedy. *Setup delta:* training dynamic vs our
   single conditioned forward pass. *Licenses:* the **prompt-stratification** design —
   decomposing by base-model behaviour, which maps onto our stratum machinery and the
   false-zero floor (claim 15), and is a natural successor analysis to P0.2's coverage
   result. *Does not license:* any mechanism transfer.
3. **Goyal et al., "Context-Parametric Inversion: Why Instruction Finetuning Can Worsen
   Context Reliance" (arXiv 2410.10796; ICLR 2025 oral).** *Verified exactly as
   described*, including the non-monotone trajectory across TULU/Alpaca/Ultrachat and
   Llama/Mistral/Pythia. *Setup delta:* their stage is instruction tuning on general
   models; ours is continued pretraining on code. *Licenses:* the premise that **a
   training stage moves the parametric-versus-contextual balance non-monotonically** is a
   measured phenomenon, not a speculation — which is the strongest remaining external
   support for an arbitration-style account, now that H-ARB's internal retrodiction has
   been withdrawn (§1.2). *Does not license:* a direction or magnitude for the Coder diet.
4. **Kim et al., "How Training Data Shapes the Use of Parametric and In-Context Knowledge
   in Language Models" (arXiv 2510.02370).** *Verified:* models arbitrate by **internal
   confidence** — parametric for high-confidence facts, context for unfamiliar ones — with
   intra-document repetition, moderate intra-document inconsistency and skewed frequency
   distributions as the enabling properties. *Setup delta:* factual knowledge conflict,
   synthetic corpora; ours is program synthesis with execution grading. *Licenses:* that
   confidence-dependent arbitration is a real, data-driven property — the premise a future
   margin instrument would need. *Does not license:* the facts→programs mapping, which is a
   genuine gap and is why no margin regressor is chartered here.
5. **Kang et al., "Demystifying Synthetic Data in LLM Pre-training" (arXiv 2510.01631).**
   *Verified:* >1000 LLMs / >100k GPU hours; rephrased synthetic shows no collapse at
   foreseeable scale while **textbook-style pure-generated** mixtures show model-collapse
   patterns. *Setup delta:* pre-training corpus composition vs our inference-time
   conditioning. *Licenses:* a sharper reading of rung 3 — phi-1 is dominantly
   textbook-style pure-generated and, if synthetic-heaviness drove the sink, should sink
   *harder* than Qwen-Coder. It does not (replicated sub-threshold, −0.033 / −0.042).
   That is mild evidence **against** the synthetic-diet story and is written into rung 3 as
   a reason the lean has stayed sub-threshold across two measurements. *Does not license:*
   closing rung 3 — family-n is still 1.
6. **Zhang et al., "Verbalized Sampling: How to Mitigate Mode Collapse and Unlock LLM
   Diversity" (arXiv 2510.01171; ICML 2026).** *Verified:* real, and it traces mode
   collapse to **typicality bias in preference data** with a training-free prompting
   remedy. **⚠ The proposal cited it without an identifier and quoted a "1.6–2.1×
   diversity" figure that could not be confirmed; the figure is not used.** *Setup delta:*
   open-ended creative generation vs execution-graded program synthesis. *Licenses:* the
   logic of §4 — if a distributional pathology can be moved by **prompt framing alone**,
   then a framing-invariant sink (branch B) is informative and a framing-sensitive one
   (A/C) is diagnostic. *Does not license:* importing their metric or expecting a
   comparable magnitude.

---

*(Results append below.)*

---

## RESULT (2026-07-25) — **INCONCLUSIVE ON INSTRUMENT. The validity gate fired by 0.0004, and it was never a real gate.** *(`h16_verb_battery.json`)*

All four arms generated and judged cleanly (exit 0, seed 233, n = 44 / 39).

| model | verb | cond | vs artifact | vs i.i.d. | below both nulls | coverage |
|---|---|---|---|---|---|---|
| **Coder-1.5B** | A `Improve it…` | 0.4292 | **−0.0296** | −0.0412 | **yes** | 0.318 |
| **Coder-1.5B** | B `Write a correct program…` | 0.3956 | **−0.0633** | −0.0748 | **yes** | 0.341 |
| DeepSeek-1.3B | A `Improve it…` | 0.3577 | −0.0031 | +0.0468 | no | 0.128 |
| DeepSeek-1.3B | B `Write a correct program…` | 0.3648 | +0.0040 | +0.0539 | no | 0.179 |

| contrast | Δ(B−A) mean frac | SE | p | Δ(B−A) coverage | p |
|---|---|---|---|---|---|
| Coder-1.5B | **−0.0336** | 0.0176 | **0.0562** | +0.0227 | 0.567 |
| DeepSeek-1.3B | +0.0071 | 0.0067 | 0.2861 | +0.0513 | 0.152 |

**The frozen validity condition — `cond_A − artifact ≤ −0.03` — returns −0.0296. It fails
by 0.0004, so no branch is adjudicated and the phase closes INCONCLUSIVE on instrument.**
It is not retuned, not re-run at a fresh seed, and the threshold is not moved. A kill
criterion that is honoured only when it is comfortable is not a criterion, and this
record's other numbers are worth reading precisely because this one was not adjusted.

### The gate was inside the noise band by construction — this is the phase's real finding

P11's committed CI for this cell's `delta_cond_minus_iid` is **[−0.1258, −0.0028]**, width
**0.123**. The seed-233 replication (−0.0412) sits comfortably inside it, as does
DeepSeek's (+0.0468 inside [−0.0207, +0.1164]). Both arms replicated their committed cells
within noise.

So a validity threshold set at **−0.03** on a quantity whose 95% interval spans ±0.06 was
**never able to function as a gate**. It had roughly even odds of firing on a faithful
replication, and it did. The threshold was a round number chosen for plausibility, not a
statistic derived from the measured spread of the thing it was gating.

**This is the same error class the record has already logged twice**, which is what makes
it worth a ledger entry rather than a shrug:

| where | the guessed tolerance | the measured reality |
|---|---|---|
| Phase 10 R3 | on-target band ±0.03 | i.i.d. estimator SE **0.028** — the band was 1.08 SE |
| **Phase 16 (here)** | validity gate −0.03 | cell CI width **0.123** — the gate sat mid-noise |

Phase 10 fixed its instance by *measuring* the SE and powering the instrument (k = 8 → 24,
SE 0.028 → 0.011). I did not carry that lesson across to a different kind of threshold.
**Practice, now explicit: any pre-registered threshold on a measured quantity must be
stated in units of that quantity's measured spread, or derived from it — never as a round
number.** Phase 14's rule asks whether a decision rule *can* fire; this asks whether it
fires *for the reason intended*. They are different failures and both are cheap to check.

### What the arms show, flagged exploratory and NOT adjudicated

Separated per §10 because the gate failed; none of this is a verdict, and no §0 row moves.

- **The independent framing makes the Coder sink deeper, not shallower** (−0.0296 →
  −0.0633; Δ −0.0336, p 0.0562 — itself a near-miss on the pre-registered p < 0.05).
  Whatever the sink is, it is **not an artifact of the "improve" instruction**, which was
  the single most plausible cheap explanation available and is the reason this phase was
  worth running. This direction is consistent with D2a's own numbers, where
  `write-correct` halved PULL but *also* lowered mean pass (0.229 → 0.133) and coverage
  (0.517 → 0.317).
- **The verb moves per-sample quality, not coverage** (Coder coverage Δ +0.0227, p 0.567),
  while P0.2 established that conditioning's dominant channel *is* coverage. Two levers,
  two different axes — which, if it held up under a real gate, would say the verb lever
  and the sink act through different mechanisms.
- **The qualitative verdict is verb-invariant.** Coder-1.5B is below both nulls under
  *both* verbs; DeepSeek under neither. The framing moves the magnitude and leaves the
  classification alone.
- **Had validity passed**, both deltas being non-significant would have selected **branch
  B** (framing-invariant). Stated because it is derivable from the committed data and
  concealing it would be worse — but it is **not** the phase's verdict, and branch B is not
  claimed. The next phase must earn it with a gate that works.

## PHASE GATE — CLOSED (2026-07-25)

1. **Outside charter verified before spend; 2 of 3 claims failed and were recorded as
   failing** (§1). ✓
2. **Two free P0 results landed and committed** — the vertex audit and the first
   coverage-axis decomposition of sink cells (§1.2, §2). ✓
3. **Validity gate honoured as frozen** — failed by 0.0004, phase reports INCONCLUSIVE,
   nothing retuned, no branch claimed. ✓
4. **Raw data committed before analysis** (`aa1c4e1`… see log), with the gate failure named
   in the commit message. ✓
5. **A mid-run inference of my own withdrawn on checking**: I read the seed-to-seed
   movement (Coder 0.023 vs DeepSeek 0.003) as evidence that instability tracks sink
   status. Against the committed CIs both replications are ordinary sampling variation, and
   the two cells' intervals are comparably wide (0.123 vs 0.137). Withdrawn. ✓
6. **All six external citations verified before any ledger entry**; two inaccuracies named
   in place (§6). ✓

**Prediction accounting.** **No branch fired — the phase is INCONCLUSIVE and is scored as
an instrument miss, not as evidence for any branch.** A (30%), B (20%), C (35%), D (10%),
E (5%) are all unresolved. The pre-registration's *substantive* odds were never tested;
what failed was a validity condition attached to them, which is a separate object and is
where the loop's error was.

**Cost.** Phase 16 **$0.46** (`modal billing report`, queried 2026-07-25 18:25 EDT;
month-to-date aggregate delta $82.80 → $83.26) against a $0.20–0.60 estimate — **inside
the band**, the sixth consecutive calibrated generation estimate. Loop total **$5.22**;
month-to-date **$83.26**, against the Amendment-3 envelope of $100 report / $120 hard stop.

**What is open.** The verb question itself, **unanswered and cheap to answer properly** —
the four arms exist, and a successor needs only a validity condition derived from the
measured CI (e.g. "VERB-A's cond−artifact falls within P11's committed CI", which these
data satisfy) rather than a round number, plus enough n to resolve a −0.034 effect at
p < 0.05. Also open, and now better motivated than before: **the coverage channel** (§2),
which is where the sink actually lives and which no phase has yet manipulated. **Nothing
is running; Phase 16 is closed.**
