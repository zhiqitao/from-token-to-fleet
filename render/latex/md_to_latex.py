#!/usr/bin/env python3
"""md_to_latex.py -- convert the 27 manuscript chapters to LaTeX for the book.

Workflow:
  1. Copy all chapter figures into render/latex/figures/ (flat, dedup by name).
  2. For each chapter, rewrite image paths to the flat figures/ dir and run pandas
     to produce a per-chapter .tex with \chapter + sections.
  3. Emit the master book.tex that \frontmatter (title/preface/toc) + \mainmatter
     (parts/chapters) + \backmatter.
"""
import os, re, sys, glob, shutil, subprocess, json

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root
LATEX = os.path.join(REPO, "render", "latex")
MANUSCRIPT = os.path.join(REPO, "design", "manuscript")
FIG = os.path.join(LATEX, "figures")
CH = os.path.join(LATEX, "chapters")

os.makedirs(FIG, exist_ok=True)
os.makedirs(CH, exist_ok=True)

# Tectonic/LaTeX binary, resolved portably: explicit TECTONIC env override,
# else whatever is on PATH. No hard-coded machine-specific paths.
TECTONIC = os.environ.get("TECTONIC") or shutil.which("tectonic") or "tectonic"


def read_yaml_chapters():
    """Return {n: {title, part}} and parts ordered from design/book.yaml."""
    text = open(os.path.join(REPO, "design", "book.yaml"), encoding="utf-8").read()
    parts = []
    chapters = {}
    cur_part = None
    for line in text.splitlines():
        m = re.match(r"\s+- id: (\w+)", line)
        if m:
            cur_part = {"id": m.group(1), "chapters": []}
            parts.append(cur_part)
            continue
        m = re.match(r"\s+title: \"(.+?)\"", line)
        if m and cur_part is not None and "title" not in cur_part:
            cur_part["title"] = m.group(1)
            continue
        m = re.match(r"\s+- \{n: (\d+), title: \"(.+?)\", status: \"(\w+)\"\}", line)
        if m and cur_part is not None:
            n = int(m.group(1))
            chapters[n] = {"title": m.group(2), "part": cur_part["id"]}
            cur_part["chapters"].append(n)
    return parts, chapters


# regex that tolerates nested brackets in alt text (e.g. '[1P]' inside alt)
# (handles arbitrary nesting depth: '[2° DERIVED; a [1P: vendor datasheet]]')
IMG_RE = re.compile(r"!\[((?:[^\[\]]|\[(?:[^\[\]]|\[[^\[\]]*\])*\])*)\]\(([^)]+)\)")


def fix_colspec(tex_path):
    """Rewrite pandoc's relative-width table colspecs (xelatex-incompatible)
    into simple p{<frac>\\linewidth} columns.
    E.g. 'p{(\\linewidth - 4\\tabcolsep) * \\real{0.3333}}' -> 'p{0.3333\\linewidth}'.
    """
    import re as _re
    tex = open(tex_path, encoding="utf-8").read()
    def repl(m):
        frac = m.group(1)
        return f"p{{{frac}\\linewidth}}"
    new = _re.sub(r"p\{\(\\linewidth\s*-\s*\d+\\tabcolsep\)\s*\*\s*\\real\{([0-9.]+)\}\}", repl, tex)
    # also collapse any residual \raggedright\arraybackslash> into plain
    if new != tex:
        open(tex_path, "w", encoding="utf-8").write(new)
        return True
    return False


