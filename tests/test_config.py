from pathlib import Path

import pytest

from rgr.config import load_config

CONFIGS = Path(__file__).parents[1] / "configs"


def test_base_encodes_decisions():
    config = load_config()
    assert config.register.d_r == 128  # D1
    assert config.register.k_soft_tokens == 8  # D1
    assert config.verifier.sees_register is False  # D3
    assert config.register.init == "problem_encoded"  # D4
    assert config.generator.frozen is True  # D6
    assert config.loop.t_max == 8  # pre-registered N


def test_phase_overlay_merges():
    config = load_config(CONFIGS / "phase3_adaptive.toml")
    assert config.loop.early_stop is True  # overlaid
    assert config.loop.t_max == 8  # inherited from base
    assert config.run.tag == "phase3"


def test_phase0_freezes_register():
    config = load_config(CONFIGS / "phase0_harness.toml")
    assert config.loop.freeze_register is True


def test_extra_tables_preserved():
    config = load_config(CONFIGS / "phase1_verifier.toml")
    assert config.extra["labels"]["candidates_per_problem"] == 16


def test_matched_compute_invariant_in_configs():
    """baselines.n must equal loop.t_max in every phase config, or the
    headline comparison is unmatched by construction."""
    for path in sorted(CONFIGS.glob("*.toml")):
        config = load_config(path if path.name != "base.toml" else None)
        assert config.extra["baselines"]["n"] == config.loop.t_max, path.name


def test_unknown_key_rejected(tmp_path):
    bad = tmp_path / "bad.toml"
    bad.write_text("[loop]\nt_mxa = 4\n")  # typo must fail loudly, not no-op
    with pytest.raises(ValueError, match="t_mxa"):
        load_config(bad)
