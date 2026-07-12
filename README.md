# RGR — Register-Gated Refinement

A minimal, falsifiable experiment for one claim:

> **An explicit internal state vector — a "register" — that gates generation and is
> updated across refinement steps improves calibration and correctness beyond what
> verification-plus-iteration already buys you.**

The register is the *only* channel that carries information across refinement steps.
Ablate its updates and the loop collapses, by construction, into verifier-reranked
best-of-n — so the central ablation and one of the baselines are the same object.

Full motivation and constraints: [docs/build-brief.md](docs/build-brief.md).
This README is the operational entry point; the brief is the source of truth for
the claim and kill criteria.

## The three hypotheses (each with a pre-committed kill criterion)

| | Claim | Gate |
|---|---|---|
| **H1** | An execution-trained verifier's confidence ranks correctness better than generator log-likelihood | Verifier AUROC must clear likelihood AUROC by a real margin, or stop |
| **H2** | Register-gated refinement beats best-of-n (B1) *and* in-context refinement (B2) at matched compute | FULL must beat both, or the register is dead (publishable negative) |
| **H3** | Settling depth tracks difficulty; adaptive stopping beats fixed-K at matched mean compute | Weaker gate; H3 failing does not sink H2 |

**H1 gates H2 gates H3.** We do not tune past a failed gate.

## Architecture in one screen

```
r ← r_0(problem)                        # problem-encoded init (D4)
for t in 0..T_max:
    candidate ← G(problem, r)           # regenerate conditioned on register
    v ← V(problem, candidate)           # verifier is register-blind in v1 (D3)
    if v ≥ τ: break                     # fixed threshold (D5)
    r ← U(r, φ(candidate), v)           # GRU update — the only cross-step channel
return best candidate by v
```

- **G** — frozen ~1.5B code model (4-bit), conditioned on the register via k learned
  soft-prompt embeddings.
- **r** — the register, `d_r = 128` (D1). Initialized from a pooled encoding of the
  problem; updated only by U.
- **U** — a small GRU cell over `(r, φ(candidate), v)`, trained by imitation first (D2).
- **V** — small verifier trained on sandboxed execution labels. Its score gates the
  loop; its negative log is the energy.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full design and
[docs/DECISIONS.md](docs/DECISIONS.md) for the resolved open decisions (D1–D8),
including why the ablation is *freeze-r-at-r_0*, not zero-r, given the
problem-encoded init.

## Repository map

```
docs/               Design docs: brief, architecture, decisions, metrics,
                    compute accounting (frozen before any run), phase plan
configs/            TOML experiment configs, one per phase, layered on base.toml
src/rgr/
  types.py          Problem / Candidate / StepRecord / Trajectory (pure stdlib)
  config.py         Typed config loading (stdlib tomllib)
  generator/        G: model wrapper, soft-prompt injection, format discipline
  register/         r_0 encoder, GRU update U, dynamics diagnostics
  verifier/         V: pooled-feature MLP, φ feature extraction
  execution/        Sandbox protocol + Daytona backend + guarded local dev backend
  loop/             The refinement loop, baselines B0/B1/B1'/B2, compute ledger
  data/             MBPP (train), HumanEval (held-out), split discipline
  evals/            pass@k (unbiased), AUROC/ECE/Brier, problem-level bootstrap
  training/         Label generation, verifier training, register imitation
scripts/            One entry point per phase, each printing its gate verdict
tests/              Stdlib-runnable tests for all pure-logic modules
```

Design rule enforced throughout: **everything that decides the experiment's
verdict (loop control flow, compute accounting, metrics) is pure stdlib Python and
tested locally.** Torch/transformers live only at the model edges
(`generator/`, `register/`, `verifier/` internals), so the experiment logic can
never silently depend on an untested GPU path.

## Status

**Phase 2 — H2 gate FAILED (2026-07-12): the register is dead as claimed.**
FULL (register-gated refinement) ties B1 (verifier-reranked best-of-n,
register frozen at r_0) *exactly* at matched compute on HumanEval: 0.6829 vs
0.6829, CI [−0.049, +0.055]. Diagnostics rule out the mundane outs — register
dynamics healthy, verifier not stale, imitation training verifiably steered
teacher-forced likelihood (−11% val) — the steering simply did not survive
sampling at 1.5B. This is the clean negative the pre-registered design was
built to surface (brief §1 H2 kill criterion).

Standing positive results: H1 PASSED — the execution-trained verifier beats
self-fluency decisively (AUROC 0.795 vs 0.696, within-problem 0.719 vs 0.568)
and lifts best-of-8 from 0.628 to 0.671 pass@1. Phase 0 baselines frozen and
bit-for-bit reproducible.

Remaining: B2 run (completes the kill record), then the write-up. Post-hoc
directions (RL regime, richer injection, larger G) are future experiments,
not rescues. See [docs/PHASES.md](docs/PHASES.md) for the gate log.

## Quickstart

```bash
pip install -e ".[dev]"      # local: pure-logic work + tests
pip install -e ".[model]"    # GPU env (Kaggle): torch/transformers extras
pip install daytona          # execution sandbox SDK (any box that runs labels)
make test                    # runs the stdlib test suite
```

Credentials: the Daytona key is read from `DAYTONA_API_KEY` or the gitignored
`rgb-daytona.txt` at the repo root. Never commit it.

### Phase 0 on the GPU box (Kaggle T4/P100)

```bash
git clone <this repo> && cd rgr
pip install -e ".[model]" daytona
export DAYTONA_API_KEY=...                     # or place rgb-daytona.txt at repo root
python scripts/phase0_lock_baselines.py --handcheck          # §11.1: inspect BY HAND
python scripts/phase0_lock_baselines.py --lock --seed-tag lock_a
python scripts/phase0_lock_baselines.py --lock --seed-tag lock_b   # reproducibility gate
```

Training runs on Kaggle/rented GPU; the 8600G box is for orchestration, analysis,
and dashboards only (§7 of the brief).
