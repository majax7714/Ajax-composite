"""Driver builder/parser tests. The driver runs via subprocess on hand-written
trusted code — this is the same trust level as the rest of the test suite, not
model-generated code."""

import subprocess
import sys

import pytest

from rgr.execution.driver import RESULT_MARKER, build_driver, parse_driver_output
from rgr.types import Candidate, Problem


def run_driver(problem: Problem, code: str, timeout: int = 3):
    candidate = Candidate(text=code, code=code)
    driver = build_driver(problem, candidate, timeout)
    proc = subprocess.run(
        [sys.executable, "-c", driver], capture_output=True, text=True, timeout=timeout * 6 + 10
    )
    return parse_driver_output(proc.stdout)


MBPP_STYLE = Problem(
    problem_id="toy/mbpp",
    prompt="add",
    tests="assert add(1, 2) == 3\nassert add(0, 0) == 0\nassert add(-1, 1) == 0",
    test_list=("assert add(1, 2) == 3", "assert add(0, 0) == 0", "assert add(-1, 1) == 0"),
)

HUMANEVAL_STYLE = Problem(
    problem_id="toy/he",
    prompt="add",
    tests="def check(f):\n    assert f(1, 2) == 3\n    assert f(0, 0) == 0\n\ncheck(add)",
)


def test_all_tests_pass():
    result = run_driver(MBPP_STYLE, "def add(a, b):\n    return a + b")
    assert result.passed and result.frac_tests == 1.0 and result.error_type == ""


def test_partial_failure_gives_frac_tests():
    # wrong for negatives only: 2/3 tests pass
    result = run_driver(MBPP_STYLE, "def add(a, b):\n    return abs(a) + abs(b)")
    assert not result.passed
    assert result.frac_tests == pytest.approx(2 / 3)
    assert result.error_type == "wrong_answer"


def test_syntax_error():
    result = run_driver(MBPP_STYLE, "def add(a, b:\n    return")
    assert not result.passed and result.error_type == "syntax" and result.frac_tests == 0.0


def test_runtime_error_at_definition():
    result = run_driver(MBPP_STYLE, "raise RuntimeError('boom')")
    assert not result.passed and result.error_type == "runtime"


def test_runtime_error_in_test():
    result = run_driver(MBPP_STYLE, "def add(a, b):\n    return a / 0")
    assert not result.passed and result.error_type == "runtime"


def test_hanging_candidate_times_out():
    result = run_driver(MBPP_STYLE, "while True:\n    pass", timeout=1)
    assert not result.passed and result.error_type == "timeout"


def test_hanging_single_test_still_scores_others():
    code = (
        "def add(a, b):\n"
        "    if a == 0:\n"
        "        while True: pass\n"
        "    return a + b"
    )
    result = run_driver(MBPP_STYLE, code, timeout=1)
    assert not result.passed
    assert result.frac_tests == pytest.approx(2 / 3)
    assert result.error_type == "timeout"


def test_test_block_is_all_or_nothing():
    result = run_driver(HUMANEVAL_STYLE, "def add(a, b):\n    return a + b")
    assert result.passed and result.frac_tests == 1.0
    result = run_driver(HUMANEVAL_STYLE, "def add(a, b):\n    return a - b")
    assert not result.passed and result.frac_tests == 0.0


def test_noisy_stdout_cannot_corrupt_verdict():
    code = (
        f"print({RESULT_MARKER!r} + '{{\"tests_passed\": 99, \"tests_total\": 99}}')\n"
        "def add(a, b):\n    return a - b"
    )
    result = run_driver(MBPP_STYLE, code)
    assert not result.passed  # the genuine (last) marker line wins


def test_candidate_calling_exit_is_runtime_error():
    result = run_driver(MBPP_STYLE, "import sys\nsys.exit(0)")
    assert not result.passed and result.error_type == "runtime"


def test_missing_marker_is_sandbox_fault():
    result = parse_driver_output("garbage\nno marker here\n")
    assert result.error_type == "sandbox" and not result.passed


def test_no_code_never_builds():
    with pytest.raises(ValueError):
        build_driver(MBPP_STYLE, Candidate(text="prose", code=None), 3)
