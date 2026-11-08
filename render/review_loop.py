#!/usr/bin/env python3
"""4-model book review loop (round-based).

Stages (one round = review/loop_v3/round_N/):
  text    — 4 models, blind independent full-manuscript pass, chunked,
            max reasoning (im-eglb 'max' / qwen38 'xhigh'), streaming.
  vision  — 4 models, figure pages rendered from the built PDF (150 dpi),
            semantic + legibility audit per review prompt v1 §2.7.
  merge   — synthesize: common (>=2 models) vs unique vs disagreement register.
  discuss — 4 models cross-critique the merged register + propose prompt edits.

Usage: python3 render/review_loop.py <text|vision|merge|discuss> <round>
"""
import os
import re
import sys
import json
import time
import glob
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V3 = os.path.join(REPO, "review/loop_v3")
PROMPT_V1 = open(os.path.join(V3, "review_prompt_v1.md"), encoding="utf-8").read()

MODELS = ["MiMo-V2.6-Flash-RL", "DeepSeek-V4.1-Flash",
          "Ornith-1.5-122B", "Qwen3.8-27B"]
ENDPOINTS = {"im-eglb": "https://api-im.eglb.intel.com/v1",
             "qwen38": "http://100.105.225.59:30000/v1"}
MODEL_EP = {m: "im-eglb" for m in MODELS}
MODEL_EP["Qwen3.8-27B"] = "qwen38"


def load_key():
    for line in open(os.path.expanduser("~/.hermes/im-eglb.env")):
        if line.startswith("IM_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


IM_KEY = load_key()
CHUNK_LIMIT = 190000  # chars per chunk (proven to fit all 4 models)


def chat(model, prompt, images=None, max_tokens=32768, retries=5):
    """Streaming chat; streaming is required on im-eglb (300s idle reset on
    non-streaming long generations). reasoning_effort: max (im-eglb) / xhigh
    (qwen38 wrapper)."""
    ep = ENDPOINTS[MODEL_EP[model]]
    h = {"Content-Type": "application/json"}
    if MODEL_EP[model] == "im-eglb" and IM_KEY:
        h["Authorization"] = "Bearer " + IM_KEY
    if images:
        content = [{"type": "text", "text": prompt}]
        for b64 in images:
            content.append({"type": "image_url",
                            "image_url": {"url": "data:image/png;base64," + b64}})
    else:
        content = prompt
    effort = os.environ.get("REVIEW_EFFORT")
    if not effort:
        effort = "max" if MODEL_EP[model] == "im-eglb" else "xhigh"
    if MODEL_EP[model] == "qwen38" and effort not in ("xhigh", "medium", "low"):
        effort = "medium"  # qwen38 wrapper enum: xhigh/medium/low only
    body = {"model": model,
            "messages": [{"role": "user", "content": content}],
            "max_tokens": max_tokens, "temperature": 0.3, "stream": True,
            "reasoning_effort": effort}
    last = None
    for attempt in range(retries):
        parts, reason = [], []
        finish = None
        try:
            req = urllib.request.Request(ep + "/chat/completions",
                                        data=json.dumps(body).encode(), headers=h)
            resp = urllib.request.urlopen(req, timeout=900)
            for raw in resp:
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
                    if ch.get("finish_reason"):
                        finish = ch["finish_reason"]
                    d = ch.get("delta") or {}
                    if d.get("content"):
                        parts.append(d["content"])
                    if d.get("reasoning_content"):
                        reason.append(d["reasoning_content"])
            c = "".join(parts)
            if finish == "length":
                # reasoning+content hit the cap -> output is TRUNCATED mid-stream
                # (observed: a register cut mid-"evidence":). Retry once at 65536.
                if body["max_tokens"] < 65536:
                    body = dict(body, max_tokens=65536)
                    last = RuntimeError("truncated at %d, retrying at 65536"
                                        % max_tokens)
                    time.sleep(3)
                    continue
                return "[[TRUNCATED at 65536]] " + c
            if not c and reason:
                c = "[[NO-CONTENT: reasoning only]]"
            return c or ""
        except Exception as e:
            last = e
            time.sleep(5 * (attempt + 1))
    return f"[[ERR {last}]]"


def build_chunks():
    """Split manuscript md files in order into <=CHUNK_LIMIT char chunks."""
    files = sorted(glob.glob(os.path.join(
        REPO, "design/manuscript/**/*.md"), recursive=True))
    chunks, cur = [], ""
    for f in files:
        t = open(f, encoding="utf-8").read()
        # strip image payloads (alt kept) to save tokens; vision pass handles pixels
        t = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"[FIGURE: \1]", t)
        if len(cur) + len(t) > CHUNK_LIMIT and cur:
            chunks.append(cur)
            cur = t
        else:
            cur += "\n\n" + t
    if cur:
        chunks.append(cur)
    return chunks


