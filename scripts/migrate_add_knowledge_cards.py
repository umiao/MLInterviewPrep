"""Migration: add knowledge_cards + company_card_overlays tables.

AC (T-P1-185):
  - New table `knowledge_cards` (canonical cross-company knowledge) with
    provenance columns (source_company, source_file, source_line_start/end).
  - New table `company_card_overlays` (per-company product/interview-format
    overlay under a canonical card), with UNIQUE(card_id, company_id, angle).
  - Schema aligns with the Option A consolidation plan in
    docs/analysis/company_prep_overlap.md (T-P0-184).

Usage:
    python scripts/migrate_add_knowledge_cards.py
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"


DDL_KNOWLEDGE_CARDS = """
CREATE TABLE IF NOT EXISTS knowledge_cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    canonical_body TEXT NOT NULL,
    tags TEXT,
    source_company TEXT,
    source_file TEXT,
    source_line_start INTEGER,
    source_line_end INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

DDL_COMPANY_CARD_OVERLAYS = """
CREATE TABLE IF NOT EXISTS company_card_overlays (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER NOT NULL REFERENCES knowledge_cards(id) ON DELETE CASCADE,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    angle TEXT NOT NULL CHECK(angle IN ('product','interview-format','translation','example')),
    overlay_body TEXT NOT NULL,
    source_file TEXT,
    source_line_start INTEGER,
    source_line_end INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(card_id, company_id, angle)
)
"""

INDEXES = [
    "CREATE INDEX IF NOT EXISTS ix_knowledge_cards_slug ON knowledge_cards(slug)",
    "CREATE INDEX IF NOT EXISTS ix_company_card_overlays_card ON company_card_overlays(card_id)",
    "CREATE INDEX IF NOT EXISTS ix_company_card_overlays_company ON company_card_overlays(company_id)",
]


def migrate(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON")

    cur.execute(DDL_KNOWLEDGE_CARDS)
    print("[DONE] knowledge_cards table ready")
    cur.execute(DDL_COMPANY_CARD_OVERLAYS)
    print("[DONE] company_card_overlays table ready")
    for stmt in INDEXES:
        cur.execute(stmt)
    print(f"[DONE] {len(INDEXES)} indexes ensured")

    conn.commit()

    cards = cur.execute("SELECT COUNT(*) FROM knowledge_cards").fetchone()[0]
    overlays = cur.execute(
        "SELECT COUNT(*) FROM company_card_overlays"
    ).fetchone()[0]
    print(f"[VERIFY] cards={cards}, overlays={overlays}")
    conn.close()


if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else str(DEFAULT_DB)
    print(f"Migrating database: {db_path}")
    migrate(db_path)
