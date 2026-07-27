# Phase 23 — the bottom of the ladder: does the sink have a lower edge?

*Charter opened 2026-07-27. Fourteenth iteration of the unattended loop ([AUTONOMOUS_LOOP.md],
Amendments 1–6). Opened out of [ARCHITECTURE_AUDIT.md], which was itself opened at the author's
instruction to look before spending. Append-only; frozen before spend.*

---

## 0. Why this question — and an honest correction to the audit that proposed it

[ARCHITECTURE_AUDIT.md] §3 proposed **H-EMBED**: the sink tracks embedding-parameter fraction
(≥10% sinks, ≤7% clean) rather than family or raw scale, and predicted **Coder-0.5B at ≈28%
should sink hardest of any cell in the record.**

**That prediction cannot do the work the audit claimed.** Within the Qwen-Coder family,
*smaller* and *higher embedding fraction* are **perfectly correlated** — 0.5B is both the
smallest rung and the highest-fraction one. A plain "smaller is worse" account makes the same
prediction. **Coder-0.5B therefore does not discriminate H-EMBED from scale**, and the audit
should not have implied it would. The one point in the record that *does* discriminate them is
DeepSeek-1.3B (smaller than Coder-1.5B, so scale says sink; 5% embedding, so H-EMBED says
clean; measured clean-ish) — and the audit's own central finding is that DeepSeek is confounded
four ways, so it cannot carry the weight either. **H-EMBED is not testable with the models this
record has.** Recorded here rather than quietly dropped.

**What Coder-0.5B *can* answer is a different and better question.** The at-match effects
across the committed ladder are **non-monotone**:

| rung | at-match cond−iid | embedding share |
|---|---|---|
| **0.5B** | **UNMEASURED — open since Phase 7 (§0.2)** | ≈28% |
| 1.5B | −0.045 / −0.048 | ≈15% |
| 3B | −0.051 | ≈10% |
| 7B | −0.008 | ≈7% |

1.5B and 3B are indistinguishable and 7B is clean, so the record has an **upper** edge and no
information about a **lower** one. Every account currently on the table — smallness,
embedding fraction, competence — predicts *deeper* going down. But there is a competing shape
the record has hinted at since §0.2's "narrow competence window": **a model too weak to use an
artifact may be too weak to be dragged down by one.**

> **The question:** going down from 1.5B, does the sink keep deepening — or does it have a
> **lower edge**, making the curve an inverted-U in scale rather than a monotone slide?

This closes the record's **oldest open rung** (open since Phase 7) and discriminates between
two live shapes, which is more than the phase the audit originally recommended would have done.

---

## 1. Step 2a — literature check *(Amendment 5; performed before this charter was frozen)*

**(a) The general-effect null.** Huang et al. (arXiv 2310.01798) — degradation under
self-correction is worst in small models. **A 0.5B model degrading is the null, not a finding.**
Branch A below is written so that this null wins by default; only branches B and C carry
information beyond it.

