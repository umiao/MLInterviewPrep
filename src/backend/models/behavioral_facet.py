"""Behavioral facet taxonomy models (Phase 2 of BQ-TAX refactor).

Facets are a secondary, narrow-purpose tag layer complementing ``behavioral_themes``.
Unlike themes (which partition every question/example into broad motion-of-the-story
buckets), facets are applied sparingly. A facet ID may optionally point at a
parent theme when the facet is a sub-type of that theme.

Facet usage rule (authoritative):
    Facets are ONLY for
      (a) staff/L6 signal tags (e.g. "ambiguity_tolerance", "principal_judgment"),
      (b) cross-theme retrieval tags (e.g. "migration", "incident_response" that
          span multiple primary themes and multiple categories),
      (c) scenario sub-type when a rename of the parent theme would mix
          abstraction layers.
    Facets are NOT a dumping ground for "things we felt like tagging". Reviewers
    should reject facet proposals that do not fit one of the three slots above.

Phase 2 introduces the schema only; no facets are seeded until Phase 2.5 content
work supplies a reviewer-approved starter list.
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


class BehavioralFacet(Base):
    """A narrow-purpose behavioral tag (staff-signal / cross-theme / sub-type)."""

    __tablename__ = "behavioral_facets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String, nullable=False, unique=True)
    label = Column(String, nullable=False)
    parent_theme_id = Column(
        Integer,
        ForeignKey("behavioral_themes.id", ondelete="SET NULL"),
        nullable=True,
    )
    description = Column(Text, nullable=True)
    display_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    parent_theme = relationship("BehavioralTheme", foreign_keys=[parent_theme_id])
    question_tags = relationship(
        "QuestionFacetTag",
        back_populates="facet",
        cascade="all, delete-orphan",
    )
    example_tags = relationship(
        "ExampleFacetTag",
        back_populates="facet",
        cascade="all, delete-orphan",
    )


class QuestionFacetTag(Base):
    """Join row linking a behavioral_question to a behavioral_facet."""

    __tablename__ = "question_facet_tags"

    question_id = Column(
        Integer,
        ForeignKey("behavioral_questions.id", ondelete="CASCADE"),
        primary_key=True,
    )
    facet_id = Column(
        Integer,
        ForeignKey("behavioral_facets.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at = Column(DateTime, default=datetime.utcnow)

    facet = relationship("BehavioralFacet", back_populates="question_tags")


class ExampleFacetTag(Base):
    """Join row linking a behavioral_example to a behavioral_facet."""

    __tablename__ = "example_facet_tags"

    example_id = Column(
        Integer,
        ForeignKey("behavioral_examples.id", ondelete="CASCADE"),
        primary_key=True,
    )
    facet_id = Column(
        Integer,
        ForeignKey("behavioral_facets.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at = Column(DateTime, default=datetime.utcnow)

    facet = relationship("BehavioralFacet", back_populates="example_tags")
