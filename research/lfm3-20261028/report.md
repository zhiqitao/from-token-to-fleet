# Liquid AI LFM3 调查报告

- 调查日期：2026-10-28（UTC-07:00）；一手检索时间窗 2026-10-28T21:23:59Z–21:38:00Z
- 书稿冻结点：2026-08-30（本报告全部内容晚于冻结点，仅可作为**另行标注日期的补充材料**，见 proposed-insertions.md）
- 证据策略：官方博客为一手骨架；**本次检索未找到 LFM3 技术报告**（检索范围见 §8），故以 HF 模型卡 + config.json + 官方建模代码作交叉验证层
- 结构化逐条证据：`claims.json`（32 条，含逐字引文与状态）；来源与 hash：`source-index.md`；原始证据：`raw/`

## 1. 发布与检索日期

- 官方博客《Introducing LFM3: Every Modality for Specialized Intelligence》页内标注 **OCT 27, 2026** [1]；HF 官方博客同日 "Published October 27, 2026" [3]；Liquid AI X 账号帖时间 5:07 PM · Oct 27, 2026。
- HF 模型卡 `lastModified = 2026-10-28T17:16:37Z`（发布次日仍在修订），当前 sha `ac2586a3…` [9]。本报告所引模型卡为该修订版。
- 本报告全部检索发生于 2026-10-28（UTC），hash 见 source-index.md。

## 2. 发布家族与变体（精确清单）

首发 6 个模型，全部源自同一 LFM3-1.7B-Base 骨干，均为 2B 级 [1][3]：

| 模态 | 变体 | 输入→输出 | 建于 | 参数（来源） |
|---|---|---|---|---|
| 文本 | **LFM3-1.7B**（+ **LFM3-1.7B-Base** 预训练检查点） | 文本→文本 | Base | 1.73B（HF 卡/文档 [5][11]） |
| 视觉 | **LFM3-VL-2B** | 文本/图像/视频→文本 | LFM3 骨干+视觉编码器 | 1.9B（博客表列 [1]） |
| 音频 | **LFM3-Audio-2B** | 文本/音频→文本/语音 | 骨干+音频编码器/解码器/LiquidCodec | 2B 级（博客 [1]） |
| 全能 | **LFM3-Omni-2B** | 文本/图像/视频/音频→文本/语音 | 骨干+视觉与音频编码器 | **2.2B**（博客正文 [1]） |
| 决策 | **d1-2B** | 文本/图像/视频→校准答案 | **LFM3-VL-2B** | 2B 级 [1][3] |
| 决策 | **d1-Omni-2B** | +音频→校准答案 | **LFM3-Omni-2B** | 2B 级 [1][3] |

注意两点：(a) 博客称 "six … trained from LFM3-1.7B-Base"，而 HF 博客表格显示两个 d1 模型分别建于 VL-2B/Omni-2B——即**间接**源自 Base，表述存在层级差异（claims C32）；(b) "2B 级"是产品命名，Omni 实为 2.2B。

**导出/量化变体**（HF API 实测清单 [4]）：文本模型有 GGUF、MLX(4/5/6/8bit/bf16)、ONNX、FP8、NVFP4；VL 有 GGUF/MLX/ONNX/FP8/NVFP4；Omni/Audio 有 GGUF/MLX/ONNX。d1 系列另有 GGUF/MLX/ONNX 及旧 d1-3B、d1-omni-600M。

## 3. 参数与架构

### 3.1 参数

- LFM3-1.7B(-Base)：**厂商报告总参数 1.73B，为 dense 架构**。配置与建模代码未显示 MoE 专家路由；本调查不另设未经计数验证的“激活参数”数字 [5][6]。
- 关键超参（config.json 逐字 [5]）：hidden 2048、intermediate 7680、24 层、16 查询头 / **4 KV 头**（GQA）、head_dim 128、tie_word_embeddings=true、dtype bfloat16。

### 3.2 tri-hybrid 层架构（博客骨架 × config 交叉验证，完全一致）

博客 [1]："Of its 24 layers, 13 are convolutions, 5 are SWA with a 256-token window, and 6 are global attention." config.json 的 `layer_types` 给出**逐层精确序列**，逐层计数 conv=13 / sliding=5 / full=6，`sliding_window: 256`，与博客、HF 卡、官方文档 [11] 四处一致（claims C07）：

```
conv conv full conv slid conv full conv slid conv full conv slid conv full conv slid conv full conv slid conv full conv
```

精确顺序为：开头 2 个卷积，随后重复 5 次“全局注意力 → 卷积 → 滑窗注意力 → 卷积”，最后接“全局注意力 → 卷积”。

