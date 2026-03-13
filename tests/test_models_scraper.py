"""Tests for SeedURL, ScrapedPage, InterviewQuestion models."""
import pytest
from sqlalchemy.exc import IntegrityError

from src.backend.models.scraper import InterviewQuestion, ScrapedPage, SeedURL

# --- SeedURL tests ---


def test_seed_url_creation(db_session):
    """SeedURL basic creation works."""
    s = SeedURL(url="https://example.com", source_site="blind")
    db_session.add(s)
    db_session.commit()
    assert s.id is not None


def test_seed_url_defaults(db_session):
    """SeedURL defaults: is_active=True, check_interval_hours=24."""
    s = SeedURL(url="https://example.com", source_site="blind")
    db_session.add(s)
    db_session.commit()
    db_session.refresh(s)
    assert s.is_active is True
    assert s.check_interval_hours == 24
    assert s.last_checked_at is None
    assert s.content_hash is None
    assert s.company is None
    assert s.role_filter is None


def test_seed_url_duplicate_url(db_session):
    """Duplicate SeedURL url raises IntegrityError."""
    s1 = SeedURL(url="https://example.com", source_site="blind")
    s2 = SeedURL(url="https://example.com", source_site="1point3acres")
    db_session.add(s1)
    db_session.commit()
    db_session.add(s2)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_seed_url_invalid_source_site(db_session):
    """SeedURL with invalid source_site raises IntegrityError."""
    s = SeedURL(url="https://example.com", source_site="invalid_site")
    db_session.add(s)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_seed_url_all_valid_source_sites(db_session):
    """SeedURL accepts all valid source_site values."""
    for i, site in enumerate(("blind", "1point3acres", "leetcode_discuss", "glassdoor")):
        s = SeedURL(url=f"https://example.com/{i}", source_site=site)
        db_session.add(s)
    db_session.commit()


def test_seed_url_relationship_to_scraped_pages(db_session):
    """SeedURL.scraped_pages relationship works."""
    seed = SeedURL(url="https://example.com", source_site="blind")
    db_session.add(seed)
    db_session.flush()

    page = ScrapedPage(
        seed_url_id=seed.id,
        url="https://example.com/page1",
        content_hash="hash1",
        extracted_text="text",
    )
    db_session.add(page)
    db_session.commit()
    db_session.refresh(seed)
    assert len(seed.scraped_pages) == 1
    assert seed.scraped_pages[0].url == "https://example.com/page1"


# --- ScrapedPage tests ---


def test_scraped_page_creation(db_session):
    """ScrapedPage basic creation with defaults."""
    p = ScrapedPage(url="https://test.com", content_hash="abc123", extracted_text="text")
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    assert p.id is not None
    assert p.scraped_at is not None
    assert p.seed_url_id is None
    assert p.raw_html is None


def test_scraped_page_unique_constraint(db_session):
    """ScrapedPage (url, content_hash) unique constraint."""
    p1 = ScrapedPage(url="https://test.com", content_hash="abc123", extracted_text="text")
    p2 = ScrapedPage(url="https://test.com", content_hash="abc123", extracted_text="text")
    db_session.add(p1)
    db_session.commit()
    db_session.add(p2)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_scraped_page_same_url_different_hash_ok(db_session):
    """Same URL with different content_hash is allowed (updated content)."""
    p1 = ScrapedPage(url="https://test.com", content_hash="hash1", extracted_text="v1")
    p2 = ScrapedPage(url="https://test.com", content_hash="hash2", extracted_text="v2")
    db_session.add_all([p1, p2])
    db_session.commit()
    assert p1.id != p2.id


def test_scraped_page_different_url_same_hash_ok(db_session):
    """Different URLs with same content_hash is allowed."""
    p1 = ScrapedPage(url="https://a.com", content_hash="same_hash", extracted_text="text")
    p2 = ScrapedPage(url="https://b.com", content_hash="same_hash", extracted_text="text")
    db_session.add_all([p1, p2])
    db_session.commit()
    assert p1.id != p2.id


def test_scraped_page_cascade_delete_questions(db_session):
    """Deleting a ScrapedPage cascades to its InterviewQuestions."""
    page = ScrapedPage(url="https://test.com", content_hash="h1", extracted_text="text")
    db_session.add(page)
    db_session.flush()

    q = InterviewQuestion(
        scraped_page_id=page.id,
        question_text="Design a system",
        question_type="ml_system_design",
    )
    db_session.add(q)
    db_session.commit()
    q_id = q.id

    db_session.delete(page)
    db_session.commit()
    assert db_session.get(InterviewQuestion, q_id) is None


# --- InterviewQuestion tests ---


def test_interview_question_creation(db_session):
    """InterviewQuestion basic creation with defaults."""
    q = InterviewQuestion(question_text="Explain backprop", question_type="ml_theory")
    db_session.add(q)
    db_session.commit()
    db_session.refresh(q)
    assert q.id is not None
    assert q.is_reviewed is False
    assert q.created_at is not None
    assert q.scraped_page_id is None
    assert q.company is None
    assert q.notes is None


def test_interview_question_invalid_type(db_session):
    """InterviewQuestion with invalid question_type raises IntegrityError."""
    q = InterviewQuestion(
        question_text="Design a system",
        question_type="invalid_type",
    )
    db_session.add(q)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_interview_question_all_valid_types(db_session):
    """InterviewQuestion with all valid question_type values succeeds."""
    valid_types = (
        "coding",
        "ml_theory",
        "ml_system_design",
        "behavioral",
        "ml_coding",
        "general_system_design",
    )
    for qt in valid_types:
        q = InterviewQuestion(question_text=f"Q about {qt}", question_type=qt)
        db_session.add(q)
    db_session.commit()


def test_interview_question_tags_list_property(db_session):
    """InterviewQuestion.tags_list returns parsed JSON list."""
    q = InterviewQuestion(
        question_text="Q1",
        question_type="coding",
        tags='["dp","arrays"]',
    )
    db_session.add(q)
    db_session.commit()
    assert q.tags_list == ["dp", "arrays"]


def test_interview_question_tags_list_setter(db_session):
    """InterviewQuestion.tags_list setter serializes to JSON."""
    q = InterviewQuestion(question_text="Q1", question_type="coding")
    q.tags_list = ["graph", "bfs"]
    db_session.add(q)
    db_session.commit()
    db_session.refresh(q)
    assert q.tags_list == ["graph", "bfs"]


def test_interview_question_empty_tags(db_session):
    """InterviewQuestion with null tags returns empty list."""
    q = InterviewQuestion(question_text="Q1", question_type="coding")
    db_session.add(q)
    db_session.commit()
    assert q.tags_list == []


def test_interview_question_linked_to_scraped_page(db_session):
    """InterviewQuestion linked to ScrapedPage via FK."""
    page = ScrapedPage(url="https://test.com", content_hash="h1", extracted_text="text")
    db_session.add(page)
    db_session.flush()

    q = InterviewQuestion(
        scraped_page_id=page.id,
        question_text="Design X",
        question_type="ml_system_design",
        company="Google",
        role="MLE",
        year=2025,
    )
    db_session.add(q)
    db_session.commit()
    db_session.refresh(q)
    assert q.scraped_page.url == "https://test.com"
    assert q.company == "Google"
    assert q.year == 2025


def test_interview_question_nullable_type(db_session):
    """InterviewQuestion with null question_type is allowed."""
    q = InterviewQuestion(question_text="Unknown type question")
    db_session.add(q)
    db_session.commit()
    assert q.question_type is None
