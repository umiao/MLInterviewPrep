"""Tests for content_pipeline preprocessing, chunking, queue, and content retrieval."""
import json

from src.backend.models.company import Company
from src.backend.models.framework import FrameworkNode
from src.backend.models.problem import Problem
from src.backend.models.reading import ReadingProgress
from src.backend.services.content_pipeline import (
    CONTENT_TYPE_FRAMEWORK_NODE,
    CONTENT_TYPE_INTERVIEW_QUESTION,
    CONTENT_TYPE_PREP_NOTES,
    chunk_text,
    compute_content_hash,
    get_content_text,
    get_reading_queue,
    preprocess_for_tts,
)


# ---------------------------------------------------------------------------
# preprocess_for_tts tests
# ---------------------------------------------------------------------------
def test_strip_headings():
    """Markdown headings are stripped but text preserved."""
    text = "# Hello\n## World\n### Level 3"
    result = preprocess_for_tts(text)
    assert "Hello" in result
    assert "World" in result
    assert "Level 3" in result
    assert "#" not in result


def test_headings_get_pause_marker():
    """Headings produce [PAUSE] markers in v2."""
    text = "# Introduction\nSome text.\n## Details\nMore text."
    result = preprocess_for_tts(text)
    assert "[PAUSE]" in result
    assert "Introduction" in result
    assert "Details" in result


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
    """Bullet points converted to sentences with period ending."""
    text = "- First item\n- Second item\n* Third item"
    result = preprocess_for_tts(text)
    assert "First item." in result
    assert "Second item." in result
    assert "Third item." in result
    assert "- " not in result
    assert "* " not in result


def test_bullet_with_existing_period():
    """Bullets already ending in punctuation keep it."""
    text = "- Already has a period.\n- Ends with bang!"
    result = preprocess_for_tts(text)
    assert "Already has a period." in result
    assert "Ends with bang!" in result
    # Should NOT have double period
    assert ".." not in result


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


def test_expand_w_abbreviations():
    """w/ and w/o expanded."""
    text = "w/ caching and w/o locks"
    result = preprocess_for_tts(text)
    assert "with caching" in result
    assert "without locks" in result


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
    assert "[PAUSE]" in result


# ---------------------------------------------------------------------------
# chunk_text tests
# ---------------------------------------------------------------------------
def test_chunk_text_basic():
    """Basic text chunked at sentence boundaries."""
    text = "First sentence. Second sentence. Third sentence."
    chunks = chunk_text(text, max_chars=40)
    assert len(chunks) >= 2
    # Every sentence appears in some chunk
    full = " ".join(chunks)
    assert "First sentence." in full
    assert "Second sentence." in full
    assert "Third sentence." in full


def test_chunk_text_never_breaks_mid_sentence():
    """Chunks never break mid-sentence."""
    text = "Short. " * 20
    chunks = chunk_text(text.strip(), max_chars=30)
    for chunk in chunks:
        # Each chunk should end with a period (complete sentence)
        assert chunk.strip().endswith(".")


def test_chunk_text_long_sentence():
    """A single sentence longer than max_chars becomes its own chunk."""
    long_sentence = "A" * 600 + "."
    text = f"Short. {long_sentence} Also short."
    chunks = chunk_text(text, max_chars=500)
    assert any(long_sentence in c for c in chunks)


def test_chunk_text_empty():
    """Empty text returns empty list."""
    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_chunk_text_single_sentence():
    """Single sentence returns one chunk."""
    chunks = chunk_text("Hello world.", max_chars=500)
    assert len(chunks) == 1
    assert chunks[0] == "Hello world."


def test_chunk_text_respects_max_chars():
    """All chunks (except those with a single long sentence) respect max_chars."""
    sentences = ["This is sentence number one.", "Here is sentence number two.",
                 "And the third sentence here.", "Fourth one is also medium length.",
                 "Fifth sentence rounds it out."]
    text = " ".join(sentences)
    chunks = chunk_text(text, max_chars=80)
    for chunk in chunks:
        # Only single-sentence chunks can exceed max_chars
        sentence_count = len([s for s in chunk.split(". ") if s.strip()])
        if sentence_count > 1:
            assert len(chunk) <= 80


# ---------------------------------------------------------------------------
# compute_content_hash tests
# ---------------------------------------------------------------------------
def test_compute_content_hash_deterministic():
    """Same text produces same hash."""
    h1 = compute_content_hash("Hello world")
    h2 = compute_content_hash("Hello world")
    assert h1 == h2
    assert len(h1) == 64  # SHA-256 hex digest


