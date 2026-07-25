# Phase 12 — the internals probe: what do sinking models do differently?

*Charter opened 2026-07-25 with author sign-off on the toolchain
([AUTONOMOUS_LOOP.md] §3.6). Third iteration of the unattended loop. Append-only;
pre-registration frozen before spend.*

## 0. The question

After Phase 9, the mechanism stands as: **OOD firmly disfavored** (the sink is decoupled
from surprise), **self-exemplar RECLASS excluded** (the Coder model sinks on foreign
artifacts too), and what survives is a **Coder-diet-intrinsic conditioning fragility**
with the **positive mechanism OPEN**. §0.4 named the internals probe as the only
remaining instrument for it.

**Two barriers around this probe turned out to be false**, and both were removed by the
loop rather than by new evidence:

1. §0.4 called it *"outside this record's toolchain/budget."* The **budget** half was a
   phantom — Phase 10 P0.1 showed the cost record was anchored to an inferred $31 that
   was never billed; true all-in project spend was $78.
2. The **toolchain** half is nearly as soft. `j8_ppl` (Phase 8 D3) already runs
   HF-transformers bf16 forward passes on exactly these models, on a working
   `PPL_IMAGE`. Capturing attention is an extension of a validated path, not a new
   stack. *(Recorded because it is the same error class the record keeps finding: an
   estimate written down once, then treated as a measured constraint.)*

## 1. The contrast this phase can draw, and could not before

The probe was originally specified as **self-vs-foreign attention**. Phase 9 dissolved
that framing — the Coder model sinks on both — so self-vs-foreign is no longer where the
variance is. What Phases 9 and 11 built instead is a **2×2 in which sink status is not
collinear with model size**:

| | **SINKS** (cond below artifact) | **CLEAN** (cond tracks artifact) |
|---|---|---|
| **small** | **Coder-1.5B** (−0.052, n=44) | **DeepSeek-1.3B** (+0.050, n=39) |
| **large** | **Coder-3B** (−0.051, n=39) | **Coder-7B** (−0.008, n=29) |

1.3B is clean while 1.5B sinks; 3B sinks while 7B is clean. **Any internal quantity that
tracks sink status here cannot be explained as a size effect** — and any that tracks
size is thereby excluded as the mechanism. This control did not exist before Phase 11.

## 2. What is measured

For each model, on the **same problems and the same artifacts**, teacher-force the
model over `[conditioned prompt containing the artifact] + [its own committed
conditioned generation]` and record, for every generated-token position, how attention
mass is divided between:

- the **artifact span** (the code block inside the frozen `_d2c_context` wording),
- the **problem-statement span**,
- the **already-generated** span.

Primary quantity: **mean fraction of attention mass on the artifact span**, averaged
over heads and layers, reported also as a **per-layer profile** and with its
**per-problem spread**. Frozen: `attn_implementation="eager"`, bf16, batch 1,
`max_length` 1024, greedy teacher-forcing (no sampling — this is a forward pass over
text that already exists in the committed pools).

Artifacts and generations come from the committed cells (P11 1.5B/3B, P10 R5 7B, P7 M1
DeepSeek), so **no new generation is performed** and the probe measures exactly the runs
the sink verdicts were computed from.

## 3. Pre-registered predictions

The honest state of prior belief: attention mass is a **blunt** instrument, and the
phenomenon is puzzling in a way that does not obviously reduce to "more" or "less"
attention. The sink lands **below both nulls** — worse than copying *and* worse than
ignoring — so neither pure over-attention nor pure under-attention is a natural
explanation. That is priced in below.

