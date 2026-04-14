"""Retrofit drawer links in company_documents content.

Rewrites plain-text problem references into markdown drawer links:
  'LC 123'        -> '[LC 123](lc://123)'
  'LeetCode 123'  -> '[LeetCode 123](lc://123)'
  <custom title>  -> '[<custom title>](db://<db_id>)' (per-doc mapping)

Idempotent: existing links of the same shape are preserved untouched.

Supports --dry-run to preview diffs without DB writes.

Target docs (T-P0-193 scope): 3, 19, 26, 30, 31, 32, 35, 47.

Task: T-P0-196.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

TARGET_DOC_IDS: tuple[int, ...] = (3, 19, 26, 30, 31, 32, 35, 47)

# Match either an already-rewritten LC link (group 1) or a bare 'LC 123' / 'LC123' (group 2+3).
# The first alternative consumes existing links so we never rewrite them.
_LC_COMBINED = re.compile(
    r"(\[LC\s*\d+\]\(lc://\d+\))"
    r"|(\bLC\s*(\d+)\b)"
)

_LEETCODE_COMBINED = re.compile(
    r"(\[LeetCode\s*#?\s*\d+\]\(lc://\d+\))"
    r"|(\b[Ll]eet[Cc]ode\s*#?\s*(\d+)\b)"
)


def rewrite_lc(text: str) -> tuple[str, int]:
    """Rewrite bare 'LC 123' to '[LC 123](lc://123)'. Idempotent.

    Returns (new_text, replacements_made).
    """
    count = 0

    def _sub(m: re.Match[str]) -> str:
        nonlocal count
        if m.group(1) is not None:
            return m.group(1)
        lc_id = m.group(3)
        count += 1
        return f"[LC {lc_id}](lc://{lc_id})"

    return _LC_COMBINED.sub(_sub, text), count


def rewrite_leetcode(text: str) -> tuple[str, int]:
    """Rewrite bare 'LeetCode 123' / 'LeetCode #123' to linked form. Idempotent."""
    count = 0

    def _sub(m: re.Match[str]) -> str:
        nonlocal count
        if m.group(1) is not None:
            return m.group(1)
        lc_id = m.group(3)
        count += 1
        # Preserve original casing of the literal
        literal = m.group(2)
        return f"[{literal}](lc://{lc_id})"

    return _LEETCODE_COMBINED.sub(_sub, text), count


@dataclass
class CustomMapping:
    """Map a custom problem title (regex pattern) to a problems.id."""

    pattern: str
    db_id: int
    display: str | None = None  # canonical display title; defaults to match text

    def compiled(self) -> re.Pattern[str]:
        return re.compile(self.pattern)


def rewrite_custom(text: str, mappings: Iterable[CustomMapping]) -> tuple[str, int]:
    """Rewrite custom problem titles to '[title](db://ID)'. Idempotent.

    For each mapping, we build a combined regex like the LC pattern so that a
    title already wrapped in '[...](db://ID)' is skipped.
    """
    total = 0
    for m in mappings:
        pat = re.compile(
            r"(\[[^\]]+\]\(db://" + re.escape(str(m.db_id)) + r"\))"
            r"|(" + m.pattern + r")"
        )
        count = 0

        def _sub(match: re.Match[str]) -> str:
            nonlocal count
            if match.group(1) is not None:
                return match.group(1)
            literal = match.group(2)
            display = m.display if m.display is not None else literal
            count += 1
            return f"[{display}](db://{m.db_id})"

        text = pat.sub(_sub, text)
        total += count
    return text, total


def fuzzy_find_problem_id(
    conn: sqlite3.Connection, title: str, threshold: float = 0.6
) -> int | None:
    """Fuzzy-match a title against problems.title. Returns best id or None."""
    rows = conn.execute("SELECT id, title FROM problems").fetchall()
    best_id: int | None = None
    best_ratio = 0.0
    title_norm = title.lower().strip()
    for pid, ptitle in rows:
        if not ptitle:
            continue
        ratio = difflib.SequenceMatcher(None, title_norm, ptitle.lower()).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_id = pid
    return best_id if best_ratio >= threshold else None


def retrofit_doc(
    content: str, custom_mappings: Iterable[CustomMapping] = ()
) -> tuple[str, dict[str, int]]:
    """Run all rewriters against one document body. Returns (new_content, stats)."""
    stats: dict[str, int] = {}
    content, stats["lc"] = rewrite_lc(content)
    content, stats["leetcode"] = rewrite_leetcode(content)
    content, stats["custom"] = rewrite_custom(content, custom_mappings)
    return content, stats


# Per-doc custom-title mappings. Populated by T-P0-197 (run step) after Pinterest #7
# (T-P0-194) and any other custom rows are confirmed in the problems table. Keys are
# doc ids; values are lists of CustomMapping.
CUSTOM_MAPPINGS: dict[int, list[CustomMapping]] = {
    # Doc 31 (Uber BPS Custom) + doc 47 (Pinterest) mappings filled in T-P0-197.
}


def load_doc(conn: sqlite3.Connection, doc_id: int) -> tuple[str, str]:
    row = conn.execute(
        "SELECT title, content FROM company_documents WHERE id = ?", (doc_id,)
    ).fetchone()
    if row is None:
        raise ValueError(f"doc {doc_id} not found")
    return row[0], row[1]


def save_doc(conn: sqlite3.Connection, doc_id: int, new_content: str) -> None:
    conn.execute(
        "UPDATE company_documents SET content = ?, updated_at = datetime('now') "
        "WHERE id = ?",
        (new_content, doc_id),
    )


def unified_diff_preview(old: str, new: str, label: str, context: int = 1) -> str:
    """Return a short unified diff (only changed hunks)."""
    return "".join(
        difflib.unified_diff(
            old.splitlines(keepends=True),
            new.splitlines(keepends=True),
            fromfile=f"{label} (before)",
            tofile=f"{label} (after)",
            n=context,
        )
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--doc-ids",
        nargs="*",
        type=int,
        default=list(TARGET_DOC_IDS),
        help="Document ids to retrofit (default: all 8 targets).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes; do not write to the database.",
    )
    parser.add_argument(
        "--diff",
        action="store_true",
        help="Print a unified diff of each changed doc to stdout.",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DB_PATH,
        help=f"SQLite DB path (default: {DB_PATH}).",
    )
    args = parser.parse_args(argv)

    conn = sqlite3.connect(str(args.db))
    try:
        summary: list[dict[str, object]] = []
        for doc_id in args.doc_ids:
            title, content = load_doc(conn, doc_id)
            mappings = CUSTOM_MAPPINGS.get(doc_id, [])
            new_content, stats = retrofit_doc(content, mappings)
            changed = new_content != content
            summary.append(
                {
                    "doc_id": doc_id,
                    "title": title,
                    "changed": changed,
                    "stats": stats,
                }
            )
            if args.diff and changed:
                sys.stdout.write(
                    unified_diff_preview(content, new_content, f"doc_{doc_id}")
                )
            if changed and not args.dry_run:
                save_doc(conn, doc_id, new_content)
        if not args.dry_run:
            conn.commit()
        print(json.dumps({"dry_run": args.dry_run, "docs": summary}, indent=2))
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
