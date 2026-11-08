# Proposed insertions — Intel backend qualification

Editorial status: developed English text and an original rendered figure, not applied to the manuscript. Existing H100 worked examples remain intact. Evidence snapshot for new version/product statements: 2026-10-28 UTC. The existing Appendix A cutoff remains 2026-08-30 with its separately labeled September observation. Claim IDs refer to claims.json; reference numbers refer to citation-ledger.json.

## Integration map: exact current source anchors

Paths are relative to the repository. Line numbers are discovery aids; quoted headings and anchors control because other manuscript editors are active.

| ID | Proposed location | Operation and purpose | Duplication control |
|---|---|---|---|
| IX-T0 | chapter-05/chapter-05.md, §4 Measurement, after model quality/deployment tests (line 115 onward) | Add the model/backend qualification paragraph below | Does not repeat the model-selection or quantization chapters |
| IX-T1 | chapter-08/chapter-08.md, §1 Concept (line 7), after the first hardware-resource discussion | Add identity and backend paragraph | Leaves the H100 roofline and canonical MFU arithmetic unchanged |
| IX-T2 | chapter-07/chapter-07.md, §3 Worked Example, after existing canonical calculation and before §4 Measurement (line 90) | Add a short contrasting memory-fit example | Explicitly not a replacement for the canonical 70B/MHA scenario |
| IX-T3 | chapter-11/chapter-11.md, after Table 11-2 interpretation paragraph (line 149), before §7 | Add complete-path explanation, checklist, IX-F1 | Does not redraw four serving concerns or explain continuous batching a second time |
| IX-T3-table | chapter-11/chapter-11.md, Table 11-2, supported hardware row (line 147) | Date-qualified correction proposed below; keep as a supplement unless cutoff is updated | Do not silently present October support as August support |
| IX-T4 | chapter-09/chapter-09.md, §1 paragraph beginning “Communication in a distributed LLM system” (line 9), and §4 Measurement (lines 81–83) | Replace universal NVIDIA topology language with bounded examples; qualify collective tooling | Retain ring semantics and directional arithmetic; do not redo calculations being edited by another reviewer |
| IX-T4b | chapter-10/chapter-10.md, §5 Common Mistakes, bullet “TP belongs behind NVLink” (line 117), and §6 first bullet (line 129) | Replace universal fabric requirement with latency/traffic requirement | No new parallelism taxonomy |
| IX-T5 | chapter-14/chapter-14.md, §4 Measurement (line 53); cross-reference from chapter-15 §The Optimization Decision Map (line 50) | Add backend comparison protocol | Does not reproduce the full benchmark suite; ties it to portability |
| IX-T6 | chapter-16/chapter-16.md, §4 Measurement (line 147) | Add support/migration/fallback cost paragraph | Does not add speculative price or fleet calculations |
| IX-T7 | chapter-18/chapter-18.md, §3.1 Hardware capacity mapping (line 45); cross-reference from chapter-20 §4 Measurement (line 53) and chapter-21 §4 Measurement (line 55) | Add qualification-before-placement paragraph | Same promotion gate, not a second ops framework |
| IX-A1 | chapter-27/chapter-27.md, after the last existing technical subsection and before §8 First-hand Sources (line 151) | Add boxed October supplement below, with its own references | Preserve August and September dates; do not renumber existing snapshot claims as if freshly revalidated |

All chapter paths above are under design/manuscript/. Chapters 05, 07–18, 20, 21 and 27 were read substantively during this investigation. These are source-text integration proposals, not verified positions in a newly typeset book. The immutable proof remains 361 pages, US Letter, SHA256 66f8392d6b768de7af4695b3d93d70b48858eb75a944020dbcfa9f4d1768b758.

## IX-T0 — Model identity includes the execution path

A model name alone does not define a deployable artifact. The relevant identity includes the checkpoint revision, tokenizer, numerical representation, engine revision and device backend. A loader may recognize the model while a fused attention operator, recurrent-state update or quantized expert kernel is unavailable on the target device. A fallback can restore execution but change latency, memory use or numerical behavior. We therefore separate model-quality acceptance from backend qualification. Both must hold for the same configuration. A small successful completion does not validate long-context state, concurrent-request isolation or the intended serving SLO. [4][49][52]

