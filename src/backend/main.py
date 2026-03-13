"""FastAPI application entry point."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func

from src.backend.config import get_settings
from src.backend.database import init_db
from src.backend.routers.companies import router as companies_router
from src.backend.routers.framework import router as framework_router
from src.backend.routers.problems import router as problems_router
from src.backend.routers.qa import router as qa_router
from src.backend.routers.scraper import router as scraper_router

logger = logging.getLogger(__name__)


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


@app.get("/api/health")
def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}


app.include_router(problems_router, prefix="/api")
app.include_router(qa_router, prefix="/api")
app.include_router(framework_router, prefix="/api")
app.include_router(companies_router, prefix="/api")
app.include_router(scraper_router, prefix="/api")


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

    db = SessionLocal()
    try:
        problems = db.query(Problem).all()
        framework_nodes = db.query(FrameworkNode).all()
        companies = db.query(Company).all()
        questions = db.query(InterviewQuestion).all()

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
