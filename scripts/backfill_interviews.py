"""One-shot backfill: create Company records, link events, import prep notes.

Invalidates TTS caches when prep_notes change so audio is regenerated
with the latest content.
"""
import sys
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import text  # noqa: E402

from src.backend.database import SessionLocal, get_engine, init_db  # noqa: E402
from src.backend.models.reading import AudioCache, TTSSummary  # noqa: E402
from src.backend.models.timeline import InterviewEvent  # noqa: E402
from src.backend.services.company_service import get_or_create_company  # noqa: E402

PREP_NOTES_PATH = Path(
    r"C:\Users\Shenghui Xu\Desktop\2026 跳槽准备"
    r"\2026_03_15_LinkedIn_HR_Call\linkedin_hr_call_prep.md"
)


def _invalidate_tts_cache(db: "Session", content_type: str, content_id: int) -> None:  # type: ignore[name-defined]  # noqa: F821
    """Delete TTS summary and audio cache rows for a content item.

    Args:
        db: Database session.
        content_type: The content type string.
        content_id: The content item's primary key.
    """
    tts_deleted = (
        db.query(TTSSummary)
        .filter(TTSSummary.content_type == content_type, TTSSummary.content_id == content_id)
        .delete()
    )
    audio_deleted = (
        db.query(AudioCache)
        .filter(AudioCache.content_type == content_type, AudioCache.content_id == content_id)
        .delete()
    )
    print(f"  TTS cache invalidated: {tts_deleted} summaries, {audio_deleted} audio files deleted")


def main() -> None:
    """Run the backfill."""
    engine = get_engine("sqlite:///data/mle_prep.db")
    init_db(engine)

    db = SessionLocal()
    try:
        # 1. Create companies
        linkedin = get_or_create_company("LinkedIn", db)
        doordash = get_or_create_company("DoorDash", db)
        db.commit()
        print(f"Companies: LinkedIn id={linkedin.id}, DoorDash id={doordash.id}")

        # 2. Import prep notes for LinkedIn
        prep_text = PREP_NOTES_PATH.read_text(encoding="utf-8")
        if linkedin.prep_notes == prep_text:
            print("LinkedIn prep_notes already up to date, skipping.")
        else:
            linkedin.prep_notes = prep_text
            db.commit()
            print(f"LinkedIn prep_notes: {len(prep_text)} chars imported")
            # Invalidate stale TTS caches for this content
            _invalidate_tts_cache(db, "prep_notes", linkedin.id)
            db.commit()

        # 3. Link existing events to companies
        events = db.query(InterviewEvent).all()
        for event in events:
            if event.company_name.lower() == "linkedin":
                event.company_id = linkedin.id
            elif event.company_name.lower() == "doordash":
                event.company_id = doordash.id
        db.commit()
        print(f"Updated {len(events)} events with company_id")

        # 4. Verify
        print("\n=== Verification ===")
        for row in db.execute(
            text("SELECT id, name, prep_notes IS NOT NULL FROM companies")
        ):
            print(f"  Company: id={row[0]}, name={row[1]}, has_prep_notes={bool(row[2])}")
        for row in db.execute(
            text("SELECT id, company_name, company_id FROM interview_events")
        ):
            print(f"  Event: id={row[0]}, company={row[1]}, company_id={row[2]}")

        print("\n[DONE] Backfill complete.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
