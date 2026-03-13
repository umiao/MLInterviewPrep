"""Study plan generation based on urgency scoring."""
from datetime import datetime

from sqlalchemy.orm import Session

from src.backend.models.company import CompanyTopicWeight
from src.backend.models.framework import FrameworkNode


def compute_urgency(
    importance: float,
    progress_pct: float,
    last_studied_at: datetime | None,
    days_until_interview: int,
) -> float:
    """Compute urgency score for a topic.

    Args:
        importance: Topic importance weight (0-1).
        progress_pct: Current progress (0-100).
        last_studied_at: When last studied (None = never).
        days_until_interview: Days until next interview.

    Returns:
        Urgency score (higher = more urgent).
    """
    now = datetime.utcnow()
    if last_studied_at is None:
        recency_decay = 1.0
    else:
        days_since = (now - last_studied_at).days
        recency_decay = min(1.0, days_since / 7)

    deadline_factor = max(1.0, 30 / max(1, days_until_interview))
    return importance * (1 - progress_pct / 100) * recency_decay * deadline_factor


def suggest_study_plan(
    db: Session,
    target_company_ids: list[int],
    available_hours: float,
    days_until_interview: int,
) -> list[dict]:
    """Return prioritized topic list with time allocations.

    Args:
        db: Database session.
        target_company_ids: Company IDs to weight by.
        available_hours: Available study hours.
        days_until_interview: Days until interview.

    Returns:
        List of topic dicts with urgency scores and time allocations.
    """
    nodes = (
        db.query(FrameworkNode)
        .filter(FrameworkNode.status != "mastered")
        .all()
    )

    # Build company weight map
    company_weights: dict[int, float] = {}
    if target_company_ids:
        weight_rows = (
            db.query(CompanyTopicWeight)
            .filter(CompanyTopicWeight.company_id.in_(target_company_ids))
            .all()
        )
        for w in weight_rows:
            node_id = w.framework_node_id
            company_weights[node_id] = max(
                company_weights.get(node_id, 0), w.weight
            )

    # Score each node
    scored: list[dict] = []
    for node in nodes:
        urgency = compute_urgency(
            node.importance,
            node.progress_pct,
            node.last_studied_at,
            days_until_interview,
        )
        # Apply company weight multiplier
        if target_company_ids and node.id in company_weights:
            urgency *= company_weights[node.id]
        elif target_company_ids:
            urgency *= 1.0  # default weight

        scored.append({
            "node_id": node.id,
            "title": node.title,
            "path": node.path,
            "urgency": round(urgency, 3),
            "progress_pct": node.progress_pct,
            "importance": node.importance,
            "confidence": node.confidence_level,
        })

    scored.sort(key=lambda x: x["urgency"], reverse=True)
    top = scored[:20]

    # Allocate time proportional to urgency
    total_urgency = sum(t["urgency"] for t in top) or 1.0
    available_minutes = available_hours * 60
    for t in top:
        t["allocated_minutes"] = round(
            (t["urgency"] / total_urgency) * available_minutes
        )

    return top
