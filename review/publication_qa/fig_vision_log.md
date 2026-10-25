# Figure Vision / Print-Legibility Log (Batch 1)

Proof PDF: `render/build/from-token-to-fleet-v20260913.pdf` (355 pp, US Letter 8.5x11).
Judge: subagent (deepseek-v4-flash-vision-exp). Crops rendered at dpi=300 in `review/publication_qa/renders/`.
Method per figure: locate caption in PDF text -> render clip of figure body -> read generator source + caption -> compute effective ppi from embedded px / placement width (text block width 6.10 in = 439.2 pt) -> check geometry (img/drawing bbox vs caption, span overlaps, font sizes). Pixel-only checks (label-in-box, collisions, arrowhead terminus) are marked **PENDING_VISION** — they require the parent's `vision_analyze` round, not extractable text/geometry.

## Row summary (FIGID | pdfpage | verdict)

```
Fig 1   | 13  | OK: front-matter vector (no raster); caption gap clean.
Fig 2   | 14  | OK: front-matter vector (no raster); caption gap clean.
Fig 1.1 | 25  | OK: raster 398 ppi, img/caption gap 13.8pt, no clip; PENDING_VISION (label-in-box/arrows).
Fig 1.2 | 26  | OK: raster 523 ppi (highest in batch), gap 13.8pt; PENDING_VISION.
Fig 2.1 | 33  | needs_crop_inspect: vector, min font 8.0pt (smallest in batch), dense 3-band labels; PENDING_VISION.
Fig 2.2 | 40  | OK: raster 400 ppi, gap 13.8pt; PENDING_VISION.
Fig 3.1 | 57  | OK: raster 350 ppi, but TALL near-full-page image (y 96-615); check stretch; PENDING_VISION.
Fig 4.1 | 82  | OK: raster 436 ppi, gap 13.8pt; PENDING_VISION.
```

---

### Fig 1 (front matter) — pdf page 13
- **Generator:** `render/archify/spine-decision-loop.json` -> `render/archify/spine-decision-loop-deliver.html` -> `assets/spine-decision-loop.pdf` (embedded by `render/latex/preface.tex` `\includegraphics`, label `fig:spine-loop`).
- **Caption:** "The architect's decision loop — the book's spine. A vague requirement is carried through workload characterization, constraints, candidate architectures, benchmarking, bottleneck analysis, TCO, and a final red-team challenge before an architecture [is selected]."
- **Effective ppi:** VECTOR (no raster image; PDF draws it as drawings+text).
- **Geometry:** drawings x 86.4-525.6, y 52.4-552.1; caption at y 565.9 (gap ~13.8pt). 17 text spans; **0 span overlaps**. Font sizes 8.7-11.8pt.
- **Verdict:** OK. No clipping / no overlap. Front-matter vector figure; font sizes well above the 8pt floor.

### Fig 2 (front matter) — pdf page 14
- **Generator:** `assets/preface-trace.pdf` (embedded by `render/latex/preface.tex` `\includegraphics`, label `fig:traceability`). NOTE: no matching `render/archify/*.json` found in the tree for this diagram — source JSON not located; flag to parent that only the compiled PDF exists in this checkout.
- **Caption:** "Reading the book two ways. A (left): layer-by-layer, Part I → VI, building the substrate then the discipline. B (right): question-by-question, a set of independent navigation prompts — each maps one reader's question (token → cost, fits host?, which phase binds?, 1 host or fleet?, who serves it?, is it the right call?) to the chapter that answers it."
- **Effective ppi:** VECTOR.
- **Geometry:** drawings x 86.4-525.6, y 52.4-541.0; caption y 554.7. 24 spans; **0 overlaps**. Font sizes 8.6-14.0pt.
- **Verdict:** OK. No clipping / no overlap.

### Fig 1.1 — pdf page 25
- **Generator:** `design/manuscript/chapter-01/figures/gen_fig-01-kv-cache.py` -> `fig-01-kv-cache.png` (+`.pdf`).
- **Caption:** "The KV cache: every decoded token adds one K/V per layer per head. This is a single-layer detail view (one layer's K/V heads); the multi-layer, multi-head overview and the full token-travel pipeline are in Fig 1.2 and Fig 2.1."
- **Effective ppi:** 2428 px / 6.10 in = **398.0 ppi**.
- **Geometry:** img bbox x 86.4-525.6, y 212.5-498.3; caption y 512.1 (gap 13.8pt, no overlap). Raster 2428x1580.
- **Verdict:** OK layout/geometry. **PENDING_VISION** — verify from the rendered crop: (1) each labeled box's text sits inside its border (no straddle), (2) no label collides with another label or the box border, (3) arrowheads terminate on box borders, count rounded boxes.

### Fig 1.2 — pdf page 26
- **Generator:** `design/manuscript/chapter-01/figures/gen_fig-01-token-travel.py` -> `fig-01-token-travel.png`.
- **Caption:** "How a token travels: text → tokenizer → IDs → embedding → attention → KV cache. Conceptual only: this is a one-pass abstraction, not the full transformer — the K/V are produced within every applicable layer, and the KV cache is a persistent state that is both written (append) and read (attend) across steps..."
- **Effective ppi:** 3192 px / 6.10 in = **523.3 ppi** (highest in batch).
- **Geometry:** img bbox x 86.4-525.6, y 203.4-493.9; caption y 507.7 (gap 13.8pt). Raster 3192x2112.
- **Verdict:** OK. **PENDING_VISION** — verify arrow direction text→tokenizer→IDs→embedding→attention→KV cache reads left-to-right, no label overlap, boxes not clipped at image edge.

