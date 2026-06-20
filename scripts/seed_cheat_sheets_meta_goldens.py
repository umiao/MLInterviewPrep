"""Seed (T-P1-924): write Meta-golden cheat sheets from drafts into system_designs.

Reads the git-tracked, human-reviewed cheat-sheet drafts in
``scripts/cheatsheet_drafts/<slug>.md`` and upserts each into
``system_designs.cheat_sheet`` (matched by slug). Deterministic and idempotent:
a row is only written when its stored cheat_sheet differs from the draft, so a
rerun with unchanged drafts reports 0 updated.

The drafts are produced by ``scripts/gen_cheat_sheets_meta_goldens.py`` (the
DeepSeek authoring aid, supervised-only). This seed has NO DeepSeek dependency
and is safe to run in any environment -- the drafts are the source of truth.

Run::

    python scripts/seed_cheat_sheets_meta_goldens.py
    python scripts/seed_cheat_sheets_meta_goldens.py --dry-run
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.system_design import SystemDesign  # noqa: E402

_DRAFTS = Path(__file__).resolve().parent / "cheatsheet_drafts"

# Allowlist: only these 9 Meta-golden slugs may be written by this seed. Guards
# against a stray .md in the drafts dir clobbering an unrelated row.
ALLOWED_SLUGS: frozenset[str] = frozenset(
    {
        "meta-v2v-search-golden",
        "meta-ads-golden",
        "meta-event-rec-golden",
        "meta-location-rec-golden",
        "meta-yelp-restaurant-golden",
        "meta-fb-newsfeed-golden",
        "meta-ig-story-golden",
        "meta-spotify-music-golden",
        "meta-event-attendance-golden",
    }
)


def _load_drafts() -> dict[str, str]:
    """Map slug -> cheat-sheet markdown from scripts/cheatsheet_drafts/*.md."""
    out: dict[str, str] = {}
    for md in sorted(_DRAFTS.glob("*.md")):
        slug = md.stem
        if slug not in ALLOWED_SLUGS:
            print(f"[skip] {md.name}: not an allowed Meta-golden slug")
            continue
        text = md.read_text(encoding="utf-8").strip()
        if text:
            out[slug] = text
    return out


def seed_meta_golden_cheat_sheets(dry_run: bool = False) -> dict[str, int]:
    """Upsert cheat sheets from drafts. Returns counts of updated/unchanged/missing."""
    drafts = _load_drafts()
    init_db()
    db = SessionLocal()
    updated = 0
    unchanged = 0
    missing = 0
    try:
        for slug, content in drafts.items():
            row = (
                db.query(SystemDesign)
                .filter(SystemDesign.slug == slug)
                .first()
            )
            if row is None:
                print(f"[missing] no system_designs row for slug {slug!r}")
                missing += 1
                continue
            if (row.cheat_sheet or "").strip() == content.strip():
                unchanged += 1
                continue
            print(
                f"[{'would-update' if dry_run else 'update'}] {slug} "
                f"({len(content)} chars)"
            )
            if not dry_run:
                row.cheat_sheet = content
            updated += 1
        if not dry_run:
            db.commit()
        else:
            db.rollback()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
    return {"updated": updated, "unchanged": unchanged, "missing": missing}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--dry-run", action="store_true", help="report changes without writing"
    )
    args = ap.parse_args()
    result = seed_meta_golden_cheat_sheets(dry_run=args.dry_run)
    print(
        f"Seed {'(dry-run) ' if args.dry_run else ''}complete: "
        f"{result['updated']} updated, {result['unchanged']} unchanged, "
        f"{result['missing']} missing."
    )
