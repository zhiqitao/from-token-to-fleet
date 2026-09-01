#!/usr/bin/env python3
"""preprocess_md.py — deterministic numbered figure/table captions for the whole book.

Usage: python3 preprocess_md.py CHAPTER_NO FILE.md

Rewrites each figure/table marker into a numbered caption that is visible and
unique in the rendered PDF/EPUB WITHOUT relying on LaTeX float counters or CJK
fonts. Prefixes are ASCII ('Fig N.M' / 'Tab N.M') to avoid missing-glyph issues.

Marker styles supported:
  Style A (legacy):   *FIG-IDENT-abc* — caption     /  **TAB-IDENT-abc** — caption
  Style B (new):      *Fig. `ident` — caption*

For figures the caption is emitted directly under the image (no #fig auto-label)
so pandoc renders it as plain strong text with no double-numbering.
"""
import re, sys

FIG_A = re.compile(r'^\*{1,2}FIG-([A-Za-z0-9_-]+)\**\s*[\u2014-]\s*(.*)$')
TAB_A = re.compile(r'^\*{1,2}TAB-([A-Za-z0-9_-]+)\**\s*[\u2014-]\s*(.*)$')
FIG_B = re.compile(r'^\*Fig\.\s+`([A-Za-z0-9_-]+)`\s*[\u2014-]\s*(.*?)\*?\s*$')
IMG = re.compile(r'^(!\[[^\]]*\]\([^)]+\))\s*$')


def process(text, chapter):
    lines = text.split('\n')
    out = []
    i = 0
    n = len(lines)
    figno = 0
    tabno = 0
    while i < n:
        line = lines[i]
        s = line.strip()
        if s.startswith('*Fig.'):
            m = FIG_B.match(s)
            if m:
                figno += 1
                cap = m.group(2).strip()
                j = len(out) - 1
                while j >= 0 and out[j].strip() == '':
                    j -= 1
                prev = out[j].strip() if j >= 0 else ''
                im = IMG.match(prev)
                if im:
                    out[j] = prev + '\n\n**Fig %d.%d** %s' % (int(chapter), figno, cap)
                    i += 1
                    continue
                else:
                    out.append(line); i += 1; continue
        elif s.startswith('*FIG') or s.startswith('**FIG'):
            m = FIG_A.match(s)
            if m:
                figno += 1
                cap = m.group(2).strip()
                j = len(out) - 1
                while j >= 0 and out[j].strip() == '':
                    j -= 1
                prev = out[j].strip() if j >= 0 else ''
                im = IMG.match(prev)
                if im:
                    out[j] = prev + '\n\n**Fig %d.%d** %s' % (int(chapter), figno, cap)
                    i += 1
                    continue
                else:
                    out.append(line); i += 1; continue
        elif s.startswith('*TAB') or s.startswith('**TAB'):
            m = TAB_A.match(s)
            if m:
                tabno += 1
                cap = m.group(2).strip()
                out.append('\n**Tab %d.%d** %s\n' % (int(chapter), tabno, cap))
                i += 1
                continue
        out.append(line)
        i += 1
    return '\n'.join(out)


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) >= 2 and args[0].isdigit():
        chapter, path = args[0], args[1]
    else:
        chapter, path = '0', (args[0] if args else '-')
    data = sys.stdin.read() if path == '-' else open(path, encoding='utf-8').read()
    print(process(data, chapter), end='')
