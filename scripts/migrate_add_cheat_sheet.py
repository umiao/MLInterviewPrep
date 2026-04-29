"""Migration: Add cheat_sheet column to system_designs table.

Safe to run on existing databases. Adds the column only if it doesn't exist.
For dev environments, recreating the DB from scratch (via seed import) is also fine.

Usage:
    python scripts/migrate_add_cheat_sheet.py
"""
import sqlite3
import sys
from pathlib import Path


def migrate(db_path: str) -> None:
    """Add cheat_sheet TEXT column to system_designs table if missing."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(system_designs)")
    columns = {row[1] for row in cursor.fetchall()}

    if "cheat_sheet" in columns:
        print("[SKIP] cheat_sheet column already exists in system_designs table.")
        conn.close()
        return

    cursor.execute("ALTER TABLE system_designs ADD COLUMN cheat_sheet TEXT")
    conn.commit()
    print("[DONE] Added cheat_sheet column to system_designs table.")
    conn.close()


if __name__ == "__main__":
    default_db = str(Path(__file__).resolve().parent.parent / "data" / "mle_prep.db")
    db_path = sys.argv[1] if len(sys.argv) > 1 else default_db
    print(f"Migrating database: {db_path}")
    migrate(db_path)
