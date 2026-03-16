"""Tests for content_pipeline preprocessing."""
from src.backend.services.content_pipeline import preprocess_for_tts


def test_strip_headings():
    """Markdown headings are stripped but text preserved."""
    text = "# Hello\n## World\n### Level 3"
    result = preprocess_for_tts(text)
    assert "Hello" in result
    assert "World" in result
    assert "Level 3" in result
    assert "#" not in result


def test_remove_bold_italic():
    """Bold and italic markers removed, text preserved."""
    text = "This is **bold** and *italic* and ***both***."
    result = preprocess_for_tts(text)
    assert "**" not in result
    assert "*italic*" not in result
    assert "bold" in result
    assert "italic" in result
    assert "both" in result


def test_remove_links():
    """Markdown links converted to plain text."""
    text = "See [this page](https://example.com) for details."
    result = preprocess_for_tts(text)
    assert "this page" in result
    assert "https://example.com" not in result
    assert "[" not in result


def test_skip_code_blocks():
    """Code blocks are entirely skipped."""
    text = "Before code.\n```python\ndef foo():\n    pass\n```\nAfter code."
    result = preprocess_for_tts(text)
    assert "Before code" in result
    assert "After code" in result
    assert "def foo" not in result
    assert "pass" not in result


def test_remove_inline_code():
    """Inline code backticks removed, content preserved."""
    text = "Use `pip install` to install."
    result = preprocess_for_tts(text)
    assert "`" not in result
    assert "pip install" in result


def test_bullet_points_to_sentences():
    """Bullet points converted to plain text."""
    text = "- First item\n- Second item\n* Third item"
    result = preprocess_for_tts(text)
    assert "First item" in result
    assert "Second item" in result
    assert "Third item" in result
    assert "- " not in result
    assert "* " not in result


def test_numbered_lists():
    """Numbered list prefixes removed."""
    text = "1. First\n2. Second\n3. Third"
    result = preprocess_for_tts(text)
    assert "First" in result
    assert "1." not in result


def test_expand_abbreviations():
    """Common abbreviations expanded."""
    text = "e.g. trees, i.e. graphs, etc."
    result = preprocess_for_tts(text)
    assert "for example" in result
    assert "that is" in result
    assert "et cetera" in result


def test_collapse_blank_lines():
    """Multiple blank lines collapsed to one."""
    text = "A\n\n\n\n\nB"
    result = preprocess_for_tts(text)
    assert "\n\n\n" not in result
    assert "A" in result
    assert "B" in result


def test_empty_input():
    """Empty string returns empty."""
    assert preprocess_for_tts("") == ""
    assert preprocess_for_tts("   ") == ""


def test_combined_markdown():
    """Full markdown document processed correctly."""
    text = """# Dynamic Programming

**Dynamic programming** is an optimization technique that solves problems
by breaking them into overlapping sub-problems.

## Key Concepts

- **Memoization**: Store results of expensive function calls
- **Tabulation**: Build solution bottom-up, i.e. iteratively

```python
dp[i] = dp[i-1] + dp[i-2]
```

See [Wikipedia](https://en.wikipedia.org/wiki/DP) for more details, e.g. examples.
"""
    result = preprocess_for_tts(text)
    assert "Dynamic Programming" in result
    assert "Dynamic programming" in result
    assert "Memoization" in result
    assert "#" not in result
    assert "**" not in result
    assert "```" not in result
    assert "dp[i]" not in result
    assert "for example" in result
    assert "that is" in result
