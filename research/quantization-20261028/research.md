# 量化不是一个格式选择：从数值表示到可验证的部署配置

研究日期：2026-10-28 UTC（工作开始于 2026-10-27 PDT）。本报告是独立研究与未应用提案，不是出版审计，不作 readiness 判断。用户提供的当前书稿身份为 361 页、US Letter 8.5×11；本任务没有重数 PDF、检查渲染页或做印刷验证。工作只写入本目录，没有委派、书稿修改、提交、推送或配置变更。

## 1. 最值得纳入本书的结论

量化应接入本书既有的因果链：工作负载 → 允许的质量损失 → 哪类张量压缩 → 实际编码与元数据 → 可用内核 → 内存/流量/计算变化 → 目标 SLO 下的有效产出。不是再添加一份“4-bit 技术排行榜”。

最重要的区分有 6 个：

1. AWQ/GPTQ 主要回答“量化值怎样选”；GGUF 回答“张量与模型元数据怎样装入文件”；MXFP4/NVFP4 回答“值和共享尺度怎样表示”。这几个名称不是同一层的候选项。ModelOpt 同时提供 INT4 AWQ-lite 和 NVFP4 AWQ-lite recipe，是方法轴与表示轴可以组合的直接代码证据。[Q01–Q05, Q28]
2. “4-bit”不是实际每参数 0.5 B。MXFP4 的紧凑 block 是 17 B/32 值，即 0.53125 B/value；NVFP4 常见 1D 路径是 9 B/16 值，再加 tensor-global scale。GGML Q4_K 是 144 B/256，即 0.5625 B/value。数字相同的有效位宽也不代表编码相同。[Q07, Q10, Q13]
3. “支持某 checkpoint”与“以该位宽原生计算”必须分开。已读 vLLM 代码存在 NVFP4 原生 CUTLASS、Marlin W4A16，以及反量化到 BF16 的 fallback。MXFP4 Marlin 代码还明确说明会忽略请求的 activation quantization。[Q19–Q21]
4. 量化权重不自动量化 KV。权重、激活、KV、梯度/优化器和通信各有自己的 dtype 与 scales。长上下文部署仍须独立重算 KV 和分页/scale 开销。[Q18, Q34]
5. 数值格式没有提供任务准确度保证。PTQ 的校准、QAT/QAD 的恢复、保留高精度层、真实导出内核及评测样本共同决定结果。NVFP4 训练论文也不是只把 dtype 改成 FP4。[Q14, Q29]
6. 本书截止日为 2026-08-30。OCP 1.1（2026-10-09）及本次读取的 October upstream 支持条件不能静默写进 August snapshot。机制可以引用截止日前的论文/规范；新内核能力必须留在独立日期框或下一版。[Q11, Q24]

