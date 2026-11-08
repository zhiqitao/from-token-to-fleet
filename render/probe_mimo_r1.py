#!/usr/bin/env python3
"""Reproduce the exact R1 MiMo call; capture per-attempt error detail."""
import os, json, sys, time, urllib.request

os.chdir("/home/ubuntu/hermes-work/from-token-to-fleet")
sys.path.insert(0, "render")
import importlib.util
spec = importlib.util.spec_from_file_location("ms", "render/methodology_study.py")
ms = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ms)

B = ms.BUNDLE
prompt = ms.R1_PROMPT % (B["master_instructions"], B["rounds"]["R1_20261030"],
                          B["rounds"]["R7_20261104"], B["rounds"]["LOOP8_core"])
print("prompt chars:", len(prompt), flush=True)

h = {"Content-Type": "application/json", "Authorization": "Bearer " + ms.IM_KEY}
body = {"model": "MiMo-V2.6-Flash-RL",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 16000, "temperature": 0.3,
        "reasoning_effort": "max"}

for attempt in range(4):
    t0 = time.time()
    try:
        req = urllib.request.Request(ms.ENDPOINTS["im-eglb"] + "/chat/completions",
                                    data=json.dumps(body).encode(), headers=h)
        r = json.load(urllib.request.urlopen(req, timeout=900))
        m = r["choices"][0]["message"]
        c = m.get("content") or ""
        print(f"attempt {attempt}: SUCCESS [{time.time()-t0:.0f}s] "
              f"finish={r['choices'][0].get('finish_reason')} content={len(c)} chars",
              flush=True)
        out = "review/loop_v3/mimo_r1_retry.json"
        json.dump({"content": c}, open(out, "w"), ensure_ascii=False, indent=1)
        print("saved", out, flush=True)
        break
    except Exception as e:
        print(f"attempt {attempt}: FAIL [{time.time()-t0:.0f}s] "
              f"{type(e).__name__}: {e}", flush=True)
        time.sleep(10)