四项设计变更（博客 [1]，均在 modeling_lfm3.py / config 中得到代码级印证）：

1. **门控短卷积**：核大小 **7**（LFM2 为 3）；config `conv_L_cache: 7` [5]。卷积层占 13/24，"over half the layers"。
2. **Head-wise gated attention**：`gate_proj = Linear(hidden→num_heads)`，`gate = sigmoid(...)`，`attn_output * gate`——每个头可整体关断；厂商称可抑制激活离群值、改善量化与训练稳定性 [1][6]。
3. **Partial RoPE**：全局注意力层仅旋转每头**最高频一半**（config `partial_rotary_factor: 0.5`，rope_theta 1e6），低频半按内容匹配、与距离无关；SWA 层保持全 RoPE（rope_theta 1e4，无 partial 字段）[1][5]。
4. **Sandwich norm**：每块对输入与输出都归一化（config `use_sandwich_norm: true`，代码三处分支 [5][6]）。

**所检配置未列出独立 RNN/SSM 算子层**：三类算子是卷积、滑窗注意力和全局注意力。不过卷积解码会更新固定长度状态；不能把“无独立 RNN 层”写成“没有递归状态更新” [6]。本报告不从 LFM2 推断任何 LFM3 规格；上文所有数字均直接来自 LFM3 一手来源（LFM2 仅在厂商自己做对比时被提及）。

### 3.3 状态 / KV 内存缩放（本调查推导，基于一手 config）

三类层的解码状态随上下文的缩放完全不同（claims C13，推导自 config.json [5]）：

- **卷积层（13 层）**：无 KV 缓存；状态 = 核窗口缓冲（`conv_L_cache: 7`），**O(1) 有界**。
- **SWA 层（5 层）**：KV 仅需最近 256 token（`sliding_window: 256`），**保留窗口的理论状态量为 O(1)**，前提是运行时确实裁剪缓存。每层 2×4×128×256×2B = 524,288 B；5 层共 2,621,440 B（2.5 MiB）。这不是对任意运行时实际分配量的测量。
- **全局注意力层（6 层）**：KV 随上下文**线性增长**；每 token 每层 2(K,V)×4 kv头×128 dim×2B(bf16) = 2,048 B，6 层合计 **12,288 B/token ≈ 12 KB/token**；128K 上下文 ≈ **1.61 GB**。

该推导与厂商声称一致（claims C14，博客 [1]）："a full 128K-token context needs 1.6 GB of KV cache, against 4.3 GB for Qwen3.5-4B and 5.6 GB for MiniCPM5-2B."——在滑窗缓存确实被裁剪的假设下，随上下文线性增长的 KV 项来自 6 个全局层。这里 128K 按 131,072 tokens 计算：全局层合计 1,610,612,736 B（1.5 GiB，约 1.611 GB）；262,144 tokens 时为 3,221,225,472 B（3 GiB，约 3.221 GB），另需滑窗缓存、卷积状态、权重与工作区。因此，约 1 GB 的 4-bit **权重大小不能推出总内存需求，也不能证明 256K 上下文适合 1 GB 内存设备**。厂商 1.6 GB 属于来源报告的数值；因没有确认测量方法，不将其标记为本地测量或已确认的厂商实测。

配套图：`figures/lfm3-architecture.svg`（可编辑源）→ `lfm3-architecture.png/.pdf`（渲染件），打印可读性测试见 §10。

## 4. 训练与后训练

**预训练（Base，22T tokens 总量）** [1][7]：
- 主预训练：相较 LFM2 增加科研论文、仓库级代码、更多数学与更广知识源。
- 中期训练：**最后 3.5T tokens** 为精选高质量数据，agentic 轨迹与工具调用占比更大，并**将上下文扩展到 256K**。
- HF 卡配图 alt 文本给出更细阶段划分（[5]，属厂商图注）：~15T web/合成 → 3T code/math/science(4K) → 3T 精选 agentic(32K) → 500B(128K) → 50B(256K) = 22T。

**后训练四阶段（LFM3-1.7B）** [1][5]：
1. **SFT**：1.75T tokens（聊天、推理、工具调用、agentic 轨迹）；
2. **混合 RL**：多域同时训练（math/code/SQL/结构化输出），奖励含长度惩罚；
3. **MOPD（多域 on-policy 蒸馏）**：6 个专家 RL 教师（code、math、tool use、long context、agentic、enterprise workflows）蒸馏回单模型；
4. **Agentic RL**：在真实 agent harness 内运行网页浏览到办公任务。

未披露：训练算力/硬件、优化器、学习率、数据集构成明细、教师模型规格——技术报告缺失导致训练细节止步于博客粒度（§8）。

