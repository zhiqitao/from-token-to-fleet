#!/usr/bin/env python3
"""Retry one slice of a review chunk at a given effort, merge into the file.
Usage: python3 render/retry_slice.py <model> <chunk_idx> <start> <end> <effort>
Example: python3 render/retry_slice.py MiMo-V2.6-Flash-RL 4 90524 131840 medium
(slice bounds = quarter1 of half0: half0=chunk[:90524], q1=half0[49208:])
"""
import os, sys, json, importlib.util

os.chdir("/home/ubuntu/hermes-work/from-token-to-fleet")
model, ci, s, e, effort = (sys.argv[1], int(sys.argv[2]), int(sys.argv[3]),
                           int(sys.argv[4]), sys.argv[5])
spec = importlib.util.spec_from_file_location("rl", "render/review_loop.py")
rl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rl)
chunks = rl.build_chunks()
os.environ["REVIEW_EFFORT"] = effort
piece = chunks[ci][s:e]
print("slice %d[%d:%d] = %d chars, effort=%s" % (ci, s, e, len(piece), effort), flush=True)
prompt = rl.PROMPT_V1 + "\n\n" + rl.TEXT_TASK + piece
out = rl.chat(model, prompt)
print("out: %d chars" % len(out), flush=True)
new = rl.parse_issues(out)
fp = "review/loop_v3/round_1/text_%s_c%d.json" % (model, ci)
existing = []
if os.path.exists(fp):
    try:
        existing = json.loads(open(fp, encoding="utf-8").read().split("\nCOVERAGE")[0])
    except Exception:
        existing = rl.parse_issues(open(fp, encoding="utf-8").read())
merged = existing + new
open(fp, "w", encoding="utf-8").write(json.dumps(merged, ensure_ascii=False, indent=1))
print("wrote %s total: %d (new %d)" % (fp, len(merged), len(new)), flush=True)