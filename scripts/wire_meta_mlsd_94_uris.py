"""Wire all 13 sd:// golden URIs into Meta MLSD doc 94 (T-P0-890).

Per T-P0-890. cd94 (id=94) Section 1 'Family Taxonomy 总表' is augmented with
an explicit `sd-golden` column linking each Q row to its golden example, and
each `### QN.` heading in Section 2 is suffixed with the same arrow link.

Idempotency: sentinel `<!-- META_MLSD_94_URI_WIREUP_20260514 -->` placed
immediately after the existing FAMILY_TAXONOMY sentinel. On re-run, if the
sentinel is present and all 13 slugs already linked in both the table and the
headings, report UNCHANGED with 0 writes.

Scope: edits the BODY of content only -- the drawer header block (sentinel
`<!-- META_MLSD_DRAWER_HEADER_94_20260512 -->`) at the very top is preserved
verbatim. The drawer-header retrofit script remains the canonical source for
the header block; this script does NOT regenerate it.

Q -> slug mapping (frozen at T-P0-890):
  Q1  -> meta-top3-comments-golden
  Q2  -> meta-v2v-search-golden
  Q3  -> meta-friend-rec-golden
  Q4  -> meta-ads-golden
  Q5  -> meta-event-rec-golden
  Q6  -> meta-location-rec-golden
  Q7  -> meta-weapon-ads-golden
  Q8  -> meta-yelp-restaurant-golden
  Q9  -> meta-fb-newsfeed-golden
  Q10 -> meta-ig-story-golden
  Q11 -> meta-spotify-music-golden
  Q12 -> meta-event-attendance-golden
  Q13 -> meta-reels-golden
"""
from __future__ import annotations

import hashlib
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"

DOC_ID = 94
COMPANY_ID = 31

WIREUP_SENTINEL = "<!-- META_MLSD_94_URI_WIREUP_20260514 -->"
FAMILY_SENTINEL = "<!-- META_MLSD_FAMILY_TAXONOMY_20260511 -->"
DRAWER_SENTINEL = "<!-- META_MLSD_DRAWER_HEADER_94_20260512 -->"

# Q-number -> slug (1-indexed; Q13 = Reels, already in place).
Q_SLUGS = {
    1: "meta-top3-comments-golden",
    2: "meta-v2v-search-golden",
    3: "meta-friend-rec-golden",
    4: "meta-ads-golden",
    5: "meta-event-rec-golden",
    6: "meta-location-rec-golden",
    7: "meta-weapon-ads-golden",
    8: "meta-yelp-restaurant-golden",
    9: "meta-fb-newsfeed-golden",
    10: "meta-ig-story-golden",
    11: "meta-spotify-music-golden",
    12: "meta-event-attendance-golden",
    13: "meta-reels-golden",
}

# Original Section 1 header line (4 cols).
ORIG_HEADER = "| # | 题目 | Family | 核心 unique twist |"
ORIG_SEP    = "| - | --- | --- | --- |"
NEW_HEADER  = "| # | 题目 | Family | 核心 unique twist | sd-golden |"
NEW_SEP     = "| - | --- | --- | --- | --- |"


