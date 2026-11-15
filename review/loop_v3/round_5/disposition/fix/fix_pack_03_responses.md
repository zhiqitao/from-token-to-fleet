# fix_pack_03 responses — round_5 disposition (24 items: ch17 + ch13)

Format: Severity | Location | Problem | Change | Status | evidence

1. P1 | ch17 §4 Counter-scenario A (design/manuscript/chapter-17/chapter-17.md L202) | 3.35 TB/s ÷ 14 GB = 239 tok/s is a per-GPU rate labelled "per-host", and the 20,000 tok/s demand was compared against it as one-host capacity | Relabelled the rate per-GPU with explicit host scope — "~239 tok/s per GPU (one GPU serves the 7B model; ×8 if data-parallel replicated)" — and kept the downstream comparison on that scope ("the same per-GPU scope … one serving GPU"; per-host rate = per-GPU rate here) | FIXED | source now reads "per-GPU decode token rate … ~239 tok/s per GPU"; grep "per-host decode token rate" in chapter-17.md → 0 hits.

2. P3 | Fig 17.1 caption (chapter-17.md L17) | "22 with the reserve (case (ii))" conflates 21 KV-screen hosts + 1 N−1 reserve with case (ii)'s zero-spare prefill screen ⌈21.81⌉ = 22 | Caption now: "21 + 1 N−1 reserve = 22 (coincidentally equal to the case (ii) prefill screen ⌈21.81⌉ = 22 at zero spare — same number, different derivation)" | FIXED | disambiguation present verbatim in the pandoc latex output of the caption; both derivations named.

3. P1 | Table 17-2, row "N @ T=0, FP8 (C=35; 23.275)", column 100 rps (chapter-17.md L282) | ⌈860/23.275⌉ = ⌈36.949⌉ = 37, table printed 38 | 38 → 37 | FIXED | row now "| ⌈344/23.275⌉ ≈ 15 | ⌈860/23.275⌉ ≈ 37 | ⌈1720/23.275⌉ ≈ 74 |"; 860 ÷ 23.275 = 36.9495.

4. P1 | Table 17-2, same row, column 200 rps | ⌈1720/23.275⌉ = ⌈73.899⌉ = 74, table printed 75 | 75 → 74 | FIXED | same row read back from source and from pandoc output; 1720 ÷ 23.275 = 73.8990.

5. P1 | Table 17-2, same two cells (chapter-17.md L282) | same off-by-one cells as items 3/4 | — | DUPLICATE | same row already corrected by CH17-T172-01 and CH17-T172-02 (row now 15/37/74).

6. P1 | ch17 §3 L27, §3 L46, §8 continuity note L254 | §17.8's note claimed to supersede §17.3/§17.4 "where W is concerned" while their 344/21 counts stood unqualified and Table 17-2 keeps W = 8.6 s as a live row | Scoped L27 and L46 to the "non-agentic canonical request, W = 8.6 s" with a forward reference to §17.8's larger agentic W; note rewritten to "applies to the agentic T=3 scenario, and the non-agentic W = 8.6 s figures above stand for that scenario" | FIXED | grep "supersedes" in chapter-17.md → 0 hits; both scope phrases and the new note present in pandoc output.

7. P2 | ch17 §4 Counter-scenario A paragraph (L202) | paragraph names decode bandwidth, then compute/KV "not bandwidth alone", then bandwidth again as the binding term | One binding term stated (decode bandwidth, ~14 GB weight reads, per-GPU token rate); the compute/KV clause recast as a secondary check: "after bandwidth, verify compute/KV headroom at the required batch" | FIXED | paragraph now runs binding term → verification step → "the binding term is bandwidth, not memory", no contradiction left.

8. P2 | Table 17-2, same two cells | same arithmetic error | — | DUPLICATE | already fixed by CH17-T172-01/-02 (and CH17-02/CH16-17-04 cover the same cells).

9. P2 | actual location design/manuscript/chapter-16/chapter-16.md §8 L248 (pack page_hint said Ch 17 §17.8 — corrected here per fix_instruction) | "0.48 rps/replica the canonical 21-host fleet sustains" is underived and implies 4 two-GPU replicas/host, contradicting canonical TP=8 | Restated the comparison at host level — "2 rps average is 1 rps per host, well inside the 40/21 ≈ 1.9 rps per host the canonical 21-host fleet sustains" — and stated the canonical replica definition (TP=8, one model instance per host, so no per-replica rate) | FIXED | book-wide grep "0.48" and "0.25 rps" in design/manuscript → 0 hits; new host-level sentence present in pandoc output.

