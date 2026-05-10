# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

#### T-P0-808: [KG-INT B4a-google] Google dry-run: archive plan + causal-proof matrix
- **Priority**: P0
- **Complexity**: L
- **Depends on**: T-P1-798, T-P1-799, T-P1-800, T-P1-801, T-P1-802, T-P1-803, T-P1-804, T-P1-805, T-P1-806, T-P1-807
- **Description**: Per docs/workflow/company_internalization_protocol.md, dry-run for Google. Read all 6 note-surfaces for company_id=see audit B1, produce docs/archive_plans/B4a-google_2026-05-10.md with §1 Inventory snapshot (byte counts + first 200 chars per surface), §2 Migration matrix (per-row 4-tuple: 原 prose 摘要 / 原覆盖 / 现迁移到 (kg/db/cd/sd URI) / 可验证查询), §3 Skeleton preview (full markdown of replacement thin drawer-link doc), §4 Hard-archive checklist (DB DELETE rows + UPDATE clears + seed-script moves + INSERT-statement restore.sql to be generated), §5 Promotion candidates flagged for meta-prep (any patterns spotted in this company that should be batch-promoted by B4-promotion). Discord ping user with plan path. WRITES NOTHING TO DB. AC: plan markdown exists; §2 has >=1 row per archive candidate; §3 skeleton renders; §5 lists 0+ candidates.

#### T-P0-809: [KG-INT B4a-lyra] Lyra dry-run: archive plan + causal-proof matrix
- **Priority**: P0
- **Complexity**: M
- **Depends on**: T-P1-798, T-P1-799, T-P1-800, T-P1-801, T-P1-802, T-P1-803, T-P1-804, T-P1-805, T-P1-806, T-P1-807
- **Description**: Per docs/workflow/company_internalization_protocol.md, dry-run for Lyra. Read all 6 note-surfaces for company_id=see audit B1, produce docs/archive_plans/B4a-lyra_2026-05-10.md with §1 Inventory snapshot (byte counts + first 200 chars per surface), §2 Migration matrix (per-row 4-tuple: 原 prose 摘要 / 原覆盖 / 现迁移到 (kg/db/cd/sd URI) / 可验证查询), §3 Skeleton preview (full markdown of replacement thin drawer-link doc), §4 Hard-archive checklist (DB DELETE rows + UPDATE clears + seed-script moves + INSERT-statement restore.sql to be generated), §5 Promotion candidates flagged for meta-prep (any patterns spotted in this company that should be batch-promoted by B4-promotion). Discord ping user with plan path. WRITES NOTHING TO DB. AC: plan markdown exists; §2 has >=1 row per archive candidate; §3 skeleton renders; §5 lists 0+ candidates.

### P1 -- Should Have (agentic intelligence)

#### T-P1-582: [BQ-DEPTH-11] Bulk probe_notes for remaining ~36 high-probability questions
- **Priority**: P1
- **Complexity**: L
- **Depends on**: T-P1-581
- **Description**: After calibration samples (BQ-DEPTH-09) approved + primary flags set (BQ-DEPTH-10), write probe_notes for the remaining 36 questions in the top 40.

Split into 3-4 sub-batches of ~10 each, each a separate autonomous session per feedback_always_auto_run. Between batches, user spot-check one probe_notes entry to catch style drift early.

Content rules (locked by BQ-DEPTH-09 calibration):
- 中文叙述 + 英文术语
- All 4 schema fields required (core_signal, what_good_looks_like, what_L5_adds, common_failure_modes)
- Reference the is_primary story in what_good_looks_like
- No angle_label -- angle lives in prose

Deliverables:
- scripts/seed_bq_probe_notes_batch{1-4}_20260421.py -- each idempotent + DB-backup-guarded
- After each batch: spot-check doc attached to Discord for user review

AC:
- All 40 top questions have probe_notes set
- Each batch script re-runs with [SKIP]
- No schema field empty; all 4 structured fields populated for every question
- User spot-check passed between batches

#### T-P1-583: [BQ-DEPTH-12] Frontend Phase D: primary-story prominent card + probe_notes expandable panel
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-581
- **Description**: src/frontend/src/pages/BehavioralQuestions.tsx redesign.

Journey-first AC (from CLAUDE.md planning rules): user opens /behavioral -> clicks expand on a top-40 question -> sees ONE gold-bordered primary story card (big, with full relevance_note + STAR Situation preview + 'use this angle' hint) -> sees 'Also applies' collapsed panel with 2-3 backup stories -> clicks 'What this question probes' -> sees 4-section probe_notes panel (core_signal / what_good_looks_like / what_L5_adds / common_failure_modes).

Scenario matrix:
- Question has is_primary link + probe_notes -> full new treatment
- Question has is_primary link + no probe_notes -> primary card only, probe panel hidden
- Question has no is_primary link (non-top-40) -> current flat list fallback (no visual regression)
- Question has 0 links -> current 'no example' red badge

Manual smoke test AC:
- Launch vite dev (localhost:5173/behavioral); pick OWN-1 (will have probe_notes after Phase C); verify primary card is gold-bordered and renders at top; verify probe_notes panel expands and shows 4 sections with markdown; verify 'Also applies' toggles

Also update frontend type src/frontend/src/types/behavioral.ts to include probe_notes + is_primary.

AC:
- TypeScript compiles
- vitest suite passes
- Manual smoke test path completes without console errors
- No regression on questions without probe_notes / without is_primary

#### T-P1-777: Pinterest LC notes voice + density refactor: pilot on LC 465 + LC 1723
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Discord ad-hoc msg 1501625424210563193 (2026-05-06): user flagged LC 465 + LC 1723 bitmask/状压 explanations as 啰嗦 + variable naming/comments 太简单. Audit complete (see PROGRESS 2026-05-06 16:50 [planning] entry): identified 6 verbosity patterns (P1 section duplication, P2 AI-explainer padding, P3 tutorial-tone code comments, P4 retained code-review nits, P5 dense-prose lemmas, P6 worked-example tables). Concrete deltas drafted: LC 465 5375c -> ~2400-2800c, LC 1723 5604c -> ~3000c. Propagation surface clean (only doc 47 + 66 link, no SD/framework/BQ refs). Awaiting user answers to 3 open Qs before executing: (1) cut depth approval, (2) voice anchor (LC 322 vs LC 426/1293), (3) drop Approach C in LC 1723. On approval: execute as seed_pinterest_lc_voice_refactor_465_1723_20260506.py with sentinel-guarded UPDATE on problems.notes for ids 214 + 1067; verify byte-level via re-run [SKIP], API smoke, drawer render.

#### T-P1-797: [KG-INT A2] Frontend: replace hasPrepNotes with has_meaningful_note + tooltip + test
- **Priority**: P1
- **Complexity**: S
- **Depends on**: T-P1-796
- **Description**: src/frontend/src/pages/Companies.tsx:509-521: replace hasPrepNotes with has_meaningful_note from API response. Keep inPipeline (status!=rejected) gate. Update title attr to 'Has prep notes / docs / tagged content'. Add 1 vitest case asserting red-dot renders when has_meaningful_note=true. AC: vitest passes; manual browser smoke at /companies shows red-dot on the ~12 companies the composite rule selects (verify against A0 EDA list).

#### T-P1-798: [KG-INT B1] Full per-company audit dump across 6 note surfaces
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: Script scripts/_audit_company_kg_internalization.py: for each of 32 companies, dump bytes/topics/KG-coverage/drawer-link-ratio/internalization-candidate% per surface (prep_notes, notes, company_documents, problem_company_tags, node_company_tags, behavioral_example_company_tags). Write docs/audit/company_kg_internalization_audit_2026-05-10.md. AC: report exists; covers all 32 companies; each company has 6-surface row.

#### T-P1-799: [KG-INT B2a] kg://N URI scheme: frontend parser + dispatch callback
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: src/frontend/src/components/ui/MarkdownPreview.tsx: add 5th regex ^kg://(\d+)(?:#[^\s]*)?$ + onKgLinkClick(nodeId) callback prop. Wire dispatcher: either reuse existing /kg/graph view focused on the node id, OR build new lightweight KgNodeDrawer component (decide based on existing FrameworkNode endpoint shape). Backend: ensure GET endpoint for framework_nodes by id exists (likely src/backend/routers/kg.py). AC: clicking kg://1 link in any markdown opens the node drawer/view; vitest snapshot for parser regex.