Claims: IX-022, IX-024, IX-030.

## IX-T1 — A resource model survives a backend change; an implementation may not

The compute and memory equations apply across accelerator vendors. Their constants belong to a specific device and execution path. A peak INT8 dense TOPS figure does not describe BF16 throughput, a sparse peak does not describe a dense workload, and aggregate device memory is not one allocation pool. The useful comparison starts with the model's operators, resident bytes and communication pattern. It then asks which kernels implement those operations on the candidate hardware. [7][8][11]

In PyTorch, `torch.xpu` names the Intel GPU device backend. It does not name every Intel accelerator. Intel Gaudi uses a separate `hpu` path and software stack. A client NPU can use the OpenVINO NPU plugin rather than the GPU backend. Even within Intel GPU inference, an engine-native SYCL path can bypass PyTorch. oneAPI libraries, SYCL execution and Level Zero provide different parts of the software path; none supplies a serving scheduler by itself. Figure IX-F1 makes these boundaries explicit. [25][47][54][55][66]

This distinction changes a portability decision. A device API can be available while a required model operator or cache layout is not. Source-level portability therefore reduces one part of migration work. It does not establish feature parity, numerical equivalence or sustained performance.

Claims: IX-001–004, IX-018–019, IX-026.

## IX-T2 — A smaller-model counterexample: fit is a gate, not a prediction

Consider an illustrative 8-billion-parameter model stored entirely in FP16. Its raw weights occupy 16 GB. Assume 32 attention layers, eight KV heads per layer, a head dimension of 128 and two bytes per KV element. This is a separate GQA example, not the handbook's canonical 70B attention layout. The KV storage per resident token is

\[
2 \times 32 \times 8 \times 128 \times 2 = 131{,}072\ \text{bytes}.
\]

At 9,500 resident tokens, one sequence needs 1.245184 GB of raw KV. With an explicitly assumed 4 GB reserve for runtime state and workspace, the analytical budget is 21.245184 GB. A nominal 24 GB device passes this preliminary capacity gate. It does not yet pass an allocation or serving test. The reserve is an assumption, and the calculation excludes unmodeled conversion peaks, fragmentation and additional sequences. [ILLUSTRATIVE][DERIVED; arithmetic.json]

The counterexample is equally important. Ideal four-bit storage for 70 billion weights is already 35 GB before scales, alignment, unquantized layers, KV or workspace. Neither a 24 GB nor a 32 GB card holds that unsharded tensor. Two 24 GB cards provide 48 GB in total, but a working placement still needs supported sharding and a feasible budget on each rank. Shared client memory adds another constraint: the installed system capacity must also serve the operating system and other devices. It is not a guaranteed GPU allocation. [30][35][37]

Capacity and bandwidth answer different questions. Reading the illustrative 16 GB of weights once at 456 GB/s takes at least about 35.1 ms in a simple weights-only streaming model. At 608 GB/s, the corresponding value is about 26.3 ms. These are analytical byte-transfer floors, not measured token latencies. They ignore attention, KV traffic, launch overhead and communication, and they assume the nominal bandwidth is achieved. Batching or reuse can also change the bytes moved per output token. Passing the capacity gate therefore justifies a measurement, not a throughput or cost claim. [7][8][30][ILLUSTRATIVE][DERIVED]

Claims: IX-009–012, IX-018. Calculations: build_registry.py → arithmetic.json.

## IX-T3 — The complete backend path

A serving engine needs more than a visible accelerator. It needs a compatible model implementation, numerical representation, attention path, cache management, kernel set, runtime and driver. Distributed execution adds a collective backend and a supported transport. Figure IX-F1 separates these dependencies from the final qualification decision. Its columns are alternatives, not interchangeable APIs. [49][52][54][55][66][67]

