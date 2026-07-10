"""MBPP (sanitized) — training and validation data (brief §4).

427 hand-verified problems from google-research/mbpp, pinned by checksum.
Tagged TRAIN by the split guard; carve validation off with
rgr.data.splits.train_val_split.

Prompt construction: MBPP descriptions don't name the function, so the tests
are shown in the prompt (standard MBPP protocol) — the model must be told the
expected signature. The same prompt template is used for every condition, so
this can't differentially flatter any of them.
"""

from __future__ import annotations

import json

from rgr.data.fetch import fetch
from rgr.data.splits import TaggedDataset, tag
from rgr.types import Problem

MBPP_URL = "https://raw.githubusercontent.com/google-research/google-research/master/mbpp/sanitized-mbpp.json"
MBPP_SHA256 = "ca95deaa9a01ef0a6f439f88bcf0dd3db3563d22f22aad6cae04ebb9a8d8c8e9"

PROMPT_TEMPLATE = (
    "{description}\n\nYour solution must be a Python function that passes these tests:\n"
    "```python\n{tests}\n```"
)


def load_mbpp() -> TaggedDataset:
    path = fetch(MBPP_URL, "sanitized-mbpp.json", MBPP_SHA256)
    rows = json.loads(path.read_text())
    return tag("mbpp", [_to_problem(row) for row in rows])


def _to_problem(row: dict) -> Problem:
    test_list = tuple(row["test_list"])
    return Problem(
        problem_id=f"mbpp/{row['task_id']}",
        prompt=PROMPT_TEMPLATE.format(
            description=row["prompt"].strip(), tests="\n".join(test_list)
        ),
        tests="\n".join(test_list),
        test_list=test_list,
        test_setup="\n".join(row.get("test_imports", [])),
        source="mbpp",
    )
