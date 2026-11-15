# fix_pack_00 responses — round 5 disposition (target: ch15, 20 items)

Format per item: Severity | Location | Problem | Change | Status | Evidence.

---

## CH15-S5-01
| Field | Value |
|---|---|
| Severity | P1 |
| Location | chapter-15.md §5 Common Mistakes, "Ignoring KV cache growth" bullet |
| Problem | §5 called 100 "the in-flight geometry" while §3 labels 100 the active-user population and ~86 the in-flight request count — the passage contradicts §3 in the same breath. |
| Change | Replaced "~100 concurrent full-context *requests* (the in-flight geometry…)" with "~86 concurrent in-flight *requests* (§3: 10 rps × 8.6 s — request occupancy, not the ~100 active-user population)". |
| Status | **FIXED** |
| Evidence | Premise re-verified before edit (old clause present); new clause now matches §3's "~86 average in-flight requests at 10 rps … distinct from the ~100 active-user population". |

## CH15-SN-01
| Field | Value |
|---|---|
| Severity | P2 |
| Location | chapter-15.md, Architect's Question scope note (now the *Fleet implication* callout) |
| Problem | "~7-host prefill requirement" (100% MFU) mixed with the 35%-MFU screen in one clause; "prefill compute then binds" is true only under the 35% screen. |
| Change | Named the MFU basis: "bounded below by the ~7-host prefill requirement at theoretical peak (100% MFU); at the 35% MFU planning assumption the prefill screen is 19 hosts and binds above the 10-host FP8-KV screen". |
| Status | **FIXED** |
| Evidence | Premise held (old clause present); both bases now labelled, and 19 > 10 makes the binding claim follow from the stated numbers. |

## CH15-S6-01
| Field | Value |
|---|---|
| Severity | P2 |
| Location | chapter-15.md §6 decision (2) parenthetical |
| Problem | Reviewer meta-commentary left in prose ("whichever is meant", "specify which quantity is being tuned") instead of resolving whether 8 = prefill chunk tokens or decode batch requests. |
| Change | Resolved as a decode batch (decision (2) is max decode-step batch granularity): "(a max batch size of 8 requests per decode step — an [ILLUSTRATIVE] configuration, not the recommendation; the knee must be measured on the target stack)". |
| Status | **FIXED** |
| Evidence | Premise held; both meta-commentary phrases now absent (grep 0 hits), "the knee must be measured on the target stack" kept, [ILLUSTRATIVE] label preserved. |

## CH15-TERM-01
| Field | Value |
|---|---|
| Severity | P3 |
| Location | Global ch15–17 (defect located in chapter-15.md §4) |
| Problem | "KV-cache" (hyphenated) vs majority open form "KV cache" across ch15–17. |
| Change | "populating the KV-cache blocks" → "populating the KV cache blocks"; open form now sole form. |
| Status | **FIXED** |
| Evidence | Pre-edit counts: ch15 KV-cache 1 / KV cache 15, ch16 0/1, ch17 0/10; post-edit KV-cache = 0 in all three chapters. |

## CH15-SN-02
| Field | Value |
|---|---|
| Severity | P3 |
| Location | chapter-15.md, Architect's Question scope note (whole paragraph) |
| Problem | One dense paragraph carried ~10 claims and 3 host counts (21/10/~7) before §1. |
| Change | Split into a 3-sentence scope statement (one-host framing kept: per-request feasibility container, per-host SLO claim, "not the fleet configuration") plus a "> **Fleet implication (host-count arithmetic):**" blockquote (established callout convention, cf. Ch 17 reconciliation box) holding the Little's-Law/host-count arithmetic, with fleet sizing deferred to Ch 16/17. |
| Status | **FIXED** |
| Evidence | Scope paragraph now ends before the callout; all three host counts live only in the callout; protective one-host framing and roadmap sentence preserved verbatim. |

## CH15-01
| Field | Value |
|---|---|
| Severity | P1 |
| Location | chapter-15.md L101 (§8 mini-case scope note) |
| Problem | "bounded below by ~7 prefill hosts" used the 100%-MFU ceiling as a host-sizing screen; with 7 < 10 prefill would not bind. |
| Change | "bounded below by the 35%-MFU prefill screen of 19 hosts under case (i) (21 under case (iii), 22 under case (ii)) — the FP8-KV screen of 10 lies below it, so prefill compute binds". |
| Status | **FIXED** |
| Evidence | Premise held at L101; 19 > 10 now makes "prefill compute binds" follow, matching ch08 L171 and ch17 L123 screens. |

