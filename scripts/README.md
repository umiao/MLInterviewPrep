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

## T-P2-353 lifecycle migration (2026-05-24, human-reviewed)

The deferred bulk migration ran once under human review. The 602 flat scripts
were partitioned by **risk**, not by name, because most of them resolve the DB /
repo root from a `__file__`-anchored path that assumes the script sits exactly
one level below repo root — a naive `git mv` silently breaks that path. Final
disposition (counts are post-correction; see the caveat below):

| Bucket | Count | Disposition |
|--------|-------|-------------|
| **Hard-pinned** — referenced by `tests/` or `.github/ci.yml` (incl. dynamic `importlib.import_module`), or imported as a lib by sibling scripts (`study_note_builder`, `audit_mlsd_prose_quality`, …) | 18 | **Stay flat.** Moving breaks a test/CI/import. |
| **Depth-coupled** — any `__file__`-anchored repo-root resolution (see idioms below) | 363 | **Stay flat.** Moving breaks the script's own DB path; not worth rewriting frozen code. |
| **Dead dated one-shots** — `_YYYYMMDD` suffix, already run | 150 | **`git mv` → `scripts/archive/`.** Path breakage irrelevant (never re-run); history preserved. |
| **Path-safe undated** — *no* `__file__` use at all, no sibling-import, no test ref | 71 | **`git mv` → `seed/` (16) or `tools/` (55)** + `SAFE_DELETE_AFTER` marker. |

### Depth-coupling is more than `.parent.parent` (the trap that cost two rounds)

The first cut keyed only on `Path(__file__)...parent.parent` / `.parents[1]` and
wrongly moved ~33 scripts that encode the **same** depth-1 assumption via other
idioms. The `lint_script_lifecycle.py` live-reference scan caught the resulting
breakage, but the rule is now: **a script is depth-coupled (stays flat) if it
uses `__file__` for *anything*.** The equivalent idioms to watch for:

    Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
    Path(__file__).resolve().parents[1]
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # nested dirname
    os.path.join(os.path.dirname(__file__), "..", "data", ...)    # '..' join
    Path(__file__).resolve().parent / "study_note_builder.py"     # sibling to a pinned lib
    os.path.join(os.path.dirname(__file__), "node_translations")  # sibling dir

Only scripts whose paths are **cwd-relative** (`Path("data/...")`) or that import
the app via `from src...` (resolved through `sys.path`, not file location) are
safe to relocate.

## Guard — going forward

Depth-coupled flat scripts **stay flat** by design: relocating one requires also
rewriting its path depth. **New** scripts should be born in the right namespace
AND resolve paths from repo root via a depth-independent anchor (walk up to the
dir containing `data/`, not a fixed `__file__` depth). Existing flat scripts are
**not** linted.

## Lifecycle markers (for scripts placed in `seed/` or `tools/`)

    # SAFE_DELETE_AFTER: YYYY-MM-DD   explicit retention date
    # RUN_ONCE                        intentionally one-shot
    # PINNED_BY: <ticket|test|importer>   in-use / to-be-fixed -- never auto-retired

`PINNED_BY` is for "in use, do not delete" (distinct from "observe then retire").
The lint *also* auto-pins any script with a **live code reference** (static OR
dynamic import, or a path-literal call) found by scanning `.py`/`.yml`/`.sh`/
`Makefile` (markdown/logs/archive/ are ignored — a prose mention is not a
dependency). So a retirement decision is based on **live references at
retire-time**, not on static visibility at write-time — closing the gap that the
migration was bitten by. Pinned scripts are reported (with their referrers) for
human review and never trip `--strict`.

Run the lint: `python scripts/lint_script_lifecycle.py [--strict|--json|--verbose]`
