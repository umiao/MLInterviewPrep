"""Add Pinterest Escape Room custom problem to mle_prep.db.

Source: Pinterest coding round 2025-11 (non-LC, recurring).
Design a Game(rooms, people) data structure with:
  - proceedToNextRoom(pid) -- O(1)
  - getPeople(roomId)      -- O(1)
  - getTop(K)              -- O(N + K), positional ranking with
                              tiebreak by entry-order within a room.

Canonical answer: doubly-linked list per room + global {pid -> node} map.

Idempotent: if a row with this title already exists, updates notes only.

Task: T-P0-397
"""
from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

TITLE = "Escape Room Game State (rooms + people)"
SOURCE = "pinterest_interview,custom"
COMPANY_TAGS = json.dumps(["Pinterest"])
TAGS = json.dumps(["OOD", "Linked List", "Hash Map", "Design"])
PATTERN = "Design + Doubly-Linked List"
DIFFICULTY = "medium"
CATEGORY = "algorithm"
PRIORITY = 1  # P0

DESCRIPTION = """\
[Pinterest coding 2025-11] Design a game-state data structure for an escape-room
experience. Rooms are numbered 1..R in order of advancement. People enter the
lowest room and proceed forward one room at a time.

Required API:
  - proceedToNextRoom(pid): move person `pid` from their current room to the next
    one, preserving entry-order within the new room. O(1).
  - getPeople(roomId): return the list of people currently in `roomId`, in order
    of their entry into that room. O(1) to return, O(k) to materialize the list
    where k is the room size.
  - getTop(K): return the K most-advanced people. Ranking = higher roomId first;
    tiebreak within the same room = earlier entry first. O(N + K).

Canonical design: a doubly-linked list per room (ordered by entry time) plus a
global map `people: pid -> node` for O(1) node lookup. getTop walks rooms from
highest to lowest, collecting nodes in DLL order, until K are gathered.
"""

SOLUTION_TAG = "[Pinterest Escape Room Canonical Solution]"

