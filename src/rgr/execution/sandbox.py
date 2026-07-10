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


def load_daytona_key(key_file: str | Path = "rgb-daytona.txt") -> str:
    """DAYTONA_API_KEY env var, else the gitignored key file at the repo root."""
    key = os.environ.get("DAYTONA_API_KEY", "").strip()
    if key:
        return key
    path = Path(key_file)
    if not path.is_absolute():
        path = Path(__file__).parents[3] / path
    if path.exists():
        key = path.read_text().strip()
        if key:
            return key
    raise RuntimeError(
        "no Daytona API key: set DAYTONA_API_KEY or provide the key file "
        f"(looked at {path})"
    )


class DaytonaBackend:
    """Daytona cloud sandbox via the `daytona` SDK (lazy import — GPU boxes
    and label runs need it, the local test suite does not).

    One sandbox is created lazily and reused across executions — creation
    costs seconds, a code_run costs a fraction of that, and label generation
    is thousands of executions (brief §7). The driver's internal
    signal.alarm handles hung candidates, so the sandbox survives timeouts;
    if the sandbox itself dies (SDK error), it is torn down and the next
    execute() recreates it. Call close() when done.
    """

    def __init__(self, timeout_seconds: int = 10, api_key: str | None = None) -> None:
        self.timeout_seconds = timeout_seconds
        self._api_key = api_key or load_daytona_key()
        self._client = None
        self._sandbox = None

    def _get_sandbox(self):
        from daytona import Daytona, DaytonaConfig

        if self._client is None:
            self._client = Daytona(DaytonaConfig(api_key=self._api_key))
        if self._sandbox is None:
            self._sandbox = self._client.create()
        return self._sandbox

    def execute(self, problem: Problem, candidate: Candidate) -> ExecutionResult:
        from rgr.execution.driver import build_driver, parse_driver_output

        if candidate.code is None:
            return no_code_result()
        driver = build_driver(problem, candidate, self.timeout_seconds)
        # Hard backstop above the driver's own alarms: candidate exec + each
        # test can each burn up to timeout_seconds inside the driver.
        sdk_timeout = self.timeout_seconds * (2 + len(problem.test_list)) + 30
        try:
            sandbox = self._get_sandbox()
            response = sandbox.process.code_run(driver, timeout=sdk_timeout)
        except Exception:
            self._teardown()  # sandbox state unknown — recreate on next call
            return ExecutionResult(passed=False, frac_tests=0.0, error_type="sandbox")
        return parse_driver_output(response.result or "")

    def _teardown(self) -> None:
        sandbox, self._sandbox = self._sandbox, None
        if sandbox is not None:
            try:
                sandbox.delete()
            except Exception:
                pass  # already gone; Daytona auto-stops idle sandboxes

    def close(self) -> None:
        self._teardown()

    def __enter__(self) -> "DaytonaBackend":
        return self

    def __exit__(self, *exc_info) -> None:
        self.close()


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


def make_backend(name: str, timeout_seconds: int, api_key: str | None = None) -> ExecutionBackend:
    if name == "daytona":
        return DaytonaBackend(timeout_seconds, api_key=api_key)
    if name == "local_unsafe":
        return LocalUnsafeBackend(timeout_seconds)
    raise ValueError(f"unknown execution backend: {name!r}")
