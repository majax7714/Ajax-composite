"""The H1 verdict function is pure logic — test it end to end on synthetic
scores where the right answer is known."""

import random

from rgr.training.train_verifier import h1_head_to_head


def synthetic(n_problems=40, per_problem=6, verifier_sharp=True, seed=5):
    rng = random.Random(seed)
    verifier, likelihood, labels, pids = [], [], [], []
    for p in range(n_problems):
        for _ in range(per_problem):
            correct = rng.random() < 0.4
            # verifier tracks correctness; likelihood is nearly uninformative
            v = (0.7 if correct else 0.3) + rng.gauss(0, 0.1) if verifier_sharp else rng.random()
            lik = rng.gauss(-1.0, 0.3) + (0.05 if correct else 0.0)
            verifier.append(v)
            likelihood.append(lik)
            labels.append(correct)
            pids.append(f"p{p}")
    return verifier, likelihood, labels, pids


def test_sharp_verifier_passes_h1():
    result = h1_head_to_head(*synthetic(verifier_sharp=True))
    assert result["auroc_verifier"] > result["auroc_likelihood"]
    assert result["h1_pass"]


def test_uninformative_verifier_fails_h1():
    result = h1_head_to_head(*synthetic(verifier_sharp=False))
    assert not result["h1_pass"]
