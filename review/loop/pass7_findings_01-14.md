# PASS-7 REVIEW — FINDINGS ch01-14 ('From Token to Fleet')

Fresh rigorous review of chapters 01-14. New comments not previously resolved. Each finding:
**Severity: X | Location: Y | Problem: Z | Why it matters: W | Recommended change: C**

---

## MODERATE

### [P7-1] Ch9 §2 InfiniBand lower-bound time contradicts its own stated bandwidth
**Severity: MODERATE**
**Location:** design/manuscript/chapter-09/chapter-09.md, §2 ("Mental Model"), line 45.
**Problem:** The text says "if those same 140 GB travel over a 200 Gb/s HDR InfiniBand link (≈ 25 GB/s effective unidirectional) it is ≈ 2.8 s — 18× longer". But 140 GB ÷ 25 GB/s = **5.6 s**, not 2.8 s. The 2.8 s figure implies 50 GB/s (i.e. it silently uses the bidirectional aggregate), and the "18× longer" multiple (0.16 × 18 ≈ 2.88 s) is consistent with the 2.8 s value, not with a 25 GB/s unidirectional link (which would be 5.6 s and ~35× longer).
**Why it matters:** This is the worked lower-bound example that establishes the chapter's central interconnect ranking (the "2–3 orders of magnitude" drop and the relative fabric times). A reader who takes the stated 25 GB/s unidirectional and computes 140/25 gets 5.6 s, finding a 2× disagreement with the printed 2.8 s; the same sentence also understates the InfiniBand-vs-NVLink penalty (18× vs the correct ~35×). It undermines the chapter's own discipline of "treat bytes ÷ bandwidth as a lower bound" and makes the ranking non-reproducible.
**Recommended change:** Either fix the time and multiple to "≈ 5.6 s (≈ 35× longer)" for a 25 GB/s unidirectional link, or relabel the bandwidth as "≈ 50 GB/s bidirectional aggregate" to keep 2.8 s / 18×. Pick one basis and state it.

### [P7-2] Ch12 Candidate (c) quality fate contradicts §3's careful framing
**Severity: MODERATE**
**Location:** design/manuscript/chapter-12/chapter-12.md, §8 mini-case (paragraph on Candidate (c)) and Table 12-1 row (c), pitted against §3 Candidate (c).
**Problem:** §3 is careful and methodologically explicit: whether a 7B-class model "can match the 70B model's answer quality on this workload is NOT derivable from parameter count... an empirical question answered only by running the actual evaluation set," so Candidate (c) is "flagged for measurement against the quality gate, not dismissed by parameter counting." But the mini-case asserts flatly "fails the quality constraint — the 7B model cannot reach the required answer quality regardless of KV quantization," and Table 12-1 row (c) states "fails quality ceiling" / "✗ fails quality ceiling," with no "to be measured" caveat. The very next sentence in the same mini-case then says "The architect does NOT discard Candidate (c) by parameter counting alone: it is provisionally moved to the quality-gate evaluation (Chapters 13–14) to measure whether a 7B-class model actually meets the workload's capability/quality threshold." Those two statements directly contradict each other.
**Why it matters:** The chapter's central lesson in §3 is precisely that capability is not inferable from parameter count and must be measured. The mini-case and Table 12-1 assert the opposite as a settled conclusion, then walk it back in the same breath. This is the strongest self-contradiction in ch01-14 and will confuse a reader about whether the book holds "7B fails quality" as fact or as a testable hypothesis.
**Recommended change:** Soften the mini-case and Table 12-1 to match §3: e.g. "fails/uncertain on the quality gate — to be measured in Ch13-14" rather than "cannot reach the required answer quality regardless of KV quantization." Keep the table cell as "provisional — subject to the quality-gate measurement."

---

## MINOR

### [P7-3] Ch8 Table 8-1 duplicate table header + stray header text in caption
**Severity: MINOR**
**Location:** design/manuscript/chapter-08/chapter-08.md, §3, lines 65-67 (Table 8-1).
**Problem:** The caption line (65) ends with a spurious "| metric | value | derivation |" appended to the caption paragraph, and then line 67 repeats "| metric | value | derivation |" as the actual table header. The table header row therefore appears twice, with the first instance mashed into the caption line.
**Why it matters:** In the rendered book this emits a leftover table-header fragment inside the caption text and a duplicated header row, which looks like a conversion/edit artifact and degrades the table's cleanliness.
**Recommended change:** Remove the trailing "| metric | value | derivation |" from the caption line so the caption runs cleanly and the header appears only once.

