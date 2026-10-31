# ch456 — FTF-N04（Ch5/Ch6 侧：单流 50 tok/s vs Ch15 8,000 tok/s 口径）— Ch5/6 侧 FIXED，Ch15 侧 OPEN

- 范围：`chapter-05.md:93`（对账注）、`chapter-06.md:62`（goodput 例）。**Ch15 不在本任务授权内，未改。**
- 状态：**Ch5/Ch6 侧 FIXED；Ch15 侧 OPEN（需 Ch15 owner）**。

## 复算（before）

| 检查 | 算式 | 结果 |
|---|---|---|
| 规范 batch-1 decode | 1 ÷ 25 ms/token（Ch2/Ch5 TPOT 预算） | **40 tok/s** → 50 tok/s 与之一致（单流/低 batch） |
| 8,000 tok/s 若作 batch-1 decode 所需带宽 | 140 GB × 8,000 | **1,120 TB/s** |
| 8×H100 聚合 HBM | 8 × 3.35 TB/s | **26.8 TB/s** → 超 **41.8×**，不可能 |
| 8,000 的真实来源 | 9,200 ÷ 1.08 s | **8,519 ≈ 8.5K** = Ch4:167 明写的 "≈8.5K tokens/s prefill" |

结论：**50 tok/s = 单流 decode；8,000 tok/s = prefill 侧/整请求摊薄速率；35,000–70,000 = 批处理 serving 吞吐** —— 三者是不同工况，不是同一量的两个值。原 Ch5 对账注把 8,000 同时称作 "raw batch-1" 和 "multi-request serving throughput"，自相矛盾且与 40 tok/s 的规范 batch-1 冲突。

## 修复（仅标注口径，未改任何数字）

1. **Ch5:93**：删去 "raw batch-1 ≈ 8,000" 的错误标注，改为 "8,000 = prefill-side / whole-request rate（Ch4 ≈8.5K prefill = 9,200 ÷ ~1.08 s；batch-1 decode 在 25 ms/token 下是 ~40 tok/s, Ch2）"，并显式写明 "50（单流 decode）与 8,000（prefill 侧）是同一主机的不同 phase，不是同一量的两个值"。`[ILLUSTRATIVE][DERIVED]` 结尾标签保留。
2. **Ch6:62**：给 50→70 tok/s 加口径标注（Ch5 单流/低 batch 基准 = floor，非主机 aggregate serving rate；Ch15 的 8,000 是 prefill 侧、35,000–70,000 才是批处理 serving）。50 / 70 / 1.8 / 2.3 / 2 s / 20 / 40% / 96% / 94% / 48 / 65.8 等原有数字全部未动。

**文件**: `design/manuscript/chapter-05/chapter-05.md`

- sha256 **before**: `f35d5e73c19a057c4c438853f1e206ff4922aff1c97fa72b659cbdfc783b7ad8`
- sha256 **after**: `376a07d6f2e87a61b6ba63f7518e62b1fea3d56296edf8bb72629d9a1204343e`

**精确 diff**:

