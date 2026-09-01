# Chapter 2 — What Actually Happens During Inference

## The Architect's Question

After this chapter we should be able to reason about the two fundamental modes of LLM inference — prefill and decode — and to identify which system constraint each mode exposes. We should be able to compute the bandwidth and FLOP demands of a given workload, compare them against real hardware limits, and understand why decode is HBM-bandwidth-bound while prefill is compute-bound. This distinction directly shapes architectural decisions: whether we need more GPUs, whether we can disaggregate prefill from decode, and how we size memory and compute in a fleet. After this chapter we should see inference not as a single monolithic cost but as two opposite-bound processes that require different levers.

## 1. Concept

Inference is the process of turning a sequence of input tokens into a sequence of output tokens using a trained neural network. In an autoregressive model, every generated token requires a fresh forward pass, but the computation split between the prefix (the prompt) and the suffix (the generated output) is fundamentally different.

**Prefill** is the first pass over the prompt. The model reads every token of the input context, computes attention over the entire prefix, and produces the first output token. During prefill, the model attends over all input positions, so the work grows with the square of the context length.

**Decode** is the per-token generation that follows. After prefill, each new token only attends to the cached keys and values from the prefix plus all previously generated tokens. The per-step cost is constant in context length — we only attend to the new token against the cache — but it requires reading the entire model weight matrix from HBM every step, because the auto-regressive pass reuses the same parameters over and over.

The critical architectural insight: prefill is dominated by FLOPs (matrix-multiply arithmetic), while decode is dominated by HBM memory bandwidth (reading 140 GB of weights 40 times a second). These are opposite bottlenecks, and confusing them is the most common architectural misstep.

## 2. Mental Model

Think of inference as two gears turning at different speeds. The prefill gear is large and toothed: it does a lot of work per revolution (many FLOPs), but it only turns once per request. The decode gear is small and smooth: it turns every token, doing relatively little work per step, but it keeps turning for every output token. The prefill gear is limited by how fast the compute engines can crank (FLOPS); the decode gear is limited by how fast data can be fed from memory (GB/s). When we ask "is this workload compute-bound or bandwidth-bound?" the answer depends entirely on which gear is doing the work.

A useful concrete image: prefill is like filling a bucket from a fire hose — a burst of high-rate flow that fills the entire capacity in one go. Decode is like drinking from that bucket one sip at a time — each sip is small, but we keep sipping until the bucket is empty. The hose is limited by pipe width (bandwidth); the sips are limited by cup size and swallowing rate (compute).

## 3. Worked Example

To make the distinction concrete, let us walk through the canonical enterprise Q&A scenario from §14: a 70B-class dense model in FP16, 1 host with 8 × H100 GPUs, prompt of 1,200 tokens + 8K retrieved context (~9.2K input), 300-token output, TTFT budget 1.2 s (retrieval ~120 ms + prefill), TPOT budget ~25 ms/token. All numbers are derived from the canonical scenario; none are measurement claims.

### Table 2-1 — Decode bandwidth and prefill FLOPs (worked example, not reference)

| metric | value | derivation |
|---|---|---|
| Model params | 70B | §14 canonical |
| Model weight bytes (FP16) | 140 GB | 2 bytes × 70B params [1P DERIVED] |
| Decode: weight-read per token | 140 GB | Auto-regressive: one read of all weights per generated token [1P DERIVED] |
| Decode: required bandwidth (TPOT ~25 ms) | 5.6 TB/s | 140 GB / 0.025 s [DERIVED] |
| H100 HBM3 peak bandwidth | 3.35 TB/s | NVIDIA H100 specs [2° FACT] |
|| Decode: bandwidth verdict | bandwidth-bound | 5.6 > 3.35 → single H100 cannot meet the demand [2° DERIVED] |
| Prefill: input tokens | 9,200 | 1,200 prompt + 8K context [1P DERIVED] |
| Prefill: FLOPs (2 × params × tokens) | 1.29 PFLOP | 2 × 70e9 × 9.2e3 ≈ 1.29 × 10^15 [DERIVED] |
| H100 BF16 dense compute | 989 TFLOPS | NVIDIA H100 BF16 tensor-core peak [2° FACT] |
| Prefill: compute verdict | compute-bound | 1.29 PFLOP / ~1.08 s ≈ 1.19 PFLOPS > 0.989 PFLOPS peak → single H100 insufficient for real-time prefill [DERIVED] |

![Fig 2.1 — Decode vs prefill: bandwidth vs compute [ILLUSTRATIVE conceptual]](figures/fig-02-0201.png)

*Fig 2.1 — Decode is HBM-bandwidth-bound (5.6 TB/s vs H100 3.35 TB/s); prefill is compute-bound (~1.19 PFLOPS required vs H100 0.989 PFLOPS peak).*

