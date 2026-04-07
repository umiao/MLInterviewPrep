"""Pydantic schemas for InterviewEvent.

Timezone convention: all datetimes are stored and returned as naive local time
(Pacific Time). The frontend displays them via ``new Date()`` which interprets
naive ISO strings as local time — matching the user's system timezone.
"""
from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.functional_validators import BeforeValidator


def _strip_tz(v: datetime | str) -> datetime:
    """Strip timezone info so datetimes are stored as naive local time.

    Prevents accidental UTC conversion when a TZ-aware datetime is provided
    (e.g. from ``Date.toISOString()`` which appends ``Z``).
    """
    if isinstance(v, str):
        v = datetime.fromisoformat(v.replace("Z", "+00:00") if v.endswith("Z") else v)
    if v.tzinfo is not None:
        # Import here to keep module-level import light
        from zoneinfo import ZoneInfo

        v = v.astimezone(ZoneInfo("America/Los_Angeles")).replace(tzinfo=None)
    return v


NaivePacific = Annotated[datetime, BeforeValidator(_strip_tz)]

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
    scheduled_at: NaivePacific
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
    scheduled_at: NaivePacific | None = None
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
