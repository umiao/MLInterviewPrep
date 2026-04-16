# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

#### T-P0-471: [KG-P1-02] Deploy doc_kind taxonomy: canonical_hub / composition / drill
- **Priority**: P0
- **Complexity**: S
- **Depends on**: None
- **Description**: Current `company_documents.doc_kind` CHECK accepts: prep_note, hub_doc, card_index. KG design calls for richer taxonomy: add 'canonical_hub', 'composition', 'drill'.

SCHEMA CHANGE:
- Relax or rebuild CHECK on doc_kind to accept: prep_note, hub_doc, card_index, canonical_hub, composition, drill.
- Use the copy-swap migration pattern already shipped (see scripts/_migrate_doc_kind_add_card_index.py as template).

BACKFILL MAPPING (after schema):
- All 11 Google R1 'Drill' docs (55,56,60,61,62,63,64,65,67,68,69) -> doc_kind='drill'
- Google 2026-04-17 Prep Hub (53) -> hub_doc (already)
- Pinterest card_index (66) -> card_index (already)
- Everything else stays prep_note until Phase 2 classifies each.

IMPLEMENTATION:
- scripts/_migrate_doc_kind_add_taxonomy_20260416.py (idempotent, copy-swap + UPDATE backfill).
- Verify reserve cost: N rows preserved.
- Update pydantic schemas / TypeScript types that enumerate doc_kind (grep for Literal['prep_note', ...] and str enums).

ACCEPTANCE CRITERIA:
1. `sqlite3 data/mle_prep.db 'SELECT DISTINCT doc_kind FROM company_documents'` includes 'drill' for 11 Google docs.
2. Re-run migration prints [UNCHANGED].
3. Backend pydantic schema accepts new kinds; API test GET /api/companies/3/documents returns 200.
4. Frontend CompanyDocument type updated.
5. npm run build passes 0 TS errors.
6. Commit: [KG-P1-02] doc_kind taxonomy: canonical_hub, composition, drill + Google R1 backfill

#### T-P0-472: [KG-P1-03] Markdown '正典' (canonical) link convention + POC patch on 2 framework_nodes
- **Priority**: P0
- **Complexity**: S
- **Depends on**: None
- **Description**: Establish canonical cross-ref syntax so future docs link to framework_nodes uniformly, enabling future scraping into concept_links table.

CONVENTION (to document in docs/protocol/kg_markdown_conventions.md):
- Canonical (one-source-of-truth pointer):
    > **正典** [Concept Title (pillar1.path.to.node)](/framework/{node_id})
- Mentions / see-also:
    > **也见** [Title](/framework/{node_id})
- Composed-of (for canonical_hub listing its components):
    - [Component Title](/framework/{node_id}) -- 一句话角色
- Prereq / follow-up: use '> **前置**' / '> **后续**' prefixes.

All canonical links MUST sit on their own markdown blockquote line (> prefix) so a future parser can extract via regex `> \*\*(正典|也见|前置|后续)\*\* \[.*?\]\(/framework/(\d+)\)`.

POC SCOPE:
1. Write the convention doc at docs/protocol/kg_markdown_conventions.md (~150 lines, with examples + anti-patterns).
2. Pick TWO existing framework_nodes that reference other nodes informally today (grep framework_nodes.description for /framework/ and '见 node' etc). Patch their description to use the new blockquote syntax. Prefer nodes where the link already exists as plain text.
3. Add unit test tests/test_kg_link_convention.py that regex-scans the two patched nodes and asserts at least one canonical-syntax link is found.

ACCEPTANCE CRITERIA:
1. docs/protocol/kg_markdown_conventions.md exists with 正典/也见/前置/后续/composed-of examples.
2. At least 2 framework_nodes patched; DB UPDATE via scripts/patch_kg_link_syntax_poc.py (idempotent, sentinel 'KG_LINK_POC_20260416').
3. Test passes.
4. Commit: [KG-P1-03] KG markdown link convention + POC patch on 2 nodes

NON-GOALS: Do NOT backfill the whole corpus; POC only. Do NOT build the scraper that populates concept_links (separate task).

#### T-P0-473: [KG-P2-01] Consolidate Bias-Variance as canonical_hub (Google doc 56 + node)
- **Priority**: P0
- **Complexity**: M
- **Depends on**: T-P0-470
- **Description**: Phase 2 first real canonical hub. Target: unify the Bias-Variance treatment into ONE framework_node as canonical authority, with Google drill doc 56 repositioned as a 'drill' that LINKS to the canonical hub (no re-derivation).

