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
fig, ax = plt.subplots(figsize=(6.1, 3.1))
fig._hermes_print_sized = True
ax.set_xscale('log')
ax.set_xlim(0.3, 30000)
ax.set_ylim(0, 1.48)
ax.axis('off')
# log axis from 0.3 to 30000
import matplotlib.ticker as mtick
import matplotlib as _mpl
_mpl.rcParams['hatch.linewidth'] = 1.4
_mpl.rcParams['hatch.color'] = '#000000'

# ---- TOP ANNOTATION: the movement qualifier (prominent, own zone above the band) ----
ax.text(95, 1.44,
        'operating points are NOT fixed:',
        fontsize=8.5, color='#444', ha='center', va='top', fontweight='bold')
ax.text(95, 1.35,
        'batch · context · KV precision · kernel/hardware',
        fontsize=8.5, color='#555', ha='center', va='top')
ax.text(95, 1.26,
        'all move a point across the ridge',
        fontsize=8.5, color='#444', ha='center', va='top', fontweight='bold')

# ---- ROOFLINE REGIONS (shaded band, its own vertical zone) ----
ridge = 295
BAND_LO, BAND_HI = 0.30, 1.02
ax.axvline(ridge, color='#c0392b', ls='--', lw=1.4, ymin=BAND_LO, ymax=BAND_HI)
ax.text(ridge*1.35, 0.38, 'roofline\nridge ~295', fontsize=8, color='#c0392b', fontweight='bold')
ax.axvspan(0.3, ridge, color='#f6dcc8', alpha=0.55, hatch='///', ec='#5a2e08', lw=0, ymin=BAND_LO, ymax=BAND_HI)
ax.text(6, 1.00, 'memory-bound\n(bandwidth)', fontsize=8.5, color='#8a3a12', ha='center', va='top', fontweight='bold')
ax.axvspan(ridge, 30000, color='#c9d8ee', alpha=0.55, hatch='xxx', ec='#12294f', lw=0, ymin=BAND_LO, ymax=BAND_HI)
ax.text(4200, 1.00, 'compute-bound\n(FLOPs)', fontsize=8.5, color='#1a3a6b', ha='center', va='top', fontweight='bold')

# ---- OPERATING POINTS (inside the band, name above marker, note below it) ----
points = [
    ('decode @ low batch', 1.0, '#c0392b', 'o', 'HBM weight-stream per token:\n~1 FLOP/byte at batch-1 (Ch8)'),
    ('prefill @ 9.2K prompt', 9200, '#27408b', '^', '2·N·L over HBM weight stream:\n~9.2K FLOP/byte (high intensity)'),
]
for name, x, col, mk, note in points:
    ax.plot([x], [0.70], mk, ms=12, color=col, clip_on=False)
    # name clearly below the marker (wide gap so the dot never touches the label)
    ax.text(x, 0.50, name, ha='center', fontsize=10, color=col, fontweight='bold')
    ax.text(x, 0.34, note, fontsize=8, color='#444', ha='center', va='top', fontweight='bold')

# ---- BOTTOM BAND: a clean, self-contained x-axis ----
ax.annotate('', xy=(30000, 0.16), xytext=(0.3, 0.16),
            arrowprops=dict(arrowstyle='-|>', lw=1.7, color='#555'))
ax.text(0.35, 0.115, 'lower →', fontsize=8.5, color='#555', ha='left')
ax.text(29000, 0.115, '→ higher', fontsize=8.5, color='#555', ha='right')
ax.text(1000, 0.055, 'arithmetic intensity (FLOP/byte) →', fontsize=9.5, color='#333',
        ha='center', fontweight='bold')

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
fig._hermes_print_sized = True   # regen must not re-boost/reflow
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
# ANALYTICAL/DERIVED tag in-plot (upper right whitespace)
ax.text(0.99, 0.94, 'ANALYTICAL [DERIVED]\n(t ∝ 2·V/B)', transform=ax.transAxes,
        fontsize=8, color='#8a5a00', ha='right', va='top')
