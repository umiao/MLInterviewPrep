# Seed Smoke-Test Protocol -- framework_node Batches

**Status**: Adopted 2026-04-25 (T-P0-612, [KG-FIX-04])
**Trigger**: Any seed batch that inserts/updates **3 or more** rows in
`framework_nodes` is required to run this 5-step checklist before merge.
**Why**: The `ml-fundamentals` slash-path bug (35 nodes, all silently
bucketed under "Other" on the KG page) shipped because the seed scripts
were validated against unit tests but never against the actual KG render.
This protocol converts that lesson into machinery.

See related rule in `CLAUDE.md` (Behavior Rules) and the postmortem in
`LESSONS.md` (2026-04-25 entry).

## Scope

In scope:

- Any change that inserts >=3 new `framework_nodes` rows.
- Any change that mass-updates `path`, `parent_id`, or `pillar` on >=3
  existing `framework_nodes` rows (these mutate the KG topology in the
  same way an insert does).

Out of scope:

- Single-node tweaks (title, description, rendered content).
- Updates that only touch fields the KG layout does not consume
  (`difficulty`, `mastery`, etc.). When in doubt, run the protocol --
  it is cheap.

## The 5 steps

### Step 1 -- Run the seed against staging DB

Run the seed script idempotently against `data/mle_prep.db` (or a copy if
the run is risky):

```bash
python scripts/seed_<your_batch>.py
```

Verify the row count change matches the script's intent:

```bash
python -c "import sqlite3; print(sqlite3.connect('data/mle_prep.db').execute('SELECT COUNT(*) FROM framework_nodes').fetchone())"
```

### Step 2 -- `_pillar_of` full-table scan

Confirm every node in the table maps to a known pillar via the backend's
`_pillar_of()` derivation. Any `None` pillar means a node is going to land
in the grey "Other" bucket on the KG page.

```bash
python -c "
import sqlite3, sys
sys.path.insert(0, 'src')
from backend.routers.kg import _pillar_of
conn = sqlite3.connect('data/mle_prep.db')
rows = conn.execute('SELECT id, path, parent_id FROM framework_nodes').fetchall()
nodes = {r[0]: {'id': r[0], 'path': r[1], 'parent_id': r[2]} for r in rows}
known = {'pillar1','pillar2','pillar3','pillar4','pillar5','pillar6','pillar7','pillar8','ml-fundamentals'}
bad = [(nid, nodes[nid]['path'], _pillar_of(nodes, nid)) for nid in nodes if _pillar_of(nodes, nid) not in known]
print(f'total={len(nodes)}  bad={len(bad)}')
for b in bad[:10]: print(b)
"
```

Pass condition: `bad=0`. Any output means the seed introduced a node that
the KG cannot classify -- fix before proceeding (typically a missing
`parent_id` or a typo in `path`).

### Step 3 -- Cold-start KG screenshot

Start the frontend dev server and capture the KG page in its initial
collapsed state. Cold start is the realistic first-render path that
`vitest` does not exercise.

```bash
cd src/frontend
npm run dev
```

Then in a browser at `http://localhost:5173/kg`:

1. Wait for the graph to settle (no animation in flight).
2. Capture the full viewport. Save to
   `logs/kg_smoke_<TASK_ID>_<YYYYMMDD>/cold_after.png`.
3. Visually verify: no grey FALLBACK_STYLE swimlane appears unless your
   seed deliberately introduces an unclassified root.

### Step 4 -- Expand-all screenshot + lane count

Click "Expand All" (or the equivalent control) and capture the same
viewport again at `logs/kg_smoke_<TASK_ID>_<YYYYMMDD>/expandall_after.png`.

Count the swimlanes and assert against expectation:

| Pre-seed lane count | Post-seed lane count | Verdict                                  |
| ------------------- | -------------------- | ---------------------------------------- |
| N                   | N                    | Existing taxonomy reused (typical).      |
| N                   | N+1                  | New taxonomy added (must update PILLAR_ORDER + PILLAR_STYLES). |
| N                   | >N+1                 | Suspicious -- usually means slash/dot mismatch. |

As of 2026-04-25 the canonical lane count is **9** (pillar1..pillar8 +
ml-fundamentals).

### Step 5 -- Diff before vs after

If a `cold_before.png` / `expandall_before.png` baseline exists from the
last protocol run, diff visually. Watch for:

- Swimlanes swapping order unexpectedly (broken `PILLAR_ORDER`).
- Border colour changes on existing lanes (broken `PILLAR_STYLES`).
- Nodes that previously rendered under one lane now appearing under
  "Other" (regression in `_pillar_of()` or schema drift).

If no baseline exists, save the current `*_after.png` screenshots as the
new baseline for the next batch.

## Pass / fail

A seed batch passes the protocol when:

- Step 2 prints `bad=0`.
- Step 4 lane count matches expectation (or the change is documented in
  the task description and the four required updates from
  `docs/protocol/kg_markdown_conventions.md` §10.3 are in the same
  change).
- Step 5 shows no unexpected regressions on existing lanes.

Failure on any step is a blocker for merge -- not a deferred follow-up.

## Output artifacts

Each protocol run produces a directory under `logs/`:

```
logs/kg_smoke_<TASK_ID>_<YYYYMMDD>/
  cold_before.png      (optional, if baseline existed)
  cold_after.png       (required)
  expandall_before.png (optional)
  expandall_after.png  (required)
  pillar_scan.txt      (Step 2 output)
  notes.md             (lane count delta + any anomalies)
```

Commit these alongside the seed script. The screenshots are evidence the
protocol ran, not just was claimed to have run.

## Why this protocol exists

The KG bug history shows that vitest passes while every node is bucketed
as "Other". Unit tests cover argument shape; only the actual render
exercises the layout pipeline end-to-end. This 5-step gate is the
cheapest reliable way to catch the class of bugs a unit test cannot see.
