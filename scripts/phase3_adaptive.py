#!/usr/bin/env python3
"""Phase 3 — adaptive compute (H3).

  --sweep-tau   Sweep tau on MBPP-validation ONLY; freeze the chosen value.
  --h3          Early-stopping runs on HumanEval: spearman(steps-to-stop,
                difficulty proxy from Phase 0 B0 pass rates); adaptive vs
                fixed-K at matched MEAN generations (assert_matched
                mean-matched mode); compute-accuracy Pareto data.

Gate: positive depth-difficulty correlation AND adaptive >= fixed-K at matched
mean compute. Weaker gate — H3 failing does not sink H2.
"""

from __future__ import annotations

import argparse

from rgr.config import load_config


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/phase3_adaptive.toml")
    for flag in ("--sweep-tau", "--h3"):
        parser.add_argument(flag, action="store_true")
    args = parser.parse_args()
    config = load_config(args.config)
    print(f"phase3 config loaded: early_stop={config.loop.early_stop}, tau={config.loop.tau}")
    raise NotImplementedError("Phase 3: wire after Phase 2 gate passes")


if __name__ == "__main__":
    main()
