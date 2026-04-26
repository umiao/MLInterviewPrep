"""Behavioral Questions API routes."""
import json
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.backend.database import get_db
from src.backend.models.behavioral import (
    BehavioralExample,
    BehavioralQuestion,
    QuestionExampleLink,
)
from src.backend.models.behavioral_facet import (
    BehavioralFacet,
    ExampleFacetTag,
)
from src.backend.models.behavioral_theme import (
    BehavioralTheme,
    ExampleThemeTag,
    QuestionThemeTag,
)
from src.backend.schemas.behavioral import (
    BehavioralExampleCreate,
    BehavioralExampleResponse,
    BehavioralExampleUpdate,
    BehavioralQuestionCreate,
    BehavioralQuestionResponse,
    BehavioralQuestionUpdate,
    CategorySummary,
    CoverageCell,
    QuestionExampleLinkCreate,
    QuestionExampleLinkResponse,
)
from src.backend.schemas.behavioral_theme import BehavioralThemeResponse

router = APIRouter()


# ---------------------------------------------------------------------------
# Questions CRUD
# ---------------------------------------------------------------------------


@router.get("/behavioral/questions", response_model=list[BehavioralQuestionResponse])
def list_questions(
    category_id: str | None = Query(default=None),
    search: str | None = Query(default=None),
    theme: str | None = Query(default=None),
    theme_mode: str = Query(default="or"),
    db: Session = Depends(get_db),
) -> list[dict]:
    """List behavioral questions with optional filters.

    Args:
        category_id: Filter by category.
        search: Search in question text.
        theme: Comma-separated theme slug list.
        theme_mode: "or" (union) or "and" (intersection) for multi-theme filter.
        db: Database session.

    Returns:
        List of questions with example counts.
    """
    query = db.query(BehavioralQuestion)
    if category_id:
        query = query.filter(BehavioralQuestion.category_id == category_id)
    if search:
        query = query.filter(BehavioralQuestion.text.ilike(f"%{search}%"))

    if theme:
        if theme_mode not in ("or", "and"):
            raise HTTPException(
                status_code=400,
                detail="theme_mode must be 'or' or 'and'",
            )
        slugs = [s.strip() for s in theme.split(",") if s.strip()]
        if not slugs:
            raise HTTPException(status_code=400, detail="empty theme filter")
        theme_rows = (
            db.query(BehavioralTheme).filter(BehavioralTheme.slug.in_(slugs)).all()
        )
        found_slugs = {t.slug for t in theme_rows}
        unknown = [s for s in slugs if s not in found_slugs]
        if unknown:
            raise HTTPException(
                status_code=400,
                detail=f"unknown theme slug(s): {','.join(unknown)}",
            )
        theme_ids = [t.id for t in theme_rows]
        if theme_mode == "or":
            query = query.join(
                QuestionThemeTag,
                QuestionThemeTag.question_id == BehavioralQuestion.id,
            ).filter(QuestionThemeTag.theme_id.in_(theme_ids)).distinct()
        else:  # and
            matching_ids = (
                select(QuestionThemeTag.question_id)
                .where(QuestionThemeTag.theme_id.in_(theme_ids))
                .group_by(QuestionThemeTag.question_id)
                .having(
                    func.count(func.distinct(QuestionThemeTag.theme_id))
                    == len(theme_ids)
                )
            )
            query = query.filter(BehavioralQuestion.id.in_(matching_ids))

    questions = query.order_by(BehavioralQuestion.category_id, BehavioralQuestion.question_id).all()

    # Batch-fetch theme tags for all questions in one query to avoid N+1.
    q_ids = [q.id for q in questions]
    theme_rows_by_q: dict[int, list[dict]] = {qid: [] for qid in q_ids}
    if q_ids:
        rows = (
            db.query(
                QuestionThemeTag.question_id,
                BehavioralTheme.slug,
                BehavioralTheme.label,
                BehavioralTheme.display_order,
            )
            .join(BehavioralTheme, BehavioralTheme.id == QuestionThemeTag.theme_id)
            .filter(QuestionThemeTag.question_id.in_(q_ids))
            .order_by(BehavioralTheme.display_order, BehavioralTheme.slug)
            .all()
        )
        for qid, slug, label, _order in rows:
            theme_rows_by_q[qid].append({"slug": slug, "label": label})

    result = []
    for q in questions:
        link_count = (
            db.query(func.count(QuestionExampleLink.id))
            .filter(QuestionExampleLink.question_id == q.id)
            .scalar()
            or 0
        )
        result.append({
            "id": q.id,
            "question_id": q.question_id,
            "text": q.text,
            "category_id": q.category_id,
            "category_name": q.category_name,
            "original_category": q.original_category,
            "difficulty": q.difficulty,
            "company_target": q.company_target,
            "created_at": q.created_at,
            "example_count": link_count,
            "theme_tags": theme_rows_by_q.get(q.id, []),
            "probe_notes": (
                json.loads(q.probe_notes) if q.probe_notes else None
            ),
            "probe_notes_updated_at": q.probe_notes_updated_at,
        })
    return result


