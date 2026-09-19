# Chapter 4 — The Anatomy of an AI Workload

## The Architect's Question

After this chapter we should be able to take a vague deployment ask — "thousands of employees asking questions over internal documents" — and turn it into a *measurable workload* across six concrete dimensions. We will trace the arithmetic from user concurrency through traffic, token profile, latency, economics, and operational constraints, ending with a workload characterization that directly enables system architecture decisions. After this chapter, the question "which model should we choose?" can be answered with numbers, not intuition.

## 1. Concept

### The Six-Dimension Workload-Characterization Framework

A workload is defined by six orthogonal dimensions. Together they form a complete specification that — taken alone — determines model selection, system architecture, and economic feasibility. No single dimension is sufficient; the architect must characterize all six before committing to a design.

1. **Quality** — the fidelity, accuracy, and capability the workload demands of the model. Includes reasoning depth, tool-use requirements, modality (text‑only, multimodal, etc.), and any accuracy thresholds (e.g. >85% factual recall on internal Q&A). Quality is the *goal*; the other dimensions are the *constraints* within which quality must be delivered.

2. **Traffic** — the request rate the system must sustain, expressed in requests per second (rps) or queries per second, plus concurrency levels and burstiness. Traffic determines the compute and memory bandwidth required to keep the serving pipeline saturated without excessive queuing.

3. **Token profile** — the distribution of input length, output length, and context length per request. This is the workload's "shape" in token space: how many tokens arrive in the prompt, how many the model generates, and whether the prompt is dense (long context) or sparse. The token profile is the primary driver of memory (KV cache) and prefill cost.

4. **Latency** — the time budget for different stages of request processing. Typically split into *time-to-first-token* (TTFT), which encompasses retrieval and prefill, and *time-per-output-token* (TPOT), which governs decode length. Latency budgets feed directly into SLOs and serve as the key differentiator between serving configurations (e.g. continuous batching vs. discrete batching).

5. **Economic constraints** — the cost budget denominated in tokens per dollar, dollars per million tokens, or cost per request. This dimension translates traffic and token profile into a recurring cost line, and it determines whether a given infrastructure choice (single node vs. multi‑node, FP16 vs. FP8) is affordable at scale.

6. **Operational constraints** — availability, privacy, locality, and update frequency. Multi‑region deployment for fault tolerance. Data‑privacy requirements that force on‑prem or VPC‑local embedding models. Update frequency that dictates how often embeddings or model weights must be refreshed. These constraints often interact with traffic and economics to force architectural compromises.

The framework is deliberately dimensional: a workload that is "high‑quality, high‑traffic, long‑context, low‑latency, cost‑sensitive, private" is fundamentally different from "low‑quality, low‑traffic, short‑context, high‑latency, cost‑abundant, public," even if the raw text looks the same. The framework prevents the architect from optimizing one dimension at the expense of others — a common failure mode.

## 2. Mental Model

Think of the six dimensions as the axes of a six‑dimensional space in which every AI workload resides. A workload's position in this space is its *fingerprint*. When an architect says "we need a model for enterprise Q&A," that is only a descriptor of the quality dimension. To make the statement actionable, we must project the workload onto all six axes: *what quality level, how much traffic, what token profile, what latency SLO, what economic ceiling, what operational constraints?* The intersection of these projections is the workload point that drives every downstream decision — model selection, infrastructure sizing, serving configuration, and TCO.

The mental model is not a checklist; it is a *lens*. Looking through it, the architect sees which dimensions are tight (binding) and which are loose (permissive). Tight dimensions become the design drivers; loose dimensions offer optimization freedom. The goal is to identify the binding constraints so that resources are allocated where they matter most.

## 3. Worked Example

### Characterizing the Canonical Enterprise-Q&A RAG Workload

We now apply the six‑dimension framework to the **canonical enterprise‑Q&A RAG workload** used throughout this handbook. The canonical numbers are the fixed reference set for Part II; all arithmetic in this chapter traces to them (see the canonical-scenario provenance, Table 4-3).

#### Table 4-1 — Six-dimension workload characterization for the canonical RAG workload

