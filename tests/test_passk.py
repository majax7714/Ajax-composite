import pytest

from rgr.evals.passk import mean_pass_at_k, pass_at_1_by_selection, pass_at_k


def test_all_correct():
    assert pass_at_k(10, 10, 1) == 1.0
    assert pass_at_k(10, 10, 5) == 1.0


def test_none_correct():
    assert pass_at_k(10, 0, 1) == 0.0
    assert pass_at_k(10, 0, 10) == 0.0


def test_pass_at_1_is_fraction():
    assert pass_at_k(10, 3, 1) == pytest.approx(0.3)


def test_known_value():
    # n=4, c=1, k=2: 1 - C(3,2)/C(4,2) = 1 - 3/6 = 0.5
    assert pass_at_k(4, 1, 2) == pytest.approx(0.5)


def test_guaranteed_when_failures_fewer_than_k():
    # n=5, c=4 -> only 1 failure; any k>=2 sample must contain a pass
    assert pass_at_k(5, 4, 2) == 1.0


def test_k_greater_than_n_raises():
    with pytest.raises(ValueError):
        pass_at_k(4, 2, 5)


def test_c_out_of_range_raises():
    with pytest.raises(ValueError):
        pass_at_k(4, 5, 2)


def test_mean_pass_at_k():
    assert mean_pass_at_k([(4, 4, ), (4, 0)], 1) == pytest.approx(0.5)


def test_selection_pass_at_1():
    assert pass_at_1_by_selection([True, False, True, True]) == pytest.approx(0.75)
