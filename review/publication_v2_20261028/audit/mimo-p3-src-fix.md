# MiMo P3 + 源文核验修复 — R30 后续（本轮实证）

- 日期：2026-10-31 (UTC-07)；对象：`mimo-arithmetic-r30.md`（MiMo-0001）、`mimo-discovery-r30.md`（MiMo-2003…2007）、`mimo-source-verification.md`（C04/C05/C13/C18/C23）
- 方法：每条先独立复算/实测（Python 复算、curl/Wayback API/HF API、逐节 grep 回验），确认后才改；改后逐串 grep 复验在位
- 边界：只改 7 个 chapter-*.md + `audit/source-verification.md` 台账 + 本文件；无 renderer/根文件改动、无 build、无 git、无委派
- 结论：**11/11 已处置（10 FIXED + 1 FIXED-源文侧/渲染复验顺延）**，0 个猜测值，其余数字全部保留

## 0. SHA256（before → after）

| 文件 | before | after |
|---|---|---|
| design/manuscript/chapter-15/chapter-15.md | `cbcfcf7d039a32f1…41582ed` | `e1dbfaedd0d892a8…c1fa757d` |
| design/manuscript/chapter-19/chapter-19.md | `cfb9c53e4a85a30b…d6ba48` | `95781134a1a60ecc…5f7c4ac2` |
| design/manuscript/chapter-05/chapter-05.md | `3d2c2604784c2d31…23b7116` | `0b97968d4e177d95…46a6ff8f5` |
| design/manuscript/chapter-06/chapter-06.md | `4ad061640747875b…e903d51` | `4bbece1a36898df8…cc900d8a9` |
| design/manuscript/chapter-20/chapter-20.md | `0d81b19586b8204f…6ff20843` | `fa00790a272ba373…feafe16e1` |
| design/manuscript/chapter-09/chapter-09.md | `d52f0edc8c555ac5…0cb7cac35` | `ec62facd12c03066…74cfd90d` |
| design/manuscript/chapter-27/chapter-27.md | `b0448a468024336f…9fa8082` | `41571b3e636f3841…71e641fb` |
| review/…/audit/source-verification.md | `c4fb1bf00c604244…135f2973` | `5d0afeb8abb3037f…1a8a345e8` |

（完整 64 位串见仓库内 `sha256sum` 复跑；before 串存于 scratch `mimo_p3_before.sha`。）

## 1. MiMo-0001 — Ch15 §15.10 mini-case MFU — FIXED

- **复算（改前）**：70,000 tok/s × 2×70×10⁹ = 9.8×10¹⁵ FLOP/s；单机峰 8×989 TFLOPS = 7.912×10¹⁵ → 单机 123.9 %（与 §6「~124 % one-host」逐位一致，§6 原文实读在位）；双机 9.8/15.82 = **61.94 % ≈ 62 %**；等价 35,000/56,500 = 61.95 %。38 % 反推需 ≈42,800 tok/s，与 70,000 矛盾；38 恰为 Table 15-1「Typical」拥塞标签（双义确认）。
- **diff**：`The MFU stabilizes at 38 %.` → `The MFU stabilizes at ~62 % — 70,000 tok/s × 2 × 70×10⁹ FLOP/token = 9.8 ×10¹⁵ FLOP/s against the two-host 15.82 ×10¹⁵ FLOP/s peak (half of the ~124 % one-host figure in §6); the 38 % in Table 15-1 is that table's congestion label, not an MFU.`
- 其余数字（8,000/70,000/35,000/26/37/21、Table 15-1 的 12/38/52）全部未动；全书 grep 无其他「stabilizes at 38」引用。

## 2. MiMo-2003 — Ch19 §19.3 → §19.6 — FIXED

- **回验**：`billable` 全章仅 2 处 — §6（源文 L196 `## 6. Architecture Consequence`，L200 定义句「billable tokens / KV-resident tokens」）与被修的引用句本身；§3（Worked Example）无 `billable`。Ch19 仅首节无号，源 6 = 渲染 19.6（discovery 已证 Ch19 源↔PDF 一致）。
- **diff**：`(see the billable-vs-KV-resident distinction in §19.3)` → `… §19.6)`。全书无其他 `§19.3/§19.6` 交叉引用。

## 3. MiMo-2004 — Fig 5.1 图注 §5.4 — FIXED（删错引，不改主张）

- **回验**：§5.4 Measurement（L125-133）三条 = token 拆分/输出长度/p95 上下文，无 gate、无 target corpus；`target corpus` 全章仅出现在图注自身（L188）。**注意：audit 建议改指 §5.3 的「must be validated on the target corpus」——本轮 grep 证实该句在 Ch5 不存在**（§5.3 内只有 1M-chunk corpus 等），故不采用该改指，改为删去错引、保留自足主张。
- **diff**：`those gates are measured on the target corpus (§5.4) and are not shown here` → `… on the target corpus and are not shown here`。五道 gate 清单、其余图注文字未动。

