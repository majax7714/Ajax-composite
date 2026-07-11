#!/usr/bin/env python3
"""Phase 1 — verifier (H1).

GPU stages (run on Kaggle via `kaggle_launch.py launch phase1_data`):
  --labels     Batched candidate generation on MBPP train+val (16/problem
               across temps), executed through a Daytona pool, written to
               runs/phase1/ (labels.jsonl + phi arrays). Resumable.
  --reencode   phi features for the frozen Phase-0 HumanEval candidates
               (artifacts/lock_a.jsonl in the bundle) — the H1 eval set.

Local stages (CPU, after fetching the kernel output):
  --train      Train V-v1 (pooled-feature MLP + aux heads, register-blind
               per D3) on split=train, select on split=val AUROC.
  --h1         Score the HumanEval candidates with V; head-to-head vs the
               stored mean log-likelihoods; print the gate verdict
               (METRICS.md: delta-AUROC >= 0.05, bootstrap CI excluding 0).

Gate: if --h1 fails, stop. Do not build the register on an untrustworthy
confidence signal.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).parents[1]
sys.path.insert(0, str(REPO / "src"))

from rgr.config import Config, load_config
from rgr.data.humaneval import load_humaneval
from rgr.data.mbpp import load_mbpp
from rgr.data.splits import train_val_split
from rgr.types import SplitRole

LABELS_DIR = Path("runs/phase1")
HELDOUT_DIR = Path("runs/phase1_heldout")
LOCK_A = Path("artifacts/lock_a.jsonl")


def fname(problem_id: str) -> str:
    return problem_id.replace("/", "__") + ".npy"


def build_generator(config: Config):
    from rgr.generator.model import Generator

    generator = Generator(config.generator)
    print(f"loading {config.generator.model_name} ...")
    generator.load()
    return generator


def stage_labels(config: Config, generator) -> None:
    from rgr.execution.sandbox import DaytonaBackend
    from rgr.training.labels import ExecutionPool, generate_labels

    mbpp = load_mbpp()
    train, val = train_val_split(mbpp, config.data.val_fraction, config.data.seed)
    labels_config = config.extra["labels"]
    pool = ExecutionPool(
        lambda: DaytonaBackend(config.execution.timeout_seconds),
        size=int(labels_config.get("pool_size", 4)),
    )
    try:
        generate_labels(
            {
                "train": train.checkout(SplitRole.TRAIN),
                "val": val.checkout(SplitRole.VALIDATION),
            },
            generator,
            pool,
            LABELS_DIR,
            candidates_per_problem=int(labels_config["candidates_per_problem"]),
            temperatures=list(labels_config["temperatures"]),
        )
    finally:
        pool.close()
    print(f"labels complete -> {LABELS_DIR}")


def stage_reencode(config: Config, generator) -> None:
    import numpy as np

    problems = {p.problem_id: p for p in load_humaneval().checkout(SplitRole.HELDOUT_EVAL)}
    records = [json.loads(line) for line in open(LOCK_A)]
    phi_dir = HELDOUT_DIR / "phi"
    phi_problem_dir = HELDOUT_DIR / "phi_problems"
    phi_dir.mkdir(parents=True, exist_ok=True)
    phi_problem_dir.mkdir(parents=True, exist_ok=True)

    for i, record in enumerate(records):
        problem = problems[record["problem_id"]]
        out = phi_dir / fname(problem.problem_id)
        if out.exists():
            continue
        phi = np.stack([
            generator.embed_candidate(problem, step["text"]).cpu().numpy()
            for step in record["steps"]
        ]).astype(np.float16)
        np.save(out, phi)
        np.save(phi_problem_dir / fname(problem.problem_id),
                generator.embed_problem(problem).cpu().numpy().astype(np.float16))
        if (i + 1) % 20 == 0:
            print(f"reencoded {i + 1}/{len(records)}")
    print(f"reencode complete -> {HELDOUT_DIR}")


def load_feature_split(labels_dir: Path):
    """-> {split: [(phi_p, phi_c, passed, frac, err_idx, logprob, pid), ...]}"""
    import numpy as np

    from rgr.verifier.model import ERROR_TYPES

    by_split: dict[str, list] = {"train": [], "val": []}
    records = [json.loads(line) for line in open(labels_dir / "labels.jsonl")]
    phi_cache: dict[str, tuple] = {}
    for record in records:
        pid = record["problem_id"]
        if pid not in phi_cache:
            phi_cache[pid] = (
                np.load(labels_dir / "phi" / fname(pid)).astype(np.float32),
                np.load(labels_dir / "phi_problems" / fname(pid)).astype(np.float32),
            )
        phi_c, phi_p = phi_cache[pid]
        err = record["error_type"] if record["error_type"] in ERROR_TYPES else "runtime"
        by_split[record["split"]].append((
            phi_p, phi_c[record["idx"]], float(record["passed"]),
            record["frac_tests"], ERROR_TYPES.index(err),
            record["mean_logprob"], pid,
        ))
    return by_split


def stage_train(config: Config) -> None:
    import numpy as np
    import torch

    from rgr.evals.calibration import auroc
    from rgr.verifier.model import Verifier

    torch.manual_seed(config.run.seed)
    by_split = load_feature_split(LABELS_DIR)
    train_config = config.extra["verifier_train"]

    def tensors(rows):
        return (
            torch.tensor(np.stack([r[0] for r in rows])),
            torch.tensor(np.stack([r[1] for r in rows])),
            torch.tensor([r[2] for r in rows]),
            torch.tensor([r[3] for r in rows]),
            torch.tensor([r[4] for r in rows]),
        )

    tr = tensors(by_split["train"])
    va = tensors(by_split["val"])
    print(f"train {len(tr[2])} candidates (pass rate {tr[2].mean():.3f}), "
          f"val {len(va[2])} (pass rate {va[2].mean():.3f})")

    model = Verifier(config.verifier, phi_dim=tr[0].shape[1])
    optimizer = torch.optim.AdamW(model.parameters(), lr=float(train_config["lr"]))
    batch_size = int(train_config["batch_size"])
    best_auroc, best_state, since_best = -1.0, None, 0

    for epoch in range(int(train_config["epochs"])):
        model.train()
        perm = torch.randperm(len(tr[2]))
        for start in range(0, len(perm), batch_size):
            sel = perm[start : start + batch_size]
            out = model(tr[0][sel], tr[1][sel])
            loss = torch.nn.functional.binary_cross_entropy(
                out["p_correct"].clamp(1e-6, 1 - 1e-6), tr[2][sel]
            )
            if "frac_tests" in out:
                loss = loss + 0.5 * torch.nn.functional.mse_loss(out["frac_tests"], tr[3][sel])
            if "error_type_logits" in out:
                loss = loss + 0.25 * torch.nn.functional.cross_entropy(
                    out["error_type_logits"], tr[4][sel]
                )
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        model.eval()
        with torch.no_grad():
            val_scores = model(va[0], va[1])["p_correct"].tolist()
        val_auroc = auroc(val_scores, [bool(y) for y in va[2].tolist()])
        marker = ""
        if val_auroc > best_auroc:
            best_auroc, since_best = val_auroc, 0
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
            marker = "  <- best"
        else:
            since_best += 1
        print(f"epoch {epoch + 1}: val AUROC {val_auroc:.4f}{marker}")
        if since_best >= 3:
            print("early stop (no val improvement for 3 epochs)")
            break

    Path("artifacts").mkdir(exist_ok=True)
    torch.save({"state_dict": best_state, "val_auroc": best_auroc},
               "artifacts/verifier_v1.pt")
    print(f"saved artifacts/verifier_v1.pt (val AUROC {best_auroc:.4f})")


def stage_h1(config: Config) -> None:
    import numpy as np
    import torch

    from rgr.training.train_verifier import h1_head_to_head
    from rgr.verifier.model import Verifier

    records = [json.loads(line) for line in open(LOCK_A)]
    checkpoint = torch.load("artifacts/verifier_v1.pt", weights_only=True)
    sample = np.load(HELDOUT_DIR / "phi_problems" / fname(records[0]["problem_id"]))
    model = Verifier(config.verifier, phi_dim=sample.shape[0])
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()

    verifier_scores, likelihood_scores, labels, pids = [], [], [], []
    with torch.no_grad():
        for record in records:
            pid = record["problem_id"]
            phi_c = torch.tensor(np.load(HELDOUT_DIR / "phi" / fname(pid)).astype(np.float32))
            phi_p = torch.tensor(
                np.load(HELDOUT_DIR / "phi_problems" / fname(pid)).astype(np.float32)
            ).expand(len(record["steps"]), -1)
            scores = model(phi_p, phi_c)["p_correct"].tolist()
            for step, v in zip(record["steps"], scores):
                # no-code candidates score 0 at inference (Verifier.score);
                # mirror that rule here so the eval matches deployment
                verifier_scores.append(0.0 if step["code"] is None else v)
                likelihood_scores.append(step["mean_logprob"]
                                         if step["mean_logprob"] is not None else -1e9)
                labels.append(step["execution"]["passed"])
                pids.append(pid)

    result = h1_head_to_head(verifier_scores, likelihood_scores, labels, pids)
    print("\n=== H1 head-to-head (HumanEval, frozen Phase-0 candidates) ===")
    for key, value in result.items():
        print(f"  {key}: {value}")
    print("\nGATE:", "PASS" if result["h1_pass"] else "FAIL",
          "(need delta >= 0.05 with CI excluding 0)")
    json.dump(result, open("artifacts/h1_result.json", "w"), indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/phase1_verifier.toml")
    for flag in ("--labels", "--reencode", "--train", "--h1"):
        parser.add_argument(flag, action="store_true")
    args = parser.parse_args()
    config = load_config(args.config)

    if args.labels or args.reencode:
        generator = build_generator(config)
        if args.labels:
            stage_labels(config, generator)
        if args.reencode:
            stage_reencode(config, generator)
    if args.train:
        stage_train(config)
    if args.h1:
        stage_h1(config)
    if not any((args.labels, args.reencode, args.train, args.h1)):
        parser.error("pick at least one stage")


if __name__ == "__main__":
    main()
