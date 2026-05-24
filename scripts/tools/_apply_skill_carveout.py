# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
"""Apply SKILL.md write/edit permission carve-out to all 4 project settings.json files.

T-P2-664: Widen .claude/skills/*/SKILL.md permission carve-out across 4 projects.

Idempotent: safe to re-run. Reads each settings.json, ensures the two carve-out
strings exist in permissions.allow, writes back only if changed.
"""

from __future__ import annotations

import json
from pathlib import Path

CARVEOUT_ENTRIES = [
    "Write(.claude/skills/**/SKILL.md)",
    "Edit(.claude/skills/**/SKILL.md)",
]

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]

PROJECT_SETTINGS_PATHS = [
    WORKSPACE_ROOT / ".claude" / "settings.json",
    WORKSPACE_ROOT / "MLInterviewPrep" / ".claude" / "settings.json",
    WORKSPACE_ROOT / "helixos" / ".claude" / "settings.json",
    WORKSPACE_ROOT / "homestead_asset_management_system" / ".claude" / "settings.json",
]


def apply_carveout(settings_path: Path) -> tuple[bool, list[str]]:
    """Ensure CARVEOUT_ENTRIES exist in permissions.allow. Return (changed, allow_list)."""
    text = settings_path.read_text(encoding="utf-8")
    data = json.loads(text)

    permissions = data.setdefault("permissions", {})
    allow = permissions.setdefault("allow", [])

    added: list[str] = []
    for entry in CARVEOUT_ENTRIES:
        if entry not in allow:
            allow.append(entry)
            added.append(entry)

    if not added:
        return (False, allow)

    new_text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    settings_path.write_text(new_text, encoding="utf-8")
    return (True, allow)


def main() -> int:
    for path in PROJECT_SETTINGS_PATHS:
        if not path.exists():
            print(f"[SKIP] {path} (not found)")
            continue
        changed, allow = apply_carveout(path)
        marker = "[ADDED]" if changed else "[OK]"
        print(f"{marker} {path}")
        for entry in CARVEOUT_ENTRIES:
            present = "yes" if entry in allow else "no"
            print(f"        {entry}: {present}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
