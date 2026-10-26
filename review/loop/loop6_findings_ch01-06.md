# Loop 6 — Confirmation pass: Front matter + Chapters 1–6

**Artifact:** `render/build/from-token-to-fleet-v20260913.pdf` (361 pp; scope = PDF pp. 1–106 = front matter + Ch 1–6; Ch 7 opens PDF p.107).
**Standard:** `review/complete-manuscript-review-prompt.md` (read in full). **Baselines:** `loop4_findings_ch01-06.md`, `loop5_findings_ch01-06.md` (both read in full).
**Method:** full text extraction of all 107 in-scope pages and complete read; targeted verification of every named Loop-4/5 fix; PyMuPDF audits (label-pair census, bracket balance per page, cross-ref resolution, font-size census, span/frame geometry, table-rule geometry, caption/continuation checks, navigation check); 21 fresh independent arithmetic re-derivations; vision inspection of all 10 in-scope figure pages plus two 300-dpi zoom crops (fig 2.1 middle strip, fig 6.2 top).
**Page convention:** "p.N" = PDF page; printed = PDF − 18 for Ch 1–6; front matter cited by PDF page + roman.
**Read-only:** no manuscript, render source, or build artifact was modified.

---

## 1. Named-fix verification (the ten Loop-4/5 fixes this pass was asked to confirm)

