<!-- Auto-generated: CLAUDE.md.local + shared. Do not edit directly. -->
# Project Context

## Project Overview
MLInterviewPrep is a personal ML/MLE interview preparation platform: a FastAPI + SQLAlchemy
backend stores companies, problems, framework nodes (KG), and rich per-company study
documents; a React + TypeScript frontend renders an interactive knowledge graph, a
Kanban-style prep board, and Markdown/KaTeX study notes. Content is authored as
idempotent Python seed scripts (the only sanctioned write path into the DB) and consumed
during live mock interviews and daily drills.

## Tech Stack
- Python 3.11+
- FastAPI, Uvicorn (backend API)
- SQLAlchemy 2.x (ORM, SQLite at `src/backend/mle_prep.db` / `data/mle_prep.db`)
- Pydantic v2, pydantic-settings (schemas, config)
- Anthropic SDK (LLM-assisted content drafting)
- python-docx, edge-tts (document + TTS utilities)
- httpx, python-multipart, python-dotenv
- React 19 + TypeScript + Vite (frontend)
- @xyflow/react + elkjs (KG visualization and layout)
- @tanstack/react-query (data fetching)
- react-markdown + rehype-katex + remark-math + remark-gfm (note rendering)
- react-syntax-highlighter, recharts, @hello-pangea/dnd, Tailwind CSS v4
- pytest, pytest-asyncio, ruff (backend tests + lint)
- vitest, eslint, typescript-eslint (frontend tests + lint)

## File Structure
- `src/backend/` - FastAPI app: `main.py`, `config.py`, `database.py`, `models/`, `schemas/`, `routers/`, `services/`, `scraper/`, `seed_data/`
- `src/frontend/` - React + Vite app (TypeScript)
- `scripts/` - Idempotent seed scripts (`seed_*.py`), audits, migrations, one-off tools (prefixed `_` for throwaways)
- `tests/` - pytest suite (backend)
- `data/` - Runtime data, including `mle_prep.db` (not in git)
- `docs/` - Workflow specs (autonomous mode, exit protocol, Chinese conversion spec, human input)
- `logs/` - Audit outputs, before/after snapshots, smoke-test artifacts
- `shared/` - Cross-project shared hooks, settings, and CLAUDE.md shared content
- `archive/` - Archived progress log + completed task log
- `scripts/git-hooks/` - Git hook sources (installed via `scripts/setup-hooks.sh`)

## Invariants (must always hold, violation = bug)
1. .env file never tracked by git
2. No hardcoded secrets in code
3. Every DB content row (company_documents, framework_nodes, problems, etc.) must have a git-tracked, idempotent Python seed script as its source of truth. Ad-hoc SQL or manual DB edits are prohibited — the DB is a regenerable projection of the seed scripts, never the source of truth itself.

## Surface Identification

Before editing DB content for a request that mentions a UI surface (the "dashboard," "left tab," "first nav item," "我们 app," "left nav," "the prep board," etc.), map widget -> data source FIRST. Pattern-matching from the prior turn's edit target is the failure mode (see `logs/2026-04-30_pinterest_root_cause.md`); the table below is the canonical prior that overrides it.

| Widget (file)                                         | Query key                  | API endpoint               | DB table / column                                |
|-------------------------------------------------------|----------------------------|----------------------------|--------------------------------------------------|
| `Dashboard.InterviewTimeline` (timeline/InterviewTimeline.tsx) | `["timeline","events"]`    | `GET /timeline/events`     | `interview_events`                               |
| `Dashboard.TodayFocusCards` (pages/Dashboard.tsx)     | `["dashboard","today"]`    | `GET /dashboard/today`     | derived: `framework_nodes` + `reading_progress`  |
| `Dashboard.WeeklyActivity` (charts/WeeklyActivityChart.tsx) | `["dashboard","activity"]` | `GET /dashboard/activity`  | derived: `problem_attempts` + `study_sessions`   |
| `Dashboard.PillarProgress` (pages/Dashboard.tsx)      | `["framework","tree"]`     | `GET /framework/tree`      | `framework_nodes` (depth-0 pillars)              |
| `Dashboard.CompanySummary` (pages/Dashboard.tsx)      | `["dashboard","summary"]`  | `GET /dashboard/summary`   | derived: `companies.status` counts               |
| `Dashboard.PrepQuickAccess` (pages/Dashboard.tsx)     | `["companies"]`            | `GET /companies`           | `companies.prep_notes` (markdown checklist)      |
| `KG.NodeDetail` (framework KG drawer)                 | `["framework","node",id]`  | `GET /framework/nodes/:id` | `framework_nodes` + `framework_node_problems`    |
| `CompanyDrawer.Notes` (per-company prep doc viewer)   | `["companies",id,"docs"]`  | `GET /companies/:id/docs`  | `company_documents.content` (prose study notes)  |