![IX-F1. Three accelerator paths and one qualification gate. Solid arrows denote dependencies; dashed arrows bring the complete path to qualification. Intel GPU, Gaudi and client NPU do not share one device API. The GPU column includes PyTorch XPU and engine-native SYCL alternatives. A visible device or a loaded model does not validate memory residency, operators, request isolation, collectives or an SLO. Original conceptual diagram; no measured performance data.](figures/intel-backend-paths.png){width=6.1in}

The distinction matters when an engine changes its implementation without failing the request. OpenVINO GenAI documents a paged-attention path that can fall back to contiguous-cache SDPA if initialization fails. Explicit paged-attention selection can instead make that failure visible. A service that still generates tokens may therefore have lost the cache behavior assumed by its capacity calculation. The resulting concurrency limit and queueing latency must be measured again. This CPU/GPU behavior does not imply the same feature set on the NPU. [36]

Graph execution provides a second example. Capturing work can reduce repeated launch overhead, but it introduces startup work and constraints on supported shapes and operators. A compiler transformation and graph replay are not the same mechanism. The examined SGLang XPU documentation treats decode and prefill graphs separately and marks them experimental and opt-in. The prefill `breakable` path uses segmented capture rather than `torch.compile`. More capture is not automatically better when startup delay or shape diversity dominates. [49]

A compact qualification record can contain seven gates:

1. Exact device, checkpoint, tokenizer, engine and dependency identities are fixed.
2. Each rank fits weights, KV, workspace and temporary conversion state.
3. Required operators, weight/activation/KV formats and attention layouts execute correctly.
4. Scheduling, cache reuse, graph behavior and any fallback are observable.
5. Required collectives work on the deployed topology and message sizes.
6. Long-context quality, concurrent-request isolation and failure recovery pass.
7. Measured tail latency and quality-qualified goodput satisfy the workload contract.

A failure closes the proposed configuration. A different configuration can be evaluated, but a reduced context, changed quality threshold or disabled feature is a changed deployment—not an unnoticed repair to the original result.

Claims: IX-019–027. Figure evidence and editable assets: figures/manifest.json.

### IX-T3-table — Candidate date-qualified table correction

Do not silently edit the August snapshot. If Table 11-2 is explicitly refreshed to the October supplement, its hardware row can read:

| capability | vLLM | SGLang | TensorRT-LLM | llama.cpp | architectural note |
|---|---|---|---|---|---|
| supported hardware | Existing paths plus Intel GPU XPU; version/model dependent | Existing paths plus Intel GPU XPU; version/model dependent | Existing NVIDIA-specific scope unchanged by this investigation | CPU and device-specific backends, including Intel GPU SYCL | Backend coverage is not engine-wide feature parity; see the dated supplement |

This is a narrow correction based on the investigated Intel paths. It does not certify every non-Intel cell in the existing table. [49][52][54][67]

## IX-T4 — Fabric names are examples, not prerequisites

Replacement for the first topology paragraph in Chapter 9 §1:

Communication follows the deployed topology, not a universal vendor hierarchy. A server may connect accelerators through PCIe, a dedicated scale-up fabric, integrated Ethernet links or a combination of paths. NVLink and NVSwitch are NVIDIA examples. Gaudi has a different integrated-network topology. Across hosts, Ethernet/RoCE or InfiniBand may carry traffic, subject to the actual adapter, routing and transport support. The relevant quantities are directional bandwidth, latency, contention and the physical traffic of the chosen collective. A product name alone supplies none of those measurements for a deployment. [11][47]

Addition to Chapter 9 §4:

Collective tests must exercise the backend used by the workload. NCCL tests describe an NCCL path; they do not certify XCCL or HCCL. The examined vLLM XPU configuration uses XCCL with recent PyTorch, while Gaudi exposes HCCL. The test record needs rank placement, data type, message size, transport and a sent/received bandwidth convention. For Gaudi's documented 24 × 200 Gb/s port total, the nominal arithmetic is 600 GB/s per direction or 1,200 GB/s bidirectional aggregate. Neither value is an achieved all-reduce bandwidth. [11][47][67][1P][DERIVED]

Replacement for “TP belongs behind NVLink” and its matching architecture shorthand in Chapter 10:

