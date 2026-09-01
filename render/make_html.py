#!/usr/bin/env python3
"""
make_html.py — build a single self-contained REVIEW artifact of the whole book
(single entry point replacing make_review.py's HTML path).

Output:  render/build/review-dark.html
  the entire book as ONE dark-mode, self-contained HTML file, all 27 chapters
  in FULL TEXT (no skeleton mode), figures inlined as base64 PNG.

Design goals (per render/HTML_STREAMLINING_PLAN.md):
  - Full-text chapters (aligned with the LaTeX pipeline; drops the old
    skeleton-summary mode).
  - No Chromium/PDF dependency (review value is the self-contained HTML).
  - Simplified preface extraction (first paragraphs of book-architecture.md
    §1,2 instead of brittle multi-regex).
  - Markdown -> HTML via pandoc (shared with the LaTeX pipeline).
  - Figures: inline the same per-chapter PNGs (browser-displayable) that the
    LaTeX pipeline also reads, keeping one image source shared by both lines.

Usage:  python3 render/make_html.py
"""

import base64
import io
import os
import re
import subprocess
import datetime

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESIGN = os.path.join(REPO, "design")
MANUSCRIPT = os.path.join(DESIGN, "manuscript")
BUILD = os.path.join(REPO, "render", "build")
os.makedirs(BUILD, exist_ok=True)

# Version = date stamp (YYYYMMDD), e.g. 20260830 -- same rule as the LaTeX
# pipeline (emit_book.py). Each dated build is its own identifiable snapshot.
VERSION = datetime.date.today().strftime("%Y%m%d")
# Deterministic slug shared by every deliverable so the file name means
# something: from-token-to-fleet-v20260830.{pdf,html}
BOOK_SLUG = "from-token-to-fleet"
OUT_STEM = f"{BOOK_SLUG}-v{VERSION}"

IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")

DARK_CSS = """
:root{--bg:#0f1115;--fg:#e6e6e6;--accent:#6aa9d6;--part:#8fb7d9;--muted:#9aa3ad;--tbl:#23272f;}
*{box-sizing:border-box}
body{margin:0 auto;max-width:880px;padding:28px 36px 120px;background:var(--bg);color:var(--fg);font:16px/1.6 Georgia,'Times New Roman',serif;}
h1,h2,h3,h4{font-family:-apple-system,'Segoe UI',sans-serif;color:var(--fg);line-height:1.25;}
h1{font-size:30px;border-bottom:2px solid var(--part);padding-bottom:10px;margin-top:38px}
h2{font-size:22px;color:var(--accent);margin-top:34px}
h3{font-size:18px;color:var(--part)}
.titleblock{text-align:center;padding:60px 0 40px;border-bottom:1px solid #333}
.titleblock h1{font-size:38px;border:none}
.subtitle{font-size:20px;color:var(--part);margin-top:8px}
.toc-part{color:var(--part);margin:18px 0 4px;font-variant:small-caps;letter-spacing:.5px}
ul.toc{list-style:none;padding-left:8px;margin:2px 0 6px}
ul.toc li{margin:3px 0}
ul.toc a{color:var(--fg);text-decoration:none}
ul.toc a:hover{color:var(--accent)}
a{color:var(--accent)}
table{border-collapse:collapse;margin:14px auto;background:var(--tbl)}
th,td{border:1px solid #3a4150;padding:6px 10px;font-size:14px}
th{background:#2a303b}
img{max-width:100%;height:auto;display:block;margin:14px auto}
figure{margin:18px 0;text-align:center}
figcaption{font-size:13px;color:var(--muted);margin-top:6px}
pre{background:#161a22;border:1px solid #2a303b;padding:12px;border-radius:6px;overflow-x:auto}
code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:14px}
h1 code,h2 code,h3 code{background:none}
blockquote{border-left:3px solid var(--accent);margin:12px 0;padding:2px 14px;color:var(--muted)}
.skel{color:var(--muted);font-style:italic}
"""


def load_book():
    """Return (title, subtitle, parts=[{id,title,theme,chapters:[(n,title,status)]}])."""
    text = open(os.path.join(DESIGN, "book.yaml"), encoding="utf-8").read()
    title = re.search(r'title: "(.+?)"', text).group(1)
    sub = re.search(r'subtitle: "(.+?)"', text)
    parts = []
    cur = None
    for line in text.splitlines():
        m = re.match(r"\s+- id: (\w+)", line)
        if m:
            cur = {"id": m.group(1), "chapters": []}
            parts.append(cur); continue
        m = re.match(r"\s+title: \"(.+?)\"", line)
        if m and cur is not None and "title" not in cur:
            cur["title"] = m.group(1); continue
        m = re.match(r"\s+theme: \"(.+?)\"", line)
        if m and cur is not None and "theme" not in cur:
            cur["theme"] = m.group(1); continue
        m = re.match(r"\s+- \{n: (\d+), title: \"(.+?)\", status: \"(\w+)\"\}", line)
        if m and cur is not None:
            cur["chapters"].append((int(m.group(1)), m.group(2), m.group(3)))
    return title, (sub.group(1) if sub else ""), parts


