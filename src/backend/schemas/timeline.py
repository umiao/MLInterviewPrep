"""Pydantic schemas for InterviewEvent."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

EVENT_TYPE = Literal[
    "hr_call",
    "phone_screen",
    "technical",
    "onsite",
    "offer_deadline",
    "behavioral",
    "system_design",
    "take_home",
    "other",
]

EVENT_STATUS = Literal["upcoming", "completed", "cancelled", "rescheduled"]


class InterviewEventCreate(BaseModel):
    """Schema for creating an interview event."""

    company_name: str = Field(min_length=1)
    company_id: int | None = None
    event_type: EVENT_TYPE
    title: str = Field(min_length=1)
    description: str | None = None
    scheduled_at: datetime
    duration_minutes: int | None = None
    location: str | None = None
    status: EVENT_STATUS = "upcoming"


class InterviewEventUpdate(BaseModel):
    """Schema for partial interview event update."""

    company_name: str | None = Field(default=None, min_length=1)
    company_id: int | None = None
    event_type: EVENT_TYPE | None = None
    title: str | None = Field(default=None, min_length=1)
    description: str | None = None
    scheduled_at: datetime | None = None
    duration_minutes: int | None = None
    location: str | None = None
    status: EVENT_STATUS | None = None


class InterviewEventResponse(BaseModel):
    """Schema for interview event API response."""

    id: int
    company_id: int | None = None
    company_name: str
    event_type: str
    title: str
    description: str | None = None
    scheduled_at: datetime
    duration_minutes: int | None = None
    location: str | None = None
    status: str = "upcoming"
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
