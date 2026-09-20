# Chapter 8 — Compute

## The Architect's Question

After chapters on tokens, workloads, and memory, the architect naturally asks: *how much compute does this actually require, and at what point does the hardware cease to be the limiting factor?* This chapter gives us the FLOP-scale arithmetic, the arithmetic-intensity roofline, and the utilization framework that lets us answer that question without guessing. We will move from per-token FLOPs to prefill PFLOP counts to sustained MFU on real hardware, and then to the roofline that tells us whether a given layer is compute-bound or memory-bound — the difference that decides whether we should reach for batching, quantization, or a different hardware generation. Throughout, the arithmetic anchors to the canonical enterprise-Q&A RAG scenario (canonical scenario (Ch 4, Table 4-3)): ~10 rps average / ~40 rps peak traffic (2,000 registered users × 5% concurrency → 100 concurrent → ~10 rps via Little's Law; peaks at 20% concurrency → ~40 rps), with 70B FP16 weights and an 8×H100 host. KV cache per-token figures are referenced at FP16 (~2.5 MB/token) unless an 8-bit (~1.3 MB/token) variant is explicitly stated.

## 1. Concept

Compute in a language model is priced in floating-point operations, or FLOPs. Every matrix multiplication, every attention weight update, every activation function evaluation contributes to the total. The architect's first principle is that FLOPs scale linearly with parameter count and context length, but the *efficiency* with which those FLOPs are executed depends on the hardware ridge point and the arithmetic intensity of the kernel.

For a dense transformer layer, the dominant cost is the matrix multiplication — query-key, value-aggregation, and MLP projections. In FP16, a single multiply-add counts as two FLOPs. The per-token cost is therefore approximately 2 ×N FLOPs where N is the number of active parameters. This is the arithmetic baseline: every token processed costs roughly two floating-point operations per parameter.

But FLOPs alone do not tell the full story. The hardware can only execute FLOPs if data is available — weights, activations, and KV cache all compete for the same HBM bandwidth. The arithmetic intensity (FLOP/byte) determines whether a kernel is compute-bound (intensity above the ridge point) or memory-bound (intensity below). This roofline model is the central diagnostic tool of this chapter: it tells us, for any given layer and precision, whether increasing FLOPs will actually reduce latency or whether we are already starved for bytes.

> **Three different "bounds" — keep them apart.** Throughout this book, three words that all contain "bound" mean three different things, and conflating them is a real error. **Compute-bound** means performance is limited primarily by arithmetic throughput (the kernel sits above the ridge; it is starved for FLOPs). **Memory-bandwidth-bound** (what the roofline calls "memory-bound") means performance is limited by memory-transfer bandwidth (the kernel sits below the ridge; it is starved for bytes moving per second). **Memory-capacity-constrained** (equivalently KV-capacity-constrained) means feasible concurrency or context is limited by *how much data fits in HBM* — not by how fast it moves. The canonical RAG workload illustrates all three without overlap: prefill is compute-bound (high intensity), decode is bandwidth-bound (low intensity), and long input raises KV residency, which capacity-constrains how many requests can be resident at once. "Input-heavy" does **not** by itself mean "memory-bound" — it tends to raise prefill compute *and* KV-capacity pressure, two distinct effects. When the book says "memory-bound" without qualification, it means *bandwidth-bound* in the roofline sense; capacity pressure is stated explicitly.

The chapter unfolds in four parts. First, the core arithmetic: FLOPs per token, prefill PFLOP counts, and H100 sustained utilization. Second, the roofline: why early layers are compute-bound while later layers and decode are memory-bound. Third, the canonical scenario arithmetic: 70B on 8×H100, TTFT 1.2 s, TPOT ~25 ms. Fourth, the mini-case: a continuous deployment scenario that threads the prefill/decode divide.

## 2. Mental Model

Think of FLOPs as the distance a car can travel on a gallon of fuel: it tells us the system's capacity, not how long the trip will take. The trip time is determined by the ridge point: if the arithmetic intensity is below the ridge, adding more FLOPs won't help because we are waiting for data. If we are above the ridge, we are limited by how fast the compute can chew through operations. The roofline chart — peak TFLOPS on the vertical axis, FLOP/byte on the horizontal — is the map that resolves this. Where our kernel lands on that chart decides whether we should profile memory bandwidth or compute throughput.

![Fig 8.1 — Where inference computation and data movement actually live. The hierarchy runs from the smallest/fastest/closest resource (registers, tensor cores, on-chip SRAM) to the largest/slower/farther (HBM, GPU interconnect, other GPUs). Inference work maps onto it: matrix multiply runs on the tensor cores; model weights and the KV cache are predominantly HBM-resident; FlashAttention restructures attention to tile through on-chip memory and cut HBM traffic; tensor-parallel communication crosses the GPU interconnect. The gradient of speed↔capacity↔distance is why compute, memory bandwidth, memory capacity and interconnect bandwidth are *distinct* architectural constraints — each is a different level of this ladder. [ILLUSTRATIVE conceptual]](figures/fig-08-0802.png)

*Read this ladder together with the roofline:* the roofline's vertical axis (peak TFLOPS) and horizontal axis (FLOP/byte) are both determined by *where* on this hierarchy the work sits. A kernel is compute-bound when its FLOPs run on the tensor cores and data fits in on-chip memory (high arithmetic intensity); it is bandwidth-bound when it must stream large tensors from HBM faster than the bytes can move (low arithmetic intensity). So the "bound" classification of Ch. 8 is not a property of the model alone — it follows from where the model's weights and the KV cache happen to be resident, and how much of the computation a kernel can keep on-chip. Ch. 15's FlashAttention discussion is exactly this ladder in action: keep more of the tile on-chip, move fewer bytes between HBM and the compute units.

## 3. Worked Example: Canonical Scenario Arithmetic

The canonical scenario (Ch 4, Table 4-3) is an enterprise Q&A system: 70B-class dense model, FP16 weights (~140 GB), 1 host with 8×H100-class GPUs (80 GB each), ~10 requests/s average, peaks ~40 rps, average prompt 1,200 tokens + 8K retrieved context (~9.2K input), 300-token output, TTFT budget 1.2 s (retrieval ~120 ms + prefill), TPOT budget ~25 ms/token.

*Scope.* "1 host with 8×H100" here is a **per-host / per-request** feasibility container (does one host meet one request's latency and memory SLO). It is **not** a claim that one host absorbs the 40 rps peak arrival rate — as Ch 17 derives, that peak puts in-flight concurrency λ·W ≈ 344 at the ~8.6 s service time, far above one host's KV-residency ceiling (C ≈ 18), so the *fleet* needs ~20 hosts. The compute/roofline arithmetic of this chapter answers the per-request and per-host-shard question; the fleet question is a separate multiplication that Ch 16–17 performs. We keep them distinct because each requires measuring against a different quantity (a latency budget vs an arrival rate).

### FLOPs per token

For a 70B-parameter dense model in FP16, the per-token forward FLOP count is approximately:

$$
\text{FLOP/}_{\text{token}} \approx 2 \times N = 2 \times 70 \times 10^9 \approx 140 \text{ GFLOP/token}
$$

[DERIVED: 2 FLOPs/parameter × 70 ×10⁹ params; standard dense-forward arithmetic, consistent with the 175B ≈ 0.35 TFLOP/token correction from moe-vs-dense E5]

This applies to both prefill and decode: each token that enters the forward pass costs ~140 GFLOP. The distinction between prefill and decode is not in the per-token FLOP count but in the data movement pattern — prefill reads the full context once, while decode re-reads weights per token.

### Prefill PFLOP for 9.2K input

For a single request with 9.2K input tokens, the prefill FLOP cost is:

$$
\text{prefill FLOPs} \approx 2 \times N \times L = 2 \times 70 \times 10^9 \times 9.2 \times 10^3 \approx 1.29 \text{ PFLOP}
$$

[DERIVED: 2 ×N × L where N=70B, L=9,200; reconciles with Ch.2 scaling law if the full 14.8T-token pre-train budget is distributed across active parameters; the figure is large because the full context is attended to, but it is a one-time cost per request, not a sustained rate]

*Accuracy of the 2 ×N × L approximation.* This linear prefill count omits the quadratic attention term, $\approx 4 \times n_\text{layers} \times L^2 \times d$. At the canonical 9.2K context that correction is small — roughly **+17%** of the 1.29 PFLOP — so the 2NL roofline is a sound teaching baseline there. But the omission grows with context: at 32K the attention term is ~**+60%** and at 128K it *dominates* (~2.4× the linear term). An architect sizing long-context prefill must add the quadratic term or measure it; the Unknowns section returns to this.

At 10 requests/s, the sustained prefill throughput demand is:

$$
\text{prefill demand} = 1.29 \times 10^{15} \text{ FLOP} \times 10 \text{ rps} \approx 12.9 \text{ PFLOP/s}
$$

[DERIVED]

**Table 8-1** — Per-token FLOP cost and prefill PFLOP for the canonical 70B workload. *(Per-token FLOP and prefill PFLOP computations are [ILLUSTRATIVE][DERIVED] from 2 × params × tokens; hardware peaks [1P: vendor datasheet] or [1P][FACT]; the 30–40% MFU range is [2°: industry benchmarks]; the ~295 FLOP/byte ridge is [2°][DERIVED] = 989 TFLOPS ÷ 3.35 TB/s.)*  | metric | value | derivation |

| metric | value | derivation |
|---|---|---|
| per-token FLOPs (forward) | ~140 GFLOP/token | 2 ×70B params [DERIVED; consistent with moe-vs-dense E5 correction: 175B ≈ 0.35 TFLOP/token] |
| prefill FLOPs for 9.2K input | ~1.29 PFLOP | 2 ×70 ×10⁹ × 9.2 ×10³ [DERIVED] |
| sustained prefill demand @ 10 rps | ~12.9 PFLOP/s | 1.29 PFLOP × 10 [DERIVED] |
| H100 peak FP16 TFLOPS | ~989 TFLOPS [1P: NVIDIA H100 datasheet] | NVIDIA H100 SXM5 datasheet, without sparsity |
| H100 sustained MFU (typical) | 30–40% [2°: industry benchmarks] | ~346 TFLOPS sustained at 35% MFU |
| prefill throughput per GPU | ~2,471 tokens/s | 346 TFLOPS ÷ 140 GFLOP/token [DERIVED; **per-GPU scope**] |
| prefill throughput per host (8×H100) | ~19,800 tokens/s | 8 × 2,471 [DERIVED; **idealized aggregate, before TP/system loss**] |
| H100 ridge point (dense FP16) | ~295 FLOP/byte | 989 ÷ 3.35 [DERIVED: peak TFLOPS ÷ HBM bandwidth] |

*All figures trace to the canonical scenario (Ch 4, Table 4-3) and validated sources; none are measurement claims.*
This is the prefill compute demand. An 8×H100 node can sustain some fraction of this at MFU (mixed-precision FLOP utilization), which we estimate next.

### Sustained vs. peak: H100 MFU

NVIDIA H100 SXM5 lists ~1,979 TFLOPS FP16 Tensor Core peak "with sparsity" and ~989 TFLOPS FP16 peak without sparsity [1P: NVIDIA H100 datasheet]. In practice, sustained mixed-precision FLOP utilization (MFU) for a well-tuned transformer workload typically runs at 30–40% of peak on H100 [2°: industry benchmark reports, derived from real kernel profiles]. At 35% MFU:

$$
\text{sustained} = \text{peak} \times \text{MFU} = 989 \text{ TFLOPS} \times 0.35 \approx 346 \text{ TFLOPS}
$$

[2°][DERIVED: peak × typical MFU — the MFU range is a secondary, empirical figure, so this sustained value inherits the provenance of its weakest input, not the first-party peak]

**Scope matters here.** The 346 TFLOPS figure is the sustained rate of a *single* H100, and the 2,471 tokens/s derived from it is therefore a **per-GPU** number. The canonical host is an *8×H100* node, so we must not multiply demand by a per-GPU rate as if it were per-node. Track the scope explicitly as we scale.

Per **GPU** (one H100 at 35% MFU):

$$
\text{prefill tokens/s (per GPU)} = \frac{346 \text{ TFLOPS}}{140 \text{ GFLOP/token}} \approx 2{,}471 \text{ tokens/s}
$$

[DERIVED: sustained FLOPS ÷ per-token FLOPs; **per-GPU scope**]

Per **host** (8×H100, idealized before TP communication, imbalance, and kernel/system overhead):

$$
\text{prefill tokens/s (per 8×H100 host)} = 8 \times 2{,}471 \approx 19{,}800 \text{ tokens/s}
$$

or, equivalently, `8 × 346 TFLOPS ≈ 2.77 PFLOPS` sustained ÷ 140 GFLOP/token. [DERIVED: per-GPU × 8; **idealized aggregate, first-order only**]

For 10 rps with 9.2K input tokens each, the prefill demand is ~92,000 tokens/s (from the canonical workload). At ~19,800 tokens/s per host, we would need roughly:

$$
n_\text{hosts} = \frac{\text{tokens/s demand}}{\text{tokens/s per host}} = \frac{92{,}000}{19{,}800} \approx 4.6 \to \sim 5 \text{ hosts}
$$

[DERIVED: token demand ÷ per-host prefill throughput; **idealized aggregate**]

At the peak 40 rps (368,000 tokens/s) the same arithmetic gives ~18.6 → **~19–20 hosts**. This aligns — independently — with the KV-residency / Little's-Law fleet sizing derived in Chapters 15–20 (~20 hosts at peak), which is a useful cross-check that the two fundamentally different constraints (prefill FLOP throughput vs. KV residency/service time) point at the same order of fleet.

**Honest boundary on both numbers.** The per-GPU `2,471 tokens/s` is itself an *analytical* figure at an assumed 35% MFU — not a measured throughput. The `8×` aggregate (`~19,800`/host) is a **theoretical first-order estimate** that assumes perfect tensor-parallel scaleout: it does **not** account for TP communication, per-rank load imbalance, kernel inefficiency under a given batch, or scheduling/system overhead. It is an upper-bound analysis value, not a servable goodput. Actual reachable prefill throughput must come from benchmark goodput under the target workload (Chapter 14). Treat both numbers as scope-disciplined *models*, never as measured capacity.

This rough sizing illustrates that prefill is FLOP-bound at this scale — the compute requirement is the primary constraint, and memory bandwidth (HBM at 3.35 TB/s per H100) is sufficient to keep the compute fed if the kernel is efficient. The ridge point for dense FP16 on H100 is ~295 FLOP/byte (989 ÷ 3.35); the arithmetic intensity of a mature attention kernel sits near or above this ridge, meaning the kernel is compute-saturated rather than bandwidth-starved once the batch is large enough.

### Decode: bandwidth-bound at low batch

![Fig 8.2 — Per-GPU roofline for dense FP16, one H100 vs one H200 (a per-GPU chart, not a host-level one). Compute ceiling and HBM bandwidth are single-GPU quantities here (989 TFLOPS, 3.35 / 4.8 TB/s), so the ridge point and the memory-bound slope are per-GPU. Prefill (9.2K input) sits to the right of the ridge, on the compute-bound plateau; decode (batch=1) sits to the left, on the memory-bound slope, and continuous batching climbs the slope as batch grows. The ridge *classification* (compute- vs memory-bound) is unchanged by ideal N-way replication because both peak FLOP/s and HBM bandwidth scale with GPU count; host-level attainable performance additionally depends on sharding and communication. [DERIVED from 1P: vendor datasheet]](figures/fig-08-0801.png)

*The roofline: prefill is compute-bound, low-batch decode is memory-bound.*

<!-- Figure spec: mechanism-first roofline diagram; arithmetic intensity on x-axis, achievable FLOP/s on y-axis, ridge line where FLOP-bound meets byte-bound; label the prefill and decode operating points. -->

For decode, the per-token FLOP cost is the same ~140 GFLOP, but the arithmetic intensity drops sharply. Each decoded token re-reads all 70B weights from HBM. A 70B FP16 weight matrix is 70 ×10⁹ × 2 B = 140 GB — one full pass reads **140 GB**, not 280 GB. (The naïve “2 ×70 ×10⁹ × 2 B ≈ 280 GB” double-counts the FP16 footprint: the leading “2” is already inside the 2-bytes-per-element, so writing 2 ×70 ×10⁹ × 2 B counts the weight bytes twice. Any KV/output-projection reads are a separate, smaller term on top, not a second full weight footprint.) The effective arithmetic intensity is therefore:

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

- **If prefill is FLOP-bound** (as it is for 70B+ models with long contexts), the primary optimization is batching — larger prefill batches do **not** remove the per-request attention work (each sequence still has its own attention computation); they *improve accelerator utilization* by forming larger matrix operations, amortizing weight and execution overhead across requests, and raising achieved FLOP/s. The relevant lever is the achieved efficiency (MFU) of the prefill kernel, not a change to the per-request FLOP count. System design should therefore provision for batchable prefill (continuous batching, Orca, vLLM continuous batching) as the first-order throughput lever.

- **If decode is memory-bound** (single-stream, low batch), the primary optimization is batching — even modest batch sizes (8–16) raise arithmetic intensity toward the ridge, improving TFLOP/s utilization. KV cache quantization (FP8, int8) also reduces bytes per token, raising effective intensity. P/D disaggregation (prefill on GPUs, decode on a separate pool) can rebalance: prefill’s FLOP demand is served by compute-optimized GPUs, while decode’s bandwidth demand is served by wide-memory GPUs or even CPU offload.

- **If the ridge point is exceeded** (e.g. H200 with 4.8 TB/s HBM3e and 4 PFLOPS FP8, giving a ~833 FLOP/byte ridge in FP8), the same workload may shift from memory-bound to compute-bound, changing the optimal hardware choice. This is why the H200 represents a inflection point where inference and training hardware lines begin to converge [1P: NVIDIA H100 datasheet].

In practice, the architect measures arithmetic intensity for the target workload and precision, locates the kernel on the roofline chart, and then selects hardware and batching strategy accordingly. The roofline is the diagnostic; the architecture decision follows.

## 7. What We Still Don't Know

- **Arithmetic intensity of fused kernels.** Most roofline estimates treat attention or MLP as separate matmuls, but in practice frameworks fuse multiple operations into a single kernel. The effective FLOP/byte of a fused attention+MLP kernel is not well cataloged in primary sources and would require profiling on the target hardware to anchor.

- **MFU across precisions and sparsity.** The 30–40% H100 FP16 figure is a rule of thumb; actual utilization depends on architecture, kernel quality, and batch config. A systematic MFU atlas across H100/H200/GB200, FP16/BF16/FP8, dense/MOE would be a valuable reference.

- **Arithmetic intensity of emerging attention mechanisms.** Linear attention (DeltaNet, MLA), compressed attention (CSA, HCA), and hybrid sparse patterns have different FLOP profiles and data movement. Their roofline position is not yet established in primary sources.

- **Frontier 2026 has begun to answer this.** DeepSeek-V4's hybrid CSA+HCA attention reports that, at 1M-token context, single-token inference drops to ~27% of the FLOPs (Pro) / ~10% (Flash) and KV cache to ~10% / ~7% of DeepSeek-V3.2 [1P: arXiv 2606.19348]. GLM-5.3-Flash's sparse+linear hybrid reports a ~3× attention-compute and ~4.4×KV cache reduction [1P: HF zai-org/GLM-5.3-Flash]. These are [1P] first-party vendor figures, not yet independently reprofiled on our own hardware — which is exactly the arithmetic-intensity measurement an architect should still do before trusting a vendor's roofline claim for their own workload.

- **How quantization shifts the ridge.** Moving from FP16 to FP8/int8 changes peak TFLOP/s and bytes-per-operand, shifting the ridge point. The net effect depends on the quantization scheme (element-wise vs. per-tensor, dynamic vs. static) and whether the kernel is re-tuned for the lower precision.

## 8. End-of-Chapter Mini-Case: Continuous Deployment Scenario

An architect is brought into an ongoing deployment of a 70B-class Q&A system on 8×H100 GPUs. The system is serving ~10 requests/s average with ~9.2K input + 300 output tokens per request, and the TTFT budget is being missed: p95 TTFT is 2.8 s, exceeding the SLO of 2 s. The TPOT of 28 ms/token is within spec, but the prefill delay is the bottleneck.

The temptation is to reach for a roofline and "prove" prefill is memory-bound. That reasoning is wrong here, and the error is worth naming: it is spread by treating prefill like token-by-token decode. In decode, each new token re-reads the weight matrix from HBM, so the arithmetic intensity is ~1 FLOP/byte — genuinely memory-bound. In prefill, the weight matrix is read *once* and reused across the whole sequence; the sequence dimension supplies the matrix-matrix reuse. Prefill's effective intensity is `(2 × N × L) / (N × 2 B)` = `L / 1 byte per parameter` ≈ **9,200 FLOP/byte** at the canonical 9.2K context — two orders of magnitude above the ~295 FLOP/byte dense-FP16 ridge. Prefill is compute-bound, exactly as the rest of this chapter teaches.

So a high TTFT is *not* evidence of a bandwidth problem. The architect does the correct thing: profile the prefill kernel and determine which of several distinct causes is actually limiting it, rather than assuming memory. The profile separates four candidates:

- **Compute-bound** — the GEMMs are saturated at high MFU; more FLOPs/ops per token would not help, but better kernel efficiency (flash-attention, fused MLP) would.
- **Communication-bound** — tensor/pipeline parallelism crosses the NVLink/Host fabric; data movement, not math, is the ceiling. The fix is a different parallelization or a smaller cross-GPU footprint.
- **Launch / occupancy-limited** — the kernel is too small or the grid under-fills the SMs; increasing batch or improving occupancy raises utilization without adding hardware.
- **Attention / memory constrained (within prefill)** — the quadratic attention term, not the linear weights, grows with context; at 32K+ contexts this term dominates prefill cost (Table 8-1), so the fix is to reduce the attention term (flash-attention, sparse/linear attention), not to batch harder.

The architect measures MFU to choose among these. If the prefill kernel is running at 12% MFU, the problem is occupancy or launch — grow the batch or fuse kernels. If MFU is already near ~40% and the kernel is compute-saturated, then prefill *is* compute-bound and more batch just queues more work without reducing per-request TTFT; the lever instead is kernel efficiency, attention-term control, or P/D disaggregation so prefill's FLOP profile is served by compute-optimized GPUs while decode's bandwidth profile runs on wide-memory GPUs.

The recommendation is therefore: profile first (MEASURE, do not assume), and only then pick the intervention. Batching helps when prefill is occupancy-limited; kernel fusion helps when GEMMs are under-saturated; attention-term control and disaggregation help when the bottleneck is the quadratic attention term or the compute/bandwidth mismatch between phases. The workload's true roofline position, not an assumed "memory-bound prefill," dictates the fix.

***

*Reading the roofline (summary of Fig 8.2): the dense-FP16 ridge at ~295 FLOP/byte (H100: 989 TFLOPS ÷ 3.35 TB/s) separates the compute-bound region (right) from the memory-bound region (left). Prefill sits far above the ridge — its arithmetic intensity is set by the sequence length (weights read once, reused across all tokens), so it is compute-bound; decode at batch=1 sits just below the ridge (~1 FLOP/byte) and is memory-bound. Batching and quantization shift kernels rightward toward the ridge; the distinction between the two phases is the single most important reading of this chart.*

*Prefill PFLOP also grows with context: 2 ×70B × L tokens, from 2K to 32K. This is the one-time compute cost of loading a long context; sustained throughput (tokens/s) is what matters for continuous serving, and at the canonical 9.2K point it is ~1.29 PFLOP (Table 8-1).*