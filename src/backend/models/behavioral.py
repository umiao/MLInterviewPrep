"""Behavioral Questions models: BehavioralQuestion, BehavioralExample, QuestionExampleLink."""
import json
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


class BehavioralQuestion(Base):
    """A behavioral interview question, clustered by leadership principle."""

    __tablename__ = "behavioral_questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(String, nullable=False, unique=True)  # e.g. "OWN-1"
    text = Column(Text, nullable=False)
    category_id = Column(String, nullable=False, index=True)  # e.g. "ownership"
    category_name = Column(String, nullable=False)  # e.g. "Ownership & Accountability"
    original_category = Column(String, nullable=True)  # original blog category
    difficulty = Column(String, nullable=True)  # easy/medium/hard
    company_target = Column(String, nullable=True)  # e.g. "Meta E6"
    created_at = Column(DateTime, default=datetime.utcnow)

    example_links = relationship(
        "QuestionExampleLink",
        back_populates="question",
        cascade="all, delete-orphan",
    )


class BehavioralExample(Base):
    """A STAR-format behavioral example/story from real projects."""

    __tablename__ = "behavioral_examples"

    id = Column(Integer, primary_key=True, autoincrement=True)
    example_id = Column(String, nullable=False, unique=True)  # e.g. "EX-01"
    title = Column(String, nullable=False)
    source_project = Column(String, nullable=True)
    situation = Column(Text, nullable=True)
    task = Column(Text, nullable=True)
    action = Column(Text, nullable=True)
    result = Column(Text, nullable=True)
    evidence_quotes = Column(Text, nullable=True)  # JSON array
    principle_tags = Column(Text, nullable=True)  # JSON array
    risk_statement = Column(Text, nullable=True)
    analogy = Column(Text, nullable=True)
    tech_terms = Column(Text, nullable=True)  # JSON dict {"term": "definition"}
    created_at = Column(DateTime, default=datetime.utcnow)

    question_links = relationship(
        "QuestionExampleLink",
        back_populates="example",
        cascade="all, delete-orphan",
    )

    @property
    def evidence_quotes_list(self) -> list[str]:
        """Return evidence quotes as Python list."""
        if not self.evidence_quotes:
            return []
        return json.loads(self.evidence_quotes)

    @evidence_quotes_list.setter
    def evidence_quotes_list(self, value: list[str]) -> None:
        """Set evidence quotes from Python list."""
        self.evidence_quotes = json.dumps(value, ensure_ascii=False)

    @property
    def principle_tags_list(self) -> list[str]:
        """Return principle tags as Python list."""
        if not self.principle_tags:
            return []
        return json.loads(self.principle_tags)

    @principle_tags_list.setter
    def principle_tags_list(self, value: list[str]) -> None:
        """Set principle tags from Python list."""
        self.principle_tags = json.dumps(value, ensure_ascii=False)

    @property
    def tech_terms_dict(self) -> dict[str, str]:
        """Return tech terms as Python dict."""
        if not self.tech_terms:
            return {}
        return json.loads(self.tech_terms)

    @tech_terms_dict.setter
    def tech_terms_dict(self, value: dict[str, str]) -> None:
        """Set tech terms from Python dict."""
        self.tech_terms = json.dumps(value, ensure_ascii=False)


class QuestionExampleLink(Base):
    """Many-to-many link between questions and examples with relevance note."""

    __tablename__ = "question_example_links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(
        Integer, ForeignKey("behavioral_questions.id", ondelete="CASCADE"),
        nullable=False,
    )
    example_id = Column(
        Integer, ForeignKey("behavioral_examples.id", ondelete="CASCADE"),
        nullable=False,
    )
    relevance_note = Column(Text, nullable=True)  # Why this example fits this question
    created_at = Column(DateTime, default=datetime.utcnow)

    question = relationship("BehavioralQuestion", back_populates="example_links")
    example = relationship("BehavioralExample", back_populates="question_links")