10. P1 | Table 17-2, same two cells | same arithmetic error | — | DUPLICATE | already fixed by CH17-T172-01/-02.

11. P2 | ch17 §4 "Simultaneous feasibility check", end of subsection (after L151) | subsection computed 93%/>100% prefill occupancy but never stated the effect on the 21/31/32 headline counts | Added "Effect on the headline counts": at the KV-screen rate prefill alone consumes ~93% (case i) or >100% (≈109%/≈101%, cases ii/iii), so 2.0 req/s/host is not simultaneously sustainable with decode and the counts are lower bounds pushed upward — by ≥ the ~7% deficit (case i) and more (cases ii/iii) | FIXED | new paragraph present in pandoc output immediately after "the sizing in this chapter is a planning bound."

12. P3 | ch17 §7 first open question (L244) | "the failover example below" — the N = 4 example is in §6, which precedes §7 | "the failover example below" → "the failover example in §6" | FIXED | grep "failover example below" in chapter-17.md → 0 hits; §6 failover example still at L232.

13. P3 | ch17 §4 "Load-balancer overhead factor" paragraph (L155) | 13 × 0.95 = 12.35 (C×ρ, no u) presented as "the slot-equivalent schedulable fraction" beside the formula's 8.645, never reconciled | States the formula's effective slot count C × u × ρ = 13 × 0.70 × 0.95 = 8.645 and labels 12.35 the ρ-only product "shown here only to be rejected", not an admission count; the rate conversion now refers to the 8.645 coefficient | FIXED | both "8.645" and "shown here only to be rejected" present in the paragraph (pandoc output).

14. P3 | ch17 §5 Common Mistake 5 (L218) | comma splice with capitalized "The" after a comma | ", The linear model" → "; the linear model" | FIXED | grep "margin, The linear" → 0 hits; sentence now "; the linear model t = t_inference + t_tool is a lower bound".

15. P3 | ch17 §4 paragraph after Table 17-1 (L118) | two different screens both print 29 (and 32) with no screen tag | Tagged every count with its screen — 21/22 (KV screen), 29 (u-only KV screen: 344/(17 × 0.70) = 28.9 → 29), 31+1 = 32 (KV-only policy), 34 (case ii), 29 (case-(i) prefill at u×ρ + spare: ⌈18.606/0.665⌉ + 1), 32 (case-(iii) prefill at u×ρ + spare) — and added "Two coincidences to keep straight … same numbers, different screens." | FIXED | new tags and the coincidence sentence present verbatim in pandoc output.

16. P2 | Fig 17.1 caption (chapter-17.md L17) + in-figure note (render/fig_ch17_capacity.py L124) | caption and figure both assert the N−1 residual "clears the burst *only* at ρ = 1" while giving break-even ρ ≥ 0.917 | Caption: "at ideal ρ = 1 the N−1 = 3 residual (~6.0 req/s) clears the ~5.5 burst with ~0.5 req/s margin; break-even is ρ ≈ 0.917, so it clears the burst only for ρ ≥ 0.917 …"; figure note: "N-1 clears the burst only for ρ ≥ 0.917: at ρ = 0.85 the residual = ~5.1 < ~5.5 (it fails)." (script docstring updated too) | FIXED | regenerated ONLY fig-17-1701 via render/regen_one.py (RC=0, PNG+PDF written); vision read-back of the new PNG quotes the new note and finds no "only at ρ = 1"; book-wide grep "clears the burst" → only the reworded caption.

17. P3 | render/fig_ch17_capacity.py L108 (Fig 17.1 y-axis) | y-axis "req·s⁻¹" vs "req/s" in title, annotations and caption | ylabel → "load / capacity (req/s)" | FIXED | same single-figure regen as item 16; vision read-back: y-axis reads "load / capacity (req/s)"; grep "req·s" in design/manuscript → 0 hits.

18. P2 | Fig 17.1 caption + in-figure note | same self-contradiction as item 16 (independently found) | — | DUPLICATE | same caption clause and same figure note already reworded under FIG-17.1-1.

19. P1 | ch13 §3 first paragraph (chapter-13.md L37/L40) | "not as the Cluster tier" contradicts the chapter's own §2 ladder and Table 13-1's "traffic > host goodput" trigger (a 21-host replica fleet is traffic-driven cluster scaling) | Now: the workload sits on the server tier "as a *fleet* of ~21 server-class hosts at the 40 rps peak (Ch 16/17) — model residency is server-class, but by Table 13-1's *traffic > host goodput* trigger the traffic scaling is a **cluster** of server-class hosts, not weight-splitting" | FIXED | grep "not as the Cluster tier" → 0 hits; the reconciled sentence appears in pandoc output.

