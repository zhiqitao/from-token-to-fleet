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

**Title:** ADR 0016 — Model Quantization: FP16 vs BF16 for 70B Inference

**Status:** Accepted

**Context:**
The fleet runs a 70-billion-parameter dense model for RAG Q&A serving. Two quantization formats are under consideration: FP16 (standard floating-point16) and BF16 (brain floating-point16). The system currently deploys FP16 on NVIDIA A100 GPUs with 80 GB HBM2e memory. The team is evaluating whether to migrate to BF16 to reduce memory pressure at the cost of reduced dynamic range.

**Decision:**
Continue with FP16 quantization for the 70B model. BF16 migration is deferred to a future hardware refresh.

**Rationale:**
- FP16 provides sufficient precision for Q&A use cases; empirical evaluation on the retrieval and generation pipelines shows no measurable drop in exact-match scores.
- A100 GPUs natively support FP16 tensor operations with no performance penalty; BF16 would require explicit casting, adding kernel launch overhead.
- The earlier A100 sizing discussion flags that a single 80 GB HBM2e A100 cannot hold a full 70B FP16 model by itself — 140 GB of weights alone exceeds 80 GB, so a deployment must use model parallelism (e.g., 2×80 GB A100 for the ~140 GB weights with KV in a portion of the pool) or quantization (FP8/8-bit) to fit a single card. The ADR therefore records the real constraint: FP16 residency is ~164 GB with 9.2K KV on the canonical 70B (Chapter 7), requiring multiple GPUs or compression. BF16 would change bytes-per-parameter but not this fit logic; the burden is the migration cost, not a free 40 GB win on an already-too-small card.
- The fleet's next GPU refresh (expected Q3 2027) will likely include BF16/TF32 support, making a deferred migration natural.

**Consequences:**
- **Positive:** No code change required; zero risk of introducing inference bugs; existing monitoring and alerting remain valid.
- **Negative:** ~40 GB more memory per model instance compared to BF16; if GPU prices or availability shift, the fleet may need to carry fewer concurrent models.
- **Monitoring:** Track per-request latency, GPU memory utilization, and model output quality on a held-out Q&A set. If quality degrades, reassess quantization choices.

**Alternatives Considered:**
1. **Pure FP32:** Rejected — 280 GB per model instance, exceeding A100 memory by 200+ GB. Not viable without model parallelism.
2. **8-bit Int8 quantization:** Rejected — while memory reduces to ~70 GB, accuracy drops on multi-step reasoning tasks; not acceptable for the Q&A SLA.
3. **Model parallelism (pipeline parallel):** Rejected — introduces cross-GPU communication latency; degrades user-perceived response time for short queries.

**Evidence Tags:** FACT: A100 FP16 tensor core throughput = 312 TFLOPS. DERIVED: 70B FP16 model footprint ≈ 140 GB parameters + 30 GB activations ≈ 170 GB total. HYPOTHESIS: BF16 migration would reduce memory by ~40% with <0.5% quality impact, based on [Schema et al., 2023].

### 3.1 A copy-ready blank template

This is the minimal template to copy into a repo, intended to be filled and to serve as a reusable professional artifact. Every section maps to a discipline from this handbook; the model-shape ADR above is one filled example, and Chapter 22's loop supplies the architecture-decision context.

```
# ADR-NNNN — <Short Decision Title>

## Status
<proposed | accepted | superseded | deprecated>   (date)

## Decision (the committed choice, one paragraph, reversible in principle)

## Architecture Decision Context   (from Chapter 22's loop)
- Business objective:  <what outcome this enables>
- Workload:            <characterization: tokens, rps, peak>
- Requirements+SLOs:   <quality / latency / availability, measurable>
- Constraints:         <privacy, region, ops, procurement, budget>

## Decision

## Alternatives considered
1. <option> — <why rejected>
2. <option> — <why rejected>

## Evidence
- <claim> — FACT/DERIVED/HYPOTHESIS [1P]/[2°]/[VERIFY]
- Unit check:  <does each derived quantity's unit make sense?>
- Sanity check: <is each result physically possible? (e.g. MFU ≤ 1)>

## Trade-offs & consequences
- Pro:   <expected positive effects>
- Con:   <expected negative effects>
- Risk:  <residual uncertainty>

## Decision owner
<person / team>

## Validation plan
<how this decision will be benchmarked/verified post-deploy>

## Rollback plan
<how we unwind if the decision fails its SLO>

## Review trigger
<what event (metric, date, new evidence) re-opens this ADR>
```

