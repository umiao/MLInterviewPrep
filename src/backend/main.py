"""FastAPI application entry point."""
from __future__ import annotations

import csv
import io
import json
import logging
import time
from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta
from typing import Any

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy import func
from starlette.middleware.base import BaseHTTPMiddleware

from src.backend.config import get_settings
from src.backend.database import init_db
from src.backend.routers.companies import router as companies_router
from src.backend.routers.forum import router as forum_router
from src.backend.routers.framework import router as framework_router
from src.backend.routers.problems import router as problems_router
from src.backend.routers.qa import router as qa_router
from src.backend.routers.reading import router as reading_router
from src.backend.routers.scraper import router as scraper_router
from src.backend.routers.timeline import router as timeline_router

logger = logging.getLogger(__name__)


class ResponseTimeMiddleware(BaseHTTPMiddleware):
    """Log response time for every request."""

    async def dispatch(self, request: Request, call_next):
        """Measure and log request duration.

        Args:
            request: Incoming HTTP request.
            call_next: Next middleware/handler in chain.

        Returns:
            Response with X-Response-Time header added.
        """
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Response-Time"] = f"{duration_ms:.1f}ms"
        logger.info(
            "%s %s -> %d (%.1fms)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: init DB and seed data on startup."""
    init_db()

    # Auto-load seed data if problems table is empty
    from src.backend.database import SessionLocal
    from src.backend.models.problem import Problem

    db = SessionLocal()
    try:
        count = db.query(Problem).count()
        if count == 0:
            from src.backend.services.seed_loader import load_all_seeds

            results = load_all_seeds(db)
            logger.info("Seed data loaded: %s", results)
    finally:
        db.close()

    yield


app = FastAPI(title="MLE Interview Prep", lifespan=lifespan)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(ResponseTimeMiddleware)


@app.exception_handler(ValidationError)
async def pydantic_validation_error_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    """Return structured 422 response for Pydantic validation errors.

    Args:
        request: Incoming HTTP request.
        exc: Pydantic ValidationError.

    Returns:
        JSON response with error details.
    """
    return JSONResponse(
        status_code=422,
        content={
            "detail": [
                {
                    "loc": list(err.get("loc", [])),
                    "msg": err.get("msg", ""),
                    "type": err.get("type", ""),
                }
                for err in exc.errors()
            ]
        },
    )


@app.get("/", include_in_schema=False)
def root() -> dict:
    """Root endpoint with API info and navigation links."""
    return {
        "name": "MLE Interview Prep API",
        "docs": app.docs_url or "/docs",
        "health": "/api/health",
    }


@app.get("/api/health")
def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}


app.include_router(problems_router, prefix="/api")
app.include_router(qa_router, prefix="/api")
app.include_router(framework_router, prefix="/api")
app.include_router(companies_router, prefix="/api")
app.include_router(scraper_router, prefix="/api")
app.include_router(timeline_router, prefix="/api")
app.include_router(reading_router, prefix="/api")
app.include_router(forum_router, prefix="/api")


