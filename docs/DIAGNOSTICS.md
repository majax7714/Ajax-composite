# Diagnostics — what the H2 null means

One paragraph per diagnostic: procedure, the number(s), and whether the
**pre-registered prediction held**. Full procedures and the committed predictions
live in [PRE-B2-HANDOFF.md] §4; this file is where results land as they run.

All are **EXPLORATORY / POST-HOC**. They do **not** reopen the H2 verdict
([PHASES.md] Phase-2: FAIL, register dead) and do **not** support any "would have
worked if" claim. Held-out hygiene by diagnostic:

- **DIAG-1, DIAG-4** — re-analysis of committed Phase-0/Phase-2 artifacts; no new
  HumanEval access (DONE).
- **DIAG-2, DIAG-3** — MBPP val only; cost nothing against held-out.
- **DIAG-5** — re-analysis of *already-revealed* Phase-0 HumanEval passing
  candidates (teacher-forced NLL, no new generation, no new selection); spends no
  new held-out peek.
- **DIAG-6** — the one exception: *new* HumanEval generation, but for benchmark
  *characterization* only (it makes no register claim and, if anything, deflates
  future headroom claims). Lowest priority; clearly labeled as touching held-out.
- **DIAG-7** — CPU re-analysis of committed `b2.jsonl` + `full_b1.jsonl`
  (post-B2); no new access.

Predictions are committed before each diagnostic runs (DIAG-1..4 on 2026-07-12;
DIAG-5, DIAG-6, and the DIAG-3 directional hypothesis added 2026-07-12 after
DIAG-1/DIAG-4 reframed the null; DIAG-7 added 2026-07-12 after B2 landed). They
are left standing whether they hold or not.

---

## DIAG-1 — Did the register ever generate anything?  *(CPU · status: DONE 2026-07-12)*

**Pre-registered prediction:** of the 9 FULL-only wins, 0 or 1 came from a
problem where B1's pool was empty; FULL solves 0 of the ~26 oracle-empty
(pass@8 = 0) problems — i.e. the register's *generative* effect is exactly zero
and every FULL "win" is reselection among candidates B1 also sampled.

**Procedure (summary):** stratify the 9 FULL-only and 9 B1-only wins by whether
the losing condition's own 8-candidate pool contained a passing candidate; count
how many oracle-empty problems each condition solved. Inputs:
`runs/phase2/full_b1.jsonl`, `artifacts/lock_a.jsonl`. Output:
`artifacts/diag1_oracle_stratification.json` (`scripts/diag1_oracle_stratification.py`).

**RESULT.** Phase-0 oracle: 138 covered / 26 empty (pass@8 = 0.8415, exact).
9 FULL-only, 9 B1-only disagreements. Of FULL's 9 wins: **8 reselection** (B1's
own pool held a pass the verifier skipped), **1** from a B1-pool-empty problem.
Symmetry control: **2** of B1's 9 wins had FULL's pool empty. Of the 26
oracle-empty problems, FULL's selected candidate solved **3**, B1's solved
**5** (both via fresh resampling — lock_a's pool ≠ FULL/B1's).