**Worked example arithmetic details:**

- **Decode bandwidth.** In auto-regressive decode, generating one token requires a full forward pass of the 70B parameter matrix. At FP16 (2 bytes per parameter), the weight footprint is $W = N \times 2 = 140$ GB. With a TPOT budget of ~25 ms per token, the system must read all $W$ bytes in $\tau = 0.025$ s, so the required bandwidth is

$$
B_\text{req} = \frac{W}{\tau} = \frac{140 \text{ GB}}{0.025 \text{ s}} = 5{,}600 \text{ GB/s} = 5.6 \text{ TB/s}
$$

[2° DERIVED]. A single NVIDIA H100 HBM3 delivers ~3.35 TB/s peak bandwidth [2° FACT]. Since $5.6 > 3.35$, one H100 cannot supply the required weight-read rate — the decode phase is HBM-bandwidth-bound [2° DERIVED], and serving 70B-class output requires multi-GPU scaling or bandwidth-increasing topologies (e.g.
NVLink-connected nodes).

- **Prefill FLOPs.** The prefill pass computes attention over the 9.2K input tokens and produces the first output token. The FLOP count for a dense transformer forward pass is well approximated as $2 \times \text{params} \times \text{tokens}$ (the factor of 2 accounts for multiply-add per parameter per token). Thus:

$$
\text{prefill FLOPs} = 2 \times N \times L = 2 \times 70 \times 10^9 \times 9.2 \times 10^3 \approx 1.288 \times 10^{15} \approx 1.29 \text{ PFLOP}
$$

[2° DERIVED]. An NVIDIA H100 delivers ~989 TFLOPS (BF16 dense tensor-core peak) [2° FACT], which is 0.989 PFLOPS. The required rate against the ~1.08 s prefill budget is

$$
\text{rate} = \frac{1.29 \text{ PFLOP}}{1.08 \text{ s}} \approx 1.19 \text{ PFLOPS}
$$

Crossing $1.19 > 0.989$ — a single H100 cannot execute the prefill FLOPs within the TTFT budget; the prefill phase is compute-bound [2° DERIVED]. Multiple GPUs (model parallelism or data parallelism) or more efficient attention implementations are required to meet the latency SLO.

## 4. Measurement

How do we know whether a given workload is prefill-bound or decode-bound in practice? Three practical measurements:

1. **Divide the TTFT into retrieval + prefill.** Measure the retrieval latency (vector search, document fetch) separately from the prefill latency (prompt processing). In the canonical scenario, retrieval takes ~120 ms, leaving ~1.08 s for prefill on a 9.2K-token prompt. If prefill exceeds this budget, the bottleneck is compute or memory, not retrieval.

2. **Log TPOT per token across the request.** Track the time-per-token for the generated output. If TPOT is ~25 ms and does not decrease as the output lengthens (because the KV cache amortizes the attention over the prefix), the per-step cost is constant — consistent with decode being bandwidth-bound (same weights read each step). If TPOT drops with longer contexts, the model may be compute-bound per step (attention over more keys/values adds FLOPs).

3. **Measure actual HBM utilization vs FLOP utilization.** Using GPU profilers (NVIDIA Nsight, vLLM stats), watch the fraction of peak HBM bandwidth consumed versus the fraction of peak FLOPS consumed. If HBM utilization is near 100% while FLOPS utilization is low, the kernel is bandwidth-bound (typical of decode). If FLOPS utilization is near 100% while HBM utilization is low, the kernel is compute-bound (typical of prefill).

These measurements cost nothing but a profiler attach and a few representative requests — and they prevent the architect from applying the wrong optimization lever.

## 5. Common Mistakes

- **Treating prefill and decode as the same bottleneck.** The most dangerous mistake is assuming that what slows prefill will also slow decode, or vice versa. Prefill FLOPs scale with input length; decode bandwidth is constant per token. Confusing the two leads to over-provisioning compute for a bandwidth-bound workload, or under-provisioning compute for a compute-bound one.

- **Assuming one H100 suffices for 70B inference.** The arithmetic in Section 4 shows that a single H100 cannot meet the decode bandwidth demand (5.6 TB/s vs 3.35 TB/s) nor the prefill compute demand (1.29 PFLOP vs 0.989 PFLOPS). Attributing 70B serveability to a single GPU ignores the opposite bottlenecks and produces an architecture that fails latency SLOs.

- **Ignoring the input/output token asymmetry.** A workload with 9.2K input tokens and 300 output tokens spends the great majority of its latency and energy in prefill, not decode. Quoting only throughput per second or only per-token latency hides that the two legs of the request have different cost structures and different optimization paths.

