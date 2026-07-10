"""Likelihood scorer — the H1 comparator, and Phase 0's stand-in reranker.

Satisfies VerifierLike using the generator's own mean token log-probability:
"self-fluency" as confidence, exactly the signal H1 claims an
execution-trained V beats. Pure stdlib (the number was computed at generation
time).

Scores are raw log-probabilities, NOT probabilities in [0, 1] — fine for
reranking and AUROC (rank-invariant), never for tau-gating or ECE without
normalization (METRICS.md caveat).
"""

from __future__ import annotations

from rgr.types import Candidate, Problem

NO_CODE_SCORE = -1e9  # unextractable candidates rank below everything


class LikelihoodScorer:
    def score(self, problem: Problem, candidate: Candidate, register=None) -> float:
        if candidate.code is None or candidate.mean_logprob is None:
            return NO_CODE_SCORE
        return candidate.mean_logprob
