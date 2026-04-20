# Behavioral UI + Golden Flag Integration Plan (T-GOLD-07)

Discovery notes for T-P2-558 feeding into the T-P2-559 (07b) implementation.
Covers: drawer existence/placement, react-query cache invalidation, card-list
surfaces for `goldenCardClass` + `GoldenBadge`, PUT endpoint confirmation, and
the 07b complexity estimate.

## 1. Drawer component -- does a BehavioralExampleDrawer exist?

Yes, effectively. There is no `BehavioralExampleDrawer.tsx` file per se, but the
drawer UX is implemented as:

- **Shell**: `src/frontend/src/components/ui/SlideOverPanel.tsx`
  (the same shared panel used by `FrameworkNodeDrawer` in T-GOLD-05).
- **Body**: `src/frontend/src/components/behavioral/ExampleDrawerContent.tsx`
  -- a `DrawerLayout` with `ExampleMetaPane` (left) + `ExampleStarContent` (right).

Two consumers mount this pair:

| Consumer | File | State variable |
|---|---|---|
| Behavioral main page | `src/frontend/src/pages/BehavioralQuestions.tsx` | `drawerExampleId: string \| null` |
| Theme deep-link page | `src/frontend/src/pages/BehavioralThemePage.tsx` | `activeExample: BehavioralExample \| null` |

Both already import `SlideOverPanel` + `ExampleDrawerContent` in the same shape,
so the toggle wiring has a single insertion point.

### Toggle placement -- mirroring the T-GOLD-05 rule

`SlideOverPanel` now accepts `headerActions?: ReactNode` and
`headerAccentClassName?: string` (added in T-GOLD-05 for the framework drawer).
The header is still minimal: title + close-x, identical to the
`FrameworkNodeDrawer` header pre-audit. Per the T-GOLD-05 decision rule:

> If header has clear room next to the close (X) button: put `GoldenToggleButton`
> there, icon-only, 32x32.

**Decision: icon variant in the header, left of the close button.**
Also pass `headerAccentClassName = isGolden ? "border-t-2 border-t-orange-300" : ""`
to echo the card visual, exactly as `FrameworkNodeDrawer` does.

The cleanest wiring is to extend `ExampleDrawerContent` so the consumer pages
don't each need to know the toggle existed, OR to keep
`ExampleDrawerContent` body-only and render `GoldenToggleButton` in each page's
`<SlideOverPanel headerActions={...}>` prop. Recommended: **pass `headerActions`
from each page**, matching the `FrameworkNodeDrawer` composition. Reason: the
two pages already own the active-example state and the `SlideOverPanel` props
(title, onClose), so keeping the toggle co-located with them avoids threading
`itemId` / `isGolden` down through `ExampleDrawerContent`.

## 2. React-query cache keys -- invalidation planning

Grep of `queryKey:` across behavioral consumers (and story-arcs/coverage that
enrich from the same `BehavioralExample` rows):

| Key | File | Notes |
|---|---|---|
| `["behavioral-categories"]` | `BehavioralQuestions.tsx` | Independent of golden state -- no invalidation needed. |
| `["behavioral-themes"]` | `BehavioralQuestions.tsx`, `BehavioralThemePage.tsx` | Independent -- no invalidation needed. |
| `["behavioral-questions", cat, search, themeSlugs, themeMode]` | `BehavioralQuestions.tsx` | No golden fields returned on questions; no invalidation needed. |
| `["behavioral-examples"]` | `BehavioralQuestions.tsx` | **Must invalidate.** List carries `is_golden` / `golden_at`. |
| `["behavioral-coverage"]` | `BehavioralQuestions.tsx` (`viewMode==="coverage"`) | Cells don't carry golden, so not strictly required, but re-fetch is cheap. Leave unlisted for now. |
| `["behavioral-gaps"]` | `BehavioralQuestions.tsx` | No golden fields. Skip. |
| `["behavioral-examples-theme", slug]` | `BehavioralThemePage.tsx` | **Must invalidate.** Same row shape as `/behavioral/examples`. |
| `["behavioral-questions-theme", slug]` | `BehavioralThemePage.tsx` | No golden. Skip. |
| `["story-arcs"]` | `StoryMapView.tsx` | Enriches example rows with title/link_count from DB; **backend `/behavioral/story-arcs` does NOT currently pass through is_golden**. Leave alone for 07b; revisit in 09 if the Golden aggregator needs it. |

`GoldenToggleButton` (T-GOLD-03) already lists for `behavioral_example`:

```ts
["behavioral", "examples"],
["behavioral", "example", itemId],
["behavioral-examples"],
["behavioral-examples-theme"],
```

The hyphenated keys match current consumers; the `["behavioral", "examples"]`
tuple is forward-compat for any future consumer. **No changes needed in
`GoldenToggleButton` for 07b.** (Note: react-query treats
`["behavioral-examples-theme"]` as a prefix match vs
`["behavioral-examples-theme", slug]`, so all slug-scoped queries invalidate.)

## 3. Card list rendering locations -- where to apply `goldenCardClass` + `GoldenBadge`

Three card-rendering sites exist in the behavioral UI. Only two are in scope
for 07b (the "Examples" surfaces); the third (`QuestionRow`) is a question-row
list and does not carry `is_golden`.

