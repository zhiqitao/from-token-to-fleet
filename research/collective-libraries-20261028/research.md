# 加速器集合通信与 MPI：机制、边界及入书建议

研究快照：2026-10-28 UTC（本地 2026-10-27 PDT）。本报告由独立研究代理完成，未继续委派。只在本研究目录落盘。没有修改书稿、配置、版本历史或发布物。

## 0. 结论与证据边界

NCCL、oneCCL 与 MPI 不是“GPU 通信与 CPU 通信”的对立。MPI 是接口与语义标准；Open MPI、MPICH、Intel MPI 是实现。NCCL 与 oneCCL 是特定集合通信库。共同基础是参与者、通信组、类型、计数、归约与数据分布；主要差异在实现覆盖面、设备运行时集成、执行进度、错误处理、拓扑选择与支持矩阵。[mpi50-pdf][nccl-api-header][oneccl-header]

本次独立确认的高优先级问题：

1. 冻结 PDF 物理 141 / 印刷 123 的 0.27 s 不能在其给定的点到点 ring 模型下成立。140 GB、8 ranks 给出每 rank 发送 245 GB，另接收 245 GB。H100 每 GPU 的 900 GB/s 双向总和对应每方向 450 GB/s。配对正确的式子是 245/450 = 490/900 = 0.54444 s。不是 245/900。它是理想字节项，不是实测。[nccl-performance][h100-datasheet] CPU 独立计算已运行，见 calculations.json。
2. 140 GB 输入不能放进单张 80 GB GPU。两张 GPU 能放下 140 GB 权重，不代表训练时权重、梯度、优化器状态、激活和临时区一起放得下。不能把“多 GPU 组成一个逻辑 DP replica”直接代入“一个 NCCL rank 对应一个 CUDA device”的公式；须说明实际 communicator 与分片。[h100-datasheet][nccl-init]
3. 被归档/弃用的是旧 Intel torch-ccl 绑定仓库。不能由此推出 oneCCL 停更。oneCCL 官方仓库 API 在本次获取时为 archived=false，默认分支 master-v2；GitHub latest release 为 2022.1.0，发布时间却是 2026-08-15。2022.1.0 是版本字符串，不是发布时间年份。[torch-ccl][oneccl-repo][oneccl-release]
4. 不能把 PyTorch backend 名 xccl 当成已经核实的独立 Intel XCCL 后继库。PyTorch v2.9.0 文档推荐 XPU 使用 XCCL；本次 pinned torch-xpu-ops 代码调用 onecclComm_t 与 oneccl 包装接口。另一份 RFC 是演进提案，不是已发布支持矩阵。试探 intel/xccl 仓库返回 404，本报告不据此构造产品迁移叙事。[torch-v29-doc][torch-xccl-code][xccl2-rfc]
5. GPU-aware MPI 确实存在，但不能把“有设备指针支持”扩展成“所有非阻塞/持久化集合操作均支持设备缓冲区”。Open MPI v5.0.x 文档分别列 CUDA-aware 与 CUDA-aware UCX 的限制，明确列出非阻塞归约的限制。MPICH v5.0.2 文档列 CUDA、HIP、Level Zero 构建支持，也不是逐操作保证。[openmpi-cuda][mpich-v502]

证据规则：方括号中的检索键对应 sources.md 和 claims.json 的 source_id。每条源记录含实际获取 URL、UTC 获取时间、原始 SHA-256、局部引文与版本范围。失效请求保留在 retrieval.json，但不作为证据。可变分支与在线文档只证明本次抓取快照；本地哈希保存了所读内容，不自动证明历史版本支持。供应商性能说法不提升为独立测量。

冻结基线：review/publication_v2_20261028/baseline/from-token-to-fleet-v20260913.pdf；361 页；612×792 pt，即 US Letter 8.5×11 in；SHA-256 66f8392d6b768de7af4695b3d93d70b48858eb75a944020dbcfa9f4d1768b758。物理 17 / 印刷 xi 的证据截止为 2026-08-30。NCCL v2.32.3-1（2026-09-17）和 MPICH v5.0.2（2026-09-28）晚于该截止，不应静默写回旧版。[nccl-release][mpich-release] 本次仅研究与提出未应用候选文本；不是全书视觉审校或发行认证。

## 1. 先定义语义，再选择库

本节限一个 intracommunicator。rank 是组内编号，不等于节点；一个进程可管理多个设备，也可有多个 communicator。rank 的组内顺序决定 gather 拼接及 scatter 分区顺序。communicator 同时给出参与群体与通信匹配上下文。[mpi50-pdf][nccl-init]