## 5. 分词器与上下文

- 词表 **128,000**，"the same 128K vocabulary as LFM2.5-8B-A1B"（厂商语，[1]）；config `vocab_size: 128000`，bos/eos/pad = 124894/124900/124893 [5]。
- 上下文 **256K（262,144，输入+输出）**：博客、HF 卡、docs 三处一致 [1][5][11]；由中期训练阶段扩展而来。
- 语言 16 种（en/ar/zh/fr/de/it/ja/ko/pt/es/vi/th/id/hi/ru/pl，HF 卡 frontmatter [5]）。
- 工具调用格式：LFM3 改为 `qwen3_coder` 超集（LFM2/LFM2.5 为自定义格式）[12]。

## 6. 权重、许可与部署

- **开放权重**：base 与后训练模型均在 Hugging Face、Playground、Liquid AI API 提供 [1]；HF API 确认仓库非 gated（`"gated": false` [9]）。
- **许可**：**LFM Open License v1.0**（HF frontmatter `license: other, license_name: lfm1.0`；LICENSE 全文抓取，Licensor = Liquid AI, Inc. [8]）。非 OSI 标准许可证，具体条款以 LICENSE 文本为准。
- **推理引擎：支持 vs 实测**（区分很重要）：
  - *支持（模型卡声明 [5]）*：BF16→vLLM/SGLang/Transformers；FP8→SGLang；NVFP4→SGLang；GGUF→llama.cpp/Ollama/LM Studio；MLX(4bit)→MLX；另有 ONNX 仓库。博客另称 day-0 伙伴含 Intel(OpenVINO)、Qualcomm AI Hub、Vercel、OpenRouter 等 [1]。
  - *实测（有方法学）*：边缘 = llama.cpp **Q4_0 GGUF、32,768 上下文、batch=1、100 输出 tokens、GPU offload**，设备 AMD Ryzen AI Max+ 395 (Vulkan) / Apple M5 Max (Metal) / iPhone 17 Pro [5]；GPU = **单张 NVIDIA B300 + SGLang BF16、1024 并发 → 3.6B tokens/天** [5]。
  - *文档滞后矛盾*：docs 的 vLLM 页检索时**仍只写 LFM2.5**（`Lfm2ForCausalLM` 等），未提 LFM3，而模型卡 BF16 行恰链接此页（claims C27）[10]。vLLM 对 LFM3 的原生支持在该页无记载——"supported" 以模型卡为准，独立验证未做（本调查未运行任何推理）。

## 7. 基准方法论审查

**谁跑的**：全部为**厂商自测**（博客与 HF 卡表格）。截至 2026-10-28，未发现任何独立第三方复现；VentureBeat/Unite.AI/MindStudio 均为转述厂商数字（claims C24）[13]；MacPaw 的 65 任务对比是厂商引用的伙伴测试 [1]。

**实测 vs 推导**：
- 实测（方法学披露较全 [5]）：主基准表 = vLLM BF16、逐模型满上下文、默认 temp 0.6/top_p 0.95、逐基准覆盖（BFCL greedy≤32,768 输出；WebArena≤40 步；SWE-bench OpenCode≤250 轮等）；边缘表 = 上节 Q4_0 配置；GPU 吞吐 = B300/SGLang。
- 推导/汇总：表中 "Average" 行为**逐项非加权平均**（厂商自述 [1]）；"35% fewer parameters" 为厂商取整（1−1.73/2.6=33.5%，1−1.7/2.6=34.6%，claims C29）；"1.6GB KV" 与本调查 12KB/token 推导一致（C13/C14）。

**硬件/精度/上下文/批大小**：见上；基准表批大小未披露（仅边缘表披露 batch=1）。

**对比公平性问题（明确记录）**：
1. **上下文不对称**：LFM3-1.7B/Qwen3.5-4B/9B 用 262,144，LFM2.5-2.6B/MiniCPM5-2B/Gemma 4 E4B 只有 131,072 [5]——对 LFM2.5 的 WebArena 3.02 等低分，长上下文差异是部分混杂因素。
2. **llama.cpp build 不同**：LFM3 用 "a llama.cpp build with LFM3 support"，对照模型用公开 release b11744 [5]——非同一二进制。
3. **参数级差大**：1.7B vs 9.7B (Qwen3.5-9B) 同表比较，厂商叙事为"以小博大"；表内 LFM3 并非全胜（GPQA、RULER 128K、SWE-bench、MCP-Atlas 等由大模型领先，博客亦自认 [1]）。
4. **自限声明**：HF 卡明言 "not recommended for agentic coding or complex multi-step reasoning due to its small size" [5]，与表中 SWE-bench 43.40 并读更审慎。
5. **托管 API 上下文 128K vs 模型 256K**：VentureBeat 转述登录后控制台 [13]，本调查未登录验证（claims C31，secondary-unverified）。

