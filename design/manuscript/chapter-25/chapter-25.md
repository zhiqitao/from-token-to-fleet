# Chapter 25 — The Architecture Decision Record

## The Architect's Question

As the "From Token to Fleet" handbook reaches its final chapters, we turn from technical mechanisms to the governance of those mechanisms. With ~2,000 users, a RAG Q&A system, and a 70B dense FP16 deployment, the question becomes: how does the team capture, justify, and evolve the architectural choices that keep the fleet running? The Architecture Decision Record (ADR) is the answer — a lightweight, text-first practice that records not just what was decided, but why, what alternatives were considered, and what trade-offs were accepted. This chapter explores the ADR pattern in the context of a production AI system, providing a reusable template and a worked example centered on model-shape choices.

## 1. Concept

An Architecture Decision Record is a single Markdown file that captures a significant architectural decision and its context. The format was popularized by Michael Nygard and has been adopted by teams ranging from startups to enterprises managing complex AI/ML stacks. Each ADR follows a minimal structure:

- **Title** and status (proposed, accepted, superseded, deprecated)
- **Context** — the problem, constraints, and goals that prompted the decision
- **Decision** — the chosen approach, concise and explicit
- **Consequences** — outcomes, both positive and negative, that flow from the decision
- **Alternatives considered** — other paths rejected, with brief rationale for rejection

These five are the *core* fields. The worked ADR in §25.3 and the copy-ready template in §25.3.1 both keep them and then add record-specific apparatus — the worked record adds a Rationale and Evidence Tags; the template adds Evidence, decision owner, validation, rollback, review trigger, and falsification path — without changing the core.

The key distinction between an ADR and a standard design document is intent: an ADR is meant to be living, reviewed in pull requests, and occasionally superseded. It answers the "why" at the moment the decision was made, preserving it for future engineers who must reason about the system years later.

In a RAG/Q&A fleet with 70B models, ADRs prevent the "why did we choose this tokenizer?" or "why FP16 over BF16?" questions from becoming tribal knowledge. They also integrate naturally with git — each ADR lives in version control, linked to the commit or PR that implemented the decision.

## 2. Mental Model

The mental model underpinning ADRs is simple: architectural decisions are irreversible (or costly to reverse) choices that deserve permanent documentation. Unlike code comments, which explain what a function does, ADRs explain why the system is structured as it is. This mental model has three layers:

1. **Problem awareness** — What forces are at play? (load patterns, latency requirements, budget constraints, team expertise)
2. **Choice architecture** — What design options exist? What are their properties?
3. **Outcome acceptance** — What will we live with? What will we monitor?

For AI/ML systems, this model extends to decisions about model quantization, retrieval chunk sizes, embedding dimensions, and infrastructure trade-offs. Each decision carries FACT/DERIVED/HYPOTHESIS evidence tags, making the ADR itself a source of verifiable claims rather than opinion.

The ADR format also enforces a habit: before committing to a decision, the team must explicitly articulate alternatives. This alone often reveals overlooked options or clarifies why the chosen path is genuinely optimal.

## 3. Worked Example: Model-Shape ADR

**Title:** ADR 0016 — Model Precision: FP16 vs BF16 for 70B Inference

**Status:** Accepted

**Context:**
The fleet runs a 70-billion-parameter dense model for RAG Q&A serving on an 8×H100 host (640 GB). The team is choosing the deployment weight precision: FP16 (float16) or BF16 (bfloat16). A common assumption — that migrating to BF16 halves the model's memory and buys headroom — is wrong, and this record exists partly to correct it. FP16 and BF16 are both 16-bit formats, 2 bytes per parameter, so a 70B model occupies ~140 GB in either. This ADR is therefore not a memory decision; it is a numerical-range and operational-consistency decision.

**Decision:**
Render the serving model in BF16.

**Rationale:**

