#!/usr/bin/env python3
"""V-v2b — QLoRA cross-encoder verifier on Qwen2.5-Coder-1.5B.

Escalation path so far (all selected on MBPP val, never HumanEval):
  v1 pooled-phi MLP      val 0.750 -> heldout FAILED (delta 0.012)
  v2 codebert-base       val 0.665 -> disqualified on val, peek unspent
  v2b (this)             Qwen2.5-Coder-1.5B + 4-bit + LoRA + cls head

Rationale: the frozen-feature ceiling killed v1 and codebert is too weak a
code model; v2b fine-tunes the strongest code understander that fits the T4 —
the same base model as G, but trained as a classifier on execution labels.

GPU stage (Kaggle, `kaggle_launch.py launch phase1_v2b`): train on
artifacts/phase1_labels.jsonl split=train, select epoch on split=val AUROC,
score the frozen HumanEval candidates. Writes runs/phase1_v2b/.

Local stage (--h1): the single remaining H1 peek — spend it ONLY if v2b's
val AUROC beats v1's 0.750.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).parents[1]
sys.path.insert(0, str(REPO / "src"))

from rgr.config import load_config

BASE_MODEL = "Qwen/Qwen2.5-Coder-1.5B-Instruct"
LABELS = Path("artifacts/phase1_labels.jsonl")
LOCK_A = Path("artifacts/lock_a.jsonl")
OUT = Path("runs/phase1_v2b")

V1_VAL_AUROC = 0.7498  # the bar v2b must clear on val to earn the H1 peek


def pair_text(problem_prompt: str, code: str | None) -> str:
    return (
        f"{problem_prompt.strip()}\n\n# Candidate solution:\n```python\n"
        f"{code if code is not None else ''}\n```\n# Is this solution correct?"
    )


def stage_train_and_score(config) -> None:
    import torch
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from transformers import (
        AutoModelForSequenceClassification,
        AutoTokenizer,
        BitsAndBytesConfig,
    )

    from rgr.data.humaneval import load_humaneval
    from rgr.data.mbpp import load_mbpp
    from rgr.evals.calibration import auroc
    from rgr.types import SplitRole

    torch.manual_seed(config.run.seed)
    v2b = config.extra.get("verifier_v2b", {})
    epochs = int(v2b.get("epochs", 3))
    batch_size = int(v2b.get("batch_size", 4))
    grad_accum = int(v2b.get("grad_accum", 4))
    lr = float(v2b.get("lr", 1e-4))
    max_length = int(v2b.get("max_length", 768))

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(
        BASE_MODEL,
        num_labels=1,
        quantization_config=BitsAndBytesConfig(
            load_in_4bit=True, bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
        ),
        device_map="auto",
    )
    model.config.pad_token_id = tokenizer.pad_token_id or tokenizer.eos_token_id
    model = prepare_model_for_kbit_training(model)
    model = get_peft_model(model, LoraConfig(
        r=16, lora_alpha=32, lora_dropout=0.05, bias="none",
        task_type="SEQ_CLS",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        modules_to_save=["score"],
    ))
    model.print_trainable_parameters()
    device = next(model.parameters()).device

    mbpp_prompts = {p.problem_id: p.prompt for p in load_mbpp().problems}
    records = [json.loads(line) for line in open(LABELS)]
    train_rows = [r for r in records if r["split"] == "train"]
    val_rows = [r for r in records if r["split"] == "val"]
    print(f"train {len(train_rows)}, val {len(val_rows)}")

    def encode(rows, prompts):
        texts = [pair_text(prompts[r["problem_id"]], r["code"]) for r in rows]
        return tokenizer(texts, truncation=True, max_length=max_length,
                         padding=True, return_tensors="pt")

    @torch.no_grad()
    def score_rows(rows, prompts, chunk=16):
        model.eval()
        scores = []
        for start in range(0, len(rows), chunk):
            enc = encode(rows[start : start + chunk], prompts).to(device)
            logits = model(**enc).logits.squeeze(-1).float()
            scores.extend(torch.sigmoid(logits).tolist())
        return scores

    optimizer = torch.optim.AdamW(
        [p for p in model.parameters() if p.requires_grad], lr=lr
    )
    best_auroc, best_scores_heldout = -1.0, None
    order = torch.randperm(len(train_rows))

    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        order = torch.randperm(len(train_rows))
        for step, start in enumerate(range(0, len(order), batch_size)):
            rows = [train_rows[i] for i in order[start : start + batch_size]]
            enc = encode(rows, mbpp_prompts).to(device)
            y = torch.tensor([float(r["passed"]) for r in rows], device=device)
            logits = model(**enc).logits.squeeze(-1).float()
            loss = torch.nn.functional.binary_cross_entropy_with_logits(logits, y)
            (loss / grad_accum).backward()
            if (step + 1) % grad_accum == 0:
                optimizer.step()
                optimizer.zero_grad()
            if (step + 1) % 100 == 0:
                print(f"epoch {epoch + 1} step {step + 1}/{len(order) // batch_size} "
                      f"loss {float(loss):.4f}", flush=True)

        val_scores = score_rows(val_rows, mbpp_prompts)
        val_auroc = auroc(val_scores, [bool(r["passed"]) for r in val_rows])
        marker = ""
        if val_auroc > best_auroc:
            best_auroc = val_auroc
            marker = "  <- best"
            OUT.mkdir(parents=True, exist_ok=True)
            model.save_pretrained(OUT / "lora")
            json.dump({"val_auroc": best_auroc, "epoch": epoch + 1,
                       "scores": val_scores}, open(OUT / "val_scores.json", "w"))
            # Score heldout at each new best so the artifact always matches
            # the selected checkpoint (cheap: 1312 forward passes).
            he_prompts = {p.problem_id: p.prompt
                          for p in load_humaneval().checkout(SplitRole.HELDOUT_EVAL)}
            heldout = []
            for record in [json.loads(line) for line in open(LOCK_A)]:
                for s in record["steps"]:
                    heldout.append({"problem_id": record["problem_id"], "code": s["code"],
                                    "passed": s["execution"]["passed"],
                                    "mean_logprob": s["mean_logprob"]})
            scores = score_rows(heldout, he_prompts)
            for row, score in zip(heldout, scores):
                row["v2b_score"] = score if row["code"] is not None else 0.0
                del row["code"]
            json.dump(heldout, open(OUT / "heldout_scores.json", "w"))
        print(f"epoch {epoch + 1}: val AUROC {val_auroc:.4f}{marker}", flush=True)

    print(f"done: best val AUROC {best_auroc:.4f} "
          f"({'clears' if best_auroc > V1_VAL_AUROC else 'DOES NOT clear'} "
          f"v1's {V1_VAL_AUROC})")


def stage_h1() -> None:
    from rgr.training.train_verifier import h1_head_to_head

    val = json.load(open(OUT / "val_scores.json"))
    if val["val_auroc"] <= V1_VAL_AUROC:
        print(f"REFUSING the H1 peek: v2b val AUROC {val['val_auroc']:.4f} does not "
              f"beat v1's {V1_VAL_AUROC} — the peek budget stays unspent.")
        return
    rows = json.load(open(OUT / "heldout_scores.json"))
    result = h1_head_to_head(
        [r["v2b_score"] for r in rows],
        [r["mean_logprob"] if r["mean_logprob"] is not None else -1e9 for r in rows],
        [r["passed"] for r in rows],
        [r["problem_id"] for r in rows],
    )
    print("\n=== H1 head-to-head, V-v2b QLoRA (final peek) ===")
    for key, value in result.items():
        print(f"  {key}: {value}")
    print("\nGATE:", "PASS" if result["h1_pass"] else "FAIL",
          "(need delta >= 0.05 with CI excluding 0)")
    json.dump(result, open("artifacts/h1_v2b_result.json", "w"), indent=2)


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
