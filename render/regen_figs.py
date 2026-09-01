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


def _duo_savefig(fname, *args, **kwargs):
    """Write the original output (PNG), then a sibling vector PDF."""
    # Original call (writes the .png exactly as before)
    _orig_savefig(fname, *args, **kwargs)
    if isinstance(fname, str) and fname.lower().endswith(".png"):
        pdf_path = fname[:-4] + ".pdf"
        kw = dict(kwargs)
        kw.pop("dpi", None)  # vector backend ignores dpi
        _orig_savefig(pdf_path, format="pdf", **kw)
        print("  +vector", pdf_path)


def main():
    plt.savefig = _duo_savefig
    for script in FIG_SCRIPTS:
        name = os.path.basename(script)
        print("==", name)
        src = open(script, encoding="utf-8").read()
        # exec in an isolated namespace; relative paths (design/...) resolve
        # from the repo root (cwd).
        ns = {"__name__": "__main__", "__file__": script}
        exec(compile(src, script, "exec"), ns)
    print("DONE")


if __name__ == "__main__":
    main()
