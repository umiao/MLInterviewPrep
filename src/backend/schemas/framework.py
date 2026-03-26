"""Pydantic schemas for Framework and StudyLog."""
from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class FrameworkNodeUpdate(BaseModel):
    """Schema for partial framework node update."""

    title: str | None = None
    description: str | None = None
    status: Literal["not_started", "in_progress", "review", "mastered"] | None = None
    progress_pct: float | None = Field(default=None, ge=0, le=100)
    confidence_level: int | None = Field(default=None, ge=0, le=5)
    priority: Literal["P0", "P1", "P2", "P3"] | None = None
    importance: float | None = Field(default=None, ge=0, le=1)


class StudyLogCreate(BaseModel):
    """Schema for creating a study log entry."""

    date: date
    duration_minutes: int = Field(ge=1)
    activity_type: str | None = None
    notes: str | None = None


class FrameworkNodeResponse(BaseModel):
    """Schema for framework node API response."""

    id: int
    path: str
    depth: int
    title: str
    description: str | None = None
    parent_id: int | None = None
    status: str = "not_started"
    progress_pct: float = 0.0
    confidence_level: int = 0
    importance: float = 1.0
    priority: str = "P1"
    estimated_hours: float | None = None
    children: list[FrameworkNodeResponse] = []

    @field_validator("progress_pct", mode="before")
    @classmethod
    def _coalesce_progress(cls, v: float | None) -> float:
        return v if v is not None else 0.0

    @field_validator("confidence_level", mode="before")
    @classmethod
    def _coalesce_confidence(cls, v: int | None) -> int:
        return v if v is not None else 0

    @field_validator("importance", mode="before")
    @classmethod
    def _coalesce_importance(cls, v: float | None) -> float:
        return v if v is not None else 1.0

    @field_validator("priority", mode="before")
    @classmethod
    def _coalesce_priority(cls, v: str | None) -> str:
        return v if v is not None else "P1"

    model_config = ConfigDict(from_attributes=True)


class StudyLogResponse(BaseModel):
    """Schema for study log API response."""

    id: int
    framework_node_id: int
    date: date
    duration_minutes: int
    activity_type: str | None = None
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)
