# 新模型趋势独立研究：把“新型号”转化为可迁移的架构推理

研究快照：2026-10-28 UTC；本机实际日期仍为 2026-10-27 PDT。本次工具观测为 2026-10-27T23:40:46-07:00。日期不是从目录名反推。

范围：公开研究、证据登记、英文候选增补。没有修改书稿、网关或其他代理文件，没有委派、发布、提交或推送。没有运行模型权重或复现性能实验。本报告不构成出版就绪认证，也没有审查冻结 PDF 的版面。已读 MASTER_INSTRUCTIONS.md，并以源稿作章节映射；不能把源稿定位当作已核对的 PDF 页码。

## 1. 结论与范围冻结

最有价值的增补不是再列一个模型排行榜，而是补上三个因果机制：

1. 参数分配、历史状态表示、重复计算深度是独立的维度。Qwen/Qwen3.8-27B 是 dense FFN，但不是全层标准 softmax attention。Huginn/Ouro 可以共享权重而重复执行；共享权重不代表共享 KV，也不代表较低的每 token FLOPs。
2. 内存账本必须按状态类型、阶段和存储层级拆分。DeepSeek-V4.1-Flash 的 prefill/decode 激活参数不同；报告中的 global HBM KV、SWA state、persistent SSD/host cache 也不是同一个分母。一个 bytes/token 不能替代整个请求内存预算。
3. 训练能力提升、推理算法和产品服务政策必须分开。Ornith 的 self-improvement 主要是训练任务、scaffold 和 rollout 的联合优化；不是模型内部的 shared-depth recursion。“Flash”也不是统一架构或“小模型”的证明。

现有 Ch3 已有 Qwen3.8-27B 与 Flash-Next；Appendix A 已有 DeepSeek/Qwen/GLM 的 hybrid-attention 比较及 Ornith 观察。不能把这些全部再当成“书里缺失的新趋势”。真正缺口是 shared-depth recurrence 的状态/调度后果、阶段化计算，以及跨来源版本和 benchmark scope 的核对。

建议冻结：正文仅补可迁移机制和适用条件；另加明确标为 2026-10-28 的独立技术更新。用 Qwen27 作 dense/hybrid 的小例子，用 DeepSeek4.1 作阶段/状态拆分的例子，用 Huginn/Ouro 作实验性 shared-depth 例子。Ornith 用作训练与推理的边界案例。MiMo 和 Gemini 仅占机制表中的反例，不增加独立产品章节。

## 2. 身份、发布日期与来源版本登记

以下“确认”是确认公开一手记录与其内容，不是确认厂商性能已经独立复现。来源 key 对应 source-index.json，包含本次 GET 的时间、最终地址、ETag、内容哈希和本地快照。逐条 consequential claim 在 claims.json。

