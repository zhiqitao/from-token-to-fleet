#!/usr/bin/env python3
"""emit_book.py -- generate the master book.tex from book.yaml + converted chapters.

Produces render/latex/book.tex: frontmatter (title page, preface, TOC),
mainmatter (6 parts, 27 chapters), backmatter.
"""
import os, re, glob, datetime

# Build mode: "tagged" (default, PDF/UA accessibility tree) or "plain"
# (smaller, non-tagged).  Set via the BOOK_BUILD_MODE env var.
BUILD_MODE = os.environ.get("BOOK_BUILD_MODE", "tagged").lower()
PLAIN = BUILD_MODE != "tagged"

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
    lines.append(r"{\Large\itshape An AI Solution Architect’s Handbook\par}")
    lines.append(r"\vspace{0.8cm}")
    lines.append(r"{\normalsize First edition, 2026\par}")
    lines.append(r"\vfill")
    lines.append(r"{\large Zhiqi Tao\par}")
    lines.append(r"\vspace{0.8cm}")
    lines.append(r"{\small\itshape From a single token’s cost to the fleet that carries it, every architectural decision can be traced — and defended — with arithmetic.\par}")
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
    # The legal block below must fit one page (R5-004: a spilling one-line
    # warranty printed "ii" inside roman front matter).  Two extra baselines of
    # text height absorb the edition/licence wording without touching the page
    # geometry elsewhere in the book.
    lines.append(r"\enlargethispage{2\baselineskip}")
    lines.append(r"{\centering\MakeUppercase{Copyright \textcopyright{} 2026 Zhiqi Tao}\\[2pt] All rights reserved, except as explicitly granted below.\par}")
    # R5-004 follow-on: the page must stay a single page.  It previously spilled
    # the one-line warranty onto a second page (which printed "2", an arabic
    # number inside roman front matter).  The legal block is therefore set in
    # \small (conventional for a copyright page) inside its own group, with the
    # heading gap reclaimed, so the added edition/licence wording cannot push
    # the warranty onto a verso.
    lines.append(r"\vspace{0.25cm}")
    lines.append(r"{\small")
    lines.append(r"\noindent\textbf{License.} This work --- the book text, diagrams, figures, and build scripts --- is distributed under the \emph{source-available} grant stated below. That grant is the operative license for this edition: the default is all rights reserved, and the two permissions below are the stated exception. The full text of the license, including the redistribution restrictions and the channel-specific terms (e.g.\ Amazon KDP), is the \texttt{LICENSE} file in the repository, which is the authoritative statement of rights for this work. The two bullets are a plain-language summary, not the license text; they are not operative in their own right, and the \texttt{LICENSE} file at the pinned commit below governs wherever the two differ.")
    lines.append("")
    lines.append(r"\begin{itemize}")
    lines.append(r"\item \textbf{\color{memory}You may} freely read, study, learn from, and \textbf{redistribute} the work (verbatim, with attribution) for personal and non-commercial ends --- no permission needed.")
    lines.append(r"\item \textbf{\color{compute}Commercial use or publication} --- a paid product, course, book, or report --- requires the author's \textbf{prior written approval}.")
    lines.append(r"\end{itemize}")
    lines.append("")
    lines.append(r"\noindent To request commercial permission, contact \texttt{zhiqi.tao@gmail.com}.")
    lines.append("")
    # Round-5 finding R5-003: the "Edition source revision." run-in heading was
    # stretched across a line (huge interword gaps) and the SPDX identifier was
    # split as "LicenseRef- / ZhiqiResearch...".  Cause: a 40-character commit
    # hash is unbreakable, so LaTeX justified the short line before it to full
    # measure.  Fix: set this reference block ragged-right (no justification
    # stretch is possible) and \mbox the SPDX identifier so it never breaks.
    lines.append(r"{\raggedright")
    # R6 LICENSE-LINK-001: the visible link text previously showed only the
    # repository root while the prose promised a direct link to the pinned
    # LICENSE file.  Print the pinned path in the link text so the visible URL
    # and the sentence agree.
    lines.append(r"\noindent\textbf{SPDX identifier:} \mbox{\texttt{LicenseRef-ZhiqiResearch-FromTokenToFleet-1.0}}. The identifier is a custom \texttt{LicenseRef}, not an OSI-approved standard licence: this work's terms are its own, and no standard-licence text can be substituted for them.\par")
    lines.append(r"\noindent\textbf{Full terms:} \href{https://github.com/zhiqitao/from-token-to-fleet/blob/27f4cd571d53ecb2ac549d5825a77c87f8736ad3/LICENSE}{\texttt{https://github.com/zhiqitao/from-token-to-fleet/blob/27f4cd5/LICENSE}}")
    lines.append("")
    lines.append(r"\noindent\textbf{Edition source revision.}\ This edition is built from commit \mbox{\texttt{27f4cd571d53ecb2ac549d5825a77c87f8736ad3}} (short \texttt{27f4cd5}) of the repository. The link above resolves that commit's \texttt{LICENSE} file directly, so the terms quoted here can be read in their exact published form without locating the revision elsewhere (raw file: \href{https://raw.githubusercontent.com/zhiqitao/from-token-to-fleet/27f4cd571d53ecb2ac549d5825a77c87f8736ad3/LICENSE}{\texttt{https://raw.githubusercontent.com/zhiqitao/from-token-to-fleet/27f4cd5/LICENSE}}).\par}")
    lines.append("")
    lines.append(r"\noindent\textbf{Edition identification.} First edition, 2026 --- build identifier \texttt{v20260913}; single evidence cutoff \textbf{2026-08-30}. Both identifiers are restated in the Preface and the Edition-history panel of the Sources, Method, and Reproducibility chapter.")
    lines.append("")
    lines.append(r"\noindent\textbf{Applicable terms and edition.} The SPDX identifier above names the licence version this edition is published under, and the commit above is the immutable source revision that carries it; together they identify the terms for online verification. The operative licence text is \emph{not} reproduced in this artifact --- the paragraphs above are a plain-language summary --- so a reader holding only this file must retrieve the grant from the pinned commit.")
    lines.append("")
    lines.append(r"\noindent\textbf{Technical disclaimer.} This book describes an evolving field. Model names, parameter counts, prices, context limits, throughput and latency figures, licences, and benchmark results change quickly and differ by region, hardware SKU, precision and sparsity, batch size, software stack, and measurement method. Every quantitative value here carries explicit evidence labels on the book's three axes --- provenance (where the number came from), epistemic status (what was done to it: FACT, DERIVED, ASSUMPTION, HYPOTHESIS, or UNRESOLVED), and an optional measurement status (ANALYTICAL, SCENARIO-DERIVED, MODELED, MEASURED, or UNMEASURED). The axes and the full label set are defined in the Preface, and the labels are catalogued in the Sources, Method, and Reproducibility chapter. Each value is a snapshot as of the evidence cutoff recorded above, and must be re-verified against the vendor's current documentation before any procurement or deployment decision.")
    lines.append("")
    lines.append(r"\noindent\footnotesize \textbf{Currency.} Technical content is current as of the dated build; the fastest-moving claims (Appendix A and the economics chapters) are flagged in-text as items that require re-checking against current vendor documentation.")
    lines.append(r"\vfill")
    lines.append(r"\noindent\footnotesize The work is provided ``as is'', without warranty of any kind.")
    lines.append(r"}")
    lines.append(r"\end{titlepage}")
    return "\n".join(lines)