## 8. 矛盾与不可得工件（显式记录）

| # | 事项 | 状态 |
|---|---|---|
| 1 | **本次检索未找到 LFM3 技术报告** | arXiv `ti/abs "LFM3"` 0 条；HF papers `[]`；liquid.ai/research 无 LFM3 链接（仅有 LFM2 报告 2511.23404）[2][14]。官方引用条目指向博客自身（`journal = Liquid AI Blog`）[1]。→ 本调查以博客为骨架、HF/config/代码交叉验证；训练算力、优化器、数据明细等**无来源可查** |
| 2 | **本次未定位到官方 LFM3 专属 GitHub 仓库** | github.com/LiquidAI/lfm3 → 404；GitHub org "LiquidAI" API 404；"liquid-ai" org 仅 Plankton/Vehicles [15]。代码经 HF `trust_remote_code` 分发（modeling_lfm3.py 42,359 B [6]）；搜索到的 lfm3-* 仓库均为第三方 |
| 3 | docs vLLM 页仍为 LFM2.5 | 见 §6，claims C27 |
| 4 | "six … trained from Base" vs d1 建于 VL/Omni | 表述层级差异，claims C32 |
| 5 | "35% fewer" vs 算术 33.5%/34.6% | 厂商取整，claims C29 |
| 6 | API 128K vs 模型 256K | 二手来源未验证，claims C31 |
| 7 | 博客 1.6GB KV 无测量工具/精度 | vendor-reported；是否来自运行时测量未确认，claims C14 |

## 9. 图（架构/状态图）

一手细节充分（逐层序列、核大小、窗口、RoPE、门、norm 均有 config+代码），故绘制了**独立说明图**（非厂商美术图）：`figures/lfm3-architecture.svg`（可编辑源）+ `.png` + `.pdf`（渲染件）。图仅传达已确认机制：24 层 tri-hybrid 序列、三类层的解码状态缩放（O(1)/O(1)/O(T)）、12KB/token 推导链。打印可读性测试（439.2pt 栏宽、≥8pt）结果见 §10 与 `figures/QA.md`。

## 10. 打印可读性测试

见 `figures/QA.md`：以 pymupdf 读矢量 PDF 文本层，栏宽 439.2pt 放置下最小 span ≥8pt 方为通过；测试脚本与数值记录于该文件。

## 来源（一手优先）

[1] https://www.liquid.ai/blog/lfm3 （OCT 27, 2026；raw/blog_lfm3.html sha256 6570a6a7…）
[2] https://export.arxiv.org/api/query?search_query=ti:%22LFM3%22+OR+abs:%22LFM3%22 （0 条）
[3] https://huggingface.co/blog/LiquidAI/lfm3 （Published October 27, 2026）
[4] https://huggingface.co/api/models?author=LiquidAI&search=LFM3&limit=100
[5] https://huggingface.co/LiquidAI/LFM3-1.7B/raw/main/README.md （+ config.json 同目录；sha256 ca4ea3e8…/8c6ae8b8…）
[6] https://huggingface.co/LiquidAI/LFM3-1.7B/raw/main/modeling_lfm3.py （sha256 e8cd5254…）
[7] https://huggingface.co/LiquidAI/LFM3-1.7B-Base/raw/main/README.md （sha256 b135e4bc…）
[8] https://huggingface.co/LiquidAI/LFM3-1.7B/raw/main/LICENSE （sha256 4d28ca14…）
[9] https://huggingface.co/api/models/LiquidAI/LFM3-1.7B （lastModified 2026-10-28T17:16:37Z）
[10] https://docs.liquid.ai/deployment/gpu-inference/vllm （仍为 LFM2.5）
[11] https://docs.liquid.ai/lfm/models/lfm3-1.7b
[12] https://docs.liquid.ai/lfm/key-concepts/tool-use.md
[13] https://venturebeat.com/technology/liquid-ais-new-lfm3-models-put-browser-agents-voice-commands-and-image-recognition-onto-enterprise-controlled-devices （二手）
[14] https://www.liquid.ai/research （无 LFM3 链接）
[15] https://api.github.com/orgs/liquid-ai/repos （仅 Plankton/Vehicles）；https://github.com/LiquidAI/lfm3 → 404

完整 URL/时间/hash 表见 `source-index.md`；逐条逐字证据见 `claims.json`。