"""Seed Pinterest system-design markdown into DB.

Reads 7 `docs/company/pinterest/system_design_*.md` files and upserts them into
the `system_designs` table with slugs `pinterest-*`. Also seeds 3 non-SD
markdown files (bq_question_map, lc_investigation_restaurant_intervals,
uber_phone_screen_prep) as rows in `company_documents`.

Idempotent: re-running produces 0 net changes (upsert by slug / by title).

Usage:
    python scripts/seed_pinterest_sd.py [--db data/mle_prep.db] [--dry-run]
"""
from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS = REPO_ROOT / "docs"
DEFAULT_DB = REPO_ROOT / "data" / "mle_prep.db"

# (source_file_stem, slug, company_scope_subtitle)
SD_FILES: list[tuple[str, str]] = [
    ("system_design_concepts", "pinterest-system-design-concepts"),
    ("system_design_ad_ctr", "pinterest-ad-ctr"),
    ("system_design_embeddings", "pinterest-embeddings"),
    ("system_design_chatbot_pins", "pinterest-chatbot-pins"),
    ("system_design_pin_ranking", "pinterest-pin-ranking"),
    ("system_design_pins_search", "pinterest-pins-search"),
    ("system_design_notification_reco", "pinterest-notification-reco"),
    ("system_design_catalog_bulk_update", "pinterest-catalog-bulk-update"),
]

# (source_path_relative_to_docs, company_id, title)
DOC_FILES: list[tuple[str, int, str]] = [
    ("pinterest/bq_question_map.md", 29, "Pinterest BQ Question Map"),
    (
        "pinterest/lc_investigation_restaurant_intervals.md",
        29,
        "Pinterest LC Investigation: Restaurant Intervals",
    ),
    ("uber_phone_screen_prep.md", 5, "Uber Phone Screen Prep"),
]

PINTEREST_SUBTITLE = "Pinterest ML System Design"

# Keywords for bucketing remaining sections into columns.
TRADEOFF_KEYS = ("tradeoff", "follow-up", "follow up", "trade-off")
DEFENSE_KEYS = ("failure", "cold start", "mitigation", "cold-start")
VERBAL_KEYS = ("timing", "cheat sheet", "45-min", "45 min", "时间分配")


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def split_sections(md: str) -> tuple[str, list[tuple[str, str]]]:
    """Return (h1_title, list of (heading_line, body)) for top-level `## ` sections."""
    lines = md.splitlines()
    h1 = ""
    for line in lines:
        if line.startswith("# "):
            h1 = line[2:].strip()
            break

    # Split by `^## ` (exclude `###`).
    parts = re.split(r"(?m)^(## [^\n]+)$", md)
    # parts[0] = preamble. Then alternating heading, body.
    sections: list[tuple[str, str]] = []
    for i in range(1, len(parts), 2):
        head = parts[i].strip()
        body = parts[i + 1] if i + 1 < len(parts) else ""
        sections.append((head, body.strip()))
    return h1, sections


def _section_matches(head: str, keys: tuple[str, ...]) -> bool:
    h = head.lower()
    return any(k in h for k in keys)


def map_to_columns(md: str) -> dict[str, str | None]:
    """Heuristically split sections into system_designs columns.

    Numbered sections 0..7 → overview/architecture/dataflow/formulas/production_constraints.
    Keyword-matched sections (Tradeoffs, Failure Modes, Timing) → tradeoffs/defense/verbal_outline.
    """
    h1, sections = split_sections(md)

    cols: dict[str, list[str]] = {
        "overview": [],
        "architecture": [],
        "dataflow": [],
        "formulas": [],
        "production_constraints": [],
        "tradeoffs": [],
        "defense": [],
        "verbal_outline": [],
    }

    # Prepend H1 to overview.
    if h1:
        cols["overview"].append(f"# {h1}\n")

    for head, body in sections:
        full = f"{head}\n\n{body}".strip()
        if _section_matches(head, TRADEOFF_KEYS):
            cols["tradeoffs"].append(full)
            continue
        if _section_matches(head, DEFENSE_KEYS):
            cols["defense"].append(full)
            continue
        if _section_matches(head, VERBAL_KEYS):
            cols["verbal_outline"].append(full)
            continue

        # Numbered section: extract leading integer.
        m = re.match(r"##\s*(\d+)\.", head)
        if m:
            n = int(m.group(1))
            if n == 0:
                cols["overview"].append(full)
            elif n == 1:
                cols["architecture"].append(full)
            elif n in (2, 3):
                cols["dataflow"].append(full)
            elif n in (4, 5):
                cols["formulas"].append(full)
            elif n in (6, 7):
                cols["production_constraints"].append(full)
            else:
                # Higher-numbered sections default to production_constraints
                # unless they already match a keyword bucket above.
                cols["production_constraints"].append(full)
        else:
            cols["production_constraints"].append(full)

    return {k: ("\n\n".join(v).strip() or None) for k, v in cols.items()}


