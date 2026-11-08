#!/usr/bin/env python3
"""Phase 0 step 3: 4-model joint study of ChatGPT's review methodology.

R1: each model independently analyzes the ChatGPT MASTER_INSTRUCTIONS +
representative issue records -> what is its finding mechanism, what do we
adopt/adapt/drop for our 4-model fleet, what is missing, concrete proposals.
R2 (round2): each model sees the other three R1 analyses -> critique,
correlate, refine. Parent synthesizes into review prompt v1.

Usage: python3 render/methodology_study.py r1|r2
"""
import os
import json
import sys
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLE = json.load(open(os.path.join(REPO, "review/loop_v3/methodology_bundle.json")))

MODELS = ["MiMo-V2.6-Flash-RL", "DeepSeek-V4.1-Flash",
          "Ornith-1.5-122B", "Qwen3.8-27B"]
ENDPOINTS = {
    "im-eglb": "https://api-im.eglb.intel.com/v1",
    "qwen38": "http://100.105.225.59:30000/v1",
}
MODEL_EP = {m: "im-eglb" for m in MODELS}
MODEL_EP["Qwen3.8-27B"] = "qwen38"


def load_key():
    for line in open(os.path.expanduser("~/.hermes/im-eglb.env")):
        line = line.strip()
        if line.startswith("IM_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


IM_KEY = load_key()


def chat(model, prompt, max_tokens=16000, retries=5):
    """Streamed chat call. Streaming is REQUIRED on im-eglb for long generations:
    a non-streaming response sends no bytes until fully generated, and a proxy in
    the path resets the connection at exactly ~300s idle (reproduced: 301s
    ConnectionResetError). Streaming sends deltas from first_event ~12s onward and
    survived a 384s generation."""
    ep = ENDPOINTS[MODEL_EP[model]]
    h = {"Content-Type": "application/json"}
    if MODEL_EP[model] == "im-eglb" and IM_KEY:
        h["Authorization"] = "Bearer " + IM_KEY
    body = {"model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens, "temperature": 0.3, "stream": True}
    # Highest-reasoning config, empirically probed per endpoint:
    #   im-eglb backend enum: 'none','minimal','low','medium','high','xhigh','max' -> use 'max'
    #   qwen38 wrapper only allows xhigh(default)/medium/low -> use 'xhigh'
    #   (numeric 1/1.0 also accepted by DeepSeek but 'max' measured highest reasoning tokens)
    body["reasoning_effort"] = "max" if MODEL_EP[model] == "im-eglb" else "xhigh"
    last = None
    for attempt in range(retries):
        content, reasoning = [], []
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
                    delta = ch.get("delta") or {}
                    if delta.get("content"):
                        content.append(delta["content"])
                    if delta.get("reasoning_content"):
                        reasoning.append(delta["reasoning_content"])
            c = "".join(content)
            if not c and reasoning:
                c = "[[NO-CONTENT: reasoning only]]"
            return c or ""
        except Exception as e:
            last = e
            import time
            time.sleep(5 * (attempt + 1))
    return f"[[ERR {last}]]"


R1_PROMPT = """You are one of four reviewer models planning a new self-review loop for a technical book (From Token to Fleet, 457pp, US Letter, near publication). A previous external review by ChatGPT (GPT-6.1 Sol) was highly effective and we are studying ITS METHODOLOGY before designing ours.

Below are (A) the full instruction document that drove ChatGPT's review, and (B) five representative issue records it produced, showing how it actually FOUND problems.

Analyze independently (your own judgment, do not be agreeable for its own sake):

1. FINDING MECHANISM: What are the concrete mechanisms by which this review discovers defects? (e.g. independent rederivation, denominator integrity, rendered-page inspection, cross-chapter tracing...) Rank the top 5 by yield.
2. ADOPT / ADAPT / DROP: For a 4-model fleet (MiMo, DeepSeek, Ornith-122B, Qwen3.8-27B - all reasoning+vision+long-context, each round reviews the FULL book), which parts of this methodology do we adopt verbatim, adapt, or drop? Consider: our machine gates already pin numeric-consistency and stale-value classes every build.
3. WHAT IS MISSING: What would a multi-model fleet do that this single-model review could not? What failure modes of multi-model review itself must we design against (false-positive amplification, herd behavior, one model anchoring others)?
4. CONCRETE PROPOSALS: 5-10 specific, actionable rules to put in our review prompt v1.

Format: markdown with those four headers. Be specific and terse. No flattery, no generic advice.

=== (A) MASTER INSTRUCTIONS (the prompt that drove the review) ===
%s

=== (B) REVIEW ROUND 1 (first round, 2026-10-30) ===
%s

=== (C) REVIEW ROUND 7 (latest round, 2026-11-04) ===
%s

=== (D) LOOP 8 CORE REVIEW (2026-10-26) ===
%s
"""

R2_PROMPT = """You are one of four reviewer models refining a shared review methodology. Round 1: each of the four models independently analyzed ChatGPT's review methodology (below). Your task now: read all four analyses, then produce your FINAL position.

1. CORRELATE: which recommendations do >=2 models independently agree on (high confidence)?
2. DISSENT: where do you disagree with the other models, and why? Name the model.
3. FALSE-POSITIVE DEFENSE: propose concrete rules that prevent the fleet from amplifying a single model's misreading (a prior example: one model flagged '17/8.6=1.977' as P0 by ignoring the '~' sign).
4. FINAL PROPOSALS: your ranked list of rules for review prompt v1 (merge, do not merely repeat).

Format: markdown with those four headers. Terse, specific, no flattery.

=== YOUR ROUND-1 ANALYSIS ===
%s

=== ROUND-1 ANALYSES OF THE OTHER THREE MODELS ===
%s
"""


def run(stage):
    outdir = os.path.join(REPO, "review/loop_v3")
    os.makedirs(outdir, exist_ok=True)
    if stage == "r1":
        prompt = R1_PROMPT % (BUNDLE["master_instructions"],
                              BUNDLE["rounds"]["R1_20261030"],
                              BUNDLE["rounds"]["R7_20261104"],
                              BUNDLE["rounds"]["LOOP8_core"])
        results = {}
        for m in MODELS:
            print(f"=== R1 {m} ===", flush=True)
            try:
                results[m] = chat(m, prompt)
            except Exception as e:
                results[m] = f"[[ERR {e}]]"
            print(f"  {len(results[m])} chars", flush=True)
        json.dump(results, open(os.path.join(outdir, "r1_analyses.json"), "w"),
                  ensure_ascii=False, indent=1)
        print("saved r1_analyses.json")
    elif stage == "r2":
        r1 = json.load(open(os.path.join(outdir, "r1_analyses.json")))
        results = {}
        for m in MODELS:
            others = "\n\n".join(
                f"--- analysis by {om} ---\n{r1[om]}"
                for om in MODELS if om != m)
            prompt = R2_PROMPT % (r1[m], others)
            print(f"=== R2 {m} ===", flush=True)
            try:
                results[m] = chat(m, prompt)
            except Exception as e:
                results[m] = f"[[ERR {e}]]"
            print(f"  {len(results[m])} chars", flush=True)
        json.dump(results, open(os.path.join(outdir, "r2_positions.json"), "w"),
                  ensure_ascii=False, indent=1)
        print("saved r2_positions.json")


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "r1")