# PASS-9 REVIEW — FINDINGS ch01-14 ('From Token to Fleet')

Fresh rigorous convergence review of chapters 01-14. New comments not previously resolved
(PASS-1..8 items verified as present and deliberately NOT re-reported). Each finding:
**Severity: X | Location: Y | Problem: Z | Why it matters: W | Recommended change: C**

---

## MINOR

### [P9-1] Ch2 §6 stray "design." artifact mid-sentence
**Severity: MINOR**
**Location:** design/manuscript/chapter-02/chapter-02.md, §6 "Architecture Consequence", line ~144.
**Problem:** The paragraph ends "...must be measured. (The asymmetry makes it a candidate worth benchmarking, not a concluded win.) **design.** This is the central theme of Chapter 11 (Serving) and Pattern 4 (Prefill/decode disaggregation)." A bare "design." sits between the closing parenthesis and the next sentence — a leftover fragment, not part of any sentence.
**Why it matters:** In the rendered book this emits an orphaned word ("design.") that is clearly an editing artifact in a normal-flow paragraph, degrading the prose polish the rest of the chapter maintains.
**Recommended change:** Delete the stray "design." so the sentence runs "...not a concluded win.) This is the central theme of Chapter 11..."

### [P9-2] Ch3 §3 compute-ratio derivation uses doubled intermediate FLOP values (0.056/0.28 vs 0.028/0.14)
**Severity: MINOR**
**Location:** design/manuscript/chapter-03/chapter-03.md, §3 "Why MoE saves compute but not KV cache memory", line ~65.
**Problem:** The prose computes the MoE-vs-dense ratio as `0.056/0.28 ≈ 0.20×`, but the chapter's own per-forward-pass FLOP values are **0.028 T** (MoE, 14B × 2) and **0.14 T** (dense 70B) — see Table 3.2, Table 3-1, and line 61–63. The displayed intermediates 0.056 T and 0.28 T are each exactly 2× those values. The ratio is coincidentally still 0.20, but the numerator/denominator do not match the book's stated FLOP-per-pass constants.
**Why it matters:** This is the chapter's headline compute-ratio derivation; the prose and the accompanying tables (which correctly use 0.028/0.14 and 28 B ÷ 140 B) now disagree with the inline fraction. A reader reconciling the prose against Table 3.2/Table 3-1 finds the intermediates doubled and cannot reproduce the value from the stated constants.
**Recommended change:** Write the fraction as `0.028/0.14` (or equivalently `28 B ÷ 140 B`) to match the FLOP values quoted throughout the chapter.

### [P9-3] Ch4 §3 prefill-rate basis ("on an H100, ~8.5K tokens/s") contradicts Ch2's single-H100-insufficient finding
**Severity: MINOR**
**Location:** design/manuscript/chapter-04/chapter-04.md, §3 "Latency from SLO", line ~161.
**Problem:** "prefill (~1.08 s for 9,200 tokens **on an H100**, assuming ~8.5K tokens/s prefill throughput)." The ~8.5K tok/s (9,200 ÷ 1.08 = 8,519) is attributed to *an H100*. But Ch2 explicitly derives that a single H100 **cannot** meet the 1.08 s prefill (1.29 PFLOP / 1.08 s ≈ 1.19 PFLOPS > 0.989 PFLOPS peak), and Ch8 states the per-GPU prefill ceiling is ~2,471 tok/s (at 35% MFU), with per-host ~19,800 tok/s. Sustaining 8.5K tok/s on one H100 would itself require ~1.19 PFLOPS, which the book says exceeds the H100's peak.
**Why it matters:** Ch4 is the provenance chapter and the TTFT budget is the canonical latency anchor. Attributing 8.5K tok/s to "an H100" contradicts Ch2's parallel conclusion (single H100 insufficient) and Ch8's scoped per-GPU/per-host prefill figures, so a reader cross-checking the three chapters finds the same quantity stated three ways with one of them inconsistent.
**Recommended change:** Scoped to the canonical host: "prefill (~1.08 s for 9,200 tokens across the 8×H100 host, ≈8.5K tokens/s prefill), below the host's ~19,800 tok/s ideal (Ch8); a single H100 cannot reach this (Ch2)." Or restate against Ch8's per-GPU vs per-host figures.

