"""Retrofit Meta MLSD SD id=41 (Reels Golden) overview with Drawer 入口 header (T-P0-846).

Per T-P0-846 ([Meta-MLSD J]). Target: system_designs.id=41,
slug='meta-reels-golden',
title='Meta MLSD Golden Example: Reels Home Feed Recommendation (45min walkthrough)'.

Prepends a Drawer 入口 顶部 section (5 entries, NO self-link
sd://meta-reels-golden) + horizontal rule to the `overview` column ONLY.
The other 8 content columns (architecture / dataflow / formulas /
production_constraints / tradeoffs / defense / verbal_outline / cheat_sheet)
remain byte-identical pre vs post.

DRAWER URI INVENTORY (5 entries, NO self-link sd://meta-reels-golden):
  - cd://94                                  (Family Taxonomy + 13 Question Cards)
  - cd://95                                  (Cross-cutting 积木库)
  - cd://96                                  (45min Playbook + 4 Strong Moments)
  - cd://97                                  (T-A: RecSys 核心模型 8 工作)
  - sd://interview-recommendation-system     (general RecSys SD cookbook)

DEPS resolved at runtime (fail loud if any drift):
  - cd://94, cd://95, cd://96, cd://97 must exist with expected title fragments
  - sd://interview-recommendation-system slug resolves

Idempotency: sentinel <!-- META_MLSD_DRAWER_HEADER_SD41_20260512 --> placed
as the first line of overview. On re-run, if sentinel present + overview
byte-identical to the rebuilt content, report UNCHANGED with 0 writes.

Self-link contract: sd://meta-reels-golden (self) must NOT appear in the
prepended Drawer 入口 block (checked via post-build scan over the prepended
block only — the body may keep any pre-existing inline cross-references).

Column-isolation: pre-edit snapshots of all 8 sibling content columns are
captured and compared byte-for-byte after the UPDATE. Any drift aborts with
a non-zero exit code (the UPDATE is in the same transaction as the readback,
but we use the readback solely as a tripwire — the SQL only touches
overview + updated_at).

Style: NO emoji; blockquote `> ` prefix on every drawer line; `**[label](URI)**`
bold-link format; horizontal rule `---` separator before body.
"""
from __future__ import annotations

import hashlib
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"

SENTINEL = "<!-- META_MLSD_DRAWER_HEADER_SD41_20260512 -->"

SD_ID = 41
EXPECTED_SLUG = "meta-reels-golden"
EXPECTED_TITLE = (
    "Meta MLSD Golden Example: Reels Home Feed Recommendation "
    "(45min walkthrough)"
)

# Sibling drawer references (5 entries, NO self-link sd://meta-reels-golden).
FAMILY_TAXONOMY_DOC_ID = 94    # 13 题 Family Taxonomy
CROSS_CUTTING_DOC_ID = 95      # Cross-cutting 积木库
MAIN_HUB_DOC_ID = 96           # 45min Playbook + 4 Strong Moments
RECSYS_MODELS_DOC_ID = 97      # T-A: RecSys 核心模型 8 工作 (per T-P0-842)
SD_GENERIC_RECSYS = "interview-recommendation-system"

DRAWER_INDEX = (
    f"> ## Drawer 入口（点击展开详读）\n"
    f">\n"
    f"> | 入口 | 内容 | 何时打开 |\n"
    f"> | --- | --- | --- |\n"
    f"> | **[13 题 Family Taxonomy](cd://{FAMILY_TAXONOMY_DOC_ID})** "
    f"| Q1-Q12 卡片 + 题型识别 | 拿到新题，30 秒锁定 family |\n"
    f"> | **[Cross-cutting 9 ML 积木](cd://{CROSS_CUTTING_DOC_ID})** "
    f"| Two-Tower / IPS / LLM-teacher / Calibration | 套通用 ML 模块 |\n"
    f"> | **[45min Playbook + 4 Strong Moments](cd://{MAIN_HUB_DOC_ID})** "
    f"| 节奏 + 元结构 + meta-rules | 整体 framework |\n"
    f"> | **[RecSys 核心模型 8 工作](cd://{RECSYS_MODELS_DOC_ID})** "
    f"| DCN / DLRM / HSTU / RankMixer / RQ-VAE / CF | 模型层面 deep-dive |\n"
    f"> | **[通用 RecSys SD Cookbook](sd://{SD_GENERIC_RECSYS})** "
    f"| Two-Tower + DLRM + MMoE 教科书 | 想看通用 RecSys 而不止 Meta |\n"
    f"\n"
    f"---\n"
    f"\n"
)

PREPENDED_BLOCK = f"{SENTINEL}\n\n{DRAWER_INDEX}"

# Columns that MUST remain byte-identical pre/post (column-isolation).
PRESERVED_COLUMNS = (
    "architecture",
    "dataflow",
    "formulas",
    "production_constraints",
    "tradeoffs",
    "defense",
    "verbal_outline",
    "cheat_sheet",
)


