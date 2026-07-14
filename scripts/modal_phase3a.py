#!/usr/bin/env python3
"""Phase 3a — benchmark screen (GATE). Pre-registered in docs/PHASE_3.md §4.1.

Part A (this file, `characterize`): feedback richness (criterion 2) — load candidate
benchmarks, report n_problems, tests-per-problem, and execution paradigm. Pure
dataset property, no generation.

Part B (later): coverage k=50 (criterion 1) on the feedback-rich tractable candidate.

Usage:  modal run scripts/modal_phase3a.py::characterize
"""
from __future__ import annotations

import json

import modal

IMAGE = modal.Image.debian_slim(python_version="3.12").pip_install(
    "datasets==5.0.0", "huggingface_hub==1.11.0")
VOL = modal.Volume.from_name("rgr-hf-cache", create_if_missing=True)
app = modal.App("rgr-phase3a")


@app.function(image=IMAGE, volumes={"/cache": VOL}, timeout=3600,
              env={"HF_HOME": "/cache/hf"})
def characterize() -> dict:
    """Load each candidate benchmark; report columns, n, a tests-per-problem proxy,
    and paradigm. Robust per-benchmark (one failure doesn't sink the rest)."""
    import statistics

    from datasets import load_dataset

    out = {}

    def rec(name, note="", **kw):
        out[name] = {"note": note, **kw}
        print(f"\n### {name} — {note}")
        for k, v in kw.items():
            print(f"  {k}: {v}")

    # ---- BigCodeBench (function-call, unittest) ----
    try:
        ds = load_dataset("bigcode/bigcodebench", split="v0.1.4")
        cols = ds.column_names
        n = len(ds)
        # test methods per problem = count of 'def test' in the unittest `test` field
        tm = [ds[i]["test"].count("def test") for i in range(min(n, 400))]
        libs = set()
        for i in range(min(n, 200)):
            try:
                libs |= set(json.loads(ds[i]["libs"])) if isinstance(ds[i]["libs"], str) else set(ds[i]["libs"])
            except Exception:
                pass
        rec("BigCodeBench", "function-call / unittest", columns=cols, n=n,
            test_methods_median=statistics.median(tm), test_methods_mean=round(statistics.mean(tm), 1),
            distinct_libs_sampled=len(libs))
    except Exception as e:
        rec("BigCodeBench", f"LOAD FAILED: {e!r}")

    # ---- EvalPlus MBPP+ (function-call, assert) ----
    for hf, label in [("evalplus/mbppplus", "MBPP+"), ("evalplus/humanevalplus", "HumanEval+")]:
        try:
            ds = load_dataset(hf, split="test")
            cols = ds.column_names
            n = len(ds)
            key = "test" if "test" in cols else ("assertion" if "assertion" in cols else cols[-1])
            asserts = [str(ds[i].get(key, "")).count("assert") for i in range(min(n, 400))]
            rec(f"EvalPlus {label}", "function-call / assert (augmented tests)",
                columns=cols, n=n, assert_field=key,
                asserts_median=statistics.median(asserts), asserts_mean=round(statistics.mean(asserts), 1))
        except Exception as e:
            rec(f"EvalPlus {label}", f"LOAD FAILED: {e!r}")

    # ---- APPS (stdin/stdout, I/O cases) ----
    try:
        ds = load_dataset("codeparrot/apps", split="test", trust_remote_code=True)
        n = len(ds)
        ios = []
        for i in range(0, min(n, 600), 3):
            try:
                io = json.loads(ds[i]["input_output"]) if ds[i]["input_output"] else {}
                ios.append(len(io.get("inputs", [])))
            except Exception:
                pass
        rec("APPS", "stdin/stdout / I-O pairs", columns=ds.column_names, n=n,
            io_cases_median=statistics.median(ios) if ios else 0,
            io_cases_mean=round(statistics.mean(ios), 1) if ios else 0)
    except Exception as e:
        rec("APPS", f"LOAD FAILED: {e!r}")

    return out


@app.function(image=IMAGE, volumes={"/cache": VOL}, timeout=1800,
              env={"HF_HOME": "/cache/hf"})
def bcb_libs() -> dict:
    """Library frequency across BigCodeBench — sizes the execution image."""
    from collections import Counter

    from datasets import load_dataset
    ds = load_dataset("bigcode/bigcodebench", split="v0.1.4")
    c = Counter()
    for i in range(len(ds)):
        libs = ds[i]["libs"]
        try:
            libs = json.loads(libs) if isinstance(libs, str) else libs
        except Exception:
            libs = []
        c.update(libs)
    return {"n_problems": len(ds), "distinct_libs": len(c),
            "top40": c.most_common(40)}


