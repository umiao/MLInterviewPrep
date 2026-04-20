# Golden Marker

## Intent

The **golden marker** is a curation flag layered on top of three content
tables -- `framework_nodes`, `behavioral_examples`, and
`company_documents` -- that lets the user tag items they consider the
"best of the best" reference material for mock-interview drills. It is
orthogonal to progress tracking: `status` / `progress_pct` /
`confidence_level` describe **how far through the material the user is**,
while `is_golden` describes **how highly the user rates the material
itself** once it's been reviewed.

Concretely, during a mock interview the user wants a one-click way to
pull up a curated subset ("show me only the framework nodes, STAR
examples, and company docs I've marked as canonical") without
reinterpreting the per-item progress metadata. Golden is that subset.

## Decision rule

There is **no hard criterion in code** for what makes an item
"golden." The flag is entirely at the user's discretion: they toggle it
on when they judge the item worth revisiting, and off when they
disagree with their past self or the content has been superseded. The
backend must not auto-flip the flag based on progress_pct, confidence,
last_studied_at, or any other heuristic -- those signals are advisory
and already surfaced elsewhere.

## Semantics of `golden_at`

`golden_at` is a user-visible "recently curated" timestamp, not an
audit trail:

- **`false -> true`**: set `golden_at = NOW()`. This makes a "recently
  promoted" sort (`ORDER BY golden_at DESC`) meaningful -- the top of
  the list is what the user most recently decided is canonical.
- **`true -> false`**: **leave `golden_at` untouched**. Demotion does
  not reset the timestamp, so if the user re-promotes the same item
  later, the promotion feels like a fresh decision and sorts to the top
  at that moment.
- **`true -> true` (no-op)**: no change. Idempotent PUTs must not bump
  the timestamp.

This logic is enforced at the **endpoint layer**, not the model layer
(see T-GOLD-02 / T-P1-553). Seed scripts that set `is_golden = True`
should also set `golden_at` explicitly -- the DB default is NULL, which
is correct for "never been golden."

## Schema

All three tables gained the same pair of columns in
`scripts/migrate_add_golden_marker_20260420.py`:

| Column      | Type     | Nullable | Default |
| ----------- | -------- | -------- | ------- |
| `is_golden` | BOOLEAN  | NOT NULL | `0`     |
| `golden_at` | DATETIME | NULL     | NULL    |

Pydantic response schemas (`FrameworkNodeResponse`,
`BehavioralExampleResponse`, `CompanyDocumentResponse`) and update
schemas (`FrameworkNodeUpdate`, `BehavioralExampleUpdate`,
`CompanyDocumentUpdate`) expose both fields.

## Scope of this task (T-P1-552)

This task is schema-only. The endpoint golden_at auto-refresh, the
frontend toggle component, and the card / drawer / filter integrations
are tracked as T-GOLD-02 through T-GOLD-09.
