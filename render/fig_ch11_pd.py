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
#
# P2-04 FIX (independent review): the single schematic drew a prefill 8xH100
# host and a decode 8xH100 host (i.e. an INTER-HOST link) while the caption
# quoted the on-node 450 GB/s NVLink number first and the 40 GB/s fabric
# second, so the two bandwidths were attached to one ambiguous topology.
# The figure is now SPLIT into the two cases it actually describes:
#   (A) within-NVLink-domain P/D separation  -> 450 GB/s (on-node)
#   (B) cross-host disaggregation            -> 40 GB/s (fabric)
# and the aggregate KV-migration budget caveat (35 GB/request x 40 req/s
# = 1.4 TB/s of payload) is stated once, as a figure footer.
# Numbers are unchanged; only topology / labelling / annotation moved.
# Layout is checked with render/scratch layout probe: no text straddles a box
# border and no two text spans overlap (all authored sizes >= 8.2pt, figure
# is print-size authored at the 6.10in column, so placed size = authored).
fig, ax = plt.subplots(figsize=(6.1, 4.7))
fig._hermes_print_sized = True   # print-size authored: regen must not re-boost/reflow
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')

# Title (short)
ax.text(0.5, 0.965, 'P/D disaggregation: two cases, two different KV links',
        fontsize=9.6, fontweight='bold', ha='center', color='#1a1a1a')
ax.text(0.5, 0.925, 'the split is the same; the transfer link — and its cost — is not',
        fontsize=8.6, ha='center', color='#555')

# =========================== PANEL A =====================================
# (A) prefill + decode partitions INSIDE ONE 8xH100 host = one NVLink domain.
ax.text(0.255, 0.875, 'A. Within one NVLink domain', fontsize=9.0,
        fontweight='bold', ha='center', color='#1a1a1a')
ax.text(0.255, 0.825, '~35 GB ≈ 0.08 s (on-node)', fontsize=8.4,
        ha='center', color='#2b2b2b')

# host = one NVLink domain
ax.add_patch(FancyBboxPatch((0.03, 0.34), 0.45, 0.44, boxstyle='round,pad=0.01',
                            fc='#fdfdfd', ec='#7f8c8d', lw=1.6))
ax.text(0.255, 0.745, '8× H100 host', fontsize=8.4,
        ha='center', va='center', color='#444')

def _gpu_grid(x0, y0, fc, ec, cols=2, rows=2, gx=0.045, gy=0.07, pad=0.012):
    for c in range(cols):
        for r in range(rows):
            ax.add_patch(FancyBboxPatch((x0 + pad + c * (gx + 0.015),
                                         y0 + pad + r * (gy + 0.015)),
                                        gx, gy, boxstyle='round,pad=0.004',
                                        fc=fc, ec=ec, lw=0.8))

# prefill partition (4 of the 8 GPUs)
ax.add_patch(FancyBboxPatch((0.07, 0.38), 0.13, 0.34, boxstyle='round,pad=0.008',
                            fc='#fdecea', ec='#c0392b', lw=1.8))
ax.text(0.135, 0.685, 'PREFILL', fontsize=8.8, fontweight='bold',
        ha='center', va='center', color='#c0392b')
ax.text(0.135, 0.635, '4 GPUs', fontsize=8.2, ha='center', va='center', color='#2b2b2b')
_gpu_grid(0.07, 0.38, '#e67e22', '#a04000')

# decode partition (the other 4 GPUs)
ax.add_patch(FancyBboxPatch((0.31, 0.38), 0.13, 0.34, boxstyle='round,pad=0.008',
                            fc='#eaf2f8', ec='#27408b', lw=1.8))
ax.text(0.375, 0.685, 'DECODE', fontsize=8.8, fontweight='bold',
        ha='center', va='center', color='#27408b')
ax.text(0.375, 0.635, '4 GPUs', fontsize=8.2, ha='center', va='center', color='#2b2b2b')
_gpu_grid(0.31, 0.38, '#2980b9', '#154360')

# KV transfer, on-node (bandwidth stacked so it stays inside the link gap)
ax.annotate('', xy=(0.303, 0.55), xytext=(0.207, 0.55),
            arrowprops=dict(arrowstyle='-|>', lw=3.2, color='#a93226'))
ax.text(0.255, 0.605, 'KV', fontsize=8.4, fontweight='bold',
        ha='center', va='center', color='#a93226')
ax.text(0.255, 0.505, '450', fontsize=8.4, fontweight='bold',
        ha='center', va='center', color='#a93226')
