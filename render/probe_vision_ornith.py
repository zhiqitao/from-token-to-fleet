#!/usr/bin/env python3
"""Probe which Ornith backend can actually do round-2 vision on 4-image
batches: 122B@max (round-1 veteran) vs 397B@medium (text champion).
Writes one real manifest batch ([39,40,91,110]) per candidate to
review/loop_v3/round_2/probe_<model>_<effort>.txt and prints a summary.
"""
import os, json, base64, importlib.util, time
os.chdir("/home/ubuntu/hermes-work/from-token-to-fleet")
spec = importlib.util.spec_from_file_location("rl", "render/review_loop.py")
rl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rl)
rl.MODEL_EP["Ornith-1.5-397B"] = "im-eglb"
rl.MODEL_EP["Ornith-1.5-122B"] = "im-eglb"
man = json.load(open("review/loop_v3/pages/manifest.json"))
pd = "review/loop_v3/pages"
PAGES = [39, 40, 91, 110]


def run(model, effort):
    batch = [m for m in man if m["page"] in PAGES]
    imgs = [base64.b64encode(open(os.path.join(pd, m["file"]), "rb").read()).decode()
            for m in batch]
    prompt = rl.PROMPT_V1 + "\n\n" + rl.VISION_TASK + \
        "\nPages in this batch: %s" % PAGES
    os.environ["REVIEW_EFFORT"] = effort
    t = time.time()
    out = rl.chat(model, prompt, images=imgs, max_tokens=12000)
    dt = time.time() - t
    tag = "review/loop_v3/round_2/probe_%s_%s.txt" % (
        model.replace("/", "_"), effort)
    open(tag, "w").write(out)
    head = out[:120].replace("\n", " ")
    print("%s@%s -> %d chars (%.0fs) | %s" % (model, effort, len(out), dt, head),
          flush=True)
    return len(out)


run("Ornith-1.5-122B", "max")
run("Ornith-1.5-397B", "medium")
print("probe done", flush=True)