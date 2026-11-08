#!/usr/bin/env python3
"""Round-2 vision for the Ornith slot on 397B, BATCH=4.

im-eglb caps the Ornith model group at 4 images per request (HTTP 400
"At most 4 image(s) may be provided"), so stage_vision's BATCH=8 fails.
Deletes the 5 forty-byte error files, then re-batches the 39 manifest
pages 4-at-a-time into vis_Ornith-1.5-397B_b{0..9}.json.
"""
import os, sys, json, base64, importlib.util
os.chdir("/home/ubuntu/hermes-work/from-token-to-fleet")
spec = importlib.util.spec_from_file_location("rl", "render/review_loop.py")
rl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rl)
rl.MODEL_EP["Ornith-1.5-397B"] = "im-eglb"
model = "Ornith-1.5-397B"
BATCH = 4
outdir = os.path.join(rl.V3, "round_2")
pages_dir = os.path.join(rl.V3, "pages")
# drop the HTTP-400 stubs
for bi in range(5):
    fp = os.path.join(outdir, "vis_%s_b%d.json" % (model, bi))
    if os.path.exists(fp) and "ERR HTTP Error 400" in open(fp).read():
        os.remove(fp)
        print("removed stub", os.path.basename(fp), flush=True)
manifest = json.load(open(os.path.join(pages_dir, "manifest.json")))
batches = [manifest[i:i + BATCH] for i in range(0, len(manifest), BATCH)]
print("%d pages -> %d batches of <=%d" % (len(manifest), len(batches), BATCH), flush=True)
for bi, batch in enumerate(batches):
    fp = os.path.join(outdir, "vis_%s_b%d.json" % (model, bi))
    if os.path.exists(fp):
        print("skip existing", os.path.basename(fp), flush=True)
        continue
    imgs = [base64.b64encode(open(os.path.join(pages_dir, m["file"]), "rb").read()).decode()
            for m in batch]
    pgs = [m["page"] for m in batch]
    prompt = rl.PROMPT_V1 + "\n\n" + rl.VISION_TASK + "\nPages in this batch: %s" % pgs
    print("[vision] %s batch %d pages %s" % (model, bi, pgs), flush=True)
    out = rl.chat(model, prompt, images=imgs, max_tokens=12000)
    open(fp, "w", encoding="utf-8").write(out)
    print("  -> %d chars" % len(out), flush=True)
print("ornith vision (397B, batch=4) done", flush=True)