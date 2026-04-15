"""Translate problem descriptions to Chinese for Pinterest custom problems +
recent LC follow-ups (LC 1135 / 85 / 1570 / 703 / 973 / 378).

Per user: retain API / variable names / formulas in English but write the
problem statement in Chinese. Idempotent: detects a trailing marker and skips
if already translated.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
MARKER = "\n\n*题面中文翻译 2026-04-15，原英文见 git 历史。*"

# Keyed by internal problem id for the Pinterest custom set (they have no
# leetcode_id) and by leetcode_id for the LC follow-ups.
BY_INTERNAL_ID: dict[int, str] = {
    1068: """[Pinterest coding 2026-11] 为密室逃脱体验设计一个游戏状态数据结构。房间按推进顺序
编号 1..R，玩家从编号最小的房间进入，每次前进一个房间。

**需要支持的 API**：
- `proceedToNextRoom(pid)`：把玩家 `pid` 从当前房间移动到下一个房间，保留其在新房间里按
  进入时间的排序。O(1)。
- `getPeople(roomId)`：按进入该房间的时间顺序返回 `roomId` 里当前的玩家列表。返回句柄
  O(1)，物化整张列表 O(k)，其中 k 是该房间人数。
- `getTop(K)`：返回最靠前的 K 位玩家。排序规则 = 房间号越大越靠前；同房间内进入时间
  越早越靠前。O(N + K)。

**标准设计**：每个房间一条按进入时间排序的双向链表 (DLL)，外加一个全局映射
`people: pid -> node` 做 O(1) 节点定位。`getTop` 从房间号最大的往回扫，按 DLL 顺序
采集节点，收够 K 个即返回。""",
    1071: """[Pinterest coding 2026-11] 二维网格上的光线传播模拟。灯塔朝某个方向发射光束，
光束按格子前进并与网格内容发生交互：

- `.`  空格子     — 方向不变继续前进
- `/`  镜子       — `(dr, dc) -> (-dc, -dr)`，如向右入射反射成向上
- `\\`  镜子       — `(dr, dc) -> ( dc,  dr)`，如向右入射反射成向下
- `|`  分束器     — 若光束水平，分成上 + 下两束；垂直入射则直穿
- `-`  分束器     — 若光束垂直，分成左 + 右两束；水平入射则直穿

在光束离开网格或重复访问到某个 `(格子, 方向)` 状态之前，统计被照亮的**不同格子**的
数量。

**常见追问**：
(a) 多个灯塔同时发射：取所有被照亮集合的并集。
(b) 最佳放置：枚举每个边界格子作为光源，报告最大照亮数（朴素 O(N*M*(N+M))；带
    循环感知 memoization 可到 O(N*M)）。
(c) 循环检测：由 `(格子, 方向)` 的 visited 集合天然保证终止。""",
    1072: """[Pinterest coding 2026-11] 给一个单词列表（通常已预排序）和一组查询前缀，对每个
前缀返回列表中**以该前缀开头的第一个单词**的下标；没有则返回 -1。

**例**：
```
words    = ['a', 'apple', 'appz', 'b']
prefixes = ['ap']
output   = [1]        # 'apple' 是第一个以 'ap' 开头的单词
```

**标准 follow-up**：
(a) 单词表固定、前缀大量：预处理一次 Trie，每次查询 O(|prefix|)。
(b) 单词未排序：排序 + 记录原下标，或者直接用 Trie。
(c) 返回所有匹配下标而非第一个：在 Trie 节点上挂下标列表。""",
    1073: """[Pinterest coding 2026-11] 实现 `my_round(s: str) -> int`，把字符串 `s` 表示的十进制
数按**四舍五入到最近整数**返回，**不准调用 `float(s)`**。`float()` 对极长输入
（如 400 位数字）会悄悄溢出，且二进制浮点带来的舍入假象（例如
`float('2.675')` 的 round-half-even 行为与十进制 half-up 不一致）必须避免。

**Half-up 规则**（负数向远离 0 方向舍入）：
```
'2.4'   -> 2
'2.5'   -> 3
'-2.5'  -> -3
'9.5'   -> 10          # 进位传播
'-.2'   -> 0           # 没有整数部分
'2.'    -> 2           # 没有小数部分
'  +3 ' -> 3           # 允许空白 + 显式正负号
```

**非法输入**（`""`, `"."`, `"1.2.3"`, `"abc"`) → `ValueError`。

**Follow-up (T-P1-403)**：推广到 "保留 p 位小数" 的精度舍入，复用同一套解析 + 进位
机制，只是把进位停止位从个位换到第 p 位。""",
    1074: """[Pinterest coding 2026-11, T-P1-402 的 follow-up] 实现
