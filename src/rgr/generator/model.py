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
        return self.sample_batch(build_prompt(problem.prompt), 1, register=register)[0]

    def sample(self, problem: Problem, n: int, *, temperature: float | None = None,
               register=None) -> list[Candidate]:
        """n candidates for one problem in a single batched generate call.
        All share one prompt, so num_return_sequences batching has no padding
        asymmetry. ~5-8x faster than n sequential calls; used by label
        generation (Phase 1)."""
        return self.sample_batch(build_prompt(problem.prompt), n,
                                 temperature=temperature, register=register)

    # --- FeedbackGeneratorLike (B2 only) ---

    def generate_with_feedback(self, problem: Problem, prev: Candidate, verifier_score: float) -> Candidate:
        prompt = build_feedback_prompt(problem.prompt, prev.code or prev.text, verifier_score)
        return self.sample_batch(prompt, 1, register=None)[0]

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

    def embed_candidate(self, problem: Problem, completion_text: str):
        """phi for a stored completion, matching generation-time phi.

        Causal LM hidden states depend only on the prefix, so teacher-forcing
        the same (chat prompt + completion) tokens reproduces the states that
        emitted each completion token: output positions [L-1, L+T-2] for a
        prompt of length L and completion of length T. Used to re-encode the
        frozen Phase-0 HumanEval candidates as the H1 evaluation features.
        (Decode/re-tokenize can shift token boundaries slightly; mean pooling
        absorbs it.)
        """
        import torch

        self._require_loaded()
        prompt_ids = self._chat_ids(build_prompt(problem.prompt))
        comp = self._tokenizer(completion_text, return_tensors="pt",
                               add_special_tokens=False, truncation=True,
                               max_length=self.config.max_new_tokens)
        comp_ids = comp.input_ids.to(self.device)
        if comp_ids.shape[1] == 0:
            return self.embed_problem(problem)  # degenerate empty completion
        full = torch.cat([prompt_ids, comp_ids], dim=1)
        with torch.no_grad():
            out = self._model(input_ids=full, output_hidden_states=True)
        h = out.hidden_states[-1][0]  # (L+T, d)
        L, T = prompt_ids.shape[1], comp_ids.shape[1]
        return h[L - 1 : L - 1 + T].float().mean(dim=0)

    # --- internals ---

    def _chat_ids(self, user_prompt: str):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
        encoded = self._tokenizer.apply_chat_template(
            messages, add_generation_prompt=True, return_tensors="pt"
        )
        # transformers version drift: newer releases return a BatchEncoding,
        # older ones a bare tensor.
        return getattr(encoded, "input_ids", encoded).to(self.device)

    def sample_batch(self, user_prompt: str, n: int, *, temperature: float | None = None,
                     register=None) -> list[Candidate]:
        import torch

        self._require_loaded()
        temperature = self.config.temperature if temperature is None else temperature
        input_ids = self._chat_ids(user_prompt)

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
                num_return_sequences=n,
                max_new_tokens=self.config.max_new_tokens,
                do_sample=temperature > 0,
                temperature=temperature or None,
                top_p=self.config.top_p,
                pad_token_id=self._tokenizer.eos_token_id,
                return_dict_in_generate=True,
                output_scores=True,
                output_hidden_states=True,
            )

        # With inputs_embeds (no input_ids), sequences holds generated tokens
        # only: (n, T_max_emitted). pad_token == eos, so a sequence's real
        # length runs through its FIRST eos; everything after is padding.
        sequences = out.sequences
        eos = self._tokenizer.eos_token_id
        lengths = []
        for row in sequences:
            hits = (row == eos).nonzero()
            lengths.append(int(hits[0]) + 1 if len(hits) else row.shape[0])

        # Per-step last-layer states at the emitting position: (T, n, d).
        # hidden_states[t][-1] is (n, seq_t, d) — seq_t = prompt at t=0, else 1.
        states = torch.stack(
            [h[-1][:, -1, :].float() for h in out.hidden_states[: sequences.shape[1]]]
        )
        # Per-step token log-probs under the sampling logits: (T, n).
        logprobs = torch.stack([
            torch.log_softmax(step_scores.float(), dim=-1)
            .gather(-1, sequences[:, t : t + 1])
            .squeeze(-1)
            for t, step_scores in enumerate(out.scores)
        ])

        candidates = []
        for i in range(sequences.shape[0]):
            length = lengths[i]
            text = self._tokenizer.decode(sequences[i][:length], skip_special_tokens=True)
            candidates.append(Candidate(
                text=text,
                code=extract_code(text),
                mean_logprob=float(logprobs[:length, i].mean()) if length else None,
                prompt_tokens=prompt_tokens,
                generated_tokens=length,
                phi=states[:length, i].mean(dim=0) if length else None,
            ))
        return candidates

    @staticmethod
    def make_candidate(text: str, **kwargs) -> Candidate:
        return Candidate(text=text, code=extract_code(text), **kwargs)