def fix_wide_tables(tex_path):
    """Scale down pandoc longtable colspecs whose p{\\\\linewidth} column widths
    sum to near (or over) the text block, so the total table width (columns plus
    longtable's inter-column \\\\tabcolsep padding) does not overflow the ~6.1in
    column.  Keeps a target sum (<=0.88) to leave room for the padding; never
    widens an already-narrow table.  Also makes long filename-like tokens in
    cells breakable (allowbreak before '.json'/'.pt'/'.png'/'/'-separators) so a
    single unhyphenatable name cannot push a column past the margin."""
    import re as _re
    tex = open(tex_path, encoding="utf-8").read()
    # Operate on each longtable block, from \\begin{longtable} up to the first
    # \\toprule / \\end{longtable}.  The colspec (the p{...} widths) lives there.
    def repl(blk):
        spec = blk[:blk.find("\\toprule") if "\\toprule" in blk else len(blk)]
        fracs = [float(x) for x in _re.findall(r"p\{([0-9.]+)\\linewidth\}", spec)]
        if not fracs:
            return blk
        total = sum(fracs)
        scale = (0.88 / total) if total > 0.88 else 1.0
        def rep2(mm):
            return "p{%s\\linewidth}" % ("%.4f" % (float(mm.group(1)) * scale))
        return _re.sub(r"p\{([0-9.]+)\\linewidth\}", rep2, blk)
    new = _re.sub(r"(?s)(\\begin\{longtable\}.*?\\toprule|\\begin\{longtable\}.*?\\end\{longtable\})",
                  lambda mm: repl(mm.group(1)), tex)
    # Breakable filename tokens in TABLE CELL text.  Never touch
    # \includegraphics{...} paths (those sit in figures/, not cells) -- guard by
    # only rewriting inside \begin{longtable}...\end{longtable} blocks.
    def break_files(blk):
        # Break long filename-like tokens at their extension dot.
        return _re.sub(r"([A-Za-z0-9_./-]+)\.(json|pt|png|pdf|csv|yaml|yml)\b",
                       r"\1.\\allowbreak\\hbox{}\2", blk)
    new = _re.sub(r"(?s)(\\begin\{longtable\}.*?\\end\{longtable\})",
                  lambda mm: break_files(mm.group(1)), new)
    if new != tex:
        open(tex_path, "w", encoding="utf-8").write(new)
        return True
    return False


def fix_figure_width(tex_path):
    """Ensure every pandoc \includegraphics is width-constrained to the text
    block (scale down over-wide figures, never enlarge). Pandoc emits
    \includegraphics[keepaspectratio,alt={...}]{figures/x.png} with no width;
    append width=\maxwidth{\textwidth} so wide source images fit."""
    tex = open(tex_path, encoding="utf-8").read()
    # Rewrite \includegraphics[keepaspectratio,alt={...}]{file} to add width.
    import re as _re
    pat = _re.compile(r"\\includegraphics\[((?:[^\[\]]|\[[^\]]*\])*)\]\{(figures/[^}]+)\}")
    def repl(m):
        opts = m.group(1)
        if "width=" in opts:      # already has a width: leave unchanged
            return m.group(0)
        return "\\includegraphics[%s,width=\\maxwidth{\\textwidth},keepaspectratio]{%s}" % (opts, m.group(2))
    new = pat.sub(repl, tex)
    if new != tex:
        open(tex_path, "w", encoding="utf-8").write(new)
        return True
    return False


def fix_verbatim(tex_path):
    """Route pandoc's plain \\\\begin{verbatim} blocks through fancyvrb's
    Verbatim with breaklines/breakanywhere so long code lines wrap instead of
    overflowing the ~6.1in text column."""
    import re as _re
    tex = open(tex_path, encoding="utf-8").read()
    if "\\begin{verbatim}" not in tex:
        return False
    tex = tex.replace("\\begin{verbatim}",
        "\\begin{Verbatim}[breaklines=true, breakanywhere=true, fontsize=\\small]")
    tex = tex.replace("\\end{verbatim}", "\\end{Verbatim}")
    open(tex_path, "w", encoding="utf-8").write(tex)
    return True


