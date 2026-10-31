#!/usr/bin/env python3
# arithmetic-recompute-r27.py — Pass D independent arithmetic audit of the R27 proof
# PDF: review/publication_v2_20261028/work/accelerated_external_review_proof_r27/
#      render/build/from-token-to-fleet-v20260913.pdf
#      (425 pp, sha256 d700c1979efb2a825da146ac6500d59f452c77f4bd629f054ff04e7c1fd6aec9)
#
# Every quantity is recomputed FROM FIRST PRINCIPLES from the book's declared inputs,
# then compared with the value the book states (book_stated). Standalone: no repo imports.
# Status: PASS = reproduces; FAIL = does not reproduce; BORDERLINE = differs only at the
# stated rounding digit (reported with severity in arithmetic-audit-r27.md).
import math

RESULTS = []

def check(group, name, computed, book_stated, *, tol=None, note=""):
    """Compare computed vs book-stated. tol=None -> exact equality required."""
    if tol is None:
        ok = (computed == book_stated)
        diff = "" if ok else f"  diff={computed - book_stated:+g}"
    else:
        ok = abs(computed - book_stated) <= tol
        diff = "" if ok else f"  diff={computed - book_stated:+g} (tol {tol})"
    RESULTS.append((group, name, computed, book_stated, ok, note, diff))
    return ok

def r(x, nd):  # round-half-away-from-zero display helper (matches book display style)
    return float(f"%.{nd}f" % x)

# ---------------------------------------------------------------- (1) KV per token / slots
BYTES = 2 * 80 * 8192 * 2                       # BF16: 2B x 80 layers x 8192 hidden x (K+V)
check("1 KV", "KV/token BF16 bytes 2x80x8192x2", BYTES, 2_621_440)
check("1 KV", "KV/token BF16 in MiB", BYTES / 2**20, 2.5)
check("1 KV", "KV/token FP8 bytes (halved)", BYTES / 2, 1_310_720)
check("1 KV", "KV/token FP8 in MiB", (BYTES / 2) / 2**20, 1.25)
kv95 = 9_500 * BYTES                            # 9,500-token max residency, decimal GB
check("1 KV", "9,500 tok KV bytes", kv95, 24_903_680_000)
check("1 KV", "9,500 tok KV decimal GB", kv95 / 1e9, 24.90368)
hbm = 640 - 140 - 64                            # pool - weights - runtime reserve
check("1 KV", "HBM KV budget 640-140-64 (GB)", hbm, 436)
check("1 KV", "byte-accurate slots 436/24.90368", r(hbm / (kv95 / 1e9), 2), 17.51)
check("1 KV", "integer slot floor", math.floor(hbm / (kv95 / 1e9)), 17)
# FP8 variants quoted in Ch7/Ch15/Ch17
kv95_fp8 = 9_500 * (BYTES / 2)
check("1 KV", "FP8 9,500-tok KV GB", kv95_fp8 / 1e9, 12.45184, note="book ~12.45 GB")
check("1 KV", "FP8 slots T=0 floor", math.floor(hbm / (kv95_fp8 / 1e9)), 35)
check("1 KV", "FP8 concurrency rise 436/12.45", r(hbm / 12.45, 1), 35.0)

