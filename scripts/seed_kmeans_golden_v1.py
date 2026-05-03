"""Seed: T-P2-699 [KMEANS-GOLDEN-5] -- Replace problems.id=1064 notes with the
condensed K-Means / K-Means++ golden draft.

Targets problems.id=1064 ("K-Means Pure Python Implementation (K-Means++)").
Unlike scripts/seed_kmeans_vanilla_init_20260502.py (which APPENDED a sibling
section), this script REPLACES the entire notes column with the rewrite at
docs/drafts/kmeans_golden_v1.md. The new draft is a full rewrite (~7KB vs the
existing ~9.8KB) optimized for density and review.

Idempotency:
- Sentinel `<!-- KMEANS_GOLDEN_V1_20260502 -->` is prepended as the first line
  of the new notes value.
- Re-runs detect the sentinel; if the existing notes are byte-equal to the
  canonical payload, [SKIP] with 0 writes. If sentinel is present but bytes
  drifted, the row is rewritten in place.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"
DRAFT_PATH = REPO_ROOT / "docs" / "drafts" / "kmeans_golden_v1.md"
PROBLEM_ID = 1064
SENTINEL = "<!-- KMEANS_GOLDEN_V1_20260502 -->"


def build_payload() -> str:
    """Read the draft file and prepend the sentinel as the first line."""
    body = DRAFT_PATH.read_text(encoding="utf-8")
    return f"{SENTINEL}\n{body}"


def main() -> int:
    if not DB_PATH.exists():
        print(f"[FAIL] Database not found: {DB_PATH}")
        return 1
    if not DRAFT_PATH.exists():
        print(f"[FAIL] Draft not found: {DRAFT_PATH}")
        return 1

    payload = build_payload()

    conn = sqlite3.connect(str(DB_PATH))
    conn.text_factory = str
    try:
        row = conn.execute(
            "SELECT id, title, notes FROM problems WHERE id = ?",
            (PROBLEM_ID,),
        ).fetchone()
        if row is None:
            print(f"[FAIL] No row for problems.id={PROBLEM_ID}")
            return 1
        pid, title, old_notes = row
        old_notes = old_notes or ""

        if SENTINEL in old_notes and old_notes == payload:
            print(
                f"[SKIP] id={pid} sentinel present and notes byte-equal "
                f"(notes_len={len(old_notes)})"
            )
            return 0

        action = "REWRITE" if SENTINEL in old_notes else "REPLACE"

        conn.execute(
            "UPDATE problems SET notes = ? WHERE id = ?",
            (payload, pid),
        )
        conn.commit()

        check = conn.execute(
            "SELECT notes FROM problems WHERE id = ?", (pid,)
        ).fetchone()[0]
        if not check.startswith(SENTINEL):
            print("[FAIL] Sentinel not at start of notes after write")
            return 1
        if check != payload:
            print("[FAIL] Notes do not match payload after write")
            return 1

        print(
            f"[{action}] id={pid} '{title}' notes "
            f"{len(old_notes)} -> {len(payload)} chars"
        )
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