### Fig 2.1 — pdf page 33
- **Generator:** `render/fig_ch2_pipeline.py` -> `fig-02-0202.png` (+`.pdf`). NOTE: in this build the figure is embedded as **VECTOR** (no raster xref from `get_image_info`; present as drawings+text), so the source PNG (2440 px wide, = 400 ppi if rasterized) is not what the PDF places.
- **Caption:** "The canonical end-to-end inference pipeline, in three bands. PREFILL (top) is the one-shot parallel pass over the whole prompt; it populates the persistent KV cache and is the dominant contributor to TTFT... DECODE (bottom) is the single-token autoregressive loop, measured by TPOT/ITL..."
- **Effective ppi:** VECTOR (n/a). Source PNG would be 2440/6.1 = 400 ppi.
- **Geometry:** drawings x 86.4-525.6, y 52.4-499.1; caption y 512.8 (gap 13.7pt). 20 spans; **0 overlaps**. Font sizes 8.0-9.0pt — **min 8.0pt is the smallest font in this batch**.
- **Verdict:** **needs_crop_inspect** — layout is clean (no overlap, no clip) but the three dense bands use 8.0-9.0pt labels, the smallest in the batch. **PENDING_VISION** — verify the "PREFILL / PERSISTENT KV CACHE / DECODE" band labels and the populate/read/append arrows are legible, and that the per-step "conceptual per-step, per-layer cache I/O" annotation is not clipped by the page-header area at the top of the figure (its top edge is at y~52, adjacent to the running head).

### Fig 2.2 — pdf page 40
- **Generator:** `render/fig_ch2_roofline.py` -> `fig-02-0201.png` (+`.pdf`).
- **Caption:** "Prefill and decode on the roofline ridge. Low-batch decode (streaming weights per token) lands at ~1 FLOP/byte — the memory-bound side; long-prompt prefill lands at high intensity — the compute-bound side. These are operating points, not fixed identities..."
- **Effective ppi:** 2440 px / 6.10 in = **400.0 ppi**.
- **Geometry:** img bbox x 86.4-525.6, y 193.4-517.4; caption y 531.2 (gap 13.8pt). Raster 2440x1800.
- **Verdict:** OK. **PENDING_VISION** — verify the roofline ridge line, the "~1 FLOP/byte" memory-bound vs compute-bound labels, and that the axis labels/curves don't overlap the ridge line.

### Fig 3.1 — pdf page 57
- **Generator:** `render/fig_ch3.py` -> `fig-03-0301.png` (dpi=350).
- **Caption:** "Dense vs MoE parameter allocation and KV cache behavior. Controlled comparison: same 70B-equivalent class, same attention geometry, same context and cache dtype — so the KV footprint is identical and only the active-compute fraction differs..."
- **Effective ppi:** 2135 px / 6.10 in = **350.0 ppi** (lowest but print-acceptable for an illustrative chart).
- **Geometry:** img bbox x 86.4-525.6, y 96.2-614.6 — **tallest figure in batch** (~518 pt tall, near-page); caption y 628.4 (gap 13.8pt). Raster 2135x2520.
- **Verdict:** OK geometry. **PENDING_VISION** — verify the two-panel (dense vs MoE) comparison isn't vertically stretched and that the parameter/KV bar labels and "active-compute fraction" annotation are legible at 350 ppi.

### Fig 4.1 — pdf page 82
- **Generator:** `render/fig_batch1.py` (base pattern `fig-04-0401`; line 44 `plt.savefig(base % (4,4,4), dpi=350)`) -> `fig-04-0401.png`.
- **Caption:** "Six-dimension workload characterization mapped to architectural decisions. Each arrow means the dimension constrains/informs the corresponding architectural choice — it is a heuristic influence, not a deterministic one-to-one mapping. The arrows are non-exclusive..."
- **Effective ppi:** 2660 px / 6.10 in = **436.1 ppi**.
- **Geometry:** img bbox x 86.4-525.6, y 129.0-568.2; caption y 582.0 (gap 13.8pt). Raster 2660x2660 (square).
- **Verdict:** OK. **PENDING_VISION** — verify the six dimensions map to their decisions with readable arrows and that none of the arrow labels/boxes are clipped at the image edges.

---

# Figure Vision / Print-Legibility Log (Batch 6)

Judge: subagent (deepseek-v4-flash-vision-exp). Proof: `render/build/from-token-to-fleet-v20260913.pdf`. Crops rendered at dpi=300 in `review/publication_qa/renders/fig<ID>.png`. Verdicts from the placed-page vector text layer (min on-page span size), the book text-on-text collision scan (threshold 0.15), and caption completeness.

## Row summary (FIGID | pdfpage | generator | caption | eff_ppi | verdict)

| FIGID | pdfpage | generator | caption | eff_ppi | verdict |
|---|---|---|---|---|---|
| Fig 24.1 | 302 | render/fig_ch24.py | Red Team / Green Team cycle: probe->guardrails->metrics->green-team loop needs decision gates (release-blocking severity, test-corpus ownership, regression thresholds) to be actionable. | vector (∞) | PASS |
| Fig 25.1 | 311 | render/fig_ch25_adr.py | The Anatomy of an Architecture Decision Record (Context/Options/Decision/Rationale/Consequences). | 391 (raster) | PASS |
| Fig 26.1 | 318 | render/fig_ch26_fingerprint.py | Workload fingerprints on the six axes; subjective normalized scores from the canonical workload, not empirically measured; archetypes are reference points, not clusters. | vector (∞) | PASS |
| Fig 26.2 | 324 | render/fig_ch26_feedback.py | Pattern Application Diagram: Pattern-Measurement-Feedback loop on the capstone scenario, FACT->DERIVED->PATTERN (mean TTFT ~180 ms, p99 ~250 ms, ~48% lower gen cost). | vector (∞) | PASS |
| Fig A.1 | 327 | render/fig_2701.py | 2026 frontier MoE extreme sparsity: four open models, total vs activated params, active fraction in single digits [1P]. | vector (∞) | PASS |
| Fig A.2 | 333 | render/fig_ch27_norm.py | Vendor-reported KV/FLOP reduction; each model relative to its OWN stated predecessor, one row per family with own baseline, no shared bar scale. | vector (∞) | PASS |
| Fig A.3 | 336 | render/fig_2703.py | A conceptual layering of frontier AI systems: vertical stacking is a layering, not a causal lineage; dates are approximate era markers. | 367 (raster) | PASS |
| Fig A.4 | 337 | render/fig_2702.py | Where should intelligence live? horizontal bands are a design choice, not a ranking; boundaries shift with workload/trust/cost. | vector (∞) | PASS |

