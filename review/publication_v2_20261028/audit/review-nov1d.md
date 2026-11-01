# FTF-nov1d — 2026-11-01 4 项已核实 P1 的修复证据（Table 17-2 floor 错误 + u-only/u×ρ 政策标注）

- **范围**：仅 `design/manuscript/` 3 个文件（chapter-17 / chapter-08 / chapter-13）+ 本证据文件 + `review-nov1d.diff`。
- **未做**：未改 renderer/根文件、未改 `render/check_regressions.py`（见 §5 OPEN）、无全书 build、无 git、未动 `review/.../work/*` 内的历史 proof 副本（非权威源）。
- **备份**：`~/.hermes/profiles/muta/cache/scratch/nov1d/before/`（3 份修复前原件 + `sha_before.json`）。
- **完整 diff**：`review/publication_v2_20261028/audit/review-nov1d.diff`（`diff -u` 字节精确，8 处替换 = 8 `-`/`+` 行对）。

**采用政策（与 Ch4/Ch17 Table 17-1 一致）**：u=0.70 与 ρ=0.95 **独立**，u×ρ=0.665；N = ⌈λ·W/(C·u·ρ)⌉ + N_spare 为**答案值**；保留的 u-only（ρ=1）数字一律标注为 `ρ = 1 u-only screen` 下界对照。

## SHA-256（before → after）

| 文件 | before | after |
|---|---|---|
| chapter-17/chapter-17.md | `3d7a3fbe43dc110ab5417b09bf6c072968ae05f9ffe277ea4329240ae7a621c5` | `ccc7accbb3a398b0a1b109d8655292bd8ac0a69f85365acbad625751d1b8ef43` |
| chapter-08/chapter-08.md | `259593b68991b66a882d69359b1a3b55a62435bdddf3f36db8dedf13e5d05656` | `fc271ba7a4979372e86d220964418fc12908bb641d0c5c6ef57b99a52e08635c` |
| chapter-13/chapter-13.md | `beb3b359d5ab40834df88da962fd5bc5549a35e35ef656fe6b35284aec0be38d` | `b8a885fd6dd12849506a570aaadf202bb600b008a4898bc61feedac4cb64b5e7` |

## 1. P1-(1) Table 17-2 floor 错误（ch17 L271）— FIXED

- **Before**：`| 200 rps (2× growth) | 1,720 | 2,760 | ⌈1720/11.305⌉ ≈ 153 | ⌈2760/8.645⌉ ≈ 319 | ⌈2760/17.955⌉ ≈ 154 |`
- **After**：同上，仅 `319` → `320`。
- **复算**：2760 ÷ 8.645 = 319.25968768… → **⌈·⌉ = 320**（319 是取 floor 的错值；nov1c 证据文件中"319.26 → 319"的括注同样误用了 floor，本文件予以更正记录，nov1c 历史证据不改）。
- **同表其余格全量复算（u×ρ 分母 11.305 / 8.645 / 17.955）**：40 rps → 31 / 64 / 31；100 rps → 77 / 160 / 77；200 rps → 153 / **320** / 154；N−1 行（40 rps）→ 32 / 65 / 32。全部与表内一致 ✓（仅 319 一格错）。

## 2. P1-(2) Ch8 30/33 → 32/34（ch8 L179、L181）— FIXED

- **L179 Before**：`… and 30 (KV-only) / 33 (case (ii)) at the 70% + N−1 policy, Ch 16/17 — are …`
- **L179 After**：`… and 32 (KV-only) / 34 (case (ii)) at the 70% × 95% + N−1 policy, Ch 16/17 (the ρ = 1 u-only screen reads 30 / 33) — are …`
- **L181 Before**：`(19 / 21 / 22, and 30 / 33 at the 70% + N−1 policy)`
- **L181 After**：`(19 / 21 / 22, and 32 / 34 at the 70% × 95% + N−1 policy — 30 / 33 on the ρ = 1 u-only screen)`
- **复算**：KV-only u×ρ：⌈344/11.305⌉ = ⌈30.429⌉ = 31，+1 = **32**；case(ii)：⌈21.81/0.665⌉ = ⌈32.797⌉ = 33，+1 = **34**。u-only 对照：⌈344/11.9⌉+1 = 29+1 = **30**；⌈21.81/0.7⌉+1 = 32+1 = **33** ✓。与 Ch16 L165（32/34）、Ch17 表注（⌈21.81/0.665⌉+1 = 34、KV-only 32）逐字一致。
- **Ch8 全章 host 数一致性核查**：~5（10 rps 原始比值，标 idealized）✓；19/21/22（35% MFU 计算屏，按 case 标注，与 Ch17 表注同口径）✓；`⌈344/17⌉ = 21`（u=1 满利用率屏）**已补注** `the full-utilization screen; 31 working / 32 total at the 70% × 95% policy`（对齐 Ch17 L27/L123 自身写法）；L65 `~21 hosts (Ch 17's floor-17 screen)` **已补注** 同样的 full-utilization + 31/32 政策对；21/22 台成本数字为 Ch16 既有 included-cost，未动 ✓。全章已无未标注的 u-only 政策值。

## 3. P1-(3) Ch17 §17.8 FP16 散文 152（ch17 L253）— FIXED

