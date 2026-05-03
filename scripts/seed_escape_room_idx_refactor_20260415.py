"""Refactor Escape Room (id 1068) to use internal room indexes (0..R-1) per user
discussion 2026-04-15.

Eliminates `_order_desc` and `_next_idx` by:
  - Storing Node.idx (position in the rooms sequence) instead of Node.room_id
  - Indexing `_rooms` as a list by idx (not a dict by room_id)
  - Keeping only the two boundary mappings `_idx_to_room` and `_room_to_idx`
    (the latter only for getPeople(roomId) lookups)

getTop iterates `range(R-1, -1, -1)` directly (no cached reversed list).
proceedToNextRoom advances `node.idx + 1`, no dict update, no -1 sentinel.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

NOTES_1068 = """## Escape Room Game State (Pinterest 2025-11)

三个操作：
- `proceedToNextRoom(pid)` — 玩家 pid 前进一房，O(1)
- `getPeople(roomId)` — 按入房顺序返回房内玩家，O(k)
- `getTop(K)` — 按 (前进位置降序, 同房入房序) 返回前 K 名，O(R + K)

### 数据结构
- **每个位置一个双向链表（DLL）**，用 **sentinel 自环** 实现：O(1) 尾部 append、O(1) 按节点指针 unlink，所有真实节点的 `prev/next` 永远非 None。
- **`_rooms: list[_DLL]`**：下标 i 即第 i 个房间（玩家前进位置）；把"房间序列"内化为整数位置，`room_id` 只是对外的 label。
- **`_idx_to_room: list[int]`** 和 **`_room_to_idx: dict[int, int]`**：I/O 边界的双向映射。前者把位置还原回 room_id（如果需要），后者让 `getPeople(roomId)` O(1) 反查位置。
- **全局 `pid → Node` 哈希**：O(1) 定位某人当前节点；Node 反存 `idx`，unlink 时能定位所属 DLL。

**为什么必须用 DLL**：玩家不按 FIFO 离开（先解谜者先走），要从队列中间 O(1) 摘除。`list.remove` 和 `collections.deque` 的中间删除都是 O(k)。

**为什么用 sentinel 自环**：普通 "head/tail + None" 写法里 `append` / `unlink` 有多处 None 分支判断，边界容易写错；sentinel 自环让空表也是合法形态（`sentinel ↔ sentinel`），insert/unlink 全部是零分支指针更新。

**为什么内部用 idx 而不是 room_id**：`proceedToNextRoom` 就是 `node.idx + 1`，无需额外字典记录"下一房间"，也无需缓存 `_order_desc` 供 `getTop` 倒序。`room_id` 作为主键只在 I/O 边界出现。

### Code

```python
class _Node:
    def __init__(self, pid, idx):
        self.pid, self.idx = pid, idx
        self.prev = self.next = None


class _DLL:
    def __init__(self):
        s = _Node(None, None)
        s.prev = s.next = s
        self.sentinel = s
        self.size = 0

    def append(self, node):
        tail = self.sentinel.prev
        node.prev, node.next = tail, self.sentinel
        tail.next = self.sentinel.prev = node
        self.size += 1

    def unlink(self, node):
        node.prev.next, node.next.prev = node.next, node.prev
        node.prev = node.next = None
        self.size -= 1

    def iter_forward(self):
        cur = self.sentinel.next
        while cur is not self.sentinel:
            yield cur
            cur = cur.next


class Game:
    def __init__(self, rooms, people):
        # 位置 i 对应 rooms[i];room_id 只是外部标签。
        self._idx_to_room = list(rooms)
        self._room_to_idx = {rid: i for i, rid in enumerate(rooms)}

        # _rooms[i] 是第 i 个房间的玩家 DLL;按位置索引,O(1) 定位。
        self._rooms = [_DLL() for _ in rooms]

        # pid -> Node;Node 内反存 idx (不是 room_id)。
        self._people = {}

        for pid in people:
            node = _Node(pid, 0)                   # 所有人初始位置 = 0
            self._rooms[0].append(node)
            self._people[pid] = node

    def proceedToNextRoom(self, pid):
        node = self._people[pid]
        i = node.idx
        if i + 1 == len(self._rooms):
            return                                 # 已在最终房,no-op
        self._rooms[i].unlink(node)
        node.idx = i + 1
        self._rooms[i + 1].append(node)

    def getPeople(self, roomId):
        i = self._room_to_idx.get(roomId)
        if i is None:
            return []
        return [n.pid for n in self._rooms[i].iter_forward()]

    def getTop(self, K):
        # 位置越靠后越领先;同房内链表正向遍历保证入房先后。
        out = []
        for i in range(len(self._rooms) - 1, -1, -1):
            for n in self._rooms[i].iter_forward():
                out.append(n.pid)
                if len(out) == K:
                    return out
        return out
```

### 复杂度

| Op | Time |
|----|------|
| `__init__` | O(R + N) |
| `proceedToNextRoom` | O(1) |
| `getPeople(roomId)` | O(k) |
| `getTop(K)` | O(R + K) |

### 陷阱
1. **sentinel 必须自环初始化**（`s.prev = s.next = s`），否则空表时 `sentinel.prev` 是 None，首次 `append` 会炸。
2. Node 存 `idx` 而非 `room_id`，unlink 时 `_rooms[node.idx]` 能 O(1) 定位 DLL。
3. `i + 1 == len(_rooms)` 判断终点，不需要哨兵值。

### 追问
- **getTop 降到 O(K)**：再维护一个"非空位置"的索引降序 DLL，append / unlink 时按 `dll.size` 从 0 ↔ 1 的切换同步更新。
- **玩家可跳过某些房间**：把 `node.idx + 1` 换成每人自己的"剩余位置序列"，或给 Node 加 `next_idx` 字段。
- **room_id 不唯一**：题目一般保证 room_id 作为主键；若真有共享属性的需求，那是辅助表 `attribute → list[room_id]` 的事，不应让 room_id 本身变非唯一。

### 45 秒口播
> "核心是每个位置一个双向链表加全局 pid→Node 哈希。必须用双向链表是因为玩家不按 FIFO 离开——先解谜者先走——要从队列中间 O(1) 摘除，list 和 deque 的中间删都做不到。DLL 里用 sentinel 自环节点充当首尾哨兵，真实节点的 prev/next 永远非 None，insert 和 unlink 都是零分支的三四行指针更新。**关键抽象是把房间序列内化成整数位置 0 到 R-1**，Node 反存 idx 而不是 room_id：proceedToNextRoom 就是 node.idx + 1 的 unlink + append，没有额外字典更新；getTop 倒序直接 range(R-1, -1, -1) 生成；room_id 退化成外部 label，只在 getPeople 输入时通过 `_room_to_idx` 反查一次。这样省掉了'下一房 idx 字典'和'倒序缓存'两个辅助结构，心智负担降到最低。"
"""

def main():
    conn = sqlite3.connect(DB)
    n = conn.execute(
        "UPDATE problems SET notes = ? WHERE id = 1068", (NOTES_1068,)
    ).rowcount
    print(f"Problem 1068: updated {n} row(s), new len = {len(NOTES_1068)}")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
