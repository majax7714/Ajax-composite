"""The refinement loop — the object under test.

One function implements FULL, FULL-adaptive, B1, and B0, differing only in
flags (ARCHITECTURE.md §2). That identity is the point: B1 *is* the
register-update-ablated FULL (freeze_register=True), conditioned on the same
frozen r_0(problem), so FULL-vs-B1 isolates exactly the register updates (D4).

Information-flow contract: nothing from step t reaches step t+1 except the
register, mutated only by ``updater.update``. The loop never shows G a previous
candidate (that is B2, in rgr.loop.baselines) and never re-derives state from
the trajectory.
"""

from __future__ import annotations

from rgr.loop.budget import ComputeLedger
from rgr.loop.interfaces import (
    GeneratorLike,
    RegisterInitLike,
    RegisterUpdateLike,
    VerifierLike,
)
from rgr.types import Problem, StepRecord, Trajectory


def run_refine(
    problem: Problem,
    generator: GeneratorLike,
    verifier: VerifierLike,
    register_init: RegisterInitLike,
    updater: RegisterUpdateLike,
    *,
    t_max: int,
    freeze_register: bool = False,
    early_stop: bool = False,
    tau: float = 0.9,
    condition: str | None = None,
) -> Trajectory:
    """Run the loop on one problem.

    Conditions by flags:
      FULL (H2)          freeze_register=False, early_stop=False
      FULL-adaptive (H3) freeze_register=False, early_stop=True
      B1 / ablation      freeze_register=True,  early_stop=False
      B0                 t_max=1
    """
    if condition is None:
        condition = (
            "b0" if t_max == 1
            else "b1" if freeze_register
            else "full_adaptive" if early_stop
            else "full"
        )

    ledger = ComputeLedger()
    trajectory = Trajectory(problem_id=problem.problem_id, condition=condition, ledger=ledger)

    register = register_init.init(problem)

    for t in range(t_max):
        candidate = generator.generate(problem, register)
        ledger.charge_generation(candidate.prompt_tokens, candidate.generated_tokens)

        score = verifier.score(problem, candidate, register)
        ledger.charge_verifier()

        trajectory.steps.append(
            StepRecord(
                step=t,
                candidate=candidate,
                verifier_score=score,
                register_norm=updater.norm(register),
            )
        )

        if early_stop and score >= tau:
            trajectory.stopped_early = True
            break

        if not freeze_register and t < t_max - 1:
            new_register = updater.update(register, candidate, score)
            ledger.charge_update()
            trajectory.steps[-1].register_delta_norm = updater.delta_norm(register, new_register)
            register = new_register

    return trajectory
