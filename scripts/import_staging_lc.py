"""Import parsed LC problems from staging_lc_parsed.json into mle_prep.db.

Handles two cases:
1. Existing problems (matched by leetcode_id): merge company_tags, update difficulty if missing
2. New problems: insert with all fields

Usage:
    python scripts/import_staging_lc.py [--dry-run]
"""
import argparse
import json
import logging
import re
import sys
from pathlib import Path

from sqlalchemy.orm import Session

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import importlib.util  # noqa: E402

from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.problem import Problem  # noqa: E402

# Load sibling helper by file path -- the workspace has a colliding
# ``scripts`` package from another sub-project, so ``from scripts.*`` is
# unreliable here.
_HELPER_PATH = PROJECT_ROOT / "scripts" / "_lc_import_helpers.py"
_helper_spec = importlib.util.spec_from_file_location(
    "_lc_import_helpers", _HELPER_PATH
)
assert _helper_spec is not None and _helper_spec.loader is not None
_lc_import_helpers = importlib.util.module_from_spec(_helper_spec)
_helper_spec.loader.exec_module(_lc_import_helpers)
warn_if_missing_family = _lc_import_helpers.warn_if_missing_family

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

PARSED_FILE = PROJECT_ROOT / "data" / "staging_lc_parsed.json"


def title_to_slug(title: str) -> str:
    """Convert a LeetCode problem title to URL slug.

    Args:
        title: Problem title, e.g. "Two Sum"

    Returns:
        URL slug, e.g. "two-sum"
    """
    slug = title.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def merge_company_tags(existing_json: str | None, new_tags: list[str]) -> str:
    """Merge new company tags into existing JSON array, preserving order.

    Args:
        existing_json: Current company_tags JSON string (or None).
        new_tags: Tags to add if not present.

    Returns:
        Updated JSON array string.
    """
    current = json.loads(existing_json) if existing_json else []

    for tag in new_tags:
        if tag not in current:
            current.append(tag)

    return json.dumps(current, ensure_ascii=False)


def import_problems(db: Session, dry_run: bool = False) -> dict:
    """Import parsed LC problems into database.

    Args:
        db: Database session.
        dry_run: If True, don't commit changes.

    Returns:
        Dict with import statistics.
    """
    with open(PARSED_FILE, encoding="utf-8") as f:
        parsed = json.load(f)

    logger.info("Loaded %d parsed problems from %s", len(parsed), PARSED_FILE.name)

    # Pre-load existing problems by leetcode_id for fast lookup
    existing_problems: dict[int, Problem] = {}
    for p in db.query(Problem).filter(Problem.leetcode_id.isnot(None)).all():
        existing_problems[p.leetcode_id] = p

    logger.info("Found %d existing problems in DB", len(existing_problems))

    stats = {"inserted": 0, "merged": 0, "total": len(parsed)}

    for item in parsed:
        lc_id = item["lc_id"]
        title = item["title"]
        difficulty_raw = item.get("difficulty")
        difficulty = difficulty_raw.lower() if difficulty_raw else None
        company_tags = item.get("company_tags", [])
        url = f"https://leetcode.com/problems/{title_to_slug(title)}/"

        if lc_id in existing_problems:
            # Merge: update company_tags, fill missing difficulty
            existing = existing_problems[lc_id]
            existing.company_tags = merge_company_tags(
                existing.company_tags, company_tags
            )
            if not existing.difficulty and difficulty:
                existing.difficulty = difficulty
            if not existing.url:
                existing.url = url
            stats["merged"] += 1
        else:
            # Insert new problem. staging_lc does not set a family, so every
            # newly inserted row is flagged (warn + append to quarantine TSV).
            family = item.get("family")
            warn_if_missing_family(
                lc_id=lc_id,
                title=title,
                family=family,
                source_script="import_staging_lc.py",
            )
            new_problem = Problem(
                leetcode_id=lc_id,
                title=title,
                url=url,
                difficulty=difficulty,
                category="algorithm",
                family=family,
                company_tags=json.dumps(company_tags, ensure_ascii=False),
                priority=2,
            )
            db.add(new_problem)
            # Track for duplicate detection within this batch
            existing_problems[lc_id] = new_problem
            stats["inserted"] += 1

    if dry_run:
        logger.info("[DRY RUN] Would insert %d, merge %d", stats["inserted"], stats["merged"])
        db.rollback()
    else:
        db.commit()
        logger.info("Committed: inserted %d, merged %d", stats["inserted"], stats["merged"])

    return stats


def main() -> None:
    """Entry point for the import script."""
    parser = argparse.ArgumentParser(description="Import parsed LC problems into DB")
    parser.add_argument("--dry-run", action="store_true", help="Preview without committing")
    args = parser.parse_args()

    if not PARSED_FILE.exists():
        logger.error("Parsed file not found: %s", PARSED_FILE)
        sys.exit(1)

    # Initialize DB (creates tables if needed)
    init_db()
    db = SessionLocal()

    try:
        stats = import_problems(db, dry_run=args.dry_run)
        logger.info("Summary: %s", json.dumps(stats))
    finally:
        db.close()


if __name__ == "__main__":
    main()
