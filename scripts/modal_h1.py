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
               temperature: float = 0.8, top_p: float = 1.0, seed: int = 17):
    """Frozen R2/p3b fenced-completion scaffold, parametrized by model.
    items: [{qid, context|None}]."""
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
                  max_model_len=8192, seed=seed)
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
