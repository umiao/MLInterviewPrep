"""Content preprocessing pipeline for TTS synthesis.

Converts markdown/structured text into clean spoken-word text suitable
for text-to-speech engines. Provides queue ranking, chunking, and
content retrieval for the reading/radio feature.
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from src.backend.models.company import Company, CompanyTopicWeight
from src.backend.models.framework import FrameworkNode
from src.backend.models.problem import Problem
from src.backend.models.reading import ReadingProgress, Transcript
from src.backend.models.timeline import InterviewEvent
from src.backend.services.study_planner import compute_urgency

logger = logging.getLogger(__name__)

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


@dataclass
class InterviewContext:
    """Upcoming interview context derived from interview_events."""

    company_ids: list[int] = field(default_factory=list)
    days_until_soonest: int = 30
    imminent_company_ids: list[int] = field(default_factory=list)


def get_interview_context(
    db: Session,
    now: datetime | None = None,
) -> InterviewContext:
    """Query upcoming interviews and derive scheduling context.

    Args:
        db: Database session.
        now: Current datetime (default: utcnow). Accepts both naive and
            timezone-aware datetimes.

    Returns:
        InterviewContext with company_ids, days until soonest, and
        imminent (< 3 days) company_ids.
    """
    if now is None:
        now = datetime.now(UTC)

    # Ensure now is timezone-aware for comparison
    if now.tzinfo is None:
        now = now.replace(tzinfo=UTC)

    upcoming = (
        db.query(InterviewEvent)
        .filter(
            InterviewEvent.status == "upcoming",
            InterviewEvent.scheduled_at > now,
        )
        .order_by(InterviewEvent.scheduled_at.asc())
        .all()
    )

    if not upcoming:
        return InterviewContext()

    ctx = InterviewContext()
    seen_ids: set[int] = set()

    for event in upcoming:
        if event.company_id and event.company_id not in seen_ids:
            ctx.company_ids.append(event.company_id)
            seen_ids.add(event.company_id)

    # Days until soonest interview
    soonest = upcoming[0]
    sched = soonest.scheduled_at
    if sched.tzinfo is None:
        sched = sched.replace(tzinfo=UTC)
    delta = (sched - now).total_seconds() / 86400.0
    ctx.days_until_soonest = max(1, int(delta))

    # Imminent: interviews within 3 days
    for event in upcoming:
        sched = event.scheduled_at
        if sched.tzinfo is None:
            sched = sched.replace(tzinfo=UTC)
        days_away = (sched - now).total_seconds() / 86400.0
        if days_away < 3 and event.company_id and event.company_id not in set(ctx.imminent_company_ids):
            ctx.imminent_company_ids.append(event.company_id)

    return ctx


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
        if problem.description:
            parts.append(f"\n{problem.description}")
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
# preprocess_for_tts (v3)
# ---------------------------------------------------------------------------
def _is_cjk_char(ch: str) -> bool:
    """Return True if ch is a CJK Unified Ideograph.

    Args:
        ch: A single character.

    Returns:
        True if the character is CJK.
    """
    cp = ord(ch)
    return (
        0x4E00 <= cp <= 0x9FFF
        or 0x3400 <= cp <= 0x4DBF
        or 0x20000 <= cp <= 0x2A6DF
        or 0x2A700 <= cp <= 0x2B73F
        or 0xF900 <= cp <= 0xFAFF
    )


def _cjk_ratio(line: str) -> float:
    """Return fraction of non-whitespace characters that are CJK.

    Args:
        line: Text line to check.

    Returns:
        Float between 0.0 and 1.0.
    """
    chars = [ch for ch in line if not ch.isspace()]
    if not chars:
        return 0.0
    return sum(1 for ch in chars if _is_cjk_char(ch)) / len(chars)


def preprocess_for_tts(text: str) -> str:
    """Convert markdown text to plain spoken-word text for TTS.

    Transformations (v3):
    - Strip markdown headings (#, ##, etc.) but keep the text, add natural pause
    - Remove bold/italic markers (**, *, __, _)
    - Remove markdown links, keep link text
    - Skip code blocks (``` ... ```)
    - Remove inline code backticks
    - Convert bullet points to sentences (ensure period ending)
    - Convert checkboxes (- [x], - [ ]) to spoken text
    - Strip table syntax into readable text
    - Remove horizontal rules (---, ***, ___)
    - Remove underscore placeholders (_____)
    - Skip CJK-only lines (>80% CJK characters)
    - Expand common abbreviations (e.g., i.e.)
    - Collapse multiple blank lines

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

        # Horizontal rules: lines of only -, *, or _ (3+)
        if re.match(r"^[-*_]{3,}$", stripped):
            result_lines.append("")
            continue

        # Table divider lines: |---|---|
        if re.match(r"^\|[-:| ]+\|$", stripped):
            continue

        # Table data rows: | cell | cell |
        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            cells = [c for c in cells if c]
            if cells:
                stripped = ", ".join(cells) + "."
            else:
                continue

        # Strip heading markers and add natural pause (empty line)
        if stripped.startswith("#"):
            stripped = re.sub(r"^#{1,6}\s*", "", stripped)
            if stripped:
                result_lines.append("")
                result_lines.append(stripped)
            continue

        # Remove markdown links [text](url) -> text
        stripped = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", stripped)

        # Remove bold/italic markers
        stripped = re.sub(r"\*{1,3}([^*]+)\*{1,3}", r"\1", stripped)
        stripped = re.sub(r"_{1,3}([^_]+)_{1,3}", r"\1", stripped)

        # Remove inline code backticks
        stripped = re.sub(r"`([^`]+)`", r"\1", stripped)

        # Remove underscore placeholders (5+ underscores)
        stripped = re.sub(r"_{5,}", "", stripped)

        # Checkboxes: - [x] text -> "Completed: text." / - [ ] text -> "To do: text."
        checkbox_checked = re.match(r"^[-*+]\s+\[x\]\s+(.*)", stripped, re.IGNORECASE)
        checkbox_unchecked = re.match(r"^[-*+]\s+\[ \]\s+(.*)", stripped)
        if checkbox_checked:
            sentence = checkbox_checked.group(1).strip()
            if sentence and sentence[-1] not in ".!?":
                sentence += "."
            stripped = f"Completed: {sentence}"
        elif checkbox_unchecked:
            sentence = checkbox_unchecked.group(1).strip()
            if sentence and sentence[-1] not in ".!?":
                sentence += "."
            stripped = f"To do: {sentence}"
        else:
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

        # Skip CJK-only lines (>80% CJK characters)
        if stripped and _cjk_ratio(stripped) > 0.8:
            logger.debug("Skipping CJK-dominant line: %.50s...", stripped)
            continue

        result_lines.append(stripped)

    text = "\n".join(result_lines)

    # Expand common abbreviations
    text = re.sub(r"\be\.g\.\s*", "for example, ", text)
    text = re.sub(r"\bi\.e\.\s*", "that is, ", text)
    text = re.sub(r"\betc\.", "et cetera.", text)
    text = re.sub(r"\bvs\.\s*", "versus ", text)
    text = re.sub(r"\bw/\s", "with ", text)
    text = re.sub(r"\bw/o\s", "without ", text)

    # Expand technical abbreviations for TTS
    text = re.sub(r"\bML\b", "machine learning", text)
    text = re.sub(r"\bDL\b", "deep learning", text)
    text = re.sub(r"\bNLP\b", "natural language processing", text)
    text = re.sub(r"\bCV\b", "computer vision", text)
    text = re.sub(r"\bAPI\b", "A P I", text)
    text = re.sub(r"\bSQL\b", "S Q L", text)
    text = re.sub(r"\bLLM\b", "L L M", text)
    # Big-O notation: O(n) -> O of n
    text = re.sub(r"O\(([^)]+)\)", r"O of \1", text)

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
    now: datetime | None = None,
) -> list[QueueItem]:
    """Build a ranked reading queue from all content types.

    Automatically queries upcoming interview events to determine which
    companies to prioritize and how urgently. When an interview is < 3
    days away, that company's prep_notes are boosted to the top.

    Falls back to standard urgency-based ordering when no upcoming
    interviews exist and no company_ids are provided.

    Args:
        db: Database session.
        company_ids: Optional list of company IDs to prioritize.
            When None, auto-detects from upcoming interview events.
        days_until_interview: Days until next interview for urgency calc.
            When interview context is auto-detected, this is overridden.
        limit: Maximum queue items to return.
        now: Current datetime for interview context (default: utcnow).

    Returns:
        Sorted list of QueueItem objects, highest urgency first.
    """
    # --- Auto-detect interview context ---
    interview_ctx = get_interview_context(db, now=now)
    imminent_ids: set[int] = set(interview_ctx.imminent_company_ids)

    if company_ids is None and interview_ctx.company_ids:
        # Auto-populate from upcoming interviews
        company_ids = interview_ctx.company_ids
        days_until_interview = interview_ctx.days_until_soonest
    elif company_ids is None:
        company_ids = []

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

        # Imminent interview boost: prep_notes for < 3 day interviews
        # get a massive boost to ensure they appear first
        if company.id in imminent_ids:
            urgency *= 100.0

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

    # Split pending vs completed; pending capped by limit, completed always returned
    pending = [i for i in items if not i.completed]
    completed = [i for i in items if i.completed]
    pending.sort(key=lambda x: x.urgency, reverse=True)
    pending = pending[:limit]
    completed.sort(key=lambda x: x.urgency, reverse=True)

    return pending + completed