## 4. MiMo-2005 — Ch6 p99 ≈ 1.33 s — FIXED（诚实重述）

- **复算（改前）**：σ 由 p95=0.99 反解 = 0.12955（p90 复算 0.9445 ≈ 0.94 ✓）；对数正态主体 p99 = 0.8·e^(2.3263σ) = **1.081 s**；混合分布总体 p99：x<5 时 F(x)=0.99·G(x)<0.99 ⇒ **总体 p99 = 5.0 s**；1.33 s 只能是 N=10,000 线性插值落在最大非离群抽样的刀口值（101/10,000 即翻到 5.0）。
- **diff（关键句）**：`… and p99 ≈ 1.33 s.` → `… and p99 ≈ 1.33 s — a knife-edge property of *this* N = 10,000 sample, not of the distribution: linear interpolation lands on the largest non-straggler draw, while the population p99 of the stated 99 % log-normal + 1 % straggler mixture is 5.0 s (one extra straggler, 101 of 10,000, moves the sample p99 to 5.0 s too).`；`**even p99 (≈ 1.33 s) still looks healthy.**` → `**even this sample's p99 (≈ 1.33 s) still looks healthy — the population p99 is 5.0 s, sitting on the straggler cluster.**`；`they sit *between*… so a p99 line alone` → `in this sample they sit … so the interpolated p99 line alone`。
- 保留：0.80/0.94/0.99/1.33/5.0/0.84、Fig 6.2 图注、尾部论点（p99.9/max 才见离群）；未把 1.33 冒充「in-distribution lognormal 值」（那是 1.08，audit 口径二在此不成立，故采用口径一 + 刀口说明）。

## 5. MiMo-2006 — Ch20 §8 括注 — FIXED

- **回验**：同章 §3（L49）原文在位：「the two views are *the same identity*, λW/C = λ/(C/W)」+「The "far fewer hosts (~6)" figure applies only to the 10-rps average (⌈86/17⌉ = 6), not the 40-rps peak」。
- **diff**：`(The KV-residency bound, Chapter 17, needs far fewer — ⌈86/17⌉ = 6 at the 10-rps average — but the throughput/latency bound binds here, so the larger requirement governs.)` → `(⌈86/17⌉ = 6 is not a second, tighter constraint: it is the *same* identity λW/C = λ/(C/W) — the KV-residency view of §3 — evaluated at the 10-rps average instead of the 40-rps peak; at the peak both views give ⌈344/17⌉ = 21 (→ 22 with the ρ ≈ 0.95 derate), so the peak requirement governs.)`
- 数字 6/21/22/16.15 全保留；归因由「界别之差」改为「均值 vs 峰值」。

## 6. MiMo-2007 — Ch15 源↔PDF 节号 — FIXED（源文侧；渲染复验顺延）

- **回验**：Ch15 三个无号 `##`（L3 Architect's Question、L52 Optimization Decision Map、L70 Two Mechanisms）；源 `## 5..8.` 渲染为 15.7–15.10（后两个无号节吃掉 15.5/15.6）。全书 grep `§15\.` / `15.10` / `15.7` 交叉引用 **0 命中**（改号不断链）；`{.unnumbered}` 为本书既有惯例（ch9/ch18/ch27 共 12 处，ch27 A 节已由 discovery 验证渲染生效）。
- **diff**：三个标题各加 `{.unnumbered}`（`## The Architect's Question` → `## The Architect's Question {.unnumbered}`，另两个同）。预期渲染：源 5–8 → 15.5–15.8，源号=渲染号；§6（124 % 注）渲染号由 15.8 变 15.6，恰好使 `mimo-arithmetic-r30.md` 里「§15.6」的引用转为正确。
- **顺延（非 OPEN 的猜测项）**：PDF 重渲染核验需全书 build，本轮边界禁止 → 留待下一次 build 验证 15.5–15.8 生效。

## 7. MiMo-C04 — 2 条 Habana UNVERIFIED → SNAPSHOT-PINNED — FIXED

- **实测（改前）**：Wayback API 两 URL 均有快照 `20260926170046` / `20260926170113`（status 200，HCCL 快照实抓 200）；live 页自述 **Gaudi Documentation 1.24.2**（实抓命中 ×2），live 200；`/en/1.24.2/`、`/en/1.20.0/` 404（无版本路径，仍无 commit pin）。
- **diff（台账）**：§3 标题 `UNVERIFIED — …` → `SNAPSHOT-PINNED — moving ref, no commit; Wayback snapshot (upgraded from UNVERIFIED per MiMo-C04)`；两行 Status → `SNAPSHOT-PINNED - Wayback 2026-09-26 (20260926170046/20260926170113)`，Why 补快照 URL 200 + 版本 1.24.2；§4 A-S88/A-S92 行 Status/Revision/Content check 同步；Totals `2 UNVERIFIED` → `2 SNAPSHOT-PINNED (… previously recorded UNVERIFIED — MiMo-C04)`；§5 脚注负载句、§10 附录行同步；R3 规则补「有不可变第三方快照时升级 SNAPSHOT-PINNED」。
- 手稿脚注 `[^oct-ix-47]/[^oct-ix-55]` 未动（本就无 UNVERIFIED 字样，URL 照印，pin 落在证据层）。

