# Pre-B2 handoff — post-mortem, frozen B2 spec, and the diagnostics that
# decide what the H2 null means

*Committed 2026-07-12, **before B2 has run**. Everything in §3 (branch
interpretation of B2) and §4 (diagnostic predictions) is pre-registered: the
interpretations and predictions are written down now so they cannot be
retrofitted to whatever numbers come back. Append outcomes; never revise the
predictions. This document is the source of truth for the post-H2-gate plan;
[PHASES.md] carries the one-line-per-run log, [DIAGNOSTICS.md] carries the
per-diagnostic results as they land.*

---

## 0. What this plan is, and what it is not

The H2 gate fired. Register-gated refinement (FULL) tied its own ablation (B1)
**exactly** — pass@1 0.6829 vs 0.6829, Δ = 0.0000, CI [−0.0488, +0.0549]
([artifacts/h2_result.json], [PHASES.md] Phase-2 gate). Under the pre-committed
kill criterion ([build-brief.md] §1) the register claim is **dead at this scale
and training regime**. That verdict is final and is *not* reopened by anything
below.

This plan is **not**: a rescue of the register, a retune of any Phase-2
component, or a modification of B2 in any respect.

This plan **is**: (a) run B2 exactly as pre-registered, and (b) run four
diagnostics that determine *what the null means*. The distinction matters
because the post-mortem (§1) concludes the null was likely **over-determined by
design choices upstream of the register itself**. The register may be dead; it
may also simply never have been on trial. B2 plus the diagnostics discriminate
between those, and they point to completely different next experiments (§5).

---

## 1. Post-mortem — the null was probably over-determined

The writeup ([WRITEUP.md] Abstract, §4.3) currently frames the result as *"every
link in the chain worked except the last one."* That framing is probably wrong.
Three links were likely broken before the last one, and two were baked into the
original build brief. **This section is a hypothesis, not a finding** — DIAG-1
and DIAG-4 (§4) are what confirm or refute it; until they run, the writeup's
"every link worked" line stands as written and is flagged, not edited.

### 1.1 The task had almost no refinement headroom

pass@8 = 0.8415 on HumanEval; verifier-selected pass@1 = 0.6829 = 112/164;
oracle at n=8 = 138/164.

- ~26 problems: a correct candidate exists in the pool, the verifier picks wrong
  (a **selection** failure).
- ~26 problems: the pool contains nothing correct (a **generation** failure).

Refinement's entire purpose is to reach solutions the model would not otherwise
sample — i.e. to fix the second category, which is ~16% of the benchmark. The
domain was chosen because execution gives clean verification: correct for H1,
wrong for H2. It optimized the control (verification) and starved the treatment
(generative steering), on a benchmark already ~84% saturated at the pool level.

### 1.2 The register was fed a representation already measured near-chance

The sharpest point, and the evidence is inside our own writeup. V-v1 (MLP over
mean-pooled frozen-G `[φ(problem); φ(candidate)]`) failed H1 with within-problem
macro AUROC 0.579 (near chance); an in-domain probe on those features reaches
only 0.642, losing to raw likelihood ([WRITEUP.md] §4.2, [PHASES.md] Phase-1).

Now look at the update rule: `r_{t+1} = U(r_t, φ(candidate_t), v_t)`. The input
`φ(candidate_t)` is *the exact representation we proved carries almost no
within-problem correctness signal*. The only correctness-bearing input to the
register is the scalar `v_t`. Across 8 steps the register receives at most ~8
scalars of real information plus a stream of chance-level features. The V-v1
failure predicted the H2 failure. We fixed the verifier by fine-tuning the
representation end-to-end (V-v2b); we never fixed **U's input**.

Worse: the execution driver returns `{passed, frac_tests, error_type}` with
per-test granularity — the richest diagnostic channel in the system — and it fed
V's *training labels* but never entered the *loop*. The register was not
bandwidth-limited at d_r = 128; it was **starved at the input**.

