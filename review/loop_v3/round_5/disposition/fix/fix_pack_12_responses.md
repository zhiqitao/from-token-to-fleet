# Fix Pack 12 — responses (round 5)

Format: Severity | Location | Problem | Change | Status | evidence

---

**P2** | Ch 21 §6 Architecture Consequence (chapter-21.md) | Section was a cross-chapter summary, not architectural consequences | Added 3 sentences after the summary paragraph: components (evaluation runner, canary router, rollback mechanism), design decisions (gate granularity, canary routing strategy, rollback trigger), trade-offs (gate latency vs promotion speed, canary traffic vs evaluation fidelity) | **FIXED** | Premise held verbatim (quote intact, section = 2 paragraphs + Fig 21.1); new paragraph present at chapter-21.md §6, no labels/claims added beyond the fix.

**P3** | Ch 21 §7 item 2 (chapter-21.md) | "(to be verified)" ambiguous about uncertainty category | Rewrote to "is workload-dependent and evolves with traffic patterns — an ongoing verification requirement, not a gap in this manuscript's research" | **FIXED** | Premise held (bare "(to be verified)" present at line 92); grep confirms the phrase is gone and the clarified category text is in place.

**P2** | Ch 21 §7; Ch 22 §7; Ch 23 §4/§5/§7 (chapter-21.md, chapter-22.md, chapter-23.md) | Prose status variants not searchable against the [FACT]/[DERIVED]/[ASSUMPTION]/[HYPOTHESIS]/[UNRESOLVED] taxonomy | Normalized to bracketed taxonomy: "(a hypothesis)"→[HYPOTHESIS] (ch21 §7 item 1), "to be verified per service"→[UNRESOLVED] per service (ch21 §7 item 3), "(a hypothesis awaiting verification)"→[HYPOTHESIS] (ch22 §7 ×4, ch23 §7 item 2), "(to be verified) items"→[UNRESOLVED] items (ch23 §4 and §5), "(unresolved: evidence pending)"→[UNRESOLVED] (ch23 §7 ×2); "to be verified" mapped to [UNRESOLVED] (the in-pack option — adding a defined label would require editing Ch 4 / Appendix A, outside this pack's targets) | **FIXED** | All five prose variants grep-clean across the three chapters (rc=1); new marker counts ch21=2, ch22=4, ch23=6; ch22 edits are in §7 (header at line 123, bullets 128–131) as the fix_instruction names Ch 22 §7 explicitly; overlap with CH21-04 limited to ch21 §7 item 2, already clarified there first — not a duplicate (different defect, different text after that fix).

**P3** | Ch 21 §3, "Cost of a bad ungated release" (chapter-21.md) | "the direct cost" read as incident cost; $5,394 is ordinary serving volume × rate | Renamed to "the serving cost of the 216,000 requests exposed … (volume × unit rate — incurred whether or not the regression occurred)"; business-cost sentence kept as dominant term; no incident estimate added | **FIXED** | Premise held verbatim; grep confirms "the direct cost is" = 0 occurrences; arithmetic untouched (216 × 24.97 = 5,393.5 ✓).

**P3** | Table 2-1 page break (item file field says chapter-21.md; table actually lives in chapter-02.md) | Table began at page foot with only 2 rows before the break, no continuation cue | None needed — fix option "keep Table 2-1 together on one page" already implemented in current source | **SKIPPED_PREMISE** | chapter-02.md already has `\Needspace{32\baselineskip}` immediately before "### Table 2-1" (sibling working-tree edit predating this pack), which reserves 32 lines and pushes the whole ~17-line table to the next page; chapter-21.md contains no Table 2-1; PDF-level re-verification would require a full rebuild, which is forbidden here.

**P3** | Figure 21.1 in-figure note (render/fig_ch21_pipeline.py:43) | "hatched = live production stage (not gated): Serve" contradicted the sixth gate at the Promote→Serve seam | Rewrote note to "hatched = live production stage (no gate follows it): Serve"; regenerated fig-21-2101 only via render/regen_one.py | **FIXED** | regen_one.py exit 0 ("ONE-DONE fig_ch21_pipeline.py"); PNG 2135×1435 and 1-page PDF both valid; vision check of the new PNG quotes the note exactly, unclipped, no overlap, six gate boxes + hatched Serve intact.

**P1** | Ch 23 §8 mini-case, burst-buffer worked example (chapter-23.md) | Queue depth stated 200 (should be 150) and drain ~4 s (should be 3 s), contradicting the sentence's own formulas | Rewrote worked example: 200 arrive, 50 served during burst; queue depth at burst end = (200−50) × 1 = 150; drained in 150/50 = 3 s; max queue wait = 3 s; total from burst start = 4 s; conclusion (separate queue-and-drain degraded-mode SLO, option a) kept | **FIXED** | Premise held verbatim; grep confirms "200 × 1 = 200" and "in ~4 s" = 0 and the corrected strings present; arithmetic rechecked (200−50=150, 150/50=3, 1+3=4).

**P2** | Ch 23 §8, 141 rps figure (chapter-23.md) | Base figure's inputs (model size, output tokens, hardware, FLOP convention) unstated; no derivation exists anywhere in the manuscript | Stated assumptions inline: "≤141 rps — 7B FP16, ~500 output tokens/request, H100; no derivation is given elsewhere in this manuscript" (no cross-reference invented, per the instruction's note) | **FIXED** | Premise held (grep: "141" only in ch23); assumptions now present in the burst-buffer paragraph; no fabricated Ch X §Y reference.

