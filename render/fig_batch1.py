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
fig, ax = plt.subplots(figsize=(6.5, 5.0))
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
ax.annotate('140 GB (70B weights)', xy=(140, 5e4), xytext=(1.6, 1.4e5),
            arrowprops=dict(arrowstyle='->'), fontsize=9)
ax.set_xlabel('Data volume (GB)')
ax.set_ylabel('All-reduce completion time (ms)')
ax.set_title('All-reduce time vs data volume,\nby interconnect tier', fontsize=10.5)
# legend OUTSIDE the axes (below) so it does not occlude the data
ax.legend(fontsize=8.5, loc='upper center', bbox_to_anchor=(0.5, -0.14), ncol=2, frameon=False)
ax.grid(alpha=0.3, which='both')
ax.set_xlim(0.005, 200); ax.set_ylim(1, 2e6)
plt.tight_layout(rect=(0, 0.08, 1, 1))
plt.savefig(base % (9, 9, 9), dpi=150); plt.close()
print('Ch09 done')

# ---- Ch11: serving stack flow ---- (vertical input->output flow; resource-coded; P/D split)
fig, ax = plt.subplots(figsize=(6.1, 5.9))
ax.set_xlim(0, 18); ax.set_ylim(0, 12); ax.axis('off')
BLUE='#3a6ea5'; GREEN='#27ae60'; ORANGE='#e67e22'; RED='#c0392b'; GREY='#555'; PURPLE='#6c3483'
def box(x,y,w,h,s,fc,fs=9.3):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.02',fc=fc,ec='none'))
    ax.text(x+w/2,y+h/2,s,ha='center',va='center',color='white',fontsize=fs,fontweight='bold')
def arrow(x1,y1,x2,y2,c=GREY,lw=2.0):
    ax.annotate('',xy=(x2,y2),xytext=(x1,y1),arrowprops=dict(arrowstyle='-|>',lw=lw,color=c))
# top: request -> scheduler
box(2.6,9.6,8.0,1.5,'Request stream\n(text -> tokens)',BLUE,fs=9.0)
arrow(6.6,9.6,6.6,8.7)
# scheduler + batching
box(2.6,7.4,8.0,1.2,'Scheduler +\ncontinuous batching',PURPLE,fs=8.4)
ax.text(10.9,8.0,'scheduling\n<-> latency',fontsize=7.2,color=PURPLE,ha='left',va='center')
arrow(6.6,7.4,6.6,6.8)
ax.text(6.6,6.55,'P/D split (two regimes)',fontsize=7.6,color=GREY,ha='center')
arrow(4.5,6.4,4.5,5.9); arrow(8.6,6.4,8.6,5.9)
# prefill (compute) and decode (bandwidth) pools
ax.add_patch(FancyBboxPatch((1.6,4.4),5.9,1.5,boxstyle='round,pad=0.02',fc=GREEN,ec='none'))
ax.text(4.55,5.15,'Prefill pool\ncompute -> TTFT',ha='center',va='center',color='white',fontsize=8.4,fontweight='bold')
ax.add_patch(FancyBboxPatch((8.6,4.4),6.0,1.5,boxstyle='round,pad=0.02',fc=ORANGE,ec='none'))
ax.text(11.6,5.15,'Decode pool\nbandwidth -> TPOT/ITL',ha='center',va='center',color='white',fontsize=8.2,fontweight='bold')
# shared KV cache band below both pools
ax.add_patch(FancyBboxPatch((1.6,2.4),12.4,1.4,boxstyle='round,pad=0.02',fc=RED,ec='none'))
ax.text(7.8,3.2,'KV cache - memory capacity -> concurrency',ha='center',va='center',color='white',fontsize=8.6,fontweight='bold')
ax.text(7.8,2.7,'PagedAttention (page table) + prefix cache',ha='center',va='center',color='white',fontsize=7.8,fontstyle='italic')
# prefill WRITES kv (down); decode READS/APPENDS kv (two-way)
arrow(4.55,4.4,4.55,3.8,RED,2.2)   # prefill populates KV (write)
ax.annotate('',xy=(11.6,3.8),xytext=(11.6,4.4),arrowprops=dict(arrowstyle='<|-|>',lw=2.0,color=RED))  # decode read+append (both ways)
ax.text(12.0,4.1,'KV read\n+append',fontsize=6.8,color=RED,ha='left',va='center')
# decode -> output (output sits to the right, clear of the KV band)
arrow(14.6,5.15,15.6,5.15)  # decode right edge -> output
box(15.7,4.55,2.3,1.2,'Output\ntokens',GREY,fs=8.4)
# legend row (bottom-left; label beside swatch, no clipping)
leg=[('Request',BLUE),('Scheduler',PURPLE),('Prefill',GREEN),('Decode',ORANGE),('KV',RED)]
for i,(lab,c) in enumerate(leg):
    x=1.6+i*2.9
    ax.add_patch(Rectangle((x,0.6),0.75,0.7,fc=c,ec='none'))
    ax.text(x+0.9,0.95,lab,ha='left',va='center',color='#333',fontsize=7.2)
ax.text(1.6,0.2,'legend: colour = the resource that stage trades / occupies',fontsize=7.0,color=GREY,ha='left')
# title
ax.text(7.0,11.4,'The serving stack: batching trades latency,\nprefix cache skips prefill, P/D split trades memory & throughput',
    fontsize=8.2,fontweight='bold',ha='center',color='#333')
plt.tight_layout()
plt.savefig(base % (11, 11, 11), dpi=150); plt.close()
print('Ch11 done')

print('batch part 1 complete')