```diff
--- a/design/manuscript/chapter-05/chapter-05.md
+++ b/design/manuscript/chapter-05/chapter-05.md
@@ -91,5 +91,5 @@
 [ILLUSTRATIVE][DERIVED]: tokens/s per dollar for generation. On‑demand H100 list price ~$2.50/hour per GPU → 8×H100 = $20/hour. At ~50 tok/s aggregate throughput, the effective cost is ~0.40 $/tok/s, or equivalently ~2.5 tokens/s per dollar-hour. In tokens‑per‑dollar terms: 50 tok/s × 3600 s/hr ÷ $20/hr = 9,000 tokens per dollar per hour of runtime.
 
-> **Economics unit note (reconciliation with Ch. 4 and Ch. 15).** Both chapters use the same on-demand price basis: ~$2.50/hr per H100 → ~$20/hr per 8×H100 host. Two things must be kept straight. First, *units*: this chapter expresses **tokens per dollar-hour** (token-rate × 3600 s ÷ hourly cost), while Chapter 4 expresses **tokens per second per dollar** (token-rate ÷ per-second cost); convert by ÷3600. Second, *throughput basis*: the ~50 tok/s used here is a deliberately **conservative single-stream / low-batch generation rate** adopted to illustrate the per-dollar *method*, **not** a claim about the host's batched serving throughput. Chapter 15's measured-range figure (raw batch-1 ≈ 8,000 tok/s rising to ~35,000–70,000 tok/s under FlashAttention + continuous batching) is the multi-request *serving* throughput of the same host. The per-dollar figures therefore scale up substantially at batch, and the 9,000 tokens/dollar-hour figure should be read as a floor set by the single-stream assumption, not as the host's economic optimum. [ILLUSTRATIVE][DERIVED]
+> **Economics unit note (reconciliation with Ch. 4 and Ch. 15).** Both chapters use the same on-demand price basis: ~$2.50/hr per H100 → ~$20/hr per 8×H100 host. Two things must be kept straight. First, *units*: this chapter expresses **tokens per dollar-hour** (token-rate × 3600 s ÷ hourly cost), while Chapter 4 expresses **tokens per second per dollar** (token-rate ÷ per-second cost); convert by ÷3600. Second, *throughput basis*: the ~50 tok/s used here is a deliberately **conservative single-stream / low-batch generation rate** adopted to illustrate the per-dollar *method*, **not** a claim about the host's batched serving throughput. Chapter 15's figures are two different quantities, and neither is the single-stream decode rate used here: its **~8,000 tok/s is a prefill-side / whole-request rate** (Chapter 4's ≈8.5K tokens/s prefill — 9,200 tokens ÷ ~1.08 s — not batch-1 *decode*, which at the canonical 25 ms/token is ~40 tok/s, Chapter 2), while its **~35,000–70,000 tok/s** is the multi-request *serving* throughput under FlashAttention + continuous batching. The ~50 tok/s here (single-stream decode) and Chapter 15's ~8,000 tok/s (prefill-side) are therefore different phases of the same host, not two values for one quantity. The per-dollar figures therefore scale up substantially at batch, and the 9,000 tokens/dollar-hour figure should be read as a floor set by the single-stream assumption, not as the host's economic optimum. [ILLUSTRATIVE][DERIVED]
 
 [ILLUSTRATIVE][DERIVED]: tokens/s per dollar with prefill included. (Mixed-input convention: when a derivation mixes a canonical price with an illustrative rate, the result carries the non-canonical provenance — here the 50 tok/s rate input is [ILLUSTRATIVE][ASSUMPTION] while the $20/hr price is canonical.) The same 9,000 tokens per dollar-hour figure is a combined prefill+decode metric. Because this workload is input‑heavy (9.2K input vs 300 output tokens), the prefill leg consumes **~97% of the tokens** per request (9,200 ÷ 9,500) — and, because each prefill token runs the full $2\times70B$ forward FLOP, it is also **~97% of the linear forward-FLOP cost** (before the quadratic attention term). But it is only **~13% of the wall-clock time** (1.08 s prefill vs 7.5 s decode), because prefill is compute‑intensive yet batchable across concurrent requests, while decode is a sequentially‑limited token-by-token stream. So the honest picture is *both*: prefill dominates the compute/FLOP budget (and hence the GPU-hour cost of running the pipeline), and decode dominates the wall-clock latency budget (and hence per‑request service time). The per‑dollar economics therefore favor models that reduce the *prefill compute* burden (smaller context, larger batch, lower per‑token FLOP) more than models that optimize decode throughput alone — but a deployment must balance both, since decode still sets the latency SLO.
```


**文件**: `design/manuscript/chapter-06/chapter-06.md`

