"""Pydantic schemas for scraper module."""
import json
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SeedURLCreate(BaseModel):
    """Schema for creating a seed URL."""

    url: str = Field(min_length=1)
    source_site: Literal["blind", "1point3acres", "leetcode_discuss", "glassdoor"]
    company: str | None = None
    role_filter: str | None = None
    check_interval_hours: int = Field(default=24, ge=1)


class SeedURLResponse(BaseModel):
    """Schema for seed URL API response."""

    id: int
    url: str
    source_site: str
    company: str | None = None
    role_filter: str | None = None
    is_active: bool = True
    last_checked_at: datetime | None = None
    check_interval_hours: int = 24

    model_config = ConfigDict(from_attributes=True)


class PasteRequest(BaseModel):
    """Schema for pasting interview experience text."""

    text: str = Field(min_length=10)
    company: str | None = None
    role: str | None = None


class ScraperRunRequest(BaseModel):
    """Schema for triggering a scraper run."""

    seed_url_ids: list[int] | None = None


class InterviewQuestionResponse(BaseModel):
    """Schema for interview question API response."""

    id: int
    scraped_page_id: int | None = None
    company: str | None = None
    role: str | None = None
    level: str | None = None
    interview_round: str | None = None
    year: int | None = None
    question_text: str
    question_type: str | None = None
    tags: list[str] = []
    mapped_framework_node_id: int | None = None

    @field_validator("tags", mode="before")
    @classmethod
    def parse_tags_json(cls, v: object) -> list[str]:
        """Parse JSON string tags from DB into a list."""
        if isinstance(v, str):
            return json.loads(v)
        if v is None:
            return []
        return v
    is_reviewed: bool = False
    notes: str | None = None
    difficulty_estimate: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