def fix_urls(tex_path):
    """Wrap long bare URLs in body text in \\\\url{} so the hyphens url-package
    lets them break across lines (a raw http://... string cannot break and
    overflows the text column).  Skip URLs already wrapped and those inside
    \\includegraphics / tables (handled elsewhere)."""
    import re as _re
    tex = open(tex_path, encoding="utf-8").read()
    # Only rewrite outside longtable and outside \texttt{...}/\url{...}.
    parts = _re.split(r"(?s)(\\begin\{longtable\}.*?\\end\{longtable\})", tex)
    changed = False
    def wrap(body):
        # Match a bare URL, then trim trailing punctuation (; , . ) ] ), and
        # un-escape any \\_ pandoc emitted so it doesn't render a literal
        # backslash inside \\url{} (url handles underscores natively).
        pat = _re.compile(r"(?<!\\url\{)(https?://[^\s}]+)")
        def repl(mm):
            u = mm.group(1)
            u = _re.sub(r"[;,.)\]]+$", "", u)
            return "\\url{%s}" % u.replace("\\_", "_")
        return pat.sub(repl, body)
    new = parts[0]
    for k in range(1, len(parts), 2):
        new += parts[k]                      # longtable block: leave alone
        if k + 1 < len(parts):
            new += wrap(parts[k + 1])
    if new != tex:
        open(tex_path, "w", encoding="utf-8").write(new)
        return True
    return False


def short_title(full):
    """Derive a concise navigational title from a (possibly long) figure caption.

    Used as the bracket-form short caption for caption[short]{long} so the
    List of Figures lists a navigational phrase rather than the full paragraph.
    Strategy: take the leading clause up to the first sentence-period that is
    followed by whitespace-and-a-capital (a natural title boundary), fall back to
    the first em-dash / colon, and cap the length.
    """
    import re as _re
    s = full.strip()
    # cut at first '. ' that looks like a sentence boundary
    m = _re.match(r"^(.*?\.)\s+(?=[A-Z])", s)
    if m and len(m.group(1)) > 12:
        s = m.group(1)
    # cut at first em-dash / colon (falls back for caption-phrase titles)
    if len(s) > 60:
        for sep in (" — ", "——", " — ", ":", " - "):
            i = s.find(sep)
            if 0 < i < 200:
                s = s[:i].strip()
                break
    # hard cap ~80 chars to keep the List of Figures tidy
    if len(s) > 84:
        s = s[:81].rstrip() + "…"
    # strip trailing punctuation and any leftover bracket marker
    s = s.rstrip(" .:;")
    return s.strip() or ""


