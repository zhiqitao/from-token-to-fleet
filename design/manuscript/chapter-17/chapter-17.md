# Chapter 17 — From Server to Fleet

## The Architect's Question

Having established the single-host serving model — a 70B FP16 model on 8×H100 serving ~2,000 registered users at ~10 rps average / ~40 rps peak — the natural next question is: when does one host cease to suffice, and how do we scale to a fleet? This chapter answers the architect's question: at what point must we move from a lone server to a coordinated fleet, and what are the quantitative trade-offs of that transition?

## 1. Concept

The transition from a single-server deployment to a fleet is not a qualitative leap but a quantitative threshold crossing. In the single-server model, all request routing, load balancing, and health monitoring occur within one process on one machine. The architect thinks in terms of request-per-second capacity, GPU memory utilization, and inference latency on that one host. As traffic grows, the single host hits limits in three domains: computational throughput (tokens/sec), GPU memory capacity, and inter-request interference (contention for shared resources such as NVMe I/O, PCIe bandwidth, and CPU). When any of these limits is breached, the fleet model introduces multiple identical hosts behind a load balancer, each independently serving a slice of the total traffic. The fleet model adds three new architectural ingredients: (a) a load balancer that distributes requests across hosts, (b) cross-host communication patterns when a request span multiple machines, and (c) capacity planning that accounts for redundancy, failover, and the diminishing returns of horizontal scaling. The key insight is that horizontal scaling transforms per-host limits into system-wide capacities, but at the cost of added coordination overhead, state synchronization, and network budgeting.

## 2. Mental Model

We visualize the fleet as a two-level hierarchy. At the top level, a load balancer — either hardware (L7 switch) or software (NGINX, HAProxy, Cloud Load Balancer) — accepts inbound requests and routes them to one of N backend hosts. Each backend host runs an identical copy of the model and serves requests independently. At the bottom level, each host operates exactly as the single-server model does: a model engine accepting prompts, producing completions, and returning tokens to the load balancer, which forwards the response to the client.

The mental model introduces two new invariants. First, the **throughput invariant**: total system throughput ≈ N × throughput_per_host, reduced by a factor ρ that captures load‑balancer overhead, health‑check traffic, and imperfect distribution (typically ρ ∈ [0.85, 0.98] depending on LB sophistication). Second, the **memory invariant**: total GPU memory across the fleet is N × memory_per_host, but the per-host memory available for model weights and KV cache remains the same as the single-host case. The fleet does not increase the per-host model size; it increases the aggregate number of concurrent requests the system can serve by parallelizing across hosts.

![Fig 17.1 - A fleet of one model: a load balancer fans requests out to N identical hosts, each running the same model on its own GPU [ILLUSTRATIVE][DERIVED]](figures/fig-17-1701.png)

A critical detail is the **session-affinity** decision. If user sessions must maintain conversation state (KV cache, accumulated tool outputs, retrieval context), the load balancer must route subsequent requests from the same user to the same host (sticky sessions). This reduces cross-host communication but limits the effective parallelism, because a popular user can pin a single host to capacity while other hosts stand underutilized. If sessions are stateless (the model is reloaded or KV cache is discarded between requests), any host can serve any request, and load distribution becomes even. The architect must choose between density (sticky sessions, higher per-host utilization) and evenness (stateless routing, lower per-host utilization but better load balance).

## 3. Worked Example

We continue from the canonical scenario: ~2,000 registered users, ~5% concurrent (~100 users), ~10 rps average / ~40 rps peak, prompt ~9,200 input tokens + ~300 output, 70B-class dense FP16 model, 8×H100 host with 640 GB GPU memory. A single 8×H100 host's capacity is set by the *binding constraint* among GPU compute, HBM bandwidth, and KV cache memory. Let us verify with arithmetic, keeping the two quantities distinct: **aggregate HBM** (640 GB) is not the same as **KV-available memory** (640 − 140 GB weights − runtime/workspace reserve).

