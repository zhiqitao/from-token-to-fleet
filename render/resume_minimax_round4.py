#!/usr/bin/env python3
"""Self-healing resume of the MiniMax-M3.1-Flash round-4 review.

The im-eglb MiniMax upstream went unresponsive mid-run; review_loop.py writes
44-byte "[[ERR ...]]" files for failed chunks/batches and then SKIPS them on
re-run, so this driver deletes error files, waits for a live model, reruns the
stages, and repeats until everything is clean or the deadline passes.
"""
import glob
import json
import os
import subprocess
import time
import urllib.request

REPO = "/home/ubuntu/hermes-work/from-token-to-fleet"
OUT = os.path.join(REPO, "review/loop_v3/round_4")
MODEL = "MiniMax-M3.1-Flash"
DEADLINE = time.time() + 16 * 3600


def load_key():
    for line in open(os.path.expanduser("~/.hermes/im-eglb.env")):
        if line.startswith("IM_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


KEY = load_key()


def probe():
    """PONG + a sustained-generation mini-request; both must succeed."""
    for payload, to in (
        ({"model": MODEL, "messages": [{"role": "user",
          "content": "Reply with exactly: PONG"}],
          "max_tokens": 8000, "temperature": 0}, 60),
        ({"model": MODEL, "messages": [{"role": "user",
          "content": "Summarize in one sentence: " + "KV cache reuse lowers prefill cost. " * 1200}],
          "max_tokens": 4000, "temperature": 0, "reasoning_effort": "max"}, 240),
    ):
        req = urllib.request.Request(
            "https://api-im.eglb.intel.com/v1/chat/completions",
            data=json.dumps(payload).encode(),
            headers={"Authorization": "Bearer " + KEY,
                     "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=to) as r:
                d = json.load(r)
            if not (d.get("choices") or [{}])[0].get("message", {}).get("content"):
                return False
        except Exception as e:
            print(f"  probe fail: {e!r}", flush=True)
            return False
    return True


def error_files():
    out = []
    for fp in sorted(glob.glob(os.path.join(OUT, "*MiniMax*.json"))):
        try:
            head = open(fp, encoding="utf-8").read(60)
        except OSError:
            continue
        if head.startswith("[[ERR") or os.path.getsize(fp) < 100:
            out.append(fp)
    return out


def clean():
    for fp in error_files():
        print("  removing error file:", os.path.basename(fp), flush=True)
        os.remove(fp)


def run_stage(stage):
    print(f"[{time.strftime('%H:%M:%S')}] running stage: {stage}", flush=True)
    subprocess.run(["python3", "render/review_loop.py", stage, "4", MODEL],
                   cwd=REPO, timeout=6 * 3600)


def wait_live():
    while time.time() < DEADLINE:
        if probe():
            print(f"[{time.strftime('%H:%M:%S')}] model LIVE", flush=True)
            return True
        print(f"[{time.strftime('%H:%M:%S')}] model down; sleeping 300s", flush=True)
        time.sleep(300)
    return False


def summary():
    def parse(text):
        dec = json.JSONDecoder()
        import re
        for m in re.finditer(r"\[", text):
            try:
                arr, _ = dec.raw_decode(text[m.start():])
            except json.JSONDecodeError:
                continue
            if isinstance(arr, list) and arr and isinstance(arr[0], dict):
                return arr
        return []
    print("=== FINAL STATE ===", flush=True)
    for kind in ("text", "vis"):
        n, sv = 0, {}
        files = sorted(glob.glob(os.path.join(OUT, f"{kind}_MiniMax*.json")))
        for fp in files:
            txt = open(fp, encoding="utf-8").read()
            if txt.startswith("[[ERR"):
                print("STILL-FAILED:", os.path.basename(fp), flush=True)
                continue
            for i in parse(txt):
                n += 1
                s = str(i.get("severity", "?"))
                sv[s] = sv.get(s, 0) + 1
        print(f"{kind}: files={len(files)} issues={n} severity={sv}", flush=True)


round_no = 0
while time.time() < DEADLINE:
    round_no += 1
    print(f"--- resume round {round_no} ---", flush=True)
    clean()
    if not wait_live():
        print("DEADLINE hit while waiting for model", flush=True)
        break
    run_stage("text")
    clean()
    if not wait_live():
        break
    run_stage("vision")
    if not error_files():
        print("ALL CLEAN", flush=True)
        break
    print("still have error files; back off 10 min", flush=True)
    time.sleep(600)

summary()