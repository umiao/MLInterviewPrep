# KG-FIX-05 Smoke Test Notes (T-P0-613)

**Date**: 2026-04-25
**Branch**: `kg-fix-20260425` (DO NOT auto-merge to main)
**Protocol**: `docs/workflow/seed_smoke_test_protocol.md`

## Step 2 -- `_pillar_of` full-table scan

Result: `total=238  bad=0` (see `pillar_scan.txt`). Every framework_node
maps to one of the 9 known pillars (pillar1..pillar8 + ml-fundamentals).

Pillar distribution:

| pillar           | count |
| ---------------- | ----- |
| ml-fundamentals  | 36    |
| pillar2          | 34    |
| pillar6          | 33    |
| pillar1          | 28    |
| pillar4          | 27    |
| pillar3          | 24    |
| pillar5          | 20    |
| pillar7          | 20    |
| pillar8          | 16    |

ml-fundamentals subtree breakdown matches AC1: 1 root (depth 0) ->
7 categories (depth 1) -> 28 leaves (depth 2) = 36 total.

## Step 3 / 4 -- Cold + Expand-All screenshots

| File                  | Backend version       | Result                                |
| --------------------- | --------------------- | ------------------------------------- |
| `cold_before.png`     | `main` (pre-fix)      | ml-fundamentals lane: GREY FALLBACK   |
| `cold_after.png`      | `kg-fix-20260425`     | ml-fundamentals lane: CYAN (fixed)    |
| `expandall_before.png`| `main` (pre-fix)      | grey FALLBACK, 44 distinct API pillar keys |
| `expandall_after.png` | `kg-fix-20260425`     | 9 swimlanes (pillar1..8 + ml-fundamentals) |

Capture method: backend was temporarily started on `main`'s versions of
`src/backend/routers/kg.py`, `src/frontend/src/components/kg/kgStyles.ts`,
`src/frontend/src/components/kg/useKgLayout.ts` to capture `_before.png`,
then restored to HEAD for `_after.png`. Working tree was not affected.

API-level evidence of the bug (captured during before-screenshot session):

```
--- BUG STATE: API pillar keys (44 distinct) ---
pillar2: 34
pillar6: 33
pillar1: 28
pillar4: 27
pillar3: 24
pillar5: 20
pillar7: 20
pillar8: 16
ml-fundamentals: 1
ml-fundamentals/attention_transformer: 1
ml-fundamentals/attention_transformer/kv-cache: 1
ml-fundamentals/attention_transformer/mha-mqa-gqa: 1
... (35 more slash-fragmented keys)
```

After the fix the same query returns 9 keys, with `ml-fundamentals` collapsing
36 nodes correctly.

## Step 4 -- Lane count verdict

| Pre-seed lanes | Post-fix lanes | Verdict                          |
| -------------- | -------------- | -------------------------------- |
| 8 (working)    | 9 (working)    | New `ml-fundamentals` taxonomy added; PILLAR_ORDER + PILLAR_STYLES + WHITELIST + convention test all updated in FIX-01..04 |

`ml-fundamentals` is the canonical 9th lane as of 2026-04-25.

## Step 5 -- Diff before vs after

Visible deltas:

- `ml-fundamentals` swimlane dot: grey -> cyan.
- API `pillar` field for ml-fundamentals descendants: 35 distinct
  slash-keys -> single `ml-fundamentals` key.
- No regression on existing pillar1..8 lanes (same colors, same order).

## Verdict

PASS. Step 2 `bad=0`, lane count = 9 (matches expectation), no regressions.
Hard merge gate left in place per AC4 -- branch is pushed but NOT merged.
