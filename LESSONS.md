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

## 2026-04-13 -- react-markdown v10 urlTransform strips custom schemes
- **Context**: Built a `lc://N` clickable-link convention so company prep docs could open a problem detail drawer in-place. Implemented via a custom `a` component override in MarkdownPreview that looks for `href` matching `/^lc:\/\/(\d+)$/`.
- **What went wrong**: In dev the links were styled correctly but clicks opened blank new tabs. The drawer never fired.
- **Root cause**: react-markdown 10's default `defaultUrlTransform` whitelists only `http`, `https`, `mailto`, `tel`, and relative URLs. Any other scheme (including `lc://`) is stripped to empty string BEFORE reaching custom component overrides. My `a` override received `href=""`, regex didn't match, fallback rendered `<a href="" target="_blank">` -> browser opens blank tab.
- **Fix**: Add `urlTransform={(url) => url}` (identity) to `<ReactMarkdown>`. Security still holds because our override handles the scheme split: `lc://` -> in-app button, everything else -> external anchor with `rel="noopener noreferrer"`.
- **Detection tip**: "Link clicks open blank tabs" with no console errors = DOM href is empty. Inspect the rendered `<a>` in devtools. If `href=""`, the markdown sanitizer is eating your custom scheme.
- **Applies to**: Any project using react-markdown 8+ with custom URL schemes for in-app navigation or app-specific actions.
- **Tags**: #frontend #react-markdown #custom-scheme #sanitization

## 2026-04-13 -- Orchestrator `all_done` flag is sticky; new-batch launches can silently bail
- **Context**: Added 10 new BQ rework tasks to task_db on 2026-04-13. Launched `autonomous_run.ps1 10` expecting all 10 to run. The runner completed only T-P0-380 then exited announcing "all_done=true -- all tasks complete!" even though 9 active tasks remained.
- **Root cause**: `.claude/session_state.json` had `all_done: true` from the **previous** batch (Pinterest rework, completed 2026-04-12 17:01). The new batch's child sessions update `last_task` and `last_status` on exit, but do NOT automatically reset `all_done`. The orchestrator checks `all_done` at the top of each loop iteration and bails if true, regardless of whether new tasks exist in the backlog.
- **Symptom**: Background runner exits after 1 session with exit 0 and a misleading "all tasks complete" log line, even though `task_db.py list` shows 9+ active tasks.
- **Detection tip**: If a launched autonomous runner exits much sooner than expected (e.g. after 1 session when 10 were configured), check `.claude/session_state.json` for `all_done: true` + confirm via `task_db.py list` whether active tasks actually remain.
- **Fix (manual)**: Before launching a new batch after a previous batch completed, reset: `python -c "import json, pathlib; p=pathlib.Path('.claude/session_state.json'); s=json.loads(p.read_text(encoding='utf-8')); s['all_done']=False; p.write_text(json.dumps(s, indent=2), encoding='utf-8')"`
- **Fix (systemic, future work)**: Either (a) `task_db.py add` should reset `all_done=False` atomically when new tasks land, or (b) the orchestrator should cross-check: if `all_done=true` but `task_db.py has-unblocked` returns unblocked tasks, ignore the flag and proceed.
- **Applies to**: Any project using `scripts/autonomous_run.{sh,ps1}` with multi-batch workflows where new tasks are added between runs.
- **Tags**: #orchestration #autonomous #session-state #sticky-flag

### [2026-04-15] Auto-bolding inside LaTeX/code leaks ** into rendered output
- **Context**: StudyNoteBuilder registered abbreviations and auto-bolded the first occurrence via `re.sub` over the entire content string. Docstring claimed it skipped math/code; implementation did not.
- **What went wrong**: A term whose first match was inside `$$...$$` (e.g. `\mathrm{MSE}`) became `\mathrm{**MSE**}`. In math mode `**` is not bold syntax — it renders as literal asterisks inside the formula. Reported by user viewing node 195.
- **Fix pattern**: Substitutions that semantically belong to prose must explicitly tokenise the input into prose vs protected spans (code fences, inline code, display math, inline math) and run the substitution ONLY on prose spans. Lookbehind/lookahead guards (e.g. `(?<!\*\*)`) are insufficient because they don't know about surrounding context like `\mathrm{...}`.
- **Also**: `save_to_db` with "skip-if-title-exists" idempotency made the fix harder to roll out — re-running the seed didn't refresh content. Consider making content-repair seeds explicitly support update-on-hash-mismatch, or at least document how to force a repair.
- **Tags**: #markdown #latex #regex-scoping #idempotent-seed-limitation