### [P7-4] Ch8 §3 prefill-FLOP derivation cites an irrelevant "14.8T-token pre-train budget"
**Severity: MINOR**
**Location:** design/manuscript/chapter-08/chapter-08.md, §3 "Prefill PFLOP for 9.2K input", line 53.
**Problem:** The derivation annotation reads "[DERIVED: 2 ×N × L where N=70B, L=9,200; reconciles with Ch.2 scaling law if the full 14.8T-token pre-train budget is distributed across active parameters; the figure is large because... ]". The "14.8T-token pre-train budget" is a pre-training-corpus statistic and has nothing to do with the FLOPs of a single 9.2K-token prefill pass; it does not "reconcile" with anything, and reads like a leftover line from a different (training-cost) derivation.
**Why it matters:** It introduces a spurious quantity into an otherwise clean single-request FLOP derivation (2·N·L), which is supposed to be a simple first-principles count. A reviewer comparing derivations will be confused about what the 14.8T number refers to.
**Recommended change:** Trim the note to the pure "2 × N × L where N=70B, L=9,200" derivation and drop the 14.8T pre-train-budget sentence (or move it to a training-cost discussion where it belongs).

### [P7-5] Ch9 §5 common-mistake bandwidth unit mismatch (25 Gb/s gives ~56 s)
**Severity: MINOR**
**Location:** design/manuscript/chapter-09/chapter-09.md, §5 "Common Mistakes", line 96.
**Problem:** "A 70B model gradient all-reduce at 25 Gb/s takes ~56 s per step." 140 GB at 25 Gb/s = 3.125 GB/s gives ~45 s, and at 25 GB/s gives 5.6 s; ~56 s only results from a *2.5 GB/s practical-effective* figure (as used in §3 Option C), not from "25 Gb/s". The printed bandwidth and the printed time disagree.
**Why it matters:** The section is explicitly about avoiding under-budgeting slow-fabric communication; the mismatch between the stated link rate and the derived time weakens the example and propagates an inconsistent constant into the "15.5 hours" follow-on.
**Recommended change:** State the effective rate explicitly, e.g. "at 25 Gb/s Ethernet (≈2.5 GB/s effective), 140 GB ÷ 2.5 ≈ 56 s per step."

### [P7-6] Ch9 Fig 9.1 caption: "≈70 GB of weights in BF16" contradicts its own "140 GB weight footprint"
**Severity: MINOR**
**Location:** design/manuscript/chapter-09/chapter-09.md, §2 Fig 9.1 caption (line 49).
**Problem:** Caption: "the dashed marker sits at the 140 GB weight footprint of a 70B model (≈ 70 GB of weights in BF16 across 8 participants)." A 70B model in BF16 is 2 B/param = 140 GB, as the caption itself says in the same sentence. "≈70 GB" corresponds to 1 B/param (FP8/int8), not BF16; and "across 8 participants" would give ~17.5 GB/participant, again not 70 GB.
**Why it matters:** The figure caption is the place that anchors the x-axis data volume; an internally contradictory weight figure undermines the plot's meaning and the reader's confidence in the interconnect-time curves.
**Recommended change:** Change to "≈140 GB of weights in BF16" (or, if plotting per-rank shards, state the correct per-participant figure).

### [P7-7] Ch7 Table 7-1 row derivation mislabeled (total-KV row shows residency math)
**Severity: MINOR**
**Location:** design/manuscript/chapter-07/chapter-07.md, Table 7-1, "total inference KV (9.5K max)" row (line 40).
**Problem:** The value "≈ 24.9 GB" is correct, but its derivation column reads "140 GB weights + KV 24.9 GB ≈ 164.9 GB" — that is the *residency* total, not the derivation of the KV figure (which should be 9,500 × 2,621,440 B ≈ 24.9 GB). The derivation for the KV row points at the wrong quantity while the value row next to "inference residency" actually carries it.
**Why it matters:** Even though the number is right, the derivation column is the audit trail the book promises; a wrong derivation next to the KV total makes the table's provenance column incorrect and invites a reader to double-count weights + KV.
**Recommended change:** Set the derivation to "9,500 × 2,621,440 B ≈ 24.9 GB" and let the residency row carry the "140 + 24.9 = 164.9 GB" note.

