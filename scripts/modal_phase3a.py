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
                 dataset: str = "bigcode/bigcodebench", model: str = MODEL,
                 shuffle: bool = False):
    """Generate k i.i.d. samples per BigCodeBench-instruct problem (vLLM bf16)."""
    import random as _rnd
    from datasets import load_dataset
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams

    ds = load_dataset(dataset, split="v0.1.4")
    order = list(range(len(ds)))
    if shuffle:
        _rnd.Random(seed).shuffle(order)
    idx = order[:min(n_problems, len(ds))]
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


BASE_MODEL = "Qwen/Qwen2.5-Coder-1.5B"  # completion model — deeper pass@k tail (R2)
# truncate a base-model completion at the first top-level construct after the body
_BASE_STOP = ["\ndef ", "\nclass ", "\nif __name__", "\n@", "\nprint(",
              "\nassert ", "\n# Test", "\n```", "\nExample"]


@app.function(image=GEN_IMAGE, gpu="L4", volumes={"/cache": VOL}, timeout=7200)
def r2_generate(n_problems: int = 200, k: int = 50, seed: int = 17,
                dataset: str = "bigcode/bigcodebench", arch: str = "base",
                temperature: float = 1.0, top_p: float = 1.0):
    """R2 tail-un-suppression sweep [PHASE_3R.md R2]. Random samples only (D15).
    arch='base' → completion model on `complete_prompt` (code = prompt+continuation,
    truncated at the next top-level construct); arch='instruct' → chat on
    `instruct_prompt` (fenced extraction). top_p/temperature swept to lift the tail
    nucleus/Instruct-collapse suppress. Returns the same shape bcb_exec consumes."""
    import random as _rnd
    from datasets import load_dataset
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams

    ds = load_dataset(dataset, split="v0.1.4")
    order = list(range(len(ds)))
    _rnd.Random(seed).shuffle(order)              # random-sample only
    idx = order[:min(n_problems, len(ds))]
    model = BASE_MODEL if arch == "base" else MODEL
    tok = AutoTokenizer.from_pretrained(model)
    SYS = ("You are a Python programming assistant. Answer with a single fenced "
           "Python code block containing a complete solution, and nothing else.")

    if arch == "base":
        prompts = [ds[i]["complete_prompt"] for i in idx]
        stop = _BASE_STOP
    else:
        prompts = [tok.apply_chat_template(
            [{"role": "system", "content": SYS},
             {"role": "user", "content": ds[i]["instruct_prompt"]}],
            add_generation_prompt=True, tokenize=False) for i in idx]
        stop = None

    llm = LLM(model=model, dtype="bfloat16", gpu_memory_utilization=0.90,
              max_model_len=4096, seed=seed)
    sp = SamplingParams(n=k, temperature=temperature, top_p=top_p, max_tokens=1024,
                        seed=seed, stop=stop)
    outs = llm.generate(prompts, sp)

    problems = []
    for j, i in enumerate(idx):
        if arch == "base":
            # code = signature/docstring prompt + generated body (a full module)
            codes = [ds[i]["complete_prompt"] + o.text for o in outs[j].outputs]
        else:
            codes = [_extract_code(o.text) for o in outs[j].outputs]
        problems.append({"task_id": ds[i]["task_id"], "test": ds[i]["test"],
                         "entry_point": ds[i]["entry_point"], "codes": codes})
    return {"problems": problems, "k": k, "arch": arch,
            "temperature": temperature, "top_p": top_p}