### 1.3 The training objective was exponentially disconnected from the goal

Val teacher-forced loss 0.1713 → 0.1530 (−10.7%). If that is mean NLL per token
at ~156 tokens/candidate, the sequence probability of the target went from
≈ exp(−26.7) ≈ 3e-12 to ≈ exp(−23.9) ≈ 4e-11 — a 13× improvement, from
unsamplable to unsamplable. Mean-per-token NLL is dominated by boilerplate the
prefix already supplies (`def`, indentation, argument names); the handful of
tokens where the algorithm is chosen barely move the average.

Add: the register was trained **off-policy** (prefixes unrolled over Phase-1
candidates sampled *without* register conditioning), and V is register-blind so
there is no V→r gradient path at all (D3, D10). The register never received a
single gradient from an execution outcome under its own sampling distribution.

### 1.4 Root cause

The constraint *"refinement = regenerate under the updated register, nothing else
carried across steps"* bought an exact ablation (**the ablation IS the baseline**
— genuinely the best feature of the design) at the cost of strangling the
mechanism's information channel down to a scalar plus a chance-level feature,
pushed through 8 soft tokens, trained off-policy on a proxy objective, on a task
with ~16% generative headroom. The failure is beautifully *attributed*. It was
also close to *predetermined*.

---

## 2. B2 — FROZEN. Do not modify.

B2 runs exactly as pre-registered in [build-brief.md] §5 and
[COMPUTE_ACCOUNTING.md]. No changes of any kind. Verified against the code and
configs on 2026-07-12:

| Frozen parameter | Value | Source of record |
|---|---|---|
| Generations/problem (N) | 8 (initial + 7 revisions) | `loop.t_max = 8` / `baselines.n = 8` [configs/base.toml] |
| Decoding | temp 0.8, top-p 0.95, max 512 new tok, seed 17 | [configs/base.toml] |
| G | Qwen2.5-Coder-1.5B-Instruct, 4-bit, frozen | D6 |
| V (selection) | V-v2b, register-blind | D3, D9 |
| Cross-step channel | previous candidate + verifier score in the prompt | `run_b2` ([rgr/loop/baselines.py]) |
| Held-out set | HumanEval, 164, checksum-pinned | [rgr/data/splits.py] |
| Code path | `phase2_register_loop.py --b2` → `run_comparison(["b2"], "b2")` | writes `runs/phase2/b2.jsonl` |

**Do not** add error traces, test feedback, or `error_type` to B2's prompt —
however tempting, and however much §1.2 argues that feedback is what makes
iteration work. That is a different experiment (§5). B2's entire value is being
the thing we pre-registered. If B2 as specified looks weak: good, that is
informative — note the concern in the run log, do not act on it. Any deviation
destroys the only thing B2 is for.

---

## 3. Pre-registered interpretation of B2 (committed now, before the number)

B2 is not bookkeeping. B2 determines what the H2 null *means*. The branch verdict
is written now:

**Branch A — B2 also ties B1 (within CI).**
→ Cross-step information *of any kind* — including raw text, the highest-bandwidth
channel a transformer has — buys nothing in this setting. Then the H2 null says
nothing about registers; it says *this task at this scale has no iteration
headroom*, exactly as pass@8 = 0.8415 predicts. The experiment was uninformative
about the actual hypothesis. **Next step is task redesign (§5), not an
architecture change.**

**Branch B — B2 beats B1 (CI excludes 0).**
→ Iteration *does* pay here, and a 128-dim latent through 8 soft tokens lost to
putting the previous attempt in the context window. Sharper and more interesting:
in a transformer, a latent register competes against in-context text, and text is
the channel the architecture was built to condition on. The register would be
**architecturally parasitic** — dominated by a mechanism the substrate already
optimizes for. **Next step is an architecture-level rethink, not a task change.**

