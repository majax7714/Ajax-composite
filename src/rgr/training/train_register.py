"""Phase 2: imitation training of the register modules (D2).

Trainable surface (exactly, per D6): RegisterInjector, ProblemRegisterEncoder,
RegisterUpdate. G and V frozen.

Regime (a) from brief §2 — imitation toward register trajectories that led to
passes:

  1. ROLLOUT: run the FULL loop with current (initially random) register
     modules over MBPP-train; execute every step's candidate in the sandbox;
     keep trajectories that reach a pass by step t*.
  2. TARGETS: for each kept trajectory, the register states r_1..r_t* that
     preceded the passing candidate define the imitation targets; candidates
     and verifier scores along the way are the inputs U saw.
  3. FIT: teacher-forced sequence loss — unroll U on the recorded
     (phi(candidate_t), v_t) inputs and regress onto the recorded target
     trajectory; injector/encoder gradients flow through the same unroll via
     a language-modeling-free surrogate: maximize V's score of the passing
     candidate under the injected register (V frozen, differentiable).
  4. ITERATE rollout -> fit; refresh V's training set from current-policy
     rollouts between iterations (staleness check: METRICS.md diagnostics).

D2's revisit clause: if kept-trajectory counts are too sparse to fit, log the
sparsity numbers in DECISIONS.md before considering the RL regime.

Stability watch (brief §8: "expect to spend most of your time here"):
rgr.register.diagnostics runs on every rollout batch; collapse/blow-up alerts
halt training rather than silently continuing.
"""

from __future__ import annotations


def rollout_for_imitation(problems, generator, verifier, register_init, updater, backend, config):
    """Step 1-2: collect kept trajectories with per-step execution labels."""
    raise NotImplementedError("Phase 2")


def fit_register_modules(kept_trajectories, injector, encoder, updater, verifier, config):
    """Step 3: teacher-forced imitation + frozen-V score surrogate."""
    raise NotImplementedError("Phase 2")
