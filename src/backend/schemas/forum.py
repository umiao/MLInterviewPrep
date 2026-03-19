"""Pydantic schemas for Forum scraping API."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ForumSeedCreate(BaseModel):
    """Schema for creating a forum seed."""

    url: str = Field(min_length=1)
    source_site: Literal["1point3acres"] = "1point3acres"
    label: str | None = None
    company_id: int | None = None


class ForumSeedResponse(BaseModel):
    """Schema for forum seed API response."""

    id: int
    url: str
    source_site: str
    label: str | None = None
    company_id: int | None = None
    is_active: bool = True
    last_scraped_at: datetime | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ForumPostLinkResponse(BaseModel):
    """Schema for forum post link API response."""

    id: int
    forum_seed_id: int
    url: str
    external_post_id: str | None = None
    title: str | None = None
    discovered_at: datetime | None = None
    status: str = "pending"
    retry_count: int = 0
    last_error: str | None = None
    fetch_order: int | None = None
    post_id: int | None = None

    model_config = ConfigDict(from_attributes=True)


class ForumPostResponse(BaseModel):
    """Schema for forum post API response."""

    id: int
    forum_post_link_id: int
    raw_text: str
    content_hash: str
    author: str | None = None
    published_at: str | None = None
    fetched_at: datetime | None = None
    company_id: int | None = None

    model_config = ConfigDict(from_attributes=True)


class ForumProgressResponse(BaseModel):
    """Schema for forum seed fetch progress."""

    total: int
    pending: int
    fetched: int
    failed: int
    last_fetched_url: str | None = None


class ForumImportRequest(BaseModel):
    """Schema for importing a forum post to prep notes."""

    company_id: int