| Dimension | Characteristic | Derivation / Source |
|:-------|:-----------------------------|:---------------------------------------------------------|
| **Quality** | Factual accuracy >85% on enterprise Q&A; reasoning via retrieval; no tool use beyond search API | [2°] DERIVED from enterprise benchmark suites (e.g. HotpotQA‑style retrieval Q&A) |
| **Traffic** | ~10 rps average; peaks ~40 rps | **Derivation**: 2,000 registered users × 5% concurrency = 100 concurrent users. By Little's Law (L = λW), with L = 100 and average request duration W ≈ 10 s, throughput λ = L/W = 100/10 ≈ 10 rps. Peaks ~40 rps arise when concurrency spikes to ~20% (400 users) with the same 10 s duration, yielding λ = 400/10 = 40 rps. |
| **Token profile** | Input: ~1,200 prompt + ~8,000 retrieved context ≈ 9,200 tokens; Output: ~300 tokens; total ≈ 9,500 tokens/request | [1P] canonical scenario (Ch 4, Table 4-3); tokenizer‑verified on the target model's tokenizer |
| **Latency** | TTFT budget 1.2 s (retrieval ~120 ms + prefill ~1.08 s); TPOT budget ~25 ms/token; p95 TTFT ≤ 2 s, p95 TPOT ≤ 35 ms | [2°] SLO-derived from user‑experience targets; retrieval latency from vector DB on same‑region deployment |
| **Economic constraints** | ~$1.20 per 1M input tokens, ~$2.00 per 1M output tokens on 8×H100 cloud instance; ~95,000 input tokens/s per dollar at 10 rps; infrastructure cost ≈ $20/hour for an 8×H100 host ($2.50/GPU-hr on-demand) | **illustrative 2026 cloud-price input** ($2.50/H100-GPU-hour, [ILLUSTRATIVE], not a market fact) → $20/hr per 8-GPU node; the $/1M-token and tokens/s-per-dollar values are derived from that input and the canonical workload |
| **Operational constraints** | Multi‑region deployment (active‑active for availability); embeddings refreshed daily from document store; privacy‑sensitive documents force on‑prem or VPC‑local retrieval; 99.9% availability SLA | [2°] DERIVED from typical enterprise IT policy and the canonical scenario's availability requirements |

#### Table 4-2 — Canonical workload characterization across six dimensions

| Metric | Value | Derivation / Source |
|---|---|---|
| Quality | >85% factual accuracy [2° DERIVED] | Enterprise Q&A benchmarks |
| Traffic | 10 rps avg; 40 rps peak [2° DERIVED] | 2,000 users × 5% concurrency = 100 concurrent; 100/10s = 10 rps; peaks at 20% concurrency → 40 rps |
| Token profile | 9,200 input tokens + 300 output tokens [1P canonical scenario (Ch 4, Table 4-3)] | 1,200 prompt + 8K context; 300‑token answer |
| Latency | TTFT 1.2 s (retrieval ~120 ms + prefill); TPOT ~25 ms/token [2° SLO] | User‑experience targets |
| Economics | $1.20/M input; $2.00/M output; ~$20/hr per 8×H100 host ($2.50/GPU-hr) | **illustrative 2026 price input** ($2.50/H100-GPU-hr, [ILLUSTRATIVE]); tokens/s per dollar derived from it |
| Operational | Multi‑region; daily embedding refresh; 99.9% availability [2° DERIVED] | Enterprise IT policy |

*(All figures trace to the canonical scenario (Ch 4, Table 4-3); none are independent measurement claims. Table 4-2 consolidates the six‑dimension characterization for quick reference.)*

> **Canonical Workload — the single reference set.** This box is the one authoritative set of numbers every chapter disciplines on. When a chapter states a workload parameter, it comes from here and nowhere else. The derived values (requests/s, tokens/s) are this box's arithmetic, recomputed in the chapter that needs them.
>
> | Field | Value |
> |---|---|
> | Employees / registered users | ~2,000 |
> | Active users at peak concurrency | ~100 (5% of 2,000) |
> | Average request rate | 10 rps |
> | Peak request rate | 40 rps |
> | Prompt / query | 1,200 tokens |
> | Retrieved context | 8,000 tokens |
> | Total input | 9,200 tokens |
> | Output | 300 tokens |
> | Model baseline | Dense 70B |
> | Weight precision | FP16 (2 B/param → ~140 GB) |
> | KV precision | FP16 (2.62 MB/token → ~24.1 GB @ 9.2K) |
> | TTFT SLO | 1.2 s (retrieval ~120 ms + prefill ~1.08 s); p95 ≤ 2 s |
> | TPOT SLO | 25 ms/token; p95 ≤ 35 ms |
> | Hardware | 8 × H100 (80 GB each, 640 GB) |
> | Compute price | $2.50/GPU-hr (illustrative 2026 input) → ~$20/hr per 8×H100 host |
> | Availability | 99.9% |
> | Monthly budget | ~$15,000 (illustrative ceiling) |
>
> *The two derived rates most chapters cite: at 10 rps the input demand is ~92,000 tokens/s (9,200 × 10) and output ~3,000 tokens/s (300 × 10); at 40 rps peak the input demand is ~368,000 tokens/s (9,200 × 40). These come from this box, not from a chapter re-deriving the mix differently.*

