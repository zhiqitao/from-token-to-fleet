# MiMo 源文核验 — R30 引用/出处独立复核（fresh pass）

| 项 | 值 |
|---|---|
| 被审对象 | FTF-R10 台账 `audit/source-verification.md` + ch7/ch8/ch9 未钉引用 + 2026-10-28 附录增补 |
| 核验日 | 2026-10-31 (UTC-07)；网络可达处实测，不可达记 **unverified/inaccessible**，不判 confirmed |
| 范围 | (1) A-S88/A-S92 与 ch7/8/9 moving refs；(2) 增补出处显式性；(3) 钉死 commit 抽样 200 + 数字对源；(4) 引用-主张错配 / 基准被标为实测 / 8月快照被当现状 |
| 证据工具 | curl 状态码、GitHub/HF API、pdftotext、Wayback API、浏览器渲染 (z.ai SPA)、仓库内 2026-10-28 归档 |
| 新发现 | **MiMo-C01 – C23**（本文件，只读审计，未改任何稿件/台账） |

**证据分级约定**：`vendor` = 厂商自述 [1P]；`independent` = 第三方 [2°]；`author-measured` = 本书自测（本轮**未发现任何一条**）。

---

## 1. A-S88 / A-S92（两条 UNVERIFIED Habana）

| ID | 引用 | 主张 | 判定 | 证据 |
|---|---|---|---|---|
| **MiMo-C01** | `A-S88` docs.habana.ai/en/latest/API_Reference_Guides/HCCL_APIs/index.html（ch8 L46、ch9 L129、ch27 L338 `[^oct-ix-47]`） | "Habana 自带 HCCL 集合通信库" / "Gaudi exposes HCCL" | **confirmed（内容层）**；钉死状态仍 UNVERIFIED（R3 处置可接受） | 2026-10-31 HTTP **200**；页面标题 "Habana Collective Communications Library (HCCL) API Reference — Gaudi Documentation **1.24.2**"；同页 `init_process_group(backend='hccl')`。主张与源一致，vendor 文档 |
| **MiMo-C02** | `A-S92` …/Porting_PyTorch_Models_to_Gaudi.html（ch8 L46、ch27 L346 `[^oct-ix-55]`） | "Gaudi 走独立 `hpu` 路径，张量分配为 `torch.device(\"hpu\")`" | **confirmed（内容层）** | HTTP **200**；页面正文逐字含 `device = torch.device("hpu")`、`import habana_frameworks.torch.core`。ch8 主张与源逐字一致 |
| **MiMo-C03** | 台账 §3 "no versioned path, tag or commit id" | 同左 | **confirmed** | 实测 `/en/1.24.2/…` 与 `/en/1.20.0/…` 均 **404**；`/en/` 200；页面无 `<option>` 版本选择器，meta `version-slug=latest`。补充：页内自述版本串 "Gaudi Documentation 1.24.2" **可取**，台账未记录（可作 provenance） |
| **MiMo-C04** | 台账 §3/§4 对 A-S88/A-S92 记 "no archived copy" | 暗示无任何不可变副本 | **mismatch（表述不完整，非致命）** | Wayback API 返回两 URL 均有快照 `20260926170046` / `20260926170113`，实抓 **200** 且内容匹配（HCCL 标题命中；porting 快照含 `hpu`×2）。仓库自有归档 `source-index.json`（78 条）确无 habana → "no archived copy" 仅对**仓库归档**为真；第三方不可变快照**本可取**，状态可从 UNVERIFIED 升为 snapshot-pinned |

## 2. ch7/ch8/ch9 仍 moving 的 `raw/main` 类引用

**清单实测**（与台账 §10 对账）：ch7 = 2 ✓；ch8 = 6 ✓；**ch9 = 5，台账只列 2**。

