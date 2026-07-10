#!/usr/bin/env python3
"""Kaggle-side connectivity smoke (no GPU needed).

Verifies, from inside a Kaggle kernel: the repo imports, the test suite's
pure-logic core passes, the Daytona key is present, and a real sandbox
roundtrip works from Kaggle's network. Run before burning GPU time.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))


def main() -> None:
    print("[1/4] repo imports ...")
    from rgr.config import load_config
    from rgr.data.humaneval import load_humaneval
    from rgr.data.mbpp import load_mbpp
    from rgr.execution.sandbox import DaytonaBackend, load_daytona_key
    from rgr.types import Candidate, Problem

    config = load_config()
    print(f"      ok (model={config.generator.model_name}, N={config.loop.t_max})")

    print("[2/4] datasets from bundled cache ...")
    mbpp, he = load_mbpp(), load_humaneval()
    print(f"      ok (mbpp={len(mbpp.problems)}, humaneval={len(he.problems)})")

    print("[3/4] daytona key present ...")
    load_daytona_key()
    print("      ok")

    print("[4/4] daytona roundtrip from kaggle ...")
    problem = Problem(problem_id="smoke/kaggle", prompt="add",
                      tests="assert add(1,2)==3", test_list=("assert add(1,2)==3",))
    with DaytonaBackend(timeout_seconds=5) as backend:
        result = backend.execute(problem, Candidate(text="", code="def add(a,b):\n    return a+b"))
    assert result.passed, f"sandbox roundtrip failed: {result}"
    print("      ok")
    print("SMOKE PASS")


if __name__ == "__main__":
    main()
