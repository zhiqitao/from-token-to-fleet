# PASS-11 FIXER — Responses (convergence pass, 8 small findings)

PASS-11 is a convergence pass and it confirms strong convergence: ch01-14 found **0 CRITICAL,
0 MAJOR, 0 MODERATE** — only 2 MINOR; ch15-27 found 6 (1 MODERATE, 5 MINOR). Total **8**,
all small. Findings in pass11_findings_01-14.md / pass11_findings_15-27.md. The PASS-10
deep-scale items (taxonomy harmonization, Ch16 TCO, duplication, claim-strength, glossary)
were all confirmed landed and correctly NOT re-reported. Trend: 22 → 12 → 11 → 24(deep) → 8.

## ch01-14 (2 MINOR)

- **P11-1 undefined "E1"/"E5" evidence keys** — ch07:143 ("(E1, E5)"), ch08:41 & 69
  ("moe-vs-dense E5 correction") cited a fact-key set that is nowhere defined. Replaced with
  resolvable pointers: ch07 → "the total-vs-active and MoE-vs-dense facts of Ch 3 (total ≠
  active per token; MoE gives compute sparsity, not weight-residency sparsity)"; ch08 →
  "consistent with the dense-forward scaling of Ch 3: 175B → 2 × 175 × 10⁹ ≈ 0.35 TFLOP/token."
  (Verified the 175B → 0.35 TFLOP/token arithmetic: 2×175e9 = 0.35e15.)
- **P11-2 Ch12 Table 12-1 "economics" column mislabeled** — The column held throughput/quality
  verdicts, not cost. Renamed the column "economics" → "**verdict**" and made the cells verdict-
  shaped: (a) "✗ capacity: needs ~5 hosts (per-request-latency baseline only)"; (b) "~2× capex +
  fabric; right at scale"; (c) "✗ >1 card at peak". Now the column's label matches its content.

## ch15-27 (1 MODERATE, 5 MINOR)

- **P11-3 [MODERATE] Ch22 Table 22-1 provenance residual** — The PASS-10 P10-M fix claimed to
  correct Table 22-1 but only the ratio row landed. Fixed the input/output token rows to
  `[canonical scenario][ASSUMPTION]` (matching §3 Step 1), so the whole table agrees with the
  prose — chosen scenario inputs are assumptions, not derived.
- **P11-4 [MINOR] worksheet.tex reduced taxonomy** — The worksheet (4th place the taxonomy is
  published) still advertised a 2-provenance × 3-status subset. Updated to the full two-axis
  list (provenance [1P]/[canonical scenario]/[2°]/[LAB]/[ILLUSTRATIVE]; status FACT/DERIVED/
  ASSUMPTION/HYPOTHESIS/UNRESOLVED) with a pointer to the Sources chapter. Now all four
  published statements of the taxonomy agree.
- **P11-5 [MINOR] Ch16 "a assumed"** — Corrected to "an assumed load-duration curve".
- **P11-6 [MINOR] Ch17 "a request span"** — Corrected to "a request spans multiple machines".
- **P11-7 [MINOR] Ch18 "per request … per hour" unit mix** — Corrected "Total token volume per
  request: ~9,200 in + ~300 out per hour" → "… ~9,200 in + ~300 out" (dropped the erroneous
  "per hour"; the values are per-request token counts).
- **P11-8 [MINOR] Ch18 $8,100 → $8,035** — Re-verified the derivation: ($23.75 − $12.59) × 720
  hr = $11.16 × 720 = **$8,035/month** (was overstated at $8,100). The "≈47% reduction" is
  accurate (1 − 12.59/23.75 = 47.0%).

## Items re-verified and confirmed consistent (per subagents' "considered and excluded")

- FP8-vs-8-bit KV (1.42 vs 1.31) consistently distinguished; ch05 "8-bit ~1.3" is the byte-halving
  figure, no conflict.
- ch09 56 s (flat lower-bound) vs 98 s (ring-adjusted) — both correct under stated framing.
- token-layer phrasing confined to Ch1; other chapters rewritten to "unit-and-token work of Ch 1".
- Measurement §4 de-duplication held; gradient 140/280 reconciled; Ch12 prefix-cache labeled
  [HYPOTHESIS]; Ch12 candidate (a) framed per-request baseline; Fig 7.1 "illustrates"; $15K
  per-host ceiling.
- Re-verified canonical arithmetic: 1.29 PFLOP prefill, 5.6 TB/s decode, 295 FLOP/byte ridge,
  24.1/24.9 GB KV, $0.012/req, 16.5M tokens/$, 2.1 req/s — all consistent.
- Ch15-27: C≈18, ~2.1 req/s, 344 in-flight, ~20 hosts; Ch17 W≈13.8 s lower bound; Ch19
  turn distribution/α/β; Ch22 1.29 PFLOP/5.6 TB/s; Ch24 PIES 768/6.5-host floor; Ch25
  30-vs-64 GB reconciliation and 18→33 concurrency; Ch27 Appendix A — all recompute correctly.

## Status
8/8 addressed. Convergence confirmed (PASS-11 = 8, all MINOR + 1 MODERATE residual-fix, with 0
CRITICAL/MAJOR). Rebuilding and verifying, then PASS-12. Expect PASS-12 to be near-zero.