**Single-host concurrency capacity (KV-bound).** The per-token KV footprint for the canonical 70B model is 2 × layers × hidden × bytes = 2 ×80 ×8,192 ×2 = 2,621,440 B ≈ 2.62 MB/token (Chapter 7 canonical). Subtract the 140 GB FP16 weights and ~64 GB runtime/activations/workspace from the 640 GB pool, leaving ≈436 GB available for KV. Each request at 9,200 input + 300 output reserves a **9,500-token max** KV of 9,500 ×2.62 MB ≈ 24.9 GB (the initial 9.2K residency is 24.1 GB). A single host therefore holds C = 436 GB ÷ 24.9 GB ≈ **18 concurrent requests** — using the canonical layer-complete κ. Computing κ from a single layer instead of all 80 would overstate the concurrency figure by two orders of magnitude.

**Viability at peak.** Peak traffic is 40 rps; with the canonical ~8.6 s per-request service time (1.08 s prefill + 7.5 s decode), Little's Law puts ≈ 40 × 8.6 ≈ **344 requests in flight**, against a KV capacity of ~18 per host. **A single host is not viable at peak even for the non-agentic canonical workload** — the fleet needs roughly ⌈344/18⌉ ≈ **20 hosts** at 40 rps (≈28 at the 70% utilization target), and more for growth to 100 rps. This flips the original conclusion: the fleet is not a distant luxury but a necessity at the canonical peak, driven by the product of service time (8.6 s) and arrival rate.

**KV compression is the first lever.** Switching KV to FP8 (≈54% of BF16, vLLM-measured [S6]) cuts the 9.5K max per-request KV to ≈13.4 GB and raises C to ≈33 concurrent per host (436 ÷ 13.4 ≈ 32.5), roughly doubling headroom before buying hardware. This is why the architect treats KV precision as a first-class capacity dial, not a cosmetic detail.

**Threshold for fleet expansion.** Suppose the agentic layer from Chapter 19 is added. Chapter 19's own telemetry puts the turn distribution at 68% terminating in T=1, 25% in T=2, 5% in T=3, and 2% exceeding the turn limit (falling back to single-shot). That makes the **median** turn count T=1 (68% of requests finish on the first turn) and the **95th percentile** T=3 (cumulative 68+25+5 = 98% by T=3). Each turn adds ~800 tokens of retrieved context (delta) and ~65 tokens of model-generated reasoning (gamma), so the effective per-request token count is
$$
I(T) = I_0 + T(\delta + \gamma) + O_\text{final} = 9{,}200 + T \times 865 + 300
$$
- Median (T=1): $I(1) = 9{,}200 + 1 \times 800 + 1 \times 65 + 300 = 10{,}365$ tokens
- 95th percentile (T=3): $I(3) = 9{,}200 + 3 \times 800 + 3 \times 65 + 300 = 12{,}095$ tokens
- Worst case (T=4, the rare tail beyond the 95th): $I(4) = 9{,}200 + 4 \times 800 + 4 \times 65 + 300 = 12{,}960$ tokens

The KV cache per request rises proportionally, and per-host concurrency capacity follows from the Ch17 formula $C = M_{kv}/(I(T)\kappa)$:
- at T=1 (median): $10{,}365 \times 2.62 \text{ MB} \approx 27.2 \text{ GB/request} \Rightarrow C \approx 16$ concurrent
- at T=3 (95th): $12{,}095 \times 2.62 \text{ MB} \approx 31.7 \text{ GB/request} \Rightarrow C \approx 14$ concurrent
- at T=4 (worst case): $12{,}960 \times 2.62 \text{ MB} \approx 34.0 \text{ GB/request} \Rightarrow C \approx 13$ concurrent

Even the *median* agentic request already drops a single host below the 40-concurrent peak demand (C≈16 < the in-flight concurrency needed at peak), so the fleet is required under almost any agentic assumption. **Scaling forecast (service-time-aware).** Because the canonical workload's service time is ~8.6 s — not a ~1 s latency — the in-flight concurrency at the 40 rps peak is λ_peak × W ≈ 40 × 8.6 ≈ **344 requests**, not 40. With FP16 KV (baseline C≈18), the fleet needs ⌈344/18⌉ ≈ **20 hosts** at full utilization (≈28 at the 70% utilization target). Agentic turns make this strictly worse: each additional turn adds ~800 tokens of context (lowering C) and more generated tokens (raising W), so the agentic T=3 case needs a larger fleet still (C≈14 in the 95th-percentile case and a longer W). The load balancer distributes λ/N rps per host and λ·W/N concurrent per host, and each host's per-host KV usage must stay comfortably under its C. This is the fleet point: hosts are added because *concurrency in flight × KV-per-request* exceeds a single host's residency — and concurrency in flight must be computed from the full service time, not a target latency.

