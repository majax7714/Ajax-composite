#!/usr/bin/env python3
"""Phase 3a option (a) — competitive (stdin/stdout) benchmark screen.

BigCodeBench (function-call) failed the gate on random samples: shallow reachable
tail (~0.10 headroom) at both 0.5B and 1.5B ([PHASE_3.md] §4.2). Competitive
benchmarks are the class most likely to have a DEEP reachable tail in the coverage
band. This file screens **LiveCodeBench** (contamination-controlled, difficulty
tiers), which needs a stdin/stdout execution harness (run candidate as a program,
feed stdin, compare stdout) rather than the BigCodeBench unittest path.

Step 1 (this): `characterize_lcb` — does it load on datasets 5.0? schema? test-case
format/compression? difficulty distribution? tests/problem (criterion 2)? De-risks
the executor build before writing it.
"""
from __future__ import annotations

import json

import modal

IMAGE = modal.Image.debian_slim(python_version="3.12").pip_install(
    "datasets==5.0.0", "huggingface_hub==1.11.0")
VOL = modal.Volume.from_name("rgr-hf-cache", create_if_missing=True)
app = modal.App("rgr-lcb")


@app.function(image=IMAGE, volumes={"/cache": VOL}, timeout=3600,
              env={"HF_HOME": "/cache/hf"})
def characterize_lcb() -> dict:
    """Try to load LiveCodeBench a few ways; report schema + a decoded test-case
    sample + difficulty distribution + tests/problem."""
    from collections import Counter

    from datasets import load_dataset

    report = {}

    def try_load(name, **kw):
        try:
            ds = load_dataset(name, split="test", **kw)
            return ds, None
        except Exception as e:
            return None, repr(e)[:200]

    ds = None
    for name, kw in [
        ("livecodebench/code_generation_lite", {"version_tag": "release_v5"}),
        ("livecodebench/code_generation_lite", {}),
        ("livecodebench/code_generation", {}),
    ]:
        ds, err = try_load(name, **kw)
        report[f"load::{name}::{kw}"] = "OK" if ds is not None else f"FAIL {err}"
        if ds is not None:
            report["loaded_as"] = f"{name} {kw}"
            break

    if ds is None:
        return report

    report["n"] = len(ds)
    report["columns"] = ds.column_names
    row = ds[0]
    # difficulty distribution
    if "difficulty" in ds.column_names:
        report["difficulty_dist"] = dict(Counter(ds[i]["difficulty"] for i in range(len(ds))))
    # inspect a test-case field: public/private test cases, format, compression
    for tc_field in ("public_test_cases", "private_test_cases", "test_cases", "test"):
        if tc_field in ds.column_names:
            v = row[tc_field]
            info = {"type": type(v).__name__, "len": len(v) if hasattr(v, "__len__") else None,
                    "preview": str(v)[:300]}
            # try to decode: JSON, or base64+zlib+json (LiveCodeBench private cases)
            try:
                info["as_json_len"] = len(json.loads(v))
                info["decode"] = "json"
            except Exception:
                try:
                    import base64
                    import pickle
                    import zlib
                    dec = json.loads(zlib.decompress(base64.b64decode(v.encode())).decode())
                    info["decoded_json_len"] = len(dec)
                    info["decode"] = "b64+zlib+json"
                    info["case0_keys"] = list(dec[0].keys()) if dec else None
                except Exception as e2:
                    info["decode"] = f"unknown ({repr(e2)[:80]})"
            report[f"field::{tc_field}"] = info
    # count tests/problem (criterion 2) on a sample, and starter_code presence
    report["fields_present"] = {f: (f in ds.column_names)
                                for f in ("question_content", "starter_code", "difficulty",
                                          "public_test_cases", "private_test_cases")}
    return report


# ---- coverage screen: generate + stdin/stdout judge ----

MODEL = "Qwen/Qwen2.5-Coder-1.5B-Instruct"
GEN_IMAGE = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("vllm==0.11.0", "transformers==4.57.0", "datasets==5.0.0")
    .env({"HF_HOME": "/cache/hf", "TOKENIZERS_PARALLELISM": "false",
          "VLLM_LOGGING_LEVEL": "WARNING"})
)
EXEC_IMAGE = modal.Image.debian_slim(python_version="3.12").pip_install(
    "datasets==5.0.0", "numpy").env({"HF_HOME": "/cache/hf"})