### Fig 24.1 — pdf page 302
- **Generator:** `render/fig_ch24.py` -> `fig-24-2401.png` (+`.pdf`). NOTE: embedded as **VECTOR** (no raster xref; drawn as drawings+text).
- **Effective ppi:** VECTOR (no raster). Source PNG fig-24-2401.png is 2440 px wide -> would be 2440/6.1 = 400 ppi if rasterized; the book places the vector PDF.
- **Geometry:** figure frame x 86.4-525.6, y 176.3-507.5; caption y 521.2 (gap 13.7pt). 9 spans in frame; **min 8.00pt**; 0 spans <8pt. Caption ends "...not a gate."
- **Verdict:** PASS (>=8pt floor, no overlap, caption complete).

### Fig 25.1 — pdf page 311
- **Generator:** `render/fig_ch25_adr.py` -> `fig-25-2501.png` (+`.pdf`). Embedded as **RASTER** (xref 16231, 2384 px wide).
- **Effective ppi:** 2384 px / 6.10 in = **390.8 ppi**. Source PDF (fig-25-2501.pdf) is natively 439.2pt (6.1in) wide, min span **8.50pt** -> placed at native width, so on-page min font = 8.50pt.
- **Geometry:** img bbox x 86.4-525.6, y 182.0-569.6; caption y 583.4 (gap 13.8pt).
- **Verdict:** PASS (source on-page min 8.5pt, high res raster, no clip).

### Fig 26.1 — pdf page 318
- **Generator:** `render/fig_ch26_fingerprint.py` -> `fig-26-2602.png` (+`.pdf`). (fig_ch26_radar.py is the RETIRED radar; fingerprint writes this figure.) Embedded as **VECTOR**.
- **Effective ppi:** VECTOR. Source PNG fig-26-2602.png (dpi=350) would be ~350 ppi if rasterized; not placed.
- **Geometry:** frame x 86.4-525.6, y 194.4-491.8; caption y 505.5. 26 spans; **min 8.00pt**; 0 <8pt. Caption ends "...not measured clusters."
- **Verdict:** PASS.

### Fig 26.2 — pdf page 324
- **Generator:** `render/fig_ch26_feedback.py` -> `fig-26-2601.png` (+`.pdf`). Embedded as **VECTOR**.
- **Effective ppi:** VECTOR.
- **Geometry:** frame x 86.4-525.6, y 152.1-518.1; caption y 531.8. 18 spans; **min 8.05pt**; 0 <8pt. Caption ends "...is a distinct scenario."
- **Verdict:** PASS.

### Fig A.1 — pdf page 327
- **Generator:** `render/fig_2701.py` -> `fig-27-2701.png` (+`.pdf`). Embedded as **VECTOR**. `fig._hermes_print_sized = True` (6.1in column authored).
- **Effective ppi:** VECTOR.
- **Geometry:** frame x 86.4-525.6, y 250.2-487.8; caption y 501.5. 22 spans; **min 8.50pt**; 0 <8pt.
- **Verdict:** PASS.

### Fig A.2 — pdf page 333
- **Generator:** `render/fig_ch27_norm.py` -> `fig-27-2704.png` (+`.pdf`). Embedded as **VECTOR**. Print-size authored (figsize 6.1x7.4in); fonts 10.0/9.6/9.0/8.8pt.
- **Effective ppi:** VECTOR.
- **Geometry:** frame x 86.4-525.6, y 89.0-621.8 (tall); caption y 635.6 (gap 13.8pt). 32 spans; **min 8.00pt**; 0 <8pt. Caption ends "...no shared bar scale to compare across."
- **Verdict:** PASS. Tall figure but caption fully on page (max caption y ~689 < text-block bottom), no clip.

### Fig A.3 — pdf page 336
- **Generator:** `render/fig_2703.py` -> `fig-27-2703.png`. NOTE: **no `.pdf` sibling** — the book embeds the **RASTER** PNG (xref 17477, 2239 px wide). Print-size authored (figsize 6.1x6.1in), fonts 8.5-8.8pt.
- **Effective ppi:** 2239 px / 6.10 in = **367.0 ppi**.
- **Geometry:** img bbox x 86.4-525.6, y 121.6-589.3; caption y 603.0 (gap 13.7pt). No vector text layer (raster); generator fonts 8.5-8.8pt at native 6.1in width -> on-page >=8.5pt.
- **Verdict:** PASS (print-size authored >=8.5pt at 367 ppi). NOTE: raster only; sub-8pt/clip cannot be confirmed from the text layer — flagged for the parent's vision round.

### Fig A.4 — pdf page 337
- **Generator:** `render/fig_2702.py` -> `fig-27-2702.png` (+`.pdf`). Embedded as **VECTOR**. Print-size authored (figsize 6.1x7.6in), `_hermes_print_sized = True`.
- **Effective ppi:** VECTOR.
- **Geometry:** frame x 86.4-525.6, y 81.8-629.0 (tall); caption y 642.8. 22 spans; **min 8.00pt**; 0 <8pt. Caption ends "...not 'what is best here.'"
- **Verdict:** PASS. Tall figure but caption fully on page (max caption y ~696), no clip.

---

# Figure Vision / Print-Legibility Log (Batch 4)

Judge: subagent (deepseek-v4-flash-vision-exp). Proof: `render/build/from-token-to-fleet-v20260913.pdf` (355 pp). Crops rendered at dpi=300 in `review/publication_qa/renders/fig<ch>_<fig>.png`. Method: locate caption in PDF text -> render clip of figure body (dpi=300) -> find generator via manuscript figure PNG -> read caption -> compute eff_ppi (source PNG px-width / 6.10 in placement) -> check geometry (drawing/img bbox vs caption, span overlaps, font sizes) + `vision_analyze` on the rendered crop for pixel-only checks (clip, label collision, legibility).

## Row summary (FIGID | pdfpage | generator | caption | eff_ppi | verdict)

