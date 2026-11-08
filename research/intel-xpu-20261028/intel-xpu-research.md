# Intel GPU/XPU：机制、支持边界与入书取舍

研究快照：2026-10-28 UTC（本机时区仍为 2026-10-27 PDT）；研究范围仅为公开资料和候选增补。正文作者仍为 Zhiqi Tao。本目录没有改动书稿、共享配置或其他研究者文件，也没有提交、推送或发布。

## 1. 结论：可进入候选集，不等于已经证明“崛起”

值得入书的变化是部署路径变得更可核查：上游 PyTorch 有 Intel GPU `torch.xpu`，vLLM 和 SGLang 有明确的 XPU 集成，llama.cpp 有原生 SYCL 后端，OpenVINO GenAI 有不同于 PyTorch 的推理路径。不能把这些信号合并成市场份额增长、普遍更低 TCO 或生产规模胜出的结论。[1][2][25][49][52][54][66][67]

最小连贯增补不是另加一章产品目录，而是：修正计算/通信章节的 CUDA 特指表达；在 serving 章节加入“完整支持路径”小节和原创建议图 IX-F1；在内存章节加入一个有条件的算例；在运维/经济性章节明确回退和支持成本；在 Appendix A 单独加入 2026-10-28 增补。具体英文成稿见 proposed-insertions.md。

图的学习任务是区分设备 API 与端到端服务资格。已提供 editable SVG、原始生成器、300 ppi PNG、矢量 PDF、灰度 PNG 和 US Letter 独立排版证明。最终检查记录在 figures/QA.md；不把独立图检查冒充整本书出版认证。

## 2. 身份定义：五个容易混淆的层次

| 名称 | 本文采用的精确定义 | 不能推出的结论 | 证据/claim |
|---|---|---|---|
| `torch.xpu` | PyTorch 的 Intel GPU 设备 API；调用、分配、stream 和算子执行入口 | Intel CPU、Gaudi、NPU 都使用这个设备后端 | [66], IX-001 |
| oneAPI / SYCL | oneAPI 是工具/库生态；SYCL 是编程模型。编译器、库、运行时、驱动各有职责 | 源码可编译就有相同 kernel 性能或数值结果 | [54][66][67], IX-019/026 |
| Intel GPU | Arc、Arc Pro、Max、Flex、D-series 等具体 GPU；资源和生命周期必须按 SKU | 所有系列共享同一显存、互连和 engine 支持 | [7]–[10][27][30][58] |
| Client heterogeneous system | CPU、集成 GPU 和 NPU 的系统组合；内存与功耗预算可能共享 | 各自 TOPS 能相加成为一个 LLM kernel 的吞吐 | [35][37], IX-003/018 |
| Intel Gaudi | 独立的 AI accelerator 架构、`hpu` 软件路径与 HCCL collectives | 是 Intel GPU XPU 的一个别名，或 XPU 支持列表自动适用 | [11][47][55], IX-002/028 |

oneDNN 提供深度学习算子实现，oneMKL 提供数学库；SYCL 编译/执行路径可调用这些库，也可能使用 engine 自有 kernel。Level Zero 是底层 GPU runtime/driver API 层，不是 continuous batching scheduler。不能画成“所有 engine 都依次经过 oneDNN 和 oneMKL”的唯一流水线。llama.cpp 的原生 SYCL 路径可以不经过 PyTorch；OpenVINO plugin 路径也不是 `torch.xpu` 的同义词。[25][54][66][67]

## 3. 硬件身份、资源和发布状态

下表均为厂商资料，不是本研究实测。GB 使用厂商十进制标记，不能与运行时报告的 GiB 直接相减。板卡功耗、处理器 package power、系统墙上功耗互不等价。未知项保留未知，不用同系列规格补齐。

