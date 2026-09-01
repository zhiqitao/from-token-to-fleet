# Chapter 9 — Communication

## The Architect's Question

Before we can place a model across multiple GPUs or across a cluster, we need to know what the interconnect can — and cannot — move. This chapter asks: given a model size, a parallelism strategy, and a traffic pattern (all-reduce, all-gather, reduce-scatter), what is the communication time, and does it dominate the compute budget? We will size the hidden bottleneck that often goes unnoticed until the job stalls.

## 1. Concept

Communication in a distributed LLM system is not a single pipe. It is a hierarchy: each GPU talks to its neighbors over PCIe, nodes within a server meet over NVLink/NVSwitch, racks talk over 200/400 GbE RoCE, and cross-rack or cross-data-center traffic rides InfiniBand. Each layer has a distinct bandwidth ceiling, a distinct latency profile, and a distinct cost per gigabyte. The architect must match the collective operation to the layer where the bandwidth is sufficient, because moving the same data over a slower layer adds minutes to training time or inference latency for no computational benefit.

The collective operations that dominate multi-node training and inference are:

- **all-reduce**: every GPU contributes a gradient fragment; the result (the sum, scaled by 1/N) is delivered to every GPU. This is the workhorse of data-parallel and model-parallel training.
- **all-gather**: every GPU contributes a tensor; every GPU receives the concatenation of all fragments. Used when a model split across nodes needs the full weight or KV cache locally.
- **reduce-scatter**: the inverse of all-gather. Every GPU contributes a fragment; each GPU receives a portion of the final result, sized 1/N of the input. Used when the full tensor does not need to reside on any single GPU.

The bandwidth each collective consumes depends on three factors: the data volume (bytes), the number of participating nodes (N), and the interconnect's effective bandwidth in the presence of contention. A 70B FP16 model is 140 GB. An all-reduce of that model across 8 GPUs on a single node moves 140 GB over NVLink; across 8 nodes connected by InfiniBand moves 140 GB (or more, depending on the algorithm) over the fabric. The same 140 GB over a 25 GB/s Ethernet link takes more than 5× the time of the same operation over a 900 GB/s NVLink.

**Table 9-1** — Interconnect hierarchy with bandwidth (bidirectional where applicable), latency, and approximate cost per GB. PCIe Gen5 x16 ~64 GB/s, ~1 µs latency, low cost (integrated); NVLink H100 900 GB/s bisection, ~0.5–1 µs latency, high cost (GPU-attached); Ethernet RoCE2 200/400 Gb/s ≈ 25/50 GB/s, ~10–25 µs latency, moderate cost (standard NICs); InfiniBand HDR 400 Gb/s / NDR 800 Gb/s ≈ 50/100 GB/s, ~2–5 µs latency, high cost (switches, optics). Cost per GB is inversely proportional to bandwidth for fixed-form optics, but system cost includes cables, switches, and rack density trade-offs.


#### Table 9-1 — The interconnect hierarchy

| Layer | Example | Bandwidth (one direction / aggregate) | Latency | Cost | [source] |
|---|---|---|---|---|---|
| Chip-to-memory | HBM3 (H100) | 3.35 TB/s | ~ns | — | [2° FACT] |
| GPU-to-GPU (in-node) | NVLink (H100) | 900 GB/s per GPU, bidirectional aggregate | ~us | high capex | [2° FACT] |
| GPU-to-CPU / NIC | PCIe Gen5 | ~64 GB/s per x16 direction | ~us | low | [2° FACT] |
| Node-to-node (rack) | RoCE / Ethernet 400Gb/s | ~50 GB/s per port | ~us | medium | [2° FACT] |
| Rack/cluster | InfiniBand HDR/NDR | 400/800 Gb/s ≈ 50/100 GB/s per port | ~us | high capex | [2° FACT] |

*(Hierarchy: bandwidth drops ~2–3 orders of magnitude from HBM to the cluster fabric — the reason the interconnect, not the GPU, often binds at scale. Figures are established hardware specs [2° FACT].)*


## 2. Mental Model

Think of the interconnect as a series of concentric rings. The GPU sits at the center, reachable fastest via PCIe. One ring out is the node: GPUs on the same server are joined by NVLink and NVSwitch, forming a high-radix, low-latency mesh. The next ring out is the rack: 10–20 GbE or 100/200/400 GbE RoCE connects nodes. The outermost ring is the cluster or data centre: InfiniBand HDR (400 Gb/s) or NDR (800 Gb/s) stitches racks into a single logical network. A well-designed deployment keeps the heavy collectives (all-reduce, reduce-scatter) on the inner rings and reserves the outer rings for less volume or latency-tolerant traffic.

