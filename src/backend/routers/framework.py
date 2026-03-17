"""Framework tree and study log API routes."""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.backend.database import get_db
from src.backend.models.framework import FrameworkNode, StudyLog
from src.backend.models.problem import Problem
from src.backend.models.scraper import InterviewQuestion
from src.backend.schemas.framework import (
    FrameworkNodeResponse,
    FrameworkNodeUpdate,
    StudyLogCreate,
    StudyLogResponse,
)
from src.backend.schemas.problem import ProblemResponse
from src.backend.schemas.scraper import InterviewQuestionResponse

router = APIRouter()


def _build_tree(
    nodes: list[FrameworkNode], max_depth: int | None
) -> list[dict]:
    """Build nested tree from flat list of nodes in O(n)."""
    node_map: dict[int, dict] = {}
    for n in nodes:
        node_map[n.id] = {
            "id": n.id,
            "path": n.path,
            "depth": n.depth,
            "title": n.title,
            "description": n.description,
            "parent_id": n.parent_id,
            "status": n.status,
            "progress_pct": n.progress_pct,
            "confidence_level": n.confidence_level,
            "importance": n.importance,
            "priority": n.priority,
            "estimated_hours": n.estimated_hours,
            "children": [],
        }

    roots: list[dict] = []
    for n in nodes:
        if max_depth is not None and n.depth > max_depth:
            continue
        entry = node_map[n.id]
        if n.parent_id and n.parent_id in node_map:
            parent = node_map[n.parent_id]
            if max_depth is None or parent["depth"] <= max_depth:
                parent["children"].append(entry)
        elif n.parent_id is None:
            roots.append(entry)

    return roots


@router.get("/framework/tree", response_model=list[FrameworkNodeResponse])
def get_framework_tree(
    max_depth: int | None = Query(default=None, ge=0, le=4),
    db: Session = Depends(get_db),
) -> list[dict]:
    """Return the framework knowledge tree."""
    nodes = db.query(FrameworkNode).order_by(FrameworkNode.depth, FrameworkNode.id).all()
    return _build_tree(nodes, max_depth)


