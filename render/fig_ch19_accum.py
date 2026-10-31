import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Patch, Rectangle

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

fig, ax = plt.subplots(figsize=(6.1, 6.4))
fig._hermes_print_sized = True   # regen must not re-boost/reflow
fig._hermes_print_crop_bottom_in = 0.35  # trim 25.2pt of verified blank export padding
# ylim toped just above the column-name row so the legend sits close to the
# bars (the old top was 12.2, leaving ~1/3 of the axes empty below the legend).
ax.set_xlim(0, 12.8); ax.set_ylim(-0.6, 10.6)
# R27 P2: the figure had no y-axis, no ticks, no units — the bars are drawn to
# scale via h_of(tok)=tok*0.00035 but the reader could only read the text labels.
# Show a left y-axis in tokens (the bar base sits at data y=2.4 = 0 tokens) while
# keeping the x-axis off (categorical columns) and the spines hidden (text-art
# look).  axis('off') would set axison=False and block the y-axis, so hide the
# pieces individually instead.
ax.xaxis.set_visible(False)
ax.yaxis.set_visible(True)
for _sp in ax.spines.values():
    _sp.set_visible(False)
ax.set_yticks([2.4 + t*0.00035 for t in (0, 4000, 8000, 12000)])
ax.set_yticklabels(['0', '4K', '8K', '12K'])
ax.set_ylabel('Tokens / request', fontsize=9)

# distinct component styles: (fill, edge, hatch)
ST = {
    'I0':   ('#c8d8ea', '#27408b', '//'),   # blue diagonal
    'Ofin': ('#6f9e5f', '#1e7a59', ''),     # solid green (no hatch)
    'delta':('#7fc6b5', '#1a7a63', '...'),  # teal dots
    'gamma':('#f5c98b', '#e67e22', 'xx'),   # orange cross
}

_badges = []   # (text_artist, band_height_data) for the post-layout fit check

def band(x, y, h, key, label, lfs, lcolor):
    fc, ec, hatch = ST[key]
    ax.add_patch(FancyBboxPatch((x, y), cwd, h, boxstyle='round,pad=0.01',
                                fc=fc, ec=ec, lw=1.2, hatch=hatch))
    if label:
        _badges.append((ax.text(x+cwd/2, y+h/2, label, fontsize=lfs,
                                ha='center', va='center',
                                color=lcolor, fontweight='bold',
                                bbox=dict(boxstyle='round,pad=0.12', fc='white',
                                          ec='none', alpha=0.75)), h))

for i, (name, dl, gm, kv) in enumerate(cols):
    x = xs[i]
    ax.text(x+cwd/2, 8.3, name, fontsize=8.5, fontweight='bold', ha='center', color='#27408b')
    y = 2.4
    # initial prompt I0 (blue, constant)
    h0 = h_of(I0)
    band(x, y, h0, 'I0', 'I\u2080 (in)', 9.5, '#27408b')
    y += h0

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
    # Match the companion chart: initial context, retrieval, reasoning, output.
    # Keep every component to scale; the fixed output is too thin for a label.
    hf = h_of(300)
    band(x, y, hf, 'Ofin', None, 8.5, '#0d4a35')
    y += hf
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

# ---- counterfactual column semantics (R08/R11): each column is a SEPARATE
# completion after T turns (incl. one final 300-token answer), not successive
# internal states of one live agent that already answered at turn 1.
ax.text(6.4, 9.30, 'counterfactual: each column = a separate completion after T turns,',
        fontsize=8.5, ha='center', color='#111')
ax.text(6.4, 8.95, 'including one final 300-token answer \u2014 not successive states of one live agent.',
        fontsize=8.5, ha='center', color='#111')

