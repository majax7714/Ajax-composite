#!/usr/bin/env python3
"""DIAG-4 (items 1-2) — settle the training-objective units.

Pre-registered in docs/PRE-B2-HANDOFF.md §4. EXPLORATORY / POST-HOC. CPU-only.

Item 1 (units): the teacher-forced loss is HuggingFace CausalLM `out.loss` over
labels with prompt+soft positions masked to -100 (scripts/phase2_register_loop.py
stage_train, batch_loss). That is the MEAN cross-entropy (NLL) per *target*
token, averaged over val examples in val_loss(). So 0.1713 (untrained) / 0.1530
(trained) are mean per-token NLL. Confirmed by code inspection, reproduced here
from the saved register_modules.pt scalars.

Item 2 (implied sequence probability at REAL lengths): using the aggregate
per-token NLL and each val target's real token count (generated_tokens, i.e. the
true sampled length — no re-tokenization), compute implied sequence log-prob
-NLL*L and probability exp(-NLL*L). The 156-token average is deliberately NOT
used. Caveat: this applies the aggregate NLL uniformly per token; exact
per-example NLL (and the entropy split, item 3) need the GPU pass noted in the
handoff. Item 2 is what carries the pre-registered "< 1e-9" claim.

Committed prediction: post-training target sequence probability stays < 1e-9.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from statistics import median

REPO = Path(__file__).parents[1]
sys.path.insert(0, str(REPO / "src"))

LABELS = REPO / "runs/kaggle/phase1_data/runs/phase1/labels.jsonl"
MODULES = REPO / "runs/kaggle/phase2_train/runs/phase2/register_modules.pt"
OUT = REPO / "artifacts/diag4_objective_units.json"
THRESH = 1e-9


def as_bool(v) -> bool:
    return v if isinstance(v, bool) else str(v).strip().lower() == "true"


def load_nll() -> tuple[float, float, str]:
    """(untrained, trained) mean per-token NLL from the saved training artifact,
    falling back to the committed log numbers if torch/file is unavailable."""
    try:
        import torch
        d = torch.load(MODULES, weights_only=True, map_location="cpu")
        return float(d["val_loss_untrained"]), float(d["val_loss"]), "register_modules.pt"
    except Exception as e:  # noqa: BLE001
        print(f"(register_modules.pt unavailable: {e}; using committed log values)")
        return 0.1713, 0.1530, "PHASES.md / rgr-phase2-train.log"


def seq_prob(nll_per_tok: float, length: int) -> float:
    return math.exp(-nll_per_tok * length)


def main() -> None:
    untrained, trained, src = load_nll()

    # Val passing candidates = the population of possible imitation targets.
    lengths = []
    for line in open(LABELS):
        r = json.loads(line)
        if str(r["split"]) == "val" and as_bool(r["passed"]):
            lengths.append(int(r["generated_tokens"]))
    lengths.sort()
    n = len(lengths)

    # L at which trained seq-prob crosses the 1e-9 threshold.
    cross_L = -math.log(THRESH) / trained  # exp(-trained*L) = 1e-9

    def summarize(nll: float) -> dict:
        probs = [seq_prob(nll, L) for L in lengths]
        return {
            "nll_per_token": nll,
            "median_len": median(lengths),
            "median_seq_logprob": -nll * median(lengths),
            "median_seq_prob": seq_prob(nll, int(median(lengths))),
            "seq_prob_at_min_len": seq_prob(nll, lengths[0]),
            "seq_prob_at_max_len": seq_prob(nll, lengths[-1]),
            "n_targets_above_1e-9": sum(1 for p in probs if p >= THRESH),
            "frac_below_1e-9": sum(1 for p in probs if p < THRESH) / n,
        }

    result = {
        "_label": "EXPLORATORY / POST-HOC — does not reopen the H2 gate",
        "item1_units": {
            "conclusion": "mean per-token NLL (HF out.loss over masked labels, "
                          "averaged over val examples)",
            "source": src,
            "val_nll_untrained": untrained,
            "val_nll_trained": trained,
            "relative_improvement": (untrained - trained) / untrained,
        },
        "item2_sequence_probability": {
            "population": "val-split passing candidates (possible imitation targets)",
            "n_targets": n,
            "length_source": "generated_tokens (true sampled length)",
            "length_min_median_max": [lengths[0], median(lengths), lengths[-1]],
            "threshold": THRESH,
            "trained_crosses_1e-9_at_len": cross_L,
            "untrained": summarize(untrained),
            "trained": summarize(trained),
            "prob_ratio_trained_over_untrained_at_median": math.exp(
                (untrained - trained) * median(lengths)),
        },
    }
    OUT.write_text(json.dumps(result, indent=2, default=str))

    t = result["item2_sequence_probability"]["trained"]
    u = result["item2_sequence_probability"]["untrained"]
    print("=== DIAG-4 items 1-2 — objective units ===")
    print(f"item 1: 0.1713/0.1530 are MEAN PER-TOKEN NLL ({src}); "
          f"improvement {result['item1_units']['relative_improvement']:.1%}")
    print(f"item 2: {n} val passing targets, real lengths "
          f"[{lengths[0]}, {median(lengths):.0f}, {lengths[-1]}] tokens")
    print(f"  trained seq-prob crosses 1e-9 at L={cross_L:.0f} tokens")
    print(f"  trained : median seq-prob {t['median_seq_prob']:.2e}; "
          f"at min-len {t['seq_prob_at_min_len']:.2e}; "
          f"{t['n_targets_above_1e-9']}/{n} targets >= 1e-9")
    print(f"  untrained: median seq-prob {u['median_seq_prob']:.2e}")
    print(f"  {t['frac_below_1e-9']:.1%} of trained targets stay below 1e-9")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