The three blocks most often skipped are the **Architecture Decision Context**, the **unit check**, and the **decision owner + review trigger** — and skipping exactly those three is what turns an ADR into a decision log instead of a decision *apparatus*. The context ties the technical choice to a business outcome; the unit check enforces Chapter 22's evidence discipline; the owner and review trigger make it a living document rather than a tombstone.

## 4. Measurement

ADRs are only as good as the evidence they embed. This chapter recommends that each ADR include at least two derived quantities — quantities computed from raw data, not merely observed. In the model-shape ADR above, the derived quantities are:

1. **70B FP16 model footprint** — $W = N \times \text{bytes-per-param} = 70 \times 10^9 \times 2 \text{ B} = 140$ GB parameters, plus ~30 GB activations (typical profiling-derived overhead) ≈ $170$ GB total. Derived from the model parameter count and a typical activation overhead factor estimated from profiling runs.
2. **BF16 migration would reduce memory by ~40% with <0.5% quality impact** — the parameter footprint scales ~linearly with byte-width: FP16 ($2 \text{ B/param}$) vs BF16-to-FP32 mixes, giving roughly a $2\times$ byte-width ratio that translates to a ~40% memory reduction for the same model; validated by a small-scale accuracy benchmark on 1% of the validation set.

Additional measurable quantities that should be tracked (even if not all included in the ADR itself) include:

- GPU memory utilization per request (derived from NVIDIA management library stats)
- Per-request latency p99 (derived from request-timing histograms)
- Exact-match score on the Q&A dev set (derived from evaluation harness runs)

Each derived quantity should be tagged with its evidence source [1P]/[2°]/[VERIFY], linking to a profiling script, a benchmark run, or a verified observation. This makes the ADR a citable source of truth rather than a static narrative.

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
- **ADR proliferation:** As the fleet grows, the number of ADRs will grow. A naming convention (ADR 0001, ADR 0002, ...) and a top-level index (ADR index.md) prevent the record from becoming unwieldy.
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

**Scenario:** The fleet decides to migrate from a single 70B FP16 model to a two-model mixture-of-experts (MoE) architecture, each expert 34B parameters, FP16, running on the same A100 GPUs.

**The ADR (draft):**

- **Title:** ADR 0017 — MoE Model Deployment
- **Status:** Proposed
- **Context:** User queries have grown 35% YoY; a single 70B model cannot sustain p99 latency < 5 seconds under peak load. MoE allows routing 2× more effective parameters within the same memory budget.
- **Decision:** Migrate to two 34B FP16 experts with top-1 routing, accepting a 5% increase in inference latency per request due to routing overhead.
- **Consequences:** 
  - Positive: Effective parameter count rises from 70B to ~68B (2 × 34B × routing fraction), improving answer quality on factual Q&A. GPU memory per expert fits within A100 80 GB, enabling 2× concurrent instances.
  - Negative: Routing logic adds ~50 ms latency; requires new monitoring for route distribution skew.
- **Alternatives considered:** 
  1. Increase batch size — rejected, increases memory pressure and worsens tail latency.
  2. Move to GGUF 4-bit — rejected, quality regression above the SLA threshold.
  3. Model sharding across GPU nodes — rejected, operations overhead for inter-node communication.
- **Evidence:** FACT: A100 FP16 expert 34B footprint ≈ 68 GB parameters + 15 GB activations. DERIVED: Top-1 routing reduces effective parameters by ~50% compared to uniform mixing.

This mini-case illustrates how the ADR format captures not just the "what" but the "how much" — derived quantities, trade-offs, and explicit alternatives. The team can now evaluate the proposal against the fleet's latency and quality SLAs, with all reasoning preserved for future review.

---