import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['pdf.fonttype']=42
matplotlib.rcParams['ps.fonttype']=42
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

base = 'design/manuscript/chapter-%02d/figures/fig-%02d-%02d01.png'

# ---- Ch13: reference-architecture ladder + escalation triggers ----
# DISABLED: redrawn with Archify (render/archify/ch13-ladder.json + ch13-ladder-min.html)
# to fix the green de-escalation label overlapping the Cluster/fleet box.
# Asset: design/manuscript/chapter-13/figures/fig-13-1301.{pdf,png}.

# ---- Ch14: capability screen then deployment benchmark ----
# RETIRED: this single-row block used 2.6-unit boxes with long labels
# ('Capability screen (MMLU/GSM8K/QA)', 'Deployment bench (TTFT/goodput/KV)')
# that clip at the box right edge (B06). The canonical generator is
# render/fig_ch14_select.py (two aligned STATE/PROCESS rows, 5.2-unit boxes,
# shorter labels). Do NOT regenerate fig-14-1401 from this batch.
print('Ch14: see render/fig_ch14_select.py (stale batch block retired)')

# ---- Ch16: TCO three delivery modes ----
# RETIRED: this block drew the STALE pre-rework scenario ($21.2K/mo, break-even 1.02M,
# canonical 26M req/mo) that contradicts the Ch16 caption and the 6.24M business-hours
# basis (B01/B07). The canonical generator is render/fig_ch16_tco.py, which draws the
# root-derived fleet model and explicit paid-occupancy assumptions.
# Do NOT regenerate fig-16-1601 from this batch or duplicate its numeric inputs.
print('Ch16: see render/fig_ch16_tco.py (stale batch block retired)')

# ---- Ch21: AI Factory promotion pipeline ----
# RETIRED: this block drew an 8-box chevron chain with 'Rollback' INLINE as a
# forward stage before Serve, a single 'gate' tick at the Evaluate->Canary seam
# (matching neither the title nor the caption), and ambiguous red rollback arrows
# (C-16). The canonical generator is render/fig_ch21_pipeline.py: 7 forward stages
# (Data->Train->Eval->Canary->Observe->Promote->Serve) with rollback as a separate
# red FAIL box (the failure path) and a green production-feedback loop. Do NOT
# regenerate fig-21-2101 from this batch.
print('Ch21: see render/fig_ch21_pipeline.py (stale batch block retired)')

# ---- Ch23: from vague ask to architectural bounds (worked example, not a generic funnel) ----
fig, ax = plt.subplots(figsize=(6.1, 6.4))
ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis('off')
# A generic funnel restates the chapter; instead trace the CANONICAL vague ask
# ("our app is slow") through each gate to a quantified architectural bound.
stages = [
    ('1. What is the true problem?',
     '"our app is slow" \u2192 TTFT p95 2.1 s on a 70B model'),
    ('2. What does success look like?',
     'p95 TTFT \u2264 2 s, ~25 ms/token, 40 rps peak'),
    ('3. What data exists?',
     '9.2K-token prompts; shared prefix (hit rate to benchmark)'),
    ('4. What are the constraints?',
     '8\u00d7H100 host, ~$14.6K/mo, no SLO headroom'),
    ('5. What is in scope now?',
     'KV precision FP16\u2192FP8 + prefix cache + routing'),
]
for i, (q, a) in enumerate(stages):
    w = 8.6 - i*0.55
    y = 8.6 - i*1.35
    ax.add_patch(FancyBboxPatch(((10-w)/2, y), w, 1.08, boxstyle='round,pad=0.02', fc='#f0b35f', ec='#c07a2a'))
    ax.text(5, y+0.80, q, ha='center', va='center', fontsize=9.5, fontweight='bold', color='#4a2f10')
    ax.text(5, y+0.34, a, ha='center', va='center', fontsize=8.5, color='#5a3a14')
    if i < len(stages)-1:
        # connector: an explicit line spanning the FULL gap (box i bottom y-0.02
        # -> box i+1 top y-0.25) plus a small arrowhead at the bottom.  R27 P2:
        # the old annotate arrow rendered as a bare floating triangle (its head was
        # larger than the ~10pt gap and its length was inconsistent).  An explicit
        # line guarantees the connector touches both box edges.
        ax.plot([5, 5], [y-0.02, y-0.25], color='#a05a1a', lw=2.4, zorder=3)
        ax.annotate('', xy=(5, y-0.25), xytext=(5, y-0.16),
                    arrowprops=dict(arrowstyle='-|>', lw=2.4, color='#a05a1a', mutation_scale=8))
# outcome (narrower than the top box so the funnel silhouette holds: the quantified
# bound is the narrow, specific result of the five widening questions)
ax.add_patch(FancyBboxPatch((1.7, 1.13), 6.6, 1.15, boxstyle='round,pad=0.02', fc='#6f9e5f', ec='#3d5a2f'))
ax.text(5, 1.71, 'Quantified bounds: TTFT / throughput / cost', ha='center', va='center',
        color='white', fontsize=8.5, fontweight='bold')
ax.annotate('', xy=(5, 2.30), xytext=(5, 3.18),
            arrowprops=dict(arrowstyle='-|>', lw=1.6, color='#3d5a2f', mutation_scale=13))
ax.text(5, 9.85, 'From a vague ask to architectural bounds (worked example)', fontsize=11.6, fontweight='bold', ha='center', color='#1a1a1a')
plt.tight_layout()
plt.savefig(base % (23, 23, 23), dpi=350)
plt.savefig((base % (23, 23, 23)).replace('.png', '.pdf'), format='pdf')
plt.close()
print('Ch23 done')

# ---- Ch25: anatomy of an ADR ----
# RETIRED: this block drew the OLD five fields (Context/Options/Decision/Rationale/
# Consequences), which conflict with the copy-ready template's core fields (C-20).
# The canonical generator is render/fig_ch25_adr.py, now drawing the five CORE fields
# in §25.1 order (Title & status / Context / Decision / Consequences / Alternatives).
# Do NOT regenerate fig-25-2501 from this batch.
print('Ch25: see render/fig_ch25_adr.py (stale batch block retired)')

print('batch part 2 complete')
