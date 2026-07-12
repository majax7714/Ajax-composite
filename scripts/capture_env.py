#!/usr/bin/env python3
"""Capture the runtime environment for env/kaggle_phase0_2.lock (Phase K, §1).

Runs on a free Kaggle CPU session. Dumps package versions, CUDA/driver info (if a
GPU is attached), a full pip freeze, and — critically — the Qwen model revision
SHA (pin the revision, not just the repo name). The generator loads
Qwen/Qwen2.5-Coder-1.5B-Instruct from `main` with no explicit revision (D6 /
model.py), so the SHA is resolved here from the Hub.

CPU/GPU caveat (PHASE_K.md §1): a Kaggle CPU session ships a CPU-only torch build,
so `torch`/CUDA here will NOT match the GPU stack (torch 2.9 + cuXX per the GPU
logs). The Python-level packages are shared; take torch/CUDA from the GPU logs.
"""
import json
import os
import platform
import subprocess
import sys

MODEL = "Qwen/Qwen2.5-Coder-1.5B-Instruct"
out = {"python": sys.version, "platform": platform.platform()}


def ver(mod):
    try:
        return getattr(__import__(mod), "__version__", "present(no __version__)")
    except Exception as e:  # noqa: BLE001
        return f"(absent: {type(e).__name__})"


for m in ("torch", "transformers", "bitsandbytes", "accelerate", "peft",
          "numpy", "datasets", "huggingface_hub", "tokenizers", "safetensors"):
    out[m] = ver(m)

try:
    import torch
    out["torch_cuda"] = torch.version.cuda
    out["cuda_available"] = torch.cuda.is_available()
    out["torch_cudnn"] = (torch.backends.cudnn.version()
                          if torch.backends.cudnn.is_available() else None)
except Exception as e:  # noqa: BLE001
    out["torch_cuda_error"] = repr(e)

try:
    out["nvidia_smi"] = subprocess.run(
        ["nvidia-smi"], capture_output=True, text=True, timeout=30).stdout or "(empty)"
except Exception as e:  # noqa: BLE001
    out["nvidia_smi"] = f"(absent: {type(e).__name__})"

try:
    from huggingface_hub import HfApi
    info = HfApi().model_info(MODEL)
    out["qwen_model"] = MODEL
    out["qwen_revision_sha"] = info.sha
    out["qwen_last_modified"] = str(getattr(info, "lastModified", "?"))
except Exception as e:  # noqa: BLE001
    out["qwen_revision_error"] = repr(e)

try:
    out["pip_freeze"] = subprocess.run(
        [sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True,
        timeout=180).stdout
except Exception as e:  # noqa: BLE001
    out["pip_freeze"] = f"(err: {e!r})"

os.makedirs("runs/env", exist_ok=True)
json.dump(out, open("runs/env/capture.json", "w"), indent=2)
brief = {k: v for k, v in out.items() if k not in ("pip_freeze", "nvidia_smi")}
print(json.dumps(brief, indent=2))
print("\nwrote runs/env/capture.json")
