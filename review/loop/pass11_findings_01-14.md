# PASS-11 — CONVERGENCE REVIEW, ch01-14 ('From Token to Fleet')

Scope: convergence pass over `design/manuscript/chapter-01..14` (the source for the 308-pp
`from-token-to-fleet-v20260913-full.pdf`). Full careful read of all 14 chapters against the
book's own rules: two-axis evidence taxonomy (provenance `[1P]/[canonical scenario]/[2°]/[LAB]/[ILLUSTRATIVE]`
× status `[FACT]/[DERIVED]/[ASSUMPTION]/[HYPOTHESIS]/[UNRESOLVED]`, no `[INTERPRETATION]`),
investigative narration, 谦逊语气 (no reader-address, no "Think of X as Y"), and the fixed canonical
reference set (canonical-workload.yaml / Ch 4 Table 4-3).

Method: read every line of ch01-14; re-verified every numeric/cross-ref I could, and compared
each candidate finding against all prior pass findings (PASS-1..9 numeric/cross-ref; PASS-10
deep-scale). Only genuinely NEW, non-fixed items are reported. Items that were already fixed,
that are covered by an already-reported PASS-1..10 finding, or that are intentional/consistent
despite appearing inconsistent were verified and **excluded** (see the "considered and excluded"
table at the bottom).

## Verdict

**STRONG CONVERGENCE — no CRITICAL, no MAJOR, and no MODERATE new findings.** All previously-reported
issues (PASS-1..10) are materially resolved in the source. Two **(2) MINOR** cosmetic/verifiability
items remain that no prior pass touched.

---

## MINOR (new, not previously reported)

### [P11-1] Undefined evidence keys "E1", "E5", "moe-vs-dense E5" referenced in reader-facing prose
**Location:** `chapter-07/chapter-07.md:143` ("The MoE-vs-dense facts (E1, E5) confirm…");
`chapter-08/chapter-08.md:41` ("…consistent with the 175B ≈ 0.35 TFLOP/token correction from moe-vs-dense E5");
`chapter-08/chapter-08.md:69` (same "moe-vs-dense E5 correction" in Table 8-1).
**Problem:** These cite a fact/evidence key set ("E1", "E5") that is **nowhere defined** in ch01–14
(or, per repo-wide grep, anywhere in `design/`, `ref/`, or `craft/`). A reader of the published book
has no way to resolve what "E5" is or what "moe-vs-dense E5" points to. The surrounding text is
self-contained and numerically correct (175B → 0.35 TFLOP/token is 2×175e9 = 0.35e15, consistent with
the 70B → 140 GFLOP/token), so no number or conclusion is wrong — but it is a dangling provenance
pointer in a book whose central discipline is auditable evidence.
**Why it matters (MINOR):** The book's core pitch is that every claim carries a verifiable source.
An unexplained "E5" code re-introduces exactly the "cite a key the reader can't look up" problem the
evidence appendix was meant to solve; it undercuts verifiability even though it changes nothing.
**Recommended change:** Replace the E-key shorthand with a resolvable pointer, e.g. "consistent with the
moe-vs-dense correction (Chapter 3 §3 / Table 3-1: 175B ≈ 0.35 TFLOP/token)" and, in ch07, "the
total-vs-active facts of Ch 3 §1 confirm…" — or add "E1/E5" to a definitions/evidence legend if the
E-key index is meant to be public.

### [P11-2] Ch12 Table 12-1: the "economics" column is populated with throughput/quality verdicts, not economics
**Location:** `chapter-12/chapter-12.md` Table 12-1, lines **83–85** (column header "economics"):
row (a) = "✗ throughput: needs ~5 hosts"; row (c) = "✗ >1 card at peak". (Row (b) = "✗ 2 hosts + fabric",
which is genuinely economic.)
**Problem:** The column is labeled **economics**, but rows (a) and (c) put a *throughput/capacity*
verdict there (and row (c) also folds in quality under a different column). The throughput verdict for
(a) is already given (correctly) in the "throughput" column, so the economics column becomes a
duplicate, mislabeled throughput verdict rather than a cost figure. Readers using the table to compare
candidate *economics* get no dollar/TCO value in the column that claims to be about economics.
**Why it matters (MINOR):** Table hygiene / label–content mismatch in the chapter's central
candidate-comparison table; it does not misstate any number, but it makes the constraint-satisfaction
columns harder to read at a glance.
**Recommended change:** Either rename the column to "constraint verdict" (and keep the throughput note),
or put an explicit cost figure there (e.g. "≈$14.6K/mo per host (Ch 16)") and move the "needs ~5 hosts" /
">1 card at peak" throughput notes into the throughput or SLO column.

