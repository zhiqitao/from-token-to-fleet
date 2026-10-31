# Chapter 18 — Operating Multiple Models

## The Architect's Question

> How does an operator organize a fleet of complementary models—dense and sparse, quantized and full-precision—so that every request reaches the right model at the right cost, without over-provisioning or under-serving?

This chapter answers that question with real arithmetic, routing logic, and operational judgment.

## 1. Concept

A mixed-model fleet treats each model family as a resource with distinct cost, latency, and capability profiles. Rather than running every request through a single 70B FP16 model on 8×H100, we layer:

- **Dense FP16** (baseline, high-quality)
- **Dense 4-bit GGUF** (lowest cost, edge-friendly; highest latency — see §18.3.2)
- **MoE sparse** (selective activation, higher throughput per GPU)
- **Quantized variants** (4-bit/8-bit trade-offs)

The fleet operates on a *routing function* R(query) → model_id that maps incoming requests to the cheapest model satisfying quality constraints.

Key design principles:

1. **Cost-per-token** is the primary unit of comparison across quantizations.
2. **Latency-per-token** determines interactive vs. batch placement.
3. **Capability gaps** (context window, tool-use, multilingual) dictate minimum model tiers.
4. **Consolidation** saves capex when overlap in workload profiles is high; **separation** preserves isolation when workloads have divergent SLA or security needs.

## 2. Mental Model

The fleet operates as a *cost-aware load balancer* with three decision layers:

**Table 18-1** — Fleet routing decision hierarchy: capability filter → cost/SLO gate → fallthrough.

| Layer | Question | Decision |
|------|----------|----------|
| **Capability filter** | Does any model in the fleet meet the request's feature requirements? | Eliminate models that lack the feature (e.g., context window too small, no tool-use). |
| **Cost/SLO gate** | Among remaining models, which minimizes weighted cost = α·token_cost + β·latency_cost? | Route to the cheapest suitable model; adjust α,β per deployment mode (interactive vs. batch). |
| **Fallthrough** | If all suitable models are at capacity, what is the next-best alternative? | Queue, degrade quantization, or escalate to the next tier. |

The weighting (α,β) is deployment-context dependent. A chat UI tolerates ~200 ms of added service latency per request; a batch ETL job tolerates ~2 s per request but demands lower token cost. These are per-request service-latency thresholds for the short-prompt routing scenario — the chat figure sits under the chapter's ≤500 ms interactive threshold (§18.3.4) — not the canonical TTFT/TPOT SLO (Ch 4); the canonical TPOT budget of ~25 ms is a per-token quantity and is not what these per-request figures measure.

## 3. Worked Example

**Scenario:** ~2,000 users, ~5% concurrent (≈100 simultaneous), ~10 rps average / ~40 rps peak. Total token volume per request: ~9,200 in + ~300 out. Base hardware: 8×H100, 640 GB total VRAM. Model families: a 70B dense FP16, a 70B MoE (16 experts, 2 active), and a family of 8-bit/4-bit quantized models (70B equivalent).

### 3.1. Hardware capacity mapping

| Model | VRAM (model precision) | VRAM (8-bit) | VRAM (4-bit) | # fit on 8×H100 |
|------|-------------|--------------|--------------|-----------------|
| 70B dense FP16 | 140 GB | — | — | 1 (140 GB weights across the 8-GPU pool, ~17.5 GB/GPU under TP; with KV, the full 640 GB pool is used) |
| 70B dense 8-bit | — | ~70 GB | — | 1 (weights alone fit on 1×H100, leaving 7 GPUs; with the canonical KV budget the 8×H100 pool still holds weights + KV) |
| 70B MoE FP16 (2/16 experts) | 140 GB | — | — | 1 (same as dense FP16; weights + KV fit in the 640 GB pool) |
| 70B MoE 8-bit (2 active) | — | ~70 GB | — | 1 |
| 70B 4-bit GGUF | — | — | ~35 GB | ~5 (canonical 436 GB KV budget reserved: (640−436)/35 ≈ 5; ~18 by weights alone; the worked deployment below uses 2 copies) |

