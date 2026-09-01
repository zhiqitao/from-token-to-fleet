#!/usr/bin/env python3
"""
make_review.py — build a single self-contained REVIEW artifact of the whole book.

Outputs (into render/build/):
  review-dark.html  the entire book as ONE dark-mode, self-contained HTML file
                    (images inlined as base64) — for human/agent review any browser.
  review-light.pdf  the same content rendered as a light-mode PDF (via headless
                    Chromium --print-to-pdf), for reading/attaching.

It assembles, from the repo's authoritative sources:
  - Title + subtitle            : design/book.yaml
  - Preface                     : distilled from design/book-architecture.md
                                    (§1 positioning, §2 spine, §14 reading paths)
  - Table of contents           : design/book.yaml (all 26 chapters, per part)
  - Chapter 1 (full text)       : design/manuscript/chapter-01/chapter-01.md
                                    (+ its two figures, inlined as base64)
  - Chapters 2-26 (skeleton)    : per-chapter one-line theses from
                                    design/book-architecture.md §9

The script is deterministic (no network, no random): the same repo always
produces the same artifact. It requires only Python's `markdown` package and a
Chromium binary for the PDF step (see CHROME below).

Usage:  python3 render/make_review.py
"""

import base64
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESIGN = os.path.join(REPO, "design")
MANUSCRIPT = os.path.join(DESIGN, "manuscript")
BUILD = os.path.join(REPO, "render", "build")
os.makedirs(BUILD, exist_ok=True)

# Chromium for the PDF step. Prefer one on PATH, then the playwright-downloaded
# binary (discovered without assuming a user or a specific browser build number).
CHROME_CANDIDATES = ["chromium", "chromium-browser", "google-chrome", "chrome"]

def _playwright_chrome():
    import glob
    for base in (os.path.expanduser("~/.cache/ms-playwright"),
                 os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "")):
        if not base or not os.path.isdir(base):
            continue
        hits = sorted(glob.glob(os.path.join(base, "*")), reverse=True)
        for d in hits:
            exe = os.path.join(d, "chrome-linux", "chrome")
            if os.path.isfile(exe) and os.access(exe, os.X_OK):
                return exe
    return None


