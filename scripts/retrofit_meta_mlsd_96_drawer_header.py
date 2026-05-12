"""Retrofit Meta MLSD doc 96 (Main Hub) with Drawer 入口 header + dedupe (T-P0-845).

Per T-P0-845 ([Meta-MLSD I]). Target: company_documents.id=96, company_id=31,
title '[Meta-MLSD] 45min Playbook + 4 Strong Moments' (is_golden=1, default
first-page Meta MLSD entry).

Two-part edit:
1. Prepend a prominent Drawer 入口 顶部 section (5 entries, NO self-link
   cd://96) + horizontal rule before the body.
2. Dedupe: REMOVE the existing mid-doc 'Section 8 Drawer — 深内容入口' (from
   T-P0-840 initial seed; its 3 entries are now superseded by the new top
   section). Renumber the original 'Section 9. 30 秒判题流程' → 'Section 8.'.

Section 2's inline reference `[Reels Home Feed (45min walkthrough) →](sd://
meta-reels-golden)` is narrative prose, KEPT verbatim (dedupe only applies
to the drawer-index style section).

DRAWER URI INVENTORY (5 entries, NO self-link cd://96):
  - sd://meta-reels-golden                  (T-P0-837)
  - cd://94                                  (Family Taxonomy + 13 Question Cards)
  - cd://95                                  (Cross-cutting 积木库)
  - cd://97                                  (T-A: RecSys 核心模型 8 工作)
  - sd://interview-recommendation-system     (general RecSys SD cookbook)

DEPS resolved at runtime (fail loud if any drift):
  - cd://94, cd://95, cd://97 must exist with expected title fragments
  - sd://meta-reels-golden, sd://interview-recommendation-system slugs resolve

Idempotency: sentinel <!-- META_MLSD_DRAWER_HEADER_96_20260512 --> placed as
the first content line. The body transform (drop old Section 8 + renumber)
is itself idempotent. On re-run, if sentinel present + content byte-identical,
report UNCHANGED with 0 writes.

Self-link contract: cd://96 must NOT appear in the prepended Drawer 入口
section (checked via post-write scan over the prepended block only — body
may keep any pre-existing inline cross-references unchanged).

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

SENTINEL = "<!-- META_MLSD_DRAWER_HEADER_96_20260512 -->"

COMPANY_ID = 31  # Meta
DOC_ID = 96
EXPECTED_TITLE = "[Meta-MLSD] 45min Playbook + 4 Strong Moments"

# Sibling drawer references (5 entries, NO self-link cd://96).
FAMILY_TAXONOMY_DOC_ID = 94    # 13 题 Family Taxonomy
CROSS_CUTTING_DOC_ID = 95      # Cross-cutting 积木库
RECSYS_MODELS_DOC_ID = 97      # T-A: RecSys 核心模型 8 工作 (per T-P0-842)
SD_REELS_GOLDEN = "meta-reels-golden"
SD_GENERIC_RECSYS = "interview-recommendation-system"

# Old Section 8 dedupe markers (from T-P0-840 initial seed).
SECTION_8_HEADER_OLD = "## 8. Drawer — 深内容入口"
SECTION_9_HEADER_OLD = "## 9. 30 秒判题流程"
SECTION_8_HEADER_NEW = "## 8. 30 秒判题流程"

DRAWER_INDEX = f"""> ## Drawer 入口（点击展开详读）
>
> | 入口 | 内容 | 何时打开 |
> | --- | --- | --- |
> | **[Reels Golden Example (45min 全文)](sd://{SD_REELS_GOLDEN})** | 八段台词 + 4 Strong Moments verbatim | 想看 DLRM/multi-task/multimodal 实战编排 |
> | **[13 题 Family Taxonomy](cd://{FAMILY_TAXONOMY_DOC_ID})** | Q1-Q12 卡片 + 题型识别 | 拿到新题，30 秒锁定 family |
> | **[Cross-cutting 9 ML 积木](cd://{CROSS_CUTTING_DOC_ID})** | Two-Tower / IPS / LLM-teacher / Calibration | 套通用 ML 模块 |
> | **[RecSys 核心模型 8 工作](cd://{RECSYS_MODELS_DOC_ID})** | DCN / DLRM / HSTU / RankMixer / RQ-VAE / CF | 模型层面 deep-dive |
> | **[通用 RecSys SD Cookbook](sd://{SD_GENERIC_RECSYS})** | Two-Tower + DLRM + MMoE 教科书 | 想看通用 RecSys 而不止 Meta |

---

"""

PREPENDED_BLOCK = f"{SENTINEL}\n\n{DRAWER_INDEX}"


def sha256_bytes(text: str) -> str:
    """Return SHA-256 hex digest of UTF-8 encoded string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def transform_body(body: str) -> str:
    """Drop old Section 8 drawer + renumber Section 9 → Section 8 (idempotent)."""
    # Idempotent: if already transformed, no-op.
    if SECTION_8_HEADER_OLD not in body:
        if SECTION_8_HEADER_NEW in body:
            return body
        raise RuntimeError(
            "body lacks both old Section 8 header "
            f"{SECTION_8_HEADER_OLD!r} and post-transform header "
            f"{SECTION_8_HEADER_NEW!r}; refusing to guess"
        )

    start = body.find(SECTION_8_HEADER_OLD)
    next_sec = body.find(SECTION_9_HEADER_OLD, start)
    if next_sec == -1:
        raise RuntimeError(
            f"Section 9 marker {SECTION_9_HEADER_OLD!r} not found after "
            f"Section 8 at offset {start}"
        )

    # Remove block from `## 8. Drawer ...` through (exclusive) `## 9. ...`.
    # The original `---\n\n` separator that preceded Section 8 is preserved
    # (it now separates Section 7 from the renumbered Section 8).
    trimmed = body[:start] + body[next_sec:]
    return trimmed.replace(SECTION_9_HEADER_OLD, SECTION_8_HEADER_NEW, 1)


def build_content(existing_body: str) -> str:
    """Assemble final content = sentinel + drawer index + transformed body."""
    return f"{PREPENDED_BLOCK}{transform_body(existing_body)}"


def validate_content(content: str, transformed_body: str) -> None:
    """Sanity checks mirroring T-P0-845 acceptance criteria."""
    # AC #1: content STARTS WITH `> ## Drawer 入口` (after sentinel + blank).
    if not content.startswith(SENTINEL):
        raise RuntimeError(
            f"sentinel must be first line of content; got {content[:80]!r}"
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

    # AC #2: 5 unique drawer URIs each appear exactly once IN PREPENDED BLOCK;
    # and cd://96 (self) must NOT appear in PREPENDED BLOCK at all.
    drawer_uris = [
        f"sd://{SD_REELS_GOLDEN}",
        f"cd://{FAMILY_TAXONOMY_DOC_ID}",
        f"cd://{CROSS_CUTTING_DOC_ID}",
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

    self_uri = f"cd://{DOC_ID}"
    if self_uri in PREPENDED_BLOCK:
        raise RuntimeError(
            f"self-link violation: {self_uri!r} found in prepended block"
        )

    # AC #3: old Section 8 header fully removed.
    if SECTION_8_HEADER_OLD in content:
        raise RuntimeError(
            f"dedupe failed: {SECTION_8_HEADER_OLD!r} still present in content"
        )

    # AC #4: Section 9 renumbered to Section 8.
    if SECTION_9_HEADER_OLD in content:
        raise RuntimeError(
            f"renumber failed: {SECTION_9_HEADER_OLD!r} still present"
        )
    if SECTION_8_HEADER_NEW not in content:
        raise RuntimeError(
            f"renumber failed: {SECTION_8_HEADER_NEW!r} not found in content"
        )

    # AC #5: H2 count = 1 (Drawer 入口 inside blockquote, `> ## `) + 8
    # (Sections 1..8). Both `## ` and `> ## ` are counted via lines starting
    # with `## ` after stripping leading `> `.
    h2_lines = [
        ln for ln in lines
        if ln.lstrip("> ").startswith("## ")
    ]
    if len(h2_lines) != 9:
        raise RuntimeError(
            f"expected 9 H2 headings (1 Drawer 入口 + 8 sections); "
            f"got {len(h2_lines)}: {h2_lines}"
        )
    # Verify sections 1..8 numeric headers all present (in body, not blockquote).
    body_h2 = [ln for ln in lines if ln.startswith("## ")]
    for n in range(1, 9):
        if not any(ln.startswith(f"## {n}.") for ln in body_h2):
            raise RuntimeError(
                f"missing body section header `## {n}.` in renumbered content"
            )

    # AC #6: length range ~7000-8500 chars (spec ~7800-8200 bytes; allow
    # margin since len() counts chars not bytes).
    n_chars = len(content)
    if not (7000 <= n_chars <= 8500):
        raise RuntimeError(
            f"content char-length {n_chars} not in [7000, 8500]"
        )

    # AC: body preserved verbatim — content must end with transformed_body
    # (no destructive edit beyond the documented Section 8 dedupe).
    if not content.endswith(transformed_body):
        raise RuntimeError(
            "transformed body not preserved verbatim at end of content"
        )

    # AC: required body landmarks still present.
    required_body_fragments = [
        "<!-- META_MLSD_MAIN_HUB_20260511 -->",
        "# Meta MLSD 45-min Playbook",
        "## 1. 节奏 Timing Skeleton (45min)",
        "## 2. 4 Strong Moments",
        "Strong Moment #1",
        "Strong Moment #4",
        "## 7. E4 标准 vs E5 加分上限",
        # Inline narrative reference in Section 2 must survive.
        "[Reels Home Feed (45min walkthrough, 8 段台词 verbatim) →]"
        f"(sd://{SD_REELS_GOLDEN})",
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
    """Retrofit doc 96 with Drawer 入口 header + dedupe (idempotent)."""
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

        # Strip prepended block (if sentinel present) before transforming body.
        if existing_content.startswith(SENTINEL):
            body_raw = existing_content[len(PREPENDED_BLOCK):]
        else:
            body_raw = existing_content

        # Defensive sibling backlink check (cd:// + sd://).
        sibling_specs = [
            (FAMILY_TAXONOMY_DOC_ID, "Family Taxonomy"),
            (CROSS_CUTTING_DOC_ID, "Cross-cutting"),
            (RECSYS_MODELS_DOC_ID, "推荐系统核心模型"),
        ]
        for cd_id, title_frag in sibling_specs:
            r = conn.execute(
                "SELECT id, title FROM company_documents "
                "WHERE id = ? AND company_id = ?",
                (cd_id, COMPANY_ID),
            ).fetchone()
            if r is None or title_frag not in r[1]:
                print(
                    f"[ERROR] cd://{cd_id} ({title_frag}) backlink "
                    f"missing or drifted: row={r!r}"
                )
                return 1
            print(f"[OK] cd://{cd_id} verified: {r[1]!r}")

        for slug in (SD_REELS_GOLDEN, SD_GENERIC_RECSYS):
            sd = conn.execute(
                "SELECT id, slug FROM system_designs WHERE slug = ?",
                (slug,),
            ).fetchone()
            if sd is None:
                print(f"[ERROR] sd://{slug} missing")
                return 1
            print(f"[OK] sd://{slug} verified: id={sd[0]}")

        # Build + validate new content.
        transformed = transform_body(body_raw)
        content = build_content(body_raw)
        validate_content(content, transformed)
        print(
            f"[OK] content validated: chars={len(content)} "
            f"bytes={len(content.encode('utf-8'))}"
        )

        # Idempotency gate.
        if content == existing_content:
            print(
                "[UNCHANGED] sentinel present + content byte-identical; "
                "0 writes"
            )
            print("[OK] post-validation passed")
            return 0

        if existing_content.startswith(SENTINEL):
            print(
                "[WARN] sentinel present but content drifted; will re-write"
            )

        # UPDATE.
        now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        new_hash = sha256_bytes(content)
        conn.execute(
            "UPDATE company_documents "
            "SET content = ?, content_hash = ?, updated_at = ? "
            "WHERE id = ?",
            (content, new_hash, now, DOC_ID),
        )
        conn.commit()
        old_len = len(existing_content)
        print(
            f"[UPDATE] id={DOC_ID} old_chars={old_len} "
            f"new_chars={len(content)} delta={len(content) - old_len:+d} "
            f"hash={new_hash[:12]}..."
        )

        # Post-write re-read sanity.
        post = conn.execute(
            "SELECT content, updated_at FROM company_documents WHERE id = ?",
            (DOC_ID,),
        ).fetchone()
        if post[0] != content:
            print("[ERROR] post-write content readback mismatch")
            return 1
        if not post[1].startswith(datetime.now(UTC).strftime("%Y-%m-%d")):
            print(
                f"[WARN] updated_at not today's date: {post[1]!r} "
                f"(may be timezone drift, non-fatal)"
            )
        print(f"[OK] post-write readback verified; updated_at={post[1]!r}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
