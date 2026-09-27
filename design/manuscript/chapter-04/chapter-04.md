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

The six dimensions are best read as the axes of a six‑dimensional space in which every AI workload resides. A workload's position in this space is its *fingerprint*. When an architect says "we need a model for enterprise Q&A," that is only a descriptor of the quality dimension. To make the statement actionable, we must project the workload onto all six axes: *what quality level, how much traffic, what token profile, what latency SLO, what economic ceiling, what operational constraints?* The intersection of these projections is the workload point that drives every downstream decision — model selection, infrastructure sizing, serving configuration, and TCO.

The mental model is not a checklist; it is a *lens*. Looking through it, the architect sees which dimensions are tight (binding) and which are loose (permissive). Tight dimensions become the design drivers; loose dimensions offer optimization freedom. The goal is to identify the binding constraints so that resources are allocated where they matter most.

## 3. Worked Example

### Characterizing the Canonical Enterprise-Q&A RAG Workload

RAG is retrieval-augmented generation: the system retrieves relevant passages from a document store and prepends them to the user's question as context, so the model answers from evidence rather than memory. The canonical workload below is the book's running example of such a system (the Preface defines the term; this is where it becomes a quantified workload).

We now apply the six‑dimension framework to the **canonical enterprise‑Q&A RAG workload** used throughout this handbook. The canonical numbers are the fixed reference set for Part II; all arithmetic in this chapter traces to them (see the canonical-scenario provenance, Table 4-3).

#### Table 4-1 — Six-dimension workload characterization for the canonical RAG workload

| Dimension | Characteristic | Derivation / Source |
|:-------|:-----------------------------|:---------------------------------------------------------|
| **Quality** | Factual accuracy >85% on enterprise Q&A; reasoning via retrieval; no tool use beyond search API | [2°] DERIVED from enterprise benchmark suites (e.g. HotpotQA‑style retrieval Q&A) |
| **Traffic** | ~10 rps average; peaks ~40 rps | **Derivation**: 2,000 registered users × 5% concurrency = 100 concurrent users. By Little's Law (L = λW), with L = 100 and average request duration W ≈ 10 s, throughput λ = L/W = 100/10 ≈ 10 rps. Peaks ~40 rps arise when concurrency spikes to ~20% (400 users) with the same 10 s duration, yielding λ = 400/10 = 40 rps. |
| **Token profile** | Input: ~1,200 prompt + ~8,000 retrieved context ≈ 9,200 tokens; Output: ~300 tokens; total ≈ 9,500 tokens/request | [1P] canonical scenario (Ch 4, Table 4-3); tokenizer‑verified on the target model's tokenizer |
| **Latency** | TTFT budget 1.2 s (retrieval ~120 ms + prefill ~1.08 s); TPOT budget ~25 ms/token; p95 TTFT ≤ 2 s, p95 TPOT ≤ 35 ms | [2°] SLO-derived from user‑experience targets; retrieval latency from vector DB on same‑region deployment |
| **Economic constraints** | ~$1.20 per 1M input tokens, ~$2.00 per 1M output tokens on 8×H100 cloud instance; ~16.5M input tokens per dollar (and ~540K output tokens per dollar) at 10 rps; infrastructure cost ≈ $20/hour for an 8×H100 host ($2.50/GPU-hr on-demand) | **illustrative 2026 cloud-price input** ($2.50/H100-GPU-hour, [ILLUSTRATIVE], not a market fact) → $20/hr per 8-GPU node; the $/1M-token and tokens-per-dollar values are derived from that input and the canonical workload |
| **Operational constraints** | Multi‑region deployment (active‑active for availability); embeddings refreshed daily from document store; privacy‑sensitive documents force on‑prem or VPC‑local retrieval; 99.9% availability SLA | [2°] DERIVED from typical enterprise IT policy and the canonical scenario's availability requirements |

#### Table 4-2 — Canonical workload characterization across six dimensions

