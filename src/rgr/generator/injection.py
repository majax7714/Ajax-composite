"""Register injection — the ONLY way r touches G (ARCHITECTURE.md §3, rule 2).

r (d_r) -> k soft-prompt embeddings (k x d_model), prepended to the prompt
embeddings of the frozen generator. Simplest buildable path per brief §2;
FiLM / cross-attention variants are post-H3 work.
"""

from __future__ import annotations

import torch
from torch import nn


class RegisterInjector(nn.Module):
    def __init__(self, d_r: int, k: int, d_model: int) -> None:
        super().__init__()
        self.k = k
        self.d_model = d_model
        self.proj = nn.Linear(d_r, k * d_model)

    def forward(self, register: torch.Tensor) -> torch.Tensor:
        """(d_r,) -> (k, d_model), or batched (b, d_r) -> (b, k, d_model)."""
        squeeze = register.dim() == 1
        r = register.unsqueeze(0) if squeeze else register
        out = self.proj(r).view(r.shape[0], self.k, self.d_model)
        return out.squeeze(0) if squeeze else out
