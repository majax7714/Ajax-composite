# Architecture audit — is "family" a proxy for something we never measured?

*Opened 2026-07-27, between Phase 22's close and any Phase 23 charter, at the author's
instruction: "we've found consistently that what we measured was not what we were measuring —
worth a look up before progressing through a further phase." Not a phase. No spend. Literature
plus $0 measurement on committed data. Append-only.*

---

## 0. The question

Every family contrast in this record compares models that differ in **many** things at once.
The record has been calling that variable "family" or "training diet." This audit asks what
else moves with it.

---

## 1. What actually differs between the four models

Sources: [Qwen2.5-Coder Technical Report](https://arxiv.org/html/2409.12186v1),
[StarCoder2 and The Stack v2](https://arxiv.org/pdf/2402.19173),
[deepseek-coder-1.3b-base](https://huggingface.co/deepseek-ai/deepseek-coder-1.3b-base).
Vocabulary sizes independently confirmed by loading each tokenizer locally.

| | Qwen2.5(-Coder)-1.5B | DeepSeek-Coder-1.3B | StarCoder2-3B |
|---|---|---|---|
| layers × hidden | 28 × 1536 | 24 × 2048 | 30 × 3072 |
| attention | **GQA** 12 q / 2 kv | **MHA** 16 | **GQA + sliding window 4096** |
| vocabulary | **151,646** | **32,000** | **49,152** |
| embeddings | **tied** | untied | untied |
| context | 32k | 16k | 16k (4k SWA) |

**Four architectural variables move together with "family": attention scheme, vocabulary size,
embedding tying, and depth/width ratio.** No cell in this record separates them.

**The one clean contrast in the entire record is `Qwen2.5-Coder-1.5B` vs `Qwen2.5-1.5B`** —
identical 28×1536, identical GQA, identical tokenizer, tied embeddings both, differing only in
the Coder continued-pretraining stage. **Phase 20 measured it at +0.0088 ± 0.0157, p 0.57 —
null.**

> **The only architecturally clean comparison this record has ever run found no difference,
> and every comparison that found a difference is architecturally confounded.**

---

## 2. H-VOCAB — measured, $0, and it lands

**Hypothesis.** §6's string-space PULL is a *token-level* process scored in *string* space. A
model reproducing an in-context artifact emits it token by token; with finer tokenization each
step is a shorter, easier prediction. So PULL may be measuring **tokenizer granularity**, not
anchoring strength.

**Measurement.** Tokens-per-character of committed candidate code under each model's own
tokenizer, against Phase 22's PULL:

| model | vocab | **tokens/char** | **PULL** |
|---|---|---|---|
| DeepSeek-Coder-1.3B | 32,022 | **0.3935** | **+0.764** |
| StarCoder2-3B | 49,152 | **0.3590** | **+0.623** |
| Qwen2.5-1.5B | 151,665 | **0.3164** | +0.435 |
| Qwen2.5-Coder-1.5B | 151,665 | **0.3164** | +0.418 |

**Spearman(tokens/char, PULL) = +1.000.** And the two models with *identical* tokenizers land
adjacent in PULL (0.418 / 0.435), exactly as the confound predicts.

**What this does and does not do.**

- It **does** mean the *cross-family ordering* of PULL — the thing §6 got excited about, that
  "DeepSeek copies nearly twice as hard" — **cannot be read as a model property.** It is
  rank-indistinguishable from a tokenizer property.
- It **does not** touch §8's universal: PULL is positive in all eight cells (+0.163 to +0.764),
  so conditioning drags every model toward the artifact in string space regardless.
- It **does not** explain within-tokenizer variation: Coder-1.5B 0.418, Coder-3B 0.564,
  Coder-7B 0.408, general-1.5B 0.435 all share one tokenizer and span 0.16.
- **phi-1 breaks it** (+0.163, on a ~51k-vocab CodeGen tokenizer that should predict ≈0.62).
  Marked, not explained away. n = 4 with **3 distinct tokenizers** is weak, and a rank
  correlation of +1.000 over three values is nearly uninformative on its own — it is the
  identical-tokenizer pair landing adjacent that carries the weight.

**Status: the cross-family PULL ordering is withdrawn as a model-level claim** and recorded as
confounded with tokenization. Third hypothesis retired today, again for $0.

---

## 3. H-EMBED — a new candidate for the scale boundary, and it fits better than scale does

The record's live scale statement is: sink **present at 1.5B and 3B, absent at 7B**. "Scale"
has never explained *why* 7B escapes. Here is a variable that is not scale and orders the data
better. Embedding parameters as a fraction of total (vocab × hidden ÷ total params;
**computed, not vendor-reported** — treat as approximate):

| model | vocab × hidden | ≈ embedding share | measured |
|---|---|---|---|
| Coder-**0.5B** | 151,936 × 896 | **≈28%** | **UNADJUDICATED** (§0.4 open rung) |
| Coder-1.5B | 151,646 × 1536 | ≈15% | **SINKS** |
| general-Qwen-1.5B | 151,646 × 1536 | ≈15% | **SINKS** |
| Coder-3B | 151,936 × 2048 | ≈10% | **SINKS** |
| Coder-7B | 152,064 × 3584 | ≈7% | **CLEAN** |
| StarCoder2-3B | 49,152 × 3072 | ≈5% | void / ambiguous |
| DeepSeek-1.3B | 32,000 × 2048 | ≈5% | clean by 0.0008 |
| phi-1 | ≈51k × 2048 | ≈8% | sub-threshold sink |

**Every model at ≥10% sinks. Every model at ≤7% is clean or ambiguous.** That threshold
separates the data better than family (which Phase 20 killed) and better than raw scale
(DeepSeek-1.3B is *smaller* than Coder-1.5B and does not sink).

**A sharp, falsifiable prediction:** **Coder-0.5B, at ≈28%, should sink hardest of any cell in
the record.** It is already §0.4's open rung, and it is a Qwen-Coder model — so family, diet,
tokenizer and prompt are all held fixed while the proposed variable is pushed to its extreme.
A scale account predicts the opposite direction of nothing in particular; H-EMBED predicts a
specific extremum.

*Honesty about what this is:* a **post-hoc ordering over eight points with hand-computed
numbers**, generated after seeing the outcomes. It is a hypothesis for pre-registration, not a
finding, and it must be tested on a cell whose result is not yet known.

---

## 4. Rejected on inspection — H-SWA

StarCoder2-3B has a **4,096-token sliding window**. If conditioned prompts exceeded it, the
model would lose the problem statement while retaining the artifact — an architectural
mechanism for arm asymmetry. **Rejected on direction:** truncation would hit the *longer*
conditioned prompts, but the observed parse deficit is in the **i.i.d.** arm (0.9167 vs
0.9717). The mechanism predicts the wrong arm. Recorded because it was checked, not because it
survived.

---

## 5. What this changes about the record's own history

**Phase 15's result now reads differently.** It found attention *concentration* tracked the
sink across three model pairs and died to the fourth — the one holding architecture fixed —
and concluded concentration is "a property of the architecture, not of the pathology." That
conclusion is correct and now has a candidate referent: **GQA (2 KV heads) versus MHA (16
heads)** is an architectural difference in attention structure large enough to produce exactly
that. The record measured a real thing and named it vaguely.

**The pattern the author identified is now three-for-three.** Position (Δ_art) confounded the
family contrast; conditioning-induced format compliance confounded the parse-rate contrast;
tokenizer granularity confounds the string-space contrast. **In every case the confound was a
property of the *instrument* that happened to correlate with the *grouping variable*.** That is
now a standing hazard with a name, and it belongs in §10.

---

## 6. Recommendation for Phase 23

**Do not run the n≈200 DeepSeek cell.** It is the obvious successor and it is the wrong buy:
it would spend real money resolving a contrast that is confounded four ways regardless of the
answer. Whatever it returned, the record could not attribute it.

**Two candidates that are not confounded:**

1. **Coder-0.5B at true match — tests H-EMBED where family, diet and tokenizer are all fixed.**
   §0.4 already lists the rung as open, and §0.2 notes it could not be placed at its own
   straddle by mining, so it needs generated artifacts. Directional prediction committed above.
2. **A DeepSeek scale ladder (1.3B vs 6.7B)** — repeats the Qwen ladder's *structure* inside a
   different architecture. If the sink appears at DeepSeek-6.7B's embedding fraction and not at
   1.3B's, family is dead as an explanation for good; if neither sinks, architecture is
   carrying more than diet.

(1) is cheaper, tests a variable this audit generated, and keeps every confound fixed. It is
the recommendation.
