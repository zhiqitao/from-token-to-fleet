CH5-01 | P2 | chapter-05.md L62 | 'the 2×FLOP cost' → 'the ~4.8×FLOP cost (14.08 vs 2.94 GFLOP per 64-token query, Table 5-1)' | FIXED
CH5-02 | P2 | chapter-05.md L58, L62 | L58 split claim → 'can halve the index storage ... (encoder compute essentially unchanged)'; L62 '~2× case' → 'halves index storage (encoder compute ~unchanged)' | FIXED
CH5-03 | P2 | chapter-05.md L56 | Appended embedding-table scope caveat to Table 5-1 footnote before [DERIVED] | FIXED
CH5-04 | P2 | chapter-05.md L62, L64 | L62 '(reports span a few to ~15%…)' → '(an unverified prior … [HYPOTHESIS]…)'; L64 added same pair-quantification test to mpnet recommendation | FIXED
CH5-06 | P2 | chapter-05.md L149 | Rewrote Q* bullet to carry chapter's hedge (break-even workload/domain-specific, must be measured) | FIXED
CH5-07 | P2 | chapter-05.md L119 | Appended scope note: Q* omits recurring per-query prefill/retrieval saving → lower bound on fine-tuning case | FIXED
CH5-09 | P2 | chapter-05.md L89 | '1.2 s SLO line' → '1.2 s design budget'; '~0.12 s headroom … for prefill alone' → 'exactly the ~120 ms retrieval allocation, i.e. zero true headroom' | FIXED