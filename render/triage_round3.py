#!/usr/bin/env python3
"""Round-3 triage: is each TEXT finding's quoted_clause present in the
CURRENT manuscript (post Rounds 1-2 + this round's P1 fixes)?
Writes review/loop_v3/round_3/triage.json + prints PRESENT/ABSENT split.
PRESENT  -> the quoted text exists; the model's complaint targets live text.
ABSENT   -> quote not found; either the text changed already (likely
             already-satisfied) or the quote is composite/elided (spot-check).
"""
import json, glob, os, re

os.chdir("/home/ubuntu/hermes-work/from-token-to-fleet")
MS = "design/manuscript"
parts = []
for f in glob.glob(MS + "/**/*.md", recursive=True):
    parts.append(open(f, errors="ignore").read())
book_all = "\n".join(parts)
flat = re.sub(r"[*_`]", "", book_all)
flat_norm = re.sub(r"\s+", " ", flat)


def norm(s):
    s = re.sub(r"[*_`]", "", s)
    s = s.replace("\u202f", " ").replace("\u00a0", " ")
    s = s.replace("\u2014", "-").replace("\u2013", "-")
    s = s.replace("\u2212", "-").replace("\u00d7", "x")
    return re.sub(r"\s+", " ", s).strip()


def load(fp):
    t = open(fp, encoding="utf-8").read().split("\nCOVERAGE")[0]
    t = re.sub(r"```[a-z]*", "", t).replace("[[TRUNCATED at 65536]]", "")
    dec = json.JSONDecoder()
    for m in re.finditer(r"\[", t):
        try:
            obj, _ = dec.raw_decode(t, m.start())
            if isinstance(obj, list):
                return [x for x in obj if isinstance(x, dict)]
        except Exception:
            continue
    return []


rows = []
for fp in sorted(glob.glob("review/loop_v3/round_3/text_*.json")):
    model = os.path.basename(fp)[5:].rsplit("_c", 1)[0]
    chunk = os.path.basename(fp).rsplit("_c", 1)[1].split(".")[0]
    for it in load(fp):
        if it.get("severity") not in ("P2", "P3"):
            continue
        q = norm(str(it.get("quoted_clause", "")))
        if len(q) < 12:
            status = "SHORT"
        elif q in norm(flat):
            status = "PRESENT"
        else:
            # flexible: allow minor numeric/spacing drift
            pat = re.escape(q)
            pat = pat.replace(re.escape(" "), r"\s+")
            status = "PRESENT" if re.search(pat, norm(flat)) else "ABSENT"
        rows.append({
            "id": it.get("id"), "sev": it.get("severity"),
            "model": model, "chunk": chunk, "status": status,
            "chapter": it.get("chapter"),
            "quote": str(it.get("quoted_clause", ""))[:180],
            "observed": str(it.get("observed", ""))[:400],
            "correction": str(it.get("correction", ""))[:300],
        })

out = "review/loop_v3/round_3/triage.json"
json.dump(rows, open(out, "w"), ensure_ascii=False, indent=1)
from collections import Counter
print("triaged:", len(rows), Counter(r["status"] for r in rows))
print("wrote", out)