# Chapter 2 — What Actually Happens During Inference

## The Architect's Question

After this chapter we should be able to reason about the two fundamental modes of LLM inference — prefill and decode — and to identify which system constraint each mode exposes. We should be able to compute the bandwidth and FLOP demands of a given workload, compare them against real hardware limits, and understand why decode is HBM-bandwidth-bound while prefill is compute-bound. This distinction directly shapes architectural decisions: whether we need more GPUs, whether we can disaggregate prefill from decode, and how we size memory and compute in a fleet. After this chapter we should see inference not as a single monolithic cost but as two opposite-bound processes that require different levers.

## 1. Concept

Inference is the process of turning a sequence of input tokens into a sequence of output tokens using a trained neural network. In an autoregressive model, every generated token requires a fresh forward pass, but the computation split between the prefix (the prompt) and the suffix (the generated output) is fundamentally different.

**Prefill** is the first pass over the prompt. The model reads every token of the input context, computes attention over the entire prefix, and produces the first output token. During prefill, the model attends over all input positions, so the work grows with the square of the context length.

**Decode** is the per-token generation that follows. After prefill, each new token only attends to the cached keys and values from the prefix plus all previously generated tokens. In the *batch-1-equivalent* weight-streaming model we use for this first-pass arithmetic, the per-step cost is constant in context length — we only attend to the new token against the cache — and it requires reading the entire model weight matrix from HBM every step, because the auto-regressive pass reuses the same parameters over and over. (In a real serving stack, batching and weight-read amortization change this per-request picture substantially; that is the subject of later chapters.)

The critical architectural insight: prefill is dominated by FLOPs (matrix-multiply arithmetic), while decode is dominated by HBM memory bandwidth (reading 140 GB of weights 40 times a second). These are opposite bottlenecks, and confusing them is the most common architectural misstep.

![Fig 2.1 — The canonical end-to-end inference pipeline: prompt to generated tokens, divided into PREFILL (top) and DECODE (bottom). Prefill is the one-shot parallel burst that populates the KV cache and yields the first token — it commonly occupies a higher-arithmetic-intensity regime, straining compute, and is measured by TTFT. Decode is the sequential autoregressive loop that reuses the cached K/V and re-reads weights every step — it commonly occupies a lower-arithmetic-intensity regime, straining HBM bandwidth and capacity, and is measured by TPOT/ITL. These are useful heuristics, not universal laws: which phase is actually compute- or bandwidth-bound is a property of the model × workload × kernel × hardware operating point (developed through the roofline framework in Ch 8). [ILLUSTRATIVE conceptual]](figures/fig-02-0202.png)

*This is the figure the rest of the book builds on.* Keep the shape in mind: every later chapter refines one part of it. **Chapter 3** (model) asks *what the blocks compute and how the KV cache is sized*; **6** (metrics) measures which phase is the bottleneck; **7** (memory) prices the KV cache precisely; **8** (compute) derives the FLOPs and roofline that make prefill compute-bound; **10** (parallelism) splits the model across the devices the pipeline traverses; **11** (serving) schedules many of these pipelines; **15** (performance) diagnoses which phase actually hurts; and the fleet chapters price the host count the loop demands. Because the two phases stress *different* resources, the armature of the whole book sits on this single split.

**Where the Q/K/V and KV cache live in this picture (the bridge to Ch. 3/7).** The transformer layer computes, for each token, three learned projections — **query (Q)**, **key (K)** and **value (V)**. Attention scores are the similarity of a query to every prior key; the scores weight the values, which are blended into the token's new representation. What matters for architecture: **K and V for a token do not change once that token has been processed.** The query for a *later* token attends against them, but rewriting them would be redundant work. So decode does not recompute the prefix's K/V — it *reuses* the stored K and V from prefill. That is the KV cache: not an optimization bolted on, but the direct consequence of *which* projections are reusable and which (the query) is always new. It is also why KV memory grows with sequence length (one K and one V per token, per layer) and why attention implementation and precision (GQA/MQA, FlashAttention, KV quantization) change an architecture problem that is really a memory problem. Ch. 3 and Ch. 7 do the arithmetic; this figure is where the causal thread starts.

