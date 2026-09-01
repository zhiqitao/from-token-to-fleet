# Chapter 12 — Designing the AI System: From Constraints to Candidates

## The Architect's Question
Designing an AI system means producing candidate architectures from the substrate — memory, compute, communication, and parallelism — rather than selecting a canned stack. This chapter works through a synthesis method: given a characterized workload from the six-dimension framework (Ch. 4), generate two or three candidate architectures that each satisfy the hard constraints (memory fit, latency budget, economics), then carry them forward for evaluation in Chs. 14–16. The core thesis is that design is constraint-driven generation, not menu-picking. This distinguishes our approach from the abstract meta-method presented in Ch. 22, which operates at a level of generality that does not instantiate against concrete substrate constraints. In the language of the book's spine — the decision loop *constrain → synthesize → measure → decide → refine* — this chapter is the **synthesize** step: we turn a constraint-characterized workload into a bounded set of candidate architectures that then enter the measure/decide stages in Chs. 14–16.

## 1. Concept
The architect's first step is to reverse-engineer the workload into its constituent constraints. From the six dimensions — quality requirements, traffic profile, token profile, latency budget, economic ceiling, and operational constraints — we extract the three hard constraints that any candidate must satisfy: (1) the total weight memory must fit the target residency budget, (2) the KV-cache footprint plus weight memory must fit the host's aggregate memory, and (3) the total request latency (prefill + decode) must stay within the budget. Any architecture that violates any one of these is eliminated before evaluation. This constraint-first posture inverts the typical practice of browsing vendor offerings and then hoping they fit; instead, we generate architectures that we know can physically reside and operate within the specified substrate.

## 2. Mental Model
Think of the substrate as a set of bounded resources and the architecture design problem as a packing exercise. The resources are: GPU memory (weight residency + KV cache), memory bandwidth (prefill throughput), inter-GPU communication volume (for parallelism schemes), and the latency budget split between prefill and decode. A candidate architecture is a valid packing of the workload's weight memory and KV-cache into the available GPU memory, paired with a parallelism and caching strategy that delivers the required tokens-per-second throughput within the latency budget. The architect alternates between squeezing the residency footprint (e.g., via KV quantization or precision reduction) and adjusting the parallelism layout (e.g., parameter vs. data vs. pipeline) until all three hard constraints are simultaneously satisfiable. This mental model — substrate as packing problem — is what enables systematic candidate generation rather than ad hoc selection.

## 3. Worked Example
We generate three candidate architectures for the canonical enterprise-Q&A RAG workload: ~10 requests/s average, peak 40 rps, 70B FP16 model, 9.2K token input (1,200 prompt + 8K retrieved context), 300-token output. The canonical weight memory is 140 GB (70B × 2 bytes FP16). The KV-cache for 9.2K context at FP16 precision ([1P §14]) is approximately 24 GB (2 × num_layers × hidden_dim × 9,200 × 2 bytes / scale factor), giving a total residency of 164 GB. A single 8×H100 host provides 640 GB aggregate memory (8 × 80 GB), leaving ample headroom. Each candidate satisfies the three hard constraints differently.

**Candidate (a): single 8×H100 host with prefix caching (Ch. 11).**  
All 70B weights and the full 24 GB KV cache reside on the 8-GPU host. Prefix caching from Ch. 11 amortizes the prefill attention over repeated requests with the same prompt prefix, reducing effective prefill FLOPs by ~30% at 10 rps average and ~50% at peak 40 rps when many requests share common document roots. The 8×H100 host fits the full 164 GB residency easily, but on *throughput* we must be honest with the Chapter 8 arithmetic: a single node sustains only ~2,471 prefill-tokens/s, far below the ~92K input tokens/s the workload needs on average — prefill is compute-bound here, and meeting it is exactly the scaling problem Chapters 15–17 take up. Memory fit and throughput fit are different gates: the memory gate passes with one host; the throughput gate does not. Memory fit: 140 GB weights + 24 GB KV = 164 GB < 640 GB aggregate ([1P §14]). Latency budget: prefill + decode stay within budget thanks to prefix caching and the high bandwidth of 8×H100. Economics: one host purchase, one software license tier.