**Standing prediction (recorded 2026-07-12): Branch A, ~65/35.** Rationale:
pass@8 = 0.84 leaves little for iteration to do, and the self-correction
literature is consistent that models do not reliably self-correct without
external feedback — which B2, as specified, does not receive.

> Whichever branch fires, this section is not revised afterward. The outcome is
> **appended** below; the prediction is **left standing, right or wrong.**

**B2 OUTCOME: _pending_.** (To append: B2 pass@1, Δ(B2−B1) with CI, branch fired,
prediction held? — one line, no edits above.)

---

## 4. Diagnostics — what the null means

**Integrity constraints (read before running any diagnostic):**

- These are **EXPLORATORY / POST-HOC**, not confirmatory. They analyze data from
  an already-revealed held-out evaluation. Label every result as such in its
  artifact. They **may not** reopen the H2 verdict, and **may not** become a
  claim that the register "would have worked if."
- **Held-out hygiene.** DIAG-1 and DIAG-4 are pure re-analysis of existing
  Phase-0/Phase-2 artifacts — no new HumanEval access, no new peek. DIAG-2 and
  DIAG-3 run on **MBPP val, not HumanEval**, precisely so they cost nothing
  against held-out. Do not touch HumanEval for them.
- **Priority under GPU quota.** DIAG-1 and DIAG-4 are CPU-first and free — run
  them first. **B2 has first claim on GPU quota.** DIAG-2 (probe training, cheap)
  and DIAG-3 (needs generation) run after B2.

Predictions below are pre-registered. Report predictions-vs-outcomes honestly,
including the ones recorded here — they are on the record specifically so they
can be wrong.

### DIAG-1 — Did the register ever *generate* anything? (CPU, free, run first)

The decisive one. FULL and B1 have symmetric disagreements: 9 FULL-only wins,
9 B1-only wins. The question is whether FULL's wins are real steering or pure
resampling noise.

**Procedure.** From `runs/phase2/full_b1.jsonl` and Phase-0 oracle coverage
(`artifacts/lock_a.jsonl`, `artifacts/phase0_difficulty_proxy.csv`), for every
problem compute per-condition oracle pool coverage (did any of the 8 candidates
pass?). Then stratify:

1. Of the 9 FULL-only wins: how many had B1's own pool containing ≥1 passing
   candidate (B1 had the answer, verifier mis-selected)?
2. Of the 9 FULL-only wins: how many had B1's pool containing **zero** passing
   candidates — i.e. FULL reached a solution B1's sampling could not?
3. Same stratification for the 9 B1-only wins (symmetry control).
4. Of the ~26 problems where the Phase-0 oracle pool is empty (pass@8 = 0), how
   many did FULL solve? How many did B1?

**Interpretation (committed).** If (2) = 0 and (4) shows FULL solving zero
oracle-empty problems, the register's generative effect is *exactly zero, not
merely unmeasurable* — every FULL "win" is the verifier picking differently among
candidates B1 also had. That is strictly stronger than the current null and
belongs in the paper.

**Prediction:** (2) = 0 or 1; FULL solves 0 of the oracle-empty problems.

**Output:** `artifacts/diag1_oracle_stratification.json` + a 4-row table.
**Readiness:** all inputs committed; CPU-runnable now.

### DIAG-2 — Encoding failure or transmission failure? (MBPP val, cheap GPU, after B2)

The current experiment cannot distinguish two failure modes with opposite fixes:
(a) `r_t` encodes nothing useful (input starvation, §1.2), or (b) `r_t` encodes
fine but the soft-prompt channel cannot transmit it to G (authority failure).

**Procedure.** On **MBPP val**, roll out FULL and store trajectories r_0 … r_7.
Train small linear/MLP probes from `r_t` to predict:

- `v_{t-1}` (previous verifier score) — regression, report R².
- `passed_{t-1}` (binary) — report AUROC.
- `error_type_{t-1}` (categorical) — macro-F1 vs a majority baseline.
- (control) `t` itself — if only this is decodable, the register is a step counter.