**A vocabulary note that prevents a common conflation.** Several terms sound like the same thing but are *not* interchangeable, and the chapter will use them precisely:

| term | what it is | what it is **not** |
|---|---|---|
| **KV cache** | the stored K and V tensors per token per layer, saved so decode does not recompute the prefix | an *optimization* over a shared prefix |
| **PagedAttention** | a memory-*allocation* scheme for the KV cache (splits it into fixed-size pages, cuts fragmentation/waste) | a way to *reduce* the amount of KV state |
| **prefix caching / KV reuse** | reusing *already-computed* K/V for a shared prefix, to skip re-prefilling it | the same as caching the KV of a *single* request's own decode |
| **prompt caching** | broader system/provider term; the book uses it to mean *reusing the KV of a shared prompt prefix across requests* | a distinct mechanism from prefix caching |
| **KV quantization** | reducing the *bytes* per K/V element (e.g. FP16→FP8) | reducing the *number* of key/value entries |
| **KV offloading** | moving some KV state out of GPU HBM (to host DRAM/SSD), trading capacity against transfer latency | shrinking the state itself |

The short version: the **KV cache** is *the state*; **PagedAttention** manages *where that state lives* on the device; **prefix caching** avoids *computing it twice* for a shared prefix; **quantization** shrinks *each element*; **offloading** moves *some of it elsewhere*. Each attacks a different constraint (capacity, fragmentation, redundant compute, byte count, residency), and each has its own trade-off — later chapters put numbers on them.

