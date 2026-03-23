"""One-time migration: recalculate all parent node progress_pct and status.

Walks the framework tree bottom-up (deepest nodes first) and recalculates
each parent's progress_pct (importance-weighted average of children) and
status (derived from children using priority model).

Idempotent: safe to run multiple times. Only modifies parent nodes
(nodes that have children). Leaf nodes are untouched.

Usage:
    python scripts/migrate_recalculate_parent_progress.py
    python scripts/migrate_recalculate_parent_progress.py --dry-run
"""

import argparse
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, func  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from src.backend.models.framework import FrameworkNode  # noqa: E402


def _derive_status(child_statuses: list[str]) -> str:
    """Derive parent status from children.

    All mastered -> mastered. All not_started -> not_started.
    Otherwise -> in_progress.
    """
    statuses = set(child_statuses)
    if statuses == {"mastered"}:
        return "mastered"
    if statuses == {"not_started"}:
        return "not_started"
    return "in_progress"


def recalculate_parents(db_url: str, *, dry_run: bool = False) -> int:
    """Recalculate all parent nodes bottom-up.

    Args:
        db_url: SQLAlchemy database URL.
        dry_run: If True, print changes but don't commit.

    Returns:
        Number of nodes updated.
    """
    engine = create_engine(db_url)
    session_factory = sessionmaker(bind=engine)
    db = session_factory()

    try:
        # Get max depth
        max_depth = db.query(func.max(FrameworkNode.depth)).scalar() or 0

        updated = 0
        # Walk bottom-up: from max_depth-1 down to 0
        for depth in range(max_depth - 1, -1, -1):
            parents = (
                db.query(FrameworkNode)
                .filter(FrameworkNode.depth == depth)
                .all()
            )
            for parent in parents:
                children = (
                    db.query(FrameworkNode)
                    .filter(FrameworkNode.parent_id == parent.id)
                    .all()
                )
                if not children:
                    continue  # leaf node, skip

                # Calculate weighted progress
                total_importance = sum(c.importance for c in children)
                if total_importance > 0:
                    weighted = sum(c.progress_pct * c.importance for c in children)
                    new_progress = round(weighted / total_importance, 1)
                else:
                    new_progress = round(
                        sum(c.progress_pct for c in children) / len(children), 1,
                    )

                # Derive status
                new_status = _derive_status([c.status for c in children])

                # Check if anything changed
                changed = (
                    parent.progress_pct != new_progress
                    or parent.status != new_status
                )

                if changed:
                    old_progress = parent.progress_pct
                    old_status = parent.status
                    print(
                        f"  [{parent.id}] {parent.title}: "
                        f"progress {old_progress}% -> {new_progress}%, "
                        f"status {old_status} -> {new_status}"
                    )

                    if not dry_run:
                        parent.progress_pct = new_progress
                        parent.status = new_status

                        # Timestamps: only-set-never-clear
                        now = datetime.utcnow()
                        if new_status != "not_started" and parent.started_at is None:
                            parent.started_at = now
                        if new_status == "mastered" and parent.completed_at is None:
                            parent.completed_at = now

                    updated += 1

        if not dry_run:
            db.commit()
            print(f"\nCommitted {updated} updates.")
        else:
            print(f"\n[DRY RUN] Would update {updated} nodes.")

        return updated
    finally:
        db.close()


def main() -> None:
    """Run the migration."""
    parser = argparse.ArgumentParser(
        description="Recalculate parent framework node progress and status.",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print changes without committing.",
    )
    parser.add_argument(
        "--db-url", default=None,
        help="Database URL. Defaults to DATABASE_URL env var.",
    )
    args = parser.parse_args()

    db_url = args.db_url or os.environ.get("DATABASE_URL")
    if not db_url:
        print("Error: set DATABASE_URL or pass --db-url", file=sys.stderr)
        sys.exit(1)

    print(f"Database: {db_url}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print()

    count = recalculate_parents(db_url, dry_run=args.dry_run)
    if count == 0:
        print("All parent nodes are already up-to-date.")


if __name__ == "__main__":
    main()
