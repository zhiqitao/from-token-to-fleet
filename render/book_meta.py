#!/usr/bin/env python3
"""Live metadata for the deliverable PDF.

Review-fleet prompts used to hardcode the book's page count and file size. Those
literals went stale as the book grew (a round-12 reviewer was told "519 pages"
while holding the 553-page build), and the mismatch was reported back as a
scope/input complaint instead of a review. Always read the numbers off the PDF
being sent, never from a constant.
"""
import os
import re
import subprocess

DEFAULT_PDF = ("/home/ubuntu/hermes-work/from-token-to-fleet/render/build/"
               "from-token-to-fleet-v20260913.pdf")


def _pages_pdfinfo(path):
    out = subprocess.run(["pdfinfo", path], capture_output=True, text=True,
                         timeout=120).stdout
    m = re.search(r"^Pages:\s+(\d+)", out, re.M)
    return int(m.group(1)) if m else None


def _pages_pypdf(path):
    from pypdf import PdfReader
    return len(PdfReader(path).pages)


def pdf_pages(path=DEFAULT_PDF):
    """Page count of the actual file, or None if it cannot be determined."""
    for probe in (_pages_pdfinfo, _pages_pypdf):
        try:
            n = probe(path)
            if n:
                return n
        except Exception:
            pass
    return None


def pdf_mb(path=DEFAULT_PDF):
    """File size in MB (1 decimal), or None."""
    try:
        return round(os.path.getsize(path) / 1e6, 1)
    except OSError:
        return None


def describe(path=DEFAULT_PDF):
    """Human/LLM-facing phrase, e.g. '553 pages, 9.8 MB'."""
    n, mb = pdf_pages(path), pdf_mb(path)
    if n and mb:
        return "%d pages, %s MB" % (n, mb)
    if n:
        return "%d pages" % n
    return "unknown length"


if __name__ == "__main__":
    print(describe())
