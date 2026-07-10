import pytest

from rgr.register.diagnostics import final_register_variance, register_health
from rgr.types import Candidate, StepRecord, Trajectory


def trajectory(norms_and_deltas: list[tuple[float, float | None]]) -> Trajectory:
    t = Trajectory(problem_id="toy/1", condition="full")
    for i, (norm, delta) in enumerate(norms_and_deltas):
        t.steps.append(
            StepRecord(
                step=i,
                candidate=Candidate(text="x", code="x"),
                verifier_score=0.5,
                register_norm=norm,
                register_delta_norm=delta,
            )
        )
    return t


def test_healthy_dynamics():
    health = register_health([trajectory([(11.3, 0.8), (11.3, 0.6), (11.3, None)])])
    assert health.healthy
    assert health.mean_delta_norm == pytest.approx(0.7)


def test_collapse_detected():
    health = register_health([trajectory([(11.3, 1e-5), (11.3, 1e-6), (11.3, None)])])
    assert health.collapsed
    assert not health.healthy


def test_blowup_detected():
    health = register_health([trajectory([(10.0, 500.0), (5e3, 500.0), (1e4, None)])])
    assert health.blown_up
    assert not health.healthy


def test_requires_recorded_norms():
    empty = Trajectory(problem_id="toy/2", condition="b1")
    with pytest.raises(ValueError):
        register_health([empty])


def test_final_variance():
    assert final_register_variance({"a": 1.0, "b": 1.0, "c": 1.0}) == 0.0
    assert final_register_variance({"a": 0.0, "b": 2.0}) == pytest.approx(2.0)
