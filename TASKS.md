# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

### P1 -- Should Have (agentic intelligence)

#### T-P1-96: Auto-link company on timeline event creation via get_or_create_company
- **Priority**: P1
- **Complexity**: S
- **Depends on**: T-P1-95
- **Description**: ## Acceptance Criteria
1. timeline router create_event() calls get_or_create_company(event.company_name, db) to resolve company_id
2. timeline router update_event() does the same when company_name changes
3. EventFormModal onSuccess invalidates both ["timeline","events"] and ["companies"] queries
4. Tests: create event with new company -> Company auto-created; create event with existing name (different case) -> linked, no duplicate; update event company_name -> new Company if needed

#### T-P1-97: PrepNotesTab with checkbox click-toggle + Companies page integration
- **Priority**: P1
- **Complexity**: L
- **Depends on**: T-P1-95
- **Description**: ## Acceptance Criteria
1. New utils/markdown.ts: countUnchecked(md) and countChecked(md) using regex ^[-*]\s*\[ \] and ^[-*]\s*\[[xX]\]; toggleCheckbox(md, lineIndex) toggles [ ] <-> [x]
2. New PrepNotesTab component (companyId, initialNotes, onNotesChanged props):
   a. Edit/Preview toggle
   b. Preview mode: ReactMarkdown with custom li renderer -- clicking checkbox toggles state via toggleCheckbox(), triggers debounced save
   c. Edit mode: textarea with raw markdown
   d. Auto-save: 500ms debounce, useMutation PUT /companies/{id} with { prep_notes }
   e. Status: "Saving..." / "Saved" / "Save failed" (red text + retry button)
   f. Import button: file input (.md), POST /companies/{id}/prep-notes/import with FormData + mode radio (append default / replace)
   g. Invalidates ["companies"] on save
3. Company type updated: prep_notes: string | null added to Company and CompanyCreate
4. CompanyDetailPanel: "Prep" tab added with red dot badge showing unchecked count
5. CompanyCard: red dot indicator if prep_notes has unchecked items
6. Journey AC: User opens company -> clicks Prep tab -> imports .md -> sees rendered checklist -> clicks checkbox in preview -> toggles, red dot count decreases -> closes and reopens -> state persisted
7. Failure AC: Network error during save -> "Save failed" shown in red -> user clicks retry -> saves successfully

#### T-P1-98: Dashboard timeline prep notes modal + red dots on EventCard
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-97
- **Description**: ## Acceptance Criteria
1. InterviewTimeline: new onCompanyClick(companyName, companyId) prop
2. EventCard: company_name rendered as blue clickable text with e.stopPropagation() (clicking name opens prep modal, clicking card still opens edit event modal)
3. InterviewTimeline fetches /companies alongside events, builds Map<id, Company> lookup
4. Red dot next to company name on EventCard if countUnchecked(prep_notes) > 0
5. New PrepNotesModal: base Modal (max-w-2xl), fetches company, renders PrepNotesTab, has "View in Companies" navigation link
6. PrepNotesModal onClose: invalidates ["companies"] to sync red dots on Dashboard
7. Dashboard.tsx: state for prepCompanyId/Name, passes onCompanyClick to InterviewTimeline, renders PrepNotesModal
8. EventFormModal: onSuccess also invalidates ["companies"]
9. Journey AC: User sees red dot on "LinkedIn" in timeline -> clicks company name -> modal opens with prep checklist -> toggles checkbox -> closes modal -> red dot count updates on timeline
10. Inverse AC: Company with no prep_notes or all checked -> no red dot shown

### P2 -- Nice to Have

### P3 -- Stretch Goals

## Blocked

## Completed Tasks

> 87 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-03-16** -- T-P1-95: Add prep_notes to Company model + migration v3 + get_or_create_company service. ## Acceptance Criteria
- [x] **2026-03-15** -- T-P2-94: [B7] Frontend: Analytics deep-dive (radar chart, scatter plot, trend lines). AC:\n- Pattern comfort radar chart (Recharts RadarChart) on Problems page or Dashboard\n- Framework confidence vs import
- [x] **2026-03-15** -- T-P2-93: [B6] Frontend: QA session summarize button in ReviewPanel. AC:
- [x] **2026-03-15** -- T-P2-92: [B6] Frontend: Settings page (import/export + scraper management). AC:
- [x] **2026-03-15** -- T-P2-91: [B6] Frontend: Framework tree search + breadcrumb path. AC:
- [x] **2026-03-15** -- T-P2-90: [B6] Frontend: Kanban drag-and-drop for Companies page. AC:
- [x] **2026-03-15** -- T-P2-72: Add GET / root endpoint returning API info JSON
- [x] **2026-03-15** -- T-P2-68: Add combined backend+frontend startup script (scripts/dev.py)
