"""Tests for the Blind 75 notes import script (docx parser logic)."""
import importlib
import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Make scripts importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import the module directly by path
_spec = importlib.util.spec_from_file_location(
    "import_blind75_notes",
    PROJECT_ROOT / "scripts" / "import_blind75_notes.py",
)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["import_blind75_notes"] = _mod
_spec.loader.exec_module(_mod)

parse_docx = _mod.parse_docx


def _make_mock_doc(paragraphs: list[str]):
    """Create a mock docx Document with given paragraph texts.

    Args:
        paragraphs: List of paragraph text strings.

    Returns:
        Mock Document object.
    """
    doc = MagicMock()
    mock_paras = []
    for text in paragraphs:
        p = MagicMock()
        p.text = text
        mock_paras.append(p)
    doc.paragraphs = mock_paras
    return doc


def _run_parse(paragraphs: list[str]) -> list[dict]:
    """Run parse_docx with mocked docx.Document.

    Args:
        paragraphs: List of paragraph text strings.

    Returns:
        Parsed entries from parse_docx.
    """
    mock_doc = _make_mock_doc(paragraphs)
    mock_docx_module = MagicMock()
    mock_docx_module.Document.return_value = mock_doc

    with patch.dict(sys.modules, {"docx": mock_docx_module}):
        return parse_docx("fake.docx")


class TestParseDocx:
    """Test docx parsing logic."""

    def test_basic_extraction(self):
        """Extracts problem ID and notes from simple format."""
        result = _run_parse([
            "1. Two Sum",
            "Use a hash map to store complements.",
            "Time: O(n), Space: O(n)",
            "",
            "217. Contains Duplicate",
            "Sort or use a set.",
        ])

        assert len(result) == 2
        assert result[0]["leetcode_id"] == 1
        assert "hash map" in result[0]["notes"]
        assert result[1]["leetcode_id"] == 217

    def test_lc_prefix_format(self):
        """Handles 'LC 1' and 'LeetCode 217' formats."""
        result = _run_parse([
            "LC 1: Two Sum",
            "Hash map approach.",
            "",
            "LeetCode 217",
            "Set approach.",
        ])

        assert len(result) == 2
        assert result[0]["leetcode_id"] == 1
        assert result[1]["leetcode_id"] == 217

    def test_empty_notes_skipped(self):
        """Problems with no content after header are not included."""
        result = _run_parse([
            "1. Two Sum",
            "",
            "217. Contains Duplicate",
            "Has notes.",
        ])

        # Problem 1 has empty notes, so only problem 217 should appear
        assert len(result) == 1
        assert result[0]["leetcode_id"] == 217

    def test_multiline_notes(self):
        """Notes spanning multiple paragraphs are combined."""
        result = _run_parse([
            "1. Two Sum",
            "Line 1.",
            "Line 2.",
            "Line 3.",
        ])

        assert len(result) == 1
        assert "Line 1." in result[0]["notes"]
        assert "Line 3." in result[0]["notes"]
