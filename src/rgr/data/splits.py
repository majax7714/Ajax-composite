"""Split discipline (D8): HumanEval never touches training or tuning.

Every dataset handle is tagged with its allowed role; ``checkout`` refuses to
serve a held-out dataset to a training/tuning consumer. Contamination becomes a
raised exception, not a convention.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from rgr.types import Problem, SplitRole

HELDOUT_SOURCES = {"humaneval", "humaneval+"}


class SplitViolation(RuntimeError):
    pass


@dataclass(frozen=True)
class TaggedDataset:
    name: str
    role: SplitRole
    problems: tuple[Problem, ...]

    def checkout(self, purpose: SplitRole) -> tuple[Problem, ...]:
        """Hand out problems for ``purpose``. Held-out data serves only
        HELDOUT_EVAL; training data may also serve validation-style purposes.
        """
        if self.role == SplitRole.HELDOUT_EVAL and purpose != SplitRole.HELDOUT_EVAL:
            raise SplitViolation(
                f"{self.name} is held-out evaluation data and may not be used for "
                f"{purpose.value} — this is the contamination guard (DECISIONS.md D8)"
            )
        return self.problems


def tag(name: str, problems: list[Problem]) -> TaggedDataset:
    sources = {p.source for p in problems}
    if sources & HELDOUT_SOURCES:
        if sources - HELDOUT_SOURCES:
            raise SplitViolation(f"dataset {name} mixes held-out and training sources: {sources}")
        role = SplitRole.HELDOUT_EVAL
    else:
        role = SplitRole.TRAIN
    return TaggedDataset(name=name, role=role, problems=tuple(problems))


def train_val_split(
    dataset: TaggedDataset, val_fraction: float, seed: int
) -> tuple[TaggedDataset, TaggedDataset]:
    """Deterministic problem-level split of a TRAIN dataset."""
    if dataset.role != SplitRole.TRAIN:
        raise SplitViolation("only training datasets can be split")
    if not 0.0 < val_fraction < 1.0:
        raise ValueError("val_fraction must be in (0, 1)")
    problems = list(dataset.problems)
    random.Random(seed).shuffle(problems)
    n_val = max(1, int(len(problems) * val_fraction))
    val, train = problems[:n_val], problems[n_val:]
    return (
        TaggedDataset(f"{dataset.name}-train", SplitRole.TRAIN, tuple(train)),
        TaggedDataset(f"{dataset.name}-val", SplitRole.VALIDATION, tuple(val)),
    )
