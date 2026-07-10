"""Run persistence: trajectories + execution outcomes -> JSONL, and back.

Records are flat JSON so the dashboard and audits never need to unpickle
anything. Every record embeds its ledger (COMPUTE_ACCOUNTING.md: "audits never
require a rerun") and the config tag + seed that produced it.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from rgr.types import ExecutionResult, Trajectory


def trajectory_record(
    trajectory: Trajectory,
    executions: list[ExecutionResult | None],
    *,
    tag: str,
    seed: int,
) -> dict[str, Any]:
    """One JSON record per (problem, condition) run.

    ``executions[i]`` is the sandbox verdict for step i's candidate, or None
    if that candidate was not executed (execution policy is the caller's:
    Phase 0 executes everything; deployment-style eval executes only the
    selected candidate).
    """
    if len(executions) != len(trajectory.steps):
        raise ValueError("one execution slot per step required (use None for unexecuted)")
    return {
        "problem_id": trajectory.problem_id,
        "condition": trajectory.condition,
        "tag": tag,
        "seed": seed,
        "stopped_early": trajectory.stopped_early,
        "best_index": trajectory.best_index,
        "ledger": trajectory.ledger.as_dict() if trajectory.ledger else None,
        "steps": [
            {
                "step": s.step,
                "verifier_score": s.verifier_score,
                "register_norm": s.register_norm,
                "register_delta_norm": s.register_delta_norm,
                "text": s.candidate.text,
                "code": s.candidate.code,
                "mean_logprob": s.candidate.mean_logprob,
                "prompt_tokens": s.candidate.prompt_tokens,
                "generated_tokens": s.candidate.generated_tokens,
                "execution": (
                    {
                        "passed": e.passed,
                        "frac_tests": e.frac_tests,
                        "error_type": e.error_type,
                    }
                    if e is not None
                    else None
                ),
            }
            for s, e in zip(trajectory.steps, executions)
        ],
    }


def write_jsonl(path: str | Path, records: list[dict[str, Any]]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")


def append_jsonl(path: str | Path, record: dict[str, Any]) -> None:
    """Incremental write so an interrupted run keeps its finished problems."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(record) + "\n")


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def n_correct(record: dict[str, Any]) -> tuple[int, int]:
    """(n_executed, n_passed) over a record's steps — the (n, c) that pass@k
    and the difficulty proxy consume."""
    executed = [s["execution"] for s in record["steps"] if s["execution"] is not None]
    return len(executed), sum(1 for e in executed if e["passed"])


def selected_passed(record: dict[str, Any]) -> bool:
    """Did the verifier-selected candidate pass? (Deployment pass@1.)"""
    execution = record["steps"][record["best_index"]]["execution"]
    if execution is None:
        raise ValueError(f"{record['problem_id']}: selected candidate was not executed")
    return execution["passed"]
