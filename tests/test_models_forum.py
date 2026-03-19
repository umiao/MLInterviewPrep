"""Tests for forum models: ForumSeed, ForumPostLink, ForumPost."""
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.backend.database import Base, _run_migrations


def _make_session():
    """Create an in-memory DB with all tables and return a session."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)
    return engine, session_factory()


def test_import_forum_models():
    """ForumSeed, ForumPostLink, ForumPost importable from models package."""
    from src.backend.models import ForumPost, ForumPostLink, ForumSeed

    assert ForumSeed.__tablename__ == "forum_seeds"
    assert ForumPostLink.__tablename__ == "forum_post_links"
    assert ForumPost.__tablename__ == "forum_posts"


def test_tables_created_via_create_all():
    """Tables created correctly via Base.metadata.create_all."""
    engine, _ = _make_session()
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "forum_seeds" in tables
    assert "forum_post_links" in tables
    assert "forum_posts" in tables


def test_create_forum_seed(db_session):
    """Can create a ForumSeed row."""
    from src.backend.models.forum import ForumSeed

    seed = ForumSeed(url="https://example.com/forum", source_site="1point3acres")
    db_session.add(seed)
    db_session.commit()
    assert seed.id is not None
    assert seed.is_active is True
    assert seed.last_scraped_at is None


def test_forum_seed_url_unique(db_session):
    """ForumSeed.url has UNIQUE constraint."""
    from src.backend.models.forum import ForumSeed

    s1 = ForumSeed(url="https://example.com/a", source_site="1point3acres")
    s2 = ForumSeed(url="https://example.com/a", source_site="1point3acres")
    db_session.add(s1)
    db_session.commit()
    db_session.add(s2)
    try:
        db_session.commit()
        raise AssertionError("Should have raised IntegrityError")
    except IntegrityError:
        db_session.rollback()


def test_create_post_link(db_session):
    """Can create a ForumPostLink with correct defaults."""
    from src.backend.models.forum import ForumPostLink, ForumSeed

    seed = ForumSeed(url="https://example.com/forum", source_site="1point3acres")
    db_session.add(seed)
    db_session.commit()

    link = ForumPostLink(
        forum_seed_id=seed.id,
        url="https://example.com/post/1",
        external_post_id="pid12345",
        title="Test Post",
        fetch_order=1,
    )
    db_session.add(link)
    db_session.commit()
    assert link.status == "pending"
    assert link.retry_count == 0
    assert link.last_error is None


def test_post_link_url_unique(db_session):
    """ForumPostLink.url has UNIQUE constraint."""
    from src.backend.models.forum import ForumPostLink, ForumSeed

    seed = ForumSeed(url="https://example.com/forum", source_site="1point3acres")
    db_session.add(seed)
    db_session.commit()

    l1 = ForumPostLink(forum_seed_id=seed.id, url="https://example.com/post/1")
    l2 = ForumPostLink(forum_seed_id=seed.id, url="https://example.com/post/1")
    db_session.add(l1)
    db_session.commit()
    db_session.add(l2)
    try:
        db_session.commit()
        raise AssertionError("Should have raised IntegrityError")
    except IntegrityError:
        db_session.rollback()


def test_post_link_external_id_unique(db_session):
    """ForumPostLink.external_post_id has UNIQUE constraint."""
    from src.backend.models.forum import ForumPostLink, ForumSeed

    seed = ForumSeed(url="https://example.com/forum", source_site="1point3acres")
    db_session.add(seed)
    db_session.commit()

    l1 = ForumPostLink(
        forum_seed_id=seed.id, url="https://example.com/post/1", external_post_id="pid1"
    )
    l2 = ForumPostLink(
        forum_seed_id=seed.id, url="https://example.com/post/2", external_post_id="pid1"
    )
    db_session.add(l1)
    db_session.commit()
    db_session.add(l2)
    try:
        db_session.commit()
        raise AssertionError("Should have raised IntegrityError")
    except IntegrityError:
        db_session.rollback()


def test_create_forum_post(db_session):
    """Can create a ForumPost linked to a ForumPostLink."""
    from src.backend.models.forum import ForumPost, ForumPostLink, ForumSeed

    seed = ForumSeed(url="https://example.com/forum", source_site="1point3acres")
    db_session.add(seed)
    db_session.commit()

    link = ForumPostLink(forum_seed_id=seed.id, url="https://example.com/post/1")
    db_session.add(link)
    db_session.commit()

    post = ForumPost(
        forum_post_link_id=link.id,
        raw_text="Interview experience at company X",
        content_hash="abc123",
        author="user1",
        published_at="2026-03-01",
    )
    db_session.add(post)
    db_session.commit()
    assert post.id is not None
    assert post.fetched_at is not None


def test_forum_post_link_id_unique(db_session):
    """ForumPost.forum_post_link_id has UNIQUE constraint (one post per link)."""
    from src.backend.models.forum import ForumPost, ForumPostLink, ForumSeed

    seed = ForumSeed(url="https://example.com/forum", source_site="1point3acres")
    db_session.add(seed)
    db_session.commit()

    link = ForumPostLink(forum_seed_id=seed.id, url="https://example.com/post/1")
    db_session.add(link)
    db_session.commit()

    p1 = ForumPost(
        forum_post_link_id=link.id, raw_text="text1", content_hash="hash1"
    )
    p2 = ForumPost(
        forum_post_link_id=link.id, raw_text="text2", content_hash="hash2"
    )
    db_session.add(p1)
    db_session.commit()
    db_session.add(p2)
    try:
        db_session.commit()
        raise AssertionError("Should have raised IntegrityError")
    except IntegrityError:
        db_session.rollback()


def test_cascade_delete(db_session):
    """Deleting ForumSeed cascades to ForumPostLinks and ForumPosts."""
    from src.backend.models.forum import ForumPost, ForumPostLink, ForumSeed

    seed = ForumSeed(url="https://example.com/forum", source_site="1point3acres")
    db_session.add(seed)
    db_session.commit()

    link = ForumPostLink(forum_seed_id=seed.id, url="https://example.com/post/1")
    db_session.add(link)
    db_session.commit()

    post = ForumPost(
        forum_post_link_id=link.id, raw_text="content", content_hash="hash"
    )
    db_session.add(post)
    db_session.commit()

    # Delete seed -- should cascade
    db_session.delete(seed)
    db_session.commit()

    assert db_session.query(ForumSeed).count() == 0
    assert db_session.query(ForumPostLink).count() == 0
    assert db_session.query(ForumPost).count() == 0


def test_status_check_constraint(db_session):
    """ForumPostLink.status CHECK constraint rejects invalid values."""
    from src.backend.models.forum import ForumPostLink, ForumSeed

    seed = ForumSeed(url="https://example.com/forum", source_site="1point3acres")
    db_session.add(seed)
    db_session.commit()

    link = ForumPostLink(
        forum_seed_id=seed.id, url="https://example.com/post/1", status="invalid"
    )
    db_session.add(link)
    try:
        db_session.commit()
        raise AssertionError("Should have raised IntegrityError for invalid status")
    except IntegrityError:
        db_session.rollback()


def test_migration_v9_idempotent():
    """Migration v9 is idempotent -- running twice does not error."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # create_all sets up base tables, then migrations add columns/new tables
    Base.metadata.create_all(bind=engine)
    _run_migrations(engine)
    _run_migrations(engine)

    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "forum_seeds" in tables
    assert "forum_post_links" in tables
    assert "forum_posts" in tables


def test_relationship_navigation(db_session):
    """Relationships navigate correctly between models."""
    from src.backend.models.forum import ForumPost, ForumPostLink, ForumSeed

    seed = ForumSeed(url="https://example.com/forum", source_site="1point3acres")
    db_session.add(seed)
    db_session.commit()

    link = ForumPostLink(forum_seed_id=seed.id, url="https://example.com/post/1")
    db_session.add(link)
    db_session.commit()

    post = ForumPost(
        forum_post_link_id=link.id, raw_text="content", content_hash="hash"
    )
    db_session.add(post)
    db_session.commit()

    # Navigate: seed -> links -> post
    assert len(seed.post_links) == 1
    assert seed.post_links[0].url == "https://example.com/post/1"
    assert seed.post_links[0].post.raw_text == "content"

    # Navigate: post -> link -> seed
    assert post.post_link.forum_seed.url == "https://example.com/forum"
