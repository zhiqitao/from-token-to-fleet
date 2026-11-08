# Proposed insertions — Liquid AI LFM3（补充材料提案）

**总原则**：LFM3 发布于 **2026-10-27**，晚于书稿冻结点 **2026-08-30**。以下任何内容入书都必须作为**另行标注日期的补充材料**（例如侧栏/附注 "Post-freeze update (2026-10-28): …"），**不得静默替换**冻结时点已有的 LFM2/LFM2.5 对比、表格或正文数字。本文件仅为提案，未改动任何 manuscript 源文件。

**证据基础**：`report.md`、`claims.json`（32 条逐字证据）、`source-index.md`。所有数字为厂商一手披露或本调查基于一手 config 的推导，均注明来源；无任何本调查自行运行的 benchmark。

## Ch 3 — Understanding the Model（架构）

- **插入点**：混合架构/注意力变体处。
- **内容**：LFM3 tri-hybrid 作为"逐层异构算子栈"的实例：24 层 = 13 门控短卷积(k=7) + 5 SWA(w=256) + 6 全局注意力；四项机制（head-wise sigmoid 门、partial RoPE 0.5、sandwich norm、GQA 4 KV 头）逐条引博客+config。[report §3.2, C07–C12]
- **形式**：一段说明文 + 可选侧栏引用 `figures/lfm3-architecture.svg` 渲染件。
- **日期标注**：`Liquid AI blog, 2026-10-27; HF config.json, retrieved 2026-10-28`。
- **注意**：不得改写 Ch3 已冻结的 LFM2 架构描述；LFM3 仅作后续世代补充。

## Ch 5 — From Workload to Model Selection（选型）

- **插入点**：小模型/端侧选型讨论。
- **内容**：LFM3 家族"一骨干六模型"选型表（text/VL/Audio/Omni/d1×2，输入→输出、建于哪个检查点、1.73B/1.9B/2.2B 参数）；厂商自限声明 "not recommended for agentic coding or complex multi-step reasoning" 应同时引用。[report §2, C02–C06, C30]
- **形式**：小表 + 两句说明。
- **日期标注**：同上；参数为 HF 卡 1.73B（dense，无激活/总参数之分）。

## Ch 7 — Memory Is the First Constraint（内存）

- **插入点**：KV cache 随上下文缩放处——**最贴切的插入**。
- **内容**：三类层状态缩放对比：conv O(1)（无 KV）、SWA O(1)（256 窗口，~2.6MB 恒定）、全局注意力 O(T)（12KB/token 推导，6/24 层承担）→ 128K≈1.61GB，与厂商 1.6GB 声称互证（对照 Qwen3.5-4B 4.3GB、MiniCPM5-2B 5.6GB，vendor-reported）。[report §3.3, C13–C14]
- **形式**：一段推导式说明文 + `figures/lfm3-architecture.pdf`（已过 439.2pt/8.50pt 打印测试，见 figures/QA.md）。
- **日期标注**：推导基于 HF config.json（retrieved 2026-10-28）；1.6GB 为厂商报告值，是否为运行时测量未确认，须注明。

## Ch 8 — Compute（计算）

- **插入点**：推理吞吐/端侧计算处。
- **内容**：厂商实测吞吐及其方法学（**支持 vs 实测分开写**）：边缘 llama.cpp Q4_0/32K/batch1/100 out/GPU offload 三设备；GPU 单张 B300+SGLang BF16/1024 并发→3.6B tokens/天。公平性注记：对照模型用 llama.cpp b11744 而 LFM3 用定制 build；docs vLLM 页仍为 LFM2.5。[report §6–§7, C19–C22, C27]
- **形式**：短段落 + 方法学括注。
- **日期标注**：`Liquid AI model card, lastModified 2026-10-28`。

## Appendix A — 基准/对比附录

- **插入点**：基准方法论或模型对比表附录。
- **内容**：(a) LFM3 厂商基准表的**方法学审查**——全部 vendor-run、无独立复现（截至 2026-10-28）、上下文不对称（262,144 vs 131,072）、"35% fewer" 为取整（算术 33.5%/34.6%）、Average 为非加权均值；(b) 明确标注 **本次检索未找到 LFM3 技术报告**（arXiv 0 条），训练算力/优化器/数据明细无来源。[report §7–§8, C23–C29]
- **形式**：附注段落或一张"方法学注记"小表。
- **硬性要求**：整块标注为 2026-10-28 补充调查结果；**不得**并入冻结的既有对比表数值。

## 不建议插入

- 任何需要本调查自行跑 benchmark 才能成立的对比（任务禁止虚构 benchmark 运行，且未执行）。
- LFM3-VL/Audio/Omni 的 62 项视觉表、音频表等——仅厂商披露、无独立验证，且与书稿 Ch3/5/7/8/AppendixA 主线关联弱；如需，仅可作为带日期的厂商数据引用。
- 从 LFM2 规格推断 LFM3 的任何写法（任务明令禁止；本调查所有 LFM3 数字均直接来自 LFM3 一手来源）。