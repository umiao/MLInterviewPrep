"""Populate interview-harmful-content-detection system design (4 sections).

Content covers a Meta-classic Trust & Safety interview topic: Design a Harmful
Content Detection System -- multi-stage pipeline (edge filter -> ML classifier
-> human review -> appeal/feedback -> retraining loop), multi-modal fusion,
adversarial robustness, fairness, and reviewer wellness.

This is a REVIEW-PROMPT GRADE module (4 sections only: overview / architecture
/ tradeoffs / defense). Other 4 columns intentionally left NULL.

Idempotent: creates record if missing, overwrites the 4 sections it owns.
"""
import re
import sys
from pathlib import Path

_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.system_design import SystemDesign  # noqa: E402

SLUG = "interview-harmful-content-detection"
TITLE = "Design a Harmful Content Detection System"
DISPLAY_ORDER = 120

_STAGING_DIR = Path(__file__).resolve().parent.parent / "docs" / "staging" / "generated" / "system_designs"
_STAGING_PREFIX = "interview_harmful_content_detection"

_SECTION_FILES = {
    "overview": f"{_STAGING_PREFIX}__overview.md",
    "architecture": f"{_STAGING_PREFIX}__architecture.md",
    "tradeoffs": f"{_STAGING_PREFIX}__tradeoffs.md",
    "defense": f"{_STAGING_PREFIX}__defense.md",
}

_FRONTMATTER_RE = re.compile(r"^---\n.*?\n---\n", re.DOTALL)


def _load_section(filename: str) -> str:
    """Read a staging .md file and strip the YAML frontmatter."""
    path = _STAGING_DIR / filename
    text = path.read_text(encoding="utf-8")
    body = _FRONTMATTER_RE.sub("", text, count=1)
    return body.strip() + "\n"


def populate_interview_harmful_content_detection() -> None:
    """Create or update the interview-harmful-content-detection record (4 sections)."""
    init_db()
    db = SessionLocal()

    sections = {name: _load_section(fn) for name, fn in _SECTION_FILES.items()}

    try:
        record = (
            db.query(SystemDesign)
            .filter(SystemDesign.slug == SLUG)
            .first()
        )

        if record is None:
            record = SystemDesign(
                slug=SLUG,
                title=TITLE,
                display_order=DISPLAY_ORDER,
            )
            db.add(record)
            db.flush()
            print(f"[DONE] Created SystemDesign record: slug='{SLUG}', title='{TITLE}'")
        else:
            print(f"[INFO] Found existing record for slug='{SLUG}', updating...")
            record.title = TITLE
            record.display_order = DISPLAY_ORDER

        record.overview = sections["overview"]
        record.architecture = sections["architecture"]
        record.tradeoffs = sections["tradeoffs"]
        record.defense = sections["defense"]

        db.commit()
        print(f"[DONE] Updated 4 sections for '{SLUG}'.")

        db.refresh(record)
        for name in ("overview", "architecture", "tradeoffs", "defense"):
            length = len(getattr(record, name) or "")
            status = "[OK]" if length > 100 else "[WARN] short"
            print(f"  {status} {name}: {length} chars")

        chinese_pattern = re.compile(r"[一-鿿]")
        for name in ("overview", "architecture", "tradeoffs", "defense"):
            content = getattr(record, name) or ""
            if chinese_pattern.search(content):
                print(f"  [OK] {name}: Chinese chars present")
            else:
                print(f"  [WARN] {name}: No Chinese chars found!")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    populate_interview_harmful_content_detection()
