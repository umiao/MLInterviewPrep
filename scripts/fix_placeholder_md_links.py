"""Rewrite placeholder relative `.md` links in `company_documents` to real routes.

Targets:
    - doc_id=47 (Pinterest LC Must-Do): 9 refs
    - doc_id=36 (Uber HR Call Prep):     1 ref

SD files → `/system-design/<slug>`.
Doc files → `/companies/<cid>/prep?doc=<id>` (resolved from company_documents by title).

Idempotent: re-running produces 0 diff. Rewrites only the exact placeholder
patterns listed below — already-rewritten links pass through untouched.

Usage:
    python scripts/fix_placeholder_md_links.py [--db data/mle_prep.db] [--dry-run]
"""
from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = REPO_ROOT / "data" / "mle_prep.db"

# Relative .md path → canonical route (doc routes resolved at runtime by title).
SD_ROUTES: dict[str, str] = {
    "./pinterest/system_design_ad_ctr.md": "/system-design/pinterest-ad-ctr",
    "./pinterest/system_design_embeddings.md": "/system-design/pinterest-embeddings",
    "./pinterest/system_design_chatbot_pins.md": "/system-design/pinterest-chatbot-pins",
    "./pinterest/system_design_pin_ranking.md": "/system-design/pinterest-pin-ranking",
    "./pinterest/system_design_pins_search.md": "/system-design/pinterest-pins-search",
    "./pinterest/system_design_notification_reco.md": "/system-design/pinterest-notification-reco",
    "./pinterest/system_design_catalog_bulk_update.md": "/system-design/pinterest-catalog-bulk-update",
}

# Relative .md path → (company_id, document_title_to_resolve).
DOC_ROUTES: dict[str, tuple[int, str]] = {
    "./pinterest/bq_question_map.md": (29, "Pinterest BQ Question Map"),
    "./pinterest/lc_investigation_restaurant_intervals.md": (
        29,
        "Pinterest LC Investigation: Restaurant Intervals",
    ),
    "uber_phone_screen_prep.md": (5, "Uber Phone Screen Prep"),
}

TARGET_DOCS = (47, 36)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _resolve_doc_id(cur: sqlite3.Cursor, cid: int, title: str) -> int | None:
    cur.execute(
        "SELECT id FROM company_documents WHERE company_id = ? AND title = ?",
        (cid, title),
    )
    row = cur.fetchone()
    return row[0] if row else None


def build_rewrite_map(cur: sqlite3.Cursor) -> dict[str, str]:
    out = dict(SD_ROUTES)
    for rel, (cid, title) in DOC_ROUTES.items():
        doc_id = _resolve_doc_id(cur, cid, title)
        if doc_id is None:
            print(f"WARN: cannot resolve doc for {title!r} (company={cid})",
                  file=sys.stderr)
            continue
        out[rel] = f"/companies/{cid}/prep?doc={doc_id}"
    return out


def rewrite_content(content: str, rewrites: dict[str, str]) -> tuple[str, int]:
    """Replace `](old)` → `](new)` for each mapping. Returns (new, count)."""
    count = 0
    for old, new in rewrites.items():
        needle = f"]({old})"
        replacement = f"]({new})"
        n = content.count(needle)
        if n:
            content = content.replace(needle, replacement)
            count += n
    return content, count


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=str(DEFAULT_DB))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"ERROR: db not found: {db_path}", file=sys.stderr)
        return 1

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    rewrites = build_rewrite_map(cur)
    total = 0
    changed = 0
    for did in TARGET_DOCS:
        cur.execute("SELECT content FROM company_documents WHERE id = ?", (did,))
        row = cur.fetchone()
        if not row:
            print(f"WARN: doc id={did} not found", file=sys.stderr)
            continue
        new, count = rewrite_content(row[0], rewrites)
        total += count
        if new != row[0]:
            changed += 1
            if args.dry_run:
                print(f"WOULD UPDATE doc id={did}: {count} rewrite(s)")
            else:
                cur.execute(
                    "UPDATE company_documents SET content = ?, updated_at = ? WHERE id = ?",
                    (new, _now(), did),
                )
                print(f"updated doc id={did}: {count} rewrite(s)")
        else:
            print(f"doc id={did}: no change (idempotent)")

    if args.dry_run:
        con.rollback()
    else:
        con.commit()
    con.close()
    print(f"\n{'DRY-RUN' if args.dry_run else 'DONE'}: {changed} doc(s) updated, "
          f"{total} link rewrite(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