def find_chrome():
    for c in CHROME_CANDIDATES:
        if os.path.isfile(c) and os.access(c, os.X_OK):
            return c
        # also try a PATH lookup
        r = subprocess.run(["sh", "-c", f"command -v {c}"], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    return _playwright_chrome()


def load_yaml_chapters():
    """Parse design/book.yaml: return (title, subtitle, parts=[{id,title,theme,chapters:[(n,title,status)]}])."""
    text = open(os.path.join(DESIGN, "book.yaml"), encoding="utf-8").read()
    book_title = re.search(r'title: "(.+?)"', text).group(1)
    sub = re.search(r'subtitle: "(.+?)"', text)
    subtitle = sub.group(1) if sub else ""
    parts = []
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
        m = re.match(r"\s+theme: \"(.+?)\"", line)
        if m and cur is not None:
            cur["theme"] = m.group(1)
            continue
        m = re.match(r"\s+- \{n: (\d+), title: \"(.+?)\", status: \"(\w+)\"\}", line)
        if m and cur is not None:
            cur["chapters"].append((int(m.group(1)), m.group(2), m.group(3)))
    return book_title, subtitle, parts


def load_preface():
    """Distill a short reader-facing preface from book-architecture.md."""
    arch = open(os.path.join(DESIGN, "book-architecture.md"), encoding="utf-8").read()
    parts = []
    m = re.search(r"## 1\. Title & positioning\s+(.+?)\n(?=\n## |\Z)", arch, re.S)
    if m:
        pos = re.search(r"A learning resource.*?layer\.", m.group(1), re.S)
        parts.append(pos.group(0).strip() if pos else "")
    m = re.search(r"## 2\. The spine.*?\n> (.+?)\n", arch, re.S)
    if m:
        parts.append("The book has one thesis, and it is the spine of every chapter: " + m.group(1).strip())
    m = re.search(r"\*\*Reading paths\.\*\*.*?(?=\n\n|\Z)", arch, re.S)
    if m:
        parts.append("How to read it: " + " ".join(m.group(0).replace("**Reading paths.**", "").split()))
    # dedupe empties
    return [p for p in parts if p]


def load_skeleton():
    """Extract per-chapter one-line theses from §9 (Ch N · Title — desc ...)."""
    arch = open(os.path.join(DESIGN, "book-architecture.md"), encoding="utf-8").read()
    m = re.search(r"## 9\. Revised chapter skeleton(.*?)(?=\n## 10\.|\Z)", arch, re.S)
    if not m:
        return {}
    sec = m.group(1)
    out = {}
    for line in sec.splitlines():
        mm = re.match(r"- \*\*Ch (\d+) · (.+?)\*\*[— ]+(.*)$", line.strip())
        if mm:
            out[int(mm.group(1))] = {"title": mm.group(2).strip(), "thesis": mm.group(3).strip()}
        elif re.match(r"- \*\*Ch (\d+) · (.+?)\*\*$", line.strip()):
            mm = re.match(r"- \*\*Ch (\d+) · (.+?)\*\*$", line.strip())
            out[int(mm.group(1))] = {"title": mm.group(2).strip(), "thesis": ""}
    return out


def load_chapter(n):
    """Return (markdown_body, {rel_img_path: b64}) for chapter n (full text)."""
    chp = os.path.join(MANUSCRIPT, "chapter-%02d" % n, "chapter-%02d.md" % n)
    text = open(chp, encoding="utf-8").read()
    figs = {}
    for p in re.findall(r"!\[[^\]]*\]\(([^)]+)", text):
        rel = p.split("#")[0]
        full = os.path.normpath(os.path.join(os.path.dirname(chp), rel))
        if os.path.exists(full):
            figs[rel] = base64.b64encode(open(full, "rb").read()).decode()
    return text, figs


def load_chapter1():
    """Back-compat alias that returns chapter 1."""
    return load_chapter(1)


def inline_base64(md_body, figs):
    def rep(m):
        title = m.group(1) or ""          # group 1 = alt text
        rel = m.group(2).split("#")[0]    # group 2 = image path
        b64 = figs.get(rel)
        if not b64:
            return m.group(0)
        ext = rel.rsplit(".", 1)[-1].lower()
        mime = {"png": "image/png", "jpg": "image/jpeg", "svg": "image/svg+xml"}.get(ext, "image/png")
        return f'![{title}](data:{mime};base64,{b64})'
    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", rep, md_body)


def render_toc(parts):
    lines = ["<h2>Table of Contents</h2>"]
    for p in parts:
        lines.append(f"<h3 class='toc-part'>Part {p['id']} — {p['title']}</h3>")
        lines.append("<ul class='toc'>")
        for n, t, s in p["chapters"]:
            status = f"<span class='st-{s}'>{s}</span>"
            anchor = f"chapter-{n:02d}"
            lines.append(f"<li><a href='#{anchor}'><b>Ch {n}.</b> {t}</a> {status}</li>")
        lines.append("</ul>")
    return "\n".join(lines)


def render_skeletons(skeleton, parts):
    """Render chapters 2..26 as skeletons using their §9 theses (fall back to yaml title)."""
    secs = []
    # order by part
    for p in parts:
        secs.append(f"<h3 class='parthead'>Part {p['id']} — {p['title']}</h3>")
        for n, t, s in p["chapters"]:
            if n == 1:
                continue  # ch1 is full text
            sk = skeleton.get(n, {})
            thesis = sk.get("thesis") or "<i>(thesis not yet drafted — see architecture §9)</i>"
            title = t
            name = sk.get("title")
            extra = f"<span class='archname'>(architecture title: {name})</span>" if name and name != t else ""
            secs.append(
                f"<section class='skeleton' id='chapter-{n:02d}'>"
                f"<h4>Ch {n}. {title} {extra} <span class='st-{s}'>[{s}]</span></h4>"
                f"<p>{thesis}</p></section>"
            )
    return "\n".join(secs)


DARK_CSS = """
:root{--bg:#0f1115;--fg:#e6e6e6;--muted:#9aa3ad;--accent:#7aa2f7;--line:#2a2f3a;--card:#171b23;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.7 -apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;}
.page{max-width:860px;margin:0 auto;padding:48px 40px 80px;}
h1{font-size:34px;line-height:1.25;margin:0 0 4px}
h2{font-size:26px;border-bottom:1px solid var(--line);padding-bottom:8px;margin-top:44px}
h3{font-size:20px;margin-top:32px}
h4{font-size:17px;margin-top:24px}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
p{margin:12px 0}
strong{color:#fff}
hr{border:none;border-top:1px solid var(--line);margin:36px 0}
code{background:#262b36;padding:2px 6px;border-radius:4px;font-family:ui-monospace,Menlo,monospace;font-size:0.92em}
pre{background:#0b0e13;border:1px solid var(--line);border-radius:8px;padding:16px;overflow-x:auto}
pre code{background:none;padding:0}
blockquote{margin:16px 0;padding:2px 16px;border-left:4px solid var(--accent);background:var(--card);border-radius:0 8px 8px 0}
table{border-collapse:collapse;margin:16px 0;width:100%}
th,td{border:1px solid var(--line);padding:8px 12px;text-align:left}
th{background:var(--card)}
img{max-width:100%;height:auto;border-radius:8px;margin:16px 0}
em{color:var(--muted)}
.titleblock{border-bottom:1px solid var(--line);padding-bottom:28px;margin-bottom:8px}
.subtitle{color:var(--muted);font-size:19px;margin-top:6px}
.meta{color:var(--muted);font-size:14px;margin-top:14px}
.toc-part{margin-bottom:6px}
ul.toc{padding-left:22px}
ul.toc li{margin:3px 0}
.st-drafted{color:#7ee787;font-weight:600}
.st-planned{color:var(--muted)}
.skel{color:var(--muted);font-size:0.88em}
.parthead{margin-top:36px;color:var(--accent)}
.skeleton{border:1px solid var(--line);border-radius:8px;padding:12px 16px;margin:12px 0;background:var(--card)}
.archname{color:var(--muted);font-size:0.85em;font-weight:400}
preface p{color:var(--fg)}
"""

LIGHT_CSS = """
:root{--bg:#ffffff;--fg:#1a1a1a;--muted:#5a6472;--accent:#1f5fbf;--line:#d8dde3;--card:#f6f8fa;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.7 -apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;}
.page{max-width:860px;margin:0 auto;padding:48px 40px 80px;}
h1{font-size:34px;line-height:1.25;margin:0 0 4px}
h2{font-size:26px;border-bottom:1px solid var(--line);padding-bottom:8px;margin-top:44px}
h3{font-size:20px;margin-top:32px}
h4{font-size:17px;margin-top:24px}
a{color:var(--accent);text-decoration:none}
p{margin:12px 0}
hr{border:none;border-top:1px solid var(--line);margin:36px 0}
code{background:#f0f2f5;padding:2px 6px;border-radius:4px;font-family:ui-monospace,Menlo,monospace;font-size:0.92em}
pre{background:#f6f8fa;border:1px solid var(--line);border-radius:8px;padding:16px;overflow-x:auto}
pre code{background:none;padding:0}
blockquote{margin:16px 0;padding:2px 16px;border-left:4px solid var(--accent);background:var(--card);border-radius:0 8px 8px 0}
table{border-collapse:collapse;margin:16px 0;width:100%}
th,td{border:1px solid var(--line);padding:8px 12px;text-align:left}
th{background:var(--card)}
img{max-width:100%;height:auto;border-radius:8px;margin:16px 0}
.titleblock{border-bottom:1px solid var(--line);padding-bottom:28px;margin-bottom:8px}
.subtitle{color:var(--muted);font-size:19px;margin-top:6px}
.meta{color:var(--muted);font-size:14px;margin-top:14px}
.st-drafted{color:#116329;font-weight:600}
.st-planned{color:var(--muted)}
.skel{color:var(--muted);font-size:0.88em}
.parthead{margin-top:36px;color:var(--accent)}
.skeleton{border:1px solid var(--line);border-radius:8px;padding:12px 16px;margin:12px 0;background:var(--card)}
.archname{color:var(--muted);font-size:0.85em;font-weight:400}
"""


def build_html(css):
    import markdown
    book_title, subtitle, parts = load_yaml_chapters()
    preface = load_preface()

    preface_html = "".join(f"<p>{p}</p>" for p in preface)

    parts_html = ""
    for p in parts:
        parts_html += f"<h3 class='parthead'>Part {p['id']} — {p['title']} <span class='skel'>({p['theme']})</span></h3>"
        parts_html += "<ul class='toc'>"
        for n, t, s in p["chapters"]:
            status = f"<span class='st-{s}'>{s}</span>"
            parts_html += f"<li><a href='#chapter-{n:02d}'><b>Ch {n}.</b> {t}</a> {status}</li>"
        parts_html += "</ul>"

    # Render EVERY chapter's full text, in book order (from book.yaml parts).
    sections = []
    for p in parts:
        for n, t, s in p["chapters"]:
            md, figs = load_chapter(n)
            kit = markdown.markdown(
                inline_base64(md, figs),
                extensions=["tables", "fenced_code", "attr_list", "md_in_html"],
            )
            sections.append(f"<section id='chapter-{n:02d}'><h2>Chapter {n}</h2>{kit}</section>")
    all_chapters_html = "\n\n<hr>\n\n".join(sections)

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{book_title}</title>
<style>{css}</style></head><body><div class="page">
<div class="titleblock">
<h1>{book_title}</h1>
<div class="subtitle">{subtitle}</div>
<div class="meta">A review artifact generated by <code>render/make_review.py</code> · {subprocess.run(['date','+%Y-%m-%d'],capture_output=True,text=True).stdout.strip()}</div>
</div>

<h2>Preface</h2>
<preface>{preface_html}</preface>

{render_toc(parts)}

<hr>

{all_chapters_html}

</div></body></html>"""
    return html


def main():
    # dark HTML
    dark_html = build_html(DARK_CSS)
    dark_path = os.path.join(BUILD, "review-dark.html")
    open(dark_path, "w", encoding="utf-8").write(dark_html)

    # light HTML (temp) -> PDF via chromium
    light_html = build_html(LIGHT_CSS)
    light_tmp = os.path.join(BUILD, "_review-light.html")
    open(light_tmp, "w", encoding="utf-8").write(light_html)

    chrome = find_chrome()
    if not chrome:
        print("WARNING: no chromium found; skipping PDF build. Run render/setup_environment.sh or install chromium.")
        print(f"Wrote dark HTML: {dark_path}")
        return 0
    pdf_path = os.path.join(BUILD, "review-light.pdf")
    r = subprocess.run(
        [chrome, "--headless", "--no-sandbox", "--disable-gpu",
         f"--print-to-pdf={pdf_path}", f"file://{light_tmp}"],
        capture_output=True, text=True,
    )
    if os.path.exists(pdf_path):
        print(f"Wrote light PDF: {pdf_path} ({os.path.getsize(pdf_path)} bytes)")
    else:
        print("PDF build failed:", r.stderr[-400:])
    print(f"Wrote dark HTML: {dark_path} ({os.path.getsize(dark_path)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
