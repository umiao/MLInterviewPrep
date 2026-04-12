"""Polish LC 311/815/1244 notes: translate remaining English prose headings to Chinese.

Keeps code blocks, algorithm names (BFS, CSR, MapReduce, etc.), complexity notation,
and LeetCode problem references in English per task spec.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"


LC_311 = """## Sparse Matrix Multiplication (LC 311)

### **思路：稀疏矩阵优化**

标准矩阵乘法 O(m*k*n)，但稀疏矩阵中大量元素为 0，乘以 0 的运算可以完全跳过。

**核心优化**：预处理每行/每列的非零元素位置和值，只遍历非零项。

### **解法：双稀疏表示**

```python
class Solution:
    def multiply(self, mat1, mat2):
        m, k, n = len(mat1), len(mat1[0]), len(mat2[0])
        res = [[0] * n for _ in range(m)]

        # 预处理 mat1：每行记录非零的 (列号, 值)
        sparse1 = [[] for _ in range(m)]
        for i in range(m):
            for j in range(k):
                if mat1[i][j]:
                    sparse1[i].append((j, mat1[i][j]))

        # 预处理 mat2：每行记录非零的 (列号, 值)
        sparse2 = [[] for _ in range(k)]
        for i in range(k):
            for j in range(n):
                if mat2[i][j]:
                    sparse2[i].append((j, mat2[i][j]))

        # 三重循环只遍历非零项
        for i in range(m):
            for col1, val1 in sparse1[i]:       # mat1[i][col1] != 0
                for col2, val2 in sparse2[col1]: # mat2[col1][col2] != 0
                    res[i][col2] += val1 * val2

        return res
```
- 时间：O(m*k*n) 最坏，实际 O(nnz1 * avg_nnz2_per_row)，nnz 表示非零元素数
- 空间：O(nnz1 + nnz2) 稀疏表示

---

### **关键技巧**

1. **跳过零元素**：`res[i][j] += mat1[i][col] * mat2[col][j]`，只有当 mat1[i][col] 和 mat2[col][j] 都非零时才计算
2. **稀疏表示**：`sparse1[i]` 存 (col, val) 对，`sparse2[k]` 存 (col, val) 对；三重循环变为“对每个 i，对 i 行的非零 col1，对 col1 行的非零 col2”
3. **为什么不用 CSR/CSC？** 面试中 list-of-tuples 最直观；CSR（压缩稀疏行）是工业标准但实现复杂

### **进阶追问**

- **如果矩阵极大（分布式）？** → 分块乘法（Block Matrix Multiplication）；用 MapReduce：map 阶段按 (i, j) 分发，reduce 阶段累加
- **如果需要多次乘法？** → 预处理一次稀疏表示，后续复用
- **CSR 格式**：由 `values[]`、`col_indices[]`、`row_ptr[]` 三个数组构成，是 scipy.sparse 的标准格式
- **LC 1570 Dot Product of Two Sparse Vectors**：一维简化版，思路一致
"""


LC_815 = """## Bus Routes (LC 815)

### **我的解法：以路线为节点的 BFS（有性能隐患）**

```python
class Solution:
    def numBusesToDestination(self, routes, source, target):
        if source == target:
            return 0
        routeData = {i: set(route) for i, route in enumerate(routes)}
        queue = deque()
        visited = set()
        for i in routeData:
            if source in routeData[i]:
                queue.append(i)
                visited.add(i)
        if not queue:
            return -1
        ans = 1
        while queue:
            for _ in range(len(queue)):
                cur = queue.popleft()
                if target in routeData[cur]:
                    return ans
                for key in routeData:  # 每条路线 O(R) —— 瓶颈！
                    if key not in visited and routeData[key] & routeData[cur]:
                        queue.append(key)
                        visited.add(key)
            ans += 1
        return -1
```
- **问题**：内层遍历所有路线 O(R)，集合取交 O(S)，总复杂度 O(R^2 * S)；路线多时会 TLE

---

### **最优解：以站点为节点的 BFS + `stop_to_routes` 映射**

预建 `stop -> [route_ids]` 映射，通过站点找相邻路线，每个站点和路线只访问一次。

```python
from collections import deque, defaultdict

class Solution:
    def numBusesToDestination(self, routes, source, target):
        if source == target:
            return 0

        # 预处理：每个站点属于哪些路线
        stop_to_routes = defaultdict(set)
        for i, route in enumerate(routes):
            for stop in route:
                stop_to_routes[stop].add(i)

        visited_routes = set()
        visited_stops = set([source])
        queue = deque([source])  # 以站点为节点做 BFS
        buses = 0

        while queue:
            buses += 1
            for _ in range(len(queue)):
                stop = queue.popleft()
                for route_id in stop_to_routes[stop]:
                    if route_id in visited_routes:
                        continue
                    visited_routes.add(route_id)
                    for next_stop in routes[route_id]:
                        if next_stop == target:
                            return buses
                        if next_stop not in visited_stops:
                            visited_stops.add(next_stop)
                            queue.append(next_stop)
        return -1
```
- 时间：O(R * S) 建图 + O(R * S) BFS，每个站点和路线各访问一次
- 空间：O(R * S)

---

### **关键技巧**

1. **以站点 BFS vs 以路线 BFS**：站点级 BFS 通过 `stop_to_routes` 映射找相邻路线，避免 O(R^2) 的两两集合比较
2. **双 visited 集合**：`visited_routes` 防止重复展开路线，`visited_stops` 防止重复入队站点
3. **为什么不用路线 BFS + 集合取交？** 当 R=500、S=10^5 时，O(R^2*S) 约 2.5*10^12，必定 TLE

### **进阶追问**

- **LC 1135 Connecting Cities With Minimum Cost**：图上的最小生成树
- **面试追问**：如果需要输出具体换乘方案？→ BFS 时记录每条路线的来源（父路线 + 换乘站点）
"""


LC_1244 = """## Design A Leaderboard (LC 1244)

### **思路**
用 HashMap 存储 `playerId -> score`。`addScore` 累加分数，`top(K)` 取前 K 大分数之和，`reset` 删除玩家。

### **核心代码**
```python
import heapq
from collections import defaultdict

class Leaderboard:
    def __init__(self):
        self.scores: dict[int, int] = defaultdict(int)

    def addScore(self, playerId: int, score: int) -> None:
        self.scores[playerId] += score

    def top(self, K: int) -> int:
        return sum(heapq.nlargest(K, self.scores.values()))

    def reset(self, playerId: int) -> None:
        del self.scores[playerId]
```

### **关键技巧**
- `top(K)` 用 `heapq.nlargest` 比完全排序更优：O(n log K) vs O(n log n)
- `addScore` 是累加，不是覆盖
- 若 `top(K)` 调用频繁，可用 `SortedList` 把查询优化到 O(K)

### **复杂度**
- `addScore`：O(1)；`top`：O(n log K)；`reset`：O(1)
- 空间：O(n)
"""


def main() -> None:
    updates = {311: LC_311, 815: LC_815, 1244: LC_1244}
    conn = sqlite3.connect(DB)
    try:
        cur = conn.cursor()
        for lc, notes in updates.items():
            cur.execute(
                "UPDATE problems SET notes = ? WHERE leetcode_id = ?",
                (notes, lc),
            )
            print(f"[UPDATE] LC {lc}: {len(notes)} chars, rows={cur.rowcount}")
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
