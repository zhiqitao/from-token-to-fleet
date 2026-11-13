# Round 4 — Disposition ledger (653 findings, 4-model panel)

Method: quote-presence triage (315 text: 303 PRESENT / 12 ABSENT) -> per-item
independent re-verification by subagent (source grep + arithmetic recompute for
text; 110dpi rendered-page re-inspection + pdftotext for vision) -> four-way
verdict. Every verdict file passed the acceptance gate (count match, allowed
verdict enum, CONFIRMED carries fix_instruction, evidence non-empty).

## Totals

| kind | CONFIRMED | FALSE_POSITIVE | DEFENSIBLE | total |
|---|---|---|---|---|
| text | 166 | 37 | 112 | 315 |
| vision | 120 | 143 | 75 | 338 |
| **all** | **286** | **180** | **187** | **653** |

FP rate: text 11.7%, vision 42.3% (calibration confirmed: vision findings are
glyph-misread prone; all were re-checked on the rendered page before verdict).

## Fix queue

286 CONFIRMED -> 278 unique after cross-model dedup (8 collapsed) ->
77 chunks in 27 conflict-free waves (no two chunks in a wave touch the same
file; figure chunks capped at 4 items). Chunk files: fix/fix_wNNbMM.json;
responses: fix/fix_wNNbMM_responses.md.

## Cross-model signals

- 8 findings found by >=2 models (merged.json common); all involved MiniMax.
- discuss stage (compact register): 12 prompt edits saved in
  ../prompt_edits_r4.json for the round-5 review prompt.
