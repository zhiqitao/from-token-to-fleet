import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Patch

# ---- fig-19-1903: Agentic Context Accumulation (full-width redraw) ----
# Canonical (Ch 19): I0=9200, delta=800 retrieved, gamma=65 generated per turn.
# KV @ 2.62 MB/token: 24.9..34.0 GB.
# Redesign (v8 review): the 5 columns now span the full figure width (no large
# blank margins), each component uses a DISTINCT fill+pattern (so O_final and
# delta no longer merge), and the in-bar labels are larger and high-contrast.
I0, d, g = 9200, 800, 65
cols = [
    ('Single-shot', 0,   0,   24.9),
    ('Turn 1',     d,   g,   27.2),
    ('Turn 2',     2*d, 2*g, 29.4),
    ('Turn 3',     3*d, 3*g, 31.7),
    ('Turn 4',     4*d, 4*g, 34.0),
]
# full-width layout: 5 columns across the whole axis
n = len(cols)
margin = 0.35
gap = 0.55
cwd = (12.8 - 2*margin - (n-1)*gap) / n   # ~2.24 -> wider columns
xs = [margin + i*(cwd+gap) for i in range(n)]
def h_of(tok): return tok * 0.00035

fig, ax = plt.subplots(figsize=(6.1, 5.63))
fig._hermes_print_sized = True   # regen must not re-boost/reflow
# ylim toped just above the column-name row so the legend sits close to the
# bars (the old top was 12.2, leaving ~1/3 of the axes empty below the legend).
ax.set_xlim(0, 12.8); ax.set_ylim(-0.6, 10.6); ax.axis('off')

# distinct component styles: (fill, edge, hatch)
ST = {
    'I0':   ('#c8d8ea', '#27408b', '//'),   # blue diagonal
    'Ofin': ('#6f9e5f', '#1e7a59', ''),     # solid green (no hatch)
    'delta':('#7fc6b5', '#1a7a63', '...'),  # teal dots
    'gamma':('#f5c98b', '#e67e22', 'xx'),   # orange cross
}

def band(x, y, h, key, label, lfs, lcolor):
    fc, ec, hatch = ST[key]
    ax.add_patch(FancyBboxPatch((x, y), cwd, h, boxstyle='round,pad=0.01',
                                fc=fc, ec=ec, lw=1.2, hatch=hatch))
    if label:
        ax.text(x+cwd/2, y+h/2, label, fontsize=lfs, ha='center', va='center',
                color=lcolor, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.12', fc='white', ec='none', alpha=0.75))

for i, (name, dl, gm, kv) in enumerate(cols):
    x = xs[i]
    ax.text(x+cwd/2, 8.3, name, fontsize=8.5, fontweight='bold', ha='center', color='#27408b')
    y = 2.4
    # initial prompt I0 (blue, constant)
    h0 = h_of(I0)
    band(x, y, h0, 'I0', 'I\u2080 (in)', 9.5, '#27408b')
    y += h0
    # final output O_final (solid green, constant 300 tokens) — drawn to scale
    # (no minimum clamp) so the bar heights grow linearly with the cumulative
    # context; the label lives in the legend (the band is too thin to hold it).
    hf = h_of(300)
    band(x, y, hf, 'Ofin', None, 8.5, '#0d4a35')
    y += hf
    # retrieved tool output (teal dots, grows with turns) — to scale
    if dl > 0:
        h1 = h_of(dl)
        band(x, y, h1, 'delta', '\u03b4', 10.5, '#0a4a3a')
        y += h1
    # generated reasoning (orange cross, grows with turns) — to scale; label in
    # the legend (the band is too thin to hold it at the small end).
    if gm > 0:
        h2 = h_of(gm)
        band(x, y, h2, 'gamma', None, 10.0, '#8a4b08')
        y += h2
    ax.text(x+cwd/2, y+0.5, f'KV {kv:.1f}', fontsize=8.5, ha='center',
            fontweight='bold', color='#c0392b')

# conclusion lines
ax.text(6.4, 1.60, 'Illustrative append-only context; compaction/reconstruction can interrupt growth',
        fontsize=9, ha='center', color='#1a1a1a', fontweight='bold')
ax.text(6.4, 1.10, 'agentic depth is a fleet-sizing problem: KV grows ~36% (24.9 \u2192 34.0 GB)',
        fontsize=9, ha='center', color='#c0392b', fontweight='bold')
ax.text(6.4, 0.58, 'canonical example @ 2.62 MB/token; total = I\u2080 + T\u00b7\u03b4 + T\u00b7\u03b3 + O_final',
        fontsize=8.5, ha='center', color='#444')
ax.text(6.4, 0.22, '(I\u2080 = 9.2K input, O_final = 300 output).',
        fontsize=8.5, ha='center', color='#444')

# legend (distinct swatches)
legend_comps = [
    ('initial prompt I\u2080 (9.2K in)', '#c8d8ea', '//'),
    ('final output O_final (300)', '#6f9e5f', ''),
    ('retrieved tool output (\u03b4)', '#7fc6b5', '...'),
    ('generated reasoning (\u03b3)', '#f5c98b', 'xx'),
]
ax.legend(handles=[Patch(fc=c, ec='#333', hatch=h, label=l) for l, c, h in legend_comps],
          loc='upper center', bbox_to_anchor=(0.5, 0.985), fontsize=8.4, frameon=False, ncol=2,
          bbox_transform=ax.transAxes, handlelength=1.4, columnspacing=1.2)

plt.tight_layout()
plt.savefig('design/manuscript/chapter-19/figures/fig-19-1903.png',
            dpi=400, bbox_inches='tight', pad_inches=0.08)
plt.close()
print('fig-19-1903 full-width redraw (distinct patterns, larger labels)')
