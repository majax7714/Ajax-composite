"""Phase 4 Modal runner — H1 cross-family battery + H2 hint/near-miss arms
([PHASE_4.md] H1/H2, pre-registered 2026-07-16).

Families: deepseek-ai/deepseek-coder-1.3b-base, bigcode/starcoder2-3b.
Cells per family (seed 17, top_p 1.0, T=0.8):
  smoke  — 8 LCB-easy problems x 8, frozen fenced scaffold; gate wf>=0.85 dg<=0.10
  lcb    — full 80 LCB-easy, k=50; SHORT-CIRCUIT judge (pass@k only, §8-5 cost rule)
  bcb    — committed 200-problem BCB-Complete subset (seed-17 shuffle), k=50
  d2c    — frozen 44 D2c artifacts x {E0 no-context, E1 D2C context}, k=8;
           ALL-CASES judge (frac is the analysis); PULL computed locally

Judge code duplicated verbatim from the frozen implementations (modal_lcb.lcb_exec,
modal_phase3a.bcb_exec) with two recorded deviations: an optional short-circuit in
the LCB judge (pass/fail semantics identical) and right-sized containers (cpu=8/16
LCB, cpu=16/32GiB BCB vs the 32/64 legacy — §8 entry 5).

Remote results are volume-persisted under /cache/h1/<tag>.json before returning
(resume across app death); local copies land in runs/modal/h1_*.json.
"""
import json
from pathlib import Path

import modal

VOL = modal.Volume.from_name("rgr-hf-cache", create_if_missing=True)
app = modal.App("rgr-h1")

FAMILIES = {
    "deepseek": "deepseek-ai/deepseek-coder-1.3b-base",
    "starcoder2": "bigcode/starcoder2-3b",
}
QWEN_BASE = "Qwen/Qwen2.5-Coder-1.5B"  # the frozen Phase-3b config generator (H2 arms)
QWEN7B = "Qwen/Qwen2.5-Coder-7B"                  # J5 (sign-off 2026-07-17)
QWEN7B_INSTRUCT = "Qwen/Qwen2.5-Coder-7B-Instruct"

# Phase 6 P1 discriminator battery — pinned revisions (main SHAs resolved
# 2026-07-17, [PHASE_6.md] P0.1). (short_name -> (model_id, revision)).
J6_MODELS = {
    "qwen05b": ("Qwen/Qwen2.5-Coder-0.5B",
                "8123ea2e9354afb7ffcc6c8641d1b2f5ecf18301"),
    "qwen3b": ("Qwen/Qwen2.5-Coder-3B",
               "09d9bc5d376b0cfa0100a0694ea7de7232525803"),
    "qwen15b_general": ("Qwen/Qwen2.5-1.5B",
                        "8faed761d45a263340a0528343f099c05c9a4323"),
}
# Phase 6 P2 — distinct-seed verification of the flagship floor number.
QWEN_BASE_REV = "df3ce67c0e24480f20468b6ef2894622d69eb73b"  # 1.5B-Coder base @ main
P2_SEED = 41  # DISTINCT from the record's seed 17 (mandatory distinct-seed protocol)

# Phase 7 P1 — matched-artifact battery ([PHASE_7.md] P1). Each model is
# conditioned at its OWN quality match (Delta_art ~ 0) on artifacts mined from the
# fixed donor pool (scripts/j7_match_artifacts.py). Revisions reuse the Phase 6
# P0.1 pins (organic pins from that table). (cell -> (model_id, revision)).
J7_MODELS = {
    "M5_coder0p5b":     ("Qwen/Qwen2.5-Coder-0.5B",
                         "8123ea2e9354afb7ffcc6c8641d1b2f5ecf18301"),
    "M2_general1p5b":   ("Qwen/Qwen2.5-1.5B",
                         "8faed761d45a263340a0528343f099c05c9a4323"),
    "M3_starcoder2_3b": ("bigcode/starcoder2-3b",
                         "733247c55e3f73af49ce8e9c7949bf14af205928"),
    "M1_deepseek1p3b":  ("deepseek-ai/deepseek-coder-1.3b-base",
                         "c919139c3a9b4070729c8b2cca4847ab29ca8d94"),
    "M4_coder7b":       ("Qwen/Qwen2.5-Coder-7B",
                         "0396a76181e127dfc13e5c5ec48a8cee09938b02"),
}
LCB_DATASET = "livecodebench/code_generation"
BCB_DATASET = "bigcode/bigcodebench"

GEN_IMAGE = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("vllm==0.11.0", "transformers==4.57.0", "datasets==5.0.0")
    .env({"HF_HOME": "/cache/hf", "TOKENIZERS_PARALLELISM": "false",
          "VLLM_LOGGING_LEVEL": "WARNING",
          "HF_HUB_OFFLINE": "1", "HF_DATASETS_OFFLINE": "1"})
)
DL_IMAGE = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("huggingface_hub")
    .env({"HF_HOME": "/cache/hf"})  # hub ONLINE: this image exists to fetch models
)
LCB_EXEC_IMAGE = modal.Image.debian_slim(python_version="3.12").pip_install(
    "datasets==5.0.0", "numpy").env({"HF_HOME": "/cache/hf",
                                     "HF_HUB_OFFLINE": "1", "HF_DATASETS_OFFLINE": "1"})
BCB_EXEC_IMAGE = modal.Image.debian_slim(python_version="3.12").pip_install(
    "datasets==5.0.0", "numpy", "pandas", "scipy", "scikit-learn", "matplotlib",
    "seaborn", "requests", "beautifulsoup4", "lxml", "nltk", "sympy", "pillow",
    "flask", "statsmodels", "openpyxl", "python-dateutil", "pytz", "regex",
    "faker", "cryptography", "networkx", "sqlalchemy", "pyyaml", "wordcloud",
    "textblob", "gensim", "folium", "geopy", "django", "psutil",
).env({"HF_HOME": "/cache/hf", "MPLBACKEND": "Agg"})

_BASE_STOP = ["\ndef ", "\nclass ", "\nif __name__", "\n@", "\nprint(",
              "\nassert ", "\n# Test", "\n```", "\nExample"]


def _cache_or(tag, compute):
    """Volume-first persistence: return /cache/h1/<tag>.json if present, else
    compute, write, commit, return."""
    p = Path(f"/cache/h1/{tag}.json")
    if p.exists():
        return json.loads(p.read_text())
    out = compute()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out))
    VOL.commit()
    return out


@app.function(image=DL_IMAGE, volumes={"/cache": VOL}, timeout=3600)
def h1_download():
    from huggingface_hub import snapshot_download
    for mid in FAMILIES.values():
        print("downloading", mid)
        snapshot_download(mid)
    VOL.commit()
    return list(FAMILIES.values())


@app.function(image=GEN_IMAGE, gpu="L4", volumes={"/cache": VOL}, timeout=7200)
def h1_gen_lcb(model_id: str, items: list, n: int, tag: str,
               temperature: float = 0.8, top_p: float = 1.0, seed: int = 17,
               revision: str = None):
    """Frozen R2/p3b fenced-completion scaffold, parametrized by model.
    items: [{qid, context|None}]. `revision` (added Phase 6, no-op default —
    existing frozen callers omit it) pins the exact HF commit at load time."""
    def compute():
        from datasets import load_dataset
        from vllm import LLM, SamplingParams

        ds = load_dataset(LCB_DATASET, split="test")
        q = {ds[i]["question_id"]: ds[i]["question_content"] for i in range(len(ds))}

        def prompt(it):
            head = "Problem:\n" + q[it["qid"]].strip()
            if it.get("context"):
                head += "\n\n" + it["context"].rstrip()
            return (head + "\n\nA complete Python 3 program that reads from standard "
                    "input and writes the answer to standard output:\n\n```python\n")

        llm = LLM(model=model_id, dtype="bfloat16", gpu_memory_utilization=0.90,
                  max_model_len=8192, seed=seed,
                  **({"revision": revision} if revision else {}))
        sp = SamplingParams(n=n, temperature=temperature, top_p=top_p,
                            max_tokens=1536, seed=seed, stop=["```", "\nProblem:"])
        outs = llm.generate([prompt(it) for it in items], sp)
        return [{"qid": it["qid"], "codes": [(o.text.strip() or None) for o in req.outputs]}
                for it, req in zip(items, outs)]
    return _cache_or(tag, compute)


@app.function(image=GEN_IMAGE, gpu="L4", volumes={"/cache": VOL}, timeout=7200)
def h1_gen_bcb(model_id: str, tag: str, n_problems: int = 200, k: int = 50,
               seed: int = 17, temperature: float = 0.8, top_p: float = 1.0):
    """Frozen R2 base-completion BCB path (committed seed-17 shuffle subset)."""
    def compute():
        import random as _rnd

        from datasets import load_dataset
        from vllm import LLM, SamplingParams

        ds = load_dataset(BCB_DATASET, split="v0.1.4")
        order = list(range(len(ds)))
        _rnd.Random(seed).shuffle(order)
        idx = order[:min(n_problems, len(ds))]

        llm = LLM(model=model_id, dtype="bfloat16", gpu_memory_utilization=0.90,
                  max_model_len=4096, seed=seed)
        sp = SamplingParams(n=k, temperature=temperature, top_p=top_p,
                            max_tokens=1024, seed=seed, stop=_BASE_STOP)
        outs = llm.generate([ds[i]["complete_prompt"] for i in idx], sp)
        return {"problems": [
            {"task_id": ds[i]["task_id"], "test": ds[i]["test"],
             "entry_point": ds[i]["entry_point"],
             "codes": [ds[i]["complete_prompt"] + o.text for o in outs[j].outputs]}
            for j, i in enumerate(idx)], "k": k}
    return _cache_or(tag, compute)


@app.function(image=LCB_EXEC_IMAGE, volumes={"/cache": VOL}, timeout=14400,
              cpu=8.0, memory=16384)
def h1_lcb_exec(question_ids: list, codes: list, tag: str, cap_private: int = 12,
                timeout_s: int = 8, short_circuit: bool = False) -> list:
    """Frozen lcb_exec judge (verbatim semantics) + optional short-circuit.
    short_circuit=True: stop at first failing case — pass/fail identical, frac
    NOT meaningful (reported as prefix-frac; consumers must not use it)."""
    def compute():
        import json as _j
        import os
        import signal
        import subprocess
        import sys
        import tempfile
        from concurrent.futures import ThreadPoolExecutor
        from pathlib import Path as _P

        from datasets import load_dataset

        ds = load_dataset(LCB_DATASET, split="test")
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
                (_P(d) / "s.py").write_text(PRE + code)
                (_P(d) / "in.txt").write_text(stdin_str)
                outf, errf = _P(d) / "o.txt", _P(d) / "e.txt"
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
                elines = [l for l in errf.read_text(errors="replace").strip().splitlines()
                          if l.strip()]
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
            return {"passed": not failing, "n_tests": len(cases),
                    "n_passed": n_passed,
                    "frac": n_passed / len(cases) if cases else 0.0,
                    "failing": failing, "err": first_err, "exc": first_exc}

        out = []
        with ThreadPoolExecutor(max_workers=8) as tp:
            for qid, row in zip(question_ids, codes):
                out.append(list(tp.map(judge, [(c, qid) for c in row])))
        return out
    return _cache_or(tag, compute)


@app.function(image=BCB_EXEC_IMAGE, volumes={"/cache": VOL}, timeout=14400,
              cpu=16.0, memory=32768)
def h1_bcb_exec(problems: list, tag: str, timeout_s: int = 10,
                max_workers: int = 16) -> list:
    """Frozen bcb_exec judge, verbatim (right-sized container recorded)."""
    def compute():
        import os
        import signal
        import subprocess
        import sys
        import tempfile
        from concurrent.futures import ThreadPoolExecutor
        from pathlib import Path as _P

        PREAMBLE = (
            "import resource as _rs, socket as _sk\n"
            "try:\n"
            f"    _rs.setrlimit(_rs.RLIMIT_CPU, ({timeout_s}, {timeout_s}))\n"
            "    _rs.setrlimit(_rs.RLIMIT_AS, (2*1024**3, 2*1024**3))\n"
            "except Exception: pass\n"
            "_sk.setdefaulttimeout(4)\n\n"
        )
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
                (_P(d) / "cand.py").write_text(PREAMBLE + code + "\n\n" + test + RUNNER)
                outf = _P(d) / "o.txt"
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
                    try:
                        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                    except (ProcessLookupError, PermissionError):
                        pass
                    try:
                        proc.wait(timeout=5)
                    except Exception:
                        pass
                try:
                    out = outf.read_text(errors="replace")
                except OSError:
                    out = ""
            if timed_out:
                return {"passed": False, "frac": 0.0, "err": "timeout"}
            line = next((l for l in out.splitlines() if l.startswith("BCBRESULT")), None)
            if line:
                d = json.loads(line[len("BCBRESULT"):].strip())
                n, f, e = d["n"], d["f"], d["e"]
                ok = n > 0 and f == 0 and e == 0
                return {"passed": ok, "n_tests": n, "n_passed": n - f - e,
                        "frac": (n - f - e) / n if n else 0.0,
                        "err": "" if ok else "wrong_answer"}
            err = ("import" if ("ModuleNotFoundError" in out or "ImportError" in out)
                   else "syntax" if "SyntaxError" in out else "runtime")
            return {"passed": False, "frac": 0.0, "err": err}

        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as tp:
            for prob in problems:
                results.append(list(tp.map(run_one, [(c, prob["test"]) for c in prob["codes"]])))
        return results
    return _cache_or(tag, compute)