| 精确产品 | 发布/可得性证据 | 单设备内存与带宽 | 计算精度与功耗边界 | 部署含义 |
|---|---|---|---|---|
| Intel Arc Pro B70 | 2026-03-25 公告称当日开始销售；未独立核查库存 [13] | 32 GB dedicated VRAM；608 GB/s。取回的数据表未写明内存类型，不擅填 GDDR6 [7] | 367 INT8 dense TOPS；160–290 W；Intel reference 230 W；native PCIe Gen5 x16 | 容量比 B60 大，不构成 70B 四位模型单卡可装的证明；伙伴板规格可能不同 |
| Intel Arc Pro B65 | 同一公告计划 mid-April 2026；数据表标头更新时间 2026-04-20 不是零售实测日期 [8][13] | 32 GB GDDR6；608 GB/s | 197 INT8 dense TOPS；200 W reference；PCIe Gen5 x16 | B70/B65 带宽相同而 INT8 峰值不同，decode 不能按 TOPS 比例推算 |
| Intel Arc Pro B60 | 2025-05-19 公告计划 June 2025 sampling，不是 June GA [32]；2026 独立作者叙述实际购得 [61] | 24 GB GDDR6；456 GB/s [30] | 197 INT8 dense TOPS；120–200 W reference；PCIe 5.0 x8 级板卡连接需核查实际 negotiated link | 小模型/量化的候选；多卡不自动形成单次可分配内存 |
| Intel Arc Pro B50 | 同次公告计划 July 2025 [32] | 16 GB；224 GB/s；press deck [31]，不能误写 12 GB | 170 peak TOPS；70 W total board power；不要与 BF16 FLOP/s 排名 | 16 GB 权重恰好等于标称容量仍没有 KV/workspace 空间 |
| Intel Arc B580 | 2024-12 公告：2024-12-13 开售 [33] | SKU 241598：12 GB GDDR6，456 GB/s [68] | 233 INT8 TOPS，精度/稀疏性不能由数值猜测；本研究不使用其作跨厂商峰值比较 | 容量和 driver/kernel 支持比游戏 benchmark 更相关 |
| Intel Arc B570 | 同一公告：2025-01-16 开售；ARK launch quarter Q4'24 与零售日期不是同一字段 [33][69] | SKU 241676：10 GB GDDR6，380 GB/s | 203 INT8 TOPS；板卡功耗未纳入本次已核实字段 | 不能套用 B580 的 12 GB 与带宽 |
| Intel Data Center GPU Max 1550 | Q1'23 launch；SKU 写 Expected Discontinuance Jan 2026 [9] | 128 GB HBM2e；SKU 3276.8 GB/s [9][10] | 专用 GPU 路径；本表不采用未逐 form factor 核实的功耗/计算峰值 | 历史连续性和现有资产候选；不是无条件的新采购默认 |
| Intel Data Center GPU Flex 170 | Q3'22；SKU 230019 [58] | 16 GB GDDR6；576 GB/s | PCIe 4.0 x16 上限；本次未证明它是当前 vLLM/SGLang 首选支持设备 | 不能因 `Flex` 出现在旧 IPEX-LLM 文档就推荐存量软件路径 |
| Intel Core Ultra X9 388H / Intel Arc B390 GPU | Q1'26、Launched [35] | 系统最大 96 GB、LPDDR5X up to 9600 MT/s；不是 96 GB GPU 保证可分配量 | GPU 122 INT8 TOPS、NPU 50 INT8 TOPS；25 W base/80 W max turbo 为处理器级，不是独立 GPU 板卡 TDP | 需预算 OS、CPU/NPU、其他进程占用、最大 allocation 和 sustained package power |
| Intel Gaudi 3 OAM 场景 | July 2025 V1 Rev.3 白皮书；IBM Cloud 可得性公告是供应方信号 [11][56] | 128 GB HBM2e，3.7 TB/s | 表 1：BF16/FP8 MME 各 1678 TFLOPS；导言约写 1.8 PFLOPS，不能把二者当额外独立实测；不同卡形/功率须分开 | HPU/HCCL 路径；24×200 Gb/s port，具体 scale-up/out 见下文 |
| Intel GPU D-series / Intel GPU D270，formerly Crescent Island | 2025-10-14 初次公告说 H2'26 采样 [6]；2026 Hot Chips 与 October OCP 更新，后者称 sampling underway [28][29] | Intel-branded PCIe card 160 GB LPDDR5X；partner options up to 480 GB；不能一律写 480 GB [28 footnote] | OCP 列 1.5 TB/s、1.3 PFLOPS FP8、350 W；本次未取得逐伙伴 SKU 的带宽/稀疏性/功率完整表 | 采样，不是已验证 GA；产品页的对竞品性能是 projection/internal analysis，不是可移植实测 [27] |

数据完整性反例：原先访问的 URL slug 写 Flex 170，但 SKU 230020 实际页面是 Flex 140。已排除 [48]，只用 SKU 230019 的 [58]。产品名出现在 URL 上不构成身份验证。SGLang 错路径 [15] 和 OMIX 的 Page Not Found [70] 也已隔离。

可得性资料还有内部冲突：B70 sheet [7] 的产品渲染旁写 “Intel version not available for purchase”，但 March 25 公告 [13] 明示 Intel-branded 与 partner 卡当日开始销售。这里不擅自判定哪一份准确，也不以 datasheet 的渲染说明抹去另一公告；库存与实际可购板卡保持未独立核验。厂商资料之间不一致本身就是采购验证项。

### 内存、互连和方向必须共同核算