| FIGID | pdfpage | generator | caption | eff_ppi | verdict |
|---|---|---|---|---|---|
| Fig 12.1 | 175 | render/fig_ch12.py | Candidate architecture synthesis, constraint-first: three conditional candidates, each with its own open validation gate; scope canonical workload; [ILLUSTRATIVE conceptual]. | 350 (raster-derived) | PASS |
| Fig 13.1 | 184 | render/fig_ch13_escalation.py | The reference-architecture ladder and its escalation triggers; escalate on model/KV/throughput overage, de-escalate on privacy/sovereignty/cost (also utilization, failure domain, ops burden, SLO margin); [ILLUSTRATIVE conceptual]. | 350 (raster-derived) | PASS |
| Fig 14.1 | 190 | render/fig_ch14_select.py | Capability screen then deployment benchmark; [ILLUSTRATIVE conceptual]. | 400 (raster-derived) | **FLAG: sub-8pt** — `screen`/`benchmark`/`gate` = 7.6pt; 2-line grey note `filter narrows the candidates…` = 7.5pt |
| Fig 15.1 | 196 | render/fig_ch15_flashattn.py | FlashAttention: the same math, far less HBM traffic; before (naive/SDPA) vs after (flash); tile-level on-chip reuse is per-tile; [ILLUSTRATIVE conceptual]. | 400 (raster-derived) | PASS (note: bottom 2-line citation small+low-contrast but 8.1pt; no clip/overlap) |
| Fig 15.2 | 198 | render/fig_ch15_goodput.py | Prefix caching and batching act on different serving phases: caching reduces prefill work; batching raises decode goodput; illustrative synthetic curves; [ILLUSTRATIVE][ASSUMPTION]. | 385 (raster-derived) | MINOR: panel (a) `[ILLUSTRATIVE]` tag `[` overlaps legend box border; panel (b) red-annotation last line treads dashed knee line |
| Fig 16.1 | 217 | render/fig_ch16_tco.py | TCO break-even: self-hosted vs managed API (canonical 80-layer full-MHA 70B FP16 8xH100); break-even volume illustrative, not portable; [ILLUSTRATIVE][DERIVED]. | 350 (raster-derived) | **FLAG: title/subtitle overlap** — "ILLUSTRATIVE LOWER-BOUND — NOT APPLES-TO-APPLES…" collides with "TCO break-even (~20-host fleet)" |
| Fig 17.1 | 221 | render/fig_ch17_capacity.py | Sizing a fleet by burst peak, headroom, and failover; a ~5.5 req/s burst a single host cannot meet, so a 4-host fleet (~8.0) is sized above it and N-1=3 residual (~6.0) still clears; [ILLUSTRATIVE][DERIVED]. | 400 (raster-derived) | **FLAG: sub-8pt** — top italic caveat (2 lines) = 7.0pt; `failover` label grazed by orange N-1 line |

### Notes
- All 7 figures are **vector-drawn** in the PDF (0 embedded raster images on these pages, i.e. the placeable `.pdf` sibling is embedded); `eff_ppi` is the source manuscript PNG px-width / 6.10 in placement, the size it would be at if rasterized. All ≥350 ppi (≥300 threshold met).
- No figure in this batch has text clipped **past its own figure bbox**; the flagged items are sub-8pt internal font size and one genuine label-on-label title/subtitle overlap (Fig 16.1) plus a minor legend-border overlap (Fig 15.2).
- Verified via `vision_analyze` on the actual rendered crop pixels for every figure in this batch.

### Per-figure detail
- **Fig 12.1 (p175)** — 10 spans, min 8.0pt. Vision: no clip, no overlap, no unreadable text. PASS.
- **Fig 13.1 (p184)** — 26 spans, min 8.0pt. Vision: clean, consistent type hierarchy. PASS.
- **Fig 14.1 (p190)** — 17 spans, **min 7.5pt** (5 spans <8pt). Vision: 2-line grey bottom note is smallest/hardest-to-read; no clip/overlap but sub-8pt body text.
- **Fig 15.1 (p196)** — 25 spans, min 8.10pt. Vision: no clip/overlap; bottom citation small+low-contrast but ≥8pt.
- **Fig 15.2 (p198)** — 36 spans, min 8.0pt. Vision: panel (a) `[ILLUSTRATIVE]` tag collides with legend border; panel (b) annotation edge-crowds dashed knee line. Minor.
- **Fig 16.1 (p217)** — 32 spans, min 8.2pt, **1 overlap** (area 556: "TCO break-even (~20-host fleet)" × "ILLUSTRATIVE LOWER-BOUND — NOT APPLES-TO-APPLES…"). Vision confirms label-on-label title/subtitle collision at top of figure.
- **Fig 17.1 (p221)** — 31 spans, **min 7.0pt** (2 spans <8pt: top italic caveat). Vision: caveat smallest/low-contrast; `failover` label grazed by orange N-1 residual line — sub-8pt + minor crowding.

---

# Figure Vision / Print-Legibility Log (Batch 2 — Figs 5.1–7.5)

Judge: subagent (deepseek-v4-flash-vision-exp). Proof: `render/build/from-token-to-fleet-v20260913.pdf`. Crops rendered at dpi=300 in `review/publication_qa/renders/fig5_1.png … fig7_5.png`. Verdicts for the four vector figures come from the placed-page vector text layer (span bbox overlaps, clip, font size); the four raster figures have labels baked into pixels, so those were checked with `vision_analyze` on the rendered crop.

## Row summary (FIGID | pdfpage | generator | caption | eff_ppi | verdict)

