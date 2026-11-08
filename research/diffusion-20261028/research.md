# Diffusion mechanisms and diffusion language models：从 token 到 fleet 的边界扩展

状态：研究交付；未修改书稿。本文为中文研究包，不是出版就绪认证，也不是硬件性能复现。

时间：本次工具时钟为 2026-10-27 23:44 PDT，UTC 已为 2026-10-28。目录日期采用任务日期。所有外部事实均来自本次获取并保留的原始论文、官方页面、模型卡/config 或上游实现。来源检索不是穷尽调查；下文的“当前”仅指本次来源快照，不声称找到了所有最新模型。

## 1. 最值得写进本书的结论

1. token 仍是输入、输出与计费的接口单位，但不再足以单独描述内部计算。扩散语言模型需要同时记录最终输出 token、被重复计算的位置、顺序模型调用、采样/验证工作和可提交的输出。token→资源→服务→fleet 的推理链仍然有效，变化的是 token→资源这一段的执行模型。[D07–D14, D33]
2. 应保留全书自回归主线。实际源码已经在第 1 章限定“text-tokenized autoregressive models”，第 2 章也写明“In an autoregressive model”。没有证据支持把整本书诊断为“错误地声称所有 LLM 都逐 token 生成”。需要局部补作用域，尤其是“token 的 K/V 一经计算就不变”、统一的 weights+KV 推理内存下界和 prefill 后直接得到首 token 的时序。[D29]
3. “扩散没有 KV cache”已经不可作为普遍判断；“普通 AR KV cache 可以原样使用”同样不成立。存在近似缓存、延迟缓存/周期刷新、训练得到的 block-causal 缓存边界，以及 encoder-context 与 mutable canvas 分离的体系。这些方案的正确性边界和成本不同。[D11–D13, D18, D24–D27]
4. 不能把“多个位置并行预测”换算成同倍数 wall-clock 加速。并行预测可能减少依赖深度，但增加总位置计算、attention、logits、采样缓冲与验证工作。减少步数还可能改变采样分布和任务质量。[D10, D33–D34]
5. 公开记录支持的代表性实例包括开放权重的 LLaDA、Dream、LLaDA2.2 和实验性 DiffusionGemma，以及封闭 API Mercury 3。Gemini Diffusion 的官方页面仍称 experimental demo。它们不能放在同一栏里视为相同成熟度的生产系统。[D17–D23, D35]
6. 最强反例来自支持者自己的记录。Google 明确说明 DiffusionGemma 整体质量低于标准 Gemma 4，低并发收益不能直接外推高 QPS；LLaDA2.2 报告承认复杂 JSON/SQL/tool-call 的局部一致性问题；早期 LLaDA 论文在 MBPP 上并未胜过 AR 对照。这比选择单个最高 tokens/s 更有架构价值。[B01–B04, D15]

## 2. 范围、证据与时间纪律

本研究不覆盖视频生成/Wan，不做第二份视频产品调查。讨论 continuous diffusion 的目的仅是建立生成机制关系，再转向离散文本与部署后果。DiffusionGemma 的多模态输入只作为支持边界说明；不把输入视频理解误写为输出视频生成。

claims.json 是逐条论断台账。每条含来源 URL、原始字节 SHA-256、文本文件、行号、引文和限制。数字性能记录 B01–B05 有相同的条件字段：模型修订、硬件、精度、输入/输出长度、采样 schedule、NFE、batch、质量指标、baseline、发布日期和服务定义。未公开或未核实的条件明确保留 UNVERIFIED。来源字节和抓取时间见 source-manifest.json；本研究没有下载模型权重或执行模型。

本书的 provenance 与 epistemic status 不能混用：方法作者对自身算法的描述、厂商规格可记 [1P][FACT]，意思是“来源确实这样写”，不是已复现的性能事实。算式记 [DERIVED]，示意输入记 [ILLUSTRATIVE][ASSUMPTION]。第三方对 LLaDA/Dream 的原始评测论文虽是直接读取的 primary publication，但按本书第 26 章的来源分类，对模型的外部测量采用 [2°]。本次没有 [LAB] GPU 测量。台账的 UNMEASURED 指本研究未测量，不是否认论文作者声称做过实验。

实际截止规则：design/manuscript/chapter-27/chapter-27.md:3–14 明确冻结四家比较与 A.10 来源列表在 2026-08-30，并且只允许已明确框出的 2026-09-27 观察作为现有例外。不能把 Mercury 3（官方发布页 2026-10-19）或 Flash-dLLM（arXiv v1 2026-09-22）塞进四家表格。即使某模型在 8 月前已发布，本次下载的 main/模型卡修订也不是 8 月归档的证明。[D30]