等长稠密张量是解释 all-reduce 的常用特例，不是所有 MPI 集合操作的总约束。实际约定至少包括 communicator、操作顺序、root（有则必填）、元素 count、dtype、归约 op、缓冲区布局与 in-place 规则。MPI 允许 derived datatypes，部分集合操作有 v/w 变长/异构类型接口；GPU 库的连续 typed-buffer 接口通常更窄。相同字节数不等于匹配的类型签名。[mpi50-pdf][nccl-api-header][oneccl-header]

| 操作 | 输入与结果（N ranks） | 容易混淆的边界 |
|---|---|---|
| all-reduce | 每 rank 输入 c 元素；按对应元素归约；每 rank 得到 c 元素 | SUM 不自带除 N；库可另提供 AVG 或自定义 op |
| reduce | 同样的逐元素归约；完整结果只在 root 有效 | 不是每个 rank 都得到完整结果 |
| all-gather | 等长特例：每 rank 输入 c 元素；每 rank 得到按 rank 顺序拼接的 Nc 元素 | 拼接不做求和；变长需明确接口 |
| reduce-scatter | 等分特例：每 rank 输入 Nc 元素；归约后每 rank 得到自己的 c 元素分区 | 输入 count 与输出 count 不能混用 |
| broadcast | root 的 c 元素被复制到各 rank | 不是把各 rank 的输入相加 |
| all-to-all | 每 rank 输入 N 个目标块；rank j 接收每个源 rank 发给 j 的块 | 是源×目标分布转置；MoE 常需不等长 counts |
| barrier | 所有组成员进入后，成员才能完成同步 | 不传用户张量；不是隐式设备流同步或所有未完成通信的总等待 |

语义来自 MPI 5.0 第 6 章；NCCL v2.32.3-1 header 有 ncclAlltoAll 与 ncclAvg，不能重复旧时代“没有 all-to-all/只有 SUM”的断言。库没有显式 barrier API 也不表示框架没有 barrier：框架可用一个小集合操作实现；设备数据可用性仍依赖流/事件与具体 Work 完成约定。[mpi50-pdf][nccl-api-header][torch-xccl-code]

All-reduce 可以分解为 reduce-scatter + all-gather：先得到已经归约的分片，再把这些分片拼接。单独 all-gather 原始输入不完成归约；reduce-scatter 也不是 all-gather 的数学逆操作。[mpi50-pdf][nccl-performance] 独立小例：4 ranks 分别输入 [r,2r,-r,0]，r=1..4；SUM 是 [10,20,-10,0]，平均才是 [2.5,5,-2.5,0]。已用 CPU 检查两阶段分解，不声称调用了真实通信库。

浮点加法不满足实数意义上的结合律。MPI 5.0 §6.9.1 明确允许与结合律相关的重排，并建议实现尽可能重现结果；这不等于跨算法、规模、版本、设备都 bitwise 相同。固定 seed、数学上相同的 SUM 与 bitwise reproducibility 是三个不同约束。Python binary64 的 (1e16 + -1e16) + 1 = 1，而 1e16 + (-1e16 + 1) = 0；这里只说明原因。[mpi50-pdf] 确定性声明须限定 communicator、rank 映射、算法/协议、输入、dtype、kernel、运行时、硬件与版本；固定算法本身也不是充分证明。

## 2. 四层结构，以及另行存在的控制路径

```text
工作负载/框架：TP / DP / EP / FSDP / PP
                  |
框架 backend：ProcessGroupNCCL / ProcessGroupXCCL / Gloo / MPI
                  |
集合库或实现：NCCL / oneCCL / Gloo / MPI implementation
                  |
设备执行与传输：CUDA 或 SYCL/Level Zero；P2P、共享内存、RDMA/verbs、OFI、UCX、TCP
                  |
物理资源：HBM、NVLink/xGMI、PCIe、NIC、交换网络、NUMA

旁路控制路径：scheduler/launcher → processes → rank/device mapping
                              → store/MPI/PMI/rendezvous → communicator bootstrap
```

这是概念分层，不是每个库都经过所有盒子的调用栈。MPI 实现可内嵌集合算法，也可接入 UCC；oneCCL 的某些 transport 可用 MPI；NCCL 可用 MPI 分发 bootstrap ID，而集合 payload 仍由 NCCL 的设备与网络路径承载。OFI/UCX 是通信软件层，不是物理 NIC；Level Zero/CUDA 是设备运行时，不是 all-reduce 语义；PyTorch xccl 是 backend 名，不等于物理网络。[nccl-example-mpi][oneccl-atl-mpi][oneccl-atl-ofi][ucc][torch-v29-doc]

