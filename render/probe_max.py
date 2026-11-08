#!/usr/bin/env python3
"""Probe: does Ornith at MAX reasoning survive a ~45K piece?
Prints output length + issue count; writes NOTHING.
Usage: python3 render/probe_max.py <chunk_idx> <piece_idx>
"""
import os, re, sys, importlib.util

os.chdir("/home/ubuntu/hermes-work/from-token-to-fleet")
spec = importlib.util.spec_from_file_location("rl", "render/review_loop.py")
rl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rl)
chunks = rl.build_chunks()
os.environ["REVIEW_EFFORT"] = "max"
model = "Ornith-1.5-122B"
TARGET = 45000

ci, pi = int(sys.argv[1]), int(sys.argv[2])
c = chunks[ci]
bounds = [0] + [m.start() for m in re.finditer(r"\n(?=#{1,3} )", c)] + [len(c)]
pieces = []
start = 0
for i in range(1, len(bounds)):
    if bounds[i] - start >= TARGET or i == len(bounds) - 1:
        pieces.append(c[start:bounds[i]])
        start = bounds[i]
piece = pieces[pi]
print("probe: c%d piece %d = %d chars, effort=max" % (ci, pi, len(piece)), flush=True)
prompt = rl.PROMPT_V1 + "\n\n" + rl.TEXT_TASK + piece
out = rl.chat(model, prompt)
print("RESULT: %d chars, issues: %d" % (len(out), len(rl.parse_issues(out))), flush=True)