建议：正文新增不依赖近期产品名的机制小节；另建明确标注“2026-10-28 UTC research snapshot; outside the frozen comparison”的独立短附录/附录附页。这样也避免把 A.6 的“single”后快照例外静默改成多个。

## 3. 机制关系：相关，不等同

### 3.1 Continuous diffusion、score 与 ODE

DDPM 的正向过程用预定噪声逐步破坏连续数据，反向模型学习恢复。简化训练目标预测噪声，与加权 denoising score matching 有关系。score 是受扰动数据分布的 ∇x log p_t(x)，不是模型输出的通用“置信度”。[D01–D02]

SDE 框架描述正向噪声过程及其 reverse-time SDE。相关 probability-flow ODE 在理想条件下可具有相同时间边缘分布，但其样本轨迹不等同于随机反向 SDE。有限步数求解误差、随机性与 NFE 也不相同。“deterministic sampler”不意味着一次前向或无需迭代。[D02]

### 3.2 Flow matching 与 rectified flow

Flow matching 对指定概率路径的向量场做回归，可以采用 diffusion path，也可以超出这种路径。它不是把 DDPM 的同一个 loss 改名。Rectified flow 从连接两端样本的直线插值学习输运场，可用再次 rectification 改善路径；训练用直线插值不保证学到的所有生成轨迹严格直线，更不保证任何模型都一步达到同样质量。[D03–D04]

它们与 score-based diffusion 都可从简单分布出发，重复调用模型、积分或更新状态得到样本，因此共享“顺序迭代×每步工作量”的系统问题。但训练目标、路径、采样器与状态空间须分别说明。不能由一个图像 flow 模型的机制推断某个封闭文本 API 的内部算法。

### 3.3 离散与 masked diffusion

文本 token 是类别变量。D3PM 用类别状态上的 Markov transition matrix 定义 corruption，可使用 uniform replacement、absorbing state 等形式。吸收态可以是 MASK；masked diffusion 是其中一类，不是离散扩散的唯一实现。[D05]

MDLM 展示 masked diffusion 的 likelihood-bound 训练与 carry-over unmasking。LLaDA 采用随机 mask 比例，loss 仅计算被 mask 位置，并有与 mask 比例相关的权重。非因果 Transformer 根据当前完整状态预测缺失 token。SFT 保持 prompt 清洁、扰动 response，以学习条件分布。不能把这种目标等同于固定 mask 比率的普通 MLM，也不能把它等同于 next-token cross entropy。[D06–D07]

语言模型是否 diffusion，与是否输出 chain-of-thought 是两个轴。AR 模型的长推理、反思和 agent tool loop 不因重复调用就变成 diffusion；dLLM 也可生成推理文本，其内部 denoising round 不是一次 agent turn。DFlash 是第三种组合：diffusion drafter 提议块，AR target 验证；target 的因果分布没有因此变成 diffusion 分布。[D28]

## 4. 从训练目标到 inference trajectory

### 4.1 原始 masked canvas

给定清洁 prompt 和输出容量 G，LLaDA 的基本 generate 从 G 个 MASK 开始。每轮前向预测各 mask 的 logits；sampler 选择本轮提交的位置，其余候选保持 MASK。论文的随机 remasking 对应反向过程；low-confidence 选择是改变采样路径的策略。[D08]

重要区分：重新 mask 低置信的本轮候选，不一定是反复修改已提交 token。实际 generate.py 用 torch.where(mask_index, x0, x) 保持已解码位置。它还预分配 prompt+gen_length，并按配置跑循环；输出里的 EOS 或后处理裁剪不等于立即停止所有计算。当前仓库另有按块追加的 var_generate，不能把基本 generate 的行为外推到所有入口。[D08]

Dream 的被检视 sampler 在各轮用 full attention 前向，按时间或 confidence 更新 mask。它的 config 写 use_cache=true，但这只是配置字段，不是实现了正确持久 AR cache 的证明；同理 max_position_embeddings 不是经过验证的可用长上下文质量。[D09]

### 4.2 为什么并行会损失质量

同一前向得到多个位置的分布，通常是给定当前 canvas 的各位置边缘预测。这些预测并未互相条件化到本轮刚采样的其他位置。因此，独立地接受多个“看起来合理”的 token，可能得到不合理的组合。confidence threshold、动态接受数量、更多轮数、重新加噪或 verify pass 都在处理这个问题，不能视为纯粹免费系统优化。[D10]

