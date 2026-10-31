# P2/P3 剩余发现修复审计证据（2026-10-30）

范围：仅改动受影响的 chapter-*.md（Ch4/9/16/19/22/23）+ 本审计证据。未动其他章节、渲染器、根目录；未做全书构建 / git 提交 / 委派。
方法：每项先重算，再改；保留 [ILLUSTRATIVE]/[DERIVED]/provenance 与其余数值。

## 文件 sha256（改后）
- chapter-04/chapter-04.md: 956544676f6db88ba1a4b43b4804cebd3a6f32c5347df8c730d25d3c76c94385
- chapter-09/chapter-09.md: d52f0edc8c555ac5751babb447811b2a2bafb23324c53b7445833120cb7cac35
- chapter-16/chapter-16.md: 0cbb7c38782ec418c811f8b4341d702d066685581f0d5f4ab1f51cbbc1361144
- chapter-19/chapter-19.md: cfb9c53e4a85a30bee15152a9f8803593cdf9b31b37382e0debcdb880ed6ba48
- chapter-22/chapter-22.md: 83683ee7be1d783e15e45d49965aefdc29c5cb375efd55d903c56273c41dacb9
- chapter-23/chapter-23.md: b2c5d345bb8987479c5b64fb28bfa4874830ad7bae4a550a4bd0f13f4d90002c

---

## FTF-N08（Ch22）10/40 rps 溯源措辞不一致
- 重算/判定：Ch4（canonical 场景章）把 10/40 rps 定为「declared, not derived」的 [canonical scenario][ASSUMPTION] 流量输入；Ch22 原句误标为「derived quantities [ILLUSTRATIVE][DERIVED], not stipulated」。真溯源 = 声明（stipulated/declared），非派生。
- 前：`These are derived quantities [ILLUSTRATIVE][DERIVED], not stipulated.`
- 后：`These are declared traffic inputs [canonical scenario][ASSUMPTION], not derived from the user population (walk-through in Ch 4 §4.3).`
- 数值不变（~10 rps / ~40 rps）。Ch22 其余「derived quantities」均指 token 吞吐/KV/prefill FLOPs/decode BW 等真实派生量，未动。

## FTF-N09（Ch23）Table 23-1 成本行未在对话中确立
- 判定：对话原只确立 5 个 bound（traffic/tokens/SLO/quality/ops）；architect 问了成本（line 52）但 lead 只答了数据敏感（line 53），成本行「within self-host budget」被当作对话产出，违反本章 coverage 规则（六数齐备）。
- 修复方式：在对话中确立成本（而非标为假设），使 worked example 完整演示六数提取。
- 前（lead 答）：`"It's internal and regulated; keep it on-prem if at all possible."`
- 后（lead 答）：`"It's internal and regulated; keep it on-prem if at all possible. And at this scale we'd rather not pay per-token API fees — keep it within a self-host budget."`
- 新增：`**→ Bound 6: cost ceiling — within a self-host budget (Ch16).** [canonical scenario] (Ch 4, Table 4-2)`
- 镜像复述（line 56）补入成本：`...fully on-prem because it's regulated, and within a self-host budget. Have I captured it?`
- 结果：对话现含 Bound 1–6 共 6 个，与「six numbers / six bounds」框架及 Table 23-1 成本行一致。

