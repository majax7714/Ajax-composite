"""Shape/stability tests for the torch-edge modules. Skipped when torch is
not installed (the pure-stdlib core never depends on these)."""

import pytest

torch = pytest.importorskip("torch")

from rgr.config import VerifierConfig
from rgr.generator.injection import RegisterInjector
from rgr.register.encoder import ConstantRegisterInit
from rgr.register.update import RegisterUpdate
from rgr.types import Candidate, Problem
from rgr.verifier.model import ERROR_TYPES, Verifier

D_R, PHI = 128, 1536


def test_register_update_shapes_and_rms():
    u = RegisterUpdate(d_r=D_R, phi_dim=PHI)
    r2 = u.forward(torch.randn(D_R), torch.randn(PHI), 0.7)
    assert r2.shape == (D_R,)
    assert abs(float(r2.detach().pow(2).mean().sqrt()) - 1.0) < 1e-4


def test_register_update_delta_clip():
    u = RegisterUpdate(d_r=D_R, phi_dim=PHI, rms_normalize=False, max_update_norm=0.5)
    r = torch.zeros(D_R)
    r2 = u.forward(r, torch.randn(PHI) * 100, 1.0)
    assert float((r2 - r).detach().norm()) <= 0.5 + 1e-5


def test_register_update_protocol_uses_attached_phi():
    u = RegisterUpdate(d_r=D_R, phi_dim=PHI)
    candidate = Candidate(text="x", code="x", phi=torch.randn(PHI))
    r2 = u.update(torch.randn(D_R), candidate, 0.3)
    assert r2.shape == (D_R,)
    with pytest.raises(RuntimeError):
        u.update(torch.randn(D_R), Candidate(text="x", code="x"), 0.3)


def test_injector_shapes():
    inj = RegisterInjector(d_r=D_R, k=8, d_model=PHI)
    assert inj(torch.randn(D_R)).shape == (8, PHI)
    assert inj(torch.randn(4, D_R)).shape == (4, 8, PHI)


def test_constant_init():
    init = ConstantRegisterInit(d_r=D_R)
    problem = Problem(problem_id="t/1", prompt="p", tests="t")
    assert init.init(problem).shape == (D_R,)


def test_verifier_heads_and_range():
    v = Verifier(VerifierConfig(), phi_dim=PHI)
    out = v(torch.randn(5, PHI), torch.randn(5, PHI))
    assert out["p_correct"].shape == (5,)
    assert out["frac_tests"].shape == (5,)
    assert out["error_type_logits"].shape == (5, len(ERROR_TYPES))
    assert (out["p_correct"] >= 0).all() and (out["p_correct"] <= 1).all()


def test_verifier_register_blind_rejects_register_dim_zero():
    with pytest.raises(ValueError):
        Verifier(VerifierConfig(sees_register=True), phi_dim=PHI, d_r=0)


def test_verifier_score_zero_for_no_code():
    v = Verifier(VerifierConfig(), phi_dim=PHI)
    problem = Problem(problem_id="t/1", prompt="p", tests="t")
    assert v.score(problem, Candidate(text="prose", code=None)) == 0.0
