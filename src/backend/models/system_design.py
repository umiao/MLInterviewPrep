"""System design case study model."""
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text

from src.backend.database import Base


class SystemDesign(Base):
    """A system design case study module with 8 markdown content sections."""

    __tablename__ = "system_designs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(Text, nullable=False)
    subtitle = Column(Text, nullable=True)
    diagram_filename = Column(String(255), nullable=True)

    # 8 markdown content sections (all editable via frontend)
    overview = Column(Text, nullable=True)                # S1: Overview & Motivation
    architecture = Column(Text, nullable=True)            # S2: Architecture Deep Dive
    dataflow = Column(Text, nullable=True)                # S3: Data Flow & Key Components
    formulas = Column(Text, nullable=True)                # S4: Formulas & Algorithms
    production_constraints = Column(Text, nullable=True)  # S5: Production Constraints
    tradeoffs = Column(Text, nullable=True)               # S6: Trade-off Analysis
    defense = Column(Text, nullable=True)                 # S7: Adversarial Defense Q&A
    verbal_outline = Column(Text, nullable=True)          # S8: Verbal Outline (3-min & 10-min)

    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