已制作 2 张原始机制图：CCL-F1 展示 SUM、reduce-scatter→all-gather 与逐方向字节；CCL-F2 展示 backend→library/algorithm→runtime/transport→hardware，并把 bootstrap 控制路径单列为虚线。后者用 NVIDIA 与 Intel 两条示例列，避免画成 NVIDIA 库调用 Intel runtime；没有为了列全厂商增加无教学价值的第三列。可编辑 SVG、矢量 PDF、300 dpi PNG、图注、alt text 与复现命令见 figures/manifest.json；整图、细节及灰度实际检查见 figures/QA.md。它们没有未经测量的性能曲线。

## 3. MPI 的公平基线

MPI 5.0 是规范，包含点到点、集合通信、communicator、派生类型、单边通信及更多能力。非阻塞集合操作返回 request；完成由对应测试/等待语义确定。持久化集合操作可先初始化 request，再重复启动；并不缓存结果，也不消除 payload 或自动消除设备同步。[mpi50-pdf]

GPU-aware/CUDA-aware MPI 一般指实现能识别并处理设备缓冲区。它不单独保证路径是 device-to-device RDMA；实现可能根据 size、协议、peer 可达性、registration、provider 和硬件走直接路径或 staging。GPUDirect RDMA 需要相应 NIC、GPU、驱动与拓扑支持；识别指针与实际绕过 host staging 是两项验证。[openmpi-cuda]

本次逐版本核验：

- Open MPI v5.0.x 的官方 CUDA 页面列出设备 buffer 的 MPI_Allreduce 等接口，同时明确 CUDA-aware UCX 不支持 MPI_Ireduce/MPI_Iallreduce 等非阻塞归约。该页面有不同路径的列表，不能挑一个列表扩展为所有组件的能力；列表甚至保留一个 MPI_Iialltoallv 拼写，未把该字面字符串解释为新增 API。[openmpi-cuda]
- MPICH v5.0.2 的 README 第 3 节列 CUDA、Intel Level Zero、HIP 的自动探测/构建开关。这证明这些 runtime 路径被项目声明支持，不证明任意 provider、datatype 或 persistent GPU collective 均可用。[mpich-v502]
- MPI 5.0 §2.4.4.1 的 progress 规则要求正确程序按 weak progress 假设编写。非阻塞调用允许重叠，但不等于后台必然自主推进，也不保证 overlap 有效。是否有 progress thread、调用 MPI_Test 的频率以及通信组件的能力，应在目标实现中验证。[mpi50-pdf]
- CUDA/SYCL 流上的 producer 与 MPI 调用必须建立明确依赖。不能仅凭设备指针有效，就认为 MPI request 已自动等待任意计算流。标准接口、实现扩展和框架封装须分别记录；本次未验证通用 MPI stream-aware 扩展的逐版本支持，因此不作其普及程度的断言。

合理比较对象是“给定版本/构建/provider 的 GPU-aware MPI collective”与“给定版本/构建/transport 的 accelerator collective”，不是“老式 CPU blocking MPI”与“现代 GPU 库”。

## 4. NCCL：主机提交不等于主机搬运

版本锚：GitHub latest release 在本次获取时为 v2.32.3-1，2026-09-17；对应源码树 SHA 及下载文件哈希见 claims.json。在线 user guide 是 2026-10-28 抓取，不假装所有在线页面都精确对应此 tag。[nccl-release][nccl-tree]

典型路径：

1. launcher 创建进程；应用确定 global/local rank、CUDA device 与通信组。NCCL 不替代集群调度器。
2. 生成 ncclUniqueId，经 store、socket、MPI 等带外分发；各 rank 调用 communicator 初始化。官方 MPI 示例用 MPI_Bcast 分发 ID，用 NCCL 执行 all-reduce；启动器/MPI 的存在不能证明 MPI 承载该张量 payload。[nccl-init][nccl-example-mpi]
3. NCCL 发现 GPU/CPU/NIC/PCIe/NVLink 等拓扑，搜索通信图，建立 channel/peer transport。tag 内 topo.cc、search.cc、transport.cc 是实现证据。[nccl-topo-code][nccl-search-code][nccl-transport-code]
4. 按 collective、规模、消息大小、拓扑与可用能力选择算法/协议/channel 配置。v2.32.3-1 的 src/tuning/cost_model.cc 包含 ring/tree/NVLS 等模型；不是单一固定 ring。[nccl-cost-model]
5. 主机 API 把操作提交到 CUDA stream；通常返回表示已入队，不表示输出已可供 CPU 或无依赖的另一流读取。同一流后续工作按流序衔接；跨流消费需建立事件/等待。CPU 若读取结果，需要相应完成同步。[nccl-streams][nccl-init]
6. GPU 执行数据移动/归约；跨网路径还可能使用 CPU proxy 驱动网络进度。GPU SM、HBM、PCIe/NIC 与 CPU 都可能成为共享资源，不能说“通信完全免费地在独立引擎运行”。tag 内 proxy.cc 证实 CPU proxy 实现存在；具体路径是否启用须看日志与 profiler。[nccl-ring-code][nccl-proxy-code]