@app.function(image=LCB_EXEC_IMAGE, volumes={"/cache": VOL}, timeout=1800,
              cpu=2.0, memory=8192)
def h1_dump_questions(question_ids: list) -> dict:
    """H2 prep: dump statements (+ any solution-bearing metadata) for hint work."""
    from datasets import load_dataset
    ds = load_dataset(LCB_DATASET, split="test")
    want = set(question_ids)
    out, cols = {}, ds.column_names
    for i in range(len(ds)):
        qid = ds[i]["question_id"]
        if qid in want:
            row = {"question_content": ds[i]["question_content"],
                   "starter_code": ds[i].get("starter_code", ""),
                   "difficulty": ds[i].get("difficulty", ""),
                   "contest_date": str(ds[i].get("contest_date", "")),
                   "metadata": str(ds[i].get("metadata", ""))[:2000]}
            out[qid] = row
    return {"columns": cols, "questions": out}


# ---------------------------------------------------------------- local helpers

REPO = Path(__file__).parents[1]


def _pass_at_k(n, c, kk):
    from math import comb
    return 1.0 if n - c < kk else 1.0 - comb(n - c, kk) / comb(n, kk)


def _lcb_easy_qids():
    res = json.loads((REPO / "runs/modal/lcb_res_lcb_r2_base_T08.json").read_text())
    return res["question_ids"]


def _d2c_artifacts():
    """The frozen 44-artifact set (W3 §2 rule, from committed pools)."""
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


def _d2c_context(a):
    """Frozen D2C wording (modal_lcb._p3b_context)."""
    npass = a["n_tests"] - a["n_failed"]
    code = (a.get("code") or "")[:3000]
    return (f"A previous attempt:\n```python\n{code}\n```\n"
            f"This attempt passed {npass} of {a['n_tests']} tests.\n"
            "Improve it so that all tests pass.")


def _persist(name, obj):
    p = REPO / f"runs/modal/{name}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj))
    return obj


def _load(name):
    p = REPO / f"runs/modal/{name}.json"
    return json.loads(p.read_text()) if p.exists() else None


# ---------------------------------------------------------------- entrypoints

# ---- H2 frozen prompt wording + local plumbing ([PHASE_4.md] H2) ----

def _hint_context(hint):
    """Frozen HINT context block (parallel structure to the R3 TRACE block)."""
    return f"Approach hint: {hint}\nWrite a correct complete program."


def _trace_context(a):
    """Frozen TRACE wording (modal_lcb._p3b_context, verbatim)."""
    t = a["trace"]
    return (f"A previous attempt failed {a['n_failed']} of {a['n_tests']} tests.\n"
            f"First failing test:\ninput:\n{t['stdin']}\n"
            f"expected output:\n{t['expected']}\nactual output:\n{t['actual']}\n"
            "Write a correct complete program.")


def _h2_frozen():
    return json.loads((REPO / "artifacts/h2_hints_frozen.json").read_text())


def _mcnemar_one_sided(b, c):
    from math import comb
    m = b + c
    if m == 0:
        return 1.0
    return sum(comb(m, k) for k in range(b, m + 1)) / 2 ** m


def _wilcoxon_mc_one_sided(diffs, trials=20000, seed=17):
    """P(mean signed diff >= observed) under sign-flip null."""
    import random as _r
    rng = _r.Random(seed)
    obs = sum(diffs) / len(diffs)
    hits = 0
    for _ in range(trials):
        s = sum(d if rng.random() < 0.5 else -d for d in diffs) / len(diffs)
        if s >= obs:
            hits += 1
    return (hits + 1) / (trials + 1)


@app.function(image=LCB_EXEC_IMAGE, volumes={"/cache": VOL}, timeout=3600, cpu=8.0,
              memory=16384)
def h2_trace_capture(question_ids: list, codes: list, tag: str,
                     cap_private: int = 12, timeout_s: int = 8) -> list:
    """First-failing-case capture — duplicated verbatim from the frozen
    modal_lcb.lcb_trace_capture (512-char cap)."""
    def compute():
        import json as _j
        import os
        import signal
        import subprocess
        import sys
        import tempfile
        from pathlib import Path as _P

        from datasets import load_dataset

        ds = load_dataset(LCB_DATASET, split="test")
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
                (_P(d) / "s.py").write_text(PRE + code)
                (_P(d) / "in.txt").write_text(stdin_str)
                outf, errf = _P(d) / "o.txt", _P(d) / "e.txt"
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
                elines = [l for l in errf.read_text(errors="replace").strip().splitlines()
                          if l.strip()]
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
    return _cache_or(tag, compute)


@app.local_entrypoint()
def h1_prefetch():
    print(h1_download.remote())


@app.local_entrypoint()
def h2_manip(family: str = "qwen"):
    """H2a manipulation-check gate: 20 mid-p̂ problems x {E0-25, HINT-25}, fresh.
    family='qwen' is the gate (frozen config); other families run the E-H2
    exploratory discrimination cell ([PHASE_4.md] E-H2)."""
    import statistics as st

    model = QWEN_BASE if family == "qwen" else FAMILIES[family]
    suf = "" if family == "qwen" else f"_{family}"
    fz = _h2_frozen()
    qids = fz["groups"]["manip_check"]
    hints = fz["hints"]
    items = ([{"qid": q, "context": None} for q in qids]
             + [{"qid": q, "context": _hint_context(hints[q])} for q in qids])
    gen = _load(f"h2_manip_cand{suf}") or _persist(
        f"h2_manip_cand{suf}",
        h1_gen_lcb.remote(model, items, 25, tag=f"h2_manip_cand{suf}"))
    res = _load(f"h2_manip_res{suf}") or _persist(
        f"h2_manip_res{suf}",
        h1_lcb_exec.remote([g["qid"] for g in gen], [g["codes"] for g in gen],
                           tag=f"h2_manip_res{suf}", short_circuit=True))
    n = len(qids)
    e0 = [sum(r["passed"] for r in row) / len(row) for row in res[:n]]
    hi = [sum(r["passed"] for r in row) / len(row) for row in res[n:]]
    diffs = [b - a for a, b in zip(e0, hi)]
    p = _wilcoxon_mc_one_sided(diffs)
    mean_d = st.mean(diffs)
    gate = "PASS" if (mean_d > 0 and p < 0.05) else (
        "HARM" if mean_d < -0.05 else "FAIL")
    out = {"_label": f"H2a manipulation check [{family}]", "model": model,
           "n_problems": n,
           "e0_mean_pass": st.mean(e0), "hint_mean_pass": st.mean(hi),
           "mean_uplift": mean_d, "p_one_sided": p, "gate": gate,
           "per_problem": [{"qid": q, "e0": a, "hint": b}
                           for q, a, b in zip(qids, e0, hi)]}
    (REPO / f"artifacts/h2_manip_check{suf}.json").write_text(json.dumps(out, indent=2))
    print(f"=== H2a manipulation check [{family}]: E0 {st.mean(e0):.3f} → HINT "
          f"{st.mean(hi):.3f} (Δ {mean_d:+.3f}, p {p:.4f}) → {gate} ===")


@app.local_entrypoint()
def h2a_stratum(amended: bool = False):
    """H2a stratum arm: medium 0/50 stratum (n=68), fresh B1-50 vs HINT-50,
    paired exact McNemar. Fires on manipulation-gate PASS, or under the AMENDED
    pre-registration ([PHASE_4.md] H2a part 2: original gate metric documented as
    mis-specified; coverage-form gate passed via H2b p=0.015)."""
    gate = json.loads((REPO / "artifacts/h2_manip_check.json").read_text())["gate"]
    if gate != "PASS" and not amended:
        print(f"manipulation gate = {gate}; stratum run POSTPONED per pre-reg "
              "(run with --amended under the H2a part 2 registration)")
        return
    fz = _h2_frozen()
    qids = fz["groups"]["stratum_medium"]
    hints = fz["hints"]
    items = ([{"qid": q, "context": None} for q in qids]
             + [{"qid": q, "context": _hint_context(hints[q])} for q in qids])
    gen = _load("h2a_cand") or _persist(
        "h2a_cand", h1_gen_lcb.remote(QWEN_BASE, items, 50, tag="h2a_cand"))
    res = _load("h2a_res") or _persist(
        "h2a_res",
        h1_lcb_exec.remote([g["qid"] for g in gen], [g["codes"] for g in gen],
                           tag="h2a_res", short_circuit=True))
    n = len(qids)
    b1 = [any(r["passed"] for r in row) for row in res[:n]]
    hi = [any(r["passed"] for r in row) for row in res[n:]]
    b = sum(1 for x, y in zip(b1, hi) if y and not x)
    c = sum(1 for x, y in zip(b1, hi) if x and not y)
    p = _mcnemar_one_sided(b, c)
    out = {"_label": "H2a stratum arm — HINT-50 vs fresh B1-50, medium 0/50 [PHASE_4.md H2a]",
           "n": n, "b1_recoveries": sum(b1), "hint_recoveries": sum(hi),
           "hint_only": b, "b1_only": c, "p_one_sided_mcnemar": p,
           "recovered_qids": {"b1": [q for q, x in zip(qids, b1) if x],
                              "hint": [q for q, x in zip(qids, hi) if x]},
           "floor_reference_W0c": 2.0}
    (REPO / "artifacts/h2a_hint_arm.json").write_text(json.dumps(out, indent=2))
    print(f"=== H2a stratum: B1 {sum(b1)}, HINT {sum(hi)} (hint-only {b}, b1-only {c}, "
          f"p {p:.4f}); floor ref 2.0 ===")


@app.function(image=DL_IMAGE, volumes={"/cache": VOL}, timeout=3600)
def h5_download(models: list):
    from huggingface_hub import snapshot_download
    for mid in models:
        print("downloading", mid)
        snapshot_download(mid)
    VOL.commit()
    return models


@app.function(image=GEN_IMAGE, gpu="L4", volumes={"/cache": VOL}, timeout=3600)
def h5_selfhint_gen(model_id: str, question_ids: list, tag: str,
                    max_tokens: int = 120):
    """J3/J4 SELFHINT channel: an instruct model writes its own approach hint
    from the problem statement alone. Frozen prompt [PHASE_5.md J3]."""
    def compute():
        import re

        from datasets import load_dataset
        from transformers import AutoTokenizer
        from vllm import LLM, SamplingParams

        ds = load_dataset(LCB_DATASET, split="test")
        q = {ds[i]["question_id"]: ds[i]["question_content"] for i in range(len(ds))}
        tok = AutoTokenizer.from_pretrained(model_id)

        def prompt(qid):
            user = (f"Problem:\n{q[qid][:2500]}\n\nIn at most two sentences, state "
                    "the algorithmic approach a correct solution must take. "
                    "Describe the idea only — no code, no variable names.")
            return tok.apply_chat_template([{"role": "user", "content": user}],
                                           add_generation_prompt=True, tokenize=False)

        llm = LLM(model=model_id, dtype="bfloat16", gpu_memory_utilization=0.90,
                  max_model_len=8192, seed=17)
        sp = SamplingParams(n=1, temperature=0.0, max_tokens=max_tokens, seed=17)
        outs = llm.generate([prompt(qid) for qid in question_ids], sp)
        res = []
        for qid, req in zip(question_ids, outs):
            txt = re.sub(r"```.*?(```|$)", "", req.outputs[0].text, flags=re.DOTALL).strip()
            res.append({"qid": qid, "selfhint": txt})
        return res
    return _cache_or(tag, compute)


