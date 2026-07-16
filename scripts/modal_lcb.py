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
        """Return (status, stdout, exception_line). status ∈ {ok, runtime, timeout}."""
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "s.py").write_text(PRE + code)
            (Path(d) / "in.txt").write_text(stdin_str)
            outf, errf = Path(d) / "o.txt", Path(d) / "e.txt"
            with open(d + "/in.txt") as fin, open(outf, "wb") as fout, open(errf, "wb") as ferr:
                try:
                    p = subprocess.Popen([sys.executable, "s.py"], stdin=fin, stdout=fout,
                                         stderr=ferr, cwd=d, start_new_session=True)
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
            elines = [l for l in errf.read_text(errors="replace").strip().splitlines() if l.strip()]
        return status, out, (elines[-1][:200] if elines else "")

    def judge(args):
        """R3/BEST-SO-FAR fix: run ALL cases (no short-circuit), record per-case
        results — frac_tests, failing case ids, error class, first exception."""
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
        n = len(cases)
        return {"passed": n_passed == n, "n_tests": n, "n_passed": n_passed,
                "frac": n_passed / n, "failing": failing,
                "err": "" if n_passed == n else first_err, "exc": first_exc}

    results = []
    with ThreadPoolExecutor(max_workers=32) as tp:
        for qid, row in zip(question_ids, codes):
            results.append(list(tp.map(judge, [(c, qid) for c in row])))
    return results


BASE_MODEL = "Qwen/Qwen2.5-Coder-1.5B"  # completion model — deeper pass@k tail (R2)


@app.function(image=GEN_IMAGE, gpu="L4", volumes={"/cache": VOL}, timeout=7200)
def lcb_r2_generate(n_problems: int = 100, k: int = 50, difficulty: str = "easy",
                    seed: int = 17, arch: str = "base", temperature: float = 1.0,
                    top_p: float = 1.0):
    """R2 tail-un-suppression sweep, LiveCodeBench arm [PHASE_3R.md R2]. arch='base'
    → completion model on a fenced-markdown prompt (the model completes a ```python
    block; stop on the closing fence — clean extraction without chat collapse);
    arch='instruct' → the existing chat path. temperature/top_p swept."""
    import random as _rnd

    from datasets import load_dataset
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams

    ds = load_dataset(DATASET, split="test")
    idx = _stdin_problems(ds, difficulty)
    _rnd.Random(seed).shuffle(idx)
    idx = idx[:n_problems]
    model = BASE_MODEL if arch == "base" else MODEL
    SYS = ("You are an expert competitive programmer. Write a complete Python 3 "
           "program that reads from standard input and writes the answer to standard "
           "output. Respond with a single fenced Python code block and nothing else.")

    if arch == "base":
        prompts = [
            ("Problem:\n" + ds[i]["question_content"].strip() +
             "\n\nA complete Python 3 program that reads from standard input and "
             "writes the answer to standard output:\n\n```python\n") for i in idx]
        stop = ["```", "\nProblem:"]
    else:
        tok = AutoTokenizer.from_pretrained(model)
        prompts = [tok.apply_chat_template(
            [{"role": "system", "content": SYS},
             {"role": "user", "content": ds[i]["question_content"]}],
            add_generation_prompt=True, tokenize=False) for i in idx]
        stop = None

    llm = LLM(model=model, dtype="bfloat16", gpu_memory_utilization=0.90,
              max_model_len=8192, seed=seed)
    sp = SamplingParams(n=k, temperature=temperature, top_p=top_p, max_tokens=1536,
                        seed=seed, stop=stop)
    outs = llm.generate(prompts, sp)

    def base_code(text):
        s = text.strip()
        return s or None

    codes = [[(base_code(o.text) if arch == "base" else _extract_code(o.text))
              for o in outs[j].outputs] for j in range(len(idx))]
    return {"question_ids": [ds[i]["question_id"] for i in idx], "codes": codes,
            "k": k, "difficulty": difficulty, "model": model, "arch": arch,
            "temperature": temperature, "top_p": top_p}


