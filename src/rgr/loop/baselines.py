"""Baselines that are NOT flag-variants of the loop.

B0 and B1 are run_refine with flags (see rgr.loop.refine) — B1 in particular
must go through the identical code path to keep ablation ≡ baseline exact.

Here live the two conditions that call the generator differently:
  B1' — no injection at all (register=None). Secondary control isolating the
        static value of r_0 conditioning (D4). Reported, does not gate H2.
  B2  — in-context iterative refinement: previous candidate + verifier feedback
        in the prompt. The "iteration without a latent state" comparator.
"""

from __future__ import annotations

from rgr.loop.budget import ComputeLedger
from rgr.loop.interfaces import FeedbackGeneratorLike, GeneratorLike, VerifierLike
from rgr.types import Problem, StepRecord, Trajectory


def run_b1_prime(
    problem: Problem,
    generator: GeneratorLike,
    verifier: VerifierLike,
    *,
    n: int,
) -> Trajectory:
    """Best-of-n with NO register injection; verifier-reranked."""
    ledger = ComputeLedger()
    trajectory = Trajectory(problem_id=problem.problem_id, condition="b1_prime", ledger=ledger)
    for t in range(n):
        candidate = generator.generate(problem, None)
        ledger.charge_generation(candidate.prompt_tokens, candidate.generated_tokens)
        score = verifier.score(problem, candidate, None)
        ledger.charge_verifier()
        trajectory.steps.append(StepRecord(step=t, candidate=candidate, verifier_score=score))
    return trajectory


def run_b2(
    problem: Problem,
    generator: FeedbackGeneratorLike,
    first_generator: GeneratorLike,
    verifier: VerifierLike,
    *,
    n: int,
) -> Trajectory:
    """In-context iterative refinement: attempt, then n-1 revision rounds, each
    seeing the previous candidate and the verifier's score in the prompt.

    Costs n generations — same budget as FULL at t_max=n. Its prompts grow with
    the embedded previous candidate; that token asymmetry favors B2 and is
    recorded in the ledger (COMPUTE_ACCOUNTING.md audit column 2).
    """
    ledger = ComputeLedger()
    trajectory = Trajectory(problem_id=problem.problem_id, condition="b2", ledger=ledger)

    candidate = first_generator.generate(problem, None)
    ledger.charge_generation(candidate.prompt_tokens, candidate.generated_tokens)
    score = verifier.score(problem, candidate, None)
    ledger.charge_verifier()
    trajectory.steps.append(StepRecord(step=0, candidate=candidate, verifier_score=score))

    for t in range(1, n):
        candidate = generator.generate_with_feedback(problem, candidate, score)
        ledger.charge_generation(candidate.prompt_tokens, candidate.generated_tokens)
        score = verifier.score(problem, candidate, None)
        ledger.charge_verifier()
        trajectory.steps.append(StepRecord(step=t, candidate=candidate, verifier_score=score))

    return trajectory
