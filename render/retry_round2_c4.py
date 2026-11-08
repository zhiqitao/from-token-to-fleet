#!/usr/bin/env python3
"""Round-2 MiMo c4: the pathological chunk. Chapter-boundary pieces at ~45K,
recursive re-split on <200-char (truncation) replies, floor 8K, medium effort.
Writes review/loop_v3/round_2/text_MiMo-V2.6-Flash-RL_c4.json
Usage: python3 render/retry_round2_c4.py
"""
import os, re, json, importlib.util

os.chdir("/home/ubuntu/hermes-work/from-token-to-fleet")
spec = importlib.util.spec_from_file_location("rl", "render/review_loop.py")
rl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rl)
chunks = rl.build_chunks()
os.environ["REVIEW_EFFORT"] = "medium"
model = "MiMo-V2.6-Flash-RL"
fp = "review/loop_v3/round_2/text_%s_c4.json" % model
TARGET = 45000
FLOOR = 8000


def review_piece(piece, depth=0):
    prompt = rl.PROMPT_V1 + "\n\n" + rl.TEXT_TASK + piece
    out = rl.chat(model, prompt)
    print("    %d chars (depth %d, piece %d)" % (len(out), depth, len(piece)), flush=True)
    if len(out) >= 200 or len(piece) <= FLOOR:
        return rl.parse_issues(out)
    bounds = [m.start() for m in re.finditer(r"\n(?=#{1,3} )", piece)]
    mid = len(piece) // 2
    if not bounds:
        return []
    b = min(bounds, key=lambda x: abs(x - mid))
    if b < 1000 or len(piece) - b < 1000:
        return []
    print("  -> re-split at %d (%d / %d)" % (b, b, len(piece) - b), flush=True)
    return review_piece(piece[:b], depth + 1) + review_piece(piece[b:], depth + 1)


c = chunks[4]
bounds = [0] + [m.start() for m in re.finditer(r"\n(?=#{1,3} )", c)] + [len(c)]
pieces = []
start = 0
for i in range(1, len(bounds)):
    if bounds[i] - start >= TARGET or i == len(bounds) - 1:
        pieces.append(c[start:bounds[i]])
        start = bounds[i]
print("c4: %d pieces %s" % (len(pieces), [len(x) for x in pieces]), flush=True)
all_issues = []
for pi, piece in enumerate(pieces):
    print("  piece %d (%d chars)" % (pi, len(piece)), flush=True)
    all_issues.extend(review_piece(piece))
open(fp, "w", encoding="utf-8").write(
    json.dumps(all_issues, ensure_ascii=False, indent=1))
print("wrote %s issues: %d" % (fp, len(all_issues)), flush=True)