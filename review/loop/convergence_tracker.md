# Loop-to-convergence tracker (user: run for ~10 passes, stop at zero new findings)

Method: each loop = (1) independent re-review of the CURRENT rebuilt PDF per the 55-section
standard by parallel chapter reviewers; (2) trust-but-verify each finding against source;
(3) fix EVERYTHING incl. suggestion-level; (4) figure fixes; (5) rebuild; (6) record new-findings
count. Convergence = a pass that returns 0 new findings across ALL chapter halves + back matter.

| Pass | Date | Reviewers | New findings (C/M/Mod/Min) | Artifact | State |
|------|------|-----------|---------------------------|----------|-------|
| Loop1 2026-10-25 | ch1-6+front, ch7-12, ch13-18, ch19-27+bm | 5 C / 13 M / ... | loop1_findings_*.md | REVIEWED; fixes in flight |
| Loop2 | — | — | — | pending |
| Loop3 | — | — | — | pending |
| Loop4 | — | — | — | pending |
| Loop5 | — | — | — | pending |
| Loop6 | — | — | — | pending |
| Loop7 | — | — | — | pending |
| Loop8 | — | — | — | pending |
| Loop9 | — | — | — | pending |
| Loop10 | — | — | — | pending |

Exit condition: a pass returns 0 new findings across ch1-6, ch7-12, ch13-18, ch19-27+backmatter.
Do not stop early; a single "no new findings" on one half is not the exit signal.

## Loop 1 known totals (per reviewers)
- ch1-6+frontmatter: 5 CRITICAL, 11 MAJOR, 28 MODERATE, 29 MINOR (73)
- ch7-12: 0 C, 0 M, 21 MODERATE, 17 MINOR (38)
- ch13-18: 0 C, 2 MAJOR, 7 MODERATE, 13 MINOR (22)
- ch19-27+backmatter: 0 C, 2 MAJOR, 6 MODERATE, 5 MINOR (13)
- Total: 5 C, 15 MAJOR, 62 MODERATE, 64 MINOR (~146 findings)

## Loop 1 fixes status
- Committed `9217637d`: ch1 LLaMA dim, ch5 MiniLM params, ch3 unit collision, ch6 broken
  sentence, ch13 per-host rps, ch15 O(L), ch11 taxonomy cross-ref.
- In flight (5 subagents): ch7-8, ch15-18, ch19-27+backmatter, ch9-16 voice/cross-ref, ch1-6
  taxonomy harmonization.
- Still to do after they land: figure-font fixes (Fig 1.2 5.6pt, Fig 2.1 5.9pt, Fig 3.1/6.1
  7.8pt), frontmatter/cover nit reports, then rebuild + Loop 2.
