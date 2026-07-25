# Phase 15 — does attention concentration track the SINK, or the architecture?

*Charter opened 2026-07-25. Sixth iteration of the unattended loop
([AUTONOMOUS_LOOP.md], Amendment 1). Selected by a full-record review rather than as
the continuation of Phase 14 — see §2. Append-only; pre-registration frozen before spend.*

## P0 (free, landed before the charter) — **S1's head-count caveat is DISCHARGED** *(`h15_s1_headcount_control.json`)*

Phase 13 S1 found artifact attention more **concentrated** in sinking models and flagged
its own caveat: the four architectures have different head counts (12H / 16H / 28H per
layer; 336 / 576 / 784 / 384 total) and neither Gini nor top-5% share is obviously
invariant to how many heads it is computed over.

That caveat deserved more than a mention, because **head count is aligned with the
contrast**: the clean model has *more* heads than the sinking model in **both** pairs
(336 sink vs 384 clean; 576 sink vs 784 clean). A statistic that merely drifts downward
with n would manufacture "tracks sink status across both pairs" out of nothing.

S1 committed the full per-head matrices, so this was testable for **$0**
([scripts/j15_s1_headcount_control.py], seed 211, 2,000 subsamples):

| variant | small pair Δ Gini | large pair Δ Gini | tracks? |
|---|---|---|---|
| **as published** (all heads) | +0.0608 | +0.0523 | yes |
| **common total head count** (n = 336) | **+0.0608** | **+0.0521** | **yes** |
| **common heads per layer** (H = 12) | **+0.0613** | **+0.0528** | **yes** |

Top-5% share behaves the same (+0.0140/+0.0302 → +0.0105/+0.0288 → +0.0171/+0.0301).
Head count does not even order the statistic: by total heads the Gini sequence is
336→0.5619, 384→0.5012, 576→0.5506, 784→0.4983 — **not monotone**. The script also
re-derives S1's four committed numbers from the matrices to <0.005 as a check on itself.

**The caveat is discharged. The finding is not a head-count artifact.** Two exposures S1
carried are *not* touched by this and are what Phase 15 is for: **one model per cell**,
and **no error bars of any kind** — S1 reported four point estimates with no uncertainty
over the ~29 problems each was averaged from.

## 1. The question

Coder-1.5B **0.5619** (sinks) · Coder-3B **0.5506** (sinks) · DeepSeek-Coder-1.3B
**0.5012** (clean) · Coder-7B **0.4983** (clean).

Within the Coder family concentration falls monotonically with size (0.5619 → 0.5506 →
0.4983) — so a **size** account is live. It is not *pure* size, because DeepSeek-Coder-1.3B
is the smallest model of the four and sits **low**, which is exactly why S1 was designed on
a 2×2 where sink status is not collinear with size. But with one model per cell, "tracks
sink status" and "tracks size, with DeepSeek off-trend for family reasons" are not
separated by four points.

**The record contains a cell that separates them, already generated and committed, and it
has never been looked at with this instrument: `Qwen2.5-1.5B` (general), the Phase-7 M2
matched cell.** It is the *same base model, same size, and — expected — the same 28 layers
× 12 heads* as `Qwen2.5-Coder-1.5B`, differing **only in the Coder continued-pretraining
stage**. And it is measured **clean** (cond − iid −0.0001, p 0.50, n = 28, [PHASE_7.md] M2).

So it forces the choice directly:

- concentration tracks **sink status** → general-1.5B sits **low**, with the clean group,
  despite being architecturally identical to the highest-concentration model in the record;
- concentration tracks **architecture/size** → general-1.5B sits **high**, with Coder-1.5B,
  and S1's cross-model reading collapses into a size curve with one off-trend point.

No subsampling control can substitute for this: it removes the architecture question **by
construction** rather than by statistics.

## 2. Why this and not the linear continuation *(the fork, per Amendment 1)*

The linear successor to Phase 14 is the **corrected ablation** — re-run with an ablated
i.i.d. arm so `sink(K) = cond_ablated(K) − iid_ablated(K)`, ≈8 arms, ≈$2. It is fully
specified in [PHASE_14.md] and remains open. It is **not** taken now, for three reasons:

1. **It targets heads selected by S1's ranking.** The whole motivation for ablating the
   *top artifact-attention* heads is S1's concentration result. Running a third
   intervention on a selection rationale that has one model per cell and no error bars is
   the record's own named failure mode — deriving from a handful of cells and then
   fitting everything to it (§10, "treading into our own water").
2. **Two ablation phases have already returned nothing about the sink** (P13 branch C,
   P14 vacuous). The prior that a third succeeds without new information is poor.
3. **Order and price.** This phase costs ≈$0.05–0.20 in forward passes against ≈$2, and
   its outcome changes whether the ablation is worth running at all: if concentration is a
   size effect, the ablation's target set has no special status and the design should
   change before it is paid for.

**Options that were live in the full-record review, and why they lost.** *The 3B→7B sink
boundary* (§0.4) — refines the scope of a claim that is already settled and at no risk;
no live claim depends on it. *The stale-stack audit of LIVE rows* — already performed
(§0.3 stack-lineage, Phase 7 P0.3: only row 3 is pre-M and it is already scoped to that
stack), so there was nothing to find. *The synthetic-data family-n = 1 question* (phi-1)
— needs a second non-phi synthetic-code family, i.e. a new model download, which trips
[AUTONOMOUS_LOOP.md] §3.6. *A hostile-reader audit in the Phase-10 style* — Phase 10 was
the loop's highest-yield phase, but its targets (the cost record, the criterion drift, M4)
were found and closed; the equivalent target today **is** S1's support, which is what this
phase attacks.

## 3. Design

