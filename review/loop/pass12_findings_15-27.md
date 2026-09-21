# PASS-12 FINAL Convergence Review — Chapters 15–27 + Back Matter
## Book: "From Token to Fleet" (v20260913-full.pdf, 308pp)
## Scope: final convergence pass to confirm zero-new-comments. Source reviewed:
##   design/manuscript/chapter-15.md … chapter-27.md, plus back matter
##   (preface.tex, glossary.tex, sources.tex, references.tex, worksheet.tex).
## Review date: 2026-09-20
## Principle applied: report ONLY genuinely NEW issues not already raised and
##   fixed in PASS-1..11. PASS-8=12, PASS-9=11, PASS-10=24 (deep scale), PASS-11=8.
##   All numeric/cross-ref, deep-scale, and convergence items from PASS-1..11 are
##   confirmed LANDED and are NOT re-reported here.

---

## FINDINGS (genuinely new; none duplicate PASS-1..11)

**Severity: MINOR | Location: Back matter worksheet.tex (lines 11–12, "applies the whole loop to the own workload") | Problem:** Missing possessive determiner: the sentence reads "a single sheet that applies the whole loop to **the own workload**." It should be "to **the architect's own workload**" or "to **one's own workload**" — "the own" is not grammatical English. | **Why it matters:** This is a published, action-facing back-matter artifact the reader fills in; a how-to sheet that itself contains a dropped possessive reads as an unedited slip in a pass meant to reach zero. (The PASS-11 fix to this same file's taxonomy paragraph landed correctly at lines 18–22; this line was untouched by that fix.) | **Recommended change:** "…applies the whole loop to **the architect's own workload**." (Avoid "your own" here, per the book's no-reader-address / no-second-person voice rule.)

**Severity: MINOR | Location: Ch18 §8 mini-case (chapter-18.md line 154) | Problem:** The mini-case states its scenario as "1,000 users, 20% concurrent (200 simultaneous), **~5 rps average / 20 rps peak**. Hourly tokens: ~4,500 in + 500 out = **5,000**." The arrival rate and the stated hourly token volume are mutually inconsistent: at 5 rps average, an hour carries 18,000 requests, and even at a modest ~250 tokens/request that is ~4.5M tokens/hour — ~900× the stated 5,000. The 5,000-token figure implies ~0.28 tokens/request, which is impossible. | **Why it matters:** The mini-case's routing arithmetic happens to be self-consistent on the token volume alone ($2.68/hr, $1,930/mo, $8,870/mo savings all recompute from 5,000 tokens/hr × the tier rates), so the rps statement is *not* used in the math — but the scenario's own stated load (5 rps) cannot coexist with its stated 5,000 tokens/hour, which breaks the workload's internal coherence. | **Recommended change:** Either drop/adjust the "~5 rps average / 20 rps peak" clause (since the token volume drives the arithmetic), or restate the hourly volume to a value consistent with the 5/20 rps (e.g. state a per-request token count and recompute: at ~5 rps and ~250 tokens/req the hourly volume is ~4.5M tokens, three orders above the current 5,000).

---

## Items checked and found consistent (no action this pass)

- Ch15: 2×70B×9,200 ≈ 5.15×10¹⁶ FLOP/s vs 8×989 TFLOPS = 7.91×10¹⁵ (~6.5× congestion check, correctly framed as NOT an MFU); KV 2.62 MB/token × 80 layers = 24.9 GB @9.5K; 436 GB ÷ 24.9 ≈ C≈18; SDPA 4·L²·d ≈ 2.8×10¹²/layer ×80 ≈ 2.2×10¹⁴; Table 15-1 in-flight 17/86/344 = λ·8.6; 8.75× jump decomposition (kernel/batching vs ~2× host); FP8 2.62→1.42 MB/token (→13.4 GB, C≈33) consistent in §5/§6.
- Ch16: $350K/5yr ≈ $5.8K/mo; 8×700 W+2.2 kW×PUE1.3≈10.1 kW×720 hr×$0.15≈$1.1K/mo; $148K/26M≈$5.7/1K; 5×$20×720≈$72K; $72K/26M≈$2.8/1K; 0.002×9.2+0.008×0.3≈$0.0208; 26M×$0.0208≈$541K; break-even $148K/$0.0208≈7.1M. TCO "size the fleet first" — all consistent.
- Ch17: I(0/1/3/4)=9,500/10,365/12,095/12,960 tokens; C = 436/24.9/27.2/31.7/34.0 ≈ 18/16/14/13; λ·W=344 @40 rps, 1,380 @100 rps; FP8 C≈33 @T=0; Table 17-1 (28/57/32 @40, 69/141/79 @100, 137/282/158 @200) all recompute; mini-case W≈13.8 s (1.08+12.4+0.4) and 141/79 hosts; 8.6 s vs 13.8 s scope deliberately distinct.
- Ch18: 700/200/100 → 6.65M/1.9M/0.95M tokens → $8.31/$1.90/$2.38 → $12.59/hr vs $23.75/hr; $8,035/mo; weighted latency 0.70×250+0.20×300+0.10×120 ≈ 247 ms; mini-case 4,000×$0.0002+750×$0.0015+250×$0.003 = $2.68/hr → $1,930/mo, savings $8,870/mo (≈82%) — all recompute (PASS-7/8 basis fixes landed).
- Ch19: α(1/2/3/4)=1.09/1.18/1.27/1.36×; turn distribution 68/25/5/2 → median T=1, 90th T=2, 95th T=3; expected input ≈10,350, expected total ≈10,650, α≈1.12×; β(3)=1+660/8,600≈1.08×; Table 19-1 (10,065…12,960 input; 27.2…34.0 GB KV; 8.8…9.5 s E2E) all recompute. Incremental orchestration (~660 ms) vs full service time (13.8 s) scope note held.
- Ch20: 35,000/9,500 ≈ 3.7 req/s (non-binding); 18/8.6 ≈ 2.1 req/s (binding); 8×2.1 ≈ 17 req/s; ⌈40/2.1⌉ ≈ 20 hosts; ⌈40/(2.1×0.9)⌉ ≈ 22; $20/2.1 ≈ $9.5/req/s-hr; 40×8.6 = 344 in-flight. Marginal-vs-average cost framing correct.
- Ch21: 6/24×864,000 ≈ 216,000 requests; 216×$5.7 ≈ $1,231 / 216×$2.8 ≈ $605; 5%×864,000×2/24 ≈ 3,600; ~60× blast-radius reduction — all recompute.
- Ch22: 9,200÷300 ≈ 30×; 92,000/3,000 tokens/s @10 rps and 368,000/12,000 @40; 2×70B×9.2K ≈ 1.29 PFLOP; 140 GB/25 ms ≈ 5.6 TB/s; Table 22-1 input/output ratio + input/output-token rows now uniformly `[canonical scenario][ASSUMPTION]` and ratio `[canonical scenario][DERIVED]` (PASS-11 P11-3 landed); the nominal 1.31→~12 GB vs measured FP8 1.42→~13.4 GB sensitivity note is the intended PASS-9 labeling (both figures on their stated context bases).
- Ch24: PIES 4×8×6×4 = 768 → 217; p = 50/48,000 ≈ 0.00104; E[total] = 10,000×0.0052 = 52; 40×1.29 ≈ 51.5 PFLOP/s ÷ 7.9 ≈ 6.5-host floor ÷(7.9×0.4) ≈ 16.3 hosts @40% MFU; Table 24-1 cycles (217→143→138, 0.006→0.003→0.0025, 7.8→5.4→4.1, 3.1→2.4→1.3, 0.61→0.44→0.32, 8%→3.5%→1.2%) — all recompute; "missing [FACT]/[DERIVED]/[HYPOTHESIS] axis" noted.
- Ch25: 70B×2 B = 140 GB; INT8 → 70 GB; FP32 → 280 GB; ADR 0016 both 16-bit ~140 GB; ADR 0017 FP8 54% → 13.4 GB, 436÷13.4 ≈ 33 concurrent; 140+436+64 = 640 GB envelope; ~30 GB per-request vs ~64 GB runtime reserve explicitly distinguished.
- Ch26: capstone/main TTFT SLO scoped to time-to-first-token (not end-to-end ~8.6 s), and §8 QPS capped at the ~2 req/s per-host ceiling (PASS-9 reconciliation landed); Table 26-2 values internally consistent; workload-to-strategy matrix coherent.
- Ch27 Appendix A: active fractions (104/2800≈3.7%, 13/284≈4.6%, 18/320≈5.6%, 6/125≈4.8%); [1P] tags and verify-on-own-hardware caveats; Observed/Interpretation/Hypothesis separation clean; Fig 7.1 cross-ref and Ch22 the "spine" cross-references resolve.
- Back matter: preface/sources.taxonomy (five provenance × five status, plus [S#]-is-not-provenance) and the worksheet taxonomy (now full two-axis, PASS-11 P11-4) all agree; glossary covers RQO/FSDP/CP/κ/ρ; references [S1]–[S6] entries present with stable links.
- Voice-hygiene sweep (zero reader-address "you/your", zero "Think of X as Y", zero imperative "Consider…/Note that…") across ch15–27 and all back matter: CLEAN. (The few "you/your" hits are in-character dialogue in Ch23 and attacker/example strings in Ch24, not reader-address.)

---

## VERDICT
**2 genuinely new findings, both MINOR** — everything else has converged. No CRITICAL, no MAJOR, no MODERATE. The two items are: (1) a dropped possessive in the back-matter worksheet ("applies the whole loop to the own workload" → "…the architect's own workload"); and (2) an illustrative mini-case parameter inconsistency in Ch18 §8 (stated ~5 rps average is incompatible with the stated 5,000 tokens/hour, ~900× off). Trend is strong: PASS-8=12 → PASS-9=11 → PASS-10=24 (deep) → PASS-11=8 → **PASS-12=2**, and both survivors are presentation/parameter-coherence nits (one grammar, one illustrative-scenario inconsistency that does not affect any published cost arithmetic). This represents effective convergence to near-zero; fixing these two and running one more confirmation pass should land at ZERO new comments.
