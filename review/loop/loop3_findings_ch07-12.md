# Loop-3 Final Convergence Re-Review — Chapters 7–12

**Built PDF:** `render/build/from-token-to-fleet-v20260913.pdf` — **366 pp.** (rebuilt 2026-10-25 18:30; the Loop-2 build was 358 pp., so all page numbers below are re-mapped).
**Range:** PDF pp. 110–182. Ch openers: 7→p111, 8→p127, 9→p140, 10→p149, 11→p158, 12→p171, 13→p183. Body label = PDF page − 18 (unchanged).
**Standard:** `review/complete-manuscript-review-prompt.md` (read in full). Predecessors: `loop1_findings_ch07-12.md`, `loop2_findings_ch07-12.md`.
**Method:** pymupdf per-page text/span/drawing extraction; automated class scans (voice, tags, placeholders, glyphs, sub-8 pt spans, ink-extent vs the 525.6 pt column, duplicate-header rule geometry, LoF cross-check); 35-item independent arithmetic re-derivation; 140 dpi renders of 10 pages inspected via vision (Figs 7.2, 7.3, 9.1, 11.1, 11.3, 12.1; Tables 8-1, 12-1, 12-2).
**Mode:** READ-ONLY — no source, build, or commit touched; this file is the only write.

Severity totals: **CRITICAL 0 · MAJOR 1 · MODERATE 3 · MINOR 8** (12 findings — down from 54 in Loop 2).

---

## A. Focus item 1 — ch12 candidate-survival reconciliation: **CONFIRMED SELF-CONSISTENT**