NOTES = SOLUTION_TAG + """

## Problem (Pinterest 2025-11)

Design `Game(rooms, people)` with three operations:

| Method | Complexity | Semantics |
|--------|-----------|-----------|
| `proceedToNextRoom(pid)` | O(1) | Move `pid` from current room to the next numbered room. |
| `getPeople(roomId)` | O(1) return (O(k) materialize) | People in `roomId`, in entry order. |
| `getTop(K)` | O(N + K) | Top-K by (roomId desc, entry_order asc). |

## Canonical Data Structure

- Per-room **Doubly-Linked List (DLL)** keeps entry order, supports O(1)
  append-tail and O(1) unlink-by-node.
- Global **hash map** `people: pid -> Node` gives O(1) lookup for the person's
  current node (the node stores a back-pointer to its owning room).
- `rooms: dict[int, DLL]` keyed by room id. For `getTop`, iterate `sorted(rooms,
  reverse=True)` once at construction (rooms are typically small and static).

### Why a Doubly-Linked List (DLL) instead of `list` / `deque`?

- `proceedToNextRoom` must unlink `pid` from the middle of its current room
  (people don't always move in **FIFO (First-In-First-Out)** order -- whoever
  solves the puzzle first advances). A Python `list.remove(x)` is O(k);
  DLL unlink is O(1) via the node reference stored in the global map.
- `collections.deque` only supports O(1) on the two ends; middle removal is
  still O(k), so it is not sufficient either.
- Append to the new room's tail preserves entry-order for tiebreaks.

## Python Implementation

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterator


@dataclass
class _Node:
    pid: int
    room_id: int
    prev: "_Node | None" = None
    next: "_Node | None" = None


class _DLL:
    \"\"\"Doubly-linked list with O(1) append-tail and O(1) unlink.\"\"\"

    __slots__ = ("head", "tail", "size")

    def __init__(self) -> None:
        self.head: _Node | None = None
        self.tail: _Node | None = None
        self.size: int = 0

    def append(self, node: _Node) -> None:
        node.prev = self.tail
        node.next = None
        if self.tail is None:
            self.head = node
        else:
            self.tail.next = node
        self.tail = node
        self.size += 1

    def unlink(self, node: _Node) -> None:
        if node.prev is not None:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next is not None:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
        node.prev = node.next = None
        self.size -= 1

    def iter_forward(self) -> Iterator[_Node]:
        cur = self.head
        while cur is not None:
            yield cur
            cur = cur.next


class Game:
    \"\"\"Escape-room game state.

    rooms: list of room ids in advancement order (e.g. [1, 2, 3, 4, 5]).
    Players enter at rooms[0] and proceed forward one room at a time.
    \"\"\"

    def __init__(self, rooms: list[int], people: list[int]) -> None:
        # Room id -> DLL of nodes currently in that room.
        self._rooms: dict[int, _DLL] = {rid: _DLL() for rid in rooms}
        # Advancement order (ascending).
        self._order: list[int] = list(rooms)
        # Cache reversed-order for O(R) getTop scan.
        self._order_desc: list[int] = list(reversed(rooms))
        # pid -> next-room index into _order; -1 means "finished".
        self._next_idx: dict[int, int] = {}
        # pid -> Node (current location).
        self._people: dict[int, _Node] = {}

        start_room = rooms[0]
        for pid in people:
            node = _Node(pid=pid, room_id=start_room)
            self._rooms[start_room].append(node)
            self._people[pid] = node
            self._next_idx[pid] = 1 if len(rooms) > 1 else -1

    def proceedToNextRoom(self, pid: int) -> None:
        \"\"\"Move pid from current room to the next. O(1).\"\"\"
        node = self._people[pid]
        nxt = self._next_idx[pid]
        if nxt == -1:
            return  # already in final room
        self._rooms[node.room_id].unlink(node)
        new_room = self._order[nxt]
        node.room_id = new_room
        self._rooms[new_room].append(node)
        self._next_idx[pid] = nxt + 1 if nxt + 1 < len(self._order) else -1

    def getPeople(self, roomId: int) -> list[int]:
        \"\"\"Return pids in roomId, in entry order. O(k) where k = room size.\"\"\"
        dll = self._rooms.get(roomId)
        if dll is None:
            return []
        return [node.pid for node in dll.iter_forward()]

    def getTop(self, K: int) -> list[int]:
        \"\"\"Top-K most-advanced. O(R + K) where R = number of rooms.\"\"\"
        out: list[int] = []
        for rid in self._order_desc:
            for node in self._rooms[rid].iter_forward():
                out.append(node.pid)
                if len(out) == K:
                    return out
        return out
```

## Complexity Table

| Op | Time | Space |
|----|------|-------|
| `__init__(R, N)` | O(R + N) | O(R + N) |
| `proceedToNextRoom` | O(1) | - |
| `getPeople(roomId)` | O(k) materialize | - |
| `getTop(K)` | O(R + K) | O(K) output |

Total space: O(R + N) for the rooms + people maps + DLL nodes.

Note on `getTop(K)` complexity: the interview spec states O(N + K), which is
also a valid bound because R <= N (empty rooms contribute a constant scan
step). The tighter bound O(R + K) holds whenever K people are collected
before all rooms are visited, which is the typical case.

## Edge Cases

1. `pid` already in the final room -> `proceedToNextRoom` no-ops (guard on `-1`).
2. `roomId` not in game -> `getPeople` returns `[]`.
3. `K > N` -> `getTop` returns all N people, clamped naturally by the loop.
4. Tiebreak: within a room, the `_DLL.iter_forward` order preserves entry
   order because every `proceedToNextRoom` appends to the tail of the new room.

## Chinese Notes (中文解析)

**核心思路**: "每房间一个**双向链表 (Doubly-Linked List, DLL)** + 全局
`pid -> Node` 映射 (hash map)"。两者缺一不可:
- 只有链表没映射 -> 无法 O(1) 定位某人节点, unlink 变 O(k)。
- 只有映射没链表 -> 无法 O(1) unlink + 保持入房顺序。

**为什么不能用 `deque`?** `deque` 只支持两端 O(1), 中间 remove 是 O(k)。
房间里的人不按 **FIFO (First-In-First-Out, 先进先出)** 出房 (先解谜的先走),
所以必须能 O(1) 从中间摘除。

**Top-K 排名规则**: 房号大的优先 (越靠后越领先), 同房内先到先优先。
因此遍历房间倒序, 每个房间内链表正序, 累计到 K 即返回。

**陷阱**:
1. 必须在 Node 里存 `room_id` 反指针, 不然 unlink 时不知道从哪个链表摘。
2. `_next_idx` 要在构造时就记好, 避免每次查 "当前是 rooms 里第几个" 的 O(R) 扫描。
3. 最后房间的人不要继续前进 (用 -1 哨兵表示已完成)。

**扩展追问 (面试常见)**:
- Q: 如果支持 "某人跳过某些房间怎么办?"
  A: 把 `_next_idx` 改为每人自己的 "剩余房间序列" 列表即可, 仍是 O(1)。
- Q: 如果要求 `getTop(K)` 是 O(K) (不依赖 R)?
  A: 维护一个 `non_empty_rooms: DLL[int]` (按房号降序), 每次 unlink/append
     时同步维护房间非空状态, getTop 直接从这个 DLL 头部开始遍历。

## Self-Test (smoke)

```python
g = Game([1, 2, 3], [10, 20, 30])
assert g.getPeople(1) == [10, 20, 30]
g.proceedToNextRoom(20)        # 20 -> room 2
assert g.getPeople(1) == [10, 30]
assert g.getPeople(2) == [20]
g.proceedToNextRoom(30)        # 30 -> room 2
assert g.getPeople(2) == [20, 30]  # entry order preserved
g.proceedToNextRoom(20)        # 20 -> room 3
# Ranking: room 3 [20], room 2 [30], room 1 [10]
assert g.getTop(2) == [20, 30]
assert g.getTop(10) == [20, 30, 10]
```
"""


