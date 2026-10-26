# Chapter 11 — Serving: From Model in Memory to Requests in Flight


Serving is a small set of composable mechanisms — continuous batching, paged/blocked KV cache, prefix caching, and prefill/decode disaggregation — that turn a static in-memory model into a live multi-request system. The architecture choices that matter are which of these are adopted and how they share the host's KV budget, because the latency SLO is met by the batch and cache strategy rather than by the model alone.

## The Architect's Question

After this chapter we should be able to answer the operational half of deployment: *the model is in memory and the requests are arriving at ~10 per second — how do we actually serve them without violating our latency SLO?* We will develop the serving mechanisms that turn a static model into a live, multi-request system: how requests are batched, how KV cache memory is managed, how repeated prefixes are reused, and when to split prefill from decode onto separate pools. After this chapter, serving is not a black box — it is a sequence of explicit architectural choices, each with a measurable consequence.

## 1. Concept

Serving is a small set of mechanisms, invented roughly in order:

1. **Batching** — running multiple requests through the model together to amortize the weight reads. The key modern advance is **continuous (iteration-level) batching** introduced by **Orca (OSDI 2022)**: instead of waiting for an entire batch to finish, the scheduler admits and evicts requests at every decoding step, filling the GPU's idle slots as soon as they free up. [S1][1P]

2. **PagedAttention / vLLM (SOSP 2023)** — managing the KV cache in fixed-size blocks (like a virtual-memory page table) so that different requests' KV caches no longer need contiguous memory, slashing fragmentation and letting the serving engine pack far more concurrent requests. [S2][1P]

3. **Prefix caching** — recognizing that many requests share context (e.g. the same retrieved documents), and caching the KV of the common prefix so a new request does not re-prefill it. **RadixAttention (SGLang)** and **Automatic Prefix Caching (vLLM APC)** are the canonical implementations. [S3][1P]

4. **P/D disaggregation** — splitting the compute-bound *prefill* stage from the bandwidth-bound *decode* stage onto separate pools, because they bottleneck on different resources. Pioneered by **Splitwise (ISCA 2024)** and **DistServe (OSDI 2024)**; **Mooncake** takes the KV-centric view, transferring KV caches from the prefill pool to the decode pool (with CPU/DRAM/SSD offload) and reports up to **525% throughput lift** in long-context simulation and **75% more requests** on a real Kimi workload. [S4][1P]

These mechanisms compose: continuous batching is the baseline, PagedAttention makes it memory-efficient, prefix caching makes it cheaper, and P/D disaggregation makes it scale.

**Source keys [S1]–[S6].** The bracketed keys used throughout this book (and in the evidence taxonomy of the Sources, Method, and Reproducibility chapter) point to the primary sources below. Each is a [1P] first-party or peer-reviewed source; the book's derived numbers cite the key plus a [DERIVED] tag.

- **[S1] Orca** — Yu et al., "Orca: A Distributed Serving System for Transformer-Based Generative Models," OSDI 2022. Continuous (iteration-level) batching.
- **[S2] PagedAttention / vLLM** — Kwon et al., "Efficient Memory Management for Large Language Model Serving with PagedAttention," SOSP 2023. Block-based KV cache.
- **[S3] Prefix caching** — "Fast Inference from Transformers via Radix Attention" (SGLang, 2023) and vLLM Automatic Prefix Caching (APC). Caching shared-prefix KV.
- **[S4] P/D disaggregation** — "Splitwise: Efficient Generative LLM Inference Using Phase Splitting" (ISCA 2024), "DistServe: Disaggregating Prefill and Decoding for Goodput-optimized Large Language Model Serving" (OSDI 2024), and Mooncake (KV-centric disaggregation, 2024).
- **[S5] DFlash** — Chen et al., "DFlash: Block Diffusion for Flash Speculative Decoding," ICML 2026 (PMLR v306; arXiv:2602.06036). Speculative-decoding system reporting >6× lossless acceleration over autoregressive decoding (up to 6.1× on Qwen3-8B) and up to 2.5× faster than the prior state of the art, EAGLE-3.
- **[S6] vLLM FP8-KV blog** — the vLLM FP8-KV blog post's '54%' figure is a decode inter-token-latency (ITL) slope, a LATENCY metric, not a memory/residency ratio. Any reference to it (Chapters 1, 3, 6, 7, 15, 22, Appendix A and the glossary) is a latency reference only. The KV memory footprint this book uses is the raw tensor byte-halving of ~1.31 MB/token (exactly 50% of BF16) [ILLUSTRATIVE][DERIVED]; any block-allocation/metadata overhead is NOT vendor-measured here and must be filled by a deployment benchmark.

