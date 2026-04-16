# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

### P1 -- Should Have (agentic intelligence)

#### T-P0-420: [Google/R1] Multi-objective ranking: DPP/MMR + Etsy diversity 故事机制
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Etsy diversity 必被追问机制. AC: (1) MMR = λ·rel-(1-λ)·max_sim; (2) DPP 用 det(L_S) 同时 model rel(对角) + diversity(非对角); (3) intent collapse → allocation primitive 平台化 = module arbitration; (4) 和 uncertainty weighting/GradNorm/Pareto 正交. Ref: doordash_ranking §5.

#### T-P1-440: Pinterest card index: backend + data prep
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: # Pinterest Card Index: Backend + Data Prep (T-P1-224)

## Goal
Seed a `card_index` document for Pinterest (company_id=29) that defines 10 cluster cards grouping 28 problems. Extend `doc_kind` enum to support this new kind. Tag LC 85 as Pinterest.

## Files
- `src/backend/models/company.py:93` — CompanyDocument.doc_kind Column (CHECK constraint)
- `src/backend/database.py:486` — migration hook for doc_kind
- `scripts/_seed_pinterest_card_index.py` — NEW seed script to create

## Steps

### 1. Extend doc_kind enum
Update CHECK constraint: `doc_kind IN ('prep_note','hub_doc','recruiter_call','other','card_index')`.
- Edit `models/company.py:96` CheckConstraint
- Edit `database.py:507` migration SQL to use new enum (for fresh DBs)
- For existing DB: run one-off `ALTER TABLE` via copy-swap (SQLite) OR simpler: drop and recreate CHECK via table rewrite. Use the same pattern as `scripts/_migrate_companies_status_not_null.py`.

### 2. Tag LC 85 with Pinterest
`UPDATE problems SET company_tags = json_set(company_tags, '$[#]', 'Pinterest') WHERE leetcode_id=85` — or simpler: load, append, save.

### 3. Create seed script `scripts/_seed_pinterest_card_index.py`
Inserts a company_document with:
- company_id=29
- title="Pinterest Prep Card Index"
- doc_kind="card_index"
- source_type="manual"
- content = JSON with schema below

### JSON Schema
```json
{
  "schema_version": 1,
  "cards": [
    {
      "name_zh": "字符串/数字运算",
      "name_en": "String / Digit Arithmetic",
      "summary_zh": "核心：carry propagation, partition('.') 解析, shift-based 精度舍入",
      "problems": [
        {"id": 135, "leetcode_id": 43, "title": "Multiply Strings", "one_liner": "逐位乘法 pos[i+j] / pos[i+j+1]"},
        {"id": 1073, "leetcode_id": null, "title": "round() from scratch (string input, no float)", "one_liner": "half-up 进位链，禁用 float()"},
        {"id": 1074, "leetcode_id": null, "title": "round by precision p (string s, precision p)", "one_liner": "shift 复用 1073 + 还原"}
      ]
    }
  ]
}
```

### 4. Full 10-card data (problem id mappings)
Use these exact problem DB ids (verified from DB):

Card 1 — 字符串/数字运算 / String / Digit Arithmetic:
  LC 43 (id=135), db:1073, db:1074

Card 2 — 单调栈/直方图 / Monotonic Stack / Histogram:
  LC 84 (id=85), LC 85 (id=242)

Card 3 — 贪心差分 / Greedy on Differences:
  LC 1526 (id=236), LC 3229 (id=157)

Card 4 — 仓储/箱子装填 / Warehouse / Box Packing:
  LC 1564 (id=1069), LC 1580 (id=1070)

Card 5 — 图论/欧拉/BFS / Graph / Eulerian / BFS:
  LC 332 (id=148), LC 815 (id=217), LC 465 (id=214)

Card 6 — 回溯/DFS / Backtracking / DFS:
  LC 282 (id=439), LC 1110 (id=1066), LC 1723 (id=1067)

Card 7 — DP/二分 / DP / Binary Search:
  LC 322 (id=55), LC 410 (id=265), LC 1055 (id=498)

Card 8 — 堆/模拟/设计 / Heap / Simulation / Design:
  LC 2402 (id=258), LC 1244 (id=199), LC 642 (id=237), LC 311 (id=277)

Card 9 — 区间/子序列 / Interval / Subsequence:
  LC 1851 (id=144), LC 392 (id=417)

Card 10 — Pinterest 定制题 / Pinterest Custom:
  db:1068, db:1071, db:1072, db:1075, db:1076

Use full titles exactly as stored in DB (query to fetch).

