"""Seed BQ-TAX Phase 2 taxonomy delta (T-P1-599).

Adds the reviewer-approved delta on top of the BQ-TAX-01 schema:

- 2 new themes appended after display_order 15 (current tail
  ``oncall_prod_incident``):
    - ``customer_user_focus`` / 'Customer & User Focus' (display_order 16)
    - ``ethical_integrity_backbone`` / 'Ethical Integrity & Backbone'
      (display_order 17)

- 4 new facets:
    - ``fast_learning`` (parent_theme_id NULL -- cross-theme capability tag)
    - ``scrappy_innovation`` (parent_theme_id NULL -- solution-style tag)
    - ``strategic_scope`` (parent_theme_id NULL -- staff/L6 signal tag)
    - ``scope_creep_pm_ambiguity`` (parent_theme_id = id of
      ``ambiguity_uncertainty`` theme -- scenario sub-type, demotes the
      legacy ``scope_creep_ambiguous`` theme)

The legacy ``scope_creep_ambiguous`` theme (display_order 12) is NOT deleted
in this script. Per Phase 2 scope, we keep the row + its existing tags so
retag work (BQ-TAX-03) can port references gradually. Phase 3 will drop
the legacy theme once all tags are migrated.

Idempotent:
  - Themes: upsert by slug. Pre-existing row -> refresh label/description/
    display_order; no duplicate insert.
  - Facets: upsert by slug. Pre-existing row -> refresh label/description/
    parent_theme_id/display_order; no duplicate insert.
  - Re-run prints ``[SKIP]`` for every untouched row. 2nd invocation is a
    full no-op (0 themes inserted, 0 facets inserted).

DB-backup-guarded:
  Before any write, copies the target DB to
  ``<db>.bak.<timestamp>_pre_bq_taxonomy_delta``. Skip via ``--no-backup``.

Usage:
    python scripts/seed_bq_taxonomy_delta_20260421.py [--no-backup]
"""
from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.backend.database import SessionLocal, get_engine, init_db  # noqa: E402
from src.backend.models.behavioral_facet import BehavioralFacet  # noqa: E402
from src.backend.models.behavioral_theme import BehavioralTheme  # noqa: E402

# ---------------------------------------------------------------------------
# Delta spec (reviewer-approved 2026-04-21)
# ---------------------------------------------------------------------------

NEW_THEMES: list[dict] = [
    {
        "slug": "customer_user_focus",
        "label": "Customer & User Focus",
        "display_order": 16,
        "description": (
            "Stories whose narrative axis is doing the right thing for the "
            "user/customer (Amazon Customer Obsession, Meta Move Fast For "
            "Users, Google Focus on the User). Primary signal: the decision "
            "hinged on user impact rather than internal metrics or team "
            "convenience."
        ),
    },
    {
        "slug": "ethical_integrity_backbone",
        "label": "Ethical Integrity & Backbone",
        "display_order": 17,
        "description": (
            "Stories driven by integrity, ethical stance, or disagree-not-"
            "just-commit backbone -- pushing back even at personal or "
            "political cost. Distinct from conflict_disagreement (which is "
            "about navigating interpersonal tension) by requiring a real "
            "ethical / values-based stake."
        ),
    },
]

