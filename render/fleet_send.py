#!/usr/bin/env python3
"""Fan the current book PDF to the remaining 6 review-fleet models.
Page count and file size are read from the PDF at send time (book_meta), never
hardcoded — a stale "(519 pages)" vs the real 553-page build was reported back
by a round-12 reviewer as a scope/input defect.
Concurrency=2 (avoid gateway 500 storm). Writes per-model findings to reviewer_fleet/.
Resumable: skips models that already have a *_findings.json on disk."""
import os, re, sys, json, base64, urllib.request, time, concurrent.futures, hashlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import book_meta

PDF = "/home/ubuntu/hermes-work/from-token-to-fleet/render/build/from-token-to-fleet-v20260913.pdf"
OUTDIR = "/home/ubuntu/.hermes/profiles/muta/cache/scratch/reviewer_fleet"
ENV = os.path.expanduser("~/.hermes/im-eglb.env")
MODEL_LIST_URL = "https://api-im.eglb.intel.com/v1/models"
CHAT_URL = "https://api-im.eglb.intel.com/v1/chat/completions"
REMAINING = ["DeepSeek-V4.1-Flash","GLM-5.3-Flash","HY4-Flash","MiMo-V2.6-Flash-RL",
             "MiniMax-M3.1-Flash","Muse-Spark-Open","Qwen3.8-Flash-Next"]

# Per-model OFFICIAL model-card sampling (verified 2026-11-21). Do NOT use temp=0 — greedy
# decoding on these reasoning models causes degenerate/empty content (reasoning eats budget).
CARD_SAMPLING = {
    "DeepSeek-V4.1-Flash":  {"temperature": 1.0, "top_p": 0.95},
    "MiMo-V2.6-Flash-RL":   {"temperature": 1.0, "top_p": 0.95},
    "MiniMax-M3.1-Flash":   {"temperature": 1.0, "top_p": 0.95},
    "GLM-5.3-Flash":        {"temperature": 1.0, "top_p": 0.95},
    "Qwen3.8-Flash-Next":   {"temperature": 1.0, "top_p": 0.95, "top_k": 20},  # think-on
    "HY4-Flash":            {"temperature": 0.9, "top_p": 1.0},
    "Muse-Spark-Open":      {"temperature": 1.0, "top_p": 1.0},
}
DEFAULT_SAMPLING = {"temperature": 1.0, "top_p": 0.95}

def load_key():
    for line in open(ENV):
        m = re.search(r'IM_API_KEY\s*=\s*"?([^"\n]+)"?', line)
        if m: return m.group(1).strip()
    raise SystemExit("no IM_API_KEY")


def parse_findings(text):
    """Parse findings from model output: JSON array, single object, or concatenated objects.
    Returns list or None. Brace-balanced split so inner ']' in prose can't break it."""
    if not text or not text.strip():
        return None
    s = text.strip()
    # strip markdown fences
    s = re.sub(r"^```(?:json)?\s*|\s*```$", "", s).strip()
    # try as-is first (array or single object)
    for cand in (s, "["+s+"]"):
        try:
            o = json.loads(cand)
            return o if isinstance(o, list) else [o]
        except Exception:
            pass
    # brace-balanced split of concatenated top-level objects
    objs=[]; depth=0; start=None; instr=False; esc=False
    for i,ch in enumerate(s):
        if instr:
            if esc: esc=False
            elif ch=="\\": esc=True
            elif ch=='"': instr=False
            continue
        if ch=='"': instr=True
        elif ch=="{":
            if depth==0: start=i
            depth+=1
        elif ch=="}":
            depth-=1
            if depth==0 and start is not None:
                objs.append(s[start:i+1]); start=None
    if objs:
        try:
            return [json.loads(o) for o in objs]
        except Exception:
            return None
    return None


# Per-model output budget. Reasoning-heavy models (MiMo, Qwen) burn 25-31KB reasoning before
# emitting content — a small cap leaves content=0 (finish=length). Streaming (call() uses
# stream=True) makes long generations safe (no 300s LB reset), so give them room to finish.
REASON_BUDGET = {
    "MiMo-V2.6-Flash-RL": 64000,
    "Qwen3.8-Flash-Next": 64000,
    "DeepSeek-V4.1-Flash": 32000,
    "GLM-5.3-Flash": 32000,
}
DEFAULT_BUDGET = 24000