## Acceptance Criteria
- [ ] doc_kind CHECK constraint includes 'card_index' (verify via `PRAGMA table_info` or SQL query)
- [ ] LC 85 company_tags contains "Pinterest"
- [ ] Single card_index doc exists: `SELECT COUNT(*) FROM company_documents WHERE doc_kind='card_index' AND company_id=29` = 1
- [ ] JSON content parses (`json.loads(content)` succeeds)
- [ ] All 28 problem IDs resolve: each `problems[*].id` exists in problems table
- [ ] Seed script is idempotent (re-run updates, doesn't duplicate)

## Verification
```bash
python scripts/_seed_pinterest_card_index.py
python -c "
import sqlite3, json
c = sqlite3.connect('data/mle_prep.db')
r = c.execute(\"SELECT content FROM company_documents WHERE doc_kind='card_index' AND company_id=29\").fetchone()
data = json.loads(r[0])
assert len(data['cards']) == 10
total_problems = sum(len(card['problems']) for card in data['cards'])
assert total_problems == 28
# Verify all problem IDs exist
for card in data['cards']:
    for p in card['problems']:
        assert c.execute('SELECT 1 FROM problems WHERE id=?', (p['id'],)).fetchone()
print('[PASS] 10 cards, 28 problems, all IDs resolve')
"
```

## Commit message
`[T-P1-224] Add card_index doc_kind + seed Pinterest 10-cluster card index`

#### T-P1-441: Pinterest card index: frontend CardGrid component
- **Priority**: P1
- **Complexity**: S
- **Depends on**: T-P1-440
- **Description**: # Pinterest Card Index: Frontend CardGrid Component (T-P1-225)

## Goal
Create `CompanyCardIndex.tsx` that fetches the card_index doc for a company and renders it as a responsive card grid with bilingual headers and problem links.

## Files
- `src/frontend/src/components/CompanyCardIndex.tsx` — NEW component
- `src/frontend/src/pages/QuickIndex.tsx` — reference pattern for card layout (line 1-357)
- `src/frontend/src/components/ui/MarkdownPreview.tsx:17-26` — reference for lc:// / db:// link handling
- `src/frontend/src/pages/PrepNotesPage.tsx:531-532` — existing drawer callback pattern
- `src/frontend/src/api.ts` (or similar) — fetch `GET /companies/:id/documents`
- `src/frontend/src/types.ts` — add `CardIndexContent` type

## Interface
```tsx
interface CardIndexContent {
  schema_version: number;
  cards: Array<{
    name_zh: string;
    name_en: string;
    summary_zh: string;
    problems: Array<{
      id: number;
      leetcode_id: number | null;
      title: string;
      one_liner: string;
    }>;
  }>;
}

interface CompanyCardIndexProps {
  companyId: number;
  onLcClick: (lcId: number) => void;   // opens LC drawer
  onDbClick: (dbId: number) => void;   // opens DB drawer
}
```

## Component Behavior

### 1. Fetch card_index document
- `GET /companies/:companyId/documents` filtered by `doc_kind === 'card_index'`
- Parse `content` as JSON into `CardIndexContent`
- Show loading spinner during fetch, error banner on failure, empty state if no card_index doc

### 2. Layout
- CSS grid: `grid-template-columns: repeat(auto-fit, minmax(380px, 1fr))`
- Gap: 16px
- Each card: border, rounded corners, padding 16px, subtle shadow

### 3. Card rendering
```tsx
<div className="card">
  <h3>
    <span className="text-zh">{card.name_zh}</span>
    <span className="text-en"> -- {card.name_en}</span>
  </h3>
  <p className="summary">{card.summary_zh}</p>
  {card.problems.length <= 5 ? (
    <ul>{card.problems.map(renderProblem)}</ul>
  ) : (
    <details>
      <summary>{card.problems.length} 题</summary>
      <ul>{card.problems.map(renderProblem)}</ul>
    </details>
  )}
</div>
```

### 4. Problem link rendering
```tsx
const renderProblem = (p) => (
  <li key={p.id}>
    <button
      onClick={() => p.leetcode_id ? onLcClick(p.leetcode_id) : onDbClick(p.id)}
      className="problem-link"
    >
      {p.leetcode_id ? `LC ${p.leetcode_id}` : `db:${p.id}`} {p.title}
    </button>
    {p.one_liner && <span className="one-liner"> — {p.one_liner}</span>}
  </li>
);
```

## Style Notes
- Follow existing Tailwind/CSS conventions from QuickIndex.tsx
- Bilingual header: Chinese bold + English lighter weight (QuickIndex has similar pattern)
- Problem link looks clickable (underline on hover), no default blue anchor style
- Summary line uses italic or muted color

## Acceptance Criteria
- [ ] `CompanyCardIndex.tsx` exports a typed default component
- [ ] Fetches and parses card_index doc successfully for companyId=29
- [ ] Renders 10 cards with all 28 problems
- [ ] Bilingual headers display correctly (中文 first, English after ` -- `)
- [ ] Cards with >5 problems are collapsed by default (use `<details>`)
- [ ] Clicking LC problem calls `onLcClick(leetcode_id)`
- [ ] Clicking custom problem (leetcode_id=null) calls `onDbClick(id)`
- [ ] Responsive: renders 2-3 columns at 1440px, 1 column at 375px
- [ ] No TypeScript errors (`npm run build` passes)

## Verification
1. `npm run build` in src/frontend — must pass
2. Temporarily mount component standalone in a dev route and verify rendering
3. Click one LC and one db:// problem, confirm callbacks fire

## Commit message
`[T-P1-225] Add CompanyCardIndex component with bilingual cluster cards`

## Depends on: T-P1-224

#### T-P1-442: Pinterest card index: integrate tab=index into PrepNotesPage
- **Priority**: P1
- **Complexity**: S
- **Depends on**: T-P1-441
- **Description**: # Pinterest Card Index: Integrate tab=index into PrepNotesPage (T-P1-226)

## Goal
Add a new `tab=index` to PrepNotesPage that renders CompanyCardIndex. Tab is only visible when the company has a card_index document.

## Files
- `src/frontend/src/pages/PrepNotesPage.tsx` (549 lines) — add new tab
- `src/backend/schemas/company.py:73-84` — verify CompanyDocumentResponse already exposes `doc_kind` (add if missing)
- `src/backend/routers/companies.py` — verify list endpoint returns doc_kind (already does per grep at line 507)

## Backend check first
Before frontend work, verify `CompanyDocumentResponse` schema includes `doc_kind`. If missing:
```python
# schemas/company.py CompanyDocumentResponse
doc_kind: str | None = None
```
(The companies router already returns doc_kind in responses — line 507.)

## Frontend changes

### 1. Tab state
Find the tab state management in PrepNotesPage (search for `tab=docs` or similar URL query logic). Add `'index'` as a valid tab value.

### 2. Tab button rendering
Find the tab button bar. Add:
```tsx
{hasCardIndex && (
  <button
    onClick={() => setTab('index')}
    className={tab === 'index' ? 'active' : ''}
  >
    索引 / Index
  </button>
)}
```
where `hasCardIndex` is derived from the docs list:
```tsx
const hasCardIndex = documents.some(d => d.doc_kind === 'card_index');
```

### 3. Conditional rendering
In the tab content rendering, add:
```tsx
{tab === 'index' && (
  <CompanyCardIndex
    companyId={Number(id)}
    onLcClick={(lcId) => { setDbDrawerId(null); setLcDrawerId(lcId); }}
    onDbClick={(dbId) => { setLcDrawerId(null); setDbDrawerId(dbId); }}
  />
)}
```
(Reuse the exact drawer handler pattern from line 531-532.)

### 4. Default tab logic
If the URL has no explicit `?tab=X` and the company has a card_index, default to `tab=index`. Otherwise preserve existing default. This makes the index the landing view for Pinterest.

## Acceptance Criteria
- [ ] `GET /companies/29/prep` (no tab param) lands on Index tab (card grid visible)
- [ ] URL `?tab=index` renders CompanyCardIndex
- [ ] URL `?tab=docs` still works (no regression)
- [ ] URL `?tab=problems` still works
- [ ] Index tab button is HIDDEN for companies with no card_index document (e.g. `/companies/1/prep`)
- [ ] Clicking a problem card opens the drawer (LC or DB)
- [ ] No console errors in browser devtools on initial load
- [ ] `npm run build` passes

## Verification (manual smoke)
Start backend + frontend, then in browser:
1. http://localhost:5173/companies/29/prep — should land on Index tab
2. Click one card problem — drawer opens with correct problem notes
3. Switch to Docs tab — doc 47 renders as before
4. Switch to Problems tab — problem list renders as before
5. Visit http://localhost:5173/companies/1/prep — Index tab should NOT appear
6. Open browser console — no errors

## Commit message
`[T-P1-226] Add tab=index to PrepNotesPage rendering CompanyCardIndex`

## Depends on: T-P1-225

#### T-P1-443: Problems tab: Custom badge + source-type filter switch
- **Priority**: P1
- **Complexity**: S
- **Depends on**: T-P1-442
- **Description**: # Problems tab: Custom badge + source-type filter (T-ML-xxx)

## Goal
Make custom (non-LC) problems visually distinct in the Problems.tsx table and add a source-type switch at the top: All / LC Only / Custom Only.

## Context
- 44 custom problems exist in DB (`leetcode_id IS NULL`), covering Pinterest, Snowflake, Uber, DoorDash, 1point3acres, etc.
- Backend `GET /problems` already returns them; no backend changes needed.
- Current UI: custom rows show "-" in the LC column, visually dim and easy to miss.

## Files
- `src/frontend/src/pages/Problems.tsx` (1063 lines) — main page
- `src/frontend/src/api.ts` — `GET /problems` client (no changes needed)
- `src/backend/routers/problems.py:141-216` — reference for existing filters (DO NOT modify)

## Changes

### 1. Custom badge in title/LC column
Replace the "-" rendering for `p.leetcode_id == null`:
- Show a pill/badge like `[Custom]` or `[自建]` with colored background (e.g., purple/amber)
- Keep the title prominent; badge should be a small inline tag
- Example: `<Badge variant="custom">Custom</Badge> Escape Room Game State`

### 2. Source-type switch
Add a segmented control above the Problems table:
- Options: `All` / `LeetCode` / `Custom`
- Default: `All`
- Renders as a 3-button segmented control (similar to existing UI primitives)
- URL state: `?source_type=all|lc|custom`
- Filter logic (client-side since API returns all):
  - `all`: no filter
  - `lc`: `p.leetcode_id != null`
  - `custom`: `p.leetcode_id == null`

### 3. Row count update
Show filtered counts near the switch: "显示 44 / 共 1089 题" (show "filtered / total").

## Acceptance Criteria
- [ ] Custom problems display a visible [Custom] badge in the Problems table
- [ ] Segmented control "All / LeetCode / Custom" appears above the table
- [ ] Switching to "Custom" hides LC problems and vice versa
- [ ] URL param `source_type` persists across reloads (`?source_type=custom`)
- [ ] Row count label updates to reflect filtered count
- [ ] No regression on existing filters (difficulty, category, pattern, source, company, status)
- [ ] `npm run build` passes

## Verification
1. Start backend + frontend.
2. Navigate to /problems — default All, see both LC and Custom rows.
3. Switch to Custom — verify only custom rows, count correct.
4. Switch to LeetCode — verify only LC rows, count correct.
5. Combine with company filter "Snowflake" — only 2 Snowflake custom problems show.
6. Refresh with `?source_type=custom` — starts on Custom tab.

## Commit message
`[T-ML-xxx] Problems tab: Custom badge + source-type filter switch`

## Depends on: T-P1-442 (sequenced after Pinterest card index work to avoid frontend merge conflicts)

#### T-P1-444: Problems tab: Custom-mode company-grouped view
- **Priority**: P1
- **Complexity**: S
- **Depends on**: T-P1-443
- **Description**: # Problems tab: Custom-mode company-grouped view (T-ML-xxx)

## Goal
When the user switches to `source_type=custom`, render custom problems as a COMPANY-GROUPED card layout (like the Pinterest card index), not a flat table. This makes company-based discovery primary for custom problems.

## Context
Depends on T-P1-443 (custom badge + switch). T-P1-443 adds the switch but still renders custom rows in the same flat table. This task upgrades the Custom view to a grouped card layout.

## Files
- `src/frontend/src/pages/Problems.tsx` — add grouped-by-company rendering for Custom mode
- `src/frontend/src/components/CompanyCardIndex.tsx` (from T-P1-441) — reference pattern for card layout; may extract a shared `ProblemCardGroup` component if reuse is clean
- `src/frontend/src/api.ts` — `GET /problems?source_type=custom` (client-side filter, no backend change)

## Design

### Layout (only when `source_type === 'custom'`)
- Group the filtered custom problems by `company_tags` (JSON array, can contain multiple companies per problem — show under EACH company)
- For problems with `company_tags == []`, group under "未归类 / Unassigned"
- Each group is a card:
  ```
  ┌───────────────────────────────────────┐
  │ Snowflake (2 题)                       │
  ├───────────────────────────────────────┤
  │ • Nearest Bathroom to Each Desk       │
  │ • Max Tree Height After Deleting ...  │
  └───────────────────────────────────────┘
  ```
- Click problem title → open existing ProblemDrawer (same as flat table row click)
- Grid: 2 columns desktop, 1 column mobile (same as CompanyCardIndex)

### Company filter interaction
- Existing sidebar company filter still applies — if set, only that company's card shows
- If no company filter, all company cards render

### Problem counts per company (current custom problem distribution)
Verify roughly matches expectation (pull via API or quick query):
- Pinterest: ~7 custom
- Snowflake: 2 custom (just added)
- Uber: ~X custom
- DoorDash: ~X custom
- 1point3acres: ~X
- Others: likely single-company tags

## Acceptance Criteria
- [ ] When switched to Custom tab, problems render as company-grouped cards (not flat table)
- [ ] Clicking a problem title opens the ProblemDrawer
- [ ] Problems with multi-company tags appear under EACH company (dedup if same problem twice in one company)
- [ ] Problems with empty company_tags go to "未归类" group
- [ ] Sidebar company filter narrows to selected company only
- [ ] Switching back to "All" or "LC" restores flat table
- [ ] No regression on Problems page filters
- [ ] `npm run build` passes

## Verification
1. Switch to Custom — see grouped cards with company names
2. Click "Snowflake" card problem → drawer opens with notes
3. Sidebar company filter "Pinterest" → only Pinterest card visible
4. Switch to "All" → flat table restored, custom rows still have [Custom] badge
5. Clear filters, count per card matches actual custom-problem distribution

## Commit message
`[T-ML-xxx] Problems tab: company-grouped view for Custom mode`

## Depends on: T-P1-443

### P2 -- Nice to Have

#### T-P1-421: [Google/R1] A/B test 严谨性: sample size/SRM/CUPED/novelty
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: pillar7 有基础但缺 drill. AC: (1) n=(z+z)^2·2σ²/Δ²; (2) SRM 是 randomization 健康性不是结果; (3) CUPED 用 pre-period covariate 降 variance; (4) novelty 早期正偏/primacy 负偏 1 周洗期; (5) Etsy GMB 碰过哪个 trap.

#### T-P1-422: [Google/R1] Feature drift 监控: PSI/KL/JS 区别 + alert threshold
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: AC: (1) PSI=Σ(a-e)·ln(a/e), 0.1 warn/0.25 critical; (2) KL 不对称无界, JS 对称 bounded; (3) 连续用 KS; (4) concept drift P(y|x) vs covariate shift P(x); (5) 分 feature/分段 alert.

#### T-P1-423: [Google/R1] Train-serve skew/leakage/时序 split 拷打
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: AC: (1) target encoding K-fold leakage + fold-out 修正; (2) 为什么 ranking 必须 time-based split; (3) feature store parity 三种 skew (时间戳/null 语义/填充); (4) label leakage: future-only aggregates; (5) 一个真实踩坑.

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

- [x] **2026-04-15** -- T-P0-424: [Slack-SFDC] HR call Wed 2026-04-15 14:00 EST = 11:00 PT. Slack (Salesforce) ML team recruiter call. 时间: 04/15 Wed 14:00 EST = 13:00 CST = 11:00 PT. 30-45 min 预期. 准备: (1) 自我介绍 90
- [x] **2026-04-15** -- T-P0-419: [Google/R1] Two-tower retrieval 深挖 (超越 InfoNCE 基础). staging 11 覆盖 InfoNCE 但缺系统级. AC: (1) 为什么两塔 (query 塔不看 doc 侧 → offline index); (2) negative sampling 四种 + failure mode; (
- [x] **2026-04-15** -- T-P0-418: [Google/R1] IPS/counterfactual eval/去偏 NDCG (SIGIR paper talking points). Gap: staging 无. SIGIR paper 必问. AC: (1) IPS 重加权 1/P(shown); (2) examination hypothesis P(click)=P(exam)·P(rel); (3) SNIP
- [x] **2026-04-15** -- T-P0-417: [Google/R1] Calibration 三法 (Platt/Isotonic/Temperature) + GMB bidding 校准陷阱. Gap: staging 没提. Round1 recruiter 明列. AC: (1) Platt=logistic over logit; (2) Isotonic preserve ranking 粒度粗; (3) Temperat
- [x] **2026-04-15** -- T-P0-416: [Google/R1] NDCG/MAP/MRR 定义 + position bias 拷打自测. Gap: staging 只讲 ROC/PR. AC: (1) 默写 DCG=Σ(2^rel-1)/log2(i+1), NDCG=DCG/IDCG; (2) 为什么 MAP 不适合 graded relevance; (3) positi
- [x] **2026-04-15** -- T-P0-415: [Google/R1] LambdaRank/LambdaMART 推导 + pointwise/pairwise/listwise 对比自测. Gap vs staging 13: staging 无 ranking loss 推导. Round1 必考. AC: (1) 默写 RankNet pairwise sigmoid loss; (2) LambdaRank 如何用 de
