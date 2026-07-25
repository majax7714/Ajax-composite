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
