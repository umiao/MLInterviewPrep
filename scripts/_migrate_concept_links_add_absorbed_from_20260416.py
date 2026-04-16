"""Extend concept_links.relation CHECK vocabulary to include 'absorbed_from'.

KG Phase 2 Task KG-P2-02 introduces an edge used when a canonical_hub has
absorbed unique material from a legacy 合集 doc. The reverse edge from hub
to source doc is labelled 'absorbed_from'. The prior vocabulary (after
KG-P2-01) was {canonical, mentions, composed_of, prereq, follow_up,
see_also, drill}. SQLite cannot ALTER a CHECK constraint in place, so we
recreate the table preserving all rows and indexes.

Idempotent: inspects the current CHECK SQL; if 'absorbed_from' is already
present, prints [UNCHANGED] and exits without touching the DB.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

NEW_RELATIONS = (
    "canonical", "mentions", "composed_of", "prereq",
    "follow_up", "see_also", "drill", "absorbed_from",
)
_RELATIONS_SQL = ",".join(f"'{r}'" for r in NEW_RELATIONS)

CREATE_NEW_TABLE_SQL = f"""
CREATE TABLE concept_links__new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    src_kind TEXT NOT NULL CHECK(src_kind IN ('framework_node','company_document')),
    src_id INTEGER NOT NULL,
    dst_kind TEXT NOT NULL CHECK(dst_kind IN ('framework_node','company_document')),
    dst_id INTEGER NOT NULL,
    relation TEXT NOT NULL CHECK(relation IN ({_RELATIONS_SQL})),
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


def _current_check_sql(conn: sqlite3.Connection) -> str:
    """Return the CREATE TABLE SQL for concept_links (or empty string)."""
    row = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='concept_links'"
    ).fetchone()
    return row[0] if row else ""


def migrate() -> int:
    """Recreate concept_links with 'absorbed_from' relation added.

    Returns 0 on success (including no-op), 2 if DB missing, 3 if the base
    table is absent.
    """
    if not DB_PATH.exists():
        print(f"[ERROR] DB not found: {DB_PATH}")
        return 2

    conn = sqlite3.connect(str(DB_PATH))
    try:
        current = _current_check_sql(conn)
        if not current:
            print("[ERROR] concept_links table missing. Run the P1-01 "
                  "migration first.")
            return 3

        if "'absorbed_from'" in current:
            print("[UNCHANGED] concept_links already accepts 'absorbed_from'")
            return 0

        conn.execute("PRAGMA foreign_keys = OFF")
        conn.execute("BEGIN")
        conn.execute(CREATE_NEW_TABLE_SQL)
        conn.execute(
            "INSERT INTO concept_links__new "
            "(id, src_kind, src_id, dst_kind, dst_id, relation, weight, note, created_at) "
            "SELECT id, src_kind, src_id, dst_kind, dst_id, relation, weight, note, created_at "
            "FROM concept_links"
        )
        conn.execute("DROP TABLE concept_links")
        conn.execute("ALTER TABLE concept_links__new RENAME TO concept_links")
        conn.execute(CREATE_INDEX_SRC_SQL)
        conn.execute(CREATE_INDEX_DST_SQL)
        conn.execute("COMMIT")
        conn.execute("PRAGMA foreign_keys = ON")
        print(f"[DONE] concept_links relation vocabulary extended: {NEW_RELATIONS}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(migrate())
