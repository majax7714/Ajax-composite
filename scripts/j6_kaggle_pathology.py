"""Phase 6 P1 — pathology-origin cell, KAGGLE re-baseline ([PHASE_6.md] P1 + the
Kaggle amendment). Self-contained vLLM/bf16 kernel (the Kaggle image has no
`modal`, so nothing is imported from modal_h1.py).

Runs the two frozen J5-Q1 cells on one checkpoint, on Kaggle T4:
  Q1a — D2c code cell: 44 frozen artifacts x {E0 no-context, E1 D2C context}
        x k=8, ALL-CASES judge, mean frac (blend geometry: cond vs iid vs copy).
  Q1b — language cell: 20 manip problems x {E0, HINT} x k=25, short-circuit
        judge, per-sample mean pass (harm vanish/persist band).

SYNC NOTE — the scaffold prompt, the D2C/HINT context wording, the 44-artifact
selection, and the judge are COPIED VERBATIM from scripts/modal_h1.py
(h1_gen_lcb / _d2c_context / _hint_context / _d2c_artifacts / h1_lcb_exec) and
scripts/w0_recomputes-adjacent frozen text. If any of those change in modal_h1,
change them here too, or the Kaggle cell stops being comparable to the record.
Config is identical to the Modal cell (seed 17, T=0.8, top_p 1.0, bf16); the ONLY
intended difference is the GPU/stack — that is the re-baseline.

Invoked by kaggle_launch.py's runner as:
  python scripts/j6_kaggle_pathology.py --name <short> --model <hf_id> --rev <sha>
Writes runs/j6_kaggle/h6_pathology_origin_kaggle_<name>.json (+ raw pools).
"""
import argparse
import json
import os
import random
import signal
import statistics as st
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LCB_DATASET = "livecodebench/code_generation"
OUT_DIR = REPO / "runs" / "j6_kaggle"

# ---- frozen wording, verbatim from modal_h1.py -----------------------------

def _scaffold_prompt(question, context):
    head = "Problem:\n" + question.strip()
    if context:
        head += "\n\n" + context.rstrip()
    return (head + "\n\nA complete Python 3 program that reads from standard "
            "input and writes the answer to standard output:\n\n```python\n")


def _d2c_context(a):
    npass = a["n_tests"] - a["n_failed"]
    code = (a.get("code") or "")[:3000]
    return (f"A previous attempt:\n```python\n{code}\n```\n"
            f"This attempt passed {npass} of {a['n_tests']} tests.\n"
            "Improve it so that all tests pass.")


def _hint_context(hint):
    return f"Approach hint: {hint}\nWrite a correct complete program."


def _d2c_artifacts():
    """The frozen 44-artifact set (W3 §2 rule) — model-independent inputs."""
    w0b = json.loads((REPO / "artifacts/w0b_copy_null.json").read_text())
    cand = json.loads((REPO / "runs/modal/lcb_cand_lcb_r2_base_T08.json").read_text())
    res = json.loads((REPO / "runs/modal/lcb_res_lcb_r2_base_T08.json").read_text())
    codes_by_qid = dict(zip(res["question_ids"], cand["codes"]))
    rows_by_qid = dict(zip(res["question_ids"], res["results"]))
    arts = []
    for qid, v in w0b["per_problem"].items():
        band = v["band_40_60_idx"]
        if not band:
            continue
        fr = {a["cand_idx"]: a["copy_null_frac"] for a in v["partial_artifacts"]}
        for bi in sorted(band, key=lambda i: (abs(fr[i] - 0.5), i)):
            if codes_by_qid[qid][bi]:
                row = rows_by_qid[qid][bi]
                arts.append({"qid": qid, "cand_idx": bi, "code": codes_by_qid[qid][bi],
                             "frac": row["frac"], "n_tests": row["n_tests"],
                             "n_failed": row["n_tests"] - row["n_passed"]})
                break
    assert len(arts) == 44, len(arts)
    return arts


def _wilcoxon_mc_one_sided(diffs, trials=20000, seed=17):
    rng = random.Random(seed)
    obs = sum(diffs) / len(diffs)
    hits = 0
    for _ in range(trials):
        s = sum(d if rng.random() < 0.5 else -d for d in diffs) / len(diffs)
        if s >= obs:
            hits += 1
    return (hits + 1) / (trials + 1)


# ---- judge, verbatim semantics from modal_h1.h1_lcb_exec -------------------