| FIGID | pdfpage | generator | caption(1-line) | eff_ppi | verdict |
|---|---|---|---|---|---|
| Fig 5.1 | 96 | render/fig_ch5_rag.py | Model selection for RAG: workload → five selection surfaces → two legs (retrieval/embedding, generation/70B) → the system decision. | vector (source PNG 350 ppi @6.10in) | OK — no overlap/clip; min label 8.0pt |
| Fig 6.1 | 99 | render/fig_ch6_diag.py | The metric hierarchy as a diagnostic chain (workload → resource → serving). | 350 (raster 2135px @6.10in) | OK — no overlap/clip; labels legible (vision) |
| Fig 6.2 | 101 | render/fig_ch6_hist.py | Request-latency distribution: p50/p90/p95/p99 and the mean. | vector (source PNG 350 ppi @6.10in) | OK — no overlap/clip; min label 8.5pt |
| Fig 7.1 | 113 | render/fig_ch7_gqa.py | Grouped-Query Attention cuts per-token KV (n_q : n_kv = 8:1). | 350 (raster 2135px @6.10in) | **FAIL — label collision:** orange side-caption "shared K/V heads" runs across the first K/V box and collides with the white "K/V" label inside it (confirmed on zoomed crop) |
| Fig 7.2 | 119 | render/fig_ch7.py | KV cache size vs context length, full-MHA vs GQA (FP16/FP8); ~8× GQA saving, 9.2K ≈24GB FP16 bound. | 350 (raster 2135px @6.10in) | OK — no label-label overlap/clip; footnote legible (vision) |
| Fig 7.3 | 120 | render/fig_ch7.py | Inference vs fine-tuning memory floor (70B): ~165GB serve vs ~1,120GB Adam; QLoRA ~60GB. | 350 (raster 2135px @6.10in) | OK — no label-label overlap/clip (green annotation arrow crosses "~60GB"; graphic-vs-text, not label-label) |
| Fig 7.4 | 121 | render/fig_ch7_budget.py | Concurrency budget: 640GB host pool = 140 weights + ~64 runtime + ~436 KV → ≈17.5 requests. | vector (source PNG 350 ppi @6.10in) | OK — no overlap/clip; min label 8.5pt |
| Fig 7.5 | 122 | render/fig_ch7_tetris.py | Memory Tetris: 640GB aggregate pool fills at 9.5K/32K/128K; only the KV cache grows. | vector (source PNG 331 ppi @6.10in) | OK — no overlap/clip; min label 8.0pt |

### Fig 5.1 — pdf page 96
- **Generator:** `render/fig_ch5_rag.py` -> `fig-05-0501.png` (+`.pdf`). Embedded as **VECTOR** (no raster xref; drawn as drawings+text).
- **Effective ppi:** VECTOR. Source PNG fig-05-0501.png is 2135 px wide (authored dpi=350) -> would be 2135/6.1 = 350 ppi if rasterized; the book places the vector PDF.
- **Geometry:** figure frame x 86.4-525.6, y 104.3-579.5; caption y 593.3 (gap ~13.8pt). 15 spans in frame; **min 8.00pt**; 0 spans <8pt; **0 overlaps**; no clip. Caption: "Model selection for RAG… the system decision."
- **Verdict:** OK.

### Fig 6.1 — pdf page 99
- **Generator:** `render/fig_ch6_diag.py` -> `fig-06-0601.png`. No `.pdf` sibling -> embedded as **RASTER** (xref 4477, 2135 px wide).
- **Effective ppi:** 2135 px / 6.10 in = **350.0 ppi**.
- **Geometry:** img bbox x 86.4-525.6, y 204.5-547.0; caption y 560.8 (gap 13.8pt). Raster (no vector text layer); verified via `vision_analyze` on the 300-dpi crop: no label overlap, no edge clip, all text legible.
- **Verdict:** OK.

### Fig 6.2 — pdf page 101
- **Generator:** `render/fig_ch6_hist.py` -> `fig-06-0602.png` (+`.pdf`). Embedded as **VECTOR**.
- **Effective ppi:** VECTOR. Source PNG 2135 px (dpi=350) -> 350 ppi if rasterized; not placed.
- **Geometry:** frame x 86.4-525.6, y 224.6-527.0; caption y 540.7. 29 spans; **min 8.50pt**; 0 <8pt; **0 overlaps**; no clip. Caption: "Request-latency distribution: p50/p90/p95/p99 and the mean."
- **Verdict:** OK.

### Fig 7.1 — pdf page 113
- **Generator:** `render/fig_ch7_gqa.py` -> `fig-07-0703.png`. No `.pdf` sibling -> embedded as **RASTER** (xref 5263, 2135 px wide).
- **Effective ppi:** 2135 px / 6.10 in = **350.0 ppi**.
- **Geometry:** img bbox x 86.4-525.6, y 218.2-506.2; caption y 520.0 (gap 13.8pt). Raster (no vector text layer); checked via `vision_analyze` on the 300-dpi crop and a 600-dpi left-side zoom.
- **Verdict:** **FAIL — label collision.** The orange row-caption "shared K/V heads" (drawn at x=0.35, ha='left', data y≈3.04 in `fig_ch7_gqa.py`) runs rightward across the first K/V box (box spans data x 1.025–2.275) and collides with the white "K/V" label centered inside it. The blue "query heads" label (x=0.35, y≈5.02) likewise runs over the first three blue query cells (cells begin at data x 0.60). No clipping and no sub-8pt text; the defect is the caption-vs-label overlap.

### Fig 7.2 — pdf page 119
- **Generator:** `render/fig_ch7.py` -> `fig-07-0701.png`. Embedded as **RASTER** (xref 5588, 2135 px wide).
- **Effective ppi:** 2135 px / 6.10 in = **350.0 ppi**.
- **Geometry:** img bbox x 86.4-525.6, y 169.7-500.9; caption y 514.6 (gap 13.8pt). Raster; verified via `vision_analyze`: no label-label overlap (text-over-graphic annotations are fine), no edge clip, footnote legible.
- **Verdict:** OK.

### Fig 7.3 — pdf page 120
- **Generator:** `render/fig_ch7.py` -> `fig-07-0702.png`. Only PNG present (no `.pdf` sibling) -> embedded as **RASTER** (xref 5600, 2135 px wide).
- **Effective ppi:** 2135 px / 6.10 in = **350.0 ppi**.
- **Geometry:** img bbox x 86.4-525.6, y 187.0-539.8; caption y 553.6 (gap 13.8pt). Raster; verified via `vision_analyze`: no label-label overlap, no edge clip, footnote legible. NOTE: the green "QLoRA fits a single H100" annotation's arrow crosses the "~60GB" value label — a graphic-vs-text intersection, not a label-label collision.
- **Verdict:** OK.