| ID | 引用 | 主张 | 判定 | 证据 |
|---|---|---|---|---|
| **MiMo-C05** | ch9 L175 `intel/torch-ccl/master/README.md`、L187 `ROCm/rccl/develop/README.md`、L187 `openucx/ucc/master/README.md` | 台账 §10 称 ch9 仅剩 2 条 moving | **mismatch（清单漏计 3 条）** | 实测 ch9 moving 共 5（habana `/latest/`、gloo `/main/`、上述 3 条 branch）。R1 枚举式只认 `main/latest/…`，`master/develop` 落漏网 → 台账"其余 moving refs"计数不完整 |
| **MiMo-C06** | 台账所列 ch7/8/9 全部 10 条 moving refs | 是否已 stale/错误 | **acceptable（今日未漂移），但仍 unpinned** | 10/10 HTTP **200**（2026-10-31）。5 条 HF 引用 main 与 R10 钉死 commit **字节相同**（Qwen3.8-27B `1d4bf0f2`、huginn `bb6621b6`、Wan `b8fff731`、DS-V4.1 `314113f8`、LLaDA2.X `a7983298`，sha256 逐一比对 IDENTICAL）；gloo README 自 2026-06-17 未再改；habana 现行 docs=1.24.2。**风险仍在**：A-S15 已示范 3 天内漂移，这些引用无 pin 即静默漂移 |
| **MiMo-C07** | ch7 L114 Qwen3.8-27B `raw/main/config.json` | 16 全注意力层 / 4 KV heads / head_dim 256 / 262,144 tokens；65,536 B→16 GiB、131,072→8 GiB | **confirmed**（vendor config + 本书算术） | config `text_config`: `layer_types` 64 层中 **full_attention=16**（interval=4）、`num_key_value_heads=4`、`head_dim=256`、`max_position_embeddings=262144`；算术实算 `2×16×4×256×2=65536`、×262144 = 17,179,869,184 B = **16.0 GiB**、×131072 = **8.0 GiB** ✓ |
| **MiMo-C08** | ch7 L124 / ch8 L79 huginn `raw/main/README.md` | 模型卡要求 `HuginnDynamicCache`，否则后调用覆盖前迭代 K/V | **confirmed** | README L179-180 逐字："requires its own KV-cache implementation `HuginnDynamicCache`, otherwise the KV-caches of later calls to the recurrent block will overwrite the earlier ones"；`### Per-Token Adaptive Compute` 节存在（与 `[^oct-mt-huginn]` 所指节名一致） |
| **MiMo-C09** | ch8 L29 `inclusionAI/LLaDA2.X/main/LLaDA2_2_tech_report.pdf` | LLaDA2.2 在 per-token 路由**之前**限制 block 的专家池 | **confirmed** | PDF 实抓（702,354 B，与 pin 字节同）：§2.2 "fixed-capacity block-level expert pool"、"forming a fixed-capacity expert pool P. In our default setting, **C = 48**"、"token-wise routing **inside the admitted expert pool**" |
| **MiMo-C10** | ch8 L79 DS-V4.1-Flash `resolve/main/…pdf` | 架构在 prefill/decode 激活不同路径（phase-dependent） | **confirmed** | PDF 实抓（1,809,802 B，与 pin 同）："…only 8B parameters during prefill"、"16B during decode"、"CSA2 Reuse Mode … 15 kernels during prefill and 11 during decode"、CED "compute only the first half of the layers during the prefill" |
| **MiMo-C11** | ch8 L237 Wan `blob/main/transformer/config.json` | hidden 3,072 / 30 层 / 24 heads（VAE 48 通道、patch (1,2,2)） | **confirmed** | config：`num_attention_heads=24`、`num_layers=30`、`attention_head_dim=128` → 24×128=**3072**（实算）、`in_channels=48`、`patch_size=[1,2,2]` ✓ |
| **MiMo-C12** | ch9 L175 torch-ccl `master` README | README 声明项目已归档/弃用并指向 PyTorch | **confirmed（内容）**，但引用本身是 moving `master` | README 首行 "## THIS PROJECT IS ARCHIVED"、"**DEPRECATED**. Please use PyTorch directly for distributed scenarios" ✓；HTTP 200 |
| **MiMo-C13** | ch9 L187 gloo `main` README | "Gloo 既是通信库**也是框架 backend 名**" | **mismatch（后半句所引源不支持）** | README 全文 **0 次** "backend"；仅 "Collective communications library with various primitives for multi-machine training"。前半句 confirmed；"framework backend 名" 属常识性正确但**该引用未载**（PyTorch 文档才载） |

