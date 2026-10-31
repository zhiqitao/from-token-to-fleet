# 图表审计 Pass E — R27 冻结 PDF 逐图记录（figure-audit）

对象：`review/publication_v2_20261028/work/accelerated_external_review_proof_r27/render/build/from-token-to-fleet-v20260913.pdf`（425 页，只读，未改动 manuscript/style/generator）。
方法：pymupdf 提取每图几何/字号/图注 → 140 dpi 按实体印刷尺寸渲染整页与图区 → 2×2 接触表（15 张，全部 57 图，印刷尺寸视觉检查）→ 20 张 280 dpi 局部放大复核疑似缺陷。像素级灰度碰撞、栅格图字号（用 Fig 20.1 已知 8.6pt 标定）为程序测量，见 `figure-method.md`。
覆盖标记：**S**=接触表（印刷尺寸）；**Z**=接触表+放大复核。57 图全部 S，20 图 Z，无 INCOMPLETE。
计数核对：List of Figures 共 **57 个编号图**（前置 1、2 + 正文 50 + 附录 A.1–A.5）；父任务所称 58 = 57 编号图 + 封面 Figure 元素（结构树 58 个 Figure/Alt）。58/58 均有 Alt，本审计覆盖全部 57 个编号图。
严重度：P0 科学错误/误导（**本轮 0 个**）｜P1 必须修（<8pt、图注缺 takeaway/状态/caveat）｜P2 应修（箭头不达目标、标签-目标错配、碰撞、跨图图例冲突、灰度塌缩）｜P3 打磨。

---

## 第 1 章

**Fig 1.1** | PDF p27 / 印刷 p7 | Z | 栅格图（422dpi）
- 主张：每个解码步为每层每头追加一对 K/V，下一步 attention 读取。
- 科学：✓（per-layer/per-head 标注齐全；写后读逻辑正确）。箭头方向：✓ 8 条箭头全部正确（放大复核否证了"重复箭头"初判）。标签语义：✓。
- 轴/单位：N/A（流程图）。字号：栅格，实测最小字高标定 ≈9.1pt ✓（估测法，见 method）。
- 对比/灰度：橙/紫/灰四类框与灰/绿箭头为**仅靠颜色**区分，灰度下塌缩（P3）。留白/重叠/碰撞：无重叠；"store V" 标签与竖直连线**近贴**（未压字）。
- 箭头触达：✓ 全部贴目标边。图注：takeaway ✓ / 状态 [ILLUSTRATIVE conceptual] ✓ / caveat ✓（"concept; arithmetic in Ch.7"）。
- 来源状态：ILLUSTRATIVE conceptual。印刷可读：✓（框文字 9–11pt 级）。
- 严重度：P3。修改：灰度安全化——写/读路径改用线型（实线/虚线）区分，勿仅靠灰绿。

**Fig 1.2** | PDF p28 / 印刷 p8 | S | 栅格图（521dpi）
- 主张：text→tokenizer→IDs→embedding→attention→KV cache 的单趟抽象。
- 科学：✓（图注已声明 one-pass 抽象、K/V 在每层产生）。箭头方向：✓ 6 箭头均触目标。标签语义：✓。
- 轴/单位：N/A。字号：栅格最小字高标定 ≈**8.0pt**（全书栅格图最低，临界 ✓）。
- 对比/灰度：绿/青/橙/紫四色框 + 绿读箭头在灰度下塌缩（P3）。重叠/碰撞：无。
- 箭头触达：✓。图注：takeaway ✓ / 状态 ✓ / caveat ✓（1052 字符，9 句）。来源状态：ILLUSTRATIVE conceptual。
- 印刷可读：✓ 但副标签最小。严重度：P3。修改：副标签放大到 ≥9pt 或加深；灰度加线型冗余。

## 第 2 章

**Fig 2.1** | PDF p35 / 印刷 p15 | S | 矢量
- 主张：PREFILL 一遍填充持久 KV cache，DECODE 逐 token 读/写循环。
- 科学：✓（图注明确 TTFT≠prefill 延迟）；**观察**：PREFILL 泳道画成 "token + position" 单 token 形态，与"整段 prompt 一遍"的图注表述有概念落差（图内有 "conceptual per-step" 斜体注）→ P3。
- 箭头方向：✓（populate/read/append/initialize/loop 全对且触目标）。标签语义：✓。轴/单位：N/A。
- 字号：min **8.0pt** ✓（零余量）。对比/灰度：绿 initialize 箭与灰 loop 箭灰度同灰（P3，有位置冗余）。
- 重叠/碰撞：无。图注：takeaway ✓ / 状态 ✓ / caveat ✓。来源状态：ILLUSTRATIVE conceptual。印刷可读：✓。
- 严重度：P3。修改：PREFILL 泳道画成整段 prompt 条带（或加 "whole prompt, one pass" 微标）。

**Fig 2.2** | PDF p43 / 印刷 p23 | Z | 矢量（log-log roofline）
- 主张：decode 落在 memory-bound 侧、prefill 落在 compute-bound 侧，ridge ≈295 FLOP/byte。
- 科学：✓（1e15/3.4e12≈295；decode≈1、prefill≈1e4 强度自洽；"markers = regime, not measured MFU" 已声明）。
- 箭头方向：N/A（图）。标签语义：✓。轴/单位：✓ 双轴 log、FLOP/s 与 FLOP/byte 均标注。
- 字号：min 8.0pt ✓（灰斜体注释框文字对比度偏低 → P3）。
- **碰撞：白色注释框压在黑色 roofline 斜线上（x≈30–80 处线被遮断），框右缘贴近红色 ridge 虚线 → P2**。
- 留白：✓。灰度：两区域靠斜/横影线区分 ✓，红点/蓝三角靠形状 ✓。
- 箭头触达：N/A。图注：takeaway ✓ / 状态 ✓ / caveat ✓。来源状态：（无括号标签，正文含 "operating points" 声明）。
- 印刷可读：✓。严重度：**P2**。修改：注释框移到左下空白或加白底+细边并让开斜线；框文字改深灰。

## 第 3 章

**Fig 3.1** | PDF p51 / 印刷 p31 | S | 矢量，与正文同页（11 行正文，无重叠）
- 主张：前向 q（右向）与学习的反向 pθ（左向）在连续噪声与 MASK 两条道上对照。
- 科学：✓（mask 位置一致；图注声明"非所有扩散模型定义、非测量"）。箭头方向：✓ 双向正确且触目标。标签语义：✓（M=MASK、illustrative token IDs）。
- 轴/单位：N/A（示意条）。字号：min 10.1pt ✓。灰度：黑/橙箭头另有方向冗余 ✓。重叠/碰撞：无。
- 图注：takeaway ✓ / 状态（"Conceptual drawing, not a measurement"）✓ / caveat ✓。来源状态：概念图，无括号标签（散文状态）。
- 印刷可读：✓。严重度：P3。修改：可不改；如统一风格可补 [ILLUSTRATIVE conceptual]。

**Fig 3.2** | PDF p53 / 印刷 p33 | S | 矢量
- 主张：自回归前缀 / 全画布掩码 / 块因果三种采样的提交顺序与复用状态不同。
- 科学：✓（A 下划线增长、B 非连续接受、C 活动块重算均正确；图注"not a timing diagram"）。箭头方向：✓（左→右推进 + 橙色 repeat 自环触目标）。标签语义：✓（图例齐全）。
- 轴/单位：N/A。字号：min 10.1pt ✓。灰度：虚线/影线冗余 ✓。重叠/碰撞：无。图注：takeaway ✓ / 状态 ✓ / caveat ✓。
- 来源状态：散文状态。印刷可读：✓。严重度：P3（无缺陷）。修改：无。