NCCL 也已有 device-side API。当前官方 guide 说明可在 CUDA kernel 内执行设备发起的通信；LSA（Load/Store Accessible）面向可经内存 load/store 访问的 CUDA P2P peer，GIN（GPU-Initiated Networking）面向网络通信。文档声明 Device API 自 2.28 引入、GIN 自 2.28.7 引入，并对设备/能力做条件限制。它不是把 host ncclAllReduce 原样移进 kernel，也不意味着所有 GPU/NIC 都支持同一 offload 路径。对入书内容，稳妥表述是“host stream API 之外存在受条件限制的 device API”；不在此书写未实测的硬件覆盖表。[nccl-device-guide][nccl-device]

错误有提交错误与异步执行错误两层。ncclCommGetAsyncError 的 success 不能替代 stream completion；文档指出 stream 操作可先入队成功，随后报告异步错误。abort、finalize、destroy 的生命周期各有要求；communicator 出错后，不应继续假定原结果正确。具体恢复策略由框架/服务验证，本次不声称透明重试或容错收缩总能成功。[nccl-init][nccl-api-header]

## 5. oneCCL、旧绑定与 XCCL：按版本解开名字

oneCCL 官方 UXL 仓库本次不是 archived，默认 master-v2。latest GitHub release 2022.1.0 的 release timestamp 是 2026-08-15；不能把 latest API 的返回等同于 Intel 所有 binary distribution 的最新版本。[oneccl-repo][oneccl-release]

本次直接读了该 tag 的 include/oneapi/ccl.h、plugins/legacy/ccl_legacy.cpp 与 deps/libccl 下的 MPI/OFI transport 源码：

- 公开 C API 包含 communicator、count/dtype/op 和 Stream 参数；SYCL 示例把 queue 指针传给 collective。README 明确 C API 使用 plugin architecture，并列 ONECCL_LEGACY、ONECCL_LEGACY_CPU、ONECCL_NULL 等选择。NULL 插件不是性能基准的正常 payload 实现。[oneccl-header][oneccl-v2-example][oneccl-v2-readme][oneccl-plugin-doc]
- legacy 插件把 GPU 路径转到 ccl::allreduce 与 ccl::create_stream；源码要求 in-order SYCL queue，拒绝 out-of-order queue 的用法。stream=null 的 CPU 分支会 event.wait；带 queue 的 CPU buffer 分支还有 queue->wait 与 host_task；blocking 配置可在返回前 queue->wait。不能把所有路径概括为“主机 API 一律非阻塞”。[oneccl-legacy-plugin]
- tag 内确实包含 ATL MPI 与 OFI 实现；legacy env 文档列 CCL_ATL_TRANSPORT=mpi/ofi 及 CCL_ATL_HMEM，并说明 GPU buffer 的实际 HMEM 能力取决于 transport 与系统配置。SYCL/Level Zero 是设备执行/内存层，不与 MPI/OFI 同属一个互斥“后端枚举”。[oneccl-atl-mpi][oneccl-atl-ofi][oneccl-env][oneccl-v2-readme]
- 不把 legacy env 页面默认值当成所有 v2 plugin 的统一默认值；也不把 NVIDIA 对应名称的 error API 当成相同语义的保证。已核验代码路径与未验证 binary 兼容性须分开。
- 错误处理还存在明确的 plugin 边界：2022.1.0 的 src/api.cpp 将捕获的 C++ 异常转换为 onecclPluginException；若 communicator 没有 finalize/abort callback，相应 API 返回 onecclNotImplemented。同步返回码不能单独证明队列中 GPU 工作已经完成；应用仍须处理队列/运行时的异步失败，并验证所选 plugin 的恢复契约。该事实不等于断言每个 legacy 构建都缺这些 callback。[oneccl-api-code][oneccl-legacy-plugin]
- 旧 intel/torch-ccl README 明确 ARCHIVED/DEPRECATED，建议直接使用 PyTorch。PyTorch v2.9.0 文档已有 xccl backend；本次 torch-xpu-ops commit 73a6552c3c122614d2651de2a0c6feb8f81ae613 的 ProcessGroupXCCL 使用 onecclComm_t 和 xccl::onecclAllGather 等接口。该 commit 是演进中的源码证据，不证明所有已发布 PyTorch wheel 已使用相同 ABI。[torch-ccl][torch-v29-doc][torch-xccl-code]
- issue 194761 的 RFC 只作为演进背景；不把提案中的模块边界或命名改动认定为已发布。intel/xccl 请求 404，未核实独立 successor library；未从失败请求推出“不存在任何同名内部/其他项目”。[xccl2-rfc]

