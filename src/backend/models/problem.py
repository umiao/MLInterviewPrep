"""Module 1 models: Problem, Attempt, QASession."""
import json
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.orm import relationship

from src.backend.database import Base


class Problem(Base):
    """LeetCode / coding problem tracker."""

    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, autoincrement=True)
    leetcode_id = Column(Integer, nullable=True)
    title = Column(Text, nullable=False)
    url = Column(Text, nullable=True)
    difficulty = Column(
        String,
        CheckConstraint("difficulty IN ('easy','medium','hard')"),
        nullable=True,
        index=True,
    )
    tags = Column(Text, nullable=True)  # JSON array
    pattern = Column(Text, nullable=True, index=True)
    family = Column(Text, nullable=True, index=True)
    category = Column(
        String,
        CheckConstraint("category IN ('algorithm','ml_coding','system_design')"),
        nullable=False,
        default="algorithm",
        server_default="algorithm",
    )
    source = Column(Text, nullable=True)
    company_tags = Column(Text, nullable=True)  # JSON array
    priority = Column(
        Integer,
        CheckConstraint("priority BETWEEN 1 AND 3"),
        default=2,
    )
    is_completed = Column(Boolean, default=False)
    comfort_level = Column(
        Integer,
        CheckConstraint("comfort_level BETWEEN 0 AND 5"),
        default=0,
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    last_attempted_at = Column(DateTime, nullable=True)
    next_review_at = Column(DateTime, nullable=True, index=True)
    framework_node_id = Column(
        Integer, ForeignKey("framework_nodes.id", ondelete="SET NULL"), nullable=True, index=True
    )
    description = Column(Text, nullable=True)
    neetcode_slug = Column(String, nullable=True)
    description_source = Column(String, nullable=True)  # "neetcode", "manual", "leetcode"
    notes = Column(Text, nullable=True)
    frequency_rank = Column(Integer, nullable=True)
    is_golden = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("0"),
    )
    golden_at = Column(DateTime, nullable=True)

    attempts = relationship("Attempt", back_populates="problem", cascade="all, delete-orphan")
    qa_sessions = relationship("QASession", back_populates="problem", cascade="all, delete-orphan")
    framework_node = relationship("FrameworkNode", backref="problems")

    @property
    def tags_list(self) -> list[str]:
        """Return tags as Python list."""
        if not self.tags:
            return []
        try:
            return json.loads(self.tags)
        except (json.JSONDecodeError, TypeError):
            return [t.strip() for t in self.tags.split(",") if t.strip()]

    @tags_list.setter
    def tags_list(self, value: list[str]) -> None:
        """Set tags from Python list."""
        self.tags = json.dumps(value, ensure_ascii=False)

    @property
    def company_tags_list(self) -> list[str]:
        """Return company_tags as Python list."""
        if not self.company_tags:
            return []
        try:
            return json.loads(self.company_tags)
        except (json.JSONDecodeError, TypeError):
            return [t.strip() for t in self.company_tags.split(",") if t.strip()]

    @company_tags_list.setter
    def company_tags_list(self, value: list[str]) -> None:
        """Set company_tags from Python list."""
        self.company_tags = json.dumps(value, ensure_ascii=False)


class Attempt(Base):
    """A single attempt at solving a problem."""

    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    duration_seconds = Column(Integer, nullable=True)
    result = Column(
        String,
        CheckConstraint("result IN ('solved','hint','failed','timeout')"),
        nullable=True,
    )
    approach_notes = Column(Text, nullable=True)
    complexity_time = Column(Text, nullable=True)
    complexity_space = Column(Text, nullable=True)
    llm_review = Column(Text, nullable=True)  # JSON string
    comfort_after = Column(
        Integer,
        CheckConstraint("comfort_after BETWEEN 1 AND 5"),
        nullable=True,
    )

    problem = relationship("Problem", back_populates="attempts")


class QASession(Base):
    """Multi-turn Q&A conversation session."""

    __tablename__ = "qa_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=True)
    topic = Column(Text, nullable=True)
    messages = Column(Text, nullable=False)  # JSON array of {role, content, timestamp}
    created_at = Column(DateTime, default=datetime.utcnow)
    summary = Column(Text, nullable=True)

    problem = relationship("Problem", back_populates="qa_sessions")

    @property
    def messages_list(self) -> list[dict]:
        """Return messages as Python list."""
        if not self.messages:
            return []
        try:
            return json.loads(self.messages)
        except (json.JSONDecodeError, TypeError):
            return []

    @messages_list.setter
    def messages_list(self, value: list[dict]) -> None:
        """Set messages from Python list."""
        self.messages = json.dumps(value, ensure_ascii=False)
