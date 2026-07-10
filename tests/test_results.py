import pytest

from rgr.loop.budget import ComputeLedger
from rgr.results import (
    append_jsonl,
    n_correct,
    read_jsonl,
    selected_passed,
    trajectory_record,
    write_jsonl,
)
from rgr.types import Candidate, ExecutionResult, StepRecord, Trajectory


def make_trajectory(scores: list[float]) -> Trajectory:
    ledger = ComputeLedger()
    t = Trajectory(problem_id="toy/1", condition="b1_likelihood", ledger=ledger)
    for i, score in enumerate(scores):
        ledger.charge_generation(10, 20)
        ledger.charge_verifier()
        t.steps.append(
            StepRecord(step=i, candidate=Candidate(text=f"c{i}", code=f"x={i}"), verifier_score=score)
        )
    return t


def executions(passes: list[bool]) -> list[ExecutionResult]:
    return [ExecutionResult(passed=p, frac_tests=1.0 if p else 0.0) for p in passes]


def test_roundtrip(tmp_path):
    record = trajectory_record(make_trajectory([0.1, 0.9]), executions([False, True]), tag="t", seed=1)
    path = tmp_path / "out.jsonl"
    write_jsonl(path, [record])
    append_jsonl(path, record)
    loaded = read_jsonl(path)
    assert len(loaded) == 2
    assert loaded[0] == record
    assert loaded[0]["ledger"]["generations"] == 2


def test_n_correct_and_selection():
    record = trajectory_record(
        make_trajectory([0.1, 0.9, 0.5]), executions([True, True, False]), tag="t", seed=1
    )
    assert n_correct(record) == (3, 2)
    assert selected_passed(record)  # argmax score is step 1, which passed


def test_selection_of_failing_candidate():
    record = trajectory_record(
        make_trajectory([0.9, 0.1]), executions([False, True]), tag="t", seed=1
    )
    assert not selected_passed(record)  # reranker picked the failing one


def test_unexecuted_slots():
    record = trajectory_record(
        make_trajectory([0.1, 0.9]), [None, ExecutionResult(passed=True, frac_tests=1.0)],
        tag="t", seed=1,
    )
    assert n_correct(record) == (1, 1)
    assert selected_passed(record)


def test_unexecuted_selected_raises():
    record = trajectory_record(
        make_trajectory([0.9, 0.1]), [None, ExecutionResult(passed=True, frac_tests=1.0)],
        tag="t", seed=1,
    )
    with pytest.raises(ValueError):
        selected_passed(record)


def test_execution_count_mismatch_raises():
    with pytest.raises(ValueError):
        trajectory_record(make_trajectory([0.5]), [], tag="t", seed=1)
