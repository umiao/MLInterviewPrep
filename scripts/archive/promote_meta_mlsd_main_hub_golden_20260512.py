"""T-P0-841 [Meta-MLSD E] -- Promote new MLSD main hub to is_golden=1 and
demote the previous Meta golden onsite-prep doc (id=82) to is_golden=0.

Acts on `company_documents` for `company_id=31` (Meta):

- Resolves the new main hub by canonical title lookup (NOT hardcoded id):
    `[Meta-MLSD] 45min Playbook + 4 Strong Moments` (seeded by T-P0-840).
- Demotes the prior onsite-prep golden `id=82` (`[Meta] AI-Native Onsite Prep`)
  -- preserved (NOT deleted) so the AI-Native onsite round can still use it.
- Promotes the new main hub: is_golden=1 + golden_at=now.

Single transaction; partial failure rolls back both writes.

Idempotency:
- If both flips already match the target state, both rows are [SKIP].
- If only one side is drifted, only that side is written.
- golden_at is only stamped when transitioning 0 -> 1 (no overwrite on
  re-runs with existing golden_at).

Out-of-scope and intentional:
- Doc id=90 (`[Meta] AI-Native Coding Inventory & Cheat Sheet`, doc_kind=hub_doc)
  is ALSO currently is_golden=1. It serves the parallel AI-Native coding flow
  and is referenced by other docs (cd://90 in doc 82). The T-P0-841 spec only
  names doc 82 for demotion; doc 90 is left untouched. As a consequence the
  spec's validation `COUNT(is_golden=1)=1 for company_id=31` cannot be met
  post-run -- after this script the count is 2 (doc 90 + doc 96). This is
  documented in PROGRESS.md and is the deliberate interpretation; see also the
  state of `company_documents` before this run.
"""
from __future__ import annotations

import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"

META_COMPANY_ID = 31
NEW_MAIN_HUB_TITLE = "[Meta-MLSD] 45min Playbook + 4 Strong Moments"
OLD_GOLDEN_DOC_ID = 82


def _now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")


