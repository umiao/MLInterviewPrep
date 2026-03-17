"""Import Blind 75 solution notes from a .docx file into the database.

Two-step process:
  Step 1 (default): Parse docx -> JSON preview at data/blind75_parsed.json
  Step 2 (--commit): Write parsed entries into the database

Usage:
  python scripts/import_blind75_notes.py path/to/Blind75.docx
  python scripts/import_blind75_notes.py --commit
"""
import argparse
import io
import json
import logging
import re
import sys
from pathlib import Path

# Ensure UTF-8 stdout on Windows (cp1252 cannot encode CJK characters)
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Ensure project root is importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)

BLIND75_JSON = PROJECT_ROOT / "src" / "backend" / "seed_data" / "blind75.json"
PARSED_OUTPUT = PROJECT_ROOT / "data" / "blind75_parsed.json"


def _load_blind75_index() -> dict[int, dict]:
    """Load blind75.json and return a dict keyed by leetcode_id.

    Returns:
        Mapping of leetcode_id -> problem metadata dict.
    """
    with open(BLIND75_JSON, encoding="utf-8") as f:
        problems = json.load(f)
    return {p["leetcode_id"]: p for p in problems}


def parse_docx(docx_path: str) -> list[dict]:
    """Parse a docx file containing Blind 75 solution notes.

    Expects paragraphs with a pattern like "number: <int>" or "#<int>"
    to identify problems, followed by note text until the next problem.

    Args:
        docx_path: Path to the .docx file.

    Returns:
        List of dicts with keys: leetcode_id, title_hint, notes.
    """
    try:
        from docx import Document as _Document
    except ImportError:
        print("[FAIL] python-docx is required: pip install python-docx")
        sys.exit(1)

    doc = _Document(docx_path)
    entries: list[dict] = []
    current_id: int | None = None
    current_title_hint: str = ""
    current_lines: list[str] = []

    # Pattern to match problem identifiers like "1. Two Sum", "#1", "number: 1"
    # Include full-width colon \uff1a and full-width period \uff0e for CJK docs
    id_pattern = re.compile(
        r"(?:^|\s)#?(\d{1,4})[.\s:\uff1a\uff0e]+\s*(.*)",
        re.IGNORECASE,
    )
    # Also match "LC 1" or "LeetCode 1" patterns
    lc_pattern = re.compile(
        r"(?:lc|leetcode)\s*#?\s*(\d{1,4})[.\s:]*\s*(.*)",
        re.IGNORECASE,
    )

    def flush() -> None:
        """Save accumulated notes for the current problem."""
        if current_id is not None and current_lines:
            text = "\n".join(current_lines).strip()
            if text:
                entries.append({
                    "leetcode_id": current_id,
                    "title_hint": current_title_hint,
                    "notes": text,
                })

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            current_lines.append("")
            continue

        # Check for a new problem header
        match = lc_pattern.match(text) or id_pattern.match(text)
        if match:
            lc_id = int(match.group(1))
            title_hint = match.group(2).strip() if match.group(2) else ""
            # Only treat as new problem if ID is in a reasonable range
            if 1 <= lc_id <= 2000:
                flush()
                current_id = lc_id
                current_title_hint = title_hint
                current_lines = []
                continue

        current_lines.append(text)

    flush()
    return entries


def step1_parse(docx_path: str) -> None:
    """Parse docx and write JSON preview.

    Args:
        docx_path: Path to the .docx file.
    """
    blind75_index = _load_blind75_index()
    raw_entries = parse_docx(docx_path)

    results: list[dict] = []
    matched_ids: set[int] = set()

    for entry in raw_entries:
        lc_id = entry["leetcode_id"]
        meta = blind75_index.get(lc_id)
        matched = meta is not None
        results.append({
            "leetcode_id": lc_id,
            "title": meta["title"] if meta else entry["title_hint"],
            "notes": entry["notes"],
            "matched": matched,
            "in_blind75": matched,
        })
        if matched:
            matched_ids.add(lc_id)

    # Log blind75 problems without notes
    missing = [p for lc_id, p in sorted(blind75_index.items()) if lc_id not in matched_ids]

    # Also add blind75 problems without notes for completeness
    for p in missing:
        results.append({
            "leetcode_id": p["leetcode_id"],
            "title": p["title"],
            "notes": None,
            "matched": True,
            "in_blind75": True,
        })

    PARSED_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(PARSED_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Summary
    with_notes = [r for r in results if r["notes"]]
    without_notes = [r for r in results if not r["notes"]]
    not_in_blind75 = [r for r in results if not r["in_blind75"]]

    print(f"[DONE] Parsed {len(raw_entries)} entries from docx")
    print(f"  {len(with_notes)} problems with notes")
    print(f"  {len(without_notes)} blind75 problems without notes")
    if not_in_blind75:
        print(f"  {len(not_in_blind75)} entries NOT in Blind 75:")
        for r in not_in_blind75:
            print(f"    LC {r['leetcode_id']}: {r['title']}")
    print(f"\nOutput: {PARSED_OUTPUT}")
    print("Review the JSON, then run with --commit to write to DB.")


def step2_commit() -> None:
    """Read parsed JSON and write to database."""
    if not PARSED_OUTPUT.exists():
        print(f"[FAIL] {PARSED_OUTPUT} not found. Run step 1 first (without --commit).")
        sys.exit(1)

    with open(PARSED_OUTPUT, encoding="utf-8") as f:
        entries = json.load(f)

    blind75_index = _load_blind75_index()

    from src.backend.database import SessionLocal, init_db
    from src.backend.models.problem import Problem

    init_db()
    db = SessionLocal()

    updated = 0
    inserted = 0
    skipped = 0

    try:
        for entry in entries:
            lc_id = entry["leetcode_id"]
            notes = entry.get("notes")

            existing = db.query(Problem).filter(Problem.leetcode_id == lc_id).first()

            if existing:
                if notes and (not existing.notes or existing.notes != notes):
                    existing.notes = notes
                    updated += 1
                else:
                    skipped += 1
            else:
                meta = blind75_index.get(lc_id)
                if not meta and not entry.get("in_blind75"):
                    skipped += 1
                    continue

                if meta:
                    import json as json_mod
                    new_problem = Problem(
                        leetcode_id=lc_id,
                        title=meta["title"],
                        url=meta.get("url"),
                        difficulty=meta.get("difficulty"),
                        tags=json_mod.dumps(meta.get("tags", []), ensure_ascii=False),
                        pattern=meta.get("pattern"),
                        source=meta.get("source", "blind75"),
                        notes=notes,
                    )
                    db.add(new_problem)
                    inserted += 1
                else:
                    skipped += 1

        db.commit()
        print("[DONE] Database updated:")
        print(f"  {updated} updated (notes added/changed)")
        print(f"  {inserted} inserted (new problems)")
        print(f"  {skipped} skipped (no change needed)")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def main() -> None:
    """Entry point for the import script."""
    parser = argparse.ArgumentParser(
        description="Import Blind 75 notes from docx into the database",
    )
    parser.add_argument(
        "docx_path",
        nargs="?",
        help="Path to the .docx file (step 1: parse to JSON)",
    )
    parser.add_argument(
        "--commit",
        action="store_true",
        help="Step 2: write parsed JSON to database",
    )
    args = parser.parse_args()

    if args.commit:
        step2_commit()
    elif args.docx_path:
        step1_parse(args.docx_path)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