def fix_captions(tex_path):
    """Strip the manually-written 'Fig X.Y' prefix from captions and alt text.

    Pandoc copies the markdown caption verbatim (e.g. '*Fig 1.1 — The KV cache…*'),
    so the resulting \\caption{Fig 1.1 — …} duplicates the figure environment's
    auto-generated 'Figure 1.1:' label.  Also strip the editorial bracket markers
    ([ILLUSTRATIVE…], [VERIFY], [HYPOTHESIS], [DERIVED]) from captions/alt so they
    do not leak into the List of Figures or the accessibility alt text.
    """
    import re as _re
    tex = open(tex_path, encoding="utf-8").read()
    orig = tex

    # Strip a leading self-referential 'Fig X.Y' (optionally inside
    # \\hyperref[fig:X.Y]{Fig X.Y}) plus the following dash run.
    lead = _re.compile(
        r"(?:\\hyperref\[fig:\d+\.\d+\]\{)?"
        r"\s*Fig(?:ure)?\s+(?:\d+\.\d+|[A-Z]\.\d+)\}?\s*(?:---|--|[—–-]|\\textemdash)+\s*"
    )
    # Also a leading bare 'Fig X.Y —' with no link.
    lead2 = _re.compile(r"\s*Fig(?:ure)?\s+(?:\d+\.\d+|[A-Z]\.\d+)\s*(?:---|--|[—–-])+\s*")

    def strip_lead(t):
        t = lead.sub("", t)
        t = lead2.sub("", t)
        return t

    def clean_marks(t):
        # Remove editorial bracket markers: {[}ILLUSTRATIVE textual{]},
        # [ILLUSTRATIVE…], [VERIFY…], [HYPOTHESIS…], [DERIVED…], [1P], [2°…],
        # and the pandoc-escaped braces around them.
        t = _re.sub(r"\{\[\]\}\s*(?:ILLUSTRATIVE|VERIFY|HYPOTHESIS|DERIVED)[^\[\]]*\{\]\}", "", t)
        t = _re.sub(r"\[\s*(?:ILLUSTRATIVE|VERIFY|HYPOTHESIS|DERIVED)[^\[\]]*\]", "", t)
        # Drop a stray leading backslash that can remain from a stripped
        # '\hyperref[...]{Fig X.Y} --- ' prefix (an undefined-control-sequence
        # whose first char silently drops the caption's leading word).  Only
        # remove a backslash immediately followed by a capital letter that was
        # not itself a real LaTeX command.
        t = _re.sub(r"^\s*\\\s*(?=[A-Z])", "", t)
        t = _re.sub(r"\s+", " ", t).strip()
        return t

    # Apply to every \\caption{...} and alt={...}.
    def cap_repl(m):
        full = clean_marks(strip_lead(m.group(1)))
        short = short_title(full)
        # Short caption goes into the bracket form so the List of Figures lists a
        # navigational title instead of the full paragraph (reviewer §8).
        if short and short != full:
            return "\\caption[" + short + "]{" + full + "}"
        return "\\caption{" + full + "}"
    tex = _re.sub(r"\\caption\{((?:[^{}]|\{[^{}]*\})*)\}", cap_repl, tex)

    def alt_repl(m):
        return "alt={" + clean_marks(strip_lead(m.group(1))) + "}"
    tex = _re.sub(r"alt=\{((?:[^{}]|\{[^{}]*\})*)\}", alt_repl, tex)

    if tex != orig:
        open(tex_path, "w", encoding="utf-8").write(tex)
        return True
    return False


def fix_minicase_toc(tex_path):
    """Suppress the per-chapter *template* sections from the TOC.

    The 26 chapters each use the same 8-part template (The Architect's Question
    / Concept / Mental Model / Worked Example / Measurement / Common Mistakes /
    Architecture Consequence / What We Still Don't Know). Left as normal
    \\section, these write hundreds of near-identical lines into the table of
    contents. We wrap each such template \\section in \\ntsection (defined in
    book.sty), which numbers and formats it exactly like \\section but writes
    NO toc entry. The chapter's 'End-of-Chapter Mini-Case: <distinct title>'
    section is deliberately left as a normal \\section so it remains a
    navigable, distinct TOC entry.
    """
    import re as _re
    TEMPLATE = (
        "The Architect's Question", "Concept", "Mental Model",
        "Worked Example", "Measurement", "Common Mistakes",
        "Architecture Consequence", "What We Still Don't Know",
    )
    tex = open(tex_path, encoding="utf-8").read()
    orig = tex
    # Match an entire \section{...}\label{...} (title may wrap across lines).
    pat = _re.compile(r"\\section\{((?:[^{}]|(?:\{[^{}]*\}))*?)\}(\s*\\label\{[^}]*\})?", flags=_re.S)
    def repl(m):
        title = m.group(1).strip()
        label = m.group(2) or ""
        # Normalize: drop LaTeX escapes/brackets, then match on the leading
        # template keyword so a subtitled variant is caught too (e.g.
        # "Worked Example — Embedding-Model vs Generation").
        norm = _re.sub(r"\\(?:[\\&%$#_{}]|text[a-z]+)|[{}~]", "", title).strip()
        base = re.split(r"[:\u2014\u2013-]", norm)[0].strip()
        if any(t.strip() == base for t in TEMPLATE):
            return "\\ntsection{" + title + "}" + label + "\n"
        return m.group(0)
    tex = pat.sub(repl, tex)
    if tex != orig:
        open(tex_path, "w", encoding="utf-8").write(tex)
        return True
    return False


