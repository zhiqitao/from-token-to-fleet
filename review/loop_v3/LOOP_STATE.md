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
| 4 | IN PROGRESS (text 23/24, vision 22/44; MiMo c3 + 3× vision running) | merged.json run once (stale, rerun after data) | pending | pending | pending | pending | — |
| 5–14 | not started | | | | | | |

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