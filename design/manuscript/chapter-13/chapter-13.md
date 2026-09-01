# Chapter 13 — Reference Architectures: From Local to Hyperscale

## The Architect's Question

After this chapter we should be able to look at a characterized workload and place it on the right **archetype** — the canonical deployment shapes that recur across the industry — without reinventing a design from scratch. We will map the four tiers (local/edge, server, cluster, hyperscale), state what each can serve in model size and traffic, and develop the decision rule for when a workload outgrows a tier and must escalate. After this chapter, "we run on a server" or "we need a cluster" is a defensible, quantified statement tied to the workload's numbers — not a guess.

## 1. Concept

Architectures recur not because engineers lack imagination but because the *constraints* recur. Four archetypes cover the vast majority of AI deployments, distinguished by how many GPUs are involved and over what interconnect:

1. **Local / edge** — a single GPU (or a laptop-class accelerator). Serves small models (up to ~7-13B at tight context) that must run on-device for privacy, latency, or connectivity reasons. Interconnect is not the question; memory capacity is.

2. **Server** — one host with 1-8 GPUs, typically H100/H200, joined by NVLink/NVSwitch. Serves dense models up to ~70B-180B with real concurrency. This is the canonical enterprise-Q&A tier and the book's 8×H100 baseline. [2° FACT]

3. **Cluster** — multiple hosts (tens to hundreds of GPUs) joined by InfiniBand or high-speed Ethernet. Required when a model exceeds a node's memory (so it must be split per Ch10) or when traffic outgrows one host (so P/D disaggregation per Ch11 applies).

4. **Hyperscale / data-center fleet** — dedicated fleets of specialized inference/training clusters, often MoE or KV-centric (Mooncake-style disaggregation [S4][1P]), serving many tenants at enormous scale. The economics favor extreme specialization.

These are a *continuum*, not hard categories; the useful question is always **which tier does OUR workload's bounds demand?**

## 2. Mental Model

Think of each tier as a **box with a fixed memory budget and a fixed cross-node bandwidth**. A workload fits a tier if (a) the model's weight + KV residency fits the tier's total GPU memory (Ch7), and (b) the tier's interconnect can carry the communication the chosen parallelism requires (Ch9/Ch10), and (c) the resulting throughput + latency meets the SLO (Ch11).

The mental model is a **ladder with explicit rungs**: we climb a rung when a binding constraint can no longer be met. The three classic triggers for climbing:

- **Memory**: model + KV no longer fits one node → cluster (split weights).
- **Traffic**: one host's throughput ceiling (goodput) below demand → more replicas (DP across nodes) or P/D disaggregation → cluster.
- **Latency/geography**: SLO can't be met due to distance or contention → move the serving edge closer (local) or split prefill/decode.

We do not climb for fashion; we climb when a measured number crosses a threshold.

## 3. Worked Example

### Placing the Canonical Workload

The canonical enterprise-Q&A RAG workload sits firmly on the **server** tier. We verify each bound:

- **Memory**: 70B FP16 weights = 140 GB; KV for 9.2K context at FP16 ≈ 24.7 GB; inference residency ≈ 164.7 GB [2° DERIVED]. An 8×H100 host (640 GB) fits this with ample headroom for concurrency (Ch11 showed ~24 GB per request × concurrent requests still fits). ✓ [2° DERIVED]

- **Throughput**: ~10 rps average / 40 rps peak, input-heavy (9.2K in / 300 out). Ch11 showed continuous batching + prefix caching keeps p95 TTFT under the 2 s SLO on a single 8×H100 host. ✓

- **Interconnect**: parallelism is unnecessary (one node) — the interconnect question doesn't bind. ✓

So a single 8×H100 server is the right archetype — which is exactly what earlier chapters assumed. [2° DERIVED]

### Escalating: When 10× Traffic Forces the Cluster Tier

Now suppose the workload's demand grows to ~100 rps average (a 10×). Recompute the ceiling:

- **Throughput ceiling of one host**: continuous batching on 8×H100 at ~9.5K tokens/request sustained roughly tens of thousands of tokens/s; goodput against the SLO is the binding number. At ~100 rps × 9.5K tokens = ~950K tokens/s, one host's goodput is exceeded. [2° DERIVED]

- **Response**: replicate the model across multiple servers (data parallelism at the serving layer — run N identical 8×H100 hosts behind a load balancer), so each host carries ~10 rps again. This is the **cluster** tier: the model still fits one node (so no weight-splitting), but the *fleet* of replicas is a small cluster. The escalation is driven by traffic, not memory. [2° DERIVED]

### Dropping a Tier: When Privacy Forces Local

If the workload must run fully on-site without data leaving a facility, and the model can be distilled to a 7-13B capable of the Q&A task, the **local/edge** tier applies: a single GPU runs the distilled model at reduced (but acceptable) accuracy for privacy. The tier choice traded capability for the operational constraint (privacy). [2° DERIVED]