def fix_crossrefs(tex_path, chnum):
    """Add \\label to every figure/table and turn body references
    ('Fig X.Y', 'TAB X.Y', 'Chapter N') into clickable \\hyperref links.
    Returns True if the file changed."""
    import re as _re
    tex = open(tex_path, encoding="utf-8").read()

    # 1) Label every figure from its caption: \label{fig:X.Y} before \end{figure}
    fig_pat = _re.compile(r"(\\begin\{figure\}.*?\\caption\{([^}]*?)\})(.*?)(\\end\{figure\})", _re.S)
    def fig_repl(m):
        head, caption, between, end = m.groups()
        mm = _re.search(r"\bFig(?:ure)?\s+(\d+)\.(\d+)", caption)
        if not mm:
            return m.group(0)
        lab = f"fig:{mm.group(1)}.{mm.group(2)}"
        return f"{head}{between}\n\\label{{{lab}}}{end}"
    tex = fig_pat.sub(fig_repl, tex)

    # 2) Label every longtable by chapter position: \label{tab:<chnum>.<k>}
    tab_pat = _re.compile(r"(\\begin\{longtable\}.*?)(\\end\{longtable\})", _re.S)
    k = [0]
    def tab_repl(m):
        k[0] += 1
        body, end = m.groups()
        lab = f"tab:{chnum}.{k[0]}"
        return f"{body}\n\\label{{{lab}}}{end}"
    tex = tab_pat.sub(tab_repl, tex)

    # 3) Body refs -> \\hyperref. Stash caption/alt definitions first so a
    #    definition never links to itself.
    protected = {}
    def stash(m):
        key = f"XZPROT{len(protected)}XZ"
        protected[key] = m.group(0)
        return key
    tex2 = _re.sub(r"\\caption\{[^{}]*\}", stash, tex)
    tex2 = _re.sub(r"alt=\{[^{}]*\}", stash, tex2)

    def linkrefs(s):
        # Skip verbatim/Verbatim code blocks first so a copy-ready template
        # (e.g. the ADR template in Ch25) does NOT get "Chapter 22" turned into
        # \\hyperref[chap:22]{Chapter 22} — that would leak LaTeX markup into a
        # block meant to be copied as plain Markdown.
        blocks = _re.split(r"(\\begin\{(?:verbatim|Verbatim)\}.*?\\end\{(?:verbatim|Verbatim)\})", s, flags=_re.S)
        out = []
        for part in blocks:
            if _re.match(r"^\\begin\{(?:verbatim|Verbatim)\}", part):
                out.append(part)
                continue
            # Stash heading-title bodies so a cross-reference inside a heading
            # ("Table 4-1", "Fig X.Y") is NOT hyperref-wrapped — a \\hyperref in
            # a moving heading argument triggers "There's no line here to end".
            stash = {}
            def stub2(m):
                k = f"XZH{len(stash)}XZ"
                stash[k] = m.group(2)
                return m.group(1) + k + "}"
            part = _re.sub(r"(\\(?:chapter|section|subsection|subsubsection|paragraph)\s*\*?\s*\{)(.*?)\}(?=(?:\\label|\\index|\n|$))", stub2, part, flags=_re.S)
            part = _re.sub(r"\bFig(?:ure)?\s+(\d+)\.(\d+)",
                           lambda mm: f"\\hyperref[fig:{mm.group(1)}.{mm.group(2)}]{{Fig {mm.group(1)}.{mm.group(2)}}}", part)
            part = _re.sub(r"\bTable\s+(\d+)-(\d+)",
                           lambda mm: f"\\hyperref[tab:{mm.group(1)}.{mm.group(2)}]{{Table {mm.group(1)}-{mm.group(2)}}}", part)
            part = _re.sub(r"\bChapter\s+(\d+)",
                           lambda mm: f"\\hyperref[chap:{mm.group(1)}]{{Chapter {mm.group(1)}}}", part)
            for k, v in stash.items():
                part = part.replace(k, v)
            out.append(part)
        return "".join(out)
    tex2 = linkrefs(tex2)
    for key, val in protected.items():
        tex2 = tex2.replace(key, val)

    if tex2 != tex:
        open(tex_path, "w", encoding="utf-8").write(tex2)
        return True
    return False


