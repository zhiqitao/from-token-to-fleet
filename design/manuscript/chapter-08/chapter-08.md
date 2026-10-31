# Chapter 8 — Compute

## The Architect's Question

After chapters on tokens, workloads, and memory, the architect naturally asks: *how much compute does this actually require, and at what point does the hardware cease to be the limiting factor?* This chapter gives us the FLOP-scale arithmetic, the arithmetic-intensity roofline, and the utilization framework that lets us answer that question without guessing. We will move from per-token FLOPs to prefill PFLOP counts to sustained MFU on real hardware, and then to the roofline that tells us whether a given layer is compute-bound or memory-bound — the difference that decides whether we should reach for batching, quantization, or a different hardware generation. Throughout, the arithmetic anchors to the canonical enterprise-Q&A RAG scenario (Ch 4, Table 4-2): ~10 rps average / ~40 rps peak traffic, with 70B FP16 weights and an 8×H100 host. KV cache per-token figures are referenced at FP16 (~2.62 MB/token, i.e. 2.5 MiB) unless an 8-bit (~1.31 MB/token, 1.25 MiB) variant is explicitly stated.

## 1. Concept

Compute in a language model is priced in floating-point operations, or FLOPs. Every matrix multiplication, every attention weight update, every activation function evaluation contributes to the total. The architect's first principle is that FLOPs scale linearly with parameter count and context length, but the *efficiency* with which those FLOPs are executed depends on the hardware ridge point and the arithmetic intensity of the kernel.

For a dense transformer layer, the dominant cost is the matrix multiplication — query-key, value-aggregation, and MLP projections. In FP16, a single multiply-add counts as two FLOPs. The per-token cost is therefore approximately 2 ×N FLOPs where N is the number of active parameters. This is the arithmetic baseline: every token processed costs roughly two floating-point operations per parameter.

### Fewer sequential evaluations can mean more total work

*Implementation observations: 2026-10-28. The work counters below are illustrative, not measured performance.*

For an iterative language generator, the approximately 2N projection-cost rule applies to processed positions, not just final output tokens. Let $P_j$ be the active parameter count and $Q_j$ the positions evaluated in network evaluation $j$. A projection-dominated work proxy is

$$F_{\text{projection}} \approx \sum_{j} 2 P_j Q_j.$$

The trace also needs attention pair counts, output-head work, routing, sampling, refresh and verification. For a full dense-attention evaluation over length L, attention work grows quadratically with L. For K active queries over a cached prefix of length C, the attention main term grows with K(C + K), before the architecture's head and layer factors. Reducing the number of recomputed query positions does not eliminate reads of a long prefix. [DERIVED]

Consider an explicitly illustrative 7B-active-parameter model that emits 256 tokens in 32-token blocks and uses eight decoder evaluations per block. There are eight blocks, hence 64 sequential decoder evaluations. The decoder nevertheless evaluates 256 × 8 = 2,048 output positions. Its projection proxy is 2 × 7B × 2,048 = 28.672 TFLOP. A simplified output-only AR counter evaluates 256 positions and gives 3.584 TFLOP. The block example has one quarter as many sequential evaluations but eight times as much output-side projection work. These are different quantities, not contradictory results. [ILLUSTRATIVE][ASSUMPTION][DERIVED]

This arithmetic omits prompt encoding, context attention, block-finalization encoding, the output head, refresh, classifier-free guidance, verification and communication. It also simplifies the book's first-token-from-prefill convention. It compares counters, not equal-quality models, and predicts neither a fourfold speedup nor an eightfold end-to-end slowdown. A network-evaluation count must include extra verification passes and the shapes of any combined guidance branches, rather than count only outer sampler rounds. [DERIVED]

Why might the higher-work path still finish earlier? Processing more positions together can reuse loaded weights across more matrix rows and improve low-batch utilization. Why might it lose under load? Optimized AR request batching can already supply those rows, while refinement continues to repeat work. Distributed execution also repeats tensor-parallel collectives and any expert dispatch required by each evaluation. The number of sequential rounds and the total communicated bytes can move in opposite directions. [DERIVED] The low-concurrency case is vendor-reported rather than re-measured here: Google's DiffusionGemma card reports low-batch generation speed while warning of quality and high-QPS limits ([DiffusionGemma card](https://huggingface.co/google/diffusiongemma-26B-A4B-it/raw/f7f5b7f5fa82ffc52addd066915886d497f5517b/README.md)). [1P][FACT]

MoE adds a working-set issue. Active parameters per token do not equal the union of experts touched by all positions in a parallel block. LLaDA2.2 explicitly limits a block's expert pool before per-token routing ([LLaDA2.2 technical report](https://raw.githubusercontent.com/inclusionAI/LLaDA2.X/main/LLaDA2_2_tech_report.pdf), retrieved 2026-10-28). That bounds an execution working set; it does not make the other resident experts disappear. The useful measurements are expert-union size, dispatch bytes, load imbalance and collective time, alongside active FLOPs. [1P][FACT]; measurement consequence [DERIVED]

The resulting fleet decision follows measured service demand. At a fixed task-quality and latency target, GPU-seconds, successful-request throughput and resident state determine capacity. Output tokens divided by denoising steps do not determine the number of hosts. [DERIVED]


### The roofline diagnostic

But FLOPs alone do not tell the full story. The hardware can only execute FLOPs if data is available — weights, activations, and KV cache all compete for the same HBM bandwidth. The arithmetic intensity (FLOP/byte) determines whether a kernel is compute-bound (intensity above the ridge point) or memory-bound (intensity below). This roofline model is the central diagnostic tool of this chapter: it tells us, for any given layer and precision, whether increasing FLOPs will actually reduce latency or whether we are already starved for bytes.