`arithmetic.json` 由 build_registry.py 实际计算。一个理想 70B 四位权重张量为 35 GB，尚不含 scale、zero point、alignment、非量化层、KV、workspace。它已经超过 32 GB 和 24 GB。因此“B70 32 GB = 可单卡运行任意 70B Q4”被这个反例否定。两张 24 GB 卡的标称总量是 48 GB；可行性仍取决于分片、每 rank 峰值、复制层、KV 分布和 peer/host 路径。

Gaudi 3 的 24×200 Gb/s，换算为全部端口每方向 600 GB/s、双向合计 1200 GB/s。白皮书的八卡 HLB-325 场景把每卡 21 个端口用于到其他七卡的直连，余下三个用于 scale-out；理论每方向分别是 525 和 75 GB/s。不能把 1200 GB/s 写成一次 all-reduce 的有效带宽，也不能把它直接拿来除单向字节。Max 的 Xe Link 频率/端口指标同样不能转换为任意拓扑的 bisection guarantee。[11]

## 4. 当前软件栈：版本和支持边界优先于品牌

### 4.1 可追溯版本快照

| 项目 | 本轮取回的 release metadata | 内容固定点/实际边界 |
|---|---|---|
| PyTorch | v2.14.1，2026-09-30T19:14:48Z [22] | commit 5c4886908584029761b579af026dcfb627c84070；guide [66]。不能把 latest 自动替换到所有 engine requirements |
| vLLM | v0.32.0，2026-10-18T06:50:48Z [21] | commit 5df63a7203cdb9328d824a27b682e77c7b9928be；code [52]、requirements [53]、XPU guide [67] |
| SGLang | v0.5.22，2026-10-19T02:55:19Z [42] | 研究的 commit a1966e1b5d8b750b494d7e53cca1d2464f960038，commit 时间 2026-10-28T06:26:29Z，由 commit API 另行验证 [49]–[51][72]。main 的较新功能不能自动声称属于发布包 |
| llama.cpp | 开发快照，不冒称 semver release | commit 8ca4060b7e30e76baaa5670ee1ec1b760b7f8552 [41][54] |
| OpenVINO Runtime | 2026.4.1，2026-10-01T13:45:59Z [26] | 与 GenAI 包身份分开；live/nightly 文档不构成该 release 的全部能力保证 |
| OpenVINO GenAI | 2026.4.1.0，2026-10-01T13:52:44Z [71] | 机制页 [36] 是 live 文档，未逐项回溯到 release tag |
| Intel Gaudi software docs | 1.24.2 文档标头 [47][55] | 只核实 HPU/HCCL 身份与文档内容，未完成该 release 的 OS/container/model support matrix |
| IPEX / IPEX-LLM | retirement / archived [5][14] | IPEX 维护通告至 March 2026；当前不应默认先安装旧 extension；IPEX-LLM 还明示 known security issues |

PyTorch 的 pinned guide 把 2.5 起点称为 Prototype，当前示例包括 eager、`torch.compile`、FP32/BF16/FP16/AMP。它不是“所有算子都等价支持”的承诺。guide 区分 Max 的 RHEL 9.2、SLES 15 SP5、Ubuntu Server 22.04（>=5.15 LTS kernel）与客户端 Windows 11 / Ubuntu / WSL2 条件；Panther Lake 行又不同。不能把 Max 的 kernel 下限复制到 B70/Series 3。[66]

vLLM pinned requirements 是 `torch==2.14.0`、`triton==3.8.0+xpu`、`vllm_xpu_kernels==0.1.15.4`、`auto_round_lib==0.16.0`；guide 指定 Python 3.12，提供 `vllm/vllm-openai-xpu`，并建议 compute runtime 26.18.38308.1 以避免特定 kernel 兼容问题。然而同一 pinned guide 还写 Triton 3.7.2+xpu，且特定 graph path 要 oneAPI runtime 2026.1.1 系列。发现这种 docs/requirements 不一致时，正确结论是需要解析 lock、构建/运行测试，不是把两个版本拼在一起当一键配方。本研究未安装这些包，也未核查 wheel/container digest。[53][67]

SGLang XPU 文档示例使用 Python 3.12、torch 2.14.0+xpu 与 xgrammar 0.1.33，并警示避免依赖解析拉入 CUDA Triton。它同时有“only source”陈述和 prebuilt `v0.5.22-xpu` Docker 指令，不能摘一句宣布不存在容器。Dockerfile 和 communicator 也取回了，但没有实际 pull/build。[49]–[51]

### 4.2 能力矩阵：不能从 engine 的总表推出 backend 组合

状态 `D` = 文档/源码记录；`E` = 明示 experimental/beta；`U` = 本次未验证；不是实测评级。