@app.local_entrypoint()
def j3_selfhint():
    """J3 — SELFHINT-50 on the 68-problem medium stratum [PHASE_5.md J3]."""
    fz = _h2_frozen()
    qids = fz["groups"]["stratum_medium"]
    sh = _load("j3_selfhints") or _persist(
        "j3_selfhints",
        h5_selfhint_gen.remote("Qwen/Qwen2.5-Coder-1.5B-Instruct", qids,
                               tag="j3_selfhints"))
    by = {r["qid"]: r["selfhint"] for r in sh}
    items = [{"qid": q, "context": _hint_context(by[q])} for q in qids]
    gen = _load("j3_cand") or _persist(
        "j3_cand", h1_gen_lcb.remote(QWEN_BASE, items, 50, tag="j3_cand"))
    res = _load("j3_res") or _persist(
        "j3_res",
        h1_lcb_exec.remote([g["qid"] for g in gen], [g["codes"] for g in gen],
                           tag="j3_res", short_circuit=True))
    # controls: same-day fresh B1-50 and HINT-50 from the H2a amended run
    h2a_res = json.loads((REPO / "runs/modal/h2a_res.json").read_text())
    n = len(qids)
    b1 = [any(r["passed"] for r in row) for row in h2a_res[:n]]
    hint = [any(r["passed"] for r in row) for row in h2a_res[n:]]
    selfh = [any(r["passed"] for r in row) for row in res]
    def mcn(x, y):
        b = sum(1 for a, bb in zip(x, y) if bb and not a)
        c = sum(1 for a, bb in zip(x, y) if a and not bb)
        return b, c, _mcnemar_one_sided(b, c)
    b_vs, c_vs, p_vs_b1 = mcn(b1, selfh)
    bh, ch, p_vs_hint = mcn(selfh, hint)
    out = {"_label": "J3 — SELFHINT-50 vs B1-50/HINT-50, medium 0/50 [PHASE_5.md J3]",
           "n": n, "b1_recoveries": sum(b1), "hint_recoveries": sum(hint),
           "selfhint_recoveries": sum(selfh),
           "selfhint_vs_b1": {"selfhint_only": b_vs, "b1_only": c_vs, "p": p_vs_b1},
           "hint_vs_selfhint": {"hint_only": bh, "selfhint_only": ch, "p": p_vs_hint},
           "recovered_qids_selfhint": [q for q, v in zip(qids, selfh) if v]}
    (REPO / "artifacts/h5_selfhint_qwen.json").write_text(json.dumps(out, indent=2))
    print(f"=== J3: B1 {sum(b1)} | SELFHINT {sum(selfh)} | HINT {sum(hint)} ; "
          f"selfhint-vs-B1 p {p_vs_b1:.4f} ; hint-vs-selfhint p {p_vs_hint:.4f} ===")


@app.local_entrypoint()
def j4_prefetch():
    print(h5_download.remote(["deepseek-ai/deepseek-coder-1.3b-instruct"]))


@app.local_entrypoint()
def j5_prefetch():
    print(h5_download.remote([QWEN7B, QWEN7B_INSTRUCT]))


@app.local_entrypoint()
def j5_smoke():
    """J5 smoke gate + KV feasibility: 8 LCB-easy x 8 on 7B base."""
    qids = _lcb_easy_qids()[:8]
    gen = _load("j5_smoke_cand") or _persist(
        "j5_smoke_cand",
        h1_gen_lcb.remote(QWEN7B, [{"qid": q, "context": None} for q in qids], 8,
                          tag="j5_smoke_cand"))
    codes = [g["codes"] for g in gen]
    flat = [c for row in codes for c in row]
    wf = sum(1 for c in flat if c) / len(flat)
    dg = sum(1 for c in flat if c and len(c) < 20) / max(1, sum(1 for c in flat if c))
    res = _load("j5_smoke_res") or _persist(
        "j5_smoke_res",
        h1_lcb_exec.remote([g["qid"] for g in gen], codes, tag="j5_smoke_res",
                           short_circuit=True))
    npass = sum(1 for row in res for r in row if r["passed"])
    ok = wf >= 0.85 and dg <= 0.10
    print(f"=== J5 smoke (7B): wf {wf:.3f} dg {dg:.3f} passed {npass}/{len(flat)} "
          f"→ {'PASS' if ok else 'FAIL'} ===")
    print("sample:\n" + next((c for c in flat if c), "")[:300])


@app.local_entrypoint()
def j5_q1():
    """J5 Q1 — pathology persistence at 7B: (a) D2c cell 44 x {E0,E1} x 8
    all-cases; (b) language cell 20 x {E0,HINT} x 25 [PHASE_5.md J5]."""
    import statistics as st

    # Q1a — D2c cell
    arts = _d2c_artifacts()
    items = ([{"qid": a["qid"], "context": None} for a in arts]
             + [{"qid": a["qid"], "context": _d2c_context(a)} for a in arts])
    dgen = _load("j5_q1a_cand") or _persist(
        "j5_q1a_cand", h1_gen_lcb.remote(QWEN7B, items, 8, tag="j5_q1a_cand"))
    dres = _load("j5_q1a_res") or _persist(
        "j5_q1a_res",
        h1_lcb_exec.remote([g["qid"] for g in dgen], [g["codes"] for g in dgen],
                           tag="j5_q1a_res"))
    n = len(arts)
    e0_frac = [st.mean(x["frac"] for x in row) for row in dres[:n]]
    e1_frac = [st.mean(x["frac"] for x in row) for row in dres[n:]]
    copy_null = [a["frac"] for a in arts]
    d_iid = [b - a for a, b in zip(e0_frac, e1_frac)]
    d_copy = [b - a for a, b in zip(copy_null, e1_frac)]
    # one-sided: P(conditioned below null) via sign-flip on negated deltas
    p_sink_iid = _wilcoxon_mc_one_sided([-x for x in d_iid])
    p_sink_copy = _wilcoxon_mc_one_sided([-x for x in d_copy])
    q1a = {"e0_mean_frac_iid": st.mean(e0_frac), "e1_mean_frac_cond": st.mean(e1_frac),
           "copy_null_mean": st.mean(copy_null),
           "delta_cond_minus_iid": st.mean(d_iid),
           "delta_cond_minus_copy": st.mean(d_copy),
           "p_one_sided_cond_below_iid": p_sink_iid,
           "p_one_sided_cond_below_copy": p_sink_copy}
    print(f"Q1a: iid {q1a['e0_mean_frac_iid']:.3f} | cond {q1a['e1_mean_frac_cond']:.3f} | "
          f"copy {q1a['copy_null_mean']:.3f} | p_below_iid {p_sink_iid:.4f} "
          f"p_below_copy {p_sink_copy:.4f}")

    # Q1b — language cell
    fz = _h2_frozen()
    qids = fz["groups"]["manip_check"]
    hints = fz["hints"]
    items = ([{"qid": q, "context": None} for q in qids]
             + [{"qid": q, "context": _hint_context(hints[q])} for q in qids])
    mgen = _load("j5_q1b_cand") or _persist(
        "j5_q1b_cand", h1_gen_lcb.remote(QWEN7B, items, 25, tag="j5_q1b_cand"))
    mres = _load("j5_q1b_res") or _persist(
        "j5_q1b_res",
        h1_lcb_exec.remote([g["qid"] for g in mgen], [g["codes"] for g in mgen],
                           tag="j5_q1b_res", short_circuit=True))
    m = len(qids)
    e0 = [sum(r["passed"] for r in row) / len(row) for row in mres[:m]]
    hi = [sum(r["passed"] for r in row) / len(row) for row in mres[m:]]
    diffs = [b - a for a, b in zip(e0, hi)]
    q1b = {"e0_mean_pass": st.mean(e0), "hint_mean_pass": st.mean(hi),
           "mean_uplift": st.mean(diffs),
           "p_one_sided_uplift": _wilcoxon_mc_one_sided(diffs)}
    print(f"Q1b: E0 {q1b['e0_mean_pass']:.3f} → HINT {q1b['hint_mean_pass']:.3f} "
          f"(Δ {q1b['mean_uplift']:+.3f}, p {q1b['p_one_sided_uplift']:.4f})")

    out = {"_label": "J5 Q1 — pathology persistence at 7B [PHASE_5.md J5]",
           "model": QWEN7B, "q1a_d2c": q1a, "q1b_language": q1b}
    (REPO / "artifacts/h5_7b_pathology.json").write_text(json.dumps(out, indent=2))
    print("wrote artifacts/h5_7b_pathology.json")


@app.local_entrypoint()
def j5_q2_screen():
    """J5 Q2 step 1 — 7B medium screen (78 x 50, all-cases)."""
    med = json.loads((REPO / "runs/modal/lcb_res_lcb_r2_base_medium_T08.json").read_text())
    qids = med["question_ids"]
    gen = _load("j5_q2_screen_cand") or _persist(
        "j5_q2_screen_cand",
        h1_gen_lcb.remote(QWEN7B, [{"qid": q, "context": None} for q in qids], 50,
                          tag="j5_q2_screen_cand"))
    res = _load("j5_q2_screen_res") or _persist(
        "j5_q2_screen_res",
        h1_lcb_exec.remote([g["qid"] for g in gen], [g["codes"] for g in gen],
                           tag="j5_q2_screen_res"))
    import statistics as st
    counts = [(len(row), sum(r["passed"] for r in row)) for row in res]
    p8 = st.mean(_pass_at_k(n, c, 8) for n, c in counts)
    p50 = st.mean(_pass_at_k(n, c, 50) for n, c in counts)
    stratum = [q for q, row in zip(qids, res) if not any(r["passed"] for r in row)]
    rich = sum(1 for q, row in zip(qids, res)
               if q in stratum and any(0 < r["frac"] < 1 for r in row))
    out = {"_label": "J5 Q2 step 1 — 7B medium screen [PHASE_5.md J5]",
           "model": QWEN7B, "pass@8": p8, "pass@50": p50,
           "stratum_size": len(stratum), "richness": rich, "stratum_qids": stratum}
    (REPO / "artifacts/h5_7b_medium_screen.json").write_text(json.dumps(out, indent=2))
    print(f"=== J5 Q2 screen: pass@8 {p8:.3f} pass@50 {p50:.3f} | "
          f"stratum {len(stratum)}/78 | richness {rich} ===")


@app.local_entrypoint()
def j5_q2_arms():
    """J5 Q2 step 3 — B1-50 / SELFHINT-50 on the 7B stratum (7B-Instruct writes
    the self-hints). Launch only after the floor prediction is committed."""
    scr = json.loads((REPO / "artifacts/h5_7b_medium_screen.json").read_text())
    qids = scr["stratum_qids"]
    sh = _load("j5_selfhints") or _persist(
        "j5_selfhints",
        h5_selfhint_gen.remote(QWEN7B_INSTRUCT, qids, tag="j5_selfhints"))
    sh_by = {r["qid"]: r["selfhint"] for r in sh}
    items = ([{"qid": q, "context": None} for q in qids]
             + [{"qid": q, "context": _hint_context(sh_by[q])} for q in qids])
    gen = _load("j5_arms_cand") or _persist(
        "j5_arms_cand", h1_gen_lcb.remote(QWEN7B, items, 50, tag="j5_arms_cand"))
    res = _load("j5_arms_res") or _persist(
        "j5_arms_res",
        h1_lcb_exec.remote([g["qid"] for g in gen], [g["codes"] for g in gen],
                           tag="j5_arms_res", short_circuit=True))
    n = len(qids)
    b1 = [any(r["passed"] for r in row) for row in res[:n]]
    se = [any(r["passed"] for r in row) for row in res[n:]]
    b = sum(1 for x, y in zip(b1, se) if y and not x)
    c = sum(1 for x, y in zip(b1, se) if x and not y)
    out = {"_label": "J5 Q2 — B1-50 vs SELFHINT-50 on the 7B stratum [PHASE_5.md J5]",
           "n": n, "b1_recoveries": sum(b1), "selfhint_recoveries": sum(se),
           "selfhint_only": b, "b1_only": c,
           "p_one_sided_mcnemar": _mcnemar_one_sided(b, c),
           "recovered_qids": {"b1": [q for q, v in zip(qids, b1) if v],
                              "selfhint": [q for q, v in zip(qids, se) if v]}}
    (REPO / "artifacts/h5_7b_switchon.json").write_text(json.dumps(out, indent=2))
    print(f"=== J5 Q2 arms: B1 {sum(b1)} | SELFHINT {sum(se)} "
          f"(+{b}/-{c}, p {out['p_one_sided_mcnemar']:.4f}) ===")


@app.function(image=LCB_EXEC_IMAGE, volumes={"/cache": VOL}, timeout=1800,
              cpu=2.0, memory=8192)
def j5_hard_qids(cap: int = 100, seed: int = 17) -> list:
    """LCB hard stdin population under the identical selection rule that built
    the W2 medium population [PHASE_5.md J5 Q2 extension]."""
    import json as _j
    import random as _rnd

    from datasets import load_dataset
    ds = load_dataset(LCB_DATASET, split="test")
    idx = []
    for i in range(len(ds)):
        if ds[i]["difficulty"] != "hard":
            continue
        try:
            pub = _j.loads(ds[i]["public_test_cases"])
            if pub and pub[0].get("testtype") == "stdin":
                idx.append(i)
        except Exception:
            pass
    _rnd.Random(seed).shuffle(idx)
    return [ds[i]["question_id"] for i in idx[:cap]]


