"""Seed Meta MLSD RecSys core models prep_note (T-P0-842).

Per T-P0-842 ([Meta-MLSD F]). Target: company_documents row for company_id=31
(Meta) titled '[Meta-MLSD] 推荐系统核心模型复习笔记 (8 工作 + 脉络)'.

This is the model-level deep-dive drawer for Meta MLSD prep, referenced from
the main hub (cd://96) and all sibling drawers (94 / 95 / sd://41 via
sibling retrofit tasks T-P0-843..846).

CONTENT STRUCTURE:
  1. Sentinel HTML comment (idempotency gate)
  2. Drawer 入口 section (blockquote + 3-col table + 5 sibling URIs, NO
     self-reference, NO emoji) per
     docs/prep/meta_mlsd_2026-05-12/README.md spec
  3. Horizontal rule
  4. Body = verbatim照搬 source_03_recsys_models.md (read at runtime from
     git-tracked path so any edit to source flows on re-seed)

DRAWER URI INVENTORY (5 entries, all non-self):
  - sd://meta-reels-golden                  (sibling: Reels golden example)
  - cd://94                                  (sibling: Family Taxonomy)
  - cd://95                                  (sibling: Cross-cutting 积木)
  - cd://96                                  (sibling: Main Hub)
  - sd://interview-recommendation-system     (general RecSys SD cookbook)

DEPS (resolved at task start, verified runtime):
  - cd://94, cd://95, cd://96 exist with expected title fragments
  - sd://meta-reels-golden, sd://interview-recommendation-system resolve

DB TARGET: data/mle_prep.db, table=company_documents
  is_golden  = 0
  doc_kind   = 'prep_note'
  source_type = 'manual'

Idempotency: sentinel <!-- META_MLSD_RECSYS_MODELS_20260512 --> gates the
write. Second run = 0 writes when content is byte-identical.

Self-link contract: this script does NOT write 'cd://<new_id>' anywhere in
the content; post-insert sanity scan re-checks against the assigned id.

Style: NO emoji; markdown-native visual prominence; 中文 narration + English
ML terms (照搬 source_03 verbatim, no paraphrase, no math reformatting).
"""
from __future__ import annotations

import hashlib
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"
SOURCE_PATH = (
    REPO_ROOT
    / "docs"
    / "prep"
    / "meta_mlsd_2026-05-12"
    / "source_03_recsys_models.md"
)
SENTINEL = "<!-- META_MLSD_RECSYS_MODELS_20260512 -->"

COMPANY_ID = 31  # Meta
DOC_TITLE = "[Meta-MLSD] 推荐系统核心模型复习笔记 (8 工作 + 脉络)"
DOC_KIND = "prep_note"
SOURCE_TYPE = "manual"
IS_GOLDEN = 0

# Sibling drawer references (NO self-link — this new doc's id is unknown
# until INSERT; sibling tasks T-P0-843..846 will add cd://<new_id> to their
# own drawer index sections, not this one).
FAMILY_DOC_ID = 94  # T-P0-838 Family Taxonomy
JIMU_DOC_ID = 95    # T-P0-839 Cross-cutting 积木
MAIN_HUB_DOC_ID = 96  # T-P0-840 Main hub Playbook
SD_REELS_GOLDEN = "meta-reels-golden"        # T-P0-837
SD_GENERIC_RECSYS = "interview-recommendation-system"

DRAWER_INDEX = f"""> ## Drawer 入口（点击展开详读）
>
> | 入口 | 内容 | 何时打开 |
> | --- | --- | --- |
> | **[Reels Golden Example (45min 全文)](sd://{SD_REELS_GOLDEN})** | 八段台词 + 4 Strong Moments verbatim | 想看 DLRM/multi-task/multimodal 实战编排 |
> | **[13 题 Family Taxonomy](cd://{FAMILY_DOC_ID})** | Q1-Q12 卡片 + 题型识别 | 拿到新题，30 秒锁定 family |
> | **[Cross-cutting 9 ML 积木](cd://{JIMU_DOC_ID})** | Two-Tower / IPS / LLM-teacher / Calibration | 套通用 ML 模块 |
> | **[45min Playbook + 4 Strong Moments](cd://{MAIN_HUB_DOC_ID})** | 节奏 + 元结构 + meta-rules | 整体 framework |
> | **[通用 RecSys SD Cookbook](sd://{SD_GENERIC_RECSYS})** | Two-Tower + DLRM + MMoE 教科书 | 想看通用 RecSys 而不止 Meta |

---

"""


