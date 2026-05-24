"""Condense Pinterest LC 1564/1580 + Escape Room notes per user feedback 2026-04-15.

Changes:
- Keep 45-sec 口播 script (user preference).
- Drop multi-line dry-run walkthroughs (redundant with script).
- 1580 main body switched to two-end two-pointer greedy (O(1) space, matches doc 47 framing).
- Escape Room: deduplicated English/Chinese sections, fixed table formatting, tightened code comments.

Idempotent: re-running overwrites notes to the canonical version below.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

LC_1564 = """## LC 1564 - Put Boxes Into Warehouse I (前缀 min + 贪心)

> Pinterest must-do (2025-11). Sister: LC 1580.

### 核心洞察
箱子从左入口进，第 j 号房间被沿途最矮房间卡住 → **有效限高 `eff[j] = min(warehouse[0..j])`** 是单调不增的"走廊"。

### 贪心（两种镜像写法等价）
- **大箱配大房**：`boxes desc`，指针 `i=0` 从最高房开始；`box <= eff[i]` 则放 + `i++`，否则**丢箱**（i 不动，更小的箱可能仍能塞进 eff[i]）。
- **小箱配小房**：`boxes asc`，从 `eff[-1]` 最矮房开始；塞不进则**跳房间**（矮到所有未放箱都塞不下）。

关键：塞不进时跳**哪一侧**取决于方向——方向错了会错失未来配对。

### Code（O(n + m log m) time, O(1) 额外空间）
```python
def maxBoxesInWarehouse(boxes, warehouse):
    eff = warehouse[:]
    for j in range(1, len(eff)):
        eff[j] = min(eff[j-1], eff[j])
    boxes.sort(reverse=True)
    ans, i = 0, 0
    for box in boxes:
        if i < len(eff) and box <= eff[i]:
            ans += 1; i += 1
    return ans
```

### 与 1580 的差别
1564 单入口 → eff 单调不增，无需排序；1580 双入口 → eff 非单调，必须**排序 eff** 或用**双端双指针**。

### 45 秒口播
> "箱子从左进入，第 j 号房间的有效限高是 warehouse 从 0 到 j 的前缀 min，一次扫描得到一条单调不增的'有效走廊'。然后贪心：把箱子降序排序，从最高房间开始；当前最大箱塞得下就塞，塞不下就丢这个箱子（更小的也许仍能塞进这间高房），指针不动。O(n + m log m) 时间，O(1) 额外空间（原地改 warehouse）。与 1580 的差别：1580 允许两侧进入，eff 变成 max(前缀 min, 后缀 min) 的上包络，不再单调，需要排序 eff 后双指针配对，或者更优雅地用双端指针每步把当前最大箱放到 warehouse 更高的那一端。"
"""

LC_1580 = """## LC 1580 - Put Boxes Into Warehouse II (双入口 + 双端双指针)

> Pinterest must-do (2025-11). Sister: LC 1564.

### 核心洞察
箱子可从左或右进入，房间 j 受"入口侧前缀 min"约束，箱子选更宽松一侧 → `eff[j] = max(leftMin[j], rightMin[j])`。但 eff **不再单调**，1564 写法失效。

### 贪心：双端双指针（推荐，O(1) 额外空间）
**关键观察**：当前最大箱只能塞进 warehouse 的两端之一。理由：若它能放在中段某位置 j，则从至少一个入口走到 j 的路径全部 >= box；那条路径上**靠近入口的两端位置**自然也 >= box，可直接放在端点。

```python
def maxBoxesInWarehouse(boxes, warehouse):
    boxes.sort(reverse=True)
    l, r, ans = 0, len(warehouse) - 1, 0
    for box in boxes:
        if l > r: break
        if warehouse[l] >= box:
            l += 1; ans += 1
        elif warehouse[r] >= box:
            r -= 1; ans += 1
        # else: 两端都塞不下该大箱 -> 丢箱
    return ans
```

**O(n + m log m) 时间，O(1) 额外空间**。

### 备选写法：排序 eff
构造 `eff[j] = max(leftMin[j], rightMin[j])`，排序 eff + 排序 boxes，小箱配小房，塞不进则跳房间。正确但多 O(n log n) 排序 + O(n) 空间，不如双端法干净。

### 陷阱
1. `eff` 取 `max`（选宽松一侧）**不是 min**——这是与 1564 最容易混淆的点。
2. 双端法两端都塞不下时丢**箱**（不是房），因为大箱别处也塞不进，更小的箱后续仍可试左右指针之间的中段。

### 45 秒口播
> "箱子可双向入，每个房间的有效限高 = max(从左进来的前缀 min, 从右进来的后缀 min)——箱子选更宽松的一侧。eff 不再单调，所以 1564 的'从最矮房扫'失效。最干净的写法是双端双指针：boxes 降序排，左右指针夹住 warehouse；当前最大箱试两端，哪端够高就放入哪端并收缩该端，两端都不够高就丢箱。正确性：最大箱只能落在两端，因为中段任何可行位置的路径两端已经 >= box，可以就近放端点。O(n + m log m) 时间，O(1) 额外空间。"
"""

ESCAPE_ROOM = """## Escape Room Game State (Pinterest 2025-11)

三个操作：
- `proceedToNextRoom(pid)` — 单人前进一房，O(1)
- `getPeople(roomId)` — 房内按入房序返回，O(k)
- `getTop(K)` — 按 (房号降序, 同房内入房序) 返回前 K 名，O(R + K)

