# PASS-9 FIXER — Responses (11 new comments, loop continues)

PASS-9 surfaced 11 new comments (ch01-14: 6 [all MINOR]; ch15-27: 5 [3 MEDIUM, 2 LOW]).
Rate is converging: PASS-6=14, PASS-7=22, PASS-8=12, PASS-9=11, and severity is dropping
(no CRITICAL since early passes; PASS-9 had 0 MAJOR). Findings in pass9_findings_01-14.md / pass9_findings_15-27.md.

## ch01-14 (6 MINOR)

- **P9-1 (Ch2 §6) stray "design." artifact** — Removed orphan "design." fragment mid-sentence. Source Ch2.
- **P9-2 (Ch3 §3) doubled FLOP intermediates** — Line-65 example used 0.056/0.28 (each 2×)
  instead of the chapter's canonical 0.028T (MoE) and 0.14T (dense). Corrected to
  `\frac{0.028}{0.14} \approx 0.20\times`; ratio unchanged.

  *(Verified: 14B active × 2 = 0.028T and 70B × 2 = 0.14T are the canonical per-forward-pass
  constants; the 0.056/0.28 were a doubled slip.)*

- **P9-3 (Ch4 §3) "~8.5K tok/s on an H100" prefixed with token-layer vs capacity-frame note** —
  Re-framed as "on the same compute class (FP8)" and scoped to the single-host per-GPU
  prefill view, avoiding an unscoped claim that a single H100 alone sustains the fleet's
  demand. Cross-checked against Ch8 prefill-in-parallel view.
- **P9-4 (Ch7 header note) 8-bit KV constant attribution** — Note now reads "~1.3 MB/token
  (8-bit)" (the `[1P]`-sourced 1.3125... figure) rather than implying a differentially-labelled
  value; the nominal vs measured FP8 distinction is spelled out (see P9-10).
- **P9-5 (Ch7 Table 7-2 / §1 / §3) 9.2K residency value mismatch** — Table 7-2 and the
  prose and §3 used ~165 GB / ~25 GB for "9.2K input", but 140 + 24.1 = **164.1 GB**
  (165 / 24.9 is the 9.5K-max context). Corrected all 9.2K-labelled rows and prose to
  **164.1 GB** (and §3's KV addend to **24.1 GB**), leaving the 9.5K-max rows at 164.9/24.9.
- **P9-6 (Ch12 §3 summary) candidate (c) "rules it out"** — §3 summary panel still stated
  candidate (c) was ruled out by a quality ceiling, contradicting the PASS-7 provisional
  softening. Re-worded to "**provisional** — its fate turns on the Ch13–14 quality-gate
  measurement, not on parameter counting."

## ch15-27 (3 MEDIUM, 2 LOW)

- **P9-7 (Ch15 §3) attention FLOP 2× undercount [MEDIUM]** — Ch15 used `2·L²·d_model`
  (counting only one matmul / MACs), but the textbook form (both Q·Kᵀ and ·V, in FLOPs)
  is `4·n_layers·L²·d`, and that is exactly what Ch8's ~17%-at-9.2K figure and Ch22's
  formula use. Corrected Ch15 to **4·L²·d_model**: 4 × 9,200² × 8,192 ≈ **2.8 × 10¹² FLOPs/layer**
  (per-head 4 × 9,200² × 128 ≈ **4.3 × 10¹⁰**), × 80 layers ≈ **2.2 × 10¹⁴**. Added pointer to
  Ch8's formula and Ch22 Fig 22.1.

  *(Independently re-derived: 4·L²·d·n = 2.219×10¹⁴ = 17.2% of 2·N·L = 1.288×10¹⁵, matching
  the book's +17% — the 2× form gives 8.6% and would break consistency.)*

- **P9-8 (Ch26 §3 + §8) capstone sub-second p99 / 12 QPS contradicts canonical ~8.6s / ~2.1 req/s [MEDIUM]** —
  The capstone re-introduced the sub-second end-to-end p99 that Ch20's mini-case explicitly
  corrects as infeasible for the canonical 9.2K/300-token profile (which takes ~8.6s and
  caps one host at ~2.1 req/s). Fixed by **scoping the sub-second figure to time-to-first-token
  (TTFT)** and **correcting the §8 QPS to the ~2 req/s per-host ceiling** (§1 "12 QPS"→"~2 QPS"
  within the ~2.1 req/s ceiling; §2 "12→7.8 QPS"→"~2.0→~1.3 QPS"; §3 latency "<300 ms"→"TTFT p99 <300 ms").
  Added an explicit note that the canonical ~8.6s end-to-end and ~2.1 req/s ceiling still hold
  and that the sub-second capstone figures are TTFT, not end-to-end.
- **P9-9 (Ch17 §4 vs §6) cross-host bandwidth formula contradiction [MEDIUM]** — §4 defined
  per-request as `D/(λ_net·φ·N)` = 625 MB/s while §6 defined the aggregate as `φ·N·D/λ_net`
  = 100 MB/s, giving a per-request figure larger than the aggregate (unphysical — aggregate
  must include the per-request bursts). Reconciled on one clean definition:
  **per-request burst = D/λ_net = 250 MB/s ≈ 2 Gbps**; **fleet aggregate = φ·N·(D/λ_net) =
  100 MB/s = 0.8 Gbps** (identical to §6's B_min, so the two sections now agree). The scaling
  argument is now *stronger* and *correct*: at φ=0.5, D=50 MB the burst itself (20 Gbps)
  exceeds a single 10 Gbps link *before* the aggregate (5 GB/s, ~4× over) does. §6's B_min
  tie-in sentence updated to reference §4's burst/aggregate separation.
- **P9-10 (Ch22 Table 22-1 / Ch27 §5) unlabelled nominal-vs-measured KV split [LOW]** —
  The sensitivity note "at 8-bit KV ... falls to ~12 GB under ideal byte-halving" used the
  nominal 1.31 MB/token halving, while the measured FP8 constant is ~1.42 MB/token (54% of
  BF16, [S6]) giving ~13.4 GB. Labelled both: Ch22 note now states the nominal 1.31 → ~12 GB
  vs measured 1.42 → ~13.4 GB; Ch27 §5 now states "the two 8-bit figures — nominal byte-halving
  ~1.31 MB/token versus measured FP8 ~1.42 MB/token (54% of BF16 [S6]) — are distinct, and the
  measured one is what the fleet-sizing chapters use."
- **P9-11 (Ch17 §8 / Ch19) W prefill 1.08s vs scaled 1.42s basis [LOW]** — W≈13.8s holds the
  prefill at the canonical 9.2K representative rather than the full 12,095-token context
  (which would scale it to ~1.42s and give W≈14.2s). Added an explicit note in Ch17 §8 that
  W≈13.8s is a **lower bound** on the agentic service time, and the derived in-flight/host
  counts are corresponding lower bounds.

## Status
11/11 comments addressed. All fixes verified against source. Now rebuilding and re-reviewing
(PASS-10). Convergence trend: 14 → 22 → 12 → 11; severity floor has dropped to MINOR/LOW.
