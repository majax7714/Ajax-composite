"""Register-dynamics diagnostics — collapse and blow-up detection (brief §8).

Pure stdlib: consumes the norms already recorded in StepRecords, so it runs in
analysis on any machine. Logged on every Phase >= 2 run, not optionally
(ARCHITECTURE.md). Thresholds are heuristics to *flag* runs for inspection,
not gates.
"""

from __future__ import annotations

from dataclasses import dataclass

from rgr.types import Trajectory


@dataclass(frozen=True)
class RegisterHealth:
    mean_norm: float
    max_norm: float
    mean_delta_norm: float
    collapsed: bool  # updates stopped moving: register is inert
    blown_up: bool  # norm ran away: dynamics unstable

    @property
    def healthy(self) -> bool:
        return not (self.collapsed or self.blown_up)


def register_health(
    trajectories: list[Trajectory],
    *,
    collapse_delta: float = 1e-3,
    blowup_norm: float = 1e3,
) -> RegisterHealth:
    norms = [
        s.register_norm
        for t in trajectories
        for s in t.steps
        if s.register_norm is not None
    ]
    deltas = [
        s.register_delta_norm
        for t in trajectories
        for s in t.steps
        if s.register_delta_norm is not None
    ]
    if not norms:
        raise ValueError("no register norms recorded — diagnostics require FULL trajectories")

    mean_norm = sum(norms) / len(norms)
    max_norm = max(norms)
    mean_delta = sum(deltas) / len(deltas) if deltas else 0.0
    return RegisterHealth(
        mean_norm=mean_norm,
        max_norm=max_norm,
        mean_delta_norm=mean_delta,
        collapsed=bool(deltas) and mean_delta < collapse_delta,
        blown_up=max_norm > blowup_norm,
    )


def final_register_variance(final_norm_by_problem: dict[str, float]) -> float:
    """Variance of final register norms across problems. Near-zero variance
    with nonzero deltas suggests convergence to a problem-independent fixed
    point — the register moved but learned nothing problem-specific."""
    values = list(final_norm_by_problem.values())
    if len(values) < 2:
        raise ValueError("need at least two problems")
    mean = sum(values) / len(values)
    return sum((v - mean) ** 2 for v in values) / (len(values) - 1)