| 能力 | vLLM XPU | SGLang XPU pinned tree | llama.cpp SYCL | OpenVINO GenAI / Gaudi |
|---|---|---|---|---|
| 模型身份 | [4] 有按 XPU 列表，live；不能泛化到同名系列所有修订 | Llama/Qwen；MXFP4 tested model 明列 openai/gpt-oss-20b | 模型/architecture 与 GGUF loader、kernel 都要符合；U 对任意混合/多模态组合 | OpenVINO 各 pipeline/plugin 独立；Gaudi integration 自有支持表 |
| 权重/激活量化 | code 注册 AWQ/GPTQ 等 method 不等于每种形状/packing 可运行 | D：Xe2/BMG MXFP4 fused MoE experts，W4A16；attention/router/embedding/head 保持 BF16；EP 未验证 | GGUF 存储不保证每种量化都有同等 SYCL kernel；逐格式核查 | 当前资料不足以列可运行的所有 device×W/A/KV 组合，保留 U |
| KV、paged attention、prefix | [65] Intel GPU 行列 CP/APC；具体 kernel/量化 KV 仍要核对 | D/E：Radix/context 路径；DCP 有明确约束 | Tensor split 要 flash attention；f16 KV 推荐，不能由此声明任意低位 KV 支持 | OpenVINO CPU/GPU PA 支持 block pool；NPU 不自动共享这些能力 [36] |
| Continuous batching | D：serving path；不会自动保障 tail SLO | D：serving path；形状/graph bucket 改变调度约束 | server 功能与 kernel/多 stream 对应配置 U | OpenVINO 的 scheduler 每步重组活跃请求；PA 失败可能回退 SDPA |
| Graph / compile | code 有 supports_xpu_graph 和配置；generic feature table 的 CUDA graph 行 Intel 为否，不能判定全面支持/全面不支持 | E：decode full、prefill breakable 均 opt-in；prefill breakable 不经 torch.compile；decode compile 增加启动工作 | 原生 SYCL 路径不是 torch.compile 的自动继承者 | Gaudi HPU Graphs 是单独机制；本研究不展开 release parity |
| TP / PP / collectives | D：TP；E：PP online serving 仅 single-node mp；torch>=2.8 xccl，旧版本 torch-ccl | communicator 调用分布式；MXFP4 EP U；多节点未本地验证 | Tensor split 优化为两 GPU；其他数量 generic all-reduce；多节点 U | Gaudi HCCL 单独核验；不能运行 nccl-tests 来认证 XCCL/HCCL |
| P/D disaggregation | U：本轮未验证具体 transport/拓扑/量化组合 | E：NIXL，homogeneous XPU P/D 的两例测试模型；UCX_POSIX_USE_PROC_LINK=n 有特定要求；DCP pack fast path CUDA-only，XPU 按 token 传输 | U，不因为 SYCL 多卡就声明支持服务池 KV transport | 需要分别核查 engine 和网络/缓存布局，U |
| 多模态/推理型工作负载 | [65] mm 行不是全部 image/video/audio operator 的保证 | 文档提及 diffusion 不等于任何 VLM/reasoning 配置通过 | 附加 encoder/投影器的显存与 operator 要单列 | NPU/plugin/model pipeline 条件不同；reasoning 额外 token 增加 KV、decode 和调度压力 |

关键反例：OpenVINO 文档指出 PA 初始化失败时 `LLMPipeline` / `VLMPipeline` 可退到 SDPA；显式 `ATTENTION_BACKEND="PA"` 或 scheduler 配置可使不支持时直接失败。模型“能出字”不保证 paged KV 或 continuous batching 的原定机制仍生效。[36]

另一个反例：SGLang DCP 可以延长可服务 context，却增加 decode 工作/通信；只在 TP 与 KV heads 关系符合条件且 context 确实装不下时有意义。它不是“并行度更大必然更快”。[49]

## 5. 性能与经济性：本次不建立排名

已取回 Intel MLPerf 报道 [59]、EmbeddedLLM B60 文章 [60] 和独立作者的 April 2026 双卡实践 [61]。资料的证据角色不同：厂商公布/提交、受硬件支持的开发实验、个人环境部署。后者报告 driver/kernel panic、主机 RAM OOM、recurrent-state 请求间泄漏、fork 与 upstream 行为差异。历史故障有助于制定回归测试，但不能当作 October 2026 上游仍有同一 bug 的证明。

本研究不转抄其 tokens/s、倍率或价格数字作为书稿性能结果。原因是没有得到可同时锁定模型 commit、权重表示、kernel、engine commit、batch、长度分布、排队策略、功率边界、质量阈值与 SLO 的可比记录。没有运行本机/远端 GPU benchmark，也没有对各方 measurement 重新复现。即使 benchmark 文章可访问，也不等于满足可比性要求。