### 4.3 Block diffusion 与编辑

Block diffusion 将外层序列分为因果排列的块，块内反向生成可以双向。对训练/推理 mask 一致的 block-causal 模型，后续块不能反向改变已完成前缀的状态，因此可复用该前缀。块内 mutable state 与前缀仍需分开处理。[D13]

Fast-dLLM v2 是对 AR 模型的 block-diffusion 适配，不是 v1 的一个缓存 flag。LLaDA2.1 将 mask-to-token 与 token-to-token editing 组合。LLaDA2.2 再支持 keep/substitute/delete/insert，补齐位置后继续编辑，但实现仍通过 padding/truncation 恢复固定 block 长度；不能描述成任意增长的全局 canvas。[D14–D15]

停止也不是单一“收敛”：可以是 mask 清零、无位置更新、稳定/置信条件、EOS/长度上限，或 post-edit round 上限。SGLang 的 JointThresholdInDel 有防止原始 mask 无进展、累积 post-edit budget 和最终控制 token 清理的逻辑。它不提供语义正确性证明。[D25]

### 4.4 无 MASK 的离散反例

DiffusionGemma 的已发布卡说明 encoder 处理并缓存 context，decoder 对固定 canvas 双向去噪，完成后再编码并提交到 context cache，继续下一 canvas。SGLang 的 Gemma4Renoise 使用随机 token/renoising，不需要 MASK；带 entropy acceptance、上一轮 logits self-conditioning、稳定与置信条件、最大步数。这足以反驳“所有 diffusion LM 都从全 MASK 单调解除”的过度概括。[D18–D20]

## 5. 已核对的实例与成熟度

| 实例 | 已核实的记录 | 类型/边界 | 对本书的价值 |
|---|---|---|---|
| GSAI-ML/LLaDA-8B-Instruct | 官方发布公告 2025-02-14；检查到权重仓库文件列表、模型卡与 config | 开放权重研究模型；本次未加载权重。当前仓库另有 iLLaDA 公告，不能把原始 8B 称为最新家族版本 | 最清楚的 masked objective、固定 canvas 与“无优化不等于不能缓存”起点 |
| Dream-org/Dream-v0-Instruct-7B | 官方 checkpoint 公告 2025-04-05；论文 v1 2025-08-21；模型卡/config/generation code | 开放权重研究发布；仓库创建时间、发布公告、论文时间分开 | AR 初始化到 diffusion；full-attention 重复计算；config 字段不足以证明 runtime 支持 |
| inclusionAI/LLaDA2.2-flash | 官方 2026-07 公告，HF 创建 2026-07-16；模型卡、报告及对应 config | 开放权重，长上下文 agentic block diffusion；100B 为卡片的 non-embedding 口径 | T2T/InDel、block routing、服务端采样与评测采样不完全相同 |
| google/diffusiongemma-26B-A4B-it | 官方发布 2026-06-10，HF card/config/generation config | 实验性开放权重；卡列 25.2B total / 3.8B active；不是“已替代 AR 生产模型” | 无 MASK 的离散采样；encoder/cache 与 bidirectional canvas；低并发硬件利用 |
| mercury-3 | 官方发布页 2026-10-19；当前 API 文档还列 mercury-2.5、mercury-2 | 封闭商业 API，厂商记录显示可用；本次未认证调用。权重修订、内部架构/NFE/精度未公开核实 | API 合约与内部执行分开；普通流式/修订快照的两种语义 |
| Gemini Diffusion | 官方模型页明确 experimental demo | 不是已核实的开放 checkpoint 或通用自托管 runtime | 演示存在不等于生产支持边界明确 |
| Fast-dLLM / dKV-Cache / Flash-dLLM | 原论文、官方仓库，Flash 含 Triton kernel/eval 源码 | 研究方法及实现，不是独立的新基础模型产品；Flash 是 8 月之后论文 | 缓存/刷新、核函数/额外 verify 的真实成本 |

依据：[D17–D28, D35]。精确修订：LLaDA 08b83a6feb34df1a6011b80c3c00c7563e963b07；Dream 05334cb9faaf763692dcf9d8737c642be2b2a6ae；LLaDA2.2 9b78da3f9149f1e239fb6d15f20a326fde574b9f；DiffusionGemma f7f5b7f5fa82ffc52addd066915886d497f5517b。上述是本次检查的 HF revision，不是论文 benchmark 使用相同 revision 的保证。模型卡与 config 已用这些 revision 再次固定抓取。