**Fig 3.3** | PDF p62 / 印刷 p42 | S | 栅格（350dpi，同页 15 行正文，无重叠）
- 主张：Wan2.2 A14B 随去噪调度切换两个常驻专家，仅选中者参与一次前向。
- 科学：✓（2×≈14B≈27B 常驻、14B 激活，与 A14B 命名一致；图注"not a memory measurement"）。箭头方向：✓（高噪→低噪，虚线箭头触目标）。标签语义：✓（"stage widths do not encode step counts"）。
- 轴/单位：N/A。字号：栅格标定 ≈9.0pt ✓。灰度：蓝虚线/橙框/黑箭头有线型冗余 ✓。重叠/碰撞：无。
- 图注：takeaway ✓ / 状态（"Mechanism schematic, not a memory measurement"）✓ / caveat ✓。来源状态：散文状态。
- 印刷可读：✓。严重度：P3。修改：无。

**Fig 3.4** | PDF p66 / 印刷 p46 | S | 矢量
- 主张：同注意力几何下 70B dense 与 8 专家 MoE 的 KV 相同，激活参数 70B vs ≈14B 不同。
- 科学：✓（70B×2B=140GB、14B×2B≈28GB；条件"same attention geometry/context/dtype"已写明）。箭头：N/A（并排网格）。标签语义：✓。
- 轴/单位：N/A。字号：min 8.4pt ✓。灰度：蓝/橙 active 色块与红标题在灰度接近（P3，有图例/位置冗余）。
- 重叠/碰撞：无（红框网格完整）。图注：takeaway ✓ / 状态 ✓ / caveat ✓。来源状态：DERIVED, ILLUSTRATIVE。
- 印刷可读：✓（斜体 "controlled:" 行最紧）。严重度：P3。修改：active 色块加影线冗余。

## 第 4 章

**Fig 4.1** | PDF p89 / 印刷 p69 | S | 矢量
- 主张：六个工作负载维度各自约束对应的架构决策。
- 科学：✓（图注已声明"启发式影响、非一一映射、非排他"）。箭头方向：✓ 6 条虚线左→右，箭头触橙框左边。标签语义：✓。
- 轴/单位：N/A。字号：min 9.2pt ✓。灰度：蓝/橙两列色塌缩为两级灰（P3，有列位冗余）。
- 重叠/碰撞：无；"KV cache size & prefill demand" 贴右框边（未截断，P3）。图注：takeaway ✓ / 状态 ✓ / caveat ✓。
- 来源状态：ILLUSTRATIVE conceptual。印刷可读：✓。严重度：P3。修改：右列文字内边距 +2pt。

## 第 5 章

**Fig 5.1** | PDF p104 / 印刷 p84 | S | 矢量
- 主张：工作负载 → 五个选型面 → 检索/生成两腿 → 系统决策。
- 科学：✓（图注明确"选型图，非评估流水线"，评估门在 §5.4）。箭头方向：✓ drives/split/context/answer 全对且触目标。标签语义：✓。
- 轴/单位：N/A。字号：min 8.0pt ✓。灰度：四色粉彩填充塌缩为近同浅灰（P3，有边框/文字冗余）。
- 重叠/碰撞：无。图注：takeaway ✓ / 状态 ✓ / caveat ✓。来源状态：ILLUSTRATIVE conceptual。印刷可读：✓。
- 严重度：P3。修改：粉彩填充改不同边框线型。

## 第 6 章

**Fig 6.1** | PDF p107 / 印刷 p87 | S | 矢量
- 主张：三层指标构成诊断链——因果向下、诊断向上。
- 科学：✓。箭头方向：✓ 左绿实线向下、右红虚线向上，箭头/起点圆点触框边。标签语义：✓（旋转 causation/diagnosis + 底部图例）。
- 轴/单位：N/A。字号：min 8.4pt ✓。灰度：绿/红箭头灰度为中灰/深灰，靠方向+线型可分（P3）。
- 重叠/碰撞：无。图注：takeaway ✓ / 状态 [ILLUSTRATIVE conceptual] ✓ / caveat ✓。来源状态：ILLUSTRATIVE conceptual。
- 印刷可读：✓。严重度：P3。修改：无。

**Fig 6.2** | PDF p109 / 印刷 p89 | Z | 矢量（合成延迟直方图）
- 主张：均值/p99 看起来正常，仍有 1% ≈5s 长尾击穿 2s SLO。
- 科学：**△**——分位线与柱质量自洽（mode 0.7 < p50 0.8 < mean 0.85 < p99 1.33 ✓）；但**粉色 straggler 带从 4s 起，2–4s 同样违反 SLO 的区间未着色**，读者易把带读成"违规区"（图内文字写的是 "1% stragglers ~5s"，语义可辩护但不完整）→ P2。
- 箭头方向：N/A。标签语义：✓（放大复核否证"标签压柱"与"标签过小"初判：标签在柱上方空白、错落排布）。
- 轴/单位：✓ Request latency (s) / Request count。字号：min 8.5pt ✓。
- 碰撞：图例框右缘**轻微压到粉带**（P3）。灰度：蓝柱/绿线同灰、粉带近白（P3，有线型/位置冗余）。
- 图注：**仅标题 86 字符——无 takeaway 句、无状态标签、无 caveat → P1**。
- 来源状态：图内标题含 [ILLUSTRATIVE synthetic profile]，图注缺失。印刷可读：✓。
- 严重度：**P1（图注）+ P2（带语义）**。修改：①图注补一句 takeaway + [ILLUSTRATIVE synthetic] + "band marks ≥4s tail, not the full SLO-violating region"；②粉带左缘移到 2s SLO 线或加 "≥4s" 标注。

## 第 7 章

**Fig 7.1** | PDF p122 / 印刷 p102 | S | 矢量，同页 13 行正文（无重叠）
- 主张：GQA 中 8 个 query 头共享 1 个 K/V 头，per-token KV 降 ≈8×。
- 科学：✓（n_q:n_kv=8:1 扇入与图一致；算术指向正文）。箭头：N/A（无向连线，扇入线不穿字）。标签语义：✓。
- 轴/单位：N/A。字号：min 8.2pt ✓。灰度：蓝 query / 橙 K-V 仅颜色区分（P3，有文字冗余）。
- 重叠/碰撞：无。图注：takeaway ✓ / 状态 ✓ / caveat ✓（"head glyphs schematic"）。来源状态：DERIVED, ILLUSTRATIVE。
- 印刷可读：✓。严重度：P3。修改：无。

**Fig 7.2** | PDF p124 / 印刷 p104 | S | 矢量
- 主张：循环层保持定长状态，全注意力层保持增长的 KV 历史。
- 科学：✓（图注声明 recurrent 快照是相继的、非联合保留；Qwen3.8-27B 配置背书、非实测比）。箭头方向：✓ 肘形箭头触目标。标签语义：✓。
- 轴/单位：N/A。字号：min 9.4pt ✓。灰度：蓝/红塌缩为浅/中灰（P3，有 compute/store 文字冗余）。
- 重叠/碰撞：无。图注：takeaway ✓ / 状态 ✓ / caveat ✓。来源状态：散文状态（configuration-backed, not measured）。
- 印刷可读：✓。严重度：P3。修改：无。

**Fig 7.3** | PDF p128 / 印刷 p108 | S | 栅格（600dpi）
- 主张：量化选型只产出打包张量，实际执行取决于是否有兼容 kernel。
- 科学：✓（"repacking ≠ numerical conversion"、三条 dispatch 路径正确；图注"not an accuracy/throughput comparison"）。箭头方向：✓ 触目标。标签语义：✓。
- 轴/单位：N/A。字号：栅格标定 ≈8.9pt ✓。灰度：全黑白，无塌缩 ✓。
- 重叠/碰撞：无（高容器内略挤，P3）。图注：takeaway ✓ / 状态 ✓ / caveat ✓。来源状态：散文状态。
- 印刷可读：✓。严重度：P3。修改：无。

**Fig 7.4** | PDF p130 / 印刷 p110 | S | 栅格（600dpi）
- 主张：同样 32 个 E2M1 值，MXFP4 17B（4.25 bit/值）vs NVFP4 18B（4.5 bit/值）。
- 科学：✓（16B+1B=17、16B+2B=18、FP32 per-tensor=4B；"not a physical packing order" 已声明）。箭头：N/A。标签语义：✓。
- 轴/单位：无轴，单位写在标签（B、bit/value）✓。字号：栅格标定 ≈9.4pt ✓。灰度：黑白影线 ✓。
- 重叠/碰撞：无。图注：takeaway ✓ / 状态 ✓ / caveat ✓。来源状态：散文状态（derived storage accounting）。
- 印刷可读：✓。严重度：P3。修改：无。

