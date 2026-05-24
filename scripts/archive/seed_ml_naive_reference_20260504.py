"""Seed: T-P0-728 -- ML Naive Reference card (KNN + KMeans + LogReg).

Single responsibility: UPSERT the ML Naive Reference summary problem row that
backs the new "Naive Reference Implementations" card on QuickIndex (ML tab,
section below the existing 5 problem cards). Notes content lives in
``docs/drafts/ml_naive_reference_v1.md``; this script reads that file and
writes it to ``problems.notes`` with a sentinel prepended.

User-confirmed design (Discord 2026-05-04):
- Stay-at-3 reference set: KNN + KMeans + LogReg (the GLM-orthogonal subset).
- Linear regression (closed-form lstsq, db://1102) and Geometric Median
  (Weiszfeld iteration, db://1108) are tracked in their own problem rows;
  this card is intentionally orthogonal.
- ``is_golden`` defaults to 0; the card uses a parallel purple/indigo visual
  marker (``referenceCardClass`` in ``utils/goldenStyle.ts``), not the golden
  orange treatment.

Idempotency:
- Sentinel ``<!-- ML_NAIVE_REFERENCE_V1_20260504 -->`` is the first line of
  the notes payload. Re-runs detect it; if existing notes/title/description
  are byte-equal to the canonical payload, [SKIP] with 0 writes. Otherwise
  UPDATE in place (or INSERT on first run).

Length cap: payload (sentinel + draft body) must be <= 12,000 chars.
Current draft is ~8.6 KB; the cap leaves headroom for future expansions.
"""
from __future__ import annotations

import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"
DRAFT_PATH = REPO_ROOT / "docs" / "drafts" / "ml_naive_reference_v1.md"

TITLE = "ML 朴素实现汇总: KNN + KMeans + Logistic Regression"
SOURCE = "ml-naive-reference-2026-05-04"
DIFFICULTY = "medium"
PATTERN = "ML Reference"
CATEGORY = "ml_coding"
TAGS = '["ml-fundamentals", "reference", "knn", "kmeans", "logistic-regression"]'
COMPANY_TAGS = '["Meta", "Uber", "DoorDash", "Pinterest"]'
PRIORITY = 1

SENTINEL = "<!-- ML_NAIVE_REFERENCE_V1_20260504 -->"
LENGTH_CAP = 12000

DESCRIPTION = (
    "Side-by-side naive reference impls of KNN, KMeans, and Logistic "
    "Regression using common variable conventions (N/M/D/k/C). For ML "
    "interview coding-round quick recall and cross-comparison. Linear "
    "regression (closed-form lstsq, db://1102) and geometric median "
    "(Weiszfeld iteration, db://1108) are tracked in their own problem rows; "
    "this card is the GLM-orthogonal subset showcasing shared vectorization "
    "tricks (pairwise distance expansion, argpartition top-k, broadcasting "
    "one-hot voting, k-means++ init, empty-cluster reseed, GLM canonical-link "
    "gradient simplification)."
)


def build_payload() -> str:
    """Read the reference draft and prepend the sentinel as the first line."""
    body = DRAFT_PATH.read_text(encoding="utf-8")
    if body.startswith(SENTINEL):
        return body
    return f"{SENTINEL}\n{body}"


def main() -> int:
    if not DB_PATH.exists():
        print(f"[FAIL] Database not found: {DB_PATH}")
        return 1
    if not DRAFT_PATH.exists():
        print(f"[FAIL] Draft not found: {DRAFT_PATH}")
        return 1

    notes_payload = build_payload()
    if len(notes_payload) > LENGTH_CAP:
        print(
            f"[FAIL] Notes payload {len(notes_payload)} chars exceeds cap "
            f"{LENGTH_CAP}. Trim the draft."
        )
        return 1

    conn = sqlite3.connect(str(DB_PATH))
    conn.text_factory = str
    try:
        row = conn.execute(
            "SELECT id, title, description, notes "
            "FROM problems WHERE title = ? AND source = ?",
            (TITLE, SOURCE),
        ).fetchone()

        now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")

        if row is None:
            cur = conn.execute(
                "INSERT INTO problems "
                "(title, description, notes, difficulty, pattern, "
                "category, tags, source, company_tags, priority, "
                "is_completed, comfort_level, description_source, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
                "0, 0, 'manual', ?)",
                (
                    TITLE,
                    DESCRIPTION,
                    notes_payload,
                    DIFFICULTY,
                    PATTERN,
                    CATEGORY,
                    TAGS,
                    SOURCE,
                    COMPANY_TAGS,
                    PRIORITY,
                    now,
                ),
            )
            new_id = int(cur.lastrowid or 0)
            conn.commit()
            print(
                f"[INSERT] '{TITLE}' id={new_id} "
                f"description={len(DESCRIPTION)} notes={len(notes_payload)} chars"
            )
        else:
            pid, old_title, old_desc, old_notes = row
            old_title = old_title or ""
            old_desc = old_desc or ""
            old_notes = old_notes or ""
            new_id = int(pid)
            if (
                old_title == TITLE
                and old_desc == DESCRIPTION
                and old_notes == notes_payload
            ):
                print(
                    f"[SKIP] id={pid} '{TITLE}' title+description+notes "
                    f"byte-equal (notes={len(old_notes)})"
                )
            else:
                conn.execute(
                    "UPDATE problems "
                    "SET title = ?, description = ?, notes = ?, "
                    "    difficulty = ?, pattern = ?, category = ?, "
                    "    tags = ?, company_tags = ?, priority = ? "
                    "WHERE id = ?",
                    (
                        TITLE,
                        DESCRIPTION,
                        notes_payload,
                        DIFFICULTY,
                        PATTERN,
                        CATEGORY,
                        TAGS,
                        COMPANY_TAGS,
                        PRIORITY,
                        pid,
                    ),
                )
                conn.commit()

                check = conn.execute(
                    "SELECT title, notes FROM problems WHERE id = ?", (pid,)
                ).fetchone()
                check_title, check_notes = check
                if check_title != TITLE or check_notes != notes_payload:
                    print("[FAIL] Title or notes do not match payload after write")
                    return 1
                if not check_notes.startswith(SENTINEL):
                    print("[FAIL] Sentinel not at start of notes after write")
                    return 1

                print(
                    f"[UPDATE] id={pid} '{old_title}' -> '{TITLE}', "
                    f"notes {len(old_notes)} -> {len(notes_payload)} chars"
                )
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