入书宜分为常青机制与明确日期的短边栏；不宣称 oneCCL 与 NCCL 因 API 外形接近而可直接互换。

## 6. 算法、协议与拓扑分别决定什么

| 机制 | 发生什么 | 适用判断与边界 |
|---|---|---|
| ring all-reduce | 常见分解为 reduce-scatter，再 all-gather；每阶段 N−1 次邻居交换 | 带宽友好；朴素步数随 N 增长，小消息不一定好 |
| tree / recursive schemes | 层级聚合并分发，或递归交换 | 常能减少延迟轮数；具体字节量、root 负载与均衡依算法而变 |
| hierarchical | 先局部组，再跨组，再局部分发/拼接 | 利用节点内外带宽差；NIC 对齐、组形状决定关键路径 |
| pairwise all-to-all | 每轮交换不同目标块；常见成对轮换 | 与 EP 路由相符；目的地偏斜、incast 与最慢接收端支配尾部 |
| chunking / pipelining | 大 tensor 分块，不同块在不同链路/阶段重叠 | 额外 launch、同步、缓冲区与小块效率需权衡 |
| channels / protocols | channel 提供并行通信路径；LL/LL128/Simple 改变低层搬运与同步方式 | protocol 不是 ring/tree 算法，也不是 Ethernet/IB 物理层 |
| hardware collective offload | 交换侧 multicast/reduction 或支持的其他卸载路径减少端点中转 | 需要明确硬件、op/dtype、注册/地址与版本条件；点到点 ring 界不能直接套用 |

MPI 定义语义，不规定一定 ring；NCCL 也按代价模型选择，oneCCL likewise 有多种实现路径。表中步骤/复杂度是解释机制的抽象，不是测得的通信时间。[mpi50-pdf][nccl-ring-code][nccl-cost-model][oneccl-env]

[ILLUSTRATIVE][DERIVED] [ANALYTICAL] 在等块、平衡、无 offload 的点到点 ring 中，T ≈ 2(N−1)α + [2(N−1)M/N]/B_send。小 M 时 α、kernel launch 和进度支配；大 M 时有效 B 更重要。不能只按峰值带宽判定 ring 总胜 tree。hierarchical、递归算法或 offload 可改变步骤与瓶颈，不能机械沿用同一 α 和字节项。

NCCL 官方 env guide 的 NVLS/NVLSTree 明确启用 NVLink SHARP offload；其 availability 依赖硬件。nccl-tests PERFORMANCE.md 对其点到点推导明确写了“as long as they use point-to-point operations”。因此 0.54444 s 是指定 ring 的理想字节界，不是对所有 NVSwitch all-reduce 的普适下界。观察到 busbw 超过某个简单 ring 对照值时，应先查 offload/归一化，不立即断言违反物理约束。[nccl-env][nccl-performance]

同理，重叠不是把通信时间从账上删除。可能使用 GPU SM、HBM、L2、PCIe、NIC、CPU proxy；在独立运行时更快的通信 kernel，可能因争用让并发 GEMM 更慢。公平评价应报告 exposed communication、计算减速与最终 step/ITL/goodput，而不是只报告 overlap 百分比。

## 7. 单位与方向：独立复核冻结回归

术语约定：

- logical bytes M：输入/结果的语义大小；all-gather 与 reduce-scatter 要注明是本 rank fragment 还是完整张量。
- sent bytes S：该 rank 发出的 payload；received bytes R：该 rank 收到的 payload。
- endpoint aggregate S+R：发送与接收相加；对整个系统再求和，会把每次传输在两端各计一次。
- sum-rank sent：全体 rank 发出的 payload 总和；仍不是多跳物理链路实际承载总和。
- algorithm bandwidth：按 benchmark 定义的 logical size/time；并非 NIC byte counter。
- bus bandwidth：对 algbw 乘 collective-specific factor 的归一化指标；并非逐链路测量。
- directional bandwidth：一个方向的容量；bidirectional aggregate：同时发送和接收容量之和，不能拿来除单向字节。
- link bandwidth：指定 link/port 容量；per-GPU port aggregate：一个 GPU 多端口总量；bisection bandwidth：选定拓扑切分的可用跨切面容量。三者不是同一分母。