#### Table 4-3 — Canonical-scenario provenance (the single reference set)

Every quantity below is either an assumed workload input, a vendor fact, a modeled result, or a dated price snapshot. This is the authority for which is which; chapters refer back to it rather than restating provenance each time.

| Quantity | Value | Status |
|:--|:--|:--|
| Registered users | 2,000 | [ILLUSTRATIVE][ASSUMPTION] workload input |
| Active fraction | 5% (~100 concurrent) | [ILLUSTRATIVE][ASSUMPTION] |
| Average / peak traffic | 10 rps / 40 rps | [ILLUSTRATIVE][ASSUMPTION] |
| Input tokens | 9,200 (1,200 prompt + 8,000 retrieved) | [ILLUSTRATIVE][ASSUMPTION] |
| Output tokens | 300 | [ILLUSTRATIVE][ASSUMPTION] |
| Model parameters | 70B | [ILLUSTRATIVE][ASSUMPTION] reference model |
| Attention architecture | full-MHA reference model (K/V width = hidden_dim) | [ILLUSTRATIVE][ASSUMPTION] (a real 70B may use GQA, ~8x less KV; Ch 7) |
| KV per token (FP16, MHA) | 2.62 MB | [2°][DERIVED] from the general KV formula, MHA case |
| KV per token (FP8, vLLM ~54%) | 1.42 MB | [1P][FACT] vLLM-measured |
| H100 HBM per GPU | 80 GB | [1P][FACT] vendor |
| H100 BF16 peak | ~0.989 PFLOPS | [1P][FACT] vendor |
| Retrieval latency | 120 ms | [ILLUSTRATIVE][ASSUMPTION] |
| Prefill latency (TTFT) | 1.08 s | [2°][DERIVED]/benchmark assumption |
| Decode (TPOT) | 25 ms/token | [2°][DERIVED]/benchmark assumption |
| Host price (8xH100, on-demand) | ~$20/hr | [ILLUSTRATIVE] dated price snapshot |

#### Arithmetic Walk‑Through: From Users to Requests per Second

The step from "~2,000 registered users" to "~10 rps average" is the key connective tissue that makes the continuous scenario concrete. Here is the full derivation, traceable line by line:

1. **Concurrency**: a fraction $f$ of the $N$ registered users are actively in flight at any moment. With $f = 0.05$ and $N = 2{,}000$:

$$
C = f \cdot N = 0.05 \times 2{,}000 = 100 \text{ concurrent users}
$$

2. **Request completion time** (service time $W$): the average end‑to‑end time from request submission to answer delivery is ~10 s. This comprises retrieval (~120 ms) + prefill (~1.08 s for 9,200 tokens on H100) + decode of 300 tokens at ~25 ms/token (~7.5 s). The dominant term is decode, but the full pipeline sits at ~10 s.

3. **Throughput via Little's Law**: Little's Law, $L = \lambda W$, relates average concurrency $L$, average arrival rate $\lambda$, and average time in system $W$. Rearranging to solve for throughput:

$$
\lambda = \frac{L}{W} = \frac{100 \text{ concurrent}}{10 \text{ s}} = 10 \text{ rps}
$$

4. **Peak throughput**: if concurrency spikes to $f = 0.20$ (i.e. 400 users) and the per‑request duration stays $W = 10$ s, Little's Law gives

$$
\lambda_{\text{peak}} = \frac{f_{\text{peak}} \cdot N}{W} = \frac{0.20 \times 2{,}000}{10} = 40 \text{ rps}
$$

This matches the canonical peak of ~40 rps.