@app.get("/api/dashboard")
def get_dashboard():
    """Aggregated dashboard data from all modules."""
    from src.backend.database import SessionLocal
    from src.backend.models.company import Company
    from src.backend.models.framework import FrameworkNode, StudyLog
    from src.backend.models.problem import Attempt, Problem
    from src.backend.models.scraper import InterviewQuestion

    db = SessionLocal()
    try:
        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)

        total_problems = db.query(func.count(Problem.id)).scalar() or 0
        completed = (
            db.query(func.count(Problem.id))
            .filter(Problem.is_completed.is_(True))
            .scalar()
            or 0
        )
        due_for_review = (
            db.query(func.count(Problem.id))
            .filter(Problem.next_review_at.isnot(None), Problem.next_review_at <= now)
            .scalar()
            or 0
        )

        weighted_sum = (
            db.query(func.sum(FrameworkNode.progress_pct * FrameworkNode.importance))
            .filter(FrameworkNode.importance > 0)
            .scalar()
            or 0
        )
        total_importance = (
            db.query(func.sum(FrameworkNode.importance))
            .filter(FrameworkNode.importance > 0)
            .scalar()
            or 1
        )
        overall_progress = round(weighted_sum / total_importance, 1)

        pillars = (
            db.query(FrameworkNode.title, FrameworkNode.progress_pct)
            .filter(FrameworkNode.depth == 0)
            .all()
        )

        attempts_7d = (
            db.query(func.count(Attempt.id))
            .filter(Attempt.started_at >= week_ago)
            .scalar()
            or 0
        )
        week_minutes = (
            db.query(func.sum(StudyLog.duration_minutes))
            .filter(StudyLog.date >= week_ago.date())
            .scalar()
            or 0
        )
        questions_7d = (
            db.query(func.count(InterviewQuestion.id))
            .filter(InterviewQuestion.created_at >= week_ago)
            .scalar()
            or 0
        )

        companies = db.query(Company).filter(Company.applied_at.isnot(None)).all()
        company_deadlines = [{"name": c.name, "status": c.status} for c in companies]

        total_questions = db.query(func.count(InterviewQuestion.id)).scalar() or 0

        return {
            "problems": {
                "total": total_problems,
                "completed": completed,
                "due_for_review": due_for_review,
            },
            "framework": {
                "overall_progress_pct": overall_progress,
                "pillars": [{"title": p[0], "progress": p[1]} for p in pillars],
            },
            "recent_activity": {
                "attempts_7d": attempts_7d,
                "study_hours_7d": round(week_minutes / 60, 1),
                "questions_added_7d": questions_7d,
            },
            "company_deadlines": company_deadlines,
            "scraper": {"total_questions": total_questions},
        }
    finally:
        db.close()


@app.get("/api/dashboard/today")
def get_dashboard_today():
    """Today's focus data: due reviews, weakest topic, streak days."""
    from src.backend.database import SessionLocal
    from src.backend.models.framework import FrameworkNode, StudyLog
    from src.backend.models.problem import Attempt, Problem

    db = SessionLocal()
    try:
        now = datetime.utcnow()

        # Due reviews count
        due_reviews = (
            db.query(func.count(Problem.id))
            .filter(Problem.next_review_at.isnot(None), Problem.next_review_at <= now)
            .scalar()
            or 0
        )

        # Suggested focus topic: leaf node with lowest progress_pct among
        # nodes that have importance > 0 and are not mastered
        weakest_node = (
            db.query(FrameworkNode)
            .filter(
                FrameworkNode.importance > 0,
                FrameworkNode.status != "mastered",
            )
            .order_by(FrameworkNode.progress_pct.asc(), FrameworkNode.importance.desc())
            .first()
        )
        suggested_focus_topic = None
        if weakest_node:
            suggested_focus_topic = {
                "id": weakest_node.id,
                "title": weakest_node.title,
                "path": weakest_node.path,
                "progress_pct": weakest_node.progress_pct,
            }

        # Streak days: consecutive days (ending today) with any activity
        # Activity = attempt or study log
        streak_days = 0
        check_date = date.today()
        while True:
            has_attempt = (
                db.query(func.count(Attempt.id))
                .filter(
                    func.date(Attempt.started_at) == check_date,
                )
                .scalar()
                or 0
            )
            has_study = (
                db.query(func.count(StudyLog.id))
                .filter(StudyLog.date == check_date)
                .scalar()
                or 0
            )
            if has_attempt > 0 or has_study > 0:
                streak_days += 1
                check_date -= timedelta(days=1)
            else:
                break

        return {
            "due_reviews": due_reviews,
            "suggested_focus_topic": suggested_focus_topic,
            "streak_days": streak_days,
        }
    finally:
        db.close()