#### T-P1-800: [KG-INT B2b] Add 'meta-prep' pillar + 5 sub-node stubs
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: Idempotent seed scripts/seed_meta_prep_pillar.py: insert depth-0 node path='meta-prep' (title 'Cross-Company Interview Meta-Knowledge') + 5 depth-1 children: meta-prep/behavioral-clusters, meta-prep/lc-keyword-checklists, meta-prep/system-design-must-knows, meta-prep/onsite-loop-templates, meta-prep/code-pad-best-practices. Stubs only (one-line description each); B3 fills content. AC: framework_nodes count +6; KG view at /kg/graph shows new pillar.

#### T-P1-801: [KG-INT B2c] Internalization protocol doc + promotion_criteria + archive/ scaffold
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Write docs/workflow/company_internalization_protocol.md (7-step protocol + §2 Migration matrix template with 4-tuple causal-proof: (原 prose 摘要, 原覆盖, 现迁移到, 可验证查询)). Write docs/workflow/promotion_criteria.md: locks 'appears in >=3 of 11 P0+P1 companies AND wording can be de-companied' as the meta-prep promotion threshold. Create archive/company_internalized/.gitkeep + archive/seed_scripts/.gitkeep. AC: 2 protocol docs committed; archive/ subdirs exist.

#### T-P1-802: [KG-INT B2d] audit_uri_consistency.py: extend with kg:// scheme support
- **Priority**: P1
- **Complexity**: S
- **Depends on**: T-P1-799
- **Description**: scripts/audit_uri_consistency.py currently covers db:// cd:// sd:// (see file's docstring lines 1-30). Add kg://N regex + check N exists in framework_nodes.id. Surface as 4th audit class with VALID/ERROR (no cross-table WARNING since kg targets a distinct table). Update docstring + --json output schema. AC: audit script processes a company_documents row containing kg://1 link with a valid framework_node id=1, reports VALID; with id=99999 (nonexistent) reports ERROR.

#### T-P1-803: [KG-INT B3-1] Shared substrate: behavioral patterns -> meta-prep/behavioral-clusters
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-800, T-P1-801
- **Description**: Scan all 11 P0+P1 companies' surfaces (prep_notes, notes, company_documents). Extract behavioral patterns appearing in >=3 of 11 (per promotion_criteria.md). Author idempotent seed for meta-prep/behavioral-clusters + child nodes (one per cluster). Sources: STAR templates, cluster-first survey methodology, dual-cut pattern. AC: framework_nodes under meta-prep/behavioral-clusters has >=5 child nodes; each node has 'sources_companies' field listing >=3 P0+P1 IDs.

#### T-P1-804: [KG-INT B3-2] Shared substrate: SD vocab -> meta-prep/system-design-must-knows
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-800, T-P1-801
- **Description**: Same protocol as B3-1 but for system-design vocabulary: ANN/HNSW/IVF/PQ, LTR/NDCG, MMoE/PLE, calibration metrics, etc. Extract terms that appear in >=3 P0+P1 companies' SD prep. Cross-link to existing system_designs rows + framework_nodes via kg:// or sd://. AC: meta-prep/sd-must-knows child node count >=20; cross-links present.

#### T-P1-805: [KG-INT B3-3] Shared substrate: AI-native code-pad -> meta-prep/code-pad-best-practices
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-800, T-P1-801
- **Description**: Extract AI-native coding playbook (Meta-style 3-step prompt drill, AI tool usage best practices) from companies whose interviews emphasize this (Meta, OpenAI, Anthropic). AC: meta-prep/code-pad-best-practices child nodes >=4; sources include all companies that emphasize AI-native.

#### T-P1-806: [KG-INT B3-4] Shared substrate: LC keywords -> meta-prep/lc-keyword-checklists
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-800, T-P1-801
- **Description**: Cross-company LC keyword frequency: which problem types/tags appear in >=3 P0+P1 prep docs. Build per-tag checklist + frequency annotation. AC: lc-keyword-checklists has child nodes per high-frequency tag; each annotates its source companies.

#### T-P1-807: [KG-INT B3-5] Shared substrate: onsite loop templates -> meta-prep/onsite-loop-templates
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-800, T-P1-801
- **Description**: Extract general onsite loop structures (4-round VO, hiring committee, team match) appearing in >=3 P0+P1 docs. AC: onsite-loop-templates has >=3 template child nodes with structural diagrams.

#### T-P1-821: [KG-INT B4-promotion] Consolidate flagged promotion candidates -> meta-prep updates
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P0-808, T-P0-809, T-P0-810, T-P0-811, T-P0-812, T-P0-813, T-P0-814, T-P1-815, T-P1-816, T-P1-817, T-P1-818, T-P1-819, T-P1-820
- **Description**: Read §5 'Promotion candidates flagged for meta-prep' from each B4a archive plan in docs/archive_plans/. Deduplicate. For candidates passing the >=3 P0+P1 threshold (per promotion_criteria.md), author follow-up seed updates to meta-prep child nodes. AC: list of accepted vs rejected candidates committed; framework_nodes deltas applied via idempotent seed; updated archive plans get a §6 'promoted' section.

### P2 -- Nice to Have

#### T-P2-585: [BQ-DEPTH-14] Phase E: narrow probe-drift detector (principle_tags/risk/outcome/hash only)
- **Priority**: P2
- **Complexity**: S
- **Depends on**: T-P1-582
- **Description**: Per user direction: drift trigger must be NARROW. Monitoring arbitrary STAR field changes will produce noise the user learns to ignore.

Write scripts/detect_probe_drift.py that flags probe_notes needing refresh ONLY when one of these changes on a linked story since probe_notes_updated_at:
- behavioral_examples.principle_tags
- behavioral_examples.risk_statement
- behavioral_examples.result (the outcome)
- Narrative hash (SHA256 of situation+task+action+result) changed AND delta > threshold (e.g. >30% diff)

Output: docs/bq_probe_drift_report_<date>.md listing (question_id, linked_example_id, drift_reason, diff_preview).

Optional: cron-schedule via session_context.py reminder (not hook -- reminder only).

AC:
- Script reads-only; no DB writes
- Empty output when no drift (silent-on-no-work rule)
- False-positive rate: manually run after BQ-DEPTH-09 with no changes; expect 0 reports
- True-positive rate: manually mutate a test risk_statement; expect 1 report

#### T-P2-835: [KG-INT B6-P2-batch] 18 applied-status companies: KG-extraction only (no archive)
- **Priority**: P2
- **Complexity**: L
- **Depends on**: T-P1-803, T-P1-804, T-P1-805, T-P1-806, T-P1-807
- **Description**: For 18 applied-status companies (Apple, Nvidia, Reddit, Salesforce, Microsoft, Instacart, Robinhood, Roblox, Amazon, Coinbase, Quora, Intuit, Snap, OpenAI, Anthropic, Airbnb, Glean, Netflix), run a lightweight pass: scan notes/cd content for promotion-eligible patterns + add concept_links to existing/new framework_nodes. NO archive (these may upgrade to phone_screen). AC: framework_nodes concept_links count > current 11; report at docs/audit/p2_batch_kg_extraction_2026-05-10.md.

#### T-P2-836: [KG-INT B6-cleanup] Final acceptance checklist + audit + savings stats
- **Priority**: P2
- **Complexity**: S
- **Depends on**: T-P1-821, T-P2-835, T-P1-834
- **Description**: Final 4-item acceptance checklist (per Discord plan v3 §9): (a) all P0/P1 companies' prep_notes/notes byte counts < threshold anchored by A0 EDA; (b) meta-prep child nodes mean byte count > 800; (c) audit_uri_consistency.py reports 0 broken kg:// db:// cd:// sd://; (d) red-dot logic manual smoke on sample companies passes. Compute byte-savings stats (before vs after) + commit count + KG growth (node + link delta). PROGRESS close-out entry summarizes the 42-task batch. AC: all 4 checklist items pass; close-out entry written.

### P3 -- Stretch Goals

## Blocked

