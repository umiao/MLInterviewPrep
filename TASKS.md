# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

### P1 -- Should Have (agentic intelligence)

#### T-P1-360: QuickIndex: add section toggle bar (LC / ML coding / BQ)
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Restructure src/frontend/src/pages/QuickIndex.tsx — add a top toggle bar so the user can show ONE of three sections at a time: LeetCode / ML coding / Behavioral Questions.

EXECUTION STEPS:

1. Split the existing hardcoded 'problems' array (lines 3-20) into TWO arrays at the top of the file:
   - LC_PROBLEMS: items where lcId is defined
   - ML_PROBLEMS: items where lcId is undefined (currently 'K-Means (K-Means++)' and 'Lock Combination BFS (Bidirectional)')

2. Add a SECTION_TYPE union and useSearchParams hook to read/write ?section=lc|ml|bq:
       import { useSearchParams } from 'react-router-dom';
       const [params, setParams] = useSearchParams();
       const section = (params.get('section') as 'lc'|'ml'|'bq') || 'lc';

3. Render a top button row using existing Tailwind utility classes from this codebase (match the style of the existing rounded-lg border-gray-200 cards). Reference snippet (use template literal for the className with the active/inactive ternary):

       <div className="flex gap-2 mb-6">
         {(['lc','ml','bq'] as const).map(s => (
           <button
             key={s}
             onClick={() => setParams({ section: s })}
             className={
               'px-4 py-2 rounded-lg border text-sm font-medium transition-all ' +
               (section === s
                 ? 'border-blue-500 bg-blue-50 text-blue-700'
                 : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300')
             }
           >
             {s === 'lc' ? 'LeetCode' : s === 'ml' ? 'ML Coding' : 'Behavioral'}
           </button>
         ))}
       </div>

   (String concatenation is used instead of a template literal so this description is robust to shell quoting; either form is acceptable in the actual code.)

4. Render conditionally:
   - section === 'lc'  ->  existing grid using LC_PROBLEMS
   - section === 'ml'  ->  existing grid using ML_PROBLEMS
   - section === 'bq'  ->  placeholder div with text 'Coming soon (filled in by T-P1-361)' — leave it intentionally empty here. Do NOT scope-creep into BQ rendering in this task.

5. Default behavior: if no ?section= param, treat as 'lc'. Do not rewrite the URL until the user clicks a toggle.

6. Manual smoke test (REQUIRED — npm run build is necessary but not sufficient):
   - Restart vite (cd src/frontend && npm run dev, runs on 5173)
   - Open http://localhost:5173/quick-index — verify default view = LeetCode grid (14 cards)
   - Click 'ML Coding' — verify shows 2 cards (K-Means, Lock Combo BFS), URL updates to /quick-index?section=ml
   - Click 'Behavioral' — verify shows the placeholder, URL updates to /quick-index?section=bq
   - Refresh on /quick-index?section=ml — verify ML section is still selected
   - Browser back from BQ -> ML -> LC -> works
   - cd src/frontend && npm run build (which is tsc -b && vite build, per project rule) is clean

ACCEPTANCE:
- 3 toggle buttons render at top of QuickIndex.
- Only one section visible at a time.
- ?section= URL param round-trips (refresh + back button work).
- Existing 16 problems split correctly: 14 LC + 2 ML.
- BQ section placeholder explicitly says it is filled in by T-P1-361.
- npm run build passes.

#### T-P1-361: QuickIndex BQ section: render theme cards grouped by cluster
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-359
- **Description**: Inside the BQ section of QuickIndex (placeholder added by T-P1-360), render the 15 behavioral_themes as cards grouped by semantic cluster family.

DEPENDS ON: T-P1-359 (theme filter API fix) and T-P1-360 (BQ section placeholder).

EXECUTION STEPS:

1. Add a useQuery for the themes endpoint at the top of QuickIndex.tsx (when section==='bq'):

       const { data: themes } = useQuery({
         queryKey: ['behavioral-themes'],
         queryFn: () => api.get('/api/behavioral/themes').then(r => r.data),
         enabled: section === 'bq',
         staleTime: Infinity,         // themes change rarely; never auto-refetch within a session
         gcTime: 1000 * 60 * 60,      // keep cached for an hour even after unmount, so toggling sections doesn't trigger a refetch
       });

   The endpoint already exists at /api/behavioral/themes (see routers/behavioral.py list_themes around line 155). Each theme has: id, slug, label, description, display_order, question_count, example_count.

2. Define the cluster-family grouping inline (one source of truth, do not split into a separate file unless 3+ pages need it):

       const CLUSTER_FAMILIES: { id: string; label: string; theme_slugs: string[] }[] = [
         { id: 'failure',    label: 'Failure & Ownership',    theme_slugs: ['failure_setback', 'ownership_accountability'] },
         { id: 'conflict',   label: 'Conflict & Collaboration', theme_slugs: ['conflict_disagreement', 'collaboration_teamwork'] },
         { id: 'decision',   label: 'Decision under Ambiguity', theme_slugs: ['prioritization_tradeoffs', 'ambiguity_uncertainty', 'scope_creep_ambiguous'] },
         { id: 'execution',  label: 'Execution & Pressure',   theme_slugs: ['deadline_pressure', 'process_systems', 'oncall_prod_incident'] },
         { id: 'leadership', label: 'Leadership & People',    theme_slugs: ['leadership_direction', 'mentoring_coaching'] },
         { id: 'technical',  label: 'Technical Depth',         theme_slugs: ['technical_problem_solving', 'code_quality_tech_debt'] },
         { id: 'data',       label: 'Data and Decisions',      theme_slugs: ['data_analysis'] },
       ];

   Verify all 15 theme slugs are covered exactly once. If a future theme is added without a family, render it under an 'Other' family at the bottom (do not crash).

3. For each family, render a section: a small label + a flex/grid of theme cards. Each theme card:
   - Theme label (large)
   - 'N questions / M examples' subtitle
   - Hover state matching the existing LC card style
   - Wrapped in a Link to /behavioral/theme/<slug>?from=quick-index
   - If question_count===0 AND example_count===0, dim the card (text-gray-400) — do not hide it.

   Use grid-cols-2 md:grid-cols-3 lg:grid-cols-4 to match the LC grid feel. Family heading is text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2.

4. Manual smoke test:
   - Open /quick-index?section=bq — verify all 7 family headings appear in order
   - Verify each family contains the expected theme cards
   - Verify counts match what is in the DB (failure_setback should now show 5 examples, ~15 questions)
   - Click failure_setback card — verify navigation to /behavioral/theme/failure_setback?from=quick-index (T-P1-362 wires up the destination page)
   - Refresh — counts still load
   - Verify dimmed card if any theme has 0 questions and 0 examples

ACCEPTANCE:
- All 15 themes render in 7 family groups.
- Counts come from /api/behavioral/themes (not hardcoded).
- Click navigation produces the correct URL with the from param.
- The failure_setback card shows 5 examples after T-P1-358 + this task.
- npm run build passes.

#### T-P1-362: BQ theme detail page: example cards with Chinese pitch + STAR drawer
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-358, T-P1-359
- **Description**: New page at route /behavioral/theme/:slug for the BQ theme detail view. Add the route in src/frontend/src/App.tsx and create the page component.

DEPENDS ON: T-P1-358 (cn_elevator_pitch field), T-P1-359 (theme filter on /examples).

EXECUTION STEPS:

1. Add new route in App.tsx (right after the existing 'behavioral' route):
       <Route path="behavioral/theme/:slug" element={<BehavioralThemePage />} />

2. Create new file src/frontend/src/pages/BehavioralThemePage.tsx with the following structure:

   - Read :slug via useParams<{slug: string}>().
   - Read ?from= via useSearchParams (used by the back link).
   - Three queries (or one combined query if you add /api/behavioral/themes/<slug>/detail later):
       (a) themes: GET /api/behavioral/themes — find the matching theme by slug
       (b) examples: GET /api/behavioral/examples?theme=<slug> — depends on T-P1-359 fix
       (c) questions: GET /api/behavioral/questions?theme=<slug>
   - Page header:
       <header>
         <Link to={returnUrl}>← Back</Link>  // returnUrl = '/quick-index?section=bq' if from==='quick-index', else '/quick-index?section=bq'
         <h1>{theme.label}</h1>
         <div>{theme.description}</div>
         <div>{theme.question_count} questions · {theme.example_count} examples</div>
       </header>
   - Examples grid: render each example as a card with:
       - example_id (small mono badge)
       - title (English)
       - cn_elevator_pitch — IF NULL, fall back to title in italic-gray. Split the pitch on the ' | ' separator to display key facts as bullet pills.
       - onClick: setActiveExampleId(example.example_id)
   - Questions list (smaller, below): plain bullet list of question texts with the question_id as a leading mono badge.

3. Drawer (REVISED per code review — single fetch, no race condition):
   - Use existing component src/frontend/src/components/ui/SlideOverPanel.tsx (already used by BehavioralQuestions).
   - State: const [activeExample, setActiveExample] = useState<BehavioralExample | null>(null);
     (Hold the FULL example object, not just the id.)
   - When the user clicks an example card, call setActiveExample(example) — passing the already-loaded object from the examples list query. Do NOT issue a second fetch.
   - The /api/behavioral/examples?theme=<slug> response already includes situation/task/action/result/evidence_quotes/principle_tags/risk_statement/analogy/tech_terms/linked_questions per BehavioralExampleResponse (src/backend/schemas/behavioral.py line 105+). Pass activeExample directly to ExampleDrawerContent — drawer becomes a pure render-from-props component, no useEffect / no loading state / no race condition possible.
   - SlideOverPanel must dim background and close on outside click + Escape key (verify these props exist; if not, add them — needed for T-P2-363 path 1).
   - CRITICAL: opening/closing the drawer must NOT change the URL. Use React state only. This way browser back from the theme page goes to /quick-index?section=bq, not back through every example the user opened.

4. Empty state: if examples.length === 0, render a friendly message 'No master stories tagged to this theme yet.' Do not crash.

5. Manual smoke test (run in browser, not just type-check):
   - Navigate /quick-index?section=bq -> click 'Failure & Setback' -> URL becomes /behavioral/theme/failure_setback?from=quick-index
   - Verify 5 example cards render: EX-15, EX-16, EX-17, EX-30, EX-33B, each showing the Chinese pitch from T-P1-358
   - Click EX-33B card -> drawer opens with full STAR
   - Press Escape -> drawer closes, URL unchanged, scroll position retained
   - Click 'Back' link -> returns to /quick-index?section=bq (BQ section still visible)
   - Browser back from theme page (without going through Back link) -> also returns to /quick-index?section=bq

6. i18n / typography sub-step (REQUIRED — added per code review): the cn_elevator_pitch is mixed CN/EN content rendered alongside English UI chrome. The ' | KEY FACTS: ' split produces pills with both CN and EN tokens, which will font-fallback differently in the same line and cause vertical misalignment.
   - Use a single CSS class for the pill that explicitly sets font-family with both English and CJK fallbacks in order: e.g. `font-family: 'Inter', 'Noto Sans CJK SC', system-ui, sans-serif;` (or whatever the project's existing CN-capable font stack is — check src/frontend/src/index.css first to reuse).
   - Set explicit `line-height` and `vertical-align: baseline` on the pill so the CN glyphs and EN glyphs do not produce row-height jitter.
   - Manual smoke test: render a card with a pitch containing both Chinese and 'KEY FACTS:' English in the same pill row — verify glyphs sit on the same baseline, no row-height jitter.

ACCEPTANCE:
- New route and page render for all 15 theme slugs.
- 5 failure-cluster examples render with Chinese pitch and key facts.
- Clicking an example card opens the slide-over drawer with full STAR — using the already-loaded example object, NO second API fetch.
- Drawer state is local React state (does NOT touch URL).
- Back link and browser back both return to /quick-index?section=bq.
- CN/EN typography on the pitch pills is verified visually — no font-fallback jitter.
- npm run build passes.

### P2 -- Nice to Have

#### T-P2-363: BQ navigation: end-to-end browse-path preservation across QuickIndex/theme/drawer
- **Priority**: P2
- **Complexity**: S
- **Depends on**: T-P1-361, T-P1-362
- **Description**: Audit and fix end-to-end navigation paths so user never loses browse context across QuickIndex(BQ) -> theme detail -> example drawer.

DEPENDS ON: T-P1-361 and T-P1-362.

PATHS THAT MUST WORK:

1. QuickIndex(BQ) -> click theme card -> theme detail -> click example -> drawer opens -> close drawer -> still on theme detail page with scroll position preserved.
2. theme detail -> click 'Back' link -> /quick-index?section=bq (BQ section still selected).
3. Browser back button from theme detail -> /quick-index?section=bq (same as path 2).
4. Deep link directly to /behavioral/theme/failure_setback?from=quick-index (no prior visit to QuickIndex) -> Back link still navigates to /quick-index?section=bq (graceful default for from-less case too).
5. /quick-index?section=bq refresh -> BQ section still rendered (already covered by T-P1-360, re-verify).
6. /quick-index?section=ml -> click any LC link (cross-section) -> navigate forward -> browser back -> /quick-index?section=ml (URL preserved, not reset to default).

EXECUTION STEPS:

1. Create the back-link hook at src/frontend/src/hooks/useReturnPath.ts:
       import { useSearchParams } from 'react-router-dom';
       export function useReturnPath(defaultPath: string): string {
         const [params] = useSearchParams();
         const from = params.get('from');
         if (from === 'quick-index') return '/quick-index?section=bq';
         return defaultPath;
       }
   Theme detail page uses this for its Back link.

2. Real scroll position preservation (REVISED per code review — the previous 'capture into a ref' was a toy and would not survive a real navigation):

   Create src/frontend/src/hooks/useScrollRestore.ts:

       import { useEffect } from 'react';
       import { useLocation } from 'react-router-dom';

       const STORAGE_PREFIX = 'scroll:';

       export function useScrollRestore(): void {
         const location = useLocation();
         // location.key is unique per history entry (react-router v6+); persisted across the same
         // entry's lifetime even if component unmounts.
         const storageKey = STORAGE_PREFIX + location.key;

         // Save on unmount or before next route change
         useEffect(() => {
           const onScroll = () => {
             sessionStorage.setItem(storageKey, String(window.scrollY));
           };
           window.addEventListener('scroll', onScroll, { passive: true });
           return () => window.removeEventListener('scroll', onScroll);
         }, [storageKey]);

         // Restore on mount
         useEffect(() => {
           const stored = sessionStorage.getItem(storageKey);
           if (stored !== null) {
             // requestAnimationFrame so the page has rendered before we scroll
             requestAnimationFrame(() => window.scrollTo(0, parseInt(stored, 10)));
           }
           // do NOT depend on storageKey for restore — only run once on mount
           // eslint-disable-next-line react-hooks/exhaustive-deps
         }, []);
       }

   Wire useScrollRestore() into the BehavioralThemePage component (top of component body) AND into QuickIndex (so the BQ section also restores after coming back from a theme detail page).

   For drawer-open scroll preservation: the drawer is a slide-over overlay, so document scroll position is naturally preserved unless SlideOverPanel adds `body { overflow: hidden }` or similar. If it does, capture window.scrollY into a ref BEFORE the panel opens and restore it AFTER it closes. Verify in path 1 manual smoke test.

3. Verify SlideOverPanel does NOT add a history entry. If it does (e.g., uses useNavigate), refactor to local state — this is the critical bug to prevent path 3 from getting stuck inside the drawer history.

4. Manual smoke test ALL 6 paths in a real browser. For each path, write a one-line PASS/FAIL note in the PR description or commit message.

5. Optional but recommended: add a Playwright e2e test under tests/frontend/e2e/behavioral_navigation.spec.ts covering paths 1-3 if the project already has Playwright set up. If not, do not add the framework in this task — flag as a future task.

ACCEPTANCE:
- All 6 paths verified manually with PASS notes.
- Theme detail Back link works for both ?from=quick-index and the no-from case.
- Drawer open/close does not pollute browser history.
- Scroll position restored after drawer close.
- npm run build passes.

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

- [x] **2026-04-11** -- T-P2-356: Behavioral: semantic relevance spot-check script for 10 random Q-example links. # Behavioral: semantic relevance spot-check script for 10 random Q-example links
- [x] **2026-04-11** -- T-P2-324: [DEBT] helixos: Sync dev deps from requirements.txt to pyproject.toml. 6 packages in requirements.txt not in pyproject.toml: httpx, ruff, pytest-asyncio, mypy, pytest, pytest-timeout. Add as 
- [x] **2026-04-11** -- T-P2-323: [DEBT] MLInterviewPrep: Sync dev deps from requirements.txt to pyproject.toml. 6 packages in requirements.txt not in pyproject.toml: pytest, pytest-asyncio, beautifulsoup4, pyyaml, ruff, playwright. 
- [x] **2026-04-11** -- T-P2-322: [DEBT] MLInterviewPrep: Add problems.db to .gitignore. problems.db is untracked in MLInterviewPrep git repo and not in .gitignore. The .gitignore already covers interview_prep
- [x] **2026-04-11** -- T-P2-321: [SYNC] helixos: Propagate 3 new lessons from MLInterviewPrep 2026-04-08. Three new MLInterviewPrep LESSONS.md entries not yet in helixos: (1) autonomous_run.sh uses sub-project task_db not root
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
