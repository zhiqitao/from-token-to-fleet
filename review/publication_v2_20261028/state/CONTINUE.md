# CONTINUE.md — resumable handoff (autonomous loop)

Repo: /home/ubuntu/hermes-work/from-token-to-fleet
Updated: 2026-10-31
Current verdict: **RELEASE CANDIDATE** (R30). Publication approval FALSE (external gates).

## Working model (user-directed, 2026-10-31)
- **Main agent (DeepSeek-V4-Flash) = reviewer/auditor.** I conduct the review myself: recompute key derivations, cross-chapter consistency, figure legibility (min >=8pt), source/provenance discipline, content-loss scan. I do NOT delegate detection to subagents.
- **MiMo-2.6-Flash-RL (im-eglb/EGLB) = fixer.** I dispatch MiMo subagents to fix the issues I find. Iterate: I review -> MiMo fixes -> rebuild -> I re-review, until I find nothing further.
- Delegation: `im-eglb` / `MiMo-V2.6-Flash-RL`, 6 children, 32768 tokens.

## Release candidate
- **R30**: `review/publication_v2_20261028/work/accelerated_external_review_proof_r30/render/build/from-token-to-fleet-v20260913.pdf`
  SHA `6dfc1479…`, 425 pp, US Letter, tagged, **0 Type3**, all figs >=8pt. origin/main HEAD `3ab5b5f6`.
- Round history R27->R30 all pushed; all prior external-review + independent-audit P0/P1 CLOSED.

## MiMo audit of R30 (deleg_51b5c14e): "one fix round's findings" — fix batch IN FLIGHT (deleg_4a305c28)
- **P2**: MiMo-2001 (Ch13 100rps -> ~74 hosts; 'well under ceiling' false); MiMo-2002 (Ch25 32 KV heads -> 64 to match 2.62 MB/token).
- **P2 figure**: MiMo-F001 (A.4 contrast 3.47:1 -> >=4.5:1), F002 (21.1 arrowhead), F003 (7.5 9.5K/10K), F004 (23.1 connectors), F005 (16.1 grayscale band).
- **P3**: MiMo-0001 (Ch15 MFU 38%->62%), MiMo-2003 (19.6 ref), 2004 (5.1 ref), 2005 (Ch6 p99 5.0s), 2006 (Ch20 mean-vs-bound), 2007 (Ch15 section numbering).
- **Source**: C04 (habana snapshot-pin), C05 (ch9 5 refs), C13 (gloo 'backend'), C18 (GLM 131K), C23 (A-S02 shell).
- MiMo arithmetic = 94/96 PASS, 0 new P0/P1. Findings: review/publication_v2_20261028/audit/mimo-*-r30.md.

## NEXT EXACT COMMANDS
1. Integrate deleg_4a305c28 (MiMo fixes) -> freeze/build **R31** (`freeze_r31_loop5.py` + `run_frozen_build_guarded.py`). Verify structure tree / 0 Type3 / >=8pt / fig contrast.
2. **I (DeepSeek) audit R31 myself** (recompute, cross-ref, fig legibility, content-loss). Dispatch MiMo to fix any finding. Iterate until I find nothing.
3. On convergence: publishing-readiness.md -> hand to author for print proof + sign-off.
4. Push each round to origin/main.

## External / blocked (keep OPEN, do NOT mark passed)
- veraPDF/PAC PDF-1 cert (not installed) -> `pdfuaid:part` held.
- font/image rights manifest, ISBN, physical print proof, author sign-off.
- exact original 362pp canonical not recoverable; live canonical preserved (`82006201…`).
- IX/T3-table HOLD (Ch11 Table 11-2). 4 heading-skips (ch09/10/15). FTF-R06 multi-region GATE.

## Build guard
Always build via `run_frozen_build_guarded.py <proof> --run` (rejects live/completed, protects live canonical). Never `bash render/build.sh` live.
