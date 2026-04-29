"""Seed Uber ML Coding Golden Answer 集合 (Staff-Level) into company_documents.

Idempotent UPSERT keyed by (company_id=5, title=DOC_TITLE). Re-running with
unchanged source markdown produces zero net change (same content_hash).

Source: src/backend/seed_data/uber/ml_coding_golden.md (4 Staff-level items:
geometric median, K-Means numpy-only, linear regression, logistic regression).

Task: T-P0-629 ([UBER-VO-2])
"""
from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "mle_prep.db"
MD_PATH = PROJECT_ROOT / "src" / "backend" / "seed_data" / "uber" / "ml_coding_golden.md"

COMPANY_ID = 5  # Uber
DOC_TITLE = "Uber ML Coding Golden Answer 集合 (Staff-Level)"
DOC_KIND = "prep_note"
SOURCE_TYPE = "prep_doc"
IS_GOLDEN = 1
SOURCE_PATH = "src/backend/seed_data/uber/ml_coding_golden.md"


def compute_hash(content: str) -> str:
    """SHA-256 over UTF-8 bytes — used as the idempotency key."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def main() -> None:
    """Read markdown and UPSERT into company_documents."""
    with open(MD_PATH, encoding="utf-8") as f:
        content = f.read()
    new_hash = compute_hash(content)

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, content_hash FROM company_documents "
        "WHERE company_id = ? AND title = ?",
        (COMPANY_ID, DOC_TITLE),
    )
    row = cursor.fetchone()

    if row is None:
        cursor.execute(
            "INSERT INTO company_documents "
            "(company_id, title, content, source_type, doc_kind, is_golden, "
            " content_hash, source_path, golden_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))",
            (
                COMPANY_ID, DOC_TITLE, content, SOURCE_TYPE, DOC_KIND,
                IS_GOLDEN, new_hash, SOURCE_PATH,
            ),
        )
        print(f"[INSERT] doc_id={cursor.lastrowid} chars={len(content)} "
              f"hash={new_hash[:12]}")
    else:
        doc_id, old_hash = row
        if old_hash == new_hash:
            print(f"[NOOP]   doc_id={doc_id} content_hash unchanged "
                  f"({new_hash[:12]}) -- idempotent re-run")
        else:
            cursor.execute(
                "UPDATE company_documents SET "
                "content = ?, source_type = ?, doc_kind = ?, "
                "is_golden = ?, content_hash = ?, source_path = ?, "
                "updated_at = datetime('now'), "
                "golden_at = COALESCE(golden_at, datetime('now')) "
                "WHERE id = ?",
                (
                    content, SOURCE_TYPE, DOC_KIND, IS_GOLDEN,
                    new_hash, SOURCE_PATH, doc_id,
                ),
            )
            print(f"[UPDATE] doc_id={doc_id} chars={len(content)} "
                  f"old={old_hash[:12]} new={new_hash[:12]}")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
