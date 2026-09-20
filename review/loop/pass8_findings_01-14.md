# PASS-8 REVIEW — FINDINGS ch01-14 ('From Token to Fleet')

Fresh rigorous convergence review of chapters 01-14. New comments not previously resolved
(PASS-1..7 items verified as present and deliberately NOT re-reported). Each finding:
**Severity: X | Location: Y | Problem: Z | Why it matters: W | Recommended change: C**

---

## MODERATE

### [P8-1] Ch4 §8 mini-case derives ~50 rps from an ~8.6 s service time that actually gives ~58 rps
**Severity: MODERATE**
**Location:** design/manuscript/chapter-04/chapter-04.md, §8 End-of-Chapter Mini-Case, lines ~225-231.
**Problem:** "If the company has 5,000 employees and expects 10% concurrent activity during peak Q&A periods... the concurrency rises to 500 users. With the same **~8.6 s** request duration, throughput climbs to **~50 rps**." But 500 ÷ 8.6 = **58.1 rps**, not ~50. The ~50 rps figure is exactly 500 ÷ 10 (the coarser *planning* service-time), so the mini-case has silently swapped back to the ~10 s W for the throughput step while naming ~8.6 s. The downstream fleet sizing then inherits the error: `n_hosts = 50/2.1 ≈ 24` (and ~34 at 70% util) should be 58/2.1 ≈ **28 hosts** (≈40 at 70% util) if the ~8.6 s service time were actually used.
**Why it matters:** Ch4 §3 explicitly disciplines the ~8.6 s (fleet-sizing) vs ~10 s (planning-round) service-time distinction and pins the canonical ledger to ~8.6 s. This mini-case both restates that distinction and then breaks it in the same paragraph, producing a `host count` that is inconsistent with its own stated service time and with the Little's-Law formula the chapter teaches (C = λW ⇒ λ = 500/8.6 = 58).
**Recommended change:** Either state the service time as ~10 s where ~50 rps is used (500/10 = 50, giving the existing 24/34 host counts), or keep ~8.6 s and recompute the throughput and host counts to ~58 rps ⇒ ~28 hosts (~40 at 70% util). Do not mix the two W values in one derivation.

### [P8-2] Ch4 §3 Economic Constraints claims one host can serve the canonical workload at target SLO
**Severity: MODERATE**
**Location:** design/manuscript/chapter-04/chapter-04.md, §3 "Economic Constraints", line ~175.
**Problem:** "a 70B FP16 model on one host can serve the canonical workload at the target SLO, but scaling to higher traffic or longer contexts would require additional hosts." The canonical workload is ~10 rps avg / ~40 rps peak. This is contradicted by the book's own later arithmetic: Ch8 (Table 8-1, ~92,000/19,800 ≈ 4.6 → **~5 hosts** at the 10 rps *average*, and ~19-20 hosts at 40 rps peak), Ch12 candidate (a) ("a single host fails the throughput gate"), and Ch11/Ch13/Ch17 (single host C ≈ 18 KV-resident vs ~344 in flight at 40 rps ⇒ ~20 hosts). So a single host cannot *serve the workload* — it is only per-request-latency-feasible.
**Why it matters:** Ch4 is the provenance chapter the whole book cites; an unqualified "one host can serve the canonical workload at the target SLO" is exactly the per-request-feasibility-vs-capacity conflation that Ch2, Ch8, Ch11, Ch13 all carefully flagged as a scope note. A reader taking Ch4 at face value would size a one-host deployment that the rest of the book proves is throughput- and capacity-insufficient.
**Recommended change:** Add the standard per-request-feasibility scope qualifier (as in Ch2/Ch8/Ch13): "...meets the *per-request* latency SLO (TTFT/TPOT) on one host, but the *capacity* question — how many hosts absorb the 10 rps avg / 40 rps peak arrival — is a separate computation (~5 hosts at avg; ~20 hosts at peak; Ch 8, 16-17)."

