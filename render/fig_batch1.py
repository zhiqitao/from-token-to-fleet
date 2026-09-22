import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as _mpl
_mpl.rcParams['axes.formatter.use_mathtext']=False

from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

base = 'design/manuscript/chapter-%02d/figures/fig-%02d-%02d01.png'

# ---- Ch02: Decode vs prefill: an arithmetic-intensity CONTINUUM, not two boxes ----
# The old binary "decode=bandwidth / prefill=compute" chart taught a rule that Ch8
# later has to undo. This redesign places the two canonical operating points on an
# arithmetic-intensity axis split by the roofline ridge (~295 FLOP/byte), and shows
# the knobs (batch, context, precision) that move a point across the ridge.
fig, ax = plt.subplots(figsize=(6.1, 3.4))
ax.set_xscale('log')
ax.set_xlim(0.3, 2000)
ax.set_ylim(0, 1)
ax.axis('off')
# log axis from 0.3 to 2000
import matplotlib.ticker as mtick

# draw the axis
ax.annotate('', xy=(2000, 0.14), xytext=(0.3, 0.14),
            arrowprops=dict(arrowstyle='-|>', lw=1.6, color='#555'))
ax.text(0.35, 0.10, 'lower →', fontsize=8, color='#555', ha='left')
ax.text(1900, 0.10, '→ higher', fontsize=8, color='#555', ha='right')
ax.text(1000, 0.30, 'arithmetic intensity (FLOP/byte) →', fontsize=9, color='#333',
        ha='center', fontweight='bold')

# ridge line (from Ch8 ~295)
ridge = 295
ax.axvline(ridge, color='#c0392b', ls='--', lw=1.4)
ax.text(ridge*1.1, 0.62, 'roofline\nridge ~295', fontsize=8, color='#c0392b', fontweight='bold')

# memory-bound region (left of ridge)
ax.axvspan(0.3, ridge, color='#fdf0e7', alpha=0.5)
ax.text(4, 0.82, 'memory-bound\n(bandwidth)', fontsize=8, color='#8a3a12', ha='center', fontweight='bold')
# compute-bound region (right of ridge)
ax.axvspan(ridge, 2000, color='#eaf1fb', alpha=0.5)
ax.text(1200, 0.82, 'compute-bound\n(FLOPs)', fontsize=8, color='#1a3a6b', ha='center', fontweight='bold')

# canonical operating points
points = [
    ('decode @ low batch', 1.0, '#c0392b', 'HBM weight-stream per token:\n~1 FLOP/byte at batch-1 (Ch8)'),
    ('prefill @ 9.2K prompt', 180, '#27408b', '2·N·L over HBM weight stream:\nhigh intensity, near/above ridge'),
]
for name, x, col, note in points:
    ax.plot([x], [0.42], 'o', ms=10, color=col, clip_on=False)
    ax.annotate(name, xy=(x, 0.42), xytext=(x, 0.52), ha='center', fontsize=8.5,
                color=col, fontweight='bold', arrowprops=dict(arrowstyle='-', lw=0.8, color=col))
    ax.text(x, 0.20, note, fontsize=7, color='#555', ha='center')

# knobs that move the points
ax.text(60, 0.02, 'batch size ↑ · context ↑ · KV precision ↓ · kernel/hardware →  all move a point across the ridge',
        fontsize=7.5, color='#666', ha='center', style='italic')

plt.tight_layout(pad=0.2)
plt.savefig('design/manuscript/chapter-02/figures/fig-02-0201.png', dpi=200); plt.close()
print('Ch02 (continuum) done')

# ---- Ch04: Six-dimension workload characterization -> architectural decisions ----
# The six dimensions the chapter actually defines (§4.2.1): quality, traffic, token
# profile, latency, economic constraints, operational constraints.
fig, ax = plt.subplots(figsize=(12, 7))
ax.set_xlim(0, 14); ax.set_ylim(0, 10); ax.axis('off')
dims = ['Quality requirements', 'Traffic / concurrency', 'Token profile', 'Latency SLO', 'Economic constraints', 'Operational constraints']
cons = ['model size / type', 'concurrency & batching', 'KV cache size & prefill demand', 'TTFT/TPOT & batch window', 'host count & cost ceiling', 'multi-region vs. single-region']
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
fig, ax = plt.subplots(figsize=(6.1, 4.7))
cols = {'NVSwitch (1.8 TB/s)': ('#27408b', '-', 'o'),
        'NVLink (0.9 TB/s)': ('#3a6ea5', '--', 's'),
        'InfiniBand (0.4 TB/s)': ('#e67e22', '-.', '^'),
        'Ethernet (0.1 TB/s)': ('#c0392b', ':', 'D')}
for name, b in bw.items():
    c, ls, mk = cols[name]
    t = data_per_byte * size / b   # GB / (GB/s) = s
    ax.loglog(size, t*1000, color=c, ls=ls, marker=mk, markevery=30,
              lw=1.8, label=name, markersize=3.5)  # ms
ax.axvline(140, color='#555', ls='--', lw=1.3)   # 140 GB = 70B model FP16
ax.annotate('140 GB (70B weights)', xy=(140, 5e4), xytext=(1.6, 1.4e5),
            arrowprops=dict(arrowstyle='->'), fontsize=8.5)
ax.set_xlabel('Data volume (GB)', fontsize=9)
ax.set_ylabel('All-reduce completion time (ms)', fontsize=9)
ax.set_title('All-reduce time vs data volume,\nby interconnect tier', fontsize=9.5)
ax.tick_params(labelsize=10)
# legend OUTSIDE the axes (below) so it does not occlude the data
ax.legend(fontsize=8, loc='upper center', bbox_to_anchor=(0.5, -0.14), ncol=2, frameon=False)
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