# ---------------------------------------------------- (2) non-agentic service time & hosts
W_exec = 1.08 + 300 * 0.025                     # prefill + TPOT x output
check("2 hosts", "W_exec = 1.08+300x0.025 (s)", W_exec, 8.58)
W_plan = 8.6                                     # declared rounded planning service time
check("2 hosts", "peak zero-spare ceil(40x8.6/17)", math.ceil(40 * W_plan / 17), 21)
check("2 hosts", "70%+N-1 ceil(344/(17x0.7))+1", math.ceil(344 / (17 * 0.7)) + 1, 30)
check("2 hosts", "70% working hosts ceil(344/11.9)", math.ceil(344 / 11.9), 29)
check("2 hosts", "95% sched factor ceil(344/(17x0.95))", math.ceil(344 / (17 * 0.95)), 22)
check("2 hosts", "avg zero-spare ceil(86/17)", math.ceil(86 / 17), 6)
check("2 hosts", "independent prefill ceil(368000/19770)", math.ceil(368_000 / 19_770), 19)
check("2 hosts", "avg prefill ceil(92000/19770)", math.ceil(92_000 / 19_770), 5)
check("2 hosts", "Little in-flight @40rps 40x8.6", 40 * W_plan, 344)
check("2 hosts", "Little in-flight @10rps 10x8.6", 10 * W_plan, 86)
# Ch16 claim: 29 surviving x 1.9767 x 0.70 ~= 40.2
surv = 29 * (17 / 8.6) * 0.70
check("2 hosts", "29x1.9767x0.70 (book says ~=40.2)", r(surv, 1), 40.2,
      note=f"exact {surv:.4f} -> book 40.2 overstates; >=40 still holds")

# ------------------------------------------------------------- (3) calendar request volume
req_mo = 10 * 8 * 3600 * 260 / 12
check("3 calendar", "10x8x3600x260/12 req/mo", req_mo, 6_240_000)
active_s = req_mo / 10                          # 6,240,000 req / 10 rps
check("3 calendar", "active seconds/month", active_s, 624_000)
check("3 calendar", "request-active hours", r(active_s / 3600, 2), 173.33)
check("3 calendar", "daily req 10x8x3600", 10 * 8 * 3600, 288_000)

# ------------------------------------------------------------------- (4) TCO (Ch16)
host_mo = 350_000 / 60 + 1_110.33              # capex/60mo + energy per host
tco21 = 21 * host_mo + 10_000
check("4 TCO", "per-host $/mo 350000/60+1110.33", r(host_mo, 2), 6943.66, note="exact 6943.663333")
check("4 TCO", "21-host monthly $", r(tco21, 2), 155_816.93)
check("4 TCO", "21-host $/1K", r(tco21 / req_mo * 1000, 2), 24.97)
check("4 TCO", "21-host $/1K exact", tco21 / req_mo * 1000, 24.97066185897436)
tco22 = 22 * host_mo + 10_000
check("4 TCO", "22-host monthly $", r(tco22, 2), 162_760.59)
check("4 TCO", "22-host $/1K", r(tco22 / req_mo * 1000, 2), 26.08)
tco30 = 30 * (350_000 / 60) + 30 * 1_110.33 + 10_000
check("4 TCO", "30-host monthly $", r(tco30, 2), 218_309.90)
check("4 TCO", "30-host $/1K", r(tco30 / req_mo * 1000, 2), 34.99)
cloud_def = 6 * 730 * 20
check("4 TCO", "cloud 4380h x $20", cloud_def, 87_600)
check("4 TCO", "cloud $/1K exact", cloud_def / req_mo * 1000, 14.038461538461538)
check("4 TCO", "cloud $/1K display", r(cloud_def / req_mo * 1000, 2), 14.04)
cloud_on = 21 * 730 * 20
check("4 TCO", "always-on 15330h x $20", cloud_on, 306_600)
check("4 TCO", "always-on $/1K exact", cloud_on / req_mo * 1000, 49.13461538461539)
check("4 TCO", "always-on $/1K display", r(cloud_on / req_mo * 1000, 2), 49.13)
api_px = 0.002 * 9.2 + 0.008 * 0.3             # $2/M-in, $8/M-out frontier tier
check("4 TCO", "API $/req 0.002x9.2+0.008x0.3", api_px, 0.0208)
api_mo = req_mo * api_px
check("4 TCO", "API monthly $", api_mo, 129_792)
check("4 TCO", "API $/1K", api_mo / req_mo * 1000, 20.8)
be = tco21 / api_px
check("4 TCO", "break-even 155816.93/0.0208", r(be, 2), 7_491_198.56)
check("4 TCO", "band low 155816.93/0.025", r(tco21 / 0.025, 1), 6_232_677.2)
check("4 TCO", "band high 155816.93/0.015", r(tco21 / 0.015, 2), 10_387_795.33)
check("4 TCO", "30-host break-even/0.0208 (M)", r(tco30 / api_px / 1e6, 1), 10.5)
check("4 TCO", "self/cloud ratio 155816.93/87600", r(tco21 / cloud_def, 2), 1.78)

