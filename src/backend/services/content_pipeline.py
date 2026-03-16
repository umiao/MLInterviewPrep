"""Content preprocessing pipeline for TTS synthesis.

Converts markdown/structured text into clean spoken-word text suitable
for text-to-speech engines.
"""
from __future__ import annotations

import re


def preprocess_for_tts(text: str) -> str:
    """Convert markdown text to plain spoken-word text for TTS.

    Transformations (v1):
    - Strip markdown headings (#, ##, etc.) but keep the text
    - Remove bold/italic markers (**, *, __, _)
    - Remove markdown links, keep link text
    - Skip code blocks (``` ... ```)
    - Remove inline code backticks
    - Convert bullet points to sentences
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

        # Strip heading markers
        if stripped.startswith("#"):
            stripped = re.sub(r"^#{1,6}\s*", "", stripped)

        # Remove markdown links [text](url) -> text
        stripped = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", stripped)

        # Remove bold/italic markers
        stripped = re.sub(r"\*{1,3}([^*]+)\*{1,3}", r"\1", stripped)
        stripped = re.sub(r"_{1,3}([^_]+)_{1,3}", r"\1", stripped)

        # Remove inline code backticks
        stripped = re.sub(r"`([^`]+)`", r"\1", stripped)

        # Convert bullet points to plain sentences
        stripped = re.sub(r"^[-*+]\s+", "", stripped)
        # Numbered lists
        stripped = re.sub(r"^\d+\.\s+", "", stripped)

        result_lines.append(stripped)

    text = "\n".join(result_lines)

    # Expand common abbreviations
    text = re.sub(r"\be\.g\.", "for example", text)
    text = re.sub(r"\bi\.e\.", "that is", text)
    text = re.sub(r"\betc\.", "et cetera", text)
    text = re.sub(r"\bvs\.", "versus", text)

    # Collapse multiple blank lines to single
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()
