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


def fix_figure_width(tex_path):
    """Ensure every pandoc \\includegraphics is width-constrained to the text
    block (scale down over-wide figures, never enlarge). Pandoc emits
    \\includegraphics[keepaspectratio,alt={...}]{figures/x.png} with no width;
    append width=\\maxwidth{\\textwidth} so wide source images fit."""
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
        s = _re.sub(r"\bFig(?:ure)?\s+(\d+)\.(\d+)",
                    lambda mm: f"\\hyperref[fig:{mm.group(1)}.{mm.group(2)}]{{Fig {mm.group(1)}.{mm.group(2)}}}", s)
        s = _re.sub(r"\bTable\s+(\d+)-(\d+)",
                    lambda mm: f"\\hyperref[tab:{mm.group(1)}.{mm.group(2)}]{{Table {mm.group(1)}-{mm.group(2)}}}", s)
        s = _re.sub(r"\bChapter\s+(\d+)",
                    lambda mm: f"\\hyperref[chap:{mm.group(1)}]{{Chapter {mm.group(1)}}}", s)
        return s
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
        # Strip hardcoded 'N. ' ordinal prefixes from headings (e.g. '## 1. Concept')
        # so header numbering is owned by the renderer (LaTeX \section auto-numbers
        # to '7.2 Concept' instead of producing '7.2 1. Concept').
        txt = re.sub(r"^(#{2,3})\s+\d{1,2}\.\s+", r"\1 ", txt, flags=re.M)
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
        fix_figure_width(out)
        fix_crossrefs(out, n)
        built[n] = (chapters[n]["title"], out)
    return built


if __name__ == "__main__":
    mapping = copy_figures()
    print("figures copied:", len(mapping))
    built = convert(mapping)
    print("chapters converted:", len(built))
