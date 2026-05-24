# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
"""Import Uber BPS prep documents into company_documents table.

Imports 7 new Uber prep docs and updates existing Phone Screen Prep doc (id=3).
All docs go to company_id=5 (Uber) with source_type=prep_doc.
"""
import os
import sqlite3

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DB_PATH = os.path.join(PROJECT_DIR, "data", "mle_prep.db")
DOCS_DIR = os.path.join(PROJECT_DIR, "docs")

UBER_COMPANY_ID = 5

# Documents to insert as new rows
NEW_DOCS = [
    ("uber_bps_lc_solutions.md", "Uber BPS LeetCode Solutions Guide"),
    ("uber_bps_custom_solutions.md", "Uber BPS Custom Problem Solutions"),
    ("uber_bps_pattern_cheatsheet.md", "Uber BPS Pattern Cheat Sheet by Algorithm"),
    ("uber_bps_design_architecture.md", "Uber BPS Design & Architecture Prep"),
    ("uber_bps_knn_ml_fundamentals.md", "Uber BPS KNN & ML Fundamentals Review"),
    ("uber_bps_mock_sets.md", "Uber BPS Timed Mock Interview Sets"),
    ("uber_hr_call_prep.md", "Uber HR Call Prep Notes"),
]

# Existing doc to update (replace outdated content)
UPDATE_DOC_ID = 3
UPDATE_FILE = "uber_phone_screen_prep.md"
UPDATE_TITLE = "Uber BPS Phone Screen Prep"


def read_doc(filename: str) -> str:
    """Read a markdown file from docs directory."""
    path = os.path.join(DOCS_DIR, filename)
    with open(path, encoding="utf-8") as f:
        return f.read()


def main() -> None:
    """Import all Uber BPS prep docs into the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Update existing Phone Screen Prep doc (id=3)
    content = read_doc(UPDATE_FILE)
    cursor.execute(
        "UPDATE company_documents SET title=?, content=?, source_type=? "
        "WHERE id=? AND company_id=?",
        (UPDATE_TITLE, content, "prep_doc", UPDATE_DOC_ID, UBER_COMPANY_ID),
    )
    print(f"[UPDATED] doc#{UPDATE_DOC_ID}: {UPDATE_TITLE} ({len(content)} chars)")

    # 2. Insert new documents
    for filename, title in NEW_DOCS:
        content = read_doc(filename)
        cursor.execute(
            "INSERT INTO company_documents (company_id, title, content, source_type) "
            "VALUES (?, ?, ?, ?)",
            (UBER_COMPANY_ID, title, content, "prep_doc"),
        )
        doc_id = cursor.lastrowid
        print(f"[INSERTED] doc#{doc_id}: {title} ({len(content)} chars)")

    conn.commit()

    # 3. Verify
    cursor.execute(
        "SELECT id, title, source_type, length(content) FROM company_documents "
        "WHERE company_id=? ORDER BY id",
        (UBER_COMPANY_ID,),
    )
    rows = cursor.fetchall()
    print(f"\nAll Uber docs ({len(rows)}):")
    for r in rows:
        print(f"  doc#{r[0]}: {r[1]} (type={r[2]}, {r[3]} chars)")

    conn.close()
    print("\n[DONE] Import complete.")


if __name__ == "__main__":
    main()