| 原始发现名称／精确 ID | 发布者与日期证据 | 确认状态与边界 |
|---|---|---|
| `qwen3.8 27b` → `Qwen/Qwen3.8-27B` | Alibaba Qwen；官方 GitHub News 为 2026-08-14。HF createdAt 为 08-05、lastModified 为 08-14，不能把仓库创建日当公开发布日。 | 精确 ID、模型卡、config、Apache-2.0 LICENSE 均已取回。27B 独立技术报告本次未找到；架构以型号卡/config 加实现交叉确认，不能把 Flash-Next 报告移植成27B报告。 |
| `ornith 1.5` → `ornith-ai/Ornith-1.5-397B`、`ornith-ai/Ornith-1.5-35B-A3B`、`ornith-ai/Ornith-1.5-9B` | Ornith Team / `ornith-ai`；官方报告标 Aug. 2026。397B/35B HF 仓库 08-18 创建、08-23 修改。 | 这些是具体变体，不是单一“Ornith1.5”架构。书中所写精确 08-19 发布日本次没有独立一手日期确认，保留 UNVERIFIED。 |
| `ornith-ai/Ornith-1.5-122B` | 同一公开发布体系；HF createdAt 2026-10-16、lastModified 10-21。 | 是十月可取得的变体；精确公开首发日未从公告确认。不要把它倒填入八月家族比较。 |
| `deepseek-ai/DeepSeek-V4-Flash` | DeepSeek；报告 `2606.19348`，卡/config已取回。 | 报告/卡一致支持架构数字，但日期元数据存在异常：abs 显示 Submitted 26 Apr 2026，与 `2606` 标识前缀不一致。保留原始记录，不“修正”ID或日期。发布日期年表暂不依赖该字段。 |
| `deepseek-ai/DeepSeek-V4.1-Flash` 与 `deepseek-ai/DeepSeek-V4.1-Flash-1017` | DeepSeek；前者 HF 09-10 创建、10-16 修改；后者官方卡称 minor update。 | V4.1 的官方 PDF、config、inference/model.py 均已取得。`1017` 是 ID 的组成部分，不能仅凭它推导完整发布时间。两个本次 config 哈希相同，权重是否相同不由此决定。 |
| `zai-org/GLM-5.3-Flash` | Z.ai；HF 08-25 创建、10-15 修改。 | 卡/config/code验证架构；卡链接的 arXiv `2602.15763` 是 GLM-5 母报告，v1 02-17、v2 02-24，不是 5.3-Flash 专属报告。精确首发日仍须公告补证。 |
| `XiaomiMiMo/MiMo-V2-Flash` | Xiaomi MiMo；`2601.02780` v1 2026-01-06，v2 01-08。 | 报告、卡、config、官方 GitHub 均取回。这是机制对照，不声称是十月最新型号。 |
| `XiaomiMiMo/MiMo-V2.6-Flash-RL` | Xiaomi MiMo；HF 09-21 创建、10-09 修改。 | 官方 PDF、卡、config、模型代码取回。RL 是精确 ID 的部分，不能丢掉。首发日不以 createdAt 代替。 |
| `gemini-3.8-flash` | Google DeepMind；卡 Published 2 September 2026；型号文档 10-22 更新。 | 精确 API ID、公开卡及 API limits 已验证。不是开权重模型。未取得其精确参数量或 KV 内部布局。通用 latest-model 页面现在介绍 Gemini 4 Argon，不能用那个页面给 3.8 补规格。 |
| `tomg-group-umd/huginn-0125` | 论文作者团队／公开仓库；`2502.05171` v1 2025-02-07，v2 02-17。 | 已发布研究 checkpoint，不是十月新发布的生产服务。论文、卡、config、官方研究仓库与模型实现取回。 |
| `ByteDance/Ouro-2.6B` | Ouro 论文团队／ByteDance 发布仓库；`2510.25741` v1 2025-10-29，当前 v6 2026-10-11。 | “近期”指修订，不是首次发布。HTML全文404，已用 v6 PDF替代。卡/config/code存在未解决差异，不宜直接抄参数→FLOPs算例。 |

### 尚未解决的身份信息

“DeepReinforce”是当前书稿的 Ornith 归属写法，但本次取回的报告署 Ornith Team、HF 组织名为 Ornith。`deepreinforce-ai/Ornith-1` raw README 可取回并与 Ornith 卡互链，而 GitHub organization API 返回404。这个组合不能独立确认公司/团队法律实体。建议正文先写 Ornith Team (`ornith-ai`)，DeepReinforce 的企业归属标 UNVERIFIED；不是认定二者无关。

原始发现词 `qwen3.8 27b` 和 `ornith 1.5` 都找到公开一手型号，未把本地 endpoint label 当成证据。对于“recursive models”，它是待消歧的机制类别，不是可验证的型号名。

## 3. 逐类机制与交叉核对

### 3.1 Qwen3.8-27B：dense 不等于“标准全注意力”

卡给出 dense 语言 FFN、原生 image/video understanding，语言部分64层。config `layer_types` 为48个 `linear_attention`、16个 `full_attention`，与卡中的16组“3 Gated DeltaNet + 1 Gated Attention”一致。`model_type=qwen3_5_text` 是实现复用，不是证据说明型号名错了。公开 Transformers 实现具备 GDN 的 recurrent-state 更新路径。[Q01–Q04]

total/active：卡把语言模型称27B dense；HF safetensors统计约27.78B，但该库存数字不能无说明地变成“所有语言/视觉/MTP参数均每token激活27.78B”。dense主要描述 FFN 参数分配；embedding lookup、vision encoder和draft module的参与范围不同。

