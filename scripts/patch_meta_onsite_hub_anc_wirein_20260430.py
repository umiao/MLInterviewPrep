"""[META-ANC-10] Wire AI-Native Coding Inventory hub into cd://82 (golden).

Edits company_documents id=82 ('[Meta] AI-Native Onsite Prep (2026-05-01)')
to add a new section (Section T5) referencing the AI-Native Coding Inventory
& Cheat Sheet drawer (cd://<new_hub_id>) so the day-of reading flow surfaces
the inventory.

This is the HIGHEST-RISK edit in the META-ANC track because it mutates the
golden hub the user reads day-of. The script enforces:

1. MANDATORY backup BEFORE any modification (FIX #4 priority-1):
   `data/backups/cd_82_anc_wirein_<UTC-ISO>.md`. Backup write failure aborts.
2. Two-phase sentinel-anchor approach (FIX #4 -- replaces fragile string-grep):
   - Phase 1 (anchor install): if `<!-- ANC_WIREIN_AFTER -->` not present,
     insert it on the line AFTER the line containing `(cd://89)`.
   - Phase 2 (content insert/replace): split on
     `<!-- ANC_WIREIN BEGIN --> ... <!-- ANC_WIREIN END -->`. If markers
     exist, replace inner content. Else append after the anchor.
3. Schedule edit also two-phase, sentinel-bracketed:
   - Phase A (sched anchor wrap): wrap existing AI-Native Coding rowspan
     cell inner HTML with `<!-- ANC_SCHED BEGIN --> ... <!-- ANC_SCHED END -->`
     if not present.
   - Phase B (sched content): replace inner content with the cd://90 link
     appended.
4. Idempotency key (FIX #5): semantic NOOP via `_normalize` (strip per-line
   trailing whitespace, force LF, collapse 3+ blank lines to 2). Run-twice
   second invocation must show ALL phases NOOP.
5. COMPANY_ID self-check (FIX #7): query Meta by name, assert == 31. Plus
   id=82 doc title LIKE '%AI-Native Onsite Prep%'.
6. New hub discovery: SELECT id FROM company_documents WHERE company_id=31
   AND content LIKE '%META_AI_NATIVE_CODING_INVENTORY_20260501%'. Expect
   exactly 1.
7. Required-keywords assertion (FIX #8): post-update, cd://82 contains
   ['§T5', f'cd://{new_hub_id}', 'AI-Native Coding Problem Inventory',
    '<!-- ANC_WIREIN BEGIN -->', '<!-- ANC_WIREIN END -->'].
8. CLI flag: `--dry-run` (default off). Dry-run does backup + Phase 1 + 2
   in-memory and prints a diff; does NOT write to DB.

Reference golden examples:
- Hub-doc UPSERT pattern: scripts/content_meta_anc_inventory_hub.py.
- Sentinel-bracket UPSERT semantics: project convention.
"""
from __future__ import annotations

import argparse
import difflib
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.company import Company, CompanyDocument  # noqa: E402

TARGET_DOC_ID = 82
TARGET_TITLE_LIKE = "%AI-Native Onsite Prep%"
NEW_HUB_SENTINEL = "META_AI_NATIVE_CODING_INVENTORY_20260501"

ANCHOR = "<!-- ANC_WIREIN_AFTER -->"
WIREIN_BEGIN = "<!-- ANC_WIREIN BEGIN -->"
WIREIN_END = "<!-- ANC_WIREIN END -->"
SCHED_BEGIN = "<!-- ANC_SCHED BEGIN -->"
SCHED_END = "<!-- ANC_SCHED END -->"

CD89_PATTERN = re.compile(r"\(cd://89\)")
SCHED_TD_PATTERN = re.compile(
    r'(<td rowspan="2">)(.*?)(</td>)',
    re.DOTALL,
)


def _wirein_block(new_hub_id: int) -> str:
    """Return the §T5 block to insert between WIREIN_BEGIN/END markers.

    Must NOT contain datetime.now() or any other non-deterministic content.
    """
    return (
        "\n"
        "## §T5 AI-Native Coding Problem Inventory & Cheat Sheet\n"
        "\n"
        "11:00 / 13:00 两场 coding round 之前 5 分钟扫一遍: 8 题速查表 "
        "(Maze / Max Unique / Friend Recommendation / Sparse Matrix /\n"
        "Linear Regression / Compiler / Find Words / Card Game) + 跨题共通考点 "
        "+ 临场 prompt 4 模板 (CLARIFY / VERIFY /\n"
        "IMPLEMENT / REVIEW) + AI 协作分工对照表 + 离场 60s checklist + "
        "AI 失分 3-tombstone (Card Game / Compiler / Friend Rec).\n"
        "\n"
        f"[**[打开 §T5 AI-Native Coding Inventory → drawer]**](cd://{new_hub_id})\n"
    )


