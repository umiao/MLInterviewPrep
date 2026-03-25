"""Seed script for behavioral questions data.

Loads clustered questions and behavioral examples from JSON data files
into the behavioral_questions, behavioral_examples, and
question_example_links tables.

Usage:
    python scripts/seed_behavioral.py
    python scripts/seed_behavioral.py --dry-run
"""
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.backend.database import SessionLocal, init_db
from src.backend.models.behavioral import (
    BehavioralExample,
    BehavioralQuestion,
    QuestionExampleLink,
)


def load_json(path: Path) -> dict:
    """Load a JSON file with UTF-8 encoding.

    Args:
        path: Path to JSON file.

    Returns:
        Parsed JSON data.
    """
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def seed_questions(db, questions_data: dict, dry_run: bool = False) -> dict:
    """Seed behavioral questions from clustered data.

    Args:
        db: Database session.
        questions_data: Parsed bq_clustered_questions.json.
        dry_run: If True, don't commit.

    Returns:
        Dict with counts: inserted, skipped.
    """
    inserted = 0
    skipped = 0

    for category in questions_data["categories"]:
        cat_id = category["id"]
        cat_name = category["name"]

        for q in category["questions"]:
            existing = (
                db.query(BehavioralQuestion)
                .filter(BehavioralQuestion.question_id == q["id"])
                .first()
            )
            if existing:
                skipped += 1
                continue

            bq = BehavioralQuestion(
                question_id=q["id"],
                text=q["text"],
                category_id=cat_id,
                category_name=cat_name,
                original_category=q.get("original_category"),
                company_target="Meta E6",  # from blog source
            )
            db.add(bq)
            inserted += 1

    if not dry_run:
        db.flush()

    return {"inserted": inserted, "skipped": skipped}


def seed_examples(db, examples_data: dict, dry_run: bool = False) -> dict:
    """Seed behavioral examples from DoorDash deep dives + blog answers.

    Args:
        db: Database session.
        examples_data: Parsed bq_behavioral_examples.json.
        dry_run: If True, don't commit.

    Returns:
        Dict with counts: inserted, skipped.
    """
    inserted = 0
    skipped = 0

    # DoorDash + user-provided examples
    for ex in examples_data["examples"]:
        existing = (
            db.query(BehavioralExample)
            .filter(BehavioralExample.example_id == ex["id"])
            .first()
        )
        if existing:
            skipped += 1
            continue

        be = BehavioralExample(
            example_id=ex["id"],
            title=ex["title"],
            source_project=ex.get("source_project"),
            situation=ex.get("situation"),
            task=ex.get("task"),
            action=ex.get("action"),
            result=ex.get("result"),
            evidence_quotes=json.dumps(
                ex.get("evidence_quotes", []), ensure_ascii=False
            ),
            principle_tags=json.dumps(
                ex.get("principle_tags", []), ensure_ascii=False
            ),
        )
        db.add(be)
        inserted += 1

    # Blog existing answers (convert to example format)
    for ans in examples_data.get("blog_proj_existing_answers", []):
        existing = (
            db.query(BehavioralExample)
            .filter(BehavioralExample.example_id == ans["id"])
            .first()
        )
        if existing:
            skipped += 1
            continue

        be = BehavioralExample(
            example_id=ans["id"],
            title=ans["title"],
            source_project=ans.get("source", "blog_proj"),
            principle_tags=json.dumps(
                ans.get("principle_tags", []), ensure_ascii=False
            ),
        )

        # Blog answers have their STAR content in the clustered questions file
        # We'll populate from existing_answers if available
        db.add(be)
        inserted += 1

    if not dry_run:
        db.flush()

    return {"inserted": inserted, "skipped": skipped}


