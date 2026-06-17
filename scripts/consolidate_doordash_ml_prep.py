"""Consolidate DoorDash ML Domain prep docs 40-46 into one master document.

Idempotent: re-running updates the master doc in place (looked up by exact title).
Also rewrites originals 40-46 to include a redirect banner at the top pointing to
the master doc. Banner is idempotent — only inserted once.

Structure of master doc:
    # DoorDash ML Domain Prep -- Master
    ## Table of Contents
    - links to each of 7 source sections
    ## <source 1 short title>
    ### <source 1 H2 #1>
    #### <source 1 H3 #1>
    ...
    ## <source 2 short title>
    ...

Source H1 is stripped; source H2 is demoted to H3; source H3 is demoted to H4.
The new master-level H2 per source carries the short (post-colon) title.
"""
from __future__ import annotations

import os
import re
import sqlite3
from collections.abc import Iterable

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_DIR, "data", "mle_prep.db")

COMPANY_ID = 2  # DoorDash
SOURCE_IDS = [40, 41, 42, 43, 44, 45, 46]
MASTER_TITLE = "DoorDash ML Domain Prep \u2014 \u5408\u96c6 (Master)"
REDIRECT_MARK = "<!-- doordash-ml-prep-consolidated -->"


def slugify(text: str) -> str:
    """Mirror src/frontend/src/utils/slugify.ts behavior."""
    import re as _re
    s = text.lower().strip()
    s = _re.sub(r"\s+", "-", s)
    s = _re.sub(r"[^\w\u4e00-\u9fff\u3400-\u4dbf-]", "", s)
    s = _re.sub(r"-{2,}", "-", s)
    s = _re.sub(r"^-|-$", "", s)
    return s


def short_title(full_title: str) -> str:
    """Extract the post-colon part of a DoorDash prep doc title."""
    return full_title.split(":", 1)[-1].strip() if ":" in full_title else full_title


def demote_headings(content: str) -> str:
    """Drop the first H1; demote remaining H{n} to H{n+1} up to H5.

    Source docs have structure: `# <title>` then H2/H3/H4. We want source H2
    to become H3 in the master so source headings nest under the new H2 per
    source. The original H1 line is removed entirely (replaced by a synthetic
    master-level H2).
    """
    lines = content.splitlines()
    out: list[str] = []
    h1_dropped = False
    for line in lines:
        m = re.match(r"^(#{1,5})\s+(.+)$", line)
        if m:
            hashes, text = m.group(1), m.group(2)
            if not h1_dropped and len(hashes) == 1:
                h1_dropped = True
                continue  # skip the leading H1
            # Demote by 1 (cap at 6)
            new_level = min(len(hashes) + 1, 6)
            out.append("#" * new_level + " " + text)
        else:
            out.append(line)
    # Trim leading blank lines
    while out and not out[0].strip():
        out.pop(0)
    return "\n".join(out)


def build_master_content(sources: list[tuple[int, str, str]]) -> str:
    """Assemble the consolidated content.

    sources: list of (id, title, content) tuples in order.
    """
    parts: list[str] = []
    parts.append(f"# {MASTER_TITLE}")
    parts.append("")
    parts.append(
        "> \u672c\u6587\u6863\u5408\u5e76\u4e86 7 \u4efd DoorDash ML Domain Prep "
        "\u5b50\u6587\u6863\uff08id 40-46\uff09\uff0c\u7528\u4e8e\u7edf\u4e00\u6d4f"
        "\u89c8\u548c\u5feb\u901f\u5bfc\u822a\u3002\u5de6\u4fa7 TOC \u4fa7\u8fb9\u680f"
        "\u81ea\u52a8\u751f\u6210\uff0c\u70b9\u51fb\u5c0f\u8282\u540d\u5373\u53ef"
        "\u8df3\u8f6c\u3002"
    )
    parts.append("")
    parts.append("## \u76ee\u5f55 (Table of Contents)")
    parts.append("")
    for _doc_id, title, _ in sources:
        short = short_title(title)
        parts.append(f"- [{short}](#{slugify(short)})")
    parts.append("")
    parts.append("---")
    parts.append("")

    for doc_id, title, content in sources:
        short = short_title(title)
        parts.append(f"## {short}")
        parts.append("")
        parts.append(
            f"> \u6765\u6e90\uff1a\u539f\u6587\u6863 id={doc_id}\uff08\u5728\u5728\u4ed3"
            f"\u5e93\u4e2d\u4f5c\u4e3a\u72ec\u7acb\u6761\u76ee\u4fdd\u7559\uff09\u3002"
        )
        parts.append("")
        parts.append(demote_headings(content))
        parts.append("")
        parts.append("---")
        parts.append("")

    return "\n".join(parts).rstrip() + "\n"