**Fig 7.5** | PDF p137 / 印刷 p117 | Z | 矢量（log-log）
- 主张：KV 随上下文线性增长，GQA 较 full-MHA 省 ≈8×；参数量不决定 KV。
- 科学：✓（2.62MB/tok×9.5K=24.9GB ✓；128K≈335GB vs 436GB 预算 ✓；FP8 为字节减半非实测已声明）。
- **标签-目标错配：注释 "9.5K ≈ 24.9 GB" 的箭头落在 x=10K 的数据标记上（数据点在 1/3/10/32/128K），9.5K 无标记 → P2**。
- 箭头方向：✓（唯一箭头方向对）。标签语义：✓。轴/单位：✓ 双 log、GB 与 K tokens 标注。
- 字号：min 8.5pt ✓（底部灰色脚注最小、对比偏低 → P3）。
- 碰撞：右侧注释的细引线**穿过蓝色 GQA-FP16 曲线**（P3）。灰度：四系列靠 ○□▲▼ 形状区分 ✓。
- 图注：takeaway ✓ / 状态 ✓ / caveat ✓。来源状态：DERIVED, ILLUSTRATIVE。印刷可读：✓。
- 严重度：**P2**。修改：把注释改为 "10K ≈ 26.2 GB"，或在 9.5K 处补一个标记并让箭头指向它；引线改走空白区。

**Fig 7.6** | PDF p138 / 印刷 p118 | S | 矢量（条形图）
- 主张：同一 70B：推理 ≈165GB、全量微调 ≈1120GB、QLoRA ≈50–70GB。
- 科学：✓（16B/param×70B=1120GB；1120>640、60<80 成立；副标题声明列间非单变量对比）。箭头方向：✓（QLoRA 箭触 1×H100 线）。标签语义：✓。
- 轴/单位：✓ GPU memory floor (GB) 0–1400；X 类目。字号：min 8.2pt ✓（4 行脚注最小）。
- 灰度：三参考线用不同线型 ✓。重叠/碰撞：无。图注：takeaway ✓ / 状态 ✓ / caveat ✓。
- 来源状态：DERIVED, ILLUSTRATIVE。印刷可读：✓。严重度：P3。修改：无。

**Fig 7.7** | PDF p139 / 印刷 p119 | S | 矢量（100% 堆叠条）
- 主张：640GB 池 = 140 权重 + 64 运行时 + 436 KV → 436/24.9≈17.5 → ~17 并发。
- 科学：✓（140+64+436=640；436/24.9=17.51；图注含 aggregate-feasibility 与 per-rank TP=8 分片 caveat，1830 字符）。
- 箭头：N/A（公式内 →）。标签语义：✓。轴/单位：无轴，段内 GB 单位 ✓。字号：min 8.5pt ✓。
- 灰度：三段用斜线/实心/竖条纹区分 ✓。重叠/碰撞：无。图注：takeaway ✓ / 状态 ✓ / caveat ✓（超长，10 句）。
- 来源状态：DERIVED, ILLUSTRATIVE。印刷可读：✓。严重度：P3。修改：图注过长可拆分，非缺陷。

**Fig 7.8** | PDF p140 / 印刷 p120 | S | 矢量（Memory Tetris）
- 主张：上下文增长只推高 KV，9.5K/32K/128K → 229/288/539GB，均在 640GB 下。
- 科学：✓（204+24.9/84/335=229/288/539；539<640；图注声明 aggregate 可行性 caveat）。
- 箭头：N/A。标签语义：✓。轴/单位：无轴，"bar heights to scale (GB)" + 80GB 参考线 ✓。
- 字号：min 8.2pt ✓（9.5K 段标签最紧）。
- **灰度：runtime（绿斜影线）与 weights（蓝斜影线）在灰度下成为同款灰斜线，仅靠段内文字区分 → P2**。
- 重叠/碰撞：无（"KV 335 GB" 在红线下沿，未压）。图注：takeaway ✓ / 状态 ✓ / caveat ✓。
- 来源状态：DERIVED, ILLUSTRATIVE。印刷可读：✓。严重度：**P2**。修改：weights 段改横影线或点纹，与 runtime 斜影线区分。

## 第 8 章

**Fig 8.1** | PDF p146 / 印刷 p126 | S | 矢量
- 主张：计算与数据搬运分居存储层级不同层，容量↑速度↓距离↑。
- 科学：✓（权重+KV→HBM、TP/PP→互连、P/D KV→远端映射正确）。箭头方向：✓（"what runs here →" 右向；红色双向梯度箭头为坐标轴式，非流程，可接受）。标签语义：✓。
- 轴/单位：N/A。字号：min 10.0pt ✓。灰度：蓝/橙/绿三层色塌缩（P3，有行名冗余）。
- 重叠/碰撞：无。图注：takeaway ✓ / 状态 ✓ / caveat ✓。来源状态：ILLUSTRATIVE conceptual。印刷可读：✓。
- 严重度：P3。修改：无。

**Fig 8.2** | PDF p152 / 印刷 p132 | S | 矢量（roofline H100 vs H200）
- 主张：H200 带宽更高 → ridge 更低（≈206 vs ≈295），共享 989 TFLOPS 顶。
- 科学：✓（989/3.35≈295、989/4.8≈206；FMA=2 FLOPs、peak datasheet、非实测 MFU 均在图注声明）。
- 箭头方向：✓（memory-bound 斜率小箭头）。标签语义：✓（PER GPU、ANALYTICAL (DERIVED)）。
- 轴/单位：✓ 双 log，TFLOPS per GPU / FLOP per byte per GPU。字号：min 8.0pt ✓（零余量）。
- 灰度：实线+圆 vs 虚线+三角 ✓。重叠/碰撞：无（ridge 标注贴近曲线但未压）。
- 图注：takeaway ✓ / 状态（散文 "peak/theoretical, not achieved"）✓ / caveat ✓。来源状态：散文状态。
- 印刷可读：✓。严重度：P3。修改：无。

**Fig 8.3** | PDF p157 / 印刷 p137 | S | 栅格（350dpi）
- 主张：Wan2.2 TI2V-5B 整段去噪：31×44×80×48 → 27,280 tokens → 50 步×2 CFG → 121 帧 1280×704@24fps。
- 科学：✓（patch (1,2,2)→31·22·40=27,280；stride (4,16,16)→1+4·30=121、44·16=704、80·16=1280；图注 [1P][FACT] + "Schematic, not a latency"）。箭头方向：✓ 触目标，自环闭合。标签语义：✓（实线=数据、虚线=条件）。
- 轴/单位：N/A。字号：栅格标定 ≈9.3pt ✓。灰度：橙/浅蓝分组仅颜色（P3，有线型冗余）。
- 重叠/碰撞：无。图注：takeaway ✓ / 状态 ✓ / caveat ✓。来源状态：[1P][FACT]。印刷可读：✓。
- 严重度：P3。修改：无。

## 第 9 章

**Fig 9.1** | PDF p166 / 印刷 p146 | S | 矢量（log-log）
- 主张：N=8 ring all-reduce 理想时间随张量线性，NVLink ≫ HDR ≫ RoCE。
- 科学：✓（1.75=2(N−1)/N；140GB→0.544/6.125/98s 与副标题一致；450GB/s 单向、"No curve is measured" 已声明）。
- 箭头：N/A（140GB 参考线无头）。标签语义：✓。轴/单位：✓ Ideal ring completion time (ms) / Logical input tensor per rank (GB)，双 log。
- 字号：min 9.0pt ✓。灰度：三系列靠线型+标记形状 ✓。
- 重叠/碰撞：无；右上 RoCE 100,000ms 标记贴轴顶（可能轻微出界 → P3，建议 ylim 留 5% 余量）。
- 图注：takeaway ✓ / 状态 ✓ / caveat ✓。来源状态：ANALYTICAL, DERIVED, ILLUSTRATIVE。印刷可读：✓。
- 严重度：P3。修改：y 轴上限加余量。

