# D1 修复证据：Ch4 §4.8 50 rps 主机数 25/36 → 26/37（全槽位 ceil）

- **Finding**：D1（MEDIUM）— `audit/arithmetic-audit-r27.md` §一 D1 行；`issue-ledger.md` D1 行（IN FIX）
- **位置**：`design/manuscript/chapter-04/chapter-04.md` §4.8 mini-case（L250 推导引语 / L253 公式 / L256 两处）
- **状态**：**RED → GREEN**
- **ch4 sha256**：before `f866fa7e566ae0d97280cb590fb059ee8f98a5120d3afb8929c79b367bf22084` → after `ae7a42fde67607ee81abbe887fc785e25b2b3db41285a2ab3c7971f46fbb9dd6`
- **改动范围**：仅本章 3 行（4 处内容编辑）+ 本证据文件；无其他编辑、无全书 build、无 git 提交

## 1. RED（修复前，书中原值 = 严格复现）

| # | 位置 | 原文（RED） |
|---|------|------------|
| 1 | L250 引语 | "…i.e. **C/W ≈ 17.5 KV-resident requests ÷ 8.6 s**), the fleet **rounds to**:" |
| 2 | L253 公式 | `n_\text{hosts} = \frac{50 \text{ rps}}{2.0 \text{ req/s/host}} \approx 25 \text{ hosts}`（满载） |
| 3 | L256 | "and roughly **~36 hosts** at a 70% target utilization"；"the binding figure is the KV-residency/service-time **~25 (full util) / ~36 (70%)** result" |

原推导 = **连续商**：满载 50 ÷ (17.5/8.6) = 430/17.5 = 24.57 ≈ 25；70%：50 ÷ (2.0×0.7) = 35.71 ≈ 36 —— 直接用连续 17.5 槽定主机数，与全书整数槽位规范冲突（D1 所指）。

## 2. 规范依据（同书 whole-slot 约定）

- **Ch14**：「The analytical KV quotient C ≈ 17.5 gives at most **17 whole-context slots, not a deployable concurrency of 17.5**.」
- **Ch16**：「**Ch 17's whole-slot convention floors C to 17** first and gives 21」
- **canonical 40 rps（对照）**：⌈344/17⌉ = **21**；70%：⌈344/11.9⌉ = **29**（+N−1 = **30**）— Ch16/Ch17/Ch20 同式 `N = ⌈λ·W/(C·util)⌉`

## 3. 按声明输入复算（与 canonical 40 rps 完全同一 whole-slot ceil）

声明输入：λ = **50 rps**（declared scenario input）、W = **8.6 s**、C ≈ 17.5 → **17 whole slots**（floor）

| 量 | 式 | 值 |
|----|----|----|
| in-flight（本段已声明） | λ·W = 50 × 8.6 | **430** |
| 满载主机数 | ⌈430/17⌉ = ⌈25.294⌉ | **26**（原 25；连续 430/17.5 = 24.57） |
| 70% 主机数 | ⌈430/(17×0.7)⌉ = ⌈430/11.9⌉ = ⌈36.134⌉ | **37**（原 36；连续 430/12.25 = 35.10） |
| 对照 canonical 满载 | ⌈344/17⌉ = ⌈20.235⌉ | 21 ✓ 同式 |
| 对照 canonical 70% | ⌈344/11.9⌉ = ⌈28.908⌉（+1 = 30） | 29 ✓ 同式 |

## 4. GREEN（修复后，书中新值）

| # | 位置 | 新文（GREEN） |
|---|------|--------------|
| 1 | L250 引语 | "…i.e. **the whole-slot floor 17 KV-resident requests ÷ 8.6 s = 1.977** — C ≈ 17.5 is the analytical quotient, floored to 17 deployable whole-context slots per the book's whole-slot convention, Chapters 14/16/17), the fleet **rounds up by the same whole-slot ceiling the canonical 40 rps case uses (⌈344/17⌉ = 21)**:" |
| 2 | L253 公式 | `n_\text{hosts} = \left\lceil \frac{50 \text{ rps} \times 8.6 \text{ s}}{17 \text{ slots}} \right\rceil = \lceil 430/17 \rceil = \lceil 25.29 \rceil = 26 \text{ hosts}`（满载） |
| 3 | L256 | "and roughly **~37 hosts** at a 70% target utilization **(⌈430/(17 × 0.7)⌉ = ⌈430/11.9⌉ = ⌈36.13⌉)**"；"the binding figure is the KV-residency/service-time **~26 (full util) / ~37 (70%)** result" |

## 5. 结论方向不变（book conclusion preserved）

