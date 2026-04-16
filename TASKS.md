# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

### P1 -- Should Have (agentic intelligence)

#### T-P1-468: [QIdx-B5] LC 362 Design Hit Counter: expand notes
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Expand thin notes for LC 362 Design Hit Counter to full solution + mark completed.

CURRENT STATE: leetcode_id=362, family='stateful_ds_design', is_completed=0, LENGTH(notes)=956 (too thin).

PROBLEM RECAP: HitCounter with hit(timestamp) and getHits(timestamp) returning hits in past 300 seconds (sliding 5-minute window).

SOLUTIONS TO COVER:
- Solution A: queue of timestamps. hit: append. getHits: popleft while front < timestamp - 300; return len(queue). O(1) amortized hit; O(k) getHits where k = expired entries.
- Solution B: circular buffer size 300, bucket[(ts % 300)] = (ts, count). hit: if bucket.ts == ts increment else reset (ts, 1). getHits: sum bucket.count for each of 300 buckets where ts > timestamp - 300. O(1) hit, O(300) = O(1) getHits.
- B vs A: B is O(1) per op but fixed 300 memory; A is O(calls in window) memory and O(k) getHits which can burst. Production systems use B.

IMPLEMENTATION:
- scripts/_update_lc362_notes.py (REPLACE existing thin notes, do not append; use sentinel '<!-- LC362_NOTES_V2 -->' to detect re-run).
- StudyNoteBuilder + Chinese + idempotent.

NOTES COVER (Chinese):
1. 题目定位: stateful_ds_design, 滑动时间窗计数 canonical 问题.
2. 两解法对比表 (内存 / 时间 / 爆发容忍 / 是否支持任意窗口大小).
3. 解法 A 代码 + 走查; 解法 B 代码 + 为什么 bucket=300 固定 (题目给定 window).
4. 复杂度分析 + 为什么 B 的 O(300) 算 O(1).
5. Follow-up:
   (a) 并发 hit 安全 -> bucket 上加 CAS 或 shard 按 ts 哈希;
   (b) 任意窗口大小 window_sec -> bucket 数 = window_sec, getHits 遍历全部桶;
   (c) 超高 QPS 下 bucket 溢出 -> 按秒的 count 用 atomic int64;
   (d) 分布式 -> Redis sliding-window-log (zset + remove-score-range).
6. 45 秒 pitch.

AC:
1. UPDATE notes (REPLACE, not append), is_completed=1, for lcid=362.
2. LENGTH(notes) >= 2500.
3. Re-run prints [UNCHANGED].
4. Commit: [T-P1-468] LC 362 Design Hit Counter: expand to full A/B comparison + follow-ups.

### P2 -- Nice to Have

#### T-P2-469: [QIdx-C1] Harden LC import scripts to set family
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: Harden LC import scripts so new rows no longer default to family=NULL silently.

BACKGROUND: Current pipeline adds LC problems via import_staging_lc.py and multiple seed_*lc*.py scripts. None set family; result is 1026 LC problems with family=NULL in DB. This task prevents the rot from growing.

IMPLEMENTATION: Pick a low-intrusion path:
- Locate all LC-insert call sites: grep -r -l "INSERT INTO problems" scripts/ and inspect each.
- Typical files (verify before editing): scripts/import_staging_lc.py, scripts/seed_pinterest_lc_problems.py, scripts/_seed_*.py that touch problems.
- At each INSERT: if family is not provided or is NULL/empty, log the row to logs/lc_family_quarantine.tsv (append-only tsv: timestamp\tlc_id\ttitle\tsource_script). Print WARN to stderr: [WARN] LC {id} inserted without family; logged to quarantine.
- DO NOT fail the insert -- non-blocking warn-and-log.
- Add a new helper module scripts/_lc_import_helpers.py with one function: warn_if_missing_family(lc_id, title, family, source_script). Each import script imports and calls this before/after the INSERT.

ACCEPTANCE CRITERIA:
1. scripts/_lc_import_helpers.py exists with warn_if_missing_family.
2. At least 2 existing import call sites patched to use it.
3. Demo: running any patched importer with a row that has no family produces a WARN line and appends a row to logs/lc_family_quarantine.tsv.
4. Rows WITH family do not produce warnings or quarantine entries.
5. Existing smoke tests (if any for these importers) still pass.
6. Commit: [T-P2-469] Harden LC import scripts: warn + quarantine rows missing family

NON-GOALS: No DB schema change. No retroactive fix for the 1026 existing NULL-family rows (covered separately if needed). No hard validation failure on insert (non-blocking warn only).

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

#### T-P1-238: [SYNC] Fix helixos: replace bare python with absolute path in settings.json hooks
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: helixos/.claude/settings.json uses bare `python` for all hook commands (plan_mode_hook, block_dangerous, commit_msg_guard, secret_guard, tasks_md_guard, file_watch_warn, yaml_validate, lint_check, test_check, archive_check, session_context). Per CLAUDE.md Prohibited Actions: bare python resolves to Windows Store stub (exit code 49) and hooks silently fail. Fix: replace all `python "$CLAUDE_PROJECT_DIR/..."` with `/c/Anaconda/python.exe "$CLAUDE_PROJECT_DIR/..."`. Source: MLInterviewPrep settings.json (already fixed). Also add setup_python_env.sh as first SessionStart hook (bash "$CLAUDE_PROJECT_DIR/.claude/hooks/setup_python_env.sh") -- MLInterviewPrep has this, helixos does not. Copy setup_python_env.sh from MLInterviewPrep if not present.

