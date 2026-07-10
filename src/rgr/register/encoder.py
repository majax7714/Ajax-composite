"""r_0 — problem-encoded register initialization (D4).

r_0 = W_0 · phi(problem), a learned linear projection of the frozen generator's
mean-pooled last-layer hidden states over the problem tokens. No separate
encoder model (D7: one φ source, the generator itself).

A learned-constant variant is kept as the debug fallback named in D4's revisit
clause (register.init = "learned_constant" in config).
"""

from __future__ import annotations

import torch
from torch import nn

from rgr.types import Problem


class ProblemRegisterEncoder(nn.Module):
    """Satisfies RegisterInitLike once ``embed_problem`` is wired to G."""

    def __init__(self, d_r: int, phi_dim: int, embed_problem=None) -> None:
        super().__init__()
        self.proj = nn.Linear(phi_dim, d_r)
        # Callable Problem -> torch.Tensor(phi_dim,), supplied at assembly time
        # (scripts/) from the generator's pooling to keep this module G-agnostic.
        self.embed_problem = embed_problem

    @torch.no_grad()
    def init(self, problem: Problem) -> torch.Tensor:
        if self.embed_problem is None:
            raise RuntimeError("embed_problem not wired; see scripts/ assembly")
        return self.proj(self.embed_problem(problem))

    def forward(self, phi_problem: torch.Tensor) -> torch.Tensor:
        return self.proj(phi_problem)


class ConstantRegisterInit(nn.Module):
    """Learned-constant r_0 — D4's debug fallback, and the purer-ablation
    variant if register updates collapse."""

    def __init__(self, d_r: int) -> None:
        super().__init__()
        self.r0 = nn.Parameter(torch.zeros(d_r))

    @torch.no_grad()
    def init(self, problem: Problem) -> torch.Tensor:
        return self.r0.clone()