- 50 rps 仍需 **>21 hosts**：26 > 21 ✓（70%：37 > 29/30 ✓）
- KV 界仍主导 prefill 界：26 > ~23（460,000 ÷ 19,800 = 23.23，**未改**；其 ~23→24 属另案 D5，OPEN，不在本修复范围）✓ —— "prefill-throughput is a *lower* bound… the KV-bound dominates" 论证链不变
- 未动：50-vs-40 "separate cases, not a contradiction" 调和句、canonical ~21/~29/~30、成本段 6–21 hosts / $87.6K–$306.6K、全部 [DERIVED]/[ASSUMPTION]/provenance 标签与其余数字 ✓

## 6. 精确 diff

校验：将 4 处编辑反向回放重建 before 态，sha256 = `f866fa7e566ae0d97280cb590fb059ee8f98a5120d3afb8929c79b367bf22084`（与修复前一致）→ 下列 diff 恰为本修复的全部改动，无其他行。

```diff
--- a/design/manuscript/chapter-04/chapter-04.md
+++ b/design/manuscript/chapter-04/chapter-04.md
@@ -247,13 +247,13 @@
 
 An architect is brought into the early design of an internal Q&A platform. The stakeholder says: "We have thousands of employees who want to ask questions over our internal documents. We need it to be accurate and fast, but we don't know how many thousands or how fast is fast enough." Before any architecture can be defended, the architect does the workload characterization that this chapter walks through.
 
-From the unit-and-token work of Ch 1 alone, the architect can already establish: the unit is tokens; the request shape will be prompt + retrieved context + output; the workload is input‑heavy; and the first number to lock down is tokens‑per‑request, because every downstream decision (which model fits, how much memory, what latency is possible) is priced against it. Using the canonical scenario as a starting point — ~2,000 registered users, ~5% concurrency, ~10 rps, ~9.2 K input + 300 output tokens — the architect projects the enterprise's actual headcount. If the company has 5,000 employees and expects 10% concurrent activity during peak Q&A periods (after a policy rollout), that gives **500 active people** — a *population* measure, **not** 500 requests currently occupying the inference service. An arrival rate requires its own traffic assumption or observation. Suppose user research and demand modeling independently set the busy-period peak to **50 requests/s** (a declared scenario input at this growth scale, not a figure derived from the 500-user count — Little's Law cannot convert an active-user population into an arrival rate without knowing in-flight request occupancy). With the illustrative ~8.6 s engine response duration, Little's Law implies approximately 50 × 8.6 ≈ **430 requests in the system** across the fleet at that rate — distinct from the 500 active people. It is the *arrival rate*, not the user count, that sizes the fleet. Using the canonical per-host bound from Chapters 15–20 (a single 8×H100 host serves ~2.0 req/s at full modeled utilization, i.e. C/W ≈ 17.5 KV-resident requests ÷ 8.6 s), the fleet rounds to:
-
-$$
-n_\text{hosts} = \frac{50 \text{ rps}}{2.0 \text{ req/s/host}} \approx 25 \text{ hosts} \quad (\text{full utilization})
-$$
-
-and roughly **~36 hosts** at a 70% target utilization. A prefill-throughput cross-check from the Chapter 8 model bounds it from below: 50 rps × 9.2K input = 460,000 prefill tokens/s ÷ ~19,800 tokens/s per host (the host's *sustained-planning* prefill rate, 8 × 2,471 tok/s at 35% MFU — a planning rate, not a ceiling: the peak-derived ceiling is ~56.5K tok/s; not a measured goodput) ≈ **~23 hosts**. (Do not divide by the ~8.5K tok/s single-request prefill rate, 9.2K ÷ 1.08 s — that is the rate for one request monopolizing a host, not a per-host aggregate, and using it here would be a unit error.) So prefill-throughput is a *lower* bound on host count; the binding figure is the KV-residency/service-time ~25 (full util) / ~36 (70%) result. The two do not "agree" — the KV-bound dominates, and the prefill model shows why adding hosts for prefill alone is the wrong lever at this scale; both are *analytical* bounds that must be confirmed by benchmark goodput (Chapter 14). Note this mini-case is a 5,000-employee growth scenario at 50 rps, distinct from the canonical 40 rps peak (which sizes to ~21 hosts full-util / ~29 working at 70% (30 with N−1), Chapters 8/16/17/20/25); the two are separate cases, not a contradiction.
+From the unit-and-token work of Ch 1 alone, the architect can already establish: the unit is tokens; the request shape will be prompt + retrieved context + output; the workload is input‑heavy; and the first number to lock down is tokens‑per‑request, because every downstream decision (which model fits, how much memory, what latency is possible) is priced against it. Using the canonical scenario as a starting point — ~2,000 registered users, ~5% concurrency, ~10 rps, ~9.2 K input + 300 output tokens — the architect projects the enterprise's actual headcount. If the company has 5,000 employees and expects 10% concurrent activity during peak Q&A periods (after a policy rollout), that gives **500 active people** — a *population* measure, **not** 500 requests currently occupying the inference service. An arrival rate requires its own traffic assumption or observation. Suppose user research and demand modeling independently set the busy-period peak to **50 requests/s** (a declared scenario input at this growth scale, not a figure derived from the 500-user count — Little's Law cannot convert an active-user population into an arrival rate without knowing in-flight request occupancy). With the illustrative ~8.6 s engine response duration, Little's Law implies approximately 50 × 8.6 ≈ **430 requests in the system** across the fleet at that rate — distinct from the 500 active people. It is the *arrival rate*, not the user count, that sizes the fleet. Using the canonical per-host bound from Chapters 15–20 (a single 8×H100 host serves ~2.0 req/s at full modeled utilization, i.e. the whole-slot floor 17 KV-resident requests ÷ 8.6 s = 1.977 — C ≈ 17.5 is the analytical quotient, floored to 17 deployable whole-context slots per the book's whole-slot convention, Chapters 14/16/17), the fleet rounds up by the same whole-slot ceiling the canonical 40 rps case uses (⌈344/17⌉ = 21):
+
+$$
+n_\text{hosts} = \left\lceil \frac{50 \text{ rps} \times 8.6 \text{ s}}{17 \text{ slots}} \right\rceil = \lceil 430/17 \rceil = \lceil 25.29 \rceil = 26 \text{ hosts} \quad (\text{full utilization})
+$$
+
+and roughly **~37 hosts** at a 70% target utilization (⌈430/(17 × 0.7)⌉ = ⌈430/11.9⌉ = ⌈36.13⌉). A prefill-throughput cross-check from the Chapter 8 model bounds it from below: 50 rps × 9.2K input = 460,000 prefill tokens/s ÷ ~19,800 tokens/s per host (the host's *sustained-planning* prefill rate, 8 × 2,471 tok/s at 35% MFU — a planning rate, not a ceiling: the peak-derived ceiling is ~56.5K tok/s; not a measured goodput) ≈ **~23 hosts**. (Do not divide by the ~8.5K tok/s single-request prefill rate, 9.2K ÷ 1.08 s — that is the rate for one request monopolizing a host, not a per-host aggregate, and using it here would be a unit error.) So prefill-throughput is a *lower* bound on host count; the binding figure is the KV-residency/service-time ~26 (full util) / ~37 (70%) result. The two do not "agree" — the KV-bound dominates, and the prefill model shows why adding hosts for prefill alone is the wrong lever at this scale; both are *analytical* bounds that must be confirmed by benchmark goodput (Chapter 14). Note this mini-case is a 5,000-employee growth scenario at 50 rps, distinct from the canonical 40 rps peak (which sizes to ~21 hosts full-util / ~29 working at 70% (30 with N−1), Chapters 8/16/17/20/25); the two are separate cases, not a contradiction.
 
 At the canonical instance rate (~$20/hr per 8×H100 host), the canonical 6–21-host fleet on-demand clouds is roughly **$87.6K–$306.6K/month** (6 hosts at ~$87.6K/month — $87,600 = 6 × 730 h default paid-occupancy input ≈ $14.04/1K — up to 21 hosts always-on at peak, $306,600 ≈ $49.13/1K; the paid-occupancy hours are an explicit illustrative input, not a measured duty cycle) depending on purchase mode and duty cycle (the canonical self-host total is $155,816.93/mo ≈ $24.97/1K — capex amortized runs lower, on-demand burst higher; Chapter 16 develops the TCO properly). The architect can now speak the system's currency — tokens, rps, dollars per million — and can engage the rest of the team on model selection, serving configuration, and TCO with concrete numbers rather than vague assurances.
```

## 7. 验证记录

```
recompute: in-flight=430.0, full=ceil(430/17)=26, 70%=ceil(430/11.9)=37
canonical: ceil(344/17)=21, ceil(344/11.9)=29 (+N-1=30)
prefill lower bound=460000/19800=23.23 -> ~23; KV binds: 26 > 23.2 True
conclusion: 50 rps requires >21 hosts True (full) / True (70%)
stale refs in §4.8 (≈25 hosts / ~25 (full util) / ~36 (70%) / **~36 hosts** / 17.5-连续引语): NONE
GREEN strings present: ⌈430/17⌉=⌈25.29⌉=26 (LaTeX in $$) / **~37 hosts** / ⌈430/11.9⌉=⌈36.13⌉ / ~26 (full util) / ~37 (70%) / ⌈344/17⌉=21 — all True
```

复算工具：Python `math.ceil`，输入仅取本章声明值（50 rps、8.6 s、17 whole slots），舍入与 canonical 40 rps 案例逐式相同。
