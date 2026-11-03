import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# ---- fig-19-1903: state-management POLICY comparison (Ch19 §6) ----
# 2026-11-01 review P2-12: Fig 19.2 and Fig 19.3 used to teach the SAME
# lesson (token/KV accumulation across turns), so 19.3 is recast as the
# distinct half of the pair: 19.2 quantifies the append-only bounding case,
# 19.3 compares the three state-management policies against it.
#
# Three policies, three different QUANTITIES moved:
#   * append-only        -> the footprint itself (24.9 -> 34.0 GB, +36%) [DERIVED]
#   * compaction         -> the footprint (held roughly flat)            [ILLUSTRATIVE]
#   * prefix-cache eviction -> cached-prefix memory + re-prefill; the
#     request's own context/KV is unchanged (still 34.0 GB)              [ILLUSTRATIVE]
#
# Only the append-only bar is derived from Ch 19 arithmetic; the other two
# are qualitative and are labelled as such in the figure, the caption and the
# body text.  The R08/R11 counterfactual column semantics are preserved: each
# bar is a SEPARATE completed request after 4 turns, not an intermediate
# state of one live agent.

rows = [
    # (y, name, value, colour, hatch, edge, value label, sub-line)
    (2, 'Append-only', 34.0, '#c0392b', '..', 'white',
     '34.0 GB',
     '[DERIVED] bounding case — nothing evicted; bounds what the system tolerates'),
    (1, 'Compaction', 24.9, '#6f9e5f', '//', '#1e7a59',
     '≈24.9 GB',
     '[ILLUSTRATIVE] summarize/truncate each turn — moves the footprint itself'),
    (0, 'Prefix-cache eviction', 34.0, '#3a6ea5', 'xx', '#1e3a5f',
     '34.0 GB (unchanged)',
     '[ILLUSTRATIVE] evicts the reusable prefix — moves cache memory and re-prefill'),
]

fig, ax = plt.subplots(figsize=(6.1, 5.2))
fig._hermes_print_sized = True   # regen must not re-boost/reflow

BAR_H = 0.34
for y, name, val, col, hatch, ec, vlab, sub in rows:
    ax.barh(y, val, BAR_H, color=col, hatch=hatch, edgecolor=ec, linewidth=1.0)
    ax.text(val + 0.7, y, vlab, va='center', ha='left', fontsize=8.6,
            fontweight='bold', color=col)
    # Opaque white bbox behind each annotation line so the vertical single-shot
    # dashed reference line (x=24.9), which spans the full plot height, is masked
    # behind the text rather than crossing through it (review: line-over-text).
    ax.text(0.4, y - 0.44, sub, va='center', ha='left', fontsize=8.0, color='#333',
            bbox=dict(boxstyle='round,pad=0.10', fc='white', ec='none', alpha=1.0))

# single-shot reference: the footprint every policy starts from
ax.axvline(24.9, ls='--', lw=1.0, color='#555', zorder=0)
ax.text(25.6, 2.62, 'single-shot 24.9 GB', fontsize=8.2, color='#555',
        ha='left', va='center')

ax.set_xlim(0, 48)
ax.set_ylim(-0.75, 2.85)
ax.set_yticks([r[0] for r in rows])
ax.set_yticklabels([r[1] for r in rows], fontsize=9.0, fontweight='bold')
ax.set_xlabel('FP16 KV / request after four agent turns (GB)', fontsize=9)
ax.set_xticks([0, 10, 20, 30, 40])
ax.tick_params(labelsize=8.6)
ax.grid(axis='x', alpha=0.3)
for sp in ('top', 'right'):
    ax.spines[sp].set_visible(False)

fig.suptitle('State-management policy at turn 4: three policies move three different things',
             fontsize=10.5, fontweight='bold')
fig.text(0.5, 0.925, 'canonical 2.62 MB/token; only the append-only bar is derived',
         ha='center', va='top', fontsize=9.0, color='#333')

# counterfactual column semantics (R08/R11), preserved verbatim in meaning
fig.text(0.5, 0.215,
         'counterfactual: each bar = a separate completed request after 4 turns',
         ha='center', va='center', fontsize=8.4, color='#111')
fig.text(0.5, 0.168,
         '(one final 300-token answer) — not an intermediate state of a live agent.',
         ha='center', va='center', fontsize=8.4, color='#111')
fig.text(0.5, 0.095,
         'append-only total = I₀ + T·δ + T·γ + O_final  @ 2.62 MB/token',
         ha='center', va='center', fontsize=8.4, color='#444')
fig.text(0.5, 0.048,
         '(I₀ = 9.2K input, δ = 800 retrieved, γ = 65 generated, O = 300 output per turn)',
         ha='center', va='center', fontsize=8.4, color='#444')

plt.subplots_adjust(left=0.185, right=0.97, top=0.855, bottom=0.30)

plt.savefig('design/manuscript/chapter-19/figures/fig-19-1903.png',
            dpi=400, bbox_inches='tight', pad_inches=0.08)
import matplotlib as mpl
with mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-19/figures/fig-19-1903.pdf',
                format='pdf', bbox_inches='tight', pad_inches=0.08)
plt.close()
print('wrote fig-19-1903 (policy comparison: append-only vs compaction vs prefix-cache eviction)')