`round_by_precision(s: str, p: str) -> str`，把字符串 `s` 表示的十进制数
**四舍五入到 `p` 的最近倍数**，`p` 是以字符串形式给出的 10 的幂（如 `'100'`,
`'10'`, `'1'`, `'0.1'`, `'0.01'`）。返回同样是字符串。**不准 `float()`**（溢出 +
二进制表示伪像两个坑）。

**例**：
```
s='12567',    p='100'  -> '12600'
s='1234.678', p='0.1'  -> '1234.7'
s='1234.678', p='0.01' -> '1234.68'
s='99.5',     p='1'    -> '100'
s='-0.05',    p='0.1'  -> '-0.1'   # half away from zero
s='49',       p='100'  -> '0'
s='50',       p='100'  -> '100'
```

Half-up 规则（远离 0）。进位传播可能跨越小数点（例 `'9.99'` at `p='0.1'` →
`'10.0'`）。""",
    1075: """[Pinterest coding 2026-11] 某公司把资源（文件夹、文档、项目）组织为一个**有向无
环图 (DAG)**，边 `parent -> child` 代表 child 被 parent 包含 / 继承自 parent。管理
员可以把某用户的权限授予单个节点；该授权**自动传播到该节点的所有后代**。

设计 `PermissionSystem`：
- `addEdge(parent, child)`：搭建 DAG（保证无环）。
- `grant(user, node)`：给用户在 `node` 上授权（并自动对所有后代生效）。
- `hasAccess(user, node)`：当且仅当用户在 `node` **自身或任一祖先**上有授权时返回
  True。

**讨论过的 follow-up**：
(a) `revoke(user, node)`：传播如何与冲突授权交互。
(b) 多继承：一个节点可能有多个父亲（真 DAG，不是树）。
(c) 规模：百万级节点和授权、查询极度倾斜——什么时候做 memoization、什么时候
    预计算闭包。
(d) 组概念：`user -> group -> node` 形成两层 DAG。""",
    1076: """[Pinterest coding 2026-11] Pinterest 后端存一个异构关系图，节点包括 pin、board、
user。两节点间有边表示存在直接关系，例如：
- pin P 被保存到 board B         (pin-board 边)
- user U 关注 board B            (user-board 边)
- board B1 由 board B2 克隆      (board-board 边)

设计 `ConnectivityService`：
- `addEdge(a, b)`：记录一条新关系边（无向）。
- `areConnected(a, b)`：当且仅当 a 和 b 在关系图的**同一连通分量**中返回 True。

**讨论过的 follow-up**：
(a) `componentSize(x)` 与 `countComponents()` 摊还 O(1)。
(b) 允许删边：语义如何变？（Union-Find 单独不够用了。）
(c) a 到 b 的**最短跳数**，而不仅仅是连通性。
(d) 规模：数十亿条边流式进入；分片 worker；最终一致性。""",
}

BY_LC_ID: dict[int, str] = {
    1135: """有 `N` 座城市，编号 1 到 N。

给定 `connections`，其中每条 `connections[i] = [city1, city2, cost]` 表示连通
`city1` 和 `city2` 所需的花费，连接是**双向**的。

返回使得任意两座城市之间存在连通路径的**最小总花费**。若无法让所有城市两两连通，
返回 -1。

**例 1**：N = 3, connections = [[1,2,5],[1,3,6],[2,3,1]] → 6

**例 2**：N = 4, connections = [[1,2,3],[3,4,4]] → -1（图不连通）

**约束**：1 <= N <= 10000；1 <= connections.length <= 10000；0 <= cost <= 1e5。""",
    85: """给定一个只含 `'0'` 和 `'1'` 的二维字符矩阵，找出**全由 `'1'` 组成的最大矩形**并
返回其面积。

**例**：

```
输入:
[
  ["1","0","1","0","0"],
  ["1","0","1","1","1"],
  ["1","1","1","1","1"],
  ["1","0","0","1","0"]
]
输出: 6
```""",
    1570: """给定两个稀疏向量，计算它们的点积。

实现 `SparseVector` 类：
- `SparseVector(nums)`：用向量 `nums` 初始化对象。
- `dotProduct(vec)`：计算当前实例与 `vec` 的点积。

**稀疏向量**指绝大多数元素为 0 的向量；你应当**高效存储**稀疏向量并实现两个
`SparseVector` 之间的点积。

**Follow-up**：如果只有其中一个向量是稀疏的，又该怎么做？

