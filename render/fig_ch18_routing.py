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
FS = 8.6            # ~on-page size (no boost at column width)
PADX = 0.45         # extra box width (%) beyond label
SEG = 1.2           # gap between horizontal boxes (%) of label width

def tw(s):
    return TextPath((0, 0), s, size=FS, prop=BOLD).get_extents().width

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
    ('Capability filter\n(specialised needed?)', '#e67e22', '#b35900'),
    ('Cost / SLO gate\n(route = f(cost, latency))', '#e67e22', '#b35900'),
    ('Fallthrough\n(general model)', '#e67e22', '#b35900'),
]
spine_w = sum(max(tw(l) for l in d[0].split('\n'))*(1+PADX) for d in spine_defs) + GAP*(len(spine_defs)-1)
spine = hflow(spine_defs, SP, (W - spine_w)/2, GAP)

# ---- specialist leaf group ----
spec_defs = [
    ('Embedding', '#3a6ea5', '#1a3a6b'),
    ('Vision', '#8055b5', '#5a3a8a'),
    ('Math / reason', '#c0392b', '#8a2a20'),
]
# ---- general leaf group ----
gen_defs = [
    ('Large frontier', '#1f7a8c', '#14525f'),
    ('Small gen', '#2e9e63', '#1f7245'),
    ('General model', '#2e9e63', '#1f7245'),
]
spec_w = sum(tw(l)*(1+PADX) for l,_,_ in spec_defs) + GAP*(len(spec_defs)-1) + 6
gen_w  = sum(tw(l)*(1+PADX) for l,_,_ in gen_defs)  + GAP*(len(gen_defs)-1) + 6
# two groups side by side centred with a larger separator
groupgap = 26
total = spec_w + groupgap + gen_w
x0s = (W - total)/2
spec = hflow(spec_defs, RES, x0s, GAP+6)
gen  = hflow(gen_defs, RES, x0s + spec_w + groupgap, GAP+6)

# ---- spine 'no' arrows ----
for i in range(len(spine)-1):
    arrow(spine[i][1], SP, spine[i+1][0], SP)

# ---- branches down ----
def branch(xf, yf, xt, yt, lab, lx, ly, color='#2f6f4f'):
    arrow(xf, yf, xt, yt, color=color)
    ax.text(lx, ly, lab, fontsize=FS-0.6, color=color, ha='center', fontweight='bold')

sep = (spine[1][0]+spine[1][1])/2
spc = (spine[2][0]+spine[2][1])/2
fth = (spine[3][0]+spine[3][1])/2
spg = (spec[0][0]+spec[-1][1])/2
gpg = (gen[0][0]+gen[-1][1])/2
branch(sep, SP-14, spg, RES+16, 'yes -> specialist', spg+8, 132, '#2f6f4f')
branch(spc, SP-14, gpg-30, RES+16, 'yes -> general', gpg-40, 148, '#2f6f4f')
branch(fth, SP-14, gpg+8, RES+16, 'fallthrough', gpg+55, 116, '#555')

# ---- bottom annotation ----
ax.text(W/2, 26, 'only ONE model is selected per request (early exit on a match)',
        fontsize=FS-0.6, ha='center', color='#666')
ax.text(W/2, 13, 'policy: capability first, then cost/SLO, then general fallback. [ILLUSTRATIVE][DERIVED]',
        fontsize=FS-1.0, ha='center', color='#666')

plt.tight_layout()
plt.savefig('design/manuscript/chapter-18/figures/fig-18-1801.png', dpi=200)
plt.close()
print('wrote fig-18-1801 (column-width wide cascade, sized boxes)')
