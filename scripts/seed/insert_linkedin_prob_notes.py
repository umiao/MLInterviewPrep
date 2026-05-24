# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
"""Insert LinkedIn probability/statistics interview prep notes into company_documents."""
import os
import sqlite3

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DB_PATH = os.path.join(PROJECT_DIR, "data", "mle_prep.db")
CONTENT_PATH = os.path.join(PROJECT_DIR, "data", "linkedin_prob_notes_content.md")


def main() -> None:
    """Insert the prep notes into the database."""
    with open(CONTENT_PATH, encoding="utf-8") as f:
        content = f.read()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO company_documents (company_id, title, content, source_type) "
        "VALUES (?, ?, ?, ?)",
        (
            1,
            "LinkedIn probability/statistics interview prep notes (1point3acres)",
            content,
            "prep_doc",
        ),
    )
    conn.commit()
    doc_id = cursor.lastrowid
    content_len = len(content)
    print(f"[DONE] Inserted document id={doc_id}, content length={content_len} chars")
    conn.close()


if __name__ == "__main__":
    main()
