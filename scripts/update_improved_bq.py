"""Update behavioral_examples with improved story data from bq_improved_stories.md.

Parses the improved stories markdown and updates all matching records in
behavioral_examples with:
  - situation (1-sentence)
  - action (bullet points)
  - result (impact-driven)
  - risk_statement
  - analogy
  - tech_terms (JSON dict)

Usage:
    python scripts/update_improved_bq.py              # dry-run (default)
    python scripts/update_improved_bq.py --apply       # actually write to DB
"""

import argparse
import json
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "mle_prep.db"
STORIES_PATH = PROJECT_ROOT / "docs" / "bq_improved_stories.md"
BACKUP_SCRIPT = PROJECT_ROOT.parent / "scripts" / "db_backup.py"


# ---------------------------------------------------------------------------
# Markdown parser
# ---------------------------------------------------------------------------

def parse_stories(md_path: Path) -> list[dict]:
    """Parse bq_improved_stories.md and extract per-story fields.

    Args:
        md_path: Path to the improved stories markdown file.

    Returns:
        List of dicts, each containing example_id and updated fields.
    """
    text = md_path.read_text(encoding="utf-8")

    stories = []

    # More robust: split by story boundaries
    # Find all story section starts
    headers = list(re.finditer(
        r"^#{2,3}\s+(?:STORY\s+\d+:.+|COL-\d+:.+|EXISTING\s+ANSWERS.+)",
        text,
        re.MULTILINE,
    ))

    for i, match in enumerate(headers):
        header_line = match.group(0)

        # Skip the "EXISTING ANSWERS" meta-header
        if "EXISTING ANSWERS" in header_line:
            continue

        # Extract example_id from header
        ex_match = re.search(r"\((EX-\d+)(?:\s*/\s*Story\s+\w)?\)", header_line)
        col_match = re.search(r"(COL-\d+):", header_line)

        if ex_match:
            example_id = ex_match.group(1)
        elif col_match:
            # COL-1..COL-4 map to BLOG-01..BLOG-04
            col_num = int(col_match.group(1).split("-")[1])
            example_id = f"BLOG-{col_num:02d}"
        else:
            continue

        # Extract section text between this header and the next
        start = match.end()
        if i + 1 < len(headers):
            end = headers[i + 1].start()
        else:
            # For the last story, go until the Technical Term Quick Reference
            ref_match = re.search(r"^##\s+Technical Term", text[start:], re.MULTILINE)
            end = start + ref_match.start() if ref_match else len(text)

        section = text[start:end].strip()

        parsed = _parse_section(section, example_id)
        if parsed:
            stories.append(parsed)

    return stories


def _parse_section(section: str, example_id: str) -> dict | None:
    """Parse a single story section into structured fields.

    Args:
        section: The markdown text for one story.
        example_id: The example ID (e.g., "EX-01").

    Returns:
        Dict with example_id and extracted fields, or None if parsing fails.
    """
    result = {"example_id": example_id}

    # Extract Situation
    sit_match = re.search(
        r"\*\*Situation:\*\*\s*(.+?)(?=\n\n|\n>|\n\*\*)",
        section,
        re.DOTALL,
    )
    if sit_match:
        result["situation"] = _clean_text(sit_match.group(1))

    # Extract Risk if not addressed
    risk_match = re.search(
        r"\*\*Risk if not addressed:\*\*\s*(.+?)(?=\n\n|\n>|\n\*\*)",
        section,
        re.DOTALL,
    )
    if risk_match:
        result["risk_statement"] = _clean_text(risk_match.group(1))

    # Extract Action (bullet points)
    action_match = re.search(
        r"\*\*Action:\*\*\s*\n((?:[-*]\s+.+\n?)+)",
        section,
    )
    if action_match:
        result["action"] = _clean_text(action_match.group(1))

    # Extract Result
    result_match = re.search(
        r"\*\*Result:\*\*\s*(.+?)(?=\n---|\n##|\Z)",
        section,
        re.DOTALL,
    )
    if result_match:
        result["result"] = _clean_text(result_match.group(1))

    # Extract Terms (from > **Terms:** blocks)
    terms_match = re.search(
        r">\s*\*\*Terms?:\*\*\s*(.+?)(?=\n\n|\n\*\*)",
        section,
        re.DOTALL,
    )
    if terms_match:
        result["tech_terms"] = _parse_terms(terms_match.group(1))

    # Extract Simple analogy
    analogy_match = re.search(
        r">\s*\*\*Simple analogy:\*\*\s*(.+?)(?=\n\n|\n\*\*)",
        section,
        re.DOTALL,
    )
    if analogy_match:
        result["analogy"] = _clean_text(analogy_match.group(1))

    return result