@app.local_entrypoint()
def lcb_r2_smoke(n_problems: int = 8, k: int = 8, difficulty: str = "easy",
                 arch: str = "base", temperature: float = 1.0):
    """Validate the base completion prompt/extraction path on LCB before the full R2
    sweep (pre-registered caveat: 'validate the prompt/extraction path before trusting
    any number'). Prints a sample program, degenerate rate, and pass stats."""
    from collections import Counter
    from pathlib import Path
    gen = lcb_r2_generate.remote(n_problems, k, difficulty, 17, arch, temperature, 1.0)
    Path("runs/modal").mkdir(parents=True, exist_ok=True)
    Path(f"runs/modal/lcb_r2_smoke_{arch}.json").write_text(json.dumps(gen))
    results = lcb_exec.remote(gen["question_ids"], gen["codes"])
    ncodes = sum(len(row) for row in gen["codes"])
    nnull = sum(1 for row in gen["codes"] for c in row if not c or len(c.strip()) < 5)
    passed = sum(r["passed"] for res in results for r in res)
    fracs = [r["frac"] for res in results for r in res if "frac" in r]
    print(f"\n=== LCB R2 smoke: {arch} @ T={temperature}, top_p=1.0 "
          f"({n_problems} problems × k={k}, {difficulty}) ===")
    print(f"candidates {ncodes} | empty/degenerate {nnull} ({nnull/max(1,ncodes):.2f}) | "
          f"passed {passed} ({passed/max(1,ncodes):.2f})")
    if fracs:
        print(f"frac_tests: mean {sum(fracs)/len(fracs):.3f}  "
              f">0 {sum(f>0 for f in fracs)/len(fracs):.2f}  ==1 {sum(f>=1 for f in fracs)/len(fracs):.2f}")
    print("--- sample program (problem 0, candidate 0) ---")
    print((gen["codes"][0][0] or "<none>")[:600])
    print("--- errors ---")
    print(dict(Counter(r["err"] for res in results for r in res)))


@app.local_entrypoint()
def lcb_r2_screen(n_problems: int = 100, k: int = 50, difficulty: str = "easy",
                  arch: str = "base", temperature: float = 1.0):
    """One R2 LCB sweep cell: generate (random stdin problems) → persist pool →
    exec (hardened all-case judge) → score against the gate + persist per-candidate
    detail (enriched pool for D2c/R3). tag = lcb_r2_<arch>_T<temp>."""
    from collections import Counter
    from math import comb
    from pathlib import Path

    def pak(n, c, kk):
        return 1.0 if n - c < kk else 1.0 - comb(n - c, kk) / comb(n, kk)

    # Difficulty enters the tag for non-easy runs so W2's medium pools can never
    # overwrite the landed easy artifacts (which predate this suffix).
    dsuf = "" if difficulty == "easy" else f"_{difficulty}"
    tag = f"lcb_r2_{arch}{dsuf}_T{str(temperature).replace('.', '')}"
    gen = lcb_r2_generate.remote(n_problems, k, difficulty, 17, arch, temperature, 1.0)
    Path("runs/modal").mkdir(parents=True, exist_ok=True)
    Path(f"runs/modal/lcb_cand_{tag}.json").write_text(json.dumps(gen))
    results = lcb_exec.remote(gen["question_ids"], gen["codes"])
    Path(f"runs/modal/lcb_res_{tag}.json").write_text(json.dumps(
        {"tag": tag, "question_ids": gen["question_ids"], "results": results}))

    counts, errs = [], Counter()
    for res in results:
        counts.append((len(res), sum(r["passed"] for r in res)))
        errs.update(r["err"] for r in res)

    def mpak(kk):
        return sum(pak(n, c, kk) for n, c in counts) / len(counts)

    p8, p50 = mpak(8), mpak(min(k, 50))
    in_band, hd = 0.30 <= p8 <= 0.60, (p50 - p8) >= 0.15
    result = {"benchmark": f"LiveCodeBench/code_generation[{difficulty},stdin]"
                           f" [{arch}, T={temperature}, top_p=1.0]",
              "generator": gen["model"], "n_problems": len(counts), "k": k,
              "pass@1": mpak(1), "pass@8": p8, "pass@50": p50, "headroom": p50 - p8,
              "error_breakdown": dict(errs), "band": in_band, "headroom_ok": hd,
              "gate": "PASS" if (in_band and hd) else "does-not-qualify"}
    Path("artifacts").mkdir(exist_ok=True)
    Path(f"artifacts/phase3a_screen_{tag}.json").write_text(json.dumps(result, indent=2))
    print(f"\n=== LCB R2 screen [{difficulty}, stdin] {arch} @ T={temperature}, top_p=1.0 "
          f"({len(counts)} problems, k={k}) ===")
    print(f"pass@1 {result['pass@1']:.3f}  pass@8 {p8:.3f}  pass@50 {p50:.3f}  "
          f"(headroom {p50-p8:+.3f})")
    print(f"coverage band [0.30,0.60]: {in_band}   headroom ≥0.15: {hd}")
    print(f"errors: {dict(errs)}")
    print(f"\nR2 gate ({tag}): {result['gate']}")
    print(f"wrote artifacts/phase3a_screen_{tag}.json")


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


