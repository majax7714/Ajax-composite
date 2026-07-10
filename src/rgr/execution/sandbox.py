"""Execution backends: (problem, candidate) -> ExecutionResult.

Safe execution is non-negotiable (brief §4). The sanctioned backend is Daytona
(the existing rollout harness). LocalUnsafeBackend exists for smoke tests on
trusted toy problems ONLY and refuses to run without RGR_ALLOW_LOCAL_EXEC=1.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Protocol

from rgr.types import Candidate, ExecutionResult, Problem


class ExecutionBackend(Protocol):
    def execute(self, problem: Problem, candidate: Candidate) -> ExecutionResult:
        ...


def no_code_result() -> ExecutionResult:
    return ExecutionResult(passed=False, frac_tests=0.0, error_type="no_code")


class DaytonaBackend:
    """Wrapper around the existing Daytona rollout harness (brief §4).

    To wire in Phase 0: point this at the standing harness — create/reuse a
    sandbox, write candidate code + problem tests, run with the configured
    timeout, map the outcome to ExecutionResult {passed, frac_tests,
    error_type}. Must count individual test outcomes (frac_tests is an
    auxiliary training target for V), not just overall pass/fail.
    """

    def __init__(self, timeout_seconds: int = 10) -> None:
        self.timeout_seconds = timeout_seconds

    def execute(self, problem: Problem, candidate: Candidate) -> ExecutionResult:
        if candidate.code is None:
            return no_code_result()
        raise NotImplementedError("Phase 0: wire the Daytona rollout harness")


class LocalUnsafeBackend:
    """Subprocess execution on THIS machine. Dev smoke tests only.

    Runs model-generated code locally with no isolation beyond a timeout.
    Guarded: raises unless RGR_ALLOW_LOCAL_EXEC=1 is set explicitly. Never use
    for label generation or evaluation runs.
    """

    def __init__(self, timeout_seconds: int = 10) -> None:
        if os.environ.get("RGR_ALLOW_LOCAL_EXEC") != "1":
            raise RuntimeError(
                "LocalUnsafeBackend executes untrusted code on this machine. "
                "Set RGR_ALLOW_LOCAL_EXEC=1 only for smoke tests on trusted "
                "toy problems; use the Daytona backend for everything real."
            )
        self.timeout_seconds = timeout_seconds

    def execute(self, problem: Problem, candidate: Candidate) -> ExecutionResult:
        if candidate.code is None:
            return no_code_result()
        source = f"{candidate.code}\n\n{problem.tests}\n"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidate_test.py"
            path.write_text(source)
            try:
                proc = subprocess.run(
                    [sys.executable, str(path)],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_seconds,
                    cwd=tmp,
                )
            except subprocess.TimeoutExpired:
                return ExecutionResult(passed=False, frac_tests=0.0, error_type="timeout")
        if proc.returncode == 0:
            return ExecutionResult(passed=True, frac_tests=1.0, error_type="")
        stderr = proc.stderr or ""
        if "SyntaxError" in stderr:
            error = "syntax"
        elif "AssertionError" in stderr:
            error = "wrong_answer"
        else:
            error = "runtime"
        # frac_tests is all-or-nothing here; per-test granularity is the
        # Daytona backend's job (aux target for V).
        return ExecutionResult(passed=False, frac_tests=0.0, error_type=error)


def make_backend(name: str, timeout_seconds: int) -> ExecutionBackend:
    if name == "daytona":
        return DaytonaBackend(timeout_seconds)
    if name == "local_unsafe":
        return LocalUnsafeBackend(timeout_seconds)
    raise ValueError(f"unknown execution backend: {name!r}")