## 3. 2026-10-28 增补出处显式性

| ID | 引用 | 主张 | 判定 | 证据 |
|---|---|---|---|---|
| **MiMo-C14** | ch27 L3/L5/L151-153/L157/L212/L226/L236/L262；ch8 L42；A.10 L367；ch19 L182 | 增补为**独立日期的后快照附录**，非 8 月刷新 | **confirmed** | 逐行实读：L153 含读者可见句 "Sources inspected 28 October 2026 as part of this separately dated addendum, **not a refresh of the August comparison tables**"（ch19 L182 同句已在用）；L5 "hard boundary… **not a current model leaderboard**"；L212 "not support at the August cutoff. No backend performance was measured"；L226/L236/L262 边界句齐。计数与台账 §8 一致：`retrieved 2026-10-28`=**23**、`2026-10-28`=**34**、`[1P]`=**36**、`[2°]`=**4**。**未发现**任何把 10 月材料表述为 8 月刷新的句子 |

## 4. 钉死 commit 抽样 + 数字对源

| ID | 引用 | 主张 | 判定 | 证据 |
|---|---|---|---|---|
| **MiMo-C15** | 抽样 18 条 pinned URL（A-S01/13/14/15/17/20/23/26/27/28/37/43/44/47/48/54/78/103 代表）+ 8 个 GitHub pin | 台账 §2 "every pin re-fetched 200" | **confirmed** | 18/18 HTTP **200**（2026-10-31）；GitHub commits API 8/8 存在且 committer 日期**全部 ≤ 2026-10-28**（Dream 2025-11-21、LLaDA 2026-07-15、Qwen 2026-08-27、Hunyuan 2026-04-10、Flash-dLLM 2026-10-07、transformers 2026-10-22、LLaDA2.X 2026-07-22、GLM-5 2026-10-15）；vLLM `41dd82e6…`（ch27 L214）存在，2026-10-28T06:31Z |
| **MiMo-C16** | A-S01 钉死 Qwen3.8-Flash-Next `tech_report.pdf`（ch27 L69/L71） | 125B/6B、51B n-gram 脱存主机、GDN+QSA(micro-block)、Gated Residual、Muon+AdamW、训练成本 ~1/9 Qwen3.7-Plus | **confirmed**（vendor report） | PDF 实抓 200：摘要逐项命中（"125B parameters, 6B activated… additional 51B… held off the accelerator"、"tables are prefetched from host memory"、"micro-block granularity"、"Gated Residual"、"Muon"、"AdamW"、"to Qwen3.7-Plus at roughly **a ninth of the training cost**"）。**注意**：`262K/YaRN`、`512 experts`、`10 routed + 1 shared` **不在 tech report 内**，而在 HF **model card**（"Context Length: 262,144… e.g., YaRN"、"Number of Experts: 512"、"Number of Activated Experts: **10 Routed + 1 Shared**"）；L69 抬头同时点名 HF 与 GitHub 两源 → 引用充分，但钉死的正文链接（report）并不含这三项 |
| **MiMo-C17** | A-S02 Z.ai 发布文（ch27 L75） | 3.0× 更低 attention compute、4.4× 更小 KV cache（per head per layer / 每层 BF16 均值，对比 GLM-5.3）；320B/18B；首个原生多模态；1M 原生上下文 | **confirmed**（vendor；经浏览器渲染取回正文） | 直抓仅 604 B SPA 壳 → 改用浏览器渲染（13,552 字符）：逐字命中 "attention compute per head per layer and average KV cache size per layer (BF16). Compared with GLM-5.3, GLM-5.3-Flash uses **3.0×** less attention compute and a **4.4×** smaller KV cache"、"first natively multimodal… **320B** total parameters and just **18B** active"；1M 由 config `text_config.max_position_embeddings=1048576` 佐证。**口径限定（per-head/per-layer、非整机）在稿内已如实保留** ✓ |
| **MiMo-C18** | ch27 L75 "…, **131 K output**" | GLM-5.3-Flash 输出上限 131K | **unverified** | 渲染后发布文全文无 "131"；HF card / config.json / generation_config.json / GLM-5 README / HF meta 本地归档逐一 grep **无 131/131072**。数字可能对，但**所引各源均未载** → 引用-主张缺口（建议补源或删数） |
| **MiMo-C19** | ch9 L129 Gaudi 3 白皮书 | 24 × 200 Gb/s 端口 → 600 GB/s 单向 / 1,200 GB/s 双向（标 derived nominal） | **confirmed**（vendor + 本书算术） | 白皮书 PDF 200： "**24 x 200G Eth Ports**"、"200Gb/s Bi-Directional"、正文 "1200 GB/s"；实算 24×200/8=**600**、×2=**1200** ✓；稿内明写 "neither is an achieved all-reduce bandwidth" ✓ |
| **MiMo-C20** | A-S27 钉死 `zai-org/GLM-5/…README.md` | 脚注称 "GLM-5.3 & GLM-5.3-Flash" | **confirmed** | 钉死 README 200，L18 章 `### GLM-5.3 & GLM-5.3-Flash`，与 `[^oct-mt-glm]` 所指节名一致 |

