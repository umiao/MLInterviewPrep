"""Company tag association models: problem/node/behavioral-example -> company."""
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import backref, relationship

from src.backend.database import Base

_RELEVANCE_CHECK = CheckConstraint(
    "relevance IN ('core','likely','stretch')", name=None
)
_SOURCE_VALUES = (
    "manual",
    "auto_from_doc_ref",
    "auto_from_overlay",
    "auto_from_interview_log",
)
_SOURCE_CHECK_SQL = (
    "source IN ('manual','auto_from_doc_ref',"
    "'auto_from_overlay','auto_from_interview_log')"
)


class ProblemCompanyTag(Base):
    """Association: a Problem tagged as relevant to a Company."""

    __tablename__ = "problem_company_tags"
    __table_args__ = (
        UniqueConstraint("problem_id", "company_id", name="uq_pct_problem_company"),
        CheckConstraint(
            "relevance IN ('core','likely','stretch')", name="ck_pct_relevance"
        ),
        CheckConstraint(_SOURCE_CHECK_SQL, name="ck_pct_source"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    problem_id = Column(
        Integer,
        ForeignKey("problems.id", ondelete="CASCADE"),
        nullable=False,
    )
    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    relevance = Column(String, nullable=False, default="core")
    source = Column(String, nullable=False, default="manual")
    notes = Column(Text, nullable=True)
    added_at = Column(DateTime, default=datetime.utcnow)

    problem = relationship(
        "Problem",
        backref=backref(
            "company_tags_assoc",
            cascade="all, delete-orphan",
            passive_deletes=True,
        ),
        passive_deletes=True,
    )
    company = relationship(
        "Company",
        backref=backref(
            "problem_tags",
            cascade="all, delete-orphan",
            passive_deletes=True,
        ),
        passive_deletes=True,
    )


class NodeCompanyTag(Base):
    """Association: a FrameworkNode tagged as relevant to a Company."""

    __tablename__ = "node_company_tags"
    __table_args__ = (
        UniqueConstraint("node_id", "company_id", name="uq_nct_node_company"),
        CheckConstraint(
            "relevance IN ('core','likely','stretch')", name="ck_nct_relevance"
        ),
        CheckConstraint(_SOURCE_CHECK_SQL, name="ck_nct_source"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(
        Integer,
        ForeignKey("framework_nodes.id", ondelete="CASCADE"),
        nullable=False,
    )
    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    relevance = Column(String, nullable=False, default="core")
    source = Column(String, nullable=False, default="manual")
    notes = Column(Text, nullable=True)
    added_at = Column(DateTime, default=datetime.utcnow)

    node = relationship(
        "FrameworkNode",
        backref=backref(
            "company_tags_assoc",
            cascade="all, delete-orphan",
            passive_deletes=True,
        ),
        passive_deletes=True,
    )
    company = relationship(
        "Company",
        backref=backref(
            "node_tags",
            cascade="all, delete-orphan",
            passive_deletes=True,
        ),
        passive_deletes=True,
    )


class BehavioralExampleCompanyTag(Base):
    """Association: a BehavioralExample tagged as relevant to a Company.

    ``company_attribute`` is a free-form string describing which company
    attribute this example illustrates (e.g. "Googleyness" for Google,
    "Move Fast" for Meta). Generic column name supports all companies.
    """

    __tablename__ = "behavioral_example_company_tags"
    __table_args__ = (
        UniqueConstraint(
            "example_id", "company_id", name="uq_bect_example_company"
        ),
        CheckConstraint(
            "relevance IN ('core','likely','stretch')", name="ck_bect_relevance"
        ),
        CheckConstraint(_SOURCE_CHECK_SQL, name="ck_bect_source"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    example_id = Column(
        Integer,
        ForeignKey("behavioral_examples.id", ondelete="CASCADE"),
        nullable=False,
    )
    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    relevance = Column(String, nullable=False, default="core")
    source = Column(String, nullable=False, default="manual")
    company_attribute = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    added_at = Column(DateTime, default=datetime.utcnow)

    example = relationship(
        "BehavioralExample",
        backref=backref(
            "company_tags_assoc",
            cascade="all, delete-orphan",
            passive_deletes=True,
        ),
        passive_deletes=True,
    )
    company = relationship(
        "Company",
        backref=backref(
            "behavioral_example_tags",
            cascade="all, delete-orphan",
            passive_deletes=True,
        ),
        passive_deletes=True,
    )
