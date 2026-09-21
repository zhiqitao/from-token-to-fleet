# PASS-15 — FINAL WHOLE-BOOK CONFIRMATION ('From Token to Fleet')

**Verdict: ONE genuinely NEW MINOR finding (ch11 reader-imperative); everything else in the
complete book is CONVERGED.** Not a full "zero" (a single unreported voice-hygiene item
surfaced on the integrated read), but the book is otherwise at convergence.

Scope: final whole-book gate over the COMPLETE source — `design/manuscript/chapter-01.md …
chapter-27.md` plus back matter (`render/latex/preface.tex`, `render/latex/backmatter/{
glossary,sources,references,worksheet}.tex`). Build under review:
`from-token-to-fleet-v20260913-full.pdf` (308pp). Objective: confirm the whole book has no
NEW comments so the review loop can exit. Both halves had independently reached zero
(ch01-14 = PASS-14, ch15-27 = PASS-13); this pass re-read the integrated book and checked
for NEW whole-book-level (cross-half) issues that isolated half-passes could not see.

---

## A. FINDINGS (genuinely NEW only)

### 1. [MINOR] ch11 §3 "Discrete Batching Wastes the GPU" — reader-imperative "Imagine…"

- **Location:** `design/manuscript/chapter-11/chapter-11.md:40` (opening line of the
  "Discrete Batching Wastes the GPU" subsection).
- **Text:** `Imagine naive **discrete (static) batching**: the server accumulates requests
  until a batch fills, then runs them to completion, then starts the next batch.`
- **Problem:** This is a reader-addressing imperative. The book's voice is strict
  investigative narration with **NO reader-address**, and the review loop's own
  operational standard (applied explicitly in the ch15-27 passes, PASS-12/PASS-13) banned
  "Consider…/Note that…/**Imagine…**" imperatives, confirming ZERO such forms in ch15-27
  and all back matter. ch11 is in the ch01-14 half, and none of the ch01-14 passes
  (PASS-7..14, which converged at zero) ever scanned for/flagged this construction — so it
  survived to the whole-book gate.
- **Why it matters:** Cross-half voice inconsistency. The same class of reader-imperative
  was actively eliminated on one side of the book and left in place on the other, so the
  voice is not uniform. A reader-address imperative ("Imagine…") also runs counter to the
  book's declared no-reader-address discipline.
- **Recommended change:** Recast as plain investigative narration. E.g. "Naive **discrete
  (static) batching** accumulates requests until a batch fills, then runs them to
  completion, then starts the next batch." (Drop the leading "Imagine"; the sentence then
  reads as a neutral mechanism description consistent with the surrounding prose.)
- Severity stays MINOR: single instance, cosmetic-to-voice, no technical or numerical
  error.

---

## B. What was verified this pass (in the SAME chapter/half that reported zero — re-checked
   on the integrated book, not re-reported)

The following apparent whole-book concerns were investigated and **confirmed NOT to be
issues**:

1. **ch04 "50 rps → ~24/34 hosts" vs the canonical 40 rps / ~20 hosts elsewhere — NOT an
   inconsistency.** The ch04 §8 mini-case is a deliberate *projection* to a larger company
   (5,000 employees, 10% concurrent → 500 users → 500 ÷ 10 s ≈ **50 rps**), not a
   contradicting statement of the canonical workload. It re-derives 50 rps from its own
   Little's-law step and then applies the same canonical per-host bound (`~2.1 req/s/host`,
   `~19,800 tok/s/host`, `C/W = 18 ÷ 8.6 s`, Ch 15–20) and the same Ch-8 prefill
   cross-check, so 24 hosts (KV/service-time) and ~23 hosts (prefill) agree at "the same
   order." The canonical peak of 40 rps is stated in the same chapter's Table 4-3 and used
   consistently everywhere else; the mini-case is internally coherent.

