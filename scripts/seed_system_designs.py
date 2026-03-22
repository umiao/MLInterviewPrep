"""Seed script for system design modules.

Inserts 6 system design case study modules with metadata.
Idempotent: upserts by slug (if exists, updates title/subtitle/diagram/order only).
Content sections are left empty for manual population.
"""
import sys
from pathlib import Path

# Ensure project root is on sys.path so imports work when run as a script
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.backend.database import SessionLocal, init_db
from src.backend.models.system_design import SystemDesign

# Module seed data: slug, title, subtitle, diagram_filename, display_order
MODULES: list[dict[str, str | int]] = [
    {
        "slug": "module-arbitration",
        "title": "Module Arbitration: Content Marketplace for eBay SRP",
        "subtitle": (
            "Two-stage offline value estimation + online runtime arbitration "
            "for whole-page optimization"
        ),
        "diagram_filename": "module_arbitration.png",
        "display_order": 1,
    },
    {
        "slug": "llm-orchestration",
        "title": "LLM-Generated Artifact Orchestration for Structured Search",
        "subtitle": (
            "Production-ready architecture for structured conversational search "
            "with online inference + offline learning"
        ),
        "diagram_filename": "llm_orchestration.png",
        "display_order": 2,
    },
    {
        "slug": "pbe-pipeline",
        "title": "Product-Based Experience Logging & Dataset Pipeline",
        "subtitle": (
            "End-to-end PBE optimization: trackable IDs, viewport logging, "
            "attribution, training-data materialization"
        ),
        "diagram_filename": "pbe_pipeline.png",
        "display_order": 3,
    },
    {
        "slug": "ranking-allocation",
        "title": "Ranking-as-Allocation: Diversity Allotment Policy Framework",
        "subtitle": (
            "Diversity allotment policy with online serving + nearline "
            "closed-loop policy management"
        ),
        "diagram_filename": "ranking_allocation.png",
        "display_order": 4,
    },
    {
        "slug": "database-comparison",
        "title": "Database Systems Comparison: Cassandra & Distributed Storage",
        "subtitle": (
            "Architecture comparison across Cassandra, HBase, DynamoDB, ScyllaDB, "
            "CockroachDB -- CAP trade-offs, consistency models, and selection criteria"
        ),
        "diagram_filename": "database_comparison.png",
        "display_order": 5,
    },
    {
        "slug": "distributed-task-queue",
        "title": "Distributed Task Queue: Failure Modes, Idempotency & Exactly-Once",
        "subtitle": (
            "Deep failure analysis across 7 scenarios -- worker crash, dual execution, "
            "poison pill, broker restart -- with idempotency and fencing token solutions"
        ),
        "diagram_filename": "distributed_task_queue.png",
        "display_order": 6,
    },
]


def seed_system_designs() -> dict[str, int]:
    """Insert or update system design modules.

    Returns:
        Dict with counts of inserted and updated records.
    """
    init_db()
    db = SessionLocal()
    inserted = 0
    updated = 0

    try:
        for data in MODULES:
            existing = (
                db.query(SystemDesign)
                .filter(SystemDesign.slug == data["slug"])
                .first()
            )
            if existing:
                existing.title = data["title"]
                existing.subtitle = data["subtitle"]
                existing.diagram_filename = data["diagram_filename"]
                existing.display_order = data["display_order"]
                updated += 1
            else:
                module = SystemDesign(
                    slug=data["slug"],
                    title=data["title"],
                    subtitle=data["subtitle"],
                    diagram_filename=data["diagram_filename"],
                    display_order=data["display_order"],
                )
                db.add(module)
                inserted += 1

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    return {"inserted": inserted, "updated": updated}


if __name__ == "__main__":
    result = seed_system_designs()
    print(
        f"Seed complete: {result['inserted']} inserted, "
        f"{result['updated']} updated."
    )
