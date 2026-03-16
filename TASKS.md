# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

### P1 -- Should Have (agentic intelligence)

#### T-P1-85: [B4] Backend: Split dashboard API into today/activity/summary endpoints
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P0-81
- **Description**: AC:
- GET /api/dashboard/today: due_reviews count, suggested_focus_topic (weakest), streak_days
- GET /api/dashboard/activity: [{date, attempts, study_minutes, questions_added}] for last 30 days
- GET /api/dashboard/summary: problems (total/completed), framework overall_progress_pct, company counts by status
- Keep GET /api/dashboard for backward compat (aggregates the 3 sub-endpoints)
- Tests for each new endpoint
- streak_days: count consecutive days with any activity (attempt or study log)

Key files: src/backend/main.py

#### T-P1-86: [B4] Frontend: Dashboard rewrite with Today Focus + Weekly Chart + Pillar Progress
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-85, T-P0-78, T-P0-74
- **Description**: AC:
- Row 1: Today Focus cards (3-col): Due Reviews (clickable -> /problems?review=due), Weakest Topic (clickable -> /framework), Streak days
- Row 2 left: WeeklyActivityChart (Recharts BarChart, stacked attempts + study mins, 7 days)
- Row 2 right: Framework Pillar Progress Bars (existing PillarBar, click navigates to Framework page)
- Row 3: Company Status Summary (compact counts per status)
- No heatmap, no pie chart. Clean and actionable.
- Uses React Query for all 3 dashboard endpoints
- Loading skeletons instead of Loading... text

Key files: src/frontend/src/pages/Dashboard.tsx (rewrite), new components/charts/WeeklyActivityChart.tsx

#### T-P1-87: [B5] Backend: DELETE companies/{id}, POST/DELETE questions, extend PUT questions/{id}
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P0-74
- **Description**: AC:
- DELETE /api/companies/{id}: deletes company + cascades topic weights. Returns count of deleted weights.
- POST /api/questions: create single question (question_text, company, role, question_type, level, year, tags, difficulty_estimate, mapped_framework_node_id)
- DELETE /api/questions/{id}: delete question
- PUT /api/questions/{id}: accept all editable fields (company, role, question_type, level, year, tags, difficulty_estimate, mapped_framework_node_id, notes)
- Tests for each new/modified endpoint

Key files: src/backend/routers/companies.py, src/backend/routers/scraper.py, src/backend/schemas/scraper.py

#### T-P1-88: [B5] Frontend: Companies edit/delete + topic weight editor
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-87, T-P0-76
- **Description**: AC:
- Edit company in FocusTopicsPanel: name, group_tag, notes, applied_at all editable + Save
- Delete company button -> ConfirmDialog showing cascade count (N topic weights will be removed)
- TopicWeightEditor: list current weights with sliders (0-5), add/remove topics
- Toast on all mutation success/failure
- React Query cache invalidation after mutations

Key files: src/frontend/src/pages/Companies.tsx, new components/companies/EditCompanyPanel.tsx, TopicWeightEditor.tsx

#### T-P1-89: [B5] Frontend: Questions add/edit/delete + bulk mark reviewed + framework mapping
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-87, T-P0-82
- **Description**: AC:
- + Add Question button -> AddQuestionModal (question_text, company, role, type, level, year, tags)
- Inline edit metadata in expanded row (all fields editable via PUT)
- Delete with ConfirmDialog
- Bulk mark reviewed: checkboxes on rows + floating action bar
- FrameworkNodePicker in expanded row for mapped_framework_node_id
- Toast on all mutations

Key files: src/frontend/src/pages/Questions.tsx, new components/questions/AddQuestionModal.tsx, EditableQuestionRow.tsx

### P2 -- Nice to Have

#### T-P2-90: [B6] Frontend: Kanban drag-and-drop for Companies page
- **Priority**: P2
- **Complexity**: M
- **Depends on**: T-P1-88
- **Description**: AC:
- Install @hello-pangea/dnd
- Wrap Kanban columns as Droppable, cards as Draggable
- On drop: call PUT /companies/{id} with new status
- Visual feedback during drag (shadow, placeholder)
- React Query cache invalidation after status change
- Toast on success/failure

Key files: src/frontend/src/pages/Companies.tsx