DATASET = "livecodebench/code_generation"


def _extract_code(text):
    import re
    m = re.search(r"```(?:python|py)?\s*\n(.*?)```", text, re.DOTALL)
    if m:
        return m.group(1).strip() or None
    s = text.strip()
    return s if re.match(r"^(import |from |def |class |n |input\()", s) else None


def _stdin_problems(ds, difficulty):
    """Indices of stdin-type problems at the given difficulty."""
    import json as _j
    out = []
    for i in range(len(ds)):
        if ds[i]["difficulty"] != difficulty:
            continue
        try:
            pub = _j.loads(ds[i]["public_test_cases"])
            if pub and pub[0].get("testtype") == "stdin":
                out.append(i)
        except Exception:
            pass
    return out


@app.function(image=GEN_IMAGE, gpu="L4", volumes={"/cache": VOL}, timeout=7200)
def lcb_generate(n_problems: int = 100, k: int = 50, difficulty: str = "medium",
                 seed: int = 17, model: str = MODEL):
    """Generate k programs per LiveCodeBench stdin problem (random sample)."""
    import random as _rnd

    from datasets import load_dataset
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams

    ds = load_dataset(DATASET, split="test")
    idx = _stdin_problems(ds, difficulty)
    _rnd.Random(seed).shuffle(idx)
    idx = idx[:n_problems]
    tok = AutoTokenizer.from_pretrained(model)
    SYS = ("You are an expert competitive programmer. Write a complete Python 3 "
           "program that reads from standard input and writes the answer to standard "
           "output. Respond with a single fenced Python code block and nothing else.")

    def prompt(i):
        return tok.apply_chat_template(
            [{"role": "system", "content": SYS},
             {"role": "user", "content": ds[i]["question_content"]}],
            add_generation_prompt=True, tokenize=False)

    prompts = [prompt(i) for i in idx]
    llm = LLM(model=model, dtype="bfloat16", gpu_memory_utilization=0.90,
              max_model_len=8192, seed=seed)
    sp = SamplingParams(n=k, temperature=0.8, top_p=0.95, max_tokens=1536, seed=seed)
    outs = llm.generate(prompts, sp)
    return {"question_ids": [ds[i]["question_id"] for i in idx],
            "codes": [[_extract_code(o.text) for o in outs[j].outputs] for j in range(len(idx))],
            "k": k, "difficulty": difficulty, "model": model}


@app.function(image=EXEC_IMAGE, volumes={"/cache": VOL}, timeout=7200, cpu=32.0,
              memory=65536, env={"HF_HOME": "/cache/hf"})
def lcb_exec(question_ids: list, codes: list, cap_private: int = 12,
             timeout_s: int = 8) -> list:
    """Hardened stdin/stdout judge. For each candidate, run the program per test
    case (public + up to cap_private private), short-circuit on first failure,
    compare normalized stdout. Same process-group/file-output/killpg/rlimit hardening
    as the BigCodeBench executor."""
    import json as _j
    import os
    import signal
    import subprocess
    import sys
    import tempfile
    from concurrent.futures import ThreadPoolExecutor
    from pathlib import Path

    from datasets import load_dataset

    ds = load_dataset(DATASET, split="test")
    by_id = {}
    for i in range(len(ds)):
        qid = ds[i]["question_id"]
        if qid in set(question_ids):
            try:
                cases = _j.loads(ds[i]["public_test_cases"]) + _j.loads(ds[i]["private_test_cases"])
            except Exception:
                cases = _j.loads(ds[i]["public_test_cases"])
            pub = [c for c in cases if c.get("testtype") == "stdin"]
            by_id[qid] = pub[:3 + cap_private]

    PRE = ("import resource as _rs\n"
           f"try: _rs.setrlimit(_rs.RLIMIT_CPU, ({timeout_s}, {timeout_s})); "
           "_rs.setrlimit(_rs.RLIMIT_AS, (3*1024**3//2, 3*1024**3//2))\n"
           "except Exception: pass\n")

    def norm(s):
        return "\n".join(l.rstrip() for l in s.strip("\n").split("\n")).rstrip()

    def run_case(code, stdin_str):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "s.py").write_text(PRE + code)
            (Path(d) / "in.txt").write_text(stdin_str)
            outf = Path(d) / "o.txt"
            with open(d + "/in.txt") as fin, open(outf, "wb") as fout:
                try:
                    p = subprocess.Popen([sys.executable, "s.py"], stdin=fin, stdout=fout,
                                         stderr=subprocess.DEVNULL, cwd=d, start_new_session=True)
                except Exception:
                    return None
                try:
                    p.wait(timeout=timeout_s)
                except subprocess.TimeoutExpired:
                    p_ok = False
                else:
                    p_ok = (p.returncode == 0)
                try:
                    os.killpg(os.getpgid(p.pid), signal.SIGKILL)
                except (ProcessLookupError, PermissionError):
                    pass
                try:
                    p.wait(timeout=5)
                except Exception:
                    pass
            return outf.read_text(errors="replace") if p_ok else None

    def judge(args):
        code, qid = args
        if code is None:
            return {"passed": False, "err": "no_code"}
        cases = by_id.get(qid, [])
        if not cases:
            return {"passed": False, "err": "no_tests"}
        for c in cases:
            out = run_case(code, c["input"])
            if out is None:
                return {"passed": False, "err": "runtime"}
            if norm(out) != norm(c["output"]):
                return {"passed": False, "err": "wrong_answer"}
        return {"passed": True, "err": ""}

    results = []
    with ThreadPoolExecutor(max_workers=32) as tp:
        for qid, row in zip(question_ids, codes):
            results.append(list(tp.map(judge, [(c, qid) for c in row])))
    return results