def load_preface():
    """Distill a short preface from book-architecture.md (simplified: grab §1 + §2)."""
    p = os.path.join(DESIGN, "book-architecture.md")
    if not os.path.exists(p):
        return []
    text = open(p, encoding="utf-8").read()
    paras = []
    for sect in [r"## 1\. Title & positioning", r"## 2\. The spine"]:
        m = re.search(sect + r"\s*(.+?)(?=\n## |\Z)", text, re.S)
        if m:
            block = m.group(1).strip()
            chunks = re.split(r"\n\s*\n", block)
            # skip a leading bold title line like "**From Token to Fleet...**"
            if chunks and chunks[0].startswith("**") and "**" in chunks[0][2:]:
                chunks = chunks[1:]
            first = chunks[0].strip() if chunks else ""
            first = re.sub(r"^> ?", "", first, flags=re.M)
            if first:
                paras.append(first)
    return paras


def chapter_md(n):
    return os.path.join(MANUSCRIPT, f"chapter-{n:02d}", f"chapter-{n:02d}.md")



def inline_html_imgs(html_frag, chapter_dir):
    """After pandoc conversion, replace every <img src="relative/path"> whose source
    file exists under chapter_dir with a base64 data URI.  This is the single,
    robust mechanism for inlining figures -- it does not depend on grabbing
    markdown image syntax before pandoc, so multiline / `]`-bearing alt text
    (e.g. 'Fig A.1 ... [1P]') is handled correctly by pandoc and caught here."""
    def rep(m):
        attrs = m.group(1)
        src_m = re.search(r'src="([^"]+)"', attrs)
        alt_m = re.search(r'alt="([^"]*)"', attrs)
        if not src_m:
            return m.group(0)
        rel = src_m.group(1).split("#")[0]
        if rel.startswith("http") or rel.startswith("data:"):
            return m.group(0)
        candidates = [
            # prefer vector svg sibling when present (smaller, crisper)
            os.path.join(chapter_dir, os.path.splitext(rel)[0] + ".svg"),
            os.path.join(chapter_dir, "figures", os.path.splitext(rel)[0] + ".svg"),
            os.path.join(chapter_dir, rel),
            os.path.join(chapter_dir, "figures", rel),
        ]
        src = next((c for c in candidates if os.path.exists(c)), None)
        if src is None:
            return m.group(0)  # leave as-is; caller flags it
        with open(src, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        ext = src.lower().rsplit(".", 1)[-1]
        mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
                "svg": "image/svg+xml", "gif": "image/gif"}.get(ext, "application/octet-stream")
        alt = alt_m.group(1) if alt_m else ""
        return f'<img alt="{alt}" src="data:{mime};base64,{b64}"/>'
    return re.sub(r"<img\b([^>]*)>", rep, html_frag)


def render_toc(parts):
    h = ["<h2>Table of Contents</h2>"]
    for p in parts:
        h.append(f"<h3 class='toc-part'>Part {p['id']} — {p['title']}</h3>")
        h.append("<ul class='toc'>")
        for n, t, st in p["chapters"]:
            h.append(f"<li><a href='#chapter-{n:02d}'>Ch {n}. {t}</a> <span class='skel'>[{st}]</span></li>")
        h.append("</ul>")
    return "\n".join(h)


def number_headings(body, n):
    """Number section/subsection headings in a chapter's HTML body to match the
    LaTeX numbering (chapter.section and chapter.section.subsection), and strip
    any hardcoded 'N. ' ordinal prefixes from the source markdown headings.

    The source markdown uses '## 1. Concept' style headings. LaTeX auto-numbers
    them as '7.2 Concept'; here we drop the redundant hardcoded ordinal and
    inject the same chapter.section (and chapter.section.subsection) number so
    the HTML and PDF agree on section numbering.
    """
    def stripordinal(t):
        return re.sub(r"^\d{1,2}\.\s+", "", t)
    # split body into <h2>...</h2> blocks and everything between, keeping order
    # so subsection (h3) numbering can reuse the current section counter.
    out = []
    sec = 0
    sub = 0
    pat = re.compile(r"(<h2 id=\"([^\"]*)\"\s*>(.*?)</h2>)|(<h3 id=\"([^\"]*)\"\s*>(.*?)</h3>)", re.S)
    last = 0
    for m in pat.finditer(body):
        out.append(body[last:m.start()])
        if m.group(1):  # h2 -> new section
            sec += 1
            sub = 0
            inner = stripordinal(m.group(3).strip())
            repl = f"<h2 id=\"{m.group(2)}\">{n}.{sec} {inner}</h2>"
        else:           # h3 -> subsection of current section
            sub += 1
            inner = stripordinal(m.group(6).strip())
            repl = f"<h3 id=\"{m.group(5)}\">{n}.{sec}.{sub} {inner}</h3>"
        out.append(repl)
        last = m.end()
    out.append(body[last:])
    return "".join(out)


