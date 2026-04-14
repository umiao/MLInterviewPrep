"""Reverse sync: dump DB content into markdown under ``docs/generated/`` (DR/backup).

Produces one .md per row with frontmatter capturing the origin row + hash so the
files can be round-tripped through ``sync_docs_to_db.py``.  ``docs/generated/``
is gitignored; this is intended for disaster-recovery and one-off ad-hoc edits
when the authoring md file has been lost or never existed.

Usage:
    python scripts/dump_db_to_docs.py                   # all tables
    python scripts/dump_db_to_docs.py --table system_designs
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import text  # noqa: E402

from src.backend.database import get_engine, init_db  # noqa: E402

OUT_ROOT = PROJECT_ROOT / "docs" / "generated"

TABLE_COLUMNS = {
    "company_documents": [("content", "id", "title")],
    "system_designs": [
        (col, "slug", "title") for col in (
            "overview", "architecture", "dataflow", "formulas",
            "production_constraints", "tradeoffs", "defense", "verbal_outline",
        )
    ],
}


def slugify(s: str) -> str:
    """Lowercase + replace non-alnum with ``_``. For filename safety only."""
    out = "".join(c if c.isalnum() else "_" for c in (s or "").lower())
    return out.strip("_") or "untitled"


def dump_table(table: str) -> int:
    """Emit all rows of a table into per-row/per-column md files. Return count."""
    engine = get_engine()
    written = 0
    with engine.connect() as conn:
        for column, key_col, title_col in TABLE_COLUMNS[table]:
            rows = conn.execute(text(
                f"SELECT {key_col}, {title_col}, {column} FROM {table}"
            )).fetchall()
            for key, title, content in rows:
                if content is None or content == "":
                    continue
                dest = OUT_ROOT / table / f"{slugify(str(key))}__{column}.md"
                dest.parent.mkdir(parents=True, exist_ok=True)
                h = hashlib.sha256(content.encode("utf-8")).hexdigest()
                target_key = "target_id" if key_col == "id" else "target_slug"
                frontmatter = (
                    f"---\n"
                    f"target_table: {table}\n"
                    f"{target_key}: {key}\n"
                    f"target_column: {column}\n"
                    f"origin_title: {title}\n"
                    f"origin_hash: {h}\n"
                    f"---\n"
                )
                dest.write_text(frontmatter + content, encoding="utf-8")
                written += 1
    return written


def main() -> int:
    """CLI entry point."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--table", choices=list(TABLE_COLUMNS.keys()),
                    help="dump a single table (default: all)")
    args = ap.parse_args()
    init_db(get_engine())

    total = 0
    tables = [args.table] if args.table else list(TABLE_COLUMNS.keys())
    for t in tables:
        n = dump_table(t)
        print(f"[DUMP] {t}: {n} files")
        total += n
    print(f"\n[SUMMARY] {total} files written under {OUT_ROOT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
