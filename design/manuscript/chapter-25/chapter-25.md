# Chapter 25: The Architecture Decision Record

## The Architect's Question

As the "From Token to Fleet" handbook reaches its final chapters, we turn from technical mechanisms to the governance of those mechanisms. With ~2,000 users, a RAG Q&A system, and a 70B dense FP16 deployment, the question becomes: how does the team capture, justify, and evolve the architectural choices that keep the fleet running? The Architecture Decision Record (ADR) is the answer — a lightweight, text-first practice that records not just what was decided, but why, what alternatives were considered, and what trade-offs were accepted. This chapter explores the ADR pattern in the context of a production AI system, providing a reusable template and a worked example centered on model-shape choices.

## 1. Concept

An Architecture Decision Record is a single Markdown file that captures a significant architectural decision and its context. The format was popularized by Michael Nygard and has been adopted by teams ranging from startups to enterprises managing complex AI/ML stacks. Each ADR follows a minimal structure:

- **Title** and status (proposed, accepted, superseded, deprecated)
- **Context** — the problem, constraints, and goals that prompted the decision
- **Decision** — the chosen approach, concise and explicit
- **Consequences** — outcomes, both positive and negative, that flow from the decision
- **Alternatives considered** — other paths rejected, with brief rationale for rejection

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
- For this workload both precisions clear the quality bar on the held-out Q&A set, with no exact-match change between them, so the deciding factors are range robustness and consistency — not capacity. In this illustrative evaluation the exact-match result showed no difference [ILLUSTRATIVE][ASSUMPTION — to be confirmed by the deployment quality gate: we did not run this comparison on real hardware in this handbook; it is an assumed outcome for the worked ADR].
- A100 (and the 8×H100 host) natively supports BF16 and TF32 on its Tensor Cores. There is no "next GPU generation" required and no explicit-casting penalty; the premise that these formats wait for future hardware is itself the kind of error an ADR should catch.
- Operational consistency: the training run that produced the weights used BF16 mixed precision. Keeping inference in BF16 avoids a training-to-serving cast and keeps behavior predictable.

