# Phase M — stack migration (Kaggle/HF/4-bit → Modal/vLLM/fp16)

*Written 2026-07-12. **This work does not start yet.** Read §0 before anything
else. Nothing in this document may be executed until the current experimental
record is closed on the existing Kaggle stack. This is a pre-registered plan and
a hard gate, not a task in progress.*

---

## 0. HARD PRECONDITION — do not begin until all of these are committed

- [ ] **B2 complete**, `artifacts/h2_b2_result.json` written, Branch A/B verdict
      appended to [PRE-B2-HANDOFF.md] §3.
- [ ] **DIAG-2** (register probes), **DIAG-3** (control authority), **DIAG-5**
      (does the teacher-forced gain transfer to HumanEval?), **DIAG-4 item 3**
      (entropy split) complete and written to [DIAGNOSTICS.md].
- [ ] **DIAG-6** (large-k pass@k on the 26 oracle-empty problems — the headroom
      ceiling) complete, *if it is going to be run on the old stack at all*.

**Why this is a hard gate.** Every fix in this document changes sampling
numerics. Switching precision, or swapping HF `generate()` for vLLM, will
**permanently destroy the bit-for-bit Phase-0 lock** (lock_a/lock_b, 164/164
byte-identical candidates, 204,553 tokens). That lock is one of the best assets
this project has. Any comparison that straddles the migration is confounded by
the stack change and is worthless.

**Migrate at a clean phase boundary. Never mid-comparison.**

---

## 1. The inefficiency, quantified

Phase-0 generated 204,553 tokens. Across Phases 0–2 the total is roughly ~800k
generated tokens, inside ~25 T4-hours. Subtract the QLoRA verifier fine-tune and
register training (call it 3–5 hours, legitimately spent) and the effective
generation rate is **~10 tokens/second**.

For reference: a 1.5B model on a T4 should reach 30–50 tok/s at batch 1 with
plain HF `generate()`, and 1,000–3,000+ tok/s aggregate under vLLM with
continuous batching. We are an order of magnitude below even the naive number.
Three causes, in descending order of cost.

### 1.1 Sandbox execution is almost certainly blocking inside the GPU kernel

12,100 Daytona runs across Phases 0–2. At ~2–4 s per cloud round trip (container
spin-up → run → teardown), serial, that is **7–13 hours of a T4 sitting idle**
waiting on a CPU container — plausibly half the entire quota spend.

The fix follows from one realization: **the refinement loop never needs the
sandbox.**

```
r ← r₀(problem)
for t: candidate ← G(problem, r);  v ← V(problem, candidate);  r ← U(r, φ(candidate), v)
```

`V` is the neural verifier, **not** the execution sandbox. Execution is only used
for (a) generating V's training labels, (b) final pass@1 scoring, (c) oracle
coverage — **none inside the loop**. So the pipeline decouples into three stages
that were never actually coupled:

| Stage | Where | What |
|---|---|---|
| 1. generate | GPU (Modal, vLLM) | run the full loop; dump every candidate + verifier score |
| 2. execute | CPU (local or Daytona, parallel) | label every candidate |
| 3. score / train | GPU (Modal) | metrics, V training, register training |

Stage 2 on the Fedora workstation (8600G, 12 threads) chews through 12,100 short
Python functions with timeouts in well under an hour, for $0. The existing driver
(`tests/test_driver.py`, 8/8 canonical validation) already returns the right
shape — it just needs to run **outside** the GPU session.

### 1.2 4-bit on a 1.5B model is a straight loss

1.5B params × fp16 ≈ 3.1 GB; a T4 has 16 GB. We were never memory-constrained.
bitsandbytes NF4 dequantizes on every forward pass — it buys memory we don't need
and costs throughput we do (typically 2–4× slower than fp16 at low batch). D6
("4-bit NF4, frozen") was inherited from the 4B QLoRA work, where it was correct.
Here it is not.

*Note:* T4 is Turing (sm75) — fp16 yes, bf16 no. On L4/A10 (Ada/Ampere), use bf16.

### 1.3 No continuous batching, and the batching axis was wrong

The loop is sequential *per problem* but embarrassingly parallel *across
problems*; the current implementation walks problems serially.