**Prediction held? PARTLY — the miss was conceptual, and the conclusion is
stronger than the prediction.** The count "FULL-only wins with B1 pool empty" = 1
landed inside the predicted 0–1. "FULL solves 0 oracle-empty" was literally wrong
(3) — because the prediction treated "pass@8 = 0 in the Phase-0 draw" as "the
model cannot solve this." It is not: it is "not reached in *that* 8-sample draw at
temp 0.8." These problems are **low-probability, not out of distribution**; a
fresh resample recovers some. B1 is functionally a fresh *no-update* resample;
FULL is a resample **plus** register steering — and FULL reached **fewer**
previously-unreached problems than the resample control (3 vs 5; n = 26, Δ = 2, so
*not* "the register hurts," but the point estimate sits on the wrong side of
zero). The correct, strictly-stronger-than-Δ=0.000 statement: **the register's
generative effect is non-positive.** It is weakly consistent with the DIAG-3
entropy-killer hypothesis (register narrowing G's reach). And because 3–5 of the
26 dissolve under resampling, the genuine generation-failure set is < 26,
tightening §1.1 — the benchmark is even more saturated (DIAG-6 will bound it).
(What *causes* the emptiness — starvation vs transmission — is DIAG-2/DIAG-3/DIAG-5.)

---

## DIAG-2 — Encoding failure or transmission failure?  *(MBPP val · Modal T4 · status: DONE 2026-07-13)*

**Pre-registered prediction:** `passed_{t-1}` AUROC ≈ 0.55–0.65 (weak), step
index `t` strongly decodable — i.e. mostly **encoding failure** (register starved
at the input) with a clock component.

**Procedure (summary):** roll out FULL on MBPP val, store r_0…r_7, train small
probes r_t → {v_{t-1} (R²), passed_{t-1} (AUROC), error_type_{t-1} (macro-F1), t
(control)}. Chance probes ⇒ encoding failure; strong probes + flat pass rate ⇒
transmission failure; only-t ⇒ step counter. Output:
`artifacts/diag2_register_probes.json`.

**RESULT (2026-07-13, Modal T4 rollout on 42 MBPP-val problems, 294 probe rows).**
*Methodology note, logged honestly:* a first pass used random-row 5-fold CV and
got `passed_{t-1}` AUROC **0.87** — but rows are 7-per-problem and random splitting
leaks a problem's own register directions across train/test. Re-fit with
**problem-grouped** CV (leakage-free): **`passed_{t-1}` AUROC 0.558** (base rate
0.62), `v_{t-1}` R² −63, **`t` R² −98** (not decodable).

**Prediction held? Encoding-failure part YES; clock part NO.** `passed_{t-1}`
AUROC 0.558 lands squarely in the predicted 0.55–0.65 *weak* band — the register
carries only marginal decodable correctness signal, i.e. it is **near
encoding failure, starved at the input** (confirms [PRE-B2-HANDOFF.md] §1.2's
near-chance-φ prediction). But `t` is **not** decodable, so the "clock" half of the
prediction is refuted — the register did not even learn a step counter. Read
together with DIAG-3 (below): the register barely *encodes* useful signal yet still
*perturbs* sampling — so the perturbation is uninformative, not a knows-but-can't-
say transmission failure. → `artifacts/diag2_register_probes.json`

---

## DIAG-3 — Control authority: does r move G's sampling at all?  *(MBPP val · Modal T4 · status: DONE 2026-07-13)*

**Pre-registered prediction:** across-set edit distance statistically
indistinguishable from within-set; mean token-level KL(r_0 ‖ r_7) < 0.05 nats;
pass-rate difference CI straddles 0 — i.e. `r` has ~zero causal effect on what G
samples.

**Directional hypothesis (committed 2026-07-12, before the run):** if
**within-r_7 diversity < within-r_0 diversity**, the register is acting as an
**entropy killer** — soft-prompt conditioning narrowing the sampling distribution
the way a more specific prompt does. That would be fatal and pointedly ironic: a
mechanism whose *only* path to value was reaching solutions the model would not
otherwise sample would instead be *reducing* its reach. DIAG-1's B1 > FULL on the
oracle-empty stratum is weakly consistent with exactly this. (Getting this on the
record before the measurement is worth more than getting it right after.)

**Procedure (summary):** on MBPP val, sample 8 candidates under r_0 and 8 under a
well-updated r_7; compare within- vs across-set normalized edit distance,
pass-rate delta (CI), and first-32-token KL. Report within-r_0 vs within-r_7
diversity explicitly (the entropy-killer test). Produce the headline sentence
"8 soft tokens driven by a 128-dim register shift G's distribution by ⟨X⟩."
Output: `artifacts/diag3_control_authority.json`.

**RESULT (2026-07-13, Modal T4, 42 MBPP-val problems, m=8 per set).** Diversity
(mean normalized edit distance): within-r₀ **0.252**, within-r₇ **0.297**,
across **0.282**. **Mean KL(r₀ ‖ r₇) = 0.117 nats** over the first 32 next-token
positions. Pass rate: r₀ 0.598 vs r₇ 0.598, **Δ = 0.000, CI [−0.060, +0.057]**.

**Headline:** 8 soft-prompt embeddings driven by a 128-dim register shift G's
next-token distribution by **~0.12 nats** and *raise* within-set diversity, but
move pass rate by **0.000**.

**Prediction held? Partly — with one clean refutation.** *Pass-rate CI straddles 0*
→ held: the register has **no correctness-directed** authority. But *mean KL 0.117
nats* exceeds the predicted "< 0.05 / ~zero causal effect" — the register **does**
measurably move sampling, more than predicted. And the **entropy-killer hypothesis
is REFUTED**: within-r₇ diversity (0.297) is *higher* than within-r₀ (0.252), so
r₇ *widens* the sampling distribution rather than narrowing it. Net reading: the
register has **non-trivial but directionless control authority** — it perturbs and
even diversifies G's sampling (KL 0.117, +diversity) without steering toward
correct programs (Δpass 0). That the DIAG-7 pool-concentration effect is *not*
r₇-diversity-narrowing means it has a different origin (out-of-domain HumanEval
mis-steering, cf. DIAG-5), not entropy-killing. → `artifacts/diag3_control_authority.json`

---

## DIAG-4 — Settle the training-objective units  *(items 1–2 DONE 2026-07-12 CPU; item 3 DONE 2026-07-13 Modal T4)*

**Pre-registered prediction:** > 80% of the −10.7% teacher-forced loss
improvement sits on low-entropy (boilerplate) tokens; post-training sequence
probability of the target candidate stays below 1e-9 — i.e. training moved a
proxy that has no mechanical route to changing sampling behavior.

**Procedure (summary):** confirm 0.1713 / 0.1530 is mean per-token NLL
(code: HF `out.loss` over masked labels — confirmed); compute implied
sequence-level probability at real per-candidate token counts; split the per-
position NLL improvement into low- vs high-entropy tokens. Items 1–2 are
CPU-free; the entropy split (item 3) needs a small GPU forward pass over the
val targets. Output: `artifacts/diag4_objective_units.json`
(`scripts/diag4_objective_units.py`).

**RESULT (items 1–2).** *Item 1:* confirmed — 0.1713 → 0.1530 are **mean
per-token NLL** (read from `register_modules.pt`; HF `out.loss` over masked
labels), −10.7%. *Item 2:* the imitation targets (400 val passing MBPP
candidates, real lengths from `generated_tokens`) have **median 28 tokens**
(min 18, max 511) — **not** the 156-token HumanEval average §1.3 assumed.
Trained sequence-prob crosses 1e-9 only at L = 135 tokens, so at the median
target it is **1.4e-2** (untrained 8.3e-3), and **391/400 (97.8%)** of targets
sit above 1e-9.

**Prediction held? NO — it refutes post-mortem §1.3's arithmetic and opens a
sharper puzzle.** "Post-training target sequence probability stays < 1e-9" is
false: only 2.2% of targets fall below 1e-9; the median is ~1.4e-2, eminently
samplable. §1.3 imported the 156-token HumanEval length into an analysis of *MBPP*
training targets (~5× shorter); the exponential did the rest. The −10.7% moved
seq-prob **within a samplable regime** (8.3e-3 → 1.4e-2 at the median).

**But this does not resolve anything — it replaces a wrong explanation with a
genuine contradiction.** 1.4e-2 vs 8.3e-3 is a **1.7× increase** in the
probability of sampling the target; had it transferred, pass@1 could not have
moved by exactly 0.0000. We now hold a 1.7× in-domain teacher-forced gain against
a precisely-zero sampled effect. Deeper: *both* the original §1.3 calc and this
refutation measured the **wrong object** — P(exact string), when the objective is
P(*any* passing program), and with a passing set of enormous cardinality the two
barely relate. The imitation loss is string-reproduction; the null is a
**generalization failure from specific strings to the correctness manifold**,
which indicts the imitation-first call (D2(a)) in favour of RL's set-membership
reward ([DECISIONS.md] D2). "Training was not a no-op" **stands**, but what the
training *bought* is the open question. **DIAG-5** (does the teacher-forced gain
transfer to HumanEval?) and the entropy split (item 3) adjudicate the 1.7×→0 gap.
See [PRE-B2-HANDOFF.md] §1.3.

**RESULT (item 3, 2026-07-13, Modal T4 — faithful full k~U reproduction).** The
full prefix construction reproduces the training loss **exactly** (val NLL
0.1716 → 0.1529 untrained→trained, vs the reported 0.1713 → 0.1530). Splitting the
per-token improvement (12,632 tokens, entropy proxy = untrained per-token NLL,
median 0.0015): **99.7% of the −10.7% gain sits on HIGH-entropy (decision) tokens,
only 0.34% on low-entropy (boilerplate)** — mean improvement 0.023/token on
decision tokens vs 8e-5 on boilerplate.

**Prediction held? NO — refuted, and the *opposite* is true.** The pre-registered
call was ">80% of the improvement on low-entropy (boilerplate) tokens" (i.e.
training moved a mechanically-irrelevant quantity). Instead the training moved
almost entirely the **algorithmic-decision tokens** under teacher forcing. This
*strengthens* "training was not a no-op" and **sharpens the 1.7×→0 puzzle**: the
register demonstrably improved exactly the high-entropy decision tokens
teacher-forced, yet free sampling did not change (H2 null). The disconnect is
therefore a pure **teacher-forced→sampled gap** on the decision tokens, not a
"moved the wrong tokens" artifact. → `artifacts/diag4_item3_entropy_split.json`

---

## DIAG-5 — Does the teacher-forced gain transfer to HumanEval?  *(Modal T4 · status: DONE 2026-07-13)*

Added 2026-07-12 after DIAG-4 surfaced the 1.7×-teacher-forced → 0.000-sampled
contradiction. This is the decisive fork between the two explanations of it.

**Pre-registered prediction:** the 1.7× teacher-forced gain **shrinks
substantially or vanishes** on HumanEval — a domain/length transfer failure (the
register was trained to steer 28-token MBPP one-liners and deployed on 156-token
HumanEval functions, a ~5.6× length shift that DIAG-4's own numbers surfaced).

**Procedure (summary):** no new generation, no new peek — re-analyze the
already-labeled Phase-0 HumanEval passing candidates (`lock_a`). Compute
teacher-forced NLL of those passing candidates under the **trained** soft prompt
vs **untrained**, exactly as in Phase-2 training. Report the HumanEval
trained/untrained NLL and implied seq-prob multiplier next to the MBPP-val 1.7×.

**Interpretation (committed).**
- Gain **vanishes** on HumanEval → **domain/length transfer failure.** The
  register learned 28-token one-liners; deployment was out of length distribution.
  Fix: train in-domain or length-matched. DIAG-3 becomes secondary.
- Gain **survives** (~1.7× teacher-forced) but sampling stays flat → **pure
  teacher-forced/sampled gap** (the string→class problem). Then **DIAG-3 is
  decisive** and the story is transmission/authority.

**Why before DIAG-2:** one cheap GPU forward pass, no new held-out evaluation,
and it separates the two live explanations. DIAG-2's encoding/transmission
question only matters once DIAG-5 says the gain reaches the eval domain at all.

**Output:** `artifacts/diag5_transfer.json`.

**RESULT (2026-07-13, Modal T4).** Measured the trained-vs-untrained r₀ (k=0,
static) steering NLL on passing candidates in each domain:

| domain | target len | untrained → trained NLL | seq-prob mult (untrained→trained) |
|---|---|---|---|
| MBPP-val (in-domain) | ~42 tok | 0.1548 → 0.1481 | **×1.33** (helps) |
| HumanEval (held-out) | ~136 tok | 0.1073 → **0.1168** | **×0.28** (actively hurts) |

**Prediction held? YES — and overshot.** The gain did not merely vanish on
HumanEval, it **reversed**: the trained injection *lowers* the likelihood of the
HumanEval passing targets. The register learned MBPP-specific (short-target)
steering that mis-fires on the 3.3× longer HumanEval functions — a **domain/length
transfer failure**, dovetailing with DIAG-4 (targets median 28 tok MBPP vs 156
HumanEval). Per the fork, this makes DIAG-3 *secondary* to the domain/length story
— though DIAG-4 item 3 (gain concentrated on decision tokens, yet flat sampling)
keeps the teacher-forced→sampled gap live as well; both point at the same fix
(train in-domain / length-matched, and on-policy). **Scope caveat:** this measures
the k=0 *static* r₀ steering (the trained W₀+injector), a core component used at
every step-0 and by B1; the full k~U objective's HumanEval transfer was not
separately measured (would need HumanEval prefix construction), but the r₀
reversal already demonstrates the overfit. → `artifacts/diag5_transfer.json`

---

## DIAG-6 — Bound the maximum possible refinement headroom  *(HumanEval · GPU · status: DESCOPED 2026-07-12 → Phase 3, [DECISIONS.md] D12)*

**DESCOPED** (not run on the current stack). Its finding — the headroom ceiling is
low — is already carried by pass@8 = 0.8415 + DIAG-1's resampling recovery +
DIAG-7's pool account, and it is the most expensive item (~$3.30). The same
large-k pass@k measurement relocates to **Phase 3's benchmark-selection screen**,
pointed at a useful question. Rationale recorded as D12. Spec retained below for
if it is ever run there.

Added 2026-07-12 after DIAG-1 showed "oracle-empty" problems dissolve under
resampling.

**Pre-registered prediction:** on the 26 Phase-0 oracle-empty problems pass@k
rises steeply with k — **pass@50 ≥ 0.8** — so most "generation failures" are
sampling variance and the genuine refinement target is a small single-digit % of
the benchmark.

**Procedure (summary):** sample large-k (k ≈ 50–100) on the 26 oracle-empty
problems; compute unbiased pass@k. This is a hard ceiling on what *any* refinement
mechanism could ever win here.

**Interpretation (committed).** If pass@50 ≈ 0.95, most oracle-empty problems were
low-probability draws, the genuine refinement target is ~5% of problems, and the
§5 task-redesign conclusion is **mandatory, stated with a number** rather than
argued. If pass@50 stays low, a genuine hard core exists — the place a real
generative mechanism would have to win.

**Held-out note:** the one diagnostic that does *new* HumanEval generation.
Benchmark characterization only — no register claim; if anything it deflates
future headroom claims. Lowest priority under quota.

**Output:** `artifacts/diag6_headroom_ceiling.json` (if ever run).

**RESULT:** DESCOPED (not run) — [DECISIONS.md] D12. Its finding (low headroom
ceiling) is already carried by pass@8 0.84 + DIAG-1 + DIAG-7; the large-k pass@k
relocates to Phase-3 benchmark selection.
**Prediction held?** n/a (not run).

---

## DIAG-7 — Oracle pool coverage by cross-step channel: was every channel net-harmful?  *(CPU · committed data · status: DONE 2026-07-12)*

Added 2026-07-12 after B2 landed at 0.6220 < B1 0.6829 (Branch A). The sharp,
zero-GPU test of the whole account. Known going in: only the *selected* pass@1
per condition (FULL/B1 0.6829, B2 0.6220) from the `--h2` verdict. Unrevealed and
pre-registered here: **per-condition pool coverage (pass@8 = "did any of the 8
candidates pass").**

**The hypothesis and its sharp prediction.** If the cross-step channels are
net-harmful — each conditioning on prior *failed* attempts and anchoring the model
onto them — then pool coverage should degrade *monotonically in channel
bandwidth*: B1 (no cross-step, fresh i.i.d. samples) richest, FULL (128-dim latent
register) mildly degraded, B2 (full previous-candidate text) most degraded.

**Pre-registered prediction (2026-07-12): pool coverage ordered B1 > FULL > B2,**
with **B1 ≈ 0.84, FULL ≈ 0.82–0.84, B2 ≈ 0.72–0.78.**

**Procedure.** From committed `runs/phase2/full_b1.jsonl` (FULL, B1) and
`runs/phase2/b2.jsonl` (B2): per condition, pool coverage = fraction of the 164
problems with ≥1 passing candidate among its 8. Report the three numbers and the
ordering. Output `artifacts/diag7_oracle_coverage.json`
(`scripts/diag7_pool_coverage.py`).

**Interpretation (committed).** If the ordering holds, the null is not merely
"the register did nothing" — it is a **complete mechanistic account**: every
cross-step channel we built was net-harmful, monotonically in bandwidth, and that
was *structurally guaranteed* by a task whose pool coverage is already ~0.84 at
i.i.d. sampling, leaving anchoring nowhere to add and everywhere to subtract. That
is a materially stronger paper than a bare null, for an afternoon of CPU.

**RESULT.** Pool coverage (pass@8): **B1 0.8476 (139/164) > FULL 0.8232 (135/164)
> B2 0.7073 (116/164)** — strict monotonic ordering in channel bandwidth.
Selected pass@1: B1 0.6829, FULL 0.6829, B2 0.6220.

**Prediction held? YES.** Strict ordering B1 > FULL > B2 as predicted; B1 0.848
(pred ~0.84 ✓), FULL 0.823 (pred 0.82–0.84 ✓), B2 0.707 (pred 0.72–0.78 — landed
a hair below, i.e. the text channel was *even more* harmful than predicted). Two
sharpenings, both from committed data:

- **FULL vs B1 isolates the register updates** (both inject r₀; FULL updates r_t,
  B1 freezes it) → the register updates **cost 2.4 pts of pool coverage** (0.8232
  vs 0.8476, 135 vs 139 problems). So the register is not merely non-positive
  (DIAG-1) — its updates *actively shrink the reachable pool*. The verifier
  reselected FULL back to 0.6829, masking the pool damage at pass@1; for B2 the
  14-pt pool crash broke through to pass@1 (0.6220).
- **FULL's mean passing-candidates/problem (4.811) exceeds B1's (4.671) despite
  lower coverage** — the register piles *redundant* passes onto already-solvable
  problems while losing marginal ones (consistent with DIAG-1: B1 reaches more
  oracle-empty problems). B2's mean (3.640) is lowest — the text channel reduces
  both coverage *and* richness. *[Update 2026-07-13: this pool-concentration was
  hypothesised as the DIAG-3 "entropy-killer" signature, but DIAG-3's direct
  measurement REFUTED that — r₇ is more diverse than r₀. So the concentration is
  mis-directed steering (cf. DIAG-5's out-of-domain reversal), not
  diversity-narrowing.]*

The outcome-level account: at ~0.85 i.i.d. pool coverage there is almost nothing
for cross-step conditioning to *add* and a great deal for anchoring on prior
failures to *subtract*, so bandwidth buys harm. The GPU diagnostics (DIAG-2/3/5,
done 2026-07-13) pin the internal mechanism; see the Synthesis below.

### DIAG-7 — Correction: significance of the FULL−B1 gap  *(pre-registered 2026-07-13, before the McNemar run)*

External review flagged that the sharpening bullet above — "the register updates
**cost 2.4 pts** of pool coverage … its updates *actively shrink the reachable
pool*" — over-reads a **4-problem** paired difference (FULL 135/164 vs B1 139/164).
This is the same evidence strength DIAG-1 correctly *refused* to call "the register
hurts" (n=26, Δ=2). The DIAG-7 causal phrasing is therefore inconsistent with
DIAG-1 and is the one to fix. **The pre-registered DIAG-7 *prediction* (ordering
B1>FULL>B2 with point values) is untouched and still held** — only the interpretive
prose claiming a *significant* FULL−B1 harm is under correction (append, don't
revise).

**Test (pre-registered):** McNemar on the paired per-problem coverage discordance,
exact binomial (small counts), for FULL vs B1, B1 vs B2, FULL vs B2.

**Pre-registered expectation:** FULL vs B1 **non-significant** (p ≳ 0.2) — the point
estimate stays on the harm side but within paired noise; B1 vs B2 and FULL vs B2
**significant** (the 23-problem B2 crash is real and large). Corrected headline if
it lands: *no evidence the register improves pool coverage (measured six ways, all
null); only the text channel's degradation is statistically established.*

---

## DIAG-8 — Anchoring (content) vs prompt degradation (format): why does B2's pool crash?  *(CPU · committed data · pre-registered 2026-07-13, before the run)*

DIAG-7's most novel finding — pool coverage degrades monotonically in channel
bandwidth — confounds **bandwidth** with two mechanisms Phase 3 must tell apart:
(a) **anchoring (content):** conditioning on the failed candidate makes G generate
variations on its own mistake; (b) **prompt degradation (format):** an instruct
model never trained to condition on a prior attempt simply generates worse under
the unfamiliar ~2× prompt, regardless of content. DIAG-7 inferred (a) and measured
neither; DIAG-3 already refuted the *diversity-narrowing* form of anchoring **for
the register**, so (a) is weaker than it looks. Load-bearing: under (a) "low
bandwidth is a feature" motivates Phase 3's abstraction-not-candidate design; under
(b) B2's 0.707 is a formatting artifact and Phase 3 changes shape.

**Metric:** normalized edit distance `1 − difflib.SequenceMatcher(None,a,b).ratio()`
on extracted `code` — the exact DIAG-3 metric (numbers compare directly to DIAG-3's
within-r₀ 0.252 / within-r₇ 0.297). Three quantities, mean over the 164 problems:
- `d_consec` — B2 adjacent pairs `dist(code[i], code[i−1])`, i=1..7 (the anchored
  transitions; step 0 is un-anchored, prompt 191 tok vs ~360 for steps 1–7);
- `d_b2_all` — B2 all C(8,2) pairs (B2's intrinsic-diversity control; holds B2
  generation fixed);
- `d_b1_all` — B1 all C(8,2) pairs (i.i.d. baseline).

**Decision rule (pre-registered):**
- **Anchoring** if `d_consec < d_b1_all` **and** `d_consec < d_b2_all` — chained
  candidates cluster, both vs i.i.d. and vs B2's own non-adjacent pairs. Bandwidth
  story holds.
- **Prompt degradation** if `d_consec ≈ d_b2_all ≈ d_b1_all` yet B2 pass rate lower
  — B2 no more clustered than i.i.d., just worse. 0.707 is a formatting artifact.

**Pre-registered prediction:** *partial anchoring* — `d_consec ≈ 0.75 × d_b1_all`
(roughly a quarter tighter), and below `d_b2_all` too. Genuine prior: an instruct
model handed its own prior attempt predominantly edits it; but DIAG-3's refuted
diversity-narrowing and the review's caution keep the degradation branch open.

**Output:** `artifacts/diag8_anchoring.json` (`scripts/diag8_anchoring.py`).

---

## DIAG-9 — Semantic anchoring & refinement trajectory: does B2 loop on its own failure mode?  *(CPU · committed data · pre-registered 2026-07-13, before the run)*

DIAG-8 tests anchoring at the surface (edit distance); DIAG-9 tests it semantically
and asks whether the text channel *refines at all*. Uses B2's committed per-step
`error_type` and `frac_tests`.

**Metrics:**
- **error-type persistence:** P(`error_type[i]` == `error_type[i−1]` | both steps
  fail) vs the chance rate (share of the modal error type among failing steps).
  Excess ⇒ B2 stuck on the same failure mode.
- **refinement trajectory:** mean `frac_tests` by step index 0..7 — does
  conditioning on the prior attempt raise the fraction of tests passed across steps
  (genuine refinement) or stay flat/decline (net-harm)?

**Decision rule / pre-registered prediction:**
- If error-type persists **above** chance **and** frac_tests is **flat/declining** →
  semantic content-anchoring confirmed: B2 loops on its own failure mode,
  "refinement" doesn't refine (corroborates DIAG-8 anchoring + DIAG-7 net-harm).
- If error-type at chance and frac_tests flat → no semantic anchoring; degradation
  is generic.
- **Prediction (committed):** error-type persistence **modestly above** chance;
  frac_tests **flat across steps** (no monotone climb) — the text channel neither
  refines nor productively diversifies.

**Output:** `artifacts/diag9_error_persistence.json` (`scripts/diag9_error_persistence.py`).

---

## Roll-up — all diagnostics closed (2026-07-13)

| Diagnostic | Headline number | Prediction held? | What it implies about the null |
|---|---|---|---|
| DIAG-1 | FULL generative wins ≤ B1's (1 vs 2; 3 vs 5 oracle-empty) | partly (spirit yes, literal no) | register's generative effect is non-positive; "unreachable" set < 26 |
| DIAG-2 | passed_{t-1} AUROC **0.558** (grouped CV); t not decodable | encoding-failure part **yes**, clock part **no** | register barely encodes correctness, no clock → **starved at the input** (§1.2) |
| DIAG-3 | KL(r₀‖r₇) **0.117 nats**, r₇ *more* diverse; Δpass **0.000** | partly; entropy-killer **refuted** | register perturbs sampling but **directionless** (non-zero authority, zero steering) |
| DIAG-4·1-2 | median target seq-prob 1.4e-2 (samplable) | **no** (refutes §1.3 arithmetic) | opened the 1.7×→0 puzzle; targets were samplable |
| DIAG-4·3 | **99.7%** of −10.7% gain on *decision* tokens | **no** (predicted boilerplate) | training moved the right tokens teacher-forced → pure TF→sampled gap |
| DIAG-5 | r₀ steering ×1.33 MBPP but **×0.28 (reverses)** HumanEval | **yes** (overshot) | domain/length transfer failure (28-tok MBPP → 156-tok HumanEval) |
| DIAG-6 | **descoped → Phase 3** (D12) | — | ceiling already carried by pass@8 + DIAG-1 + DIAG-7 |
| DIAG-7 | pool coverage 0.848 > 0.823 > 0.707 (B1>FULL>B2) | **yes** (strict) | every cross-step channel net-harmful, monotonic in bandwidth; updates cost 2.4 pts of pool |

## Synthesis — what the null means (diagnostic record closed 2026-07-13)

The H2 null is **over-determined**, and every candidate cause is now measured:

1. **No task headroom** (DIAG-1, DIAG-7). pass@8 ≈ 0.85 at i.i.d. sampling; the
   genuinely-unreachable set is < 26/164; and pool coverage degrades monotonically
   in cross-step bandwidth (B1 > FULL > B2) — anchoring on a saturated task's own
   failures is net-harmful, and the register *updates* cost 2.4 pts of pool.
2. **The register is starved at the input** (DIAG-2). r_t carries only marginal
   decodable correctness signal (passed AUROC 0.558) and not even a clock —
   confirming §1.2's near-chance-φ prediction.
3. **Its control authority is directionless** (DIAG-3). r₇ *does* move G's sampling
   (KL 0.117 nats) and even widens diversity, but shifts pass rate by 0.000 — it
   perturbs without steering (the entropy-killer hypothesis is refuted; DIAG-7's
   pool concentration is out-of-domain mis-steering, not diversity-narrowing).
4. **The training objective moved a proxy that doesn't survive sampling**
   (DIAG-4·1-3, DIAG-5). Targets were samplable, and training concentrated its gain
   on the *right* decision tokens teacher-forced (99.7%) — yet sampling stayed flat
   (a pure teacher-forced→sampled gap), and the learned r₀ steering *reversed* out
   of domain (×0.28 on HumanEval), overfit to MBPP length.

None of these individually "explains" the null; together they make it inevitable.
The productive next moves are already recorded: an on-policy set-membership
objective ([DECISIONS.md] D2 post-hoc), a richer input into U ([PRE-B2-HANDOFF.md]
§5), in-domain/length-matched training, and a task with genuine headroom — but
those are Phase-3 design questions, not extensions of this record.
