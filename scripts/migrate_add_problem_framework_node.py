"""Migration: Add framework_node_id column to problems table.

Safe to run on existing databases. Adds the column only if it doesn't exist.
For dev environments, recreating the DB from scratch (via seed import) is also fine.

Usage:
    python scripts/migrate_add_problem_framework_node.py
"""
import sqlite3
import sys
from pathlib import Path


def migrate(db_path: str) -> None:
    """Add framework_node_id FK column to problems table if missing."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if column already exists
    cursor.execute("PRAGMA table_info(problems)")
    columns = {row[1] for row in cursor.fetchall()}

    if "framework_node_id" in columns:
        print("[SKIP] framework_node_id column already exists in problems table.")
        conn.close()
        return

    # Add the column (SQLite doesn't support ADD CONSTRAINT for FK inline,
    # but the column will work with the ORM FK enforcement)
    cursor.execute(
        "ALTER TABLE problems ADD COLUMN framework_node_id INTEGER "
        "REFERENCES framework_nodes(id) ON DELETE SET NULL"
    )
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_problems_framework_node_id ON problems(framework_node_id)")
    conn.commit()
    print("[DONE] Added framework_node_id column + index to problems table.")
    conn.close()


if __name__ == "__main__":
    # Default to the standard dev database path
    default_db = str(Path(__file__).resolve().parent.parent / "data" / "mle_prep.db")
    db_path = sys.argv[1] if len(sys.argv) > 1 else default_db
    print(f"Migrating database: {db_path}")
    migrate(db_path)
