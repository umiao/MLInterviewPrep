"""Reassign display_order for the Meta-MLSD golden family into the ml-mlsd tab window.

Task: T-P0-906 (GAP A visibility, SCHEME B user-approved 2026-05-16).

The ml-mlsd frontend tab filters modules by ``display_order in [130, 199)``
(``SystemDesignList.tsx:360``). Before this seed, only sd41-44 (the four
quality-leading goldens) lived in that window at 130-133; sd45-53 were
stranded at 207-260, so the tab showed 4 of the 13-题 family instead of 13.

SCHEME B keeps sd41-44 at 130-133 UNCHANGED (quality-leading at the front)
and appends sd45-53 into 134-142 ordered by the doc-96 / cd94 Question-card
number ascending (Q2, Q4, Q5, Q6, Q8, Q9, Q10, Q11, Q12 -- Q1/Q3/Q7/Q13 are
the four already at front).

Q -> slug mapping verified against company_documents id=94
([Meta-MLSD] Family Taxonomy + 13 Question Cards) before write:

  disp  id    slug                          Q     status
  130   sd41  meta-reels-golden             Q13   assert-unchanged
  131   sd42  meta-top3-comments-golden     Q1    assert-unchanged
  132   sd43  meta-weapon-ads-golden        Q7    assert-unchanged
  133   sd44  meta-friend-rec-golden        Q3    assert-unchanged
  134   sd50  meta-v2v-search-golden        Q2    reorder
  135   sd49  meta-ads-golden               Q4    reorder
  136   sd51  meta-event-rec-golden         Q5    reorder
  137   sd52  meta-location-rec-golden      Q6    reorder
  138   sd46  meta-yelp-restaurant-golden   Q8    reorder
  139   sd45  meta-fb-newsfeed-golden       Q9    reorder
  140   sd47  meta-ig-story-golden          Q10   reorder
  141   sd53  meta-spotify-music-golden     Q11   reorder
  142   sd48  meta-event-attendance-golden  Q12   reorder

Idempotent: sets exact targets keyed on slug, safe to re-run (re-run = no-op).
The ``insert_meta_*`` scripts are skip-if-exists, so this reorder seed is the
authoritative source of truth for these rows' display_order going forward
(same contract as scripts/reorder_pinterest_to_bottom_20260501.py).

A post-write self-check hard-fails (exit 2) if any AC is violated:
  * the ml-mlsd window [130, 199) does not contain exactly 13 rows
  * sd41-44 are not exactly at 130-133
  * the 13 rows are not the expected slugs in the expected order
  * any collision with the interview window (<130) or Pinterest (>=199)
"""
from __future__ import annotations

import sys
from pathlib import Path

_root = str(Path(__file__).resolve().parent.parent)
if _root not in sys.path:
    sys.path.insert(0, _root)

from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.system_design import SystemDesign  # noqa: E402

WINDOW_LO = 130
WINDOW_HI = 199  # half-open: [130, 199)

# slug -> target display_order for the 9 rows this seed moves (sd45-53).
REORDER = {
    "meta-v2v-search-golden": 134,       # sd50  Q2
    "meta-ads-golden": 135,              # sd49  Q4
    "meta-event-rec-golden": 136,        # sd51  Q5
    "meta-location-rec-golden": 137,     # sd52  Q6
    "meta-yelp-restaurant-golden": 138,  # sd46  Q8
    "meta-fb-newsfeed-golden": 139,      # sd45  Q9
    "meta-ig-story-golden": 140,         # sd47  Q10
    "meta-spotify-music-golden": 141,    # sd53  Q11
    "meta-event-attendance-golden": 142, # sd48  Q12
}

# slug -> required (unchanged) display_order for the 4 quality-leading rows.
KEEP_UNCHANGED = {
    "meta-reels-golden": 130,          # sd41  Q13
    "meta-top3-comments-golden": 131,  # sd42  Q1
    "meta-weapon-ads-golden": 132,     # sd43  Q7
    "meta-friend-rec-golden": 133,     # sd44  Q3
}

# Full expected window contents after the write: disp -> slug, ascending.
EXPECTED_WINDOW = sorted(
    [(v, k) for k, v in {**KEEP_UNCHANGED, **REORDER}.items()]
)


def _self_check(db) -> None:
    """Assert all T-P0-906 acceptance criteria; raise SystemExit(2) on failure."""
    errors: list[str] = []

    # AC: sd41-44 must be exactly at 130-133 (we never write them; verify).
    for slug, want in KEEP_UNCHANGED.items():
        row = db.query(SystemDesign).filter(SystemDesign.slug == slug).first()
        if row is None:
            errors.append(f"KEEP slug missing: {slug}")
        elif row.display_order != want:
            errors.append(
                f"KEEP {slug}: display_order={row.display_order}, expected {want} (must stay unchanged)"
            )

    # AC: the ml-mlsd window [130, 199) returns exactly the 13 expected rows in order.
    window = (
        db.query(SystemDesign)
        .filter(
            SystemDesign.display_order >= WINDOW_LO,
            SystemDesign.display_order < WINDOW_HI,
        )
        .order_by(SystemDesign.display_order)
        .all()
    )
    got = [(r.display_order, r.slug) for r in window]
    if len(got) != 13:
        errors.append(f"window [130,199) has {len(got)} rows, expected 13: {got}")
    if got != EXPECTED_WINDOW:
        errors.append(f"window contents mismatch:\n  got={got}\n  exp={EXPECTED_WINDOW}")

    # AC: no collision -- none of the family slugs may sit in interview (<130)
    # or Pinterest (>=199) windows.
    family = set(KEEP_UNCHANGED) | set(REORDER)
    for r in db.query(SystemDesign).filter(SystemDesign.slug.in_(family)).all():
        if not (WINDOW_LO <= r.display_order < WINDOW_HI):
            errors.append(
                f"COLLISION {r.slug}: display_order={r.display_order} outside [130,199)"
            )

    if errors:
        print("[FAIL] self-check failed:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        raise SystemExit(2)
    print("[OK] self-check passed: ml-mlsd window [130,199) = 13 rows, "
          "sd41-44 unchanged at 130-133, no interview/Pinterest collision.")


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        changed = 0
        for slug, target in REORDER.items():
            row = db.query(SystemDesign).filter(SystemDesign.slug == slug).first()
            if row is None:
                print(f"[WARN] missing slug: {slug}")
                continue
            if row.display_order == target:
                print(f"[NOOP] {slug}: already at {target}")
                continue
            print(f"[UPDATE] {slug}: {row.display_order} -> {target}")
            row.display_order = target
            changed += 1
        db.commit()
        print(f"[DONE] reordered {changed} Meta-MLSD modules into [130,199).")
        _self_check(db)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