nccl-tests 定义 algbw=M/t，all-reduce 的 busbw=algbw×2(N−1)/N；其 all-gather 和 reduce-scatter 的 size 约定以完整数组为基准，分别对应 NCCL sendcount×dtype_bytes×N 与 recvcount×dtype_bytes×N。[nccl-performance]

独立按 ring 步骤计数：每阶段发送 N−1 块，每块 M/N；两阶段所以 S=2(N−1)M/N，R=S。在 N=8、M=140 decimal GB 时：

| 量 | 结果 | 口径 |
|---|---|---|
| 逻辑输入 | 140 GB/rank | 不是总网络流量 |
| reduce-scatter 发送 | 122.5 GB/rank | 接收另计同量 |
| all-gather 发送 | 122.5 GB/rank | 接收另计同量 |
| 两阶段发送 / 接收 | 各 245 GB/rank | 不把两者混成 245 GB |
| 单 rank 端点总计 | 490 GB | send+receive |
| 全体 rank 发送总计 | 1,960 GB | 接收总计另为 1,960 GB |
| 理想字节时间 | 245/450 = 490/900 = 0.54444 s | 不含 latency、归约、争用与协议损耗 |

数据手册正文确认 900 GB/s 是总双向，表格列 SXM 80 GB 与该 NVLink 标称值；不适用于任意 H100 PCIe 型号。[h100-datasheet] 对一方向 140 GB 单次传输则为 140/450=0.31111 s。冻结稿的 0.16 s 与 0.27 s 都混用了方向；其中 ring 值应约 0.54 s。

连带项：若仍保留假定单向有效 40 GB/s 和 2.5 GB/s，ring 的 6.125 s 与 98 s 不变；相对理想 450 GB/s 的倍率变为 11.25× 与 180×，不是 22× / 350×。只有真的重复 100 次完整 140 GB all-reduce 才能把 0.54444 s 乘成 54.444 s；把一个梯度拆成 100 buckets 不等于复制 100 次完整梯度。Chapter 10 的 280 GB FP32 梯度若使用相同 ring，其发送 490 GB，NVLink 理想字节项为 490/450=1.08889 s，不是 490/900≈0.54 s。以上均由脚本复核。[nccl-performance]

位置边界：物理 141/印刷 123 是冻结回归主锚；Chapter 10 物理 152/印刷 134 为相关分母。Fig 9.1 的源 caption 确实混用 NVLink 双向和网络单向数字，但本任务没有逐像素检查该图，也未修改它；父代理需在重绘与整书重建后验证图片和相关倍率一起闭合。可变 chapter-09 早段已出现部分修正，后面的 Option A 仍残留旧式；不能据部分源码修正宣布 PDF 闭环。

## 8. LLM 中实际通信的对象

共同原则：选择正确的 group、元素精度、tensor layout、调用次数与时间尺度。DP×TP×PP×EP 的群体不是整机/全舰队统一 N。[megatron-mappings][megatron-layers][torch-fsdp]

| 场景 | 常见对象/操作 | 不应套用的模型 |
|---|---|---|
| 普通 TP decode | 层内 activation partial results；all-reduce 或 reduce-scatter/all-gather | 每个 token 重新 all-gather 全部权重 |
| DP training | gradient buckets；all-reduce，可能积累后才同步 | inference replicas 也做梯度同步 |
| FSDP/ZeRO-style sharding | 按具体策略 gather 参数、reduce-scatter 梯度、分片 optimizer states | 每种 ZeRO stage 都搬运同一状态，或一次 gather 整模型 |
| EP | routed token activations dispatch 与 expert outputs combine；all-to-all/变长或专用 kernel | 所有 rank 都必有完全均衡的固定 count |
| PP | stage 边界 activation forward；training backward 还有 gradient P2P | 所有 stage 每层做全组 all-reduce |
| P/D KV transfer | 选定请求/块的 KV ownership 或布局转移 | 一定是 collective，或每 decode step 发送整份 KV |
| independent inference replicas | 请求被路由到一个 replica，组内可能 TP | 跨所有服务副本建立每 token 梯度 communicator |

