"""Check specific files (from stdin, one per line) for emoji characters.

Designed for use in git pre-commit hooks: pipe staged file paths into this
script and it will exit 0 if clean, 1 if any emoji are found.

Usage:
    git diff --cached --name-only --diff-filter=ACM | python scripts/check_emoji_files.py
"""
import os
import re
import sys

# Force UTF-8 on stdout/stderr so diagnostics containing emoji chars don't crash
# on Windows (default cp1252 cannot encode e.g. \u274c and raises UnicodeEncodeError).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Regex matching common emoji ranges. MUST stay byte-identical to
# scripts/check_emoji.py and .claude/hooks/lint_check.py. Locked by
# tests/test_emoji_regex_equivalence.py.
_EMOJI_RE = re.compile(
    "["
    "\U0001f600-\U0001f64f"  # emoticons
    "\U0001f300-\U0001f5ff"  # misc symbols & pictographs
    "\U0001f680-\U0001f6ff"  # transport & map
    "\U0001f900-\U0001f9ff"  # supplemental symbols
    "\U0001fa00-\U0001fa6f"  # chess symbols
    "\U0001fa70-\U0001faff"  # symbols extended-A
    "\u200d"                 # zero-width joiner
    "\ufe0f"                 # variation selector-16
    "]"
)

_SCAN_EXTENSIONS = {
    ".py", ".md", ".yaml", ".yml", ".toml", ".cfg", ".ini", ".txt",
    ".json", ".html", ".css", ".js", ".ts", ".sh", ".bat", ".ps1",
}

# Extensions where emoji should block (code/config). Doc files only warn —
# matches the policy in scripts/check_emoji.py and .claude/hooks/lint_check.py.
_CODE_EXTENSIONS = {
    ".py", ".yaml", ".yml", ".toml", ".cfg", ".ini",
    ".json", ".html", ".css", ".js", ".ts", ".sh", ".bat", ".ps1",
}


def scan_files(file_paths: list[str]) -> tuple[list[str], list[str]]:
    """Check listed files for emoji. Returns (code_hits, doc_hits)."""
    code_hits: list[str] = []
    doc_hits: list[str] = []
    for fpath in file_paths:
        ext = os.path.splitext(fpath)[1].lower()
        if ext not in _SCAN_EXTENSIONS:
            continue
        if not os.path.isfile(fpath):
            continue
        try:
            with open(fpath, encoding="utf-8", errors="replace") as f:
                for lineno, line in enumerate(f, start=1):
                    if _EMOJI_RE.search(line):
                        preview = line.rstrip()[:120]
                        hit = f"  {fpath}:{lineno}: {preview}"
                        if ext in _CODE_EXTENSIONS:
                            code_hits.append(hit)
                        else:
                            doc_hits.append(hit)
        except OSError:
            continue
    return code_hits, doc_hits


def main() -> int:
    """Read file paths from stdin, scan for emoji. Exit 0 if no code hits; 1 otherwise."""
    paths = [line.strip() for line in sys.stdin if line.strip()]
    if not paths:
        return 0
    code_hits, doc_hits = scan_files(paths)
    if doc_hits:
        report = "\n".join(doc_hits[:10])
        print(
            f"[WARN] Emoji in {len(doc_hits)} doc file(s) (warning only):\n{report}",
            file=sys.stderr,
        )
    if code_hits:
        report = "\n".join(code_hits[:30])
        print(
            f"[FAIL] Emoji found in {len(code_hits)} code/config location(s):\n{report}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
