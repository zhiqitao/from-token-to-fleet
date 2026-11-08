# Round-1 cross-reviewer overlap analysis

Findings loaded: 135 (4-model panel; Ornith = 122B c0/c1/c5 + 397B c1-c4)
Matching: same chapter AND (shared distinctive anchor OR token Jaccard >= 0.16).

## Consensus clusters (found by 2+ reviewers): 18

### [P1/P2] DeepSeek,MiMo,Ornith,Qwen — 4 findings
- `DeepSeek-V4.1-Flash` CH5-01: **768‑dim embeddings** give adequate retrieval quality at ~1 GFLOPs per embedding
- `MiMo-V2.6-Flash-RL` CH5-001: 768‑dim embeddings give adequate retrieval quality at ~1 GFLOPs per embedding
- `Ornith-1.5-122B` CH5-01: The ~50 tok/s here (single-stream decode) ... batch-1 decode, which at the canonical 25 ms/toke
- `Qwen3.8-27B` CH5-MINI-001: 768-dim embeddings give adequate retrieval quality at ~1 GFLOPs per embedding

### [P1/P2] DeepSeek,MiMo,Ornith — 3 findings
- `DeepSeek-V4.1-Flash` CH4-01: or **39 hosts** under the book's provisioning policy, which multiplies the independent ρ = 0.95
- `MiMo-V2.6-Flash-RL` CH20-IP03: the fleet must satisfy every named screen, and the *larger* requirement wins — **21 hosts under
- `Ornith-1.5-397B` CH16-TCO-01: policy u × ρ working = 31, + N_spare = 32 (KV-only, case (i)) ... ⌈344/11.305⌉ = 31 and 32 tota

### [P2/P3] DeepSeek,MiMo,Qwen — 3 findings
- `DeepSeek-V4.1-Flash` CH7-04: only ~1–2 at 128K
- `MiMo-V2.6-Flash-RL` CH7-001: KV cache per token (8-bit) | 2 ×80 ×8192 ×1 B ≈ 1.3 MB ... KV cache per token (FP8) | 1.31 MB
- `Qwen3.8-27B` CH8-FOOT-001: 2 ×70B × L tokens scales linearly — ~0.29 PFLOP at 2K → ~4.6 PFLOP at 32K

### [P2/P3] MiMo,Ornith — 3 findings
- `MiMo-V2.6-Flash-RL` CH8-001: ~0.29 PFLOP at 2K → ~4.6 PFLOP at 32K
- `Ornith-1.5-122B` CH7-FIG75-32K-80GB: figure-spec: "callouts at 9.2K (~24 GB FP16) and 32K (~80 GB)" vs prose "the KV cache rises to 
- `Ornith-1.5-397B` CH22-KV8BIT-01: KV cache memory per request | ~24.1 GB (9.2K, FP16) / ~24.9 GB (9.5K max) | 2.62 MB/token × 9,2

### [P1] DeepSeek,Ornith — 2 findings
- `DeepSeek-V4.1-Flash` CH12-HOSTCOUNT-01: the gate closes only when the host class is replicated to ~5 hosts (Chs. 15–17)
- `Ornith-1.5-397B` CH12-PD-POOL-RESIDENCY: §12.3 body: 'residency = 140 GB weights plus the pool's in-flight KV population — at the canoni

### [P1/P2] DeepSeek,Ornith — 2 findings
- `DeepSeek-V4.1-Flash` CH19-03: The fallback's failed-attempt decode (3 × 65 = 195 tokens ≈ 4.9 s at 25 ms/token) is real GPU t
- `Ornith-1.5-397B` CH19-FALLBACK-01: Fallback: 3 attempted turns + single-shot (2%) | ... | Model input tok 39,395 | Model output to

### [P2] DeepSeek,MiMo — 2 findings
- `DeepSeek-V4.1-Flash` CH20-01: the ρ ≈ 0.95 fractional-throughput derate raises the requirement to 344 / (0.95 × 17) = 344/16.
- `MiMo-V2.6-Flash-RL` F2: 21 hosts (KV, case-independent); prefill screen 19 case (i) / 22 case (ii); 70% × 95% + N−1 pol

### [P2/P3] DeepSeek,Ornith — 2 findings
- `DeepSeek-V4.1-Flash` CH24-01: In the illustrative scenario we model this as adding ~150 ms latency per query and reducing PIE
- `Ornith-1.5-397B` CH24-GUARDRAIL-01: In the illustrative scenario we model this as adding ~150 ms latency per query and reducing PIE

