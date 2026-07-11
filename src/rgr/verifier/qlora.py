"""V-v2b at inference: the QLoRA cross-encoder as a VerifierLike (D9).

Loads the frozen 4-bit base + the val-selected LoRA adapter and scores
P(correct | problem, candidate code) from raw text. Register-blind (D3) —
the ``register`` argument is accepted and ignored.

Costs a ~1.5B forward pass per call; charged to the ledger's verifier_calls
audit column (COMPUTE_ACCOUNTING.md; primary budget unit is unchanged).
"""

from __future__ import annotations

from rgr.types import Candidate, Problem

BASE_MODEL = "Qwen/Qwen2.5-Coder-1.5B-Instruct"


def pair_text(problem_prompt: str, code: str | None) -> str:
    """MUST stay byte-identical to scripts/phase1_v2b_qlora.pair_text —
    V-v2b was trained on this exact format."""
    return (
        f"{problem_prompt.strip()}\n\n# Candidate solution:\n```python\n"
        f"{code if code is not None else ''}\n```\n# Is this solution correct?"
    )


class QloraVerifier:
    def __init__(self, adapter_path: str, max_length: int = 768) -> None:
        self.adapter_path = adapter_path
        self.max_length = max_length
        self._model = None
        self._tokenizer = None

    def load(self) -> None:
        import torch
        from peft import PeftModel
        from transformers import (
            AutoModelForSequenceClassification,
            AutoTokenizer,
            BitsAndBytesConfig,
        )

        self._tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
        base = AutoModelForSequenceClassification.from_pretrained(
            BASE_MODEL,
            num_labels=1,
            quantization_config=BitsAndBytesConfig(
                load_in_4bit=True, bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16,
            ),
            device_map="auto",
        )
        base.config.pad_token_id = self._tokenizer.pad_token_id or self._tokenizer.eos_token_id
        self._model = PeftModel.from_pretrained(base, self.adapter_path)
        self._model.eval()

    def score_texts(self, pairs: list[tuple[str, str | None]]) -> list[float]:
        """Batched scoring of (problem_prompt, code) pairs."""
        import torch

        if self._model is None:
            raise RuntimeError("call load() first")
        texts = [pair_text(prompt, code) for prompt, code in pairs]
        device = next(self._model.parameters()).device
        enc = self._tokenizer(texts, truncation=True, max_length=self.max_length,
                              padding=True, return_tensors="pt").to(device)
        with torch.no_grad():
            logits = self._model(**enc).logits.squeeze(-1).float()
        return torch.sigmoid(logits).tolist()

    # --- VerifierLike ---

    def score(self, problem: Problem, candidate: Candidate, register=None) -> float:
        if candidate.code is None:
            return 0.0  # deployment rule: unextractable code is an automatic failure
        return self.score_texts([(problem.prompt, candidate.code)])[0]
