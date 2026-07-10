"""Sandbox driver: the program that runs (candidate, tests) inside the sandbox.

Pure stdlib on both sides. ``build_driver`` emits a self-contained Python
script; the sandbox runs it; ``parse_driver_output`` maps its stdout back to
ExecutionResult. The candidate and tests are embedded as a JSON literal, so no
escaping games and no shell quoting anywhere.

The driver prints exactly one line starting with RESULT_MARKER, last, so
candidate stdout noise can't corrupt the verdict. Anything without that marker
(driver crash, sandbox OOM) parses as error_type="sandbox".

Per-test granularity: when test_list is provided, each statement runs
independently in a copy-free namespace (tests share the candidate's namespace
but candidates are re-exec'd fresh per call, and MBPP asserts are read-only) —
frac_tests = passed/total, V's auxiliary target. A lone test block gives 0/1.

Timeouts: signal.alarm inside the driver (per candidate exec and per test), so
an infinite-loop candidate yields error_type="timeout" without killing the
sandbox session; the SDK-level timeout stays as the hard backstop.
"""

from __future__ import annotations

import json

from rgr.types import Candidate, ExecutionResult, Problem

RESULT_MARKER = "RGR_RESULT::"

_DRIVER_TEMPLATE = '''
import json, signal, sys

PAYLOAD = json.loads({payload_json!r})

class _Timeout(Exception):
    pass

def _alarm(signum, frame):
    raise _Timeout()

signal.signal(signal.SIGALRM, _alarm)

result = {{"error_type": "", "tests_passed": 0, "tests_total": 0}}
namespace = {{"__name__": "__main__"}}

def emit():
    sys.stdout.flush()
    print()
    print({marker!r} + json.dumps(result))
    sys.exit(0)

# --- candidate ---
try:
    signal.alarm(PAYLOAD["timeout"])
    exec(compile(PAYLOAD["code"], "<candidate>", "exec"), namespace)
    signal.alarm(0)
except SyntaxError:
    result["error_type"] = "syntax"
    emit()
except _Timeout:
    result["error_type"] = "timeout"
    emit()
except BaseException:
    result["error_type"] = "runtime"
    emit()

# --- test setup (dataset-provided imports; a failure fails all tests) ---
tests = PAYLOAD["test_list"] or [PAYLOAD["test_block"]]
result["tests_total"] = len(tests)
if PAYLOAD["test_setup"]:
    try:
        signal.alarm(PAYLOAD["timeout"])
        exec(compile(PAYLOAD["test_setup"], "<setup>", "exec"), namespace)
        signal.alarm(0)
    except BaseException:
        result["error_type"] = "runtime"
        emit()

first_error = ""
for test in tests:
    try:
        signal.alarm(PAYLOAD["timeout"])
        exec(compile(test, "<test>", "exec"), namespace)
        signal.alarm(0)
        result["tests_passed"] += 1
    except _Timeout:
        first_error = first_error or "timeout"
    except AssertionError:
        first_error = first_error or "wrong_answer"
    except BaseException:
        first_error = first_error or "runtime"
result["error_type"] = "" if result["tests_passed"] == result["tests_total"] else first_error
emit()
'''


def build_driver(problem: Problem, candidate: Candidate, timeout_seconds: int) -> str:
    """Driver source for one (problem, candidate). Candidate must have code."""
    if candidate.code is None:
        raise ValueError("no-code candidates never reach the sandbox (see no_code_result)")
    payload = json.dumps(
        {
            "code": candidate.code,
            "test_list": list(problem.test_list),
            "test_block": problem.tests,
            "test_setup": problem.test_setup,
            "timeout": timeout_seconds,
        }
    )
    return _DRIVER_TEMPLATE.format(payload_json=payload, marker=RESULT_MARKER)


def parse_driver_output(stdout: str) -> ExecutionResult:
    """Map driver stdout to ExecutionResult. Missing marker => sandbox fault."""
    marker_line = None
    for line in stdout.splitlines():
        if line.startswith(RESULT_MARKER):
            marker_line = line  # keep the last one; candidate noise can't fake it after ours
    if marker_line is None:
        return ExecutionResult(passed=False, frac_tests=0.0, error_type="sandbox")
    try:
        raw = json.loads(marker_line[len(RESULT_MARKER):])
    except json.JSONDecodeError:
        return ExecutionResult(passed=False, frac_tests=0.0, error_type="sandbox")
    total = raw.get("tests_total", 0)
    passed_count = raw.get("tests_passed", 0)
    frac = passed_count / total if total else 0.0
    return ExecutionResult(
        passed=total > 0 and passed_count == total,
        frac_tests=frac,
        error_type=raw.get("error_type", "sandbox"),
    )
