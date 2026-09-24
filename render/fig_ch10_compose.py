#!/usr/bin/env python3
"""fig-10-1002: Composing the parallel dimensions (a concrete DP x TP x PP + EP).

PASS-24 fix: the Archify version was fully abstract (three generic bands with an
up-pointing 'composition' arrow, no model/GPU grid, no CP, no partitioned/replicated
encoding). This shows the composition CONCRETELY: a single PP stage decomposed into a
2x2 DP x TP GPU grid, with the weight matrix TP-sharded, the batch DP-sharded, and
the MoE experts EP-sharded across the same four GPUs (all-to-all), plus an explicit
per-dimension PARTITIONED / REPLICATED / COMMUNICATION annotation row. The reading
order is top-down (PP stage -> grid -> per-dimension split), with CP noted as an
optional sequence-axis split.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

W = 6.1
FS = 9.2
fig, ax = plt.subplots(figsize=(W, W*1.02))
fig._hermes_print_sized = True
ax.set_xlim(0, 10); ax.set_ylim(-3.8, 9.4); ax.axis('off')

# ---- title ----
ax.text(5.0, 9.05, 'Composing the parallel dimensions (concrete)', ha='center', va='center',
        fontsize=10.5, fontweight='bold', color='#1a1a1a')

# ---- PP stage container (top) ----
ax.add_patch(FancyBboxPatch((0.5, 7.5), 9.0, 1.15, boxstyle='round,pad=0.02,rounding_size=0.2',
                            fc='#eef3ee', ec='#2e9e63', lw=1.4))
ax.text(5.0, 8.35, 'one PP stage', ha='center', va='center', fontsize=FS+0.4, fontweight='bold', color='#1e5c3a')
ax.text(5.0, 7.85, 'a DP \u00d7 TP \u00d7 EP mesh of GPUs (pipeline divides the model into stages)', ha='center',
        va='center', fontsize=FS-0.7, color='#444')
ax.annotate('', xy=(3.2, 7.5), xytext=(0.9, 6.05),
            arrowprops=dict(arrowstyle='-|>', lw=1.4, color='#2e9e63'))
ax.text(3.35, 6.75, 'stage boundary \u2192 next\nstage (P2P activations)', fontsize=FS-1.1, color='#2e9e63',
        ha='left', va='center')
ax.annotate('', xy=(5.0, 7.55), xytext=(5.0, 6.05),
            arrowprops=dict(arrowstyle='-|>', lw=1.4, color='#555'))

# ---- 2x2 GPU grid (DP x TP) with model splits ----
grid = {}
gx0, gy0, cw, ch, gxs, gys = 1.2, 3.3, 3.5, 1.35, [1.2, 4.9], [4.4, 2.9]
for r, gy in enumerate(gys):
    for c, gx in enumerate(gxs):
        grid[(r, c)] = (gx, gy)
        ax.add_patch(FancyBboxPatch((gx, gy), cw, ch, boxstyle='round,pad=0.02,rounding_size=0.15',
                                    fc='#d3e0f2', ec='#27408b', lw=1.3))
        ax.text(gx+cw/2, gy+ch-0.35, f'GPU {r*2+c+1}', ha='center', va='center', fontsize=FS-0.6,
                fontweight='bold', color='#16295c')
        ax.text(gx+cw/2, gy+0.5, f'(DP rank {c+1} \u00b7 TP rank {r+1})', ha='center', va='center',
                fontsize=FS-1.4, color='#3a5a9a')

# TP: weight matrix sharded across the 2 rows (banner in the clear gap above the grid,
# so it does NOT overlap the GPU rank labels)
ax.add_patch(FancyBboxPatch((1.1, 6.0), 7.9, 0.42, boxstyle='round,pad=0.02', fc='#c0392b', ec='none', alpha=0.25))
ax.text(5.05, 6.21, 'W (weight matrix) \u2014 TP-sharded across the 2 TP rows', ha='center', va='center',
        fontsize=FS-1.0, color='#7b241c', fontweight='bold')
# DP: batch sharded across the 2 columns
ax.add_patch(FancyBboxPatch((1.1, 2.02), 7.2, 0.42, boxstyle='round,pad=0.02', fc='#2e9e63', ec='none', alpha=0.25))
ax.text(5.0, 2.23, 'data batch \u2014 DP-sharded across the 2 DP columns', ha='center', va='center',
        fontsize=FS-1.0, color='#1e5c3a', fontweight='bold')

# ---- EP: MoE experts sharded across the 4 GPUs (all-to-all), to the right ----
ax.add_patch(FancyBboxPatch((0.5, 0.7), 9.0, 0.95, boxstyle='round,pad=0.02,rounding_size=0.15',
                            fc='#fdeecb', ec='#c98a1e', lw=1.3))
ax.text(5.0, 1.32, 'EP: MoE experts sharded across all 4 GPUs \u2014 token \u2192 expert = all-to-all', ha='center',
        va='center', fontsize=FS-0.9, color='#8a5a12', fontweight='bold')
ax.text(5.0, 0.9, 'experts 1-15 \u00b7 each GPU holds its slice; attention/shared weights replicated', ha='center',
        va='center', fontsize=FS-1.5, color='#6a4a12')

# ---- per-dimension annotation: PARTITIONED / REPLICATED / COMMUNICATION ----
ax.add_patch(FancyBboxPatch((0.5, -0.35), 9.0, 0.85, boxstyle='round,pad=0.02,rounding_size=0.12',
                            fc='#f4f4f4', ec='#bbbbbb', lw=0.9))
cols = [('dimension', 0.9, '#444', 'normal'),
        ('PARTITIONED', 3.1, '#27408b', 'bold'),
        ('REPLICATED', 6.1, '#555', 'bold'),
        ('COMMUNICATION', 8.9, '#a53226', 'bold')]
for lbl, x, col, wg in cols:
    ax.text(x, 0.08, lbl, ha='center', va='center', fontsize=FS-1.2, color=col, fontweight=wg)
rows = [('TP', 'W rows', 'activations', 'all-reduce'),
        ('PP', 'layers', 'boundary activations', 'P2P'),
        ('DP', 'data batch', 'model + optimizer', 'all-reduce'),
        ('EP', 'MoE experts', 'attn + weights', 'all-to-all'),
        ('CP (opt)', 'token sequence', 'model weights', 'ring')]
ax.annotate('', xy=(5.0, -0.70), xytext=(5.0, -0.35),
            arrowprops=dict(arrowstyle='-|>', lw=1.2, color='#555'))
yy = -1.05
for r in rows:
    ax.text(0.9, yy, r[0], ha='center', va='center', fontsize=FS-1.2, color='#333', fontweight='bold')
    ax.text(3.1, yy, r[1], ha='center', va='center', fontsize=FS-1.5, color='#333')
    ax.text(6.1, yy, r[2], ha='center', va='center', fontsize=FS-1.5, color='#444')
    ax.text(8.9, yy, r[3], ha='center', va='center', fontsize=FS-1.5, color='#7b241c')
    yy -= 0.34

out = 'design/manuscript/chapter-10/figures/fig-10-1002.png'
plt.savefig(out, dpi=170)
plt.close()
print('wrote fig-10-1002 (concrete composition)')