**Routing rules** (from the priors above; do NOT override based on which surface was edited last turn):
- Schedule / itinerary / calendar / "interview confirmed for X" / interviewer name + ISO-8601 date = `interview_events` (NEVER `company_documents.content`).
- Pipeline status (interested / applying / interviewing / offered / rejected) = `companies.status`.
- Daily focus / weakest topic / streak = derived from existing tables; no direct write target -- update the underlying `framework_nodes` or `reading_progress` row.
- Per-company checklist ("research X, mock Y, review Z") = `companies.prep_notes` (markdown).
- Prose study notes (and ONLY those) = `company_documents.content`.
- KG node prose = `framework_nodes.description`. Adding a LeetCode problem TO a node = INSERT into `framework_node_problems` join table, NOT prose mention in description.

**Idempotent seed pattern per row type** (Invariant 3 -- ad-hoc SQL is prohibited):
- `interview_events`: `scripts/_add_<company>_<date>.py`. Canonical key: `(company_id, scheduled_at, interviewer_name)`.
- `company_documents`: `scripts/seed_<company>_<doc>.py` with sentinel-based UPSERT.
- `problems`: `scripts/seed_<company>_lc_problems.py` (or focused `_add_*.py`); canonical key `leetcode_id` or `title`.
- `framework_nodes`: `scripts/seed_node_<id>_*.py` or pillar batches; canonical key `path`.
- `framework_node_problems`: usually written alongside problem seeds; canonical key `(node_id, problem_id)`.

**Enforcement layer** (independent of this section -- they are TWO layers, not one):
- `.claude/hooks/invariant3_guard.py` (T-P0-660 + T-P0-660b extension) blocks raw SQL writes from `scripts/migrations/*` to `data/*.db` AND blocks writes to `company_documents.content` whose payload contains schedule-shaped prose (ISO-8601 timestamp + interviewer-name pattern within 30 lines). This catches the failure mode when the priors above are overridden by recency priming.
- The `/dashboard` skill (`.claude/skills/dashboard/SKILL.md`) references this table as its single source of truth and walks the 6-step protocol before any DB write.

## Autonomous Mode Invocation

The proven invocation pattern for autonomous mode in this project:

```bash
cd <project-root> && bash scripts/autonomous_run.sh [max_sessions]
```

Where:
- `<project-root>` is THIS project's directory (the one containing `CLAUDE.md` and `.claude/tasks.db`).
- `[max_sessions]` is a **positive integer** (default 5). Non-integer args are rejected at startup with a clear error; the script will not silently misinterpret a project name as a count (workspace-wide invariant `INV-AUTORUN-2`).
- The script refuses to run if the caller's cwd is not the project root (`INV-AUTORUN-3`). Always `cd` first.

**If `claude -p` hangs silently** (zero log output for >60s after the "Session N/N" banner): this is a known transient class — cold-start of MCP/plugin/hook init or transient API slowness, NOT auth, NOT script-form drift. Kill the runner, remove `.claude/autonomous.lock`, retry. See `docs/investigations/autorun_hang_2026-05-02.md` (in the workspace root) and root `LESSONS.md` 2026-05-02 entry for the full diagnosis.

**Hang auto-recovery (AR-7 + AR-11 + AR-12 + AR-15 + AR-18)**: each `claude -p` invocation is wrapped with a 900s default timeout (override via `CLAUDE_P_TIMEOUT`). As of 2026-05-03 (AR-12/15/18), the wrapper classifies each timeout via the `_classify_head` helper into 5 outcomes, with a working-tree (porcelain hash) extension layer between the HEAD-diff classification and the AR-7 retry/abort path:

| Outcome | Trigger | Action |
|---------|---------|--------|
| `head_legit` | HEAD moved + task-ID-shaped commit `[T-XXX-NNN]` + (no `EXPECTED_TASK_PREFIX` set OR strict match) + non-WIP | INFO success, return 0 (no retry) |
| `head_legit_unexpected` | HEAD moved + task-ID-shaped commit + `EXPECTED_TASK_PREFIX` set but mismatched + non-WIP | INFO soft-credit success, return 0 |
| `head_wip` | HEAD moved + task-ID-shaped + `[T-XXX-NNN WIP]` suffix | WARN + retry; second WIP-only timeout aborts 124 |
| `head_external` | HEAD moved + commit prefix NOT task-ID-shaped (e.g. `[T-adhoc-...]` lowercase) | WARN external-commit + fall through to AR-12 |
| `head_unchanged` | HEAD did not move | Fall through to AR-12 |

