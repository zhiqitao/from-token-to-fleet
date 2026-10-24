import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ---- fig-26-2602: Workload fingerprints (grouped bars, NOT radar) ----
# A radar chart's enclosed-area reading is invalid (axis-order + normalisation
# dependent).  A grouped BAR chart encodes each workload's normalised profile on
# six comparably-scaled axes by height + hatch (grayscale-safe), so the axes are
# independent and directly comparable.
dims = ['Context\nlength', 'Traffic\n(rps)', 'Quality\nrequired', 'Cost\nsensitive',
        'Latency\nsensitive', 'Output\ntokens']
# normalised 0-1 profiles (illustrative, per the chapter's workload taxonomy)
longctx = [0.95, 0.20, 0.70, 0.55, 0.40, 0.45]
chat    = [0.35, 0.95, 0.50, 0.75, 0.90, 0.55]
batch   = [0.55, 0.60, 0.30, 0.85, 0.35, 0.90]

x = np.arange(len(dims)); wdt = 0.25
fig, ax = plt.subplots(figsize=(6.1, 4.13))
fig._hermes_print_sized = True   # regen must not re-boost/reflow
b1 = ax.bar(x-wdt, longctx, wdt, label='Long-context RAG Q&A', color='#3a6ea5', hatch='/')
b2 = ax.bar(x,     chat,    wdt, label='High-throughput chat', color='#e67e22', hatch='x')
b3 = ax.bar(x+wdt, batch,   wdt, label='Batch inference',      color='#6f9e5f', hatch='.')

ax.set_xticks(x)
ax.set_xticklabels(dims, fontsize=9.2, rotation=0, ha='center')
ax.tick_params(axis='x', length=0, pad=6)
ax.set_ylabel('Normalised intensity (0-1)', fontsize=9)
# raise the top so the legend has its own clear band INSIDE the plot (above the
# tallest bar, 0.95) — the earlier bbox_to_anchor=(0.5,1.01) put it OUTSIDE the
# axes, on the same line as the title, so the two collided.
ax.set_ylim(0, 1.45)
# title: the internal "confirm against real telemetry" note is dropped from the
# published title (it belongs in the caption, not the figure heading)
ax.set_title('Workload fingerprints on six axes (grouped bars, not radar)', fontsize=10)
# legend in its own band at the TOP INSIDE the plot (clear of the title above and
# the bars below)
ax.legend(fontsize=8.2, loc='upper center', ncol=3, frameon=False,
          bbox_to_anchor=(0.5, 0.99), columnspacing=1.2, handlelength=1.4)
ax.grid(axis='y', alpha=0.3)
ax.text(0.98, -0.13, 'per-axis 0-1 scale; compare within an axis, not across axes.', transform=ax.transAxes,
        fontsize=8.0, color='#555', va='top', ha='right')
plt.tight_layout()
plt.savefig('design/manuscript/chapter-26/figures/fig-26-2602.png', dpi=350)
import matplotlib as mpl
with mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-26/figures/fig-26-2602.pdf', format='pdf')
plt.close()
print('wrote fig-26-2602 (grouped bars, horizontal labels)')
