"""Forum scraping models: ForumSeed, ForumPostLink, ForumPost."""
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
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from src.backend.database import Base


class ForumSeed(Base):
    """A forum seed URL to scrape for interview posts."""

    __tablename__ = "forum_seeds"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(Text, nullable=False, unique=True)
    source_site = Column(String, nullable=False)
    label = Column(Text, nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    last_scraped_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    post_links = relationship(
        "ForumPostLink", back_populates="forum_seed", cascade="all, delete-orphan"
    )


class ForumPostLink(Base):
    """A discovered post link from a forum seed page."""

    __tablename__ = "forum_post_links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    forum_seed_id = Column(Integer, ForeignKey("forum_seeds.id"), nullable=False)
    url = Column(Text, nullable=False, unique=True)
    external_post_id = Column(Text, nullable=True, unique=True)
    title = Column(Text, nullable=True)
    discovered_at = Column(DateTime, default=datetime.utcnow)
    status = Column(
        String,
        CheckConstraint("status IN ('pending', 'fetched', 'failed')"),
        nullable=False,
        default="pending",
    )
    retry_count = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)
    fetch_order = Column(Integer, nullable=True)

    forum_seed = relationship("ForumSeed", back_populates="post_links")
    post = relationship(
        "ForumPost", back_populates="post_link", cascade="all, delete-orphan", uselist=False
    )

    @hybrid_property
    def post_id(self) -> int | None:
        """Return the associated ForumPost ID if fetched, else None."""
        return self.post.id if self.post else None


class ForumPost(Base):
    """Fetched content from a forum post."""

    __tablename__ = "forum_posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    forum_post_link_id = Column(
        Integer, ForeignKey("forum_post_links.id"), nullable=False, unique=True
    )
    raw_text = Column(Text, nullable=False)
    content_hash = Column(Text, nullable=False)
    author = Column(Text, nullable=True)
    published_at = Column(Text, nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)

    post_link = relationship("ForumPostLink", back_populates="post")