After classification, if `head_external` or `head_unchanged` AND working-tree porcelain hash changed AND extension not yet used, **AR-12** kicks in: log `INFO: working tree changed... extending +CLAUDE_P_TIMEOUT_EXT (default 300s) once`, re-run `claude -p` for the extension window, re-classify. The extension is a one-shot per wrapper invocation. If extension also fails to commit, fall through to **AR-7** retry: WARN attempt 1/2 → ERROR abort 124 on second hang.

**Hyperparameters & kill switches** (env-overridable):
- `CLAUDE_P_TIMEOUT=900` — default per-attempt timeout. Bumped from 600 in AR-15 (2026-05-03) because pytest 1232 + cold-start MCP + multi-file edits leave <8min for actual reasoning at 600s.
- `CLAUDE_P_TIMEOUT_EXT=300` — AR-12 working-tree extension window.
- `CLAUDE_P_DISABLE_PROGRESS_SIGNAL=1` — disable AR-12 (porcelain hash check). Falls back to AR-7 on `head_unchanged`.
- `CLAUDE_P_DISABLE_ATTRIBUTION=1` — disable AR-18 (task-ID sanity regex + EXPECTED_TASK_PREFIX). Falls back to pre-AR-18 behavior (any non-WIP HEAD movement credits as success — vulnerable to external-commit false positives).
- `EXPECTED_TASK_PREFIX` — set by outer loop's `task_db.py list --status active` peek. Best-effort tight-match. If unset, falls back to mandatory sanity regex only.

**Operational rule**: external git commits (main-thread Claude, IDE auto-commit, etc.) on the same repo during an autorun are now safe — AR-18's mandatory sanity regex (`^\[T-[A-Z0-9-]+(\ WIP)?\]`) rejects ad-hoc commit prefixes (which use lowercase like `[T-adhoc-...]`). Pre-AR-18, this was a hard rule (no concurrent commits); now it is a soft preference (concurrent commits with task-ID-shaped messages might still cause `head_legit_unexpected` if the prefix matches a real task ID).

Manual intervention (kill + clear lockfile) is only needed if the wrapper itself fails to fire. Telemetry:
- `grep -c "timed out at exit but task committed" logs/autonomous*.log` — AR-11 success count
- `grep -c "AR-12" logs/autonomous*.log` — AR-12 extension trigger count
- `grep -c "AR-18" logs/autonomous*.log` — AR-18 attribution rejection count

**Do NOT use** `claude -p PROMPT --bare` to test auth — `--bare` skips OAuth by design and will report "Not logged in" regardless of state. Use `claude auth status` (returns structured JSON with `loggedIn`, `email`, `subscriptionType`) for the proper auth probe.

**Workspace-wide alternative**: from the workspace root, `bash scripts/autonomous_run.sh [max_sessions] <project_dir>` delegates to a sub-project. Functionally equivalent to the local form; the local form is preferred for clarity (no risk of cross-project confusion).

## Key Constraints
- All API keys and cookies from .env, never hardcoded
- Every function must have type hints and docstring
- **Dependency source-of-truth**: Both `pyproject.toml` `[project].dependencies` and
  `requirements.txt` list dependencies. Keep them in sync manually. When adding a new
  dependency, add it to BOTH files. `pyproject.toml` is the canonical spec;
  `requirements.txt` exists for `pip install -r` convenience.

## Git Conventions
- **Commit message format**: `[T-XX-N] Brief English description of what was done`
  - Describe the IMPLEMENTATION (what was done), not the task spec verbatim
  - If the task title is in Chinese, translate/summarize to English
  - Use the same brief-title style as PROGRESS.md entries
  - Example: Task "刷新页面后conversation会丢失" -> `[T-P0-165] Recover conversation from plain log after page refresh`
- **Language**: All commit messages in English. No CJK characters.
- **Force-push**: Always use `--force-with-lease`, never `--force`.

## Code Style
- Use ruff for linting
- Type checking: mypy
- Test: pytest
- **Regression tests**: When fixing a bug, always add a regression test
- **No emoji**: Never use emoji characters in code, docs, configs, or hook output.
  Use ASCII text tags (e.g., [DONE], [FAIL], [WARN]) instead.
- **Explicit UTF-8**: All file I/O and subprocess calls must specify `encoding="utf-8"`.
  Never rely on locale defaults (cp1252 on Windows).