| # | branch | reading | odds |
|---|---|---|---|
| **A** | sinking models allocate **less** artifact attention than clean models, tracking sink status not size | consistent with Phase 8 D1's "elaborates rather than copies": weak integration → the model departs from the artifact and does so badly | **30%** |
| **B** | sinking models allocate **more** | over-fixation: the model latches onto artifact surface and corrupts it while elaborating | **25%** |
| **C** | **no difference tracking sink status** in mean artifact attention (or it tracks size instead) | the simplest attention-allocation accounts are **excluded**; the mechanism is not "how much the model looks at the artifact," pushing it to representation- or head-level structure. **A null here is a real result** and narrows the space | **35%** |
| **D** | technical failure / infeasible at this memory budget | instrument miss; recorded, no adjudication | **10%** |

**Decision rule.** A and B are each adjudicated only if the difference **tracks sink
status across both size pairs** — i.e. Coder-1.5B vs DeepSeek-1.3B *and* Coder-3B vs
Coder-7B point the same way. A difference appearing in only one pair is **C with a
flagged pointer**, not a finding: with four models this is a 2×2 with one cell per
condition, and single-pair effects are exactly what the record has been burned by.

**Secondary (exploratory, separated per §10):** the per-layer profile and the
per-problem spread are described but **not** used to adjudicate. If mean mass is null
while spread differs, that is recorded as a pointer for a successor phase, not claimed.

**What this phase cannot do.** It cannot establish a *causal* mechanism — attention is
correlational, and a difference would license "sinking models allocate attention
differently," not "attention allocation causes the sink." Causal work would need
intervention (head ablation), which is not chartered here. This is stated now so that
no result of this phase is later over-read.

**Cost estimate: $0.40–1.00.** Forward passes only, ~30 sequences × 4 models, no
generation; model load time dominates. Calibrated from Phase 10/11's measured rates and
reconciled at close per Amendment 2. Loop spend before this phase: **$1.38** of the
$90/$110 envelope; month-to-date **$79.42** of the $200 cap.

---

*(Results append below.)*

---

## RUN 1 — INVALID (recorded, not silently redone)

The first launch died **locally during cell assembly**, before any `.remote()` call:
`_p12_cells` looked up the powered-sweep caches as `j11_sweep_{rung}_cand` while
`j11_ladder` had persisted them as `j11_sweep_cand_{rung}`, so `_load` returned `None`
and the dict comprehension raised `TypeError`. **No GPU ran; $0 spent** beyond app
creation. Recorded per the Phase-9 run-1 precedent. Two changes followed: an `assert`
on the cache loads so a missing input fails with a named tag, and a **local dry-run of
the whole assembly before re-spending** — which is what verified the fix, returning
per-model artifact means of 0.4589 / 0.6096 / 0.7264 / 0.3608, matching the committed
`mean_copy_null` of the P11 1.5B, P11 3B, R5 7B and P7 M1 cells exactly.

## RESULT (2026-07-25) — **BRANCH C: artifact attention does not track sink status** *(`h12_internals_probe.json`)*

| model | status | n | **artifact frac** | sd | SE | problem frac | layers |
|---|---|---|---|---|---|---|---|
| Coder-1.5B | **SINKS** | 29 | **0.1078** | 0.0287 | 0.0053 | 0.398 | 28 |
| Coder-3B | **SINKS** | 30 | **0.1046** | 0.0256 | 0.0047 | 0.436 | 36 |
| Coder-7B | clean | 29 | **0.0981** | 0.0341 | 0.0063 | 0.452 | 28 |
| DeepSeek-1.3B | clean | 29 | **0.1131** | 0.0429 | 0.0080 | 0.316 | 24 |

**The two pairs disagree in sign and both differences are inside noise:**

| pair | sink | clean | Δ | SE of Δ | Δ in SE |
|---|---|---|---|---|---|
| small — 1.5B (sink) vs 1.3B (clean) | 0.1078 | 0.1131 | **−0.0053** | 0.0096 | **0.55** |
| large — 3B (sink) vs 7B (clean) | 0.1046 | 0.0981 | **+0.0065** | 0.0079 | **0.82** |