| Artifact | PDF page | What it now says | Verdict |
|---|---|---|---|
| Fig 12.1 | p178 (body 160) | `④ OUTCOME / SURVIVORS (a) · (b) / each needs a ~5-host prefill pool` and `✗ GATED / (c) pending Ch. 14`; caption: "three **conditional candidates**, each with its own open validation gate (not a settled verdict) … per-candidate verdicts in Table 12-1 / §12.3" | ✅ |
| §12.8 prose | p177 (159) | "Because candidate (c) is strongly suspected to fail the quality gate **[HYPOTHESIS]**, it is not a finalist; **the finalists are Candidates (a) and (b)**, and the near-term decision falls between them." | ✅ |
| Table 12-1 verdict column | p179 (161) | (a) "**conditional finalist** — ✗ single-host capacity: needs ~5 hosts"; (b) "**conditional finalist** — ✗ throughput at a single prefill host…"; (c) "**gated, not a finalist** — ✗ quality gate open (Ch 14); ✗ >1 card at peak" | ✅ |
| Closing paragraph | p182 (164) | "no candidate is a deployment-validated survivor; all three are conditional candidates with an open validation gate" | ✅ (qualifies the figure's SURVIVORS label) |

Vision p178: connector branches from CANDIDATES via a bus with **two arrowheads** (one per box); GATED box carries diagonal hatch + ✗ (non-colour cues); no collisions, no sub-8 pt labels. Vision p179: all ✓/✗ markers render as **clean glyphs — no tofu** (the `\x17` in text extraction is the ✗ mapping artifact, as Loop 1 noted). Loop-2's MAJOR three-way conflict is **resolved**; the caption's "not a settled verdict" is now consistent with a diagram whose ✗ means "gated/pending", not "rejected".

## B. Focus item 2 — Loop-2 figure fixes: **ALL HOLD**

| Fix | PDF page | Vision evidence |
|---|---|---|
| Fig 7.2 red label no longer grazes the curve | p122 (104) | "9.2K ≈ 24 GB (FP16 bound)" sits in clear whitespace; the only line touching the red curve is an **intentional leader arrow** to the 10 K marker. Blue GQA annotation in open region right of where curves end. No collisions/clipping; smallest in-figure text ≈9–10 pt. |
| Fig 7.3 green annotation off the border | p123 (105) | "QLoRA fits a single H100" stops a clear margin inside the right spine; no reference line crosses any value tag; three lines use distinct dash/dash-dot/dot patterns + legend labels (grayscale-safe); no sub-8 pt text. |
| Fig 9.1 y-axis | p143 (125) | Axis renumbered to plain values (1, 10, … 100000) — **the ~5–6 pt 10^x superscripts are gone**; no curve/label collisions, no clipping. *New residual:* top tick reads **`1e+06`** (finding M3). |
| Fig 11.3 | p168 (150) | No stray tick; all directional connectors have arrowheads; caption cites **§9.8** (not §9.5) and uses **~0.08 s @ 450 GB/s per direction**; smallest label ≈9 pt. |
| Fig 12.1 | p178 (160) | See §A. |

## C. Focus item 3 — new contradictions from Loop-2 edits: **NONE FOUND** (one rounding note)

| Loop-2 edit | Re-derivation / audit | Result |
|---|---|---|
| MFU expansion (p132/133) | "at MFU (model FLOPs utilization)"; "sustained model FLOPs utilization (MFU)". Book-wide grep: **0** "mixed-precision … MFU". Glossary p349: "MFU — model FLOPs utilization" | ✅ consistent |
| 475.5 GB (Table 7-1, p114/115) | 128,000 × 2,621,440 B = 335.54 GB → 140 + 335.5 = **475.5**; fits-row "475.5 GB < 640 GB"; 32K row 83.9 on the same exact-byte basis | ✅ one basis throughout |
| 25 Gb/s ≈350× (p141) | 140/2.5 = 56 s; 140/900 = 0.156 s; 56/0.16 = 350 as written; §9.2 "~35×" (5.6 vs 0.16) and §9.6 "~350× vs RoCE" (98/0.27 = 363) all agree. *Note:* exact bandwidth ratios are 900/2.5 = **360×** and 900/25 = **36×**; the chapter consistently rounds down to 350/35 using its own rounded 0.16 s — internally consistent, ~3 % below exact. | ✅ (no contradiction; "~360×/36×" would be exact) |
| DFlash 2.5× vs EAGLE-3 (p159/164) | S5 now complete: "Chen et al., 'DFlash: Block Diffusion…,' ICML 2026 (PMLR v306; arXiv:2602.06036) … >6× … (up to 6.1× on Qwen3-8B) and up to 2.5× faster than … EAGLE-3". The 2.5× is now **vs EAGLE-3**, not a qualifier of >6× — contradiction gone; p164/p169 quotes match the key. [1P] on paper results matches the taxonomy (p323: "[1P] covers … a vendor or paper author's figure"). | ✅ |
| S6 pointer list (p160) | Now "Chapters 1, 3, 6, 7, 15, 22 and Appendix A". Book-wide audit of "54%": Ch 1 (p24), **Ch 3 (p51)**, Ch 6 (p109), Ch 7 (p119), Ch 11 (p160 = the key itself), Ch 15 (p207/208), Ch 22 (p288), App A (p342), glossary (p349/354/360). Every listed chapter is real (Loop-2's "Ch 2" was actually Ch 3). | ✅ w/ residual M6 (glossary not listed) |

---

## D. Findings

| Sev | PDF page (body) | Location | Problem | Why it matters | Recommended change |
|---|---|---|---|---|---|
| MAJOR | 132 (114), 153 (135), 180 (162), 181 (163) | Table 8-1 continuation; Table 10-1 first data page; Table 12-1 continuation; Table 12-2 first data page | **Duplicated table headers / empty ruled band — a build artifact.** Vision p132: header "metric value derivation" printed **twice**, stacked, with rules above/below each (rule geometry 72/98/113/139). Vision p181: the full 7-column header printed twice with a **blank, double-ruled band** between the copies (zero data rows under the first copy). p153: identical header lines at y80/y121 + rules 72/98/114/139. p180: repeated header then an empty 25 pt band between rules y122/y147 before the footnote. Tables 7-1/7-2/9-1/11-1/11-2 continuations show only a single header — the defect is specific to tables whose caption/heading sits on the previous page. | A reader sees what looks like a broken/duplicated table on four pages; it is the classic double-`\endhead` typesetting bug and undermines care on exactly the chapter-summary tables. | Suppress the first header copy when the body starts (or drop the carryover header); re-render and re-check all continued tables book-wide. |
| MODERATE | 131 (113), 152 (134), 180 (162) | Table 8-1 caption; Table 10-1 caption; §12.8.2 heading + intro | **Caption/heading stranded with ~315–347 pt (~40–47 %) of trailing blank; table body on the next page.** p131: caption block ends y397 (text limit ≈712), table rows on p132. p152: "Table 10-1 — Parallelism strategies at a glance" is the last line at y392, table entirely on p153. p180: §12.8.2 heading + intro end y365, Table 12-2 on p181. | Excessive blank space + caption separated from its table by a page break is a §49 publication defect — and it is the trigger for the MAJOR double-header bug (finding 1). | Keep caption + at least the header + first rows together (move the float earlier or shrink it); then re-verify the header duplication is gone. |
| MODERATE | 161→162 (143→144) | §11.3.3 lead-in vs Fig 11.1 | **Figure-description-before-figure:** §11.3.3 ends with the figure's lead-in ("Discrete batching runs each batch to completion … (Illustrative, after Orca, OSDI 2022.)") on p161, but the rest of p161 then contains **§11.3.4 (PagedAttention), §11.3.5 (Prefix Caching) and the start of §11.3.6** before the reader reaches Fig 11.1 at the top of p162. | The described diagram appears two subsections after its description; the reader must hold the slot-diagram mental model across unrelated mechanism text. | Force the figure to float within §11.3.3 (place it before §11.3.4), or move the lead-in to the figure page. |
| MODERATE | 169 (151) | §11.7 "What We Still Don't Know" | **Uncertainty-tag drift — the last unfixed instance of the Loop-2 class.** Three ad-hoc parentheticals: "general rules are **(a hypothesis)**" (dangling, ungrammatical as written), and two "**(to be verified)**" (RadixAttention/APC prefill-FLOP reduction; Mooncake KV-transfer crossover). No tag lead-in, while §12.7 has "each flagged [HYPOTHESIS]" and §10.7 now uses "[TODO: measure on target cluster]". The Mooncake crossover is measurable on target hardware — the same class Loop-2 re-filed as a measurement TODO in §10.7. | The book's own tag vocabulary exists; three prose holdouts in one section read as unfinished editing, and one item is filed under the wrong uncertainty category (standard §38). | Rewrite bullet 1 as prose + [HYPOTHESIS]; replace both "(to be verified)" with the standard tag — the crossover as "[TODO: measure on target cluster]" (matching §10.7), the prefix-hit rate as "[HYPOTHESIS]"; add the same one-line lead-in used in §12.7. |
| MINOR | 143 (125) | Fig 9.1 y-axis, top tick | **New from the Loop-2 y-axis fix:** the axis now reads 1, 10, 100, 1000, 10000, 100000, **`1e+06`** — five plain decimal ticks then a machine-notation tick. | Mixed tick formats in one axis read as auto-generated output; inconsistent with the x-axis decimals. | Set the top tick as "1,000,000" (or re-limit the axis to 100000). |
| MINOR | 144 (126) | §9.3 ring equation, B_eff subscript | The **5.98 pt "eff" subscript** persists — the only sub-8 pt text span in pp110–182 (all other spans ≥7.97 pt; figure text ≥8 pt per vision). | Below the ≥8 pt floor in the one spot Loop-2 named; 6 pt against an 8 pt rule. | Raise the subscript to ≥7 pt or document an exemption for math subscripts. |
| MINOR | 179 (161) | Table 12-1 header + body cells | Stranded operators persist and spread: header still wraps `memory:` / `weights +` / `KV` (**"+" at line end**, Loop-2 residual, vision-confirmed); body cells now also strand **"140 + 24 ="**, **"14 + ~1.2 ="** (total on next line, all three rows), **"8×H100 +"**, **"4.65) +"**, **"~2× capex +"**. | Dangling binary operators at line ends are the same defect class the standard's table review rejects; the totals being pushed to their own line weakens the arithmetic scan-path. | Reword headers ("memory: weights+KV" / "weights and KV") and widen the memory/verdict columns so "=" and "+" stay with both operands. |
| MINOR | 23 (5) vs 113 (95) | Ch 1 first GQA use vs Table 7-1 note | **Loop-2's fix did not land:** "GQA" is still first used unexpanded in Ch 1 (p23: "GQA/MQA head sharing"); the first expansion is now the Table 7-1 note on p113 ("a grouped-query attention (GQA) model…"). | Term used before defined (standard §35); the definition lands 90 pages after first use. | Expand at first use in Ch 1 ("grouped-query attention (GQA)"), keep the ch7 expansion as a reminder. |
| MINOR | 114 (96) | Table 7-1 derivation note | Bare section cross-ref survives: "scale-offset metadata overhead is NOT vendor-measured **(see §3)**" — reads as Chapter 3. All other bare-§N instances flagged by Loop-2 (pp139/147/150/170/173/174) are fixed to full identifiers. | One ambiguous navigation pointer left in an otherwise-standardised set. | "(see §7.3)". |
| MINOR | 160 (142) | [S6] source key pointer list | Chapters listed are now all correct, but the **glossary** carries three 54% mentions (p349/354/360) and [S6] tags (p354/358/360) yet is absent from "Any reference to it (Chapters 1, 3, 6, 7, 15, 22 and Appendix A)". (Ch 11's p160 mention is the key itself — self-exclusion is fine.) | The key's audit trail still omits real references — the exact defect Loop-2 flagged, reduced but not eliminated. | Append "and the glossary" (or "Glossary") to the list. |
| MINOR | 162 (144) | Fig 11.1 annotations | Loop-2 residuals persist: **two leader lines still have no arrowheads** (red "idle (bubble)" pointer; grey "a finishing sequence frees its slot" pointer), and a short vertical tick still rises from the top of the "next batch waits" box. *Correction to Loop-2:* the tick is in the **discrete (left)** panel on the box's top edge, not crossing the continuous panel's top-left. | Arrowless leaders leave direction ambiguous; the tick reads as rendering debris. | Add arrowheads (or delete the leaders); delete the tick or make it an intentional axis mark. |
| MINOR | 156 (138) | §10.7 first bullet | The Loop-2-prescribed fix landed but duplicates itself: "the exact NVLink-vs-fabric crossover for a given model is **a measurement TODO [TODO: measure on target cluster]**" — prose and tag say the same thing, and the word "TODO" appears twice in one sentence. | Reads like an unresolved editor note rather than a scoped measurement item. | "…crossover for a given model is unmeasured [TODO: measure on target cluster]" (keep the tag, drop the prose "TODO"). |

---

## E. Loop-2 named findings — status (54 rows)

**MAJOR — 6/6 FIXED:** XNAME placeholder (gone book-wide) · "25 GB/s … more than 5×" (rewritten p141, see §C rounding note) · MFU "mixed-precision" expansion (fixed p132/133, glossary-consistent) · ch12 three-way verdict conflict (fixed, §A) · Table 12-2 qualitative host cells (now "~1 (92K ÷ ~197K)" / "~2 (368K ÷ ~197K), before headroom", p181) · §12.7 literal ` - ` list (now real bullets + single [HYPOTHESIS] lead-in, p176).

**MODERATE — 21/22 fixed or absorbed; 1 partial, plus 1 Loop-2 missed:**

| Loop-2 item (old page) | Status |
|---|---|
| Fig 12.1 caption cites non-existent "one prefill host fails" line | ✅ caption rewritten |
| §12.8.1 heading stranded from Table 12-1 | ✅ heading now atop p179 with its table |
| Fig 11.1 caption "vertical column" vs staircase | ✅ caption now "step boundaries are staggered across rows" |
| Ch11 opener "stack" vs Fig 11.2 "not a stack" | ✅ opener now "a small set of composable mechanisms" (p158) |
| §11.3.3 triple retelling + duplicate OSDI source note | ✅ one lead-in; source note appears once (p161); caption carries none |
| Two paragraphs re-stating Fig 11.2/11.3 captions | ✅ none remain (p168 ends at caption; p169 opens §11.7) |
| Ch8 "just below the ridge" summary | ✅ p134: "far left of the chart (~1 FLOP/byte, ~295× below the ridge)"; now adjacent to Fig 8.2 (p135) |
| §7.2 "KV-heads = query-heads = hidden_dim" | ✅ p115: "n_KV-heads × head_dim = hidden_dim, i.e. KVMHA per-token = 2 × nlayers × dhidden × B" |
| §8.7 H200 FP8-ridge direction error | ✅ p137 rewritten and correct (250 on 295 vs 206; "a higher ridge … makes compute-bound harder"; precision-scaling invariance stated) |
| §9.3 40 GB/s above per-link line rate | ✅ p144: "(aggregated across 2 HDR rails/ports per node — the multi-rail effective bandwidth referenced in §9.2 and Fig 9.1)" |
| 0.04 s at bidirectional aggregate | ✅ 0.04 gone; p168 uses "~0.08 s … at NVLink's 450 GB/s per direction" |
| Fig 11.3 cross-ref §9.5 → wrong section | ✅ now §9.8 |
| DFlash >6× vs 2.5× + incomplete S5 | ✅ see §C |
| S6 pointer list wrong chapters | ✅ w/ residual M6 |
| §11.6.1 engine matrix unnumbered/uncaptioned | ✅ "Table 11-2 — Serving engines by architectural capability (time-sensitive)" (p165) |
| Table 12-2 "$148K × 20 hosts" + basis switch | ✅ p181: "~20 hosts, ~$148K/mo total (self-host, Ch 16); cloud-equivalent ≈$292K (§12.8)"; row (b) "+ fabric (adder not costed in Ch 16)" |
| §12.7 "§3" wrong cross-ref | ✅ now §12.4 |
| §8.6 "Chapters 15–20" derivation scope | ✅ p133: "Chapter 17, with the cost basis in Chapter 16" |
| §7.7 first bullet (GQA restatement as "unknown") | ✅ p120 retitled "Per-model KV state beyond K/V…" |
| §8.6 batch 8–16 "toward the ridge" | ✅ p134: "~32 FLOP/byte, still ~9× below the 295 ridge (… batch ≈ 295 …)" |
| GQA used before expansion | ❌ **NOT FIXED → M5** |
| "(to be verified)"/"(a hypothesis)" tag drift | ⚠️ **PARTIAL → M4** (§10.7 and §12.7 fixed; §11.7 remains) |
| [1P] on book-derived canonical numbers | ✅ now "[ASSUMPTION] canonical (Ch 4, Table 4-3)" (pp172/175); matches taxonomy p323 |
| §9.6 "2 orders of magnitude" | ✅ p146: "~22× vs InfiniBand and ~350× vs RoCE" |

**MINOR — 22/24 fixed; 2 partial:**

| Loop-2 item | Status |
|---|---|
| Fig 7.2 red label graze | ✅ (§B) |
| Fig 7.3 green annotation at border | ✅ (§B) |
| Fig 11.x stray tick + arrowless leaders | ⚠️ **PARTIAL → M10** (Fig 11.3 clean; Fig 11.1 leaders still arrowless) |
| Table 11-1 unbracketed S-keys / row-1 [1P] | ✅ p163: "[S1][1P]"…; row 1 Source = "—" |
| Table 9-1 four-line header | ✅ single-line header (p141) |
| Table 7-1 rounding basis (475.0/335.4/83.8) | ✅ 83.9 / 335.5 / 475.5, one exact-byte basis |
| Sub-8 pt set (Fig 9.1 exponents, 5.98 pt 'eff', Fig 11.3 raster) | ⚠️ **MOSTLY → M2** (Fig 9.1 superscripts gone; 'eff' remains; Fig 11.3 labels now ≈9 pt) |
| Header-wrap set (7-2 "GB)", 12-1 "+", 12-2 stagger, engine note) | ⚠️ **PARTIAL → M4/M7** (7-2, 12-2, engine header fixed; 12-1 "+" + body operators remain) |
| Engine cell "of-/fload" hyphenation | ✅ now renders "re-compute/off-load" (p165) |
| Table 8-1 caption scope / no "(continued)" | ⚠️ caption widened ✅; continuation page still uncaptioned **and** double-headed (folded into F1/F2) |
| NCCL unexpanded | ✅ p112 "NCCL (NVIDIA Collective Communications Library)" |
| §7.6 bullet "≈2.5 MB/token" | ✅ p119 (§7.5): "≈2.62 MB/token (2.5 MiB — §7.4)" |
| "2–22×TTFT" + untagged range | ✅ p121: "2–22× TTFT … [S7][1P][FACT]" |
| §9.5 56 s vs 98 s | ✅ p145: "~56 s per step (a flat lower bound; ~98 s …)" |
| Bare "§N" cross-refs | ⚠️ **PARTIAL → M9** (all fixed except p114 "(see §3)") |
| Table 10-1 DP row 2.5 MB → 24.1 GB | ✅ p154: "~2.62 MB/token at FP16 (2.5 MiB) … ~24.1 GB" |
| §10.8 "~11×H100 minimum" | ✅ p157: "~10×H100 for weights alone (~11 once KV/workspace is included)" |
| §11.3.1 nested parens / pseudo-tag | ✅ p160: "Recall the canonical enterprise-Q&A RAG workload (Ch 4, Table 4-3):" |
| §11.6 "hold TTFT under 10 rps" | ✅ p164: "hold TTFT under the SLO (1.2 s, p95 ≤ 2 s) at 10 rps…" |
| Fig 11.1 "Ch 11 §4" self-refs | ✅ "§11.4" in caption and in-figure note |
| "5.6 TB/s aggregate single-device" | ✅ p161/p165: "whole-model weight-read rate of ~5.6 TB/s if served by one device … sharded to ~0.70 TB/s per GPU" |
| "Treat it as a map" imperative | ✅ p165: "The table is a map of which mechanism to look for, not a ranking." |
| §12.5 "15–20% of residency" | ✅ p175: "≈15% … (24.1/164.1; rising past 20% beyond ~11K)" |
| ASD-STE sentence-length style pass | ➖ not re-measured; remains a style pass, not a per-sentence defect |

## F. Classes checked and CLEAN (stated explicitly)

- **Left-over you/your:** **0** occurrences of you/your/yourself in pp110–182; **0** "think of / imagine / picture / ask yourself" constructions. Ch11 and ch12 openers remain neutralised.
- **Literal ` - ` markdown list leaks:** **0** in range; §12.7 renders as true "•" bullets.
- **Stray asterisks:** **0** `*` characters in range (Loop-1's "not*" artifact gone).
- **XNAME / placeholder tokens:** XNAME **0 book-wide**; no TODO/FIXME/XXX/⟨…⟩/TBD except the intentional, Loop-2-prescribed `[TODO: measure on target cluster]` tag (M11 concerns only its prose duplication).
- **Tofu / broken glyphs:** **0** notdef/replacement chars; ✓ ✗ × · ≪ ÷ ≈ ≤ — all render clean (vision pp178/179/181).
- **Sub-8 pt text:** only the 5.98 pt "eff" subscript (M2). All other spans in range ≥7.97 pt; all figure text ≥8 pt by span measurement and vision (7.2, 7.3, 9.1, 11.1, 11.3, 12.1).
- **Table overflow past 525.6 pt:** **none.** Pixel-ink measurement at 150 dpi: max right ink 526.6 pt (antialias) on pp113/116/141/142; tables 132/153 ≤525.6; 179/181 end at 510.7/510.2. The 531.2 pt span bboxes ("2 ×", "nccl-tests") remain advance-width artifacts. Vision confirms no cell crosses the margin on pp132/179/181.
- **Stranded section headings:** **none.** No section heading is the last block on any page; the two lowest (§7.8 p121, §9.2 p141, both y≈650) each carry 2 body lines. §12.8.1 now sits atop its table (Loop-2's stranded heading fixed). Stranded *table captions* are finding F2.
- **Figure-description-before-figure:** only Fig 11.1 (M3). §10.6's orphaned "five parallelization strategies" caption stays fixed (normal prose); no italic caption-styled block appears without its figure anywhere in range; Fig 9.1's old duplicate caption on the preceding page is gone (single caption p143).
- **List-of-Figures accuracy:** all 13 ch7–12 entries match the built pages exactly (7.1→98, 7.2→104, 7.3→105, 7.4→106, 7.5→107, 8.1→111, 8.2→117, 9.1→125, 10.1→133, 11.1→144, 11.2→149, 11.3→150, 12.1→160).
- **Evidence tags on canonical numbers:** [1P]-on-book-construct drift fixed; [1P] on paper results matches the taxonomy definition (p323).

## G. Arithmetic re-derivation sample (35 checks, 0 mismatches)

2×70B = 140 GFLOP/token · 2NL = 1.288 PFLOP · ×10 rps = 12.9 PFLOP/s · 989×0.35 = 346 TFLOPS · 346 TFLOPS ÷ 140 GFLOP = 2,472 ≈ 2,471 tok/s/GPU · ×8 = 19,780 ≈ 19,800/host · ridge 989 ÷ 3.35 = 295.2 · 92K ÷ 19.78K = 4.65 hosts · 368K ÷ 19.78K = 18.60 (ceil 19) · 9,200 × 2,621,440 B = 24.12 GB · ÷2 = 12.06 GB · 128,000 × 2,621,440 B = 335.5 GB → 140+335.5 = 475.5 · 32,000 × = 83.9 GB · 140/2.5 = 56 s, 140/900 = 0.156 s (ratio 360× exact; text 350× on its rounded 0.16 s) · 140/25 = 5.6 s (ratio 36× exact; text ~35×) · ring 1.75×140/40 = 6.13 ≈ 6.1 s · 1.75×140/2.5 = 98 s · 1.75×140/900 = 0.272 s · 6.13/0.272 = 22.5 ≈ 22× · 98/0.272 = 360 ≈ 350× · 7B: 346 TFLOPS ÷ 14 GFLOP = 24.7K/GPU → 197.8K/host · $20×730 = $14.6K · 24.1/164.1 = 14.7% ≈ 15% · 1.288 PFLOP ÷ 1.08 s = 1.19 PFLOPS · 19.78K ÷ 0.7 = 28.3K ≈ 28K · 436/24.9 = 17.5 concurrency · $116K+$22K+$10K = $148K.

## H. Remaining-risk assessment (ch7–12)

1. **Strongest remaining risk is layout, not content:** the rebuild introduced a double-header/blank-band artifact on four table pages (F1) and three ~40 %-blank caption pages (F2). These are build-level; fix the float/header logic, then re-scan every continued table book-wide (other chapter ranges likely share it).
2. **Content convergence is essentially achieved:** all 6 Loop-2 MAJORs and 21/22 Loop-2 MODERATEs verified fixed in the built PDF; the ch12 verdict triangle and all named figure fixes hold under vision.
3. **Worth one more targeted pass:** §11.7 tag cleanup (M4) after edit; Fig 11.1 arrowheads (M10); Table 12-1 column widths (M7) — then re-verify pp131/132/152/153/180/181 only.
4. **Claims needing verification (outside this range's control):** S5's identifiers (ICML 2026 / PMLR v306 / arXiv:2602.06036) are now complete but were not externally verified in this pass; the 350×/360× rounding should be standardised in one place (§9.1) if exactness is wanted.
5. **Most likely to still hide subtle problems:** ch9's flat-vs-ring lower-bound pairs (56 s/98 s, 0.16 s/0.27 s) are correct but rely on the reader tracking two bases; and Table 12-2's ~19-vs-~20 host counts (headroom +1 implied, unstated) are reconcilable but not spelled out.