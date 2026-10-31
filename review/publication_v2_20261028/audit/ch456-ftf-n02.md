# ch456 — FTF-N02（Ch4 §4.3 悬空交叉引用 "3.3M"）— FIXED

- 范围：仅 `design/manuscript/chapter-04/chapter-04.md:178` 括注。
- 状态：**FIXED（源文）**；未做整书构建（超出本任务授权）。

## 复算（before）

| 量 | 算式 | 结果 |
|---|---|---|
| Ch4 全队列输入 tokens/cloud dollar | 92,000 ÷ (120/3600) | **2,760,000**（≈2.76M，与正文一致） |
| Ch4 全队列输出 | 3,000 ÷ (120/3600) | 90,000 |
| Ch4 合计（blended） | 95,000 × 3600 ÷ 120 | **2,850,000**（≈2.85M，表 §4.3 一致） |
| 若按 120,000 tok/s ÷ $120/hr | 120,000/120 × 3600 | 3,600,000 |
| Ch5 tokens/dollar-hour | 50 × 3600 ÷ 20 | **9,000** ✓ |

- 全 `design/manuscript/` 检索 `3.3M|3.3 million`：**修复前仅此 1 处（即引用本身）**；3.3M 来自旧版 5-host/$100/hr 口径（92,000 ÷ 0.0278 = 3.3M），现行源已是 6-host/$120/hr。
- 被指向的 Ch5 对账注（`chapter-05.md:93`）实际对账内容 = **单位**（tokens/dollar-hour vs tokens/s per dollar）+ **吞吐口径**（50 单流 vs Ch15 的 8,000 / 35,000–70,000），**不含 3.3M** → 原括注既引错数字也误述被引内容。

## 修复

改为指向真实存在的对账内容与真实数字：Ch5 的 **9,000 tokens per dollar-hour = 单流（50 tok/s）**；Ch4 自身的 **~2.76M 输入（~2.85M 合计）tokens per cloud dollar = 全队列 aggregate**。所有既有数字（9,000 / 50 / 2.76M / 2.85M / 92,000 / 3,000 / $120 / 19,800 / 3.56M / 56.5K）全部保留，未新增未复算的数。

**文件**: `design/manuscript/chapter-04/chapter-04.md`

- sha256 **before**: `ae7a42fde67607ee81abbe887fc785e25b2b3db41285a2ab3c7971f46fbb9dd6`
- sha256 **after**: `1518e8da9b177710c81d68523b9131f33cf517442e42b7566b2aeafd50e957ee`

**精确 diff**:

