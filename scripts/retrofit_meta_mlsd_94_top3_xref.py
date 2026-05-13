"""Retrofit Meta MLSD doc 94 with sd://meta-top3-comments-golden cross-links (T-P0-855).

Two surgical inserts into company_documents.id=94 content (does NOT replace any
existing structure, only inserts two lines):

  1. Drawer 入口 table: new row immediately AFTER the sd://meta-reels-golden row
     (golden examples grouped together at top of table).
     New row:
       > | **[Top-3 Comments Golden Example (45min)](sd://meta-top3-comments-golden)** | 45-min full pacing + Bias Tower + Shadow Logging | 想看 Top-3 Comments 完整 walkthrough |

  2. Q1 'Top 3 Comments Extraction' card: italic anchor line appended AFTER the
     Strong Moment paragraph, BEFORE the '### Q2.' header (preserves the 30-second
     judging density of the Q1 card itself — only +1 anchor line).
     New line:
       *→ 完整 45min 脚本见 sd://meta-top3-comments-golden*

Idempotency: detect `sd://meta-top3-comments-golden` already present in content;
on re-run report UNCHANGED with 0 writes (skip both inserts).

Self-link contract preserved: cd://94 must remain absent from the Drawer 入口 table.

Style: NO emoji; blockquote `> ` prefix on drawer row; italic with single `*` on
anchor line.
"""
from __future__ import annotations

import hashlib
import re
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"

COMPANY_ID = 31  # Meta
DOC_ID = 94
EXPECTED_TITLE = "[Meta-MLSD] Family Taxonomy + 13 Question Cards (drawer)"

TARGET_SD_SLUG = "meta-top3-comments-golden"
TARGET_URI = f"sd://{TARGET_SD_SLUG}"

# --- Insert 1: drawer row ---------------------------------------------------
# Existing row that anchors the insertion point.
REELS_GOLDEN_ROW = (
    "> | **[Reels Golden Example (45min 全文)](sd://meta-reels-golden)** "
    "| 八段台词 + 4 Strong Moments verbatim "
    "| 想看 DLRM/multi-task/multimodal 实战编排 |"
)
TOP3_GOLDEN_ROW = (
    f"> | **[Top-3 Comments Golden Example (45min)]({TARGET_URI})** "
    "| 45-min full pacing + Bias Tower + Shadow Logging "
    "| 想看 Top-3 Comments 完整 walkthrough |"
)

# --- Insert 2: Q1 anchor line -----------------------------------------------
# The Q1 Strong Moment line is one long markdown line followed by a blank then
# '### Q2.'. We match the boundary `\n### Q2.` and insert the anchor + blank
# line just before it. The anchor is italic (single-star) on its own line.
Q1_ANCHOR_LINE = f"*→ 完整 45min 脚本见 {TARGET_URI}*"
Q2_HEADER_PATTERN = re.compile(r"\n### Q2\. ")