支持边界差异：DiffusionGemma 卡的叙述含 video input，但规格表及检视的 SGLang recipe 列 text/image。本文不认证 video runtime 支持。LLaDA2.2 card 的评测配置 temperature=1.0，官方 SGLang JointThresholdInDel 实现却明确 greedy；两者不可视为同一采样分布。[D19, D25]

## 6. 资源预算：需要替换的不是 token，而是执行账本

### 6.1 统一工作模型

定义 C 为 prompt 长度，G 为最终输出 token，K 为 canvas/block 长度，S_b 为第 b 块实际迭代数。第 j 次模型调用计算 Q_j 个 query/token 位置、访问 A_j 个 attention pair。NFE 记录实际网络评估；还记录调用类型、处理形状与批维，避免把 CFG 两路合并的一次 kernel dispatch 误算成只有一路工作。

投影主导的近似：

    F_projection ≈ Σ_j 2 P_active,j Q_j
    F_attention ≈ Σ_j 4 n_layers d A_j

第一式继承本书 2N 的近似，不能用输出 token 直接代替 Q_j。第二式只对应常规 dense attention 的 QK/AV 主项；GQA、滑窗、分层结构、padding、heads 与输出投影需依具体模型调整。这些是 [DERIVED][ANALYTICAL] 的预算工具，不是性能公式。[D33]

几种不同账本：

- 无缓存全 canvas：每步可重算 C+G，投影工作近似 S×2P(C+G)，attention pair 工作 O(S(C+G)^2)。源码的 full forward 不会因为只提交少数 token 就自动只算这些位置。
- 固定 context、块内 K 位置去噪：每步可能只对 K 位置做 decoder 投影，但 attention 仍访问前缀，主项 O(K(C+prefix+K))；加一次 encoder prefill、block commit 编码及刷新。
- 固定 query window 的近似 cache：Q_j 可较小，cache read 仍可扫描长 context。不要从减少 query 数跳到“全部 attention 成本同倍下降”。
- verify、CFG、refresh、extra editing 各自进入账本；外层 S 不是通用 NFE。Flash-dLLM 的 verify pass 就是显式反例。

依赖深度与工作量是不同轴。下列算例由 calculate.py 实际计算，详见 calculations.json；输入均为 [ILLUSTRATIVE][ASSUMPTION]，不是任何模型测量：P=7B、G=256、block=32、每块 8 次 forward。外层有 8 块，64 次顺序去噪调用，但 decoder 位置累计 2,048，投影近似 28.672 TFLOP。输出端 AR 简化计数为 256 次位置计算、3.584 TFLOP。该示例将顺序步数降到 1/4，却把输出投影工作提高到 8 倍。未计 prompt、context attention、commit 编码、head、通讯、verify；也简化了本书首 token 计入 prefill 的约定。因此它不是 4 倍加速或 8 倍总计算的实测结论。

### 6.2 Roofline、MoE 与网络

一次处理更多位置，可让相同权重服务更多矩阵行，改善低 batch 时的 arithmetic intensity；所以增加 FLOPs 仍可能降低 wall-clock。但当 AR 已被请求 batch 饱和，或 diffusion 每步大量重复计算，收益会变小甚至反转。Google 的低并发定位与 Fast-dLLM 的大 batch 限制支持这种条件性解释，而不是“diffusion 天生 compute-bound”的定律。[B02, D11]

MoE 的 per-token active 参数还不等于一次并行块的 expert union。LLaDA2.2 先把 block expert pool 限制为 48，再在 pool 内为各 token 做 top-8，来源 config 共 256 routed experts。意义是控制专家工作集，不是把模型 residency 减成 active 参数。多位置 routing 也可能增大 all-to-all、激活缓冲和负载不均；必须测 expert 分布与 TP/EP 通讯，不能从 token 并行推断通信消失。[D16]

### 6.3 内存与 state

推理峰值应分解为：

    M_peak = W_resident + M_reusable_context + M_mutable_canvas
             + M_activations/logits + M_workspace + M_runtime

各项要按真实 lifetime 计量，别把共享 tensor 重复加。普通 AR 的 KV bytes/token 公式仍适用于实际存下来的 K/V 张量，但不证明它们可跨 diffusion round 复用。[D34]