# Facet spec: parent_theme_slug=None means cross-theme (parent_theme_id NULL)
NEW_FACETS: list[dict] = [
    {
        "slug": "fast_learning",
        "label": "Fast Learning",
        "parent_theme_slug": None,
        "display_order": 1,
        "description": (
            "Cross-theme capability tag (reviewer note: learning is a "
            "capability, not a scenario -- must be an independent retrieval "
            "axis). Applied when the signal is time-to-productivity or "
            "ramp-up speed in a new domain/stack/role."
        ),
    },
    {
        "slug": "scrappy_innovation",
        "label": "Scrappy Innovation",
        "parent_theme_slug": None,
        "display_order": 2,
        "description": (
            "Cross-theme solution-style tag (reviewer note: solution style, "
            "not scenario). Applied when the story centers on achieving "
            "disproportionate impact with small resources / unorthodox "
            "approach (bias-for-action, invent-and-simplify adjacent)."
        ),
    },
    {
        "slug": "strategic_scope",
        "label": "Strategic / Org-Level Scope",
        "parent_theme_slug": None,
        "display_order": 3,
        "description": (
            "Staff/L6 signal tag (reviewer note: not a theme -- do NOT "
            "split leadership_direction). Applied when the scope of impact "
            "crosses multiple orgs, shapes multi-quarter strategy, or "
            "influences C-level / VP decisions."
        ),
    },
    {
        "slug": "scope_creep_pm_ambiguity",
        "label": "Scope Creep / PM Ambiguity",
        "parent_theme_slug": "ambiguity_uncertainty",
        "display_order": 4,
        "description": (
            "Scenario sub-type of ambiguity_uncertainty (reviewer note: "
            "demoting legacy ``scope_creep_ambiguous`` theme -- scenario "
            "vs capability cannot be bundled into one theme). Applied when "
            "the story hinges on shifting requirements, rescoping, or "
            "unclear PM/stakeholder asks."
        ),
    },
]


# ---------------------------------------------------------------------------
# DB-file backup
# ---------------------------------------------------------------------------


def _backup_db(db_path: Path) -> Path | None:
    """Copy the DB file to a timestamped ``.bak`` before mutating.

    Args:
        db_path: Absolute path to the SQLite DB file.

    Returns:
        Path to the backup file, or ``None`` if the source does not exist.
    """
    if not db_path.exists():
        return None
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = db_path.with_name(f"{db_path.name}.bak.{ts}_pre_bq_taxonomy_delta")
    shutil.copy2(db_path, backup)
    return backup


# ---------------------------------------------------------------------------
# Upsert helpers
# ---------------------------------------------------------------------------


def _upsert_theme(db, spec: dict) -> tuple[BehavioralTheme, bool]:
    """Insert-or-refresh a theme by slug.

    Args:
        db: SQLAlchemy session.
        spec: Theme spec dict with keys slug/label/display_order/description.

    Returns:
        Tuple of (theme row, inserted_flag). inserted_flag is True iff a new
        row was created this run.
    """
    existing = (
        db.query(BehavioralTheme)
        .filter(BehavioralTheme.slug == spec["slug"])
        .first()
    )
    if existing is not None:
        existing.label = spec["label"]
        existing.description = spec["description"]
        existing.display_order = spec["display_order"]
        return existing, False
    row = BehavioralTheme(
        slug=spec["slug"],
        label=spec["label"],
        description=spec["description"],
        display_order=spec["display_order"],
    )
    db.add(row)
    db.flush()
    return row, True


def _upsert_facet(
    db,
    spec: dict,
    slug_to_theme: dict[str, BehavioralTheme],
) -> tuple[BehavioralFacet, bool]:
    """Insert-or-refresh a facet by slug.

    Args:
        db: SQLAlchemy session.
        spec: Facet spec dict with keys slug/label/parent_theme_slug/
            display_order/description.
        slug_to_theme: Map of theme slug -> BehavioralTheme row, for parent
            resolution.

    Returns:
        Tuple of (facet row, inserted_flag).
    """
    parent_slug = spec["parent_theme_slug"]
    if parent_slug is None:
        parent_id: int | None = None
    else:
        parent_row = slug_to_theme.get(parent_slug)
        if parent_row is None:
            parent_row = (
                db.query(BehavioralTheme)
                .filter(BehavioralTheme.slug == parent_slug)
                .first()
            )
        if parent_row is None:
            raise RuntimeError(
                f"Facet {spec['slug']!r} references missing parent theme "
                f"{parent_slug!r} -- run seed_behavioral_themes.py first."
            )
        parent_id = parent_row.id

    existing = (
        db.query(BehavioralFacet)
        .filter(BehavioralFacet.slug == spec["slug"])
        .first()
    )
    if existing is not None:
        existing.label = spec["label"]
        existing.description = spec["description"]
        existing.parent_theme_id = parent_id
        existing.display_order = spec["display_order"]
        return existing, False
    row = BehavioralFacet(
        slug=spec["slug"],
        label=spec["label"],
        parent_theme_id=parent_id,
        description=spec["description"],
        display_order=spec["display_order"],
    )
    db.add(row)
    db.flush()
    return row, True


