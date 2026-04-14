# docs/ → DB Sync Convention (T-P1-213)

## TL;DR

- **Authoring source**: markdown files under `MLInterviewPrep/docs/**/*.md` (Git-tracked).
- **Runtime read path**: DB tables `company_documents`, `system_designs` (and later `knowledge_cards`, `framework_nodes.description`).
- **Sync script**: `scripts/sync_docs_to_db.py` — one-way `docs → DB`, idempotent.
- **Reverse script**: `scripts/dump_db_to_docs.py` — DR/backup into `docs/generated/` (gitignored).
- **Never hand-edit DB content columns directly.** Edit the md, then sync.

## Why this pattern

The UI reads content from the DB (with WAL SQLite), but markdown is the ergonomic
authoring surface (diff-friendly, grep-friendly, works in any editor, reviewable in PRs).
A content-hash-gated sync bridges the two without continuous duplication:

- The md file stores the *intent*.
- The DB row stores the *runtime payload* plus a `content_hash` = sha256(body).
- Re-running sync is a no-op when hashes match. Edits flip the hash → row updates.

Modeled loosely on Notion/Confluence "source import" flows, but git-native.

## Frontmatter contract

Each authoring md file must begin with a YAML frontmatter block:

```markdown
---
target_table: system_designs        # or company_documents
target_slug: interview-url-shortener  # for system_designs (or target_id: N)
target_column: overview              # optional; defaults are 'content' / 'overview'
---

<markdown body — this is what gets hashed and written to the DB column>
```

Rules:
- `target_table` ∈ `{company_documents, system_designs}`.
- For `company_documents` use `target_id: N` (integer primary key).
- For `system_designs` use `target_slug: <slug>` (preferred) or `target_id`.
- `target_column` must be in the column allowlist in `sync_docs_to_db.py`
  (content for company_documents; overview/architecture/dataflow/formulas/
  production_constraints/tradeoffs/defense/verbal_outline for system_designs).
- The **body** after the closing `---` is the hashed payload. Frontmatter is NOT part of the hash.

## Workflow

1. Edit `docs/**/*.md` (add frontmatter the first time).
2. `python scripts/sync_docs_to_db.py --dry-run` → preview what would change.
3. `python scripts/sync_docs_to_db.py` → apply.
4. Commit the md change (the DB update is runtime state; the md is the spec).

Rows untouched by any md file keep their DB content unchanged — sync never
deletes. To retire a doc, remove the DB row via an explicit script, not by
deleting the md.

## Backfill + bootstrap

- Existing DB rows had `content_hash = NULL`. Run
  `python scripts/sync_docs_to_db.py --backfill-hashes` once to populate
  sha256 of current DB content. After that, sync becomes hash-gated.
- To start authoring an existing DB row in md, run `dump_db_to_docs.py`,
  copy the generated file from `docs/generated/` into an authoring location
  (e.g. `docs/synced/`), and commit it.

## Archive

`archive/` holds stable content that is no longer in active `docs/` but worth
keeping for audit (e.g. retrofit sql dumps, deprecated seeds). Archived files
are not scanned by the sync script.

## Related: T-P0-199 placeholder links

Once md files are round-trippable via sync, broken `.md`-file links in
company_documents can be rewritten programmatically to `db://` / `lc://`
drawer routes by a follow-up migration pass (unblocks T-P0-199).

## Files

- `scripts/sync_docs_to_db.py` — docs → DB upsert (idempotent, hash-gated).
- `scripts/dump_db_to_docs.py` — DB → `docs/generated/` dump (DR only).
- `src/backend/database.py` migration 18 — adds `content_hash` + `source_path`
  columns to `company_documents` and `system_designs`.
- `docs/synced/` — curated authoring md files with frontmatter (dogfood).
- `docs/generated/` — gitignored DR output of `dump_db_to_docs.py`.
