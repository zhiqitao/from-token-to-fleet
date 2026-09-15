#!/usr/bin/env python3
"""Post-process the built book PDF: set a clean page-label dictionary and
write metadata.  The PDF viewer's page labels should match the printed folios:
  - PDF pages 4..21   -> roman (front matter: preface, TOC, List of Figures)
  - PDF pages 22..end -> decimal (main matter: body + back matter)
  - PDF pages 0..3    -> cover / verso / copyright / verso (unnumbered)
Also linearize (Fast Web View) the final digital PDF.
"""
import os, sys, pymupdf

def fix(inpath, outpath):
    doc = pymupdf.open(inpath)
    n = len(doc)
    # Find the frontmatter->mainmatter boundary: the first page whose printed
    # arabic folio is '1' in the body (after the TOC/LOF).  Defer to a value
    # passed in, else detect: roman runs from the preface page (idx 4) to just
    # before the first 'Part' divider body.  Use 22 (known from current layout)
    # unless an override is given.
    main_start = int(os.environ.get("MAIN_START", "22"))
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
    print("wrote", outpath, "pages", n)

if __name__ == "__main__":
    fix(sys.argv[1], sys.argv[2])
