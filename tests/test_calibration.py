import pytest

from rgr.evals.calibration import auroc, brier, ece, minmax_normalize


def test_auroc_perfect_ranking():
    assert auroc([0.9, 0.8, 0.2, 0.1], [True, True, False, False]) == 1.0


def test_auroc_inverted_ranking():
    assert auroc([0.1, 0.2, 0.8, 0.9], [True, True, False, False]) == 0.0


def test_auroc_chance():
    assert auroc([0.5, 0.5, 0.5, 0.5], [True, False, True, False]) == pytest.approx(0.5)


def test_auroc_ties_half_credit():
    # pos=[0.5], neg=[0.5, 0.1]: one win over 0.1, one tie -> (1 + 0.5)/2
    assert auroc([0.5, 0.5, 0.1], [True, False, False]) == pytest.approx(0.75)


def test_auroc_monotone_invariance():
    scores = [0.1, 0.4, 0.35, 0.8, 0.7]
    labels = [False, False, True, True, False]
    logits = [s * 10 - 3 for s in scores]  # monotone transform
    assert auroc(scores, labels) == pytest.approx(auroc(logits, labels))


def test_auroc_single_class_raises():
    with pytest.raises(ValueError):
        auroc([0.5, 0.6], [True, True])


def test_brier():
    assert brier([1.0, 0.0], [True, False]) == 0.0
    assert brier([0.0, 1.0], [True, False]) == 1.0
    assert brier([0.5], [True]) == pytest.approx(0.25)


def test_ece_perfectly_calibrated_bins():
    # bin [0.7, 0.8): confidences 0.7, 0.7, 0.7, 0.7 with 70% wrong->approx
    probs = [0.75] * 4
    labels = [True, True, True, False]
    assert ece(probs, labels, n_bins=10) == pytest.approx(0.0)


def test_ece_overconfident():
    assert ece([0.95] * 4, [False] * 4, n_bins=10) == pytest.approx(0.95)


def test_ece_rejects_non_probabilities():
    with pytest.raises(ValueError):
        ece([1.5], [True])


def test_minmax():
    assert minmax_normalize([-2.0, 0.0, 2.0]) == [0.0, 0.5, 1.0]
    assert minmax_normalize([3.0, 3.0]) == [0.5, 0.5]
