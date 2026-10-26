# Loop 5 — Convergence re-review, front matter + Chapters 1–6

**Artifact:** `render/build/from-token-to-fleet-v20260913.pdf` (363 pp; scope = PDF pp. 1–107 = front matter + Ch 1–6)
**Method:** full read of `review/complete-manuscript-review-prompt.md` (§§1–53); regression read of loop1–4 findings; full text read of every in-scope page; PyMuPDF audits (label census, cross-ref resolution, bracket balance, font-size census, frame-overflow, caption/continuation checks); 11 figure pages rendered at 150 dpi and inspected; 73 independent arithmetic re-derivations.
**Page convention:** chapter pages cited as "PDF p.N (printed p.M)" — printed = PDF − 18; front matter cited by PDF page + printed roman.
**Read-only:** no manuscript file was modified.

---

## 1. Findings

| ID | Sev | Location | Class | Finding (evidence) |
|---|---|---|---|---|
| L5-M1 | **MAJOR** | PDF p.16 (Preface, printed x) ×2; PDF p.87 (Ch 5, printed 69); PDF pp.353, 356 (Sources, printed 335/338) ×3 | cross-ref / structural (§29) | **The Table 4-3 → 4-2 renumber is incomplete: 6 stale `Table 4-3` references remain book-wide, 3 in scope.** The Preface's evidence-discipline page — the taxonomy's home — tells the reader the canonical workload is "(Ch. 4, Table 4-3)" twice; Ch 5 §5.3.1 says the 1 M-chunk corpus is "not part of Table 4‑3"; the Sources chapter repeats it twice. A reader following any of them finds no such table. Separately, the merged flagship **Table 4-1 has zero inbound references book-wide** (its only occurrence is its own caption), so the six-dimension table is unreachable by cross-ref. 54 refs do now point at Table 4-2 with the correct caption — the acceptance criterion ("all refs point to Table 4-2") is *not* met. |
| L5-D1 | MODERATE | PDF p.79 (Ch 4 §4.4, printed 61) | class D — contradiction | **§4.4 restates "the six dimensions" incorrectly.** §4.1 (PDF p.60) defines Quality / Traffic / Token profile / Latency / Economic constraints / Operational constraints; Ch 3 (PDF p.57) repeats that list correctly. §4.4 then says "For the six dimensions (workload type, token mix, concurrency, latency, memory, economics)" — it substitutes *memory* (not a dimension) for *Operational constraints* and *workload type* for *Quality*. Two different six-dimension lists, 22 pages apart, in the chapter whose job is to teach the framework. |
| L5-D2 | MODERATE | PDF p.74 (printed 56), p.83 (printed 65) vs p.63/p.75 (printed 45/57) | class D — contradictory repetition (Loop-4 M-4, half-fixed) | **19,800 tok/s carries two incompatible labels inside one chapter.** p.63 and p.75: "a planning rate, not a ceiling: the peak-derived ceiling is ~56.5K tok/s" (the fix that landed). But p.74 still says "below the host's ~19,800 tok/s **ideal**" and p.83 still says "the host's **idealized** aggregate prefill rate … an **analytical upper bound**, not a measured goodput" — and adds "before TP/system loss", which asserts the opposite direction from the ceiling rule. The negation vocabulary landed; the two surviving "ideal/upper bound" call-sites were not swept. |
| L5-D3 | MODERATE | PDF p.98 (Ch 6 fig 6.1, printed 80) | class D — figure vs prose (Loop-1 → Loop-4 M-1, unfixed) | **fig 6.1 blurs layer ownership — the exact confusion the chapter exists to prevent.** (a) The Serving card still lists **KV** ("TTFT · TPOT · goodput · KV") while p.79 lists KV cache occupancy under *resource* metrics — carried from Loop 1 and still wrong. (b) The figure's own footer legend reads "causation ↓ (workload → serving) \| diagnosis ↑ (serving → workload)", collapsing the three-layer chain into the direct workload→serving hop that §6.1 explicitly forbids ("never jump from a workload metric straight to a serving metric"); the caption states the chain correctly (workload → resource → serving), so figure and caption disagree. (c) The Workload card reads "tokens/s · context · **response-time**" — response time is a serving quantity, and §6.1's workload list is rps / token profile / concurrency (concurrency is absent). Three chips, three mismatches. |
| L5-C1 | MODERATE | PDF pp.62–71 (Ch 4, printed 44–53) | class C — redundancy (§44, §46, §19) | **The consolidation removed the table-vs-table duplication but left the chapter presenting its canonical numbers three times in eleven consecutive pages, with verbatim caveat repeats.** Objects: Table 4-1 "Six-dimension workload characterization" (pp.62–64), the Canonical Workload box "the one authoritative set of numbers" (pp.64–67), Table 4-2 provenance ledger (pp.68–71). "not a Little's-Law derivation … (walk-through in §4.3)" appears **near-verbatim in three table cells** (p.62 Table 4-1 Traffic row, p.66 box Average-arrival row, p.69 Table 4-2 row) plus the walk-through itself — four statements of one distinction in ten pages. "a different provider tier, not the same line item" appears **three times** (p.63 table cell, p.75 prose bullet, p.76 cost-basis note) plus a fourth short form in the p.78 cost table. §46: one canonical statement + pointers, not three restatements. |
| L5-C2 | MODERATE | PDF pp.63–64 (Table 4-1, printed 45–46) | §26 — density/usability | **The merged table is coherent but its Derivation/Source column is prose in a table.** The Economic row's derivation cell runs ~30 lines (whole-fleet denominator rule + sustained-planning-rate + frontier-tier price note + two pointers); the Traffic and Latency cells run 8–15 lines each. §26: a table should make comparison easier, not compress paragraphs. The six-dimension comparison the table exists to enable is now harder to scan than the compact restatement it replaced. Fix: keep one-line derivation cells, move the rationale to notes beneath the table. |
| L5-D4 | MODERATE | PDF p.66 (box, printed 48) vs p.68 (Table 4-2 caption, printed 50) | class D — authority ambiguity (§29) | **Two adjacent objects both claim to be "the single reference set".** The box self-titles "Canonical Workload — the single reference set … the one authoritative set of numbers every chapter disciplines on"; Table 4-2's caption is "Canonical-scenario provenance (**the single reference set**)" while its own intro says its job is provenance authority ("the authority for which is which"). The caption therefore both duplicates the box's self-title and mislabels its own role. After the consolidation a reader still cannot tell which object is authoritative for the canonical numbers — the residual of Loop-4 M-0. |
| L5-M2 | MODERATE | PDF p.99→p.101; PDF p.57 ×6; p.64; p.65; p.67 | taxonomy form / typography (Loop-4 M-7, unfixed) | **Label atomicity still breaks three ways.** (a) The page-break tear persists: p.99 ends "[canonical" and p.101 (across the fig 6.2 page) begins "scenario][ASSUMPTION]" — the only two bracket-imbalance pages in scope. (b) 7 soft-hyphenated label tokens: `[ASSUMP­TION]` ×6 on PDF p.57 (printed 39) and `[canonical scenario][ASSUMP­TION]` on PDF p.64 (printed 46). (c) Two status brackets now carry 100+ characters of prose inside the brackets — `[ASSUMPTION — planning round; retrieval ~120 ms + prefill ~1.08 s + decode ~7.5 s ≈ 10 s …planning fiction]` (p.65) and `[ASSUMPTION — the same busy-period behavior scaled to the burst/traffic spike; a scenario input, not a measured arrival rate]` (p.67) — so the token is no longer atomic and a reader scanning for `[ASSUMPTION]` finds a bracket that ends two lines later. |
| L5-P1 | MODERATE | PDF pp.16–17 (Preface, printed x–xi) | §50 / §19 — best-form (Loop-1 MODERATE, never tracked in loops 2–4) | **The book's epistemic contract is still one dense wall of prose.** Five provenance values × five status values × pairing rules × the Axis-3 riding rule × the mapping table × two habits are delivered as continuous paragraphs with inline examples; no table, no visual, no worked pair. This is the section every later label depends on, and it is the least scannable page in the front matter. Render the axes as a small 2-column table (axis → values → one example each) and keep the prose for the rules only. |
| L5-N1 | MINOR | PDF pp.9–10 (LoF); Contents p.7; PDF p.13 | front matter (Loop-4 N-1, partial) | Preface figures are numbered **1 and 2** (LoF entries "1 The architect's decision loop…", "2 Reading the book two ways"), colliding with the chapter figure scheme; **Contents has no "List of Figures" entry** (LoF is orphaned) and there is **no List of Tables**; **5 LoF entries still end with a terminal period before the leaders** — 6.1 (in scope), 16.1, 19.3, 22.1, 26.2 (out of scope). The other 34 entries were cleaned. |
| L5-N2 | MINOR | PDF p.14 (Preface fig 2 panel B, printed viii) | figure typography (Loop-2 MAJOR → Loop-4 N-2, residual) | Box 6 still has the question mark **in contact with** the chapter tag: "is it the right call?Ch16/22/25" — zero gap, glyphs touching (vision-verified; the other five boxes have a clear gap). Also panel-B Q4 is "1 host or fleet? — Ch17" while the adjacent checklist says "(Chs. 16–17)"; the other five now match their checklist entries exactly. |
| L5-N3 | MINOR | PDF p.56 (Ch 3 fig 3.1, printed 38) | figure typography (Loop-2/3; Loop-4 recorded this as fixed — it is not) | The right-column title **"MoE (8 experts)" is not centered over its grid** (left title is), and the figure still contains **no "schematic, not to scale" note** — the caption carries it alone (Loop-4 N-12 half-fix). |
| L5-N4 | MINOR | PDF pp.30, 58, 84, 94/95, 106 | §49 — whitespace | Chapter endings spill 1–2 lines onto an otherwise empty page: printed p.12 (PDF 30, 160 chars, ends y=102), printed p.40 (PDF 58, 209 chars), printed p.88 (PDF 106, 209 chars) are ~90 % blank; printed p.66 (PDF 84) ends at y=250. Ch 5 ends at y=458 with fig 5.1 alone on the next page (improved from Loop-1's ~75 % blank, still ~40 %). |
| L5-N5 | MINOR | PDF p.30 (Ch 1, printed 12) | vocabulary (Loop-2/Loop-4 N-3) | "high-throughput chat (**decode-bound**)" — the last remaining phase-dominance use of "-bound"; every other site now says decode-dominant / prefill-dominated. |
| L5-N6 | MINOR | 34 spans / 13 pages: PDF 23, 41, 49, 50, 64, 74, 83, 87, 90–94 | typography (Loop-4 N-4) | Body/table/sidenote math still renders at **7.97 pt** (printed pp. 5, 23, 31, 32, 46, 56, 65, 69, 72–76) — the 8 pt floor holds for figure text but not for body math. |
| L5-N7 | MINOR | all 8 tables (PDF 27, 48, 57, 62, 68, 88, 103) | typography (Loop-4 N-5) | **No table header row is styled**: `Dimension`, `Quantity`, `Value`, `Status`, `Metric`, `Phase`, `metric` all render flags=4 (serifed, not bold) at 10.9 pt — headers are distinguished by position only. |
| L5-N8 | MINOR | all captions | §24 — consistency (Loop-4 N-6) | Two caption grammars persist: tables are `Table N-M — Title case`, figures are `figure N.M: lowercase sentence`. |
| L5-N9 | MINOR | PDF p.100 (fig 6.2, printed 82) | taxonomy form (Loop-4 M-8c) | The in-figure annotation "**[ILLUSTRATIVE synthetic profile]**" is a bracketed token that is not an axis value — it reads as a label pair with a missing second bracket. |
| L5-N10 | MINOR | PDF p.93 (Ch 5 §5.7, printed 75) | logic / taxonomy | §5.7's closing sentence says these flags should be "promoted to [1P][DERIVED] or [2°][DERIVED], dropped, or **demoted into the 'What We Still Don't Know' section**" — but the sentence stands *inside* §5.7 "What We Still Don't Know", so nothing in it can be demoted into it; and the only promotion paths offered are *derived-arithmetic* destinations, none of which is a measurement, for three questions whose resolution **is** measurement (guardrail latency, break-even volume, embedding quality). |
| L5-N11 | MINOR | PDF p.26 (fig 1.2, printed 8) | §25 — visual semantics (Loop-1 MINOR, unrecorded since) | Purple means *stored K/V* in fig 1.1 but *Embedding and KV Cache* in fig 1.2 — the same fill encodes two different concepts across consecutive figures. |
| L5-N12 | MINOR | PDF p.33 (Ch 2 §2.1, printed 15) | §24 — arrow convention (Loop-1 MODERATE, downgraded) | The arrow-convention paragraph still concedes one glyph = five meanings (into / out of / read / write / loop); the fig 2.1 caption rule ("every arrow is labeled at the point it enters the figure") mitigates but does not remove the ambiguity. |

---

## 2. Tally

| Severity | Count | IDs |
|---|---|---|
| CRITICAL | 0 | — |
| MAJOR | 1 | L5-M1 |
| MODERATE | 8 | L5-D1, L5-D2, L5-D3, L5-C1, L5-C2, L5-D4, L5-M2, L5-P1 |
| MINOR | 12 | L5-N1 … L5-N12 |
| **Total** | **21** | |

**By section**

| Section | MAJ | MOD | MIN | Verdict |
|---|---|---|---|---|
| Front matter (pp. 1–18) | 1 | 1 | 1 | Preface content is strong; the evidence-discipline page and the LoF/numbering apparatus still need work. |
| Ch 1 (pp. 19–30) | 0 | 0 | 4 | Content excellent (§1.1.4 attention precision is a highlight); only typography/figure-semantics minors. |
| Ch 2 (pp. 31–45) | 0 | 0 | 1 | **Excellent — say so once and move on.** §2.3–2.5 walk-through, fig 2.1 (vision-verified: arrowheads, junction dots, band labels all correct) and fig 2.2 are the best-taught material in scope; one figure-typography minor. |
| Ch 3 (pp. 46–59) | 0 | 1 | 2 | §3.6.1 passes the transfer test; label soft-hyphens and fig 3.1 residuals only. |
| Ch 4 (pp. 60–84) | 0 | 5 | 3 | The consolidation landed structurally but created the loop's densest cluster: contradiction, redundancy, density and authority findings all sit in the canonical-number complex. |
| Ch 5 (pp. 85–95) | 0 | 0 | 3 | §5.3's fixes all landed (50 tok/s relabeled with a full unit note; 14B/47B relabeled; paradigms de-markdowned; Q∗ uses `=`); one stale ref, one logic slip, whitespace. |
| Ch 6 (pp. 96–107) | 0 | 1 | 2 | §6.3.3 and the mini-case are excellent; Table 6-1 now fits one page; fig 6.1 is the one real defect. |

---

## 3. Loop-4 fix verification (the seven named fixes)

| Loop-4 fix | Status | Evidence |
|---|---|---|
| Tables 4-1/4-2 consolidated | **Landed, with residue** | One six-dimension table remains (Table 4-1, PDF 62–64); the duplicate compact restatement is gone. Residue: prose-dense cells (L5-C2), three-object authority overlap (L5-C1, L5-D4). |
| Table 4-2 numbering clean? | **No** | 54 refs now point to Table 4-2 with the correct caption, but **6 stale `Table 4-3` refs remain** (3 in scope) and Table 4-1 has zero inbound refs → L5-M1. |
| Merged table coherent? | **Structurally yes, typographically no** | Columns Dimension / Characteristic / Derivation / Source are consistent across pp.62–64 with repeated headers; the Economic derivation cell is ~30 lines of prose (L5-C2). |
| `[1P][FACT]` vendor cards | **Landed** | PDF pp.63, 74, 69, 76, 86 — all five hardware/price call-outs carry `[1P][FACT]` with a named source. |
| sustained-planning-rate vs ceiling | **Landed, one contradiction left** | Defined once (p.63), used consistently (pp.75, 83), ceiling distinguished ("not a ceiling: ~56.5K"); but p.74/p.83 still say "ideal"/"analytical upper bound" → L5-D2. |
| Reservoir analogy | **Landed** | Consistent across pp.34, 41, 44, 47, 50, 54, 66, 70, 72, 74, 76, 78, 84, 94; no garden-hose/fire-hose variants; no contradiction with the roofline. |
| Vocab negation | **Landed** | "not a ceiling" (p.75), "not a Little's-Law derivation" ×4, "not a market fact", "not a measured arrival rate" — all present and correctly scoped. |
| `[S4]` definition | **Landed** | First use at PDF p.103 (printed 85) carries `[S4][1P][FACT] (source keys: …)`; §6.6 and §6.7 use S1–S6 consistently. |
| Ch 4 Table 4-3 → 4-2 renumber | **Partial** | 54 updated, 6 stale → L5-M1. |

---

## 4. Classes verified clean (checked, no finding)

- **Arithmetic:** 73 independent re-derivations across printed pp. 44–88 — 0 mismatches (Little's-Law walk-through, 19,800/56.5K ceilings, 8.6 s/1.2 s/25 ms, 9,200/300 tokens, $0.01164, 3.31 M/107,914/3.564 M tok/s/$, 24.1/83.9/335.5 GB KV, 2.62 MB/token, 989 TFLOPS/3.35 TB/s/1.4e11, roofline 295, intensity 9,200, 25/36/23 hosts, 20/29/30 hosts, $73K/$292K, 0.84 vs 0.85, 9,000 vs 3.3 M tok/$-hr, 12,960 chunks, 3.42 M combined).
- **Placeholders:** 0 (`TBD|FIXME|XXX|TK|PLACEHOLDER|lorem`).
- **Stray asterisks / markdown leaks:** 0 (the single `|` on PDF p.98 is fig 6.1's footer separator, not markup).
- **Tofu / replacement characters:** 0 in scope.
- **Double spaces in body text:** 0.
- **Second-person "you":** 1 (printed p.5, license page — permitted).
- **Bare `§N` cross-refs:** 0; every `§N.M` in scope resolves to a real section.
- **Figure cross-refs:** every `Fig N.M` in scope resolves; figure-before-text ordering holds throughout.
- **Table cross-refs:** all resolve **except** `Table 4-3` (L5-M1).
- **Navigation accuracy:** Contents page numbers for all 6 chapters, LoF numbers for all 9 in-range figures + 2 preface figures — 0 mismatches against actual pages.
- **Orphaned table captions:** 0 (no caption in the last 3 lines of any page).
- **Multi-page table continuation:** Table 4-1 (pp.44–46) and Table 4-2 (pp.51–53) repeat their header rows on every continuation page.
- **Table 6-1 single page:** both rows + the verdict note now sit on printed p.85 (Loop-4 N-9 fixed).
- **Text-frame overflow:** max x1 = 528.3 (justified body, R = 525.6) and 531.2 (sidenote) — no out-of-frame text.
- **Sub-8 pt figure text:** floor is 8.0 pt (body math is L5-N6).
- **Stranded headings:** 0.
- **Premature acronyms:** MFU, TPOT, goodput, LoRA, ADR, SLA, QPS, TTFT all defined before first use.
- **Mini-case thread:** 6/6 chapters, each with inputs → arithmetic → decision → transfer pointer.
- **Cross-chapter number continuity:** 20/20 spot checks agree (20 hosts, 29/30, $15K, 19,800, 56.5K, 8.6 s, 1.2 s, 25 ms, 9,200, 300, 99.9 %, 8×H100, 140 GB, 2.62 MB, 70B, 80 layers, 1.4e11, 989 TFLOPS, 3.35 TB/s, 640 GB).
- **Taxonomy pair syntax (vocabulary):** every inline pair uses declared tokens (`canonical scenario`/`ASSUMP­TION`/`DERIVED`/`FACT`, `ILLUSTRATIVE`/`DERIVED`, `1P`/`FACT`/`DERIVED`, `2°`/`DERIVED`, `LAB`/`FACT`, `S1`–`S6`) — no undeclared tokens; the residuals are *form* (soft hyphen, long gloss), captured in L5-M2.
- **`[UNRESOLVED]`:** single marker, 8 uses, all in §4.7/§5.7/§6.7.
- **Bracket balance:** 105/107 pages balanced (the 2 failures are L5-M2a).
- **Figure pages vision-inspected and clean:** fig 1.1 (no border collisions), fig 1.2 ("append K,V" clears all borders; KV subtitle unclipped), fig 2.1 (arrowheads + junction dots + consistent band labels), fig 2.2 (no overlaps, ridge shown, grayscale-safe), fig 3.1 (no overlaps), fig 4.1 (no arrow/label collisions), fig 5.1 (clean), fig 6.2 (no overlaps; mean in legend as captioned), preface fig 1 (distinct dash patterns, outer loop 04→01, grayscale-safe).
- **Previously open, now resolved:** Loop-1's two-service-times MODERATE (the chapter now names both, pins 8.6 s for sizing and labels 10 s a planning fiction); Loop-1's "Start here" and reader-address items; Loop-2's 9,000 tokens/$-hr MAJOR (now `[ILLUSTRATIVE][DERIVED]` with a full unit note citing Ch 15's range); Loop-2's 14B/47B MAJOR (now `[ILLUSTRATIVE][DERIVED]`); Loop-2's continuous-batching/prefix-caching MAJOR (explicitly disentangled in §4.6); Loop-3's fig 2.1 arrowheads/junction dots; Loop-4's Table 6-1 split, markdown leak in §5.3.3, `∝`→`=`, "inculcates", "architects … they", 400-user scaling label, "population in flight" wording, `[canonical scenario]` bare singleton on p.73, magnitude spacing, magnitude-space artifacts, `[LAB]`/`[UNRESOLVED]`/asterisk/placeholder scans.

---

## 5. Convergence risk notes

1. **Loop-4 recorded several fixes that this build does not show**: fig 6.1's KV card (L5-D3), the label page-tear (L5-M2a), fig 3.1's title centering (L5-N3), fig 2 box 6's gap (L5-N2), the LoF periods (L5-N1), and the "ideal/upper bound" sweep (L5-D2). Treat Loop-4's convergence list as unverified for those six.
2. **The renumber is the one MAJOR and it is mechanical** — six find-and-replace sites, three of them in scope, one of them on the page that defines the book's provenance system. It should be closed before any further content work.
3. **Ch 4's canonical-number complex is now the least-optimal passage in scope** (§50): eleven consecutive pages, three authority objects, one caveat stated three times in table cells. The literal duplication is gone; the underlying "which object is authoritative?" question is not.
4. **No CRITICAL and only one MAJOR** — the manuscript is close. The remaining work is (a) one cross-ref sweep, (b) one contradiction sweep for "ideal/upper bound", (c) one figure rebuild (6.1), (d) a Ch 4 compression pass, (e) a typography batch (headers, 7.97 pt math, caption grammar, soft hyphens, chapter-end widows).