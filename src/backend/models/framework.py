"""Module 3 models: FrameworkNode, StudyLog."""
import json
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.orm import relationship

from src.backend.database import Base


class FrameworkNode(Base):
    """A node in the MLE interview framework knowledge tree."""

    __tablename__ = "framework_nodes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, ForeignKey("framework_nodes.id"), nullable=True)
    path = Column(String, nullable=False, unique=True)
    depth = Column(Integer, nullable=False, default=0)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    importance = Column(Float, default=1.0, server_default=text("1.0"))
    priority = Column(String, default="P1", server_default=text("'P1'"))
    estimated_hours = Column(Float, nullable=True)
    status = Column(
        String,
        CheckConstraint(
            "status IN ('not_started','in_progress','review','mastered')"
        ),
        default="not_started",
    )
    progress_pct = Column(
        Float,
        CheckConstraint("progress_pct BETWEEN 0 AND 100"),
        default=0.0,
        server_default=text("0.0"),
    )
    confidence_level = Column(
        Integer,
        CheckConstraint("confidence_level BETWEEN 0 AND 5"),
        default=0,
        server_default=text("0"),
    )
    relevant_companies = Column(Text, nullable=True)  # JSON array
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    last_studied_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    children = relationship(
        "FrameworkNode",
        back_populates="parent",
        cascade="all, delete-orphan",
    )
    parent = relationship(
        "FrameworkNode",
        remote_side=[id],
        back_populates="children",
    )
    study_logs = relationship(
        "StudyLog", back_populates="framework_node", cascade="all, delete-orphan"
    )

    @property
    def relevant_companies_list(self) -> list[str]:
        """Return relevant_companies as Python list."""
        if not self.relevant_companies:
            return []
        return json.loads(self.relevant_companies)

    @relevant_companies_list.setter
    def relevant_companies_list(self, value: list[str]) -> None:
        """Set relevant_companies from Python list."""
        self.relevant_companies = json.dumps(value, ensure_ascii=False)


class StudyLog(Base):
    """A study session log entry for a framework node."""

    __tablename__ = "study_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    framework_node_id = Column(
        Integer, ForeignKey("framework_nodes.id"), nullable=False
    )
    date = Column(Date, nullable=False, index=True)
    duration_minutes = Column(Integer, nullable=False)
    activity_type = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    framework_node = relationship("FrameworkNode", back_populates="study_logs")
