# PASS-12 — FINAL CONVERGENCE REVIEW, ch01-14 ('From Token to Fleet')

**Verdict: NO NEW FINDINGS.**

Scope: final convergence pass over `design/manuscript/chapter-01..14` (the source for the
308-pp `from-token-to-fleet-v20260913-full.pdf`). A full careful line-by-line read of all 14
chapters against the book's own rules: two-axis evidence taxonomy (provenance
`[1P]/[canonical scenario]/[2°]/[LAB]/[ILLUSTRATIVE]` × status
`[FACT]/[DERIVED]/[ASSUMPTION]/[HYPOTHESIS]/[UNRESOLVED]`, no `[INTERPRETATION]`), investigative
narration, 谦逊语气 (no reader-address, no "Think of X as Y"), and the fixed canonical reference
set (canonical-workload.yaml / Ch 4 Table 4-3). Every candidate finding was compared against
PASS-1..11 and re-verified before being accepted or excluded.

## Result: ZERO new issues.

- **0 CRITICAL, 0 MAJOR, 0 MODERATE, 0 MINOR** newly-identified items in ch01-14.
- Confirmed the two PASS-11 MINOR residuals (**P11-1** undefined "E1"/"E5" codes; **P11-2**
  Ch12 Table 12-1 "economics" column) are **fully fixed in source**:
  - P11-1: No "E1"/"E5"/"moe-vs-dense E5" string remains anywhere in ch01-14 (grep returns
    zero). ch07:143 now cites "the total-vs-active and MoE-vs-dense facts of Ch 3"; ch08:41/69
    now cite "the dense-forward scaling of Ch 3: 175B → 2 × 175 × 10⁹ ≈ 0.35 TFLOP/token" (a
    resolvable pointer to the same 2×N formula; verified 2×175e9 = 0.35e15).
  - P11-2: Ch12 Table 12-1 (line 81) column is now **"verdict"**, populated with verdict-shaped
    cells: (a) "✗ capacity: needs ~5 hosts (per-request-latency baseline only)"; (b) "~2× capex +
    fabric; right at scale"; (c) "✗ >1 card at peak". Label now matches content.

## What was checked (all consistent)

- **Voice / tone:** zero "you"/"your" reader-address, zero "Think of X as Y" constructions,
  zero `[INTERPRETATION]` tags. 谦逊语气 held throughout.
- **Taxonomy brackets:** 8 `[ASSUMPTION]` status tags, all carrying a valid provenance axis
  (e.g. `[ILLUSTRATIVE][ASSUMPTION]`); single-axis-implied house variation (as permitted by
  sources.tex) is not a defect. No orphan status-only or provenance-only brackets found.
- **Figures:** every `figures/…` reference in ch01-14 resolves to a file on disk (script check
  returned zero missing); no dangling figure refs.
- **Placeholders:** no TODO/TBD/author-note/"to be filled"; the only "to be verified" phrasing is
  the book's legitimate UNRESOLVED/hypothesis discipline.
- **Re-verified canonical arithmetic** (sample, all consistent with Ch 4 Table 4-3 / the
  canonical box and across chapters):
  - Ch1/Ch7 KV: 2 × 80 × 8192 × 2 B = 2,621,440 B = 2.5 MiB / 2.62 MB (FP16, decimal) and
    1,310,720 B = 1.25 MiB (8-bit); 24.1 GB @9.2K, 24.9 GB @9.5K, 164.1 GB vs 164.9≈165 GB
    residency distinction held (P8-6, P9-5 resolved).
  - Ch2/Ch6/Ch8 compute: 140 GFLOP/token, 1.29 PFLOP prefill, 1.19 PFLOPS rate, 5.6 TB/s decode,
    346 TFLOPS (×0.35 MFU), 2,471 tok/s/GPU, ~19,800 tok/s/host, ridge ~295 FLOP/byte,
    prefill demand 12.9 PFLOP/s, attention term +17% @9.2K / +60% @32K / ~2.4× @128K.
  - Ch2/Ch4/Ch8/Ch13/Ch14 latency & fleet: 344 in-flight (40×8.6), C≈18 → ~2.1 req/s,
    ~5 hosts @avg / ~19–20 @peak, ~24/34 hosts (Ch4 mini-case).
  - Ch9 communication: NVLink 140/900 ≈ 0.16 s (ring 0.27 s); Option B (InfiniBand ring with
    ~40 GB/s effective) ≈ 6.1 s; Option C (Ethernet ring) ≈ 98 s; ~22× (~6.1/0.27) and ~350×
    (~98/0.27); ~35 GB KV /900 ≈ 0.04 s. (The 40 GB/s "effective" vs 25 GB/s "per-link" and the
    flat-vs-ring 5.6 s / ~35× and 6.1 s / ~22× framings were all explicitly verified as
    correct-and-intentional in PASS-8 line 68 and PASS-9 line 64.) P7-1/P7-5 resolved.
  - Ch10 routing: 140 GB weights → ≥2 H100; FP32 gradient 280 GB → 11 s / 0.31 s sync;
    PP bubble speedups 32/11 ≈ 2.9× and 128/35 ≈ 3.66×.
  - Ch12/Ch14: prefix-cache ~28K tok/s (19.8K × ~1.43 for the ~30% amortization); Ch14 loaded
    at ~18 concurrent / ~2.1 req/s (not the 40 rps fleet burst) and goodput ~19,800 ≈ the
    ~20K tok/s it serves (P8-3 resolved).

## Considered and excluded (verified not-new / not-a-defect)

- **Ch9 Option B ~40 GB/s vs ~25 GB/s HDR per-link.** Rejected — already explicitly verified
  as intended "effective" (multi-port/aggregation) throughput in PASS-8 and PASS-9; consistent.
- **Ch9 "~22×" (ring-adjusted) vs "~35×" (flat lower-bound) NVLink→InfiniBand multiples.**
  Rejected — both correct under their own (explicitly stated) flat vs ring models; the chapter
  names the distinction; not an inconsistency.
- **Ch4 §3 "~$2,500/month reserved" aside.** Rejected — explicitly labeled
  `(illustrative)`, is a separate purchase-mode aside, and is **not** consumed by any derived
  number (every computed TCO uses the canonical on-demand $20/hr → ~$14.6K/mo per-host basis).
- **Ch8 [DERIVED] "175B → 0.35 TFLOP/token".** Rejected — introduced only as an example of the
  dense 2×N scaling formula, consistent with Ch 3's total-vs-active machinery; the pointer
  ("dense-forward scaling of Ch 3") is resolvable. It is the P11-1 replacement, applied as
  specified.
- **Ch7 "token layer"** and cross-chapter "unit-and-token work of Ch 1" phrasing. Rejected —
  confined to Ch1 (self-referential) and the Ch1 cross-references, per PASS-10-7 / PASS-11
  considered-and-excluded.

---

*Conclusion: ch01-14 have fully converged. The trend across passes — 12 → 11 → 24 (deep-scale)
→ 8 (all MINOR + 1 MODERATE residual) → **0** — confirms the FINAL convergence pass finds **zero
genuinely new comments**. No open items remain in ch01-14. Recommend the loop be concluded; no
further fixes required for these chapters.*
