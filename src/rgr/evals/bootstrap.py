"""Problem-level bootstrap CIs (docs/METRICS.md).

Resampling is over PROBLEMS, never candidates — candidates within a problem are
correlated, and resampling them would understate the CI in FULL's favor.
"""

from __future__ import annotations

import random
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class BootstrapResult:
    point: float
    lo: float
    hi: float
    n_resamples: int

    @property
    def excludes_zero(self) -> bool:
        """The H2 gate check: CI strictly on one side of 0."""
        return self.lo > 0.0 or self.hi < 0.0


def bootstrap_ci(
    problems: Sequence[T],
    statistic: Callable[[Sequence[T]], float],
    *,
    n_resamples: int = 10_000,
    alpha: float = 0.05,
    seed: int = 17,
) -> BootstrapResult:
    """Percentile CI of ``statistic`` under problem-level resampling.

    ``statistic`` maps a sequence of per-problem records to a scalar. For H2
    deltas, each record carries both conditions' outcomes for that problem and
    the statistic is the paired difference — pairing stays intact because we
    resample whole problems.
    """
    if not problems:
        raise ValueError("no problems")
    rng = random.Random(seed)
    n = len(problems)
    stats = []
    for _ in range(n_resamples):
        sample = [problems[rng.randrange(n)] for _ in range(n)]
        stats.append(statistic(sample))
    stats.sort()
    lo_idx = int((alpha / 2) * n_resamples)
    hi_idx = min(int((1 - alpha / 2) * n_resamples), n_resamples - 1)
    return BootstrapResult(
        point=statistic(problems),
        lo=stats[lo_idx],
        hi=stats[hi_idx],
        n_resamples=n_resamples,
    )


def spearman(x: Sequence[float], y: Sequence[float]) -> float:
    """Spearman rank correlation (average ranks for ties). For H3
    depth-vs-difficulty."""
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("need two sequences of equal length >= 2")

    def ranks(values: Sequence[float]) -> list[float]:
        order = sorted(range(len(values)), key=lambda i: values[i])
        result = [0.0] * len(values)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
                j += 1
            avg_rank = (i + j) / 2 + 1
            for idx in order[i : j + 1]:
                result[idx] = avg_rank
            i = j + 1
        return result

    rx, ry = ranks(x), ranks(y)
    mx = sum(rx) / len(rx)
    my = sum(ry) / len(ry)
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    vx = sum((a - mx) ** 2 for a in rx)
    vy = sum((b - my) ** 2 for b in ry)
    if vx == 0 or vy == 0:
        raise ValueError("constant sequence has no rank correlation")
    return cov / (vx * vy) ** 0.5
