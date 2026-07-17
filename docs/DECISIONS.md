# Decisions

> **Status note (2026-07-17, appended — content below unrevised):** Covers
> D1–D14 (Phases 0–M, including the D14 statistical-reproducibility standard,
> still in force). From Phase 3 on, decisions are recorded in the phase
> charters (PHASE_3*.md, PHASE_4.md, PHASE_5.md) and indexed in the journal.

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

*Post-hoc note (2026-07-12, after the H2 null + DIAG-4):* the imitation-first call
was probably the wrong starting choice, for a reason we could not see going in.
The implemented objective `−log P(specific passing candidate)` is a
**string-reproduction** objective; the goal is P(any passing program), a
**set-membership** objective. DIAG-4 caught them coming apart: a 1.7× teacher-forced
gain on specific strings produced exactly 0.0000 sampled pass@1 movement — the
signature of a string→class generalization gap. RL with execution reward (regime
(b)) optimizes set membership directly. So D2(a) bought stability at the cost of
optimizing the wrong object; the next register experiment should *start* from
regime (b), not extend imitation. This does not retro-change what was run — it
records why the starting call was likely wrong. See [PRE-B2-HANDOFF.md] §1.3 and
[DIAGNOSTICS.md] DIAG-4 / DIAG-5.

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

## D11 — Generator precision on the migrated stack: **SETTLED at M0 → half precision (bf16 on L4)** (2026-07-13)

**Decision (M0, 2026-07-13):** drop 4-bit NF4; run G in **half precision** —
**bf16 on the L4 target** (Ada/sm89 supports it; use fp16 only if a run ever lands
on a Turing/sm75 T4). Full prior context in [PHASE_M.md] §3, §7.

**Reasoning.** 4-bit NF4 (D6) was inherited from the 4B QLoRA work where it was
correct; at 1.5B it never was — fp16 weights are ~3.1 GB against L4's 24 GB, so we
were never memory-constrained, and NF4 dequantizes every forward pass, costing 2–4×
throughput and degrading the generator the entire experiment depends on. Phase 3
([PHASE_3.md]) makes throughput load-bearing (large-k pass@k screen at k=50, more
conditions, on-policy GRPO rollouts), so the throughput win is no longer optional.

**Accepted consequences.** (i) **M4 verifier revalidation** — V-v2b was trained on
4-bit-generated candidates; half precision shifts the candidate distribution
underneath V (a *substrate* change, not actor drift), so V is revalidated and
retrained if AUROC degrades vs the recorded 0.7951/0.7189. (ii) All baselines
**re-lock** on the new stack (M3/M5); no post-migration number is ever compared to a
pre-migration one. (iii) Cheaper than it looks: Phase 3 re-locks baselines on a new
benchmark regardless (3a), so the migration is nearly free.

*Gate status:* §0 of [PHASE_M.md] is **green** — B2 + all diagnostics (DIAG-1..11)
closed on the old stack, record committed. Settled here at M0, not before.

## D12 — DIAG-6 descoped from the diagnostic record (2026-07-12)

DIAG-6 (large-k pass@k, k ≈ 50–100, on the 26 oracle-empty HumanEval problems —
the headroom ceiling) is **descoped**, not run on the current stack. Reasoning:
it is the most expensive remaining item (~$3.30, vs < $1 for all other GPU
diagnostics combined) and now largely **redundant** — its finding (the refinement
headroom ceiling is low) is already carried by pass@8 = 0.8415 plus DIAG-1's
resampling recovery (3–5 of 26 dissolve) plus DIAG-7's pool-coverage account, and
the task is being redesigned regardless. The same measurement is worth far more
pointed at a *useful* question: it folds into **Phase 3's benchmark-selection
screen** (choose a benchmark with genuine generative headroom), where large-k
pass@k is the natural instrument. Not dropped — relocated.

*Revisit if:* Phase 3 benchmark selection needs the ceiling on the *current*
HumanEval set specifically (unlikely — Phase 3 changes the benchmark).

## D13 — HumanEval reclassified from held-out to dev set (2026-07-13)

HumanEval has now been **peeked** for B0, B1, FULL, B2, and seven diagnostics
(DIAG-1/5/7/7b/8/9 read its candidates; DIAG-10 will generate on it). As a
held-out confirmatory set it is **burned** — no honest confirmatory claim can rest
on it again. Rather than pretend otherwise, it is **explicitly reclassified as a
dev set** from 2026-07-13: free to iterate on, including DIAG-10's new generation,
because nothing confirmatory is being claimed from it.

