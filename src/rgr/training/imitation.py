"""Imitation via likelihood steering on synthesized prefixes (PHASE2-PLAN, D10).

The register's job, stated as a supervised objective: given a prefix of k
failed candidates (their phi embeddings and verifier scores), produce a
register r_k under which the frozen generator assigns higher likelihood to a
candidate known to pass. Prefixes are synthesized from the Phase-1 label set,
so round 1 needs no new rollouts.

Pure-logic parts (example synthesis, k-bucketing) live here untorched and
unit-tested; the teacher-forced loss lives in scripts/phase2_register_loop.py.
"""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class ImitationExample:
    problem_id: str
    prefix_idx: tuple[int, ...]  # candidate indices (failed) in register order
    target_idx: int  # candidate index (passed) whose likelihood to raise

    @property
    def k(self) -> int:
        return len(self.prefix_idx)


def build_examples(
    passed_by_problem: dict[str, list[bool]],
    *,
    per_problem: int,
    k_max: int,
    seed: int,
) -> list[ImitationExample]:
    """Synthesize prefix->target examples for every problem that has both
    outcomes. k ~ Uniform{0..min(k_max, n_fails)}; prefix = k distinct fails
    in random order; target = a random pass. Problems that are all-pass or
    all-fail contribute nothing (no contrast to learn from).
    """
    rng = random.Random(seed)
    examples: list[ImitationExample] = []
    for problem_id in sorted(passed_by_problem):
        passed = passed_by_problem[problem_id]
        pass_idx = [i for i, p in enumerate(passed) if p]
        fail_idx = [i for i, p in enumerate(passed) if not p]
        if not pass_idx or not fail_idx:
            continue
        for _ in range(per_problem):
            k = rng.randint(0, min(k_max, len(fail_idx)))
            prefix = tuple(rng.sample(fail_idx, k))
            target = rng.choice(pass_idx)
            examples.append(ImitationExample(problem_id, prefix, target))
    return examples


def bucket_by_k(
    examples: list[ImitationExample], batch_size: int, seed: int
) -> list[list[ImitationExample]]:
    """Batches whose members share k, so the register unroll is a clean
    batched loop with no masking. Order of batches is shuffled."""
    rng = random.Random(seed)
    buckets: dict[int, list[ImitationExample]] = {}
    for example in examples:
        buckets.setdefault(example.k, []).append(example)
    batches: list[list[ImitationExample]] = []
    for k in sorted(buckets):
        rows = buckets[k]
        rng.shuffle(rows)
        batches.extend(rows[i : i + batch_size] for i in range(0, len(rows), batch_size))
    rng.shuffle(batches)
    return batches


def unroll_register(r0, prefix_phis, prefix_scores, updater):
    """r_k for a batch sharing prefix length k. Differentiable through
    updater (and through r0 into the encoder).

    r0: (b, d_r) · prefix_phis: (b, k, phi_dim) · prefix_scores: (b, k)
    """
    register = r0
    k = prefix_phis.shape[1] if prefix_phis.dim() == 3 else 0
    for t in range(k):
        register = updater.forward(register, prefix_phis[:, t, :], prefix_scores[:, t])
    return register
