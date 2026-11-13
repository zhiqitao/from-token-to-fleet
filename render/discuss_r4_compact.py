#!/usr/bin/env python3
"""Re-run the round-4 discuss stage with a COMPACT register.

The full-stage run exhausted the shared 65536 reasoning+content window on all
4 models ([[TRUNCATED at 65536]] stubs) because the merged register was
220K chars at reasoning_effort=max. This variant sends only the 8 common
findings + 67 unique P0/P1 findings (21.5K chars) and keeps effort=max.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import review_loop as rl  # noqa: E402

D = "/home/ubuntu/hermes-work/from-token-to-fleet/review/loop_v3/round_4"
blob = open(os.path.join(D, "discuss_compact_register.json"), encoding="utf-8").read()
task = rl.DISCUSS_TASK.replace("{ROUND}", "4")
task += ("\n\nNOTE: the register below is COMPACT — all 8 common findings plus\n"
         "unique P0/P1 findings only. Answer for THIS register.\n")

for model in rl.MODELS:
    fp = os.path.join(D, "discuss_%s.json" % model)
    if os.path.exists(fp):
        print("exists, skip:", model, flush=True)
        continue
    print("[discuss-compact]", model, flush=True)
    out = rl.chat(model, rl.PROMPT_V1 + "\n\n" + task + blob, max_tokens=65536)
    open(fp, "w", encoding="utf-8").write(out)
    stub = out.startswith("[[TRUNCATED") or out.startswith("[[ERR")
    print("  -> %d chars%s" % (len(out), "  STUB/ERR" if stub else ""), flush=True)
print("discuss-compact done", flush=True)