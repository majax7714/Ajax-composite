"""phi — the shared pooled-embedding feature (D7).

One phi source for everything (r_0 encoder, U's candidate input, V's features):
mean-pooled last-layer hidden states from the frozen generator. Centralized
here so "what phi means" can never drift between modules.
"""

from __future__ import annotations

import torch


def mean_pool(hidden_states: torch.Tensor, attention_mask: torch.Tensor | None = None) -> torch.Tensor:
    """(seq, d) or (batch, seq, d) -> (d,) or (batch, d), mask-aware."""
    if hidden_states.dim() == 2:
        return hidden_states.mean(dim=0) if attention_mask is None else (
            (hidden_states * attention_mask.unsqueeze(-1)).sum(0)
            / attention_mask.sum().clamp(min=1)
        )
    if attention_mask is None:
        return hidden_states.mean(dim=1)
    mask = attention_mask.unsqueeze(-1).to(hidden_states.dtype)
    return (hidden_states * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1)