**Candidate (b): P/D-disaggregated two-pool.**  
We keep the full 70B model in both pools and split by *phase* — which is what prefill/decode (P/D) disaggregation actually means (Chapter 11): a compute-bound prefill pool and a bandwidth-bound decode pool, each holding the complete 140 GB weights plus the in-flight KV, with the KV hidden-state handed between them (Splitwise / DistServe / Mooncake). Each pool therefore needs its own 8×H100 host (residency ~164 GB — weights plus one request's KV — comfortably under 640 GB). The win is that prefill and decode no longer fight over the same host's resources: the prefill pool runs FLOPS-saturated on the 9.2K input, the decode pool runs bandwidth-saturated on the 300 output tokens, and KV crosses between them. The cost is a second host plus the KV-transfer fabric and orchestration, so this pays only once the workload actually outgrows a single host (Chapter 11's “when to disaggregate”). Economics: two hosts and added fabric; it is the right architecture at scale, not for the single-host canonical case.

**Candidate (c): KV-quantized smaller host.**  
We downgrade to a 7B-class model (7B × 2 bytes = 14 GB weights) with KV-cache quantized to 4-bit, yielding a KV footprint of ~6 GB for 9.2K context. Total residency: 14 GB + 6 GB = 20 GB, which fits on a single H100 (80 GB) with 60 GB of headroom for overhead. The trade-off is a significant quality drop: the 7B model cannot achieve the same answer quality on complex enterprise Q&A as the 70B model, even with retrieval augmentation. To compensate, we apply KV-quantization at 4-bit, which recovers most of the lost quality relative to unquantized KV, but the model's intrinsic capacity remains the binding constraint. Throughput on a single H100 is far higher than on the 70B — a 7B prefill costs only ~14 GFLOP/token, so one card sustains tens of thousands of prefill tokens/s (vs ~2,471 for the 70B node, Chapter 8) — yet even that cannot change the verdict: at peak 40 rps the workload needs ~368K input tokens/s, so satisfying peak prefill still needs more than a handful of cards, and the 7B's quality ceiling on complex enterprise Q&A remains the binding constraint regardless of throughput. This candidate illustrates the extreme end of the KV-quantization space: the memory footprint is trivially small, but neither quality nor throughput makes it competitive for this workload.

*Memory/residency arithmetic summary.* The canonical weights (140 GB) + KV (24 GB FP16) = 164 GB fits 640 GB (8×H100). Candidate (a) uses the full host with room to spare. Candidate (b) keeps the full model in each pool, so each 8×H100 host also holds ~164 GB. Candidate (c) fits 20 GB on one H100, but its quality ceiling rules it out for the quality target.

## 4. Measurement
To validate a candidate architecture, the architect must derive three numbers from first principles and verify them against the substrate:
1. **Weight memory.**

$$
W = N \times \text{bytes-per-param}
$$

where $N$ is the parameter count and bytes-per-param is 2 for FP16 (replace 2 with bit-width/8 for quantization). Derived fact [2° DERIVED]: $70 \times 10^9 \times 2 \text{ B} = 140$ GB.
2. **KV-cache footprint.**

$$
KV = 2 \times n_\text{layers} \times d_\text{hidden} \times L \times \text{bytes-per-activation}
$$

where $L$ is the context length. For a 70B model with 8-bit KV caching, this is approximately 12 GB for 9.2K context; at FP16 precision it doubles to ~24 GB [2° DERIVED]. The architect should compute this for the exact context length of the workload, not assume a fixed value.
3. **Throughput per device.** Tokens-per-second that a single device can sustain for prefill and decode, measured on the target hardware. This is the number that, multiplied by the number of devices in the candidate layout, must exceed the workload's tokens-per-second demand (92K input tokens/s average, 3K output tokens/s average, 368K input tokens/s peak, 12K output tokens/s peak). Vendors publish peak numbers; the architect should treat these as [VERIFY] benchmarks and measure on equivalent hardware when possible.

All three numbers must be confirmed before a candidate is carried forward ([1P §14]). If any one fails, the candidate is returned to the synthesis step.

## 5. Common Mistakes
- **Menu-picking without constraint validation.** Browsing vendor offerings and selecting the one that "feels right" rather than generating candidates against quantified hard constraints. This is the opposite of the constraint-driven method described here.
- **Ignoring the KV-cache residency arithmetic.** Assuming that the weight memory is the only memory budget item. In input-heavy workloads ([1P §14]: 9.2K average context, 30× more input than output), the KV cache can be 15–20% of total residency and is often the binding constraint.
- **Over-optimizing prefix caching.** Assuming that prefix caching can amortize prefill across all requests. In practice, cache effectiveness depends on the overlap of prompt prefixes across the traffic workload; sparse prefix sharing reduces the realized savings.
- **Using KV-quantization as a free lunch.** Quantizing the KV cache reduces memory footprint but introduces quality degradation that may be unacceptable for the target workload. The architect must measure the quality impact before committing to a quantized KV layout.
- **Forgetting the latency split.** Treating the latency budget as a single number rather than a prefill/decode split. A candidate may meet the total latency budget by trading prefill for decode or vice versa, which may not satisfy the service-level objectives for either leg.

## 6. Architecture Consequence
The three candidates carry forward into the evaluation chapters (Chs. 14–16) with distinct test plans. Candidate (a), the single 8×H100 host with prefix caching, is the baseline: we evaluate throughput, cost-per-token, and latency SLO compliance on a single hardware configuration. Candidate (b), the P/D-disaggregated two-pool, is evaluated on the added complexity of inter-group communication and the pipeline overlap efficacy; we measure whether the latency budget is maintained under the partitioned layout. Candidate (c), the KV-quantized 7B model, is evaluated on the quality-degradation trade-off; we compare answer quality against the 70B baseline and compute the economic break-even point (number of hosts required) against the quality loss. The synthesis method produces these candidates as a set from which the evaluation chapter selects based on quantitative results, not on gut feeling.

## 7. What We Still Don't Know
As of 2026-08, several questions remain open and are flagged [VERIFY]:
- **KV-quantization quality impact at 4-bit for enterprise Q&A.** The quality loss from 4-bit KV quantization has not been systematically characterized across the diversity of enterprise prompts in the canonical workload. [VERIFY HYPOTHESIS]
- **Prefix-caching effectiveness under realistic traffic overlap.** The assumed 30–50% prefill amortization rests on the premise that many requests share document-level prefixes. Empirical measurement of prefix overlap across a production enterprise traffic trace is needed to confirm these numbers. [VERIFY HYPOTHESIS]
- **P/D-disaggregation communication overhead in multi-host settings.** The boundary between parameterparallel and data-parallel placement is relatively unexplored at the 70B scale; the actual communication volume and its latency impact depend on the routing library and network topology. [VERIFY HYPOTHESIS]
- **Whether 8-bit KV caching is sufficient for 9.2K context at FP16-equivalent quality.** The arithmetic in §3 assumes 8-bit KV reduces memory by 2× with minimal quality loss, but the interaction between 8-bit quantization and the retrieval-augmented generation pipeline has not been verified. [VERIFY HYPOTHESIS]

These flags exist because home-lab measurements are not reference per the evidence taxonomy; they will be resolved (promoted, dropped, or demoted) before publication.

## 8. End-of-Chapter Mini-Case
An architect is brought into a design conversation for a company-wide internal Q&A system. The stakeholder states: "We need an AI system that can answer employee questions over our internal documentation, with acceptable quality and within budget." Before any architecture can be defended, the architect applies the constraint-driven method from this chapter.

First, the workload is characterized across the six dimensions. Quality requirements fix the model class: the system must achieve ~70B-model answer quality on enterprise prompts. The traffic profile is estimated at ~500 employees active during business hours, generating ~20 questions/hour peak, ~2 rps average. The token profile is 1,000-token prompts plus 8K retrieved context plus 300-token answers, roughly 9.3K tokens per request. The latency budget is 5 seconds end-to-end. The economic ceiling is $15,000 monthly operating budget. The operational constraint is that the system must run on existing on-premise GPU infrastructure (no cloud add-ons).

From the token profile, the architect computes: 9.3K input tokens + 300 output tokens ≈ 9.6K tokens per request. At 2 rps average and 20 rps peak, the system must sustain ~19.2K input tokens/s average and ~384K input tokens/s peak. The hard constraints are then extracted: weight memory must fit the on-premise GPU inventory; KV cache + weights must fit within that inventory; total tokens-per-second across the installed devices must exceed the peak traffic demand.

The architect generates three candidates using the method from §3. Candidate (a): a single 8×H100 host with 70B FP16 weights + 24 GB KV cache and prefix caching, which fits the memory budget (164 GB < 640 GB aggregate ([1P §14])) — but as Chapter 8 shows, one node sustains only ~2,471 prefill-tokens/s, far short of the ~19.2K input tokens/s the mini-case's ~2 rps average demands, so the memory gate passes while the throughput gate already fails. Candidate (b): a P/D-disaggregated two-pool keeping the full 70B in each pool (prefill and decode pools, each ~164 GB residency on its own 8×H100 host), which buys phase-splitting at the cost of a second host plus the KV-transfer fabric. Candidate (c): a KV-quantized 7B model on a single H100, which fits the memory budget (20 GB total residency) but fails the quality constraint — the 7B model cannot reach the required answer quality regardless of KV quantization — and fails the throughput demand at peak, making it economically non-viable.

The architect discards Candidate (c) immediately: it satisfies the hard memory constraint but violates the quality and economic constraints. Between Candidates (a) and (b), the decision hinges on whether the doubled hardware cost of Candidate (b) is justified by its operational flexibility (e.g., independent scaling of prefill and decode pools, fault isolation). The architect presents both candidates, together with the honest throughput arithmetic of Chapter 8 (no canonical single host meets the full prefill demand alone), to the stakeholder as the decision foundation.

* * *
![Fig 12.1 — Candidate architecture synthesis: three candidate architectures from the canonical enterprise-Q&A RAG workload, comparing memory residency, parallelism plan, and constraint-satisfaction outcome (memory fit, latency SLO, economics) [ILLUSTRATIVE conceptual]](figures/fig-12-1201.png)

### Table 12-1 — Candidate architectures with constraint-satisfaction columns

| candidate | memory (weights + KV) | host layout | throughput | SLO | economics |
|---|---|---|---|---|---|
| (a) 8×H100 + prefix caching | 140 + 24 = **164 GB** | 1 × 8×H100 | prefill ~1,200 · decode ~300 tok/s | ✓ memory 164 < 640 GB · ✓ latency in 5 s | ✓ 1 host |
| (b) P/D-disaggregated | 140 + 24 = **164 GB** per pool | 2 × 8×H100 | prefill pool ~2,471 · decode BW-bound | ✓ memory per host · ✓ phase-split at scale | ✗ 2 hosts + fabric |
| (c) KV-quantized 7B | 14 + 6 = **20 GB** | 1 × H100 | ~tens of thousands · decode > 70B | ✗ fails quality ceiling | ✗ >1 card at peak |

*All figures trace to the §14 canonical scenario; the KV-cache and throughput numbers are [2° DERIVED] worked examples, not measurement claims.*

--- 

*Next chapter: Chapter 13 — Evaluating Candidate Architectures, which subjects the three candidates from Table 12-1 to quantitative throughput, cost, and quality evaluation across the canonical workload.*
