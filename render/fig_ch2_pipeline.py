#!/usr/bin/env python3
"""fig-02-0202: CANONICAL end-to-end inference pipeline (prefill / persistent KV cache / decode).

Reconstruction per the figure-quality review AND the author's agreed design:
  PREFILL (top, blue)      : prompt -> token embeddings -> transformer layers
                             -> first generated token (logits + sampling)
  PERSISTENT KV CACHE (mid): the accumulated conversation state, orange
  DECODE  (bottom, peach)  : current token -> transformer layers -> next token
                             (logits + sampling)  -- autoregressive loop

Column budget: the prefill/decode rails carry 4 / 3 boxes across the 6.1in
column; 'logits + sampling' is folded into the token-OUTPUT box (review item 6
allows the simplification if the caption says the layers output passes through
an output-head/sampling step).  Both rails' 'Transformer layers' boxes share
one x-column, so the same-model axis is explicit.

HOW THE FLOWS ARE KEPT APART:
  - STATE FLOW (short verticals in the shared transformer-layers column):
      populate (prefill layers -> cache, orange, down)
      read     (cache -> decode layers, blue, down, on the LEFT)
      append   (decode layers -> cache, orange, up, on the RIGHT)
    read and append land on opposite sides of the layers box so direction is
    unmistakable, not a narrow collinear pair.
  - TOKEN FLOW (dark) runs along each rail.
  - GREEN INIT (first token -> decode): drops down the far-right margin, runs
    left along an UPPER channel, rises into the CURRENT token from below.
  - RED LOOP (next token -> current): drops down the right margin, runs left
    along a LOWER channel (below the green channel), rises into the CURRENT
    token from below-left.  Single unambiguous recurrence representation.

Each rail's title above it and its metric note below it; titles/metrics use the
inter-band gaps cleanly.  The operating-point qualification is its own band at
the bottom.  Colour carries category (blue=compute, orange=KV state,
green=init, red=recurrence) and is grayscale-safe via arrows + position.
Authored at the 6.1in column width (exempt from regen re-boost).
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
from matplotlib.path import Path as _Path

BOLD = FontProperties(weight='bold')
W = 6.1 * 72
FS   = 8.7
FSL  = 8.4
FSN  = 8.2
GAP  = 16                     # arrow gap between boxes

C_AR = '#4a4a4a'; C_POP = '#c06010'; C_RD = '#2f6bb0'; C_GN = '#2e8b57'; C_LOOP = '#c0392b'
C_PF = '#eaf1fb'; C_DC = '#fdf0e7'; C_KC = '#fbe3c8'
CAT_LAYERS = ('#cfe0f5', '#27408b', '#16295c')
CAT_TOK    = ('#d5f0dd', '#2e8b57', '#1c5a37')
CAT_GREY   = ('#ececec', '#8a8a8a', '#222222')


def tw(s, fs=FS):
    return TextPath((0, 0), s, size=fs, prop=BOLD).get_extents().width


# ---------------- bottom-up vertical budget ----------------
note_y   = 14
note_h   = 34
red_chan = note_y + note_h + 18
g_chan   = red_chan + 18
dc_cy    = g_chan + 44
dc_top   = dc_cy + 27
dc_title = dc_top + 18
dc_sub   = dc_title + 20
dc_under = dc_sub + 18                  # decode metric line (under the rail, above cache? no) -- see below
KVC_h   = 72
KVC_BOT = dc_cy + 27 + 30               # cache band sits above the decode rail
KVC_TOP = KVC_BOT + KVC_h
pf_cy   = KVC_TOP + 46                  # prefill rail row
pf_top  = pf_cy + 27
pf_title = pf_top + 18
pf_sub   = pf_title + 20
Ht = pf_sub + 22


fig, ax = plt.subplots(figsize=(6.1, Ht / 72))
fig._hermes_print_sized = True
ax.set_xlim(0, W); ax.set_ylim(0, Ht); ax.axis('off')
ax.set_aspect('auto')


def label(cx, cy, s, color='#333', fs=FSL, ha='center', weight='normal', va='center'):
    ax.text(cx, cy, s, ha=ha, va=va, fontsize=fs, color=color, fontweight=weight)


def arrow(x1, y1, x2, y2, color=C_AR, lw=1.4):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='-|>', lw=lw, color=color,
                                shrinkA=0, shrinkB=0))


def box(cx, cy, txt, cat, sub=None, fs=FS):
    fill, edge, tcol = cat
    bw = max(tw(txt, fs) + 14, 66)
    bh = 40
    ax.add_patch(FancyBboxPatch((cx - bw / 2, cy - bh / 2), bw, bh,
                  boxstyle='round,pad=0.03,rounding_size=1.6', fc=fill, ec=edge,
                  lw=1.3, clip_on=False, zorder=3))
    ax.text(cx, cy + (0 if not sub else 4), txt, ha='center', va='center',
            fontsize=fs, color=tcol, fontweight='bold', zorder=4)
    if sub:
        ax.text(cx, cy - 9, sub, ha='center', va='center',
                fontsize=fs - 1.0, color=tcol, zorder=4)
    return bw


def row_boxes(order, cy):
    """Place boxes left-to-right with equal GAP, return dict name->(left,right,bot,top,cx).
    order = list of (name, cat, sub)."""
    widths = {n: max(tw(n, FS) + 14, 66) for n, _, _ in order}
    total = sum(widths.values()) + GAP * (len(order) - 1)
    x0 = (W - total) / 2
    out = {}
    cx = x0
    for n, cat, sub in order:
        bw = widths[n]
        out[n] = (cx, cx + bw, cy - 20, cy + 20, cx + bw / 2)
        box(cx + bw / 2, cy, n, cat, sub=sub)
        cx += bw + GAP
    return out


# ==================== shared columns ====================
# Transformer-layers column is the SAME in both rails (the same model).  Derive
# it first from the layers box, then the token-output column aligns between
# prefill (first token) and decode (next token).
X_L = 0.47 * W
X_F = 0.83 * W
# we override the auto-layout: place layers at X_L and the token output at X_F.
# Layout prefill (4 boxes) and decode (3 boxes) around them.

# ==================== PREFILL rail (top) ====================
label(W / 2, pf_title, 'PREFILL', '#1a3a6b', FS + 2.4, weight='bold')
label(W / 2, pf_sub, 'processes the whole prompt in parallel  ·  measured by TTFT',
      '#2a4a7a', FSN)

# Prefill boxes: prompt, embeddings, layers, first-token(logits+samp).
# Anchor layers at X_L and first token at X_F; place prompt/embeddings to the left.
pf_anchor = {}
# compute widths
def bw(n): return max(tw(n, FS) + 14, 66)
pw = bw('Prompt tokens'); ew = bw('Token embeddings'); lw = bw('Transformer layers')
fw = bw('First generated token')

xl = X_L                      # layers centre
xf = X_F                      # first-token centre
xe = xl - lw / 2 - GAP - ew / 2      # embeddings centre
xp = xe - ew / 2 - GAP - pw / 2      # prompt centre
pf_anchor['Prompt tokens'] = (xp - pw / 2, xp + pw / 2, pf_cy - 20, pf_cy + 20, xp)
pf_anchor['Token embeddings'] = (xe - ew / 2, xe + ew / 2, pf_cy - 20, pf_cy + 20, xe)
pf_anchor['Transformer layers'] = (xl - lw / 2, xl + lw / 2, pf_cy - 20, pf_cy + 20, xl)
pf_anchor['First generated token'] = (xf - fw / 2, xf + fw / 2, pf_cy - 20, pf_cy + 20, xf)
box(xl, pf_cy, 'Transformer layers', CAT_LAYERS, sub='same model as decode')
box(xp, pf_cy, 'Prompt tokens', CAT_GREY)
box(xe, pf_cy, 'Token embeddings', CAT_GREY)
box(xf, pf_cy, 'First generated token', CAT_TOK, sub='logits + sampling')
for a, b in [('Prompt tokens', 'Token embeddings'),
             ('Token embeddings', 'Transformer layers'),
             ('Transformer layers', 'First generated token')]:
    arrow(pf_anchor[a][1] + 2, pf_cy, pf_anchor[b][0] - 2, pf_cy, C_AR, 1.2)
ax.add_patch(FancyBboxPatch((10, pf_cy - 27), W - 20, 54,
              boxstyle='round,pad=0.02,rounding_size=3', fc=C_PF, ec='#b9cbe8',
              lw=1.0, alpha=0.45, clip_on=False, zorder=0))

# ==================== PERSISTENT KV CACHE (middle) ====================
kc_hw = 0.40 * W
kc_cx = W / 2
label(kc_cx, KVC_TOP - 16, 'PERSISTENT  KV  CACHE', '#7a3410', FS + 1.2, weight='bold')
label(kc_cx, KVC_TOP - 35, 'accumulated key/value state for the whole conversation',
      '#8a4a1a', FSN - 0.6)
label(kc_cx, KVC_BOT + 17,
      'created by prefill   ·   read + extended by decode   ·   never recomputed',
      '#7a3410', FSN - 0.6, weight='bold')
ax.add_patch(FancyBboxPatch((kc_cx - kc_hw, KVC_BOT), kc_hw * 2, KVC_h,
              boxstyle='round,pad=0.04,rounding_size=4', fc=C_KC, ec='#c06010',
              lw=1.6, clip_on=False, zorder=1))

# ==================== DECODE rail (bottom) ====================
label(W / 2, dc_title, 'DECODE', '#8a3a12', FS + 2.4, weight='bold')
label(W / 2, dc_cy - 27 - 12, 'generates tokens one at a time  ·  measured by TPOT and ITL',
      '#7a3410', FSN)

cw = bw('Current token'); nw = bw('Next token')
xc = pf_anchor['Current token'][0] if 'Current token' in pf_anchor else 0
# current token at the left margin; layers at X_L; next token at X_F
xc_centre = 0.08 * W
nxc = X_F
dc_anchor = {}
dc_anchor['Current token'] = (xc_centre - cw / 2, xc_centre + cw / 2, dc_cy - 20, dc_cy + 20, xc_centre)
dc_anchor['Transformer layers'] = (X_L - lw / 2, X_L + lw / 2, dc_cy - 20, dc_cy + 20, X_L)
dc_anchor['Next token'] = (nxc - nw / 2, nxc + nw / 2, dc_cy - 20, dc_cy + 20, nxc)
box(xc_centre, dc_cy, 'Current token', CAT_TOK)
box(X_L, dc_cy, 'Transformer layers', CAT_LAYERS, sub='same model as prefill')
box(nxc, dc_cy, 'Next token', CAT_TOK, sub='logits + sampling')
for a, b in [('Current token', 'Transformer layers'),
             ('Transformer layers', 'Next token')]:
    arrow(dc_anchor[a][1] + 2, dc_cy, dc_anchor[b][0] - 2, dc_cy, C_AR, 1.2)
ax.add_patch(FancyBboxPatch((10, dc_cy - 27), W - 20, 54,
              boxstyle='round,pad=0.02,rounding_size=3', fc=C_DC, ec='#e8c3a8',
              lw=1.0, alpha=0.45, clip_on=False, zorder=0))

# ==================== STATE FLOW (populate / read / append) ====================
pfL = pf_anchor['Transformer layers']
dcL = dc_anchor['Transformer layers']
# populate: prefill layers -> cache (down), at the layers column
arrow(X_L, pfL[2] - 2, X_L, KVC_TOP - 2, C_POP, 2.0)
_popy = (pfL[2] + KVC_TOP) / 2
ax.text(X_L - 12, _popy, 'populate', color='#7a3410', fontsize=FSN - 0.4,
        fontweight='bold', ha='right', va='center')
ax.text(X_L + 12, _popy, 'KV cache', color='#7a3410', fontsize=FSN - 0.4,
        ha='left', va='center')

# read: cache -> decode layers (down, LEFT of layers column)
rd_x = X_L - 28
arrow(rd_x, KVC_BOT + 2, rd_x, dcL[2] - 2, C_RD, 2.0)
_rdy = (KVC_BOT + dcL[2]) / 2
ax.text(rd_x - 8, _rdy, 'read cached K/V', color='#2f6bb0', fontsize=FSN - 0.4,
        fontweight='bold', ha='right', va='center')

# append: decode layers -> cache (up, RIGHT of layers column)
ap_x = X_L + 22
arrow(ap_x, dcL[2] - 2, ap_x, KVC_BOT + 2, C_POP, 2.0)
_apy = (KVC_BOT + dcL[2]) / 2
ax.text(ap_x + 8, _apy, 'append new K/V', color='#7a3410', fontsize=FSN - 0.4,
        fontweight='bold', ha='left', va='center')

# ==================== GREEN INIT (first token -> decode loop) ====================
ft = pf_anchor['First generated token']
ct = dc_anchor['Current token']
rmargin = W - 14
gv = [(ft[4], ft[2]), (rmargin, ft[2]), (rmargin, g_chan),
      (ct[4], g_chan), (ct[4], ct[3])]
gc = [_Path.MOVETO, _Path.LINETO, _Path.LINETO, _Path.LINETO, _Path.LINETO]
ax.add_patch(FancyArrowPatch(path=_Path(gv, gc), arrowstyle='-|>', lw=1.8,
             color=C_GN, shrinkA=0, shrinkB=0, clip_on=False, zorder=2))
ax.text(rmargin - 4, (ft[2] + g_chan) / 2, 'Initializes decode\n(with the first token)',
        color='#1c5a37', fontsize=FSN - 0.6, fontweight='bold', ha='right', va='center')

# ==================== RED AUTOREGRESSIVE LOOP (next -> current) ====================
nt = dc_anchor['Next token']
rv = [(nt[4], nt[3]), (rmargin, nt[3]), (rmargin, red_chan),
      (ct[0] - 10, red_chan), (ct[0] - 10, ct[2] + 4)]
rc = [_Path.MOVETO, _Path.LINETO, _Path.LINETO, _Path.LINETO, _Path.LINETO]
ax.add_patch(FancyArrowPatch(path=_Path(rv, rc), arrowstyle='-|>', lw=1.8,
             color=C_LOOP, shrinkA=0, shrinkB=0, clip_on=False, zorder=2))
ax.text(ct[0] - 12, red_chan - 12, 'Repeat for next token\n(autoregressive loop)',
        color='#8f2318', fontsize=FSN - 0.6, fontweight='bold', ha='right', va='center')

# ==================== operating-point qualification ====================
ax.add_patch(FancyBboxPatch((10, note_y), W - 20, note_h,
              boxstyle='round,pad=0.02,rounding_size=3', fc='#f7f7f7', ec='#c8c8c8',
              lw=0.9, clip_on=False, zorder=0))
label(W / 2, note_y + note_h / 2 + 7,
      'Compute- vs. bandwidth-bound is an operating-point property:',
      '#222', FSN, weight='bold')
label(W / 2, note_y + note_h / 2 - 7,
      'prefill is commonly compute-sensitive, decode often bandwidth-sensitive at low batch, but neither is a fixed rule.',
      '#333', FSN - 0.4)

plt.subplots_adjust(left=0.02, right=0.98, top=0.99, bottom=0.01)
plt.savefig('design/manuscript/chapter-02/figures/fig-02-0202.png', dpi=200)
with matplotlib.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-02/figures/fig-02-0202.pdf', format='pdf')
plt.close()
print('wrote fig-02-0202 (three-band reconstruction)  Ht=%.0f' % Ht)