@app.function(image=EXEC_IMAGE, timeout=7200, cpu=32.0, memory=65536)
def bcb_exec(problems: list, timeout_s: int = 10, max_workers: int = 16) -> list:
    """Execute each candidate's code+unittest, HARDENED so a single candidate can
    never wedge the pool:
      • own session (start_new_session) → the whole process group is killable;
      • stdout/stderr → a FILE, never a PIPE → no grandchild-holds-the-pipe deadlock
        (the exact bug that stuck the earlier runs);
      • on timeout, os.killpg(SIGKILL) reaps the candidate AND any children it spawned;
      • a per-process rlimit preamble bounds CPU seconds (infinite loops die fast),
        memory (2 GB), and socket timeout (network tests fail fast).
    Returns per-candidate pass + frac + error class."""
    import os
    import signal
    import subprocess
    import sys
    import tempfile
    from concurrent.futures import ThreadPoolExecutor
    from pathlib import Path

    PREAMBLE = (
        "import resource as _rs, socket as _sk\n"
        "try:\n"
        f"    _rs.setrlimit(_rs.RLIMIT_CPU, ({timeout_s}, {timeout_s}))\n"
        "    _rs.setrlimit(_rs.RLIMIT_AS, (2*1024**3, 2*1024**3))\n"
        "except Exception: pass\n"
        "_sk.setdefaulttimeout(4)\n\n"
    )
    # Emit per-test detail (failing method names + first exception) so the pool can
    # serve R3/BEST-SO-FAR, not just pass/fail. [PHASE_3R Addendum II §1]
    RUNNER = ("\n\nimport unittest as _ut, json as _json\n"
              "_r = _ut.main(argv=[''], exit=False, verbosity=0).result\n"
              "_fe = list(_r.failures) + list(_r.errors)\n"
              "_fail = [str(t).split()[0] for t, _tb in _fe]\n"
              "_exc = ''\n"
              "if _fe:\n"
              "    _ls = [l for l in _fe[0][1].strip().splitlines() if l.strip()]\n"
              "    _exc = _ls[-1][:200] if _ls else ''\n"
              "print('BCBRESULT', _json.dumps({'n': _r.testsRun, 'f': len(_r.failures),"
              " 'e': len(_r.errors), 'fail': _fail, 'exc': _exc}))\n")

    def run_one(args):
        code, test = args
        if code is None:
            return {"passed": False, "frac": 0.0, "err": "no_code"}
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "cand.py").write_text(PREAMBLE + code + "\n\n" + test + RUNNER)
            outf = Path(d) / "o.txt"
            timed_out = False
            with open(outf, "wb") as fh:
                try:
                    proc = subprocess.Popen([sys.executable, "cand.py"], stdout=fh,
                                            stderr=subprocess.STDOUT, cwd=d,
                                            start_new_session=True)
                except Exception:
                    return {"passed": False, "frac": 0.0, "err": "spawn"}
                try:
                    proc.wait(timeout=timeout_s)
                except subprocess.TimeoutExpired:
                    timed_out = True
                # reap the whole session (candidate + any grandchildren) unconditionally
                try:
                    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                except (ProcessLookupError, PermissionError):
                    pass
                try:
                    proc.wait(timeout=5)
                except Exception:
                    pass
            # a candidate can delete/clobber its own cwd (base-model garbage does);
            # a missing/unreadable output file is a failure, never a batch-abort
            try:
                out = outf.read_text(errors="replace")
            except OSError:
                out = ""
        if timed_out:
            return {"passed": False, "frac": 0.0, "n_tests": 0, "n_passed": 0,
                    "failing": [], "exc": "", "err": "timeout"}
        line = next((l for l in out.splitlines() if l.startswith("BCBRESULT")), None)
        if line:
            d = json.loads(line[len("BCBRESULT"):].strip())
            n, f, e = d["n"], d["f"], d["e"]
            ok = n > 0 and f == 0 and e == 0
            return {"passed": ok, "n_tests": n, "n_passed": n - f - e,
                    "frac": (n - f - e) / n if n else 0.0, "failing": d.get("fail", []),
                    "exc": d.get("exc", ""), "err": "" if ok else "wrong_answer"}
        err = ("import" if ("ModuleNotFoundError" in out or "ImportError" in out)
               else "syntax" if "SyntaxError" in out else "runtime")
        return {"passed": False, "frac": 0.0, "n_tests": 0, "n_passed": 0,
                "failing": [], "exc": "", "err": err}

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as tp:
        for prob in problems:
            results.append(list(tp.map(run_one, [(c, prob["test"]) for c in prob["codes"]])))
    return results