---

## Considered and excluded (verified not-new / not-a-defect)

These were checked deliberately and are **not** reported, to avoid false positives on a convergence pass:

- **FP8 vs 8-bit KV (~1.42 vs ~1.31 MB/token).** Used consistently — the book now distinguishes
  the vLLM-measured FP8 operative figure (1.42 MB, 54% of BF16) from the naive byte-halving lower bound
  (1.31 MB). ch05:36's "8-bit (~1.3 MB/token)" is the 8-bit byte-halving figure, consistent with ch07 §4
  item 4; no conflict. (P10-3 already fixed the stale 23.8 GB / 1.3 MB in book-architecture §14.)
- **ch09 "56 s" vs "98 s" all-reduce time.** Both are correct under their own framing: §2/§5 Common
  Mistake use the flat `bytes ÷ bandwidth` **lower bound** (140 GB/2.5 ≈ 56 s), while §3 Options use the
  **ring-adjusted** `2(N−1)/N·M` model (~98 s). The book states the flat-vs-ring distinction explicitly;
  not an inconsistency.
- **"The token layer" phrasing.** Now confined to ch01 (lines 35, 100), where it is self-referential
  to the token chapter; the non-token-chapter instances (ch02:160, ch04:225, ch05:159, ch07:171) were
  rewritten to "the unit-and-token work of Ch 1" (P10-7). No undefined abstraction leaks into other chapters.
- **Measurement §4 de-duplication.** ch04 §4, ch05 §4, ch06 §4, ch07 §4 now each restate only their own
  chapter-specific additions with a one-line cross-reference to Ch1 (P10-1 resolved; no verbatim triple remains).
- **ch09 vs ch10 gradient size (140 GB FP16 vs 280 GB FP32).** Reconcilsed via the explicit gradient-dType
  note in ch09 §3 (P10-6); both are correct for their stated dtype.
- **ch12 prefix-cache amortization 30%/50% & ~28K tok/s.** Now labeled **[HYPOTHESIS]** in §3, §8, and
  Table 12-1 (P10-5 resolved); no longer presented as measured.
- **ch12 candidate (a) "baseline" naming.** Now framed as the per-request-latency baseline with an explicit
  "not a capacity baseline" scope note (P10-11 resolved).
- **ch07 Fig 7.1 / Fig 7.2 "visual proof" wording.** Replaced with "illustrates the 8× reduction" (P10-12 resolved).
- **Canonical budget $15K.** Relabeled as a **per-host** ceiling with the multi-host ($75K–$350K/mo)
  reconciliation note (ch04 canonical box, ch12 §8) (P10-4 resolved).
- **Re-verified arithmetic** (sample): 2×70e9×9.2e3 ≈ 1.29 PFLOP; 140 GB/0.025 s ≈ 5.6 TB/s;
  989/3.35 ≈ 295 FLOP/byte ridge; 9,200 × 2.62 MB ≈ 24.1 GB / 9,500 × 2.62 MB ≈ 24.9 GB;
  ($1.20×9.2 + $2.00×0.3)/1000 ≈ $0.012; 92,000/0.00556 ≈ 16.5M tokens/$; 18/8.6 ≈ 2.1 req/s;
  0.99×0.8+0.01×5 ≈ 0.84 s. All consistent with the canonical set and across chapters.
- **Taxonomy bracket style** ([2°] DERIVED, [DERIVED: …], [1P: …], [2°: …]). Acceptable house variation
  where one axis is implied (sources.tex permits a single implied axis); not a defect.

---

*Conclusion: the 14 chapters have converged. Two MINOR reservations (P11-1, P11-2) that no prior pass
addressed; neither affects correctness, both are one-line edits. Recommend addressing them and
concluding the loop with zero outstanding items.*
