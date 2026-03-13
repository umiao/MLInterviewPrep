"""Shared pytest fixtures for the test suite."""
import os
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Set test env vars before any app imports
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key-not-real")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from src.backend.database import Base, _create_views, get_db  # noqa: E402
from src.backend.models import FrameworkNode, Problem  # noqa: E402


@pytest.fixture()
def db_engine():
    """Create an in-memory SQLite engine for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    _create_views(engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session(db_engine):
    """Create a test database session."""
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = session_factory()
    yield session
    session.rollback()
    session.close()


@pytest.fixture()
def test_client(db_engine):
    """Create a FastAPI TestClient with DB override."""
    from fastapi.testclient import TestClient

    from src.backend.main import app

    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # Patch init_db to no-op (tables already created by db_engine fixture)
    # and patch SessionLocal for dashboard/export endpoints that use it directly
    with patch("src.backend.main.init_db"), \
         patch("src.backend.database.SessionLocal", session_factory):
        client = TestClient(app)
        yield client
    app.dependency_overrides.clear()


@pytest.fixture()
def seed_problems(db_session):
    """Insert 5 test problems."""
    problems = []
    for i, (title, diff, pat) in enumerate([
        ("Two Sum", "easy", "hash_map"),
        ("3Sum", "medium", "two_pointers"),
        ("Merge Intervals", "medium", "interval"),
        ("Binary Tree Max Path Sum", "hard", "tree"),
        ("Climbing Stairs", "easy", "dp"),
    ], start=1):
        p = Problem(
            leetcode_id=i * 10,
            title=title,
            difficulty=diff,
            pattern=pat,
            tags='["test"]',
            company_tags='["google"]',
            source="test",
        )
        db_session.add(p)
        problems.append(p)
    db_session.commit()
    for p in problems:
        db_session.refresh(p)
    return problems


@pytest.fixture()
def mock_llm():
    """Create a mock LLMService that returns canned JSON responses.

    The mock's chat method returns a dict by default.
    Override mock_llm.chat.return_value for custom responses.
    """
    canned = {
        "verdict": "optimal",
        "feedback": "Good approach.",
        "hint": None,
        "optimal_complexity": {"time": "O(n)", "space": "O(1)"},
        "pattern": "two_pointers",
        "follow_up": "What about edge cases?",
    }
    mock = MagicMock()
    mock.chat.return_value = canned
    return mock


@pytest.fixture()
def mock_llm_text():
    """Create a mock LLMService that returns plain text responses."""
    mock = MagicMock()
    mock.chat.return_value = "This is a test LLM response."
    return mock


@pytest.fixture()
def seed_framework(db_session):
    """Insert a 2-level framework tree."""
    root = FrameworkNode(
        path="pillar1",
        depth=0,
        title="Coding & Algorithms",
        importance=1.0,
        priority="P0",
        estimated_hours=40,
    )
    db_session.add(root)
    db_session.flush()

    child = FrameworkNode(
        parent_id=root.id,
        path="pillar1.dp",
        depth=1,
        title="Dynamic Programming",
        importance=0.9,
        priority="P0",
        estimated_hours=10,
    )
    db_session.add(child)
    db_session.commit()
    db_session.refresh(root)
    db_session.refresh(child)
    return [root, child]
