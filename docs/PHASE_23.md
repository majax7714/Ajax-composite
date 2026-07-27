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