**Cross-host communication.** In the canonical scenario, requests are independent — no user session spans multiple hosts. If an agentic loop required retrieving results from a prior host (e.g., distributed retrieval), the system would need a coordination layer (Redis, gRPC, or message queue) with added latency. We quantify this below in the measurement section.

## 4. Measurement

We derive three real quantities from the worked example and from production traffic patterns.

### Per-host throughput and KV cache budget

Let H be the number of hosts, λ the incoming rps peak, T the random variable for agent turn count with distribution P(T), δ = 800 tokens per turn of retrieved context, γ = 65 tokens of model-generated reasoning per turn, and O_final = 300 final output tokens. The per-request token count is

$$
I(T) = I_0 + T \cdot \delta + T \cdot \gamma + O_\text{final}
$$

where I₀ = 9,200 is the baseline input tokens. The per-host concurrent‑request capacity in terms of KV cache is

$$
C = \frac{M_{kv}}{I(T) \cdot \kappa}
$$

where M_kv is the KV‑available memory — the portion of on‑host HBM left for KV after weights and runtime — and $\kappa = 2 \times n_\text{layers} \times d_\text{hidden} \times \text{bytes} \approx 2.5$ MB/token is the per‑token KV footprint (Chapter 7 canonical; κ includes all layers — omitting the layer factor understates KV memory by orders of magnitude). For the canonical host, M_kv = 640 GB − 140 GB (FP16 weights) − ~64 GB (runtime/activations/workspace/NCCL) ≈ 436 GB. Dividing memory by bytes (not the byte‑divided‑by‑bytes collapse that trips unit analysis):

- For T = 0 (baseline, I = 9,500): C = 436 GB / (9,500 ×2.62 MB) ≈ 436/24.9 ≈ **18 concurrent requests per host**.
- For T = 1 (median, per the Chapter 19 distribution; 68% terminate on turn 1): C = 436 GB / (10,365 ×2.62 MB) ≈ 436/27.2 ≈ **16 concurrent requests per host**.
- For T = 3 (95th percentile; cumulative 98% by T=3): C = 436 GB / (12,095 ×2.62 MB) ≈ 436/31.7 ≈ **14 concurrent requests per host**.
- For T = 4 (worst-case tail beyond the 95th): C = 436 GB / (12,960 ×2.62 MB) ≈ 436/34.0 ≈ **13 concurrent requests per host**.

These numbers are the KV-residency ceiling; measured concurrency may be lower if GPU throughput or bandwidth binds first, so the architect takes the min of the KV, compute, and bandwidth capacities.

If the peak traffic λ_peak = 40 rps, Little's Law gives the number of requests *in flight* as λ_peak × L, where **L must be the full per-request service time** — for this canonical workload that is ~8.6 s (1.08 s prefill + ~7.5 s decode of 300 output tokens at ~25 ms/token, Chapter 8), NOT a sub-second TTFT-type latency. Using a ~1 s "latency" here is the classic fleet-sizing error: it undercounts in-flight concurrency by roughly the ratio of service time to target latency (here ~8.6×). The minimum number of hosts is

$$
H_\text{min} = \left\lceil \frac{\lambda_\text{peak} \cdot W}{C} \cdot \frac{1}{u} \right\rceil
$$

where $u$ is the utilization target and $W$ is the **full service time** (end-to-end: prefill + decode + any tool/orchestration overhead). At the canonical peak:

- **KV-residency ceiling (C) is a per-host concurrency limit, not a fleet-size answer by itself.** A host holds C ≈ 18 concurrent full-context requests (computed above). The fleet size is governed by how many requests are *in flight at the peak*, which is λ_peak × W.
- At λ_peak = 40 rps and W ≈ 8.6 s, in-flight concurrency ≈ 40 × 8.6 ≈ **344 requests**. With C ≈ 18 per host (FP16 KV) at full utilization, H_min ≈ 344/18 ≈ 19 → **~20 hosts** (≈28 at the 70% utilization target). This is the honest fleet size and matches the throughput/latency analysis in Chapter 20.
- Switching to FP8 KV (κ ≈ 1.42 MB/token, 54% of BF16, C ≈ 33 at T=0) raises per-host concurrency to ~33, cutting the fleet to H_min ≈ 344/33 ≈ 10.4 → **~11 hosts** (≈15 at 70% util).