@app.local_entrypoint()
def j5_hard_screen():
    """J5 Q2 extension step 1 — 7B hard screen (cap-100 x 50, all-cases judge)
    [PHASE_5.md J5 Q2 extension pre-registration]."""
    qids = _load("j5_hard_qids") or _persist("j5_hard_qids", j5_hard_qids.remote())
    gen = _load("j5_hard_screen_cand") or _persist(
        "j5_hard_screen_cand",
        h1_gen_lcb.remote(QWEN7B, [{"qid": q, "context": None} for q in qids], 50,
                          tag="j5_hard_screen_cand"))
    res = _load("j5_hard_screen_res")
    if res is None:
        # Sharded judging (§8 container right-sizing): one 8-cpu container hit
        # its 4h ceiling on the full 61x50 hard set. Frozen judge semantics
        # unchanged; per-shard volume tags keep the run resumable.
        chunk = 8
        shards = [gen[i:i + chunk] for i in range(0, len(gen), chunk)]
        calls = [h1_lcb_exec.spawn([g["qid"] for g in s], [g["codes"] for g in s],
                                   tag=f"j5_hard_screen_res_s{k}")
                 for k, s in enumerate(shards)]
        res = [row for c in calls for row in c.get()]
        _persist("j5_hard_screen_res", res)
    import statistics as st
    counts = [(len(row), sum(r["passed"] for r in row)) for row in res]
    p8 = st.mean(_pass_at_k(n, c, 8) for n, c in counts)
    p50 = st.mean(_pass_at_k(n, c, 50) for n, c in counts)
    stratum = [q for q, row in zip(qids, res) if not any(r["passed"] for r in row)]
    rich = sum(1 for q, row in zip(qids, res)
               if q in stratum and any(0 < r["frac"] < 1 for r in row))
    out = {"_label": "J5 Q2 extension step 1 — 7B hard screen [PHASE_5.md J5]",
           "model": QWEN7B, "n_problems": len(qids), "pass@8": p8, "pass@50": p50,
           "stratum_size": len(stratum), "richness": rich, "stratum_qids": stratum}
    (REPO / "artifacts/h5_7b_hard_screen.json").write_text(json.dumps(out, indent=2))
    print(f"=== J5 hard screen: pass@8 {p8:.3f} pass@50 {p50:.3f} | "
          f"stratum {len(stratum)}/{len(qids)} | richness {rich} ===")


@app.local_entrypoint()
def j5_dump_hard_questions():
    """Statements for the 7B hard stratum (self-hint grading needs them)."""
    hard = json.loads((REPO / "artifacts/h5_7b_hard_screen.json").read_text())
    out = h1_dump_questions.remote(hard["stratum_qids"])
    (REPO / "runs/modal/j5_hard_questions.json").write_text(json.dumps(out))
    print(f"dumped {len(out['questions'])} hard statements")


@app.local_entrypoint()
def j5_pooled_arms():
    """J5 Q2 extension steps 3-4 — B1-50 / SELFHINT-50 on the POOLED stratum
    (medium 46 + hard). Launch only after the hard-floor prediction is committed
    and the pooled power gate passes [PHASE_5.md J5 Q2 extension]."""
    med = json.loads((REPO / "artifacts/h5_7b_medium_screen.json").read_text())
    hard = json.loads((REPO / "artifacts/h5_7b_hard_screen.json").read_text())
    qids = med["stratum_qids"] + hard["stratum_qids"]
    n_med = len(med["stratum_qids"])
    sh = _load("j5_selfhints_pooled") or _persist(
        "j5_selfhints_pooled",
        h5_selfhint_gen.remote(QWEN7B_INSTRUCT, qids, tag="j5_selfhints_pooled"))
    sh_by = {r["qid"]: r["selfhint"] for r in sh}
    items = ([{"qid": q, "context": None} for q in qids]
             + [{"qid": q, "context": _hint_context(sh_by[q])} for q in qids])
    gen = _load("j5_pooled_arms_cand") or _persist(
        "j5_pooled_arms_cand",
        h1_gen_lcb.remote(QWEN7B, items, 50, tag="j5_pooled_arms_cand"))
    res = _load("j5_pooled_arms_res") or _persist(
        "j5_pooled_arms_res",
        h1_lcb_exec.remote([g["qid"] for g in gen], [g["codes"] for g in gen],
                           tag="j5_pooled_arms_res", short_circuit=True))
    n = len(qids)
    b1 = [any(r["passed"] for r in row) for row in res[:n]]
    se = [any(r["passed"] for r in row) for row in res[n:]]
    b = sum(1 for x, y in zip(b1, se) if y and not x)
    c = sum(1 for x, y in zip(b1, se) if x and not y)
    out = {"_label": "J5 Q2 — B1-50 vs SELFHINT-50 on the pooled 7B stratum "
                     "[PHASE_5.md J5 Q2 extension]",
           "n": n, "n_medium": n_med, "n_hard": n - n_med,
           "b1_recoveries": sum(b1), "selfhint_recoveries": sum(se),
           "b1_recoveries_medium": sum(b1[:n_med]),
           "b1_recoveries_hard": sum(b1[n_med:]),
           "selfhint_recoveries_medium": sum(se[:n_med]),
           "selfhint_recoveries_hard": sum(se[n_med:]),
           "selfhint_only": b, "b1_only": c,
           "p_one_sided_mcnemar": _mcnemar_one_sided(b, c),
           "recovered_qids": {"b1": [q for q, v in zip(qids, b1) if v],
                              "selfhint": [q for q, v in zip(qids, se) if v]}}
    (REPO / "artifacts/h5_7b_switchon.json").write_text(json.dumps(out, indent=2))
    print(f"=== J5 pooled arms: B1 {sum(b1)} (med {out['b1_recoveries_medium']} "
          f"hard {out['b1_recoveries_hard']}) | SELFHINT {sum(se)} "
          f"(+{b}/-{c}, p {out['p_one_sided_mcnemar']:.4f}) ===")


@app.local_entrypoint()
def j4_screen():
    """J4 step 1 — DeepSeek medium screen: 78 problems, k=50, all-cases judge
    (frac consumed by artifact selection + richness) [PHASE_5.md J4]."""
    med = json.loads((REPO / "runs/modal/lcb_res_lcb_r2_base_medium_T08.json").read_text())
    qids = med["question_ids"]
    gen = _load("j4_screen_cand") or _persist(
        "j4_screen_cand",
        h1_gen_lcb.remote(FAMILIES["deepseek"],
                          [{"qid": q, "context": None} for q in qids], 50,
                          tag="j4_screen_cand"))
    res = _load("j4_screen_res") or _persist(
        "j4_screen_res",
        h1_lcb_exec.remote([g["qid"] for g in gen], [g["codes"] for g in gen],
                           tag="j4_screen_res"))
    import statistics as st
    counts = [(len(row), sum(r["passed"] for r in row)) for row in res]
    p1 = st.mean(c / n for n, c in counts)
    p8 = st.mean(_pass_at_k(n, c, 8) for n, c in counts)
    p50 = st.mean(_pass_at_k(n, c, 50) for n, c in counts)
    stratum = [q for q, row in zip(qids, res) if not any(r["passed"] for r in row)]
    near = {x: sum(1 for _, c in counts if c == x) for x in (1, 2)}
    rich = sum(1 for q, row in zip(qids, res)
               if q in stratum and any(0 < r["frac"] < 1 for r in row))
    out = {"_label": "J4 step 1 — DeepSeek LCB-medium screen [PHASE_5.md J4]",
           "model": FAMILIES["deepseek"], "n_problems": len(qids), "k": 50,
           "pass@1": p1, "pass@8": p8, "pass@50": p50,
           "stratum_size_pass50_eq_0": len(stratum), "near_x1_x2": near,
           "stratum_with_partial_credit": rich,
           "stratum_qids": stratum}
    (REPO / "artifacts/h5_deepseek_medium_screen.json").write_text(json.dumps(out, indent=2))
    print(f"=== J4 screen: pass@1 {p1:.3f} pass@8 {p8:.3f} pass@50 {p50:.3f} | "
          f"stratum {len(stratum)}/{len(qids)} (x=1:{near[1]} x=2:{near[2]}) | "
          f"richness {rich}/{len(stratum)} ===")


@app.local_entrypoint()
def j4_arms():
    """J4 step 2 — DeepSeek four-arm stratum contrast: B1/TRACE/HINT/SELFHINT-50
    on the 76-problem DeepSeek-native stratum [PHASE_5.md J4]."""
    scr = json.loads((REPO / "artifacts/h5_deepseek_medium_screen.json").read_text())
    qids = scr["stratum_qids"]
    fz = _h2_frozen()
    ext = json.loads((REPO / "artifacts/h5_hints_extension.json").read_text())["hints"]
    hints = {**fz["hints"], **ext}

    # artifacts from the DeepSeek-native screen pool (frozen R3 rule)
    cand = _load("j4_screen_cand")
    res = _load("j4_screen_res")
    art = {}
    for g, row in zip(cand, res):
        if g["qid"] not in qids:
            continue
        best_i, best_f = None, -1.0
        for i, (cd, r) in enumerate(zip(g["codes"], row)):
            if cd and r["frac"] > best_f:
                best_i, best_f = i, r["frac"]
        if best_i is not None:
            r = row[best_i]
            art[g["qid"]] = {"qid": g["qid"], "code": g["codes"][best_i],
                             "frac": r["frac"], "n_tests": r["n_tests"],
                             "n_failed": r["n_tests"] - r["n_passed"]}
    missing = [q for q in qids if q not in art]
    if missing:
        print(f"{len(missing)} stratum problems without usable artifact "
              f"(excluded from TRACE, kept in other arms): {missing}")
    aq = [q for q in qids if q in art]

    traces = _load("j4_traces") or _persist(
        "j4_traces",
        h2_trace_capture.remote(aq, [art[q]["code"] for q in aq], tag="j4_traces"))
    tr_by = {t["qid"]: t for t in traces}
    for q in aq:
        art[q]["trace"] = {k: tr_by[q][k] for k in ("stdin", "expected", "actual")}

    sh = _load("j4_selfhints") or _persist(
        "j4_selfhints",
        h5_selfhint_gen.remote("deepseek-ai/deepseek-coder-1.3b-instruct", qids,
                               tag="j4_selfhints"))
    sh_by = {r["qid"]: r["selfhint"] for r in sh}

    items = ([{"qid": q, "context": None} for q in qids]
             + [{"qid": q, "context": _trace_context(art[q])} for q in aq]
             + [{"qid": q, "context": _hint_context(hints[q])} for q in qids]
             + [{"qid": q, "context": _hint_context(sh_by[q])} for q in qids])
    gen = _load("j4_arms_cand") or _persist(
        "j4_arms_cand",
        h1_gen_lcb.remote(FAMILIES["deepseek"], items, 50, tag="j4_arms_cand"))
    res4 = _load("j4_arms_res") or _persist(
        "j4_arms_res",
        h1_lcb_exec.remote([g["qid"] for g in gen], [g["codes"] for g in gen],
                           tag="j4_arms_res", short_circuit=True))
    n = len(qids)
    na = len(aq)
    seg = {"B1": (qids, res4[:n]), "TRACE": (aq, res4[n:n + na]),
           "HINT": (qids, res4[n + na:2 * n + na]),
           "SELFHINT": (qids, res4[2 * n + na:])}
    rec = {a: {q: any(r["passed"] for r in row) for q, row in zip(qs_, rows)}
           for a, (qs_, rows) in seg.items()}

    def mcn(xa, xb, universe):
        b = sum(1 for q in universe if rec[xb].get(q) and not rec[xa].get(q))
        c = sum(1 for q in universe if rec[xa].get(q) and not rec[xb].get(q))
        return {"arm_only": b, "base_only": c, "p": _mcnemar_one_sided(b, c)}

    out = {"_label": "J4 — DeepSeek four-arm stratum contrast [PHASE_5.md J4]",
           "n_stratum": n, "n_trace_arm": na,
           "recoveries": {a: sum(v.values()) for a, v in rec.items()},
           "contrasts": {
               "TRACE_vs_B1": mcn("B1", "TRACE", aq),
               "HINT_vs_B1": mcn("B1", "HINT", qids),
               "SELFHINT_vs_B1": mcn("B1", "SELFHINT", qids),
               "HINT_vs_TRACE": mcn("TRACE", "HINT", aq),
               "HINT_vs_SELFHINT": mcn("SELFHINT", "HINT", qids)},
           "floor_prediction_committed": 0.0,
           "recovered_qids": {a: sorted(q for q, v in rec[a].items() if v)
                              for a in rec}}
    (REPO / "artifacts/h5_deepseek_fourarm.json").write_text(json.dumps(out, indent=2))
    print(f"=== J4 arms: " + " | ".join(f"{a} {sum(v.values())}" for a, v in rec.items()))
    for k, v in out["contrasts"].items():
        print(f"  {k}: +{v['arm_only']}/-{v['base_only']} p={v['p']:.4f}")