## 8. MiMo-C05 — ch9 moving 清单 2 → 5 — FIXED

- **实测**：ch9 moving refs 实为 5：habana `/latest/`(L129)、gloo `/main/`(L187)、torch-ccl `/master/`(L175)、rccl `/develop/`(L187)、ucc `/master/`(L187)；与 audit 一致。
- **diff（台账 §10）**：`chapter-09/chapter-09.md: 2 — …` → `: 5 — …`（补 3 条 branch URL），并注明根因（R1 枚举只认 `main/latest/…`，漏 `master/develop`）+ 评估：5/5 HTTP 200（2026-10-31，与 C06 一致），**仍 unpinned、有静默漂移风险**（A-S15 已示范 3 天漂移）→ 保持 out-of-scope 记录，不在此轮 pin。

## 9. MiMo-C13 — gloo README 无 "backend" — FIXED

- **实测**：gloo `main` README 实抓 `grep -c backend` = **0**；PyTorch v2.9.0 `docs/source/distributed.md` 实抓 200、`gloo` 命中 20 处（含 backend 表、"Gloo backend"）。
- **diff（手稿 ch9 L187）**：`and Gloo is both a communication library and a framework backend name ([Gloo README](…gloo/main/README.md), all retrieved 2026-10-28).` → 拆成两半各配其源：`… a communication library ([Gloo README](…)) and a framework backend name ([PyTorch distributed documentation, pinned to v2.9.0](…pytorch/v2.9.0/docs/source/distributed.md), all retrieved 2026-10-28).`（新引 URL 为 tag 钉死、非 moving，且与 ch9 L175 既有 URL 同源）。
- **diff（台账 §10）**：新增一条 Claim-vs-source wording 记录（gloo README 0 次 backend、改引 v2.9.0 distributed.md）。说明：台账原文并无 gloo 主张句，故「source-verification wording」落在手稿句 + 台账留痕两处。

## 10. MiMo-C18 — GLM「131 K output」— FIXED（删数）

- **实测**：HF `zai-org/GLM-5.3-Flash` generation_config.json（无 max_new_tokens）、config.json（无 131）、README（无 131/max output）实抓复验均无此数；audit C17 渲染后的发布文全文亦无 "131"。**无可加的源 → 按任务口径删除**（不猜、不加限定语堆砌）。
- **diff（ch27 L75）**：`320 B total / 18 B activated, 1M native context, 131 K output.` → `320 B total / 18 B activated, 1M native context.`；320 B/18 B/1M/3.0×/4.4× 等其余数字全保留；全书 grep `131 K|131K` 0 残留。

## 11. MiMo-C23 — A-S02 归档为空壳 — FIXED（台账留痕）

- **diff（台账 §4 A-S02 行 Content check）**：`≡ archived 2026-10-28 bytes` → `≡ archived 2026-10-28 bytes — **but the archive is a 604 B SPA shell** (glm-report.txt 604 B, glm-report.clean.md 0 B): the byte match is true yet vacuous, no article body is archived; body-level claims verifiable only via JS render (MiMo-C23/C17).`

## 12. 复验与遗留

- 改后 grep 全绿：6 个旧串 0 残留（`MFU stabilizes at 38`、`§19.3`、`target corpus (§5.4)`、`even p99 (≈ 1.33 s)`、`needs far fewer`、`131 K output`）；新串全部在位（含 ch15 `{.unnumbered}` ×3、台账 SNAPSHOT-PINNED ×6、ch9 清单 `: 5`、604 B 注、C13 注）。
- 台账残留 `UNVERIFIED` 4 处均为规则/历史表述（R3 规则句、"upgraded from / previously recorded UNVERIFIED"），非在册状态。
- **OPEN / 顺延**：① MiMo-2007 的 PDF 渲染复验（需 build，本轮禁 build）；② `r10_check.py` 不在仓库树内（`find` 0 命中），台账所载「re-run must exit 0」本轮无法执行 — 下轮拿到脚本后复跑；③ C05 的 3 条 branch 引用仍 unpinned（本轮只修清单不 pin，pin 属 R1 范围）。
- 未动：issue-ledger.md、renderer、根文件、其余章节、任何非列示数字。