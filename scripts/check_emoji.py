"""Standalone emoji scanner for CI. Exits non-zero if emoji found in code/config files.

Emoji in doc files (.md/.txt) produce a warning but do not fail the scan,
matching the policy in .claude/hooks/lint_check.py.
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
# scripts/check_emoji_files.py and .claude/hooks/lint_check.py. Locked by
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

# Extensions where emoji should block (code/config). Doc files only warn.
_CODE_EXTENSIONS = {
    ".py", ".yaml", ".yml", ".toml", ".cfg", ".ini",
    ".json", ".html", ".css", ".js", ".ts", ".sh", ".bat", ".ps1",
}

_SKIP_DIRS = {
    ".git", "__pycache__", ".venv", "venv", "node_modules",
    ".mypy_cache", ".ruff_cache", "data", ".claude", "dist",
}


def scan_single_file(fpath: str, root: str) -> tuple[list[str], list[str]]:
    """Scan one file for emoji; return (code_hits, doc_hits) keyed by extension policy.

    Files outside _SCAN_EXTENSIONS produce empty lists. OSErrors (e.g. broken
    symlink, permission denied) are swallowed to match the walker's tolerance.
    """
    code_hits: list[str] = []
    doc_hits: list[str] = []
    ext = os.path.splitext(fpath)[1].lower()
    if ext not in _SCAN_EXTENSIONS:
        return code_hits, doc_hits
    try:
        with open(fpath, encoding="utf-8", errors="replace") as f:
            for lineno, line in enumerate(f, start=1):
                if _EMOJI_RE.search(line):
                    rel = os.path.relpath(fpath, root)
                    preview = line.rstrip()[:120]
                    hit = f"  {rel}:{lineno}: {preview}"
                    if ext in _CODE_EXTENSIONS:
                        code_hits.append(hit)
                    else:
                        doc_hits.append(hit)
    except OSError:
        pass
    return code_hits, doc_hits


def scan_emoji(root: str) -> tuple[list[str], list[str]]:
    """Walk project tree and return (code_hits, doc_hits) for any emoji found."""
    code_hits: list[str] = []
    doc_hits: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        for fname in filenames:
            fpath = os.path.join(dirpath, fname)
            file_code, file_doc = scan_single_file(fpath, root)
            code_hits.extend(file_code)
            doc_hits.extend(file_doc)
    return code_hits, doc_hits


def main() -> int:
    """Run emoji scan. Exit 0 if no code/config hits; 1 if any. Doc hits warn only.

    With no CLI args: scans the full repo root (CI default). With one or more
    positional args: scans only those paths (file or directory). Unknown paths
    produce a [WARN] but do not fail the scan.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    targets = sys.argv[1:] or [project_root]
    code_hits: list[str] = []
    doc_hits: list[str] = []
    for tgt in targets:
        if os.path.isdir(tgt):
            tgt_code, tgt_doc = scan_emoji(tgt)
        elif os.path.isfile(tgt):
            tgt_code, tgt_doc = scan_single_file(tgt, os.path.dirname(tgt) or ".")
        else:
            print(f"[WARN] Not a file or directory: {tgt}", file=sys.stderr)
            continue
        code_hits.extend(tgt_code)
        doc_hits.extend(tgt_doc)
    if doc_hits:
        report = "\n".join(doc_hits[:10])
        print(
            f"[WARN] Emoji in {len(doc_hits)} doc file(s) (warning only):\n{report}",
            file=sys.stderr,
        )
    if code_hits:
        report = "\n".join(code_hits[:30])
        print(f"[FAIL] Found emoji in {len(code_hits)} code/config location(s):\n{report}")
        return 1
    print("[OK] No emoji found in code/config files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
