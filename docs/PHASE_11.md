# Phase 11 — is the sink scale-bounded? The Coder ladder at match, powered

*Charter opened 2026-07-25. Second iteration of the unattended loop
([AUTONOMOUS_LOOP.md]); opened under **Amendment 1** — the loop takes its recommended
option and documents the fork. Append-only; every run pre-registered with odds and
decision rules committed before it launches.*

## 0. The question, and why it is next

Phase 10 retracted the 7B sink and measured its absence at true match. That left the
**scale question OPEN**: the sink is measured at 1.5B–3B and absent at 7B, which
*resembles* the J5/Phase-6 "scale-bounded" reading — but that reading is not restored,
because Phase 7's critique of its evidence (measured only far over-quality) stands.

There is a second, sharper reason to run this now. **Phase 10 demonstrated that a
small-n positive cell in this record can fail to replicate.** M4 was n = 20, carried
into the abstract and two Index rows, "confirmed" once by a drifted cell, and it did not
survive re-running on its own inputs. The same exposure exists elsewhere:

| load-bearing positive cell | n | cond − artifact | powered? |
|---|---|---|---|
| D2c original (Coder-1.5B) | 44 | −0.121 | no (k=8 era) |
| **G1c** (Coder-1.5B, self) — Phase 9 crux | **10** | −0.155 | no |
| **G1d** (Coder-1.5B, foreign) — Phase 9 crux | **10** | −0.193 | no |
| Coder-3B (size curve point) | — | −0.076 | no |

**Phase 9's DIET conclusion — the record's most recent headline, and the one that closed
the provenance confound — rests on two n = 10 cells.** Nothing about them is known to be
wrong. But after M4 it would be negligent to build further on cells of that size without
a powered replication, and the ladder measurement and the replication are *the same
experiment*: a Coder-1.5B cell at match, powered, at n ≥ 30, is simultaneously a scale
point and a replication of G1c/D2c.

**The fork (documented, per Amendment 1).** The alternative was the **internals probe**
— the only remaining instrument for the positive mechanism, which Phase 10's P0.1
un-shelved by correcting the cost record. It is **not taken here** because attention
extraction sits outside the vLLM path and trips [AUTONOMOUS_LOOP.md] §3.6 (*new
toolchain*), which requires author sign-off the loop does not have. It remains the
standing Phase-12 candidate. Of the options runnable on the current stack, the ladder
was chosen over "a clean model below Δ_art 0 with the powered instrument" because the
latter tests a question no live claim depends on, while this one tests two.

## 1. Standing rules

Unchanged from Phase 10, plus the two instruments it produced: **all targeting uses the
powered k = 24 map**, and **adjudication is on the original below-both-nulls
definition** (the legacy `matched_sink_signature` is reported, never adjudicative).

## 2. Design

For each of **Coder-1.5B** (`df3ce67c…`) and **Coder-3B** (`09d9bc5d…`):

1. **Powered i.i.d. sweep**, k = 24, **seed 151**, over all 80 donor-pool problems.
2. **Offline targeting** (free): frozen miner rule; maximise **n** subject to
   **|predicted Δ_art| ≤ 0.010**; tie-break smaller |pred Δ_art|, then narrower band.
3. **The cell**: `_matched_cell` at **seed 173**, E0 + E1 fresh in one batch.

**Minimum n = 30. On-target |Δ_art(powered)| ≤ 0.020.** A miss is reported as a miss and
**not re-run to fit**. Δ_art reported from the powered map (primary) and the cell's own
k = 8 E0 (secondary, for continuity).

*Provenance note:* the donor pool is Qwen2.5-Coder-1.5B-base output, so the 1.5B cell is
**self-provenance**. Phase 9 refuted H-SELF (the Coder model sinks on foreign artifacts
too), so self-provenance is licensed and non-confounding — this is a direct payoff of
that phase and is stated so the reader need not re-derive it.

## 3. Pre-registered predictions

**The ladder (joint), combined with Phase 10's R5 at 7B:**

| # | branch | reading | odds |
|---|---|---|---|
| **L1** | sink at **1.5B and 3B**, absent at 7B | scale-boundedness **confirmed on matched, powered evidence** — the first time the record can say it without a positional confound. The Phase-6 "competence window" returns in corrected form: a *diet × scale* effect, not diet × position | **50%** |
| **L2** | sink at **1.5B only** | the boundary sits between 1.5B and 3B, not 3B and 7B; the Coder-3B size-curve point does not survive powering | **25%** |
| **L3** | sink at **neither** | the 1.5B sink itself fails to replicate at n ≥ 30. **Phase 9's DIET conclusion and the whole Coder-diet line would be in question** — a 1:1 refutation of the record's central LIVE claim. **HALT and report** per §3.1 | **10%** |
| **L4** | mixed / off-target / infeasible | instrument miss on one or both cells | **15%** |

**Per-cell:** Coder-1.5B reproduces below-both-nulls at n ≥ 30 — **75%** (D2c is n = 44
with p ≈ 5e-5 and two independent designs agree; far better supported than M4 ever was).
Coder-3B reproduces — **55%** (one prior point, never powered).

**Methodological:** both cells land |achieved Δ_art| ≤ 0.02 — **80%** (the powered
instrument has now hit its target twice: −0.0467 → −0.0466, +0.0023 → +0.0023).