**(b) The embedding/vocabulary literature already owns H-EMBED's general claim, which is why
this charter does not test it.** [Scaling Laws with Vocabulary: Larger Models Deserve Larger
Vocabularies](https://arxiv.org/abs/2407.13623) (NeurIPS 2024) establishes that optimal
vocabulary follows a power law in model size and that mis-matched vocabulary costs quality; a
mechanism is reported elsewhere — at 32k vocab **97.6%** of tokens receive >100 updates versus
**7.3%** at 2M vocab, i.e. large vocabularies starve per-token embedding updates. Weight-tying
analyses independently place the point where tying stops mattering at **1–3B parameters**,
which is exactly the range where this record's sink is present and above which it vanishes.
**Consequence:** "embedding fraction matters for small models" is established prior art and
this record may not claim it. Only its *application to in-context conditioning degradation*
could be novel, and §0 explains why this phase cannot establish that application. *Snippet-level
except the Tao et al. abstract; marked accordingly.*

**(c) What the search did not find:** any report of a **lower edge** — a scale below which
in-context conditioning stops degrading a model because it is too weak to be anchored. The
inverted-U shape, if it appears, appears unpre-empted.

---

## 2. Design

**Model.** `Qwen/Qwen2.5-Coder-0.5B`, the revision already pinned in `J7_MODELS`
(`M5_coder0p5b`). Family, diet, tokenizer, prompt and harness identical to the 1.5B/3B/7B rungs
— this is a **within-family** cell, so none of the audit's four confounds vary.

**Steps.** (i) k=24 i.i.d. sweep over the 80-problem donor pool (**1,920** generations).
(ii) Per-problem artifact selection nearest 0.5B's own i.i.d., tolerance ±0.10 — the
`_p20_select`/`_p21_select` rule, unchanged. (iii) Two arms at k=24, seed **433**.

**THE FLOOR, AND THE HEADROOM RESTRICTION — pre-registered.** Phase 7's M5 measured 0.5B at
mean i.i.d. **0.1229**. A model near the floor cannot fall far: on a problem where its i.i.d.
is 0.02, no sink beyond −0.02 is expressible, and the copy null is likewise near zero. **The
donor pool makes this concrete: 1,317 of 4,000 candidates sit below frac 0.05.** Matching 0.5B
per-problem would therefore hand it near-zero artifacts on many problems, where the
below-both-nulls criterion has nothing to detect.

**Restriction, fixed in advance:** the cell is built only from problems where 0.5B's k=24
i.i.d. is **≥ 0.08**, guaranteeing measurable headroom. This selects problems 0.5B handles
relatively well; that is a **stated scope limit, not a correction** — the cell measures the sink
where 0.5B has room for one, and says so.

**The floor does not block the test.** To match the record's deepest at-match effect (−0.051)
a problem needs i.i.d. ≥ 0.051 for the effect to be expressible at all; the ≥0.08 restriction
clears that with margin. **The test is not floor-blocked and the arithmetic is stated before
the run.**

**Primary statistics.** cond − i.i.d. and cond − artifact, bootstrap CI over problems (seed
439, B = 8000); **below-both-nulls** requires both CIs to exclude zero.
**Co-primary, pre-registered — the relative sink** `(cond − iid) / iid`. Absolute effects are
not comparable across quality levels when one cell sits near the floor; the relative statistic
is. Both are reported for this cell **and recomputed for the 1.5B/3B/7B rungs** so the ladder
can be read in one currency. Committed relative values for comparison, from at-match cells:
1.5B −0.045/0.331 ≈ **−0.136**; 3B −0.051/0.643 ≈ **−0.079**; 7B −0.008/0.753 ≈ **−0.011**.

### Frozen decision rules and kill criteria — *per-cell, evaluated inside the branch expression*

- **CELL VOID** ⟺ parse rate < 0.95 in either arm **or** between-arm parse gap > **2.0pp**
  (§8 entry 13 — the differential is the operative quantity).
- **OFF-TARGET** ⟺ achieved aggregate Δ_art outside **±0.020**.
- **INFEASIBLE** ⟺ fewer than **30** problems satisfy (i.i.d. ≥ 0.08) **and** (an artifact
  within ±0.10 exists). **This is a real possible outcome, not a formality** — Phase 7 recorded
  0.5B as un-sample-able at the straddle, and if it is un-sample-able at true match too, that
  is the honest answer to a rung open since Phase 7 and it closes as INFEASIBLE.

### Branches, with odds committed before the run

| | branch | reading | odds |
|---|---|---|---|
| **A** | sinks **as deep or deeper** than 1.5B (cond−iid ≤ −0.045, below both nulls) | monotone accounts survive; **no lower edge**. Note this is also the **literature's null** (§1a) — small models degrade — so it is the *least* informative substantive outcome | **25%** |
| **B** | sinks, but **shallower** than 1.5B on BOTH absolute and relative statistics | **inverted-U: the sink has a lower edge.** A model too weak to use an artifact is too weak to be dragged down by one. The scale story becomes a competence *window*, reconnecting to §0.2's original framing | **35%** |
| **C** | does **NOT** sink (below-both-nulls false) | a **hard** lower edge, and the strongest version of B. Would also refute H-EMBED at its own extreme — the highest embedding fraction in the record, clean | **20%** |
| **D** | INFEASIBLE, void, or off-target | no adjudication; if INFEASIBLE, the rung is declared un-measurable in this instrument and closed as such | **20%** |

**A discriminating note fixed in advance:** absolute and relative statistics can disagree —
0.5B could be shallower in absolute terms purely because it has less room. **B requires BOTH**
to be shallower than 1.5B's (−0.045 absolute, −0.136 relative). If they disagree, the phase
reports **UNCLASSIFIED** and the disagreement is the finding, because it means the floor is
doing the work.

### Power, stated in advance

Projected from the committed ladder's per-arm spread at k=24: per-cell SE ≈ **0.014** at n ≈ 40,
MDE ≈ **0.044**. That resolves a 1.5B-sized effect (−0.045) at roughly 80% power and **cannot
resolve a −0.02 effect** — so a shallow-but-nonzero result will be reported with that limit
attached, and branch C requires the CI to exclude zero rather than merely containing it.
**Variance at the floor is likely lower** (fracs compressed toward 0), which helps; that is an
expectation, not a promise.

### Cost

**Estimate $0.55–1.20.** Basis: Phase 22 measured **$0.000197/generation** on 1.5B-class models;
this is ~3,840 generations (1,920 sweep + 2 × ~40 × 24 arms) of a **0.5B** model, i.e. smaller
and cheaper per generation, giving ≈**$0.76** central. MTD **$91.80** (2026-07-27) against
Amendment 6's **$130 report / $200 hard stop**. Loop total to date $13.72.

---

## 3. Pre-registration freeze

Frozen at commit `PENDING` (stamped at close), **before** any Phase-23 generation ran.

---

## 4. Step-9a search plan — *committed with this charter, before any result*

| if the branch is | queries | a hit that would change the reading |
|---|---|---|
| **A** | "small language model in-context degradation monotone scale code"; "sub-1B model conditioning harm" | a documented monotone in-context degradation curve would make this a replication of the general null, not a finding |
| **B / C** | "inverted U scale in-context learning ability threshold"; "model too small to use demonstrations exemplar"; "emergent in-context copying threshold parameters" | prior documentation of a **lower** scale edge for in-context influence would pre-empt the inverted-U, and would be the single most important citation this phase could find |
| **D** | "benchmark floor effect small model pass@k evaluation headroom" | prior treatment of floor-limited evaluation would give the INFEASIBLE verdict a citation instead of an anecdote |

**Every branch:** re-check Huang et al. (§11), and record what the search **failed** to find.

---

## 5. RESULT — **BRANCH C fires by the frozen rule, and the frozen rule is not what happened**

*Closed 2026-07-27. Raw artifact committed **unread** at `96f1e83`.*

| quantity | value |
|---|---|
| n | **31** (32 dropped for headroom, 17 for no artifact within ±0.10) |
| achieved Δ_art | **+0.0018** |
| mean i.i.d. / cond / artifact | 0.2919 / 0.2682 / 0.3168 |
| **cond − i.i.d.** | **−0.0236**, CI95 **[−0.0575, +0.0090]** — includes zero |
| **cond − artifact** | **−0.0485**, CI95 **[−0.0773, −0.0225]** — **excludes zero** |
| relative sink | −0.0211, CI95 **[−0.1865, +0.1631]** |
| below both nulls | **false** → branch **C** |
| parse i.i.d. / cond | 0.9772 / 0.9892, gap **1.21pp** (under the 2.0pp void) |

**Branch C's committed text reads "a HARD lower edge." That is not supported and must not be
quoted.** At n=31 the MDE is ≈**0.050** and the interval reaches **−0.0575** — this null cannot
exclude an effect larger than the one measured at 1.5B. **It is an underpowered null, not
evidence of absence.** The point estimate (−0.0236) is directionally shallower than 1.5B's
−0.045, and both pre-registered "shallower" flags fired, so the data leans toward B/C — but the
phase **cannot distinguish A from B from C** and the honest verdict is that the lower-edge
question remains open.

**Two pre-registrations that did something useful by failing.** (i) The **floor concern
dissolved**: the headroom restriction selected almost entirely from the sweep's upper mode
(bimodal — 25 problems under 0.05, 23 in [0.30,0.35)), giving the cell a mean i.i.d. of 0.2919,
so max expressible sink was −0.29 and the floor never bound. The relative statistic was
co-primary *for a problem the design's own restriction removed*. (ii) That relative statistic
proved **useless at this n** — CI [−0.1865, +0.1631], four times the width of the absolute one,
because dividing by small i.i.d. values inflates variance. Both are recorded as
pre-registration misses, and both were only visible because the quantities were committed in
advance.

**Scope, stated plainly.** The cell measures **0.5B on the 31 problems it handles well** — mean
i.i.d. 0.2919, essentially Coder-1.5B's overall quality — not 0.5B at its typical competence
(sweep mean 0.2022). The ladder comparison is also **unpaired**: the 1.5B cell sat on a
different subset. A lower-edge claim from this cell would be confounded with subset selection.

### 5.1 The finding is not the branch — it is which leg produced it

`below_both_nulls` is a **conjunction**: cond−iid AND cond−artifact must both exclude zero.
**These two legs do not carry equal variance.** `cond − artifact` compares an estimated
quantity to a **fixed, exactly-known** number. `cond − iid` compares an estimated quantity to
**another estimated** one, so it carries roughly twice the variance component. Measured across
every committed at-match cell:

| cell | i.i.d.-leg CI width | artifact-leg CI width | ratio | verdict |
|---|---|---|---|---|
| P19 twin | 0.1121 | — | — | clean (i.i.d. leg only) |
| P22 Coder-1.5B | 0.0531 | 0.0377 | 1.41 | SINK |
| P22 general-Qwen-1.5B | 0.0422 | 0.0362 | 1.17 | SINK |
| **P22 DeepSeek-1.3B** | 0.0445 | 0.0174 | **2.56** | **clean — gated by the i.i.d. leg** |
| P22 StarCoder2-3B | 0.0709 | 0.0663 | 1.07 | clean — both legs |
| **P23 Coder-0.5B** | 0.0673 | 0.0547 | 1.23 | **clean — gated by the i.i.d. leg** |

**The i.i.d. leg is wider in every single cell.** And of the three "clean" verdicts with an
artifact leg measured, **two — DeepSeek and now Coder-0.5B — have an artifact leg that
decisively excludes zero.** Both models are measurably **below the copy null**. Their clean
verdicts rest entirely on the noisier leg failing to resolve.

> **"Clean" in this record has systematically meant "the higher-variance leg could not be
> resolved," not "no effect."** Three verdicts, one mechanism — and the first of them, Phase
> 19's twin, was already proven wrong by a better-powered design in Phase 20.

That is now **§8 entry 16**, and it changes how every clean verdict in the record should be
read, including the one this phase just produced.

### 5.2 Cost

**$0.6702** measured — MTD **$91.7985 → $92.4687**, snapshot taken in the launching shell —
against a pre-registered **$0.55–1.20** with $0.76 central. **Inside the band, 12% under
central.** Cheapest phase in the record. MTD $92.47 against $130 / $200.

### 5.3 Process failure: no verifier was written before this run

Phases 20, 21 and 22 each committed an independent verifier **before** any result existed.
**Phase 23 did not.** The re-derivation in §5.1 was run *after* the artifact landed — it agrees
to four decimals, but a check written after seeing the answer is worth strictly less than one
written before, and the record should not pretend otherwise. Logged as **§8 entry 17**.