**The resource model (the book's recurring framework).** Inference consumes several *fundamentally different* resources, and the single most useful habit an architect can build is to name which one a given optimization or bottleneck is about. The pipeline figure above surfaces four of them, and the metric chapter (Ch. 6) and the design chapter (Ch. 12) build on the same set. The book will use these names consistently:

| resource | unit | what it limits | first surfaces in |
|---|---|---|---|
| **compute capacity** | FLOPs | how much arithmetic per unit time | prefill (Ch. 2, 8) |
| **memory bandwidth** | bytes/s | how fast data can move | decode (Ch. 2, 8) |
| **memory capacity** | bytes resident | how much state fits (weights + KV) | KV cache / concurrency (Ch. 7) |
| **interconnect bandwidth/latency** | bytes/s, delay | cross-GPU / cross-host movement | parallelism (Ch. 9, 10) |
| **scheduling capacity** | useful work resident | keeping hardware busy despite request raggedness | serving (Ch. 11) |
| **latency budget** | TTFT, TPOT/ITL, end-to-end | the SLO the system must meet | workload (Ch. 4) |
| **throughput / goodput** | useful tokens/s under SLO | completed work, not just tokens/s | metrics (Ch. 6) |

The discipline the book applies everywhere: **every optimization is a hypothesis about which resource it shifts and what it trades away.** FlashAttention moves the bottleneck from *bandwidth* toward *compute* (fewer HBM round-trips); KV quantization trades *capacity* for a small precision loss; prefix caching trades *prefill compute* for *cache residency*; continuous batching trades *latency* for *utilization*; P/D disaggregation trades a *homogeneous pool's* simplicity for separate *compute- vs bandwidth-optimized* pools. When the book introduces a technique, it will name the resource it targets and the resource it costs — that is the difference between reasoning and a vendor catalog. The optimization decision map (Ch. 15) is this framework read backwards: from an observed symptom to the resource that is likely starved.

**The causal chain (how the chapters hold together).** The book is one argument, not a set of topics. The thread is:

tokens determine sequence length → sequence length determines KV growth and attention work → KV growth determines memory pressure → attention and model execution determine compute and bandwidth demand → those resource demands determine latency behavior → latency and concurrency determine scheduler requirements → scheduler behavior determines serving efficiency → serving efficiency and SLOs determine host count → host count and model topology determine interconnect and fleet architecture → fleet architecture determines cost, resilience, placement, and operational complexity.

Every chapter is one link of that chain, and each *deepens* the same mental model from Ch. 2 rather than restarting it. By the time the argument reaches Ch. 11 (serving) or Ch. 17 (fleet), the concepts were introduced in Ch. 2 — Ch. 2 gave the shape, the later chapters give the numbers and the decisions. If a chapter ever feels like "here is another concept," it has broken the thread.

## 2. Mental Model

Inference is two fundamentally different physical processes, distinguished by what limits them.

**Prefill is compute-bound.** It is like turning on a massive industrial fire hose to fill a reservoir. The burst of flow is enormous, and the time it takes is limited entirely by the raw horsepower of the pump (compute/FLOPs) pushing the water. The pipe is wide open, but the motor is working at its absolute limit.

**Decode is bandwidth-bound.** It is like trying to empty a 140,000-gallon swimming pool through a standard garden hose every 25 milliseconds just to produce a single glass of water. The pump (compute) is more than powerful enough, but the diameter of the hose (HBM bandwidth) physically cannot move that volume of water in that time frame.

When we ask "is this workload compute-bound or bandwidth-bound?" the answer depends entirely on which physical constraint we are hitting: the horsepower of the engine, or the diameter of the pipe.

## 3. Worked Example

To make the distinction concrete, let us walk through the canonical enterprise Q&A scenario from canonical scenario (Ch 4, Table 4-3): a 70B-class dense model in FP16, 1 host with 8×H100 GPUs, prompt of 1,200 tokens + 8K retrieved context (~9.2K input), 300-token output, TTFT budget 1.2 s (retrieval ~120 ms + prefill), TPOT budget ~25 ms/token. All numbers are derived from the canonical scenario; none are measurement claims. Where the book writes *Analytical bound — not a benchmark*, it marks a first-order model check under a stated bounding assumption, not a measurement of actual serving throughput.
*Scope of the single-host premise.* Throughout this chapter and the arithmetic chapters that follow, "1 host with 8×H100" is a **per-host / per-request feasibility** container: it asks whether one host can meet the per-request latency and memory SLO (TTFT 1.2 s, TPOT ~25 ms, KV residency) for a single in-flight request. It is **not** a claim that one host serves the canonical 10 rps average / 40 rps peak *arrival rate*. The per-request arithmetic here answers "does one host's compute/bandwidth/memory satisfy one request's latency budget"; the *capacity* question — how many such hosts to absorb λ = 40 rps, where in-flight concurrency λ·W ≈ 344 at the ~8.6 s service time — is answered later (Ch 16–17), and is a different computation that must not be conflated with per-request feasibility. Keeping the two questions separate is the difference between sizing a host and sizing a fleet.

### Table 2-1 — Decode bandwidth and prefill FLOPs (worked example, not reference)

| metric | value | derivation |
|---|---|---|
| Model params | 70B | canonical scenario (Ch 4, Table 4-3) |
| Model weight bytes (FP16) | 140 GB | 2 bytes × 70B params [ILLUSTRATIVE][DERIVED] |
| Decode: weight-read per token | 140 GB | Auto-regressive, batch-1-equivalent: one read of all weights per generated token before batching/amortization [ILLUSTRATIVE][DERIVED] |
| Decode: required bandwidth (TPOT ~25 ms) | 5.6 TB/s | 140 GB / 0.025 s (batch-1-equivalent weight-streaming model, before amortization) [DERIVED] |
| H100 HBM3 peak bandwidth | 3.35 TB/s | NVIDIA H100 specs [1P][FACT] |
| Decode: bandwidth verdict | bandwidth-bound | 5.6 > 3.35 → under the batch-1-equivalent model, a single H100 cannot meet the demand; batching/amortization change this (see later chapters) [ILLUSTRATIVE][DERIVED] |
| Prefill: input tokens | 9,200 | 1,200 prompt + 8K context [ILLUSTRATIVE][DERIVED] |
| Prefill: FLOPs (2 × params × tokens) | 1.29 PFLOP | 2 ×70e9 ×9.2e3 ≈ 1.29 ×10^15 [DERIVED] |
| H100 BF16 dense compute | 989 TFLOPS | NVIDIA H100 BF16 tensor-core peak [1P][FACT] |
| Prefill: compute verdict | compute-bound | 1.29 PFLOP / ~1.08 s ≈ 1.19 PFLOPS > 0.989 PFLOPS peak → single H100 insufficient for real-time prefill [DERIVED] |

![Fig 2.2 — Prefill and decode sit on an arithmetic-intensity continuum, split by the roofline ridge. Low-batch decode (streaming weights per token) lands at ~1 FLOP/byte — the memory-bound side; long-prompt prefill lands at high intensity — the compute-bound side. These are operating points, not fixed identities: batch, context, precision, kernel and hardware all move a point across the ridge. [ILLUSTRATIVE conceptual, roofline developed in Ch 8]](figures/fig-02-0201.png)

*Decode is HBM-bandwidth-bound (5.6 TB/s vs H100 3.35 TB/s); prefill is compute-bound (~1.19 PFLOPS required vs H100 0.989 PFLOPS peak). *(Analytical bound — not a benchmark: these are first-order model checks, not a measurement of actual serving throughput.)*

**Worked example arithmetic details:**

- **Decode bandwidth.** In auto-regressive decode, generating one token requires a full forward pass of the 70B parameter matrix. At FP16 (2 bytes per parameter), the weight footprint is $W = N \times 2 = 140$ GB. **This is the aggregate model-wide weight traffic** — but note the unit of comparison carefully. Name it precisely: this 140 GB is the **logical model-weight footprint used as a first-order HBM traffic approximation** (what later chapters call the **canonical weight-stream approximation**). It is the footprint you get from *reading every parameter once per decode step in a dense model with no reuse*, not a claim about physical HBM traffic in a real engine. Physical traffic depends on residency, caching hierarchy, fusion, batching, quantization, sharding, and implementation, and rises or falls accordingly. For a hypothetical single-device implementation holding the entire FP16 model, the aggregate model-weight traffic per decode step is ~140 GB; on a tensor-parallel deployment both weight residency *and* this traffic are sharded across GPUs, so the relevant comparison is per-GPU shard traffic against per-GPU HBM bandwidth, plus communication overhead. (A 140-GB FP16 model cannot reside on a single 80-GB H100 anyway, so the whole-model-on-one-GPU comparison is deliberately hypothetical.) With a TPOT budget of ~25 ms per token, the *aggregate* required bandwidth is

$$
B_\text{req} = \frac{W}{\tau} = \frac{140 \text{ GB}}{0.025 \text{ s}} = 5{,}600 \text{ GB/s} = 5.6 \text{ TB/s}
$$

[ILLUSTRATIVE][DERIVED]. A single NVIDIA H100 HBM3 delivers ~3.35 TB/s peak bandwidth [1P][FACT]. Since $5.6 > 3.35$, under this batch-1-equivalent weight-streaming model one H100 cannot supply the required *aggregate* weight-read rate — the decode phase is HBM-bandwidth-bound [ILLUSTRATIVE][DERIVED]. Read this as an *aggregate lower-bound illustration*, not as the literal bandwidth requirement of a single H100 in a realistic 8×H100 configuration (where the model and its traffic are sharded, so each GPU streams only its shard against its own 3.35 TB/s, plus communication overhead). This is a statement about the *specified* single-request, ~25 ms/token model, not about all possible 70B serving: batching, weight-read amortization, and precision changes (later chapters) fundamentally alter the per-request bandwidth demand. Within the model, meeting that latency target calls for multi-GPU scaling or bandwidth-increasing topologies (e.g. NVLink-connected nodes).

- **Prefill FLOPs.** The prefill pass computes attention over the 9.2K input tokens and produces the first output token. The *parameterized-linear* FLOP floor for a dense transformer forward pass is well approximated as $2 \times \text{params} \times \text{tokens}$ (the factor of 2 accounts for multiply-add per parameter per token). Call this what it is: **the parameterized-linear FLOP floor, $2NL$, excluding explicit attention-score/value aggregation and other non-matmul overhead.** The full-attention component is *not* captured by $2NL$ — it grows ~quadratically with sequence length (Ch 22), so for a 9.2K-token prefill $2NL$ is a lower bound on total compute, not the whole story. Thus:

$$
\text{prefill FLOPs} = 2 \times N \times L = 2 \times 70 \times 10^9 \times 9.2 \times 10^3 \approx 1.288 \times 10^{15} \approx 1.29 \text{ PFLOP}
$$

[ILLUSTRATIVE][DERIVED]. An NVIDIA H100 delivers ~989 TFLOPS (BF16 dense tensor-core peak, without sparsity) [1P][FACT], which is 0.989 PFLOPS. (Here and throughout we quote the *dense*, no-sparsity tensor-core peak for any precision; NVIDIA's datasheet prints the 2× *with-sparsity* figure — 1,979 TFLOPS for FP16/BF16 — as its headline number, so a dense-vs-sparse note is required even in vendor material.) The required rate against the ~1.08 s prefill budget is

$$
\text{rate} = \frac{1.29 \text{ PFLOP}}{1.08 \text{ s}} \approx 1.19 \text{ PFLOPS}
$$

Crossing $1.19 > 0.989$ — **even before accounting for attention overhead, kernel inefficiency, and sub-100% MFU, this first-order lower bound already exceeds the H100's theoretical peak.** Therefore one H100 cannot satisfy the stated prefill budget under these assumptions; the prefill phase is compute-bound [ILLUSTRATIVE][DERIVED]. Note the direction of this argument: exceeding the *theoretical peak* proves the target is impossible on a single H100 under the stated model, but it does **not** imply any rate below the peak is achievable — real kernels land well under MFU 100%. Meeting the latency SLO therefore calls for multiple GPUs (model parallelism or data parallelism) or more efficient attention implementations.

## 4. Measurement

How do we know whether a given workload is prefill-bound or decode-bound in practice? Three practical measurements:

1. **Divide the TTFT into retrieval + prefill.** Measure the retrieval latency (vector search, document fetch) separately from the prefill latency (prompt processing). In the canonical scenario, retrieval takes ~120 ms, leaving ~1.08 s for prefill on a 9.2K-token prompt. If prefill exceeds this budget, the bottleneck is compute or memory, not retrieval.

2. **Log TPOT against current sequence length, at controlled batch/concurrency.** Track the time-per-token as the generated sequence grows. This is a *scaling curve*, not a binary verdict. An **increasing** TPOT as the sequence lengthens reveals growing KV-attention cost — each new token attends over a longer KV sequence, and decode attention work and KV cache traffic generally grow with sequence length even though cached K/V projections are not recomputed. A relatively **flat** TPOT suggests weight streaming (a fixed per-step cost — reading the full 140 GB weight matrix each step) remains dominant. TPOT does not *have* to stay constant; batching, kernel choice, occupancy, and scheduling can make the observed curve complicated, so measure it rather than asserting a trend.

3. **Measure actual HBM utilization vs FLOP utilization.** Using GPU profilers (NVIDIA Nsight, vLLM stats), watch the fraction of peak HBM bandwidth consumed versus the fraction of peak FLOPS consumed. If HBM utilization is near 100% while FLOPS utilization is low, the kernel is bandwidth-bound (typical of decode). If FLOPS utilization is near 100% while HBM utilization is low, the kernel is compute-bound (typical of prefill).

These measurements cost nothing but a profiler attach and a few representative requests — and they prevent the architect from applying the wrong optimization lever.

## 5. Common Mistakes

- **Treating prefill and decode as the same bottleneck.** A dangerous mistake is assuming that what slows prefill will also slow decode, or vice versa. Prefill FLOPs scale with input length; decode bandwidth is constant per token. Confusing the two leads to over-provisioning compute for a bandwidth-bound workload, or under-provisioning compute for a compute-bound one.

- **Assuming one H100 suffices for 70B inference.** The arithmetic in Section 4 shows that a single H100 cannot meet the decode bandwidth demand (5.6 TB/s vs 3.35 TB/s) nor the prefill compute demand (1.29 PFLOP vs 0.989 PFLOPS). Attributing 70B serveability to a single GPU ignores the opposite bottlenecks and produces an architecture that fails latency SLOs.

- **Ignoring the input/output token asymmetry.** A workload with 9.2K input tokens and 300 output tokens imposes a *substantial prefill compute burden* despite producing relatively few output tokens — do not infer serving cost or resource pressure from output-token count alone. The two legs of the request have different cost structures and different optimization paths: decode is repeated per output token and dominates *wall-clock latency* (at the canonical ~25 ms/token, 300 output tokens ≈ 7.5 s of decode vs a ~1.08 s prefill budget), while prefill is a large one-shot burst of compute and dominates the *compute* burden (the 9.2K-input attention pass). Quoting only per-token latency or only throughput/s hides this distinction.

- **Using manufacturer-peak bandwidth/FLOPS without mapping to real kernels.** H100 3.35 TB/s HBM3 is the theoretical peak; actual sustained bandwidth for weight-read kernels may be 60–80% of peak. H100 989 TFLOPS BF16 dense is the tensor-core peak; actual matmul throughput depends on kernel fusion, batching, and precision. Citing raw numbers without kernel context is an anti-catalog error — the number must be matched to the actual serving kernel in use.

## 6. Architecture Consequence

The opposite bottlenecks of prefill and decode have immediate architectural consequences:

- **Prefill is compute-bound → optimization levers:** kernel fusion (flash-attention, scaled-dot-product attention with fewer reads), model parallelism (splitting the 70B parameters across GPUs), more GPUs in parallel, or prefill-specific servers that dedicate hardware to the bursty preload phase. Quantization (FP8/BF16) does *not* reduce the underlying algorithmic operation count (the usual 2 × params × tokens FLOPs are approximately unchanged — the matmuls still multiply the same matrices); rather it reduces the precision, lowers the bytes transferred/stored, and can raise the *effective* accelerator throughput (8-bit tensor cores run at higher peak rate).

- **Decode is bandwidth-bound → optimization levers:** continuous batching (vLLM, PagedAttention) to amortize weight reads across many tokens in flight, KV cache offloading to SSD or system memory, P/D (prefill/decode) disaggregation (separate pools of GPUs for prefill bursts vs. decode steady state), and higher-bandwidth memory topologies (NVSwitch, HBM3e).

The key architectural decision this enables: **can we disaggregate prefill and decode onto different hardware?** If prefill needs more FLOPS and decode needs more bandwidth, a single homogeneous GPU pool is suboptimal. A two-pool architecture — a prefill cluster optimized for compute (more GPUs, higher FLOPS) and a decode cluster optimized for bandwidth (faster HBM, larger NVLink domains) — is therefore an architecture worth testing. Whether it actually needs fewer GPUs is not established by the asymmetry alone: it depends on achievable utilization, duplicated model residency, KV-transfer cost, interconnect topology, workload shape, burstiness, and the hardware assigned to each pool, all of which must be measured. (The asymmetry makes it a candidate worth benchmarking, not a concluded win.) This is the central theme of Chapter 11 (Serving) and Pattern 4 (Prefill/decode disaggregation).

## 7. What We Still Don't Know

- **Sustained HBM bandwidth for weight-read kernels.** The 3.35 TB/s H100 figure is a theoretical peak; real serving kernels (vLLM, TGI, transformer-engine) may achieve different sustained rates depending on kernel fusion, graph optimization, and batch size. — a hypothesis to be measured on real hardware before it is cited.

- **Effect of continuous batching on the 2 × params × tokens approximation.** Continuous batching amortizes weight reads and improves hardware utilization, scheduling efficiency, and aggregate goodput — but it does **not** reuse one request's transformer activations to avoid the forward-pass work of another unrelated request, so it does not reduce the mathematical FLOP count per request. Compute that *is* re-used across requests sharing a common prefix is a different mechanism: **prefix caching** (or KV reuse), which skips the re-prefill of a shared prefix and thereby does cut real forward-pass work for that portion. The magnitude of the prefix-cache hit rate at fleet scale is not yet pinned down. — to be benchmarked with realistic concurrency patterns.

- **Cross-technology bandwidth numbers.** HBM3e (next-generation) promises ~6+ TB/s per GPU, and AMD MI300X promises ~5.3 TB/s. How these compare to the 5.6 TB/s decode demand shifts the GPU count equation but does not change the fundamental bandwidth-bound vs compute-bound classification. [ILLUSTRATIVE][DERIVED] — vendor-published numbers, verify against the specific generation in use.

- **Effect of quantization on decode bandwidth vs prefill FLOPs.** Int4 or FP8 quantization reduces the weight bytes (e.g., 70B at FP8 = 70 GB instead of 140 GB), which directly lowers the HBM read demand in decode; it does *not* reduce the algorithmic operation count of the matmuls (the 2 × params × tokens FLOPs are approximately unchanged), though lower precision can raise the *effective* throughput of the tensor cores at which those ops run. The direction of the shift is clear (decode bandwidth improves; prefill ceiling rises in effective rate), but the precise trade-off point where decode becomes compute-bound rather than bandwidth-bound depends on the quantization scheme and hardware support. — workload-dependent.

## 8. End-of-Chapter Mini-Case: TTFT and the Prefill/Decode Split

The architect is still in the early design conversation about the internal Q&A tool described in Chapter 1. The team has settled on a 70B-class dense model for accuracy, and they have a rough traffic estimate: ~2,000 registered employees, each roughly as active as the canonical scenario (~10 requests/s average, peaks ~40 rps), with prompts of ~1,200 tokens of internal documents plus ~8K retrieved context and ~300 tokens of answer.

From the unit-and-token work of Ch 1 alone, the architect can already state the hard numbers: each request carries ~9.2K input tokens and ~300 output tokens. At 10 rps average, the system must sustain ~92,000 input tokens/s in prefill and ~3,000 output tokens/s in decode. At 40 rps peak, those numbers jump to ~368,000 and ~12,000 respectively. The architect can also state the two opposite bottlenecks: prefill will be compute-bound (~1.29 PFLOP per request at 9.2K input), and decode will be bandwidth-bound (a ~140 GB/token weight-read requiring ~5.6 TB/s sustained over each ~25 ms decode step). The team's immediate architectural choice is whether to build a single homogeneous GPU cluster or to separate prefill and decode pools — the differing bottleneck profiles make disaggregation worth evaluating, though whether it uses fewer GPUs must be measured rather than assumed (Ch 11).

Before passing this workload to Chapter 4 (workload anatomy), the architect locks in one more number: the tokens-per-request split. This is the currency every downstream chapter will price against, and it has already been established as ~9.2K input + ~300 output per request. The rest of the design — model fitting, memory budget, latency budget, cost — can now proceed in token-denominated terms.