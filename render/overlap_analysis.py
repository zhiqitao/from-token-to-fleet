#!/usr/bin/env python3
"""Cross-reviewer overlap analysis (Round 1, dispositioned).
Cluster findings across models by chapter + anchor overlap (table/fig refs,
distinctive numbers) or token Jaccard; report consensus (2+ models) vs unique.
Writes review/loop_v3/round_1/overlap_analysis.md
"""
import json, glob, os, re, itertools
from collections import defaultdict

os.chdir("/home/ubuntu/hermes-work/from-token-to-fleet/review/loop_v3/round_1")

STOP = set("""the a an of to in and or for with on at by from is are be been was were
this that these those it its as not no than then which who whom whose what when where
how why can could should would may might must will shall do does did done have has had
page chapter section see also vs via per each every any all both same different new old
text says stated states claim claims claims' observed evidence correction root cause
acceptance test quoted clause severity model issue finding fix rejected none required
not required optional optionally""".split())

# canonical constants that appear in every finding -> not distinctive anchors
CANON = set("""40 10 9200 9,200 300 70 8 25 2.62 436 640 140 20 2000 2,000 1.31 9500 9,500
1.08 8.6 17 21 19 32 34 22 989 1.288 128 32k 9.2k 5 2 3 1 4 6 7 9 11 13 15 16 18 23 24 25 26 27
100 50 60 65 70b h100 fp16 fp8 kv mfu rps tpot ttft p95 p99 slo""".split())

def load(fp):
    t = open(fp, encoding="utf-8").read()
    t = t.split("\nCOVERAGE")[0]
    t = re.sub(r"```[a-z]*", "", t)
    t = t.replace("[[TRUNCATED at 65536]]", "")
    dec = json.JSONDecoder()
    # 1) first complete list
    for m in re.finditer(r"\[", t):
        try:
            obj, _ = dec.raw_decode(t, m.start())
            if isinstance(obj, list):
                return [x for x in obj if isinstance(x, dict)]
        except Exception:
            continue
    # 2) per-object salvage (broken JSON inside list)
    objs = []
    for m in re.finditer(r"\{", t):
        try:
            obj, _ = dec.raw_decode(t, m.start())
            if isinstance(obj, dict) and ("severity" in obj or "id" in obj):
                objs.append(obj)
        except Exception:
            continue
    return objs

def feats(it):
    txt = " ".join(str(it.get(k, "")) for k in
                    ("quoted_clause", "observed", "correction", "evidence"))
    low = txt.lower()
    anchors = set()
    for m in re.finditer(r"(?:table|fig(?:ure)?)\s*\d+[-.]\d+", low):
        anchors.add(m.group(0).replace(" ", ""))
    for m in re.finditer(r"§+\s*\d+(?:\.\d+)?", low):
        anchors.add(m.group(0).replace(" ", ""))
    for m in re.finditer(r"\d[\d,\.]*\s*(?:gb|pflop|gflop|tflop|tok/s|toks|hosts?|nodes?|req/s|ms\b|mb\b|k\b)", low):
        num = m.group(0).replace(" ", "")
        digits = re.sub(r"[^\d,\.]", "", m.group(0)).replace(",", "").replace(".", "")
        if digits and digits not in CANON:
            anchors.add(num)
    toks = set(w for w in re.findall(r"[a-z0-9\.]+", low) if w not in STOP and len(w) > 2)
    return anchors, toks

issues = []
for fp in sorted(glob.glob("text_*.json")):
    base = os.path.basename(fp)[5:]
    model, ch = base.rsplit("_c", 1)
    for it in load(fp):
        if not isinstance(it, dict):
            continue
        a, t = feats(it)
        issues.append(dict(model=model, chunk=int(ch[:-5]),
                           chapter=str(it.get("chapter", "?")),
                           sev=it.get("severity", "?"),
                           iid=str(it.get("id", "?"))[:44],
                           subj=str(it.get("quoted_clause") or it.get("observed") or "")[:110],
                           corr=str(it.get("correction", "")),
                           anchors=a, toks=t))

print("loaded", len(issues), "findings")