20. P3 | ch13 §13.3 heading (chapter-13.md, line before "## 3. Worked Example") | stranded heading: last line of the page, content starts on the next page | Inserted the repo-convention reservation line `\needspace{4\baselineskip}` immediately before "## 3. Worked Example" (needspace is already loaded in book.sty; md_to_latex's fix_needspace normalises it to \Needspace) | FIXED | premise re-verified in the current build first (pdftotext of render/build/from-token-to-fleet-v20260913.pdf: PDF p235 = printed 215 ends with "13.3. Worked Example"); pandoc (same flags as md_to_latex) now emits `\needspace{4\baselineskip}` directly before `\section{3. Worked Example}` — heading + ≥2 body lines reserved. Whole PDF deliberately not rebuilt.

21. P2 | ch13 §13.2 prose trigger list vs Fig 13.1 red triggers (chapter-13.md L25-L29) | figure's within-tier "KV residency > cap → Single host" trigger absent from the prose list; prose Memory trigger not tied to a figure boundary | Chose the prose-side option: added the bullet "**KV residency per GPU**: model + KV no longer fits one GPU → single host — the within-tier step Fig 13.1 shows between Single GPU and Single host.", tagged the Memory bullet "— the Single host → Multi-host climb in Fig 13.1.", and changed the lead-in "The three classic triggers" → "The classic triggers" | FIXED | new bullet and boundary tag present in pandoc output; figure binary untouched by this item (no generator change needed).

22. P2 | Fig 13.1 caption (chapter-13.md L92) | rung names (Single GPU/Single host/Multi-host/Cluster-fleet) do not map one-to-one onto §13.1's four numbered tiers | Appended to the caption: "Rungs refine the §13.1 tiers: Single GPU = Local/edge, Single host = Server, Multi-host = Cluster, Cluster/fleet = Hyperscale fleet." | FIXED | mapping note appears inside `\caption{…}` in the pandoc output of chapter-13.md.

23. P2 | render/fig_ch13_escalation.py L50 (four green markers in Fig 13.1) | "▼ constraints → STOP" reads as "constraints cause STOP", inverting the figure's own bottom note | Markers → "no binding / constraint → STOP" (instruction's wording, wrapped to two lines so it clears the red trigger band) | FIXED | regenerated ONLY fig-13-1301 via render/regen_one.py (RC=0, PNG+PDF written); vision read-back quotes all four markers as "no binding / constraint → STOP"; renderer probe: 0 marker/trigger overlaps, all text inside the 610×700 px canvas.

24. P3 | render/fig_ch13_escalation.py L96-L98 (bottom note) and L50-L51 (STOP lines) | bottom note measured ≈7 pt / ~49% K (below the 8 pt floor), STOP lines at the 8.0 pt floor | Note → 9.0 pt, color #4d4d4d (70% K ≥ 60% K), wrapped to two lines so it fits the 6.1 in print canvas; STOP lines → 8.5 pt (≥ the 8.0 pt box sub-label) | FIXED | same single-figure regen as item 23; probe reports note fs 9.0 color #4d4d4d fully inside the canvas and stops fs 8.5; vision read-back confirms the note is complete and unclipped on both edges.

## Counts

- FIXED: 20 (items 1,2,3,4,6,7,9,11,12,13,14,15,16,17,19,20,21,22,23,24)
- SKIPPED_PREMISE: 0
- NEEDS_REGEN: 0
- DUPLICATE: 4 (items 5, 8, 10, 18)
- Total: 24

## Files changed

- design/manuscript/chapter-17/chapter-17.md (items 1,2,3,4,6,7,11,12,13,14,15,16)
- design/manuscript/chapter-16/chapter-16.md (item 9)
- design/manuscript/chapter-13/chapter-13.md (items 19,20,21,22)
- render/fig_ch17_capacity.py (items 16,17) → design/manuscript/chapter-17/figures/fig-17-1701.png + .pdf regenerated
- render/fig_ch13_escalation.py (items 23,24) → design/manuscript/chapter-13/figures/fig-13-1301.png + .pdf regenerated
- review/loop_v3/round_5/disposition/fix/fix_pack_03_responses.md (this file)

Regeneration used `python render/regen_one.py <script>` only (matplotlib was absent from the system Python, so a scratch venv at ~/.hermes/profiles/muta/cache/scratch/figenv was created to run it); no other figure and no PDF was rebuilt.