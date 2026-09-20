# PASS-2 FIXER — Responses to PASS-2 review comments

## High-severity finding (from ch10-18 deep-read; verified and fixed)

### [P2-1] Ch13 single-host-vs-fleet contradiction. SEVERITY: High. STATUS: FIXED.
Location: Ch13 §3 Worked Example (lines 39-45) + §5 Common Mistakes.
Problem: Ch13 §3 asserted "a single 8×H100 server is the right archetype" for the canonical
  workload, citing Ch11's single-host TTFT result. But Ch16/17 prove the canonical 40 rps peak
  requires ~20 hosts (344 in-flight / ~18 KV-resident per host). Ch11 was already correctly
  scoped (its mini-case is explicitly "latency-bound, single-host"), but Ch13 §3 still carried
  the unsharded "single host is the right archetype" claim — a genuine cross-chapter
  contradiction.
Fix: Re-scoped Ch13 §3 to distinguish the two axes: the server tier is the right
  *model-residency* archetype (model + KV fit one node; per-request TTFT SLO met), while
  explicitly stating the single host is NOT capacity-sufficient at the 40 rps peak (~20 hosts
  per Ch16/17). Also scoped the §5 Common-Mistakes "hyperscale before measuring goodput"
  bullet to note the canonical workload *does* outgrow one host at peak, so the fleet is
  warranted there. Verified against Ch16/17 arithmetic (344 in-flight, ~20 hosts).

## Verified-clean (no action) — from deep-reads
- task-0 (ch1-9): canonical-number chain internally consistent across all nine chapters
  (70B/FP16 -> 140 GB; 2.62 MB/token full-MHA -> 24.1 GB @9.2K). Ch1 KV formula intentionally
  generic (defers to Ch7), verified non-defect.
- task-2 (ch19-27 + back matter): PASS-1 fixes confirmed present (glossary expanded; ADR
  template single '## Decision' + placeholder; no bracketed [INTERPRETATION]); Appendix A [1P]
  tagged/dated; canonical numbers consistent (Ch7/8/15/17 values).

## Objective audits this pass
- All 41 figures at/above 7.5pt on-page floor.
- No markdown leaks; no new overfull >25pt; 0 LaTeX errors.
- Glossary additions render correctly.
- Voice-hygiene: no new narrator-address violations (only "single most X" rhetorical emphases
  retained per "do not manufacture problems" - fine in a practitioner book).
- Canonical arithmetic re-verified: I(3)=12,095; KV 31.7GB; in-flight 344; ~20 hosts.
- Ch16 power decomposition verified (~$1.1K/mo/host, ~$22K/mo for 20 hosts).