### 可复现对照协议（计划，不是测量结果）

1. 身份清单：PCI device/board ID、GPU revision、显存、主板/CPU/NUMA、实际 PCIe 速率与 lane、GPU pair connectivity、NIC/firmware、OS/kernel、driver/compute runtime、engine commit、wheel hash、container digest、resolved requirements。禁止只写 latest。
2. 两个比较问题分开。机制隔离实验固定同一模型 revision、tokenizer、数值表示、KV dtype、采样与功能；方案选择实验允许各后端最佳可用 kernel/量化，但须先通过同一质量容差和业务约束，完整披露差异。不能混合宣称纯硬件收益。
3. 先功能再负载：单算子与完整输出；长 context；并发请求隔离；取消/重试；多模态 encoder；TP rank 正确性；graph on/off；prefix cache 冷/热；故障恢复。需要的功能不支持则配置判失败，不能偷偷降低上下文或质量后仍计胜出。
4. 负载 grid：输入 128/2048/9216 token，输出 64/300/1024；这是明确的实验设计值，不是假装生产测量。batch/concurrency 1/4/16，随后开放式到达率 sweep 至饱和；缓存冷热分别跑；reasoning 工作负载另设真实停止条件、总生成 token 与质量核验，防止因提早停止获得假加速。
5. 预热、graph capture、编译、模型转换分别计时；warm steady-state、cold start 分开。固定持续时间并至少重复 3 次，保存逐请求时间戳、错误、超时/取消、token 计数、质量结果。p50/p95/p99 的统计方法和误差也记录。
6. 分别报告 prefill 吞吐、decode 吞吐、TTFT、ITL、端到端 latency 与失败率。请求 goodput = 同时满足质量与所有 SLO 的成功请求数 / 墙钟秒；token goodput = 这些合规请求的输出 token 总量 / 同一墙钟秒。其余请求和失败消耗仍计入资源成本。p95 通过不等于每个请求都合规。
7. 用整机 AC 功率积分得到 kWh；device telemetry 可做诊断但不冒充整机功耗。$/合规请求或 $/合规百万输出 token 的分子包含整机、网络、软件支持、运维/移植、闲置、重试和 fallback 成本；区域/时间/税/报价与摊销窗口必须给出。本研究没有报价，不填 TCO 数字。
8. 再做拓扑实验：实际模型所需 dtype/消息大小下测 XCCL 或 HCCL collectives；分 sent/received/双向 aggregate；记录 rank mapping、P2P/host staging 和 p95。只有端到端 SLO 通过，新增卡才有经济意义。

## 6. 何时是可信候选，何时不宜推荐

可信候选：目标模型的完整数值表示能按 rank 装入；所需 attention/量化/多模态 kernel 和 cache path 有明确支持；已选择可维护软件；主机/driver/拓扑匹配；质量、尾延迟和恢复经过真实验证。Arc 的本地/工作站探索和 OpenVINO 的边缘/客户端路线值得作为选择题；Gaudi 是独立数据中心方案；D270 尚限跟踪采样阶段。

不能推荐：只看到设备枚举；只按加总 VRAM 判断模型可装；依赖已归档且有安全警告的软件；必需功能是未经验证的组合；kernel fallback 没有可观测性；只比较 INT8 TOPS 与别家的 BF16 FLOP/s；把 device TDP 当系统费用；把供应方可得性公告当客户生产使用；或把 roadmap projection 当实测收益。

“崛起”的可证伪标准：后续上游支持停止维护、版本升级持续破坏目标工作负载、独立实验在相同质量/SLO 下没有竞争力、采购/支持持续不可得、真实客户规模化部署无法核验，都会削弱命题。相反，持续 CI/稳定发布、可重现模型覆盖、独立质量/SLO/能源对照和有时间窗口的生产部署/续购记录才会增强命题。此次找到 integration 和局部实际使用信号，尚未建立份额趋势。

## 7. 正文机制与日期快照分工

已阅读当前模型选择、内存、计算、通信、并行、serving、性能、经济性、reference architectures、placement/ops 和 Appendix A 的相关全文；第 21 章的后端/生命周期内容也实读而非只看标题。章节定位见英文交付中的 exact anchors。当前 Chapter 9 有其他编辑者的未提交改动；本任务仅针对读到的 source 提出建议，不改动或回滚。

