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

Frozen at commit `3e18e67`, **before** any Phase-20 generation ran. The independent
verifier (`scripts/j20_verify.py`) was committed at `583e80d`, while the run was still
generating and before any result existed.

---

## 5. RESULT — ⚠ **a LIVE claim is refuted 1:1. The loop HALTS here (§3.1).**

### 5.1 The cell

All frozen gates pass: twin Δ_art **−0.0054**, sibling **−0.0042** (both within ±0.020);
parse rate **0.99** on all four arms; n = 61 ≥ 30. The independent verifier — committed
before any result existed — rebuilds the selection to n = 61, confirms **32/61 problems
gave the two models genuinely different artifacts**, and reports **ALL QUANTITIES AGREE**.

| | i.i.d. | cond | artifact | **cond − i.i.d.** | **cond − artifact** | below **both** nulls |
|---|---|---|---|---|---|---|
| **TWIN** `Qwen2.5-1.5B` *(non-Coder)* | 0.3004 | 0.2632 | 0.2885 | **−0.0372** [−0.0573, −0.0176] | **−0.0253** [−0.0438, −0.0079] | **YES** |
| **SIBLING** `Qwen2.5-Coder-1.5B` | 0.3508 | 0.3048 | 0.3561 | **−0.0460** [−0.0683, −0.0240] | **−0.0513** [−0.0712, −0.0318] | **YES** |

> **PAIRED difference (twin − sibling) = +0.0088 ± 0.0157, CI95 [−0.0210, +0.0388],
> p 0.5735.** **BRANCH B — indistinguishable**, the 35% branch.

### 5.2 What this refutes

**Claims 8 and 11 both assert, as their family-contrast leg:** *"non-Coder families
(DeepSeek / StarCoder2 / general-Qwen) show **no** code sink at match"*, and from that,
*"the Coder continued-pretraining diet, **not** architecture/tie, not scale."*

**The architecture twin is a non-Coder model and it sinks at true match.** Below its own
i.i.d. **and** below the copy null, both intervals excluding zero — a SINK under the
record's original below-both-nulls definition, the one Phase 10 P0.2 restored. And it
sinks **as hard as its Coder sibling**: the difference is +0.009 with a CI that **excludes**
every prior estimate of it (+0.061 from Phase 19, +0.054 from this phase's own gated P0).

This is not a failure to find a difference. **It is a measurement that the difference is
smaller than 0.039**, on the cleanest control the record possesses — same base, verified
same 28L × 12H, same scale, same problems, same donor pool, same selector, same k, same
seed, same judge, differing only in the Coder continued-pretraining stage.

### 5.3 Why every previous cell missed it — and why the record is coherent, not contradictory

Nothing here contradicts a prior *measurement*; it contradicts a prior *reading*.

- **Phase 7 M2** measured the twin at **Δ_art +0.0642** and got ≈ −0.0001. Phase 19's P0
  already showed why: at that position the twin's own compression (+0.040) almost exactly
  cancels its intercept (−0.040). **Its "clean" verdict was arithmetically a cancellation**,
  and this phase confirms it by removing the cancellation.
- **Phase 19** measured the twin at true match and got −0.0027, CI [−0.0588, +0.0533], and
  called it CLEAN. **Phase 20's −0.0372 sits inside that CI.** Phase 19 was not wrong; it
  was underpowered — the MDE was 0.080 and it recorded that as §8 entry 12. **The very next
  cell demonstrated that the underpowered "clean" verdict was a false negative.** That is
  the strongest possible vindication of writing entry 12 rather than banking branch A.
- **The sibling replicates**: −0.0460 here against P11's −0.0638 (inside its CI). So the
  design reproduces the known Coder sink *and* finds the twin matching it.

### 5.4 What is NOT refuted — stated precisely, because the scope matters

- **Phase 9's 2×2 stands.** At Δ_art ≈ −0.06 with generated artifacts, Coder-1.5B sank
  −0.200/−0.238 while **DeepSeek-1.3B** sank only −0.062. That is a 3–4× family difference
  at matched position and this phase does not touch it. **DeepSeek is a different model from
  general-Qwen**, and the two results are compatible.
- So the surviving statement is narrower and stranger: **general-Qwen-1.5B sinks like
  Coder-1.5B; DeepSeek-1.3B does not.** "Non-Coder ⇒ no sink" is dead. Something separates
  DeepSeek from *both* Qwen models — which points at the **Qwen base**, not the Coder stage.
- **DeepSeek and StarCoder2 have never been measured at true match either** (Δ_art +0.050,
  +0.033 — the same cancellation zone as P7's M2). Their "clean" verdicts are now
  **suspect on exactly the same grounds** and must be re-measured before anything is said
  about families.

### 5.5 Prediction accounting, and the odds that were right for the wrong reason

A 55% / **B 35%** / C 5% / D 5%. **B fires.** The charter read B as *"indistinguishable at
MDE 0.043; the family contrast stays unresolved"* — but B is stronger than the charter
anticipated, because the charter did not consider that **both** models might sink
significantly. The pre-registered reading of B was "unresolved"; the actual content is
"resolved, and against the claim." The odds were right; the interpretation attached to them
was too weak, and that is recorded rather than quietly upgraded.

**Cost $1.43** (MTD aggregate delta $85.40 → $86.83, per Amendment 2) against a $1.50–2.60
estimate — **below the band**, the first under-run in ten estimates. Loop total **$8.79**;
MTD **$86.83** against $100 / $120.

---

## 6. GATE — **HALT AND REPORT (§3 condition 1)**

The loop spec's first halt condition is *"a result directly refutes a LIVE claim 1:1.
Freeze, write it up, stop."* The author's standing instruction is identical and explicit.
**This is that case**, and the loop stops here rather than chartering a successor.

**Frozen for the author:**

1. **A non-Coder model sinks at true match, as hard as its Coder sibling** (−0.0372 vs
   −0.0460, difference +0.009, p 0.57, both below both nulls at power).
2. **The family-contrast leg of claims 8 and 11 is refuted as stated.** The Coder-diet
   attribution's *architecture control* has flipped: the variable the claim names — the
   Coder continued-pretraining stage — does not separate sinking from non-sinking here.
3. **What survives** is Phase 9's provenance-controlled 2×2 (Coder ≫ DeepSeek at matched
   position). The likely revised shape is **a Qwen-base effect rather than a Coder-stage
   effect**, but that is a hypothesis, not a measurement, and no claim should be rewritten
   to it without a cell.
4. **Two cells would settle the shape**, both cheap and both now obvious: **DeepSeek-1.3B
   and StarCoder2-3B at TRUE match**, paired against the sibling exactly as here. If they
   stay clean at match while both Qwen models sink, the claim becomes "Qwen base," not
   "Coder diet." If they sink too, the sink is universal at ≤3B and the whole family axis
   collapses. Estimated $1.20–2.00 for both.

**Nothing is running. Phase 20 is closed and the loop is halted pending author review.**

---
