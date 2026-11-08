#!/usr/bin/env python3
"""Ornith c1..c4 on Ornith-1.5-397B (im-eglb), reasoning_effort=max.

122B failed/truncated even at 80K halves -> switch the slot to 397B.
Try the FULL chunk first; if the reply is truncated (<200 chars), fall back
to recursive chapter-boundary split at ~45K pieces (floor 8K).
Output: review/loop_v3/round_1/text_Ornith-1.5-397B_c{ci}.json
Usage: python3 render/retry_ornith397.py 1 2 3 4
"""
import os, re, sys, json, importlib.util
os.chdir("/home/ubuntu/hermes-work/from-token-to-fleet")
spec = importlib.util.spec_from_file_location("rl", "render/review_loop.py")
rl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rl)
rl.MODEL_EP["Ornith-1.5-397B"] = "im-eglb"  # not in review_loop MODELS
chunks = rl.build_chunks()
os.environ["REVIEW_EFFORT"] = "max"   # highest reasoning tier on im-eglb
model = "Ornith-1.5-397B"
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
    print("c%d: %d chars — trying full chunk first" % (ci, len(c)), flush=True)
    out, iss = review_piece(c)
    all_issues = []
    for ii in iss:
        all_issues.extend(ii)
    open(fp, "w", encoding="utf-8").write(
        json.dumps(all_issues, ensure_ascii=False, indent=1))
    print("wrote %s issues: %d" % (fp, len(all_issues)), flush=True)
print("ornith397 done", flush=True)