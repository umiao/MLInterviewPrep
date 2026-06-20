# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

### P1 -- Should Have (agentic intelligence)

#### T-P1-821: [KG-INT B4-promotion] Consolidate flagged promotion candidates -> meta-prep updates
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-815, T-P1-816, T-P1-817, T-P1-818, T-P1-819, T-P1-820
- **Description**: Read §5 'Promotion candidates flagged for meta-prep' from each B4a archive plan in docs/archive_plans/. Deduplicate. For candidates passing the >=3 P0+P1 threshold (per promotion_criteria.md), author follow-up seed updates to meta-prep child nodes. AC: list of accepted vs rejected candidates committed; framework_nodes deltas applied via idempotent seed; updated archive plans get a §6 'promoted' section.

### P2 -- Nice to Have

#### T-P2-836: [KG-INT B6-cleanup] Final acceptance checklist + audit + savings stats
- **Priority**: P2
- **Complexity**: S
- **Depends on**: T-P1-821, T-P1-834
- **Description**: Final 4-item acceptance checklist (per Discord plan v3 §9): (a) all P0/P1 companies' prep_notes/notes byte counts < threshold anchored by A0 EDA; (b) meta-prep child nodes mean byte count > 800; (c) audit_uri_consistency.py reports 0 broken kg:// db:// cd:// sd://; (d) red-dot logic manual smoke on sample companies passes. Compute byte-savings stats (before vs after) + commit count + KG growth (node + link delta). PROGRESS close-out entry summarizes the 42-task batch. AC: all 4 checklist items pass; close-out entry written.

### P3 -- Stretch Goals

## Blocked

#### T-P0-822: [KG-INT B4b-google] Google execute: hard-archive + skeleton seed + acceptance proof
- **Priority**: P0
- **Complexity**: L
- **Depends on**: None
- **Description**: EXECUTE (after manual unblock following user [approved] on docs/archive_plans/B4a-google_2026-05-10.md). Steps: (1) generate archive/company_internalized/B4a-google_2026-05-10_restore.sql with INSERT statements for every row to be deleted, (2) write full prose dump to archive/company_internalized/B4a-google_2026-05-10.md, (3) move source seed scripts (scripts/seed_google_*.py / scripts/content_*google*.py / scripts/patch_google_*.py) -> archive/seed_scripts/B4a-google/, (4) DELETE rows per §4 plan, (5) author NEW seed scripts/seed_google_drawer_index.py for the thin skeleton doc and run it (Invariant 3 compliance), (6) run scripts/audit_uri_consistency.py and assert exit 0, (7) execute the §2 'verifiable queries' and capture output as PROGRESS acceptance proof. Idempotent (re-runs detect already-archived state and no-op). AC: all 7 steps pass; PROGRESS entry includes verifiable-query outputs; UI loads / company page without dangling refs.

#### T-P0-823: [KG-INT B4b-lyra] Lyra execute: hard-archive + skeleton seed + acceptance proof
- **Priority**: P0
- **Complexity**: M
- **Depends on**: T-P0-822
- **Description**: EXECUTE (after manual unblock following user [approved] on docs/archive_plans/B4a-lyra_2026-05-10.md). Steps: (1) generate archive/company_internalized/B4a-lyra_2026-05-10_restore.sql with INSERT statements for every row to be deleted, (2) write full prose dump to archive/company_internalized/B4a-lyra_2026-05-10.md, (3) move source seed scripts (scripts/seed_lyra_*.py / scripts/content_*lyra*.py / scripts/patch_lyra_*.py) -> archive/seed_scripts/B4a-lyra/, (4) DELETE rows per §4 plan, (5) author NEW seed scripts/seed_lyra_drawer_index.py for the thin skeleton doc and run it (Invariant 3 compliance), (6) run scripts/audit_uri_consistency.py and assert exit 0, (7) execute the §2 'verifiable queries' and capture output as PROGRESS acceptance proof. Idempotent (re-runs detect already-archived state and no-op). AC: all 7 steps pass; PROGRESS entry includes verifiable-query outputs; UI loads / company page without dangling refs.

#### T-P0-824: [KG-INT B4b-pinterest-toc] Pinterest-TOC execute: hard-archive + skeleton seed + acceptance proof
- **Priority**: P0
- **Complexity**: M
- **Depends on**: T-P0-823
- **Description**: EXECUTE (after manual unblock following user [approved] on docs/archive_plans/B4a-pinterest-toc_2026-05-10.md). Steps: (1) generate archive/company_internalized/B4a-pinterest-toc_2026-05-10_restore.sql with INSERT statements for every row to be deleted, (2) write full prose dump to archive/company_internalized/B4a-pinterest-toc_2026-05-10.md, (3) move source seed scripts (scripts/seed_pinterest_toc_*.py / scripts/content_*pinterest_toc*.py / scripts/patch_pinterest_toc_*.py) -> archive/seed_scripts/B4a-pinterest-toc/, (4) DELETE rows per §4 plan, (5) author NEW seed scripts/seed_pinterest_toc_drawer_index.py for the thin skeleton doc and run it (Invariant 3 compliance), (6) run scripts/audit_uri_consistency.py and assert exit 0, (7) execute the §2 'verifiable queries' and capture output as PROGRESS acceptance proof. Idempotent (re-runs detect already-archived state and no-op). AC: all 7 steps pass; PROGRESS entry includes verifiable-query outputs; UI loads / company page without dangling refs.