2. **Canonical-number consistency across the whole book** (the requirement for a FINAL
   convergence gate): verified consistent across ch01-27 for
   input=9,200 / output=300 tokens, dense 70B FP16 (~140 GB weights), KV 2.62 MB/token FP16
   (nominal 1.31 / measured 1.42 MB/token FP8 note retained and flagged), ~2.1 req/s/host,
   ~19,800 tok/s/host, 8×H100 host (~$20/hr, ~3.35 TB/s HBM), canonical peak 40 rps /
   average 10 rps. The host-count variants (~20 canonical; ~24/~34 only in the ch04
   mini-case projection; ~28/57/32 etc. in ch17's alternate table) all correspond to
   distinct, explicitly-scoped scenario branches, not drift.

3. **Cross-chapter references:** scripted scan of all "Chapter N / Ch N" references in
   ch01-27 → zero out-of-range pointers (all resolve to ch01-27; Ch 27 is Appendix A).
   Preface's claimed cross-refs verified present: Ch26 §2.1 workload-to-strategy decision
   matrix; Ch25 Architecture Decision Record; Ch22 decision loop (the "spine"); Appendix A
   dependence on Chs. 3, 7–11.

4. **Figure references:** all `![](...)` figure refs in all 27 chapters resolve to files in
   their per-chapter `figures/` dir; zero missing.

5. **Source/citation tags:** body `[S1]..[S6]` present with stable links in References
   (the apparent "missing" S2–S5 in a naive scan is a LaTeX-formatting artifact of the
   tag delimiters; entries are present). All figure/provenance/status tags balanced.

6. **Taxonomy:** no `[INTERPRETATION]`; all provenance × status pairs drawn from the five
   provenance (`[1P]`/`[canonical scenario]`/`[2°]`/`[LAB]`/`[ILLUSTRATIVE]`) × five status
   (`[FACT]`/`[DERIVED]`/`[ASSUMPTION]`/`[HYPOTHESIS]`/`[UNRESOLVED]`) scheme; the
   `[S#]`-is-not-provenance note in Sources/References and the single-axis house
   abbreviation are consistent.

7. **Reader-address sweep (whole book):** the only `you/your` occurrences are legitimate —
   ch23 answered/dialogue quotes (mini-case dialogue + mirror line), ch24 role-play /
   injection attack-string examples and a table cell, and `references.tex`'s
   "Attention Is All You Need" (a paper title). No genuine reader-address prose. The
   additional imperative scan (Consider/Note/Imagine/Picture/Let's) found only ch11:40
   ("Imagine…", item A.1) and the two legitimate mathematical "Let H be…/Let T be…"
   definitions (ch17:54, ch19:77) — the latter are standard notational conventions, not
   reader-address. "Recall the canonical workload…" is a consistent cross-reference
   connective used throughout, not flagged.

8. **Voice / glossary / preface / worksheet:** preface reads coherently and accurately
   promises what the book delivers; glossary covers the acronyms; worksheet line-12
   possessive (PASS-12) confirmed fixed; source-method, taxonomy, and unit conventions all
   agree. The glossary glossing prefill="the compute-bound pass" / decode="the
   bandwidth-bound pass" is a deliberate gloss whose qualification lives in the body; this
   was accepted in PASS-13 and is not re-raised.

---

## C. FINAL REMAINING-RISK ASSESSMENT

- **No remaining technical, numerical, structural, evidential, or cross-reference risk.**
  The complete book's arithmetic, canonical scenario, cross-references, taxonomy, figures,
  and back matter all cohere.
- **Single remaining item:** the ch11:40 reader-imperative "Imagine…" (MINOR, voice). It is
  small, localized, and the only reason this is not a clean "zero" at the whole-book level.
- **Loop state:** with this one MINOR item addressed (a 3-word recast), the whole book is at
  convergence. Convergence trajectory overall: the half-passes both hit zero, and the
  integrated read surfaced exactly one cross-half voice item. No chapter or
  conceptual-transition region remains that needs another substantive pass.
