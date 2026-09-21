# PASS-13 FINAL Convergence Review — Chapters 15–27 + Back Matter
## Book: "From Token to Fleet" (v20260913-full.pdf, 308pp)
## Scope: FINAL gate — confirm ZERO new comments so the review loop can exit.
##   Source reviewed: design/manuscript/chapter-15.md … chapter-27.md, plus back
##   matter (render/latex/preface.tex, render/latex/backmatter/{glossary,sources,
##   references,worksheet}.tex).
## Review date: 2026-09-20
## Principle applied: report ONLY genuinely NEW issues not already raised and
##   fixed in PASS-1..12. Convergence history: PASS-8=12, PASS-9=11, PASS-10=24
##   (deep scale), PASS-11=8, PASS-12=2 (both MINOR and now FIXED). This pass
##   re-verified that the PASS-12 fixes landed and that all PASS-1..11 items
##   remain resolved; it did NOT re-report any of them.

---

## FINDINGS

**NO NEW FINDINGS.** Zero CRITICAL / MAJOR / MODERATE / MINOR issues.

No genuinely new comment survives a careful, independent read of chapters 15–27
and all back-matter files. Every defect raised in PASS-1..12 is confirmed
resolved, and no new defect of any severity was introduced.

---

## What was verified this pass (independent re-check, not a re-report)

**PASS-12 fixes landed and correct:**
- `worksheet.tex` line 12: now reads "applies the whole loop to the **architect's
  own workload**" (dropped possessive fixed; no-reader-address preserved).
- `chapter-18.md` §8 mini-case: the load is now stated coherently — "a modest,
  deliberately low volume — **5,000 tokens/hour** (each request ~250 tokens →
  ~20 requests/hour), a light load chosen to make the per-token routing economics
  concrete"; the added scope note cleanly separates the mini-case's per-token
  tier rates from the §3.2 per-1M ledger. All downstream figures
  ($0.80/$1.13/$0.75 = $2.68/hr, $1,930/mo, $8,870 savings, 82%) recompute from
  the 5,000 tokens/hour and are unchanged.

**Canonical arithmetic recomputed end-to-end (all agree):**
- Ch15: 2×70B×9,200 ≈ 5.15×10¹⁶ vs 8×989 = 7.91×10¹⁵ (~6.5×, correctly framed
  as a congestion check, not MFU); KV 2.62 MB/token × 9,500 ≈ 24.9 GB, 436÷24.9
  ≈ C≈18, FP8 → ~13.4 GB / C≈33; 4·L²·d ≈ 2.8×10¹²/layer ×80 ≈ 2.2×10¹⁴.
- Ch16: $350K/5yr ≈ $5.8K/mo → $116K/mo (20 hosts); opex ~$22K/mo; $148K/26M ≈
  $5.7/1K; $72K/26M ≈ $2.8/1K; API $0.0208/req → $541K/mo (26M × $0.0208);
  break-even $148K/$0.0208 ≈ 7.1M.
- Ch17: I(0/1/3/4) = 9,500/10,365/12,095/12,960; C ≈ 18/16/14/13; λ·W = 344
  @40, 1,380 @100, 2,760 @200; Table 17-1 (28/57/32 @40, 69/141/79 @100,
  137/282/158 @200) all recompute at u=0.7; §8 mini-case W≈13.8 s (1.08 +
  12.4 + 0.4) and 141 hosts @100 rps FP16 / 79 FP8.
- Ch18: 700/200/100 × 9.5K = 6.65M/1.9M/0.95M → $8.31/$1.90/$2.38 = $12.59/hr
  vs $23.75; $8,035/mo; weighted latency 0.70×250+0.20×300+0.10×120 ≈ 247 ms.
- Ch19: α(1/2/3/4) = 1.09/1.18/1.27/1.36×; Table 19-1 input/total/KV all
  recompute; expected input 10,350 / expected total 10,650 / α≈1.12×; T·L_agent
  = 220/440/660 ms; β(3) ≈ 1.08×; the "incremental orchestration" (~660 ms) vs
  "full service time" (~13.8 s) scope distinction held clearly.
- Ch20: 35,000/9,500 ≈ 3.7 req/s (correctly non-binding); 18/8.6 ≈ 2.1 req/s
  (binding); 8×2.1 ≈ 17 req/s; ⌈40/2.1⌉ ≈ 20, ⌈40/(2.1×0.9)⌉ ≈ 22; $20/2.1 ≈
  $9.5/req/s-hr.
