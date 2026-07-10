"""Format discipline: make G emit code, and extract it deterministically.

Pure stdlib. A candidate with no extractable code becomes code=None — an
automatic execution failure that still consumes budget (COMPUTE_ACCOUNTING.md).
The per-condition extraction rate is a standing diagnostic (METRICS.md).
"""

from __future__ import annotations

import re

SYSTEM_PROMPT = (
    "You are a Python programming assistant. Answer with a single fenced "
    "Python code block containing a complete solution, and nothing else."
)

FEEDBACK_TEMPLATE = (
    "Your previous attempt:\n```python\n{prev_code}\n```\n"
    "An external verifier estimated its probability of being correct at "
    "{score:.2f}. Write an improved complete solution as a single fenced "
    "Python code block."
)

_FENCE_RE = re.compile(r"```(?:python|py)?\s*\n(.*?)```", re.DOTALL)


def build_prompt(problem_prompt: str) -> str:
    return f"{problem_prompt.strip()}\n\nRespond with a single fenced Python code block."


def build_feedback_prompt(problem_prompt: str, prev_code: str, score: float) -> str:
    """Baseline B2's prompt — previous candidate + verifier feedback in context.
    The FULL loop must never use this (information-flow rule 2)."""
    return build_prompt(problem_prompt) + "\n\n" + FEEDBACK_TEMPLATE.format(
        prev_code=prev_code, score=score
    )


def extract_code(completion: str) -> str | None:
    """First fenced code block; falls back to whole text iff it parses as code
    heuristically (starts with def/import/from/class). None otherwise."""
    match = _FENCE_RE.search(completion)
    if match:
        code = match.group(1).strip()
        return code or None
    stripped = completion.strip()
    if re.match(r"^(def |import |from |class )", stripped):
        return stripped
    return None