def _lot_short_title(raw):
    """Short title for the List of Tables: the caption's leading phrase, with
    the long qualifier clauses trimmed.  Hand-tuned overrides sit below so the
    index stays readable where a caption is itself a paragraph."""
    OVERRIDES = {
        "7-1": "KV cache size per token and per-context arithmetic (canonical 80-layer, full-MHA 70B, FP16)",
        "7-2": "Memory floors by regime: inference and fine-tuning",
        "8-1": "Per-token FLOP cost, prefill PFLOP, and derived prefill and roofline rates",
        "12-1": "Candidate architectures scored against the three gates",
        "16-1": "TCO comparison across delivery modes",
        "16-2": "Availability-scope reconciliation and remaining gaps",
        "17-1": "Provisioning policy: symbols, canonical values, and independent factors",
        "17-2": "Fleet sizing matrix: KV-residency ceiling and minimum hosts",
    }
    return OVERRIDES.get(raw)


def table_catalogue():
    """Return [(printed_id, label, title)] for every numbered table that has a
    printed ID in the manuscript, in document order.

    The manuscript captions a table either as a heading ('#### Table 4-1 — T')
    or as a bold run-in ('**Table 4-1 — T**', '**Table 4-1** — T'); both forms
    are matched here.  Only tables whose LaTeX \\label exists are emitted, so a
    caption without a labelled longtable can never produce a '??' page number.
    """
    labels = set()
    for tex in sorted(glob.glob(os.path.join(LATEX, "chapters", "ch*.tex"))):
        labels.update(re.findall(r"\\label\{tab:([^}]+)\}",
                                 open(tex, encoding="utf-8").read()))
    pats = [
        r"^#{2,5}\s+Table\s+(\d+)-(\d+)\s*[—]\s*(.+)$",
        r"^\*\*Table\s+(\d+)-(\d+)\s*[—]\s*(.+)$",
        r"^\*\*Table\s+(\d+)-(\d+)\*\*\s*[—]\s*(.+)$",
        r"^\*Table\s+(\d+)-(\d+)\s*[—]\s*(.+)$",
        r"^:\s*\*\*Table\s+(\d+)-(\d+)\*\*\s*[—]\s*(.+)$",
    ]
    rows = []
    for md in sorted(glob.glob(os.path.join(REPO, "design", "manuscript",
                                            "chapter-*", "chapter-*.md"))):
        seen = {}
        for line in open(md, encoding="utf-8").read().split("\n"):
            for p in pats:
                m = re.match(p, line)
                if m:
                    seen.setdefault((m.group(1), m.group(2)), m.group(3))
                    break
        for (n, m), raw in seen.items():
            key = f"{n}.{m}"
            if key not in labels:
                continue
            title = _lot_short_title(f"{n}-{m}")
            if title is None:
                title = re.sub(r"\*\*|\*|`", "", raw)
                title = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", title)
                title = re.sub(r"\s+", " ", title).strip().rstrip(".")
                for sep in (". ", " (", " [", "; "):
                    i = title.find(sep)
                    if 12 < i:
                        title = title[:i]
                        break
            rows.append((int(n), int(m), f"Table {n}-{m}", key, title.strip().rstrip(".")))
    # Order by chapter, then by table number --- a reader looks a table up by
    # its number, not by where it happens to fall in the chapter's flow (Ch. 26
    # prints 26-3 before 26-1).
    rows.sort()
    return [(pid, key, title) for (_, _, pid, key, title) in rows]


