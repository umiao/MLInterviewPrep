"""Pydantic schemas for Company."""
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CompanyCreate(BaseModel):
    """Schema for creating a company."""

    name: str = Field(min_length=1)
    group_tag: str | None = None
    interview_stages: list[dict] = []
    status: Literal[
        "applied", "phone_screen", "onsite", "offer", "rejected"
    ] = "applied"
    applied_at: date | None = None
    notes: str | None = None
    prep_notes: str | None = None


class CompanyUpdate(BaseModel):
    """Schema for partial company update."""

    name: str | None = Field(default=None, min_length=1)
    group_tag: str | None = None
    interview_stages: list[dict] | None = None
    status: Literal[
        "applied", "phone_screen", "onsite", "offer", "rejected"
    ] | None = None
    applied_at: date | None = None
    notes: str | None = None
    prep_notes: str | None = None


class CompanyResponse(BaseModel):
    """Schema for company API response."""

    id: int
    name: str
    group_tag: str | None = None
    interview_stages: list[dict] = []
    status: str = "applied"
    applied_at: date | None = None
    notes: str | None = None
    prep_notes: str | None = None

    model_config = ConfigDict(from_attributes=True)


class TopicWeightCreate(BaseModel):
    """Schema for creating/updating a topic weight."""

    framework_node_id: int
    weight: float = Field(default=1.0, ge=0, le=5)