def sha256_bytes(text: str) -> str:
    """Return SHA-256 hex digest of UTF-8 encoded string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_content(source_body: str) -> str:
    """Assemble final content = sentinel + drawer index + body."""
    return f"{SENTINEL}\n\n{DRAWER_INDEX}{source_body}"


def validate_content(content: str) -> None:
    """Cheap structural checks mirroring T-P0-842 acceptance criteria."""
    if SENTINEL not in content:
        raise RuntimeError("sentinel missing")

    # AC #2: byte length in [14000, 20000]. The spec says "length(content)"
    # but cites "source 14KB + drawer index ~1KB" which only makes sense as
    # UTF-8 bytes (source is 10485 chars / 16804 bytes — chars would be
    # ~11KB, well below 14000). Validate bytes.
    n_bytes = len(content.encode("utf-8"))
    if not (14000 <= n_bytes <= 20000):
        raise RuntimeError(
            f"content byte-length {n_bytes} not in [14000, 20000]"
        )

    # AC #3: Drawer 入口 section appears before any body H1 — i.e., the
    # blockquote H2 anchor precedes the first '# ' line.
    lines = content.splitlines()
    drawer_line = next(
        (i for i, ln in enumerate(lines) if ln.startswith("> ## Drawer 入口")),
        None,
    )
    if drawer_line is None:
        raise RuntimeError("Drawer 入口 blockquote H2 anchor missing")
    body_h1_line = next(
        (i for i, ln in enumerate(lines) if ln.startswith("# ")),
        None,
    )
    if body_h1_line is None:
        raise RuntimeError("body H1 missing")
    if drawer_line >= body_h1_line:
        raise RuntimeError(
            f"Drawer 入口 (line {drawer_line}) must precede body H1 "
            f"(line {body_h1_line})"
        )

    # AC #4: 5 unique drawer URIs in the drawer table (sd + cd + cd + cd + sd).
    drawer_uris = [
        f"sd://{SD_REELS_GOLDEN}",
        f"cd://{FAMILY_DOC_ID}",
        f"cd://{JIMU_DOC_ID}",
        f"cd://{MAIN_HUB_DOC_ID}",
        f"sd://{SD_GENERIC_RECSYS}",
    ]
    for uri in drawer_uris:
        if uri not in content:
            raise RuntimeError(f"drawer URI missing: {uri!r}")
    # Each URI appears exactly once (dedupe contract).
    for uri in drawer_uris:
        c = content.count(uri)
        if c != 1:
            raise RuntimeError(
                f"drawer URI {uri!r} appears {c} times; must be exactly 1"
            )

    # AC #5: 10 total '## ' substring matches (9 body H2 + 1 inside-blockquote
    # '> ## Drawer 入口' which still contains '## ' as substring).
    h2_substring_count = content.count("## ")
    if h2_substring_count != 10:
        raise RuntimeError(
            f"expected 10 '## ' substring matches "
            f"(9 body H2 + 1 Drawer 入口), got {h2_substring_count}"
        )
    # Also assert all 8 work titles + 跨工作 H2 anchors are present as
    # standalone body H2 lines (catch any source drift).
    body_h2_lines = [ln for ln in lines if ln.startswith("## ")]
    if len(body_h2_lines) != 9:
        raise RuntimeError(
            f"expected 9 body '## ' H2 lines, got {len(body_h2_lines)}"
        )
    required_h2_fragments = [
        "DCN v1 / v2",
        "DLRM",
        "Collaborative Filtering",
        "多模态 Embedding",
        "Multi-task Head",
        "RQ-VAE",
        "HSTU",
        "RankMixer",
        "跨工作的脉络梳理",
    ]
    for frag in required_h2_fragments:
        if not any(frag in ln for ln in body_h2_lines):
            raise RuntimeError(
                f"body H2 fragment missing from source: {frag!r}"
            )

    # AC #6: at least 4 bold callouts of source_03 style markers.
    callout_markers = ["**核心想法**", "**架构 flow**", "**为什么这样设计**"]
    callout_total = sum(content.count(m) for m in callout_markers)
    if callout_total < 4:
        raise RuntimeError(
            f"need >=4 bold callout markers across {callout_markers}, "
            f"got {callout_total}"
        )

    # NO emoji (style rule). Reject any common emoji codepoints quickly —
    # scan for any char in known emoji blocks.
    for ch in content:
        cp = ord(ch)
        # Coarse: any astral-plane char outside the CJK/math/punctuation we
        # actually use. Specifically reject the Emoticons block, Misc
        # Symbols and Pictographs, Transport and Map, Supplemental Symbols.
        if (
            0x1F300 <= cp <= 0x1F9FF
            or 0x2600 <= cp <= 0x27BF  # Misc Symbols / Dingbats
        ):
            raise RuntimeError(
                f"emoji-like char detected at U+{cp:04X}: {ch!r}"
            )


def main() -> int:
    """Upsert the Meta MLSD RecSys core models doc (idempotent)."""
    if not DB_PATH.exists():
        print(f"[ERROR] db not found: {DB_PATH}")
        return 1
    if not SOURCE_PATH.exists():
        print(f"[ERROR] source markdown not found: {SOURCE_PATH}")
        return 1

    source_body = SOURCE_PATH.read_text(encoding="utf-8")
    if not source_body.startswith("# 推荐系统核心模型复习笔记"):
        print(
            f"[ERROR] source body did not start with expected H1: "
            f"{source_body.splitlines()[0]!r}"
        )
        return 1

    content = build_content(source_body)
    validate_content(content)
    print(
        f"[OK] content validated: chars={len(content)} "
        f"bytes={len(content.encode('utf-8'))}"
    )

    conn = sqlite3.connect(str(DB_PATH))
    try:
        # 1. Verify Meta company.
        row = conn.execute(
            "SELECT name FROM companies WHERE id = ?", (COMPANY_ID,)
        ).fetchone()
        if row is None:
            print(f"[ERROR] company_id={COMPANY_ID} not found")
            return 1
        print(f"[OK] target company: id={COMPANY_ID} name={row[0]!r}")

        # 2. Defensive: verify all 3 sibling cd:// backlinks + 2 sd:// slugs.
        sibling_specs = [
            (FAMILY_DOC_ID, "Family Taxonomy"),
            (JIMU_DOC_ID, "Cross-cutting"),
            (MAIN_HUB_DOC_ID, "45min Playbook"),
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

        # 3. Upsert.
        existing = conn.execute(
            "SELECT id, content FROM company_documents "
            "WHERE company_id = ? AND title = ?",
            (COMPANY_ID, DOC_TITLE),
        ).fetchone()

        now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        new_hash = sha256_bytes(content)

        if existing is None:
            conn.execute(
                "INSERT INTO company_documents "
                "(company_id, title, content, source_type, doc_kind, "
                "is_golden, content_hash, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    COMPANY_ID,
                    DOC_TITLE,
                    content,
                    SOURCE_TYPE,
                    DOC_KIND,
                    IS_GOLDEN,
                    new_hash,
                    now,
                    now,
                ),
            )
            conn.commit()
            new_id = conn.execute(
                "SELECT id FROM company_documents "
                "WHERE company_id = ? AND title = ?",
                (COMPANY_ID, DOC_TITLE),
            ).fetchone()[0]
            print(
                f"[INSERT] id={new_id} chars={len(content)} "
                f"bytes={len(content.encode('utf-8'))} "
                f"hash={new_hash[:12]}..."
            )
            doc_id = new_id
        else:
            existing_id, existing_content = existing
            doc_id = existing_id
            if SENTINEL in existing_content and existing_content == content:
                print(
                    f"[UNCHANGED] id={existing_id} sentinel present + "
                    f"content byte-identical; 0 writes"
                )
            else:
                conn.execute(
                    "UPDATE company_documents "
                    "SET content = ?, content_hash = ?, updated_at = ? "
                    "WHERE id = ?",
                    (content, new_hash, now, existing_id),
                )
                conn.commit()
                old_len = len(existing_content)
                print(
                    f"[UPDATE] id={existing_id} old_len={old_len} "
                    f"new_len={len(content)} delta={len(content) - old_len:+d}"
                )

        # 4. AC #7 self-link exclusion: content must not reference its own id.
        self_uri = f"cd://{doc_id}"
        # Word-boundary protection: cd://9 must not match cd://97. Use
        # delimiter set.
        delims = {" ", "\n", ")", "]", "|", ">", "<", "\t"}
        hits = 0
        i = 0
        while True:
            j = content.find(self_uri, i)
            if j < 0:
                break
            after = content[j + len(self_uri) : j + len(self_uri) + 1]
            if after == "" or after in delims or not after.isdigit():
                hits += 1
            i = j + 1
        if hits != 0:
            print(
                f"[ERROR] self-link violation: content contains "
                f"'{self_uri}' {hits} times"
            )
            return 1
        print(f"[OK] self-link exclusion verified: '{self_uri}' absent")

        # 5. AC #1: post-INSERT title query returns exactly 1 row.
        cnt = conn.execute(
            "SELECT COUNT(*) FROM company_documents "
            "WHERE company_id = ? AND title = ?",
            (COMPANY_ID, DOC_TITLE),
        ).fetchone()[0]
        if cnt != 1:
            print(f"[ERROR] expected exactly 1 row, got {cnt}")
            return 1
        print(f"[OK] post-INSERT title query: {cnt} row")

        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