**Consequence for Phase 3:** a *fresh* held-out benchmark is required regardless of
this decision (Phase 3 also needs a task with genuine generative headroom — pass@8
here is 0.84, [DIAGNOSTICS.md] DIAG-1/7 — so HumanEval fails the headroom screen
too). Candidate fresh sets to select at Phase-3 design: MBPP+/EvalPlus test split,
LiveCodeBench, or a contamination-controlled slice. The dev/test split is to be
frozen at Phase-3 design before any generation on the new test set.

*This is what makes DIAG-10 cheap and honest:* it runs on HumanEval-as-dev, spends
no confirmatory budget, and its trajectory metric (per-step pass decline) needs
only the same model+harness, not a headroom-sweet-spot task.

## D14 — Reproducibility standard on the vLLM/bf16 stack: statistical, not bit-for-bit (2026-07-13, Phase M / M5)

The Phase-0 bit-for-bit lock (lock_a/lock_b, 164/164 byte-identical) was a property
of the old HF stack: fixed `torch.manual_seed` + deterministic algorithms →
bit-identical runs. **The vLLM/bf16 throughput stack does not reproduce
byte-for-byte** — M5 measured, across two independent seeded runs, **greedy
143/164** and **seeded-stochastic 294/328** candidates byte-identical. The
divergences are coherent alternative generations (as at GATE K1), caused by
nondeterministic throughput kernels (reduction atomics, CUDA graphs, the
FlashInfer→PyTorch sampling fallback). This is **inherent to the stack**, not a bug,
and it is the accepted cost of the 100× throughput (D11).

**Decision:** retire the bit-lock; the reproducibility standard on the new stack is
**statistical** — aggregate metrics (pass@k, AUROC, matched-compute deltas) reproduce
within sampling noise, and Phase-3 comparisons already gate on bootstrap CIs, which
are robust to ~10% candidate-level nondeterminism. Evidence it holds: M3's two
independent bf16 draws agreed to ~1 pt (B0 0.6418 vs 0.6479; pass@8 0.9146 vs
0.9024). `lock_a_bf16.jsonl` / `lock_b_bf16.jsonl` are retained as a reference that
documents the drift level, not as a bit-lock.

*Honest cost:* this is a genuine reduction in reproducibility rigor vs the old stack.
A bit-reproducible *verification* mode (greedy + `enforce_eager` + a deterministic
attention backend, at a throughput cost) could be pursued if a future result ever
needs exact replay; it is not the deployment mode and is not built now.

## D15 — Phase-3 benchmark + generator scale: (BigCodeBench-Complete, Qwen2.5-Coder-0.5B) — **RETRACTED 2026-07-14**

> **RETRACTED.** The selection below rested on the n=40 screen using the **first** 40
> BigCodeBench problems. The full-benchmark confirmation (n=400 **random**, k=50)
> showed first-n is ~2× easier than a random draw: (Complete, 0.5B) is pass@8 **0.161
> / headroom +0.092** on a representative sample — it **does not** qualify (below the
> [0.30,0.60] band, headroom < 0.15). D15 is void; Phase 3a is re-opened and being
> re-screened on random samples ([PHASE_3.md] §4.2 correction banner). The original
> reasoning is kept below for the record.

*(Original entry, 2026-07-13 — now retracted:)*

The 3a screen (GATE, [PHASE_3.md] §4) selects the task on its pass@k curve. Exactly
one screened config clears both criteria — coverage pass@8 ∈ [0.30, 0.60], headroom
pass@50 − pass@8 ≥ 0.15, and ≫3 tests/problem:

| config | pass@8 | headroom | import-fail | verdict |
|---|---|---|---|---|
| BigCodeBench-Complete @ 1.5B | 0.579 | +0.071 | 0.000 | too easy (shallow headroom) |
| **BigCodeBench-Complete @ 0.5B** | **0.340** | **+0.185** | 0.006 | **SELECTED** |
| BigCodeBench-Hard @ 1.5B | 0.175 | +0.175 | 0.130 | too hard (below band) |

**Decision:** Phase 3b runs on **BigCodeBench-Complete with Qwen2.5-Coder-0.5B-Instruct
as the frozen generator G.** BigCodeBench's rich unittest feedback (~5 methods/problem,
D15 satisfies the "gradient to descend" criterion) plus the 0.5B coverage regime give
the reachable-but-improbable headroom the register experiment needs — the thing
HumanEval (0.90) never had.

**Consequence (accepted):** the RGR stack is **rebuilt at 0.5B** — register injection
(`prompt_embeds` re-validated at 0.5B, an M1-style check), U, and the verifier all
retrain on 0.5B/BigCodeBench candidates. This is a scale change from Phases 0–2's
1.5B; those results stay historical (already the rule since D11/D14). M4 already told
us V-v2b must be retrained regardless.