Re-run the Phase-12/13 attention probe on **six** committed cells, **retaining per-problem
resolution** (S1 averaged it away, which is why it has no error bars):

| cell | status at match | Δ_art | n | role |
|---|---|---|---|---|
| Coder-1.5B (P11) | **SINKS** −0.052 | +0.0016 | 44 | S1 replication |
| Coder-3B (P11) | **SINKS** −0.051 | −0.0005 | 39 | S1 replication |
| Coder-7B (P10 R5) | clean −0.008 | +0.0023 | 29 | S1 replication |
| DeepSeek-Coder-1.3B (P7 M1) | clean +0.050 | +0.0499 | 39 | S1 replication |
| **Qwen2.5-1.5B general (P7 M2)** | **clean** −0.0001 | +0.0642 | 28 | **the decisive cell** |
| **StarCoder2-3B (P7 M3)** | **clean** +0.008 | +0.0326 | 39 | second size-matched pair |

Same frozen probe as Phase 12 (`eager` attention, bf16, batch 1, `max_length` 1024,
greedy teacher-forcing over `[conditioned prompt] + [the cell's own committed
generation]`). **No new generation** — every sequence already exists in a committed pool.

**Two outputs per model:** (a) the per-head artifact-attention matrix averaged over
problems, exactly as S1 defined it, for continuity; (b) **per-problem** matrices, which
S1 did not keep, enabling a **bootstrap over problems** (2,000 resamples, seed 223) for a
CI on every concentration statistic — the uncertainty quantification the finding has
never had.

**Pairs adjudicated** (S1's frozen both-metrics rule, extended to the new cells):

| pair | sink | clean | controls for |
|---|---|---|---|
| P1 *(S1)* | Coder-1.5B | DeepSeek-Coder-1.3B | — (size-adjacent, different family) |
| P2 *(S1)* | Coder-3B | Coder-7B | family + diet held |
| **P3 (new)** | **Coder-1.5B** | **general-Qwen-1.5B** | **size, architecture, base model — only diet differs** |
| **P4 (new)** | **Coder-3B** | **StarCoder2-3B** | size |

## 4. Pre-registered predictions

| # | branch | reading | odds |
|---|---|---|---|
| **A** | **both new pairs track** (P3 and P4 positive on both metrics) | concentration survives its hardest available test; a size account is excluded by P3, which holds architecture fixed. The strongest correlational statement this record could make about the mechanism | **35%** |
| **B** | **P3 fails** — general-Qwen-1.5B concentrates like Coder-1.5B | concentration is **architecture/scale-linked, not sink-linked**; S1's cross-model reading collapses to a size curve with DeepSeek off-trend, and the ablation thread loses its rationale. Pressures no LIVE claim (S1 was never promoted to one) but retires the record's only positive internal signal | **35%** |
| **C** | **mixed** — P3 tracks, P4 does not (or vice versa) | inconclusive; recorded as a pointer, no claim, and the bootstrap CIs decide whether it is worth a successor | **20%** |
| **D** | technical failure on one or more cells (StarCoder2's attention implementation is the named risk; a per-cell failure does **not** invalidate the others) | instrument miss on that cell, recorded | **10%** |

**A and B are priced level at 35%.** S1 fired as a 30% underdog and has now survived a
head-count control it could have died on, which is genuine evidence. Against that: the
record's newest positive findings have a poor replication record (M4 died at re-run; the
Phase-10 gain law died on 14 cells), P3 is a strictly harder test than anything S1 faced,
and the Coder family's own 0.5619 → 0.5506 → 0.4983 sequence is exactly what a size
effect looks like.

**Reachability check — required by the new §10 rule this record adopted today, applied to
its own first phase.** The adjudicated quantity is `Gini(per-head artifact attention)` and
`top-5% share`, computed **independently per model** from that model's own attention
matrices. No constant is shared between the arms of any pair, and no arm's statistic is a
function of the other's — unlike Phase 14, where both arms were pinned to `y = x − art` by
a shared scalar. The pair differences are therefore free to take either sign, and branches
A and B are **both reachable on real data**; C is reachable whenever the two new pairs
disagree; D on any load/attention-implementation failure. *(Verified symbolically before
freezing, per §10 addendum 2026-07-25 and §8 entry 8 — this is the check whose absence
cost Phase 14.)*

**Validity conditions, frozen.** The four S1 cells are re-run through the same probe on
committed text with greedy teacher-forcing, so they must **reproduce S1's published
statistics to within 0.01** (bf16 nondeterminism only). If they do not, the phase reports
**INCONCLUSIVE on instrument** and no pair is adjudicated — a probe that cannot reproduce
its own prior output cannot be trusted on new cells. General-1.5B's architecture
(28L × 12H) is **verified from the run's own reported dims**, not assumed; if it differs
from Coder-1.5B, P3 loses its "architecture held fixed" status and is reported as a
size-matched pair only.

**What a hit would and would not license.** A would license *"artifact attention is more
concentrated in models that sink, and this is not explained by size, head count, or
architecture."* It would **not** license any causal claim — this is the same
correlational instrument Phase 12 used, and Phase 12's own caveat stands: attention
measurements localise correlation, not function. It would also **not** resurrect the
ablation thread by itself; it would only restore the rationale for designing one properly.

**Cost estimate: $0.05–0.20.** Forward passes only, ~6 models × ~30 sequences, no
generation, model load dominates. **Labelled estimate**, and deliberately low: the
record's forward-pass estimator has been the badly-calibrated one — Phase 12 was estimated
at $0.40–1.00 and cost **$0.02** (20–50× high), while the generation estimator has been
accurate four times running (Amendment 2). Reconciled against `modal billing report` at
close. Loop spend before this phase: **$4.73** of the $90/$110 envelope; month-to-date
**$82.77** of the $200 cap.

---

*(Results append below.)*
