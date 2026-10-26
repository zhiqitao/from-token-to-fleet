import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties

# ---- fig-18-1801: Sequential model-routing decision tree (WIDE horizontal) ----
# Policy: Request -> capability filter -> (yes: specialist)/(no) -> cost+SLO gate
# -> (yes: general)/(no) -> fallthrough general model.
#
# Author at EXACTLY the 6.1in column width so regen_figs does NOT boost the fonts
# (a wider authoring size would clamp down and re-boost text into fixed boxes,
# clipping it).  Boxes are sized to their measured label width with generous
# padding, so a label always fits.  1 data unit == 1 point.
BOLD = FontProperties(weight='bold')
W = 6.1 * 72        # 439.2 pt == column width
Ht = 4.3 * 72
FS = 9.0            # ~on-page size (no boost at column width)
PADX = 0.45         # extra box width (%) beyond label
SEG = 1.2           # gap between horizontal boxes (%) of label width

def tw(s):
    return TextPath((0, 0), s, size=FS, prop=BOLD).get_extents().width

def lh(s):
    # half-width of a branch label text (labels are drawn at FS-0.2)
    return TextPath((0, 0), s, size=FS-0.2, prop=BOLD).get_extents().width / 2

def box(xc, yc, text, fc, ec, tc='white'):
    lines = text.split('\n')
    w = max(tw(ln) for ln in lines) * (1 + PADX)
    n = len(lines)
    h = n * FS * 1.5 * (1 + 0.6)
    ax.add_patch(FancyBboxPatch((xc-w/2, yc-h/2), w, h,
                  boxstyle='round,pad=0.05,rounding_size=1.0', fc=fc, ec=ec, lw=1.4, clip_on=False))
    ax.text(xc, yc, text, ha='center', va='center', fontsize=FS, color=tc, fontweight='bold')
    return xc-w/2, xc+w/2

def arrow(x1,y1,x2,y2,color='#555'):
    ax.annotate('', xy=(x2,y2), xytext=(x1,y1),
                arrowprops=dict(arrowstyle='-|>', lw=1.8, color=color, shrinkA=0, shrinkB=0))

fig, ax = plt.subplots(figsize=(6.1, 4.3))
fig._hermes_print_sized = True   # regen must not re-boost/reflow
ax.set_xlim(0, W); ax.set_ylim(0, Ht); ax.axis('off')
ax.set_title('Routing every request to the right specialised model (sequential cascade)',
             fontsize=FS+1.2, fontweight='bold', ha='center', color='#1a1a1a', pad=12)

SP = 190
RES = 70
GAP = 5.0          # pt gap between top boxes

def hflow(defs, y, xstart, gap):
    xc = xstart; edges = []
    for lab, fc, ec in defs:
        w = max(tw(l) for l in lab.split('\n')) * (1+PADX)
        xc = xc + w/2
        l, rr = box(xc, y, lab, fc, ec)
        edges.append((l, rr))
        xc = rr + gap
    return edges

# ---- top spine (left -> right), centred ----
spine_defs = [
    ('Request', '#27408b', '#1a3a6b'),
    ('Capability filter', '#e67e22', '#b35900'),
    ('Cost/SLO gate', '#e67e22', '#b35900'),
    ('Fallthrough', '#e67e22', '#b35900'),
]
spine_w = sum(max(tw(l) for l in d[0].split('\n'))*(1+PADX) for d in spine_defs) + GAP*(len(spine_defs)-1)
spine = hflow(spine_defs, SP, (W - spine_w)/2, GAP)

# ---- specialist leaf group ----
spec_defs = [
    ('Embedding', '#3a6ea5', '#1a3a6b'),
    ('Vision', '#8055b5', '#5a3a8a'),
    ('Math/reason', '#c0392b', '#8a2a20'),
]
# ---- general leaf group ----
gen_defs = [
    ('Frontier', '#1f7a8c', '#14525f'),
    ('Small gen', '#2e9e63', '#1f7245'),
    ('General', '#2e9e63', '#1f7245'),
]
spec_w = sum(tw(l)*(1+PADX) for l,_,_ in spec_defs) + GAP*(len(spec_defs)-1) + 6
gen_w  = sum(tw(l)*(1+PADX) for l,_,_ in gen_defs)  + GAP*(len(gen_defs)-1) + 6
# two groups side by side with a separator that leaves margin inside the column
groupgap = 40
total = spec_w + groupgap + gen_w
# core: if total exceeds the column, shrink the inter-box gap so everything fits inside W.
# (leave no box or arrow off the right/left edge.)
if total > W*0.98:
    scale_gap = (W*0.98 - spec_w - gen_w) / (len(spec_defs)+len(gen_defs)-1)
    gap_eff = max(2.0, scale_gap)
else:
    gap_eff = GAP
x0s = (W - total)/2
spec = hflow(spec_defs, RES, x0s, gap_eff)
gen  = hflow(gen_defs, RES, x0s + spec_w + groupgap, gap_eff)

# ---- spine 'no' arrows ----
for i in range(len(spine)-1):
    arrow(spine[i][1], SP, spine[i+1][0], SP)

