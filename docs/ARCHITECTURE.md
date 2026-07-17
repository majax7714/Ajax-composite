# Architecture

> **Status note (2026-07-17, appended — content below unrevised):** Historical.
> Describes `src/rgr/` for the original register experiment (frozen since
> Phase 2). Later-phase experiment code lives in `scripts/modal_*.py`; the
> current entry point is [WRITEUP-rgr.md](WRITEUP-rgr.md).

How the four components fit together, how information is allowed to flow, and
where each piece lives in `src/rgr/`. The design constraint that everything else
serves: **the register update is the only channel that carries information across
refinement steps.** Every interface below is shaped to make violating that
constraint hard.

---

## 1. Components

### G — Generator (`rgr/generator/`)

Qwen2.5-Coder-1.5B-Instruct, loaded 4-bit, **frozen** (D6). Two entry points:

- `generate(problem, soft_prompt) -> Candidate` — one sampled candidate,
  conditioned on the problem prompt with `k` soft-prompt embeddings prepended.
  Also returns mean token log-probability (the H1 likelihood baseline) and the
  pooled last-layer hidden states (reused as φ).
- `generate_with_feedback(problem, prev_candidate, feedback) -> Candidate` —
  **used by baseline B2 only.** The FULL loop must never call this; the type
  system doesn't stop you, the code review discipline does, and
  `rgr.loop.refine` simply has no path to it.

`generator/formatting.py` owns the format-discipline layer: prompt template that
elicits fenced code, and extraction of the code block from the raw completion.
A candidate that yields no extractable code is recorded as `code=None` and is an
automatic execution failure (never silently dropped — it consumes budget).

`generator/injection.py`: `RegisterInjector`, a learned linear map
`r (d_r) -> k × d_model` embeddings. Trainable. This is the *only* way r touches G.

### r — Register (`rgr/register/`)

A `d_r = 128` vector. Initialized by `RegisterEncoder` (`register/encoder.py`):
a learned linear projection of φ(problem) (D4). Updated only by U. The loop
treats it as opaque state; nothing else reads or writes it.

`register/diagnostics.py` tracks the failure modes named in §8 of the brief:
per-step norm, step-to-step delta norm, cross-problem variance of final
registers. Collapse (deltas → 0) and blow-up (norm → ∞) both have alert
thresholds; these diagnostics are logged on every Phase-2 run, not optionally.

### U — Register update (`rgr/register/update.py`)

`GRUCell` over input `[φ(candidate); v]`, hidden state r. Stability guards built
in, not bolted on: RMS-normalization of r after each update and a max-norm clip
on the delta (both configurable, both on by default). Trained by imitation (D2).

### V — Verifier (`rgr/verifier/`)

V-v1: MLP over `[φ(problem); φ(candidate)]` → sigmoid `P(correct)`, with
auxiliary heads for fraction-of-tests-passed and error type (D7). Register-blind
in v1 (D3); `verifier.sees_register` config flag reserves the v2 coupling.
Trained on execution labels from the sandbox (Phase 1), refreshed from
current-policy rollouts between phases to fight actor/critic staleness (§2 of
the brief) — staleness is measured, not assumed: V's AUROC on fresh rollouts is
a standing diagnostic.

---

## 2. The loop (`rgr/loop/`)

`loop/refine.py` implements:

```
r ← r_0(problem)
for t in 0..T_max:
    candidate ← G(problem, inject(r))
    v ← V(problem, candidate)
    record step; charge ledger
    if early_stop and v ≥ τ: break
    if not freeze_register:
        r ← U(r, φ(candidate), v)
return trajectory (best candidate = argmax v)
```

Two flags define every experimental condition:

| Condition | `freeze_register` | `early_stop` | Notes |
|---|---|---|---|
| FULL (fixed-K, H2) | false | false | K = T_max steps, always |
| FULL (adaptive, H3) | false | true | fixed τ (D5) |
| **B1** (best-of-n) | **true** | false | *identical code path* — the ablation **is** the baseline |
| B0 (single-shot) | — | — | `T_max = 1` degenerate case |

B1′ (no injection) and B2 (in-context refinement) live in `loop/baselines.py`
as separate paths, because they change what G is called with, not just the flags.

The loop is written against **protocols** (`loop/interfaces.py`): `GeneratorLike`,
`VerifierLike`, `RegisterInitLike`, `RegisterUpdateLike`. It is pure stdlib and
fully unit-tested with fakes — the control flow that decides H2/H3 never depends
on GPU code.

### Compute ledger (`loop/budget.py`)

Every generator call, verifier call, and update is charged to a `ComputeLedger`
attached to the trajectory. The matched-compute rule is specified and frozen in
[COMPUTE_ACCOUNTING.md](COMPUTE_ACCOUNTING.md); the ledger records the raw
quantities (calls, prompt tokens, generated tokens) so the accounting can be
audited after the fact without rerunning.

---

## 3. Information-flow rules (the ablation contract)

1. Cross-step state is `r` and nothing else. No candidate text, no verifier
   feedback, no scores flow from step t to t+1 in FULL — only through U into r.
2. G's context at step t is: soft prompt from `r_t` + problem prompt. Never a
   previous candidate (that's B2, a baseline, not the mechanism).
3. B1 conditions on frozen `r_0(problem)` so that FULL-vs-B1 isolates exactly
   the register *updates* (D4). B1′ measures the static value of r_0 itself.
4. V sees `(problem, candidate)` only (D3, v1).

Any code change that would breach rule 1–4 changes the experiment, not the
implementation, and needs a DECISIONS.md entry first.

---

## 4. Training dataflow

```
Phase 1:  G + sandbox ──► labeled candidates (candidates × execution results)
                              │
                              ▼
                        train V (supervised)  ──►  H1 gate: AUROC(V) vs AUROC(likelihood)

Phase 2:  run loop with untrained U, collect trajectories, keep those reaching a pass
                              │
                              ▼
          imitation targets for U + injector + r_0 encoder (G, V frozen)
                              │
                              ▼
          FULL vs B1 vs B2 at matched compute  ──►  H2 gate
          (refresh V's training set from current-policy rollouts between rounds)

Phase 3:  sweep τ on MBPP validation, freeze, evaluate adaptive vs fixed-K  ──►  H3 gate
```

Execution labels come exclusively from `rgr/execution/` (Daytona sandbox;
guarded local backend for smoke tests only). Result schema:
`{passed: bool, frac_tests: float, error_type: str}` — the auxiliary targets for V.

---

## 5. Data (`rgr/data/`)

- **MBPP / MBPP+** — training and validation (candidate labeling, U imitation,
  all threshold/hyperparameter selection).
- **HumanEval / HumanEval+** — held-out evaluation only. `rgr.data.splits` tags
  every dataset handle with its allowed role and refuses to serve HumanEval to a
  training-tagged consumer; contamination is a code-level error, not a
  convention.
- **Difficulty proxy (H3):** per-problem single-shot pass rate from the Phase-0
  B0 runs (model-relative, cheap, already computed by the time H3 needs it).

---

## 6. What is deliberately not here

Per §0 of the brief: no from-scratch energy/diffusion LM, no substrate claims,
no SOTA chase. The conceptual mapping (chemical-state gating → register;
consistency manifold → execution-grounded verifier; Hamiltonian settling →
dissipative energy descent with adaptive depth) is stated in the brief §3 and
belongs in the paper as *functional* organization — it imposes no code.