### [P8-3] Ch10 §3 gradient all-reduce labels the gradient BF16 but uses 4 B/param (FP32) → 280 GB
**Severity: MODERATE**
**Location:** design/manuscript/chapter-10/chapter-10.md, §3 "Data Parallelism", line ~96.
**Problem:** "grad bytes = N × bytes/param = 70 × 10⁹ × 4 B ≈ 280 GB per step (**BF16 gradient**; the all-reduce moves the gradient once, not weights+gradients)." BF16 is **2 B/param**, so a BF16 gradient of a 70B model is 70e9 × 2 = **140 GB**, not 280 GB. The 4 B/param used to reach 280 GB is the FP32 footprint. The subsequent sync times (280/25 ≈ 11 s; 280/900 ≈ 0.31 s) are then computed on the FP32 value, whereas a true BF16 gradient gives 140/25 ≈ 5.6 s and 140/900 ≈ 0.16 s.
**Why it matters:** The byte-per-parameter is the load-bearing constant here and it disagrees with the stated precision by 2×, which halves the headline all-reduce sync times (and so halves the "far too slow" conclusion). It is also the same byte-count choice (4 B = FP32 vs 2 B = BF16) that the book elsewhere keeps rigorous, so the inconsistent label weakens the chapter's precision discipline at exactly the point where it argues DP is gradient-sync-bound.
**Recommended change:** Either relabel the example as an **FP32** gradient ("70 × 10⁹ × 4 B ≈ 280 GB per step (FP32 gradient)") to keep 280 GB / 11 s / 0.31 s, or keep the "BF16 gradient" label and change the value to 70 × 10⁹ × 2 B = 140 GB, giving 5.6 s and 0.16 s. Pick one and make the label and the byte-count agree.