# ---- Phase 3b W4 [PHASE_3B.md W3 freeze — no design decisions live here] ----
# Frozen config: BASE_MODEL fenced-completion, T=0.8, top_p=1.0, seed 17, hardened
# judge, no learned verifier. Prompt wording below is the frozen W3 text.

def _p3b_context(arm, artifact):
    """The frozen per-arm context block. artifact: {code, n_failed, n_tests,
    trace:{stdin, expected, actual}, abstraction}."""
    nf, nt = artifact["n_failed"], artifact["n_tests"]
    code = (artifact.get("code") or "")[:3000]  # context-window guard
    if arm == "B1":
        return None
    if arm == "ANCHOR":
        return (f"A previous attempt:\n```python\n{code}\n```\n"
                f"This attempt failed {nf} of {nt} tests.\n"
                "Write a corrected complete program.")
    if arm == "TRACE":
        t = artifact["trace"]
        return (f"A previous attempt failed {nf} of {nt} tests.\n"
                f"First failing test:\ninput:\n{t['stdin']}\n"
                f"expected output:\n{t['expected']}\nactual output:\n{t['actual']}\n"
                "Write a correct complete program.")
    if arm == "MODELABS":
        return (f"A previous attempt failed {nf} of {nt} tests.\n"
                f"Analysis of the error: {artifact['abstraction']}\n"
                "Write a correct complete program.")
    if arm == "D2C":
        npass = nt - nf
        return (f"A previous attempt:\n```python\n{code}\n```\n"
                f"This attempt passed {npass} of {nt} tests.\n"
                "Improve it so that all tests pass.")
    if arm == "BESTABS":
        t = artifact["trace"]
        return (f"A previous attempt:\n```python\n{code}\n```\n"
                f"This attempt failed {nf} of {nt} tests.\n"
                f"First failing test:\ninput:\n{t['stdin']}\n"
                f"expected output:\n{t['expected']}\nactual output:\n{t['actual']}\n"
                "Write a corrected complete program.")
    raise ValueError(arm)


@app.function(image=EXEC_IMAGE, volumes={"/cache": VOL}, timeout=3600, cpu=8.0,
              memory=16384, env={"HF_HOME": "/cache/hf"})
def lcb_trace_capture(question_ids: list, codes: list, cap_private: int = 12,
                      timeout_s: int = 8) -> list:
    """One artifact per problem → first-failing-case detail (case idx, stdin,
    expected, actual/error), 512-char truncation per W3. Deliberate small
    duplication of lcb_exec's runner — the frozen judge is not touched."""
    import json as _j
    import os
    import signal
    import subprocess
    import sys
    import tempfile
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
            by_id[qid] = [c for c in cases if c.get("testtype") == "stdin"][:3 + cap_private]

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
            outf, errf = Path(d) / "o.txt", Path(d) / "e.txt"
            with open(d + "/in.txt") as fin, open(outf, "wb") as fout, open(errf, "wb") as ferr:
                try:
                    p = subprocess.Popen([sys.executable, "s.py"], stdin=fin, stdout=fout,
                                         stderr=ferr, cwd=d, start_new_session=True)
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
            elines = [l for l in errf.read_text(errors="replace").strip().splitlines() if l.strip()]
        return status, out, (elines[-1][:200] if elines else "")

    def cut(s):
        return s[:512]

    out = []
    for qid, code in zip(question_ids, codes):
        cases = by_id.get(qid, [])
        rec = {"qid": qid, "n_tests": len(cases), "n_failed": 0, "case_idx": None,
               "stdin": "", "expected": "", "actual": "", "err": ""}
        if not code or not cases:
            rec["err"] = "no_code" if not code else "no_tests"
            out.append(rec)
            continue
        first = None
        for i, c in enumerate(cases):
            status, o, exc = run_case(code, c["input"])
            bad = status != "ok" or norm(o) != norm(c["output"])
            if bad:
                rec["n_failed"] += 1
                if first is None:
                    first = (i, c, status, o, exc)
        if first:
            i, c, status, o, exc = first
            actual = (exc or status) if status != "ok" else o
            rec.update({"case_idx": i, "stdin": cut(c["input"]),
                        "expected": cut(c["output"]), "actual": cut(actual),
                        "err": "wrong_answer" if status == "ok" else status})
        out.append(rec)
    return out