# ---- branches down ----
def branch(xf, yf, xt, yt, lab, lx, ly, color='#1e5a3a'):
    arrow(xf, yf, xt, yt, color=color)
    ax.text(lx, ly, lab, fontsize=FS-0.2, color=color, ha='center', fontweight='bold')

# ---- branches down: direct fan-out arrows from each gate to each leaf, so every
#      leaf has an explicit, unambiguous incoming connector ----
def fan(drop_x, y_from, leaves, color, lab, lab_x, lab_y):
    BUS_Y = RES+44           # bus row, above all leaf-arrow tails
    # vertical from the gate down to the bus
    arrow(drop_x, y_from, drop_x, BUS_Y, color)
    # horizontal distribution bus: join the gate's drop point to the leaves' own
    # drop columns (leaf centres), so the bus stays INSIDE the fed group and never
    # runs out toward a neighbouring box (e.g. the fallthrough General target).
    centers = [(x0+x1)/2 for (x0, x1) in leaves]
    bx0 = min([drop_x] + centers)
    bx1 = max([drop_x] + centers)
    ax.plot([bx0, bx1], [BUS_Y, BUS_Y], color=color, lw=1.6)
    # one distinct down-arrow per leaf, all starting BELOW the bus (clean verticals)
    for cx in centers:
        ax.annotate('', xy=(cx, RES+16), xytext=(cx, BUS_Y-2),
                    arrowprops=dict(arrowstyle='-|>', lw=1.4, color=color, shrinkA=0, shrinkB=0))
    ax.text(lab_x, lab_y, lab, fontsize=FS-0.2, color=color, ha='center', fontweight='bold')

sep = (spine[1][0]+spine[1][1])/2
spc = (spine[2][0]+spine[2][1])/2
fth = (spine[3][0]+spine[3][1])/2
spg = (spec[0][0]+spec[-1][1])/2
gen_yes_x = (gen[0][1]+gen[1][0])/2
gen_ft_x  = (gen[2][0]+gen[2][1])/2
# branch labels are anchored by their RIGHT edge GAP_LB left of their own gate's
# drop line, on a single common row, so the yes/fallthrough annotations read
# consistently and no label can ever be struck by its own drop line.  Placement
# uses the RENDERED text width (the TextPath estimate undershoots the drawn
# glyphs, which pushed a centred label past its drop line and made the two 'yes'
# labels touch: '...specialistyes...' and struck 'small').
LB_Y    = 146          # common branch-label row
GAP_LB  = 8.0          # clearance between a label's right edge and its drop line
_renderer = fig.canvas.get_renderer()
def rtext_w(s):
    t = ax.text(0, 0, s, fontsize=FS-0.2, fontweight='bold')
    bb = t.get_window_extent(renderer=_renderer)
    t.remove()
    inv = ax.transData.inverted()
    x0, _ = inv.transform((bb.x0, bb.y0))
    x1, _ = inv.transform((bb.x1, bb.y1))
    return x1 - x0
def label_cx(drop_x, text):
    # centre so the widest line's right edge sits GAP_LB left of the drop line
    width = max(rtext_w(ln) for ln in text.split('\n'))
    return drop_x - GAP_LB - width/2

fan(sep, SP-14, spec, '#1e5a3a', 'yes \u2192 specialist',
    label_cx(sep, 'yes \u2192 specialist'), LB_Y)
# The Cost/SLO 'yes' label annotates both Frontier and Small gen; split it to two
# lines so its widest line fits the gap between the two gate drop lines (a single
# line is wider than that gap, so it was struck by one of the drop lines).
fan(spc, SP-14, gen[:2], '#1e5a3a', 'yes \u2192\nfrontier / small',
    label_cx(spc, 'yes \u2192\nfrontier / small'), LB_Y)
# fallthrough -> General: orthogonal connector (down, across, down) so it cannot
# cross through its own 'fallthrough' label, and it clearly targets General only.
EY = 156                                    # elbow row
ax.plot([fth, fth], [SP-14, EY], color='#444', lw=1.8)
ax.plot([fth, gen_ft_x], [EY, EY], color='#444', lw=1.8)
ax.annotate('', xy=(gen_ft_x, RES+16), xytext=(gen_ft_x, EY),
            arrowprops=dict(arrowstyle='-|>', lw=1.8, color='#444', shrinkA=0, shrinkB=0))
ax.text(label_cx(gen_ft_x, 'fallthrough'), LB_Y, 'fallthrough',
        fontsize=FS-0.2, color='#444', ha='center', fontweight='bold')

# ---- bottom annotation ----
ax.text(W/2, 26, 'only ONE model is selected per request (early exit on a match)',
        fontsize=FS-0.2, ha='center', color='#444')
# NOTE: the [ILLUSTRATIVE][DERIVED] tag lives in the figure CAPTION (chapter-18.md),
# not in the diagram — keep it out of the drawn text.
ax.text(W/2, 13, 'policy: capability first, then cost/SLO, then general fallback.',
        fontsize=FS-0.2, ha='center', color='#444')

plt.tight_layout()
plt.savefig('design/manuscript/chapter-18/figures/fig-18-1801.png', dpi=400)
import matplotlib as mpl
with mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-18/figures/fig-18-1801.pdf', format='pdf')
plt.close()
print('wrote fig-18-1801 (column-width wide cascade, sized boxes)')