def _clean_text(text: str) -> str:
    """Clean extracted markdown text: strip blockquote markers, normalize whitespace.

    Args:
        text: Raw extracted text.

    Returns:
        Cleaned text string.
    """
    # Remove leading > from blockquote lines
    lines = text.strip().split("\n")
    cleaned = []
    for line in lines:
        line = re.sub(r"^>\s*", "", line)
        cleaned.append(line.strip())
    return " ".join(cleaned).strip()


def _parse_terms(text: str) -> dict[str, str]:
    """Parse technical terms from the Terms block into a dict.

    Args:
        text: The terms text block (e.g., "*LTR (Learning to Rank)* = ML model...").

    Returns:
        Dict mapping term names to definitions.
    """
    terms = {}
    # Pattern: *Term (Full Name)* = definition  OR  *Term* = definition
    for match in re.finditer(
        r"\*([^*]+)\*\s*=\s*([^.]+(?:\.[^*])*?)(?=\.\s*\*|\.\s*$|\Z)",
        text,
        re.DOTALL,
    ):
        term_name = match.group(1).strip()
        definition = match.group(2).strip().rstrip(".")
        # Normalize whitespace
        definition = re.sub(r"\s+", " ", definition)
        terms[term_name] = definition
    return terms


# ---------------------------------------------------------------------------
# Database operations
# ---------------------------------------------------------------------------