Tensor parallelism requires a communication path fast enough for its per-layer exchanges. NVLink is one implementation, not a requirement of the algorithm. PCIe or another fabric is viable only when measured collective cost leaves sufficient latency and throughput margin. The feasible split also depends on each rank's memory and supported kernels. A slower link can erase a capacity gain even when the weights fit. [11][54][67]

Claims: IX-002, IX-020, IX-026, IX-028.

## IX-T5 — Two fair comparisons answer different questions

A hardware-isolation comparison holds the model revision, numerical representation, KV format, request distribution and functional features constant. This limits the claim to the tested common path. A deployment comparison can instead use each backend's best available implementation, but all candidates must first satisfy the same quality and service constraints. If one candidate uses a different representation or disables a feature, the result concerns a different complete configuration—not hardware alone.

Both comparisons need cold and warm runs, separate prefill and decode observations, a load sweep, and per-request timing. Request goodput counts successful requests that satisfy quality and every request-level SLO. Token goodput counts the output tokens of those compliant requests over the same wall-clock interval. Timeouts, failed attempts and fallback work still consume resources. A p95 threshold is a configuration-level statistic; it is not itself a count of compliant work. An increase in raw tokens per second can therefore coexist with unchanged or lower goodput.

Graph startup, cache warmth, host-side conversion and request isolation belong in the record. Reasoning workloads also need total generated-token counts and a fixed quality test. Fewer generated tokens can mean less work, not a faster implementation. These controls preserve the interpretation of Chapter 15's optimization map when the backend changes.

Basis: comparison protocol in intel-xpu-research.md §5; no new measured claim.

## IX-T6 — Support cost enters the same denominator

A lower accelerator price does not establish a lower service cost. Migration work, pinned-runtime maintenance, security updates, failed attempts, spare capacity and fallback execution belong in the cost numerator. The denominator remains quality-qualified, SLO-compliant work. A configuration that needs more replicas because its tail latency or usable KV capacity is worse can reverse an apparent device-price advantage.

Software lifecycle changes this calculation. The retrieved IPEX retirement guidance points toward upstream PyTorch, while IPEX-LLM announces archival and known security issues. An archived optimization can remain technically executable while becoming an unsuitable default for a maintained service. Existing deployments need an explicit migration or support decision. Current product prices and a measured service capacity are still required before either backend receives a TCO recommendation. [5][14]

Claims: IX-007–008. No price estimate is proposed.

## IX-T7 — Qualification precedes placement and promotion

Placement starts with feasible configurations, not with a vendor label. A small local model can be a candidate for an Intel GPU or an OpenVINO client path when its operators, memory budget and service behavior pass the same gates as the central service. An integrated GPU and an NPU remain separate choices even when they share a package and system memory. Their advertised compute figures do not form one execution budget. [25][35][37]

A routing policy also needs the cost of failure. If a local attempt misses its contract and falls back to a central service, both attempts contribute resource use and end-to-end delay. The fallback route must preserve the data policy and still meet any applicable deadline. Promotion therefore follows a canary on the exact model/backend configuration, with monitored cache behavior, correctness, tail latency and rollback. Replacing a driver, kernel package or graph mode can change that configuration even when the model identifier is unchanged.

Claims: IX-003, IX-018–019, IX-027. Chapter 20 and Chapter 21 need only cross-reference this paragraph and their existing routing/promotion controls.

## IX-A1 — Boxed dated appendix supplement

