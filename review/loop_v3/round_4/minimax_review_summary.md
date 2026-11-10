# MiniMax-M3.1-Flash review — loop_v3 round 4 (independent panel pass)

Model: `MiniMax-M3.1-Flash` (im-eglb, new panel member), reasoning_effort=max,
streaming. Text stage: 6 chunks (whole manuscript, figures stripped, 55-section
standard + review_prompt_v2). Vision stage: 11 batches = 87 figure pages rendered
at 150 dpi from the current built PDF (render/latex/book.pdf, 462 pp, built
2026-11-09 05:54).

Run window: 2026-11-09 20:13 → 2026-11-10 13:40 PST. The im-eglb MiniMax
upstream was unresponsive 03:00–05:40 (all requests timed out; MiMo/DeepSeek
healthy), which failed text c3–c5 and vision b6–b9; `render/resume_minimax_round4.py`
cleaned the `[[ERR]]` files, waited for a live model, and re-ran them to completion.

## Findings count (normalized severity)

| Stage | Files | Total | P0 | P1 | P2 | P3 |
|---|---|---|---|---|---|---|
| text (c0–c5) | 6/6 | 152 | 0 | 11 | 64 | 77 |
| vision (b0–b10) | 11/11 | 223 | 4 | 32 | 76 | 111 |
| **total** | 17 | **375** | **4** | **43** | **140** | **188** |

Panel comparison this round (merge stage): MiniMax 375, Qwen3.8-27B 92,
MiMo-V2.6-Flash-RL 65, DeepSeek-V4.1-Flash 13. Cross-model consensus: 6 findings,
all of them involving MiniMax (4 with Qwen, 1 with MiMo).

## P0 dispositions — all 4 DISPROVED against the current built PDF

Each was checked twice: `pdftotext` extraction of the exact PDF page, then a
110 dpi render of that page vision-inspected.

| id | claim | verification | verdict |
|---|---|---|---|
| FIG-2.2-A | caption says "long-prefix prefill lands at ~41 FLOP/byte", contradicting plot (~10^4) and prose (~2K) | caption actually reads "long-prompt prefill lands at high intensity" (no number); prose says ~9.2K; marker sits at ~10^4 | FALSE POSITIVE — quoted caption does not exist |
| FIG-7.7-01 | substitution line reads "436 GB + 24.9 GB = 17.5" (plus sign) | page 145 line reads "≈ 436 GB ÷ 24.9 GB ≈ 17.5" (division), matching the formula line above | FALSE POSITIVE — misread ÷ as + |
| FIG-8.2-01 | caption claims 1,979 TFLOPS for H200 | caption states a single shared "989 TFLOPS, 3.35 / 4.8 TB/s"; "1,979" appears nowhere on page or figure | FALSE POSITIVE — hallucinated caption value |
| PAGE-227-01 | text computes 4×9,200²×8,192 = 2.2×10^16 (off by 100×) | page 247 prints 2.8×10^12 per layer and 2.2×10^14 across 80 layers — both correct | FALSE POSITIVE — misread exponent 14 as 16 |

## P1 sample verification (5 of 43 checked)

| id | stage | quote real? | verdict |
|---|---|---|---|
| CH4-01 | text | yes (ch4 L49/L193) | real lead — economics headline priced on 6/21-host full-util basis vs the book's own 9/32 policy-fleet screen; book does caveat "before SLO/headroom/failover", so disposition is likely DEFENSIBLE-or-label, not a rewrite |
| CH11-01 | text | yes (ch11 L130) | real lead — "single host holds TTFT at 10 rps" bullet vs Ch4/Ch12/Ch13 "one host cannot serve the offered rate" |
| CH26-01 | text | yes (ch26 L104) | real lead — 450 ms declared "service-time sum with no queueing term" while ρ≈1 is acknowledged in the same sentence |
| TBL-12.2-01 | vision | no | FALSE POSITIVE — actual cell reads "19.8K ≪ ~92K" and "92K ÷ 19.8K ≈ 4.65"; reviewer read ≪ as ≈, 92K as 9.2K, ÷ as × |
| FIG-7.5-01 | vision | garbled | mostly FALSE POSITIVE — actual caption reads "~2.62 MB/token, FP8/8-bit ~1.31; at 128K ... ~335 GB"; reviewer quoted "1.31 GB", "~535 GB", a fragment salad. Residual real nit: the caption prints "~1.31" with no unit |

## Calibration conclusion

- **Text-stage findings are high-value**: 3/3 sampled quotes were real and the
  recomputations used the book's own numbers.
- **Vision-stage findings have a high false-positive rate**: 4/4 P0 and 2/2
  sampled P1 vision findings were glyph-level misreads or hallucinated quotes
  (÷→+, ≪→≈, 92K→9.2K, 10^14→10^16, invented caption numbers).
- Treat the 223 vision findings as LEADS requiring page re-check before any fix;
  the 152 text findings can go to disposition with normal trust-but-verify.

## Artifacts

- `review/loop_v3/round_4/text_MiniMax-M3.1-Flash_c{0..5}.json`
- `review/loop_v3/round_4/vis_MiniMax-M3.1-Flash_b{0..10}.json`
- `review/loop_v3/round_4/minimax_all_issues.json` (375 issues, severity normalized)
- `review/loop_v3/round_4/merged.json` (4-model merge incl. MiniMax)
- `render/resume_minimax_round4.py` (self-healing resume driver)