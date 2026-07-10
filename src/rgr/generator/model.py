"""G — frozen 4-bit generator with soft-prompt injection.

Satisfies GeneratorLike and FeedbackGeneratorLike. GPU-edge module: needs the
[model] extra and a GPU; the local suite tests everything around it through
the protocols. Contract honored here:

  - generate(problem, register): ONE sampled candidate; register (if not None)
    enters as k soft-prompt embeddings prepended to the chat prompt embeddings
    — the only way r touches G. Attaches mean_logprob (H1 likelihood
    baseline), token counts (ledger), and phi (mean-pooled last-layer hidden
    states over generated tokens) so U and V never re-encode.
  - generate_with_feedback: B2 only — previous candidate + verifier score in
    the PROMPT. Never called by rgr.loop.refine.
  - embed_problem(problem): phi over the problem text (r_0 encoder, V features).
"""

from __future__ import annotations

from rgr.config import GeneratorConfig
from rgr.generator.formatting import (
    SYSTEM_PROMPT,
    build_feedback_prompt,
    build_prompt,
    extract_code,
)
from rgr.types import Candidate, Problem


class Generator:
    def __init__(self, config: GeneratorConfig, injector=None) -> None:
        self.config = config
        self.injector = injector  # rgr.generator.injection.RegisterInjector | None
        self._model = None
        self._tokenizer = None

    # --- loading ---

    def load(self) -> None:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

        quant = (
            BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16,
            )
            if self.config.load_4bit
            else None
        )
        self._tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
        self._model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            quantization_config=quant,
            device_map="auto",
            torch_dtype=torch.bfloat16 if quant is None else None,
        )
        self._model.eval()
        if self.config.frozen:
            for p in self._model.parameters():
                p.requires_grad_(False)

    @property
    def d_model(self) -> int:
        self._require_loaded()
        return self._model.config.hidden_size

    @property
    def device(self):
        self._require_loaded()
        return self._model.get_input_embeddings().weight.device

    def _require_loaded(self) -> None:
        if self._model is None:
            raise RuntimeError("call load() first")

    # --- GeneratorLike ---

    def generate(self, problem: Problem, register) -> Candidate:
        return self._sample(build_prompt(problem.prompt), register)

    # --- FeedbackGeneratorLike (B2 only) ---

    def generate_with_feedback(self, problem: Problem, prev: Candidate, verifier_score: float) -> Candidate:
        prompt = build_feedback_prompt(problem.prompt, prev.code or prev.text, verifier_score)
        return self._sample(prompt, register=None)

    # --- phi source (r_0 encoder, V features) ---

    def embed_problem(self, problem: Problem):
        """Mean-pooled last-layer hidden states over the raw problem text."""
        import torch

        self._require_loaded()
        ids = self._tokenizer(problem.prompt, return_tensors="pt", truncation=True).input_ids
        ids = ids.to(self.device)
        with torch.no_grad():
            out = self._model(input_ids=ids, output_hidden_states=True)
        return out.hidden_states[-1][0].float().mean(dim=0)

    # --- internals ---

    def _sample(self, user_prompt: str, register) -> Candidate:
        import torch

        self._require_loaded()
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
        encoded = self._tokenizer.apply_chat_template(
            messages, add_generation_prompt=True, return_tensors="pt"
        )
        # transformers version drift: newer releases return a BatchEncoding,
        # older ones a bare tensor.
        input_ids = getattr(encoded, "input_ids", encoded).to(self.device)

        embeds = self._model.get_input_embeddings()(input_ids)
        prompt_tokens = input_ids.shape[1]
        if register is not None:
            if self.injector is None:
                raise RuntimeError("register given but no injector wired")
            soft = self.injector(register.to(self.device)).to(embeds.dtype).unsqueeze(0)
            embeds = torch.cat([soft, embeds], dim=1)
            prompt_tokens += soft.shape[1]
        attention_mask = torch.ones(embeds.shape[:2], dtype=torch.long, device=self.device)

        with torch.no_grad():
            out = self._model.generate(
                inputs_embeds=embeds,
                attention_mask=attention_mask,
                max_new_tokens=self.config.max_new_tokens,
                do_sample=self.config.temperature > 0,
                temperature=self.config.temperature or None,
                top_p=self.config.top_p,
                pad_token_id=self._tokenizer.eos_token_id,
                return_dict_in_generate=True,
                output_scores=True,
                output_hidden_states=True,
            )

        # With inputs_embeds (no input_ids), sequences holds generated tokens only.
        gen_ids = out.sequences[0]
        text = self._tokenizer.decode(gen_ids, skip_special_tokens=True)

        # Mean token log-probability under the sampling distribution's logits —
        # the H1 likelihood baseline.
        logprobs = [
            torch.log_softmax(step_scores[0].float(), dim=-1)[token].item()
            for step_scores, token in zip(out.scores, gen_ids)
        ]
        mean_logprob = sum(logprobs) / len(logprobs) if logprobs else None

        # phi: last-layer hidden state of each generated position, mean-pooled.
        # out.hidden_states[t][-1] is (batch, seq_t, d); seq_t is the prompt at
        # t=0 and 1 thereafter — taking [:, -1, :] uniformly gives exactly the
        # positions that emitted the generated tokens.
        steps = [h[-1][:, -1, :].float() for h in out.hidden_states[: len(gen_ids)]]
        phi = torch.cat(steps, dim=0).mean(dim=0) if steps else None

        return Candidate(
            text=text,
            code=extract_code(text),
            mean_logprob=mean_logprob,
            prompt_tokens=prompt_tokens,
            generated_tokens=len(gen_ids),
            phi=phi,
        )

    @staticmethod
    def make_candidate(text: str, **kwargs) -> Candidate:
        return Candidate(text=text, code=extract_code(text), **kwargs)
