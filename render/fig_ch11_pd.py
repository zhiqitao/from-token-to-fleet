import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# ---- fig-11-1103: P/D Disaggregation Topology ----
# REDESIGN (reviewer, 2026-09-27): the prior version packed each pool with a
# 2x2 GPU grid plus two lines of rationale and the bridge with a multi-line
# KV-ownership paragraph and a bottom "why split" metrics block, so the figure
# read as a wall of text.  New version is three large, mostly-empty blocks
# (prefill pool | single KV-transfer line | decode pool) with MINIMAL labels.
# The ownership split, the why-split rationale and the FLOPs / HBM numbers now
# live in the manuscript caption, not in the diagram.
fig, ax = plt.subplots(figsize=(6.1, 4.4))
fig._hermes_print_sized = True   # print-size authored: regen must not re-boost/reflow
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')

# Title (short)
ax.text(0.5, 0.965, 'P/D disaggregation:', fontsize=9.2, fontweight='bold',
        ha='center', color='#1a1a1a')
ax.text(0.5, 0.925, 'a compute pool and a bandwidth pool, spliced once',
        fontsize=8.6, ha='center', color='#555')

# ---- Prefill pool (left, large empty block) ----
ax.add_patch(FancyBboxPatch((0.02, 0.18), 0.36, 0.66, boxstyle='round,pad=0.01',
                            fc='#fdecea', ec='#c0392b', lw=2.4))
ax.text(0.20, 0.76, 'PREFILL POOL', ha='center', va='center',
        fontsize=11.5, color='#c0392b', fontweight='bold')
for gx in [0.055, 0.135, 0.215, 0.295]:   # unlabelled GPU glyphs
    ax.add_patch(FancyBboxPatch((gx, 0.34), 0.06, 0.10, boxstyle='round,pad=0.005',
                                fc='#e67e22', ec='#a04000', lw=0.8))

# ---- Decode pool (right, large empty block) ----
ax.add_patch(FancyBboxPatch((0.62, 0.18), 0.36, 0.66, boxstyle='round,pad=0.01',
                            fc='#eaf2f8', ec='#27408b', lw=2.4))
ax.text(0.80, 0.76, 'DECODE POOL', ha='center', va='center',
        fontsize=11.5, color='#27408b', fontweight='bold')
for gx in [0.655, 0.735, 0.815, 0.895]:   # unlabelled GPU glyphs
    ax.add_patch(FancyBboxPatch((gx, 0.34), 0.06, 0.10, boxstyle='round,pad=0.005',
                                fc='#2980b9', ec='#154360', lw=0.8))

# ---- Single bridging transfer line ----
ax.annotate('', xy=(0.62, 0.55), xytext=(0.38, 0.55),
            arrowprops=dict(arrowstyle='<|-|>', lw=4.0, color='#a93226'))
ax.text(0.50, 0.68, 'KV TRANSFER', ha='center', va='center',
        fontsize=8.6, color='#a93226', fontweight='bold')

# ---- Input / output anchors (faint, single words) ----
ax.text(0.20, 0.06, 'prompt \u2192', ha='center', va='center', fontsize=8.5,
        color='#333', fontweight='bold')
ax.annotate('', xy=(0.20, 0.175), xytext=(0.20, 0.06),
            arrowprops=dict(arrowstyle='-|>', lw=1.4, color='#333'))
ax.text(0.80, 0.06, 'tokens \u2192', ha='center', va='center', fontsize=8.5,
        color='#333', fontweight='bold')
ax.annotate('', xy=(0.80, 0.175), xytext=(0.80, 0.06),
            arrowprops=dict(arrowstyle='-|>', lw=1.4, color='#333'))

plt.tight_layout()
plt.savefig('design/manuscript/chapter-11/figures/fig-11-1103.png', dpi=150)
plt.close()
print('fig-11-1103 done')