# ------------------------------------------------------- (5) agentic W(T), ledger, alpha
I0, delta, gamma, O, tpref = 9_200, 800, 65, 300, 1.08
tpot, tool_leg = 0.025, 0.133                   # 25 ms/token; Ch17 ~133 ms/turn tool leg
def W(T, prefill=tpref):                        # Ch19 formula, held-prefill instantiation
    return prefill + tpot * (O + T * gamma) + T * tool_leg
for T, stated in [(1, 10.3), (2, 12.1), (3, 13.8), (4, 15.6)]:
    w = W(T)
    check("5 agentic", f"W({T}) same-formula 1dp", r(w, 1), stated,
          note=f"exact {w:.3f}")
check("5 agentic", "W(0) single-shot", W(0), 8.58, note="book W(0)=8.6 planning / 8.58 exec")
# literal printed formula T_prefill(I(T)) instead of held 1.08
def W_lit(T):
    IT = I0 + T * (delta + gamma) + O
    return tpref * IT / I0 + tpot * (O + T * gamma) + T * tool_leg
check("5 agentic", "W(3) literal T_prefill(I(T)) 1dp", r(W_lit(3), 1), 13.8,
      note=f"exact {W_lit(3):.3f} (book discloses ~14.2 lower-bound gap)")
# token model
I = {T: I0 + T * (delta + gamma) + O for T in range(1, 5)}
check("5 agentic", "I(1)", I[1], 10_365)
check("5 agentic", "I(2)", I[2], 11_230)
check("5 agentic", "I(3)", I[3], 12_095)
check("5 agentic", "I(4)", I[4], 12_960)
for T in (1, 2, 3, 4):
    check("5 agentic", f"alpha({T})", r(I[T] / 9_500, 2), [None, 1.09, 1.18, 1.27, 1.36][T])
# call ledger (T=3, 4 model calls, +865/call)
calls = [I0 + k * (delta + gamma) for k in range(4)]
task_in = sum(calls)
task_out = O + 3 * gamma
check("5 agentic", "ledger call inputs", calls, [9_200, 10_065, 10_930, 11_795])
check("5 agentic", "task_input", task_in, 41_990)
check("5 agentic", "task_output", task_out, 495)
billed = task_in + task_out
check("5 agentic", "billed no-cache", billed, 42_485)
perfect = calls[-1] + task_out                  # 9,200 + 3x865 + 495
check("5 agentic", "billed perfect-cache", perfect, 12_290)
check("5 agentic", "exec multiplier 42485/9500", r(billed / 9_500, 2), 4.47)
check("5 agentic", "peak KV 12095 -> GB", r(I[3] * BYTES / 1e9, 1), 31.7)
check("5 agentic", "C at T=3 436/31.706", r(436 / (I[3] * BYTES / 1e9), 1), 13.8,
      note="floor 13")
check("5 agentic", "C at T=1 floor", math.floor(436 / (I[1] * BYTES / 1e9)), 16)
check("5 agentic", "C at T=4 floor", math.floor(436 / (I[4] * BYTES / 1e9)), 12)
check("5 agentic", "C FP8 at T=3 raw", r(436 / (I[3] * BYTES / 2 / 1e9), 1), 27.5,
      note="floor 27")
# latency rows
Lbase, Lagent = 8.6, 0.220
for T, stated in [(1, 8.8), (2, 9.0), (3, 9.3), (4, 9.5)]:
    check("5 agentic", f"L_E2E({T}) 1dp", r(Lbase + T * Lagent, 1), stated)