@app.function(image=GEN_IMAGE, gpu="L4", volumes={"/cache": VOL}, timeout=7200)
def p3b_generate(items: list, n: int = 50, temperature: float = 0.8,
                 top_p: float = 1.0, seed: int = 17):
    """Frozen-config base-path generation. items: [{qid, context|None}]; the prompt
    is the R2 base fenced-completion scaffold with the frozen context block (if any)
    inserted between problem and invitation."""
    from datasets import load_dataset
    from vllm import LLM, SamplingParams

    ds = load_dataset(DATASET, split="test")
    q = {ds[i]["question_id"]: ds[i]["question_content"] for i in range(len(ds))}

    def prompt(it):
        head = "Problem:\n" + q[it["qid"]].strip()
        if it.get("context"):
            head += "\n\n" + it["context"].rstrip()
        return (head + "\n\nA complete Python 3 program that reads from standard "
                "input and writes the answer to standard output:\n\n```python\n")

    llm = LLM(model=BASE_MODEL, dtype="bfloat16", gpu_memory_utilization=0.90,
              max_model_len=8192, seed=seed)
    sp = SamplingParams(n=n, temperature=temperature, top_p=top_p, max_tokens=1536,
                        seed=seed, stop=["```", "\nProblem:"])
    outs = llm.generate([prompt(it) for it in items], sp)
    return [{"qid": it["qid"], "codes": [(o.text.strip() or None) for o in req.outputs]}
            for it, req in zip(items, outs)]


@app.function(image=GEN_IMAGE, gpu="L4", volumes={"/cache": VOL}, timeout=3600)
def p3b_abstractions(items: list):
    """ABSTRACT-model channel: the instruct sibling compresses the trace. T=0,
    <=160 tokens, code stripped. items: [{qid, code, trace_text}]."""
    import re

    from datasets import load_dataset
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams

    ds = load_dataset(DATASET, split="test")
    q = {ds[i]["question_id"]: ds[i]["question_content"] for i in range(len(ds))}
    tok = AutoTokenizer.from_pretrained(MODEL)

    def prompt(it):
        user = (f"Problem:\n{q[it['qid']][:2000]}\n\nFailed attempt:\n```python\n"
                f"{it['code'][:2000]}\n```\n\nExecution result:\n{it['trace_text'][:800]}\n\n"
                "In 2-4 sentences, state what is wrong with the approach and what a "
                "correct approach must do differently. Do not write code.")
        return tok.apply_chat_template(
            [{"role": "user", "content": user}], add_generation_prompt=True, tokenize=False)

    llm = LLM(model=MODEL, dtype="bfloat16", gpu_memory_utilization=0.90,
              max_model_len=8192, seed=17)
    sp = SamplingParams(n=1, temperature=0.0, max_tokens=160, seed=17)
    outs = llm.generate([prompt(it) for it in items], sp)
    res = []
    for it, req in zip(items, outs):
        txt = re.sub(r"```.*?(```|$)", "", req.outputs[0].text, flags=re.DOTALL).strip()
        res.append({"qid": it["qid"], "abstraction": txt})
    return res


# ---- W4 local helpers (pure CPU, committed-pool plumbing) ----

def _p3b_pool_files(stratum):
    from pathlib import Path
    base = {"medium": "lcb_r2_base_medium_T08", "easy": "lcb_r2_base_T08"}[stratum]
    return (Path(f"runs/modal/lcb_cand_{base}.json"),
            Path(f"runs/modal/lcb_res_{base}.json"))


