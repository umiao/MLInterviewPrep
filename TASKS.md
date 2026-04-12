# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

### P1 -- Should Have (agentic intelligence)

### P2 -- Nice to Have

#### T-P2-364: Behavioral failure cluster: structural polish (tags + narration guards) for EX-15/16/17/30
- **Priority**: P2
- **Complexity**: M
- **Depends on**: T-P1-358
- **Description**: STRUCTURAL/MECHANICAL polish ONLY for the 4 remaining failure-cluster master stories. Brings them in line with the EX-33B presentation standard WITHOUT inventing new factual content, so an autonomous session can run this end-to-end with no human fact-check.

FORBIDDEN in this task (deferred to a separate collaborative pass with the user):
- Inventing new evidence_quotes
- Inventing new analogies
- Rewriting Action / Result narrative
- Changing any factual claims (numbers, names, dates, project descriptions)

PERMITTED in this task:
- Adding entries to principle_tags (read-modify-write JSON, no removals)
- Appending a NARRATION-RISK GUARD paragraph to risk_statement (using the templates below — copy verbatim, do NOT rewrite)
- Appending a TEMPORAL POV PRINCIPLE paragraph to risk_statement, EX-16 only

DELIVERABLE: a single idempotent script scripts/_polish_failure_cluster_structural.py modeled after scripts/_patch_ex33b_kpi.py. Each edit gated on a marker string ("NARRATION-RISK GUARD" / "TEMPORAL POV") so re-running does not duplicate.

PER-STORY EXACT EDITS:

================================================================================
EX-15 (Model Deprecation Incident)
================================================================================

principle_tags: ensure JSON list contains the strings 'failure', 'humility', 'process_improvement_from_incident'. Use a read-modify-write pattern: load json, add missing, dump. Do NOT remove existing tags.

risk_statement: idempotent-append (gate on the sentinel string '<!-- NRG-v1 -->' — if already present in risk_statement, skip. Use a specific sentinel rather than a substring of the human-readable header to avoid false-positive idempotency skips if the phrase 'NARRATION-RISK GUARD' appears in any future content):

\n\n<!-- NRG-v1 --> NARRATION-RISK GUARD: This is a 'failure that became a process improvement' story. The risk in narration is that the cross-team-alignment-mechanism tail makes the failure itself feel small. STOP the story at the lesson ('I learned to surface informal stakeholder relationships before deprecating shared infrastructure'); only mention the cross-team mechanism if the interviewer asks 'what changed afterwards'.

================================================================================
EX-16 (Cross-Datacenter Deployment Incident)
================================================================================

principle_tags: ensure JSON list contains 'failure', 'humility', 'cross_boundary_failure'. Read-modify-write.

risk_statement: idempotent-append (gate on the sentinel string '<!-- TPV-v1 -->' — if already present in risk_statement, skip. Use a specific sentinel rather than a substring of the human-readable header to avoid false positives):

\n\n<!-- NRG-v1 --> <!-- TPV-v1 --> NARRATION-RISK GUARD + TEMPORAL POV: This story has a redemption tail (the declarative artifactory invitation) that risks the disguised-success trap. For pure-failure / mistake / 'what would you do differently' questions, STOP the story at the rollback and the new cross-team-reviewer policy. The artifactory invitation belongs to a separate framing of the same incident (a calculated-risk / paradigm-shift cut) and must NOT be appended to the failure narration. At the moment of the incident, before the artifactory invitation existed, this WAS a failure full stop — and that is the only POV the interviewer should hear when they asked a failure question.

================================================================================
EX-17 (Difficult Feedback from Senior IC)
================================================================================

principle_tags: ensure JSON list contains 'failure', 'humility'. Read-modify-write.

risk_statement: idempotent-append (gate on the marker substring 'NARRATION-RISK GUARD'):

\n\n<!-- NRG-v1 --> NARRATION-RISK GUARD: The temptation in this story is to lean on 'I built credibility back', which sounds like a redemption arc. The actual lesson is that I failed to push back on the manager-driven shortcut under pressure. Frame the lesson as 'I learned to gate-keep my own work even when my manager is the one cutting the corner', and let the credibility recovery be IMPLIED, not narrated.

================================================================================
EX-30 (Hash Capability Misdesign)
================================================================================