def sha256_bytes(text: str) -> str:
    """Return SHA-256 hex digest of UTF-8 encoded string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def apply_inserts(content: str) -> str:
    """Apply both inserts and return new content. Raises on anchor miss."""
    # Insert 1: drawer row after the meta-reels-golden row.
    if REELS_GOLDEN_ROW not in content:
        raise RuntimeError(
            "drawer anchor row 'Reels Golden Example' not found in content"
        )
    replacement = f"{REELS_GOLDEN_ROW}\n{TOP3_GOLDEN_ROW}"
    if content.count(REELS_GOLDEN_ROW) != 1:
        raise RuntimeError(
            f"drawer anchor row appears "
            f"{content.count(REELS_GOLDEN_ROW)}x; expected exactly 1"
        )
    new_content = content.replace(REELS_GOLDEN_ROW, replacement, 1)

    # Insert 2: anchor line before '### Q2.' (sits at end of Q1 card).
    matches = list(Q2_HEADER_PATTERN.finditer(new_content))
    if len(matches) != 1:
        raise RuntimeError(
            f"expected exactly 1 '### Q2.' header, found {len(matches)}"
        )
    m = matches[0]
    # Insert: existing pattern is "...selected comments.\"\n\n### Q2. ".
    # We replace the leading "\n### Q2. " with "\n{anchor}\n\n### Q2. ".
    insertion = f"\n{Q1_ANCHOR_LINE}\n"
    new_content = (
        new_content[: m.start()] + insertion + new_content[m.start():]
    )
    return new_content


def validate(new_content: str, old_content: str) -> None:
    """Sanity checks mirroring T-P0-855 acceptance criteria."""
    # AC #1: drawer entry table contains the new row pointing to TARGET_URI.
    if TOP3_GOLDEN_ROW not in new_content:
        raise RuntimeError("new drawer row not present after insertion")

    # AC #2: Q1 card末尾 contains the italic anchor line.
    if Q1_ANCHOR_LINE not in new_content:
        raise RuntimeError("Q1 anchor line not present after insertion")

    # AC #3: total delta < 500 bytes (only 2 markdown lines added).
    delta_bytes = (
        len(new_content.encode("utf-8")) - len(old_content.encode("utf-8"))
    )
    if not (0 < delta_bytes < 500):
        raise RuntimeError(
            f"content byte delta {delta_bytes:+d} out of (0, 500)"
        )

    # AC #4: self-URI cd://94 NOT in Drawer 入口 table block.
    # Drawer block = first occurrence of '> ## Drawer 入口' through the '---'
    # immediately following the table.
    start = new_content.find("> ## Drawer 入口")
    if start < 0:
        raise RuntimeError("Drawer 入口 header not found")
    rule_offset = new_content.find("\n---\n", start)
    if rule_offset < 0:
        raise RuntimeError("horizontal rule after Drawer table not found")
    drawer_block = new_content[start:rule_offset]
    self_uri = f"cd://{DOC_ID}"
    if self_uri in drawer_block:
        raise RuntimeError(
            f"self-link violation: {self_uri} found in Drawer 入口 block"
        )

    # AC: the new drawer row sits immediately after the reels-golden row
    # (golden grouping). No interleaving other rows.
    reels_idx = new_content.find(REELS_GOLDEN_ROW)
    top3_idx = new_content.find(TOP3_GOLDEN_ROW)
    expected_top3_idx = reels_idx + len(REELS_GOLDEN_ROW) + 1  # "\n"
    if top3_idx != expected_top3_idx:
        raise RuntimeError(
            f"top3 row not adjacent to reels row: "
            f"reels_end={reels_idx + len(REELS_GOLDEN_ROW)} "
            f"top3_start={top3_idx}"
        )

    # AC: anchor line sits between Q1 Strong Moment and '### Q2.'.
    anchor_idx = new_content.find(Q1_ANCHOR_LINE)
    q2_idx = new_content.find("\n### Q2. ")
    q1_strong_idx = new_content.find('**Strong Moment**: "The comment at position 0')
    if not (q1_strong_idx >= 0 and q1_strong_idx < anchor_idx < q2_idx):
        raise RuntimeError(
            f"Q1 anchor not positioned between Strong Moment and Q2 header: "
            f"q1_strong={q1_strong_idx} anchor={anchor_idx} q2={q2_idx}"
        )

    # Body landmarks preserved.
    required_fragments = [
        "<!-- META_MLSD_DRAWER_HEADER_94_20260512 -->",
        "<!-- META_MLSD_FAMILY_TAXONOMY_20260511 -->",
        "# Meta MLSD - Family Taxonomy + 13 Question Cards (drawer)",
        "## 1. Family Taxonomy 总表",
        "## 2. Per-Question Cards (Q1-Q13)",
        "### Q1. Top 3 Comments Extraction",
        "### Q13. Reels",
    ]
    for frag in required_fragments:
        if frag not in new_content:
            raise RuntimeError(f"landmark missing post-insert: {frag!r}")

    # NO emoji style rule on the two inserted strings.
    for label, s in (("TOP3_GOLDEN_ROW", TOP3_GOLDEN_ROW),
                     ("Q1_ANCHOR_LINE", Q1_ANCHOR_LINE)):
        for ch in s:
            cp = ord(ch)
            if (
                0x1F300 <= cp <= 0x1F9FF
                or 0x2600 <= cp <= 0x27BF
            ):
                raise RuntimeError(
                    f"emoji-like char in {label} at U+{cp:04X}: {ch!r}"
                )


def main() -> int:
    """Retrofit doc 94 with two sd://meta-top3-comments-golden cross-links."""
    if not DB_PATH.exists():
        print(f"[ERROR] db not found: {DB_PATH}")
        return 1

    conn = sqlite3.connect(str(DB_PATH))
    try:
        row = conn.execute(
            "SELECT id, company_id, title, content "
            "FROM company_documents WHERE id = ?",
            (DOC_ID,),
        ).fetchone()
        if row is None:
            print(f"[ERROR] company_documents.id={DOC_ID} not found")
            return 1
        existing_id, existing_company, existing_title, existing_content = row
        if existing_company != COMPANY_ID:
            print(
                f"[ERROR] expected company_id={COMPANY_ID}, got "
                f"{existing_company}"
            )
            return 1
        if existing_title != EXPECTED_TITLE:
            print(
                f"[ERROR] title drift: expected {EXPECTED_TITLE!r}, got "
                f"{existing_title!r}"
            )
            return 1
        print(
            f"[OK] target: id={existing_id} title={existing_title!r} "
            f"chars={len(existing_content)}"
        )

        # Idempotency: TARGET_URI already present anywhere => UNCHANGED.
        if TARGET_URI in existing_content:
            # Run validation on existing content to confirm both inserts are
            # present and correctly placed (defense against partial prior run).
            try:
                # Re-validate against (new=existing, old=existing-without-both).
                # We can't reconstruct old, so just run the landmark checks
                # that don't depend on byte-delta.
                if TOP3_GOLDEN_ROW not in existing_content:
                    print(
                        f"[ERROR] {TARGET_URI} present but TOP3_GOLDEN_ROW "
                        "shape drifted"
                    )
                    return 1
                if Q1_ANCHOR_LINE not in existing_content:
                    print(
                        f"[ERROR] {TARGET_URI} present but Q1_ANCHOR_LINE "
                        "shape drifted"
                    )
                    return 1
            except Exception as e:
                print(f"[ERROR] idempotency re-validation failed: {e}")
                return 1
            print(
                f"[UNCHANGED] {TARGET_URI} already present + shapes match; "
                "0 writes"
            )
            return 0

        # Verify target system_design slug exists (fail loud on drift).
        sd = conn.execute(
            "SELECT id, slug FROM system_designs WHERE slug = ?",
            (TARGET_SD_SLUG,),
        ).fetchone()
        if sd is None:
            print(f"[ERROR] sd://{TARGET_SD_SLUG} missing from system_designs")
            return 1
        print(f"[OK] sd://{TARGET_SD_SLUG} verified: id={sd[0]}")

        # Apply both inserts and validate.
        new_content = apply_inserts(existing_content)
        validate(new_content, existing_content)
        delta_b = (
            len(new_content.encode("utf-8"))
            - len(existing_content.encode("utf-8"))
        )
        print(
            f"[OK] content validated: old_chars={len(existing_content)} "
            f"new_chars={len(new_content)} delta_bytes={delta_b:+d}"
        )

        # UPDATE.
        now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        new_hash = sha256_bytes(new_content)
        conn.execute(
            "UPDATE company_documents "
            "SET content = ?, content_hash = ?, updated_at = ? "
            "WHERE id = ?",
            (new_content, new_hash, now, DOC_ID),
        )
        conn.commit()
        print(
            f"[UPDATE] id={DOC_ID} chars={len(new_content)} "
            f"hash={new_hash[:12]}..."
        )

        # Post-write readback.
        post = conn.execute(
            "SELECT content, updated_at FROM company_documents WHERE id = ?",
            (DOC_ID,),
        ).fetchone()
        if post[0] != new_content:
            print("[ERROR] post-write readback mismatch")
            return 1
        print(f"[OK] post-write readback verified; updated_at={post[1]!r}")

        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