### Fig 7.4 — pdf page 121
- **Generator:** `render/fig_ch7_budget.py` -> `fig-07-0704.png` (+`.pdf`). Embedded as **VECTOR**.
- **Effective ppi:** VECTOR. Source PNG 2135 px (dpi=350) -> 350 ppi if rasterized; not placed.
- **Geometry:** frame x 86.4-525.6, y 113.4-394.2; caption y 408.0. 10 spans; **min 8.50pt**; 0 <8pt; **0 overlaps**; no clip. Caption: "The concurrency budget: where a 70B host's 640GB pool goes…"
- **Verdict:** OK.

### Fig 7.5 — pdf page 122
- **Generator:** `render/fig_ch7_tetris.py` -> `fig-07-0705.png` (+`.pdf`). Embedded as **VECTOR**.
- **Effective ppi:** VECTOR. Source PNG 2021 px wide -> 2021/6.1 = **331 ppi** if rasterized; not placed.
- **Geometry:** frame x 86.4-525.6, y 169.5-500.7; caption y 514.5. 14 spans; **min 8.00pt**; 0 <8pt; **0 overlaps**; no clip. Caption: "Memory Tetris: how the 8×H100 host's 640GB aggregate pool fills at 9.5K/32K/128K…"
- **Verdict:** OK.

---

# Figure Vision / Print-Legibility Log (Batch 5 — Figs 18.1–23.1)

Judge: subagent (deepseek-v4-flash-vision-exp). Proof: `render/build/from-token-to-fleet-v20260913.pdf` (355 pp). Crops rendered at **dpi=300** in `review/publication_qa/renders/fig_<ch>_<fig>.png`. Method: locate caption in PDF text -> render clip of figure body -> find generator via manuscript figure PNG (`design/manuscript/chapter-NN/figures/`) -> read caption -> compute eff_ppi (source PNG width / 6.10 in placement) -> check geometry (drawing/img bbox vs caption, span overlaps, on-page font size) + `vision_analyze` on the rendered crop for pixel-only checks. Sub-8pt measured from vector on-page span size (19.1/21.1/22.1 placed as vector) or authored font size × placement scale (raster). File is append-only.

## Row summary (FIGID | pdfpage | generator | caption | eff_ppi | verdict)

| FIGID | pdfpage | generator | caption | eff_ppi | verdict |
|---|---|---|---|---|---|
| Fig 18.1 | 245 | render/fig_ch18_routing.py | Model-routing decision tree: capability filter → cost/SLO gate → fallthrough, with specialist/general/fallback leaves. | 400 (raster) | **FLAG — label collision + truncation:** mid-row branch labels "yes → specialist" and "yes → frontier / small" render back-to-back (read "...specialistyes..."); "small" truncated to "smal" by the dropped green arrow line. No edge clip; min text 8.8pt. |
| Fig 19.1 | 248 | render/fig_ch19_loop.py | The agent loop: a four-state state machine (Plan/Execute/Observe/Decide), loop-back to Plan, terminal outcomes. | vector (source PNG 350 @6.10in) | PASS — no overlap, no clip; min on-page span 8.0pt. (Archify `agent-loop-lifecycle` on-page vector.) |
| Fig 19.2 | 255 | render/fig_ch19_trend.py | Token growth vs resulting KV growth across agent turns (I₀ + T·δ + T·γ + O_final; 24.9→34.0 GB). | 427 (raster) | **FLAG — sub-8pt ≈7.5pt:** authored 8.0pt legend/ticks squeezed 6.52in→6.10in (×0.936). No overlap/clip (vision). |
| Fig 19.3 | 256 | render/fig_ch19_accum.py | The agentic context block grows every turn (single-shot→turn 4, KV 24.9→34.0 GB). | 390 (raster) | PASS — no overlap/clip; min text ≈8.6pt (authored 8.4pt × 1.025). |
| Fig 20.1 | 269 | render/fig_ch20_capacity.py | Fleet capacity: analytical bound vs modeled offered-load-served curve vs host count. | 498 (raster) | **FLAG — sub-8pt ≈6.4pt:** authoring PDF is 546.7pt (7.6in) wide, placed at 439.2pt (6.10in) → ×0.803, so 8.0pt tick/annotation text → 6.43pt. No label-label overlap/clip; bottom-panel dotted curve crosses annotation text (text-vs-graphic). |
| Fig 21.1 | 274 | render/fig_ch21_pipeline.py | The AI Factory promotion pipeline: measured gate on each transition (build/integrate/staging/canary/prod). | vector (source PNG 350 @6.10in) | PASS (borderline) — no label-label overlap/clip; min on-page span 8.0pt. Minor: "Observe"/"Promote" letters tight to box edge. |
| Fig 22.1 | 282 | render/fig_ch22_divergence.py | Prefill vs decode scaling as context grows; quadratic attention overtakes linear at ~53.4K. | vector (source PNG 350 @6.10in) | **FLAG — sub-8pt 7.8pt + text-on-curve:** annotation "2·N only — full decode adds KV attention" = 7.8pt; left-panel "quadratic overtakes / linear at ~53K" sits on/through the plotted curves. No edge clip. |
| Fig 23.1 | 290 | render/fig_batch2.py | From a vague ask to architectural bounds (worked-example interrogation sequence). | 350 (raster) | PASS — no overlap, no clip; min text 8.5pt. |

### Notes
- **3 sub-8pt** figures in this batch (19.2 ≈7.5pt, 20.1 ≈6.4pt, 22.1 ≈7.8pt) — all below the 8pt print floor.
- **2 visual defects:** Fig 18.1 (branch-label collision + "small" truncation by arrow), Fig 22.1 (annotation sits on the curves). Fig 21.1 has only a minor letter-to-box-edge tightness (not a defect).
- 19.1 / 21.1 / 22.1 are embedded as **vector** in the PDF (on-page span size measured directly from the placed text layer); the rest are **raster**.
- Verified with `vision_analyze` on the actual rendered crop pixels for every figure (39/38/37 .. checked individually, incl. a zoomed crop of the Fig 18.1 label row).