Appendix A 的硬 cutoff 为 2026-08-30，已有单独 September observation。建议保留该事实基线，新增带边框的“Intel backend supplement — observed 2026-10-28 UTC”。正文只写经来源支持的机制，不把 October 的具体版本写成 August 已验证现状。若出版方决定整体更新 cutoff，需对全部产品、软件、模型、价格和 reference architecture 做一致性复核；本任务不宣称已完成。

## 8. 证据、权利和完成边界

`claims.json` 是 claim-to-source 矩阵：含精确 URL、release/event date、逐来源 UTC retrieval time、摘录与行范围、pin、support boundary、provenance、处置与未执行状态。部分页面没有可证 publication date，显式 null；Last-Modified 和 PDF 包装器 Published Time 不自动当正式发布日期。`citation-ledger.json` 的 accessed 是抓取主机的 PDT 日历日，逐次 UTC 时间在 retrievals.jsonl / claims.json，二者并不矛盾。

权利边界：英文增补与图为原创；只引用短技术标识/事实。不使用厂商图、logo 或复刻 slide。来源缓存和 PDF 用于本次私有 provenance，不建议未经许可作为公开附件整批分发。商标使用、第三方资料再分发和最终出版许可仍需常规权利审查；本研究不是法律意见。

未验证：实际 GPU/NPU/Gaudi 运行、wheel/container 安装与 digest、全量 OS/kernel/firmware support matrix、分配上限与 peer access、每种 W/A/KV 组合、质量/长程状态隔离、生产利用率、库存/实际价格/TCO、独立可比能效、全部 source snapshot 的出版再分发许可、整本 PDF 集成/分页与实体印刷样张。原创建议图的局部 render/inspection 与这些事项分开记录。

## References

编号对应 citation-ledger.json；每个重要来源均在本轮实际取回，错误页面已排除。完整 URL、抓取时间、摘录与 hash 见 claims.json。以下参考列表由 finalize.py 从实际引用编号自动生成。

<!-- REFERENCES -->

[1] pytorch-current — https://docs.pytorch.org/docs/stable/notes/get_start_xpu.html
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:38:57.546603+00:00. Provenance: upstream_project_first_party_not_independent_performance_validation.

[2] pytorch-25 — https://pytorch.org/blog/intel-gpu-support-pytorch-2-5
    Publication/release: 2024-10-25. Retrieved UTC: 2026-10-28T06:38:57.548240+00:00. Provenance: upstream_project_first_party_not_independent_performance_validation.

[4] vllm-models — https://docs.vllm.ai/en/stable/models/hardware_supported_models/xpu
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:38:57.549971+00:00. Provenance: upstream_project_first_party_not_independent_performance_validation.

[5] ipex-retirement — https://intel.github.io/intel-extension-for-pytorch/xpu/latest
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:38:57.550787+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[6] crescent-announcement — https://www.intel.com/content/www/us/en/newsroom/news/artificial-intelligence/intel-to-expand-ai-accelerator-portfolio-with-new-gpu.html
    Publication/release: 2025-10-14. Retrieved UTC: 2026-10-28T06:38:57.844033+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[7] b70-datasheet — https://intel.com/content/dam/www/central-libraries/us/en/documents/2026-03/datasheet-b70-gpu.pdf
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:38:58.006118+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[8] b65-datasheet — https://intel.com/content/dam/www/central-libraries/us/en/documents/2026-03/datasheet-b65-gpu.pdf
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:38:58.021078+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[9] max1550 — https://www.intel.com/content/www/us/en/products/sku/232873/intel-data-center-gpu-max-1550/specifications.html
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:39:34.005157+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[10] max-brief — https://www.intel.com/content/dam/www/central-libraries/us/en/documents/2023-01/data-center-gpu-max-series-product-brief.pdf
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:39:34.006441+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[11] gaudi3-whitepaper — https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:39:34.007182+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[13] b70-launch — https://intel.com/content/www/us/en/newsroom/news/client-computing/intel-core-ultra-series-3-with-vpro-powers-next-gen-pcs-on-18a.html
    Publication/release: 2026-03-25. Retrieved UTC: 2026-10-28T06:39:34.010078+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[14] ipex-llm — https://raw.githubusercontent.com/intel/ipex-llm/main/README.md
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:39:35.229808+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[15] sglang-xpu — https://raw.githubusercontent.com/sgl-project/sglang/main/docs/platforms/intel_xpu.md
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:39:35.380511+00:00. Provenance: upstream_project_first_party_not_independent_performance_validation. EXCLUDED FROM SUPPORT: Wrong SGLang path; fetched body is a 404 response.

[21] vllm-release — https://api.github.com/repos/vllm-project/vllm/releases/latest
    Publication/release: 2026-10-18T06:50:48Z. Retrieved UTC: 2026-10-28T06:40:03.034342+00:00. Provenance: upstream_project_first_party_not_independent_performance_validation.