### [P7-8] Ch6 §3 worked-latency example uses a p99 SLO while the canonical SLO is p95
**Severity: MINOR**
**Location:** design/manuscript/chapter-06/chapter-06.md, §3 "Latency Is a Distribution, Not a Mean", lines 49 and 54.
**Problem:** The illustrative request-latency example is framed against "a p99 TTFT SLO of ≤ 2 s" (line 49) and "under a 2 s SLO" (line 54), and the accompanying Figure 6.2 caption discusses the p99 reading. But the book's canonical latency SLO is p95 ≤ 2 s (Ch4 Table 4-3), and §3 itself later states "we budget TTFT ≤ 1.2 s ... with a p95 ≤ 2 s" (line 56). The example therefore mixes p99 and p95 SLO percentiles without flagging the switch.
**Why it matters:** The chapter's own thesis is that the SLO percentile matters and that p95 vs p99 frame the tail differently; using p99 for the example while the canonical (and the rest of the chapter) uses p95 blurs the very distinction the chapter is teaching and could be misread as the book's SLO being p99.
**Recommended change:** Frame the example against the canonical p95 ≤ 2 s (and note p99 = 1.33 s is still under budget while the 1% stragglers at ~5 s breach it), or explicitly label it a distinct p99-scenario illustration.

---

## Checks run (clean — no action)

- **Arithmetic spot-checks (all consistent):** Ch1 KV 70B FP16 ≈ 1.3 MB/token (8-bit) and 2.62 MB/token (FP16); Ch2 prefill 1.29 PFLOP, 1.19 PFLOPS rate, decode 5.6 TB/s; Ch3 MoE FLOPs 0.028T (14B×2), residency 94 GB (47B×2), KV identical dense-vs-MoE; Ch4 Little's-law 10/40 rps, token throughputs (92K/368K input, 3K/12K output), cost/request $0.01164, KV 24.1 GB @9.2K, GQA ~0.33 MB/token, C≈18/8.6s≈2.1 req/s, 24/34 hosts; Ch5 9,000 tokens/(dollar·hr), 24.1 GB KV, 2.62 MB/token budget; Ch6 mean 0.84 s, 8×0.989≈7.9 PFLOPS host; Ch7 KV 2.62 MiB/MB reconciliation, 164.9/165 GB, 24.9 GB @9.5K, 1310,720 B=1.25 MiB, FP8 54% of BF16, ~436 GB KV budget / C≈18; Ch8 140 GFLOP/token, 1.29 PFLOP, 12.9 PFLOP/s, 346 TFLOPS (×0.35), 2,471 tok/s per GPU, 19,800/host, ~5 hosts @avg / ~19-20 @peak, ridge 295 & 206 FLOP/byte (H200), attention term +17% @9.2K/+60% @32K/~2.4× @128K; Ch9 0.16 s NVLink lower bound (correct), Option A/B/C ring times, ~22×/~350×; Ch10 ≥2 GPUs to hold 140 GB, grad 280 GB, 11 s/0.31 s sync, PP bubble speedups; Ch11/12/13/14 344 in-flight (40×8.6), 164/165 GB residency, 92K/19800≈4.6→~5 hosts, C≈18 vs ~20 hosts fleet.
- **Resolved items re-verified as present, not re-reported:** Ch7 100-layer/12288-dim ~4.9 MB/token; Ch13 single-host-vs-fleet capacity distinction (§3, §5 common mistake); Ch12 164/165 host-fit language; Ch2 scope-of-single-host note; Ch11 Fig 11.3 refs resolved.
- **Figure/caption presence:** Figs 1.1, 1.2, 2.1, 2.2, 3.1, 4.1, 5.1, 6.1, 6.2, 7.1-7.5, 8.1, 8.2, 9.1, 10.1, 10.2, 11.1-11.3, 12.1, 13.1, 14.1 all present with captions and in-body refs; no dangling refs in ch01-14.
- **Glossary / terminology / voice hygiene:** no new narrator-voice or import-of-record issues found in ch01-14.
- **No overclaiming found** beyond P7-2 (Candidate (c) quality). All throughput/residency figures in ch01-14 are appropriately scoped as [ILLUSTRATIVE][DERIVED], "worked example, not reference," analytical-bound, or [2°]-to-verify.