- **B1** (i.i.d. samples): all 164 × 8 = 1,312 generations in a single batch.
- **FULL / B2** (sequential refinement): 8 rounds of a **164-way batch** —
  generate step-t for all problems at once, score all 164 with V at once, update
  all 164 registers, advance to t+1.

That is the whole rewrite: **vectorize across problems, not across steps.**

---

## 2. The unlock: vLLM supports soft-prompt injection

This was the binding constraint, and it resolves cleanly. vLLM accepts a
`prompt_embeds` tensor of shape `(sequence_length, hidden_size)` directly,
bypassing the token-id → embedding lookup, while retaining PagedAttention and
continuous batching. Enabled by `--enable-prompt-embeds` (server) or
`enable_prompt_embeds=True` (offline `LLM` API).

**The register architecture survives the migration unchanged.** Build the
sequence yourself: `[soft_prompt_embeds(8, 1536)] ++ [embed(templated_prompt)]`.

Two traps — flag both:

1. **Chat template.** G is Qwen2.5-Coder-1.5B-Instruct and assumes a chat
   template. vLLM does **not** apply a chat template to `prompt_embeds` — the
   caller embeds the *already-templated* prompt. Get this wrong and generation
   quality silently collapses. Apply `tokenizer.apply_chat_template(...)` first,
   embed the result, then splice the soft prompt in at the correct position.
2. **Engine version.** `prompt_embeds` landed in the v0 engine first and was
   ported to v1 separately. **Verify on the pinned vLLM version** before building
   on it. If v1 support is absent, pin v0 or fall back to HF for the register path
   only.

For teacher-forced NLL (DIAG-4 / DIAG-5-style work), `prompt_logprobs` covers it.

---

## 3. The honest cost ledger of migrating

Not free. Budget it explicitly.

**We permanently lose bit-identity with the old stack.** Phase-0/H1/H2 numbers
become historical results from a retired stack. They may be cited as such; they
may **never** be compared against anything produced on the new stack. Everything
gets re-locked.

**fp16 will make G better, with consequences:**

- B0/B1 baselines will rise.
- pass@8 oracle will rise, which **shrinks refinement headroom further** — it
  *strengthens* the §1.1 "no generative headroom" argument in the post-mortem and
  makes a Branch-A task redesign more urgent, not less.
- V-v2b was trained on 4-bit-generated candidates. Switching G to fp16 changes
  the candidate distribution *underneath* the verifier. This is not ordinary
  actor drift — it is a **substrate change**. V must be revalidated and probably
  retrained (gate M4). Budget the label regeneration.

**Recommendation: switch to fp16 anyway.** 4-bit was never justified at 1.5B, it
actively degrades the generator the whole experiment depends on, and if B2 lands
in Branch A we re-lock baselines on a new benchmark regardless — which makes the
migration nearly free. But make the call **explicitly** and record it as a
decision (D11); do not let it happen by accident.

---

## 4. Modal — the target platform

Chosen over GCP (zero default GPU quota, slow/uncertain approval, pay for the
whole VM while the GPU idles, no A10G) and over staying on Kaggle (weekly quota
wall, 12-hour session cap, ephemeral sessions re-downloading a 3 GB model every
time). We have prior Modal experience from dark-phoenix.

**Rates (verified 2026-07):** T4 ~$0.59/hr, L4 ~$0.80/hr ($0.000222/sec), A10
~$1.10/hr. Per-second billing, scale-to-zero, $30/month free credits.

**Cost projection:** the fixed stack should run this project end-to-end in
~2–5 L4-hours → **$1.60–$4.00**, entirely inside the free monthly credit. The
practical outcome: the quota wall disappears at $0/month.

Setup notes:

- `@app.function(gpu="L4")` — Python decorators, no YAML, no Dockerfile.
- **Persistent Volume** for HF cache + model weights. Kills the per-session 3 GB
  re-download Kaggle forces.
- Use **preemptible** (the default). Non-preemptible carries a 3× multiplier and
  buys nothing for batch research jobs.
- **Do NOT move execution into Modal Sandboxes** — they bill CPU at ~3× the
  standard Function rate. Keep Daytona, or better, run stage 2 locally on the
  Fedora box for free.
- No 12-hour session cap; cold starts are irrelevant for batch jobs.
- Worth an email: Modal has a startup/academic credit program (grants reported up
  to $10k). Selenex may qualify.