@app.get("/api/dashboard/activity")
def get_dashboard_activity():
    """Activity data for the last 30 days.

    Returns a list of {date, attempts, study_minutes, questions_added}
    for each of the last 30 days.
    """
    from src.backend.database import SessionLocal
    from src.backend.models.framework import StudyLog
    from src.backend.models.problem import Attempt
    from src.backend.models.scraper import InterviewQuestion

    db = SessionLocal()
    try:
        today = date.today()
        start_date = today - timedelta(days=29)  # 30 days including today

        # Attempts per day
        attempt_rows = (
            db.query(
                func.date(Attempt.started_at).label("day"),
                func.count(Attempt.id).label("cnt"),
            )
            .filter(func.date(Attempt.started_at) >= start_date)
            .group_by(func.date(Attempt.started_at))
            .all()
        )
        attempts_by_day = {str(row.day): row.cnt for row in attempt_rows}

        # Study minutes per day
        study_rows = (
            db.query(
                StudyLog.date.label("day"),
                func.sum(StudyLog.duration_minutes).label("mins"),
            )
            .filter(StudyLog.date >= start_date)
            .group_by(StudyLog.date)
            .all()
        )
        study_by_day = {str(row.day): row.mins or 0 for row in study_rows}

        # Questions added per day
        question_rows = (
            db.query(
                func.date(InterviewQuestion.created_at).label("day"),
                func.count(InterviewQuestion.id).label("cnt"),
            )
            .filter(func.date(InterviewQuestion.created_at) >= start_date)
            .group_by(func.date(InterviewQuestion.created_at))
            .all()
        )
        questions_by_day = {str(row.day): row.cnt for row in question_rows}

        # Build result for all 30 days
        result = []
        for i in range(30):
            d = start_date + timedelta(days=i)
            d_str = str(d)
            result.append({
                "date": d_str,
                "attempts": attempts_by_day.get(d_str, 0),
                "study_minutes": study_by_day.get(d_str, 0),
                "questions_added": questions_by_day.get(d_str, 0),
            })

        return result
    finally:
        db.close()


@app.get("/api/dashboard/summary")
def get_dashboard_summary():
    """Summary stats: problems, framework progress, company counts by status."""
    from src.backend.database import SessionLocal
    from src.backend.models.company import Company
    from src.backend.models.framework import FrameworkNode
    from src.backend.models.problem import Problem

    db = SessionLocal()
    try:
        # Problems
        total_problems = db.query(func.count(Problem.id)).scalar() or 0
        completed = (
            db.query(func.count(Problem.id))
            .filter(Problem.is_completed.is_(True))
            .scalar()
            or 0
        )

        # Framework overall progress
        weighted_sum = (
            db.query(func.sum(FrameworkNode.progress_pct * FrameworkNode.importance))
            .filter(FrameworkNode.importance > 0)
            .scalar()
            or 0
        )
        total_importance = (
            db.query(func.sum(FrameworkNode.importance))
            .filter(FrameworkNode.importance > 0)
            .scalar()
            or 1
        )
        overall_progress = round(weighted_sum / total_importance, 1)

        # Company counts by status
        status_rows = (
            db.query(Company.status, func.count(Company.id))
            .group_by(Company.status)
            .all()
        )
        company_counts = {row[0]: row[1] for row in status_rows}

        return {
            "problems": {
                "total": total_problems,
                "completed": completed,
            },
            "framework_overall_progress_pct": overall_progress,
            "company_counts_by_status": company_counts,
        }
    finally:
        db.close()


def _dt(val: datetime | None) -> str | None:
    """Serialize datetime to ISO 8601 string."""
    return val.isoformat() if val else None


def _date(val) -> str | None:
    """Serialize date to ISO 8601 string."""
    return val.isoformat() if val else None


