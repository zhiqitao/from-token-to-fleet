import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# =====================================================================
# fig-12-1201 "Candidate architecture synthesis"
# ---------------------------------------------------------------------
# REDESIGN: the prior version was 3 stacked bar panels comparing bare
# candidate configurations.  A review demanded a figure that visualizes
# the SYNTHESIS REASONING CHAIN itself, so this version draws the
# constraint-driven generation process as a clean box-and-arrow vertical
# flow at single-column width:
#
#   REQUIREMENTS  ->  CONSTRAINTS (hard gates)  ->  CANDIDATES
#        ->  TEST AGAINST (memory / latency / economics)
#        ->  SURVIVORS vs REJECTED
#
# All numbers are traced to Table 12.1 / §3 (chapter-12.md):
#   weights 140/140/14 GB, KV 24/24/6 GB  -> total 164/164/20 GB.
#   8xH100 aggregate ceiling 640 GB; single H100 ceiling 80 GB.
#   prefill (a) ~19.8K, P/D prefill pool ~19.8K.
#   (c) KV-quant 7B fails the QUALITY gate -> excluded (no throughput bar).
# Throughput demand from the canonical case: ~92K input tok/s average.
# =====================================================================

fig, ax = plt.subplots(figsize=(6.1, 7.9))
fig._hermes_print_sized = True   # print-size authored: regen must not re-boost/reflow
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')


def box(x, y, w, h, fc, ec, lw=1.4, r=0.035):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle=f"round,pad=0,rounding_size={r}",
                                fc=fc, ec=ec, lw=lw, zorder=2))


def arrow(x0, y0, x1, y1, color='#444'):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1),
                                 arrowstyle='-|>', mutation_scale=14,
                                 lw=1.6, color=color, zorder=1))


def note(x, y, s, size=7.4, color='#333', weight='normal', ha='center'):
    ax.text(x, y, s, fontsize=size, color=color, fontweight=weight,
            ha=ha, va='center', zorder=3)


X0, W = 0.06, 0.88   # box left edge & width for full-width stages
CX = X0 + W / 2      # center x for full-width boxes

# ---------------------------------------------------------------------
# Stage 1 — REQUIREMENTS
# ---------------------------------------------------------------------
box(X0, 0.885, W, 0.085, '#eaf1fb', '#3a6ea5')
note(CX, 0.930, '① REQUIREMENTS  —  canonical enterprise-Q&A RAG workload',
     size=9.2, color='#27408b', weight='bold')
note(CX, 0.900, '~2,000 users · ~10/40 rps · 9.2K-in/300-out · quality ~70B', size=7.6)
arrow(CX, 0.885, CX, 0.850)

# ---------------------------------------------------------------------
# Stage 2 — CONSTRAINTS (the hard gates every candidate must pass)
# ---------------------------------------------------------------------
box(X0, 0.755, W, 0.085, '#fdf3e0', '#d68910')
note(CX, 0.800, '② CONSTRAINTS  —  hard gates',
     size=9.2, color='#935116', weight='bold')
note(CX, 0.770, 'memory (residency ≤ host) · latency (TTFT/TPOT) · economics (per-host ceiling)', size=7.6)
arrow(CX, 0.755, CX, 0.720)

# ---------------------------------------------------------------------
# Stage 3 — CANDIDATES (generate two or three satisfying the gates)
# ---------------------------------------------------------------------
box(X0, 0.625, W, 0.085, '#e7f5ec', '#1e8449')
note(CX, 0.670, '③ GENERATE CANDIDATES',
     size=9.2, color='#145a32', weight='bold')
note(CX, 0.640, '(a) 8×H100 + prefix cache   ·   (b) P/D-disaggregated 2-pool   ·   (c) KV-quantized 7B', size=7.6)
arrow(CX, 0.625, CX, 0.585)

# ---------------------------------------------------------------------
# Stage 4 — TEST AGAINST memory / latency / economics
# (container is tall; header sits CLEAR of the candidate rows below it)
# ---------------------------------------------------------------------
box(X0, 0.200, W, 0.355, '#f4f4f4', '#555555')
note(CX, 0.527, '④ TEST AGAINST  memory · latency · economics',
     size=9.2, color='#333', weight='bold')

rows = [
    dict(name='(a) 8×H100 + prefix cache',
         gate='MEM ✓ · latency ✓ · cost ✓  |  but prefill ~19.8K ≪ ~92K needed',
         res='✗ capacity (needs ~5 hosts)',
         edge='#3a6ea5', rescol='#7f8c8d'),
    dict(name='(b) P/D-disaggregated 2-pool',
         gate='MEM ✓ · latency ✓ · 2 hosts + fabric (~2× capex)',
         res='✓ survives as the at-scale answer',
         edge='#1e8449', rescol='#1e8449'),
    dict(name='(c) KV-quantized 7B',
         gate='MEM ✓ · cheapest (1 H100)  |  but fails the QUALITY gate',
         res='✗ EXCLUDED',
         edge='#c0392b', rescol='#c0392b'),
]

ry = 0.420          # bottom of first candidate row; its top (0.505) sits well below the header
rh = 0.085
gap = 0.018
for r in rows:
    box(X0 + 0.02, ry, W - 0.04, rh, '#ffffff', r['edge'], lw=1.3, r=0.02)
    ax.text(X0 + 0.045, ry + rh * 0.84, r['name'], fontsize=8.6,
            fontweight='bold', color=r['edge'], ha='left', va='center', zorder=3)
    ax.text(X0 + 0.045, ry + rh * 0.48, r['gate'],
            fontsize=6.7, color='#555', ha='left', va='center', zorder=3)
    ax.text(X0 + 0.045, ry + rh * 0.15, r['res'],
            fontsize=6.6, color=r['rescol'], fontweight='bold',
            ha='left', va='center', zorder=3)
    ry -= (rh + gap)

arrow(CX, 0.200, CX, 0.186)

# ---------------------------------------------------------------------
# Stage 5 — OUTCOMES: SURVIVORS vs REJECTED
# ---------------------------------------------------------------------
sx = X0 + 0.02
sw = (W - 0.04) * 0.58
box(sx, 0.070, sw, 0.112, '#e7f5ec', '#1e8449')
note(sx + sw / 2, 0.160, '⑤ OUTCOME — SURVIVORS', size=8.6, color='#145a32', weight='bold')
note(sx + sw / 2, 0.113,
     '(a) per-request-latency baseline\n(b) at-scale P/D answer — carried to Ch.13–14',
     size=6.9)

bx = sx + sw + 0.03
bw = W - 0.04 - sw - 0.03
box(bx, 0.070, bw, 0.112, '#fdecea', '#c0392b')
note(bx + bw / 2, 0.160, '✗ REJECTED', size=8.6, color='#7b241c', weight='bold')
note(bx + bw / 2, 0.113, '(c) fails quality gate\n→ excluded from evaluation', size=6.9)

plt.tight_layout()
plt.savefig('design/manuscript/chapter-12/figures/fig-12-1201.png', dpi=150)
plt.close()
print('wrote fig-12-1201.png')