- 双向注意力下，不变的 token ID 仍可能因其他位置变化而产生不同 hidden/K/V。Fast-dLLM 的 approximate prefix/DualCache、dKV 的一步延迟与周期刷新，以及 Flash 的 attention-guided selective refresh 都在处理这一点。
- block-causal 前缀、encoder context 与 mutable decoder canvas 可提供明确的复用边界。这里要问“什么状态不再依赖会变化的 token”，而不只是“是否有 cache”。
- inference 无 autograd 时，增加迭代不必线性增加峰值内存；存 history、上一轮 logits/self-conditioning、验证双视图会改变结论。Dream 的可选 histories.append(x.clone()) 是明确的生命周期差异。
- 单 batch 的 256×262,144 FP32 logits 已是 268,435,456 bytes，即 256 MiB，仅为张量形状算术，不是实测峰值。采样概率、排序、FP64 噪声、workspace、self-conditioning 与 batch 还可能增加峰值。LLaDA 参考代码在非零温度时把 Gumbel 相关张量转 FP64，权重 BF16 不代表全部运行时 tensor 都是 BF16。

依据：[D08, D11–D13, D18–D20, D27, D34]；logits 示例已由 calculate.py 核算。

### 6.4 真实 serving 支持不能由模型名推断

本次检查 SGLang revision a1966e1b5d8b750b494d7e53cca1d2464f960038 的 scheduler、算法与测试源码，未运行它们。FDFO 允许 block 完成请求先离开 batch，保留未完成 block 的 state/KV。这是对不等迭代数的专用处理，不是宣称 AR continuous batching 原样适用。[D24]

Paged block table 可以用于分配，但它不解决 stale K/V 的数学有效性；prefix cache 的 key 还必须对应已提交真实 token，不能对应未解码 MASK。不同 S_b 使 lockstep batch 有尾部浪费；吞吐、抢占/取消、request lifetime 和 p99 都取决于调度实现。[D24]

更具体的反例：同一 SGLang revision 的 Gemma4Renoise 明确禁用 radix cache、chunked prefill，拒绝 quantized loading、pipeline/context parallelism；检查到的 request validator 拒绝 grammar/JSON-schema/logit-bias 等，普通 temperature/top-k/top-p 不控制其 renoise sampler。厂商其他引擎的 FP8/NVFP4 宣传不等于该 backend 已支持。[D26, D36]

文档/源码差异也必须保留：cookbook 简述 Triton/eager，但算法已有 triton/fa4 backends 以及受 fa4 条件约束的 FULL-prefill CUDA graph 路径。不能照文档写“永远不能 graph capture”，也不能凭静态代码声称已在目标机器运行。CUDA/ROCm 字样不构成所有 AMD/NVIDIA SKU、CPU 或 Apple 的通用认证。[D36]

Flash-dLLM 仓库确有 Triton kernel、fused projection/RoPE/cache write 与 eval loader；“已有 kernel”是可核对事实。“在本机可用”未验证。dInfer 最初 /main/README.md 为 404，经官方 repo metadata 找到默认分支后成功获取；README 的不同 backend/模型映射不能泛化到所有 dLLM。[D27]

## 7. 服务指标：首个可见字不等于首个承诺字

为同一请求记录以下时间点：接收、入队、admit、context encode 完成、首份 draft、首个不可撤销输出前缀/块、最终提交、验证完成。TTFT 必须说明是 draft 还是 committed。对语音、工具调用或流式消费者，尚会被覆盖的文本不能作为等价的已提交输出。[D20, D22, D26]

普通 AR 的 ITL 描述相邻提交 token 的间隔。对 block stream，一次包里有很多 token、包间等待较长；客户端把同一包拆成零间隔 token，会人为制造很漂亮的 ITL。应报告 block arrival gaps、block 大小分布、first-commit latency、time-to-final/valid answer，以及实际 consumer stall。平均“decode duration/output tokens”可以保留为摊销速率，但不可替代交互尾部时延。

Mercury 文档的 diffusing=true 每次返回正在改进的全文，而不是新的 append-only delta；重放时必须覆盖，而不是拼接。它可以让首屏更早，但不能重复计量修订字数为最终 throughput。其 JSON-schema 文档是产品合约描述，不是本研究测到的 100% validity。[D22]

goodput 建议并列两个口径，避免把新实验偷换成旧定义：

- 本书已有的 token SLO-goodput：只计最终提交且满足已声明时限的 token，不计被覆盖的 drafts。
- 额外的 successful-request goodput：Σ 1[task valid AND quality pass AND service SLO pass] / 测量墙钟时间。

后者是新协议定义，不是对全书 goodput 概念的无声改写。重试、fallback 和工具执行若在服务范围内，必须计入时延、成本与成功率。

## 8. 性能数字：保留条件，拒绝排名