@app.get("/api/export")
def export_data():
    """Export all data as single JSON with full fields and nested relationships."""
    from src.backend.database import SessionLocal
    from src.backend.models.company import Company
    from src.backend.models.framework import FrameworkNode
    from src.backend.models.problem import Problem
    from src.backend.models.scraper import InterviewQuestion
    from src.backend.models.timeline import InterviewEvent as IEvent

    db = SessionLocal()
    try:
        problems = db.query(Problem).all()
        framework_nodes = db.query(FrameworkNode).all()
        companies = db.query(Company).all()
        questions = db.query(InterviewQuestion).all()
        events = db.query(IEvent).order_by(IEvent.scheduled_at).all()

        return {
            "problems": [
                {
                    "id": p.id,
                    "leetcode_id": p.leetcode_id,
                    "title": p.title,
                    "url": p.url,
                    "difficulty": p.difficulty,
                    "tags": p.tags_list,
                    "pattern": p.pattern,
                    "category": p.category,
                    "source": p.source,
                    "company_tags": p.company_tags_list,
                    "priority": p.priority,
                    "is_completed": p.is_completed,
                    "comfort_level": p.comfort_level,
                    "created_at": _dt(p.created_at),
                    "last_attempted_at": _dt(p.last_attempted_at),
                    "next_review_at": _dt(p.next_review_at),
                    "framework_node_id": p.framework_node_id,
                    "attempts": [
                        {
                            "id": a.id,
                            "started_at": _dt(a.started_at),
                            "duration_seconds": a.duration_seconds,
                            "result": a.result,
                            "approach_notes": a.approach_notes,
                            "complexity_time": a.complexity_time,
                            "complexity_space": a.complexity_space,
                            "comfort_after": a.comfort_after,
                        }
                        for a in p.attempts
                    ],
                }
                for p in problems
            ],
            "framework_nodes": [
                {
                    "id": n.id,
                    "parent_id": n.parent_id,
                    "path": n.path,
                    "depth": n.depth,
                    "title": n.title,
                    "description": n.description,
                    "importance": n.importance,
                    "priority": n.priority,
                    "estimated_hours": n.estimated_hours,
                    "status": n.status,
                    "progress_pct": n.progress_pct,
                    "confidence_level": n.confidence_level,
                    "relevant_companies": n.relevant_companies_list,
                    "started_at": _dt(n.started_at),
                    "completed_at": _dt(n.completed_at),
                    "last_studied_at": _dt(n.last_studied_at),
                    "created_at": _dt(n.created_at),
                    "study_logs": [
                        {
                            "id": sl.id,
                            "date": _date(sl.date),
                            "duration_minutes": sl.duration_minutes,
                            "activity_type": sl.activity_type,
                            "notes": sl.notes,
                            "created_at": _dt(sl.created_at),
                        }
                        for sl in n.study_logs
                    ],
                }
                for n in framework_nodes
            ],
            "companies": [
                {
                    "id": c.id,
                    "name": c.name,
                    "group_tag": c.group_tag,
                    "interview_stages": c.interview_stages_list,
                    "status": c.status,
                    "applied_at": _date(c.applied_at),
                    "notes": c.notes,
                    "prep_notes": c.prep_notes,
                    "topic_weights": [
                        {
                            "framework_node_id": tw.framework_node_id,
                            "weight": tw.weight,
                        }
                        for tw in c.topic_weights
                    ],
                }
                for c in companies
            ],
            "interview_questions": [
                {
                    "id": q.id,
                    "company": q.company,
                    "role": q.role,
                    "level": q.level,
                    "interview_round": q.interview_round,
                    "year": q.year,
                    "question_text": q.question_text,
                    "question_type": q.question_type,
                    "tags": q.tags_list,
                    "mapped_framework_node_id": q.mapped_framework_node_id,
                    "is_reviewed": q.is_reviewed,
                    "notes": q.notes,
                    "difficulty_estimate": q.difficulty_estimate,
                    "created_at": _dt(q.created_at),
                }
                for q in questions
            ],
            "interview_events": [
                {
                    "id": e.id,
                    "company_id": e.company_id,
                    "company_name": e.company_name,
                    "event_type": e.event_type,
                    "title": e.title,
                    "description": e.description,
                    "scheduled_at": _dt(e.scheduled_at),
                    "duration_minutes": e.duration_minutes,
                    "location": e.location,
                    "status": e.status,
                    "created_at": _dt(e.created_at),
                }
                for e in events
            ],
        }
    finally:
        db.close()