> **Three different "bounds" — keep them apart.** Throughout this book, three words that all contain "bound" mean three different things, and conflating them is a real error. **Compute-bound** means performance is limited primarily by arithmetic throughput (the kernel sits above the ridge; it is starved for FLOPs). **Memory-bandwidth-bound** (what the roofline calls "memory-bound") means performance is limited by memory-transfer bandwidth (the kernel sits below the ridge; it is starved for bytes moving per second). **Memory-capacity-constrained** (equivalently KV-capacity-constrained) means feasible concurrency or context is limited by *how much data fits in HBM* — not by how fast it moves. The canonical RAG workload illustrates all three without overlap: prefill is compute-bound (high intensity), decode is bandwidth-bound (low intensity), and long input raises KV residency, which capacity-constrains how many requests can be resident at once. "Input-heavy" does **not** by itself mean "memory-bound" — it tends to raise prefill compute *and* KV-capacity pressure, two distinct effects. When the book says "memory-bound" without qualification, it means *bandwidth-bound* in the roofline sense; capacity pressure is stated explicitly.

### A resource model survives a backend change; an implementation may not

*Backend-documentation observations: 2026-10-28. They do not establish feature availability at the edition's 2026-08-30 cutoff.*

The compute and memory equations apply across accelerator vendors. Their constants belong to a specific device and execution path. A peak INT8 dense TOPS figure does not describe BF16 throughput, a sparse peak does not describe a dense workload, and aggregate device memory is not one allocation pool. The useful comparison starts with the model's operators, resident bytes and communication pattern. It then asks which kernels implement those operations on the candidate hardware ([Arc Pro B70 datasheet](https://intel.com/content/dam/www/central-libraries/us/en/documents/2026-03/datasheet-b70-gpu.pdf), [Arc Pro B65 datasheet](https://intel.com/content/dam/www/central-libraries/us/en/documents/2026-03/datasheet-b65-gpu.pdf), [Gaudi 3 Accelerator white paper](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf)). [1P]

