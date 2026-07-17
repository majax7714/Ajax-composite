# Register-Gated Refinement (RGR) — Build Brief

> **Status note (2026-07-17, appended — content below unrevised):** Historical.
> This brief specifies the original RGR experiment (Phases 0–2). The claim it
> defines was killed by its own pre-registered gate (H2 FAIL, 2026-07-12); the
> brief remains the frozen spec of record for §§1–5 of the journal. Current
> entry point: [WRITEUP-rgr.md](WRITEUP-rgr.md) and the repository README.

*Working title; rename to taste. `RGR` abbreviates cleanly and stays descriptive.*

---

## 0. What this is, and what it deliberately is not

This is a minimal, falsifiable experiment for one claim: **an explicit internal state vector — a "register" — that gates generation and is updated across refinement steps improves calibration and correctness beyond what verification-plus-iteration already buys you.** That claim is the functional core of the architecture we converged on. Everything else in that architecture (non-autoregressive joint settling over tokens, energy-based latent relaxation from scratch) is either unsolved at scale or already exists in the literature, so we are not building it here. We are isolating the one piece that is *yours* and testing whether it carries load.

Concretely, we are **not**:
- building a from-scratch energy-based or diffusion language model (unstable, multi-year, not the point),
- claiming any substrate/constitution property — this is a frankly functional stand-in, and we should say so in the paper,
- trying to beat SOTA code models. We are testing a *mechanism*, on a small model, where a null result is still informative.

The whole design is arranged so that the central ablation is clean: **the register is the only channel that carries information across refinement steps.** If performance improves across steps and that improvement vanishes when we ablate the register, the improvement is attributable to the register and to nothing else. That is the entire experimental point.

---

## 1. The three claims, as kill-able hypotheses

Each has a pre-committed kill criterion. If the criterion fires, that claim is dead and we say so rather than rescuing it.

**H1 — External consistency beats self-fluency as a confidence signal.**
A learned verifier scoring `(problem, candidate)` against execution-grounded labels ranks correct-above-incorrect better than the generator's own token log-likelihood.
- *Metric:* AUROC of confidence → correctness; secondary ECE, Brier.
- *Kill:* verifier AUROC does not exceed likelihood AUROC by a meaningful margin on held-out problems. If confidence can't be made trustworthy, the rest of the loop is built on sand — stop here.

**H2 — The register carries functional load (the novel claim).**
Register-gated iterative refinement beats verifier-reranked best-of-n *and* in-context iterative refinement, **at matched compute**.
- *Metric:* pass@1 and pass@k at equal total forward passes; delta vs each baseline.
- *Kill:* FULL ties B1 and B2 within noise at matched compute. If a learned latent state adds nothing over parallel sampling or in-context feedback, the register is dead — and that is a clean, publishable negative given the BBS-adjacent framing.

**H3 — Settling depth tracks difficulty (adaptive compute).**
When the loop early-stops on verifier confidence crossing threshold τ, steps-to-stop correlates with problem difficulty, and adaptive stopping beats fixed-K at matched *average* compute.
- *Metric:* correlation(steps-to-stop, difficulty proxy); adaptive vs fixed-K pass@1 at matched mean forward passes.
- *Kill:* no correlation, or adaptive stopping fails to beat fixed-K. Weaker kill — H3 failing doesn't sink H2, it just means the adaptive-compute story isn't there yet.

Order matters. **H1 gates H2 gates H3.** Do not proceed past a failed gate by tuning until it passes; that's how you fool yourself.

---

## 2. Architecture

Four components. Keep the generator cheap (frozen or LoRA); put the trainable novelty in the small modules around it.

**G — Generator.** A small code model (start at ~1.5B, see §7). Frozen, or light LoRA. Produces a candidate solution conditioned on the problem *and* the current register `r_t`.

**r — Register.** A continuous vector (start `d_r = 128–256`), the slow variable. Initialized `r_0` (learned constant or a cheap encoding of the problem). This is the *only* state that persists and mutates across refinement steps. Functionally it is your chemical-state-gating claim: it conditions which continuations are reachable and biases what the verifier treats as low-energy, and it updates from the trajectory of the settling itself.

