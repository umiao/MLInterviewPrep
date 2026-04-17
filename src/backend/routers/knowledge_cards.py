"""Knowledge card API: canonical cross-company cards + per-company overlays.

Introduced by T-P1-185. Drives the merged company-prep view described in the
Option A plan (docs/staging/analysis/company_prep_overlap.md).
"""
import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.backend.database import get_db
from src.backend.models.knowledge_card import CompanyCardOverlay, KnowledgeCard

router = APIRouter()


def _card_dict(card: KnowledgeCard, overlays: list[CompanyCardOverlay]) -> dict[str, Any]:
    return {
        "id": card.id,
        "slug": card.slug,
        "title": card.title,
        "canonical_body": card.canonical_body,
        "tags": json.loads(card.tags) if card.tags else [],
        "provenance": {
            "source_company": card.source_company,
            "source_file": card.source_file,
            "source_line_start": card.source_line_start,
            "source_line_end": card.source_line_end,
        },
        "overlays": [
            {
                "company_id": o.company_id,
                "angle": o.angle,
                "overlay_body": o.overlay_body,
                "source_file": o.source_file,
                "source_line_start": o.source_line_start,
                "source_line_end": o.source_line_end,
            }
            for o in overlays
        ],
    }


@router.get("/knowledge_cards")
def list_knowledge_cards(
    company_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """List all knowledge cards. If company_id is given, only overlays for that
    company are attached (canonical body is always returned)."""
    cards = db.query(KnowledgeCard).order_by(KnowledgeCard.slug).all()
    out: list[dict[str, Any]] = []
    for c in cards:
        overlays = c.overlays
        if company_id is not None:
            overlays = [o for o in overlays if o.company_id == company_id]
        out.append(_card_dict(c, overlays))
    return out


@router.get("/knowledge_cards/{slug}")
def get_knowledge_card(
    slug: str,
    company_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    card = db.query(KnowledgeCard).filter(KnowledgeCard.slug == slug).first()
    if not card:
        raise HTTPException(status_code=404, detail=f"Knowledge card not found: {slug}")
    overlays = card.overlays
    if company_id is not None:
        overlays = [o for o in overlays if o.company_id == company_id]
    return _card_dict(card, overlays)
