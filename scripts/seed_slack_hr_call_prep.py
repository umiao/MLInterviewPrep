"""Seed Slack (Salesforce) HR call prep doc into company_documents and update company/event rows.

Run: python scripts/seed_slack_hr_call_prep.py

Idempotent: updates existing company_documents row if title already present; otherwise inserts.
"""
import json
import os
import sqlite3

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_DIR, "data", "mle_prep.db")
DOCS_DIR = os.path.join(PROJECT_DIR, "docs")

COMPANY_ID = 32  # Slack
DOC_TITLE = "Slack (Salesforce) ML -- HR Call Prep"
DOC_FILE = "slack_hr_call_prep.md"


def main() -> None:
    """Ingest Slack HR call prep doc and update company/event records."""
    doc_path = os.path.join(DOCS_DIR, DOC_FILE)
    with open(doc_path, encoding="utf-8") as f:
        content = f.read()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Seed company_documents (idempotent upsert by title).
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
        print(f"[UPDATE] company_documents id={existing[0]}")
    else:
        cursor.execute(
            "INSERT INTO company_documents (company_id, title, content, source_type, doc_kind) "
            "VALUES (?, ?, ?, ?, ?)",
            (COMPANY_ID, DOC_TITLE, content, "prep_doc", "prep_note"),
        )
        print(f"[INSERT] company_documents id={cursor.lastrowid}")

    # 2. Update Slack company row: status -> phone_screen, add interview_stages + notes.
    interview_stages = json.dumps([
        {"name": "HR Call (recruiter screen)", "status": "upcoming"},
        {"name": "Phone Screen (ML + coding)", "status": "upcoming"},
        {"name": "Virtual Onsite (TBD rounds)", "status": "upcoming"},
    ])

    notes = (
        "Slack ML team (Salesforce ownership). HR call 2026-04-15 Wed 14:00 EST = 11:00 PT, 30-45 min.\n"
        "Prep doc: docs/slack_hr_call_prep.md. Self-intro, why-Slack, main story, comp, 3 questions.\n"
        "Target comp: $400-550K TC for Senior MLE. Timeline: 4-6 weeks.\n"
        "Slack ML hot spots: Slack AI (summary, search answers), channel/message ranking, "
        "enterprise search, Agentforce integration."
    )

    cursor.execute(
        "UPDATE companies SET status = 'phone_screen', interview_stages = ?, notes = ? "
        "WHERE id = ?",
        (interview_stages, notes, COMPANY_ID),
    )
    print(f"[UPDATE] companies id={COMPANY_ID} status=phone_screen")

    # 3. Attach prep reference to the existing hr_call interview_event (keep status=upcoming until call happens).
    updated_desc = (
        "2026-04-15 Wed 14:00 EST = 11:00 PT, 30-45 min. Recruiter screen for Slack (Salesforce) ML. "
        "Prep doc: docs/slack_hr_call_prep.md. Goals: (1) confirm team/role/loop, "
        "(2) deliver 90s self-intro + Ranking-as-Allocation main story, "
        "(3) comp anchor $400-550K TC, (4) ask 3 prepared questions."
    )
    cursor.execute(
        "UPDATE interview_events SET description = ? "
        "WHERE company_id = ? AND event_type = 'hr_call' AND status = 'upcoming'",
        (updated_desc, COMPANY_ID),
    )
    print(f"[UPDATE] interview_events updated rows={cursor.rowcount}")

    conn.commit()
    conn.close()
    print("[DONE] Slack HR call prep seeded.")


if __name__ == "__main__":
    main()
