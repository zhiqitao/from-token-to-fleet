# Proposed quantization insertions — not applied

Editorial status: substantive candidate English prose, figures and citations for author integration. This file does not change the manuscript. Local figure IDs QF1/QF2 and claim IDs Q01–Q38 are research identifiers, not final book numbering or replacements for existing [S#] references. Proposed figure width is 6.1 inches, derived from the current US Letter build and its 1.2-inch side margins. Figure captions and alt text are also in figures/manifest.json.

Temporal rule: the main mechanism discussion uses pre-2026-08-30 papers/specifications. Current implementation examples are explicitly dated 2026-10-28 and are not assertions about support at the book's August cutoff. Material requiring October code belongs in a separately dated update unless historical implementation evidence is added. Citations link to primary sources; source-index.md and claims.json preserve fetched snapshots, hashes and limits.

## Placement A — Chapter 5, candidate selection

File: `design/manuscript/chapter-05/chapter-05.md`, after the five selection surfaces at lines 15–17. Add the following bridge, not another model-family survey.

### A model candidate includes its deployment precision

A model name alone does not identify a deployable candidate. The same checkpoint can produce different quality, memory use and execution paths under different quantization recipes. We therefore compare a base-model revision together with its tensor precisions, calibration or recovery procedure, export schema and serving backend. The quality gate applies to that exported deployment, including its tokenizer, prompt template and modal branches. A language-only quantization result does not establish that a vision encoder, projector or tool-use workload retains the same behavior. The mechanism and byte accounting appear in Chapter 7; Chapter 14 supplies the acceptance test. [1P][DERIVED] ([AWQ](https://arxiv.org/abs/2306.00978v6); [GPTQ](https://arxiv.org/abs/2210.17323v2); research claims Q01–Q04, Q35.)

## Placement B — Chapter 7, main explanatory insertion

File: `design/manuscript/chapter-07/chapter-07.md`. Insert after the explanation of Table 7-2, immediately before §4. Existing Table 7-2 remains a rough memory floor. This insertion explains its missing metadata and execution assumptions rather than replacing the canonical scenario.

<a id="q-layers"></a>
### Quantization describes several different choices

“Four-bit model” leaves several architectural questions open. Which tensors use four-bit values? How are those values chosen? What do the four bits represent? Where are scales stored? Which kernel consumes the resulting tensors? Figure QF1 separates these questions. A calibration method, a tensor encoding and a checkpoint container can participate in the same deployment; they are not competing answers to one question.

![Figure QF1. Quantization choices and execution paths. Methods, representations, packed tensors and containers describe different parts of a deployment. Loading still requires a compatible runtime layout and kernel. Unsupported combinations may be rejected; fallback is not guaranteed.](figures/qf1-quantization-layers.png){width=6.1in}

AWQ and GPTQ primarily address error control during post-training weight quantization. AWQ uses representative activations to identify important channels and chooses equivalent channel scaling that reduces the error introduced by quantizing weights. “Activation-aware” describes the information used by the method; it does not mean that activations are also stored in four bits. The paper's exploratory observation about protecting a small fraction of salient weights is not a definition requiring those weights to remain FP16. Its scaling method seeks protection without that irregular mixed-precision storage. [1P][FACT] ([AWQ, §3](https://arxiv.org/pdf/2306.00978v6); Q01–Q02.)

GPTQ instead uses approximate second-order information to compensate for quantization error in the remaining weights as quantization proceeds. Its original implementation targets weight quantization, not activation quantization. Neither method name uniquely specifies a group size, scale dtype, zero-point layout, permutation or checkpoint packing. Those fields are needed to reproduce both accuracy and memory use. Calibration data must represent the intended workload; a method's reported behavior on one evaluation does not establish behavior on another distribution. [1P][FACT] ([GPTQ, §2–4](https://arxiv.org/pdf/2210.17323v2); Q03–Q04.)

A container answers a different question. GGUF stores model metadata, tensor descriptions, tensor types and aligned tensor payloads. It is not a single numerical precision. Its tensor-type field permits different encodings within one model. Consequently, a comparison labeled “AWQ versus GGUF” confounds an error-control method with a file format unless both sides are expanded into complete deployment configurations. The useful comparison specifies the method, tensor encodings, mixed-precision exceptions and execution backend. The same caution applies to safetensors: storing tensors in a recognized container does not establish that a loader understands their quantized schema. [1P][DERIVED] ([GGUF specification, pinned revision](https://github.com/ggml-org/ggml/blob/da8e2a54b919557b816b1c2beb432ccb766f7ce0/docs/gguf.md); Q05.)

A compact configuration record can keep the axes separate:

| Field | Architectural question |
|---|---|
| Target tensors | Weights, activations and KV cache each need an explicit precision policy. |
| Error-control procedure | What calibration, optimization, fine-tuning or distillation selected the values? |
| Numerical scheme | What are the value encoding, scale encoding, group axis and zero-point rule? |
| Export and packing | What container, tensor schema, padding and alignment does the loader expect? |
| Execution path | Which operator, device and kernel consume the tensors, and what happens if unsupported? |

The record is more durable than a list of product names. It also exposes a missing assumption before a memory estimate becomes a hardware recommendation.

<a id="q-block-bytes"></a>
### Shared scales change the storage calculation

OCP MXFP4 1.0 uses E2M1 four-bit values, with one eight-bit E8M0 scale shared by a block of 32 values. E8M0 represents a power-of-two scale. The common one-dimensional NVFP4 scheme also uses E2M1 values, but shares an E4M3 local scale over 16 values and uses an additional FP32 tensor-global scale. Neither scheme uses an affine integer zero point in this comparison. The local scale's encoding and granularity change the set of representable values and its adaptation to a block's dynamic range; smaller groups also require more scale bytes. This is a mechanism difference, not an automatic accuracy ranking. [1P][FACT] ([OCP MX 1.0, §4–6](https://www.opencompute.org/documents/ocp-microscaling-formats-mx-v1-0-spec-final-pdf); [NVIDIA NVFP4 explanation, 2025-06-24](https://developer.nvidia.com/blog/introducing-nvfp4-for-efficient-and-accurate-low-precision-inference/); Q09, Q12.)

Figure QF2 holds the number of logical values constant. The same 32 four-bit values require 16 payload bytes in either scheme. MXFP4 adds one local-scale byte, producing 17 bytes per 32 values, or 0.53125 B/value. Common 1D NVFP4 adds two local-scale bytes, producing 18 bytes per 32 values, or 0.5625 B/value, before the tensor-global scale. For a tensor with N values in complete blocks, this example's compact NVFP4 storage is 0.5625N + 4 bytes. The four global-scale bytes are shared across the tensor, not repeated for each block. [1P][DERIVED][ANALYTICAL] (Q10, Q13; independently reproduced in independent_calculations.py.)

![Figure QF2. Four-bit payloads and shared scale storage. Both rows represent 32 E2M1 values. Bars are proportional only for payload and local-scale bytes; the separate FP32 NVFP4 scale is per tensor. Totals exclude padding, headers, extra copies and high-precision exceptions. This is storage accounting, not an accuracy or throughput comparison.](figures/qf2-block-scale-bytes.png){width=6.1in}

These rates are not the total footprint of a model. A mixed-precision model retains some tensors at higher precision. A file adds metadata and alignment gaps. A runtime may pad dimensions, reorder scales, create extra representations or reserve workspace. The memory ledger therefore separates checkpoint bytes, resident tensors, load/repack peak, activations, KV cache and workspace. A checkpoint that fits on disk may still fail during loading, and a successfully loaded checkpoint may not leave enough memory for the intended context and concurrency. The exact runtime layouts remain implementation-dependent. [1P][DERIVED][ANALYTICAL] (Q04–Q06, Q31–Q32.)

<a id="q-worked-example"></a>
### Worked example: scale overhead is small but not zero

Consider a 4096 × 4096 weight matrix: 16,777,216 values. The shape is illustrative; the byte results follow the stated layouts. BF16 payload occupies 33,554,432 bytes. MXFP4 with complete 32-value blocks occupies 8,912,896 bytes. Common 1D NVFP4 with complete 16-value blocks and one FP32 global scale occupies 9,437,188 bytes. The difference comes from the chosen scale representation and grouping, not a different number of four-bit payload values. Both calculations exclude padding, additional scale copies and non-weight tensors. [ILLUSTRATIVE][DERIVED][ILLUSTRATIVE] (Q10, Q13; calculations.json.)

An integer scheme can produce a different bill again. With groups of 128, an illustrative INT4 layout containing an FP16 scale and a packed four-bit zero point per group uses 8,716,288 bytes for the same matrix. Replacing the packed zero with an FP16 scaled-zero increases that layout to 8,912,896 bytes. Equal total bytes do not make this integer scheme numerically equivalent to MXFP4. The example explains why an estimate needs the actual scale and zero layout rather than “four bits plus a little overhead.” It does not choose an accuracy or speed winner. [ILLUSTRATIVE][DERIVED][ILLUSTRATIVE] (AWQ implementation details are current-code observations; [pinned linear implementation](https://github.com/mit-han-lab/llm-awq/blob/d6e797a42b9ef7778de8ee2352116e0f48a78d61/awq/quantize/qmodule.py) is indexed as AWQ-LINEAR; Q04.)

For a separate resource sensitivity, suppose a 70B-parameter teaching model stores 98% of parameters in MXFP4 and 2% in BF16. Those fractions are deliberately chosen, not a real checkpoint inventory. Compact weight storage becomes 39.24375 GB rather than 140 GB. Retaining the chapter's full-MHA, BF16 KV assumptions—80 layers, KV width 8192, 9,500 tokens per sequence—leaves raw KV at 24.90368 GB per sequence. In a 640 GB aggregate pool with a fixed 64 GB reserve, the storage-only integer ceiling rises from 17 sequences to 21, not in proportion to the weight compression. The added KV budget does not prove that the ranks can place it or that 21 requests meet the latency SLO. Workspace, fragmentation and per-rank balance still need measurement, and the reserve itself may change. [ILLUSTRATIVE][DERIVED][ILLUSTRATIVE] (Q33; full assumptions and exact arithmetic in calculations.json.)

The causal consequence is narrower than “quantization solves memory.” Weight compression frees one term in the memory ledger. If KV dominates the remaining footprint, context length and concurrency can still bind. Weight precision and KV precision remain separate decisions, with separate scale calibration, attention-kernel support and quality validation. KIVI's separate treatment of key and value statistics is one example of a KV-specific method, not a consequence of choosing an AWQ weight checkpoint. [1P][FACT] ([KIVI](https://arxiv.org/abs/2402.02750v2); Q18, Q34.)

### Methods, containers and representations at a glance

This table compares roles, not competing vendors or measured performance. October implementation rows must remain in a dated update for the August edition.

| Item | What it specifies | What remains to establish |
|---|---|---|
| AWQ / GPTQ | Error control for post-training weight quantization | Encoding, groups, scales, packing, exceptions and selected kernel |
| GGUF | Container metadata and typed tensor payloads | Each tensor encoding and the loader/backend's actual coverage |
| GGML K / IQ | Specific block encodings and decoding rules | Tensor mix, calibration/imatrix policy and backend support |
| MXFP4 | E2M1 values and shared E8M0 block scaling in OCP 1.0 | Recipe, tensor roles, runtime layout and native or emulated arithmetic |
| Common 1D NVFP4 | E2M1 values, 16-value E4M3 scales and tensor FP32 scale | Training/inference recipe, padding, device and kernel support |
| FP8 / INT8 / INT4 | Value type or bitwidth, only partially specified by the name | Scaling, grouping, zero rule and operand precision |

FP8 also needs a precise definition: E4M3 and E5M2 differ in range and special-value behavior, and the OFP8 specification does not choose the scaling algorithm. SmoothQuant is a W8A8 calibration method, not another name for INT8. NF4 is a nonuniform representation used by QLoRA; a four-bit frozen training base does not imply native FP4 GEMM or describe the memory used by adapters, activations, gradients and optimizer state. [1P][FACT] ([OFP8](https://www.opencompute.org/documents/ocp-8-bit-floating-point-specification-ofp8-revision-1-0-2023-12-01-pdf-1); [SmoothQuant](https://arxiv.org/abs/2211.10438v7); [QLoRA](https://arxiv.org/abs/2305.14314v1); Q16–Q17.)

## Placement C — Chapter 8, after the decode-intensity explanation

File: `design/manuscript/chapter-08/chapter-08.md:141–145`. Append the following subsection; do not repeat the block arithmetic.

### The execution path determines the applicable roofline

Quantizing stored weights reduces one source of memory traffic, but the selected kernel determines the arithmetic. In a fused weight-dequantization path, a kernel reads compressed weights and converts them for higher-precision multiplication. A native block-scaled path instead requires compatible low-bit operands, scale layouts and device instructions. An emulation path may reconstruct higher-precision weights before GEMM. These paths can load related checkpoint representations while having different traffic, compute and workspace costs. Their operation counts and supported peak rates cannot be mixed in one roofline. Figure QF1 makes this execution gate explicit. [1P][DERIVED] (October implementation examples and their temporal limits appear in the dated note below; Q19–Q21, Q32.)

In Chapter 7's illustrative mixed-weight sensitivity, a dense 2N useful-operation convention and one complete weight stream give about 3.567 FLOP/B at batch one, compared with 1 FLOP/B for BF16 weights. This is a weight-only analytical intensity, not a 3.567× throughput prediction. It excludes activation and KV traffic, conversion, additional scale traffic and communication. At large batch or during prefill, a GEMM may already be compute-bound; during long-context decode, attention and KV access can dominate. A lower weight-byte count therefore changes a candidate bottleneck, not the measured end-to-end bottleneck by definition. [ILLUSTRATIVE][DERIVED][ILLUSTRATIVE] (calculations.json.)

Communication needs a separate ledger. Compressed checkpoint loading can reduce distribution bytes if compressed files are transferred. It does not automatically compress activation all-reduces, expert all-to-all traffic or optimizer communication. Fewer devices might become feasible after a memory reduction, but that is a new parallelism configuration with different compute, memory and interconnect limits. Communication savings cannot be credited before the transmitted tensor types, placement and collective schedule are known. [1P][DERIVED] (The distinction follows the weight-only scope of [GPTQ](https://arxiv.org/pdf/2210.17323v2); Q03.)

## Placement D — Chapter 11, after Table 11-2 and its explanation

File: `design/manuscript/chapter-11/chapter-11.md:143–149`. Add a compatibility gate, not another fast-aging engine ranking.

<a id="q-kernel-gates"></a>
### A recognized quantization name is not an end-to-end support claim

A deployment needs a chain of compatible choices: checkpoint schema, model graph, tensor layout, operator coverage, runtime dependencies and device instructions. “Supports four-bit weights” does not establish support for a model's grouped expert GEMMs, attention variant, modal branches or KV format. A backend may accept a checkpoint and select a different arithmetic path, reject a particular shape, or need a temporary higher-precision representation. Figure QF1 distinguishes serialized tensors from the kernel-required runtime layout. A missing compatible path is a deployment failure, not a guaranteed fallback. [1P][DERIVED] (Q19–Q26, Q35; implementation-specific examples are dated separately.)

The deployment record therefore includes the exact model and engine revision, device architecture, driver/toolkit and library versions, quantized tensor inventory, selected kernels and fallback logs. It also records cold-load peak and steady HBM separately. This record determines whether the configuration can be reproduced; a single support-table checkmark does not. Allocator or scheduling limits then determine how much of the remaining memory can become usable KV capacity without violating latency targets. Smaller weights do not justify increasing admitted concurrency until the new operating point is measured.

## Placement E — Chapter 14, §4 Measurement

Add this quantization-specific test card after the existing performance/quality measurement guidance. It augments that guidance rather than replacing it.

<a id="q-validation"></a>
### Acceptance test for a quantized deployment

The comparison is paired: one base-model revision, fixed tokenizer and prompt template, fixed decoding/reasoning budget, the same workload and the same hardware. The candidate differs by a documented precision recipe and its required kernel path. Calibration data are separate from test data. If a high-precision baseline was never published, that absence remains explicit; the experiment cannot establish loss relative to unavailable original weights.

Accuracy is checked on the actual exported implementation. Reasoning tasks need verifiable answers under a fixed effort budget. Code tasks need execution and tests, not only syntactic validity. Tool tasks need correct tool selection, valid arguments, completed outcomes and a record of retries or unsafe actions. Multimodal tasks fix preprocessing and evaluate every affected modal branch. Long-context tests cover both retrieval and dependencies over position and generation length; weight precision and KV precision are varied separately. A favorable perplexity result does not establish all of these capabilities. These are acceptance criteria for the proposed experiment, not claims that a particular format passes them. [ILLUSTRATIVE][ASSUMPTION][UNMEASURED] (Q29, Q34–Q37.)

The load test keeps arrival traces, prompt/output distributions, parallelism and cache state fixed. It measures load peak, steady/reserved HBM, kernel selection, TTFT, inter-token latency, completion time, errors and task quality. A bounded first screen can use at least 200 paired examples per critical task and three repetitions per load point, but these are illustrative starting budgets, not proof of rare-failure or p99 reliability. Final sample sizes follow the predeclared degradation bound and statistical power. Only candidates that pass the quality gate enter a comparison of SLO-goodput and cost per successful task. [ILLUSTRATIVE][ASSUMPTION][UNMEASURED]

## Placement F — Chapter 15, after the decision map

File: `design/manuscript/chapter-15/chapter-15.md:57–64`. Add one paragraph.

Weight quantization is a candidate intervention when weight capacity or weight traffic is limiting. After the change, the bottleneck may move to KV access, attention, collective communication, conversion kernels or queueing. The next measurement therefore repeats the workload and SLO test rather than inferring a gain from checkpoint size. More KV headroom can permit a larger batch, but a larger batch can also increase waiting time or decode-step duration. The useful operating point is the one that preserves task quality and request-level SLOs, not the one that fills the most memory. Chapter 7's storage sensitivity and Figure QF2 describe an input to this decision, not its performance result.

## Placement G — Chapter 18, quality/cost routing discussion

File: `design/manuscript/chapter-18/chapter-18.md:129–149`. Add the following bridge without duplicating existing goodput definitions.

A routing candidate is a validated deployment variant, not only a model family. A lower-precision variant can lower resource use, but its quality loss may appear selectively in reasoning, code, tool arguments or long contexts. Retries and longer generations can consume the apparent savings. The routing table therefore attaches quality and SLO evidence to the exact precision/backend combination, and the fallback preserves the task's acceptance conditions. A change to scales, excluded layers or execution kernels creates a new candidate for validation; it does not inherit the previous candidate's quality curve automatically. (Q29, Q35, Q37.)

## Placement H — Chapter 26, after the workload-to-strategy matrix

File: `design/manuscript/chapter-26/chapter-26.md:23–40`. Add a compact decision paragraph, not a second taxonomy.

The quantization ADR names the active constraint, the affected tensors and the proposed deployment configuration. Its resource ledger includes metadata, retained high-precision tensors, KV and peak workspace. Its acceptance conditions include task quality, request-level SLOs and rollback. Chapter 7 explains the representation; Chapter 11 establishes execution compatibility; Chapter 14 verifies the candidate. A recommendation becomes defensible when those three records agree, not when a format name appears in a support matrix.

## Separately dated implementation note — not part of the August snapshot

Proposed location: a new dated numerical-format/implementation note adjacent to, but not silently merged into, Appendix A (`design/manuscript/chapter-27/chapter-27.md`, which is frozen to 2026-08-30). Heading: “Quantization implementation observations — 2026-10-28”. Do not alter the appendix's four-family comparison.

Current implementations illustrate why representation and execution are separate. At vLLM commit `41dd82e6a7392ead33b1e8a7d175442511e488ca`, NVFP4 has a CUTLASS low-bit path, a Marlin W4A16 path and a higher-precision emulation path. Its MXFP4 Marlin code explicitly ignores a requested activation-quantization configuration because that kernel is weight-only. These are different execution experiments even when the stored weights use the same named representation. They are code observations, not benchmarks or proof that a particular installed release selects the native path. [1P][FACT] ([NVFP4 CUTLASS](https://github.com/vllm-project/vllm/blob/41dd82e6a7392ead33b1e8a7d175442511e488ca/vllm/model_executor/kernels/linear/nvfp4/cutlass.py); [NVFP4 Marlin](https://github.com/vllm-project/vllm/blob/41dd82e6a7392ead33b1e8a7d175442511e488ca/vllm/model_executor/kernels/linear/nvfp4/marlin.py); [MXFP4 Marlin](https://github.com/vllm-project/vllm/blob/41dd82e6a7392ead33b1e8a7d175442511e488ca/vllm/model_executor/kernels/linear/mxfp4/marlin.py); Q19–Q21.)

The same separation appears in GGML/llama.cpp. At the pinned revision in the source ledger, `block_q4_K` occupies 144 bytes for 256 values: 4.5 effective bits/value. `Q4_K_M`, however, selects a mixture of tensor encodings and can promote selected tensors to Q6_K. IQ encodings have their own grid, sign, lookup and scale layouts; their imatrix requirements are type-specific. The complete model's average precision therefore follows a tensor inventory, not one block's byte rate. GGML's `block_nvfp4` also has a specific scale layout; the name alone does not establish interoperability with NVIDIA's tensor-global-scale representation. [1P][DERIVED][ANALYTICAL] ([block definitions](https://github.com/ggml-org/llama.cpp/blob/8ca4060b7e30e76baaa5670ee1ec1b760b7f8552/ggml/src/ggml-common.h); [tensor selection](https://github.com/ggml-org/llama.cpp/blob/8ca4060b7e30e76baaa5670ee1ec1b760b7f8552/src/llama-quant.cpp); Q06–Q08, Q15.)

Post-training calibration and training-based recovery also describe different work. PTQ estimates quantization parameters without a full model-training run; the particular algorithm can search scales or compensate weight errors. QAT updates model parameters while accounting for quantization effects. QAD additionally uses teacher targets to recover behavior. That recovery consumes training compute and memory, and a favorable fake-quant evaluation still needs confirmation after export through the real serving kernels. Calibration, recovery and inference therefore receive separate resource ledgers and separate quality records. [1P][DERIVED] ([Model Optimizer QAT/QAD example, pinned revision](https://github.com/NVIDIA/Model-Optimizer/blob/580ffff1cddb9b20a38b7434e6290654ebf96a8f/examples/llm_qat/README.md); Q29.)

An NVFP4 training recipe need not have the same storage arrangement as Figure QF2's common 1D inference example. Transformer Engine documents two-dimensional 16×16 weight scaling, as well as gradient-specific stochastic rounding, transformations for weight-gradient computation and high-precision treatment of sensitive layers. These are additional recipe choices, not properties supplied by the four-bit value code. Training can also require multiple tensor orientations, higher-precision state and temporary buffers. The unique scale information of a 2D block is therefore not a prediction of resident training memory, nor a reason to reuse an inference footprint as the training budget. [1P][DERIVED] ([Transformer Engine NVFP4](https://docs.nvidia.com/deeplearning/transformer-engine/features/low_precision_training/nvfp4/nvfp4.html); Q14.)

OCP MicroXcaling 1.1 is dated 2026-10-09 and renames E8M0 to UE8M0 while clarifying conversion and boundary behavior. That revision is later than the book's cutoff. Figure QF2 deliberately uses the 1.0 E8M0 terminology; a future revision can update the terminology with its date explicit. Current Model Optimizer recipes also combine AWQ-lite error control with either INT4 or NVFP4 representations. This is evidence that the method and representation are combinable axes, not that every method/container/backend combination is available. [1P][FACT] (OCP-V11, MO-AWQ-PRESET and MO-NV-AWQ-PRESET in [source-index.md](source-index.md); Q11, Q28.)

## Editorial integration checks still required

- Resolve local QF1/QF2 to final figure numbering and book citation IDs without dropping primary-source URLs or revision limits.
- Keep October implementation evidence in its dated note, or add pre-cutoff tag/commit evidence before moving specific implementation claims into the August snapshot.
- Check the actual integrated Letter pages: figures, captions, table width, page breaks and cross-references. The isolated assets have their own QA; they have not been integrated into the rendered manuscript.
- Run workload quality and performance tests before adding deployment gains, winners or native-support claims. No inference results were produced in this assignment.
