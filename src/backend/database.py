"""Database engine and session setup."""
import logging
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from src.backend.config import get_settings

logger = logging.getLogger(__name__)

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
    _run_migrations(engine)
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


# ---------------------------------------------------------------------------
# Schema migrations
# ---------------------------------------------------------------------------

# Each migration is a (version, description, sql_statements) tuple.
# sql_statements is a list of SQL strings to execute in order.
# Migrations MUST be idempotent (use IF NOT EXISTS / check before ALTER).
MIGRATIONS: list[tuple[int, str, list[str]]] = [
    (
        1,
        "Add framework_node_id column and index to problems table",
        [
            # SQLite has no IF NOT EXISTS for ALTER TABLE ADD COLUMN,
            # so we check via PRAGMA before executing.
            "ADD_COLUMN_IF_MISSING:problems:framework_node_id:"
            "ALTER TABLE problems ADD COLUMN framework_node_id INTEGER "
            "REFERENCES framework_nodes(id) ON DELETE SET NULL",
            "CREATE INDEX IF NOT EXISTS ix_problems_framework_node_id "
            "ON problems(framework_node_id)",
        ],
    ),
    (
        3,
        "Add prep_notes column to companies table",
        [
            "ADD_COLUMN_IF_MISSING:companies:prep_notes:"
            "ALTER TABLE companies ADD COLUMN prep_notes TEXT",
        ],
    ),
    (
        2,
        "Create interview_events table",
        [
            "CREATE TABLE IF NOT EXISTS interview_events ("
            "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "  company_id INTEGER REFERENCES companies(id) ON DELETE SET NULL,"
            "  company_name VARCHAR NOT NULL,"
            "  event_type VARCHAR NOT NULL,"
            "  title VARCHAR NOT NULL,"
            "  description TEXT,"
            "  scheduled_at TIMESTAMP NOT NULL,"
            "  duration_minutes INTEGER,"
            "  location VARCHAR,"
            "  status VARCHAR NOT NULL DEFAULT 'upcoming',"
            "  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            ")",
            "CREATE INDEX IF NOT EXISTS ix_interview_events_scheduled_at "
            "ON interview_events(scheduled_at)",
        ],
    ),
    (
        4,
        "Create reading_progress, reading_sessions, audio_cache tables",
        [
            "CREATE TABLE IF NOT EXISTS reading_progress ("
            "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "  content_type VARCHAR NOT NULL,"
            "  content_id INTEGER NOT NULL,"
            "  last_chunk_index INTEGER DEFAULT 0,"
            "  char_offset INTEGER DEFAULT 0,"
            "  total_chars INTEGER DEFAULT 0,"
            "  completed BOOLEAN DEFAULT 0,"
            "  last_read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
            "  UNIQUE(content_type, content_id)"
            ")",
            "CREATE TABLE IF NOT EXISTS reading_sessions ("
            "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "  started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,"
            "  ended_at TIMESTAMP,"
            "  content_items_read INTEGER DEFAULT 0,"
            "  total_duration_seconds REAL DEFAULT 0.0,"
            "  tts_engine VARCHAR"
            ")",
            "CREATE TABLE IF NOT EXISTS audio_cache ("
            "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "  content_type VARCHAR NOT NULL,"
            "  content_id INTEGER NOT NULL,"
            "  content_hash VARCHAR NOT NULL,"
            "  file_path TEXT NOT NULL,"
            "  engine VARCHAR NOT NULL,"
            "  voice VARCHAR NOT NULL,"
            "  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
            "  UNIQUE(content_type, content_id, engine, voice)"
            ")",
        ],
    ),
    (
        5,
        "Create tts_summaries table for LLM-generated TTS summaries",
        [
            "CREATE TABLE IF NOT EXISTS tts_summaries ("
            "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "  content_type VARCHAR NOT NULL,"
            "  content_id INTEGER NOT NULL,"
            "  content_hash VARCHAR NOT NULL,"
            "  summary_text TEXT NOT NULL,"
            "  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
            "  UNIQUE(content_type, content_id)"
            ")",
        ],
    ),
    (
        6,
        "Create transcripts table for faithful spoken-word transcripts",
        [
            "CREATE TABLE IF NOT EXISTS transcripts ("
            "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "  content_type VARCHAR NOT NULL,"
            "  content_id INTEGER NOT NULL,"
            "  source_hash VARCHAR NOT NULL,"
            "  transcript_text TEXT NOT NULL,"
            "  transcript_hash VARCHAR NOT NULL,"
            "  generation_method VARCHAR NOT NULL,"
            "  prompt_version INTEGER NOT NULL,"
            "  is_latest BOOLEAN NOT NULL DEFAULT 1,"
            "  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
            "  UNIQUE(content_type, content_id, source_hash, prompt_version)"
            ")",
        ],
    ),
    (
        7,
        "Add description, neetcode_slug, description_source columns to problems",
        [
            "ADD_COLUMN_IF_MISSING:problems:description:"
            "ALTER TABLE problems ADD COLUMN description TEXT",
            "ADD_COLUMN_IF_MISSING:problems:neetcode_slug:"
            "ALTER TABLE problems ADD COLUMN neetcode_slug VARCHAR",
            "ADD_COLUMN_IF_MISSING:problems:description_source:"
            "ALTER TABLE problems ADD COLUMN description_source VARCHAR",
        ],
    ),
    (
        8,
        "Add notes column to problems",
        [
            "ADD_COLUMN_IF_MISSING:problems:notes:"
            "ALTER TABLE problems ADD COLUMN notes TEXT",
        ],
    ),
    (
        9,
        "Create forum_seeds, forum_post_links, forum_posts tables",
        [
            "CREATE TABLE IF NOT EXISTS forum_seeds ("
            "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "  url TEXT NOT NULL UNIQUE,"
            "  source_site VARCHAR NOT NULL,"
            "  label TEXT,"
            "  company_id INTEGER REFERENCES companies(id) ON DELETE SET NULL,"
            "  is_active BOOLEAN DEFAULT 1,"
            "  last_scraped_at TIMESTAMP,"
            "  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            ")",
            "CREATE TABLE IF NOT EXISTS forum_post_links ("
            "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "  forum_seed_id INTEGER NOT NULL REFERENCES forum_seeds(id) ON DELETE CASCADE,"
            "  url TEXT NOT NULL UNIQUE,"
            "  external_post_id TEXT UNIQUE,"
            "  title TEXT,"
            "  discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
            "  status VARCHAR NOT NULL DEFAULT 'pending'"
            "    CHECK(status IN ('pending', 'fetched', 'failed')),"
            "  retry_count INTEGER DEFAULT 0,"
            "  last_error TEXT,"
            "  fetch_order INTEGER"
            ")",
            "CREATE TABLE IF NOT EXISTS forum_posts ("
            "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "  forum_post_link_id INTEGER NOT NULL UNIQUE"
            "    REFERENCES forum_post_links(id) ON DELETE CASCADE,"
            "  raw_text TEXT NOT NULL,"
            "  content_hash TEXT NOT NULL,"
            "  author TEXT,"
            "  published_at TEXT,"
            "  fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
            "  company_id INTEGER REFERENCES companies(id) ON DELETE SET NULL"
            ")",
        ],
    ),
    (
        10,
        "Create company_documents table for child docs per company",
        [
            "CREATE TABLE IF NOT EXISTS company_documents ("
            "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "  company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,"
            "  title VARCHAR NOT NULL,"
            "  content TEXT NOT NULL DEFAULT '',"
            "  source_type VARCHAR NOT NULL DEFAULT 'manual',"
            "  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
            "  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            ")",
            "CREATE INDEX IF NOT EXISTS ix_company_documents_company_id "
            "ON company_documents(company_id)",
        ],
    ),
    (
        11,
        "Add last_scraped_page column to forum_seeds",
        [
            "ADD_COLUMN_IF_MISSING:forum_seeds:last_scraped_page:"
            "ALTER TABLE forum_seeds ADD COLUMN last_scraped_page INTEGER",
        ],
    ),
    (
        12,
        "Fix NULL priority in problems table",
        [
            "UPDATE problems SET priority = 2 WHERE priority IS NULL",
        ],
    ),
]