### [P9-4] Ch7 opening misattributes the "~1.3 MB/token" figure to the canonical scenario, which is actually 2.62 MB (FP16)
**Severity: MINOR**
**Location:** design/manuscript/chapter-07/chapter-07.md, header note, line ~5.
**Problem:** "KV cache per-token figures are given at the referenced precision throughout: ~1.3 MB/token at 8-bit, ~2.5 MB/token at FP16; **the canonical scenario's headline ~1.3 MB/token figure is the 8-bit variant.**" The canonical scenario (Ch4 Table 4-3 / canonical box) uses FP16 and quotes **2.62 MB/token** as its headline KV constant — every derived canonical number (24.1 GB @9.2K, 164 GB residency, C≈18) is computed from 2.62 MB/token. The ~1.3 MB/token figure is **Chapter 1's** 8-bit reference (as Ch7 line 4 itself says: "the canonical ~1.3 MB/token figure from Chapter 1"), not the canonical scenario's.
**Why it matters:** This is a precision/provenance collision in the very chapter whose job is to reconcile the two KV constants. A reader taking the sentence literally concludes the canonical scenario's KV is 1.3 MB (8-bit) and then can't explain why every canonical number uses 2.62 MB. It also un-settles the precisely-labeled Ch1 (1.3 MB, 8-bit) vs Ch4 (2.62 MB, FP16) distinction the book worked hard to lock.
**Recommended change:** Reword to "**Chapter 1's ~1.3 MB/token figure is the 8-bit variant** (the canonical scenario's KV is 2.62 MB/token at FP16)."

### [P9-5] Ch7 Table 7-2 (and §prose) still quote the 9.5K-max residency for the "9.2K input" case
**Severity: MINOR**
**Location:** design/manuscript/chapter-07/chapter-07.md, Table 7-2 row 1 (line ~81); also §1 line ~11 and §4 item 3 (line ~103).
**Problem:** Table 7-2's "inference (weights + KV, **9.2K input**)" row reports "**~165 GB (9.2K)**", and §1/§4 repeat "~165 GB ... with 9.2K context" / "~25 GB" for the 9.2K case. But the 9.2K-initial residency is 140 + 24.1 = **164.1 GB** (the 9.5K-max is 164.9 ≈ 165 GB, with the 9.5K-max KV of 24.9 ≈ 25 GB). P8-6 deliberately corrected Table 7-1 to use 164.1 GB / 24.1 GB for every 9.2K-labeled row; Table 7-2 and the prose still use the 9.5K-max values under a 9.2K label.
**Why it matters:** The book now (correctly, per the audited Table 7-1 and the canon 24.1 GB @9.2K / 24.9 GB @9.5K distinction) requires the 9.2K figure be 164.1 GB. Table 7-2's "~165 GB (9.2K)" and the parallel prose now sit inconsistent with that corrected table, so a reviewer reconciling Table 7-1 (164.1 @9.2K) against Table 7-2 (~165 @9.2K) finds the same residual mismatch P8-6 was meant to remove.
**Recommended change:** For 9.2K-labeled rows/prose use **164.1 GB** (140 + 24.1) and **~24.1 GB** KV; reserve 165/164.9 GB and ~24.9/25 GB for the explicit "9.5K max" statements.

### [P9-6] Ch12 §3 summary still asserts candidate (c) is ruled out "for the quality target" (settled), contradicting the provisional framing
**Severity: MINOR**
**Location:** design/manuscript/chapter-12/chapter-12.md, §3 "Memory/residency arithmetic summary", line ~24.
**Problem:** The summary line reads "Candidate (c) fits 20 GB on one H100, but its **quality ceiling rules it out for the quality target**." But the same chapter's §3 candidate (c), Table 12-1 row (c) ("✗ quality — provisional (subject to Ch 13–14 quality-gate measurement)"), the §7 Unknowns, and the §8 mini-case ("it is provisionally moved to the quality-gate evaluation ... whether a 7B-class model can reach the required answer quality is a hypothesis to be measured") all explicitly hold candidate (c) as **provisional**, not ruled out. The §3 thesis itself is precisely that capability is "NOT derivable from parameter count" and must be measured.
**Why it matters:** This is a residual of the PASS-7 candidate-(c) contradiction (P7-2): the main text, table, and mini-case were softened to "provisional / to be measured," but this one summary sentence still states a settled "rules it out" verdict. It reintroduces the exact self-contradiction P7-2 flagged and undercuts the chapter's core lesson that quality is a measured gate, not a parameter-count inference.
**Recommended change:** Align the summary with the provisional treatment: "Candidate (c) fits 20 GB on one H100 and its throughput is high, but it is **provisional** — its fate turns on the Ch13–14 quality-gate measurement, not on parameter counting."

---
## Checks run (clean — consolidated arithmetic/consistency verified, no new action)