> Intel backend supplement — observed 2026-10-28 UTC; outside the 2026-08-30 evidence snapshot.
>
> Observed. The retrieved release APIs identify PyTorch v2.14.1 (September 30), vLLM v0.32.0 (October 18), SGLang v0.5.22 (October 19), OpenVINO Runtime 2026.4.1 and OpenVINO GenAI 2026.4.1.0 (October 1). These are release identities, not one validated combined environment. The examined vLLM XPU requirements pin PyTorch 2.14.0, Triton 3.8.0+xpu and vllm_xpu_kernels 0.1.15.4. Its guide and dependency file disagree on the Triton version, so installation instructions require resolution and testing. [21][22][26][42][53][67][71]
>
> Observed. Intel's March announcement places Arc Pro B70 availability on March 25, 2026 and B65 availability in mid-April. Their datasheets both specify 32 GB and 608 GB/s, but different INT8 dense peaks. Intel's October OCP statement describes GPU D-series, formerly Crescent Island, as sampling. Its footnote distinguishes a 160 GB Intel-branded card from partner options up to 480 GB. General availability and independent performance are not established by that statement. [7][8][13][28]
>
> Interpretation. Upstream device and engine integration make Intel GPU configurations concrete candidates for evaluation. They do not establish parity across models, quantization paths, graph modes, collectives or hardware generations. Gaudi and client NPU paths remain separate. [47][49][54][55][66]
>
> Hypothesis. Intel configurations may offer a useful capacity, energy or cost trade-off for particular workloads. This requires independent measurements at the same quality and SLO. Current upstream support, vendor availability announcements and a local deployment account do not establish a market-share trend or a universal winner. [56][60][61]

## Editorial and verification boundaries

The prose and figure are developed artifacts, not a publication certificate. Integration still requires citation-format normalization, figure numbering, final page/caption placement, and review of the complete rendered book. No inherited H100 performance or TCO result has been revalidated here. All resource examples added above are explicitly sourced specifications or illustrative arithmetic, not invented measurements. The original source snapshots are evidence caches, not a proposed public reproduction of third-party documents.

## References used by the proposed text

<!-- REFERENCES -->

[4] vllm-models — https://docs.vllm.ai/en/stable/models/hardware_supported_models/xpu
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:38:57.549971+00:00. Provenance: upstream_project_first_party_not_independent_performance_validation.

[5] ipex-retirement — https://intel.github.io/intel-extension-for-pytorch/xpu/latest
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:38:57.550787+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[7] b70-datasheet — https://intel.com/content/dam/www/central-libraries/us/en/documents/2026-03/datasheet-b70-gpu.pdf
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:38:58.006118+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[8] b65-datasheet — https://intel.com/content/dam/www/central-libraries/us/en/documents/2026-03/datasheet-b65-gpu.pdf
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:38:58.021078+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[11] gaudi3-whitepaper — https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:39:34.007182+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[13] b70-launch — https://intel.com/content/www/us/en/newsroom/news/client-computing/intel-core-ultra-series-3-with-vpro-powers-next-gen-pcs-on-18a.html
    Publication/release: 2026-03-25. Retrieved UTC: 2026-10-28T06:39:34.010078+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[14] ipex-llm — https://raw.githubusercontent.com/intel/ipex-llm/main/README.md
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:39:35.229808+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[21] vllm-release — https://api.github.com/repos/vllm-project/vllm/releases/latest
    Publication/release: 2026-10-18T06:50:48Z. Retrieved UTC: 2026-10-28T06:40:03.034342+00:00. Provenance: upstream_project_first_party_not_independent_performance_validation.

[22] pytorch-release — https://api.github.com/repos/pytorch/pytorch/releases/latest
    Publication/release: 2026-09-30T19:14:48Z. Retrieved UTC: 2026-10-28T06:40:03.035011+00:00. Provenance: upstream_project_first_party_not_independent_performance_validation.

[25] openvino-doc — https://docs.openvino.ai/2026/openvino-workflow-generative/inference-with-genai.html
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:40:03.285638+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[26] openvino-release — https://api.github.com/repos/openvinotoolkit/openvino/releases/latest
    Publication/release: 2026-10-01T13:45:59Z. Retrieved UTC: 2026-10-28T06:40:03.326425+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[28] ocp2026 — https://www.intel.com/content/www/us/en/newsroom/news/artificial-intelligence/intel-accelerates-open-infrastructure-agentic-ai-era.html
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:42:10.169726+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[30] b60-datasheet — https://download.intel.com/newsroom/2025/client-computing/Intel-Arc-Pro-B60-Data-Sheet.pdf
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:42:10.171465+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[35] panther388 — https://www.intel.com/content/www/us/en/products/sku/245526/intel-core-ultra-x9-processor-388h-18m-cache-up-to-5-10-ghz/specifications.html
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:42:16.207899+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[36] ov-continuous — https://openvinotoolkit.github.io/openvino.genai/docs/concepts/optimization-techniques/continuous-batching
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:42:18.159634+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[37] ov-memory — https://docs.openvino.ai/nightly/openvino-workflow/running-inference/optimize-inference/managing-igpu-memory-usage.html
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:42:18.523796+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[42] sglang-release — https://api.github.com/repos/sgl-project/sglang/releases/latest
    Publication/release: 2026-10-19T02:55:19Z. Retrieved UTC: 2026-10-28T06:43:06.657637+00:00. Provenance: upstream_project_first_party_not_independent_performance_validation.