**Interpretation (committed).**
- Probes at chance → **encoding failure**: the register is starved at the input;
  d_r, GRU, and injection are all exonerated. Fix is `error_type` / failing-test
  IDs / a fine-tuned candidate encoder into U.
- Probes succeed but per-step pass rate stays flat → **transmission failure**:
  the register knows things it cannot say. Fix is injection bandwidth/authority.
- Only `t` decodable → the register learned a clock.

**Prediction:** `passed_{t-1}` AUROC ≈ 0.55–0.65 (weak); `t` strongly decodable.
I.e. mostly encoding failure with a clock.

**Output:** `artifacts/diag2_register_probes.json`.
**Readiness:** needs a **new Kaggle kernel** (MBPP-val FULL rollout + trajectory
dump; probes train on CPU from the dump). Not built yet.

### DIAG-3 — Control authority: does `r` move G's sampling at all? (MBPP val, GPU, after B2)

The flat per-step pass rate (0.60, 0.62, 0.61, 0.61, 0.57, 0.58, 0.60, 0.62) and
near-uniform argmax position (29/18/22/18/21/12/21/23) already suggest `r` has
~zero causal effect on G. Quantify it — arguably more publishable than the H2
null itself.

**Procedure.** On **MBPP val**, per problem: sample 8 candidates conditioned on
`r_0`, and 8 conditioned on a well-updated `r_7` (from a FULL rollout on that
problem). Compute:

- Mean pairwise normalized edit distance within-`r_0`, within-`r_7`, and
  across the two sets. If across ≈ within, `r` is not changing what G writes.
- Pass-rate difference between the two sets (CI).
- Token-level KL between next-token distributions under `r_0` vs `r_7` soft
  prompts, at the first 32 generated positions, averaged over problems.
- (headline) an explicit statement: *"8 soft-prompt embeddings driven by a
  128-dim register shift G's sampled distribution by ⟨X⟩."*

**Prediction:** across-set edit distance statistically indistinguishable from
within-set; mean KL small (< 0.05 nats); pass-rate difference CI straddles 0.

**Output:** `artifacts/diag3_control_authority.json`.
**Readiness:** needs a **new Kaggle kernel** (r_0-vs-r_7 paired sampling on MBPP
val + KL/edit-distance instrumentation). Not built yet.

### DIAG-4 — Settle the training-objective units (CPU-first, free, run first)

Cheap; closes §1.3 definitively.

**Procedure.** From the Phase-2 training kernel (`rgr-phase2-train`), confirm
whether 0.1713 / 0.1530 is mean NLL per token or a sum/other normalization.
Then, on the Phase-2 val targets, compute for the target passing candidate:

1. Mean per-token NLL, untrained vs trained (should reproduce the numbers).
2. Implied sequence-level log-prob and probability, untrained vs trained, at the
   **actual per-candidate token counts** (do NOT use the 156-token average — use
   real lengths).
3. The entropy profile: per-position NLL split into low-entropy tokens
   (boilerplate the model already predicts) vs high-entropy tokens (algorithmic
   decision points). How much of the −10.7% came from each?

**Interpretation (committed).** If the improvement concentrates in low-entropy
tokens *and* the sequence probability of the target stays < 1e-9 after training,
§1.3 is confirmed: we optimized a quantity with no mechanical route to changing
sampling behavior, and the writeup's *"training was not a no-op"* line must be
restated as *"training moved a proxy that cannot move the objective."*

**Prediction:** > 80% of the loss improvement sits on low-entropy tokens;
post-training sequence probability of the target stays below 1e-9.

**Output:** `artifacts/diag4_objective_units.json`.
**Readiness:** units-confirmation (code inspection: HF `out.loss` on masked
labels = mean per-token NLL — confirmed) and the implied-sequence-prob
computation (aggregate loss × real token counts from `phase1_labels.jsonl`,
CPU tokenizer) are CPU-free and runnable now. **The entropy-split sub-part (item
3) needs a small GPU forward pass** over the ~240 val targets with/without the
trained soft prompt — per-token NLLs were never logged during training. Items
1–2 (which carry the pre-registered "< 1e-9" claim) do not depend on the GPU
sub-part.

