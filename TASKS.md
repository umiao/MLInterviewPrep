# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

### P1 -- Should Have (agentic intelligence)

### P2 -- Nice to Have

#### T-P2-437: [SYNC] Propagate 4 new MLInterviewPrep lessons to helixos LESSONS.md
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: 4 lessons from MLInterviewPrep (2026-04-10 to 2026-04-15) not yet in helixos LESSONS.md. All apply to helixos. (1) 2026-04-10: Validation must happen on a surface isomorphic to the production path (#validation #production-path #consumer-verification). (2) 2026-04-13: react-markdown v10 urlTransform strips custom schemes (#react-markdown #custom-scheme -- helixos uses react-markdown). (3) 2026-04-13: Orchestrator all_done flag is sticky -- new batch launches silently bail if session_state.json has all_done:true (#autonomous #orchestration #sticky-flag). (4) 2026-04-15: Auto-bolding inside LaTeX/code leaks ** into rendered output -- regex substitutions must skip math/code spans (#markdown #latex #regex-scoping). Source: MLInterviewPrep/LESSONS.md entries dated 2026-04-10 through 2026-04-15.

#### T-P2-438: [DEBT] MLInterviewPrep: httpx duplicated in pyproject.toml main + dev groups
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: pyproject.toml lists httpx==0.27.2 in both [project].dependencies (main) and [project.optional-dependencies].dev. This is a silent duplicate: installing with [dev] extras adds httpx twice, potentially causing version conflicts in future. Fix: remove from dev group since it is already a main dependency.

#### T-P2-439: [DEBT] MLInterviewPrep: requirements.txt has scraper deps in wrong section
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: beautifulsoup4==4.12.2 and playwright==1.58.0 are in [project.optional-dependencies].scraper in pyproject.toml but appear in the main (non-optional) section of requirements.txt. This means pip install -r requirements.txt always installs scraper deps even in non-scraper environments. Fix: move both to a [scraper] comment group in requirements.txt or add a requirements-scraper.txt. Note: pyproject.toml is canonical spec per CLAUDE.md.

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

> 398 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-04-16** -- T-P1-423: [Google/R1] Train-serve skew/leakage/时序 split 拷打. AC: (1) target encoding K-fold leakage + fold-out 修正; (2) 为什么 ranking 必须 time-based split; (3) feature store parity 三种 s
- [x] **2026-04-16** -- T-P1-422: [Google/R1] Feature drift 监控: PSI/KL/JS 区别 + alert threshold. AC: (1) PSI=Σ(a-e)·ln(a/e), 0.1 warn/0.25 critical; (2) KL 不对称无界, JS 对称 bounded; (3) 连续用 KS; (4) concept drift P(y|x) vs
- [x] **2026-04-16** -- T-P1-421: [Google/R1] A/B test 严谨性: sample size/SRM/CUPED/novelty. pillar7 有基础但缺 drill. AC: (1) n=(z+z)^2·2σ²/Δ²; (2) SRM 是 randomization 健康性不是结果; (3) CUPED 用 pre-period covariate 降 varia
- [x] **2026-04-15** -- T-P1-444: Problems tab: Custom-mode company-grouped view. # Problems tab: Custom-mode company-grouped view (T-ML-xxx)
- [x] **2026-04-15** -- T-P1-443: Problems tab: Custom badge + source-type filter switch. # Problems tab: Custom badge + source-type filter (T-ML-xxx)
- [x] **2026-04-15** -- T-P1-442: Pinterest card index: integrate tab=index into PrepNotesPage. # Pinterest Card Index: Integrate tab=index into PrepNotesPage (T-P1-226)
- [x] **2026-04-15** -- T-P1-441: Pinterest card index: frontend CardGrid component. # Pinterest Card Index: Frontend CardGrid Component (T-P1-225)
- [x] **2026-04-15** -- T-P1-440: Pinterest card index: backend + data prep. # Pinterest Card Index: Backend + Data Prep (T-P1-224)
- [x] **2026-04-15** -- T-P0-424: [Slack-SFDC] HR call Wed 2026-04-15 14:00 EST = 11:00 PT. Slack (Salesforce) ML team recruiter call. 时间: 04/15 Wed 14:00 EST = 13:00 CST = 11:00 PT. 30-45 min 预期. 准备: (1) 自我介绍 90
- [x] **2026-04-15** -- T-P0-420: [Google/R1] Multi-objective ranking: DPP/MMR + Etsy diversity 故事机制. Etsy diversity 必被追问机制. AC: (1) MMR = λ·rel-(1-λ)·max_sim; (2) DPP 用 det(L_S) 同时 model rel(对角) + diversity(非对角); (3) inte
- [x] **2026-04-15** -- T-P0-419: [Google/R1] Two-tower retrieval 深挖 (超越 InfoNCE 基础). staging 11 覆盖 InfoNCE 但缺系统级. AC: (1) 为什么两塔 (query 塔不看 doc 侧 → offline index); (2) negative sampling 四种 + failure mode; (
- [x] **2026-04-15** -- T-P0-418: [Google/R1] IPS/counterfactual eval/去偏 NDCG (SIGIR paper talking points). Gap: staging 无. SIGIR paper 必问. AC: (1) IPS 重加权 1/P(shown); (2) examination hypothesis P(click)=P(exam)·P(rel); (3) SNIP
- [x] **2026-04-15** -- T-P0-417: [Google/R1] Calibration 三法 (Platt/Isotonic/Temperature) + GMB bidding 校准陷阱. Gap: staging 没提. Round1 recruiter 明列. AC: (1) Platt=logistic over logit; (2) Isotonic preserve ranking 粒度粗; (3) Temperat
- [x] **2026-04-15** -- T-P0-416: [Google/R1] NDCG/MAP/MRR 定义 + position bias 拷打自测. Gap: staging 只讲 ROC/PR. AC: (1) 默写 DCG=Σ(2^rel-1)/log2(i+1), NDCG=DCG/IDCG; (2) 为什么 MAP 不适合 graded relevance; (3) positi
- [x] **2026-04-15** -- T-P0-415: [Google/R1] LambdaRank/LambdaMART 推导 + pointwise/pairwise/listwise 对比自测. Gap vs staging 13: staging 无 ranking loss 推导. Round1 必考. AC: (1) 默写 RankNet pairwise sigmoid loss; (2) LambdaRank 如何用 de