@app.local_entrypoint()
def j4_validate():
    """J4 recovery validation: judge rerun on every recovered (arm, qid) row."""
    out4 = json.loads((REPO / "artifacts/h5_deepseek_fourarm.json").read_text())
    scr = json.loads((REPO / "artifacts/h5_deepseek_medium_screen.json").read_text())
    qids = scr["stratum_qids"]
    gen = _load("j4_arms_cand")
    n = len(qids)
    na = out4["n_trace_arm"]
    offs = {"B1": (0, qids), "TRACE": (n, qids[:na]), "HINT": (n + na, qids),
            "SELFHINT": (2 * n + na, qids)}
    sub = []
    for arm, rq in out4["recovered_qids"].items():
        off, universe = offs[arm]
        for q in rq:
            i = universe.index(q)
            sub.append((f"{arm}:{q}", gen[off + i]))
    rr = _load("j4_res_rerun") or _persist(
        "j4_res_rerun",
        h1_lcb_exec.remote([g["qid"] for _, g in sub], [g["codes"] for _, g in sub],
                           tag="j4_res_rerun", short_circuit=True))
    stable = {key: bool(any(r["passed"] for r in row)) for (key, _), row in zip(sub, rr)}
    ok = sum(stable.values())
    (REPO / "artifacts/h5_deepseek_rerun.json").write_text(json.dumps(stable, indent=1))
    print(f"rerun stability: {ok}/{len(stable)} recovered rows reproduce: {stable}")


@app.local_entrypoint()
def h2a_validate():
    """Recovery validation for the amended stratum run: judge rerun on the
    recovered problems' HINT rows (fresh tag), stability per recovery."""
    res = json.loads((REPO / "runs/modal/h2a_res.json").read_text())
    gen = json.loads((REPO / "runs/modal/h2a_cand.json").read_text())
    n = 68
    rec = json.loads((REPO / "artifacts/h2a_hint_arm.json").read_text())["recovered_qids"]["hint"]
    sub = [(g["qid"], g["codes"]) for g in gen[n:] if g["qid"] in rec]
    rr = _load("h2a_res_rerun") or _persist(
        "h2a_res_rerun",
        h1_lcb_exec.remote([q for q, _ in sub], [c for _, c in sub],
                           tag="h2a_res_rerun", short_circuit=True))
    first = {g["qid"]: row for g, row in zip(gen[n:], res[n:])}
    stable = {}
    for (qid, _), row2 in zip(sub, rr):
        p1 = {i for i, r in enumerate(first[qid]) if r["passed"]}
        p2 = {i for i, r in enumerate(row2) if r["passed"]}
        stable[qid] = {"first_pass_idx": sorted(p1), "rerun_pass_idx": sorted(p2),
                       "stable": bool(p1 & p2)}
    ok = sum(1 for v in stable.values() if v["stable"])
    print(f"rerun stability: {ok}/{len(stable)} recoveries reproduce")
    (REPO / "artifacts/h2a_rerun_stability.json").write_text(
        json.dumps(stable, indent=1))


@app.local_entrypoint()
def h2b_band():
    """H2b near-miss band: 39 problems x {B1-25, TRACE-25, HINT-25}, all fresh."""
    fz = _h2_frozen()
    qids = fz["groups"]["near_miss"]
    hints = fz["hints"]

    # artifact per problem: highest-frac FAILING candidate from the run-config pool
    pools = {
        "easy": ("lcb_cand_lcb_r2_base_T08.json", "lcb_res_lcb_r2_base_T08.json"),
        "medium": ("lcb_cand_lcb_r2_base_medium_T08.json",
                   "lcb_res_lcb_r2_base_medium_T08.json"),
    }
    art = {}
    for _, (cf, rf) in pools.items():
        cand = json.loads((REPO / "runs/modal" / cf).read_text())
        res = json.loads((REPO / "runs/modal" / rf).read_text())
        for qid, crow, rrow in zip(res["question_ids"], cand["codes"], res["results"]):
            if qid not in qids or qid in art:
                continue
            best_i, best_f = None, -1.0
            for i, (cd, r) in enumerate(zip(crow, rrow)):
                if cd and not r["passed"] and r["frac"] > best_f:
                    best_i, best_f = i, r["frac"]
            if best_i is not None:
                r = rrow[best_i]
                art[qid] = {"qid": qid, "code": crow[best_i], "frac": r["frac"],
                            "n_tests": r["n_tests"],
                            "n_failed": r["n_tests"] - r["n_passed"]}
    missing = [q for q in qids if q not in art]
    if missing:
        print(f"no failing artifact for {missing} (excluded, counted)")
    aq = [q for q in qids if q in art]

    traces = _load("h2b_traces") or _persist(
        "h2b_traces",
        h2_trace_capture.remote(aq, [art[q]["code"] for q in aq], tag="h2b_traces"))
    tr_by = {t["qid"]: t for t in traces}
    for q in aq:
        art[q]["trace"] = {k: tr_by[q][k] for k in ("stdin", "expected", "actual")}

    items = ([{"qid": q, "context": None} for q in aq]
             + [{"qid": q, "context": _trace_context(art[q])} for q in aq]
             + [{"qid": q, "context": _hint_context(hints[q])} for q in aq])
    gen = _load("h2b_cand") or _persist(
        "h2b_cand", h1_gen_lcb.remote(QWEN_BASE, items, 25, tag="h2b_cand"))
    res = _load("h2b_res") or _persist(
        "h2b_res",
        h1_lcb_exec.remote([g["qid"] for g in gen], [g["codes"] for g in gen],
                           tag="h2b_res", short_circuit=True))
    n = len(aq)
    arms = {"B1": res[:n], "TRACE": res[n:2 * n], "HINT": res[2 * n:]}
    rec = {a: [any(r["passed"] for r in row) for row in rows]
           for a, rows in arms.items()}
    out = {"_label": "H2b near-miss band — B1/TRACE/HINT k=25, all fresh [PHASE_4.md H2b]",
           "n": n, "excluded_no_artifact": missing,
           "recoveries": {a: sum(v) for a, v in rec.items()},
           "contrasts": {}}
    for a in ("TRACE", "HINT"):
        b = sum(1 for x, y in zip(rec["B1"], rec[a]) if y and not x)
        c = sum(1 for x, y in zip(rec["B1"], rec[a]) if x and not y)
        out["contrasts"][f"{a}_vs_B1"] = {
            "arm_only": b, "b1_only": c, "p_one_sided_mcnemar": _mcnemar_one_sided(b, c)}
    # per-tier (min-x) reporting
    nmc = fz["near_miss_cells"]
    tiers = {q: min(nmc[q].values()) for q in aq}
    out["per_tier"] = {
        str(t): {a: sum(1 for q, v in zip(aq, rec[a]) if tiers[q] == t and v)
                 for a in rec} | {"n": sum(1 for q in aq if tiers[q] == t)}
        for t in sorted(set(tiers.values()))}
    out["recovered_qids"] = {a: [q for q, v in zip(aq, rec[a]) if v] for a in rec}
    (REPO / "artifacts/h2b_near_miss.json").write_text(json.dumps(out, indent=2))
    print(f"=== H2b: n={n} | " + " ".join(f"{a} {sum(v)}" for a, v in rec.items())
          + " | " + json.dumps(out["contrasts"]) + " ===")


@app.local_entrypoint()
def h2_dump_questions():
    """Dump statements for the H2 target sets (medium stratum + near-miss +
    manipulation-check band) to runs/modal/h2_questions.json."""
    med = json.loads((REPO / "runs/modal/lcb_res_lcb_r2_base_medium_T08.json").read_text())
    qids = set()
    for qid, row in zip(med["question_ids"], med["results"]):
        if not any(c["passed"] for c in row):
            qids.add(qid)
    cells = ["lcb_res_lcb_r2_base_T08.json", "lcb_res_lcb_r2_base_T10.json",
             "lcb_res_lcb_r2_base_T12.json", "lcb_res_lcb_r2_instruct_T12.json",
             "lcb_res_lcb_r2_base_medium_T08.json"]
    for f in cells:
        d = json.loads((REPO / "runs/modal" / f).read_text())
        for qid, row in zip(d["question_ids"], d["results"]):
            x = sum(1 for c in row if c["passed"])
            if x in (1, 2):
                qids.add(qid)
    easy = json.loads((REPO / "runs/modal/lcb_res_lcb_r2_base_T08.json").read_text())
    band = sorted(
        ((qid, sum(1 for c in row if c["passed"]))
         for qid, row in zip(easy["question_ids"], easy["results"])),
        key=lambda t: (abs(t[1] - 25), t[0]))
    qids |= {qid for qid, x in band[:20] if 10 <= x <= 40}
    out = h1_dump_questions.remote(sorted(qids))
    _persist("h2_questions", out)
    print(f"dumped {len(out['questions'])} questions; columns: {out['columns']}")


@app.local_entrypoint()
def h1_smoke(family: str = "deepseek"):
    """Per-family smoke gate: 8 LCB-easy x 8, frozen scaffold.
    Gate: well-formed >= 0.85, degenerate <= 0.10."""
    mid = FAMILIES[family]
    qids = _lcb_easy_qids()[:8]
    items = [{"qid": q, "context": None} for q in qids]
    gen = _load(f"h1_smoke_cand_{family}") or _persist(
        f"h1_smoke_cand_{family}",
        h1_gen_lcb.remote(mid, items, 8, tag=f"smoke_cand_{family}"))
    codes = [g["codes"] for g in gen]
    flat = [c for row in codes for c in row]
    wf = sum(1 for c in flat if c) / len(flat)
    dg = sum(1 for c in flat if c and len(c) < 20) / max(1, sum(1 for c in flat if c))
    res = _load(f"h1_smoke_res_{family}") or _persist(
        f"h1_smoke_res_{family}",
        h1_lcb_exec.remote([g["qid"] for g in gen], codes,
                           tag=f"smoke_res_{family}"))
    fracs = [r["frac"] for row in res for r in row]
    npass = sum(1 for row in res for r in row if r["passed"])
    ok = wf >= 0.85 and dg <= 0.10
    out = {"_label": f"H1 smoke gate — {family} ({mid})", "n": len(flat),
           "well_formed": wf, "degenerate": dg,
           "mean_frac": sum(fracs) / len(fracs), "n_passed_candidates": npass,
           "gate": "PASS" if ok else "FAIL"}
    (REPO / f"artifacts/h1_smoke_{family}.json").write_text(json.dumps(out, indent=2))
    sample = next((c for c in flat if c), "")[:400]
    print(f"=== H1 smoke {family}: wf {wf:.3f} dg {dg:.3f} "
          f"mean_frac {out['mean_frac']:.3f} passed {npass}/{len(flat)} → {out['gate']} ===")
    print("sample:\n" + sample)


@app.local_entrypoint()
def h1_battery(family: str = "deepseek"):
    """Cells (ii) LCB-easy, (i) BCB, (iii/iv) D2c E0/E1 — resume-safe."""
    mid = FAMILIES[family]

    # cell (ii) — LCB-easy 80 x 50, short-circuit judge
    qids = _lcb_easy_qids()
    gen = _load(f"h1_cand_lcb_{family}") or _persist(
        f"h1_cand_lcb_{family}",
        h1_gen_lcb.remote(mid, [{"qid": q, "context": None} for q in qids], 50,
                          tag=f"cand_lcb_{family}"))
    res = _load(f"h1_res_lcb_{family}") or _persist(
        f"h1_res_lcb_{family}",
        h1_lcb_exec.remote([g["qid"] for g in gen], [g["codes"] for g in gen],
                           tag=f"res_lcb_{family}", short_circuit=True))
    print(f"[{family}] LCB cell judged ({len(res)} problems)")

    # cell (i) — BCB 200 x 50
    bgen = _load(f"h1_cand_bcb_{family}") or _persist(
        f"h1_cand_bcb_{family}", h1_gen_bcb.remote(mid, tag=f"cand_bcb_{family}"))
    bres = _load(f"h1_res_bcb_{family}") or _persist(
        f"h1_res_bcb_{family}",
        h1_bcb_exec.remote(bgen["problems"], tag=f"res_bcb_{family}"))
    print(f"[{family}] BCB cell judged ({len(bres)} problems)")

    # cell (iii/iv) — D2c E0/E1, k=8, all-cases
    arts = _d2c_artifacts()
    items = ([{"qid": a["qid"], "context": None} for a in arts]
             + [{"qid": a["qid"], "context": _d2c_context(a)} for a in arts])
    dgen = _load(f"h1_cand_d2c_{family}") or _persist(
        f"h1_cand_d2c_{family}",
        h1_gen_lcb.remote(mid, items, 8, tag=f"cand_d2c_{family}"))
    dres = _load(f"h1_res_d2c_{family}") or _persist(
        f"h1_res_d2c_{family}",
        h1_lcb_exec.remote([g["qid"] for g in dgen], [g["codes"] for g in dgen],
                           tag=f"res_d2c_{family}"))
    print(f"[{family}] D2c cell judged ({len(dres)} rows: 44 E0 + 44 E1)")
    print(f"[{family}] battery complete — run h1_report")


