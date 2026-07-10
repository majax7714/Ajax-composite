"""Typed configuration, loaded from TOML (stdlib tomllib — no dependencies).

``load_config(phase_path)`` deep-merges the phase overlay onto configs/base.toml.
Values encoding decisions D1-D8 live in base.toml; see docs/DECISIONS.md.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class GeneratorConfig:
    model_name: str = "Qwen/Qwen2.5-Coder-1.5B-Instruct"
    load_4bit: bool = True
    frozen: bool = True
    max_new_tokens: int = 512
    temperature: float = 0.8
    top_p: float = 0.95


@dataclass(frozen=True)
class RegisterConfig:
    d_r: int = 128
    k_soft_tokens: int = 8
    init: str = "problem_encoded"  # D4; "learned_constant" is the debug fallback
    rms_normalize: bool = True
    max_update_norm: float = 1.0


@dataclass(frozen=True)
class VerifierConfig:
    sees_register: bool = False  # D3
    hidden_dim: int = 512
    aux_frac_tests: bool = True
    aux_error_type: bool = True


@dataclass(frozen=True)
class LoopConfig:
    t_max: int = 8
    early_stop: bool = False
    tau: float = 0.9
    freeze_register: bool = False


@dataclass(frozen=True)
class ExecutionConfig:
    backend: str = "daytona"
    timeout_seconds: int = 10


@dataclass(frozen=True)
class DataConfig:
    train: str = "mbpp"
    heldout: str = "humaneval"
    val_fraction: float = 0.1
    seed: int = 17


@dataclass(frozen=True)
class RunConfig:
    seed: int = 17
    output_dir: str = "runs"
    tag: str = ""


@dataclass(frozen=True)
class Config:
    generator: GeneratorConfig = field(default_factory=GeneratorConfig)
    register: RegisterConfig = field(default_factory=RegisterConfig)
    verifier: VerifierConfig = field(default_factory=VerifierConfig)
    loop: LoopConfig = field(default_factory=LoopConfig)
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)
    data: DataConfig = field(default_factory=DataConfig)
    run: RunConfig = field(default_factory=RunConfig)
    # Phase-specific tables ([labels], [verifier_train], [register_train],
    # [baselines], ...) are kept as plain dicts — they change per phase and
    # don't warrant schema churn in the core.
    extra: dict[str, Any] = field(default_factory=dict)


_SECTION_TYPES = {
    "generator": GeneratorConfig,
    "register": RegisterConfig,
    "verifier": VerifierConfig,
    "loop": LoopConfig,
    "execution": ExecutionConfig,
    "data": DataConfig,
    "run": RunConfig,
}


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def _build_section(cls: type, table: dict[str, Any], section: str) -> Any:
    known = {f.name for f in fields(cls)}
    unknown = set(table) - known
    if unknown:
        raise ValueError(f"unknown keys in [{section}]: {sorted(unknown)}")
    return cls(**table)


def load_config(phase_path: str | Path | None = None, base_path: str | Path | None = None) -> Config:
    """Load base.toml, overlay a phase config if given, return a typed Config."""
    base_path = Path(base_path) if base_path else Path(__file__).parents[2] / "configs" / "base.toml"
    with open(base_path, "rb") as f:
        raw = tomllib.load(f)
    if phase_path is not None:
        with open(phase_path, "rb") as f:
            raw = _deep_merge(raw, tomllib.load(f))

    sections = {name: _build_section(cls, raw.pop(name, {}), name) for name, cls in _SECTION_TYPES.items()}
    return Config(**sections, extra=raw)
