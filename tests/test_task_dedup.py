"""Tests for task deduplication logic in session_context and task_dedup_check."""
import sys
from pathlib import Path

# Make hooks importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".claude" / "hooks"))

from session_context import _get_active_tasks, _get_completed_task_ids  # noqa: E402
from task_dedup_check import _extract_section_task_ids  # noqa: E402


# ---------------------------------------------------------------------------
# _get_completed_task_ids tests
# ---------------------------------------------------------------------------
class TestGetCompletedTaskIds:
    """Tests for _get_completed_task_ids helper."""

    def test_no_completed_section(self) -> None:
        """Return empty set when there is no Completed Tasks section."""
        content = "## Active Tasks\n#### T-P0-1: Some task\n"
        assert _get_completed_task_ids(content) == set()

    def test_empty_completed_section(self) -> None:
        """Return empty set when Completed Tasks section has no task IDs."""
        content = (
            "## Active Tasks\n#### T-P0-1: Do stuff\n\n"
            "## Completed Tasks\n<!-- nothing here -->\n"
        )
        assert _get_completed_task_ids(content) == set()

    def test_finds_completed_ids(self) -> None:
        """Extract task IDs from completed section."""
        content = (
            "## Active Tasks\n#### T-P0-1: Active task\n\n"
            "## Completed Tasks\n"
            "- [x] T-P0-2: Done task (2025-01-01)\n"
            "- [x] T-P1-3: Another done (2025-01-02)\n"
        )
        assert _get_completed_task_ids(content) == {"T-P0-2", "T-P1-3"}

    def test_cross_section_isolation(self) -> None:
        """IDs in Active Tasks are not picked up as completed."""
        content = (
            "## Active Tasks\n#### T-P0-1: Active task\n\n"
            "## Completed Tasks\n"
            "- [x] T-P0-2: Done task (2025-01-01)\n"
        )
        result = _get_completed_task_ids(content)
        assert "T-P0-1" not in result
        assert "T-P0-2" in result


# ---------------------------------------------------------------------------
# _get_active_tasks dedup tests
# ---------------------------------------------------------------------------
class TestActiveTasksDedup:
    """Tests for dedup filtering in _get_active_tasks."""

    def _write_tasks_file(self, tmp_path: Path, content: str) -> Path:
        """Write a TASKS.md file in tmp_path and return root."""
        tasks_file = tmp_path / "TASKS.md"
        tasks_file.write_text(content, encoding="utf-8")
        return tmp_path

    def test_filters_duplicated_task(self, tmp_path: Path) -> None:
        """A task in both Active and Completed should be filtered from active output."""
        content = (
            "## Active Tasks\n"
            "#### T-P0-1: Duplicate task\n"
            "- **Priority**: P0\n"
            "- **Complexity**: S\n"
            "- **Depends on**: Nothing\n\n"
            "## Completed Tasks\n"
            "- [x] T-P0-1: Duplicate task (2025-01-01)\n"
        )
        root = self._write_tasks_file(tmp_path, content)
        result = _get_active_tasks(root, current_task_id=None)
        assert "T-P0-1" not in result

    def test_keeps_unique_active_tasks(self, tmp_path: Path) -> None:
        """Tasks only in Active (not in Completed) should appear in output."""
        content = (
            "## Active Tasks\n"
            "#### T-P0-1: Active task\n"
            "- **Priority**: P0\n"
            "- **Complexity**: M\n"
            "- **Depends on**: Nothing\n\n"
            "#### T-P0-2: Another active\n"
            "- **Priority**: P0\n"
            "- **Complexity**: S\n"
            "- **Depends on**: Nothing\n\n"
            "## Completed Tasks\n"
            "- [x] T-P0-3: Done task (2025-01-01)\n"
        )
        root = self._write_tasks_file(tmp_path, content)
        result = _get_active_tasks(root, current_task_id=None)
        assert "T-P0-1" in result
        assert "T-P0-2" in result
        assert "T-P0-3" not in result


# ---------------------------------------------------------------------------
# _extract_section_task_ids (hook) tests
# ---------------------------------------------------------------------------
class TestTaskDedupHook:
    """Tests for task_dedup_check._extract_section_task_ids."""

    def test_extracts_active_task_ids(self) -> None:
        """Extract IDs from Active Tasks section."""
        content = (
            "## Active Tasks\n"
            "#### T-P0-1: Task one\n"
            "#### T-P1-2: Task two\n\n"
            "## Completed Tasks\n"
        )
        result = _extract_section_task_ids(content, "Active Tasks")
        assert result == {"T-P0-1", "T-P1-2"}

    def test_extracts_completed_task_ids(self) -> None:
        """Extract IDs from Completed Tasks section."""
        content = (
            "## Active Tasks\n\n"
            "## Completed Tasks\n"
            "- [x] T-P0-1: Done (2025-01-01)\n"
            "- [x] T-P0-2: Also done (2025-01-02)\n"
        )
        result = _extract_section_task_ids(content, "Completed Tasks")
        assert result == {"T-P0-1", "T-P0-2"}

    def test_missing_section_returns_empty(self) -> None:
        """Return empty set for a section that does not exist."""
        content = "## Active Tasks\n#### T-P0-1: Task\n"
        result = _extract_section_task_ids(content, "Nonexistent Section")
        assert result == set()

    def test_overlap_detection(self) -> None:
        """Demonstrate overlap detection using set intersection."""
        content = (
            "## Active Tasks\n"
            "#### T-P0-1: Duplicate\n\n"
            "## Completed Tasks\n"
            "- [x] T-P0-1: Duplicate (2025-01-01)\n"
            "- [x] T-P0-2: Only completed (2025-01-02)\n"
        )
        active = _extract_section_task_ids(content, "Active Tasks")
        completed = _extract_section_task_ids(content, "Completed Tasks")
        overlap = active & completed
        assert overlap == {"T-P0-1"}