| Site | File | Render shape | 07b action |
|---|---|---|---|
| `ExampleCard` (examples view + inline under QuestionRow) | `BehavioralQuestions.tsx` (two definitions: a top-level `ExampleCard` near L179 for the Examples view, and the inline block inside `QuestionRow` at L466--507 that renders a *mini* example card under an expanded question) | `<div>` with `border-2 border-gray-200 hover:border-blue-400`; has header row of example_id + title + principle pills + `[+]/[-]` | Apply `goldenCardClass(isGolden)` appended to className; render `<GoldenBadge golden={isGolden} />` next to the `Needs Input` pill. |
| `ExampleCard` (theme page grid) | `BehavioralThemePage.tsx` L137--182 | `<button>` card with `border border-gray-200 hover:border-blue-400`; has example_id badge + title + pitch/facts | Same treatment: `goldenCardClass` + `GoldenBadge`. |
| `ArcExampleCard` | `components/behavioral/StoryMapView.tsx` L73 | Timeline card in the story-map view; data comes from `/behavioral/story-arcs` which does NOT currently return `is_golden` | **Skip in 07b.** Out of scope until `/behavioral/story-arcs` is extended; handled in T-GOLD-09 if needed. |
| `QuestionRow` expanded mini-card (L466--507 of `BehavioralQuestions.tsx`) | same file | Links to an example; it's a cross-reference surface, not the example card itself | **Optional.** Could show a tiny `<GoldenBadge />` near the title link for consistency. Propose: yes, tiny badge only, no `goldenCardClass` (these are nested preview blocks, not primary cards). |

`principle_tags_live` in `StoryMapView` is DB-sourced but limited to principle
strings. The story-map arc backend would need an additive change to surface
`is_golden`; defer.

### Filter UX on the Behavioral page (mirroring `?golden=1` from T-GOLD-06)

`BehavioralQuestions.tsx` already uses `useSearchParams` for `themes` and
`theme_mode`. Propose adding `?golden=1` with a **"Golden only" pill** in the
same row as the view-mode toggles (or next to the category filter). When
active:

- `viewMode === "examples"`: filter by `ex.is_golden`.
- `viewMode === "questions"`: hide the `linkedExamples` preview for non-golden
  examples; keep questions visible. (Or hide questions whose only examples are
  non-golden. Decide in 07b based on screenshot.)
- `viewMode === "coverage"`: filter rows in the heatmap by `ex.is_golden`.
- `viewMode === "story-map"`: no-op for now (data source lacks the flag).

`BehavioralThemePage` is a deep-link surface with no tab bar. Propose: **no
filter toggle on the theme page** -- the page is already narrow-scope, and the
analogous `T-GOLD-08` decision for company docs is also "no filter on index
pages". Card visuals + drawer toggle still render.

## 4. Backend PUT endpoint -- confirmed from T-GOLD-02

`src/backend/routers/behavioral.py::update_example` at L499--537:

- Path: `PUT /behavioral/examples/{example_db_id}` (DB id, not string
  `example_id`).
- Body: `BehavioralExampleUpdate` (pydantic, `is_golden: bool | None = None`).
- Stamps `golden_at = datetime.utcnow()` on a `false -> true` transition
  (L522--525). Leaves `golden_at` on `true -> false`, matching the T-GOLD-02 contract.
- Response is `BehavioralExampleResponse`; `_build_example_response` at L317
  already includes `is_golden: bool(ex.is_golden)` and `golden_at: ex.golden_at`.

`GoldenToggleButton.buildEndpoint("behavioral_example", itemId)` produces
`/behavioral/examples/${itemId}` -- exact match.

**No backend change needed for 07b.** The frontend `BehavioralExample` type in
`src/frontend/src/types/behavioral.ts` will need two new fields appended
(`is_golden: boolean; golden_at: string | null;`) so the compiler can route the
values through.

## 5. Complexity estimate for T-P2-559 (T-GOLD-07b)

**Estimate: S (small).** Reasoning:

- Drawer wiring is a two-site copy of the `FrameworkNodeDrawer` pattern (pass
  `headerActions` + `headerAccentClassName` from `BehavioralQuestions.tsx` and
  `BehavioralThemePage.tsx`). Probably 15--20 lines across both files.
- Card visuals are mechanical: add `goldenCardClass(isGolden)` to each card's
  className and render `<GoldenBadge />` in the existing pill row. Two card
  sites (the top-level `ExampleCard` in `BehavioralQuestions.tsx` examples view
  + `ExampleCard` in `BehavioralThemePage.tsx`). Maybe a third tiny badge in
  `QuestionRow`'s mini-card if we opt in.
- `?golden=1` filter: `BehavioralQuestions.tsx` already has the URL-param
  plumbing (`themes`, `theme_mode`). Adding `golden` is a straight copy of
  T-GOLD-06's `writeParams` / `toggleGoldenOnly` / "Golden only" pill.
- Type change: 2-line addition to `BehavioralExample`.
- React-query invalidation: already handled by `GoldenToggleButton` from
  T-GOLD-03. Verify with DevTools only -- no code change.
- `StoryMapView` is out of scope; avoids a backend touch.

No new components, no backend edits, no endpoint work. The only non-trivial
decision is the `?golden=1` behavior for `viewMode==="questions"` (hide
non-golden previews vs hide whole questions); resolve in the 07b task spec
with a screenshot. `M` would be justified only if we decide to extend
`/behavioral/story-arcs` and the coverage matrix to carry `is_golden`, which
should stay on the 09 task instead.

Recommended 07b scope cap: do not touch `StoryMapView`, do not touch
`/behavioral/coverage-matrix`, do not touch `/behavioral/story-arcs`.
