#!/usr/bin/env python3
"""emit_book.py -- generate the master book.tex from book.yaml + converted chapters.

Produces render/latex/book.tex: frontmatter (title page, preface, TOC),
mainmatter (6 parts, 27 chapters), backmatter.
"""
import os, re, glob, datetime

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LATEX = os.path.join(REPO, "render", "latex")

# Version = date stamp (YYYYMMDD), e.g. 20260830. Deliberately NOT a semantic
# 0.01-style number -- each dated build is its own identifiable snapshot.
VERSION = datetime.date.today().strftime("%Y%m%d")
# Deterministic slug shared by every deliverable so the file name means
# something: from-token-to-fleet-v20260830.pdf
BOOK_SLUG = "from-token-to-fleet"
OUT_STEM = f"{BOOK_SLUG}-v{VERSION}"


def read_parts():
    text = open(os.path.join(REPO, "design", "book.yaml"), encoding="utf-8").read()
    parts = []
    chapters = {}
    cur = None
    for line in text.splitlines():
        m = re.match(r"\s+- id: (\w+)", line)
        if m:
            cur = {"id": m.group(1), "chapters": []}
            parts.append(cur)
            continue
        m = re.match(r"\s+title: \"(.+?)\"", line)
        if m and cur is not None and "title" not in cur:
            cur["title"] = m.group(1)
            continue
        m = re.match(r"\s+- \{n: (\d+), title: \"(.+?)\", status: \"(\w+)\"\}", line)
        if m and cur is not None:
            n = int(m.group(1))
            chapters[n] = m.group(2)
            cur["chapters"].append(n)
    return parts, chapters


def clean_chapter_title(n):
    """Return the chapter's display title (drop 'Chapter N —' prefix from md H1)."""
    md = open(os.path.join(REPO, f"design/manuscript/chapter-{n:02d}/chapter-{n:02d}.md"),
              encoding="utf-8").read()
    h1 = None
    for line in md.split("\n"):
        if line.startswith("# "):
            h1 = line[2:].strip()
            break
    if h1:
        # strip leading 'Chapter N' / 'Chapter N —' / 'Chapter N:'
        h1 = re.sub(r"^Chapter\s+\d+\s*[—:]?\s*", "", h1)
    return h1


def tex_escape(s):
    return (s.replace("&", "\\&").replace("%", "\\%")
             .replace("#", "\\#").replace("_", "\\_")
             .replace("~", "\\textasciitilde{}").replace("^", "\\textasciicircum{}"))

def make_titlepage():
    """Return the title-page LaTeX block: title, subtitle, version, and the
    author's one-line frame (a learning tool written for myself)."""
    lines = []
    lines.append(r"\begin{titlepage}")
    lines.append(r"\thispagestyle{empty}")
    lines.append(r"\centering")
    lines.append(r"\vspace*{3cm}")
    lines.append(r"{\Huge\bfseries From Token to Fleet\par}")
    lines.append(r"\vspace{1.5cm}")
    lines.append(r"{\Large\itshape An AI Solution Architect's Handbook\par}")
    lines.append(r"\vspace{0.8cm}")
    lines.append(r"{\normalsize Version %s\par}" % VERSION)
    lines.append(r"\vfill")
    lines.append(r"{\large Zhiqi Tao\par}")
    lines.append(r"\vspace{0.8cm}")
    lines.append(r"{\small\itshape First and foremost a learning tool I wrote for myself --- if it helps you too, that is a bonus, above and beyond what I set out to do.\par}")
    lines.append(r"\vfill")
    lines.append(r"\end{titlepage}")
    return "\n".join(lines)


