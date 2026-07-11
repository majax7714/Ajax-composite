"""Phase 1 label generation: candidates x execution results -> V training set.

The expensive line item is sandboxed execution, not training (brief §7), so
executions run through a small pool of Daytona sandboxes in parallel while
generation is batched (one num_return_sequences call per temperature).

Outputs, per run directory:
  labels.jsonl        one record per candidate:
                      {problem_id, idx, split, temperature, text, code,
                       mean_logprob, prompt_tokens, generated_tokens,
                       passed, frac_tests, error_type, policy_tag}
  phi/<problem>.npy   float16 (n_candidates, d_model) generation-time phi,
                      row-aligned with idx
  phi_problems/<problem>.npy  float16 (d_model,) problem embedding

Resumable per problem: a problem is done when its phi file exists AND its
records are in labels.jsonl (phi is written after the records, so a partial
problem re-runs whole).

Staleness discipline (brief §2): every record carries policy_tag so V
refreshes can filter to current-policy rollouts.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from rgr.types import Candidate, ExecutionResult, Problem


def split_counts(total: int, temperatures: Sequence[float]) -> list[tuple[float, int]]:
    """Distribute `total` candidates across temperatures, remainder to the
    later (higher-diversity) temps. split_counts(16, [.2,.8,1.]) -> 5/5/6."""
    if total < len(temperatures):
        raise ValueError("need at least one candidate per temperature")
    base, rem = divmod(total, len(temperatures))
    counts = [base] * len(temperatures)
    for i in range(rem):
        counts[len(temperatures) - 1 - i] += 1
    return list(zip(temperatures, counts))


class ExecutionPool:
    """K sandboxes executing candidates concurrently. Each worker owns one
    backend (sandboxes are not assumed re-entrant)."""

    def __init__(self, backend_factory, size: int) -> None:
        self.backends = [backend_factory() for _ in range(size)]
        self.pool = ThreadPoolExecutor(max_workers=size)

    def execute_all(self, problem: Problem, candidates: list[Candidate]) -> list[ExecutionResult]:
        def run(args):
            worker_idx, candidate = args
            return self.backends[worker_idx].execute(problem, candidate)

        jobs = [(i % len(self.backends), c) for i, c in enumerate(candidates)]
        # chunk so one backend never runs two jobs at once
        results: list[ExecutionResult] = [None] * len(jobs)  # type: ignore[list-item]
        for start in range(0, len(jobs), len(self.backends)):
            chunk = jobs[start : start + len(self.backends)]
            for offset, result in enumerate(self.pool.map(run, chunk)):
                results[start + offset] = result
        return results

    def close(self) -> None:
        for backend in self.backends:
            backend.close()
        self.pool.shutdown()


def generate_labels(
    problems_by_split: dict[str, Sequence[Problem]],
    generator,
    execution_pool: ExecutionPool,
    out_dir: str | Path,
    *,
    candidates_per_problem: int,
    temperatures: Sequence[float],
    policy_tag: str = "phase1_raw",
    log_every: int = 10,
) -> None:
    import numpy as np

    out_dir = Path(out_dir)
    phi_dir = out_dir / "phi"
    phi_problem_dir = out_dir / "phi_problems"
    phi_dir.mkdir(parents=True, exist_ok=True)
    phi_problem_dir.mkdir(parents=True, exist_ok=True)
    labels_path = out_dir / "labels.jsonl"

    def fname(problem_id: str) -> str:
        return problem_id.replace("/", "__") + ".npy"

    done = set()
    if labels_path.exists():
        recorded = {json.loads(line)["problem_id"] for line in open(labels_path)}
        done = {p for p in recorded if (phi_dir / fname(p)).exists()}
    if done:
        print(f"resuming: {len(done)} problems already labeled")

    plan = split_counts(candidates_per_problem, temperatures)
    todo = [(s, p) for s, ps in problems_by_split.items() for p in ps if p.problem_id not in done]
    for i, (split, problem) in enumerate(todo):
        candidates: list[Candidate] = []
        temps: list[float] = []
        for temperature, count in plan:
            batch = generator.sample(problem, count, temperature=temperature)
            candidates.extend(batch)
            temps.extend([temperature] * count)

        executions = execution_pool.execute_all(problem, candidates)

        with open(labels_path, "a") as f:
            for idx, (candidate, temperature, execution) in enumerate(
                zip(candidates, temps, executions)
            ):
                f.write(json.dumps({
                    "problem_id": problem.problem_id,
                    "idx": idx,
                    "split": split,
                    "temperature": temperature,
                    "text": candidate.text,
                    "code": candidate.code,
                    "mean_logprob": candidate.mean_logprob,
                    "prompt_tokens": candidate.prompt_tokens,
                    "generated_tokens": candidate.generated_tokens,
                    "passed": execution.passed,
                    "frac_tests": execution.frac_tests,
                    "error_type": execution.error_type,
                    "policy_tag": policy_tag,
                }) + "\n")

        d_model = generator.d_model
        phi = np.stack([
            c.phi.cpu().numpy() if c.phi is not None else np.zeros(d_model, dtype=np.float32)
            for c in candidates
        ]).astype(np.float16)
        np.save(phi_dir / fname(problem.problem_id), phi)
        np.save(
            phi_problem_dir / fname(problem.problem_id),
            generator.embed_problem(problem).cpu().numpy().astype(np.float16),
        )

        if (i + 1) % log_every == 0:
            print(f"{i + 1}/{len(todo)} problems labeled")