```diff
--- a/design/manuscript/chapter-04/chapter-04.md
+++ b/design/manuscript/chapter-04/chapter-04.md
@@ -176,5 +176,5 @@
 - **Infrastructure**: A single host with 8×H100 GPUs (640 GB total GPU memory, 140 GB model FP16 weights fit with room for KV cache). Capital cost ≈ $20/hour on-demand ($2.50/GPU-hr), or ~$2,500/month reserved (illustrative committed-use discount; a ~83% discount on H100 on-demand is unusually deep and differs from the on-demand basis the canonical box uses) — the canonical box uses the on-demand basis.
 - **Token pricing**: ~$1.20 per million input tokens, ~$2.00 per million output tokens on the same H100 instance (mid-tier managed-API list price, derived from cloud provider pricing as of 2026). The frontier-class API used in the Ch 16 TCO comparison is priced higher (~$2/$8 per 1M) — a different provider tier, not the same line item.
-- **Throughput per dollar**: At 10 rps average, the system processes ~92,000 input tokens/s + ~3,000 output tokens/s. **The dollar denominator must be the whole fleet that serves this rate, not one host.** At the ~6-host average the whole-fleet spend is ~$120/hour (≈ $0.0333 per second), so ~92,000 / 0.0333 ≈ **~2.76 million input tokens per cloud dollar** and ~3,000 / 0.0333 ≈ **~90,000 output tokens per cloud dollar**. These are *modeled, whole-fleet* figures (before SLO/headroom/failover). A separate quantity is a single host's *sustained-planning* prefill rate (~19,800 tok/s at 35% MFU, Ch 8 — a planning rate, not a ceiling: the peak-derived ceiling is ~56.5K tok/s): ~19,800 × 3,600 / $20 ≈ **~3.56M prefill tokens per host-dollar** — a different denominator and a different rate, and **not** a claim that one host serves the offered load. Never present a tokens-per-dollar figure with the offered workload rate divided by a single-host price. (Chapter 5 expresses the same economics on a GPU list-price basis as **tokens per dollar-hour**; see its throughput-basis reconciliation note — the 9,000 is single-stream/the 3.3M is whole-fleet aggregate — before cross-chapter comparison.)
+- **Throughput per dollar**: At 10 rps average, the system processes ~92,000 input tokens/s + ~3,000 output tokens/s. **The dollar denominator must be the whole fleet that serves this rate, not one host.** At the ~6-host average the whole-fleet spend is ~$120/hour (≈ $0.0333 per second), so ~92,000 / 0.0333 ≈ **~2.76 million input tokens per cloud dollar** and ~3,000 / 0.0333 ≈ **~90,000 output tokens per cloud dollar**. These are *modeled, whole-fleet* figures (before SLO/headroom/failover). A separate quantity is a single host's *sustained-planning* prefill rate (~19,800 tok/s at 35% MFU, Ch 8 — a planning rate, not a ceiling: the peak-derived ceiling is ~56.5K tok/s): ~19,800 × 3,600 / $20 ≈ **~3.56M prefill tokens per host-dollar** — a different denominator and a different rate, and **not** a claim that one host serves the offered load. Never present a tokens-per-dollar figure with the offered workload rate divided by a single-host price. (Chapter 5 expresses the same economics on a GPU list-price basis as **tokens per dollar-hour**; see its throughput-basis reconciliation note before cross-chapter comparison — Chapter 5's **9,000 tokens per dollar-hour** is single-stream (50 tok/s), while this chapter's **~2.76M input tokens per cloud dollar** (~2.85M combined) is whole-fleet aggregate.)
 - **Cost per request**: At 10 rps, each request carries ~9,500 tokens (9,200 input + 300 output). At the per‑million rates, cost per request ≈ ($1.20 × 9.2 + $2.00 × 0.3) / 1,000 ≈ $0.01164 ≈ **$0.012 per request** per inference cycle. At 40 rps peak, cost scales linearly. **Basis note — two different cost bases, not interchangeable.** The $0.012 figure is derived from *per-token market/API list prices* ($1.20/M in, $2.00/M out) for the *mid-tier* managed API; it is a cloud-provider price a customer would pay per request on that hosted API. (The *frontier-class* API used in the Ch 16 TCO comparison is priced higher — ~$2/$8 per 1M, ~$0.0208 per request; see the token-pricing bullet above for the tier distinction.) It is *not* the fleet owner's marginal infrastructure cost. The owned-fleet cost is nearly all fixed capex/opex and barely scales per request, but it must be computed on the **whole fleet**, not one host: the $20/hr is the price of a *single* 8×H100 host, while the canonical 10 rps average / 40 rps peak needs ~6 hosts at average and ~21 at peak (Ch 16/17). So the owned per-request cost is (N_hosts × $20/hr) ÷ (rps × 3600) ≈ (6 × $20) ÷ (10 × 3600) ≈ **~$0.0033 per request** at average, and (21 × $20) ÷ (40 × 3600) ≈ **~$0.0029 per request** at peak — the two no longer coincide exactly, because the floor-17 KV screen rounds 10 rps up to 6 hosts and 40 rps up to 21 (6/10 ≠ 21/40), so the peak lands slightly cheaper per request. (Dividing one host's $20/hr by the whole workload's 10 rps would give ~$0.00056, but that is dimensionally wrong: one host cannot serve 10 rps of this workload.) Keep the two bases separate: use the per-token price for a *hosted/API* cost model, and the fleet $/hr ÷ fleet rps for an *owned fleet*. The two are juxtaposed in the cost-basis table below (§4.3) only to show the hosted-API pricing basis, not as an owned-fleet marginal cost.
 
```

## 验证

- `grep -rn "3.3M|3.3 million" design/manuscript/` → **NONE**（0 命中）。
- 括注仍指向 Ch5 `chapter-05.md:93` 的对账注，语义与该注一致。
- 未触碰 `[ILLUSTRATIVE]`/`[DERIVED]` 标签与任何其他数字。
