#!/usr/bin/env python3
"""Generate the KDP interior-only archive from a plain build.

The plain archive ('render/build/from-token-to-fleet-v<date>-plain.pdf') opens on
the full-bleed page-0 cover by design (the DIGITAL edition). For a print run we
need a clean interior that starts at the half-title block and keeps correct page
parity, with the cover supplied separately as cover_premium_front/wrap.pdf.

Usage:
    python3 render/make_interior.py [plain_archive] [interior_out]

Defaults to the v20260913 plain build and a '-plain-interior.pdf' sibling.
Drops the cover page (page 0) and renumbers bookmarks/pages so the printed folio
starts at 1. Idempotent and cheap to rerun after any rebuild.
"""
import os
import sys
import fitz  # PyMuPDF


def main():
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    kdp = "--kdp" in sys.argv   # PRINT-01: strip bookmarks + disallowed metadata
    src = args[0] if args else os.path.join(
        repo, "render/build/from-token-to-fleet-v20260913-plain.pdf")
    out = args[1] if len(args) > 1 else src.replace(".pdf", "-kdp-split.pdf" if kdp else "-interior.pdf")

    d = fitz.open(src)
    n = d.page_count
    if n < 2:
        raise SystemExit(f"not enough pages in {src}: {n}")
    # Confirm page 0 is really the cover (it is an includepdf of the front cover).
    first_txt = d[0].get_text().strip()
    if "FROM TOKEN" not in first_txt and "TO FLEET" not in first_txt:
        raise SystemExit(
            "page 0 does not carry the cover title; refusing to drop it.")

    interior = fitz.open()
    interior.insert_pdf(d, from_page=1, to_page=n - 1)

    if not kdp:
        # Digital/readable edition: copy bookmarks (shifted -1, drop p0 entries).
        toc = []
        for lvl, title, page in d.get_toc():
            if page <= 1:
                continue
            toc.append([lvl, title, page - 1])
        interior.set_toc(toc)
        interior.set_metadata(d.metadata)
        label = "interior (digital, with bookmarks)"
    else:
        # KDP manuscript: no bookmark tree, no disallowed interactive/metadata
        # objects (PRINT-01). Keep searchable text; set clean minimal metadata.
        interior.set_toc([])
        interior.set_metadata({
            "title": "From Token to Fleet: An AI Solution Architect's Handbook",
            "author": "Zhiqi Tao",
            "subject": "AI systems architecture",
            "keywords": "",
            "creator": "",
            "producer": "",
            "creationDate": "", "modDate": ""})
        label = "interior (KDP, no bookmarks)"
    interior.save(out, garbage=4, deflate=True)
    print(f"{label}: {interior.page_count} pages (from {n} incl. cover)")
    print(f"saved {os.path.relpath(out, repo)}")


if __name__ == "__main__":
    main()
