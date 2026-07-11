import threading

import pytest

from rgr.training.labels import ExecutionPool, split_counts
from rgr.types import Candidate, ExecutionResult, Problem

PROBLEM = Problem(problem_id="toy/1", prompt="p", tests="t")


def test_split_counts_even():
    assert split_counts(15, [0.2, 0.8, 1.0]) == [(0.2, 5), (0.8, 5), (1.0, 5)]


def test_split_counts_remainder_to_high_temps():
    assert split_counts(16, [0.2, 0.8, 1.0]) == [(0.2, 5), (0.8, 5), (1.0, 6)]
    assert split_counts(17, [0.2, 0.8, 1.0]) == [(0.2, 5), (0.8, 6), (1.0, 6)]


def test_split_counts_single_temp():
    assert split_counts(8, [0.8]) == [(0.8, 8)]


def test_split_counts_too_few_raises():
    with pytest.raises(ValueError):
        split_counts(2, [0.2, 0.8, 1.0])


class FakeBackend:
    """Records concurrent use so the pool's one-job-per-backend rule is testable."""

    def __init__(self):
        self.busy = False
        self.calls = 0
        self.overlap = False
        self.lock = threading.Lock()

    def execute(self, problem, candidate):
        with self.lock:
            if self.busy:
                self.overlap = True
            self.busy = True
        self.calls += 1
        result = ExecutionResult(passed=candidate.code == "good", frac_tests=1.0)
        with self.lock:
            self.busy = False
        return result

    def close(self):
        self.closed = True


def test_pool_executes_all_in_order():
    backends = []

    def factory():
        backend = FakeBackend()
        backends.append(backend)
        return backend

    pool = ExecutionPool(factory, size=3)
    candidates = [Candidate(text="", code="good" if i % 2 == 0 else "bad") for i in range(10)]
    results = pool.execute_all(PROBLEM, candidates)
    pool.close()

    assert len(results) == 10
    # order preserved: result i corresponds to candidate i
    assert [r.passed for r in results] == [i % 2 == 0 for i in range(10)]
    assert sum(b.calls for b in backends) == 10
    assert not any(b.overlap for b in backends)
    assert all(getattr(b, "closed", False) for b in backends)
