"""Pydantic schemas for behavioral questions module."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

# -- Question schemas --

class BehavioralQuestionCreate(BaseModel):
    """Schema for creating a behavioral question."""

    question_id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    category_id: str = Field(min_length=1)
    category_name: str = Field(min_length=1)
    original_category: str | None = None
    difficulty: str | None = None
    company_target: str | None = None


class BehavioralQuestionUpdate(BaseModel):
    """Schema for updating a behavioral question."""

    text: str | None = None
    category_id: str | None = None
    category_name: str | None = None
    original_category: str | None = None
    difficulty: str | None = None
    company_target: str | None = None


class QuestionThemeBrief(BaseModel):
    """Compact theme entry embedded in question responses."""

    slug: str
    label: str

    model_config = ConfigDict(from_attributes=True)


class BehavioralQuestionResponse(BaseModel):
    """Schema for behavioral question API response."""

    id: int
    question_id: str
    text: str
    category_id: str
    category_name: str
    original_category: str | None = None
    difficulty: str | None = None
    company_target: str | None = None
    created_at: datetime | None = None
    example_count: int = 0
    theme_tags: list[QuestionThemeBrief] = []

    model_config = ConfigDict(from_attributes=True)


# -- Example schemas --

class BehavioralExampleCreate(BaseModel):
    """Schema for creating a behavioral example."""

    example_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    source_project: str | None = None
    situation: str | None = None
    task: str | None = None
    action: str | None = None
    result: str | None = None
    evidence_quotes: list[str] = []
    principle_tags: list[str] = []
    risk_statement: str | None = None
    analogy: str | None = None
    tech_terms: dict[str, str] = {}
    cn_elevator_pitch: str | None = None


class BehavioralExampleUpdate(BaseModel):
    """Schema for updating a behavioral example."""

    title: str | None = None
    source_project: str | None = None
    situation: str | None = None
    task: str | None = None
    action: str | None = None
    result: str | None = None
    evidence_quotes: list[str] | None = None
    principle_tags: list[str] | None = None
    risk_statement: str | None = None
    analogy: str | None = None
    tech_terms: dict[str, str] | None = None
    cn_elevator_pitch: str | None = None


class LinkedQuestionBrief(BaseModel):
    """Brief question info for embedding in example responses."""

    id: int
    question_id: str
    text: str
    category_id: str
    relevance_note: str | None = None

    model_config = ConfigDict(from_attributes=True)


class BehavioralExampleResponse(BaseModel):
    """Schema for behavioral example API response."""

    id: int
    example_id: str
    title: str
    source_project: str | None = None
    situation: str | None = None
    task: str | None = None
    action: str | None = None
    result: str | None = None
    evidence_quotes: list[str] = []
    principle_tags: list[str] = []
    risk_statement: str | None = None
    analogy: str | None = None
    tech_terms: dict[str, str] = {}
    cn_elevator_pitch: str | None = None
    created_at: datetime | None = None
    linked_questions: list[LinkedQuestionBrief] = []

    model_config = ConfigDict(from_attributes=True)


# -- Link schemas --

class QuestionExampleLinkCreate(BaseModel):
    """Schema for creating a question-example link."""

    question_id: int
    example_id: int
    relevance_note: str | None = None


class QuestionExampleLinkResponse(BaseModel):
    """Schema for link API response."""

    id: int
    question_id: int
    example_id: int
    relevance_note: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


# -- Category summary --

class CategorySummary(BaseModel):
    """Summary of a BQ category."""

    category_id: str
    category_name: str
    question_count: int
    covered_count: int  # questions with at least 1 example
    example_count: int  # total linked examples


# -- Coverage matrix for visualization --

class CoverageCell(BaseModel):
    """Single cell in the example-principle coverage matrix."""

    example_id: str
    example_title: str
    category_id: str
    category_name: str
    link_count: int  # how many questions in this category this example covers
