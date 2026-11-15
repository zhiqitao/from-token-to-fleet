# loop_v3 — multi-round review loop state (main driver)

Directive (user, 2026-11-10): run the review loop for **10 more rounds or stop
earlier at convergence**. This file is the durable state; the main driver
updates it at every phase transition.

## Round ledger

| round | data | merge | discuss | disposition | fixes | rebuild | verdict |
|---|---|---|---|---|---|---|---|
| 1 | DONE | DONE | — | DONE (round_2 triage) | DONE | — | 184→111 fixes/73 rejects lineage |
| 2 | DONE | DONE | — | DONE | DONE | — | closed |
| 3 | DONE | DONE | — | DONE | DONE | DONE (462pp, 4 gates green) | close-out commits e186c904/51f818b8/05e48956 |
| 4 | DONE (653 findings: text 315 + vision 338) | DONE (common 8/unique 637) | DONE (compact register; 12 prompt edits saved) | DONE (286 CONFIRMED / 180 FP / 187 DEFENSIBLE; ledger disposition.md) | DONE (278 deduped → 245 applied / 17 skipped-premise / 17 duplicates; 77 chunks) | DONE (486pp, all gates green; commits fdc95be5 + 1f2a1473) | closed; round 5 data in flight |
| 5 | DONE (823 findings: text 450 + vision 373; 72/72 clean files via effort ladder + max_tokens=262144 for MiniMax 1M ctx) | DONE (common 21/unique 802) | DONE (compact register 102/40K; 4/4; prompt_edits_r5.json) | DONE (341 CONFIRMED / 242 FP / 239 DEFENSIBLE / 1 UNVERIFIABLE; 42/42 batches gate 0 problems; ledger disposition.md) | DONE (292 deduped → 189 applied / 58 skipped-premise / 45 duplicates / 0 needs-regen; 13 packs; commit 910aa565) | DONE (497pp tagged + plain green, all audits; 89 vision pages re-rendered; commits 910aa565 + d438ac05) | closed; NOT converged (292 CONFIRMED > 0) → round 6 required |
| 6–14 | next: DATA (panel: DS/MiniMax alternating as delegate backends per user directive 2026-11-14) | | | | | | |

Panel: MiMo-V2.6-Flash-RL, DeepSeek-V4.1-Flash, Qwen3.8-27B,
MiniMax-M3.1-Flash (new, joined r4). All im-eglb/qwen38, reasoning_effort=max.

## Per-round cycle (repeat R = 4, 5, ... 14)

1. **DATA** — `render/review_loop.py text R <model>` (6 chunks, whole manuscript
   md) + `vision R <model>` (11 batches, 87 figure pages at 150 dpi from the
   CURRENT built PDF). After any rebuild: re-render pages + manifest
   (`render/render_fig_pages.py`, `render/make_manifest.py`) BEFORE dispatching
   vision, or reviewers read stale pages.
2. **MERGE** — `review_loop.py merge R` → `round_R/merged.json` (common ≥2 models
   vs unique).
3. **DISCUSS** — `review_loop.py discuss R` → per-model false-positive /
   adjudication / prompt-edit JSON.
4. **DISPOSITION** — quote-presence triage (round-3 method: triage.json PRESENT/
   ABSENT; ABSENT quote = fabricated unless flexible search finds a paraphrase),
   then independent re-verification (source grep + arithmetic recompute) per item.
   Every finding → CONFIRMED / FALSE POSITIVE / DEFENSIBLE. Ledger:
   `round_R/disposition.md`. Vision findings are LEADS ONLY (MiniMax r4
   calibration: 4/4 P0 + 2/2 sampled P1 vision findings were glyph misreads) —
   each must be re-checked on the rendered page before any fix.
5. **FIX** — subagent fan-out, ≤7 items per fixer, disjoint chapter files;
   fixer writes edits + `round_R/responses.md` (Severity | Location | Problem |
   Why | Change | Status | Response). Check `git status` before re-dispatch
   (a dead batch may have landed partial edits).
6. **REBUILD** — `render/build.sh` → new PDF; verify page count, gates,
   programmatic audits (stranding detector, NUL/tofu, raw-^{, font floor,
   cross-ref integrity) on the CURRENT build.
7. **RE-RENDER** pages/manifest for the next round's vision stage.
8. **CONVERGENCE CHECK** — if disposition found **0 CONFIRMED actionable
   fixes** in the round → STOP (converged). Else R+1, hard cap R=14.

## Anti-patterns (from skill)

- Never trust a reviewer verdict: text-layer check disproves vision claims;
  raster check disproves text-layer claims about figures.
- Error files (`[[ERR ...]]`, 44 bytes) block re-runs — delete before re-dispatch.
- im-eglb model list and health are volatile — probe before each data dispatch.
- A finding not reproducible in the CURRENT build is closed, not a to-do.
- Re-verify prior-pass fixes each round (a rebuild can re-introduce them).

## Log

- 2026-11-10: directive received. Round 4 data collection in flight (driven by a
  parallel process; this driver does NOT duplicate data dispatches — it
  reconciles and takes over from merge onward). MiniMax r4 pass complete and
  committed f0f19dad (375 findings; 4/4 P0 disproved).
- 2026-11-13: ROUND 4 CLOSED. Disposition 653 → 286 CONFIRMED (dedup 278) →
  fix fan-out 245 applied / 17 skipped-premise / 17 duplicates (77 chunks,
  13 packs, responses in disposition/fix/*_responses.md). Rebuild hit a tagpdf
  para-hook failure root-caused by bisect to ch25: the ADR-template heading
  merged onto one long line triggered fancyvrb breaklines inside Verbatim,
  which desyncs tagpdf hooks — fix = split at the semicolon (wording kept).
  486pp tagged + plain builds green (tables/leaks/regressions/stale-values/
  3× lualatex/fig-struct/pdf-meta). PITFALL: system python3 has no pymupdf;
  build meta steps (fix_fig_struct/fix_pdf_meta/render_fig_pages) need
  /home/ubuntu/.hermes/hermes-agent/venv/bin/python3 (pyshim on PATH works).
  COORDINATION: parallel process owns DATA (relaunched vision 5 after a
  stale-pages kill); this driver re-rendered pages/manifest post-rebuild and
  owns merge onward. text c0 was an ERR stub during the md-race — verify/fill
  before merge.
- 2026-11-15: ROUND 5 CLOSED (second, independent disposition — this session's
  847-unique verification track): 849 collected -> 847 unique -> 847 verified
  by 5 read-only waves (528 ACCEPT / 155 ACCEPT-PARTIAL / 164 REJECT; both P0
  REJECT) -> 683 fixable -> 27 per-chapter batches + 1 cross-chapter batch ->
  494 FIXED / 189 ALREADY-FIXED (parallel's 189-fix pass) / 0 BLOCKED;
  responses.md 847 rows; gap_ledger.json fix_status written. Rebuild 501pp
  (497->501 from post-d438ac05 fixes) all gates green, SAME-LINE overlap 0
  (fixed Table 15-1 col-6 header overflow: soft hyphen in "parameter-matmul",
  introduced by 910aa565 header rename). Commit de040ac2 pushed. FIX BACKENDS:
  user directive 2026-11-14 — delegate subagents alternate DeepSeek-V4.1-Flash
  and MiniMax-M3.1-Flash (im-eglb); MiniMax delegate backend DOWN 2026-11-15
  ~00:00-07:30 (6 casualties: ch18/21/22/23/25/26 all re-dispatched on DS,
  zero-loss or partial-resume). R6 data (parallel-driven) in flight.