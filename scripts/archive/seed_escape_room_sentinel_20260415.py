"""Rewrite Escape Room (id 1068) notes with sentinel-based DLL per user feedback 2026-04-15.

Changes:
- Switch _DLL from head/tail + None sentinels to a single self-looping sentinel node.
  Every real node has non-None prev/next, so append/unlink become branch-free.
- Add comments explaining design intent (why sentinel, why reverse-pointer to room_id,
  why pre-stored next_idx) without line-by-line annotation noise.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

NOTES_1068 = """## Escape Room Game State (Pinterest 2025-11)

三个操作：
- `proceedToNextRoom(pid)` — 玩家 pid 前进一房，O(1)
- `getPeople(roomId)` — 按入房顺序返回房内玩家，O(k)
- `getTop(K)` — 按 (房号降序, 同房入房序) 返回前 K 名，O(R + K)

### 数据结构
- **每房一个双向链表（DLL）**，用 **sentinel 自环** 实现：O(1) 尾部 append、O(1) 按节点指针 unlink，且所有真实节点的 `prev/next` 永远非 None（无需 None 分支判断）。
- **全局 `pid → Node` 哈希**：O(1) 定位某人当前节点。
- **`pid → next_idx`**：预存前进序列中下一位的下标，避免每次 O(R) 扫描 `rooms.index(current)`。

**为什么必须用 DLL**：玩家不按 FIFO 离开（先解谜者先走），要从队列中间 O(1) 摘除。`list.remove` 和 `collections.deque` 的中间删除都是 O(k)。

**为什么用 sentinel 自环**：普通 "head/tail + None" 写法里，`append` 要判 `tail is None`，`unlink` 要判 `node.prev is None` 和 `node.next is None` 共四处——边界条件多，是常见 bug 点。sentinel 自环让空表本身也是"首尾指向 sentinel"的合法形态，insert/unlink 全部走统一指针更新路径、零分支。代价是每个 DLL 多占一个 sentinel 节点（空房间也占 1）——对 R 个房间即 +R 节点，完全可忽略。

**为什么 Node 要反存 `room_id`**：`unlink(node)` 发生在全局哈希拿到的 Node 上，需要知道它属于哪个房间的 DLL 才能操作；反指针让这步也是 O(1)。

### Code

