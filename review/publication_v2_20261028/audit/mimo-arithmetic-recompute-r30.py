#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pass-D 独立算术复算 · R30 评审本 (MiMo)
零依赖：只用 stdlib math。所有输入均为书中声明输入 (declared inputs)，
第一性原理复算，逐项与书中印刷值比对。

对象: review/publication_v2_20261028/work/accelerated_external_review_proof_r30/
      render/build/from-token-to-fleet-v20260913.pdf (425pp)
用法: python3 mimo-arithmetic-recompute-r30.py [extracted.txt]
      第二个参数可选：pdftotext 抽取的全文，用于"书中印刷值是否在位"的存在性检查。
"""
import math
import sys

PASS, FAIL, INFO = 0, 0, 0
rows = []


def check(group, label, computed, book, tol=None, note=""):
    """computed 与 book 比对（tol 为绝对容差；None = 精确到显示位）"""
    global PASS, FAIL
    ok = False
    if isinstance(book, str) or isinstance(computed, str):
        ok = str(computed) == str(book)
    elif tol is None:
        ok = abs(computed - book) < 1e-9
    else:
        ok = abs(computed - book) <= tol
    rows.append((group, label, computed, book, "PASS" if ok else "FAIL", note))
    if ok:
        PASS += 1
    else:
        FAIL += 1
    return ok


def ceil_div(a, b):
    return math.ceil(a / b - 1e-12)


# ---------------------------------------------------------------- (1) KV / 槽位
KV = 2 * 80 * 8192 * 2                      # BF16 KV per token, bytes
check("(1)", "KV/token BF16 = 2x80x8192x2 (B)", KV, 2621440)
mem9500 = 9500 * KV
check("(1)", "9,500 tok -> GB (decimal)", mem9500 / 1e9, 24.90368, 1e-9)
check("(1)", "HBM = 640-140-64 (GB)", 640 - 140 - 64, 436)
slot = math.floor(436e9 / mem9500)
check("(1)", "slot floor = floor(436GB/24.90368GB)", slot, 17)
check("(1)", "continuous quotient 436/24.90368 (book 17.51)",
      round(436e9 / mem9500, 2), 17.51, 1e-9)
# 附：FP8 半字节槽位（同书 Ch17）
kv8 = 2 * 80 * 8192 * 1
check("(1)", "KV/token FP8 (B)", kv8, 1310720)
check("(1)", "FP8 slot floor", math.floor(436e9 / (9500 * kv8)), 35)

# ------------------------------------------------------- (2) 非 agentic 主机数
W = 1.08 + 300 * 0.025
check("(2)", "W = 1.08+300x0.025 (s)", W, 8.58)
check("(2)", "decode share 7.5/8.58 (%)", 100 * 7.5 / W, 87.4, 0.1)
check("(2)", "peak ceil(344/17)", ceil_div(344, 17), 21)
check("(2)", "70% working ceil(344/11.9)", ceil_div(344, 11.9), 29)
check("(2)", "70%+N-1 = 29+1", ceil_div(344, 11.9) + 1, 30)
check("(2)", "95% derate ceil(344/16.15)", ceil_div(344, 16.15), 22)
check("(2)", "avg KV ceil(86/17)", ceil_div(86, 17), 6)
check("(2)", "50rps full ceil(430/17)", ceil_div(430, 17), 26)
check("(2)", "50rps 70% ceil(430/11.9)", ceil_div(430, 11.9), 37)
check("(2)", "prefill peak ceil(368,000/19,770)", ceil_div(368000, 19770), 19)
check("(2)", "prefill avg ceil(92,000/19,770)", ceil_div(92000, 19770), 5)
check("(2)", "N-1 survival 29x1.9767x0.70", 29 * (17 / 8.6) * 0.70, 40.1, 0.05)

# ---------------------------------------------------------------- (3) 日历量
req = 10 * 8 * 3600 * 260 / 12
check("(3)", "req/mo = 10x8x3600x260/12", req, 6240000)
check("(3)", "active h/mo = 8x260/12", 8 * 260 / 12, 173.3333333333, 1e-6)
check("(3)", "active h/mo = 6,240,000/10/3600", 6240000 / 10 / 3600, 173.3333333333, 1e-6)
check("(3)", "active seconds/mo", 6240000 / 10, 624000)

# ------------------------------------------------------------------- (4) TCO
per_host_capex = 350000 / 60
energy_host = 7.8 * 1.3 * 0.15 * 730          # 10.14 kW x $0.15 x 730h
check("(4)", "energy $/host/mo = 10.14kWx0.15x730", round(energy_host, 2), 1110.33, 0.005)
t21 = 21 * per_host_capex + 21 * energy_host + 10000
check("(4)", "21-host monthly total", round(t21, 2), 155816.93, 0.005)
check("(4)", "21-host capex 21x350,000/60", round(21 * per_host_capex, 2), 122500.00, 0.005)
check("(4)", "21-host energy 21x1,110.33", round(21 * energy_host, 2), 23316.93, 0.005)
per1k_21 = t21 / 6240000 * 1000
check("(4)", "$/1K = 155,816.93/6.24M", per1k_21, 24.97066185897436, 1e-12)
check("(4)", "$/1K rounded", round(per1k_21, 2), 24.97, 1e-9)
t22 = 22 * per_host_capex + 22 * energy_host + 10000
check("(4)", "22-host monthly total", round(t22, 2), 162760.59, 0.005)
check("(4)", "22-host $/1K rounded", round(t22 / 6240000 * 1000, 2), 26.08, 1e-9)
t30 = 30 * per_host_capex + 30 * energy_host + 10000
check("(4)", "30-host monthly total", round(t30, 2), 218309.90, 0.005)
check("(4)", "30-host $/1K rounded", round(t30 / 6240000 * 1000, 2), 34.99, 1e-9)
api = 6240 * 20.8
check("(4)", "API $/mo = 6,240 x $20.8/1K", api, 129792.0)
check("(4)", "API $/1K = 2x9.2+8x0.3 ($/1M->req)", (2 * 9.2 + 8 * 0.3) / 1000, 0.0208, 1e-12)
be = t21 / 0.0208
check("(4)", "break-even = 155,816.93/0.0208", round(be, 2), 7491198.56, 0.005)
check("(4)", "band low = /0.025", round(t21 / 0.025, 2), 6232677.20, 0.005)
check("(4)", "band high = /0.015", round(t21 / 0.015, 2), 10387795.33, 0.005)
check("(4)", "30-host break-even ~M", round(t30 / 0.0208 / 1e6, 1), 10.5, 1e-9)
check("(4)", "cloud 6-host $/mo = 6x730x20", 6 * 730 * 20, 87600)
check("(4)", "cloud 6-host $/1K", round(87600 / 6240, 4), 14.0385, 1e-4)
check("(4)", "always-on 21-host $/mo", 21 * 730 * 20, 306600)
check("(4)", "always-on $/1K", round(306600 / 6240, 2), 49.13, 1e-9)

# ------------------------------------------------------- (5) agentic Ch17/Ch19
def W_of(T):
    return 1.08 + 0.025 * (300 + 65 * T) + 0.133 * T


check("(5)", "W(3) = 1.08+0.025x495+3x0.133", W_of(3), 13.854, 1e-12)
check("(5)", "W(1) -> 10.3", round(W_of(1), 1), 10.3, 1e-9)
check("(5)", "W(2) -> 12.1", round(W_of(2), 1), 12.1, 1e-9)
check("(5)", "W(4) -> 15.6", round(W_of(4), 1), 15.6, 1e-9)
check("(5)", "W(0) -> 8.6", round(W_of(0), 1), 8.6, 1e-9)
I = {T: 9200 + T * 865 + 300 for T in range(5)}
check("(5)", "I(3)", I[3], 12095)
task_input = 9200 + 10065 + 10930 + 11795
check("(5)", "task_input ledger", task_input, 41990)
task_output = 3 * 65 + 300
check("(5)", "task_output", task_output, 495)
peak_bytes = I[3] * KV
check("(5)", "peak 12,095 -> GB", peak_bytes / 1e9, 31.7063168, 1e-9)
check("(5)", "peak -> 31.7 GB (1dp)", round(peak_bytes / 1e9, 1), 31.7, 1e-9)
check("(5)", "alpha = 12,095/9,500", round(I[3] / 9500, 2), 1.27, 1e-9)
check("(5)", "multiplier = 42,485/9,500", round((task_input + task_output) / 9500, 2), 4.47, 1e-9)
check("(5)", "perfect-cache billed = 11,795+495", 11795 + 495, 12290)
# Ch19 §19.3 无条件账本
dist = [(0.68, 19630, 19265, 365), (0.25, 30625, 30195, 430),
        (0.05, 42485, 41990, 495), (0.02, 39890, 39395, 495)]
tot = sum(p * t for p, t, _, _ in dist) * 100
tot_in = sum(p * i for p, _, i, _ in dist) * 100
tot_out = sum(p * o for p, _, _, o in dist) * 100
check("(5)", "total tokens /100 req", round(tot), 2392670)
check("(5)", "cost/completed = 2,392,670/98", round(tot / 98), 24415)
check("(5)", "input/completed", round(tot_in / 98), 24017)
check("(5)", "output/completed", round(tot_out / 98), 398)
check("(5)", "excl. fallback = (2,392,670-79,780)/98", round((tot - 2 * 39890) / 98), 23601)
check("(5)", "delta tokens", round(tot / 98) - round((tot - 2 * 39890) / 98), 814)
check("(5)", "delta %", round(100 * 814 / 23601, 1), 3.4, 1e-9)
mean = (0.68 * 220 + 0.25 * 440 + 0.05 * 660 + 0.02 * 860)
check("(5)", "mean orchestration ms", round(mean), 310)
check("(5)", "conditional mean ms", round((0.68 * 220 + 0.25 * 440 + 0.05 * 660) / 0.98), 299)

# ------------------------------------------------------------------- (6) Ch20
c40 = 40 * 17 / 8.6
check("(6)", "C_analytic(40) = 40x17/8.6", round(c40, 2), 79.07, 1e-9)
check("(6)", "C_eff(22) >= 40 ?", 0.95 * 22 * 17 / 8.6 >= 40, True)
check("(6)", "C_eff(21) < 40 ?", 0.95 * 21 * 17 / 8.6 < 40, True)
check("(6)", "8-host aggregate 8x17/8.6", round(8 * 17 / 8.6, 1), 15.8, 1e-9)
check("(6)", "marginal $/rps/h = 20x8.6/17", round(20 * 8.6 / 17, 2), 10.12, 1e-9)
prefill_ceiling = 8 * 0.989e15 * 0.35 / (2 * 70e9)
check("(6)", "prefill ceiling tok/s", round(prefill_ceiling), 19780)
check("(6)", "18,400/19,780 (%)", round(100 * 18400 / prefill_ceiling), 93)

# ------------------------------------------------------------------- (7) Ch16
check("(7)", "crossover 7.491M", round(be / 1e6, 3), 7.491, 1e-9)
check("(7)", "feasible bound 40x624,000", 40 * 624000, 24960000)
check("(7)", "40.1 (29x1.9767x0.70)", round(29 * (17 / 8.6) * 0.7, 1), 40.1, 1e-9)

# ------------------------------------------------------------- (8) Ch21 / Ch23
daily = 10 * 8 * 3600
check("(8)", "daily req @10rpsx8h", daily, 288000)
exposed = 6 / 8 * daily
check("(8)", "exposed = 6/8x288,000", exposed, 216000)
check("(8)", "$ cost = 216,000x24.97066185897436/1,000",
      round(exposed * per1k_21 / 1000), 5394)
check("(8)", "$ cloud = 216,000x14.038461538461538/1,000",
      round(exposed * (87600 / 6240000 * 1000) / 1000, 2), 3032.31, 0.005)
canary = 0.05 * daily * 2 / 8
check("(8)", "canary = 5%x288,000x2/8", canary, 3600)
check("(8)", "blast-radius x", exposed / canary, 60)
check("(8)", "latency regression (%)", 100 * (2.8 - 1.9) / 1.9, 47.37, 0.01)

# ---------------------------------------------------------------- (9) capstone
cap = 0.02497066 * 0.65 * 0.80
check("(9)", "0.02497066x0.65x0.80", round(cap, 7), 0.0129847, 1e-9)
check("(9)", "-> $0.013 (3dp)", round(cap, 3), 0.013, 1e-9)
check("(9)", "cost fraction 0.65x0.80", 0.65 * 0.80, 0.52, 1e-12)

# ------------------------------------------------- 前轮修复在位性（R30 文本层）
prior = [
    ("13.854", "Ch19 W(3) 脚注"),
    ("⌈430/17⌉", "Ch4 D1: 26 (50rps 满载)"),
    ("⌈36.13⌉", "Ch4 D1: 37 (50rps 70%)"),
    ("40.1", "Ch16 D2: 40.1"),
    ("15.6 hours", "Ch9 D7: 15.6 h"),
    ("23.23, ceiled to a whole host", "Ch4 D5: ~24 hosts"),
    ("35,000", "Ch15 N03: 35,000 tok/s 下端"),
    ("56,000", "Ch15 N03: 56,000 tok/s 上端"),
    ("79.07", "Ch20 40-host analytic（预期不在位）"),
]
text = ""
if len(sys.argv) > 1:
    with open(sys.argv[1], encoding="utf-8", errors="replace") as fh:
        text = " ".join(fh.read().split())   # 折叠换行，避免行末断词漏检
    for needle, why in prior:
        found = needle in text
        expect_absent = needle == "79.07"
        ok = (not found) if expect_absent else found
        rows.append(("fix", f"在位性: {why}", found, (not expect_absent),
                    "PASS" if ok else "FAIL", needle))
        if ok:
            PASS += 1
        else:
            FAIL += 1

# ------------------------------------------- 新发现：Ch15 §15.10 MFU 复算
mfu_two_host = 70000 * (2 * 70e9) / (2 * 8 * 0.989e15)
rows.append(("NEW", "Ch15 §15.10 'MFU stabilizes at 38%' vs 复算",
             round(mfu_two_host * 100, 1), 38.0, "FAIL",
             "70,000 tok/s 双机 = 9.8 PFLOP/s ÷ 15.82 PFLOP/s ≈ 62%；38% 需 ~42,800 tok/s"))
FAIL += 1
rows.append(("NEW", "同章 §15.6 自洽性: 70,000 单机 = ~124% MFU（书中）→ 双机 62%",
             62.0, 38.0, "FAIL", "同章两处对同一 70,000 tok/s 给出不相容 MFU"))
FAIL += 1

# ------------------------------------------------------------------------ 输出
w = (6, 52, 22, 22, 6)
print(f"{'GRP':<6} {'CHECK':<52} {'RECOMPUTED':>22} {'BOOK':>22} {'R':<6}")
print("-" * 112)
for g, lab, comp, book, res, note in rows:
    c = comp if not isinstance(comp, float) else round(comp, 6)
    b = book if not isinstance(book, float) else round(book, 6)
    print(f"{g:<6} {lab:<52} {str(c):>22} {str(b):>22} {res:<6}" + (f"  {note}" if note else ""))
print("-" * 112)
print(f"TOTAL {PASS + FAIL} checks | PASS {PASS} | FAIL {FAIL}")
sys.exit(0)