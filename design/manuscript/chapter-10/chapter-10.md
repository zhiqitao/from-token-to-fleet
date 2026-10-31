# Chapter 10 — Parallelism: Splitting the Model Across Machines

## The Architect's Question

After this chapter we should be able to answer the inevitable scaling question: *a single GPU cannot hold this model or keep up with this workload — how do we split the work across many GPUs, and which split is right?* We will build the arithmetic for why a model outgrows one GPU, then study the five parallelization strategies — tensor, pipeline, data, expert, and sequence parallelism — plus a serving-only sixth (P/D disaggregation, which has no training counterpart), and develop a rule for choosing among them based on the model's weight-residency, the workload's batch shape, and the interconnect speed. After this chapter, "we scaled it out" becomes a precise claim about *what* was split and *why*.

## 1. Concept

The central idea: parallelism is **splitting one of the three things a model occupies — its weights, its layers, or its data — across multiple devices.** Before reading on, one framing note that prevents a common source of confusion: **the parallelism toolkit differs between training and inference, and "data parallelism" means different things in each mode.** In *training*, DP means replicated weights plus gradient all-reduce every step (plus FSDP, which shards and re-gathers weights/optimizer state); the communication load is at the gradient-sync point. In *inference*, DP simply means running independent model replicas to raise throughput — there is no gradient sync at all, because each request is served by one replica. There is also an inference-specific family — context/pipeline partitioning, expert parallelism, and **P/D disaggregation** (splitting the prefill stage from the decode stage into separate pools) — which has no training analogue. The rest of this section defines the strategies, and §10.3 applies them to inference (the book's canonical serving context) unless a strategy is explicitly training-only.

The strategy names tell us what gets split:

1. **Tensor parallelism (TP)** splits a single layer's weights across GPUs. Each GPU holds a slice of the weight matrix and exchanges partial results through the TP group's interconnect. These layer-level dependencies require sufficient measured bandwidth and low latency; NVLink is one implementation, not an algorithmic requirement. TP is *intra-layer*. (Inference: shards weights; per-step exchange is activations, not weights — see Ch. 9.)

2. **Pipeline parallelism (PP)** splits the model's layers (stages) across GPUs. GPU 1 runs layers 1–10, GPU 2 runs 11–20, and so on; activations flow forward, gradients flow backward. PP is *inter-layer*, communication-light, but idle bubbles appear at stage boundaries. (Inference: can split decode stages; bubbles hurt latency-sensitive serving more than training.)

3. **Data parallelism (DP)** — *different in the two modes.* Training: replicates all weights on every GPU, feeds each a different batch, all-reduces gradients after each step; communication-heavy only at the gradient-sync point, but each GPU must hold the full model. Inference: independent replicas each serve a disjoint set of requests; no gradient sync; throughput scales linearly until KV or memory binds (Ch. 17).

4. **Expert parallelism (EP)** shards the experts of a Mixture-of-Experts model across GPUs and routes each token to the GPU holding its experts — an all-to-all exchange per token. EP is MoE-specific. (Used in both training and inference for MoE models.)

5. **Sequence/context parallelism (CP)** splits the sequence dimension across GPUs, useful for very long contexts where the KV cache or attention activations exceed one GPU. (Inference-centric; the serving analogue of training sequence parallelism.)

6. **P/D disaggregation (inference)** — separates the compute-bound prefill stage from the bandwidth-bound decode stage onto different GPU pools so each can be sized and scaled independently (Ch. 11). This has no training counterpart and is a serving-only strategy.

These are not alternatives; production systems **compose** them (e.g. DP across nodes × TP within a node × PP across a few nodes; or TP+CP within a decode pool + a separate prefill pool). The architect's job is deciding which dimension to split first, and in which mode (training vs inference) the parallelism is being applied.

![Fig 10.1 — Three parallelism patterns, one per panel: tensor parallel shards one layer's weights (activations replicated; partial sums all-reduced every layer), pipeline parallel splits the layer stack into stages (hidden states move P2P; an idle bubble at fill/drain), and data parallel replicates the model while splitting the batch (training all-reduces gradients; inference replicas run unsynced). Each panel names what splits, what is replicated, and what communicates. **Communication-specificity note:** the TP collective is *algorithm-dependent* — a plain all-reduce of partial sums is one option, but fused kernels often use reduce-scatter + all-gather (or a single all-reduce) depending on the framework; the PP bubble size depends on *microbatch scheduling* (more microbatches shrink the bubble but add memory). The panels show the canonical configuration (TP all-reduce per layer; PP with a small fixed microbatch count); substitute the actual collective and schedule for the target stack. **Grayscale note:** each box's text label carries its role, so the in-figure color key (blue = weights · orange = GPU · green = data · red = comms) is redundant, not load-bearing. [ILLUSTRATIVE conceptual]](figures/fig-10-1001.png)

The strategies are not either/or. Fig 10.1 shows the three canonical patterns side by side. **Tensor parallel** shards one layer's weight matrix across GPUs — activations are replicated, and each GPU's partial sums are all-reduced at layer-level dependencies in the illustrated layout. Those frequent exchanges make measured collective latency and throughput margin important. **Pipeline parallel** cuts the layer stack into stages on different GPUs — hidden states cross stage boundaries point-to-point, an idle bubble appears as the pipeline fills and drains, and the communication can span nodes if the stage-boundary transfer meets its budget. **Data parallel** replicates the whole model and splits the batch — in training every replica all-reduces its gradient each step; in inference the replicas are independent, each serving a disjoint slice of requests with no sync at all. Expert and sequence parallelism (EP/CP) are additional axes that reuse the same machinery. The three primary patterns **compose** (e.g. DP across nodes × TP within a node × PP across a few nodes) — which dimension binds determines which to split first.

## 2. Mental Model

Each strategy is best distinguished by *what it trades bandwidth for*. Tensor parallelism exchanges layer results to distribute weight residency but adds synchronization dependencies. Pipeline parallelism transfers stage-boundary activations and accepts bubbles as the price of not holding all layers on one GPU. Training data parallelism trades gradient bandwidth for replicated weights; inference replicas have no gradient synchronization. In either mode, each replica's assigned devices must fit its state.

The useful mental model is a **resource triangle**: we have weights (memory), activations (work), and data (batch). Each strategy moves one corner off a single GPU at the cost of communication. When a GPU runs out of *memory*, we reach for TP/PP (weight splitting). When a GPU is *idle* waiting, we reach for DP/CP (more work per GPU). When the model is *too big to replicate*, TP wins over DP. The binding constraint chooses the strategy.

#### Table 10-1 — Parallelism strategies at a glance

| Strategy | What it splits | Replicates | Communicates | Fits when |
|---|---|---|---|---|
| Tensor (TP) | a layer's weights within a GPU group | activations | layer-result collectives; fabric-dependent cost | weight shards fit; measured exchange meets the SLO |
| Pipeline (PP) | the layer stack into stages | hidden states | hidden states → P2P (stage boundaries only) | model spans nodes |
| Data (DP) | the data batch | model + optimizer | gradients → all-reduce (per step) | model fits one GPU, need throughput (the canonical 70B is 140 GB > 80 GB per GPU, so it does not fit one GPU — DP is not its baseline; see §10.3) |
| Expert (EP) | MoE experts | attention / weights | routes → all-to-all (per token) | MoE models |
| Sequence (CP) | the token sequence | model weights | KV → ring | long contexts, KV too big |

*(Strategies compose; the table names the primary cost each trades.)*

## 3. Worked Example

### Why the Canonical 70B Doesn't Fit One H100

The canonical model is 70B FP16 dense = 140 GB of weights [ILLUSTRATIVE][DERIVED] (reality check: 70 ×10⁹ params × 2 bytes). A single H100 has 80 GB of HBM [1P][FACT]. The arithmetic is immediate:

- The weights alone don't fit on one H100:

$$
140 \text{ GB weights} > 80 \text{ GB HBM}
$$

We need at least $140 / 80 \approx 1.75$ → **≥ 2 GPUs just to hold the weights** (and that's before KV cache, which adds ~2.62 MB/token at FP16 (2.5 MiB) — the 9.2K-token canonical prompt needs ~24.1 GB more (initial KV)). [ILLUSTRATIVE][DERIVED]

The canonical 8×H100 host (640 GB total) fits the weights + KV comfortably, which is why the single-host baseline in earlier chapters works. But if the model grows (say to 400B) or owns more, the split becomes mandatory:

### Tensor Parallelism: Splitting Weights Across GPUs

With tensor parallelism, the 140 GB weight tensor is partitioned across GPUs. Two H100 GPUs would hold 70 GB of weights each, before KV state, activations and runtime overhead. A simplified tensor-parallel forward pass exchanges partial activations rather than gathering the full weights. For an eight-rank ring, one equal-sized all-reduce per layer and no overlap, the bandwidth term is $T_\text{tp} \approx n_\text{layers} \times 2(N-1)/N \times M_\text{act}/B_\text{dir}$. Here $M_\text{act}$ is the full logical activation tensor in bytes contributed by each rank to one collective; for a dense activation it is token count times hidden dimension times bytes per element. The actual number and shapes of collectives depend on the partitioning and kernels. $B_\text{dir}$ is directional effective bandwidth, not the sum of send and receive peaks. H100 advertises 900 GB/s bidirectional per GPU, corresponding to a 450 GB/s peak in each direction; achieved bandwidth requires measurement. Step latency, contention and reduction work are additional costs. [1P][DERIVED]

Tensor parallelism keeps weight shards resident and exchanges layer results. In a row-parallel linear layer, ranks compute partial outputs from their local weight shards; a reduction combines those partial outputs. Other layouts can use reduce-scatter and all-gather instead.[^oct-ccl-meg] The buffer shape, communication precision, group size and number of collective calls determine the byte budget. Ordinary TP decode does not fetch the full model weights over the network again for every token.

Consider a small illustrative decode step with 16 active sequences, one new token per sequence, hidden width 8,192, two-byte BF16 communication and eight TP ranks. Assume two output all-reduces per transformer block — attention output and MLP — 80 blocks, no sequence parallelism, and a balanced point-to-point ring. (The bandwidth term above counts one collective per layer; this budget's two-per-block assumption is why the call count below is 160 rather than 80.) These are explicit teaching inputs, not a measured model configuration. [ILLUSTRATIVE][ASSUMPTION][ANALYTICAL]

Each all-reduce has a logical input of

$$
M = 16 \times 8{,}192 \times 2 = 262{,}144\ \text{B} = 256\ \text{KiB}.
$$

The ring moves $1.75M = 448$ KiB per rank sent and another 448 KiB received — the physical volume moved exceeds the logical payload above.[^oct-ccl-ring] Across 160 calls (two per block × 80 blocks), each rank sends 70 MiB and receives 70 MiB in that one decode step. The ideal byte term is about 0.163 ms at the 450 GB/s directional bandwidth above, or 2.936 ms at an assumed 25 GB/s; neither is an inter-token-latency prediction. The simple ring also contains 160 × 14 = 2,240 communication steps, plus launch, compute dependencies and contention. At this message size, latency and progress can matter more than the large-buffer bandwidth score. This is the forward inference exchange, accumulated per layer — not a training backward pass, and not a whole-model weight transfer. [ILLUSTRATIVE][DERIVED][ANALYTICAL]

The token population is the rows processed in this step, not the full historical context length. Prefill may process many more rows. A different sequence-parallel layout, fused kernel or offload path changes the operation and its schedule. The budget therefore begins with the deployed layer trace, not a fixed "bytes per model" rule. This distinction also changes the economics: a faster nominal fabric may not reduce the host count if launch overhead, compute or memory residency remains binding.

### Pipeline Parallelism: Splitting Layers, Accepting Bubbles

Pipeline parallelism puts stage $P$ on GPU $P$. The cost is the **pipeline bubble**: while the first micro-batch fills the pipeline and the last one drains, stages sit idle. With $P$ stages and $m$ micro-batches, the steady-state **ideal speedup** over a single serial pass is:

$$
\text{ideal speedup} = \frac{m \cdot P}{m + P - 1}
$$

The $P{-}1$ term in the denominator is the bubble: the pipeline fills and drains exactly once per $m$-batch pass, so $P{-}1$ stage-slots are wasted out of the $m \cdot P$ slots each stage would otherwise work. With $P = 4$ stages and $m = 8$ micro-batches, ideal utilization is

$$
\frac{8 \cdot 4}{8 + 4 - 1} = \frac{32}{11} \approx 2.9\times \quad (\text{out of } 4\times)
$$

— a meaningful bubble. Fewer stages or more micro-batches shrink it: with $m = 32$,

$$
\frac{32 \cdot 4}{32 + 4 - 1} = \frac{128}{35} \approx 3.66\times.
$$

The lesson: PP is communication-light (each stage only moves activation boundaries across the fabric) but always pays a bubble that grows with stage count. [ILLUSTRATIVE][DERIVED]

### Data Parallelism: Replicating, Then Syncing Gradients

Data parallelism replicates the 140 GB model on every GPU. For the gradient all-reduce: if the model has 140 GB of weights and we sync gradients after each step across G GPUs, each GPU sends its gradient tensor once per step. The gradient bytes are

$$
\text{grad bytes} = N_\text{params} \times \text{bytes/param} = 70 \times 10^9 \times 4 \text{ B} \approx 280 \text{ GB}
$$

per step (FP32 gradient; the all-reduce moves the gradient once, not weights+gradients). As in Chapter 9, a ring all-reduce moves $2\frac{N-1}{N}$ times the per-rank gradient through each rank, so for $N=8$ the per-rank traffic is $1.75 \times 280 \approx 490$ GB and the sync time is $T_\text{ring} = 2\frac{N-1}{N}\,\text{bytes} / B_\text{eff}$. At 25 GB/s (single 200Gb/s link) that is `490 / 25 ≈ 19.6 s` per step — far too slow if the step takes ~1 s. At the H100 NVLink directional peak of 450 GB/s, the same ideal ring estimate is `490/450 ≈ 1.09 s`. The 900 GB/s bidirectional sum cannot divide a send-only traffic count; this remains a communication model, not proof of training-state fit. The sync cost, not compute, often caps DP at small scale unless the interconnect is fast. [1P][DERIVED]

The 280 GB is the logical FP32 gradient for a full model replica, not a feasible single-H100 allocation. In hybrid DP×TP training, a DP communicator can join matching parameter shards from different replicas. Its per-device buffer size and participating ranks replace the full-replica logical inputs above; the TP group within each replica is a different communicator ([NCCL communicator definition](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/usage/communicators.html)). Chapter 9's separate 140 GB example assumes FP16 gradients, so the two examples must retain their different precision bases.

Two more communication objects complete the picture. For expert parallelism, the population is routed token copies rather than TP partial outputs. With eight EP ranks, 256 local tokens per rank, top-2 routing, hidden width 8,192 and BF16, an illustrative uniform routing model produces 8 MiB of route rows per rank. Seven eighths go remote: dispatch sends and receives 7 MiB per rank. An equal-sized combine doubles those totals to 14 MiB sent and 14 MiB received. This excludes metadata, padding, compression, route deduplication and load skew. A hot destination can dominate completion even when the average byte budget fits. Specialized dispatch/combine implementations may exploit structure that a fixed-count all-to-all does not expose.[^oct-ccl-ep] [ILLUSTRATIVE][DERIVED][ANALYTICAL]

FSDP changes the object again. Its communication can gather a module's parameter shards before computation and reduce-scatter that module's gradients afterward. An illustrative 64 MiB unit split eight ways requires 56 MiB sent and 56 MiB received per rank for a balanced ring all-gather; the same full-size gradient gives the same per-rank reduce-scatter volumes. This is a unit-sized calculation, not a claim that every forward gathers the whole model or every optimizer state.[^oct-ccl-fsdp] [ILLUSTRATIVE][DERIVED][ANALYTICAL]

## 4. Measurement

Four habits anchor the architect:

1. **Measure weight residency before choosing a split.** `bytes = params × bytes_per_param` lands first; it decides whether TP/PP (memory) or DP (replication) is even possible.

2. **Measure the actual collective path.** For the H100 example, 900 GB/s is the bidirectional peak sum, not a directional or sustained rate. Compare measured collective completion times at the deployed message shapes, rank placement and contention. A cluster's bandwidth depends on its links, rail count and topology; the fabric name alone does not determine the gap.

3. **Measure the bubble and the step time.** For PP, log the fraction of idle GPU time (bubble) vs compute. For DP, time the gradient all-reduce as a fraction of step time — if it exceeds ~20%, it caps scaling.

4. **Measure communication overlap.** The best systems overlap all-reduce with the next forward/backward compute. Log the non-overlapped comm time — that is the true cost, not the raw bytes.

## 5. Common Mistakes

- **Splitting with DP when the model doesn't fit.** DP replicates weights; if 140 GB > 80 GB, one DP replica doesn't even fit one GPU. Reach for TP/PP first.

- **Using TP without budgeting its exchanges.** The same byte term is larger at 25 GB/s than at 450 GB/s, but whether it binds depends on message shape, call count and exposed latency. Tensor parallelism requires a communication path fast enough for its per-layer exchanges: NVLink is one implementation, not a requirement of the algorithm.[^oct-ix-t4b] PCIe or another fabric is viable only when measured collective cost leaves sufficient latency and throughput margin — a measurement requirement, not a claim of universal performance for any fabric. The feasible split also depends on each rank's memory and supported kernels; a slower link can erase a capacity gain even when the weights fit.

- **Ignoring the pipeline bubble.** PP's idle stages waste real utilization; the bubble grows with stage count. It is not free.

- **Quoting peak interconnect spec as sustained.** NVLink 900 GB/s is aggregate peak; real all-reduce achieves a fraction. Budget headroom.

- **Treating parallelism as an either/or.** Real systems compose DP×TP×PP; the question is which dimension binds, not which one to use.

## 6. Architecture Consequence

The parallelism strategy is forced by the binding constraint, and that constraint is usually **memory** for large models:

- **A model that exceeds one GPU's memory** must split weights → TP (within a node, over the fabric that actually connects its GPUs — the requirement is measured collective latency and throughput margin, not a vendor fabric name) or PP (across nodes, low comm). Which one depends on whether the model fits a node: fits one node → TP among its GPUs; spans nodes → PP across them, with TP inside each node.

- **A workload with high throughput demand** (like the canonical ~10 rps / 40 rps) → independent inference replicas after the state fits each replica's assigned devices. The canonical 70B fits across an 8×H100 node through intra-host model parallelism; additional replicas address fleet capacity. Gradient synchronization applies only to training or fine-tuning.

- **MoE models** (if chosen per Ch3) push toward EP, because the full expert set must be resident (the active count sets compute per token, not residency) and EP shards the experts across GPUs.

- **The canonical answer**: the book's ~70B/8×H100 baseline uses intra-host TP=8 to distribute the 140 GB weights and serving state. It requires model parallelism within the host, but not cross-host model parallelism. Eight ranks are the chosen baseline, not a minimum derived from weight bytes alone. TP, PP and independent replicas can then be composed according to measured capacity, communication and SLO constraints; their names do not establish a universal escalation order.

Table 10-1 above consolidates the five parallelization strategies (plus the serving-only P/D disaggregation): reading across a row gives one strategy's full trade-off (what it splits, what it replicates, what it communicates, when it fits), and reading down a column shows how each axis varies across strategies. (Fig 10.1 illustrates the three canonical patterns — TP, PP, DP — side by side; the table adds the specialist EP and CP rows.)

<!-- Figure spec: mechanism-first diagram; model shown as weight-matrix + layer-stack + batch; arrows show TP slicing weights, PP stacking stages, DP replicating with all-reduce, EP sharding experts, CP splitting sequence; annotate comm cost + use-case per strategy. -->

## 7. What We Still Don't Know

- **Optimal split for very large MoE or long-context models** is workload- and interconnect-dependent; the exact NVLink-vs-fabric crossover for a given model is unmeasured [UNRESOLVED] — measure on the target cluster.

- **2026 MoE scaling has moved the specialist/EP frontier.** Kimi K3 activates just 16 of 896 routed experts per token (2.8T total / 104B active) via its Stable LatentMoE [1P: arXiv 2607.24653]; Qwen3.8-Flash-Next routes 10+1 of 512 experts (125B total / 6B active) [1P: HF Qwen/Qwen3.8-Flash-Next]. These extreme sparsities (16/896 ≈ 1.8% expert activation) are why expert-parallel and fused cross-expert comm kernels (e.g. MoE expert parallelism with fused compute/communication, as in DeepSeek's DeepEP/TileLang infra) are increasingly central to serving large MoE fleets [1P: arXiv 2606.19348]. For the architect this changes the serving calculus: a frontier MoE's activated footprint (Kimi 104B, Qwen 6B) can be dramatically smaller than its total size, so the *compute* decision is made against active parameters — but the *memory-bound* EP decision (how many experts must be resident) is made against **total** parameters, since the full expert set occupies HBM even when only a fraction is routed per token.
- **Communication-overlap efficiency** in real kernels is hard to predict from spec; sustained all-reduce throughput is a **[HYPOTHESIS]** until measured on the target cluster.
- **The right parallelism for mixed prefill/decode (P/D disaggregated) serving** — where the prefill pool and decode pool may want different splits — is an active research area and a **[HYPOTHESIS]** for this book.

## 8. End-of-Chapter Mini-Case: Diagnosing Why the Grown 400B MoE Is Slow

An architect inherits a deployment where the internal Q&A model (from Ch1's mini-case) has been fine-tuned and grown to a 400B-parameter MoE. The team reports "parallelism is killing us — everything is slow." The architect applies this chapter's lens. First, weight residency: a 400B model needs ~`400e9 ×2 bytes = 800 GB` even before KV — that is ~10×H100 for weights alone (~11 once KV/workspace is included), far beyond one node. **The model necessarily spans nodes; the architect must choose an inter-node decomposition** — often PP and/or EP for MoE — while avoiding expensive cross-node TP where possible (TP benefits from a tightly coupled NVLink-style interconnect; across a slower network its per-layer all-reduce cost grows fast). Within each node, the MoE active weights are small, so the team uses EP to shard experts + TP inside the node. The architect measures the interconnect: the cross-node PP boundary runs over the cluster fabric (not NVLink), so they minimize the number of PP stages to shrink the bubble, and they verify the DP gradient-sync (if fine-tuning) stays under ~20% of step time. The result: a composed PP × EP × TP configuration whose binding constraints (memory across nodes + expert routing) are each addressed by the strategy that trades the right bandwidth. The team's "parallelism is slow" becomes a precise, diagnosed, and fixed split.

[^oct-ccl-meg]: Row-parallel reduction and its collective mappings in NVIDIA Megatron-LM at pinned revision `b9d4e2b2c899ef7a77b482ff81d020b3d328d8ab` (retrieved 2026-10-28 UTC; implementation observation outside the 2026-08-30 snapshot, not an accelerator performance test): https://raw.githubusercontent.com/NVIDIA/Megatron-LM/b9d4e2b2c899ef7a77b482ff81d020b3d328d8ab/megatron/core/tensor_parallel/mappings.py and https://raw.githubusercontent.com/NVIDIA/Megatron-LM/b9d4e2b2c899ef7a77b482ff81d020b3d328d8ab/megatron/core/tensor_parallel/layers.py

[^oct-ccl-ring]: Ring normalization 2(N-1)/N and the algorithmic/bus-bandwidth conventions: nccl-tests PERFORMANCE.md at pinned revision `afd59abab774a6a4b492eb344bd0c845a0b7bb4d` (retrieved 2026-10-27): https://raw.githubusercontent.com/NVIDIA/nccl-tests/afd59abab774a6a4b492eb344bd0c845a0b7bb4d/doc/PERFORMANCE.md

[^oct-ccl-ep]: Dispatch/combine structure in DeepSeek DeepEP at pinned revision `f6aa38fe06cd4a0489e7730365d4e0114970a2f3` (retrieved 2026-10-27): https://raw.githubusercontent.com/deepseek-ai/DeepEP/f6aa38fe06cd4a0489e7730365d4e0114970a2f3/README.md

[^oct-ccl-fsdp]: FSDP `_fully_shard` implementation, PyTorch v2.9.0 tag (retrieved 2026-10-27): https://raw.githubusercontent.com/pytorch/pytorch/v2.9.0/torch/distributed/fsdp/_fully_shard/_fully_shard.py

[^oct-ix-t4b]: NVLink and NVSwitch are NVIDIA scale-up fabric examples, not requirements of tensor parallelism: the Gaudi 3 white paper documents a different integrated-network topology: https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf ; PCIe-attached device backends appear in inspected engine sources — llama.cpp SYCL backend at pinned revision `8ca4060b7e30e76baaa5670ee1ec1b760b7f8552`: https://raw.githubusercontent.com/ggml-org/llama.cpp/8ca4060b7e30e76baaa5670ee1ec1b760b7f8552/docs/backend/SYCL.md ; vLLM XPU installation guide at pinned revision `5df63a7203cdb9328d824a27b682e77c7b9928be`: https://raw.githubusercontent.com/vllm-project/vllm/5df63a7203cdb9328d824a27b682e77c7b9928be/docs/getting_started/installation/gpu.xpu.inc.md (retrieved 2026-10-28; outside the book's 2026-08-30 evidence cutoff).