## CH15-02
| Field | Value |
|---|---|
| Severity | P2 |
| Location | chapter-15.md Table 15-1 header |
| Problem | "prefill demand ÷ host peak" gave no denominator; values 0.33/1.63/6.51 imply 56,500 tok/s (100% MFU), unstated and off the canonical 35% screen. |
| Change | Header now "prefill demand ÷ 100%-MFU parameter-matmul ceiling (56,500 tok/s)" (option a — denominator stated; values unchanged, so §3's "~6.5× demand over host peak" and the note stay consistent). |
| Status | **FIXED** |
| Evidence | 18,400/56,500=0.33, 92,000/56,500=1.63, 368,000/56,500=6.51 re-verified; denominator now printed in the header. |

## CH15-SCOPE-TILDE
| Field | Value |
|---|---|
| Severity | P3 |
| Location | chapter-15.md scope note / *Fleet implication* callout |
| Problem | "⌈344/17⌉ = ~21 hosts" hedged an exact ceiling while the same sentence printed "⌈344/35⌉ = 10" unhedged. |
| Change | "⌈344/17⌉ = **21 hosts**" — tilde removed. |
| Status | **FIXED** |
| Evidence | 344/17 = 20.235 → ⌈⌉ = 21 exactly; both ceilings in the sentence now unhedged; prose "~21 on the FP16 KV reference" (no ceiling operator) left as written. |

## CH15-17-01
| Field | Value |
|---|---|
| Severity | P1 |
| Location | chapter-17.md §4 bullet "The 25 ms/token in W is the TPOT budget…" (fix_instruction targets Ch 17) |
| Problem | 5.2 ms/step floor counted weights only; omitted the per-step KV read (17 × 24.9 GB), so "well under the 25 ms SLO" and the band's floor were wrong by ~4×. |
| Change | Added "bytes/step = 140 GB + B × 24.9 GB → at B = 17 ≈ 563 GB ÷ 26.8 TB/s ≈ 21 ms/step"; rewrote "well under" as "~84% of the 25 ms budget, not well under it"; re-anchored the band (weights-only 5.2 → KV-inclusive ~21 ms floor, W ≈ 7.4 s, in-flight ≈ 295, ~18 hosts; 25 ms pole kept); added the peak decode-leg check 12,000 × (140/17 + 24.1) GB/token ≈ 388 TB/s ≈ 14× HBM. |
| Status | **FIXED** |
| Evidence | 140+17×24.9=563.4 GB; 563.4/26.8=21.0 ms; 1.08+300×0.021=7.38 s; 40×7.38=295; ⌈295/17⌉=18; 12,000×32.335=388 TB/s; 388/26.8=14.5 — all recomputed and printed. |

## CH15-17-02
| Field | Value |
|---|---|
| Severity | P1 |
| Location | chapter-17.md §4 same bullet (sizing pole + sensitivity band); scope set by Ch 15 §1's TPOT ≤ 40 ms SLO |
| Problem | 25 ms called the "least-favourable/conservative" pole although the book's stated SLO pole is 40 ms; band 5.2/10/25 omitted the SLO pole (40 ms → W 13.08 s, in-flight 523, ⌈523/17⌉ = 31 hosts). |
| Change | Took the instruction's second option: named 25 ms a tighter internal sizing target (not least-favourable), added the 40 ms TPOT SLO pole to the band (W ≈ 13.1 s, in-flight ≈ 523, ~31 hosts on the KV screen) and stated "sizing at the SLO pole gives ~31 hosts"; "conservative choice" sentence rewritten. |
| Status | **FIXED** |
| Evidence | 300×40 ms=12.0 s → W=13.08; 40×13.08=523.2; ⌈523/17⌉=31 (+48% vs 21) — recomputed; band now 5.2 / ~21 / 25 / 40 with each pole labelled. |

## CH15-16-03
| Field | Value |
|---|---|
| Severity | P1 |
| Location | chapter-15.md scope note AND §8 mini-case (both "~7 prefill" places) |
| Problem | Same two passages as CH15-SN-01 (scope note) and CH15-01 (mini-case): ~7 at 100% MFU used as the binding screen. |
| Change | None — both places already fixed earlier in this pack (SN-01 named the MFU bases in the scope note; CH15-01 installed the 19/21/22-host 35%-MFU screen at L101). |
| Status | **DUPLICATE** |
| Evidence | Pack order: CH15-SN-01 (scope note) and CH15-01 (L101) precede this item and cover its exact "replace in both places" instruction; post-edit grep: 0 hits for "~7 prefill hosts" and "prefill compute then binds" in chapter-15.md. |

## CH15-15-08
| Field | Value |
|---|---|
| Severity | P2 |
| Location | chapter-15.md Table 15-1, "Illustrative load pressure" column + note |
| Problem | Undefined 12/38/52 column beside computed ratios; the note itself proposed removal ("or move the label to prose") and was never applied. |
| Change | Deleted the column (header + 3 values); ordinal commentary kept in the table note ("**Illustrative load pressure** — kept in prose here, not as a table column … the 12/38/52 values (light/typical/peak) …"); note's "(… or move the label to prose)" and "replace the column" wording updated; mini-case reference changed from "column" to "note". |
| Status | **FIXED** |
| Evidence | Table now 9 columns (was 10), all rows 10 pipes; check_tables gate passes; 12/38/52 and the [ILLUSTRATIVE] label survive in prose; mini-case "the 38 in Table 15-1's *illustrative load pressure* note" no longer points at a deleted column. |

## CH15-15-09
| Field | Value |
|---|---|
| Severity | P2 |
| Location | chapter-15.md Table 15-1, "Dominant Bottleneck" column |
| Problem | Column mixed §3's two axes (kernel label "Compute (SDPA)" vs capacity labels) and the Light row named compute although its own ratios say KV (0.97×) binds before prefill (0.33×). |
| Change | Split into "kernel regime (§3)" and "binding workload constraint (§3)"; Light row's binding constraint now leads with KV ("KV capacity — ~97% of the 436 GB budget …, tighter than prefill's 0.33× of peak") while "Compute (SDPA)" moved to the kernel-regime cell; note explains the split and that kernel regime is load-invariant (rows without a stated kernel label show "—"). |
| Status | **FIXED** |
| Evidence | 17×24.9=423.3/436=0.97 vs 18,400/56,500=0.33 — KV is the tighter ratio and is now the named binding constraint; axis labels match §3's definitions. |

## CH15-15-13
| Field | Value |
|---|---|
| Severity | P2 |
| Location | chapter-15.md §6 throughput-range sentence; chapter-17.md §4 reconciliation box item (3) |
| Problem | Same paragraph stated 35,000–56,000 then 35,000–48,000; Ch 17 cited the superseded 56,000 upper end. |
| Change | One range with basis in §6: "~35,000–48,000 tokens/s [ILLUSTRATIVE achievable range] at the canonical context (…; upper end = the case-(ii) attention-adjusted ceiling, lower end = the mini-case's per-host figure)"; Ch 17 item (3) now "~35,000–48,000 tok/s (Ch. 15)" and its shorthand "~35–48K". |
| Status | **FIXED** |
| Evidence | 7.912e15/1.4e11=56,514 (case i, labelled ceiling), case (ii) 1.5099e15/9,200=48,206 ≈ 48,000, mini-case ≈35,000 tok/s/host; grep: 0 hits for "35,000–56,000" and "~35–56K" in ch15/ch17. |

## CH15-15-16
| Field | Value |
|---|---|
| Severity | P2 |
| Location | chapter-15.md §7, second open question |
| Problem | Question conflated continuous batching (admission/scheduling policy — no chunk size) with chunked-prefill chunk size, in the chapter whose §6 separates them. |
| Change | Split into two questions: "*What is the optimal continuous‑batching admission and scheduling policy — maximum decode‑step batch, fairness, and prefill/decode interleaving — for the canonical workload?*" (+ one sentence: trades decode throughput against tail latency, knee measured on the target stack) and "*What is the optimal chunked‑prefill chunk size as a function of request arrival distribution (Poisson vs. bursty) and tail‑latency targets?*" with the original Poisson/burst follow-up kept on the latter. |
| Status | **FIXED** |
| Evidence | Arrival-distribution/tail-latency framing retained only on the chunked-prefill question per instruction; §6's "(distinct from … prefill token-budget chunking)" separation now echoed, not contradicted. |

## CH15-15-24
| Field | Value |
|---|---|
| Severity | P3 |
| Location | chapter-15.md §4 metric-family sentence; §6 decision (2) |
| Problem | "(§5)" resolved to Common Mistakes, not the unnumbered Optimization Decision Map; "§4's prefill token-budget chunking" pointed at Measurement, which contains no chunking (it lives in the unnumbered Two Mechanisms section). |
| Change | "the evidence column of the decision map (§5)" → "the evidence column of the Optimization Decision Map"; "(distinct from §4's prefill token-budget chunking)" → "(distinct from the Two Mechanisms subsection's prefill token-budget chunking)". |
| Status | **FIXED** |
| Evidence | Heading order re-checked (## 4. Measurement L40, ## The Optimization Decision Map {.unnumbered} L52, ## Two Mechanisms {.unnumbered} L71, ## 5. Common Mistakes L81); both wrong §-references now gone (grep 0 hits). |

## CH15-15-26
| Field | Value |
|---|---|
| Severity | P3 |
| Location | chapter-15.md §6, fourth decision (KV cache affinity) |
| Problem | "routing to the same GPU" is ill-defined for a TP=8 model and conflicts with the book's host-level affinity model (Ch 17 sticky sessions route to the same host). |
| Change | "routing to the same GPU" → "routing to the same host". |
| Status | **FIXED** |
| Evidence | Premise held (phrase present once in ch15); matches ch17 "route subsequent requests from the same user to the same host (sticky sessions)". |

## FIG-15.1-03
| Field | Value |
|---|---|
| Severity | P2 |
| Location | chapter-15.md, Fig 15.1 caption (caption edit preferred; no generator change) |
| Problem | "O(L²)" only on the BEFORE panel invited the inference that FlashAttention is asymptotically cheaper in HBM traffic; caption's scope note addressed the mathematics, not the asymptotics. |
| Change | Added to the caption: "Both paths still do Θ(L²) HBM element accesses (with d fixed) — the gain is a constant factor set by on-chip capacity (d²/M), not a lower order." |
| Status | **FIXED** |
| Evidence | Caption edit only — figure binary untouched (fig-15-1502.png/pdf mtimes unchanged, 00:46); [ILLUSTRATIVE conceptual] label and I/O citation preserved. |

## FIG-15.2-01
| Field | Value |
|---|---|
| Severity | P2 |
| Location | chapter-15.md, Fig 15.2 caption (caption option chosen; no re-render needed) |
| Problem | In-plot symbols S and P undefined in figure, caption or prose; "shared" reading of S contradicts the plotted curve. |
| Change | Caption now defines them: "the in-plot note's f(r)=(S+P/r)/(S+P) uses P = 40% — the reusable prefix share of the prompt — and S = 60% — the unique suffix". |
| Status | **FIXED** |
| Evidence | Matches render/fig_ch15_goodput.py (P_frac, S_frac = 0.40, 0.60 and the note string 'f(r)=(S+P/r)/(S+P)\nP=40%, S=60%'); f(10)=(0.6+0.04)/1=0.64 = plotted ~64, asymptote 60%; a reader can now state P and S from the caption alone. |

## FIG-15.2-03
| Field | Value |
|---|---|
| Severity | P2 |
| Location | render/fig_ch15_goodput.py line 57 (panel-(a) formula note) → regenerated figure 15.2 |
| Problem | Panel-(a) note at 7.0 pt, below the book's 8 pt in-figure floor, while carrying the decision-relevant formula. |
| Change | fontsize 7.0 → 8.0; regenerated ONLY this figure via `render/regen_one.py render/fig_ch15_goodput.py` (matplotlib-bearing venv python; default python3 lacks matplotlib). |
| Status | **FIXED** |
| Evidence | Exit 0, "ONE-DONE fig_ch15_goodput.py"; fig-15-1501.png 255,834→257,203 B (2440×1400 RGBA) and .pdf 34,152→34,108 B (PDF 1.4, 1 page) with advanced mtimes, fig-15-1502 untouched; both notes now 8.0 pt — measured at 150 dpi the 8 pt cap glyph is 16.67 px (≥ ~12 px) and identical to the 8.0 pt panel-(b) callout (17.00 px line box). |

---

## Counts
- FIXED: 19
- SKIPPED_PREMISE: 0
- NEEDS_REGEN: 0
- DUPLICATE: 1 (CH15-16-03)

## Files changed
- design/manuscript/chapter-15/chapter-15.md
- design/manuscript/chapter-17/chapter-17.md
- render/fig_ch15_goodput.py
- design/manuscript/chapter-15/figures/fig-15-1501.png (regenerated)
- design/manuscript/chapter-15/figures/fig-15-1501.pdf (regenerated)

## Gates run (all pass)
- render/check_tables.py — "all markdown tables: column counts consistent" (exit 0)
- render/check_md_leaks.py — "no markdown leak risks detected" (exit 0)
- render/check_regressions.py — exit 0 (includes stale-value gate OK)
- render/check_stale_values.py — "OK - no stale superseded values found in live manuscript text" (exit 0)
- No PDF rebuild; only fig-15-1501 binaries rewritten.