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

### [2026-03-19] Test fixtures based on assumed HTML structure break on real pages
- **Context**: Forum extractor `extract_post_links` used `ul.hotlist li a` selector based on a hypothetical page structure. Live scrape returned 0 links because the real 1point3acres tag page uses a Discuz table layout (`th > a[href*=thread-]`).
- **What went wrong / What I learned**: Three issues surfaced only during live execution: (1) The extractor's CSS selector was wrong for the actual page. (2) `os.environ.get()` in the service didn't load `.env` -- only pydantic-settings `get_settings()` does. (3) Each `th` contained duplicate thread links (2 anchors per row), causing UNIQUE constraint violations on `external_post_id`.
- **Fix / Correct approach**: (1) Added dual-strategy extractor: try table layout first, fall back to hotlist. Deduplicate by href. (2) Use `get_settings()` instead of `os.environ.get()` for config values loaded from `.env`. (3) Added same-seed `external_post_id` conflict check in upsert. Key takeaway: always validate extractors against real HTML before marking scraper tasks as done.
- **Tags**: #scraper #extractors #testing #live-validation #pydantic-settings
### [2026-03-20] Rate limiting must live in exactly one layer
- **Context**: Forum scraper was taking 20-45s per page despite 0.5-5s site config, because rate delays existed in three places: site config (service layer), `fetch_page_cdp(delay=(5,15))`, and `fetch_page_with_cookie(delay=(5,15))`.
- **What went wrong / What I learned**: Each Playwright method had its own default `delay` parameter that stacked on top of the service-layer rate limit. A 255-page scrape estimated at 40min took 2+ hours. Additionally, the failed CDP attempt (Playwright startup + ECONNREFUSED) added ~2-3s overhead per page even though no Chrome debug instance was running.
- **Fix / Correct approach**: (1) Rate limiting belongs in the service/orchestration layer only. Crawler methods should default to `delay=(0,0)`. (2) Add a fast TCP probe (`socket.create_connection` with 0.5s timeout) before attempting CDP -- skip the expensive Playwright startup entirely. (3) Commit DB per-page, not end-of-run: the first crash lost 50+ pages of scraped links. (4) For long-running scrapes, the data pipeline pattern: idempotent upserts + per-item commits + resumable offset = safe to kill and restart.
- **Tags**: #scraper #rate-limiting #performance #crash-safety #playwright
### [2026-03-20] batch command doc/code mismatch caused silent data loss
- **Context**: `task_db.py batch` created 3 tasks with empty title and description. The batch call used nested `{"cmd": "add", "args": {"title": "..."}}` format as documented in CLAUDE.md and SKILL.md. But the actual code reads flat keys: `cmd_dict.get("title", "")`.
- **What went wrong / What I learned**: (1) Documentation (CLAUDE.md, SKILL.md) documented an `args` nesting format that never existed in the implementation. (2) The batch add path had no validation -- empty title was silently accepted, creating useless task records. (3) The batch result `{"ok": true}` gave no signal that data was lost. Three bugs compounded: wrong docs + no validation + misleading success response = silent corruption only caught by manual inspection.
- **Fix / Correct approach**: (1) Made batch() support BOTH flat and nested-args formats (merge `args` dict into top-level before processing). (2) Added title-non-empty validation that raises ValueError before creating the task. (3) Fixed docs in CLAUDE.md and SKILL.md to show correct flat format. (4) Added 6 regression tests covering both formats and validation. Key takeaway: any "fire and forget" CLI command that returns `{"ok": true}` must validate required fields -- silent success with missing data is worse than a crash.
- **Tags**: #task-db #batch #validation #docs-code-mismatch #silent-failure

### [2026-03-20] Claude Code Bash tool ignores .bashrc -- use CLAUDE_ENV_FILE and absolute paths
- **Context**: Scheduled task and manual Bash calls failed with exit code 49 because `python` resolved to the Windows Store stub (`AppData/Local/Microsoft/WindowsApps/python.exe`). Prior fix added Anaconda to PATH in `~/.bashrc` + `~/.bash_profile`, but this did NOT work.
- **What went wrong / What I learned**: The Claude Code Bash tool runs **non-login, non-interactive** shells (`shopt login_shell = off`, `$BASH_ENV` empty). These shells do NOT source `.bashrc`, `.bash_profile`, or `/etc/profile`. The `.bashrc` fix was a no-op. Additionally, all hooks in `settings.json` using bare `python` also resolved to the stub -- they were silently failing too.
- **Fix / Correct approach**: Two-part fix: (1) **SessionStart bash hook** (`setup_python_env.sh`) writes `export PATH="/c/Anaconda:..."` to `$CLAUDE_ENV_FILE` -- this is the ONLY mechanism to inject env vars into the Bash tool. Must be a bash script (not Python, since Python itself is broken at that point). (2) **Absolute paths** in all `settings.json` hook commands: `/c/Anaconda/python.exe` instead of bare `python`. `.bashrc`/`.bash_profile` are irrelevant for Claude Code.
- **Tags**: #windows #python #path #hooks #bash-tool #claude-code #scheduled-tasks

