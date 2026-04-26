"""Seed BQ-TAX Phase 2 retag (T-P1-600 / BQ-TAX-03).

Three-part retag against the new themes/facets seeded by BQ-TAX-02
(``scripts/seed_bq_taxonomy_delta_20260421.py``):

1.  Mechanical migration: every row tagged with the legacy
    ``scope_creep_ambiguous`` theme gets a ``scope_creep_pm_ambiguity``
    facet tag added, and the legacy theme tag removed.

2.  New theme tagging: apply the two new themes
    (``customer_user_focus``, ``ethical_integrity_backbone``) across
    existing examples + questions per the per-row rationale documented
    in ``docs/bq_taxonomy_retag_log_20260421.md``.

3.  New facet tagging: apply the three cross-theme facets
    (``fast_learning``, ``scrappy_innovation``, ``strategic_scope``)
    across existing examples + questions per the same rationale doc.

After (1)-(3) verify zero rows still reference ``scope_creep_ambiguous``,
then drop the legacy theme so ``behavioral_themes`` row count goes
17 -> 16.

Idempotent:
  - Each tag insert is upsert-by-(parent_id, child_id). Re-runs print
    ``[SKIP]`` for already-present rows.
  - The legacy theme drop is conditional on its existence + zero
    referrers; re-run is a no-op once dropped.

DB-backup-guarded:
  Before any write, copies the target DB file to
  ``<db>.bak.<timestamp>_pre_bq_taxonomy_retag``. Skip via ``--no-backup``.

Usage:
    python scripts/seed_bq_taxonomy_retag_20260421.py [--no-backup]
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
from src.backend.models.behavioral import (  # noqa: E402
    BehavioralExample,
    BehavioralQuestion,
)
from src.backend.models.behavioral_facet import (  # noqa: E402
    BehavioralFacet,
    ExampleFacetTag,
    QuestionFacetTag,
)
from src.backend.models.behavioral_theme import (  # noqa: E402
    BehavioralTheme,
    ExampleThemeTag,
    QuestionThemeTag,
)

# ---------------------------------------------------------------------------
# Retag spec (per-row rationale lives in
# docs/bq_taxonomy_retag_log_20260421.md -- this dict is the executable
# manifestation of those decisions, treat the doc as source of truth).
# ---------------------------------------------------------------------------

LEGACY_THEME_SLUG = "scope_creep_ambiguous"
DEMOTE_FACET_SLUG = "scope_creep_pm_ambiguity"

# Examples that get the new themes (user-advocacy / backbone). Conservative.
EXAMPLE_NEW_THEME_TAGS: dict[str, list[str]] = {
    "EX-03": ["ethical_integrity_backbone"],
    "EX-04": ["customer_user_focus", "ethical_integrity_backbone"],
    "EX-07": ["customer_user_focus", "ethical_integrity_backbone"],
    "EX-08": ["ethical_integrity_backbone"],
    "EX-09": ["customer_user_focus"],
    "EX-09B": ["customer_user_focus"],
    "EX-13": ["ethical_integrity_backbone"],
    "EX-14": ["ethical_integrity_backbone"],
    "EX-15": ["ethical_integrity_backbone"],
    "EX-17": ["ethical_integrity_backbone"],
    "EX-18": ["ethical_integrity_backbone"],
    "EX-20": ["customer_user_focus", "ethical_integrity_backbone"],
    "EX-23": ["customer_user_focus"],
    "EX-24": ["customer_user_focus"],
    "EX-33": ["ethical_integrity_backbone"],
    "EX-34": ["customer_user_focus", "ethical_integrity_backbone"],
    "BLOG-04": ["ethical_integrity_backbone"],
}

# Examples that get the new facets (cross-theme capability/style/scope).
EXAMPLE_NEW_FACET_TAGS: dict[str, list[str]] = {
    "EX-06": ["scrappy_innovation", "strategic_scope"],
    "EX-07": ["scrappy_innovation"],
    "EX-08": ["strategic_scope"],
    "EX-09": ["scrappy_innovation"],
    "EX-09B": ["scrappy_innovation"],
    "EX-12": ["fast_learning"],
    "EX-12B": ["fast_learning", "scrappy_innovation", "strategic_scope"],
    "EX-13": ["strategic_scope"],
    "EX-14": ["fast_learning", "scrappy_innovation"],
    "EX-15": ["strategic_scope"],
    "EX-20": ["strategic_scope"],
    "EX-21": ["scrappy_innovation", "strategic_scope"],
    "EX-23": ["strategic_scope"],
    "EX-24": ["strategic_scope"],
    "EX-30": ["strategic_scope"],
    "EX-33": ["strategic_scope"],
    "EX-34": ["strategic_scope"],
}

# Questions that get the new themes.
QUESTION_NEW_THEME_TAGS: dict[str, list[str]] = {
    "COM-2": ["ethical_integrity_backbone"],
    "IMP-1": ["customer_user_focus"],
    "IMP-2": ["customer_user_focus"],
    "IMP-11": ["ethical_integrity_backbone"],
    "IMP-12": ["ethical_integrity_backbone"],
    "IMP-13": ["ethical_integrity_backbone"],
    "IMP-15": ["customer_user_focus", "ethical_integrity_backbone"],
}

# Questions that get the new facets.
QUESTION_NEW_FACET_TAGS: dict[str, list[str]] = {
    "ADP-1": ["fast_learning"],
    "OWN-9": ["scrappy_innovation"],
    "PS-2": ["scrappy_innovation"],
    "INN-2": ["scrappy_innovation"],
    "INN-4": ["scrappy_innovation"],
    "INN-7": ["strategic_scope"],
    "INN-9": ["scrappy_innovation"],
    "LDR-3": ["strategic_scope"],
    "IMP-7": ["strategic_scope"],
    "IMP-10": ["strategic_scope"],
}


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
    backup = db_path.with_name(f"{db_path.name}.bak.{ts}_pre_bq_taxonomy_retag")
    shutil.copy2(db_path, backup)
    return backup


# ---------------------------------------------------------------------------
# Tag upsert helpers
# ---------------------------------------------------------------------------


def _upsert_example_theme_tag(db, example_id: int, theme_id: int) -> bool:
    """Insert example->theme tag if absent. Returns True iff inserted."""
    existing = (
        db.query(ExampleThemeTag)
        .filter(
            ExampleThemeTag.example_id == example_id,
            ExampleThemeTag.theme_id == theme_id,
        )
        .first()
    )
    if existing is not None:
        return False
    db.add(ExampleThemeTag(example_id=example_id, theme_id=theme_id))
    db.flush()
    return True


def _upsert_question_theme_tag(db, question_id: int, theme_id: int) -> bool:
    """Insert question->theme tag if absent. Returns True iff inserted."""
    existing = (
        db.query(QuestionThemeTag)
        .filter(
            QuestionThemeTag.question_id == question_id,
            QuestionThemeTag.theme_id == theme_id,
        )
        .first()
    )
    if existing is not None:
        return False
    db.add(QuestionThemeTag(question_id=question_id, theme_id=theme_id))
    db.flush()
    return True


def _upsert_example_facet_tag(db, example_id: int, facet_id: int) -> bool:
    """Insert example->facet tag if absent. Returns True iff inserted."""
    existing = (
        db.query(ExampleFacetTag)
        .filter(
            ExampleFacetTag.example_id == example_id,
            ExampleFacetTag.facet_id == facet_id,
        )
        .first()
    )
    if existing is not None:
        return False
    db.add(ExampleFacetTag(example_id=example_id, facet_id=facet_id))
    db.flush()
    return True


def _upsert_question_facet_tag(db, question_id: int, facet_id: int) -> bool:
    """Insert question->facet tag if absent. Returns True iff inserted."""
    existing = (
        db.query(QuestionFacetTag)
        .filter(
            QuestionFacetTag.question_id == question_id,
            QuestionFacetTag.facet_id == facet_id,
        )
        .first()
    )
    if existing is not None:
        return False
    db.add(QuestionFacetTag(question_id=question_id, facet_id=facet_id))
    db.flush()
    return True


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------


def _theme_id_by_slug(db, slug: str) -> int:
    """Return theme.id by slug, raising on absence."""
    row = (
        db.query(BehavioralTheme).filter(BehavioralTheme.slug == slug).first()
    )
    if row is None:
        raise RuntimeError(
            f"Theme {slug!r} not found -- run seed_behavioral_themes.py "
            "and seed_bq_taxonomy_delta_20260421.py first."
        )
    return row.id


def _facet_id_by_slug(db, slug: str) -> int:
    """Return facet.id by slug, raising on absence."""
    row = (
        db.query(BehavioralFacet).filter(BehavioralFacet.slug == slug).first()
    )
    if row is None:
        raise RuntimeError(
            f"Facet {slug!r} not found -- run "
            "seed_bq_taxonomy_delta_20260421.py first."
        )
    return row.id


def _example_id_by_label(db, label: str) -> int:
    """Return behavioral_examples.id for example_id label, raising on absence."""
    row = (
        db.query(BehavioralExample)
        .filter(BehavioralExample.example_id == label)
        .first()
    )
    if row is None:
        raise RuntimeError(f"Example {label!r} not found in DB.")
    return row.id


def _question_id_by_label(db, label: str) -> int:
    """Return behavioral_questions.id for question_id label, raising on absence."""
    row = (
        db.query(BehavioralQuestion)
        .filter(BehavioralQuestion.question_id == label)
        .first()
    )
    if row is None:
        raise RuntimeError(f"Question {label!r} not found in DB.")
    return row.id


# ---------------------------------------------------------------------------
# Main retag routine
# ---------------------------------------------------------------------------


def retag() -> dict:
    """Run the three-part retag + legacy theme drop.

    Returns:
        Dict with per-step counters and post-run totals for AC verification.
    """
    engine = get_engine()
    init_db(engine)

    db = SessionLocal()
    try:
        counters: dict[str, int] = {
            "ex_theme_inserted": 0,
            "ex_theme_skipped": 0,
            "q_theme_inserted": 0,
            "q_theme_skipped": 0,
            "ex_facet_inserted": 0,
            "ex_facet_skipped": 0,
            "q_facet_inserted": 0,
            "q_facet_skipped": 0,
            "ex_legacy_migrated": 0,
            "ex_legacy_already": 0,
            "q_legacy_migrated": 0,
            "q_legacy_already": 0,
            "legacy_theme_dropped": 0,
        }

        # Part 1: Mechanical migration of scope_creep_ambiguous tags.
        legacy_theme = (
            db.query(BehavioralTheme)
            .filter(BehavioralTheme.slug == LEGACY_THEME_SLUG)
            .first()
        )
        demote_facet_id = _facet_id_by_slug(db, DEMOTE_FACET_SLUG)

        if legacy_theme is None:
            print(
                f"[SKIP] legacy theme {LEGACY_THEME_SLUG!r} already dropped"
                " -- migration is a no-op"
            )
        else:
            legacy_theme_id = legacy_theme.id

            ex_legacy_rows = (
                db.query(ExampleThemeTag)
                .filter(ExampleThemeTag.theme_id == legacy_theme_id)
                .all()
            )
            for tag in ex_legacy_rows:
                inserted = _upsert_example_facet_tag(
                    db, tag.example_id, demote_facet_id
                )
                if inserted:
                    counters["ex_legacy_migrated"] += 1
                else:
                    counters["ex_legacy_already"] += 1
                db.delete(tag)
            db.flush()

            q_legacy_rows = (
                db.query(QuestionThemeTag)
                .filter(QuestionThemeTag.theme_id == legacy_theme_id)
                .all()
            )
            for tag in q_legacy_rows:
                inserted = _upsert_question_facet_tag(
                    db, tag.question_id, demote_facet_id
                )
                if inserted:
                    counters["q_legacy_migrated"] += 1
                else:
                    counters["q_legacy_already"] += 1
                db.delete(tag)
            db.flush()

            print(
                f"[MIGRATE] examples: {counters['ex_legacy_migrated']} "
                f"new facet tags, {counters['ex_legacy_already']} "
                f"already-present (theme tag still removed)"
            )
            print(
                f"[MIGRATE] questions: {counters['q_legacy_migrated']} "
                f"new facet tags, {counters['q_legacy_already']} "
                f"already-present (theme tag still removed)"
            )

        # Part 2: New theme tagging (customer_user_focus / ethical_integrity_backbone).
        for label, slugs in EXAMPLE_NEW_THEME_TAGS.items():
            ex_id = _example_id_by_label(db, label)
            for slug in slugs:
                t_id = _theme_id_by_slug(db, slug)
                if _upsert_example_theme_tag(db, ex_id, t_id):
                    counters["ex_theme_inserted"] += 1
                    print(f"[DONE] example {label} += theme {slug!r}")
                else:
                    counters["ex_theme_skipped"] += 1

        for label, slugs in QUESTION_NEW_THEME_TAGS.items():
            q_id = _question_id_by_label(db, label)
            for slug in slugs:
                t_id = _theme_id_by_slug(db, slug)
                if _upsert_question_theme_tag(db, q_id, t_id):
                    counters["q_theme_inserted"] += 1
                    print(f"[DONE] question {label} += theme {slug!r}")
                else:
                    counters["q_theme_skipped"] += 1

        # Part 3: New facet tagging (fast_learning / scrappy_innovation / strategic_scope).
        for label, slugs in EXAMPLE_NEW_FACET_TAGS.items():
            ex_id = _example_id_by_label(db, label)
            for slug in slugs:
                f_id = _facet_id_by_slug(db, slug)
                if _upsert_example_facet_tag(db, ex_id, f_id):
                    counters["ex_facet_inserted"] += 1
                    print(f"[DONE] example {label} += facet {slug!r}")
                else:
                    counters["ex_facet_skipped"] += 1

        for label, slugs in QUESTION_NEW_FACET_TAGS.items():
            q_id = _question_id_by_label(db, label)
            for slug in slugs:
                f_id = _facet_id_by_slug(db, slug)
                if _upsert_question_facet_tag(db, q_id, f_id):
                    counters["q_facet_inserted"] += 1
                    print(f"[DONE] question {label} += facet {slug!r}")
                else:
                    counters["q_facet_skipped"] += 1

        # Part 4: Drop the legacy theme once references are zero.
        if legacy_theme is not None:
            remaining_ex = (
                db.query(ExampleThemeTag)
                .filter(ExampleThemeTag.theme_id == legacy_theme.id)
                .count()
            )
            remaining_q = (
                db.query(QuestionThemeTag)
                .filter(QuestionThemeTag.theme_id == legacy_theme.id)
                .count()
            )
            if remaining_ex == 0 and remaining_q == 0:
                db.delete(legacy_theme)
                db.flush()
                counters["legacy_theme_dropped"] = 1
                print(f"[DROP] theme {LEGACY_THEME_SLUG!r} (0 referrers)")
            else:
                raise RuntimeError(
                    f"Refusing to drop {LEGACY_THEME_SLUG!r}: still has "
                    f"{remaining_ex} example refs + {remaining_q} question refs."
                )

        db.commit()

        # Post-run totals for AC gates.
        counters["themes_total"] = db.query(BehavioralTheme).count()
        counters["facets_total"] = db.query(BehavioralFacet).count()
        counters["legacy_theme_refs_remaining"] = (
            1 if (
                db.query(BehavioralTheme)
                .filter(BehavioralTheme.slug == LEGACY_THEME_SLUG)
                .first()
                is not None
            ) else 0
        )
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

    report = retag()

    print()
    print("=" * 60)
    print("BQ-TAX Phase 2 retag report")
    print("=" * 60)
    print(
        f"Example theme tags inserted: {report['ex_theme_inserted']} "
        f"(skipped {report['ex_theme_skipped']})"
    )
    print(
        f"Question theme tags inserted: {report['q_theme_inserted']} "
        f"(skipped {report['q_theme_skipped']})"
    )
    print(
        f"Example facet tags inserted: {report['ex_facet_inserted']} "
        f"(skipped {report['ex_facet_skipped']})"
    )
    print(
        f"Question facet tags inserted: {report['q_facet_inserted']} "
        f"(skipped {report['q_facet_skipped']})"
    )
    print(
        f"Legacy example tags migrated: {report['ex_legacy_migrated']} "
        f"(facet already-present {report['ex_legacy_already']})"
    )
    print(
        f"Legacy question tags migrated: {report['q_legacy_migrated']} "
        f"(facet already-present {report['q_legacy_already']})"
    )
    print(f"Legacy theme dropped this run: {report['legacy_theme_dropped']}")
    print(f"behavioral_themes row count: {report['themes_total']}")
    print(f"behavioral_facets row count: {report['facets_total']}")

    # AC gates:
    #  - themes_total == 16 (17 -> 16 once legacy dropped)
    #  - legacy theme has 0 referrers + has been dropped
    ok = (
        report["themes_total"] == 16
        and report["legacy_theme_refs_remaining"] == 0
    )
    if ok:
        print("[OK] AC gates met (themes==16, legacy theme dropped).")
        return 0
    print(
        f"[FAIL] AC gates NOT met: themes={report['themes_total']} "
        f"(want 16), legacy_remaining={report['legacy_theme_refs_remaining']} "
        "(want 0)."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
