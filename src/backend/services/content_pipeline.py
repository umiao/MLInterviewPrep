"""Content preprocessing pipeline for TTS synthesis.

Converts markdown/structured text into clean spoken-word text suitable
for text-to-speech engines. Provides queue ranking, chunking, and
content retrieval for the reading/radio feature.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass

from sqlalchemy.orm import Session

from src.backend.models.company import Company, CompanyTopicWeight
from src.backend.models.framework import FrameworkNode
from src.backend.models.problem import Problem
from src.backend.models.reading import ReadingProgress
from src.backend.services.study_planner import compute_urgency

# ---------------------------------------------------------------------------
# Content types
# ---------------------------------------------------------------------------
CONTENT_TYPE_FRAMEWORK_NODE = "framework_node"
CONTENT_TYPE_PREP_NOTES = "prep_notes"
CONTENT_TYPE_INTERVIEW_QUESTION = "interview_question"

VALID_CONTENT_TYPES = {
    CONTENT_TYPE_FRAMEWORK_NODE,
    CONTENT_TYPE_PREP_NOTES,
    CONTENT_TYPE_INTERVIEW_QUESTION,
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------
@dataclass
class QueueItem:
    """A single item in the reading queue."""

    content_type: str
    content_id: int
    title: str
    urgency: float
    total_chars: int
    last_chunk_index: int = 0
    char_offset: int = 0
    completed: bool = False


# ---------------------------------------------------------------------------
# get_content_text
# ---------------------------------------------------------------------------
def get_content_text(db: Session, content_type: str, content_id: int) -> str | None:
    """Return raw text for a content item, or None if not found.

    Args:
        db: Database session.
        content_type: One of the VALID_CONTENT_TYPES.
        content_id: Primary key of the content item.

    Returns:
        The raw text content, or None if the item does not exist.
    """
    if content_type == CONTENT_TYPE_FRAMEWORK_NODE:
        node = db.get(FrameworkNode, content_id)
        if node is None:
            return None
        # Use description; fall back to title if no description
        return node.description or node.title

    if content_type == CONTENT_TYPE_PREP_NOTES:
        company = db.get(Company, content_id)
        if company is None:
            return None
        return company.prep_notes or None

    if content_type == CONTENT_TYPE_INTERVIEW_QUESTION:
        problem = db.get(Problem, content_id)
        if problem is None:
            return None
        # Build a readable text from problem fields
        parts: list[str] = [problem.title]
        if problem.difficulty:
            parts.append(f"Difficulty: {problem.difficulty}.")
        if problem.pattern:
            parts.append(f"Pattern: {problem.pattern}.")
        if problem.category:
            label = problem.category.replace("_", " ")
            parts.append(f"Category: {label}.")
        if problem.tags:
            try:
                tag_list = json.loads(problem.tags)
                if tag_list:
                    parts.append(f"Tags: {', '.join(tag_list)}.")
            except (json.JSONDecodeError, TypeError):
                pass
        return " ".join(parts)

    return None


# ---------------------------------------------------------------------------
# compute_content_hash
# ---------------------------------------------------------------------------
def compute_content_hash(text: str) -> str:
    """Compute SHA-256 hash of content text for cache invalidation.

    Args:
        text: The content text.

    Returns:
        Hex-encoded SHA-256 digest.
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# preprocess_for_tts (v2)
# ---------------------------------------------------------------------------
def preprocess_for_tts(text: str) -> str:
    """Convert markdown text to plain spoken-word text for TTS.

    Transformations (v2):
    - Strip markdown headings (#, ##, etc.) but keep the text, add [PAUSE]
    - Remove bold/italic markers (**, *, __, _)
    - Remove markdown links, keep link text
    - Skip code blocks (``` ... ```)
    - Remove inline code backticks
    - Convert bullet points to sentences (ensure period ending)
    - Expand common abbreviations (e.g., i.e.)
    - Collapse multiple blank lines
    - Add [PAUSE] markers at heading boundaries

    Args:
        text: Raw markdown text.

    Returns:
        Cleaned text suitable for TTS synthesis.
    """
    if not text:
        return ""

    lines = text.split("\n")
    result_lines: list[str] = []
    in_code_block = False

    for line in lines:
        stripped = line.strip()

        # Toggle code block state
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue

        # Skip code block contents
        if in_code_block:
            continue

        # Strip heading markers and add [PAUSE]
        if stripped.startswith("#"):
            stripped = re.sub(r"^#{1,6}\s*", "", stripped)
            if stripped:
                result_lines.append("[PAUSE]")
                result_lines.append(stripped)
            continue

        # Remove markdown links [text](url) -> text
        stripped = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", stripped)

        # Remove bold/italic markers
        stripped = re.sub(r"\*{1,3}([^*]+)\*{1,3}", r"\1", stripped)
        stripped = re.sub(r"_{1,3}([^_]+)_{1,3}", r"\1", stripped)

        # Remove inline code backticks
        stripped = re.sub(r"`([^`]+)`", r"\1", stripped)

        # Convert bullet points to plain sentences
        bullet_match = re.match(r"^[-*+]\s+(.*)", stripped)
        if bullet_match:
            sentence = bullet_match.group(1).strip()
            # Ensure ends with period
            if sentence and sentence[-1] not in ".!?":
                sentence += "."
            stripped = sentence

        # Numbered lists
        num_match = re.match(r"^\d+\.\s+(.*)", stripped)
        if num_match:
            sentence = num_match.group(1).strip()
            if sentence and sentence[-1] not in ".!?":
                sentence += "."
            stripped = sentence

        result_lines.append(stripped)

    text = "\n".join(result_lines)

    # Expand common abbreviations
    text = re.sub(r"\be\.g\.\s*", "for example, ", text)
    text = re.sub(r"\bi\.e\.\s*", "that is, ", text)
    text = re.sub(r"\betc\.", "et cetera.", text)
    text = re.sub(r"\bvs\.\s*", "versus ", text)
    text = re.sub(r"\bw/\s", "with ", text)
    text = re.sub(r"\bw/o\s", "without ", text)

    # Collapse multiple blank lines to single
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# ---------------------------------------------------------------------------
# chunk_text
# ---------------------------------------------------------------------------
def chunk_text(text: str, max_chars: int = 500) -> list[str]:
    """Split text into chunks at sentence boundaries.

    Never breaks mid-sentence. If a single sentence exceeds max_chars,
    it becomes its own chunk.

    Args:
        text: The preprocessed text to chunk.
        max_chars: Maximum characters per chunk.

    Returns:
        List of text chunks.
    """
    if not text:
        return []

    # Split into sentences using regex (handles ., !, ?)
    # Keep the delimiter attached to the sentence
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    # Filter empty strings
    sentences = [s for s in sentences if s.strip()]

    if not sentences:
        return [text.strip()] if text.strip() else []

    chunks: list[str] = []
    current_chunk: list[str] = []
    current_len = 0

    for sentence in sentences:
        sentence_len = len(sentence)

        # If adding this sentence would exceed max_chars and we have content
        if current_len + sentence_len + (1 if current_chunk else 0) > max_chars and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]
            current_len = sentence_len
        else:
            current_chunk.append(sentence)
            current_len += sentence_len + (1 if len(current_chunk) > 1 else 0)

    # Don't forget the last chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