[47] gaudi-ccl — https://docs.habana.ai/en/latest/API_Reference_Guides/HCCL_APIs/index.html
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:43:07.171812+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[49] sglang-pinned-doc — https://raw.githubusercontent.com/sgl-project/sglang/a1966e1b5d8b750b494d7e53cca1d2464f960038/docs/docs/hardware-platforms/xpu.mdx
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:46:42.644037+00:00. Provenance: upstream_project_first_party_not_independent_performance_validation.

[52] vllm-pinned-xpu — https://raw.githubusercontent.com/vllm-project/vllm/5df63a7203cdb9328d824a27b682e77c7b9928be/vllm/platforms/xpu.py
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:46:42.646991+00:00. Provenance: upstream_project_first_party_not_independent_performance_validation.

[53] vllm-pinned-req — https://raw.githubusercontent.com/vllm-project/vllm/5df63a7203cdb9328d824a27b682e77c7b9928be/requirements/xpu.txt
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:46:42.654940+00:00. Provenance: upstream_project_first_party_not_independent_performance_validation.

[54] llama-pinned-doc — https://raw.githubusercontent.com/ggml-org/llama.cpp/8ca4060b7e30e76baaa5670ee1ec1b760b7f8552/docs/backend/SYCL.md
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:46:42.818624+00:00. Provenance: upstream_project_first_party_not_independent_performance_validation.

[55] gaudi-port — https://docs.habana.ai/en/latest/PyTorch/PyTorch_Model_Porting/Porting_PyTorch_Models_to_Gaudi.html
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:46:42.826573+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[56] ibm-gaudi — https://newsroom.ibm.com/blog-intel-and-ibm-announce-the-availability-of-intel-gaudi-3-ai-accelerators-on-ibm-cloud
    Publication/release: 2025-03-31. Retrieved UTC: 2026-10-28T06:46:42.843413+00:00. Provenance: commercial_provider_first_party_announcement.

[60] embeddedllm-b60 — https://embeddedllm.com/blog/benchmarking-llm-inference-intel-arc-pro-b60
    Publication/release: 2026-02-14. Retrieved UTC: 2026-10-28T06:47:01.401203+00:00. Provenance: third_party_experiment_hardware_provided_by_Sparkle_with_Intel_technical_support.

[61] linville-arc — https://bentech.substack.com/p/running-local-llms-on-intel-arc-pro
    Publication/release: 2026-04-13. Retrieved UTC: 2026-10-28T06:47:01.402066+00:00. Provenance: independent_author_self_report_not_independently_reproduced.

[66] torch-pinned-md — https://raw.githubusercontent.com/pytorch/pytorch/5c4886908584029761b579af026dcfb627c84070/docs/source/notes/get_start_xpu.md
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:47:53.081489+00:00. Provenance: upstream_project_first_party_not_independent_performance_validation.

[67] vllm-pinned-xpu-guide — https://raw.githubusercontent.com/vllm-project/vllm/5df63a7203cdb9328d824a27b682e77c7b9928be/docs/getting_started/installation/gpu.xpu.inc.md
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:47:53.082687+00:00. Provenance: upstream_project_first_party_not_independent_performance_validation.

[71] openvino-genai-release — https://api.github.com/repos/openvinotoolkit/openvino.genai/releases/latest
    Publication/release: 2026-10-01T13:52:44Z. Retrieved UTC: 2026-10-28T06:47:53.274463+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.
