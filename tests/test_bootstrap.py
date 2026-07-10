import pytest

from rgr.evals.bootstrap import bootstrap_ci, spearman


def test_bootstrap_point_matches_statistic():
    data = [1.0, 2.0, 3.0, 4.0]
    result = bootstrap_ci(data, lambda s: sum(s) / len(s), n_resamples=200)
    assert result.point == pytest.approx(2.5)
    assert result.lo <= result.point <= result.hi


def test_bootstrap_deterministic_under_seed():
    data = list(range(20))
    stat = lambda s: sum(s) / len(s)  # noqa: E731
    a = bootstrap_ci(data, stat, n_resamples=500, seed=7)
    b = bootstrap_ci(data, stat, n_resamples=500, seed=7)
    assert (a.lo, a.hi) == (b.lo, b.hi)


def test_excludes_zero():
    # paired deltas all positive -> CI must exclude zero
    deltas = [0.1, 0.2, 0.15, 0.12, 0.18, 0.11, 0.3, 0.22]
    result = bootstrap_ci(deltas, lambda s: sum(s) / len(s), n_resamples=1000)
    assert result.excludes_zero
    # deltas straddling zero symmetrically -> CI should contain zero
    mixed = [-0.2, 0.2, -0.1, 0.1, -0.15, 0.15, -0.05, 0.05]
    result = bootstrap_ci(mixed, lambda s: sum(s) / len(s), n_resamples=1000)
    assert not result.excludes_zero


def test_spearman_perfect_monotone():
    assert spearman([1, 2, 3, 4], [10, 20, 30, 40]) == pytest.approx(1.0)
    assert spearman([1, 2, 3, 4], [40, 30, 20, 10]) == pytest.approx(-1.0)


def test_spearman_ties():
    # ties get average ranks; correlation stays defined
    value = spearman([1, 1, 2, 3], [1, 2, 3, 4])
    assert -1.0 <= value <= 1.0


def test_spearman_constant_raises():
    with pytest.raises(ValueError):
        spearman([1, 1, 1], [1, 2, 3])
