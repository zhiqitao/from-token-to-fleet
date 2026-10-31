#!/usr/bin/env python3
"""Eight-rank ring, directional endpoint bandwidth. Not a benchmark."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'design/manuscript/chapter-09/figures/fig-09-0901'
N = 8
FACTOR = 2 * (N - 1) / N
TIERS = [
    ('H100 NVLink: directional peak 450 GB/s', 450, '#27408b', '-', 'o'),
    ('Two-rail HDR: assumed effective 40 GB/s', 40, '#9a4f00', '--', '^'),
    ('25GbE RoCE: assumed effective 2.5 GB/s', 2.5, '#a02a2a', ':', 's'),
]

def main():
    volume = np.logspace(-2, np.log10(250), 160)
    fig, ax = plt.subplots(figsize=(6.1, 4.9))
    fig._hermes_print_sized = True
    fig.subplots_adjust(left=.16, right=.97, top=.80, bottom=.31)
    for name, bandwidth, color, style, marker in TIERS:
        ax.loglog(volume, 1000 * FACTOR * volume / bandwidth,
                  color=color, ls=style, marker=marker, markevery=24,
                  lw=1.8, markersize=4, label=name)
    ax.axvline(140, color='#666', ls='-.', lw=1)
    for _, bandwidth, color, _, _ in TIERS:
        ax.plot(140, 1000 * FACTOR * 140 / bandwidth, marker='o',
                color=color, markersize=5)
    ax.set_xlim(.01, 250)
    ax.set_ylim(.02, 250000)
    ax.set_xticks([.01, .1, 1, 10, 140])
    ax.set_xticklabels(['0.01', '0.1', '1', '10', '140'])
    ax.set_yticks([.1, 1, 10, 100, 1000, 10000, 100000])
    ax.set_yticklabels(['0.1', '1', '10', '100', '1000', '10000', '100000'])
    ax.tick_params(labelsize=9)
    ax.set_xlabel('Logical input tensor per rank (GB)', fontsize=9.5)
    ax.set_ylabel('Ideal ring completion time (ms)', fontsize=9.5)
    ax.grid(which='major', alpha=.3)
    fig.text(.5, .95, 'Ring traffic and directional bandwidth',
             ha='center', fontsize=12, weight='bold')
    fig.text(.5, .895, 'N = 8; sent bytes per rank = 1.75 × tensor bytes',
             ha='center', fontsize=9.5)
    fig.text(.5, .85, '140 GB: NVLink 544 ms | HDR 6,125 ms | RoCE 98,000 ms',
             ha='center', fontsize=9)
    fig.legend(*ax.get_legend_handles_labels(), loc='lower center',
               bbox_to_anchor=(.5, .055), fontsize=9, frameon=False)
    fig.text(.5, .025, 'Analytical model; no offload, latency or overlap; not measured',
             ha='center', fontsize=9)
    assert FACTOR * 140 == 245
    assert abs(245 / 450 - 490 / 900) < 1e-12
    assert abs(245 / 40 - 6.125) < 1e-12
    assert 245 / 2.5 == 98
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT.with_suffix('.png'), dpi=400)
    with matplotlib.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
        fig.savefig(OUT.with_suffix('.pdf'))
    plt.close(fig)
    print('PASS directional arithmetic; PNG + Type42 PDF:', OUT)

if __name__ == '__main__':
    main()