- **Ch1** KV 70B FP16 2.62 MB/token (2,621,440 B), 8-bit 1.31 MB (1.25 MiB); 7B ~256 KB @8-bit (2×32×4096×1); embeddings 100k×4096 ≈ 0.41B ✓.
- **Ch2** decode 5.6 TB/s (140/0.025), H100 3.35 TB/s, 1.29 PFLOP prefill, 1.19 PFLOPS rate > 0.989; Fig 2.1/2.2 present ✓.
- **Ch3** MoE 47B total / 14B active, active 0.028T (28 GB read), dense 0.14T, ~0.20×/~5×, residency 94 GB (47B×2); KV identical dense-vs-MoE; Table 3.2 & Table 3-1 consistency ✓.
- **Ch4** Little's-law 10/40 rps; 92,000/368,000 & 3,000/12,000 tokens/s; cost/req $0.01164; KV 24.1 GB @9.2K; GQA ~0.33 MB/token (~8×); C=18/8.6≈2.1 req/s; mini-case 50 rps (planning-round ~10 s) → 24/34 hosts, ~23 by Ch8 prefill (460,000/19,800) ✓; §3 "one host" now has the per-request-feasibility scope qualifier (P8-2 resolved, verified present) ✓.
- **Ch5** KV 2.62 MB/token = 2.5 MiB; 640−140=500 GB headroom, 24.1/500=4.8%; 9,000 tokens/dollar-hr (50×3600/20); prefill ~97% of tokens, ~13% of wall-clock (1.08/8.58); embedding ~2× FLOP (P8-5 resolved: all-mpnet ~1 GFLOP vs bge-large ~2 GFLOP) ✓.
- **Ch6** E[L]=0.99×0.8+0.01×5.0=0.84 s; per-GPU decode 140/8/0.025=0.70 TB/s; host prefill 8×0.989≈7.9 PFLOPS; goodput 50→70 tok/s is +40% with unchanged goodput; p95 canonical SLO used (P7-8 resolved) ✓.
- **Ch7** Table 7-1 9.2K rows now use 164.1 GB (P8-6 resolved, verified present); 24.1/24.9/83.8/335.4 GB; 164.9≈165, 224, 475 GB; 3×H100=240 GB; 640=140+64+436; C≈18, FP8 ~33; FP8 1.42 MB vs 8-bit 1.31 MB (naive halving distinction); 64-layer≈2.1 MB, 100-layer≈4.9 MB ✓.
- **Ch8** 140 GFLOP/token, 1.29 PFLOP, 12.9 PFLOP/s, 346 TFLOPS @35%, 2,471 tok/s per GPU, 19,800/host, ~5 hosts @avg / ~19-20 @peak; ridge 989/3.35≈295 (H200 206; FP8 ~833); attention term +17%@9.2K/+60%@32K/~2.4×@128K; decode intensity 1.0 FLOP/byte; prefill intensity 9,200 FLOP/byte (2NL/(N×2B)=L); "14.8T" note removed (P7-4 resolved) ✓.
- **Ch9** NVLink 140/900=0.16 s (ring 0.27 s); IB 25 GB/s → 5.6 s (~35×); Eth 3 GB/s → 47 s; Option A/B/C ring times 0.16/6.1/98 s; ~22×/~350×; common-mistake 25 Gb/s ≈2.5 GB/s → 56 s (P7-5 resolved); Fig 9.1 caption now "140 GB ... in BF16" (P7-6 resolved) ✓.
- **Ch10** 140/80≈1.75 → ≥2 GPUs; PP bubble (8×4)/(11)=2.9×, (32×4)/(35)=3.66×; 400B=800 GB (~10-11×H100); gradient all-reduce now labeled **FP32** (280 GB, 11 s/0.31 s) — P8-3 resolved ✓.
- **Ch11** ~24.1 GB KV/request; C≈18; ~344 in flight at 40 rps; ~19,800 tok/s host; ~5/20 hosts cross-refs consistent; §8 scope note present ✓.
- **Ch12** 140+24=164 GB; candidate (c) 7B×2=14 GB + 4-bit KV ~6 GB → 20 GB, ~14 GFLOP/token; candidate (c) quality now *provisional* in §3/Table 12-1/§8 (P7-2 largely resolved — residual P9-6 noted); ~5 hosts (a) ✓.
- **Ch13** 140+24.9=164.9≈165 GB; 40×8.6≈344 vs C≈18 ⇒ ~20 hosts; 100 rps×9.5K=950K tok/s; single-host-vs-fleet distinction (PASS-1..8 resolved, verified present) ✓; Table 13-1 note typo-free ✓.
- **Ch14** benchmark loaded at C≈18 (~2.1 req/s), goodput ~19,800 tok/s consistent with 2.1×9.5K≈20K; "meets per-request TTFT SLO at that concurrency" (P8-4 resolved) ✓.
- **Figure/caption presence:** Figs 1.1-1.2, 2.1-2.2, 3.1, 4.1, 5.1, 6.1-6.2, 7.1-7.5, 8.1-8.2, 9.1, 10.1-10.2, 11.1-11.3, 12.1, 13.1, 14.1 all present with captions and in-body refs; no missing PNG/PDF targets; no dangling fig refs in ch01-14 (verified against chapter figure directories).
- **Cross-chapter consistency sweep:** canonical 2.62 MB/token & 2,621,440 B; ~2.5 MB/token (2.5 MiB) shorthand ✓; F16 residency 164-165 GB; C≈18; ~24/34 and ~19-20/~20 host counts; no remaining narrator-voice or import-of-record issues found.

---
## End of PASS-9 ch01-14 findings (6 new comments: 6 MINOR, 0 MODERATE, 0 MAJOR).
