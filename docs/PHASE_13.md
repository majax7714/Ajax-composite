# Phase 13 — head ablation: the record's first causal intervention

*Charter opened 2026-07-25 with author sign-off on head ablation. Fourth iteration of
the unattended loop. Append-only; pre-registration frozen before spend.*

## 0. Why this is different from every prior phase

Every measurement in this record so far — twelve phases — has been **observational**.
Cells are constructed, models are run, differences are compared. Nothing has ever been
*intervened on*. Head ablation changes that: it manipulates the model's internals and
asks whether the sink follows. That is a different epistemic object, and it is worth
saying plainly at the top, because it is also the first place where a positive result
could license the word **"causes."**

## 1. The fork (documented, per Amendment 1)

Author sign-off named **head ablation**. Taken — but **sequenced**, not jumped to.
Ablation requires *targets*: with 28 layers × 12–28 heads there are 300–700 candidates
per model, and a blind sweep is both unaffordable and underpowered. Phase 12 averaged
over heads by design, so the per-head data does not yet exist.

Therefore **S1 (per-head measurement, cheap) runs first and selects the targets for S2
(ablation)**. If S1 had been skipped, S2 would have been a lottery.

**A methodological constraint discovered while scoping, and it changes S1's question.**
Attention heads are **not comparable across models** — Coder-1.5B, Coder-3B, Coder-7B
and DeepSeek-1.3B have different depths, head counts and learned roles, so "head 7 of
layer 12" denotes nothing in common between them. The cross-model question must
therefore be asked of **architecture-independent distributional statistics**, not of
head identities. S1 is specified accordingly.

## 2. S1 — per-head structure *(cheap; runs first, selects S2's targets)*

Re-run the Phase-12 probe **retaining per-head resolution** (same sequences, same
committed cells, same frozen prompt). Two outputs:

**(a) Cross-model, architecture-independent:** is artifact attention more
**concentrated** across heads in sinking models than clean ones? Reported as the
**top-5% head share** of total artifact attention and the **Gini coefficient** over
per-head artifact attention. Adjudicated under Phase 12's rule: an effect counts only if
it **tracks sink status across both size pairs** (1.5B vs 1.3B *and* 3B vs 7B).

**(b) Within-model, for targeting:** rank Coder-1.5B's heads by mean artifact attention.
This is a *selection* step, not a test, and produces S2's ablation set.

| # | S1 prediction | odds |
|---|---|---|
| 1 | concentration tracks sink status across both pairs | **30%** |
| 2 | no consistent concentration difference (as with the mean in P12) | **55%** |
| 3 | technical failure | **15%** |

## 3. S2 — the intervention *(gated on S1 producing a target set)*

**Model:** Coder-1.5B (the strongest, best-powered sinker: −0.052 at n = 44, P11).

**Ablation mechanism.** A forward pre-hook on `self_attn.o_proj` zeroing that head's
slice of the projection input (`[h·d_head : (h+1)·d_head]`) — architecture-agnostic for
the llama-style blocks both families use. Frozen: **K = 16** heads.

**Four arms, same problems, same artifacts, same seed, all generated through the *same*
HF path** — this is essential and is the phase's main methodological risk. The record's
sink numbers were produced by **vLLM**; an HF-generated arm is not directly comparable to
them, so the baseline must be re-established inside this phase rather than borrowed:

| arm | context | ablation |
|---|---|---|
| **B0** | none (i.i.d.) | — |
| **B1** | full conditioning | none — **the HF-path sink baseline** |
| **B2** | full conditioning | top-K artifact-attending heads (from S1b) |
| **B3** | full conditioning | K heads chosen at random, seed-fixed — **the control for "ablating any 16 heads hurts"** |

**The quantity of interest is not "does B2 differ from B1" but whether B2 moves the sink
*more than B3 does*.** Ablating 16 heads degrades a model somewhat no matter which ones;
B3 prices that.

**Pre-registered decision rule.** Let `sink(arm) = mean_cond − mean_artifact`.

| # | branch | reading | odds |
|---|---|---|---|
| **A** | `sink(B2)` is closer to zero than `sink(B1)` **by more than** `sink(B3)` is | the artifact-attention channel is **causally involved** in the degradation — the first causal statement this record could make | **35%** |
| **B** | B2 and B3 move the sink by indistinguishable amounts | the degradation does **not** flow through the top artifact-attending heads; consistent with P12's magnitude null, and it pushes the mechanism further from attention routing | **40%** |
| **C** | both ablations destroy performance (B2 and B3 fall below the i.i.d. arm) | K too large; uninformative, recorded as an instrument miss with K revised in a successor, **not** re-run at a tuned K inside this phase | **20%** |
| **D** | technical failure | recorded | **5%** |

**B is favoured over A** for the reason P12 supplies: if attention *magnitude* to the
artifact does not distinguish sinking from clean models, there is no strong prior that
removing the highest-magnitude heads will remove the sink.

**Validity conditions, frozen.** B1 must reproduce a sink on the HF path
(`sink(B1) ≤ −0.03`); if it does not, the phase reports **INCONCLUSIVE on instrument** —
the intervention cannot be interpreted against a baseline that does not show the effect,
and no arm comparison is adjudicated. n ≥ 30 problems. Judge and criterion unchanged
(all-cases judge; below-both-nulls reporting).

**What a positive result would and would not license.** A would license *"ablating these
heads reduces the degradation"* — a causal claim about a manipulation. It would **not**
license *"these heads implement the sink"* or any story about what the heads compute;
head ablation is a lesion study, and lesions localise contribution, not function.

**Cost estimate: $0.50–2.00.** S1 ≈ $0.05 (forward passes; P12 cost $0.02 and this adds
only per-head retention). S2 is four arms × ~40 problems × 8 candidates ≈ 1,300
generations on 1.5B through **HF generate**, which is materially slower than vLLM —
the widest band in this estimate, and the reason it is a band. Reconciled at close per
[AUTONOMOUS_LOOP.md] Amendment 2, which has now been calibrated for generation workloads
(accurate) but was 20–50× high for forward-pass-only work (P12).

Loop spend before this phase: **$1.40** of the $90/$110 envelope; month-to-date
**$79.44** of the $200 cap.

---

*(Results append below.)*
