# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
"""Seed Pinterest recruiter call prep notes into company_documents and update company record."""
import json
import os
import sqlite3

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_DIR, "data", "mle_prep.db")
DOCS_DIR = os.path.join(PROJECT_DIR, "docs")

COMPANY_ID = 29  # Pinterest


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Seed recruiter call prep document
    doc_path = os.path.join(DOCS_DIR, "pinterest_recruiter_call_prep.md")
    with open(doc_path, encoding="utf-8") as f:
        content = f.read()

    # Check if document already exists
    cursor.execute(
        "SELECT id FROM company_documents WHERE company_id = ? AND title = ?",
        (COMPANY_ID, "Pinterest Senior MLE -- Recruiter Call Prep"),
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
            (COMPANY_ID, "Pinterest Senior MLE -- Recruiter Call Prep", content, "prep_doc"),
        )
        print(f"[INSERT] Created new document id={cursor.lastrowid}")

    # 2. Update company status to phone_screen and set interview stages
    interview_stages = json.dumps([
        {"name": "Recruiter Call", "status": "completed"},
        {"name": "Phone Screen (60min: ML Project + ML Fundamentals + Coding)", "status": "upcoming"},
        {"name": "VO Round 1: Coding", "status": "upcoming"},
        {"name": "VO Round 2: Coding", "status": "upcoming"},
        {"name": "VO Round 3: ML Deep Dive", "status": "upcoming"},
        {"name": "VO Round 4: ML System Modeling", "status": "upcoming"},
        {"name": "VO Round 5: Behavioral", "status": "upcoming"},
    ])

    notes = (
        "Senior ML Engineer position\n"
        "TC ~$500K/yr\n"
        "Hiring model: general pool, ~5 HC available, competitive Team Match required\n\n"
        "2026-04-08 Recruiter Call Summary:\n"
        "- Phone Screen (60min): ML Project Discussion + 3 ML Fundamentals questions + Coding\n"
        "- Virtual Onsite (5 rounds x 60min): Coding x2, ML Deep Dive, ML System Modeling, BQ\n"
        "- Environment: Google Meet + CoderPad (no compiler)\n"
        "- Phone screen time TBD -- need to send 3+ availability slots to David"
    )

    cursor.execute(
        "UPDATE companies SET status = 'phone_screen', "
        "interview_stages = ?, notes = ? WHERE id = ?",
        (interview_stages, notes, COMPANY_ID),
    )
    print("[UPDATE] Pinterest status -> phone_screen, interview stages set")

    # 3. Update recruiter call event to completed
    cursor.execute(
        "UPDATE interview_events SET status = 'completed', "
        "description = 'Completed recruiter call with David. Interview structure confirmed: "
        "Phone Screen (60min) then Virtual Onsite (5 rounds). Phone screen time TBD.' "
        "WHERE company_id = ? AND event_type = 'hr_call' AND status = 'upcoming'",
        (COMPANY_ID,),
    )
    rows_updated = cursor.rowcount
    print(f"[UPDATE] Marked {rows_updated} recruiter call event(s) as completed")

    conn.commit()
    conn.close()
    print("[DONE] Pinterest prep data seeded successfully")


if __name__ == "__main__":
    main()