ax.tick_params(labelsize=10)
# legend OUTSIDE the axes (below) so it does not occlude the data
ax.legend(fontsize=8, loc='upper center', bbox_to_anchor=(0.5, -0.14), ncol=2, frameon=False)
ax.grid(alpha=0.3, which='both')
ax.set_xlim(0.005, 200); ax.set_ylim(1, 2e6)
plt.tight_layout(rect=(0, 0.08, 1, 1))
plt.savefig(base % (9, 9, 9), dpi=150); plt.close()
print('Ch09 done')

# ---- Ch11: serving = four concerns, not a layer stack ----
# The old top-down "serving stack" implied rigid layering. Present serving as four
# orthogonal concerns (request scheduling / state management / reuse / resource
# specialisation) that all act on the request stream in parallel -- none stacked on
# another. Arranged as a 2x2 concern matrix around the central request->output flow.
fig, ax = plt.subplots(figsize=(6.4, 5.9))
ax.set_xlim(0, 20); ax.set_ylim(0, 13); ax.axis('off')
BLUE='#3a6ea5'; GREEN='#27ae60'; ORANGE='#e67e22'; RED='#c0392b'; GREY='#555'; PURPLE='#6c3483'
def bbox(x,y,w,h,fc,ec='none',lw=0):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.02',fc=fc,ec=ec,lw=lw))
def jar(x1,y1,x2,y2,c=GREY,lw=2.0):
    ax.annotate('',xy=(x2,y2),xytext=(x1,y1),arrowprops=dict(arrowstyle='-|>',lw=lw,color=c))
def concern(x,y,w,h,name,col,mech,trade):
    bbox(x,y,w,h,'#fbfbfb',col,1.6)
    bbox(x,y+h-0.66,w,0.66,col)
    ax.text(x+w/2,y+h-0.33,name,ha='center',va='center',color='white',fontsize=8.2,fontweight='bold')
    ax.text(x+0.4,y+h-1.25,mech,ha='left',va='top',fontsize=7.4,color='#222')
    ax.text(x+0.4,y+0.32,trade,ha='left',va='center',fontsize=7.0,color=col,style='italic')

# title
ax.text(10,12.4,'Serving = four concerns, not a stack',fontsize=9.2,fontweight='bold',ha='center',color='#333')
ax.text(10,11.72,'orthogonal decisions - they interact, but none sits on top of another',
        fontsize=7.1,ha='center',color=GREY,style='italic')

# request stream (top)
bbox(6.0,10.2,8.0,1.25,BLUE)
ax.text(10,10.82,'Request stream\n(text \u2192 tokens)',ha='center',va='center',color='white',fontsize=8.5,fontweight='bold')

# concern matrix container
bbox(0.5,3.35,19.0,6.55,'#f4f6fa','#bbbbbb',1.0)
ax.text(1.0,9.62,'THE FOUR SERVING CONCERNS',fontsize=7.8,fontweight='bold',ha='left',color='#5a5a5a')

# 2x2 concern cards flanking the central flow
concern(1.0,3.75,7.9,2.55,'REQUEST SCHEDULING',PURPLE,
        'continuous batching: admit &\nevict at every decode step',
        'scheduling \u2194 latency \u00b7 utilization')
concern(11.1,3.75,7.9,2.55,'STATE MANAGEMENT',RED,
        'KV cache in fixed pages\n(PagedAttention page table)',
        'memory capacity \u2192 concurrency')
concern(1.0,6.85,7.9,2.55,'REUSE',GREEN,
        'prefix cache (RadixAttention / APC):\nreuse KV of shared context',
        're-prefill FLOPs & memory skipped')
concern(11.1,6.85,7.9,2.55,'RESOURCE SPECIALISATION',ORANGE,
        'P/D split: prefill pool (compute) +\ndecode pool (bandwidth)',
        'two regimes \u2192 two pools')

# central flow: request -> through the concern matrix -> tokens
jar(10,10.2,10,2.95,GREY,1.7)
ax.text(10.45,6.55,'all four in parallel',fontsize=6.9,color=GREY,ha='left',va='center',style='italic')

# output (bottom)
bbox(6.8,1.55,6.4,1.0,GREY)
ax.text(10,2.05,'Output tokens',ha='center',va='center',color='white',fontsize=8.2,fontweight='bold')

plt.tight_layout()
plt.savefig(base % (11, 11, 11), dpi=150); plt.close()
print('Ch11 done')

print('batch part 1 complete')