**Fig 9.2** | PDF p167 / 印刷 p147 | S | 矢量
- 主张：四秩 ring：reduce-scatter + all-gather，每秩收发各 12B、合计 24B。
- 科学：✓（和值 10/20/−10/0、6+6B/相位、24B 总计自洽；"no averaging or measured performance" 已声明）。箭头方向：✓ 触目标（含 R3→R0 回边）。
- 标签语义：✓。轴/单位：N/A。字号：min 9.5pt ✓。灰度：橙/蓝/红相位色塌缩（P3，有文字标签）。
- 重叠/碰撞：无。图注：takeaway ✓ / 状态 ✓ / caveat ✓。来源状态：DERIVED, ILLUSTRATIVE。印刷可读：✓。
- 严重度：P3。修改：无。

**Fig 9.3** | PDF p168 / 印刷 p148 | S | 矢量
- 主张：payload 路径（framework→library→runtime→hardware）与 communicator 建链路径分离。
- 科学：✓（图注声明 2026-10-28 实现快照、虚线建链不表示 MPI 承载 payload——该日期与书稿日期一致，非笔误）。箭头方向：✓ 触目标（红色控制虚线跨层是有意）。
- 标签语义：✓（1–4 层编号+图例）。轴/单位：N/A。字号：min 9.5pt ✓。灰度：蓝/橙填充塌缩、红虚线/黑实线靠线型 ✓。
- 重叠/碰撞：无。图注：takeaway ✓ / 状态 ✓ / caveat ✓。来源状态：ILLUSTRATIVE。印刷可读：✓。
- 严重度：P3。修改：无。

## 第 10 章

**Fig 10.1** | PDF p180 / 印刷 p160 | Z | 矢量（三面板）
- 主张：TP 切一层权重、PP 切层栈、DP 切批——通信位置各不同。
- 科学：✓（TP 每层 all-reduce、PP 仅阶段边界、DP 训练同步/推理独立均正确；图注含 "all-reduce 是选项之一，fused kernel 常用 RS+AG" 的限定）。箭头方向：✓ 全部触目标（放大复核）。
- 标签语义：✓；**"idle (bubble)" 位于面板 B 且为灰色注释（初判"红色语义错配"被否证）**。
- **图例-图形不一致：图例 weights/data 画的是带斜影线的色块，图形里 W 条与 batch shard 是实心填充；comms 图例为红虚线框而图形用实线红框 → P2**。
- 轴/单位：N/A。字号：min 8.5pt ✓。
- **灰度：图例中 weights 与 data 两个色块用同一款单斜线影线、仅色相不同 → 灰度下不可分；图形三类浅填充也趋同 → P2**。
- 重叠/碰撞：无。图注：takeaway ✓ / 状态 ✓ / caveat ✓。来源状态：ILLUSTRATIVE conceptual。印刷可读：✓。
- 严重度：**P2**。修改：图例与图形统一（都用影线或都用实心），weights/data 影线方向相反（/ vs \）。

## 第 11 章

**Fig 11.1** | PDF p193 / 印刷 p173 | S | 矢量（Orca 槽位图）
- 主张：连续批处理用释放槽即时回填，消除离散批处理的 idle bubble。
- 科学：✓（图注声明 decode-only 示意）。箭头方向：✓ 触目标（黑色注释箭头轻微跨过上沿，P3）。标签语义：✓。
- 轴/单位：X 轴 "time (decode steps/iterations)" ✓；Y 为无标签槽行（示意，可接受）。
- 字号：min 8.0pt ✓。**灰度：粉影线(idle) 与绿影线(new) 灰度同灰同纹 → 回填/空转不可分 → P2**。
- 重叠/碰撞：无实质。图注：takeaway ✓ / 状态 ✓ / caveat ✓。来源状态：ILLUSTRATIVE conceptual。印刷可读：✓（细条纹在印刷下偏细）。
- 严重度：**P2**。修改：idle 与 new 用不同影线方向或加 ▨/░ 图案差异。

**Fig 11.2** | PDF p197 / 印刷 p177 | S | 矢量，同页 6 行正文（无重叠）
- 主张：serving 是四个正交关注点，不是层叠栈。
- 科学：✓（四机制举例与 §11 一致）。箭头：N/A（无连接线，符合"非栈"意图）。标签语义：✓。
- 轴/单位：N/A。字号：min 9.2pt ✓。灰度：四象限边框色塌缩（P3，有标题文字）。
- 重叠/碰撞：无。图注：takeaway ✓ / 状态 ✓ / caveat ✓。来源状态：ILLUSTRATIVE conceptual。印刷可读：✓。
- 严重度：P3。修改：无。

**Fig 11.3** | PDF p198 / 印刷 p178 | S | 矢量
- 主张：P/D 分离 = prefill 池(FLOPs) + decode 池(HBM) + 一次 KV 传输。
- 科学：✓（35GB@450GB/s≈0.08s vs 1.08s prefill、40GB/s≈0.9s 的不等式在图注给出）。箭头方向：✓ KV TRANSFER prefill→decode、prompt 入、generated tokens 出，均触边。
- 标签语义：✓。轴/单位：N/A。字号：min 8.5pt ✓。灰度：红/蓝边框与橙/蓝 GPU 块塌缩（P3，有文字）。
- 重叠/碰撞：无。图注：takeaway ✓ / 状态 ✓ / caveat ✓。来源状态：DERIVED, ILLUSTRATIVE。印刷可读：✓。
- 严重度：P3。修改：无。

**Fig 11.4** | PDF p202 / 印刷 p182 | S | 矢量
- 主张：可见设备≠可用 serving 路径，整条栈必须过资格门。
- 科学：✓（torch.xpu / hpu / OpenVINO、SYCL+L0、HCCL、"Gaudi≠Intel GPU" 均正确）。箭头方向：✓ 触目标（虚线入资格门）。
- 标签语义：✓ 但**三列窄框内 3 行折行密集，为全书最挤的图**（字号 min 10.1pt，非字号问题而是排布密度）→ P3。
- 轴/单位：N/A。灰度：仅资格门红边为颜色强调，灰度丢失 salience（P3，有 ✗/文字）。
- 重叠/碰撞：无。图注：takeaway ✓ / 状态（"no measured performance data"）✓ / caveat ✓。来源状态：散文状态。
- 印刷可读：✓（≥10pt）。严重度：P3。修改：列宽加宽或每行减字。## 第 12 章

**Fig 12.1** | PDF p216 / 印刷 p196 | Z | 矢量
- 主张：约束优先的候选合成：三个条件候选各带开放验证门，同过 MEM/THR/QUAL。
- 科学：✓（图注声明"非定论、未部署验证、需在目标负载实测"）。箭头方向：✓ ①→②、②→③ 向下正确。
- **箭头触达：③→底排的横向总线带 3 个箭头——左右两个分别触 OUTCOME/GATED 顶边 ✓，中间一个悬在两框之间的空隙、无目标（冗余/浮动）→ P2；①→②、②→③ 的居中箭头停在下框上方留白（未贴边）→ P2**。
- 标签语义：✓（①–④、(a)(b)(c)）。轴/单位：N/A。字号：min 8.0pt ✓。
- 灰度：GATED 靠影线+✗ 与 OUTCOME 实心可分 ✓。碰撞：影线穿过 GATED 文字（可读，P3）。
- 图注：takeaway ✓ / 状态 ✓ / caveat ✓。来源状态：ILLUSTRATIVE conceptual。印刷可读：✓。
- 严重度：**P2**。修改：删掉中间冗余箭头（或让它指向一个真实目标）；①② 箭头下移贴框边。

## 第 13 章

