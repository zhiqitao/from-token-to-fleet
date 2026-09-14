import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

base = 'design/manuscript/chapter-%02d/figures/fig-%02d-%02d01.png'

# ---- Ch02: Decode vs prefill: bandwidth vs compute ----
# LEFT: bandwidth demand vs supply (decode) ~ correct units (TB/s vs TB/s)
# RIGHT: prefill compute demand converted to a REQUIRED compute RATE (~PFLOPS) vs supply
import math
prefill_work = 1.29      # PFLOP (2NL at 9.2K)
prefill_budget_s = 1.08  # implicit ~1 s budget at 9.2K ctx full pass
prefill_rate = prefill_work / prefill_budget_s  # ~1.2 PFLOPS required
fig, axes = plt.subplots(1, 2, figsize=(11, 5))
ax = axes[0]
ax.bar(['decode\n(needed)', 'H100\n(supply)'], [5.6, 3.35], color=['#c0392b', '#3a6ea5'], hatch=['//', ''], edgecolor=['#7a1f1a','none'])
for i, v in enumerate([5.6, 3.35]):
    ax.text(i, v+0.1, f'{v} TB/s', ha='center', fontweight='bold')
ax.set_ylabel('HBM bandwidth (TB/s)')
ax.set_title('Decode: HBM-bandwidth-bound\n(5.6 needed > 3.35 supply)')
ax.grid(alpha=0.3, axis='y')
# right: required prefill compute RATE (~1.2 PFLOPS) vs H100 peak RATE (0.989 PFLOPS)
ax = axes[1]
ax.bar(['prefill\n(req. rate)', 'H100\n(peak rate)'], [prefill_rate, 0.989], color=['#c0392b', '#3a6ea5'], hatch=['//', ''], edgecolor=['#7a1f1a','none'])
for i, v in enumerate([prefill_rate, 0.989]):
    ax.text(i, v+0.03, f'{v:.2f} PFLOPS', ha='center', fontweight='bold')