def _judge(question_ids, codes, cap_private=12, timeout_s=8, short_circuit=False):
    from datasets import load_dataset

    ds = load_dataset(LCB_DATASET, split="test")
    want = set(question_ids)
    by_id = {}
    for i in range(len(ds)):
        qid = ds[i]["question_id"]
        if qid in want:
            try:
                cases = (json.loads(ds[i]["public_test_cases"])
                         + json.loads(ds[i]["private_test_cases"]))
            except Exception:
                cases = json.loads(ds[i]["public_test_cases"])
            pub = [c for c in cases if c.get("testtype") == "stdin"]
            by_id[qid] = pub[:3 + cap_private]

    PRE = ("import resource as _rs\n"
           f"try: _rs.setrlimit(_rs.RLIMIT_CPU, ({timeout_s}, {timeout_s})); "
           "_rs.setrlimit(_rs.RLIMIT_AS, (3*1024**3//2, 3*1024**3//2))\n"
           "except Exception: pass\n")

    def norm(s):
        return "\n".join(line.rstrip() for line in s.strip("\n").split("\n")).rstrip()

    def run_case(code, stdin_str):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "s.py").write_text(PRE + code)
            (Path(d) / "in.txt").write_text(stdin_str)
            outf, errf = Path(d) / "o.txt", Path(d) / "e.txt"
            with open(d + "/in.txt") as fin, open(outf, "wb") as fout, \
                    open(errf, "wb") as ferr:
                try:
                    p = subprocess.Popen([sys.executable, "s.py"], stdin=fin,
                                         stdout=fout, stderr=ferr, cwd=d,
                                         start_new_session=True)
                except Exception:
                    return "runtime", "", ""
                try:
                    p.wait(timeout=timeout_s)
                    status = "ok" if p.returncode == 0 else "runtime"
                except subprocess.TimeoutExpired:
                    status = "timeout"
                try:
                    os.killpg(os.getpgid(p.pid), signal.SIGKILL)
                except (ProcessLookupError, PermissionError):
                    pass
                try:
                    p.wait(timeout=5)
                except Exception:
                    pass
            out = outf.read_text(errors="replace")
            elines = [line for line in errf.read_text(errors="replace").strip().splitlines()
                      if line.strip()]
        return status, out, (elines[-1][:200] if elines else "")

    def judge(args):
        code, qid = args
        base = {"passed": False, "n_tests": 0, "n_passed": 0, "frac": 0.0,
                "failing": [], "err": "no_code", "exc": ""}
        if code is None:
            return base
        cases = by_id.get(qid, [])
        if not cases:
            return {**base, "err": "no_tests"}
        n_passed, failing, first_err, first_exc = 0, [], "", ""
        for i, c in enumerate(cases):
            status, out, exc = run_case(code, c["input"])
            if status != "ok":
                failing.append(i)
                first_err = first_err or status
                first_exc = first_exc or exc
            elif norm(out) != norm(c["output"]):
                failing.append(i)
                first_err = first_err or "wrong_answer"
            else:
                n_passed += 1
            if short_circuit and failing:
                break
        return {"passed": not failing, "n_tests": len(cases), "n_passed": n_passed,
                "frac": n_passed / len(cases) if cases else 0.0,
                "failing": failing, "err": first_err, "exc": first_exc}

    out = []
    with ThreadPoolExecutor(max_workers=8) as tp:
        for qid, row in zip(question_ids, codes):
            out.append(list(tp.map(judge, [(c, qid) for c in row])))
    return out


# ---- generation ------------------------------------------------------------

