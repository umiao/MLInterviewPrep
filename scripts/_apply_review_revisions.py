"""Apply 7 task revisions from the user's external code-review pass.

Changes (acknowledged + applied):
  T-P1-358: add PRAGMA table_info assert at top of seed script (avoid silent
            seed-before-migration failure on SQLite)
  T-P1-359: add a methodological PID + module-path verification step BEFORE
            declaring stale-uvicorn as root cause (don't conclude on a
            "restart fixed it" result alone)
  T-P1-360: add staleTime: Infinity / keepPreviousData on the BQ themes useQuery
            so section toggling does not refetch
  T-P1-362: drop the drawer's second fetch entirely. The list_examples endpoint
            already returns full STAR (per schemas/behavioral.py line 105+:
            situation/task/action/result/evidence_quotes/principle_tags/
            risk_statement/analogy/tech_terms/linked_questions are all in
            BehavioralExampleResponse). Drawer just renders the already-loaded
            example object. Also adds an i18n typography sub-step for the
            CN/EN font fallback misalignment on the elevator-pitch pill split.
  T-P2-363: replace toy useReturnPath with REAL scroll restore via
            sessionStorage keyed by location.key + window.scrollY
  T-P2-364: replace 'NARRATION-RISK GUARD' substring marker with the
            specific sentinel '<!-- NRG-v1 -->' to avoid false-positive
            idempotency skips if the phrase appears in future content
  T-P2-365: tighten audit pass criterion: a story passes only if it has
            BOTH (a) a quantitative number in the Result section AND (b) a
            metric name + direction-of-change in the Action section. The
            old "1+ class" was too lax.

Declined (per meta-review):
  - QuickIndex subcomponent split (premature refactor)
  - Reorder T-P1-362 before T-P1-361 (technical reason was wrong)
  - Code-level FORBIDDEN guard in T-P2-364 (overkill on top of marker gating)

Credit:
  - The /themes counts contract is ALREADY locked in
    src/backend/schemas/behavioral_theme.py: question_count: int,
    example_count: int (non-Optional). Pydantic enforces. No fix needed.
"""
import sqlite3
from pathlib import Path

DB = Path(__file__).parent.parent / ".claude" / "tasks.db"


# ----------------------------------------------------------------------------
# T-P1-358 — add PRAGMA assert step
# ----------------------------------------------------------------------------

OLD_358 = "Script structure: connect to data/mle_prep.db, for each (example_id, pitch): UPDATE behavioral_examples SET cn_elevator_pitch=? WHERE example_id=?. Re-runnable. Use encoding='utf-8' for the script file."

NEW_358 = (
    "Script structure: connect to data/mle_prep.db, for each (example_id, pitch): UPDATE behavioral_examples SET cn_elevator_pitch=? WHERE example_id=?. Re-runnable. Use encoding='utf-8' for the script file.\n\n"
    "PREFLIGHT ASSERT (REQUIRED — added per code review): the script MUST run a PRAGMA table_info(behavioral_examples) check at the top and exit with a clear error if cn_elevator_pitch is not in the column list. SQLite will silently no-op an UPDATE on a missing column under certain pragma configurations, so a missing migration would otherwise produce a green run with zero rows actually updated. Pattern:\n\n"
    "    cols = {row[1] for row in conn.execute('PRAGMA table_info(behavioral_examples)').fetchall()}\n"
    "    if 'cn_elevator_pitch' not in cols:\n"
    "        raise SystemExit('cn_elevator_pitch column missing — run the migration in step 1 first')\n"
)


# ----------------------------------------------------------------------------
# T-P1-359 — add PID + module-path verification step
# ----------------------------------------------------------------------------

OLD_359 = "2. Restart the backend on port 8100:"

