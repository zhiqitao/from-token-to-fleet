# Chapter 20: Fleet-Level Optimization

## The Architect's Question

As a RAG Q&A workload scales from a single host to a fleet of serving nodes, the architect must confront a new set of trade-offs: how does aggregate throughput scale with added hardware, how does scheduling latency affect user-perceived latency, and at what point does autoscaling cease to be cost-effective? This chapter addresses these questions through concrete arithmetic, not hand-waving.

## 1. Concept

Fleet-level optimization treats the entire collection of serving hosts as a single resource pool rather than independent islands. The central insight is that aggregate system throughput is not merely the sum of individual host throughputs; it is modulated by scheduling overhead, network contention, and the cost of moving data between hosts and storage. In a well-designed fleet, the marginal cost per additional query declines as the fleet grows, because fixed costs (model loading, infrastructure) are amortized across more concurrent requests.

The key concepts are:

- **Aggregate throughput**: The total queries-per-second the fleet can sustain before latency SLA violations.
- **Scheduling overhead**: The per-request cost of dispatching a query to an available host, including placement decisions and data movement.
- **Autoscaling break-even**: The point at which adding another host reduces marginal cost per query versus the fixed cost of provisioning and maintaining that host.

## 2. Mental Model

The mental model for fleet optimization replaces the single-host query pipeline with a two-level hierarchy. At the lower level, each host processes queries using its GPU/CPU pipeline. At the upper level, a scheduler routes incoming requests across hosts, handling load balancing, model parallelism where needed, and graceful degradation under overload.

The scheduler's decisions have direct impact on the tail of the latency distribution. Poor placement can cause some hosts to saturate while others remain underutilized, inflating the 99th-percentile latency even when aggregate throughput is ample. Conversely, intelligent scheduling—such as consistent hashing for session affinity or predictive placement based on historical patterns—keeps utilization flat across the fleet and minimizes tail latency.

A critical assumption in this model is that the workload follows a known arrival process. For the canonical scenario described here: ~2,000 users, ~5% concurrent, generating ~10 rps average and ~40 rps peak. With ~9,200 in-tokens and ~300 out-tokens per query, and a 70B dense FP16 model running on 8×H100 (640 GB total HBM3), the fleet must sustain roughly 40 concurrent queries at peak, each requiring a full forward pass through the model.

## 3. Worked Example

Consider a fleet of N hosts, each with 8×H100 running a single 70B FP16 model instance. Two capacities must be reconciled — **throughput** (tokens/s) and **KV residency** (concurrent requests) — and neither can be reduced to a single "QPS" constant, because QPS is workload-specific (per-request input/output tokens, context length, batch). 

**Latency floor first, then reconcile the two capacity bounds.** A 300-output-token request at a ~25 ms/token decode rate (Chapter 8) takes ~7.5 s of generation alone, plus ~1.1 s prefill, so the service time is ~8.6 s per request (before tool calls). Two separate ceilings bound how many requests a host can *serve per second*, and they must be reconciled — they are not interchangeable:

