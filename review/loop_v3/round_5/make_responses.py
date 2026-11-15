#!/usr/bin/env python3
"""Round 5 close-out: write gap_ledger statuses + responses.md (847 rows).
Run AFTER all fixreports (incl. fix_cross.json) are final.
Format: | Severity | Location | Problem | Why | Recommended | Status | Response |
"""
import json, glob, os, re
from collections import Counter

D = os.path.dirname(os.path.abspath(__file__))
led = json.load(open(f"{D}/gap_ledger.json"))

# fix status per id (fixreports; cross report overrides per-chapter BLOCKED)
fix = {}
for f in sorted(glob.glob(f"{D}/fixreports/fix_ch*.json")) + [f"{D}/fixreports/fix_cross.json"]:
    if not os.path.exists(f):
        continue
    for x in json.load(open(f)):
        prev = fix.get(x["id"])
        # DONE wins over SKIP wins over BLOCKED; cross report overrides BLOCKED
        rank = {"DONE": 3, "SKIP": 2, "BLOCKED": 1}
        if prev is None or rank[x["status"]] > rank[prev[0]]:
            fix[x["id"]] = (x["status"], x.get("note", ""))

def esc(s, limit=None):
    s = str(s or "").replace("|", "\\|").replace("\n", " ").strip()
    if limit and len(s) > limit:
        s = s[:limit].rsplit(" ", 1)[0] + " …"
    return s

rows = []
stat = Counter()
for it in led:
    v = it["verdict"]
    if v == "REJECT":
        status = "REJECTED"
        resp = "Rejected at verification: " + esc(it.get("verdict_evidence", ""), 300)
    else:
        st, note = fix.get(it["id"], ("MISSING", ""))
        status = {"DONE": "FIXED", "SKIP": "ALREADY-FIXED", "BLOCKED": "BLOCKED",
                  "MISSING": "MISSING"}[st]
        resp = {"FIXED": "Fixed: " + esc(note, 300),
                "ALREADY-FIXED": "Fix already present in tree (parallel pass): " + esc(note, 200),
                "BLOCKED": "Blocked: " + esc(note, 200),
                "MISSING": "No fix report row"}[status]
    stat[status] += 1
    loc = f"Ch {it.get('chapter','?')} ({it['id']}" + (f", p.{it['page_hint']}" if it.get("page_hint") else "") + ")"
    rows.append("| {sev} | {loc} | {prob} | {why} | {rec} | {status} | {resp} |".format(
        sev=esc(it["severity"]), loc=esc(loc), prob=esc(it.get("observed", ""), 700),
        why=esc(it.get("verdict_evidence", ""), 700), rec=esc(it.get("verdict_fix") or it.get("correction", ""), 500),
        status=status, resp=esc(resp, 350)))

# ledger status field
for it in led:
    v = it["verdict"]
    if v == "REJECT":
        it["fix_status"] = "REJECTED"
    else:
        st, note = fix.get(it["id"], ("MISSING", ""))
        it["fix_status"] = {"DONE": "FIXED", "SKIP": "ALREADY-FIXED", "BLOCKED": "BLOCKED",
                            "MISSING": "MISSING"}[st]
        it["fix_note"] = note
json.dump(led, open(f"{D}/gap_ledger.json", "w"), ensure_ascii=False, indent=1)

hdr = f"""# Round 5 — responses.md (per-issue disposition, 847 verified findings)

# Scope: 849 collected issues -> 847 unique -> 847 verified by 5 read-only waves
# (evidence iron rule: grep/file:line/arithmetic/vision/PDF measurement).
# Verdicts: 528 ACCEPT + 155 ACCEPT-PARTIAL = 683 fixable; 164 REJECT (both P0 REJECT).
# Fix application: 27 per-chapter batches + 1 cross-chapter batch (447 FIXED by this
# session, 223 ALREADY-FIXED by the parallel session's 189-fix disposition pass,
# 13 BLOCKED -> cross batch). Panel: MiMo-V2.6-Flash-RL, DeepSeek-V4.1-Flash,
# Qwen3.8-27B, MiniMax-M3.1-Flash. Fix backends: MiMo + DeepSeek-V4.1-Flash
# (MiniMax delegate backend down 2026-11-15 00:00-07:00, 6 casualties re-dispatched).

| Severity | Location | Problem | Why | Recommended | Status | Response |
|---|---|---|---|---|---|---|
"""
open(f"{D}/responses.md", "w").write(hdr + "\n".join(rows) + "\n")
print("responses.md rows:", len(rows), "| status:", dict(stat))