## [2026-04-16] Dual tasks.db scoping: `task_db.py` adds go to cwd's nearest CLAUDE.md
- **Context**: planted 16 active tasks from root `Gen_AI_Proj` cwd via `python .claude/hooks/task_db.py add`; launched `autonomous_run.sh MLInterviewPrep`. 10 sessions no-op'd; all burned.
- **What I learned**: `_find_project_root()` in `.claude/hooks/task_db.py` walks up from `Path.cwd()` for the first `CLAUDE.md`. Since Gen_AI_Proj and each sub-project (MLInterviewPrep, helixos, etc.) have their own `CLAUDE.md`, they resolve to DIFFERENT `.claude/tasks.db` files. A task added while cwd=root lives in root's tasks.db and is invisible to the sub-project. autonomous_run.sh cd's into the sub-project before spawning each session -- so sub-project scope saw 0 active tasks even though root scope had 16.
- **Fix / correct approach**:
  1. BEFORE `task_db.py add`, always `cd` into the project directory whose work this task represents. Root-cwd task adds are for *repo-level* work only.
  2. `autonomous_run.sh` now runs `python .claude/hooks/task_db.py has-unblocked` from `WORK_DIR` at the top of its main loop; if exit code != 0, break immediately (no wasted session). This catches future scoping mistakes as "orchestrator stops at session 0" rather than "orchestrator runs 10 no-op sessions".
  3. Migration between DBs: use `task_db.py add` (letting the target DB assign fresh global-counter IDs), NOT SQL INSERT with old IDs -- IDs can collide across DBs (T-P2-239 did, as two unrelated tasks).