#### T-P0-810: [KG-INT B4a-pinterest-toc] Pinterest-TOC dry-run: archive plan + causal-proof matrix
- **Priority**: P0
- **Complexity**: M
- **Depends on**: T-P1-798, T-P1-799, T-P1-800, T-P1-801, T-P1-802, T-P1-803, T-P1-804, T-P1-805, T-P1-806, T-P1-807
- **Description**: Per docs/workflow/company_internalization_protocol.md, dry-run for Pinterest-TOC. Read all 6 note-surfaces for company_id=see audit B1, produce docs/archive_plans/B4a-pinterest-toc_2026-05-10.md with §1 Inventory snapshot (byte counts + first 200 chars per surface), §2 Migration matrix (per-row 4-tuple: 原 prose 摘要 / 原覆盖 / 现迁移到 (kg/db/cd/sd URI) / 可验证查询), §3 Skeleton preview (full markdown of replacement thin drawer-link doc), §4 Hard-archive checklist (DB DELETE rows + UPDATE clears + seed-script moves + INSERT-statement restore.sql to be generated), §5 Promotion candidates flagged for meta-prep (any patterns spotted in this company that should be batch-promoted by B4-promotion). Discord ping user with plan path. WRITES NOTHING TO DB. AC: plan markdown exists; §2 has >=1 row per archive candidate; §3 skeleton renders; §5 lists 0+ candidates.

#### T-P0-811: [KG-INT B4a-pinterest-concepts] Pinterest-CONCEPTS dry-run: archive plan + causal-proof matrix
- **Priority**: P0
- **Complexity**: L
- **Depends on**: T-P1-798, T-P1-799, T-P1-800, T-P1-801, T-P1-802, T-P1-803, T-P1-804, T-P1-805, T-P1-806, T-P1-807
- **Description**: Per docs/workflow/company_internalization_protocol.md, dry-run for Pinterest-CONCEPTS. Read all 6 note-surfaces for company_id=see audit B1, produce docs/archive_plans/B4a-pinterest-concepts_2026-05-10.md with §1 Inventory snapshot (byte counts + first 200 chars per surface), §2 Migration matrix (per-row 4-tuple: 原 prose 摘要 / 原覆盖 / 现迁移到 (kg/db/cd/sd URI) / 可验证查询), §3 Skeleton preview (full markdown of replacement thin drawer-link doc), §4 Hard-archive checklist (DB DELETE rows + UPDATE clears + seed-script moves + INSERT-statement restore.sql to be generated), §5 Promotion candidates flagged for meta-prep (any patterns spotted in this company that should be batch-promoted by B4-promotion). Discord ping user with plan path. WRITES NOTHING TO DB. AC: plan markdown exists; §2 has >=1 row per archive candidate; §3 skeleton renders; §5 lists 0+ candidates.

#### T-P0-812: [KG-INT B4a-pinterest-prep] Pinterest-prep dry-run: archive plan + causal-proof matrix
- **Priority**: P0
- **Complexity**: M
- **Depends on**: T-P1-798, T-P1-799, T-P1-800, T-P1-801, T-P1-802, T-P1-803, T-P1-804, T-P1-805, T-P1-806, T-P1-807
- **Description**: Per docs/workflow/company_internalization_protocol.md, dry-run for Pinterest-prep. Read all 6 note-surfaces for company_id=see audit B1, produce docs/archive_plans/B4a-pinterest-prep_2026-05-10.md with §1 Inventory snapshot (byte counts + first 200 chars per surface), §2 Migration matrix (per-row 4-tuple: 原 prose 摘要 / 原覆盖 / 现迁移到 (kg/db/cd/sd URI) / 可验证查询), §3 Skeleton preview (full markdown of replacement thin drawer-link doc), §4 Hard-archive checklist (DB DELETE rows + UPDATE clears + seed-script moves + INSERT-statement restore.sql to be generated), §5 Promotion candidates flagged for meta-prep (any patterns spotted in this company that should be batch-promoted by B4-promotion). Discord ping user with plan path. WRITES NOTHING TO DB. AC: plan markdown exists; §2 has >=1 row per archive candidate; §3 skeleton renders; §5 lists 0+ candidates.

#### T-P0-813: [KG-INT B4a-uber] Uber dry-run: archive plan + causal-proof matrix
- **Priority**: P0
- **Complexity**: L
- **Depends on**: T-P1-798, T-P1-799, T-P1-800, T-P1-801, T-P1-802, T-P1-803, T-P1-804, T-P1-805, T-P1-806, T-P1-807
- **Description**: Per docs/workflow/company_internalization_protocol.md, dry-run for Uber. Read all 6 note-surfaces for company_id=see audit B1, produce docs/archive_plans/B4a-uber_2026-05-10.md with §1 Inventory snapshot (byte counts + first 200 chars per surface), §2 Migration matrix (per-row 4-tuple: 原 prose 摘要 / 原覆盖 / 现迁移到 (kg/db/cd/sd URI) / 可验证查询), §3 Skeleton preview (full markdown of replacement thin drawer-link doc), §4 Hard-archive checklist (DB DELETE rows + UPDATE clears + seed-script moves + INSERT-statement restore.sql to be generated), §5 Promotion candidates flagged for meta-prep (any patterns spotted in this company that should be batch-promoted by B4-promotion). Discord ping user with plan path. WRITES NOTHING TO DB. AC: plan markdown exists; §2 has >=1 row per archive candidate; §3 skeleton renders; §5 lists 0+ candidates.

#### T-P0-814: [KG-INT B4a-meta] Meta dry-run: archive plan + causal-proof matrix
- **Priority**: P0
- **Complexity**: L
- **Depends on**: T-P1-798, T-P1-799, T-P1-800, T-P1-801, T-P1-802, T-P1-803, T-P1-804, T-P1-805, T-P1-806, T-P1-807
- **Description**: Per docs/workflow/company_internalization_protocol.md, dry-run for Meta. Read all 6 note-surfaces for company_id=see audit B1, produce docs/archive_plans/B4a-meta_2026-05-10.md with §1 Inventory snapshot (byte counts + first 200 chars per surface), §2 Migration matrix (per-row 4-tuple: 原 prose 摘要 / 原覆盖 / 现迁移到 (kg/db/cd/sd URI) / 可验证查询), §3 Skeleton preview (full markdown of replacement thin drawer-link doc), §4 Hard-archive checklist (DB DELETE rows + UPDATE clears + seed-script moves + INSERT-statement restore.sql to be generated), §5 Promotion candidates flagged for meta-prep (any patterns spotted in this company that should be batch-promoted by B4-promotion). Discord ping user with plan path. WRITES NOTHING TO DB. AC: plan markdown exists; §2 has >=1 row per archive candidate; §3 skeleton renders; §5 lists 0+ candidates.

#### T-P0-822: [KG-INT B4b-google] Google execute: hard-archive + skeleton seed + acceptance proof
- **Priority**: P0
- **Complexity**: L
- **Depends on**: T-P0-808
- **Description**: EXECUTE (after manual unblock following user 👍 on docs/archive_plans/B4a-google_2026-05-10.md). Steps: (1) generate archive/company_internalized/B4a-google_2026-05-10_restore.sql with INSERT statements for every row to be deleted, (2) write full prose dump to archive/company_internalized/B4a-google_2026-05-10.md, (3) move source seed scripts (scripts/seed_google_*.py / scripts/content_*google*.py / scripts/patch_google_*.py) -> archive/seed_scripts/B4a-google/, (4) DELETE rows per §4 plan, (5) author NEW seed scripts/seed_google_drawer_index.py for the thin skeleton doc and run it (Invariant 3 compliance), (6) run scripts/audit_uri_consistency.py and assert exit 0, (7) execute the §2 'verifiable queries' and capture output as PROGRESS acceptance proof. Idempotent (re-runs detect already-archived state and no-op). AC: all 7 steps pass; PROGRESS entry includes verifiable-query outputs; UI loads / company page without dangling refs.

#### T-P0-823: [KG-INT B4b-lyra] Lyra execute: hard-archive + skeleton seed + acceptance proof
- **Priority**: P0
- **Complexity**: M
- **Depends on**: T-P0-809, T-P0-822
- **Description**: EXECUTE (after manual unblock following user 👍 on docs/archive_plans/B4a-lyra_2026-05-10.md). Steps: (1) generate archive/company_internalized/B4a-lyra_2026-05-10_restore.sql with INSERT statements for every row to be deleted, (2) write full prose dump to archive/company_internalized/B4a-lyra_2026-05-10.md, (3) move source seed scripts (scripts/seed_lyra_*.py / scripts/content_*lyra*.py / scripts/patch_lyra_*.py) -> archive/seed_scripts/B4a-lyra/, (4) DELETE rows per §4 plan, (5) author NEW seed scripts/seed_lyra_drawer_index.py for the thin skeleton doc and run it (Invariant 3 compliance), (6) run scripts/audit_uri_consistency.py and assert exit 0, (7) execute the §2 'verifiable queries' and capture output as PROGRESS acceptance proof. Idempotent (re-runs detect already-archived state and no-op). AC: all 7 steps pass; PROGRESS entry includes verifiable-query outputs; UI loads / company page without dangling refs.

