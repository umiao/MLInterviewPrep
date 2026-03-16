"""Scraper API routes."""
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.backend.database import get_db
from src.backend.models.scraper import InterviewQuestion, ScrapedPage, SeedURL
from src.backend.schemas.scraper import (
    InterviewQuestionResponse,
    PasteRequest,
    ScraperRunRequest,
    SeedURLCreate,
    SeedURLResponse,
)
from src.backend.scraper.extractors import compute_content_hash
from src.backend.services.llm_service import LLMService
from src.backend.services.question_extractor import extract_questions

router = APIRouter()


@dataclass
class ScraperJobStatus:
    """Status of a background scraper job."""

    job_id: str
    status: str = "running"
    seeds_total: int = 0
    seeds_processed: int = 0
    questions_found: int = 0
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    errors: list[str] = field(default_factory=list)


_scraper_jobs: dict[str, ScraperJobStatus] = {}


# -- Seed URL endpoints --

@router.get("/scraper/seeds", response_model=list[SeedURLResponse])
def list_seed_urls(
    source_site: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[SeedURL]:
    """List seed URLs with optional filters."""
    query = db.query(SeedURL)
    if source_site:
        query = query.filter(SeedURL.source_site == source_site)
    if is_active is not None:
        query = query.filter(SeedURL.is_active == is_active)
    return query.all()


@router.post("/scraper/seeds", response_model=SeedURLResponse, status_code=201)
def create_seed_url(
    seed: SeedURLCreate, db: Session = Depends(get_db)
) -> SeedURL:
    """Create a new seed URL."""
    existing = db.query(SeedURL).filter(SeedURL.url == seed.url).first()
    if existing:
        raise HTTPException(status_code=409, detail="Seed URL already exists")

    db_seed = SeedURL(
        url=seed.url,
        source_site=seed.source_site,
        company=seed.company,
        role_filter=seed.role_filter,
        check_interval_hours=seed.check_interval_hours,
    )
    db.add(db_seed)
    db.commit()
    db.refresh(db_seed)
    return db_seed


# -- Paste endpoint --

@router.post("/scraper/paste")
async def paste_experience(
    paste: PasteRequest, db: Session = Depends(get_db)
) -> dict:
    """Extract interview questions from pasted text."""
    content_hash = compute_content_hash(paste.text)

    existing_page = (
        db.query(ScrapedPage)
        .filter(ScrapedPage.content_hash == content_hash, ScrapedPage.url == "manual_paste")
        .first()
    )
    if existing_page:
        questions = (
            db.query(InterviewQuestion)
            .filter(InterviewQuestion.scraped_page_id == existing_page.id)
            .all()
        )
        return {
            "questions_count": len(questions),
            "questions": [
                {
                    "id": q.id,
                    "question_text": q.question_text,
                    "question_type": q.question_type,
                    "company": q.company,
                    "role": q.role,
                }
                for q in questions
            ],
            "was_duplicate": True,
        }

    page = ScrapedPage(
        url="manual_paste",
        extracted_text=paste.text,
        content_hash=content_hash,
        seed_url_id=None,
    )
    db.add(page)
    db.flush()

    context = {}
    if paste.company:
        context["company"] = paste.company
    if paste.role:
        context["role"] = paste.role

    llm = LLMService()
    extracted = await extract_questions(llm, paste.text, context or None)

    questions = []
    for q_data in extracted:
        q = InterviewQuestion(
            scraped_page_id=page.id,
            company=q_data.get("company"),
            role=q_data.get("role"),
            level=q_data.get("level"),
            interview_round=q_data.get("round"),
            question_text=q_data["question_text"],
            question_type=q_data.get("question_type"),
            tags=json.dumps(q_data.get("tags", []), ensure_ascii=False),
        )
        db.add(q)
        questions.append(q)

    db.commit()
    for q in questions:
        db.refresh(q)

    return {
        "questions_count": len(questions),
        "questions": [
            {
                "id": q.id,
                "question_text": q.question_text,
                "question_type": q.question_type,
                "company": q.company,
                "role": q.role,
            }
            for q in questions
        ],
        "was_duplicate": False,
    }


# -- Scraper run endpoints --

def _run_scraper_job(job_id: str, seed_url_ids: list[int] | None) -> None:
    """Background task: crawl seed URLs and extract questions."""
    job = _scraper_jobs[job_id]
    try:
        from src.backend.database import SessionLocal
        db = SessionLocal()
        try:
            query = db.query(SeedURL).filter(SeedURL.is_active.is_(True))
            if seed_url_ids:
                query = query.filter(SeedURL.id.in_(seed_url_ids))
            seeds = query.all()
            job.seeds_total = len(seeds)

            for seed in seeds:
                try:
                    from src.backend.scraper.crawler import PlaywrightCrawler
                    from src.backend.scraper.extractors import extract_posts
                    from src.backend.scraper.site_configs import get_config

                    config = get_config(seed.source_site)
                    crawler = PlaywrightCrawler()
                    import asyncio
                    html = asyncio.run(crawler.fetch_page(seed.url, config))

                    if not html:
                        job.errors.append(f"Empty response from {seed.url}")
                        job.seeds_processed += 1
                        continue

                    posts = extract_posts(html, seed.source_site)
                    llm = LLMService()

                    for post in posts:
                        content_hash = compute_content_hash(post.get("body_text", ""))
                        existing = (
                            db.query(ScrapedPage)
                            .filter(
                                ScrapedPage.url == post.get("url", seed.url),
                                ScrapedPage.content_hash == content_hash,
                            )
                            .first()
                        )
                        if existing:
                            continue

                        page = ScrapedPage(
                            seed_url_id=seed.id,
                            url=post.get("url", seed.url),
                            extracted_text=post.get("body_text", ""),
                            content_hash=content_hash,
                        )
                        db.add(page)
                        db.flush()

                        extracted = asyncio.run(extract_questions(
                            llm, post.get("body_text", ""),
                            {"company": seed.company} if seed.company else None,
                        ))
                        for q_data in extracted:
                            db.add(InterviewQuestion(
                                scraped_page_id=page.id,
                                company=q_data.get("company"),
                                role=q_data.get("role"),
                                level=q_data.get("level"),
                                interview_round=q_data.get("round"),
                                question_text=q_data["question_text"],
                                question_type=q_data.get("question_type"),
                                tags=json.dumps(
                                    q_data.get("tags", []), ensure_ascii=False
                                ),
                            ))
                            job.questions_found += 1

                    seed.last_checked_at = datetime.utcnow()
                    db.commit()
                except Exception as e:
                    job.errors.append(f"Error processing {seed.url}: {e!s}")
                finally:
                    job.seeds_processed += 1

            job.status = "completed"
        finally:
            db.close()
    except Exception as e:
        job.status = "failed"
        job.errors.append(f"Job failed: {e!s}")
    finally:
        job.completed_at = datetime.utcnow()


@router.post("/scraper/run", status_code=202)
def run_scraper(
    request: ScraperRunRequest,
    background_tasks: BackgroundTasks,
) -> dict:
    """Trigger a scraper run in the background."""
    job_id = str(uuid.uuid4())
    _scraper_jobs[job_id] = ScraperJobStatus(job_id=job_id)
    background_tasks.add_task(_run_scraper_job, job_id, request.seed_url_ids)
    return {"job_id": job_id, "status": "started"}


@router.get("/scraper/status")
def get_scraper_status() -> list[dict]:
    """Return current and recent scraper job statuses."""
    now = datetime.utcnow()
    # Prune old completed jobs
    to_remove = []
    for job_id, job in _scraper_jobs.items():
        if job.completed_at and (now - job.completed_at).total_seconds() > 3600:
            to_remove.append(job_id)
    for job_id in to_remove:
        del _scraper_jobs[job_id]

    return [
        {
            "job_id": j.job_id,
            "status": j.status,
            "seeds_total": j.seeds_total,
            "seeds_processed": j.seeds_processed,
            "questions_found": j.questions_found,
            "started_at": j.started_at.isoformat(),
            "completed_at": j.completed_at.isoformat() if j.completed_at else None,
            "errors": j.errors,
        }
        for j in _scraper_jobs.values()
    ]


# -- Interview questions endpoints --

@router.get("/questions", response_model=list[InterviewQuestionResponse])
def list_questions(
    company: str | None = Query(default=None),
    role: str | None = Query(default=None),
    question_type: str | None = Query(default=None),
    is_reviewed: bool | None = Query(default=None),
    year: int | None = Query(default=None),
    search: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[InterviewQuestion]:
    """List interview questions with filters."""
    query = db.query(InterviewQuestion)
    if company:
        query = query.filter(InterviewQuestion.company.ilike(f"%{company}%"))
    if role:
        query = query.filter(InterviewQuestion.role.ilike(f"%{role}%"))
    if question_type:
        query = query.filter(InterviewQuestion.question_type == question_type)
    if is_reviewed is not None:
        query = query.filter(InterviewQuestion.is_reviewed == is_reviewed)
    if year:
        query = query.filter(InterviewQuestion.year == year)
    if search:
        query = query.filter(InterviewQuestion.question_text.ilike(f"%{search}%"))
    return query.offset(offset).limit(limit).all()


@router.put("/questions/{question_id}")
def update_question(
    question_id: int, body: dict, db: Session = Depends(get_db)
) -> dict:
    """Update an interview question."""
    q = db.query(InterviewQuestion).filter(InterviewQuestion.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    for attr_name in ("is_reviewed", "notes", "difficulty_estimate", "mapped_framework_node_id"):
        if attr_name in body:
            setattr(q, attr_name, body[attr_name])

    db.commit()
    db.refresh(q)
    return {"id": q.id, "updated": True}


@router.post("/questions/{question_id}/analyze")
async def analyze_question(
    question_id: int, db: Session = Depends(get_db)
) -> dict:
    """Use LLM to analyze an interview question."""
    q = db.query(InterviewQuestion).filter(InterviewQuestion.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    llm = LLMService()
    result = await llm.chat(
        system_prompt=(
            "You are an MLE interview prep expert. Analyze this interview question "
            "and provide structured guidance. Return JSON with: solution_approach, "
            "key_concepts (array), difficulty (easy/medium/hard), "
            "related_patterns (array), suggested_study (string)."
        ),
        messages=[{
            "role": "user",
            "content": f"Analyze this interview question:\n{q.question_text}",
        }],
        response_format="json",
    )

    if isinstance(result, dict) and "error" not in result:
        q.notes = json.dumps(result, ensure_ascii=False)
        db.commit()

    return result
