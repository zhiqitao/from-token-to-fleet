#!/usr/bin/env python3
"""fig-02-0202: canonical prefill / persistent KV cache / decode pipeline.

Per the figure-quality review (Block C): the prior draft was too information-
dense -- every box carried a subtitle, the cache sat in prose, and the timing
acronyms (TTFT/TPOT) and a long operating-point note fought the geometry.  The
word rule was: if a reader must read text below caption size to get the primary
idea, REMOVE information rather than enlarge the composition.

This revision keeps ONLY:
  * three band titles  : PREFILL / PERSISTENT KV CACHE / DECODE
  * one-line box labels : prompt, token + position, transformer, logits +
                          sampling, first token   (prefill)
                          previous token, ... , next token  (decode)
  * one-line transition labels : populate, read, initialize, loop

Geometry carries the meaning:
  * the two PROCESSING rails contain identical box columns, and the transformer
    box shares one X-column across both rails and one shade -> "same model,
    same position".
  * the three BANDS are drawn large relative to the labels; the cache band is
    the visual middle.
  * GREEN "initialize" : starts at the RIGHT-MIDPOINT of the 'first token'
    box, runs down the right margin, left along a channel just above the decode
    rail, and drops into the TOP of the 'previous token' box.
  * GREY "loop"        : starts at the BOTTOM-MIDPOINT of the 'next token' box,
    runs below the decode rail, and rises into the BOTTOM of 'previous token' --
    so the two feedback arrows land on OPPOSITE edges of the same input box.

Monochrome except for the channel-redundant green/grey pair: green = initialize,
grey = loop.  No icons, no extra line weights, no under-size type.

Authored directly at the 6.1in column width (_hermes_print_sized) so the regen
pass does not re-boost the fonts; the on-page font sizes below are the sizes.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
from matplotlib.path import Path as _Path

BOLD = FontProperties(weight='bold')
W = 6.1 * 72          # 6.1in column, in points
FS  = 8.0             # box label  (8pt body minimum on page)
FST = 9.0             # band title
FSN = 8.5             # transition label (bumped from 8.0 for print legibility, v8 review)
PAD = 8               # horizontal padding inside each box
GAP = 11              # gap between rail boxes
BH  = 30              # box height
LM  = 8               # left margin
RMB = 16              # right margin reserved for the green descent corridor

# monochrome greys + the single green channel-accent
C_AR    = '#3a3a3a'   # rail / populate / read arrows
C_LOOP  = '#6a6a6a'   # grey loop arrow (darkened from #8a8a8a for print contrast, v8 review)
C_GN    = '#2c7a4b'   # green initialize arrow
C_EDGE  = '#5a5a5a'
C_BOX   = '#f1f1f1'   # neutral boxes
C_TOK   = '#e6e6e6'   # token boxes (first/next/previous) - shaded alike
C_TRANS = '#d8d8d8'   # transformer boxes (same model) - darkest
C_BAND  = '#f8f8f8'
C_BAND_E = '#c6c6c6'
C_CACHE = '#efefef'


def tw(s, fs=FS):
    return TextPath((0, 0), s, size=fs, prop=BOLD).get_extents().width


def bw(n):
    return max(tw(n, FS) + PAD, 44)


# ---------------- shared columns (solved to fit the 6.1in column) ---------
# transformer centre X_T is placed so the widest box left of the transformer
# (decode's 'previous token') lands flush at LM; the token-output centre X_O is
# derived so boxes never overlap and the right margin stays clear for green.
wT   = bw('transformer')
wTP  = bw('token + position')
wIn  = max(bw('prompt'), bw('previous token'))
wLog = bw('logits + sampling')
wTok = max(bw('first token'), bw('next token'))
X_T = LM + wT / 2 + GAP + wTP + GAP + wIn
X_O = X_T + wT / 2 + GAP + wLog + GAP + wTok / 2
X_BANDR = W - RMB                  # right edge of the prefill/decode bands
X_R = W - 8                        # green descent / turn-out column

# ---------------- vertical budget (y = 0 at bottom, up) ----------------
loop_chan = 26                    # grey loop channel
dc_title  = loop_chan + 26        # DECODE label (below the rail)
dc_rail   = dc_title + 42         # decode rail centre
dc_bot    = dc_rail - BH / 2 - 10
dc_top    = dc_rail + BH / 2 + 10
green_chan = dc_top + 14          # green initialize channel (read corridor)
kc_bot    = green_chan + 34       # cache band bottom
kc_top    = kc_bot + 56           # cache band top
pf_bot    = kc_top + 46           # populate corridor
pf_rail   = pf_bot + BH / 2 + 10
pf_top    = pf_rail + BH / 2 + 10
pf_title  = pf_top + 20           # PREFILL label (above the rail)
Ht = pf_title + 16

fig, ax = plt.subplots(figsize=(6.1, Ht / 72))
fig._hermes_print_sized = True
ax.set_xlim(0, W); ax.set_ylim(0, Ht); ax.axis('off')
ax.set_aspect('auto')


def label(cx, cy, s, color='#333333', fs=FS, weight='normal'):
    ax.text(cx, cy, s, ha='center', va='center', fontsize=fs, color=color,
            fontweight=weight)


def arrow(x1, y1, x2, y2, color=C_AR, lw=1.4):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='-|>', lw=lw, color=color,
                                shrinkA=0, shrinkB=0))


def box(cx, cy, txt, fill, edge=C_EDGE):
    bx = bw(txt)
    ax.add_patch(FancyBboxPatch((cx - bx / 2, cy - BH / 2), bx, BH,
                  boxstyle='round,pad=0.03,rounding_size=1.6', fc=fill, ec=edge,
                  lw=1.2, clip_on=False, zorder=3))
    ax.text(cx, cy, txt, ha='center', va='center', fontsize=FS, color='#222222',
            fontweight='bold', zorder=4)
    return bx


def band(x0, y0, x1, y1, fc=C_BAND):
    ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0,
                  boxstyle='round,pad=0.02,rounding_size=3', fc=fc, ec=C_BAND_E,
                  lw=1.0, clip_on=False, zorder=0))


def layout_row(names, cy, fills):
    """Place a rail anchored so 'transformer' sits at X_T and the token-output
    at X_O; boxes left of the transformer fill right-to-left, the box between
    transformer and token-output sits in between.  Returns name -> (l,r,b,t,cx)."""
    widths = {n: bw(n) for n in names}
    il = next(i for i, n in enumerate(names) if n == 'transformer')
    it = next(i for i, n in enumerate(names) if n in ('first token', 'next token'))
    out = {}
    out['transformer'] = (X_T - wT / 2, X_T + wT / 2, cy - BH / 2, cy + BH / 2, X_T)
    tn = names[it]
    out[tn] = (X_O - wTok / 2, X_O + wTok / 2, cy - BH / 2, cy + BH / 2, X_O)
    x = X_T + wT / 2 + GAP
    for i in range(il + 1, it):
        n = names[i]; w_ = widths[n]
        out[n] = (x, x + w_, cy - BH / 2, cy + BH / 2, x + w_ / 2)
        x += w_ + GAP
    x = X_T - wT / 2 - GAP
    for i in range(il - 1, -1, -1):
        n = names[i]; w_ = widths[n]
        out[n] = (x - w_, x, cy - BH / 2, cy + BH / 2, x - w_ / 2)
        x -= w_ + GAP
    for n, f in zip(names, fills):
        l, r, b, t, cx = out[n]
        box(cx, cy, n, f)
    return out


# ==================== PREFILL ====================
band(LM, pf_bot, X_BANDR, pf_top)
label(W / 2, pf_title, 'PREFILL', '#333333', FST, weight='bold')
pf_names = ['prompt', 'token + position', 'transformer',
            'logits + sampling', 'first token']
pf = layout_row(pf_names, pf_rail, [C_BOX, C_BOX, C_TRANS, C_BOX, C_TOK])
for a, b in [('prompt', 'token + position'), ('token + position', 'transformer'),
             ('transformer', 'logits + sampling'),
             ('logits + sampling', 'first token')]:
    arrow(pf[a][1] + 2, pf_rail, pf[b][0] - 2, pf_rail, C_AR, 1.2)

# ==================== PERSISTENT KV CACHE ====================
kc_cx = W / 2
kc_hw = 0.30 * W                       # centred, leaves the right margin clear
band(kc_cx - kc_hw, kc_bot, kc_cx + kc_hw, kc_top, C_CACHE)
label(kc_cx, (kc_top + kc_bot) / 2, 'PERSISTENT  KV  CACHE', '#333333', FST,
      weight='bold')

# ==================== populate (prefill transformer -> cache, down) ==========
arrow(X_T, pf['transformer'][2] - 2, X_T, kc_top + 2, C_AR, 2.0)
_py = (pf['transformer'][2] + kc_top) / 2
ax.text(X_T - 12, _py, 'populate', color='#333333', fontsize=FSN,
        fontweight='bold', ha='right', va='center')

# ==================== DECODE ====================
band(LM, dc_bot, X_BANDR, dc_top)
label(W / 2, dc_title, 'DECODE', '#333333', FST, weight='bold')
dc_names = ['previous token', 'token + position', 'transformer',
            'logits + sampling', 'next token']
dc = layout_row(dc_names, dc_rail, [C_TOK, C_BOX, C_TRANS, C_BOX, C_TOK])
for a, b in [('previous token', 'token + position'),
             ('token + position', 'transformer'),
             ('transformer', 'logits + sampling'),
             ('logits + sampling', 'next token')]:
    arrow(dc[a][1] + 2, dc_rail, dc[b][0] - 2, dc_rail, C_AR, 1.2)

# ==================== read (cache -> decode transformer, down) ==============
# The green "initialize" channel (gn_y = green_chan) runs in the gap BELOW the
# cache box, so the read arrow is split into two segments with a bridge gap
# where the green line passes over it.
gn_y = green_chan                  # gap below cache [dc_top, kc_bot]: no pierce
BR = 7                             # bridge half-gap where green passes over
# Upper read stub is a PLAIN line (no head) so the single "read" flow shows one
# arrowhead only at its final destination (the decode transformer).
ax.plot([X_T, X_T], [kc_bot - 2, gn_y + BR], color=C_AR, lw=2.0,
        solid_capstyle='butt', zorder=2)
arrow(X_T, gn_y - BR, X_T, dc['transformer'][3] + 2, C_AR, 2.0)
_ry = (kc_bot + gn_y + BR) / 2
ax.text(X_T - 12, _ry, 'read', color='#333333', fontsize=FSN,
        fontweight='bold', ha='right', va='center')

# ==================== append (decode transformer -> cache, up) ==============
# The decode step writes its new K/V back to the cache (the caption's "appends
# the new K/V").  Routed to the RIGHT of the read arrow (X_T + 26) so the two
# cache operations are visually distinct.  BRIDGE the arrow around gn_y where
# the green initialize line crosses it (same mechanism as the read arrow), so
# the green line passes over cleanly rather than cutting the append stroke.
X_APP = X_T + 26
ax.plot([X_APP, X_APP], [kc_bot - 4, gn_y + BR], color=C_AR, lw=2.0,
        solid_capstyle='butt', zorder=3)
ax.plot([X_APP, X_APP], [gn_y - BR, dc['transformer'][3] + 2], color=C_AR,
        lw=2.0, solid_capstyle='butt', zorder=3)
_ay = (dc['transformer'][3] + kc_bot) / 2
ax.text(X_APP + 12, _ay, 'append', color='#333333', fontsize=FSN,
        fontweight='bold', ha='left', va='center')

# R-09: the single read/append pair is a *conceptual* per-step, per-layer
# cache I/O, not one global read/append bracketing the whole transformer.
# Placed in the clear strip right of the "append" label, above the green
# initialize line (data coords ~x 295-382, y 137-160).  Darkened and moved
# clear of the append label so it reads as a caption note, not a box label.
ax.text(298, 149, 'conceptual per-step,\nper-layer cache I/O',
        color='#404040', fontsize=8.0, style='italic',
        ha='left', va='center')

# ==================== GREEN initialize ====================
# first token (right edge) -> down the right margin -> left along the channel
# below the cache box -> drop into the TOP of previous token.  The channel
# (green_chan) sits in the empty gap between the cache box bottom (kc_bot) and
# the decode rail top (dc_top), so the green line never pierces the cache box;
# the read arrow is bridged where the green line crosses it.
ft = pf['first token']
prev = dc['previous token']
# End the green drop 1pt INTO the box (below its top edge) so the arrowhead
# tip clearly touches the previous-token box's top border (no floating gap).
# FancyArrowPatch with a `path` does not render the -|> head, so the line body
# is drawn plain and an explicit annotate arrowhead is added at the terminal.
gv = [(ft[1], pf_rail), (X_R, pf_rail), (X_R, gn_y),
      (prev[4], gn_y), (prev[4], prev[3] - 1)]
gc = [_Path.MOVETO, _Path.LINETO, _Path.LINETO, _Path.LINETO, _Path.LINETO]
ax.add_patch(FancyArrowPatch(path=_Path(gv, gc), arrowstyle='-', lw=1.6,
             color=C_GN, shrinkA=0, shrinkB=0, clip_on=False, zorder=5))
ax.annotate('', xy=(prev[4], prev[3] - 1), xytext=(prev[4], prev[3] + 11),
            arrowprops=dict(arrowstyle='-|>', lw=1.6, color=C_GN,
                            shrinkA=0, shrinkB=0), zorder=5)
ax.text(X_R - 4, gn_y + 8, 'initialize', color=C_GN, fontsize=FSN,
        fontweight='bold', ha='right', va='bottom')

# ==================== GREY loop ====================
nt = dc['next token']
rv = [(nt[4], nt[2]), (nt[4], loop_chan), (prev[4], loop_chan),
      (prev[4], prev[2])]
rc = [_Path.MOVETO, _Path.LINETO, _Path.LINETO, _Path.LINETO]
ax.add_patch(FancyArrowPatch(path=_Path(rv, rc), arrowstyle='-|>', lw=1.6,
             color=C_LOOP, shrinkA=0, shrinkB=0, clip_on=False, zorder=2))
ax.text(prev[4] + 8, loop_chan - 14, 'loop', color=C_LOOP, fontsize=FSN,
        fontweight='bold', ha='left', va='center')

plt.subplots_adjust(left=0.0, right=1.0, top=1.0, bottom=0.0)
plt.savefig('design/manuscript/chapter-02/figures/fig-02-0202.png', dpi=200)
with matplotlib.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-02/figures/fig-02-0202.pdf',
                format='pdf')
plt.close()
print('wrote fig-02-0202  Ht=%.0f  X_T=%.0f X_O=%.0f X_BANDR=%.0f'
      % (Ht, X_T, X_O, X_BANDR))