def _generate(llm, question_by_qid, items, n):
    """items: [{qid, context|None}] -> [{qid, codes:[str|None]*n}]."""
    from vllm import SamplingParams
    sp = SamplingParams(n=n, temperature=0.8, top_p=1.0, max_tokens=1536,
                        seed=17, stop=["```", "\nProblem:"])
    prompts = [_scaffold_prompt(question_by_qid[it["qid"]], it.get("context"))
               for it in items]
    outs = llm.generate(prompts, sp)
    return [{"qid": it["qid"], "codes": [(o.text.strip() or None) for o in req.outputs]}
            for it, req in zip(items, outs)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--smoke", action="store_true",
                    help="8 LCB-easy x 8 gate only (wf>=0.85 dg<=0.10)")
    args = ap.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    from datasets import load_dataset
    from vllm import LLM

    ds = load_dataset(LCB_DATASET, split="test")
    q = {ds[i]["question_id"]: ds[i]["question_content"] for i in range(len(ds))}
    llm = LLM(model=args.model, revision=args.rev, dtype="bfloat16",
              gpu_memory_utilization=0.90, max_model_len=8192, seed=17)

    if args.smoke:
        easy = json.loads(
            (REPO / "runs/modal/lcb_res_lcb_r2_base_T08.json").read_text())["question_ids"][:8]
        gen = _generate(llm, q, [{"qid": x, "context": None} for x in easy], 8)
        flat = [c for g in gen for c in g["codes"]]
        wf = sum(1 for c in flat if c) / len(flat)
        dg = sum(1 for c in flat if c and len(c) < 20) / max(1, sum(1 for c in flat if c))
        res = _judge([g["qid"] for g in gen], [g["codes"] for g in gen], short_circuit=True)
        npass = sum(1 for row in res for r in row if r["passed"])
        ok = wf >= 0.85 and dg <= 0.10
        out = {"_label": f"P1 Kaggle smoke — {args.name}", "model": args.model,
               "revision": args.rev, "wf": wf, "dg": dg, "n_pass": npass,
               "n": len(flat), "gate": "PASS" if ok else "FAIL"}
        (OUT_DIR / f"smoke_{args.name}.json").write_text(json.dumps(out, indent=2))
        print(f"=== j6 KAGGLE smoke ({args.name}={args.model}): wf {wf:.3f} dg {dg:.3f} "
              f"pass {npass}/{len(flat)} -> {out['gate']} ===")
        return

    # Q1a — D2c code cell (all-cases judge, mean frac)
    arts = _d2c_artifacts()
    items = ([{"qid": a["qid"], "context": None} for a in arts]
             + [{"qid": a["qid"], "context": _d2c_context(a)} for a in arts])
    dgen = _generate(llm, q, items, 8)
    (OUT_DIR / f"q1a_cand_{args.name}.json").write_text(json.dumps(dgen))
    dres = _judge([g["qid"] for g in dgen], [g["codes"] for g in dgen])
    n = len(arts)
    e0_frac = [st.mean(x["frac"] for x in row) for row in dres[:n]]
    e1_frac = [st.mean(x["frac"] for x in row) for row in dres[n:]]
    copy_null = [a["frac"] for a in arts]
    d_iid = [b - a for a, b in zip(e0_frac, e1_frac)]
    d_copy = [b - a for a, b in zip(copy_null, e1_frac)]
    q1a = {"e0_mean_frac_iid": st.mean(e0_frac), "e1_mean_frac_cond": st.mean(e1_frac),
           "copy_null_mean": st.mean(copy_null),
           "delta_cond_minus_iid": st.mean(d_iid),
           "delta_cond_minus_copy": st.mean(d_copy),
           "p_one_sided_cond_below_iid": _wilcoxon_mc_one_sided([-x for x in d_iid]),
           "p_one_sided_cond_below_copy": _wilcoxon_mc_one_sided([-x for x in d_copy])}
    print(f"Q1a ({args.name}): iid {q1a['e0_mean_frac_iid']:.3f} | cond "
          f"{q1a['e1_mean_frac_cond']:.3f} | copy {q1a['copy_null_mean']:.3f} | "
          f"p_below_iid {q1a['p_one_sided_cond_below_iid']:.4f} "
          f"p_below_copy {q1a['p_one_sided_cond_below_copy']:.4f}")

    # Q1b — language cell (short-circuit judge, mean pass)
    fz = json.loads((REPO / "artifacts/h2_hints_frozen.json").read_text())
    qids = fz["groups"]["manip_check"]
    hints = fz["hints"]
    items = ([{"qid": x, "context": None} for x in qids]
             + [{"qid": x, "context": _hint_context(hints[x])} for x in qids])
    mgen = _generate(llm, q, items, 25)
    (OUT_DIR / f"q1b_cand_{args.name}.json").write_text(json.dumps(mgen))
    mres = _judge([g["qid"] for g in mgen], [g["codes"] for g in mgen], short_circuit=True)
    m = len(qids)
    e0 = [sum(r["passed"] for r in row) / len(row) for row in mres[:m]]
    hi = [sum(r["passed"] for r in row) / len(row) for row in mres[m:]]
    diffs = [b - a for a, b in zip(e0, hi)]
    q1b = {"e0_mean_pass": st.mean(e0), "hint_mean_pass": st.mean(hi),
           "mean_uplift": st.mean(diffs),
           "p_one_sided_uplift": _wilcoxon_mc_one_sided(diffs),
           "saturation_caveat": st.mean(e0) > 0.9}
    print(f"Q1b ({args.name}): E0 {q1b['e0_mean_pass']:.3f} -> HINT "
          f"{q1b['hint_mean_pass']:.3f} (d {q1b['mean_uplift']:+.3f}, "
          f"p {q1b['p_one_sided_uplift']:.4f})")

    out = {"_label": f"Phase 6 P1 KAGGLE re-baseline — {args.name} [PHASE_6.md P1]",
           "model": args.model, "revision": args.rev, "stack": "kaggle-T4/vLLM/bf16",
           "seed": 17, "q1a_d2c": q1a, "q1b_language": q1b}
    (OUT_DIR / f"h6_pathology_origin_kaggle_{args.name}.json").write_text(
        json.dumps(out, indent=2))
    print(f"wrote runs/j6_kaggle/h6_pathology_origin_kaggle_{args.name}.json")


if __name__ == "__main__":
    main()