# ---------------------------------------------------------------------------
# Main seed routine
# ---------------------------------------------------------------------------


def seed() -> dict:
    """Apply the Phase 2 delta. Returns counter dict for verification.

    Returns:
        Dict with counts ``themes_inserted``, ``themes_skipped``,
        ``facets_inserted``, ``facets_skipped``, plus the resulting totals
        ``themes_total`` and ``facets_total``.
    """
    engine = get_engine()
    init_db(engine)

    db = SessionLocal()
    try:
        counters = {
            "themes_inserted": 0,
            "themes_skipped": 0,
            "facets_inserted": 0,
            "facets_skipped": 0,
        }

        slug_to_theme: dict[str, BehavioralTheme] = {}
        for spec in NEW_THEMES:
            row, inserted = _upsert_theme(db, spec)
            slug_to_theme[spec["slug"]] = row
            if inserted:
                print(f"[DONE] inserted theme {spec['slug']!r}")
                counters["themes_inserted"] += 1
            else:
                print(f"[SKIP] theme {spec['slug']!r} already exists")
                counters["themes_skipped"] += 1

        for spec in NEW_FACETS:
            row, inserted = _upsert_facet(db, spec, slug_to_theme)
            if inserted:
                parent_desc = (
                    f"parent={spec['parent_theme_slug']!r}"
                    if spec["parent_theme_slug"] is not None
                    else "parent=NULL (cross-theme)"
                )
                print(f"[DONE] inserted facet {spec['slug']!r} {parent_desc}")
                counters["facets_inserted"] += 1
            else:
                print(f"[SKIP] facet {spec['slug']!r} already exists")
                counters["facets_skipped"] += 1

        db.commit()

        counters["themes_total"] = db.query(BehavioralTheme).count()
        counters["facets_total"] = db.query(BehavioralFacet).count()
        return counters
    finally:
        db.close()


def _resolve_db_file() -> Path | None:
    """Resolve the SQLite DB file path that the SQLAlchemy engine binds to.

    Returns:
        Absolute Path to the DB file if the engine URL is a ``sqlite://``
        file URL, else ``None`` (e.g. in-memory DB during tests).
    """
    engine = get_engine()
    url = engine.url
    if url.drivername != "sqlite":
        return None
    if url.database in (None, "", ":memory:"):
        return None
    return Path(url.database).resolve()


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip pre-seed DB-file backup",
    )
    args = parser.parse_args(argv)

    if not args.no_backup:
        db_file = _resolve_db_file()
        if db_file is not None:
            bkp = _backup_db(db_file)
            if bkp is not None:
                print(f"[BACKUP] {bkp.name}")
        else:
            print("[BACKUP] skipped -- non-file DB URL")

    report = seed()

    print()
    print("=" * 60)
    print("BQ-TAX Phase 2 delta seed report")
    print("=" * 60)
    print(f"Themes inserted this run: {report['themes_inserted']}")
    print(f"Themes skipped (already present): {report['themes_skipped']}")
    print(f"Facets inserted this run: {report['facets_inserted']}")
    print(f"Facets skipped (already present): {report['facets_skipped']}")
    print(f"behavioral_themes row count: {report['themes_total']}")
    print(f"behavioral_facets row count: {report['facets_total']}")

    # AC gates: after first run, totals must be >= 17 themes and >= 4 facets.
    ok = report["themes_total"] >= 17 and report["facets_total"] >= 4
    if ok:
        print("[OK] AC totals met (themes >= 17, facets >= 4).")
        return 0
    print("[FAIL] AC totals NOT met.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