@app.local_entrypoint()
def libs_main():
    r = bcb_libs.remote()
    print(f"BigCodeBench: {r['n_problems']} problems, {r['distinct_libs']} distinct libs")
    print("top 40 libs (name, #problems):")
    for name, cnt in r["top40"]:
        print(f"  {name:<22} {cnt}")


# ---- Part B: coverage screen (criterion 1) on BigCodeBench ----

MODEL = "Qwen/Qwen2.5-Coder-1.5B-Instruct"
GEN_IMAGE = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("vllm==0.11.0", "transformers==4.57.0", "datasets==5.0.0")
    .env({"HF_HOME": "/cache/hf", "TOKENIZERS_PARALLELISM": "false",
          "VLLM_LOGGING_LEVEL": "WARNING"})
)
# Broad scientific/web stack — covers the bulk of BigCodeBench; import-failure rate
# measured and reported so the coverage estimate is honest.
EXEC_IMAGE = modal.Image.debian_slim(python_version="3.12").pip_install(
    "datasets==5.0.0", "numpy", "pandas", "scipy", "scikit-learn", "matplotlib",
    "seaborn", "requests", "beautifulsoup4", "lxml", "nltk", "sympy", "pillow",
    "flask", "statsmodels", "openpyxl", "python-dateutil", "pytz", "regex",
    "faker", "cryptography", "networkx", "sqlalchemy", "pyyaml", "wordcloud",
    "textblob", "gensim", "folium", "geopy", "django", "psutil",
).env({"HF_HOME": "/cache/hf", "MPLBACKEND": "Agg"})

_FENCE = None


def _extract_code(text):
    import re
    global _FENCE
    if _FENCE is None:
        _FENCE = re.compile(r"```(?:python|py)?\s*\n(.*?)```", re.DOTALL)
    m = _FENCE.search(text)
    if m:
        return m.group(1).strip() or None
    s = text.strip()
    return s if __import__("re").match(r"^(def |import |from |class )", s) else None


@app.function(image=GEN_IMAGE, gpu="L4", volumes={"/cache": VOL}, timeout=7200)
def bcb_generate(n_problems: int = 60, k: int = 50, seed: int = 17,
                 dataset: str = "bigcode/bigcodebench", model: str = MODEL):
    """Generate k i.i.d. samples per BigCodeBench-instruct problem (vLLM bf16)."""
    from datasets import load_dataset
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams

    ds = load_dataset(dataset, split="v0.1.4")
    idx = list(range(min(n_problems, len(ds))))
    tok = AutoTokenizer.from_pretrained(model)
    SYS = ("You are a Python programming assistant. Answer with a single fenced "
           "Python code block containing a complete solution, and nothing else.")

    def prompt(i):
        return tok.apply_chat_template(
            [{"role": "system", "content": SYS},
             {"role": "user", "content": ds[i]["instruct_prompt"]}],
            add_generation_prompt=True, tokenize=False)

    prompts = [prompt(i) for i in idx]
    llm = LLM(model=model, dtype="bfloat16", gpu_memory_utilization=0.90,
              max_model_len=4096, seed=seed)
    sp = SamplingParams(n=k, temperature=0.8, top_p=0.95, max_tokens=1024, seed=seed)
    outs = llm.generate(prompts, sp)

    problems = []
    for j, i in enumerate(idx):
        codes = [_extract_code(o.text) for o in outs[j].outputs]
        problems.append({"task_id": ds[i]["task_id"], "test": ds[i]["test"],
                         "entry_point": ds[i]["entry_point"], "codes": codes})
    return {"problems": problems, "k": k}