| 记录 | 论文/厂商实际声称 | 已知条件与最关键缺口 | 可采用的结论 |
|---|---|---|---|
| B01 LLaDA | GSM8K/Math 在所选质量点报告 1.5×/1.8×；MBPP 落后 | 单 A100 80GB、双方 BF16、batch1、输出256；速度点具体 NFE 未核实，任务 prompt 均值不同 | 任务与采样点会改变胜负，不能宣布扩散普遍更快 |
| B02 DiffusionGemma | 卡报告低 batch H100 FP8 >1100 tok/s；博客 up to 4× | exact batch、prompt/完整输出分布、speed-run revision/NFE 未披露核实；质量不等价 | 低并发/硬件利用假设值得测；高并发成本与质量须另测 |
| B03 Mercury 3 | 1068 tok/s、4–8× 对比 | 只有 NVIDIA GPUs 类别；SKU/数量、精度、batch、长度、schedule/NFE、服务边界未核实 | 只能写 vendor-reported；不能与自托管 GPU 结果做资源效率排名 |
| B04 LLaDA2.2 | 11 workloads BF16 平均1.64×；FP8再增18.6% | baseline Ling-2.6-flash 启用4-token MTP；硬件/实际长度分布/速度运行 NFE 与精确 revision 未核实；SWE scaffold 也有差别 | 新 agentic block-diffusion 证据，但不足以证明本书 canonical SLO 改善 |
| B05 Flash-dLLM | 对 uncached greedy diffusion 报22.3–148.2× | 单 A10080GB、batch32、长度256/512；BF16 loader 已查但论文 run 精度对应未核实；动态 NFE、checkpoint revision 不完整 | 证明 baseline 选择很重要；不是相对优化 AR 的同倍加速，verify 也非普遍无损 |

完整条件在 claims.json，不把缺失值补成常见默认设置。Flash 表中 HumanEval512 的 verify pass@1 为40.24%，confidence-only 为42.07%；这只是来源自己的可核对反例，未在本机复现。[B05]

独立反面材料：The Bitter Lesson 的原始评测检查较早的 LLaDA/Dream 类模型，报告 tool format 与 feedback replanning 失败；不能把它投射到之后的 LLaDA2.2/Mercury3。The Flexibility Trap 区分任意生成顺序与并行更新，并指出高置信优先可能绕开需要探索的不确定位置。两者否定“可编辑所以必然推理更好”，不证明扩散永远不适合 agent。[D31–D32]

## 9. 可复现比较协议（设计，未运行）

目标不是安排一个最快排行榜，而是估计在同质量门槛下的资源与 SLO Pareto frontier。

1. 冻结工件。记录每个模型/tokenizer/config/engine commit、权重 hash/量化配方、driver/CUDA/ROCm/PyTorch/Triton/compiler、kernel backend、图编译开关。封闭 API 记录 model ID、请求时间、region、可见版本、retry policy；内部 NFE/硬件不可见则标 unknown，放在独立服务对比层，不做 GPU FLOP 效率归因。
2. 冻结语义请求集。采用同一份 RAG 输入、长文本、代码 infilling/固定区编辑、嵌套 JSON/tool calls；保留任务输入 byte hash 和每种 tokenizer 的 token 长度。一个层次固定可比较 token 形状分析硬件，另一个层次固定真实语义/字节分析服务；不能靠截掉不同内容强行等 token。
3. 冻结质量门。预先写明 exact match、unit-test pass、schema validator、保留区域不变性、grounded answer rubric。校准集选择 schedule/cache/threshold，holdout 才测结果；保留随机 seeds 与置信区间，禁止用最终测集调到“质量相同”。
4. 给两方合理优化。AR 至少分别测 optimized KV+batch 和可用 speculative 路径。diffusion 测完整回算、cache/refresh、block size、threshold/step cap、self-conditioning 和 verify 的适用组合。普通 AR FIM 也是编辑 baseline，不能把 infilling 宣称为 diffusion 独占。
5. 对每次请求记执行 trace。列每次 forward 的 shape、有效计算位置、attention context、CFG分支、refresh/verify、NFE、已提交 tokens、draft revisions、EOS 后浪费和 padding。用 profiler 测 kernel 时间、HBM/activation/workspace 峰值、通信、host sampling 同步；NFE 与 FLOP 估计分开。
6. 先做单请求 warmed steady-state，再做 batch sweep 与 open-loop offered-load sweep；同时记录编译/冷启动一次性成本。混合短/长 context，构造慢收敛请求，测试 FDFO/lockstep、取消、OOM、admission/reject、排队；不得只用 closed-loop 隐藏过载。
7. 输出 p50/p95/p99 的 draft/commit/final/valid latency、block gap、raw final-token throughput、本书 token SLO-goodput 和额外 valid-request goodput、能耗和成功任务成本。相同 quality gate 下才比较服务前沿；没有达到门槛的点保留失败，不拿更低质量换一个“更快”。
8. 本书 canonical 9.2K-in/300-out 单列为真实 workload case。先检查各模型的实际语义能力和长度支持，再在实测服务时间/内存下重算 fleet：使用观察到的成功率、排队与重试，不把 300/S 直接乘现有 host capacity。

