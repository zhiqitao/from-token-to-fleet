# 图表 P2 剩余项修复记录（figure-P2 remaining fixes）

对象：`from-token-to-fleet` 14 张图（任务项 1/2/5/7/9/10/11/12/13/14/15/16）。
方法：定位生成器 → 最小修改 → 重新生成 → pymupdf 量最小字号（≥8pt）→ 200dpi 渲染 + vision 复核（印刷尺寸）。
工作图（before/after/裁剪）存于 `$TMPDIR/figp2/`（base_*.png=修复前，new_*/v2_*/v3_*/v4_*/v5_*.png=各轮，crop_*.png=局部放大）。
未改动任何数值/数据/图注语义；未做整书构建 / git / 委派。

## 状态总览

| 项 | 图 | 生成器 | 修复前缺陷 | 修复 | 最小字号 | vision | before→after (pdf sha) |
|---|---|---|---|---|---|---|---|
| 1 | 16.1 | fig_ch16_tco.py | feasible-max 白框压在灰虚线上、无引线 | 框左移至灰线左侧 + 水平引线触灰线 | 8.00pt | ✓ | 5dae928b→048608f3 |
| 2 | 18.1 | fig_ch18_routing.py | 续行箭头无 "no" 标签、箭头悬浮不贴框 | 加 "no" 标签 + 箭头加杆贴框（前轮已改，本轮重生成确认） | 8.80pt | ✓ | 89baf3d4→8883e49a |
| 5 | 21.1 | fig_ch21_pipeline.py | 反馈箭头只指 Data、Serve 灰度不可辨 | 反馈线加第二箭头指 Eval + Serve 改斜影线（前轮已改，本轮重生成确认） | 8.00pt | ✓ | a4d262f0→32ab6961 |
| 7 | 7.5 | fig_ch7.py | 注释 "9.5K≈24.9GB" 箭头指 10K(9.2K) 标记 | 标记 9.2K→9.5K，与注释/图注一致 | 8.50pt | ✓ | db72a177→36661e6a |
| 9 | 10.1 | fig_ch10_parallel.py | 图例影线 vs 图形实心；weights/data 同纹 | 图形加影线（W 条///、batch\\、GPU×、comms 虚框）；weights/data 反向 | 8.50pt | ✓ | 84b05266→251da85c |
| 10 | 12.1 | fig_ch12.py | ③→底排中间冗余浮箭；①② 箭头不贴框 | 删中央杆+总线，改两条直箭（倒 V）触 OUTCOME/GATED 顶边 | 8.00pt | ✓ | d7b317b2→2128a91a |
| 11 | 23.1 | fig_batch2.py | 4 个橙三角连接件悬浮无杆 | 改显式竖线跨满框间空隙 + 小箭头触上下框 | 8.50pt | ✓ | 2b72e640→b33b2025 |
| 12 | 25.1 | fig_ch25_adr.py | 红虚线箭头距 ADR-002 顶栏 ~6.5pt 未触 | 箭头改直线、缩头(8)、尖端延至 new_top-0.18 触顶栏 | 8.00pt | ✓ | 8b600c5b→10f1ac9b |
| 13 | 2.2 | fig_ch2_roofline.py | 白注释框压断黑色 roofline 斜线 | 框移至左上 (1.0, 8.0e14)，整框在斜线上方；文字改深灰 | 8.00pt | ✓ | 56004fb9→5c76a925 |
| 14 | Fig 2(前置) | fig_preface_trace.py | 蓝/红列仅靠色；外缘 ▼ 无杆浮字 | 右列改虚线框（左列实线）；两侧边距箭头缩头(7)显杆 | 8.00pt | ✓ | 869ab6c3→3ea969cc |
| 15a | 7.8 | fig_ch7_tetris.py | runtime/weights 灰度同斜影线 | weights 单向斜线(///)、runtime 交叉网(×)、KV 点纹（前轮已改，本轮重生成确认） | 8.20pt | ✓ | fe986b9e→5dd3ec6e |
| 15b | 11.1 | fig_ch11_batch.py | idle/new 灰度同纹 | idle 点框+反斜、new 实框+正斜、in-flight 实心（前轮已改，本轮重生成确认） | 8.00pt | ✓ | 6bb6142f→943549a4 |
| 16a | A.2 | fig_ch27_norm.py | 警示条仅红字、灰度失效 | 加粗黑边 + 斜影线底纹的警示框 | 8.00pt | ✓ | 382644e4→5ed87694 |
| 16b | A.4 | fig_2702.py | 浅带白字低对比 | 按带亮度选字色：浅带(>145)改深字、深带留白字 | 8.00pt | ✓ | 61a3c520→668184f2 |

## 逐图说明

### 项 1 — Fig 16.1（TCO break-even）
- 前轮已给三框加引线，但 feasible-max 框被放在灰虚线正上方（x=vol_max），白底仍遮断灰线、引线不可见。
- 本轮：把 feasible-max 框移到灰线左侧（xytext=vol_max*0.16），水平引线（lw1.2）从框右缘触到灰线。
- vision（crop_16.1_topright.png）：框在灰线左侧、水平箭头触灰线、灰线顶部可见。break-even/INFEASIBLE 两框引线前轮已确认。
- 最小字号 8.00pt。

### 项 2 — Fig 18.1（路由级联）
- 前轮已加 "no" 标签 + 箭头加杆贴框。本轮重生成 + vision 确认：三条横向续行箭头均带 "no" 标签、有杆、触目标框边；扇出箭头触叶框顶边。
- 最小字号 8.80pt。

### 项 5 — Fig 21.1（生命周期门）
- 前轮已加第二反馈箭头指 Eval + Serve 改斜影线。本轮重生成 + vision 确认：绿色反馈线有两个箭头（Data 左缘 + Eval 顶边）；Serve 框为斜影线、与实心蓝阶段框灰度可分。
- 最小字号 8.00pt。

### 项 7 — Fig 7.5（KV 随上下文）
- 注释 "9.5K ≈ 24.9 GB" 与图注一致（2.62MB/tok×9.5K），但数据标记在 9.2K（视觉读作 10K），箭头指到 9.2K 标记 → 标签-目标错配。
- 本轮：把标记列 9.2K→9.5K（ctx 数组 + 高亮 scatter），箭头即指到 9.5K 标记，与注释/图注一致。未改 24.9GB 数值。
- vision（v2_7.5.png）：箭头落在 9.5K 标记上，标签与目标一致。
- 最小字号 8.50pt。

### 项 9 — Fig 10.1（TP/PP/DP 三面板）
- 图例 weights/data 画影线、图形用实心（不一致）；weights(///) 与 data(×) 在小色块下近似同纹。
- 本轮：cbox 加 hatch/ls 参数；图形元素套用图例影线（W 条 ///、batch shard \\、GPU 框 ×、all-reduce 框 虚线+点）；图例改为 weights=///、GPU=×、data=\\、comms=...，weights/data 反向。
- vision（v2_10.1.png）：图例与图形影线一致；weights(/) 与 data(\) 方向相反、灰度可分。
- 最小字号 8.50pt。

### 项 10 — Fig 12.1（候选合成）
- ③→底排中央杆+总线留下一个中间浮 tick；①② 箭头前轮已贴框。
- 本轮：删中央杆+水平总线，改两条直箭（从 CANDIDATES 底边中点分叉，倒 V）直接触 OUTCOME/GATED 顶边（xy y=0.288）。
- vision（v2_12.1.png）：中间无浮 tick；两箭头触底框顶边。
- 最小字号 8.00pt。

### 项 11 — Fig 23.1（模糊诉求→边界）
- 4 个橙连接件是"孤立三角"（箭头头 > 框间 ~10pt 空隙），无杆、悬浮。
- 本轮：改显式竖线（ax.plot）跨满框间空隙（y-0.02→y-0.25）+ 小箭头头(8)触下框。逐 gap 像素测量：4 条均跨满 27–28px。
- vision（v4_23.1.png）：橙连接件有可见竖杆、触上下框。（绿→结果框杆顶留白为 P3，不在本轮范围。）
- 最小字号 8.50pt。

### 项 12 — Fig 25.1（ADR 解剖）
- 红虚线箭头尖端距 ADR-002 顶栏 ~6.5pt 未触（大箭头头+曲线使视觉尖端偏上）。
- 本轮：箭头改直线(rad=0)、缩头(mutation 8)、尖端延至 new_top-0.18。像素测量：尖端落在 ADR-002 顶栏上（gap≈0）。
- vision（crop_25.1_gap.png 放大）：箭头尖端触 ADR-002 顶栏。
- 最小字号 8.00pt。

### 项 13 — Fig 2.2（roofline）
- 白注释框 (3.0,1.6e14) 宽 ~2.1 个十进位，黑色 roofline 斜线穿过框被遮断。
- 本轮：框移至左上 (1.0, 8.0e14)，整框在斜线上方（框右缘 x~126 处斜线 ~4.2e14，低于框底 ~6.2e14）；文字 #555→#333。
- vision（v4_2.2.png）：斜线完整可见、框在斜线上方清晰区。
- 最小字号 8.00pt。

### 项 14 — Fig 2（前置：两种读法）
- 蓝/红两列均实线框+平涂，灰度趋同；两侧外缘 5+5 个 ▼ 无杆浮字。
- 本轮：右列框改虚线（ls='--'，左列留实线）；两侧边距箭头缩头(mutation 7)显杆。
- vision（v3_pref2.png）：左列实线/右列虚线灰度可分；边距箭头有可见竖杆。
- 最小字号 8.00pt。

### 项 15a — Fig 7.8（Memory Tetris）
- 前轮已改：weights 单向斜线(///)、runtime 交叉网(×)、KV 点纹。本轮重生成 + vision 确认三者灰度可分。
- 最小字号 8.20pt。

### 项 15b — Fig 11.1（Orca 槽位）
- 前轮已改：idle 点框+反斜、new 实框+正斜、in-flight 实心。本轮重生成 + vision 确认灰度可分（方向+框线+明度三重冗余）。
- 最小字号 8.00pt。

### 项 16a — Fig A.2（厂商 % remaining）
- 警示 "NOT A CROSS-MODEL PERFORMANCE RANKING" 仅红粗体字、无边框/底纹，灰度失效。
- 本轮：加 Rectangle 粗黑边(lw2.5)+斜影线(///)底纹框住两行警示文字。
- vision（v3_A.2.png）：警示为粗黑边+斜纹底纹的横幅，灰度可辨。
- 最小字号 8.00pt。

### 项 16b — Fig A.4（智能该放哪）
- 浅蓝 "Inside post-training"、浅绿 "Inside weights"（及浅蓝 "Inside test-time search"）白字压浅底，低对比。
- 本轮：加 _text_color()，按带亮度(>145)选深字(#1a1a1a)、深带留白字。
- vision（v3_A.4.png）：三条浅带均深字、无白字压浅底。
- 最小字号 8.00pt。

## 资产落位
- 源：`design/manuscript/<ch>/figures/fig-*.pdf/.png`（13 张）+ `render/latex/assets/preface-trace.pdf/.png`（前置）。
- 构建副本：`render/latex/figures/fig-*.pdf/.png`（13 张，已校验与源 sha 一致）；前置图生成器直写 `render/latex/assets/`。
- 4 个原仅出 PNG 的生成器（fig_ch7.py / fig_batch2.py / fig_ch25_adr.py / fig_ch2_roofline.py）已补 `savefig(..., format='pdf')`，保证构建取到与 PNG 同步的矢量 PDF（copy_figures 的 "PDF≥PNG 才用 PDF" 守卫）。

## 未修 / 说明
- 无。14 张全部修复并通过 ≥8pt + vision 复核。
- 23.1 绿→结果框杆顶留白、18.1 六色灰度塌缩等为 P3，不在本轮 P2 范围，未动。