## 2. Mental Model

Serving is **managing three precious resources against a stream of arrivals**: GPU compute (FLOPs, bound in prefill), GPU memory bandwidth (HBM, bound in decode), and GPU memory capacity (HBM bytes, bound by KV cache). Each mechanism trades one of these:

- **Batching** improves compute and bandwidth utilization by amortizing the fixed per-step weight reads across more requests.
- **PagedAttention** improves memory capacity by eliminating KV fragmentation.
- **Prefix caching** reduces memory capacity and prefill compute by reusing already-computed KV.
- **P/D disaggregation** lets the prefill pool run at high compute utilization and the decode pool at high bandwidth utilization simultaneously, instead of one pool being starved.

The mental model is a **resource budget**: a request arrives, consumes some FLOPs (prefill), some bandwidth (decode), and some memory (its KV cache) for its lifetime. Serving architecture is about sizing and scheduling those three budgets so the SLO holds across the burst.

## 3. Worked Example

### The Canonical Workload in a Serving System

Recall the canonical enterprise-Q&A RAG workload (Ch 4, Table 4-3): ~10 rps average, ~40 rps peak; each request carries ~9,200 input tokens and ~300 output tokens; TTFT budget 1.2 s, TPOT ~25 ms/token. [ASSUMPTION]

### Discrete Batching Wastes the GPU

Naive **discrete (static) batching** accumulates requests until a batch fills, then runs them to completion, then starts the next batch. Problems compound at this workload's 9.2K-input shape:

- Requests arrive in *bursts* (recall the ~40 rps peak). Discrete batching forces early-arriving requests to **wait** for the batch to fill, inflating TTFT toward the 2 s SLO breach.
- The batch is locked until its *slowest* member finishes (fits-all-in-one-run), so a short 100-token output tails behind the longest while the GPU finishes the whole batch — idle bubbles at the end of every batch.
- Batch boundaries create periods where the GPU drains (no work) then floods — utilization is spiky around the mean. [ILLUSTRATIVE][DERIVED]

### Continuous Batching Fills the Bubbles

**Continuous batching (Orca [S1][1P])** eliminates the batch boundary: at every decode step the scheduler accepts any new prefill-ready request and evicts any finished one, so decode slots never sit idle. In the canonical stream, a 300-token decode at ~25 ms/token occupies a slot for ~7.5 s; while a long decode runs, the freed FLOPs are continuously refilled by new short requests. The utilization gain is the difference between spiky discrete batches and a continuously-fed pipeline. Rather than stipulate a single percent, the mechanism makes the GPU the steady bottleneck instead of the scheduler. [ILLUSTRATIVE][DERIVED]

![Fig 11.1 — Discrete vs continuous batching (Orca-style slot diagram). The horizontal axis is **time (decode steps / iterations)**; each row is one decode step, and in the continuous panel the step boundaries are staggered across rows as the scheduler admits new requests and evicts finished ones. In the top (discrete) panel a batch is locked until its slowest member finishes, so short outputs idle in the trailing slots; in the bottom (continuous) panel freed slots are refilled every step. The diagram is a **decode-only** illustration (all shown requests are in the per-token decode phase); a real serving system also interleaves prefill of newly-arrived requests into the same steps, which is the mixed prefill/decode scheduling developed in §11.4 and Ch 15. [ILLUSTRATIVE conceptual]](figures/fig-11-1102.png)

*Discrete batching runs each batch to completion, leaving GPU slots idle as sequences finish early; continuous batching admits and evicts requests at every decode step, backfilling freed slots. (Illustrative, after Orca, OSDI 2022.)*

### PagedAttention: Killing the Fragmentation Tax

In re-packaged (naive) serving, each request's KV cache for 9.2K input is ~24.1 GB (FP16, ~2.62 MB/token × 9,200, initial KV) [ILLUSTRATIVE][DERIVED]. If served contiguously, variable-length completions leave fragmented, unusable holes — exactly like a fragmented heap. **PagedAttention/vLLM [S2][1P]** allocates KV in fixed blocks shared and evicted like page frames, so the ~24.1 GB per request is packed densely and more concurrent requests fit in the same 640 GB node [ILLUSTRATIVE][DERIVED]. The win is *more concurrency under the same SLO*, not faster single-request math.