def main():
    os.makedirs(OUTDIR, exist_ok=True)
    key = load_key()
    raw = open(PDF,"rb").read()
    dataurl = "data:application/pdf;base64," + base64.b64encode(raw).decode()
    print("[fleet] pdf %.2f MB sha=%s dataurl=%d chars" % (
        len(raw)/1e6, hashlib.sha256(raw).hexdigest()[:16], len(dataurl)), flush=True)
    # fresh model list
    try:
        req = urllib.request.Request(MODEL_LIST_URL, headers={"Authorization":"Bearer "+key})
        with urllib.request.urlopen(req, timeout=30) as r:
            live = sorted(m.get("id","") for m in json.load(r).get("data",[]))
        print("[fleet] live models:", live, flush=True)
    except Exception as e:
        print("[fleet] model-list failed (%s), using static list" % e, flush=True)
        live = REMAINING
    # authoritative live set from the just-run health probe (overrides flaky in-script enum)
    livefile = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fleet_live_models.txt")
    if os.path.exists(livefile):
        probed = [l.strip() for l in open(livefile) if l.strip()]
        live = [m for m in live if m in probed]  # intersect with endpoint enum
        print("[fleet] live (from health probe):", live, flush=True)
    todo = [m for m in REMAINING if m in live and
            not os.path.exists(os.path.join(OUTDIR, m+"_findings.json"))]
    print("[fleet] todo (skipping done/live-missing):", todo, flush=True)
    if not todo:
        print("[fleet] nothing to do", flush=True); return

    prompt = """You are an independent reviewer on a 7-model reviewer fleet reviewing the book "from-token-to-fleet" (__BOOK_META__). The PDF is attached — read the WHOLE document (your context is 1M tokens). __BOOK_META__ is read from the attached file itself; if your reader reports a different total, trust the file and say so rather than stopping. This is the current deliverable build (vector figures, merged font subsets).

Report genuine defects only, across these dimensions:
(a) internal contradictions between chapters/sections;
(b) arithmetic errors — RECOMPUTE numbers from the text's own inputs and report mismatches;
(c) unsupported/overreaching claims vs evidence labels [1P]/[DERIVED]/[ILLUSTRATIVE]/[HYPOTHESIS];
(d) broken cross-references (Sec.N.M, Fig N.M, Table N-M that do not resolve);
(e) unclear/ambiguous sentences (ASD-STE100: ambiguous pronoun, dangling reference);
(f) rendering artifacts in the text layer (duplicated tokens, mangled punctuation, orphan fragments, unreadable figure labels).

ANTI-FABRICATION: cite the real PDF page number and a verbatim quote for every finding. Never invent a page, quote, or number. A truthful low-count report beats an inflated one.

Output STRICT JSON only (no prose, no markdown fences): a JSON array of objects, each:
{"id","severity"(P0/P1/P2/P3),"dimension","page","chapter","evidence"(verbatim quote),"issue"(one sentence),"fix_instruction"(one concrete fix),"confidence"(high/med/low)}
Aim for signal over volume."""
    prompt = prompt.replace("__BOOK_META__", book_meta.describe(PDF))


    def call(model, max_tokens=12000, timeout=1800):
        s = CARD_SAMPLING.get(model, DEFAULT_SAMPLING)
        body = json.dumps({"model":model,"max_tokens":max_tokens,"stream":True,
            "temperature":s["temperature"],"top_p":s["top_p"],
            **({"top_k":s["top_k"]} if "top_k" in s else {}),
            "messages":[{"role":"user","content":[
                {"type":"file","file":{"filename":"book.pdf","file_data":dataurl}},
                {"type":"text","text":prompt}]}]}).encode()
        rq = urllib.request.Request(CHAT_URL, data=body,
            headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"})
        t=time.time()
        # stream=True: SSE keeps bytes flowing, bypassing the external LB's 300s idle RST.
        content=[]; reasoning=[]; finish=None; usage={}
        try:
            with urllib.request.urlopen(rq, timeout=timeout) as resp:
                buf=b""
                for chunk in iter(lambda: resp.read(65536), b""):
                    buf+=chunk
                    while b"\n" in buf:
                        line,buf=buf.split(b"\n",1)
                        line=line.strip()
                        if not line.startswith(b"data:"): continue
                        data=line[5:].strip()
                        if data==b"[DONE]": continue
                        try: obj=json.loads(data)
                        except Exception: continue
                        if obj.get("usage"): usage=obj["usage"]
                        ch=(obj.get("choices") or [{}])[0]
                        delta=ch.get("delta") or {}
                        if delta.get("content"): content.append(delta["content"])
                        if delta.get("reasoning_content"): reasoning.append(delta["reasoning_content"])
                        if ch.get("finish_reason"): finish=ch["finish_reason"]
            c="".join(content).strip(); rsn="".join(reasoning)
            return {"model":model,"ok":True,"content":c,"reasoning_len":len(rsn),
                    "finish":finish,"usage":usage,"secs":round(time.time()-t,1)}
        except urllib.error.HTTPError as e:
            return {"model":model,"ok":False,"error":"HTTP %d: %s"%(e.code,e.read().decode()[:200]),"secs":round(time.time()-t,1)}
        except Exception as e:
            return {"model":model,"ok":False,"error":repr(e)[:200],"secs":round(time.time()-t,1)}

    def work(m):
        # Empty content at finish=length = reasoning ate the WHOLE budget. The fix is a BIGGER
        # max_tokens (upward ladder), never smaller. Card sampling already set in call().
        r = {"ok": False, "content": "", "error": "not attempted"}
        # Keep generation short: the gateway resets the connection at ~300s on long
        # generations. A single moderate budget finishes under that; a big budget invites
        # the reset. (A prior upward ladder 16000->48000 CAUSED 305s resets.)
        _budget = REASON_BUDGET.get(m, DEFAULT_BUDGET)
        for attempt, mt in enumerate([_budget]):
            # transient connection-reset / HTTP 5xx retry (same model, small backoff)
            for net_try in range(4):
                r = call(m, max_tokens=mt)
                if r.get("ok"):
                    break
                if "Connection reset" in (r.get("error") or "") or "HTTP 5" in (r.get("error") or ""):
                    print("[%s] net err (%s), retry %d/3" % (m, (r.get("error") or "")[:50], net_try+1), flush=True)
                    time.sleep(8); continue
                break
            if r.get("ok") and r.get("content"):
                break
            if r.get("ok") and not r.get("content"):
                rc = r.get("reasoning_len", 0)
                print("[%s] empty at mt=%d (finish=%s, reasoning=%dB) -> LARGER budget", flush=True
                      ) if False else print("[%s] empty at mt=%d (finish=%s) -> try LARGER" % (
                          m, mt, r.get("finish")), flush=True)
        open(os.path.join(OUTDIR, m+"_raw.txt"),"w").write(r.get("content") or r.get("error",""))
        parsed=None; n=None
        if r.get("ok") and r.get("content"):
            parsed = parse_findings(r["content"])
            if parsed is not None:
                n=len(parsed)
                json.dump(parsed, open(os.path.join(OUTDIR,m+"_findings.json"),"w"),
                          ensure_ascii=False, indent=1)
            else:
                n="PARSE-FAIL"
        _s = CARD_SAMPLING.get(m, DEFAULT_SAMPLING)
        print("[%s] T=%s top_p=%s ok=%s %ss finish=%s content=%dB reasoning=%dB findings=%s %s" % (
            m, _s.get("temperature"), _s.get("top_p"),
            r.get("ok"), r.get("secs"), r.get("finish"), len(r.get("content","")),
            r.get("reasoning_len",0),
            n, "" if r.get("ok") else r.get("error","")[:80]), flush=True)
        return m, r.get("ok"), n

    t0=time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        list(ex.map(work, todo))
    # final tally
    allf = sorted(f[:-len("_findings.json")] for f in os.listdir(OUTDIR) if f.endswith("_findings.json"))
    print("[fleet] DONE wall=%.0fs | findings files: %d/7 -> %s" % (
        time.time()-t0, len(allf), allf), flush=True)

if __name__ == "__main__":
    main()
