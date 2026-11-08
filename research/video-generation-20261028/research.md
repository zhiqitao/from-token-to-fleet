# 视频生成系统研究：从 Wan 的视频形状到服务与集群决策

研究快照：2026-10-28 UTC（工具核验当地时间为 2026-10-27 深夜，目录采用 UTC 日期）。书稿证据截止：2026-08-30。范围：研究、候选英文正文与原创图，不改书稿，不部署、不跑生成模型、不提交、不推送、不修改配置、不再委派。

## 1. 结论与证据边界

最值得加入本书的不是“视频模型目录”，而是一个范围扩展：token → workload 这条因果链需要先确定 token 属于哪一种执行过程。视频帧、潜变量单元、视频 transformer positions、文本 tokens、采样步与模型求值次数不是同一单位。全片去噪不具备自动继承文本 AR 缓存和 TTFT/TPOT 模型的理由。

本次得到的关键结论：

1. Wan2.2 TI2V-5B 是适合本书的小型资源算例。它的 VAE stride 是 `(T,H,W)=(4,16,16)`，而不是 A14B 所用的 `(4,8,8)`；patch 均为 `(1,2,2)`。直接沿用旧代压缩常数会使这个算例的视频 token 数错到另一个量级。[VG004–VG006]
2. A14B 的专家按噪声阶段切换，不是照搬语言 MoE 的逐 token top-k FFN 路由。约 27B 总参数和约 14B 活跃参数分别约束常驻与执行；两者是官方约数，不能把“两个精确 14B”相加来修正官方总数。[VG003]
3. 官方当前 API 已列出 `wan3.0-video` / `wan3.0-video-prime`，且标注 preview。这只支持托管 API 的事实，不支持“Wan3 已公开权重、继承 Wan2.2 MoE 或 VAE”的推断。也没有在本研究中建立其精确首发日期。[VG017–VG018、VG042]
4. 当前公开 Wan-AI 库存还包括 Wan-Dancer、Wan2.2-Animate-2 及其蒸馏变体。因此只调查 Wan2.1/2.2 基础 T2V 会漏掉现有官方研究路径。精确库存已单独保存，不把 HF 创建/修改时间冒充发布日。[VG015–VG016]
5. LTX-2 的报告、HunyuanVideo-1.5 的报告有助于比较高压缩、多模态耦合、稀疏注意力与蒸馏的系统后果。但是供应方表格不能直接拼成“每条可用视频成本”排行。[VG019–VG023、VG033–VG034]
6. 已开发 2 张原创机制图，分别解释 dense 5B 的视频状态路径与 A14B 的活跃/常驻差异，避免合成一个不存在的混合架构。图源、350 dpi PNG、灰度版、实际尺寸证明和 QA 均在 `figures/`。

