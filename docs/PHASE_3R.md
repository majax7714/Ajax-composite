# Phase 3R — three audits before any claim is published

*Written 2026-07-14, after Phase 3a returned F2 (gate NEGATIVE). External review found
three unexamined assumptions inherited from frozen Phase-0 choices. R1 and R2 audit
existing claims (must run before publication); R3 is the new evidence. Order: R1a →
R1b → R2 → R3 (R1 cheapest, highest stakes). **Standing rule: append, never revise;
pre-register every prediction before its run and leave it standing.***

---

## R1 — Did anything corrupt H1, the only positive result?

### R1a — Provenance of the logprob bug. **DONE 2026-07-14 → H1 is bug-clear.**

**The bug (fix commit `00ddc84`, Phase M):** vLLM's `CompletionOutput.cumulative_logprob`
is `None` unless `SamplingParams(logprobs=…)` is set. `modal_phasem.py::m3_generate`
did not set it, so every `mean_logprob` was `None` and the likelihood-argmax silently
picked candidate 0. A **vLLM-API-specific** defect in the port.

**Was it present in Phase-1 H1?** No, on three independent checks:
1. The fix touches only `scripts/modal_phasem.py` (the vLLM port); the diff is purely
   the `cumulative_logprob`→`logprobs=1` change.
2. Phase-1/0 computed `mean_logprob` on the **HF** path (`src/rgr/generator/model.py`:
   `mean(log_softmax(out.scores)[sampled_token])`), written in `86c48ea` (Phase 1) and
   **never changed since** — a different mechanism that computes from real scores at
   generation time and cannot silently produce `None`.
3. The Phase-0 lock H1 scored (`artifacts/lock_a.jsonl`) has **0/1312 `None`**
   `mean_logprob` (range [−0.457, −0.005]) — the likelihood arm was fully populated
   with real values.

**Verdict: the bug was port-introduced, caught before it contaminated M3, and never
touched H1.** H1's likelihood baseline on the retired HF/4-bit stack is intact *with
respect to this bug*; the ΔAUROC +0.099 and 0.628→0.671 numbers stand as reported.
(This clears the *bug*; the *quantization* question is R1b and is still open.)

### R1b — Was H1 measuring verification, or measuring quantization damage? *(pre-registered before run)*