@app.local_entrypoint()
def h1_report():
    """Aggregate all persisted cells → per-finding verdicts per the pre-reg."""
    import difflib
    import random
    import statistics as st

    def wilcoxon_mc_one_sided(diffs, trials=20000, seed=17):
        """P(mean signed diff <= observed) under sign-flip null (as committed)."""
        rng = random.Random(seed)
        obs = sum(diffs) / len(diffs)
        hits = 0
        for _ in range(trials):
            s = sum(d if rng.random() < 0.5 else -d for d in diffs) / len(diffs)
            if s <= obs:
                hits += 1
        return (hits + 1) / (trials + 1)

    arts = _d2c_artifacts()
    out = {"_label": "H1 — cross-family battery results [PHASE_4.md H1]",
           "families": {}}
    for family, mid in FAMILIES.items():
        f = {"model": mid}
        res = _load(f"h1_res_lcb_{family}")
        if res:
            counts = [(len(r), sum(x["passed"] for x in r)) for r in res]
            f["lcb_easy"] = {
                "pass@1": st.mean(c / n for n, c in counts),
                "pass@8": st.mean(_pass_at_k(n, c, 8) for n, c in counts),
                "pass@50": st.mean(_pass_at_k(n, c, 50) for n, c in counts),
            }
            f["lcb_easy"]["headroom"] = f["lcb_easy"]["pass@50"] - f["lcb_easy"]["pass@8"]
        bres = _load(f"h1_res_bcb_{family}")
        if bres:
            counts = [(len(r), sum(x["passed"] for x in r)) for r in bres]
            f["bcb"] = {
                "pass@1": st.mean(c / n for n, c in counts),
                "pass@8": st.mean(_pass_at_k(n, c, 8) for n, c in counts),
                "pass@50": st.mean(_pass_at_k(n, c, 50) for n, c in counts),
            }
            f["bcb"]["headroom"] = f["bcb"]["pass@50"] - f["bcb"]["pass@8"]
        dgen, dres = _load(f"h1_cand_d2c_{family}"), _load(f"h1_res_d2c_{family}")
        if dgen and dres:
            n = len(arts)
            e0g, e1g = dgen[:n], dgen[n:]
            e0r, e1r = dres[:n], dres[n:]
            e0_frac = [st.mean(x["frac"] for x in row) for row in e0r]
            e1_frac = [st.mean(x["frac"] for x in row) for row in e1r]
            def pulls(gens):
                ms = []
                for a, g in zip(arts, gens):
                    ps = [1.0 - difflib.SequenceMatcher(None, c, a["code"]).ratio()
                          for c in g["codes"] if c]
                    if ps:
                        ms.append(st.mean(ps))
                return ms
            e0_pull, e1_pull = pulls(e0g), pulls(e1g)
            diffs = [b - a for a, b in zip(e0_frac, e1_frac)]
            f["d2c"] = {
                "e0_mean_frac_iid_null": st.mean(e0_frac),
                "e1_mean_frac_conditioned": st.mean(e1_frac),
                "copy_null_artifact_frac": st.mean(a["frac"] for a in arts),
                "delta_conditioned_minus_iid": st.mean(diffs),
                "p_one_sided_sink": wilcoxon_mc_one_sided(diffs),
                "e0_anchor_pull": st.mean(e0_pull),
                "e1_conditioned_pull": st.mean(e1_pull),
                "form_holds_pull": st.mean(e1_pull) < 0.8 * st.mean(e0_pull),
            }
        out["families"][family] = f
    qwen = {"lcb_easy": {"pass@8": 0.5658, "pass@50": 0.7625, "headroom": 0.1967},
            "bcb": {"pass@8": 0.3280, "pass@50": 0.4250, "headroom": 0.0970},
            "d2c": {"e1_conditioned_frac": 0.374, "qwen_iid_null": 0.468,
                    "copy_null": 0.494, "e0_anchor_pull": 0.774,
                    "e1_conditioned_pull": 0.430}}
    out["qwen_reference"] = qwen
    (REPO / "artifacts/h1_cross_family.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
    print("wrote artifacts/h1_cross_family.json")


# ========================================================================
# Phase 6 P1 — pathology-origin discriminator battery ([PHASE_6.md] P1).
# The two frozen J5 Q1 cells (D2c code + language manipulation), pointed at
# new checkpoints via J6_MODELS. Additive: the frozen j5_* entrypoints and
# their committed 7B outputs are untouched; every tag/output here is
# namespaced by the model short-name, and the model load is revision-pinned.
# ========================================================================

def _j6_model(name):
    if name not in J6_MODELS:
        raise SystemExit(f"unknown checkpoint '{name}'; choose from {list(J6_MODELS)}")
    return J6_MODELS[name]


@app.function(image=DL_IMAGE, volumes={"/cache": VOL}, timeout=3600)
def j6_download(model_id: str, revision: str):
    from huggingface_hub import snapshot_download
    print("downloading", model_id, "@", revision)
    snapshot_download(model_id, revision=revision)
    VOL.commit()
    return {"model": model_id, "revision": revision}


@app.local_entrypoint()
def j6_prefetch(name: str = "qwen3b"):
    """Fetch + revision-pin one P1 checkpoint to the volume cache."""
    model_id, rev = _j6_model(name)
    print(j6_download.remote(model_id, rev))


@app.local_entrypoint()
def j6_smoke(name: str = "qwen3b"):
    """Per-checkpoint smoke gate (charter): 8 LCB-easy x 8, wf>=0.85 dg<=0.10."""
    model_id, rev = _j6_model(name)
    qids = _lcb_easy_qids()[:8]
    gen = _load(f"j6_smoke_cand_{name}") or _persist(
        f"j6_smoke_cand_{name}",
        h1_gen_lcb.remote(model_id, [{"qid": q, "context": None} for q in qids], 8,
                          tag=f"j6_smoke_cand_{name}", revision=rev))
    codes = [g["codes"] for g in gen]
    flat = [c for row in codes for c in row]
    wf = sum(1 for c in flat if c) / len(flat)
    dg = sum(1 for c in flat if c and len(c) < 20) / max(1, sum(1 for c in flat if c))
    res = _load(f"j6_smoke_res_{name}") or _persist(
        f"j6_smoke_res_{name}",
        h1_lcb_exec.remote([g["qid"] for g in gen], codes,
                           tag=f"j6_smoke_res_{name}", short_circuit=True))
    npass = sum(1 for row in res for r in row if r["passed"])
    ok = wf >= 0.85 and dg <= 0.10
    print(f"=== j6 smoke ({name} = {model_id} @ {rev[:12]}): wf {wf:.3f} dg {dg:.3f} "
          f"passed {npass}/{len(flat)} → {'PASS' if ok else 'FAIL'} ===")
    print("sample:\n" + next((c for c in flat if c), "")[:300])


@app.local_entrypoint()
def j6_pathology(name: str = "qwen3b"):
    """P1 — the two frozen cells on one checkpoint (run j6_smoke first).
    Q1a D2c code cell (44 x {E0,E1} x 8, all-cases judge, mean frac);
    Q1b language cell (20 x {E0,HINT} x 25, per-sample mean pass).
    Writes artifacts/h6_pathology_origin_<name>.json (blend geometry +
    language band); raw pools persist to runs/modal/j6_* for the free-rider
    copy-fidelity/size-curve analysis."""
    import statistics as st
    model_id, rev = _j6_model(name)

    # Q1a — D2c code-conditioning cell (blend geometry: cond vs iid vs copy)
    arts = _d2c_artifacts()
    items = ([{"qid": a["qid"], "context": None} for a in arts]
             + [{"qid": a["qid"], "context": _d2c_context(a)} for a in arts])
    dgen = _load(f"j6_q1a_cand_{name}") or _persist(
        f"j6_q1a_cand_{name}",
        h1_gen_lcb.remote(model_id, items, 8, tag=f"j6_q1a_cand_{name}", revision=rev))
    dres = _load(f"j6_q1a_res_{name}") or _persist(
        f"j6_q1a_res_{name}",
        h1_lcb_exec.remote([g["qid"] for g in dgen], [g["codes"] for g in dgen],
                           tag=f"j6_q1a_res_{name}"))
    n = len(arts)
    e0_frac = [st.mean(x["frac"] for x in row) for row in dres[:n]]
    e1_frac = [st.mean(x["frac"] for x in row) for row in dres[n:]]
    copy_null = [a["frac"] for a in arts]
    d_iid = [b - a for a, b in zip(e0_frac, e1_frac)]
    d_copy = [b - a for a, b in zip(copy_null, e1_frac)]
    p_sink_iid = _wilcoxon_mc_one_sided([-x for x in d_iid])
    p_sink_copy = _wilcoxon_mc_one_sided([-x for x in d_copy])
    q1a = {"e0_mean_frac_iid": st.mean(e0_frac), "e1_mean_frac_cond": st.mean(e1_frac),
           "copy_null_mean": st.mean(copy_null),
           "delta_cond_minus_iid": st.mean(d_iid),
           "delta_cond_minus_copy": st.mean(d_copy),
           "p_one_sided_cond_below_iid": p_sink_iid,
           "p_one_sided_cond_below_copy": p_sink_copy}
    print(f"Q1a ({name}): iid {q1a['e0_mean_frac_iid']:.3f} | cond "
          f"{q1a['e1_mean_frac_cond']:.3f} | copy {q1a['copy_null_mean']:.3f} | "
          f"p_below_iid {p_sink_iid:.4f} p_below_copy {p_sink_copy:.4f}")

    # Q1b — language-channel cell (harm vanish/persist band)
    fz = _h2_frozen()
    qids = fz["groups"]["manip_check"]
    hints = fz["hints"]
    items = ([{"qid": q, "context": None} for q in qids]
             + [{"qid": q, "context": _hint_context(hints[q])} for q in qids])
    mgen = _load(f"j6_q1b_cand_{name}") or _persist(
        f"j6_q1b_cand_{name}",
        h1_gen_lcb.remote(model_id, items, 25, tag=f"j6_q1b_cand_{name}", revision=rev))
    mres = _load(f"j6_q1b_res_{name}") or _persist(
        f"j6_q1b_res_{name}",
        h1_lcb_exec.remote([g["qid"] for g in mgen], [g["codes"] for g in mgen],
                           tag=f"j6_q1b_res_{name}", short_circuit=True))
    m = len(qids)
    e0 = [sum(r["passed"] for r in row) / len(row) for row in mres[:m]]
    hi = [sum(r["passed"] for r in row) / len(row) for row in mres[m:]]
    diffs = [b - a for a, b in zip(e0, hi)]
    q1b = {"e0_mean_pass": st.mean(e0), "hint_mean_pass": st.mean(hi),
           "mean_uplift": st.mean(diffs),
           "p_one_sided_uplift": _wilcoxon_mc_one_sided(diffs),
           "saturation_caveat": st.mean(e0) > 0.9}
    print(f"Q1b ({name}): E0 {q1b['e0_mean_pass']:.3f} → HINT {q1b['hint_mean_pass']:.3f} "
          f"(Δ {q1b['mean_uplift']:+.3f}, p {q1b['p_one_sided_uplift']:.4f})"
          + ("  [SATURATED >0.9 — compressed cell]" if q1b["saturation_caveat"] else ""))

    out = {"_label": f"Phase 6 P1 — pathology origin cell, {name} [PHASE_6.md P1]",
           "model": model_id, "revision": rev,
           "q1a_d2c": q1a, "q1b_language": q1b}
    (REPO / f"artifacts/h6_pathology_origin_{name}.json").write_text(
        json.dumps(out, indent=2))
    print(f"wrote artifacts/h6_pathology_origin_{name}.json")


@app.local_entrypoint()
def j6_p2_distinct_seed():
    """P2 — distinct-seed fresh B1-50 on the frozen Qwen 68-problem medium
    stratum ([PHASE_6.md] P2; the floor instrument's 6th out-of-sample test,
    first under a satisfied fresh-draw premise). Committed prediction (frozen
    in scripts/j6_p2_floor_predict.py): E = 2.01, point 2, band [0,4],
    >=5 falsifies. Seed 41 (distinct from the record's 17); revision-pinned
    (the medium screen predates revision-pinning, so under D14's statistical
    standard the intended difference from the screen is the seed). The committed
    prediction is fit from the screen pool's own near-miss counts and is
    therefore seed/revision-agnostic."""
    fz = _h2_frozen()
    qids = fz["groups"]["stratum_medium"]
    assert len(qids) == 68, f"stratum {len(qids)} != 68"
    items = [{"qid": q, "context": None} for q in qids]
    gen = _load("j6_p2_b1_cand") or _persist(
        "j6_p2_b1_cand",
        h1_gen_lcb.remote(QWEN_BASE, items, 50, tag="j6_p2_b1_cand",
                          seed=P2_SEED, revision=QWEN_BASE_REV))
    res = _load("j6_p2_b1_res") or _persist(
        "j6_p2_b1_res",
        h1_lcb_exec.remote([g["qid"] for g in gen], [g["codes"] for g in gen],
                           tag="j6_p2_b1_res", short_circuit=True))
    rec = [any(r["passed"] for r in row) for row in res]
    n_rec = sum(rec)
    verdict = ("in-band" if n_rec <= 4 else "FALSIFIES-high(>=5)")

    # Distinct-seed protocol validation (informational): confirm this arm is NOT
    # ~50% byte-identical to the same-seed screen pool (the J5 confound).
    ident = None
    try:
        scr = json.loads(
            (REPO / "runs/modal/lcb_cand_lcb_r2_base_medium_T08.json").read_text())
        res0 = json.loads(
            (REPO / "runs/modal/lcb_res_lcb_r2_base_medium_T08.json").read_text())
        scr_by_qid = dict(zip(res0["question_ids"], scr["codes"]))
        same = tot = 0
        for g in gen:
            base = set(c for c in (scr_by_qid.get(g["qid"]) or []) if c)
            for c in g["codes"]:
                tot += 1
                if c and c in base:
                    same += 1
        ident = same / tot if tot else None
    except Exception as e:  # noqa: BLE001 — validation only, never blocks the verdict
        ident = f"unavailable ({e})"

    out = {"_label": "Phase 6 P2 — distinct-seed fresh B1-50, Qwen medium stratum "
                     "[PHASE_6.md P2; floor instrument 6th out-of-sample test]",
           "model": QWEN_BASE, "revision": QWEN_BASE_REV, "seed": P2_SEED,
           "n_stratum": len(qids), "recoveries": n_rec,
           "committed_prediction": {"E": 2.01, "point": 2, "band_94pct": [0, 4],
                                    "falsifies_high": 5,
                                    "source": "scripts/j6_p2_floor_predict.py"},
           "verdict": verdict,
           "identical_to_screen_frac": ident,
           "recovered_qids": [q for q, v in zip(qids, rec) if v]}
    (REPO / "artifacts/h6_p2_distinct_seed_b1.json").write_text(json.dumps(out, indent=2))
    print(f"=== P2 distinct-seed B1-50 (seed {P2_SEED}): {n_rec} recoveries — "
          f"committed band [0,4], >=5 falsifies → {verdict} "
          f"(identical-to-screen {ident}) ===")


# ========================================================================
# Phase 7 P1 — the matched-artifact battery ([PHASE_7.md] P1) + the P0.3
# stack-fingerprint hook. Each cell conditions ONE model on artifacts MINED to
# its own quality match (Delta_art ~ 0; scripts/j7_match_artifacts.py) plus its
# own iid (E0) on the SAME problems. Code channel only (the relational axis is
# defined on frac; no language analogue). Additive: frozen j5_*/j6_* untouched.
# ========================================================================

def _j7_model(cell):
    if cell not in J7_MODELS:
        raise SystemExit(f"unknown cell '{cell}'; choose from {list(J7_MODELS)}")
    return J7_MODELS[cell]


def _stack_hashes():
    """P0.3(b) local half of the stack fingerprint: content hashes of the frozen
    generation template, the D2c context wording, and the judge — so a silent
    change to any is detectable in every Phase-7 artifact. Read from the module
    source via ast (robust to the @app.function decorators)."""
    import ast
    import hashlib
    src = Path(__file__).read_text()
    tree = ast.parse(src)
    segs = {n.name: ast.get_source_segment(src, n)
            for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}

    def h(name):
        return hashlib.sha256(segs[name].encode()).hexdigest()[:16]

    return {"gen_template_hash": h("h1_gen_lcb"),
            "d2c_context_hash": h("_d2c_context"),
            "judge_hash": h("h1_lcb_exec")}


@app.function(image=GEN_IMAGE, gpu="L4", volumes={"/cache": VOL}, timeout=600)
def j7_fingerprint():
    """P0.3(b) remote half: the runtime stack the gen cells actually ran on."""
    import torch
    import vllm
    p = torch.cuda.get_device_properties(0)
    return {"gpu_name": p.name, "gpu_capability": f"{p.major}.{p.minor}",
            "dtype": "bfloat16", "torch": torch.__version__,
            "cuda": torch.version.cuda, "vllm": vllm.__version__}


def _stack_block():
    """Full stack fingerprint (remote versions + local content hashes), cached."""
    fp = _load("j7_stack_fp") or _persist("j7_stack_fp", j7_fingerprint.remote())
    return {**fp, **_stack_hashes()}


@app.local_entrypoint()
def j7_prefetch(cell: str = "M1_deepseek1p3b"):
    """Fetch + revision-pin one matched-battery model to the volume cache."""
    model_id, rev = _j7_model(cell)
    print(j6_download.remote(model_id, rev))


@app.local_entrypoint()
def j7_smoke(cell: str = "M1_deepseek1p3b"):
    """Per-cell smoke gate (charter): 8 LCB-easy x 8, wf>=0.85 dg<=0.10."""
    model_id, rev = _j7_model(cell)
    qids = _lcb_easy_qids()[:8]
    gen = _load(f"j7_smoke_cand_{cell}") or _persist(
        f"j7_smoke_cand_{cell}",
        h1_gen_lcb.remote(model_id, [{"qid": q, "context": None} for q in qids], 8,
                          tag=f"j7_smoke_cand_{cell}", revision=rev))
    codes = [g["codes"] for g in gen]
    flat = [c for row in codes for c in row]
    wf = sum(1 for c in flat if c) / len(flat)
    dg = sum(1 for c in flat if c and len(c) < 20) / max(1, sum(1 for c in flat if c))
    res = _load(f"j7_smoke_res_{cell}") or _persist(
        f"j7_smoke_res_{cell}",
        h1_lcb_exec.remote([g["qid"] for g in gen], codes,
                           tag=f"j7_smoke_res_{cell}", short_circuit=True))
    npass = sum(1 for row in res for r in row if r["passed"])
    ok = wf >= 0.85 and dg <= 0.10
    print(f"=== j7 smoke ({cell} = {model_id} @ {rev[:12]}): wf {wf:.3f} dg {dg:.3f} "
          f"passed {npass}/{len(flat)} → {'PASS' if ok else 'FAIL'} ===")
    print("sample:\n" + next((c for c in flat if c), "")[:300])


@app.local_entrypoint()
def j7_matched(cell: str = "M1_deepseek1p3b"):
    """P1 matched-artifact code cell (run j7_smoke first). Condition <model> on
    its MINED matched artifacts (Delta_art ~ 0) x8, all-cases judge, vs its own
    iid (E0) on the SAME problems. Matched-sink signature (pre-registered):
    cond mean frac < own iid, one-sided MC-Wilcoxon p < 0.05, AND effect <= -0.05
    (the depth threshold that keeps 'sink' distinct from imitation drag). Copy-null
    (artifact frac) reported for the record but the two nulls converge at match.
    Writes artifacts/h7_matched_<cell>.json with the stack fingerprint block."""
    import statistics as st
    model_id, rev = _j7_model(cell)
    matched = json.loads((REPO / "artifacts/h7_matched_artifacts.json").read_text())
    cinfo = matched["cells"][cell]
    arts = cinfo["artifacts"]
    n = len(arts)
    if n == 0:
        raise SystemExit(f"cell {cell} has no mined artifacts")

    items = ([{"qid": a["qid"], "context": None} for a in arts]
             + [{"qid": a["qid"], "context": _d2c_context(a)} for a in arts])
    dgen = _load(f"j7_cand_{cell}") or _persist(
        f"j7_cand_{cell}",
        h1_gen_lcb.remote(model_id, items, 8, tag=f"j7_cand_{cell}", revision=rev))
    dres = _load(f"j7_res_{cell}") or _persist(
        f"j7_res_{cell}",
        h1_lcb_exec.remote([g["qid"] for g in dgen], [g["codes"] for g in dgen],
                           tag=f"j7_res_{cell}"))
    e0_frac = [st.mean(x["frac"] for x in row) for row in dres[:n]]
    e1_frac = [st.mean(x["frac"] for x in row) for row in dres[n:]]
    copy_null = [a["frac"] for a in arts]
    d_iid = [b - a for a, b in zip(e0_frac, e1_frac)]
    d_copy = [b - a for a, b in zip(copy_null, e1_frac)]
    p_sink_iid = _wilcoxon_mc_one_sided([-x for x in d_iid])
    mean_e0, mean_e1, mean_copy = st.mean(e0_frac), st.mean(e1_frac), st.mean(copy_null)
    effect = mean_e1 - mean_e0
    # bootstrap 95% CI on the paired cond-minus-iid effect (deterministic seed)
    import random
    rng = random.Random(17)
    boot = sorted(st.mean(rng.choice(d_iid) for _ in d_iid) for _ in range(2000))
    ci = [round(boot[49], 4), round(boot[1949], 4)]
    matched_sink = bool(mean_e1 < mean_e0 and p_sink_iid < 0.05 and effect <= -0.05)

    out = {"_label": f"Phase 7 P1 — matched-artifact code cell, {cell} [PHASE_7.md P1]",
           "cell": cell, "model": model_id, "revision": rev,
           "n_problems": n, "min_n_met": cinfo["min_n_met"],
           "target_iid": cinfo["target_iid"], "diet": cinfo["diet"],
           "mean_iid_e0": round(mean_e0, 4), "mean_cond_e1": round(mean_e1, 4),
           "mean_copy_null": round(mean_copy, 4),
           "delta_cond_minus_iid": round(effect, 4),
           "delta_cond_minus_iid_ci95": ci,
           "actual_delta_art": round(mean_copy - mean_e0, 4),
           "delta_cond_minus_copy": round(mean_e1 - mean_copy, 4),
           "p_one_sided_cond_below_iid": p_sink_iid,
           "matched_sink_signature": matched_sink,
           "stack": _stack_block()}
    (REPO / f"artifacts/h7_matched_{cell}.json").write_text(json.dumps(out, indent=2))
    print(f"=== j7 matched ({cell}): iid {mean_e0:.3f} → cond {mean_e1:.3f} "
          f"(copy {mean_copy:.3f}) | Δvs_iid {effect:+.3f} CI {ci} "
          f"| actual Δart {mean_copy-mean_e0:+.3f} | p_below_iid {p_sink_iid:.4f} "
          f"| MATCHED-SINK {matched_sink} (n={n}"
          f"{'' if cinfo['min_n_met'] else ' <MIN_N — underpowered'}) ===")


# ========================================================================
# Phase 8 — mechanism (D3 perplexity) + confound closures (C2/C3/C4)
# ([PHASE_8.md]). Additive; reuses h1_gen_lcb / h1_lcb_exec / _d2c_* / _stack_block.
# ========================================================================

PHI1 = "microsoft/phi-1"
PHI1_REV = "d4c0adcb065e84e00ca814e35cba3012ea9841ab"  # synthetic code pedagogy (C3)

# C-cell -> (model_id, revision, seed). DeepSeek/Coder7B reuse the P0.1 pins;
# C4 uses a DISTINCT seed (43) from the M4 run (17) per the distinct-seed protocol.
J8_CELLS = {
    "C2_deepseek_below0": ("deepseek-ai/deepseek-coder-1.3b-base",
                           "c919139c3a9b4070729c8b2cca4847ab29ca8d94", 17),
    "C4_coder7b_widerN":  ("Qwen/Qwen2.5-Coder-7B",
                           "0396a76181e127dfc13e5c5ec48a8cee09938b02", 43),
}

PPL_IMAGE = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("torch==2.8.0", "transformers==4.57.0", "accelerate")
    .env({"HF_HOME": "/cache/hf", "TOKENIZERS_PARALLELISM": "false",
          "HF_HUB_OFFLINE": "1", "HF_DATASETS_OFFLINE": "1"})
)


