"""Bulk import LinkedIn seed data into the interview_questions table.

Reads all JSON files from data/linkedin_seed/, validates required fields,
and inserts into the DB via SQLAlchemy. Skips duplicates (same question_text
for company=LinkedIn). Also updates the LinkedIn company entry with prep_notes.

Idempotent: safe to re-run.
"""

import json
import sys
from pathlib import Path

# Allow running from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.company import Company  # noqa: E402
from src.backend.models.scraper import InterviewQuestion  # noqa: E402

SEED_DIR = Path(__file__).resolve().parent.parent / "data" / "linkedin_seed"

SEED_FILES = [
    "coding.json",
    "ml_theory_and_coding.json",
    "ml_system_design.json",
]

LINKEDIN_PREP_NOTES = (
    "Phone screen format: 45-60 min, typically 1-2 rounds.\n"
    "Heavy on coding (LC medium, data structures, graph/tree, SQL),\n"
    "ML system design (feed ranking, job recommendations, metrics, A/B testing),\n"
    "and product/metrics questions (feature evaluation, metric debugging).\n"
    "Behavioral questions appear but are lighter weight.\n"
    "Common topics: topological sort, hash map design, tree traversal,\n"
    "recommendation systems, ranking models, experimentation frameworks."
)


def load_seed_file(filepath: Path) -> list[dict]:
    """Load and return questions from a seed JSON file.

    Args:
        filepath: Path to the JSON seed file.

    Returns:
        List of question dicts.
    """
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)
    return data


def import_questions() -> None:
    """Import all LinkedIn seed questions into the database."""
    init_db()
    db = SessionLocal()
    try:
        # Get existing LinkedIn question texts for dedup
        existing_texts = {
            row.question_text
            for row in db.query(InterviewQuestion.question_text).filter(
                InterviewQuestion.company == "LinkedIn"
            ).all()
        }

        total_added = 0
        total_skipped = 0

        for filename in SEED_FILES:
            filepath = SEED_DIR / filename
            if not filepath.exists():
                print(f"  [WARN] Seed file not found: {filepath}")
                continue

            questions = load_seed_file(filepath)
            added = 0
            skipped = 0

            for q in questions:
                # Validate required fields
                if not q.get("question_text"):
                    print(f"  [WARN] Skipping question with empty question_text in {filename}")
                    skipped += 1
                    continue
                if q.get("company") != "LinkedIn":
                    print(f"  [WARN] Skipping non-LinkedIn question in {filename}: {q.get('company')}")
                    skipped += 1
                    continue

                # Dedup check
                if q["question_text"] in existing_texts:
                    skipped += 1
                    continue

                # Build InterviewQuestion
                iq = InterviewQuestion(
                    company=q["company"],
                    role=q.get("role"),
                    level=q.get("level"),
                    interview_round=q.get("interview_round"),
                    year=q.get("year"),
                    question_text=q["question_text"],
                    question_type=q.get("question_type"),
                    tags=json.dumps(q.get("tags", []), ensure_ascii=False),
                    difficulty_estimate=q.get("difficulty_estimate"),
                    notes=q.get("notes"),
                    is_reviewed=False,
                )
                db.add(iq)
                existing_texts.add(q["question_text"])
                added += 1

            print(f"  {filename}: {added} added, {skipped} skipped")
            total_added += added
            total_skipped += skipped

        # Update LinkedIn company prep_notes
        linkedin = db.query(Company).filter(Company.name == "LinkedIn").first()
        if linkedin:
            linkedin.prep_notes = LINKEDIN_PREP_NOTES
            linkedin.status = "phone_screen"
            print("  Updated LinkedIn company prep_notes and status=phone_screen")
        else:
            # Create LinkedIn entry if missing
            linkedin = Company(
                name="LinkedIn",
                status="phone_screen",
                prep_notes=LINKEDIN_PREP_NOTES,
            )
            db.add(linkedin)
            print("  Created LinkedIn company entry")

        db.commit()
        print(f"\nTotal: {total_added} questions added, {total_skipped} skipped")

    finally:
        db.close()


if __name__ == "__main__":
    import_questions()