def build_html():
    title, subtitle, parts = load_book()
    preface = load_preface()
    out = []
    out.append("<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'/>")
    out.append(f"<title>{title}</title><style>{DARK_CSS}</style>")
    # KaTeX for math: self-contained math rendering via CDN (falls back to
    # raw LaTeX source if offline). The book now carries ~120 display/inline
    # formulas (Ch.2-22), so inline math must render, not show as raw $...$.
    out.append("<link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css'/>")
    out.append("<script defer src='https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js'></script>")
    out.append("<script defer src='https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js' onload='renderMathInElement(document.body,{delimiters:[{left:\"$$\",right:\"$$\",display:true},{left:\"$\",right:\"$\",display:false}]})'></script>")
    out.append("</head><body>")
    out.append(f"<div class='titleblock'><h1>{title}</h1>")
    if subtitle:
        out.append(f"<div class='subtitle'>{subtitle}</div>")
    out.append(f"<div style='color:#9aa3ad;margin-top:14px;font-size:14px'>Version {VERSION}</div>")
    out.append("<div style='color:#9aa3ad;margin-top:20px;font-style:italic;max-width:620px;margin-left:auto;margin-right:auto'><p>First and foremost a learning tool I wrote for myself &mdash; if it helps you too, that is a bonus, above and beyond what I set out to do.</p></div>")
    out.append("<div style='color:#9aa3ad;margin-top:18px;font-size:13px;max-width:640px;margin-left:auto;margin-right:auto;border-top:1px solid #333;padding-top:12px'>Copyright &copy; 2026 Zhiqi Tao, all rights reserved. Licensed under a <b>source-available</b> license: free to read, study, and redistribute (with attribution) for personal and non-commercial ends; <b>commercial use or publication requires the author's prior written approval</b> (zhiqi.tao@gmail.com). Full terms: <code>github.com/zhiqitao/from-token-to-fleet</code> &middot; SPDX <code>LicenseRef-ZhiqiResearch-FromTokenToFleet-1.0</code>.</div>")
    out.append("</div>")
    if preface:
        out.append("<h2>Preface</h2>")
        for para in preface:
            out.append(f"<p>{para}</p>")
        # inline the book-spine decision-loop diagram into the preface for
        # PDF/HTML consistency (light diagram on dark card, like other figures)
        spine_png = os.path.join(os.path.dirname(os.path.abspath(__file__)), "archify", "spine-diagram.png")
        if os.path.exists(spine_png):
            b64 = base64.b64encode(open(spine_png, "rb").read()).decode()
            out.append("<figure style='margin:22px auto 4px;text-align:center'>"
                       f"<img alt='The architect decision loop' src='data:image/png;base64,{b64}' "
                       "style='max-width:100%;border:1px solid var(--border,#334155);border-radius:8px'/>"
                       "<figcaption>The architect's decision loop &mdash; the book's spine. A vague requirement is carried through workload characterization, constraints, candidate architectures, benchmarking, bottleneck analysis, TCO, and a final red-team challenge before an architecture is committed.</figcaption></figure>")
    out.append(render_toc(parts))
    # build chapter map
    chmap = {}
    for p in parts:
        for n, t, st in p["chapters"]:
            chmap[n] = (t, st)
    for n in sorted(chmap):
        md_path = chapter_md(n)
        if not os.path.exists(md_path):
            out.append(f"<section id='chapter-{n:02d}'><h2>Chapter {n}</h2><p class='skel'>[draft missing]</p></section>")
            continue
        md_text = open(md_path, encoding="utf-8").read()
        chapter_dir = os.path.dirname(md_path)
        r = subprocess.run(["pandoc", "-f", "markdown+pipe_tables+fenced_code_blocks-yaml_metadata_block",
                            "-t", "html5"], input=md_text.encode(), capture_output=True)
        body = r.stdout.decode() if r.returncode == 0 else md_text
        body = inline_html_imgs(body, chapter_dir)
        body = number_headings(body, n)
        title_t = chmap[n][0]
        out.append(f"<section id='chapter-{n:02d}'><h2>Chapter {n} — {title_t}</h2>{body}</section>")
    out.append("</body></html>")
    return "\n".join(out)


def main():
    html = build_html()
    dst = os.path.join(BUILD, OUT_STEM + ".html")
    open(dst, "w", encoding="utf-8").write(html)
    print(f"wrote {dst} ({os.path.getsize(dst)/1024:.0f} KB, {html.count('<section')} sections)")


if __name__ == "__main__":
    main()