## D3（Ch19）W(3) 取整不透明（13.854 vs 13.8）
- 重算：W(3) = 1.08 + 0.025×495 + 3×0.133 = 1.08 + 12.375 + 0.399 = **13.854 s**（四舍五入 13.9）。表列 13.8 是 Ch17 声明的下界（prefill 固定在 canonical 9.2K 代表值 1.08 s，未按 12,095-token 上下文放大；放大则 prefill≈1.42 s、W≈14.2 s）。
- 修复：表脚注（line 291）显式给出精确 13.854、下界约定与 prefill 固定 1.08 s。
- 前：`**Full agentic service time W** = Ch 17 §8's grown-context prefill + decode of all generated tokens + tool leg (~13.8 s at T = 3, a lower bound) — the row that sets concurrency and fleet size.`
- 后：`**Full agentic service time W** = Ch 17 §8's prefill + decode of all generated tokens + tool leg, with the prefill **held at the canonical 1.08 s** (the 9.2K representative) rather than scaled to the grown I(T) — so W(3) = 1.08 + 0.025×495 + 3×0.133 = **13.854 s** (rounds to 13.9 s); the table reports **13.8 s**, Chapter 17's stated lower bound (scaling the prefill to the 12,095-token context would give ~1.42 s and W ≈ 14.2 s). This is the row that sets concurrency and fleet size.`
- 表内 W 行数值（~10.3/~12.1/~13.8/~15.6）保持不变。

## D4（Ch19）公式 T_prefill(I(T)) 与表用 held-1.08 不一致
- 重算：按 grown prefill（1.08×I(T)/9,200）算 W(T)≈{10.4,12.3,14.2,16.0}；表用 held-1.08 得 {10.3,12.1,13.854,15.6}。二者差异源于 prefill 是否随 I(T) 放大。
- 修复：与 D3 合并，在表脚注显式声明「表内 W 行 prefill 固定在 canonical 1.08 s，未按 grown I(T) 放大」，使公式（通用形式）与表（held-1.08 取值）一致透明。
- 无独立数值改动（见 D3 前后）。

## D6（Ch19）α(T=2) 正文 1.12× vs 表 1.18×
- 重算：§3 手工 trace（tool 输出 800+350=1,150）→ 10,650/9,500 = **1.121 ≈ 1.12×**；per-turn 约定（δ=800+γ=65/turn）→ (9,500+2×865)/9,500 = 11,230/9,500 = **1.182 ≈ 1.18×**（Table 19-1 T=2 列）。两者各自正确，属不同约定，非矛盾。
- 前：`- Amplification factor: 10,650 / 9,500 ≈ 1.12×`
- 后：`- Amplification factor: 10,650 / 9,500 ≈ 1.12× (this specific hand-worked trace, tool outputs 800 + 350; the per-turn convention of §4/Table 19-1 — δ=800 + γ=65 per turn — gives α(T=2) = (9,500 + 2×865)/9,500 = 11,230/9,500 ≈ 1.18× — different conventions, not a discrepancy)`

## D2（Ch16）29×1.9767×0.70 取整
- 重算：29 × 1.9767 × 0.70 = **40.127** → 40.1（原文 40.2）。40.1 ≥ 40 rps 结论仍成立。
- 前：`29 surviving × 1.9767 × 0.70 ≈ 40.2 ≥ 40 rps`
- 后：`29 surviving × 1.9767 × 0.70 ≈ 40.1 ≥ 40 rps`

## D5（Ch4）prefill 下界 460,000/19,800
- 重算：460,000 ÷ 19,800 = **23.23** → 取整到整台主机 = **24**（23 台仅 455,400 tok/s < 460,000）。
- 前：`≈ **~23 hosts**.`
- 后：`≈ **~24 hosts** (460,000 ÷ 19,800 = 23.23, ceiled to a whole host).`
- 逻辑不变：prefill 下界（~24）仍低于 KV 约束（~26 full-util / ~37 @70%），KV 仍为主导。

## D7（Ch9）56,000 s 换算小时
- 重算：56,000 ÷ 3,600 = **15.556 h** → 15.6（原文 15.5）。
- 前：`~56,000 s (15.5 hours)`
- 后：`~56,000 s (15.6 hours)`

---

## 结论
8 项全部重算并修复，无 OPEN 项；未改动任何 [ILLUSTRATIVE]/[DERIVED]/provenance 标签语义（N08 为纠正误标溯源，N09 为补全对话以符合本章 coverage 规则），其余数值与标签保留。