### [P8-4] Ch14 §3 Step 3 "Candidate A meets SLO" contradicts the single-host ceiling and its own goodput
**Severity: MODERATE**
**Location:** design/manuscript/chapter-14/chapter-14.md, §3 Step 2-3, lines ~34-41.
**Problem:** Step 2 explicitly sets the benchmark at "~40 rps... ~344 requests in flight per Little's law — Ch 17," and Step 3 then reports "Candidate A (a 70B dense on 8×H100) shows p95 TTFT 1.9 s and goodput 9,800 tok/s at 40 rps concurrency — **meets** the canonical SLO." Two inconsistencies: (a) a single 8×H100 host has a KV-residency ceiling of C ≈ 18 (Ch11/13/17), so it cannot hold ~344 in-flight requests at all — the book elsewhere says a single host cannot carry the 40 rps peak; (b) at 40 rps × ~9.5K tokens/request the demand is ~380,000 tok/s, so a goodput of 9,800 tok/s is only **2.6%** of demand — i.e. ~97% of tokens miss the SLO, the opposite of "meets the canonical SLO."
**Why it matters:** Ch14 is the chapter that teaches goodput as the true SLO-windowed metric; its own worked example pairs a "meets the SLO" verdict with a goodput that (on the book's own goodput definition) says the SLO is massively breached, and with a single host that physically cannot absorb the 344 in-flight requests the protocol just specified. A reader cannot reproduce or trust the worked result, and it undercuts the chapter's central claim about reading goodput.
**Recommended change:** Make the scenario self-consistent: either run the benchmark at a concurrency a single 8×H100 host can hold (C ≈ 18, i.e. ~2.1 req/s full utilization) with a goodput that represents meeting the SLO there, or name the candidate as the ~20-host fleet that actually serves the 40 rps peak and set goodput to the full ~380K tok/s order. Ensure the goodput and the SLO verdict are consistent with the stated concurrency.

---

## MINOR

### [P8-5] Ch5 §3 "4×FLOP cost" of bge-large-en over all-mpnet does not match the FLOP table
**Severity: MINOR**
**Location:** design/manuscript/chapter-05/chapter-05.md, §3 Embedding selection Takeaway, line ~54.
**Problem:** "the bge-large-en option is overkill for this scale and its marginal quality gain does not offset the **4×FLOP** cost over all-mpnet-base-v2." The chapter's own embedding table (lines 42-46) lists all-mpnet-base-v2 (768-dim) at **~1 GFLOPs** and bge-large-en (1024-dim) at **~2 GFLOPs** — a 2× ratio, not 4×. (Compared to the 384-dim all-MiniLM at ~0.3 GFLOPs, bge-large is ~6.7×, also not 4×.)
**Why it matters:** The takeaway's justification for recommending 768-dim over 1024-dim is built on a "4×FLOP" cost that the chapter's own FLOP column does not support; a reader cross-checking the two finds a factor-of-2 disagreement in the exact quantity (per-embedding FLOPs) that drives the recommendation.
**Recommended change:** Change "4×FLOP" to "~2×FLOP" to match the table (all-mpnet ~1 GFLOPs vs bge-large ~2 GFLOPs), or state the comparison baseline explicitly and use the correct ratio.

### [P8-6] Ch7 Table 7-1 "fits 2×H100 at 9.2K?" row uses the 9.5K-max value (164.9 GB), not the 9.2K value
**Severity: MINOR**
**Location:** design/manuscript/chapter-07/chapter-07.md, Table 7-1, rows ~50-52 (and the residency rows).
**Problem:** The row "fits 2×H100 at 9.2K? | no, 164.9 GB > 160 GB" carries the **9.5K-max** residency value (140 + 24.9 = 164.9 GB), but the row label says "at 9.2K." At the 9.2K context the residency is 140 GB + 24.1 GB = **164.1 GB** (the table's own 9.2K-initial-KV row is 24.1 GB, not 24.9 GB). The verdict (164.1 > 160, still no) is unaffected, but the numeric shown is the wrong context length's value.
**Why it matters:** Table 7-1 is the audited KV/residency table the book promises traceable derivations in; pairing a "9.2K" label with the 9.5K-max total (and writing 164.9 rather than 164.1) is a small but genuine label/datum mismatch that a reader reconciling 9.2K-initial (24.1 GB) vs 9.5K-max (24.9 GB) will trip on.
**Recommended change:** For the 9.2K label rows, use 164.1 GB (140 + 24.1); keep 164.9/165 GB for the explicit "9.5K max" rows. (Or relabel the row "fits 2×H100 at 9.5K max?" if the max value is intended.)

---
## Checks run (clean — consolidated arithmetic/consistency verified, no new action)

- **Ch1 KV** 70B FP16 2.62 MB/token, 8-bit 1.31 MB/token (1.25 MiB); embeddings 100k×4096 ≈ 0.4B ✓.
- **Ch2** decode 5.6 TB/s (140/0.025), H100 3.35 TB/s, prefill 2NL=1.288→1.29 PFLOP, rate 1.19 PFLOPS; MI300X ~5.3 TB/s [ILLUSTRATIVE] ✓; λ·W≈344 at 8.6 s ✓.
- **Ch3** MoE total 47B / active 14B (14×2=28 GB read/token), 0.028T, ~0.20× vs dense, 5× reduction; residency 94 GB (47×2); KV identical dense-vs-MoE; Qwen 125B/6B, ~250 GB total ~12 GB active working set ✓.
- **Ch4** Little's law 100/10=10 rps, peak 0.20×2000/10=40 rps; 92,000/368,000 & 3,000/12,000 tokens/s; cost/req ($1.20×9.2+$2.00×0.3)/1000=$0.01164; KV 24.1 GB@9.2K (2,621,440 B/token), GQA ~0.33 MB/token (~8× less); 241 GB @10 concurrent; C=18/8.6≈2.1 req/s; ~24/34 hosts ✓.
- **Ch5** KV per token 2,621,440 B=2.62 MB; 640−140=500 GB headroom, 24.1/500=4.8%; 9,000 tokens/dollar-hr (50×3600/20); prefill ~97% tokens, ~13% wall-clock; mini-case 3.1 GB vs 1.5 GB index ✓.
- **Ch6** E[L]=0.99×0.8+0.01×5.0=0.84 s; per-GPU decode 140/8/0.025=0.70 TB/s; host prefill 8×0.989≈7.9 PFLOPS; 50→70 tok/s is +40% ✓.
- **Ch7** KV 2.62 MB (2,560 KB / 2.5 MiB), 8-bit 1.25 MiB; 24.1/24.9/83.8/335.4 GB; 164.9/165, 224, 475 GB; 3×H100=240 GB; 640=140+64+436, C≈18, FP8~33; FP8 1.42 MB (54% of BF16, 13.4 GB@9.5K), 8-bit 1.31 MB (~12 GB, ~152 GB total); 64-layer/8192≈2.1 MB, 100-layer/12288≈4.9 MB ✓.
- **Ch8** 140 GFLOP/token, 1.29 PFLOP, 12.9 PFLOP/s, 346 TFLOPS@35%, 2,471 tok/s per GPU, 19,800/host, 92,000/19,800≈4.6→~5 hosts, 368K/19,800≈18.6→~19-20; ridge 989/3.35≈295 (H200 989/4.8≈206; FP8 4P/4.8T≈833); attention term +17%@9.2K / +60%@32K / ~2.4×@128K; decode intensity 140G/140G=1.0 FLOP/byte; prefill (2NL)/(N×2B)=L=9,200 FLOP/byte ✓.
- **Ch9** NVLink 140/900=0.156→0.16 s; IB effective 40 GB/s ring 6.1 s; Eth 2.5 GB/s ring 98 s; ~22× (6.1/0.27) and ~350× (98/0.27) ✓; ~35 GB KV /900=0.04 s ✓.
- **Ch10** 140/80=1.75→≥2 GPUs; PP bubble (8×4)/(8+4-1)=2.9×, (32×4)/(32+4-1)=3.66×; 400B=800 GB (~10-11×H100); 2×H100/3×H100 fit note ✓.
- **Ch11** ~24.1 GB KV/request; C≈18; ~344 in flight at 40 rps ✓; ~19,800 tok/s and ~5/20 hosts cross-refs consistent.
- **Ch12** 140+24=164 GB; candidate (c) 7B×2=14 GB + 4-bit KV ~6 GB → 20 GB, ~14 GFLOP/token → tens-of-thousands tok/s; candidate (c) quality framed as provisional (P7-E resolved, verified present) ✓; ~5 hosts (a) ✓.
- **Ch13** 140+24.9=164.9≈165 GB; 40×8.6≈344 vs C≈18 ⇒ ~20 hosts; 100 rps×9.5K=950K tok/s ✓.
- **Ch14** ~344 in flight at 40 rps (40×8.6); deployment-vs-capability framing and two-stage flow ✓.
- **Figure/caption presence:** Figs 1.1-1.2, 2.1-2.2, 3.1, 4.1, 5.1, 6.1-6.2, 7.1-7.5, 8.1-8.2, 9.1, 10.1-10.2, 11.1-11.3, 12.1, 13.1, 14.1 all present with captions and in-body refs; no dangling fig refs in ch01-14. Ch9 Fig 9.1 caption now uses the correct 140 GB BF16 (P7-J verified fixed).
- **Cross-chapter consistency sweep:** canonical 2.62 MB/token & 2,621,440 B; ~2.5 MB/token (2.5 MiB) shorthand ✓; F16 residency 164-165 GB; C≈18; ~24/34 and ~19-20/~20 host counts; no remaining ch01-14 narrator-voice or import-of-record issues found.

---
## End of PASS-8 ch01-14 findings (6 new comments: 4 MODERATE, 2 MINOR).