def _sched_inner(new_hub_id: int) -> str:
    """Inner HTML for the schedule rowspan cell, between SCHED_BEGIN/END."""
    return (
        '<a href="cd://86">§T1 Code-Pad LLM Prompt + 3-Step Playbook</a> '
        '· <a href="cd://89">§T4-bp 临场 Prompt 写作 Best Practices</a> '
        f'· <a href="cd://{new_hub_id}">§T5 AI-Native Coding Inventory</a>'
    )


def _normalize(text: str) -> str:
    """Semantic normalization for NOOP comparison.

    Strip per-line trailing whitespace, force LF line endings, collapse
    3+ blank lines to 2.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [ln.rstrip() for ln in text.split("\n")]
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def _resolve_company_id(db) -> int:
    company_id = (
        db.query(Company).filter(Company.name == "Meta").one().id
    )
    if company_id != 31:
        raise RuntimeError(
            f"[META-ANC-10] expected Meta company_id=31, got {company_id}"
        )
    return int(company_id)


def _resolve_new_hub_id(db, company_id: int) -> int:
    rows = (
        db.query(CompanyDocument.id, CompanyDocument.title)
        .filter(
            CompanyDocument.company_id == company_id,
            CompanyDocument.content.like(f"%{NEW_HUB_SENTINEL}%"),
        )
        .all()
    )
    if len(rows) != 1:
        raise RuntimeError(
            f"[META-ANC-10] expected exactly 1 hub matching sentinel "
            f"{NEW_HUB_SENTINEL!r}, got {len(rows)}: "
            f"{[(r.id, r.title) for r in rows]}"
        )
    return int(rows[0].id)


def _load_target(db) -> CompanyDocument:
    doc = (
        db.query(CompanyDocument)
        .filter(CompanyDocument.id == TARGET_DOC_ID)
        .first()
    )
    if doc is None:
        raise RuntimeError(
            f"[META-ANC-10] target company_documents id={TARGET_DOC_ID} not found"
        )
    if "AI-Native Onsite Prep" not in (doc.title or ""):
        raise RuntimeError(
            f"[META-ANC-10] cd://{TARGET_DOC_ID} title sanity check failed: "
            f"{doc.title!r} does not contain 'AI-Native Onsite Prep'"
        )
    return doc


def _backup(content: str) -> Path:
    """Write current cd://82 content to a timestamped backup file. Abort on failure."""
    ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    backup_dir = Path(__file__).resolve().parent.parent / "data" / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"cd_82_anc_wirein_{ts}.md"
    try:
        backup_path.write_text(content, encoding="utf-8")
    except OSError as e:
        raise RuntimeError(
            f"[META-ANC-10] backup write failed at {backup_path}: {e}"
        ) from e
    print(f"[BACKUP] wrote cd://82 snapshot ({len(content)} chars) -> {backup_path}")
    return backup_path


def _phase1_install_anchor(content: str) -> tuple[str, str]:
    """Insert ANCHOR on the line after the line containing `(cd://89)`.

    Idempotent: if ANCHOR already present, no-op. Returns (new_content, status).
    Aborts if `(cd://89)` not found (means cd://82 structure changed).
    """
    if ANCHOR in content:
        return content, "NOOP"
    lines = content.split("\n")
    insert_at = None
    for i, ln in enumerate(lines):
        if CD89_PATTERN.search(ln):
            insert_at = i + 1
            break
    if insert_at is None:
        raise RuntimeError(
            "[META-ANC-10] Phase 1 abort: `(cd://89)` not found in cd://82 -- "
            "structure changed; refuse to wire blindly"
        )
    lines.insert(insert_at, ANCHOR)
    return "\n".join(lines), "INSERT"


def _phase2_wirein_content(content: str, new_hub_id: int) -> tuple[str, str]:
    """Insert or replace the §T5 block bracketed by WIREIN_BEGIN/END.

    If both markers exist (paired), replace inner content. Otherwise append a
    fresh bracketed block immediately after ANCHOR. Idempotent at semantic
    level via _normalize() comparison upstream.
    """
    block = _wirein_block(new_hub_id)
    bracketed = f"{WIREIN_BEGIN}{block}{WIREIN_END}\n"

    if WIREIN_BEGIN in content and WIREIN_END in content:
        pattern = re.compile(
            re.escape(WIREIN_BEGIN) + r".*?" + re.escape(WIREIN_END),
            re.DOTALL,
        )
        new_content, n = pattern.subn(
            f"{WIREIN_BEGIN}{block}{WIREIN_END}", content, count=1
        )
        if n != 1:
            raise RuntimeError(
                "[META-ANC-10] Phase 2 abort: WIREIN markers present but "
                "regex replace count != 1"
            )
        return new_content, "REPLACE"

    if ANCHOR not in content:
        raise RuntimeError(
            "[META-ANC-10] Phase 2 abort: ANCHOR missing -- run Phase 1 first"
        )
    new_content = content.replace(ANCHOR, f"{ANCHOR}\n\n{bracketed}", 1)
    return new_content, "INSERT"