def sha256_bytes(text: str) -> str:
    """Return SHA-256 hex digest of UTF-8 encoded string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def verify_slug_existence(conn: sqlite3.Connection) -> None:
    """Fail-loud guard: every slug must exist in system_designs."""
    rows = {
        r[0]
        for r in conn.execute(
            "SELECT slug FROM system_designs WHERE slug LIKE 'meta-%'"
        ).fetchall()
    }
    missing = [s for s in Q_SLUGS.values() if s not in rows]
    if missing:
        raise RuntimeError(f"missing sd slugs: {missing}")


def already_wired(content: str) -> bool:
    """True iff sentinel present + all 13 slugs present at least 2x.

    The 2x threshold catches the (table cell + heading link) pair.
    """
    if WIREUP_SENTINEL not in content:
        return False
    for slug in Q_SLUGS.values():
        # Q13 has 1 extra inline mention pre-existing in the twist column;
        # Q1 has 1 extra mention from retrofit_meta_mlsd_94_top3_xref.py.
        # So a strict ">= 2" suffices for the new (table cell + heading) pair.
        if content.count(slug) < 2:
            return False
    return True


def transform_content(content: str) -> str:
    """Apply the URI wire-up edits, line by line, to the existing content."""
    lines = content.split("\n")

    # 1. Insert wire-up sentinel right after the FAMILY sentinel.
    try:
        fam_idx = next(
            i for i, ln in enumerate(lines) if ln.strip() == FAMILY_SENTINEL
        )
    except StopIteration as exc:
        raise RuntimeError(
            f"FAMILY sentinel {FAMILY_SENTINEL!r} not found in content"
        ) from exc
    if lines[fam_idx + 1].strip() == WIREUP_SENTINEL:
        # Already inserted; no-op for sentinel.
        pass
    else:
        lines.insert(fam_idx + 1, WIREUP_SENTINEL)

    # 2. Patch Section 1 table header + separator + 13 data rows.
    header_idx = None
    for i, ln in enumerate(lines):
        if ln == ORIG_HEADER:
            header_idx = i
            break
        if ln == NEW_HEADER:
            # Already migrated; will still patch rows defensively below.
            header_idx = i
            break
    if header_idx is None:
        raise RuntimeError(
            f"Section 1 table header not found: {ORIG_HEADER!r}"
        )
    lines[header_idx] = NEW_HEADER
    if lines[header_idx + 1] not in (ORIG_SEP, NEW_SEP):
        raise RuntimeError(
            f"unexpected separator row at line {header_idx + 1}: "
            f"{lines[header_idx + 1]!r}"
        )
    lines[header_idx + 1] = NEW_SEP

    # 3. Patch the 13 data rows (must start with `| N | `).
    rows_seen = 0
    i = header_idx + 2
    while rows_seen < 13:
        ln = lines[i]
        if not ln.startswith("| "):
            raise RuntimeError(
                f"expected table row at line {i}, got: {ln!r}"
            )
        # Parse row number from leading cell.
        # Format: `| N | 题目 | Family | twist |` or already-migrated
        # `| N | 题目 | Family | twist | [link](sd://...) |`.
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        try:
            q_num = int(cells[0])
        except ValueError as exc:
            raise RuntimeError(
                f"row {i}: cannot parse Q-number from {cells[0]!r}"
            ) from exc
        if q_num != rows_seen + 1:
            raise RuntimeError(
                f"row {i}: expected Q{rows_seen + 1}, got Q{q_num}"
            )
        slug = Q_SLUGS[q_num]
        new_cell = f"[link](sd://{slug})"
        if len(cells) == 4:
            # 4-cell original layout: append the 5th cell.
            lines[i] = (
                f"| {cells[0]} | {cells[1]} | {cells[2]} | {cells[3]} "
                f"| {new_cell} |"
            )
        elif len(cells) == 5:
            # Already migrated -- normalize the URI cell.
            lines[i] = (
                f"| {cells[0]} | {cells[1]} | {cells[2]} | {cells[3]} "
                f"| {new_cell} |"
            )
        else:
            raise RuntimeError(
                f"row {i}: unexpected cell count {len(cells)}: {cells!r}"
            )
        rows_seen += 1
        i += 1

    # 4. Patch each `### QN.` heading: append ` -> [sd-golden](sd://slug)`
    # iff not already present. Use the unicode arrow U+2192 ('->' rendered).
    for j, ln in enumerate(lines):
        if not ln.startswith("### Q"):
            continue
        # Match `### Q<NUM>. <rest>`.
        # Extract N from `### Q<N>.`.
        try:
            after_q = ln[len("### Q"):]
            num_str = after_q.split(".", 1)[0]
            q_num = int(num_str)
        except (ValueError, IndexError):
            continue
        if q_num not in Q_SLUGS:
            continue
        slug = Q_SLUGS[q_num]
        suffix_marker = f"](sd://{slug})"
        if suffix_marker in ln:
            # Already wired in heading; skip.
            continue
        lines[j] = f"{ln} → [sd-golden](sd://{slug})"

    return "\n".join(lines)


def validate(new_content: str, old_content: str) -> None:
    """Post-transform invariants."""
    # Drawer header must remain at the top, byte-identical to before.
    if not new_content.startswith(DRAWER_SENTINEL):
        raise RuntimeError("drawer header sentinel no longer at top of content")
    # Wire-up sentinel must be present.
    if WIREUP_SENTINEL not in new_content:
        raise RuntimeError("wire-up sentinel missing post-transform")
    # Each slug must appear at least 2x (table cell + heading).
    for q_num, slug in Q_SLUGS.items():
        c = new_content.count(slug)
        if c < 2:
            raise RuntimeError(
                f"Q{q_num} slug {slug!r} count {c} < 2 (need table cell + heading)"
            )
    # Family taxonomy sentinel must still be present.
    if FAMILY_SENTINEL not in new_content:
        raise RuntimeError("FAMILY_SENTINEL missing post-transform")
    # New header / separator present.
    if NEW_HEADER not in new_content:
        raise RuntimeError("new 5-col header missing")
    if NEW_SEP not in new_content:
        raise RuntimeError("new 5-col separator missing")
    # Total char length sane window (mirrors drawer-retrofit validator).
    n = len(new_content)
    if n > 21000:
        raise RuntimeError(f"content {n} chars > 21000 cap")
    if n < 14400:
        raise RuntimeError(f"content {n} chars < 14400 floor (destructive?)")
    # Content must have grown from the original (this is a wire-UP, not a strip).
    if n <= len(old_content):
        raise RuntimeError(
            f"content did not grow: old={len(old_content)} new={n}"
        )


def main() -> int:
    """Wire 13 sd:// URIs into cd94. Idempotent."""
    if not DB_PATH.exists():
        print(f"[ERROR] db not found: {DB_PATH}")
        return 1

    conn = sqlite3.connect(str(DB_PATH))
    try:
        verify_slug_existence(conn)
        print(f"[OK] all 13 sd:// slugs verified in system_designs")

        row = conn.execute(
            "SELECT id, company_id, title, content "
            "FROM company_documents WHERE id = ?",
            (DOC_ID,),
        ).fetchone()
        if row is None:
            print(f"[ERROR] company_documents.id={DOC_ID} not found")
            return 1
        _, company_id, title, existing_content = row
        if company_id != COMPANY_ID:
            print(
                f"[ERROR] expected company_id={COMPANY_ID}, got {company_id}"
            )
            return 1
        print(
            f"[OK] target: id={DOC_ID} title={title!r} "
            f"chars={len(existing_content)}"
        )

        if already_wired(existing_content):
            print(
                "[UNCHANGED] wire-up sentinel present + all 13 slugs linked; "
                "0 writes"
            )
            return 0

        new_content = transform_content(existing_content)
        validate(new_content, existing_content)
        new_hash = sha256_bytes(new_content)
        print(
            f"[OK] post-transform: chars={len(new_content)} "
            f"delta={len(new_content) - len(existing_content):+d} "
            f"hash={new_hash[:12]}..."
        )

        now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            "UPDATE company_documents "
            "SET content = ?, content_hash = ?, updated_at = ? "
            "WHERE id = ?",
            (new_content, new_hash, now, DOC_ID),
        )
        conn.commit()
        print(f"[UPDATE] id={DOC_ID} updated_at={now}")

        # Post-write re-read.
        post = conn.execute(
            "SELECT content FROM company_documents WHERE id = ?",
            (DOC_ID,),
        ).fetchone()[0]
        if post != new_content:
            print("[ERROR] post-write readback mismatch")
            return 1
        print("[OK] post-write readback verified")

        # Final slug count summary.
        for q_num, slug in Q_SLUGS.items():
            print(f"  Q{q_num:2d} -> {slug} (count={post.count(slug)})")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