#### T-P0-825: [KG-INT B4b-pinterest-concepts] Pinterest-CONCEPTS execute: hard-archive + skeleton seed + acceptance proof
- **Priority**: P0
- **Complexity**: L
- **Depends on**: T-P0-824
- **Description**: EXECUTE (after manual unblock following user [approved] on docs/archive_plans/B4a-pinterest-concepts_2026-05-10.md). Steps: (1) generate archive/company_internalized/B4a-pinterest-concepts_2026-05-10_restore.sql with INSERT statements for every row to be deleted, (2) write full prose dump to archive/company_internalized/B4a-pinterest-concepts_2026-05-10.md, (3) move source seed scripts (scripts/seed_pinterest_concepts_*.py / scripts/content_*pinterest_concepts*.py / scripts/patch_pinterest_concepts_*.py) -> archive/seed_scripts/B4a-pinterest-concepts/, (4) DELETE rows per §4 plan, (5) author NEW seed scripts/seed_pinterest_concepts_drawer_index.py for the thin skeleton doc and run it (Invariant 3 compliance), (6) run scripts/audit_uri_consistency.py and assert exit 0, (7) execute the §2 'verifiable queries' and capture output as PROGRESS acceptance proof. Idempotent (re-runs detect already-archived state and no-op). AC: all 7 steps pass; PROGRESS entry includes verifiable-query outputs; UI loads / company page without dangling refs.

#### T-P0-826: [KG-INT B4b-pinterest-prep] Pinterest-prep execute: hard-archive + skeleton seed + acceptance proof
- **Priority**: P0
- **Complexity**: M
- **Depends on**: T-P0-825
- **Description**: EXECUTE (after manual unblock following user [approved] on docs/archive_plans/B4a-pinterest-prep_2026-05-10.md). Steps: (1) generate archive/company_internalized/B4a-pinterest-prep_2026-05-10_restore.sql with INSERT statements for every row to be deleted, (2) write full prose dump to archive/company_internalized/B4a-pinterest-prep_2026-05-10.md, (3) move source seed scripts (scripts/seed_pinterest_prep_*.py / scripts/content_*pinterest_prep*.py / scripts/patch_pinterest_prep_*.py) -> archive/seed_scripts/B4a-pinterest-prep/, (4) DELETE rows per §4 plan, (5) author NEW seed scripts/seed_pinterest_prep_drawer_index.py for the thin skeleton doc and run it (Invariant 3 compliance), (6) run scripts/audit_uri_consistency.py and assert exit 0, (7) execute the §2 'verifiable queries' and capture output as PROGRESS acceptance proof. Idempotent (re-runs detect already-archived state and no-op). AC: all 7 steps pass; PROGRESS entry includes verifiable-query outputs; UI loads / company page without dangling refs.

#### T-P0-827: [KG-INT B4b-uber] Uber execute: hard-archive + skeleton seed + acceptance proof
- **Priority**: P0
- **Complexity**: L
- **Depends on**: T-P0-826
- **Description**: EXECUTE (after manual unblock following user [approved] on docs/archive_plans/B4a-uber_2026-05-10.md). Steps: (1) generate archive/company_internalized/B4a-uber_2026-05-10_restore.sql with INSERT statements for every row to be deleted, (2) write full prose dump to archive/company_internalized/B4a-uber_2026-05-10.md, (3) move source seed scripts (scripts/seed_uber_*.py / scripts/content_*uber*.py / scripts/patch_uber_*.py) -> archive/seed_scripts/B4a-uber/, (4) DELETE rows per §4 plan, (5) author NEW seed scripts/seed_uber_drawer_index.py for the thin skeleton doc and run it (Invariant 3 compliance), (6) run scripts/audit_uri_consistency.py and assert exit 0, (7) execute the §2 'verifiable queries' and capture output as PROGRESS acceptance proof. Idempotent (re-runs detect already-archived state and no-op). AC: all 7 steps pass; PROGRESS entry includes verifiable-query outputs; UI loads / company page without dangling refs.

