"""One-shot: translate LC 2402 solution notes to Chinese."""
import sqlite3

NOTES = r'''## LC 2402 - Meeting Rooms III (Two-Heap Simulation)

> Pinterest must-do list. See [Pinterest Prep Notes](../docs/company/pinterest/recruiter_call_prep.md#pinterest-lc-%E5%BF%85%E5%88%B7%E9%A2%98%E5%88%97%E8%A1%A8-14-%E9%A2%98)

### 题目回顾
- 共 `n` 个房间，编号 `0..n-1`。给出 `meetings[i] = [start, end]`，所有 `start` 互不相同。
- 规则：每个 meeting 占用**当前空闲中编号最小**的房间；如果没有空闲房间，则**推迟**到**最早结束**的房间空出来（duration 保持不变，tiebreak 取编号最小的房间）。
- 返回承办 meeting 次数最多的房间编号（tiebreak 取最小编号）。

### 核心模式：Two-Heap Simulation

- **Free heap**：`free_rooms` = 房间编号的 min-heap（编号最小的先 pop）。
- **Busy heap**：`(end_time, room_id)` 的 tuple（最早结束的先 pop；tuple 比较会自动在同 end_time 时给出最小 room_id）。

按 start 时间遍历每个 meeting：
1. **Release**：当 `busy[0].end <= start` 时，把该房间从 `busy` 移到 `free`。
2. **Assign**：
   - 若 `free` 非空：pop 编号最小的 free 房间，push `(end, room)` 到 busy。
   - 否则：从 busy pop 出最早结束的 `(end_busy, room)`，push `(end_busy + (end - start), room)` —— meeting 被推迟但 duration 保留。
3. `count[room]` 加一。

最后 `count.index(max(count))` 返回承办次数最多、编号最小的房间（`list.index` 返回第一次出现的位置）。

### 推荐写法

```python
import heapq

class Solution:
    def mostBooked(self, n: int, meetings: list[list[int]]) -> int:
        meetings.sort()
        free = list(range(n))   # 已经是合法的 min-heap（有序）
        busy: list[tuple[int, int]] = []   # (end_time, room_id)
        count = [0] * n

        for start, end in meetings:
            # 先释放所有在 `start` 之前结束的房间
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

### Code Review（对你的写法）

你的解法**正确且结构良好**。几点小建议：

| Issue | Original | Improved |
|-------|----------|----------|
| 命名 | `ans`（其实是 count 数组，不是答案） | `count` |
| 最后扫描 | 手写循环配 `>` 比较 | `count.index(max(count))` —— 更 idiomatic，tiebreak 语义一致 |
| Heap 初始化 | `freeRooms = [i for i in range(n)]` | `list(range(n))` —— 效果相同，已排序的 list 本身就是合法 heap |
| `occupiedRooms[0][0] <= start` | 可行 | OK，但 `<=` 是关键 —— 见下方陷阱 |

正确性方面你的逻辑是对的：
- 每轮先 release 再 assign。
- 延迟公式 `endTime + (end - start)` 保留了 duration。
- `(end_time, room_id)` tuple 给出了正确的 tiebreak（先比较 end，再比较 room_id）。
- 从 `i=0` 用严格 `>` 扫描 `ans[i] > meetingCnt`，tie 时自然返回最小编号。

### 一些微妙的陷阱

1. **release 循环里的 `<=` vs `<`**：必须是 `<=`。题目规定 meeting `[start, end]` 占用房间的区间是 `[start, end)`；如果某房间 `end == start(下一个 meeting)`，那它就是空闲的。你的代码用 `<=` 是对的。

2. **Busy heap 的 tiebreak**：当两个房间同时 end，题目要求优先选编号更小的。Tuple 比较 `(end, room)` 自动满足。若改成 `(time, -room)` 等写法则会破坏 tiebreak。

3. **Delay 使用 `(end - start)`，不是 `end`**：常见 bug 是写成 `end_busy + end`，会算出错误的结束时间。Duration 是 `end - start`。

4. **不要重建 busy heap**：push `(end_busy + duration, room)` 后 `heappush` 已经维护好了 heap property，不需要 re-sort。

5. **Meetings sort**：按 `start` 排序（默认 tuple sort 对 `[start, end]` 可行，因为题目保证 starts 互不相同）。

### 替代方案：Single-Heap（Lazy）变体

有些解法只保留 `busy`，在 heap 内部标记空闲 slot。代码更乱，且渐进复杂度相同。**为了清晰起见优先用 two-heap 模式。**

### 复杂度

设 `m = len(meetings)`。
- **时间**：sort 是 O(m log m)；每个 meeting 的 heap 操作 O(log n)（摊还：每个房间总共被 push/pop O(m) 次）。整体 **O((m + n) log n + m log m)**。
- **空间**：O(n)（heap + count 数组）。

### 面试时的模式识别

关键词：「resource allocation」「lowest-numbered available」「delay until ready」 → **two-heap simulation**（free + busy）。

相关题目：
- LC 253 Meeting Rooms II（求最少房间数 —— 一个 heap，用 end time 即可）
- LC 1834 Single-Threaded CPU（类似的两结构：pending queue + running heap）
- LC 1882 Process Tasks Using Servers（几乎完全相同的模式：free/busy heap，tiebreak 在 server weight/index）

### 总结

你的解法基本就是标准答案。改进点都是表面的（命名 `count`、用 `list.index(max(...))` 习惯用法）。把这个 two-heap 模式背下来 —— 它会出现在 LC 1882、LC 1834 以及 task scheduling 类系统设计题里。
'''


def main() -> None:
    conn = sqlite3.connect("data/mle_prep.db")
    cur = conn.cursor()
    cur.execute("UPDATE problems SET notes = ? WHERE leetcode_id = 2402", (NOTES,))
    conn.commit()
    row = cur.execute("SELECT length(notes) FROM problems WHERE leetcode_id = 2402").fetchone()
    print(f"Updated. notes length = {row[0]}")
    conn.close()


if __name__ == "__main__":
    main()