def test_compute_content_hash_changes_on_text_change():
    """Different text produces different hash."""
    h1 = compute_content_hash("Version 1")
    h2 = compute_content_hash("Version 2")
    assert h1 != h2


# ---------------------------------------------------------------------------
# get_content_text tests
# ---------------------------------------------------------------------------
def test_get_content_text_framework_node(db_session):
    """Retrieves framework node description."""
    node = FrameworkNode(
        path="test.node",
        depth=0,
        title="Test Node",
        description="This is the node content.",
    )
    db_session.add(node)
    db_session.commit()
    db_session.refresh(node)

    text = get_content_text(db_session, CONTENT_TYPE_FRAMEWORK_NODE, node.id)
    assert text == "This is the node content."


def test_get_content_text_framework_node_fallback_to_title(db_session):
    """Falls back to title when description is empty."""
    node = FrameworkNode(
        path="test.notitle",
        depth=0,
        title="Just a Title",
        description=None,
    )
    db_session.add(node)
    db_session.commit()
    db_session.refresh(node)

    text = get_content_text(db_session, CONTENT_TYPE_FRAMEWORK_NODE, node.id)
    assert text == "Just a Title"


def test_get_content_text_prep_notes(db_session):
    """Retrieves company prep notes."""
    company = Company(name="TestCo", prep_notes="Study system design.")
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)

    text = get_content_text(db_session, CONTENT_TYPE_PREP_NOTES, company.id)
    assert text == "Study system design."


def test_get_content_text_prep_notes_none(db_session):
    """Returns None when company has no prep notes."""
    company = Company(name="EmptyCo")
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)

    text = get_content_text(db_session, CONTENT_TYPE_PREP_NOTES, company.id)
    assert text is None


def test_get_content_text_interview_question(db_session):
    """Retrieves problem as readable text."""
    problem = Problem(
        title="Two Sum",
        difficulty="easy",
        pattern="hash_map",
        category="algorithm",
        tags=json.dumps(["array", "hash"]),
    )
    db_session.add(problem)
    db_session.commit()
    db_session.refresh(problem)

    text = get_content_text(db_session, CONTENT_TYPE_INTERVIEW_QUESTION, problem.id)
    assert "Two Sum" in text
    assert "easy" in text
    assert "hash_map" in text
    assert "algorithm" in text
    assert "array" in text


def test_get_content_text_not_found(db_session):
    """Returns None for non-existent items."""
    assert get_content_text(db_session, CONTENT_TYPE_FRAMEWORK_NODE, 9999) is None
    assert get_content_text(db_session, CONTENT_TYPE_PREP_NOTES, 9999) is None
    assert get_content_text(db_session, CONTENT_TYPE_INTERVIEW_QUESTION, 9999) is None


def test_get_content_text_invalid_type(db_session):
    """Returns None for invalid content type."""
    assert get_content_text(db_session, "invalid_type", 1) is None


# ---------------------------------------------------------------------------
# get_reading_queue tests
# ---------------------------------------------------------------------------
def test_reading_queue_includes_framework_nodes(db_session):
    """Queue includes framework nodes with descriptions."""
    node = FrameworkNode(
        path="test.q1",
        depth=0,
        title="DP Basics",
        description="Dynamic programming fundamentals.",
        importance=1.0,
        progress_pct=0.0,
    )
    db_session.add(node)
    db_session.commit()

    queue = get_reading_queue(db_session)
    assert len(queue) == 1
    assert queue[0].content_type == CONTENT_TYPE_FRAMEWORK_NODE
    assert queue[0].title == "DP Basics"


def test_reading_queue_excludes_mastered(db_session):
    """Queue excludes mastered framework nodes."""
    node = FrameworkNode(
        path="test.mastered",
        depth=0,
        title="Mastered Topic",
        description="Already know this.",
        status="mastered",
    )
    db_session.add(node)
    db_session.commit()

    queue = get_reading_queue(db_session)
    assert len(queue) == 0


def test_reading_queue_excludes_nodes_without_description(db_session):
    """Queue excludes framework nodes with no description."""
    node = FrameworkNode(
        path="test.empty",
        depth=0,
        title="No Content",
        description=None,
    )
    db_session.add(node)
    db_session.commit()

    queue = get_reading_queue(db_session)
    assert len(queue) == 0


def test_reading_queue_sorted_by_urgency(db_session):
    """Queue items sorted by urgency descending."""
    high = FrameworkNode(
        path="test.high",
        depth=0,
        title="High Urgency",
        description="Important topic.",
        importance=2.0,
        progress_pct=0.0,
    )
    low = FrameworkNode(
        path="test.low",
        depth=0,
        title="Low Urgency",
        description="Less important.",
        importance=0.1,
        progress_pct=80.0,
    )
    db_session.add_all([high, low])
    db_session.commit()

    queue = get_reading_queue(db_session)
    assert len(queue) == 2
    assert queue[0].urgency >= queue[1].urgency
    assert queue[0].title == "High Urgency"


