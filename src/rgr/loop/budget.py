"""Compute ledger — the enforcement arm of docs/COMPUTE_ACCOUNTING.md.

Primary budgeted unit: candidate generations. Everything else (verifier calls,
update calls, token counts) is recorded for the audit columns. Evaluation code
uses ``assert_matched`` before comparing conditions; unequal generation counts
are an error, not a warning, except in H3 mean-matched mode.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass
class ComputeLedger:
    generations: int = 0
    verifier_calls: int = 0
    update_calls: int = 0
    prompt_tokens: int = 0
    generated_tokens: int = 0

    def charge_generation(self, prompt_tokens: int = 0, generated_tokens: int = 0) -> None:
        self.generations += 1
        self.prompt_tokens += prompt_tokens
        self.generated_tokens += generated_tokens

    def charge_verifier(self) -> None:
        self.verifier_calls += 1

    def charge_update(self) -> None:
        self.update_calls += 1

    def as_dict(self) -> dict[str, int]:
        return asdict(self)


@dataclass
class BudgetReport:
    """Aggregate ledger over a set of trajectories, for the audit columns."""

    condition: str
    problems: int = 0
    total: ComputeLedger = field(default_factory=ComputeLedger)

    def add(self, ledger: ComputeLedger) -> None:
        self.problems += 1
        self.total.generations += ledger.generations
        self.total.verifier_calls += ledger.verifier_calls
        self.total.update_calls += ledger.update_calls
        self.total.prompt_tokens += ledger.prompt_tokens
        self.total.generated_tokens += ledger.generated_tokens

    @property
    def mean_generations(self) -> float:
        return self.total.generations / self.problems if self.problems else 0.0


class ComputeMismatchError(ValueError):
    pass


def assert_matched(reports: list[BudgetReport], mean_matched: bool = False, tolerance: float = 0.0) -> None:
    """Refuse to compare conditions at unequal compute.

    Exact mode (H2): every condition must have identical total generations.
    Mean-matched mode (H3): mean generations per problem must agree within
    ``tolerance`` (adaptive stopping can't hit an integer exactly).
    """
    if len(reports) < 2:
        return
    if mean_matched:
        means = [r.mean_generations for r in reports]
        if max(means) - min(means) > tolerance:
            raise ComputeMismatchError(
                f"mean generations differ beyond tolerance {tolerance}: "
                + ", ".join(f"{r.condition}={r.mean_generations:.2f}" for r in reports)
            )
    else:
        totals = {r.total.generations for r in reports}
        if len(totals) > 1:
            raise ComputeMismatchError(
                "total generations differ: "
                + ", ".join(f"{r.condition}={r.total.generations}" for r in reports)
            )