#### T-P0-824: [KG-INT B4b-pinterest-toc] Pinterest-TOC execute: hard-archive + skeleton seed + acceptance proof
- **Priority**: P0
- **Complexity**: M
- **Depends on**: T-P0-810, T-P0-823
- **Description**: EXECUTE (after manual unblock following user 👍 on docs/archive_plans/B4a-pinterest-toc_2026-05-10.md). Steps: (1) generate archive/company_internalized/B4a-pinterest-toc_2026-05-10_restore.sql with INSERT statements for every row to be deleted, (2) write full prose dump to archive/company_internalized/B4a-pinterest-toc_2026-05-10.md, (3) move source seed scripts (scripts/seed_pinterest_toc_*.py / scripts/content_*pinterest_toc*.py / scripts/patch_pinterest_toc_*.py) -> archive/seed_scripts/B4a-pinterest-toc/, (4) DELETE rows per §4 plan, (5) author NEW seed scripts/seed_pinterest_toc_drawer_index.py for the thin skeleton doc and run it (Invariant 3 compliance), (6) run scripts/audit_uri_consistency.py and assert exit 0, (7) execute the §2 'verifiable queries' and capture output as PROGRESS acceptance proof. Idempotent (re-runs detect already-archived state and no-op). AC: all 7 steps pass; PROGRESS entry includes verifiable-query outputs; UI loads / company page without dangling refs.

#### T-P0-825: [KG-INT B4b-pinterest-concepts] Pinterest-CONCEPTS execute: hard-archive + skeleton seed + acceptance proof
- **Priority**: P0
- **Complexity**: L
- **Depends on**: T-P0-811, T-P0-824
- **Description**: EXECUTE (after manual unblock following user 👍 on docs/archive_plans/B4a-pinterest-concepts_2026-05-10.md). Steps: (1) generate archive/company_internalized/B4a-pinterest-concepts_2026-05-10_restore.sql with INSERT statements for every row to be deleted, (2) write full prose dump to archive/company_internalized/B4a-pinterest-concepts_2026-05-10.md, (3) move source seed scripts (scripts/seed_pinterest_concepts_*.py / scripts/content_*pinterest_concepts*.py / scripts/patch_pinterest_concepts_*.py) -> archive/seed_scripts/B4a-pinterest-concepts/, (4) DELETE rows per §4 plan, (5) author NEW seed scripts/seed_pinterest_concepts_drawer_index.py for the thin skeleton doc and run it (Invariant 3 compliance), (6) run scripts/audit_uri_consistency.py and assert exit 0, (7) execute the §2 'verifiable queries' and capture output as PROGRESS acceptance proof. Idempotent (re-runs detect already-archived state and no-op). AC: all 7 steps pass; PROGRESS entry includes verifiable-query outputs; UI loads / company page without dangling refs.

#### T-P0-826: [KG-INT B4b-pinterest-prep] Pinterest-prep execute: hard-archive + skeleton seed + acceptance proof
- **Priority**: P0
- **Complexity**: M
- **Depends on**: T-P0-812, T-P0-825
- **Description**: EXECUTE (after manual unblock following user 👍 on docs/archive_plans/B4a-pinterest-prep_2026-05-10.md). Steps: (1) generate archive/company_internalized/B4a-pinterest-prep_2026-05-10_restore.sql with INSERT statements for every row to be deleted, (2) write full prose dump to archive/company_internalized/B4a-pinterest-prep_2026-05-10.md, (3) move source seed scripts (scripts/seed_pinterest_prep_*.py / scripts/content_*pinterest_prep*.py / scripts/patch_pinterest_prep_*.py) -> archive/seed_scripts/B4a-pinterest-prep/, (4) DELETE rows per §4 plan, (5) author NEW seed scripts/seed_pinterest_prep_drawer_index.py for the thin skeleton doc and run it (Invariant 3 compliance), (6) run scripts/audit_uri_consistency.py and assert exit 0, (7) execute the §2 'verifiable queries' and capture output as PROGRESS acceptance proof. Idempotent (re-runs detect already-archived state and no-op). AC: all 7 steps pass; PROGRESS entry includes verifiable-query outputs; UI loads / company page without dangling refs.

#### T-P0-827: [KG-INT B4b-uber] Uber execute: hard-archive + skeleton seed + acceptance proof
- **Priority**: P0
- **Complexity**: L
- **Depends on**: T-P0-813, T-P0-826
- **Description**: EXECUTE (after manual unblock following user 👍 on docs/archive_plans/B4a-uber_2026-05-10.md). Steps: (1) generate archive/company_internalized/B4a-uber_2026-05-10_restore.sql with INSERT statements for every row to be deleted, (2) write full prose dump to archive/company_internalized/B4a-uber_2026-05-10.md, (3) move source seed scripts (scripts/seed_uber_*.py / scripts/content_*uber*.py / scripts/patch_uber_*.py) -> archive/seed_scripts/B4a-uber/, (4) DELETE rows per §4 plan, (5) author NEW seed scripts/seed_uber_drawer_index.py for the thin skeleton doc and run it (Invariant 3 compliance), (6) run scripts/audit_uri_consistency.py and assert exit 0, (7) execute the §2 'verifiable queries' and capture output as PROGRESS acceptance proof. Idempotent (re-runs detect already-archived state and no-op). AC: all 7 steps pass; PROGRESS entry includes verifiable-query outputs; UI loads / company page without dangling refs.

#### T-P0-828: [KG-INT B4b-meta] Meta execute: hard-archive + skeleton seed + acceptance proof
- **Priority**: P0
- **Complexity**: L
- **Depends on**: T-P0-814, T-P0-827
- **Description**: EXECUTE (after manual unblock following user 👍 on docs/archive_plans/B4a-meta_2026-05-10.md). Steps: (1) generate archive/company_internalized/B4a-meta_2026-05-10_restore.sql with INSERT statements for every row to be deleted, (2) write full prose dump to archive/company_internalized/B4a-meta_2026-05-10.md, (3) move source seed scripts (scripts/seed_meta_*.py / scripts/content_*meta*.py / scripts/patch_meta_*.py) -> archive/seed_scripts/B4a-meta/, (4) DELETE rows per §4 plan, (5) author NEW seed scripts/seed_meta_drawer_index.py for the thin skeleton doc and run it (Invariant 3 compliance), (6) run scripts/audit_uri_consistency.py and assert exit 0, (7) execute the §2 'verifiable queries' and capture output as PROGRESS acceptance proof. Idempotent (re-runs detect already-archived state and no-op). AC: all 7 steps pass; PROGRESS entry includes verifiable-query outputs; UI loads / company page without dangling refs.

#### T-P1-581: [BQ-DEPTH-10] Primary-story batch: mark is_primary=1 for top 40 high-probability questions
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: From the Phase A matrix (BQ-DEPTH-01), propose the top 40 high-probability BQ questions (based on company overlap + asked-frequency intuition). For each, pick the ONE primary story.

Dependency on BQ-DEPTH-09 is through user-approved calibration style + schema, but this task can run in parallel with C2 bulk if user approves the 40 assignments upfront.

Deliverables:
- docs/bq_primary_story_assignments_20260421.md -- 40 rows with (question_id, primary_example_id, rationale)
- scripts/seed_bq_primary_flags_20260421.py -- idempotent, DB-backup-guarded
- Invariant: each question has exactly one is_primary=1 link (trigger or pre-check)

AC:
- User reviews 40 assignments on Discord BEFORE DB write
- Script re-runs with [SKIP]
- SELECT question_id, COUNT(*) FROM question_example_links WHERE is_primary=1 GROUP BY question_id HAVING COUNT(*) > 1 returns empty
- 40 questions have is_primary=1 set; other questions left at is_primary=0 until later batch

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

#### T-P1-627: Add display_label short field to principle_tags so pills show short labels (full phrase in tooltip)
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Follow-up to T-P0-626. Pill UI primitive is for short labels; commit e52d568 (2026-04-23) put 33-char-avg phrases in principle_tags. T-P0-626 patches the layout to tolerate long phrases; this ticket fixes the data layer.

