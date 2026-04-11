"""Pydantic schemas for behavioral theme taxonomy."""
from pydantic import BaseModel, ConfigDict


class BehavioralThemeResponse(BaseModel):
    """API response for a single theme with counts."""

    id: int
    slug: str
    label: str
    description: str | None = None
    display_order: int
    question_count: int
    example_count: int

    model_config = ConfigDict(from_attributes=True)
