#!/usr/bin/env python3
"""Phase 0 — harness. Lock B0 and B1 baselines (brief §11.1-3).

  --handcheck   Generate one completion for 20 MBPP problems, print prompt /
                raw completion / extracted code for MANUAL inspection, execute
                each in the sandbox, report the extraction rate. (§11.1's
                by-hand format-discipline check.)
  --lock        On HumanEval (held out): N samples per problem with a frozen
                null register (no injection exists yet), execute ALL samples,
                rerank by likelihood (no V yet — Phase 1 re-locks with V).
                One run yields every Phase-0 number:
                  B0 pass@1  = unbiased pass@1 over the N samples,
                  B1 pass@1  = executed verdict of the likelihood-argmax,
                  pass@k curve, and per-problem (n, c) — the H3 difficulty
                  proxy. Results stream to runs/phase0/<tag>.jsonl (resumable).

Gate: run --lock twice with different --seed-tag labels but the same seed; the
numbers must reproduce. Record the verdict in docs/PHASES.md before Phase 1.

Needs the [model] extra and a GPU (Kaggle T4/P100 per brief §7), plus the
Daytona key (DAYTONA_API_KEY or the gitignored key file).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from rgr.config import Config, load_config
from rgr.data.humaneval import load_humaneval
from rgr.data.mbpp import load_mbpp
from rgr.evals.passk import mean_pass_at_k
from rgr.execution.sandbox import make_backend
from rgr.generator.model import Generator
from rgr.loop.interfaces import NoRegister
from rgr.loop.refine import run_refine
from rgr.results import append_jsonl, n_correct, read_jsonl, selected_passed, trajectory_record
from rgr.types import SplitRole
from rgr.verifier.likelihood import LikelihoodScorer


def set_seed(seed: int) -> None:
    # Reproducibility gate note: seeding happens once at run start, so the
    # two gate runs must both be CLEAN full runs — a resumed run consumes RNG
    # differently and will not bit-match, which is expected and fine for
    # resuming, but not for the gate comparison.
    import random

    random.seed(seed)
    import torch

    torch.manual_seed(seed)


def build_generator(config: Config) -> Generator:
    set_seed(config.run.seed)
    generator = Generator(config.generator)
    print(f"loading {config.generator.model_name} (4bit={config.generator.load_4bit}) ...")
    generator.load()
    return generator


def handcheck(config: Config, n_problems: int = 20) -> None:
    generator = build_generator(config)
    problems = load_mbpp().checkout(SplitRole.TRAIN)[:n_problems]
    extracted = 0
    with make_backend(config.execution.backend, config.execution.timeout_seconds) as backend:
        for problem in problems:
            candidate = generator.generate(problem, None)
            print("=" * 78)
            print(f"[{problem.problem_id}] PROMPT:\n{problem.prompt}\n")
            print(f"RAW COMPLETION:\n{candidate.text}\n")
            if candidate.code is None:
                print("EXTRACTED CODE: <none — format failure>")
                continue
            extracted += 1
            result = backend.execute(problem, candidate)
            print(f"EXTRACTED CODE:\n{candidate.code}\n")
            print(f"EXECUTION: passed={result.passed} frac={result.frac_tests:.2f} "
                  f"error={result.error_type!r}")
    print("=" * 78)
    print(f"extraction rate: {extracted}/{len(problems)}")
    print("Inspect the completions above BY HAND before checking the Phase-0 box.")


def lock(config: Config, out_tag: str) -> None:
    generator = build_generator(config)
    scorer = LikelihoodScorer()
    null_register = NoRegister()
    problems = load_humaneval().checkout(SplitRole.HELDOUT_EVAL)
    n = config.loop.t_max
    out_path = Path(config.run.output_dir) / "phase0" / f"{out_tag}.jsonl"

    done = {r["problem_id"] for r in read_jsonl(out_path)} if out_path.exists() else set()
    if done:
        print(f"resuming: {len(done)} problems already in {out_path}")

    with make_backend(config.execution.backend, config.execution.timeout_seconds) as backend:
        for i, problem in enumerate(problems):
            if problem.problem_id in done:
                continue
            trajectory = run_refine(
                problem, generator, scorer, null_register, null_register,
                t_max=n, freeze_register=True, condition="b1_likelihood",
            )
            executions = [backend.execute(problem, s.candidate) for s in trajectory.steps]
            append_jsonl(out_path, trajectory_record(
                trajectory, executions, tag=out_tag, seed=config.run.seed,
            ))
            if (i + 1) % 10 == 0:
                print(f"{i + 1}/{len(problems)} problems done")

    summarize(out_path, n)


def summarize(out_path: Path, n: int) -> None:
    records = read_jsonl(out_path)
    counts = [n_correct(r) for r in records]
    print(f"\n=== Phase 0 numbers ({out_path}, {len(records)} problems) ===")
    print(f"B0  pass@1 (unbiased over {n} samples): {mean_pass_at_k(counts, 1):.4f}")
    print(f"B1  pass@1 (likelihood-reranked):       "
          f"{sum(selected_passed(r) for r in records) / len(records):.4f}")
    for k in (2, 4, 8):
        if k <= n:
            print(f"    pass@{k}: {mean_pass_at_k(counts, k):.4f}")
    no_code = sum(1 for r in records for s in r["steps"] if s["code"] is None)
    total = sum(len(r["steps"]) for r in records)
    print(f"format-discipline: {total - no_code}/{total} candidates had extractable code")
    print("\nFreeze these numbers in docs/PHASES.md (gate log). Per-problem (n, c)")
    print("difficulty proxies live in the JSONL for Phase 3.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/phase0_harness.toml")
    parser.add_argument("--handcheck", action="store_true")
    parser.add_argument("--lock", action="store_true")
    parser.add_argument("--summarize", metavar="JSONL", help="re-print numbers from a results file")
    parser.add_argument("--seed-tag", default="lock_a", help="output file label (run twice: lock_a, lock_b)")
    args = parser.parse_args()

    config = load_config(args.config)
    if args.summarize:
        summarize(Path(args.summarize), config.loop.t_max)
    elif args.handcheck:
        handcheck(config)
    elif args.lock:
        lock(config, args.seed_tag)
    else:
        parser.error("pick one of --handcheck / --lock / --summarize")


if __name__ == "__main__":
    main()
