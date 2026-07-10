"""Calibration metrics for H1: AUROC (primary), ECE and Brier (secondary).

Pure stdlib implementations per docs/METRICS.md. AUROC uses the Mann-Whitney
rank formulation with ties counted 1/2, so it is invariant to monotone
transforms — verifier probabilities and raw log-likelihoods compare fairly
without normalization.
"""

from __future__ import annotations


def auroc(scores: list[float], labels: list[bool]) -> float:
    """P(score_positive > score_negative) + 0.5 * P(tie)."""
    if len(scores) != len(labels):
        raise ValueError("scores and labels differ in length")
    pos = sorted(s for s, y in zip(scores, labels) if y)
    neg = sorted(s for s, y in zip(scores, labels) if not y)
    if not pos or not neg:
        raise ValueError("AUROC needs both classes present")

    # O((P+N) log) two-pointer sweep over sorted lists.
    wins = ties = 0.0
    i = j = 0  # neg pointers: strictly-less count and less-or-equal count
    for p in pos:
        while i < len(neg) and neg[i] < p:
            i += 1
        while j < len(neg) and neg[j] <= p:
            j += 1
        wins += i
        ties += j - i
    return (wins + 0.5 * ties) / (len(pos) * len(neg))


def brier(probs: list[float], labels: list[bool]) -> float:
    """Mean squared error of probability vs {0,1} outcome."""
    if len(probs) != len(labels):
        raise ValueError("probs and labels differ in length")
    if not probs:
        raise ValueError("empty input")
    return sum((p - float(y)) ** 2 for p, y in zip(probs, labels)) / len(probs)


def ece(probs: list[float], labels: list[bool], n_bins: int = 10) -> float:
    """Expected calibration error, equal-width bins on [0, 1].

    Inputs must already be probabilities; normalize log-likelihoods first
    (min-max per dataset — see METRICS.md caveat) via ``minmax_normalize``.
    """
    if len(probs) != len(labels):
        raise ValueError("probs and labels differ in length")
    if not probs:
        raise ValueError("empty input")
    if any(not 0.0 <= p <= 1.0 for p in probs):
        raise ValueError("ECE requires probabilities in [0, 1]")

    bins: list[list[tuple[float, bool]]] = [[] for _ in range(n_bins)]
    for p, y in zip(probs, labels):
        idx = min(int(p * n_bins), n_bins - 1)
        bins[idx].append((p, y))

    total = len(probs)
    err = 0.0
    for members in bins:
        if not members:
            continue
        conf = sum(p for p, _ in members) / len(members)
        acc = sum(1.0 for _, y in members if y) / len(members)
        err += (len(members) / total) * abs(acc - conf)
    return err


def minmax_normalize(values: list[float]) -> list[float]:
    """Map to [0, 1]; constant input maps to 0.5."""
    lo, hi = min(values), max(values)
    if hi == lo:
        return [0.5] * len(values)
    return [(v - lo) / (hi - lo) for v in values]
