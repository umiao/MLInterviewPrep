"""System design case study API routes."""
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.backend.database import get_db
from src.backend.models.system_design import SystemDesign

router = APIRouter(prefix="/system-designs", tags=["system-designs"])


class SystemDesignSummaryResponse(BaseModel):
    """Summary fields returned in the list endpoint (no full markdown)."""

    id: int
    slug: str
    title: str
    subtitle: str | None
    diagram_filename: str | None
    display_order: int

    model_config = {"from_attributes": True}


class SystemDesignFullResponse(SystemDesignSummaryResponse):
    """Full module response including all 8 markdown sections."""

    overview: str | None
    architecture: str | None
    dataflow: str | None
    formulas: str | None
    production_constraints: str | None
    tradeoffs: str | None
    defense: str | None
    verbal_outline: str | None
    created_at: datetime | None
    updated_at: datetime | None


class SystemDesignUpdate(BaseModel):
    """Partial update schema -- all fields optional."""

    title: str | None = None
    subtitle: str | None = None
    diagram_filename: str | None = None
    overview: str | None = None
    architecture: str | None = None
    dataflow: str | None = None
    formulas: str | None = None
    production_constraints: str | None = None
    tradeoffs: str | None = None
    defense: str | None = None
    verbal_outline: str | None = None
    display_order: int | None = None


@router.get("", response_model=list[SystemDesignSummaryResponse])
def list_system_designs(
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """Return all system design modules (summary fields only, no markdown content)."""
    modules = (
        db.query(SystemDesign)
        .order_by(SystemDesign.display_order, SystemDesign.id)
        .all()
    )
    return [
        {
            "id": m.id,
            "slug": m.slug,
            "title": m.title,
            "subtitle": m.subtitle,
            "diagram_filename": m.diagram_filename,
            "display_order": m.display_order,
        }
        for m in modules
    ]


@router.get("/{slug}", response_model=SystemDesignFullResponse)
def get_system_design(
    slug: str,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Return a full system design module by slug, including all sections."""
    module = db.query(SystemDesign).filter(SystemDesign.slug == slug).first()
    if not module:
        raise HTTPException(status_code=404, detail="System design module not found")

    return {
        "id": module.id,
        "slug": module.slug,
        "title": module.title,
        "subtitle": module.subtitle,
        "diagram_filename": module.diagram_filename,
        "overview": module.overview,
        "architecture": module.architecture,
        "dataflow": module.dataflow,
        "formulas": module.formulas,
        "production_constraints": module.production_constraints,
        "tradeoffs": module.tradeoffs,
        "defense": module.defense,
        "verbal_outline": module.verbal_outline,
        "display_order": module.display_order,
        "created_at": module.created_at,
        "updated_at": module.updated_at,
    }


@router.put("/{slug}", response_model=SystemDesignFullResponse)
def update_system_design(
    slug: str,
    update_data: SystemDesignUpdate,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Partial update of a system design module by slug.

    Accepts any subset of fields. Updates the updated_at timestamp.
    """
    module = db.query(SystemDesign).filter(SystemDesign.slug == slug).first()
    if not module:
        raise HTTPException(status_code=404, detail="System design module not found")

    changes = update_data.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(module, field, value)

    module.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(module)

    return {
        "id": module.id,
        "slug": module.slug,
        "title": module.title,
        "subtitle": module.subtitle,
        "diagram_filename": module.diagram_filename,
        "overview": module.overview,
        "architecture": module.architecture,
        "dataflow": module.dataflow,
        "formulas": module.formulas,
        "production_constraints": module.production_constraints,
        "tradeoffs": module.tradeoffs,
        "defense": module.defense,
        "verbal_outline": module.verbal_outline,
        "display_order": module.display_order,
        "created_at": module.created_at,
        "updated_at": module.updated_at,
    }