def upsert_sd(cur: sqlite3.Cursor, slug: str, title: str, fields: dict[str, str | None],
              display_order: int, dry: bool) -> str:
    cur.execute("SELECT id FROM system_designs WHERE slug = ?", (slug,))
    existing = cur.fetchone()
    now = _now()
    payload = {
        "slug": slug,
        "title": title,
        "subtitle": PINTEREST_SUBTITLE,
        "diagram_filename": None,
        **fields,
        "display_order": display_order,
        "updated_at": now,
    }
    if existing:
        if dry:
            return f"UPDATE id={existing[0]} slug={slug}"
        cols = ", ".join(f"{k} = :{k}" for k in payload)
        cur.execute(f"UPDATE system_designs SET {cols} WHERE slug = :slug", payload)
        return f"updated id={existing[0]} slug={slug}"
    payload["created_at"] = now
    cols = ", ".join(payload.keys())
    placeholders = ", ".join(f":{k}" for k in payload)
    if dry:
        return f"INSERT slug={slug}"
    cur.execute(
        f"INSERT INTO system_designs ({cols}) VALUES ({placeholders})", payload
    )
    return f"inserted id={cur.lastrowid} slug={slug}"


def upsert_doc(cur: sqlite3.Cursor, company_id: int, title: str, content: str,
               dry: bool) -> str:
    cur.execute(
        "SELECT id FROM company_documents WHERE company_id = ? AND title = ?",
        (company_id, title),
    )
    existing = cur.fetchone()
    now = _now()
    if existing:
        if dry:
            return f"UPDATE doc id={existing[0]} title={title!r}"
        cur.execute(
            "UPDATE company_documents SET content = ?, updated_at = ? WHERE id = ?",
            (content, now, existing[0]),
        )
        return f"updated doc id={existing[0]} title={title!r}"
    if dry:
        return f"INSERT doc company_id={company_id} title={title!r}"
    cur.execute(
        "INSERT INTO company_documents "
        "(company_id, title, content, source_type, created_at, updated_at) "
        "VALUES (?, ?, ?, 'markdown', ?, ?)",
        (company_id, title, content, now, now),
    )
    return f"inserted doc id={cur.lastrowid} title={title!r}"


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

    actions: list[str] = []

    # Seed system_designs.
    for i, (stem, slug) in enumerate(SD_FILES):
        src = DOCS / "company" / "pinterest" / f"{stem}.md"
        if not src.exists():
            print(f"WARN: missing {src}", file=sys.stderr)
            continue
        md = src.read_text(encoding="utf-8")
        h1, _ = split_sections(md)
        title = h1 or stem.replace("_", " ").title()
        fields = map_to_columns(md)
        # display_order 199..206: SD_FILES[0]=concept doc -> 199, then ad-ctr..catalog
        # land at 200..206 (matches existing DB state and the >= 199 frontend filter).
        display_order = 199 + i
        actions.append(upsert_sd(cur, slug, title, fields, display_order, args.dry_run))

    # Seed company_documents for the 3 non-SD files.
    for rel, cid, title in DOC_FILES:
        src = DOCS / rel
        if not src.exists():
            print(f"WARN: missing {src}", file=sys.stderr)
            continue
        content = src.read_text(encoding="utf-8")
        actions.append(upsert_doc(cur, cid, title, content, args.dry_run))

    if args.dry_run:
        con.rollback()
    else:
        con.commit()
    con.close()

    for a in actions:
        print(a)
    print(f"\n{'DRY-RUN' if args.dry_run else 'DONE'}: {len(actions)} action(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