check("5 agentic", "beta at T=3 (9.26/8.6)", r((Lbase + 3 * Lagent) / Lbase, 2), 1.08)
check("5 agentic", "T.Lagent at T=3 (ms)", 3 * Lagent * 1000, 660)
# Ch17 mini-case fleet at 100 rps, T=3
check("5 agentic", "in-flight 100x13.8", 100 * 13.8, 1_380)
check("5 agentic", "N ceil(1380/(13x0.7))", math.ceil(1380 / (13 * 0.7)), 152)
check("5 agentic", "N full-util ceil(1380/13)", math.ceil(1380 / 13), 107)
# Ch19 worked example (section 19.3) vs per-turn convention at T=2
worked = (10_000 + 350) + 300                  # trace: 800 then 350 tool outputs, no gamma
check("5 agentic", "worked example total T=2", worked, 10_650)
check("5 agentic", "worked example alpha T=2", r(worked / 9_500, 2), 1.12,
      note="Table 19-1 states 1.18 at T=2 -> same quantity, two values")

# --------------------------------------------------------------- (6) Ch20 capacity curves
per_host = 17 / 8.6
check("6 ch20", "per-host rps 17/8.6", r(per_host, 4), 1.9767)
check("6 ch20", "ideal hosts ceil(40/1.9767)", math.ceil(40 / per_host), 21)
check("6 ch20", "95% hosts ceil(40/(0.95x1.9767))", math.ceil(40 / (0.95 * per_host)), 22)
check("6 ch20", "avg hosts ceil(10/1.9767)", math.ceil(10 / per_host), 6)
check("6 ch20", "C_analytic(8) 8x17/8.6", r(8 * per_host, 1), 15.8)
check("6 ch20", "marginal $20x8.6/17", r(20 * 8.6 / 17, 2), 10.12)
check("6 ch20", "prefill ceiling 8x0.989PFx35%/140e9", 8 * 0.989e15 * 0.35 / (2 * 70e9), 19_780)
check("6 ch20", "stress screen 2.0x9200", 2.0 * 9_200, 18_400)
check("6 ch20", "ratio 18400/19780", r(18_400 / 19_780, 2), 0.93)

# ------------------------------------------------------- (7) Ch16 fixed-peak feasible bound
check("7 ch16", "40x624,000 req/mo", 40 * active_s, 24_960_000)

# ------------------------------------------------- (8) Ch21 gating / regression mini-case
breach = 6 / 8 * 288_000
check("8 ch21", "6/8x288,000 requests", breach, 216_000)
cost_self = breach * (tco21 / req_mo * 1000) / 1000
check("8 ch21", "216,000 x $24.97/1K", r(cost_self, 0), 5_394)
cost_cloud = breach * (cloud_def / req_mo * 1000) / 1000
check("8 ch21", "216,000 x $14.04/1K exact", r(cost_cloud, 2), 3_032.31)
check("8 ch21", "display $", r(cost_cloud, 0), 3_032)
check("8 ch21", "latency regression (2.8-1.9)/1.9", r((2.8 - 1.9) / 1.9, 2), 0.47)
canary = 0.05 * 288_000 * 2 / 8
check("8 ch21", "canary 5%x288,000x2/8", canary, 3_600)
check("8 ch21", "blast-radius reduction 216000/3600", breach / canary, 60)

# ------------------------------------------------------------- (9) Ch26 capstone per-query
cap = (tco21 / req_mo) * 0.65 * 0.80           # $/req x 65% reach engine x 0.80 sharded
check("9 capstone", "0.02497066x0.65x0.80", r(cap, 7), 0.0129847)
check("9 capstone", "display $/query", r(cap, 3), 0.013)
check("9 capstone", "cost fraction 0.65x0.80", 0.65 * 0.80, 0.52)
check("9 capstone", "saving 1-0.52", 1 - 0.52, 0.48)

# ------------------------------------------------------------- (10) fig 20.1 @ N=40
check("10 fig20.1", "C_analytic(40) = 40x17/8.6", r(40 * per_host, 2), 79.07,
      note="curve value; not printed in the 425 pages")

