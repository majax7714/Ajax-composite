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

## DIAG-1 — Did the register ever generate anything?  *(CPU · status: PENDING)*

**Pre-registered prediction:** of the 9 FULL-only wins, 0 or 1 came from a
problem where B1's pool was empty; FULL solves 0 of the ~26 oracle-empty
(pass@8 = 0) problems — i.e. the register's *generative* effect is exactly zero
and every FULL "win" is reselection among candidates B1 also sampled.

**Procedure (summary):** stratify the 9 FULL-only and 9 B1-only wins by whether
the losing condition's own 8-candidate pool contained a passing candidate; count
how many oracle-empty problems each condition solved. Inputs:
`runs/phase2/full_b1.jsonl`, `artifacts/lock_a.jsonl`,
`artifacts/phase0_difficulty_proxy.csv`. Output:
`artifacts/diag1_oracle_stratification.json`.

**RESULT:** _pending_.
**Prediction held?** _pending._

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

## DIAG-4 — Settle the training-objective units  *(CPU-first · status: PENDING)*

**Pre-registered prediction:** > 80% of the −10.7% teacher-forced loss
improvement sits on low-entropy (boilerplate) tokens; post-training sequence
probability of the target candidate stays below 1e-9 — i.e. training moved a
proxy that has no mechanical route to changing sampling behavior.

**Procedure (summary):** confirm 0.1713 / 0.1530 is mean per-token NLL
(code: HF `out.loss` over masked labels — confirmed); compute implied
sequence-level probability at real per-candidate token counts; split the per-
position NLL improvement into low- vs high-entropy tokens. Items 1–2 are
CPU-free; the entropy split (item 3) needs a small GPU forward pass over the
~240 val targets. Output: `artifacts/diag4_objective_units.json`.

**RESULT:** _pending_.
**Prediction held?** _pending._

---

## Roll-up (fill when all four are in)

| Diagnostic | Headline number | Prediction held? | What it implies about the null |
|---|---|---|---|
| DIAG-1 | _pending_ | _pending_ | generative effect real / exactly zero |
| DIAG-2 | _pending_ | _pending_ | encoding vs transmission failure |
| DIAG-3 | _pending_ | _pending_ | control authority of r over G |
| DIAG-4 | _pending_ | _pending_ | objective-vs-goal disconnect |
