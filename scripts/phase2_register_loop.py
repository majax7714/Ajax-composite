#!/usr/bin/env python3
"""Phase 2 — the register loop (H2, the core claim). Plan: docs/PHASE2-PLAN.md.

GPU stages (Kaggle):
  --score    kaggle_launch.py launch phase2_score   (~0.7h)
             Score all Phase-1 candidates with V-v2b -> runs/phase2/v_scores.json
  --train    kaggle_launch.py launch phase2_train   (~2-2.5h)
             Likelihood-steering imitation (D10): synthesized failure prefixes
             -> register r_k -> teacher-forced -logP_G(passing candidate).
             Trains {injector, r_0 encoder W_0, U}; G frozen 4-bit.
             Saves runs/phase2/register_modules.pt, selected on val loss.
  --full     kaggle_launch.py launch phase2_full    (~5.5h)
             HumanEval: FULL (N=8, sequential, register updating) and
             B1 (N=8, register frozen at r_0 — batched; i.i.d. by construction).
             Every candidate executed. Resumable JSONL.
  --b2       kaggle_launch.py launch phase2_b2      (~4.5h)
             B2 in-context refinement, N=8, V-v2b scored, executed.

Local stage:
  --h2       The gate verdict: Δpass@1/Δpass@k (FULL−B1, FULL−B2) with
             problem-level bootstrap CIs at matched compute; B1' read from the
             frozen Phase-1 artifact (identical candidates, same reranker);
             verifier staleness check; register health report.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).parents[1]
sys.path.insert(0, str(REPO / "src"))

from rgr.config import Config, load_config
from rgr.types import SplitRole

OUT = Path("runs/phase2")
LABELS = Path("artifacts/phase1_labels.jsonl")
PHI_DIR = Path("artifacts/phase1_phi")
PHI_PROBLEM_DIR = Path("artifacts/phase1_phi_problems")
V2B_LORA = Path("artifacts/v2b_lora")
V_SCORES = Path("artifacts/v_scores.json")  # produced by --score, re-bundled
LOCK_A = Path("artifacts/lock_a.jsonl")
B1_PRIME_SCORES = Path("artifacts/heldout_scores.json")  # v2b scores of lock_a


def fname(problem_id: str) -> str:
    return problem_id.replace("/", "__") + ".npy"


# --------------------------------------------------------------------------
# --score
# --------------------------------------------------------------------------

def stage_score(config: Config) -> None:
    from rgr.data.mbpp import load_mbpp
    from rgr.verifier.qlora import QloraVerifier

    verifier = QloraVerifier(str(V2B_LORA))
    print("loading V-v2b ...")
    verifier.load()
    prompts = {p.problem_id: p.prompt for p in load_mbpp().problems}
    records = [json.loads(line) for line in open(LABELS)]

    scores: dict[str, list[float | None]] = {}
    chunk = 16
    for start in range(0, len(records), chunk):
        rows = records[start : start + chunk]
        batch_scores = verifier.score_texts(
            [(prompts[r["problem_id"]], r["code"]) for r in rows]
        )
        for r, s in zip(rows, batch_scores):
            scores.setdefault(r["problem_id"], [None] * 16)[r["idx"]] = (
                s if r["code"] is not None else 0.0
            )
        if (start // chunk) % 25 == 0:
            print(f"{start + len(rows)}/{len(records)} scored", flush=True)

    OUT.mkdir(parents=True, exist_ok=True)
    json.dump(scores, open(OUT / "v_scores.json", "w"))
    print(f"wrote {OUT / 'v_scores.json'}")


# --------------------------------------------------------------------------
# --train
# --------------------------------------------------------------------------

def stage_train(config: Config) -> None:
    import numpy as np
    import torch

    from rgr.data.mbpp import load_mbpp
    from rgr.generator.formatting import SYSTEM_PROMPT, build_prompt
    from rgr.generator.injection import RegisterInjector
    from rgr.generator.model import Generator
    from rgr.register.update import RegisterUpdate
    from rgr.training.imitation import bucket_by_k, build_examples

    torch.manual_seed(config.run.seed)
    t_config = config.extra["register_train"]
    epochs = int(t_config.get("epochs", 3))
    batch_size = int(t_config.get("batch_size", 4))
    lr = float(t_config.get("lr", 1e-4))
    per_problem = int(t_config.get("examples_per_problem", 12))
    k_max = int(t_config.get("k_max", 7))

    generator = Generator(config.generator)
    print(f"loading {config.generator.model_name} ...")
    generator.load()
    model, tokenizer = generator._model, generator._tokenizer
    device, d_model = generator.device, generator.d_model
    d_r = config.register.d_r

    injector = RegisterInjector(d_r, config.register.k_soft_tokens, d_model).to(device).float()
    w0 = torch.nn.Linear(d_model, d_r).to(device).float()
    updater = RegisterUpdate(
        d_r, d_model,
        rms_normalize=config.register.rms_normalize,
        max_update_norm=config.register.max_update_norm,
    ).to(device).float()

    records = [json.loads(line) for line in open(LABELS)]
    by_pid: dict[str, list[dict]] = {}
    for r in records:
        by_pid.setdefault(r["problem_id"], []).append(r)
    for rows in by_pid.values():
        rows.sort(key=lambda r: r["idx"])
    v_scores = json.load(open(V_SCORES))
    problems = {p.problem_id: p for p in load_mbpp().problems}
    val_pids = {r["problem_id"] for r in records if r["split"] == "val"}

    def examples_for(pids):
        passed = {pid: [r["passed"] for r in by_pid[pid]] for pid in pids}
        return build_examples(passed, per_problem=per_problem, k_max=k_max,
                              seed=config.run.seed)

    train_examples = examples_for([p for p in by_pid if p not in val_pids])
    val_examples = examples_for(val_pids)
    print(f"examples: train {len(train_examples)}, val {len(val_examples)}")

    phi_cache = {pid: torch.tensor(np.load(PHI_DIR / fname(pid)).astype(np.float32))
                 for pid in by_pid}
    phi_problem_cache = {pid: torch.tensor(
        np.load(PHI_PROBLEM_DIR / fname(pid)).astype(np.float32)) for pid in by_pid}

    embed_layer = model.get_input_embeddings()

    def chat_prompt_ids(pid):
        messages = [{"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": build_prompt(problems[pid].prompt)}]
        enc = tokenizer.apply_chat_template(messages, add_generation_prompt=True,
                                            return_tensors="pt")
        return getattr(enc, "input_ids", enc)[0]

    prompt_ids_cache: dict[str, "torch.Tensor"] = {}

    def batch_loss(batch):
        k = batch[0].k
        r0 = w0(torch.stack([phi_problem_cache[e.problem_id] for e in batch]).to(device))
        if k:
            phis = torch.stack([phi_cache[e.problem_id][list(e.prefix_idx)] for e in batch]).to(device)
            vs = torch.tensor([[v_scores[e.problem_id][i] for i in e.prefix_idx]
                               for e in batch], dtype=torch.float32).to(device)
            register = r0
            for t in range(k):
                register = updater.forward(register, phis[:, t, :], vs[:, t])
        else:
            register = r0
        soft = injector(register).to(model.dtype)  # (b, k_soft, d_model)

        losses = []
        for row, e in enumerate(batch):
            if e.problem_id not in prompt_ids_cache:
                prompt_ids_cache[e.problem_id] = chat_prompt_ids(e.problem_id)
            p_ids = prompt_ids_cache[e.problem_id].to(device)
            target_text = by_pid[e.problem_id][e.target_idx]["text"]
            t_ids = tokenizer(target_text, return_tensors="pt", add_special_tokens=False,
                              truncation=True, max_length=config.generator.max_new_tokens
                              ).input_ids[0].to(device)
            ids = torch.cat([p_ids, t_ids])
            embeds = torch.cat([soft[row], embed_layer(ids.unsqueeze(0))[0].to(soft.dtype)]
                               ).unsqueeze(0)
            labels = torch.cat([
                torch.full((soft.shape[1] + len(p_ids),), -100, device=device,
                           dtype=torch.long),
                t_ids,
            ]).unsqueeze(0)
            out = model(inputs_embeds=embeds, labels=labels)
            losses.append(out.loss.float())
        return torch.stack(losses).mean()

    @torch.no_grad()
    def val_loss():
        batches = bucket_by_k(val_examples, batch_size, seed=0)
        total, n = 0.0, 0
        for batch in batches:
            total += float(batch_loss(batch)) * len(batch)
            n += len(batch)
        return total / n

    params = (list(injector.parameters()) + list(w0.parameters())
              + list(updater.parameters()))
    optimizer = torch.optim.AdamW(params, lr=lr)
    print(f"trainable params: {sum(p.numel() for p in params):,}")

    base_val = val_loss()
    print(f"val loss before training: {base_val:.4f}")
    best_val, best_state = float("inf"), None
    for epoch in range(epochs):
        batches = bucket_by_k(train_examples, batch_size, seed=config.run.seed + epoch)
        for step, batch in enumerate(batches):
            loss = batch_loss(batch)
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(params, 1.0)
            optimizer.step()
            if (step + 1) % 50 == 0:
                print(f"epoch {epoch + 1} step {step + 1}/{len(batches)} "
                      f"loss {float(loss):.4f}", flush=True)
        vl = val_loss()
        marker = ""
        if vl < best_val:
            best_val = vl
            best_state = {
                "injector": {k: v.cpu().clone() for k, v in injector.state_dict().items()},
                "w0": {k: v.cpu().clone() for k, v in w0.state_dict().items()},
                "updater": {k: v.cpu().clone() for k, v in updater.state_dict().items()},
            }
            marker = "  <- best"
        print(f"epoch {epoch + 1}: val loss {vl:.4f}{marker}", flush=True)

    OUT.mkdir(parents=True, exist_ok=True)
    torch.save({
        "modules": best_state,
        "val_loss": best_val,
        "val_loss_untrained": base_val,
        "d_r": d_r, "k_soft": config.register.k_soft_tokens, "d_model": d_model,
    }, OUT / "register_modules.pt")
    print(f"saved register_modules.pt (val {best_val:.4f}, untrained {base_val:.4f})")


# --------------------------------------------------------------------------
# --full / --b2 (HumanEval comparison runs)
# --------------------------------------------------------------------------

def load_register_stack(config: Config, generator):
    import torch

    from rgr.generator.injection import RegisterInjector
    from rgr.register.encoder import ProblemRegisterEncoder
    from rgr.register.update import RegisterUpdate

    checkpoint = torch.load(Path("artifacts/register_modules.pt"), weights_only=True)
    device = generator.device
    injector = RegisterInjector(checkpoint["d_r"], checkpoint["k_soft"],
                                checkpoint["d_model"]).to(device).float()
    injector.load_state_dict(checkpoint["modules"]["injector"])
    encoder = ProblemRegisterEncoder(checkpoint["d_r"], checkpoint["d_model"],
                                     embed_problem=generator.embed_problem).to(device).float()
    encoder.proj.load_state_dict(checkpoint["modules"]["w0"])
    updater = RegisterUpdate(checkpoint["d_r"], checkpoint["d_model"]).to(device).float()
    updater.load_state_dict(checkpoint["modules"]["updater"])
    for module in (injector, encoder, updater):
        module.eval()
        for p in module.parameters():
            p.requires_grad_(False)
    generator.injector = injector
    return encoder, updater


def run_comparison(config: Config, conditions: list[str], out_tag: str) -> None:
    import torch

    from rgr.data.humaneval import load_humaneval
    from rgr.execution.sandbox import DaytonaBackend
    from rgr.generator.formatting import build_prompt
    from rgr.generator.model import Generator
    from rgr.loop.baselines import run_b2
    from rgr.loop.budget import ComputeLedger
    from rgr.loop.refine import run_refine
    from rgr.results import append_jsonl, read_jsonl, trajectory_record
    from rgr.training.labels import ExecutionPool
    from rgr.types import StepRecord, Trajectory
    from rgr.verifier.qlora import QloraVerifier

    torch.manual_seed(config.run.seed)
    generator = Generator(config.generator)
    print(f"loading {config.generator.model_name} ...")
    generator.load()
    verifier = QloraVerifier(str(V2B_LORA))
    print("loading V-v2b ...")
    verifier.load()

    need_register = any(c in ("full", "b1") for c in conditions)
    encoder = updater = None
    if need_register:
        encoder, updater = load_register_stack(config, generator)

    n = config.loop.t_max
    problems = load_humaneval().checkout(SplitRole.HELDOUT_EVAL)
    out_path = OUT / f"{out_tag}.jsonl"
    done = {(r["problem_id"], r["condition"]) for r in read_jsonl(out_path)} \
        if out_path.exists() else set()
    if done:
        print(f"resuming: {len(done)} (problem, condition) pairs present")

    pool = ExecutionPool(lambda: DaytonaBackend(config.execution.timeout_seconds), size=4)
    try:
        for i, problem in enumerate(problems):
            for condition in conditions:
                if (problem.problem_id, condition) in done:
                    continue
                if condition == "full":
                    trajectory = run_refine(
                        problem, generator, verifier, encoder, updater,
                        t_max=n, freeze_register=False, early_stop=False,
                    )
                elif condition == "b1":
                    # Frozen register => steps are i.i.d. given r_0; batching is
                    # an efficiency move with the same distribution and budget.
                    r0 = encoder.init(problem)
                    ledger = ComputeLedger()
                    trajectory = Trajectory(problem_id=problem.problem_id,
                                            condition="b1", ledger=ledger)
                    candidates = generator.sample_batch(
                        build_prompt(problem.prompt), n, register=r0)
                    for t, candidate in enumerate(candidates):
                        ledger.charge_generation(candidate.prompt_tokens,
                                                 candidate.generated_tokens)
                        score = verifier.score(problem, candidate, None)
                        ledger.charge_verifier()
                        trajectory.steps.append(StepRecord(
                            step=t, candidate=candidate, verifier_score=score,
                            register_norm=updater.norm(r0)))
                elif condition == "b2":
                    trajectory = run_b2(problem, generator, generator, verifier, n=n)
                else:
                    raise ValueError(condition)

                executions = pool.execute_all(
                    problem, [s.candidate for s in trajectory.steps])
                append_jsonl(out_path, trajectory_record(
                    trajectory, list(executions), tag=out_tag, seed=config.run.seed))
            if (i + 1) % 10 == 0:
                print(f"{i + 1}/{len(problems)} problems done", flush=True)
    finally:
        pool.close()
    print(f"complete -> {out_path}")


# --------------------------------------------------------------------------
# --h2 (local verdict)
# --------------------------------------------------------------------------

def stage_h2(config: Config) -> None:
    from rgr.evals.bootstrap import bootstrap_ci
    from rgr.evals.calibration import auroc
    from rgr.register.diagnostics import register_health
    from rgr.results import read_jsonl, selected_passed

    n = config.loop.t_max

    def outcomes(path, condition):
        rows = [r for r in read_jsonl(path) if r["condition"] == condition]
        assert all(len(r["steps"]) == n for r in rows), f"unmatched compute in {condition}"
        return {r["problem_id"]: r for r in rows}

    full = outcomes(OUT / "full_b1.jsonl", "full")
    b1 = outcomes(OUT / "full_b1.jsonl", "b1")
    b2_path = OUT / "b2.jsonl"
    b2 = outcomes(b2_path, "b2") if b2_path.exists() else None

    # B1' from frozen Phase-1 artifacts (identical candidates + reranker)
    b1p_rows = json.load(open(B1_PRIME_SCORES))
    by_pid: dict[str, list] = {}
    for r in b1p_rows:
        by_pid.setdefault(r["problem_id"], []).append((r["v2b_score"], r["passed"]))
    b1p_pass = {pid: max(rows, key=lambda x: x[0])[1] for pid, rows in by_pid.items()}

    pids = sorted(full)
    print(f"=== H2 verdict ({len(pids)} problems, N={n} matched) ===")

    def report(name, other):
        paired = [(selected_passed(full[p]), selected_passed(other[p])) for p in pids]
        delta = bootstrap_ci(paired, lambda s: sum(a - b for a, b in s) / len(s))
        f_rate = sum(a for a, _ in paired) / len(paired)
        o_rate = sum(b for _, b in paired) / len(paired)
        verdict = "BEATS" if (delta.point > 0 and delta.excludes_zero) else "ties/loses"
        print(f"FULL {f_rate:.4f} vs {name} {o_rate:.4f} | Δ {delta.point:+.4f} "
              f"CI [{delta.lo:+.4f}, {delta.hi:+.4f}] -> FULL {verdict} {name}")
        return delta

    d_b1 = report("B1 ", b1)
    d_b2 = report("B2 ", b2) if b2 else None
    b1p_rate = sum(b1p_pass[p] for p in pids) / len(pids)
    print(f"B1' (no injection, frozen Phase-1): {b1p_rate:.4f} (control, not a gate)")

    # verifier staleness on current-policy (FULL) candidates
    scores, labels = [], []
    for p in pids:
        for s in full[p]["steps"]:
            scores.append(s["verifier_score"])
            labels.append(s["execution"]["passed"])
    if len(set(labels)) == 2:
        stale = auroc(scores, labels)
        print(f"verifier AUROC on FULL rollouts: {stale:.4f} "
              f"(Phase-1 heldout was 0.7951; drop >0.05 => refresh V)")

    # register health from recorded norms
    class _T:  # adapt records to diagnostics input
        def __init__(self, r):
            from rgr.types import StepRecord, Candidate, Trajectory
            self.steps = [StepRecord(step=s["step"], candidate=Candidate(text="", code=None),
                                     verifier_score=s["verifier_score"],
                                     register_norm=s["register_norm"],
                                     register_delta_norm=s["register_delta_norm"])
                          for s in r["steps"]]
    health = register_health([_T(full[p]) for p in pids])
    print(f"register health: mean‖r‖ {health.mean_norm:.3f}, meanΔ {health.mean_delta_norm:.4f}, "
          f"collapsed={health.collapsed}, blown_up={health.blown_up}")

    gate = (d_b1.point > 0 and d_b1.excludes_zero
            and (d_b2 is None or (d_b2.point > 0 and d_b2.excludes_zero)))
    print("\nGATE:", ("PASS" if gate else "FAIL")
          + ("" if b2 else "  (B2 pending — verdict incomplete)"))
    json.dump({"delta_b1": vars(d_b1), "delta_b2": vars(d_b2) if d_b2 else None,
               "b1_prime": b1p_rate, "gate_pass": gate},
              open("artifacts/h2_result.json", "w"), indent=2, default=str)

    # B2 completion of the record + pre-registered branch verdict (PRE-B2-HANDOFF
    # §3). Additive: this reads the frozen b2.jsonl, it does not alter B2's run.
    if b2:
        full_rate = sum(selected_passed(full[p]) for p in pids) / len(pids)
        b2_rate = sum(selected_passed(b2[p]) for p in pids) / len(pids)
        b1_rate = sum(selected_passed(b1[p]) for p in pids) / len(pids)
        paired = [(selected_passed(b2[p]), selected_passed(b1[p])) for p in pids]
        d_b2_b1 = bootstrap_ci(paired, lambda s: sum(a - b for a, b in s) / len(s))
        # Branch A = B2 ties B1 (CI includes 0); Branch B = B2 beats B1.
        branch = "B" if (d_b2_b1.point > 0 and d_b2_b1.excludes_zero) else "A"

        def gens(rec):
            return rec["ledger"]["generations"]

        def ptok(cond):
            return sum(cond[p]["ledger"]["prompt_tokens"] for p in pids)

        matched = all(gens(c[p]) == n for c in (full, b1, b2) for p in pids)
        b2_result = {
            "_label": "B2 (in-context refinement) completes the H2 kill record; "
                      "does NOT change the FAIL gate (claim required beating both).",
            "n_problems": len(pids),
            "N_matched": n,
            "ledger_generations_matched": matched,
            "full_pass_at_1": full_rate,
            "b1_pass_at_1": b1_rate,
            "b2_pass_at_1": b2_rate,
            "delta_full_minus_b2": vars(d_b2),   # kill-criterion piece ("ties both")
            "delta_b2_minus_b1": vars(d_b2_b1),  # pre-registered branch discriminator
            "branch": branch,
            "branch_note": ("A = B2 ties B1 (no iteration headroom at this scale); "
                            "B = B2 beats B1 (register parasitic to in-context text)."),
            "prompt_tokens_full": ptok(full),
            "prompt_tokens_b2": ptok(b2),  # audit: B2's growing context (favors B2)
        }
        json.dump(b2_result, open("artifacts/h2_b2_result.json", "w"),
                  indent=2, default=str)
        print(f"\nB2 branch {branch}: B2 {b2_rate:.4f} vs B1 {b1_rate:.4f} | "
              f"Δ(B2−B1) {d_b2_b1.point:+.4f} CI [{d_b2_b1.lo:+.4f}, {d_b2_b1.hi:+.4f}]"
              f" | ledger matched={matched}")
        print("wrote artifacts/h2_b2_result.json")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/phase2_register.toml")
    for flag in ("--score", "--train", "--full", "--b2", "--h2"):
        parser.add_argument(flag, action="store_true")
    args = parser.parse_args()
    config = load_config(args.config)

    if args.score:
        stage_score(config)
    if args.train:
        stage_train(config)
    if args.full:
        run_comparison(config, ["full", "b1"], "full_b1")
    if args.b2:
        run_comparison(config, ["b2"], "b2")
    if args.h2:
        stage_h2(config)
    if not any(vars(args)[k] for k in ("score", "train", "full", "b2", "h2")):
        parser.error("pick a stage")


if __name__ == "__main__":
    main()