def run_backup() -> bool:
    """Run the database backup script before making changes.

    Returns:
        True if backup succeeded, False otherwise.
    """
    if not BACKUP_SCRIPT.exists():
        print(f"[FAIL] Backup script not found: {BACKUP_SCRIPT}")
        return False

    print("[INFO] Running database backup...")
    result = subprocess.run(
        [sys.executable, str(BACKUP_SCRIPT)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    if result.returncode != 0:
        print(f"[FAIL] Backup failed (exit code {result.returncode})")
        print(result.stderr)
        return False

    print(f"[OK] Backup completed: {result.stdout.strip()}")
    return True


def show_diff(conn: sqlite3.Connection, stories: list[dict]) -> int:
    """Show old-vs-new diff for each record that would be updated.

    Args:
        conn: SQLite connection.
        stories: Parsed story data.

    Returns:
        Number of records that would be updated.
    """
    update_count = 0
    for story in stories:
        eid = story["example_id"]
        row = conn.execute(
            "SELECT example_id, situation, action, result, "
            "risk_statement, analogy, tech_terms FROM behavioral_examples "
            "WHERE example_id = ?",
            (eid,),
        ).fetchone()

        if not row:
            print(f"\n[WARN] {eid}: not found in DB, skipping")
            continue

        fields = ["situation", "action", "result", "risk_statement", "analogy", "tech_terms"]
        has_changes = False
        diff_lines = []

        for field in fields:
            new_val = story.get(field)
            if new_val is None:
                continue

            col_idx = fields.index(field) + 1  # offset by 1 (example_id is col 0)
            old_val = row[col_idx]

            if field == "tech_terms":
                new_str = json.dumps(new_val, ensure_ascii=False)
                old_str = old_val or ""
                if old_str != new_str:
                    has_changes = True
                    diff_lines.append(f"  {field}:")
                    diff_lines.append(f"    - OLD: {_truncate(old_str, 80)}")
                    diff_lines.append(f"    + NEW: {_truncate(new_str, 80)}")
            else:
                if (old_val or "") != new_val:
                    has_changes = True
                    diff_lines.append(f"  {field}:")
                    diff_lines.append(f"    - OLD: {_truncate(old_val or '', 80)}")
                    diff_lines.append(f"    + NEW: {_truncate(new_val, 80)}")

        if has_changes:
            update_count += 1
            print(f"\n[DIFF] {eid}:")
            for line in diff_lines:
                print(line)

    return update_count


def apply_updates(conn: sqlite3.Connection, stories: list[dict]) -> int:
    """Apply all updates in a single transaction.

    Args:
        conn: SQLite connection.
        stories: Parsed story data.

    Returns:
        Number of records updated.

    Raises:
        Exception: If any update fails (transaction is rolled back).
    """
    update_count = 0

    for story in stories:
        eid = story["example_id"]

        # Check record exists
        row = conn.execute(
            "SELECT id FROM behavioral_examples WHERE example_id = ?", (eid,)
        ).fetchone()
        if not row:
            print(f"[WARN] {eid}: not found in DB, skipping")
            continue

        # Build SET clause dynamically
        set_parts = []
        params = []

        for field in ("situation", "action", "result", "risk_statement", "analogy"):
            if field in story:
                set_parts.append(f"{field} = ?")
                params.append(story[field])

        if "tech_terms" in story:
            tt_json = json.dumps(story["tech_terms"], ensure_ascii=False)
            # Validate JSON roundtrip
            json.loads(tt_json)
            set_parts.append("tech_terms = ?")
            params.append(tt_json)

        if not set_parts:
            continue

        params.append(eid)
        sql = f"UPDATE behavioral_examples SET {', '.join(set_parts)} WHERE example_id = ?"
        conn.execute(sql, params)
        update_count += 1
        print(f"  [OK] {eid} updated ({len(set_parts)} fields)")

    return update_count


def _truncate(text: str, max_len: int) -> str:
    """Truncate text for display.

    Args:
        text: Text to truncate.
        max_len: Maximum length before truncation.

    Returns:
        Truncated text with ellipsis if needed.
    """
    if len(text) <= max_len:
        return text
    return text[:max_len] + "..."


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Entry point for the improved BQ update script."""
    # Force UTF-8 stdout on Windows
    if sys.stdout.encoding != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    if sys.stderr.encoding != "utf-8":
        sys.stderr.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Update behavioral_examples with improved story data"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually write changes to DB (default is dry-run)",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DB_PATH,
        help=f"Database path (default: {DB_PATH})",
    )
    parser.add_argument(
        "--stories",
        type=Path,
        default=STORIES_PATH,
        help=f"Stories markdown path (default: {STORIES_PATH})",
    )
    args = parser.parse_args()

    if not args.stories.exists():
        print(f"[FAIL] Stories file not found: {args.stories}")
        sys.exit(1)

    if not args.db.exists():
        print(f"[FAIL] Database not found: {args.db}")
        sys.exit(1)

    # Parse stories
    print(f"[INFO] Parsing stories from: {args.stories}")
    stories = parse_stories(args.stories)
    print(f"[INFO] Parsed {len(stories)} stories")

    if not stories:
        print("[FAIL] No stories parsed, aborting")
        sys.exit(1)

    conn = sqlite3.connect(str(args.db))

    if not args.apply:
        # Dry-run: show diff
        print("\n=== DRY RUN (use --apply to write) ===\n")
        count = show_diff(conn, stories)
        print(f"\n=== {count} records would be updated ===")
        conn.close()
        return

    # Apply mode: backup first
    if not run_backup():
        print("[FAIL] Backup failed, aborting update")
        conn.close()
        sys.exit(1)

    print("\n=== APPLYING UPDATES ===\n")
    try:
        count = apply_updates(conn, stories)
        conn.commit()
        print(f"\n=== {count} records updated successfully ===")
    except Exception as e:
        conn.rollback()
        print(f"\n[FAIL] Update failed, rolled back: {e}")
        conn.close()
        sys.exit(1)

    conn.close()


if __name__ == "__main__":
    main()
