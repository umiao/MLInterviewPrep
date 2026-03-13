"""Tests for Framework and Company Pydantic schemas."""
from datetime import date

import pytest
from pydantic import ValidationError

from src.backend.schemas.company import CompanyCreate
from src.backend.schemas.framework import FrameworkNodeUpdate, StudyLogCreate


def test_framework_node_update_progress_out_of_range():
    """progress_pct=101 raises ValidationError."""
    with pytest.raises(ValidationError):
        FrameworkNodeUpdate(progress_pct=101)


def test_framework_node_update_valid():
    """Valid partial update succeeds."""
    u = FrameworkNodeUpdate(status="mastered", confidence_level=5)
    assert u.status == "mastered"


def test_study_log_duration_zero():
    """duration_minutes=0 raises ValidationError."""
    with pytest.raises(ValidationError):
        StudyLogCreate(date=date(2024, 1, 1), duration_minutes=0)


def test_study_log_valid():
    """Valid StudyLogCreate succeeds."""
    s = StudyLogCreate(date=date(2024, 1, 1), duration_minutes=30)
    assert s.duration_minutes == 30


def test_company_create_empty_name():
    """Empty company name raises ValidationError."""
    with pytest.raises(ValidationError):
        CompanyCreate(name="")


def test_company_create_valid():
    """Valid CompanyCreate succeeds."""
    c = CompanyCreate(name="Google", group_tag="llm_first")
    assert c.status == "applied"