**U — Register update.** A small recurrent cell (GRU is fine to start): `r_{t+1} = U(r_t, φ(candidate_t), v_t)` where `φ(candidate_t)` is a pooled embedding of the current candidate (mean-pool of G's last hidden states, or a small encoder) and `v_t` is the verifier's score/features. This is where cross-step "learning within a single problem" lives.

**V — Verifier (the energy).** Predicts `P(correct | problem, candidate, r_t)`. Trained on execution-grounded labels. Its scalar output *is* the confidence that gates the loop; its negative log is your energy. Conditioning V on `r_t` too lets the register bias the landscape, not just the generation — that's the "register shapes what counts as low-energy" piece.

**Register injection (how `r_t` conditions G).** Simplest buildable path: a learned projection `r_t → k soft-prompt embeddings` prepended to G's context. Keeps G frozen, keeps the trainable surface small. FiLM-style modulation of hidden states or a cross-attention register token are richer alternatives to try later; do not start there.

### Inference loop

```
r ← r_0(problem)
for t in 0..T_max:
    candidate ← G(problem, r)          # regenerate, conditioned on register
    v ← V(problem, candidate, r)       # confidence / -energy
    if v ≥ τ: break                    # settled — adaptive stop (H3)
    r ← U(r, φ(candidate), v)          # update the slow variable
return best candidate by v
```

**Critical design choice that makes the ablation clean:** refinement = *regenerate conditioned on the updated register*, **not** edit-the-previous-candidate and **not** show-G-its-last-attempt-in-context. Under this rule, the register is the sole carrier of information from step `t` to step `t+1`. Ablate `r` (freeze it / zero it) and the loop collapses to independent samples — i.e., best-of-n. That means **your ablation and one of your baselines are the same object**, which is exactly the crispness you want.

### Training signal

- **V**: supervised on execution labels. Generate many candidates per problem across register states, run them in a sandbox against tests, label pass/fail (and richer signal — fraction of tests passed, error type — as auxiliary targets to sharpen the score).
- **U + injection + r_0**: trained so the loop reaches passing candidates in fewer steps. Two viable regimes — (a) supervised/imitation toward register trajectories that led to passes, or (b) RL over the loop with reward = execution pass, verifier score as shaped intermediate reward. Start with (a); it's stabler and you have the rollout infra. Keep G frozen initially so you're only fighting instability in the small modules.

**Watch:** V is trained on G's outputs; as U changes what G emits, V drifts stale. Plan to refresh V's training set from current-policy rollouts between phases (standard actor/critic staleness — name it so it doesn't surprise you).

---

## 3. The conceptual mapping (so the thread stays explicit)

State this in the paper plainly, as *functional* organization, not ontology:

- **Chemical-state gating of memory** → the register gating retrieval/generation. Memory is re-derived each step under the current register rather than stored-and-fetched — reconstructive in Bartlett's sense, falling out of the architecture rather than bolted on.
- **Consistency manifold / external grounding** → the execution-trained verifier. Confidence tracks correctness because it's grounded in something outside the model's own fluency.
- **Localized-Hamiltonian settling** → inference-as-relaxation with adaptive depth. Note honestly: this is energy *descent* (dissipative, we want a minimum), not conservative Hamiltonian flow — the register/verifier supply the dissipation.

Do not overclaim the substrate connection. This is the functional skeleton of the idea proven small; the constitution question is explicitly bracketed.

---

## 4. Task and data

Code, because execution gives free ground-truth verification — that's the entire reason this domain is tractable and confidence can be trusted.

- **Train:** MBPP (and MBPP+ for denser tests). You already have a Loop 1 dataset covering MBPP/xLAM — reuse it for the format-discipline layer so G reliably *emits* code rather than narrating.
- **Held-out eval:** HumanEval / HumanEval+, kept strictly out of training to avoid the contamination that makes code numbers lie.
- **Difficulty proxy for H3:** baseline single-shot pass rate per problem (cheap, model-relative), optionally cross-checked against any available human difficulty labels.

Sandbox execution: reuse your Daytona rollout harness — safe execution is non-negotiable and you already have it standing.

---

## 5. Baselines and ablations

All compared **at matched compute** (equal total forward passes / equal wall-clock). Un-matched comparisons here are worthless.

| Condition | Cross-step info | What it controls for |
|---|---|---|
| **B0** — single-shot | none | raw pass@1 floor |
| **B1** — best-of-n + verifier rerank | none (parallel) | "verification/sampling alone" — *this is also the register-ablated FULL* |
| **B2** — in-context iterative refine | prev candidate + verifier feedback in prompt | "iteration with in-context feedback alone" |
| **FULL** — register-gated refine | learned latent register only | the claim |

The two comparisons that decide H2: **FULL vs B1** (does register-carried iteration beat parallel sampling?) and **FULL vs B2** (does a learned latent state beat in-context feedback?). Tie both and the register is dead.

---

## 6. Metrics

- **Correctness:** pass@1; pass@k with the unbiased estimator; all at matched compute.
- **Calibration (H1):** AUROC(confidence → correct) primary; ECE, Brier secondary; verifier vs likelihood head-to-head.
- **Register load (H2):** pass@k deltas FULL−B1, FULL−B2, with CIs over problem-level bootstrap.
- **Adaptive compute (H3):** corr(steps-to-stop, difficulty); adaptive-vs-fixed-K pass@1 at matched mean forward passes; a compute–accuracy Pareto curve.
- **Diagnostics:** register trajectory norms/variance (is it moving or collapsing?), steps-to-settle distribution, verifier staleness (V accuracy on current-policy rollouts over time).

---

## 7. Compute and infra

- **Model:** start **small — ~1.5B code model** (e.g. a Qwen2.5-Coder-class 1.5B). The experiment is about the mechanism; a small model iterates the loop far faster and a mechanism that helps a small model is the cleaner result. Scale to your 4B QLoRA setup only after the loop demonstrably works.
- **Where:** 4-bit inference of a 1.5–4B model fits a single T4/P100 — your Kaggle PEFT/QLoRA pipeline covers training the small modules and LoRA. The expensive line item is *label generation* (many sandboxed executions), not training — budget for that.
- **Your 8600G iGPU** is fine for orchestration/analysis, not for the training loop. Keep training on Kaggle/rented GPU; keep the harness and dashboards local.
- **Baseline discipline:** lock a pre-training dashboard baseline before any RGR training — same move you made for the QLoRA runs. B0/B1 numbers frozen first, everything measured as delta against them.

---

## 8. Known hard parts (the honest list)

- **Verifier quality is the ballgame.** A weak V makes the whole loop chase a bad gradient. If H1 is marginal, everything downstream is suspect. This is the highest risk and it's front-loaded on purpose.
- **Register dynamics can collapse or run away.** A live recurrent state in the loop wants to degenerate (norm blow-up, collapse to constant). Expect to spend most of your time here: normalization on `r`, update-magnitude clipping, spectral care on U.
- **Verifier staleness under a moving generator** — the actor/critic drift noted in §2. Refresh V between phases.
- **Matched-compute accounting is fiddly and easy to get wrong** in a way that flatters FULL. Decide the accounting rule *before* running, write it down, don't touch it.
- **Small-model ceiling:** a 1.5B model may fail problems no amount of settling fixes — the register can only re-route within the model's competence. Read H2 as *delta at matched compute*, not absolute pass rate.

---

## 9. Open decisions to settle before Phase 1

These are genuinely yours to make; I'd resolve them explicitly rather than drift into defaults:

1. **`d_r` and `k` (soft-prompt width).** Start 128 / 8; sweep later.
2. **U training regime:** imitation (a) first, RL (b) later — confirm you want to start conservative.
3. **Does V see `r_t`?** Recommended yes (register biases the landscape), but it adds a coupling that can destabilize — you may want V register-blind for the first working version, then add the coupling.
4. **`r_0`:** learned constant vs problem-encoded. Problem-encoded is richer but muddies the "register carries *cross-step* info" story — a learned constant makes the ablation purer for H2.
5. **Stop rule τ:** fixed threshold vs learned/annealed. Fixed first.

---

## 10. Phase plan with gates

**Phase 0 — Harness (no learning yet).**
Dataset splits wired; Daytona execution sandbox returning clean pass/fail; B0 single-shot and B1 best-of-n numbers locked on held-out. Format-discipline layer confirmed (G emits code, doesn't narrate). *Gate: reproducible baseline pass@1 on the dashboard.*

**Phase 1 — Verifier (tests H1).**
Generate labeled candidates, train V, compare V vs likelihood on calibration. No register yet. *Gate: V AUROC clears likelihood by a real margin. If not — stop and fix confidence before building the loop.*

**Phase 2 — Register loop (tests H2, the core).**
Add r, U, injection; train the small modules with G frozen. Run FULL vs B1 vs B2 at matched compute. *Gate: FULL beats both baselines. This is the result the paper lives or dies on.*

**Phase 3 — Adaptive compute (tests H3).**
Add τ early-stopping; measure depth-vs-difficulty and the compute Pareto. *Gate: adaptive beats fixed-K at matched mean compute.*

Only after all three: scale model size, richer injection (FiLM/cross-attn), RL register training.

---

## 11. First concrete steps (start here)

1. Pin the small code model and confirm 4-bit inference + your format-discipline layer produce clean, executable code on 20 MBPP problems by hand.
2. Stand up the Daytona execution wrapper: `(problem, candidate) → {pass, frac_tests, error_type}`.
3. Lock B0 and B1 on the HumanEval held-out set. Freeze those numbers on the dashboard.
4. Generate the first V training set (candidates × execution labels), train a small V, and run the *single* comparison that gates everything: **V AUROC vs likelihood AUROC.**

If step 4 comes back positive, you have earned the right to build the register. If it comes back flat, you've learned the cheapest possible version of the most important thing, and you fix confidence before spending a week on register dynamics.

---

*This is a starting scaffold, not a spec — §9 is deliberately unresolved so the design decisions stay yours.*
