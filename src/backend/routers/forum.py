"""Forum scraping API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.backend.database import get_db
from src.backend.models.forum import ForumPost, ForumPostLink, ForumSeed
from src.backend.schemas.company import CompanyResponse
from src.backend.schemas.forum import (
    ForumImportRequest,
    ForumPostLinkResponse,
    ForumPostResponse,
    ForumProgressResponse,
    ForumSeedCreate,
    ForumSeedResponse,
)
from src.backend.scraper.crawler import PlaywrightCrawler
from src.backend.services.forum_service import (
    fetch_next_unfetched,
    fetch_single_post,
    get_fetch_progress,
    import_post_to_prep_notes,
    scrape_seed_page,
)

router = APIRouter()


def _company_to_response(c) -> dict:
    """Convert Company ORM to response dict.

    Args:
        c: Company ORM instance.

    Returns:
        Dict matching CompanyResponse schema.
    """
    return {
        "id": c.id,
        "name": c.name,
        "group_tag": c.group_tag,
        "interview_stages": c.interview_stages_list,
        "status": c.status,
        "applied_at": c.applied_at,
        "notes": c.notes,
        "prep_notes": c.prep_notes,
    }


@router.get("/forum/seeds", response_model=list[ForumSeedResponse])
def list_seeds(
    company_id: int | None = None,
    source_site: str | None = None,
    db: Session = Depends(get_db),
) -> list[ForumSeed]:
    """List forum seeds with optional filters.

    Args:
        company_id: Filter by company ID.
        source_site: Filter by source site.
        db: Database session.

    Returns:
        List of ForumSeed objects.
    """
    query = db.query(ForumSeed)
    if company_id is not None:
        query = query.filter(ForumSeed.company_id == company_id)
    if source_site is not None:
        query = query.filter(ForumSeed.source_site == source_site)
    return query.all()


@router.post("/forum/seeds", response_model=ForumSeedResponse, status_code=201)
def create_seed(
    body: ForumSeedCreate,
    db: Session = Depends(get_db),
) -> ForumSeed:
    """Create a new forum seed.

    Args:
        body: Seed creation data.
        db: Database session.

    Returns:
        Created ForumSeed object.
    """
    existing = db.query(ForumSeed).filter(ForumSeed.url == body.url).first()
    if existing:
        raise HTTPException(status_code=409, detail="Seed URL already exists")

    seed = ForumSeed(
        url=body.url,
        source_site=body.source_site,
        label=body.label,
        company_id=body.company_id,
    )
    db.add(seed)
    db.commit()
    db.refresh(seed)
    return seed


@router.delete("/forum/seeds/{seed_id}", status_code=204)
def delete_seed(
    seed_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete a forum seed and cascade to links/posts.

    Args:
        seed_id: ID of the seed to delete.
        db: Database session.
    """
    seed = db.query(ForumSeed).filter(ForumSeed.id == seed_id).first()
    if not seed:
        raise HTTPException(status_code=404, detail="Seed not found")
    db.delete(seed)
    db.commit()


@router.post(
    "/forum/seeds/{seed_id}/scrape",
    response_model=list[ForumPostLinkResponse],
)
async def scrape_links(
    seed_id: int,
    db: Session = Depends(get_db),
) -> list[ForumPostLink]:
    """Phase A: scrape index page and discover post links.

    Args:
        seed_id: ID of the seed to scrape.
        db: Database session.

    Returns:
        List of discovered ForumPostLink objects.
    """
    seed = db.query(ForumSeed).filter(ForumSeed.id == seed_id).first()
    if not seed:
        raise HTTPException(status_code=404, detail="Seed not found")

    crawler = PlaywrightCrawler()
    try:
        return await scrape_seed_page(db, seed_id, crawler)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/forum/seeds/{seed_id}/links",
    response_model=list[ForumPostLinkResponse],
)
def list_links(
    seed_id: int,
    db: Session = Depends(get_db),
) -> list[ForumPostLink]:
    """List post links for a seed.

    Args:
        seed_id: ID of the seed.
        db: Database session.

    Returns:
        List of ForumPostLink objects.
    """
    seed = db.query(ForumSeed).filter(ForumSeed.id == seed_id).first()
    if not seed:
        raise HTTPException(status_code=404, detail="Seed not found")
    return (
        db.query(ForumPostLink)
        .filter(ForumPostLink.forum_seed_id == seed_id)
        .order_by(ForumPostLink.fetch_order)
        .all()
    )


@router.post("/forum/links/{link_id}/fetch", response_model=ForumPostResponse)
async def fetch_post(
    link_id: int,
    db: Session = Depends(get_db),
) -> ForumPost:
    """Phase B: fetch a single post by link ID.

    Args:
        link_id: ID of the ForumPostLink to fetch.
        db: Database session.

    Returns:
        Fetched ForumPost object.
    """
    link = db.query(ForumPostLink).filter(ForumPostLink.id == link_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Post link not found")

    crawler = PlaywrightCrawler()
    try:
        post = await fetch_single_post(db, link_id, crawler)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if post is None:
        raise HTTPException(
            status_code=204,
            detail="Post already fetched or fetch failed",
        )
    return post


@router.post(
    "/forum/seeds/{seed_id}/fetch-next",
    response_model=ForumPostResponse,
    responses={204: {"description": "No pending posts"}},
)
async def fetch_next(
    seed_id: int,
    db: Session = Depends(get_db),
) -> ForumPost:
    """Fetch the next unfetched post for a seed.

    Args:
        seed_id: ID of the seed.
        db: Database session.

    Returns:
        Fetched ForumPost, or 204 if none pending.
    """
    seed = db.query(ForumSeed).filter(ForumSeed.id == seed_id).first()
    if not seed:
        raise HTTPException(status_code=404, detail="Seed not found")

    crawler = PlaywrightCrawler()
    post = await fetch_next_unfetched(db, seed_id, crawler)

    if post is None:
        raise HTTPException(status_code=204, detail="No pending posts")
    return post


@router.get("/forum/posts/{post_id}", response_model=ForumPostResponse)
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
) -> ForumPost:
    """Get a single forum post by ID.

    Args:
        post_id: ID of the post.
        db: Database session.

    Returns:
        ForumPost object.
    """
    post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("/forum/posts/{post_id}/import", response_model=CompanyResponse)
def import_post(
    post_id: int,
    body: ForumImportRequest,
    db: Session = Depends(get_db),
) -> dict:
    """Import a forum post into a company's prep notes.

    Args:
        post_id: ID of the forum post.
        body: Import request with company_id.
        db: Database session.

    Returns:
        Updated Company as dict.
    """
    try:
        company = import_post_to_prep_notes(db, post_id, body.company_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _company_to_response(company)


@router.get(
    "/forum/seeds/{seed_id}/progress",
    response_model=ForumProgressResponse,
)
def get_progress(
    seed_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """Get fetch progress for a seed.

    Args:
        seed_id: ID of the seed.
        db: Database session.

    Returns:
        Progress stats dict.
    """
    seed = db.query(ForumSeed).filter(ForumSeed.id == seed_id).first()
    if not seed:
        raise HTTPException(status_code=404, detail="Seed not found")
    return get_fetch_progress(db, seed_id)