NEW_359 = (
    "2a. METHODOLOGY GUARD (REQUIRED — added per code review): before restarting, do NOT conclude stale-uvicorn from the symptom alone. Capture the running process's identity AND its loaded module path so you can verify the hypothesis after restart, instead of just declaring victory because the symptom went away.\n"
    "    - Find the PID: `lsof -i :8100` (Linux/macOS) or `netstat -ano | findstr :8100` (Windows). Record the PID.\n"
    "    - Confirm the process is the uvicorn we expect: `ps -p <PID> -o command=` (Linux) or `wmic process where ProcessId=<PID> get CommandLine` (Windows).\n"
    "    - Capture the routers/behavioral.py mtime AND a hash of its current contents on disk: `md5sum src/backend/routers/behavioral.py`.\n"
    "    - Note these in the commit message or PROGRESS entry as evidence.\n"
    "    - After restart, hit the endpoint and check that the response now includes the theme_tags key. If theme_tags now appears AND the on-disk md5 was the same before/after restart, you have proven the hypothesis (running module was older than the on-disk file). If theme_tags is still missing, the bug is in code and you must debug the join — do not write 'restart fixed it' as the resolution.\n\n"
    "2b. Restart the backend on port 8100:"
)


# ----------------------------------------------------------------------------
# T-P1-360 — add staleTime config to BQ themes query (the change actually
# lives in T-P1-361 since that's where the useQuery is added, but a forward-
# reference note in 360 is harmless and prevents accidental refetch when
# the toggle wires up)
# ----------------------------------------------------------------------------

# Actually T-P1-360 doesn't add the themes query at all (just placeholder).
# The fix belongs in T-P1-361 where the query is created. Apply it there.

OLD_361_QUERY = (
    "       const { data: themes } = useQuery({\n"
    "         queryKey: ['behavioral-themes'],\n"
    "         queryFn: () => api.get('/api/behavioral/themes').then(r => r.data),\n"
    "         enabled: section === 'bq',\n"
    "       });"
)

NEW_361_QUERY = (
    "       const { data: themes } = useQuery({\n"
    "         queryKey: ['behavioral-themes'],\n"
    "         queryFn: () => api.get('/api/behavioral/themes').then(r => r.data),\n"
    "         enabled: section === 'bq',\n"
    "         staleTime: Infinity,         // themes change rarely; never auto-refetch within a session\n"
    "         gcTime: 1000 * 60 * 60,      // keep cached for an hour even after unmount, so toggling sections doesn't trigger a refetch\n"
    "       });"
)


# ----------------------------------------------------------------------------
# T-P1-362 — drop drawer second fetch + i18n typography sub-step
# ----------------------------------------------------------------------------

OLD_362_DRAWER = (
    "3. Drawer:\n"
    "   - Use existing component src/frontend/src/components/ui/SlideOverPanel.tsx (already used by BehavioralQuestions).\n"
    "   - State: const [activeExampleId, setActiveExampleId] = useState<string | null>(null);\n"
    "   - When activeExampleId is set, fetch GET /api/behavioral/examples/by-example-id/<id> and pass to the existing src/frontend/src/components/behavioral/ExampleDrawerContent.tsx component.\n"
    "   - SlideOverPanel must dim background and close on outside click + Escape key (verify these props exist on SlideOverPanel; if not, add them — they are needed for path 1 of T-P2-363).\n"
    "   - CRITICAL: opening/closing the drawer must NOT change the URL. Use React state only. This way browser back from the theme page goes to /quick-index?section=bq, not back through every example the user opened."
)

NEW_362_DRAWER = (
    "3. Drawer (REVISED per code review — single fetch, no race condition):\n"
    "   - Use existing component src/frontend/src/components/ui/SlideOverPanel.tsx (already used by BehavioralQuestions).\n"
    "   - State: const [activeExample, setActiveExample] = useState<BehavioralExample | null>(null);\n"
    "     (Hold the FULL example object, not just the id.)\n"
    "   - When the user clicks an example card, call setActiveExample(example) — passing the already-loaded object from the examples list query. Do NOT issue a second fetch.\n"
    "   - The /api/behavioral/examples?theme=<slug> response already includes situation/task/action/result/evidence_quotes/principle_tags/risk_statement/analogy/tech_terms/linked_questions per BehavioralExampleResponse (src/backend/schemas/behavioral.py line 105+). Pass activeExample directly to ExampleDrawerContent — drawer becomes a pure render-from-props component, no useEffect / no loading state / no race condition possible.\n"
    "   - SlideOverPanel must dim background and close on outside click + Escape key (verify these props exist; if not, add them — needed for T-P2-363 path 1).\n"
    "   - CRITICAL: opening/closing the drawer must NOT change the URL. Use React state only. This way browser back from the theme page goes to /quick-index?section=bq, not back through every example the user opened."
)