### 数据结构
- **每房一个双向链表（DLL）**：O(1) 尾部 append、O(1) 按节点指针 unlink
- **全局 `pid → Node` 哈希**：O(1) 定位某人当前节点
- **`pid → next_idx`**：预存前进序列中下一位下标，避免每次 O(R) 扫描

**为什么必须 DLL**：人不按 FIFO 出房（先解谜者先走），需要从中间 O(1) 摘除；`list.remove` 和 `deque` 中间删除都是 O(k)。Node 里反存 `room_id` 让 unlink 能找到所属房间。

### Code
```python
class _Node:
    __slots__ = ('pid', 'room_id', 'prev', 'next')
    def __init__(self, pid, room_id):
        self.pid, self.room_id = pid, room_id
        self.prev = self.next = None

class _DLL:
    __slots__ = ('head', 'tail', 'size')
    def __init__(self):
        self.head = self.tail = None
        self.size = 0
    def append(self, node):
        node.prev, node.next = self.tail, None
        if self.tail: self.tail.next = node
        else: self.head = node
        self.tail = node
        self.size += 1
    def unlink(self, node):
        if node.prev: node.prev.next = node.next
        else: self.head = node.next
        if node.next: node.next.prev = node.prev
        else: self.tail = node.prev
        node.prev = node.next = None
        self.size -= 1
    def iter_forward(self):
        cur = self.head
        while cur:
            yield cur
            cur = cur.next

class Game:
    def __init__(self, rooms, people):
        self._order = list(rooms)
        self._order_desc = list(reversed(rooms))
        self._rooms = {rid: _DLL() for rid in rooms}
        self._people = {}
        self._next_idx = {}
        start = rooms[0]
        for pid in people:
            node = _Node(pid, start)
            self._rooms[start].append(node)
            self._people[pid] = node
            self._next_idx[pid] = 1 if len(rooms) > 1 else -1

    def proceedToNextRoom(self, pid):
        node = self._people[pid]
        nxt = self._next_idx[pid]
        if nxt == -1: return  # already final
        self._rooms[node.room_id].unlink(node)
        new_room = self._order[nxt]
        node.room_id = new_room
        self._rooms[new_room].append(node)
        self._next_idx[pid] = nxt + 1 if nxt + 1 < len(self._order) else -1

    def getPeople(self, roomId):
        dll = self._rooms.get(roomId)
        return [n.pid for n in dll.iter_forward()] if dll else []

    def getTop(self, K):
        out = []
        for rid in self._order_desc:
            for n in self._rooms[rid].iter_forward():
                out.append(n.pid)
                if len(out) == K: return out
        return out
```

### 复杂度
| Op | Time |
|----|------|
| `__init__` | O(R + N) |
| `proceedToNextRoom` | O(1) |
| `getPeople(roomId)` | O(k) 物化 |
| `getTop(K)` | O(R + K) |

### 陷阱
1. Node 反存 `room_id`，unlink 才知道从哪个 DLL 摘。
2. `_next_idx` 预存，避免每次 `rooms.index(current)` 的 O(R)。
3. 终点房用 `-1` 哨兵，`proceedToNextRoom` no-op。

### 追问
- **getTop 要 O(K)**：再维护一个"非空房间"的房号降序 DLL，append/unlink 时同步更新。
- **有人跳房间**：把 `_next_idx` 换成每人自己的剩余房间序列列表。

### Self-test
```python
g = Game([1, 2, 3], [10, 20, 30])
assert g.getPeople(1) == [10, 20, 30]
g.proceedToNextRoom(20)
assert g.getPeople(1) == [10, 30] and g.getPeople(2) == [20]
g.proceedToNextRoom(30); g.proceedToNextRoom(20)
assert g.getTop(2) == [20, 30]
assert g.getTop(10) == [20, 30, 10]
```

### 45 秒口播
> "核心是每房一个双向链表加全局 pid→Node 哈希。必须双向链表是因为人不按 FIFO 出房——先解谜者先走——要从队中间 O(1) 摘除，list 和 deque 的中间删都做不到。Node 反存 room_id 让 unlink 能找到所属链表。proceedToNextRoom 是 O(1) 的 unlink 旧房加 append 新房尾；入房尾部保证同房内入房顺序正确。getPeople 正向遍历 O(k)。getTop 按房号倒序扫链表正向累计到 K，O(R + K)；要降到 O(K) 可以再维护一个非空房间的房号降序链表。关键冗余是 pid→Node 让定位 O(1)，next_idx 预存前进下标避免每次扫 rooms。"
"""

UPDATES = [
    (1564, LC_1564),
    (1580, LC_1580),
]

def main():
    conn = sqlite3.connect(DB)
    for lcid, notes in UPDATES:
        n = conn.execute(
            "UPDATE problems SET notes = ? WHERE leetcode_id = ?",
            (notes, lcid),
        ).rowcount
        print(f"LC {lcid}: updated {n} row(s), new len = {len(notes)}")
    n = conn.execute(
        "UPDATE problems SET notes = ? WHERE id = 1068",
        (ESCAPE_ROOM,),
    ).rowcount
    print(f"Problem 1068 (Escape Room): updated {n} row(s), new len = {len(ESCAPE_ROOM)}")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