### Prefix Caching: Don't Re-Prefill the Same Documents

The RAG request's 8K retrieved-context tokens are largely shared across queries (same documents). Without caching, every request re-runs the ~1.29 PFLOP prefill for those 8K tokens [ILLUSTRATIVE][DERIVED]. **RadixAttention / APC [S3][1P]** caches the KV of common prefixes, so a new request reuses the shared-document KV and prefills only the unique query tail — cutting the dominant prefill FLOPs and TTFT for repeated-context traffic [ILLUSTRATIVE][DERIVED].

### When to Disaggregate: Prefill and Decode Want Different Pools

Recall from Ch2/Ch6: prefill is **compute-bound** (~1.29 PFLOP → ~1.19 PFLOPS required vs 0.989 PFLOPS peak), decode is **bandwidth-bound** (the whole-model weight-read rate of ~5.6 TB/s if served by one device vs 3.35 TB/s per GPU; under the canonical 8×H100 host it is sharded to ~0.70 TB/s per GPU, and the shard-invariant cause is the low ~1.0 FLOP/byte intensity, Ch 6) [1P][DERIVED]. Serving both from one pool forces a compromise: batch for prefill and it slows decode; optimize for decode and prefill starves. **P/D disaggregation (Splitwise/DistServe/Mooncake [S4][1P])** runs prefill nodes at high FLOP-utilization and decode nodes at high bandwidth-utilization, transferring KV across via the fabric (**Fig 11.3** shows the two-pool topology and what moves between them). Mooncake's reported >525% long-context throughput and +75% request count are the quantitative anchor [S4][1P]. For the canonical single-host (~10 rps) this disaggregation is premature; it pays off only when the workload outgrows a node and the two phases' resource conflicts become binding.

#### Table 11-1 — Serving techniques at a glance

| Technique | Mechanism | Primary resource traded | When it matters | Source |
|---|---|---|---|---|
| Discrete batching | Lock batch to completion | — (wastes) | baseline only | — |
| Continuous batching (Orca) | Admit/evict at each decode step | compute+bandwidth util | high concurrency | [S1][1P] |
| PagedAttention / vLLM | Block-based KV pages | memory capacity | many concurrent requests | [S2][1P] |
| Prefix caching (RadixAttention/APC) | Cache shared-prefix KV | prefill FLOPs + memory | repeated-context RAG | [S3][1P] |
| P/D disaggregation | Split prefill/decode pools + KV transfer | both at scale | workload outgrows a node | [S4][1P] |

## 4. Measurement

Good serving telemetry answers "are we meeting the SLO while keeping the GPU busy?":

1. **Measure goodput, not raw throughput** — tokens/s that arrive before their SLO deadline (Ch6). Continuous batching is only a win if it raises goodput.

2. **Measure KV utilization** — fraction of the 640 GB node memory consumed by live KV vs weights. PagedAttention and prefix caching both raise the effective KV packing; track it.

3. **Measure prefill-vs-decode utilization separately** — a FLOP-bound prefill core and a bandwidth-bound decode core running on one pool tells us when to disaggregate.

4. **Measure the scheduler's real occupancy** — idle decode slots, queue wait, and the tail of TTFT under load, not the average.

## 5. Common Mistakes

- **Assuming bigger batches always help.** Bigger discrete batches raise raw tokens/s but push TTFT past the SLO, zeroing goodput (Ch6). Continuous batching exists precisely to uncouple batch size from wait.

- **Serving KV contiguous and watching fragmentation.** PagedAttention removes the fragmentation tax; skipping it wastes memory under concurrency.

- **Re-prefilling shared context.** Without prefix caching, repeated RAG documents are recomputed per request — one of the most wasteful failures for this workload.

- **Choosing P/D disaggregation too early.** Splitting pools adds fabric + orchestration; for a single host it is overhead without the resource conflict that motivates it.

