# PASS-3 FIXER — Responses

### [P3-1] Ch12 164 vs 165 GB residency. SEVERITY: Minor (clarity). STATUS: FIXED.
Location: Ch12 §3 (memory/residency arithmetic summary, L24 + Table rows L83/84).
Problem: Ch12 states residency as "140 + 24 = 164 GB" while Ch7/Ch13 state "≈165 GB".
  A cross-chapter reader comparing them sees two values and may read it as drift.
  Investigation: both are correct, but at DIFFERENT context lengths. 140 + 24.1 GB KV
  @9.2K input = 164.1 -> 164 GB (Ch12); 140 + 24.9 GB KV @~9.5K max = 164.9 -> 165 GB
  (Ch7/13). The canonical residency (frozen) is 165 GB with KV sized at max context.
  Ch12 used the 9.2K-input KV without stating the basis.
Fix: Added explicit context-length label in Ch12: "KV (24 GB FP16 **at the 9.2K input
  context**)". Now the 164 (9.2K) vs 165 (9.5K max) values are unambiguous, not drift.
  Verified both values against canonical: 164.1@9.2K, 164.9@9.5K.

## Confirmation-review conclusion (whole-book cross-chapter consistency)
The PASS-3 confirmation reviewer scanned all 27 chapters + back matter anchored to
canonical-workload.yaml v2 and reported the canonical chain is largely clean:
KV per-token 2.62 MB/2.5 MiB; 140 GB weights; 24.1/24.9 GB KV; ~436 GB budget; 18/33
concurrent; 344 in-flight; 5 avg / 20 peak hosts; TTFT 1.08s; W 8.6s; fine-tune 1,120 GB
— all hold consistently, and the Ch13 server-tier fix is confirmed. The single-host-vs-fleet
framing is now consistent (no "one host serves the whole arrival" claims remain). The only
rounding nuance (Ch12 164 vs 165) is now context-labeled above.

## Objective audits this pass
- 0 LaTeX errors, 0 undefined, max overfull 19.09pt (<25 gate).
- All 41 figures at/above 7.5pt on-page floor.
- No markdown leaks; no remaining single-host-serves-everything claim (scan returned 0).
- Canonical values all present and internally consistent.