全部 claim 的证据与限制在 claims.json；全部原始 URL、修订、访问时间及 SHA-256 在 source-index.md 和 evidence/sources.json。文中 Qxx 是本研究 ledger ID，不冒用书中 [S#] 编号。

## 2. 范围、证据等级与时间边界

已读取 controlling MASTER_INSTRUCTIONS.md，采用其因果重建、独立推导、来源与时间一致性要求；本研究不扩张为全书逐页审校。相关书稿源文本覆盖 Ch5、7、8、11、14、15、18、26、Appendix A（chapter-27）及 Sources, Method, and Reproducibility。章节定位见第 10 节。页码尚未通过当前渲染 PDF 核对，所以只给文件/行和短文本锚，不虚构物理页码。

书中实际三轴 taxonomy（render/latex/backmatter/sources.tex:7–55）：

- Axis 1 来源：[1P]、[2°]、[LAB]、[ILLUSTRATIVE]；内部 canonical scenario 另有明确来源说明。
- Axis 2 状态：[FACT]、[DERIVED]、[ASSUMPTION]、[HYPOTHESIS]、[UNRESOLVED]。
- Axis 3 测量阶段：[ANALYTICAL]、[ILLUSTRATIVE]、[MODELED]、[MEASURED]；未测为 [UNMEASURED]。

本报告的规范/代码定义用 [1P][FACT]，字节算术用 [1P][DERIVED][ANALYTICAL]；新 70B 敏感性示例用 [ILLUSTRATIVE][DERIVED][ILLUSTRATIVE]。这里执行了算术，不把它记成 [LAB][MEASURED]。原论文/vendor benchmarks 即使存在，也没有被本研究复测；没有把来源的速度或质量数字移植为部署结果。

已取证的时间层次：

- GPTQ：2210.17323v1（2022-10-31）及 v2（2023-03-22）。AWQ：2306.00978v1（2023-06-01）、v5（2024-07-18）及当前 v6（2026-04-25）。本研究的定义交叉比对原论文与代码，正式候选引用明确版本，不把 abstract 的 latest revision 当作最初发布日期。
- OCP MX 1.0：2023-09-07；OFP8 1.0：原文日期 2023-06-20，版本表有 2023-12-01 bias 修正。NVFP4 官方介绍：2025-06-24；NVFP4 训练论文 2509.25149v2：arXiv 2026-03-04，而文档页眉为 2026-03-06，两者保留，不自行“修正”。
- OCP MicroXcaling 1.1：2026-10-09。版本表明确将 E8M0 改称 UE8M0，并调整转换与边界定义。MXFP4 表仍为 E2M1、32 值、8-bit scale，不能因此把两个版本说成毫无变化。[Q11]
- GGML block/llama.cpp 与 engine 代码是本次固定 commit；例如 llama.cpp 8ca4060b7e30e76baaa5670ee1ec1b760b7f8552，vLLM 41dd82e6a7392ead33b1e8a7d175442511e488ca，ModelOpt 580ffff1cddb9b20a38b7434e6290654ebf96a8f。精确 commit 日期在 evidence/code_pins.json。GGUF 规范另取 ggml 固定 revision da8e2a54b919557b816b1c2beb432ccb766f7ce0。
- live docs 无确定发布日期的条目标为“发布日期未建立”，而不是把抓取日写成发布日。GitHub latest release API 本次返回 ModelOpt 0.47.0（2026-09-23）、vLLM v0.32.0（2026-10-18）、SGLang v0.5.22（2026-10-19）、TensorRT-LLM v1.2.1（2026-04-20）。这些 tag 不自动包含本次 HEAD 的功能。没有做 tag 到各 kernel 的逐文件映射。

August 版可直接讨论的稳定机制，以截止日前明确版本的论文/规范为基础；本次发现的 GGML 结构、mixed-policy 细节、engine fallback、ModelOpt preset 只能作为 October 实现证据。若要声称它们在 August 已支持，需要补历史 tag/commit 证据。

## 3. 机制优先的分类，不把名词排成单轴

建议在 Ch7 放一个五字段“精度配置”，不是再创一套 evidence taxonomy：

`配置 = (目标张量, 值表示与scale, 误差控制方法, checkpoint封装/布局, 执行内核与硬件)`

另外记录训练/校准阶段、每层例外和 KV 策略。例如“某模型 AWQ”仍缺少 weight bits、group、scale/zero dtype、packing、activation/KV dtype、排除层、backend 与版本。正确的对象是可复现配置，而不是量化名。

### AWQ 与 GPTQ：方法轴

AWQ 用校准集的 activation statistics 识别显著通道，通过等价通道缩放降低权重量化误差。名字中的 activation-aware 不表示激活已经压成低位；原论文目标是 weight-only。论文先用少量 FP16 salient weights 解释现象，最终方法避免依赖那种不规则混精度存储。因此不能定义为“99% INT4 + 1% FP16”。[AWQ-V6 §3；Q01–Q02]

GPTQ 通过层输出重建目标和近似二阶信息，在量化部分权重后补偿剩余权重误差。原论文明确没有包含 activation quantization，也说其当时内核的收益来自压缩访存，而非直接加速混合精度乘法。group size、对称/非对称、activation order/排列、g_idx、实际 packing 是实现配置，不能归结为一个固定“GPTQ 格式”。[GPTQ-PAPER §2–4；GPTQ-ALGO；Q03–Q04]

两者均属于无需完整重训的 PTQ 路径，但校准数据不是无关紧要的输入。校准分布、长度、模态及敏感层是否保留影响质量，论文对某组任务的结论不保证当前 reasoning/tool workload。

### GGUF 与 GGML：封装轴和编码轴

GGUF 规范定义 header、metadata、tensor descriptors、每个 tensor 的 type 与 offset，以及 alignment；规范默认 general.alignment 为 32。它可以装浮点、整数块、K/IQ、MXFP4 等不同 tensor encodings。因此“GGUF vs AWQ”不是编码层面的公平二选一。[GGUF-PINNED；Q05]

K 家族不是一个“整数 q × 单 scale”的统一布局。Q2_K/Q4_K/Q5_K 有 affine 类 min/scale 的层次结构；Q3_K/Q6_K 使用不同尺度结构。Q4_K 是 8×32 的子块组成 256 值 super-block，包含两个 FP16 super-scales、12 B 的压缩 scales/mins、128 B 四位数据。不存在可直接套给所有 K 家族的 zero-point 字节数。[GGML-BLOCKS；Q07]

IQ 家族也不是同一种标量浮点。IQ2/3 的若干实现解码 grid indices 和符号；IQ4_NL 用非均匀 lookup table；IQ4_XS 又有不同 scale packing。共享 codebook 在实现中，不是每个 block 都存一份 codebook。imatrix 是量化时使用的代表性激活统计，不是 KV，也不是推理所需完整校准集。部分低位路径会因为缺 imatrix 而拒绝量化；另一些可选用它，不能统一写成“所有 GGUF 免校准”或“所有 IQ 必须校准”。[GGML-QUANTS；LLAMA-IMATRIX；LLAMA-MIX；Q08]

`Q4_K_M` 是模型级选型 policy，不是 `block_q4_K` 的新结构。已读代码可将 attention value、FFN down 等某些 tensor 提升到 Q6_K，条件还依赖架构和层位置。因此文件的平均 bit/parameter 应按 tensor inventory 加权；不能给所有 Q4_K_M 模型一个精确常数。[LLAMA-MIX；Q06]

### MXFP4 与 NVFP4：数值/共享尺度轴

MXFP4（OCP 1.0）每个值是 E2M1，32 值共享一个 E8M0 无符号二次幂尺度。它没有 affine zero point；E8M0 不是普通带 sign 的 E8M0 float，也不表示零。规范区分元素编码与 block scale，允许软/硬件实现且不要求厂商支持全部 MX 类型。这是互换格式规则，不是“任何 GPU 都原生 FP4”的承诺。[OCP-V1 §4–6；Q09]

NVFP4 的常见 1D 定义是 `x = x_E2M1 × s_E4M3,block × s_FP32,global`，每 16 个值一个局部尺度。相对 MXFP4，它用更小 block、含 mantissa 的局部尺度及 tensor-global scale。尺度粒度/表示改变误差分布，也改变字节数；不是名称新旧带来的自动质量提升。[NVFP4-BLOG；NVFP4-TE；Q12–Q13]

必须另讲训练 recipe。TE 当前 NVFP4 weight 默认可用 16×16 的 2D scaling，activation/gradient 用 1D；gradient stochastic rounding、wgrad 的 Random Hadamard Transform、保留敏感末层高精度是额外算法。2D 方块共享“唯一 scale 信息”更少，但实际内核可能复制尺度、存 row/column 副本及额外 amax/inverse；不能把 2D 的信息下界称为所有 NVFP4 checkpoint 的实际 footprint。[TE-PRIMER；NVFP4-PAPER；Q14]

一个需要显式保留的实现差异：GGML `block_nvfp4` 为 64 值、4 个 UE4M3 尺度和 32 B 数据；reference dequant 函数直接使用这几个局部尺度，没有 tensor-global 参数。NVIDIA 的通用表示有 global scale。代码中同名 type 不证明 checkpoint 布局或数值范围可直接互换；本研究没有建立 GGML↔NVIDIA NVFP4 的完整转换一致性证据。[GGML-BLOCKS、GGML-QUANTS；Q15]

### FP8、INT8/INT4 与关联方法

OFP8 E4M3 和 E5M2 的 exponent/mantissa、Inf/NaN 语义及范围不同；FP8 本身没有规定 scale 如何选择。per-tensor、per-channel、per-token、blockwise 和 MXFP8 都不能只按“1 B”描述完整配置。MXFP8 的 E8M0 block scaling 也不等同普通 FP8 tensor scaling。[OFP8-FIXED；TE-PRIMER；Q16]

INT8/INT4 必须补 signed/unsigned、是否对称、scale/zero dtype 和 group；乘法可能是 INT8×INT8、低位权重反量化后×FP16/BF16，或其他混合路径。SmoothQuant 是把 activation outlier 难度迁移到权重的 W8A8 PTQ 方法，属于方法轴。[SMOOTHQUANT；Q17]

NF4 是 QLoRA 的非均匀四位表示；double quantization 压缩量化常数。QLoRA 的 frozen base、adapter、gradient/optimizer/activation 显存账不同于推理。NF4 的位宽不证明硬件支持原生 NF4 GEMM，也不能将 QLoRA 当作所有 FP4 训练的统称。[QLORA；Q17]

相关且应有限引入的新方向是 mixed precision 自动分配、NVFP4 QAT/QAD、局部 scale/误差优化，以及独立 KV 量化。ModelOpt 当前 recipe 同时支持更细的 MLP/expert-only 部署；这些是质量恢复与算子覆盖策略，不是一个可跨模型排名的新格式。ModelOpt 声称 GPT-OSS 的 MXFP4→NVFP4 cast 可 bit-exact，但文中同时限定 scale 指数跨度，并给 out-of-range fallback。只保留有条件结论，不推广为“量化之间随便无损转”。[MO-HF-PTQ；MO-HF-QAT；Q28–Q29, Q36]

## 4. 一张有架构用途的比较表

下表的字节数是已说明布局的 compact tensor payload 或其公式，不是整模型 disk/HBM，不是准确度排名。模型兼容性全部需要 architecture loader + layer/kernel 检查。

| 候选/层次 | 误差控制与典型角色 | 值/尺度/分组 | 含尺度字节示例 | 执行与关键门槛 |
|---|---|---|---|---|
| AWQ 方法 + group INT4 | 激活统计 PTQ；常见 W4A16，KV独立 | affine INT4；group可配，scale/zero布局由实现决定 | g128、FP16 scale+packed4-bit zero：0.51953125 B/W；TinyChat FP16 scale+scaled-zero：0.53125 B/W，未含pad | fused dequant/GEMM或其他backend；packing、shape、架构不可省 |
| GPTQ 方法 + group INT4 | 二阶误差补偿 PTQ；常见 weight-only | 对称/非对称、group和order可配 | 对称g128+FP16 scale：0.515625 B/W；其他布局另计g_idx/zero | 指定checkpoint dialect和内核；原论文速度不能移植 |
| GGUF封装 + Q4_K/IQ | K/IQ、可选/必要imatrix、mixed tensor policy | Q4_K 256值；IQ按具体type读struct/grid | Q4_K 0.5625；IQ2_XXS 0.2578125；IQ4_XS 0.53125 B/W | llama.cpp/backend逐type覆盖；GGUF本身不保证某engine支持 |
| OCP MXFP4 | 可用PTQ/QAT/模型原生低精度流程；W或W/A由recipe决定 | E2M1；32值/E8M0 scale | 0.53125 B/value | native block-scaled path、W4A16或emulation需分列 |
| NVFP4常见1D | PTQ/QAT/QAD；W4A4或weight-only依路径 | E2M1；16值/E4M3 + tensor FP32 | 0.5625 B/value + global scale | native Blackwell路径与Marlin/emulation是不同实验 |
| FP8/INT8 | PTQ/QAT；W8A8、W8A16或KV分别选择 | FP8需具体E4M3/E5M2；INT8需scale/zero/granularity | 数据1 B/value，另加各级scale/zero | 特定SM/ISA、算子、激活和attention coverage |
| NF4/QLoRA | frozen低位base + adapter finetune | 非均匀codebook；可double-quantize scales | 名义0.5 B/W，metadata另算 | 训练内存/反量化与服务GEMM不是一个承诺 |

计算出处：independent_calculations.py、calculations.json；定义出处：Q01–Q18。相同 0.53125 B/W 不意味着 TinyChat INT4、IQ4_XS 与 MXFP4 数值等价。

## 5. 独立字节账：执行结果与边界

运行命令：`python3 research/quantization-20261028/independent_calculations.py`。标准库 Fraction 做精确运算；选定结构另用 ctypes 检查本机 C-compatible 字段排布。19 个 block 结果及断言已通过。这里不是编译/运行 GGML 内核，也没有测模型 HBM。

### 5.1 block 例子

- Q4_K：2+2+12+128=144 B/256 → 4.5 bit/value。
- Q6_K：128+64+16+2=210 B/256 → 6.5625 bit/value。
- IQ2_XXS：2+64=66 B/256 → 2.0625 bit/value。
- IQ4_XS：2+2+4+128=136 B/256 → 4.25 bit/value。
- MXFP4：1+16=17 B/32 → 4.25 bit/value。
- GGML NVFP4：4+32=36 B/64 → 4.5 bit/value；该结构本身不含额外 tensor-global scale。

以上全为 [1P][DERIVED][ANALYTICAL]，根据本次 pinned block code。完整 K/IQ 表见 calculations.md。

### 5.2 同一个4096×4096权重矩阵

参数数 16,777,216；不含 bias、文件 header、非权重张量、padding 或额外 scale 副本：

- BF16：33,554,432 B。
- g128 INT4，FP16 scale + packed4-bit zero：8,716,288 B；4.15625 bit/W。
- g128 INT4，FP16 scale + FP16 scaled-zero：8,912,896 B；4.25 bit/W。
- 对称 INT4+FP16 scale：8,650,752 B；4.125 bit/W。
- MXFP4：8,912,896 B；4.25 bit/W。
- 1D NVFP4、一个FP32 global scale：9,437,188 B；约4.500001907 bit/W。
- 如果某 GPTQ dialect 还存 K 个 int32 g_idx，本例另加16,384 B。这不是所有 GPTQ checkpoint 强制存在的字段。

这些是明确布局的算术，不是“所有 AWQ 都比所有 NVFP4 更小”。AWQ reference WQLinear 还把 group slots 按特定方式填充：N=4096、K=4224、g128 时33组要占40个scale/zero slots，得到9,306,112 B、约4.303030303 bit/W。[AWQ-LINEAR；Q04]

### 5.3 padding不是一个统一百分比

- GGUF data alignment 32 的教学例：三个payload分别18/144/17 B，其起始offset为0/32/192，payload合计179 B，span到最后字节209 B；没有计header/metadata和最终pad。不能把 header 及所有 gap 算进“每个block scale”。
- 已读 vLLM `swizzle_blockscale` 把 M pad到128、K_scale pad到4。假设 scale shape 为129×257，则逻辑33,153 B，实际该pad矩阵66,560 B。它只是可复现shape例子，不是模型平均开销比例。[VLLM-NV-UTIL；Q31]
- TE 16×16 weight 2D scaling 对该矩阵的唯一scale信息只需65,536 B，加数据和一个global是8,454,148 B；这是信息下界，不是经确认的导出/驻留布局。不能与1D checkpoint总字节直接排名。

### 5.4 资源账示例：只变权重，不改canonical baseline

新示例明确假设：70B参数中98%用MXFP4、2%留BF16；80层、full-MHA KV宽8192，9,500 tokens/sequence；640 GB总池，固定64 GB runtime reserve。98%不是任何真实模型的实测比例；640 GB与64 GB沿用书中教学假设，不证明逐rank可放置。

| 量 | BF16权重基线 | 新mixed-weight变体 |
|---|---:|---:|
| compact权重 | 140 GB | 39.24375 GB（36.54859 GiB） |
| KV raw B/token | 2,621,440 | 不变 |
| 每sequence KV | 24.90368 GB | 不变 |
| 扣权重与reserve的KV预算 | 436 GB | 536.75625 GB |
| fractional storage ceiling | 17.50745 | 21.55329 |
| integer storage ceiling | 17 | 21 |

标签：[ILLUSTRATIVE][DERIVED][ILLUSTRATIVE]。尚未加入 tensor/global scale、padding、KV block/scales、加载/repack峰值、rank不平衡与新workspace。实际reserve不能无条件保持64 GB。这个例子说明：权重压得明显更小，KV不变时并发存储上界只有限增加；它不是21 req/s，也不是21条请求一定达到SLO。

## 6. 从表示到执行：实际兼容性门槛

每条部署配置至少通过以下门槛：

1. 模型/图：精确checkpoint revision、architecture、attention/linear-attention、expert layout、vision/audio分支、tokenizer、chat template、tool schema。
2. 张量：encoding、group/block axis、scales/zeros/global scales、order/packing、混精度例外、TP切分后shape与padding。
3. 内核：dense linear、MoE grouped GEMM、embedding/head、attention与KV reader分别检查；记录真实selected kernel与fallback。
4. 平台：GPU exact SM/ISA与compiled targets、engine commit/wheel、CUDA/ROCm/oneAPI、driver、PyTorch、FlashInfer/CUTLASS/TE/cuDNN等依赖。格式规范不能替代这层。
5. 资源/质量/SLO：steady HBM及load peak、任务级质量、TTFT/ITL/完成时间、请求级goodput，再讨论成本。

本次能够证实的条件，不把它们扩成全平台认证：

| 路径 | 本次一手证据 | 不得推论 |
|---|---|---|
| vLLM AWQ | pinned AutoAWQ config支持4-bit；默认支持half/bfloat16，最低capability helper为75；Marlin不合shape可fallback | 不代表每种模型/层、每种AWQ文件都可运行 |
| vLLM FP4 Marlin | helper为CUDA且SM capability≥75；NVFP4文档字符串为W4A16；MXFP4代码可忽略激活量化请求 | 不能写“跑了W4A4/原生FP4”；SGLang自己的gate不同 |
| vLLM NVFP4 CUTLASS / emulation | 代码有input FP4量化、blockscale swizzle、padding；另有dequant→BF16 fallback | build已包含支持、runtime已选中该kernel均未验证 |
| SGLang modelopt_fp4 | 官方当前文档列SM80–SM90 Marlin，SM100/120 FlashInfer/CUTLASS；cuDNN backend列CUDA13+、cuDNN9.15+；online MoE路径另列SM100/103 | 不能用一行“Blackwell”覆盖全部后端、SM与模型 |
| TE |安装页CUDA12.1+，Blackwell12.8+，cuDNN9.12+；这是TE要求 | 不等于TensorRT-LLM HEAD或所有FP4 engine的依赖 |
| ModelOpt→TensorRT-LLM | HF PTQ脚注NVFP4 inference为Blackwell+TRT-LLM1.2+；某些模型只支持HF export | quantizer支持不等于backend该模型算子完整可服务 |
| vLLM GGUF | 官方明确highly experimental/under-optimized；建议用基座tokenizer，配置转换有条件 | llama.cpp能加载不等于vLLM覆盖/速度相同 |

来源 Q19–Q27、Q35。SGLang当前矩阵还列AMD/Ascend/XPU等路径；特别是其 MXFP4 “supported” 行与“native instructions”不是同一问题。本研究没有完成各非NVIDIA ISA与内核映射，不依据总表的Yes宣称原生FP4，更不侵入其他agent的Intel研究目录。OpenVINO microscaling页面同样只能证明特定runtime的转换/执行说明，不证明目标CPU有原生FP4吞吐。

驱动需要特别保守：CUDA compatibility表给出的12.x≥525、13.x≥580是minor-version compatibility下限，带limited feature set/PTX限制；Blackwell支持、新PTX指令及特定wheel可能要求更高driver。没有一个已证实的“所有NVFP4部署统一最低driver”可在本研究中给出。[CUDA-COMPAT；Q23]

## 7. 来源之间的差异、成熟度与许可

已确定而不应掩平的差异：

- TensorRT-LLM support-matrix仍出现container25.06、TensorRT10.11；本次HEAD requirements却有cuda-python≥13、cu132 wheel index、torch2.14范围。这不是一组一致验证过的环境，也不是“文档全错”的证明。版本需要固定到同一release/container后重新核对。[Q24]
- vLLM通用量化总表仍以Volta→Hopper等旧列表示覆盖，没有足够信息描述新FP4路径；pinned code已经有MXFP4/NVFP4 kernels。总表缺某行不是不存在；代码存在也不是稳定release已包含。[VLLM-QUANT；Q19–Q21]
- ModelOpt有某模型可量化/可export脚注，不等于TensorRT-LLM/vLLM/SGLang三个backend同时支持。HF PTQ矩阵的部分VLM默认只量化language branch，vision保留高精度。[Q35]
- AutoAWQ README声明停维护，最后测试Torch2.6.0/Transformers4.51.3；AWQ原方法、TinyChat实现、llm-compressor等迁移路径不能合并成一个生命周期结论。[Q27]
- GGML NVFP4 block与NVIDIA全局scale表示差异、TE训练2D与常见推理1D差异、OCP1.0/1.1命名与边界差异，各需保留版本语境。[Q11, Q14–Q15]

成熟度只作可审计描述：AWQ/GPTQ有原始论文与多engine代码；GGUF/llama.cpp已有具体type实现，但外部engine GGUF路径可能仍标实验；NVFP4/MXFP4既有原生路径也有fallback，当前支持随SM、形状、模型、dense/MoE而变。本研究没有依据star/download数字给成熟度排名。

许可证检查：AWQ仓库MIT；GPTQ仓库Apache-2.0；llama.cpp仓库MIT；TE/ModelOpt/vLLM仓库Apache-2.0；TensorRT-LLM当前LICENSE说明主项目Apache-2.0并列其他许可代码。OCP MX规范本身适用OWFa1.0，而不是把规范当MIT代码。模型权重许可、校准数据许可、运行时二进制、CUDA/cuDNN/container条款仍需独立检查；“编码开放”不授予checkpoint商用权。没有下载权重，也未完成发行包依赖许可审计。[Q38；OCP-V1 License；TRT-LICENSE]

## 8. 为什么更小不保证更快

内存账至少拆为：checkpoint磁盘字节、steady tensor residency、常驻额外副本、load/repack峰值、activations、KV、workspace/allocator。磁盘可更小但load时生成高精度副本；scale swizzle可能填充；训练可能同时保存高精度master及两个方向的低精度副本。[Q14, Q19, Q31–Q32]

性能账至少拆为：逻辑算术量、所选kernel支持的dense/sparse峰值、实际traffic/request、achieved bandwidth、kernel time、端到端延迟及goodput。4bit→2×更高peak并非格式性质，必须明确hardware operand模式与计算路径。W4A16不能借W4A4的peak画roofline。

以第5节新mixed权重为例，若仍用密集2N有用操作数并仅计一次权重stream，batch1 intensity从1变为约3.567447 FLOP/B；这只说明理想模型中的权重字节项变化。KV/activation流量、conversion、scale读取、launch、collective、路由与scheduler都没计入。不能据此宣称3.57× token/s。高batch/prefill的GEMM若已compute-bound，反量化或fallback可能抵销权重流量收益；长上下文attention与KV可能接管瓶颈。

不比较不匹配的模型/硬件/上下文/精度数据。尤其不拿“另一个更大MoE的FP4吞吐”去证明本模型量化收益，也不把paper的“up to”提升变成fleet goodput。

## 9. 没有测量时的有限评测协议

这是待执行实验设计，不是已测结果。决策单位是“基座revision+量化recipe+engine/kernel+hardware+workload”。

第一阶段：固定一个代表性基座及一个可获得的FP16/BF16或原生发布基线。若模型只发布低精度权重，就明确缺少高精度因果baseline，不能声称“相对原始无损”。锁定tokenizer/template、image预处理、tool schema、reasoning effort、采样/seed、上下文与输出预算。先比较同engine；跨engine另立实验，避免把kernel/template差异归因量化。

第二阶段：校准集与测试集隔离，记录来源、hash、样本数和长度/语言/代码/图像分布。PTQ、imatrix、QAT/QAD用的数据及训练预算分别记账。逐层异常、router、vision/projector、normalization及输出head的高精度例外进入tensor inventory。长上下文包含真实长文和位置/依赖测试，不只needle题。

第三阶段：小规模sanity后运行以下任务集合，拒绝用perplexity单指标代替：

- reasoning：可验证多步答案、预算/思考长度、最终正确率，观察低位是否导致重复/过长/截断；固定reasoning effort。
- code：隔离环境中的单测、pass@1、编译/执行成功、补丁正确性；记录timeout和重试，不把syntax过关等同功能正确。
- tools/agents：schema合法率、参数正确率、工具选择/完成率、错误操作和重试总成本；使用mock或安全沙箱，不能让评测执行危险外部动作。
- multimodal：OCR、图表/空间/视觉推理及图文指令；固定resolution/crops/video frames；视觉分支是否量化单列。
- long context：短/中/声明部署上限3档以上的任务性能，覆盖prefill与长decode积累、KV精度、混合/滑窗层和prefix-cache场景。权重精度与KV精度做分离对照。

首轮可采用每个关键任务至少200个配对样本、每种负载3次重复作为资源有界的筛选起点，全部标 [ILLUSTRATIVE][ASSUMPTION]；稀有失败、p99和安全后果不能靠这个样本量认证。最终样本量由预先声明的可接受退化区间和统计功效决定；对配对任务差值给置信区间，负载测试说明时间相关性/重采样单位，不把少量运行的p99当稳定尾部。

第四阶段：固定同硬件与功率、同TP/PP/EP/DP、同max-batch/token budget、同缓存状态和到达trace，分开测低batch decode、高batch/prefill、混合队列。记录cold load与warmup、selected kernels、fallback日志、peak allocated/reserved HBM、KV allocation、工作空间、traffic/request、TTFT/ITL/end-to-end p50/p95/p99及错误率。goodput按满足质量门槛与全部所声明SLO的请求/有效token计，禁止只乘一个p95布尔指标。给cache命中/未命中分布并正确合并分位数。

第五阶段：预注册接受条件，包括各任务允许退化、tool安全失败上限、目标负载SLO及N−1/rollback。未通过quality gate的快配置不进入成本比较；通过后比较每成功合规任务成本与总token/重试，而非只看名义$/raw token。结果进入Ch18 routing/Ch25 ADR，不能默认为质量不足时“降量化”是无风险fallback。

## 10. 与现稿的最小整合

现稿已经讲了KV独立精度、memory floors、roofline移动与时间敏感engine表；不应写成“本书完全忽略量化”。缺口主要是配置层次、真实开销和从可加载到可部署的证据链。

| 位置与源文本锚 | 提案 | 不重复的作用 |
|---|---|---|
| chapter-05/chapter-05.md:15–17，五个selection surfaces之后 | 一段“模型候选实际是部署配置” | 将质量/模态与precision recipe绑定，避免只选模型名 |
| chapter-07/chapter-07.md:88，Table7-2解释之后、§4之前 | 主机制小节、紧凑比较表、block算术、一个新sensitivity box | 定义只有此处充分展开；不重写canonical140GB/24.9GB |
| chapter-08/chapter-08.md:141–145，decode intensity之后 | 一段“存储/执行路径决定哪条roofline” | 明确W4A16与W4A4，避免带宽/算力混用 |
| chapter-11/chapter-11.md:143–149，Table11-2及解释之后 | 精度配置兼容性gate；October细节放日期框 | 不把GGUF/AWQ/FP8当同一类型的support栏 |
| chapter-14/chapter-14.md，§4 Measurement | 量化配对评测卡，细节见本报告第9节 | 用任务质量+tail SLO接受配置，不搬paper speedup |
| chapter-15/chapter-15.md:57–64，decision map之后 | 一段新瓶颈与回归验证 | 字节节省不直接变goodput |
| chapter-18/chapter-18.md:129–149，Common Mistakes/quality-cost curves | 将路由单位绑定validated quantized variant | 低位模型不是未验证的随意fallback |
| chapter-26/chapter-26.md:23–40，workload-to-strategy matrix之后 | 短的quantization ADR/checklist引用 | 只保留决策卡，不重复技术百科 |
| chapter-27/chapter-27.md:5、53、151，freeze note与sources | 不改四家comparison；可另设“2026-10-28数值与实现补记” | OCP1.1、October backend能力与August证据隔离 |

候选英文文本在 proposed-insertions.md，全部未应用。新增两幅原始机制图使用本地研究编号 QF1/QF2，并非书稿正式编号：QF1 区分方法、表示、packing、container、runtime layout 与兼容内核；QF2 独立计算 MXFP4/NVFP4 的局部尺度及 tensor-global scale 字节。figure-plan.md 记录学习目标和版面依据；figures/manifest.json 记录源文件、PNG、复现命令、caption、alt text、prose anchors 与 claim IDs。实际 build 的 Letter 8.5in 减去左右各 1.2in，得到 6.1in 正文宽；两图按此宽度生成 600dpi PNG，最小字为 9pt。整图、细节及 Letter placement proof 的真实检查与修订在 figures/QA.md。整合后主表与图注仍需检查列宽、字号、分页，不能由 Markdown 正确或孤立图通过就判断全书印刷可读。

## 11. 明确缺失的证据与交付边界

未完成且不以推导替代：

- 没有目标GPU上的benchmark或quality eval，没有可匹配的reasoning/code/tool/multimodal/long-context结果，因此没有winner。[Q37]
- 没有下载、转换或运行实际checkpoint，没有核验tensor inventory总disk字节、steady/peak HBM、per-rank放置、global scale副本和workspace。
- 没有核验所有engine的August历史版本，也没有把October HEAD功能映射到latest release tag；当前支持页与requirements差异已明示。
- 没有证明GGML NVFP4与NVIDIA checkpoint的端到端转换一致性，也没有执行官方有条件MXFP4→NVFP4 bit-exact cast。
- 没有覆盖全部硬件ISA/driver组合、全部模型家族；非NVIDIA原生路径仍需专门验证。数字格式不提供完整model/vision/attention兼容承诺。
- 没有构建或视觉审校整合后的书稿PDF，没有物理印刷proof。已完成的仅是新增孤立图及其 Letter placement proof 的视觉检查；无publication readiness结论。

本目录包含真实抓取的原论文、规范和实现快照；失败URL也记录，不能因为fetch脚本exit0就声称每个URL成功。来源hash与claim text-anchor由build_claims.py逐条验证，算术由independent_calculations.py可重跑。候选涉及的稳定机制与October支持事实分离；是否采用候选内容仍需作者整合与后续验证。
