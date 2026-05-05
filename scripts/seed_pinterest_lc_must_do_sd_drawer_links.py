"""Migrate the 7 ``/system-design/pinterest-*`` path links in doc 47 to ``sd://`` URIs.

Step 4 of the 6-step Pinterest System Design drawer fix (T-P0-731..736). After
T-P0-731 added the ``sd://<slug>`` URI scheme to MarkdownPreview, T-P0-732 built
SystemDesignDrawer, and T-P0-733 wired it into PrepNotesPage.DocumentViewer, this
seed flips the content references in ``company_documents.id=47`` (Pinterest LC
Must-Do: Review & Index, company_id=29) so the 7 SD table links render as
drawer-trigger buttons instead of full-page navigations.

Idempotent: re-running after success is a no-op (detects 0 path-form +
7 sd:// links pre-state and exits 0 with an "already migrated" log).

Invariant 3 compliance: this is the git-tracked, idempotent Python source of
truth for the doc-47 link migration. NO ad-hoc SQL.

Acceptance criteria (mirrors task T-P0-734):
- Exactly 7 ``](/system-design/pinterest-<slug>)`` matches replaced with
  ``](sd://<slug>)`` -- no other content changes.
- Recompute ``content_hash`` (SHA256 of new content) and bump ``updated_at``
  in a single transaction.
- Re-run after success = no-op.
"""
from __future__ import annotations

import hashlib
import re
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

DOC_ID = 47
EXPECTED_COMPANY_ID = 29  # Pinterest -- defensive double-check
EXPECTED_SLUGS = (
    "pinterest-ad-ctr",
    "pinterest-embeddings",
    "pinterest-chatbot-pins",
    "pinterest-pin-ranking",
    "pinterest-pins-search",
    "pinterest-notification-reco",
    "pinterest-catalog-bulk-update",
)
EXPECTED_LINK_COUNT = 7

# Anchored on the ``](`` and ``)`` boundaries so we only touch markdown links,
# never bare prose mentions of ``/system-design/...``.
PATH_LINK_PATTERN = re.compile(r"]\(/system-design/(pinterest-[a-z-]+)\)")
SD_LINK_PATTERN = re.compile(r"]\(sd://(pinterest-[a-z-]+)\)")


def count_links(content: str) -> tuple[int, int]:
    """Return (path_link_count, sd_link_count) for pinterest-* slugs."""
    return (
        len(PATH_LINK_PATTERN.findall(content)),
        len(SD_LINK_PATTERN.findall(content)),
    )


def migrate(content: str) -> tuple[str, list[str]]:
    """Apply the 7 path -> sd:// rewrites. Returns (new_content, slugs_replaced)."""
    replaced: list[str] = []

    def _sub(m: re.Match[str]) -> str:
        slug = m.group(1)
        replaced.append(slug)
        return f"](sd://{slug})"

    new_content = PATH_LINK_PATTERN.sub(_sub, content)
    return new_content, replaced


def main() -> int:
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, company_id, title, content, content_hash "
            "FROM company_documents WHERE id = ?",
            (DOC_ID,),
        )
        row = cur.fetchone()
        if row is None:
            print(f"[FAIL] company_documents.id={DOC_ID} not found", file=sys.stderr)
            return 2

        doc_id, company_id, title, content, old_hash = row
        if company_id != EXPECTED_COMPANY_ID:
            print(
                f"[FAIL] doc {doc_id} has company_id={company_id}, "
                f"expected {EXPECTED_COMPANY_ID} -- aborting",
                file=sys.stderr,
            )
            return 2

        before_path, before_sd = count_links(content)
        print(f"[INFO] doc {doc_id} ({title!r})")
        print(f"[INFO] before: path-form={before_path}, sd://={before_sd}, "
              f"len={len(content)}, hash={old_hash[:12]}...")

        # Idempotency: if all 7 already migrated, exit no-op.
        if before_path == 0 and before_sd == EXPECTED_LINK_COUNT:
            print(f"[OK] already migrated ({before_sd} sd:// links present, "
                  f"0 path-form remain) -- no-op")
            return 0

        if before_path != EXPECTED_LINK_COUNT:
            print(
                f"[FAIL] expected {EXPECTED_LINK_COUNT} path-form links, "
                f"found {before_path} -- aborting (manual review required)",
                file=sys.stderr,
            )
            return 2

        new_content, replaced = migrate(content)
        after_path, after_sd = count_links(new_content)

        # Post-condition asserts.
        if after_path != 0:
            print(
                f"[FAIL] post-migrate path-form count={after_path}, expected 0",
                file=sys.stderr,
            )
            return 2
        if after_sd != EXPECTED_LINK_COUNT:
            print(
                f"[FAIL] post-migrate sd:// count={after_sd}, "
                f"expected {EXPECTED_LINK_COUNT}",
                file=sys.stderr,
            )
            return 2
        replaced_set = set(replaced)
        expected_set = set(EXPECTED_SLUGS)
        if replaced_set != expected_set:
            missing = expected_set - replaced_set
            extra = replaced_set - expected_set
            print(
                f"[FAIL] slug mismatch: missing={sorted(missing)}, "
                f"extra={sorted(extra)}",
                file=sys.stderr,
            )
            return 2

        # Other-case gate: only the 7 link substrings should differ.
        delta_chars = abs(len(new_content) - len(content))
        # Each replacement: "](/system-design/<slug>)" -> "](sd://<slug>)"
        # net delta per link = len("/system-design/") - len("sd://") = 15 - 5 = 10
        expected_delta = 10 * EXPECTED_LINK_COUNT
        if delta_chars != expected_delta:
            print(
                f"[FAIL] unexpected length delta: {delta_chars} chars "
                f"(expected {expected_delta} = 10 * {EXPECTED_LINK_COUNT})",
                file=sys.stderr,
            )
            return 2

        new_hash = hashlib.sha256(new_content.encode("utf-8")).hexdigest()
        now_utc = datetime.now(UTC).isoformat(timespec="seconds")

        cur.execute(
            "UPDATE company_documents "
            "SET content = ?, content_hash = ?, updated_at = ? "
            "WHERE id = ?",
            (new_content, new_hash, now_utc, doc_id),
        )
        conn.commit()

        print(f"[OK] migrated {len(replaced)} link(s):")
        for slug in replaced:
            print(f"     /system-design/{slug}  ->  sd://{slug}")
        print(f"[INFO] after:  path-form={after_path}, sd://={after_sd}, "
              f"len={len(new_content)}, hash={new_hash[:12]}...")
        print(f"[INFO] length delta: {delta_chars} chars "
              f"(== 10 * {EXPECTED_LINK_COUNT} as expected)")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