This is the gold-standard reference. Verify-only:
- principle_tags MUST already contain 'failure'. If absent, add it (do not remove anything).
- risk_statement MUST already contain a narration-risk note ('Use this story for failure-type questions; it does not have a success-tail to soften it.'). If the marker 'NARRATION-RISK GUARD' is also missing, append a one-line redirect to make grep-by-marker uniform across all 4 stories:
  \n\n<!-- NRG-v1 --> NARRATION-RISK GUARD: See existing 'Use this story for failure-type questions...' clause above. This story is the cluster's gold standard and needs no additional guard.

================================================================================
VERIFICATION (script must run after the patches and exit non-zero if any check fails):

For each of EX-15, EX-16, EX-17, EX-30:
  - SELECT principle_tags FROM behavioral_examples WHERE example_id=...
  - assert 'failure' in json.loads(principle_tags)
  - SELECT risk_statement FROM behavioral_examples WHERE example_id=...
  - assert '<!-- NRG-v1 -->' in risk_statement  # sentinel, not human-readable header
For EX-16 specifically:
  - assert '<!-- TPV-v1 -->' in risk_statement  # sentinel, not human-readable header

After DB-level checks pass, verify via the API consumer path:
  - curl -s http://localhost:8100/api/behavioral/examples/by-example-id/EX-15 | python -c 'import json,sys; d=json.load(sys.stdin); assert "failure" in d["principle_tags"]; assert '<!-- NRG-v1 -->' in d['risk_statement']'
  - Repeat for EX-16, EX-17, EX-30.

(Restart uvicorn first if T-P1-359 was not yet applied in this session.)

================================================================================
ACCEPTANCE:
- All 4 stories have 'failure' principle_tag.
- All 4 stories have the sentinel '<!-- NRG-v1 -->' in risk_statement (specific sentinel chosen to avoid false-positive idempotency skips on future content containing the human-readable phrase).
- EX-16 specifically also has the sentinel '<!-- TPV-v1 -->' in risk_statement.
- No new evidence_quotes / analogies / STAR-text rewrites were committed.
- Re-running scripts/_polish_failure_cluster_structural.py is idempotent (no duplicated paragraphs, exits cleanly).
- Commit message: '[T-P2-364] Failure cluster structural polish: tags + narration guards'.

DOES NOT cover (deferred to a separate user-collaborative task — to be filed only if the user asks for it):
- Adding new evidence_quotes to EX-15, EX-16, EX-17
- Adding analogies
- Rewriting Action sections to add realization beats
- Adding cn_elevator_pitch refinements (handled by T-P1-358)

#### T-P2-365: Behavioral audit: verify all technical_problem_solving examples have explicit data-driven evidence
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: Audit pass over the example_theme_tags rows for theme_id=technical_problem_solving (currently 27 examples). For each, read the example record and verify it contains BOTH (a) a quantitative number in the Result section (e.g., '+1% GMB', '200M+', 'p99 latency dropped 30%') AND (b) a metric name and direction-of-change in the Action section. (a)+(b) together is the bar for a real data-driven story; either one alone is too easy to satisfy with hand-waving (per code-review tightening). (c) an A/B test reference and (d) a data-derived hypothesis are STRONG SUPPORTING evidence — if an example has (c) or (d) plus only one of (a)/(b), it can be marked NEEDS-NOTE rather than RECOMMEND-UNTAG. If an example has neither (a) nor (b), the technical depth narrative is unsupported -- either (i) the relevance_note on the technical_problem_solving theme tag must explain why this story still belongs to tech depth without numbers, OR (ii) untag from technical_problem_solving and document the untag reason. Generate a markdown audit report at docs/audits/tech_depth_data_driven_2026-04.md listing each of the 27 examples with PASS / NEEDS-NOTE / RECOMMEND-UNTAG verdicts. Do NOT auto-untag in this task -- collect findings for human review. AC: report file exists, all 27 examples accounted for, summary counts at the top.

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

