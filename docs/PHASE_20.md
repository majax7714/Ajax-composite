# Phase 20 — the paired twin-vs-sibling cell: does the architecture twin sink *less*?

*Charter opened 2026-07-26. Eleventh iteration of the unattended loop
([AUTONOMOUS_LOOP.md], Amendments 1–4a). Author instruction: "good to continue with the
paired twin vs sibling." Append-only; pre-registration frozen before spend.*

---

## 0. What Phase 19 left

Phase 19 measured the architecture twin (`Qwen2.5-1.5B`) at true match and found it
**clean** (−0.0027), against its Coder sibling's −0.0638. Branch A fired. But the charter
had claimed the cell could separate two predictions 0.04 apart, and it could not: achieved
SE 0.0286 gave an **MDE of 0.080**, and the twin-vs-sibling difference came out
**+0.0610 ± 0.0424, p 0.150 — not significant** (§8 entry 12).

The comparison was **unpaired**: each model was matched to its *own* quality, which put them
on different problem subsets. Problem difficulty is the dominant variance component in every
cell this record has run, and an unpaired design pays for all of it.

---

## 1. P0 — free, landed before this charter (`scripts/j20_p0_paired.py`,
`h20_p0_paired.json`)

### 1.1 A paired estimate already existed — and its own gate rejects it

The two committed cells **share 37 problems**. A paired difference is computable on them at
zero cost, so it was — behind a pre-registered position gate, because restricting to a
shared subset is itself a re-selection:

| | Δ_art, full cell | Δ_art, shared subset | drift | within ±0.020? |
|---|---|---|---|---|
| twin | −0.0039 | −0.0025 | +0.0014 | **yes** |
| **sibling** | +0.0015 | **+0.0362** | **+0.0347** | **NO** |

**The gate fires.** The shared 37 put the *sibling* 0.036 above its own quality — off the
match its cell was targeted to — so the free paired estimate (**+0.0537 ± 0.0341, p 0.115**)
**is not usable as a verdict** and is not treated as one.

It is, however, informative twice over. The per-problem **correlation between the two
models' effects is r = +0.415**, so pairing is worth having (it cut the SE 23% at fixed n).
And the sibling's effect on that subset (−0.0359) versus its full cell (−0.0638) differs by
+0.028, against **+0.023 predicted by its own compression slope** at the +0.036 position
drift — **the compression law correctly predicting a within-record shift it was not fitted
on.** Both facts feed the design below.

### 1.2 The power arithmetic, computed before spending — the §8 entry 12 practice