def copy_figures():
    """Copy all chapter figures into a flat dir; return {orig_rel: flat_name}."""
    mapping = {}
    for md in sorted(glob.glob(os.path.join(MANUSCRIPT, "chapter-*", "*.md"))):
        ch = os.path.dirname(md)
        txt = open(md, encoding="utf-8").read()
        for m in IMG_RE.finditer(txt):
            rel = m.group(2).split("#")[0]
            if rel.startswith("http"):
                continue
            src = os.path.normpath(os.path.join(ch, rel))
            if not os.path.exists(src):
                continue
            # Prefer a sibling vector .pdf (matplotlib 'pdf' backend) when it
            # exists -- keeps the book PDF small and figures crisp on zoom.
            # Hand-drawn HTML/SVG originals (no .pdf) stay as .png.
            if src.lower().endswith(".png"):
                pdf_src = src[:-4] + ".pdf"
                if os.path.exists(pdf_src):
                    src = pdf_src
            flat = os.path.basename(src)
            dst = os.path.join(FIG, flat)
            # Always copy so regenerated figures propagate; cheap (few figures)
            # and avoids stale-artifact bugs like a black-background old copy
            # surviving when the source was fixed.
            shutil.copy(src, dst)
            mapping[rel] = flat
    return mapping



def convert(mapping):
    """Run pandoc per chapter -> chapters/chNN.tex with \chapter\label."""
    parts, chapters = read_yaml_chapters()
    built = {}
    for n in sorted(chapters):
        src = os.path.join(MANUSCRIPT, "chapter-%02d" % n, "chapter-%02d.md" % n)
        if not os.path.exists(src):
            continue
        txt = open(src, encoding="utf-8").read()
        # Strip the H1 chapter title line (book.tex supplies \chapter{title});
        # otherwise pandoc would emit a duplicate 'Chapter N' heading.
        lines = txt.split("\n")
        if lines and lines[0].startswith("# "):
            lines.pop(0)
        txt = "\n".join(lines)
        # Strip hardcoded 'N. ' / 'N.N. ' ordinal prefixes from headings (e.g.
        # '## 1. Concept', '### 3.1 Hardware capacity mapping') so header
        # numbering is owned by the renderer (LaTeX \section auto-numbers to
        # '7.2 Concept' / '18.4.1 Hardware…' instead of duplicating it).
        txt = re.sub(r"^(#{2,3})\s+\d{1,2}(?:\.\d{1,2})?\.?\s+", r"\1 ", txt, flags=re.M)
        # rewrite image paths to flat figures dir
        def rep(m):
            alt = m.group(1)
            rel = m.group(2).split("#")[0]
            flat = mapping.get(rel, rel)
            return f"![{alt}](figures/{flat})"
        txt = IMG_RE.sub(rep, txt)
        md_path = os.path.join(LATEX, "_md", f"ch{n:02d}.md")
        os.makedirs(os.path.dirname(md_path), exist_ok=True)
        open(md_path, "w", encoding="utf-8").write(txt)
        out = os.path.join(CH, f"ch{n:02d}.tex")
        cmd = [
            "pandoc", md_path,
            "-f", "markdown+pipe_tables+fenced_code_blocks-yaml_metadata_block",
            "-t", "latex",
            "--top-level-division=chapter",
            "-o", out,
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"pandoc fail ch{n}: {r.stderr[-400:]}")
        fix_colspec(out)
        fix_wide_tables(out)
        fix_figure_width(out)
        fix_verbatim(out)
        fix_urls(out)
        fix_crossrefs(out, n)
        fix_captions(out)
        fix_minicase_toc(out)
        built[n] = (chapters[n]["title"], out)
    return built


if __name__ == "__main__":
    mapping = copy_figures()
    print("figures copied:", len(mapping))
    built = convert(mapping)
    print("chapters converted:", len(built))
