# PASS-17 FIXER RESPONSES — full-prompt re-review of the fully rendered PDF

Applied the complete 55-section prompt to the BUILT PDF (from-token-to-fleet-v20260913-full.pdf,
308pp) with visual figure inspection. The pass surfaced a NEW defect class the 16 text-only passes
missed: **rendered-figure label clipping / figure-vs-prose numeric mismatch / figure-composition**.
All findings addressed below.

| # | Severity | Location | Problem | Disposition |
|---|----------|----------|---------|-------------|
| P17-1 | CRITICAL | Fig 8.1 ladder | 6/7 box labels clipped by box edges; title overlaps top box | FIXED — widened ladder boxes (auto-sized to longest label), broke long names onto two lines, lowered title & box stack. Pixel-verified all 7 names fully inside boxes; title clear. |
| P17-2 | MAJOR | Fig 10.2 | Review claimed "PP · Pipeline Paralle", "CP · Context Paralle", "experts 6-1" clipped | VERIFIED FALSE POSITIVE — PDF text layer contains FULL strings ("PP · Pipeline Parallel" 105.5pt span, "experts 1-5/6-10/11-15" all present). The "experts 6-1" was a vision misread; "experts 11-15" spans 62pt inside its 92pt box. No clipping. |
| P17-3 | MAJOR | Fig 7.3 | Full-fine-tune bar ~1260 GB vs body/Table 7-2 ~1120 GB | FIXED — fig_ch7.py `vals[1]` 1260→1120. Rebuilt; ~1260 gone, ~1120 present; also cleaned legend/red-note overlap. |
| P17-4 | MODERATE | Fig 4.1 | Figure's six axes ≠ the chapter's six-dimension framework | FIXED — aligned to Quality/Traffic/Token-profile/Latency/Economic/Operational with the caption's exact consequences mapping. |
| P17-5 | MODERATE | Fig 6.1 | No arrowheads/legend; ordering vs §6.2.1 | FIXED — added boxed "Direction of the chain" legend (solid=Causation↓, dashed=Diagnosis↑). Ordering already matches the causal chain (Workload→Resource→Serving); §6.2.1's 1/2/3 numbering is a different (question) enumeration. Legend at ≥9.7pt on-page. |
| P17-6 | MODERATE | Fig 10.1 | Band titles overprint child boxes; purple title overprints sentence | FIXED — raised band-title banners above their dashed regions (banner bottom clears box top by ~18px); separated purple title/sentence (y 403→392 / 419→436). Re-delivered via Archify (9/9). |
| P17-7 | MINOR | Fig 6.2 mean | Figure 0.85 vs §6.4.1 analytic 0.84 | FIXED — §6.4.1 now notes the exact simulated stream mean ≈0.85s vs the 0.84 two-point approximation. |
| P17-8 | MINOR | Fig 7.4 | FP8 row omits weights/runtime labels; in-figure title vs caption mismatch | FIXED — added FP8-row weights/runtime/KV labels; in-figure title now matches caption ("The concurrency budget: where a 70B host's 640 GB pool goes"). |
| P17-9 | MINOR | Fig 7.2 | Legend covers data; FP8 label vs measured FP8; annotation crosses KV line | FIXED — legend moved outside plot (bbox_to_anchor); FP8 re-labeled "byte-halving bound, ~1.3 MB/tok"; 9.2K annotation repositioned clear of the 436 GB line. |
| P17-10 | MINOR | Fig 12.1 | "decode pool: bandwidth-bound" note overlaps ~19.8K label | FIXED — note repositioned to upper axes region (y=24500) clear of the bar/label. |
| P17-11 | MODERATE | Fig A.1 | Log-axis bars under-encode total:active ratio | FIXED — re-encoded as linear bars of active-fraction % (the message), with total/active annotated per row. Rebuilt; single-digit sparsity now visually primary. |
| P17-12 | MODERATE | Ch16 §16.4 vs Ch18 §3.2 | Self-host ~$0.60/1M vs per-1M table $2.50/1M (4.2×) | FIXED (scoped, not contradicted) — added explicit basis note in Ch18 §3.2: per-model nominal rate vs fleet-amortized TCO; the ~4× gap is a utilization/throughput basis difference, not a contradiction. |
| P17-13 | MODERATE | Ch16 vs Ch17 | Ch16 prices at full-util ~20 hosts; book's own 70% rule → ~28 hosts | FIXED — added explicit provisioning-sensitivity block in Ch16 §16.4 stating the full-utilization assumption and giving the 70%-util (~28 hosts, ~$203K/mo, ~$7.8/1K) alternative. |
| P17-14 | MINOR | Fig 15.1 | Two bottom O(L²)/O(L) annotations too close | FIXED — widened inter-panel gap (8→20pt) for clear separation. |

## Verified in the rebuilt PDF
- Fig 7.3: "~1120 GB" present, "1260" gone; x-ticks legible.
- Fig 8.1: all 7 labels fully inside boxes; title clear of top box (pixel-verified).
- Fig 7.2: legend outside plot; FP8 labeled byte-halving bound; annotation clear of KV line.
- Fig A.1: linear active-fraction bars, "single-digit active" visually primary.
- Fig 6.1: directional legend present ≥9.7pt.
- Fig 10.1: band-title banners clear of child boxes; purple title/sentence separated.
- Ch16/Ch18 cross-chapter notes present in PDF text.

## Convergence note
PASS-17 = 14 findings (1 CRITICAL, 2 MAJOR [1 false-positive], 7 MODERATE, 4 MINOR), all addressed.
This was the visual/figure-scale pass that the text-only loop had been missing.