Megatron 的 RowParallelLinear 和映射函数为 TP activation reduction 提供实现锚；FSDP v2.9.0 的 fully_shard docstring 解释 all-gather 参数与 reduce-scatter 梯度；DeepEP README 描述 dispatch/combine 及专用优化，但其速度数字不在此作为独立比较证据。[megatron-layers][megatron-mappings][torch-fsdp][deepep]

### 8.1 小型 TP 算例

[ILLUSTRATIVE][ASSUMPTION] [ANALYTICAL] 16 条活跃 decode 序列，各在此 step 处理 1 token，hidden=8192，通信 BF16=2 B，TP=8。约定每 block 两个 row-parallel 输出使用 all-reduce，80 blocks；不使用 sequence parallel、压缩、fused alternative 或 offload。

单次逻辑张量 M=16×8192×2=262,144 B=256 KiB。ring 每 rank 发 448 KiB，另收 448 KiB。160 次调用使每 rank 每 decode step 发 70 MiB，另收 70 MiB。按理想单向 450 GB/s，只有 0.16311 ms 的字节项；按假定单向 25 GB/s 为 2.93601 ms。这不是 ITL 预测：朴素 ring 还有 160×14=2,240 个串行步的 α 项，此外有 launch、计算依赖、争用和调度。小消息的 latency 与进度因此可能比带宽更重要。

B 是本次 step 的 token 行数，不是全部历史 context tokens。prefill 的 token 行数可能大很多；实际 CP/SP/TP layout 可改变 collective 和 tensor shape。该算例不是全书 70B 模型的独立实测。

### 8.2 EP 与 FSDP 的对照

[ILLUSTRATIVE][ASSUMPTION] [ANALYTICAL] 8 EP ranks，每 rank 本地产生 256 tokens，top-2，hidden=8192，BF16；假设路由均匀，每条 expert route 独立发一完整 activation row。每 rank 的 route 数据共 8 MiB，7/8 去远端，dispatch 发/收各 7 MiB。若 combine 每 route 返回同样大小，dispatch+combine 发/收各 14 MiB。metadata、alignment、padding、量化、去重、capacity/drop、热点均未计；真实 EP 的最忙 rank 与跨节点 cut 才决定尾部。[deepep]

[ILLUSTRATIVE][ASSUMPTION] [ANALYTICAL] 一个完整参数 unit=64 MiB，8-way 分片，ring all-gather 每 rank 发/收各 56 MiB；完整梯度同为 64 MiB 时，等分 reduce-scatter 也各 56 MiB。调用单位是 sharded module/bucket，不必整模型。optimizer state 是否移动取决于实际策略，不应把 optimizer state all-gather 说成每次 forward 的普遍动作。[torch-fsdp][nccl-performance]

## 9. 只保留有教学价值的替代实现

- RCCL：AMD ROCm/HIP 生态，README 声明支持 GPU collectives、PCIe/xGMI、verbs/TCP 路径。这里仅用它证明“相同语义，不同设备栈”；不把 develop 分支里的新 offload 能力扩展为所有已发布 ROCm 的特性。[rccl]
- Gloo：框架 backend 与库的同名实例。官方 README 描述 CPU/GPU 算法，但不能据此推导 PyTorch 某版 Gloo backend 暴露每一项 GPU 能力。PyTorch v2.9.0 的推荐和操作矩阵应单独核对。[gloo][torch-v29-doc]
- UCC：可以服务不同 programming models，声明可选 CUDA/HIP 支持，文档含 Open MPI 集成。它说明“MPI 实现与集合库可组合”，而非竞争产品只能二选一。[ucc]
- DeepEP：针对 EP dispatch/combine 的专用通信实现，提醒框架未必始终走通用 ProcessGroup all-to-all；不扩展成全种类集合库目录。[deepep]

## 10. 运维与公平评价协议

下面是待执行的验证方案，不是已执行测试结果。库版本、接口相同或单机 smoke test 通过，都不构成生产可互换性证明。

### 10.1 固定比较契约

分两层比较：同硬件上不同可用实现，研究软件路径差异；不同厂商平台比较，研究整个部署方案，不宣称隔离出了“库本身”的效应。记录 accelerator SKU、HBM、驱动、CUDA/ROCm/SYCL/Level Zero、库版本/构建、framework backend、network plugin/provider、NIC/firmware、rail 数、switch、link rate、CPU/NUMA affinity、rank→GPU→NIC 映射、group population、buffer dtype/count/layout、op、in-place、graph capture、registration、算法/协议及环境变量。[nccl-env][nccl-troubleshoot][oneccl-env][mpich-v502]

### 10.2 先正确性，再速度