#### T-P0-828: [KG-INT B4b-meta] Meta execute: hard-archive + skeleton seed + acceptance proof
- **Priority**: P0
- **Complexity**: L
- **Depends on**: T-P0-827
- **Description**: EXECUTE (after manual unblock following user [approved] on docs/archive_plans/B4a-meta_2026-05-10.md). Steps: (1) generate archive/company_internalized/B4a-meta_2026-05-10_restore.sql with INSERT statements for every row to be deleted, (2) write full prose dump to archive/company_internalized/B4a-meta_2026-05-10.md, (3) move source seed scripts (scripts/seed_meta_*.py / scripts/content_*meta*.py / scripts/patch_meta_*.py) -> archive/seed_scripts/B4a-meta/, (4) DELETE rows per §4 plan, (5) author NEW seed scripts/seed_meta_drawer_index.py for the thin skeleton doc and run it (Invariant 3 compliance), (6) run scripts/audit_uri_consistency.py and assert exit 0, (7) execute the §2 'verifiable queries' and capture output as PROGRESS acceptance proof. Idempotent (re-runs detect already-archived state and no-op). AC: all 7 steps pass; PROGRESS entry includes verifiable-query outputs; UI loads / company page without dangling refs.

#### T-P1-606: Fix emoji-scan cp1252 crash + lock regex consistency (F-1 + F-3 + meta-test)
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Commit 1 of the emoji-scanner fix plan. BLOCKED on user decision between options A/B/C for the 1 legit FE0F hit in PROGRESS.md:590 (discord msg 1497033478842351616, 2026-04-23).

INVESTIGATION COMPLETE, revised findings:
- Original plan assumed 3 regexes byte-identical (subagent survey claim). Verified empirically: FALSE. check_emoji.py retains stale BMP ranges \u2600-\u26ff + \u2700-\u27bf; check_emoji_files.py and lint_check.py had them removed 2026-04-11 per archive/progress_log.md:20 (to kill 81 BLACK STAR-style false positives).
- Current full-repo scan: 63 hits from stale check_emoji.py regex; 62 are BMP false positives that DISAPPEAR under the narrow (canonical) regex; 1 is a legit U+FE0F variation selector in PROGRESS.md:590 from a quoted historical discord message about a prior emoji incident.
- Root cause of user pain is this regex drift (RC-3), not the Windows encoding issue alone (RC-1 is latent).