OLD_362_AC = (
    "ACCEPTANCE:\n"
    "- New route and page render for all 15 theme slugs.\n"
    "- 5 failure-cluster examples render with Chinese pitch and key facts.\n"
    "- Clicking an example card opens the slide-over drawer with full STAR.\n"
    "- Drawer state is local React state (does NOT touch URL).\n"
    "- Back link and browser back both return to /quick-index?section=bq.\n"
    "- npm run build passes."
)

NEW_362_AC = (
    "6. i18n / typography sub-step (REQUIRED — added per code review): the cn_elevator_pitch is mixed CN/EN content rendered alongside English UI chrome. The ' | KEY FACTS: ' split produces pills with both CN and EN tokens, which will font-fallback differently in the same line and cause vertical misalignment.\n"
    "   - Use a single CSS class for the pill that explicitly sets font-family with both English and CJK fallbacks in order: e.g. `font-family: 'Inter', 'Noto Sans CJK SC', system-ui, sans-serif;` (or whatever the project's existing CN-capable font stack is — check src/frontend/src/index.css first to reuse).\n"
    "   - Set explicit `line-height` and `vertical-align: baseline` on the pill so the CN glyphs and EN glyphs do not produce row-height jitter.\n"
    "   - Manual smoke test: render a card with a pitch containing both Chinese and 'KEY FACTS:' English in the same pill row — verify glyphs sit on the same baseline, no row-height jitter.\n\n"
    "ACCEPTANCE:\n"
    "- New route and page render for all 15 theme slugs.\n"
    "- 5 failure-cluster examples render with Chinese pitch and key facts.\n"
    "- Clicking an example card opens the slide-over drawer with full STAR — using the already-loaded example object, NO second API fetch.\n"
    "- Drawer state is local React state (does NOT touch URL).\n"
    "- Back link and browser back both return to /quick-index?section=bq.\n"
    "- CN/EN typography on the pitch pills is verified visually — no font-fallback jitter.\n"
    "- npm run build passes."
)


# ----------------------------------------------------------------------------
# T-P2-363 — real scroll restore (sessionStorage + location.key)
# ----------------------------------------------------------------------------

OLD_363_HOOK = (
    "1. Create a small hook src/frontend/src/hooks/useReturnPath.ts:\n"
    "       import { useSearchParams } from 'react-router-dom';\n"
    "       export function useReturnPath(defaultPath: string): string {\n"
    "         const [params] = useSearchParams();\n"
    "         const from = params.get('from');\n"
    "         if (from === 'quick-index') return '/quick-index?section=bq';\n"
    "         return defaultPath;\n"
    "       }\n"
    "   Theme detail page uses this for its Back link with default '/quick-index?section=bq'.\n\n"
    "2. Add scroll position preservation:\n"
    "   - On the theme detail page, when opening the drawer, capture window.scrollY into a ref. When closing the drawer, restore it. (SlideOverPanel may already do this — verify.)\n"
    "   - On QuickIndex BQ section, no scroll restore needed unless theme list grows long; defer if not visible problem."
)

