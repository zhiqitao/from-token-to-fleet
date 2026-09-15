import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ---- fig-14-1401: model-selection screen pipeline ----
# Screen on capability first, then benchmark survivors on the real workload.
fig, ax = plt.subplots(figsize=(9, 3.6))
ax.set_xlim(0, 22); ax.set_ylim(0, 6); ax.axis('off')
ax.set_title('Selecting a model for the fleet: screen on capability, then benchmark on the workload',
             fontsize=11, fontweight='bold', color='#1a1a1a')

def cell(x, y, w, h, label, fc):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.05', fc=fc, ec='#1a3a6b', lw=1.1))
    ax.text(x+w/2, y+h/2, label, ha='center', va='center', fontsize=8.6, color='white', fontweight='bold')

def stage(x, w, name, screen, fc1, fc2):
    cell(x, 3.6, w, 1.1, name, fc1)
    cell(x, 2.0, w, 1.1, screen, fc2)

# Stage 1: candidates -> capability screen
stage(0.6, 4.6, 'Candidate models', 'Capability screen\n(MMLU / GSM8K / …)', '#3a6ea5', '#e67e22')
# Stage 2: survivors -> deployment bench
stage(7.0, 4.6, 'Survivors', 'Deployment bench\n(TTFT / goodput / KV)', '#3a6ea5', '#e67e22')
# Stage 3: selection + TCO
stage(13.4, 4.6, 'Selection', 'TCO + SLO gate', '#3a6ea5', '#e67e22')

# arrows between stages
for x0, x1 in [(5.2, 7.0), (11.6, 13.4)]:
    ax.annotate('', xy=(x1+0.1, 4.15), xytext=(x0-0.1, 4.15),
                arrowprops=dict(arrowstyle='-|>', lw=2.0, color='#444'))
ax.text(18.0, 4.15, '→ deployed', fontsize=8, color='#2f6f4f', fontweight='bold')

ax.text(11.0, 1.0, 'filter narrows the candidate set (capability first), then the surviving\nmodels are measured on the real workload against the SLO gate.  [2° DERIVED]',
        fontsize=8, ha='center', color='#666')
plt.tight_layout()
plt.savefig('design/manuscript/chapter-14/figures/fig-14-1401.png', dpi=150)
plt.close()
print('wrote fig-14-1401')
