"""pass@k with the unbiased estimator (Chen et al., 2021). Spec: docs/METRICS.md."""

from __future__ import annotations

from math import comb


def pass_at_k(n: int, c: int, k: int) -> float:
    """Unbiased pass@k for one problem: n samples, c of them correct.

    pass@k = 1 - C(n-c, k) / C(n, k). Raises if k > n — silently truncating
    would quietly change the estimator.
    """
    if not 0 <= c <= n:
        raise ValueError(f"need 0 <= c <= n, got n={n} c={c}")
    if not 1 <= k <= n:
        raise ValueError(f"need 1 <= k <= n, got n={n} k={k}")
    if n - c < k:
        return 1.0
    return 1.0 - comb(n - c, k) / comb(n, k)


def mean_pass_at_k(counts: list[tuple[int, int]], k: int) -> float:
    """Mean over problems of pass@k. ``counts`` is [(n_i, c_i), ...]."""
    if not counts:
        raise ValueError("no problems")
    return sum(pass_at_k(n, c, k) for n, c in counts) / len(counts)


def pass_at_1_by_selection(selected_passed: list[bool]) -> float:
    """Deployment pass@1: fraction of problems where the *selected* candidate
    (verifier argmax) passed. This is the headline correctness number for every
    condition with a verifier (METRICS.md)."""
    if not selected_passed:
        raise ValueError("no problems")
    return sum(selected_passed) / len(selected_passed)
