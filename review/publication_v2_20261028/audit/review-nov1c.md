# FTF-nov1c — 2026-11-01 15:17 评审（441 页）P1/P2 修复证据

- **范围**：仅 `design/manuscript/*.md`（10 章）+ 图生成器/图资产（`render/fig_ch17_capacity.py`、`fig-17-1701.png/.pdf`）+ 本证据文件。
- **未做**：未改 renderer/根文件（`render/latex/*`、`book.yaml`、`book-architecture.md`、`canonical-workload.yaml`、`numerical-audit-ledger.md`）；无全书 build、无 git、无委派。
- **备份**：`~/.hermes/profiles/muta/cache/scratch/nov1c/before/`（13 份修复前原件）+ `sha_before.json`。
- **完整 diff**：`review/publication_v2_20261028/audit/review-nov1c.diff`（542 行，`diff -u`，字节精确）。

## 0. 复算基准（本文件所有数字的第一性原理来源）

参数全部取自书中既有声明：λ=40 rps、W=8.6 s、C=17（436 ÷ 24.9037 = 17.51 → floor 17）、u=0.70、ρ=0.95、N_spare=1、in-flight = λ·W = **344**；FP8 槽 floor 35；TCO：capex = n×350,000/60，energy = n×1,110.33，+10,000 固定，÷6,240,000 req → per-1K。

**选定策略（P1-01）**：u 与 ρ **独立**（非嵌套），分母相乘，N−1 备机在 ceil **之后**加：

```
N_provisioned = ⌈λ·W_KV / (C · u · ρ)⌉ + N_spare = ⌈344 / (17×0.70×0.95)⌉ + 1 = ⌈344/11.305⌉ + 1 = 31 + 1 = 32
```

若 ρ 已含在 70% 净折减内，则公式取 ρ=1 → ⌈344/11.9⌉+1 = **30**（书中已明确写出该变体并声明**本书不作此主张**）。

## 1. P1-01 — ρ/u/N−1 合成（RED → GREEN）

| 量 | 修复前（RED） | 修复后（GREEN） | 独立复算 |
|---|---|---|---|
| KV-only 政策 working | 29（⌈344/11.9⌉，ρ 未入式） | **31**（⌈344/11.305⌉） | 30.43 → 31 ✓ |
| KV-only 政策 total（+1） | **30** | **32**（31+1） | 31+1 ✓ |
| case(ii) 全方形 prefill 政策 total | 33（⌈21.81/0.70⌉+1） | **34**（⌈21.81/0.665⌉+1 = 33+1） | 32.797 → 33 → 34 ✓ |
| case(i) / case(iii) 政策 total | 28 / 30 | **29 / 32** | 27.97→28→29；30.39→31→32 ✓ |
| TCO @32 | $218,309.90/mo、$34.99/1K（30 台） | **$232,197.23/mo、$37.21/1K** | 186,666.67+35,530.56+10,000 = 232,197.23；÷6,240,000×1,000 = 37.2111 ✓ |
| TCO @34 | $239,140.89/mo、$38.32/1K（33 台） | **$246,084.55/mo、$39.44/1K** | 198,333.33+37,751.22+10,000 = 246,084.55；39.4366 ✓ |
| N−1 存活校验 | 29×1.9767×0.70 ≈ 40.1 | 31×1.9767×0.70×0.95 ≈ **40.7 ≥ 40** | 40.7497 ✓ |
| 盈亏平衡（Ch16） | 10.5M req/mo | **11.2M** | 232,197.23÷0.0208 = 11.163M ✓ |
| FP8 政策 | 15 working / 16 total | **不变**（⌈344/23.275⌉ = ⌈14.78⌉ = 15 / 16） | ✓ 已在书中写明"ceil 吸收了额外折减" |

