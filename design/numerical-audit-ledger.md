# Numerical Audit Ledger — v20260830 systemic review
# Source of truth: design/canonical-workload.yaml + render/canonical_calc.py
# Canonical anchors: KV/token FP16 = 2.62 MB exact / 2.5 MB book-rounded;
#   weights 70B FP16 = 140 GB; 8xH100 = 640 GB; usable ~512 GB.
#
# STATUS 2026-08-30: All P0 items below RESOLVED + verified in rebuilt PDF
# (226 pp, 0 unresolved refs). Ch15 MFU+KV rebuilt, ch8 weight-read fixed,
# ch17 fleet rebuilt from canonical KV, ch18 request-level routing, ch19
# execution-trace + Table 19-1 populated, ch9/ch10 parallelism clarified,
# ch16 TCO parameterized, ch20 250QPS marked ILLUSTRATIVE. See git log.

## CONFIRMED P0 (off-canonical, must rebuild)
### ch15
- [ ] KV per token written as `2 x 8192 x 2 = 32 KB` (per-LAYER only; missing x80 layers)
      -> canonical 2 x 80 x 8192 x 2 = 2.62 MB/token. Downstream 304 MB/user & 30.4 GB/100 users wrong by ~80x.
- [ ] MFU = 6.6 (>1.0 = impossible). Loss-denominator & arithmetic must be rebuilt;
      never present a utilization ratio >1. Distinguish model FLOPs vs measured device FLOPs, batching, parallelism.
### ch17
- [ ] kappa = 128 bytes/token incompatible with canonical 70B/80L/8192d (off by ~20,000x).
      512 GB / 128 B = 4.2e9 tokens correct arithmetic, but described as ~440 concurrent -> wrong;
      ~440/330 concurrent + five-host recommendation must be rebuilt from canonical KV.
### ch8
- [ ] Weight reads stated as `2 x 70e9 x 2 B = 280 GB` (double-counts 140 GB FP16 weights).
      Single weight read = 140 GB. Rebuild FLOP/byte example accordingly.
### ch18
- [ ] Routes arbitrary portions of a request's INPUT tokens to different models (70% in-tokens ->A, all 300 out ->D).
      Ordinary request-level routing sends a WHOLE request to one model. Reframe as 70% of REQUESTS ->A etc.
### ch19
- [ ] 14-17 GB/request memory figures derived from ch15's wrong KV. Rebuild from canonical 24.7 GB/request KV.
- [ ] "one turn = one LLM inference + one tool call" stated as general -> reframe as one simplified execution model;
      define execution trace (model invocations / tool calls / observations / amplification).
### ch20
- [ ] "250 QPS/host, 16ms median, 40ms p99" hard-coded as if universal -> label ILLUSTRATIVE benchmark hypothesis.

## SECONDARY (structural / labeling)
### ch7
- [ ] (review: 164-165 GB does NOT fit 2x80GB=160GB HBM with runtime headroom) -- already flagged; 2xH100 needs runtime reserve.
### ch16
- [ ] TCO inputs ($3.50/hr, 50kW, $0.15/kWh, $120K staff...) -> move to explicit scenario parameter table; already [2 deg illustrative] in part.
### ch4
- [ ] 5% concurrency / 10s duration presented as workload property -> make explicit assumptions (population vs active vs arrival).
### quality
- [ ] "85% factual accuracy" too coarse -> decompose into multidimensional acceptance criteria.
### general
- [ ] Some illustrative numbers labeled DERIVED -> add ILLUSTRATIVE as 5th evidence category.
- [ ] KV hidden-dim used where GQA/MQA needs H_kv x D_head -> teach general formula 2*L*H_kv*D_head*bytes early (ch7 already covers).
- [ ] unit-check discipline: every worked example gets quantity/unit/formula/substitution/result/sanity.

## Scope note
Freeze prose. Fix the quantitative spine from canonical, propagate, label ILLUSTRATIVE,
then rebuild PDF. Do NOT patch numbers independently of the canonical set.