NEW_363_HOOK = (
    "1. Create the back-link hook at src/frontend/src/hooks/useReturnPath.ts:\n"
    "       import { useSearchParams } from 'react-router-dom';\n"
    "       export function useReturnPath(defaultPath: string): string {\n"
    "         const [params] = useSearchParams();\n"
    "         const from = params.get('from');\n"
    "         if (from === 'quick-index') return '/quick-index?section=bq';\n"
    "         return defaultPath;\n"
    "       }\n"
    "   Theme detail page uses this for its Back link.\n\n"
    "2. Real scroll position preservation (REVISED per code review — the previous 'capture into a ref' was a toy and would not survive a real navigation):\n\n"
    "   Create src/frontend/src/hooks/useScrollRestore.ts:\n\n"
    "       import { useEffect } from 'react';\n"
    "       import { useLocation } from 'react-router-dom';\n\n"
    "       const STORAGE_PREFIX = 'scroll:';\n\n"
    "       export function useScrollRestore(): void {\n"
    "         const location = useLocation();\n"
    "         // location.key is unique per history entry (react-router v6+); persisted across the same\n"
    "         // entry's lifetime even if component unmounts.\n"
    "         const storageKey = STORAGE_PREFIX + location.key;\n\n"
    "         // Save on unmount or before next route change\n"
    "         useEffect(() => {\n"
    "           const onScroll = () => {\n"
    "             sessionStorage.setItem(storageKey, String(window.scrollY));\n"
    "           };\n"
    "           window.addEventListener('scroll', onScroll, { passive: true });\n"
    "           return () => window.removeEventListener('scroll', onScroll);\n"
    "         }, [storageKey]);\n\n"
    "         // Restore on mount\n"
    "         useEffect(() => {\n"
    "           const stored = sessionStorage.getItem(storageKey);\n"
    "           if (stored !== null) {\n"
    "             // requestAnimationFrame so the page has rendered before we scroll\n"
    "             requestAnimationFrame(() => window.scrollTo(0, parseInt(stored, 10)));\n"
    "           }\n"
    "           // do NOT depend on storageKey for restore — only run once on mount\n"
    "           // eslint-disable-next-line react-hooks/exhaustive-deps\n"
    "         }, []);\n"
    "       }\n\n"
    "   Wire useScrollRestore() into the BehavioralThemePage component (top of component body) AND into QuickIndex (so the BQ section also restores after coming back from a theme detail page).\n\n"
    "   For drawer-open scroll preservation: the drawer is a slide-over overlay, so document scroll position is naturally preserved unless SlideOverPanel adds `body { overflow: hidden }` or similar. If it does, capture window.scrollY into a ref BEFORE the panel opens and restore it AFTER it closes. Verify in path 1 manual smoke test."
)


# ----------------------------------------------------------------------------
# T-P2-364 — sentinel marker
# ----------------------------------------------------------------------------

T_364_SUBSTITUTIONS = [
    # Replace bare 'NARRATION-RISK GUARD' substring marker with sentinel <!-- NRG-v1 -->
    # in the gating logic, while keeping the human-readable header in the appended text.
    ("gate on the marker substring 'NARRATION-RISK GUARD' — if already present, skip", "gate on the sentinel string '<!-- NRG-v1 -->' — if already present in risk_statement, skip. Use a specific sentinel rather than a substring of the human-readable header to avoid false-positive idempotency skips if the phrase 'NARRATION-RISK GUARD' appears in any future content"),
    ("gate on the marker substring 'TEMPORAL POV' — if already present, skip", "gate on the sentinel string '<!-- TPV-v1 -->' — if already present in risk_statement, skip. Use a specific sentinel rather than a substring of the human-readable header to avoid false positives"),
    # Append the sentinels into the templates themselves
    ("\\n\\nNARRATION-RISK GUARD: This is a 'failure that became a process improvement' story.", "\\n\\n<!-- NRG-v1 --> NARRATION-RISK GUARD: This is a 'failure that became a process improvement' story."),
    ("\\n\\nNARRATION-RISK GUARD + TEMPORAL POV: This story has a redemption tail", "\\n\\n<!-- NRG-v1 --> <!-- TPV-v1 --> NARRATION-RISK GUARD + TEMPORAL POV: This story has a redemption tail"),
    ("\\n\\nNARRATION-RISK GUARD: The temptation in this story", "\\n\\n<!-- NRG-v1 --> NARRATION-RISK GUARD: The temptation in this story"),
    ("\\n\\nNARRATION-RISK GUARD: See existing 'Use this story for failure-type questions...' clause above.", "\\n\\n<!-- NRG-v1 --> NARRATION-RISK GUARD: See existing 'Use this story for failure-type questions...' clause above."),
    # Verification asserts switch from 'NARRATION-RISK GUARD' to '<!-- NRG-v1 -->'
    ("assert 'NARRATION-RISK GUARD' in risk_statement", "assert '<!-- NRG-v1 -->' in risk_statement  # sentinel, not human-readable header"),
    ("assert 'TEMPORAL POV' in risk_statement", "assert '<!-- TPV-v1 -->' in risk_statement  # sentinel, not human-readable header"),
    ("assert \"NARRATION-RISK GUARD\" in d[\"risk_statement\"]", "assert '<!-- NRG-v1 -->' in d['risk_statement']"),
    ("- All 4 stories have a 'NARRATION-RISK GUARD' marker string in risk_statement.", "- All 4 stories have the sentinel '<!-- NRG-v1 -->' in risk_statement (specific sentinel chosen to avoid false-positive idempotency skips on future content containing the human-readable phrase)."),
    ("- EX-16 specifically also has 'TEMPORAL POV' language.", "- EX-16 specifically also has the sentinel '<!-- TPV-v1 -->' in risk_statement."),
]


