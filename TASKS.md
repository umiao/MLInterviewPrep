# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

### P1 -- Should Have (agentic intelligence)

### P2 -- Nice to Have

#### T-P2-185: [SYNC] helixos CLAUDE.md: Add no-bare-python rule to Prohibited Actions
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: MLInterviewPrep CLAUDE.md Prohibited Actions has this rule (lines 62-66):

  Never use bare `python` in hook commands or scripts. The Windows Store stub exits with code 49. Use `/c/Anaconda/python.exe` (absolute path) in settings.json hooks. The SessionStart hook setup_python_env.sh injects Anaconda into PATH for Bash tool calls via CLAUDE_ENV_FILE.

helixos CLAUDE.md has the lesson in LESSONS.md (line 266) but not in Prohibited Actions. Add the rule to the Prohibited Actions section to prevent recurrence.

Should be done AFTER [SYNC] helixos: Fix broken hooks task.

#### T-P2-186: [SYNC] Propagate ruff version-drift lesson to helixos
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: MLInterviewPrep LESSONS.md has [2026-03-02] lesson about ruff version drift between local and CI (loose pin + separate install = silent drift). Tags: #ruff #ci #version-drift. Not yet in helixos LESSONS.md. Action: append the lesson to helixos/LESSONS.md with [PROPAGATED] tag.

#### T-P2-187: [SYNC] Add setup_python_env.sh + absolute Python path to helixos and template
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: MLInterviewPrep has: (1) setup_python_env.sh SessionStart hook that writes Anaconda to CLAUDE_ENV_FILE, (2) /c/Anaconda/python.exe absolute paths in all settings.json hook commands. helixos and claude-code-project-template both use bare python in settings.json and have no setup_python_env.sh. Per LESSONS.md: Bash tool runs non-login shells, .bashrc not sourced, bare python resolves to Windows Store stub. Source: MLInterviewPrep/.claude/hooks/setup_python_env.sh and settings.json. Action: copy setup_python_env.sh to helixos and template, update settings.json hook commands to use absolute path.

#### T-P2-206: [SYNC] Propagate 2 universal lessons to helixos LESSONS.md
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: helixos/LESSONS.md is missing 2 universal lessons already in the template:
1. [2026-03-02] Ruff version drift between local and CI (#ruff #ci) -- loose ruff pin causes CI-only failures; fix: pin ruff==X.Y.Z in requirements.txt.
2. [2026-03-11] Task ID P = Phase anti-pattern went undetected (#task-naming #convention-drift) -- P should always mean priority, never phase/stage.

Action: Append both entries (verbatim from template LESSONS.md) to helixos/LESSONS.md. Source: claude-code-project-template/LESSONS.md.

#### T-P2-207: [SYNC] Remove deprecated stop-cache from helixos test_check.py
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: helixos/.claude/hooks/test_check.py still imports and uses check_stop_cache/write_stop_cache from hook_utils. MLInterviewPrep already removed the cache in T-P2-188 (commit abf6543), per the lesson that stop caches can produce false passes when files change between sessions.

Action: Update helixos/.claude/hooks/test_check.py to match MLInterviewPrep version -- remove check_stop_cache/write_stop_cache import and usage. Run tests after to confirm hook still works.

Source: MLInterviewPrep/.claude/hooks/test_check.py (current, cache-free version).

#### T-P2-208: [SYNC] Remove deprecated stop-cache from template test_check.py
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: claude-code-project-template/.claude/hooks/test_check.py still uses check_stop_cache/write_stop_cache from hook_utils. The lesson [2026-03-18] established that stop caches cause false PASS results when files change between sessions. MLInterviewPrep already fixed this.

Action: Update template/.claude/hooks/test_check.py to match MLInterviewPrep version -- remove cache import and usage. The template is the reference baseline, so it should have the best-known version of all hooks.

Source: MLInterviewPrep/.claude/hooks/test_check.py.

#### T-P2-209: [SYNC] Propagate template session_context db-missing warning to MLInterviewPrep
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: claude-code-project-template/.claude/hooks/session_context.py (lines 475-486) has a db_missing_warning feature: if .claude/tasks.db is absent but TASKS.md has tasks, it warns the user to run task_db.py import. This is useful for fresh-clone scenarios.

MLInterviewPrep/.claude/hooks/session_context.py is missing this warning block.

Action: Port the db_missing_warning block from template to MLInterviewPrep session_context.py.

### P3 -- Stretch Goals

## Blocked

#### T-P1-184: [SYNC] helixos: Fix broken hooks -- use absolute Python path + add setup_python_env.sh
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: All hooks in helixos settings.json use bare python which resolves to the Windows Store stub (exit 49) on this machine. MLInterviewPrep already has the fix applied.

Actions needed:
1. Copy .claude/hooks/setup_python_env.sh from MLInterviewPrep to helixos (writes Anaconda to CLAUDE_ENV_FILE)
2. Update helixos .claude/settings.json: replace all python with /c/Anaconda/python.exe in ALL hook commands
3. Add SessionStart hook entry for setup_python_env.sh

BLOCKED: Claude Code file permissions block writes to helixos .claude/hooks/ directory from MLInterviewPrep session. Must be done from a helixos session or manually.

## Completed Tasks

> 207 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-03-27** -- T-P1-231: Fix PrepNotesPage tab overflow: document dropdown. Replace document tab buttons with dropdown select in PrepNotesPage.tsx. Design: Lines 156-175, replace documents?.map(Ta
- [x] **2026-03-27** -- T-P0-235: Day1 Expansion C: Answer all checklist questions. After expansions A+B are done, answer ALL 10 existing checklist questions plus any new ones added by A+B. Format: keep t
- [x] **2026-03-27** -- T-P0-234: Day1 Expansion B: VAE details + ControlNet deep-dive + industry landscape. Expand Day 1 note with 3 more sections: (1) VAE deep-dive: encoder/decoder architecture, latent space regularization (KL
- [x] **2026-03-27** -- T-P0-233: Day1 Expansion A: PE deep-dive + sinusoidal derivation + KV-Cache. Expand Day 1 note (doc id=18) with 3 new sections: (1) Positional Embedding deep-dive: absolute PE, sinusoidal PE deriva
- [x] **2026-03-27** -- T-P0-232: Add Builder convention to CLAUDE.md + update memory. After pilot validates Builder, codify the convention. (1) CLAUDE.md Prohibited Actions: add 'Never write study note cont
- [x] **2026-03-27** -- T-P0-230: Scale: Rewrite remaining 6 Adobe docs with validated Builder. After Day 1 pilot validates the Builder API, rewrite Days 2-7 (company_documents ids 6-11). For each doc: (1) Use StudyN
- [x] **2026-03-27** -- T-P0-229: Pilot: Rewrite Day 1 (Diffusion) end-to-end with Builder. END-TO-END PILOT to validate Builder API before scaling. Take Adobe Day 1 doc (company_documents id=5, Diffusion Models)
- [x] **2026-03-27** -- T-P0-228: Enable rehype-raw in MarkdownPreview. Install rehype-raw and add to MarkdownPreview. (1) npm install rehype-raw. (2) MarkdownPreview.tsx: import rehypeRaw, ad
- [x] **2026-03-27** -- T-P0-227: Minimal StudyNoteBuilder + FormulaBlock typed constraint. Minimal viable Builder with one typed block (FormulaBlock). Design: (1) FormulaBlock dataclass: latex:str, explanation:s