TEXT_TASK = """REVIEW TASK — blind independent pass over the manuscript chunk below.
Apply the review standard above. Output ONLY a JSON array of issues (schema:
{id, severity: P0|P1|P2|P3, confidence, page_hint, chapter, quoted_clause,
observed, evidence, root_cause, correction, acceptance_test}). Include the
source operator (~, ≈, ≤, =) in quoted_clause for numeric findings. If none:
[]. Do not invent issues; only what the chunk justifies. Also output a final
line outside the JSON: COVERAGE: <what you actually checked in this chunk>.

MANUSCRIPT CHUNK:
"""

VISION_TASK = """REVIEW TASK — figure audit. The images are rendered pages
(150 dpi) of the built PDF containing figures. For EACH figure on these pages:
(1) semantic check: do drawn labels/numbers match the caption and prose claims
visible on the page? (2) legibility at print size: any label too small,
clipped, overlapping, or unreadable? (3) grayscale distinguishability.
Output ONLY a JSON array: {id, page, figure, severity, issue, evidence,
acceptance_test}. If none: []. Final line outside JSON: COVERAGE: <pages and
figures actually inspected>.
"""


def stage_text(round_no):
    outdir = os.path.join(V3, "round_%d" % round_no)
    os.makedirs(outdir, exist_ok=True)
    chunks = build_chunks()
    print("chunks:", [len(c) for c in chunks], flush=True)
    for model in MODELS:
        reg = []
        for ci, chunk in enumerate(chunks):
            fp = os.path.join(outdir, "text_%s_c%d.json" % (
                model.replace("/", "_"), ci))
            if os.path.exists(fp):
                reg.append(open(fp, encoding="utf-8").read())
                continue
            prompt = PROMPT_V1 + "\n\n" + TEXT_TASK + chunk
            print(f"[text] {model} chunk {ci} ({len(chunk)} chars)", flush=True)
            out = chat(model, prompt)
            open(fp, "w", encoding="utf-8").write(out)
            print(f"  -> {len(out)} chars", flush=True)
            reg.append(out)
    print("text stage done", flush=True)


def stage_vision(round_no):
    outdir = os.path.join(V3, "round_%d" % round_no)
    os.makedirs(outdir, exist_ok=True)
    pages_dir = os.path.join(V3, "pages")
    manifest = json.load(open(os.path.join(pages_dir, "manifest.json")))
    BATCH = 8
    batches = [manifest[i:i + BATCH]
               for i in range(0, len(manifest), BATCH)]
    import base64
    for model in MODELS:
        for bi, batch in enumerate(batches):
            fp = os.path.join(outdir, "vis_%s_b%d.json" % (
                model.replace("/", "_"), bi))
            if os.path.exists(fp):
                continue
            imgs = [base64.b64encode(open(
                os.path.join(pages_dir, m["file"]), "rb").read()).decode()
                for m in batch]
            pgs = [m["page"] for m in batch]
            prompt = PROMPT_V1 + "\n\n" + VISION_TASK + \
                "\nPages in this batch: %s" % pgs
            print(f"[vision] {model} batch {bi} pages {pgs}", flush=True)
            out = chat(model, prompt, images=imgs, max_tokens=12000)
            open(fp, "w", encoding="utf-8").write(out)
            print(f"  -> {len(out)} chars", flush=True)
    print("vision stage done", flush=True)


