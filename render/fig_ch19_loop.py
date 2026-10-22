#!/usr/bin/env python3
"""fig-19-1901: the agent loop as a four-state state machine.

PASS-24 fix: the Archify-rendered version drew the four top state boxes edge-to-edge
with no gap and carried the descriptor (sublabel) too close to the bold title, so the
sublabel ("tool call routed", "append result") was clipped by the neighbouring box and
read as crashed text. This matplotlib version gives each box proper width + a gap, and
keeps the state title and a SHORT descriptor vertically separated inside the box.
A loop-back returns Plan -> feedback. Terminal nodes (Final answer / Stopped) below.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

FS = 9.5
W = 6.1
fig, ax = plt.subplots(figsize=(W, W*0.62))
fig._hermes_print_sized = True   # print-size authored: regen must not re-boost/reflow
ax.set_xlim(0, 10.9); ax.set_ylim(0, 6.2); ax.axis('off')

# four loop states across the top, with gaps
states = [
    ('Plan',    'read, plan',      '#d6f0f7', '#1b7a9e', 'model'),
    ('Execute', 'tool call',       '#d9f3e0', '#2e9e63', 'action'),
    ('Observe', 'append result',   '#d9f3e0', '#2e9e63', 'state'),
    ('Decide',  'resolved?',       '#fbe0e0', '#c0392b', 'check'),
]
box_w, box_h, y0 = 2.42, 1.5, 4.15
gap = 0.18
xs = [0.6 + i*(box_w+gap) for i in range(4)]
for (name, desc, fc, ec, tag), x in zip(states, xs):
    ax.add_patch(FancyBboxPatch((x, y0), box_w, box_h, boxstyle='round,pad=0.02,rounding_size=0.35',
                                fc=fc, ec=ec, lw=1.4))
    ax.text(x+0.20, y0+box_h-0.42, name, ha='left', va='center', fontsize=8.4, fontweight='bold', color='#1a1a1a')
    ax.text(x+box_w/2, y0+0.48, desc, ha='center', va='center', fontsize=8.3, color='#444')
    ax.text(x+box_w-0.12, y0+box_h-0.42, tag, ha='right', va='center', fontsize=8.0, color=ec, style='italic')

# forward loop arrows Plan->Execute->Observe->Decide
for i in range(len(xs)-1):
    ax.annotate('', xy=(xs[i+1], y0+box_h/2), xytext=(xs[i]+box_w, y0+box_h/2),
                arrowprops=dict(arrowstyle='-|>', lw=1.8, color='#555'))

# ---- Decide's three outgoing arrows, each on its OWN exit point + channel so
# they never overlap/cross (defect fix). Loop (dashed) = high channel, resolved
# (gray) = low channel, stopped (gray) = straight down; all leave Decide's bottom
# edge at distinct x and travel at distinct y levels.
x_loop, x_res = 8.7, 9.2                  # separate exit points left of Decide center
x_stp = xs[3]+box_w/2                     # stopped exits at Decide's center
y_loop, y_res = 3.62, 3.05                # loop channel ABOVE the resolved channel
plan_cx, fa_cx = xs[0]+box_w/2, xs[1]+box_w/2
term_y = 1.05                             # lower terminal row widens the arrow band

# loop-back: Decide -> Plan (dashed, the iterative loop) -- drops at x_loop, runs
# left along y_loop (well above the resolved line), then up into Plan.
ax.plot([x_loop, x_loop], [y0, y_loop], color='#1b7a9e', lw=1.6, ls='--')
ax.plot([x_loop, plan_cx], [y_loop, y_loop], color='#1b7a9e', lw=1.6, ls='--')
ax.annotate('', xy=(plan_cx, y0+0.1), xytext=(plan_cx, y_loop),
            arrowprops=dict(arrowstyle='-|>', lw=1.6, color='#1b7a9e', ls='--'))
# loop label sits just above its own dashed line, clear of the boxes and the gray
# resolved path.
ax.text((x_loop+plan_cx)/2, y_loop+0.12, 'loop (iterate) — not resolved',
        ha='center', va='bottom', fontsize=8.0, color='#1b7a9e')

# terminal outcomes below, from Decide
# Final answer: resolved arrow = down at x_res, left along y_res, then a short
# stub down into Final's top-center.  Orthogonal L-path never crosses the loop.
ax.plot([x_res, x_res], [y0, y_res], color='#555', lw=1.4)
ax.plot([x_res, fa_cx], [y_res, y_res], color='#555', lw=1.4)
ax.annotate('', xy=(fa_cx, term_y+box_h), xytext=(fa_cx, y_res),
            arrowprops=dict(arrowstyle='-|>', lw=1.4, color='#555'))
# 'resolved' label parks in the clear band between the two channels (gray line
# below, dashed blue line above), with open space on every side.
ax.text(7.9, y_res+0.10, 'resolved', ha='center', va='bottom',
        fontsize=8.0, color='#555', fontweight='bold')
# Stopped: vertical from Decide's bottom-right to Stopped's top (Stopped at xs[3])
ax.annotate('', xy=(x_stp, term_y+box_h), xytext=(x_stp, y0),
            arrowprops=dict(arrowstyle='-|>', lw=1.4, color='#555'))
ax.text(x_stp+0.12, (y0+term_y+box_h)/2, 'limit hit', ha='left', va='center',
        fontsize=8.0, color='#555', fontweight='bold')
terms = [
    ('Final answer', 'emit', '#ece6fb', '#5b3fa8', 'done', xs[1]),
    ('Stopped', 'limit', '#fdeecb', '#c98a1e', 'terminal', xs[3]),
]
for (name, desc, fc, ec, tag, tx) in terms:
    ax.add_patch(FancyBboxPatch((tx, term_y), box_w, box_h, boxstyle='round,pad=0.02,rounding_size=0.35',
                                fc=fc, ec=ec, lw=1.4))
    ax.text(tx+0.18, term_y+box_h-0.42, name, ha='left', va='center', fontsize=8.4, fontweight='bold', color='#1a1a1a')
    ax.text(tx+box_w/2-0.55, term_y+0.48, desc, ha='center', va='center', fontsize=8.3, color='#444')
    ax.text(tx+box_w-0.12, term_y+0.48, tag, ha='right', va='center', fontsize=8.0, color=ec, style='italic')

ax.text(5.0, 5.95, 'The agent loop: a four-state state machine', ha='center', va='center',
        fontsize=10.5, fontweight='bold', color='#1a1a1a')
ax.text(5.0, 0.45, 'resolved \u2192 final answer; no resolution within the turn limit \u2192 stopped [ILLUSTRATIVE conceptual]',
        ha='center', va='center', fontsize=8.0, color='#666')

out = 'design/manuscript/chapter-19/figures/fig-19-1901.png'
plt.savefig(out, dpi=170)
# vector sibling .pdf so the book embed prefers the crisp PDF (see md_to_latex
# copy_figures guard: the .pdf must be at least as new as the .png). The default
# matplotlib pdf.fonttype is 3 (Type3), which embeds text as glyph raster and the
# book build flags it; force TrueType (Type42) so the figure's text is real text.
import matplotlib as _mpl
with _mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    fig.savefig(out.replace('.png', '.pdf'))
plt.close()
print('wrote fig-19-1901 (agent loop, matplotlib)')