@app.local_entrypoint()
def lcb_screen(n_problems: int = 100, k: int = 50, difficulty: str = "medium",
               model: str = MODEL, tag: str = "lcb_med"):
    from collections import Counter
    from math import comb
    from pathlib import Path

    def pak(n, c, kk):
        return 1.0 if n - c < kk else 1.0 - comb(n - c, kk) / comb(n, kk)

    gen = lcb_generate.remote(n_problems, k, difficulty, 17, model)
    Path("runs/modal").mkdir(parents=True, exist_ok=True)
    Path(f"runs/modal/lcb_cand_{tag}.json").write_text(json.dumps(gen))
    results = lcb_exec.remote(gen["question_ids"], gen["codes"])

    counts, errs = [], Counter()
    for res in results:
        counts.append((len(res), sum(r["passed"] for r in res)))
        errs.update(r["err"] for r in res)

    def mpak(kk):
        return sum(pak(n, c, kk) for n, c in counts) / len(counts)

    p8, p50 = mpak(8), mpak(min(k, 50))
    in_band, hd = 0.30 <= p8 <= 0.60, (p50 - p8) >= 0.15
    result = {"benchmark": f"LiveCodeBench/code_generation[{difficulty},stdin]",
              "generator": model, "n_problems": len(counts), "k": k,
              "pass@1": mpak(1), "pass@8": p8, "pass@50": p50, "headroom": p50 - p8,
              "error_breakdown": dict(errs), "band": in_band, "headroom_ok": hd,
              "gate": "PASS" if (in_band and hd) else "does-not-qualify"}
    Path("artifacts").mkdir(exist_ok=True)
    Path(f"artifacts/phase3a_screen_{tag}.json").write_text(json.dumps(result, indent=2))
    print(f"\n=== LiveCodeBench screen [{difficulty}, stdin] @ {model.split('/')[-1]} "
          f"({len(counts)} problems, k={k}) ===")
    print(f"pass@1 {result['pass@1']:.3f}  pass@8 {p8:.3f}  pass@50 {p50:.3f}  "
          f"(headroom {p50-p8:+.3f})")
    print(f"coverage band [0.30,0.60]: {in_band}   headroom ≥0.15: {hd}")
    print(f"errors: {dict(errs)}")
    print(f"\n3a gate ({tag}): {result['gate']}")
    print(f"wrote artifacts/phase3a_screen_{tag}.json")


@app.local_entrypoint()
def char_lcb_main():
    r = characterize_lcb.remote()
    from pathlib import Path
    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/lcb_characterization.json").write_text(json.dumps(r, indent=2, default=str))
    print("=== LiveCodeBench characterization ===")
    print(json.dumps(r, indent=2, default=str)[:3000])
    print("wrote artifacts/lcb_characterization.json")
