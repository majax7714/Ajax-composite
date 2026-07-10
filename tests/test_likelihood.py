from rgr.verifier.likelihood import NO_CODE_SCORE, LikelihoodScorer
from rgr.types import Candidate, Problem

PROBLEM = Problem(problem_id="toy/1", prompt="p", tests="t")


def test_scores_by_mean_logprob():
    scorer = LikelihoodScorer()
    high = Candidate(text="a", code="x=1", mean_logprob=-0.2)
    low = Candidate(text="b", code="x=2", mean_logprob=-1.5)
    assert scorer.score(PROBLEM, high, None) > scorer.score(PROBLEM, low, None)


def test_no_code_ranks_last():
    scorer = LikelihoodScorer()
    prose = Candidate(text="I would iterate...", code=None, mean_logprob=-0.01)
    worst_code = Candidate(text="c", code="x=3", mean_logprob=-50.0)
    assert scorer.score(PROBLEM, prose, None) == NO_CODE_SCORE
    assert scorer.score(PROBLEM, worst_code, None) > scorer.score(PROBLEM, prose, None)
