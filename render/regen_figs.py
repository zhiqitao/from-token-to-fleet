"""Regenerate all chapter figures as BOTH bitmap PNG (HTML) and vector PDF (LaTeX).

Strategy: monkeypatch matplotlib.pyplot.savefig so that every existing
`plt.savefig('...png', dpi=...)` call writes the PNG as-is AND a sibling
vector .pdf (matplotlib's 'pdf' backend, which ignores dpi).  This lets us
reuse the 11 existing fig_*.py scripts verbatim, without editing 36 call
sites.  The LaTeX pipeline then includes the vector .pdf, shrinking the
final book PDF and keeping figures crisp at any zoom.

Run from the repo root:
    python3 render/regen_figs.py
"""
import glob
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG_SCRIPTS = sorted(glob.glob(os.path.join(REPO, "render", "fig_*.py")))

_orig_savefig = plt.savefig

# The book's text column is ~6.1in but every figure is authored at 8-16in wide,
# then clamped to \textwidth, so the fonts shrink proportionally and become
# unreadable in print (~0.4-0.6x of nominal).  Scale every figure's type back up
# by (figure width in inches / 6.1) so text lands at its nominal point size on
# the page.  Preserves relative sizes (titles remain larger than labels).
TEXTW_IN = 6.1
_scaled_fignums = set()   # reset per script so each figure is scaled once


def _scale_figure_fonts(fig, num):
    """Multiply all text font sizes in a figure by figwidth/TEXTW_IN (once)."""
    if num in _scaled_fignums:
        return
    _scaled_fignums.add(num)
    try:
        factor = fig.get_size_inches()[0] / TEXTW_IN
    except Exception:
        return
    if factor <= 1.05:      # near or below column width: leave alone
        return
    # Axis-off text-art diagrams draw boxes/labels at fixed data coordinates, so
    # enlarging the fonts clips labels at the boxes/canvas edges.  Leave these
    # figures alone: their internal proportions are authored to fit, and clamping
    # to the column already shrinks everything together without clipping.
    text_art = all(not ax.get_xaxis().get_visible() and not ax.get_yaxis().get_visible()
                   for ax in fig.axes) and any(ax.patches for ax in fig.axes)
    if text_art:
        return
    # Cap the scale so labels on dense multi-panel charts don't overflow their
    # allotted space (two-line x-tick names especially).  ~1.5x is a good
    # legibility/overflow balance.
    factor = min(factor, 1.5)
    for txt in fig.texts:
        txt.set_fontsize(txt.get_fontsize() * factor)
    for ax in fig.axes:
        if ax.title:
            ax.title.set_fontsize(ax.title.get_fontsize() * factor)
        if ax.xaxis.label:
            ax.xaxis.label.set_fontsize(ax.xaxis.label.get_fontsize() * factor)
        if ax.yaxis.label:
            ax.yaxis.label.set_fontsize(ax.yaxis.label.get_fontsize() * factor)
        for l in ax.xaxis.get_ticklabels():
            l.set_fontsize(l.get_fontsize() * factor)
        for l in ax.yaxis.get_ticklabels():
            l.set_fontsize(l.get_fontsize() * factor)
        leg = ax.get_legend()
        if leg:
            for t in leg.get_texts():
                t.set_fontsize(t.get_fontsize() * factor)
        for t in ax.texts:
            t.set_fontsize(t.get_fontsize() * factor)


def _duo_savefig(fname, *args, **kwargs):
    """Write the original output (PNG), then a sibling vector PDF."""
    # Scale fonts up on every open figure so print-size type is legible.
    text_art_fig = None
    try:
        for num in plt.get_fignums():
            fig = plt.figure(num)
            _scale_figure_fonts(fig, num)
            # For axis-off text-art diagrams (which we don't font-scale), crop
            # their excess whitespace with bbox_inches='tight' so the drawing
            # fills more of the printed column.  Charts with far-off clip_on
            # annotations must NOT use tight bbox (it can balloon the canvas).
            ta = all(not ax.get_xaxis().get_visible() and not ax.get_yaxis().get_visible()
                     for ax in fig.axes) and any(ax.patches for ax in fig.axes)
            if ta:
                text_art_fig = num
    except Exception as e:
        print("  (font-scale skipped:", e, ")")
    # Original call (writes the .png exactly as before)
    kw_save = dict(kwargs)
    if text_art_fig is not None:
        kw_save.setdefault("bbox_inches", "tight")
        kw_save.setdefault("pad_inches", 0.05)
    _orig_savefig(fname, *args, **kw_save)
    if isinstance(fname, str) and fname.lower().endswith(".png"):
        pdf_path = fname[:-4] + ".pdf"
        kw = dict(kwargs)
        kw.pop("dpi", None)  # vector backend ignores dpi
        if text_art_fig is not None:
            kw.setdefault("bbox_inches", "tight")
            kw.setdefault("pad_inches", 0.05)
        _orig_savefig(pdf_path, format="pdf", **kw)
        print("  +vector", pdf_path)


def main():
    plt.savefig = _duo_savefig
    for script in FIG_SCRIPTS:
        name = os.path.basename(script)
        print("==", name)
        _scaled_fignums.clear()  # fresh figure set per script
        src = open(script, encoding="utf-8").read()
        # exec in an isolated namespace; relative paths (design/...) resolve
        # from the repo root (cwd).
        ns = {"__name__": "__main__", "__file__": script}
        try:
            exec(compile(src, script, "exec"), ns)
        except SystemExit:
            # A retired script may call sys.exit(0) to skip itself; since we
            # exec all scripts in ONE interpreter, swallow that so the regen
            # loop (and every later figure script) keeps running.
            continue
    print("DONE")


if __name__ == "__main__":
    main()