def upsert() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    cur.execute(
        "SELECT id, notes FROM problems WHERE title = ? AND leetcode_id IS NULL",
        (TITLE,),
    )
    row = cur.fetchone()
    now = datetime.now(UTC).isoformat()

    if row is None:
        cur.execute("SELECT MAX(id) FROM problems")
        next_id = (cur.fetchone()[0] or 0) + 1
        cur.execute(
            """
            INSERT INTO problems (
                id, leetcode_id, title, url, difficulty, tags, pattern,
                category, source, company_tags, priority, is_completed,
                comfort_level, created_at, description, notes
            ) VALUES (?, NULL, ?, NULL, ?, ?, ?, ?, ?, ?, ?, 0, 0, ?, ?, ?)
            """,
            (
                next_id,
                TITLE,
                DIFFICULTY,
                TAGS,
                PATTERN,
                CATEGORY,
                SOURCE,
                COMPANY_TAGS,
                PRIORITY,
                now,
                DESCRIPTION,
                NOTES,
            ),
        )
        print(f"[INSERT] id={next_id} title={TITLE!r}")
    else:
        pid, existing_notes = row
        if existing_notes and SOLUTION_TAG in existing_notes:
            print(f"[SKIP] id={pid} already has canonical solution")
        else:
            merged = (existing_notes + "\n\n---\n\n" + NOTES) if existing_notes else NOTES
            cur.execute(
                "UPDATE problems SET notes = ?, description = ? WHERE id = ?",
                (merged, DESCRIPTION, pid),
            )
            print(f"[UPDATE] id={pid} notes appended")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    upsert()
