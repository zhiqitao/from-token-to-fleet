# Vision transport smoke test

**Date:** 2026-10-24
**Primary reasoning/vision model:** DeepSeek V4 Flash Vision Exp (per directive)
**Endpoints available:** native vision via `vision_analyze` (Hermes image tool)

## Test procedure
1. Rendered PDF **p25** (Figure 1.1, KV cache per token) from `render/build/from-token-to-fleet-v20260913.pdf` (355-page build, HEAD `e6b16f40`).
2. Saved full page at 200 dpi (`renders/p25_full.png`) and a 300-dpi crop of the Fig 1.1 region (`renders/p25_fig11_crop.png`).
3. Sent the actual crop PNG to the vision model via `vision_analyze` with a question answerable ONLY from pixels (count boxes, arrow routing, label-in-vs-border, collisions, arrowhead terminus).
4. Cross-checked against prior standalone figure PNG verification (the same figure was redrawn and independently vision-checked in the P1-07/P2-02 fix).

## Result

The model answered from the actual image pixels (it reported **7 rounded boxes**, described the left-to-right arrow flow tokens → append → stored K/V state → read for attention, and located each element left/center/right, top/middle/bottom). It returned **High confidence** on spatial questions that cannot be answered from extracted text and gave location descriptions — this is native pixel reception, not a text-path/text-file fallback.

| Question | Answer | Confidence |
|---|---|---|
| Number of rounded boxes | 7 (two cropped at edge) | High |
| `append new token KV` inside border or straddling | **INSIDE** (no straddle) | High |
| `store` label collides with box border? | **No** (clear gap) | High |
| Arrowheads reach box borders? | **Yes** (tips on border) | High |
| Any label overlapping another? | **No** | High |

## Conclusion
**PASS.** The vision transport delivers real pixels to the model and the model answers pixel-only spatial questions correctly. This validates the figure/print QA path. Model configuration unchanged during test.

## Caveat
This is a single-figure smoke test. It confirms the transport works; it does **not** certify all 46 figures or every page. That work is ongoing in the figure/page audit passes.
