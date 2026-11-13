#!/usr/bin/env python3
"""Round-4 MiMo vision batch 2: 23-char TRUNCATED stub on
pages [112,113,128,130,134,136,143,144]. 4-image halves, recurse to
single pages on failure, merge every valid array, write vis_MiMo b2.
"""
import os, sys, json, base64

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import review_loop as rl

PAGES_DIR = os.path.join(rl.V3, "pages")
OUT = os.path.join(rl.V3, "round_4", "vis_MiMo-V2.6-Flash-RL_b2.json")
MODEL = "MiMo-V2.6-Flash-RL"
manifest = json.load(open(os.path.join(PAGES_DIR, "manifest.json")))
by_page = {m["page"]: m for m in manifest}


def call(pages):
    imgs = [base64.b64encode(open(os.path.join(
        PAGES_DIR, by_page[p]["file"]), "rb").read()).decode()
        for p in pages]
    prompt = rl.PROMPT_V1 + "\n\n" + rl.VISION_TASK + \
        "\nPages in this batch: %s" % pages
    out = rl.chat(MODEL, prompt, images=imgs, max_tokens=12000)
    arr = rl.parse_issues(out)
    ok = not out.startswith("[[NO-CONTENT") and len(out) > 100
    print(f"  pages {pages} -> {len(out)} chars, {len(arr)} issues, "
          f"{'VALID' if ok else 'STUB'}", flush=True)
    return ok, arr, out


def solve(pages, depth=0):
    """Return (ok, issues, note). Recurse on stub."""
    ok, arr, out = call(pages)
    if ok:
        return True, arr, ""
    if len(pages) == 1:
        return False, [], f"GAP: page {pages[0]} toxic (reasoning-only x4)"
    mid = len(pages) // 2
    l = solve(pages[:mid], depth + 1)
    r = solve(pages[mid:], depth + 1)
    return (l[0] or r[0]), l[1] + r[1], "; ".join(
        x for x in (l[2], r[2]) if x)


print("r4 b2 isolation start", flush=True)
ok, issues, note = solve([112, 113, 128, 130, 134, 136, 143, 144])
body = json.dumps(issues, ensure_ascii=False, indent=1)
if note:
    body += "\n\nCOVERAGE: partial — " + note
open(OUT, "w", encoding="utf-8").write(body)
print(f"WROTE b2: {len(issues)} issues, note={note or 'none'}", flush=True)
print("r4 b2 isolation done", flush=True)