Under the pre-registered decision rule an effect must **track sink status across both
size pairs**. It does not: the signs oppose, and neither magnitude reaches 1 SE. All
four models allocate ≈ 10% of generation-time attention mass to the artifact,
regardless of whether conditioning on it degrades them.

**Branch C — the 35% favourite, and the one deliberately priced highest.** The simplest
attention-allocation accounts of the sink are **excluded**: it is not that sinking
models look at the artifact too little (they don't), nor too much (they don't). Whatever
the Coder diet does to conditioning, it is not visible in *how much* the model attends
to the code it was given.

### Why this is a strong null rather than a blind instrument

The probe **does** resolve systematic between-model structure — it simply isn't
sink-related. Two effects show up cleanly, and both are of the kind the design was built
to exclude:

- **Problem-statement attention tracks *size*, monotonically, within the Coder family:**
  1.5B **0.398** → 3B **0.436** → 7B **0.452**. Larger models spend more of their
  attention on the problem. Sink status is dissociated from size here by construction,
  so this cannot be the mechanism — and its presence shows the measurement is sensitive
  enough to see a real ~0.05 effect, five to ten times the sink-status deltas.
- **The per-layer profile tracks *family/architecture*:** all three Qwen models peak at
  ≈ 57% relative depth (L16/28, L21/36, L16/28) while DeepSeek peaks at ≈ 37% (L9/24).
  Coder-7B is clean yet shares the sinking models' profile, so layer shape is a family
  signature, not a sink signature.

An instrument that detects a size effect and a family effect but no sink effect, on the
same sequences, is reporting an absence rather than failing to look.

*(Both bullets are exploratory per §10 and per this phase's own secondary clause — they
are described, not adjudicated, and no claim is built on them.)*

### What is now excluded, and what is not

**Excluded:** artifact-attention *magnitude* as the mechanism of the Coder sink.

**Not excluded, and explicitly not touched:** *where within* the artifact attention
lands (the probe measures mass on the whole span, not its distribution over buggy vs
sound regions — the artifacts carry test-level pass counts but no line-level labels);
head-level structure (this averages over heads, and a small number of specialised heads
could differ while the mean does not); anything at the representation level; and
anything causal — as stated before the run, attention is correlational and this phase
was never able to license a causal claim.

**The positive mechanism remains OPEN**, but the space is smaller than it was this
morning: OOD disfavored (P9), self-exemplar excluded (P9), and now attention-allocation
magnitude excluded (P12).

## PHASE GATE — CLOSED (2026-07-25)

1. **Probe built and run** on the 2×2 where sink status is not collinear with size. ✓
2. **Branch recorded with its decision rule applied as frozen** — pairs disagreed, so C,
   not a single-pair claim. ✓
3. **Run 1's invalidity recorded**, cause named, guard added. ✓
4. **Causal over-reading pre-empted** in the charter and honoured in the result. ✓

**Prediction accounting.** **C (35%) HIT** — the branch priced highest, and priced that
way for the stated reason: a sink that lands below *both* nulls is not naturally
explained by more or less attention. A 30% and a 25% branch did not fire; D (10%) did
not fire.

**Cost.** Phase 12 **≈ $0.02** (month-to-date $79.42 → $79.44; aggregate delta, per-app
lines lag and this may rise). Estimate was **$0.40–1.00** — over by ~20–50×. Amendment 2
fixed the estimator for *generation* workloads (R4/R5/P11 all accurate) but it is still
badly calibrated for **forward-pass-only** workloads, where model load dominates and
total GPU time is minutes. Recorded as a second calibration lesson rather than a
repeat of the first.

**Loop total $1.40** of the $90/$110 envelope; month-to-date $79.44 of $200.

**What is open.** The within-artifact *distribution* of attention (needs line-level
bug labels, which the current artifacts lack); **head-level** analysis; and the causal
step (**head ablation**), which would be the first intervention this record has ever
run and needs its own charter. **Nothing is running; Phase 12 is closed.**