- **Believing speculative decoding (DFlash reports >6× lossless acceleration, up to 2.5× faster than EAGLE-3 [S5][1P]) is a serving baseline.** These are paper-reported results under the paper's evaluation setup, not portable serving-speed figures. Speculative decoding is an optimization for bandwidth-bound decode, not a requirement, and must be validated on the workload.

## 6. Architecture Consequence

The serving mechanisms dictate the deployment choices:

- **Baseline (canonical single-host):** continuous batching (vLLM/Orca) is near-mandatory to hold TTFT under the SLO (1.2 s, p95 ≤ 2 s) at 10 rps input-heavy load; PagedAttention ensures the ~24.1 GB-per-request KV pack fits; prefix caching is the highest-leverage optimization because the workload is repeated-context RAG. This matches the memory and compute conclusions of Ch4/Ch7 for the ~10 rps *average* baseline; at the ~40 rps peak the KV budget forces replication, which Chapter 17 sizes. [S1][S2][S3][1P]

- **Scaling up:** those three carry the workload far before disaggregation is justified. FP8 KV (raw tensor byte-halving = 1.31 MB/token, exactly 50% of BF16) [ILLUSTRATIVE][DERIVED] and KV offloading are memory levers available without restructuring.

- **Beyond a node:** when prefill FLOPs and decode bandwidth fight on one pool, P/D disaggregation (Splitwise/DistServe/Mooncake) is the architecture of choice, with Mooncake's KV-transfer engine moving caches between pools. [S4][1P]

![Fig 11.2 — Serving is four orthogonal concerns, not a stack (request scheduling, state management, reuse, resource specialisation). A concrete serving design that chooses one mechanism per concern: **request scheduling** = continuous (Orca-style) batching; **state management** = PagedAttention (fixed-size KV pages); **reuse** = prefix caching of shared context; **resource specialisation** = P/D disaggregation (separate prefill and decode pools). The four are independent dials — a system can combine any mechanism with any other — and the canonical 8×H100 host uses all four together. [ILLUSTRATIVE conceptual]](figures/fig-11-1101.png)

*The design lever is what each concern trades: **request scheduling** exchanges latency for utilization, **state management** exchanges memory capacity for concurrency, **reuse** avoids re-prefill FLOPs, and **resource specialisation** matches two compute/memory regimes to two pools.*

<!-- Figure spec: mechanism-first serving-flow diagram; request stream → scheduler → KV page table (+ prefix cache) → optional prefill pool / decode pool split → output; annotate the resource each stage trades. -->

