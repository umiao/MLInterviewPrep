"""Database engine and session setup."""
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from src.backend.config import get_settings

Base = declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False)


def get_engine(database_url: str | None = None):
    """Create a SQLAlchemy engine.

    Args:
        database_url: Override URL. Defaults to settings.DATABASE_URL.

    Returns:
        SQLAlchemy Engine instance.
    """
    url = database_url or get_settings().DATABASE_URL
    connect_args: dict = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(url, connect_args=connect_args)


def get_db():
    """FastAPI dependency that yields a DB session and closes it after the request."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(engine=None):
    """Create all tables. Call on startup.

    Args:
        engine: Optional engine override. Creates default if None.
    """
    if engine is None:
        engine = get_engine()
        # Ensure data directory exists for file-based SQLite
        url = str(engine.url)
        if url.startswith("sqlite:///") and url != "sqlite:///:memory:":
            db_path = url.replace("sqlite:///", "")
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    SessionLocal.configure(bind=engine)
    # Import models so Base.metadata sees them
    import src.backend.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _enable_wal(engine)
    _create_views(engine)


def _enable_wal(engine) -> None:
    """Enable WAL journal mode for file-based SQLite databases.

    Args:
        engine: SQLAlchemy engine to configure.
    """
    url = str(engine.url)
    if url.startswith("sqlite") and ":memory:" not in url:
        with engine.begin() as conn:
            conn.execute(text("PRAGMA journal_mode=WAL"))


def _create_views(engine) -> None:
    """Create database views for aggregate reporting.

    Args:
        engine: SQLAlchemy engine to execute DDL against.
    """
    v_problem_stats = text("""
        CREATE VIEW IF NOT EXISTS v_problem_stats AS
        SELECT
            p.id AS problem_id,
            p.title,
            p.difficulty,
            p.pattern,
            p.category,
            p.is_completed,
            p.comfort_level,
            p.next_review_at,
            COUNT(a.id) AS attempt_count,
            COALESCE(AVG(a.duration_seconds), 0) AS avg_duration_seconds,
            MAX(a.started_at) AS last_attempt_at,
            MAX(a.comfort_after) AS best_comfort
        FROM problems p
        LEFT JOIN attempts a ON a.problem_id = p.id
        GROUP BY p.id
    """)

    v_weekly_progress = text("""
        CREATE VIEW IF NOT EXISTS v_weekly_progress AS
        SELECT
            strftime('%Y-%W', sl.date) AS year_week,
            COUNT(DISTINCT sl.framework_node_id) AS nodes_studied,
            SUM(sl.duration_minutes) AS total_study_minutes,
            ROUND(SUM(sl.duration_minutes) / 60.0, 1) AS total_study_hours,
            COUNT(sl.id) AS session_count
        FROM study_logs sl
        GROUP BY strftime('%Y-%W', sl.date)
    """)

    with engine.begin() as conn:
        conn.execute(v_problem_stats)
        conn.execute(v_weekly_progress)