def make_list_of_tables():
    """Return the List of Tables block: printed ID, short title, folio.

    Folios come from \\pageref on the table's own label, so the page numbers are
    resolved by LaTeX at build time and can never drift from the body.  Tables
    the manuscript never numbers are not listed --- an unnumbered table has no
    printed ID for a reader to look up.
    """
    rows = table_catalogue()
    lines = []
    lines.append(r"\phantomsection")
    lines.append(r"\addcontentsline{toc}{chapter}{List of Tables}")
    lines.append(r"\chapter*{List of Tables}")
    lines.append(r"\markboth{List of Tables}{List of Tables}")
    lines.append(r"{\footnotesize Every table the book numbers, with a page on which it "
                 r"appears. Unnumbered tables --- inline worked calculations and continuation "
                 r"panels --- carry no printed ID and are not indexed here.\par}")
    lines.append(r"\vspace{0.6em}")
    lines.append(r"{\small")
    lines.append(r"\begin{list}{}{%")
    lines.append(r"  \setlength{\leftmargin}{0pt}\setlength{\labelwidth}{0pt}%")
    lines.append(r"  \setlength{\labelsep}{0pt}\setlength{\itemindent}{0pt}%")
    lines.append(r"  \setlength{\parsep}{3pt}\setlength{\itemsep}{0pt}%")
    lines.append(r"  \setlength{\rightmargin}{0pt}}")
    for printed_id, key, title in rows:
        lines.append(r"\item \mbox{%s}\hspace{0.7em}%s\dotfill\ \pageref{tab:%s}"
                     % (printed_id, tex_escape(title), key))
    lines.append(r"\end{list}")
    lines.append(r"}")
    if not rows:
        lines.append(r"\noindent No numbered tables.")
    return "\n".join(lines)


