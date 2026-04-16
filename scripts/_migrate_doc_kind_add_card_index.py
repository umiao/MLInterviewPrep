"""One-shot migration: add 'card_index' to company_documents.doc_kind CHECK.

Existing DBs received the doc_kind column via migration 19 with CHECK list
('prep_note','hub_doc','recruiter_call','other'). T-P1-440 needs a new
'card_index' doc kind for the Pinterest cluster-card landing page.

SQLite has no ALTER TABLE ... MODIFY CHECK, so we copy-then-swap following
the pattern of `_migrate_companies_status_not_null.py`.

Idempotent: if the current DDL already includes 'card_index', the migration
skips cleanly.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"


def migrate() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = OFF")
    try:
        ddl = conn.execute(
            "SELECT sql FROM sqlite_master "
            "WHERE type='table' AND name='company_documents'"
        ).fetchone()[0]
        if "'card_index'" in ddl:
            print("[SKIP] company_documents.doc_kind already allows 'card_index'")
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
                    CHECK(doc_kind IN ('prep_note','hub_doc','recruiter_call','other','card_index')),
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
        print(
            "[DONE] company_documents.doc_kind CHECK now allows 'card_index' "
            f"(preserved {row_count} rows)"
        )

    finally:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.close()


if __name__ == "__main__":
    migrate()
