#!/usr/bin/env python3
"""MiMo c4 half 0 (90,524 chars) still truncates at medium.
Split it at chapter boundaries into two ~45K quarters, review at medium,
and MERGE into the existing c4 file (which already holds half 1's issues).
"""
import os, re, json, importlib.util

os.chdir("/home/ubuntu/hermes-work/from-token-to-fleet")
spec = importlib.util.spec_from_file_location("rl", "render/review_loop.py")
rl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rl)
chunks = rl.build_chunks()
os.environ["REVIEW_EFFORT"] = "medium"
model = "MiMo-V2.6-Flash-RL"
fp = "review/loop_v3/round_1/text_%s_c4.json" % model

c = chunks[4]
half0 = c[:90524]  # the truncating half from retry_c4_split.py
mid = len(half0) // 2
bounds = [m.start() for m in re.finditer(r"\n(?=#{1,3} )", half0)]
b = min(bounds, key=lambda x: abs(x - mid)) if bounds else mid
q1, q2 = half0[:b], half0[b:]
print("quarters: %d / %d (split at %d)" % (len(q1), len(q2), b), flush=True)

new_issues = []
for qi, q in enumerate([q1, q2]):
    prompt = rl.PROMPT_V1 + "\n\n" + rl.TEXT_TASK + q
    out = rl.chat(model, prompt)
    print("  quarter %d: %d chars" % (qi, len(out)), flush=True)
    new_issues.extend(rl.parse_issues(out))

# merge with existing (half 1) issues
existing = []
if os.path.exists(fp):
    try:
        existing = json.loads(open(fp, encoding="utf-8").read().split("\nCOVERAGE")[0])
    except Exception:
        existing = rl.parse_issues(open(fp, encoding="utf-8").read())
merged = existing + new_issues
open(fp, "w", encoding="utf-8").write(json.dumps(merged, ensure_ascii=False, indent=1))
print("wrote %s total issues: %d (was %d, new %d)" % (
    fp, len(merged), len(existing), len(new_issues)), flush=True)