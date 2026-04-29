"""Prepend a deprecation/redirect banner to the legacy Uber LC index doc (id=81).

T-P2-633 ([UBER-VO-6]): id=37 'Uber VO 完整准备指南' is now the multi-charter
hub (Round 1 LC / Round 2 ML Coding / Round 3 ML SD / Round 4 BQ / HR). This
script prepends a markdown blockquote banner above the existing
``<!-- UBER_LC_INDEX_V1 -->`` sentinel pointing users at id=37, while leaving
the rest of the doc (the 47-problem index built by
``scripts/seed_uber_lc_index.py``) untouched.

Idempotency strategy:
  * Wrap the banner in its own sentinel pair
    ``<!-- T-P2-633:REDIRECT-BANNER BEGIN/END -->``.
  * On re-run, if a block matching that sentinel pair already exists, the
    script replaces the block in place (so banner-text edits are picked up
    next run) and skips the DB write when content_hash is unchanged.
  * If ``seed_uber_lc_index.py`` is re-run after this script, the entire doc
    body is regenerated and the banner is wiped — re-run this redirect script
    after any re-seed to restore.

Run: python scripts/update_uber_lc_index_redirect.py
"""
from __future__ import annotations

import hashlib
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "mle_prep.db"

UBER_COMPANY_ID = 5
TARGET_DOC_ID = 81
TARGET_DOC_TITLE = "Uber LC 题库索引视图 (Index View)"
INDEX_SENTINEL = "<!-- UBER_LC_INDEX_V1 -->"
BANNER_BEGIN = "<!-- T-P2-633:REDIRECT-BANNER BEGIN -->"
BANNER_END = "<!-- T-P2-633:REDIRECT-BANNER END -->"

BANNER_BODY = (
    "> **[UPDATED 2026-04-28]** This LC-only index has been folded into the new\n"
    "> [Uber VO 多 Charter 索引](db://37) which lists Round 1 LC, Round 2 ML Coding,\n"
    "> Round 3 ML SD, Round 4 BQ, and HR side-by-side. The 47 LC problems below\n"
    "> remain the source of truth for Round 1 coverage; the new index links here\n"
    "> for the LC charter."
)


def compute_hash(content: str) -> str:
    """SHA-256 over UTF-8 bytes — used as the idempotency key."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def build_banner_block() -> str:
    """Return the banner section incl. sentinels and trailing blank line."""
    return f"{BANNER_BEGIN}\n{BANNER_BODY}\n{BANNER_END}\n\n"


def strip_existing_banner(content: str) -> str:
    """Remove any existing ``T-P2-633:REDIRECT-BANNER`` block if present.

    Re-running with a freshly authored banner body should produce the new
    content rather than stacking old + new banners.
    """
    if BANNER_BEGIN not in content or BANNER_END not in content:
        return content
    start = content.index(BANNER_BEGIN)
    end = content.index(BANNER_END) + len(BANNER_END)
    after = content[end:]
    if after.startswith("\n\n"):
        after = after[2:]
    elif after.startswith("\n"):
        after = after[1:]
    return content[:start] + after


def prepend_banner(existing_content: str) -> str:
    """Return new content with a single banner block above ``INDEX_SENTINEL``.

    If existing_content does not start with ``INDEX_SENTINEL``, fail loud —
    that means the doc shape changed and a human should review before this
    script touches it.
    """
    cleaned = strip_existing_banner(existing_content)
    if not cleaned.lstrip().startswith(INDEX_SENTINEL):
        raise SystemExit(
            f"[ABORT] doc id={TARGET_DOC_ID} no longer starts with "
            f"'{INDEX_SENTINEL}' — refusing to patch. Got first 80 chars: "
            f"{cleaned[:80]!r}"
        )
    return build_banner_block() + cleaned


def main() -> None:
    """Patch id=81 with the redirect banner; idempotent."""
    if not DB_PATH.exists():
        raise SystemExit(f"DB not found: {DB_PATH}")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.with_suffix(f".db.bak.{ts}_pre_uber_lc_redirect")
    shutil.copy2(DB_PATH, backup_path)
    print(f"[BACKUP] {backup_path.name}")

    with sqlite3.connect(str(DB_PATH)) as conn:
        row = conn.execute(
            "SELECT id, content, content_hash FROM company_documents "
            "WHERE id = ? AND company_id = ? AND title = ?",
            (TARGET_DOC_ID, UBER_COMPANY_ID, TARGET_DOC_TITLE),
        ).fetchone()
        if row is None:
            raise SystemExit(
                f"[ABORT] doc id={TARGET_DOC_ID} (Uber, '{TARGET_DOC_TITLE}') "
                "not found — has the seed been run?"
            )
        doc_id, old_content, old_hash = row

        new_content = prepend_banner(old_content)
        new_hash = compute_hash(new_content)

        if old_hash == new_hash:
            print(
                f"[UNCHANGED] doc id={doc_id} "
                f"content_hash matches ({new_hash[:12]}...)"
            )
            return

        conn.execute(
            "UPDATE company_documents "
            "SET content = ?, content_hash = ?, "
            "    updated_at = CURRENT_TIMESTAMP "
            "WHERE id = ?",
            (new_content, new_hash, doc_id),
        )
        conn.commit()
        print(
            f"[UPDATED] doc id={doc_id} "
            f"old_len={len(old_content)} new_len={len(new_content)} "
            f"hash={new_hash[:12]}..."
        )


if __name__ == "__main__":
    main()