*(Each row's footprint is its own model's size at the named precision — put the number in that precision's column. A dash means that precision does not apply to the row's naming.)*

\needspace{3\baselineskip}

With 8×H100 (640 GB), we can simultaneously run the weights of:

- **One 70B dense FP16** (140 GB)
- **One 70B 8-bit dense** (70 GB)
- **One 70B MoE 8-bit** (~70 GB)
- **Two 70B 4-bit GGUF** (≈70 GB total)

That is ~350 GB of weights, leaving ~290 GB for KV cache and for smaller specialized models (e.g., 22B, 8B) for classification or routing. KV, not weights, is the binding term: as the FP16 row above notes, that tier's KV alone uses the full 640 GB pool, so this co-residency holds only while the resident tiers' combined KV fits.

### Qualification precedes placement and promotion {.unnumbered}

Placement starts with feasible configurations, not with a vendor label. A small local model can be a candidate for an Intel GPU or an OpenVINO client path when its operators, memory budget and service behavior pass the same gates as the central service.[^oct-ix-t7-openvino] An integrated GPU and an NPU remain separate choices even when they share a package and system memory. Their advertised compute figures do not form one execution budget.[^oct-ix-t7-devices]

A routing policy also needs the cost of failure. If a local attempt misses its contract and falls back to a central service, both attempts contribute resource use and end-to-end delay. The fallback route must preserve the data policy and still meet any applicable deadline. Promotion therefore follows a canary on the exact model/backend configuration, with monitored cache behavior, correctness, tail latency and rollback. Replacing a driver, kernel package or graph mode can change that configuration even when the model identifier is unchanged.[^oct-ix-t7-configpath]

### 3.2. Per-token cost (example numbers, Q4 2026 pricing)

| Model | Token cost (USD / 1M) | Per-request service latency (ms) | Basis |
|-------|----------------------|--------------------|---------------------|
| 70B dense FP16 | $2.50 | 120 | capital + energy |
| 70B dense 8-bit | $1.25 | 250 | public cloud [1P] |
| 70B MoE 8-bit | $1.00 | 300 | public cloud [1P] |
| 70B 4-bit GGUF | $0.15 | 800 | energy only |

*Row hardware (Model-column parentheticals, moved here): 70B dense FP16 on 8×H100, capital amortized; 70B dense 8-bit on 1×H100; 70B MoE 8-bit with 2 active experts; 70B 4-bit GGUF local, no GPU.*

