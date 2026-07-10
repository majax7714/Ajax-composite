"""Loop control-flow tests with fakes — the code that decides H2/H3.

The fakes model the essential physics: a register that improves generation
quality only when it is updated. That lets us assert the structural claims:
B1 (frozen register) is i.i.d. sampling, FULL benefits only through U, early
stopping charges only what it uses, and the ledger matches the accounting doc.
"""

from __future__ import annotations

from rgr.loop.baselines import run_b1_prime, run_b2
from rgr.loop.refine import run_refine
from rgr.types import Candidate, Problem

PROBLEM = Problem(problem_id="toy/1", prompt="add two numbers", tests="assert add(1,2)==3")


class FakeGenerator:
    """Quality equals the register value; records what it was conditioned on."""

    def __init__(self):
        self.registers_seen = []

    def generate(self, problem, register):
        self.registers_seen.append(register)
        quality = 0.0 if register is None else register
        return Candidate(
            text=f"q={quality}", code="def add(a,b): return a+b",
            prompt_tokens=10, generated_tokens=5,
        )

    def generate_with_feedback(self, problem, prev, verifier_score):
        return Candidate(
            text=prev.text + "+fb", code=prev.code,
            prompt_tokens=10 + prev.generated_tokens, generated_tokens=5,
        )


class FakeVerifier:
    def score(self, problem, candidate, register):
        return 0.0 if register is None else min(float(register) / 10.0, 1.0)


class FakeInit:
    def init(self, problem):
        return 1.0


class FakeUpdater:
    def update(self, register, candidate, verifier_score):
        return register + 1.0

    def norm(self, register):
        return abs(register)

    def delta_norm(self, before, after):
        return abs(after - before)


def run(t_max=4, **kwargs):
    return run_refine(
        PROBLEM, FakeGenerator(), FakeVerifier(), FakeInit(), FakeUpdater(),
        t_max=t_max, **kwargs,
    )


def test_full_register_advances_each_step():
    gen = FakeGenerator()
    trajectory = run_refine(
        PROBLEM, gen, FakeVerifier(), FakeInit(), FakeUpdater(), t_max=4,
    )
    assert gen.registers_seen == [1.0, 2.0, 3.0, 4.0]
    assert trajectory.condition == "full"
    assert trajectory.ledger.update_calls == 3  # no update after the last step


def test_frozen_register_is_iid_best_of_n():
    """The ablation contract: freeze_register makes every step identical to
    step 0 — i.e., B1 is exactly N independent samples conditioned on r_0."""
    gen = FakeGenerator()
    trajectory = run_refine(
        PROBLEM, gen, FakeVerifier(), FakeInit(), FakeUpdater(),
        t_max=4, freeze_register=True,
    )
    assert gen.registers_seen == [1.0, 1.0, 1.0, 1.0]
    assert trajectory.condition == "b1"
    assert trajectory.ledger.update_calls == 0


def test_best_candidate_is_verifier_argmax():
    trajectory = run(t_max=4)
    scores = [s.verifier_score for s in trajectory.steps]
    assert trajectory.best_score == max(scores)
    assert trajectory.best_index == scores.index(max(scores))


def test_early_stop_charges_only_used_compute():
    # register 1 -> score 0.1, register 2 -> 0.2, register 3 -> 0.3 >= tau=0.25
    # -> stops after the third generation
    trajectory = run(t_max=10, early_stop=True, tau=0.25)
    assert trajectory.stopped_early
    assert trajectory.num_generations == 3
    assert trajectory.ledger.generations == 3
    assert trajectory.condition == "full_adaptive"


def test_b0_is_t_max_1():
    trajectory = run(t_max=1)
    assert trajectory.condition == "b0"
    assert trajectory.ledger.generations == 1
    assert trajectory.ledger.update_calls == 0


def test_ledger_token_accounting():
    trajectory = run(t_max=4)
    assert trajectory.ledger.generations == 4
    assert trajectory.ledger.prompt_tokens == 40
    assert trajectory.ledger.generated_tokens == 20
    assert trajectory.ledger.verifier_calls == 4


def test_b1_prime_no_injection():
    gen = FakeGenerator()
    trajectory = run_b1_prime(PROBLEM, gen, FakeVerifier(), n=4)
    assert gen.registers_seen == [None, None, None, None]
    assert trajectory.condition == "b1_prime"
    assert trajectory.ledger.generations == 4


def test_b2_same_generation_budget_but_growing_prompts():
    gen = FakeGenerator()
    trajectory = run_b2(PROBLEM, gen, gen, FakeVerifier(), n=4)
    assert trajectory.ledger.generations == 4
    # revision prompts embed the previous candidate -> more prompt tokens than
    # 4 independent samples (the audited B2 asymmetry, COMPUTE_ACCOUNTING.md)
    assert trajectory.ledger.prompt_tokens > 40
