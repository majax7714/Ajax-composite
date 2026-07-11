# Decisions

Resolutions of the open decisions in §9 of the [build brief](build-brief.md), plus
infrastructure decisions made during scaffolding. Each entry states the decision,
the consequence, and what would cause us to revisit it. Decisions are frozen for
Phase 0–3; revisiting one mid-phase requires an explicit entry here explaining why.

---

## D1 — Register width and soft-prompt width: `d_r = 128`, `k = 8`

Per the brief's recommendation. Sweep only after the loop demonstrably works
(post-Phase 2), and sweep on MBPP validation, never on HumanEval.

## D2 — Register-update training regime: imitation first

U, the injection projection, and the r_0 encoder are trained by imitation toward
register trajectories that led to passing candidates (regime (a) in §2 of the
brief). RL over the loop (regime (b)) is deferred until imitation produces a
working loop. G stays frozen throughout Phases 0–3.

*Revisit if:* imitation targets prove too sparse (too few passing trajectories to
imitate) — then consider verifier-score-shaped RL, but only after documenting the
sparsity numbers here.

## D3 — Verifier is register-blind in v1

V scores `P(correct | problem, candidate)` — it does **not** see `r_t` in the
first working version. The brief recommends the coupling ("register biases the
landscape") but flags it as a destabilizer; we take the stability. Consequence:
in v1 the register conditions *generation only*, and the "register shapes what
counts as low-energy" claim is out of scope until v2.

The coupling exists behind a config flag (`verifier.sees_register`, default
`false`) so v2 is a config change plus a V retrain, not a refactor. H1 and the
Phase-2 H2 result are evaluated register-blind; any register-conditioned V is a
separate, later comparison.

## D4 — `r_0` is problem-encoded (deviation from the brief's lean)

`r_0 = W_0 · pool(G_hidden(problem))` — a learned linear projection of the frozen
generator's mean-pooled last-layer hidden states over the problem tokens. No
separate encoder model.

The brief notes a learned-constant r_0 makes the H2 ablation purer. Choosing
problem-encoding instead forces one design change to keep the claim exact:

**The ablation is *freeze r at r_0(problem)*, not zero-r.** With r frozen, every
step's generation is i.i.d. conditioned on `r_0`, so the loop collapses to
best-of-n — but only if B1 *also* conditions on the frozen `r_0`. Therefore:

- **B1** is defined as the FULL loop with `freeze_register = true` (and no early
  stop). In code they are literally the same function with a flag — see
  `rgr.loop.refine`. The H2 claim tested is precisely: *register **updates** are
  the only cross-step channel, and they carry load.*
- **B1′** (secondary control, no injection at all) isolates the *static*
  contribution of `r_0`-conditioning versus the vanilla model. B1′ is reported
  but does not gate H2.

*Revisit if:* register diagnostics show `r_t` never moves away from `r_0`
(update collapse) — a learned-constant r_0 would then be the cheaper debug.

## D5 — Stop rule: fixed threshold τ

Fixed τ, selected on MBPP validation before Phase 3 evaluation, then frozen.
Learned/annealed stopping is post-H3 work.

## D6 — Model: Qwen2.5-Coder-1.5B-Instruct, 4-bit, frozen

Per §7. No LoRA on G in v1 — the trainable surface is exactly {injection
projection, r_0 projection, U, V}. Scaling to the 4B QLoRA setup happens only
after Phase 2 passes.

## D7 — Feature extractor φ and verifier architecture (v1)

`φ(text) = mean-pool of G's last-layer hidden states` over the text's tokens,
computed with the same frozen G (no second encoder to version or drift).
V-v1 is an MLP over `[φ(problem); φ(candidate)]` with a sigmoid head; auxiliary
heads for `frac_tests_passed` and error type sharpen the score (§2). If H1 is
marginal with pooled features, V-v2 is a small fine-tuned encoder over raw text —
that escalation is pre-authorized by the brief's "verifier quality is the
ballgame" and does not need a new decision entry.

## D8 — Infrastructure choices

- **Configs are TOML** (stdlib `tomllib`) — zero-dependency parsing so config and
  all pure-logic code runs on a bare Python, keeping the verdict-deciding code
  testable everywhere.
- **Pure-stdlib core:** loop control flow, compute ledger, pass@k, calibration
  metrics, and bootstrap are dependency-free and unit-tested. Torch appears only
  inside `generator/`, `register/`, `verifier/` model internals.
- **Execution safety:** the only sanctioned backend is the Daytona sandbox. A
  local subprocess backend exists for smoke tests on trusted toy problems and
  refuses to run unless `RGR_ALLOW_LOCAL_EXEC=1` is set explicitly.
- **Compute accounting** is specified in [COMPUTE_ACCOUNTING.md](COMPUTE_ACCOUNTING.md)
  and frozen before any comparison run, per §8 of the brief.
- **Split discipline:** HumanEval/HumanEval+ never touch training, tuning, or
  threshold selection. All tuning happens on MBPP validation. Enforced by
  `rgr.data.splits` refusing to hand HumanEval to any training-tagged consumer.

## D9 — Verifier of record: V-v2b (QLoRA cross-encoder), superseding D7's V-v1

V-v1's pooled-phi features hit a measured ceiling (in-domain probe loses to
raw likelihood) and codebert-base was too weak on val. The verifier of record
is a 4-bit QLoRA classifier on Qwen2.5-Coder-1.5B-Instruct (LoRA r16 on
attention + trainable head) over raw `(problem, candidate code)` text,
val-selected. Consequences:

- **V inference costs a G-scale forward pass** (~1.5B), not an MLP — the
  compute-accounting audit columns must count V calls at this weight in
  Phase ≥ 2 (the primary budgeted unit is unchanged: candidate generations;
  one V forward ≈ 1/150th of a 156-token generation, still secondary).
- phi features stay for U's candidate input (register update), where the
  frozen pooled representation is an input signal, not the verdict.
- The aux heads (frac_tests, error_type) were not needed to pass H1; adding
  them to v2b is open Phase-2 work if the loop wants a denser reward.

## D10 — Imitation regime, concretely: likelihood steering on synthesized prefixes

D2 said "imitation first" but left the objective abstract; with V
register-blind (D3) there is no differentiable V→register path, and imitating
"register trajectories that led to passes" is vacuous when the initial modules
are random. The implemented objective (rgr/training/imitation.py,
scripts/phase2_register_loop.py --train):

sample k failed candidates from the Phase-1 label set as a prefix, unroll
r_k = U(...U(r_0, phi(c_1), v_1)..., phi(c_k), v_k), and minimize
teacher-forced -log P_G(passing candidate | prompt, soft(r_k)) with G frozen.
Prefix v scores come from V-v2b (phase2_score kernel) so training sees the
inference-time score distribution. Round 1 reuses Phase-1 data — no new
rollouts. k=0 examples train pure r_0 steering; k>0 trains failure
integration, which is exactly the cross-step-learning claim.

*Revisit if:* trained modules don't reduce val teacher-forced loss vs the
untrained baseline (logged in register_modules.pt), or H2 shows the steering
signal doesn't survive sampling.
