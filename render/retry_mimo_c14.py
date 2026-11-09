#!/usr/bin/env python3
"""Round-2 MiMo c1/c4: full-chunk retry with recursive chapter-boundary
split on truncation.

MiMo blows the shared 65536 output window (reasoning + JSON) on these two
162K/185K chunks -> 23-char [[TRUNCATED]] stubs. Try the full chunk once
(c0/c2 passed on plain retry); if <200 chars, split at the nearest chapter
boundary and recurse (floor 40K). Full-chunk success writes the raw output
(stage_text convention); a split writes one merged JSON array of parsed
issues so parse_issues sees a single list.
Deletes the two stubs first (skip-existing would otherwise freeze them).
Usage: python3 render/retry_mimo_c14.py 1 4
"""
import os, re, sys, json, importlib.util
os.chdir("/home/ubuntu/hermes-work/from-token-to-fleet")
spec = importlib.util.spec_from_file_location("rl", "render/review_loop.py")
rl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rl)
chunks = rl.build_chunks()
os.environ["REVIEW_EFFORT"] = "max"
model = "MiMo-V2.6-Flash-RL"
FLOOR = 40000


def review(piece, depth=0):
    prompt = rl.PROMPT_V1 + "\n\n" + rl.TEXT_TASK + piece
    out = rl.chat(model, prompt)
    print("    %d chars (depth %d, piece %d)" % (len(out), depth, len(piece)),
          flush=True)
    if len(out) >= 200 or len(piece) <= FLOOR:
        return out
    bounds = [m.start() for m in re.finditer(r"\n(?=#{1,3} )", piece)]
    mid = len(piece) // 2
    if not bounds:
        return out
    b = min(bounds, key=lambda x: abs(x - mid))
    if b < 2000 or len(piece) - b < 2000:
        return out
    print("  -> split at %d (%d / %d)" % (b, b, len(piece) - b), flush=True)
    o1 = review(piece[:b], depth + 1)
    o2 = review(piece[b:], depth + 1)
    if len(o1) < 200 and len(o2) < 200:
        return o1
    # merge into ONE JSON array of parsed issues
    merged = []
    for o in (o1, o2):
        merged.extend(rl.parse_issues(o))
    return json.dumps(merged, ensure_ascii=False, indent=1)


for ci in [int(x) for x in sys.argv[1:]]:
    fp = "review/loop_v3/round_3/text_%s_c%d.json" % (model, ci)
    if os.path.exists(fp):
        cur = open(fp).read()
        if len(cur) >= 200:
            print("c%d already good (%d chars), skip" % (ci, len(cur)), flush=True)
            continue
        os.remove(fp)
        print("c%d stub removed (%d chars)" % (ci, len(cur)), flush=True)
    c = chunks[ci]
    print("c%d: %d chars — full chunk first" % (ci, len(c)), flush=True)
    out = review(c)
    open(fp, "w", encoding="utf-8").write(out)
    print("wrote %s (%d chars)" % (fp, len(out)), flush=True)
print("mimo c1/c4 retry done", flush=True)