M4 already showed V-v2b's within-problem edge over likelihood collapsing **+0.15 →
+0.016** on the bf16 candidate distribution — global AUROC held (V didn't get worse),
but likelihood got *better* (best-of-8 0.6280 → 0.7256, +10 pts). Hypothesis: 4-bit
NF4 corrupts the logits, so H1's "external beats self-fluency" partly reduces to
"external beats *quantization-corrupted* self-fluency."

**Procedure.** On the bf16/vLLM M3 pool: (1) recompute the full H1 head-to-head with
the **existing** V — within-problem macro AUROC (primary), pooled AUROC (secondary,
labelled), best-of-8 pass@1 for V and likelihood; then (2) **retrain V on the bf16
distribution** (regenerate MBPP-train candidates + labels on bf16, retrain the QLoRA
cross-encoder) and retest, isolating staleness from the quantization effect.

**R1b.1 RESULT (2026-07-14, stale 4-bit-trained V on the bf16 M3 pool,
`artifacts/r1b_h2h_stale_v.json`):**

| metric | V | likelihood | edge (V − lik) | retired 4-bit H1 |
|---|---|---|---|---|
| within-problem AUROC (primary) | 0.6462 | 0.6306 | **+0.016** | +0.151 |
| pooled AUROC (secondary) | 0.7719 | 0.6809 | +0.091 | +0.099 |
| best-of-8 pass@1 | 0.6646 | **0.7256** | **−0.061** | (V 0.6707 vs lik 0.6280, +0.043) |

**The verifier's edge over likelihood is gone, and on best-of-8 pass@1 it *reverses*:
on the non-quantized generator, likelihood-reranking (0.7256) beats the stale verifier
(0.6646).** This is the "H1 partly measured quantization-corrupted self-fluency"
signature — bf16 likelihood is a much stronger baseline (0.628→0.726). Pooled AUROC
still favours V (+0.091), but pooled mixes cross-problem difficulty (§4.2's own
caveat); the *within-problem* number — what reranking uses — is +0.016. The decisive
question is now R1b.2: does a V **retrained on the bf16 distribution** recover the
edge, or is the edge intrinsically gone off the quantized generator?

**Pre-registered prediction (committed before running):** the edge is **partially
restored but far below the original +0.15** — I expect retrained-V within-problem
minus likelihood ≈ **+0.03 to +0.08** (best-of-8 V a few points above likelihood but
not the ~4-pt original margin). Both effects are real: V was stale (retraining helps)
*and* bf16 likelihood is a genuinely stronger baseline (harder to beat). So **H1
survives directionally but weakened, with an explicit caveat that quantization
inflated the apparent verifier gain** — the honest headline gains a methodological
warning (rerankers benchmarked on quantized models overstate their edge). If retrained
V−likelihood stays ≈0, H1 does not generalize off the quantized generator and the
headline changes to "neither carried load; the verifier gain was substantially a
quantization artifact." **Blocking: no H1 claim in any draft until R1b closes.**

### R1b.2 — the addendum: SE metric + three free checks, then the retrain

**Selection Efficiency (primary, stack-invariant):**
`SE = (selected_pass@1 − random_pass@1) / (oracle_pass@8 − random_pass@1)`.

| selector | stack | pass@1 | SE |
|---|---|---|---|
| likelihood | 4-bit | 0.6280 | 0.144 |
| V-v2b | 4-bit | 0.6707 | **0.315** |
| **likelihood** | **bf16** | **0.7256** | **0.305** |
| V-v2b (stale) | bf16 | 0.665 | 0.067 |

**Headline: bf16 likelihood (SE 0.305) reproduces the entire 4-bit verifier benefit
(SE 0.315) for free.** The whole of H1's gain was obtainable by not quantizing the
generator. And likelihood's improvement is not a pool effect — it gained +0.098 pass@1
while B0 gained +0.056 and oracle +0.061 (the ranking signal itself got better: the
direct signature of 4-bit corrupting the logits).

**R1b.2a — pool composition (4-bit, free).** Failing-candidate error shares: wrong_answer
0.707, runtime 0.234, no_code 0.022, timeout 0.017, syntax 0.015. *(bf16 composition
deferred to the consolidated pool below.)* `artifacts/r1b2b_stratified_auroc.json`.

**R1b.2b — stratified within-problem AUROC (4-bit) — PREDICTION REFUTED.** The
smoking-gun hypothesis was "V is near chance on the subtle (wrong_answer-only) stratum
→ V learned brokenness, not correctness." It is **wrong**: V discriminates *better* on
subtle than obvious.

| stratum (4-bit) | V AUROC | lik AUROC | edge | n |
|---|---|---|---|---|
| subtle (wrong_answer only) | **0.751** | 0.580 | +0.171 | 43 |
| obvious (any broken) | 0.690 | 0.557 | +0.133 | 47 |

**V learned real correctness signal** (0.751 on subtly-wrong code), not brokenness.
This *partially rescues* V and reframes the question: not "did V learn correctness"
(it did) but "is that signal *redundant* with a clean generator's own likelihood."

**R1b.2c — length-bias check (bf16, free) — PREDICTION HELD; no rescue for H1.**
bf16 likelihood favours *longer* candidates (corr +0.261) which are slightly *less*
correct (corr −0.163), so length bias mildly *hurts* likelihood — yet it still hits
SE 0.305; selecting by length alone is terrible (SE −0.222); length-controlled
(sum-logprob) SE 0.281 ≫ stale-V 0.067. **The bf16 likelihood baseline is genuine, not
a length artifact.** `artifacts/r1b2c_length_bias.json`.

*Net of the free checks:* neither shortcut settles it. V learned real correctness (2b),
but bf16 likelihood genuinely captures it too (2c), so the 4-bit V "edge" plausibly
existed only because 4-bit **corrupted the likelihood baseline** (SE 0.144). The
decisive test is whether an on-distribution V beats *clean* likelihood (SE 0.305).

**R1b.2d — the retrain (GPU; run after the consolidated bf16 pool).** Regenerate
Phase-1 labels from the **bf16** generator on MBPP-train, retrain V-v2b with the
identical D9 recipe (4-bit QLoRA cross-encoder, r16/α32, same schedule — only the
candidate distribution changes), evaluate on the bf16 pool. Optional off-diagonal
(scoring only): score the *4-bit* pool with the bf16-trained V (a large edge there
proves the 4-bit pool is simply easier to discriminate).

**Pre-registered kill criterion for H1 (committed before running):** if retrained-V's
SE on bf16 ≤ bf16 likelihood's **0.305**, H1 does not survive de-quantization.
- retrained SE ≈ 0.31+ → **staleness**; H1 stands restated ("beats likelihood *if
  trained on the deployment distribution*").
- retrained SE ≈ 0.05–0.10 → **artifact**; even on-distribution V can't beat free
  likelihood on a clean generator.
- retrained SE ≈ 0.15–0.25 → **partial**; report the decomposition honestly.

**Pre-registered prediction:** given 2b (V learned real correctness) but 2c (likelihood
genuine), I now expect **partial, edge-of-significant** — retrained-V SE ≈ **0.33–0.38**,
a *small* real edge over likelihood's 0.305 (V's correctness signal is partly
complementary, partly redundant). H1 survives **weakened**, with the quantization
caveat front and centre. The artifact outcome (SE ≈ likelihood) stays live.

---

## R2 — Re-screen with the tail un-suppressed *(pre-registered before run)*

F2 ("shallow tail is structural") rests on a Phase-0 decoding config with three
independent **tail-suppressors**: `top_p = 0.95` (nucleus truncates the improbable
tail — the exact thing we hunt for), `temperature = 0.8` (never swept; pass@k tail
depth rises with the k-appropriate temperature), and **Instruct** tuning (SFT/RLHF
collapse generation entropy; base/completion models have far deeper pass@k tails — the
Codex/AlphaCode reason for sampling from base models). F2's honest current scope is
"instruct Qwen at T=0.8/top-p=0.95 has a shallow tail." The gate is really 2-D
(benchmark × scale × **decoding**); Phase 3a searched only the first two.

**Procedure.** Re-screen (random samples only; first-n bias documented, D15) on the two
in-band-but-headroom-failing configs — **BigCodeBench-Complete** and
**LiveCodeBench-easy** — across: generator {Qwen2.5-Coder-1.5B **base**, Instruct
(comparison)}; `top_p = 1.0`; temperature {0.8, 1.0, 1.2}. (Base is a completion model
— validate the prompt/extraction path before trusting any number.) Plot pass@8 and
pass@50 − pass@8 over the 2-D decoding region against both gate criteria.

**Decision rule (pre-registered):** *any* (model, T, top-p) with pass@8 ∈ [0.30, 0.60]
**and** pass@50 − pass@8 ≥ 0.15 → **F2 retracted as "structural"**, scope narrowed to
the frozen config, gate PASSES, 3b proceeds on that config. *No* point clears across
base+instruct × 3 temperatures × un-truncated → **F2 strengthened** (survives the
strongest attack; decoding confound ruled out) — publish as structural.

**Pre-registered prediction (committed before running):** base + T=1.0–1.2 + top-p 1.0
deepens the tail **materially** (base pass@k tails are much deeper), plausibly past
+0.15 headroom on BigCodeBench-Complete — **but pass@8 likely drops below the 0.30
band** as per-sample quality falls. Most likely outcome: a **trade-off curve**, not a
clean pass — the two criteria move oppositely along temperature. My best guess is that
**at least one point clears both** (e.g. base near T=1.0 holding pass@8 ~0.30–0.40 with
headroom ~0.15–0.20), so I predict **F2 gets retracted-as-structural** — but with real
uncertainty; a clean trade-off with no feasible point is the second-most-likely and is
itself the most informative version of F2.

---

## R3 — Conditional reachability: the new experiment (the paper's central claim)

The gate measured **pass@50 − pass@8 = the i.i.d. tail** — but feedback-conditioned
refinement *changes the distribution*; reaching regions i.i.d. sampling never visits is
the whole point. So the i.i.d. tail is **not** a prerequisite for the mechanism the
diagnostics support (fork (ii)); F2 does not constrain it. And F2 hands us the perfect
stratum: **every problem with pass@50 = 0** is one where i.i.d. provably fails in 50
tries — a large, clean, pre-identified test bed.

**Question:** *on problems where i.i.d. resampling provably fails (pass@50 = 0), does an
error-abstraction-conditioned model ever reach a solution?* Not "does refinement
improve pass@1" — does conditioning reach what sampling cannot.

**Design.** Stratum = pass@50 = 0 problems from the best-tailed R2 config. Matched
compute, 8 steps, three channels: **B1-50** (i.i.d. resample — control, ≈0 by
construction), **ANCHOR** (previous candidate + error abstraction — the known-poison
channel, DIAG-8/10), **ABSTRACT** (error abstraction only, no candidate text — the
claim). Error abstraction = failing test names + counts + error class + exception/diff
(rich, not DIAG-10's ~2-bit `error_type` — hence R2's benchmark must be feedback-rich).
**Primary metric: absolute recovery COUNT** (B1's expected count ≈ 0, so a rate is
meaningless).

**Pre-registered predictions (committed before running):** B1-50 recovers ≈ 0
(definitional sanity — if many, the stratum is mislabelled / k=50 estimate unreliable,
a red flag); **ABSTRACT recovers > 0 and > ANCHOR** — my genuine guess is a modest but
non-trivial count (roughly **5–20%** of the stratum: the subset where the model *has*
the capability but repeats a specific error an abstraction can unstick), demonstrating
conditioning reaches beyond the i.i.d. envelope; ANCHOR ≈ 0 or worse (anchoring tax
replicates on hard problems). **Kill:** ABSTRACT ≈ 0 → feedback-conditioned refinement
cannot exceed the i.i.d. envelope even on its best-case stratum with rich feedback →
the refinement direction is dead, a clean final negative that forecloses F2's escape
hatch.

**Add-on (Addendum III §4) — cross feedback-richness × temperature.** The escape-distance law reframes ABSTRACT's mechanism as *directed escape*: temperature supplies escape energy, rich feedback supplies escape direction. So run ABSTRACT (and B1-50) across T ∈ {0.8, 1.2} × feedback ∈ {~2-bit `error_class`, rich abstraction}. **Prediction:** the two are *substitutes at the margin* (either buys some escape) but *complements in the limit* (only rich-feedback × high-T gives directed escape; undirected escape at high T is just resampling, so 2-bit × high-T ≈ B1-50). If rich feedback adds nothing that temperature alone cannot buy (pure substitutes), that is a **deflationary result about the whole self-refinement paradigm** — worth stating plainly, first.

---

## 4. The adjusted claim (what this is all for)

Not the register, not F2. The mechanism the diagnostics isolated, which R3 converts
from "removes harm" to "adds reach":

> **In iterative self-refinement, the previous candidate is the poison and the feedback
> is not.** Same execution signal, ±the failed candidate text: the candidate-anchored
> channel anti-refines while the abstraction channel does not (+0.225 late-step gap,
> DIAG-10; consecutive candidates 0.35× as diverse as i.i.d., DIAG-8). The self-refine
> literature bundles "show the model its output and the error" into one move; we
> decompose it and the harm lives entirely in one half. Free, actionable: **drop the
> failed candidate from the refinement prompt; pass only the error abstraction.**

Framing the record already supports: **test-time compute is two axes** — generative
(sample/refine, bounded by the pool tail) and selective (verify/rerank, bounded by
verifier quality). On code at 1.5B the generative axis is exhausted by k ≈ 8
(pass@50 − pass@8 ≈ +0.10) while the selective axis has ~18 points unclaimed (oracle
pass@8 0.9024 vs achieved 0.7256) — **iff R1b survives**; if V's edge is really +0.016,
the selective axis is unclaimed *and we have no working method for it*, and it must be
stated that way. Falsifiable prediction: refinement research keeps failing to replicate
as base models improve (bf16 raised coverage, cut headroom; the larger model raised
coverage +0.14, headroom +0.02).

---

## 5. Sequence & gates

1. **R1a** — bug provenance. *DONE → H1 bug-clear.*
2. **R1b** — H1 on bf16, within-problem primary; retrain V on-distribution, retest.
   *Gate: does V's edge survive off the quantized generator? Blocking on any H1 claim.*
3. **R2** — base + top-p 1.0 + temperature sweep re-screen. *Gate: any point clears both
   criteria → F2 retracted-as-structural; else F2 strengthened.*
4. **R3** — conditional recovery on the pass@50 = 0 stratum. *Gate: does ABSTRACT
   recover anything? The new evidence and the central claim.*

Predictions committed above before each run; left standing whether they hold or not.

---

## Addendum II (2026-07-14) — judge fix, D-measure, BEST-SO-FAR

**§1 judge fix — DONE (`d6cbf37`).** The Phase-3a judges destroyed downstream signal:
lcb_exec short-circuited on first failing case; bcb_exec recorded counts only. Both now
emit per candidate `{passed, n_tests, n_passed, frac, failing[], err, exc}`. §1.1
persistence check: candidate pools ARE persisted → re-execution is CPU-only (no GPU
regen). Screen verdicts (pass@8/headroom) are unaffected. R1b.2d + R2-gen untouched.

## D-measure — is anchoring about "self" at all? *(parallel, pre-registered before run)*

Every anchoring measurement (DIAG-8 edit-dist, DIAG-9b error-echo, DIAG-7 coverage) is
*distributional* — none requires the artifact to be the model's own. If anchoring is
distributional, it is a fact about **conditional generation** (tokens in context pull
the distribution toward themselves), and self-refinement is merely the special case.
Single-step conditioning on committed HumanEval pools, no loop, no reachability.

| # | context artifact | framing | isolates |
|---|---|---|---|
| E0 | nothing | — | i.i.d. baseline |
| E1 | own failed candidate (this problem) | "your previous attempt" | standard self-refine (≡ B2) |
| E2 | **byte-identical** failed candidate | "a submission from someone else" | **PROVENANCE** |
| E5 | a **correct** candidate (this problem) | "a previous attempt" | **SIGN** of the attractor |
| E3† | failed candidate from 0.5B | "someone else" | genuinely external source |
| E4† | failed candidate from a different problem | "a previous attempt" | problem-relevant vs raw token gravity |

Tier 1: E0/E1/E2/E5 (†E3/E4 if budget). **PULL** = normalized edit distance (1 −
SequenceMatcher, == DIAG-3/8) of the new generation to the conditioned artifact
(measurable at any T incl. greedy). **TAX** = pool coverage of 8 conditioned vs 8 i.i.d.
(only meaningful at T>0). Temperature T ∈ {0.0, 0.8, 1.2}.

**Pre-registered predictions:** (a) **E1 ≈ E2** (~60/40) — provenance irrelevant; the
mechanism is distributional conditioning, distinct from Tsui's blind spot (would also
predict "Wait" won't fix it). If E2 pulls markedly less → it *is* Tsui on code, our
result a special case. (b) **E5 pulls as hard as E1 but with high pass rate** (~75%) —
the attractor is **neutral**, it amplifies whatever it's aimed at; every harm in the
record is from *what we aimed it at*, not anchoring per se. (c) **TAX monotone
increasing in T, → 0 at greedy** — reconciles Self-Debug (greedy → pool size 1 → they
collect the pull without paying the tax). Output: `artifacts/dmeasure_conditioning.json`.

**RESULTS (2026-07-14, N=60 HumanEval, task `bmeetye9d`).** *Predictions above stand as written; outcomes appended.* PULL = `1 − SequenceMatcher.ratio(gen, artifact)` (**low = near-reproduction, high = divergence**); coverage = pass@ns any-pass (greedy ns=1, T>0 ns=8 — a confound flagged below). E1/E2 share the *same* failed artifact so their PULL is directly comparable; E5's PULL is to a *different* (correct) artifact.

| cond@T | PULL | coverage | TAX vs E0 |
|---|---|---|---|
| E1  0.0 / 0.8 / 1.2 | 0.075 / 0.176 / 0.309 | 0.20 / 0.52 / 0.62 | +0.45 / +0.40 / +0.28 |
| E2  0.0 / 0.8 / 1.2 | 0.043 / 0.068 / 0.157 | 0.10 / 0.22 / 0.40 | +0.55 / +0.70 / +0.50 |
| E5  0.0 / 0.8 / 1.2 | 0.020 / 0.066 / 0.168 | **1.00 / 1.00 / 1.00** | **−0.35 / −0.08 / −0.10** |
(E0 coverage 0.65 / 0.92 / 0.90.)

- **(a) E1 ≈ E2 — FALSIFIED.** Framing produces a large, consistent split in *both* axes at every T. But the split runs **opposite to Tsui**: the pre-registered trigger was "E2 *pulls markedly less* (anchors less) → Tsui on code." Instead E2 **anchors *more*** (lower edit distance to the failed artifact: 0.043/0.068/0.157 vs E1 0.075/0.176/0.309) while **repairing *less*** (coverage 0.10/0.22/0.40 vs E1 0.20/0.52/0.62). So provenance/framing matters, but "your previous attempt — improve it" is a *better* repair scaffold than "someone else's submission — write a correct solution," which is the reverse of a self-anchoring blind spot. **Caveat (honest):** E1↔E2 differ in provenance label *and* instruction verb ("improve" vs "write correct") — a bundled contrast, so the repair-rate gap is not cleanly attributable to provenance alone. Not clean Tsui, not clean provenance-irrelevance.
- **(b) E5 neutral attractor — SIGN CONFIRMED (emphatically), magnitude reframed.** Aim the attractor at a *correct* artifact and coverage → **1.00 at every temperature** (TAX negative — conditioning *adds* pass-coverage vs i.i.d.). At greedy it near-reproduces the correct code (PULL 0.020 → sim 0.98). The attractor amplifies **whatever it is aimed at**: aimed at failure, coverage collapses to 0.10–0.62; aimed at success, 1.00. The "pulls as hard as E1" clause is not directly testable (different target artifact), but reproduction-strength is symmetric across sign. This is the empirical charter for **BEST-SO-FAR**. **[RETRACTED — Addendum III §1. E5 (a *fully correct* artifact) is answer-leakage: greedy coverage 1.00 at PULL 0.020 = 98% string copy of the answer we handed it. That charters nothing about the *partial-credit* regime BEST-SO-FAR lives in. What survives: E5's PULL (0.020/0.066/0.168) ≈ E2's (0.043/0.068/0.157) → the attractor's strength is invariant to whether the target is correct — content-blindness, the defensible "neutral attractor." The real BEST-SO-FAR premise test is D2c/E6.]**
- **(c) TAX monotone↑ in T, →0 at greedy — FALSIFIED as measured.** E1 TAX is *largest* at greedy and *decreases* in T (0.45 → 0.40 → 0.28). Two reasons: (i) the metric is pass-coverage tax, not the diversity tax the prediction imagined; (ii) greedy ns=1 vs T>0 ns=8 confounds the greedy row. The clean unconfounded facts (matched ns at T>0): conditioning on a **failure** costs 0.28–0.70 pass-coverage; conditioning on a **success** gains it. **Self-Debug reconciliation survives, but via a different mechanism than predicted:** Self-Debug helps not because greedy dodges a diversity tax, but because execution-guided repair aims the attractor at a *corrected* target (E5-like, negative tax) rather than a raw failed one (E1/E2-like, positive tax).

**Headline.** Anchoring is a **neutral distributional attractor** whose sign is set entirely by its target: every harm in the RGR record traces to conditioning on failures, and E5 shows the same mechanism yields total success when aimed at a correct artifact. Directly motivates BEST-SO-FAR (aim it at the best candidate seen). Provenance is *not* irrelevant, but the effect is a framing/instruction bundle opposite to Tsui's self-anchoring direction, not a "self" blind spot. **[SUPERSEDED — Addendum III §1/§6-D2a. The "opposite to Tsui" directional read overclaims: E1↔E2 confounds attribution with the *verb* ("improve it" vs "write a correct solution"), and the verb alone predicts the whole split a priori. E1 vs E2 is therefore *uninterpretable* for provenance; the Tsui question is OPEN pending the D2a 2×2. No related-work/provenance claim may be made until D2a returns.]**

## Addendum III (2026-07-14) — the escape-distance reframe *(D-measure re-read; predictions above stand)*

D-measure's own writeup buried the finding and leaned on a leaked answer (E5). Corrections, append-only:

**§1 — E5 retracted as "charter"; content-blindness kept.** See the inline `[RETRACTED]` on the (b) bullet. E5 conditioned on a *fully correct* solution → the model copies it (greedy PULL 0.020, coverage 1.00). That is answer-leakage, and it is the degenerate endpoint (copying is optimal), not the partial-credit regime BEST-SO-FAR occupies. The defensible residue: **E5 PULL ≈ E2 PULL** → attractor strength is invariant to target correctness = **content-blindness**. The mechanism does not know what it points at.

**§2 — the escape-distance law (the actual finding).** Sort every failure-conditioned cell by PULL:

| PULL (escape distance) | coverage |
|---|---|
| 0.043 (E2, T=0) | 0.10 |
| 0.068 (E2, T=0.8) | 0.22 |
| 0.075 (E1, T=0) | 0.20 |
| 0.157 (E2, T=1.2) | 0.40 |
| 0.176 (E1, T=0.8) | 0.52 |
| 0.309 (E1, T=1.2) | 0.62 |

Monotone across two conditions × three temperatures (one trivial inversion). **When conditioned on a failure, the single variable that predicts repair is how far you escape it** — not provenance, not framing. Anchoring *is* failure-to-escape. E1 vs E2 differ only in escape distance; temperature is an escape knob; E5 is the degenerate case where escape is unnecessary. One variable subsumes the run and absorbs the prior record: DIAG-8's 0.35× diversity, DIAG-9b's error-echo, DIAG-7's coverage collapse are all *low escape distance* measured three ways.

**§3 — temperature is an anti-anchoring intervention, dose-responsive (the cleanest result, ns=8 throughout — no confound).** Hold ns=8, move T 0.8→1.2:

| condition | T=0.8 → 1.2 | Δ coverage |
|---|---|---|
| E0 (no anchor) | 0.92 → 0.90 | −0.02 — flat |
| E1 (anchored) | 0.52 → 0.62 | +0.10 |
| E2 (more anchored) | 0.22 → 0.40 | +0.18 |

Temperature rescues **only** the anchored conditions (unanchored E0 is already saturated), and the effect is **dose-responsive**: E2 (more anchored, lower PULL) gains ~2× E1. This belongs in the paper as a first-class finding. (D2b re-reports it on the confound-free mean-per-sample-pass metric.)

**D2b RESULTS (2026-07-14, re-executed committed pool; confound-free metric).** Reporting **mean per-sample pass** (consistent across T; greedy is just pass@1) alongside coverage sharpens the mechanism and forces one honest correction:

| cell (ns=8) | PULL | mean_pass | cov(any) |
|---|---|---|---|
| E1 @0.8 / 1.2 | 0.176 / 0.309 | 0.237 / **0.200** | 0.52 / 0.62 |
| E2 @0.8 / 1.2 | 0.068 / 0.157 | 0.108 / 0.129 | 0.22 / 0.40 |
| Δ mean_pass, T 0.8→1.2 | | E0 **−0.181** · E1 −0.037 · E2 **+0.021** | Δcov: E0 −0.02 · E1 +0.10 · E2 +0.18 |

- **Escape-distance law is a *coverage* (pass@k) law, not a per-sample-quality law.** Coverage is monotone in PULL (clean), but **mean per-sample pass is flat** — E1 sits at ~0.20 at every temperature. Escape buys pass@8 by **spreading the 8 samples so one lands**, not by making each attempt better. Refines §2: "how far you escape predicts *coverage*" — via diversity.
- **Temperature dose-response holds on coverage, and the ordering survives on mean_pass** (E2 +0.021 > E1 −0.037 > E0 −0.181), so the "more-anchored-benefits-more" claim is robust — but it too is a coverage/diversity effect. For unanchored E0 the extra temperature just *degrades* per-sample quality (−0.181) with coverage already saturated.
- **Consequence for R3/BEST-SO-FAR:** conditioning **relocates the distribution** (coverage) without lifting per-sample quality. "Reach what i.i.d. can't" is a diversity/coverage phenomenon — consistent with R3's distribution-shift framing, and it sharpens the BEST-SO-FAR deflation (§5): copying a near-miss won't raise its per-sample frac_tests, exactly as predicted. Output: `dmeasure_conditioning.json` → `per_sample_D2b`.

**§4 — prediction (c) was falsified *backwards*; the corrected reconciliation is sharper.** I predicted TAX rises with T, →0 at greedy. It *falls* (0.45→0.40→0.28): higher T buys escape, so **greedy is the worst case for anchoring, not the safe one** (PULL 0.043–0.075 = near-total reproduction). The "greedy has no pool to collapse" reconciliation is *refuted*, not repaired. Corrected: **escape needs a direction.** Self-Debug conditions on a failure *and supplies rich execution feedback* (traces, line-by-line) that tells the model where to diverge:

- B2, no feedback → *undirected* escape → the model copies (PULL 0.075–0.309, coverage collapse).
- B2+fb, ~2 bits (5-way `error_class`) → not enough to direct escape → still declined (−0.162).
- Self-Debug, traces + explanations → *directed* escape → it works.

**Escape requires direction; direction requires rich feedback.** This is R3's thesis with a mechanism. It predicts a **feedback-richness × temperature interaction** (substitutes at the margin — both buy escape; complements in the limit — T supplies escape *energy*, feedback supplies *direction*; undirected escape at high T is just resampling). Folded into R3 (§ below). *If they are pure substitutes, feedback does nothing temperature couldn't do more cheaply — a deflationary result about self-refinement we'd be first to state.*

**D2a RESULTS (2026-07-14 — the Tsui gate; pre-registered prediction CONFIRMED).** 2×2, all cells conditioned on the *same* failed artifact, so the two contrasts are clean:

| contrast | held fixed | ΔPULL (T=0/0.8/1.2) | Δmean_pass |
|---|---|---|---|
| **provenance** (E1 self − E2′ other) | verb = "improve" | −0.012 / −0.019 / −0.028 | +0.050 / +0.025 / **+0.006** |
| **verb** (E1 "improve" − E1′ "write-correct") | attribution = "your" | +0.042 / +0.096 / **+0.115** | +0.067 / +0.096 / +0.040 |

- **Provenance is near-irrelevant: E1 ≈ E2′.** Telling the model the failed code is "someone else's" vs "your previous attempt" barely moves PULL (≤0.028) or pass (→+0.006), and the gap *shrinks* with temperature. The verb ("improve it" vs "write a correct solution") drives the split, at **3–4× the magnitude**, and it does so *through escape distance* — "improve" diverges more (higher PULL) and repairs more, consistent with §2.
- **Resolves the `[SUPERSEDED]` Tsui flag on the (a) bullet.** The mechanism is **provenance-independent distributional conditioning — distinct from Tsui's self-anchoring blind spot** (it is not about "self"; the "Wait"/attribution family of fixes would not touch it). This is *our* result, and the related-work claim is now unblocked. It is also **not** "opposite to Tsui" (that read is retired) — it is orthogonal: Tsui's axis (whose output) is inert here; the live axis is escape distance.
- **Replicates the escape-distance law** across all 12 cells (coverage roughly monotone in PULL), on a fresh 4-condition run, with mean_pass again flat (~0.10–0.23) — corroborating D2b's "coverage via diversity, not per-sample quality."

**Follow-ups (all parallel to R2; none gates it):** D2b (metric fix, free CPU — *done, §D2b above*) · D2a (verb×provenance 2×2 — *done, Tsui gate CONFIRMED*) · D2c/E6 (partial-credit conditioning — the real BEST-SO-FAR premise test, rides R2's enriched pools). Outputs: `dmeasure_conditioning.json` (per_sample_D2b), `dmeasure_d2a_verb_provenance.json`, `dmeasure_d2c_partial_credit.json`.

## BEST-SO-FAR — point the attractor at a success *(pre-registered; rides R2's enriched pools)*

If E5 confirms the attractor is neutral, the fix isn't *remove* the candidate — it's
*aim it at a success*. Conditions on R2's selected (feedback-rich) benchmark, matched
compute: **B1** (i.i.d.), **LAST** (prev candidate ≡ B2/ANCHOR), **BEST** (highest-
frac_tests seen so far), **ABSTRACT** (error abstraction only), **BEST+ABSTRACT**. Rank
**ORACLE-first** (by execution frac_tests, not the verifier — sidesteps R1b.2: if
oracle-BEST doesn't help, verifier-BEST can't). Primary: pass@1 matched compute.
**Predictions:** BEST > LAST (~80%); BEST vs ABSTRACT genuinely open; BEST+ABSTRACT the
favourite. Depends on §1 (per-test frac) + R2 (feedback-rich pool). Convergence to name:
BEST-SO-FAR = "condition on the lowest-energy candidate seen" = the original relaxation
dynamics, needing exactly the graded landscape the feedback-richness criterion hunted for.

**REVISED predictions (Addendum III §5 — original above stands).** The escape-distance law deflates BEST-SO-FAR: if conditioning reproduces at 83–98% fidelity, conditioning on an 11/27 candidate yields an ~11/27 candidate — you anchor to a *better failure*, you don't fix the remaining tests.

| condition | original | revised |
|---|---|---|
| BEST > LAST | ~80% | ~80% — **stands** (anchors somewhere strictly better) |
| BEST vs B1 | (unstated) | **≈ hold-at-best, no gain** over the pool's best — reproduction fidelity forbids improvement |
| BEST vs ABSTRACT | "genuinely open" | **ABSTRACT favoured** — ABSTRACT supplies *direction*; BEST supplies only a starting point |
| BEST+ABSTRACT | "the favourite" | **the only condition with a mechanism** — best candidate = good start, abstraction = the escape *direction* |

D2c/E6 (partial-credit conditioning) is the premise test: if a ~40–60% candidate reproduces at ~same frac_tests, BEST-alone is dead and BEST+ABSTRACT carries the phase; if frac_tests *climbs*, the attractor does more than copy and BEST-SO-FAR is a bigger result than scoped. ORACLE-first ranking unchanged.

---

## CRASH RECOVERY (2026-07-14, ~18:00 EDT) — power-grid failure mid-run

A city-grid outage killed the local Modal client mid-sweep. All Modal apps were torn
down (`modal app list` → `[]`, no ephemeral tasks survive a client death). **Nothing is
recoverable *from the cloud*** — there is no running remote job to reattach to. Salvage
is therefore exactly what already landed on local disk. Persist-before-exec design paid
off: every candidate **pool** that finished generating was written to `runs/modal/` before
its executor ran, so no generation compute is lost — only the (cheap) execution/scoring
step and the (expensive) R1b.2d retrain need re-running. **No number below crosses a
stack boundary; nothing here is a verdict.** Recovery is exec-only where a pool exists,
full rerun where it does not. *Nothing was re-executed during this assessment (user
directive: salvage-check only).*

**SALVAGED — complete on disk, verdict already written (no action):**

| item | file | status |
|---|---|---|
| R2 base T=1.0 screen | `artifacts/phase3a_screen_r2_base_T10.json` | pass@8 0.241 / pass@50 0.390 / headroom **+0.149** — band ✗, headroom ✗ (by 0.001), gate does-not-qualify |
| R2 base T=1.2 screen | `artifacts/phase3a_screen_r2_base_T12.json` | pass@8 0.092 / pass@50 0.225 / headroom +0.133 — both ✗, does-not-qualify |

These two confirm the **pre-registered trade-off curve** (base deepens the tail
+0.108→+0.149 as T rises, but pass@8 falls out of the [0.30,0.60] band). They stand.

**SALVAGEABLE — pool complete (200 probs × 50 codes, all non-empty), screen NOT written; exec-only, no regen:**

| item | pool on disk | recovery |
|---|---|---|
| R2 base **T=0.8** screen (the pivotal coolest-base point) | `runs/modal/bcb_cand_r2_base_T08.json` (18 MB) | `modal run scripts/modal_phase3a.py::exec_only --tag r2_base_T08` → writes `artifacts/phase3a_screen_r2_base_T08.json`. Pool predates the executor-guard fix (`eec132e`); re-exec now runs the hardened judge. |
| R2 **instruct T=0.8** screen (comparison arm) | `runs/modal/bcb_cand_r2_instruct_T08.json` (8.3 MB) | `modal run scripts/modal_phase3a.py::exec_only --tag r2_instruct_T08` → writes `artifacts/phase3a_screen_r2_instruct_T08.json`. |

**KILLED — needs full regeneration (pool never written):**

| item | why lost | rerun |
|---|---|---|
| R2 **instruct T=1.0** (pool+screen) | outage hit before generation started | `modal run scripts/modal_phase3a.py::r2_screen --arch instruct --temperature 1.0` |
| R2 **instruct T=1.2** (pool+screen) | never started | `modal run scripts/modal_phase3a.py::r2_screen --arch instruct --temperature 1.2` |
| R2 **LiveCodeBench arm** (base+instruct × 3 T) | never started; needs LCB base-path build+smoke first | build LCB base path → `r2_smoke` → `r2_screen --dataset <lcb>` ×6 |
| **R1b.2d retrain + H1 verdict** | died at **epoch 3/3, step ~450/750**; `r1b2d_train_eval` trains+evals in one remote call and returns scores to the local entrypoint — **no `volume.commit` of the adapter** (only volume is `rgr-hf-cache`, the HF download cache), so the trained weights died with the container and `artifacts/r1b2d_verifier_retrain.json` was never written | `modal run scripts/modal_rgr.py::r1b2d_train_main` (regenerates from `runs/modal/r1b2d_mbpp_labeled.json`, which survived — the k=8 MBPP gen at 15:01 is intact, so only the ~3-epoch T4 retrain repeats, not the generation). |

Last-known R1b.2d training signal (bf16 stack; **informational, NOT the verdict, does
not cross any gate**): epoch-1 val AUROC 0.7009, epoch-2 val AUROC 0.7410; epoch 3 was
mid-run when the power died. The kill-line (retrained-V SE ≤ 0.305 → H1 doesn't survive
de-quantization) is **still unresolved** — it never computed.

**F2 gate status after recovery:** still open. Base cleared headroom (T=1.0 at +0.149)
but never the pass@8 band; the two instruct arms that would complete the pre-registered
base+instruct × 3-T grid (T=0.8 salvageable, T=1.0/1.2 to regen) are the missing cells.
The decision rule cannot fire until instruct T=0.8/1.0/1.2 land.

### RECOVERY UPDATE (2026-07-14, salvage exec-only, hardened judge)

**Base T=0.8 salvage LANDED** (`artifacts/phase3a_screen_r2_base_T08.json`, exec-only on
the intact pool, executor-guard `eec132e` active — no re-crash): pass@1 0.144, **pass@8
0.328**, pass@50 0.425, **headroom +0.097**. Band [0.30,0.60] **✓ (first config to clear
it)**, headroom ≥0.15 **✗**, gate does-not-qualify.

This closes the base-temperature axis and **confirms the trade-off has no feasible base
point** (the "clean trade-off, no feasible point" branch of the R2 pre-registration — the
second-most-likely and most-informative outcome):

| base config | pass@8 | headroom | band | headroom≥0.15 |
|---|---|---|---|---|
| T=0.8 | **0.328** | +0.097 | ✓ | ✗ |
| T=1.0 | 0.241 | **+0.149** | ✗ | ✗ (by 0.001) |
| T=1.2 | 0.092 | +0.133 | ✗ | ✗ |

The two criteria move oppositely and **never co-occur** on base: pass@8 needs T ≤ 0.8,
headroom needs T ≥ 1.0. No base point clears both. The instruct comparison arm (T=0.8
salvage exec running; T=1.0/1.2 need regen) is the remaining input before F2's decision
rule fires; on current evidence F2 trends toward **strengthened-as-structural** unless
instruct opens a feasible cell.

**Instruct T=0.8 salvage LANDED** (`artifacts/phase3a_screen_r2_instruct_T08.json`,
exec-only): pass@1 0.137, **pass@8 0.269**, pass@50 0.355, **headroom +0.086**. Band ✗
(0.269 < 0.30 — fails *from below*), headroom ✗, gate does-not-qualify.

**Base beats instruct at matched T=0.8 on both axes** (base 0.328 / +0.097 vs instruct
0.269 / +0.086) — the un-suppressed base completion tail is genuinely deeper, exactly the
R2 pre-registered direction. The remaining un-run cells are instruct T=1.0/1.2 (killed,
need regen); but instruct already fails the band *from below* at its coolest temperature,
and pass@8 falls monotonically with T (base: 0.328→0.241→0.092), so hotter instruct only
moves further from the band. **No config has cleared both criteria; every landed cell
fails, and the one open direction cannot help pass@8.** F2's decision rule formally
requires instruct T=1.0/1.2 to run, but the standing evidence points to **F2 strengthened
as structural** (decoding confound ruled out across the temperature axis for both
architectures). Gate remains open pending those two regen cells.

---

## Addendum IV (2026-07-14) — E5/E1 subset matched-control (§9.3.1's committed action) — CLOSED

**Question.** Were the D-measure cross-condition contrasts corrupted by per-condition
problem filtering — E1/E2 (which need a *failed* artifact) on a hard-biased subset, E5
(which needs a *correct* one) on an easy-biased subset?

**Method (free, CPU, committed data only).** `scripts/dmeasure_subset_control.py` over
`dmeasure_gen/exec.json`, `dmeasure_d2a_gen.json`, `m3_candidates/m3_labels.json`:
recover each condition's actual pid set, reconstruct the selection rule, recompute E0
restricted to E1's subset and to E5's subset. Output:
`artifacts/dmeasure_subset_control.json`.

**Result — the feared confound is structurally absent.**

- All four D-measure conditions ran on **one identical 60-problem subset**; so did all
  four D2a cells; and both runs used the **same** 60 (pid-set equality verified all
  three ways).
- Selection reconstruction: the subset is exactly the **first 60 M3-pool problems with
  both a failed and a correct non-empty candidate** ("mixed-outcome"), in pool order.
- Therefore E0-on-E1's-subset == E0-on-E5's-subset == the published E0 (mean_pass
  0.650 / 0.5875 / 0.4062, coverage 0.650 / 0.917 / 0.900 at T=0/0.8/1.2). The
  committed recompute returns the published numbers identically; **no cross-condition
  contrast ever crossed a subset boundary.**

**What remains is scope, not confound.**

- The shared subset is mixed-outcome-only (91/164 qualify: 56 always-solved, 16
  never-solved, 1 degenerate excluded) and **first-60 of those, not random**. M3
  mean-pass: subset 0.565 vs full pool 0.648 — the subset is ~8 pts *harder* than full
  HumanEval. Absolute magnitudes are scoped to mixed problems; within-subset contrasts
  are unaffected.
- At-risk claim (i) — "conditioning drops per-sample pass": **stands as measured**,
  E0 0.5875 → E1 0.2375 at T=0.8 (−0.350) and 0.4062 → 0.200 at T=1.2 (−0.206), on
  identical problems.
- At-risk claim (ii) — E5's coverage-1.00 / negative TAX: the tautology worry is
  **real but bounded** — every subset problem is solvable-within-8 by construction,
  and the matched-subset E0 is already near-saturated (0.917 / 0.900 at T=0.8/1.2;
  0.650 greedy), so E5's informative margin over its fair baseline is small
  (+0.08–0.10 at T>0). Consistent with the Addendum III §1 answer-leakage retraction
  already in place. Content-blindness (E5 PULL ≈ E2 PULL) is untouched — PULL is
  measured within the same subset.

**Verdict: the escape-distance law, the content-blindness residue, and the
temperature dose-response survive the matched-control check unchanged; magnitude
claims gain a scope note (mixed-outcome, first-60, ~8 pts harder than the full
pool). The pre-registered fear (differential subsets) did not materialize — closed
with no claim change.**