- FP16 and BF16 both store 2 bytes/parameter, so weight residency is identical (~140 GB for 70B). Stating this up front prevents anyone from later treating the choice as a memory lever.
- The real difference is range vs precision. BF16 keeps the same 8-bit exponent as FP32, so it does not overflow or underflow in activations the way FP16's 5-bit exponent can. FP16 carries more mantissa bits (10 vs 7) and is more precise when values already sit in range.
- For this workload both precisions clear the quality bar on the held-out Q&A set, with no exact-match change between them, so the deciding factors are range robustness and consistency — not capacity. In this illustrative evaluation the exact-match result showed no difference [ILLUSTRATIVE][ASSUMPTION] — to be confirmed by the deployment quality gate: we did not run this comparison on real hardware in this handbook; it is an assumed outcome for the worked ADR.
- A100 (and the 8×H100 host) natively supports BF16 and TF32 on its Tensor Cores. There is no "next GPU generation" required and no explicit-casting penalty; the premise that these formats wait for future hardware is itself the kind of error an ADR should catch.
- Operational consistency: the training run that produced the weights used BF16 mixed precision. Keeping inference in BF16 avoids a training-to-serving cast and keeps behavior predictable.

**Consequences:**

- **Positive:** range robustness in attention/softmax and long-context accumulation; no change in weight residency (both precisions are ~140 GB).
- **Negative:** lower mantissa precision than FP16 in the weights (BF16 has 7 mantissa bits vs FP16's 10), so FP16 is more precise where values already sit in range; in the illustrative evaluation on this workload the exact-match result showed no quality difference [ILLUSTRATIVE][ASSUMPTION] (to be confirmed by the deployment quality gate), so the trade-off is precision headroom, not observed quality. There is no free memory — and none should be expected.
- **Monitoring:** track per-request latency, GPU memory utilization, and held-out Q&A quality. If the BF16 output drifts, fall back to FP16 and compare both on the same set (they differ in precision, not footprint).

**Alternatives Considered:**

1. **FP16:** Rejected here — no memory advantage over BF16, and a narrower exponent range. Retained as the fallback if BF16 shows precision drift.
2. **FP8 weights:** The genuine memory lever (halves residency to ~70 GB) but needs per-tensor calibration and a validation gate; deferred as the next step, paired with the FP8 KV discussion in Chapter 7.
3. **FP32:** Rejected — 280 GB residency with no quality benefit for this workload.

**Evidence Tags:** [1P][FACT] — FP16 and BF16 are both 16-bit (2 bytes/parameter). [ILLUSTRATIVE][DERIVED] — a 70B model is ~140 GB in either (70 × 10⁹ × 2 B), the same footprint Table 22-1 and §25.4 derive. [1P][FACT] — H100 Tensor Cores support BF16 and TF32 natively. [canonical scenario][DERIVED] — weight residency is unchanged by the FP16↔BF16 choice. [ILLUSTRATIVE][ASSUMPTION] — no exact-match difference between FP16 and BF16 on the held-out Q&A set — an assumed outcome for this worked ADR, to be confirmed by the deployment quality gate (not a measurement in this handbook).

### 3.1 A copy-ready blank template

This is the template to copy into a repo, intended to be filled and to serve as a reusable professional artifact. Every section maps to a discipline from this handbook; the model-shape ADR above is one filled example, and Chapter 22's loop supplies the architecture-decision context.

```
# ADR-NNNN — <Short Decision Title>

## Status
<proposed | accepted | superseded | deprecated>  (date)

## Decision (the committed choice, one paragraph,
   reversible in principle)
<the one-sentence decision, and what it commits the team to>

## Architecture Decision Context  (from Chapter 22's loop)
- Business objective:  <what outcome this enables>
- Workload:            <characterization:
                         tokens, rps, peak>
- Requirements+SLOs:   <quality / latency / availability,
                         measurable>
- Constraints:         <privacy, region, ops,
                         procurement, budget>

## Alternatives considered
1. <option> — <why rejected>
2. <option> — <why rejected>

## Evidence
- <claim> — FACT/DERIVED/HYPOTHESIS
  [1P]/[2°]/(to be verified)
- Unit check:  <does each derived quantity's
  unit make sense?>
- Sanity check: <is each result physically
  possible? (e.g. MFU ≤ 1)>

## Trade-offs & consequences
- Pro:   <expected positive effects>
- Con:   <expected negative effects>
- Risk:  <residual uncertainty>

## Decision owner
<person / team>

## Validation plan
<how this decision will be
  benchmarked/verified post-deploy>

## Rollback plan
<how we unwind if the decision fails its SLO>

## Review trigger
<what event (metric, date, new evidence)
  re-opens this ADR>

## Falsification path
- Hypothesis:      <the claim this decision rests on,
  stated so it can be wrong>
- Evidence required: <the measurement/benchmark that
  would confirm it>
- Invalidation:     <the specific counterexample or
  measured result that would prove the decision wrong
  and force a re-open>
- Alternative:      <what we switch to if invalidated>
```

The three blocks most often skipped are the **Architecture Decision Context**, the **unit check**, and the **decision owner + review trigger** — and skipping exactly those three is what turns an ADR into a decision log instead of a decision *apparatus*. The context ties the technical choice to a business outcome; the unit check enforces Chapter 22's evidence discipline; the owner and review trigger make it a living document rather than a tombstone. The **falsification path** is what makes the decision *reproducible* rather than merely plausible: it names the hypothesis, the evidence that would confirm it, and the specific measured result that would invalidate it — so the next engineer can re-run the decision instead of inheriting it on faith.

## 4. Measurement

ADRs are only as good as the evidence they embed. This chapter recommends that each ADR include at least two derived quantities — quantities computed from raw data, not merely observed. In the model-shape ADR above, the derived quantities are:

1. **70B FP16 model footprint** — $W = N \times \text{bytes-per-param} = 70 \times 10^9 \times 2 \text{ B} = 140$ GB parameters, plus ~30 GB activations at the peak for this worked example (K+V alone: 2 × 80 layers × 9.2K × 8,192 × 2 B ≈ 24 GB, plus hidden/MLP working tensors ≈ 30 GB total) [DERIVED], giving ≈ $170$ GB total derived footprint. This ~30 GB is a *per-request working-set* figure for this ADR's single-request arithmetic; it is **not a re-labeling of** the ~64 GB runtime/workspace/NCCL reserve the body uses elsewhere (140 GB weights + ~436 GB KV budget + ~64 GB reserve = the 640 GB HBM envelope). The two answer different questions — one sizes a single request's activations, the other reserves headroom for the serving stack's runtime — and at serving time the activation working set is drawn from *within* that 64 GB workspace line (workspace includes activation buffers) — the ~30 GB is a transient single-request prefill peak, reused across the batch rather than held per request in flight (17 concurrent × 30 GB is not implied) — so the envelope closes as 140 + 436 + 64 = 640, not 670. Derived from the model parameter count and a typical activation overhead factor.
2. **Weight-quantization residency lever** — quantizing the FP16/BF16 weights to INT8 reduces the nominal parameter-weight footprint from ~140 GB to ~70 GB for a 70B model (2 B/param → 1 B/param), before runtime overheads. Whether the resulting quantized model satisfies the quality SLO must be established by benchmark, not assumed. (An FP16↔BF16 change alone is *not* a memory lever: both are 16-bit, 2 B/param, ~140 GB.)

Additional measurable quantities that should be tracked (even if not all included in the ADR itself) include:

- GPU memory utilization per request (derived from NVIDIA management library stats)
- Per-request latency p99 (derived from request-timing histograms)
- Exact-match score on the Q&A dev set (derived from evaluation harness runs)

Each derived quantity should be tagged with its evidence source [1P]/[2°]/(to be verified), linking to a profiling script, a benchmark run, or a verified observation. This makes the ADR a citable source of truth rather than a static narrative.

## 5. Common Mistakes

When adopting ADRs, teams frequently fall into patterns that undermine the format's purpose. Here are the most common, with fixes:

**Table 25-1** — Common ADR adoption mistakes and their fixes.

| Mistake | Fix |
|---|---|
| **Writing ADRs after the fact** — retroactive documentation loses the context of the decision trade-offs. | ADRs are written as part of the decision process, ideally in the same PR that implements the change. |
| **Too much detail** — documenting every incremental choice clutters the record and discourages reading. | Limit ADRs to decisions that affect system behavior, architecture, or cost. Routine choices (library upgrades without API change) need no ADR. |
| **No status tracking** — an ADR that is never updated becomes stale and erodes trust. | Use status fields (proposed → accepted → superseded) and treat the ADR as a living document reviewed in PRs. |
| **Missing alternatives** — without explicit alternatives, the ADR reads like a proclamation, not a decision log. | Always include an "Alternatives considered" section, even if the list is short. |
| **No evidence links** — claims without references become folklore. | Every derived quantity and key claim should reference a data source, script, or benchmark run. |
| **Treating ADRs as permanent** — some decisions do change. | If a decision is superseded, update the ADR status and add a superseding ADR link. Do not delete history. |

## 6. Architecture Consequence

Introducing ADRs into the "From Token to Fleet" handbook has several architecture-level consequences:

- **Decision provenance:** Every significant choice in the fleet's evolution is traceable to a git commit and a Markdown file. New engineers can audit why the system is as it is, without relying on Slack history or outdated wikis.
- **Reasoned quality optimization:** the discipline of improving an architecture decision's quality by forcing the articulation of alternatives and evidence, so the trade-off surface is explicit rather than tacit. ADRs are where that reasoning is recorded: teams can point to an ADR and say "we chose BF16 over FP16 because of range robustness and training-to-serving consistency" (as ADR 0016 does) — and those reasons are verifiable.
- **Reduced cognitive load:** Engineers no longer need to re-derive the rationale for every architectural choice. The ADR serves as a single source of truth.
- **ADR proliferation:** As the fleet grows, the number of ADRs will grow. A naming convention (ADR 0001, ADR 0002, ...) and a top-level index (ADR index) prevent the record from becoming unwieldy.
- **Integration with CI:** ADRs can be validated as part of the CI pipeline — e.g., ensuring every ADR has a status, a rationale, and at least one evidence tag. This automation reinforces the habit.

On the negative side, ADRs add a small writing overhead. For a team of ~10 engineers making ~1–2 significant architectural decisions per month, this is a manageable cost. The payoff — reduced on-call noise, faster onboarding, and fewer "why did we do it this way?" debates — more than compensates.

![Fig 25.1 — The Anatomy of an Architecture Decision Record, and how one ADR supersedes the next. **Takeaway:** an ADR is a fixed five-field record — Title and status, Context (the situation), Decision (the choice), Consequences (the effects), Alternatives considered (the rejected options) — and it is *kept, not edited*: the Consequences of ADR-001 become the Context of ADR-002, which supersedes it while the original stays on file. **Scope:** the generic anatomy and supersession rule that the chapter's worked model-shape ADR (§25.3) and the copy-ready template (§25.3.1) put into practice as their five core fields (§25.1), each extended with its own apparatus. **Warning:** illustrative structure, not a measured decision record — a real ADR must carry the evidence tags its numbers are judged by. [ILLUSTRATIVE] conceptual](figures/fig-25-2501.png)

> **DECISION STATE — CANDIDATE SCREENED; NOT COMMITTABLE — regional availability, failover, SLO-goodput and matched-scope costs pending.**
>
> An ADR may record this state. The canonical candidate has cleared the capability and *single-region* cost screens (Ch 16 §16.6, Ch 17 §17.6), but the canonical workload's 99.9% multi-region active-active requirement is unsized and unpriced, only N−1 single-host failover is modeled, SLO-goodput is unmeasured at the target offered load (Ch 14), and the delivery modes are not compared on matched scopes. Writing **HOLD** into the Status field is the correct, auditable record — and it is not the same as choosing the cheapest row.

**A worked HOLD record — ADR 0015, in this chapter's template** (the compact form appears at the Decision rung in Ch 22 §6; the record is kept, not edited).

#### ADR 0015 — Delivery mode and region topology for the canonical Q&A workload {.unnumbered}

**Status:** **HOLD** — screened, not committed.

**Context:**
The loop has produced capability, capacity and *single-region* cost screens: the 70B 8×H100 self-host clears the capability screen, and the single-region arithmetic gives ~$155.8K/mo (~$24.97/1K) self-host, ~$87.6K/mo (~$14.04/1K) on the cloud default paid-occupancy input, and ~$129.8K/mo (~$20.8/1K) managed API at the canonical 6.24M requests/mo. The canonical workload's own 99.9% multi-region active-active requirement sits in none of those numbers (Ch 16 §16.3, Table 16-2).

**Decision:**
No delivery mode is committed. The least-cost option — the cloud default paid-occupancy input at ~$14.04/1K — is explicitly **not** selected, and neither is self-host nor the managed API. **HOLD is the decision**, with the four exit criteria below as its review trigger.

**Consequences:**

- **Positive:** no input assumption is promoted to a commitment; the four pending items are named, owned and testable, and the single-region baseline (21-host KV-screen headline / 32-host N−1 policy — case (i) canonical; the case (ii) prefill screen gives 22/34, ADR 0015 R1) keeps operating as a *provisional* assumption.
- **Negative:** no procurement path this quarter, and the availability requirement stays unmet on paper until regional capacity is priced; planning must carry the single-region totals as single-region totals, not as the SLA's cost.
- **Monitoring:** regional capacity quote, region-failure test result, measured p95 SLO-goodput at the target offered load, and a matched-scope re-run of the three modes.

**Requirement coverage matrix (every stated requirement of the canonical workload → the status this ADR records):**

| # | Requirement (Ch 4 / Table 4-2; SLA) | Screen applied | Status |
|---|---|---|---|
| R1 | Serve the canonical workload: 10 rps avg / 40 rps peak, 9.2K-in / 300-out | KV-residency screen (Ch 17 Table 17-1): 21 hosts (KV, case-independent); prefill screen 19 case (i) / 22 case (ii); 70% × 95% + N−1 policy: 32 (KV screen) / 34 (case (ii) prefill screen, Ch 20) | **SCREENED** — analytical lower-bound screen, not measured SLO-goodput |
| R2 | TTFT ≤ 2 s (p95), ~25 ms/token decode | Ch 14 load test at the target offered load | **NOT VALIDATED** — unmeasured |
| R3 | 50-question retrieval-QA quality benchmark on customer data | Ch 14 evaluation run | **NOT VALIDATED** — unmeasured |
| R4 | Failover under one host loss (N−1) | 32-host policy row (31 working + 1 reserve), single region | **SCREENED** — single-host only; no region-failure test |
| R5 | **Multi-region active-active, 99.9% availability** | none — no regional capacity, replication, routing or failure test is in any number in this record | **multi-region active-active: NOT VALIDATED / NOT PRICED** |
| R6 | Cost compared across the three delivery modes | Ch 16 Tables 16-1 / 16-2 | **NOT COMPARABLE** — scopes unmatched; the multi-region row is NOT PRICED |

**R5 is the requirement the HOLD exists for: multi-region active-active is NOT VALIDATED / NOT PRICED.** Every $/1K and every host count above is single-region; the canonical workload's own stated 99.9% requirement is carried as an unpriced, untested row until exit criteria (i) and (ii) close it. [ILLUSTRATIVE][ASSUMPTION]

**Alternatives considered:**

1. **Select the least-cost mode now** — rejected: the $87.6K line is a paid-occupancy INPUT, not a measured duty cycle, and no row carries the 99.9% active-active cost; choosing it would encode an assumption as a decision.
2. **Commit to self-host** — rejected: its SLO-goodput pass is provisional until benchmarked (Ch 14), and it is single-region only.
3. **HOLD with explicit exit criteria** — adopted.

**Evidence:** [ILLUSTRATIVE][ASSUMPTION] — the three single-region cost rows are Ch 16 scenario inputs, not quotes. [DERIVED] — 6.24M req/mo and every $/1K division are Ch 16 arithmetic. [ASSUMPTION] — the 99.9% active-active requirement is the canonical workload's stated SLA (Ch 4), unpriced here.

**Trade-offs & consequences:** the team trades a decision's timeliness for its defensibility: HOLD costs optionality in the near term and prevents a cost ranking from silently becoming an availability commitment.

**Decision owner:** the serving-platform architect who ran the Ch 22 loop, with the SRE owner accountable for the region-failure test.

**Validation plan:** (i) regional capacity sized and priced for the 99.9% active-active SLA; (ii) a region-failure test defined — per-region **weight/index availability is mandatory**, **live-KV replication across regions is an optional policy** (clients may replay or recompute context in the surviving region within the recovery objectives, Ch 16 §16.3); (iii) measured p95 TTFT/TPOT SLO-goodput at the target offered load; (iv) a matched-scope re-run of the three delivery modes.

**Rollback plan:** none required while HOLD stands — no mode has been commissioned; any interim spend stays month-to-month and reversible, and the single-region baseline remains the operating assumption.

**Review trigger:** any validation item (i)–(iv) landing, or a change to the canonical workload's SLA or price period.

**Falsification path:** if all four exit criteria are met and the matched-scope re-run still shows a stable least-cost ordering, a successor record (ADR 0018 or later) lifts the HOLD and supersedes this one; ADR 0015 stays on file unchanged. If the criteria cannot be met, the HOLD itself is the finding — the requirement and the cost model do not describe the same system.

## 7. What We Still Don't Know

Despite the structured format, several questions remain open and would benefit from future ADRs or empirical studies. Each item below is a **hypothesis awaiting verification** — none has FACT instrumentation yet:

- **ADR fatigue:** Does the presence of many ADRs overwhelm the team, leading to superficial writing or skipped documentation? 
- **Evidence decay:** How long do derived quantities remain valid? Should ADRs include a "last reviewed" date and a trigger for re-evaluation?
- **Cross-ADR dependencies:** When multiple ADRs interact (e.g., a quantization choice interacts with a retrieval chunk-size choice), how should the team document the dependency graph?
- **Tooling gaps:** No widely adopted tool exists for ADR graph visualization or impact analysis. Building such a tool would require understanding the ADR network and its evolution over time.
- **ADR format evolution:** The minimal format (title and status, context, decision, consequences, alternatives) works for most cases, but edge cases — decisions involving regulatory compliance, security, or data governance — may require additional sections.

These open questions are not blockers; they are signals for when the practice matures and the team needs more sophisticated governance.

## 8. End-of-Chapter Mini-Case: An ADR for the KV-Bound Fleet

**Scenario:** The fleet serves the canonical RAG Q&A workload on an 8×H100 host. At peak the KV cache is the binding constraint: within the canonical ~436 GB practical KV budget, a full-precision FP16 KV at ~2.62 MB/token (the canonical full-MHA reference-geometry figure; ~2.5 MiB) lets a single host hold ~17.5 concurrent 9,500-token requests (byte-accurate 17.51; conservative integer floor 17). The concurrency ceiling is now limiting throughput below the target request rate.

**The ADR (draft):**

- **Title:** ADR 0017 — KV Cache Precision: FP16 vs FP8
- **Status:** Proposed
- **Context:** The canonical 70B RAG workload is bandwidth-bound at decode (Ch. 8's "memory-bound" = low arithmetic intensity, ~1 FLOP/byte), and its *concurrency* is capacity-constrained by KV residency (a distinct constraint from the decode bandwidth bound — Ch. 15). At the ~436 GB practical KV budget, full FP16 KV caps concurrency at ~17.5 requests/host, and Ch. 17 shows that ~40 rps at the canonical ~8.6 s service time implies ~344 in-flight requests — far more than one host can hold (a single host holds ~17.5 concurrent). To reach the target request rate we need either more host capacity or more KV residency per host.
- **Decision:** Render the KV cache in FP8 for the long-context decode path, keeping prefill and the retrieval/prompt phase in FP16. FP8 KV cuts KV residency to ~50% of the FP16 figure (raw byte-halving of FP16: 1.31 MB/token vs 2.62 MB/token [ILLUSTRATIVE][DERIVED]), so the same ~436 GB budget holds ~35.0 concurrent 9,500-token requests instead of ~17.5 — roughly doubling per-host concurrency without adding a host.
- **Consequences:**
  - Positive: KV residency per request falls from ~24.9 GB (FP16) to ~12.45 GB (FP8, raw byte-halving — 50% of FP16) at the 9,500-token max, so the canonical budget supports ~35.0 concurrent requests rather than ~17.5. This is a memory lever, not a compute lever: it leaves the weight-read-dominated decode cost per token nearly unchanged (it does halve the KV-read bytes, a secondary ~15% term), and it raises the concurrency the host can hold under the same KV budget.
  - Negative: FP8 KV has lower precision in the cached K/V tensors, which can add small retrieval-fidelity error on long contexts. The trade-off is memory capacity vs long-context reconstruction fidelity; it must be validated on the held-out Q&A set, not assumed.
- **Alternatives considered:**
  1. **Add capacity** — rejected as the first move: the canonical peak already needs 21 hosts on the KV screen (22 under the case (ii) prefill screen; Ch 16/17/20), so "adding a second host" misunderstands the scale; relieving the memory ceiling by adding hosts multiplies the fleet cost (each 8×H100 is ~$5.8K/mo amortized), while FP8 KV relaxes the same ceiling without commissioning new hardware.
  2. **GQA (grouped-query attention) reduction** — not available for the canonical model: the 70B reference geometry is full multi-head attention (64 KV heads, 2.62 MB/token, Ch 7). Adopting GQA would cut KV per token by ~8× (the largest single capacity lever in this book, Ch 16), but it changes the model architecture and requires retraining and re-evaluation — it is outside a serving-only change. It is the right *next-model* decision, not a knob on this deployment.
  3. **Prefix/context caching** — complementary, not a substitute: it reduces prefill work and recomputation, but does not shrink the KV resident per active long-context request; retained alongside FP8 KV.
- **Evidence Tags:** [canonical scenario][DERIVED] — at ~2.62 MB/token a 9,500-token request needs ~24.9 GB FP16 KV (9,500 × 2.62 MB ≈ 24.9 GB; Ch. 15, Ch. 17). [ILLUSTRATIVE][DERIVED] — FP8 is byte-halved to 1.31 MB/token (exactly 50% of FP16), so a 9,500-token FP8 KV ≈ 12.45 GB/request; 436 GB ÷ 12.45 GB ≈ 35.0 concurrent (floor 35). [HYPOTHESIS] — the FP8 precision shift has a small, measurable effect on long-context retrieval fidelity that must be measured on the held-out set before promoting.

This mini-case illustrates how the ADR format captures not just the "what" but the "how much" — derived quantities, trade-offs, and explicit alternatives. The team can now evaluate the proposal against the fleet's latency and quality SLAs, with all reasoning preserved for future review.

---