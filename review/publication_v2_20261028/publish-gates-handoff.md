# Publication Gates — Author Handoff Workbook

Repo: /home/ubuntu/hermes-work/from-token-to-fleet
Release candidate: **R32**
- Interior PDF: `review/publication_v2_20261028/work/accelerated_external_review_proof_r32/render/build/from-token-to-fleet-v20260913.pdf`
- SHA-256 `78cb9c46…`, **429 pp**, US Letter 8.5×11 (612×792pt), tagged, **0 Type3**, all figures ≥8pt.
- EPUB `render/build/from-token-to-fleet-v20260913.epub`; cover wrap (429pp, spine 0.97in) `render/cover/cover_wrap_letter.pdf`; front cover `render/cover/cover_clean_front.pdf`.
- origin/main HEAD `8474fe5b`.

The review-rework loop is converged (5 models + 2 independent reviews, 0 unresolved P0/P1). The items below are **external gates that require the author / a human** and are NOT auto-satisfied by the PDF.

---

## A. Approval gates (each: evidence + owner + acceptance)

| # | Gate | What is required | Evidence | Owner | Acceptance date |
|---|---|---|---|---|---|
| G1 | **LICENSE drafting (P1-01)** | Author + rights counsel: resolve the license grant §1(3) vs prohibition §2(2) tension; decide whether unaltered whole-book PDF redistribution is permitted vs separately-marketed publishing; verify Amazon KDP terms + any exclusivity choice. | Pinned `LICENSE` at the Edition-history SHA; amended operative license + matching PDF copyright page | Author + counsel | |
| G2 | **PDF/UA + accessibility (P1-04)** | Run veraPDF or Adobe preflight for PDF/UA-1; set `pdfuaid:part` in XMP only after it passes. Report conformance tool + version. | veraPDF report (not installed locally); conformance cert | Accessibility/production | |
| G3 | **Font + image rights matrix (P1-04)** | Rights on 148+ embedded fonts (embedded, incl. 2 unsubsetted Helvetica faces) and 57 figures / all artwork / source screenshots; third-party source-content rights. | Rights matrix per asset; licensing proof | Author/rights | |
| G4 | **ISBN + imprint** | Assign ISBN; decide publisher/imprint fields; go under `Zhiqi Tao` byline per the book's SPLX LicenseRef. | ISBN certificate; imprint metadata | Author | |
| G5 | **Stroke/footnote preflight (P1-03)** | Enforce ≥0.75pt on load-bearing graph strokes/axes/connectors/table rules (running-head rule is 0.4pt); confirm footnote reference marks (8pt OK) and that 5.98pt footnote-region numbers are acceptable superscripts. Thicken the headrule or accept. | KDP previewer screenshots; printed-stroke check | Production | |
| G6 | **KDP preview approval** | Test the file in the KDP previewer at the chosen trim (Letter) + interior color mode; check gutter (min inside margin 0.625in for 429pp), binding shadow, margins, color-vs-grayscale legibility. | KDP preview screenshots; chosen standard-vs-premium color | Author | |
| G7 | **Cover wrap + spine (P1-04)** | Finalize the full cover wrap (18.22×11.25in, spine 0.97in for 429pp) with chosen stock/color/trim; confirm spine text fits; the current wrap is the vector front-cover version. | Cover-wrap PDF; spine calculation; KDP cover template | Author | |
| G8 | **PHYSICAL PRINT PROOF (HARD GATE)** | Order the KDP paperback proof; photograph/inspect the proof-page matrix below; check paper stock, interior color mode, figure legibility, table margins, section starts. | Photographed proof-page matrix (see §B); recorded stock/mode | Author | |
| G9 | **Author sign-off** | Formal dated approval of the final master; record edition identifier + source revision manifest. | Signed approval record | Author | |

---

## B. Minimum physical print-proof page matrix (from the 2026-10-31 review)

Inspect these pages (PDF page numbers) in the proof:
- Front matter: 1, 3, 5 (cover/title/copyright)
- Navigation: 7–11, 15–16
- Concepts: 27–28, 51–66
- Graph-heavy: 110, 138, 153, 167, 199, 234, 264, 307–308, 324, 336, 374, 384, 390, 399
- Numerical tables + back matter: 254–265, 395–405, 418–425

Also review all 57 figures at print scale; the most discriminating are 16.1, 22.1, 7.5, 8.2, 9.1, 6.2, A.2 (color-vs-black-ink, gridlines, small annotations).

---

## C. Remaining technical/editorial polish (P2 disorder/optional — may accept with rationale per review)

- **P2-09** figure-page balance (some figures on the upper third of a page) — optional print-economy decision.
- **P3-02** repeat-caveat readability tax; **P3-03** "4–10×" vs model-specific ~14× consistency; **P3-04** add a `TEACHING GEOMETRY — RE-DERIVE FOR REAL MODEL` label on summary numbers (helps prevent misapplication).
- **P3** minor (Table 3-2 done in R32; N10–N19, KB/KiB, heading-skips in ch09/10/15).

These are non-blocking editorial items the review said can be "fix in one editorial sweep." Recommend closing P3-03 and P3-04 before the final master.

---

## D. Verdict

**RELEASE CANDIDATE.** Approval is FALSE until G1–G9 close. The reasoning/arithmetic/figures/provenance withstand 5-model + 2-review scrutiny; only the legal/production gates above (which require a human) remain.

## E. Next executable steps for the author
1. Review the license (G1) with counsel.
2. Select interior color mode (standard vs premium color) + trim (Letter) (G6/G7).
3. Order the physical proof (G8), inspect per §B.
4. Assign ISBN (G4), run veraPDF/PDF-UA (G2), compile rights matrix (G3).
5. Sign off (G9).