- **Before**：`… conservative integer floor 13), N = ⌈1,380/(13 ×0.7)⌉ ≈ **152 hosts** on FP16 KV (≈107 at full utilization).`
- **After**：`… conservative integer floor 13), N ≈ ⌈1,380/(13 × 0.70 × 0.95)⌉ = ⌈1,380/8.645⌉ = ⌈159.63⌉ ≈ **160 hosts** on FP16 KV at the Table 17-1 policy (the ρ = 1 u-only screen reads ⌈1,380/(13 ×0.7)⌉ ≈ 152; ≈107 at full utilization).`
- **复算**：1380 ÷ 8.645 = 159.6298… → **160**（= Table 17-2 同格 ✓，冲突消除）；u-only：1380 ÷ 9.1 = 151.65 → 152 ✓；满利用率：1380 ÷ 13 = 106.15 → 107 ✓。原句全部数字/推导（152、107、⌈1,380/(13 ×0.7)⌉）保留，仅改口径次序。
- **FP8 散文（L255/L257）核查**：本就携带同一约定 —— `⌈1,380/17.955⌉ = ⌈76.86⌉ ≈ 77 working hosts at the Table 17-1 policy (the u-only screen would read 74; ≈52 at full utilization)`、Decision `77 working + 1 spare: 78 total (u-only variant 74 + 1 = 75)`、occupancy 66%（u-only 74 台 69% 对照）—— **未改**，FP16/FP8 现已同构 ✓。

## 4. P1-(4) Ch13 73+1=74（ch13 L53、L106）— FIXED

- **L53 Before**：`… gives 73 working + 1 spare = **74 hosts** — not a handful.`
- **L53 After**：`… gives 73 working + 1 spare = **74 hosts** on the ρ = 1 u-only screen — 77 working + 1 spare = **78 hosts** at the Table 17-1 policy (u × ρ = 0.665; ⌈860/11.305⌉ = ⌈76.07⌉ = 77) — not a handful.`
- **L106 Before**：`— 73 working + 1 spare = **74 hosts** at Ch17's 70% target and N−1 rule — a real cluster … adds the 70% headroom and the spare host`
- **L106 After**：`— 73 working + 1 spare = **74 hosts** at Ch17's 70% target and N−1 rule on the ρ = 1 u-only screen, or 77 working + 1 spare = **78 hosts** at the Table 17-1 policy (u × ρ = 0.665) — a real cluster … adds the 70% × 95% headroom and the spare host`
- **复算**：u-only：⌈860/11.9⌉ = ⌈72.27⌉ = 73，+1 = 74 ✓（保留为下界对照）；u×ρ：⌈860/11.305⌉ = ⌈76.07⌉ = **77**，+1 = **78** ✓；满利用率 ⌈860/17⌉ = ⌈50.59⌉ = 51 ✓（原句保留）。L106 尾句 `70% headroom` → `70% × 95% headroom`（Table 17-1 政策口径，纯增补限定词）。
- **Ch13 其余 host 数核查**：L41 `~21 hosts at the 40 rps peak`（u=1 满利用率屏）**已补注** `on the full-utilization screen — 31 working / 32 total at the 70% × 95% policy`（= Ch17 L27 原句口径；⌈344/17⌉ = 20.24 → 21、政策 31+1=32 复算 ✓）；L82 `~21 hosts per Ch17` 为反面教材短引、直接归因 Ch17（Ch17 源句自带 31/32 政策对），判定**无需再标注**，未改；`51 hosts at full utilization` 已自带口径 ✓；`~100 ÷ 2.0 ≈ 50` 为明确标 naive 的对照 ✓。

## 5. OPEN — `check_regressions.host()` 覆盖缺口（按指示只报告、不改文件）

`render/check_regressions.py` L57-64：`def host(lam, w, c_floor, util=0.70)` —— **只有 u、无 ρ 参数**，6 条断言全部是 u-only 值：`29 / 73 / 145 / 61 / 152 / 304`（40/100/200 rps × T0/T3）。因此它**无法验证**本书已采纳的 u×ρ 政策值（31/32、77/78、160、320 等），也无法捕捉本次修掉的 `319` 类 floor 错误（`host(2760,1,13)==304` 是 u-only 口径，与表内 320 不冲突也不校验它）。本次**未改该文件**（改 `util=0.665` 会使 6 条既有断言全红，属破坏性变更）。实测：`python3 render/check_regressions.py` → exit 0，`OK - all numeric regression checks passed.`（改动前后均通过，因脚本不读手稿）。**建议（OPEN）**：为 `host()` 增加 `rho=0.95` 参数或新增 `host_policy()` 断言组，覆盖 31/64/77/160/153/320/154/32/65 与 32/34、78 等政策值 —— 需脚本所有者批准后另行提交。

## 6. 验证汇总

- 10 处替换全部 `count==1` 精确命中；残留扫描：`⌈2760/8.645⌉ ≈ 319`、`30 (KV-only) / 33 … 70% + N−1`、`30 / 33 at the 70% + N−1`、`= **74 hosts** — not a handful`、`adds the 70% headroom` 在 3 章中出现次数均为 **0**；新字符串各恰好 1 次。
- 三章内剩余的唯一 u-only ceil 公式即 ch17 已标注的 `⌈1,380/(13 ×0.7)⌉`（带 `ρ = 1 u-only screen reads` 标签）。
- 全部相关数字已按第一性原理复算（见 §1–§4），无一处依赖记忆。
- **无 OPEN 项**（除 §5 覆盖缺口为报告性 OPEN）：4 个 P1 全部验证并修复。