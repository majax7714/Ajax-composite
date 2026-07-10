#!/usr/bin/env python3
"""Phase 0 — harness. Lock B0 and B1 baselines (brief §11.1-3).

Steps this script owns:
  --handcheck   Print completions for 20 MBPP problems for MANUAL inspection
                (format discipline: does G emit clean executable code?).
  --lock        Run B0 (single-shot) and B1 (best-of-n, likelihood-reranked —
                no V yet) on HumanEval; write per-problem results + ledgers to
                runs/phase0/; print the numbers to freeze in docs/PHASES.md,
                including per-problem B0 pass rates (the H3 difficulty proxy).

Gate: two --lock runs with the same seed policy must reproduce. Record the
verdict in docs/PHASES.md before Phase 1.
"""

from __future__ import annotations

import argparse

from rgr.config import load_config


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/phase0_harness.toml")
    parser.add_argument("--handcheck", action="store_true")
    parser.add_argument("--lock", action="store_true")
    args = parser.parse_args()

    config = load_config(args.config)
    print(f"phase0 config loaded: model={config.generator.model_name}, N={config.loop.t_max}")
    # Assembly order (Phase 0 work):
    #   generator = Generator(config.generator); generator.load()
    #   backend = make_backend(config.execution.backend, config.execution.timeout_seconds)
    #   heldout = load_humaneval().checkout(SplitRole.HELDOUT_EVAL)
    #   B0: run_refine(..., t_max=1); B1: run_refine(..., t_max=N, freeze_register=True)
    #   (likelihood scorer stands in for V until Phase 1)
    raise NotImplementedError("Phase 0: wire generator + sandbox (see module docstrings)")


if __name__ == "__main__":
    main()
