"""Retrofit Meta MLSD doc 97 with sd://meta-top3-comments-golden drawer row (T-P0-858).

One surgical insert into company_documents.id=97 ('推荐系统核心模型复习笔记 8 工作 + 脉络')
content (does NOT replace any existing structure, only inserts a single line):

  Drawer 入口 table (顶部 blockquote H2 table): new row immediately AFTER the
  sd://meta-reels-golden row (golden examples grouped together at top of table,
  ahead of the cd://94/95/96 sibling block and sd://interview-recommendation-system).

  New row:
    > | **[Top-3 Comments Golden Example (45min)](sd://meta-top3-comments-golden)** | 把 8 工作 (DCN/DLRM/MMOE/multi-task 等) 嵌入完整 45min 编排 | 想看模型层 → 走完整脚本 |

Idempotency: detect `sd://meta-top3-comments-golden` already present in content;
on re-run report UNCHANGED with 0 writes (skip insert).

Self-link contract preserved: cd://97 must remain absent from the Drawer 入口
prepended block.

Style: NO emoji; blockquote `> ` prefix on drawer row; `**[label](URI)**` bold-link
format consistent with surrounding rows.
"""
from __future__ import annotations

import hashlib
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"

COMPANY_ID = 31  # Meta
DOC_ID = 97
EXPECTED_TITLE = "[Meta-MLSD] 推荐系统核心模型复习笔记 (8 工作 + 脉络)"

TARGET_SD_SLUG = "meta-top3-comments-golden"
TARGET_URI = f"sd://{TARGET_SD_SLUG}"

# Anchor row: insertion point is immediately AFTER this existing row.
REELS_GOLDEN_ROW = (
    "> | **[Reels Golden Example (45min 全文)](sd://meta-reels-golden)** "
    "| 八段台词 + 4 Strong Moments verbatim "
    "| 想看 DLRM/multi-task/multimodal 实战编排 |"
)
TOP3_GOLDEN_ROW = (
    f"> | **[Top-3 Comments Golden Example (45min)]({TARGET_URI})** "
    "| 把 8 工作 (DCN/DLRM/MMOE/multi-task 等) 嵌入完整 45min 编排 "
    "| 想看模型层 → 走完整脚本 |"
)


def sha256_bytes(text: str) -> str:
    """Return SHA-256 hex digest of UTF-8 encoded string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def apply_insert(content: str) -> str:
    """Insert the new drawer row directly after the reels-golden row."""
    if REELS_GOLDEN_ROW not in content:
        raise RuntimeError(
            "drawer anchor row 'Reels Golden Example' not found in content"
        )
    if content.count(REELS_GOLDEN_ROW) != 1:
        raise RuntimeError(
            f"drawer anchor row appears {content.count(REELS_GOLDEN_ROW)}x; "
            "expected exactly 1"
        )
    replacement = f"{REELS_GOLDEN_ROW}\n{TOP3_GOLDEN_ROW}"
    return content.replace(REELS_GOLDEN_ROW, replacement, 1)


def validate(new_content: str, old_content: str) -> None:
    """Sanity checks mirroring T-P0-858 acceptance criteria."""
    # AC #1: Drawer 入口 table contains the new row pointing to TARGET_URI.
    if TOP3_GOLDEN_ROW not in new_content:
        raise RuntimeError("new drawer row not present after insertion")

    # AC: byte delta is bounded — only 1 markdown line added.
    delta_bytes = (
        len(new_content.encode("utf-8")) - len(old_content.encode("utf-8"))
    )
    if not (0 < delta_bytes < 400):
        raise RuntimeError(
            f"content byte delta {delta_bytes:+d} out of (0, 400)"
        )

    # AC #2: self-URI cd://97 NOT in Drawer 入口 block.
    # Drawer block = first occurrence of '> ## Drawer 入口' through the
    # '---' immediately following the table.
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

    # AC: new top3 row sits immediately after the reels-golden row.
    reels_idx = new_content.find(REELS_GOLDEN_ROW)
    top3_idx = new_content.find(TOP3_GOLDEN_ROW)
    expected_top3_idx = reels_idx + len(REELS_GOLDEN_ROW) + 1  # "\n"
    if top3_idx != expected_top3_idx:
        raise RuntimeError(
            f"top3 row not adjacent to reels row: "
            f"reels_end={reels_idx + len(REELS_GOLDEN_ROW)} "
            f"top3_start={top3_idx}"
        )

    # AC: new top3 row sits BEFORE the cd://94 row (which is the next row).
    fam_row_marker = "[13 题 Family Taxonomy](cd://94)"
    fam_idx = new_content.find(fam_row_marker)
    if not (top3_idx < fam_idx):
        raise RuntimeError(
            f"top3 row not placed before cd://94 family row: "
            f"top3_idx={top3_idx} fam_idx={fam_idx}"
        )

    # AC #3: doc body (RecSys 8 工作 + 脉络) preserved.
    required_fragments = [
        "<!-- META_MLSD_RECSYS_MODELS_20260512 -->",
        "# 推荐系统核心模型复习笔记",
        "## 1. DCN v1 / v2 (Deep & Cross Network) — 显式特征交叉的 Cross Network 路线",
        "## 2. DLRM (Deep Learning Recommendation Model) — Meta 2019 工业级 CTR 基线",
        "## 3. Collaborative Filtering 主流方法和策略",
    ]
    for frag in required_fragments:
        if frag not in new_content:
            raise RuntimeError(f"landmark missing post-insert: {frag!r}")

    # NO emoji style rule on the inserted row.
    for ch in TOP3_GOLDEN_ROW:
        cp = ord(ch)
        if (
            0x1F300 <= cp <= 0x1F9FF
            or 0x2600 <= cp <= 0x27BF
        ):
            raise RuntimeError(
                f"emoji-like char in TOP3_GOLDEN_ROW at U+{cp:04X}: {ch!r}"
            )


def main() -> int:
    """Retrofit doc 97 with one sd://meta-top3-comments-golden drawer row."""
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
            if TOP3_GOLDEN_ROW not in existing_content:
                print(
                    f"[ERROR] {TARGET_URI} present but TOP3_GOLDEN_ROW "
                    "shape drifted"
                )
                return 1
            print(
                f"[UNCHANGED] {TARGET_URI} already present + shape matches; "
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

        # Apply insert and validate.
        new_content = apply_insert(existing_content)
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
