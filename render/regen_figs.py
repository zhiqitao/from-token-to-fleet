#!/usr/bin/env python3
"""Regenerate all chapter figures as BOTH bitmap PNG (HTML) and vector PDF (LaTeX).

Strategy: monkeypatch matplotlib.pyplot.savefig so that every existing
`plt.savefig('...png', dpi=...)` call writes the PNG as-is AND a sibling
vector .pdf (matplotlib's 'pdf' backend, which ignores dpi).  This lets us
reuse the existing fig_*.py scripts without editing every call site.

Print-typography fixes applied to EVERY figure at save time:
  * The book places figures at ~6.1in column width, but figures are authored at
    8-16in wide, so every font is downscaled to ~0.4-0.6x and becomes
    unreadable in print.  We scale fonts up to a TARGET final print size (so the
    smallest label lands near body size), then reflow the axes (tight_layout)
    so the enlarged labels don't clip against panel edges.
  * Axis-off text-art diagrams draw boxes/labels at fixed data coordinates, so
    we scale the text AND the patch geometry together (boxes grow to hold the
    larger text) and crop the canvas tightly so the diagram fills the column.
"""

import glob
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG_SCRIPTS = sorted(glob.glob(os.path.join(REPO, "render", "fig_*.py")))

# The book's print text column (inches).  Figures are clamped to this width.
TEXTW_IN = 6.1
# Desired minimum final print font size (points) for figure labels.
TARGET_SIZE_PT = 8.5
# Absolute cap so we never balloon a figure's type into absurdity.
# Wide text-art diagrams (decision loop, memory allocation, parallelism, etc.)
# are placed at downscale > 1 (figure wider than the 6.1in column), which used
# to clamp their scale factor below the on-page 8.5pt target (base fonts ended
# up ~7.2-7.34pt on page).  Raise the cap so those wide diagrams can reach the
# legibility target instead of being under-scaled.
MAX_SCALE = 6.0

_scaled_fignums = set()   # object-ids of figures already scaled (per script)

_orig_savefig = plt.savefig


def _is_text_art(fig):
    """An 'axis-off' diagram: no visible axes AND drawn patches.

    `ax.axis('off')` sets `ax.axison=False` (it does NOT flip
    `get_xaxis().get_visible()`), so detect via `get_axison()` -- and also treat
    an axes whose tick labels are all hidden as axis-off.  A real chart keeps
    at least one visible axis."
    """
    if not fig.axes:
        return False
    for ax in fig.axes:
        # `ax.axis('off')` flips the `axison` flag.  A real chart keeps it True.
        if getattr(ax, "axison", True):
            return False        # an axis is on -> real chart
    return any(getattr(ax, "patches", None) for ax in fig.axes)


def _all_text_sizes(fig):
    """Collect every text font size in the figure."""
    sizes = []
    def add(t):
        if t is not None:
            try:
                sizes.append(t.get_fontsize())
            except Exception:
                pass
    for t in fig.texts:
        add(t)
    for ax in fig.axes:
        add(ax.title)
        add(ax.xaxis.label); add(ax.yaxis.label)
        for l in ax.xaxis.get_ticklabels():
            add(l)
        for l in ax.yaxis.get_ticklabels():
            add(l)
        for t in ax.texts:
            add(t)
        leg = ax.get_legend()
        if leg:
            for t in leg.get_texts():
                add(t)
    return sizes


def _scale_axes_fonts(ax, factor):
    def s(t):
        if t is not None:
            t.set_fontsize(t.get_fontsize() * factor)
    s(ax.title)
    s(ax.xaxis.label); s(ax.yaxis.label)
    for l in ax.xaxis.get_ticklabels():
        l.set_fontsize(l.get_fontsize() * factor)
    for l in ax.yaxis.get_ticklabels():
        l.set_fontsize(l.get_fontsize() * factor)
    for t in ax.texts:
        t.set_fontsize(t.get_fontsize() * factor)
    leg = ax.get_legend()
    if leg:
        for t in leg.get_texts():
            t.set_fontsize(t.get_fontsize() * factor)


