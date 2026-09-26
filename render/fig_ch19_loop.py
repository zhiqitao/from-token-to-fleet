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
box_w, box_h, y0 = 2.45, 1.5, 4.15
gap = 0.32
xs = [0.6 + i*(box_w+gap) for i in range(4)]
for (name, desc, fc, ec, tag), x in zip(states, xs):
    ax.add_patch(FancyBboxPatch((x, y0), box_w, box_h, boxstyle='round,pad=0.02,rounding_size=0.35',
                                fc=fc, ec=ec, lw=1.4))
    ax.text(x+0.20, y0+box_h-0.42, name, ha='left', va='center', fontsize=8.7, fontweight='bold', color='#1a1a1a')
    ax.text(x+box_w/2, y0+0.48, desc, ha='center', va='center', fontsize=8.3, color='#444')
    ax.text(x+box_w-0.12, y0+box_h-0.42, tag, ha='right', va='center', fontsize=7.8, color=ec, style='italic')

# forward loop arrows Plan->Execute->Observe->Decide
for i in range(len(xs)-1):
    ax.annotate('', xy=(xs[i+1], y0+box_h/2), xytext=(xs[i]+box_w, y0+box_h/2),
                arrowprops=dict(arrowstyle='-|>', lw=1.8, color='#555'))

# loop-back: Decide -> Plan (dashed, the iterative loop)
mid_y = y0-0.85
ax.plot([xs[3]+box_w/2, xs[3]+box_w/2], [y0, mid_y], color='#1b7a9e', lw=1.6, ls='--')
ax.plot([xs[3]+box_w/2, xs[0]+box_w/2], [mid_y, mid_y], color='#1b7a9e', lw=1.6, ls='--')
ax.annotate('', xy=(xs[0]+box_w/2, y0+0.1), xytext=(xs[0]+box_w/2, mid_y),
            arrowprops=dict(arrowstyle='-|>', lw=1.6, color='#1b7a9e', ls='--'))
ax.text((xs[3]+box_w/2+xs[0]+box_w/2)/2, mid_y+0.16, 'loop (iterate)', ha='center', va='bottom',
        fontsize=7.6, color='#1b7a9e')

# terminal outcomes below, from Decide
term_y = 1.35
# Decide splits: down-left to Final answer, down-right to Stopped
# Final answer box is at tx=xs[1]; land the arrowhead on its TOP edge (box_w/2).
ax.annotate('', xy=(xs[1]+box_w/2, term_y+box_h), xytext=(xs[3]+box_w*0.35, y0),
            arrowprops=dict(arrowstyle='-|>', lw=1.4, color='#555',
                            connectionstyle='arc3,rad=0.12'))
ax.plot([xs[3]+box_w*0.75, xs[3]+box_w*0.75], [y0, term_y+0.95], color='#555', lw=1.4)
ax.annotate('', xy=(xs[3]+box_w*0.75, term_y+0.95), xytext=(xs[3]+box_w*0.75, y0),
            arrowprops=dict(arrowstyle='-|>', lw=1.4, color='#555'))
terms = [
    ('Final answer', 'emit', '#ece6fb', '#5b3fa8', 'done', xs[1]),
    ('Stopped', 'limit', '#fdeecb', '#c98a1e', 'terminal', xs[3]),
]
for (name, desc, fc, ec, tag, tx) in terms:
    ax.add_patch(FancyBboxPatch((tx, term_y), box_w, box_h, boxstyle='round,pad=0.02,rounding_size=0.35',
                                fc=fc, ec=ec, lw=1.4))
    ax.text(tx+0.18, term_y+box_h-0.42, name, ha='left', va='center', fontsize=8.4, fontweight='bold', color='#1a1a1a')
    ax.text(tx+box_w/2-0.55, term_y+0.48, desc, ha='center', va='center', fontsize=8.3, color='#444')
    ax.text(tx+box_w-0.12, term_y+0.48, tag, ha='right', va='center', fontsize=7.8, color=ec, style='italic')

ax.text(5.0, 5.95, 'The agent loop: a four-state state machine', ha='center', va='center',
        fontsize=10.5, fontweight='bold', color='#1a1a1a')
ax.text(5.0, 0.45, 'resolved \u2192 final answer; no resolution within the turn limit \u2192 stopped [ILLUSTRATIVE conceptual]',
        ha='center', va='center', fontsize=7.8, color='#666')

out = 'design/manuscript/chapter-19/figures/fig-19-1901.png'
plt.savefig(out, dpi=170)
plt.close()
print('wrote fig-19-1901 (agent loop, matplotlib)')