@app.function(image=EXEC_IMAGE, timeout=7200, cpu=16.0)
def bcb_exec(problems: list, timeout_s: int = 12) -> list:
    """Execute each candidate's code+unittest; return per-candidate pass + frac +
    error class (import failures counted separately to gauge env coverage)."""
    import subprocess
    import sys
    import tempfile
    from concurrent.futures import ThreadPoolExecutor
    from pathlib import Path

    RUNNER = ("\n\nimport unittest as _ut\n"
              "_r = _ut.main(argv=[''], exit=False, verbosity=0).result\n"
              "print('BCBRESULT', _r.testsRun, len(_r.failures), len(_r.errors))\n")

    def run_one(args):
        code, test = args
        if code is None:
            return {"passed": False, "frac": 0.0, "err": "no_code"}
        src = code + "\n\n" + test + RUNNER
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "cand.py"
            p.write_text(src)
            try:
                r = subprocess.run([sys.executable, str(p)], capture_output=True,
                                   text=True, timeout=timeout_s, cwd=d)
            except subprocess.TimeoutExpired:
                return {"passed": False, "frac": 0.0, "err": "timeout"}
        out = r.stdout + "\n" + r.stderr
        line = next((l for l in out.splitlines() if l.startswith("BCBRESULT")), None)
        if line:
            _, n, f, e = line.split()
            n, f, e = int(n), int(f), int(e)
            ok = n > 0 and f == 0 and e == 0
            return {"passed": ok, "frac": (n - f - e) / n if n else 0.0, "err": "" if ok else "wrong_answer"}
        err = ("import" if "ModuleNotFoundError" in out or "ImportError" in out
               else "syntax" if "SyntaxError" in out else "runtime")
        return {"passed": False, "frac": 0.0, "err": err}

    results = []
    with ThreadPoolExecutor(max_workers=16) as tp:
        for prob in problems:
            res = list(tp.map(run_one, [(c, prob["test"]) for c in prob["codes"]]))
            results.append(res)
    return results


@app.local_entrypoint()
def screen_main(n_problems: int = 60, k: int = 50, dataset: str = "bigcode/bigcodebench", model: str = MODEL):
    from collections import Counter
    from math import comb
    from pathlib import Path

    def pass_at_k(n, c, kk):
        return 1.0 if n - c < kk else 1.0 - comb(n - c, kk) / comb(n, kk)

    gen = bcb_generate.remote(n_problems, k, 17, dataset, model)
    problems = gen["problems"]
    results = bcb_exec.remote(problems)

    counts, errs = [], Counter()
    for res in results:
        c = sum(r["passed"] for r in res)
        counts.append((len(res), c))
        errs.update(r["err"] for r in res)
    import_rate = errs.get("import", 0) / sum(errs.values())

    def mean_pak(kk):
        return sum(pass_at_k(n, c, kk) for n, c in counts) / len(counts)

    p8, p50 = mean_pak(8), mean_pak(min(k, 50))
    in_band = 0.30 <= p8 <= 0.60
    headroom = (p50 - p8) >= 0.15
    result = {"benchmark": dataset, "generator": model, "n_problems": len(counts), "k": k,
              "pass@1": mean_pak(1), "pass@8": p8, "pass@50": p50,
              "pass50_minus_pass8": p50 - p8, "import_failure_rate": import_rate,
              "error_breakdown": dict(errs),
              "criterion1_coverage_band[0.30,0.60]": in_band,
              "criterion1_headroom>=0.15": headroom,
              "criterion2_feedback_rich": True,  # ~5 unittest methods (Part A)
              "gate": "PASS" if (in_band and headroom) else "does-not-qualify"}
    Path("artifacts/phase3a_screen.json").write_text(json.dumps(result, indent=2))
    print(f"\n=== Phase 3a — coverage screen: {dataset} ({len(counts)} problems, k={k}) ===")
    print(f"pass@1 {result['pass@1']:.3f}  pass@8 {p8:.3f}  pass@50 {p50:.3f}  "
          f"(pass@50−pass@8 = {p50-p8:+.3f})")
    print(f"coverage band [0.30,0.60]: {in_band}   headroom ≥0.15: {headroom}")
    print(f"import-failure rate (env coverage): {import_rate:.3f}   errors: {dict(errs)}")
    print(f"\n3a gate (BigCodeBench): {result['gate']}")
    print("wrote artifacts/phase3a_screen.json")


@app.local_entrypoint()
def char_main():
    from pathlib import Path
    r = characterize.remote()
    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/phase3a_characterization.json").write_text(json.dumps(r, indent=2))
    print("\n=== Phase 3a — feedback-richness screen (criterion 2: ≫3 tests/problem) ===")
    for name, d in r.items():
        if "LOAD FAILED" in d.get("note", ""):
            print(f"  {name:<20} {d['note']}")
            continue
        rich = (d.get("test_methods_median") or d.get("asserts_median") or d.get("io_cases_median") or 0)
        verdict = "PASS ≫3" if rich > 3 else "FAIL (≤3)"
        print(f"  {name:<20} n={d.get('n'):<5} tests/problem≈{rich:<5} {d.get('note','')[:28]:<30} {verdict}")
    print("wrote artifacts/phase3a_characterization.json")