| Metric | Value | Derivation / Source |
|---|---|---|
| Quality | >85% factual accuracy [ILLUSTRATIVE][DERIVED] | Enterprise Q&A benchmarks |
| Traffic | 10 rps avg; 40 rps peak [ILLUSTRATIVE][DERIVED] | 2,000 users × 5% concurrency = 100 concurrent; 100/10s = 10 rps; peaks at 20% concurrency → 40 rps |
| Token profile | 9,200 input tokens + 300 output tokens [canonical scenario (Ch 4, Table 4-3)] | 1,200 prompt + 8K context; 300‑token answer |
| Latency | TTFT 1.2 s (retrieval ~120 ms + prefill); TPOT ~25 ms/token [2° SLO] | User‑experience targets |
| Economics | $1.20/M input; $2.00/M output; ~$20/hr per 8×H100 host ($2.50/GPU-hr) | **illustrative 2026 price input** ($2.50/H100-GPU-hr, [ILLUSTRATIVE]); tokens/s per dollar derived from it |
| Operational | Multi‑region; daily embedding refresh; 99.9% availability [ILLUSTRATIVE][DERIVED] | Enterprise IT policy |

*(All figures trace to the canonical scenario (Ch 4, Table 4-3); none are independent measurement claims. Table 4-2 consolidates the six‑dimension characterization for quick reference.)*