*Basis note (reconciled with Ch16's TCO):* these per-1M figures are **per-model nominal rates for routing comparison** — the cost per 1M tokens if that model instance were serving at its own nominal throughput on its own host. The fleet-amortized per-token cost derived in Ch16 §16.3 divides the full peak-provisioned fleet TCO (~$155,817/mo ≈ ~$156K/mo, 21 hosts at full utilization) by the token volume that fleet serves at the canonical workload — 6.24M requests/month × 9,500 tokens ≈ 5.93×10¹⁰ tokens/month — giving ~$155,817 ÷ 5.93×10¹⁰ ≈ **$2.63/1M**. That is close to — but not equal to — the $2.50/1M the table prints for the FP16 tier, and the closeness is a coincidence of this volume, not an identity: the fleet-amortized figure spreads the whole 21-host included-cost total (capex amortization + energy + staff alloc) over the canonical token volume, while the table's FP16 row is a capital + energy nominal rate for one model on its own host. The two bases do not numerically match, and each moves independently if the fleet size, the served volume, or the price inputs change. Read each number with its own basis; the mixed-fleet *savings* conclusion below depends only on the relative per-model rates, not on the absolute self-host basis.

### 3.3. Routing arithmetic

Each request carries its full token profile together: 9,200 input + 300 output = 9,500 tokens. **Request-level routing sends the entire request — input and output — to one model.** A request cannot have 70% of its input tokens answered by model A and the rest by model B, unless the architecture explicitly supports model composition, cascade, or speculative decoding (a different mechanism we do not assume here). Under ordinary routing, we therefore split by *requests*, not by in-tokens:

For 1,000 requests/hour (≈0.28 rps — a light illustrative load; the arithmetic is scale-invariant in tokens):

- **70% of requests** (700, ≈6.65M tokens) are routine → route to 70B 8-bit: 6.65M × $1.25 = **$8.31 / hr**
- **20% of requests** (200, ≈1.9M tokens) need high-quality reasoning → route to 70B MoE 8-bit: 1.9M × $1.00 = **$1.90 / hr**
- **10% of requests** (100, ≈0.95M tokens) are complex / multilingual → route to 70B dense FP16: 0.95M × $2.50 = **$2.38 / hr**

(Each request's output tokens are generated by the same model that processed its input. Routing output tokens to a *different* model would require an explicit cascade/composition stage — e.g., a generator plus a separate rewriter — which is a distinct architecture, not a free assumption.) The 4-bit GGUF tier (800 ms) is listed for completeness but is *not* routed to in this 70/20/10 split: at 800 ms it would miss the 500 ms interactive threshold, so the bulk goes to the 8-bit GPU tier (250 ms) instead — the same SLO constraint the §18.8 mini-case works out in full.

**Mixed-fleet hourly cost** = $8.31 + $1.90 + $2.38 = **$12.59 / hour** vs. $23.75 / hour for single-FP16 (all 9.5M tokens at $2.50).

**Monthly savings** ≈ ($23.75 − $12.59) × 730 hr ≈ **$8,147 / month** (≈ 47% reduction) with comparable quality because the 8-bit model meets quality thresholds for ≥90% of requests.

### 3.4. Latency check

The per-request latency is that of the model serving it. The weighted-average request latency is

$$
\bar{L} = \sum_i p_i \cdot L_i = 0.70 \times 250 + 0.20 \times 300 + 0.10 \times 120 \approx 247 \text{ ms/request}
$$

(no separate output-routing term — output rides with its requesting model), where $p_i$ is the fraction of requests routed to model $i$ and $L_i$ its per-request service latency. Acceptable for interactive chat (typical threshold: ≤500 ms).

**Scope note — the latency column is an illustrative routing-comparison input, not the canonical service time.** The 120/250/300/800 ms values are *illustrative per-request latencies for a short-prompt routing scenario* (the kind of request a router triages in milliseconds), used only to compare the four models against the interactive threshold (≤500 ms). They are **not** the ~8.6 s service time of the 9.5K-token canonical RAG request (Ch 17), which is a multi-second, capacity-side number that governs fleet sizing. The cost column, by contrast, *is* computed on the canonical 9.5K-token request (6.65M tokens for 700 requests). Read the two columns on their own bases: cost on the canonical request, latency as the illustrative routing input. A deployment benchmark (Ch 14) must supply the real per-model service times before either column is used for a production decision.

The latency and capacity must also reconcile with the canonical workload's KV residency (Chapter 17): routing 70% of requests to an 8-bit model on 1×H100 changes the per-host KV ceiling accordingly, and the fleet host count is set by the model each tier runs on. These are [ILLUSTRATIVE] pricing and latency figures for Q4 2026; the architect re-runs the same arithmetic with measured per-model cost/latency from a deployment benchmark (Chapter 14).

### 3.5. Consolidation vs. separation decision

- **Consolidate** when: workload profile overlap ≥70%, latency tolerance ≥300 ms, and cost differential >30%. *Verified*: our scenario sits exactly at the threshold — it consolidates ~70% of traffic to 8-bit (at the ≥70% boundary, not above it), saving ~$11.16/hr ($23.75 − $12.59, the §18.3.3 derived figure).
- **Keep separate** when: (a) security/classification policies require isolation, (b) workloads have bimodal latency needs (some ≤50 ms, others batch-tolerant), or (c) model versioning cadence differs (e.g., frequent fine-tuning on one family, stable other).

In our example, consolidation wins because the MoE and 8-bit models capture the same request classes at lower cost, and the FP16 tier handles the tail without contention. The FP16 tier has no separate reserve in this worked example: per §18.3.1 it shares the 640 GB pool — 140 GB of weights plus KV — and at the canonical 9.5K profile it cannot be a 2-GPU reserve, because a 2-GPU shard holds 160 GB − 140 GB = 20 GB of KV headroom against the 24.9 GB that one 9,500-token request needs (κ = 2.62 MB/token, Ch 17). Two reserved GPUs suffice only for the ~250-token support queries of §18.8, not for the canonical 9.5K request.

\Needspace{11\baselineskip}

## 4. Measurement

To operate a mixed fleet we measure four cross-cutting metrics:

| Metric | How to measure | Why it matters |
|-------|----------------|----------------|
| **Weighted average cost/token** | Σ(tokens_i × cost_i) / Σ(tokens_i) across all models | Directly tracks fleet economics; target under the §18.3.2 per-1M basis (e.g. < $2.50/1M for the FP16 tier) for competitive SaaS. |
| **Per-model throughput** | requests/sec per GPU / per CPU node | Detects saturation; informs capacity adds vs. routing tweaks. |
| **Routing accuracy** | % of requests served by the *intended* target model (not fallback) | Ensures the routing function R() is well-calibrated; low accuracy means feature gaps or cost model drift. |
| **Latency p95 per model** | p95 of token-level latency per model | Guarantee SLO per tier; fleet p95 must be computed from the combined routed-request latency distribution — per-model p95 values cannot in general be averaged (percentiles are not linearly composable). |

Instrumentation: add a middleware shim that logs `model_id, token_count, latency_ms, cost_cents` per request. Export to Prometheus + Grafana for real-time dashboards.

**Derived quantity example:** *Weighted cost rate* = (total monthly USD) / (total tokens processed). Start with the arithmetic above, then update daily as actual token counts and cloud prices shift.

## 5. Common Mistakes

1. **Treating quantization as free.** 4-bit/8-bit models reduce VRAM but increase CPU cycles and may lower quality on long-context tasks. Always measure the quality hit before routing en masse.
2. **One-size-fits-all routing.** A static rule ("always use 8-bit") fails when workload mix shifts (e.g., seasonal increase in multilingual queries that need FP16 precision). Use a dynamic router with feature-gate checks.
3. **Ignoring capital amortization.** FP16 on 8×H100 has high upfront cost; spreading that cost across a mixed fleet improves effective cost/token. Don't forget to annualize GPU capex in the per-token math.
4. **Over-provisioning the top tier.** Keeping a full FP16 GPU idle "just in case" is expensive. Keep just enough capacity for the tail (≈10% of peak rps) and route the rest.
5. **No fallthrough plan.** If the preferred model is at capacity, the router must have a next‑best alternative ready; otherwise requests time out or queue indefinitely.

A routing candidate is a validated deployment variant, not only a model family. A lower-precision variant can lower resource use, but its quality loss may appear selectively in reasoning, code, tool arguments or long contexts. Retries and longer generations can consume the apparent savings. The routing table therefore attaches quality and SLO evidence to the exact precision/backend combination, and the fallback preserves the task's acceptance conditions. A change to scales, excluded layers or execution kernels creates a new candidate for validation; it does not inherit the previous candidate's quality curve automatically.

## 6. Architecture Consequence

A mixed-model fleet changes the architecture in three ways:

1. **Router shim** (HTTP middleware or gRPC interceptor) sits between the user API and the model execution layer. It evaluates feature requirements, reads current capacity, and selects model_id.
2. **Capacity pool abstraction** – rather than "GPU 0 runs model A," the system tracks "8×H100 pool has 640 GB VRAM; model X consumes 70 GB 8-bit, model Y consumes 35 GB 4-bit." The pool manager auto‑balances placements.
3. **Billing/telemetry pipeline** – each request's cost and latency are tagged with model_id, enabling downstream dashboards and alerting (e.g., "cost per token rising above $0.0025 (on the §18.8 mini-case per-token basis) for 3 consecutive hours").

The fleet operator becomes a *cost‑latency steward* rather than a single-model optimizer.

## 7. What We Still Don't Know

- **Quality–cost curves for new quantizations.** As 3-bit and sub-4-bit GGUF models emerge, the trade-off surface shifts; we need systematic human evals + automatic benchmarks (MT‑Bench, FLAN) across families.
- **Optimal router policy for non‑stationary workloads.** Reinforcement‑learning–based routing that adapts α,β weights in real time is promising but underexplored in production fleets.
- **Cross-model distillation opportunities.** Can a 70B 4-bit model be distilled from a 70B FP16 teacher without quality loss, effectively lowering the cost floor? Empirical work needed.
- **Edge–cloud continuum effects.** When users bring their own 4-bit‑quantized local models (via Ollama, etc.), the fleet routing must account for hybrid inbound/outbound token flows.

## 8. End-of-Chapter Mini-Case: A Three-Tier Customer-Support Model Fleet

**Deploy a three‑tier fleet for a customer‑support chatbot.**

- **Tier 1 (4-bit GGUF):** Handles 80% of queries (FAQ, account lookup). Runs on edge nodes (AMD Ryzen 7950X, 64 GB RAM). Cost: $0.0002/token, latency ~600 ms.
- **Tier 2 (70B 8-bit dense):** Handles 15% of queries (order status, policy look-up). Runs on 1×H100. Cost: $0.0015/token, latency ~250 ms.
- **Tier 3 (70B FP16):** Handles 5% of queries (complex escalations, multilingual). Runs on 2 GPUs reserved. Cost: $0.003/token, latency ~120 ms.

**Arithmetic:** A small pilot deployment serving ~1,000 registered users at a modest, deliberately low volume — **5,000 tokens/hour** (each request averaging ~250 tokens gives roughly 20 requests/hour, a very light load chosen to make the per-token routing economics concrete rather than to model a busy fleet; the traffic rate is not what drives this arithmetic, the per-token volume is). Hourly tokens: ~4,500 in + 500 out = 5,000. *(Scope note: these tier per-token rates are illustrative scenario values that **differ from the §18.3.2 per-1M ledger** — they are not the ledger's $1.25 (8-bit) / $2.50 (FP16) / $0.15 (4-bit) per-1M rates converted, and the 4-bit tier's ~600 ms latency differs from the ledger's 800 ms. They are on a per-token basis, distinct from — and not directly comparable to — the per-1M-token ledger; the mini-case uses them to demonstrate the routing economics, and a real deployment would price from the §18.3.2 per-1M basis.)*

- Tier 1 processes 4,000 tokens/hr → $0.80
- Tier 2 processes 750 tokens/hr → $1.13
- Tier 3 processes 250 tokens/hr → $0.75
- **Total hourly cost: $2.68** → **$1,956 / month** (× 730 hr).

**Check the SLO before the cost claim.** If we had used a single 70B FP16 model: 5,000 tokens/hr × $0.003 = $15/hr → $10,950 / month (× 730 hr). The three-tier split looks like an $8,994 / month (≈82%) saving — but the SLO gates the cost claim, and here it fails. **Tier 1 (the cheapest, 4-bit GGUF on CPU, ~600 ms) serves 80% of queries, so the p95 per-request latency is ~600 ms, which violates the 500 ms SLO for the dominant tier.** The split saves cost by routing the bulk to a slow-but-cheap model — precisely the mean-vs-tail trap: the *average* latency looks fine, yet the majority tier misses the deadline. The $8,994 / month saving is therefore *conditional* on first making Tier 1 feasible.

**Recalculated cost after substituting a feasible Tier 1.** Replace the 4-bit GGUF (CPU, ~600 ms) with 8-bit quantization on a GPU (~250 ms, $0.0015/token — the same rate as Tier 2, which is also 8-bit on 1×H100). The 80% of queries now route at $0.0015/token:

- Tier 1 (8-bit on GPU) processes 4,000 tokens/hr → $6.00
- Tier 2 (70B 8-bit dense) processes 750 tokens/hr → $1.13
- Tier 3 (70B FP16) processes 250 tokens/hr → $0.75
- **Total hourly cost: $7.88** → **$5,752 / month** (× 730 hr).

The p95 is now ~250 ms (all tiers under 500 ms), so the SLO is met. The saving narrows from $8,994 / month (≈82%) to **$5,198 / month (≈47%)** — still a clear win, but the SLO-constrained figure, not the raw 82%, is the honest number. The correct order *within the cost/SLO gate* is: check the SLO, then size the cost (the capability filter still comes first, per Fig 18.1 and Table 18-1). The routing arithmetic shows the *economic* win; the SLO check is what keeps it honest, and it must come first *in the cost analysis*.

The key enabler was the router's feature gate: queries mentioning "multilingual" or "technical specification" were auto‑escalated to Tier 3; the rest flowed to Tier 1 or Tier 2 automatically.

![Fig 18.1 — Model-routing decision tree: capability filter → cost/SLO gate → fallthrough, with the specialist, general and fallback model families as leaves [ILLUSTRATIVE conceptual][DERIVED]](figures/fig-18-1801.png)

*The routing decision chain. A request first passes a capability filter (is there a specialized model that can serve it?), then a cost/SLO gate (route = f(cost, SLO)), and otherwise falls through to a general model. Each specialized family is a leaf the router can dispatch to. This converts the raw cost arithmetic above into the operational routing shape an architect operates daily.*


[^oct-ix-t7-openvino]: \raggedright OpenVINO documentation source, "Inference with OpenVINO GenAI," at revision `6f2492828618e1becda7d5ba6df6aa339e489e44` (examples of device targets for local GenAI inference): https://raw.githubusercontent.com/openvinotoolkit/openvino/6f2492828618e1becda7d5ba6df6aa339e489e44/docs/articles_en/openvino-workflow-generative/inference-with-genai.rst (retrieved 2026-10-28, Pacific time; outside the book's 2026-08-30 evidence cutoff; documentation inspection, not a tested combined environment).
[^oct-ix-t7-devices]: Intel Core Ultra X9 388H processor specifications list the Intel Arc B390 integrated GPU and the NPU as separate devices with their own compute figures (the GPU Peak TOPS (Int8) figure is quoted for the GPU alone), while graphics uses shared system memory: [https://www.intel.com/content/www/us/en/products/sku/245526/intel-core-ultra-x9-processor-388h-18m-cache-up-to-5-10-ghz/specifications.html](https://www.intel.com/content/www/us/en/products/sku/245526/intel-core-ultra-x9-processor-388h-18m-cache-up-to-5-10-ghz/specifications.html); OpenVINO documentation on managing iGPU memory usage: https://raw.githubusercontent.com/openvinotoolkit/openvino/0e15d2a38122e6787137fa91d96fe52c61615e66/docs/articles_en/openvino-workflow/running-inference/optimize-inference/managing-igpu-memory-usage.rst (documentation source pinned to revision `0e15d2a38122e6787137fa91d96fe52c61615e66`; both inspected 2026-10-28, Pacific time, outside the book's 2026-08-30 evidence cutoff; device specifications and documentation are not a combined runtime benchmark).
[^oct-ix-t7-configpath]: \raggedright vLLM XPU requirements at pinned revision `5df63a7203cdb9328d824a27b682e77c7b9928be`, which pins the framework/runtime stack (e.g. `torch==2.14.0`): https://raw.githubusercontent.com/vllm-project/vllm/5df63a7203cdb9328d824a27b682e77c7b9928be/requirements/xpu.txt (retrieved 2026-10-28; outside the book's 2026-08-30 evidence cutoff).
