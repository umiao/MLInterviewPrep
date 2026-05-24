# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
"""Create/update Pinterest LC Must-Do review+index company document.

Idempotent: looks up by title, updates content if already exists.
"""
import sqlite3
from datetime import datetime, timezone

DB_PATH = "data/mle_prep.db"
COMPANY_ID = 29  # Pinterest
DOC_TITLE = "Pinterest LC Must-Do: Review & Index"

CONTENT = r"""# Pinterest LC Must-Do -- Review & Index

> 14 LeetCode problems from Pinterest prep list. This doc is an **index + pattern review**.
> Each entry links back to the problem's full solution notes in the problems DB.

## Quick Status

> Click a problem title to open its description + solution notes in a side drawer.

| # | LC | Title | Difficulty | Pattern | Status | Notes |
|---|-----|-------|-----------|---------|--------|-------|
| 1 | 332 | [Reconstruct Itinerary](lc://332) | Hard | Hierholzer (Eulerian Path) | Done | Written |
| 2 | 465 | [Optimal Account Balancing](lc://465) | Hard | Bitmask DP (zero-sum partition) | Done | Written |
| 3 | 815 | [Bus Routes](lc://815) | Hard | BFS on route graph | Done | Written |
| 4 | 322 | [Coin Change](lc://322) | Medium | DP (unbounded knapsack) | Done | Written |
| 5 | 282 | [Expression Add Operators](lc://282) | Hard | Backtracking + `prev` trick | Done | Written |
| 6 | 1055 | [Shortest Way to Form String](lc://1055) | Medium | Greedy / DP | Done | Written |
| 7 | 311 | [Sparse Matrix Multiplication](lc://311) | Medium | Hash-map compression | Done | Written |
| 8 | 2402 | [Meeting Rooms III](lc://2402) | Hard | Two-heap simulation | Done | Written |
| 9 | 1110 | [Delete Nodes And Return Forest](lc://1110) | Medium | DFS + `is_root` flag | Done | Written |
| 10 | 1244 | [Design A Leaderboard](lc://1244) | Medium | Sorted map / heap | Done | Written |
| 11 | 410 | [Split Array Largest Sum](lc://410) | Hard | Binary search on answer / DP | Done | Written |
| 12 | 43 | [Multiply Strings](lc://43) | Medium | Simulation on digit arrays | Done | Written |
| 13 | 642 | [Design Search Autocomplete System](lc://642) | Hard | Trie + heap | Done | Written |
| 14 | 1723 | [Find Minimum Time to Finish All Jobs](lc://1723) | Hard | Binary search + backtracking | Done | Written |

**Progress**: 14/14 done | **Notes written**: 14/14 (全部含中文 + code review)

---

## Pattern Clusters (for review)

Group problems by core technique so similar traps/tricks reinforce each other.

### Cluster A: Graph / Eulerian / BFS
- [**LC 332** Reconstruct Itinerary](lc://332) -- Hierholzer's algorithm, post-order append + reverse
- [**LC 815** Bus Routes](lc://815) -- BFS on *route* graph (nodes = routes, not stops)
- [**LC 465** Optimal Account Balancing](lc://465) -- partition graph into zero-sum components (bitmask DP)

### Cluster B: Backtracking / DFS with Carried State
- [**LC 282** Expression Add Operators](lc://282) -- `prev` trick for `*` precedence
- [**LC 1110** Delete Nodes And Return Forest](lc://1110) -- `is_root` flag carried down, None returned up
- [**LC 1723** Find Minimum Time to Finish All Jobs](lc://1723) -- backtrack + binary search on answer

### Cluster C: DP on Subsets / Indices
- [**LC 322** Coin Change](lc://322) -- classic unbounded knapsack 1D DP
- [**LC 410** Split Array Largest Sum](lc://410) -- binary search on answer OR DP on (i, k)
- [**LC 1055** Shortest Way to Form String](lc://1055) -- greedy two-pointer per chunk

### Cluster D: Heap / Simulation / Design
- [**LC 2402** Meeting Rooms III](lc://2402) -- two-heap (free + busy) with tuple tiebreak
- [**LC 1244** Design A Leaderboard](lc://1244) -- hash map + on-demand sort (or sorted structure)
- [**LC 642** Design Search Autocomplete](lc://642) -- Trie + heap/top-k
- [**LC 311** Sparse Matrix Multiplication](lc://311) -- hash-map representation

### Cluster E: String / Arithmetic Simulation
- [**LC 43** Multiply Strings](lc://43) -- digit-by-digit simulation, index arithmetic `(i+j)` and `(i+j+1)`

---

## Core Patterns Cheat Sheet

### Hierholzer's Algorithm (LC 332)
```
build graph, min-heap neighbors (lex order)
dfs(u): while graph[u]: dfs(heappop(graph[u]))
        route.append(u)    # post-order
return route[::-1]
```
Key insight: append **after** all out-edges exhausted. Dead-ends end up at tail of reversed = correct order.

### `prev` Trick for Operator Precedence (LC 282)
```
dfs(i, expr, cur, prev):
  +: new_cur = cur + x,             new_prev = x
  -: new_cur = cur - x,             new_prev = -x
  *: new_cur = cur - prev + prev*x, new_prev = prev*x
```
Invariant: `cur` is current expression value; `prev` is last additive term (signed). Multiplication rewrites last term: "undo prev, apply prev*x."

### `is_root` Flag (LC 1110)
```
dfs(node, is_root):
  deleted = node.val in to_delete
  if is_root and not deleted: forest.append(node)
  node.left  = dfs(node.left,  deleted)    # child's is_root = my deleted status
  node.right = dfs(node.right, deleted)
  return None if deleted else node         # parent auto-unlinks
```
Principle: "carry ancestor state DOWN via params, signal unlink UP via return."

### Bitmask DP on Zero-Sum Partitions (LC 465)
```
dp[mask] = max zero-sum subgroups partitioning mask
for mask where subset_sum[mask] == 0:
  enumerate submasks sub (via sub = (sub-1) & mask)
  if subset_sum[sub] == 0 and dp[mask^sub] >= 0:
    dp[mask] = max(dp[mask], 1 + dp[mask^sub])
answer = n - dp[(1<<n) - 1]
```
**Critical**: use `(sub-1) & mask` for O(3^n), NOT `range(mask+1)` which is O(4^n).

### Two-Heap Resource Simulation (LC 2402)
```
free = min-heap of room IDs
busy = min-heap of (end_time, room_id)
for meeting (start, end):
  release: while busy and busy[0][0] <= start: move to free
  assign:  if free: pop; else: delay via busy
```
Tiebreak via tuple `(end, room_id)` -- automatic.

---

## Common Traps Across the Set

1. **Leading zeros in string numbers** (LC 43, 282): `break` not `continue` once `s[0]=='0'` with `len > 1`.
2. **Submask enumeration** (LC 465, 698, 473): `sub = (sub-1) & mask` for O(3^n); `range(mask+1)` is O(4^n) but often still AC due to guards.
3. **Heap tuple tiebreak** (LC 2402, 1882, 1834): `(end, room)` gives "earliest end, then lowest ID" automatically.
4. **Post-order vs carry-down state** (LC 1110 vs LC 332): choose based on "does decision depend on ancestors or descendants?"
5. **Eval in expression problems** (LC 282): never use `eval()` in interviews; use `prev` trick.

---

## Daily Review Template

Pick 1-2 problems, spend 20 min each:
1. **Re-solve from scratch** (no notes) -- this surfaces what you actually remember.
2. **Compare to notes** -- any delta is a learning signal.
3. **State the pattern in one sentence** -- forces compression.
4. **Identify 2 related problems** -- tests transfer.

If stuck >10 min, read notes and mark for re-review tomorrow.

---

## Links

- Full problem notes: accessible via `/problems/<id>` in this UI; content is in `problems.notes` column.
- Recruiter call prep: [Pinterest Senior MLE -- Recruiter Call Prep](./docs) (separate doc id=39).
- Source: user-provided 2026-04-12 via Discord.
"""


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    cursor.execute(
        "SELECT id FROM company_documents WHERE company_id = ? AND title = ?",
        (COMPANY_ID, DOC_TITLE),
    )
    row = cursor.fetchone()

    if row:
        doc_id = row[0]
        cursor.execute(
            "UPDATE company_documents SET content = ?, updated_at = ? WHERE id = ?",
            (CONTENT, now, doc_id),
        )
        print(f"[UPDATE] doc id={doc_id} refreshed ({len(CONTENT)} chars)")
    else:
        cursor.execute(
            """INSERT INTO company_documents
            (company_id, title, content, source_type, created_at, updated_at)
            VALUES (?, ?, ?, 'prep_doc', ?, ?)""",
            (COMPANY_ID, DOC_TITLE, CONTENT, now, now),
        )
        doc_id = cursor.lastrowid
        print(f"[NEW] doc id={doc_id} created ({len(CONTENT)} chars)")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
