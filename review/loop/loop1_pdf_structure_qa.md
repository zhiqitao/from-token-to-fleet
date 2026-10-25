# PDF STRUCTURAL QA — method step 4 (programmatic)

Script: `review/publication_qa/calculations/pdf_structure_qa.py`
Build: `render/build/from-token-to-fleet-v20260913.pdf` (356 pages)

| Check | Result |
|---|---|
| Pages | 356 |
| Page size uniformity | 612×792 pt (US Letter) — uniform |
| Internal links | 322, **0 invalid targets** |
| Bookmarks/TOC | 38 entries, **0 out-of-range page refs** |
| PDF metadata SHA | **none** (correct — final-file SHA-256 lives in the external `release_manifest.json`, per P1-06) |
| Metadata creator/producer | LaTeX+hyperref / luahbtex-1.22.0 |
| Accessibility / page labels | present (tagged) |
| Vector-figure on-page font floor | all vector figures **>= 8.0pt** (Structure QA lists every figure page; the raster ones show body-baseline 9.96pt because their text is baked into the image, not the text layer) |

## Interpretation
- The structural/approval surface is clean: links resolve, TOC in-range, no self-referential
  hash in metadata (reproducibility claim now matches the external manifest).
- Vector figures all >= 8pt; raster figures verified separately (all >= 300 ppi, and the
  11 flagged raster figures were fixed & vision-verified earlier this run).
- Raster figures whose on-page-min shows the 9.96 body baseline (Figs 1.1, 1.2, 2.2, 3.1,
  4.1, 6.1, 7.1, 7.2, 7.3, 8.1, 8.2, 9.1, 11.1, 11.2, 11.3, 18.1, 19.2, 19.3, 20.1, 23.1,
  25.1) are the image-embedded ones; their text is not in the text layer, so font floor is
  judged from the generator's authored size × placement scale, already covered by the
  46-figure vision pass.

## Open question
- The four Loop 1 render-reviewers (ch1-6, ch7-12, ch13-18, ch19-27+backmatter) are still
  running the method's item 1 (contact-sheet / per-page rendered visual pass) and item 2
  (figure re-inspection). Their findings land in `review/loop/loop1_findings_ch*.md`.
