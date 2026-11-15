import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['pdf.fonttype']=42
matplotlib.rcParams['ps.fonttype']=42
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ---- fig-25-2501: ADR anatomy + supersession (redesigned, v8 review) ----
# Two ADR cards (current + new), each with the 5 sections (name + a short
# content hint), and a red DASHED supersession arrow: the old ADR's
# Consequences become the new ADR's Context; the old ADR is kept
# (superseded, not edited).
fig, ax = plt.subplots(figsize=(6.1, 5.4))
fig._hermes_print_sized = True   # regen must not re-boost/reflow
ax.set_xlim(-2.0, 29.4); ax.set_ylim(0, 22); ax.axis('off')
# FIG-25.1-02: no in-figure title — the caption carries it.

# short hints that fit inside the section boxes — the five CORE ADR fields in
# §25.1 order (C-20: the figure must match the copy-ready template's core fields,
# not the old Context/Options/Decision/Rationale/Consequences set).
stages = [
    ('Title & status', 'the record'),
    ('Context',        'the situation'),
    ('Decision',       'the choice'),
    ('Consequences',   'the effects'),
    ('Alternatives',   'rejected options'),
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
        # FIG-25.1-04: each field box spans the full card width (was left ~1/5,
        # leaving two-thirds of every card blank), name left / gloss right on one line.
        ax.add_patch(FancyBboxPatch((x0, ry+0.14), total, row_h-0.28,
                     boxstyle='round,pad=0.02,rounding_size=0.15',
                     fc='#dbe7f5', ec='#1a3a6b', lw=1.0))
        ax.text(x0+0.35, ry+row_h/2, name, ha='left', va='center',
                fontsize=8.6, fontweight='bold', color='#1a3a6b')
        ax.text(x0+total-0.35, ry+row_h/2, hint, ha='right', va='center',
                fontsize=8.5, color='#444', style='italic')  # Loop-3: was 7.2pt; R5: gloss >= 8.5pt
    return row_h

# OLD ADR (top): y 12.5 .. 20.9  (raised to widen the inter-panel gap)
old_h = 8.4; old_top = 20.9
row_h = adr_card(old_top, old_h, 'ADR-001  (superseded)', '#1a3a6b')
ax.text(x0+total+0.4-0.2, old_top-0.7, 'kept, not edited',
        fontsize=8.0, color='#888', ha='right', va='center', style='italic')  # Loop-3: was 7.8pt, below the 8pt on-page floor

# NEW ADR (bottom): y 0.6 .. 9.0  (clear gap 9.0..12.5 holds the arrow + label)
new_h = 8.4; new_top = 9.0
adr_card(new_top, new_h, 'ADR-002  (new — supersedes ADR-001)', '#7b241c')

# supersession arrow: kept entirely inside the inter-panel gap, running from the
# top card's bottom border down to the bottom card's top border. R27 P2: the tip
# must actually TOUCH the ADR-002 top rule (the card's top edge sits at
# new_top+0.06 because of the boxstyle pad).  The old tip (new_top-0.08) and the
# oversized head (mutation_scale=22) left a visible white sliver above the border;
# the tip now lands just inside the border with a smaller head.
old_bottom = old_top - old_h           # top card bottom border (y)
# FIG-25.1-01 / FIG-415-01: the arrow is anchored to the named FIELDS, not to the
# outer card edges — it leaves the ADR-001 'Consequences' box and terminates on the
# ADR-002 'Context' box, so the endpoints visibly attach to those two fields.
row_h_old = (old_h - 1.5) / n
cons_ry = old_top - 1.4 - (3+1)*row_h_old          # Consequences (i=3) row base
cons_bottom = cons_ry + 0.14                        # inside edge of that field box
row_h_new = (new_h - 1.5) / n
ctx_ry = new_top - 1.4 - (1+1)*row_h_new            # Context (i=1) row base
ctx_top = ctx_ry + 0.14 + (row_h_new - 0.28)        # inside edge of that field box
cons_cy = cons_ry + row_h_old/2                       # Consequences field centre (ADR-001)
ctx_cy  = ctx_ry + row_h_new/2                        # Context field centre (ADR-002)
box_right = x0 + total                                # right edge of the field boxes
route_x = box_right + 1.45                            # vertical run just outside the cards
# FIG-25.1-01 / FIG-415-01: the connector is anchored to the named FIELDS — it
# leaves the ADR-001 'Consequences' box, runs along the right gutter, and its
# arrowhead lands on the ADR-002 'Context' box.
ax.plot([box_right, route_x, route_x], [cons_cy, cons_cy, ctx_cy],
        color='#c0392b', lw=2.4, ls=(0, (4, 3)), solid_capstyle='butt', zorder=1)
ax.add_patch(FancyArrowPatch((route_x, ctx_cy), (box_right+0.06, ctx_cy),
             connectionstyle='arc3,rad=0.0', arrowstyle='-|>', mutation_scale=9,
             lw=2.4, color='#c0392b', linestyle=(0, (4, 3))))
# label in the inter-card gap, clear of both cards and the route; modality
# matches the caption's 'may become part of the Context'.
gap_mid = (old_bottom + new_top) / 2
ax.text(box_right-0.6, gap_mid,
        'consequences of ADR-001\nmay become the context of ADR-002',
        fontsize=8.5, color='#c0392b', ha='right', va='center', fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.25', fc='white', ec='none', alpha=0.92))

plt.tight_layout()
plt.savefig('design/manuscript/chapter-25/figures/fig-25-2501.png',
            dpi=400, bbox_inches='tight', pad_inches=0.08)
plt.savefig('design/manuscript/chapter-25/figures/fig-25-2501.pdf',
            format='pdf', bbox_inches='tight', pad_inches=0.08)
plt.close()
print('wrote fig-25-2501 (ADR anatomy + supersession, full-height)')
