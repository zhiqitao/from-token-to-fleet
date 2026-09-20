# PASS-5 FIXER — Responses (loop continues; new comments fixed)

## [P5-1] Ch16 §3 "Mode 2" heading duplicated. SEVERITY: Minor. STATUS: FIXED.
Location: Ch16 §3 (lines 56, 58).
Problem: The bold heading "**Mode 2 — cloud GPU instances (rent, scale to load).**" appeared
  as a standalone line (56) AND duplicated verbatim at the start of the paragraph (58),
  rendering as a repeated bold heading in the PDF.
Fix: Removed the standalone line-56 heading; kept the single heading leading the paragraph.
Verified no other duplicated bold headings in the book (programmatic scan).

## [P5-2] Ch19 §7 "95th-percentile latency ~880 ms" stale reference. SEVERITY: Minor. STATUS: FIXED.
(Follow-on from the PASS-4 Ch19 median-turn fix; found by PASS-5 ch19/25 convergence review.)
Location: Ch19 §7 "Latency tail under spike load" (line 178).
Problem: Stated "Our 95th-percentile latency of ~880 ms explains..." but with the corrected
  turn distribution the 95th percentile turn is T=3 (660 ms added overhead), not T=4 (880 ms).
Fix: Changed to "95th-percentile *added* orchestration latency of ~660 ms (T=3, the scenario
  turn cap; the 2% fallback is single-shot)". Consistent with Table 19-1 and §8.

## [P5-3] Ch12 Table 12-1 SLO column "latency in 5 s" inconsistent with TTFT SLO. SEVERITY: Minor.
Status: FIXED.
Location: Ch12 Table 12-1 (line 83).
Problem: The candidate (a) SLO column said "✓ latency in 5 s" but the chapter's canonical SLO is
  "TTFT ≤ 1.2 s (p95 ≤ 2 s)" (line 68). The "5 s" did not match the stated TTFT budget. (The
  "5 seconds end-to-end" text the reviewer's grep first surfaced lives in stale Aug-30 build
  artifacts in render/build/, not the current source — a stale-file false positive; the real,
  current-space discrepancy was Ch12's Table "5 s".)
Fix: Changed SLO column to "✓ TTFT SLO (≤1.2 s budget, p95 ≤2 s)" to match line 68.

## Confirmed non-issues this pass
- Stale render/build/_book.md + book.tex (Aug 30) contain an old "~500 employees / 5 s
  end-to-end" workload description; these are NOT part of the current build (current build
  reads design/manuscript/chapter-NN/*.md into render/latex/). Not a current-book defect.
- Ch17 C≈13 at T=4 (worst-case) verified correct (436/34.0).
- Ch16 Mode-1 per-request $5.7/1K verified correct.
