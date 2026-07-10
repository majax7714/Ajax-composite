import pytest

from rgr.data.splits import SplitViolation, tag, train_val_split
from rgr.types import Problem, SplitRole


def problems(source: str, n: int) -> list[Problem]:
    return [
        Problem(problem_id=f"{source}/{i}", prompt="p", tests="t", source=source)
        for i in range(n)
    ]


def test_humaneval_tagged_heldout_and_guarded():
    ds = tag("humaneval", problems("humaneval", 5))
    assert ds.role == SplitRole.HELDOUT_EVAL
    ds.checkout(SplitRole.HELDOUT_EVAL)  # allowed
    with pytest.raises(SplitViolation):
        ds.checkout(SplitRole.TRAIN)
    with pytest.raises(SplitViolation):
        ds.checkout(SplitRole.VALIDATION)


def test_mbpp_tagged_train():
    ds = tag("mbpp", problems("mbpp", 5))
    assert ds.role == SplitRole.TRAIN
    ds.checkout(SplitRole.TRAIN)  # allowed


def test_mixed_sources_rejected():
    with pytest.raises(SplitViolation):
        tag("mixed", problems("mbpp", 2) + problems("humaneval", 2))


def test_train_val_split_deterministic_and_disjoint():
    ds = tag("mbpp", problems("mbpp", 20))
    train_a, val_a = train_val_split(ds, 0.25, seed=3)
    train_b, val_b = train_val_split(ds, 0.25, seed=3)
    assert [p.problem_id for p in val_a.problems] == [p.problem_id for p in val_b.problems]
    assert len(val_a.problems) == 5
    ids_train = {p.problem_id for p in train_a.problems}
    ids_val = {p.problem_id for p in val_a.problems}
    assert not ids_train & ids_val
    assert len(ids_train | ids_val) == 20
    assert val_a.role == SplitRole.VALIDATION


def test_cannot_split_heldout():
    ds = tag("humaneval", problems("humaneval", 5))
    with pytest.raises(SplitViolation):
        train_val_split(ds, 0.2, seed=1)