复现所需执行环境尚未配置，协议不含伪造结果。calculate.py 只核算示意算术，不冒充 GPU benchmark。

## 10. 对实际章节的集成地图

| 源码锚点 | 建议 | 为什么不扩写成产品目录 |
|---|---|---|
| chapter-01:9,29,39,63 | 保留已有 AR 限定；在 summary chain 附一句“AR baseline”，并指向第3章 alternative-inference | token 的概念不需重建；attention prior-only 与缓存表述需相邻限定 |
| chapter-02:5,9,13,25 | 在模型开头/图附近补 causal decoder-only baseline；在 K/V invariance 句前加因果条件 | 首 token 属 prefill 的现有约定不能无条件用于可变 canvas |
| chapter-03:7–17 / :106–132 | 主集成点：紧接 dense/MoE 对比补一个紧凑 mechanism-first section，或放在 architecture consequence 的小节 | dense/MoE 是参数激活轴，AR/diffusion 是执行/分布轴，两者正交 |
| chapter-07:9–22 / :90 | 加 immutable-context vs mutable-canvas residency box | 不否定现有 AR KV 算式，只阻止把它当全部推理内存 |
| chapter-08:11,33–55 / :145 | 加“processed positions, not final tokens”成本框与一个示意算例 | 2N 仍有用，乘数必须变；attention/verify另列 |
| chapter-11:58–86 / :132–149 | 加 iteration-aware scheduler 与 support-boundary inset，明确 DFlash 不是完整 diffusion 服务 | 不静默把现有 Orca/PagedAttention/PD 的机制换成厂商泛称 |
| chapter-06:15 / chapter-14:28–42,53–60 | 加 draft/commit/final 时序与 matched-quality protocol | 保留已有质量筛选→部署筛选，补齐 burst stream 语义 |
| chapter-05:9–17 | 把 inference algorithm/runtime compatibility 放进 latency/context/cost surfaces | 不凭“扩散”标签先选模型；编辑与低并发是待检验候选场景 |
| chapter-26:23–40 | 可选加一行编辑/低并发生成模式，绑定验证指标 | 继续 workload→constraint→strategy，不设“diffusion 总是最快”捷径 |
| chapter-27:3–14,158–160 | 不改 frozen four-family table；新建独立 2026-10-28 UTC addendum | 后快照证据不能反向污染8月比较与来源清单 |

上表路径前缀均为 design/manuscript/chapter-NN/chapter-NN.md。具体英文候选及 exact before/after anchors 在 proposed-insertions.md。它们未应用，因此没有插入后的全书渲染 PDF 校验；已单独检查图的实际尺寸 Letter proof，但不等同于审完整书稿 PDF。

## 11. 图示实现与交付

已按追加要求制作两张原始机制图，而不是停在蓝图。D1 展示 continuous / masked discrete 的正向 corruption 与 learned reverse 两条分离箭头通道，并明确 flow matching 不等同于 diffusion。D2 展示“what stays fixed, what changes, what can be emitted”，而不是图像 diffusion 的装饰噪声图。下面是 D2 的机制组织：

- A 行 AR：固定因果前缀逐 token 延长；接受 token ID 与处理该 token 后得到 K/V 分开。图注限定快照已包含最新接受 token 的处理，避免 off-by-one cache 误读。
- B 行 full masked diffusion：fixed prompt + mutable canvas → repeated full forwards；用虚线回边表示下一轮，少数位置标 accepted/remaining；明确这个选定 sampler 不编辑已接受位置。
- C 行 block diffusion：因果前缀 → 可变块内重复 refinement → finalize/cache → 前缀延长。图脚说明 editing/renoising sampler 可不同；英文正文另外明确 uniform-state renoising 无需 MASK，避免把示例当作所有 dLLM 的定义。
- 每行标明重算范围与已 finalise 的前缀，并用真实连接到中间状态的回环表示重复评估。箭头不标实测时间，网格大小不暗示真实模型大小或速度。
- 图例用字母、问号、短横线、括号、虚线与纹理区分 accepted IDs、unresolved/inactive positions、finalized prefix 与 recomputed state。图注标 [ILLUSTRATIVE conceptual]，具体 evidence/claim IDs 见 manifest。英文候选正文显式引用两图。
- 从 US Letter build 与左右各 1.2 in 的真实页边距导出 6.1 in 文本宽度。生成器输出 400 PPI PNG、可编辑 SVG、矢量 PDF、灰度图与实际尺寸 Letter proof，均在 figures/。再审修正了 block 边界交叉、浮动回环、accepted ID 与 cached state 混淆问题；实际检查和剩余限制见 figures/QA.md。

