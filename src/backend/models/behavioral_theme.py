"""Behavioral theme taxonomy models.

Themes are a secondary classification cross-cutting the primary 9 categories
(adaptability, collaboration, ...). Each question/example may carry >=0 themes.
"""
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from src.backend.database import Base


class BehavioralTheme(Base):
    """A cross-cutting theme (e.g. failure_setback, deadline_pressure)."""

    __tablename__ = "behavioral_themes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String, nullable=False, unique=True)  # e.g. "failure_setback"
    label = Column(String, nullable=False)  # e.g. "Failure & Setback"
    description = Column(Text, nullable=True)
    display_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    question_tags = relationship(
        "QuestionThemeTag",
        back_populates="theme",
        cascade="all, delete-orphan",
    )
    example_tags = relationship(
        "ExampleThemeTag",
        back_populates="theme",
        cascade="all, delete-orphan",
    )


class QuestionThemeTag(Base):
    """Join row linking a behavioral_question to a behavioral_theme."""

    __tablename__ = "question_theme_tags"

    question_id = Column(
        Integer,
        ForeignKey("behavioral_questions.id", ondelete="CASCADE"),
        primary_key=True,
    )
    theme_id = Column(
        Integer,
        ForeignKey("behavioral_themes.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at = Column(DateTime, default=datetime.utcnow)

    theme = relationship("BehavioralTheme", back_populates="question_tags")


class ExampleThemeTag(Base):
    """Join row linking a behavioral_example to a behavioral_theme."""

    __tablename__ = "example_theme_tags"

    example_id = Column(
        Integer,
        ForeignKey("behavioral_examples.id", ondelete="CASCADE"),
        primary_key=True,
    )
    theme_id = Column(
        Integer,
        ForeignKey("behavioral_themes.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at = Column(DateTime, default=datetime.utcnow)

    theme = relationship("BehavioralTheme", back_populates="example_tags")
