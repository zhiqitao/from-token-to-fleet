#!/usr/bin/env python3
"""Paced completion of MiniMax-M3.1-Flash round-4 files.

im-eglb sheds connections (Errno 104) after a burst of large outputs —
an output-quota window. This runner gates every real request behind a
tiny PONG probe, waits for the window to open, paces requests 180s
apart, and writes the same files stage_text/stage_vision would.
"""
import os, sys, time, json, base64

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("CHAT_TIMEOUT", "240")
import review_loop as rl

MODEL = "MiniMax-M3.1-Flash"
V3, R4 = rl.V3, os.path.join(rl.V3, "round_4")


def probe() -> bool:
    try:
        out = rl.chat(MODEL, "Reply with exactly: PONG",
                      max_tokens=2000, retries=1)
        return bool(out) and not out.startswith("[[ERR") and "PONG" in out.upper()
    except Exception:
        return False


def wait_window(max_wait: int = 5400) -> bool:
    t0 = time.time()
    while time.time() - t0 < max_wait:
        if probe():
            return True
        time.sleep(90)
    return False


def main():
    chunks = rl.build_chunks()
    man = json.load(open(os.path.join(V3, "pages", "manifest.json")))
    BATCH = 8
    batches = [man[i:i + BATCH] for i in range(0, len(man), BATCH)]

    def bad(path):
        """Missing, or an [[ERR ...]] stub from a shed connection."""
        if not os.path.exists(path):
            return True
        with open(path, encoding="utf-8") as f:
            return f.read(8).startswith("[[ERR")

    miss_c = [i for i in range(len(chunks))
              if bad(os.path.join(R4, f"text_{MODEL}_c{i}.json"))]
    miss_b = [b for b in range(len(batches))
              if bad(os.path.join(R4, f"vis_{MODEL}_b{b}.json"))]
    print(f"missing text chunks: {miss_c} | missing vision batches: {miss_b}",
          flush=True)
    for i in miss_c:
        if not wait_window():
            print(f"c{i}: window never opened — stop", flush=True)
            return
        out = rl.chat(MODEL, rl.PROMPT_V1 + rl.TEXT_TASK + chunks[i],
                      retries=2)
        with open(os.path.join(R4, f"text_{MODEL}_c{i}.json"), "w") as f:
            f.write(out)
        print(f"c{i} -> {len(out)} chars", flush=True)
        time.sleep(180)
    for b in miss_b:
        if not wait_window():
            print(f"b{b}: window never opened — stop", flush=True)
            return
        batch = batches[b]
        imgs = [base64.b64encode(
                    open(os.path.join(V3, "pages", m["file"]), "rb"
                         ).read()).decode()
                for m in batch]
        pgs = [m["page"] for m in batch]
        prompt = rl.PROMPT_V1 + "\n\n" + rl.VISION_TASK + \
            "\nPages in this batch: %s" % pgs
        out = rl.chat(MODEL, prompt,
                      images=imgs, max_tokens=12000, retries=2)
        with open(os.path.join(R4, f"vis_{MODEL}_b{b}.json"), "w") as f:
            f.write(out)
        print(f"b{b} -> {len(out)} chars", flush=True)
        time.sleep(180)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()