**例 1**：
```
输入: nums1 = [1,0,0,2,3], nums2 = [0,3,0,4,0]
输出: 8
解释: v1.dotProduct(v2) = 1*0 + 0*3 + 0*0 + 2*4 + 3*0 = 8
```

**例 2**：
```
输入: nums1 = [0,1,0,0,0], nums2 = [0,0,0,0,2]
输出: 0
```

**例 3**：
```
输入: nums1 = [0,1,0,0,2,0,0], nums2 = [1,0,0,0,3,0,4]
输出: 6
```

**约束**：`n == nums1.length == nums2.length`；1 <= n <= 1e5；
0 <= nums1[i], nums2[i] <= 100。""",
    703: """设计一个类，求数据流中的**第 k 大**元素。注意：这里指排序后的第 k 大，不是第
k 个**不同**的值。

你的 `KthLargest` 类的构造函数接收整数 `k` 以及初始整数数组 `nums`（包含数据流
前几个元素）。每次调用 `KthLargest.add(val)`，返回当前数据流中第 k 大的元素。

**例**：
```
int k = 3;
int[] arr = [4,5,8,2];
KthLargest kthLargest = new KthLargest(3, arr);
kthLargest.add(3);   // 返回 4
kthLargest.add(5);   // 返回 5
kthLargest.add(10);  // 返回 5
kthLargest.add(9);   // 返回 8
kthLargest.add(4);   // 返回 8
```

**说明**：可以假设 `nums` 的长度 >= k - 1 且 k >= 1。""",
    973: """给定一个数组 `points`，其中 `points[i] = [xi, yi]` 表示 X-Y 平面上的一个点，以及
整数 `k`，返回离原点 `(0, 0)` 最近的 `k` 个点。

两点间距离使用**欧几里得距离**：`sqrt((x1-x2)^2 + (y1-y2)^2)`。

返回顺序不限；答案保证**唯一**（顺序除外）。

**例 1**：
```
输入: points = [[1,3],[-2,2]], k = 1
输出: [[-2,2]]
解释: (1,3) 到原点距离 sqrt(10)；(-2,2) 距离 sqrt(8) < sqrt(10)，所以 (-2,2) 更近。
```

**例 2**：
```
输入: points = [[3,3],[5,-1],[-2,4]], k = 2
输出: [[3,3],[-2,4]]     # [[-2,4],[3,3]] 同样接受
```

**约束**：1 <= k <= points.length <= 1e4；-1e4 <= xi, yi <= 1e4。""",
    378: """给定一个 n x n 矩阵，每**行**和每**列**均按升序排列，找出矩阵中**第 k 小**的
元素。

注意这里是排序后的第 k 小，不是第 k 个**不同**的值。

**例**：

```
matrix = [
  [ 1,  5,  9],
  [10, 11, 13],
  [12, 13, 15]
],
k = 8,
返回 13。
```

**说明**：可以假设 k 始终合法，1 <= k <= n^2。""",
}


def main() -> None:
    """Apply all Chinese translations; idempotent via marker."""
    updated = 0
    skipped = 0
    with sqlite3.connect(str(DB_PATH)) as conn:
        for internal_id, zh_desc in BY_INTERNAL_ID.items():
            row = conn.execute(
                "SELECT description FROM problems WHERE id = ?", (internal_id,)
            ).fetchone()
            if row is None or row[0] is None:
                print(f"[SKIP] id={internal_id} not found or no description")
                skipped += 1
                continue
            if MARKER in row[0]:
                skipped += 1
                continue
            new_desc = zh_desc.rstrip() + MARKER
            conn.execute(
                "UPDATE problems SET description = ?, "
                "description_source = ? WHERE id = ?",
                (new_desc, "zh-translation", internal_id),
            )
            updated += 1
        for lc_id, zh_desc in BY_LC_ID.items():
            row = conn.execute(
                "SELECT id, description FROM problems WHERE leetcode_id = ?",
                (lc_id,),
            ).fetchone()
            if row is None:
                print(f"[SKIP] lc={lc_id} not found")
                skipped += 1
                continue
            pid, existing = row
            if existing and MARKER in existing:
                skipped += 1
                continue
            new_desc = zh_desc.rstrip() + MARKER
            conn.execute(
                "UPDATE problems SET description = ?, "
                "description_source = ? WHERE id = ?",
                (new_desc, "zh-translation", pid),
            )
            updated += 1
        conn.commit()
    total = len(BY_INTERNAL_ID) + len(BY_LC_ID)
    print(f"[DONE] updated={updated} skipped={skipped} total={total}")


if __name__ == "__main__":
    main()
