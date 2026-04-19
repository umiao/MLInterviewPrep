"""Audit shim: run gates 7/8/9/11/12 on a markdown text file (no DB mutation).

Used for T-P0-518 iter-2 pilot. Mirrors the pattern from iter-1's
logs/audit_v2_s2.py but imports the A.1.v2 tightened gates (adds Gate 12
triage-depth and expanded Gate 9 verb set / short product tokens).
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from audit_mlsd_prose_quality import (  # type: ignore
    gate7_prose_ratio,
    gate8_section_contract,
    gate9_triage_signal,
    gate11_patch_ban,
    gate12_triage_depth,
    split_sections,
)


def audit_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    sections = split_sections(text)

    print(f"=== {path.name} ({len(text)} chars) ===")
    g7_ok, g7_msg, _ = gate7_prose_ratio(text)
    g8 = gate8_section_contract(sections)
    g9 = gate9_triage_signal(text)
    g11 = gate11_patch_ban(sections)
    g12 = gate12_triage_depth(text)

    print(f"[Gate 7 prose-ratio]     {'PASS' if g7_ok else 'FAIL'}: {g7_msg}")
    print(f"[Gate 8 section-contract] {'PASS' if not g8 else 'FAIL (' + str(len(g8)) + ')'}")
    for p in g8:
        print(f"  - {p}")
    print(f"[Gate 9 triage-signal]   {'PASS' if not g9 else 'FAIL (' + str(len(g9)) + ')'}")
    for p in g9:
        print(f"  - {p}")
    print(f"[Gate 11 patch-ban]      {'PASS' if not g11 else 'FAIL (' + str(len(g11)) + ')'}")
    for p in g11:
        print(f"  - {p}")
    print(f"[Gate 12 triage-depth]   {'PASS' if not g12 else 'FAIL (' + str(len(g12)) + ')'}")
    for p in g12:
        print(f"  - {p}")

    all_pass = g7_ok and not g8 and not g9 and not g11 and not g12
    print(f"=== Overall: {'PASS' if all_pass else 'FAIL'} ===\n")
    return 0 if all_pass else 1


def main(argv: list[str]) -> int:
    if not argv:
        argv = [
            "logs/id92_v1_s2_for_518iter2.md",
            "logs/id92_v2_s2_iter1.md",
            "logs/id92_v2_s2_iter2.md",
        ]
    rc = 0
    for a in argv:
        p = (REPO_ROOT / a).resolve() if not Path(a).is_absolute() else Path(a)
        rc = audit_file(p) or rc
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
