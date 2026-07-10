"""Phase 1: train V on execution labels; run the H1 head-to-head.

Loss = BCE(p_correct, passed)
     + lambda_frac * MSE(frac_tests_head, frac_tests)        (aux, D7)
     + lambda_err  * CE(error_type_logits, error_type)       (aux, D7)

Selection on MBPP-validation AUROC (never HumanEval). The gate that this
module must answer (brief §11.4): AUROC(V) vs AUROC(mean_logprob) on held-out
problems, with the pre-registered margin from docs/METRICS.md (ΔAUROC >= 0.05,
bootstrap CI excluding 0).

The evaluation half is pure stdlib and lives in rgr.evals — this module only
produces the two score lists and hands them over.
"""

from __future__ import annotations

from rgr.evals.bootstrap import bootstrap_ci
from rgr.evals.calibration import auroc


def train_verifier(labels_path: str, config) -> None:
    """Phase 1: dataset from JSONL labels (phi features computed once and
    cached — they are frozen-G outputs), AdamW, early stop on val AUROC."""
    raise NotImplementedError("Phase 1")


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