ax.set_ylabel('Compute rate (PFLOPS)')
ax.set_ylim(0, 1.6)
ax.set_title('Prefill: compute-bound → required rate\n(1.29 PFLOP ÷ ~1 s ≈ 1.2 PFLOPS)')
ax.grid(alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig(base % (2, 2, 2), dpi=150); plt.close()
print('Ch02 done')

# ---- Ch04: Six-dimension workload characterization -> architectural decisions ----
fig, ax = plt.subplots(figsize=(12, 7))
ax.set_xlim(0, 14); ax.set_ylim(0, 10); ax.axis('off')
dims = ['Throughput / RPS', 'SLO / latency', 'Context length', 'KV / input', 'Modality', 'Concurrency & burst']
cons = ['sizing / serving', 'TTFT / TPOT', 'KV & memory', 'KV cache', 'encoder / P-D split', 'batch / autoscale']
for i, (d, c) in enumerate(zip(dims, cons)):
    y = 9 - i*1.35
    ax.add_patch(FancyBboxPatch((0.5, y-0.4), 4.5, 0.8, boxstyle='round,pad=0.02', fc='#3a6ea5', ec='none'))
    ax.text(2.75, y, d, ha='center', va='center', color='white', fontsize=11, fontweight='bold')
    ax.annotate('', xy=(6.6, y), xytext=(5.2, y), arrowprops=dict(arrowstyle='-|>', lw=1.8, color='#555'))
    ax.add_patch(FancyBboxPatch((6.8, y-0.4), 6.5, 0.8, boxstyle='round,pad=0.02', fc='#e67e22', ec='none'))
    ax.text(10.05, y, c, ha='center', va='center', color='white', fontsize=11)
ax.text(7, 9.7, 'Six-dimension workload characterization → architectural consequences',
        fontsize=13, fontweight='bold', ha='center')
plt.tight_layout()
plt.savefig(base % (4, 4, 4), dpi=150); plt.close()
print('Ch04 done')

# ---- Ch05: Model selection flowchart ----
# RETIRED: competes with the Archify-rendered two-leg asset (render/archify/ch5-two-leg.json
# -> design/manuscript/chapter-05/figures/fig-05-0501.{png,pdf}), which matches the
# manuscript caption 'workload -> five selection surfaces -> two legs -> decision'.
# regen_figs.py must not clobber the Archify asset.
print('fig-05-0501: Archify-rendered asset; matplotlib generator retired')

# ---- Ch09: collective completion time vs data volume (the promised chart) ----
# all-reduce completion ~ O(2 data / B_eff); lines for the interconnect tiers
size = np.logspace(-2, 2, 200)      # GB
bw = {'NVSwitch (1.8 TB/s)': 1800, 'NVLink (0.9 TB/s)': 900,
      'InfiniBand (0.4 TB/s)': 400, 'Ethernet (0.1 TB/s)': 100}
data_per_byte = 2.0   # all-reduce ~2x data across the tree
fig, ax = plt.subplots(figsize=(9, 5.5))
cols = {'NVSwitch (1.8 TB/s)': ('#27408b', '-', 'o'),
        'NVLink (0.9 TB/s)': ('#3a6ea5', '--', 's'),
        'InfiniBand (0.4 TB/s)': ('#e67e22', '-.', '^'),
        'Ethernet (0.1 TB/s)': ('#c0392b', ':', 'D')}
for name, b in bw.items():
    c, ls, mk = cols[name]
    t = data_per_byte * size / b   # GB / (GB/s) = s
    ax.loglog(size, t*1000, color=c, ls=ls, marker=mk, markevery=30,
              lw=2, label=name, markersize=4)  # ms
ax.axvline(140, color='#555', ls='--', lw=1.5)   # 140 GB = 70B model FP16
ax.annotate('140 GB (70B weights)', xy=(140, 5e4), xytext=(8, 2e4),
            arrowprops=dict(arrowstyle='->'), fontsize=9)
ax.set_xlabel('Data volume (GB)')
ax.set_ylabel('All-reduce completion time (ms)')
ax.set_title('All-reduce time vs data volume,\nby interconnect tier', fontsize=11)
ax.legend(fontsize=8.5)
ax.grid(alpha=0.3, which='both')
ax.set_xlim(0.005, 200); ax.set_ylim(1, 2e6)
plt.tight_layout()
plt.savefig(base % (9, 9, 9), dpi=150); plt.close()
print('Ch09 done')

# ---- Ch11: serving stack flow ---- (compact 3x2 grid so it places 1:1 at column width)
fig, ax = plt.subplots(figsize=(6.0, 5.4))
ax.set_xlim(0, 12); ax.set_ylim(0, 10); ax.axis('off')
steps = ['Request stream', 'Scheduler', 'KV page table\n+ prefix cache']
row2  = ['Prefill pool', 'Decode pool', 'Output']
xs = [0.4, 4.4, 8.4]
def _row(yt, items):
    for i, s in enumerate(items):
        x = xs[i]
        ax.add_patch(FancyBboxPatch((x, yt), 3.2, 1.9, boxstyle='round,pad=0.02', fc='#3a6ea5', ec='none'))
        ax.text(x+1.6, yt+0.95, s, ha='center', va='center', color='white', fontsize=10, fontweight='bold')
    for i in range(len(items)-1):
        ax.annotate('', xy=(xs[i]+3.3, yt+0.95), xytext=(xs[i]+3.2, yt+0.95), arrowprops=dict(arrowstyle='-|>', lw=1.8, color='#555'))
_row(6.0, steps)
_row(1.6, row2)
# down arrow between rows (KV flows prefill -> decode)
ax.annotate('', xy=(4.4, 5.8), xytext=(4.4, 3.8), arrowprops=dict(arrowstyle='-|>', lw=2, color='#c0392b'))
ax.text(6.6, 4.8, 'KV transfer\n(prefill→decode)', fontsize=9, color='#c0392b', ha='left')
ax.text(6, 9.2, 'The serving stack: batching trades latency,\nprefix cache skips prefill, P/D split trades memory & throughput',
    fontsize=8.5, fontweight='bold', ha='center', color='#333')
plt.tight_layout()
plt.savefig(base % (11, 11, 11), dpi=150); plt.close()
print('Ch11 done')

print('batch part 1 complete')