#### T-P2-91: [B6] Frontend: Framework tree search + breadcrumb path
- **Priority**: P2
- **Complexity**: M
- **Depends on**: T-P0-80, T-P0-77
- **Description**: AC:
- TreeSearchBar: type to filter, matching nodes highlighted (yellow bg), non-matching ancestors auto-expanded, non-matching leaves hidden
- BreadcrumbPath: when node selected, show clickable path segments above detail panel
- Search uses client-side filter (no backend change)
- Debounced search input (useDebounce)

Key files: src/frontend/src/pages/Framework.tsx, src/frontend/src/components/FrameworkTreeView.tsx, new components/framework/TreeSearchBar.tsx, BreadcrumbPath.tsx

#### T-P2-92: [B6] Frontend: Settings page (import/export + scraper management)
- **Priority**: P2
- **Complexity**: M
- **Depends on**: T-P0-74
- **Description**: AC:
- New /settings route added to App.tsx
- Settings link in Sidebar
- Export section: Download JSON button (GET /api/export -> download), Download CSV option
- Import section: File upload zone for JSON (POST /api/import) and CSV (POST /api/import/csv), show results (inserted/skipped/errors)
- Seed section: Load Seed Data button (POST /api/import/seed)
- Scraper section: seed URL list (GET /api/scraper/seeds), add/edit/delete, Run Scraper button + job status

Key files: new src/frontend/src/pages/Settings.tsx, new components/settings/ExportPanel.tsx, ImportPanel.tsx, ScraperManager.tsx, src/frontend/src/components/Sidebar.tsx

#### T-P2-93: [B6] Frontend: QA session summarize button in ReviewPanel
- **Priority**: P2
- **Complexity**: S
- **Depends on**: T-P0-74
- **Description**: AC:
- Summarize button appears for completed QA sessions in ReviewPanel
- Calls POST /api/qa/{id}/summarize
- Shows summary text below session messages
- Toast on success/failure
- Loading state on button during request

Key files: src/frontend/src/components/ReviewPanel.tsx

#### T-P2-94: [B7] Frontend: Analytics deep-dive (radar chart, scatter plot, trend lines)
- **Priority**: P2
- **Complexity**: L
- **Depends on**: T-P1-86, T-P2-92
- **Description**: AC:\n- Pattern comfort radar chart (Recharts RadarChart) on Problems page or Dashboard\n- Framework confidence vs importance scatter plot\n- Problem comfort trend over time (per-problem line chart in ReviewPanel)\n- Company-specific prep readiness score\n- Only implement after Batches 1-6 stable\n\nOptional -- skip if not needed.

### P3 -- Stretch Goals

## Blocked

## Completed Tasks

> 71 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-03-15** -- T-P2-72: Add GET / root endpoint returning API info JSON
- [x] **2026-03-15** -- T-P2-68: Add combined backend+frontend startup script (scripts/dev.py)
- [x] **2026-03-15** -- T-P0-84: [B3] Frontend: Topic detail shows linked problems + questions in NodeDetailPanel. AC:
- [x] **2026-03-15** -- T-P0-83: [B3] Frontend: Problem CRUD (Add/Edit/Delete) + text search. AC:
- [x] **2026-03-15** -- T-P0-82: [B3] Frontend: FrameworkNodePicker component. AC:
- [x] **2026-03-15** -- T-P0-81: [B3] Backend: Add framework_node_id FK to Problem model + topic-linked endpoints. AC:
- [x] **2026-03-15** -- T-P0-80: [B2] Frontend: Notes tab in NodeDetailPanel with markdown edit/preview + autosave. AC:
- [x] **2026-03-15** -- T-P0-79: [B2] Backend: expose description in framework tree API + extend node update schema. AC:
- [x] **2026-03-15** -- T-P0-78: [B1] CJK font support + install recharts + react-markdown. AC:
- [x] **2026-03-15** -- T-P0-77: [B1] Add useFilterParams hook + useDebounce hook. AC:
- [x] **2026-03-15** -- T-P0-76: [B1] Build shared UI components (Modal, ConfirmDialog, Badge, EmptyState, LoadingSpinner, SearchInput, Pagination). AC (REDUCED SCOPE -- build only what Batch 1 needs):
- [x] **2026-03-15** -- T-P0-75: [B1] Build Toast notification system (ToastContext + ToastProvider). AC:
- [x] **2026-03-15** -- T-P0-74: [B1] Migrate all pages from useApi to React Query useQuery/useMutation. AC:
