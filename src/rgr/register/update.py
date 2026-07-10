"""U — the register update cell. r_{t+1} = U(r_t, [phi(candidate); v]).

The only cross-step channel in the architecture. Stability guards (brief §8:
"register dynamics can collapse or run away") are built into the forward pass,
on by default:
  - RMS-normalization of r after each update (keeps ||r|| ~ sqrt(d_r)),
  - max-norm clip on the delta before applying it.

Satisfies rgr.loop.interfaces.RegisterUpdateLike with Register = torch.Tensor
of shape (d_r,).
"""

from __future__ import annotations

import torch
from torch import nn

from rgr.types import Candidate


class RegisterUpdate(nn.Module):
    def __init__(
        self,
        d_r: int,
        phi_dim: int,
        *,
        rms_normalize: bool = True,
        max_update_norm: float = 1.0,
    ) -> None:
        super().__init__()
        self.d_r = d_r
        self.rms_normalize = rms_normalize
        self.max_update_norm = max_update_norm
        # input = pooled candidate embedding + scalar verifier score
        self.cell = nn.GRUCell(input_size=phi_dim + 1, hidden_size=d_r)

    def forward(self, register: torch.Tensor, phi: torch.Tensor, score: float) -> torch.Tensor:
        squeeze = register.dim() == 1
        r = register.unsqueeze(0) if squeeze else register
        p = phi.unsqueeze(0) if phi.dim() == 1 else phi
        v = torch.full((r.shape[0], 1), float(score), dtype=p.dtype, device=p.device)

        proposed = self.cell(torch.cat([p, v], dim=-1), r)

        delta = proposed - r
        if self.max_update_norm > 0:
            norm = delta.norm(dim=-1, keepdim=True).clamp(min=1e-8)
            delta = delta * (self.max_update_norm / norm).clamp(max=1.0)
        out = r + delta

        if self.rms_normalize:
            rms = out.pow(2).mean(dim=-1, keepdim=True).sqrt().clamp(min=1e-8)
            out = out / rms

        return out.squeeze(0) if squeeze else out

    # --- RegisterUpdateLike protocol (inference-side, no grad) ---

    @torch.no_grad()
    def update(self, register: torch.Tensor, candidate: Candidate, verifier_score: float) -> torch.Tensor:
        phi = self._phi(candidate)
        return self.forward(register, phi, verifier_score)

    def norm(self, register: torch.Tensor) -> float:
        return float(register.norm())

    def delta_norm(self, before: torch.Tensor, after: torch.Tensor) -> float:
        return float((after - before).norm())

    def _phi(self, candidate: Candidate) -> torch.Tensor:
        """Pooled candidate embedding. Wired to the generator's pooled hidden
        states by the runtime assembly (scripts/), which attaches phi to the
        candidate at generation time to avoid a second forward pass."""
        phi = candidate.phi
        if phi is None:
            raise RuntimeError(
                "candidate has no attached phi embedding; generator must attach "
                "pooled hidden states at generation time (see rgr.generator.model)"
            )
        return phi