> **Canonical Workload — the single reference set.** This box is the one authoritative set of numbers every chapter disciplines on. When a chapter states a workload parameter, it comes from here and nowhere else. The derived values (requests/s, tokens/s) are this box's arithmetic, recomputed in the chapter that needs them.
>
> | Field | Value |
> |---|---|
> | Employees / registered users | ~2,000 |
> | Concurrent users (typical) | ~100 (5% of 2,000) |
> | Concurrent users (peak)     | ~400 (20% of 2,000) |
> | Mean request service time (planning) | ~10 s  *[1P/ASSUMPTION — planning round; retrieval ~120ms + prefill ~1.08s + decode ~7.5s rounded to comfortable planning figure]* |
> | Average arrival rate | ~10 rps *[2° DERIVED — Little's Law 100/10]* |
> | Peak arrival rate    | ~40 rps *[2° DERIVED — Little's Law 400/10]* |
> | Prompt / query | 1,200 tokens |
> | Retrieved context | 8,000 tokens |
> | Total input | 9,200 tokens |
> | Output | 300 tokens |
> | Model baseline | Dense 70B |
> | Weight precision | FP16 (2 B/param → ~140 GB) |
> | KV precision | FP16 (2.62 MB/token → ~24.1 GB @ 9.2K) |
> | TTFT SLO | 1.2 s (retrieval ~120 ms + prefill ~1.08 s); p95 ≤ 2 s |
> | TPOT SLO | 25 ms/token; p95 ≤ 35 ms |
> | Hardware | 8×H100 (80 GB each, 640 GB) |
> | Compute price | $2.50/GPU-hr (illustrative 2026 input) → ~$20/hr per 8×H100 host |
> | Availability | 99.9% |
> | Monthly budget | ~$15,000 (illustrative *per-host* ceiling: one 8×H100 host at ~$20/hr × 730 hr ≈ $14.6K/mo. Note this is a **single host**, not the whole workload — meeting the canonical ~10 rps average / ~40 rps peak needs ~5–20 hosts, so the workload's real monthly spend is ~$75K–$350K/mo (Ch 16); the budget box is a per-host ceiling, not the workload ceiling) |
>
> *The two derived rates most chapters cite: at 10 rps the input demand is ~92,000 tokens/s (9,200 × 10) and output ~3,000 tokens/s (300 × 10); at 40 rps peak the input demand is ~368,000 tokens/s (9,200 × 40). These come from this box, not from a chapter re-deriving the mix differently.*

#### Table 4-3 — Canonical-scenario provenance (the single reference set)

Every quantity below is either an assumed workload input, a vendor fact, a modeled result, or a dated price snapshot. This is the authority for which is which; chapters refer back to it rather than restating provenance each time.

> **CANONICAL TEACHING MODEL — deliberately conservative full-MHA baseline.** The 70B dense **full-MHA** model (every query attends to every key) is a *teaching/reference* model, not a representative 2026 production 70B architecture. Modern production serving candidates use GQA/MQA and sparse attention, which shrink the KV constant several-fold (Ch 7); the ~2.62 MB/token figure is an upper bound for pedagogical clarity, and the frontier appendix (Appendix A) is the deliberate relaxation — not a correction — of this deliberately pessimistic baseline. Treating it as a property of *70B models in general* understates 2026 production KV efficiency.

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
| H100 BF16 peak (dense, no sparsity) | ~0.989 PFLOPS | [1P][FACT] vendor |
| Retrieval latency | 120 ms | [ILLUSTRATIVE][ASSUMPTION] |
| Prefill latency (TTFT) | 1.08 s | [2°][DERIVED]/benchmark assumption |
| Decode (TPOT) | 25 ms/token | [2°][DERIVED]/benchmark assumption |
| Host price (8×H100, on-demand) | ~$20/hr | [ILLUSTRATIVE] dated price snapshot |

#### Arithmetic Walk‑Through: From Users to Requests per Second

The step from "~2,000 registered users" to "~10 rps average" is the key connective tissue that makes the continuous scenario concrete. Here is the full derivation, traceable line by line:

1. **Concurrency**: a fraction $f$ of the $N$ registered users are actively in flight at any moment. With $f = 0.05$ and $N = 2{,}000$:

$$
C = f \cdot N = 0.05 \times 2{,}000 = 100 \text{ concurrent users}
$$

2. **Request completion time** (service time $W$): the average end‑to‑end time from request submission to answer delivery. We deliberately keep TWO named values, and the distinction matters: a **planning round number of ~10 s** (retrieval ~120 ms + prefill ~1.08 s + decode ~7.5 s, rounded up to a comfortable planning figure) versus the **derived model-execution service time of ~8.6 s** (prefill 1.08 s + decode 7.5 s, without the retrieval/plumbing term) that the later fleet chapters use in Little's-law sizing. The two differ by the retrieval/pipelineroom and by rounding; they are not a numerical contradiction. Whichever we use, we must use it consistently — the canonical ledger pins the fleet-sizing service time at ~8.6 s (Chapter 8), and the ~10 s figure is the coarser planning-round headline.

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

Before moving on, it is worth naming the four distinct quantities so they are not collapsed: **registered users** are the population; **concurrent users** are the activity state (those in flight at a moment); **arrival rate** (λ) is requests per unit time; and **service time** (W) is the end-to-end duration of a request. They are related by Little's Law, C = λW, but the architect must *estimate or measure* concurrency, arrival rate, and service time — none is a fixed property of the workload. Two further separations matter for KV planning and are easy to collapse, so we hold them apart here too:

**"Concurrent users" here means *active users*, not simultaneous in-flight inference requests.** The 5% figure gives ~100 active users in the modeled activity window — people who are using the tool over the window — not 100 requests that are all mid-execution at the same instant. The in-flight *request* concurrency is a different quantity, computed from Little's Law with the derived service time W ≈ 8.6 s. The two operating points are distinct rows, not one figure reconciled by an unstated multiplier:

| Operating point | Active users (population) | Arrival rate λ | In-flight requests (λ·W, W≈8.6 s) |
|---|---|---|---|
| Average | 100 (5% × 2,000) | ~10 rps | ~86 |
| Peak | 400 (20% × 2,000) | ~40 rps | ~344 |

The reason these columns differ in kind is that **active-user population** and **request occupancy** are different state variables. Active users is a *population* measure — how many people engaged the tool over the modeled window. Request occupancy is an *instantaneous* Little's-law quantity — how many requests are resident in the serving system at a moment. They are related only through the arrival rate and service time, not through a per-user request multiplicity. So at the average operating point the population (~100) and the occupancy (~86) happen to be close, while at the peak they differ (400 vs 344); neither gap needs a "one user issues several requests" reconciliation, and we do not claim one. Whenever the book says "concurrent users," read "active users in the modeled activity window"; whenever it needs the request-level occupancy that a host's KV budget must absorb, use the Little's-law λ·W figure for that specific operating point.

**The ~40 rps peak is assumed sustained over the provisioning burst interval** — long enough for Little's Law and service-time occupancy to reach the modeled steady state (seconds of sustained 40 rps), not a one-request 40-rps spike. A one-second spike would not populate the queue to λ·W; the fleet sizing deliberately treats 40 rps as the sustained burst the system must absorb. A load generator reproducing this workload should emit the same sustained arrival process, not merely target the same average QPS.

- **Concurrent *users* ≠ concurrent *requests*.** "100 concurrent users" is a statement about the *population's activity*, not about how many requests are in flight at the scheduler at any instant. The two are different state variables, and they need not be close — at the average operating point they happen to be (~100 vs ~86), at the peak they differ (~400 vs ~344).
- **Requests *in flight* ≠ KV-resident sequences.** A request in the queue, or one whose prefill is not yet admitted, is "in flight" from the user's perspective but does not yet hold a KV slot. In-flight concurrency upper-bounds the KV-concurrency the system must serve, but the KV budget is sized by the number of *resident active sequences* — which is what the concurrency ceilings in Ch 17 count. Little's Law gives the in-flight number; the KV budget is a separate, residency-side quantity obtained by multiplying the resident sequence count by per-token KV. Keeping these three apart (in flight vs resident vs per-token KV) is what prevents the "100 users → 100 KV slots" leap.

The "5% active" and "10 s duration" are deliberately simple scenario assumptions ([ILLUSTRATIVE]), not externally verified facts; in a real engagement the architect replaces them with observed concurrency, measured latency, and a burst profile from telemetry. Getting this separation right is what turns traffic modeling from a guess into a reproducible arithmetic.

#### Token Profile in Detail

The canonical workload's token profile is input‑heavy, which has direct consequences for system design:

- **Per‑request input**: 1,200 tokens (enterprise query, possibly reformulated) + 8,000 tokens (retrieved context from vector DB) ≈ 9,200 tokens. The [1P] provenance traces to the canonical scenario (Ch 4, Table 4-3).
- **Per‑request output**: ~300 tokens (the generated answer, possibly with citations).
- **Input‑to‑output ratio**: 9,200 ÷ 300 ≈ 30× more input tokens than output tokens. This ratio is [ILLUSTRATIVE][DERIVED] from the canonical numbers and is the single biggest factor in why this workload is memory‑bound (KV cache) rather than decode‑bound.
- **At 10 rps**: input tokens/s = 9,200 ×10 = 92,000 tokens/s; output tokens/s = 300 ×10 = 3,000 tokens/s. At peak 40 rps, input spikes to ~368,000 tokens/s and output to ~12,000 tokens/s. These [ILLUSTRATIVE][DERIVED] numbers appear in Table 4-2.

The input‑heavy profile means that *prefill* (processing the prompt) dominates the latency and cost budget. A model that processes 8K tokens of context in under 1 s of prefill is essential; otherwise the TTFT budget of 1.2 s cannot be met. This is why the token profile is the primary architectural driver for this workload.

#### Latency from SLO

The latency dimension is specified through Service Level Objectives, which translate user‑experience goals into concrete time budgets:

- **TTFT (time-to-first-token)**: budget of 1.2 s, comprising retrieval (~120 ms for vector search and reranking on a local GPU) + prefill (~1.08 s for 9,200 tokens across the 8×H100 canonical host, ≈8.5K tokens/s prefill — below the host's ~19,800 tok/s ideal and far above what a single H100 alone could sustain, per Ch 2 and Ch 8). p95 TTFT must stay ≤ 2 s, allowing headroom for occasional cache misses or network jitter.
- **TPOT (time-per-output-token)**: budget of ~25 ms/token. A 300‑token answer therefore takes ~7.5 s of total decode time. p95 TPOT ≤ 35 ms/token provides headroom for batching variability.

These budgets are [ILLUSTRATIVE][DERIVED] from typical enterprise Q&A user expectations (sub‑2‑second feel) and from the hardware's published prefill/decode rates. They are the latency constraints that every subsequent architectural decision must respect.

#### Economic Constraints

The economic dimension translates the token profile and traffic into a cost structure:

- **Infrastructure**: A single host with 8×H100 GPUs (640 GB total GPU memory, 140 GB model FP16 weights fit with room for KV cache). Capital cost ≈ $20/hour on-demand ($2.50/GPU-hr), or ~$2,500/month reserved (illustrative committed-use discount; a ~83% discount on H100 on-demand is unusually deep and differs from the on-demand basis the canonical box uses) — the canonical box uses the on-demand basis.
- **Token pricing**: ~$1.20 per million input tokens, ~$2.00 per million output tokens on the same H100 instance (derived from cloud provider pricing as of 2026).
- **Throughput per dollar**: At 10 rps average, the system processes ~92,000 input tokens/s + ~3,000 output tokens/s. Dividing the token rate by the $20/hour infrastructure cost (≈ $0.00556 per second) gives ~92,000 / 0.00556 ≈ **16.5 million input tokens per dollar** and ~3,000 / 0.00556 ≈ **540,000 output tokens per dollar**. (Chapter 5 expresses the same economics on a GPU list-price basis as **tokens per dollar-hour**; see its unit-reconciliation note before cross-chapter comparison.)
- **Cost per request**: At 10 rps, each request carries ~9,500 tokens (9,200 input + 300 output). At the per‑million rates, cost per request ≈ ($1.20 × 9.2 + $2.00 × 0.3) / 1,000 ≈ $0.01164 ≈ **$0.012 per request** per inference cycle. At 40 rps peak, cost scales linearly. **Basis note — two different cost bases, not interchangeable.** The $0.012 figure is derived from *per-token market/API list prices* ($1.20/M in, $2.00/M out); it is a cloud-provider price a customer would pay per request on a hosted API. It is *not* the fleet owner's marginal infrastructure cost, which is ~$20/hr ÷ 10 rps ≈ **~$0.00056 per request** (roughly 21× lower) — the owned-fleet cost is nearly all fixed capex/opex and barely scales per request. Keep these separate: use the per-token price when reasoning about a *hosted/API* cost model, and the $/hr infrastructure cost when reasoning about an *owned fleet*. The two are juxtaposed later in §4.7 only to show the hosted-API pricing basis, not as an owned-fleet marginal cost.

The economic constraint is what makes the workload real: a 70B FP16 model on one host *meets the per‑request latency SLO* (TTFT/TPOT) — but the *capacity* question, how many hosts absorb the ~10 rps average / ~40 rps peak arrival, is a separate computation. As Chapters 8 and 16–17 show, a single 8×H100 host holds ~17.5 KV‑resident requests (the conservative integer floor is 17), so it cannot carry the ~40 rps peak (~344 in flight); the canonical workload needs on the order of ~5 hosts at the average and ~20 hosts at the peak. Scaling to higher traffic or longer contexts pushes the host count further, and the cost line must be re‑evaluated.

**Cost-basis distinction (do not confuse the two):**

| Basis | Derivation | Number |
|---|---|---|
| Cloud-provider list price (what a customer pays Managed-API-by-token) | [ILLUSTRATIVE] 2026 cloud list snapshot | ~$1.20 / 1M input tokens, ~$2.00 / 1M output tokens |
| Self-host cost per million tokens (infrastructure $20/hr divided by canonical 92K inp tok/s + 3K out tok/s) | [$20/hr] / [92K inp tok/s + 3K out/s] converted to per-million-tokens via 3600 | ~$0.061 / 1M input tokens (i.e. ~16.5M tokens per dollar), ~$1.85 / 1M output tokens |

These are NOT redundant measures of the same effective cost — they are what-the-customer-pays-the-cloud (basis A) vs what-the-host-cost-spread-across-tokens-costs (basis B). Quoting both without labelling the basis confuses readers into treating basis B as if it were basis A.


## 4. Measurement

For this chapter, measurement is about **quantifying the six dimensions** so the workload can be communicated definitively and used to drive architecture decisions. The token-counting habits of Ch 1 §4 apply unchanged (run the model's own tokenizer, split input from output, log the distribution not just the mean) — rather than restate them, the three things the *six-dimension* view adds are:

1. **Quantify each dimension with a number, not a label.** For the six dimensions (workload type, token mix, concurrency, latency, memory, economics), attach a concrete measured or derived figure. "RAG" is not a load; "1.2K prompt + 8K retrieved, 300 out, 40 rps peak, p95 TTFT ≤ 2 s" is.
2. **Tie the token split to the bottleneck it drives.** An input-heavy profile (like RAG's 30× ratio) means prefill compute and KV-capacity pressure dominate; an output-heavy profile would dominate decode. State which side dominates, because it decides where the money and the architecture effort go (Ch 8).
3. **Record the peak and the tail, not just the average.** A workload that averages 9.2K input but has a long tail (e.g. 32K peak contexts) sizes the fleet very differently. Log percentiles (p90, p99) alongside the average and size against the peak.

These habits answer the book's recurring question, "what would I actually measure here?" — and they let the six dimensions be stated as numbers an architecture decision can be defended on.

## 5. Common Mistakes

- **Treating "5% concurrency" as the throughput**. Concurrency is a snapshot of simultaneous users; throughput depends on how long each request takes. 100 concurrent users with 200 s per request yield 0.5 rps, not 10 rps. The binding connection is through request duration (Little's Law). Catch this by always asking "how long is each request in system?" before quoting a concurrency-derived throughput.
- **Assuming "one token ≈ one word"**. Enterprise Q&A prompts with code snippets, JSON payloads, or technical terminology can run 2–5× the naive token estimate, silently inflating KV cache and cost.
- **Ignoring the input–output asymmetry**. An input-heavy workload like RAG tends to increase *prefill compute* and *KV-capacity* pressure — it does not by itself make the system "memory-bandwidth-bound." In the canonical model, prefill is **compute-bound** under the analytical roofline, while long input raises **KV residency**, which constrains sustainable concurrency (a capacity constraint, distinct from bandwidth). An output-heavy workload is **decode-bound** (bandwidth/runtime per generated token). Optimizing decode throughput on an input-heavy workload moves the needle negligibly; the real win is prefill reduction, prefix/KV reuse, or increasing effective carrying capacity.
- **Quoting context window as free capacity**. The 128 K token window is an upper bound; using 9.2 K of it still costs for the full 9.2 K in memory and prefill time. Keeping context shorter than necessary is not "free."
- **Overlooking operational constraints**. Multi–region deployment adds replication cost; privacy requirements may force a more expensive on-prem embedding model. These are often the true binding constraints, not the per-token price.

## 6. Architecture Consequence

The six‑dimension characterization directly dictates the architectural path for the canonical enterprise‑Q&A RAG workload:

![Fig 4.1 — Six-dimension workload characterization mapped to architectural decisions. Each arrow means the dimension *constrains/informs* the corresponding architectural choice — it is a heuristic influence, not a deterministic one-to-one mapping. [ILLUSTRATIVE conceptual]](figures/fig-04-0401.png)

*The six workload dimensions and the architectural decision each one drives: Quality → model size/type; Traffic → concurrency & batching strategy; Token profile → KV cache size & prefill demand; Latency → TTFT/TPOT targets & batch window; Economic → host count & cost ceiling; Operational → multi-region vs. single-region deployment.*

<!-- Figure spec: mechanism-first diagram; one labeled axis per dimension, each arrow ending at its architectural consequence. -->

- **Model selection**: A 70B FP16 dense model (140 GB weights) fits on a single host with 8×H100 (640 GB GPU memory). The model is large enough to answer factual enterprise questions without fine‑tuning, but the 140 GB footprint means KV cache for 9.2 K context adds ~20–30 GB of GPU memory per request at peak, leaving headroom but not abundance.
- **Serving configuration**: One host is the baseline. Continuous batching (e.g. vLLM) is nearly mandatory to achieve the 1.2 s TTFT budget under 10 rps input‑heavy traffic; without it, prefill of 9.2 K tokens per request would serialize and push TTFT well above 2 s. The input‑heavy token profile (30× more input than output) makes continuous batching especially effective, as many requests share the same prefix from retrieved context.
- **Memory planning**: KV cache for 9.2 K context on the canonical model — a 70B **full-MHA reference model** (every query head has its own K,V, so K/V width = hidden_dim = 8192) — is 2 × layers × hidden × bytes = 2,621,440 B ≈ 2.62 MB/token (Chapter 7), giving ≈9,200 ×2.62 MB ≈ 24.1 GB of initial KV per request. This is the MHA upper-bound baseline; a GQA model (8 KV heads, d_head=128) would carry only ~0.33 MB/token, ~8× less (Ch 7). At 10 concurrent full-context requests the MHA figure is ~241 GB of KV on top of the 140 GB weights — pressing against the 640 GB pool well before concurrency reaches 100. The architecture must therefore limit concurrency, quantize KV (FP8 → ~1.42 MB/token, ~13.4 GB/request at the 9.5K max), or use a GQA architecture. This is the same KV-residency discipline developed fully in Chapters 7 and 17.
- **Economic feasibility**: At ~$20/hour per 8×H100 host and ~$0.012 per request (from $1.20/M input × 9.2 K + $2.00/M output × 0.3 K), the TCO is driven by the 9.2 K input tokens per request. If the input token count could be reduced to 2 K (e.g. via better retrieval or query expansion), cost per request drops to ~$0.003, and the same traffic fits within a much lower budget. This is the lever the architect pulls when TCO is the binding constraint.
- **Operational topology**: Multi‑region deployment (active‑active) provides availability but doubles the infrastructure cost. If the 99.9% availability SLA is non‑negotiable, the architecture must absorb the 2× cost. If it is negotiable, a single-region with graceful-degrading fallback may suffice. The operational constraint thus directly sets the economic floor.

## 7. What We Still Don't Know

- **Tokenizer exactness for technical domains**: While the "one token ≈ 4 characters" rule of thumb is convenient, enterprise Q&A prompts may contain code, JSON, or domain‑specific terminology that tokenizes differently. The exact per‑token count for a given prompt distribution is (to be verified) and would require running the model's tokenizer on a representative sample of real user queries.
- **KV cache scaling with longer contexts**: The canonical scenario uses ~9.2 K input tokens. If retrieval quality degrades and context lengths grow to 32 K or 128 K, the KV cache memory per request grows linearly, and the single‑host FP16 architecture would no longer suffice without quantization or model parallelism. The breakpoint is (to be verified) and workload‑dependent.
- **Impact of reranking on latency**: The TTFT budget assumes retrieval (~120 ms) plus prefill. If a late‑stage reranker is added to the pipeline, the retrieval component's latency may increase, eating into the TTFT budget and potentially requiring a wider SLO margin or a faster retriever. The magnitude of this effect is (a hypothesis) and should be measured before production deployment.
- **Economic durability at scale**: The tokens‑per‑dollar numbers are derived from 2026 on‑demand H100 pricing. Spot instances, reserved contracts, or custom cloud agreements could shift the economics significantly. The durability of the economic model across provider changes is (a hypothesis).

## 8. End-of-Chapter Mini-Case: A Six-Dimension Workload Characterization

An architect is brought into the early design of an internal Q&A platform. The stakeholder says: "We have thousands of employees who want to ask questions over our internal documents. We need it to be accurate and fast, but we don't know how many thousands or how fast is fast enough." Before any architecture can be defended, the architect does the workload characterization that this chapter walks through.

From the unit-and-token work of Ch 1 alone, the architect can already establish: the unit is tokens; the request shape will be prompt + retrieved context + output; the workload is input‑heavy; and the first number to lock down is tokens‑per‑request, because every downstream decision (which model fits, how much memory, what latency is possible) is priced against it. Using the canonical scenario as a starting point — ~2,000 registered users, ~5% concurrency, ~10 rps, ~9.2 K input + 300 output tokens — the architect projects the enterprise's actual headcount. If the company has 5,000 employees and expects 10% concurrent activity during peak Q&A periods (after a policy rollout), the concurrency rises to 500 users. With the same ~10 s *planning-round* request duration (the Little's-law basis used above, 100 concurrent ÷ 10 s ≈ 10 rps), throughput climbs to 500 ÷ 10 ≈ **50 rps**. Using the canonical per-host bound from Chapters 15–20 (a single 8×H100 host serves ~2.0 req/s at full modeled utilization, i.e. C/W ≈ 17.5 KV-resident requests ÷ 8.6 s), the fleet rounds to:

$$
n_\text{hosts} = \frac{50 \text{ rps}}{2.0 \text{ req/s/host}} \approx 25 \text{ hosts} \quad (\text{full utilization})
$$

and roughly **~36 hosts** at a 70% target utilization. A prefill-throughput cross-check from the Chapter 8 model bounds it from below: 50 rps × 9.2K input = 460,000 prefill tokens/s ÷ ~19,800 tokens/s per host (the host's *ideal* prefill rate) ≈ ~23 hosts — and at the achieved ~8.5K tokens/s it is ~54 hosts. So prefill-throughput is a *lower* bound on host count; the binding figure is the KV-residency/service-time ~25 (full util) / ~36 (70%) result. The two do not "agree" — the KV-bound dominates, and the prefill model shows why adding hosts for prefill alone is the wrong lever at this scale; both are *analytical* bounds that must be confirmed by benchmark goodput (Chapter 14).

At the canonical instance rate (~$20/hr per 8×H100 host), ~25 hosts on on-demand clouds is roughly **$140K–$350K/month** depending on purchase mode and duty cycle (self-host capex amortized runs lower, on-demand burst higher; Chapter 16 develops the TCO properly). The architect can now speak the system's currency — tokens, rps, dollars per million — and can engage the rest of the team on model selection, serving configuration, and TCO with concrete numbers rather than vague assurances. The specific sizing — turning "thousands of employees" into a characterized workload across all six dimensions — is the payoff of Ch. 4's framework, and it is the prerequisite for every architecture question that follows.