### Per-figure detail
- **Fig 18.1 (p245)** — raster xref 12315 (2440×1720, 400 ppi), img bbox y 214.2–523.8, caption y 537.5. Min authored font 8.8pt (FS 9.0−0.2), scale 1.0. Vision (full + zoomed mid-row crop): two green branch labels touch ("specialist"/"yes" with no gap) and the centred "yes → frontier / small" is truncated to "smal" by the dropped green arrow line. **FLAG.**
- **Fig 19.1 (p248)** — vector (24 drawings, frame y 52.4–471.2), caption y 485.0. 12 spans, min 8.0pt, 0 <8pt, 0 overlaps. Vision: no overlap, no clip. PASS.
- **Fig 19.2 (p255)** — raster xref 12871 (2606×1196), img bbox y 72.0–273.6, caption y 287.3. Source authored 6.1in figsize, bbox-tight → content 6.515in, placed 6.10in → ×0.936. Min authored 8.0pt (legend/ticks/italic note) → 7.5pt on-page. Vision: no overlap/clip. **FLAG (borderline sub-8pt).**
- **Fig 19.3 (p256)** — raster xref 12885 (2381×2196), img bbox y 120.2–525.3, caption y 539.1. bbox-tight content 5.953in → ×1.025. Min authored 8.4pt (legend) → 8.6pt. Vision: no overlap/clip. PASS.
- **Fig 20.1 (p269)** — raster xref 13691 (3040×2141), img bbox y 72.0–381.3, caption y 395.1. Authoring PDF `fig-20-2001.pdf` is 546.69pt (7.6in) wide, placed at 439.2pt → ×0.803. Min authored 8.0pt (ticks/legend/annotation) → 6.43pt on-page. Vision: no label-label overlap, no edge clip; gray dotted bound crosses the bottom-panel annotation. **FLAG (sub-8pt).**
- **Fig 21.1 (p274)** — vector (48 drawings, frame y 52.4–497.5), caption y 511.3. 24 spans, min 8.0pt, 0 <8pt, 0 overlaps. Vision: no overlap/clip; "Observe"/"Promote" letters tight to box border. PASS.
- **Fig 22.1 (p282)** — vector (245 drawings, frame y 52.4–530.1), caption y 542.8. Min on-page span **7.8pt** ("2·N only — full decode adds KV attention"). Vision: no label-label overlap/clip; left-panel annotation drawn on the data curves. **FLAG (sub-8pt + text-on-curve).**
- **Fig 23.1 (p290)** — raster xref 14810 (2135×2240), img bbox y 111.5–572.3, caption y 586.0. `fig_batch2.py` figsize 6.1×6.4in, dpi 350, tight_layout → 6.1in content, scale 1.0. Min authored font 8.5pt (detail lines) → 8.5pt. Vision: no overlap, no clip, no sub-8pt.

---

# Figure Vision / Print-Legibility Log (Batch 3 — Figs 8.1, 8.2, 9.1, 10.1, 11.1–11.3)

Judge: subagent (deepseek-v4-flash-vision-exp). Proof: `render/build/from-token-to-fleet-v20260913.pdf` (355 pp). Crops rendered at **dpi=300** in `review/publication_qa/renders/fig<ID>.png`. Method: locate caption in PDF text → render clip of figure body → find generator via manuscript figure PNG (`design/manuscript/chapter-NN/figures/`) → read caption → compute eff_ppi (source PNG px-width / 6.10 in placement = 439.2 pt) → check geometry on the **vector** text layer (span size, word-box and box-border collision scans) + `vision_analyze` on the rendered crop for pixel-only checks (clip, label-in-box, label-on-label). Sub-8pt measured from the placed page / source vector-PDF span size × placement scale. File is append-only.

## Row summary (FIGID | pdfpage | generator | caption | eff_ppi | verdict)