**Cost estimate: $0.50–1.20.** Two k = 24 sweeps (2 × 80 × 24 ≈ 3,840 generations) plus
two cells (≈ 2 × 2 × 32 × 8 ≈ 1,024) on 1.5B/3B models, which bill below the 7B rate of
≈$0.17/1,000 generations measured in Phase 10. Reconciled against the bill at close per
[AUTONOMOUS_LOOP.md] Amendment 2. Loop spend before this phase: **$0.70** of the
$90/$110 envelope; month-to-date **$78.74** of the $200 cap.

---

*(Results append below.)*

---

## RESULT (2026-07-25) — **L1: the sink IS scale-bounded, on matched, powered evidence** *(`h11_coder1p5b.json`, `h11_coder3b.json`, `h11_targeting_*.json`)*

### The ladder at true match

All three rungs targeted with the **powered k = 24 instrument**, all at Δ_art ≈ 0, all
adjudicated on the **original below-both-nulls** criterion:

| rung | n | Δ_art | i.i.d. | artifact | cond | **cond − artifact** | p | **SINK** |
|---|---|---|---|---|---|---|---|---|
| **Coder-1.5B** | 44 | **+0.0016** | 0.4704 | 0.4589 | 0.4067 | **−0.0522** | **0.0130** | **YES** |
| **Coder-3B** | 39 | **−0.0005** | 0.6430 | 0.6096 | 0.5590 | **−0.0506** | **0.0081** | **YES** |
| **Coder-7B** *(P10 R5)* | 29 | +0.0023 | 0.7526 | 0.7264 | 0.7184 | −0.0080 | 0.409 | **no** |

**Branch L1 — the 50% favourite — fires.** The sink is present at 1.5B and 3B and
absent at 7B, and for the first time in this record that statement rests on cells
**matched on the relation** rather than on a fixed stimulus: every rung is at its own
Δ_art ≈ 0, so scale is no longer confounded with position. Phase 7's objection to the
J5/Phase-6 scale reading — that those cells were measured only far over-quality — does
not apply here, because these are not those cells.

### The instrument, 4 for 4

| cell | predicted Δ_art | achieved |
|---|---|---|
| R4 (7B) | −0.0467 | −0.0466 |
| R5 (7B) | +0.0023 | +0.0023 |
| **P11 1.5B** | **+0.0015** | **+0.0016** |
| **P11 3B** | **−0.0005** | **−0.0005** |

The powered targeting instrument has now placed four consecutive cells to within
0.0001 of their targets. The methodological prediction (80%, both cells within ±0.02)
**HIT** with three orders of magnitude to spare.

### The n = 10 exposure is discharged

Phase 9's DIET conclusion rested on two n = 10 cells (G1c −0.155, G1d −0.193). This
phase does **not** replicate them positionally — G1c sat at Δ_art −0.044, this cell at
+0.002 — but it establishes the thing that mattered: **the Coder-1.5B sink is real at
n = 44 under the powered instrument and the strict criterion.** It is not an
n = 10 artifact. The concern raised by M4's collapse is answered for the 1.5B rung; the
Phase-9 conclusion stands, better supported than it was.

### A quantitative note the record should carry

The at-match effects here (**−0.052**, **−0.051**) are markedly **shallower** than the
historical numbers for the same models (D2c −0.121 at Δ_art +0.026; G1c/G1d −0.155 /
−0.193 at Δ_art ≈ −0.044; Coder-3B −0.076 at −0.074). That is **coherent with R6's
refit**, which moved the trough vertex to Δ_art ≈ **−0.143**: Δ_art ≈ 0 sits on the
*shoulder* of the curve, not at its bottom. The sink is deepest below match and
shallower at match — so "the sink at match" is the conservative end of the effect, not
its peak.

The contrast with 7B sharpens accordingly: 1.5B/3B show a trough that deepens below
match, while **7B is flat across the entire measured range** (−0.003 at Δ_art −0.101,
−0.010 at −0.040, −0.004 at −0.047, −0.008 at +0.002). It is not that 7B's trough is
shallower; it is that 7B has no trough.

## PHASE GATE — CLOSED (2026-07-25)

1. **The scale question — ANSWERED.** Sink at 1.5B and 3B, absent at 7B, measured at
   match with a powered instrument. ✓
2. **The n = 10 exposure — discharged for 1.5B** (n = 44, powered, strict criterion). ✓
3. **The instrument — validated twice more** (4-for-4 to 0.0001). ✓
4. **Index current** (below). ✓

**Prediction accounting.** **L1 (50%) HIT.** L2 25% / L3 10% / L4 15% did not fire.
Per-cell: Coder-1.5B reproduces **75% HIT**; Coder-3B reproduces **55% HIT**.
Methodological (both within ±0.02) **80% HIT**. **Four for four** — a marked reversal
from Phase 10's 3-of-11, and worth noting *why*: Phase 10's questions were about
whether the record's existing beliefs survived scrutiny (they largely did not), while
Phase 11's were about a phenomenon measured with an instrument that had just been fixed.
Priors are better when the measurement is trustworthy.

**Cost.** Phase 11 **$0.68** against a $0.50–1.20 estimate — **accurate**, the third
consecutive calibrated estimate since Amendment 2. Loop total **$1.38** of the
$90/$110 envelope; month-to-date **$79.42** of the $200 cap.

**What is now open.** The **0.5B rung** (never placeable at its own straddle by mining;
needs generated artifacts). The **3B→7B boundary** — the sink is present at 3B and
absent at 7B, and nothing has been measured between. **Why** the diet does it: still the
positive-mechanism question, and the **internals probe** remains the only named
instrument, still gated on author sign-off for the toolchain (§3.6). **Nothing is
running; Phase 11 is closed.**
