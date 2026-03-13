# Progress Log

> Append-only session log. Each session adds an entry at the bottom.
> Never edit previous entries.

<!-- Entry format:

## YYYY-MM-DD HH:MM -- [T-XX-N] Brief Title
- **What I did**: 1-3 sentences on concrete actions taken
- **Deliverables**: List of files created/modified
- **Sanity check result**: What I verified and the outcome
- **Status**: [DONE] Done / [PARTIAL] Partial (what remains) / [BLOCKED] Blocked (why)
- **Request**: Cross off TASK-XXX / Move TASK-XXX to In Progress / No change

-->

## 2026-03-01 -- Task Deduplication Defense-in-Depth
- **What I did**: Implemented 3-layer dedup defense: clarified docs (CLAUDE.md, exit-protocol.md), added read-time filtering in session_context.py, created task_dedup_check.py stop hook, and registered it in settings.json. Added 10 tests.
- **Deliverables**: Modified CLAUDE.md, docs/workflow/exit-protocol.md, .claude/hooks/session_context.py, .claude/settings.json. New files: .claude/hooks/task_dedup_check.py, tests/test_task_dedup.py.
- **Sanity check result**: ruff clean, 11/11 pytest pass, hook exits 0 on clean TASKS.md, hook exits 2 and prints diagnostic on duplicate task IDs.
- **Status**: [DONE]
- **Request**: No change

## 2026-03-02 -- Git Pre-Commit Hook for Ruff Version Consistency
- **What I did**: Pinned ruff==0.1.14 in requirements.txt, fixed CI lint job to use requirements.txt, created a POSIX pre-commit hook (version guard + ruff lint + emoji scan), created check_emoji_files.py for targeted file scanning, created setup-hooks.sh installer, and updated docs (QUICKSTART, README, CLAUDE.md, LESSONS).
- **Deliverables**: Modified requirements.txt, .github/workflows/ci.yml, scripts/QUICKSTART.md, README.md, CLAUDE.md, LESSONS.md. New files: scripts/check_emoji_files.py, scripts/git-hooks/pre-commit, scripts/setup-hooks.sh.
- **Sanity check result**: ruff clean, emoji scan clean, 11/11 pytest pass, setup-hooks.sh installs successfully, version extraction tested.
- **Status**: [DONE]
- **Request**: No change

## 2026-03-12 -- Emoji Guard False Positives + TASKS.md Sync + Stop Hook Resilience
- **What I did**: Removed BMP ranges (U+2600-U+26FF, U+2700-U+27BF) from emoji regex in lint_check.py and check_emoji_files.py to eliminate 81 false positives on symbols like BLACK STAR. Added code-vs-doc distinction in stop hook so doc file emoji warns but doesn't block. Added TASKS.md auto-staging in task_db.py, pre-commit consistency check, .claude/tasks.db to .gitignore, and fresh-clone DB-missing warning in session_context.py. Extracted _get_completed_task_ids as public function and created missing task_dedup_check.py module to fix pre-existing test import errors.
- **Deliverables**: Modified .claude/hooks/lint_check.py, scripts/check_emoji_files.py, .claude/hooks/task_db.py, scripts/git-hooks/pre-commit, .claude/hooks/session_context.py, .gitignore. New files: tests/test_emoji_regex.py, .claude/hooks/task_dedup_check.py.
- **Sanity check result**: ruff clean, stop hook exits 0 (doc emoji warned not blocked), 80/80 tests pass (20 pre-existing router failures excluded), 7 emoji regex regression tests pass.
- **Status**: [DONE]
- **Request**: No change

## 2026-03-12 -- [T-P0-1] Pin all dependencies to exact versions
- **What I did**: Pinned all dependencies in requirements.txt to exact versions (fastapi==0.109.0, uvicorn==0.41.0, sqlalchemy==2.0.25, anthropic==0.84.0, pydantic-settings==2.13.1, httpx==0.27.2, beautifulsoup4==4.12.2, playwright==1.58.0, ruff==0.15.4, pytest==7.4.4). Updated pyproject.toml optional-deps (dev: pytest, httpx, ruff; scraper: playwright, beautifulsoup4) with exact pins.
- **Deliverables**: Modified requirements.txt, pyproject.toml
- **Sanity check result**: pip install succeeds, all imports work, ruff clean, 17/17 tests pass
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-1 --status completed`

## 2026-03-12 -- [T-P0-2] Config module with pydantic-settings
- **What I did**: Verified existing config.py (Settings class with DATABASE_URL, ANTHROPIC_API_KEY, LLM_MODEL, CORS_ORIGINS, DEBUG, env_file_encoding=utf-8). Added CORS_ORIGINS to .env.example. Expanded tests from 2 to 5: added defaults validation, get_settings() test, CORS_ORIGINS from env test.
- **Deliverables**: Modified .env.example, tests/test_config.py
- **Sanity check result**: 5/5 config tests pass, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-2 --status completed`

## 2026-03-12 -- [T-P0-3] Database engine + session setup
- **What I did**: Verified existing database.py (Base, get_engine with URL override, SessionLocal, get_db generator, init_db with data dir creation, check_same_thread=False for SQLite). Expanded tests from 2 to 8: added get_engine override, check_same_thread, default URL, data dir creation, generator lifecycle, SessionLocal binding tests.
- **Deliverables**: Modified tests/test_database.py (2 -> 8 tests)
- **Sanity check result**: 8/8 database tests pass, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-3 --status completed`