官方技术报告是机制骨架，代码与配置校验版本细节。特别重要的归因边界：Wan2.2 README 的报告链接仍指向 [Wan: Open and Advanced Large-Scale Video Generative Models，arXiv:2503.20314](https://arxiv.org/html/2503.20314)。该报告先于 Wan2.2；不能让它单独证明后来的 MoE 与 5B-VAE 升级。Wan2.2 特有事实在本包中引用具体发布记录、配置和采样代码。[VG011]

### 可复核的材料

- `claims.json`：逐项主张、来源 URL、发布事件/检索日期、章节位置、证据状态、适用边界、缺口。
- `sources/manifest.json`：每次成功下载的原始响应、时间、SHA-256；失败访问保留错误，不伪造内容。
- `sources/pinned-sources.json`：对已有 branch-based 源码与 commit 固定版本进行字节核对。固定版本主干包括 Wan2.2 `1ea34ff48f87168174e12956e200b1d908b1c5ff`、LTX-2 `e98f6d927d83c92ef2be6aec76c8440b19306e39`；其他固定信息由 JSON 保存。
- `source-catalogue.md`：完整原始来源索引。
- `calculations.json` / `verify_sources_and_math.py`：可复算预算；明确是分析值，不是 GPU 实测。
- `benchmark-evidence.json`：供应方性能表的可见字段与 null 缺口。
- `proposed-insertions.md`：实质英文候选正文、精确源章节锚点、参考文献及图引用。

## 2. Wan 官方家族、任务与时间

本研究查询 Wan-Video 官方 public repos、Wan-AI 作者 public 模型列表、官方 README/报告、Alibaba Cloud 模型目录。`official-wan-model-inventory.json` 保存该查询返回的精确 ID 与 revision。查询范围是这些公开端点，不是世界范围的完整性证明；其他官方组织、私有模型、区域服务与未检索端点不在“已穷尽”之列。

### 开放权重/研究实现的分层

| 家族或路径 | 已核实的变体 / 能力 | 时间与边界 |
|---|---|---|
| Wan2.1 | `T2V-1.3B`、`T2V-14B`、`I2V-14B-480P`、`I2V-14B-720P`、`FLF2V-14B-720P` | README 发布代码/权重记录为 2025-02-25；FLF 是首尾帧条件，不是一般 V2V。1.3B 推荐 480P，720P 稳定性有官方警告。[VG001] |
| Wan2.1 VACE | `VACE-1.3B` / `VACE-14B`，创建与编辑条件统一 | README 引入记录为 2025-05-14；报告区分 Context Tokenization、full tuning 与 context adapter，不把能力推广到所有 Wan 权重。[VG014] |
| Wan2.2 基础模型 | `T2V-A14B`、`I2V-A14B`、`TI2V-5B` | 官方记录 2025-07-28；A14B 双专家，5B dense；T2V/I2V 不等于 V2V。[VG002–VG006] |
| Wan2.2 S2V | `Wan2.2-S2V-14B`，给定音频、参考图、可选姿态与文本 | 官方记录 2025-08-26；音频驱动视频不等于文本联合生成原生音频。[VG012–VG013] |
| Wan2.2 Animate | `Wan2.2-Animate-14B`，角色动画/替换等特定路径 | 官方记录 2025-09-19；不与 Animate-2 合并。[VG012] |
| Wan-Animate-2 | `Wan2.2-Animate-2-14B`、Diffusers 与 Distilled-Diffusers 权重 | 报告 arXiv:2608.06009，首次提交2026-08-06、v2为2026-08-08；报告Lite的3-step蒸馏与README当前10-step示例不是同一复现配置。报告日期不代替每个权重/代码首发日期。[VG016] |
| Wan-Dancer | `Wan-Dancer-14B` | 官方代码与报告arXiv:2607.09581，首次提交2026-07-10；属于人物动作定制/动画研究路径，未建立生产SLA。[VG015] |

这些对象的原生/转换 Diffusers ID 分别保留在库存 JSON。`-Diffusers` 表示权重布局或实现转换，不自动表示新基础模型。控制输入、角色替换和长片分段对预处理、额外编码器、显存及质量指标均有影响。

### 托管 API 是另一条发布轴

Alibaba 当前 overview 还列出 2.5/2.6/2.7 服务，Wan3 API 当前列 `wan3.0-video` 和 `wan3.0-video-prime`，标注 preview。API 文档显示异步提交、任务查询、结果下载等服务行为。[VG017–VG018]

这些 ID 能证明“存在文档化接口”，不能证明公开 checkpoint、架构参数、VAE 压缩、精度或本地部署引擎。具体 T2V/I2V、参考视频、编辑、音频或多镜头输入能力必须落到具体 model ID、请求字段、region 与当前版本上。本文不把搜索结果中的 Wan2.7 “开源”“DiT”“参数量”说法转成事实，也不从旧模型为 Wan3 补参数。

生产支持同样分层：public research code、某 runtime 的 pipeline、托管 preview、已验证的生产服务 SLA 是不同证据。此处没有本地推理实测，也没有供应方 SLA 的独立验证。

## 3. 架构与机制对照

### Wan2.2 基础路径：具体常数决定预算

| 项目 | TI2V-5B | T2V-A14B / I2V-A14B |
|---|---|---|
| 结构 | dense DiT | 高/低噪声专家；按 timestep 切换 |
| 官方参数口径 | 5B 标称 | 总计约 27B，单步活跃约 14B；均为约数 |
| 隐藏维 / 层 / 头 | 3072 / 30 / 24 | 5120 / 40 / 40 |
| FFN 维 | 14336 | 13824 |
| VAE stride `(T,H,W)` | (4,16,16) | (4,8,8)，沿用 Wan2.1 VAE |
| latent channels | 48 | 基础输出为 16；I2V 输入另拼条件通道 |
| patch `(T,H,W)` | (1,2,2) | (1,2,2) |
| 默认帧 / fps | 121 / 24 | 共享默认 81 / 16 |
| schedule | 50 steps；shift=5；guidance=5 | T2V：50、shift=12、guidance=(3,4)、boundary=.875；I2V：40、shift=5、guidance=(3.5,3.5)、boundary=.900 |
| 空间规格 | “720P” 档含精确 1280×704/704×1280 | 官方 T2V/I2V 支持 480P / 720P；具体运行仍记录精确像素 |
| 文本条件 | UMT5-XXL；text_len=512 | 同共享文本配置 |
| 图像条件 | TI2V 的独立 I2V 路径 | 检查到 I2V-A14B 用 VAE 编码与 mask 条件；config `image_dim=null`，当前路径没有独立 CLIP 调用 |

来源：官方 `wan_ti2v_5B.py`、`wan_t2v_A14B.py`、`wan_i2v_A14B.py`、shared config、HF transformer/VAE configs、`textimage2video.py`、`image2video.py`。[VG004–VG010]

这张表给出的是检索到的具体配置，不是所有接口的最大时长/最大分辨率，也不是历史源码审计。可接受的整数形状不等于训练质量保证。把 121 帧、24 fps 写成所有 Wan 的默认值，或把 A14B 的 CLIP/旧 VAE 印象移给 5B，都会破坏算例。

### S2V 与控制/动画路径

[S2V 技术报告](https://humanaigc.github.io/wan-s2v-webpage/content/wan-s2v.pdf) §3 描述 VAE 视频潜变量、Wav2Vec 音频特征、时间对齐的 Audio Blocks，以及 FramePack 对历史运动帧的额外压缩。音频 cross-attention 按时间片对齐，不是把全音频与全部视频 token 一律做同一种 full attention。当前 S2V 配置为 VAE stride `(4,8,8)`、25 fps、80 帧 clip、40 steps，并有音频长度/分段延续逻辑。[VG013]

S2V 报告 §4.1 对含音频编码器和交叉注意力的训练系统写出超过 16B 参数。`S2V-14B` 是基座/产品标签，不宜被解释成所有附加组件相加后的精确参数总数。报告的 8 GPU 训练加速不是推理速度证据。

[VACE 报告](https://arxiv.org/html/2503.07598) §3.3 将帧、mask、参考信息统一为 condition representation。Context Blocks 增加额外执行与状态，编辑输入也增加解码/编码成本。Wan-Dancer 与 Animate-2 的动作用例进一步改变前处理和质量判据。它们值得在研究附录中保留，但正文不需要为每一种路径追加一套教程。

[Wan-Animate-2报告](https://arxiv.org/html/2608.06009)还提供一个必要反例：Base采用reference/denoising双分支、Time-Align RoPE和Sparse-Ref Attention；Lite通过causal mask转成chunk-wise AR，Figure2将driving stream分成8帧片段，当前chunk可看前文clean latents与本chunk其他noisy positions。这既不是全片非因果attention，也不是文本每次只生成一个token。它允许更早的chunk输出，但有历史状态、上下文长度与跨chunk误差传播问题。报告§4的teacher-forcing、error-buffer与self-forcing正针对训练—推理差异。未检索到足以确认具体KV-cache布局或无限长恒定内存的证据；不把Base、Lite和当前Distill示例当同一可运行recipe。[VG043]

### 精选比较：不同机制如何改变系统

| 比较对象 | 有依据的机制 | 可迁移的取舍，不是排名 |
|---|---|---|
| HunyuanVideo-1.5 | 8.3B DiT；VAE 4×16×16、32 channels；Qwen2.5-VL与Glyph-ByT5；报告Figure2/配置一致：patch=(1,1,1)、54个双流block、hidden2048、16头、head_dim128；SSTA、蒸馏、视频SR | latent压缩与稀疏注意力是不同轴；高分辨率可以依赖附加SR pass。特定T2V sparse/distilled权重在README仍可能是Coming soon，报告结果不证明全部已交付；此处不推测Qwen encoder参数量。[VG022–VG023] |
| LTX-2 | 音视频双流 DiT；视频 VAE 8×32×32；Gemma 3 文本条件；多阶段与空间上采样 | token 数减少不等于所有阶段免费；音频、自注意力与跨模态注意力、额外 pass 和重建均要计入。报告摘要 14B+5B，结论 13B+3B；本研究不择一消除冲突。[VG019] |
| LTX-2.5 | 官方 release notes 标记 2026-08-11；官方 v0.42 文档标称 22B | 属单独版本。gated raw card/config 返回 401，本研究未绕过访问限制，不能直接沿用 LTX-2 层数/VAE 常数。[VG020] |
| Wan3 API | 当前官方异步 preview 接口 | 外部可观测到任务/时延/收费与媒体契约；不能据接口推定 HBM、专家结构或自托管能力。[VG017] |

Hunyuan README 发布代码/权重记录为 2025-11-20，而 LICENSE 页眉的 Release Date 为 2025-11-21；保留两种原始口径，不默改为单一日期。LTX-2 报告首次提交为 2026-01-06，不把该日期自动当所有代码/权重首发日期。

此处不增加未经原始来源核实的“最新 Open-Sora”条目。有限对象已覆盖三种高杠杆设计：压缩/全片 attention、稀疏/蒸馏、音视频联合与多阶段；继续扩展目录的边际解释价值较低。

## 4. 可复算资源预算

`verify_sources_and_math.py` 生成 `calculations.json`。所有下列数值为解析推导；没有推理运行、GPU 速度、功耗或峰值 HBM 实测。

### 4.1 形状与单位

一般对齐形状下，先求实际 VAE 输出 `T_l,H_l,W_l`，再按 patch `p_t,p_h,p_w` 得到 `N=(T_l/p_t)(H_l/p_h)(W_l/p_w)`。边缘 padding、首帧约定与 sequence parallel 向上取整都必须落到具体实现。不能对未知 VAE 套一个泛化压缩率。

选 Wan2.2 TI2V-5B 的 T2V 路径，F=121、H=704、W=1280：

- `T_l=floor((121−1)/4)+1=31`。
- `H_l=44，W_l=80，C=48`；latent cells=109120。
- patch=(1,2,2) 后 `N=31×22×40=27280`。
- fp32 初始 latent payload=20951040 bytes；若另作假设 BF16 payload 则为10475520 bytes。初始 noise 源码明确 FP32，不把后者当实际 dtype。[VG010、VG024–VG025]
- 24 fps 下末帧 timestamp 跨度=(121−1)/24=5 s；恒定帧时长容器的 span=121/24≈5.0417 s。两种口径不能互换。

### 4.2 Attention、workspace 与完整模型

按 multiply-add=2 FLOP，batch=B，hidden=d，heads=h，元素字节数=s：

- dense 非因果 self-attention 核心：`4 B N² d FLOP / layer / evaluation`。
- cross-attention 核心：`4 B N M d`，M 是实际条件长度；不等于把文本 M 当视频 N。
- 一个 hidden：`B N d s bytes`；Q/K/V 三个相同形状张量合计 `3 B N d s`。
- 若物化 score：`B h N² s bytes`。这是朴素实现的单个 score payload，不是所有算法的峰值内存。
- 若是理想固定窗口 attention，pairwise 核心可按实际邻域量级变化；Hunyuan 的选择/滑窗稀疏机制还含 selection 与 kernel 开销，不能直接保证 `4Nwd` 的现实速度。

5B worked example中，d=3072、h=24、layers=30：

- 一个假设 BF16 hidden 为167608320 bytes。
- QKV payload 为502824960 bytes，但融合布局可能不同。
- 假设物化 BF16 score 为35721523200 bytes=33.2682609558 GiB。
- attention 两个核心 matmul 为9144709939200 FLOP/层/分支求值，约9.145 TFLOP。
- 30层为274341298176000 FLOP/求值。
- upstream 50 个 timesteps 每次各算 conditional/unconditional：100 个单样本分支求值；attention 核心合计27434129817600000 FLOP≈27.434 PFLOP。[VG026–VG027]

这是 attention 核心而非全模型。QKV/output 投影、FFN、time/text embedding、cross-attention、normalization、softmax、VAE、host/device transfer、通信与编解码未包含。不能用这个数除以峰值 TFLOP/s 来宣称端到端时延。也不能把 score=33.268 GiB 写成“模型一定至少需要这么多 attention HBM”：FlashAttention 类 tiled exact attention 避免保留整个 score，但不自动消除 dense pairwise arithmetic。

### 4.3 steps、NFE 与缓存

本包把 scheduler timesteps、单样本 branch evaluations、实际 forward invocations、完整网络/部分缓存网络执行分别记录。upstream 5B 的50步双 CFG分支为100个branch evaluations；拼成batch时forward调用数可能减少，算术仍处理两份样本。蒸馏、guidance-distill、跨步feature cache改变执行图，不能继续用同一个100。

默认 Wan attention 明确 `causal=False`，`window_size=(-1,-1)`。VAE 的 temporal causality 不证明 denoiser 是 causal AR。每步 latent 改变后，视频 K/V 通常重算；不能把本书 AR persistent KV 公式直接作为跨采样步增长的缓存。静态 text encoding、已实现的 text projection cache、VAE chunk cache、近似跨步 feature cache是不同机制。[VG008–VG009、VG029]

LTX 检索到的 SDPA backend 同样显式 `is_causal=False`，也支持 mask。此证据只覆盖检查到的路径，不能泛化到 LTX2.5 全部 streaming/chunk 配置。[VG021]

### 4.4 灵敏度与常驻权重

121→241帧使T_l从31变为61，token数变为53680，比例61/31≈1.96774；dense pairwise项比例≈3.87201。H/W各翻倍时token×4、pairwise×16。较大形状仅是代数压力测试，不是发布质量/硬件支持宣称。[VG028]

权重 payload 另计。用官方约数与BF16作示意，5B为约10000000000 bytes；A14B若约27B全常驻则约54000000000 bytes，约14B活跃对应约28000000000 bytes的参数子集。不是实际 checkpoint 计数或本次加载峰值；也不包括编码器、VAE、workspace和精度混用。某专家当前不运行，并不代表其权重已经离开HBM。[VG003、VG030]

## 5. 服务、并行与 fleet

以下架构建议属于提案/待实测假设，不伪装成已验证部署。

### 接纳与调度

请求契约应至少记录 `(model+revision, task, H, W, F, fps, conditioning, schedule, steps, guidance, precision, backend, parallel layout)`。按真实 token/工作/峰值内存分桶，而非只按视频秒数。不同 shape、sampler、timestep 与 guidance 分支混批可能产生 padding、控制流与编译开销。

全片去噪的一步通常更新全片，不是“输出下一帧”。若 runtime 暴露 step-boundary yield/cancel，才有把调度切在步间的实施基础；一次能调用pipeline不证明已实现continuous batching、preemption或恢复。短作业优先有利于交互但可能饿死长作业；需要 deadline、queue age 和分级配额。

预览与最终成片设独立 SLO。低步数/低分辨率预览不自动能原地延续成最终高质量recipe；中途解码出第一帧不代表其余帧已完成。交互指标可以是 time-to-first-valid-preview；生产指标是 accept→validated downloadable media 的 end-to-end。不得把 preview 当 clip goodput。

### 内存与异构放置

模型加载成功只是第一关。峰值分阶段测：text/image/audio encoders、denoiser、VAE decode、SR、编译、分支拼批、并行通信 buffer；allocator reserved/allocated 分开。OOM 接纳不能仅使用 latent payload 或总参数数。并行后既要检查每rank峰值，也要检查最慢rank与实际拓扑。

Wan2.2 官方单卡5B示例带offload/CPU T5并声称至少24GB；标准A14B单卡路径声称至少80GB。这些是供应方条件路径，不是本研究实测或任意形状保证。CPU offload节省HBM，但增加主存、PCIe与等待；频繁逐层offload与按噪声阶段换专家的transfer pattern不同。[VG030]

FP8/低比特、量化权重、容器格式、反量化与矩阵内核能力必须分开。Hunyuan README确实记录FP8 GEMM、cache等优化；不能推论所有GPU/attention/SR组件都可相同精度执行。质量退化包括时间一致性和音画同步，不只单帧清晰度。

### 通信与多GPU

Wan官方实现提供FSDP+Ulysses路径。5B heads=24，A14B heads=40；Ulysses分组必须满足具体整除约束。FSDP weight sharding、TP、sequence/context parallel不是同义词。把N分散可缓解activations或单卡计算，但引入每层/每步通信、padding与同步。按形状与拓扑实测 scaling，不能按GPU数量线性外推。[VG031]

异构卡更适合先比较独立replicas或分工pool，未必适合同步模型组。慢卡与低速链路可能拖住全组。Replica增加独立job容量；模型/序列并行改变单job可行性与时延，两者不能拿同一“clips/s提升”口径比较。

### 精确runtime证据

已核验正式GitHub release metadata和tag内文档：

| runtime版本 | published_at (UTC) | 已检查能力证据 | 截止关系 |
|---|---|---|---|
| Diffusers v0.35.0 | 2025-08-19 | Wan2.2 pipeline文档 | 截止前 |
| Diffusers v0.37.0 | 2026-03-05 | LTX-2 release支持记录 | 截止前 |
| Diffusers v0.40.0 | 2026-08-20 | WanAnimate2Pipeline文档 | 截止前 |
| Diffusers v0.42.0 | 2026-10-23 | LTX-2.5、HunyuanVideo15Pipeline文档 | 截止后，必须later snapshot |

这些是存在于正式tag的实现证据，不是本机安装、模型跑通、稳定服务或所有优化backend的验收。README尚保留“install from source”不能覆盖后来正式release；反之main文档也不能反推过去tag已支持。[VG032]

本包不编造安装/启动命令；只有已运行的研究与渲染复现命令。生产 serving engine 的调度、取消、job状态、限额、隔离、错误语义与支持GPU仍需单独验证。

### 完整成本与媒体链路

记录queue wait、cold/warm load、text/reference编码、sampling、VAE/SR、frames拷贝、video encoding、audio mux、safety scan、storage upload与delivery。Denoiser变快后CPU编码或上传可能接管尾延迟。模型下载/本地cache、checkpoint shard数、storage读带宽、解压转换、网络出口与输出保留期进入成本。

固定seed只控制某次随机初始化。保存generator、scheduler、timestep、dtype、GPU、kernel、驱动与engine版本；不承诺跨设备/内核bitwise一致。官方托管API也明确seed只能尽可能稳定，不保证完全确定。[VG038]

Goodput建议定义为同一观察窗内同时满足deadline、输出完整性、质量与安全条件的完成clip数/秒。frames/s、clips/s、generated clip-seconds/s并列且保留形状分布。拒绝、OOM、取消、重试、质量失败与后处理失败另报，不能从分母中消失。[VG041]

`cost_per_accepted_clip = total_allocated_cost_in_window / accepted_clips_in_window`。前者含idle/加载、失败尝试、encoding/storage/network与适用license；若没有合格clip则不能给出有限的每可用clip成本。不能从不匹配的GPU时长或峰值TFLOP推出价格。

## 6. 供应方基准与有界评测计划

### 已找回的原始结果

| 来源 | 原始工作负载与结果 | 不能推出的结论 |
|---|---|---|
| Hunyuan1.5报告§6/Table7 | CFG-distilled；8×H800/context parallel；720×1280；241帧；dense5.5070±.0284s/step，sparse2.9475±.0206s/step；dense用FA3，未加入工程优化 | 不是每层ms、不是单卡、不是成片耗时。fps/precision/sampler/commit未齐。[VG033] |
| 同报告Table8 | 同硬件/形状；50steps；加入SageAttention、torch.compile、featurecache；dense96.78s、sparse58.39s | 不能跨表独立归因某一种优化；报告没有清晰覆盖所有媒体处理的时间边界；缓存后NFE需要trace。[VG033] |
| LTX-2报告§6.3/Table1 | “an NVIDIA H100 GPU”；121帧；720p标签；single-stepEuler、CFG=1；Wan2.2-14B22.30s/step，LTX-2 1.22s/step | 精确像素、fps、precision、enginecommit、匹配成片质量不全；比值不等于usable-clip成本倍率。[VG034] |

`benchmark-evidence.json` 对缺失字段使用null而不是默认值。上述全部为vendor-reported；本研究没有独立复跑。Hunyuan报告另给单卡offload/tiled-VAE的13.6GB峰值路径，但不能与8卡速度表组合成一个“13.6GB且58.39s”的虚构配置。

### 建议的最小实验（未执行）

目标不是做跨模型排行榜，而是检验一个可部署recipe的正确性与首要瓶颈。

1. 固定公开checkpoint revision、engine/tag/commit、依赖/驱动、单一GPU型号及数量/拓扑。先选TI2V-5B原始T2V形状121×704×1280；没有合适GPU或权重存储时明确阻塞，不用模拟替代推理。
2. 固定12条有权使用的prompt，覆盖静物/纹理、单人/多人、动作/相机、遮挡/对象持续性、文字、复杂物理。每条2个seed，基线24个clip。只增加一个优化变体形成48个paired clips；warm-up不计质量样本，单列cold runs。
3. 预算预先限制为2 GPU-hours；超时/OOM即停止并报告被截断的case，不能把未跑样本计入完成数。此预算是提案不是已占用资源。小样本可发现故障，但不足以认证p95/p99或生产容量。
4. baseline后只改一个轴，例如steps、sparse/feature-cache、quantization或offload；保持任务与输出契约。不同模型的压缩/任务不一致时做分层comparison，不假装同一数值shape等于同一质量成本。
5. 每job trace accept/start、encoder、denoiser每步、实际forward/branch次数、per-rankGPU峰值、VAE/SR、encode/mux/upload、ready、cancel/OOM/retry；记录GPU power仅在实际测量可得时给出。
6. 前置质量gate：prompt adherence、identity/object persistence、flicker、motion continuity、geometry/physics、文字；有音频时加lip-sync、speakerassignment与audio-videooffset。保留失败输出，不只选好例子。人评盲测与逐维自动指标并列，不用单个总分遮蔽重大故障。
7. 输出质量—latency—allocatedGPUtime/acceptedclip的paired点与置信/样本限制。不生成未经测量的curve，不为失败或没跑的case补数字。
8. 再做有限到达率的queueing实验才谈SLO-goodput。先有单jobtrace与memory envelope，再进行mix-shape、cancel/resume、冷启动、编码并发与storage网络压力测试。

## 7. 质量、权利、来源与安全

质量故障至少分开记录：单帧美术质量、prompt不一致、identity漂移、对象凭空出现/消失、遮挡恢复错误、flicker、肢体/几何变形、镜头运动和物体运动不连续、物理错误、文字破碎、重复运动、长时漂移。联合音视频还涉及声画偏移、多说话人分配、口型与音色。LTX报告明确写出语言覆盖、多speaker与长时一致性限制；这些是机制边界，不宜仅列一项“quality”。

Wan2.2及相关检查到的官方专门release标Apache-2.0；README另列使用责任。LTX当前`LICENSE-2_x`属communitylicense，对年收入至少10000000 USD的entity规定付费许可及有限非商业测试例外；redistribution/notice与使用限制另列。HunyuanVideo1.5 communitylicense的Territory排除EU、UK、SouthKorea，且有release-date口径下超过100millionMAU的商业授权条件与AUP。以上是检索文本，不是法律结论，也不保证所有组件/外部编码器的许可完全一致。[VG035–VG037]

API服务条款、公开权重license、输入image/audio/人物肖像/音乐权利、生成内容使用与来源声明是不同问题。建议provenance保留checkpoint/adapter哈希、engine与recipe、seed、素材权利、编辑历史、审核决定、输出hash；metadata若重编码可能丢失，必要时保留sidecar与审计记录。不声称已实现C2PA或watermark，也不把watermark当法律许可或真实性证明。

安全gate包括非自愿冒充、未成年人、隐私、欺诈、虚假信息与权利申诉流程。涉及真实人物的S2V/角色替换尤其需要授权和误用处理。内容审核在输入和最终media阶段都可影响排队、成本与goodput。未在本研究中测试供应方审核有效性或提出法律判断。

## 8. 如何延伸书稿，而不改掉因果主线

已阅读相关实际源章节Ch1/2/3/7/8/11/14/20，并依据`design/book-architecture.md`的constraint hierarchy、证据双轴和anti-catalog规则提出候选。Ch2实际源文开头是AR的prefill/decode定义，Ch7/11以KV与文本serving为核心；不是本次发现它们数值有错，而是全书若扩到视频，就需要明确范围。

`proposed-insertions.md`已提供实质英文段落，不是outline。建议只让一个workedexample承担video算术：

- Ch2 §1：在因果链段落后补一个工作单位scope bridge。
- Ch3 §6：在2026baseline讨论后补噪声阶段专家与常驻边界，放FigureV2。
- Ch7 §2：AR persistentKV的范围；不改canonicalKVtable。
- Ch8 §6：放唯一的5Bvideo预算与FigureV1，避免多章重复推导。
- Ch11 §6：把四项servingconcerns映射到whole-clipjobs，不把KVpager复制成视频方案。
- Ch14 §4：视频benchmarktuple与计时边界。
- Ch20 §6：acceptedclip与shape-awarefleetunit；不重新编造host数量。
- 独立datednote：精选模型/engine/API比较与可见性/许可缺口。正文只引用，不塞进型号目录。

以上锚点与源行号在英文文件中给出。它们是源Markdown位置，不是物理PDF页码。361页与USLetter由任务给定；build检查证实`letterpaper`与左右1.2inmargin，textwidth=6.1in。本次不重新计页、不改PDF、不作完整渲染页面审稿。

### 哪些保持冻结

canonicalQ&A的流量、9.2K/300token、KV与host算术、主图编号、封面、整书render/publication状态全部保持不动。不能用视频例子偷偷改全书单位，也不能在没重建/审版前说新图已在书内。

### 截止日期控制

建议采用“2026-10-28视频系统快照”作为显式controlledupdate；所有候选视频扩展共享这条范围声明。Wan2.2/Animate2/Dancer、LTX2.5等发布事件在8月截止前，不代表本次检索的main源码与10月engine文档在8月已相同。若要严格纳入8月冻结正文，还需把候选的源码/许可/runtime逐项回到截止前tag或commit再验；当前证据不冒充历史版本审计。

特别是Diffusersv0.42.0发表于2026-10-23，不能因为LTX2.5在8月发布，就写成该pipeline在8月已正式支持。Wan3preview的本次服务可见性也只能放current snapshot，未确立首发日。[VG020、VG032、VG040]

## 9. 仍然开放的事项

- LTX2.5 gated raw配置401；没有访问权限就没有精确结构审计，不绕过gate。
- LTX2报告参数口径冲突仍未解；不抄一个方便的总数。
- Wan3公开权重、参数、VAE、首发时间与自托管部署证据未建立。
- 专门Wan动画/控制路径没有逐个完整checkpoint计数、最大shape/时长/peakmemory独立实测；表中未知不是零成本。
- 供应方benchmarktuple未全；本研究没有可对齐的价格/usableclip数据，也没有任何本地GPU推理或生产SLO测量。
- 当前源码证据不是截至2026-08-30的历史checkout；严格冻结整合还需历史验证。
- 图像standalone检查不等于最终PDF页检查。整合后图号、caption、分页、placementscale、灰度实际印刷与最终pageproof由主任务复验。

研究文件可交接不等于上述未知被解决，更不等于出版就绪。
