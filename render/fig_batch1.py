import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as _mpl
_mpl.rcParams['axes.formatter.use_mathtext']=False

from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

base = 'design/manuscript/chapter-%02d/figures/fig-%02d-%02d01.png'

# ---- Ch02 Fig 2.2 (arithmetic-intensity continuum / roofline) ----
# RETIRED: competes with the dedicated roofline asset render/fig_ch2_roofline.py
# -> design/manuscript/chapter-02/figures/fig-02-0201.{png,pdf}.  The reviewer (2026-09)
# demanded roofline + two regimes dominate over annotation; fig_ch2_roofline.py is a
# single log-log roofline with two large region shadings and minimal text.
# regen_figs.py must not clobber the redesigned asset.
print('fig-02-0201: see render/fig_ch2_roofline.py; Ch02 block retired')

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
# all-reduce completion ~ O(2*Nminus1/N * V / B_eff). Curves use EFFECTIVE bandwidths matched
# to the §9.4 worked example: NVSwitch 1.8, NVLink 0.9 TB/s (intra-node nominal), InfiniBand
# ~40 GB/s and RoCE2 ~2.5 GB/s (multi-node effective, incl. coding + contention) — NOT the
# nominal per-port peak, which is ~50 GB/s for both IB and RoCE (Table 9-1). Using effective
# values reconciles the figure with §9.4 (IB ~6.1 s, RoCE ~98 s at 140 GB).
size = np.logspace(-2, np.log10(300), 240)      # GB (cover past the 140 GB weight footprint)
bw = {'NVSwitch (1.8 TB/s)': 1800, 'NVLink (0.9 TB/s)': 900,
      'InfiniBand (~40 GB/s)': 40, 'RoCE2 (~2.5 GB/s)': 2.5}
data_per_byte = 1.75   # ring all-reduce moves ~2(N-1)/N * V; for N=8 nodes it is 1.75 (matches §9.4 worked example)
fig, ax = plt.subplots(figsize=(6.1, 4.7))
fig._hermes_print_sized = True   # regen must not re-boost/reflow
cols = {'NVSwitch (1.8 TB/s)': ('#27408b', '-', 'o'),
        'NVLink (0.9 TB/s)': ('#3a6ea5', '--', 's'),
        'InfiniBand (~40 GB/s)': ('#e67e22', '-.', '^'),
        'RoCE2 (~2.5 GB/s)': ('#c0392b', ':', 'D')}
for name, b in bw.items():
    c, ls, mk = cols[name]
    t = data_per_byte * size / b   # GB / (GB/s) = s
    ax.loglog(size, t*1000, color=c, ls=ls, marker=mk, markevery=30,
              lw=1.8, label=name, markersize=3.5)  # ms
ax.axvline(140, color='#555', ls='--', lw=1.3)   # 140 GB = 70B model FP16
ax.annotate('140 GB (70B weights)', xy=(140, 2e4), xytext=(2.2, 6e4),
            arrowprops=dict(arrowstyle='->'), fontsize=8.5)
ax.set_xlabel('Data volume (GB)', fontsize=9)
ax.set_ylabel('All-reduce completion time (ms)', fontsize=9)
ax.set_title('All-reduce time vs data volume,\nby interconnect tier', fontsize=9.5)
# ANALYTICAL/DERIVED tag in-plot (upper right whitespace)
ax.text(0.99, 0.94, 'ANALYTICAL [DERIVED]\n(t = 1.75·V/B, N=8 ring, effective B)', transform=ax.transAxes,
        fontsize=8, color='#8a5a00', ha='right', va='top')
ax.tick_params(labelsize=10)
# x-axis labelled tick covering the 140 GB weight-footprint reference
ax.set_xticks([0.01, 0.1, 1, 10, 100, 200])
ax.set_xticklabels(['0.01', '0.1', '1', '10', '100', '200'])
ax.set_xlim(0.01, 200)   # extend past 140 so the weight-footprint marker is in-plot
ax.set_ylim(1e-1, 1e6)
# legend OUTSIDE the axes (below) so it does not occlude the data
ax.legend(fontsize=8, loc='upper center', bbox_to_anchor=(0.5, -0.14), ncol=2, frameon=False)
ax.grid(alpha=0.3, which='both')
ax.set_xlim(0.005, 200); ax.set_ylim(1, 2e6)
plt.tight_layout(rect=(0, 0.08, 1, 1))
plt.savefig(base % (9, 9, 9), dpi=150); plt.close()
print('Ch09 done')

# ---- Ch11: serving = four concerns, not a layer stack ----
# REDESIGN (reviewer, 2026-09-27): the prior version packed each concern card
# with a mechanism line plus an italic trade-off note, burying the "orthogonal"
# claim under text.  New version makes the 2x2 orthogonality grid the dominant
# visual -- four large, empty cards (accent header only, mostly whitespace) with
# BIG concern labels, threaded by a single request -> output spine.  The
# per-concern mechanism and trade-off now live in the manuscript caption.
fig, ax = plt.subplots(figsize=(6.1, 5.2))
fig._hermes_print_sized = True   # print-size authored: regen must not re-boost/reflow
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
BLUE='#3a6ea5'; GREEN='#27ae60'; ORANGE='#e67e22'; RED='#c0392b'; GREY='#555'; PURPLE='#6c3483'

def box(x, y, w, h, fc, ec, lw=1.4):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.01', fc=fc, ec=ec, lw=lw))

def card(x, y, w, h, label, col, fill):
    box(x, y, w, h, fill, col, 2.0)
    ax.text(x + w / 2, y + h / 2, label, ha='center', va='center',
            fontsize=11.5, color=col, fontweight='bold')

# title
ax.text(0.5, 0.965, 'Serving = four orthogonal concerns, not a stack',
        fontsize=9.2, fontweight='bold', ha='center', color='#333')

# request stream (top) -> output (bottom) spine
box(0.30, 0.875, 0.40, 0.065, BLUE, BLUE, 0)
ax.text(0.5, 0.9075, 'Request stream', ha='center', va='center',
        color='white', fontsize=8.5, fontweight='bold')
ax.annotate('', xy=(0.5, 0.12), xytext=(0.5, 0.872),
            arrowprops=dict(arrowstyle='-|>', lw=1.7, color=GREY))
box(0.30, 0.045, 0.40, 0.065, GREY, GREY, 0)
ax.text(0.5, 0.0775, 'Output tokens', ha='center', va='center',
        color='white', fontsize=8.5, fontweight='bold')

# 2x2 orthogonality grid -- dominant, empty cards with BIG labels
card(0.045, 0.600, 0.415, 0.245, 'REQUEST\nSCHEDULING', PURPLE, '#f7f3fb')
card(0.540, 0.600, 0.415, 0.245, 'STATE\nMANAGEMENT', RED, '#fdecea')
card(0.045, 0.305, 0.415, 0.245, 'REUSE', GREEN, '#eafaf0')
card(0.540, 0.305, 0.415, 0.245, 'RESOURCE\nSPECIALISATION', ORANGE, '#fdf3e0')

plt.tight_layout()
plt.savefig(base % (11, 11, 11), dpi=150); plt.close()
print('Ch11 done')

print('batch part 1 complete')
