#!/usr/bin/env python3
"""Post-process a tagged LaTeX PDF (lualatex + tagpdf):

1. Remove EMPTY Figure struct shells (a /Figure element with no /K content).
   pdfpages' \\includepdf creates one Figure per internal \\includegraphics
   call; the measurement boxes never ship out, so 5 of the 6 cover Figures
   are empty shells. Removal = drop the ref from the parent's /K array and
   drop the matching /ID entry from StructTreeRoot's IDTree; unused objects
   are dropped by the subsequent garbage-collecting save.
2. Replace any remaining file-path /Alt on a Figure with descriptive text
   (no-op when the .tex source already passes alt={...}).

Idempotent. Does not claim PDF/UA conformance.
Usage: fix_fig_struct.py in.pdf out.pdf
"""
import re, sys, pymupdf

ALT_MAP = {
    "../cover/cover_clean_front.pdf":
        "Front cover of From Token to Fleet: An AI Solution Architect's Handbook by Zhiqi Tao "
        "(first edition, 2026). Cream background with a faint grid; large left-aligned title FROM TOKEN "
        "in black over TO FLEET in navy above an orange-to-teal gradient rule; subtitle An AI Solution "
        "Architect's Handbook; a central diagram scaling left to right from one orange square labeled "
        "token through teal clusters to a 3x3 grid of navy squares labeled fleet; author and edition "
        "line at the bottom left.",
    "assets/spine-decision-loop.pdf":
        "The architect's decision loop, the book's spine: a circular flow running understand the request, "
        "characterize the workload, set constraints, design and size candidates, validate and defend with "
        "benchmark and TCO, then commit; an inner green loop returns a failed validation to design and size, "
        "and an outer red loop returns a committed architecture to understanding when the requirements change.",
    "assets/preface-trace.pdf":
        "Two ways to read the book. Left: a layer-by-layer path through Parts I to VI, building the "
        "substrate then the discipline. Right: a question-by-question path mapping six navigation prompts "
        "(token to cost, fits on one host, which phase binds, one host or fleet, who serves it, is it the "
        "right call) to the chapters that answer them.",
}


def gk(d, x, k):
    return d.xref_get_key(x, k)


def struct_kids(d, x):
    """Return (kind, [struct-kid xrefs]) for a /K value."""
    t, v = gk(d, x, "K")
    if t == "array":
        refs = [int(m.group(1)) for m in re.finditer(r"(\d+)\s+0\s+R", v)]
        return "array", refs
    if t == "xref":
        return "xref", [int(v.split()[0])]
    if t == "dict":  # pymupdf resolved an indirect MCR/struct dict
        return "dict", []
    return t, []


def is_orphan(d, x):
    t, v = gk(d, x, "K")
    if t in ("null", "", "nothing"):
        return True
    if t == "array" and len(v.strip()) <= 2:  # [ ] or empty
        return True
    return False


def walk(d, x, out, parent=None):
    t, s = gk(d, x, "S")
    s = s.lstrip("/") if t == "name" else ""
    rec = dict(xref=x, S=s, parent=parent)
    out.append(rec)
    if s == "" and parent is None:  # StructTreeRoot
        pass
    kind, kids = struct_kids(d, x)
    for k in kids:
        t2, _ = gk(d, k, "S")
        if t2 == "name":
            walk(d, k, out, x)


def idtree_nodes(d, x, seen=None):
    seen = seen or set()
    if x in seen:
        return []
    seen.add(x)
    t, v = gk(d, x, "Kids")
    if t == "array":
        nodes = []
        for m in re.finditer(r"(\d+)\s+0\s+R", v):
            nodes += idtree_nodes(d, int(m.group(1)), seen)
        return nodes
    if gk(d, x, "Names")[0] == "array":
        return [x]
    return []


def pdf_str(s):
    return "(" + s.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)") + ")"


def main(inpath, outpath):
    d = pymupdf.open(inpath)
    cat = d.pdf_catalog()
    root = int(gk(d, cat, "StructTreeRoot")[1].split()[0])
    elems = []
    walk(d, root, elems)

    # --- 1) empty Figure shells
    orphans = [e for e in elems
               if e["S"] == "Figure" and e["parent"] is not None
               and is_orphan(d, e["xref"])]
    orphan_ids = set()
    for o in orphans:
        t, v = gk(d, o["xref"], "ID")
        if t == "string":
            orphan_ids.add(v)
        # drop from parent /K array
        pt, pv = gk(d, o["parent"], "K")
        assert pt == "array", (o["xref"], pt, pv)
        kept = re.sub(r"(?<!\d)%d 0 R\s*" % o["xref"], "", pv)
        assert not re.search(r"(?<!\d)%d 0 R" % o["xref"], kept), kept
        d.xref_set_key(o["parent"], "K", "[" + kept.strip() + "]")
    # drop IDTree entries that point at removed elements (leave all other
    # nodes byte-identical; a node with no match is never rewritten)
    idtree_removed = 0
    pairs_before = pairs_after = 0
    st_t, st_v = gk(d, root, "IDTree")
    if st_t == "xref":
        orphan_xrefs = {o["xref"] for o in orphans}
        for node in idtree_nodes(d, int(st_v.split()[0])):
            t, v = gk(d, node, "Names")
            if t != "array" or len(v.strip()) <= 2:
                continue
            found = re.findall(r"\(([^()]*)\)\s*(\d+)\s+0\s+R", v)
            assert found, "unparseable IDTree Names: " + v[:120]
            pairs_before += len(found)
            keep = [(n, r) for n, r in found if int(r) not in orphan_xrefs]
            drop = len(found) - len(keep)
            pairs_after += len(keep)
            if drop:
                idtree_removed += drop
                d.xref_set_key(node, "Names",
                               "[ " + " ".join("(%s) %s 0 R" % (n, r) for n, r in keep) + " ]")
        assert pairs_before - pairs_after == idtree_removed
        assert pairs_after > 0, "IDTree would be empty"

    # --- 2) file-path Alt -> descriptive text (survivors only)
    alt_fixed = 0
    for e in elems:
        if e["S"] != "Figure" or e["xref"] in {o["xref"] for o in orphans}:
            continue
        t, v = gk(d, e["xref"], "Alt")
        if t == "string" and v in ALT_MAP:
            d.xref_set_key(e["xref"], "Alt", pdf_str(ALT_MAP[v]))
            alt_fixed += 1

    d.save(outpath, garbage=0, deflate=True)
    print("alt replaced:", alt_fixed,
          "| orphan Figure shells removed:", len(orphans),
          "| IDTree entries removed:", idtree_removed,
          "| IDTree pairs %d -> %d" % (pairs_before, pairs_after))
    for o in orphans:
        print("  removed xref", o["xref"], "ID", gk(d, o["xref"], "ID")[1])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])