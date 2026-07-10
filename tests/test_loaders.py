"""Loader tests run against the local cache (data/cache/) and skip when it is
absent — the suite stays network-free. Populate the cache once with
`python3 -c "from rgr.data.mbpp import load_mbpp; load_mbpp()"` etc."""

import pytest

from rgr.data.fetch import CACHE_DIR
from rgr.types import SplitRole

needs_mbpp = pytest.mark.skipif(
    not (CACHE_DIR / "sanitized-mbpp.json").exists(), reason="mbpp cache not populated"
)
needs_humaneval = pytest.mark.skipif(
    not (CACHE_DIR / "HumanEval.jsonl.gz").exists(), reason="humaneval cache not populated"
)


@needs_mbpp
def test_mbpp_shape():
    from rgr.data.mbpp import load_mbpp

    ds = load_mbpp()
    assert ds.role == SplitRole.TRAIN
    assert len(ds.problems) == 427
    p = ds.problems[0]
    assert p.test_list and all(t.startswith("assert") for t in p.test_list)
    assert p.tests  # combined block matches the list
    assert "passes these tests" in p.prompt  # signature is visible to the model
    assert p.source == "mbpp"


@needs_humaneval
def test_humaneval_shape():
    from rgr.data.humaneval import load_humaneval

    ds = load_humaneval()
    assert ds.role == SplitRole.HELDOUT_EVAL
    assert len(ds.problems) == 164
    p = ds.problems[0]
    assert p.entry_point
    assert f"check({p.entry_point})" in p.tests
    assert p.test_list == ()  # block-style: frac_tests is 0/1 for HumanEval
    assert p.source == "humaneval"


@needs_humaneval
def test_humaneval_cannot_be_trained_on():
    from rgr.data.humaneval import load_humaneval
    from rgr.data.splits import SplitViolation

    with pytest.raises(SplitViolation):
        load_humaneval().checkout(SplitRole.TRAIN)


@needs_mbpp
def test_no_id_overlap_between_sources():
    from rgr.data.mbpp import load_mbpp

    ids = [p.problem_id for p in load_mbpp().problems]
    assert len(ids) == len(set(ids))