GATE (manual, intentional hack): status=blocked even though depends_on=None. Reason: programmatic schema has no 'not_before' field and creating a sentinel-task pattern is overhead for one ticket. Description-only soft gates are insufficient because the autonomous orchestrator's task picker reads only DB fields. Therefore status=blocked is the load-bearing gate. Re-open by manually flipping to active.

UNGATE WHEN: All Uber final-round interviews complete (last is May 4 Coding 2 with Ali Shameli). Manually run: `task_db.py update T-P1-627 --status active`. Re-launch autonomous_run.sh; the orchestrator will then pick this up.

Approach (when ungated):
- Add 'display_label' (~12 chars) to principle_tags source-of-truth seed
- Backend exposes both slug and display_label
- Frontend pills render display_label; tooltip shows full phrase
- Tags missing display_label fall back to label or auto-truncate

AC:
- All 8 EX-01 principle_tags have hand-crafted display_label
- Pills show short labels; tooltip on hover shows full phrase
- T-P0-626's _-to-space rendering becomes unnecessary once this ships

Scope: backend schema + router + frontend pill rendering + seed. M complexity.

#### T-P1-641: [CHEATSHEET-1] Schema + API: add cheat_sheet TEXT column to system_designs, expose in /system-designs/:slug
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Add nullable TEXT column 'cheat_sheet' to system_designs SQLAlchemy model + Alembic-style migration script (scripts/migrate_add_cheat_sheet.py). Update SystemDesign Pydantic schema (read + update) + frontend types/system-design.ts to include cheat_sheet field. Wire into useSystemDesignNotes if edit support is wanted (defer if too big -- read-only is fine for v1). AC: (1) ALTER TABLE migration is idempotent (IF NOT EXISTS / try-except); (2) GET /system-designs/<slug> response includes cheat_sheet (null when empty); (3) GET /system-designs (list endpoint) returns cheat_sheet too so the new tab can render without per-row fetch -- or keep list lean and have new tab call /system-designs/cheat-sheets aggregation endpoint, decide based on payload size; (4) backend tests added; (5) ruff/mypy clean. NO content authoring in this task -- column stays null.

#### T-P1-642: [CHEATSHEET-2] Frontend: add 'Cheat Sheet' tab to /system-design with one-pager card per row
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-641
- **Description**: Add third tab 'Cheat Sheet' to SystemDesignList.tsx alongside 'Interview Prep' and 'eBay Projects'. New tab renders a vertically-stacked single-page list (NOT a grid) of all system_designs entries sorted by display_order. Each entry is a CheatSheetCard component:  (a) sticky-position H2 with title + small badge for category (eBay / Pinterest / Generic / Uber); (b) MarkdownPreview of the cheat_sheet field (so code-fence ascii arch + tables render correctly with KaTeX + GFM); (c) right-edge link 'Full design ->' to /system-design/<slug>; (d) graceful empty state when cheat_sheet is null ('No cheat sheet yet'). Add ?tab=cheatsheet URL synchronization (same pattern as existing tabs). Add a left-side sticky TOC sidebar within the cheat-sheet tab (desktop only) listing all cards by title for quick jump. AC includes a manual smoke test: open /system-design?tab=cheatsheet, verify 35+ cards render, KaTeX formulas render, no console errors, deep-link to ?tab=cheatsheet#<slug> scrolls to that card. Vitest snapshot for the new component.

#### T-P1-643: [CHEATSHEET-3] Add 2 Uber rows to system_designs from doc 85 (Restaurant Rec + Budget-Constrained Promo)
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-641
- **Description**: Currently Uber Eats Restaurant Recommendation and Budget-Constrained Promo Recommendation only live inside company_documents id=85 (markdown doc). Promote them to first-class system_designs rows so they appear on /system-design page and the new Cheat Sheet tab.  Steps: (1) Create scripts/seed_uber_system_designs.py (idempotent -- upsert by slug); (2) extract content from doc 85 sections 1.x and 2.x into the corresponding system_designs columns (overview, architecture, dataflow, formulas, production_constraints, tradeoffs, defense, verbal_outline) -- DO NOT duplicate, KEEP doc 85 as the canonical narrative source and treat system_designs as the structured projection; (3) slugs: 'uber-eats-restaurant-rec' (display_order 200), 'uber-budget-promo-rec' (display_order 201); (4) populate cheat_sheet field directly from §1.6 and §2.11 (the existing one-pager sections) -- this is the ONLY content authoring in this task; (5) frontend: TOPIC_META in SystemDesignList.tsx may need a new 'Uber' category (or put under 'Specialized'). AC: backend GET /system-designs returns the 2 new rows; clicking renders the existing detail page UI with no errors; doc 85 is unchanged.

#### T-P1-644: [CHEATSHEET-4] Author cheat-sheets for 4 eBay projects (display_order 1-4)
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-641
- **Description**: Slugs: module-arbitration, llm-orchestration, pbe-pipeline, ranking-allocation. Source each cheat sheet from the existing system_designs.{overview,architecture,dataflow,formulas,production_constraints,tradeoffs,defense,verbal_outline} columns -- do NOT invent new content, distill from what is already there. Format MUST match doc 85 §1.6: (a) code-fence vertical pseudo-arch; (b) keywords block (bold industry jargon); (c) Senior signal table (不及格 vs Staff Golden); (d) mini jargon glossary. Length budget: ~2000 chars per cheat sheet. Write to cheat_sheet column via idempotent seed script scripts/seed_cheat_sheets_ebay_projects.py (upsert by slug, only update if content_hash differs). AC: 4 rows have non-null cheat_sheet; markdown lints; KaTeX renders if formulas used; vitest of CheatSheetCard with one of these 4 as fixture passes.

#### T-P1-645: [CHEATSHEET-5] Author cheat-sheets for 4 eBay reference docs (display_order 5-8)
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-641
- **Description**: Slugs: database-comparison, distributed-task-queue, vibe-code-engineering-patterns, ml-system-design-patterns. These are reference / pattern docs not single design problems, so the cheat sheet format adapts: (a) for database-comparison -- side-by-side decision matrix (workload -> recommended store) instead of vertical pseudo-arch; (b) for distributed-task-queue -- failure-mode table + idempotency strategy keywords; (c) for vibe-code -- pattern bullet-list with one-line trade-off each; (d) for ml-sd-patterns -- the cross-cutting senior signals from doc 85 §3 are a strong template, mirror that style. Same length budget (~2000 chars), same idempotent seed pattern (scripts/seed_cheat_sheets_ebay_refs.py). AC: 4 rows have non-null cheat_sheet; rendered cards visually distinct from project cards (badge color differs).

#### T-P1-646: [CHEATSHEET-6] Author cheat-sheets for 7 Pinterest ML problems
- **Priority**: P1
- **Complexity**: L
- **Depends on**: T-P1-641
- **Description**: Slugs: pinterest-ad-ctr, pinterest-embeddings, pinterest-chatbot-pins, pinterest-pin-ranking, pinterest-pins-search, pinterest-notification-reco, pinterest-catalog-bulk-update. Source from existing system_designs columns AND from any company_documents rows where company.slug='pinterest' and the doc maps to one of these 7 problems (cross-reference by title). Format MUST match doc 85 §1.6 -- vertical pseudo-arch + keywords + senior table + mini glossary. Pinterest-specific jargon to call out: PinSage, GraphSAGE, two-tower, Galaxy item embeddings, Pixie random walk, AutoML reranker -- expand each acronym in the glossary. Idempotent seed: scripts/seed_cheat_sheets_pinterest.py. Length budget per card ~2000 chars. AC: all 7 rows have non-null cheat_sheet; the vibe-code-style 'badge' on the card reads 'Pinterest'; manual smoke test on /system-design?tab=cheatsheet shows them grouped together visually.

#### T-P1-647: [CHEATSHEET-7] Author cheat-sheets for 10 generic SD problems (batch 1: Core Infra + Social/Real-time + Geo)
- **Priority**: P1
- **Complexity**: L
- **Depends on**: T-P1-641
- **Description**: Batch 1 slugs: interview-url-shortener, interview-rate-limiter, interview-distributed-cache, interview-notification-system, interview-news-feed, interview-chat-system, interview-live-comments, interview-game-leaderboard, interview-ride-sharing, interview-proximity-service. Format per doc 85 §1.6 (vertical pseudo-arch + keywords + senior table + mini glossary). Source from existing system_designs columns. Length ~1500 chars (these are interview-prep concise cards, slightly tighter than the eBay project cards). Idempotent seed: scripts/seed_cheat_sheets_generic_sd_batch1.py. AC: 10 rows have non-null cheat_sheet; ruff/mypy clean; vitest passes.

