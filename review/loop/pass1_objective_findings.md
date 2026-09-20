# PASS-1 REVIEWER — OBJECTIVE FINDINGS v2

Combined objective/programmatic/visual findings. Chapter deep-read findings from 4 subagents are
added when they complete (separate section below).

## FIGURE LEGIBILITY (on-page font floor 7.5pt)
- Fig 9.1: axis ticks 7.28pt — MAJOR
- Fig 10.1: sub-labels 5.79-7.44pt ("composition" 5.79, annotation 6.61) — MAJOR
- Fig 15.1: FlashAttention labels 6.97-7.68pt — MAJOR
- Fig 16.1: legend/annotations 6.22-7.0pt, cramped leading — MAJOR
- Fig 19.1: state ids 6.53pt + three crossing egress connectors from Decide (reading-order ambiguity) — MAJOR
- Fig 8.1: 7.48-7.8pt — MODERATE
- Fig 19.2: axis ticks 7.16pt — MODERATE
- Fig 7.1: 7.57pt — OK (at floor)

## GLOSSARY (§43): load-bearing terms OMITTED
The 21-entry glossary omits several terms the body relies on heavily and that are figure/mechanism
subjects:
- FlashAttention (Ch15 whole figure)
- PagedAttention (Ch11 serving mechanism)
- continuous batching
- arithmetic intensity / roofline / ridge point
- MoE (used heavily ch3/10/18/21)
- HBM / memory hierarchy
Recommended: add these (or a "mechanisms" group) with accurate definitions consistent with body usage.
Severity: MODERATE.

## MINOR
- Preface figures are numbered "figure 1"/"figure 2" (plain integers) while all body figures use
  "N.N" (1.1, 1.2...). Minor numbering-scheme inconsistency. Severity: MINOR.

## OBJECTIVE AUDITS — CLEAN
- All figures within margins; no overflow.
- 41 figures, all in LOF = all in body captions; no dup/gap.
- All prose "Figure N.M" refs resolve; chapter refs in-range; no dangling promises.
- No orphaned headings; no figure captions split to next page.
- Canonical numbers consistent across book (TTFT 1.08s, W 8.6s, 344 in-flight, 20 hosts,
  2.62 MB/token FP16; derivations verified: 2x80x64x128x2=2.62MB).
- Terminology consistent (KV cache no hyphen, prefill/pre-fill, no best/go-to engine claims).
- Voice-hygiene: 0 narrator violations (fixed prior pass).
- Evidence labels comply with 2-axis taxonomy; [PROVEN] absent; [INTERPRETATION] removed.
- Source URLs all resolve (200).
- No placeholder/debug text; no caption prefix duplication.
- "What We Still Don't Know" sections carry genuine uncertainty.
- Ch8 mini-case genuinely requires reasoning (corrects "reach for a roofline" misconception).
