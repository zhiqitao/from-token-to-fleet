# PASS-1 REVIEWER — Complete Findings (compiled & verified)

See pass1_objective_findings.md for the figure-legibility details. Below are the merged,
VERIFIED findings from the whole-PDF review (objective audits + 4 chapter deep-read subagents,
each claim checked against source before recording).

========================================================
A. WHOLE-BOOK FINDINGS
========================================================

[A-1] MAJOR — Ch7 fine-tuning residency arithmetic is internally inconsistent.
Location: Ch7 Table 7-2 row 2 + prose (md lines 82, 87, 117, 127, 155).
Problem: Row 82 states "~16 B/param (m + v + ΔW)" but "~1,260 GB" total. 70B × 16 B/param
  = 1,120 GB, not 1,260 (1,260 implies 18 B/param). Prose repeats "~1.26 TB"/"~1,260 GB"
  and "roughly 2×8×H100". The standard full-Adam FP16 figure is:
  weights(140) + grads(140) + m(280) + v(280) + master(280) = 1,120 GB = 16 B/param.
Why it matters: Same chapter that teaches "memory is the first constraint" for inference must
  be exact about the fine-tuning floor; an off-by-37% residency number would mis-size a
  fine-tuning node. Violates the book's own "defensible by arithmetic" thesis.
Recommended change: set total to ~1,120 GB (16 B/param) throughout Ch7 Table 7-2 row 2 and
  all prose references; keep "exceeds 1 TB" but fix the 2×8×H100 phrasing (~1.75×).

[A-2] MAJOR — Figure label legibility: several figures carry in-figure text below the 7.5pt
  on-page floor (Fig 9.1 axis ticks 7.28pt; Fig 10.1 sub-labels 5.79-7.44pt; Fig 15.1
  FlashAttention annotations 6.97pt; Fig 16.1 legend/annotations 6.22-7.0pt cramped; Fig 19.1
  state ids 6.53pt). See pass1_objective_findings.md for exact per-figure measurement.
  Fix: raise author font (author at column width so no downscale), for wide figures narrow
  content (per the font-bump paradox).

[A-3] MAJOR — Fig 19.1 reading-order ambiguity: three egress connectors from the "Decide"
  box (loop-back, resolved, stopped) are tightly packed/crossing, making the state-machine
  transition ambiguous at print scale. Fix: reroute the three connectors with clear
  horizontal separation.

[A-4] MODERATE — Glossary omits several load-bearing mechanism terms used heavily in the body
  and covered by whole figures: FlashAttention, PagedAttention, continuous batching,
  arithmetic intensity / roofline / ridge, MoE, HBM. Fix: add a "Serving & mechanisms" group.

[A-5] MINOR — Preface figures numbered "figure 1"/"figure 2" (plain integers) while all body
  figures use "N.N"; inconsistent numbering scheme.

========================================================
B. PAGE/LOCATION-SPECIFIC (from deep-read subagents, verified)
========================================================

# Ch1-6 (subagent task-0)
- (verified non-defect) Ch1 §1 KV formula presented as "generic" full-MHA: Ch1 explicitly
  defers precision to Ch7 ("We deliberately keep this to concept + order of magnitude here"),
  and 2×80×8192×1 = 1.31 MB matches canonical 8-bit. Not a defect.

# Ch7-12 (subagent task-1) — see A-1/A-2/A-3 lead.

# Ch13-18 (subagent task-2)
- Note on strengths: Ch15 strong; Ch16/17/18 tables & mini-cases verified consistent with
  source and tco_calc.py; break-even ~7.1M req/mo confirmed correct.

# Ch19-27 (subagent task-3)
- Note on strengths: Ch27 (Appendix A) genuinely strong — [1P] tags consistent, 2026-08-30
  snapshot date explicit, sources well-formed, Observed/Interpretation/Hypothesis separation
  clean. Back matter (glossary/sources/worksheet) verified coherent.

========================================================
H. FINAL REMAINING-RISK ASSESSMENT
========================================================
- Strengths verified: canonical-number chain (TTFT 1.08s, W 8.6s, 344 in-flight, 20 hosts,
  2.62 MB/token), cross-reference integrity, evidence taxonomy compliance, voice-hygiene
  (0 narrator violations), source URLs resolve, no broken figures, figures in margins.
- Remaining risks: figure on-page label legs below floor in ~5 figures (A-2) — highest-risk
  visual area; Ch7 fine-tuning number (A-1) — the one genuine numerical error found this pass.