def _finalize(problems: list, results: list, dataset: str, model: str, k: int, tag: str):
    """Score pass@k from execution results, write the artifact, print the verdict."""
    from collections import Counter
    from math import comb
    from pathlib import Path

    def pass_at_k(n, c, kk):
        return 1.0 if n - c < kk else 1.0 - comb(n - c, kk) / comb(n, kk)

    counts, errs = [], Counter()
    for res in results:
        counts.append((len(res), sum(r["passed"] for r in res)))
        errs.update(r["err"] for r in res)
    import_rate = errs.get("import", 0) / max(1, sum(errs.values()))

    def mean_pak(kk):
        return sum(pass_at_k(n, c, kk) for n, c in counts) / len(counts)

    p8, p50 = mean_pak(8), mean_pak(min(k, 50))
    in_band, headroom = 0.30 <= p8 <= 0.60, (p50 - p8) >= 0.15
    result = {"benchmark": dataset, "generator": model, "n_problems": len(counts), "k": k,
              "pass@1": mean_pak(1), "pass@8": p8, "pass@50": p50,
              "pass50_minus_pass8": p50 - p8, "import_failure_rate": import_rate,
              "error_breakdown": dict(errs),
              "criterion1_coverage_band[0.30,0.60]": in_band,
              "criterion1_headroom>=0.15": headroom, "criterion2_feedback_rich": True,
              "gate": "PASS" if (in_band and headroom) else "does-not-qualify"}
    Path("artifacts").mkdir(exist_ok=True)
    Path(f"artifacts/phase3a_screen_{tag}.json").write_text(json.dumps(result, indent=2))
    # Enriched-pool persistence (Phase 3R restart item 4): keep the per-candidate
    # execution detail (frac/n_passed/failing/exc) so D2c/E6 + R3 can consume the
    # graded landscape without re-executing. Screen verdicts unaffected.
    Path("runs/modal").mkdir(parents=True, exist_ok=True)
    Path(f"runs/modal/bcb_res_{tag}.json").write_text(json.dumps(
        {"tag": tag, "task_ids": [p["task_id"] for p in problems], "results": results}))
    print(f"\n=== Phase 3a screen: {dataset} @ {model.split('/')[-1]} "
          f"({len(counts)} problems, k={k}) ===")
    print(f"pass@1 {result['pass@1']:.3f}  pass@8 {p8:.3f}  pass@50 {p50:.3f}  "
          f"(pass@50−pass@8 = {p50-p8:+.3f})")
    print(f"coverage band [0.30,0.60]: {in_band}   headroom ≥0.15: {headroom}")
    print(f"import-failure rate: {import_rate:.3f}   errors: {dict(errs)}")
    print(f"\n3a gate ({tag}): {result['gate']}")
    print(f"wrote artifacts/phase3a_screen_{tag}.json")
    return result


@app.local_entrypoint()
def screen_main(n_problems: int = 60, k: int = 50, dataset: str = "bigcode/bigcodebench",
                model: str = MODEL, tag: str = "screen", shuffle: bool = False, workers: int = 16):
    """Generate (vLLM) → persist candidates → execute (hardened) → score. Candidates
    are saved before execution so a slow/failed exec can be re-run via exec_only
    without regenerating."""
    from pathlib import Path
    gen = bcb_generate.remote(n_problems, k, 17, dataset, model, shuffle)
    Path("runs/modal").mkdir(parents=True, exist_ok=True)
    Path(f"runs/modal/bcb_cand_{tag}.json").write_text(
        json.dumps({"problems": gen["problems"], "k": k, "dataset": dataset, "model": model}))
    results = bcb_exec.remote(gen["problems"], 8, workers)
    _finalize(gen["problems"], results, dataset, model, k, tag)


@app.local_entrypoint()
def exec_only(tag: str = "screen"):
    """Re-execute persisted candidates (runs/modal/bcb_cand_<tag>.json) — no
    regeneration. For iterating on the executor after a slow run."""
    from pathlib import Path
    c = json.loads(Path(f"runs/modal/bcb_cand_{tag}.json").read_text())
    results = bcb_exec.remote(c["problems"])
    _finalize(c["problems"], results, c["dataset"], c["model"], c["k"], tag)


