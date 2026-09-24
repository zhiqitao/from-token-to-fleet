import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ---- fig-14-1401: model-selection screen pipeline ----
# Screen on capability first, then benchmark survivors on the real workload.
# Authored at ~6.1in (print column) so it places 1:1 and labels keep their size.
# Two aligned rows: top = STATE, bottom = PROCESS. Explicit vertical connectors drop each
# state box onto its process box so the filter-then-select sequence reads directly.
fig, ax = plt.subplots(figsize=(6.1, 3.0))
fig._hermes_print_sized = True   # regen must not re-boost/reflow
ax.set_xlim(0, 23); ax.set_ylim(0, 6.2); ax.axis('off')
ax.set_title('Select models: screen on capability, then benchmark on the workload',
             fontsize=9.5, fontweight='bold', color='#1a1a1a')

def cell(x, y, w, h, label, fc):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.05', fc=fc, ec='#1a3a6b', lw=1.3))
    ax.text(x+w/2, y+h/2, label, ha='center', va='center', fontsize=9.0, color='white', fontweight='bold')

def stage(x, w, name, screen, fc1, fc2):
    cell(x, 3.9, w, 1.15, name, fc1)
    cell(x, 2.2, w, 1.15, screen, fc2)
    # vertical connector linking the state (top) to its process (bottom)
    ax.annotate('', xy=(x+w/2, 2.2+1.15), xytext=(x+w/2, 3.9),
                arrowprops=dict(arrowstyle='-|>', lw=1.8, color='#2f6f4f'))
    ax.text(x+w/2, 3.06, 'screen', fontsize=7.6, color='#2f6f4f', ha='center', va='center', fontweight='bold')

# Stage 1: candidates -> capability screen
stage(0.9, 5.2, 'Candidate\nmodels', 'Capability screen\n(MMLU / GSM8K)', '#3a6ea5', '#e67e22')
# Stage 2: survivors -> deployment bench
stage(7.2, 5.2, 'Survivors', 'Deployment bench\n(goodput)', '#3a6ea5', '#e67e22')
# Stage 3: selection + TCO
stage(13.5, 5.2, 'Selection', 'TCO + SLO gate', '#3a6ea5', '#e67e22')

# arrows between stages (top row)
for x0, x1 in [(6.1, 7.2), (12.4, 13.5)]:
    ax.annotate('', xy=(x1+0.05, 4.48), xytext=(x0-0.05, 4.48),
                arrowprops=dict(arrowstyle='-|>', lw=2.0, color='#444'))
# the final gate must pass before deployment: arrow out of the TCO+SLO gate box (bottom row)
ax.annotate('', xy=(20.6, 2.775), xytext=(18.7, 2.775),
            arrowprops=dict(arrowstyle='-|>', lw=2.2, color='#2f6f4f'))
ax.text(20.9, 2.775, 'deployed', fontsize=8.5, color='#2f6f4f', fontweight='bold', ha='left', va='center')

ax.text(11.0, 1.1, 'filter narrows the candidates (capability first), then survivors are\nmeasured on the real workload against the SLO gate.  [ILLUSTRATIVE][DERIVED]',
        fontsize=7.5, ha='center', color='#666')
plt.tight_layout(pad=0.2)
plt.savefig('design/manuscript/chapter-14/figures/fig-14-1401.png', dpi=200)
import matplotlib as mpl
with mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-14/figures/fig-14-1401.pdf', format='pdf')
plt.close()
print('wrote fig-14-1401 (state->process connectors, print-sized)')