[22] pytorch-release — https://api.github.com/repos/pytorch/pytorch/releases/latest
    Publication/release: 2026-09-30T19:14:48Z. Retrieved UTC: 2026-10-28T06:40:03.035011+00:00. Provenance: upstream_project_first_party_not_independent_performance_validation.

[25] openvino-doc — https://docs.openvino.ai/2026/openvino-workflow-generative/inference-with-genai.html
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:40:03.285638+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[26] openvino-release — https://api.github.com/repos/openvinotoolkit/openvino/releases/latest
    Publication/release: 2026-10-01T13:45:59Z. Retrieved UTC: 2026-10-28T06:40:03.326425+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[27] dseries — https://www.intel.com/content/www/us/en/products/details/discrete-gpus/data-center-gpu/d-series.html
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:42:10.166346+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[28] ocp2026 — https://www.intel.com/content/www/us/en/newsroom/news/artificial-intelligence/intel-accelerates-open-infrastructure-agentic-ai-era.html
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:42:10.169726+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[29] hotchips2026 — https://www.intel.com/content/www/us/en/newsroom/news/client-computing/intel-outlines-architectures-for-agentic-ai-at-hot-chips-2026.html
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:42:10.170534+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[30] b60-datasheet — https://download.intel.com/newsroom/2025/client-computing/Intel-Arc-Pro-B60-Data-Sheet.pdf
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:42:10.171465+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[31] b50-media — https://download.intel.com/newsroom/2025/client-computing/Intel-Arc-Pro-B-Series-Press-Deck.pdf
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:42:10.173624+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[32] b60-launch — https://www.intel.com/content/www/us/en/newsroom/news/artificial-intelligence/computex-intel-unveils-new-gpus-ai-workstations.html
    Publication/release: 2025-05-19. Retrieved UTC: 2026-10-28T06:42:11.901480+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[33] b580-launch — https://www.intel.com/content/www/us/en/newsroom/news/intel-launches-arc-b-series-graphics-cards.html
    Publication/release: 2024-12-03. Retrieved UTC: 2026-10-28T06:42:12.099185+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[35] panther388 — https://www.intel.com/content/www/us/en/products/sku/245526/intel-core-ultra-x9-processor-388h-18m-cache-up-to-5-10-ghz/specifications.html
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:42:16.207899+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[36] ov-continuous — https://openvinotoolkit.github.io/openvino.genai/docs/concepts/optimization-techniques/continuous-batching
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:42:18.159634+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[37] ov-memory — https://docs.openvino.ai/nightly/openvino-workflow/running-inference/optimize-inference/managing-igpu-memory-usage.html
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:42:18.523796+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[41] llama-head — https://api.github.com/repos/ggml-org/llama.cpp/commits/master
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:43:06.656462+00:00. Provenance: upstream_project_first_party_not_independent_performance_validation.

[42] sglang-release — https://api.github.com/repos/sgl-project/sglang/releases/latest
    Publication/release: 2026-10-19T02:55:19Z. Retrieved UTC: 2026-10-28T06:43:06.657637+00:00. Provenance: upstream_project_first_party_not_independent_performance_validation.

[47] gaudi-ccl — https://docs.habana.ai/en/latest/API_Reference_Guides/HCCL_APIs/index.html
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:43:07.171812+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[48] flex170 — https://www.intel.com/content/www/us/en/products/sku/230020/intel-data-center-gpu-flex-170/specifications.html
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:43:07.520115+00:00. Provenance: vendor_or_vendor_maintained_project_first_party. EXCLUDED FROM SUPPORT: SKU 230020 resolves to Flex 140, not the Flex 170 identity in the URL slug.

[49] sglang-pinned-doc — https://raw.githubusercontent.com/sgl-project/sglang/a1966e1b5d8b750b494d7e53cca1d2464f960038/docs/docs/hardware-platforms/xpu.mdx
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:46:42.644037+00:00. Provenance: upstream_project_first_party_not_independent_performance_validation.

[50] sglang-pinned-ccl — https://raw.githubusercontent.com/sgl-project/sglang/a1966e1b5d8b750b494d7e53cca1d2464f960038/python/sglang/srt/distributed/device_communicators/xpu_communicator.py
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:46:42.645267+00:00. Provenance: upstream_project_first_party_not_independent_performance_validation.

[51] sglang-pinned-docker — https://raw.githubusercontent.com/sgl-project/sglang/a1966e1b5d8b750b494d7e53cca1d2464f960038/docker/xpu.Dockerfile
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:46:42.646413+00:00. Provenance: upstream_project_first_party_not_independent_performance_validation.

