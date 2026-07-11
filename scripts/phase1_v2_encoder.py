#!/usr/bin/env python3
"""V-v2 — fine-tuned cross-encoder verifier (D7's pre-authorized escalation).

V-v1's pooled-phi features hit a ceiling (see PHASES.md Phase-1 attempt 1):
an in-domain probe on them loses to raw likelihood. V-v2 fine-tunes a small
code encoder end-to-end on (problem, candidate) TEXT with execution labels,
so the representation itself is learned for correctness.

GPU stage (Kaggle, `kaggle_launch.py launch phase1_v2`):
  Fine-tune microsoft/codebert-base as a cross-encoder:
      input  = problem prompt [SEP] candidate code
      target = passed (BCE via 1-logit head)
  Train on split=train of artifacts/phase1_labels.jsonl, select epoch on
  split=val AUROC (MBPP only — HumanEval is never a selection signal), then
  score the frozen Phase-0 HumanEval candidates (artifacts/lock_a.jsonl).
  Writes runs/phase1_v2/{val_scores.json, heldout_scores.json, encoder.pt}.

Local stage (--h1): the single pre-registered v2 peek at held-out —
h1_head_to_head on heldout_scores.json vs the stored mean log-likelihoods.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).parents[1]
sys.path.insert(0, str(REPO / "src"))

from rgr.config import load_config

ENCODER = "microsoft/codebert-base"
LABELS = Path("artifacts/phase1_labels.jsonl")
LOCK_A = Path("artifacts/lock_a.jsonl")
OUT = Path("runs/phase1_v2")


def pair_text(problem_prompt: str, code: str | None) -> tuple[str, str]:
    return problem_prompt, code if code is not None else ""


def stage_train_and_score(config) -> None:
    import numpy as np
    import torch
    from torch.utils.data import DataLoader, Dataset
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    sys.path.insert(0, str(REPO / "src"))
    from rgr.data.humaneval import load_humaneval
    from rgr.data.mbpp import load_mbpp
    from rgr.evals.calibration import auroc
    from rgr.types import SplitRole

    torch.manual_seed(config.run.seed)
    v2 = config.extra.get("verifier_v2", {})
    epochs = int(v2.get("epochs", 4))
    batch_size = int(v2.get("batch_size", 16))
    lr = float(v2.get("lr", 2e-5))
    max_length = int(v2.get("max_length", 512))

    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = AutoTokenizer.from_pretrained(ENCODER)
    model = AutoModelForSequenceClassification.from_pretrained(ENCODER, num_labels=1).to(device)

    mbpp_prompts = {p.problem_id: p.prompt for p in load_mbpp().problems}
    records = [json.loads(line) for line in open(LABELS)]
    train_rows = [r for r in records if r["split"] == "train"]
    val_rows = [r for r in records if r["split"] == "val"]
    print(f"train {len(train_rows)}, val {len(val_rows)}")

    class Pairs(Dataset):
        def __init__(self, rows):
            self.rows = rows

        def __len__(self):
            return len(self.rows)

        def __getitem__(self, i):
            r = self.rows[i]
            a, b = pair_text(mbpp_prompts[r["problem_id"]], r["code"])
            return a, b, float(r["passed"])

    def collate(batch):
        a, b, y = zip(*batch)
        enc = tokenizer(list(a), list(b), truncation=True, max_length=max_length,
                        padding=True, return_tensors="pt")
        return enc, torch.tensor(y)

    @torch.no_grad()
    def score_rows(rows, prompts):
        model.eval()
        scores = []
        for start in range(0, len(rows), batch_size * 2):
            chunk = rows[start : start + batch_size * 2]
            a = [prompts[r["problem_id"]] for r in chunk]
            b = [r["code"] if r["code"] is not None else "" for r in chunk]
            enc = tokenizer(a, b, truncation=True, max_length=max_length,
                            padding=True, return_tensors="pt").to(device)
            logits = model(**enc).logits.squeeze(-1)
            scores.extend(torch.sigmoid(logits).tolist())
        return scores

    loader = DataLoader(Pairs(train_rows), batch_size=batch_size, shuffle=True,
                        collate_fn=collate)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    best_auroc, best_state = -1.0, None

    for epoch in range(epochs):
        model.train()
        for step, (enc, y) in enumerate(loader):
            enc = enc.to(device)
            logits = model(**enc).logits.squeeze(-1)
            loss = torch.nn.functional.binary_cross_entropy_with_logits(logits, y.to(device))
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            if (step + 1) % 50 == 0:
                print(f"epoch {epoch + 1} step {step + 1}/{len(loader)} loss {float(loss):.4f}")

        val_scores = score_rows(val_rows, mbpp_prompts)
        val_auroc = auroc(val_scores, [bool(r["passed"]) for r in val_rows])
        marker = ""
        if val_auroc > best_auroc:
            best_auroc = val_auroc
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            marker = "  <- best"
        print(f"epoch {epoch + 1}: val AUROC {val_auroc:.4f}{marker}")

    model.load_state_dict(best_state)
    OUT.mkdir(parents=True, exist_ok=True)
    torch.save({"state_dict": best_state, "val_auroc": best_auroc, "encoder": ENCODER},
               OUT / "encoder.pt")
    json.dump({"val_auroc": best_auroc,
               "scores": score_rows(val_rows, mbpp_prompts)}, open(OUT / "val_scores.json", "w"))

    # Score the frozen HumanEval candidates for the (single) H1 v2 peek.
    he_prompts = {p.problem_id: p.prompt
                  for p in load_humaneval().checkout(SplitRole.HELDOUT_EVAL)}
    heldout = []
    for record in [json.loads(line) for line in open(LOCK_A)]:
        for step in record["steps"]:
            heldout.append({
                "problem_id": record["problem_id"],
                "code": step["code"],
                "passed": step["execution"]["passed"],
                "mean_logprob": step["mean_logprob"],
            })
    scores = score_rows(heldout, he_prompts)
    for row, score in zip(heldout, scores):
        row["v2_score"] = score if row["code"] is not None else 0.0
        del row["code"]
    json.dump(heldout, open(OUT / "heldout_scores.json", "w"))
    print(f"done: best val AUROC {best_auroc:.4f}; heldout scores written")


def stage_h1() -> None:
    from rgr.training.train_verifier import h1_head_to_head

    rows = json.load(open(OUT / "heldout_scores.json"))
    result = h1_head_to_head(
        [r["v2_score"] for r in rows],
        [r["mean_logprob"] if r["mean_logprob"] is not None else -1e9 for r in rows],
        [r["passed"] for r in rows],
        [r["problem_id"] for r in rows],
    )
    print("\n=== H1 head-to-head, V-v2 cross-encoder (single v2 peek) ===")
    for key, value in result.items():
        print(f"  {key}: {value}")
    print("\nGATE:", "PASS" if result["h1_pass"] else "FAIL",
          "(need delta >= 0.05 with CI excluding 0)")
    json.dump(result, open("artifacts/h1_v2_result.json", "w"), indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/phase1_verifier.toml")
    parser.add_argument("--train", action="store_true")
    parser.add_argument("--h1", action="store_true")
    args = parser.parse_args()
    config = load_config(args.config)
    if args.train:
        stage_train_and_score(config)
    if args.h1:
        stage_h1()
    if not (args.train or args.h1):
        parser.error("pick --train (GPU) or --h1 (local)")


if __name__ == "__main__":
    main()
