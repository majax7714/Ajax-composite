import pytest

from rgr.training.imitation import ImitationExample, bucket_by_k, build_examples


def test_build_examples_needs_both_outcomes():
    passed = {
        "p/allpass": [True, True],
        "p/allfail": [False, False],
        "p/mixed": [True, False, False],
    }
    examples = build_examples(passed, per_problem=5, k_max=7, seed=1)
    assert {e.problem_id for e in examples} == {"p/mixed"}
    assert len(examples) == 5


def test_prefixes_are_failures_targets_are_passes():
    passed = {"p/1": [True, False, True, False, False]}
    examples = build_examples(passed, per_problem=50, k_max=7, seed=2)
    fails, passes = {1, 3, 4}, {0, 2}
    for e in examples:
        assert set(e.prefix_idx) <= fails
        assert len(set(e.prefix_idx)) == len(e.prefix_idx)  # distinct
        assert e.target_idx in passes
        assert e.k <= 3


def test_k_max_respected_and_k0_present():
    passed = {"p/1": [True] + [False] * 15}
    examples = build_examples(passed, per_problem=200, k_max=7, seed=3)
    ks = {e.k for e in examples}
    assert max(ks) == 7
    assert 0 in ks  # k=0 examples train pure r_0 steering


def test_deterministic_under_seed():
    passed = {"p/1": [True, False, False, False]}
    a = build_examples(passed, per_problem=10, k_max=3, seed=9)
    b = build_examples(passed, per_problem=10, k_max=3, seed=9)
    assert a == b


def test_bucket_by_k_homogeneous_batches():
    examples = [
        ImitationExample("p/1", tuple(range(k)), 99) for k in (0, 0, 0, 1, 1, 2, 2, 2, 2, 2)
    ]
    batches = bucket_by_k(examples, batch_size=2, seed=0)
    assert sum(len(b) for b in batches) == len(examples)
    for batch in batches:
        assert len({e.k for e in batch}) == 1
        assert len(batch) <= 2


def test_unroll_register_matches_sequential():
    torch = pytest.importorskip("torch")
    from rgr.register.update import RegisterUpdate
    from rgr.training.imitation import unroll_register

    torch.manual_seed(0)
    u = RegisterUpdate(d_r=8, phi_dim=6)
    r0 = torch.randn(2, 8)
    phis = torch.randn(2, 3, 6)
    scores = torch.rand(2, 3)

    batched = unroll_register(r0, phis, scores, u)
    # sequential reference, one example at a time
    for row in range(2):
        r = r0[row]
        for t in range(3):
            r = u.forward(r, phis[row, t], float(scores[row, t]))
        assert torch.allclose(batched[row], r, atol=1e-5)
