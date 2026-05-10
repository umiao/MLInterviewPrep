"""[T-P1-796 / KG-INT A1] has_meaningful_note composite-threshold rule.

Single source of truth for the per-company "red dot" predicate consumed by
GET /companies (T-P1-796) and the Companies.tsx red-dot indicator
(T-P1-797). Cutoffs and placeholder heuristic come from the EDA in
docs/audit/red_dot_threshold_eda_2026-05-10.md (T-P1-795).

The 6 surfaces under consideration come from the Surface Identification
table in CLAUDE.md (any new per-company note surface added in the future
must be added BOTH here and to the SQL view ``company_meaningful_note_v``
in ``src.backend.database._create_views`` -- see "add new surface here"
anchors in both files).
"""
from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session

# Placeholder-shape heuristic mirrors scripts/_eda_red_dot_threshold_2026-05-10.py
# (T-P1-795). Both Python and SQL paths use the SAME pattern set; if these change,
# update BOTH:
#   - PLACEHOLDER_PATTERNS below
#   - the LIKE-clause string in src.backend.database._create_views
PLACEHOLDER_PATTERNS: tuple[str, ...] = (
    "tbd",
    "todo",
    "to do",
    "n/a",
    "na",
    "placeholder",
    "stub",
    "fill me in",
    "fill in",
    "[ ]",
    "lorem ipsum",
)

# Per-surface byte cutoffs from EDA recommendation table.
# add new surface here (also extend RED_DOT_CUTOFFS, the per-surface query
# in compute_meaningful_note_map, and the SQL view).
RED_DOT_CUTOFFS: dict[str, int] = {
    "companies.prep_notes": 50,
    "companies.notes": 50,
    "company_documents.content": 100,
    "problem_company_tags.notes": 20,
    "node_company_tags.notes": 20,
    "behavioral_example_company_tags.notes": 20,
}


def is_placeholder(value: str | None) -> bool:
    """Return True if ``value`` is empty/whitespace/short/placeholder-shaped.

    Mirrors the EDA heuristic in scripts/_eda_red_dot_threshold_2026-05-10.py:

    - ``None`` or whitespace-only -> placeholder
    - ``len(stripped) < 5`` -> placeholder (too short to carry signal)
    - ``len(stripped) < 80`` AND any PLACEHOLDER_PATTERNS substring -> placeholder
    - Otherwise -> real (a long body containing a stray "TODO" still counts as real)
    """
    if value is None:
        return True
    stripped = value.strip()
    if not stripped:
        return True
    if len(stripped) < 5:
        return True
    lowered = stripped.lower()
    return len(stripped) < 80 and any(p in lowered for p in PLACEHOLDER_PATTERNS)


def _is_meaningful(value: str | None, cutoff: int) -> bool:
    """True iff ``value`` is non-placeholder AND ``len >= cutoff``."""
    if is_placeholder(value):
        return False
    # is_placeholder guarantees value is non-None and non-empty here.
    assert value is not None
    return len(value) >= cutoff


def compute_meaningful_note_map(db: Session) -> dict[int, bool]:
    """Compute ``has_meaningful_note`` for every company in one batch.

    Returns a ``{company_id: bool}`` map covering every row in ``companies``
    (companies with no surface contribution map to ``False``). Single-pass
    over the 6 surfaces; suitable for the GET /companies list endpoint where
    per-company queries would be O(N*6).
    """
    results: dict[int, bool] = {}

    # Seed all companies with False; surfaces below flip to True.
    for (cid,) in db.execute(text("SELECT id FROM companies")).fetchall():
        results[int(cid)] = False

    surfaces: tuple[tuple[str, str], ...] = (
        # add new surface here (also update RED_DOT_CUTOFFS + view).
        (
            "companies.prep_notes",
            "SELECT id, prep_notes FROM companies WHERE prep_notes IS NOT NULL",
        ),
        (
            "companies.notes",
            "SELECT id, notes FROM companies WHERE notes IS NOT NULL",
        ),
        (
            "company_documents.content",
            "SELECT company_id, content FROM company_documents "
            "WHERE content IS NOT NULL",
        ),
        (
            "problem_company_tags.notes",
            "SELECT company_id, notes FROM problem_company_tags "
            "WHERE notes IS NOT NULL",
        ),
        (
            "node_company_tags.notes",
            "SELECT company_id, notes FROM node_company_tags "
            "WHERE notes IS NOT NULL",
        ),
        (
            "behavioral_example_company_tags.notes",
            "SELECT company_id, notes FROM behavioral_example_company_tags "
            "WHERE notes IS NOT NULL",
        ),
    )

    for surface_label, sql in surfaces:
        cutoff = RED_DOT_CUTOFFS[surface_label]
        for company_id, value in db.execute(text(sql)).fetchall():
            cid = int(company_id)
            if cid not in results:
                # Tag pointing at a stale/deleted company; ignore.
                continue
            if results[cid]:
                # Already meaningful via an earlier surface; skip.
                continue
            if _is_meaningful(value, cutoff):
                results[cid] = True

    return results


def has_meaningful_note(db: Session, company_id: int) -> bool:
    """Single-company predicate via ``company_meaningful_note_v``.

    Single SQL query against the view (created in
    ``src.backend.database._create_views``). Falls back to the Python
    ``compute_meaningful_note_map`` if the view is missing (e.g. partial
    schema in a test fixture).
    """
    try:
        row = db.execute(
            text(
                "SELECT has_meaningful_note FROM company_meaningful_note_v "
                "WHERE company_id = :cid"
            ),
            {"cid": company_id},
        ).fetchone()
    except Exception:  # noqa: BLE001
        return compute_meaningful_note_map(db).get(company_id, False)
    if row is None:
        return False
    return bool(row[0])