The derivation is explicit: the "~5% concurrently active" and "~10 rps average" are not independently asserted; they are linked by the 10 s average request duration. Change any one number and the others shift accordingly. This is the purpose of the exercise — not to produce a fixed set of gospel numbers, but to establish *how* the numbers connect, so the architect can recompute them when the requirement changes.

Before moving on, it is worth naming the four distinct quantities so they are not collapsed: **registered users** are the population; **concurrent users** are the activity state (those in flight at a moment); **arrival rate** (λ) is requests per unit time; and **service time** (W) is the end-to-end duration of a request. They are related by Little's Law, C = λW, but the architect must *estimate or measure* concurrency, arrival rate, and service time — none is a fixed property of the workload. The "5% active" and "10 s duration" are deliberately simple scenario assumptions ([ILLUSTRATIVE]), not externally verified facts; in a real engagement the architect replaces them with observed concurrency, measured latency, and a burst profile from telemetry. Getting this separation right is what turns traffic modeling from a guess into a reproducible arithmetic.

#### Token Profile in Detail

The canonical workload's token profile is input‑heavy, which has direct consequences for system design:

- **Per‑request input**: 1,200 tokens (enterprise query, possibly reformulated) + 8,000 tokens (retrieved context from vector DB) ≈ 9,200 tokens. The [1P] provenance traces to the canonical scenario (Ch 4, Table 4-3).
- **Per‑request output**: ~300 tokens (the generated answer, possibly with citations).
- **Input‑to‑output ratio**: 9,200 ÷ 300 ≈ 30× more input tokens than output tokens. This ratio is [2° DERIVED] from the canonical numbers and is the single biggest factor in why this workload is memory‑bound (KV cache) rather than decode‑bound.
- **At 10 rps**: input tokens/s = 9,200 ×10 = 92,000 tokens/s; output tokens/s = 300 ×10 = 3,000 tokens/s. At peak 40 rps, input spikes to ~368,000 tokens/s and output to ~12,000 tokens/s. These [2° DERIVED] numbers appear in Table 4-2.

The input‑heavy profile means that *prefill* (processing the prompt) dominates the latency and cost budget. A model that processes 8K tokens of context in under 1 s of prefill is essential; otherwise the TTFT budget of 1.2 s cannot be met. This is why the token profile is the primary architectural driver for this workload.

#### Latency from SLO

The latency dimension is specified through Service Level Objectives, which translate user‑experience goals into concrete time budgets:

- **TTFT (time-to-first-token)**: budget of 1.2 s, comprising retrieval (~120 ms for vector search and reranking on a local GPU) + prefill (~1.08 s for 9,200 tokens on an H100, assuming ~8.5K tokens/s prefill throughput). p95 TTFT must stay ≤ 2 s, allowing headroom for occasional cache misses or network jitter.
- **TPOT (time-per-output-token)**: budget of ~25 ms/token. A 300‑token answer therefore takes ~7.5 s of total decode time. p95 TPOT ≤ 35 ms/token provides headroom for batching variability.

These budgets are [2° DERIVED] from typical enterprise Q&A user expectations (sub‑2‑second feel) and from the hardware's published prefill/decode rates. They are the latency constraints that every subsequent architectural decision must respect.

#### Economic Constraints

The economic dimension translates the token profile and traffic into a cost structure:

- **Infrastructure**: A single host with 8 ×H100 GPUs (640 GB total GPU memory, 140 GB model FP16 weights fit with room for KV cache). Capital cost ≈ $20/hour on-demand ($2.50/GPU-hr), or ~$2,500/month reserved (illustrative) — the canonical box uses the on-demand basis.
- **Token pricing**: ~$1.20 per million input tokens, ~$2.00 per million output tokens on the same H100 instance (derived from cloud provider pricing as of 2026).
- **Throughput per dollar**: At 10 rps average, the system processes ~92,000 input tokens/s + ~3,000 output tokens/s. Dividing by the $20/hour infrastructure cost (≈ $0.0056 per second) yields ~16,500 input tokens/s per dollar and ~540 output tokens/s per dollar. These (derived — verify the input) numbers are the economics framing the canonical scenario. (Chapter 5 expresses the same economics on a GPU list-price basis as **tokens per dollar-hour**; see its unit-reconciliation note before cross-chapter comparison.)
- **Cost per request**: At 10 rps, each request carries ~9,500 tokens (9,200 input + 300 output). At the per‑million rates, cost per request ≈ ($1.20 ×9.2 + $2.00 ×0.3) / 1,000 ≈ $0.015 per request per inference cycle. At 40 rps peak, cost scales linearly.