# ----------------------------------------------------------------------------
# T-P2-365 — tighten audit criterion
# ----------------------------------------------------------------------------

OLD_365 = "verify it contains AT LEAST ONE of: (a) a quantitative number in the Result section (e.g., '+1% GMB', '200M+', 'p99 latency dropped 30%'), (b) a metric name and direction-of-change in the Action section, (c) an A/B test reference, (d) a data-derived hypothesis driving the technical decision. If an example has none of these"

NEW_365 = (
    "verify it contains BOTH (a) a quantitative number in the Result section (e.g., '+1% GMB', '200M+', 'p99 latency dropped 30%') AND (b) a metric name and direction-of-change in the Action section. (a)+(b) together is the bar for a real data-driven story; either one alone is too easy to satisfy with hand-waving (per code-review tightening). (c) an A/B test reference and (d) a data-derived hypothesis are STRONG SUPPORTING evidence — if an example has (c) or (d) plus only one of (a)/(b), it can be marked NEEDS-NOTE rather than RECOMMEND-UNTAG. If an example has neither (a) nor (b)"
)


def apply_substitution(c: sqlite3.Cursor, task_id: str, old: str, new: str, *, required: bool = True) -> None:
    c.execute("SELECT description FROM tasks WHERE id=?", (task_id,))
    desc = c.fetchone()[0]
    if old not in desc:
        if required:
            raise SystemExit(f"{task_id}: substitution OLD not found:\n  {old[:100]}...")
        return
    if new in desc:
        print(f"  [skip] {task_id}: NEW already present")
        return
    desc = desc.replace(old, new)
    c.execute("UPDATE tasks SET description=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", (desc, task_id))
    print(f"  [ok]   {task_id}: substituted ({len(old)} -> {len(new)} chars)")


def main() -> None:
    conn = sqlite3.connect(str(DB))
    c = conn.cursor()

    print("=== T-P1-358 (PRAGMA assert) ===")
    apply_substitution(c, "T-P1-358", OLD_358, NEW_358)

    print("=== T-P1-359 (methodology guard) ===")
    apply_substitution(c, "T-P1-359", OLD_359, NEW_359)

    print("=== T-P1-361 (staleTime + gcTime) ===")
    apply_substitution(c, "T-P1-361", OLD_361_QUERY, NEW_361_QUERY)

    print("=== T-P1-362 (drop second fetch + i18n typography) ===")
    apply_substitution(c, "T-P1-362", OLD_362_DRAWER, NEW_362_DRAWER)
    apply_substitution(c, "T-P1-362", OLD_362_AC, NEW_362_AC)

    print("=== T-P2-363 (real scroll restore) ===")
    apply_substitution(c, "T-P2-363", OLD_363_HOOK, NEW_363_HOOK)

    print("=== T-P2-364 (sentinel markers) ===")
    for old, new in T_364_SUBSTITUTIONS:
        apply_substitution(c, "T-P2-364", old, new, required=False)

    print("=== T-P2-365 (tighten audit) ===")
    apply_substitution(c, "T-P2-365", OLD_365, NEW_365)

    conn.commit()

    # Final lengths
    print()
    print("=== final task description lengths ===")
    for tid in ["T-P1-358", "T-P1-359", "T-P1-360", "T-P1-361", "T-P1-362", "T-P2-363", "T-P2-364", "T-P2-365"]:
        c.execute("SELECT length(description) FROM tasks WHERE id=?", (tid,))
        print(f"  {tid}: {c.fetchone()[0]} chars")
    conn.close()


if __name__ == "__main__":
    main()