def banner_text(master_id: int) -> str:
    return (
        f"{REDIRECT_MARK}\n"
        f"> \u6b64\u6587\u6863\u5df2\u5408\u5e76\u5165 "
        f"[DoorDash ML Domain Prep \u2014 \u5408\u96c6](/companies/{COMPANY_ID}/prep?doc={master_id})\u3002"
        f"\u672c\u9875\u4fdd\u7559\u7528\u4e8e\u5386\u53f2\u5bf9\u7167\u3002\n\n"
    )


def add_or_refresh_banner(content: str, master_id: int) -> str:
    """Ensure the redirect banner is the first content. Idempotent."""
    banner = banner_text(master_id)
    if REDIRECT_MARK in content:
        # Replace existing banner block (from marker to first blank line after it)
        lines = content.splitlines(keepends=True)
        start = next(i for i, ln in enumerate(lines) if REDIRECT_MARK in ln)
        # Banner spans start through the first blank line after the blockquote
        end = start + 1
        while end < len(lines) and lines[end].lstrip().startswith(">"):
            end += 1
        # skip the trailing blank line if present
        while end < len(lines) and lines[end].strip() == "":
            end += 1
            break
        return banner + "".join(lines[end:])
    return banner + content


def strip_banner(content: str) -> str:
    """Remove an existing redirect banner from content (for re-consolidation)."""
    if REDIRECT_MARK not in content:
        return content
    lines = content.splitlines(keepends=True)
    start = next(i for i, ln in enumerate(lines) if REDIRECT_MARK in ln)
    end = start + 1
    while end < len(lines) and lines[end].lstrip().startswith(">"):
        end += 1
    while end < len(lines) and lines[end].strip() == "":
        end += 1
        break
    return "".join(lines[:start] + lines[end:])


def fetch_sources(conn: sqlite3.Connection, ids: Iterable[int]) -> list[tuple[int, str, str]]:
    rows = []
    for doc_id in ids:
        row = conn.execute(
            "SELECT id, title, content FROM company_documents WHERE id = ?",
            (doc_id,),
        ).fetchone()
        if row is None:
            raise SystemExit(f"[FAIL] source doc id={doc_id} not found")
        # Remove any existing banner before consolidating
        rows.append((row[0], row[1], strip_banner(row[2])))
    return rows


def upsert_master(conn: sqlite3.Connection, content: str) -> int:
    row = conn.execute(
        "SELECT id FROM company_documents WHERE company_id = ? AND title = ?",
        (COMPANY_ID, MASTER_TITLE),
    ).fetchone()
    if row:
        master_id = row[0]
        conn.execute(
            "UPDATE company_documents SET content = ?, doc_kind = 'prep_note', "
            "updated_at = datetime('now') WHERE id = ?",
            (content, master_id),
        )
        print(f"[UPDATE] master doc id={master_id}")
    else:
        cur = conn.execute(
            "INSERT INTO company_documents (company_id, title, content, source_type, doc_kind) "
            "VALUES (?, ?, ?, 'prep_doc', 'prep_note')",
            (COMPANY_ID, MASTER_TITLE, content),
        )
        master_id = cur.lastrowid
        print(f"[INSERT] master doc id={master_id}")
    return master_id


def apply_redirect_banners(conn: sqlite3.Connection, master_id: int) -> None:
    for doc_id in SOURCE_IDS:
        row = conn.execute(
            "SELECT content FROM company_documents WHERE id = ?", (doc_id,)
        ).fetchone()
        new_content = add_or_refresh_banner(row[0], master_id)
        conn.execute(
            "UPDATE company_documents SET content = ?, updated_at = datetime('now') "
            "WHERE id = ?",
            (new_content, doc_id),
        )
    print(f"[BANNER] applied redirect to {len(SOURCE_IDS)} source docs -> master id={master_id}")


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        sources = fetch_sources(conn, SOURCE_IDS)
        master = build_master_content(sources)
        master_id = upsert_master(conn, master)
        apply_redirect_banners(conn, master_id)
        conn.commit()
        size = len(master)
        print(f"[DONE] master content size={size} chars, sources={len(sources)}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