The economic constraint is what makes the workload real: a 70B FP16 model on one host can serve the canonical workload at the target SLO, but scaling to higher traffic or longer contexts would require additional hosts, and the cost line must be re‑evaluated.


## 4. Measurement

For this chapter, measurement is about **quantifying the six dimensions** so the workload can be communicated definitively and used to drive architecture decisions. Three practical habits anchor the architect:

1. **Measure tokens, not words.** Run the model's own tokenizer on representative prompts from real traffic. The "4 chars ≈ 1 token" heuristic is for estimation only; real counts differ by language, formatting, code, and tokenizer version. Input token counts directly determine KV cache size and prefill time; output token counts determine decode bandwidth.

2. **Split input and output.** Measure both legs of the request separately (prompt tokens and generated tokens), because they land on different bottlenecks — input on memory/prefill, output on decode — and on different cost line items. An input‑heavy profile (like RAG's 30× ratio) means prefill dominates; an output‑heavy profile would dominate decode.

3. **Log the distribution, not just the mean.** A workload that averages 9.2 K input tokens but has a long tail (e.g. 32 K peak contexts) has a very different KV cache and latency profile than one with a tight distribution. Log percentiles (p90, p99) alongside the average.

These measurement habits are the token-layer answer to the book's recurring question, "what would I actually measure here?" — we measure token counts and their distribution, at the edge, before any architecture decision is made.

## 5. Common Mistakes

- **Treating "5% concurrency" as the throughput**. Concurrency is a snapshot of simultaneous users; throughput depends on how long each request takes. 100 concurrent users with 200 s per request yield 0.5 rps, not 10 rps. The binding connection is through request duration (Little's Law). Catch this by always asking "how long is each request in system?" before quoting a concurrency-derived throughput.
- **Assuming "one token ≈ one word"**. Enterprise Q&A prompts with code snippets, JSON payloads, or technical terminology can run 2–5× the naive token estimate, silently inflating KV cache and cost.
- **Ignoring the input–output asymmetry**. An input-heavy workload like RAG is memory-bound (prefill/KV cache), while an output-heavy workload is decode-bound. Optimizing decode throughput on an input-heavy workload moves the needle negligibly; the real win is prefill reduction or KV cache reuse.
- **Quoting context window as free capacity**. The 128 K token window is an upper bound; using 9.2 K of it still costs for the full 9.2 K in memory and prefill time. Keeping context shorter than necessary is not "free."
- **Overlooking operational constraints**. Multi–region deployment adds replication cost; privacy requirements may force a more expensive on-prem embedding model. These are often the true binding constraints, not the per-token price.

## 6. Architecture Consequence

The six‑dimension characterization directly dictates the architectural path for the canonical enterprise‑Q&A RAG workload:

![Fig 4.1 — Six-dimension workload characterization mapped to architectural decisions. [ILLUSTRATIVE conceptual]](figures/fig-04-0401.png)

*The six workload dimensions and the architectural decision each one drives: Quality → model size/type; Traffic → concurrency & batching strategy; Token profile → KV cache size & prefill demand; Latency → TTFT/TPOT targets & batch window; Economic → host count & cost ceiling; Operational → multi-region vs. single-region deployment.*

<!-- Figure spec: mechanism-first diagram; one labeled axis per dimension, each arrow ending at its architectural consequence. -->

- **Model selection**: A 70B FP16 dense model (140 GB weights) fits on a single host with 8 ×H100 (640 GB GPU memory). The model is large enough to answer factual enterprise questions without fine‑tuning, but the 140 GB footprint means KV cache for 9.2 K context adds ~20–30 GB of GPU memory per request at peak, leaving headroom but not abundance.
- **Serving configuration**: One host is the baseline. Continuous batching (e.g. vLLM) is nearly mandatory to achieve the 1.2 s TTFT budget under 10 rps input‑heavy traffic; without it, prefill of 9.2 K tokens per request would serialize and push TTFT well above 2 s. The input‑heavy token profile (30× more input than output) makes continuous batching especially effective, as many requests share the same prefix from retrieved context.
- **Memory planning**: KV cache for 9.2 K context on the canonical model — a 70B **full-MHA reference model** (every query head has its own K,V, so K/V width = hidden_dim = 8192) — is 2 × layers × hidden × bytes = 2,621,440 B ≈ 2.62 MB/token (Chapter 7), giving ≈9,200 ×2.62 MB ≈ 24.1 GB of initial KV per request. This is the MHA upper-bound baseline; a GQA model (8 KV heads, d_head=128) would carry only ~0.33 MB/token, ~8× less (Ch 7). At 10 concurrent full-context requests the MHA figure is ~241 GB of KV on top of the 140 GB weights — pressing against the 640 GB pool well before concurrency reaches 100. The architecture must therefore limit concurrency, quantize KV (FP8 → ~1.42 MB/token, ~13.4 GB/request at the 9.5K max), or use a GQA architecture. This is the same KV-residency discipline developed fully in Chapters 7 and 17.
- **Economic feasibility**: At ~$3.50/hour per host and ~$0.015 per request, the TCO is driven by the 9.2 K input tokens per request. If the input token count could be reduced to 2 K (e.g. via better retrieval or query expansion), cost per request drops to ~$0.004, and the same traffic fits within a much lower budget. This is the lever the architect pulls when TCO is the binding constraint.
- **Operational topology**: Multi‑region deployment (active‑active) provides availability but doubles the infrastructure cost. If the 99.9% availability SLA is non‑negotiable, the architecture must absorb the 2× cost. If it is negotiable, a single-region with graceful-degrading fallback may suffice. The operational constraint thus directly sets the economic floor.

## 7. What We Still Don't Know

- **Tokenizer exactness for technical domains**: While the "one token ≈ 4 characters" rule of thumb is convenient, enterprise Q&A prompts may contain code, JSON, or domain‑specific terminology that tokenizes differently. The exact per‑token count for a given prompt distribution is (to be verified) and would require running the model's tokenizer on a representative sample of real user queries.
- **KV cache scaling with longer contexts**: The canonical scenario uses ~9.2 K input tokens. If retrieval quality degrades and context lengths grow to 32 K or 128 K, the KV cache memory per request grows linearly, and the single‑host FP16 architecture would no longer suffice without quantization or model parallelism. The breakpoint is (to be verified) and workload‑dependent.
- **Impact of reranking on latency**: The TTFT budget assumes retrieval (~120 ms) plus prefill. If a late‑stage reranker is added to the pipeline, the retrieval component's latency may increase, eating into the TTFT budget and potentially requiring a wider SLO margin or a faster retriever. The magnitude of this effect is (a hypothesis) and should be measured before production deployment.
- **Economic durability at scale**: The tokens‑per‑dollar numbers are derived from 2026 on‑demand H100 pricing. Spot instances, reserved contracts, or custom cloud agreements could shift the economics significantly. The durability of the economic model across provider changes is (a hypothesis).

## 8. End-of-Chapter Mini-Case

An architect is brought into the early design of an internal Q&A platform. The stakeholder says: "We have thousands of employees who want to ask questions over our internal documents. We need it to be accurate and fast, but we don't know how many thousands or how fast is fast enough." Before any architecture can be defended, the architect does the workload characterization that this chapter walks through.

From the token layer alone (as we did in Ch. 4), the architect can already establish: the unit is tokens; the request shape will be prompt + retrieved context + output; the workload is input‑heavy; and the first number to lock down is tokens‑per‑request, because every downstream decision (which model fits, how much memory, what latency is possible) is priced against it. Using the canonical scenario as a starting point — ~2,000 registered users, ~5% concurrency, ~10 rps, ~9.2 K input + 300 output tokens — the architect projects the enterprise's actual headcount. If the company has 5,000 employees and expects 10% concurrent activity during peak Q&A periods (after a policy rollout), the concurrency rises to 500 users. With the same ~10 s request duration, throughput climbs to ~50 rps, which would require ~5 hosts of 8×H100 each, at a monthly infrastructure cost of ~$12,500. The architect can now speak the system's currency — tokens, rps, dollars per million — and can engage the rest of the team on model selection, serving configuration, and TCO with concrete numbers rather than vague assurances. The specific sizing — turning "thousands of employees" into a characterized workload across all six dimensions — is the payoff of Ch. 4's framework, and it is the prerequisite for every architecture question that follows.