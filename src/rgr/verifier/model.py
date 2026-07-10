"""V — the verifier (the energy). P(correct | problem, candidate).

V-v1 (D7): MLP over [phi(problem); phi(candidate)] with a sigmoid main head and
auxiliary heads (frac_tests regression, error-type classification) to sharpen
the score. Register-blind per D3: ``sees_register`` is wired but must stay
False for every H1/H2 headline run; flipping it is the v2 experiment and needs
a V retrain.

The scalar output gates the loop (tau); -log(output) is the energy in the
paper's framing. Escalation path if H1 is marginal: V-v2, a small fine-tuned
text encoder — pre-authorized by D7.
"""

from __future__ import annotations

import torch
from torch import nn

from rgr.config import VerifierConfig
from rgr.types import Candidate, Problem

ERROR_TYPES = ["", "syntax", "runtime", "timeout", "wrong_answer", "no_code"]


class Verifier(nn.Module):
    def __init__(self, config: VerifierConfig, phi_dim: int, d_r: int = 0, embed_problem=None) -> None:
        super().__init__()
        self.config = config
        if config.sees_register and d_r <= 0:
            raise ValueError("sees_register=True requires d_r > 0")
        in_dim = 2 * phi_dim + (d_r if config.sees_register else 0)
        self.trunk = nn.Sequential(
            nn.Linear(in_dim, config.hidden_dim),
            nn.GELU(),
            nn.Linear(config.hidden_dim, config.hidden_dim),
            nn.GELU(),
        )
        self.head_correct = nn.Linear(config.hidden_dim, 1)
        self.head_frac_tests = nn.Linear(config.hidden_dim, 1) if config.aux_frac_tests else None
        self.head_error_type = (
            nn.Linear(config.hidden_dim, len(ERROR_TYPES)) if config.aux_error_type else None
        )
        # Callable Problem -> phi tensor, wired at assembly time from the
        # generator (same phi source as everything else, D7).
        self.embed_problem = embed_problem

    def forward(
        self,
        phi_problem: torch.Tensor,
        phi_candidate: torch.Tensor,
        register: torch.Tensor | None = None,
    ) -> dict[str, torch.Tensor]:
        parts = [phi_problem, phi_candidate]
        if self.config.sees_register:
            if register is None:
                raise ValueError("sees_register=True but no register given")
            parts.append(register)
        h = self.trunk(torch.cat(parts, dim=-1))
        out = {"p_correct": torch.sigmoid(self.head_correct(h)).squeeze(-1)}
        if self.head_frac_tests is not None:
            out["frac_tests"] = torch.sigmoid(self.head_frac_tests(h)).squeeze(-1)
        if self.head_error_type is not None:
            out["error_type_logits"] = self.head_error_type(h)
        return out

    # --- VerifierLike (inference-side) ---

    @torch.no_grad()
    def score(self, problem: Problem, candidate: Candidate, register=None) -> float:
        if candidate.code is None:
            return 0.0  # no extractable code: automatic failure, don't spend a forward pass
        if self.embed_problem is None:
            raise RuntimeError("embed_problem not wired; see scripts/ assembly")
        if candidate.phi is None:
            raise RuntimeError("candidate has no attached phi (generator must attach it)")
        phi_p = self.embed_problem(problem)
        r = register if self.config.sees_register else None
        return float(self.forward(phi_p, candidate.phi, r)["p_correct"])