def _fix_crowded_chart(fig):
    """For chart figures, relieve the common 'labels collide' failure modes:
    - Long/multi-line x-tick labels in narrow panels -> rotate ~35deg right-
      aligned so adjacent labels don't overlap horizontally.
    - Legends sitting inside a dense plot -> move outside/clear area and shrink.
    This is the class of defect Astra flagged on many multi-panel charts."""
    for ax in fig.axes:
        try:
            labels = [t.get_text() for t in ax.get_xticklabels()]
            longest = max((len(s) for s in labels), default=0)
            # Long categorical labels (candidate names, model names, etc.)
            # overrun narrow panels once fonts grow.  Only rotate when there
            # are enough labels that horizontal spacing is genuinely tight
            # (>=4 ticks); with just 2-3 short-ish candidates across the full
            # column width they fit horizontally and rotation wastes space.
            if longest > 10 and len(labels) >= 4:
                for t in ax.get_xticklabels():
                    t.set_rotation(35)
                    t.set_ha("right")
                    t.set_rotation_mode("anchor")
        except Exception:
            pass
        try:
            leg = ax.get_legend()
            if leg:
                # If the legend overlaps the plot's data box, move it to a
                # clearer location (below/outside) and keep it small.
                bb = leg.get_window_extent()
                axbb = ax.get_window_extent()
                inside = (axbb.x0 <= bb.x1 <= axbb.x1 and
                          axbb.y0 <= bb.y1 <= axbb.y1)
                if inside and len(leg.get_texts()) >= 2:
                    leg.set_loc("upper left")
                    leg.set_framealpha(0.9)
        except Exception:
            pass


def _scale_text_art(fig, factor):
    """For axis-off diagrams, grow the FONT so labels reach ~body size at print.

    We deliberately do NOT scale the patch geometry: scaling box coords about the
    axes centre pushes edge boxes past the axes boundary (they get clipped by the
    tight-crop) and desyncs the connector arrows, which are anchored at fixed
    data coordinates.  The boxes are authored with enough slack that the bigger
    font still fits inside them; any genuinely too-small box is fixed in its
    own generator.
    """
    for ax in fig.axes:
        for t in ax.texts:
            t.set_fontsize(t.get_fontsize() * factor)
        for t in ax.xaxis.get_ticklabels():
            t.set_fontsize(t.get_fontsize() * factor)
        for t in ax.yaxis.get_ticklabels():
            t.set_fontsize(t.get_fontsize() * factor)
        try:
            if ax.get_title():
                ax.title.set_fontsize(ax.title.get_fontsize() * factor)
            ax.xaxis.label.set_fontsize(ax.xaxis.label.get_fontsize() * factor)
            ax.yaxis.label.set_fontsize(ax.yaxis.label.get_fontsize() * factor)
        except Exception:
            pass
    for t in fig.texts:
        t.set_fontsize(t.get_fontsize() * factor)


def _scale_figure_fonts(fig, num):
    """Scale fonts up so the smallest label reaches roughly body size at print,
    then reflow; for text-art diagrams scale the geometry too."""
    # Print-size-authored figures (author at 6.1in with their own font sizes)
    # must NOT be re-boosted: boosting fixed boxes clips their labels.
    if getattr(fig, '_hermes_print_sized', False):
        return
    key = id(fig)          # key by object identity, not figure number: in
    if key in _scaled_fignums:   # multi-figure scripts the same number is
        return                    # reused across subplots() calls.
    _scaled_fignums.add(key)
    try:
        width_in = fig.get_size_inches()[0]
    except Exception:
        return
    if width_in <= 1.05:
        return

    # Do NOT scale charts that already land near print size.
    # Reduce figsize to 6.1in so it's placed ~1:1 and fonts are already nominal.
    # We keep the original figsize for the data layout, but we will downscale
    # the SAVED image to the column width via the LaTeX \maxwidth clamp, so the
    # effective on-page factor is (TEXTW_IN / width_in) * scale.
    # For text-art we must use the *tight-cropped* content width (not the raw
    # figsize, which is much wider because of padding), otherwise we badly
    # underestimate the downscale and under-scale the fonts.
    downscale = width_in / TEXTW_IN     # >1 => figure is wider than column
    if _is_text_art(fig):
        try:
            fig.canvas.draw()
            ren = fig.canvas.get_renderer()
            tb = fig.get_tightbbox(ren)
            content_w_in = (tb.x1 - tb.x0) / 72.0  # pt -> in
            if content_w_in > 0.5:
                downscale = content_w_in / TEXTW_IN
        except Exception:
            pass

    sizes = _all_text_sizes(fig)
    if not sizes:
        return
    # Current smallest label on-page (approx) = smallest * (TEXTW_IN / width_in).
    smallest = min(sizes)
    on_page = smallest / downscale
    factor = TARGET_SIZE_PT / on_page if on_page > 0 else 1.0
    factor = max(1.0, min(factor, MAX_SCALE / max(1.0, downscale)))

    if _is_text_art(fig):
        # Text-art: scale fonts + geometry together (boxes grow), then the
        # canvas is tight-cropped so the diagram fills the column.
        _scale_text_art(fig, factor)
    else:
        # Chart: enlarge fonts, and grow the figure HEIGHT so multi-line axis
        # labels / legends have room (a wide-short figure clips them); then
        # reflow the axes so labels stay inside panels.
        for t in fig.texts:
            t.set_fontsize(t.get_fontsize() * factor)
        for ax in fig.axes:
            _scale_axes_fonts(ax, factor)
        try:
            w, h = fig.get_size_inches()
            # Give wide-short subplot (multi-axes) figures more height so the
            # enlarged bottom/multi-line labels fit after reflow; single-axis
            # charts (the common case) are NOT stretched -- they stay at their
            # authored aspect so they don't turn into a tall sliver.  Cap so the
            # placed figure stays within a book page.
            if len(fig.axes) > 1 and w > h:
                hscale = min(factor, 1.7)
                fig.set_size_inches(w, h * hscale)
        except Exception:
            pass
        try:
            fig.tight_layout(pad=1.5)
        except Exception:
            try:
                fig.set_layout_engine("constrained")
            except Exception:
                pass
        # Rotate long x-labels, clear legends, then reflow once more.
        _fix_crowded_chart(fig)
        try:
            fig.tight_layout(pad=1.5)
        except Exception:
            pass