# ---------------------------------------------------------------------------
# Themes
# ---------------------------------------------------------------------------


@router.get("/behavioral/themes", response_model=list[BehavioralThemeResponse])
def list_themes(db: Session = Depends(get_db)) -> list[dict]:
    """Return all behavioral themes with question/example counts.

    Args:
        db: Database session.

    Returns:
        List of theme summaries ordered by display_order.
    """
    themes = (
        db.query(BehavioralTheme)
        .order_by(BehavioralTheme.display_order, BehavioralTheme.slug)
        .all()
    )
    result = []
    for t in themes:
        q_count = (
            db.query(func.count(QuestionThemeTag.question_id))
            .filter(QuestionThemeTag.theme_id == t.id)
            .scalar()
            or 0
        )
        ex_count = (
            db.query(func.count(ExampleThemeTag.example_id))
            .filter(ExampleThemeTag.theme_id == t.id)
            .scalar()
            or 0
        )
        result.append({
            "id": t.id,
            "slug": t.slug,
            "label": t.label,
            "description": t.description,
            "display_order": t.display_order,
            "question_count": q_count,
            "example_count": ex_count,
        })
    return result


@router.post("/behavioral/questions", response_model=BehavioralQuestionResponse, status_code=201)
def create_question(
    data: BehavioralQuestionCreate,
    db: Session = Depends(get_db),
) -> dict:
    """Create a behavioral question.

    Args:
        data: Question creation data.
        db: Database session.

    Returns:
        Created question.
    """
    existing = db.query(BehavioralQuestion).filter(
        BehavioralQuestion.question_id == data.question_id
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Question ID already exists")

    q = BehavioralQuestion(
        question_id=data.question_id,
        text=data.text,
        category_id=data.category_id,
        category_name=data.category_name,
        original_category=data.original_category,
        difficulty=data.difficulty,
        company_target=data.company_target,
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    return {
        **q.__dict__,
        "example_count": 0,
        "probe_notes": None,
        "probe_notes_updated_at": None,
    }


@router.put("/behavioral/questions/{question_db_id}", response_model=BehavioralQuestionResponse)
def update_question(
    question_db_id: int,
    data: BehavioralQuestionUpdate,
    db: Session = Depends(get_db),
) -> dict:
    """Update a behavioral question.

    Args:
        question_db_id: Database ID of the question.
        data: Fields to update.
        db: Database session.

    Returns:
        Updated question.
    """
    q = db.query(BehavioralQuestion).get(question_db_id)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "probe_notes":
            if value is None:
                q.probe_notes = None
            else:
                q.probe_notes = json.dumps(value, ensure_ascii=False)
            q.probe_notes_updated_at = datetime.utcnow()
        else:
            setattr(q, key, value)

    db.commit()
    db.refresh(q)
    link_count = (
        db.query(func.count(QuestionExampleLink.id))
        .filter(QuestionExampleLink.question_id == q.id)
        .scalar()
        or 0
    )
    return {
        **q.__dict__,
        "example_count": link_count,
        "probe_notes": json.loads(q.probe_notes) if q.probe_notes else None,
        "probe_notes_updated_at": q.probe_notes_updated_at,
    }


@router.delete("/behavioral/questions/{question_db_id}", status_code=204)
def delete_question(
    question_db_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete a behavioral question.

    Args:
        question_db_id: Database ID of the question.
        db: Database session.
    """
    q = db.query(BehavioralQuestion).get(question_db_id)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    db.delete(q)
    db.commit()


# ---------------------------------------------------------------------------
# Examples CRUD
# ---------------------------------------------------------------------------


def _build_example_response(db: Session, ex: BehavioralExample) -> dict:
    """Build a full example response with linked questions, themes, and facets.

    Args:
        db: Database session.
        ex: Example ORM object.

    Returns:
        Dict suitable for BehavioralExampleResponse.
    """
    links = (
        db.query(QuestionExampleLink)
        .filter(QuestionExampleLink.example_id == ex.id)
        .all()
    )
    linked_questions = []
    for link in links:
        q = db.query(BehavioralQuestion).get(link.question_id)
        if q:
            linked_questions.append({
                "id": q.id,
                "question_id": q.question_id,
                "text": q.text,
                "category_id": q.category_id,
                "relevance_note": link.relevance_note,
                "is_primary": bool(link.is_primary),
            })

    theme_rows = (
        db.query(BehavioralTheme.slug, BehavioralTheme.label)
        .join(ExampleThemeTag, ExampleThemeTag.theme_id == BehavioralTheme.id)
        .filter(ExampleThemeTag.example_id == ex.id)
        .order_by(BehavioralTheme.display_order, BehavioralTheme.slug)
        .all()
    )
    theme_tags = [{"slug": slug, "label": label} for slug, label in theme_rows]

    facet_rows = (
        db.query(BehavioralFacet.slug, BehavioralFacet.label)
        .join(ExampleFacetTag, ExampleFacetTag.facet_id == BehavioralFacet.id)
        .filter(ExampleFacetTag.example_id == ex.id)
        .order_by(BehavioralFacet.display_order, BehavioralFacet.slug)
        .all()
    )
    facet_tags = [{"slug": slug, "label": label} for slug, label in facet_rows]

    return {
        "id": ex.id,
        "example_id": ex.example_id,
        "title": ex.title,
        "source_project": ex.source_project,
        "situation": ex.situation,
        "task": ex.task,
        "action": ex.action,
        "result": ex.result,
        "evidence_quotes": ex.evidence_quotes_list,
        "principle_tags": ex.principle_tags_list,
        "risk_statement": ex.risk_statement,
        "analogy": ex.analogy,
        "tech_terms": ex.tech_terms_dict,
        "cn_elevator_pitch": ex.cn_elevator_pitch,
        "created_at": ex.created_at,
        "is_golden": bool(ex.is_golden),
        "golden_at": ex.golden_at,
        "is_signature": bool(getattr(ex, "is_signature", False)),
        "signature_at": getattr(ex, "signature_at", None),
        "theme_tags": theme_tags,
        "facet_tags": facet_tags,
        "linked_questions": linked_questions,
    }


@router.get("/behavioral/examples", response_model=list[BehavioralExampleResponse])
def list_examples(
    principle_tag: str | None = Query(default=None),
    search: str | None = Query(default=None),
    theme: str | None = Query(default=None),
    theme_mode: str = Query(default="or"),
    db: Session = Depends(get_db),
) -> list[dict]:
    """List behavioral examples with optional filters.

    Args:
        principle_tag: Filter by principle tag.
        search: Search in title or STAR fields.
        theme: Comma-separated theme slug list.
        theme_mode: "or" (union) or "and" (intersection) for multi-theme filter.
        db: Database session.

    Returns:
        List of examples with linked questions.
    """
    query = db.query(BehavioralExample)
    if principle_tag:
        query = query.filter(
            BehavioralExample.principle_tags.ilike(f'%"{principle_tag}"%')
        )
    if search:
        query = query.filter(
            BehavioralExample.title.ilike(f"%{search}%")
            | BehavioralExample.situation.ilike(f"%{search}%")
            | BehavioralExample.action.ilike(f"%{search}%")
        )

    if theme:
        if theme_mode not in ("or", "and"):
            raise HTTPException(
                status_code=400,
                detail="theme_mode must be 'or' or 'and'",
            )
        slugs = [s.strip() for s in theme.split(",") if s.strip()]
        if not slugs:
            raise HTTPException(status_code=400, detail="empty theme filter")
        theme_rows = (
            db.query(BehavioralTheme).filter(BehavioralTheme.slug.in_(slugs)).all()
        )
        found_slugs = {t.slug for t in theme_rows}
        unknown = [s for s in slugs if s not in found_slugs]
        if unknown:
            raise HTTPException(
                status_code=400,
                detail=f"unknown theme slug(s): {','.join(unknown)}",
            )
        theme_ids = [t.id for t in theme_rows]
        if theme_mode == "or":
            query = query.join(
                ExampleThemeTag,
                ExampleThemeTag.example_id == BehavioralExample.id,
            ).filter(ExampleThemeTag.theme_id.in_(theme_ids)).distinct()
        else:  # and
            matching_ids = (
                select(ExampleThemeTag.example_id)
                .where(ExampleThemeTag.theme_id.in_(theme_ids))
                .group_by(ExampleThemeTag.example_id)
                .having(
                    func.count(func.distinct(ExampleThemeTag.theme_id))
                    == len(theme_ids)
                )
            )
            query = query.filter(BehavioralExample.id.in_(matching_ids))

    examples = query.order_by(BehavioralExample.example_id).all()
    return [_build_example_response(db, ex) for ex in examples]


@router.get(
    "/behavioral/examples/by-example-id/{example_id}",
    response_model=BehavioralExampleResponse,
)
def get_example_by_example_id(
    example_id: str,
    db: Session = Depends(get_db),
) -> dict:
    """Get a single behavioral example by its string example_id (e.g. "EX-30").

    Args:
        example_id: String example identifier (e.g. "EX-30").
        db: Database session.

    Returns:
        Example with linked questions.
    """
    ex = (
        db.query(BehavioralExample)
        .filter(BehavioralExample.example_id == example_id)
        .first()
    )
    if not ex:
        raise HTTPException(status_code=404, detail="Example not found")
    return _build_example_response(db, ex)


@router.get("/behavioral/examples/{example_db_id}", response_model=BehavioralExampleResponse)
def get_example(
    example_db_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """Get a single behavioral example with linked questions.

    Args:
        example_db_id: Database ID of the example.
        db: Database session.

    Returns:
        Example with linked questions.
    """
    ex = db.query(BehavioralExample).get(example_db_id)
    if not ex:
        raise HTTPException(status_code=404, detail="Example not found")
    return _build_example_response(db, ex)


@router.post("/behavioral/examples", response_model=BehavioralExampleResponse, status_code=201)
def create_example(
    data: BehavioralExampleCreate,
    db: Session = Depends(get_db),
) -> dict:
    """Create a behavioral example.

    Args:
        data: Example creation data.
        db: Database session.

    Returns:
        Created example.
    """
    existing = db.query(BehavioralExample).filter(
        BehavioralExample.example_id == data.example_id
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Example ID already exists")

    ex = BehavioralExample(
        example_id=data.example_id,
        title=data.title,
        source_project=data.source_project,
        situation=data.situation,
        task=data.task,
        action=data.action,
        result=data.result,
        evidence_quotes=json.dumps(data.evidence_quotes, ensure_ascii=False),
        principle_tags=json.dumps(data.principle_tags, ensure_ascii=False),
        risk_statement=data.risk_statement,
        analogy=data.analogy,
        tech_terms=json.dumps(data.tech_terms, ensure_ascii=False) if data.tech_terms else None,
    )
    db.add(ex)
    db.commit()
    db.refresh(ex)
    return _build_example_response(db, ex)


@router.put("/behavioral/examples/{example_db_id}", response_model=BehavioralExampleResponse)
def update_example(
    example_db_id: int,
    data: BehavioralExampleUpdate,
    db: Session = Depends(get_db),
) -> dict:
    """Update a behavioral example.

    Args:
        example_db_id: Database ID of the example.
        data: Fields to update.
        db: Database session.

    Returns:
        Updated example.
    """
    ex = db.query(BehavioralExample).get(example_db_id)
    if not ex:
        raise HTTPException(status_code=404, detail="Example not found")

    update_data = data.model_dump(exclude_unset=True)

    # Golden flag: false -> true stamps golden_at; true -> false leaves it.
    if "is_golden" in update_data:
        new_golden = bool(update_data["is_golden"])
        if new_golden and not ex.is_golden:
            ex.golden_at = datetime.utcnow()

    # Signature flag: false -> true stamps signature_at; true -> false leaves it.
    if "is_signature" in update_data:
        new_signature = bool(update_data["is_signature"])
        if new_signature and not getattr(ex, "is_signature", False):
            ex.signature_at = datetime.utcnow()

    for key, value in update_data.items():
        if key in ("evidence_quotes", "principle_tags"):
            setattr(ex, key, json.dumps(value, ensure_ascii=False))
        elif key == "tech_terms":
            ex.tech_terms = json.dumps(value, ensure_ascii=False) if value else None
        else:
            setattr(ex, key, value)

    db.commit()
    db.refresh(ex)
    return _build_example_response(db, ex)


@router.delete("/behavioral/examples/{example_db_id}", status_code=204)
def delete_example(
    example_db_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete a behavioral example.

    Args:
        example_db_id: Database ID of the example.
        db: Database session.
    """
    ex = db.query(BehavioralExample).get(example_db_id)
    if not ex:
        raise HTTPException(status_code=404, detail="Example not found")
    db.delete(ex)
    db.commit()


# ---------------------------------------------------------------------------
# Links CRUD
# ---------------------------------------------------------------------------


@router.post("/behavioral/links", response_model=QuestionExampleLinkResponse, status_code=201)
def create_link(
    data: QuestionExampleLinkCreate,
    db: Session = Depends(get_db),
) -> QuestionExampleLink:
    """Create a question-example link.

    Args:
        data: Link creation data.
        db: Database session.

    Returns:
        Created link.
    """
    # Validate references
    q = db.query(BehavioralQuestion).get(data.question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    ex = db.query(BehavioralExample).get(data.example_id)
    if not ex:
        raise HTTPException(status_code=404, detail="Example not found")

    # Check for duplicate
    existing = (
        db.query(QuestionExampleLink)
        .filter(
            QuestionExampleLink.question_id == data.question_id,
            QuestionExampleLink.example_id == data.example_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Link already exists")

    # Enforce single-primary-per-question invariant at the application layer
    # before the DB constraint fires, so we return a clean 409 instead of a
    # raw IntegrityError surfacing as 500.
    if data.is_primary:
        prior_primary = (
            db.query(QuestionExampleLink)
            .filter(
                QuestionExampleLink.question_id == data.question_id,
                QuestionExampleLink.is_primary.is_(True),
            )
            .first()
        )
        if prior_primary:
            raise HTTPException(
                status_code=409,
                detail="Question already has a primary example link",
            )

    link = QuestionExampleLink(
        question_id=data.question_id,
        example_id=data.example_id,
        relevance_note=data.relevance_note,
        is_primary=bool(data.is_primary),
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


@router.delete("/behavioral/links/{link_id}", status_code=204)
def delete_link(
    link_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete a question-example link.

    Args:
        link_id: Database ID of the link.
        db: Database session.
    """
    link = db.query(QuestionExampleLink).get(link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    db.delete(link)
    db.commit()


# ---------------------------------------------------------------------------
# Analytics / Visualization endpoints
# ---------------------------------------------------------------------------


@router.get("/behavioral/categories", response_model=list[CategorySummary])
def list_categories(db: Session = Depends(get_db)) -> list[dict]:
    """List all BQ categories with coverage stats.

    Args:
        db: Database session.

    Returns:
        List of category summaries with question/example counts.
    """
    categories = (
        db.query(
            BehavioralQuestion.category_id,
            BehavioralQuestion.category_name,
        )
        .distinct()
        .order_by(BehavioralQuestion.category_id)
        .all()
    )

    result = []
    for cat_id, cat_name in categories:
        q_count = (
            db.query(func.count(BehavioralQuestion.id))
            .filter(BehavioralQuestion.category_id == cat_id)
            .scalar()
            or 0
        )
        # Questions with at least 1 example
        covered = (
            db.query(func.count(func.distinct(QuestionExampleLink.question_id)))
            .join(BehavioralQuestion, QuestionExampleLink.question_id == BehavioralQuestion.id)
            .filter(BehavioralQuestion.category_id == cat_id)
            .scalar()
            or 0
        )
        # Total example links in this category
        ex_count = (
            db.query(func.count(QuestionExampleLink.id))
            .join(BehavioralQuestion, QuestionExampleLink.question_id == BehavioralQuestion.id)
            .filter(BehavioralQuestion.category_id == cat_id)
            .scalar()
            or 0
        )
        result.append({
            "category_id": cat_id,
            "category_name": cat_name,
            "question_count": q_count,
            "covered_count": covered,
            "example_count": ex_count,
        })

    return result


@router.get("/behavioral/coverage-matrix", response_model=list[CoverageCell])
def get_coverage_matrix(db: Session = Depends(get_db)) -> list[dict]:
    """Get example-category coverage matrix for visualization.

    Args:
        db: Database session.

    Returns:
        List of cells: (example, category, link_count).
    """
    # Get all examples
    examples = db.query(BehavioralExample).order_by(BehavioralExample.example_id).all()
    categories = (
        db.query(
            BehavioralQuestion.category_id,
            BehavioralQuestion.category_name,
        )
        .distinct()
        .order_by(BehavioralQuestion.category_id)
        .all()
    )

    result = []
    for ex in examples:
        for cat_id, cat_name in categories:
            count = (
                db.query(func.count(QuestionExampleLink.id))
                .join(BehavioralQuestion, QuestionExampleLink.question_id == BehavioralQuestion.id)
                .filter(
                    QuestionExampleLink.example_id == ex.id,
                    BehavioralQuestion.category_id == cat_id,
                )
                .scalar()
                or 0
            )
            if count > 0:
                result.append({
                    "example_id": ex.example_id,
                    "example_title": ex.title,
                    "category_id": cat_id,
                    "category_name": cat_name,
                    "link_count": count,
                })

    return result


@router.get("/behavioral/gaps")
def get_gaps(db: Session = Depends(get_db)) -> dict:
    """Identify questions without any examples (gap analysis).

    Args:
        db: Database session.

    Returns:
        Dict with uncovered questions grouped by category.
    """
    # All questions without any link
    all_questions = db.query(BehavioralQuestion).all()
    uncovered = []
    for q in all_questions:
        link_count = (
            db.query(func.count(QuestionExampleLink.id))
            .filter(QuestionExampleLink.question_id == q.id)
            .scalar()
            or 0
        )
        if link_count == 0:
            uncovered.append({
                "id": q.id,
                "question_id": q.question_id,
                "text": q.text,
                "category_id": q.category_id,
                "category_name": q.category_name,
            })

    # Group by category
    by_category: dict[str, list] = {}
    for q in uncovered:
        cat = q["category_id"]
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(q)

    return {
        "total_questions": len(all_questions),
        "uncovered_count": len(uncovered),
        "coverage_pct": round(
            (1 - len(uncovered) / max(len(all_questions), 1)) * 100, 1
        ),
        "uncovered_by_category": by_category,
    }


# ---------------------------------------------------------------------------
#  Story Arcs (project narrative map)
# ---------------------------------------------------------------------------


@router.get("/behavioral/story-arcs")
def get_story_arcs(db: Session = Depends(get_db)) -> dict:
    """Return story arc data with live example metadata from the database.

    Merges static arc definitions from bq_story_arcs.json with live
    example data (title, link count, principle tags) from the database.
    """
    docs_dir = Path(__file__).resolve().parent.parent.parent.parent / "docs"
    arcs_path = docs_dir / "bq_story_arcs.json"

    if not arcs_path.exists():
        raise HTTPException(status_code=404, detail="Story arcs data not found")

    with open(arcs_path, encoding="utf-8") as f:
        arcs_data = json.load(f)

    # Build lookup: example_id -> (title, link_count, principle_tags)
    examples = db.query(BehavioralExample).all()
    ex_map: dict[str, dict] = {}
    for ex in examples:
        link_count = (
            db.query(func.count(QuestionExampleLink.id))
            .filter(QuestionExampleLink.example_id == ex.id)
            .scalar()
        )
        tags = json.loads(ex.principle_tags) if ex.principle_tags else []
        ex_map[ex.example_id] = {
            "title": ex.title,
            "source_project": ex.source_project,
            "situation": ex.situation,
            "link_count": link_count,
            "principle_tags": tags,
        }

    # Enrich arc examples with live data
    for arc in arcs_data.get("arcs", []):
        for ex_entry in arc.get("examples", []):
            eid = ex_entry["example_id"]
            live = ex_map.get(eid, {})
            ex_entry["title"] = live.get("title", eid)
            ex_entry["source_project"] = live.get("source_project")
            ex_entry["situation"] = live.get("situation")
            ex_entry["link_count"] = live.get("link_count", 0)
            ex_entry["principle_tags_live"] = live.get("principle_tags", [])

    return arcs_data
