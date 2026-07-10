"""HumanEval / HumanEval+ loading — HELD-OUT EVALUATION ONLY (brief §4).

The split guard (rgr.data.splits) tags anything from these sources
HELDOUT_EVAL and will raise if a training/tuning consumer checks it out.
Never select thresholds, hyperparameters, or checkpoints on this data.
"""

from __future__ import annotations

from rgr.data.splits import TaggedDataset, tag
from rgr.types import Problem


def load_humaneval(plus: bool = False) -> TaggedDataset:
    """Phase 0 wiring: ``datasets.load_dataset("evalplus/humanevalplus")`` when
    plus else ``("openai_humaneval",)``; map rows to Problem(prompt=row
    prompt, tests=row test + check(entry_point) driver, entry_point=...)."""
    raise NotImplementedError("Phase 0: wire datasets loader (see docstring)")


def _to_problem(row: dict, plus: bool) -> Problem:
    source = "humaneval+" if plus else "humaneval"
    return Problem(
        problem_id=f"{source}/{row['task_id']}",
        prompt=row["prompt"],
        tests=f"{row['test']}\n\ncheck({row['entry_point']})\n",
        entry_point=row["entry_point"],
        source=source,
    )
