# Phase 21 — **STUB, NOT CHARTERED.** Written at the halt; awaiting author decision.

*Created 2026-07-26 at the Phase-20 halt ([AUTONOMOUS_LOOP.md] §3.1 — a result refuted a
LIVE claim 1:1). **Revised the same day** after the author pressed on whether the proposal
was the most logical *given the total evidence*, and whether the relationship should have
been found in the literature. Both pushes changed this document. **No spend has occurred
and no pre-registration is frozen.***

---

## 0. What the revision changed, and why

The first draft of this stub proposed *"do DeepSeek-1.3B and StarCoder2-3B sink at true
match?"* — a **family** question. That framing is wrong, and it is wrong in the same way the
thing it was meant to fix was wrong: **it presumes the family axis is the right axis**, which
is precisely the assumption Phase 20 just falsified.

Two corrections, both landed in the journal before this rewrite:

1. **§11 now carries the null the record never posed** — Huang et al., *LLMs Cannot
   Self-Correct Reasoning Yet* (arXiv 2310.01798, ICLR 2024): intrinsic self-correction fails
   and *sometimes degrades*, worst in small models, with apparent gains attributable to
   sampling and selection rather than critique content. Our prompt carries ~2 bits of
   feedback, which §9.3 already concluded supplies no direction — so our setting is nearer
   *intrinsic* than *fed-back*. **"Conditioning degrades generally, worse in small models"
   was always the prior, and this record attributed to family/diet for thirteen phases
   without ever putting the general null on the page.**
2. **§10 gains the balance rule and §0.3 gains the balance table** the record lacked, and
   §8 gains the forward-obligation rule. The imbalance was visible in Phase 7's own committed
   artifact.

**So the question is no longer "which family."** It is: **is the sink a general small-model
conditioning effect, or is something specific about Qwen — and is DeepSeek the real
exception rather than "non-Coder" as a class?**

---

## 1. What the corpus says once every cell is put on a common footing

The compression intercept estimates each cell's effect *at* Δ_art = 0. Phase 20 validated the
method out-of-sample: it predicted **−0.0398** for the twin and measured **−0.0372**.

| model | size | family | intercept at match | measured at match? |
|---|---|---|---|---|
| Coder-0.5B | 0.5B | Qwen-Coder | −0.029 | no |
| DeepSeek-1.3B | 1.3B | DeepSeek | **+0.011** | no |
| Coder-1.5B | 1.5B | Qwen-Coder | −0.056 | **yes, −0.046/−0.064** |
| general-Qwen-1.5B | 1.5B | Qwen | −0.040 | **yes, −0.037** |
| StarCoder2-3B | 3B | StarCoder2 | −0.021 | no |
| Coder-3B | 3B | Qwen-Coder | −0.058 | **yes, −0.051** |
| Coder-7B | 7B | Qwen-Coder | −0.020 | **yes, −0.008** |

**This is a gradient, not a dichotomy, and "non-Coder" is not the seam.** Both Qwen models
sink; StarCoder2 is intermediate and its CI includes zero; **DeepSeek-1.3B is the only model
whose intercept is positive.** Within Coder the effect is non-monotone in size — peaking at
1.5–3B and shrinking at both 0.5B and 7B — which is *compatible* with a small-model story but
not a clean instance of one.

**The honest reading: the record's one genuinely clean model is DeepSeek, and it has been
carrying the entire "non-Coder families are clean" generalisation on its own.**

---

## 2. The recommended phase — reframed

**Question:** *at true match, on shared problems, paired against a common reference — which
models fail to beat the copy null, and does the pattern follow size (the general null),
architecture family, or DeepSeek alone?*

**Design:** exactly Phase 20's machinery (`_p20_select`, per-problem per-model artifacts,
paired, k=48, gates inside the branch expression), extended to **DeepSeek-1.3B** and
**StarCoder2-3B**, each paired against Coder-1.5B on shared problems.

**Committed predictions, from the validated intercept method, to be frozen before the run:**

| cell | predicted at-match effect | predicted verdict |
|---|---|---|
| DeepSeek-1.3B | **+0.011** [−0.015, +0.033] | clean |
| StarCoder2-3B | **−0.021** [−0.067, +0.022] | ambiguous, leaning slightly negative |

**What each outcome means — and note that the general null is now a live branch, not an
afterthought:**

| outcome | reading |
|---|---|
| both sink | **the general null wins.** The sink is a small-model conditioning effect; the family axis collapses entirely and §0.2's Qwen-pathology extraction is dead |
| both clean | **DeepSeek + StarCoder2 vs both Qwens** → a Qwen-base effect, and the extraction survives with "Coder" replaced by "Qwen" throughout |
| DeepSeek clean, StarCoder2 sinks | **DeepSeek is the exception**, not a family class; the interesting question becomes what DeepSeek does differently — its compression slope is among the highest measured (0.78), i.e. it imitates the artifact most faithfully |

**Owed before freezing** (§8 entry 12): a k=24 i.i.d. sweep for each new model, the
per-problem feasibility count at ±0.10, and the achieved-SE projection with implied MDE
stated in advance together with what it cannot resolve. **Estimated $1.20–2.00 for both.**
MTD **$86.83** against $100 report / $120 hard stop.

---

## 3. Alternatives, ranked and rejected

- **Re-measure the twin.** Phase 20 carried an independent verifier that agreed on every
  quantity and the sibling replicated its committed value. Confirmation adds little.
- **Chase the mechanism** (head ablation, corrected design, ~$2). Premature: a mechanism
  phase aimed at "the Coder diet" would be aimed at something the record no longer believes.
- **A non-Qwen model at 7B** to test size against family directly. The *most* decisive design
  against the general null — but it needs a new >15 GB download, which is [AUTONOMOUS_LOOP.md]
  §3.6 author sign-off, and the loop is already halted.
- **The compression law's origin.** Its P0 is already landed and free (`h21_p0_eiv.json`);
  genuinely interesting and possibly the record's most novel product, but a new thread while
  a central claim sits refuted.

---

## 4. Already landed at the halt (free, no spend)

`scripts/j21_p0_eiv.py` → `artifacts/h21_p0_eiv.json`. The compression law was fit with the
**same estimated i.i.d. on both axes**, which biases the slope upward through shared noise for
any data. Corrected with two independent i.i.d. estimates and then de-attenuated for
errors-in-variables — the two biases run in **opposite** directions, so correcting only one
would have been its own error:

| cell | published | decorrelated | **EIV-corrected** |
|---|---|---|---|
| Coder-1.5B | +0.6366 | +0.5812 | **+0.6030** |
| Coder-3B | +0.7871 | +0.6672 | **+0.7048** |
| general-Qwen-1.5B | +0.6585 | +0.6212 | **+0.6437** |

**The law survives**, overstated by a mean of +0.044 (~6% relative), every corrected CI
excluding zero. Phase 19's position-confound argument moves 1.34× → 1.26×, unchanged.

---
