"""MBPP / MBPP+ loading — training and validation data (brief §4).

GPU/data-edge module: needs the ``datasets`` package (model extra). Emits
rgr.types.Problem with source="mbpp" / "mbpp+" so the split guard can tag it
TRAIN. Reuse note (brief §4): the existing Loop 1 dataset covering MBPP/xLAM
supplies the format-discipline layer; wire it here when porting.
"""

from __future__ import annotations

from rgr.data.splits import TaggedDataset, tag
from rgr.types import Problem


def load_mbpp(plus: bool = False) -> TaggedDataset:
    """Load MBPP (or MBPP+ for denser tests) as a tagged TRAIN dataset.

    Phase 0 wiring: ``datasets.load_dataset("evalplus/mbppplus")`` when plus
    else ``("mbpp", "sanitized")``; map each row to Problem(problem_id, prompt
    = row text, tests = "\\n".join(assert statements), source=...).
    """
    raise NotImplementedError("Phase 0: wire datasets loader (see docstring)")


def _to_problem(row: dict, plus: bool) -> Problem:
    source = "mbpp+" if plus else "mbpp"
    return Problem(
        problem_id=f"{source}/{row['task_id']}",
        prompt=row["prompt"] if "prompt" in row else row["text"],
        tests="\n".join(row["test_list"]) if "test_list" in row else row["test"],
        source=source,
    )