- **Windows-compatible docs**: Shell commands in documentation must work on both
  bash and Windows PowerShell 5.x. Use separate lines instead of `&&` chaining.
  For bash-only commands (`source`, `rm -rf`, `~` paths), provide a labeled
  PowerShell alternative.

## Prohibited Actions
- **Never use bare `python` in hook commands or scripts.** The Windows Store
  stub (`AppData/Local/Microsoft/WindowsApps/python.exe`) exits with code 49.
  Use `/c/Anaconda/python.exe` (absolute path) in `settings.json` hooks.
  The SessionStart hook `setup_python_env.sh` injects Anaconda into PATH
  for Bash tool calls via `CLAUDE_ENV_FILE`.
- Never hardcode API keys, cookies, or personal info
- Never use emoji characters anywhere in the project
- Never use subprocess.run(text=True) without encoding="utf-8"
- Never read/write files without explicit encoding="utf-8"
- **Never use `os.kill(pid, 0)` for process liveness checks.** On Windows,
  `signal.CTRL_C_EVENT == 0`, so this sends Ctrl+C to the target process
  instead of probing it.  Use `ctypes.windll.kernel32.OpenProcess()` on
  Windows, `os.kill(pid, 0)` only on Unix, behind a `sys.platform` guard.
- **Never duplicate utility functions across files.** If the same helper
  exists in >1 file, extract it to a shared module and import it.
- **TASKS.md is read-only** -- auto-generated from `.claude/tasks.db`. Never edit directly.
  Use `python .claude/hooks/task_db.py <command>` for all task operations.
  A PreToolUse hook blocks any Write/Edit targeting TASKS.md.
- **Task IDs are auto-generated.** Never invent IDs manually.
  Use `task_db.py add --title "..." --priority P0` and the system assigns the next ID.
- **For batch operations**: use `task_db.py batch --commands '[...]'` to wrap multiple
  commands atomically.

## Behavior Rules
- **Fix violations immediately**: When a check you run (lint, emoji scan, tests) discovers
  violations in project files, fix them immediately.

### Verification Requirements
- **"Tests pass" is necessary but not sufficient.** If your task changes a
  server entry point, subprocess launcher, or configuration loader, you MUST
  also run the actual code (not just mocked tests) and verify it produces
  expected output.
- **Smoke test rule**: After creating or modifying a script that users will
  invoke directly (e.g. `run_server.py`, `start.ps1`), run it for real and
  verify it reaches the expected state (e.g. "Application startup complete").
  A crash during dry-run is a blocker, not an "unrelated issue."
- **Mock tests verify arguments. Real tests verify behavior.** Both are
  needed for subprocess-based code.
- **Platform-sensitive code needs platform-specific review.** Before using
  any `os.*`, `signal.*`, or `subprocess.*` API, check the Python docs for
  Windows behavior differences.  If a function has `sys.platform` branches,
  test both branches.  Common traps: `os.kill` signal semantics, `os.getpgid`
  not existing, `signal.SIGTERM` vs `CTRL_BREAK_EVENT`.
- **Diff First rule for investigation tasks.** When given a working example
  (user-provided command, docs snippet, or reference implementation) and a
  broken implementation, the FIRST step is a mechanical diff of flags, args,
  and config between the two.  Every delta is a finding.  Do NOT skip to
  output-format analysis or external doc research before completing this diff.
  Analysis of "why" comes AFTER identifying "what's different."

### Task Planning Mode
When the user says "plan tasks" / "edit TASKS.md only" / contains keyword "TASKS.md":
- **ONLY** read code and use `task_db.py` commands (add/update/reorder tasks, set dependencies)
- Do **NOT** execute any task, write code, create files, or run tests
- Do **NOT** use TaskCreate/TaskUpdate/TaskList tools (session-only, not persistent)
- Write clear task specs with acceptance criteria, complexity, and dependencies
- End by summarizing what changed

## Task Planning Rules

These rules prevent the class of bugs found in T-P0-24 (review gate UX), where
the task was marked DONE but the drag-to-REVIEW workflow was broken because
planning missed entire branches of behavior.

1. **Scenario matrix**: Before writing code for any conditional UX task, list
   ALL condition branches with their expected outcome in the task spec.
   Check: every `if` in the AC has a corresponding `else`.
   Example: "Gate ON: modal appears. Gate OFF: direct transition + pipeline
   starts automatically."

2. **Journey-first ACs**: At least one AC per task must be a full user journey:
   "User does X -> system does Y -> user observes Z." Unit-level ACs
   ("endpoint returns 200") are necessary but not sufficient.

3. **Cross-boundary integration**: When a task spans backend + frontend, at
   least one AC must verify end-to-end wiring: API call triggers expected
   backend behavior AND result appears in UI. Verifying each piece exists
   in isolation is not enough.