def _p3b_artifacts(stratum):
    """Frozen artifact rule [W3 §1]: stratum = zero-pass problems of the committed
    pool; artifact = highest-frac candidate (ties → lowest index; None codes skipped)."""
    cand_f, res_f = _p3b_pool_files(stratum)
    cand, res = json.loads(cand_f.read_text()), json.loads(res_f.read_text())
    arts, skipped = [], []
    for qid, crow, rrow in zip(res["question_ids"], cand["codes"], res["results"]):
        if any(r["passed"] for r in rrow):
            continue
        best_i, best_f = None, -1.0
        for i, (c, r) in enumerate(zip(crow, rrow)):
            if c and r["frac"] > best_f:
                best_i, best_f = i, r["frac"]
        if best_i is None:
            skipped.append(qid)
            continue
        r = rrow[best_i]
        arts.append({"qid": qid, "cand_idx": best_i, "code": crow[best_i],
                     "frac": r["frac"], "n_tests": r["n_tests"],
                     "n_failed": r["n_tests"] - r["n_passed"]})
    if skipped:
        print(f"[{stratum}] {len(skipped)} stratum problems had no usable artifact "
              f"(all candidates None): {skipped}")
    return arts


def _p3b_traces(arts, path):
    if path.exists():
        got = {t["qid"]: t for t in json.loads(path.read_text())}
    else:
        tr = lcb_trace_capture.remote([a["qid"] for a in arts], [a["code"] for a in arts])
        path.write_text(json.dumps(tr))
        got = {t["qid"]: t for t in tr}
    for a in arts:
        t = got[a["qid"]]
        a["trace"] = {"stdin": t["stdin"], "expected": t["expected"], "actual": t["actual"]}
        a["err_class"] = t["err"]
    return arts


def _p3b_abstract(arts, path):
    if path.exists():
        got = {t["qid"]: t["abstraction"] for t in json.loads(path.read_text())}
    else:
        items = [{"qid": a["qid"], "code": a["code"],
                  "trace_text": (f"failed {a['n_failed']} of {a['n_tests']} tests; "
                                 f"first failing test: input {a['trace']['stdin'][:300]} "
                                 f"expected {a['trace']['expected'][:200]} "
                                 f"actual {a['trace']['actual'][:200]}")} for a in arts]
        res = p3b_abstractions.remote(items)
        path.write_text(json.dumps(res))
        got = {t["qid"]: t["abstraction"] for t in res}
    for a in arts:
        a["abstraction"] = got[a["qid"]]
    return arts


def _pull(gen_code, art_code):
    import difflib
    return 1.0 - difflib.SequenceMatcher(None, gen_code, art_code).ratio()


def _mcnemar_one_sided(b, c):
    from math import comb
    m = b + c
    return 1.0 if m == 0 else sum(comb(m, k) for k in range(b, m + 1)) / 2 ** m


def _wilcoxon_mc_one_sided(diffs, trials=20000, seed=17):
    """One-sided paired location test via seeded sign-flip Monte Carlo on the mean."""
    import random
    rnd = random.Random(seed)
    obs = sum(diffs) / len(diffs)
    ge = sum(1 for _ in range(trials)
             if sum(d if rnd.random() < 0.5 else -d for d in diffs) / len(diffs) >= obs)
    return (ge + 1) / (trials + 1)


_R3_ARMS = ("B1", "ANCHOR", "TRACE", "MODELABS")


@app.local_entrypoint()
def p3b_r3_smoke():
    """W3 smoke gate: 8 medium-stratum problems × 4 arms × 8 draws.
    Gate: well-formed ≥ 85% (non-None), degenerate ≤ 10% (non-None under 20 chars)."""
    from pathlib import Path

    arts = _p3b_artifacts("medium")
    arts = _p3b_traces(arts, Path("runs/modal/r3_traces_medium.json"))
    arts = _p3b_abstract(arts, Path("runs/modal/r3_abs_medium.json"))
    sm = arts[:8]
    stats = {}
    for arm in _R3_ARMS:
        items = [{"qid": a["qid"], "context": _p3b_context(arm, a)} for a in sm]
        gen = p3b_generate.remote(items, 8)
        codes = [c for g in gen for c in g["codes"]]
        nn = [c for c in codes if c]
        wf = len(nn) / len(codes)
        dg = (sum(1 for c in nn if len(c) < 20) / len(nn)) if nn else 1.0
        stats[arm] = {"well_formed": wf, "degenerate": dg}
        print(f"{arm}: well_formed {wf:.3f} degenerate {dg:.3f}")
    ok = all(v["well_formed"] >= 0.85 and v["degenerate"] <= 0.10 for v in stats.values())
    out = {"_label": "R3 smoke gate [PHASE_3B W3 §1]", "n_problems": len(sm),
           "per_arm": stats, "gate": "PASS" if ok else "FAIL"}
    Path("artifacts/r3_smoke.json").write_text(json.dumps(out, indent=2))
    print(f"R3 SMOKE GATE: {out['gate']}")
    print("wrote artifacts/r3_smoke.json")