#### T-P1-648: [CHEATSHEET-8] Author cheat-sheets for 9 generic SD problems (batch 2: Search/Data + Storage/Media + Specialized)
- **Priority**: P1
- **Complexity**: L
- **Depends on**: T-P1-641
- **Description**: Batch 2 slugs: interview-search-autocomplete, interview-top-k-heavy-hitters, interview-ad-click-aggregator, interview-web-crawler, interview-video-streaming, interview-cloud-storage, interview-price-drop-tracker, interview-online-judge, interview-ticket-reservation, interview-auction-system. (10 slugs total -- batch 2 takes the remainder.) Same format as batch 1 (~1500 chars, doc 85 §1.6 style, idempotent seed scripts/seed_cheat_sheets_generic_sd_batch2.py). AC: every interview-* row in system_designs has non-null cheat_sheet after this task lands.

#### T-P1-649: [CHEATSHEET-9] Smoke test: load /system-design?tab=cheatsheet, verify all 37 cards render, no console errors
- **Priority**: P1
- **Complexity**: S
- **Depends on**: T-P1-648
- **Description**: Final integration smoke test (manual + automated): (1) start dev server (npm run dev + uvicorn); (2) navigate to http://localhost:5173/system-design?tab=cheatsheet; (3) verify ALL rows in system_designs have a rendered card (count == row count); (4) zero console errors; (5) KaTeX formulas render where present; (6) deep-link with #<slug> hash scrolls correctly; (7) prev/next nav still works on detail pages; (8) Interview Prep + eBay Projects tabs still render unchanged (regression check). Append a screenshot or text-only confirmation to PROGRESS.md. Add a vitest E2E-ish test that mounts SystemDesignList and asserts all 3 tabs render their expected card count. AC: all 8 verification points pass; no regression in existing tabs.

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

#### T-P1-815: [KG-INT B4a-adobe] Adobe dry-run: archive plan + causal-proof matrix
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-798, T-P1-799, T-P1-800, T-P1-801, T-P1-802, T-P1-803, T-P1-804, T-P1-805, T-P1-806, T-P1-807
- **Description**: Per docs/workflow/company_internalization_protocol.md, dry-run for Adobe. Read all 6 note-surfaces for company_id=see audit B1, produce docs/archive_plans/B4a-adobe_2026-05-10.md with §1 Inventory snapshot (byte counts + first 200 chars per surface), §2 Migration matrix (per-row 4-tuple: 原 prose 摘要 / 原覆盖 / 现迁移到 (kg/db/cd/sd URI) / 可验证查询), §3 Skeleton preview (full markdown of replacement thin drawer-link doc), §4 Hard-archive checklist (DB DELETE rows + UPDATE clears + seed-script moves + INSERT-statement restore.sql to be generated), §5 Promotion candidates flagged for meta-prep (any patterns spotted in this company that should be batch-promoted by B4-promotion). Discord ping user with plan path. WRITES NOTHING TO DB. AC: plan markdown exists; §2 has >=1 row per archive candidate; §3 skeleton renders; §5 lists 0+ candidates.

#### T-P1-816: [KG-INT B4a-linkedin] LinkedIn dry-run: archive plan + causal-proof matrix
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-798, T-P1-799, T-P1-800, T-P1-801, T-P1-802, T-P1-803, T-P1-804, T-P1-805, T-P1-806, T-P1-807
- **Description**: Per docs/workflow/company_internalization_protocol.md, dry-run for LinkedIn. Read all 6 note-surfaces for company_id=see audit B1, produce docs/archive_plans/B4a-linkedin_2026-05-10.md with §1 Inventory snapshot (byte counts + first 200 chars per surface), §2 Migration matrix (per-row 4-tuple: 原 prose 摘要 / 原覆盖 / 现迁移到 (kg/db/cd/sd URI) / 可验证查询), §3 Skeleton preview (full markdown of replacement thin drawer-link doc), §4 Hard-archive checklist (DB DELETE rows + UPDATE clears + seed-script moves + INSERT-statement restore.sql to be generated), §5 Promotion candidates flagged for meta-prep (any patterns spotted in this company that should be batch-promoted by B4-promotion). Discord ping user with plan path. WRITES NOTHING TO DB. AC: plan markdown exists; §2 has >=1 row per archive candidate; §3 skeleton renders; §5 lists 0+ candidates.

#### T-P1-817: [KG-INT B4a-tiktok] TikTok dry-run: archive plan + causal-proof matrix
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-798, T-P1-799, T-P1-800, T-P1-801, T-P1-802, T-P1-803, T-P1-804, T-P1-805, T-P1-806, T-P1-807
- **Description**: Per docs/workflow/company_internalization_protocol.md, dry-run for TikTok. Read all 6 note-surfaces for company_id=see audit B1, produce docs/archive_plans/B4a-tiktok_2026-05-10.md with §1 Inventory snapshot (byte counts + first 200 chars per surface), §2 Migration matrix (per-row 4-tuple: 原 prose 摘要 / 原覆盖 / 现迁移到 (kg/db/cd/sd URI) / 可验证查询), §3 Skeleton preview (full markdown of replacement thin drawer-link doc), §4 Hard-archive checklist (DB DELETE rows + UPDATE clears + seed-script moves + INSERT-statement restore.sql to be generated), §5 Promotion candidates flagged for meta-prep (any patterns spotted in this company that should be batch-promoted by B4-promotion). Discord ping user with plan path. WRITES NOTHING TO DB. AC: plan markdown exists; §2 has >=1 row per archive candidate; §3 skeleton renders; §5 lists 0+ candidates.

#### T-P1-818: [KG-INT B4a-slack] Slack dry-run: archive plan + causal-proof matrix
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-798, T-P1-799, T-P1-800, T-P1-801, T-P1-802, T-P1-803, T-P1-804, T-P1-805, T-P1-806, T-P1-807
- **Description**: Per docs/workflow/company_internalization_protocol.md, dry-run for Slack. Read all 6 note-surfaces for company_id=see audit B1, produce docs/archive_plans/B4a-slack_2026-05-10.md with §1 Inventory snapshot (byte counts + first 200 chars per surface), §2 Migration matrix (per-row 4-tuple: 原 prose 摘要 / 原覆盖 / 现迁移到 (kg/db/cd/sd URI) / 可验证查询), §3 Skeleton preview (full markdown of replacement thin drawer-link doc), §4 Hard-archive checklist (DB DELETE rows + UPDATE clears + seed-script moves + INSERT-statement restore.sql to be generated), §5 Promotion candidates flagged for meta-prep (any patterns spotted in this company that should be batch-promoted by B4-promotion). Discord ping user with plan path. WRITES NOTHING TO DB. AC: plan markdown exists; §2 has >=1 row per archive candidate; §3 skeleton renders; §5 lists 0+ candidates.

#### T-P1-819: [KG-INT B4a-doordash] DoorDash dry-run: archive plan + causal-proof matrix
- **Priority**: P1
- **Complexity**: S
- **Depends on**: T-P1-798, T-P1-799, T-P1-800, T-P1-801, T-P1-802, T-P1-803, T-P1-804, T-P1-805, T-P1-806, T-P1-807
- **Description**: Per docs/workflow/company_internalization_protocol.md, dry-run for DoorDash. Read all 6 note-surfaces for company_id=see audit B1, produce docs/archive_plans/B4a-doordash_2026-05-10.md with §1 Inventory snapshot (byte counts + first 200 chars per surface), §2 Migration matrix (per-row 4-tuple: 原 prose 摘要 / 原覆盖 / 现迁移到 (kg/db/cd/sd URI) / 可验证查询), §3 Skeleton preview (full markdown of replacement thin drawer-link doc), §4 Hard-archive checklist (DB DELETE rows + UPDATE clears + seed-script moves + INSERT-statement restore.sql to be generated), §5 Promotion candidates flagged for meta-prep (any patterns spotted in this company that should be batch-promoted by B4-promotion). Discord ping user with plan path. WRITES NOTHING TO DB. AC: plan markdown exists; §2 has >=1 row per archive candidate; §3 skeleton renders; §5 lists 0+ candidates.

