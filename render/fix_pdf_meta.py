#!/usr/bin/env python3
"""Post-process the built book PDF: set a clean page-label dictionary and
write metadata.  The PDF viewer's page labels should match the printed folios:
  - PDF pages 4..21   -> roman (front matter: preface, TOC, List of Figures)
  - PDF pages 22..end -> decimal (main matter: body + back matter)
  - PDF pages 0..3    -> cover / verso / copyright / verso (unnumbered)
Also linearize (Fast Web View) the final digital PDF.
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
        rect = None
        for tp in toc_pages:
            r = doc[tp].search_for(title)
            if r:
                rect = r[0]; break
        if rect is None:
            key = " ".join(title.split()[:4])
            for tp in toc_pages:
                r = doc[tp].search_for(key)
                if r:
                    rect = r[0]; break
        if rect is not None:
            for tp in toc_pages:
                if doc[tp].search_for(title) or doc[tp].search_for(" ".join(title.split()[:4])):
                    doc[tp].insert_link(
                        {"kind": pymupdf.LINK_GOTO, "from": rect, "page": dest,
                         "to": pymupdf.Point(0, 0)})
                    added += 1
                    break
    return added


def fix(inpath, outpath):
    doc = pymupdf.open(inpath)
    n = len(doc)
    # Restore clickable table-of-contents entries (suppressed by PDF/UA tagging).
    n_toc = add_toc_links(doc)
    # Find the frontmatter->mainmatter boundary automatically: the first page
    # whose printed folio is the arabic numeral '1' (frontmatter folios are
    # roman; \mainmatter resets the page counter to 1).  Search forward from the
    # preface so early title/cover pages are skipped.  MAIN_START env can still
    # override for debugging.
    import re
    def printed_folio(idx):
        lines = [l.strip() for l in doc[idx].get_text().split("\n") if l.strip()]
        for l in lines:
            if re.fullmatch(r"[ivxlcdm]+", l):
                return l
        for l in reversed(lines):
            if re.fullmatch(r"\d{1,3}", l):
                return l
        return None
    main_start = int(os.environ.get("MAIN_START", "0"))
    if not main_start:
        for idx in range(8, 40):
            if printed_folio(idx) == "1":
                main_start = idx
                break
        if not main_start:
            main_start = 22  # fallback
    catalog = doc.pdf_catalog()
    nums = []
    nums.append("4 << /S /r /St 1 >>")
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
    doc.save(outpath, garbage=4, deflate=True, clean=True)
    print("wrote", outpath, "pages", n, "| TOC links:", n_toc)

if __name__ == "__main__":
    fix(sys.argv[1], sys.argv[2])
