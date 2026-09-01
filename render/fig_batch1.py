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
ax.bar(['decode\n(needed)', 'H100\n(supply)'], [5.6, 3.35], color=['#c0392b', '#3a6ea5'])
for i, v in enumerate([5.6, 3.35]):
    ax.text(i, v+0.1, f'{v} TB/s', ha='center', fontweight='bold')
ax.set_ylabel('HBM bandwidth (TB/s)')
ax.set_title('Decode: HBM-bandwidth-bound\n(5.6 needed > 3.35 supply)')
ax.grid(alpha=0.3, axis='y')
# right: required prefill compute RATE (~1.2 PFLOPS) vs H100 peak RATE (0.989 PFLOPS)
ax = axes[1]
ax.bar(['prefill\n(req. rate)', 'H100\n(peak rate)'], [prefill_rate, 0.989], color=['#c0392b', '#3a6ea5'])
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
fig, ax = plt.subplots(figsize=(12, 8))
ax.set_xlim(0, 14); ax.set_ylim(0, 10); ax.axis('off')
# Source node top-left
ax.add_patch(FancyBboxPatch((1.0, 8.3), 3.6, 1.4, boxstyle='round,pad=0.02', fc='#3a6ea5', ec='none'))
ax.text(2.8, 9.0, 'Workload\nCharacterization', ha='center', va='center', color='white', fontweight='bold')
# Five surfaces in a single vertical column on the right; arrows run horizontally
# from the source's right edge to each box's left edge -- no crossings.
surfaces = ['Capability / quality', 'Latency / compute', 'Context / KV cost', 'Cost / token', 'RAG vs end-to-end']
for i, s in enumerate(surfaces):
    y = 7.6 - i * 1.35
    ax.annotate('', xy=(6.0, y), xytext=(4.7, y),
                arrowprops=dict(arrowstyle='-|>', lw=1.5, color='#c0392b'))
    ax.add_patch(FancyBboxPatch((6.2, y - 0.35), 6.0, 0.7, boxstyle='round,pad=0.02', fc='#e67e22', ec='none'))
    ax.text(9.2, y, s, ha='center', va='center', color='white', fontsize=11)
ax.text(7, 0.6, 'Model selection surface (driven by workload, not vice-versa)',
        fontsize=12, fontweight='bold', ha='center')
plt.tight_layout()
plt.savefig(base % (5, 5, 5), dpi=150); plt.close()
print('Ch05 done')

# ---- Ch09: collective completion time vs data volume (the promised chart) ----
# all-reduce completion ~ O(2 data / B_eff); lines for the interconnect tiers
size = np.logspace(-2, 2, 200)      # GB
bw = {'NVSwitch (1.8 TB/s)': 1800, 'NVLink (0.9 TB/s)': 900,
      'InfiniBand (0.4 TB/s)': 400, 'Ethernet (0.1 TB/s)': 100}
data_per_byte = 2.0   # all-reduce ~2x data across the tree
fig, ax = plt.subplots(figsize=(9, 5.5))
cols = {'NVSwitch (1.8 TB/s)': '#27408b', 'NVLink (0.9 TB/s)': '#3a6ea5',
        'InfiniBand (0.4 TB/s)': '#e67e22', 'Ethernet (0.1 TB/s)': '#c0392b'}
for name, b in bw.items():
    t = data_per_byte * size / b   # GB / (GB/s) = s
    ax.loglog(size, t*1000, color=cols[name], lw=2, label=name)  # ms
ax.axvline(140, color='#555', ls='--', lw=1.5)   # 140 GB = 70B model FP16
ax.annotate('140 GB (70B weights)', xy=(140, 5e4), xytext=(8, 2e4),
            arrowprops=dict(arrowstyle='->'), fontsize=9)
ax.set_xlabel('Data volume (GB)')
ax.set_ylabel('All-reduce completion time (ms)')
ax.set_title('Ch09 — all-reduce time vs data volume, by interconnect tier')
ax.legend(fontsize=8)
ax.grid(alpha=0.3, which='both')
ax.set_xlim(0.005, 200); ax.set_ylim(1, 2e6)
plt.tight_layout()
plt.savefig(base % (9, 9, 9), dpi=150); plt.close()
print('Ch09 done')

# ---- Ch11: serving stack flow ----
fig, ax = plt.subplots(figsize=(13, 4.6))
ax.set_xlim(0, 16); ax.set_ylim(0, 4.6); ax.axis('off')
steps = ['Request\nstream', 'Scheduler', 'KV page table\n+ prefix cache', 'Prefill pool', 'Decode pool', 'Output']
xs = [0.3, 2.8, 5.3, 8.0, 10.6, 13.2]
for i, (s, x) in enumerate(zip(steps, xs)):
    ax.add_patch(FancyBboxPatch((x, 1.6), 2.2, 1.6, boxstyle='round,pad=0.02', fc='#3a6ea5', ec='none'))
    ax.text(x+1.1, 2.4, s, ha='center', va='center', color='white', fontsize=9.5, fontweight='bold')
    if i < len(steps)-1:
        ax.annotate('', xy=(x+2.4, 2.4), xytext=(x+2.2, 2.4), arrowprops=dict(arrowstyle='-|>', lw=2, color='#555'))
# KV-transfer edge from Prefill pool back to Decode pool (continuous batching moves KV)
ax.annotate('', xy=(10.6, 2.0), xytext=(10.2, 1.0), arrowprops=dict(arrowstyle='-|>', lw=1.8, color='#c0392b',
            connectionstyle='arc3,rad=0.25'))
ax.text(10.0, 0.55, 'KV transfer\n(prefill→decode)', fontsize=8.5, color='#c0392b', ha='center')
# mechanism tags under each box
ax.text(3.9, 1.1, 'batching: latency↔throughput', fontsize=7.5, color='#555', ha='center')
ax.text(6.6, 1.1, 'prefix cache: skips prefill', fontsize=7.5, color='#555', ha='center')
ax.text(9.2, 0.0, 'P/D split: memory↔throughput\nKV passes between pools', fontsize=7.5, color='#c0392b', ha='center')
ax.text(8, 4.3, 'The serving stack: batching trades latency, prefix cache skips prefill, P/D split trades memory & throughput',
        fontsize=10.5, fontweight='bold', ha='center', color='#333')
plt.tight_layout()
plt.savefig(base % (11, 11, 11), dpi=150); plt.close()
print('Ch11 done')

print('batch part 1 complete')
