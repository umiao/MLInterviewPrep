"""Pydantic schemas for the behavioral facet taxonomy (Phase 2)."""
from pydantic import BaseModel, ConfigDict


class BehavioralFacetBrief(BaseModel):
    """Compact facet entry embedded in question/example responses."""

    slug: str
    label: str

    model_config = ConfigDict(from_attributes=True)


class BehavioralFacetResponse(BaseModel):
    """API response for a single facet with aggregate counts."""

    id: int
    slug: str
    label: str
    parent_theme_id: int | None = None
    description: str | None = None
    display_order: int
    question_count: int = 0
    example_count: int = 0

    model_config = ConfigDict(from_attributes=True)