context：262,144 是卡所称 native window，也是 config 的 `max_position_embeddings`。1,000,000 是可扩展范围，卡另给 YaRN 与静态缩放的短文本质量警告。native不是本研究证明的训练序列长度，更不是已实测的并发服务容量。托管版“1M默认/coming soon”也不能当本地权重默认值。[Q03]

precision/engine：Apache-2.0；config bfloat16；卡列 Transformers、vLLM、SGLang、TokenSpeed 兼容。没有运行这些 engine，也不把“兼容”解释为所有精度、硬件、图模式均支持。

可加入的真实配置推导：假设完整注意力KV以BF16存储，单请求、未分片，其语言full-attention部分为 `2 × 16 × 4 × 256 × 2 = 65,536 bytes/token`；在262,144 tokens为16 GiB。只计算这一项，不含48层GDN状态、卷积状态、视觉状态、runtime和allocator。计算已用Python执行并写入 calculations.json。这比只写“hybrid省KV”更能展示如何从config走到预算。[Q05]

benchmark条件：SWE-bench Pro 使用修订任务集、Claude Code、temperature 1.0、top_p 0.95、256K上下文；QwenSWEBench为avg@3、8h、max_tokens32768。不能与其他原始任务版本的pass@1直接排名。[Q06]

### 3.2 Ornith1.5：重点是训练闭环，不是新发明的递归推理核

官方报告围绕 task generation、scaffold construction、solution rollout联合优化。卡明确写在Qwen3.5/Gemma4基础上continued pretraining/mid-training/post-training。它证明“相近骨干可因训练与harness而能力不同”，不证明推理期间不断自我更新权重，也不等同shared-depth recursion。[O01]

变体不能混用：397B config为60层、45 linear/15 full、512 routed experts/top10；35B-A3B为40层、30/10、256/top8；9B为dense、32层、24/8；122B为48层、36/12、256/top8。397B/122B的active-total没有从报告得到清晰口径，不补猜A17B/A10B；35B-A3B保留官方名称里的A3B，而不把它当本研究审计过的FLOP值。[O02–O05]

三项需要保留的细节：

发布条件也应保持型号范围：397B卡声明MIT，给BF16多GPU配方，列vLLM≥0.19.1/SGLang≥0.5.9；config ceiling为262,144，卡另提供YaRN扩展。它们是发布方配方，不是本研究测过的precision×engine兼容矩阵、单rank fit或1M质量证明。[O09]

- 397B卡称397B，但HF BF16 safetensors库存为403,397,928,944。vision/MTP/其他tensor可能造成口径差，但本研究没有完整权重形状清点，差异不强行归因。[O08]
- card task tag为text-generation，config却含vision_config。可以确认发布了视觉组件，不能用这个组合单独证明公开服务能正确接收image_url或“原生多模态”训练结论。当前书稿旧LAB探针本次没有重跑。[O06]
- 部分config为use_cache=false；卡却给vLLM/SGLang cached-serving配方。它是框架设置，不等于“这个家族不支持缓存”。[O03]

397B的86.1 Terminal-Bench2.1是厂商结果：Harbor/Terminus-2、JSON parser、128K context、temperature1/top_p1、4h、32 CPU cores/48GB RAM、5次平均。不能把它解读为模型本体能力、端点速度或所有harness下的成功率。[O07]

### 3.3 Flash：同一标签，完全不同的资源机制

| 代表 | 公开机制 | 可以推导的架构问题 | 不能从名字推出的结论 |
|---|---|---|---|
| DeepSeek-V4-Flash | 284B/13B，CSA+HCA，FP4专家等 | 历史压缩与稀疏读取、state pool与paged compressed cache、专家分布 | Flash不是13B resident模型；1M FLOPs比不是服务速度倍数 |
| DeepSeek-V4.1-Flash | 552B backbone，另196B Engram；CED；CSA2跨层KV/索引复用、FP4 main KV | prefill/decode不同计算路径；global HBM cache与persistent cache分账 | 890B/token不是整个请求内存；8B/16B不是速度比 |
| GLM-5.3-Flash | 320B/18B；config45层=34linear+11sparse；原生图像/视频 | 模态encoder、混合状态管理、encode/prefill/decode阶段的队列 | API价格低不证明FLOPs低同倍数；GLM-5报告不自动覆盖5.3 |
| MiMo-V2-Flash | 309B/15B；39SWA+9global；128-token SWA；MTP | local/global的不同状态增长、draft验收与batch竞争 | 5:1简写不能直接填48层内存表；MTP不是shared-depth reasoning |
| MiMo-V2.6-Flash-RL | 原生text/image/video/audio；main block仍39/9；report描述5层draft | 视觉/音频编码队列、blockwise speculation、训练改进与骨干继承 | RL/self-improvement不自动意味着新attention architecture |
| gemini-3.8-flash | 公开API多模态输入/文本输出，effort控制；内部精确参数/KV未建立 | 服务合同、计费、限额、版本控制与本地可观测性的区别 | 不从名称、价格或快慢反推dense/MoE、resident memory |

