"""G — frozen 4-bit generator with soft-prompt injection.

Satisfies GeneratorLike and FeedbackGeneratorLike. This is a GPU-edge module:
it holds the transformers/bitsandbytes wiring and is exercised on the training
box (Kaggle), not in the local test suite. The contract it must honor:

  - generate(problem, register): sample ONE candidate; if register is not None,
    prepend injector(register) to the prompt embeddings. Attach to Candidate:
    mean token log-prob (H1 baseline), token counts (ledger), and phi = mean
    pooled last-layer hidden states over the generated tokens (for U and V).
  - generate_with_feedback: B2 only — previous candidate + verifier score go in
    the PROMPT (build_feedback_prompt). Never called by rgr.loop.refine.
  - embed_problem(problem): phi over the problem tokens (for r_0 and V).

Phase-0 hand-check (brief §11.1): scripts/phase0_lock_baselines.py --handcheck
prints 20 MBPP completions for manual inspection before anything else runs.
"""

from __future__ import annotations

from rgr.config import GeneratorConfig
from rgr.generator.formatting import build_feedback_prompt, build_prompt, extract_code
from rgr.generator.injection import RegisterInjector
from rgr.types import Candidate, Problem


class Generator:
    def __init__(self, config: GeneratorConfig, injector: RegisterInjector | None = None) -> None:
        self.config = config
        self.injector = injector
        self._model = None
        self._tokenizer = None

    def load(self) -> None:
        """Load tokenizer + 4-bit model (bitsandbytes NF4), eval mode, frozen."""
        import torch  # noqa: F401  (GPU-edge import, deliberate late binding)
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

        quant = (
            BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4")
            if self.config.load_4bit
            else None
        )
        self._tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
        self._model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name, quantization_config=quant, device_map="auto"
        )
        self._model.eval()

    # --- GeneratorLike ---

    def generate(self, problem: Problem, register) -> Candidate:
        """Sample one candidate; inject register as soft prompt when given.

        Implementation route (to build in Phase 0/2):
          1. tokenize build_prompt(problem.prompt) via the chat template with
             SYSTEM_PROMPT; get input embeddings from the model's embedding
             layer;
          2. if register is not None: embeds = cat([injector(register),
             prompt_embeds]) and call model.generate(inputs_embeds=...,
             output_hidden_states=True, output_scores=True);
          3. compute mean token log-prob from scores; phi = mean of last-layer
             hidden states over generated tokens; code = extract_code(text).
        """
        raise NotImplementedError("Phase 0: wire transformers generation (see docstring)")

    # --- FeedbackGeneratorLike (B2 only) ---

    def generate_with_feedback(self, problem: Problem, prev: Candidate, verifier_score: float) -> Candidate:
        prompt = build_feedback_prompt(problem.prompt, prev.code or prev.text, verifier_score)
        raise NotImplementedError(f"Phase 0: as generate(), register=None, prompt={prompt[:0]!r}")

    # --- phi source for r_0 encoder and verifier features ---

    def embed_problem(self, problem: Problem):
        """Mean-pooled last-layer hidden states over the problem tokens."""
        raise NotImplementedError("Phase 1: single forward pass, pool, return tensor")

    @staticmethod
    def make_candidate(text: str, **kwargs) -> Candidate:
        return Candidate(text=text, code=extract_code(text), **kwargs)
