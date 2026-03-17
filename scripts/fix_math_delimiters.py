"""Convert $...$ inline math to $$...$$ in seed content files.

Usage:
    python scripts/fix_math_delimiters.py

Processes all scripts/seed_pillar*_content.py files in-place.
Skips fenced code blocks, inline code spans, and currency patterns.
Idempotent -- already-doubled $$...$$ is not modified.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEED_FILES = sorted(ROOT.glob("scripts/seed_pillar*_content.py"))

# Match single-dollar inline math: $content$
# Negative lookarounds prevent matching display math $$...$$
# Content must not start or end with whitespace
INLINE_MATH_RE = re.compile(
    r"(?<!\$)\$(?!\$)"  # opening $ not adjacent to another $
    r"("
    r"[^\s$][^$\n]*?[^\s$]"  # 2+ chars, no leading/trailing whitespace
    r"|"
    r"[^\s$]"  # single non-space, non-$ char
    r")"
    r"\$(?!\$)"  # closing $ not followed by $
)

CURRENCY_RE = re.compile(r"^\d[\d,.]*\s*[KkMmBb]\s*[-]?\s*$")


def is_currency(content: str) -> bool:
    """Return True if content between $ delimiters looks like currency."""
    if not content or not content[0].isdigit():
        return False
    # LaTeX commands / math operators -> definitely math, not currency
    if any(c in content for c in "\\{}_^"):
        return False
    return bool(CURRENCY_RE.match(content))


def convert_line(line: str) -> tuple[str, int]:
    """Convert $...$ to $$...$$ in a single line, protecting inline code.

    Returns (converted_line, number_of_conversions).
    """
    # Protect inline code spans from modification
    code_spans: list[str] = []

    def save_code(m: re.Match[str]) -> str:
        code_spans.append(m.group(0))
        return f"\x00CODE{len(code_spans) - 1}\x00"

    protected = re.sub(r"`[^`]+`", save_code, line)

    count = 0

    def replace_math(m: re.Match[str]) -> str:
        nonlocal count
        content = m.group(1)
        if is_currency(content):
            return m.group(0)  # leave currency unchanged
        count += 1
        return f"$${content}$$"

    converted = INLINE_MATH_RE.sub(replace_math, protected)

    # Restore inline code spans
    for i, code in enumerate(code_spans):
        converted = converted.replace(f"\x00CODE{i}\x00", code)

    return converted, count


def process_file(filepath: Path) -> int:
    """Process a seed file in-place. Returns number of conversions."""
    text = filepath.read_text(encoding="utf-8")
    lines = text.split("\n")
    in_code_block = False
    total = 0

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        new_line, count = convert_line(line)
        if count > 0:
            lines[i] = new_line
            total += count

    if total > 0:
        filepath.write_text("\n".join(lines), encoding="utf-8")

    return total


def main() -> None:
    """Process all seed content files."""
    if not SEED_FILES:
        print("No seed files found.")
        sys.exit(1)

    total = 0
    for f in SEED_FILES:
        count = process_file(f)
        print(f"  {f.name}: {count} conversions")
        total += count
    print(f"\nTotal: {total} conversions across {len(SEED_FILES)} files")


if __name__ == "__main__":
    main()