### [2026-04-07] SQLite + naive datetime: never assume UTC, check the data convention first
- **Context**: User reported Lyra appointment displaying as 4 PM instead of 9 AM (7-hour shift = PDT offset). Diagnosed as SQLite stripping timezone info.
- **What went wrong / What I learned**: Jumped to "treat naive datetimes as UTC" fix without checking the existing data convention. ALL existing events (seeds, API-created) were stored as **naive Pacific Time** and displayed correctly. The real bug was only in the frontend form: `new Date(val).toISOString()` converted to UTC before POST, but the rest of the system expected local time. My first "fix" (adding `Z` suffix to all responses) broke every correctly-stored event by reinterpreting local times as UTC. Three distinct issues conflated into one wrong diagnosis: (1) frontend form converting to UTC on submit, (2) SQLite not preserving TZ info, (3) response serialization format. Only (1) was the actual bug.
- **Fix / Correct approach**: (1) Check existing data in the DB before assuming a timezone convention. (2) Frontend: send naive datetime-local value directly, no `.toISOString()`. (3) Backend: add `NaivePacific` Pydantic validator that strips TZ info and converts TZ-aware inputs to Pacific before storage. (4) Fix corrupted DB rows. Key lesson: **"check what's in the database" before writing a timezone fix. The convention is in the data, not in the schema declaration.**
- **Tags**: #timezone #sqlite #naive-datetime #frontend #data-convention #investigate-first

### [2026-04-08] DB-only content must have a recovery path
- **Context**: Ran `content_module_arbitration.py` (hardcoded English) which overwrote Chinese translations that existed only in SQLite DB
- **What I learned**: Translated content stored only in DB with no git-tracked backup and no reproducible seed script is vulnerable to overwrite. The DB file (mle_prep.db) is not in git, so there's no version history to recover from.
- **Fix / Correct approach**: After translating content, update the seed script to contain the translated version (Chinese), or export translated content to a git-tracked JSON/markdown backup file. Any seed script that writes to DB must be the source of truth -- if content evolves past the seed script, the script becomes dangerous.
- **Tags**: #data-loss #backup #sqlite #translation #seed-script

### [2026-04-08] Markdown math `|` conflicts with remark-gfm table parsing
- **Context**: Formula rendering broke on system design page using remark-gfm + remark-math + rehype-katex
- **What I learned**: `remark-gfm` parses `|` as table cell separators BEFORE `remark-math` processes `$`/`$$` blocks. A formula like `$P(\text{click}|m, q, u)$` gets its `|` eaten by the GFM table parser, breaking the math. Additionally: (1) multi-line `$$` blocks can fail, (2) consecutive `$$` blocks need blank lines between them.
- **Fix / Correct approach**: Always use `\mid` instead of `|` for conditional probability notation in LaTeX when the renderer uses remark-gfm. Keep `$$` display math on single lines. Separate consecutive `$$` blocks with blank lines.
- **Tags**: #markdown #katex #remark-gfm #formula #rendering

### [2026-04-08] autonomous_run.sh uses sub-project task_db, not root
- **Context**: Created 8 tasks in root .claude/tasks.db, launched autonomous_run.sh with MLInterviewPrep sub-project. Session picked up a different task (T-P2-278 from MLInterviewPrep's own tasks.db).
- **What I learned**: When autonomous_run.sh runs with a sub-project directory (e.g., `autonomous_run.sh 8 MLInterviewPrep`), it uses `--cwd MLInterviewPrep/` which means the session reads MLInterviewPrep/.claude/tasks.db, NOT the root tasks.db. Tasks must be created in the correct sub-project's task_db for autonomous execution to pick them up.
- **Fix / Correct approach**: Always create tasks in the sub-project's task_db when planning autonomous execution for that sub-project. Use `cd MLInterviewPrep && python .claude/hooks/task_db.py add ...` not `cd Gen_AI_Proj && python .claude/hooks/task_db.py add ...`.
- **Tags**: #autonomous #task-db #sub-project #orchestration

### [2026-04-10] Validation must happen on a surface isomorphic to the production path
- **Context**: Baking Studio task delivered 4 failures in one session: (1) seed function skipped new recipes due to all-or-nothing guard, (2) SQLite WAL concurrent write silently lost data, (3) `tsc --noEmit` passed but `npm run build` (`tsc -b`, stricter) failed, (4) CSS changes never visually verified.
- **What I learned**: All 4 are the same root cause: validating on a surface not isomorphic to the production path. INSERT success != API-visible data. `tsc --noEmit` != production build. "Compiles" != "looks right". The single rule: **verify through the consumer (API, browser, production build), never through the producer (DB insert, lenient compiler, code inspection).**
- **Fix / Correct approach**: (1) After DB seed/insert, always verify via API `curl`, not `SELECT`. (2) Use `npm run build` (not `tsc --noEmit`) as TypeScript check -- matches production build. (3) For UI changes, run DOM assertions or take a screenshot via Playwright. (4) Side-effect verification must always go through the consumer path.
- **Tags**: #validation #production-path #consumer-verification #visual-testing #seed #wal #typescript
