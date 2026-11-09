#!/usr/bin/env python3
"""Round-3 MiMo ladder: c2/c4/c5 are stubs or shallow (23/1537/30 chars
for 174K/185K/104K inputs). Split each at a chapter boundary, review
halves at medium, merge into text_MiMo-V2.6-Flash-RL_cN.json.
Usage: python3 render/retry_round3_mimo_ladder.py
"""
import os, re, json, importlib.util

os.chdir("/home/ubuntu/hermes-work/from-token-to-fleet")
spec = importlib.util.spec_from_file_location("rl", "render/review_loop.py")
assert spec is not None and spec.loader is not None
rl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rl)
chunks = rl.build_chunks()
os.environ["REVIEW_EFFORT"] = "medium"
model = "MiMo-V2.6-Flash-RL"
TARGETS = [2, 4, 5]


def split_at_chapter(c):
    bounds = [m.start() for m in re.finditer(r"\n(?=#{1,3} )", c)]
    mid = len(c) // 2
    b = min(bounds, key=lambda x: abs(x - mid)) if bounds else mid
    if b < 3000 or len(c) - b < 3000:
        b = mid
    return c[:b], c[b:]


for ci in TARGETS:
    fp = "review/loop_v3/round_3/text_%s_c%d.json" % (model, ci)
    c = chunks[ci]
    h0, h1 = split_at_chapter(c)
    print("c%d split (%d / %d)" % (ci, len(h0), len(h1)), flush=True)
    issues = []
    for hi, half in enumerate([h0, h1]):
        out = rl.chat(model, rl.PROMPT_V1 + "\n\n" + rl.TEXT_TASK + half)
        print("  half %d: %d chars" % (hi, len(out)), flush=True)
        if len(out) < 200:
            q0, q1 = split_at_chapter(half)
            for qi, q in enumerate([q0, q1]):
                out2 = rl.chat(
                    model, rl.PROMPT_V1 + "\n\n" + rl.TEXT_TASK + q)
                print("    q%d: %d chars" % (qi, len(out2)), flush=True)
                issues.extend(rl.parse_issues(out2))
        else:
            issues.extend(rl.parse_issues(out))
    open(fp, "w", encoding="utf-8").write(
        json.dumps(issues, ensure_ascii=False, indent=1))
    print("wrote c%d issues: %d" % (ci, len(issues)), flush=True)