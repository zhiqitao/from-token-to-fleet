# Architecture Worksheet — machine-readable companion (from *From Token to Fleet*)

This is the fillable/duplicable counterpart to the book's *Architecture Worksheet*
(back matter, Rows 1–8). Use it when you want to record an architecture decision
in a form that can be diffed, versioned, or reused. A practitioner can copy this
file, fill the `answer` column, and keep it with the corresponding ADR.

The same eight rows mirror the worksheet in the book:
Row 1 Requirement, Row 2 Workload, Row 3 Model, Row 4 Compute & memory,
Row 5 Architecture implication, Row 6 Decision record, Row 7 Validation &
operations, Row 8 Economics, reliability & recovery.

| row | field | answer | evidence / source |
|---|---|---|---|
| 1 | Business objective |  |  |
| 1 | Constraints (privacy, region, ops, budget) |  |  |
| 2 | Registered users (or seats) |  |  |
| 2 | Concurrency (% active) |  |  |
| 2 | Average request rate (rps) |  |  |
| 2 | Peak request rate (rps) |  |  |
| 2 | Input tokens / request |  |  |
| 2 | Output tokens / request |  |  |
| 2 | TTFT budget / SLO |  |  |
| 2 | TPOT budget / SLO |  |  |
| 3 | Model class (dense / MoE, total params) |  |  |
| 3 | Active params / token |  |  |
| 3 | Weight precision; bytes/param |  |  |
| 3 | Weight residency |  |  |
| 3 | KV precision; KV per token |  |  |
| 3 | KV residency (weights + KV) |  |  |
| 4 | FLOPs / token (prefill, decode) |  |  |
| 4 | Arithmetic intensity (FLOP/byte) |  |  |
| 4 | Ridge point of the hardware |  |  |
| 4 | Compute- or memory-bound? |  |  |
| 4 | MFU (measured) |  |  |
| 5 | So the architecture does X, and not Y, because |  |  |
| 5 | Parallelization strategy |  |  |
| 5 | Batching / serving choices |  |  |
| 6 | Decision |  |  |
| 6 | Alternatives rejected (and why) |  |  |
| 6 | Consequences / monitoring to add |  |  |
| 7 | Quality acceptance metric (eval set; pass/fail threshold) |  |  |
| 7 | Benchmark result (which suite / harness) |  |  |
| 7 | p95 / p99 latency at target load |  |  |
| 7 | Cost per 1M tokens (or per request) |  |  |
| 7 | Failure mode observed |  |  |
| 7 | Monitoring trigger (when to page) |  |  |
| 7 | Revalidation date |  |  |
| 8 | Burst policy (what peak demand is shaped / queued vs served) |  |  |
| 8 | Failure scenario assumed and capacity reserved (N−1, spare) |  |  |
| 8 | Pricing basis: $/GPU-hr, depreciation, ops, power |  |  |
| 8 | Fully-loaded monthly fleet cost (peak and average) |  |  |
| 8 | Availability / SLO error budget (target 9s) |  |  |
| 8 | Test-load trace ID (recorded load generator config) |  |  |
| 8 | Rollback trigger (when to revert the decision) |  |  |
| 8 | ADR reference (which decision record / date) |  |  |