@app.local_entrypoint()
def p3b_r3(stratum: str = "medium"):
    """W4/R3 — four-arm conditional reachability on the frozen stratum [W3 §1].
    Every stage persists before the next (outage insurance)."""
    from pathlib import Path

    arts = _p3b_artifacts(stratum)
    arts = _p3b_traces(arts, Path(f"runs/modal/r3_traces_{stratum}.json"))
    arts = _p3b_abstract(arts, Path(f"runs/modal/r3_abs_{stratum}.json"))
    art_by_qid = {a["qid"]: a for a in arts}
    print(f"[{stratum}] {len(arts)} stratum problems with artifacts")

    data = {}
    for arm in _R3_ARMS:
        cf = Path(f"runs/modal/r3_cand_{stratum}_{arm}.json")
        rf = Path(f"runs/modal/r3_res_{stratum}_{arm}.json")
        if not cf.exists():
            items = [{"qid": a["qid"], "context": _p3b_context(arm, a)} for a in arts]
            cf.write_text(json.dumps(p3b_generate.remote(items, 50)))
            print(f"[{arm}] generated", flush=True)
        gen = json.loads(cf.read_text())
        if not rf.exists():
            results = lcb_exec.remote([g["qid"] for g in gen], [g["codes"] for g in gen])
            rf.write_text(json.dumps({"question_ids": [g["qid"] for g in gen],
                                      "results": results}))
            print(f"[{arm}] judged", flush=True)
        data[arm] = (gen, json.loads(rf.read_text())["results"])

    qids = [a["qid"] for a in arts]
    rec, pull_mean, rec_detail = {}, {}, []
    for arm in _R3_ARMS:
        gen, results = data[arm]
        r, pl = {}, []
        for g, row in zip(gen, results):
            r[g["qid"]] = any(x["passed"] for x in row)
            a = art_by_qid[g["qid"]]
            pl.extend(_pull(c, a["code"]) for c in g["codes"] if c)
            if r[g["qid"]]:
                win = next(i for i, x in enumerate(row) if x["passed"])
                rec_detail.append({"arm": arm, "qid": g["qid"], "cand_idx": win,
                                   "err_class_of_artifact": a["err_class"]})
        rec[arm] = r
        pull_mean[arm] = sum(pl) / len(pl) if pl else None

    def contrast(a1, a2):
        b = sum(1 for q_ in qids if rec[a1][q_] and not rec[a2][q_])
        c = sum(1 for q_ in qids if rec[a2][q_] and not rec[a1][q_])
        return {f"only_{a1}": b, f"only_{a2}": c, "one_sided_p": _mcnemar_one_sided(b, c)}

    counts = {arm: sum(rec[arm].values()) for arm in _R3_ARMS}
    primary = contrast("TRACE", "B1")
    secondary = {"MODELABS_vs_TRACE": contrast("MODELABS", "TRACE"),
                 "ANCHOR_vs_B1": contrast("ANCHOR", "B1"),
                 "MODELABS_vs_B1": contrast("MODELABS", "B1")}
    sig = primary["one_sided_p"] < 0.05 and counts["TRACE"] > counts["B1"]
    positive = counts["TRACE"] > counts["B1"]
    verdict = ("DIRECTED-ESCAPE SIGNAL (significant at alpha=0.05)" if sig else
               "POSITIVE-BUT-UNRESOLVABLE (pre-declared band)" if positive else
               "NULL - forecloses r>=0.15; r in [0.05,0.13) pre-declared unresolvable")

    from pathlib import Path as _P
    out_f = _P("artifacts/r3_conditional_reachability.json")
    merged = json.loads(out_f.read_text()) if out_f.exists() else {
        "_label": "R3 — conditional reachability, four arms [PHASE_3B W3 §1]"}
    merged[stratum] = {
        "n_stratum": len(arts), "recoveries": counts, "pull_mean_by_arm": pull_mean,
        "primary_TRACE_vs_B1": primary, "secondary": secondary,
        "recovery_detail": rec_detail, "verdict": verdict,
        "null_floor_note": "expected lucky B1-50 recoveries ~2.0 (medium) / ~3.6 (easy) [W0c/W2]"}
    out_f.write_text(json.dumps(merged, indent=2))

    print(f"\n=== R3 [{stratum}] — recoveries out of {len(arts)} ===")
    for arm in _R3_ARMS:
        print(f"  {arm:<9} {counts[arm]:>3}   mean PULL {pull_mean[arm]:.3f}")
    print(f"primary TRACE vs B1: {primary}")
    for k, v in secondary.items():
        print(f"secondary {k}: {v}")
    print(f"R3 VERDICT [{stratum}]: {verdict}")
    print("wrote artifacts/r3_conditional_reachability.json")