#### T-P1-820: [KG-INT B4a-parspec] PARSPEC dry-run: archive plan + causal-proof matrix
- **Priority**: P1
- **Complexity**: S
- **Depends on**: T-P1-798, T-P1-799, T-P1-800, T-P1-801, T-P1-802, T-P1-803, T-P1-804, T-P1-805, T-P1-806, T-P1-807
- **Description**: Per docs/workflow/company_internalization_protocol.md, dry-run for PARSPEC. Read all 6 note-surfaces for company_id=see audit B1, produce docs/archive_plans/B4a-parspec_2026-05-10.md with §1 Inventory snapshot (byte counts + first 200 chars per surface), §2 Migration matrix (per-row 4-tuple: 原 prose 摘要 / 原覆盖 / 现迁移到 (kg/db/cd/sd URI) / 可验证查询), §3 Skeleton preview (full markdown of replacement thin drawer-link doc), §4 Hard-archive checklist (DB DELETE rows + UPDATE clears + seed-script moves + INSERT-statement restore.sql to be generated), §5 Promotion candidates flagged for meta-prep (any patterns spotted in this company that should be batch-promoted by B4-promotion). Discord ping user with plan path. WRITES NOTHING TO DB. AC: plan markdown exists; §2 has >=1 row per archive candidate; §3 skeleton renders; §5 lists 0+ candidates.

#### T-P1-829: [KG-INT B4b-adobe] Adobe execute: hard-archive + skeleton seed + acceptance proof
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-815, T-P0-828
- **Description**: EXECUTE (after manual unblock following user 👍 on docs/archive_plans/B4a-adobe_2026-05-10.md). Steps: (1) generate archive/company_internalized/B4a-adobe_2026-05-10_restore.sql with INSERT statements for every row to be deleted, (2) write full prose dump to archive/company_internalized/B4a-adobe_2026-05-10.md, (3) move source seed scripts (scripts/seed_adobe_*.py / scripts/content_*adobe*.py / scripts/patch_adobe_*.py) -> archive/seed_scripts/B4a-adobe/, (4) DELETE rows per §4 plan, (5) author NEW seed scripts/seed_adobe_drawer_index.py for the thin skeleton doc and run it (Invariant 3 compliance), (6) run scripts/audit_uri_consistency.py and assert exit 0, (7) execute the §2 'verifiable queries' and capture output as PROGRESS acceptance proof. Idempotent (re-runs detect already-archived state and no-op). AC: all 7 steps pass; PROGRESS entry includes verifiable-query outputs; UI loads / company page without dangling refs.

#### T-P1-830: [KG-INT B4b-linkedin] LinkedIn execute: hard-archive + skeleton seed + acceptance proof
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-816, T-P1-829
- **Description**: EXECUTE (after manual unblock following user 👍 on docs/archive_plans/B4a-linkedin_2026-05-10.md). Steps: (1) generate archive/company_internalized/B4a-linkedin_2026-05-10_restore.sql with INSERT statements for every row to be deleted, (2) write full prose dump to archive/company_internalized/B4a-linkedin_2026-05-10.md, (3) move source seed scripts (scripts/seed_linkedin_*.py / scripts/content_*linkedin*.py / scripts/patch_linkedin_*.py) -> archive/seed_scripts/B4a-linkedin/, (4) DELETE rows per §4 plan, (5) author NEW seed scripts/seed_linkedin_drawer_index.py for the thin skeleton doc and run it (Invariant 3 compliance), (6) run scripts/audit_uri_consistency.py and assert exit 0, (7) execute the §2 'verifiable queries' and capture output as PROGRESS acceptance proof. Idempotent (re-runs detect already-archived state and no-op). AC: all 7 steps pass; PROGRESS entry includes verifiable-query outputs; UI loads / company page without dangling refs.

#### T-P1-831: [KG-INT B4b-tiktok] TikTok execute: hard-archive + skeleton seed + acceptance proof
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-817, T-P1-830
- **Description**: EXECUTE (after manual unblock following user 👍 on docs/archive_plans/B4a-tiktok_2026-05-10.md). Steps: (1) generate archive/company_internalized/B4a-tiktok_2026-05-10_restore.sql with INSERT statements for every row to be deleted, (2) write full prose dump to archive/company_internalized/B4a-tiktok_2026-05-10.md, (3) move source seed scripts (scripts/seed_tiktok_*.py / scripts/content_*tiktok*.py / scripts/patch_tiktok_*.py) -> archive/seed_scripts/B4a-tiktok/, (4) DELETE rows per §4 plan, (5) author NEW seed scripts/seed_tiktok_drawer_index.py for the thin skeleton doc and run it (Invariant 3 compliance), (6) run scripts/audit_uri_consistency.py and assert exit 0, (7) execute the §2 'verifiable queries' and capture output as PROGRESS acceptance proof. Idempotent (re-runs detect already-archived state and no-op). AC: all 7 steps pass; PROGRESS entry includes verifiable-query outputs; UI loads / company page without dangling refs.

#### T-P1-832: [KG-INT B4b-slack] Slack execute: hard-archive + skeleton seed + acceptance proof
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-818, T-P1-831
- **Description**: EXECUTE (after manual unblock following user 👍 on docs/archive_plans/B4a-slack_2026-05-10.md). Steps: (1) generate archive/company_internalized/B4a-slack_2026-05-10_restore.sql with INSERT statements for every row to be deleted, (2) write full prose dump to archive/company_internalized/B4a-slack_2026-05-10.md, (3) move source seed scripts (scripts/seed_slack_*.py / scripts/content_*slack*.py / scripts/patch_slack_*.py) -> archive/seed_scripts/B4a-slack/, (4) DELETE rows per §4 plan, (5) author NEW seed scripts/seed_slack_drawer_index.py for the thin skeleton doc and run it (Invariant 3 compliance), (6) run scripts/audit_uri_consistency.py and assert exit 0, (7) execute the §2 'verifiable queries' and capture output as PROGRESS acceptance proof. Idempotent (re-runs detect already-archived state and no-op). AC: all 7 steps pass; PROGRESS entry includes verifiable-query outputs; UI loads / company page without dangling refs.

#### T-P1-833: [KG-INT B4b-doordash] DoorDash execute: hard-archive + skeleton seed + acceptance proof
- **Priority**: P1
- **Complexity**: S
- **Depends on**: T-P1-819, T-P1-832
- **Description**: EXECUTE (after manual unblock following user 👍 on docs/archive_plans/B4a-doordash_2026-05-10.md). Steps: (1) generate archive/company_internalized/B4a-doordash_2026-05-10_restore.sql with INSERT statements for every row to be deleted, (2) write full prose dump to archive/company_internalized/B4a-doordash_2026-05-10.md, (3) move source seed scripts (scripts/seed_doordash_*.py / scripts/content_*doordash*.py / scripts/patch_doordash_*.py) -> archive/seed_scripts/B4a-doordash/, (4) DELETE rows per §4 plan, (5) author NEW seed scripts/seed_doordash_drawer_index.py for the thin skeleton doc and run it (Invariant 3 compliance), (6) run scripts/audit_uri_consistency.py and assert exit 0, (7) execute the §2 'verifiable queries' and capture output as PROGRESS acceptance proof. Idempotent (re-runs detect already-archived state and no-op). AC: all 7 steps pass; PROGRESS entry includes verifiable-query outputs; UI loads / company page without dangling refs.

#### T-P1-834: [KG-INT B4b-parspec] PARSPEC execute: hard-archive + skeleton seed + acceptance proof
- **Priority**: P1
- **Complexity**: S
- **Depends on**: T-P1-820, T-P1-833
- **Description**: EXECUTE (after manual unblock following user 👍 on docs/archive_plans/B4a-parspec_2026-05-10.md). Steps: (1) generate archive/company_internalized/B4a-parspec_2026-05-10_restore.sql with INSERT statements for every row to be deleted, (2) write full prose dump to archive/company_internalized/B4a-parspec_2026-05-10.md, (3) move source seed scripts (scripts/seed_parspec_*.py / scripts/content_*parspec*.py / scripts/patch_parspec_*.py) -> archive/seed_scripts/B4a-parspec/, (4) DELETE rows per §4 plan, (5) author NEW seed scripts/seed_parspec_drawer_index.py for the thin skeleton doc and run it (Invariant 3 compliance), (6) run scripts/audit_uri_consistency.py and assert exit 0, (7) execute the §2 'verifiable queries' and capture output as PROGRESS acceptance proof. Idempotent (re-runs detect already-archived state and no-op). AC: all 7 steps pass; PROGRESS entry includes verifiable-query outputs; UI loads / company page without dangling refs.

