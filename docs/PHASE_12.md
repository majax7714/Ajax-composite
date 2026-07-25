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