def _phase_a_wrap_sched_cell(content: str) -> tuple[str, str]:
    """Wrap the AI-Native Coding rowspan="2" cell inner HTML with SCHED markers.

    Idempotent: if SCHED_BEGIN already inside the rowspan cell, no-op.
    """
    m = SCHED_TD_PATTERN.search(content)
    if m is None:
        raise RuntimeError(
            "[META-ANC-10] Phase A abort: <td rowspan=\"2\">...</td> not found "
            "in schedule table"
        )
    inner = m.group(2)
    if SCHED_BEGIN in inner and SCHED_END in inner:
        return content, "NOOP"
    new_inner = f"{SCHED_BEGIN}{inner}{SCHED_END}"
    new_td = f'{m.group(1)}{new_inner}{m.group(3)}'
    new_content = content[: m.start()] + new_td + content[m.end():]
    return new_content, "INSERT"


def _phase_b_sched_content(content: str, new_hub_id: int) -> tuple[str, str]:
    """Replace the content between SCHED_BEGIN/END inside the rowspan cell.

    Sets it to the canonical 3-link inner HTML including cd://<new_hub_id>.
    """
    inner_target = _sched_inner(new_hub_id)
    pattern = re.compile(
        re.escape(SCHED_BEGIN) + r".*?" + re.escape(SCHED_END),
        re.DOTALL,
    )
    if pattern.search(content) is None:
        raise RuntimeError(
            "[META-ANC-10] Phase B abort: SCHED markers missing -- run Phase A first"
        )
    new_content, n = pattern.subn(
        f"{SCHED_BEGIN}{inner_target}{SCHED_END}", content, count=1
    )
    if n != 1:
        raise RuntimeError(
            "[META-ANC-10] Phase B abort: SCHED regex replace count != 1"
        )
    return new_content, "REPLACE"


def _assert_required_keywords(content: str, new_hub_id: int) -> None:
    required = [
        "§T5",
        f"cd://{new_hub_id}",
        "AI-Native Coding Problem Inventory",
        WIREIN_BEGIN,
        WIREIN_END,
        SCHED_BEGIN,
        SCHED_END,
    ]
    for kw in required:
        if kw not in content:
            raise RuntimeError(
                f"[META-ANC-10] post-update keyword missing: {kw!r}"
            )


def _print_diff(old: str, new: str) -> None:
    diff = difflib.unified_diff(
        old.splitlines(keepends=True),
        new.splitlines(keepends=True),
        fromfile="cd_82_before",
        tofile="cd_82_after",
        n=3,
    )
    body = "".join(diff)
    if not body:
        print("[DIFF] (empty -- semantic NOOP)")
    else:
        print("[DIFF]")
        sys.stdout.write(body)
        if not body.endswith("\n"):
            sys.stdout.write("\n")


def patch_cd82(dry_run: bool = False) -> int:
    """Apply the wire-in transform; return cd://82 final content length."""
    init_db()
    db = SessionLocal()
    try:
        company_id = _resolve_company_id(db)
        print(f"[OK] Meta company id={company_id}")

        new_hub_id = _resolve_new_hub_id(db, company_id)
        print(f"[OK] new AI-Native Coding inventory hub id={new_hub_id}")

        doc = _load_target(db)
        print(
            f"[OK] target cd://{TARGET_DOC_ID} title={doc.title!r} "
            f"len={len(doc.content or '')}"
        )

        original = doc.content or ""
        _backup(original)

        content = original
        content, p1 = _phase1_install_anchor(content)
        print(f"[PHASE 1 anchor    ] {p1}")

        content, p2 = _phase2_wirein_content(content, new_hub_id)
        print(f"[PHASE 2 wirein    ] {p2}")

        content, pa = _phase_a_wrap_sched_cell(content)
        print(f"[PHASE A sched-wrap] {pa}")

        content, pb = _phase_b_sched_content(content, new_hub_id)
        print(f"[PHASE B sched-fill] {pb}")

        _assert_required_keywords(content, new_hub_id)
        print("[OK] required keywords present")

        if _normalize(original) == _normalize(content):
            print("[NOOP] cd://82 semantically identical to original; no DB write")
            if dry_run:
                _print_diff(original, content)
            return len(original)

        if dry_run:
            print("[DRY-RUN] DB write skipped; printing diff")
            _print_diff(original, content)
            return len(content)

        old_len = len(original)
        doc.content = content
        db.commit()

        final = (
            db.query(CompanyDocument)
            .filter(CompanyDocument.id == TARGET_DOC_ID)
            .one()
        )
        print(
            f"[UPDATED] cd://{TARGET_DOC_ID} old_len={old_len} "
            f"new_len={len(final.content or '')} "
            f"delta={len(final.content or '') - old_len:+d}"
        )
        _assert_required_keywords(final.content or "", new_hub_id)
        print("[VERIFY] post-commit keywords still present")
        return len(final.content or "")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="[META-ANC-10] Wire AI-Native Coding hub into cd://82"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Backup + transform in-memory; print diff; do NOT write DB",
    )
    args = parser.parse_args()
    patch_cd82(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