**Fig 13.1** | PDF p224 / 印刷 p204 | Z | 矢量
- 主张：只有约束绑定才沿阶梯上行（GPU→host→multi-host→fleet），隐私/成本可下行。
- 科学：✓（三条红色触发注释正好落在其约束的迁移处：KV residency→host、goodput→multi-host、demand→fleet，放大复核确认）。
- 箭头方向：✓ 红色上行箭头、绿色下行箭头方向正确；**绿色虚线 de-escalate 箭头/尾均不锚定任何层级（自由漂浮）→ P3**；红色约束注释为无连接线的浮字（P3）。
- 标签语义：✓（"▼ constraints → STOP" ×4）。轴/单位：N/A。字号：min 8.0pt ✓。
- 灰度：红/绿同灰，但虚线 vs 粗实线、粗细差异提供冗余 ✓（P3）。
- 重叠/碰撞：无。图注：takeaway ✓ / 状态 ✓ / caveat ✓（"tiers are orthogonal, not a ranking"）。来源状态：ILLUSTRATIVE conceptual。
- 印刷可读：✓。严重度：P3。修改：de-escalate 虚线加两端锚点（顶/底层级小圆点）。

## 第 14 章

**Fig 14.1** | PDF p233 / 印刷 p213 | S | 矢量
- 主张：两段式基准——能力筛选（谁合格）→ 部署基准（谁满足 SLO），再喂给选型与 TCO。
- 科学：✓（顺序 capability→workload→cost/SLO 合理）。箭头方向：✓ 黑右向、绿下向、绿右向均触目标（绿标签略离轴，属标注位）。
- 标签语义：✓。轴/单位：N/A。字号：min 8.3pt ✓。灰度：蓝/橙/绿/黑降为灰阶但亮度可分（P3）。
- 重叠/碰撞：无（"deployed" 近右缘未截断）。图注：takeaway ✓ / 状态 [ILLUSTRATIVE conceptual] ✓ / **caveat 弱（227 字符单句，无"非实测"限定）→ P3**。
- 来源状态：ILLUSTRATIVE conceptual。印刷可读：✓（下方留白大）。严重度：P3。修改：图注补一句 "conceptual screen, not a measured benchmark suite"。

## 第 15 章

**Fig 15.1** | PDF p239 / 印刷 p219 | S | 矢量
- 主张：FlashAttention 数学相同、HBM 往返大幅减少（赢在 I/O 不在 FLOP）。
- 科学：✓（naive O(L²) vs tile O(L)；arXiv:2205.14135 正确；图注限定 "read once" 为 tile 级）。箭头方向：✓ 红(8)/绿(2) 双向箭头两端触框。
- 标签语义：✓。轴/单位：N/A。字号：min 8.5pt ✓。灰度：红/绿同灰（多/少靠数量与文字冗余，P3）。
- 重叠/碰撞：无。图注：takeaway ✓ / 状态 ✓ / caveat ✓。来源状态：ILLUSTRATIVE conceptual。印刷可读：✓。
- 严重度：P3。修改：无。

**Fig 15.2** | PDF p241 / 印刷 p221 | Z | 矢量（双面板）
- 主张：(a) 前缀复用↑ → prefill FLOPs↓；(b) decode goodput 随 batch 上升，缓存无关。
- 科学：**△——(b) 红色注释写 "goodput plateau (~b16)"，但曲线在 b16(≈66) 之后仍升到 b32(≈80)、b64(≈88)，并无平台；只是边际收益递减 → 注释措辞夸大 → P2**。图注本身写 "rises until HBM bandwidth saturates"，与曲线一致。
- 箭头方向：N/A（b16 红虚线为参考线无头）。标签语义：✓。轴/单位：✓ 两轴均有标签与单位（% of no-cache / a.u.）；**两 x 轴实为 log 但未标注 → P3**。
- 字号：min 8.0pt ✓（(b) 红色 5 行注释最挤 → P3）。灰度：(a) 靠标记形状 ○□ ✓；(b) 靠虚线 ✓。
- 重叠/碰撞：无。图注：takeaway ✓ / 状态 ✓ / caveat ✓。来源状态：ASSUMPTION, ILLUSTRATIVE。印刷可读：✓。
- 严重度：**P2**。修改：注释改 "diminishing gains past ~b16 (no hard plateau)" 或把曲线画到饱和；x 轴加 "log" 说明。

## 第 16 章

**Fig 16.1** | PDF p263 / 印刷 p243 | Z | 矢量（log-log TCO）
- 主张：冻结 21-host 舰队下，managed $20.80/1K 与 self-host $155.8K/mo 在 ≈7.5M req/mo 交叉（价带 6.2–10.4M），>24.96M 不可行。
- 科学：✓ **程序校验**：155800/0.0208=7.49M ✓；/0.025=6.23M、/0.015=10.39M ✓；40×624,000=24.96M ✓；蓝色点线 x=401.30 → **6.24e6（与 "canonical 6.24M" 标签一致）**；灰虚线 x=456.83 → **2.496e7（与 feasible max 一致）**（放大初判"蓝线穿星、标签错位"被坐标校验否证：星在 x≈408.6，两线相距 7.3pt）。
- 箭头方向：N/A（无箭头）。标签语义：✓（粉色价带**确实存在**并与图例色块匹配——初判否证）。
- **注释框无引线：break-even 框、feasible max 框、INFEASIBLE 框均漂浮，不指向星标/灰线/影线区 → P2**。
- **碰撞：白色 "feasible max 24.96M" 框压住蓝色点线（线被白底遮断），右缘贴灰虚线 → P2**。
- 轴/单位：✓ USD/mo、req/mo，双 log，刻度 1e3–1e7 / 1e4–1e8。字号：min 8.2pt ✓（顶部注释簇拥挤 → P3）。
- 灰度：蓝/红实线灰度为中灰/深灰可分；绿点划线与影线区靠线型 ✓（P3）。
- 图注：takeaway ✓ / 状态 ✓ / caveat ✓（1537 字符，明确 "not portable / not apples-to-apples / frozen-fleet"）。来源状态：DERIVED, ILLUSTRATIVE。
- 印刷可读：✓（顶部簇最紧）。严重度：**P2**。修改：三个注释框各加一条细引线到目标；feasible max 框左移让开蓝点线。

## 第 17 章

**Fig 17.1** | PDF p267 / 印刷 p247 | Z | 矢量，同页 15 行正文（无重叠）
- 主张：~5.5 req/s 突发单机（~2.0）扛不住 → 4 机 ~8.0 高于峰值，N−1=3 机 ~6.0 仍覆盖。
- 科学：✓ 4×2=8、3×2=6、5.5<6、5.5>2 全部自洽；图注含 queueing 限定（"capacity bound, not a queueing result; tail must be measured"）。
- 箭头方向：✓ **放大复核否证"无标注浮箭"初判**：t≈3 灰右向箭头配 "one host cannot meet the burst"；t≈9.5 为**双向竖直箭头**标 headroom/failover；峰值处红箭头指曲线——三者均有配对文字。
- 标签语义：✓。轴/单位：✓ offered load / req·s⁻¹；**x 轴 "time of day" 仅 0–10（10 小时窗），标签略含糊 → P3**。
- 字号：min 8.0pt ✓（顶部斜体免责两行最小）。灰度：实线/点线/点划线区分 ✓。
- 重叠/碰撞：无（五个标签分带排布）。图注：takeaway ✓ / 状态 ✓ / caveat ✓。来源状态：DERIVED, ILLUSTRATIVE。
- 印刷可读：✓。严重度：P3。修改：x 轴改 "time of day (h)" 或注明 10h 窗口。

## 第 18 章

**Fig 18.1** | PDF p293 / 印刷 p273 | Z | 矢量（级联路由）
- 主张：每请求只走一条路：capability filter → specialist，否则 cost/SLO gate → frontier/small，否则 fallthrough → general（早退级联）。
- 科学：✓（叶节点与级联语义完全对应；图注 "one model per request, early exit"）。箭头方向：✓ 全部左→右/向下正确。
- **标签缺口：顶部三条横向续行箭头无 "no/else" 标注，只有下分支标 "yes → …" → P2**。
- **箭头触达：三个灰色横向箭头是"孤立三角"，四周留白、无连线；下方绿色/灰色扇出箭头与目标框顶边之间有可见白缝 → P2**。
- 标签语义：✓。轴/单位：N/A。字号：min 8.8pt ✓（底部策略两行最小）。
- 灰度：橙/蓝/紫/红/青/绿六色分组在灰度塌缩，路由线与框边同灰系 → P2/P3（有文字冗余）。
- 重叠/碰撞：无（绿线贴 "yes→…" 标签但未压）。图注：takeaway ✓ / 状态 ✓ / caveat ✓。来源状态：DERIVED, ILLUSTRATIVE conceptual。
- 印刷可读：✓（上下两行间距偏紧 → P3）。严重度：**P2**。修改：①横向箭头加 "no →" 标签；②箭头加短杆并贴到框边。