Variance decomposed by subsampling committed candidates (Phase 17's method):

> **SE²(k) = 0.000238 + 0.007301 / k** at n = 37 — irreducible SE **0.0154** as k → ∞.

There is a real between-problem floor, but it is small, so **k is a live lever and n is
capped by the pool at 80 problems**. What that buys:

| target difference | k=8 | k=24 | k=48 | k=96 |
|---|---|---|---|---|
| **0.061** (Phase 19's observed) | n 90 ✗ | **n 43 ✓** | **n 31 ✓** | **n 25 ✓** |
| **0.040** | n 209 ✗ | n 99 ✗ | **n 71 ✓** | **n 57 ✓** |
| **0.016** (compression law's predicted intercept difference) | n 1304 ✗ | n 614 ✗ | n 442 ✗ | n 356 ✗ |

> **Stated plainly, in advance: this design can resolve a difference the size of the one
> Phase 19 observed (~0.05–0.06). It CANNOT resolve the compression law's predicted 0.0166 —
> that needs ~356 problems and the donor pool has 80.** No result from this phase may be
> read as evidence about the smaller hypothesis in either direction.

### 1.3 The design is feasible, and it puts both models at their own match simultaneously

The obstacle is structural: the twin's mean i.i.d. on the pool is **0.3206**, the sibling's
**0.4256**, so *no single artifact set* is at match for both — which is exactly why the
shared-37 gate failed. The resolution is **per-problem, per-model artifact selection**: for
each problem, each model gets the donor candidate nearest to **its own** k=24 i.i.d. on that
problem. The problem set is shared; the artifact is not.

At a per-problem tolerance of ±0.10, **61 of the 80 pool problems** admit a matched artifact
for *both* models, and the aggregate positions land on target:

| | mean i.i.d. | mean artifact | **aggregate Δ_art** | within ±0.020 |
|---|---|---|---|---|
| twin | 0.2939 | 0.2885 | **−0.0054** | ✓ |
| sibling | 0.3603 | 0.3561 | **−0.0042** | ✓ |

29 of the 61 problems happen to give both models the *same* donor candidate; on the other 32
they differ, which is the point — each model is placed at its own relation.

---

## 2. The question

> **On a shared problem set with each model at its own true match, is the architecture
> twin's conditioning effect different from its Coder sibling's?**

This is the record's central causal claim reduced to a single paired number. Everything else
is held fixed — same problems, same donor pool, same selector rule, same k, same seed, same
judge — and the two models differ only in the **Coder continued-pretraining stage**.

---

## 3. Design

- **Models:** `Qwen/Qwen2.5-1.5B` @ `8faed761…` (twin) and `Qwen/Qwen2.5-Coder-1.5B` @
  `df3ce67c…` (sibling) — the revisions already pinned and measured in Phases 7/11/15/19.
- **Problems:** the 61 pool problems admitting a ±0.10 per-problem match for both models,
  selected by the frozen rule in §1.3 and asserted against the committed sweeps at run time.
- **Artifacts:** per problem, per model, the donor candidate nearest that model's own k=24
  i.i.d. — precedent: Phase 9 G2's nearest-to-subset-i.i.d. selection.
- **Arms:** 4 = {twin, sibling} × {i.i.d., conditioned}, **all fresh at k=48, seed 337.**
  The i.i.d. arms are regenerated rather than reusing the k=24 sweeps so that all four arms
  share one seed and one k — Phase 18 measured a 0.114 seed swing on a currency this phase
  depends on, and Phase 19's variance model was fitted on same-k subsamples.
- **Generations:** 4 × 61 × 48 = **11,712**.

**Primary statistic.** Per problem q, `d(q) = [cond_twin(q) − iid_twin(q)] −
[cond_sib(q) − iid_sib(q)]`; report mean(d) with a paired bootstrap CI over problems
(seed 349, B = 8000) and a paired t.

**Pre-registered power.** Projected paired **SE 0.0154**, **MDE 0.0431** at 80%. Against the
best available estimate of the effect (+0.054 from §1.1, itself likely an *under*-estimate
since the sibling sat at a favourable +0.036 there), power ≈ 97%.

### Frozen decision rules and kill criteria — *evaluated inside the branch expression (§8 entry 11)*

- **OFF-TARGET** ⟺ either model's achieved aggregate Δ_art (computed against its committed
  k=24 sweep) falls outside **±0.020** — `P11_ON_TARGET`, 1.8× the powered instrument's
  measured SE.
- **INSTRUMENT FAILURE** ⟺ any of the four arms has parse rate **< 0.95** (Phase 18's lesson).
- **UNDERPOWERED** ⟺ n < 30.

Any of these → **no branch is adjudicated.** All three are evaluated in the same `if/elif`
that selects the branch, not merely printed beside it.

| | branch | reading | odds |
|---|---|---|---|
| **A** | paired CI **excludes zero, positive** (twin sinks *less*) | the DIET attribution gets its first properly-powered, position-controlled, paired direct support. Phase 19's unpaired hint is confirmed | **55%** |
| **B** | paired CI **includes zero** | the two are indistinguishable at MDE 0.043. The twin-vs-sibling difference is smaller than Phase 19 suggested, and the family contrast stays unresolved at achievable precision. This **pressures** the diet claim without refuting it — Phase 9's 2×2 still carries the attribution | **35%** |
| **C** | paired CI **excludes zero, negative** (twin sinks *more*) | contradicts the diet direction outright; would be the most consequential result the loop has produced and would trigger a halt-and-report | **5%** |
| **D** | a kill criterion fires | no adjudication | **5%** |

A is the favourite but deliberately not higher: the two prior estimates (+0.061 unpaired,
+0.054 paired-but-gated) are **the same two cells seen twice, not independent evidence**, and
both had p > 0.11.

### Cost

**Estimate $1.50–2.60.** Basis: Phase 18 ran 6,336 generations of 1.5B-class models on this
judge for a read **$1.06**; 11,712 is 1.85×, giving ≈$1.96 central. Month-to-date read
**$85.40** (2026-07-26) against **$100 report / $120 hard stop**; §4's within-$30-of-cap
guard is satisfied. Loop total to date $7.36.

*Why k=48 and not k=24 (documented fork, Amendment 1).* k=24 costs ≈$1.00 and gives MDE
0.0508 — marginal against a target of ~0.054. k=96 costs ≈$3.92 for MDE 0.0386, since the
between-problem floor dominates past k=48. k=48 is the point where the marginal MDE per
dollar collapses. The record has now failed to resolve this question **twice**; a third
marginal attempt is worse value than one decisive one.

---

## 4. Pre-registration freeze

Frozen at commit `PENDING` (stamped below), **before** any Phase-20 generation ran.

---
