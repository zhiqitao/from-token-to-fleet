#!/usr/bin/env python3
"""Post-process the built book PDF: set a clean page-label dictionary and
write metadata. The PDF viewer's labels follow the printed folios. Detect
Roman and decimal numbering starts from marginal folio text rather than a
fixed physical-page offset. Leading unnumbered pages have empty labels.
The final file is compressed; this script does not claim PDF/UA conformance.
"""
import os, sys, pymupdf

def add_toc_links(doc):
    """Inject clickable chapter/part links onto the Contents pages.

    The build uses \\DocumentMetadata{testphase=latest} (PDF/UA tagging), which
    suppresses hyperref's automatic table-of-contents link annotations (body
    cross-references are unaffected).  We therefore re-add the TOC links here,
    mapping every visible Contents entry to the PDF page its chapter/part starts
    on, using the document outline as the ground truth.
    """
    toc_pages = [p for p in range(len(doc)) if "Contents" in doc[p].get_text()[:200]]
    if not toc_pages:
        return 0
    outlines = [(t[1], t[2] - 1) for t in doc.get_toc() if t[0] in (1, 2)]
    added = 0
    for title, dest in outlines:
        # Full-title match first; fall back to the leading words (a long chapter
        # title may wrap across lines on the Contents page and won't match whole).
        match = None
        keys = []
        for key in (title, " ".join(title.split()[:4])):
            for variant in (key, key.replace("'", "’"), key.replace("’", "'")):
                if variant not in keys:
                    keys.append(variant)
        for key in keys:
            for tp in toc_pages:
                rectangles = doc[tp].search_for(key)
                if rectangles:
                    match = (tp, rectangles[0])
                    break
            if match is not None:
                break
        if match is not None:
            tp, rect = match
            doc[tp].insert_link(
                {"kind": pymupdf.LINK_GOTO, "from": rect, "page": dest,
                 "to": pymupdf.Point(0, 0)})
            added += 1
    return added


def add_figure_links(doc):
    """Restore List of Figures links by exact printed figure identifier.

    Match caption labels, not mutable short-title wording or assumed folio
    offsets. Keep native links and make repeated post-processing idempotent.
    """
    import re
    targets = {}
    lists = []
    for number, page in enumerate(doc):
        text = page.get_text()
        lines = [line for block in page.get_text('dict')['blocks']
                 for line in block.get('lines', [])]
        if 'List of Figures' in text[:200]:
            lists.append(number)
        for line in lines:
            value = ''.join(span['text'] for span in line['spans']).strip()
            match = re.match(r'^figure\s+(\d+(?:\.\d+)?|[A-Z]\.\d+)\s*[.:]', value, re.I)
            if match:
                key = match.group(1).upper()
                if key in targets:
                    raise ValueError(f'Ambiguous figure caption label: {key}')
                targets[key] = number
    added = 0
    for number in lists:
        page = doc.reload_page(doc[number])
        existing = page.get_links()
        rows = []
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines', []):
                value = ''.join(span['text'] for span in line['spans']).strip()
                match = re.match(r'^(\d+\.\d+|[A-Z]\.\d+|\d+(?=\s*$))\b', value)
                if match and line['bbox'][0] < 170:
                    rows.append((match.group(1).upper(), pymupdf.Rect(line['bbox'])))
        rows.sort(key=lambda row: row[1].y0)
        for index, (key, box) in enumerate(rows):
            if key not in targets:
                raise ValueError(f'No caption target for List of Figures entry {key}')
            bottom = rows[index + 1][1].y0 - 1 if index + 1 < len(rows) else min(page.rect.height - 82, box.y1 + 18)
            rect = pymupdf.Rect(box.x0, box.y0, page.rect.width - 80, max(box.y1, bottom))
            if any(link.get('kind') == pymupdf.LINK_GOTO and
                   link.get('page') == targets[key] and
                   pymupdf.Rect(link['from']).intersects(rect) for link in existing):
                continue
            page.insert_link({'kind': pymupdf.LINK_GOTO, 'from': rect,
                              'page': targets[key], 'to': pymupdf.Point(0, 0)})
            added += 1
    return added


def fix(inpath, outpath):
    doc = pymupdf.open(inpath)
    n = len(doc)
    # Restore clickable table-of-contents entries (suppressed by PDF/UA tagging).
    n_toc = add_toc_links(doc)
    n_figures = add_figure_links(doc)
    # Find the frontmatter->mainmatter boundary automatically: the first page
    # whose printed folio is the arabic numeral '1' (frontmatter folios are
    # roman; \mainmatter resets the page counter to 1).  Search forward from the
    # preface so early title/cover pages are skipped.  MAIN_START env can still
    # override for debugging.
    import re
    def printed_folio(idx):
        page = doc[idx]
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines', []):
                top = line['bbox'][1]
                if not (top < 70 or top > page.rect.height - 82):
                    continue
                text = ''.join(span['text'] for span in line['spans']).strip()
                if re.fullmatch(r'[ivxlcdm]+|\d{1,3}', text):
                    return text
        return None
    scan_end = min(40, len(doc))
    roman_start = next((idx for idx in range(scan_end)
                        if printed_folio(idx) == 'i'), None)
    if roman_start is None:
        raise ValueError('Cannot identify the first printed Roman folio')
    main_start = int(os.environ.get("MAIN_START", "0"))
    if not main_start:
        main_start = next((idx for idx in range(roman_start + 1, scan_end)
                           if printed_folio(idx) == '1'), None)
    if main_start is None or not roman_start < main_start < len(doc):
        raise ValueError('Cannot identify a valid main-matter numbering start')
    catalog = doc.pdf_catalog()
    nums = ['0 << /P () >>']
    nums.append(f"{roman_start} << /S /r /St 1 >>")
    nums.append(f"{main_start} << /S /D /St 1 >>")
    pagelabels = "<< /Nums [ %s ] >>" % " ".join(nums)
    xref = doc.get_new_xref()
    doc.update_object(xref, pagelabels)
    doc.xref_set_key(catalog, "PageLabels", "%d 0 R" % xref)
    # Linearize / Fast Web View
    doc.set_metadata({
        "title": doc.metadata.get("title") or "From Token to Fleet",
        "author": doc.metadata.get("author") or "Zhiqi Tao",
    })
    # clean=False: MuPDF content-stream cleaning strips the empty BDC/EMC
    # pairs tagpdf emits for empty text/structure elements, which orphans
    # their marked-content references (dangling MCRs) in the struct tree.
    doc.save(outpath, garbage=4, deflate=True, clean=False)
    print("wrote", outpath, "pages", n, "| TOC links:", n_toc,
          "| List of Figures links:", n_figures)

if __name__ == "__main__":
    fix(sys.argv[1], sys.argv[2])