- Ch21: 6/24×864,000 ≈ 216,000; 216×$5.7 ≈ $1,231 / 216×$2.8 ≈ $605;
  5%×864,000×2/24 ≈ 3,600; ~60× blast-radius reduction.
- Ch22: 9,200÷300 ≈ 30×; 92,000/3,000 @10 and 368,000/12,000 @40; 2×70B×9.2K ≈
  1.29 PFLOP; 140 GB/25 ms ≈ 5.6 TB/s; Table 22-1 provenance/status uniform
  `[canonical scenario][ASSUMPTION]` (input/output tokens) and
  `[canonical scenario][DERIVED]` (ratio); nominal-vs-measured FP8 KV note
  retained (1.31 vs 1.42 MB/token). The §6 "against one GPU's ~3.35 TB/s"
  comparison matches Ch8's established whole-model-weight-read teaching model
  (decode intensity ≈ 1.0 FLOP/byte < ~295 ridge), not a new inconsistency.
- Ch24: PIES 4×8×6×4 = 768 → 217; p ≈ 0.00104; E[total] = 10,000×0.0052 = 52;
  40×1.29 ≈ 51.5 PFLOP/s ÷ 7.9 ≈ 6.5-host floor ÷ (7.9×0.4) ≈ 16.3 hosts @40%
  MFU; Table 24-1 cycles (217→143→138, 0.006→0.003→0.0025, 7.8→5.4→4.1,
  3.1→2.4→1.3, 0.61→0.44→0.32, 8%→3.5%→1.2%) all recompute; "missing
  [FACT]/[DERIVED]/[HYPOTHESIS] axis" note retained.
- Ch25: 70B×2 B = 140 GB; INT8 → 70 GB; FP32 → 280 GB; ADR 0016 both 16-bit
  ~140 GB; ADR 0017 FP8 54% → 13.4 GB, 436÷13.4 ≈ 33; 140+436+64 = 640 GB
  envelope; ~30 GB per-request vs ~64 GB runtime reserve explicitly
  distinguished.
- Ch26: capstone/main TTFT scoped to time-to-first-token, not end-to-end ~8.6 s;
  §8 QPS capped at the ~2 req/s per-host ceiling; Table 26-2 values internally
  consistent (the Step-2 35% cache-hit is the applied assumption; the 38% in
  Table 26-2 is the measured/DERIVED observed value — the assumption-vs-observed
  distinction PASS-9 reconciled, not a live inconsistency); workload-to-strategy
  matrix coherent; utilization-note correctly frames SLO-bound resource vs bare
  percentage.
- Ch27 Appendix A: active fractions (104/2800≈3.7%, 13/284≈4.6%, 18/320≈5.6%,
  6/125≈4.8%); `[1P]` tags + verify-on-own-hardware caveats; the
  Observed/Interpretation/Hypothesis three-layer separation is clean and
  intentional (prose register, not a stray taxonomy label); Figure/Ch cross-refs
  resolve.
- Back matter: preface/sources taxonomy (five provenance × five status, plus
  the `[S#]`-is-not-provenance note) and the worksheet taxonomy all agree;
  glossary covers RQO/FSDP/CP/κ/ρ; references [S1]–[S6] present with stable
  links; worksheet line 12 possessive (PASS-12) fixed.

**Voice-hygiene sweep (zero NEW):** no reader-address "you/your" outside
in-character dialogue (Ch23 mirrored customer quote) and role-play/injection
example strings (Ch24) — exactly the pattern PASS-11/12 already cleared. Zero
"Think of X as Y", zero imperative "Consider…/Note that…/Imagine…" anywhere in
ch15–27 or back matter. No bare `[INTERPRETATION]` taxonomy label anywhere
(Ch27's "Interpretation" use is the intentional Observed/Interpretation/
Hypothesis prose register).

**Internal-naming note (not reported):** figure source filenames for a few
figures are numbered opposite their on-page order (e.g. Fig 15.1 → fig-15-1502,
Fig 15.2 → fig-15-1501; Fig 26.1 → fig-26-2602, Fig 26.2 → fig-26-2601). This is
purely an internal asset-name ordering artifact with no reader-visible effect and
is the same cosmetic class PASS-7/9 already treated as "flagged cosmetic, no
re-report"; not re-raised here.

---

## VERDICT

**NO NEW FINDINGS — ZERO new comments, ch15–27 + back matter.** Both PASS-12
survivors are confirmed fixed, every PASS-1..11 item remains resolved, and no new
defect (at any severity) is present. Convergence is complete:
PASS-8=12 → PASS-9=11 → PASS-10=24 → PASS-11=8 → PASS-12=2 → **PASS-13=0**.
The review loop can exit.