#### Table 13-1 — Reference architecture archetypes

| Tier | GPUs | Interconnect | Model range | Typical latency | When to use |
|---|---|---|---|---|---|
| Local / edge | 1 | — | ≤7-13B dense | low (on-device) | privacy, offline, connectivity |
| Server | 1-8 | NVLink/NVSwitch | ≤~70-180B dense | meets §14 SLO | most single-tenant enterprise |
| Cluster | tens-hundreds | InfiniBand/Eth | any that needs splitting | depends | model > node, or traffic > host goodput |
| Hyperscale fleet | dedicated | high-bandwidth fabric | MoE+, specialized | extreme-scale economics | multi-tenant, largest scale |

*(Bounds are [2° FACT]/[2° DERIVED] design heuristics, not vendor guarantees.)*

## 4. Measurement

The tier decision is only as good as the numbers that trigger it. We measure three things:

1. **Residency vs tier memory** (Ch7): does weight + KV fit? If not, the floor is a cluster.
2. **Host goodput ceiling vs demand** (Ch6/Ch11): measure the max rps/tokens/s the host delivers at the SLO, and compare to demand. When demand > ceiling, escalate.
3. **Communication fraction** (Ch9/Ch10): if the parallelism the cluster requires spends >~20% of step time on collectives, the interconnect (not the GPU) is the binding tier constraint.

These three numbers locate the workload on the ladder objectively.

## 5. Common Mistakes

- **Choosing hyperscale before measuring goodput.** Most workloads never exceed one host's goodput; building a fleet first is expensive and unnecessary.
- **Using model size as the only tier driver.** A 70B model fits a server; traffic, not size, usually forces the cluster — an architect who only watches parameters escalates too early or too late.
- **Ignoring the operational constraint.** Privacy/geography can force a *lower* tier regardless of what compute wants; the ladder is bounded by operations, not just performance.
- **Assuming a smaller model can't serve the tier.** Distilled small models on local GPUs can meet the goal when the capability suffices — don't over-provision the tier.
- **Treating tiers as walls.** They are a continuum; the correct answer can be a hybrid (edge cache + server generation) the measured numbers justify.

## 6. Architecture Consequence

The archetype sets the entire downstream design vocabulary. On the **server** tier (canonical), the consequences are already established: continuous batching + PagedAttention + prefix caching (Ch11), KV quantization when residency binds (Ch7), no parallelism (Ch10). Moving up to **cluster** introduces: DP/PP/TP replicas (Ch10), P/D disaggregation (Ch11), and interconnect budgeting (Ch9). Moving **down** to local forces distillation and on-device KV limits. The tier is the top-level decision; every other choice in the book slots beneath it.

![Fig 13.1 — The reference-architecture ladder and its escalation triggers [ILLUSTRATIVE conceptual]](figures/fig-13-1301.png)

*Fig 13.1 — The reference-architecture ladder: single GPU → single host → multi-host → cluster/fleet, with escalation triggers (red: model/KV/throughput outgrows a tier) and de-escalation (green: privacy, data sovereignty, cost) moving a workload between tiers.*

<!-- Figure spec: mechanism-first diagram; two axes (model residency on one, throughput demand on the other); four tier regions; arrow annotations for the three escalation triggers. Canonical workload dot in the server tier. -->

## 7. What We Still Don't Know

- **Exact host goodput ceilings** depend on the specific server, model, degree and batching; the representative numbers here are [VERIFY] per deployment.
- **When P/D disaggregation's benefit crosses its cost** for mid-tier workloads is [HYPOTHESIS]; the breakpoint is workload- and fabric-specific.
- **Fleet-level economics** (Ch16 TCO across a cluster) interact with the tier choice in ways that are [HYPOTHESIS] until a real cost model is applied.

## 8. End-of-Chapter Mini-Case

An architect returns to the canonical internal Q&A service a year later. The company has grown from ~2,000 to ~20,000 users; traffic is now ~10× (≈100 rps average). The on-prem service is saturated: p95 TTFT has drifted to 3 s against the 2 s SLO. Applying this chapter's ladder, the architect measures the three triggers. Memory: the 70B model still fits one 8×H100 node (164.7 GB residency), so the *model* does not force a cluster. Traffic: host goodput is exceeded at ~100 rps — the binding trigger. Operational: the data privacy requirement still forbids a public hyperscale cloud. The architect's decision: escalate to the **cluster** tier but keep it on-prem — run a small fleet of 8×H100 replicas behind a load balancer so each carries ~10 rps again, staying within both the memory and the privacy constraints. The result: p95 TTFT back under 1.8 s at 100 rps, on site, without hyperscale — because the architect climbed the ladder precisely one rung, and the correct rung was determined by the measured traffic trigger, not by fashion or by model size alone.
