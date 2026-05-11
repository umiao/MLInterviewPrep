"""Seed Uber Team Matching Prep doc into company_documents.

Idempotent UPSERT keyed by (company_id=5, title=DOC_TITLE). Re-running with
unchanged source markdown is a NOOP (same content_hash).

The doc is pinned to the front of the Uber prep drawer's Documents tab via
created_at = PIN_DATE (earlier than every existing Uber doc), since the API
endpoint orders by created_at ASC (src/backend/routers/companies.py:310).

Source: src/backend/seed_data/uber/team_matching_prep.md
Context: 2026-05-09 Discord ad-hoc request (msg 1502917773083414608).
Two team-match calls coming up (Rider ML, UberEats Feed); doc captures
diagnostic question playbook + +/- signal table + decision framework.
"""
from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "mle_prep.db"
MD_PATH = (
    PROJECT_ROOT
    / "src" / "backend" / "seed_data" / "uber" / "team_matching_prep.md"
)

COMPANY_ID = 5  # Uber
DOC_TITLE = "Uber Team Matching Prep — Rider ML & UberEats Feed"
DOC_KIND = "prep_note"
SOURCE_TYPE = "prep_doc"
IS_GOLDEN = 0
SOURCE_PATH = "src/backend/seed_data/uber/team_matching_prep.md"

# Earliest existing Uber doc is 2026-03-24; pin this one to 2026-03-01 so it
# sorts first in the API's ORDER BY created_at ASC.
PIN_DATE = "2026-03-01 00:00:00"


def compute_hash(content: str) -> str:
    """SHA-256 over UTF-8 bytes -- used as the idempotency key."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def main() -> None:
    """Read markdown and UPSERT into company_documents."""
    with open(MD_PATH, encoding="utf-8") as f:
        content = f.read()
    new_hash = compute_hash(content)

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, content_hash, created_at FROM company_documents "
        "WHERE company_id = ? AND title = ?",
        (COMPANY_ID, DOC_TITLE),
    )
    row = cursor.fetchone()

    if row is None:
        cursor.execute(
            "INSERT INTO company_documents "
            "(company_id, title, content, source_type, doc_kind, is_golden, "
            " content_hash, source_path, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))",
            (
                COMPANY_ID, DOC_TITLE, content, SOURCE_TYPE, DOC_KIND,
                IS_GOLDEN, new_hash, SOURCE_PATH, PIN_DATE,
            ),
        )
        print(f"[INSERT] doc_id={cursor.lastrowid} chars={len(content)} "
              f"hash={new_hash[:12]} created_at={PIN_DATE}")
    else:
        doc_id, old_hash, old_created = row
        if old_hash == new_hash and old_created == PIN_DATE:
            print(f"[NOOP]   doc_id={doc_id} content_hash unchanged "
                  f"({new_hash[:12]}) -- idempotent re-run")
        else:
            cursor.execute(
                "UPDATE company_documents SET "
                "content = ?, source_type = ?, doc_kind = ?, "
                "is_golden = ?, content_hash = ?, source_path = ?, "
                "created_at = ?, updated_at = datetime('now') "
                "WHERE id = ?",
                (
                    content, SOURCE_TYPE, DOC_KIND, IS_GOLDEN,
                    new_hash, SOURCE_PATH, PIN_DATE, doc_id,
                ),
            )
            print(f"[UPDATE] doc_id={doc_id} chars={len(content)} "
                  f"old_hash={old_hash[:12]} new_hash={new_hash[:12]} "
                  f"created_at={PIN_DATE}")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
