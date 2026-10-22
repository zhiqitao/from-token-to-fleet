import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ---- fig-25-2501: ADR anatomy + supersession (redesigned, v8 review) ----
# Two ADR cards (current + new), each with the 5 sections (name + a short
# content hint), and a red DASHED supersession arrow: the old ADR's
# Consequences become the new ADR's Context; the old ADR is kept
# (superseded, not edited).
fig, ax = plt.subplots(figsize=(6.1, 5.4))
fig._hermes_print_sized = True   # regen must not re-boost/reflow
ax.set_xlim(0, 26); ax.set_ylim(0, 22); ax.axis('off')
ax.set_title('Anatomy of an ADR, and how one ADR supersedes the next', fontsize=10.5,
             fontweight='bold', color='#1a1a1a', pad=10)

# short hints that fit inside the section boxes
stages = [
    ('Context',      'the situation'),
    ('Options',      'alternatives'),
    ('Decision',     'the choice'),
    ('Rationale',    'the "why"'),
    ('Consequences', 'the effects'),
]
n = len(stages)
w = 4.9; gap = 0.25
total = n*w + (n-1)*gap
x0 = (26 - total)/2.0

def adr_card(y_top, h, title, accent):
    ax.add_patch(FancyBboxPatch((x0-0.4, y_top-h), total+0.8, h,
                 boxstyle='round,pad=0.06,rounding_size=0.4',
                 fc='#fbfcfe', ec=accent, lw=1.6))
    ax.text(x0-0.4+(total+0.8)/2, y_top-0.7, title, ha='center', va='center',
            fontsize=9.5, fontweight='bold', color=accent)
    row_h = (h - 1.5) / n
    for i, (name, hint) in enumerate(stages):
        ry = y_top - 1.4 - (i+1)*row_h
        ax.add_patch(FancyBboxPatch((x0, ry+0.14), w, row_h-0.28,
                     boxstyle='round,pad=0.02,rounding_size=0.15',
                     fc='#dbe7f5', ec='#1a3a6b', lw=1.0))
        ax.text(x0+0.3, ry+row_h/2+0.30, name, ha='left', va='center',
                fontsize=8.6, fontweight='bold', color='#1a3a6b')
        ax.text(x0+0.3, ry+row_h/2-0.32, hint, ha='left', va='center',
                fontsize=7.2, color='#444', style='italic')
    return row_h

# OLD ADR (top): y 12.5 .. 20.9  (raised to widen the inter-panel gap)
old_h = 8.4; old_top = 20.9
row_h = adr_card(old_top, old_h, 'ADR-001  (current)', '#1a3a6b')
ax.text(x0+total+0.4-0.2, old_top-0.7, 'kept, not edited',
        fontsize=7.8, color='#888', ha='right', va='center', style='italic')

# NEW ADR (bottom): y 0.6 .. 9.0  (clear gap 9.0..12.5 holds the arrow + label)
new_h = 8.4; new_top = 9.0
adr_card(new_top, new_h, 'ADR-002  (new — supersedes ADR-001)', '#7b241c')

# supersession arrow: kept entirely inside the inter-panel gap, running from the
# top card's bottom border down to the bottom card's top border (short connector,
# inset a little so it never lies on top of either border). The arrowhead points
# down into the new card.
old_bottom = old_top - old_h           # top card bottom border (y)
ax.add_patch(FancyArrowPatch((x0+w, old_bottom-0.2), (x0+w, new_top+0.2),
             connectionstyle='arc3,rad=-0.25', arrowstyle='-|>', mutation_scale=22,
             lw=2.4, color='#c0392b', ls='dashed'))
# label in the gap, centred vertically between the two borders and placed to the
# right of the arrow, so neither collides with the other or with the panel borders.
gap_mid = (old_bottom + new_top) / 2
ax.text(x0+w+2.45, gap_mid,
        'consequences of ADR-001\nbecome the context of ADR-002',
        fontsize=8.0, color='#c0392b', ha='left', va='center', fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.25', fc='white', ec='none', alpha=0.92))

plt.tight_layout()
plt.savefig('design/manuscript/chapter-25/figures/fig-25-2501.png',
            dpi=200, bbox_inches='tight', pad_inches=0.08)
plt.close()
print('wrote fig-25-2501 (ADR anatomy + supersession, full-height)')
