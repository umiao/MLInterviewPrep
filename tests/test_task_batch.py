"""Tests for TaskStore.batch() -- arg format and validation."""

import sys
from pathlib import Path

import pytest

# Make hooks importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".claude" / "hooks"))

from task_store import TaskStore  # noqa: E402


@pytest.fixture()
def store(tmp_path: Path) -> TaskStore:
    """Create a temporary TaskStore for testing."""
    db_path = tmp_path / "tasks.db"
    s = TaskStore(str(db_path))
    yield s
    s.close()


class TestBatchAdd:
    """Tests for batch add command."""

    def test_flat_format_works(self, store: TaskStore) -> None:
        """Flat keys (no args nesting) should create task with title."""
        results = store.batch([
            {"cmd": "add", "title": "Test task flat", "priority": "P0",
             "description": "Some description"},
        ])
        assert results[0]["ok"] is True
        task = store.get(results[0]["id"])
        assert task is not None
        assert task.title == "Test task flat"
        assert task.description == "Some description"

    def test_nested_args_format_works(self, store: TaskStore) -> None:
        """Nested args format should also create task with title."""
        results = store.batch([
            {"cmd": "add", "args": {"title": "Test task nested",
                                    "priority": "P1",
                                    "description": "Nested desc"}},
        ])
        assert results[0]["ok"] is True
        task = store.get(results[0]["id"])
        assert task is not None
        assert task.title == "Test task nested"
        assert task.description == "Nested desc"

    def test_empty_title_raises(self, store: TaskStore) -> None:
        """Batch add with empty title should raise, not silently create."""
        with pytest.raises(RuntimeError, match="title is required"):
            store.batch([
                {"cmd": "add", "title": "", "priority": "P0"},
            ])

    def test_missing_title_raises(self, store: TaskStore) -> None:
        """Batch add with no title key should raise."""
        with pytest.raises(RuntimeError, match="title is required"):
            store.batch([
                {"cmd": "add", "priority": "P0"},
            ])

    def test_nested_args_empty_title_raises(self, store: TaskStore) -> None:
        """Nested args with empty title should also raise."""
        with pytest.raises(RuntimeError, match="title is required"):
            store.batch([
                {"cmd": "add", "args": {"title": "  ", "priority": "P0"}},
            ])

    def test_multiple_adds_with_descriptions(self, store: TaskStore) -> None:
        """Multiple batch adds should all preserve title and description."""
        results = store.batch([
            {"cmd": "add", "title": "Task A", "description": "Desc A"},
            {"cmd": "add", "title": "Task B", "description": "Desc B"},
            {"cmd": "add", "title": "Task C", "description": "Desc C"},
        ])
        assert len(results) == 3
        for i, letter in enumerate(["A", "B", "C"]):
            task = store.get(results[i]["id"])
            assert task is not None
            assert task.title == f"Task {letter}"
            assert task.description == f"Desc {letter}"
