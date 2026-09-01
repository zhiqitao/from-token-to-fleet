# Chapter 8 — Compute

## The Architect's Question

After chapters on tokens, workloads, and memory, the architect naturally asks: *how much compute does this actually require, and at what point does the hardware cease to be the limiting factor?* This chapter gives us the FLOP-scale arithmetic, the arithmetic-intensity roofline, and the utilization framework that lets us answer that question without guessing. We will move from per-token FLOPs to prefill PFLOP counts to sustained MFU on real hardware, and then to the roofline that tells us whether a given layer is compute-bound or memory-bound — the difference that decides whether we should reach for batching, quantization, or a different hardware generation. Throughout, the arithmetic anchors to the canonical enterprise-Q&A RAG scenario (§14): ~10 rps average / ~40 rps peak traffic (2,000 registered users × 5% concurrency → 100 concurrent → ~10 rps via Little's Law; peaks at 20% concurrency → ~40 rps), with 70B FP16 weights and an 8×H100 host. KV-cache per-token figures are referenced at FP16 (~2.5 MB/token) unless an 8-bit (~1.3 MB/token) variant is explicitly stated.

## 1. Concept

Compute in a language model is priced in floating-point operations, or FLOPs. Every matrix multiplication, every attention weight update, every activation function evaluation contributes to the total. The architect's first principle is that FLOPs scale linearly with parameter count and context length, but the *efficiency* with which those FLOPs are executed depends on the hardware ridge point and the arithmetic intensity of the kernel.

For a dense transformer layer, the dominant cost is the matrix multiplication — query-key, value-aggregation, and MLP projections. In FP16, a single multiply-add counts as two FLOPs. The per-token cost is therefore approximately 2 × N FLOPs where N is the number of active parameters. This is the arithmetic baseline: every token processed costs roughly two floating-point operations per parameter.

But FLOPs alone do not tell the full story. The hardware can only execute FLOPs if data is available — weights, activations, and KV cache all compete for the same HBM bandwidth. The arithmetic intensity (FLOP/byte) determines whether a kernel is compute-bound (intensity above the ridge point) or memory-bound (intensity below). This roofline model is the central diagnostic tool of this chapter: it tells us, for any given layer and precision, whether increasing FLOPs will actually reduce latency or whether we are already starved for bytes.

The chapter unfolds in four parts. First, the core arithmetic: FLOPs per token, prefill PFLOP counts, and H100 sustained utilization. Second, the roofline: why early layers are compute-bound while later layers and decode are memory-bound. Third, the canonical scenario arithmetic: 70B on 8 × H100, TTFT 1.2 s, TPOT ~25 ms. Fourth, the mini-case: a continuous deployment scenario that threads the prefill/decode divide.

## 2. Mental Model

Think of FLOPs as the distance a car can travel on a gallon of fuel: it tells us the system's capacity, not how long the trip will take. The trip time is determined by the ridge point: if the arithmetic intensity is below the ridge, adding more FLOPs won't help because we are waiting for data. If we are above the ridge, we are limited by how fast the compute can chew through operations. The roofline chart — peak TFLOPS on the vertical axis, FLOP/byte on the horizontal — is the map that resolves this. Where our kernel lands on that chart decides whether we should profile memory bandwidth or compute throughput.

## 3. Worked Example: Canonical Scenario Arithmetic

The canonical scenario (§14, book-architecture.md) is an enterprise Q&A system: 70B-class dense model, FP16 weights (~140 GB), 1 host with 8 × H100-class GPUs (80 GB each), ~10 requests/s average, peaks ~40 rps, average prompt 1,200 tokens + 8K retrieved context (~9.2K input), 300-token output, TTFT budget 1.2 s (retrieval ~120 ms + prefill), TPOT budget ~25 ms/token.

### FLOPs per token

For a 70B-parameter dense model in FP16, the per-token forward FLOP count is approximately:

$$
\text{FLOP/}_{\text{token}} \approx 2 \times N = 2 \times 70 \times 10^9 \approx 140 \text{ GFLOP/token}
$$

[DERIVED: 2 FLOPs/parameter × 70 × 10⁹ params; standard dense-forward arithmetic, consistent with the 175B ≈ 0.35 TFLOP/token correction from moe-vs-dense E5]

This applies to both prefill and decode: each token that enters the forward pass costs ~140 GFLOP. The distinction between prefill and decode is not in the per-token FLOP count but in the data movement pattern — preflight reads the full context once, while decode re-reads weights per token.

### Prefill PFLOP for 9.2K input

For a single request with 9.2K input tokens, the prefill FLOP cost is:

$$
\text{prefill FLOPs} \approx 2 \times N \times L = 2 \times 70 \times 10^9 \times 9.2 \times 10^3 \approx 1.29 \text{ PFLOP}
$$

[DERIVED: 2 × N × L where N=70B, L=9,200; reconciles with Ch.2 scaling law if the full 14.8T-token pre-train budget is distributed across active parameters; the figure is large because the full context is attended to, but it is a one-time cost per request, not a sustained rate]

*Accuracy of the 2 × N × L approximation.* This linear prefill count omits the quadratic attention term, $\approx 4 \times n_\text{layers} \times L^2 \times d$. At the canonical 9.2K context that correction is small — roughly **+17%** of the 1.29 PFLOP — so the 2NL roofline is a sound teaching baseline there. But the omission grows with context: at 32K the attention term is ~**+60%** and at 128K it *dominates* (~2.4× the linear term). An architect sizing long-context prefill must add the quadratic term or measure it; the Unknowns section returns to this.

At 10 requests/s, the sustained prefill throughput demand is:

$$
\text{prefill demand} = 1.29 \times 10^{15} \text{ FLOP} \times 10 \text{ rps} \approx 12.9 \text{ PFLOP/s}
$$

[DERIVED]

**Table 8-1** — Per-token FLOP cost and prefill PFLOP for the canonical 70B workload. *(Per-token FLOP and prefill PFLOP computations are [2° DERIVED] from 2 × params × tokens; hardware peaks [1P: vendor datasheet] or [2° FACT]; the 30–40% MFU range is [2°: industry benchmarks]; the ~295 FLOP/byte ridge is [2° DERIVED] = 989 TFLOPS ÷ 3.35 TB/s.)*  | metric | value | derivation |

| metric | value | derivation |
|---|---|---|
| per-token FLOPs (forward) | ~140 GFLOP/token | 2 × 70B params [DERIVED; consistent with moe-vs-dense E5 correction: 175B ≈ 0.35 TFLOP/token] |
| prefill FLOPs for 9.2K input | ~1.29 PFLOP | 2 × 70 × 10⁹ × 9.2 × 10³ [DERIVED] |
| sustained prefill demand @ 10 rps | ~12.9 PFLOP/s | 1.29 PFLOP × 10 [DERIVED] |
| H100 peak FP16 TFLOPS | ~989 TFLOPS [1P: facts/training.md T5] | NVIDIA H100 SXM5 datasheet, without sparsity |
| H100 sustained MFU (typical) | 30–40% [2°: industry benchmarks] | ~346 TFLOPS sustained at 35% MFU |
| H100 ridge point (dense FP16) | ~295 FLOP/byte | 989 ÷ 3.35 [DERIVED: peak TFLOPS ÷ HBM bandwidth] |

*All figures trace to the canonical scenario (§14) and validated old-repo sources; none are measurement claims.*
This is the prefill compute demand. An 8 × H100 node can sustain some fraction of this at MFU (mixed-precision FLOP utilization), which we estimate next.

### Sustained vs. peak: H100 MFU

NVIDIA H100 SXM5 lists ~1,979 TFLOPS FP16 Tensor Core peak "with sparsity" and ~989 TFLOPS FP16 peak without sparsity [1P: facts/training.md T5, NVIDIA datasheet]. In practice, sustained mixed-precision FLOP utilization (MFU) for a well-tuned transformer workload typically runs at 30–40% of peak on H100 [2°: industry benchmark reports, derived from real kernel profiles]. At 35% MFU:

$$
\text{sustained} = \text{peak} \times \text{MFU} = 989 \text{ TFLOPS} \times 0.35 \approx 346 \text{ TFLOPS}
$$

[DERIVED: peak × typical MFU]

At 346 TFLOPS sustained, the number of tokens/s the system can prefill is:

$$
\text{prefill tokens/s} = \frac{\text{sustained}}{\text{FLOP/}_{\text{token}}} = \frac{346 \text{ TFLOPS}}{140 \text{ GFLOP/token}} \approx 2{,}471 \text{ tokens/s}
$$

[DERIVED: sustained FLOPS ÷ per-token FLOPs]

For 10 rps with 9.2K input tokens each, the prefill demand is ~92,000 tokens/s (from the canonical workload). At 2,471 tokens/s per node, we would need roughly:

$$
n_\text{nodes} = \frac{\text{tokens/s demand}}{\text{tokens/s per node}} = \frac{92{,}000}{2{,}471} \approx 37 \text{ nodes}
$$

[DERIVED: token demand ÷ per-node prefill throughput]

This rough sizing illustrates that prefill is FLOP-bound at this scale — the compute requirement is the primary constraint, and memory bandwidth (HBM at 3.35 TB/s per H100) is sufficient to keep the compute fed if the kernel is efficient. The ridge point for dense FP16 on H100 is ~295 FLOP/byte (989 ÷ 3.35); the arithmetic intensity of a mature attention kernel sits near or above this ridge, meaning the kernel is compute-saturated rather than bandwidth-starved once the batch is large enough.

### Decode: bandwidth-bound at low batch

![Fig 8.1 — Prefill above the ridge (compute-bound), decode below it (memory-bound). H100 (solid) vs H200 (dashed) ridge points from vendor datasheets (989 TFLOPS, 3.35 / 4.8 TB/s); Continuous-Batching arrow shows decode climbing the slope as batch grows [2° DERIVED; H100/H200 peaks [1P: vendor datasheet]](figures/fig-08-0801.png)

*Fig 8.1 — The roofline: prefill is compute-bound, low-batch decode is memory-bound.*

<!-- Figure spec: mechanism-first roofline diagram; arithmetic intensity on x-axis, achievable FLOP/s on y-axis, ridge line where FLOP-bound meets byte-bound; label the prefill and decode operating points. -->

For decode, the per-token FLOP cost is the same ~140 GFLOP, but the arithmetic intensity drops sharply. Each decoded token re-reads all 70B weights from HBM. A 70B FP16 weight matrix is 70 × 10⁹ × 2 B = 140 GB — one full pass reads **140 GB**, not 280 GB. (The naïve “2 × 70 × 10⁹ × 2 B ≈ 280 GB” double-counts the FP16 footprint: the leading “2” is already inside the 2-bytes-per-element, so writing 2 × 70 × 10⁹ × 2 B counts the weight bytes twice. Any KV/output-projection reads are a separate, smaller term on top, not a second full weight footprint.) The effective arithmetic intensity is therefore:

$$
\text{arithmetic intensity}_{\text{decode}} \approx \frac{140 \text{ GFLOP}}{140 \text{ GB}} \approx 1.0 \text{ FLOP/byte}
$$

[DERIVED; a lower-bound bandwidth model — real kernels also read activations and KV, so measured intensity is typically below this and heavily dependent on fusion and cache residency]

This is well below the H100 dense-FP16 ridge of ~295 FLOP/byte, meaning single-stream decode is overwhelmingly memory-bandwidth-bound. Throughput improves with batching because the weight-reread amortizes across tokens — at batch=32, the effective intensity rises toward the ridge, and TFLOP/s utilization increases accordingly. This is why continuous-batching systems (Orca, vLLM) prioritize batch growth: it is the primary lever for pushing decode arithmetic intensity toward the ridge.

## 4. Measurement

Three measurable quantities anchor compute sizing:

1. **Per-token FLOP count.** Measure by flops profiling (e.g. NVIDIA Nsight Compute) on the target model and precision. The 2×N rule is a useful prior, but actual count varies by layer depth, activation choice (SiLU vs. ReLU), and whether kernel fusion combines matmuls.

2. **Sustained MFU.** Profile TFLOP/s achieved divided by peak TFLOP/s for the target hardware and precision. A well-tuned transformer on H100 FP16 typically lands in the 30–40% range; below 20% suggests a memory or communication bottleneck that should be diagnosed before scaling.

3. **Arithmetic intensity (FLOP/byte).** Compute as achieved FLOPs divided by bytes transferred (weights + activations + KV read/write). Compare to the hardware ridge point (H100 dense FP16: ~295 FLOP/byte; H200: ~989 TFLOPS ÷ 4.8 TB/s ≈ 206 FLOP/byte — H200 keeps H100's GH100 die and its dense FP16 peak, trading a bigger/faster HBM3e for bandwidth; GB200 BF16: much higher due to NVFP4). If intensity is below the ridge, the kernel is memory-bound; above, compute-bound.

## 5. Common Mistakes

- **Assuming 2×N FLOPs/token is exact.** It is a baseline derivation; actual per-token FLOPs vary with layer depth, activation fusion, and kernel fusion. Profile before quoting.

- **Treating prefill and decode as having the same FLOP/byte profile.** Prefill reads the full context once and is FLOP-bound; decode re-reads weights per token and is memory-bound. The arithmetic-intensity roofline distinguishes them.

- **Using peak TFLOP/s as sustained throughput.** Peak includes sparsity or BF16/FP8 variants that may not be available in the chosen precision. Use the FP16 number without sparsity (≈989 TFLOPS on H100) as the baseline for dense compute sizing.

- **Ignoring the batch-size dependence of arithmetic intensity.** A single-token decode batch has very low intensity; batching raises it. Always state the batch assumption when reporting TFLOP/s or tokens/s.

- **Confusing H100 sparsity-inclusive peak (1,979 TFLOPS) with dense peak (989 TFLOPS).** The 2× sparsity figure appears in vendor data sheets but most transformer workloads do not activate sparsity. Quote the dense figure unless the kernel is specifically sparsity-enabled.

## 6. Architecture Consequence

The compute arithmetic and roofline have direct consequences for system design:

- **If prefill is FLOP-bound** (as it is for 70B+ models with long contexts), the primary optimization is batching — larger prefill batches amortize the context attention cost across more requests, raising arithmetic intensity and increasing TFLOP/s utilization. System design should therefore provision for batchable prefill (continuous batching, Orca, vLLM continuous batching) as the first-order throughput lever.

- **If decode is memory-bound** (single-stream, low batch), the primary optimization is batching — even modest batch sizes (8–16) raise arithmetic intensity toward the ridge, improving TFLOP/s utilization. KV cache quantization (FP8, int8) also reduces bytes per token, raising effective intensity. P/D disaggregation (prefill on GPUs, decode on a separate pool) can rebalance: prefill’s FLOP demand is served by compute-optimized GPUs, while decode’s bandwidth demand is served by wide-memory GPUs or even CPU offload.

- **If the ridge point is exceeded** (e.g. H200 with 4.8 TB/s HBM3e and 4 PFLOPS FP8, giving a ~833 FLOP/byte ridge in FP8), the same workload may shift from memory-bound to compute-bound, changing the optimal hardware choice. This is why the H200 represents a inflection point where inference and training hardware lines begin to converge [1P: facts/training.md T5].

In practice, the architect measures arithmetic intensity for the target workload and precision, locates the kernel on the roofline chart, and then selects hardware and batching strategy accordingly. The roofline is the diagnostic; the architecture decision follows.

## 7. What We Still Don't Know

- **Arithmetic intensity of fused kernels.** Most roofline estimates treat attention or MLP as separate matmuls, but in practice frameworks fuse multiple operations into a single kernel. The effective FLOP/byte of a fused attention+MLP kernel is not well cataloged in primary sources and would require profiling on the target hardware to anchor.

- **MFU across precisions and sparsity.** The 30–40% H100 FP16 figure is a rule of thumb; actual utilization depends on architecture, kernel quality, and batch config. A systematic MFU atlas across H100/H200/GB200, FP16/BF16/FP8, dense/MOE would be a valuable reference.

- **Arithmetic intensity of emerging attention mechanisms.** Linear attention (DeltaNet, MLA), compressed attention (CSA, HCA), and hybrid sparse patterns have different FLOP profiles and data movement. Their roofline position is not yet established in primary sources.

- **Frontier 2026 has begun to answer this.** DeepSeek-V4's hybrid CSA+HCA attention reports that, at 1M-token context, single-token inference drops to ~27% of the FLOPs (Pro) / ~10% (Flash) and KV cache to ~10% / ~7% of DeepSeek-V3.2 [1P: arXiv 2606.19348]. GLM-5.3-Flash's sparse+linear hybrid reports a ~3× attention-compute and ~4.4× KV-cache reduction [1P: HF zai-org/GLM-5.3-Flash]. These are [1P] first-party vendor figures, not yet independently reprofiled on our own hardware — which is exactly the arithmetic-intensity measurement an architect should still do before trusting a vendor's roofline claim for their own workload.

- **How quantization shifts the ridge.** Moving from FP16 to FP8/int8 changes peak TFLOP/s and bytes-per-operand, shifting the ridge point. The net effect depends on the quantization scheme (element-wise vs. per-tensor, dynamic vs. static) and whether the kernel is re-tuned for the lower precision.

## 8. End-of-Chapter Mini-Case: Continuous Deployment Scenario

An architect is brought into an ongoing deployment of a 70B-class Q&A system on 8 × H100 GPUs. The system is serving ~10 requests/s average with ~9.2K input + 300 output tokens per request, and the TTFT budget is being missed: p95 TTFT is 2.8 s, exceeding the SLO of 2 s. The TPOT of 28 ms/token is within spec, but the prefill delay is the bottleneck.

The architect first profiles the arithmetic intensity of the prefill kernel. The per-token FLOP count is ~140 GFLOP (2 × 70B), and the effective bandwidth per token is ~140 GB (re-reading the 70B weight matrix from HBM for each of the 9.2K input tokens). This gives an effective FLOP/byte of roughly 140 GFLOP ÷ 140 GB ≈ 1 FLOP/byte — well below the H100 dense-FP16 ridge of ~295 FLOP/byte. The kernel is strongly memory-bound during prefill.

The immediate question: why is prefill memory-bound when the H100 has 3.35 TB/s HBM3 bandwidth? The answer is that a 9.2K input context means each prefill pass reads the full weight matrix once, but the activation keys/values for 9.2K tokens also flow through the pipeline. The total bytes per token are higher than the weight-read alone, and the effective intensity drops further.

The architect's first fix is to increase the prefill batch size. Continuous batching (vLLM Orca-style) accumulates incoming requests into larger batches, which raises the effective arithmetic intensity because the weight matrix read is amortized across more tokens. At batch=32, the effective intensity rises to ~2–3 FLOP/byte, still below the ridge but much closer. At batch=128, the intensity approaches the ridge and TFLOP/s utilization climbs from ~15% to ~45%.

The second fix is to profile the actual MFU achieved. If the system is running at 12% MFU on prefill, there is headroom to absorb more batch without adding hardware. If MFU is already near 40%, the bottleneck is elsewhere (communication, kernel inefficiency, or KV cache residency), and simply batching harder yields diminishing returns.

The architect's recommendation: enable continuous batching with a target batch size of 64–128, profile the resulting MFU and TTFT, and if TTFT remains above SLO, consider P/D disaggregation — offload decode to a separate pool of GPUs with wide HBM bandwidth, freeing the prefill GPUs to run larger batches at higher FLOP utilization. The key insight is that the workload's position on the roofline chart (memory-bound prefill) dictates the fix: batching to raise intensity, or hardware that raises the ridge point (H200, GB200), or disaggregation that separates the two bottleneck profiles.

***

*Reading the roofline (summary of Fig 8.1): the dense-FP16 ridge at ~295 FLOP/byte (H100: 989 TFLOPS ÷ 3.35 TB/s) separates the compute-bound region (right) from the memory-bound region (left). Prefill kernels typically operate in the 1–3 FLOP/byte range for long contexts, decode kernels near 1.0 FLOP/byte at batch=1; batching and quantization shift kernels rightward toward the ridge.*

*Prefill PFLOP also grows with context: 2 × 70B × L tokens, from 2K to 32K. This is the one-time compute cost of loading a long context; sustained throughput (tokens/s) is what matters for continuous serving, and at the canonical 9.2K point it is ~1.29 PFLOP (Table 8-1).*