#### T-P1-254: [SYNC] helixos: Fix bare python in settings.json + add setup_python_env.sh
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: CRITICAL: helixos settings.json uses bare python for ALL hook commands. On Windows, bare python resolves to the AppData Store stub (exit code 49), silently breaking all hooks. Fix: (1) Replace all bare python with /c/Anaconda/python.exe in settings.json. (2) Add setup_python_env.sh SessionStart hook (copy from MLInterviewPrep) to inject Anaconda into PATH for Bash tool calls via CLAUDE_ENV_FILE. CLAUDE.md already documents this prohibition (added 2026-03-21 via propagation) but the fix was never applied. This is the same root cause as MLInterviewPrep lesson [2026-03-20] #bash-tool #path.

#### T-P1-319: [SYNC] helixos: Fix bare python in settings.json hooks (critical)
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: ALL hook commands in helixos settings.json use bare python instead of /c/Anaconda/python.exe. This causes exit code 49 on Windows Store stub. Also missing setup_python_env.sh in SessionStart. Actions: (1) Replace python with /c/Anaconda/python.exe in every hook command. (2) Add setup_python_env.sh as first SessionStart hook copied from MLInterviewPrep. Source: MLInterviewPrep settings.json, LESSONS.md 2026-03-20.

#### T-P2-187: [SYNC] Add setup_python_env.sh + absolute Python path to helixos and template
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: MLInterviewPrep has: (1) setup_python_env.sh SessionStart hook that writes Anaconda to CLAUDE_ENV_FILE, (2) /c/Anaconda/python.exe absolute paths in all settings.json hook commands. helixos and claude-code-project-template both use bare python in settings.json and have no setup_python_env.sh. Per LESSONS.md: Bash tool runs non-login shells, .bashrc not sourced, bare python resolves to Windows Store stub. Source: MLInterviewPrep/.claude/hooks/setup_python_env.sh and settings.json. Action: copy setup_python_env.sh to helixos and template, update settings.json hook commands to use absolute path.

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

#### T-P2-239: [SYNC] Propagate session_context.py improvements from MLInterviewPrep to helixos
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: MLInterviewPrep session_context.py has two improvements over helixos version: (1) Extracted _get_completed_task_ids() as a named helper function instead of inline code. (2) Added fresh-clone DB missing warning: if .claude/tasks.db is missing but TASKS.md has tasks, warn user to run `python .claude/hooks/task_db.py import`. Apply both changes to helixos/.claude/hooks/session_context.py.

#### T-P2-255: [DEBT] helixos: Remove deprecated stop cache usage from test_check.py
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: test_check.py imports check_stop_cache and write_stop_cache from hook_utils and uses them to skip re-running tests in the same session. These deprecated caching functions were removed from the hook architecture (LESSONS.md lesson [2026-03-18]: removed lint cache so every Stop hook runs fresh). The caching logic means test failures can be silently skipped if tests passed earlier in the same session. Fix: Remove the cache check/write calls from test_check.py so tests always run fresh on Stop. Keep check_stop_cache/write_stop_cache in hook_utils.py only if other hooks still use them.

#### T-P2-320: [SYNC] helixos: Remove deprecated stop-cache from test_check.py
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: helixos test_check.py still uses check_stop_cache/write_stop_cache which were deprecated per LESSONS.md 2026-03-18. Cache can produce false passes when files change between cache write and next session. MLInterviewPrep already removed this. Action: Remove cache imports and calls from test_check.py; clean up hook_utils.py if no other callers.

## Completed Tasks

> 430 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-04-16** -- T-P2-460: [Pinterest-SD] Responsible AI / Inclusive AI + model monitoring & retraining playbook. Gap: Pinterest brands on 'Inclusive AI' (skin-tone-fair visual search case study) but no prep doc covers it. Bundle with
- [x] **2026-04-16** -- T-P2-459: [Pinterest-SD] Multimodal unsafe content detection + query expansion recall boost. Gap: two known Pinterest SD interview prompts -- neither has a dedicated doc. (1) Unsafe content (image+text multimodal)
- [x] **2026-04-16** -- T-P2-458: [Pinterest-Gen] GAN / VAE / Diffusion contrast one-pager + Pinterest use cases. Gap: no generative-model contrast at pitch level. Pinterest angle (visual content): pin generation, style transfer for b
- [x] **2026-04-16** -- T-P2-439: [DEBT] MLInterviewPrep: requirements.txt has scraper deps in wrong section. beautifulsoup4==4.12.2 and playwright==1.58.0 are in [project.optional-dependencies].scraper in pyproject.toml but appea
- [x] **2026-04-16** -- T-P2-438: [DEBT] MLInterviewPrep: httpx duplicated in pyproject.toml main + dev groups. pyproject.toml lists httpx==0.27.2 in both [project].dependencies (main) and [project.optional-dependencies].dev. This i
- [x] **2026-04-16** -- T-P1-467: [QIdx-B4] LC 1845 Seat Reservation Manager: Chinese solution notes. Write Chinese solution notes for LC 1845 Seat Reservation Manager and mark completed.
- [x] **2026-04-16** -- T-P1-466: [QIdx-B3] LC 1825 Finding MK Average: Chinese solution notes. Write Chinese solution notes for LC 1825 Finding MK Average and mark completed.
- [x] **2026-04-16** -- T-P1-465: [QIdx-B2] LC 1146 Snapshot Array: Chinese solution notes. Write Chinese solution notes for LC 1146 Snapshot Array and mark completed.
- [x] **2026-04-16** -- T-P1-464: [QIdx-B1] LC 895 Maximum Frequency Stack: Chinese solution notes. Write Chinese solution notes for LC 895 Maximum Frequency Stack and mark completed.
