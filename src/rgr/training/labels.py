"""Phase 1 label generation: candidates x execution results -> V training set.

The expensive line item is sandboxed execution, not training (brief §7) —
budget and log sandbox time here. Records are JSONL, one per (problem,
candidate), with everything V's training and the H1 head-to-head need:

  {problem_id, candidate_text, candidate_code, mean_logprob,     # H1 baseline
   passed, frac_tests, error_type,                               # labels
   temperature, seed, generator_config_hash}                     # provenance

Staleness discipline (brief §2): tag every record with the policy that
produced it (generator config + injector/U checkpoint id, or "phase1_raw" when
no register modules exist yet). V refreshes between phases filter on this tag.
"""

from __future__ import annotations

from collections.abc import Iterable

from rgr.execution.sandbox import ExecutionBackend
from rgr.loop.interfaces import GeneratorLike
from rgr.types import Problem


def generate_labels(
    problems: Iterable[Problem],
    generator: GeneratorLike,
    backend: ExecutionBackend,
    *,
    candidates_per_problem: int,
    temperatures: list[float],
    out_path: str,
    policy_tag: str = "phase1_raw",
) -> None:
    """For each problem: sample candidates across temperatures (register=None
    in Phase 1 — no register modules exist yet), execute each in the sandbox,
    append one JSONL record per candidate.

    Wiring left for Phase 1: temperature control on the generator, resumable
    output (skip problems already present in out_path), sandbox-time logging.
    """
    raise NotImplementedError("Phase 1: see docstring for the record schema and loop")