- **Using manufacturer-peak bandwidth/FLOPS without mapping to real kernels.** H100 3.35 TB/s HBM3 is the theoretical peak; actual sustained bandwidth for weight-read kernels may be 60–80% of peak. H100 989 TFLOPS BF16 dense is the tensor-core peak; actual matmul throughput depends on kernel fusion, batching, and precision. Citing raw numbers without kernel context is an anti-catalog error — the number must be matched to the actual serving kernel in use.

## 6. Architecture Consequence

The opposite bottlenecks of prefill and decode have immediate architectural consequences:

- **Prefill is compute-bound → optimization levers:** kernel fusion (flash-attention, scaled-dot-product attention with fewer reads), model parallelism (splitting the 70B parameters across GPUs), more GPUs in parallel, quantization (FP8/BF16 reduces FLOP count and memory traffic), or prefill-specific servers that dedicate hardware to the bursty preload phase.

- **Decode is bandwidth-bound → optimization levers:** continuous batching (vLLM, PagedAttention) to amortize weight reads across many tokens in flight, KV cache offloading to SSD or system memory, P/D (prefill/decode) disaggregation (separate pools of GPUs for prefill bursts vs. decode steady state), and higher-bandwidth memory topologies (NVSwitch, HBM3e).

The key architectural decision this enables: **can we disaggregate prefill and decode onto different hardware?** If prefill needs more FLOPS and decode needs more bandwidth, a single homogeneous GPU pool is suboptimal. A two-pool architecture — a prefill cluster optimized for compute (more GPUs, higher FLOPS) and a decode cluster optimized for bandwidth (faster HBM, larger NVLink domains) — can achieve the same serving SLO with fewer total GPUs than a homogeneous design. This is the central theme of Chapter 11 (Serving) and Pattern 4 (Prefill/decode disaggregation).

## 7. What We Still Don't Know

- **Sustained HBM bandwidth for weight-read kernels.** The 3.35 TB/s H100 figure is a theoretical peak; real serving kernels (vLLM, TGI, transformer-engine) may achieve different sustained rates depending on kernel fusion, graph optimization, and batch size. [VERIFY HYPOTHESIS] — measure on real hardware before citing.

- **Prefill FLOP cost per token under continuous batching.** The 2 × params × tokens approximation ignores that continuous batching reuses activations across requests, potentially reducing the effective FLOP count per request. The magnitude of this effect at fleet scale is not yet pinned down. [VERIFY HYPOTHESIS] — benchmark with realistic concurrency patterns.

- **Cross-technology bandwidth numbers.** HBM3e (next-generation) promises ~6+ TB/s per GPU, and AMD MI300X promises ~5.3 TB/s. How these compare to the 5.6 TB/s decode demand shifts the GPU count equation but does not change the fundamental bandwidth-bound vs compute-bound classification. [2° FACT] — vendor-published numbers, verify against the specific generation in use.

- **Effect of quantization on decode bandwidth vs prefill FLOPs.** Int4 or FP8 quantization reduces the weight bytes (e.g., 70B at FP8 = 70 GB instead of 140 GB) and may change the FLOP arithmetic (8-bit matmuls may use tensor cores at different utilization). The direction of the shift is clear (both bottlenecks improve), but the precise trade-off point where decode becomes compute-bound rather than bandwidth-bound depends on the quantization scheme and hardware support. [VERIFY HYPOTHESIS] — workload-dependent.

## 8. End-of-Chapter Mini-Case

The architect is still in the early design conversation about the internal Q&A tool described in Chapter 1. The team has settled on a 70B-class dense model for accuracy, and they have a rough traffic estimate: ~2,000 registered employees, each roughly as active as the canonical scenario (~10 requests/s average, peaks ~40 rps), with prompts of ~1,200 tokens of internal documents plus ~8K retrieved context and ~300 tokens of answer.

From the token layer alone, the architect can already state the hard numbers: each request carries ~9.2K input tokens and ~300 output tokens. At 10 rps average, the system must sustain ~92,000 input tokens/s in prefill and ~3,000 output tokens/s in decode. At 40 rps peak, those numbers jump to ~368,000 and ~12,000 respectively. The architect can also state the two opposite bottlenecks: prefill will be compute-bound (~1.29 PFLOP per request at 9.2K input), and decode will be bandwidth-bound (~5.6 TB/s required weight-read rate per token). The team's immediate architectural choice is whether to build a single homogeneous GPU cluster or to separate prefill and decode pools — the arithmetic from this chapter makes clear that a homogeneous design will be suboptimal for either bottleneck, and that the disaggregation option explored in Chapter 11 is worth evaluating early.

Before passing this workload to Chapter 4 (workload anatomy), the architect locks in one more number: the tokens-per-request split. This is the currency every downstream chapter will price against, and it has already been established as ~9.2K input + ~300 output per request. The rest of the design — model fitting, memory budget, latency budget, cost — can now proceed in token-denominated terms.