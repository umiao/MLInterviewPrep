"""Pydantic schemas for Problem and Attempt CRUD."""
import json
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProblemCreate(BaseModel):
    """Schema for creating a new problem."""

    leetcode_id: int | None = None
    title: str = Field(min_length=1)
    url: str | None = None
    difficulty: Literal["easy", "medium", "hard"] | None = None
    tags: list[str] = []
    pattern: str | None = None
    category: Literal["algorithm", "ml_coding", "system_design"] = "algorithm"
    source: str | None = None
    company_tags: list[str] = []
    priority: int = Field(default=2, ge=1, le=3)
    framework_node_id: int | None = None
    description: str | None = None
    neetcode_slug: str | None = None
    description_source: str | None = None
    notes: str | None = None


class ProblemUpdate(BaseModel):
    """Schema for partial problem update."""

    leetcode_id: int | None = None
    title: str | None = Field(default=None, min_length=1)
    url: str | None = None
    difficulty: Literal["easy", "medium", "hard"] | None = None
    tags: list[str] | None = None
    pattern: str | None = None
    category: Literal["algorithm", "ml_coding", "system_design"] | None = None
    source: str | None = None
    company_tags: list[str] | None = None
    priority: int | None = Field(default=None, ge=1, le=3)
    is_completed: bool | None = None
    comfort_level: int | None = Field(default=None, ge=0, le=5)
    framework_node_id: int | None = None
    description: str | None = None
    neetcode_slug: str | None = None
    description_source: str | None = None
    notes: str | None = None


class ProblemResponse(BaseModel):
    """Schema for problem API response."""

    id: int
    leetcode_id: int | None = None
    title: str
    url: str | None = None
    difficulty: str | None = None
    tags: list[str] = []
    pattern: str | None = None
    category: str = "algorithm"
    source: str | None = None
    company_tags: list[str] = []
    priority: int | None = 2
    is_completed: bool = False
    comfort_level: int = 0
    created_at: datetime | None = None
    last_attempted_at: datetime | None = None
    next_review_at: datetime | None = None
    framework_node_id: int | None = None
    description: str | None = None
    neetcode_slug: str | None = None
    description_source: str | None = None
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("tags", "company_tags", mode="before")
    @classmethod
    def parse_json_list(cls, v: object) -> list[str]:
        """Parse JSON string to list if needed (SQLAlchemy stores as text)."""
        if v is None:
            return []
        if isinstance(v, str):
            return json.loads(v)
        return v  # type: ignore[return-value]


class AttemptCreate(BaseModel):
    """Schema for creating a new attempt."""

    duration_seconds: int | None = Field(default=None, ge=0)
    result: Literal["solved", "hint", "failed", "timeout"]
    approach_notes: str | None = None
    complexity_time: str | None = None
    complexity_space: str | None = None
    comfort_after: int = Field(ge=1, le=5)


class AttemptResponse(BaseModel):
    """Schema for attempt API response."""

    id: int
    problem_id: int
    started_at: datetime | None = None
    duration_seconds: int | None = None
    result: str | None = None
    approach_notes: str | None = None
    complexity_time: str | None = None
    complexity_space: str | None = None
    llm_review: str | None = None
    comfort_after: int | None = None

    model_config = ConfigDict(from_attributes=True)
