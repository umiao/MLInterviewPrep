"""One-shot: translate LC 332 solution notes to Chinese."""
import sqlite3

NOTES = r'''## LC 332 - Reconstruct Itinerary (Hierholzer's Algorithm)

> Pinterest must-do list. See [Pinterest Prep Notes](../docs/pinterest_recruiter_call_prep.md#pinterest-lc-%E5%BF%85%E5%88%B7%E9%A2%98%E5%88%97%E8%A1%A8-14-%E9%A2%98)

### 核心洞察 (Information Gap)

这道题并不是标准的 backtracking 问题。它本质上是在一个有向图中寻找 **Eulerian Path** —— 一条恰好经过每条边一次的路径。对应的核心算法是 **Hierholzer's Algorithm**，时间复杂度 O(E)。如果不知道 Hierholzer，一般会退化成 O(E! * V) 的 backtracking，在大输入下会 TLE。

**为什么是 Eulerian Path？** "把所有机票用完一次" = 每条边只经过一次；"必须从 JFK 出发" = 固定起点；题目保证存在合法行程 = Eulerian path 一定存在。

### Hierholzer's Algorithm

1. 构建邻接表（有向图），对每个节点的邻居按字典序排序（使用 min-heap 更高效）。
2. 从 JFK 开始 DFS，每次贪心取字典序最小的邻居（`heappop`）。
3. 当一个节点没有可走的边时，**post-order** 把它 append 到结果里。
4. 最后把结果反转。

**为什么用 post-order？** 如果 pre-order 直接 append，可能在所有边用完之前就卡在 dead-end。Post-order 让 dead-end 最先被 append（反转后它们会排在结果末尾），而还有剩余边的节点继续深入探索。

**为什么要反转？** Post-order 是倒着构建路径的。最先耗尽所有边的节点对应行程的**最后**一个机场。

### 标准解法 (Polished Solution)

```python
from collections import defaultdict
import heapq

class Solution:
    def findItinerary(self, tickets: list[list[str]]) -> list[str]:
        graph = defaultdict(list)
        for src, dst in tickets:
            heapq.heappush(graph[src], dst)

        route = []

        def dfs(node: str) -> None:
            while graph[node]:
                nxt = heapq.heappop(graph[node])
                dfs(nxt)
            route.append(node)  # post-order

        dfs("JFK")
        return route[::-1]
```

**写法要点**：
- 用 `heapq` 在建图过程中直接维持 min-heap，省掉事后 `heapify` 的一步。
- `route` 用闭包捕获的局部 list，不污染 instance 状态。
- `while graph[node]` 而不是 `for`：因为递归过程中会不断 pop，`for` 的迭代器会失效。

### Complexity

- **Time**: O(E log E)，E = 机票数。每条边入堆出堆各一次，每次 log E。
- **Space**: O(E + V)，图 + 递归栈。

### Traps & Edge Cases

1. **同一对城市之间有重复边**：例如 JFK->SFO 出现两次。heap 天然支持重复元素。
2. **Dead-end 检测**：靠 post-order 解决。朴素的贪心 DFS 会卡住。
3. **字典序**：heap 每次给出最小邻居。用 sort 也可以，但和 pop 的模式配合时 heap 更自然。
4. **递归深度**：最多 300 张机票 = 最多 301 层递归，Python 默认 1000 深度下安全。

### 面试模式识别 (Pattern Recognition)

看到 "用完每一条 [edge / ticket / connection] 恰好一次" + "重建路径" 的组合，立刻想到 **Eulerian Path** + **Hierholzer's**。

注意区分 **Hamiltonian Path**（每个 node 只经过一次），后者是 NP-complete，性质完全不同。
'''

conn = sqlite3.connect("data/mle_prep.db")
conn.execute("UPDATE problems SET notes = ? WHERE leetcode_id = 332", (NOTES,))
conn.commit()
print(f"[OK] LC 332 notes updated ({len(NOTES)} chars)")
conn.close()