![Fig 11.3 — P/D disaggregation topology: a prefill-optimized pool (FLOPs) and a decode-optimized pool (HBM) bridged by KV transfer. The KV-transfer arrow is the load-bearing cost: it moves the per-request KV state (e.g. ~35 GB for a ~13K-token context at 2.62 MB/token, §9.8) over the interconnect, and the disaggregation is only worth it when the prefill/decode specialization benefit **exceeds** the KV-transfer time plus the orchestration overhead of routing requests between two pools. Illustrative: at NVLink's 450 GB/s per direction (§9.2) that ~35 GB transfer is ~0.08 s, which is small against the ~1.08 s prefill it enables, so the inequality holds on-node; over a 40 GB/s fabric it is ~0.9 s, which can erase the benefit — the transfer cost is the term that decides whether P/D disaggregation pays. [ILLUSTRATIVE][DERIVED]](figures/fig-11-1103.png)

*The KV moves once per request, then stays local (ownership splits); the split itself exists because the two stages want opposite resources under load — prefill needs compute capacity (~1.19 PFLOPS required vs 0.989 peak single-H100), while decode needs HBM bandwidth (the whole-model weight-read rate of ~5.6 TB/s if served by one device vs 3.35 TB/s per GPU, sharded to ~0.70 TB/s per GPU under the canonical 8×H100 host, Ch 6) [1P][DERIVED].*

### The Mechanisms, Not the Product Catalog

The mechanisms above are what matter; the engines are just implementations of them. This comparison is organized by *architectural capability* so it transfers across specific products and versions. **It is explicitly time-sensitive** — capabilities, supported models, and features change fast, and these rows must be re-verified against each engine's current first-party documentation before any deployment decision. The table is a map of *which mechanism to look for*, not a ranking.

#### Table 11-2 — Serving engines by architectural capability (time-sensitive)

| capability | vLLM | SGLang | TensorRT-LLM | llama.cpp | architectural note |
|---|---|---|---|---|---|
| scheduler model | continuous batching | continuous + RadixAttention | batch orchestration (TRT engine) | single/multi-stream | which batching algorithm, not which vendor |
| KV-memory management | PagedAttention | RadixAttention (page + prefix tree) | KV re-compute/off-load on engine | custom KV store | how KV is allocated/fragmented |
| prefix caching | auto prefix | Radix prefix tree | some cache | limited | how much re-prefill is avoided |
| quantization support | broad (GPTQ/AWQ/FP8) | broad | tight NVIDIA-precision (FP8/INT8/INT4) | GGUF (K-quants) | what precision the kernels are tuned for |
| parallelism | TP/PP/DP | TP/PP/DP | TP/PP/DP (NVIDIA-optimized) | limited / CPU+GPU | how the model is split |
| P/D capabilities | some (separate prefill/decode) | native disaggregation | via engine orchestration | n/a | whether prefill and decode can run on separate pools |
| structured generation | constrained decoding | constrained (XGrammar) | constrained | constrained | whether output can be schema-constrained |
| supported hardware | NVIDIA / AMD / CPU | NVIDIA / AMD | NVIDIA-only | CPU + consumer GPUs | deployment niche |

The columns read as *knobs on a common set of mechanisms*, not as "which engine is best." An engine's real value is which mechanisms it implements *well for the deployed workload's shape* — e.g. a repeated-context RAG workload cares most about the prefix-caching row (RadixAttention in SGLang is a strong implementation), while a latency-critical single-stream deployment might care more about the scheduler and structured-generation rows. **Never conclude "X is the go-to engine"** — that is workload-independent and will be wrong. The only defensible statement is workload-specific: *for this request shape, this precision, and this hardware, engine Y implements the mechanism Z we need; benchmark it against the alternative (Ch. 14).*

## 7. What We Still Don't Know

As of 2026-08, several questions remain open, each flagged **[HYPOTHESIS]** or **[TODO: measure on target cluster]**:

- **Portable end-to-end goodput across real enterprise RAG** — Mooncake's 525%/75% [S4][1P] and DFlash's >6× [S5][1P] are strong anchors but are workload-specific; general rules remain an open hypothesis **[HYPOTHESIS]**.
- **Prefix-cache hit rates in mixed traffic** — the real reduction in prefill FLOPs from RadixAttention/APC for a given document-distribution remains a hypothesis **[HYPOTHESIS]**.
- **KV-transfer cost at scale** — Mooncake's engine moves KV to CPU/DRAM/SSD [S4][1P], but the exact latency/bandwidth crossover where disaggregation wins is unmeasured **[TODO: measure on target cluster]**.

## 8. End-of-Chapter Mini-Case: Which Serving Mechanism to Reach For

An architect runs the canonical internal Q&A service on a single 8×H100 host and sees p95 TTFT creep toward 2.2 s against a 2 s SLO as traffic peaks at 40 rps. Applying this chapter: the architect first confirms continuous batching is on (vLLM) and that PagedAttention is active — otherwise the ~24.1 GB-per-request KV for 9.2K inputs fragments and concurrency collapses. The biggest lever: prefix caching. The RAG traffic reuses the same retrieved documents, so the architect enables automatic prefix caching and watches TTFT drop as the 8K-context prefill is replaced by cached KV lookups. The architect does **not** reach for P/D disaggregation or speculative decoding — the single host is resource-sufficient *for this latency/SLO* once the wasted re-prefill is eliminated. The result: p95 TTFT back under 1.8 s at 40 rps, goodput restored, with only configuration changes — because the architecture followed the serving mechanism that matched the workload's repeated-context shape. 
Scope note: this is a **latency-bound, single-host** judgment. It answers "can one host meet the TTFT SLO per request," *not* "can one host carry the whole 40 rps arrival rate." At the canonical peak, in-flight concurrency at the ~8.6 s service time is ≈344 requests, far above an 8×H100 host's KV-residency ceiling (C ≈ 17.5, conservative integer floor 17); a *single* host therefore cannot serve the peak *traffic*, even though it can meet the per-request TTFT SLO. The capacity/fleet question — how many such hosts for λ=40 rps — is answered by Chapter 17's service-time-aware sizing (≈20 hosts), not by this mini-case. The two questions (per-request latency vs aggregate capacity) must not be conflated.
