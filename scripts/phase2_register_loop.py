#!/usr/bin/env python3
"""Phase 2 — register loop (H2, the core result).

  --rollout     Collect imitation trajectories (rgr.training.train_register).
  --train       Fit injector + r_0 encoder + U; G and V frozen (D2, D6).
  --staleness   V AUROC on current-policy rollouts; refresh V if drop > 0.05.
  --h2          FULL vs B1 vs B1' vs B2 on HumanEval at matched compute
                (assert_matched enforces the ledger); pass@k deltas with
                problem-level bootstrap CIs; register diagnostics report.

Gate: FULL beats BOTH B1 and B2 with CIs excluding 0. A tie with either kills
the register (clean negative — write it up, don't tune past it).
"""

from __future__ import annotations

import argparse

from rgr.config import load_config


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/phase2_register.toml")
    for flag in ("--rollout", "--train", "--staleness", "--h2"):
        parser.add_argument(flag, action="store_true")
    args = parser.parse_args()
    config = load_config(args.config)
    print(f"phase2 config loaded: d_r={config.register.d_r}, k={config.register.k_soft_tokens}")
    raise NotImplementedError("Phase 2: wire after Phase 1 gate passes")


if __name__ == "__main__":
    main()