4. **"Other case" gate**: Every conditional AC ("when X is enabled...") must
   explicitly specify what happens when the condition is false. If the inverse
   case is not specified, add it before starting work. Missing inverse =
   missing requirement.

5. **Manual smoke test AC**: Every UX task must include an AC of the form
   "Manually verify: [exact browser action] -> [expected visual result]."
   "Build succeeds" and "tests pass" do not catch wiring failures.

6. **New-field consumer audit**: When a task introduces a new model field
   (e.g., `plan_status`) that existing UI components might display, list
   ALL components that render related data and verify each uses the correct
   source of truth.  A new field that no consumer reads yet is dead code;
   a consumer that reads the new field before it is populated shows stale data.
   (Post-mortem: T-P0-57/T-P0-59 -> T-P0-66 -- `hasNoPlan` used `plan_status`
   instead of `description`, showing wrong state for all existing tasks.)

## State Machine Rules

1. **Document transitions completely**: Any workflow with status transitions
   must document in the task spec: (a) all valid states, (b) the trigger for
   each transition, (c) side-effects attached to each transition.
   Side-effects on transitions (e.g., "entering REVIEW starts the review
   pipeline") are the backend's responsibility -- the frontend only initiates
   the status change, never the side-effect directly.

## Hook Development Rules
- **Never use bare `json.load(sys.stdin)`** -- always use `hook_utils.safe_read_stdin()`
- **Hooks must never crash** -- infrastructure errors must exit 0, never a raw traceback
- **Use `hook_utils.run_hook()`** as the entry point for all hooks
- **New hooks**: copy `.claude/hooks/_template.py` and fill in the logic

## Human Input Protocol
- Tasks requiring human-provided files are tagged `[NEEDS-INPUT: description]` in TASKS.md
- `docs/human_input/` contains the master checklist and per-task spec files
- Use `/collect-input` to check status, guide input, validate, and unblock tasks

---

## Session Workflow

The **SessionStart hook** provides authoritative startup context including task status,
recent progress, and lessons. Trust its output at session start.

### During Work
- Work on **one task at a time**. Move it to "In Progress" via `task_db.py update T-XX-N --status in_progress`.
- Refer to the task's **Acceptance Criteria** as your definition of done.
- If you discover new work, add it via `task_db.py add`. Don't silently absorb scope.
- For **L-complexity tasks**, maintain `.claude/checkpoint.json` with sub-task progress:
  ```json
  {"task": "T-XX-N", "subtasks": [{"name": "...", "done": false}],
   "last_working_file": "src/...", "last_working_line": 42}
  ```

### Autonomous Mode
When triggered via `scripts/autonomous_run.sh`, read `docs/workflow/autonomous.md` for
the full ruleset.

---

## Exit Protocol

Before stopping, complete these steps (the **Stop hook** enforces them):

1. **Verify**: Run code, check outputs exist, run tests if applicable
2. **PROGRESS.md**: Append a session entry (format below)
3. **TASKS.md**: Update task status via `task_db.py update T-XX-N --status completed`
4. **LESSONS.md**: Only if bug >10 min, surprising behavior, or effective pattern

```
## YYYY-MM-DD HH:MM -- [TASK-XXX] Brief Title
- **What I did**: 1-3 sentences
- **Deliverables**: Files created/modified
- **Sanity check result**: What was verified
- **Status**: [DONE] / [PARTIAL] (what remains) / [BLOCKED] (why)
- **Request**: `task_db.py update T-XX-N --status completed` / No change
```

Full protocol details: `docs/workflow/exit-protocol.md`

---

## File Conventions

| File | Purpose | Update frequency | Size invariant |
|------|---------|-----------------|----------------|
| `TASKS.md` | Auto-generated from `.claude/tasks.db` | Auto-regenerated by task_db.py | Read-only. Use `task_db.py` for all changes. |
| `PROGRESS.md` | Chronological session log | Every session (append-only) | Under ~300 lines. Archive older sessions to `archive/progress_log.md` when exceeded. Keep ~40-50 most recent sessions. |
| `LESSONS.md` | Critical knowledge and mistakes | Only when a lesson is learned | N/A |

**`.claude/tasks.db`** is the runtime source of truth for task state.
**TASKS.md** is the git-tracked projection (auto-generated, read-only).

**PROGRESS.md** archival convention: When the file exceeds ~300 lines, move older session entries (keeping the most recent ~40-50 sessions) to `archive/progress_log.md`. The archive file uses chronological order (oldest first) matching PROGRESS.md structure. New content is appended to the archive file on subsequent archivals.