CURRENT STATE (verify before editing):
- Google company_documents id=56 'Bias-Variance + Overfitting Diagnosis Drill' = 7166 chars (Google R1 specific).
- Possible framework_nodes covering bias-variance: search framework_nodes.title / path for 'bias', 'variance', 'overfit' (you should find at least one; identify it).
- LinkedIn 合集 doc 21 has a bias-variance section (chars unknown; part of 66.8K).

AC:
1. Canonical framework_node (identified or newly created) becomes the CANONICAL authority; length 8000-12000 bytes; covers: definitions, decomposition proof sketch, diagnostic curves (train vs val as complexity rises), remedies table (high bias / high variance / both), interview pitfalls.
2. Google doc 56 rewritten as DRILL: keeps Google-specific angle (whatever that is -- read the doc first), but replaces any re-derivation with '> **正典** [Bias-Variance (pillarN.path)](/framework/{id})' pointer. Target length <=5000 chars after shrinking.
3. concept_links entries inserted (requires KG-P1-01 to be complete):
    - src=company_document:56, dst=framework_node:<id>, relation='canonical'
    - src=framework_node:<id>, dst=company_document:56, relation='drill' (reverse edge)
4. Idempotent seed script scripts/consolidate_bias_variance_20260416.py.
5. Commit: [KG-P2-01] Bias-Variance canonical hub + Google drill 56 trim

DEPENDS ON: KG-P1-01 (concept_links), KG-P1-02 (doc_kind 'drill'), KG-P1-03 (markdown convention).

#### T-P0-474: [KG-P2-02] Consolidate Regularization as second canonical_hub (extends node 195)
- **Priority**: P0
- **Complexity**: S
- **Depends on**: None
- **Description**: Phase 2 second canonical hub. User-picked (over Optimizer / Class Imbalance / Eval Metrics). Target: unify Regularization treatment into framework_node 195 as canonical authority.

CURRENT STATE (verified):
- framework_node id=195 was expanded under T-P0-220 with primal-dual KKT derivation + geometric picture. Length: 7543 chars (post-expansion).
- Legacy 合集 Doc 21 (LinkedIn 概率统计) contains L1/L2 proofs as UNIQUE sole source per audit.
- Multiple drill docs mention regularization tangentially (e.g., Google 55 Regularization Deep Dive, Doc 27 ML理论).

SCOPE:
1. Read Doc 21's L1/L2 sections + Google Doc 55 + any framework_node content touching regularization. Produce a diff analysis (what's unique, what's duplicated).
2. Absorb Doc 21 unique L1/L2 proofs into framework_node 195 (target: 10000-14000 chars; stay within drawer/always-visible budget per template v1.1).
3. Reposition Google Doc 55 as 'drill' (doc_kind='drill' via KG-P1-02 taxonomy): trim re-derivations, replace with '> **正典** [Regularization (pillarN.path)](/framework/195)'. Target: 55 shrinks from 8396 -> ~5000 chars.
4. concept_links: doc 55 -> node 195 (canonical); node 195 -> doc 55 (drill) + doc 21 (absorbed_from).
5. Archive pre-migration snapshots of doc 55 + relevant Doc 21 sections to archive/pre_kg/YYYYMMDD/.

ACCEPTANCE CRITERIA:
1. framework_node 195 length: 10000-14000 chars; covers L1 vs L2 geometric picture + KKT + soft-thresholding + probabilistic Laplace/Gaussian priors + elastic net brief + weight decay vs L2 subtlety in Adam.
2. Google Doc 55 trimmed to <=5500 chars, contains canonical pointer blockquote.
3. concept_links rows inserted (3 edges).
4. Idempotent seed: scripts/consolidate_regularization_20260416.py.
5. Commit: [KG-P2-02] Regularization canonical hub (node 195) + Google doc 55 trim + Doc 21 absorb

DEPENDS ON: KG-P1-01 (concept_links), KG-P1-02 (doc_kind), KG-P1-03 (markdown convention).

NON-GOALS: Do NOT delete Doc 21 (legacy 合集 per user: per-concept manual review only). Do NOT touch other Doc 21 sections (only the L1/L2 subsection).

#### T-P0-476: [KG-M-00] Generate per-concept coverage checklist (human review format) for 合集 docs 19/21/22/27
- **Priority**: P0
- **Complexity**: S
- **Depends on**: None
- **Description**: FIRST step of 合集 migration. Per user instruction, we do NOT auto-deprecate. Produce a per-doc, per-concept checklist so user can sign off concept-by-concept.