def _run_migrations(engine) -> None:
    """Apply pending schema migrations.

    Tracks applied versions in a ``schema_versions`` table.
    Each migration is idempotent and safe to re-run.

    Args:
        engine: SQLAlchemy engine to run migrations against.
    """
    with engine.begin() as conn:
        conn.execute(text(
            "CREATE TABLE IF NOT EXISTS schema_versions ("
            "  version INTEGER PRIMARY KEY,"
            "  description TEXT NOT NULL,"
            "  applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            ")"
        ))

        rows = conn.execute(text("SELECT version FROM schema_versions")).fetchall()
        applied = {row[0] for row in rows}

        for version, description, statements in MIGRATIONS:
            if version in applied:
                continue

            for stmt in statements:
                if stmt.startswith("ADD_COLUMN_IF_MISSING:"):
                    _add_column_if_missing(conn, stmt)
                else:
                    conn.execute(text(stmt))

            conn.execute(
                text(
                    "INSERT INTO schema_versions (version, description) "
                    "VALUES (:v, :d)"
                ),
                {"v": version, "d": description},
            )
            logger.info("Applied migration %d: %s", version, description)


def _add_column_if_missing(conn, directive: str) -> None:
    """Handle ADD_COLUMN_IF_MISSING directive.

    Format: ``ADD_COLUMN_IF_MISSING:table:column:ALTER TABLE ...``

    Args:
        conn: Active database connection.
        directive: The directive string to parse.
    """
    parts = directive.split(":", 3)
    # parts = ["ADD_COLUMN_IF_MISSING", table, column, alter_sql]
    table = parts[1]
    column = parts[2]
    alter_sql = parts[3]

    existing = conn.execute(text(f"PRAGMA table_info({table})")).fetchall()
    existing_names = {row[1] for row in existing}

    if column not in existing_names:
        conn.execute(text(alter_sql))
