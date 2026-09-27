#!/usr/bin/env python3
"""fig-02-0201: Fig 2.2 — the arithmetic-intensity continuum split by the roofline ridge.

Reviewer: "TOO MUCH ANNOTATION relative to physical footprint; give roofline and two
regimes substantially more visual dominance."

Redesign: ONE log-log roofline plot fills the 6.1in column, and the two regimes carry
their own background.  Each regime is drawn as a large shading AND given its own
region label AND its own hatch texture, so the memory-bound / compute-bound split is
readable without relying on colour alone (label + texture + colour).  Text is held to
the reviewer's minimum: title, x/y axis labels, the ridge label, the two operating-point
labels, and the two region labels.  Every per-point numeric note from the earlier design
is dropped; those values live in the caption.  The roofline curve is the single heaviest
element (lw 2.8); the regimes sit beneath it; the markers / labels are lightest.

Derived numbers match the Ch2 canonical table and the Ch8 roofline:
  peak compute = 0.989 PFLOPS   (H100 BF16 dense tensor-core, no sparsity)
  peak HBM     = 3.353 TB/s     -> ridge = peak_compute / peak_bw ~= 295 FLOP/byte
  prefill @ ~9.2K FLOP/byte = compute-bound (right of ridge)
  decode  @ ~1  FLOP/byte   = memory-bound  (left of ridge)

Authored at the 6.1in column width (exempt from regen re-boost).
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mtick

matplotlib.rcParams['hatch.linewidth'] = 0.6

# ---- hardware model (matches Ch2 table + Ch8 roofline) ----
PEAK_FLOPS = 0.989e15      # FLOP/s  (0.989 PFLOPS)
PEAK_BW    = 3.353e12      # bytes/s (3.35 TB/s)
RIDGE      = PEAK_FLOPS / PEAK_BW            # ~295 FLOP/byte

XMIN, XMAX = 0.3, 30000.0
YMIN, YMAX = 1.0e11, 3.0e15

I = np.logspace(np.log10(XMIN), np.log10(XMAX), 400)
roofline = np.minimum(PEAK_BW * I, PEAK_FLOPS)   # attainable upper envelope

# regime fills + matching label/hatch channels (never colour alone)
C_MEM  = '#e2a366'   # memory-bound fill
C_CMP  = '#8fb0dd'   # compute-bound fill
C_MEML = '#7a4a12'   # memory-bound label
C_CMPL = '#173a6e'   # compute-bound label

fig, ax = plt.subplots(figsize=(6.1, 4.5))
fig._hermes_print_sized = True                  # regen must not re-boost/reflow
ax.set_xscale('log'); ax.set_yscale('log')
ax.set_xlim(XMIN, XMAX); ax.set_ylim(YMIN, YMAX)

# === dominant regime shading (background) with a distinct hatch per regime ===
mask_mem = I <= RIDGE
mask_cmp = I >= RIDGE
ax.fill_between(I[mask_mem], YMIN, roofline[mask_mem],
                facecolor=C_MEM, alpha=0.55, lw=0, hatch='///',
                edgecolor=C_MEML, zorder=1)          # memory-bound slope
ax.fill_between(I[mask_cmp], YMIN, roofline[mask_cmp],
                facecolor=C_CMP, alpha=0.55, lw=0, hatch='---',
                edgecolor=C_CMPL, zorder=1)          # compute-bound plateau

# === region labels (the redundant, non-colour channel) ===
ax.text(4.5, 1.05e12, 'memory-bound', color=C_MEML, fontsize=12.5,
        ha='center', va='center', fontweight='bold', alpha=0.9, zorder=2)
ax.text(2200.0, 1.6e13, 'compute-bound', color=C_CMPL, fontsize=12.5,
        ha='center', va='center', fontweight='bold', alpha=0.9, zorder=2)

# === ridge (boundary between the two regimes) ===
ax.axvline(RIDGE, color='#c0392b', ls='--', lw=1.7, zorder=3)
ax.text(RIDGE * 1.03, YMAX * 0.82, 'roofline ridge ~295', color='#c0392b',
        fontsize=8.5, ha='left', va='top', fontweight='bold', zorder=6)

# === roofline curve (heaviest element; upper envelope) ===
ax.plot(I, roofline, color='#1a1a1a', lw=2.8, zorder=4, solid_capstyle='round')

# === operating points: markers on the roofline, labels lifted into white space ===
ax.plot([1.0], [PEAK_BW * 1.0], marker='o', ms=11, color='#c0392b',
        mec='#7a1c10', zorder=5)
ax.annotate('decode', xy=(1.0, PEAK_BW), xytext=(0, 15), textcoords='offset points',
            ha='center', va='bottom', color='#8f2318', fontsize=11,
            fontweight='bold', zorder=6)

ax.plot([9200.0], [PEAK_FLOPS], marker='^', ms=12, color='#27408b',
        mec='#12294f', zorder=5)
ax.annotate('prefill', xy=(9200.0, PEAK_FLOPS), xytext=(0, 15),
            textcoords='offset points', ha='center', va='bottom',
            color='#12294f', fontsize=11, fontweight='bold', zorder=6)

# === axes + minimal text ===
ax.set_xlabel('arithmetic intensity (FLOP/byte)', fontsize=9.5, fontweight='bold')
ax.set_ylabel('attainable performance (FLOP/s)', fontsize=9.5, fontweight='bold')
ax.set_title('Prefill and decode: two regimes split by the roofline ridge',
             fontsize=11, fontweight='bold', pad=9)

ax.xaxis.set_major_locator(mtick.LogLocator(base=10.0))
ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda v, p: '%g' % round(v)))
ax.yaxis.set_major_locator(mtick.LogLocator(base=10.0))
ax.yaxis.set_major_formatter(mtick.LogFormatterSciNotation())
ax.xaxis.set_minor_formatter(mtick.NullFormatter())
ax.yaxis.set_minor_formatter(mtick.NullFormatter())
ax.tick_params(axis='both', which='major', labelsize=8.4)
ax.grid(True, which='major', axis='both', alpha=0.26, ls=':', lw=0.8, color='#888')

plt.tight_layout(pad=0.6)
plt.savefig('design/manuscript/chapter-02/figures/fig-02-0201.png', dpi=200)
plt.close()
print('wrote fig-02-0201')