*Standing (not this task):* UNC Charlotte's cluster is the better long-term answer
— free, larger, no quota anxiety — but needs a faculty sponsor and on-campus
presence. Modal is the bridge until then. When the sponsor lands, revisit; ACCESS
Explore (1–2 business-day approval) and NAIRR become available at the same moment.

---

## 5. Phase M — gates

Sequential. Each gate must pass before the next begins. No gate may be tuned past.
(Same discipline as Phases 0–2; it is the reason this project is trustworthy.)

- [ ] **M0 — Precondition.** §0 checklist fully green. Tag the repo pre-migration
      so the old stack is recoverable exactly. Record **D11** (§7) before any code.
- [ ] **M1 — Correctness gate: does vLLM reproduce HF's soft-prompt semantics?**
      Fix a register `r`. Generate greedily (temp = 0) for ~20 problems under
      (a) HF + soft prompt, (b) vLLM + `prompt_embeds`. Compare token-for-token.
      *Gate:* near-identical greedy outputs (minor numerical divergence in the tail
      is fine; systematic divergence at token 1–3 means the chat template is wrong
      — §2 trap 1). If this fails, **stop** — the register path does not migrate
      and nothing downstream is valid.
- [ ] **M2 — Throughput gate.** Measure tok/s on the old and new stacks, same
      workload; report the multiple. *Gate:* ≥ 20×. If under ~5×, something is
      still wrong — find it before proceeding, don't accept a partial win.
- [ ] **M3 — Statistical equivalence, not bit equivalence.** Re-run the Phase-0
      baseline (B0, B1) on the new stack. Bit-identity is not expected (different
      precision, different sampling impl). *Gate:* new pass@1 within a defensible
      distance of the old, and any shift **explained** (fp16 improving G is an
      expected upward shift, not a bug — but state it, size it, record it).
- [ ] **M4 — Verifier revalidation.** Score fp16-generated candidates with V-v2b;
      compute AUROC and within-problem macro AUROC on the new candidate
      distribution. *Gate:* if AUROC degrades materially vs the recorded
      0.7951 / 0.7189 on 4-bit candidates, regenerate labels and retrain V on the
      new stack. H1 is the one result that carried load; it must survive the
      migration or be re-established.
- [ ] **M5 — Re-lock.** New bit-for-bit reproducibility lock on the new stack: two
      independent runs, same seed policy, byte-identical candidates — the new
      lock_a/lock_b. Freeze new baselines. Update [COMPUTE_ACCOUNTING.md]: the
      budgeted unit ("one candidate generation") is unchanged, but note the stack
      change in the amendment log (empty until now).

---

## 6. What NOT to do

- **Do not migrate before §0 is green.** The temptation will be strongest exactly
  when B2 is slow. Resist it.
- **Do not fix throughput and change the experiment in the same commit.** One
  variable at a time. The migration is a no-science-change refactor; the task
  redesign (Branch A) is a separate, later step with its own baselines.
- **Do not compare any post-migration number to any pre-migration number. Ever.**
  Re-lock first.
- **Do not move Daytona into Modal Sandboxes** (3× CPU premium). Local CPU is free
  and faster.
- **Do not "optimize" by reducing N, T_max, or the sample budget.** The compute
  accounting rule is frozen; the whole point is that the *same* budget now costs
  minutes instead of hours.

---

## 7. Open decision (record as D11 before starting)

**Precision:** fp16 (recommended — §3) vs staying 4-bit to preserve the verifier's
training distribution. Choosing fp16 means accepting the M4 verifier retrain;
choosing 4-bit means keeping a known-degraded generator and forfeiting most of the
throughput win. Make the call explicitly, write it into [DECISIONS.md] (D11) with
the reasoning, and don't revisit it silently. Reserved as **D11 (open)** now; it
is settled at **M0**, not before.

**Deliverables (produced as Phase M runs, not now):**

- this `PHASE_M.md` gate log (M0–M5, dates, pass/fail),
- **D11** in [DECISIONS.md] (settled at M0),
- new lock_a/lock_b artifacts,
- a one-line throughput result (old tok/s → new tok/s) in [PHASES.md],
- an amendment entry in [COMPUTE_ACCOUNTING.md] (the first one).
