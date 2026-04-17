"""Seed detailed solutions for custom (non-LC) Uber problems into mle_prep.db.

Parses docs/company/uber/bps_custom_solutions.md and extracts per-problem sections,
then appends them to the `notes` field of matching DB problems.

Idempotent: skips problems that already have the [Uber BPS Custom Solution] tag.

Task: T-P0-243
"""

import re
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
DOC_PATH = Path(__file__).resolve().parent.parent / "docs" / "uber_bps_custom_solutions.md"

# Map problem number (1-25) to DB problem ID
PROBLEM_MAP: dict[int, int] = {
    1: 1031,   # Purchase Optimization
    2: 1032,   # Customer Revenue & Referral Tracking
    3: 1033,   # Uber Rider Connection Log
    4: 1034,   # Elevator Binary Search OA
    5: 1035,   # Server Throughput with Heap
    6: 1036,   # Cart & Pricing Engine OOD
    7: 1037,   # Circular Array Shortest Jump
    8: 1038,   # Robot Distance in Grid
    9: 1039,   # Min Operations n to 0
    10: 1040,  # Shortest Subarray with k Distinct
    11: 1041,  # Price Discount
    12: 1042,  # Balanced Permutation
    13: 1043,  # Elevator/Stairs Energy
    14: 1044,  # N-ary Tree 3-Part
    15: 1045,  # Max Throughput with Budget
    16: 1046,  # Parking Lot OOD
    17: 1047,  # Task Assignment to 2 People
    18: None,  # Jump Game Prime -> already in LC solutions
    19: None,  # Min Edge Reversal -> already in LC solutions
    20: None,  # Palindrome Paths -> already in LC solutions
    21: 1048,  # Minesweeper Grid Generator
    22: 1049,  # 2D Grid Nearest Exit
    23: 1050,  # Lock Combination BFS
    24: 1051,  # Non-overlapping Interval Triples
    25: 1052,  # City Graph BFS Sort
}

SOLUTION_TAG = "[Uber BPS Custom Solution]"


def parse_solutions(doc_path: Path) -> dict[int, str]:
    """Parse markdown doc and extract per-problem solution sections.

    Returns: {problem_number: solution_markdown}
    """
    text = doc_path.read_text(encoding="utf-8")

    # Split on "## N. " or "## (N) " section headers
    # Pattern matches: ## 1. Title or ## (1) Title
    pattern = r"^## (?:(\d+)\.|(\(\d+\)))\s+"
    sections: dict[int, str] = {}

    lines = text.split("\n")
    current_num = None
    current_lines: list[str] = []

    for line in lines:
        match = re.match(r"^## (\d+)\.\s+", line)
        if match:
            # Save previous section
            if current_num is not None:
                sections[current_num] = "\n".join(current_lines).strip()
            current_num = int(match.group(1))
            current_lines = [line]
        elif current_num is not None:
            # Stop at Summary Table or next major section
            if line.startswith("## Summary") or line.startswith("## Pattern"):
                sections[current_num] = "\n".join(current_lines).strip()
                current_num = None
                current_lines = []
            else:
                current_lines.append(line)

    # Save last section
    if current_num is not None:
        sections[current_num] = "\n".join(current_lines).strip()

    return sections


def seed_solutions() -> None:
    """Seed solutions into DB notes field."""
    if not DOC_PATH.exists():
        print(f"[ERROR] Document not found: {DOC_PATH}")
        return

    sections = parse_solutions(DOC_PATH)
    print(f"Parsed {len(sections)} problem sections from document\n")

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    updated = 0
    skipped = 0

    for prob_num, db_id in sorted(PROBLEM_MAP.items()):
        if db_id is None:
            print(f"  [SKIP] Problem {prob_num}: LC variant (see LC solutions doc)")
            skipped += 1
            continue

        if prob_num not in sections:
            print(f"  [WARN] Problem {prob_num}: no section found in document")
            skipped += 1
            continue

        # Check current notes
        cursor.execute("SELECT id, title, notes FROM problems WHERE id = ?", (db_id,))
        row = cursor.fetchone()
        if not row:
            print(f"  [WARN] DB ID {db_id} not found, skipping problem {prob_num}")
            skipped += 1
            continue

        current_notes = row["notes"] or ""
        if SOLUTION_TAG in current_notes:
            print(f"  [SKIP] {row['title']} (#{prob_num}) already has custom solution")
            skipped += 1
            continue

        # Build solution note
        solution_md = sections[prob_num]
        tagged_solution = f"{SOLUTION_TAG} Problem #{prob_num}\n\n{solution_md}"

        if current_notes:
            new_notes = current_notes + "\n\n---\n\n" + tagged_solution
        else:
            new_notes = tagged_solution

        cursor.execute("UPDATE problems SET notes = ? WHERE id = ?", (new_notes, db_id))
        updated += 1
        print(f"  [OK] {row['title']} (#{prob_num}, db_id={db_id})")

    conn.commit()
    conn.close()
    print(f"\nDone: {updated} updated, {skipped} skipped")


if __name__ == "__main__":
    print("=== Seeding Uber BPS Custom Solutions ===\n")
    seed_solutions()
