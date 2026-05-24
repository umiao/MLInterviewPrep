# `scripts/` — lifecycle namespaces (WSH-F1 / WSH-F3)

Helper scripts are organized into four lifecycle namespaces so a stale one-shot
script does not silently rot next to load-bearing infrastructure, and so
`lint_script_lifecycle.py` can mechanically tell them apart.

| Namespace          | Lifecycle  | Lint        | What goes here |
|--------------------|------------|-------------|----------------|
| `scripts/infra/`   | persistent | **exempt**  | Long-lived infrastructure the system depends on every run. |
| `scripts/migrate/` | run-once   | opt-in      | Unidirectional schema/data migrations. |
| `scripts/seed/`    | one-shot   | **linted**  | Data-seeding / backfill scripts. |
| `scripts/tools/`   | ephemeral  | **linted**  | Ad-hoc / dev utilities, throwaway converters. |
| `scripts/archive/` | retired    | **exempt**  | Dead one-shots kept only for git history (not linted, not run). |

## T-P2-353 lifecycle migration (2026-05-23, human-reviewed)

The deferred bulk migration ran once under human review. The 602 flat scripts
were partitioned by **risk**, not by name, because 81% of them hard-code
`Path(__file__).resolve().parent.parent` (DB at depth-1 below repo root) — a
naive `git mv` silently breaks that path. The applied rule:

| Bucket | Count | Disposition |
|--------|-------|-------------|
| **Hard-pinned** — referenced by `tests/` or `.github/ci.yml` (incl. dynamic `importlib.import_module`), or imported as a lib by sibling scripts (`study_note_builder`, `audit_mlsd_prose_quality`, …) | 15+3 | **Stay flat.** Moving breaks a test/CI/import. |
| **Depth-coupled** — undated, uses `.parent.parent` / `.parents[1]` | 332 | **Stay flat.** Moving breaks the script's own DB path; not worth a 332-file rewrite of frozen code. |
| **Dead dated one-shots** — `_YYYYMMDD` suffix, already run | 150 | **`git mv` → `scripts/archive/`.** Path breakage irrelevant (never re-run); history preserved. |
| **Path-safe undated** — no `.parent.parent`, no sibling-import, no test ref | 104 | **`git mv` → `seed/` (42) or `tools/` (62)** + `SAFE_DELETE_AFTER` marker. |

## Guard — going forward

The depth-coupled flat scripts (`.parent.parent` DB resolution) **stay flat** by
design: relocating one requires also rewriting its path depth. **New** scripts
should be born in the right namespace AND resolve paths from repo root via a
depth-independent anchor (walk up to the dir containing `data/`, not a fixed
`.parent.parent`). Existing flat scripts are **not** linted.

## Lifecycle markers (for scripts placed in `seed/` or `tools/`)

    # SAFE_DELETE_AFTER: YYYY-MM-DD   explicit retention date
    # RUN_ONCE                        intentionally one-shot

Run the lint: `python scripts/lint_script_lifecycle.py [--strict|--json|--verbose]`