- **Detection**: after adding tasks intended for a sub-project, verify `cd <subproject> && python .claude/hooks/task_db.py list --status active` shows them. If not, planting was mis-scoped.
- **Related**: scripts/migrate_active_tasks_to_mlp_20260416.py (this session's one-shot migration tool); commits 98d6cc4 (root) + 1022be8 (MLP).
- **Tags**: #orchestrator #task-db #multi-repo #session-scoping #silent-failure

### [2026-04-17] Claude Code usage limit breaks long `claude -p` batch scripts
- **Context**: `scripts/rewrite_nodes_to_cn.py` uses `claude -p` subprocess ~150 times to rewrite KG nodes. Phase A, A2, B ran cleanly (30+33+29=92 calls). Phase C hit the Claude Code subscription limit at call ~10; remaining 30 calls returned `api_error_status=429` with `{"result":"You've hit your limit · resets 7pm (America/Los_Angeles)"}` — NON-ZERO stdout, NOT stderr, `rc=1`.
- **What I learned**:
  1. `claude -p` usage is subject to the user's Claude Code subscription cap, reset daily at 7pm PT.
  2. The 429 response is JSON-formed and has `is_error: true` + `api_error_status: 429` + result string "You've hit your limit". Script parsed fine as JSON — the old RuntimeError triggered on rc=1 only.
  3. A batch of ~90-130 calls seems to exhaust one day's allowance.
- **Fix pattern**:
  1. Script should detect 429 pattern in result and either (a) sleep until next 7pm PT or (b) fail fast with clear "usage limit hit" message instead of generic RuntimeError.
  2. For long batch jobs: split into sub-200-call chunks, run across multiple days, or budget against actual measured cost-per-call.
  3. When resuming after limit reset, idempotency + history-table gating is essential — we would have re-done work otherwise.
- **Related task**: T-P1-498 KG-CN-01
- **Tags**: #claude-code #usage-limits #batch-scripts #429-retry

### [2026-04-18] `hasContent(node)` is the only sanctioned content-presence check
- **Context**: KG-UX-10 (T-P1-501) introduced tri-state click behavior: empty-content nodes skip the drawer and either expand children or play a focus animation. "Empty content" was initially going to be `node.content_length === 0` sprinkled across consumers — fast to write, impossible to evolve safely.
- **What I learned**: Once a predicate ("does this node have drawer content?") has product meaning — gating UX branches, keyboard a11y, badges — it MUST live behind a single util. Scattered `content_length === 0` / `> 0` / `description &&` checks at 4+ call sites means the day we add `is_stub`, enable lazy loading of descriptions, or change the empty-sentinel from 0 to null, we must hunt every site and hope we find them all. Class of bug: drawer opens on empty node in one place but not another; keyboard Enter on empty leaf plays focus animation but screen-reader label says "click to open".
- **Rule**: `hasContent(node)` from `src/frontend/src/components/framework/hasContent.ts` is the ONLY sanctioned way to answer "does this node have drawer content?". It accepts both API raw shape (`{content_length}`) and in-app `NodeMeta` shape (`{contentLength}`), so consumers never reshape.
- **How to apply**:
  1. New consumer needs "is this node empty?" → import `hasContent` and call `hasContent(node)` or `!hasContent(node)`. Never write `content_length === 0`, `content_length > 0`, or `!node.description` as a substitute.
  2. Display/threshold math (stub badge at `< 2000`, arc fraction = `contentLength / COMPLETENESS_FULL`, bar fill) is NOT a content-presence check — it legitimately reads `contentLength` directly. Keep these out of `hasContent`.
  3. If the presence rule changes (e.g. add `is_stub`, switch to lazy-loaded description), update `hasContent.ts` only. Callers need no change.
  4. Audit sentinel: `grep -rn 'content_length === 0\|content_length > 0' src/frontend/src/` must return 0 matches outside `hasContent.ts`.
- **Related task**: T-P2-503 (migration + lesson), T-P1-501 (introduced util)
- **Tags**: #frontend #kg #source-of-truth #predicate-util #future-proofing

### [2026-04-18] Background runner visibility: `nohup ... &` vs Bash `run_in_background`
- **Context**: Launched `autonomous_run.sh` with `nohup bash scripts/autonomous_run.sh 5 MLInterviewPrep > $LOG 2>&1 &` and marked the Bash tool call itself `run_in_background: true`. User noticed they (and I) could not track progress.
- **What went wrong**: `&` detaches the child from the parent shell. The parent shell exits ~immediately after forking, so the Bash tool reports "command completed" within seconds even though the real runner is still executing for 20+ minutes. `nohup` made this worse (SIGHUP-proof, but no stdout linkage back to Claude). The Bash tool's `run_in_background` was tracking the wrong process (the short-lived launcher, not the runner).
- **Fix / Correct approach**: Two options, pick one:
  1. **Bash `run_in_background` directly** (no `&`, no `nohup`): `bash scripts/autonomous_run.sh 5 MLInterviewPrep 2>&1` with `run_in_background: true`. Bash tool owns the runner's PID for its real lifetime; `Read` tool retrieves output; completion notification fires when the runner actually exits.
  2. **Detach + Monitor** (if you need the runner to survive session restarts): keep `nohup ... &` BUT pair with `Monitor` on `tail -f` of the log file, filtered via `grep -E --line-buffered 'Session [0-9]+/|complete|Committed|Error|FAILED|Traceback|Finished'`. Each session boundary or error surfaces as a chat notification.
- **Do NOT**: use `run_in_background` AND `nohup &` together. The Bash tracking becomes useless (sees launcher's quick exit) and you lose visibility.
- **Related task**: T-P1-505 / T-P1-506 batch launch
- **Tags**: #orchestration #autonomous #bash #monitor #visibility #gotcha

### [2026-04-19] Human-approval-gate language in task specs is sticky — write it self-cancelling
- **Context**: T-P0-516 had a "does NOT auto-start after 518 completes — waits for Discord approval" note in its description. After user approved 518 on 2026-04-19 and 518 flipped to completed (clearing the gate), two subsequent autonomous sessions STILL skipped 516 because they re-read the task spec fresh each session and interpreted the gate language as persistent.
- **What went wrong**: Autonomous sessions don't have session-to-session memory of "the human approval already happened." They read the task spec verbatim each time. Gate language phrased as a standing rule ("does NOT auto-start") is sticky even when the gate condition has been cleared externally.
- **Fix / Correct approach**:
  1. Preferred: use a separate blocking task (e.g., a dedicated "approval gate" task that gets marked completed by the human) rather than embedding gate prose inside the downstream task's description. Then normal dependency semantics handle it.
  2. Alternative: if you must embed gate prose, make it self-cancelling: "If T-P0-518 status=completed (check with task_db.py get), this gate is cleared and you should proceed immediately."
  3. When removing the gate language, UPDATE the task description via `task_db.py update --description`, not just rely on DB state. Autonomous sessions read the spec text, not the dependency graph semantics alone.
- **Cost**: 2 unnecessary session roundtrips (sessions 2 and 3 of Phase 2 runner skipped 516 and did 520/517 instead; session 4 finally picked 516 after I cleaned the description).
- **Related task**: T-P0-516 gate confusion (2026-04-19)
- **Tags**: #autonomous #task-spec #approval-gate #gotcha #workflow

## [2026-04-20] Generic toggle components must verify react-query invalidation keys against real consumers
- **Context**: Introduced `<GoldenToggleButton itemType="..." ... />` (T-P1-554) as a generic switch over three item types (framework_node, behavioral_example, company_document). Wrote invalidation keys by pattern guess: `["companies", "document", itemId]`.
- **What went wrong**: Discovered during T-P2-560 integration that the actual React-Query keys used by PrepNotesPage hooks were `["companyDocuments", companyId]` / `["companyDocument", docId]` -- pattern-named, NOT path-slug-named. Our pattern-guessed keys matched zero real queries, so toggling golden on a company doc didn't invalidate anything and the UI showed stale state until manual refresh.
- **Fix**: T-P2-560 commit `7a835c1` rewrote the invalidation block in GoldenToggleButton to use the real key names. Also surfaces a testing gap: unit tests for the toggle mocked useMutation but didn't assert on `queryClient.invalidateQueries` arguments.
- **Rule**: For any generic component that dispatches to multiple consumers by discriminator, grep the consumer for its actual query keys BEFORE wiring invalidation -- do not guess by convention. Add an assertion test for each discriminator path that verifies the exact invalidation keys match what the consumer reads.
- **Tags**: #react-query #invalidation #generic-components #integration-risk

## [2026-04-20] Copying raw notes into KG docs needs a two-pass pass-through (emoji + inline math)
- **Context**: User provided raw notes with `❌`/`✅` markers and requested "critical distillation" into the MHA/MQA/GQA leaf (node 225). I lifted the markers directly and also wrapped an inline formula `x = x + \text{Attn}(x)` in backticks (code span) to "make it look formula-like."
- **What went wrong**: (1) Project CLAUDE.md explicitly forbids emoji in any doc / config / code; I violated it by passing through `❌`/`✅` as-is. (2) Markdown code spans (backticks) suppress KaTeX, so the backticked inline formula rendered literally as `x = x + \text{Attn}(x)` instead of math. User caught both on the frontend.
- **Fix**: T-P2-571 — swap backticks to `$...$` for inline math; replace emoji with ASCII `**[误]** / **[对]**` tags. Also ran a cross-node emoji regex scan over all docs I edited this session to ensure nothing else leaked.
- **Rule**: When absorbing user-supplied raw notes into KG docs, do a two-pass translation: (a) **rendering pass** — every piece of math has to be in `$...$` or `$$...$$`; never use backticks for math ('looks like code' is not good enough reason). (b) **project-convention pass** — apply the no-emoji rule; replace unicode check/cross with ASCII text tags. Run a regex scan (`[\u2600-\u27BF\U0001F300-\U0001FAFF]`) before claiming done.
- **Tags**: #markdown #katex #emoji #project-convention #content-authoring

### [2026-04-23] Never trust a subagent's "identical" / "consistent" claim without a byte-level independent verification
- **Context**: Drafting a formal root-cause plan (T-P1-606) for the user's "emoji scan 每次都 fail" complaint. Spawned an Explore subagent to map scanners + invocation sites. Its survey stated: "IDENTICAL across all three scanners [check_emoji.py / check_emoji_files.py / lint_check.py]. No divergence detected." I used that as load-bearing evidence in the §1 table, §2 RC list, and §5 non-goals. User reviewed the plan and approved execution.
- **What went wrong**: Before writing any fix code I did a belated `pattern == pattern` byte compare myself -- the three regexes were NOT identical. `check_emoji.py` pattern length was 28; `check_emoji_files.py` and `lint_check.py` were 22. The extra 6 chars were `\u2600-\u26ff` + `\u2700-\u27bf` (BMP symbols + dingbats), deliberately removed from 2 of 3 scanners on 2026-04-11 (archive/progress_log.md:20) but missed on the third. This drift was the actual root cause of the user's pain -- not the Windows encoding issue I'd originally pinned it on. If I'd executed the original plan, I would have shipped a fix that left the real bug in place. Cost: one wasted user-review roundtrip + paused execution to report and re-scope.
- **Why the subagent was wrong**: It visually compared the three files' character ranges in its head and summarized "match" without exec-running a `pattern == pattern` check or printing `len(pattern)`. Visual comparison of multi-line regex-character-class literals on screen is a poor substitute for `hash(a.pattern) == hash(b.pattern)` -- whitespace, comment lines between range rows, and tired-eye typos all hide. A subagent summary reads authoritative; that veneer is the trap.
- **Fix / Correct approach**: For ANY subagent claim of "X and Y are identical / consistent / match" -- execute the literal equality check yourself before using the claim as plan input. One shell line: `python -c "from X import R as A; from Y import R as B; assert A.pattern == B.pattern, (len(A.pattern), len(B.pattern))"`. Cost: 30 seconds. Benefit: catches drift before it propagates into a committed fix. Treat subagent "consistency confirmations" the way you treat "build passes" from CI: necessary signal, not sufficient. If you can't express the claim as a 1-line assertion, the claim is probably too vague to be load-bearing.
- **Second-order rule**: When writing plan-mode prompts to subagents, ASK explicitly for the byte-level check, e.g. "run `A.pattern == B.pattern` and report the boolean + lengths, do not eyeball". Shifting verification from subjective inspection to objective assertion up front is cheaper than auditing the subagent's output after.
- **Related task**: T-P1-606 (blocked on user decision after this finding).
- **Tags**: #subagent #verification #regex #gotcha #plan-mode #due-diligence