In PyTorch, `torch.xpu` names the Intel GPU device backend ([PyTorch XPU getting-started note](https://raw.githubusercontent.com/pytorch/pytorch/5c4886908584029761b579af026dcfb627c84070/docs/source/notes/get_start_xpu.md), pinned revision `5c48869`). It does not name every Intel accelerator. Intel Gaudi uses a separate `hpu` path and software stack ([Gaudi PyTorch porting guide](https://docs.habana.ai/en/latest/PyTorch/PyTorch_Model_Porting/Porting_PyTorch_Models_to_Gaudi.html), which allocates tensors as `torch.device("hpu")`). A client NPU can use the OpenVINO NPU plugin rather than the GPU backend ([OpenVINO GenAI documentation](https://docs.openvino.ai/2026/openvino-workflow-generative/inference-with-genai.html)). Even within Intel GPU inference, an engine-native SYCL path can bypass PyTorch ([llama.cpp SYCL backend documentation](https://raw.githubusercontent.com/ggml-org/llama.cpp/8ca4060b7e30e76baaa5670ee1ec1b760b7f8552/docs/backend/SYCL.md), pinned revision `8ca4060`). oneAPI libraries, SYCL execution and Level Zero provide different parts of the software path; none supplies a serving scheduler by itself, and Habana's collectives run through their own HCCL library ([HCCL API reference](https://docs.habana.ai/en/latest/API_Reference_Guides/HCCL_APIs/index.html)). [1P][FACT] for the stack boundaries; the portability consequence is [DERIVED].

This distinction changes a portability decision. A device API can be available while a required model operator or cache layout is not. Source-level portability therefore reduces one part of migration work. It does not establish feature parity, numerical equivalence or sustained performance. [DERIVED]


The chapter unfolds in four parts. First, the core arithmetic: FLOPs per token, prefill PFLOP counts, and H100 sustained utilization. Second, the roofline: why early layers are compute-bound while later layers and decode are memory-bound. Third, the canonical scenario arithmetic: 70B on 8×H100, TTFT 1.2 s, TPOT ~25 ms. Fourth, the mini-case: a continuous deployment scenario that threads the prefill/decode divide.

## 2. Mental Model

FLOPs are like the distance a car can travel on a gallon of fuel: it tells us the system's capacity, not how long the trip will take. The trip time is determined by the ridge point: if the arithmetic intensity is below the ridge, adding more FLOPs won't help because we are waiting for data. If we are above the ridge, we are limited by how fast the compute can chew through operations. The roofline chart — peak TFLOPS on the vertical axis, FLOP/byte on the horizontal — is the map that resolves this. Where our kernel lands on that chart decides whether we should profile memory bandwidth or compute throughput.

![Fig 8.1 — Where inference computation and data movement actually live. The hierarchy runs from the smallest/fastest/closest resource (registers, tensor cores, on-chip SRAM) to the largest/slower/farther (HBM, GPU interconnect, other GPUs). Inference work maps onto it: matrix multiply runs on the tensor cores; model weights and the KV cache are predominantly HBM-resident; FlashAttention restructures attention to tile through on-chip memory and cut HBM traffic; tensor-parallel (TP) communication crosses the GPU interconnect; pipeline-parallel (PP) communication moves activations between pipeline stages. The gradient of speed↔capacity↔distance is why compute, memory bandwidth, memory capacity and interconnect bandwidth are *distinct* architectural constraints — each is a different level of this ladder. **Schematic note:** the vertical ordering is a *relative* speed/capacity/distance ranking, not a measured timing scale — the gaps between levels are not to scale, and the same physical resource (e.g. HBM) can appear at different logical positions depending on the access pattern. [ILLUSTRATIVE conceptual]](figures/fig-08-0802.png)

*Read this ladder together with the roofline:* the roofline's vertical axis (peak TFLOPS) and horizontal axis (FLOP/byte) are both determined by *where* on this hierarchy the work sits. A kernel is compute-bound when its FLOPs run on the tensor cores and data fits in on-chip memory (high arithmetic intensity); it is bandwidth-bound when it must stream large tensors from HBM faster than the bytes can move (low arithmetic intensity). So the "bound" classification of Ch. 8 is not a property of the model alone — it follows from where the model's weights and the KV cache happen to be resident, and how much of the computation a kernel can keep on-chip. Ch. 15's FlashAttention discussion is exactly this ladder in action: keep more of the tile on-chip, move fewer bytes between HBM and the compute units.

## 3. Worked Example: Canonical Scenario Arithmetic

The canonical scenario (Ch 4, Table 4-2) is an enterprise Q&A system: the canonical 80-layer, hidden-8192, full-MHA 70B reference (a 70B-class dense model), FP16 weights (~140 GB), 1 host with 8×H100-class GPUs (80 GB each), average prompt 1,200 tokens + 8K retrieved context (~9.2K input), 300-token output, TTFT budget 1.2 s (retrieval ~120 ms + prefill), TPOT budget ~25 ms/token.

*Scope.* "1 host with 8×H100" here is a **per-host / per-request** feasibility container (does one host meet one request's latency and memory SLO). It is **not** a claim that one host absorbs the 40 rps peak arrival rate — as Ch 17 derives, that peak puts in-flight concurrency λ·W ≈ 344 at the ~8.6 s service time, far above one host's KV-residency ceiling (C ≈ 17.5, conservative integer floor 17), so the *fleet* needs ~21 hosts (Ch 17's floor-17 screen). The compute/roofline arithmetic of this chapter answers the per-request and per-host-shard question; the fleet question is a separate multiplication that Ch 17 performs (with the cost basis in Ch 16). We keep them distinct because each requires measuring against a different quantity (a latency budget vs an arrival rate).

### FLOPs per token

For a 70B-parameter dense model in FP16, the per-token forward FLOP count is approximately:

$$
\text{FLOP/}_{\text{token}} \approx 2 \times N = 2 \times 70 \times 10^9 \approx 140 \text{ GFLOP/token}
$$

[DERIVED: 2 FLOPs/parameter × 70 ×10⁹ params; standard dense-forward arithmetic, which is the same 2×N rule that gives, e.g., a 175B dense model 2 × 175 × 10⁹ ≈ 0.35 TFLOP/token]

This applies to both prefill and decode: each token that enters the forward pass costs ~140 GFLOP. The distinction between prefill and decode is not in the per-token FLOP count but in the data movement pattern — prefill reads the full context once, while decode re-reads weights per token.

The implementation examples in this paragraph were inspected on 2026-10-28. The 2P estimate (two FLOPs per parameter — the 2 ×N rule above) applies to the parameterized matrix work in a specified execution path. It does not account for all history-dependent attention, indexing, routing, or repeated-depth computation. A shared core executed several times reuses weights but repeats arithmetic. A phase-dependent architecture can also activate different paths during prefill and decode. The parameter estimate therefore needs a phase and an execution count before it enters the roofline analysis. ([DeepSeek-V4.1-Flash technical report](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/resolve/main/DeepSeek_V41_Tech_Report.pdf); [Huginn model card](https://huggingface.co/tomg-group-umd/huginn-0125/raw/main/README.md) and [Geiping et al., arXiv:2502.05171](https://arxiv.org/abs/2502.05171) for recurrence-aware cache and per-token adaptive compute). [1P][FACT] for the phase-dependent mechanisms; the execution-count qualification is [DERIVED].

### A small execution-budget example

An illustrative work model makes the distinction precise. Let `C` be fixed work outside a repeated core, `F` the work of one core pass, and `r` the executed pass count. Ignore decision overhead for this first estimate. Total work is `C + rF`; the unique core weight inventory remains unchanged as `r` changes. If `C = 1` work unit and `F = 2` work units, four passes cost 9 units and three passes cost 7. Omitting one of four passes removes 25% of core work but only `2/9`, approximately 22.2%, of total work. The units are illustrative operation-budget units, not milliseconds, FLOPs measured on a device, or a model benchmark. [ILLUSTRATIVE][DERIVED]

Selecting pass 3 after executing pass 4 still costs 9 units in this model. A real stopping check adds overhead, and lower work does not guarantee proportionally lower wall time. Small batches can underfill kernels. State movement, synchronization and memory stalls can dominate. A quality-preserving reduction in actual core executions is necessary evidence for a compute saving; a selected exit index alone is insufficient. [DERIVED]

Communication follows the executed path as well. If each core pass uses tensor-parallel collectives, repeating the core repeats those collectives unless a specific implementation changes the schedule. Weight sharing does not share their results across different hidden inputs. If MoE routing is also present, expert dispatch adds a separate traffic term; it cannot be inferred from the number of depth passes alone. Neither a shared parameter count nor a lower active-parameter count establishes the communication time. The deployment record must identify placement, parallel strategy, tensor sizes and the actual overlap achieved. [DERIVED]

### Prefill PFLOP for 9.2K input

For a single request with 9.2K input tokens, the prefill FLOP cost is:

$$
\text{prefill FLOPs} \approx 2 \times N \times L = 2 \times 70 \times 10^9 \times 9.2 \times 10^3 \approx 1.29 \text{ PFLOP}
$$

[DERIVED: 2 × N × L where N=70B, L=9,200; the figure is large because the full context is attended to, but it is a one-time cost per request, not a sustained rate]

*Accuracy of the 2 ×N × L approximation.* This linear prefill count omits the quadratic attention term, $\approx 4 \times n_\text{layers} \times L^2 \times d$. At the canonical 9.2K context that correction is small — roughly **+17%** of the 1.29 PFLOP — so the 2NL roofline is a sound teaching baseline there. But the omission grows with context: at 32K the attention term is ~**+60%** of the linear term and at 128K it *dominates* (~2.4× the linear term, ≈+240%). An architect sizing long-context prefill must add the quadratic term or measure it; the Unknowns section returns to this.

At 10 requests/s, the sustained prefill throughput demand is:

$$
\text{prefill demand} = 1.29 \times 10^{15} \text{ FLOP} \times 10 \text{ rps} \approx 12.9 \text{ PFLOP/s}
$$

[DERIVED]

**Table 8-1** — Per-token FLOP cost, prefill PFLOP, and the derived prefill and roofline rates for the canonical 70B workload. *(Per-token FLOP and prefill PFLOP computations are [ILLUSTRATIVE][DERIVED] from 2 × params × tokens; hardware peaks [1P: vendor datasheet] or [1P][FACT]; the 30–40% MFU range is [2°: industry benchmarks]; the ~295 FLOP/byte ridge is [2°][DERIVED] = 989 TFLOPS ÷ 3.35 TB/s.)*

| metric | value | derivation |
|---|---|---|
| per-token FLOPs (forward) | ~140 GFLOP/token | 2 ×70B params [DERIVED; standard dense-forward arithmetic — the same 2×N rule gives 175B ≈ 0.35 TFLOP/token] |
| prefill FLOPs for 9.2K input (linear only) | ~1.29 PFLOP | 2 ×70 ×10⁹ × 9.2 ×10³ [DERIVED; **parameterized-linear term — excludes the quadratic attention term**, see Ch 22] |
| sustained prefill demand @ 10 rps | ~12.9 PFLOP/s | 1.29 PFLOP × 10 [DERIVED] |
| H100 peak FP16 TFLOPS | ~989 TFLOPS [1P: NVIDIA H100 datasheet] | NVIDIA H100 SXM5 datasheet, without sparsity |
| H100 sustained MFU (typical) | 30–40% [2°: industry benchmarks] | ~346 TFLOPS sustained at 35% MFU |
| prefill throughput per GPU | ~2,471 tokens/s | 346 TFLOPS ÷ 140 GFLOP/token [DERIVED; **per-GPU scope**] |
| prefill throughput per host (8×H100) | ~19,800 tokens/s | 8 × 2,471 [DERIVED; **idealized aggregate, before TP/system loss**] |
| H100 ridge point (dense FP16) | ~295 FLOP/byte | 989 ÷ 3.35 [DERIVED: peak TFLOPS ÷ HBM bandwidth] |

*All figures trace to the canonical scenario (Ch 4, Table 4-2) and validated sources; none are measurement claims.*
This is the prefill compute demand. An 8×H100 node can sustain some fraction of this at MFU (model FLOPs utilization), which we estimate next.

### Sustained vs. peak: H100 MFU

NVIDIA H100 SXM5 lists ~1,979 TFLOPS FP16 Tensor Core peak "with sparsity" and ~989 TFLOPS FP16 peak without sparsity [1P: NVIDIA H100 datasheet]. In practice, sustained model FLOPs utilization (MFU) for a well-tuned transformer workload typically runs at 30–40% of peak on H100 [2°: industry benchmark reports, derived from real kernel profiles]. At 35% MFU:

$$
\text{sustained} = \text{peak} \times \text{MFU} = 989 \text{ TFLOPS} \times 0.35 \approx 346 \text{ TFLOPS}
$$

[1P][2°][DERIVED: vendor peak (1P) × typical MFU (2°) — the MFU range is a secondary, empirical figure, so the sustained value inherits the provenance of its weakest input, the 2° MFU, while the peak is first-party]

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

At the peak 40 rps (368,000 tokens/s) the same arithmetic gives ~18.6 → **~19–20 hosts**. This aligns — independently — with the KV-residency / Little's-Law fleet sizing derived in Chapter 17, with the cost basis in Chapter 16 (~21 hosts at peak, ~$155,816.93/mo self-host ≈ $24.97/1K — illustrative included-cost, Ch 16), which is a useful cross-check that the two fundamentally different constraints (prefill FLOP throughput vs. KV residency/service time) point at the same order of fleet.

**Honest boundary on both numbers.** The per-GPU `2,471 tokens/s` is itself an *analytical* figure at an assumed 35% MFU — not a measured throughput. The `8×` aggregate (`~19,800`/host) is a **theoretical first-order estimate** that assumes perfect tensor-parallel scaleout: it does **not** account for TP communication, per-rank load imbalance, kernel inefficiency under a given batch, or scheduling/system overhead. It is an upper-bound analysis value, not a servable goodput. Actual reachable prefill throughput must come from benchmark goodput under the target workload (Chapter 14). Treat both numbers as scope-disciplined *models*, never as measured capacity.

This rough sizing illustrates that prefill is FLOP-bound at this scale — the compute requirement is the primary constraint, and memory bandwidth (HBM at 3.35 TB/s per H100) is sufficient to keep the compute fed if the kernel is efficient. The ridge point for dense FP16 on H100 is ~295 FLOP/byte (989 ÷ 3.35); the arithmetic intensity of a mature attention kernel sits near or above this ridge, meaning the kernel is compute-saturated rather than bandwidth-starved once the batch is large enough.

### Decode: bandwidth-bound at low batch

![Fig 8.2 — Per-GPU roofline for dense FP16, one H100 vs one H200 (a per-GPU chart, not a host-level one). Compute ceiling and HBM bandwidth are single-GPU quantities here (989 TFLOPS, 3.35 / 4.8 TB/s), so the ridge point and the memory-bound slope are per-GPU. Conventions: a multiply-add counts as **2 FLOPs** (the FMA convention of §8.1); **dense** (no sparsity) FP16; the ceilings are **peak/theoretical** datasheet values, not achieved rates (sustained MFU is 30–40%, §8.3); the plotted prefill (9.2K input) and decode (batch=1) points are **illustrative operating points**, and a kernel's position on the roofline is a *theoretical* bound on its FLOP/byte intensity — it is **not a measured latency**. Prefill (9.2K input) sits to the right of the ridge, on the compute-bound plateau; decode (batch=1) sits to the left, on the memory-bound slope, and continuous batching climbs the slope as batch grows. The ridge *classification* (compute- vs memory-bound) is unchanged by ideal N-way replication because both peak FLOP/s and HBM bandwidth scale with GPU count; host-level attainable performance additionally depends on sharding and communication. [DERIVED from 1P: vendor datasheet]](figures/fig-08-0801.png)

*The roofline: at the canonical long-prompt operating point prefill is compute-bound; at low batch decode is memory-bound.*

<!-- Figure spec: mechanism-first roofline diagram; arithmetic intensity on x-axis, achievable FLOP/s on y-axis, ridge line where FLOP-bound meets byte-bound; label the prefill and decode operating points. -->

*Reading the roofline (summary of Fig 8.2): the dense-FP16 ridge at ~295 FLOP/byte (H100: 989 TFLOPS ÷ 3.35 TB/s) separates the compute-bound region (right) from the memory-bound region (left). Prefill sits far above the ridge — its arithmetic intensity is set by the sequence length (weights read once, reused across all tokens), so it is compute-bound; decode at batch=1 sits at the far left of the chart (~1 FLOP/byte, ~295× below the ridge) and is memory-bound. Batching and quantization shift kernels rightward toward the ridge; the distinction between the two phases is the single most important reading of this chart.*

For decode, the per-token FLOP cost is the same ~140 GFLOP, but the arithmetic intensity drops sharply. Each decoded token re-reads all 70B weights from HBM (a **batch-1-equivalent** weight-streaming read). A 70B FP16 weight matrix is 70 ×10⁹ × 2 B = 140 GB — one full pass reads **140 GB** (batch-1-equivalent), not 280 GB. (The naïve “2 ×70 ×10⁹ × 2 B ≈ 280 GB” double-counts the FP16 footprint: the leading “2” is already inside the 2-bytes-per-element, so writing 2 ×70 ×10⁹ × 2 B counts the weight bytes twice. Any KV/output-projection reads are a separate, smaller term on top, not a second full weight footprint.) The effective arithmetic intensity is therefore:

$$
\text{arithmetic intensity}_{\text{decode}} \approx \frac{140 \text{ GFLOP}}{140 \text{ GB}} \approx 1.0 \text{ FLOP/byte}
$$

[DERIVED; a lower-bound bandwidth model — real kernels also read activations and KV, so measured intensity is typically below this and heavily dependent on fusion and cache residency]

This is well below the H100 dense-FP16 ridge of ~295 FLOP/byte, meaning single-stream decode is overwhelmingly memory-bandwidth-bound. Throughput improves with batching because the weight-reread amortizes across tokens — decode intensity ≈ batch size (weight-only), so at batch=32 the effective intensity is ~32 FLOP/byte, still ~9× below the 295 ridge (compute-bound decode needs batch ≈ 295, or quantized weights, which halve bytes and double intensity), and TFLOP/s utilization increases accordingly. **KV-read caveat:** the weight-only intensity above omits the per-sequence KV re-read (~24 GB at the canonical 9.2K context, FP16 full-MHA). Including it, the decode intensity is (140·B)/(140 + 24·B) FLOP/byte, which *saturates* at ~5.8 FLOP/byte as B→∞ — far below the 295 ridge. So with the KV term, decode stays bandwidth-bound at every batch size; the "batch ≈ 295" figure is the weight-only first-order estimate (valid when the KV re-read is small relative to the weight stream, e.g. short contexts or KV quantization). This is why continuous-batching systems (Orca, vLLM) prioritize batch growth: it is the primary lever for pushing decode arithmetic intensity toward the ridge (on the weight-only term).

*Scope note on the single-device roofline here:* the 140 GB weight-read and the per-GPU ~3.35 TB/s HBM bandwidth are single-GPU quantities, so the ~1.0 FLOP/byte intensity and the "memory-bandwidth-bound" label above are a *per-kernel / single-device roofline* argument. It is **not** a verdict on the canonical 8×H100 host's actual bandwidth adequacy — under tensor parallelism the 140 GB weight matrix is sharded across GPUs, so each GPU streams only its own shard (~0.70 TB/s against its own ~3.35 TB/s, Ch 6). The classification (low-batch decode is bandwidth-bound) is shard-invariant because it follows from the low arithmetic intensity, not from the aggregate weight-read rate exceeding one GPU's bandwidth.

### The execution path determines the applicable roofline

Quantizing stored weights reduces one source of memory traffic, but the selected kernel determines the arithmetic. In a fused weight-dequantization path, a kernel reads compressed weights and converts them for higher-precision multiplication. A native block-scaled path instead requires compatible low-bit operands, scale layouts and device instructions. An emulation path may reconstruct higher-precision weights before GEMM. These paths can load related checkpoint representations while having different traffic, compute and workspace costs. Their operation counts and supported peak rates cannot be mixed in one roofline. Fig 7.3 makes this execution gate explicit. [1P][DERIVED]

In the Chapter 7 mixed-weight sensitivity — a teaching model storing 98% of parameters in MXFP4 and 2% in BF16 — a dense 2N useful-operation convention and one complete weight stream give about 3.567 FLOP/B at batch one, compared with 1 FLOP/B for BF16 weights. This is a weight-only analytical intensity, not a 3.567× throughput prediction. It excludes activation and KV traffic, conversion, additional scale traffic and communication. At large batch or during prefill, a GEMM may already be compute-bound; during long-context decode, attention and KV access can dominate. A lower weight-byte count therefore changes a candidate bottleneck, not the measured end-to-end bottleneck by definition. [ILLUSTRATIVE][DERIVED]

Communication needs a separate ledger. Compressed checkpoint loading can reduce distribution bytes if compressed files are transferred. It does not automatically compress activation all-reduces, expert all-to-all traffic or optimizer communication. Fewer devices might become feasible after a memory reduction, but that is a new parallelism configuration with different compute, memory and interconnect limits. Communication savings cannot be credited before the transmitted tensor types, placement and collective schedule are known. [1P][DERIVED] (The distinction follows the weight-only scope of [GPTQ](https://arxiv.org/pdf/2210.17323v2).)

## 4. Measurement

Three measurable quantities anchor compute sizing:

1. **Per-token FLOP count.** Measure by flops profiling (e.g. NVIDIA Nsight Compute) on the target model and precision. The 2×N rule is a useful prior, but actual count varies by layer depth, activation choice (SiLU vs. ReLU), and whether kernel fusion combines matmuls.

2. **Sustained MFU.** Profile TFLOP/s achieved divided by peak TFLOP/s for the target hardware and precision. A well-tuned transformer on H100 FP16 typically lands in the 30–40% range; below 20% suggests a memory or communication bottleneck that should be diagnosed before scaling.

3. **Arithmetic intensity (FLOP/byte).** Compute as achieved FLOPs divided by bytes transferred (weights + activations + KV read/write). Compare to the hardware ridge point (H100 dense FP16: ~295 FLOP/byte; H200: ~989 TFLOPS ÷ 4.8 TB/s ≈ 206 FLOP/byte — H200 keeps H100's GH100 die and its dense FP16 peak, trading a bigger/faster HBM3e for bandwidth; GB200: higher on both terms (faster dense BF16 peak and ~8 TB/s HBM), so its BF16 ridge is higher, and its NVFP4 ridge higher again). If intensity is below the ridge, the kernel is memory-bound; above, compute-bound.

A compute roofline does not include every exposed distributed stall. A communication kernel can consume SM and HBM resources while appearing to overlap a matrix multiplication. The joint trace must therefore distinguish model computation, collective work, exposed waiting and computation slowed by contention. Peak interconnect bandwidth cannot be added to peak compute to predict the combined schedule; Chapter 9 separates their mechanisms and measurement boundaries. [DERIVED]

## 5. Common Mistakes

- **Assuming 2×N FLOPs/token is exact.** It is a baseline derivation; actual per-token FLOPs vary with layer depth, activation fusion, and kernel fusion. Profile before quoting.

- **Treating prefill and decode as having the same FLOP/byte profile.** Prefill reads the full context once and is FLOP-bound; decode re-reads weights per token and is memory-bound. The arithmetic-intensity roofline distinguishes them.

- **Using peak TFLOP/s as sustained throughput.** Peak includes sparsity or BF16/FP8 variants that may not be available in the chosen precision. Use the FP16 number without sparsity (≈989 TFLOPS on H100) as the baseline for dense compute sizing.

- **Ignoring the batch-size dependence of arithmetic intensity.** A single-token decode batch has very low intensity; batching raises it. Always state the batch assumption when reporting TFLOP/s or tokens/s.

- **Confusing H100 sparsity-inclusive peak (1,979 TFLOPS) with dense peak (989 TFLOPS).** The 2× sparsity figure appears in vendor data sheets but most transformer workloads do not activate sparsity. Quote the dense figure unless the kernel is specifically sparsity-enabled.

## 6. Architecture Consequence

The compute arithmetic and roofline have direct consequences for system design:

- **If prefill is FLOP-bound** (as it is for 70B+ models with long contexts), the primary optimization is batching — larger prefill batches do **not** remove the per-request attention work (each sequence still has its own attention computation); they *improve accelerator utilization* by forming larger matrix operations, amortizing weight and execution overhead across requests, and raising achieved FLOP/s. The relevant lever is the achieved efficiency (MFU) of the prefill kernel, not a change to the per-request FLOP count. System design should therefore provision for batchable prefill (continuous batching, Orca, vLLM continuous batching) as the first-order throughput lever.

- **If decode is memory-bound** (single-stream, low batch), the primary optimization is batching — decode arithmetic intensity ≈ batch size, so even modest batch sizes (8–16) raise it to ~8–16 FLOP/byte (batch 16 → ~16, still ~18× below the 295 ridge), improving TFLOP/s utilization without reaching compute-bound; compute-bound decode needs batch ≈ 295, or quantized weights, which halve bytes and double intensity. KV cache quantization (FP8, int8) also reduces bytes per token, raising effective intensity. P/D disaggregation (prefill on GPUs, decode on a separate pool) can rebalance: prefill’s FLOP demand is served by compute-optimized GPUs, while decode’s bandwidth demand is served by wide-memory GPUs or even CPU offload.

- **If the workload's intensity crosses the hardware ridge** (e.g. a workload at ~250 FLOP/byte is memory-bound on H100's ~295 ridge but compute-bound on H200, whose FP16 ridge is ~206 FLOP/byte — 989 TFLOPS ÷ 4.8 TB/s — from its higher HBM3e bandwidth), the same workload may shift from memory-bound to compute-bound, changing the optimal hardware choice. The shift comes from the *lower* ridge, not from precision: a higher ridge moves the boundary right and makes compute-bound harder (H200's ~412 FLOP/byte ridge in *dense* FP8 — ~1.98 PFLOPS ÷ 4.8 TB/s, never the sparsity-inclusive ~4 PFLOPS (§8.5) — would do the opposite), and precision scaling moves intensity and ridge together (bytes halve → intensity doubles; peak doubles → ridge doubles), so FP8 alone does not change the classification. This is why the H200 represents an inflection point where inference and training hardware lines begin to converge [1P: NVIDIA H200 SXM datasheet].

In practice, the architect measures arithmetic intensity for the target workload and precision, locates the kernel on the roofline chart, and then selects hardware and batching strategy accordingly. The roofline is the diagnostic; the architecture decision follows.

### From video dimensions to repeated attention work

The same derive-then-decide move applies to a workload that evaluates all of its token positions together rather than one per step: the budget below is derived from counted dimensions, not from a duration label.

A worked example makes the new work unit concrete. We use Wan2.2 TI2V-5B in its text-to-video path, not the A14B expert model. Its configuration specifies a dense transformer with hidden width 3,072, 30 layers, and 24 attention heads. The VAE has 48 latent channels and temporal/spatial strides of 4, 16, and 16. The denoiser patches the latent video by `(1,2,2)`. The release's "720P" example is precisely 1,280 × 704 pixels, 121 frames, at 24 frames/s. The dimensions, rather than the marketing resolution label, determine the budget. [1P][FACT] ([Wan2.2 TI2V-5B configuration](https://github.com/Wan-Video/Wan2.2/blob/1ea34ff48f87168174e12956e200b1d908b1c5ff/wan/configs/wan_ti2v_5B.py), pinned revision `1ea34ff`, retrieved 2026-10-28; [Diffusers transformer config](https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B-Diffusers/blob/main/transformer/config.json)).

Fig 8.3 shows the data path. The prompt passes through UMT5-XXL. An optional image follows a separate reference-conditioning path. The T2V calculation below does not add that I2V branch to its state budget. Initial noise spans the entire latent video. Each scheduler step calls the denoiser on this representation; VAE decoding follows the final update. [1P][FACT] ([sampling loop](https://github.com/Wan-Video/Wan2.2/blob/1ea34ff48f87168174e12956e200b1d908b1c5ff/wan/textimage2video.py), pinned revision `1ea34ff`, retrieved 2026-10-28).

![Fig 8.3 — Wan2.2 TI2V-5B whole-clip denoising. The T2V worked example starts from a 31×44×80×48 latent tensor and patchifies it into 27,280 video tokens. The fetched implementation uses T_l=(F−1)//4+1, H_l=H//16 and W_l=W//16. For aligned F=4k+1, F=1+4(T_l−1): 31 latent time positions correspond to 121 frames. The optional I2V branch is separate from the T2V budget. The feedback loop is denoising/scheduler iteration, not architectural recurrence. Fifty upstream timesteps use two CFG branch evaluations each. The VAE decode is not autoregressive text decode. [1P][FACT] geometry and loop. The aligned inverse and token count are arithmetic derivations from that geometry. Schematic, not a latency or peak-memory measurement.](figures/fig-08-0803-video-latent-work.png)

For this aligned shape, the temporal latent count includes the first-frame convention:

$$T_l=\left\lfloor\frac{F-1}{4}\right\rfloor+1=31, \qquad H_l=704/16=44, \qquad W_l=1280/16=80.$$

There are 109,120 latent spatial-temporal cells, each with 48 channels. Patching reduces the number of transformer positions:

$$N=T_l\frac{H_l}{2}\frac{W_l}{2}=31\times22\times40=27{,}280.$$

Channels contribute features to each token; they do not multiply the token count. Sequence-parallel implementations may pad this length to a device-partition multiple. Conditioning tokens and condition tensors require separate accounting. [1P][DERIVED] ([sampling loop](https://github.com/Wan-Video/Wan2.2/blob/1ea34ff48f87168174e12956e200b1d908b1c5ff/wan/textimage2video.py)).

For batch size one, full noncausal attention with hidden width $d$ requires approximately

$$C_{\mathrm{attention,layer}}=4N^2d$$

FLOP for the two matrix products $QK^T$ and $AV$, counting a multiply-add as two FLOP. This excludes projections, MLPs, normalization, softmax, text cross-attention, and the decoder. Wan's inspected default sets `causal=False` and `window_size=(-1,-1)` (inspected upstream revision `1ea34ff`, retrieved 2026-10-28: [attention module](https://github.com/Wan-Video/Wan2.2/blob/1ea34ff48f87168174e12956e200b1d908b1c5ff/wan/modules/attention.py); [model geometry](https://github.com/Wan-Video/Wan2.2/blob/1ea34ff48f87168174e12956e200b1d908b1c5ff/wan/modules/model.py)). A triangular autoregressive reduction does not apply. [1P][FACT] attention mode; [1P][DERIVED] arithmetic.

At this shape the attention core requires 9,144,709,939,200 FLOP per layer, or about 9.145 TFLOP. Across 30 layers it requires about 274.341 TFLOP per branch evaluation. The inspected upstream loop evaluates conditional and unconditional predictions separately at each of its 50 default scheduler timesteps (same pinned revision `1ea34ff`). That is 100 single-sample branch evaluations, giving about 27.434 PFLOP of attention-core work over the trajectory. This is not the whole model's FLOP count and is not a GPU execution time. A runtime may batch the two branches into one forward call without removing their two-sample arithmetic. [1P][DERIVED] ([configuration](https://github.com/Wan-Video/Wan2.2/blob/1ea34ff48f87168174e12956e200b1d908b1c5ff/wan/configs/wan_ti2v_5B.py); [sampling loop](https://github.com/Wan-Video/Wan2.2/blob/1ea34ff48f87168174e12956e200b1d908b1c5ff/wan/textimage2video.py)).

The memory calculation has an equally important boundary. One hypothetical BF16 hidden tensor contains $N\times d\times2=167{,}608{,}320$ bytes. Materializing one BF16 score tensor for 24 heads would require $24\times N^2\times2=35{,}721{,}523{,}200$ bytes, or about 33.268 GiB. This is a hypothetical implementation choice, not a claim that FlashAttention allocates such a tensor. Tiled exact attention avoids retaining the full score matrix while still performing the pairwise work. The upstream code creates initial latent noise in FP32, so assigning BF16 to every live tensor would also undercount state. [1P][DERIVED] ([attention module](https://github.com/Wan-Video/Wan2.2/blob/1ea34ff48f87168174e12956e200b1d908b1c5ff/wan/modules/attention.py); [sampling loop](https://github.com/Wan-Video/Wan2.2/blob/1ea34ff48f87168174e12956e200b1d908b1c5ff/wan/textimage2video.py)).

The sensitivity explains the architectural consequence. Extending 121 to 241 frames changes the temporal latent count from 31 to 61. Token count rises by about 1.968×; the dense pairwise term rises by about 3.872×. Doubling both spatial dimensions gives four times the tokens and sixteen times the pairwise work. These are algebraic sensitivities, not claims that either larger workload meets the release's quality or memory envelope. A request limit expressed only in clip-seconds misses this distinction. [1P][DERIVED]

At 24 frames/s, 121 frames also exposes a measurement convention. The final frame's timestamp is 5 seconds after the first. A constant-frame-duration container spans $121/24$, or about 5.0417 seconds. A service contract needs one convention. "Five-second clip," "121 frames," and "27,280 latent tokens" describe related but different quantities. [DERIVED]

## 7. What We Still Don't Know

- **Arithmetic intensity of fused kernels.** Most roofline estimates treat attention or MLP as separate matmuls, but in practice frameworks fuse multiple operations into a single kernel. The effective FLOP/byte of a fused attention+MLP kernel is not well cataloged in primary sources and would require profiling on the target hardware to anchor.

- **MFU across precisions and sparsity.** The 30–40% H100 FP16 figure is a rule of thumb; actual utilization depends on architecture, kernel quality, and batch config. A systematic MFU atlas across H100/H200/GB200, FP16/BF16/FP8, dense/MOE would be a valuable reference.

- **Arithmetic intensity of emerging attention mechanisms.** Linear attention (DeltaNet, MLA), compressed attention (CSA, HCA), and hybrid sparse patterns have different FLOP profiles and data movement. Their roofline position is not yet established in primary sources.

- **Frontier 2026 has begun to answer this.** DeepSeek-V4's hybrid CSA+HCA attention reports that, at 1M-token context, single-token inference drops to ~27% of the FLOPs (Pro) / ~10% (Flash) and KV cache to ~10% / ~7% of DeepSeek-V3.2 [1P: arXiv 2606.19348]. In its [2026-08-26 release article](https://z.ai/blog/glm-5.3-flash), Z.ai compares GLM-5.3-Flash with GLM-5.3: it reports 3× less attention compute **per head per layer** and a 4.4× smaller **average BF16 KV cache per layer**. These are normalized attention metrics, not whole-model FLOP or total-cache ratios. These are [1P] first-party vendor figures, not yet independently reprofiled on our own hardware — which is exactly the arithmetic-intensity measurement an architect should still do before trusting a vendor's roofline claim for their own workload.

- **How quantization shifts the ridge.** Moving from FP16 to FP8/int8 changes peak TFLOP/s and bytes-per-operand, shifting the ridge point. The net effect depends on the quantization scheme (element-wise vs. per-tensor, dynamic vs. static) and whether the kernel is re-tuned for the lower precision.

## 8. End-of-Chapter Mini-Case: Continuous Deployment Scenario

An architect is brought into an ongoing deployment of a 70B-class Q&A system on 8×H100 GPUs. The system is serving ~10 requests/s average with ~9.2K input + 300 output tokens per request, and the TTFT budget is being missed: p95 TTFT is 2.8 s, exceeding the SLO of 2 s. The TPOT of 28 ms/token is within spec, but the prefill delay is the bottleneck.

The temptation is to reach for a roofline and "prove" prefill is memory-bound. That reasoning is wrong here, and the error is worth naming: it is spread by treating prefill like token-by-token decode. In decode, each new token re-reads the weight matrix from HBM, so the arithmetic intensity is ~1 FLOP/byte — genuinely memory-bound. In prefill, the weight matrix is read *once* and reused across the whole sequence; the sequence dimension supplies the matrix-matrix reuse. Prefill's effective intensity is `(2 × N × L) / (N × 2 bytes/param)` = `L` = **9,200 FLOP/byte** at the canonical 9.2K context — ~1.5 orders of magnitude above the ~295 FLOP/byte dense-FP16 ridge. At that operating point prefill is compute-bound, exactly as the rest of this chapter teaches.

So a high TTFT is *not* evidence of a bandwidth problem. The architect does the correct thing: profile the prefill kernel and determine which of several distinct causes is actually limiting it, rather than assuming memory. The profile separates four candidates:

- **Compute-bound** — the GEMMs are saturated at high MFU; more FLOPs/ops per token would not help, but better kernel efficiency (flash-attention, fused MLP) would.
- **Communication-bound** — tensor/pipeline parallelism crosses the NVLink/Host fabric; data movement, not math, is the ceiling. The fix is a different parallelization or a smaller cross-GPU footprint.
- **Launch / occupancy-limited** — the kernel is too small or the grid under-fills the SMs; increasing batch or improving occupancy raises utilization without adding hardware.
- **Attention / memory constrained (within prefill)** — the quadratic attention term, not the linear weights, grows with context; at 128K+ contexts this term dominates prefill cost (at 32K it is already ~+60% — the 4·n_layers·L²·d term, Fig 22.1), so the fix is to reduce the attention term (flash-attention, sparse/linear attention), not to batch harder.

The architect measures MFU to choose among these. If the prefill kernel is running at 12% MFU, the problem is occupancy or launch — grow the batch or fuse kernels. If MFU is already near ~40% and the kernel is compute-saturated, then prefill *is* compute-bound and more batch just queues more work without reducing per-request TTFT; the lever instead is kernel efficiency, attention-term control, or P/D disaggregation so prefill's FLOP profile is served by compute-optimized GPUs while decode's bandwidth profile runs on wide-memory GPUs.

The recommendation is therefore: profile first (MEASURE, do not assume), and only then pick the intervention. Batching helps when prefill is occupancy-limited; kernel fusion helps when GEMMs are under-saturated; attention-term control and disaggregation help when the bottleneck is the quadratic attention term or the compute/bandwidth mismatch between phases. The workload's true roofline position, not an assumed "memory-bound prefill," dictates the fix.

***

*Prefill PFLOP also grows with context: 2 ×70B × L tokens scales linearly — ~0.29 PFLOP at 2K → ~4.6 PFLOP at 32K — so the longer the window, the larger the one-time compute cost of loading it. Sustained throughput (tokens/s) is what matters for continuous serving, and at the canonical 9.2K point the prefill is ~1.29 PFLOP (Table 8-1).*