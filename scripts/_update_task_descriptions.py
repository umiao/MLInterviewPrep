"""One-shot: rewrite task descriptions with content that includes shell-hostile chars.

Direct SQL UPDATE on .claude/tasks.db -- bypasses task_db.py CLI to avoid bash quoting.
Idempotent (just overwrites the description column for each id listed below).
"""
import sqlite3
from pathlib import Path

DB = Path(__file__).parent.parent / ".claude" / "tasks.db"

T_360 = """Restructure src/frontend/src/pages/QuickIndex.tsx — add a top toggle bar so the user can show ONE of three sections at a time: LeetCode / ML coding / Behavioral Questions.

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
"""

T_361 = """Inside the BQ section of QuickIndex (placeholder added by T-P1-360), render the 15 behavioral_themes as cards grouped by semantic cluster family.

DEPENDS ON: T-P1-359 (theme filter API fix) and T-P1-360 (BQ section placeholder).

EXECUTION STEPS:

1. Add a useQuery for the themes endpoint at the top of QuickIndex.tsx (when section==='bq'):

       const { data: themes } = useQuery({
         queryKey: ['behavioral-themes'],
         queryFn: () => api.get('/api/behavioral/themes').then(r => r.data),
         enabled: section === 'bq',
       });

   The endpoint already exists at /api/behavioral/themes (see routers/behavioral.py list_themes around line 155). Each theme has: id, slug, label, description, display_order, question_count, example_count.

2. Define the cluster-family grouping inline (one source of truth, do not split into a separate file unless 3+ pages need it):

       const CLUSTER_FAMILIES: { id: string; label: string; theme_slugs: string[] }[] = [
         { id: 'failure',    label: 'Failure & Ownership',    theme_slugs: ['failure_setback', 'ownership_accountability'] },
         { id: 'conflict',   label: 'Conflict & Collaboration', theme_slugs: ['conflict_disagreement', 'collaboration_teamwork'] },
         { id: 'decision',   label: 'Decision under Ambiguity', theme_slugs: ['prioritization_tradeoffs', 'ambiguity_uncertainty', 'scope_creep_ambiguous'] },
         { id: 'execution',  label: 'Execution & Pressure',   theme_slugs: ['deadline_pressure', 'process_systems', 'oncall_prod_incident'] },
         { id: 'leadership', label: 'Leadership & People',    theme_slugs: ['leadership_direction', 'mentoring_coaching'] },
         { id: 'technical',  label: 'Technical Depth',         theme_slugs: ['technical_problem_solving', 'code_quality_tech_debt', 'data_analysis'] },
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
   - Open /quick-index?section=bq — verify all 6 family headings appear in order
   - Verify each family contains the expected theme cards
   - Verify counts match what is in the DB (failure_setback should now show 5 examples, ~15 questions)
   - Click failure_setback card — verify navigation to /behavioral/theme/failure_setback?from=quick-index (T-P1-362 wires up the destination page)
   - Refresh — counts still load
   - Verify dimmed card if any theme has 0 questions and 0 examples

ACCEPTANCE:
- All 15 themes render in 6 family groups.
- Counts come from /api/behavioral/themes (not hardcoded).
- Click navigation produces the correct URL with the from param.
- The failure_setback card shows 5 examples after T-P1-358 + this task.
- npm run build passes.
"""

T_362 = """New page at route /behavioral/theme/:slug for the BQ theme detail view. Add the route in src/frontend/src/App.tsx and create the page component.

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

3. Drawer:
   - Use existing component src/frontend/src/components/ui/SlideOverPanel.tsx (already used by BehavioralQuestions).
   - State: const [activeExampleId, setActiveExampleId] = useState<string | null>(null);
   - When activeExampleId is set, fetch GET /api/behavioral/examples/by-example-id/<id> and pass to the existing src/frontend/src/components/behavioral/ExampleDrawerContent.tsx component.
   - SlideOverPanel must dim background and close on outside click + Escape key (verify these props exist on SlideOverPanel; if not, add them — they are needed for path 1 of T-P2-363).
   - CRITICAL: opening/closing the drawer must NOT change the URL. Use React state only. This way browser back from the theme page goes to /quick-index?section=bq, not back through every example the user opened.

4. Empty state: if examples.length === 0, render a friendly message 'No master stories tagged to this theme yet.' Do not crash.

5. Manual smoke test (run in browser, not just type-check):
   - Navigate /quick-index?section=bq -> click 'Failure & Setback' -> URL becomes /behavioral/theme/failure_setback?from=quick-index
   - Verify 5 example cards render: EX-15, EX-16, EX-17, EX-30, EX-33B, each showing the Chinese pitch from T-P1-358
   - Click EX-33B card -> drawer opens with full STAR
   - Press Escape -> drawer closes, URL unchanged, scroll position retained
   - Click 'Back' link -> returns to /quick-index?section=bq (BQ section still visible)
   - Browser back from theme page (without going through Back link) -> also returns to /quick-index?section=bq

ACCEPTANCE:
- New route and page render for all 15 theme slugs.
- 5 failure-cluster examples render with Chinese pitch and key facts.
- Clicking an example card opens the slide-over drawer with full STAR.
- Drawer state is local React state (does NOT touch URL).
- Back link and browser back both return to /quick-index?section=bq.
- npm run build passes.
"""

