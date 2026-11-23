#!/usr/bin/env python3
"""Per-model miss analysis: send each model its own brief (findings + missed pages) and ask
why it missed them + a customized prompt for next round. Card sampling + streaming.
Writes miss_analysis/<model>_response.txt and parses a JSON object from the content."""
import json, re, os, time, urllib.request, concurrent.futures

OUTDIR = "/home/ubuntu/.hermes/profiles/muta/cache/scratch/reviewer_fleet"
ANALYSIS = os.path.join(OUTDIR, "miss_analysis")
ENV = os.path.expanduser("~/.hermes/im-eglb.env")
CHAT_URL = "https://api-im.eglb.intel.com/v1/chat/completions"
ALL = ["DeepSeek-V4.1-Flash","MiMo-V2.6-Flash-RL","MiniMax-M3.1-Flash",
       "GLM-5.3-Flash","Qwen3.8-Flash-Next","HY4-Flash","Muse-Spark-Open"]
CARD = {
 "DeepSeek-V4.1-Flash":{"t":1.0,"p":0.95},"MiMo-V2.6-Flash-RL":{"t":1.0,"p":0.95},
 "MiniMax-M3.1-Flash":{"t":1.0,"p":0.95},"GLM-5.3-Flash":{"t":1.0,"p":0.95},
 "Qwen3.8-Flash-Next":{"t":1.0,"p":0.95,"k":20},"HY4-Flash":{"t":0.9,"p":1.0},
 "Muse-Spark-Open":{"t":1.0,"p":1.0}}

def load_key():
    for line in open(ENV):
        m = re.search(r'IM_API_KEY\s*=\s*"?([^"\n]+)"?', line)
        if m: return m.group(1).strip()
    raise SystemExit("no key")

PROMPT_TMPL = """You are a book reviewer on a 7-model reviewer panel. You reviewed the book "from-token-to-fleet" (519 pages) and filed the findings in your brief. Other panel members found defects on pages YOU missed.

Your brief (JSON) is attached as the user message. It contains:
- own_findings: what you filed
- own_pages_found: pages you flagged
- missed_pages_top: pages OTHER models flagged that you did NOT, with what they found there

Analyze WHY you missed those pages. Consider: Did you under-scan those pages? Did you focus on one defect type (arithmetic) and skip others (cross-refs, contradictions, prose)? Did you stop early? Was your attention absorbed by your own findings?

Then produce a CUSTOMIZED review prompt for yourself for the next round that would close YOUR specific blind spots. The prompt should be a drop-in replacement for a generic review prompt — tuned to YOUR failure mode (e.g. "always check every cross-reference", "scan every page's caption", "balance arithmetic + contradiction checks").

Output STRICT JSON only (no prose, no fences):
{
  "miss_diagnosis": "<2-3 sentences: why you missed these pages>",
  "blind_spots": ["<specific gap 1>", "<specific gap 2>", ...],
  "customized_prompt": "<the full drop-in review prompt for you next round, 150-400 words, preserving the anti-fabrication rule and JSON-output schema>"
}"""

def call(model, brief_json, max_tokens=8000, timeout=600):
    s = CARD[model]
    body = json.dumps({"model": model, "max_tokens": max_tokens, "stream": True,
        "temperature": s["t"], "top_p": s["p"],
        **({"top_k": s["k"]} if "k" in s else {}),
        "chat_template_kwargs": {"enable_thinking": False} if model=="Qwen3.8-Flash-Next" else {},
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": PROMPT_TMPL},
            {"type": "text", "text": "YOUR BRIEF JSON:\n" + json.dumps(brief_json, ensure_ascii=False)}]}]}).encode()
    rq = urllib.request.Request(CHAT_URL, data=body,
        headers={"Authorization": "Bearer " + load_key(), "Content-Type": "application/json"})
    t = time.time(); content = []; reasoning = []
    try:
        with urllib.request.urlopen(rq, timeout=timeout) as resp:
            buf = b""
            for chunk in iter(lambda: resp.read(65536), b""):
                buf += chunk
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1); line = line.strip()
                    if not line.startswith(b"data:"): continue
                    d = line[5:].strip()
                    if d == b"[DONE]": continue
                    try: o = json.loads(d)
                    except: continue
                    ch = (o.get("choices") or [{}])[0]; dl = ch.get("delta") or {}
                    if dl.get("content"): content.append(dl["content"])
                    if dl.get("reasoning_content"): reasoning.append(dl["reasoning_content"])
        c = "".join(content).strip()
        return {"model": model, "ok": True, "content": c, "reasoning_len": len("".join(reasoning)),
                "secs": round(time.time()-t, 1)}
    except Exception as e:
        return {"model": model, "ok": False, "error": repr(e)[:200], "secs": round(time.time()-t, 1)}

def parse_json(text):
    s = re.sub(r"^```(?:json)?\s*|\s*```$", "", (text or "").strip()).strip()
    for cand in (s, "{"+s+"}"):
        try: return json.loads(cand)
        except: pass
    # find outermost balanced {}
    i = s.find("{")
    if i >= 0:
        depth=0; instr=False; esc=False
        for j in range(i, len(s)):
            ch=s[j]
            if instr:
                if esc: esc=False
                elif ch=="\\": esc=True
                elif ch=='"': instr=False
                continue
            if ch=='"': instr=True
            elif ch=="{": depth+=1
            elif ch=="}":
                depth-=1
                if depth==0:
                    try: return json.loads(s[i:j+1])
                    except: break
    return None

def work(model):
    brief = json.load(open(os.path.join(ANALYSIS, model.replace("/","_")+"_brief.json")))
    r = call(model, brief)
    open(os.path.join(ANALYSIS, model+"_response.txt"), "w").write(r.get("content") or r.get("error",""))
    parsed = parse_json(r.get("content","")) if r.get("ok") else None
    if parsed:
        json.dump(parsed, open(os.path.join(ANALYSIS, model+"_analysis.json"), "w"), ensure_ascii=False, indent=1)
    print("[%s] ok=%s %ss content=%dB reasoning=%dB parsed=%s %s" % (
        model, r.get("ok"), r.get("secs"), len(r.get("content","")), r.get("reasoning_len",0),
        bool(parsed), "" if r.get("ok") else r.get("error","")[:80]), flush=True)
    return model, bool(parsed)

if __name__ == "__main__":
    t0 = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        list(ex.map(work, ALL))
    done = [m for m in ALL if os.path.exists(os.path.join(ANALYSIS, m+"_analysis.json"))]
    print("[done] wall=%.0fs | analyses: %d/7 -> %s" % (time.time()-t0, len(done), done), flush=True)
