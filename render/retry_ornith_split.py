#!/usr/bin/env python3
"""Ornith chunks c1..cN: too big for one call (65536 truncation at max/high/medium).
Split each at the nearest chapter boundary and review each half at medium.
Usage: python3 render/retry_ornith_split.py 1 2 3
Safe to run while review_loop's single pass works on OTHER chunks (distinct files).
"""
import os, re, sys, json, importlib.util

os.chdir("/home/ubuntu/hermes-work/from-token-to-fleet")
spec = importlib.util.spec_from_file_location("rl", "render/review_loop.py")
rl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rl)
chunks = rl.build_chunks()
os.environ["REVIEW_EFFORT"] = "medium"
model = "Ornith-1.5-122B"

for ci in [int(x) for x in sys.argv[1:]]:
    fp = "review/loop_v3/round_1/text_%s_c%d.json" % (model, ci)
    if os.path.exists(fp) and os.path.getsize(fp) > 200:
        print("skip c%d (good)" % ci, flush=True)
        continue
    c = chunks[ci]
    mid = len(c) // 2
    bounds = [m.start() for m in re.finditer(r"\n(?=#{1,3} )", c)]
    b = min(bounds, key=lambda x: abs(x - mid)) if bounds else mid
    h1, h2 = c[:b], c[b:]
    print("c%d split at %d halves: %d / %d" % (ci, b, len(h1), len(h2)), flush=True)
    outs = []
    for hi, h in enumerate([h1, h2]):
        prompt = rl.PROMPT_V1 + "\n\n" + rl.TEXT_TASK + h
        out = rl.chat(model, prompt)
        print("  half %d: %d chars" % (hi, len(out)), flush=True)
        outs.append(out)
    arr = []
    cov = []
    for o in outs:
        arr.extend(rl.parse_issues(o))
        m = re.search(r"COVERAGE:.*", o)
        if m:
            cov.append(m.group(0))
    payload = json.dumps(arr, ensure_ascii=False, indent=1)
    if cov:
        payload += "\n" + "\n".join(cov)
    open(fp, "w", encoding="utf-8").write(payload)
    print("wrote %s issues: %d" % (fp, len(arr)), flush=True)
print("ornith split retry done", flush=True)