## 第 19 章

**Fig 19.1** | PDF p296 / 印刷 p276 | S | 矢量（四态状态机）
- 主张：Plan→Execute→Observe→Decide；未解决回环 Plan、解决出 Final、超轮次 Stopped——防死循环靠预算不靠模型判断。
- 科学：✓（图注含 append-only 假设、counterfactual、[ILLUSTRATIVE]、guardrail caveat 四要素）。箭头方向：✓ 全部触目标（Decide 底部三出线并行不交叉）。
- 标签语义：✓（role 标签 model/action/state/check、terminal 标签）。轴/单位：N/A。字号：min 8.0pt ✓。
- 灰度：蓝/绿/红/紫/橙塌缩，回环靠虚线/实线区分 ✓（P3）。重叠/碰撞：无（顶排四框半幅宽度略挤 → P3）。
- 图注：takeaway ✓ / 状态 ✓ / caveat ✓。来源状态：ILLUSTRATIVE。印刷可读：✓。严重度：P3。修改：无。

**Fig 19.2** | PDF p306 / 印刷 p286 | Z | 矢量（双面板柱图）
- 主张：append-only 下 tokens/req 与 FP16 KV 随轮次线性增长，24.9 → 34.0 GB。
- 科学：✓ **图内数字自洽**：(34.0−24.9)/4=2.275GB/865tok ≈2.63MB/tok ✓；24.9GB=(9200+300)×2.62MB ✓（含 300 输出，故与正文 9.2K×2.62=24.1 的差是口径而非错误）。
- 箭头：N/A。标签语义：✓。轴/单位：✓ 两面板均有 Tokens/request 与 KV/request (GB, FP16)。
- **图例缺陷：左侧 "initial context (I₀)" 与 "added per turn (δ=800+γ=65)" 两条无色块 swatch，图例行留空档 → P2**。
- **跨图冲突：与 Fig 19.3 同一量用不同图案——O 在 19.2 是绿 X 影线、在 19.3 是绿实心；δ 在 19.2 并入橙反斜线、在 19.3 是绿点纹 → 读者无法迁移图例 → P2**。
- 字号：min 8.4pt ✓。灰度：绿 X vs 红点可分 ✓；蓝/橙影线方向相反 ✓。重叠/碰撞：无。
- 图注：takeaway ✓ / 状态 ✓ / caveat ✓。来源状态：DERIVED。印刷可读：✓。严重度：**P2**。修改：补两个 swatch；两图统一 O/δ 图案。

**Fig 19.3** | PDF p307 / 印刷 p287 | Z | 矢量（堆叠柱）
- 主张：上下文块逐轮堆叠 I₀+δ+γ+O，KV 24.9→34.0GB（+36%），compaction 可打断增长。
- 科学：✓ 五个 KV 标签与公式 total=I₀+T·δ+T·γ+O_final @2.62MB 完全吻合；(34.0−24.9)/24.9=36.5%≈36% ✓；**"6" 初判被否证——白字是 δ（图例与放大框均有定义）**。
- 箭头：N/A。标签语义：✓（I₀/O_final/δ/γ 图例 + magnified slice 框）。
- **轴/单位：无 y 轴、无刻度、无单位，柱高虽按比例绘制但读者只能读文字标签 → 违反"轴/单位须标注" → P2**。
- 字号：min 8.4pt ✓。灰度：四种图案（/ \ 实心 点纹）可分 ✓。重叠/碰撞：无（放大框与 KV 27.2 标签有间隙）。
- 图注：takeaway ✓ / 状态 ✓ / caveat ✓。来源状态：DERIVED, ILLUSTRATIVE。印刷可读：✓。
- 严重度：**P2**。修改：加 y 轴（tokens 或 GB）与刻度；与 19.2 统一图案。

## 第 20 章

**Fig 20.1** | PDF p323 / 印刷 p303 | Z | 栅格（400dpi，matplotlib，字号 8.6/9.0pt）
- 主张：容量随主机数线性升，但 served demand 在 40 rps 天花板平台化，N≥22 出现 unused capacity。
- 科学：✓ 17/8.6=1.977、C_eff=0.95×、S=min(40,C_eff)、21 理想/22 含 5% 折损，全部自洽；图内标 "analytical construction, not measured"。
- 箭头方向：✓ 两条注释箭头均触目标（"21/22" 箭触 (22,40) 点；derate 箭触灰线）。
- **碰撞初判否证：灰 C_analytic 线不穿过红 UNUSED 框——在框左上角 (N≈31,≈61) 处擦过/近失，框整体在线下方 → 降级为 P3（建议框下移 4pt 留边）**。
- 标签语义：✓（3 条图例系列与曲线一一对应，无缺项）。轴/单位：✓ Host count N (hosts) / Fleet rate (req/s)，刻度 0–60 / 0–120。
- 字号：生成器 fontsize 8.6–9.0pt ✓（栅格标定最小 ≈8.6pt）。灰度：灰实线 vs 深蓝实线亮度可分（程序灰度碰撞=0）✓；注释簇拥挤 → P3。
- 图注：takeaway ✓ / 状态 ✓ / caveat ✓（1123 字符）。来源状态：DERIVED, ILLUSTRATIVE。印刷可读：✓。
- 严重度：P3。修改：UNUSED 框下移/右移留 4pt；注释簇错位排布。

## 第 21 章

**Fig 21.1** | PDF p328 / 印刷 p308 | Z | 矢量，同页 12 行正文（无重叠）
- 主张：每次晋升都是对实测指标的 PASS/FAIL 门；FAIL 回滚到 last-known-good 再验证；生产反馈闭环再进门。
- 科学：✓ 阶段序 Data→Train→Eval→Canary→Observe→Promote→Serve、6 迁移 6 门 ✓。
- **图-注不符：绿色反馈线唯一箭头落在 Data 框左边，而图注写 "Production feedback returns evidence to data/evaluation"——Eval 未被指向 → P2**。
- **箭头触达：红色 FAIL 连线为纯点线无箭头（可接受为流向）；但绿色反馈箭头与 6 个小灰色迁移箭头均停在框间空隙、不贴框边 → P3**。
- 标签语义：✓。轴/单位：N/A。字号：min 8.0pt ✓（门框三行最紧 → P3）。
- **灰度：蓝阶段框与绿 Serve 框塌缩为同中灰，Serve 不可辨；门框浅色可分 → P2**。
- 重叠/碰撞：无。图注：takeaway ✓ / 状态 ✓ / caveat ✓。来源状态：ILLUSTRATIVE。印刷可读：✓。
- 严重度：**P2**。修改：①反馈线加第二个箭头指向 Eval（或图注改为 "to data"）；②Serve 用不同填充图案；③迁移箭头贴框边。

## 第 22 章

**Fig 22.1** | PDF p335 / 印刷 p315 | Z | 矢量（双 log 面板）
- 主张：左：prefill 每请求 = 线性 2NL + 二次项，L*≈53.4K 处二次超过线性；右：decode 每 token 的参数项 2N 与上下文无关（平坦）。
- 科学：✓ **图注公式 L*=N/(2·n_layers·d)=70e9/(2×80×8192)≈53.4K 程序复算正确**；图例 "quadratic 4·N·L²·d" 的因子 4 正确（QKᵀ 2L²d + AV 2L²d）。
- **符号复用缺陷：线性项 "2·N·L" 的 N=参数量，二次项 "4·N·L²·d" 的 N=层数，同一符号两种含义（图注用 n_layers 区分，图内没有）→ P2**。
- **无解释标记：红线 x=10K 处一个实心红点，无图例无注释 → P2**。
- 箭头方向：✓（"quadratic overtakes ~53K" 紫箭头指向交叉区，**尖端略偏左于真实交点** → P3）。
- 标签语义：✓。轴/单位：✓ PFLOP/request、PFLOP/token、K tokens，双 log，10 的幂刻度。
- **字号：min 7.8pt — 全书仅有的两个 <8pt 之一 → P1**。
- 灰度：三线靠实线/虚线/点划线 ✓。碰撞：无文字压线；右面板图例折行拥挤 → P3；图例紫线画成实线而曲线是点划线（线型不一致 → P3）。
- 图注：takeaway ✓ / 状态 ✓ / caveat ✓（2108 字符，全书最长）。来源状态：DERIVED, ILLUSTRATIVE。印刷可读：**△（7.8pt 低于 8pt 门槛）**。
- 严重度：**P1（字号）+ P2（N 符号、红点）**。修改：①图例字号 8.6pt+；②二次项写 4·n_layers·L²·d；③删红点或加注释；④图例线型与曲线一致。