# ---------------------------------------------------------------------------
# get_reading_queue
# ---------------------------------------------------------------------------
def get_reading_queue(
    db: Session,
    company_ids: list[int] | None = None,
    days_until_interview: int = 30,
    limit: int = 20,
) -> list[QueueItem]:
    """Build a ranked reading queue from all content types.

    Ranks FrameworkNodes by urgency (reusing compute_urgency from
    study_planner), then interleaves prep_notes and interview_questions
    for target companies.

    Args:
        db: Database session.
        company_ids: Optional list of company IDs to prioritize.
        days_until_interview: Days until next interview for urgency calc.
        limit: Maximum queue items to return.

    Returns:
        Sorted list of QueueItem objects, highest urgency first.
    """
    company_ids = company_ids or []
    items: list[QueueItem] = []

    # --- Framework nodes (not mastered, with content) ---
    nodes = (
        db.query(FrameworkNode)
        .filter(FrameworkNode.status != "mastered")
        .filter(FrameworkNode.description.isnot(None))
        .filter(FrameworkNode.description != "")
        .all()
    )

    # Build company weight map
    company_weights: dict[int, float] = {}
    if company_ids:
        weight_rows = (
            db.query(CompanyTopicWeight)
            .filter(CompanyTopicWeight.company_id.in_(company_ids))
            .all()
        )
        for w in weight_rows:
            company_weights[w.framework_node_id] = max(
                company_weights.get(w.framework_node_id, 0), w.weight
            )

    for node in nodes:
        urgency = compute_urgency(
            node.importance,
            node.progress_pct,
            node.last_studied_at,
            days_until_interview,
        )
        if company_ids and node.id in company_weights:
            urgency *= company_weights[node.id]

        items.append(QueueItem(
            content_type=CONTENT_TYPE_FRAMEWORK_NODE,
            content_id=node.id,
            title=node.title,
            urgency=urgency,
            total_chars=len(node.description or ""),
        ))

    # --- Prep notes from target companies ---
    if company_ids:
        companies = (
            db.query(Company)
            .filter(Company.id.in_(company_ids))
            .filter(Company.prep_notes.isnot(None))
            .filter(Company.prep_notes != "")
            .all()
        )
    else:
        companies = (
            db.query(Company)
            .filter(Company.prep_notes.isnot(None))
            .filter(Company.prep_notes != "")
            .all()
        )

    for company in companies:
        # Prep notes get a boost for target companies
        urgency = 2.0 if company.id in (company_ids or []) else 1.0
        urgency *= max(1.0, 30 / max(1, days_until_interview))

        items.append(QueueItem(
            content_type=CONTENT_TYPE_PREP_NOTES,
            content_id=company.id,
            title=f"{company.name} - Prep Notes",
            urgency=urgency,
            total_chars=len(company.prep_notes or ""),
        ))

    # --- Interview questions (problems) for target companies ---
    if company_ids:
        # Get company names for matching company_tags
        target_names = (
            db.query(Company.name)
            .filter(Company.id.in_(company_ids))
            .all()
        )
        target_name_set = {n[0].lower() for n in target_names}

        problems = db.query(Problem).filter(Problem.company_tags.isnot(None)).all()
        for problem in problems:
            try:
                tags = json.loads(problem.company_tags) if problem.company_tags else []
            except (json.JSONDecodeError, TypeError):
                tags = []
            tag_lower = {t.lower() for t in tags}
            if tag_lower & target_name_set:
                urgency = 1.5 * max(1.0, 30 / max(1, days_until_interview))
                text = get_content_text(db, CONTENT_TYPE_INTERVIEW_QUESTION, problem.id)
                items.append(QueueItem(
                    content_type=CONTENT_TYPE_INTERVIEW_QUESTION,
                    content_id=problem.id,
                    title=problem.title,
                    urgency=urgency,
                    total_chars=len(text or ""),
                ))

    # --- Attach reading progress ---
    progress_map: dict[tuple[str, int], ReadingProgress] = {}
    if items:
        progress_rows = db.query(ReadingProgress).all()
        for p in progress_rows:
            progress_map[(p.content_type, p.content_id)] = p

    for item in items:
        key = (item.content_type, item.content_id)
        if key in progress_map:
            prog = progress_map[key]
            item.last_chunk_index = prog.last_chunk_index or 0
            item.char_offset = prog.char_offset or 0
            item.completed = prog.completed or False

    # Filter out completed items
    items = [i for i in items if not i.completed]

    # Sort by urgency descending
    items.sort(key=lambda x: x.urgency, reverse=True)

    return items[:limit]
