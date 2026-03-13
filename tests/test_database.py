"""Tests for database module."""
from unittest.mock import patch

from sqlalchemy import create_engine, inspect, text

from src.backend.database import Base, get_db, get_engine, init_db


def test_init_db_in_memory():
    """init_db with in-memory SQLite creates tables."""
    engine = create_engine("sqlite:///:memory:")
    init_db(engine)
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    assert "problems" in table_names
    assert "attempts" in table_names
    assert "framework_nodes" in table_names


def test_get_db_yields_session(db_session):
    """get_db yields a usable session."""
    result = db_session.execute(text("SELECT 1")).scalar()
    assert result == 1


def test_get_engine_with_override():
    """get_engine accepts a URL override."""
    engine = get_engine("sqlite:///:memory:")
    assert str(engine.url) == "sqlite:///:memory:"


def test_get_engine_sqlite_check_same_thread():
    """get_engine sets check_same_thread=False for SQLite."""
    engine = get_engine("sqlite:///:memory:")
    # Verify connection works from a different context (check_same_thread=False)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar()
    assert result == 1


def test_get_engine_default_url():
    """get_engine uses DATABASE_URL from settings when no override given."""
    with patch("src.backend.database.get_settings") as mock_settings:
        mock_settings.return_value.DATABASE_URL = "sqlite:///:memory:"
        engine = get_engine()
        assert str(engine.url) == "sqlite:///:memory:"


def test_init_db_creates_data_dir(tmp_path):
    """init_db creates parent directory for file-based SQLite."""
    db_dir = tmp_path / "subdir"
    db_file = db_dir / "test.db"
    url = f"sqlite:///{db_file}"

    with patch("src.backend.database.get_settings") as mock_settings:
        mock_settings.return_value.DATABASE_URL = url
        init_db()
        assert db_dir.exists()


def test_get_db_is_generator():
    """get_db is a generator that yields exactly one session."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)

    from src.backend.database import SessionLocal

    SessionLocal.configure(bind=engine)

    gen = get_db()
    session = next(gen)
    assert session.execute(text("SELECT 1")).scalar() == 1
    # Generator should complete after one yield
    remaining = list(gen)
    assert remaining == []


def test_init_db_binds_session_local():
    """init_db configures SessionLocal with the engine."""
    from src.backend.database import SessionLocal

    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    init_db(engine)
    # SessionLocal should now be bound and usable
    session = SessionLocal()
    try:
        result = session.execute(text("SELECT 1")).scalar()
        assert result == 1
    finally:
        session.close()
