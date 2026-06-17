"""Rewrite stale docs/<company>_*.md and docs/pinterest/ path references to
docs/company/<slug>/... after the DOCS-02 migration (T-P1-481).

This is a one-shot textual rewrite: it scans scripts/, src/, and non-archive
docs/ for the old path patterns and replaces them with the new paths in place.
It skips: archive/, docs/protocol/docs_filing_convention.md (the convention
spec intentionally documents the OLD paths as anti-patterns), PROGRESS.md,
TASKS.md, and this script itself. Safe to rerun -- idempotent (pattern no
longer matches after rewrite).

Usage: python scripts/migrate_docs_company_subdirs.py
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Map each old prefix to the new company subdir. The pattern captures the
# suffix so we can splice it into the new path untouched.
PREFIX_MAP = {
    "google": r"docs/google_([A-Za-z0-9_\-]+\.md)",
    "uber": r"docs/uber_([A-Za-z0-9_\-]+\.md)",
    "doordash": r"docs/doordash_([A-Za-z0-9_\-]+\.md)",
    "slack": r"docs/slack_([A-Za-z0-9_\-]+\.md)",
    "pinterest_flat": r"docs/pinterest_([A-Za-z0-9_\-]+\.md)",
    "pinterest_sub": r"docs/pinterest/([A-Za-z0-9_\-]+\.md)",
}


def rewrite(text: str) -> tuple[str, int]:
    """Apply all prefix substitutions; return (new_text, num_replacements)."""
    total = 0
    for key, pattern in PREFIX_MAP.items():
        if key == "pinterest_sub" or key == "pinterest_flat":
            repl = r"docs/company/pinterest/\1"
        else:
            slug = key
            repl = rf"docs/company/{slug}/\1"
        text, n = re.subn(pattern, repl, text)
        total += n
    return text, total


# Directories to walk (glob patterns relative to ROOT).
SCAN_GLOBS = [
    "scripts/**/*.py",
    "src/**/*.py",
    "src/**/*.ts",
    "src/**/*.tsx",
    "docs/**/*.md",
]

# Paths that must NOT be modified: historical records and the convention spec
# itself (which deliberately cites the old paths in §5 Anti-patterns).
SKIP_RELATIVE = {
    "PROGRESS.md",
    "TASKS.md",
    "archive/progress_log.md",
    "archive/completed_tasks.md",
    "docs/protocol/docs_filing_convention.md",
    "scripts/migrate_docs_company_subdirs.py",
}


def main() -> None:
    changed: list[tuple[str, int]] = []
    for glob in SCAN_GLOBS:
        for path in ROOT.glob(glob):
            rel = path.relative_to(ROOT).as_posix()
            if rel in SKIP_RELATIVE:
                continue
            if "archive/" in rel:
                continue
            try:
                original = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            updated, n = rewrite(original)
            if n > 0:
                path.write_text(updated, encoding="utf-8")
                changed.append((rel, n))
    print(f"[DOCS-02] Rewrote {sum(n for _, n in changed)} path references "
          f"across {len(changed)} files.")
    for rel, n in changed:
        print(f"  {n:3d}  {rel}")


if __name__ == "__main__":
    main()
