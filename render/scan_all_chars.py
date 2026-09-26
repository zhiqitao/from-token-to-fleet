#!/usr/bin/env python3
"""scan_all_chars.py — authoritative char-level text-collision scan across all figures.

Uses rawdict per-char bounding boxes (tight, no ascender/descender padding) so that
genuine glyph collisions surface while word-bbox padding false-positives vanish.
Reports figures with any overlapping chars from DIFFERENT logical text spans
(same-span chars compose one word, so adjacent letters within a word are ignored).

Usage: python3 scan_all_chars.py
"""
import pymupdf, os, itertools

ROOT = os.path.join(os.path.dirname(__file__), '..', 'design', 'manuscript')

def char_boxes(page):
    """Yield (x0,y0,x1,y1, ch, spanid) for every char; spanid groups chars by
    originating text run so intra-word adjacency is ignored."""
    out = []
    for bidx, block in enumerate(page.get_text('rawdict')['blocks']):
        for line in block.get('lines', []):
            for span in line.get('spans', []):
                sid = (bidx, id(span))
                for ch in span.get('chars', []):
                    b = ch['bbox']
                    out.append((b[0], b[1], b[2], b[3], ch['c'], sid))
    return out

def overlap(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])

def main():
    figs = []
    for dirpath, _, files in os.walk(ROOT):
        for f in files:
            if f.lower().endswith('.pdf') and f.lower().startswith('fig-'):
                figs.append(os.path.join(dirpath, f))
    figs.sort()

    findings = {}
    for path in figs:
        page = pymupdf.open(path)[0]
        cs = char_boxes(page)
        hits = []
        for a, b in itertools.combinations(cs, 2):
            if a[5] == b[5]:
                continue  # same span
            if overlap(a[:4], b[:4]):
                hits.append((round(a[0]), round(a[1]), a[4], b[4]))
        name = os.path.basename(path)
        findings[name] = hits
        pdoc = page.parent
        if pdoc:
            pdoc.close()

    flagged = {k: v for k, v in findings.items() if v}
    clean = [k for k, v in findings.items() if not v]
    print(f"figures scanned: {len(findings)}")
    print(f"char-collision clean: {len(clean)}")
    print(f"flagged: {len(flagged)}")
    print("\n=== CHAR-COLLISION FLAGGED (real glyph overlap) ===")
    for name, hits in sorted(flagged.items()):
        print(f"\n{name}  ({len(hits)} char overlaps)")
        # group by location
        locs = {}
        for x0, y0, ca, cb in hits:
            key = (x0 // 40, y0 // 30)
            locs.setdefault(key, []).append((x0, y0, ca, cb))
        for key, lst in sorted(locs.items()):
            x0, y0, ca, cb = lst[0]
            print(f"    ~({x0},{y0}) '{ca}' vs '{cb}'  (+{len(lst)-1} more)")

if __name__ == '__main__':
    main()
