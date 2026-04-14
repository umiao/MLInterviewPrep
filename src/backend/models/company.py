"""Company models: Company, CompanyTopicWeight, CompanyDocument."""
import json

from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from src.backend.database import Base


class Company(Base):
    """A target company for interview preparation."""

    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    group_tag = Column(String, nullable=True)
    interview_stages = Column(Text, nullable=True)  # JSON array
    status = Column(
        String,
        CheckConstraint(
            "status IN ('applied','phone_screen','onsite','offer','rejected')"
        ),
        default="applied",
    )
    applied_at = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    prep_notes = Column(Text, nullable=True)

    topic_weights = relationship(
        "CompanyTopicWeight", back_populates="company", cascade="all, delete-orphan"
    )
    documents = relationship(
        "CompanyDocument", back_populates="company", cascade="all, delete-orphan"
    )

    @property
    def interview_stages_list(self) -> list[dict]:
        """Return interview_stages as Python list."""
        if not self.interview_stages:
            return []
        return json.loads(self.interview_stages)

    @interview_stages_list.setter
    def interview_stages_list(self, value: list[dict]) -> None:
        """Set interview_stages from Python list."""
        self.interview_stages = json.dumps(value, ensure_ascii=False)


class CompanyTopicWeight(Base):
    """Weight of a framework topic for a specific company."""

    __tablename__ = "company_topic_weights"
    __table_args__ = (
        PrimaryKeyConstraint("company_id", "framework_node_id"),
        CheckConstraint("weight BETWEEN 0 AND 5"),
    )

    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    framework_node_id = Column(
        Integer, ForeignKey("framework_nodes.id"), nullable=False
    )
    weight = Column(Float, default=1.0)

    company = relationship("Company", back_populates="topic_weights")
    framework_node = relationship("FrameworkNode")


class CompanyDocument(Base):
    """A child document under a company (e.g. forum interview posts)."""

    __tablename__ = "company_documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False, default="")
    source_type = Column(String, nullable=False, default="manual")
    content_hash = Column(String, nullable=True)
    source_path = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    company = relationship("Company", back_populates="documents")
