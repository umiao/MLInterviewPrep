# Golden Toggle Placement Audit -- FrameworkNodeDrawer (2026-04-20)

## Audit target

`src/frontend/src/components/framework/FrameworkNodeDrawer.tsx` -- uses the
shared `SlideOverPanel` with the default (minimal) header.

## Header content before this change

The drawer header (inside `SlideOverPanel`) is very sparse:

```
+-----------------------------------------------+
|  <Node Title truncated>              [x]      |
+-----------------------------------------------+
```

Only two elements: the title (`text-lg font-semibold`, truncated) and the
close button (`text-xl` x glyph). No status pill, no confidence meter, no
progress bar, no secondary actions.

## Decision

Per the T-GOLD-05 decision rule:

> If header has clear room next to the close (X) button: put
> `GoldenToggleButton` there, icon-only, 32x32.

The header has clear room. **Placement: header, left of the close button, icon
variant.**

## Implementation notes

- `SlideOverPanel` gained two optional, backwards-compatible props:
  - `headerActions?: ReactNode` -- rendered in a flex row *before* the close
    button. Keeps the 8px gap (`gap-2`) for visual separation.
  - `headerAccentClassName?: string` -- optional extra classes concatenated
    onto the header strip. Used here to paint the thin orange-300 top border
    when the current node is golden.
- All existing `SlideOverPanel` consumers (`ProblemDrawer`, `PrepNotesModal`,
  behavioral drawers, etc.) omit both props and render identically.
- `FrameworkNode` type now includes `is_golden: boolean` and
  `golden_at: string | null`, matching the backend schema.

## Echo of card visual

When the opened node has `is_golden = true`, the drawer header gains
`border-t-2 border-t-orange-300`. This mirrors the top of the
`goldenCardClass` accent (`border-orange-300 border-l-4 border-l-orange-500`)
on MLFundamentals cards -- a deliberately thinner top stripe since the drawer
header already has `border-b` of its own.

## Manual smoke test (AC)

1. `cd src/frontend && npm run dev`
2. Open a framework node drawer.
3. Click the outlined star in the header (next to the x). Verify:
   - Icon flips to a filled orange star immediately (optimistic).
   - Toast appears: "Marked as golden".
   - Drawer header grows a thin orange top border.
4. Close the drawer, reopen a *different* golden node. Verify the star is
   filled on first paint (no flicker) and the orange border is present.
5. Click the filled star. Verify it reverts, toast says "Removed golden
   mark", and the orange border disappears.

## Not in scope (downstream tasks)

- Card-list integration on MLFundamentals + `?golden=1` filter: T-GOLD-06.
- Behavioral UI + company docs integrations: T-GOLD-07/08.
- `/golden` aggregator endpoint + page: T-GOLD-09.
