"""One-shot migration: create concept_links table for KG cross-references.

KG Phase 1 Task KG-P1-01: Introduce a structured edge table that links
framework_nodes and company_documents. Prior to this table, cross-references
were embedded as freeform markdown in description/content fields. This table
provides a queryable graph for future scrapers, the /kg viz endpoint, and
canonical-vs-drill disambiguation.

Idempotent: CREATE TABLE IF NOT EXISTS + indexes. A second run prints
[UNCHANGED].
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS concept_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    src_kind TEXT NOT NULL CHECK(src_kind IN ('framework_node','company_document')),
    src_id INTEGER NOT NULL,
    dst_kind TEXT NOT NULL CHECK(dst_kind IN ('framework_node','company_document')),
    dst_id INTEGER NOT NULL,
    relation TEXT NOT NULL CHECK(relation IN (
        'canonical','mentions','composed_of','prereq','follow_up','see_also'
    )),
    weight REAL DEFAULT 1.0,
    note TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(src_kind, src_id, dst_kind, dst_id, relation)
)
"""

CREATE_INDEX_SRC_SQL = (
    "CREATE INDEX IF NOT EXISTS ix_concept_links_src "
    "ON concept_links(src_kind, src_id)"
)
CREATE_INDEX_DST_SQL = (
    "CREATE INDEX IF NOT EXISTS ix_concept_links_dst "
    "ON concept_links(dst_kind, dst_id)"
)


def migrate() -> None:
    """Create concept_links table + indexes if absent; idempotent."""
    if not DB_PATH.exists():
        print(f"[SKIP] {DB_PATH} does not exist")
        return

    conn = sqlite3.connect(str(DB_PATH))
    try:
        existing = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='concept_links'"
        ).fetchone()
        idx_existing = conn.execute(
            "SELECT COUNT(*) FROM sqlite_master "
            "WHERE type='index' AND name IN ('ix_concept_links_src','ix_concept_links_dst')"
        ).fetchone()[0]
        if existing and idx_existing == 2:
            print("[UNCHANGED] concept_links table + indexes already present")
            return

        conn.execute("BEGIN")
        conn.execute(CREATE_TABLE_SQL)
        conn.execute(CREATE_INDEX_SRC_SQL)
        conn.execute(CREATE_INDEX_DST_SQL)
        conn.execute("COMMIT")
        print("[DONE] concept_links table + indexes created")
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
