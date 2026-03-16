"""Problem and Attempt API routes."""
import json
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import Integer, func
from sqlalchemy.orm import Session

from src.backend.database import get_db
from src.backend.models.problem import Attempt, Problem
from src.backend.schemas.problem import (
    AttemptCreate,
    AttemptResponse,
    ProblemCreate,
    ProblemResponse,
    ProblemUpdate,
)
from src.backend.services.spaced_repetition import update_review_schedule

router = APIRouter()


def _problem_to_response(p: Problem) -> dict:
    """Convert Problem ORM to response dict with JSON fields decoded."""
    return {
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
        "created_at": p.created_at,
        "last_attempted_at": p.last_attempted_at,
        "next_review_at": p.next_review_at,
        "framework_node_id": p.framework_node_id,
    }


@router.get("/problems/review-queue", response_model=list[ProblemResponse])
def get_review_queue(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[dict]:
    """Return problems due for review (next_review_at <= now), most overdue first."""
    now = datetime.utcnow()
    problems = (
        db.query(Problem)
        .filter(
            Problem.next_review_at.isnot(None),
            Problem.next_review_at <= now,
        )
        .order_by(Problem.next_review_at.asc())
        .limit(limit)
        .all()
    )
    return [_problem_to_response(p) for p in problems]


@router.get("/problems/stats")
def get_problem_stats(db: Session = Depends(get_db)) -> dict:
    """Return aggregate statistics for problems."""
    total = db.query(func.count(Problem.id)).scalar() or 0
    completed = (
        db.query(func.count(Problem.id)).filter(Problem.is_completed.is_(True)).scalar() or 0
    )
    avg_comfort = db.query(func.avg(Problem.comfort_level)).scalar() or 0.0

    # By difficulty
    diff_rows = (
        db.query(Problem.difficulty, func.count(Problem.id))
        .group_by(Problem.difficulty)
        .all()
    )
    by_difficulty = {row[0] or "unknown": row[1] for row in diff_rows}

    # By pattern
    pattern_rows = (
        db.query(
            Problem.pattern,
            func.count(Problem.id),
            func.sum(func.cast(Problem.is_completed, Integer)),
            func.avg(Problem.comfort_level),
        )
        .filter(Problem.pattern.isnot(None))
        .group_by(Problem.pattern)
        .all()
    )
    by_pattern = [
        {
            "pattern": row[0],
            "count": row[1],
            "completed": row[2] or 0,
            "avg_comfort": round(float(row[3] or 0), 1),
        }
        for row in pattern_rows
    ]

    # Weak patterns
    weak_patterns = [p["pattern"] for p in by_pattern if p["avg_comfort"] < 3 and p["count"] > 0]

    # Attempt stats
    total_attempts = db.query(func.count(Attempt.id)).scalar() or 0
    avg_duration = (
        db.query(func.avg(Attempt.duration_seconds))
        .filter(Attempt.duration_seconds.isnot(None))
        .scalar()
    )

    return {
        "total": total,
        "completed": completed,
        "avg_comfort": round(float(avg_comfort), 1),
        "by_difficulty": by_difficulty,
        "by_pattern": by_pattern,
        "weak_patterns": weak_patterns,
        "total_attempts": total_attempts,
        "avg_duration_seconds": round(float(avg_duration or 0), 1),
    }


@router.get("/problems", response_model=list[ProblemResponse])
def list_problems(
    response: Response,
    difficulty: Literal["easy", "medium", "hard"] | None = None,
    pattern: str | None = None,
    source: str | None = None,
    company: str | None = None,
    is_completed: bool | None = None,
    category: str | None = None,
    sort_by: Literal[
        "comfort_level", "last_attempted_at", "next_review_at", "created_at"
    ] = "created_at",
    sort_order: Literal["asc", "desc"] = "desc",
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[dict]:
    """List problems with optional filters."""
    query = db.query(Problem)

    if difficulty:
        query = query.filter(Problem.difficulty == difficulty)
    if pattern:
        query = query.filter(Problem.pattern == pattern)
    if source:
        query = query.filter(Problem.source.contains(source))
    if company:
        query = query.filter(Problem.company_tags.contains(f'"{company}"'))
    if is_completed is not None:
        query = query.filter(Problem.is_completed == is_completed)
    if category:
        query = query.filter(Problem.category == category)

    # Total count for pagination header
    total_count = query.count()
    response.headers["X-Total-Count"] = str(total_count)

    # Sort
    sort_col = getattr(Problem, sort_by)
    order = sort_col.asc() if sort_order == "asc" else sort_col.desc()
    query = query.order_by(order)

    problems = query.offset(offset).limit(limit).all()
    return [_problem_to_response(p) for p in problems]


@router.post("/problems", response_model=ProblemResponse, status_code=201)
def create_problem(
    problem: ProblemCreate, db: Session = Depends(get_db)
) -> dict:
    """Create a new problem."""
    if problem.leetcode_id is not None:
        existing = (
            db.query(Problem)
            .filter(Problem.leetcode_id == problem.leetcode_id)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Problem with leetcode_id {problem.leetcode_id} already exists",
            )

    db_problem = Problem(
        leetcode_id=problem.leetcode_id,
        title=problem.title,
        url=problem.url,
        difficulty=problem.difficulty,
        tags=json.dumps(problem.tags, ensure_ascii=False),
        pattern=problem.pattern,
        category=problem.category,
        source=problem.source,
        company_tags=json.dumps(problem.company_tags, ensure_ascii=False),
        priority=problem.priority,
        framework_node_id=problem.framework_node_id,
        created_at=datetime.utcnow(),
    )
    db.add(db_problem)
    db.commit()
    db.refresh(db_problem)
    return _problem_to_response(db_problem)


@router.put("/problems/{problem_id}", response_model=ProblemResponse)
def update_problem(
    problem_id: int,
    problem_update: ProblemUpdate,
    db: Session = Depends(get_db),
) -> dict:
    """Update a problem (partial update)."""
    db_problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not db_problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    update_data = problem_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field in ("tags", "company_tags") and value is not None:
            setattr(db_problem, field, json.dumps(value, ensure_ascii=False))
        else:
            setattr(db_problem, field, value)

    db.commit()
    db.refresh(db_problem)
    return _problem_to_response(db_problem)


@router.delete("/problems/{problem_id}", status_code=204)
def delete_problem(problem_id: int, db: Session = Depends(get_db)) -> None:
    """Delete a problem and all associated data."""
    db_problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not db_problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    db.delete(db_problem)
    db.commit()


@router.post(
    "/problems/{problem_id}/attempts",
    response_model=AttemptResponse,
    status_code=201,
)
def create_attempt(
    problem_id: int,
    attempt_data: AttemptCreate,
    db: Session = Depends(get_db),
) -> Attempt:
    """Record an attempt at a problem."""
    db_problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not db_problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    now = datetime.utcnow()

    # Compute next review BEFORE updating last_attempted_at
    db_problem.next_review_at = update_review_schedule(
        last_attempted_at=db_problem.last_attempted_at,
        now=now,
        comfort_after=attempt_data.comfort_after,
    )

    # Update problem state
    db_problem.last_attempted_at = now
    db_problem.comfort_level = attempt_data.comfort_after
    if attempt_data.comfort_after >= 3:
        db_problem.is_completed = True

    attempt = Attempt(
        problem_id=problem_id,
        started_at=now,
        duration_seconds=attempt_data.duration_seconds,
        result=attempt_data.result,
        approach_notes=attempt_data.approach_notes,
        complexity_time=attempt_data.complexity_time,
        complexity_space=attempt_data.complexity_space,
        comfort_after=attempt_data.comfort_after,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt


@router.get(
    "/problems/{problem_id}/attempts",
    response_model=list[AttemptResponse],
)
def list_attempts(
    problem_id: int, db: Session = Depends(get_db)
) -> list[Attempt]:
    """List all attempts for a problem, newest first."""
    db_problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not db_problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return (
        db.query(Attempt)
        .filter(Attempt.problem_id == problem_id)
        .order_by(Attempt.started_at.desc())
        .all()
    )


@router.post("/problems/{problem_id}/review")
async def review_problem(
    problem_id: int,
    body: dict,
    db: Session = Depends(get_db),
) -> dict:
    """Get LLM review of an approach for a problem."""
    db_problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not db_problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    approach_text = body.get("approach_text", "")
    if not approach_text:
        raise HTTPException(status_code=422, detail="approach_text is required")

    from src.backend.services.llm_service import LLMService

    system_prompt = (
        "You are an expert algorithm interview coach for a mid-senior MLE candidate.\n\n"
        "Your job:\n"
        "1. Evaluate the candidate's approach for correctness and optimality\n"
        "2. Push them toward the OPTIMAL solution in the FEWEST exchanges\n"
        "3. Be concise and direct -- this is speed training, not tutoring\n\n"
        "Rules:\n"
        "- If approach is optimal: confirm, ask for complexity, suggest edge cases\n"
        "- If approach works but suboptimal: hint at the better pattern\n"
        "- If approach is wrong: identify the specific flaw, give a targeted hint\n"
        "- Always state the optimal time/space complexity\n"
        "- Reference specific patterns: sliding window, monotonic stack, union-find, etc.\n\n"
        'Response format (JSON):\n'
        '{\n'
        '  "verdict": "optimal|suboptimal|incorrect|needs_clarification",\n'
        '  "feedback": "concise feedback (2-3 sentences max)",\n'
        '  "hint": "one-line hint if suboptimal/incorrect (null if optimal)",\n'
        '  "optimal_complexity": {"time": "O(...)", "space": "O(...)"},\n'
        '  "pattern": "the relevant algorithm pattern",\n'
        '  "follow_up": "one follow-up question to deepen understanding"\n'
        "}"
    )

    user_msg = (
        f"Problem: {db_problem.title} "
        f"(difficulty: {db_problem.difficulty}, pattern: {db_problem.pattern})\n\n"
        f"My approach: {approach_text}"
    )

    llm = LLMService()
    result = await llm.chat(
        system_prompt=system_prompt,
        messages=[{"role": "user", "content": user_msg}],
        response_format="json",
    )

    # Store in latest attempt if exists
    latest_attempt = (
        db.query(Attempt)
        .filter(Attempt.problem_id == problem_id)
        .order_by(Attempt.started_at.desc())
        .first()
    )
    if latest_attempt:
        latest_attempt.llm_review = json.dumps(
            result if isinstance(result, dict) else {"text": result},
            ensure_ascii=False,
        )
        db.commit()

    return result
