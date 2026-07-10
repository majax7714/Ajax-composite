"""Core datatypes shared across the pipeline.

Pure stdlib. Everything that flows between the loop, the sandbox, and the
metrics is one of these types, so the experiment's plumbing is inspectable
without touching model code.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SplitRole(str, Enum):
    """What a dataset handle may be used for. Enforced by rgr.data.splits."""

    TRAIN = "train"
    VALIDATION = "validation"
    HELDOUT_EVAL = "heldout_eval"


@dataclass(frozen=True)
class Problem:
    """A single coding problem with executable tests."""

    problem_id: str
    prompt: str
    tests: str
    entry_point: str | None = None
    source: str = ""  # "mbpp", "mbpp+", "humaneval", "humaneval+"
    # Individual test statements when the dataset provides them (MBPP's assert
    # list). Enables per-test frac_tests, V's auxiliary target. When empty,
    # ``tests`` runs as one block and frac_tests collapses to 0/1 (HumanEval's
    # check() driver).
    test_list: tuple[str, ...] = ()
    # Run once after the candidate, before any test (MBPP's test_imports).
    test_setup: str = ""


@dataclass(frozen=True)
class Candidate:
    """One sampled solution.

    ``code`` is None when the format-discipline layer found no extractable code
    block; such candidates are automatic execution failures but still consume
    budget (COMPUTE_ACCOUNTING.md).
    """

    text: str
    code: str | None
    mean_logprob: float | None = None  # H1 likelihood baseline
    prompt_tokens: int = 0
    generated_tokens: int = 0
    # Pooled last-hidden-state embedding (phi), attached by the generator at
    # generation time so U and V never need a second forward pass. Opaque here
    # (torch.Tensor at runtime) to keep this module stdlib-only.
    phi: Any = field(default=None, repr=False, compare=False)


@dataclass(frozen=True)
class ExecutionResult:
    """Sandbox verdict for (problem, candidate). The verifier's label schema."""

    passed: bool
    frac_tests: float
    error_type: str = ""  # "", "syntax", "runtime", "timeout", "wrong_answer", "no_code"


@dataclass
class StepRecord:
    """One iteration of the refinement loop."""

    step: int
    candidate: Candidate
    verifier_score: float
    register_norm: float | None = None
    register_delta_norm: float | None = None


@dataclass
class Trajectory:
    """Full record of one loop run on one problem, with its compute ledger.

    ``best_index`` is the argmax of verifier score — the deployed answer for
    every condition that has a verifier.
    """

    problem_id: str
    condition: str  # "b0" | "b1" | "b1_prime" | "b2" | "full" | "full_adaptive"
    steps: list[StepRecord] = field(default_factory=list)
    stopped_early: bool = False
    ledger: Any = None  # rgr.loop.budget.ComputeLedger

    @property
    def best_index(self) -> int:
        if not self.steps:
            raise ValueError("empty trajectory")
        return max(range(len(self.steps)), key=lambda i: self.steps[i].verifier_score)

    @property
    def best_candidate(self) -> Candidate:
        return self.steps[self.best_index].candidate

    @property
    def best_score(self) -> float:
        return self.steps[self.best_index].verifier_score

    @property
    def num_generations(self) -> int:
        return len(self.steps)
