#!/usr/bin/env python3
"""Round-4 Qwen text retry: chunks 0-4 returned 23-char stubs (65536 shared
window). Split each at a chapter boundary, review halves at medium, fall back
to quarters, and write parsed issues to
review/loop_v3/round_4/text_Qwen3.8-27B_cN.json
Chunk 5 was healthy (20145 chars) and is left untouched.
Usage: python3 render/retry_round4_qwen.py
"""
import os, re, json, importlib.util

os.chdir("/home/ubuntu/hermes-work/from-token-to-fleet")
spec = importlib.util.spec_from_file_location("rl", "render/review_loop.py")
assert spec is not None and spec.loader is not None
rl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rl)
chunks = rl.build_chunks()
os.environ["REVIEW_EFFORT"] = "medium"
model = "Qwen3.8-27B"
outdir = "review/loop_v3/round_4"


def split_at_heading(text):
    bounds = [m.start() for m in re.finditer(r"\n(?=#{1,3} )", text)]
    mid = len(text) // 2
    if not bounds:
        return len(text) // 2
    b = min(bounds, key=lambda x: abs(x - mid))
    if b < 3000 or len(text) - b < 3000:
        b = len(text) // 2
    return b


def review_piece(text, depth=0):
    """Return parsed issues for text; split further on truncation."""
    out = rl.chat(model, rl.PROMPT_V1 + "\n\n" + rl.TEXT_TASK + text)
    print("    depth %d: %d chars" % (depth, len(out)), flush=True)
    if len(out) >= 200 or depth >= 2:
        return rl.parse_issues(out)
    b = split_at_heading(text)
    issues = []
    for q in (text[:b], text[b:]):
        issues.extend(review_piece(q, depth + 1))
    return issues


for ci in range(5):
    fp = os.path.join(outdir, "text_%s_c%d.json" % (model, ci))
    if os.path.exists(fp) and os.path.getsize(fp) > 400:
        print("c%d exists, skip" % ci, flush=True)
        continue
    c = chunks[ci]
    b = split_at_heading(c)
    print("c%d split at %d (%d / %d)" % (ci, b, b, len(c) - b), flush=True)
    all_issues = []
    for hi, half in enumerate((c[:b], c[b:])):
        print("  half %d (%d chars)" % (hi, len(half)), flush=True)
        all_issues.extend(review_piece(half))
    open(fp, "w", encoding="utf-8").write(
        json.dumps(all_issues, ensure_ascii=False, indent=1))
    print("wrote %s issues: %d" % (fp, len(all_issues)), flush=True)
print("round-4 Qwen retry done", flush=True)