@app.local_entrypoint()
def p3b_d2c():
    """W4/D2c — partial-credit conditioning vs the W0b copy-null and iid-null [W3 §2]."""
    from pathlib import Path

    w0b = json.loads(Path("artifacts/w0b_copy_null.json").read_text())
    cand = json.loads(Path("runs/modal/lcb_cand_lcb_r2_base_T08.json").read_text())
    res = json.loads(Path("runs/modal/lcb_res_lcb_r2_base_T08.json").read_text())
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
                             "n_failed": row["n_tests"] - row["n_passed"],
                             "iid_null": v["iid_null_pool_mean_frac"]})
                break
    print(f"D2c artifacts: {len(arts)} (frozen set: 44)")

    cf, rf = Path("runs/modal/d2c_cand.json"), Path("runs/modal/d2c_res.json")
    if not cf.exists():
        items = [{"qid": a["qid"], "context": _p3b_context("D2C", a)} for a in arts]
        cf.write_text(json.dumps(p3b_generate.remote(items, 8)))
    gen = json.loads(cf.read_text())
    if not rf.exists():
        rf.write_text(json.dumps({"results": lcb_exec.remote(
            [g["qid"] for g in gen], [g["codes"] for g in gen])}))
    results = json.loads(rf.read_text())["results"]

    mean_gen, d_copy, d_iid, sims = [], [], [], []
    for a, g, row in zip(arts, gen, results):
        mg = sum(r["frac"] for r in row) / len(row)
        mean_gen.append(mg)
        d_copy.append(mg - a["frac"])
        d_iid.append(mg - a["iid_null"])
        sims.extend(1.0 - _pull(c, a["code"]) for c in g["codes"] if c)
    p_copy = _wilcoxon_mc_one_sided(d_copy)
    p_iid = _wilcoxon_mc_one_sided(d_iid)
    p_sink = _wilcoxon_mc_one_sided([-d for d in d_copy])
    verdict = ("CLIMB" if (p_copy < 0.05 and p_iid < 0.05) else
               "SINK" if p_sink < 0.05 else "FLAT")
    n = len(arts)
    out = {"_label": "D2c/E6 — partial-credit conditioning [PHASE_3B W3 §2]",
           "n_artifacts": n,
           "mean_frac_generated": sum(mean_gen) / n,
           "mean_copy_null": sum(a["frac"] for a in arts) / n,
           "mean_iid_null": sum(a["iid_null"] for a in arts) / n,
           "delta_vs_copy_null": sum(d_copy) / n, "p_one_sided_vs_copy_null": p_copy,
           "delta_vs_iid_null": sum(d_iid) / n, "p_one_sided_vs_iid_null": p_iid,
           "p_one_sided_sink": p_sink,
           "copy_fidelity_mean_similarity": sum(sims) / len(sims),
           "verdict": verdict}
    Path("artifacts/dmeasure_d2c_partial_credit.json").write_text(json.dumps(out, indent=2))
    print(f"\n=== D2c/E6 ({n} artifacts) ===")
    print(f"mean frac(gen) {out['mean_frac_generated']:.3f}  copy-null "
          f"{out['mean_copy_null']:.3f}  iid-null {out['mean_iid_null']:.3f}")
    print(f"vs copy-null: delta {out['delta_vs_copy_null']:+.3f} p {p_copy:.4f}   "
          f"vs iid-null: delta {out['delta_vs_iid_null']:+.3f} p {p_iid:.4f}   "
          f"sink p {p_sink:.4f}")
    print(f"copy fidelity (similarity to artifact): {out['copy_fidelity_mean_similarity']:.3f}")
    print(f"D2C VERDICT: {verdict}")
    print("wrote artifacts/dmeasure_d2c_partial_credit.json")