DeepSeek V4的10% FLOPs/7%KV是Flash在1M条件下对V3.2的报告估算，FLOPs按equivalent FP8口径；27%/10%对应Pro，不能挪给Flash。[D01]

V4.1是最有迁移价值的近期新例：报告§2.1–2.4把40层拆为20层causal encoder+20层decoder，称prefill8B、decode16B active；552B只指backbone，196B Engram另计。global HBM KV 890 bytes/token来自跨层复用与FP4；persistent SSD/host KV约为V4-Flash的1/8是另一种存储对象/策略。bounded SWA、weights、runtime都没有包含在890里。[D03–D04]

代码交叉核对也防止夸大：V4.1 inference README明确是readable reference implementation，不是生产engine；虽有DSpark forward path，generation仍是plain autoregressive。`1017`更新卡与原版config哈希相同，可以说配置相同，不能说所有权重相同或“性能增益已被证明只来自post-training”。[D05–D06]

GLM的5.3与5.3-Flash须分开：官方GitHub写5.3复用5.2 base、变化来自post-training；Flash则新训base并改架构。[G04] 目前稿里的“3×attention/4.4×KV”不能仅以February GLM-5母报告为依据。本次5.3博客直接GET未得到这些可读证据，reader替代403；不把缺证的比值升级为已验证。config确认1,048,576 ceiling，不能据此独立确认“native训练长度”。HLE with tools脚注明确用300,000 context和context management，不是1M服务质量测试。[G01–G03]

MiMo的完整报告和config一致给39SWA/9global；卡5:1简写遗漏首层global/dense例外。[M01] V2.6报告Table1总参数写310B，卡写309B；先登记rounding/scope差异，不编成增长事实。更重要的是卡/报告描述5层draft，而发布config为`num_nextn_predict_layers=3`；报告后文讨论替换SFT继承的MTP-3，尚不能确认发出的权重/engine映射，保留UNRESOLVED。[M03–M04]

Gemini卡给3.8发布日期2026-09-02；API页给input1,048,576/output65,536。3.8 architecture指向3.7，3.7再指向3.6；本次资料没有建立3.8精确total/active和cache布局。保留不披露/未验证，不从API pricing反推硬件。价格不进入候选正文的常量表，因为它同时受促销、batch/flex/priority、cache和reasoning计费影响。[F01–F02]

### 3.4 Recursive / recurrent / looped：先分清在哪个轴上重复

| 术语 | 重复对象 | 权重/状态后果 | 代表与状态 |
|---|---|---|---|
| token-history recurrence | 随输入token更新压缩state | 固定宽度state；hybrid中其余attention仍可能随历史增长 | Qwen27 GDN；公开权重/实现 |
| shared-depth / looped-depth | 当前表示通过同一core多次 | 权重可复用；算术重复；每pass KV可能不同 | Huginn、Ouro；研究checkpoint，不声称生产成熟 |
| adaptive compute / early exit | 根据输入/状态决定执行深度 | 需要停止规则、质量校准与真实跳过的runtime路径 | Huginn proof-of-concept；Ouro learned exit |
| explicit CoT / test-time search | 输出更多token／扩展候选轨迹 | 增加生成、历史或分支预算；不自动共享层权重 | 类别边界，本文不另列产品 |
| agent / recursive program loop | 外部控制器重复调用model/tools/subtasks | token重放、prefix重用、工具时延、分支和失败预算 | Ornith训练scaffold研究与Ch19的系统层讨论；不是depth证据 |
| speculative decoding / MTP | draft候选后由target验证 | 改变每target调用接受token数；额外draft权重/state | MiMo、Qwen MTP、DSpark；不是多想几轮的同义词 |
| MoE | token选部分expert | 参数分配与通信发生变化；与上述轴可组合 | Flash等；不是递归的同义词 |