**新增权威政策表**：Ch17 §17.4 **Table 17-1 — Provisioning policy (authoritative)**，逐符号定义 λ_peak / **W_KV** / **C** / **u** / **ρ** / **N_spare**，并给出"独立 vs 嵌套"的显式论证（含 ρ=1 变体 = 30 台的推导与为何本书不采用），表题保留 **analytical lower-bound screen, not measured SLO-goodput**。原 fleet-sizing matrix 顺延为 **Table 17-2**（全书仅 Ch16 一处引用 Table 17-1，已同步指向政策表；Ch17 内部引用已核对）。

**一条公式贯穿**：Ch17 §17.1/§17.3/§17.4/§17.5/§17.8/Lesson、Ch16 §16.2/§16.3/§16.4/§16.6/§16.9、Ch20 §20.1/§20.2、Ch4 §4.8、Ch25 ADR 全部改为 `⌈λ·W/(C·u·ρ)⌉ + N_spare`；矩阵三列折减因子改为 `C×0.7×0.95 = 11.305 / 8.645 / 17.955`，全部单元格重算：

| λ | in-flight | FP16 T0 | FP16 T3 | FP8 T3 | N−1 行 |
|---|---|---|---|---|---|
| 40 | 344 / 552 | 31 | 64 | 31 | **32 / 65 / 32** |
| 100 | 860 / 1,380 | 77 | 160 | 77 | — |
| 200 | 1,720 / 2,760 | 153 | **319** | 154 | — |

（复算中发现并修正一处我方录入错误：200 rps FP16 T3 初写 320，精确值 2760/8.645 = 319.26 → **319**。）
Ch17 §17.8 FP8 小案例同步：74 → **77 working / 78 total**（occupancy 69% → **66%**），并保留 u-only 变体 74 作对照。

## 2. P1-02 — Fig 17.1（图 + 生成器 + 图注）

- **图标题**：`Sizing a fleet of one model (ideal rho=1 analytical ceilings; small ~5.5-rps burst)`。
- **图内注记（3 行，右上）**：`Ideal rho=1 analytical ceiling — no SLO claim.` / `N-1 clears the burst only at rho = 1:` / `dash-dot (rho=0.85): ~5.1 < ~5.5, need 0.917.` —— **不再声称 6.0 rps 残余稳健清过 burst**。
- **新增稳健下界线**：`N1res_085 = 3 × 2.0 × 0.85 = 5.1`（dash-dot），交叉点 ρ = 5.5/(3×2.0) = **0.9167**；线与注记均写入生成器注释。
- **图注**（80 词）：`ideal ρ = 1 analytical service ceiling — no SLO claim` + `at ρ = 0.85 … ≈ 5.1 req/s, below the ~5.5 burst (ρ ≳ 0.917 …) so the 6.0 rps residual is not a robust failover margin` + `neither line is a queueing or p99 result (Ch 14)`。
- **版面校验**：临时 bbox 审计脚本（`scratch/nov1c/audit_fig17.py`）对全部 8 处 axes 文本 + 标题两两求交 → **overlaps: 0**；并用 vision 复看成图，确认无重叠/无裁切、dash-dot 线可见。为给新注记腾位，`N = 4 fleet` 标签缩短、`failover` 标签下移至 `peak-1.15`（避开 dash-dot 线）。

## 3. P1-03 — 标签三轴（Ch4 p57 变更日志 + Ch23 p335 对话）

