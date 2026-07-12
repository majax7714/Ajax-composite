# Environment capture — Phases 0–2 stack (Phase K bridge)

Captured 2026-07-12 for [../docs/PHASE_K.md] §1. This is the bridge artifact: the
Modal T4 image is pinned to it, and GATE K1 arbitrates whether the pin is faithful.

## Method

Free Kaggle **CPU** session (`kaggle_launch.py launch envcap` → `scripts/capture_env.py`,
kernel `rgr-envcap` v2, COMPLETE). Full `pip freeze` → `kaggle_phase0_2.lock`
(885 lines). Model revision resolved from the Hub.

## Key versions (as captured, Kaggle CPU image, 2026-07-12)

| package | captured | notes |
|---|---|---|
| python | 3.12.13 | matches GPU logs (python3.12) |
| torch | **2.10.0+cpu** | ⚠️ CPU build; **GPU stack ran Torch 2.9** (Phase-0/2 logs) |
| transformers | 5.0.0 | |
| bitsandbytes | 0.49.2 | GPU runner installed `-U bitsandbytes>=0.46.1` → this range |
| accelerate | 1.13.0 | |
| peft | 0.19.1 | |
| numpy | 2.0.2 | |
| datasets | 5.0.0 | |
| tokenizers | 0.22.2 | |
| safetensors | 0.7.0 | |
| huggingface_hub | 1.11.0 | |
| **Qwen revision SHA** | **`2e1fd397ee46e1388853d2af2c993145b0f1098a`** | Qwen2.5-Coder-1.5B-Instruct, last modified 2025-01-12 (stable — pin this) |

## The CPU/GPU caveat (why this is a *reconstruction*, not a snapshot)

The GPU stack that produced Phases 0–2 ran **2026-07-10/11**; this capture ran
**2026-07-12** on Kaggle's **CPU** image, which had already advanced (torch
2.10.0+cpu). The GPU logs pin **Torch 2.9**. Kaggle's CPU and GPU images are built
separately and can differ; the exact GPU-stack `transformers`/`bitsandbytes`
versions on 2026-07-10 were never recorded (`pip install -q` printed nothing, and
the ephemeral HF cache wasn't preserved). So exact bit-for-bit reproduction is not
guaranteed a priori — **GATE K1 is the arbiter**.

## Reconciled Modal T4 pins (what the image installs)

Take the capture, **override torch to the GPU-stack version**:

```
torch==2.9.0            # GPU stack (logs), NOT the CPU-captured 2.10; CUDA wheel (T4 = sm75)
transformers==5.0.0
bitsandbytes==0.49.2
accelerate==1.13.0
peft==0.19.1
numpy==2.0.2
datasets==5.0.0
tokenizers==0.22.2
safetensors==0.7.0
huggingface_hub==1.11.0
# model: Qwen/Qwen2.5-Coder-1.5B-Instruct @ 2e1fd397ee46e1388853d2af2c993145b0f1098a
```

If K1 shows **systematic** divergence (tokens 1–3), the most likely culprit is the
`transformers` generation path (5.0.0 may post-date the GPU stack); try the nearest
4.x. **Small tail divergence is acceptable** for the mechanistic diagnostics and is
logged as the first [../docs/COMPUTE_ACCOUNTING.md] amendment.