## 第 23 章

**Fig 23.1** | PDF p344 / 印刷 p324 | Z | 矢量
- 主张：模糊诉求经 5 个编号问题 → 量化边界（TTFT/吞吐/成本）。
- 科学：✓ 2.1s 观测 vs ≤2s 目标（有意更严）、~25ms/tok、40rps、9.2K、8×H100≈$14.6K/mo、FP16→FP8 全部自洽；图注声明"非穷尽清单"。
- **箭头触达：4 个橙色三角连接件悬在框间空隙，上下均不贴框（无杆箭头）→ P2**；绿色箭头头部触结果框 ✓（杆顶与框 5 留白 → P3）。
- 箭头方向：✓ 全部向下。标签语义：✓。轴/单位：N/A。字号：min 9.2pt ✓。
- 灰度：橙步骤（浅灰）vs 绿结果（中灰 + 反相文字）可分 ✓。重叠/碰撞：无。
- 图注：takeaway ✓ / 状态 ✓ / caveat ✓。来源状态：ILLUSTRATIVE。印刷可读：✓。严重度：**P2**。修改：三角连接件贴上/下框边，或加短杆。

## 第 24 章

**Fig 24.1** | PDF p357 / 印刷 p337 | S | 矢量（红/绿队循环）
- 主张：probe→exposure→guardrails→metrics→green team 的 1→6 前向 + 6→1 红色反馈闭环。
- 科学：✓ 编号顺序与回环一致；图注补三条门（阻断准则/语料归属/回归阈值）——"无门则为仪式"。
- 箭头方向：✓ 灰前向箭头逐个触框；红回环 6→1 头触框 1 左边、尾接框 6 底边 ✓。
- 标签语义：✓（口号 "probe, measure, harden" 与步骤 2/3/4 对应略含糊 → P3）。轴/单位：N/A。字号：min 8.0pt ✓。
- 灰度：红(2)/紫(4)/蓝(6) 落在相近中灰，暗红(1)≈红(2)，回环线与框 2 同灰 → P3（编号+文字冗余）。
- 重叠/碰撞：无。图注：takeaway ✓ / 状态 ✓ / caveat ✓。来源状态：ILLUSTRATIVE。印刷可读：✓。严重度：P3。修改：框 1/2 用不同填充图案。

## 第 25 章

**Fig 25.1** | PDF p366 / 印刷 p346 | Z | 矢量（ADR 解剖 + 继承）
- 主张：ADR 五段固定（Title&status/Context/Decision/Consequences/Alternatives），保留不改；ADR-001 的 Consequences 成为 ADR-002 的 Context。
- 科学：✓ 五段名正确；"kept, not edited" + supersede 语义正确。
- **箭头触达：红色虚线箭头尖端停在 ADR-002 顶栏上方 ≈25px@280dpi（≈6.5pt）处，既未触顶栏也远未触 Context 芯片（≈0.95in）；且图注暗示 chip→chip，实际是块级箭头 → P2**。
- 箭头方向：✓（上→下）。标签语义：✓（右侧红字 "consequences of 001 → context of 002" 承载精确语义）。
- 轴/单位：N/A。字号：min 8.0pt ✓（芯片斜体注释 ≈8–9pt，放大复核"5–6pt 挤迫"初判被否证：有余量）。
- 灰度：红箭头(≈33% 灰) vs 深蓝标题(≈22% 灰) 可分 ✓。重叠/碰撞：无。
- 图注：takeaway ✓ / 状态 ✓ / caveat ✓（"illustrative structure, not a measured…"）。来源状态：ILLUSTRATIVE。印刷可读：✓。
- 严重度：**P2**。修改：箭头延长触到 ADR-002 顶栏（或明确画成 Consequences chip → Context chip）。

## 第 26 章

**Fig 26.1** | PDF p373 / 印刷 p353 | S | 矢量（分组条形）
- 主张：三类工作负载在六轴上呈不同 0–1 指纹，只能轴内比较。
- 科学：✓ 图注明确"主观归一化打分、非测量数据的 min-max、非 benchmark"，并区分 Ch4 六维。
- 箭头：N/A。标签语义：✓。轴/单位：✓ Normalized intensity (0–1) 0.0–1.0；六类目轴。
- 字号：min 8.0pt ✓。灰度：系列靠影线图案（/ × 点）编码，色塌缩安全 ✓（程序检出 1 对近灰，非语义对）。
- 重叠/碰撞：无。图注：takeaway ✓ / 状态 ✓ / caveat ✓。来源状态：DERIVED, ILLUSTRATIVE。印刷可读：✓。严重度：P3。修改：无。

**Fig 26.2** | PDF p380 / 印刷 p360 | Z | 矢量（三节点闭环）
- 主张：FACT →(trace)→ DERIVED →(validate)→ PATTERN →(adjust/feedback)→ FACT 的模式-测量-反馈闭环（capstone 70B FP16/8×H100）。
- 科学：✓ 单位一致（rps / % / ms）；p99 250 < baseline 450 自洽；图注给出 −44%、~48% 口径与"均值≠分位"限定。
- 箭头方向：✓ 三条边全部 1→2→3→1 正确，红箭头**触 FACT 框底边**（放大复核：不悬空）。
- **一条边两个标签："feedback"（竖段）与 "adjust + pick pattern"（横段）并存 → 冗余/含糊 → P3**；绿框内 "sharding ⇒" 悬空箭头无宾语 → P3。
- 标签语义：✓。轴/单位：N/A（框内自带单位）。
- **字号：min 7.6pt — 全书最低，<8pt → P1**。
- 灰度：红最深/蓝中/青最浅可分 ✓（程序检出 2 对近灰，靠 1/2/3 编号与文字冗余）。
- 重叠/碰撞：无。图注：takeaway ✓ / 状态 ✓ / caveat ✓。来源状态：ILLUSTRATIVE。印刷可读：**△（7.6pt）**。
- 严重度：**P1（字号）+ P3（双标签）**。修改：①框内/边标签字号提到 ≥8.6pt；②红边只留一个标签；③补全 "sharding ⇒ …"。

## 前置页

**Fig 1**（architect's decision loop） | PDF p15 / 印刷 ix | S | 矢量
- 主张：四阶段循环 Understand → Design&size → Validate&Defend → Commit，含 re-derive（03→02）与 iterate（04→01）两条反馈。
- 科学：✓（图注说明 03 产出 provisional 建议、04 过红队才定案）。箭头方向：✓ 两条反馈方向正确且触框边。
- 标签语义：✓。轴/单位：N/A。字号：min 8.5pt ✓。灰度：绿/红反馈箭头与四色框塌缩，靠位置+文字 ✓（P3）。
- 重叠/碰撞：无（旋转标签在曲线旁）。图注：takeaway ✓ / 状态（散文，无括号标签 → P3）/ caveat ✓（"provisional until challenged"）。
- 来源状态：散文状态。印刷可读：✓。严重度：P3。修改：可补 [CONCEPTUAL]。

