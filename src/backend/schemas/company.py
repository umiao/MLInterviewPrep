"""Pydantic schemas for Company and CompanyDocument."""
from datetime import date, datetime
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


class CompanyDocumentCreate(BaseModel):
    """Schema for creating a company document."""

    title: str = Field(min_length=1)
    content: str = ""
    source_type: str = "manual"


class CompanyDocumentUpdate(BaseModel):
    """Schema for updating a company document."""

    title: str | None = None
    content: str | None = None


class CompanyDocumentResponse(BaseModel):
    """Schema for company document API response."""

    id: int
    company_id: int
    title: str
    content: str
    source_type: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
