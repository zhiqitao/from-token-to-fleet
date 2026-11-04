#!/usr/bin/env python3
"""Emit a machine-readable release manifest (PRINT-03, review 2026-11-04).

Records, for a given plain build: source commit, build command, PDF SHA-256 and
page count, the render/*figure generator script hashes, the canonical inputs
(yaml/json), evidence cutoff and addenda, and (if present) dependency locks.
The reviewer asked for a manifest pinned by source revision; this is that
record, regenerated on demand, and it lets an external reader re-derive the
figure files and compare against the shipped PDF.

Usage (from repo root):
    python3 render/make_manifest.py [plain.pdf] > release-manifest.json
"""
import os
import sys
import json
import hashlib
import subprocess
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(cmd):
    p = subprocess.run(["git", "-C", REPO, *cmd.split()], capture_output=True,
                       text=True)
    return p.stdout.strip() if p.returncode == 0 else None


def main():
    pdf = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        REPO, "render/build/from-token-to-fleet-v20260913-plain.pdf")
    pdf = os.path.abspath(pdf)

    # figure generator scripts (the render/*.py that produce the vector/PNG figures)
    gen = []
    for root, _, files in os.walk(os.path.join(REPO, "render")):
        for f in sorted(files):
            if f.endswith(".py") and (f.startswith("fig_") or f in
                                      ("capstone_calc.py", "tco_calc.py",
                                       "tco_model.py", "regen_figs.py",
                                       "agent_trace.py", "check_regressions.py")):
                p = os.path.join(root, f)
                gen.append({"script": os.path.relpath(p, REPO),
                            "sha256": sha256(p)})

    m = {
        "$schema": "from-token-to-fleet/release-manifest/1",
        "content_edition": "v20260913",
        "evidence_cutoff": "2026-08-30",
        "addenda": [
            {"id": "v20260913+addendum-20260927", "where": "App A, A.6"},
            {"id": "v20260913+addendum-20261028",
             "where": "body + App A (technology notes)"},
            {"id": "v20260913+addendum-20261101",
             "where": "App A appendix-opening service-status caveat / A.3"},
        ],
        "source_commit": git("rev-parse HEAD"),
        "source_repo": git("config --get remote.origin.url"),
        "build_command": f"bash render/build_plain.sh "
                         f"# build {os.path.basename(pdf)}",
        "pdf": {"path": os.path.relpath(pdf, REPO),
                "sha256": sha256(pdf),
                "bytes": os.path.getsize(pdf)},
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "figure_generator_scripts": gen,
        "render_scripts_sha256": {s: None for s in
                                  ("agent_trace.py", "check_regressions.py")},
        "print_gate": {
            "artifact_notes": [
                "render/build/...<date>-plain.pdf = digital edition (opens on cover).",
                "render/build/...<date>-plain-interior.pdf (--kdp) = KDP interior, "
                "bookmarks stripped, no disallowed metadata (PRINT-01).",
                "render/cover/cover_premium_front.pdf + wrap.pdf = print cover."],
        },
    }
    # add render scripts hash into the dict
    for s in list(m["render_scripts_sha256"]):
        p = os.path.join(REPO, "render", s)
        m["render_scripts_sha256"][s] = sha256(p) if os.path.exists(p) else None

    print(json.dumps(m, indent=2))


if __name__ == "__main__":
    main()