ax.text(0.255, 0.455, 'GB/s', fontsize=8.4, fontweight='bold',
        ha='center', va='center', color='#a93226')

# I/O anchors
ax.text(0.135, 0.19, 'prompt', fontsize=8.5, color='#333',
        fontweight='bold', ha='center', va='center')
ax.annotate('', xy=(0.135, 0.335), xytext=(0.135, 0.215),
            arrowprops=dict(arrowstyle='-|>', lw=1.4, color='#333'))
ax.text(0.375, 0.19, 'generated tokens →', fontsize=8.5, color='#333',
        fontweight='bold', ha='center', va='center')
ax.annotate('', xy=(0.375, 0.215), xytext=(0.375, 0.335),
            arrowprops=dict(arrowstyle='-|>', lw=1.4, color='#333'))

# =========================== PANEL B =====================================
# (B) separate prefill host and decode host = the fabric is the KV link.
ax.text(0.745, 0.875, 'B. Across hosts (fabric)', fontsize=9.0,
        fontweight='bold', ha='center', color='#1a1a1a')
ax.text(0.745, 0.825, '~35 GB ≈ 0.9 s (cross-host)', fontsize=8.4,
        ha='center', color='#2b2b2b')

def _host_box(x0, label, fc, ec, gfc, gec):
    w = 0.177
    ax.add_patch(FancyBboxPatch((x0, 0.40), w, 0.32, boxstyle='round,pad=0.008',
                                fc=fc, ec=ec, lw=2.0))
    ax.text(x0 + w / 2, 0.685, label, fontsize=8.6, fontweight='bold',
            ha='center', va='center', color=ec)
    ax.text(x0 + w / 2, 0.635, '8× H100 host', fontsize=8.2,
            ha='center', va='center', color='#2b2b2b')
    # 8 GPU glyphs = the 8-GPU host (4 x 2)
    for c in range(4):
        for r in range(2):
            ax.add_patch(FancyBboxPatch((x0 + 0.022 + c * 0.037, 0.44 + r * 0.085),
                                        0.030, 0.07, boxstyle='round,pad=0.003',
                                        fc=gfc, ec=gec, lw=0.7))

_host_box(0.515, 'PREFILL', '#fdecea', '#c0392b', '#e67e22', '#a04000')
_host_box(0.798, 'DECODE', '#eaf2f8', '#27408b', '#2980b9', '#154360')

# KV transfer, cross-host (bandwidth stacked so it stays inside the link gap)
ax.annotate('', xy=(0.79, 0.54), xytext=(0.70, 0.54),
            arrowprops=dict(arrowstyle='-|>', lw=3.2, color='#a93226'))
ax.text(0.745, 0.595, 'KV', fontsize=8.4, fontweight='bold',
        ha='center', va='center', color='#a93226')
ax.text(0.745, 0.495, '40', fontsize=8.4, fontweight='bold',
        ha='center', va='center', color='#a93226')
ax.text(0.745, 0.445, 'GB/s', fontsize=8.4, fontweight='bold',
        ha='center', va='center', color='#a93226')

# I/O anchors
ax.text(0.604, 0.19, 'prompt', fontsize=8.5, color='#333',
        fontweight='bold', ha='center', va='center')
ax.annotate('', xy=(0.604, 0.395), xytext=(0.604, 0.215),
            arrowprops=dict(arrowstyle='-|>', lw=1.4, color='#333'))
ax.text(0.887, 0.19, 'generated tokens →', fontsize=8.5, color='#333',
        fontweight='bold', ha='center', va='center')
ax.annotate('', xy=(0.887, 0.215), xytext=(0.887, 0.395),
            arrowprops=dict(arrowstyle='-|>', lw=1.4, color='#333'))

# ---- aggregate KV-migration budget caveat (stated once, for both cases) ----
ax.text(0.5, 0.13, 'Caveat — aggregate KV migration at peak:',
        fontsize=8.4, fontweight='bold', ha='center', va='center', color='#7b241c')
ax.text(0.5, 0.085, '35 GB/request × 40 req/s = 1.4 TB/s of payload.',
        fontsize=8.4, fontweight='bold', ha='center', va='center', color='#7b241c')
ax.text(0.5, 0.035, 'Per-request times assume an unshared link; '
        '1.4 TB/s exceeds any single link above.',
        fontsize=8.4, ha='center', va='center', color='#7b241c')

plt.tight_layout()
plt.savefig('design/manuscript/chapter-11/figures/fig-11-1103.png', dpi=350)
import matplotlib as mpl
with mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-11/figures/fig-11-1103.pdf', format='pdf')
plt.close()
print('fig-11-1103 done')