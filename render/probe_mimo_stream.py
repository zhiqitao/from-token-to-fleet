#!/usr/bin/env python3
"""Test whether streaming survives the 300s connection reset on im-eglb/MiMo.

Hypothesis: a 300s IDLE (or total) timeout in the path kills non-streaming
long generations at exactly ~301s. Streaming sends continuous deltas; if the
timeout is idle-based, streaming survives.
"""
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
        "reasoning_effort": "max", "stream": True}

t0 = time.time()
content_parts = []
reason_parts = []
last_byte = t0
first_event = None
try:
    req = urllib.request.Request(ms.ENDPOINTS["im-eglb"] + "/chat/completions",
                                data=json.dumps(body).encode(), headers=h)
    resp = urllib.request.urlopen(req, timeout=900)
    for raw in resp:
        now = time.time()
        if first_event is None and raw.strip():
            first_event = now - t0
        last_byte = now
        line = raw.decode("utf-8", "replace").strip()
        if not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if data == "[DONE]":
            break
        try:
            obj = json.loads(data)
        except json.JSONDecodeError:
            continue
        for ch in obj.get("choices") or []:
            delta = ch.get("delta") or {}
            if delta.get("content"):
                content_parts.append(delta["content"])
            if delta.get("reasoning_content"):
                reason_parts.append(delta["reasoning_content"])
    total = time.time() - t0
    print(f"STREAM SUCCESS [{total:.0f}s] first_event={first_event:.1f}s "
          f"content={sum(len(x) for x in content_parts)} chars "
          f"reasoning={sum(len(x) for x in reason_parts)} chars", flush=True)
    json.dump({"content": "".join(content_parts),
               "reasoning_len": sum(len(x) for x in reason_parts),
               "elapsed_s": total},
              open("review/loop_v3/mimo_r1_stream.json", "w"),
              ensure_ascii=False, indent=1)
    print("saved review/loop_v3/mimo_r1_stream.json", flush=True)
except Exception as e:
    print(f"STREAM FAIL [{time.time()-t0:.0f}s] {type(e).__name__}: {e} "
          f"(last_byte_at {last_byte-t0:.0f}s)", flush=True)