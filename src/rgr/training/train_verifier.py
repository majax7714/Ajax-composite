"""The H1 verdict: AUROC(V) vs AUROC(likelihood) with problem-level bootstrap.

Pure stdlib — callable on saved score lists without torch or a GPU, so the
gate decision itself is locally testable. The training loop that produces V
lives in scripts/phase1_verifier.py (--train); loss there is
BCE(p_correct, passed) + 0.5*MSE(frac_tests) + 0.25*CE(error_type) per D7,
selected on MBPP-validation AUROC (never HumanEval).

Pre-registered margin (docs/METRICS.md): delta-AUROC >= 0.05 with the 95%
problem-level bootstrap CI excluding 0.
"""

from __future__ import annotations

from rgr.evals.bootstrap import bootstrap_ci
from rgr.evals.calibration import auroc


def h1_head_to_head(
    verifier_scores: list[float],
    likelihood_scores: list[float],
    labels: list[bool],
    problem_ids: list[str],
) -> dict:
    """The H1 verdict. Pure logic — callable on saved scores without a GPU."""
    records = list(zip(verifier_scores, likelihood_scores, labels, problem_ids))

    def delta(sample) -> float:
        v = auroc([r[0] for r in sample], [r[2] for r in sample])
        lik = auroc([r[1] for r in sample], [r[2] for r in sample])
        return v - lik

    # Problem-level bootstrap requires resampling problems; group first.
    by_problem: dict[str, list] = {}
    for r in records:
        by_problem.setdefault(r[3], []).append(r)
    problems = list(by_problem.values())

    def stat(sample_problems) -> float:
        flat = [r for group in sample_problems for r in group]
        return delta(flat)

    ci = bootstrap_ci(problems, stat)
    return {
        "auroc_verifier": auroc(verifier_scores, labels),
        "auroc_likelihood": auroc(likelihood_scores, labels),
        "delta": ci.point,
        "ci_lo": ci.lo,
        "ci_hi": ci.hi,
        "h1_pass": ci.point >= 0.05 and ci.excludes_zero,
    }
