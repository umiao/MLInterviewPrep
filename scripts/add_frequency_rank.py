"""Add frequency_rank column to problems table and populate from parsed JSON.

Usage:
    python scripts/add_frequency_rank.py [--dry-run]
"""
import argparse
import json
import logging
import sqlite3
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "mle_prep.db"
PARSED_FILE = PROJECT_ROOT / "data" / "staging_lc_parsed.json"


def main() -> None:
    """Add frequency_rank column and populate from parsed JSON."""
    parser = argparse.ArgumentParser(description="Add frequency_rank to problems")
    parser.add_argument("--dry-run", action="store_true", help="Preview without committing")
    args = parser.parse_args()

    if not DB_PATH.exists():
        logger.error("Database not found: %s", DB_PATH)
        return
    if not PARSED_FILE.exists():
        logger.error("Parsed file not found: %s", PARSED_FILE)
        return

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Step 1: Add column if it doesn't exist
    cursor.execute("PRAGMA table_info(problems)")
    columns = [row[1] for row in cursor.fetchall()]
    if "frequency_rank" not in columns:
        logger.info("Adding frequency_rank column to problems table")
        if not args.dry_run:
            cursor.execute("ALTER TABLE problems ADD COLUMN frequency_rank INTEGER")
    else:
        logger.info("frequency_rank column already exists")

    # Step 2: Load parsed JSON and build leetcode_id -> frequency_rank map
    with open(PARSED_FILE, encoding="utf-8") as f:
        parsed = json.load(f)

    lc_id_to_rank: dict[int, int] = {}
    for item in parsed:
        lc_id = item["lc_id"]
        rank = item["frequency_rank"]
        if lc_id not in lc_id_to_rank:
            lc_id_to_rank[lc_id] = rank

    logger.info("Loaded %d frequency ranks from parsed JSON", len(lc_id_to_rank))

    # Step 3: Update problems with matching leetcode_id
    updated = 0
    for lc_id, rank in lc_id_to_rank.items():
        if not args.dry_run:
            cursor.execute(
                "UPDATE problems SET frequency_rank = ? WHERE leetcode_id = ?",
                (rank, lc_id),
            )
            updated += cursor.rowcount
        else:
            cursor.execute(
                "SELECT COUNT(*) FROM problems WHERE leetcode_id = ?",
                (lc_id,),
            )
            count = cursor.fetchone()[0]
            updated += count

    if args.dry_run:
        logger.info("[DRY RUN] Would update %d rows", updated)
        conn.close()
    else:
        conn.commit()
        logger.info("Updated %d rows with frequency_rank", updated)
        conn.close()


if __name__ == "__main__":
    main()
