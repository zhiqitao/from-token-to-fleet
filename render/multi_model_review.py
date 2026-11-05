#!/usr/bin/env python3
"""Multi-model cross-review over the fixed manuscript, from the IM EGLB fleet.

Five models, five DIFFERENT review angles, so each model hunts a distinct
failure mode and a defect any single model misses is surfaced by another.
This is the MV layer of the improved self-check architecture: the machine
gates (agent_trace/check_regressions/check_stale_values) already pin the
deterministic/numeric and stale-value classes; this deliberately covers the
semantic/qualitative classes that cannot be regexed.

Each worker reads a real manuscript excerpt (passed in), applies its ANGLE,
and returns structured JSON findings. The parent cross-compares: an issue
flagged by >=2 independent models is promoted; a model finding that a
different model independently verifies is confirmed.

Usage: python3 render/multi_model_review.py [--dry]
"""
import os
import re
import json
import sys
import glob
import urllib.request
import urllib.error

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MSG = os.path.join(REPO, "design", "manuscript")

# ---- load credentials ----
def load_key():
    for line in open(os.path.expanduser("~/.hermes/im-eglb.env")):
        line = line.strip()
        if line.startswith("IM_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("IM_API_KEY not found")


BASE = "https://api-im.eglb.intel.com/v1"
KEY = load_key()

# 4 models, 4 DISTINCT angles mapped to the review's finding classes. (GLM-5.3-256K
# is a reasoning-only model: it emits reasoning_content but never a final content
# slice on deep tasks, so it is excluded from this content-extraction review.)
MODELS_ANGLES = [
    ("Qwen3-Coder-480B-A35B-Instruct-FP8",
     "NUMERIC-CONSISTENCY: recompute every derived number from its stated inputs. "
     "Flag any displayed value that does NOT equal a recomputation from the "
     "surrounding explicit inputs (esp. sums, products, ceilings, floors, "
     "weighted means). Do not flag a number simply for being illustrative."),
    ("MiMo-V2.6-Flash-RL",
     "INTEGER-BOUNDARY: audit every ceil()/floor()/threshold/tier. Check whether "
     "inputs are rounded BEFORE the ceiling (premature rounding) and whether the "
     "integer result is arithmetically exact. Flag any host count / whole-slot "
     "count that changes if the unrounded input is used."),
    ("Ornith-1.5-397B",
     "DENOMINATOR-SCOPE: audit every average / per-X / per-completed rate. Check "
     "the numerator and denominator are the SAME quantity class (submitted vs "
     "completed vs successful; failed work included or excluded). Flag any per-X "
     "figure whose numerator/denominator span does not match its label."),
    ("Ornith-1.5-122B",
     "TERM-OVERLOAD / MEAN-VS-QUANTILE: find any single term or single percentage "
     "used for TWO different quantities (e.g. '12%' for retained-context vs "
     "processed tokens; alpha vs processed multiplier), and any percentile (p95/"
     "p99) used where a MEAN (E[W]) is required. Flag conflation, not two "
     "intentionally-separate labels."),
]


def chat(model, prompt, max_tokens=4000):
    body = json.dumps({"model": model,
                       "messages": [{"role": "user", "content": prompt}],
                       "max_tokens": max_tokens, "temperature": 0.2}).encode()
    req = urllib.request.Request(BASE + "/chat/completions", data=body,
                                 headers={"Authorization": "Bearer " + KEY,
                                          "Content-Type": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=240))
    m = r["choices"][0]["message"]
    c = m.get("content")
    if c is None and m.get("reasoning_content"):
        # reasoning model consumed the budget; surface a clear refusal
        c = "[[NO-CONTENT: only reasoning emitted]]"
    return c or ""


def read_chapter(n):
    p = os.path.join(MSG, "chapter-%02d" % n, "chapter-%02d.md" % n)
    t = open(p, encoding="utf-8").read()
    return t


def snippet(text, maxlen=2600):
    # strip figures and long math to keep the prompt focused on prose/numbers
    t = re.sub(r"!\[.*?\]\(.*?\)", "", text, flags=re.S)
    t = re.sub(r"\$\$.*?\$\$", "", t, flags=re.S)
    return t[:maxlen]


def main():
    dry = "--dry" in sys.argv
    # chapters carrying the load-bearing agentic/TCO content under review
    chapters = [19, 17, 16, 20]
    # Run per (model, chapter) so each prompt is short enough for a reasoning
    # model to finish reasoning AND emit the JSON content slice.
    results = {}   # (model, chapter) -> raw text
    for model, angle in MODELS_ANGLES:
        for ch in chapters:
            body = ("You are an independent reviewer of one architecture textbook "
                    "chapter, focused on ONE angle.\n\nYOUR ANGLE: %s\n\n"
                    "Read the chapter source below (markdown, figures and long math "
                    "removed). Report ONLY defensible findings matching your angle.\n"
                    "Output a JSON array only. Each item: "
                    "{\"issue\":\"short\",\"term\":\"the term/number\","
                    "\"severity\":\"P0|P1|P2|P3\",\"why\":\"what is wrong + how you "
                    "derived/recomputed it\",\"fix\":\"one-line suggested correction\"}."
                    " If nothing defensible, output exactly: []\n\n"
                    "Do NOT invent issues; only what the text justifies.\n\n"
                    "SOURCE (chapter %d):\n%s")
            src = snippet(read_chapter(ch))
            prompt = body % (angle, ch, src)
            key = (model, ch)
            if dry:
                results[key] = "[]"
                print(f"=== {model} ch{ch} [dry] ===")
                continue
            print(f"=== {model} ch{ch} ({len(src)} chars) ===")
            try:
                out = chat(model, prompt)
            except Exception as e:
                out = json.dumps([{"issue": "ERROR", "term": "", "severity": "P3",
                                   "why": str(e), "fix": ""}])
            results[key] = out
            print(f"  -> {len(out)} chars")
    if not dry:
        with open(os.path.join(REPO, "render/build/multimodel_findings.json"),
                  "w", encoding="utf-8") as f:
            json.dump({"%s|ch%d" % (m, c): v for (m, c), v in results.items()},
                      f, indent=2, ensure_ascii=False)
        print("saved render/build/multimodel_findings.json")


CHALLENGES = [
    # (challenge text, models to ask) - the A-01 class: does the model recompute
    # the headline derived value from the stated inputs, catching a summary that
    # quietly omits a ledger term?
    ("A-01|W(T=3) no-reuse all prefills", [
        "An agentic T=3 trace has FOUR model invocations, inputs 9200, 10065, 10930, "
        "11795 (sum 41990). Each call re-reads the full grown prefix (no prefix cache). "
        "Prefill is linear: 9200 tokens -> 1.08 s. Decode 25 ms/token over 495 output "
        "tokens. 3 tool waits of 0.133 s. Compute the TOTAL service time W. Show "
        "arithmetic. Is it 13.85 s or 17.70 s?",
        ["Qwen3-Coder-480B-A35B-Instruct-FP8", "Ornith-1.5-397B",
         "Ornith-1.5-122B", "MiMo-V2.6-Flash-RL"]]),
]


def run_challenges(dry=False):
    """Focused-recompute proofs: feed the inputs, ask each model to derive the
    headline number. Catches the A-01 class (a summary formula that omits a term
    the ledger contains) where an open 'review this chapter' prompt does not."""
    out = {}
    for name, prompt, models in CHALLENGES:
        for m in models:
            if dry:
                out["%s|%s" % (name, m)] = "[[dry]]"
                continue
            try:
                res = chat(m, prompt)
            except Exception as e:
                res = "[[ERR %s]]" % e
            out["%s|%s" % (name, m)] = res
            print(f"  [{name}] {m}: {len(res)} chars")
    return out


if __name__ == "__main__":
    main()