# ------------------------------------------- Ch4 mini-case (50 rps growth scenario)
check("4 minicase", "active people 10%x5000", 0.10 * 5_000, 500)
check("4 minicase", "in-flight 50x8.6", 50 * 8.6, 430)
rate_cont = 17.5 / 8.6                          # declared per-host bound C/W ~ 17.5/8.6
check("4 minicase", "hosts ceil(50/2.0349) continuous-17.5", math.ceil(50 / rate_cont), 25)
check("4 minicase", "hosts@70% ceil(50/(2.0349x0.7))", math.ceil(50 / (rate_cont * 0.7)), 36)
check("4 minicase", "50rps hosts under Ch17 whole-slot floor-17",
      math.ceil(430 / 17), 25, note="book 25 rests on continuous 17.5; whole-slot gives 26")
check("4 minicase", "50rps 70% hosts under Ch17 whole-slot floor-17",
      math.ceil(430 / 11.9), 36, note="book 36 rests on continuous 17.5; whole-slot gives 37")
check("4 minicase", "prefill bound ceil(460000/19800)", math.ceil(460_000 / 19_800), 23,
      note="quotient 23.23; book prints ~23 (rounded quotient, not ceiled count)")
check("4 minicase", "6-host cloud 6x730x20", 6 * 730 * 20, 87_600)
check("4 minicase", "6x730 host-hours", 6 * 730, 4_380)

# ------------------------------------------------------------------- Ch15 MFU / regimes
check("15 mfu", "in-flight light 2x8.6", 2 * 8.6, 17.2, note="table ~17")
check("15 mfu", "in-flight typical 10x8.6", 10 * 8.6, 86)
check("15 mfu", "in-flight peak 40x8.6", 40 * 8.6, 344)
check("15 mfu", "KV/user 9500x2.62144MB GB", r(9_500 * BYTES / 1e9, 1), 24.9)
check("15 mfu", "second-host jump 70000/8000", 70_000 / 8_000, 8.75)

# ------------------------------------------------------------------------ Ch8 roofline
pref = 2 * 70e9 * 9_200
check("8 roofline", "prefill FLOP 2x70e9x9.2e3", r(pref, 15), 1.288e15, note="book 1.29 PFLOP")
check("8 roofline", "required PFLOPS 1.29/1.08", r(1.288e15 / 1.08 / 1e15, 2), 1.19)
check("8 roofline", "ridge 989/3.35", r(989 / 3.35, 0), 295)
check("8 roofline", "prefill intensity FLOP/byte", pref / 140e9, 9_200, note="book ~9.2K")
check("8 roofline", "decode intensity FLOP/byte", 2 * 70e9 / 140e9, 1.0)
check("8 roofline", "decode BW 140GB/25ms TB/s", 140 / 0.025 / 1000, 5.6)
check("8 roofline", "single-req prefill 9200/1.08 (K)", r(9_200 / 1.08 / 1000, 1), 8.5, note="book ~8.5K; exact 8518.5 tok/s")
check("8 roofline", "sustained 346 TFLOPS", r(989 * 0.35, 0), 346)
check("8 roofline", "per-GPU tok/s 346e12/140e9", r(346e12 / 140e9, 0), 2_471)
check("8 roofline", "per-host 8x2471", 8 * 2_471, 19_768, note="book ~19,800 / 19,770 / 19,780")
check("8 roofline", "peak ceiling 8x989e12/140e9", r(8 * 989e12 / 140e9 / 1000, 1), 56.5,
      note="book ~56.5K tok/s")
check("8 roofline", "tokens/host-dollar 19800x3600/20", r(19_800 * 3600 / 20 / 1e6, 2), 3.56)
check("8 roofline", "Ch16 prefill screen ceil(368000/19780)", math.ceil(368_000 / 19_780), 19,
      note="book ~18.6 -> ~19-20 hosts; scope ledger 19")

