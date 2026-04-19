"""One-shot audit of logs/id92_v2_s2.md using the functions from
scripts/audit_mlsd_prose_quality.py (no DB mutation).
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from audit_mlsd_prose_quality import (  # noqa: E402
    gate11_patch_ban,
    gate7_prose_ratio,
    gate8_section_contract,
    gate9_triage_signal,
    split_sections,
)


def audit(path: Path, label: str) -> dict:
    text = path.read_text(encoding="utf-8")
    sections = split_sections(text)
    g7_ok, g7_msg, g7_ratio = gate7_prose_ratio(text)
    g8 = gate8_section_contract(sections)
    g9 = gate9_triage_signal(text)
    g11 = gate11_patch_ban(sections)

    print(f"=== {label} ({len(text)} chars) ===")
    print(f"[Gate 7 prose-ratio]   {'PASS' if g7_ok else 'FAIL'}: {g7_msg}")
    print(f"[Gate 8 section-ctx]   {'PASS' if not g8 else f'FAIL ({len(g8)})'}")
    for p in g8:
        print(f"  - {p}")
    print(f"[Gate 9 triage-signal] {'PASS' if not g9 else f'FAIL ({len(g9)})'}")
    for p in g9:
        print(f"  - {p}")
    print(f"[Gate 11 patch-ban]    {'PASS' if not g11 else f'FAIL ({len(g11)})'}")
    for p in g11:
        print(f"  - {p}")
    all_pass = g7_ok and not g8 and not g9 and not g11
    print(f"=== Overall: {'PASS' if all_pass else 'FAIL'} ===\n")
    return {
        "label": label,
        "chars": len(text),
        "g7_ratio": g7_ratio,
        "g7": g7_ok,
        "g8": g8,
        "g9": g9,
        "g11": g11,
        "all_pass": all_pass,
    }


if __name__ == "__main__":
    v1 = audit(REPO / "logs" / "id92_v1_s2.md", "V1 s2")
    v2 = audit(REPO / "logs" / "id92_v2_s2.md", "V2 s2")
