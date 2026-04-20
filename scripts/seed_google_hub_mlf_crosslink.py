"""Add '系统性八股文复习' cross-link bucket to Google Prep Hub (id=53).

Per T-P2-551 [T-MLF-11]. Inserts a new Tier-3 bucket above **Fundamentals**
with a single link out to /ml-fundamentals (the 27-question MLFundamentals
page). All surrounding Tier-2/3 buckets remain byte-identical -- the only
allowed diff is exactly the inserted bucket block.

Idempotency: if the bucket marker ('**系统性八股文复习**') already exists
in content, the run is a no-op (0 updates). First run applies 1 update;
every subsequent run reports 0 updates.
"""
from __future__ import annotations

import hashlib
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

DOC_ID = 53
BUCKET_MARKER = "**系统性八股文复习**"
INSERT_BEFORE = "**Fundamentals**"

# The new bucket block. Trailing blank line matches the spacing between the
# existing **<bucket>** sections so round-trip formatting stays consistent.
NEW_BUCKET = (
    "**系统性八股文复习**\n"
    "- [ML Fundamentals -- 27 题系统速查](/ml-fundamentals)\n"
    "\n"
)


def content_of(conn: sqlite3.Connection, doc_id: int) -> str:
    """Return company_documents.content for doc_id, or raise if missing."""
    row = conn.execute(
        "SELECT content FROM company_documents WHERE id = ?",
        (doc_id,),
    ).fetchone()
    if row is None:
        raise RuntimeError(f"doc id={doc_id} missing")
    return row[0] or ""


def sha256_of(s: str) -> str:
    """Return hex sha256 of the UTF-8 encoding of s."""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def main() -> int:
    """Apply the cross-link bucket insert idempotently. Return 0 on success."""
    if not DB_PATH.exists():
        print(f"[FAIL] db missing at {DB_PATH}", file=sys.stderr)
        return 1

    conn = sqlite3.connect(DB_PATH)
    try:
        content = content_of(conn, DOC_ID)
        pre_hash = sha256_of(content)

        if BUCKET_MARKER in content:
            print(f"[UNCHANGED] id={DOC_ID} already contains {BUCKET_MARKER!r}")
            print(f"[OK] updates=0 skipped=1 sha256={pre_hash[:16]}...")
            return 0

        # Structural pre-check: the Fundamentals anchor must appear exactly once.
        fund_count = content.count(INSERT_BEFORE)
        if fund_count != 1:
            print(
                f"[FAIL] expected exactly 1 occurrence of {INSERT_BEFORE!r}, "
                f"found {fund_count}",
                file=sys.stderr,
            )
            return 2

        # Insert the new bucket immediately before the Fundamentals bucket.
        new_content = content.replace(
            INSERT_BEFORE,
            NEW_BUCKET + INSERT_BEFORE,
            1,
        )

        # Byte-identical guard: removing the inserted chunk from new_content
        # must produce the original content exactly. This proves the only diff
        # is the new bucket; every Tier-2/3 bucket is preserved byte-for-byte.
        if new_content.replace(NEW_BUCKET, "", 1) != content:
            print(
                "[FAIL] post-insert diff is not a single clean insertion",
                file=sys.stderr,
            )
            return 3

        conn.execute(
            "UPDATE company_documents SET content = ? WHERE id = ?",
            (new_content, DOC_ID),
        )
        conn.commit()

        post_hash = sha256_of(new_content)
        print(f"[UPDATE] id={DOC_ID} inserted '系统性八股文复习' bucket above Fundamentals")
        print(f"         pre  sha256={pre_hash[:16]}...")
        print(f"         post sha256={post_hash[:16]}...")
        print(f"[OK] updates=1")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
