#!/usr/bin/env python3
"""Ornith c1..c4: recursive chapter-boundary split.
Start at ~45K pieces (medium); if a piece returns <200 chars (truncation),
split it at its nearest chapter boundary and retry; floor 8K (then accept failure).
Usage: python3 render/retry_ornith_quarters.py 1 2 3 4
"""
import os, re, sys, json, importlib.util

os.chdir("/home/ubuntu/hermes-work/from-token-to-fleet")
spec = importlib.util.spec_from_file_location("rl", "render/review_loop.py")
rl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rl)
chunks = rl.build_chunks()
os.environ["REVIEW_EFFORT"] = "medium"
model = "Ornith-1.5-122B"
TARGET = 45000
FLOOR = 8000


def review_piece(piece, depth=0):
    prompt = rl.PROMPT_V1 + "\n\n" + rl.TEXT_TASK + piece
    out = rl.chat(model, prompt)
    print("    %d chars (depth %d, piece %d)" % (len(out), depth, len(piece)), flush=True)
    if len(out) >= 200 or len(piece) <= FLOOR:
        return out, [rl.parse_issues(out)]
    bounds = [m.start() for m in re.finditer(r"\n(?=#{1,3} )", piece)]
    mid = len(piece) // 2
    if not bounds:
        return out, []  # cannot split further
    b = min(bounds, key=lambda x: abs(x - mid))
    if b < 1000 or len(piece) - b < 1000:
        return out, []
    print("  -> re-split at %d (%d / %d)" % (b, b, len(piece) - b), flush=True)
    o1, i1 = review_piece(piece[:b], depth + 1)
    o2, i2 = review_piece(piece[b:], depth + 1)
    merged = []
    for ii in i1 + i2:
        merged.extend(ii)
    return o1 + o2, [merged]


for ci in [int(x) for x in sys.argv[1:]]:
    fp = "review/loop_v3/round_1/text_%s_c%d.json" % (model, ci)
    c = chunks[ci]
    # initial pieces at ~TARGET via chapter boundaries
    bounds = [0] + [m.start() for m in re.finditer(r"\n(?=#{1,3} )", c)] + [len(c)]
    pieces = []
    start = 0
    for i in range(1, len(bounds)):
        if bounds[i] - start >= TARGET or i == len(bounds) - 1:
            pieces.append(c[start:bounds[i]])
            start = bounds[i]
    print("c%d: %d pieces %s" % (ci, len(pieces), [len(x) for x in pieces]), flush=True)
    all_issues = []
    for pi, piece in enumerate(pieces):
        print("  piece %d (%d chars)" % (pi, len(piece)), flush=True)
        _, iss = review_piece(piece)
        for ii in iss:
            all_issues.extend(ii)
    open(fp, "w", encoding="utf-8").write(
        json.dumps(all_issues, ensure_ascii=False, indent=1))
    print("wrote %s issues: %d" % (fp, len(all_issues)), flush=True)
print("ornith recursive split done", flush=True)