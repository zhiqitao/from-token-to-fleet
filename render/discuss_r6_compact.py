#!/usr/bin/env python3
"""Round-6 discuss with the COMPACT register (all 32 common + unique P0/P1).
Full register (1145 findings) would exhaust the 65536 window as in rounds 4-5.
effort=max, max_tokens=65536, exists-skip, stub detection."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import review_loop as rl  # noqa: E402

D = "/home/ubuntu/hermes-work/from-token-to-fleet/review/loop_v3/round_6"
blob = open(os.path.join(D, "discuss_compact_register.json"), encoding="utf-8").read()
task = rl.DISCUSS_TASK.replace("{ROUND}", "6")
task += ("\n\nNOTE: the register below is COMPACT — all common findings plus\n"
         "unique P0/P1 findings only (issue text truncated at 300 chars).\n"
         "Answer for THIS register.\n")

for model in rl.MODELS:
    fp = os.path.join(D, "discuss_%s.json" % model)
    if os.path.exists(fp):
        print("exists, skip:", model, flush=True)
        continue
    print("[discuss-compact-r6]", model, flush=True)
    out = rl.chat(model, rl.PROMPT_V1 + "\n\n" + task + blob, max_tokens=65536)
    open(fp, "w", encoding="utf-8").write(out)
    stub = out.startswith("[[TRUNCATED") or out.startswith("[[ERR") or out.startswith("[[NO-CONTENT")
    print("  -> %d chars%s" % (len(out), "  STUB/ERR" if stub else ""), flush=True)
print("discuss-compact-r6 done", flush=True)