REVISED EXECUTION SCOPE when unblocked:
1. scripts/check_emoji.py: remove 2 BMP range lines to match check_emoji_files.py + lint_check.py.
2. scripts/check_emoji.py + scripts/check_emoji_files.py: F-1 UTF-8 stream reconfigure at main() entry (defense in depth for future U+1F6xx emoji).
3. tests/test_emoji_regex.py (or new tests/test_emoji_scanner.py): regex-equality meta-test + subprocess cp1252 env test (reviewer's revised F-3).
4. User-chosen handling of PROGRESS.md:590 FE0F (option A/B/C pending).

#### T-P1-657: Invariant-3 promotion: doc 84 §5 N-gram LM + problem 1097 to seed scripts
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Phase 4. Promote earlier session's Uber doc 84 §5 + problem 1097 to seed scripts. **Per reviewer hole #3**: do NOT delete scripts/migrations/add_uber_prob_nextword.py. Better: keep file, replace body with a no-op + DEPRECATED header. Reasons: (a) git history preservation in working tree, not just log; (b) staging / rebuild environments that re-run migrations get a clear deprecation message rather than missing file errors; (c) future readers can grep for the original migration intent.

THREE STEPS:

1. Update scripts/seed_uber_ml_coding_golden.py:
   - Append §5 N-gram LM section to CONTENT (~600 lines from current DB doc 84 -- copy verbatim from `SELECT content FROM company_documents WHERE id=84`)
   - Bump validate_content() length range (currently caps at probably 35-40K, new content is ~49K) and add §5 markers ('## §5' or '## 5. 概率下一个词生成' or 'ngram-next-word')
   - Re-run, expect [UNCHANGED] (since DB content already matches the new CONTENT)

2. Create scripts/seed_uber_ml_coding_problems.py (or extend an existing matching seed):
   - Owns the from-scratch ML coding problems for Uber: problem 1064 (K-Means), problem 1097 (N-gram LM), and ideally also Geometric Median + Linear Regression + Logistic Regression (the 4 §-1 through §-4 problems in doc 84)
   - Idempotent UPSERT on title (or leetcode_id when present)
   - Each row gets the proper company_tags JSON ['Uber'] AND a problem_company_tags row (relevance='likely', source='manual')
   - Notes field includes [db://doc/84#<anchor>] cross-link to the matching section
   - Re-run, expect 5 [UNCHANGED] (since DB already has them via the migration)

3. Replace scripts/migrations/add_uber_prob_nextword.py with no-op + deprecation:
   - First line: `# DEPRECATED 2026-04-30: Logic moved to scripts/seed_uber_ml_coding_golden.py and scripts/seed_uber_ml_coding_problems.py per Invariant 3 (no migration scripts that write to DB).`
   - Body: `if __name__ == '__main__': sys.exit(0)`
   - Keep file in git so future tree references resolve, but it does nothing if executed
   - Same treatment for scripts/migrations/update_pinterest_onsite_itinerary.py (the other this-session migration)

ACCEPTANCE CRITERIA:
- AC1: scripts/seed_uber_ml_coding_golden.py CONTENT now includes §5; second run = [UNCHANGED]
- AC2: scripts/seed_uber_ml_coding_problems.py exists with 5 problems (1064 + 1097 + 3 others); second run = 5×[UNCHANGED]
- AC3: scripts/migrations/add_uber_prob_nextword.py and scripts/migrations/update_pinterest_onsite_itinerary.py both replaced with deprecation no-op; running each prints '[DEPRECATED] no-op' and exits 0
- AC4: T-P0-660 invariant3 lint hook does NOT trigger on the no-op deprecated files (since they no longer contain INSERT/UPDATE) — this proves the lint design works
- AC5: `git diff scripts/migrations/` shows clean rewrites; `git log --follow scripts/migrations/add_uber_prob_nextword.py` still shows full history

DEPENDS ON: T-P0-660 (lint hook should already exist — this task verifies the hook accepts the deprecated files)
COMPLEXITY: M

#### T-P1-816: [KG-INT B4a-linkedin] LinkedIn dry-run: archive plan + causal-proof matrix
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: Per docs/workflow/company_internalization_protocol.md, dry-run for LinkedIn. Read all 6 note-surfaces for company_id=see audit B1, produce docs/archive_plans/B4a-linkedin_2026-05-10.md with §1 Inventory snapshot (byte counts + first 200 chars per surface), §2 Migration matrix (per-row 4-tuple: 原 prose 摘要 / 原覆盖 / 现迁移到 (kg/db/cd/sd URI) / 可验证查询), §3 Skeleton preview (full markdown of replacement thin drawer-link doc), §4 Hard-archive checklist (DB DELETE rows + UPDATE clears + seed-script moves + INSERT-statement restore.sql to be generated), §5 Promotion candidates flagged for meta-prep (any patterns spotted in this company that should be batch-promoted by B4-promotion). Discord ping user with plan path. WRITES NOTHING TO DB. AC: plan markdown exists; §2 has >=1 row per archive candidate; §3 skeleton renders; §5 lists 0+ candidates.

#### T-P1-817: [KG-INT B4a-tiktok] TikTok dry-run: archive plan + causal-proof matrix
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: Per docs/workflow/company_internalization_protocol.md, dry-run for TikTok. Read all 6 note-surfaces for company_id=see audit B1, produce docs/archive_plans/B4a-tiktok_2026-05-10.md with §1 Inventory snapshot (byte counts + first 200 chars per surface), §2 Migration matrix (per-row 4-tuple: 原 prose 摘要 / 原覆盖 / 现迁移到 (kg/db/cd/sd URI) / 可验证查询), §3 Skeleton preview (full markdown of replacement thin drawer-link doc), §4 Hard-archive checklist (DB DELETE rows + UPDATE clears + seed-script moves + INSERT-statement restore.sql to be generated), §5 Promotion candidates flagged for meta-prep (any patterns spotted in this company that should be batch-promoted by B4-promotion). Discord ping user with plan path. WRITES NOTHING TO DB. AC: plan markdown exists; §2 has >=1 row per archive candidate; §3 skeleton renders; §5 lists 0+ candidates.

#### T-P1-819: [KG-INT B4a-doordash] DoorDash dry-run: archive plan + causal-proof matrix
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Per docs/workflow/company_internalization_protocol.md, dry-run for DoorDash. Read all 6 note-surfaces for company_id=see audit B1, produce docs/archive_plans/B4a-doordash_2026-05-10.md with §1 Inventory snapshot (byte counts + first 200 chars per surface), §2 Migration matrix (per-row 4-tuple: 原 prose 摘要 / 原覆盖 / 现迁移到 (kg/db/cd/sd URI) / 可验证查询), §3 Skeleton preview (full markdown of replacement thin drawer-link doc), §4 Hard-archive checklist (DB DELETE rows + UPDATE clears + seed-script moves + INSERT-statement restore.sql to be generated), §5 Promotion candidates flagged for meta-prep (any patterns spotted in this company that should be batch-promoted by B4-promotion). Discord ping user with plan path. WRITES NOTHING TO DB. AC: plan markdown exists; §2 has >=1 row per archive candidate; §3 skeleton renders; §5 lists 0+ candidates.

#### T-P1-820: [KG-INT B4a-parspec] PARSPEC dry-run: archive plan + causal-proof matrix
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Per docs/workflow/company_internalization_protocol.md, dry-run for PARSPEC. Read all 6 note-surfaces for company_id=see audit B1, produce docs/archive_plans/B4a-parspec_2026-05-10.md with §1 Inventory snapshot (byte counts + first 200 chars per surface), §2 Migration matrix (per-row 4-tuple: 原 prose 摘要 / 原覆盖 / 现迁移到 (kg/db/cd/sd URI) / 可验证查询), §3 Skeleton preview (full markdown of replacement thin drawer-link doc), §4 Hard-archive checklist (DB DELETE rows + UPDATE clears + seed-script moves + INSERT-statement restore.sql to be generated), §5 Promotion candidates flagged for meta-prep (any patterns spotted in this company that should be batch-promoted by B4-promotion). Discord ping user with plan path. WRITES NOTHING TO DB. AC: plan markdown exists; §2 has >=1 row per archive candidate; §3 skeleton renders; §5 lists 0+ candidates.

#### T-P1-829: [KG-INT B4b-adobe] Adobe execute: hard-archive + skeleton seed + acceptance proof
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-815, T-P0-828
- **Description**: EXECUTE (after manual unblock following user [approved] on docs/archive_plans/B4a-adobe_2026-05-10.md). Steps: (1) generate archive/company_internalized/B4a-adobe_2026-05-10_restore.sql with INSERT statements for every row to be deleted, (2) write full prose dump to archive/company_internalized/B4a-adobe_2026-05-10.md, (3) move source seed scripts (scripts/seed_adobe_*.py / scripts/content_*adobe*.py / scripts/patch_adobe_*.py) -> archive/seed_scripts/B4a-adobe/, (4) DELETE rows per §4 plan, (5) author NEW seed scripts/seed_adobe_drawer_index.py for the thin skeleton doc and run it (Invariant 3 compliance), (6) run scripts/audit_uri_consistency.py and assert exit 0, (7) execute the §2 'verifiable queries' and capture output as PROGRESS acceptance proof. Idempotent (re-runs detect already-archived state and no-op). AC: all 7 steps pass; PROGRESS entry includes verifiable-query outputs; UI loads / company page without dangling refs.

#### T-P1-830: [KG-INT B4b-linkedin] LinkedIn execute: hard-archive + skeleton seed + acceptance proof
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-816, T-P1-829
- **Description**: EXECUTE (after manual unblock following user [approved] on docs/archive_plans/B4a-linkedin_2026-05-10.md). Steps: (1) generate archive/company_internalized/B4a-linkedin_2026-05-10_restore.sql with INSERT statements for every row to be deleted, (2) write full prose dump to archive/company_internalized/B4a-linkedin_2026-05-10.md, (3) move source seed scripts (scripts/seed_linkedin_*.py / scripts/content_*linkedin*.py / scripts/patch_linkedin_*.py) -> archive/seed_scripts/B4a-linkedin/, (4) DELETE rows per §4 plan, (5) author NEW seed scripts/seed_linkedin_drawer_index.py for the thin skeleton doc and run it (Invariant 3 compliance), (6) run scripts/audit_uri_consistency.py and assert exit 0, (7) execute the §2 'verifiable queries' and capture output as PROGRESS acceptance proof. Idempotent (re-runs detect already-archived state and no-op). AC: all 7 steps pass; PROGRESS entry includes verifiable-query outputs; UI loads / company page without dangling refs.

#### T-P1-831: [KG-INT B4b-tiktok] TikTok execute: hard-archive + skeleton seed + acceptance proof
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-817, T-P1-830
- **Description**: EXECUTE (after manual unblock following user [approved] on docs/archive_plans/B4a-tiktok_2026-05-10.md). Steps: (1) generate archive/company_internalized/B4a-tiktok_2026-05-10_restore.sql with INSERT statements for every row to be deleted, (2) write full prose dump to archive/company_internalized/B4a-tiktok_2026-05-10.md, (3) move source seed scripts (scripts/seed_tiktok_*.py / scripts/content_*tiktok*.py / scripts/patch_tiktok_*.py) -> archive/seed_scripts/B4a-tiktok/, (4) DELETE rows per §4 plan, (5) author NEW seed scripts/seed_tiktok_drawer_index.py for the thin skeleton doc and run it (Invariant 3 compliance), (6) run scripts/audit_uri_consistency.py and assert exit 0, (7) execute the §2 'verifiable queries' and capture output as PROGRESS acceptance proof. Idempotent (re-runs detect already-archived state and no-op). AC: all 7 steps pass; PROGRESS entry includes verifiable-query outputs; UI loads / company page without dangling refs.

#### T-P1-832: [KG-INT B4b-slack] Slack execute: hard-archive + skeleton seed + acceptance proof
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-818, T-P1-831
- **Description**: EXECUTE (after manual unblock following user [approved] on docs/archive_plans/B4a-slack_2026-05-10.md). Steps: (1) generate archive/company_internalized/B4a-slack_2026-05-10_restore.sql with INSERT statements for every row to be deleted, (2) write full prose dump to archive/company_internalized/B4a-slack_2026-05-10.md, (3) move source seed scripts (scripts/seed_slack_*.py / scripts/content_*slack*.py / scripts/patch_slack_*.py) -> archive/seed_scripts/B4a-slack/, (4) DELETE rows per §4 plan, (5) author NEW seed scripts/seed_slack_drawer_index.py for the thin skeleton doc and run it (Invariant 3 compliance), (6) run scripts/audit_uri_consistency.py and assert exit 0, (7) execute the §2 'verifiable queries' and capture output as PROGRESS acceptance proof. Idempotent (re-runs detect already-archived state and no-op). AC: all 7 steps pass; PROGRESS entry includes verifiable-query outputs; UI loads / company page without dangling refs.

#### T-P1-833: [KG-INT B4b-doordash] DoorDash execute: hard-archive + skeleton seed + acceptance proof
- **Priority**: P1
- **Complexity**: S
- **Depends on**: T-P1-819, T-P1-832
- **Description**: EXECUTE (after manual unblock following user [approved] on docs/archive_plans/B4a-doordash_2026-05-10.md). Steps: (1) generate archive/company_internalized/B4a-doordash_2026-05-10_restore.sql with INSERT statements for every row to be deleted, (2) write full prose dump to archive/company_internalized/B4a-doordash_2026-05-10.md, (3) move source seed scripts (scripts/seed_doordash_*.py / scripts/content_*doordash*.py / scripts/patch_doordash_*.py) -> archive/seed_scripts/B4a-doordash/, (4) DELETE rows per §4 plan, (5) author NEW seed scripts/seed_doordash_drawer_index.py for the thin skeleton doc and run it (Invariant 3 compliance), (6) run scripts/audit_uri_consistency.py and assert exit 0, (7) execute the §2 'verifiable queries' and capture output as PROGRESS acceptance proof. Idempotent (re-runs detect already-archived state and no-op). AC: all 7 steps pass; PROGRESS entry includes verifiable-query outputs; UI loads / company page without dangling refs.

#### T-P1-834: [KG-INT B4b-parspec] PARSPEC execute: hard-archive + skeleton seed + acceptance proof
- **Priority**: P1
- **Complexity**: S
- **Depends on**: T-P1-820, T-P1-833
- **Description**: EXECUTE (after manual unblock following user [approved] on docs/archive_plans/B4a-parspec_2026-05-10.md). Steps: (1) generate archive/company_internalized/B4a-parspec_2026-05-10_restore.sql with INSERT statements for every row to be deleted, (2) write full prose dump to archive/company_internalized/B4a-parspec_2026-05-10.md, (3) move source seed scripts (scripts/seed_parspec_*.py / scripts/content_*parspec*.py / scripts/patch_parspec_*.py) -> archive/seed_scripts/B4a-parspec/, (4) DELETE rows per §4 plan, (5) author NEW seed scripts/seed_parspec_drawer_index.py for the thin skeleton doc and run it (Invariant 3 compliance), (6) run scripts/audit_uri_consistency.py and assert exit 0, (7) execute the §2 'verifiable queries' and capture output as PROGRESS acceptance proof. Idempotent (re-runs detect already-archived state and no-op). AC: all 7 steps pass; PROGRESS entry includes verifiable-query outputs; UI loads / company page without dangling refs.

#### T-P1-909: [ML-Infra-LLM] Seed anthropic-distributed-model-deployment golden (500GB model distribution SD)
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: CONTENT SEED (Invariant 3). Idempotent scripts/seed_anthropic_distributed_model_deployment_golden.py for a new system_designs row. Source: user-provided golden doc 'distributed_model_deployment_golden_answer.md' (500GB model -> 100-1000 GPU workers, pipeline distribution). slug='anthropic-distributed-model-deployment'; title from doc; subtitle='Anthropic · ML Infra (LLM)' (Anthropic tag = scheme A: slug prefix + subtitle, since system_designs has NO company_id col); display_order=300 (first in ML-Infra band; future docs 301,302...). 9-column mapping: overview<-需求澄清(problem+func/nonfunc+clarification+out-of-scope); architecture<-架构深度解析; dataflow<-API设计与数据流; formulas<-容量估算与核心算法(keep 20785..20785 math); production_constraints<-生产环境约束; tradeoffs<-权衡讨论; defense<-面试官追问Q&A; verbal_outline<-1小时节奏指南+3分钟电梯演讲; cheat_sheet<-常见错误+精简pitch. NOT MLSD family -> do NOT apply [DOMINANT]/floating-twist golden markers (Meta-MLSD-only contract). Sentinel UPSERT keyed on slug; 2x run = byte-identical. Optional light incremental polish: CN-narration + EN-term first-occurrence expansion consistency, obvious typos ONLY -- preserve user's voice/length, no rewrite. AC: seed exit 0 + idempotent re-run no-op; GET /api/system-designs/anthropic-distributed-model-deployment -> 200 with all 9 fields populated & non-trivial; row at display_order=300; MANUAL SMOKE: /system-design?tab=ml-infra-llm shows the card -> drawer 9 sections render incl. KaTeX math.

#### T-P1-917: [HUMAN-REVIEW] Guard Phase B: enforcer -- CI fail-on-drift (mandatory) + runtime safe-heal + settings.json wiring
- **Priority**: P1
- **Complexity**: L
- **Depends on**: T-P1-912
- **Description**: ## Summary
Phase B: promote the scanner to an ENFORCER -- a mandatory CI gate that fails on uncovered drift, plus runtime safe-mode self-heal, plus the sensitive .claude/settings.json PreToolUse wiring. Enabled only after drift taxonomy is decided.

## Context
User synthesis (overrides Review "CI optional"): until the consistency model matures, CI fail on uncovered drift is MANDATORY, not optional. Layering = pre-commit scan+suggest (Phase A, shipped) / CI fail (here, mandatory) / runtime safe-heal (here). Phase B waits for 913 (and 916) so "covered vs uncovered" is well-defined and the enforcer does not fail CI on classes still under decision.

## Acceptance Criteria
- [ ] AC1 (CI gate, mandatory): a CI step runs description_progress_guard --sweep over scripts/ AND a DB consistency check (count of fully-checked-but-not-mastered == 0) and FAILS the build (exit nonzero) on any uncovered drift. Not behind an opt-in flag.
- [ ] AC2 (runtime safe-heal): a documented safe path (e.g. a make/CLI target) that runs the T-P0-910 reconcile on the fully-checked signature so a developer can self-heal locally before pushing.
- [ ] AC3 (both branches): drift present + class is "covered" (fully-checked) -> CI fails with the exact self-heal command; drift present but class is "under-decision" (reverse/partial, per 913/916) -> CI does NOT fail on it (allow-listed) but logs it.
- [ ] AC4 (sensitive wiring, HITL): deliver the .claude/settings.json PreToolUse snippet (Write+Edit+Bash, mirroring invariant3_guard) and the CI workflow file as a diff; request explicit human sign-off for the settings.json registration -- do NOT self-apply (settings.json is in the autonomous-mode sensitive-file gate; this task carries human_review=1).
- [ ] AC5 (journey): dev pushes a non-reconciling description change -> CI fails citing the self-heal cmd -> dev runs it -> reconciled -> CI green.
- [ ] AC6: the Phase-A scanner is upgraded in-place to also support an --enforce exit-2 mode used by CI; pre-commit stays warn-only (DX preserved).

## Technical Approach
- Add CI workflow + an --enforce mode to the Phase A hook. settings.json wiring delivered as a reviewed snippet, applied by a human.

## Edge Cases
- The allow-list for under-decision classes must be data-driven (reads 913/916 verdicts) so it auto-shrinks as classes are resolved -- document.
- Never crash; CI failure messages must name the exact remediation command.

## Complexity
L -- enforcer mode + CI workflow + data-driven allow-list + sensitive split sign-off.

## Dependencies
T-P1-912 (Phase A scanner -- enforcer extends it) and T-P2-913 (reverse-drift verdicts define the under-decision allow-list). Last in the chain so CI does not fail on classes still pending a human decision.

#### T-P1-921: [WSH-E1] MLI drawer_nav 抽列 + 4 retrofit 退役 + E2 决策门
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: ## Summary
Extract drawer navigation out of company_documents.content markdown into a structured drawer_nav JSON column, assemble at render time, retire the 4 retrofit_meta_mlsd_*_drawer_header.py scripts. V1 of the multi-surface fix; NO full normalization. Adds a stability-observation gate for E2.

## drawer_nav JSON schema
{"items":[{"label":"string","anchor":"string","depth":1,"ref":"cd://N|sd://slug|null"}],"rendered_at_top":true}

## Acceptance Criteria
- [ ] AC1: company_documents gets a drawer_nav JSON column (migration + relevant seed updates).
- [ ] AC2: frontend CompanyDocDrawer assembles nav from drawer_nav above the body; render equivalent to current.
- [ ] AC3: the 4 retrofit scripts archived (moved to scripts/migrate/ with SAFE_DELETE_AFTER) or deleted; re-seed no longer needs them.
- [ ] AC4 (journey): open a Meta-MLSD doc drawer -> drawer nav shows correctly, links clickable (URI scheme preserved).
- [ ] AC5: audit_uri_consistency.py all green.
- [ ] AC6 (E2 decision gate): drawer_nav abstraction holds with NO regression on >=3 MLSD docs for >=2 weeks (no schema tweak, no retrofit-class op). E2 must NOT start until this AC is checked; once checked, human decides whether to proceed to E2 or hold.

## Complexity: M. Deps: None.

#### T-P2-922: [WSH-E2] MLI content 归一化 (sections + 跨引用外键, 终局)
- **Priority**: P2
- **Complexity**: L
- **Depends on**: T-P1-921
- **Description**: ## Summary
Normalize company_documents.content into company_document_sections (section_key/body/order) + upgrade cross-refs to FK constraints. Multi-surface render goes from 'parse markdown' to 'project sections'. The +1-quarter endgame. HUMAN_REVIEW: large schema migration. GATED by E1.AC6 (2-week no-regression observation).

## Acceptance Criteria
- [ ] AC1: join table schema + all seeds rewritten.
- [ ] AC2: cd:// / sd:// cross-refs become FK; dangling ref fails the constraint.
- [ ] AC3: projection function exports drawer-summary / full-page / index renditions from one master.
- [ ] AC4 (journey): edit one master -> all three surfaces change in sync.
- [ ] AC5: all seeds idempotent + URI audit green.

## Complexity: L. Deps: E1 (incl. AC6 gate). HUMAN_REVIEW: yes.

## Completed Tasks

> 828 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-06-19** -- T-P1-815: [KG-INT B4a-adobe] Adobe dry-run: archive plan + causal-proof matrix. Per docs/workflow/company_internalization_protocol.md, dry-run for Adobe. Read all 6 note-surfaces for company_id=see au
- [x] **2026-06-19** -- T-P1-643: [CHEATSHEET-3] Add 2 Uber rows to system_designs from doc 85 (Restaurant Rec + Budget-Constrained Promo). Currently Uber Eats Restaurant Recommendation and Budget-Constrained Promo Recommendation only live inside company_docum
- [x] **2026-06-19** -- T-P1-642: [CHEATSHEET-2] Frontend: add 'Cheat Sheet' tab to /system-design with one-pager card per row. Add third tab 'Cheat Sheet' to SystemDesignList.tsx alongside 'Interview Prep' and 'eBay Projects'. New tab renders a ve
- [x] **2026-06-19** -- T-P1-641: [CHEATSHEET-1] Schema + API: add cheat_sheet TEXT column to system_designs, expose in /system-designs/:slug. Add nullable TEXT column 'cheat_sheet' to system_designs SQLAlchemy model + Alembic-style migration script (scripts/migr
- [x] **2026-06-18** -- T-P2-585: [BQ-DEPTH-14] Phase E: narrow probe-drift detector (principle_tags/risk/outcome/hash only). Per user direction: drift trigger must be NARROW. Monitoring arbitrary STAR field changes will produce noise the user le
- [x] **2026-06-18** -- T-P1-912: Guard Phase A: scanner-only (detect + warn + autofix-suggestion, NO block, single mode). ## Summary
- [x] **2026-06-18** -- T-P1-818: [KG-INT B4a-slack] Slack dry-run: archive plan + causal-proof matrix. Per docs/workflow/company_internalization_protocol.md, dry-run for Slack. Read all 6 note-surfaces for company_id=see au
- [x] **2026-06-18** -- T-P1-583: [BQ-DEPTH-12] Frontend Phase D: primary-story prominent card + probe_notes expandable panel. src/frontend/src/pages/BehavioralQuestions.tsx redesign.
- [x] **2026-06-17** -- T-P3-916: 92-class partial pct-stale: decision doc (low risk, deterministic recommendation). ## Summary
- [x] **2026-06-17** -- T-P2-905: Archive PROGRESS.md (545 lines > ~300 convention) to archive/progress_log.md, keep ~40-50 recent sessions
- [x] **2026-06-17** -- T-P2-880: [SYNC] MLI: Add study-review skill from claude-code-project-template (relevant to MLSD study-deck work). claude-code-project-template ships `.claude/skills/study-review/` which MLI lacks. Given the active MLSD study-deck work
- [x] **2026-06-17** -- T-P2-879: [DEBT] MLI: shared/hooks/task_store.py:145 SIM105 (try/except/pass -> contextlib.suppress). `ruff check` (whole-tree scan, excluding src/tests/archive) flags shared/hooks/task_store.py:145 with SIM105: the try/ex
- [x] **2026-06-17** -- T-P2-878: [DEBT] MLI: pyproject.toml missing 4 dev deps present in requirements.txt (ruff, pytest, pytest-asyncio, pyyaml). requirements.txt lists ruff==0.15.4, pytest==7.4.4, pytest-asyncio==0.23.3, pyyaml==6.0 under a `# Development tools` he