def emit_book():
    parts, chapters = read_parts()
    lines = []
    lines.append("% Auto-generated by render/latex/emit_book.py — do not edit by hand")
    lines.append(r"\DocumentMetadata{")
    lines.append(r"  pdfversion=1.7,")
    if not PLAIN:
        # testphase=latest activates latex-lab PDF/UA tagging (the structure
        # tree).  The plain build omits it so the PDF stays small & untagged.
        lines.append(r"  testphase=latest,")
    lines.append(r"  lang=en-US,")
    lines.append(r"}")
    if PLAIN:
        lines.append(r"\documentclass[letterpaper,11pt,openany]{book}")
        lines.append(r"\usepackage[plain]{book}")
    else:
        lines.append(r"\documentclass[letterpaper,11pt,openany]{book}")
        lines.append(r"\usepackage{book}")
    lines.append(r"\usepackage{pdfpages}")
    lines.append(r"\begin{document}")
    lines.append("")
    # Cover as full-bleed page 0: include the approved premium-minimal vector
    # cover PDF first, so the deliverable opens on the cover and stays a single
    # tagged build.
    lines.append(r"\includepdf[pages=1,fitpaper=false,noautoscale=false,alt={Front cover of From Token to Fleet: An AI Solution Architect's Handbook by Zhiqi Tao (first edition, 2026). Warm ivory editorial cover with elegant typography; large left-aligned title FROM TOKEN over TO FLEET in dark navy above an orange and teal two-dash rule; subtitle An AI Solution Architect's Handbook; a central diagram scaling left to right from one orange square labeled ONE TOKEN, through a 2x2 teal grid labeled MODEL, a pale-cyan grid labeled SYSTEM, to a 3x3 navy grid labeled FLEET, threaded by orange and teal wavy trace lines; a TRACE THE DECISION tagline, author and edition line.}]{../cover/cover_premium_front.pdf}")
    lines.append("")
    # Round-5 finding R5-004: the front matter was numbered in two schemes
    # (arabic 1-2 for the copyright page, roman i+ from the Contents).  Start
    # the roman front matter here, before the title page, so every front-matter
    # page carries one scheme; \mainmatter still restarts arabic at 1.  The
    # Contents/List of Figures page references regenerate from the .toc/.lof.
    lines.append(r"\frontmatter")
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
    # KDP standard front-matter order: TOC (and list of figures) before the
    # preface.  Each on its own fresh page.
    lines.append(r"\tableofcontents")
    lines.append("")
    lines.append(r"\clearpage")
    # \listoffigures typesets a \chapter*, which the book class does NOT add to
    # the TOC; add the entry explicitly so the front-matter apparatus is
    # navigable from the Contents (round-5 finding PA-001).  \phantomsection
    # is required: without it the Contents row / PDF bookmark inherits the
    # previous anchor and jumps to the copyright page.
    lines.append(r"\phantomsection")
    lines.append(r"\addcontentsline{toc}{chapter}{List of Figures}")
    lines.append(r"\listoffigures")
    lines.append("")
    lines.append(r"\clearpage")
    # List of Tables: the book numbers 41 tables and cross-references them by
    # number, so the apparatus indexes them alongside the figures rather than
    # leaving them reachable only from a chapter's own prose (round-7 findings
    # F-001 / P1-002 / APP-01 / NAV-001 / R7-125).
    lines.append(make_list_of_tables())
    lines.append("")
    lines.append(r"\chapter{Preface}")
    lines.append(r"\input{preface}")
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
    lines.append(r"\input{backmatter/glossary}")
    lines.append(r"\input{backmatter/references}")
    lines.append(r"\input{backmatter/sources}")
    lines.append(r"\input{backmatter/worksheet}")
    lines.append("")
    lines.append(r"\end{document}")
    return "\n".join(lines)


if __name__ == "__main__":
    out = emit_book()
    path = os.path.join(LATEX, "book.tex")
    open(path, "w", encoding="utf-8").write(out)
    print("wrote", path, len(out), "chars")