- **Throughput bound (tokens/s).** A host sustains an illustrative ~35,000 tokens/s [ILLUSTRATIVE achievable range, Chapter 15]. Dividing by the ~9,500 tokens/request gives ~3.7 requests/s — **but this is not achievable here**, because it would require ~3.7 × 8.6 ≈ 32 concurrent requests in flight, roughly double the host's KV-residency ceiling (C ≈ 18, Chapter 17). The token-throughput figure is thus a non-binding upper edge for this canonical workload.
- **KV-residency / latency bound (Little's law).** The real ceiling is set by concurrency and service time together: a host holds ~18 concurrent full-context requests (KV ceiling, Chapter 17) each for ~8.6 s, so it serves C/W ≈ 18 / 8.6 ≈ **2.1 requests/s** at steady state.

The binding per-host rate is the *minimum* of the two — here the KV/latency bound. This is exactly why a token-throughput number must not be divided by tokens-per-request to manufacture a "QPS": a token and a request are different units, and prefill (compute-bound) versus decode (bandwidth-bound) tokens are not fungible in that division. The per-host request rate is a *concurrency × service-time* quantity, not a tokens ÷ tokens conversion.

- **KV-residency / latency bound (Little's law).** The real ceiling is set by concurrency and service time together: a host holds ~18 concurrent full-context requests (KV ceiling, Chapter 17) each for ~8.6 s, so it serves C/W ≈ 18 / 8.6 ≈ **2.1 requests/s** at steady state. The binding per-host rate is the *minimum* of the two — here the KV/latency bound. This is exactly why a token-throughput number must not be divided by tokens-per-request to manufacture a "QPS": a token and a request are different units, and prefill (compute-bound) versus decode (bandwidth-bound) tokens are not fungible in that division. The per-host request rate is a *concurrency × service-time* quantity, not a tokens ÷ tokens conversion.

**Call this quantity what it is.** The ~2.1 req/s figure is a **KV-residency / service-time analytical ceiling under the canonical W assumption** — not a measured serving throughput. It is achievable only if serving C concurrent sequences does *not* inflate W beyond the assumed ~8.6 s, and neither a compute, bandwidth, nor scheduler constraint binds first. In real continuous batching, W is a function of batch occupancy, scheduler policy, prefill interference, decode batching, the arrival process, tensor-parallel communication, and the context distribution — so C and W are not always independent constants. Treat ~2.1 req/s as an upper-bound model, and require benchmarked goodput (Chapter 14) under the target arrival process for actual fleet sizing.


**Fleet aggregate throughput (illustrative form).** Keeping the illustrative per-host QPS = Q for the algebra, aggregate throughput is

$$
\Lambda_\text{fleet} = N \times Q
$$

At the canonical peak of 40 rps, fleet size must satisfy **both** the KV-residency and the throughput/latency bounds *and whichever binds first*. With the per-host rate at ~2.1 req/s (the binding Little bound above), a fleet for 40 rps starts at ~20 hosts on throughput alone; the KV-residency bound is satisfied at far fewer hosts (~5 at the 10-rps average, Chapter 17), but it is not the binding constraint here — at 40 rps the throughput/Little bound requires the larger fleet. The correct statement is: the fleet must satisfy both, and the *larger* requirement wins.

**Scheduling overhead.** A lightweight round-robin scheduler adds ~0.5 ms of dispatch latency per request — negligible next to a real 7.5 s decode, but it must stay under ~5% of the *measured* per-request time.

**Autoscaling economics.** Each 8×H100 host costs ~$20/hour (cloud, $2.50/GPU-hr canonical) or ~$8/hour amortized (owned) — [ILLUSTRATIVE]. The marginal cost per additional QPS is $20 ÷ (QPS gained per host); the economic lesson (diminishing cost of a marginal host once fixed costs dominate) is sound, but the exact per-QPS figure is only meaningful after the real per-host throughput is benchmarked.

## 4. Measurement

To validate fleet-level optimization claims, three core metrics should be measured at regular intervals:

| Metric | Definition | Target |
|---|---|---|
| **Aggregate QPS** | Total queries processed per second across all hosts | ≥ 2× peak rps for comfort margin |
| **Scheduler-added p99 latency** | 99th-percentile time a request waits in the fleet dispatcher (NOT end-to-end — model execution is multi-second here) | < 100 ms |
| **Scheduler-added median latency** | 50th-percentile dispatch latency, scheduler overhead only | < 30 ms |
| **Scheduling overhead** | Fraction of per-query time spent in dispatcher, not compute | < 5% |
| **Utilization variance** | Standard deviation of per-host query rate as a fraction of mean | < 0.2 |

*Note: end-to-end median/p99 latency is deliberately **not** a fleet-level target for this canonical 9.5K-token workload — a request takes ~8.6 s in service (~1.1 s prefill + ~7.5 s decode), so an *end-to-end* <100 ms p99 is infeasible (see the mini-case). The table therefore qualifies these as scheduler-added (dispatch) latency targets only.*

Measurement methodology: use a distributed load generator (e.g., Locust or a custom gRPC-driven pump) that sends queries at the target rps while instrumenting each host's internal metrics—GPU occupancy, kernel launch time, scheduler dispatch timestamp, and queue depth. Aggregate these via a time-series database (InfluxDB or Prometheus) and compute the above metrics over sliding 1-minute windows.

A practical pitfall: measuring only aggregate QPS without tracking per-host variance can mask saturation in individual nodes. Always report both the fleet-wide and per-host metrics.

## 5. Common Mistakes

- **Treating hosts as independent**: Optimizing each host in isolation (e.g., tuning batch size per host) ignores the scheduling overhead that becomes dominant when the fleet is viewed as a unit. A suboptimal batch size on one host can increase dispatch frequency for the entire fleet.

- **Overlooking data movement cost**: In RAG workloads, the ~9,200 in-tokens and ~300 out-tokens per query must be fetched from a vector database or cache. If every host pulls data independently, the network cost scales linearly with fleet size. A better approach is to colocate vector stores with serving hosts or use a shared cache layer that amortizes fetch cost across concurrent queries.

- **Autoscaling too aggressively**: Adding hosts at the first sign of latency increase can be suboptimal if the bottleneck is scheduler throughput or cache contention, not compute capacity. Measure the marginal cost of adding a host before triggering a scale-out event.

- **Ignoring cold-start cost**: When a host is freshly provisioned or re-warmed after idle, model loading takes 30–120 seconds. Autoscaling policies must account for this warm-up window; otherwise, the fleet experiences a spike in error rate or timeout during scale-out events.

## 6. Architecture Consequence

Fleet-level optimization reshapes the serving architecture in three ways:

1. **Centralized scheduler**: A lightweight service (e.g., based on etcd or a custom placement engine) maintains real-time view of per-host utilization and makes dispatch decisions. This service must be highly available and sub-millisecond in decision latency, otherwise it becomes the system bottleneck.

2. **Data colocation**: Vector indexes and model weights are stored close to the hosts that consume them. This may mean running a local Qdrant or Milvus instance per host, or using a shared object store (e.g., MinIO) with read-replicas per availability zone. The goal is to minimize the distance—measured in network hops—between the scheduler's placement decision and the data fetch.

3. **Graceful degradation**: The fleet should have a mode where, under extreme overload, it serves stale or truncated answers rather than failing entirely. This could mean returning the top-k results from a cached embedding rather than recomputing, or surfacing a "try again" message with an estimated wait time. The architectural contract must explicitize this trade-off so product teams can set appropriate SLOs.

## 7. What We Still Don't Know

Several open questions remain at the fleet level:

- **Heterogeneous hardware**: What happens when hosts mix H100, A100, and CPU-only nodes? The scheduler must handle different throughput ceilings and memory capacities, and the aggregate throughput calculation becomes a weighted sum rather than a simple multiple. Real-world measurements of mixed-device fleets are scarce; most published benchmarking uses homogeneous hardware, so the crossover point where heterogeneity hurts versus helps is not well quantified.

- **Multi-model serving**: When multiple model sizes coexist (e.g., 70B for complex queries, 7B for quick ones), the scheduling problem gains a dimensionality dimension—placement must balance model size against query urgency and host memory. Mixed-precision serving (FP16, FP8, INT4) adds another layer: lower precision increases throughput but may degrade answer quality on subtle reasoning tasks, and the quality-throughput trade-off curve is model-specific.

- **Economic auto-scaling**: The break-even point between owning hardware versus cloud-on-demand depends on utilization patterns that are workload-specific. A fleet that runs at 20% utilization on average may be cheaper in the cloud; one at 80% utilization favors owned hardware. The transition point is a function of capital expenditure amortization period, electricity cost, and the volatility of user demand. Published TCO analyses typically assume steady utilization, but bursty workloads with short-lived spikes can make ownership risky unless over-provisioned.

- **Tail-latency arbitration**: When two queries compete for the same GPU HBM bandwidth, the 99th-percentile latency can spike disproportionately. We lack a general-purpose scheduler policy that guarantees a target tail latency under arbitrary arrival patterns; this remains an area of active research. Some systems use priority queues or token buckets to cap per-query bandwidth, but these mechanisms add scheduling complexity and can increase median latency.

- **Cross-query caching effects**: In RAG workloads, the ~9,200 in-tokens and ~300 out-tokens per query overlap significantly across users asking related questions. The potential for caching intermediate embeddings or partial KV caches is substantial, but the cost of cache management (invalidation, coherence, metadata overhead) must be quantified against the compute savings. We lack large-scale measurements of caching efficiency across diverse query populations.

## 8. End-of-Chapter Mini-Case

**Scenario**: A RAG Q&A fleet serves 2,000 users with the canonical parameters: 5% concurrent, 10 rps average / 40 rps peak, ~9,200 in-tokens + ~300 out-tokens per query, 70B dense FP16 model, 8×H100 per host, 8 hosts total.

**Question**: What is the fleet's aggregate QPS capacity at batch size 4, and what is the marginal cost per QPS when scaling from 8 to 16 hosts? Is an end-to-end 99th-percentile latency under 100 ms even feasible for this workload — and if not, what can the scheduler bound?

**Solution** (illustrative algebra — the per-host figure below is an [ILLUSTRATIVE] estimate for showing the fleet math; the real per-host QPS must come from a deployment benchmark, Chapter 14, and is bounded by KV residency per Chapter 17):

- **Per-host request rate — the KV/latency bound (Ch. 17 basis).** A host holds ~18 concurrent full-context requests (the KV-residency ceiling, Chapter 17) and each request is in service ~8.6 s (~1.1 s prefill + ~7.5 s decode of 300 output tokens at ~25 ms/token, Chapter 8). So a host serves C/W ≈ 18 / 8.6 ≈ **2.1 requests/s** at steady state. This is the defensible capacity number: it is derived from concurrency × service time (Little's law), not from dividing a token throughput by tokens per request. (Do NOT divide ~35,000 tokens/s by ~9,500 tokens/request to get ~3.7 req/s — that would require ~32 concurrent requests, which the 18-request KV ceiling cannot hold.)
- **Fleet aggregate (8 hosts):** 8 × 2.1 ≈ **17 req/s**, which is **below** the canonical 40-rps peak. On this binding bound the idealized minimum is ⌈40 / 2.1⌉ = **20 hosts**; allowing ~10% scheduling loss raises this floor to 40 / (2.1 × 0.9) ≈ 21.2 → **22 hosts**. (The KV-residency bound, Chapter 17, is satisfied at far fewer hosts — ~5 at the 10-rps average — but the throughput/latency bound binds here, so the larger requirement governs.)
- **Marginal cost (real basis):** adding one host at ~$20/hr (cloud, [ILLUSTRATIVE]) buys ~2.1 req/s, so marginal cost ≈ $20 ÷ 2.1 ≈ **$9.5 per req/s per hour.** (The earlier illustrative $0.012 figure assumed 250 req/s per host — a ~120× understatement that comes entirely from the impossible latency; with a real multi-second service time per request the per-host rate is ~2.1, not 250.)
- **Algebra practice (kept [ILLUSTRATIVE]):** the per-host 250 QPS / fleet 2,000 QPS / $0.012 per QPS arithmetic from the original exercise is retained only to show the *structure* of the fleet math (marginal host cost ÷ marginal capacity). It deliberately uses a hypothetical per-host QPS that is not achievable for this 9.2K-in/300-out workload; the architect must substitute the measured per-host rate from a Chapter 14 deployment benchmark, or the ~2.1 req/s bound derived here.
- **The 100-ms end-to-end p99 is infeasible under the stated workload, and that is the honest answer.** A request here takes ~7.5 s of decode alone (300 output tokens × ~25 ms/token, Chapter 8), so no scheduler-overhead percentage can bring end-to-end p99 under 100 ms — the model execution already exceeds the budget by two orders of magnitude. What the scheduler *can* bound is the overhead it adds *on top of* model execution: a lightweight round-robin dispatcher adds ~0.5 ms per request, which is negligible against a multi-second decode, and a <=5% scheduler-added p99 is comfortably achievable. The architect's job here is to reject the impossible SLO and state what is actually controllable, rather than tune arithmetic until a 100-ms figure appears reachable.

**Table 20-1** — Fleet QPS and latency vs. host count, batch size, and scheduling overhead.

![Fig 20.1 - Fleet throughput, and per-host utilization, vs. host count at the canonical peak load (40 rps). Top panel: throughput against host count from the KV/latency bound (~2.1 req/s/host), with a ~90% scheduling-overhead line. Bottom panel: per-host utilization at the canonical 40 rps peak. This is the honest quantity for the tail: **p99 is driven by per-host utilization, not by host count alone.** Adding hosts lowers per-host utilization (more headroom) hence lowers the expected tail; the 70%-utilization and 100%-saturation reference lines show the provisioning target. The tail also depends on the arrival process, scheduling policy, batching, and the service-time distribution, which a provisioning model alone does not capture. [ILLUSTRATIVE][DERIVED]](figures/fig-20-2001.png)