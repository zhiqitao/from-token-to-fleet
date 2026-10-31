# ch456 — FTF-N06（Ch5 §3(a) [HYPOTHESIS] "~0.8 ms on a single CPU core"）— FIXED

- 范围：仅 `design/manuscript/chapter-05/chapter-05.md:62` 该段（即 N01 中被渲染器修复找回的段落；**段落本身保留、未删除、未再破坏**）。
- 状态：**FIXED（源文）**。

## 复算（before）

按本章表 5-1 自己的公式 `FLOPs = 2 × params × L`，L = 64：

| 模型 | params | GFLOP/embedding |
|---|---|---|
| all-mpnet-base-v2（768-dim） | ~110M | 2 × 110e6 × 64 = **14.08** |
| all-MiniLM-L6-v2（384-dim） | ~23M | 2 × 23e6 × 64 = **2.94** |
| bge-large-en（1024-dim） | ~335M | 2 × 335e6 × 64 = **42.88 ≈ 43** ✓（与表/正文 ≈43 vs ≈14 一致） |

- **增量 Δ = 14.08 − 2.94 = 11.14 ≈ 11.1 GFLOP / 每 64-token query**。
- 原文 0.8 ms ⇒ 需 **11.14e9 / 0.0008 = 13.9 TFLOP/s 单核** —— 单核不可信（现实 30–200 GFLOP/s）。
- 现实单核：11.14e9 ÷ 200e9 = **55.7 ms**；÷ 30e9 = **371.2 ms** → **~56–370 ms**，占 120 ms 预算的 47%–3×，与原句 "well within" 直接冲突。
- GPU 口径：11.14e9 ÷ 10e12 = **1.11 ms**（~10 TFLOP/s 保守有效算力）→ Ch4:167 的 ~120 ms 检索预算本就写明 "vector search and reranking on a **local GPU**"，故预算自身的基准是 GPU 而非单核。

## 修复（保持"within the ~120 ms retrieval budget"论点）

改为：增量 **~11.1 GFLOP**（14.08 − 2.94，表 5-1 自己两行；同族 384-dim 变体即 ~2× 情形）→ 单核 **~56–370 ms**（30–200 GFLOP/s，**不**合预算）vs **~10 TFLOP/s GPU ~1.1 ms**（= 120 ms 预算自己的基准）→ **在预算自身基准上仍 well within ~120 ms**，并显式点名"单核编码才是不合预算的配置"。

保留的原有数字：**2,000 / ~10 rps / ~120 ms / ~15% / 2×FLOP** 全部未动；`[HYPOTHESIS]:` 标签与段落结构未动（未新增标签，避免触发渲染器 `[LABEL]:` 规则）。

**文件**: `design/manuscript/chapter-05/chapter-05.md`

- sha256 **before**: `3cf3077c9d1aa9c9a9e8cc8abde2442d431895dc9fffb31588bd30cef68ec63a`
- sha256 **after**: `376a07d6f2e87a61b6ba63f7518e62b1fea3d56296edf8bb72629d9a1204343e`

**精确 diff**:

```diff
--- a/design/manuscript/chapter-05/chapter-05.md
+++ b/design/manuscript/chapter-05/chapter-05.md
@@ -60,5 +60,5 @@
 [ILLUSTRATIVE][DERIVED]: for a 1 M‑chunk corpus (a Ch 5‑local illustrative input, not part of Table 4‑2), the index storage for a $D$‑dim float32 vector corpus is $\text{bytes} = n_\text{chunks} \times D \times 4$. For 768‑dim: $1{\times}10^6 \times 768 \times 4 = 3.07$ GB; for 384‑dim: $1{\times}10^6 \times 384 \times 4 = 1.54$ GB; a difference of ~1.5 GB. At 10× the corpus (10 M chunks), that difference grows to ~15 GB. Small relative to a 140 GB base model, but not negligible at large corpus scale: storage is a persistent footprint that scales with corpus size, not a one‑time cost that vanishes.
 
-[HYPOTHESIS]: for the canonical 2,000‑user workload with ~10 rps average, the incremental per‑request compute cost of 768‑dim vs 384‑dim embeddings is ~0.8 ms on a single CPU core, well within the ~120 ms retrieval budget. The decision hinges on whether the ~15% retrieval quality gain translates into sufficient answer‑quality improvement to justify the 2×FLOP cost — a workload‑specific tradeoff, not a universal rule.
+[HYPOTHESIS]: for the canonical 2,000‑user workload with ~10 rps average, the incremental per‑request compute cost of 768‑dim vs 384‑dim embeddings is ~11.1 GFLOP per 64‑token query (2 × params × L: 14.08 − 2.94 GFLOP, Table 5‑1's own rows; a same‑family 384‑dim variant is the ~2× case) — ~56–370 ms if encoded on a single CPU core at a realistic 30–200 GFLOP/s, but only ~1.1 ms on a ~10 TFLOP/s GPU, which is the basis the ~120 ms retrieval budget already assumes (vector search and reranking on a local GPU, Ch 4). On that basis the incremental cost stays well within the ~120 ms retrieval budget; single‑core encoding is the configuration that would not fit. The decision hinges on whether the ~15% retrieval quality gain translates into sufficient answer‑quality improvement to justify the 2×FLOP cost — a workload‑specific tradeoff, not a universal rule.
 
 **Takeaway for the canonical RAG workload:** 768‑dim (all‑mpnet‑base‑v2) is the recommended embedding model. It places the workload in the quality‑positive regime without introducing per‑request latency that threatens the TTFT SLO. The 384‑dim option is viable only if storage or compute budget is extremely constrained; the bge‑large‑en option is overkill for this scale and its marginal quality gain does not offset the ~3× FLOP cost over all‑mpnet‑base‑v2 (≈43 vs ≈14 GFLOPs per 64-token embedding in the table above, the same ratio as their parameter counts).
```

## 验证

- `grep "0.8 ms" design/manuscript/chapter-05/` → **NONE**。
- `grep -c "decision hinges"` = **1**；`grep -c "HYPOTHESIS"` = **5**（段落仍在，未被删）。
- `[ILLUSTRATIVE]`×8 / `[DERIVED]`×14 计数与修复前一致。
- Takeaway（:64）"without introducing per‑request latency that threatens the TTFT SLO" 在 GPU 基准下仍成立，未改。