---

## 5. Explicitly out of scope for this plan (the *next* experiments)

Recorded here so they do not leak into the runs above. Which of these is even
worth doing depends entirely on whether B2 lands in **Branch A** or **Branch B**
(§3). Do not start any until B2 and DIAG-1..4 are in.

- Feeding `error_type` / failing-test IDs / tracebacks into U (fixes §1.2 input
  starvation).
- On-policy training of the register (GRPO with execution reward; regime (b) of
  D2).
- A register-conditioned verifier (D3's deferred coupling; `verifier.sees_register`),
  restoring a V→r gradient path.
- Higher-authority injection (FiLM, cross-attention, KV-prefix, r-modulated LoRA)
  in place of 8 soft tokens.
- A task with genuine generative headroom (competition-level problems, or the
  pass@8 = 0 stratum where refinement must *generate*, not select).
- **Verifier-first work:** oracle 0.842 vs achieved 0.683 — ~17 points of
  headroom sit in the verifier, independent of any loop. This is where the
  measured load actually is.

---

## 6. Deliverables and readiness (2026-07-12)

**Deliverables (produced as the runs complete):**

1. `artifacts/h2_b2_result.json` — B2, run to the frozen spec, ledger-verified.
   The [WRITEUP.md] §4.3 table row filled in, and §5.3 replaced with the Branch
   A/B verdict from §3 (prediction left standing).
2. `artifacts/diag1..diag4_*.json` + [DIAGNOSTICS.md] — one paragraph per
   diagnostic: procedure, number, and whether the committed prediction held.
3. One line per run in [PHASES.md], with dates, per the existing gate-log
   convention.

**Readiness status:**

| Item | State | Blocker / note |
|---|---|---|
| B2 run | **launch-ready** | `phase2_b2` mode wired; config frozen; all bundle artifacts present. Launch: `kaggle_launch.py bundle` → `launch phase2_b2` → fetch → `--h2`. |
| B2 result file | **plumbing gap** | `--h2` writes `artifacts/h2_result.json` (overwrites the FULL-vs-B1 verdict, now with `delta_b2` filled). Deliverable names `artifacts/h2_b2_result.json`. Resolve by an analysis-only step (copy the regenerated file, or one extra `json.dump`) — **does not touch B2's frozen run.** |
| DIAG-1 | **CPU-runnable now** | inputs committed. |
| DIAG-4 (items 1–2) | **CPU-runnable now** | units confirmed by code inspection. |
| DIAG-4 (item 3) | **needs GPU** | per-token NLLs unlogged; small forward pass over ~240 val targets. |
| DIAG-2 | **needs new kernel** | MBPP-val FULL rollout + trajectory dump; then CPU probes. |
| DIAG-3 | **needs new kernel** | r_0-vs-r_7 paired MBPP-val sampling + KL/edit instrumentation. |

**Sequencing:** (1) commit this pre-registration + [DIAGNOSTICS.md] scaffold
[done 2026-07-12]. (2) DIAG-1 and DIAG-4 items 1–2 on CPU, first. (3) B2 on GPU
(first claim on quota). (4) DIAG-2, DIAG-3, DIAG-4 item 3 after B2. (5) Append
outcomes to §3 here, to [DIAGNOSTICS.md], and the [PHASES.md] log; then the
writeup edits per §6 deliverable 1.

---

*Appendix pointers: kill criteria [build-brief.md] §1; frozen accounting
[COMPUTE_ACCOUNTING.md]; decisions D1–D10 [DECISIONS.md]; the H2 verdict
[WRITEUP.md] §4.3 + [artifacts/h2_result.json]; gate log [PHASES.md].*