def _duo_savefig(fname, *args, **kwargs):
    """Write the original output (PNG), then a sibling vector PDF.

    Always save with bbox_inches='tight' so no figure clips its own title,
    tick labels, or edge annotations at the print column (~6.1in).  This fixes
    the class of defects where wide figures overflowed the trim and truncated
    their titles / axis labels (publication review 2026-09-16)."""
    text_art_save = False
    try:
        for num in plt.get_fignums():
            fig = plt.figure(num)
            # Some figures are authored at their final on-page size with boxes
            # auto-sized to their labels (fig_ch18_routing).  Re-boosting their
            # fonts into those fixed boxes clips the text, so skip any figure
            # whose title marks it as print-size-authored.
            title = ""
            try:
                for a in fig.axes:
                    if a.get_title():
                        title += a.get_title()
            except Exception:
                pass
            if "sequential cascade" in title and "specialised model" in title:
                text_art_save = _is_text_art(fig)
            else:
                _scale_figure_fonts(fig, num)
                if _is_text_art(fig):
                    text_art_save = True
    except Exception as e:
        print("  (font-scale skipped:", e, ")")

    kw = dict(kwargs)
    # `_hermes_print_sized` figures are authored at their exact on-page size (6.1in
    # column) with content already inside the axes.  Forcing bbox_inches='tight'
    # expands them to the content bbox (e.g. 6.1 -> 7.0/9.7in), so the book places
    # them at the column width and downscales, shrinking on-page fonts (the
    # font-bump paradox in reverse).  Save print-sized figures at their authored
    # size (no tight bbox) so they place 1:1.
    is_print_sized = any(getattr(plt.figure(n), "_hermes_print_sized", False)
                         for n in plt.get_fignums())
    if is_print_sized:
        kw.pop("bbox_inches", None)
        kw.pop("pad_inches", None)
    else:
        kw.setdefault("bbox_inches", "tight")
        kw.setdefault("pad_inches", 0.08)
    _orig_savefig(fname, *args, **kw)
    if isinstance(fname, str) and fname.lower().endswith(".png"):
        pdf_path = fname[:-4] + ".pdf"
        kwo = dict(kwargs)
        kwo.pop("dpi", None)
        if is_print_sized:
            kwo.pop("bbox_inches", None)
            kwo.pop("pad_inches", None)
        else:
            kwo.setdefault("bbox_inches", "tight")
            kwo.setdefault("pad_inches", 0.08)
        # Embed fonts as TrueType (Type 42) instead of Type 3 so the PDF is
        # accessible / searchable and Type-3 warnings are gone.
        with matplotlib.rc_context({
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }):
            _orig_savefig(pdf_path, format="pdf", **kwo)
        print("  +vector", pdf_path)


def main():
    plt.savefig = _duo_savefig
    for script in FIG_SCRIPTS:
        name = os.path.basename(script)
        print("==", name)
        _scaled_fignums.clear()  # fresh figure set per script
        src = open(script, encoding="utf-8").read()
        ns = {"__name__": "__main__", "__file__": script}
        try:
            exec(compile(src, script, "exec"), ns)
        except SystemExit:
            # A retired script may call sys.exit(0) to skip itself; since we
            # exec all scripts in ONE interpreter, swallow that so the regen
            # loop (and every later figure script) keeps running.
            continue
        finally:
            # Each figure script is standalone; close every figure it opened so
            # stale figures from prior scripts can't leak into the next
            # script's _duo_savefig (which scales + tight-crops every open fig).
            plt.close("all")
    print("DONE")


if __name__ == "__main__":
    main()
