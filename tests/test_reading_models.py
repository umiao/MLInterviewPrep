"""Tests for Reading models: ReadingProgress, ReadingSession, AudioCache.

Covers CRUD operations, unique constraints, and cache invalidation logic.
"""
import hashlib

from sqlalchemy import inspect

from src.backend.models.reading import AudioCache, ReadingProgress, ReadingSession


class TestReadingProgress:
    """Tests for ReadingProgress model."""

    def test_create_and_query(self, db_session):
        """Can create and retrieve a ReadingProgress record."""
        rp = ReadingProgress(
            content_type="framework_node",
            content_id=1,
            last_chunk_index=0,
            char_offset=0,
            total_chars=500,
            completed=False,
        )
        db_session.add(rp)
        db_session.commit()

        result = db_session.query(ReadingProgress).filter_by(
            content_type="framework_node", content_id=1
        ).one()
        assert result.total_chars == 500
        assert result.completed is False

    def test_update_progress(self, db_session):
        """Can update chunk index and char offset."""
        rp = ReadingProgress(
            content_type="framework_node", content_id=2,
            last_chunk_index=0, char_offset=0, total_chars=1000,
        )
        db_session.add(rp)
        db_session.commit()

        rp.last_chunk_index = 3
        rp.char_offset = 450
        db_session.commit()

        result = db_session.query(ReadingProgress).filter_by(content_id=2).one()
        assert result.last_chunk_index == 3
        assert result.char_offset == 450

    def test_unique_constraint(self, db_session):
        """Duplicate content_type+content_id raises IntegrityError."""
        from sqlalchemy.exc import IntegrityError

        rp1 = ReadingProgress(content_type="prep_notes", content_id=5)
        rp2 = ReadingProgress(content_type="prep_notes", content_id=5)
        db_session.add(rp1)
        db_session.commit()
        db_session.add(rp2)
        try:
            db_session.commit()
            raise AssertionError("Expected IntegrityError")
        except IntegrityError:
            db_session.rollback()

    def test_different_types_same_id(self, db_session):
        """Different content_type with same content_id is allowed."""
        rp1 = ReadingProgress(content_type="framework_node", content_id=1)
        rp2 = ReadingProgress(content_type="prep_notes", content_id=1)
        db_session.add_all([rp1, rp2])
        db_session.commit()

        count = db_session.query(ReadingProgress).filter_by(content_id=1).count()
        assert count == 2


class TestReadingSession:
    """Tests for ReadingSession model."""

    def test_create_session(self, db_session):
        """Can create a reading session."""
        rs = ReadingSession(
            content_items_read=5,
            total_duration_seconds=300.0,
            tts_engine="edge_tts",
        )
        db_session.add(rs)
        db_session.commit()

        result = db_session.query(ReadingSession).first()
        assert result.content_items_read == 5
        assert result.tts_engine == "edge_tts"


class TestAudioCache:
    """Tests for AudioCache model."""

    def test_create_cache_entry(self, db_session):
        """Can create an audio cache entry."""
        ac = AudioCache(
            content_type="framework_node",
            content_id=1,
            content_hash=hashlib.sha256(b"test content").hexdigest(),
            file_path="data/tts_cache/abc123.mp3",
            engine="edge_tts",
            voice="en-US-AriaNeural",
        )
        db_session.add(ac)
        db_session.commit()

        result = db_session.query(AudioCache).first()
        assert result.engine == "edge_tts"
        assert result.content_hash == hashlib.sha256(b"test content").hexdigest()

    def test_unique_constraint_content_engine_voice(self, db_session):
        """Duplicate content_type+content_id+engine+voice raises IntegrityError."""
        from sqlalchemy.exc import IntegrityError

        kwargs = dict(
            content_type="framework_node", content_id=1,
            content_hash="hash1", file_path="f1.mp3",
            engine="edge_tts", voice="en-US-AriaNeural",
        )
        db_session.add(AudioCache(**kwargs))
        db_session.commit()

        db_session.add(AudioCache(**{**kwargs, "content_hash": "hash2", "file_path": "f2.mp3"}))
        try:
            db_session.commit()
            raise AssertionError("Expected IntegrityError")
        except IntegrityError:
            db_session.rollback()

    def test_different_engines_same_content(self, db_session):
        """Same content with different engines is allowed."""
        base = dict(
            content_type="framework_node", content_id=1,
            content_hash="hash1", voice="en-US-AriaNeural",
        )
        db_session.add(AudioCache(**base, file_path="f1.mp3", engine="edge_tts"))
        db_session.add(AudioCache(**base, file_path="f2.mp3", engine="openai"))
        db_session.commit()

        count = db_session.query(AudioCache).filter_by(content_id=1).count()
        assert count == 2

    def test_cache_invalidation_hash_mismatch(self, db_session):
        """Cache entry with stale hash should be detected and replaceable."""
        old_hash = hashlib.sha256(b"old content").hexdigest()
        new_hash = hashlib.sha256(b"new content").hexdigest()

        ac = AudioCache(
            content_type="framework_node", content_id=10,
            content_hash=old_hash, file_path="old.mp3",
            engine="edge_tts", voice="en-US-AriaNeural",
        )
        db_session.add(ac)
        db_session.commit()

        # Simulate cache invalidation: content changed, hash differs
        cached = db_session.query(AudioCache).filter_by(
            content_type="framework_node", content_id=10,
            engine="edge_tts", voice="en-US-AriaNeural",
        ).first()
        assert cached.content_hash != new_hash  # Stale

        # Update cache entry with new hash and file
        cached.content_hash = new_hash
        cached.file_path = "new.mp3"
        db_session.commit()

        refreshed = db_session.query(AudioCache).filter_by(content_id=10).one()
        assert refreshed.content_hash == new_hash
        assert refreshed.file_path == "new.mp3"


class TestTablesExist:
    """Verify all three reading tables are created."""

    def test_reading_tables_created(self, db_engine):
        """init_db creates reading_progress, reading_sessions, audio_cache tables."""
        insp = inspect(db_engine)
        table_names = insp.get_table_names()
        assert "reading_progress" in table_names
        assert "reading_sessions" in table_names
        assert "audio_cache" in table_names
