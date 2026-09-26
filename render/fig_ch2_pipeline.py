#!/usr/bin/env python3
"""fig-02-0202: CANONICAL end-to-end inference pipeline (prefill / persistent KV cache / decode).

Reconstruction per the figure-quality review AND the author's agreed design.

Vertical bands (top -> bottom), each in its OWN empty region so no connector
line or box border crosses a label:

  PREFILL title + subtitle
  PREFILL rail   : prompt tokens -> token embeddings -> transformer layers -> first token
  populate corridor (arrow + flanking labels)
  PERSISTENT KV CACHE band
  read/append corridor (two arrows, labels in side whitespace)
  DECODE rail    : current token -> transformer layers -> next token
  DECODE title + subtitle   (below the rail)
  green init + red loop channels (two parallel horizontals)
  operating-point note box

Flows kept apart:
  - token flow (dark)  : runs horizontally along each rail.
  - state flow: populate (prefill layers -> cache, down), read (cache ->
    decode layers, down) and append (decode layers -> cache, up) on the shared
    transformer-layers axis, read LEFT / append RIGHT of the axis.
  - green init (first token -> current token): down the far-right margin, left
    along the green channel, up into the current-token box from below.
  - red loop (next token -> current token): down the right margin, left along
    the red channel (below green), up into the current-token box from below.

Every connector label is offset OFF its connector line.  Rail boxes are laid
out left-to-right with computed non-overlapping extents (column is 6.1in).
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
FS   = 8.9
FSN  = 8.4
GAP  = 22

C_AR   = '#4a4a4a'
C_POP  = '#c06010'
C_RD   = '#2f6bb0'
C_GN   = '#2e8b57'
C_LOOP = '#c0392b'
C_PF   = '#eaf1fb'
C_DC   = '#fdf0e7'
CAT_LAYERS = ('#cfe0f5', '#27408b', '#16295c')
CAT_TOK    = ('#d5f0dd', '#2e8b57', '#1c5a37')
CAT_GREY   = ('#ececec', '#8a8a8a', '#222222')
CAT_KC     = ('#fbe3c8', '#c06010', '#7a3410')


def tw(s, fs=FS):
    return TextPath((0, 0), s, size=fs, prop=BOLD).get_extents().width


def bw(n):
    return max(tw(n, FS) + 14, 56)


# ---------------- vertical budget ----------------
note_bot = 10
note_h   = 34
red_chan = note_bot + note_h + 40       # red loop channel
g_chan   = red_chan + 34                # green init channel
dc_sub   = g_chan + 40                  # decode subtitle (below rail)
dc_title = dc_sub + 22                  # decode title
dc_rail  = dc_title + 48                # decode rail row
KVC_BOT  = dc_rail + 70                 # read/append corridor
KVC_TOP  = KVC_BOT + 76                 # cache band
pf_rail  = KVC_TOP + 58                 # populate corridor
pf_sub   = pf_rail + 34
pf_title = pf_sub + 20
Ht = pf_title + 20

fig, ax = plt.subplots(figsize=(6.1, Ht / 72))
fig._hermes_print_sized = True
ax.set_xlim(0, W); ax.set_ylim(0, Ht); ax.axis('off')
ax.set_aspect('auto')


def label(cx, cy, s, color='#333', fs=FSN, ha='center', weight='normal', va='center'):
    ax.text(cx, cy, s, ha=ha, va=va, fontsize=fs, color=color, fontweight=weight)


def arrow(x1, y1, x2, y2, color=C_AR, lw=1.4):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='-|>', lw=lw, color=color,
                                shrinkA=0, shrinkB=0))


def box(cx, cy, txt, cat, sub=None):
    fill, edge, tcol = cat
    bx = max(bw(txt), (tw(sub, FS - 1.1) + 16) if sub else 0)
    bx = max(bx, 56)
    bh = 40
    ax.add_patch(FancyBboxPatch((cx - bx / 2, cy - bh / 2), bx, bh,
                  boxstyle='round,pad=0.03,rounding_size=1.6', fc=fill, ec=edge,
                  lw=1.3, clip_on=False, zorder=3))
    ax.text(cx, cy + (0 if not sub else 4), txt, ha='center', va='center',
            fontsize=FS, color=tcol, fontweight='bold', zorder=4)
    if sub:
        ax.text(cx, cy - 10, sub, ha='center', va='center',
                fontsize=FS - 1.1, color=tcol, zorder=4)
    return bx


def layout_row(names, cy):
    """Place rail boxes anchored so the 'Transformer layers' box is centred at X_L
    and the token-output box is centred at X_F; other boxes go to the left of the
    layers box with even GAP spacing.  Returns dict name->(left,right,bot,top,cx)."""
    widths = {n: max(bw(n), (tw(sub, FS - 1.1) + 16) if sub else 0) for n, _, sub in names}
    # find indices
    il = next(i for i, (n, _, _) in enumerate(names) if n == 'Transformer layers')
    it = next(i for i, (n, _, _) in enumerate(names) if n in
              ('First generated token', 'Next token'))
    out = {}
    # place layers box at X_L
    lw_ = widths['Transformer layers']
    out['Transformer layers'] = (X_L - lw_ / 2, X_L + lw_ / 2, cy - 20, cy + 20, X_L)
    # place token-output at X_F
    tname = names[it][0]; tw_ = widths[tname]
    out[tname] = (X_F - tw_ / 2, X_F + tw_ / 2, cy - 20, cy + 20, X_F)
    # boxes between layers(left) and token-output: none in these rails
    # boxes left of the layers box: place right-to-left with GAP
    x = X_L - lw_ / 2 - GAP
    for i in range(il - 1, -1, -1):
        n = names[i][0]; w_ = widths[n]
        out[n] = (x - w_, x, cy - 20, cy + 20, x - w_ / 2)
        x -= w_ + GAP
    # boxes right of the token-output (none in these rails)
    x = X_F + tw_ / 2 + GAP
    for i in range(it + 1, len(names)):
        n = names[i][0]; w_ = widths[n]
        out[n] = (x, x + w_, cy - 20, cy + 20, x + w_ / 2)
        x += w_ + GAP
    # draw
    for n, cat, sub in names:
        l, r, b, t, cx = out[n]
        box(cx, cy, n, cat, sub=sub)
    return out


# ---------------- columns (shared axis + token output) ----------------
X_L = 0.44 * W      # transformer layers (both rails = same model)
X_F = 0.80 * W      # first / next token (both rails)
RM  = W - 12        # right margin


# ==================== PREFILL ====================
label(W / 2, pf_title, 'PREFILL', '#1a3a6b', FS + 2.6, weight='bold')
label(W / 2, pf_sub, 'processes the whole prompt in parallel  ·  measured by TTFT', '#2a4a7a', FSN - 0.6)
pf_names = [('Prompt tokens', CAT_GREY, None),
            ('Token embeddings', CAT_GREY, None),
            ('Transformer layers', CAT_LAYERS, 'same model as decode'),
            ('First generated token', CAT_TOK, 'logits + sampling')]
pf = layout_row(pf_names, pf_rail)
for a, b in [('Prompt tokens', 'Token embeddings'),
             ('Token embeddings', 'Transformer layers'),
             ('Transformer layers', 'First generated token')]:
    arrow(pf[a][1] + 2, pf_rail, pf[b][0] - 2, pf_rail, C_AR, 1.2)
ax.add_patch(FancyBboxPatch((10, pf_rail - 27), W - 20, 54,
              boxstyle='round,pad=0.02,rounding_size=3', fc=C_PF, ec='#b9cbe8',
              lw=1.0, alpha=0.45, clip_on=False, zorder=0))

# ==================== PERSISTENT KV CACHE ====================
kc_cx = W / 2
kc_hw = 0.40 * W
label(kc_cx, KVC_TOP - 15, 'PERSISTENT  KV  CACHE', '#7a3410', FS + 1.4, weight='bold')
label(kc_cx, KVC_TOP - 34, 'accumulated key/value state for the whole conversation', '#8a4a1a', FSN - 0.7)
label(kc_cx, KVC_BOT + 17,
      'created by prefill   ·   read + extended by decode   ·   never recomputed',
      '#7a3410', FSN - 0.7, weight='bold')
ax.add_patch(FancyBboxPatch((kc_cx - kc_hw, KVC_BOT), kc_hw * 2, 76,
              boxstyle='round,pad=0.04,rounding_size=4', fc=CAT_KC[0], ec='#c06010',
              lw=1.6, clip_on=False, zorder=1))

# ==================== populate (prefill layers -> cache, down) ====================
arrow(X_L, pf['Transformer layers'][2] - 2, X_L, KVC_TOP - 2, C_POP, 2.0)
_py = (pf['Transformer layers'][2] + KVC_TOP) / 2
ax.text(X_L - 11, _py, 'populate', color='#7a3410', fontsize=FSN - 0.5,
        fontweight='bold', ha='right', va='center')
ax.text(X_L + 11, _py, 'cache', color='#7a3410', fontsize=FSN - 0.5,
        ha='left', va='center')

# ==================== DECODE title + subtitle (BELOW rail) ====================
label(W / 2, dc_title, 'DECODE', '#8a3a12', FS + 2.6, weight='bold')
label(W / 2, dc_sub, 'generates tokens one at a time  ·  measured by TPOT and ITL', '#7a3410', FSN - 0.6)

# ==================== DECODE rail ====================
dc_names = [('Current token', CAT_TOK, None),
            ('Transformer layers', CAT_LAYERS, 'same model as prefill'),
            ('Next token', CAT_TOK, 'logits + sampling')]
dc = layout_row(dc_names, dc_rail)
for a, b in [('Current token', 'Transformer layers'), ('Transformer layers', 'Next token')]:
    arrow(dc[a][1] + 2, dc_rail, dc[b][0] - 2, dc_rail, C_AR, 1.2)
ax.add_patch(FancyBboxPatch((10, dc_rail - 27), W - 20, 54,
              boxstyle='round,pad=0.02,rounding_size=3', fc=C_DC, ec='#e8c3a8',
              lw=1.0, alpha=0.45, clip_on=False, zorder=0))

# read / append (cache <-> decode layers) — labels centre in the clear corridor
# between the cache box bottom and the decode band top edge.
dl_top = dc['Transformer layers'][2]
band_top = dc_rail + 27            # decode band top edge (data coords)
rd_x = X_L - 41
ap_x = X_L - 25
arrow(rd_x, KVC_BOT + 2, rd_x, dl_top - 2, C_RD, 2.0)
arrow(ap_x, dl_top - 2, ap_x, KVC_BOT + 2, C_POP, 2.0)
_cy = (KVC_BOT + band_top) / 2
ax.text(rd_x - 7, _cy, 'read K/V', color='#2f6bb0', fontsize=FSN - 0.6,
        fontweight='bold', ha='right', va='center')
ax.text(ap_x + 7, _cy, 'append K/V', color='#7a3410', fontsize=FSN - 0.6,
        fontweight='bold', ha='left', va='center')

# ==================== GREEN INIT (first token -> current token) ====================
ft = pf['First generated token']
ct = dc['Current token']
gv = [(ft[4], ft[2]), (RM, ft[2]), (RM, g_chan), (ct[4], g_chan), (ct[4], ct[2])]
gc = [_Path.MOVETO, _Path.LINETO, _Path.LINETO, _Path.LINETO, _Path.LINETO]
ax.add_patch(FancyArrowPatch(path=_Path(gv, gc), arrowstyle='-|>', lw=1.8,
             color=C_GN, shrinkA=0, shrinkB=0, clip_on=False, zorder=2))
# green label ABOVE the green channel (line at g_chan, text centred above it)
ax.text(ct[4] + 8, g_chan + 11, 'Initializes decode (with the first token)',
        color='#1c5a37', fontsize=FSN - 0.7, fontweight='bold', ha='left', va='center')

# ==================== RED AUTOREGRESSIVE LOOP ====================
nt = dc['Next token']
rv = [(nt[4], nt[2]), (RM, nt[2]), (RM, red_chan), (ct[0] - 12, red_chan), (ct[0] - 12, ct[2] - 4)]
rc = [_Path.MOVETO, _Path.LINETO, _Path.LINETO, _Path.LINETO, _Path.LINETO]
ax.add_patch(FancyArrowPatch(path=_Path(rv, rc), arrowstyle='-|>', lw=1.8,
             color=C_LOOP, shrinkA=0, shrinkB=0, clip_on=False, zorder=2))
# red label BELOW the red channel
ax.text(ct[0] - 14, red_chan - 12, 'Repeat for next token (autoregressive loop)',
        color='#8f2318', fontsize=FSN - 0.7, fontweight='bold', ha='right', va='center')

# ==================== operating-point qualification ====================
ax.add_patch(FancyBboxPatch((6, note_bot - 2), W - 12, note_h + 4,
              boxstyle='round,pad=0.02,rounding_size=3', fc='#f7f7f7', ec='#c8c8c8',
              lw=0.9, clip_on=False, zorder=0))
label(W / 2, note_bot + note_h / 2 + 7,
      'Compute- vs. bandwidth-bound is an operating-point property:',
      '#222', FSN, weight='bold')
label(W / 2, note_bot + note_h / 2 - 7,
      'prefill is commonly compute-sensitive, decode often bandwidth-sensitive — not a fixed rule.',
      '#333', FSN - 0.6)

plt.subplots_adjust(left=0.02, right=0.98, top=0.99, bottom=0.01)
plt.savefig('design/manuscript/chapter-02/figures/fig-02-0202.png', dpi=200)
with matplotlib.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-02/figures/fig-02-0202.pdf', format='pdf')
plt.close()
print('wrote fig-02-0202  Ht=%.0f' % Ht)