DELIVERABLE: docs/audits/legacy_hejiji_coverage_checklist_20260416.md with one section per doc (19, 21, 22, 27). Each concept gets:
  - Concept title
  - Status: COVERED / PARTIAL / UNIQUE
  - Where it is (or isn't) in individual framework_nodes / other docs: specific IDs
  - Proposed action: 'safe' / 'migrate to node <id>' / 'create new node'
  - Empty checkbox: [ ] User-verified migration complete
  - Empty checkbox: [ ] Signed off for deletion from this 合集

IMPLEMENTATION:
- scripts/audit_legacy_hejiji_coverage.py reads the 4 docs and queries framework_nodes + other company_documents.
- Deterministic output; re-run produces identical file.
- Use findings from prior Explore agent audit: doc 19 has 2 UNIQUE (Diffusion, RoPE); doc 21 has 4 UNIQUE (Simpson, Queueing, EM-GMM, L1-L2 proofs); doc 22 has 2 UNIQUE (LinkedIn Rec/Rank); doc 27 has 1-2 UNIQUE (Adam/RMSprop code).

ACCEPTANCE CRITERIA:
1. Output markdown file exists with 4 sections.
2. Each section lists concepts with Status + Action + 2 checkboxes.
3. Re-run produces identical file (deterministic).
4. Commit: [KG-M-00] Generate legacy 合集 coverage checklist

NON-GOALS: Do NOT delete anything. Do NOT auto-migrate. This task only produces the review artifact.

#### T-P0-477: [KG-M-01] CRITICAL: Migrate Doc 19 Diffusion Models (sole source) to framework_node + standalone
- **Priority**: P0
- **Complexity**: M
- **Depends on**: T-P0-470
- **Description**: Doc 19 'Adobe MLE Prep All-in-One' contains Diffusion Models content (DDPM, DDIM, CFG, CLIP, SDE/ODE) that prior audit flagged as SOLE SOURCE -- not found in any framework_node or other doc. Must migrate before Doc 19 is touched.

SCOPE:
1. Read Doc 19's diffusion-model section from DB (company_documents id=19). Identify exact subsection boundaries.
2. Create NEW framework_node under pillar6 (Special Topics / Generative Models) or appropriate pillar -- researcher picks based on current tree (call it 'diffusion_models' or similar; confirm path doesn't collide).
3. Write canonical content (8000-14000 chars) covering: forward diffusion, reverse denoising, DDPM loss derivation (short), DDIM determinism, Classifier-Free Guidance, connection to SDE/ODE; paper pointers only (no long derivations of variance scheduling -- pointer to standalone doc if any).
4. Create standalone docs/diffusion_models_canonical.md that is the paper-style deep dive (longer form).
5. concept_links: framework_node <new_id> <-> company_document 19 relation='mentions'; mark the Diffusion section of Doc 19 with a '> **正典** [Diffusion Models](/framework/...)' block.
6. Archive pre-migration Doc 19 snapshot to archive/pre_kg/20260416/adobe_doc19_pre_diffusion_migration.md.

ACCEPTANCE CRITERIA:
1. New framework_node exists with >=8000 chars, no empty sections.
2. Standalone docs/diffusion_models_canonical.md exists.
3. Doc 19's diffusion section now references the canonical node via markdown '> **正典**' line.
4. Archive snapshot exists.
5. Idempotent seeder scripts/migrate_doc19_diffusion_20260416.py.
6. Commit: [KG-M-01] Migrate Doc 19 Diffusion Models to canonical framework_node

DEPENDS ON: KG-P1-01 (concept_links), KG-P1-02 (doc_kind), KG-P1-03 (markdown convention).

#### T-P0-478: [KG-M-02] CRITICAL: Migrate Doc 19 RoPE + Long Context (sole source) to framework_node
- **Priority**: P0
- **Complexity**: M
- **Depends on**: T-P0-470
- **Description**: Sibling of KG-M-01. Doc 19 RoPE + Long Context section is sole source.

SCOPE: Same pattern as KG-M-01 but for RoPE / long-context math (position encoding extension, base theta scaling, NTK-aware interpolation). Target pillar: likely pillar6 or pillar4 (transformer internals) -- researcher picks based on tree.

ACCEPTANCE: Same 6-item AC as KG-M-01 but for RoPE content.

DEPENDS ON: KG-P1-01, KG-P1-02, KG-P1-03.

#### T-P0-480: [DOCS-01] Write docs/ filing convention proposal (no file moves yet)
- **Priority**: P0
- **Complexity**: S
- **Depends on**: None
- **Description**: Prior audit: docs/ has 365 files, 6 content categories mixed together, 3 mess examples. Propose a 6-subdir convention before any migration.

DELIVERABLE: docs/protocol/docs_filing_convention.md (~200 lines) specifying:
- Charter of each top-level subdir: study/, company/<slug>/, design/, protocol/, staging/, archive/
- Filename conventions per subdir (dated vs undated, language, case)
- Graduation rules for staging/ (TTL, max age, how to promote)
- Anti-patterns (what NOT to put where)
- Migration map preview: how many files from current state move to each subdir (based on prior audit: 30 study, 52 company, 6 design, 7 protocol, 284 staging, rest archive)

DO NOT execute migration. Document-only deliverable.

ACCEPTANCE CRITERIA:
1. docs/protocol/docs_filing_convention.md exists with all 6 subdirs documented.
2. Contains 3-5 anti-pattern examples from current state.
3. Commit: [DOCS-01] docs/ filing convention proposal

### P1 -- Should Have (agentic intelligence)

#### T-P1-475: [KG-G-01] Translate 11 Google R1 drill docs to Chinese (company_documents 55,56,60-65,67-69)
- **Priority**: P1
- **Complexity**: L
- **Depends on**: None
- **Description**: Target 11 drill docs currently in English (or largely English with some Chinese tech terms). User wants Chinese-first prose per project convention.

EXACT 11 DOCS (verified via DB query):
  55 Regularization Deep Dive (8396 chars)
  56 Bias-Variance + Overfitting Diagnosis Drill (7166 chars)
  60 LambdaRank / LambdaMART Drill (8910 chars)
  61 NDCG / MAP / MRR + Position Bias Drill (11651 chars)
  62 Calibration Drill (11631 chars)
  63 IPS / Counterfactual Eval / Debiased NDCG Drill (14681 chars)
  64 Two-Tower Retrieval Deep Dive (17251 chars)
  65 Multi-Objective Ranking DPP/MMR + Etsy Diversity (22011 chars)
  67 A/B Test Rigor Drill: Sample Size/SRM/CUPED/Novelty (13752 chars)
  68 Feature Drift Drill: PSI/KL/JS/KS (15163 chars)
  69 Train-Serve Skew/Leakage/Temporal Split Drill (22121 chars)

TRANSLATION RULES (per project memory feedback_lc_notes_chinese):
- Chinese prose throughout.
- Keep English: code blocks, algorithm names (LambdaRank, NDCG@k), complexity notation (O(log n)), paper titles, variable names.
- Keep English Glossary terms in parenthesis: e.g. '位置偏差 (Position Bias)'.
- Math via $...$ inline and $$...$$ display; double-check LaTeX renders.

IMPLEMENTATION (split into 3 sub-commits for safety):
- Batch 1 (small, 4 docs): 55, 56, 60, 61
- Batch 2 (mid, 4 docs): 62, 63, 64, 67
- Batch 3 (large, 3 docs): 65, 68, 69
- Each batch: one idempotent seeder script, sentinel marker '<!-- CN_TRANSLATED_20260416 -->' appended at bottom.

ACCEPTANCE CRITERIA:
1. After each batch, the relevant docs have CJK char ratio >= 60% of prose tokens.
2. Re-run each batch prints [UNCHANGED].
3. Original content preserved in archive/pre_kg/YYYYMMDD/google_r1_en_snapshot/ as backup (plain markdown export of pre-translation text).
4. Commits: [T-KG-G-01a] Translate Google R1 drills batch 1 (55/56/60/61) / [T-KG-G-01b] batch 2 / [T-KG-G-01c] batch 3

NON-GOALS: Do NOT touch doc 57 (Staging 13 Flashcards -- already Chinese); do NOT auto-generate via LLM prompt chain without diff review.

#### T-P1-479: [KG-M-03] Delete Doc 29 Adobe ML Fundamentals (byte-identical duplicate of Doc 28)
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Prior audit confirmed doc 29 (Adobe) and doc 28 (Uber) both titled 'ML Fundamentals From-Scratch' are 151,774 chars each -- byte-identical. Safe to delete 29; all concepts covered in 28.

ACTION:
1. Verify via SHA256 that content of docs 28 and 29 match (if not, halt and re-audit).
2. archive/pre_kg/20260416/adobe_doc29_snapshot.md: save a copy.
3. DELETE FROM company_documents WHERE id=29.
4. Grep repo for any '/api/companies/.../documents/29' references -- none expected but verify.

ACCEPTANCE CRITERIA:
1. sha256(doc 28 content) == sha256(doc 29 content) before delete.
2. Doc 29 no longer returned by API.
3. No broken references.
4. Commit: [KG-M-03] Delete Doc 29 Adobe duplicate of Doc 28

DEPENDS ON: KG-M-00 (generate checklist first; user approves the delete).

#### T-P1-481: [DOCS-02] Migrate top-level company prep files to docs/company/<slug>/
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P0-480
- **Description**: Per proposed convention (DOCS-01), move 34 top-level company prep files into docs/company/<slug>/ subdirs.

SCOPE (verify count via `ls docs/*_prep.md docs/google_*.md docs/uber_*.md docs/doordash_*.md docs/slack_*.md`):
- Create docs/company/google/, docs/company/uber/, docs/company/doordash/, docs/company/slack/, docs/company/linkedin/, docs/company/adobe/ (if any corresponding files exist).
- docs/company/pinterest/ already exists -- consolidate any pinterest_* top-level files into it.
- git mv (preserves history) each file to its slug dir.
- Filename convention: strip company prefix ('google_staging_13_flashcards.md' becomes 'staging_13_flashcards.md' inside docs/company/google/).

IMPLEMENTATION:
- scripts/migrate_docs_company_subdirs.py that builds the move map and executes `git mv` via subprocess (or just moves files and user stages + commits).
- Update any code that references these paths (grep 'docs/google_' 'docs/uber_' etc in scripts/ and src/).

ACCEPTANCE CRITERIA:
1. docs/company/<slug>/ dirs exist with migrated files.
2. No top-level docs/*_prep.md / docs/google_*.md etc files remain (except symlinks if needed during transition).
3. Any script/seed referencing the old path is updated.
4. pytest + npm run build still pass.
5. Commit: [DOCS-02] Migrate company prep to docs/company/<slug>/

DEPENDS ON: DOCS-01 (convention doc must exist first for reference).

#### T-P1-482: [DOCS-03] Move intermediate / generated / audits / synced into docs/staging/
- **Priority**: P1
- **Complexity**: S
- **Depends on**: T-P0-480
- **Description**: Per DOCS-01 convention, move 274 generated system design fragments + audits/ + synced/ + analysis/ into docs/staging/ with TTL metadata.

SCOPE:
- git mv docs/generated/ -> docs/staging/generated/
- git mv docs/audits/ -> docs/staging/audits/
- git mv docs/synced/ -> docs/staging/synced/
- git mv docs/analysis/ -> docs/staging/analysis/
- Add docs/staging/README.md stating the TTL policy (files older than 30d must graduate or be deleted).

ACCEPTANCE CRITERIA:
1. Moved directories under docs/staging/ present.
2. docs/staging/README.md explains TTL.
3. Any script referencing old paths updated.
4. Commit: [DOCS-03] Move intermediate content to docs/staging/

DEPENDS ON: DOCS-01.

#### T-P1-483: [KG-VIZ-01] /kg visualization POC: Cytoscape.js + dagre (user-picked)
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: User-picked Cytoscape.js (over React Flow / D3-Force / Sigma / vis-network). POC scope below.

DEPENDENCIES TO ADD (src/frontend/package.json):
- cytoscape
- react-cytoscapejs
- cytoscape-dagre (dagre layout adapter)
- cytoscape-expand-collapse (optional but highly recommended for pillar collapse; add if bundle budget allows)
- @types/cytoscape (types)

BACKEND API (new endpoint):
- GET /api/kg/graph returns: {nodes: [{id, kind, pillar, path, title, content_length}], edges: [{src_kind, src_id, dst_kind, dst_id, relation}]}
- Nodes source: framework_nodes + (later) company_documents. For POC, emit framework_nodes only.
- Edges source: concept_links table (requires KG-P1-01 completed).
- Implement in src/backend/app/routers/kg.py (new file) with tests under src/backend/tests/test_kg_router.py.

FRONTEND ROUTE (new):
- src/frontend/src/pages/KnowledgeGraph.tsx renders full-viewport Cytoscape canvas.
- Register in App.tsx / router: path='/kg'.
- Layout: dagre (rankDir='TB') for pillar hierarchy; force fallback for cross-pillar concept_links.
- Interactions: pan/zoom, click node -> open FrameworkNodeDrawer (reuse existing component), search box filters by title.
- Styling: pillar colors via CSS-in-Cytoscape-style; Tailwind only for surrounding UI (header, search, legend).

POC SCOPE (smaller than full build):
- Support 30-50 framework_nodes (any pillar subset) + 10 synthetic concept_links if DB table empty.
- Pillar grouping visible; click expands/collapses pillar.
- FrameworkNodeDrawer opens on click.
- Search filter works.

ACCEPTANCE CRITERIA:
1. /kg route accessible and renders without layout flicker.
2. Bundle size delta under 200 KB gzip (cytoscape + dagre + react wrapper).
3. npm run build passes 0 TS errors.
4. Frontend vitest: add at least 1 test hitting KnowledgeGraph.tsx mounted + mocked /api/kg/graph.
5. Backend: /api/kg/graph returns 200 with nodes + edges schema validated.
6. Smoke: manually opened page shows 30+ nodes grouped by pillar, click opens drawer.
7. Commit: [KG-VIZ-01] /kg POC: Cytoscape.js + dagre (framework_nodes + concept_links)

DEPENDS ON: KG-P1-01 (concept_links table; without this, edges source is empty and we ship POC with synthetic edges). Best to run AFTER KG-P1-01 to use real edges.

NON-GOALS:
- No Company lens / filter in POC (defer to VIZ-02).
- No orphan detection view (defer).
- No 3D / force-only layout (dagre is primary).
- Do NOT remove FrameworkTreeView or FrameworkTreemap -- keep as complementary 2D views.

### P2 -- Nice to Have

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

- [x] **2026-04-16** -- T-P2-469: [QIdx-C1] Harden LC import scripts to set family. Harden LC import scripts so new rows no longer default to family=NULL silently.
- [x] **2026-04-16** -- T-P2-460: [Pinterest-SD] Responsible AI / Inclusive AI + model monitoring & retraining playbook. Gap: Pinterest brands on 'Inclusive AI' (skin-tone-fair visual search case study) but no prep doc covers it. Bundle with
- [x] **2026-04-16** -- T-P2-459: [Pinterest-SD] Multimodal unsafe content detection + query expansion recall boost. Gap: two known Pinterest SD interview prompts -- neither has a dedicated doc. (1) Unsafe content (image+text multimodal)
- [x] **2026-04-16** -- T-P2-458: [Pinterest-Gen] GAN / VAE / Diffusion contrast one-pager + Pinterest use cases. Gap: no generative-model contrast at pitch level. Pinterest angle (visual content): pin generation, style transfer for b
- [x] **2026-04-16** -- T-P2-439: [DEBT] MLInterviewPrep: requirements.txt has scraper deps in wrong section. beautifulsoup4==4.12.2 and playwright==1.58.0 are in [project.optional-dependencies].scraper in pyproject.toml but appea
- [x] **2026-04-16** -- T-P2-438: [DEBT] MLInterviewPrep: httpx duplicated in pyproject.toml main + dev groups. pyproject.toml lists httpx==0.27.2 in both [project].dependencies (main) and [project.optional-dependencies].dev. This i
- [x] **2026-04-16** -- T-P1-468: [QIdx-B5] LC 362 Design Hit Counter: expand notes. Expand thin notes for LC 362 Design Hit Counter to full solution + mark completed.
- [x] **2026-04-16** -- T-P1-467: [QIdx-B4] LC 1845 Seat Reservation Manager: Chinese solution notes. Write Chinese solution notes for LC 1845 Seat Reservation Manager and mark completed.
- [x] **2026-04-16** -- T-P1-466: [QIdx-B3] LC 1825 Finding MK Average: Chinese solution notes. Write Chinese solution notes for LC 1825 Finding MK Average and mark completed.
- [x] **2026-04-16** -- T-P1-465: [QIdx-B2] LC 1146 Snapshot Array: Chinese solution notes. Write Chinese solution notes for LC 1146 Snapshot Array and mark completed.
- [x] **2026-04-16** -- T-P1-464: [QIdx-B1] LC 895 Maximum Frequency Stack: Chinese solution notes. Write Chinese solution notes for LC 895 Maximum Frequency Stack and mark completed.
- [x] **2026-04-16** -- T-P0-470: [KG-P1-01] Create concept_links table + migration. Create new table `concept_links` in data/mle_prep.db for structured cross-references between concepts (framework_nodes) 
