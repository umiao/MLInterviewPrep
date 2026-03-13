"""Check specific files (from stdin, one per line) for emoji characters.

Designed for use in git pre-commit hooks: pipe staged file paths into this
script and it will exit 0 if clean, 1 if any emoji are found.

Usage:
    git diff --cached --name-only --diff-filter=ACM | python scripts/check_emoji_files.py
"""
import os
import re
import sys

# Regex matching common emoji ranges (mirrors scripts/check_emoji.py)
_EMOJI_RE = re.compile(
    "["
    "\U0001f600-\U0001f64f"  # emoticons
    "\U0001f300-\U0001f5ff"  # misc symbols & pictographs
    "\U0001f680-\U0001f6ff"  # transport & map
    "\U0001f900-\U0001f9ff"  # supplemental symbols
    "\U0001fa00-\U0001fa6f"  # chess symbols
    "\U0001fa70-\U0001faff"  # symbols extended-A
    "\u2600-\u26ff"          # misc symbols
    "\u2700-\u27bf"          # dingbats
    "\u200d"                 # zero-width joiner
    "\ufe0f"                 # variation selector-16
    "]"
)

_SCAN_EXTENSIONS = {
    ".py", ".md", ".yaml", ".yml", ".toml", ".cfg", ".ini", ".txt",
    ".json", ".html", ".css", ".js", ".ts", ".sh", ".bat", ".ps1",
}


def scan_files(file_paths: list[str]) -> list[str]:
    """Check listed files for emoji. Returns list of 'file:line: <match>' hits."""
    hits: list[str] = []
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
                        hits.append(f"  {fpath}:{lineno}: {preview}")
        except OSError:
            continue
    return hits


def main() -> int:
    """Read file paths from stdin, scan for emoji. Exit 0 if clean, 1 if found."""
    paths = [line.strip() for line in sys.stdin if line.strip()]
    if not paths:
        return 0
    hits = scan_files(paths)
    if hits:
        report = "\n".join(hits[:30])
        print(f"[FAIL] Emoji found in {len(hits)} location(s):\n{report}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
