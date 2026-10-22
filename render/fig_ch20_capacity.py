import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ---- fig-20-2001: Fleet capacity (rebuilt from the hand-authored vector PDF) ----
# Two stacked panels, 6.1in wide (print column).
#   TOP    = ANALYTICAL CAPACITY BOUND: ~2.0 req/s/host, no overhead (thin grey dashed).
#   BOTTOM = MODELED OFFERED-LOAD-SERVED CURVE: the ~2.0 req/s/host bound reduced by
#            ~95% scheduling efficiency and flattened at the canonical 40 rps peak
#            once ~20 hosts are provisioned (thick blue solid). This is a modeled
#            (derived) construction (analytical bound x 0.95) representing offered
#            load that is served, NOT a measured deployment throughput.
# The gap between the two is the scheduling + tail/queueing overhead.
# Annotations are placed in CLEAR regions (not on the curves) with leader arrows.

hosts = np.arange(0, 61)
analytical = 2.0 * hosts
measured = np.minimum(0.95 * 2.0 * hosts, 40.0)   # ~95% efficiency, capped at 40 rps

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6.1, 5.4), sharex=True)
fig._hermes_print_sized = True   # print-size authored: regen must not re-boost/reflow

# ---- TOP: analytical capacity bound ----
ax1.plot(hosts, analytical, '-', color='#888', lw=1.6, label='analytical bound (ceiling)')
ax1.axhline(40, color='#27408b', ls='--', lw=1.0, alpha=0.7)
# annotation in the LOWER-RIGHT clear corner (the grey line is at y=2x, so at
# x<10 it is near the bottom; the lower-right below the 40 line is empty) — the
# earlier top-right placement sat on the rising grey line
ax1.text(58, 4, 'canonical peak load = 40 rps', ha='right', va='bottom',
         fontsize=8.0, color='#27408b')
ax1.set_ylabel('Fleet capacity (req/s)', fontsize=9)
ax1.set_title('ANALYTICAL CAPACITY BOUND  (no overhead)', fontsize=9.5,
              fontweight='bold', color='#555', loc='left')
ax1.set_ylim(0, 125)
ax1.grid(alpha=0.3)
ax1.legend(fontsize=8.0, loc='upper left', frameon=False)
ax1.tick_params(labelsize=8)

# ---- BOTTOM: modeled offered-load-served curve ----
ax2.plot(hosts, measured, '-', color='#27408b', lw=2.8, label='modeled offered-load-served curve (95% efficiency)')
ax2.plot(hosts, analytical, ':', color='#888', lw=1.2, label='analytical bound (ceiling)')
# annotation 1: removed — the "~5 hosts -> ~9.5 req/s" data point is redundant
# (the linear rise makes it obvious) and could not be placed without crossing the
# rising blue curve. The upper annotation (annotation 2) carries the key point.
# annotation 2: ~20 hosts -> reaches the 40 rps peak. Placed in the UPPER-LEFT clear
# region (below the legend, above the rising curves: the grey line is y=2x, so at
# x<15 it is at y<30, well below this text; the legend sits at y>100, well above).
# The earlier (45,78) placement sat where the grey line (y=2x) crosses the text band.
ax2.annotate('\u224820 hosts \u2192 reaches the 40 rps peak;\nmodeled curve plateaus (95% efficiency)',
             xy=(20, 40), xytext=(2.5, 62),
             fontsize=8.2, color='#1a1a1a', ha='left', va='center',
             arrowprops=dict(arrowstyle='->', color='#555', lw=0.9))
ax2.set_ylabel('Fleet throughput (req/s)', fontsize=9)
ax2.set_title('MODELED OFFERED-LOAD-SERVED CURVE  (95% scheduling efficiency)', fontsize=9.5,
              fontweight='bold', color='#1a1a1a', loc='left')
ax2.set_ylim(0, 125)
ax2.grid(alpha=0.3)
ax2.legend(fontsize=8.0, loc='upper left', frameon=False)
ax2.tick_params(labelsize=8)

ax2.set_xlabel('Host count', fontsize=9)
fig.text(0.5, 0.005, '[ILLUSTRATIVE][DERIVED]', ha='center', fontsize=9, color='#444')

plt.tight_layout(rect=(0, 0.02, 1, 1))
import matplotlib as _mpl
with _mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-20/figures/fig-20-2001.pdf', format='pdf',
                bbox_inches='tight', pad_inches=0.05)
# also emit a PNG (the build copies the .png when no sibling .pdf exists; keep both
# in sync so a stale PNG can never shadow the new vector)
plt.savefig('design/manuscript/chapter-20/figures/fig-20-2001.png', dpi=200,
            bbox_inches='tight', pad_inches=0.05)
plt.close()
print('wrote fig-20-2001 (rebuilt; annotations moved off the curves)')
