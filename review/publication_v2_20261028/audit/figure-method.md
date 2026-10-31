# 图表审计 — 方法与测量（figure-method）

## 覆盖与产物
- 编号图 **57**（List of Figures，PDF pp.9–11）；父任务所称 58 = 57 编号图 + 封面 Figure 元素（结构树 58 个 Figure/Alt，Alt 覆盖 58/58）。
- 视觉检查：15 张 2×2 接触表（140 dpi = 实体印刷尺寸）覆盖 57/57；20 张 280 dpi 放大复核覆盖 20/57（优先图 + 疑似缺陷）。**无 INCOMPLETE**。
- 产物：`figure-crops/` 114 张、`figure-sheets/` 15 张、`figure-zooms/` 20 张、整页渲染 57 张（scratch/pages/）。
- 本审计只读：未改动 manuscript/style/generator；未做全书重建、未跑 git、未委派。

## 判据与工具
- **字号**：矢量图取 PDF 文本 span 的 min font size（真实字号，非视觉估计）；栅格图（8 个）文字不可选中，用源 PNG 连通域字高 × (439.2pt / 图宽px) 估算，并用 Fig 20.1（生成器 fontsize=8.6pt 已知）标定系数（cap 与 x-height 两路取均值），误差约 ±1pt，标 `*`。
- **灰度**：140 dpi 渲染转灰度后，统计图区内 Δluma<18 且色相差大、重叠面积 >3% 的填充对（`gray_collision_pairs`）；线型/影线/形状冗余由视觉复核判定。
- **几何**：内容流 `cm/q/Q` 矩阵跟踪得 `fig_rect`；箭头触达、压字、穿线由 280 dpi 放大逐条判定。
- **数值**：TCO/容量/FLOP/字节等关键数字用脚本复算（见 figure-priority.md）。
- **图注质量**：逐图检查 takeaway 句 / 状态标签（[TAG] 或散文）/ 单一 caveat 三要素。