- **Ch4 变更日志框**（120+ 词 → 79 词）：改为"given → derived → hypothesized → validated"四态，并显式写明 **[HYPOTHESIS] 属认识论轴、[LAB]/[2°] 属来源轴（非验证阶段）**，指向新 Note 1。
- **新增 Note 1 (Table 4-2)**：完整三轴定义 —— Axis1 来源 [1P]/[canonical scenario]/[ILLUSTRATIVE]/[2°]/[LAB] × Axis2 认识论 [FACT]/[DERIVED]/[ASSUMPTION]/[HYPOTHESIS]/[UNRESOLVED] × Axis3 测量层级 ANALYTICAL/ILLUSTRATIVE/MODELED/MEASURED(UNMEASURED)，并给出"标签对 = Axis1 + Axis2，Axis3 随行"的组合规则与禁配规则。原表级 provenance 注缩短为 50 词并入 Note 1。
- **Ch23 对话**：两处 `[2°]` → **`[ILLUSTRATIVE]`**（场景来源，非二手来源），并注明与 Sources 章的轴定义关系；全章 `[2°]` 余 0 处误标（其余 `[2°]` 均为合法来源轴用法，已全库扫描确认）。

## 4. P1-04 — `v20260913+addendum-20261101`（**部分完成 → 见 §9 OPEN**）

- **已完成**：Ch27 附录新增 **Revision note — `v20260913+addendum-20261101`（access date 2026-11-01）**，列出受影响的 DeepSeek 主张：(1) `deepseek-v4-flash` / `deepseek-v4-flash-vision-exp` 已于 2026-09-10 退役、别名改路由 V4.1-Flash，"V4-Flash" 非现役名；(2) 2026-09-10 公告"V4-Pro 自 09-14 起按 V4.1-Flash 名义与费率路由"**已被现行 change log 取代**（V4-Pro 仍独立计费）；(3) 任何把快照变体名读作"现役名"的用法。每条均标 **accessed 2026-11-01**，并声明 2026-08-30 四族对比/图/A.10 来源表**不改**；附 3 条来源 URL 与检索日期。
- **未完成**：Preface 与 Appendix 修订说明/edition history 位于 `render/latex/preface.tex`（renderer 根，非本任务所有权）→ **OPEN**。

## 5. P1-05 — Ch17 网络例（t_fixed / t_transfer / t_queue）

- 新增分解式 `t_net = t_fixed + t_transfer + t_queue`，三项各一行定义（RTT+序列化 / D÷B_effective / 排队）。
- 明确 **20 ms 是检索服务的观测往返时长（service retrieval RTT），不是 rack-line latency**，且其中已含 t_transfer 与 t_queue。
- `G_per-req = D/t_net = 250 MB/s ≈ 2 Gbps` 改称 **effective per-request goodput（payload ÷ 观测时长）**，并写明瞬时速率 = `D/t_transfer ≥ D/t_net`，链路须按 `D/t_transfer` 定容；给出 5 MB ÷ 1.25 GB/s = **4 ms** 的自洽校验。
- 共享链路判据改为 **聚合供给字节率 vs 链路预算**：`B_agg = φ·λ·D = 20 MB/s` 对 10 Gbps = 1.25 GB/s → **1.6%**（保留原 ~5× per-request 余量表述）；恶化例改为"聚合 1 GB/s ≈ 80% 链路预算 + 50 MB 需 40 ms > 20 ms，故需 20 Gbps"。
- 同步 Ch17 §17.5 `B_min` 段与 §17.8 小案例措辞（offered byte rate vs link budget；per-request transfer leg）。

## 6. P2-01 — Table 19-1

- 行名 `Incremental orchestration (Lbase + T·L_agent)` → **`Base + orchestration subtotal (Lbase + T·L_agent)`**（表内 + 正文 2 处 + 脚注，共 3 处，余 0）。
- T=3 列 `~13.8 s` → **`13.85 s`**；脚注改为 `13.854 s → 13.85 s`，并写明 **13.8/13.9 是同一数值的显示取整，不是两个量**；Ch17 §8 显示为 ~13.8 s（其 in-flight 列 1,380 = 100×13.8 依赖该显示值，故 Ch17 不改数，仅在矩阵表题加注 `13.854 s before display rounding — 13.85 s, as reported in Ch 19 Table 19-1`）。
- 正文 4 处 `~13.8 s` → `~13.85 s`（含"增长 8.6 → 至少 13.85 s (~1.6×)"）。