**Fig 2**（reading the book two ways） | PDF p16 / 印刷 x | Z | 矢量
- 主张：A 逐层读（Part I→VI）与 B 按问题跳读（问题→章节）两条独立路径。
- 科学：✓（图注声明链接是起点、非完整覆盖）。箭头方向：N/A——**但两列外缘各有 5 个"只有箭头没有杆"的 ▼ 字形，漂浮在框间空隙、偏在外侧边距、无图例 → 看起来像断箭/项目符号 → P2**（放大复核：方向朝下正确，非反向）。
- 标签语义：✓（问题+章节对清晰）。轴/单位：N/A。字号：min 8.0pt ✓。
- **灰度：蓝列 vs 红列的区分基本仅靠颜色，灰度下两列趋同 → P2**（有表头文字冗余）。
- 重叠/碰撞：无。图注：takeaway ✓ / 状态 ✓ / caveat ✓。来源状态：散文状态。印刷可读：✓。
- 严重度：**P2**。修改：▼ 加短杆居中于框间隙并加图例（"next"），或改为实心分隔符；两列加不同边框线型。

## 附录 A

**Fig A.1** | PDF p383 / 印刷 p363 | S | 矢量（条形）
- 主张：2026 前沿 MoE 激活参数占比均为个位数（4.6/3.7/4.8/5.6%）。
- 科学：✓ 13/284≈4.6、104/2800≈3.7、6/125=4.8、18/320≈5.6 复算正确；Qwen 的 51B n-gram/4B MTP 口径在注释中披露。
- 箭头：N/A。标签语义：✓。轴/单位：✓ "% of total" 0–10 步长 2。字号：min 8.5pt ✓。
- 灰度：橙条靠长度+数值 ✓。重叠/碰撞：无（Qwen 两行右注放得下）。
- 图注：takeaway ✓（在标题内）/ 状态 [1P] ✓ / **caveat 缺（138 字符，无"厂商口径/非可比"限定）→ P3**。
- 来源状态：[1P]。印刷可读：✓。严重度：P3。修改：图注补 "vendor-reported totals; active-fraction definitions vary"。

**Fig A.2** | PDF p389 / 印刷 p369 | S | 矢量（表式图）
- 主张：各模型厂商自报的 KV/计算 "% remaining" 相对自己的基线很小，但不可跨模型排名。
- 科学：✓ 7% remaining=93% reduction ✓；分母口径差异（GLM BF16/layer、attention per head per layer）已在图注逐条声明。
- 箭头方向：✓ 四条 "100% → ~X%" 内联箭头触目标值。标签语义：✓（列头+脚注+行内子注）。
- 轴/单位：N/A（表）。字号：min 8.0pt ✓（绿色两行子注最紧）。
- **灰度：行色（红/蓝/绿）与红色 "NOT A CROSS-MODEL RANKING" 警示条在灰度下同灰，警示 salience 丢失 → P2**（有文字冗余）。
- 重叠/碰撞：无。图注：takeaway ✓ / 状态 ✓ / caveat ✓（1401 字符）。来源状态：[1P][DERIVED]。印刷可读：✓。
- 严重度：**P2**。修改：警示条改粗黑边+全大写（不依赖红色），或加影线底纹。

**Fig A.3** | PDF p392 / 印刷 p372 | S | 矢量（时代层叠）
- 主张：从单模型到多模型 agent fleet 的"书脊"演进（≈2017→≈2026），分效率/能力/fleet 三层。
- 科学：✓ 年代为近似标记且图注声明"非严格年表、层叠非因果谱系"；未来行标 [ILLUSTRATIVE][DERIVED]。
- 箭头：N/A（纵向排序）。标签语义：✓（图例线型+颜色）。轴/单位：右侧 ~YYYY 为松散时标（图注已说明）✓。
- 字号：min 8.5pt ✓。灰度：类别用边框线型（虚线/实线/粗）冗余编码 ✓；两档橙色深浅塌缩（P3，非语义对）。
- 重叠/碰撞：无。图注：takeaway ✓ / 状态 ✓ / caveat ✓。来源状态：ILLUSTRATIVE。印刷可读：✓。严重度：P3。修改：无。

**Fig A.4** | PDF p393 / 印刷 p373 | S | 矢量（位置层叠）
- 主张：智能应上移（出权重→后训练→系统→fleet）；model intelligence ≠ system intelligence。
- 科学：✓ 图注明确"横带是设计选择、非优劣排序"。箭头方向：✓ 红色上行轴箭头方向正确（坐标轴式，不触目标属设计）。
- 标签语义：✓。轴/单位：非数值轴，红箭头+说明 ✓。字号：min 8.0pt ✓。
- **灰度/对比：程序检出 4 对近灰；白字压在浅色带上（浅蓝 "Inside post-training"、浅绿 "Inside weights"）→ 灰度下白字压浅灰，可读性下降 → P2**。
- 重叠/碰撞：无。图注：takeaway ✓ / 状态 ✓ / caveat ✓。来源状态：ILLUSTRATIVE。印刷可读：✓（彩色下可读）。
- 严重度：**P2**。修改：浅色带上的白字改深色字，或加深带子填充。

**Fig A.5** | PDF p398 / 印刷 p378 | S | 栅格（400dpi）
- 主张：共享权重不省已执行的计算：真退出跳过 pass 3，事后选择仍要跑完 pass 3；各迭代 cache 独立。
- 科学：✓ 两条运行路径逻辑正确；图注 "illustrative exit index, no latency/quality result"。箭头方向：✓ 全部触目标（棕色跳过折线从 pass 3 上方绕过、落点在 exit 顶边 ✓）。
- 标签语义：✓（小瑕疵：上半图叫 "core pass N"、下半图叫 "pass N" → P3）。轴/单位：N/A。
- 字号：栅格标定 ≈9.4pt ✓。灰度：蓝/粉/米三类框与棕/黑箭头塌缩，靠文字+虚线 ✓（P3）。
- 重叠/碰撞：无（棕线在虚线框上方空隙通过，未压框）。图注：takeaway ✓ / 状态 ✓ / caveat ✓。来源状态：散文状态。
- 印刷可读：✓（右侧留白大）。严重度：P3。修改：统一 "pass N" 命名。

---

## 汇总

- **P1（3）**：Fig 22.1（图内最小 7.8pt）、Fig 26.2（7.6pt）、Fig 6.2（图注仅标题，缺 takeaway/状态/caveat）。
- **P2（19 项，涉及 16 图）**：2.2 注释框压 roofline；2 蓝/红列仅靠色 + ▼ 断箭；7.5 注释标签 9.5K vs 箭头指 10K 标记；7.8 runtime/weights 灰度同纹；10.1 图例影线 vs 图形实心 + weights/data 图例同纹不可分；11.1 idle/new 灰度同纹；12.1 冗余中间箭头 + ①② 箭头不贴框；15.2 "plateau ~b16" 与曲线不符；16.1 三注释框无引线 + feasible max 框压蓝点线；18.1 续行箭头无 "no" 标签 + 箭头悬浮；19.2 图例缺 2 个 swatch；19.2↔19.3 图案映射冲突；19.3 无 y 轴/单位；21.1 反馈箭头只指 Data（图注写 data/evaluation）+ Serve 灰度不可辨；22.1 N 符号复用 + 无解释红点；23.1 橙三角连接件悬浮；25.1 红箭头不达目标；A.2 警示条灰度失效；A.4 浅带白字对比。
- **P3（34 图）**：灰度颜色冗余不足、贴边、标签措辞、图注状态标签等打磨项（逐图见上）。
- **P0：0**。所有图的数值/公式/单位经程序或放大复核未发现科学错误；接触表初判为"缺陷"的 9 项（1.1 重复箭头、6.2 标签压柱/标签过小、10.1 红色 bubble、16.1 粉带缺失与蓝线错位、17.1 无标注浮箭、19.3 白字 "6"、20.1 线穿框、25.1 芯片字号、22.1 交叉量级）在放大/坐标复核后**否证**，详见 `figure-priority.md`。
- 字号：55/57 图 ≥8.0pt（其中 17 图恰为 8.0pt 矢量字号、零余量，另 Fig 1.2 栅格估算 ≈8.0pt 临界）；2 图 <8pt；8 个栅格图文字不可选中（无障碍/检索弱点），最小字高标定 8.0–9.4pt。