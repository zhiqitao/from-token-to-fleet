#!/usr/bin/env python3
"""Round-2 vision for the Ornith slot on 122B, BATCH=4.

Probe verdict: 397B vision returns reasoning-only / degenerate output at
both max and medium effort -> unusable; 122B@max returns valid JSON+COVERAGE
(round-1 veteran, 19/19). im-eglb caps the Ornith group at 4 images/request,
so BATCH=4 (10 batches over the 39-page manifest).
Deletes the 10 garbage vis_Ornith-1.5-397B_b*.json first so merge never
double-counts a page; output: vis_Ornith-1.5-122B_b{0..9}.json (ALIASES
already globs the 122B prefix into the Ornith slot).
"""
import os, glob, json, base64, importlib.util
os.chdir("/home/ubuntu/hermes-work/from-token-to-fleet")
spec = importlib.util.spec_from_file_location("rl", "render/review_loop.py")
rl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rl)
rl.MODEL_EP["Ornith-1.5-122B"] = "im-eglb"  # dropped from MODELS, still valid
model = "Ornith-1.5-122B"
BATCH = 4
outdir = os.path.join(rl.V3, "round_2")
pages_dir = os.path.join(rl.V3, "pages")
for fp in glob.glob(os.path.join(outdir, "vis_Ornith-1.5-397B_b*.json")):
    os.remove(fp)
    print("removed garbage", os.path.basename(fp), flush=True)
manifest = json.load(open(os.path.join(pages_dir, "manifest.json")))
batches = [manifest[i:i + BATCH] for i in range(0, len(manifest), BATCH)]
print("%d pages -> %d batches of <=%d on %s" % (
    len(manifest), len(batches), BATCH, model), flush=True)
for bi, batch in enumerate(batches):
    fp = os.path.join(outdir, "vis_%s_b%d.json" % (model, bi))
    if os.path.exists(fp):
        print("skip existing", os.path.basename(fp), flush=True)
        continue
    imgs = [base64.b64encode(open(os.path.join(pages_dir, m["file"]), "rb").read()).decode()
            for m in batch]
    pgs = [m["page"] for m in batch]
    prompt = rl.PROMPT_V1 + "\n\n" + rl.VISION_TASK + \
        "\nPages in this batch: %s" % pgs
    print("[vision] %s batch %d pages %s" % (model, bi, pgs), flush=True)
    out = rl.chat(model, prompt, images=imgs, max_tokens=12000)
    open(fp, "w", encoding="utf-8").write(out)
    print("  -> %d chars" % len(out), flush=True)
print("ornith vision (122B, batch=4) done", flush=True)