def sha256_bytes(text: str | None) -> str:
    """Return SHA-256 hex digest of UTF-8 encoded string (NULL -> empty)."""
    if text is None:
        return sha256_bytes("")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_overview(existing_overview: str) -> str:
    """Prepend sentinel + drawer index to overview (idempotent)."""
    if existing_overview.startswith(SENTINEL):
        body = existing_overview[len(PREPENDED_BLOCK):]
    else:
        body = existing_overview
    return f"{PREPENDED_BLOCK}{body}"


def validate_overview(content: str, body: str) -> None:
    """Sanity checks mirroring T-P0-846 acceptance criteria."""
    # AC #1: overview STARTS WITH sentinel; first visible line is Drawer 入口.
    if not content.startswith(SENTINEL):
        raise RuntimeError(
            f"sentinel must be first line of overview; got {content[:80]!r}"
        )
    lines = content.splitlines()
    first_visible = next(
        (
            ln
            for ln in lines[1:]
            if ln.strip() and not ln.strip().startswith("<!--")
        ),
        None,
    )
    if first_visible is None or not first_visible.startswith("> ## Drawer 入口"):
        raise RuntimeError(
            f"first visible line should be Drawer 入口 blockquote; "
            f"got {first_visible!r}"
        )

    # AC #2: 5 unique drawer URIs each appear exactly once in PREPENDED BLOCK.
    drawer_uris = [
        f"cd://{FAMILY_TAXONOMY_DOC_ID}",
        f"cd://{CROSS_CUTTING_DOC_ID}",
        f"cd://{MAIN_HUB_DOC_ID}",
        f"cd://{RECSYS_MODELS_DOC_ID}",
        f"sd://{SD_GENERIC_RECSYS}",
    ]
    for uri in drawer_uris:
        c = PREPENDED_BLOCK.count(uri)
        if c != 1:
            raise RuntimeError(
                f"drawer URI {uri!r} appears {c}x in prepended block; "
                f"expected exactly 1"
            )

    # AC: self-link sd://meta-reels-golden must NOT appear in prepended block.
    self_uri = f"sd://{EXPECTED_SLUG}"
    if self_uri in PREPENDED_BLOCK:
        raise RuntimeError(
            f"self-link violation: {self_uri!r} found in prepended block"
        )

    # AC #3: horizontal rule '---' between blockquote and body.
    if "\n---\n" not in PREPENDED_BLOCK:
        raise RuntimeError(
            "horizontal rule '---' missing between blockquote and body"
        )

    # AC: body preserved verbatim — content must end with body.
    if not content.endswith(body):
        raise RuntimeError(
            "original overview body not preserved verbatim at end of content"
        )

    # AC #5: length in spec range ~3550-3700 (allow margin).
    n_chars = len(content)
    if not (3400 <= n_chars <= 3900):
        raise RuntimeError(
            f"overview char-length {n_chars} not in [3400, 3900]"
        )

    # AC: required body landmarks still present.
    required_body_fragments = [
        "# Reels Home Feed Recommendation",
        "整体节奏哲学",
        "E4 not E5",
    ]
    for frag in required_body_fragments:
        if frag not in content:
            raise RuntimeError(f"body landmark missing: {frag!r}")

    # NO emoji style rule — applied to the prepended block only.
    for ch in PREPENDED_BLOCK:
        cp = ord(ch)
        if (
            0x1F300 <= cp <= 0x1F9FF
            or 0x2600 <= cp <= 0x27BF  # Misc Symbols / Dingbats
        ):
            raise RuntimeError(
                f"emoji-like char detected in prepended block at "
                f"U+{cp:04X}: {ch!r}"
            )