def test_reading_queue_includes_prep_notes(db_session):
    """Queue includes companies with prep notes."""
    company = Company(name="Google", prep_notes="Focus on system design.")
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)

    queue = get_reading_queue(db_session, company_ids=[company.id])
    prep_items = [q for q in queue if q.content_type == CONTENT_TYPE_PREP_NOTES]
    assert len(prep_items) == 1
    assert "Google" in prep_items[0].title


def test_reading_queue_includes_interview_questions(db_session):
    """Queue includes problems tagged to target companies."""
    company = Company(name="Google")
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)

    problem = Problem(
        title="Two Sum",
        difficulty="easy",
        pattern="hash_map",
        company_tags=json.dumps(["Google"]),
    )
    db_session.add(problem)
    db_session.commit()

    queue = get_reading_queue(db_session, company_ids=[company.id])
    iq_items = [q for q in queue if q.content_type == CONTENT_TYPE_INTERVIEW_QUESTION]
    assert len(iq_items) == 1
    assert iq_items[0].title == "Two Sum"


def test_reading_queue_excludes_completed(db_session):
    """Queue excludes items marked as completed in ReadingProgress."""
    node = FrameworkNode(
        path="test.done",
        depth=0,
        title="Done Topic",
        description="Already listened.",
        importance=1.0,
    )
    db_session.add(node)
    db_session.commit()
    db_session.refresh(node)

    progress = ReadingProgress(
        content_type=CONTENT_TYPE_FRAMEWORK_NODE,
        content_id=node.id,
        completed=True,
    )
    db_session.add(progress)
    db_session.commit()

    queue = get_reading_queue(db_session)
    assert len(queue) == 0


def test_reading_queue_attaches_progress(db_session):
    """Queue items have progress from ReadingProgress."""
    node = FrameworkNode(
        path="test.partial",
        depth=0,
        title="Partial",
        description="Partially listened.",
        importance=1.0,
    )
    db_session.add(node)
    db_session.commit()
    db_session.refresh(node)

    progress = ReadingProgress(
        content_type=CONTENT_TYPE_FRAMEWORK_NODE,
        content_id=node.id,
        last_chunk_index=3,
        char_offset=150,
        completed=False,
    )
    db_session.add(progress)
    db_session.commit()

    queue = get_reading_queue(db_session)
    assert len(queue) == 1
    assert queue[0].last_chunk_index == 3
    assert queue[0].char_offset == 150


def test_reading_queue_respects_limit(db_session):
    """Queue respects the limit parameter."""
    for i in range(10):
        db_session.add(FrameworkNode(
            path=f"test.limit.{i}",
            depth=0,
            title=f"Topic {i}",
            description=f"Content {i}",
            importance=1.0,
        ))
    db_session.commit()

    queue = get_reading_queue(db_session, limit=3)
    assert len(queue) == 3


def test_reading_queue_urgency_increases_near_interview(db_session):
    """Items have higher urgency with fewer days until interview."""
    node = FrameworkNode(
        path="test.urgent",
        depth=0,
        title="Urgent Node",
        description="Content here.",
        importance=1.0,
        progress_pct=0.0,
    )
    db_session.add(node)
    db_session.commit()

    queue_far = get_reading_queue(db_session, days_until_interview=30)
    queue_near = get_reading_queue(db_session, days_until_interview=1)

    assert queue_near[0].urgency > queue_far[0].urgency


def test_reading_queue_all_three_types(db_session):
    """Queue interleaves all three content types."""
    node = FrameworkNode(
        path="test.all3",
        depth=0,
        title="Node",
        description="Framework content.",
        importance=1.0,
    )
    company = Company(name="Meta", prep_notes="Prep for Meta.")
    db_session.add_all([node, company])
    db_session.commit()
    db_session.refresh(company)

    problem = Problem(
        title="LRU Cache",
        difficulty="medium",
        pattern="design",
        company_tags=json.dumps(["Meta"]),
    )
    db_session.add(problem)
    db_session.commit()

    queue = get_reading_queue(db_session, company_ids=[company.id])
    types_in_queue = {q.content_type for q in queue}
    assert CONTENT_TYPE_FRAMEWORK_NODE in types_in_queue
    assert CONTENT_TYPE_PREP_NOTES in types_in_queue
    assert CONTENT_TYPE_INTERVIEW_QUESTION in types_in_queue