@app.local_entrypoint()
def exec_enrich(tag: str = "screen"):
    """Re-execute a persisted pool ONLY to persist per-candidate detail
    (runs/modal/bcb_res_<tag>.json) for D2c/E6 + R3. Deliberately does NOT rewrite
    the landed screen artifact: a re-exec can shift aggregates within judge noise,
    and a landed verdict is never re-scored (append, never revise)."""
    from pathlib import Path
    c = json.loads(Path(f"runs/modal/bcb_cand_{tag}.json").read_text())
    results = bcb_exec.remote(c["problems"])
    Path(f"runs/modal/bcb_res_{tag}.json").write_text(json.dumps(
        {"tag": tag, "task_ids": [p["task_id"] for p in c["problems"]],
         "results": results}))
    npass = sum(r["passed"] for res in results for r in res)
    ntot = sum(len(res) for res in results)
    print(f"enriched {tag}: {ntot} candidates, {npass} passed "
          f"({npass/max(1,ntot):.3f}); wrote runs/modal/bcb_res_{tag}.json "
          f"(screen artifact untouched)")


@app.local_entrypoint()
def r2_smoke(n_problems: int = 8, k: int = 8, arch: str = "base",
             temperature: float = 1.0, dataset: str = "bigcode/bigcodebench"):
    """Validate the base completion prompt/extraction path before the full R2 sweep
    (pre-registered caveat: 'validate the prompt/extraction path before trusting any
    number'). Prints a sample module, non-empty-body rate, and pass stats."""
    from pathlib import Path
    gen = r2_generate.remote(n_problems, k, 17, dataset, arch, temperature, 1.0)
    probs = gen["problems"]
    Path("runs/modal").mkdir(parents=True, exist_ok=True)
    Path(f"runs/modal/r2_smoke_{arch}.json").write_text(json.dumps(gen))
    results = bcb_exec.remote(probs, 8, 16)
    # non-empty / runnable diagnostics
    ncodes = sum(len(p["codes"]) for p in probs)
    nnull = sum(1 for p in probs for c in p["codes"] if not c or len(c.strip()) < 5)
    passed = sum(r["passed"] for res in results for r in res)
    fracs = [r["frac"] for res in results for r in res if "frac" in r]
    print(f"\n=== R2 smoke: {arch} @ T={temperature}, top_p=1.0 "
          f"({n_problems} problems × k={k}) ===")
    print(f"candidates {ncodes} | empty/degenerate {nnull} ({nnull/max(1,ncodes):.2f}) | "
          f"passed {passed} ({passed/max(1,ncodes):.2f})")
    if fracs:
        print(f"frac_tests: mean {sum(fracs)/len(fracs):.3f}  "
              f">0 {sum(f>0 for f in fracs)/len(fracs):.2f}  ==1 {sum(f>=1 for f in fracs)/len(fracs):.2f}")
    print("--- sample extracted module (problem 0, candidate 0) ---")
    print((probs[0]["codes"][0] or "<none>")[:600])
    print("--- errors ---")
    from collections import Counter
    print(dict(Counter(r["err"] for res in results for r in res)))


@app.local_entrypoint()
def r2_screen(n_problems: int = 200, k: int = 50, dataset: str = "bigcode/bigcodebench",
              arch: str = "base", temperature: float = 1.0, workers: int = 16):
    """One R2 sweep cell: generate (random samples) → persist → exec (fixed judge) →
    score pass@8 / pass@50−pass@8 against the gate. tag = r2_<arch>_T<temp>."""
    from pathlib import Path
    tag = f"r2_{arch}_T{str(temperature).replace('.', '')}"
    gen = r2_generate.remote(n_problems, k, 17, dataset, arch, temperature, 1.0)
    Path("runs/modal").mkdir(parents=True, exist_ok=True)
    Path(f"runs/modal/bcb_cand_{tag}.json").write_text(json.dumps(
        {"problems": gen["problems"], "k": k, "dataset": dataset,
         "model": (BASE_MODEL if arch == "base" else MODEL),
         "arch": arch, "temperature": temperature, "top_p": 1.0}))
    results = bcb_exec.remote(gen["problems"], 8, workers)
    _finalize(gen["problems"], results,
              f"{dataset} [{arch}, T={temperature}, top_p=1.0]",
              BASE_MODEL if arch == "base" else MODEL, k, tag)


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