## 测量总表
| 图 | PDF页 | 印刷页 | 图内最小字号 | 栅格dpi | 灰度近灰对 | 同页正文行 | 覆盖 | 状态标签 |
|---|---|---|---|---|---|---|---|---|
| 1.1 | 27 | 7 | ≈9.1pt* | 422.3 | 0 | 0 | Z | ILLUSTRATIVE CONCEPTUAL |
| 1.2 | 28 | 8 | ≈8.0pt* | 521.3 | 0 | 0 | S | ILLUSTRATIVE CONCEPTUAL |
| 2.1 | 35 | 15 | 8.0pt | - | 0 | 0 | S | ILLUSTRATIVE CONCEPTUAL |
| 2.2 | 43 | 23 | 8.0pt | - | 2 | 0 | Z | — |
| 3.1 | 51 | 31 | 10.1pt | - | 0 | 11 | S | — |
| 3.2 | 53 | 33 | 10.1pt | - | 0 | 0 | S | — |
| 3.3 | 62 | 42 | ≈9.0pt* | 350.0 | 0 | 15 | S | — |
| 3.4 | 66 | 46 | 8.4pt | - | 0 | 0 | S | DERIVED,ILLUSTRATIVE |
| 4.1 | 89 | 69 | 9.2pt | - | 0 | 0 | S | ILLUSTRATIVE CONCEPTUAL |
| 5.1 | 104 | 84 | 8.0pt | - | 0 | 0 | S | ILLUSTRATIVE CONCEPTUAL |
| 6.1 | 107 | 87 | 8.4pt | - | 0 | 0 | S | ILLUSTRATIVE CONCEPTUAL |
| 6.2 | 109 | 89 | 8.5pt | - | 0 | 0 | Z | — |
| 7.1 | 122 | 102 | 8.2pt | - | 0 | 13 | S | DERIVED,ILLUSTRATIVE |
| 7.2 | 124 | 104 | 9.4pt | - | 0 | 0 | S | — |
| 7.3 | 128 | 108 | ≈8.9pt* | 600.0 | 0 | 0 | S | — |
| 7.4 | 130 | 110 | ≈9.4pt* | 600.0 | 0 | 0 | S | — |
| 7.5 | 137 | 117 | 8.5pt | - | 0 | 0 | Z | DERIVED,ILLUSTRATIVE |
| 7.6 | 138 | 118 | 8.2pt | - | 0 | 0 | S | DERIVED,ILLUSTRATIVE |
| 7.7 | 139 | 119 | 8.5pt | - | 0 | 0 | S | DERIVED,ILLUSTRATIVE |
| 7.8 | 140 | 120 | 8.2pt | - | 0 | 0 | S | DERIVED,ILLUSTRATIVE |
| 8.1 | 146 | 126 | 10.0pt | - | 0 | 0 | S | ILLUSTRATIVE CONCEPTUAL |
| 8.2 | 152 | 132 | 8.0pt | - | 0 | 0 | S | — |
| 8.3 | 157 | 137 | ≈9.3pt* | 350.0 | 0 | 0 | S | — |
| 9.1 | 166 | 146 | 9.0pt | - | 0 | 0 | S | ANALYTICAL,DERIVED,ILLUSTRATIVE |
| 9.2 | 167 | 147 | 9.5pt | - | 0 | 0 | S | DERIVED,ILLUSTRATIVE |
| 9.3 | 168 | 148 | 9.5pt | - | 0 | 0 | S | ILLUSTRATIVE |
| 10.1 | 180 | 160 | 8.5pt | - | 0 | 0 | Z | ILLUSTRATIVE CONCEPTUAL |
| 11.1 | 193 | 173 | 8.0pt | - | 0 | 0 | S | ILLUSTRATIVE CONCEPTUAL |
| 11.2 | 197 | 177 | 9.2pt | - | 0 | 6 | S | ILLUSTRATIVE CONCEPTUAL |
| 11.3 | 198 | 178 | 8.5pt | - | 0 | 0 | S | DERIVED,ILLUSTRATIVE |
| 11.4 | 202 | 182 | 10.1pt | - | 0 | 0 | S | — |
| 12.1 | 216 | 196 | 8.0pt | - | 0 | 0 | Z | ILLUSTRATIVE CONCEPTUAL |
| 13.1 | 224 | 204 | 8.0pt | - | 0 | 0 | Z | ILLUSTRATIVE CONCEPTUAL |
| 14.1 | 233 | 213 | 8.3pt | - | 0 | 0 | S | ILLUSTRATIVE CONCEPTUAL |
| 15.1 | 239 | 219 | 8.5pt | - | 0 | 0 | S | ILLUSTRATIVE CONCEPTUAL |
| 15.2 | 241 | 221 | 8.0pt | - | 0 | 13 | Z | ASSUMPTION,ILLUSTRATIVE |
| 16.1 | 263 | 243 | 8.2pt | - | 0 | 0 | Z | DERIVED,ILLUSTRATIVE |
| 17.1 | 267 | 247 | 8.0pt | - | 0 | 15 | Z | DERIVED,ILLUSTRATIVE |
| 18.1 | 293 | 273 | 8.8pt | - | 0 | 4 | Z | DERIVED,ILLUSTRATIVE CONCEPTUAL |
| 19.1 | 296 | 276 | 8.0pt | - | 0 | 0 | S | ILLUSTRATIVE |
| 19.2 | 306 | 286 | 8.4pt | - | 0 | 0 | Z | DERIVED |
| 19.3 | 307 | 287 | 8.4pt | - | 0 | 0 | Z | DERIVED,ILLUSTRATIVE |
| 20.1 | 323 | 303 | ≈8.6pt* | 400.0 | 0 | 0 | Z | DERIVED,ILLUSTRATIVE |
| 21.1 | 328 | 308 | 8.0pt | - | 1 | 12 | Z | ILLUSTRATIVE |
| 22.1 | 335 | 315 | 7.8pt | - | 0 | 0 | Z | DERIVED,ILLUSTRATIVE |
| 23.1 | 344 | 324 | 9.2pt | - | 0 | 0 | Z | ILLUSTRATIVE |
| 24.1 | 357 | 337 | 8.0pt | - | 0 | 0 | S | ILLUSTRATIVE |
| 25.1 | 366 | 346 | 8.0pt | - | 0 | 0 | Z | ILLUSTRATIVE |
| 26.1 | 373 | 353 | 8.0pt | - | 1 | 0 | S | DERIVED,ILLUSTRATIVE |
| 26.2 | 380 | 360 | 7.6pt | - | 2 | 0 | Z | ILLUSTRATIVE |
| 1 | 15 | ix | 8.5pt | - | 0 | 0 | S | — |
| 2 | 16 | x | 8.0pt | - | 0 | 0 | Z | — |
| A.1 | 383 | 363 | 8.5pt | - | 0 | 0 | S | — |
| A.2 | 389 | 369 | 8.0pt | - | 0 | 0 | S | DERIVED |
| A.3 | 392 | 372 | 8.5pt | - | 1 | 0 | S | ILLUSTRATIVE |
| A.4 | 393 | 373 | 8.0pt | - | 4 | 0 | S | ILLUSTRATIVE |
| A.5 | 398 | 378 | ≈9.4pt* | 400.0 | 0 | 0 | S | — |

\* 栅格图标定估算（cap-height 路，以 Fig 20.1 已知 8.6pt 标定），±1pt。灰度近灰对 = 程序检出的填充色对数（需结合线型/影线冗余判读，非直接缺陷数）。
