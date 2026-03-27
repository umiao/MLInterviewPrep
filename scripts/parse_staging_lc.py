"""Parse 'LC to be added' staging file into clean JSON.

Two format zones:
  Zone 1 (lines 1-334): "LC_ID. Title" only, no difficulty/pct
  Zone 2 (lines 337-end): "LC_ID. Title" / "pct%" / "Easy|Med.|Hard"

All problems tagged with LinkedIn, Uber, Adobe.
Output: data/staging_lc_parsed.json
"""

import json
import re
import sys
from pathlib import Path

STAGING_FILE = Path(r"C:\Users\Shenghui Xu\Desktop\staging\LC to be added 题解.txt")
OUTPUT_FILE = Path(__file__).resolve().parent.parent / "data" / "staging_lc_parsed.json"

# Pattern: "123. Title Here"
PROBLEM_RE = re.compile(r"^(\d+)\.\s+(.+)$")
PCT_RE = re.compile(r"^\d+\.\d+%$")
DIFF_RE = re.compile(r"^(Easy|Med\.|Hard)$")

DIFF_MAP = {"Easy": "Easy", "Med.": "Medium", "Hard": "Hard"}


def parse_file(filepath: Path) -> list[dict]:
    """Parse the staging LC file and return list of problem dicts."""
    lines = filepath.read_text(encoding="utf-8").splitlines()

    problems: list[dict] = []
    seen_ids: set[int] = set()
    rank = 0

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        m = PROBLEM_RE.match(line)
        if m:
            lc_id = int(m.group(1))
            title = m.group(2).strip()
            rank += 1

            # Look ahead for pct and difficulty
            difficulty = None
            j = i + 1
            # Skip blank lines, then check for pct% and difficulty
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            if j < len(lines) and PCT_RE.match(lines[j].strip()):
                # Found pct line, next non-blank should be difficulty
                j += 1
                while j < len(lines) and lines[j].strip() == "":
                    j += 1
                if j < len(lines) and DIFF_RE.match(lines[j].strip()):
                    difficulty = DIFF_MAP[lines[j].strip()]

            if lc_id not in seen_ids:
                seen_ids.add(lc_id)
                problems.append({
                    "lc_id": lc_id,
                    "title": title,
                    "difficulty": difficulty,
                    "frequency_rank": rank,
                    "company_tags": ["LinkedIn", "Uber", "Adobe"],
                })
            # else: duplicate, skip but still counted rank

        i += 1

    return problems


def main() -> None:
    """Parse staging file and write JSON output."""
    if not STAGING_FILE.exists():
        print(f"[FAIL] Staging file not found: {STAGING_FILE}", file=sys.stderr)
        sys.exit(1)

    problems = parse_file(STAGING_FILE)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(problems, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # Stats
    with_diff = sum(1 for p in problems if p["difficulty"] is not None)
    without_diff = sum(1 for p in problems if p["difficulty"] is None)
    print(f"[DONE] Parsed {len(problems)} unique problems")
    print(f"  With difficulty: {with_diff}")
    print(f"  Without difficulty: {without_diff}")
    print(f"  Output: {OUTPUT_FILE}")

    # Sanity: check for any duplicates
    ids = [p["lc_id"] for p in problems]
    if len(ids) != len(set(ids)):
        print("[FAIL] Duplicate lc_ids found!", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