## 12. 未解决事项与交付边界

- 没有 GPU/CPU 模型 benchmark、API 调用、实际 engine launch、load test 或 kernel 编译。支持结论是 pinned 源码/官方记录范围，不是本机运行成功。
- Mercury 3 的内部配置、精度、硬件数量、NFE、cache/stream commit 实现未公开核实；不逆向猜规格。
- 部分公开 speed claims 缺完整 schedule、checkpoint revision、输入分布和质量对应点；保持 UNVERIFIED，不产出跨模型速度排名。
- DiffusionGemma 的 vendor runtime 声明与当前 SGLang quantization/graph/structured-output 支持有边界差异；真实部署要逐版本重测。
- 第三方早期 agent 失败研究不能关闭后续模型的 agentic 研究问题；后续报告也没有消除严格 JSON、长期错误积累与训练/推理对齐问题。
- 原始 LLaDA 论文的“incompatible with KV caching”应按该实现/时期理解，不能盖过之后官方实现。
- 与 8 月 cutoff 相容的历史版本仍需单独重建。当前抓取只能证明本次读取的内容，不能认证历史快照。
- 不改 manuscript、共享图稿或配置，不提交、不推送、不委派。新增图与候选正文仅写入本研究目录；仍需负责主稿的代理决定采纳、核对交叉引用、重建并验证完整 PDF。

## 13. 可直接查阅的一手入口

所有链接对应本次 source-manifest.json 中的实抓记录；具体引用段见 claims.json。

- DDPM：https://arxiv.org/abs/2006.11239（原文 HTML 已保存）
- Score SDE：https://arxiv.org/abs/2011.13456
- D3PM：https://arxiv.org/abs/2107.03006
- MDLM：https://arxiv.org/abs/2406.07524
- Flow matching：https://arxiv.org/abs/2210.02747
- Rectified flow：https://arxiv.org/abs/2209.03003
- LLaDA：https://arxiv.org/abs/2502.09992；https://github.com/ML-GSAI/LLaDA
- Dream：https://arxiv.org/abs/2508.15487v1；https://github.com/DreamLM/Dream
- Block diffusion：https://arxiv.org/abs/2503.09573
- Fast-dLLM：https://arxiv.org/abs/2505.22618；https://github.com/NVlabs/Fast-dLLM
- dKV-Cache：https://arxiv.org/abs/2505.15781；https://github.com/horseee/dKV-Cache
- Fast-dLLM v2：https://arxiv.org/abs/2509.26328
- LLaDA2.1：https://arxiv.org/abs/2602.08676
- LLaDA2.2：https://github.com/inclusionAI/LLaDA2.X；https://huggingface.co/inclusionAI/LLaDA2.2-flash（报告 PDF 已保存）
- DiffusionGemma：https://blog.google/innovation-and-ai/technology/developers-tools/diffusion-gemma-faster-text-generation/；https://huggingface.co/google/diffusiongemma-26B-A4B-it
- Gemini Diffusion：https://deepmind.google/models/gemini-diffusion/
- Mercury 3：https://www.inceptionlabs.ai/blog/introducing-mercury-3；https://docs.inceptionlabs.ai/get-started/models；https://docs.inceptionlabs.ai/capabilities/streaming；https://docs.inceptionlabs.ai/capabilities/structured-outputs
- Flash-dLLM：https://arxiv.org/abs/2609.26796；https://github.com/VILA-Lab/Flash-dLLM
- DFlash：https://arxiv.org/html/2602.06036
- 原始反面评测：https://arxiv.org/html/2601.12979；https://arxiv.org/html/2601.15165
- pinned SGLang 核心： https://raw.githubusercontent.com/sgl-project/sglang/a1966e1b5d8b750b494d7e53cca1d2464f960038/python/sglang/srt/dllm/algorithm/gemma4_renoise.py

上述 GitHub/HF 仓库根链接作为导航；实际读取的是 manifest 中的 raw/API/固定修订 URL，不能把导航链接误记为本次逐页审阅。完整源索引和可复跑检查见 source-index.md、validation.json。