@app.function(image=PPL_IMAGE, gpu="L4", volumes={"/cache": VOL}, timeout=3600)
def j8_ppl(model_id: str, revision: str, groups: dict, tag: str):
    """D3 — mean per-token NLL of `model_id` on each group of code strings.
    Returns {group: {mean_nll, n_seqs}}. Blunt exemplar-credibility proxy."""
    def compute():
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        tok = AutoTokenizer.from_pretrained(model_id, revision=revision)
        model = AutoModelForCausalLM.from_pretrained(
            model_id, revision=revision, torch_dtype=torch.bfloat16).to("cuda").eval()
        out = {}
        for name, codes in groups.items():
            nlls = []
            for c in codes:
                if not c:
                    continue
                ids = tok(c, return_tensors="pt", truncation=True,
                          max_length=1024).input_ids.to("cuda")
                if ids.shape[1] < 2:
                    continue
                with torch.no_grad():
                    nlls.append(float(model(ids, labels=ids).loss))
            out[name] = {"mean_nll": (sum(nlls) / len(nlls)) if nlls else None,
                         "n_seqs": len(nlls)}
        return out
    return _cache_or(tag, compute)


def _e0_codes(cand_pool, n):
    """Flatten the E0 (first n) half of a gen cand pool into code strings."""
    return [c for row in cand_pool[:n] for c in row["codes"] if c]


