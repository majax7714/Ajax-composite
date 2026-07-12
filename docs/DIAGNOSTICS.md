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

## DIAG-2 — Encoding failure or transmission failure?  *(MBPP val · GPU · status: PENDING)*

**Pre-registered prediction:** `passed_{t-1}` AUROC ≈ 0.55–0.65 (weak), step
index `t` strongly decodable — i.e. mostly **encoding failure** (register starved
at the input) with a clock component.

**Procedure (summary):** roll out FULL on MBPP val, store r_0…r_7, train small
probes r_t → {v_{t-1} (R²), passed_{t-1} (AUROC), error_type_{t-1} (macro-F1), t
(control)}. Chance probes ⇒ encoding failure; strong probes + flat pass rate ⇒
transmission failure; only-t ⇒ step counter. Output:
`artifacts/diag2_register_probes.json`.

**RESULT:** _pending_.
**Prediction held?** _pending._

---

## DIAG-3 — Control authority: does r move G's sampling at all?  *(MBPP val · GPU · status: PENDING)*

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

**RESULT:** _pending_.
**Prediction held?** _pending._

---

## DIAG-4 — Settle the training-objective units  *(CPU-first · items 1–2 DONE 2026-07-12; item 3 pending GPU)*

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
transfer to HumanEval?) and the entropy split (item 3, pending GPU) adjudicate the
1.7×→0 gap. See [PRE-B2-HANDOFF.md] §1.3.

---

## DIAG-5 — Does the teacher-forced gain transfer to HumanEval?  *(re-analysis · GPU · status: PENDING — run BEFORE DIAG-2)*

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
**Readiness:** small GPU forward pass (trained + untrained soft prompt over
HumanEval passing candidates); shares plumbing with DIAG-4 item 3.

**RESULT:** _pending_.
**Prediction held?** _pending._

---

## DIAG-6 — Bound the maximum possible refinement headroom  *(HumanEval · GPU · status: PENDING — lowest priority)*

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

**Output:** `artifacts/diag6_headroom_ceiling.json`.
**Readiness:** GPU generation kernel, 26 problems × ~75 samples + execution
(~2k sandboxed runs).

**RESULT:** _pending_.
**Prediction held?** _pending._

---

## DIAG-7 — Oracle pool coverage by cross-step channel: was every channel net-harmful?  *(CPU · committed data · status: PENDING)*

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
ordering. Output `artifacts/diag7_pool_coverage.json`
(`scripts/diag7_pool_coverage.py`).

**Interpretation (committed).** If the ordering holds, the null is not merely
"the register did nothing" — it is a **complete mechanistic account**: every
cross-step channel we built was net-harmful, monotonically in bandwidth, and that
was *structurally guaranteed* by a task whose pool coverage is already ~0.84 at
i.i.d. sampling, leaving anchoring nowhere to add and everywhere to subtract. That
is a materially stronger paper than a bare null, for an afternoon of CPU.

**RESULT:** _pending_.
**Prediction held?** _pending._

---

## Roll-up (fill as diagnostics land)

| Diagnostic | Headline number | Prediction held? | What it implies about the null |
|---|---|---|---|
| DIAG-1 | FULL generative wins ≤ B1's (1 vs 2; 3 vs 5 oracle-empty) | partly (spirit yes, literal no) | register's generative effect is non-positive; "unreachable" set < 26 |
| DIAG-2 | _pending (GPU)_ | _pending_ | encoding vs transmission failure |
| DIAG-3 | _pending (GPU)_ | _pending_ | control authority of r; entropy-killer? (r_7 diversity < r_0?) |
| DIAG-4 | 1.7× teacher-forced gain → 0.000 sampled | **no** (refutes §1.3 arithmetic, opens 1.7×→0 puzzle) | wrong-object failure: string-reproduction ≠ class steering; indicts D2(a) |
| DIAG-5 | _pending (GPU, run first)_ | _pending_ | domain/length transfer vs teacher-forced/sampled gap |
| DIAG-6 | _pending (GPU)_ | _pending_ | hard ceiling on refinement headroom |
| DIAG-7 | _pending (CPU)_ | _pending_ | pool coverage B1>FULL>B2? every cross-step channel net-harmful |