[52] vllm-pinned-xpu — https://raw.githubusercontent.com/vllm-project/vllm/5df63a7203cdb9328d824a27b682e77c7b9928be/vllm/platforms/xpu.py
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:46:42.646991+00:00. Provenance: upstream_project_first_party_not_independent_performance_validation.

[53] vllm-pinned-req — https://raw.githubusercontent.com/vllm-project/vllm/5df63a7203cdb9328d824a27b682e77c7b9928be/requirements/xpu.txt
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:46:42.654940+00:00. Provenance: upstream_project_first_party_not_independent_performance_validation.

[54] llama-pinned-doc — https://raw.githubusercontent.com/ggml-org/llama.cpp/8ca4060b7e30e76baaa5670ee1ec1b760b7f8552/docs/backend/SYCL.md
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:46:42.818624+00:00. Provenance: upstream_project_first_party_not_independent_performance_validation.

[55] gaudi-port — https://docs.habana.ai/en/latest/PyTorch/PyTorch_Model_Porting/Porting_PyTorch_Models_to_Gaudi.html
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:46:42.826573+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[56] ibm-gaudi — https://newsroom.ibm.com/blog-intel-and-ibm-announce-the-availability-of-intel-gaudi-3-ai-accelerators-on-ibm-cloud
    Publication/release: 2025-03-31. Retrieved UTC: 2026-10-28T06:46:42.843413+00:00. Provenance: commercial_provider_first_party_announcement.

[58] flex170-correct — https://www.intel.com/content/www/us/en/products/sku/230019/intel-data-center-gpu-flex-170/specifications.html
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:47:01.398862+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[59] intel-mlperf — https://www.intel.com/content/www/us/en/newsroom/news/artificial-intelligence/intel-delivers-ai-performance-mlperf-inference-v6-0.html
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:47:01.400538+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[60] embeddedllm-b60 — https://embeddedllm.com/blog/benchmarking-llm-inference-intel-arc-pro-b60
    Publication/release: 2026-02-14. Retrieved UTC: 2026-10-28T06:47:01.401203+00:00. Provenance: third_party_experiment_hardware_provided_by_Sparkle_with_Intel_technical_support.

[61] linville-arc — https://bentech.substack.com/p/running-local-llms-on-intel-arc-pro
    Publication/release: 2026-04-13. Retrieved UTC: 2026-10-28T06:47:01.402066+00:00. Provenance: independent_author_self_report_not_independently_reproduced.

[65] vllm-pinned-features — https://raw.githubusercontent.com/vllm-project/vllm/5df63a7203cdb9328d824a27b682e77c7b9928be/docs/features/README.md
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:47:01.958003+00:00. Provenance: upstream_project_first_party_not_independent_performance_validation.

[66] torch-pinned-md — https://raw.githubusercontent.com/pytorch/pytorch/5c4886908584029761b579af026dcfb627c84070/docs/source/notes/get_start_xpu.md
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:47:53.081489+00:00. Provenance: upstream_project_first_party_not_independent_performance_validation.

[67] vllm-pinned-xpu-guide — https://raw.githubusercontent.com/vllm-project/vllm/5df63a7203cdb9328d824a27b682e77c7b9928be/docs/getting_started/installation/gpu.xpu.inc.md
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:47:53.082687+00:00. Provenance: upstream_project_first_party_not_independent_performance_validation.

[68] b580-sku — https://www.intel.com/content/www/us/en/products/sku/241598/intel-arc-b580-graphics/specifications.html
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:47:53.083481+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[69] b570-sku — https://www.intel.com/content/www/us/en/products/sku/241676/intel-arc-b570-graphics/specifications.html
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:47:53.084131+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[70] omix-matrix — https://dgpu-docs.intel.com/driver/overview/support-matrix/omix-support-matrix.html
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T06:47:53.239020+00:00. Provenance: vendor_or_vendor_maintained_project_first_party. EXCLUDED FROM SUPPORT: Fetched response is Page Not Found; not a valid support matrix.

[71] openvino-genai-release — https://api.github.com/repos/openvinotoolkit/openvino.genai/releases/latest
    Publication/release: 2026-10-01T13:52:44Z. Retrieved UTC: 2026-10-28T06:47:53.274463+00:00. Provenance: vendor_or_vendor_maintained_project_first_party.

[72] sglang-commit-at-snapshot — https://api.github.com/repos/sgl-project/sglang/commits?until=2026-10-28T06:40:03Z&per_page=5
    Publication/release: not established in fetched source metadata; see claim event date. Retrieved UTC: 2026-10-28T07:18:24.320871+00:00. Provenance: upstream_project_first_party_not_independent_performance_validation.
