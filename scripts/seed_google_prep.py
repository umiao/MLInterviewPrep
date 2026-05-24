"""Seed Google recruiter call prep notes into company_documents and update company record."""
import json
import os
import sqlite3

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_DIR, "data", "mle_prep.db")
DOCS_DIR = os.path.join(PROJECT_DIR, "docs")

COMPANY_ID = 3  # Google


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Seed recruiter call prep document
    doc_path = os.path.join(DOCS_DIR, "google_recruiter_call_prep.md")
    with open(doc_path, encoding="utf-8") as f:
        content = f.read()

    # Check if document already exists
    cursor.execute(
        "SELECT id FROM company_documents WHERE company_id = ? AND title = ?",
        (COMPANY_ID, "Google SWE III (AI/ML) -- Recruiter Call Prep"),
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
            (COMPANY_ID, "Google SWE III (AI/ML) -- Recruiter Call Prep", content, "prep_doc"),
        )
        print(f"[INSERT] Created new document id={cursor.lastrowid}")

    # 2. Update company status to phone_screen and set interview stages
    interview_stages = json.dumps([
        {"name": "Recruiter Call", "status": "completed"},
        {"name": "Round 1: ML Domain (Virtual)", "status": "upcoming"},
        {"name": "Round 1: G&L (Virtual)", "status": "upcoming"},
        {"name": "Round 2: Coding #1 (Onsite)", "status": "upcoming"},
        {"name": "Round 2: Coding #2 (Onsite)", "status": "upcoming"},
    ])

    updated_notes = (
        "Positions applied:\n"
        "- Software Engineer, AI/ML, Google Ads\n"
        "- Software Engineer III, Core\n"
        "- Software Engineer III, Infrastructure, Core\n"
        "Note: 3 jobs in 30-day window reached. Resets 4/4.\n\n"
        "2026-04-08 Recruiter Call Summary:\n"
        "- Round 1 (virtual): ML Domain (45min) + G&L (45min)\n"
        "- Round 2 (onsite): Coding x2 (45min each)\n"
        "- ML Domain: paradigm iteration, data analysis, ML+product insight, modeling basics\n"
        "- G&L: leadership affecting multiple teams, user-first mindset\n"
        "- Coding moved to physical onsite (no virtual coding round)"
    )

    cursor.execute(
        "UPDATE companies SET status = 'phone_screen', "
        "interview_stages = ?, notes = ? WHERE id = ?",
        (interview_stages, updated_notes, COMPANY_ID),
    )
    print("[UPDATE] Google status -> phone_screen, interview stages set")

    # 3. Update recruiter call event to completed
    cursor.execute(
        "UPDATE interview_events SET status = 'completed', "
        "description = 'Completed recruiter call. Interview structure confirmed: "
        "Round 1 virtual (ML Domain + G&L), Round 2 onsite (Coding x2).' "
        "WHERE company_id = ? AND event_type = 'hr_call' AND status = 'upcoming'",
        (COMPANY_ID,),
    )
    rows_updated = cursor.rowcount
    print(f"[UPDATE] Marked {rows_updated} recruiter call event(s) as completed")

    conn.commit()
    conn.close()
    print("[DONE] Google prep data seeded successfully")


if __name__ == "__main__":
    main()