## 7. P2-02 — Ch22 结论句

`makes clear a homogeneous design will be suboptimal` → **`makes P/D disaggregation a candidate worth testing for either bottleneck; benchmarking (Ch 14) and TCO (Ch 16) determine whether it wins`**（全库该短语余 0 处）。

## 8. P2-03 / P2-07

**P2-03**：Ch25 §6 最终 ADR 新增 **Requirement coverage matrix**（R1–R6：需求 → 所用 screen → 状态），其中 **R5 = `multi-region active-active: NOT VALIDATED / NOT PRICED`**（无区域容量/复制/路由/故障测试进入任何数字），并加一句"HOLD 存在的理由就是 R5；所有 $/1K 与主机数均为单区域"。Ch22 的 ADR 记录加指针 `requirement-coverage matrix … Ch 25 §6 copy of this record`。
（假设：Ch25 §6 为"final canonical ADR"；若 canonical 指别处，指针需改指 —— 见 §9。）

**P2-07**（图注/表注压缩，推导移入编号注）：

| 位置 | 修复前词数 | 修复后词数 | 推导去向 |
|---|---|---|---|
| Ch4 pp54-57 canonical ledger（变更日志框 / teaching-model 框 / 表级 provenance 注） | ~120 / ~90 / ~120 | **79 / 69 / 65** | **Note 1 (Table 4-2)**（新增，编号注，259 词） |
| Fig 11.3 图注 | 183 | **81** | **Note 11.3-1 (Fig 11.3)**（新增：35 GB = 13,000×2.62；450 GB/s → 0.08 s；40 GB/s → 0.9 s；1.4 TB/s 为聚合校验） |
| Fig 16.1 图注 | 226 | **80** | 既有注改为 **Note 16.1-1 (Fig 16.1)**，图注指针同步 |
| Fig 22.1 图注 | 173 | **81** | 既有注改为 **Note 22.1-1 (Fig 22.1)**，图注指针同步 |

三条图注均保留"takeaway + 几何/来源 + 一条 caveat"三段式与 `[ILLUSTRATIVE][DERIVED]`。

## 9. 文件清单（sha256 前 → 后）

