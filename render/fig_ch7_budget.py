"""Fig 7.4 - The concurrency budget, split into TWO panels so the physical-memory
stack is not conflated with the derived concurrency count (publication review).

PANEL A (left): the physical on-host HBM stack.
    140 GB weights + ~64 GB runtime/workspace + ~436 GB KV budget = 640 GB pool.
    Includes the 8 x 80 GB per-rank geometry (gridlines + rank strip) and the
    aggregate-vs-per-rank warning.

PANEL B (right): the DERIVED concurrency count, shown as its own result frame.
    C(FP16) = 436 / 24.9037 ~ 17.5 -> integer floor 17 concurrent requests
    C(FP8)  = 436 / 13.448  ~ 32.4 -> integer floor 32 concurrent requests

Authored at column width so fonts print near-native, print-sized.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Rectangle

weights, runtime, kv = 140, 64, 436
total = weights + runtime + kv
kv_fp16_req, kv_fp8_req = 24.9037, 13.448
C_fp16, C_fp8 = kv / kv_fp16_req, kv / kv_fp8_req
halo = [pe.withStroke(linewidth=3.0, foreground='white')]

fig, (axA, axB) = plt.subplots(1, 2, figsize=(6.1, 3.6),
                               gridspec_kw={'width_ratios': [1.55, 1.0],
                                            'wspace': 0.18})
fig._hermes_print_sized = True

# ==================== PANEL A: physical memory stack ====================
axA.set_xlim(-12, total + 30)
axA.set_ylim(-1.35, 1.75)
axA.set_yticks([0])
axA.set_yticklabels(['KV 8-bit'], fontsize=9.5)
axA.set_xlabel('on-host HBM (GB, per 8×H100 host)', fontsize=9.5)
axA.spines['top'].set_visible(False)
axA.spines['right'].set_visible(False)
axA.tick_params(axis='x', labelsize=8.5)

axA.barh(0, weights, left=0, height=0.7, color='#3a6ea5', edgecolor='white', hatch='//', lw=0.5)
axA.barh(0, runtime, left=weights, height=0.7, color='#9aa0a6', edgecolor='white', hatch='xx', lw=0.5)
axA.barh(0, kv, left=weights + runtime, height=0.7, color='#6f9e5f', edgecolor='white', hatch='..', lw=0.5)

axA.text(weights/2, 0, '140 GB\nweights', ha='center', va='center', color='white',
         fontsize=9.5, fontweight='bold', path_effects=halo)
axA.text(weights + runtime/2, 0, '~64 GB\nruntime', ha='center', va='center', color='white',
         fontsize=9.5, fontweight='bold', path_effects=halo)
axA.text(weights + runtime + kv/2, 0, '~436 GB\nKV budget', ha='center', va='center',
         color='white', fontsize=9.5, fontweight='bold', path_effects=halo)

# 8 x 80 GB per-rank geometry
for g in range(80, 640, 80):
    axA.plot([g, g], [-0.32, 0.35], color='#3d3d3d', lw=1.0, ls=(0, (4, 2)), zorder=3)
rank_w = total / 8.0
strip_y = -0.92
for g in range(8):
    axA.add_patch(Rectangle((g*rank_w, strip_y), rank_w, 0.38, fc='#eef1f5', ec='#8a8a8a', lw=0.8))
    axA.text(g*rank_w + rank_w/2, strip_y + 0.19, f'{(g+1)*80:.0f}G', ha='center',
             va='center', fontsize=7.0, color='#555')
axA.text(0.0, strip_y - 0.14, '8 × 80 GB ranks — the aggregate screen ≠ a per-rank fit guarantee',
         ha='left', va='top', fontsize=7.2, color='#c0392b', style='italic')

# ==================== PANEL B: derived concurrency ====================
axB.set_xlim(0, 1); axB.set_ylim(-0.6, 4.6); axB.axis('off')
axB.text(0.5, 4.30, 'derived concurrency', fontsize=9.8, fontweight='bold',
         ha='center', va='center', color='#333')
axB.text(0.5, 3.92, 'C = KV budget ÷ KV/request', fontsize=8.4, ha='center',
         va='center', color='#555', style='italic')

def slot_row(ax, ycen, name, cval, cint, req, color):
    ax.text(0.10, ycen, name, fontsize=9.0, fontweight='bold', ha='left', va='center', color=color)
    ax.text(0.10, ycen - 0.40, f'C ≈ {cval:.1f}', fontsize=11, fontweight='bold',
            ha='left', va='center', color=color)
    ax.text(0.55, ycen - 0.40, f'(÷ {req:.3f} GB/request)', fontsize=6.8,
            ha='left', va='center', color='#777')
    ax.text(0.10, ycen - 0.78, f'→ integer floor {cint} requests', fontsize=8.0,
            ha='left', va='center', color='#444')

slot_row(axB, 3.10, 'FP16 / 8-bit KV', C_fp16, 17, kv_fp16_req, '#27408b')
slot_row(axB, 1.50, 'FP8 KV',          C_fp8,  32, kv_fp8_req,  '#6f9e5f')

axB.text(0.5, 0.15, 'KV slot ticks on the FP16 bar mark\nthe per-request boundaries.',
         fontsize=7.2, ha='center', va='center', color='#777', style='italic')

fig.suptitle("Concurrency budget: where a 70B host's 640 GB pool goes", fontsize=11)
plt.subplots_adjust(left=0.12, right=0.97, top=0.86, bottom=0.18)
plt.savefig('design/manuscript/chapter-07/figures/fig-07-0704.png', dpi=150)
import matplotlib as mpl
with mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-07/figures/fig-07-0704.pdf', format='pdf')
plt.close()
print('wrote fig-07-0704 (two panels: physical stack | derived concurrency)')
