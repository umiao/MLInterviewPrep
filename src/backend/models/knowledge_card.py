"""Knowledge card models: canonical cross-company cards + per-company overlays.

Introduced by T-P1-185 per the Option A consolidation plan in
docs/staging/analysis/company_prep_overlap.md (T-P0-184). See that audit for the
14 SHARED topics targeted for canonical-card migration and the provenance
conventions enforced by the source_* columns.
"""
from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from src.backend.database import Base


class KnowledgeCard(Base):
    """Canonical cross-company knowledge card (Chinese prose)."""

    __tablename__ = "knowledge_cards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String, nullable=False, unique=True, index=True)
    title = Column(String, nullable=False)
    canonical_body = Column(Text, nullable=False)
    tags = Column(Text, nullable=True)  # JSON array
    source_company = Column(String, nullable=True)
    source_file = Column(String, nullable=True)
    source_line_start = Column(Integer, nullable=True)
    source_line_end = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    overlays = relationship(
        "CompanyCardOverlay",
        back_populates="card",
        cascade="all, delete-orphan",
    )


class CompanyCardOverlay(Base):
    """Per-company overlay stacked under a canonical knowledge card."""

    __tablename__ = "company_card_overlays"
    __table_args__ = (
        UniqueConstraint("card_id", "company_id", "angle"),
        CheckConstraint(
            "angle IN ('product','interview-format','translation','example')"
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    card_id = Column(
        Integer, ForeignKey("knowledge_cards.id", ondelete="CASCADE"), nullable=False
    )
    company_id = Column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    angle = Column(String, nullable=False)
    overlay_body = Column(Text, nullable=False)
    source_file = Column(String, nullable=True)
    source_line_start = Column(Integer, nullable=True)
    source_line_end = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    card = relationship("KnowledgeCard", back_populates="overlays")