@app.post("/api/import/seed")
def import_seed():
    """Load all seed data files."""
    from src.backend.database import SessionLocal
    from src.backend.services.seed_loader import load_all_seeds

    db = SessionLocal()
    try:
        return load_all_seeds(db)
    finally:
        db.close()


def _parse_dt(val: str | None) -> datetime | None:
    """Parse ISO 8601 datetime string to datetime object."""
    if not val:
        return None
    return datetime.fromisoformat(val)


def _parse_date(val: str | None) -> date | None:
    """Parse ISO 8601 date string to date object."""
    if not val:
        return None
    return date.fromisoformat(val)


def _import_problems(db, problems_data: list[dict[str, Any]]) -> dict[str, int]:
    """Import problems, skipping duplicates by leetcode_id (if set) or title.

    Returns counts of inserted, skipped, and errors.
    """
    from src.backend.models.problem import Attempt, Problem

    inserted = 0
    skipped = 0
    errors = 0

    for item in problems_data:
        try:
            # Check for existing: by leetcode_id if present, else by title
            existing = None
            if item.get("leetcode_id"):
                existing = db.query(Problem).filter(
                    Problem.leetcode_id == item["leetcode_id"]
                ).first()
            if not existing and item.get("title"):
                existing = db.query(Problem).filter(
                    Problem.title == item["title"]
                ).first()

            if existing:
                skipped += 1
                continue

            p = Problem(
                leetcode_id=item.get("leetcode_id"),
                title=item["title"],
                url=item.get("url"),
                difficulty=item.get("difficulty"),
                tags=json.dumps(item["tags"], ensure_ascii=False)
                if isinstance(item.get("tags"), list)
                else item.get("tags"),
                pattern=item.get("pattern"),
                category=item.get("category", "algorithm"),
                source=item.get("source"),
                company_tags=json.dumps(item["company_tags"], ensure_ascii=False)
                if isinstance(item.get("company_tags"), list)
                else item.get("company_tags"),
                priority=item.get("priority", 2),
                is_completed=item.get("is_completed", False),
                comfort_level=item.get("comfort_level", 0),
                framework_node_id=item.get("framework_node_id"),
            )
            db.add(p)
            db.flush()

            # Import nested attempts
            for att_data in item.get("attempts", []):
                att = Attempt(
                    problem_id=p.id,
                    started_at=_parse_dt(att_data.get("started_at")),
                    duration_seconds=att_data.get("duration_seconds"),
                    result=att_data.get("result"),
                    approach_notes=att_data.get("approach_notes"),
                    complexity_time=att_data.get("complexity_time"),
                    complexity_space=att_data.get("complexity_space"),
                    comfort_after=att_data.get("comfort_after"),
                )
                db.add(att)

            inserted += 1
        except Exception:
            errors += 1
            logger.exception("Error importing problem: %s", item.get("title", "?"))

    return {"inserted": inserted, "skipped": skipped, "errors": errors}


