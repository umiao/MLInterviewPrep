"""InterviewEvent model for tracking interview timeline."""
from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)

from src.backend.database import Base

EVENT_TYPES = (
    "hr_call",
    "phone_screen",
    "technical",
    "onsite",
    "offer_deadline",
    "behavioral",
    "system_design",
    "take_home",
    "other",
)

EVENT_STATUSES = ("upcoming", "completed", "cancelled", "rescheduled")


class InterviewEvent(Base):
    """A scheduled interview event on the preparation timeline."""

    __tablename__ = "interview_events"
    __table_args__ = (
        CheckConstraint(
            f"event_type IN ({','.join(repr(t) for t in EVENT_TYPES)})",
            name="ck_event_type",
        ),
        CheckConstraint(
            f"status IN ({','.join(repr(s) for s in EVENT_STATUSES)})",
            name="ck_event_status",
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(
        Integer, ForeignKey("companies.id", ondelete="SET NULL"), nullable=True
    )
    company_name = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=False, index=True)
    duration_minutes = Column(Integer, nullable=True)
    location = Column(String, nullable=True)
    status = Column(String, nullable=False, default="upcoming")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
