# ADR: Checkbox state is canonical; status/progress_pct are derived projections

- **Status**: Accepted
- **Date**: 2026-05-19
- **Task**: T-P0-910 (Review point A -- "without an explicit rule, this recurs")
- **Context source**: Discord 2026-05-19 node-44 bug; root-cause `logs/review/T-P0-914_drift_rootcause_20260519.md`

## Context

KG-Framework leaf "doneness" lives in two places that can disagree:

1. The GFM task-list checkboxes inside `framework_nodes.description`
   (`- [x]` / `- [ ]`), authored by content seed scripts (the sanctioned
   Invariant-3 write path) and toggled by the notes UI.
2. The scalar columns `framework_nodes.status` and
   `framework_nodes.progress_pct`, which the KG view colours/labels by.

`status`/`progress_pct` are recomputed **only** on the API
`PUT /framework/nodes/{id}` path (the frontend computes `progress_pct` from
the checked ratio and PUTs it; the backend derives `status`). A **direct
`description` write** -- exactly what ~40 content seed scripts do -- bypasses
that derivation. Result (the 2026-05-19 node-44 bug): a node with `5/5`
boxes checked still rendered "Not Started" because no code path ever
re-derived its `status`.

Without a written rule for *which side wins*, the failure recurs the moment
anyone hand-sets `status='mastered'` on the DB: a later reconcile silently
overwrites it and nobody can say whether that was correct. That decision
must be explicit, not implied.

## Decision

**For a leaf node, the checkbox state in `description` is the single source
of truth. `status` and `progress_pct` are derived projections of it, never
independent facts.**

- `progress_pct = round(checked / total * 100, 1)` using JavaScript
  `Math.round` semantics (round-half-up), byte-identical to the frontend
  `handleCheckboxClick` path -- so an offline reconcile yields exactly the
  value a live checkbox toggle would have persisted.
- `status` is derived from `progress_pct` with **promote-only** rules,
  byte-faithful to `src/backend/routers/framework.py` L212-227:
  - `progress_pct >= 100` -> `mastered`
  - `progress_pct > 0` and current status `not_started` -> `in_progress`
  - otherwise: status unchanged (an already-advanced leaf is **never
    demoted** by a reconcile; `review -> mastered` on a fully-checked leaf
    is a legitimate promotion, not a violation -- fully-checked is terminal).
- Parent/ancestor `status`/`progress_pct` are derived by the production
  `_propagate_upward` (importance-weighted average + status derivation),
  reused -- never re-implemented.

### Consequences (the part that must be written down)

- **A manual `status` edit is NOT authoritative and WILL be reconciled.**
  Hand-setting a leaf to `mastered` while its boxes are unchecked is *drift*,
  not intent; a future reconcile may overwrite it. The checkbox state wins.
- **If a human genuinely needs a node complete without a checked checklist,
  that is a separate, explicit mechanism -- never a silent direct DB edit.**
  The intended future mechanism is a `# RECONCILE-EXEMPT:` marker honoured by
  the T-P1-912 guard (out of scope for T-P0-910). A silent ad-hoc DB write is
  precisely the Invariant-3 violation this ADR exists to prevent.
- **One deliberate exception -- the reverse class.** A leaf with
  `progress_pct > 0` and **zero** boxes checked (nodes 115/171 shape) is
  *not* zeroed by the reconcile helper, even though the live PUT path would
  (the frontend sends `0`). Silently zeroing an unknown-origin `progress_pct`
  is itself data loss. The helper logs a WARN and leaves the row untouched;
  that class is owned by T-P0-911 / T-P0-913, which escalate it to the user
  rather than guessing. Root-cause T-P0-914 validated this exclusion.

## Implementation

`scripts/lib/framework_progress.py` is the single implementation:

- `reconcile_node_from_checkboxes(db, node_id) -> bool` -- per-leaf reconcile,
  composable (takes a caller-owned session, does **not** commit), idempotent.
- `reconcile_all_fully_checked(db) -> list[int]` -- the safe batch class
  (fully-checked only); the building block for the T-P0-911 sweep.

Both call the **real** `_propagate_upward` from
`src.backend.routers.framework`. Content seeds that check boxes in
`description` should call the per-node helper after the write and before
their commit; the legacy `scripts/reconcile_node_44_*.py` delegates to it
(its inline duplicate was deleted -- single implementation).

## Alternatives considered

- *Treat `status` as canonical, checkboxes cosmetic* -- rejected: seeds and
  the notes UI both write checkboxes; there is no sanctioned writer of
  `status` other than the derive path, so checkboxes are the only
  Invariant-3-clean source.
- *Reconcile inside every seed inline* -- rejected: N drifting copies of the
  promote-only rule (the root cause). One imported, tested function instead.
- *Have the helper zero the reverse class to "fully" normalize* -- rejected:
  destroys unknown-origin data; T-P0-914 verdict is "indeterminate, escalate
  to user", not "guess".