def main() -> int:
    if not DB_PATH.exists():
        print(f"[FAIL] Database not found: {DB_PATH}")
        return 1

    conn = sqlite3.connect(str(DB_PATH))
    conn.text_factory = str
    try:
        # Step 1: resolve new main hub by title (must exist exactly once).
        new_hub_rows = conn.execute(
            "SELECT id, title, is_golden, golden_at FROM company_documents "
            "WHERE company_id = ? AND title = ?",
            (META_COMPANY_ID, NEW_MAIN_HUB_TITLE),
        ).fetchall()
        if not new_hub_rows:
            print(
                f"[FAIL] New main hub not found: company_id={META_COMPANY_ID} "
                f"title={NEW_MAIN_HUB_TITLE!r}. Run T-P0-840 seed first."
            )
            return 1
        if len(new_hub_rows) > 1:
            print(
                f"[FAIL] Expected exactly 1 row for new main hub, got "
                f"{len(new_hub_rows)}: {[r[0] for r in new_hub_rows]}"
            )
            return 1
        new_id, new_title, new_is_golden, new_golden_at = new_hub_rows[0]
        if new_id == OLD_GOLDEN_DOC_ID:
            print(
                f"[FAIL] New main hub id collides with OLD_GOLDEN_DOC_ID "
                f"({OLD_GOLDEN_DOC_ID}); refusing to proceed."
            )
            return 1

        # Step 2: load old golden (id=82); must exist for company 31.
        old_row = conn.execute(
            "SELECT id, title, is_golden, golden_at FROM company_documents "
            "WHERE id = ? AND company_id = ?",
            (OLD_GOLDEN_DOC_ID, META_COMPANY_ID),
        ).fetchone()
        if old_row is None:
            print(
                f"[FAIL] Old golden doc id={OLD_GOLDEN_DOC_ID} not found "
                f"for company_id={META_COMPANY_ID}."
            )
            return 1
        old_id, old_title, old_is_golden, old_golden_at = old_row

        now_iso = _now_iso()
        actions: list[str] = []

        # Step 3: demote old golden if currently is_golden=1.
        # Preserve the doc (NOT deleted), set golden_at=NULL to mark non-golden.
        if old_is_golden:
            conn.execute(
                "UPDATE company_documents "
                "SET is_golden = 0, golden_at = NULL, "
                "updated_at = CURRENT_TIMESTAMP "
                "WHERE id = ? AND company_id = ?",
                (OLD_GOLDEN_DOC_ID, META_COMPANY_ID),
            )
            actions.append(
                f"[DEMOTE] id={old_id} '{old_title}' "
                f"is_golden 1 -> 0 (golden_at cleared)"
            )
        else:
            actions.append(
                f"[SKIP-DEMOTE] id={old_id} '{old_title}' already is_golden=0"
            )

        # Step 4: promote new main hub if not already golden.
        if new_is_golden and new_golden_at:
            actions.append(
                f"[SKIP-PROMOTE] id={new_id} '{new_title}' already "
                f"is_golden=1 (golden_at={new_golden_at})"
            )
        elif new_is_golden and not new_golden_at:
            conn.execute(
                "UPDATE company_documents "
                "SET golden_at = ?, updated_at = CURRENT_TIMESTAMP "
                "WHERE id = ? AND company_id = ?",
                (now_iso, new_id, META_COMPANY_ID),
            )
            actions.append(
                f"[BACKFILL] id={new_id} '{new_title}' "
                f"golden_at <- {now_iso}"
            )
        else:
            conn.execute(
                "UPDATE company_documents "
                "SET is_golden = 1, golden_at = ?, "
                "updated_at = CURRENT_TIMESTAMP "
                "WHERE id = ? AND company_id = ?",
                (now_iso, new_id, META_COMPANY_ID),
            )
            actions.append(
                f"[PROMOTE] id={new_id} '{new_title}' "
                f"is_golden 0 -> 1, golden_at <- {now_iso}"
            )

        conn.commit()

        # Step 5: post-write verification (per task spec, narrowed -- doc 90
        # also currently golden; see module docstring).
        post_new = conn.execute(
            "SELECT is_golden, golden_at FROM company_documents WHERE id = ?",
            (new_id,),
        ).fetchone()
        post_old = conn.execute(
            "SELECT is_golden, golden_at FROM company_documents WHERE id = ?",
            (OLD_GOLDEN_DOC_ID,),
        ).fetchone()
        if post_new[0] != 1 or not post_new[1]:
            print(
                f"[FAIL] Post-write verify: new main hub id={new_id} "
                f"is_golden={post_new[0]} golden_at={post_new[1]}"
            )
            return 1
        if post_old[0] != 0:
            print(
                f"[FAIL] Post-write verify: old doc id={OLD_GOLDEN_DOC_ID} "
                f"is_golden={post_old[0]} (expected 0)"
            )
            return 1

        # Step 6: report counts (advisory -- doc 90 stays golden).
        meta_golden_rows = conn.execute(
            "SELECT id, title, doc_kind, is_golden, golden_at "
            "FROM company_documents WHERE company_id = ? AND is_golden = 1 "
            "ORDER BY golden_at DESC NULLS LAST, id ASC",
            (META_COMPANY_ID,),
        ).fetchall()

        for line in actions:
            print(line)
        print(
            f"[OK] new main hub id={new_id} is is_golden=1; "
            f"old doc {OLD_GOLDEN_DOC_ID} is is_golden=0."
        )
        print(
            f"[INFO] company_id={META_COMPANY_ID} now has "
            f"{len(meta_golden_rows)} is_golden=1 docs:"
        )
        for r in meta_golden_rows:
            print(
                f"        id={r[0]} doc_kind={r[2]} golden_at={r[4]} "
                f"title={r[1]!r}"
            )
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
