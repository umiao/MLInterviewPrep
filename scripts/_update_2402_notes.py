"""One-shot: write LC 2402 solution notes into problems.notes."""
import sqlite3

NOTES = r'''## LC 2402 - Meeting Rooms III (Two-Heap Simulation)

> Pinterest must-do list. See [Pinterest Prep Notes](../docs/pinterest_recruiter_call_prep.md#pinterest-lc-%E5%BF%85%E5%88%B7%E9%A2%98%E5%88%97%E8%A1%A8-14-%E9%A2%98)

### Problem Recap
- `n` rooms, numbered `0..n-1`. List of `meetings[i] = [start, end]` with unique starts.
- Rule: each meeting takes the **lowest-numbered available** room. If none free, it **delays** until the **earliest-ending** room frees, keeping the same duration (tiebreak: lowest room number).
- Return the room that hosted the most meetings (tiebreak: lowest index).

### The Key Pattern: Two-Heap Simulation

- **Free heap**: `free_rooms` = min-heap of room IDs (so lowest-numbered pops first).
- **Busy heap**: `busy = (end_time, room_id)` tuples (earliest end pops first; tuple tiebreak gives lowest room ID automatically).

For each meeting (processed by start time):
1. **Release**: while `busy[0].end <= start`, move that room from `busy` to `free`.
2. **Assign**:
   - If `free` non-empty: pop lowest free ID, push `(end, room)` to busy.
   - Else: pop earliest-ending `(end_busy, room)` from busy, push `(end_busy + (end - start), room)` -- meeting is delayed but duration preserved.
3. Increment `count[room]`.

At the end, `count.index(max(count))` returns the lowest-index room with max count (list.index returns first occurrence).

### Polished Solution

```python
import heapq

class Solution:
    def mostBooked(self, n: int, meetings: list[list[int]]) -> int:
        meetings.sort()
        free = list(range(n))   # already a valid min-heap (sorted)
        busy: list[tuple[int, int]] = []   # (end_time, room_id)
        count = [0] * n

        for start, end in meetings:
            # Release all rooms that freed up by `start`
            while busy and busy[0][0] <= start:
                _, room = heapq.heappop(busy)
                heapq.heappush(free, room)

            if free:
                room = heapq.heappop(free)
                heapq.heappush(busy, (end, room))
            else:
                end_busy, room = heapq.heappop(busy)
                heapq.heappush(busy, (end_busy + (end - start), room))
            count[room] += 1

        return count.index(max(count))
```

### Code Review of Your Version

Your solution is **correct and well-structured**. Specific nits:

| Issue | Original | Improved |
|-------|----------|----------|
| Naming | `ans` (it's a count array, not the answer) | `count` |
| Trailing scan | Manual loop with `>` comparison | `count.index(max(count))` -- idiomatic, same tiebreak semantics |
| Heap init | `freeRooms = [i for i in range(n)]` | `list(range(n))` -- same effect, sorted lists are valid heaps |
| `occupiedRooms[0][0] <= start` | works | fine, but `<=` matters here -- see trap below |

Your correctness logic is sound:
- You correctly release rooms **before** checking for free assignment each iteration.
- Your delay formula `endTime + (end - start)` preserves duration.
- The `(end_time, room_id)` tuple gives the right tiebreak (earliest end, then lowest ID).
- Iterating `ans[i] > meetingCnt` with strict `>` from `i=0` naturally returns the lowest-ID room on ties.

### The Subtle Traps

1. **`<=` vs `<` in the release loop**: must be `<=`. Problem says a meeting `[start, end]` occupies the room in `[start, end)`; a room with `end == start` of the next meeting IS free. Your code has `<=` correctly.

2. **Tiebreak in busy heap**: when two rooms end at the same time, the problem says prefer lower room ID. Tuple comparison `(end, room)` gives this automatically. If you ever use a `(time, -room)` or similar, you'd break the tiebreak.

3. **Delay uses `(end - start)`, not `end`**: a common bug is pushing `end_busy + end` which gives the wrong finish time. Duration is `end - start`.

4. **Do NOT re-sort busy**: once we push `(end_busy + duration, room)`, the heap property is maintained by `heappush`. No need to rebuild.

5. **Meetings sort**: sort by `start` (default tuple sort on `[start, end]` works since starts are unique per problem).

### Alternative: Single-Heap (Lazy) Variant

Some solutions keep only `busy` and mark free slots inside it. It's messier and no asymptotically faster. **Prefer the two-heap pattern for clarity.**

### Complexity

Let `m = len(meetings)`.
- **Time**: O(m log m) for sort + O(m log n) for heap ops per meeting (amortized: each room is pushed/popped O(m) total). Overall **O((m + n) log n + m log m)**.
- **Space**: O(n) for the heaps and count array.

### Pattern Recognition for Interviews

Cue: "resource allocation", "lowest-numbered available", "delay until ready" -> **two-heap simulation** (free + busy).

Related problems:
- LC 253 Meeting Rooms II (min rooms needed -- just one heap on end times)
- LC 1834 Single-Threaded CPU (similar two-structure: pending queue + running heap)
- LC 1882 Process Tasks Using Servers (almost identical pattern: free/busy heap with tiebreak on server weight/index)

### Summary

Your solution is basically the canonical answer. The only improvements are cosmetic (`count` naming, `list.index(max(...))` idiom). Commit this one to muscle memory -- the two-heap pattern shows up in LC 1882, LC 1834, and task-scheduling system design questions.
'''

conn = sqlite3.connect("data/mle_prep.db")
conn.execute("UPDATE problems SET notes = ? WHERE leetcode_id = 2402", (NOTES,))
conn.commit()
print(f"[OK] LC 2402 notes updated ({len(NOTES)} chars)")
conn.close()