*Reasoning for accepting the scale change:* no 1.5B-native BigCodeBench config lands
in the band — the two 1.5B splits bracket the sweet spot (too easy on Complete, too
hard on Hard). Keeping 1.5B would require an intermediate-difficulty benchmark not in
the tested set.

*Revisit if:* (a) 0.5B proves too weak for a meaningful register signal in 3b-full
(the model may lack the capability for conditioning to exploit) → screen an
intermediate-difficulty benchmark at 1.5B (LiveCodeBench/CodeContests, needs a
stdin/stdout execution harness; APPS failed to load on `datasets` 5.0); or (b) the
full-benchmark run on (Complete, 0.5B) contradicts the n=40 subset estimate.

## D16 — Finding F1: BigCodeBench cannot host the refinement experiment at 0.5–1.5B (2026-07-14, Phase 3a)

The 3a gate needs a task with reachable-but-improbable headroom (pass@8 ∈ [0.30,0.60]
AND pass@50 − pass@8 ≥ 0.15) plus rich feedback. On **random** samples (the first-n
shortcut was retired after it proved ~2× optimistic), **no BigCodeBench configuration
qualifies**:

| config (random, k=50) | pass@8 | headroom |
|---|---|---|
| Complete @ 0.5B | 0.161 | +0.092 |
| Complete @ 1.5B | 0.302 | +0.108 |
| Hard @ 1.5B (all 148) | 0.118 | +0.112 |

**The binding failure is headroom, not coverage:** it is structurally ~0.09–0.11
everywhere, never ≥0.15 — even where coverage is in-band. BigCodeBench's reachable
tail is shallow (solve-within-8-or-not), the same shape that sank HumanEval, because
function-call/unit-test benchmarks lack "reachable-but-improbable" solution diversity.
A different model scale does not fix a structural property.

**This is a documented, useful negative** — it refines the experiment: refinement
needs a task whose **pass@k keeps climbing with k** (a deep reachable tail), which
points at **competitive (stdin/stdout)** benchmarks, not function-call ones. It also
retires the first-n screening shortcut (random-only from here).

*Consequence:* pursue option (a) — screen LiveCodeBench (stdin/stdout, difficulty
tiers) with a new I/O-comparison harness. If no competitive tier qualifies either,
the gate's negative stands at this model scale and *that* is the Phase-3 result
(where refinement can and cannot live), with the coverage/headroom structure
characterized. Either way F1 stands.

*Revisit if:* a larger model (3B/7B) or a different task family is brought in — the
headroom structure may differ; F1 is scoped to 0.5–1.5B on function-call benchmarks.

### D16 extended (2026-07-14) — FINDING F2: the gate returns a NEGATIVE

The LiveCodeBench screen (option a) completes the sweep. Competitive (stdin/stdout)
was the best hope for a deep reachable tail; it is deeper than function-call but still
short:

| benchmark / tier | scale | pass@8 | headroom |
|---|---|---|---|
| BigCodeBench-Complete | 0.5B | 0.161 | +0.092 |
| BigCodeBench-Complete | 1.5B | 0.302 (band) | +0.108 |
| BigCodeBench-Hard | 1.5B | 0.118 | +0.112 |
| LiveCodeBench-easy | 1.5B | 0.541 (band) | +0.122 |
| LiveCodeBench-medium | 1.5B | 0.067 | +0.087 |

**F2:** no configuration reaches pass@50 − pass@8 ≥ 0.15 — capped at ~0.09–0.12 across
two families, two execution paradigms, three tiers, two scales. Structural: code
solutions are gettable-or-not within a few samples, so pass@k saturates and
sample-based refinement has almost no runway at 0.5–1.5B; scaling the generator UP
worsens it (more coverage → more saturation → less headroom). **The 3a gate outcome is
NEGATIVE.** 3b/3c do not proceed on a benchmark that fails the screen.

**Consequence / next-stage fork** (writeup §7.4): (i) heavier-tailed task family
(agentic/synthesis, off the code-benchmark shelf); (ii) **redefine the "reachable"
axis toward feedback-driven recovery** — does an error abstraction let the model reach
solutions it could not i.i.d.-sample (the DIAG-10 direction; does not require i.i.d.
headroom) — **recommended**; (iii) accept F2 as the Phase-3 result and write
"where/why sample-based refinement has runway on code." The next action is
pre-registering the 3b redesign around (ii). F2 stands regardless; scoped to the
tested benchmarks/scales.