使用能由 CPU 精确得到结果的小整数输入，验证 SUM/root/拼接顺序/partition/all-to-all source-destination。覆盖零 count、非整齐 sizes、不同 roots、in-place、每种 dtype/op 的支持；不支持的组合明确记 unsupported，不静默换 dtype。浮点分别报告 tolerance-based error 和固定环境重复运行的 bitwise 比较，再改变 rank mapping、算法、版本观察结果，不承诺所有组合相同。确保输入缓冲区已由 producer 完成，结果在消费者使用前满足设备完成依赖。[mpi50-pdf][nccl-streams][oneccl-legacy-plugin]

### 10.3 微基准与计时

NVIDIA 用 nccl-tests；oneCCL 使用该 tag 公开 examples/tests 与正确的非 NULL 插件；MPI 使用已核实支持该 GPU buffer 的 OSU/MPI collective tests。固定相同 tensor/group/精度和计时边界，分别报告 host enqueue 与 device-completed latency。tiny activation sizes 与大 gradient buckets 都要覆盖，不只测 100 MB–1 GB。先验证每 rank 最大 allocation+workspace 是否可驻留；禁止在 80 GB H100 上安排 140 GB 单缓冲区 benchmark。[nccl-tests-readme][oneccl-v2-example][openmpi-cuda]

记录 warmup、迭代数、重复试验、分位数定义、rank 间最大完成时间与波动。若 profiler/同步改变执行则记录 instrumentation overhead。报告原始 t、logical bytes、S/R 口径、algbw、busbw 与公式；再用 NIC/link counters 验证实际路径，不能把 busbw 当 wire counter。[nccl-performance]

### 10.4 定位路径与争用

检查拓扑与 transport 日志：NCCL_DEBUG、GRAPH/COLL/NET 等范围，MPI component/provider 配置，oneCCL plugin/transport。结合 GPU/CPU profiler、NIC counters 与 trace，区分网络 stall、HBM 争用、CPU proxy 饿死、错误 NIC/NUMA 与 rank 失衡。[torch-v29-doc][nccl-proxy-code][oneccl-env] 多 NIC 或多 rail 不代表吞吐自动相加；实际 mapping、上联 oversubscription、路由、congestion 与失败 rail 应分别测试。

在隔离服务和有并发训练/KV transfer/检索流量的服务上重放同一到达过程。测 prefill/TP decode 的关键路径、p95/p99 TTFT/ITL、队列、错误率与 SLO-goodput。通信耗时总和不是 exposed stall；跨 rank 尾部也不是均值。空闲 fabric 上更高 busbw 不自动推出更少 serving hosts。

### 10.5 失败、死锁与恢复

在隔离测试环境注入缺 rank、collective/op/count 不匹配、顺序不一致、网络中断与进程退出。校验 framework watchdog、library async error、应用 deadline 的关系，保证请求有限时失败而非永久挂起。跨 communicator 的依赖也可能成环；barrier 不是修复错误顺序的工具。[mpi50-pdf][nccl-init][torch-v29-doc] 由服务策略隔离并重建受影响的 group；不默认在错误 communicator 上重试，也不宣称 MPI/NCCL/oneCCL 都提供透明容错。

## 11. 未闭合项与父代理集成契约

已完成：一手源抓取；release/status 与命名拆分；关键源码路径检查；冻结算例的独立推导；7 项 CPU 语义/算术/逐轮 ring 测试；完整英文候选、精确锚点与跨章 map；机器可读 claim/source ledger；2 张原始机制图的可编辑 SVG、矢量 PDF、300 dpi PNG、灰度及实际宽度预览，并已实际调用 vision 工具检查整图与细节、进行二次自批判复核。

未完成且不应伪装完成：任何 accelerator library 的实际执行；跨平台性能比较；逐型号 device-API/offload 覆盖认证；oneCCL v2 对每个 binary wheel 的 ABI/plugin/default-path 验证；所有 MPI persistent/GPU datatype 组合的实测；候选图嵌入后的全书版面审校；父代理修复后的重建与发行认证。

建议集成顺序：先由父代理统一 Chapter 9 的方向与内存人口；再在 §1/§2 加常青语义、层次图与 MPI 公平比较；将现行库状态放入显式“2026-10-28 post-cutoff research snapshot”边栏或新版受控更新，不改变旧 edition 的截止口径。Chapter 10 的 TP/DP 分母及调用人口随后统一；Chapter 11/14/15/17/20 只加短交叉引用与真实 workload 的观测契约。精确锚与候选文本见 proposed-insertions.md。其他代理的 Intel XPU/量化/模型趋势等任务保持原 ownership，不在此抢改。