def main() -> int:
    """Retrofit SD id=41 overview with Drawer 入口 header (idempotent)."""
    if not DB_PATH.exists():
        print(f"[ERROR] db not found: {DB_PATH}")
        return 1

    conn = sqlite3.connect(str(DB_PATH))
    try:
        select_cols = ["id", "slug", "title", "overview"] + list(PRESERVED_COLUMNS)
        row = conn.execute(
            f"SELECT {', '.join(select_cols)} FROM system_designs WHERE id = ?",
            (SD_ID,),
        ).fetchone()
        if row is None:
            print(f"[ERROR] system_designs.id={SD_ID} not found")
            return 1
        existing_id, existing_slug, existing_title, existing_overview = row[:4]
        preserved_pre = dict(zip(PRESERVED_COLUMNS, row[4:], strict=True))

        if existing_slug != EXPECTED_SLUG:
            print(
                f"[ERROR] slug drift: expected {EXPECTED_SLUG!r}, got "
                f"{existing_slug!r}"
            )
            return 1
        if existing_title != EXPECTED_TITLE:
            print(
                f"[ERROR] title drift: expected {EXPECTED_TITLE!r}, got "
                f"{existing_title!r}"
            )
            return 1
        if existing_overview is None:
            print(f"[ERROR] overview is NULL for id={SD_ID}")
            return 1
        print(
            f"[OK] target: id={existing_id} slug={existing_slug!r} "
            f"overview_chars={len(existing_overview)}"
        )

        # Defensive sibling backlink check (cd:// + sd://).
        sibling_cd_specs = [
            (FAMILY_TAXONOMY_DOC_ID, "Family Taxonomy"),
            (CROSS_CUTTING_DOC_ID, "Cross-cutting"),
            (MAIN_HUB_DOC_ID, "45min Playbook"),
            (RECSYS_MODELS_DOC_ID, "推荐系统核心模型"),
        ]
        for cd_id, title_frag in sibling_cd_specs:
            r = conn.execute(
                "SELECT id, title FROM company_documents WHERE id = ?",
                (cd_id,),
            ).fetchone()
            if r is None or title_frag not in r[1]:
                print(
                    f"[ERROR] cd://{cd_id} ({title_frag}) backlink "
                    f"missing or drifted: row={r!r}"
                )
                return 1
            print(f"[OK] cd://{cd_id} verified: {r[1]!r}")

        sd_check = conn.execute(
            "SELECT id, slug FROM system_designs WHERE slug = ?",
            (SD_GENERIC_RECSYS,),
        ).fetchone()
        if sd_check is None:
            print(f"[ERROR] sd://{SD_GENERIC_RECSYS} missing")
            return 1
        print(f"[OK] sd://{SD_GENERIC_RECSYS} verified: id={sd_check[0]}")

        # Strip prepended block (if sentinel present) before validation.
        if existing_overview.startswith(SENTINEL):
            body_raw = existing_overview[len(PREPENDED_BLOCK):]
        else:
            body_raw = existing_overview

        new_overview = build_overview(existing_overview)
        validate_overview(new_overview, body_raw)
        print(
            f"[OK] overview validated: chars={len(new_overview)} "
            f"bytes={len(new_overview.encode('utf-8'))} "
            f"delta={len(new_overview) - len(existing_overview):+d}"
        )

        # Idempotency gate.
        if new_overview == existing_overview:
            print(
                "[UNCHANGED] sentinel present + overview byte-identical; "
                "0 writes"
            )
            return 0

        if existing_overview.startswith(SENTINEL):
            print(
                "[WARN] sentinel present but overview drifted; will re-write"
            )

        # Recompute content_hash over a stable serialization of all content
        # columns (matches existing convention: hash spans column payloads).
        full_payload = (
            new_overview
            + "\n---ARCHITECTURE---\n"
            + (preserved_pre["architecture"] or "")
            + "\n---DATAFLOW---\n"
            + (preserved_pre["dataflow"] or "")
        )
        new_hash = sha256_bytes(full_payload)

        # UPDATE overview + updated_at + content_hash. Other 8 columns NOT
        # touched by the UPDATE statement (column-isolation by construction).
        now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            "UPDATE system_designs "
            "SET overview = ?, content_hash = ?, updated_at = ? "
            "WHERE id = ?",
            (new_overview, new_hash, now, SD_ID),
        )
        conn.commit()
        print(
            f"[UPDATE] id={SD_ID} overview_old={len(existing_overview)} "
            f"overview_new={len(new_overview)} "
            f"delta={len(new_overview) - len(existing_overview):+d} "
            f"hash={new_hash[:12]}..."
        )

        # Post-write column-isolation tripwire: re-read all 8 preserved
        # columns and assert byte-identical.
        post = conn.execute(
            f"SELECT overview, updated_at, "
            f"{', '.join(PRESERVED_COLUMNS)} "
            f"FROM system_designs WHERE id = ?",
            (SD_ID,),
        ).fetchone()
        post_overview, post_updated_at = post[0], post[1]
        post_preserved = dict(
            zip(PRESERVED_COLUMNS, post[2:], strict=True)
        )
        if post_overview != new_overview:
            print("[ERROR] post-write overview readback mismatch")
            return 1
        for col in PRESERVED_COLUMNS:
            pre_val = preserved_pre[col]
            post_val = post_preserved[col]
            if pre_val != post_val:
                pre_len = len(pre_val) if pre_val else 0
                post_len = len(post_val) if post_val else 0
                print(
                    f"[ERROR] column-isolation violation: {col!r} "
                    f"pre_len={pre_len} post_len={post_len}"
                )
                return 1
            print(
                f"[OK] column-isolation {col!r}: "
                f"unchanged ({len(pre_val) if pre_val else 0} chars)"
            )

        if not post_updated_at.startswith(
            datetime.now(UTC).strftime("%Y-%m-%d")
        ):
            print(
                f"[WARN] updated_at not today's date: {post_updated_at!r} "
                f"(may be timezone drift, non-fatal)"
            )
        print(f"[OK] post-write readback verified; updated_at={post_updated_at!r}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