def match(A, B):
    """Same issue? table/fig anchor anywhere; else same chapter + (anchor or jaccard)."""
    if A["model"] == B["model"]:
        return False
    shared = A["anchors"] & B["anchors"]
    tbl = {x for x in shared if x.startswith("table") or x.startswith("fig")}
    if tbl:
        return True
    same_ch = A["chapter"] == B["chapter"] or (
        A["chapter"].isdigit() and B["chapter"].isdigit())
    if not same_ch:
        return False
    jac = len(A["toks"] & B["toks"]) / max(1, len(A["toks"] | B["toks"]))
    return len(shared) >= 2 or jac >= 0.18

# greedy complete-linkage: a finding joins a cluster only if it matches EVERY member
clusters = []
for i in range(len(issues)):
    placed = False
    for cl in clusters:
        if all(match(issues[i], issues[j]) for j in cl):
            cl.append(i); placed = True; break
    if not placed:
        clusters.append([i])
clusters = {k: v for k, v in enumerate(clusters)}

common, unique = [], []
for root, idxs in clusters.items():
    models = sorted(set(issues[i]["model"] for i in idxs))
    entry = (models, idxs)
    if len(models) >= 2:
        common.append(entry)
    else:
        unique.append(entry)
common.sort(key=lambda e: -len(e[0]))

def fam(models):
    f = set()
    for m in models:
        f.add("Ornith" if "Ornith" in m else ("MiMo" if "MiMo" in m else
              ("DeepSeek" if "DeepSeek" in m else "Qwen")))
    return f

lines = ["# Round-1 cross-reviewer overlap analysis",
          "",
          "Findings loaded: %d (4-model panel; Ornith = 122B c0/c1/c5 + 397B c1-c4)" % len(issues),
          "Matching: same chapter AND (shared distinctive anchor OR token Jaccard >= 0.16).",
          "",
          "## Consensus clusters (found by 2+ reviewers): %d" % len(common), ""]
for models, idxs in common:
    sevs = sorted(set(issues[i]["sev"] for i in idxs))
    fams = ",".join(sorted(fam(models)))
    lines.append("### [%s] %s — %d findings" % ("/".join(sevs), fams, len(idxs)))
    for i in idxs:
        lines.append("- `%s` %s: %s" % (issues[i]["model"][:20], issues[i]["iid"], issues[i]["subj"][:95]))
    lines.append("")
lines.append("## Unique clusters (single reviewer): %d" % len(unique))
per_model = defaultdict(int)
for models, idxs in unique:
    per_model[models[0]] += 1
for m, n in sorted(per_model.items(), key=lambda x: -x[1]):
    lines.append("- %s: %d unique" % (m, n))
lines.append("")
lines.append("## Unique examples per reviewer")
for m in sorted(set(issues[i]["model"] for i in range(len(issues)))):
    ex = [issues[i] for models, idxs in unique for i in idxs if issues[i]["model"] == m]
    lines.append("### %s (%d)" % (m, len(ex)))
    for it in ex[:6]:
        lines.append("- [%s] %s ch%s: %s" % (it["sev"], it["iid"], it["chapter"], it["subj"][:88]))
    lines.append("")

open("overlap_analysis.md", "w", encoding="utf-8").write("\n".join(lines))
print("consensus clusters:", len(common), "| unique clusters:", len(unique))
print("unique per model:", dict(per_model))
# per-model totals + consensus participation + defect-vs-verification
from collections import Counter
tot = Counter(issues[i]["model"] for i in range(len(issues)))
in_cons = Counter()
for models, idxs in common:
    for i in idxs:
        in_cons[issues[i]["model"]] += 1
def is_verif(idx_list):
    return all(("none" in (iss_corr[i]).lower() or "not required" in iss_corr[i].lower())
               for i in idx_list)
print()
print("per-model: total / in-consensus / unique")
for m in sorted(tot):
    print("  %-24s %3d / %2d / %2d" % (m, tot[m], in_cons[m], per_model[m]))
iss_corr = {i: issues[i]["corr"] for i in range(len(issues))}
n_verif_clusters = sum(1 for models, idxs in common if is_verif(idxs))
print("consensus clusters that are pure verifications (correction=None):", n_verif_clusters)
print()
for models, idxs in common[:14]:
    fams = ",".join(sorted(fam(models)))
    i0 = idxs[0]
    print("[%s] %s | %s" % ("/".join(sorted(set(issues[i]["sev"] for i in idxs))),
                            fams, issues[i0]["subj"][:88]))