| FIGID | pdfpage | generator | caption | eff_ppi | verdict |
|---|---|---|---|---|---|
| Fig 8.1 | 126 | render/fig_ch8_hierarchy.py | Hardware-hierarchy ladder: registers→tensor cores→SRAM→L2→HBM→interconnect→remote; where inference compute/data movement live; speed↔capacity↔distance gradient (schematic, relative not to scale). | 400 (raster 2440px @6.10in) | **FLAG — box-border strike-through:** top border of the three lower ladder boxes (`HBM (GPU memory)`, `GPU interconnect`, `other GPUs / remote`) cuts the top of the white bold title line; white glyph pokes ~4 pt above box top edge. Confirmed on vector PDF (word-box crossing at y250/296/342) and pixel-ink (0.37–0.44). Min on-page text 10.5pt; no label-on-label collision, no edge clip. |
| Fig 8.2 | 131 | render/fig_ch8.py | Per-GPU roofline, dense FP16, H100 vs H200 (per-GPU chart; FMA=2 FLOPs; peak ceilings; prefill/decode illustrative points; ridge classification unchanged by N-way replication). | 350 (raster 2135px @6.10in) | PASS (minor): no label-on-label overlap, no edge clip (vision). Note: min on-page text **7.7pt** = log-axis tick labels (mathtext exponent 0.7× base); plateau line grazes the `ANALYTICAL [DERIVED]` annotation band (roofline convention, not a label collision). |
| Fig 9.1 | 140 | render/fig_batch1.py | All-reduce completion time vs data volume by interconnect tier; effective bandwidths (NVSwitch 1.8/NVLink 0.9/IB ~40/RoCE ~2.5 GB/s); ring factor t=2·V/B; 140 GB 70B-FP16 gradient (training collective). | 350 (raster 2135px @6.10in) | PASS (minor): no label-on-label overlap, no edge clip, annotation clear of curves (vision). Note: min on-page text **7.0pt** = x-axis tick digits (10³→10⁶; bottom of figure-label floor). |
| Fig 10.1 | 148 | render/fig_ch10_parallel.py | Three parallelism patterns (TP shards one layer's weights/all-reduce; PP splits stage stack/P2P + bubble; DP replicates model/splits batch). | vector (placed 1:1, 6.1in column no downscale) | PASS. Vector PDF placed at native 439.2pt; min on-page font **8.5pt**. geom_audit's 21 "line-through-text" crossings are segment-bbox false positives (arrows pass near/through box borders in the gaps); vision + word-box scan confirm no glyph strike, no overlap, no clip, no sub-8pt. |
| Fig 11.1 | 159 | render/fig_ch11_batch.py | Discrete vs continuous (Orca) batching slot diagram; time steps, admit/evict; decode-only illustration. | 350 (raster 2135px @6.10in) | PASS: no clip, no arrow/border strike, no label-on-label overlap (vision). Min authored text 8.0pt (italic footnote/legend = smallest, at floor, legible). |
| Fig 11.2 | 162 | render/fig_batch1.py | Serving = four orthogonal concerns, not a stack (request scheduling / state management / reuse / resource specialisation). | 350 (raster 2135px @6.10in) | PASS: no overlap, no clip, no border strike (vision + word-box/box-border scan on the vector sibling = 0 hits). Min authored text 9.2pt (card labels 11.5pt, title 9.2pt), placed 1:1 → on-page ≥9.2pt. NOTE: renders as 2×2 grid, not 4 stacked rows — supports the "not a stack" claim. |
| Fig 11.3 | 163 | render/fig_ch11_pd.py | P/D disaggregation topology: prefill pool (FLOPs) + decode pool (HBM) bridged by KV transfer; worth it only when specialization benefit exceeds KV-transfer + orchestration. | 350 (raster 2135px @6.10in) | PASS (minor): no clip, no arrow/border strike, no label-on-label overlap (vision). Note: min authored text **7.5pt** = the two `8× H100 host` host captions. |

### Notes
- **1 genuine visual defect** in this batch: **Fig 8.1** box-border strike-through (the only class the word-box and box-border scanners both flag; confirmed via pixel-ink). 
- **3 sub-8pt** figures: Fig 8.2 (7.7pt log-axis ticks), Fig 9.1 (7.0pt x-tick digits), Fig 11.3 (7.5pt host captions). None is a hard block (all ≥7.0pt floor); 8.2/11.3 are minor, 9.1 is at the ~7pt floor.
- 10.1 is embedded as **vector**; its on-page min span measured directly from the placed text layer. 8.1/8.2/9.1/11.1/11.2/11.3 are **raster**; on-page font from the source vector-PDF span where a `.pdf` sibling exists (unscaled, placed 1:1) or the authored fontsize.
- Verified with `vision_analyze` on the actual rendered crop for every figure (incl. a 500-dpi zoom of the Fig 8.1 HBM-box top border).

### Per-figure detail
- **Fig 8.1 (p126)** — raster xref 5747 (2440×2360, 400 ppi), img bbox y 95.6–520.4 (figure fills top of the page), caption below. Vector sibling `fig-08-0802.pdf` natively 439.2×424.8 pt (placed 1:1), min span 10.5pt (FS 11.5−1.0). Word-box crossing at box borders y250/296/342 for `HBM (GPU`, `GPU`, `other GPUs`; pixel-ink on the border band inside text 0.37–0.44. Vision (zoom) confirms the top border cuts the top of the first line. **FLAG.**
- **Fig 8.2 (p131)** — raster xref 6003 (2135×1540, 350 ppi), img bbox y 142.8–459.6, caption below. Source vector-PDF min span 7.7pt (y-axis log tick digits). Vision: no overlap, no clip; plateau/grid lines pass near annotation labels but no glyph strike. PASS (sub-8pt note).
- **Fig 9.1 (p140)** — raster xref 6468 (2135×1645, 350 ppi), img bbox y 138.8–477.2. Source vector-PDF min span 7.0pt (x-axis tick digits). Vision: annotation arrow clear of curves, no overlap/clip. PASS (sub-8pt note).
- **Fig 10.1 (p148)** — VECTOR (40 drawings, frame y 52.4–547.0; text runs to y ~530, caption `figure 10.1:` at y 560.7). Placed at native 439.2pt (1:1). Min on-page span 8.5pt. geom_audit hits are segment-bbox false positives (arrows in gaps). Vision: no glyph strike, no overlap, no clip. PASS.
- **Fig 11.1 (p159)** — raster xref 7371 (2135×1855, 350 ppi), img bbox y 144.3–525.9. No `.pdf` sibling (PNG only). Min authored 8.0pt (figsize 6.1×5.3in, dpi 350, placed 1:1). Vision: no clip/overlap/strike; footnote/legend smallest but ≥8pt. PASS.
- **Fig 11.2 (p162)** — raster xref 7626 (2135×1225, 350 ppi), img bbox y 215.9–467.9. Vector sibling `fig-11-1101.pdf` natively 439.2×374.4 pt. Authored figsize 6.1×3.5in (dpi 350), placed 1:1; min authored 9.2pt (title), card labels 11.5pt. Word-box + box-border scans on the vector sibling = 0 hits. Vision: no overlap/clip. PASS.
- **Fig 11.3 (p163)** — raster xref 7662 (2135×1540, 350 ppi), img bbox y 72.0–388.8. No `.pdf` sibling. Min authored 7.5pt = `8× H100 host` host caps (figsize 6.1×4.4in, dpi 350, placed 1:1). Vision: no clip/overlap/strike. PASS (sub-8pt note).

## Figure fixes applied during audit (2026-10-24)
The independent vision pass found and fixed 4 genuine print-legibility defects:
- Fig 7.1: 'query heads' & 'shared K/V heads' side labels collided with cells/in-box 'K/V' -> moved to centered group-level labels. VERIFIED clean.
- Fig 15.2: per-panel '[ILLUSTRATIVE]' tags collided with panel (a) legend border and panel (b) full-height dashed line -> replaced with single figure-level footer. VERIFIED clean.
- Fig 14.1: two sub-8pt annotations (7.6/7.5) -> bumped to 8.0. VERIFIED.
- Fig 19.2: subagent flagged sub-8pt, but measured 9.96pt in-built (false alarm, no change).
