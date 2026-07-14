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
