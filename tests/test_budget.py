import pytest

from rgr.loop.budget import BudgetReport, ComputeLedger, ComputeMismatchError, assert_matched


def make_report(condition: str, generations_per_problem: list[int]) -> BudgetReport:
    report = BudgetReport(condition=condition)
    for n in generations_per_problem:
        ledger = ComputeLedger()
        for _ in range(n):
            ledger.charge_generation(prompt_tokens=100, generated_tokens=200)
        report.add(ledger)
    return report


def test_ledger_counts():
    ledger = ComputeLedger()
    ledger.charge_generation(10, 20)
    ledger.charge_verifier()
    ledger.charge_update()
    assert ledger.generations == 1
    assert ledger.prompt_tokens == 10
    assert ledger.generated_tokens == 20
    assert ledger.verifier_calls == 1
    assert ledger.update_calls == 1


def test_matched_exact_passes():
    full = make_report("full", [8, 8, 8])
    b1 = make_report("b1", [8, 8, 8])
    assert_matched([full, b1])  # no raise


def test_unmatched_exact_raises():
    full = make_report("full", [8, 8, 8])
    b1 = make_report("b1", [8, 8, 7])
    with pytest.raises(ComputeMismatchError):
        assert_matched([full, b1])


def test_mean_matched_mode():
    adaptive = make_report("full_adaptive", [3, 5, 4])  # mean 4.0
    fixed = make_report("full", [4, 4, 4])  # mean 4.0
    assert_matched([adaptive, fixed], mean_matched=True, tolerance=0.5)
    far = make_report("full", [8, 8, 8])
    with pytest.raises(ComputeMismatchError):
        assert_matched([adaptive, far], mean_matched=True, tolerance=0.5)


def test_mean_generations():
    report = make_report("b2", [2, 4])
    assert report.mean_generations == 3.0