def make_copyrightpage():
    """Return the copyright / license page (the page facing the title page).
    This is the standard book-convention location for the legal notice. It
    restates the source-available license in plain language and points to the
    full terms in the repository's LICENSE file."""
    lines = []
    lines.append(r"\begin{titlepage}")
    lines.append(r"\thispagestyle{empty}")
    lines.append(r"{\centering\MakeUppercase{Copyright \textcopyright{} 2026 Zhiqi Tao}\\[2pt] All rights reserved.\par}")
    lines.append(r"\vspace{1.2cm}")
    lines.append(r"\noindent\textbf{License.} This work --- the book text, diagrams, figures, and build scripts --- is distributed under a \emph{source-available} license.")
    lines.append("")
    lines.append(r"\begin{itemize}")
    lines.append(r"\item \textbf{\color{memory}You may} freely read, study, learn from, and \textbf{redistribute} the work (verbatim, with attribution) for personal and non-commercial ends --- no permission needed.")
    lines.append(r"\item \textbf{\color{compute}Commercial use or publication} --- a paid product, course, book, or report --- requires the author's \textbf{prior written approval}.")
    lines.append(r"\end{itemize}")
    lines.append("")
    lines.append(r"\noindent To request commercial permission, contact \texttt{zhiqi.tao@gmail.com}.")
    lines.append("")
    lines.append(r"\noindent Full terms: \texttt{github.com/zhiqitao/from-token-to-fleet}\\ (\texttt{LICENSE}, SPDX \texttt{LicenseRef-ZhiqiResearch-FromTokenToFleet-1.0})")
    lines.append(r"\vfill")
    lines.append(r"\noindent\footnotesize The work is provided ``as is'', without warranty of any kind.")
    lines.append(r"\end{titlepage}")
    return "\n".join(lines)



def emit_book():
    parts, chapters = read_parts()
    lines = []
    lines.append("% Auto-generated by render/latex/emit_book.py — do not edit by hand")
    lines.append(r"\documentclass[letterpaper,11pt,openany]{book}")
    lines.append(r"\usepackage{book}")
    lines.append(r"\begin{document}")
    lines.append("")
    # title (custom typeset inline; \title/\subtitle/\maketitle are NOT used
    # because the custom \subtitle macro would typeset content immediately)
    lines.append("")
    lines.append(make_titlepage())
    lines.append("")
    # Copyright / license notice, on the page facing the title page (the
    # standard book-convention location). Restates the source-available license
    # and points to the full terms in the repo's LICENSE file.
    lines.append(make_copyrightpage())
    lines.append("")
    lines.append(r"\frontmatter")
    lines.append("")
    # Preface comes right after the title page, before the table of contents
    # (the reader meets the author's why before the map).
    lines.append(r"\chapter{Preface}")
    lines.append(r"\input{preface}")
    lines.append("")
    # The table of contents must start on a fresh page, not share the last
    # page of the preface (LaTeX's \tableofcontents does not force a break).
    lines.append(r"\clearpage")
    lines.append(r"\tableofcontents")
    lines.append("")
    # List of Figures: the figures use proper LaTeX figure environments with
    # captions, so \listoffigures collects them automatically and acts as a
    # quick-reference index for the architect (Qwen visual review checklist #4).
    lines.append(r"\clearpage")
    lines.append(r"\listoffigures")
    lines.append("")
    lines.append(r"\mainmatter")
    lines.append("")
    # Parts with chapters
    for p in parts:
        lines.append(r"\part{%s}" % tex_escape(p["title"]))
        for n in p["chapters"]:
            if n == 27:  # appendix emitted separately under \appendix
                continue
            title = clean_chapter_title(n) or chapters.get(n, f"Chapter {n}")
            lines.append(r"\chapter{%s}" % tex_escape(title))
            lines.append(r"\label{chap:%d}" % n)
            lines.append(r"\input{chapters/ch%02d}" % n)
        lines.append("")
    # Appendix
    lines.append(r"\appendix")
    title = clean_chapter_title(27) or chapters.get(27, "Appendix A")
    lines.append(r"\chapter{%s}" % tex_escape(title))
    lines.append(r"\label{chap:27}")
    lines.append(r"\input{chapters/ch27}")
    lines.append("")
    lines.append(r"\backmatter")
    lines.append("")
    lines.append(r"\end{document}")
    return "\n".join(lines)


if __name__ == "__main__":
    out = emit_book()
    path = os.path.join(LATEX, "book.tex")
    open(path, "w", encoding="utf-8").write(out)
    print("wrote", path, len(out), "chars")
