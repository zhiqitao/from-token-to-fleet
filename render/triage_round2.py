#!/usr/bin/env python3
"""Round-2 triage: is each finding's quoted_clause present in CURRENT manuscript?
Writes review/loop_v3/round_2/triage.json + prints PRESENT/ABSENT split."""
import json, glob, os, re

os.chdir("/home/ubuntu/hermes-work/from-token-to-fleet")
MS = "design/manuscript"
book = {}
for f in glob.glob(MS + "/**/*.md", recursive=True):
    t = open(f, errors="ignore").read()
    # normalized: strip md emphasis, collapse ws
    book[f] = t
    book.setdefault("__flat__", "")
book_all = "\n".join(book[f] for f in book if f != "__flat__")
flat = re.sub(r"[*_`]", "", book_all)
flat = re.sub(r"\s+", " ", flat)
flat_hy = flat.replace("‑", "-").replace("–", "-").replace("—", "-")

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

def norm(s):
    s = re.sub(r"[*_`]", "", str(s))
    s = s.replace("‑", "-").replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", s).strip()

def present(qc):
    q = norm(qc)
    if len(q) < 24:
        return None
    # try progressively shorter distinctive windows (line-wrap tolerance)
    for n in (90, 60, 40, 28):
        if len(q) <= n:
            frag = q
        else:
            # take the densest window: middle slice
            frag = q[len(q)//2 - n//2: len(q)//2 + n//2]
        if frag in flat_hy or frag in flat:
            return True
    return False

results = []
for fp in sorted(glob.glob("review/loop_v3/round_2/text_*.json")):
    for it in load(fp):
        qc = it.get("quoted_clause") or it.get("observed") or ""
        results.append(dict(
            id=str(it.get("id", "?")), sev=it.get("severity", "?"),
            ch=str(it.get("chapter", "?")), qc=str(qc)[:160],
            present=present(qc), model=os.path.basename(fp)[5:-5],
            correction=str(it.get("correction", ""))[:400],
            observed=str(it.get("observed", ""))[:400]))
for fp in sorted(glob.glob("review/loop_v3/round_2/vis_*.json")):
    for it in load(fp):
        qc = it.get("quoted_clause") or it.get("observed") or ""
        results.append(dict(
            id=str(it.get("id", "?")), sev=it.get("severity", "?"),
            ch="vision", qc=str(qc)[:160],
            present=present(qc), model=os.path.basename(fp)[4:-5],
            correction=str(it.get("correction", ""))[:400],
            observed=str(it.get("observed", ""))[:400]))

json.dump(results, open("review/loop_v3/round_2/triage.json", "w"),
          ensure_ascii=False, indent=1)
pres = [r for r in results if r["present"]]
ab = [r for r in results if r["present"] is False]
unk = [r for r in results if r["present"] is None]
print("total %d | PRESENT %d | ABSENT %d | unknown %d" %
      (len(results), len(pres), len(ab), len(unk)))
print("\n== ABSENT (quote not in current text -> likely already-fixed/misquote) ==")
for r in sorted(ab, key=lambda x: x["sev"]):
    print("  [%s] %-30s %s" % (r["sev"], r["id"][:30], r["qc"][:78]))
print("\n== PRESENT (needs real verification) ==")
for r in sorted(pres, key=lambda x: x["sev"]):
    print("  [%s] %-30s %s" % (r["sev"], r["id"][:30], r["qc"][:78]))