The arithmetic is relentless. If all-reduce moves 140 GB and the NVLink bisection provides 900 GB/s per direction, **a lower bound** on time is 140 GB ÷ 900 GB/s ≈ **0.16 s [2° DERIVED]** — note the word *lower bound*. The actual completion time of a real collective is higher because a collective is not one flat transfer but a sequence of message-passing and reduction steps across the topology:

$$
T_{\text{collective}} \approx \alpha \times n_\text{steps} + \frac{\text{bytes}}{\beta}
$$

where $\alpha$ is the per-step latency (message setup, synchronization), $\beta$ is the achieved (not peak) bandwidth, and $n_\text{steps}$ is the number of message-passing/reduction hops. (For a flat transfer $n_\text{steps}=1$.) The 0.16 s figure uses only the $\text{bytes}/\beta$ term at peak bandwidth; real NCCL all-reduce on NVLink lands tens of % above it once per-step overhead, ring stages, and topology routing are included. So treat the `bytes ÷ bandwidth` form as a *sizing lower bound*, and reserve measured `nccl-tests` numbers (Section 4) for capacity decisions. The relative ranking between interconnects is what matters most here: if those same 140 GB travel over a 400 Gb/s InfiniBand link (≈ 50 GB/s effective unidirectional) it is ≈ 2.8 s — 18× longer; over 25 Gb/s Ethernet (≈ 3 GB/s unidirectional) ≈ 47 s. The interconnect choice is a first-order determinant of wall-clock time in all cases.

![Fig 9.1 — All-reduce time vs data volume, by interconnect tier [2° DERIVED]](figures/fig-09-0901.png)

*Fig 9.1 — All-reduce completion time as a function of data volume (x-axis, log GB) and interconnect effective bandwidth. The four lines — NVSwitch 1.8 TB/s, NVLink 0.9 TB/s, InfiniBand 0.4 TB/s, Ethernet 0.1 TB/s — are peak-bandwidth lower bounds (α/β caveat in §9.3); the dashed marker sits at the 140 GB weight footprint of a 70B model (≈ 70 GB of weights in BF16 across 8 participants). [2° DERIVED]*
<!-- Figure spec: mechanism-first — illustrate how all-reduce data flows through the interconnect hierarchy (PCIe → NVLink → NVSwitch → InfiniBand → Ethernet), with bandwidth numbers from the text annotated on each link. Used to explain the arithmetic in §9. Concept. -->

## 3. Worked Example

Consider the canonical scenario: one host eight × H100, each GPU holding 140 GB of model weights in FP16. We will run data-parallel training with full model replicas, so every all-reduce moves the full gradient tensor of 140 GB. Let us compute the communication time under three interconnect options.

**Option A — NVLink on a single host.** H100 GPUs provide 900 GB/s bidirectional NVLink bandwidth per GPU, and NVSwitch aggregates bisection bandwidth. For an all-reduce of 140 GB across 8 GPUs on one host, the effective bandwidth is close to the per-link peak because NVSwitch can forward multiple concurrent channels without severe contention. The time is approximately:

$$
T = \frac{\text{bytes}}{B_\text{eff}} = \frac{140 \text{ GB}}{900 \text{ GB/s}} \approx 0.16 \text{ s}
$$

**Option B — InfiniBand HDR across 8 nodes, one GPU per node.** HDR InfiniBand delivers 400 Gb/s per link ≈ 50 GB/s unidirectional after 8b/10b encoding and protocol headers. A ring-all-reduce or tree-all-reduce across 8 nodes will see lower effective bandwidth due to multi-hop forwarding and congestion. A realistic effective bandwidth is roughly 40 GB/s. The time is:

$$
T = \frac{140 \text{ GB}}{40 \text{ GB/s}} \approx 3.5 \text{ s}
$$

**Option C — 25 Gb/s Ethernet (RoCE2) across 8 nodes.** 25 Gb/s ≈ 3.125 GB/s unidirectional. With protocol overhead and multi-node tree contention, a practical effective bandwidth might be 2.5 GB/s. The time is:

$$
T = \frac{140 \text{ GB}}{2.5 \text{ GB/s}} \approx 56 \text{ s}
$$