# ---------------------------------------------------------------------------
# Transcript generation via LLM (replaces TTS summary)
# ---------------------------------------------------------------------------

# Current prompt version -- bump when prompt changes to invalidate cache
TRANSCRIPT_PROMPT_VERSION = 1

TRANSCRIPT_SYSTEM_PROMPT = (
    "You are a faithful text-to-speech transcript adapter. "
    "Transform written study material into clean spoken-word text, "
    "preserving all key points and optimizing for spoken delivery.\n\n"
    "Rules:\n"
    "- Preserve all factual claims, definitions, formulas, and key points. "
    "Do NOT over-summarize or drop technical details.\n"
    "- For structured data (tables, key-value pairs), convert to "
    "question-answer format when it aids listening comprehension. "
    "For narrative content, keep the natural flow.\n"
    "- Remove formatting artifacts: markdown syntax, table borders, "
    "code block markers, URLs, checkbox syntax, placeholder underscores.\n"
    "- Expand abbreviations (e.g. -> for example, ML -> machine learning, "
    "O(n) -> O of n).\n"
    "- Convert bullet lists into flowing sentences, preserving every point.\n"
    "- If content contains Chinese text, translate it accurately to English.\n"
    "- Do NOT add opinions, commentary, or filler phrases.\n"
    "- Do not drop technical details or skip sections.\n"
    "- Output ONLY the adapted text, no preamble or explanation."
)