@app.local_entrypoint()
def j8_d3():
    """D3 — artifact perplexity probe ([PHASE_8.md] D3; now DECISIVE per the D-rule).
    For each cell's model: mean NLL on (a) its conditioning artifacts, (b) its own E0
    generations (self-baseline). RECLASS => Coder models find matched artifacts as
    UNSURPRISING as their own output (surprise_ratio ~ 1) yet sink; OOD => elevated
    surprise on matched artifacts for Coder vs non-Coder. Writes h8_d3_perplexity.json."""
    d2c = _d2c_artifacts()
    d2c_codes = [a["code"] for a in d2c]
    h7 = json.loads((REPO / "artifacts/h7_matched_artifacts.json").read_text())["cells"]
    donor_cand = json.loads(
        (REPO / "runs/modal/lcb_cand_lcb_r2_base_T08.json").read_text())["codes"]
    donor_res = json.loads(
        (REPO / "runs/modal/lcb_res_lcb_r2_base_T08.json").read_text())
    donor_cb = dict(zip(donor_res["question_ids"], donor_cand))

    def matched_codes(cell):
        return [donor_cb[a["qid"]][a["cand_idx"]] for a in h7[cell]["artifacts"]]

    def matched_e0(cell):
        return _e0_codes(_load(f"j7_cand_{cell}"), h7[cell]["n"])

    # 1.5B base self-gens: donor candidates (non-artifact), up to 6/problem
    art_ci = {a["qid"]: a["cand_idx"] for a in d2c}
    base_self = []
    for a in d2c:
        got = 0
        for i, c in enumerate(donor_cb[a["qid"]]):
            if c and i != art_ci[a["qid"]]:
                base_self.append(c)
                got += 1
                if got >= 6:
                    break

    # (name, model, rev, diet, artifacts, self_e0)
    specs = [
        ("coder1p5b_sink", QWEN_BASE, QWEN_BASE_REV, "coder", d2c_codes, base_self),
        ("coder3b_sink", *J6_MODELS["qwen3b"], "coder", d2c_codes,
         _e0_codes(_load("j6_q1a_cand_qwen3b"), 44)),
        ("M4_coder7b_sink", *J7_MODELS["M4_coder7b"], "coder",
         matched_codes("M4_coder7b"), matched_e0("M4_coder7b")),
        ("M5_coder0p5b", *J7_MODELS["M5_coder0p5b"], "coder",
         matched_codes("M5_coder0p5b"), matched_e0("M5_coder0p5b")),
        ("M1_deepseek_clean", *J7_MODELS["M1_deepseek1p3b"], "organic",
         matched_codes("M1_deepseek1p3b"), matched_e0("M1_deepseek1p3b")),
        ("M2_general_clean", *J7_MODELS["M2_general1p5b"], "general",
         matched_codes("M2_general1p5b"), matched_e0("M2_general1p5b")),
        ("M3_starcoder_clean", *J7_MODELS["M3_starcoder2_3b"], "organic",
         matched_codes("M3_starcoder2_3b"), matched_e0("M3_starcoder2_3b")),
    ]
    rows = {}
    for name, mid, rev, diet, arts, self_g in specs:
        r = _load(f"j8_ppl_{name}") or _persist(
            f"j8_ppl_{name}",
            j8_ppl.remote(mid, rev, {"artifacts": arts, "self_e0": self_g},
                          tag=f"j8_ppl_{name}"))
        pa, ps = r["artifacts"]["mean_nll"], r["self_e0"]["mean_nll"]
        ratio = pa / ps if (pa and ps) else None
        rows[name] = {"diet": diet, "model": mid, "ppl_artifacts": pa, "ppl_self": ps,
                      "surprise_ratio": ratio}
        print(f"{name:20s} diet={diet:8s} ppl_art={pa:.3f} ppl_self={ps:.3f} "
              f"ratio={ratio:.3f}")

    coder_r = [v["surprise_ratio"] for k, v in rows.items() if v["diet"] == "coder"]
    other_r = [v["surprise_ratio"] for k, v in rows.items() if v["diet"] != "coder"]
    mc = sum(coder_r) / len(coder_r)
    mo = sum(other_r) / len(other_r)
    call = ("D3 => M-RECLASS-consistent (Coder surprise_ratio ~ non-Coder; matched "
            "artifacts are exemplar-credible, not off-manifold)" if mc <= mo + 0.10
            else "D3 => M-OOD-consistent (Coder matched artifacts MORE surprising)")
    print(f"\nmean surprise_ratio  coder={mc:.3f}  non-coder={mo:.3f}\nD3 CALL: {call}")
    out = {"_label": "Phase 8 D3 artifact perplexity [PHASE_8.md D3]",
           "rows": rows, "mean_ratio_coder": round(mc, 4),
           "mean_ratio_noncoder": round(mo, 4), "d3_call": call}
    (REPO / "artifacts/h8_d3_perplexity.json").write_text(json.dumps(out, indent=2))
    print("wrote artifacts/h8_d3_perplexity.json")


def _matched_cell(model_id, rev, seed, arts, cell, source_label):
    """Shared C-cell runner: E0 + E1 on `arts`, all-cases judge, sink signature."""
    import random
    import statistics as st
    n = len(arts)
    items = ([{"qid": a["qid"], "context": None} for a in arts]
             + [{"qid": a["qid"], "context": _d2c_context(a)} for a in arts])
    dgen = _load(f"j8_cand_{cell}") or _persist(
        f"j8_cand_{cell}",
        h1_gen_lcb.remote(model_id, items, 8, tag=f"j8_cand_{cell}", seed=seed,
                          revision=rev))
    dres = _load(f"j8_res_{cell}") or _persist(
        f"j8_res_{cell}",
        h1_lcb_exec.remote([g["qid"] for g in dgen], [g["codes"] for g in dgen],
                           tag=f"j8_res_{cell}"))
    e0 = [st.mean(x["frac"] for x in row) for row in dres[:n]]
    e1 = [st.mean(x["frac"] for x in row) for row in dres[n:]]
    copy_null = [a["frac"] for a in arts]
    d_iid = [b - a for a, b in zip(e0, e1)]
    p_sink = _wilcoxon_mc_one_sided([-x for x in d_iid])
    me0, me1, mc = st.mean(e0), st.mean(e1), st.mean(copy_null)
    effect = me1 - me0
    rng = random.Random(17)
    boot = sorted(st.mean(rng.choice(d_iid) for _ in d_iid) for _ in range(2000))
    ci = [round(boot[49], 4), round(boot[1949], 4)]
    sink = bool(me1 < me0 and p_sink < 0.05 and effect <= -0.05)
    out = {"_label": f"Phase 8 {cell} [PHASE_8.md]", "cell": cell, "model": model_id,
           "revision": rev, "seed": seed, "n_problems": n, "source": source_label,
           "mean_iid_e0": round(me0, 4), "mean_cond_e1": round(me1, 4),
           "mean_copy_null": round(mc, 4), "delta_cond_minus_iid": round(effect, 4),
           "delta_cond_minus_iid_ci95": ci, "actual_delta_art": round(mc - me0, 4),
           "p_one_sided_cond_below_iid": p_sink, "matched_sink_signature": sink,
           "stack": _stack_block()}
    (REPO / f"artifacts/h8_matched_{cell}.json").write_text(json.dumps(out, indent=2))
    print(f"=== j8 {cell}: iid {me0:.3f} → cond {me1:.3f} (copy {mc:.3f}) | "
          f"Δvs_iid {effect:+.3f} CI {ci} | actual Δart {mc-me0:+.3f} | "
          f"p_below_iid {p_sink:.4f} | SINK {sink} (n={n}, seed {seed}) ===")
    return out


@app.local_entrypoint()
def j8_matched(cell: str = "C2_deepseek_below0"):
    """C2/C4 confound cells (run j7_smoke on the model first if new)."""
    model_id, rev, seed = J8_CELLS[cell]
    c = json.loads((REPO / "artifacts/h8_c_artifacts.json").read_text())["cells"][cell]
    _matched_cell(model_id, rev, seed, c["artifacts"], cell,
                  f"mined donor @ {c['band']} (n={c['n']})")


@app.local_entrypoint()
def j8_phi_smoke():
    """C3 phi-1 smoke gate (its prompt format differs — a FAIL is reported, not forced)."""
    qids = _lcb_easy_qids()[:8]
    gen = _load("j8_phi_smoke_cand") or _persist(
        "j8_phi_smoke_cand",
        h1_gen_lcb.remote(PHI1, [{"qid": q, "context": None} for q in qids], 8,
                          tag="j8_phi_smoke_cand", revision=PHI1_REV))
    flat = [c for g in gen for c in g["codes"]]
    wf = sum(1 for c in flat if c) / len(flat)
    dg = sum(1 for c in flat if c and len(c) < 20) / max(1, sum(1 for c in flat if c))
    res = _load("j8_phi_smoke_res") or _persist(
        "j8_phi_smoke_res",
        h1_lcb_exec.remote([g["qid"] for g in gen], [g["codes"] for g in gen],
                           tag="j8_phi_smoke_res", short_circuit=True))
    npass = sum(1 for row in res for r in row if r["passed"])
    ok = wf >= 0.85 and dg <= 0.10
    print(f"=== j8 phi smoke: wf {wf:.3f} dg {dg:.3f} passed {npass}/{len(flat)} → "
          f"{'PASS' if ok else 'FAIL — REPORT, do not force'} ===")
    print("sample:\n" + next((c for c in flat if c), "")[:400])


@app.local_entrypoint()
def j8_c3_phi():
    """C3 — phi-1 at its OWN match (two-phase: measure iid → mine → condition).
    Second synthetic-code family; moves the diet attribution past n=1. Run
    j8_phi_smoke first. Writes artifacts/h8_matched_C3_phi1_match.json."""
    import statistics as st
    arts44 = _d2c_artifacts()
    qids = [a["qid"] for a in arts44]  # measure phi iid on the D2c problem universe
    # Phase 1 — phi i.i.d. on the cell problems
    e0gen = _load("j8_c3_phi_e0") or _persist(
        "j8_c3_phi_e0",
        h1_gen_lcb.remote(PHI1, [{"qid": q, "context": None} for q in qids], 8,
                          tag="j8_c3_phi_e0", revision=PHI1_REV))
    e0res = _load("j8_c3_phi_e0res") or _persist(
        "j8_c3_phi_e0res",
        h1_lcb_exec.remote([g["qid"] for g in e0gen], [g["codes"] for g in e0gen],
                           tag="j8_c3_phi_e0res"))
    iid_by_qid = {q: st.mean(x["frac"] for x in row)
                  for q, row in zip(qids, e0res)}
    phi_iid = st.mean(iid_by_qid.values())
    print(f"phi-1 i.i.d. on {len(qids)} problems: {phi_iid:.3f}")

    # Phase 2 — mine donor at phi's match band, condition phi on it
    donor = json.loads((REPO / "runs/modal/lcb_cand_lcb_r2_base_T08.json").read_text())
    dres = json.loads((REPO / "runs/modal/lcb_res_lcb_r2_base_T08.json").read_text())
    cb = dict(zip(dres["question_ids"], donor["codes"]))
    rb = dict(zip(dres["question_ids"], dres["results"]))
    lo, hi = phi_iid - 0.05, phi_iid + 0.05
    arts = []
    for q in dres["question_ids"]:
        inb = [(i, r) for i, r in enumerate(rb[q]) if lo <= r["frac"] <= hi and cb[q][i]]
        if inb:
            i, r = min(inb, key=lambda ir: (abs(ir[1]["frac"] - phi_iid), ir[0]))
            arts.append({"qid": q, "cand_idx": i, "code": cb[q][i], "frac": r["frac"],
                         "n_tests": r["n_tests"], "n_failed": r["n_tests"] - r["n_passed"]})
    print(f"phi matched set: n={len(arts)} at band [{lo:.3f},{hi:.3f}]")
    (REPO / "artifacts/h8_c3_phi_matched_set.json").write_text(
        json.dumps({"phi_iid": phi_iid, "band": [lo, hi], "n": len(arts),
                    "artifacts": arts}, indent=2))
    if len(arts) < 20:
        print(f"WARN: phi coverage {len(arts)} < 20 — scoped/underpowered, recorded")
    _matched_cell(PHI1, PHI1_REV, 17, arts, "C3_phi1_match",
                  f"phi iid {phi_iid:.3f}; mined donor @ [{lo:.3f},{hi:.3f}] (n={len(arts)})")
