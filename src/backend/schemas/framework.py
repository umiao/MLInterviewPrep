"""Pydantic schemas for Framework and StudyLog."""
from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


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