```python
class _Node:
    # 真实节点携带 pid 与当前 room_id (反指针,unlink 时 O(1) 定位所属 DLL);
    # sentinel 节点 pid=room_id=None,只作为首尾哨兵占位。
    def __init__(self, pid, room_id):
        self.pid, self.room_id = pid, room_id
        self.prev = self.next = None


class _DLL:
    \"\"\"Sentinel-based doubly linked list.

    不变量:sentinel.next 指向 head(无真实节点时即 sentinel 自身),
    sentinel.prev 指向 tail。所有真实节点都插在 sentinel.prev 与
    sentinel 之间,因此它们的 prev/next 永远非 None。
    \"\"\"

    def __init__(self):
        s = _Node(None, None)
        s.prev = s.next = s   # 空表时自环:sentinel ↔ sentinel
        self.sentinel = s
        self.size = 0

    def append(self, node):
        # 在 sentinel 前插入,等价于挂到链表尾部。
        tail = self.sentinel.prev
        node.prev, node.next = tail, self.sentinel
        tail.next = self.sentinel.prev = node
        self.size += 1

    def unlink(self, node):
        # 真实节点的 prev/next 都是非 None 的(sentinel 保证);无需判空。
        node.prev.next, node.next.prev = node.next, node.prev
        node.prev = node.next = None
        self.size -= 1

    def iter_forward(self):
        # 从 head 开始遍历,到 sentinel 停止。
        cur = self.sentinel.next
        while cur is not self.sentinel:
            yield cur
            cur = cur.next


class Game:
    \"\"\"Escape room state manager.

    rooms: 按前进顺序的房号(如 [1, 2, 3, 4, 5])
    people: 初始玩家列表,全部放入 rooms[0]
    \"\"\"

    def __init__(self, rooms, people):
        # _order: 房间按前进顺序排的房号序列。下标 i 对应第 i+1 个房间。
        self._order = list(rooms)

        # _order_desc: _order 的逆序缓存。getTop 要从最后一房往前扫,
        # 预缓存避免每次调用都临时 reverse。
        self._order_desc = list(reversed(rooms))

        # _rooms: 房号 -> 房内玩家的双向链表。每个 DLL 保留入房顺序,
        # 支持 O(1) append 和 O(1) unlink(靠节点指针,不用查找)。
        self._rooms = {rid: _DLL() for rid in rooms}

        # _people: pid -> Node。全局索引,让任何操作能 O(1) 拿到玩家
        # 当前所在的 DLL 节点(节点自带 room_id 反指针,顺便定位所属房)。
        self._people = {}

        # _next_idx: pid -> "该玩家下一个要去的房间在 _order 中的下标"。
        # 预存而不是每次查 _order.index(current) 来避免 O(R) 扫描;
        # 取值 -1 表示玩家已在终点房,proceedToNextRoom 会 no-op。
        self._next_idx = {}

        start = rooms[0]
        for pid in people:
            node = _Node(pid, start)
            self._rooms[start].append(node)
            self._people[pid] = node
            self._next_idx[pid] = 1 if len(rooms) > 1 else -1

    def proceedToNextRoom(self, pid):
        # 流程:查 Node -> unlink 旧房 DLL -> 切 room_id -> append 新房 DLL -> 更新 next_idx。
        node = self._people[pid]
        nxt = self._next_idx[pid]
        if nxt == -1:
            return                                 # 已在终点房,无动作
        self._rooms[node.room_id].unlink(node)
        new_room = self._order[nxt]
        node.room_id = new_room
        self._rooms[new_room].append(node)
        self._next_idx[pid] = nxt + 1 if nxt + 1 < len(self._order) else -1

    def getPeople(self, roomId):
        # 按入房顺序物化 pid 列表;未知 roomId 返回 [].
        dll = self._rooms.get(roomId)
        return [n.pid for n in dll.iter_forward()] if dll else []

    def getTop(self, K):
        # 房号降序外层循环,同房内链表正向遍历保证入房先后;累计到 K 提前返回。
        out = []
        for rid in self._order_desc:
            for n in self._rooms[rid].iter_forward():
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
2. Node 里要反存 `room_id`，unlink 时才能定位所属房间的 DLL。
3. `_next_idx` 必须预存。每次现算 `rooms.index(current)` 会把 `proceedToNextRoom` 拉到 O(R)。
4. 终点房用 `-1` 哨兵，`proceedToNextRoom` 直接 no-op。

### 追问
- **getTop 降到 O(K)**：再维护一个"非空房间"的房号降序 DLL，append / unlink 时按 `dll.size` 从 0↔1 的切换同步更新该结构。
- **玩家可跳过某些房间**：把 `_next_idx` 换成每人自己的剩余房间序列列表，仍然 O(1) 取下一房。
- **getPeople 不物化、只暴露迭代器**：直接 `yield from dll.iter_forward()` 即可，节省 O(k) 空间。

### 45 秒口播
> "核心是每房一个双向链表加全局 pid→Node 哈希。必须用双向链表是因为玩家不按 FIFO 离开——先解谜者先走——要从队列中间 O(1) 摘除，list 和 deque 的中间删都做不到。DLL 里用一个 sentinel 自环节点充当首尾哨兵，真实节点的 prev/next 永远非 None，insert 和 unlink 都是零 if 分支的三四行指针更新，边界 bug 大幅减少。Node 反存 room_id 让 unlink 能定位所属链表。proceedToNextRoom 就是 O(1) 的 unlink 旧房加 append 新房尾；入房尾部保证同房内入房顺序正确。getTop 按房号倒序扫链表正向累计到 K，O(R + K)；若要 O(K) 可以再维护一个非空房间的房号降序链表。关键冗余是 pid→Node 让定位 O(1)，next_idx 预存前进下标避免每次扫 rooms。"
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