# ---- magnified inset (R08-c): blow up the thin per-turn slice so the gamma
# band and the exact counts (delta=800, gamma=65, O=300) are readable.
# Sized from measured PDF geometry: right edge data 5.55 clears KV 29.4 (x0
# 201pt), bottom data 6.80 clears KV 27.2 (top 162.6pt), top data 7.95 clears
# the column names (~111pt).  Single-line title so 4 lines fit the gap.
bx, by, bw, bh = 0.0, 6.80, 5.55, 1.15
ax.add_patch(FancyBboxPatch((bx, by), bw, bh, boxstyle='round,pad=0.02',
                            fc='#ffffff', ec='#555', lw=1.1, alpha=0.97, zorder=5))
ax.text(bx+bw/2, by+bh-0.16, 'magnified per-turn slice:',
        fontsize=8.5, ha='center', va='center', fontweight='bold', color='#333', zorder=6)
_rows = [  # (fill, edge, hatch, label) bottom-to-top matches the real stack
    ('#7fc6b5', '#1a7a63', '...', '\u03b4 = 800 retrieved'),
    ('#f5c98b', '#e67e22', 'xx',   '\u03b3 = 65 model reasoning'),
    ('#6f9e5f', '#1e7a59', '',     'O = 300 final answer'),
]
for _i, (_fc, _ec, _h, _lab) in enumerate(_rows):
    _ry = by + 0.18 + _i*0.27
    ax.add_patch(Rectangle((bx+0.16, _ry-0.10), 0.50, 0.20,
                               fc=_fc, ec=_ec, lw=1.0, hatch=_h, zorder=6))
    ax.text(bx+0.82, _ry, _lab, fontsize=8.5, ha='left', va='center',
            color='#222', zorder=6)

# legend (distinct swatches)
legend_comps = [
    ('initial prompt I\u2080 (9.2K in)', '#c8d8ea', '//'),
    (r'final output O_final (300)', '#6f9e5f', ''),
    ('retrieved tool output (\u03b4)', '#7fc6b5', '...'),
    ('generated reasoning (\u03b3)', '#f5c98b', 'xx'),
]
ax.legend(handles=[Patch(fc=c, ec='#333', hatch=h, label=l) for l, c, h in legend_comps],
          loc='upper center', bbox_to_anchor=(0.5, 0.985), fontsize=8.4, frameon=False, ncol=2,
          bbox_transform=ax.transAxes, handlelength=1.4, columnspacing=1.2)

plt.tight_layout()

# R23 / R20-C19-09 geometric fix: a haloed label badge must fit INSIDE its own
# band.  Measured on the built vector PDF, the Turn 1 delta band is 10.28pt
# tall while the haloed 10.5pt badge is 13.10pt, so the white badge overhung
# 1.41pt up into the gamma band and 1.41pt down into the I0 band.  After the
# final layout, drop the halo on any badge taller than its band: the glyph ink
# still fits with clearance, and label text, label size and all data values
# stay exactly unchanged.  Badges that fit (I0, delta Turns 2-4) keep the halo.
_pt_per_data = abs(ax.transData.transform((0, 1))[1] -
                   ax.transData.transform((0, 0))[1]) * 72.0 / fig.dpi
for _txt, _h_data in _badges:
    # 1.25 = measured haloed-badge height / fontsize (13.10pt / 10.5pt, DejaVu).
    if _txt.get_fontsize() * 1.25 > _h_data * _pt_per_data:
        _txt.set_bbox(None)
        # va='center' anchors the em box, whose INK centre sits 0.1181*fontsize
        # pt above the anchor (measured: 1.24pt at 10.5pt DejaVu Sans, 720dpi
        # raster of the built PDF), leaving the glyph apex 0.20pt past the band's
        # top border.  Nudge down by that offset so the ink is centred in the
        # band (1.04pt clearance top and bottom).  Text, size and data unchanged.
        _x, _y = _txt.get_position()
        _txt.set_position((_x, _y - (0.1181 * _txt.get_fontsize()) / _pt_per_data))

plt.savefig('design/manuscript/chapter-19/figures/fig-19-1903.png',
            dpi=400, bbox_inches='tight', pad_inches=0.08)
plt.close()
print('fig-19-1903 full-width redraw (distinct patterns, larger labels)')