These numbers illustrate the scale: moving from NVLink to InfiniBand adds ~22× latency, and forcing the same all-reduce over Ethernet adds ~350× latency. In a training job where 100 all-reduce steps run per iteration, the NVLink path adds ~16 s of communication per iteration, the InfiniBand path adds ~350 s, and the Ethernet path adds ~5,600 s. The latter two would effectively serialize the training, turning a minutes-long job into an hours- or days-long one.

The worked example also highlights why model parallelism and pipeline parallelism exist: when a single GPU cannot hold the model, splitting it across nodes moves the communication from the inner rings to the outer rings, and the architect must budget the extra seconds per collective against the savings from fitting a larger model.

## 4. Measurement

Measuring communication in situ is harder than counting tokens, because the bandwidth numbers above are peaks; real systems see lower effective bandwidth due to congestion, operating-system interference, and protocol overhead. Three practical measurements an architect can make:

1. **Bandwidth benchmark per link.** Use `nccl-tests` or `ib_write_bw` / `bwperf` to measure achieved bandwidth on PCIe, NVLink (via NVIDIA's Nsight), RoCE, and InfiniBand. Record the unidirectional and bidirectional throughput for payload sizes matching the collective (typically 1 MB–1 GB). These numbers anchor the arithmetic to the real hardware.

2. **Collective latency and throughput.** Run `nccl-tests` all-reduce micro‑benchmarks varying the number of GPUs (1, 2, 4, 8) and the tensor size (from 100 MB up to 140 GB). Plot time vs. size and extract the slope — that slope is the effective bandwidth the collective will see in production. Compare the slope across 1 node, 2 nodes, 4 nodes, to see where the interconnect ceiling is hit.

3. **End-to-end training iteration time.** Instrument the training loop to separate compute time (FLOPs) from communication time (all-reduce collectives). Many frameworks (PyTorch Distributed, vLLM, Deepspeed) already expose a per-iteration breakdown. The communication time per iteration, divided by the number of all-reduce steps, gives the average per-collective latency, which we can compare against the benchmark numbers above.

The key invariant: always measure on the same hardware and software stack that the production job will use. A benchmark run on a clean VM with no other traffic will overstate the achievable bandwidth compared to a crowded cluster.

## 5. Common Mistakes

- **Assuming peak bandwidth is sustained.** PCIe Gen5 x16 peaks at ~64 GB/s, but a single all-reduce never saturates the full link because the traffic is split across multiple GPUs and multiple links. Measured effective bandwidth is typically 40–60% of peak; design against the measured number, not the spec sheet peak.

- **Placing all-reduce on Ethernet without a bandwidth budget.** A 70B model gradient all-reduce at 25 Gb/s takes ~56 s per step. If the training runs 1,000 iterations, that is ~56,000 s (15.5 hours) spent exclusively in communication. Always compute the per-iteration communication cost before committing to a lower-bandwidth fabric.

- **Ignoring contention from other traffic.** NVSwitch can carry many concurrent channels, but if other collectives (e.g., all-gather for optimizer state) are running simultaneously, the bisection bandwidth is shared. Measure with the full production workload pattern, not an isolated micro‑benchmark.

- **Using InfiniBand as a default without checking the cost–performance ratio.** InfiniBand HDR 400 Gb/s gives ~50 GB/s unidirectional, which is sufficient for many workloads, but the price per GB of optics and cables is 5–10× that of Ethernet. If the communication time is acceptable on RoCE2, the cheaper fabric may be the better architectural choice.

- **Overlooking protocol overhead.** RoCE and InfiniBand use different encoding (8b/10b vs. 128b/130b) and header sizes. A 400 Gb/s InfiniBand link delivers ~380 Gb/s useful payload; a 200 Gb/s RoCE link delivers ~180 Gb/s. The difference matters when we are computing per-second throughput for a fixed data volume.

## 6. Architecture Consequence

The interconnect choice is not a detail to be decided after the model, the parallelism strategy, and the hardware are selected — it is a first-class design variable that shapes all three. If the architecture calls for data-parallel training of a 70B FP16 model across 8 nodes, the all-reduce bandwidth dictates whether the nodes are connected by InfiniBand, 200 GbE, or even 100 GbE. If the budget can accommodate NVLink‑connected hosts, keeping the all-reduce on-node reduces communication time by 2 orders of magnitude compared to any multi-node fabric.

The architecture consequence also flows in the other direction: a tighter communication budget (e.g., target <0.5 s per all-reduce) may force a particular parallelism strategy. We might choose model parallelism (pipeline parallelism, tensor parallelism) to keep the per-collective data volume smaller, or we might accept a slower fabric and reduce the frequency of collectives (e.g., gradient accumulation steps between all-reduce calls). The interconnect bandwidth number is the anchor that makes these trade-offs quantifiable.

Finally, the architecture consequence extends to cost. A cluster of 8 × H100 servers connected by NVSwitch is the highest upfront capital expenditure, but it delivers the lowest per-iteration communication time, which translates to higher throughput per dollar over the life of the cluster. A cluster connected by 200 GbE RoCE has lower capital cost but higher per-iteration communication time, which may increase the total cost of ownership if the training job runs for many weeks. The architect must balance capex vs. opex by way of the communication arithmetic shown in this chapter.

## 7. What We Still Don't Know

- **Contention patterns under mixed workloads.** The benchmark numbers above assume a dedicated collective on a quiet fabric. In a production fleet, other traffic (user requests, other training jobs, KV-cache movement) shares the same links. The effective bandwidth under realistic multi‑job congestion is not yet characterized with a standard suite, and the interaction between all-reduce and RoCE/Ethernet best‑effort traffic can cause tail latency spikes that are difficult to predict.

- **Adaptive collective algorithms.** New collectives (e.g., gradient compression, sparse all-reduce, error‑bounded approximations) claim to reduce the data volume at the cost of a small accuracy loss. The bandwidth arithmetic changes when the data volume is 30 GB instead of 140 GB, but the latency per byte may increase because of compression/decompression steps. The net effect on iteration time is workload‑specific and not yet settled.

- **Optical interconnects and the next generation.** NVLink‑Switch and XNAME are pushing node‑level bandwidth higher (toward 1.8 TB/s aggregate), and optical intra‑rack fabrics (400 Gb/s–800 Gb/s per lane) are entering data centres. The arithmetic base — the relative magnitudes of PCIe, NVLink, Ethernet, InfiniBand — is stable in the near term, but the absolute numbers will shift as new silicon and cable technologies ship. Keep the framework; update the constants.

- **Cross‑domain generalization.** Most published bandwidth measurements use square matrices (all-reduce of a gradient tensor). Diagonal dominant tensors, sparse gradients, or structured compression may exhibit different effective bandwidths because the traffic pattern across links is less uniform. The arithmetic framework applies, but the constants need re‑measurement for the specific tensor shape.

## 8. End-of-Chapter Mini-Case

An architect is asked to design a distributed inference fleet for a 70B parameter model serving user queries at 200 tokens/s per user, with 10,000 concurrent users. The team debates whether to use a single 8×H100 host with NVLink, or to shard the model across 32 nodes connected by 200 GbE RoCE. Before any hardware is ordered, the architect opens this chapter and runs the communication arithmetic.

The per-request all-reduce is not the right model for inference, and neither is a blanket "all-gather the full weights every decode step." It matters which parallelism is in play: ordinary **tensor parallelism (TP)** shards each weight matrix across the GPUs, and every decode step exchanges only the *activations* (not the weights) via collective ops like all-reduce/all-gather of the small activation tensors — weight matrices stay resident and are read in place, they are not re-fetched each step. A different scheme, FSDP-style **weight gathering** (used in training, and in some sharded-inference arrangements) does all-gather weight shards before the forward pass. So the architect must name the scheme before doing the arithmetic. Concretely, for the canonical 8×H100 host the meaningful per-step data movement is a TP all-reduce of the per-layer activations (tens of MBs, not GBs) plus the KV-cache fragment exchange in disaggregated serving — e.g. ~35 GB of KV moved over NVLink (~0.04 s at 900 GB/s) when a P-D sequence transfers context between prefill and decode pools. The distinction changes the answer by orders of magnitude: re-fetching 140 GB of weights each step is pathological (that is a design smell, an anti-pattern to flag, not a baseline); exchanging activations or KV fragments is the normal case that fits comfortably within NVLink.

The architect proposes the single 8×H100 host (TP within the node, so intra-node NVLink carries the per-step activation all-reduce) for the core serving fleet, with a fallback to a 32‑node RoCE cluster only if KV concurrency or memory capacity exceeds one host (Chapter 17). The communication arithmetic made the trade-off explicit: TP activation exchanges are tens of MB and free within NVLink; cross-node weight/KV shuttling is 35× more expensive and avoided unless the fleet genuinely spans hosts. The design is now grounded in bandwidth and the *specific* parallelism scheme, not in vague notions of "scale."

---