# ------------------------------------------------------------------------ Ch9 ring comms
M, N = 140, 8
phase = (N - 1) / N * M
check("9 ring", "per-phase (N-1)/N x140 GB", phase, 122.5)
check("9 ring", "two-phase per-rank send GB", 2 * phase, 245)
check("9 ring", "flat 140/2.5 s", M / 2.5, 56)
check("9 ring", "ring 2x122.5/2.5 s", 2 * phase / 2.5, 98)
check("9 ring", "ring NVLink 245/450 s", r(245 / 450, 2), 0.54)
check("9 ring", "ring two-rail 245/40 s", r(245 / 40, 1), 6.1)
check("9 ring", "flat HDR 140/25 s", r(140 / 25, 1), 5.6)
check("9 ring", "caption factor 245/140", r(245 / 140, 2), 1.75)
check("9 ring", "1000 iters hours 56000/3600", r(56_000 / 3600, 2), 15.56,
      note="book says 15.5 h")

# ------------------------------------------------------- Ch16 two-host mini-case (exact roots)
capex2, power2, staff = 2 * 350_000 / 60, 2 * 1_110.33, 26_000
exact2 = capex2 + power2 + staff
check("16 minicase", "two-host exact $/mo", r(exact2, 2), 39_887.33)
check("16 minicase", "break-even /0.0208", r(exact2 / api_px, 0), 1_917_660,
      note="book prints $40,000/0.0208 ~= 1.9M")
check("16 minicase", "5M / break-even", r(5_000_000 / (exact2 / api_px), 2), 2.61,
      note="book prints ~2.6x")
check("16 minicase", "API@5M", 5_000_000 * api_px, 104_000)
check("16 minicase", "monthly saving", r(104_000 - exact2, 2), 64_112.67)
check("16 minicase", "annual saving (0dp)", r((104_000 - exact2) * 12, 0), 769_352,
      note="exact-root 769,352.08; rounded-root 769,352.04; book prints ~$64K/mo only")
check("16 minicase", "unallocated on exact basis", r(exact2 - capex2 - power2 - staff, 2), 0.0,
      note="book '~$0.2K of $26.2K' holds only on fully-rounded basis")

# ------------------------------------------------------------------- Ch17 Table 17-1 grid
rows = []
for lam in (40, 100, 200):
    na, ag = lam * 8.6, lam * 13.8
    rows.append((lam, na, ag,
                 math.ceil(na / 11.9), math.ceil(ag / 9.1), math.ceil(ag / 18.9)))
book_rows = [(40, 344, 552, 29, 61, 30), (100, 860, 1380, 73, 152, 74),
             (200, 1720, 2760, 145, 304, 147)]
for got, exp in zip(rows, book_rows):
    check("17 table", f"row lambda={exp[0]}", list(got), list(exp))
check("17 table", "N-1 row 40rps", [math.ceil(344 / 11.9) + 1, math.ceil(552 / 9.1) + 1,
                                     math.ceil(552 / 18.9) + 1], [30, 62, 31])
check("17 table", "storage-only 10,000/17 hosts", math.ceil(10_000 / 17), 589)

# ------------------------------------------------------------------ print report table
w_group = max(len(g[0]) for g in RESULTS)
w_name = max(len(g[1]) for g in RESULTS)
fails = border = 0
print(f"{'GROUP'.ljust(w_group)} | {'QUANTITY'.ljust(w_name)} | COMPUTED | BOOK | STATUS")
print("-" * (w_group + w_name + 60))
for g, name, comp, stated, ok, note, diff in RESULTS:
    status = "PASS" if ok else "FAIL"
    if not ok:
        fails += 1
    print(f"{g.ljust(w_group)} | {name.ljust(w_name)} | {comp} | {stated} | {status}"
          + (f"  {diff}" if diff else "") + (f"  [{note}]" if note else ""))
print("-" * (w_group + w_name + 60))
print(f"TOTAL {len(RESULTS)} checks, FAIL {fails}")