#### T-P2-207: [SYNC] Remove deprecated stop-cache from helixos + template test_check.py
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: Remove deprecated stop-cache from BOTH helixos/.claude/hooks/test_check.py AND claude-code-project-template/.claude/hooks/test_check.py. Both still import and use check_stop_cache/write_stop_cache from hook_utils. MLInterviewPrep already removed these (T-P2-188, commit abf6543) per the lesson that stop caches cause false PASS results when files change between sessions.

Verified state (2026-04-23): helixos/.claude/hooks/test_check.py lines 10, 21, 48 still import/call check_stop_cache/write_stop_cache. claude-code-project-template/.claude/hooks/test_check.py same three lines.

Action:
1. helixos/.claude/hooks/test_check.py: remove cache import and calls -- copy MLInterviewPrep version.
2. claude-code-project-template/.claude/hooks/test_check.py: same removal.
3. Clean up hook_utils.py in both repos only if no other callers remain.
4. Run tests after to confirm hook still works.

Consolidated from duplicates: T-P2-255, T-P2-320 (both helixos stop-cache), T-P2-208 (template stop-cache). All 3 marked completed-as-duplicate on 2026-04-23 per T-P2-587.

Blocked: must be executed from a helixos or template Claude Code session -- file permissions prevent writing to those repos' .claude/hooks/ from a MLInterviewPrep session.

Source: MLInterviewPrep/.claude/hooks/test_check.py (cache-free reference).

#### T-P2-239: [SYNC] Propagate session_context.py improvements from MLInterviewPrep to helixos
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: MLInterviewPrep session_context.py has two improvements over helixos version: (1) Extracted _get_completed_task_ids() as a named helper function instead of inline code. (2) Added fresh-clone DB missing warning: if .claude/tasks.db is missing but TASKS.md has tasks, warn user to run `python .claude/hooks/task_db.py import`. Apply both changes to helixos/.claude/hooks/session_context.py.

#### T-P2-636: [UBER-VO-5b POST-5/4] Bespoke pages/UberIndex.tsx with 5-tab charter switcher (deferred)
- **Priority**: P2
- **Complexity**: L
- **Depends on**: None
- **Description**: ## Status: DEFERRED post-2026-05-04 per critical review
This is the original T-P0-632 scope (bespoke React page + URL state + drawer state + browser back/forward + accessibility + vitest). Moved out of the 5/4-readiness critical path. Pick up only if the T-P0-632 MVP (id=37 patch) proves insufficient during actual prep usage.

## Trigger to re-prioritize
- I find myself navigating id=37 -> Round 2 -> click link -> target doc -> back button -> click another link, repeatedly, and the friction matters.
- Or: a follow-up Uber recruiter loop schedules another VO requiring deeper navigation.

## Goal (preserved from original plan)
A bespoke \`pages/UberIndex.tsx\` route at \`/companies/uber/index\` mirroring \`pages/QuickIndex.tsx\` pattern: 5 tab pills (LC / ML Coding / ML SD / Behavioral / HR), per-tab card grid, click-to-drawer, URL state, browser back/forward, empty-state copy, ARIA accessibility, vitest coverage.

## Locked decisions inherited from MVP
- Drawer type: SlideOverPanel via existing \`db://N#anchor\` convention (with anchor support added if T-P0-632 surfaces it as missing).
- Behavioral API: \`/behavioral/themes?company=uber\`.
- Implementation Option A: bespoke page (NOT generalize QuickIndex).

## Acceptance criteria (from original T-P0-632)
- All 5 tabs render correct content with stable URL state.
- Card click opens SlideOverPanel with anchor-scroll.
- Browser back/forward preserves tab+drawer state.
- Empty state for charters lacking content.
- Accessibility: role=tab, ARIA-controls, keyboard arrow nav.
- Vitest tab-switch + drawer-open + empty-state.
- No emoji.

## Dependencies
Upstream: T-P0-632 (MVP must ship first; if MVP suffices, this task closes as 'skipped').

#### T-P2-716: [AR-17] Placeholder ticket: PostToolUse heartbeat as fallback if AR-12 porcelain signal proves insufficient
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: **Status**: PLACEHOLDER ONLY. Do NOT implement until trigger condition met.

**Trigger condition** (do not start work until this is observed):
- AR-12 (T-P1-713) has been live for >= 1 week with telemetry collected.
- `logs/wrapper-stats.jsonl` analysis shows AR-12 false-negative rate > 10% (i.e., wrapper false-killed sessions where Claude was working in stdout but had not yet touched working tree -- e.g., stuck in a long Read/Bash loop without an Edit).
- OR user reports a specific failure mode that AR-12's porcelain signal did not catch.

**Goal (when triggered)**: Implement a finer-grained progress signal via PostToolUse hook. Hook writes a heartbeat timestamp to `.claude/heartbeat` on every tool call. Wrapper polls heartbeat freshness; mtime within last N seconds = Claude is alive even if no commit / no working-tree change yet.

**Why deferred**: AR-12 + AR-16 cover the dominant failure modes (uncommitted edits + cold-start hang). Heartbeat adds complexity (hook coordination, file-system race, polling cadence) that may be unnecessary. Wait for data before adding.

**Implementation sketch (for future reference, not to be built now)**:
1. Add PostToolUse hook `.claude/hooks/heartbeat.py` that touches `.claude/heartbeat` on every invocation.
2. In wrapper, on timeout, also stat `.claude/heartbeat`; if mtime within last 60s, treat as InProgress like AR-12 porcelain branch.
3. New telemetry branch: `heartbeat_only` (HEAD unchanged + porcelain unchanged + heartbeat fresh).
4. Same kill switch pattern: `CLAUDE_P_DISABLE_HEARTBEAT_SIGNAL=1`.
5. Clean up stale heartbeat at session start.

**Acceptance criteria (when triggered)**:
1. Trigger condition documented and met (telemetry data referenced).
2. Hook coordinated across MLI + root .claude/hooks/.
3. Wrapper integration parallel to AR-12.
4. Telemetry branch added.
5. Kill switch verified.

**Depends on**: T-P1-713 (AR-12) -- need its telemetry to know if AR-17 is justified.

## Completed Tasks

> 724 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-05-10** -- T-P1-796: [KG-INT A1] Backend: GET /companies returns has_meaningful_note bool. Implement composite threshold rule in src/backend/routers/companies.py: (prep_notes >= T_PREP) OR (notes >= T_NOTES AND 
- [x] **2026-05-10** -- T-P1-795: [KG-INT A0] EDA: red-dot threshold percentile distribution + recommendation. Compute P25/P50/P75/P95 of length(prep_notes), length(notes), length(company_documents.content), length(*_company_tags.n
- [x] **2026-05-06** -- T-P1-794: LC 312 Burst Balloons interval-DP notes + Google R2 index entry. Discord drop msg 1501832530905661570: classic interval DP, reverse enumeration of last balloon to burst.
- [x] **2026-05-06** -- T-P1-793: LC 496 简略题解 + Google R2 index entry (Discord 2026-05-07). Discord drop msg 1501827921680138421: simple single-solution notes for LC 496 (problems.id=299) + add to Google R2 Codin
- [x] **2026-05-06** -- T-P1-792: Custom 文件系统总大小计算 problem + Google R2 index entry (Discord 2026-05-07). Discord drop msg 1501825987753672826: tree-DFS custom problem covering澄清问题 + 4-level evolution (DFS w/ cycle detect -> s
- [x] **2026-05-06** -- T-P1-791: Custom Square Islands problem + Google R2 index entry (Discord 2026-05-07). Discord drop msg 1501824183984717895: user-provided 题解 for custom Google R2 problem 'Number of Square Islands'. INSERT n
- [x] **2026-05-06** -- T-P1-790: LC 1673 notes + Google R2 index entry (Discord 2026-05-07). Discord drop msg 1501821359590867046: per-problem notes for LC 1673 (problems.id=804) + new entry in Google R2 Coding In
