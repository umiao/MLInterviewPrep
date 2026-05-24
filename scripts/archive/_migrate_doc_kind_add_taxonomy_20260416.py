"""KG-P1-02: extend company_documents.doc_kind CHECK to the KG taxonomy.

Adds three new allowed values on top of the existing set:
  - canonical_hub   (Phase 2 consolidation targets)
  - composition     (composition / notebook-style docs)
  - drill           (Google R1 focused drills)

Also backfills the 11 Google R1 drill docs (ids 55, 56, 60, 61, 62, 63,
64, 65, 67, 68, 69) to doc_kind='drill'.

SQLite cannot ALTER a CHECK constraint in place, so we copy-then-swap
using the same pattern as `_migrate_doc_kind_add_card_index.py`.

Idempotent: if the DDL already lists all three new values, prints
[UNCHANGED] and exits without touching the table.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

DRILL_DOC_IDS = (55, 56, 60, 61, 62, 63, 64, 65, 67, 68, 69)
NEW_DOC_KINDS = ("canonical_hub", "composition", "drill")


def migrate() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = OFF")
    try:
        ddl = conn.execute(
            "SELECT sql FROM sqlite_master "
            "WHERE type='table' AND name='company_documents'"
        ).fetchone()[0]

        schema_has_all_new = all(f"'{k}'" in ddl for k in NEW_DOC_KINDS)

        if schema_has_all_new:
            # Schema already migrated; still run backfill (also idempotent).
            updated = _backfill_drill(conn)
            if updated == 0:
                print(
                    "[UNCHANGED] doc_kind CHECK already covers "
                    "canonical_hub/composition/drill; drill backfill already applied"
                )
            else:
                print(
                    "[DONE] doc_kind CHECK already covered taxonomy; "
                    f"backfilled {updated} row(s) to doc_kind='drill'"
                )
            return

        conn.execute("BEGIN")
        conn.execute(
            """
            CREATE TABLE company_documents_new (
                id INTEGER NOT NULL PRIMARY KEY,
                company_id INTEGER NOT NULL,
                title VARCHAR NOT NULL,
                content TEXT NOT NULL,
                source_type VARCHAR NOT NULL,
                created_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
                updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
                content_hash TEXT,
                source_path TEXT,
                doc_kind TEXT DEFAULT 'prep_note'
                    CHECK(doc_kind IN (
                        'prep_note','hub_doc','recruiter_call','other',
                        'card_index','canonical_hub','composition','drill'
                    )),
                FOREIGN KEY(company_id) REFERENCES companies (id)
            )
            """
        )
        conn.execute(
            """
            INSERT INTO company_documents_new (
                id, company_id, title, content, source_type,
                created_at, updated_at, content_hash, source_path, doc_kind
            )
            SELECT id, company_id, title, content, source_type,
                   created_at, updated_at, content_hash, source_path, doc_kind
            FROM company_documents
            """
        )
        conn.execute("DROP TABLE company_documents")
        conn.execute("ALTER TABLE company_documents_new RENAME TO company_documents")
        conn.execute(
            "CREATE INDEX IF NOT EXISTS ix_company_documents_company_id "
            "ON company_documents(company_id)"
        )
        conn.execute("COMMIT")

        row_count = conn.execute(
            "SELECT COUNT(*) FROM company_documents"
        ).fetchone()[0]
        updated = _backfill_drill(conn)
        print(
            "[DONE] doc_kind CHECK now allows "
            "canonical_hub/composition/drill "
            f"(preserved {row_count} rows, backfilled {updated} Google R1 drill docs)"
        )
    finally:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.close()


def _backfill_drill(conn: sqlite3.Connection) -> int:
    """Set doc_kind='drill' for the 11 Google R1 drill docs; return rows changed."""
    placeholders = ",".join("?" for _ in DRILL_DOC_IDS)
    cur = conn.execute(
        f"UPDATE company_documents SET doc_kind='drill' "
        f"WHERE id IN ({placeholders}) AND doc_kind != 'drill'",
        DRILL_DOC_IDS,
    )
    conn.commit()
    return cur.rowcount


if __name__ == "__main__":
    migrate()
