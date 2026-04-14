"""Sync filesystem markdown files into DB content columns (docs -> DB).

Authoring workflow: markdown files in ``MLInterviewPrep/docs/**/*.md`` are the
editable authoring surface.  The DB (``company_documents`` / ``system_designs``)
is the runtime read path.  This script upserts DB content when the md content
hash differs from the stored ``content_hash`` column.

Target resolution uses YAML frontmatter:

    ---
    target_table: company_documents   # or system_designs
    target_id: 19                      # row primary key (mutually exclusive with slug)
    target_slug: youtube-rec           # for system_designs
    target_column: content             # default: content (company_documents) / overview (system_designs)
    ---
    <markdown body>

If the md body hash matches the DB ``content_hash``, the row is skipped (idempotent).
Use ``--dry-run`` to preview planned writes without committing.

Usage:
    python scripts/sync_docs_to_db.py               # apply all
    python scripts/sync_docs_to_db.py --dry-run     # preview only
    python scripts/sync_docs_to_db.py --file X.md   # single file
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import text  # noqa: E402

from src.backend.database import get_engine, init_db  # noqa: E402

DOCS_ROOT = PROJECT_ROOT / "docs"
FRONTMATTER_DELIM = "---"

TABLE_DEFAULT_COLUMN = {
    "company_documents": "content",
    "system_designs": "overview",
}
ALLOWED_COLUMNS = {
    "company_documents": {"content"},
    "system_designs": {
        "overview", "architecture", "dataflow", "formulas",
        "production_constraints", "tradeoffs", "defense", "verbal_outline",
    },
}


@dataclass
class SyncPlan:
    """One planned upsert decided by the sync pass."""

    path: Path
    table: str
    row_key: tuple[str, object] | None  # ("id", 19) or ("slug", "youtube-rec"); None = create
    column: str
    new_hash: str
    old_hash: str | None
    body: str
    create_meta: dict[str, object] | None = None  # fields for INSERT when row_key is None

    @property
    def action(self) -> str:
        """Return action label for logging: insert/update/skip."""
        if self.row_key is None:
            return "create"
        if self.old_hash is None:
            return "insert"
        if self.old_hash == self.new_hash:
            return "skip"
        return "update"


def parse_frontmatter(raw: str) -> tuple[dict[str, str], str]:
    """Split frontmatter (YAML subset) from body. Supports only ``key: value`` lines.

    Args:
        raw: full file content.

    Returns:
        (metadata dict, body string). Empty dict if no frontmatter.
    """
    if not raw.startswith(FRONTMATTER_DELIM):
        return {}, raw
    lines = raw.split("\n")
    end = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == FRONTMATTER_DELIM:
            end = i
            break
    if end < 0:
        return {}, raw
    meta: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip().strip('"').strip("'")
    body = "\n".join(lines[end + 1:]).lstrip("\n")
    return meta, body


def sha256(s: str) -> str:
    """Return sha256 hex of a string (utf-8)."""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def discover_files(single: Path | None) -> list[Path]:
    """Return markdown files to consider (with frontmatter only)."""
    if single:
        return [single]
    return sorted(p for p in DOCS_ROOT.rglob("*.md") if p.is_file())


def build_plans(files: list[Path]) -> list[SyncPlan]:
    """Scan files, parse frontmatter, and assemble sync plans."""
    plans: list[SyncPlan] = []
    engine = get_engine()
    with engine.connect() as conn:
        for path in files:
            raw = path.read_text(encoding="utf-8")
            meta, body = parse_frontmatter(raw)
            table = meta.get("target_table")
            if table not in TABLE_DEFAULT_COLUMN:
                continue
            column = meta.get("target_column") or TABLE_DEFAULT_COLUMN[table]
            if column not in ALLOWED_COLUMNS[table]:
                print(f"[WARN] {path}: column {column!r} not allowed for {table}; skipping")
                continue
            if "target_id" in meta:
                row_key: tuple[str, object] | None = ("id", int(meta["target_id"]))
            elif "target_slug" in meta and table == "system_designs":
                row_key = ("slug", meta["target_slug"])
            elif table == "company_documents" and meta.get("company_id") and meta.get("title"):
                # Create-new-row path: no target_id yet. Will INSERT and rewrite frontmatter.
                plans.append(SyncPlan(
                    path=path,
                    table=table,
                    row_key=None,
                    column=column,
                    new_hash=sha256(body),
                    old_hash=None,
                    body=body,
                    create_meta={
                        "company_id": int(meta["company_id"]),
                        "title": meta["title"],
                        "doc_kind": meta.get("doc_kind", "prep_note"),
                    },
                ))
                continue
            else:
                print(f"[WARN] {path}: no target_id/target_slug; skipping")
                continue
            col_name, col_val = row_key
            stored = conn.execute(
                text(f"SELECT content_hash FROM {table} WHERE {col_name} = :v"),
                {"v": col_val},
            ).fetchone()
            if stored is None:
                print(f"[WARN] {path}: no {table} row with {col_name}={col_val}; skipping")
                continue
            plans.append(SyncPlan(
                path=path,
                table=table,
                row_key=row_key,
                column=column,
                new_hash=sha256(body),
                old_hash=stored[0],
                body=body,
            ))
    return plans


def _rewrite_frontmatter_target_id(path: Path, new_id: int) -> None:
    """Inject ``target_id: <new_id>`` into an existing YAML frontmatter block.

    The sync create-path calls this after a successful INSERT so subsequent
    runs resolve via target_id and are idempotent.
    """
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith(FRONTMATTER_DELIM):
        return
    lines = raw.split("\n")
    end = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == FRONTMATTER_DELIM:
            end = i
            break
    if end < 0:
        return
    # Replace existing target_id if present, else insert before closing ---.
    injected = False
    for i in range(1, end):
        if lines[i].split(":", 1)[0].strip() == "target_id":
            lines[i] = f"target_id: {new_id}"
            injected = True
            break
    if not injected:
        lines.insert(end, f"target_id: {new_id}")
    path.write_text("\n".join(lines), encoding="utf-8")


def apply_plans(plans: list[SyncPlan], dry_run: bool) -> tuple[int, int, int]:
    """Apply update/insert/create plans. Returns (updated, skipped, errors)."""
    updated = skipped = errors = 0
    engine = get_engine()
    with engine.begin() as conn:
        for p in plans:
            if p.action == "skip":
                skipped += 1
                continue
            src = str(p.path.relative_to(PROJECT_ROOT)).replace("\\", "/")
            if p.action == "create":
                assert p.create_meta is not None
                meta = p.create_meta
                if dry_run:
                    print(f"[DRY CREATE] {p.path} -> {p.table} "
                          f"(company_id={meta['company_id']}, title={meta['title']!r})")
                    updated += 1
                    continue
                try:
                    result = conn.execute(text(
                        f"INSERT INTO {p.table} "
                        "(company_id, title, content, source_type, doc_kind, "
                        "content_hash, source_path) "
                        "VALUES (:cid, :title, :body, 'manual', :kind, :h, :src)"
                    ), {
                        "cid": meta["company_id"], "title": meta["title"],
                        "body": p.body, "kind": meta["doc_kind"],
                        "h": p.new_hash, "src": src,
                    })
                    new_id = result.lastrowid
                    _rewrite_frontmatter_target_id(p.path, int(new_id))
                    print(f"[CREATE] {p.path} -> {p.table} id={new_id}")
                    updated += 1
                except Exception as exc:  # pragma: no cover
                    print(f"[ERROR] {p.path}: {exc}")
                    errors += 1
                continue
            col_name, col_val = p.row_key  # type: ignore[misc]
            sql = (
                f"UPDATE {p.table} SET {p.column} = :body, content_hash = :h, "
                f"source_path = :src WHERE {col_name} = :v"
            )
            if dry_run:
                print(f"[DRY {p.action.upper()}] {p.path} -> {p.table}.{p.column} "
                      f"where {col_name}={col_val} (hash {p.old_hash!s:.8}..-> {p.new_hash[:8]}..)")
                updated += 1
                continue
            try:
                conn.execute(text(sql), {
                    "body": p.body, "h": p.new_hash,
                    "src": src,
                    "v": col_val,
                })
                print(f"[{p.action.upper()}] {p.path} -> {p.table}.{p.column}")
                updated += 1
            except Exception as exc:  # pragma: no cover
                print(f"[ERROR] {p.path}: {exc}")
                errors += 1
    return updated, skipped, errors


def backfill_hashes(dry_run: bool) -> int:
    """Populate content_hash for rows with NULL hash, using current DB content."""
    engine = get_engine()
    filled = 0
    with engine.begin() as conn:
        for table, col in TABLE_DEFAULT_COLUMN.items():
            # Use the canonical default content column for hash backfill.
            rows = conn.execute(text(
                f"SELECT rowid, {col} FROM {table} WHERE content_hash IS NULL"
            )).fetchall()
            for rowid, content in rows:
                h = sha256(content or "")
                if dry_run:
                    print(f"[DRY BACKFILL] {table} rowid={rowid} -> {h[:8]}..")
                else:
                    conn.execute(text(
                        f"UPDATE {table} SET content_hash = :h WHERE rowid = :r"
                    ), {"h": h, "r": rowid})
                filled += 1
    return filled


def main() -> int:
    """CLI entry point."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="preview only")
    ap.add_argument("--file", type=Path, help="single md file to sync")
    ap.add_argument("--backfill-hashes", action="store_true",
                    help="populate content_hash for DB rows that have NULL")
    args = ap.parse_args()

    init_db(get_engine())

    if args.backfill_hashes:
        n = backfill_hashes(args.dry_run)
        print(f"[BACKFILL] {n} rows")

    files = discover_files(args.file)
    plans = build_plans(files)
    updated, skipped, errors = apply_plans(plans, args.dry_run)
    print(f"\n[SUMMARY] updated/insert={updated} skipped={skipped} errors={errors} "
          f"(dry_run={args.dry_run})")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
