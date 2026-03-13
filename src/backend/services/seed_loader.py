"""Seed data loader for problems and framework tree."""
import json
import logging
from pathlib import Path

from sqlalchemy.orm import Session

from src.backend.models.framework import FrameworkNode
from src.backend.models.problem import Problem

logger = logging.getLogger(__name__)

SEED_DIR = Path(__file__).parent.parent / "seed_data"


def load_seed_problems(db: Session, filepath: str) -> dict[str, int]:
    """Load problems from JSON file.

    Args:
        db: Database session.
        filepath: Path to JSON seed file.

    Returns:
        Dict with 'inserted' and 'skipped' counts.
    """
    with open(filepath, encoding="utf-8") as f:
        problems = json.load(f)

    inserted = 0
    skipped = 0

    for p in problems:
        leetcode_id = p.get("leetcode_id")
        if leetcode_id is not None:
            existing = (
                db.query(Problem)
                .filter(Problem.leetcode_id == leetcode_id)
                .first()
            )
            if existing:
                skipped += 1
                continue

        db_problem = Problem(
            leetcode_id=leetcode_id,
            title=p["title"],
            url=p.get("url"),
            difficulty=p.get("difficulty"),
            tags=json.dumps(p.get("tags", []), ensure_ascii=False),
            pattern=p.get("pattern"),
            source=p.get("source"),
            category=p.get("category", "algorithm"),
            company_tags=json.dumps(p.get("company_tags", []), ensure_ascii=False),
            priority=p.get("priority", 2),
        )
        db.add(db_problem)
        inserted += 1

    db.commit()
    return {"inserted": inserted, "skipped": skipped}


def load_seed_framework(db: Session, filepath: str) -> dict[str, int]:
    """Load framework nodes from JSON file.

    Args:
        db: Database session.
        filepath: Path to JSON seed file.

    Returns:
        Dict with 'inserted' and 'skipped' counts.
    """
    with open(filepath, encoding="utf-8") as f:
        nodes = json.load(f)

    # Sort by depth to ensure parents exist before children
    nodes.sort(key=lambda n: n.get("depth", 0))

    inserted = 0
    skipped = 0
    path_to_id: dict[str, int] = {}

    # Pre-load existing paths
    existing_nodes = db.query(FrameworkNode).all()
    for n in existing_nodes:
        path_to_id[n.path] = n.id

    for node_data in nodes:
        path = node_data["path"]
        if path in path_to_id:
            skipped += 1
            continue

        parent_path = node_data.get("parent_path")
        parent_id = None
        if parent_path:
            parent_id = path_to_id.get(parent_path)
            if parent_id is None:
                logger.warning(
                    "Parent path '%s' not found for node '%s'", parent_path, path
                )

        node = FrameworkNode(
            parent_id=parent_id,
            path=path,
            depth=node_data.get("depth", 0),
            title=node_data["title"],
            importance=node_data.get("importance", 1.0),
            priority=node_data.get("priority", "P1"),
            estimated_hours=node_data.get("estimated_hours"),
        )
        db.add(node)
        db.flush()  # Get the id for child lookups
        path_to_id[path] = node.id
        inserted += 1

    db.commit()
    return {"inserted": inserted, "skipped": skipped}


def load_all_seeds(db: Session) -> dict:
    """Load all seed data files.

    Returns:
        Combined load results.
    """
    results = {}

    blind75_path = SEED_DIR / "blind75.json"
    if blind75_path.exists():
        results["blind75"] = load_seed_problems(db, str(blind75_path))

    neetcode150_path = SEED_DIR / "neetcode150.json"
    if neetcode150_path.exists():
        results["neetcode150"] = load_seed_problems(db, str(neetcode150_path))

    framework_path = SEED_DIR / "framework_tree.json"
    if framework_path.exists():
        results["framework"] = load_seed_framework(db, str(framework_path))

    return results
