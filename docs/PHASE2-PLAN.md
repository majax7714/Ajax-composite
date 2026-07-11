# Phase 2 execution plan (written 2026-07-11, pre-build hedge)

If this session ends, a fresh session executes this document top-to-bottom.
Context: Phases 0–1 are CLOSED (see PHASES.md gate log). Verifier of record =
V-v2b QLoRA adapter at `runs/kaggle/phase1_v2b/runs/phase1_v2b/lora` (D9).
GPU budget: ~12 T4-hours remain this week (user-confirmed); plan fits in ~10.

## The training regime, concretely (extends D2 — record as D10 when built)

Imitation via **likelihood steering on synthesized prefixes**, reusing the
Phase-1 label data (no new rollouts needed for round 1):

For each MBPP problem with ≥1 passing and ≥1 failing candidate (Phase-1
labels: 16 candidates/problem with pass/fail, stored phi, and V-v2b scores —
see scoring kernel below):

1. Sample a prefix of k failed candidates (k ~ Uniform{0..7}, random order):
   `r_0 = W_0·phi(problem)`; `r_{i+1} = U(r_i, phi(c_i), v_i)` for the k
   failures (phi from stored float16 arrays, v from V-v2b scores).
2. Target: one passing candidate c* (sampled per example).
3. Loss: teacher-forced `-log P_G(c* | chat_prompt(problem), soft(r_k))`,
   G frozen 4-bit; gradients flow through the soft-prompt embeddings into
   injector, U (unrolled k steps), and W_0.

Rationale: with V register-blind (D3) there is no differentiable V→register
path, and "imitate register trajectories that led to passes" is vacuous when
initial modules are random. Likelihood steering is the supervised signal that
directly encodes the register's job: integrate failure evidence (phi, v) and
make the passing solution more likely on the next regeneration. Trainable
surface stays exactly {injector, W_0, U} (~2.4M params, D6 respected).

Register stability guards already implemented and tested
(rgr/register/update.py): RMS-norm + delta clip; diagnostics module alarms on
collapse/blow-up (rgr/register/diagnostics.py). Log RegisterHealth every run.

## Kernels (in order; each mode already has launch/status/fetch plumbing)

1. **phase2_score** (~0.7h): score all 6,832 Phase-1 candidates with V-v2b
   (LoRA in bundle) → `runs/phase2/v_scores.json` keyed (problem_id, idx).
   Needed because U consumes v_t at inference; training must see the same
   distribution.
2. **phase2_train** (~2–2.5h): the regime above. 2–3 epochs over ~6k
   examples; select on MBPP-val teacher-forced loss (val problems' examples
   held out of training). Save `register_modules.pt` (injector + W_0 + U) +
   RegisterHealth stats. Bundle needs: labels.jsonl, phi/ + phi_problems/
   arrays (~25MB), v_scores.json, v2b LoRA (~35MB).
3. **phase2_full** (~5.5h): on HumanEval, per problem: FULL (N=8, register
   updates on, V-v2b scores each step, r trajectory logged) and B1 (N=8,
   register FROZEN at r_0 — batched, since frozen-register steps are i.i.d.).
   Execute every candidate in Daytona (pooled). B1′ is FREE: it equals the
   Phase-1 V-reranked lock_a (0.6707) — same candidates, same reranker; do
   not rerun it.
4. **phase2_b2** (~4.5h): B2 in-context refinement, N=8 (prev candidate +
   verifier score in prompt via generate_with_feedback), V-v2b scored,
   executed. Sequential by construction.

If quota runs short: phase2_full is the H2-critical run; B2 can wait for the
weekly reset. FULL-vs-B1 alone decides "register updates vs parallel
sampling"; FULL-vs-B2 completes the claim.

## Local analysis (no GPU)

- H2 verdict: Δpass@1 and Δpass@k (FULL−B1, FULL−B2) with problem-level
  bootstrap CIs (rgr.evals.bootstrap); matched-compute assertion via ledgers
  (COMPUTE_ACCOUNTING.md: 8 generations/problem/condition everywhere; V calls
  reported in audit columns at G-scale weight per D9).
- Gate: FULL beats BOTH with CIs excluding 0. Tie either → register dead →
  write the negative up (brief H2 kill criterion).
- Verifier staleness: V-v2b AUROC on FULL's executed candidates vs 0.795;
  drop > 0.05 → refresh V from current-policy rollouts before trusting H2
  numbers (brief §2/§8).
- Register diagnostics: RegisterHealth over FULL trajectories; final-r
  variance across problems (rgr/register/diagnostics.py). If collapsed
  (deltas→0), D4's revisit clause fires (try learned-constant r_0 as debug).

## Known risks (pre-named)

- Imitation signal too weak at 1.5B (register can only re-route within G's
  competence, brief §8) → H2 may honestly fail; that is a result, not a bug.
- Soft-prompt gradient through 4-bit G: bitsandbytes supports input-embedding
  gradients; if numerically unstable, fall back to bf16 G for the training
  kernel only (fits T4 at 1.5B with batch 2–4).
- Teacher-forced target tokenization must reuse generator/formatting.py
  prompt template exactly (same as generation-time; see embed_candidate for
  the precedent).
- Kaggle 9h cap: phase2_full at ~5.5h has margin; if FULL steps run long,
  resume logic (JSONL per problem) already exists in the phase-0 lock script —
  reuse that pattern.
