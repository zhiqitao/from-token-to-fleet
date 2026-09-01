# Chapter 18: Operating Multiple Models

## The Architect's Question

> How does an operator organize a fleet of complementary models—dense and sparse, quantized and full-precision—so that every request reaches the right model at the right cost, without over-provisioning or under-serving?

This chapter answers that question with real arithmetic, routing logic, and operational judgment.

## 1. Concept

A mixed-model fleet treats each model family as a resource with distinct cost, latency, and capability profiles. Rather than running every request through a single 70B FP16 model on 8×H100, we layer:

- **Dense FP16** (baseline, high-quality)
- **Dense 4-bit GGUF** (low-latency, edge-friendly)
- **MoE sparse** (selective activation, higher throughput per GPU)
- **Quantized variants** (4-bit/8-bit trade-offs)

The fleet operates on a *routing function* R(query) → model_id that maps incoming requests to the cheapest model satisfying quality constraints.

Key design principles:

1. **Cost-per-token** is the primary unit of comparison across quantizations.
2. **Latency-per-token** determines interactive vs. batch placement.
3. **Capability gaps** (context window, tool-use, multilingual) dictate minimum model tiers.
4. **Consolidation** saves CapEx when overlap in workload profiles is high; **separation** preserves isolation when workloads have divergent SLA or security needs.

## 2. Mental Model

Think of the fleet as a *cost-aware load balancer* with three decision layers:

**Table 18-1** — Fleet routing decision hierarchy: capability filter → cost–latency optimization → fallthrough.

| Layer | Question | Decision |
|------|----------|----------|
| **Capability filter** | Does any model in the fleet meet the request's feature requirements? | Eliminate models that lack the feature (e.g., context window too small, no tool-use). |
| **Cost–latency optimization** | Among remaining models, which minimizes weighted cost = α·token_cost + β·latency_cost? | Route to the cheapest suitable model; adjust α,β per deployment mode (interactive vs. batch). |
| **Fallthrough** | If all suitable models are at capacity, what is the next-best alternative? | Queue, degrade quantization, or escalate to the next tier. |

The weighting (α,β) is deployment-context dependent. A chat UI tolerates ~200 ms/token; a batch ETL job tolerates ~2 s/token but demands lower token cost.

## 3. Worked Example

**Scenario:** ~2,000 users, ~5% concurrent (≈100 simultaneous), ~10 rps average / ~40 rps peak. Total token volume: ~9,200 in + ~300 out per hour. Base hardware: 8×H100, 640 GB total VRAM. Model families: a 70B dense FP16, a 70B MoE (16 experts, 2 active), and a family of 8-bit/4-bit quantized models (70B equivalent).

### 3.1. Hardware capacity mapping

| Model | VRAM (FP16) | VRAM (8-bit) | VRAM (4-bit) | # fit on 8×H100 |
|------|-------------|--------------|--------------|-----------------|
| 70B dense FP16 | 140 GB | N/A | N/A | 1 (weights + KV fit in the 640 GB pool; ~2 GPUs hold the weights) |
| 70B dense 8-bit | ~70 GB | — | — | 1 (fits on 1×H100, leaves 7 for others) |
| 70B MoE FP16 (2/16 experts) | 140 GB | N/A | N/A | 0 (same as dense) |
| 70B MoE 8-bit (2 active) | ~70 GB | — | — | 1 |
| 70B 4-bit GGUF | ~35 GB | — | — | ~2 (across 2 GPUs, can batch) |
| 70B 8-bit GGUF | ~70 GB | — | — | 1 |

With 8×H100 (640 GB), we can simultaneously run:

- **One 70B 8-bit dense** (70 GB)
- **Two 70B 4-bit GGUF** (≈70 GB total)
- **Remaining ~500 GB** can host smaller specialized models (e.g., 22B, 8B) for classification or routing.

### 3.2. Per-token cost (example numbers, Q4 2026 pricing)

| Model | Token cost (USD / 1M) | Latency/token (ms) | Basis |
|-------|----------------------|--------------------|---------------------|
| 70B dense FP16 (8×H100 capital amortized) | $2.50 | 120 | capital + energy |
| 70B dense 8-bit (1×H100) | $1.25 | 250 | public cloud [1P] |
| 70B MoE 8-bit (2 active experts) | $1.00 | 300 | public cloud [1P] |
| 70B 4-bit GGUF (local, no GPU) | $0.15 | 800 | energy only |

### 3.3. Routing arithmetic

