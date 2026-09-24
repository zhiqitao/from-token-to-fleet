import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Patch

# ---- fig-19-1903: Agentic Context Accumulation sequence ----
# Canonical (Ch 19): I0=9200, delta=800 retrieved, gamma=65 generated per turn.
# KV @ 2.62 MB/token: 24.9..34.0 GB.
I0, d, g = 9200, 800, 65
# clear-named column data: label, delta, gamma, kv_gb
cols = [
    ('Single-shot', 0,   0,   24.9),
    ('Turn 1',     d,   g,   27.2),
    ('Turn 2',     2*d, 2*g, 29.4),
    ('Turn 3',     3*d, 3*g, 31.7),
    ('Turn 4',     4*d, 4*g, 34.0),
]
xs = [0.4, 3.0, 5.6, 8.2, 10.8]
cwd = 2.4
def h_of(tok): return tok * 0.00035

fig, ax = plt.subplots(figsize=(6.1, 5.63))
fig._hermes_print_sized = True   # regen must not re-boost/reflow
ax.set_xlim(0, 14.2); ax.set_ylim(0, 12.2); ax.axis('off')
ax.text(7.1, 11.7, 'Agentic context accumulation: the KV block grows every turn',
        fontsize=10.5, fontweight='bold', ha='center', color='#1a1a1a')

for (name, dl, gm, kv), x in zip(cols, xs):
    ax.text(x+cwd/2, 8.3, name, fontsize=10, fontweight='bold', ha='center', color='#27408b')
    y = 2.4
    # initial prompt I0 (blue, constant) = 9.2K input
    h0 = h_of(I0)
    ax.add_patch(FancyBboxPatch((x, y), cwd, h0, boxstyle='round,pad=0.01',
                                fc='#c8d8ea', ec='#27408b', lw=1, hatch='//'))
    ax.text(x+cwd/2, y+h0/2, 'I\u2080 (in)', fontsize=9, ha='center', va='center', color='#27408b')
    y += h0
    # final output O_final (constant 300 tokens, separate block, matches Fig 19.2)
    hf = max(h_of(300), 0.30)
    ax.add_patch(FancyBboxPatch((x, y), cwd, hf, boxstyle='round,pad=0.01',
                                fc='#6f9e5f', ec='#1e7a59', lw=1, hatch='xx'))
    ax.text(x+cwd/2, y+hf/2, 'O\u2091', fontsize=8.5, ha='center', va='center', color='#0d4a35')
    y += hf
    # retrieved tool output (teal, grows with turns)
    if dl > 0:
        h1 = h_of(dl)
        ax.add_patch(FancyBboxPatch((x, y), cwd, h1, boxstyle='round,pad=0.01',
                                    fc='#7fc6b5', ec='#1a7a63', lw=1, hatch='xx'))
        ax.text(x+cwd/2, y+h1/2, '\u03b4', fontsize=9, ha='center', va='center', color='#0a4a3a')
        y += h1
    # generated reasoning (orange, grows with turns) — distinct hatch + min visible height
    if gm > 0:
        h2 = max(h_of(gm), 0.35)
        ax.add_patch(FancyBboxPatch((x, y), cwd, h2, boxstyle='round,pad=0.01',
                                    fc='#f5c98b', ec='#e67e22', lw=1.2, hatch='OO'))
        ax.text(x+cwd/2, y+h2/2, '\u03b3', fontsize=8.5, ha='center', va='center', color='#8a4b08',
                fontweight='bold')
        y += h2
    ax.text(x+cwd/2, y+0.5, f'KV {kv:.1f} GB', fontsize=9.5, ha='center',
            fontweight='bold', color='#c0392b')

# conclusion line in its own band above the legend
ax.text(7.1, 1.60, 'append-only illustrative model: context is only appended, never evicted',
        fontsize=9, ha='center', color='#1a1a1a', fontweight='bold')
ax.text(7.1, 1.10, 'agentic depth is a fleet-sizing problem: KV grows ~36% (24.9 \u2192 34.0 GB)',
        fontsize=9, ha='center', color='#c0392b', fontweight='bold')
ax.text(7.1, 0.55, 'canonical example @ 2.62 MB/token; total = I\u2080 + T\u00b7\u03b4 + T\u00b7\u03b3 + O_final (I\u2080 = 9.2K input, O_final = 300 output).',
        fontsize=8.5, ha='center', color='#444')

# legend in its OWN clean band at the very bottom (clear of the conclusion/note text)
legend_comps = [
    ('initial prompt I\u2080 (9.2K in)', '#c8d8ea', '//'),
    ('final output O\u2091 (300)', '#6f9e5f', 'xx'),
    ('retrieved tool output (\u03b4)', '#7fc6b5', 'xx'),
    ('generated reasoning (\u03b3)', '#f5c98b', 'OO'),
]
ax.legend(handles=[Patch(fc=c, ec='#333', hatch=h, label=l) for l, c, h in legend_comps],
          loc='lower center', bbox_to_anchor=(0.5, 0.00), fontsize=8.8, frameon=False, ncol=4,
          bbox_transform=ax.transAxes, handlelength=1.4, columnspacing=1.4)

plt.tight_layout()
plt.savefig('design/manuscript/chapter-19/figures/fig-19-1903.png',
            dpi=200, bbox_inches='tight', pad_inches=0.08)
plt.close()
print('fig-19-1903 fixed (clear field indices)')