Huginn论文和卡明确是prelude→recurrent core→coda。卡要求HuginnDynamicCache，避免不同core pass互相覆盖；提供KV sharing策略以及KL、entropy/latent difference、argmax stability停止准则。adaptive compute写明模型未为此训练，是zero-shot proof-of-concept。对生产风险的推导必须标[HYPOTHESIS]，不是“自适应服务已经验证”。[R01–R02]

Ouro v6报告提供learned exit gate和CDF threshold。§5.4.2明确naive四步有四套cache；prefill共享报告会造成GSM8K超10-point下降。Table14的last-step decode复用使GSM8K从78.92到78.85，但MATH-500从82.40到80.40；first-step only更差。不能把“4×cache reduction”扩写成“全请求memory无损降低4倍”。[R03–R04]

更强的runtime反例：本次取得的OuroModel.forward先执行完整`for current_ut`并收集hidden_states/gates，再在CausalLM.forward按exit_threshold选择hidden。这条参考路径没有因选择较早exit而跳过已执行的core；模型卡也说vLLM不支持adaptive exit。这个结论仅限静态阅读的具体版本，不代表所有研究代码/后续engine。发布config写48层，卡写24层，未解决前不由层数推出完整FLOPs或显存。[R05–R06]

## 4. 对全书因果模型的具体影响

### 4.1 内存：把一个KV常数改成按状态类型的账本

分析表达式，而非实测数字：

`M_device = W_resident_on_this_rank + M_history(T, representation, sharing) + S_bounded + M_multimodal + M_draft + M_runtime + M_allocator`

- full/GQA层：历史KV按T增长，常数用KV heads而不是query heads。
- local/SWA层：滚动状态按window封顶；prefix持久化/重放策略另列，不默认“窗口外完全免费”。
- recurrent/state层：decode时有固定宽度state；prefill chunk buffer和训练activation不是同一项。
- compressed历史：历史条目按compression rate增长，仍有tail/indexer/scales。稀疏只读top-k不代表只存top-k。
- cross-layer reuse：按独立存储对象计数，不按每consumer layer重复计数。
- recurrent-depth：共享权重不保证共享历史；必要时加入iteration维度。

各rank能否放下取决于placement、replication、engine和通信；节点aggregate memory之和不是某rank可用内存。即使减少历史项，total experts/Engram/vision模块也不会随active-per-token等比例消失。[DERIVED from Q05,D03–D05,R02–R05]

### 4.2 计算：参数量之外，还要列phase与depth

`C_token ≈ C_prelude + r_token × C_core + C_coda + C_history + C_draft/verification + C_routing`

这是机制分解，不是可代替profiling的精确公式。2P近似只覆盖指定路径的parameterized matmuls，不能覆盖所有history attention、recurrence、indexing和routing。V4.1说明P本身可随prefill/decode变化；Huginn/Ouro说明执行次数r也可能变化。故不能始终用“2×一个固定active参数量”推完整服务成本。

### 4.3 调度：depth分布和state语义成为服务输入

[HYPOTHESIS / UNMEASURED] 真正的动态early exit可能缩短部分token，却使batch内执行深度不同。同步batch可能仍受最慢sequence支配；mask/compaction、graph capture、rebatching、cache checkpoint/rollback要与迭代语义协调。待测量项包括：每token实际core执行次数、stage时间、allocator bytes、checkpoint/restore正确性、r的分布以及p95/p99 TTFT/ITL与SLO内goodput。选择早期logits但没有跳过core不是执行收益。

停止条件应同时写：硬最大depth、置信/稳定阈值、超时/任务完成或质量校准。更低threshold不自动保证答案正确；对entropy/CDF做校准与对外部任务结果校验是两件事。

### 4.4 原生多模态和action的边界

encoder把图片/视频/音频转成表示之后，prefill/decode的状态函数仍然适用；但预处理、patch/frame/audio长度、encoder compute/workspace和模态队列必须显式化。函数调用、GUI动作文本、agentic benchmark分数不单独证明存在新action-specific decoder。Ornith训练scaffold及MiMo mixed RL可改变能力而不要求每项都来自新的attention机制。

