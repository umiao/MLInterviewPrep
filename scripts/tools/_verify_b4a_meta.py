# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
"""One-shot verification of docs/archive_plans/B4a-meta_2026-05-10.md.

Checks: 5 mandatory sections present, §2 has at least one row per archive
candidate, §3 has a fenced markdown block with drawer URIs, §5 has at least
one promotion candidate.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> int:
    plan = Path("docs/archive_plans/B4a-meta_2026-05-10.md")
    content = plan.read_text(encoding="utf-8")

    sections = [
        "## §1 Inventory snapshot",
        "## §2 Migration matrix",
        "## §3 Skeleton preview",
        "## §4 Hard-archive checklist",
        "## §5 Promotion candidates",
        "## Apply gate",
    ]
    ok = True
    for sec in sections:
        present = sec in content
        print(f"  [{'PRESENT' if present else 'MISSING'}] {sec}")
        if not present:
            ok = False

    s2_start = content.find("## §2 Migration matrix")
    s2_end = content.find("## §3 Skeleton preview")
    s2 = content[s2_start:s2_end]
    archive_candidate_headings = re.findall(r"(?m)^#### Doc id=\d+", s2)
    rows = [ln for ln in s2.split("\n") if ln.startswith("| ") and not ln.startswith("|---") and not ln.startswith("| 原 prose")]
    print(f"  §2 archive-candidate headings: {len(archive_candidate_headings)}")
    print(f"  §2 markdown table rows (excluding headers): {len(rows)}")
    if len(rows) < len(archive_candidate_headings):
        print("  FAIL: fewer rows than archive candidates")
        ok = False

    skel = content[s2_end:content.find("## §4")]
    fence = skel.count("```")
    kg = len(re.findall(r"kg://[\w<>-]+", skel))
    db = len(re.findall(r"db://\d+", skel))
    cd = len(re.findall(r"cd://\d+", skel))
    sd = len(re.findall(r"sd://[a-z0-9/_-]+", skel))
    print(f"  §3 fenced delimiters: {fence} (expect >=2)")
    print(f"  §3 URIs: kg={kg} db={db} cd={cd} sd={sd}")
    if fence < 2:
        print("  FAIL: §3 missing fenced markdown block")
        ok = False

    s5_start = content.find("## §5 Promotion candidates")
    s5_end = content.find("## Apply gate")
    s5 = content[s5_start:s5_end]
    candidates = re.findall(r"(?m)^\d+\.\s+\*\*", s5)
    print(f"  §5 numbered candidates: {len(candidates)}")
    if len(candidates) < 1:
        print("  FAIL: §5 has no promotion candidates")
        ok = False

    print(f"\n  RESULT: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