def _import_framework_nodes(
    db, nodes_data: list[dict[str, Any]]
) -> dict[str, int]:
    """Import framework nodes, skipping duplicates by path.

    Returns counts of inserted, skipped, and errors.
    """
    from src.backend.models.framework import FrameworkNode, StudyLog

    inserted = 0
    skipped = 0
    errors = 0

    # Sort by depth so parents are created before children
    sorted_nodes = sorted(nodes_data, key=lambda n: n.get("depth", 0))

    # Map old path -> new id for parent resolution
    path_to_id: dict[str, int] = {}

    for item in sorted_nodes:
        try:
            path = item.get("path", "")
            existing = db.query(FrameworkNode).filter(
                FrameworkNode.path == path
            ).first()
            if existing:
                path_to_id[path] = existing.id
                skipped += 1
                continue

            # Resolve parent_id from path
            parent_id = None
            if "." in path:
                parent_path = path.rsplit(".", 1)[0]
                parent_id = path_to_id.get(parent_path)
                if parent_id is None:
                    parent_node = db.query(FrameworkNode).filter(
                        FrameworkNode.path == parent_path
                    ).first()
                    if parent_node:
                        parent_id = parent_node.id

            node = FrameworkNode(
                parent_id=parent_id,
                path=path,
                depth=item.get("depth", 0),
                title=item["title"],
                description=item.get("description"),
                importance=item.get("importance", 1.0),
                priority=item.get("priority", "P1"),
                estimated_hours=item.get("estimated_hours"),
                status=item.get("status", "not_started"),
                progress_pct=item.get("progress_pct", 0.0),
                confidence_level=item.get("confidence_level", 0),
                relevant_companies=json.dumps(
                    item["relevant_companies"], ensure_ascii=False
                )
                if isinstance(item.get("relevant_companies"), list)
                else item.get("relevant_companies"),
            )
            db.add(node)
            db.flush()
            path_to_id[path] = node.id

            # Import nested study logs
            for sl_data in item.get("study_logs", []):
                sl = StudyLog(
                    framework_node_id=node.id,
                    date=_parse_date(sl_data.get("date"))
                    or date.today(),
                    duration_minutes=sl_data["duration_minutes"],
                    activity_type=sl_data.get("activity_type"),
                    notes=sl_data.get("notes"),
                )
                db.add(sl)

            inserted += 1
        except Exception:
            errors += 1
            logger.exception(
                "Error importing framework node: %s", item.get("path", "?")
            )

    return {"inserted": inserted, "skipped": skipped, "errors": errors}


def _import_companies(db, companies_data: list[dict[str, Any]]) -> dict[str, int]:
    """Import companies, skipping duplicates by name.

    Returns counts of inserted, skipped, and errors.
    """
    from src.backend.models.company import Company, CompanyTopicWeight

    inserted = 0
    skipped = 0
    errors = 0

    for item in companies_data:
        try:
            name = item.get("name", "")
            existing = db.query(Company).filter(Company.name == name).first()
            if existing:
                skipped += 1
                continue

            c = Company(
                name=name,
                group_tag=item.get("group_tag"),
                interview_stages=json.dumps(
                    item["interview_stages"], ensure_ascii=False
                )
                if isinstance(item.get("interview_stages"), list)
                else item.get("interview_stages"),
                status=item.get("status", "applied"),
                applied_at=_parse_date(item.get("applied_at")),
                notes=item.get("notes"),
                prep_notes=item.get("prep_notes"),
            )
            db.add(c)
            db.flush()

            # Import nested topic weights
            for tw_data in item.get("topic_weights", []):
                tw = CompanyTopicWeight(
                    company_id=c.id,
                    framework_node_id=tw_data["framework_node_id"],
                    weight=tw_data.get("weight", 1.0),
                )
                db.add(tw)

            inserted += 1
        except Exception:
            errors += 1
            logger.exception("Error importing company: %s", item.get("name", "?"))

    return {"inserted": inserted, "skipped": skipped, "errors": errors}


def _import_questions(
    db, questions_data: list[dict[str, Any]]
) -> dict[str, int]:
    """Import interview questions (no dedup -- always insert).

    Returns counts of inserted and errors.
    """
    from src.backend.models.scraper import InterviewQuestion

    inserted = 0
    errors = 0

    for item in questions_data:
        try:
            q = InterviewQuestion(
                company=item.get("company"),
                role=item.get("role"),
                level=item.get("level"),
                interview_round=item.get("interview_round"),
                year=item.get("year"),
                question_text=item["question_text"],
                question_type=item.get("question_type"),
                tags=json.dumps(item["tags"], ensure_ascii=False)
                if isinstance(item.get("tags"), list)
                else item.get("tags"),
                mapped_framework_node_id=item.get("mapped_framework_node_id"),
                is_reviewed=item.get("is_reviewed", False),
                notes=item.get("notes"),
                difficulty_estimate=item.get("difficulty_estimate"),
            )
            db.add(q)
            inserted += 1
        except Exception:
            errors += 1
            logger.exception(
                "Error importing question: %s",
                item.get("question_text", "?")[:50],
            )

    return {"inserted": inserted, "skipped": 0, "errors": errors}