**P3** | Ch 23 §8, burst-buffer parenthetical (chapter-23.md) | Whole explanation (formula, worked example, conclusion, response) buried in a 3-level-nested parenthetical inside one sentence | Extracted into a separate "**The burst buffer, spelled out.**" paragraph after the main mini-case sentence; main sentence now states only the conclusion ("with a 200-rps burst buffer"); closing sentence unchanged | **FIXED** | Premise held (103-word parenthetical, nesting 3, 5 semicolon clauses); new paragraph present, main restatement sentence no longer contains the parenthetical; content preserved, no claims added.

**P3** | Ch 23 §8, "measured per-host rate" label (chapter-23.md) | 141 rps is an idealized 100% MFU roofline, not a measurement | Relabeled: "drain at rate r, an idealized 100% MFU ceiling (≤141 rps …), i.e. ~42–57 rps at 30–40% MFU; the measured per-host rate must replace this before the burst budget is trusted" (symbol r kept so D·(200−r)/r still resolves) | **FIXED** | Premise held verbatim; grep confirms "the measured per-host rate r (≤141" = 0; roofline arithmetic unchanged and rechecked (0.989e15/14e9/500 = 141.3; ×0.30–0.40 → ~42–57).

**P3** | Ch 23 §3, first Architect line (chapter-23.md) | Stray line-initial tilde inside quoted dialogue | Removed: `"~How many people will use it, and how often?"` → `"How many people will use it, and how often?"` | **FIXED** | Premise held verbatim; grep confirms `"~How many people` = 0; other dialogue tildes are numeric approximations only and were left untouched (out of scope).

---

## Counts

- FIXED: 10 (CH21-01, CH21-04, LABELS-01, CH21-02, FIG-21.1-1, CH23-01, CH23-03, CH23-05, CH23-02, CH23-04)
- SKIPPED_PREMISE: 1 (T21-01)
- DUPLICATE: 0
- NEEDS_REGEN: 0
- Total: 11

## Files changed

- design/manuscript/chapter-21/chapter-21.md (CH21-01, CH21-04, CH21-02, LABELS-01 ch21 parts)
- design/manuscript/chapter-22/chapter-22.md (LABELS-01 ch22 §7 part — named explicitly by the fix_instruction)
- design/manuscript/chapter-23/chapter-23.md (CH23-01, CH23-02, CH23-03, CH23-04, CH23-05, LABELS-01 ch23 parts)
- render/fig_ch21_pipeline.py (FIG-21.1-1 note text)
- design/manuscript/chapter-21/figures/fig-21-2101.png (regenerated, single figure only)
- design/manuscript/chapter-21/figures/fig-21-2101.pdf (regenerated, single figure only)

Note: CH23-01/02/03/05 all edit the same burst-buffer passage but each prescribes a distinct change (arithmetic, provenance, mislabel, structure) — applied in pack order as complementary fixes, none redundant, so none marked DUPLICATE. No full PDF rebuild was performed.