# Reconcile sweep -- fully-checked leaves (T-P0-911 dry-run)

- **Generated**: 2026-05-19 11:02:42
- **Mode**: dry-run (dry-run = ZERO DB writes)
- **Reconcile logic**: `scripts.lib.framework_progress.reconcile_all_fully_checked` (T-P0-910 shared helper -- NO inline logic in this tool)
- **Nodes scanned**: 301
- **Leaves that WOULD change** (fully-checked signature): [111, 114]

## Would-change: reconciled leaves

| node | path | kind | status | progress_pct | boxes |
|---:|---|---|---|---|---:|
| 111 | `pillar4.search_ir.classic_ir` | reconciled-leaf | not_started -> mastered | 100.0 -> 100.0 | 5/5 |
| 114 | `pillar4.search_ir.learning_to_rank` | reconciled-leaf | review -> mastered | 100.0 -> 100.0 | 10/10 |

## Would-change: propagated ancestors (rollup side-effect)

These change only because `_propagate_upward` recomputed them from the reconciled leaves (production rollup, not a direct signature match).

_None._

## OUT OF SCOPE -- deliberately NOT touched (AC2, Review B)

The sweep saw these and left them untouched. Pinned scope is asserted in code (`assert_scope_pinned`) and tested (`tests/test_reconcile_fully_checked_sweep.py`).

- **reverse** (pct>0, 0 checked -- 115/171 shape): [115, 171]
- **partial-stale** (0 < checked < total -- e.g. node 92): [92]
- **no-checklist drift** (0/0 boxes, drifted status -- node 69): [69]

## Next step

This is the T-P0-911 deliverable: tool + dry-run report only. Applying the change (`--apply`: timestamped `.bak` -> commit -> JSONL audit) is the separate human-gated **T-P0-915**. No `--apply` was run here.