def parse_issues(text):
    """Tolerant: extract the first valid JSON array of objects from a reply.
    Uses raw_decode from each '[' position (lazy regex loses the opening
    bracket after the first failed match)."""
    dec = json.JSONDecoder()
    for m in re.finditer(r"\[", text):
        try:
            arr, _ = dec.raw_decode(text[m.start():])
        except json.JSONDecodeError:
            continue
        if isinstance(arr, list) and arr and isinstance(arr[0], dict):
            return arr
    return []


def stage_merge(round_no):
    outdir = os.path.join(V3, "round_%d" % round_no)
    per_model = {}
    for model in MODELS:
        issues = []
        for fp in sorted(glob.glob(os.path.join(
                outdir, "text_%s_c*.json" % model)) +
                glob.glob(os.path.join(
                outdir, "vis_%s_b*.json" % model))):
            issues.extend(parse_issues(open(fp, encoding="utf-8").read()))
        per_model[model] = issues
    # cross-model match: same chapter + similar quoted/observed text
    def key(iss):
        ch = str(iss.get("chapter") or iss.get("page_hint") or
                 iss.get("page") or "")
        q = (iss.get("quoted_clause") or iss.get("issue") or
             iss.get("observed") or "")[:60].lower()
        return (re.sub(r"\W+", "", ch), re.sub(r"\W+", "", q))
    common, unique = [], []
    seen = {}
    for model, issues in per_model.items():
        for iss in issues:
            seen.setdefault(key(iss), []).append((model, iss))
    for k, hits in seen.items():
        models = {m for m, _ in hits}
        entry = {"models": sorted(models),
                 "issue": hits[0][1],
                 "severity": hits[0][1].get("severity")}
        if len(models) >= 2:
            common.append(entry)
        else:
            unique.append(entry)
    merge = {"round": round_no, "per_model_counts":
             {m: len(v) for m, v in per_model.items()},
             "common": common, "unique": unique}
    json.dump(merge, open(os.path.join(outdir, "merged.json"), "w"),
              ensure_ascii=False, indent=1)
    print("common:", len(common), "unique:", len(unique),
          "counts:", merge["per_model_counts"], flush=True)


DISCUSS_TASK = """REVIEW TASK — cross-critique (round %d).
Below is the merged register from all four models' independent passes, plus
each model's UNIQUE findings (found by one model, missed by others).
(1) FALSE-POSITIVE CHECK: which entries are wrong or misread? Apply the
approximation/operator rules. Name entry ids.
(2) UNIQUE-FINDING ADJUDICATION: for each unique finding, can you reproduce
it from the quoted text? Mark REPRODUCED / DISPROVED / NEEDS-VERIFICATION.
(3) PROMPT IMPROVEMENT: 1-3 concrete edits to the review prompt so the NEXT
round catches what this round missed (what class of issue did some models
fail to find?).
Output JSON: {false_positives: [ids], adjudications: [{id, verdict, why}],
prompt_edits: [strings]}.

MERGED REGISTER:
%s
"""


def stage_discuss(round_no):
    outdir = os.path.join(V3, "round_%d" % round_no)
    merge = json.load(open(os.path.join(outdir, "merged.json")))
    blob = json.dumps(merge, ensure_ascii=False, indent=1)
    if len(blob) > 350000:
        blob = blob[:350000]
    for model in MODELS:
        fp = os.path.join(outdir, "discuss_%s.json" % model)
        if os.path.exists(fp):
            continue
        print(f"[discuss] {model}", flush=True)
        out = chat(model, PROMPT_V1 + "\n\n" + (DISCUSS_TASK % round_no) + blob)
        open(fp, "w", encoding="utf-8").write(out)
        print(f"  -> {len(out)} chars", flush=True)
    print("discuss stage done", flush=True)


if __name__ == "__main__":
    stage = sys.argv[1]
    round_no = int(sys.argv[2])
    {"text": stage_text, "vision": stage_vision,
     "merge": stage_merge, "discuss": stage_discuss}[stage](round_no)