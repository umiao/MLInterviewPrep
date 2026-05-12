"""Retrofit Meta MLSD doc 95 with Drawer 入口 顶部 section (T-P0-844).

Per T-P0-844 ([Meta-MLSD H]). Target: company_documents.id=95, company_id=31,
title '[Meta-MLSD] Cross-cutting 积木库 (drawer)'.

Prepends a prominent Drawer 入口 section + horizontal rule BEFORE the existing
body. Existing content (sentinel <!-- META_MLSD_CROSS_CUTTING_20260511 --> +
H1 + 9-piece markdown table + Section 2 expanded notes + Section 3 decision
tree) is preserved verbatim. Pre-existing inline `sd://meta-reels-golden` and
`cd://94` references in the body are KEPT as-is (inline narrative, not a
drawer index — dedupe is not required per spec).

DRAWER URI INVENTORY (5 entries, NO self-link cd://95):
  - sd://meta-reels-golden                  (T-P0-837)
  - cd://94                                  (Family Taxonomy + 13 Question Cards)
  - cd://96                                  (45min Playbook)
  - cd://97                                  (T-A: RecSys 核心模型 8 工作)
  - sd://interview-recommendation-system     (general RecSys SD cookbook)

DEPS resolved at runtime (fail loud if any drift):
  - cd://94, cd://96, cd://97 must exist with expected title fragments
  - sd://meta-reels-golden, sd://interview-recommendation-system slugs resolve

Idempotency: sentinel <!-- META_MLSD_DRAWER_HEADER_95_20260512 --> placed as
the first content line. On re-run, if sentinel present + content byte-identical,
report UNCHANGED with 0 writes.

Self-link contract: cd://95 must NOT appear in the Drawer 入口 section
(checked via post-write scan over the prepended block only — body may keep
its existing inline cross-references unchanged).

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

SENTINEL = "<!-- META_MLSD_DRAWER_HEADER_95_20260512 -->"

COMPANY_ID = 31  # Meta
DOC_ID = 95
EXPECTED_TITLE = "[Meta-MLSD] Cross-cutting 积木库 (drawer)"

# Sibling drawer references (5 entries, NO self-link cd://95).
FAMILY_TAXONOMY_DOC_ID = 94   # 13 题 Family Taxonomy
MAIN_HUB_DOC_ID = 96          # 45min Playbook + 4 Strong Moments
RECSYS_MODELS_DOC_ID = 97     # T-A: RecSys 核心模型 8 工作 (per T-P0-842)
SD_REELS_GOLDEN = "meta-reels-golden"
SD_GENERIC_RECSYS = "interview-recommendation-system"

DRAWER_INDEX = f"""> ## Drawer 入口（点击展开详读）
>
> | 入口 | 内容 | 何时打开 |
> | --- | --- | --- |
> | **[Reels Golden Example (45min 全文)](sd://{SD_REELS_GOLDEN})** | 八段台词 + 4 Strong Moments verbatim | 想看 DLRM/multi-task/multimodal 实战编排 |
> | **[13 题 Family Taxonomy](cd://{FAMILY_TAXONOMY_DOC_ID})** | Q1-Q12 卡片 + 题型识别 | 拿到新题，30 秒锁定 family |
> | **[45min Playbook + 4 Strong Moments](cd://{MAIN_HUB_DOC_ID})** | 节奏 + 元结构 + meta-rules | 整体 framework |
> | **[RecSys 核心模型 8 工作](cd://{RECSYS_MODELS_DOC_ID})** | DCN / DLRM / HSTU / RankMixer / RQ-VAE / CF | 模型层面 deep-dive |
> | **[通用 RecSys SD Cookbook](sd://{SD_GENERIC_RECSYS})** | Two-Tower + DLRM + MMoE 教科书 | 想看通用 RecSys 而不止 Meta |

---

"""

PREPENDED_BLOCK = f"{SENTINEL}\n\n{DRAWER_INDEX}"


def sha256_bytes(text: str) -> str:
    """Return SHA-256 hex digest of UTF-8 encoded string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_content(existing_body: str) -> str:
    """Assemble final content = sentinel + drawer index + existing body verbatim."""
    return f"{PREPENDED_BLOCK}{existing_body}"


def validate_content(content: str, existing_body: str) -> None:
    """Sanity checks mirroring T-P0-844 acceptance criteria."""
    # AC: sentinel present and is first line of content.
    if not content.startswith(SENTINEL):
        raise RuntimeError(
            f"sentinel must be first line of content; got {content[:80]!r}"
        )

    # AC: Drawer 入口 blockquote is the first markdown-visible (non-comment)
    # line after sentinel + blank.
    lines = content.splitlines()
    if not lines or lines[0] != SENTINEL:
        raise RuntimeError("expected sentinel as first line")
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

    # AC #1: length(content) in [5500, 7200] (upper bumped for T-P1-850 10th 积木).
    n_chars = len(content)
    if not (5500 <= n_chars <= 7200):
        raise RuntimeError(
            f"content char-length {n_chars} not in [5500, 7200]"
        )

    # AC #3: 5 unique drawer URIs each appear exactly once IN PREPENDED BLOCK;
    # and cd://95 (self) must NOT appear in PREPENDED BLOCK at all.
    drawer_uris = [
        f"sd://{SD_REELS_GOLDEN}",
        f"cd://{FAMILY_TAXONOMY_DOC_ID}",
        f"cd://{MAIN_HUB_DOC_ID}",
        f"cd://{RECSYS_MODELS_DOC_ID}",
        f"sd://{SD_GENERIC_RECSYS}",
    ]
    for uri in drawer_uris:
        if uri not in PREPENDED_BLOCK:
            raise RuntimeError(
                f"drawer URI missing from prepended block: {uri!r}"
            )
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

    # AC #4: markdown horizontal rule '---' separator between Drawer 入口 table
    # and body.
    if "\n---\n" not in PREPENDED_BLOCK:
        raise RuntimeError("horizontal rule '---' missing from prepended block")

    # AC #5: body preserved verbatim — content must end with existing_body
    # (no destructive edit).
    if not content.endswith(existing_body):
        raise RuntimeError(
            "existing body not preserved verbatim at end of content"
        )

    # AC #5 extension: required body landmarks still present.
    required_body_fragments = [
        "<!-- META_MLSD_CROSS_CUTTING_20260511 -->",
        "# Meta MLSD - Cross-cutting 积木库 (drawer)",
        "## 1. 积木总表",
        "Two-tower retrieval",
    ]
    for frag in required_body_fragments:
        if frag not in content:
            raise RuntimeError(f"body landmark missing: {frag!r}")

    # NO emoji style rule — applied to the prepended block only. Existing
    # body (preserved verbatim) is untouched per spec.
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
    """Retrofit doc 95 with Drawer 入口 header (idempotent)."""
    if not DB_PATH.exists():
        print(f"[ERROR] db not found: {DB_PATH}")
        return 1

    conn = sqlite3.connect(str(DB_PATH))
    try:
        # 1. Fetch + verify target row.
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

        # 2. Idempotency gate: sentinel already present => UNCHANGED.
        if existing_content.startswith(SENTINEL):
            rebuilt = build_content(
                existing_content[len(PREPENDED_BLOCK):]
            )
            if rebuilt == existing_content:
                print(
                    "[UNCHANGED] sentinel present + content byte-identical; "
                    "0 writes"
                )
                validate_content(
                    existing_content,
                    existing_content[len(PREPENDED_BLOCK):],
                )
                print("[OK] post-validation passed on existing content")
                return 0
            print(
                "[WARN] sentinel present but content drifted; will re-write"
            )
            body_to_preserve = existing_content[len(PREPENDED_BLOCK):]
        else:
            body_to_preserve = existing_content

        # 3. Defensive sibling backlink check (cd:// + sd://).
        sibling_specs = [
            (FAMILY_TAXONOMY_DOC_ID, "Family Taxonomy"),
            (MAIN_HUB_DOC_ID, "45min Playbook"),
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

        # 4. Build + validate new content.
        content = build_content(body_to_preserve)
        validate_content(content, body_to_preserve)
        print(
            f"[OK] content validated: chars={len(content)} "
            f"bytes={len(content.encode('utf-8'))}"
        )

        # 5. UPDATE.
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

        # 6. Post-write re-read sanity.
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