**Consequences:**
- **Positive:** range robustness in attention/softmax and long-context accumulation; no change in weight residency (both precisions are ~140 GB).
- **Negative:** lower mantissa precision than FP16 in the weights (BF16 has 7 mantissa bits vs FP16's 10), so FP16 is more precise where values already sit in range; in the illustrative evaluation on this workload the exact-match result showed no quality difference [ILLUSTRATIVE][ASSUMPTION — to be confirmed by the deployment quality gate], so the trade-off is precision headroom, not observed quality. There is no free memory — and none should be expected.
- **Monitoring:** track per-request latency, GPU memory utilization, and held-out Q&A quality. If the BF16 output drifts, fall back to FP16 and compare both on the same set (they differ in precision, not footprint).

**Alternatives Considered:**
1. **FP16:** Rejected here — no memory advantage over BF16, and a narrower exponent range. Retained as the fallback if BF16 shows precision drift.
2. **FP8 weights:** The genuine memory lever (halves residency to ~70 GB) but needs per-tensor calibration and a validation gate; deferred as the next step, paired with the FP8 KV discussion in Chapter 7.
3. **FP32:** Rejected — 280 GB residency with no quality benefit for this workload.

**Evidence Tags:** FACT: FP16 and BF16 are both 16-bit (2 bytes/parameter); a 70B model is ~140 GB in either. FACT: A100/H100 Tensor Cores support BF16 and TF32 natively. DERIVED: weight residency is unchanged by the FP16↔BF16 choice. ILLUSTRATIVE[ASSUMPTION]: no exact-match difference between FP16 and BF16 on the held-out Q&A set — an assumed outcome for this worked ADR, to be confirmed by the deployment quality gate (not a measurement in this handbook).

### 3.1 A copy-ready blank template

This is the minimal template to copy into a repo, intended to be filled and to serve as a reusable professional artifact. Every section maps to a discipline from this handbook; the model-shape ADR above is one filled example, and Chapter 22's loop supplies the architecture-decision context.

```
# ADR-NNNN — <Short Decision Title>

## Status
<proposed | accepted | superseded | deprecated>  (date)

## Decision (the committed choice, one paragraph,
   reversible in principle)

## Architecture Decision Context  (from Chapter 22's loop)
- Business objective:  <what outcome this enables>
- Workload:            <characterization:
                         tokens, rps, peak>
- Requirements+SLOs:   <quality / latency / availability,
                         measurable>
- Constraints:         <privacy, region, ops,
                         procurement, budget>

## Decision

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
```

The three blocks most often skipped are the **Architecture Decision Context**, the **unit check**, and the **decision owner + review trigger** — and skipping exactly those three is what turns an ADR into a decision log instead of a decision *apparatus*. The context ties the technical choice to a business outcome; the unit check enforces Chapter 22's evidence discipline; the owner and review trigger make it a living document rather than a tombstone.

## 4. Measurement

ADRs are only as good as the evidence they embed. This chapter recommends that each ADR include at least two derived quantities — quantities computed from raw data, not merely observed. In the model-shape ADR above, the derived quantities are:

1. **70B FP16 model footprint** — $W = N \times \text{bytes-per-param} = 70 \times 10^9 \times 2 \text{ B} = 140$ GB parameters, plus ~30 GB activations (typical profiling-derived overhead) ≈ $170$ GB total. Derived from the model parameter count and a typical activation overhead factor estimated from profiling runs.
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
- **RQO (Reasoned Quality Optimization):** By forcing the articulation of alternatives and evidence, ADRs make the trade-off surface explicit. Teams can point to an ADR and say "we chose FP16 over BF16 because of X, Y, Z" — and those reasons are verifiable.
- **Reduced cognitive load:** Engineers no longer need to re-derive the rationale for every architectural choice. The ADR serves as a single source of truth.
- **ADR proliferation:** As the fleet grows, the number of ADRs will grow. A naming convention (ADR 0001, ADR 0002, ...) and a top-level index (ADR index) prevent the record from becoming unwieldy.
- **Integration with CI:** ADRs can be validated as part of the CI pipeline — e.g., ensuring every ADR has a status, a rationale, and at least one evidence tag. This automation reinforces the habit.

On the negative side, ADRs add a small writing overhead. For a team of ~10 engineers making ~1–2 significant architectural decisions per month, this is a manageable cost. The payoff — reduced on-call noise, faster onboarding, and fewer "why did we do it this way?" debates — more than compensates.

![Fig 25.1 — The Anatomy of an Architecture Decision Record [ILLUSTRATIVE conceptual]](figures/fig-25-2501.png)

## 7. What We Still Don't Know

Despite the structured format, several questions remain open and would benefit from future ADRs or empirical studies:

1. **ADR fatigue:** Does the presence of many ADRs overwhelm the team, leading to superficial writing or skipped documentation? 
2. **Evidence decay:** How long do derived quantities remain valid? Should ADRs include a "last reviewed" date and a trigger for re-evaluation?
3. **Cross-ADR dependencies:** When multiple ADRs interact (e.g., a quantization choice interacts with a retrieval chunk-size choice), how should the team document the dependency graph?
4. **Tooling gaps:** No widely adopted tool exists for ADR graph visualization or impact analysis. Building such a tool would require understanding the ADR network and its evolution over time.
5. **ADR format evolution:** The minimal format (title, context, decision, consequences, alternatives) works for most cases, but edge cases — decisions involving regulatory compliance, security, or data governance — may require additional sections.

These open questions are not blockers; they are signals for when the practice matures and the team needs more sophisticated governance.

## 8. End-of-Chapter Mini-Case

**Scenario:** The fleet serves the canonical RAG Q&A workload on an 8×H100 host. At peak the KV cache is the binding constraint: within the canonical ~436 GB practical KV budget, a full-precision FP16 KV at ~2.5 MB/token lets a single host hold ~18 concurrent 9,500-token requests. The concurrency ceiling is now limiting throughput below the target request rate.

**The ADR (draft):**

- **Title:** ADR 0017 — KV Cache Precision: FP16 vs FP8
- **Status:** Proposed
- **Context:** The canonical 70B RAG workload is KV-memory-bound at decode (Ch. 15). At the ~436 GB practical KV budget, full FP16 KV caps concurrency at ~18 requests/host, and Ch. 17 shows that ~40 rps at ~1 s per request implies ~40 in-flight requests — more than one host can hold. To reach the target request rate we need either more host capacity or more KV residency per host.
- **Decision:** Render the KV cache in FP8 for the long-context decode path, keeping prefill and the retrieval/prompt phase in FP16. FP8 KV cuts KV residency to ~54% of the FP16 figure (vLLM's measured FP8-KV ratio), so the same ~436 GB budget holds ~33 concurrent 9,500-token requests instead of ~18 — roughly doubling per-host concurrency without adding a host.
- **Consequences:**
  - Positive: KV residency per request falls from ~24.9 GB (FP16) to ~13.4 GB (FP8, 54% of BF16) at the 9,500-token max, so the canonical budget supports ~33 concurrent rather than ~18. This is a memory lever, not a compute lever: it does not change decode speed per token, it raises the concurrency the host can hold under the same KV budget.
  - Negative: FP8 KV has lower precision in the cached K/V tensors, which can add small retrieval-fidelity error on long contexts. The trade-off is memory capacity vs long-context reconstruction fidelity; it must be validated on the held-out Q&A set, not assumed.
- **Alternatives considered:**
  1. **Add capacity** — rejected as the first move: the canonical peak already needs ~20 hosts (Ch 16/17), so "adding a second host" misunderstands the scale; relieving the memory ceiling by adding hosts multiplies the fleet cost (each 8×H100 is ~$5.8K/mo amortized), while FP8 KV relaxes the same ceiling without commissioning new hardware.
  2. **GQA (grouped-query attention) reduction** — already in place; a further reduction changes model architecture and retraining, outside a serving-only change.
  3. **Prefix/context caching** — complementary, not a substitute: it reduces prefill work and recomputation, but does not shrink the KV resident per active long-context request; retained alongside FP8 KV.
- **Evidence Tags:** FACT: at ~2.62 MB/token a 9,500-token request needs ~24.9 GB FP16 KV (Ch. 15, Ch. 17). FACT: vLLM measures FP8 KV at ~54% of BF16 KV residency [S6][1P]. DERIVED: at 54% of the FP16 figure, a 9,500-token FP8 KV ≈ 13.4 GB/request; 436 GB ÷ 13.4 GB ≈ 33 concurrent. [HYPOTHESIS]: the FP8 precision shift has a small, measurable effect on long-context retrieval fidelity that must be measured on the held-out set before promoting.

This mini-case illustrates how the ADR format captures not just the "what" but the "how much" — derived quantities, trade-offs, and explicit alternatives. The team can now evaluate the proposal against the fleet's latency and quality SLAs, with all reasoning preserved for future review.

---