def _import_events(
    db, events_data: list[dict[str, Any]]
) -> dict[str, int]:
    """Import interview events (always insert, no dedup).

    Returns counts of inserted and errors.
    """
    from src.backend.models.timeline import InterviewEvent as IEvent

    inserted = 0
    errors = 0

    for item in events_data:
        try:
            e = IEvent(
                company_id=item.get("company_id"),
                company_name=item["company_name"],
                event_type=item["event_type"],
                title=item["title"],
                description=item.get("description"),
                scheduled_at=_parse_dt(item["scheduled_at"]),
                duration_minutes=item.get("duration_minutes"),
                location=item.get("location"),
                status=item.get("status", "upcoming"),
            )
            db.add(e)
            inserted += 1
        except Exception:
            errors += 1
            logger.exception(
                "Error importing event: %s", item.get("title", "?")
            )

    return {"inserted": inserted, "skipped": 0, "errors": errors}


@app.post("/api/import")
def import_data(payload: dict[str, Any]):
    """Import JSON data with merge semantics.

    Accepts the same format as GET /api/export.
    Skips existing records by unique key (leetcode_id/title, path, name).
    Returns per-section counts of {inserted, skipped, errors}.
    """
    from src.backend.database import SessionLocal

    db = SessionLocal()
    try:
        result: dict[str, dict[str, int]] = {}

        if "problems" in payload:
            result["problems"] = _import_problems(db, payload["problems"])
        if "framework_nodes" in payload:
            result["framework_nodes"] = _import_framework_nodes(
                db, payload["framework_nodes"]
            )
        if "companies" in payload:
            result["companies"] = _import_companies(db, payload["companies"])
        if "interview_questions" in payload:
            result["interview_questions"] = _import_questions(
                db, payload["interview_questions"]
            )
        if "interview_events" in payload:
            result["interview_events"] = _import_events(
                db, payload["interview_events"]
            )

        db.commit()
        return result
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@app.post("/api/import/csv")
async def import_csv(file: UploadFile = File(...)):
    """Import problems from a CSV file.

    Expected columns: leetcode_id, title, url, difficulty, pattern, category,
    source, priority, tags (semicolon-separated), company_tags (semicolon-separated).
    Skips existing by leetcode_id or title (same merge logic as JSON import).
    Returns {inserted, skipped, errors}.
    """
    from src.backend.database import SessionLocal

    content = await file.read()
    text = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))

    problems_data: list[dict[str, Any]] = []
    parse_errors = 0

    for row in reader:
        try:
            item: dict[str, Any] = {"title": row["title"]}
            if row.get("leetcode_id"):
                item["leetcode_id"] = int(row["leetcode_id"])
            item["url"] = row.get("url") or None
            item["difficulty"] = row.get("difficulty") or None
            item["pattern"] = row.get("pattern") or None
            item["category"] = row.get("category", "algorithm") or "algorithm"
            item["source"] = row.get("source") or None
            if row.get("priority"):
                item["priority"] = int(row["priority"])
            # Tags: semicolon-separated -> list
            tags_raw = row.get("tags", "")
            item["tags"] = (
                [t.strip() for t in tags_raw.split(";") if t.strip()]
                if tags_raw
                else []
            )
            company_raw = row.get("company_tags", "")
            item["company_tags"] = (
                [t.strip() for t in company_raw.split(";") if t.strip()]
                if company_raw
                else []
            )
            problems_data.append(item)
        except Exception:
            parse_errors += 1
            logger.exception("Error parsing CSV row: %s", row)

    db = SessionLocal()
    try:
        result = _import_problems(db, problems_data)
        result["errors"] += parse_errors
        db.commit()
        return result
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