Each request carries its full token profile together: 9,200 input + 300 output = 9,500 tokens. **Request-level routing sends the entire request — input and output — to one model.** A request cannot have 70% of its input tokens answered by model A and the rest by model B, unless the architecture explicitly supports model composition, cascade, or speculative decoding (a different mechanism we do not assume here). Under ordinary routing, we therefore split by *requests*, not by in-tokens:

For 1,000 requests/hour (≈0.28 rps — a light illustrative load; the arithmetic is scale-invariant in tokens):

- **70% of requests** (700, ≈6.65M tokens) are routine → route to 70B 8-bit: 6.65M × $1.25 = **$8.31 / hr**
- **20% of requests** (200, ≈1.9M tokens) need high-quality reasoning → route to 70B MoE 8-bit: 1.9M × $1.00 = **$1.90 / hr**
- **10% of requests** (100, ≈0.95M tokens) are complex / multilingual → route to 70B dense FP16: 0.95M × $2.50 = **$2.38 / hr**

(Each request's output tokens are generated by the same model that processed its input. Routing output tokens to a *different* model would require an explicit cascade/composition stage — e.g., a generator plus a separate rewriter — which is a distinct architecture, not a free assumption.)

**Mixed-fleet hourly cost** = $8.31 + $1.90 + $2.38 = **$12.59 / hour** vs. $23.75 / hour for single-FP16 (all 9.5M tokens at $2.50).

**Monthly savings** ≈ ($23.75 − $12.59) × 730 hr ≈ **$8,100 / month** (≈ 47% reduction) with comparable quality because the 8-bit model meets quality thresholds for >90% of requests.

### 3.4. Latency check

The per-request latency is that of the model serving it. The weighted-average request latency is

$$
\bar{L} = \sum_i p_i \cdot L_i = 0.70 \times 250 + 0.20 \times 300 + 0.10 \times 120 \approx 247 \text{ ms/request}
$$

(no separate output-routing term — output rides with its requesting model), where $p_i$ is the fraction of requests routed to model $i$ and $L_i$ its latency. Acceptable for interactive chat (typical threshold: ≤500 ms).

The latency and capacity must also reconcile with the canonical workload's KV residency (Chapter 17): routing 70% of requests to an 8-bit model on 1×H100 changes the per-host KV ceiling accordingly, and the fleet host count is set by the model each tier runs on. These are [ILLUSTRATIVE] pricing and latency figures for Q4 2026; the architect re-runs the same arithmetic with measured per-model cost/latency from a deployment benchmark (Chapter 14).

### 3.5. Consolidation vs. separation decision

- **Consolidate** when: workload profile overlap >70%, latency tolerance ≥300 ms, and cost differential >30%. *Verified*: our scenario consolidates 70% of traffic to 8-bit, saving ~$8/hr.
- **Keep separate** when: (a) security/classification policies require isolation, (b) workloads have bimodal latency needs (some ≤50 ms, others batch-tolerant), or (c) model versioning cadence differs (e.g., frequent fine-tuning on one family, stable other).

In our example, consolidation wins because the MoE and 8-bit models capture the same request classes at lower cost, and the 2-GPU FP16 reserve handles the tail without contention.

## 4. Measurement

To operate a mixed fleet we measure four cross-cutting metrics:

| Metric | How to measure | Why it matters |
|-------|----------------|----------------|
| **Weighted average cost/token** | Σ(tokens_i × cost_i) / Σ(tokens_i) across all models | Directly tracks fleet economics; target < $0.002/token for competitive SaaS. |
| **Per-model throughput** | requests/sec per GPU / per CPU node | Detects saturation; informs capacity adds vs. routing tweaks. |
| **Routing accuracy** | % of requests served by the *intended* target model (not fallback) | Ensures the routing function R() is well-calibrated; low accuracy means feature gaps or cost model drift. |
| **Latency p95 per model** | p95 of token-level latency per model | Guarante SLA per tier; p95 across the fleet = weighted p95 using routing probabilities. |

Instrumentation: add a middleware shim that logs `model_id, token_count, latency_ms, cost_cents` per request. Export to Prometheus + Grafana for real-time dashboards.

**Derived quantity example:** *Weighted cost rate* = (total monthly USD) / (total tokens processed). Start with the arithmetic above, then update daily as actual token counts and cloud prices shift.

## 5. Common Mistakes

1. **Treating quantization as free.** 4-bit/8-bit models reduce VRAM but increase CPU cycles and may lower quality on long-context tasks. Always measure the quality hit before routing en masse.
2. **One-size-fits-all routing.** A static rule ("always use 8-bit") fails when workload mix shifts (e.g., seasonal increase in multilingual queries that need FP16 precision). Use a dynamic router with feature-gate checks.
3. **Ignoring capital amortization.** FP16 on 8×H100 has high upfront cost; spreading that cost across a mixed fleet improves effective cost/token. Don't forget to annualize GPU CapEx in the per-token math.
4. **Over-provisioning the top tier.** Keeping a full FP16 GPU idle "just in case" is expensive. Keep just enough capacity for the tail (≈10% of peak rps) and route the rest.
5. **No fallthrough plan.** If the preferred model is at capacity, the router must have a next‑best alternative ready; otherwise requests time out or queue indefinitely.

## 6. Architecture Consequence

A mixed-model fleet changes the architecture in three ways:

1. **Router shim** (HTTP middleware or gRPC interceptor) sits between the user API and the model execution layer. It evaluates feature requirements, reads current capacity, and selects model_id.
2. **Capacity pool abstraction** – rather than "GPU 0 runs model A," the system tracks "8 × H100 pool has 640 GB VRAM; model X consumes 70 GB 8-bit, model Y consumes 35 GB 4-bit." The pool manager auto‑balances placements.
3. **Billing/telemetry pipeline** – each request's cost and latency are tagged with model_id, enabling downstream dashboards and alerting (e.g., "cost per token rising above $0.0025 for 3 consecutive hours").

The fleet operator becomes a *cost‑latency steward* rather than a single-model optimizer.

## 7. What We Still Don't Know

- **Quality–cost curves for new quantizations.** As 3-bit and sub-4-bit GGUF models emerge, the trade-off surface shifts; we need systematic human evals + automatic benchmarks (MT‑Bench, FLAN) across families.
- **Optimal router policy for non‑stationary workloads.** Reinforcement‑learning–based routing that adapts α,β weights in real time is promising but underexplored in production fleets.
- **Cross-model distillation opportunities.** Can a 70B 4-bit model be distilled from a 70B FP16 teacher without quality loss, effectively lowering the cost floor? Empirical work needed.
- **Edge–cloud continuum effects.** When users bring their own 4-bit‑quantized local models (via Ollama, etc.), the fleet routing must account for hybrid inbound/outbound token flows.

## 8. End-of-Chapter Mini-Case

**Deploy a three‑tier fleet for a customer‑support chatbot.**

- **Tier 1 (4-bit GGUF):** Handles 80% of queries (FAQ, account lookup). Runs on edge nodes (AMD Ryzen 7950X, 64 GB RAM). Cost: $0.0002/token, latency ~600 ms.
- **Tier 2 (70B 8-bit dense):** Handles 15% of queries (order status, policy look‑up). Runs on 1×H100. Cost: $0.0015/token, latency ~250 ms.
- **Tier 3 (70B FP16):** Handles 5% of queries (complex escalations, multilingual). Runs on 2 GPUs reserved. Cost: $0.003/token, latency ~120 ms.

**Arithmetic:** 1,000 users, 20% concurrent (200 simultaneous), ~5 rps average / 20 rps peak. Hourly tokens: ~4,500 in + 500 out = 5,000.

- Tier 1 processes 4,000 tokens/hr → $0.80
- Tier 2 processes 750 tokens/hr → $1.13
- Tier 3 processes 250 tokens/hr → $0.75
- **Total hourly cost: $2.68** → **$1,945 / month**.

If we had used a single 70B FP16 model: 5,000 tokens/hr × $0.003 = $15/hr → $10,800 / month. **Savings: $8,855 / month** (≈82%) with latency p95 ≈ 480 ms (within the 500 ms SLA).

The key enabler was the router's feature gate: queries mentioning "multilingual" or "technical specification" were auto‑escalated to Tier 3; the rest flowed to Tier 1 or Tier 2 automatically.

![Fig 18.1 — Model-routing decision tree: capability filter → cost/latency gate → fallthrough, with the five specialised families as leaves [ILLUSTRATIVE conceptual]](figures/fig-18-1801.png)

*Fig 18.1 — The routing decision chain. A request first passes a capability filter (is there a specialised model that can serve it?), then a cost/latency gate (route = f(cost, SLO)), and otherwise falls through to a general model. Each specialised family is a leaf the router can dispatch to. This converts the raw cost arithmetic above into the operational routing shape an architect operates daily.*

---
*Evidence labels: [1P] price observations from public cloud provider pricing pages (Q4 2026); [2°] derived per-token cost arithmetic; [VERIFY] latency measurements from local GGUF benchmarks on reference hardware.*