### [P1/P2] DeepSeek,Ornith — 2 findings
- `DeepSeek-V4.1-Flash` CH25-01: 70B FP16 model footprint — W = N × bytes-per-param = 70 × 10^9 × 2 B = 140 GB parameters, plus 
- `Ornith-1.5-397B` CH25-ACTIVATION-01: 70B FP16 model footprint — W = N × bytes-per-param = 70 × 10⁹ × 2 B = 140 GB parameters, plus ~

### [P1/P2] DeepSeek,MiMo — 2 findings
- `DeepSeek-V4.1-Flash` CH26-01: Until the semantic lookup mechanism and cost are described, call this an **exact-match response
- `MiMo-V2.6-Flash-RL` CH26-02: A typical re-sizing that lets the peak load concentrate on the canonical fleet (see §26.8) is c

### [P2/P3] DeepSeek,MiMo — 2 findings
- `DeepSeek-V4.1-Flash` CH26-06: | Cost | $ per query (marginal generation work) | < $0.015 | ~35% of queries skip generation |
- `MiMo-V2.6-Flash-RL` CH26-04: SM utilization 45% (baseline) … Modeled example: 68% (Table 26-2)

### [P2] DeepSeek,MiMo — 2 findings
- `DeepSeek-V4.1-Flash` APP-A-02: The earlier stages (Transformer, Efficient, MoE) are efficiency-led — they make inference affor
- `MiMo-V2.6-Flash-RL` APPA-01: The earlier stages (Transformer, Efficient, MoE) are *efficiency-led* … The later stages (Reaso

### [P2/P3] MiMo,Qwen — 2 findings
- `MiMo-V2.6-Flash-RL` CH19-01: the illustrative turn distribution here has median T = 1, 90th percentile T = 2, and 95th perce
- `Qwen3.8-27B` CH19-001: p95 = 660 ms (the 93rd–98th percentile band)

### [P2] MiMo,Ornith — 2 findings
- `MiMo-V2.6-Flash-RL` CH26-01: request rate ~2 rps (within the ~2.0 req/s per-host analytical planning ceiling) … These compon
- `Ornith-1.5-122B` CH26-CAPSTONE-MISSBUDGET: a cache miss is served by the engine at ~250 ms (a scenario value after the 35% lower arrival r

### [P3] MiMo,Ornith — 2 findings
- `MiMo-V2.6-Flash-RL` CH26-03: a cache hit returns at a fixed ~50 ms (retrieval + cache lookup, no LLM prefill)
- `Ornith-1.5-122B` CH26-HIT-PATH-RETRIEVAL: a cache hit returns at a fixed ~50 ms (retrieval + cache lookup, no LLM prefill)

### [P2/P3] Ornith — 2 findings
- `Ornith-1.5-122B` CH8-PREFILL-FLEETCAP-01: ~10 requests/s average with ~9.2K input + 300 output tokens per request ... on 8×H100 GPUs, wit
- `Ornith-1.5-397B` CH22-AGG-PFLOPS-01: Prefill is compute-bound (~1.29 PFLOP/request case (i), linear-only → ~1.19 PFLOPS required at 

### [P2/P3] Ornith,Qwen — 2 findings
- `Ornith-1.5-122B` APP-A-KV-BAND: Hybrid-attention models cut it 4–10× at the mechanism in the named configurations
- `Qwen3.8-27B` appA-002: Hybrid-attention models cut it 4–10× at the mechanism in the named configurations — a band acro

### [P1/P3] Ornith,Qwen — 2 findings
- `Ornith-1.5-397B` CH25-HOLD-01: the single-region arithmetic gives ~$155.8K/mo (~$24.97/1K) self-host, ~$87.6K/mo (~$14.04/1K) 
- `Qwen3.8-27B` CH21-001: The canonical service does ~288,000 requests/workday (10 rps × 8 h × 3,600 s; ~6.24M/month — Ch

## Unique clusters (single reviewer): 94
- DeepSeek-V4.1-Flash: 32 unique
- Ornith-1.5-397B: 28 unique
- MiMo-V2.6-Flash-RL: 25 unique
- Ornith-1.5-122B: 6 unique
- Qwen3.8-27B: 3 unique

## Unique examples per reviewer
### DeepSeek-V4.1-Flash (32)
- [P2] CH1-01 chChapter 1 — It All Starts With the First Token: During **decode**, each generated token attends once to the growing prefix, so the per-t
- [P2] CH2-01 chChapter 2 — What Actually Happens During Inference: Prefill FLOPs scale with input length; decode bandwidth is constant per token.
- [P2] CH3-01 chChapter 3 — Understanding the Model: Misreading this is the most common source of KV cache and compute underestimation.
- [P1] CH5-02 ch5: vector search with embeddings, 768‑dim all‑mpnet‑base‑v2, late‑interaction (MaxSim) retr
- [P2] CH5-03 ch5: Chapter 4 expresses **tokens per second per dollar** (token-rate ÷ per-second cost); con
- [P3] CH6-01 ch6: Prefix caching is a compute-saving move, not a latency tuning — and the telemetry told u

### MiMo-V2.6-Flash-RL (25)
- [P2] C1-4-P2-001 ch4: Per 1K req | ≈ $14.04 | ≈ $24.97 | ≈ $49.13
- [P3] C1-4-P3-001 ch4: Optimizing decode throughput on an input-heavy workload moves the needle negligibly
- [P2] CH5-002 ch5: The decision hinges on whether the ~15% retrieval quality gain translates into sufficien
- [P2] CH5-003 ch5: the bge‑large‑en option is overkill for this scale and its marginal quality gain does no
- [P2] CH9-14-001 chCh 11/13/14: The baseline unshared-KV capacity quotient is about 17.5 complete requests per host, con
- [P3] CH9-14-002 chCh 11: The ~35 GB is 13,000 tokens × 2.62 MB/token (§9.8).

### Ornith-1.5-122B (6)
- [P3] Ch4-8.5K-monopolizing-label ch4: the ~8.5K tok/s single-request prefill rate, 9.2K ÷ 1.08 s — that is the rate for one re
- [P3] CH5-02 ch5: its ~8,000 tok/s is a prefill-side / whole-request rate (Chapter 4's ≈8.5K tokens/s pref
- [P3] CH5-03 ch5: the incremental per‑request compute cost of 768‑dim vs 384‑dim embeddings is ~11.1 GFLOP
- [P3] CH7-fitgate-128K ch7: 8×H100 (no sharding ambiguity at 8 shards) passes gates 1–2 for the 9.2K and 32K rows; t
- [P3] CH7-FIG75-LINE-LABEL ch7: figure-spec: "three lines FP16/FP8/8-bit" vs caption "(full-MHA vs GQA, FP8/8-bit)" and 
- [P3] CH26-API-COST-ROUNDING ch26: $0.012/request (≈$11.6 per 1,000 requests, Ch 4)

### Ornith-1.5-397B (28)
- [P0] CH8-PREFILL-ATTENTION-TERM-DOUBLE-COUNT ch8: prefill FLOPs for 9.2K input (full-square, conservative) | ~1.5099 PFLOP | 1.288 + 4 ×80
- [P2] CH17-1701-01 ch17: the N−1 = 3 residual (~6.0 req/s) clears the burst only at ρ = 1 — at ρ = 0.85 it is 3 ×
- [P1] CH17-AGNT-01 ch17: the evaluator (render/agent_trace.py) sums every invocation's prefill: the T=3 trace has
- [P1] CH17-T172-01 ch17: N @ T=3, FP16 no-reuse (C=13; 8.645) | ⌈708/8.645⌉ ≈ 82 | ⌈1770/8.645⌉ ≈ 205 | ⌈3541/8.6
- [P2] CH16-BE-01 ch16: the low end is 6,232,677.2 = 155,816.93 ÷ 0.025 (the $25/1K top of the band) and the hig
- [P2] CH18-ROUT-01 ch18: 70% of requests (700, ≈6.65M tokens) are routine → route to 70B 8-bit: 6.65M × $1.25 = $

### Qwen3.8-27B (3)
- [P2] CH12-001 ch12: the memory footprint is trivially small, but neither quality nor throughput makes it com
- [P3] CH11-12-001 ch11, 12: prefill is compute-bound (~1.29 PFLOP → ~1.19 PFLOPS required vs 0.989 PFLOPS peak) [Ch1
- [P2] CH23-001 ch23: The framing funnel: broad ask → five question gates (problem, success, data, constraints
