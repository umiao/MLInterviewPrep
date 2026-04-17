"""Overwrite LC 1244 notes with user's lazy-heap variant + canonical nlargest discussion."""
import sqlite3

NOTES = r'''## LC 1244 - Design A Leaderboard (nlargest vs Lazy Heap)

> Pinterest must-do 列表。见 [Pinterest Prep Notes](../docs/company/pinterest/recruiter_call_prep.md)。

### 题意回顾
设计一个 `Leaderboard`，支持：
- `addScore(playerId, score)`：玩家分数累加（不是赋值）
- `top(K)`：返回当前分数最高的 K 个玩家的分数之和
- `reset(playerId)`：把玩家分数清零

LC 约束：最多 1000 次调用，`1 <= K <= playerCount`，分数累加无上限。

---

### 关键判断：该用哪种数据结构？

**结论先行**：本题的 LC 约束（<= 1000 次调用）下，**每次 `top()` 都重新用 `heapq.nlargest` 是最推荐写法** —— 简单、正确、快到足够。Lazy heap 的"摊还优秀"只在**写远多于读**且**玩家数巨大**时才值得，小规模下反而是 bug 温床。

| 方案 | `addScore` | `top(K)` | `reset` | 复杂度假设 | 推荐度 |
|------|-----------|----------|---------|------------|--------|
| **A. Hash + nlargest**（canonical）| O(1) | O(N log K) | O(1) | 小 N 下完全够 | ⭐ 推荐 |
| **B. Lazy heap**（你的写法）| O(log M) | O((M-N') log M) 最坏 | O(1) | 玩家量大且 `top` 稀疏 | [!] 细节多 |
| **C. SortedList** | O(log N) | O(K) | O(log N) | 需 `sortedcontainers` | 面试不便 |

其中 N = 当前玩家数，M = heap 中累积条目数（含过期），N' = 一次 top() 中遇到的有效条目数。

---

### Approach A: Hash + `nlargest` (canonical 写法)

```python
import heapq

class Leaderboard:
    def __init__(self):
        self.scores = {}

    def addScore(self, playerId: int, score: int) -> None:
        self.scores[playerId] = self.scores.get(playerId, 0) + score

    def top(self, K: int) -> int:
        return sum(heapq.nlargest(K, self.scores.values()))

    def reset(self, playerId: int) -> None:
        self.scores[playerId] = 0
```

**为什么 nlargest 已经够快**：`heapq.nlargest(K, iterable)` 内部维护一个大小为 K 的 min-heap，扫一遍 iterable：O(N log K)。K 远小于 N 时接近 O(N)。N <= 1000 的 LC 约束下，单次 `top` 顶多 ~10K 次比较，完全不用纠结。

**优点**：没有 stale entry 问题，没有恢复步骤，`reset` 就一行。面试首选。

---

### Approach B: Lazy Heap (你的写法)

```python
import heapq

class Leaderboard:
    def __init__(self):
        self.scores = {}          # ground truth: playerId -> current score
        self.heap = []            # lazy heap: may contain stale entries

    def addScore(self, playerId, score):
        self.scores[playerId] = self.scores.get(playerId, 0) + score
        heapq.heappush(self.heap, (-self.scores[playerId], playerId))

    def top(self, K):
        taken, total = [], 0
        while len(taken) < K:
            neg, pid = heapq.heappop(self.heap)
            if -neg == self.scores.get(pid, 0):   # 只接受最新快照
                total += -neg
                taken.append((neg, pid))
                self.scores[pid] = -1             # 防止同 id 被再取
        for neg, pid in taken:
            self.scores[pid] = -neg               # 恢复
            heapq.heappush(self.heap, (neg, pid))
        return total

    def reset(self, playerId):
        self.scores[playerId] = 0
```

核心思路：每次 `addScore` 往 heap push 新 `(-score, pid)`，不删旧条目；`top` 里 pop 时靠 `scores` 字典校验"是否最新"，过期条目自动丢弃。

**为什么这种 lazy 写法容易翻车**（按严重程度排序）：

1. **`self.scores[pid] = -1` 是 magic 哨兵**：题目没保证分数不会为负。若分数真的有 -1（题目不保证不出现），恢复步骤就乱了。**修法**：改用一个局部 `seen = set()` 判断是否已取过本次 top。
2. **必须恢复状态**：pop 出来的条目在 `top` 结束前必须 push 回去，否则后续 `top(K)` 拿不到这些玩家。任何 early return / 异常都会破坏不变量。
3. **堆大小无上限**：每次 `addScore` 都 push 新条目，不清理旧的。100 万次 `addScore` 后 heap 里有 100 万条，哪怕只有 10 个玩家。内存/时间都退化。
4. **`top()` 的最坏复杂度是 O(M log M)**：如果连续 `top` 前大量 `addScore` 累积 stale，第一次 `top` 要 pop 掉一大堆过期条目。
5. **思考负担重**：hash 字典 + lazy heap 双真值源，调试很累。面试时写错一处直接挂。

**修正版（如果面试非要 lazy heap）**：

```python
def top(self, K: int) -> int:
    seen, taken, total = set(), [], 0
    while len(taken) < K:
        neg, pid = heapq.heappop(self.heap)
        if pid in seen or -neg != self.scores.get(pid, 0):
            continue   # stale or duplicate -> discard
        seen.add(pid)
        taken.append((neg, pid))
        total += -neg
    for entry in taken:
        heapq.heappush(self.heap, entry)   # 恢复 heap
    return total
```

不再用 `scores[pid] = -1` 哨兵，不再破坏 ground truth。

---

### 什么场景下 lazy heap 才值得？

- **玩家数 N 极大**（百万级）且 `top(K)` 的 K 很小，读远少于写：`nlargest` 每次 O(N log K) 太贵
- **数据流场景**（不能一次性扫全表）：典型的 streaming top-K
- **需要 sublinear top**：配合 heap size 定期清理或换 SortedList

LC 1244 的约束完全不是这种场景。

---

### Approach C: SortedList (有外部库可用时)

```python
from sortedcontainers import SortedList

class Leaderboard:
    def __init__(self):
        self.scores = {}
        self.sorted = SortedList()   # 所有当前分数

    def addScore(self, playerId, score):
        if playerId in self.scores:
            self.sorted.remove(self.scores[playerId])
        self.scores[playerId] = self.scores.get(playerId, 0) + score
        self.sorted.add(self.scores[playerId])

    def top(self, K):
        return sum(self.sorted[-K:])   # O(K)

    def reset(self, playerId):
        if playerId in self.scores:
            self.sorted.remove(self.scores[playerId])
            del self.scores[playerId]
```

每次 `addScore` O(log N)，`top(K)` O(K)，`reset` O(log N)。
**但 LC 默认不给 `sortedcontainers`**，真面试看平台；CoderPad 用 Python 的话可以直接用。

---

### Interview Talking Points

1. **先给 canonical (Approach A)**：简洁、正确、复杂度足够。面试官满意后再展开讨论其他方案。
2. **讨论 scale-up**：如果玩家数 1M + top(10) 频繁调用，才需要 lazy heap 或 SortedList 取舍。
3. **对 `reset` 的行为说清楚**：题目是清零，不是删除 —— 说完清零后玩家仍参与后续 `top`（只是分数 0）。
4. **负分数的含义**：题目保证 score >= 0，但 reset 行为的选择使 0 分玩家仍在表中；说清楚你是否把 0 分玩家排除出 `top`。

### 相关题
- **LC 703** Kth Largest Element in a Stream —— 维护 size=K 的 min-heap，这是 lazy heap 真正擅长的场景
- **LC 480** Sliding Window Median —— 双 heap（max+min）+ lazy delete 经典案例
- **LC 295** Find Median from Data Stream —— 同 480 的双 heap pattern

### Complexity 汇总

| 方法 | add | top(K) | reset |
|------|-----|--------|-------|
| A. nlargest | O(1) | O(N log K) | O(1) |
| B. Lazy heap | O(log M) 摊还 | O((M stale) log M) | O(1) |
| C. SortedList | O(log N) | O(K) | O(log N) |

**面试默认写 A**，除非明确被要求讨论 scale。
'''

conn = sqlite3.connect("data/mle_prep.db")
conn.execute("UPDATE problems SET notes = ? WHERE leetcode_id = 1244", (NOTES,))
conn.commit()
print(f"[OK] LC 1244 notes updated ({len(NOTES)} chars)")
conn.close()
