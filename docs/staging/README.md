# docs/staging/

**Status**: Migrated from top-level `docs/` on 2026-04-16 via T-P1-482 (DOCS-03).
**Authority**: [docs/protocol/docs_filing_convention.md](../protocol/docs_filing_convention.md) §2.5, §4.

## Purpose

Holding pen for transient content:

- `generated/` -- build output from `scripts/dump_db_to_docs.py` (gitignored; DR/backup copy of DB rows).
- `audits/` -- dated point-in-time audit artifacts (link spot-checks, coverage checklists, approval mirrors).
- `synced/` -- md files round-tripped through `scripts/sync_docs_to_db.py` as authoring dogfood.
- `analysis/` -- exploratory single-shot audits that drove consolidation decisions.

Nothing in `staging/` is meant to be long-lived reference material. Long-lived
content belongs in `docs/study/`, `docs/company/<slug>/`, `docs/design/`, or
`docs/protocol/` per the filing convention.

## TTL policy (30-day soft TTL)

Files here expire **30 days** after their date stamp. Two graduation paths:

1. **Promote up** -- if a `study/`, `company/`, `design/`, or `protocol/` doc
   references a `staging/*` file, the staged file MUST be merged into the
   consumer (or moved to its own canonical home) within the next editing
   session. Long-lived references into `staging/` are a code smell.
2. **Sweep out** -- files older than 30 days (per the `_YYYYMMDD` filename
   suffix) with no inbound references are candidates for deletion. The
   owning author confirms; otherwise they move to `archive/<YYYYMMDD>/`.

A scheduled weekly sweep task (DOCS-04) walks `staging/`, lists expired
files, and posts a report to `PROGRESS.md`.

## Filename rule

All files under `staging/` (other than `generated/`, which is script-driven)
MUST carry a `_YYYYMMDD` suffix so the TTL sweep can glob expired files.
Example: `audits/qe_link_spotcheck_20260411.md`.

## Not for

- Canonical study notes (put in `docs/study/`).
- Company-specific drills (put in `docs/company/<slug>/`).
- Interview-ready system design write-ups (put in `docs/design/`).
- Format specs / conventions (put in `docs/protocol/`).
- Frozen historical snapshots (put in `archive/<YYYYMMDD>/`).
