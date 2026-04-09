"""Seed DoorDash ML Domain Ranking prep doc into company_documents."""
import os
import sqlite3

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_DIR, "data", "mle_prep.db")
DOCS_DIR = os.path.join(PROJECT_DIR, "docs")

COMPANY_ID = 2  # DoorDash

DOC_TITLE = "DoorDash ML Domain Prep: Ranking Models + Multi-Task Learning Deep Dive"


def main() -> None:
    """Read the markdown doc and upsert into company_documents."""
    doc_path = os.path.join(DOCS_DIR, "doordash_ml_domain_ranking.md")
    with open(doc_path, encoding="utf-8") as f:
        content = f.read()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Upsert document
    cursor.execute(
        "SELECT id FROM company_documents WHERE company_id = ? AND title = ?",
        (COMPANY_ID, DOC_TITLE),
    )
    existing = cursor.fetchone()
    if existing:
        cursor.execute(
            "UPDATE company_documents SET content = ?, updated_at = datetime('now') "
            "WHERE id = ?",
            (content, existing[0]),
        )
        print(f"[UPDATE] Updated existing document id={existing[0]}")
    else:
        cursor.execute(
            "INSERT INTO company_documents (company_id, title, content, source_type) "
            "VALUES (?, ?, ?, ?)",
            (COMPANY_ID, DOC_TITLE, content, "prep_doc"),
        )
        print(f"[INSERT] Created new document id={cursor.lastrowid}")

    conn.commit()
    conn.close()
    print("[DONE] DoorDash ranking prep doc seeded successfully")


if __name__ == "__main__":
    main()