> 318 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-04-11** -- T-P2-363: BQ navigation: end-to-end browse-path preservation across QuickIndex/theme/drawer. Audit and fix end-to-end navigation paths so user never loses browse context across QuickIndex(BQ) -> theme detail -> ex
- [x] **2026-04-11** -- T-P2-356: Behavioral: semantic relevance spot-check script for 10 random Q-example links. # Behavioral: semantic relevance spot-check script for 10 random Q-example links
- [x] **2026-04-11** -- T-P2-324: [DEBT] helixos: Sync dev deps from requirements.txt to pyproject.toml. 6 packages in requirements.txt not in pyproject.toml: httpx, ruff, pytest-asyncio, mypy, pytest, pytest-timeout. Add as 
- [x] **2026-04-11** -- T-P2-323: [DEBT] MLInterviewPrep: Sync dev deps from requirements.txt to pyproject.toml. 6 packages in requirements.txt not in pyproject.toml: pytest, pytest-asyncio, beautifulsoup4, pyyaml, ruff, playwright. 
- [x] **2026-04-11** -- T-P2-322: [DEBT] MLInterviewPrep: Add problems.db to .gitignore. problems.db is untracked in MLInterviewPrep git repo and not in .gitignore. The .gitignore already covers interview_prep
- [x] **2026-04-11** -- T-P2-321: [SYNC] helixos: Propagate 3 new lessons from MLInterviewPrep 2026-04-08. Three new MLInterviewPrep LESSONS.md entries not yet in helixos: (1) autonomous_run.sh uses sub-project task_db not root
- [x] **2026-04-11** -- T-P1-362: BQ theme detail page: example cards with Chinese pitch + STAR drawer. New page at route /behavioral/theme/:slug for the BQ theme detail view. Add the route in src/frontend/src/App.tsx and cr
- [x] **2026-04-11** -- T-P1-361: QuickIndex BQ section: render theme cards grouped by cluster. Inside the BQ section of QuickIndex (placeholder added by T-P1-360), render the 15 behavioral_themes as cards grouped by
- [x] **2026-04-11** -- T-P1-360: QuickIndex: add section toggle bar (LC / ML coding / BQ). Restructure src/frontend/src/pages/QuickIndex.tsx — add a top toggle bar so the user can show ONE of three sections at a
- [x] **2026-04-11** -- T-P1-359: Behavioral API: fix /questions and /examples theme filter (returns all instead of filtered). Fix /api/behavioral/questions and /api/behavioral/examples theme filter.
- [x] **2026-04-11** -- T-P1-358: Behavioral: add cn_elevator_pitch column + seed 7 master story pitches. Add behavioral_examples.cn_elevator_pitch column + populate for the 7 polished master stories: EX-15, EX-16, EX-17, EX-3
- [x] **2026-04-11** -- T-P1-357: Behavioral: populate EX-30 with Hash Misdesign + create EX-33 for MoE->Allocation. # Behavioral: populate EX-30 with Hash Misdesign + create EX-33 for MoE->Allocation paradigm shift
- [x] **2026-04-11** -- T-P1-355: Frontend: DrawerLayout single-source-of-truth responsive two-column refactor for drawer family. # Frontend: DrawerLayout single-source-of-truth responsive two-column refactor
- [x] **2026-04-11** -- T-P1-354: Behavioral: theme pills on question rows + frequency-sorted filter sidebar on BehavioralQuestions page. # Behavioral: theme pills + frequency-sorted filter sidebar on BehavioralQuestions page
- [x] **2026-04-11** -- T-P1-353: Behavioral: seed 15-theme vocabulary, tag tables, and keyword backfill on Qs and examples. # Behavioral: 15-theme vocabulary, tag tables, keyword backfill
- [x] **2026-04-11** -- T-P1-352: Behavioral: add secondary example links for single-link Qs in communication/collaboration/leadership. # Behavioral: secondary links for single-link Qs in communication/collaboration/leadership
- [x] **2026-04-11** -- T-P0-351: Behavioral: seed 3 failure-story placeholders EX-30/31/32 [NEEDS-INPUT: 3 failure stories]. # Behavioral: seed 3 failure-story placeholders EX-30/31/32
- [x] **2026-04-10** -- T-P3-349: Add node_content and node_translations artifacts from Chinese batch. Commit the per-node markdown artifacts generated during the pillar 3/6 Chinese conversion batch (T-P1-120..T-P1-130) for
- [x] **2026-04-10** -- T-P3-348: Lint: apply ruff auto-fixes to seed/translate/fix scripts. Apply ruff auto-fixes to scripts: import reordering, removal of unused imports, f-string cleanup (no placeholders).
- [x] **2026-04-10** -- T-P2-347: Pillar 3/6 translation and expansion scripts. Add translation + expansion scripts for the pillar 3/6 Chinese conversion batch (T-P1-120..T-P1-130). Scripts generate/u
- [x] **2026-04-10** -- T-P2-346: Seed LinkedIn/Google/Pinterest prep content. Add seed scripts for LinkedIn question index, LinkedIn problem notes insertion, Google prep content, Pinterest prep cont
