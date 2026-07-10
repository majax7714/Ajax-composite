"""Protocols the refinement loop is written against.

The loop (rgr.loop.refine) is pure control flow over these interfaces, so the
code that decides H2/H3 is unit-testable with fakes and never imports torch.
The torch-backed implementations live in rgr.generator / rgr.register /
rgr.verifier and satisfy these protocols structurally.

``Register`` is deliberately opaque to the loop: the loop moves it between
components and never inspects it. That opacity *is* the information-flow
contract (ARCHITECTURE.md §3) — nothing but U can read or write register state.
"""

from __future__ import annotations

from typing import Any, Protocol

from rgr.types import Candidate, Problem

Register = Any


class GeneratorLike(Protocol):
    def generate(self, problem: Problem, register: Register | None) -> Candidate:
        """Sample one candidate conditioned on the problem and (if not None)
        the register via soft-prompt injection. ``register=None`` means no
        injection at all (condition B1')."""
        ...


class FeedbackGeneratorLike(Protocol):
    """Baseline B2 only. The FULL loop has no path to this interface."""

    def generate_with_feedback(
        self, problem: Problem, prev: Candidate, verifier_score: float
    ) -> Candidate:
        ...


class VerifierLike(Protocol):
    def score(self, problem: Problem, candidate: Candidate, register: Register | None) -> float:
        """P(correct) in [0, 1]. ``register`` is passed but implementations
        must ignore it while verifier.sees_register is false (D3)."""
        ...


class RegisterInitLike(Protocol):
    def init(self, problem: Problem) -> Register:
        """r_0(problem) — problem-encoded per D4."""
        ...


class NoRegister:
    """Init+update adapter for register-free conditions (Phase 0: no register
    modules exist yet). init() -> None means the generator injects nothing;
    update is the identity on None. Satisfies RegisterInitLike and
    RegisterUpdateLike."""

    def init(self, problem: Problem) -> None:
        return None

    def update(self, register, candidate: Candidate, verifier_score: float) -> None:
        return None

    def norm(self, register) -> float:
        return 0.0

    def delta_norm(self, before, after) -> float:
        return 0.0


class RegisterUpdateLike(Protocol):
    def update(self, register: Register, candidate: Candidate, verifier_score: float) -> Register:
        """r_{t+1} = U(r_t, phi(candidate), v). The ONLY cross-step channel."""
        ...

    def norm(self, register: Register) -> float:
        """||r|| for diagnostics (rgr.register.diagnostics)."""
        ...

    def delta_norm(self, before: Register, after: Register) -> float:
        """||r_{t+1} - r_t|| for collapse/blow-up detection."""
        ...
