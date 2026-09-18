import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ---- fig-18-1801: Sequential model-routing decision tree ----
# The correct policy is a SEQUENTIAL cascade with early exit, not a parallel
# fan-out:  Request -> capability filter -> (yes: specialist model) / (no) ->
# cost+SLO gate -> (yes: general model) / (no) -> fallthrough general model.
fig, ax = plt.subplots(figsize=(6.0, 6.0))
ax.set_xlim(0, 20); ax.set_ylim(0, 17); ax.axis('off')

ax.set_title('Routing every request to the right specialised model (sequential cascade)',
             fontsize=11.5, fontweight='bold', ha='center', color='#1a1a1a')

def box(x, y, w, h, label, fc, ec, fs=10, tc='white'):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.04', fc=fc, ec=ec, lw=1.2))
    ax.text(x+w/2, y+h/2, label, ha='center', va='center', fontsize=fs, color=tc, fontweight='bold')

# Root
box(7.5, 15.0, 5.0, 1.2, 'Request', '#27408b', '#1a3a6b')
# Gate 1: capability
box(2.0, 12.0, 6.5, 1.3, 'Capability filter\n(specialised needed?)', '#e67e22', '#b35900', 9)
# Gate 2: cost/SLO
box(2.0, 9.0, 6.5, 1.3, 'Cost / SLO gate\n(route = f(cost, latency))', '#e67e22', '#b35900', 9)
# Fallthrough
box(2.0, 6.0, 6.5, 1.3, 'Fallthrough\n(general model)', '#e67e22', '#b35900', 9)

# Specialist models (fed by gate1 'yes' on the right)
box(0.5, 3.0, 4.2, 1.1, 'Embedding', '#3a6ea5', '#1a3a6b')
box(5.2, 3.0, 4.2, 1.1, 'Vision', '#8055b5', '#5a3a8a')
box(9.9, 3.0, 4.2, 1.1, 'Math / reasoning', '#c0392b', '#8a2a20')
# General models (fed by gate2 'yes' / fallthrough)
box(14.6, 3.0, 4.2, 1.1, 'Small gen', '#6f9e5f', '#3d7a44')
# Large frontier (top-right, fed by gate2 'yes')
box(14.6, 6.0, 4.2, 1.1, 'Large frontier', '#c0392b', '#8a2a20')

# Sequential west-to-east flow with yes/no branches
def arrow(x1,y1,x2,y2,color='#555',lab=None,lx=None,ly=None,lc=None):
    ax.annotate('', xy=(x2,y2), xytext=(x1,y1), arrowprops=dict(arrowstyle='-|>', lw=1.6, color=color))
    if lab:
        ax.text(lx if lx else (x1+x2)/2, ly if ly else ((y1+y2)/2)+0.2, lab, fontsize=9,
                color=lc if lc else color, ha='center', fontweight='bold')

# Request -> gate1
arrow(10.0, 15.0, 5.2, 13.3)
# gate1 -> gate2 (the 'no' path, left side) and gate1 -> specialist (the 'yes' path, right)
arrow(3.0, 12.0, 3.0, 10.3, color='#555', lab='no', lx=1.6, ly=11.2)
arrow(8.5, 12.3, 2.6, 4.1, color='#2f6f4f', lab='yes → specialist', lx=6.6, ly=7.6, lc='#2f6f4f')
# gate2 -> gate3 (no) and gate2 -> general (yes)
arrow(3.0, 9.0, 3.0, 7.3, color='#555', lab='no', lx=1.6, ly=8.2)
arrow(8.5, 9.3, 16.7, 7.1, color='#2f6f4f', lab='yes → general', lx=13.4, ly=8.9, lc='#2f6f4f')
# gate3 -> fallthrough general
arrow(5.2, 6.0, 16.0, 4.1, color='#555', lab='fallthrough', lx=11.8, ly=5.6)

# annotate: only one model is selected per request
ax.text(10.0, 1.5, 'only ONE model is selected per request (early exit on a match)',
        fontsize=8.5, ha='center', color='#666')
ax.text(10.0, 0.7, 'policy: capability first, then cost/SLO, then general fallback. [2° DERIVED]',
        fontsize=9.5, ha='center', color='#666')

plt.tight_layout()
plt.savefig('design/manuscript/chapter-18/figures/fig-18-1801.png', dpi=150)
plt.close()
print('wrote fig-18-1801 (sequential decision tree)')
