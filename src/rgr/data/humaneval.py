"""HumanEval — HELD-OUT EVALUATION ONLY (brief §4).

164 problems from openai/human-eval, pinned by checksum. The split guard tags
this HELDOUT_EVAL and raises if a training/tuning consumer checks it out.
Never select thresholds, hyperparameters, or checkpoints on this data.

The model is asked for the complete function (signature included), not a bare
continuation — the format-discipline layer extracts one fenced block, and the
test block calls check(entry_point) against whatever that block defined.
"""

from __future__ import annotations

import gzip
import json

from rgr.data.fetch import fetch
from rgr.data.splits import TaggedDataset, tag
from rgr.types import Problem

HUMANEVAL_URL = "https://raw.githubusercontent.com/openai/human-eval/master/data/HumanEval.jsonl.gz"
HUMANEVAL_SHA256 = "b796127e635a67f93fb35c04f4cb03cf06f38c8072ee7cee8833d7bee06979ef"

PROMPT_TEMPLATE = (
    "Complete the following Python function. Give the complete function "
    "(including the signature shown), plus any helpers it needs:\n"
    "```python\n{stub}\n```"
)


def load_humaneval() -> TaggedDataset:
    path = fetch(HUMANEVAL_URL, "HumanEval.jsonl.gz", HUMANEVAL_SHA256)
    with gzip.open(path, "rt") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    return tag("humaneval", [_to_problem(row) for row in rows])


def _to_problem(row: dict) -> Problem:
    return Problem(
        problem_id=f"humaneval/{row['task_id']}",
        prompt=PROMPT_TEMPLATE.format(stub=row["prompt"].rstrip()),
        tests=f"{row['test']}\n\ncheck({row['entry_point']})\n",
        entry_point=row["entry_point"],
        source="humaneval",
    )