# Deprecated: kept for backward compatibility with existing cached data
TTS_SUMMARY_SYSTEM_PROMPT = TRANSCRIPT_SYSTEM_PROMPT


@dataclass
class TranscriptResult:
    """Result of transcript generation."""

    transcript_text: str
    transcript_hash: str
    generation_method: str  # "llm" or "preprocess_fallback"
    from_cache: bool


async def generate_transcript(
    db: Session,
    content_type: str,
    content_id: int,
) -> TranscriptResult | None:
    """Generate a faithful spoken-word transcript for a content item.

    Checks the Transcript cache first (matching source_hash + prompt_version
    + is_latest=True). On cache miss, generates via LLM with fallback to
    preprocess_for_tts(). The is_latest toggle is wrapped in a single
    transaction to prevent zero-latest queries mid-operation.

    Args:
        db: Database session.
        content_type: One of the VALID_CONTENT_TYPES.
        content_id: Primary key of the content item.

    Returns:
        TranscriptResult with text and metadata, or None if content not found.
    """
    raw_text = get_content_text(db, content_type, content_id)
    if raw_text is None:
        return None

    source_hash = compute_content_hash(raw_text)

    # Check cache: is_latest=True + matching prompt_version
    cached = (
        db.query(Transcript)
        .filter(
            Transcript.content_type == content_type,
            Transcript.content_id == content_id,
            Transcript.is_latest.is_(True),
            Transcript.prompt_version == TRANSCRIPT_PROMPT_VERSION,
        )
        .first()
    )

    if cached and cached.source_hash == source_hash:
        return TranscriptResult(
            transcript_text=cached.transcript_text,
            transcript_hash=cached.transcript_hash,
            generation_method=cached.generation_method,
            from_cache=True,
        )

    # Generate new transcript
    generation_method = "llm"
    transcript_text: str | None = None

    try:
        from src.backend.services.llm_service import LLMService

        llm = LLMService()
        result = await llm.chat(
            system_prompt=TRANSCRIPT_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": raw_text}],
            response_format="text",
            max_tokens=4096,
        )

        if isinstance(result, dict) and "error" in result:
            logger.warning(
                "LLM transcript generation failed for %s/%s: %s",
                content_type, content_id, result["error"],
            )
            transcript_text = None
        else:
            transcript_text = str(result).strip() or None

    except Exception:
        logger.exception(
            "LLM unavailable for transcript generation (%s/%s), falling back",
            content_type, content_id,
        )

    # Fallback to preprocess_for_tts
    if not transcript_text:
        transcript_text = preprocess_for_tts(raw_text)
        generation_method = "preprocess_fallback"

    transcript_hash = compute_content_hash(transcript_text)

    # Single transaction: mark old as not latest, insert new as latest
    old_latest = (
        db.query(Transcript)
        .filter(
            Transcript.content_type == content_type,
            Transcript.content_id == content_id,
            Transcript.is_latest.is_(True),
        )
        .all()
    )
    for old in old_latest:
        old.is_latest = False

    new_entry = Transcript(
        content_type=content_type,
        content_id=content_id,
        source_hash=source_hash,
        transcript_text=transcript_text,
        transcript_hash=transcript_hash,
        generation_method=generation_method,
        prompt_version=TRANSCRIPT_PROMPT_VERSION,
        is_latest=True,
    )
    db.add(new_entry)
    db.commit()

    return TranscriptResult(
        transcript_text=transcript_text,
        transcript_hash=transcript_hash,
        generation_method=generation_method,
        from_cache=False,
    )