- sha256 **before**: `c2eaa84cd54178c5391a9006621d5e4570dc9f8512cd0c46313ab55f1a3f6ae4`
- sha256 **after**: `4762a0ac7bc257dcf6ad0cce527be354bcc52ca817b72092435f17ed5400ad38`
- **注意（并行外部改动）**：本任务窗口内另一 dispatched 修复（Fig 6.2 86-char caption + "behind ~1–2 same-time prefill requests"）落进同一文件，故上表 before/after sha 之间还夹着该外部改动。我方改动的**隔离** diff 为 `c2eaa84cd54178c5…` → `4762a0ac7bc257dc…`（即仅下方 goodput 一行）；我方改动前的真实基线 sha 为 `06bbe42a863e6b6d8f2e9aea5758431d3f332ceaa931eb1fe64d230802230994`（= HEAD + "~1–2" 修复，已逐字节复原验证）。

**精确 diff**:

```diff
--- a/design/manuscript/chapter-06/chapter-06.md
+++ b/design/manuscript/chapter-06/chapter-06.md
@@ -60,5 +60,5 @@
 ### Goodput vs Raw Throughput
 
-Deploying a higher-throughput configuration can *reduce* goodput. Concretely: suppose we enable larger dynamic batching to raise raw tokens/s from 50 tok/s to 70 tok/s, but the batch window pushes p95 TTFT from 1.8 s to 2.3 s — above the 2 s SLO. The extra 20 tok/s are produced, but they land in the tail that misses the SLO, so goodput does not grow. Raw throughput is up 40%; **goodput** (tokens that met the SLO) is effectively unchanged *in this case*, because the batch of SLO-compliant tokens didn't grow. (The general relation is goodput = raw_rate × compliant_fraction: if the compliant fraction falls from 96% to 94%, goodput is 50×0.96 = 48 vs 70×0.94 = 65.8 — it *rises* despite the p95 breach. The "unchanged" claim holds only when the extra tokens all land in the SLO-missing tail, i.e. the compliant fraction drops proportionally to the raw-rate gain. A p95 breach is a *configuration-level* acceptance signal; request-level SLO-goodput is a separate measurement and must be computed from the compliant fraction, not inferred from the p95 alone.) Goodput is the metric the customer experiences; raw throughput is what the GPU achieves. The architect optimizes goodput. This is why "faster" hardware or bigger batches do not trivially mean a better system.
+Deploying a higher-throughput configuration can *reduce* goodput. Concretely: suppose we enable larger dynamic batching to raise raw tokens/s from 50 tok/s to 70 tok/s (Chapter 5's single-stream / low-batch decode basis — a floor, not the host's aggregate serving rate; Chapter 15's ~8,000 tok/s is prefill-side and its ~35,000–70,000 tok/s the batched serving rate), but the batch window pushes p95 TTFT from 1.8 s to 2.3 s — above the 2 s SLO. The extra 20 tok/s are produced, but they land in the tail that misses the SLO, so goodput does not grow. Raw throughput is up 40%; **goodput** (tokens that met the SLO) is effectively unchanged *in this case*, because the batch of SLO-compliant tokens didn't grow. (The general relation is goodput = raw_rate × compliant_fraction: if the compliant fraction falls from 96% to 94%, goodput is 50×0.96 = 48 vs 70×0.94 = 65.8 — it *rises* despite the p95 breach. The "unchanged" claim holds only when the extra tokens all land in the SLO-missing tail, i.e. the compliant fraction drops proportionally to the raw-rate gain. A p95 breach is a *configuration-level* acceptance signal; request-level SLO-goodput is a separate measurement and must be computed from the compliant fraction, not inferred from the p95 alone.) Goodput is the metric the customer experiences; raw throughput is what the GPU achieves. The architect optimizes goodput. This is why "faster" hardware or bigger batches do not trivially mean a better system.
 
 ### Detecting the Regime: Bandwidth-Bound vs Compute-Bound
```

## 验证

- Ch5 对账注现无 "raw batch-1 ≈ 8,000"；Ch6 goodput 段带口径括注。
- 50 / 8,000 / 35,000–70,000 / 9,000 / 40 tok/s / 8.5K 全部可由上表复算复现。
- 未改 Ch15 → **OPEN**：`chapter-15.md:89` 仍写 "~8,000 tokens/s (raw, no flash, batch-1)"、`:100` 仍写 "token throughput rises from 8,000 to 70,000"，需由 Ch15 owner 改标为 prefill/整请求口径（本任务未获授权，未动）。
