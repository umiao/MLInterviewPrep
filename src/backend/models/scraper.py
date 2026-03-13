"""Module 2 models: SeedURL, ScrapedPage, InterviewQuestion."""
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
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from src.backend.database import Base


class SeedURL(Base):
    """Seed URL for scraping interview experiences."""

    __tablename__ = "seed_urls"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(Text, nullable=False, unique=True)
    source_site = Column(
        String,
        CheckConstraint(
            "source_site IN ('blind','1point3acres','leetcode_discuss','glassdoor')"
        ),
        nullable=False,
    )
    company = Column(Text, nullable=True)
    role_filter = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    last_checked_at = Column(DateTime, nullable=True)
    check_interval_hours = Column(Integer, default=24)
    content_hash = Column(Text, nullable=True)

    scraped_pages = relationship(
        "ScrapedPage", back_populates="seed_url", cascade="all, delete-orphan"
    )


class ScrapedPage(Base):
    """A scraped web page with extracted content."""

    __tablename__ = "scraped_pages"
    __table_args__ = (UniqueConstraint("url", "content_hash", name="uq_url_content_hash"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    seed_url_id = Column(Integer, ForeignKey("seed_urls.id"), nullable=True)
    url = Column(Text, nullable=False)
    raw_html = Column(Text, nullable=True)
    extracted_text = Column(Text, nullable=True)
    content_hash = Column(Text, nullable=False)
    scraped_at = Column(DateTime, default=datetime.utcnow)

    seed_url = relationship("SeedURL", back_populates="scraped_pages")
    questions = relationship(
        "InterviewQuestion", back_populates="scraped_page", cascade="all, delete-orphan"
    )


class InterviewQuestion(Base):
    """An interview question extracted from scraped content."""

    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scraped_page_id = Column(Integer, ForeignKey("scraped_pages.id"), nullable=True)
    company = Column(Text, nullable=True, index=True)
    role = Column(Text, nullable=True)
    level = Column(Text, nullable=True)
    interview_round = Column(Text, nullable=True)
    year = Column(Integer, nullable=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(
        String,
        CheckConstraint(
            "question_type IN ('coding','ml_theory','ml_system_design',"
            "'behavioral','ml_coding','general_system_design')"
        ),
        nullable=True,
    )
    tags = Column(Text, nullable=True)  # JSON array
    mapped_framework_node_id = Column(
        Integer, ForeignKey("framework_nodes.id"), nullable=True
    )
    is_reviewed = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    difficulty_estimate = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    scraped_page = relationship("ScrapedPage", back_populates="questions")

    @property
    def tags_list(self) -> list[str]:
        """Return tags as Python list."""
        if not self.tags:
            return []
        return json.loads(self.tags)

    @tags_list.setter
    def tags_list(self, value: list[str]) -> None:
        """Set tags from Python list."""
        self.tags = json.dumps(value, ensure_ascii=False)
