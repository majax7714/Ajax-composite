# Diagnostics — what the H2 null means

One paragraph per diagnostic: procedure, the number(s), and whether the
**pre-registered prediction held**. Full procedures and the committed predictions
live in [PRE-B2-HANDOFF.md] §4; this file is where results land as they run.

All four are **EXPLORATORY / POST-HOC** re-analyses of an already-revealed
held-out evaluation. They do **not** reopen the H2 verdict ([PHASES.md] Phase-2:
FAIL, register dead) and do **not** support any "would have worked if" claim.
Held-out hygiene: DIAG-1/DIAG-4 re-analyze committed Phase-0/Phase-2 artifacts
(no new HumanEval peek); DIAG-2/DIAG-3 run on MBPP val only.

Predictions were committed on 2026-07-12, before any diagnostic ran. They are
left standing whether they hold or not.

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

**Prediction held? PARTLY — and the conclusion is stronger than the prediction.**
The count "FULL-only wins with B1 pool empty" = 1 landed inside the predicted
0–1. "FULL solves 0 oracle-empty" was literally wrong (3). But the register's
*generative* effect is confirmed **non-positive**: the frozen-register baseline
B1 reaches at least as many novel solutions on every metric (5 ≥ 3 oracle-empty
solves; 2 ≥ 1 opponent-pool-empty wins). FULL's wins are reselection plus
resampling variance that B1 shares — no evidence the register generated anything
B1's frozen r₀ did not. (What causes the emptiness — starvation vs transmission —
is DIAG-2/DIAG-3, not this.)

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

**Procedure (summary):** on MBPP val, sample 8 candidates under r_0 and 8 under a
well-updated r_7; compare within- vs across-set normalized edit distance,
pass-rate delta (CI), and first-32-token KL. Produce the headline sentence
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

**Prediction held? NO — and it refutes post-mortem §1.3.** "Post-training target
sequence probability stays < 1e-9" is false: only 2.2% of targets fall below
1e-9; the median is ~1.4e-2, eminently samplable. [PRE-B2-HANDOFF.md] §1.3's
"exponentially disconnected / unsamplable → unsamplable" argument imported the
156-token HumanEval length into an analysis of *MBPP* training targets, which are
~5× shorter. The −10.7% moved seq-prob **within a samplable regime**
(8.3e-3 → 1.4e-2 at the median), so the writeup's original "training was not a
no-op" **stands**, and §1.3's reframing does not. The entropy-attribution split
(item 3, "*which* tokens moved") remains pending a GPU pass and does not affect
this conclusion.

---

## Roll-up (fill when all four are in)

| Diagnostic | Headline number | Prediction held? | What it implies about the null |
|---|---|---|---|
| DIAG-1 | FULL generative wins ≤ B1's (1 vs 2; 3 vs 5 oracle-empty) | partly (spirit yes, literal no) | register's generative effect is non-positive; wins are reselection + shared resampling |
| DIAG-2 | _pending (GPU)_ | _pending_ | encoding vs transmission failure |
| DIAG-3 | _pending (GPU)_ | _pending_ | control authority of r over G |
| DIAG-4 | median target seq-prob 1.4e-2; 97.8% > 1e-9 | **no** (refutes §1.3) | training targets were samplable; objective was *not* exponentially disconnected |
