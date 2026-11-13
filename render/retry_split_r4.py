#!/usr/bin/env python3
"""Round-4 split-retry for [[TRUNCATED at 65536]] text chunks.

Full-chunk retry first; if the output is still <200 chars or carries the
truncation marker, split at the nearest chapter boundary and recurse
(floor 40K), then write ONE merged JSON array of parsed issues.

Every real request is gated behind a tiny PONG probe (im-eglb sheds
connections after a burst of large outputs — Errno 104), and requests
are paced 30s apart.

Usage: python3 render/retry_split_r4.py MODEL cidx [cidx ...] [MODEL cidx ...]
"""
import os, re, sys, json, time, importlib.util

os.chdir("/home/ubuntu/hermes-work/from-token-to-fleet")
spec = importlib.util.spec_from_file_location("rl", "render/review_loop.py")
rl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rl)
os.environ["REVIEW_EFFORT"] = "max"
os.environ.setdefault("CHAT_TIMEOUT", "300")
chunks = rl.build_chunks()
FLOOR = 40000
R4 = os.path.join(rl.V3, "round_4")


def probe() -> bool:
    try:
        out = rl.chat(cur_model, "Reply with exactly: PONG",
                      max_tokens=2000, retries=1)
        return bool(out) and not out.startswith("[[ERR") and "PONG" in out.upper()
    except Exception:
        return False


def wait_window(max_wait=5400) -> bool:
    t0 = time.time()
    while time.time() - t0 < max_wait:
        if probe():
            return True
        time.sleep(90)
    return False


def good(path) -> bool:
    if not os.path.exists(path):
        return False
    t = open(path, encoding="utf-8").read()
    return len(t) >= 200 and not t.startswith("[[TRUNC") \
        and not t.startswith("[[ERR") and len(rl.parse_issues(t)) >= 1


def review(piece, depth=0):
    if not wait_window():
        print("    window never opened — abort piece", flush=True)
        return "[[ERR window]]"
    prompt = rl.PROMPT_V1 + "\n\n" + rl.TEXT_TASK + piece
    out = rl.chat(cur_model, prompt)
    time.sleep(30)
    print("    %d chars (depth %d, piece %d)%s"
          % (len(out), depth, len(piece),
             " TRUNC" if out.startswith("[[TRUNC") else ""), flush=True)
    if (len(out) >= 200 and not out.startswith("[[TRUNC")) \
            or len(piece) <= FLOOR:
        return out
    bounds = [m.start() for m in re.finditer(r"\n(?=#{1,3} )", piece)]
    mid = len(piece) // 2
    if not bounds:
        return out
    b = min(bounds, key=lambda x: abs(x - mid))
    if b < 2000 or len(piece) - b < 2000:
        return out
    print("  -> split at %d (%d / %d)" % (b, b, len(piece) - b), flush=True)
    o1 = review(piece[:b], depth + 1)
    o2 = review(piece[b:], depth + 1)
    if len(o1) < 200 and len(o2) < 200:
        return o1
    merged = []
    for o in (o1, o2):
        merged.extend(rl.parse_issues(o))
    return json.dumps(merged, ensure_ascii=False, indent=1)


args = sys.argv[1:]
groups, cur = [], None
for a in args:
    if a.isdigit():
        cur[1].append(int(a))
    else:
        cur = [a, []]
        groups.append(cur)

for model, idxs in groups:
    cur_model = model
    for ci in idxs:
        fp = os.path.join(R4, "text_%s_c%d.json" % (model, ci))
        if good(fp):
            print("%s c%d already good, skip" % (model, ci), flush=True)
            continue
        if os.path.exists(fp):
            os.remove(fp)
        print("%s c%d: %d chars — full chunk first"
              % (model, ci, len(chunks[ci]), ), flush=True)
        out = review(chunks[ci])
        open(fp, "w", encoding="utf-8").write(out)
        print("wrote %s (%d chars, %d issues)"
              % (fp, len(out), len(rl.parse_issues(out))), flush=True)
print("split-retry done", flush=True)