| # | Fix | Status | Evidence in this build |
|---|---|---|---|
| 1 | Six-dimensions list corrected (L5-D1) | **LANDED** | §4.4 (p.78) now reads "For the six dimensions (quality, traffic, token profile, latency, economic constraints, operational constraints)" — identical to §4.1 (p.59) and the Ch 3 forward-pointer (p.57). The rogue "workload type / memory" list is gone; all three in-range lists agree. |
| 2 | ideal → planning-rate (L5-D2 / Loop-4 M-4) | **LANDED** | 0 hits book-scope for "idealized prefill upper bound" and "analytical upper bound". All four 19,800 call-sites (pp.63, 73, 74, 82) now say "sustained-planning prefill rate … a planning rate, not a ceiling: the peak-derived ceiling is ~56.5K tok/s". The one surviving "ideal" (p.100) is a different, correctly scoped claim ("batch-1-equivalent idealized weight-streaming read … not a measured bytes-physically-read figure"). |
| 3 | Single-authority box (L5-D4) | **LANDED** (one residual wording, R-16) | "single reference set" occurs once, in the Canonical Workload box (p.63); Table 4-2's caption is now "Canonical-scenario provenance ledger (which value is assumed, derived, or factual) … This is the authority for which is which" — roles separated. Residual: Ch 1 p.27 still calls Table 4-2 "the one set of numbers every chapter cites" (R-16). |
| 4 | Table 4-1 inbound refs (L5-M1) | **LANDED** | 4 occurrences book-wide = caption + 3 inbound refs: p.59 ("Table 4-1 applies the framework"), p.61 intro ("Table 4-1 states the six-dimension characterization"), p.63 ("Derivation notes for Table 4-1"). |
| 5 | Little's-Law caveat 4 → 1 (L5-C1) | **LANDED** | Full caveat statement appears once, in the §4.3 walk-through (p.70: "a declared traffic assumption, NOT a Little's-law derivation from the active-user population: Little's Law, L = λW …"). Three short pointers replace the old restatements: "declared, not derived … (walk-through in §4.3)" (pp.61, 64) and "declared scenario inputs; the full walk-through is §4.3" (p.63). Provider-tier price note likewise reduced to one full + one short form (pp.63, 74). |
| 6 | [ASSUMPTION] atomic (L5-M2) | **PARTIAL — 2 of 3 sub-fixes landed** | (a) Soft-hyphenated label tokens: **0** (was 7). (b) 100+-char glosses inside brackets: **0** (was 2 — both now sit outside the bracket after an em dash). (c) Page-break tear: **still present** — p.98 ends "… never the mean. **[canonical**" and p.100 opens "**scenario][ASSUMPTION]** author-chosen SLO budget…" across the fig 6.2 page; these are the only 2 bracket-imbalance pages in scope (105/107 balanced). → R-1. |
| 7 | Table 4-3 renumber, 0 remain (L5-M1) | **LANDED** | `Table 4-3`: **0 hits book-wide**. Table 4-2: 61 refs, all resolving to the correct caption; Table 4-1: 4 (see #4). |
| 8 | Reservoir analogy (Loop-4 M-6) | **LANDED** | p.37: one reservoir in both regimes — prefill = fire hose "drawing one enormous burst of water out of a reservoir … limited entirely by the raw horsepower of the pump"; decode = "that same 140,000-liter reservoir (140 GB) … through a standard garden hose … the diameter of the hose (HBM bandwidth)". The token is the measured outflow on both sides ("the burst delivers the first glass of water, the first token" / "just to deliver one glass of water — one generated token"), and both carry the operating-point qualification. One picture across the regime flip. |
| 9 | Vocab negation (Loop-4 M-5) | **LANDED** | All six "what it is not" cells now begin with "not": "not an optimization over a shared prefix", "not a way to reduce the amount of KV state", "not the same as caching the KV of a single request's own decode", "not a separate mechanism from prefix caching in this book's usage", "not reducing the number of key/value entries", "not shrinking the state itself". |
| 10 | [S4] definition (Loop-4 M-2) | **LANDED** | First in-range S-key use (p.101) carries "[S4][1P][FACT] (source keys: each [S#] names one entry in the References chapter, where [S3]–[S7] resolve; Ch 11 lists [S1]–[S6] inline.)". No S-key occurs anywhere in range before that point, so no reader meets an undefined key; §6.6/§6.7 use S3/S4/S5/S7 consistently. |

**Score: 9 of 10 fully landed; 1 partial (label atomicity — the page tear sub-item only).**

---

## 2. Loop-5 findings re-verification (their 21 rows)

| Loop-5 ID | Status now | Note |
|---|---|---|
| L5-M1 (stale Table 4-3 + zero Table 4-1 inbound) | **Fixed** | 0 stale refs book-wide; 3 inbound refs to 4-1. |
| L5-D1 (§4.4 wrong six-dimension list) | **Fixed** | See §1 #1. |
| L5-D2 (ideal/upper-bound contradiction) | **Fixed** | See §1 #2. |
| L5-D3 (fig 6.1 three chips + collapsed legend) | **Fixed** | Vision-verified: Workload = `rps · token profile · concurrency`; Resource = `GPU util · memory · bandwidth · KV cache`; Serving = `TTFT · TPOT · goodput`; legend now reads `causation ↓ (workload → resource → serving) | diagnosis ↑ (serving → resource → workload)`; layout clean. |
| L5-C1 (Ch 4 triple restatement) | **Largely fixed** | Verbatim repeats collapsed to one statement + pointers (§1 #5); three authority objects now role-separated. |
| L5-C2 (prose-dense derivation cells) | **Fixed** | Table 4-1 cells are compact label + 2–5 lines; rationale moved to "Derivation notes for Table 4-1 — the rationale behind the compact cells above" (p.63). |
| L5-D4 (two "single reference set" claims) | **Fixed, 1 residual** | Box only; residual wording at p.27 → R-16. |
| L5-M2 (label atomicity ×3) | **Partial** | (a) tear remains → R-1; (b) soft hyphens fixed; (c) long glosses fixed. |
| L5-P1 (preface epistemic wall) | **Not fixed** | pp.16–17 still continuous prose, no axis table → R-2. |
| L5-N1 (LoF periods / preface numbering / Contents entry / List of Tables) | **Not fixed (all four sub-items)** | 5 LoF entries still end with a period (6.1, 16.1, 19.3, 22.1, 26.2); preface figures still numbered 1/2; Contents still has no "List of Figures" line; still no List of Tables → R-3…R-6. |
| L5-N2 (fig 2 box-6 gap; box-4 tag) | **Half fixed** | Box 6 gap now clear (vision: "an unambiguous space, not contact"). Box 4 still tags `Ch17` while checklist Q4 says "(Chs. 16–17)" → R-7. |
| L5-N3 (fig 3.1 title centering + scale note) | **Half fixed** | "MoE (8 experts)" now centered over its grid (vision); no "schematic, not to scale" note inside the figure → R-8. |
| L5-N4 (chapter-end whitespace) | **Partial** | Old sites at printed 40/66/88 resolved; remaining: pp.30, 83, 105 → R-9. |
| L5-N5 ("decode-bound" p.30) | **Fixed at cited site** | p.30 clean; but the preface instance Loop-4 originally flagged (PDF p.12) still reads "high-throughput chat (decode-bound)" → R-10. |
| L5-N6 (7.97 pt body math) | **Not fixed** | 35 spans at 7.97 pt across 13 pages (23, 41, 49, 50, 63, 73, 82, 86, 89–93) → R-11. |
| L5-N7 (unstyled table headers) | **Mostly not fixed** | 46 of 50 header-word spans still flags=4 (serif, not bold); 4 bold exceptions on pp.86, 96 → R-12. |
| L5-N8 (two caption grammars) | **Not fixed** | Tables `Table N-M — Title case`; figures `figure N.M: lowercase sentence` → R-13. |
| L5-N9 (fig 6.2 bracketed non-axis token) | **Not fixed** | "[ILLUSTRATIVE synthetic profile]" still the chart's second title line → R-14. |
| L5-N10 (§5.7 self-demote logic) | **Fixed** | p.92 now: "resolved by measurement into [1P][FACT] or [2°][FACT], promoted to [1P][DERIVED] or [2°][DERIVED] where the resolution is arithmetic, or dropped" — measurement destinations added, self-demote clause removed. |
| L5-N11 (purple = two concepts) | **Not fixed** | fig 1.1 purple = stored K/V; fig 1.2 purple = Embedding + KV Cache (both vision-verified) → R-15. |
| L5-N12 (arrow-convention concession) | **Fixed** | p.37 now enumerates all five arrow types with figure references (data-flow Fig 2.1/11.3, dependency, influence Fig 4.1, causation Fig 6.1, association App. A.4) plus "Where a figure's arrows are ambiguous, the caption states the intended reading." |

Also re-verified from Loop 4 (not on Loop-5's list, now confirmed fixed): M-3 evidence labels (p.21 both now `[1P][FACT]` with named sources); M-8a/b (bare `[canonical scenario]` on p.73 gone; unbracketed `(ILLUSTRATIVE — …)` form 0 in range); N-10 (400-user row now derived + labelled); N-11 (0.4B now shows 100,000 × 4,096 ≈ 409.6M); N-13 (bracketed prose sentences 0); N-8 (fig 1.2 caveat trimmed to one clause at p.27).

---

## 3. Findings

### 3a. Remaining issues (carried; real, specific, still in this build)

| ID | Sev | Location | Finding |
|---|---|---|---|
| R-1 | MODERATE | p.98 foot → p.100 head (across fig 6.2) | **Label page-tear persists** (Loop-4 M-7 / L5-M2a): sentence ends "… never the mean. **[canonical**" and resumes "**scenario][ASSUMPTION]** author-chosen SLO budget…" two pages later. Only bracket-imbalance pages in scope (p.98 = 2/1, p.100 = 5/6). A provenance label must be atomic; the reader hunting it at the page foot finds a dangling bracket. Fix: `\mbox`/no-break the pair and keep the §6.3.1 sentence clear of the fig 6.2 float. This is the one named fix that did not fully land. |
| R-2 | MODERATE | pp.16–17 (Preface, printed x–xi) | **Evidence-discipline section is still a two-page wall of prose** (L5-P1): five provenance values × five status values × pairing rules × Axis-3 rule × mapping delivered as continuous paragraphs; no table, no worked pair. It is the section every later label depends on and the least scannable page in the front matter. Editorial, not correctness. |
| R-3 | MINOR | p.9 (LoF) | 5 entries still end with a terminal period before the leaders: 6.1 (in scope), 16.1, 19.3, 22.1, 26.2; the other 35 are clean (L5-N1). |
| R-4 | MINOR | pp.9–10 | Preface figures numbered "1" and "2" in the LoF, colliding with the chapter figure scheme (L5-N1). |
| R-5 | MINOR | p.7 | Contents has no "List of Figures" line — the LoF is orphaned (L5-N1). |
| R-6 | MINOR | front matter | No List of Tables anywhere despite 20+ numbered tables (L5-N1). |
| R-7 | MINOR | p.14 vs p.15 | fig 2 panel-B box 4 tags `Ch17`; the adjacent checklist Q4 says "(Chs. 16–17)". The other five boxes match their checklist entries exactly (L5-N2 residual). |
| R-8 | MINOR | p.56 (fig 3.1) | No "schematic, not to scale" note inside the figure, where equal-sized squares stand for 140 GB vs ~94 GB vs 28 GB; the caption carries it alone (Loop-4 N-12 / L5-N3 half). Centering is now fixed. |
| R-9 | MINOR | pp.30, 83, 105 | Chapter-end whitespace: Ch 1 ends at 160 chars / 13 % fill; Ch 4 at 1,226 chars / 36 %; Ch 6 at 209 chars / 13 % (L5-N4 class). |
| R-10 | MINOR | p.12 (Preface, printed vi) | "high-throughput chat (**decode-bound**)" — phase-dominance use of "-bound" in the workload-class list; every other site now says decode-dominant/prefill-dominated (Loop-4 N-3's original site; Loop-5 fixed only the p.30 instance). |
| R-11 | MINOR | 13 pages (23, 41, 49, 50, 63, 73, 82, 86, 89–93) | 35 body/table/sidenote spans render at 7.97 pt — 0.03 pt under the declared 8 pt floor (L5-N6). Print impact negligible; the defect is that the floor claim is not true of the body. |
| R-12 | MINOR | all in-scope tables | 46 of 50 header-word spans unstyled (flags=4, same face as data); only pp.86/96 headers are bold (L5-N7). |
| R-13 | MINOR | all captions | Two caption grammars persist: `Table N-M — Title case` vs `figure N.M: lowercase sentence` (L5-N8). |
| R-14 | MINOR | p.99 (fig 6.2) | In-figure "[ILLUSTRATIVE synthetic profile]" is a bracketed token that is not an axis value — reads as a label pair with a missing second bracket (L5-N9 / Loop-4 M-8c). |
| R-15 | MINOR | pp.25–26 | Purple encodes stored K/V in fig 1.1 but "Embedding and KV Cache" in fig 1.2 — same fill, two concepts across consecutive figures (L5-N11). |
| R-16 | MINOR | p.27 (Ch 1 §1.3) | "The canonical scenario (Ch 4, **Table 4-2 — the one set of numbers every chapter cites**)" competes with the box's "it comes from here and nowhere else" (p.63). Values are identical, but after the single-authority fix two objects still carry "the one" language for the canonical numbers. Fix: point p.27 at the box (or say "Table 4-2 records provenance for the box's numbers"). |
| R-17 | MINOR (latent) | p.16 | `ILLUSTRATIVE` remains a value on both axis 1 and axis 3, so a bare token is ambiguous by construction (Loop-4 N-14). No ambiguous standalone use occurs in range — latent only. |

### 3b. New findings this pass (3 — none substantive/conceptual)

| ID | Sev | Location | Finding |
|---|---|---|---|
| L6-N1 | MINOR | p.57 (Table 3-3, derivation column) | **Bracketed provenance labels overhang the table's right rule and the text frame.** Span geometry: labels start at x0=417.4 and end at x1=547.5 (`[ILLUSTRATIVE][DERIVED]` ×3) and **571.1** (`[ILLUSTRATIVE][ASSUMPTION]`), while the table rules and every other table page stop at 525.6/528.3. Vision-confirmed at 150 dpi: the closing `]` of rows 1/3/8 visibly projects past the rules into the right margin (not clipped; ~41 pt of paper remains). Cause: the no-space pair is unbreakable, so it cannot wrap in a ~108 pt column. Loop-5's frame audit recorded max x1 = 531.2, so this is either newly introduced or newly exposed by the fix pass. Fix: allow a break between the two brackets, or widen/shorten the column. |
| L6-N2 | MINOR | p.33 (fig 2.1) | **First-column left edges of the two parallel bands do not align.** Geometry: PREFILL's `prompt` box x0=124.4 vs DECODE's `previous token` box x0=94.4 — a 30 pt inset difference — while both band containers start at 94.4 and columns 2–5 align exactly (179.4/272.0/345.1/~442). The boxes are right-anchored at x1=168.5 so the inter-box arrows align; the trade-off is a visible left-edge stagger in the book's central pipeline figure (vision-confirmed twice, full page + 300-dpi crop). Not flagged in Loops 4–5. Fix: equalize the col-1 box widths so both left edges sit at 94.4. |
| L6-N3 | MINOR (borderline) | p.33 (fig 2.1 middle strip) | **Junction dots sit where the green `initialize` line crosses the `read`/`append` verticals, but the lines only cross — they share no endpoint** (300-dpi zoom: the green line continues on both sides of each dot; `read` runs cache→transformer through it). Under the standard dot = connection convention the dots assert a false link between the initialize path and the cache I/O. **Caveat: Loop-4 recorded these dots as the fix for Loop-3's crossing finding and Loop-5 accepted them** — so this may be an intentional "mark the crossing" device; confirm intent, and if kept, state the convention in the caption. Counted as new but flagged as possibly re-litigating; drop it if the author confirms the convention is deliberate. |

---

## 4. Tally

| Severity | New this pass | Remaining carried (Loop 4/5, still open) |
|---|---|---|
| CRITICAL | 0 | 0 |
| MAJOR | 0 | 0 |
| MODERATE | 0 | 2 (R-1, R-2) |
| MINOR | 3 (L6-N1…N3) | 14 (R-3…R-16) + 1 latent (R-17) |
| **Total** | **3** | **17** |

**New findings: 3, all MINOR, none conceptual, arithmetic, or correctness defects** — far below the >8 substantive threshold; no loud signal. Two of the three are geometry-proven layout nits in figures; the third is a confirm-intent borderline. Content-level new findings: **0**.

---

## 5. Classes verified clean (checked this pass, no finding)

- **Arithmetic:** 21 fresh independent re-derivations, 0 mismatches — 436/24.9=17.5; 17.5/8.6=2.03; 460,000/19,800=23.2; 9,200/1.08=8.5K; 989 TFLOPS×0.35÷1.4e11=2,471; 8×2,471=19,768≈19,800; 140 GB/0.025 s=5.6 TB/s; 19,800×3,600/$20=3.56M; 50×8.6=430; 10×8.6=86; 40×8.6=344; 2,000/200=10 rps; 0.99×0.8+0.01×5.0=0.842; 1,200+8,000=9,200; 9,200+300=9,500; 70B×2=140 GB; 47B×2=94; 14B×2=28; 9,500×2.62 MB=24.9 GB; 32K→83.8 GB; 128K→335.4 GB. Consistent with Loops 4–5's larger samples.
- **Cross-reference resolution:** every `figure N.M`, `Table N-M`, `§N.N` in scope resolves; `Table 4-3` = 0 book-wide; no bare `§N`.
- **Navigation accuracy:** Contents page numbers 6/6 correct against actual chapter openings (2, 13, 28, 41, 66, 77); LoF page numbers 9/9 correct for in-range figures (7, 8, 15, 22, 38, 62, 76, 79, 81); part dividers correct (printed 1, 40, 88).
- **Taxonomy pair syntax:** census of adjacent pairs — all declared (`canonical scenario`×ASSUMPTION/DERIVED, `1P`×FACT/DERIVED, `ILLUSTRATIVE`×ASSUMPTION/DERIVED, `2°`×FACT/DERIVED, `S#`×1P triples); 0 undeclared tokens; 0 bare singletons on claims (all 7 bare `[canonical scenario]` uses are preface/table-note definitional prose); 0 bracketed prose sentences; 0 unbracketed ILLUSTRATIVE forms.
- **Label atomicity (except R-1):** 0 soft hyphens inside labels; 0 long glosses inside brackets; bracket balance 105/107 (the 2 failures are R-1).
- **`[UNRESOLVED]`:** single marker, 8 uses; 0 "(to be verified)" variants.
- **Hygiene:** placeholders 0; markdown residue 0; double spaces 0; tofu 0; second-person "you" 1 (p.5 license, permitted); stray asterisks 0.
- **Frame/geometry:** 0 out-of-frame body spans except the cover and L6-N1 (p.57); 0 stranded headings; all table continuation pages repeat headers (pp.62, 63, 68, 69); Table 6-1 fits one page (p.102); no orphaned captions (fig 6.2's caption is the page's last line with the figure above it — correct).
- **Figures vision-inspected and clean:** preface fig 1 (loops distinguishable by color/label/dash, outer 04→01, grayscale-safe), preface fig 2 (box-6 gap fixed; only R-7), fig 1.1 (K/V drawn separately, no border collisions), fig 1.2 (no overlaps; only R-15), fig 2.1 (arrowheads + band labels correct; only L6-N2/N3), fig 3.1 (centering fixed; only R-8), fig 4.1 (clean, unambiguous reading order), fig 5.1 (clean), fig 6.1 (**fully rebuilt and correct** — three chips, three-layer legend, clean layout), fig 6.2 (top row dense but cleanly separated — the earlier full-page impression of a p50/frame overlap was disproved at 300 dpi; only R-14).
- **Cross-chapter continuity spot checks:** 70B FP16/140 GB, 8×H100, 9.2K in/300 out, 8.6 s/10 s distinction, 19,800/56.5K, 24.1/83.9/335.5 GB, 2.62 MB/token, 10/40 rps, 86/344 occupancy, 25/36/23 hosts, $73K–$292K — all agree across pp.20–106.

**Genuinely strong (no action):** Ch 2's vocabulary table + reservoir analogy are now exemplary; fig 6.1's rebuild exactly matches the chapter's three-layer taxonomy; Ch 4's walk-through and cost-basis material remain the book's best-taught reasoning; §5.7's logic fix is precise; the single-authority split (box = numbers, Table 4-2 = provenance) is the right design.

**Not verifiable in this pass (not counted):** 2026 model/hardware claims and the targets behind `[S3]`–`[S7]` (out of range); availability-topology pricing (still declared UNPRICED/NOT VALIDATED with matching caveats).

---

## 6. Convergence verdict

**NOT YET CONVERGED under the strict 0–2-actionable rule — but the blockers are mechanical, not intellectual.**

- **Content and correctness: CONVERGED.** 9 of 10 named fixes fully landed (10th partial on a single sub-item); 0 CRITICAL, 0 MAJOR in range; 0 new content-level findings; all Loop-5 contradictions (six-dimension list, ideal-vs-planning-rate, fig 6.1 layer ownership, Table 4-3 renumber, authority overlap) verified fixed; arithmetic, cross-refs, navigation, and label vocabulary all clean.
- **What blocks a clean CONVERGED verdict (20 items, all small):**
  1. **1 mechanical MODERATE** — the label page-tear (R-1), a single `\mbox` + float-clearing fix. This is also the one named fix that did not land; it should be closed first.
  2. **1 editorial MODERATE** — render the Preface evidence-discipline axes as a table (R-2); presentation, not correctness.
  3. **17 MINOR + 3 new MINOR** — one find-and-fix/typography batch: LoF periods ×5, preface figure renumber, Contents LoF line, List of Tables, box-4 tag, fig 3.1 in-figure scale note, 3 chapter-end widows, one "decode-bound", 7.97 pt spans, table header styling, caption grammar, fig 6.2 token, purple semantics, p.27 authority wording, Table 3-3 label overhang, fig 2.1 col-1 alignment (+ confirm-intent on the junction dots).
- **Recommendation:** one mechanical fix pass over the list above (all sites named with page numbers), then re-verify R-1 and L6-N1/N2 by geometry — after that this range should pass with 0 actionable items. No further content, reasoning, or figure-redesign work is indicated for front matter + Ch 1–6.

*Loop 6, read-only confirmation pass. No manuscript, render source, or build artifact was modified.*