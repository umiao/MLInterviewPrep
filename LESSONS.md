# Lessons Learned

> Only log if: bug >10 min to debug, surprising behavior, effective pattern, non-obvious gotcha.

<!-- ENTRY FORMAT:

### [YYYY-MM-DD] Short descriptive title
- **Context**: What I was trying to do
- **What went wrong / What I learned**: The core insight
- **Fix / Correct approach**: How to do it right
- **Related task**: T-XX-N (if applicable)
- **Tags**: #tag1 #tag2 (for grep-based lookup)

-->

1. Windows UTF-8 (universal gotcha)
  - Python defaults to cp1252 on Windows. Non-ASCII paths/content break silently.
  - Rule: Force encoding="utf-8" on all open(), subprocess.run(), Path.read_text(). Force UTF-8 on sys.stdin/stdout/stderr in hooks.

  2. Stop hooks MUST output JSON to stdout (mentioned twice - both prompt and command types)
  - Exit codes alone = "JSON validation failed". Empty stdout = crash.
  - Rule: Every Stop hook prints {"ok": true} or {"ok": false, "reason": "..."} on every exit path (success, failure, timeout, error).
  Diagnostics go to stderr only.

  3. Hooks must never crash on bad stdin
  - /clear and other commands send unexpected input to hooks.
  - Rule: Never use bare json.load(sys.stdin). Always try/except with diagnostics. On parse failure: warn to stderr, exit 0.

  4. Shared hook_utils.py pattern
  - DRY boilerplate: UTF-8 init, JSON parsing, exception catching.
  - Rule: Use a single run_hook(name, main_fn) entry point for all hooks. Hooks become pure business logic.

  5. Rename/replace = reverse-reference scan
  - Plans list what to create, not what references the old thing.
  - Rule: grep -r "old_name" before and after. Add all referencing files to work list.

  6. Debug philosophy: check the contract before blaming the LLM
  - "Validation failed" = schema mismatch (deterministic). Not "LLM non-determinism".
  - Rule: (1) read exact error, (2) read docs for expected schema, (3) compare actual vs expected, (4) fix minimal delta. Never rewrite
  architecture on first failure.

### [2026-03-02] Ruff version drift between local and CI
- **Context**: requirements.txt had `ruff>=0.1.0` (loose pin) while CI ran `pip install ruff` (latest). Newer ruff versions add rules under the `UP` category that the project selects, causing CI-only lint failures invisible locally.
- **What went wrong / What I learned**: Loose version pins + separate install commands = silent version drift. CI gets a different ruff than local, and new rules break the build with no local repro.
- **Fix / Correct approach**: (1) Pin `ruff==X.Y.Z` exactly in requirements.txt. (2) CI lint job uses `pip install -r requirements.txt` instead of bare `pip install ruff`. (3) Pre-commit hook verifies installed ruff version matches the pin before every commit.
- **Tags**: #ruff #ci #version-drift #pre-commit

### [2026-03-15] SQLAlchemy create_all() does not ALTER existing tables
- **Context**: Added `framework_node_id` column to Problem model. Tests passed (in-memory DBs start fresh), but production startup crashed with `no such column: problems.framework_node_id`.
- **What went wrong / What I learned**: `Base.metadata.create_all()` only creates NEW tables. It never issues ALTER TABLE for existing ones. In-memory test DBs always start from scratch, so they never expose this gap. File-based SQLite DBs that already have the table get no schema updates.
- **Fix / Correct approach**: (1) Added versioned auto-migration system (`_run_migrations()` in `database.py`) that tracks applied versions in `schema_versions` table. (2) Each migration is idempotent. (3) Added file-based migration tests (`tests/test_migrations.py`) that create old schema, run migrations, and verify new columns exist. (4) Added schema audit test (`tests/test_schema_audit.py`) that checks all ORM columns exist in DB.
- **Tags**: #sqlalchemy #migration #sqlite #schema-drift #testing

### [2026-03-16] Tailwind v4 prose resets strikethrough on del/s elements
- **Context**: ~~strikethrough~~ text rendered by remark-gfm was not visually struck through despite correct `<del>` tags in DOM.
- **What went wrong / What I learned**: Tailwind CSS v4's `@tailwindcss/typography` (prose) resets `text-decoration` on inline elements including `<del>` and `<s>`, removing the browser default `line-through`. This is not a remark-gfm issue -- the HTML is correct but CSS overrides remove the visual.
- **Fix / Correct approach**: Add explicit `.prose del, .prose s { text-decoration: line-through; }` in the global CSS to restore the expected rendering. Check for similar prose resets when other HTML elements lose their default styling.
- **Tags**: #tailwind #prose #css #strikethrough #typography

### [2026-03-17] UI component best practices for scroll-aware mode switching
- **Context**: Designing sticky toolbar + scroll position preservation for prep notes edit/preview toggle.
- **What went wrong / What I learned**: Initial design had several anti-patterns that review caught:
  1. **DOM traversal to find scroll containers** -- walking up parentElement to find `overflow-y: auto|scroll` is fragile and breaks if CSS changes. Scroll containers are always known at design time.
  2. **Exposing bare state setters** -- exposing `setMode` lets callers bypass scroll capture. Silent bugs when new code calls `setMode` directly.
  3. **rAF guessing for layout timing** -- using `requestAnimationFrame` (even repeated) to wait for DOM layout is a guess. Async content (images, math plugins) can take arbitrarily long.
  4. **Duplicated logic across components** -- same handleModeSwitch + useLayoutEffect pattern in two files means change-one-forget-one bugs.
- **Fix / Correct approach**:
  1. **Explicit refs** -- pass scroll container refs as props or own them directly. Never discover them at runtime.
  2. **Encapsulate state transitions** -- wrap `setMode` into `switchMode(newMode, captureScroll?)` as the only public API. Impossible to forget side-effects.
  3. **ResizeObserver + timeout** -- observe content height stabilization, restore scroll when stable. 500ms timeout as fallback. Deterministic instead of frame-counting.
  4. **Extract shared hooks** -- `useScrollRestore(scrollContainerRef, mode)` used by both components. Single source of truth.
  5. **Visual affordances** -- sticky elements need `border-b` separator to distinguish from content. Functional, not decorative.
  6. **Guard arithmetic** -- `maxScroll <= 0` must short-circuit explicitly. Never leave division-by-zero protection as "mentioned in edge cases".
- **Tags**: #react #scroll #sticky #hooks #ui-patterns #code-review

### [2026-03-18] Stop hooks don't fire when Claude ends with pure text (no tool call)
- **Context**: A ruff F401 error (`import pytest` unused in test_import_blind75_notes.py) slipped through because the session ended with a pure text response, and the Stop hook only fires after tool calls.
- **What went wrong / What I learned**: The Stop hook (lint_check.py) is not guaranteed to run on every session exit. If Claude's final response is pure text with no tool call, the hook infrastructure never triggers. Additionally, the lint cache (`last_lint_pass`) could produce false passes if files changed between the cache write and the next session.
- **Fix / Correct approach**: (1) Added `scripts/check.sh` as a unified ruff+pytest runner. (2) Made running `bash scripts/check.sh` Step 0 in the Exit Protocol (CLAUDE.md) -- this is the primary defense. (3) Removed lint cache from lint_check.py so every Stop hook invocation runs a fresh check. The Stop hook remains as a backup safety net.
- **Tags**: #hooks #lint #ruff #exit-protocol #cache