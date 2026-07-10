#!/usr/bin/env python3
"""Phase 1 — verifier (H1). Generate labels, train V, run the head-to-head.

  --labels      rgr.training.labels.generate_labels over MBPP-train
                (candidates x temperatures -> sandbox -> JSONL).
  --train       rgr.training.train_verifier.train_verifier; selection on
                MBPP-val AUROC only.
  --h1          Score held-out candidates with V and with mean log-likelihood;
                rgr.training.train_verifier.h1_head_to_head prints the verdict.
  --relock-b1   Re-lock B1 with V reranking (replaces likelihood reranking).

Gate: delta-AUROC >= 0.05, CI excluding 0 (docs/METRICS.md). If it fails:
stop. Do not build the register on an untrustworthy confidence signal.
"""

from __future__ import annotations

import argparse

from rgr.config import load_config


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/phase1_verifier.toml")
    for flag in ("--labels", "--train", "--h1", "--relock-b1"):
        parser.add_argument(flag, action="store_true")
    args = parser.parse_args()
    config = load_config(args.config)
    print(f"phase1 config loaded: {config.extra.get('labels', {})}")
    raise NotImplementedError("Phase 1: wire after Phase 0 gate passes")


if __name__ == "__main__":
    main()