**Separate the two questions explicitly** — they are not interchangeable, and mixing them is the source of the under-sizing error:

1. **KV-only concurrency sizing** (does one host's KV budget hold the in-flight requests?): $H_{KV} = \lceil \lambda W / (C \cdot u) \rceil$. This uses C (KV-residency ceiling) and the full service time W.
2. **Full service-capacity sizing** (does the fleet's aggregate request rate clear the peak?): the same quantity when C/W is the per-host service rate — i.e. $H = \lceil \lambda / (\rho \cdot (C/W)) \rceil$. Because Little's Law ties concurrency, service time and arrival rate, these two views coincide: $\lambda W / C = \lambda / (C/W)$.

KV residency provides one capacity ceiling, but it is not a fleet-size answer by itself. When the canonical 300-token decode duration is included, Little's Law raises in-flight concurrency from the misleading "40 requests at 1 second" approximation to roughly **344 requests at 40 rps**, and the fleet must be sized to that.

### Load‑balancer overhead factor

Let ρ be the effective throughput fraction after load‑balancer effects. Empirically, a well‑configured software LB (NGINX) achieves ρ ≈ 0.95, meaning total system throughput = ρ · N · throughput_per_host. A hardware L7 switch may achieve ρ ≈ 0.98. The overhead comes from: health‑check traffic (~1% of requests), session‑affinity hashing skew, and LB process CPU limits. The throughput_per_host itself must come from a benchmark on the actual workload (tokens/context/batch) — it is an ILLUSTRATIVE proxy until measured. What is *derivable* is the KV‑residency ceiling C from Section 3; the LB overhead multiplies the schedulable fraction of that ceiling. In the worked example, the fleet is currently sized by KV capacity (Section 3), not by a fabricated tokens/s number: at T=4, FP16-KV C≈13/host (436 GB ÷ (12,960 × 2.62 MB ≈ 34.0 GB) ≈ 12.8) sets the ceiling, and adding a host raises aggregate schedulable concurrency by ρ·C, i.e. ~12 concurrent at ρ=0.95.

### Cross-host interconnect budget

If a fraction φ of requests require cross-host data (e.g., distributed retrieval, shared vector index), each such request incurs an additional network round‑trip latency λ_net and moves data volume D over the host‑to‑host network. Assuming an intra‑rack 10 Gbps Ethernet backbone, the per-request bandwidth drawn on the network is

$$
B_\text{per-req} = \frac{D}{\lambda_\text{net} \cdot \varphi \cdot N}
$$

For D = 5 MB (top‑5 retrieval snippets), λ_net = 20 ms (typical rack latency), φ = 0.1 (10% of requests cross‑host), N = 4: $B_\text{per-req} = 5 \text{ MB} / (0.02\text{ s} \times 0.1 \times 4) = 625\text{ MB/s} \approx 5$ Gbps — already **half** the 10 Gbps link, so only ~2× headroom. If φ scales to 0.5 (many distributed queries) and D grows to 50 MB, the per-request bandwidth becomes $50/(0.02 \times 0.5 \times 4) = 1{,}250$ MB/s ≈ 10 Gbps — right at the link limit, and aggregate traffic across the backbone is

$$
\text{aggregate} = \varphi \cdot N \cdot \frac{D}{\lambda_\text{net}} = 0.5 \times 4 \times \frac{50 \text{ MB}}{0.02 \text{ s}} = 5 \text{ GB/s}
$$

which exceeds the 10 Gbps (~1.25 GB/s) limit and would require 5× overprovisioning or a wider fabric (e.g., 50 Gbps or 100 Gbps). This calculation shows that cross-host communication must be dimensioned early, even if the base case appears benign.

## 5. Common Mistakes

1. **Ignoring KV cache growth from agentic loops.** A common mistake is to assume that adding an agentic layer barely changes per-request resource usage. As shown, each turn adds ~800 tokens of context, which linearly reduces concurrent‑request capacity. Forgetting this leads to under‑provisioning the fleet.

2. **Over‑relying on sticky sessions without load‑balance analysis.** Sticky sessions simplify cross‑host communication but can create hot‑spot hosts if a few users generate disproportionate traffic. Always measure the session‑affinity distribution; if the Gini coefficient of per-host request counts exceeds 0.3, consider stateless routing or session sharding.

3. **Using raw rps to size the fleet.** Requests‑per‑second is necessary but not sufficient; the product of rps × average latency gives concurrent load, which must fit within KV cache capacity. A host serving 40 rps at 0.5 s latency carries 20 concurrent requests, whereas at 2 s latency it carries 80 — the same rps, very different resource usage.

4. **Under‑estimating load‑balancer overhead.** A 5% throughput reduction from ρ = 0.95 may seem small, but at the margin of capacity it can be the difference between fitting on N hosts and needing N+1. Always provision with ρ explicitly in the formula.

5. **Failing to model latency tail under spike traffic.** GPU inference time is not constant; under sustained high load, kernel‑mode preemption, memory fragmentation, and concurrent kernel launches can increase per‑token latency by 20–50%. The linear model L = λ_inference + λ_tool is a lower bound; the architect should add a 20% safety margin.

## 6. Architecture Consequence

Transitioning from one host to a fleet reshapes every layer of the system.

**GPU fleet sizing.** The number of hosts N must satisfy the service‑time‑augmented capacity formula H = ⌈ λ_peak · W / (C · util_target) ⌉, where C depends on the agentic turn distribution and W is the full per‑request service time (which rises with turns — each turn adds retrieval latency and generated tokens). Two effects compound as turns grow: C falls (more tokens → more KV per request) and W rises (more per‑turn latency), so in‑flight concurrency λ·W grows on both sides. For the canonical customer‑facing peak (40 rps, W≈8.6 s), in‑flight ≈ 344 and H ≈ ⌈344/18⌉ ≈ 20 hosts at full utilization (≈28 at 70% util) with FP16 KV; FP8 KV cuts that to ~11 (≈15 at 70%). The lesson is honest: the binding term is λ·W/C, and W must be the real service time, not a sub‑second target latency. Size for the 95th‑percentile latency and token scenario, not the median, and treat KV precision as the cheapest way to shrink the fleet before adding hardware.

**Load‑balancer selection and configuration.** The choice between hardware (F5, Cloud LB) and software (NGINX, HAProxy) affects ρ and the session‑affinity model. Hardware L7 switches offer better ρ (≈0.98) but less fine‑grained traffic‑shaping; software LBs offer ρ ≈ 0.95 but can implement consistent hashing for session affinity. The architect should match the LB capability to the session model: sticky sessions → any LB; stateless → software LB with consistent hashing.

**Cross-host data infrastructure.** If any request type requires cross‑host communication (distributed retrieval, multi‑model orchestration, state sync), a dedicated backend network must be provisioned. The minimum bandwidth is B_min = φ · N · D / λ_net, and the fabric should provide at least 2×B_min for headroom. In the canonical scenario with φ = 0.1, N = 4, D = 5 MB, λ_net = 20 ms, B_min ≈ 0.8 Gbps (0.1 × 4 × 5 MB / 0.02 s = 100 MB/s), so a 10 Gbps intra‑rack network has ample headroom. But the architect should instrument φ and D from production telemetry and revisit the bandwidth provisioning quarterly.

**Observability across the fleet.** With N hosts, tracing a request end‑to‑end requires correlating the LB routing decision, the selected host’s inference logs, and any cross‑host data calls. Structured logging with a request‑ID field that propagates from the client through the LB to the host and back is essential. Distributed tracing (OpenTelemetry, Jaeger) should be enabled by default. Alerts should trigger when per‑host concurrency exceeds 80% of C, when LB error rate exceeds 0.1%, or when cross‑host bandwidth utilization exceeds 70%.

**Failover and redundancy.** With N ≥ 2, the fleet provides automatic failover: if one host crashes, the LB routes its traffic to the remaining N−1 hosts, reducing capacity by ~1/(N−1). For N = 4, a single‑host loss reduces capacity from 100% to 75% (assuming equal load distribution). The architect must decide whether this is acceptable or whether N must be larger (e.g., N = 6 for 83% residual capacity after one failure). Health‑check frequency and graceful drain procedures affect the real-world failover time, typically 5–15 seconds.

## 7. What We Still Don't Know

Despite the arithmetic above, several questions remain open and would benefit from targeted research:

- **Turn-count distribution under fleet load.** Do larger fleets (N > 4) change the observed T distribution? Intuitively, more hosts reduce per-host contention, potentially lowering latency and reducing the agentic loop depth, but empirical measurement is needed.
- **Latency amplification non-linearity.** The agentic latency model from Chapter 19 frames the added orchestration overhead as β(T) = 1 + (T·L_agent / L_base), which assumes constant per‑turn orchestration overhead and a fixed base generation time. Under fleet scaling, GPU saturation may make per‑turn overhead grow with concurrent requests, introducing convexity. Empirical load‑testing across N = 1, 2, 4, 8 hosts is required.
- **Optimal fleet size for cost vs. latency.** The cost of adding a host is roughly the cost of 8×H100 (multi‑hundred-thousand dollars). The marginal latency improvement from the Nth host diminishes (diminishing returns). A cost‑per‑latency‑improved curve would help the architect justify fleet size to stakeholders.
- **Cross‑host communication patterns at scale.** The φ = 0.1 assumption may not hold for all workloads (e.g., RAG over a shared index, distributed fine‑tuning). Real‑world measurement of cross‑host traffic patterns is needed to size the backbone accurately.
- **Context‑caching efficacy across a fleet.** If many users query related topics, can a fleet‑wide KV cache or retrieval cache reduce the effective δ per request? The savings could be substantial but require cross-host cache-invalidation protocols that are not yet well understood.

## 8. End-of-Chapter Mini-Case: Going Agentic: Service-Time-Aware Fleet Sizing

**Scenario.** A AI‑product company starts with a single 8×H100 host serving the canonical traffic of 2,000 users at 10 rps average / 40 rps peak, 9,200 input + 300 output tokens, no agentic layer. After six months, user growth pushes peak traffic to 100 rps, and the team introduces the agentic layer from Chapter 19 with a maximum of 3 turns (median T = 1, 95th‑percentile T = 3, per the Ch19 telemetry distribution).

**Initial sizing analysis (service-time-aware).** At T = 3 (the 95th‑percentile, and the honest worst‑case sizing point), I(3) = 9,200 + 3·800 + 3·65 + 300 = 12,095 tokens. With FP16 KV (κ = 2.62 MB/token), per‑request KV ≈ 31.7 GB, so KV‑residency capacity C = 436 GB ÷ 31.7 GB ≈ 14 concurrent requests per host. But concurrency *in flight* is λ × W, where W is the full service time, which here grows with the agentic turns: 1.08 s prefill (held at the canonical 9.2K single‑shot representative; a 12,095‑token prefill would scale to ~1.42 s) + (~495 generated tokens × ~25 ms/token = ~12.4 s decode) + ~0.4 s of per‑turn tool/retrieval latency ≈ **~13.8 s** (the tool/turn term here combines the per‑turn tool + retrieval latency; Chapter 19's `T·L_agent` ≈ 660 ms is the same additive orchestration overhead expressed per the turn distribution). (This W is the full agentic service time — decode of all generated tokens plus the grown‑context prefill. It is *not* the incremental orchestration‑overhead figure of ~660 ms at T=3 that Chapter 19 reports as its $T \cdot L_\text{agent}$; the two are different quantities, and it is this full W that drives concurrency and fleet size, per Chapter 19's scope note.) So at the 100‑rps peak, in‑flight concurrency ≈ 100 × 13.8 ≈ 1,380 requests, not 200. Against C ≈ 14 per host, H = ⌈1,380/(14 ×0.7)⌉ ≈ **141 hosts** on FP16 KV (≈99 at full utilization). This is the honest arithmetic the service-time model produces — the naive "1–5 hosts" rps estimate is off by two orders of magnitude because it ignores both the decode duration and the added turn latency.

**KV compression changes the answer.** Switching the KV cache to FP8 (κ ≈ 1.42 MB/token, 54% of BF16) cuts per‑request KV at T=3 to ~17.1 GB and raises C to ≈25 per host, giving H ≈ ⌈1,380/(25 ×0.7)⌉ ≈ **79 hosts** (≈55 at full utilization). Combined with prompt/prefix caching (which can eliminate the repeated 9,200‑token base prompt from the KV per turn), the practical fleet lands well below the FP16 number. KV precision and prefix caching are the primary levers that make agentic fleets affordable, but even with both, an agentic 70B workload at 100 rps is a *multi‑dozen‑host* fleet, not a handful.

**Decision.** After the honest sizing, the team provisions on the order of ~55–80 hosts (the FP8+prefix-cache range, to be validated by a Chapter 14 benchmark before committing hardware), runs NGINX as a software load balancer with consistent hashing for session affinity, and instruments each host with OpenTelemetry tracing. Cross‑host communication is minimal (φ ≈ 0.05), so the existing 10 Gbps intra‑rack network suffices. Monthly GPU‑utilization metrics should run in the 55–70% band against the KV‑residency ceiling, and the SLA must be validated by a deployment benchmark (Chapter 14) — end‑to‑end latency including agentic overhead is an ILLUSTRATIVE target until measured.

**Lesson.** The fleet decision is driven by KV‑residency capacity vs. **service‑time‑scaled concurrency** (λ·W) — not by raw rps, and not by a per‑layer KV constant. The architect's checklist: (1) compute I(T) for the expected turn distribution, (2) derive per‑host concurrent capacity C from the *canonical* per‑token KV (2 × layers × hidden × bytes), (3) convert peak rps into concurrency via λ·W using the **full service time** (prefill + decode of all generated tokens + per‑turn tool latency), (4) compute H = ⌈λ·W/(C·util_target)⌉, (5) apply the cheapest capacity levers first — KV precision (FP8), prefix caching, attention architecture (GQA/MQA) — before buying hosts, and (6) validate throughput and latency with a benchmark, not an assumption. A multi‑dozen‑host FP8 fleet costs meaningful GPU capital, but avoids both wasteful over‑provisioning and a costly re‑platform when traffic doubles.

---

**Table 17-1: Fleet sizing matrix — KV-residency ceiling and minimum hosts (canonical FP16 KV, W = full service time).**

Minimum hosts H = ⌈λ·W / (C·u)⌉ at a 70% utilization ceiling, where the in-flight concurrency **must** use the full per-request service time W — not a sub-second target latency. Two service times apply: W ≈ 8.6 s for the non-agentic canonical request (1.08 s prefill + 7.5 s decode), and W ≈ 13.8 s for the T=3 (95th-percentile) agentic request (the mini-case's service-time-aware figure). These are the in-flight counts the chapter derives in §3/§4.

| Traffic scenario (λ peak) | in-flight @ non-agentic W=8.6s | in-flight @ agentic W=13.8s | H @ T=0, FP16 (C≈18) | H @ T=3 (95th), FP16 (C≈14) | H @ T=3 (95th), FP8 (C≈25) |
|---|---|---|---|---|---|
| 40 rps (canonical peak) | 344 | 552 | ⌈344/12.6⌉ ≈ 28 | ⌈552/9.8⌉ ≈ 57 | ⌈552/17.5⌉ ≈ 32 |
| 100 rps (growth) | 860 | 1,380 | ⌈860/12.6⌉ ≈ 69 | ⌈1380/9.8⌉ ≈ 141 | ⌈1380/17.5⌉ ≈ 79 |
| 200 rps (2× growth) | 1,720 | 2,760 | ⌈1720/12.6⌉ ≈ 137 | ⌈2760/9.8⌉ ≈ 282 | ⌈2760/17.5⌉ ≈ 158 |

*The chapter sizes fleets at the **95th-percentile turn scenario (T=3)** per its own rule ("size for the 95th-percentile token scenario"), so the agentic columns use T=3 — which is also what the §8 mini-case computes (141 hosts at 100 rps). C is the KV-residency ceiling (derived): 18 concurrent full-context requests on FP16 at T=0, 14 at T=3 (12,095 tokens × 2.62 MB ≈ 31.7 GB/request over 436 GB), and ~25 on FP8 at T=3 (12,095 × 1.42 MB ≈ 17.2 GB/request; the mini-case's "≈79 hosts at FP8"). The 70% utilization target and the λ, W values are ILLUSTRATIVE scenario inputs to be validated by a deployment benchmark (Chapter 14) before committing hardware. H is a KV-residency lower bound — the true answer is the max of this KV bound and the measured throughput bound.*

---
