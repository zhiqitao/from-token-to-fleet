# CONTINUE.md — resumable handoff (autonomous loop)

Repo: /home/ubuntu/hermes-work/from-token-to-fleet
Updated: 2026-10-30
Current verdict: **RELEASE CANDIDATE** (R28). Publication approval FALSE (external gates).

## Current release candidate
- **R28**: `review/publication_v2_20261028/work/accelerated_external_review_proof_r28/render/build/from-token-to-fleet-v20260913.pdf`
  SHA `adff9250d74d19ac7d68d886781f441df2907588c788c228260d36169b8ecd2b`, 425 pp, 291 inputs, 14 overlays.
- Round-2 loop fixes integrated + verified: FTF-N01 (renderer content-loss, NBSP on `^[LABEL]:` callouts), Ch4 D1(26/37)+N02(3.3M), Ch5 N06+N04, Ch6 N04+Fig6.2 caption, Ch15 N03(NFU cap 56K — 70,000=124% MFU impossible)+N04+N05+N07, Ch17/20 range→`35,000–56,000`, Ch27 R10 immutable commit pinning, Figs 22.1(7.79→8.17pt)/26.2(7.60→8.60pt). Structure tree intact (H2 264/H3 102/H4 28, 58/58 fig alt, 0 orphan, 0 Type3, TOCI 95), no overfull, fail-loud checks passed (build exit0), release artifacts refreshed (EPUB 2026-10-31, cover wrap 18.21×11.25in 0.96in spine for 425pp).
- Issue ledger: `review/publication_v2_20261028/issue-ledger.md` — all round-2 independent-audit P0/P1 CLOSED.

## Remaining open
- **fig-P2** (16 figures): 16.1 annotation leaders/feasible-max box, 18.1 arrows/else, 19.2 legend/pattern, 19.3 y-axis/units, 21.1 feedback arrow/grayscale, 22.1 N reuse/red dot, 7.5 9.5K@10K, 15.2 plateau, 10.1 hatch/solid, 12.1 redundant arrow, 23.1 triangle, 25.1 arrow short, 2.2, 2 color-only, 7.8/11.1 grayscale, A.2/A.4.
- FTF-N08 (Ch22 rps wording), FTF-N09 (Ch23 Table 23-1 cost row), D2–D7 LOW (40.2→40.1, W(3)13.9, Ch19 formula-vs-table, prefill ~24, α(T=2) 1.12/1.18, Ch9 15.6h), P3 N10–N19 + 34 fig polish.

## External / blocked (keep OPEN, do NOT mark passed)
- veraPDF/PAC PDF-1 cert (not installed) → `pdfuaid:part` held.
- font/image rights manifest, ISBN, physical print proof, author sign-off.
- exact original 362pp canonical not recoverable; live canonical preserved (`82006201…`).
- IX/T3-table HOLD (Ch11 Table 11-2). 4 heading-skips (ch09/10/15) — veraPDF warning-level. FTF-R06 multi-region GATE.

## Delegation
- provider=qwen38/Qwen3.8-27B (tailscale 100.105.225.59:30000), 6 children, 32768 tokens (set 2026-10-30 per user).

## NEXT EXACT COMMANDS
1. Round-3: fix fig-P2 batch + FTF-N08/N09 + D2–D7 (each verify-before-edit), then rebuild R29 via a new freeze script + `run_frozen_build_guarded.py`.
2. Or converge: if a fresh independent re-audit returns 0 new P0/P1 and only cosmetic P3, declare release candidate & hand to author for print proof + sign-off.

## Build guard
Always build via `run_frozen_build_guarded.py <proof> --run` (rejects live/completed, protects live canonical). Never `bash render/build.sh` in the live repo.