@router.get("/framework/nodes/{node_id}", response_model=FrameworkNodeResponse)
def get_framework_node(
    node_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """Return a single framework node by ID."""
    node = db.query(FrameworkNode).filter(FrameworkNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Framework node not found")

    return {
        "id": node.id,
        "path": node.path,
        "depth": node.depth,
        "title": node.title,
        "description": node.description,
        "parent_id": node.parent_id,
        "status": node.status,
        "progress_pct": node.progress_pct,
        "confidence_level": node.confidence_level,
        "importance": node.importance,
        "priority": node.priority,
        "estimated_hours": node.estimated_hours,
        "children": [],
    }


def _propagate_progress(node_id: int, db: Session) -> None:
    """Recalculate progress for all ancestors in one transaction."""
    node = db.query(FrameworkNode).filter(FrameworkNode.id == node_id).first()
    if not node or node.parent_id is None:
        return
    current_parent_id = node.parent_id
    while current_parent_id is not None:
        parent = db.query(FrameworkNode).filter(
            FrameworkNode.id == current_parent_id
        ).first()
        if not parent:
            break
        children = db.query(FrameworkNode).filter(
            FrameworkNode.parent_id == current_parent_id
        ).all()
        if children:
            total_importance = sum(c.importance for c in children)
            if total_importance > 0:
                weighted = sum(c.progress_pct * c.importance for c in children)
                parent.progress_pct = round(weighted / total_importance, 1)
            else:
                parent.progress_pct = round(
                    sum(c.progress_pct for c in children) / len(children), 1
                )
        current_parent_id = parent.parent_id


@router.put("/framework/nodes/{node_id}", response_model=FrameworkNodeResponse)
def update_framework_node(
    node_id: int,
    node_update: FrameworkNodeUpdate,
    db: Session = Depends(get_db),
) -> dict:
    """Update a framework node (partial)."""
    node = db.query(FrameworkNode).filter(FrameworkNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Framework node not found")

    update_data = node_update.model_dump(exclude_unset=True)
    now = datetime.utcnow()

    # Status transition side effects
    if "status" in update_data:
        new_status = update_data["status"]
        if new_status == "in_progress" and node.started_at is None:
            node.started_at = now
        elif new_status == "mastered":
            node.completed_at = now
            node.progress_pct = 100.0
        elif node.status == "mastered" and new_status != "mastered":
            node.completed_at = None

    for field, value in update_data.items():
        setattr(node, field, value)

    db.flush()  # flush node changes
    if "progress_pct" in update_data:
        _propagate_progress(node_id, db)
    db.commit()
    db.refresh(node)

    return {
        "id": node.id,
        "path": node.path,
        "depth": node.depth,
        "title": node.title,
        "description": node.description,
        "parent_id": node.parent_id,
        "status": node.status,
        "progress_pct": node.progress_pct,
        "confidence_level": node.confidence_level,
        "importance": node.importance,
        "priority": node.priority,
        "estimated_hours": node.estimated_hours,
        "children": [],
    }


@router.get(
    "/framework/nodes/{node_id}/problems",
    response_model=list[ProblemResponse],
)
def get_node_problems(
    node_id: int,
    db: Session = Depends(get_db),
) -> list[Problem]:
    """Return problems linked to a framework node."""
    node = db.query(FrameworkNode).filter(FrameworkNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Framework node not found")

    return (
        db.query(Problem)
        .filter(Problem.framework_node_id == node_id)
        .order_by(Problem.id)
        .all()
    )


@router.get(
    "/framework/nodes/{node_id}/questions",
    response_model=list[InterviewQuestionResponse],
)
def get_node_questions(
    node_id: int,
    db: Session = Depends(get_db),
) -> list[InterviewQuestion]:
    """Return interview questions linked to a framework node."""
    node = db.query(FrameworkNode).filter(FrameworkNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Framework node not found")

    return (
        db.query(InterviewQuestion)
        .filter(InterviewQuestion.mapped_framework_node_id == node_id)
        .order_by(InterviewQuestion.id)
        .all()
    )


@router.post(
    "/framework/nodes/{node_id}/log",
    response_model=StudyLogResponse,
    status_code=201,
)
def create_study_log(
    node_id: int,
    log_data: StudyLogCreate,
    db: Session = Depends(get_db),
) -> StudyLog:
    """Record a study session for a framework node."""
    node = db.query(FrameworkNode).filter(FrameworkNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Framework node not found")

    log = StudyLog(
        framework_node_id=node_id,
        date=log_data.date,
        duration_minutes=log_data.duration_minutes,
        activity_type=log_data.activity_type,
        notes=log_data.notes,
    )
    db.add(log)

    # Update node
    node.last_studied_at = datetime.utcnow()

    # Auto-increment progress based on total study hours vs estimated
    if node.estimated_hours and node.estimated_hours > 0:
        total_minutes = (
            db.query(func.sum(StudyLog.duration_minutes))
            .filter(StudyLog.framework_node_id == node_id)
            .scalar()
            or 0
        ) + log_data.duration_minutes
        total_hours = total_minutes / 60.0
        new_progress = min(95.0, (total_hours / node.estimated_hours) * 100)
        node.progress_pct = new_progress

    db.commit()
    db.refresh(log)
    return log


@router.get(
    "/framework/nodes/{node_id}/logs",
    response_model=list[StudyLogResponse],
)
def get_study_logs(
    node_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[StudyLog]:
    """Return study logs for a framework node, newest first."""
    node = db.query(FrameworkNode).filter(FrameworkNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Framework node not found")

    logs = (
        db.query(StudyLog)
        .filter(StudyLog.framework_node_id == node_id)
        .order_by(StudyLog.date.desc(), StudyLog.id.desc())
        .limit(limit)
        .all()
    )
    return logs


@router.get("/framework/stats")
def get_framework_stats(db: Session = Depends(get_db)) -> dict:
    """Return aggregate framework statistics."""
    total_nodes = db.query(func.count(FrameworkNode.id)).scalar() or 0

    # By status
    status_rows = (
        db.query(FrameworkNode.status, func.count(FrameworkNode.id))
        .group_by(FrameworkNode.status)
        .all()
    )
    by_status = {row[0]: row[1] for row in status_rows}
    for s in ("not_started", "in_progress", "review", "mastered"):
        by_status.setdefault(s, 0)

    # Weighted progress
    weighted_sum = (
        db.query(func.sum(FrameworkNode.progress_pct * FrameworkNode.importance))
        .filter(FrameworkNode.importance > 0)
        .scalar()
        or 0.0
    )
    total_importance = (
        db.query(func.sum(FrameworkNode.importance))
        .filter(FrameworkNode.importance > 0)
        .scalar()
        or 1.0
    )
    overall_progress = round(weighted_sum / total_importance, 1) if total_importance > 0 else 0.0

    # Study hours this week
    week_ago = datetime.utcnow().date() - timedelta(days=7)
    week_minutes = (
        db.query(func.sum(StudyLog.duration_minutes))
        .filter(StudyLog.date >= week_ago)
        .scalar()
        or 0
    )
    study_hours_this_week = round(week_minutes / 60.0, 1)

    # Study hours by pillar
    pillar_rows = (
        db.query(FrameworkNode.title, func.sum(StudyLog.duration_minutes))
        .join(StudyLog, StudyLog.framework_node_id == FrameworkNode.id)
        .filter(FrameworkNode.depth == 0)
        .group_by(FrameworkNode.title)
        .all()
    )
    study_hours_by_pillar = [
        {"pillar": row[0], "hours": round((row[1] or 0) / 60.0, 1)}
        for row in pillar_rows
    ]

    # Weakest nodes
    weakest = (
        db.query(FrameworkNode)
        .filter(
            FrameworkNode.importance >= 0.5,
            FrameworkNode.confidence_level <= 2,
            FrameworkNode.status != "mastered",
        )
        .order_by(FrameworkNode.importance.desc())
        .limit(10)
        .all()
    )
    weakest_nodes = [
        {
            "id": n.id,
            "title": n.title,
            "confidence": n.confidence_level,
            "importance": n.importance,
        }
        for n in weakest
    ]

    total_study_logs = db.query(func.count(StudyLog.id)).scalar() or 0

    return {
        "total_nodes": total_nodes,
        "by_status": by_status,
        "overall_progress_pct": overall_progress,
        "study_hours_this_week": study_hours_this_week,
        "study_hours_by_pillar": study_hours_by_pillar,
        "weakest_nodes": weakest_nodes,
        "total_study_logs": total_study_logs,
    }


@router.get("/framework/suggest")
async def suggest_study(
    company_ids: str | None = Query(default=None),
    hours: float = Query(default=3.0, ge=0.5),
    days: int = Query(default=14, ge=1),
    use_llm: bool = Query(default=False),
    db: Session = Depends(get_db),
) -> dict:
    """Suggest a study plan based on urgency scoring."""
    from src.backend.services.study_planner import suggest_study_plan

    target_ids: list[int] = []
    if company_ids:
        target_ids = [int(x) for x in company_ids.split(",") if x.strip()]

    topics = suggest_study_plan(db, target_ids, hours, days)

    result: dict = {"structured": topics, "plan_text": None}

    if use_llm:
        from src.backend.services.llm_service import LLMService

        topic_summary = "\n".join(
            f"- {t['title']} (urgency: {t['urgency']:.2f}, progress: {t['progress_pct']:.0f}%)"
            for t in topics[:15]
        )
        llm = LLMService()
        plan_text = await llm.chat(
            system_prompt="You are a study planning assistant for MLE interview prep.",
            messages=[{
                "role": "user",
                "content": (
                    f"Given these topics ranked by urgency:\n{topic_summary}\n\n"
                    f"Available time: {hours} hours. Days until interview: {days}.\n"
                    "Generate a concise daily study plan with rationale."
                ),
            }],
        )
        if isinstance(plan_text, str):
            result["plan_text"] = plan_text

    return result