@app.local_entrypoint()
def p3b_bsf():
    """W4/BEST-SO-FAR — five conditions on the refinement-regime problems [W3 §3]."""
    from pathlib import Path

    cand = json.loads(Path("runs/modal/lcb_cand_lcb_r2_base_T08.json").read_text())
    res = json.loads(Path("runs/modal/lcb_res_lcb_r2_base_T08.json").read_text())
    probs = []
    for qid, crow, rrow in zip(res["question_ids"], cand["codes"], res["results"]):
        c8, r8 = crow[:8], rrow[:8]
        if any(r["passed"] for r in r8):
            continue
        if not any(0.0 < r["frac"] < 1.0 for r in r8):
            continue
        bi, bf = None, -1.0
        for i, (c, r) in enumerate(zip(c8, r8)):
            if c and r["frac"] > bf:
                bi, bf = i, r["frac"]
        li = next((i for i in range(7, -1, -1) if c8[i]), None)
        if bi is None or li is None:
            continue
        probs.append({"qid": qid,
                      "best": {"qid": qid, "code": c8[bi], "frac": r8[bi]["frac"],
                               "n_tests": r8[bi]["n_tests"],
                               "n_failed": r8[bi]["n_tests"] - r8[bi]["n_passed"]},
                      "last": {"qid": qid, "code": c8[li], "frac": r8[li]["frac"],
                               "n_tests": r8[li]["n_tests"],
                               "n_failed": r8[li]["n_tests"] - r8[li]["n_passed"]}})
    print(f"BEST-SO-FAR problems: {len(probs)} (frozen set: 30)")

    best_arts = [p["best"] for p in probs]
    _p3b_traces(best_arts, Path("runs/modal/bsf_traces.json"))
    conds = ("B1", "LAST", "BEST", "ABSTRACT", "BESTABS")

    def context(cond, p):
        if cond == "B1":
            return None
        if cond == "LAST":
            return _p3b_context("ANCHOR", p["last"])
        if cond == "BEST":
            return _p3b_context("ANCHOR", p["best"])
        if cond == "ABSTRACT":
            return _p3b_context("TRACE", p["best"])
        if cond == "BESTABS":
            return _p3b_context("BESTABS", p["best"])

    cf, rf = Path("runs/modal/bsf_cand.json"), Path("runs/modal/bsf_res.json")
    order = [(cond, p) for cond in conds for p in probs]
    if not cf.exists():
        items = [{"qid": p["qid"], "context": context(cond, p)} for cond, p in order]
        cf.write_text(json.dumps(p3b_generate.remote(items, 8)))
    gen = json.loads(cf.read_text())
    if not rf.exists():
        rf.write_text(json.dumps({"results": lcb_exec.remote(
            [g["qid"] for g in gen], [g["codes"] for g in gen])}))
    results = json.loads(rf.read_text())["results"]

    cov, frac = {c: {} for c in conds}, {c: [] for c in conds}
    for (cond, p), g, row in zip(order, gen, results):
        cov[cond][p["qid"]] = any(r["passed"] for r in row)
        frac[cond].append(sum(r["frac"] for r in row) / len(row))
    qids = [p["qid"] for p in probs]

    def vs_b1(cond):
        b = sum(1 for q_ in qids if cov[cond][q_] and not cov["B1"][q_])
        c = sum(1 for q_ in qids if cov["B1"][q_] and not cov[cond][q_])
        return {f"only_{cond}": b, "only_B1": c, "one_sided_p": _mcnemar_one_sided(b, c)}

    summary = {c: {"coverage": sum(cov[c].values()) / len(qids),
                   "mean_frac": sum(frac[c]) / len(frac[c]),
                   "vs_B1": (vs_b1(c) if c != "B1" else None)} for c in conds}
    out = {"_label": "BEST-SO-FAR — five conditions [PHASE_3B W3 §3]",
           "n_problems": len(probs), "conditions": summary}
    Path("artifacts/bestsofar.json").write_text(json.dumps(out, indent=2))
    print(f"\n=== BEST-SO-FAR ({len(probs)} problems, 8 draws/condition) ===")
    for c in conds:
        s = summary[c]
        extra = f"  vs B1 {s['vs_B1']}" if s["vs_B1"] else ""
        print(f"  {c:<9} coverage {s['coverage']:.3f}  mean_frac {s['mean_frac']:.3f}{extra}")
    print("wrote artifacts/bestsofar.json")