## 5. 章节整合图：依据当前源稿，不依据想象中的目录

| 当前文件定位 | 当前已有内容 | 最小整合建议及依赖 |
|---|---|---|
| `design/manuscript/chapter-03/chapter-03.md:116–130`，§6 baseline shift | 已有dense反例Qwen27、Flash-Next和total/active区分 | 不重写成产品介绍；增加独立三轴：FFN allocation、history state、execution depth。§1:11“dense activates all parameters”限定到dense FFN/matmul路径，排除embedding、vision、draft的粗暴等同。 |
| `chapter-03/chapter-03.md:59–78`，MoE与KV | 已有同attention几何下MoE不减KV及hybrid例外 | 保留受控比较；“Only changing ... can stop cache from growing”改为改变growth law/constant/bounded component。GQA、压缩、offload不一概等于停止增长。不是要求重开已解决的MoE控制变量问题。 |
| `chapter-05/chapter-05.md:115`，§4 Measurement；§6:137 | model-selection gates | 加model/version、context native/extended/validated、precision/engine及effort/harness四栏证据签名；继续用原有memory/goodput/quality gates。 |
| `chapter-07/chapter-07.md:24`，§3；§4:90 | full-MHA canonical预算与其他attention讨论 | 加Qwen27 raw GQA component的配置推导框；通向按state类型求和。full-MHA只能在固定几何/精度条件下作比较界，不能当任意recursive模型的全局上界。 |
| `chapter-08/chapter-08.md:33`，FLOPs/token；§4:145 | 2P与sequence-dependent attention区分 | 追加phase-specific P与r_core；不改70B canonical常量，不用V4.1的8B替换它。 |
| `chapter-11/chapter-11.md:70`，prefix reuse；§4:88；capability表:136 | batching、paged/prefix、P/D disaggregation | 增加bounded recurrent/SWA state与shared-depth cache的保存/复用限制；能力表由“supports model”细化到hybrid state、speculation、actual early exit。Ouro静态路径作警示，不声称engine性能。 |
| `chapter-12/chapter-12.md:29`，§4；Table12-1:89 | 三gate比较 | 仅加candidate evidence signature；aggregate fit不等per-rank fit，native context不等目标并发capacity。无需另建模型排名矩阵。 |
| `chapter-19/chapter-19.md:133`，Multi-step reasoning cost；§6:165 | 外部agent turns与token amplification | 插入depth loop不等agent loop；Ornith作训练变化案例。已有turn数×tokens预算之外另列internal compute，不把latent rounds算成API turns。 |
| `chapter-27/chapter-27.md:3–14`、§3:67、§4:73、§5:81、§6:95、Sources:151 | 08-30四family envelope；09-27 Ornith LAB sidebar | 保留原scope。新增独立10-28 update及独立sources，不偷偷变成六family比较。修订下述来源/措辞问题，再评估图表传播。 |

## 6. 需要限定或替换的旧说法，而不是无界扩写

这些是源稿证据候选，不是完成PDF审核后的正式出版缺陷结案。

- Appendix A §3（源行71）把host-RAM embedding offload称纯作者推断。新取得的08-26官方技术报告abstract/§2.3明确写tables held off accelerator、host-memory prefetching。可改为“厂商报告的机制；具体本地placement/速度仍未复现”。这不是增加更强的部署性能承诺。[T01]
- Appendix A §4（源行75）把GLM5.3-Flash细项绑在GLM5母报告。保留卡/config支持的320B/18B、sparse+linear、多模态；3×/4.4×、cache precision组合、131K output及EPD要补型号专属来源/条件，否则暂不作为已证数字写入更新。[G01–G03]
- Appendix A §6 Ornith旧LAB sidebar（源行79）不能作为本次已重跑证据；“DeepReinforce”、精确08-19发布日期、本地endpoint到公开weights映射分别保留证据边界。无需删除真实旧观察，但不能传播成独立型号规格或benchmark。[O01,O06]
- Appendix A的“only constants differ”（源行93及Ch3相近表述）对phase-dependent CED和shared-depth cache太窄。保持“同一决策流程”，改成“常数、state growth law、执行阶段和调度单位可能同时变化”。
- Qwen3.8-Flash-Next的125B/6B active分母只含backbone，另51B n-gram与4B MTP要保持独立。报告attention-module的7.6×/4.9×不能转写全模型或fleet吞吐倍数。[T01–T02]
- 上述QSA速度数字的条件为1M context、prefill最后16K chunk/batch1、decode batch4/next_n4（含3步MTP），baseline是FlashInfer paged GQA；本次可读实验段未找到具体GPU型号。硬件条件不完整，不移植为部署预测。MiMo的“tripled”也未补成自造hardware/batch条件。
- MiMo headline5:1和Ouro card24-layer不能直接抄进工程算例；已查到更具体冲突时，应记录冲突，而不是挑方便的来源。