| 文件 | before | after |
|---|---|---|
| design/manuscript/chapter-04/chapter-04.md | `a891632dbf81159a9e021efd1d3ed0071e9150aba22df20fe2128aa0b8b4863a` | `b297660b6a294adb59efb55e41c1246b2eaba01ee1d35ec0e19026ef63e51b86` |
| design/manuscript/chapter-11/chapter-11.md | `ce4ddcfee6e035509ea909916c0a75899d59574ead2d172da12790dc8f74f1d3` | `d78868fdd6209d19d424102e20de3a44a644c8457fdc92c0f13bb1c9a8488ceb` |
| design/manuscript/chapter-16/chapter-16.md | `19ae2a73d3e85519971ec55fb7088f00093ee2200e72ebb1a5a79bc9caca58e2` | `2d67ed15bea5a865e70c00079662d8327d3431b9c4830c5d108d1ac01ccf10f7` |
| design/manuscript/chapter-17/chapter-17.md | `b775d814f446686cedebb9611fb959bc1bce88fb6c847541c670069120358e6e` | `09299b9b50bd6de91c8a1ac2942577f2073e1122749f5996c2654219fcb24055` |
| design/manuscript/chapter-19/chapter-19.md | `56fd9b539c8c69f6867221f46dba61c88aa0406a6d962bdd76c445cb6bfa46c6` | `aa0607b88b66174843ff32f515352cae0eb950909406d53c1236010e02295288` |
| design/manuscript/chapter-20/chapter-20.md | `faff9831bbbae095ae9cfb90687482daedbc9ae36b81236958cad87ad8508caf` | `945b85a24443c90b840af522cb7b10d59d6c34d4716491b57035874f6d0f023b` |
| design/manuscript/chapter-22/chapter-22.md | `247c916ee687113952bc36404dcafdecb2d53afc613d7482d89f30eaf5cfa4bc` | `0cfa07bae3894fbc4d2a4f4aca4eb2fc59e778e2bc0f1d07e010475731223c16` |
| design/manuscript/chapter-23/chapter-23.md | `b2c5d345bb8987479c5b64fb28bfa4874830ad7bae4a550a4bd0f13f4d90002c` | `868e3387a85dc67427e49be2695acd5d73aa5805edeb09ed109424573ea44dc4` |
| design/manuscript/chapter-25/chapter-25.md | `86f640461d541015f8f2cf6dbdbd0395edb90c5d233d218c8f87ca3ec2e87655` | `cec020b35468512cd33ae776435b59efe6be02a4689db3553c2381e2c0fd5ecf` |
| design/manuscript/chapter-27/chapter-27.md | `1650ed0450b0fc3e8df0b043a391020b27faa6030a8800fed30395f33f68745f` | `2670ba7d9901a87201aa8cac529215b6dd7f328ec3d30f2a6af5dd2f5762f2f1` |
| render/fig_ch17_capacity.py | `fada6d9669c5654f66fd7cb552daf5414365bbd2e9b918bdbad68a3cf009cd00` | `c822f3d91c26bd63712a6967d990d7f941da4e176d74d1addcea66e11b5e8951` |
| design/manuscript/chapter-17/figures/fig-17-1701.png | `357aed2c9a86c1b1cbbfc4e61645630a8178112d28a2252a8461eb0fa4789160` | `fe7ed149aca16220b08912d8a13d6ca62b1ec53f47301f0ab1159ea024f189f4` |
| design/manuscript/chapter-17/figures/fig-17-1701.pdf | `e812094d43bcdde03d98c1c4d1b69177c1d18658efa9145646a6b41055c1947c` | `15c49bbada5a0394579db5483ab7949f572096e387cb9fd4afb0e0e84e73d8ee` |

## 10. 复核扫描（修复后全库 `design/`）

- 陈旧值 **0 命中**：`218,309` / `34.99` / `38.32` / `239,140` / `29 working` / `30 hosts` / `⌈21.81/0.70` / `⌈344/11.9`（作为政策式）/ `19/21/22/30/33` / `Incremental orchestration (` / `makes clear a homogeneous`。
- 保留的合法旧值：`⌈430/11.9⌉ = ⌈36.13⌉`（Ch4 u-only 屏，已标注"u-only screen"并给出政策值 39）；`⌈344/11.9⌉` 不再作为政策式出现。
- 全部新值已用独立 Python 复算脚本逐项断言（见 §1 表）。

## 11. OPEN（本任务范围内不可解）

1. **P1-04 未完**：`render/latex/preface.tex` 的 Preface 修订说明 + Appendix revision note + Edition history 未加 `v20260913+addendum-20261101`（renderer 根，非本任务所有权）。Ch27 附录侧已完成。
2. **P2-03 canonical 指认**：requirement-coverage matrix 落在 Ch25 §6 ADR（并由 Ch22 ADR 指向）。若"final canonical ADR"另有所指，需改指针。
3. **Table 17-1/17-2 重编号**：`render/latex/emit_book.py` 由字面 `Table 17-N` 生成 `\hyperref[tab:17.N]`；本次把政策表定为 17-1、矩阵顺延 17-2，**需一次全书 build 验证交叉引用**（本任务不做 build）。
4. **Ch17 的 13.8 s 显示值**：Ch17 in-flight 列（1,380 = 100×13.8）与矩阵表题依赖 13.8 显示；已加"13.854 s before display rounding"注记，但若要求全书统一印 13.85，则 Ch17 矩阵 in-flight 列需连动改为 1,385/2,770 并重算整表 —— 超出本次"keep other numbers"约束，未做。