T_363 = """Audit and fix end-to-end navigation paths so user never loses browse context across QuickIndex(BQ) -> theme detail -> example drawer.

DEPENDS ON: T-P1-361 and T-P1-362.

PATHS THAT MUST WORK:

1. QuickIndex(BQ) -> click theme card -> theme detail -> click example -> drawer opens -> close drawer -> still on theme detail page with scroll position preserved.
2. theme detail -> click 'Back' link -> /quick-index?section=bq (BQ section still selected).
3. Browser back button from theme detail -> /quick-index?section=bq (same as path 2).
4. Deep link directly to /behavioral/theme/failure_setback?from=quick-index (no prior visit to QuickIndex) -> Back link still navigates to /quick-index?section=bq (graceful default for from-less case too).
5. /quick-index?section=bq refresh -> BQ section still rendered (already covered by T-P1-360, re-verify).
6. /quick-index?section=ml -> click any LC link (cross-section) -> navigate forward -> browser back -> /quick-index?section=ml (URL preserved, not reset to default).

EXECUTION STEPS:

1. Create a small hook src/frontend/src/hooks/useReturnPath.ts:
       import { useSearchParams } from 'react-router-dom';
       export function useReturnPath(defaultPath: string): string {
         const [params] = useSearchParams();
         const from = params.get('from');
         if (from === 'quick-index') return '/quick-index?section=bq';
         return defaultPath;
       }
   Theme detail page uses this for its Back link with default '/quick-index?section=bq'.

2. Add scroll position preservation:
   - On the theme detail page, when opening the drawer, capture window.scrollY into a ref. When closing the drawer, restore it. (SlideOverPanel may already do this — verify.)
   - On QuickIndex BQ section, no scroll restore needed unless theme list grows long; defer if not visible problem.

3. Verify SlideOverPanel does NOT add a history entry. If it does (e.g., uses useNavigate), refactor to local state — this is the critical bug to prevent path 3 from getting stuck inside the drawer history.

4. Manual smoke test ALL 6 paths in a real browser. For each path, write a one-line PASS/FAIL note in the PR description or commit message.

5. Optional but recommended: add a Playwright e2e test under tests/frontend/e2e/behavioral_navigation.spec.ts covering paths 1-3 if the project already has Playwright set up. If not, do not add the framework in this task — flag as a future task.

ACCEPTANCE:
- All 6 paths verified manually with PASS notes.
- Theme detail Back link works for both ?from=quick-index and the no-from case.
- Drawer open/close does not pollute browser history.
- Scroll position restored after drawer close.
- npm run build passes.
"""

T_364 = """COLLABORATIVE TASK — DO NOT EXECUTE AUTONOMOUSLY. This task must be run in the main conversation with the user, like the EX-33B polishing session, because each story revision needs user fact-check before commit.

Polish the 4 remaining failure-cluster master stories (EX-15, EX-16, EX-17, EX-30) to match the EX-30 / EX-33B gold-standard structure.

PER-STORY CURRENT-STATE FINDINGS (from session 2026-04-11 survey):

EX-15 Model Deprecation Incident:
- Action is bullet form, no realization beat
- NO evidence_quotes
- NO analogy
- principle_tags = [adaptability, ownership, innovation] — missing 'failure' tag
- risk_statement focuses on technical impact, not narration risk
- Needs: realization beat in Action, 2+ quotes, 1 analogy, 'failure' tag, narration-risk guard

EX-16 Cross-DC Deployment Incident:
- Same gaps as EX-15 (bullet Action, no quotes, no analogy, weak tags)
- CRITICAL: R section has a redemption tail ('this directly led to being invited to participate in the declarative artifactory initiative') — same disguised-success trap as old EX-33. Needs a TEMPORAL POV / narration-stop guard like EX-33B's risk_statement: 'For pure-failure questions stop at the lesson, not at the artifactory tail.'

EX-17 Difficult Feedback from Senior IC:
- Already enriched in T-P2-356 spot-check (root-cause paragraph appended)
- Still missing: quote(s), analogy, 'failure' tag
- Smallest delta of the four

EX-30 Hash Capability Misdesign:
- Already gold standard (4-beat narrative, 3 quotes, analogy, 'this is not a happy ending' line, 'failure' tag)
- Only delta: align principle_tags with the failure_setback theme convention (probably no change needed)

WORKFLOW (per story, in main conversation):
1. Read full STAR fields from DB.
2. Draft revisions field-by-field. Send to user for fact-check.
3. After user approval, write a per-story idempotent patch script under scripts/_polish_<example_id>.py (mirroring scripts/_patch_ex33b_kpi.py pattern).
4. Run, verify via /api/behavioral/examples/by-example-id/<id>.
5. Commit with [T-P2-364] prefix.

PER-STORY ACCEPTANCE (gate before commit):
- Action narrates a moment-of-realization beat (not just bullets).
- At least 2 evidence_quotes.
- At least 1 analogy.
- risk_statement includes a NARRATION-RISK guard (what the storyteller should NOT include / where to stop), not just technical impact.
- principle_tags includes 'failure' (or equivalent humility/learning tag).

DEPENDS ON: T-P1-358 — the cn_elevator_pitch should already be populated for these 5 by T-P1-358. This task can refine the pitch wording per story but should not introduce new pitches from scratch.

DO NOT mark this task as autonomously executable. The orchestrator should skip this task and only the human + main session should pick it up."""


UPDATES = {
    "T-P1-360": T_360,
    "T-P1-361": T_361,
    "T-P1-362": T_362,
    "T-P2-363": T_363,
    "T-P2-364": T_364,
}


def main() -> None:
    conn = sqlite3.connect(str(DB))
    c = conn.cursor()
    for tid, desc in UPDATES.items():
        c.execute(
            "UPDATE tasks SET description = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (desc, tid),
        )
        if c.rowcount != 1:
            print(f"[warn] {tid}: rowcount={c.rowcount}")
        else:
            print(f"[ok] {tid}: {len(desc)} chars")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