## 5. 错配 / 误标 / 快照当现状 扫描

| ID | 对象 | 判定 | 证据 |
|---|---|---|---|
| **MiMo-C21** | ch27/ch8/ch9 全部 "measured" 出现处 | **confirmed clean（无基准被标为实测）** | 逐处语境均为否定/限定："do not… establish locally measured performance"(L153)、"vendor-reported rather than re-measured here"(ch8 L27)、"not a measured timing scale / throughput / latency"(ch8 L57/163/169)、"analytical comparisons, **not measured NCCL results**"(ch9 L62)、"**No curve is measured performance**"(ch9 L64)。`[^oct-ix-60]` 第三方基准标 `[2°]` 且明写 "book has not reproduced its measurements" ✓ |
| **MiMo-C22** | 2026-08 快照是否被当现状 | **confirmed clean** | L5 明写硬边界 + "not a current model leaderboard"；A.10 L367 "Compiled 2026-08-30… vendor-reported [1P]"；ch8 L42 "observations: 2026-10-28… do not establish feature availability at the edition's 2026-08-30 cutoff"；ch9 表 9-3 标 "(2026-10-28 snapshot)"。**未发现** 8 月数值以"当前"口吻陈述 |
| **MiMo-C23** | 台账 A-S02 行 "Content check ≡ archived 2026-10-28 bytes" | **mismatch（内容核验为空壳，表述误导）** | 仓库归档 `sources/glm-report.txt` = **604 B SPA 壳**（`glm-report.clean.md` = **0 B**），sha256 相符故"≡"字节为真，但**归档内无文章正文** → 该行"内容一致"对本条无信息量。发布文主张现仅能靠 JS 渲染核验（本轮已做，见 C17） |

---

## 汇总

- **confirmed**：C01, C02, C03, C06, C07, C08, C09, C10, C11, C12, C14, C15, C16, C17, C19, C20, C21, C22
- **mismatch**：C04（"no archived copy" 忽略 Wayback 快照）、C05（ch9 moving 清单漏 3 条）、C13（gloo "backend 名" 所引源不载）、C23（A-S02 内容核验为空壳）
- **unverified**：C18（"131 K output" 各引各源均无此数）
- **inaccessible**：无（本轮所有目标 URL 均可达；z.ai 需 JS 渲染已绕过）
- **证据分级**：全部数字类主张为 **vendor-assertion [1P]** 或本书 **[DERIVED] 算术**；第三方仅 `[2°]` 两条（A-S94/95，标记正确）；**author-measured = 0**，与稿内自述一致。
- **对 R10 的净结论**：台账主体（105 条、22 pin、RED→GREEN）经抽样复核成立；需修 4 处表述/清单（C04/C05/C13/C23）与 1 处缺源数字（C18），均不推翻 R10 结论。