async def get_or_create_transcript(
    db: Session,
    content_type: str,
    content_id: int,
) -> TranscriptResult | None:
    """Public API: get cached transcript or generate on demand.

    Args:
        db: Database session.
        content_type: One of the VALID_CONTENT_TYPES.
        content_id: Primary key of the content item.

    Returns:
        TranscriptResult, or None if content not found.
    """
    return await generate_transcript(db, content_type, content_id)


def get_cached_transcript(
    db: Session,
    content_type: str,
    content_id: int,
) -> TranscriptResult | None:
    """Return cached transcript if it exists and is current.

    Does NOT call the LLM. Returns None if no valid cache exists.

    Args:
        db: Database session.
        content_type: One of the VALID_CONTENT_TYPES.
        content_id: Primary key of the content item.

    Returns:
        Cached TranscriptResult, or None if not available or stale.
    """
    raw_text = get_content_text(db, content_type, content_id)
    if raw_text is None:
        return None

    source_hash = compute_content_hash(raw_text)

    cached = (
        db.query(Transcript)
        .filter(
            Transcript.content_type == content_type,
            Transcript.content_id == content_id,
            Transcript.is_latest.is_(True),
            Transcript.prompt_version == TRANSCRIPT_PROMPT_VERSION,
        )
        .first()
    )

    if cached and cached.source_hash == source_hash:
        return TranscriptResult(
            transcript_text=cached.transcript_text,
            transcript_hash=cached.transcript_hash,
            generation_method=cached.generation_method,
            from_cache=True,
        )

    return None


# ---------------------------------------------------------------------------
# Deprecated wrappers (kept for backward compatibility)
# ---------------------------------------------------------------------------
async def generate_tts_summary(
    db: Session,
    content_type: str,
    content_id: int,
) -> str | None:
    """Deprecated: Use generate_transcript() instead.

    Args:
        db: Database session.
        content_type: One of the VALID_CONTENT_TYPES.
        content_id: Primary key of the content item.

    Returns:
        Transcript text, or None if content not found.
    """
    result = await generate_transcript(db, content_type, content_id)
    return result.transcript_text if result else None


def get_cached_summary(
    db: Session,
    content_type: str,
    content_id: int,
) -> str | None:
    """Deprecated: Use get_cached_transcript() instead.

    Args:
        db: Database session.
        content_type: One of the VALID_CONTENT_TYPES.
        content_id: Primary key of the content item.

    Returns:
        Cached transcript text, or None if not available.
    """
    result = get_cached_transcript(db, content_type, content_id)
    return result.transcript_text if result else None


# ---------------------------------------------------------------------------
# Neetcode slug utility (Task 3)
# ---------------------------------------------------------------------------
def title_to_neetcode_slug(title: str) -> str:
    """Convert a problem title to a neetcode.io URL slug.

    Lowercase, spaces to hyphens, strip non-alphanumeric (except hyphens).

    Args:
        title: Problem title string.

    Returns:
        URL-safe slug for neetcode.io.
    """
    slug = title.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s]+", "-", slug)
    slug = re.sub(r"-{2,}", "-", slug)
    return slug.strip("-")