def seed_existing_answer_content(
    db, questions_data: dict, dry_run: bool = False
) -> int:
    """Populate STAR content for blog-sourced examples from clustered questions data.

    Args:
        db: Database session.
        questions_data: Parsed bq_clustered_questions.json with existing_answers.
        dry_run: If True, don't commit.

    Returns:
        Number of examples updated.
    """
    updated = 0
    # Map question_id -> blog example_id
    blog_id_map = {
        "COL-1": "BLOG-01",
        "COL-2": "BLOG-02",
        "COL-3": "BLOG-03",
        "COL-4": "BLOG-04",
    }

    for ans in questions_data.get("existing_answers", []):
        blog_ex_id = blog_id_map.get(ans["question_id"])
        if not blog_ex_id:
            continue

        be = (
            db.query(BehavioralExample)
            .filter(BehavioralExample.example_id == blog_ex_id)
            .first()
        )
        if not be:
            continue

        answer = ans.get("answer", {})
        if answer:
            be.situation = answer.get("situation")
            be.task = answer.get("task")
            be.action = answer.get("action")
            be.result = answer.get("result")
            updated += 1

    if not dry_run:
        db.flush()

    return updated


def seed_links(db, examples_data: dict, dry_run: bool = False) -> dict:
    """Create cross-reference links between questions and examples.

    Args:
        db: Database session.
        examples_data: Parsed bq_behavioral_examples.json.
        dry_run: If True, don't commit.

    Returns:
        Dict with counts: inserted, skipped.
    """
    inserted = 0
    skipped = 0

    all_sources = list(examples_data["examples"]) + list(
        examples_data.get("blog_proj_existing_answers", [])
    )

    for source in all_sources:
        example_id_str = source["id"]
        be = (
            db.query(BehavioralExample)
            .filter(BehavioralExample.example_id == example_id_str)
            .first()
        )
        if not be:
            continue

        for xref in source.get("cross_references", []):
            q_id_str = xref["question_id"]
            bq = (
                db.query(BehavioralQuestion)
                .filter(BehavioralQuestion.question_id == q_id_str)
                .first()
            )
            if not bq:
                continue

            # Check for existing link
            existing = (
                db.query(QuestionExampleLink)
                .filter(
                    QuestionExampleLink.question_id == bq.id,
                    QuestionExampleLink.example_id == be.id,
                )
                .first()
            )
            if existing:
                skipped += 1
                continue

            link = QuestionExampleLink(
                question_id=bq.id,
                example_id=be.id,
                relevance_note=xref.get("relevance_note"),
            )
            db.add(link)
            inserted += 1

    if not dry_run:
        db.flush()

    return {"inserted": inserted, "skipped": skipped}


def main() -> None:
    """Run the behavioral questions seed script."""
    dry_run = "--dry-run" in sys.argv

    docs_dir = project_root / "docs"
    questions_path = docs_dir / "bq_clustered_questions.json"
    examples_path = docs_dir / "bq_behavioral_examples.json"

    if not questions_path.exists():
        print(f"[FAIL] Questions file not found: {questions_path}")
        sys.exit(1)
    if not examples_path.exists():
        print(f"[FAIL] Examples file not found: {examples_path}")
        sys.exit(1)

    questions_data = load_json(questions_path)
    examples_data = load_json(examples_path)

    print(f"[INFO] Loading from: {questions_path.name}, {examples_path.name}")
    print(f"[INFO] Dry run: {dry_run}")

    init_db()
    db = SessionLocal()

    try:
        # Step 1: Seed questions
        q_result = seed_questions(db, questions_data, dry_run)
        print(f"[DONE] Questions: {q_result}")

        # Step 2: Seed examples
        ex_result = seed_examples(db, examples_data, dry_run)
        print(f"[DONE] Examples: {ex_result}")

        # Step 3: Populate STAR content for blog answers
        updated = seed_existing_answer_content(db, questions_data, dry_run)
        print(f"[DONE] Blog answer content populated: {updated}")

        # Step 4: Create cross-reference links
        link_result = seed_links(db, examples_data, dry_run)
        print(f"[DONE] Links: {link_result}")

        if not dry_run:
            db.commit()
            print("[DONE] All data committed.")
        else:
            db.rollback()
            print("[INFO] Dry run - rolled back.")

        # Summary
        total_q = db.query(BehavioralQuestion).count()
        total_ex = db.query(BehavioralExample).count()
        total_links = db.query(QuestionExampleLink).count()
        print(f"\n[SUMMARY] DB state: {total_q} questions, {total_ex} examples, {total_links} links")

    except Exception as e:
        db.rollback()
        print(f"[FAIL] Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