## 7. 日期边界与传播方案

任务提醒八月cutoff；但实际当前Appendix A写08-30 hard boundary，并已有09-27 sidebar。不能自行声称全书统一08-19，也不能自动把整个edition改成10-28。

推荐方案：

1. 原正文canonical与08-30四family comparison不改含义。另设“Dated update — evidence retrieved 28 October 2026”。说明包含八月已发布模型的重验、九月新型号及十月论文修订，retrieval date不等release date。
2. 更新只展示机制差异，单独引用新source版本。Ouro v6不能回填为八月已知；MiMo2.6、DeepSeek4.1、Ornith122不能进入原08-30 figures。
3. 正文可放短cross-reference。新figure/table有独立编号和scope，不沿用原four-family denominator。
4. 如果父代理决定受控更新整个cutoff，必须同步：front matter/edition/date policy、Appendix header、source manifest、figures/captions、Ch3示例、Ch7/8推导边界、Ch11engine能力表、Ch5/12选型依据、Ch19benchmark scopes、EPUB/PDF引用与重建。需要重新审PDF；本研究不能替代这个传播与验证工作。

最小coherent additions：一个dated subsection、一个机制表、两张各自解释独立机制的图，以及混合状态预算、重复执行预算、调度与经济分母的实质正文。英文素材见 proposed-insertions.md，全部未应用；不把共享深度机制缩成只有一句限定。

已制作 MT-1（token-history 轴上的固定形状状态与增长的 full-attention KV）和 MT-2（一个共享权重对象、独立 iteration cache、真实停止与事后选择）。两图均为原创机制示意，不是 agent 外部调用图或 speculative draft 图，也没有未经测量的 speedup 曲线。`figure-plan.md` 记录必要性与位置；`figures/manifest.json` 提供 SVG、生成器、400-PPI PNG、向量 PDF、caption、alt text、claim ID 和复现命令。目标宽度由当前 Letter 版式推得 6.1 英寸；`figures/QA.md` 记录完整图、局部、灰阶与第二轮自批判检查。最终书内分页、caption binding 与纸质印刷仍需父代理验证。

## 8. 证据状态、缺口与复现边界

本次没有独立的GPU benchmark。任何vendor/author结果均保留其数据集、harness、context、precision与module范围。事实标签指“来源确实这样写”，不等同该硬件环境已证明。

发布前仍需解决：Ornith企业归属和精确首发日期；各新增HF repo的公开launch日；Ornith nominal-vs-tensor inventory及视觉服务路径；GLM5.3专属ratio的完整来源；MiMo2.6 shipped draft mapping；Ouro layer-count/训练token口径与真实skip-compute engine；DeepSeek V4 arXiv日期异常；Gemini未公开的精确架构不补猜。这里的UNVERIFIED不代表模型不存在。

链接验证使用实际GET而非只看搜索摘要；所有作为证据的source均有本地内容与哈希。失败也保存：GLM reader403、DeepSeek-V4猜测GitHub404、Ouro HTML404（PDF成功替代）、DeepReinforce org API404。未把失败URL写成已读报告。SearXNG不可达时内置搜索明确走keyless rescue，搜索仅作发现；所有accepted claim均来自直接取回的一手来源。

验证与文件清单：claims.json含机器可审计claim；source-index.json含所有取回/失败记录；fetch-log.json保留每次尝试；calculations.json含已执行推导；manuscript-read-hashes.json记录映射时源稿版本；validation.json由最后验证脚本生成。完整一手URL目录见 primary-sources.md。
