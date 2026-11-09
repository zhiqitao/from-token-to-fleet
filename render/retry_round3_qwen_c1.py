#!/usr/bin/env python3
"""Round-3 Qwen c1 retry: split the 162881-char chunk at a chapter
boundary, review each half at medium, merge into
review/loop_v3/round_3/text_Qwen3.8-27B_c1.json
Usage: python3 render/retry_round3_qwen_c1.py
"""
import os, re, json, importlib.util

os.chdir("/home/ubuntu/hermes-work/from-token-to-fleet")
spec = importlib.util.spec_from_file_location("rl", "render/review_loop.py")
assert spec is not None and spec.loader is not None  # file exists on disk
rl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rl)
chunks = rl.build_chunks()
os.environ["REVIEW_EFFORT"] = "medium"
model = "Qwen3.8-27B"
fp = "review/loop_v3/round_3/text_%s_c1.json" % model

c = chunks[1]
bounds = [m.start() for m in re.finditer(r"\n(?=#{1,3} )", c)]
mid = len(c) // 2
b = min(bounds, key=lambda x: abs(x - mid))
if b < 3000 or len(c) - b < 3000:
    b = len(c) // 2
halves = [c[:b], c[b:]]
print("c1 split at %d (%d / %d)" % (b, b, len(c) - b), flush=True)
all_issues = []
for hi, half in enumerate(halves):
    prompt = rl.PROMPT_V1 + "\n\n" + rl.TEXT_TASK + half
    out = rl.chat(model, prompt)
    print("  half %d: %d chars" % (hi, len(out)), flush=True)
    if len(out) < 200:
        # one more split for the failing half
        bb = [m.start() for m in re.finditer(r"\n(?=#{1,3} )", half)]
        mm = len(half) // 2
        b2 = min(bb, key=lambda x: abs(x - mm)) if bb else len(half) // 2
        for qi, q in enumerate([half[:b2], half[b2:]]):
            out2 = rl.chat(model, rl.PROMPT_V1 + "\n\n" + rl.TEXT_TASK + q)
            print("    q%d: %d chars" % (qi, len(out2)), flush=True)
            all_issues.extend(rl.parse_issues(out2))
    else:
        all_issues.extend(rl.parse_issues(out))
open(fp, "w", encoding="utf-8").write(
    json.dumps(all_issues, ensure_ascii=False, indent=1))
print("wrote %s issues: %d" % (fp, len(all_issues)), flush=True)