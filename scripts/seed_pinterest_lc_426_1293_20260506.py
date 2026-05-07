"""Seed Pinterest add-ons LC 426 + LC 1293 (2026-05-06).

User Discord drops 2026-05-06:
- msg 1501481299339378778: LC 1293 with user-provided BFS-with-state solution.
- msg 1501487906064437319: LC 426, asked for best-practice solution from scratch.

Both problems already exist in `problems` (id=332 LC 426, id=451 LC 1293) from the
bulk LC import with descriptions but `notes=NULL` and no Pinterest tag. This seed:

  1. UPDATEs both rows in place: append "Pinterest" to company_tags (preserving
     existing [LinkedIn, Uber, Adobe]), fill `notes` with a Chinese 题解, set
     `family` / `pattern` / `source` / `tags` / `is_completed=1`.
  2. Appends rows 11 + 12 to the LC index doc (id=47) "扩展 & Follow-up 题"
     table with 来源 = "2026-05 user dump", and bumps the footer counter
     33 -> 35 + the refactored stamp.

Idempotent: re-running detects existing notes via sentinels, idempotently merges
Pinterest into company_tags, and skips the LC index update if the sentinel
substrings are present.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

LC_INDEX_DOC_ID = 47
PINTEREST = "Pinterest"

# ----- LC 426 -----
LC426_PROBLEM_ID = 332
LC426_NOTES_SENTINEL = "<!-- PINTEREST_LC426_NOTES_20260506 -->"
LC426_FAMILY = "tree-inorder-relink"
LC426_PATTERN = "BST in-order traversal + prev pointer relink"
LC426_TAGS = ["Tree", "DFS", "Linked List", "BST", "Pinterest"]
LC426_NOTES = LC426_NOTES_SENTINEL + """
## LC 426 Convert BST to Sorted Doubly Linked List (Pinterest 2026-05)

### 题目要点
- BST 中序遍历天然产出排序序列；只要在中序顺序里**就地**把 `left` 当 `prev`、`right` 当 `next` 重接，就得到双向链表。
- 题目要求 **circular**：遍历完成后把 `head.left = tail` 与 `tail.right = head` 闭环。
- in-place：不能新建 Node，只能复用原 BST 节点的两个指针。

### 推荐解法 1：递归中序 + `prev` 状态机（best practice）

抓住一个不变量：**在中序回调到达当前节点 `node` 的瞬间，`prev` 指向已串好链表的尾节点**。每次访问节点只做两件事：
1. `prev.right = node; node.left = prev`（把当前节点拼到尾部）
2. `prev = node`（推进尾指针）

第一次进入回调时 `prev` 是 None，说明 `node` 就是最左节点（也即整个链表的 head）。遍历结束后 `prev` 是最右节点（tail），最后闭环 `head.left = tail; tail.right = head`。

```python
class Solution:
    def treeToDoublyList(self, root):
        if not root:
            return None
        self.first = None  # head of the linked list
        self.last = None   # rolling tail (a.k.a. prev)

        def inorder(node):
            if not node:
                return
            inorder(node.left)
            if self.last:
                # link current node to the running tail
                self.last.right = node
                node.left = self.last
            else:
                # first node visited == leftmost == head
                self.first = node
            self.last = node
            inorder(node.right)

        inorder(root)
        # close the circle
        self.last.right = self.first
        self.first.left = self.last
        return self.first
```

- **Time**: `O(n)`，每个节点访问一次。
- **Space**: `O(h)` 递归栈，`h` 是树高；最坏退化成链 O(n)，平衡 BST O(log n)。

### 推荐解法 2：迭代中序 + 显式 stack（避免递归深度）

面试官追问"不许递归 / 担心 stack overflow"时切到这套：

```python
class Solution:
    def treeToDoublyList(self, root):
        if not root:
            return None
        stack, node = [], root
        first = last = None
        while stack or node:
            while node:
                stack.append(node)
                node = node.left
            node = stack.pop()  # 中序到达 node
            if last:
                last.right = node
                node.left = last
            else:
                first = node
            last = node
            node = node.right
        first.left = last
        last.right = first
        return first
```

复杂度同上：`O(n)` 时间，`O(h)` 空间（stack 取代递归栈，本质等价）。

### 易错点
1. **不闭环**：题目明说 circular，漏掉 `first.left = last; last.right = first` 是常见 0 分项。
2. **空树**：`if not root: return None` 必须前置；不要等 `inorder` 跑完才发现 `last is None` 时崩。
3. **写成"先收集列表再串"**：那不是 in-place，违反题意；用 `prev` 滚动指针是关键。
4. **递归方向写反**：必须 `inorder(left) -> 处理 node -> inorder(right)`，把"处理"放错位置就不再是 in-order。
5. **指针赋值顺序**：先 `last.right = node` 再 `node.left = last`，反过来也行；但 `self.last = node` 必须在两个 link 之后。

### 面试节奏
1. 先口头确认：BST？需要排序？需要 circular？双向？(节省时间，立刻问)
2. 给 in-order 性质 + `prev` 滚动指针不变量。
3. 写递归版；`first` / `last` 用类成员或 closure 都行（面试官有时会要求纯函数式：用一个 `dummy` head，让 `prev = dummy`，最后返回 `dummy.right`，闭环时拆掉 dummy。这是变体但 cleaner）。
4. 复杂度 `O(n) / O(h)`；追问 stack overflow 切迭代版。

### dummy-head 变体（更 cleaner）

```python
class Solution:
    def treeToDoublyList(self, root):
        if not root:
            return None
        dummy = TreeNode(0)
        prev = dummy

        def inorder(node, prev):
            if not node:
                return prev
            prev = inorder(node.left, prev)
            prev.right = node
            node.left = prev
            return inorder(node.right, node)

        last = inorder(root, prev)
        first = dummy.right
        first.left = last
        last.right = first
        return first
```

dummy 只是为了消去"第一次没有 prev"的特判；产线代码里更喜欢这种写法。

### 45 秒口播
> "BST 中序遍历产出排序序列，所以中序里维护一个滚动 `prev` 指针：每访问到 node 就 `prev.right = node, node.left = prev, prev = node`。第一个访问到的就是 head；中序结束后 prev 是 tail，最后闭环 `head.left = tail; tail.right = head` 完成 circular DLL。in-place 复用原节点，时间 O(n)，空间 O(h) 栈深。stack overflow 担忧切迭代版。"
"""

# ----- LC 1293 -----
LC1293_PROBLEM_ID = 451
LC1293_NOTES_SENTINEL = "<!-- PINTEREST_LC1293_NOTES_20260506 -->"
LC1293_FAMILY = "bfs-stateful"
LC1293_PATTERN = "BFS with state = (x, y, k_remaining)"
LC1293_TAGS = ["BFS", "Graph", "Grid", "State Search", "Pinterest"]
LC1293_NOTES = LC1293_NOTES_SENTINEL + """
## LC 1293 Shortest Path in a Grid with Obstacles Elimination (Pinterest 2026-05)

### 题目要点
- m × n 网格；0 是空格、1 是障碍。从 `(0,0)` 走到 `(m-1, n-1)`，可上下左右移动。
- 至多可以**消除 k 个障碍**穿过它们。求最短步数；若无法到达返回 -1。
- 关键观察：**剩余消除次数本身是状态的一部分**；以更多剩余 k 到达同一格的路径不应被"已访问 (x,y)"屏蔽——它在未来更有可能找到捷径。

### 解法：BFS with state = `(x, y, k_remaining)`

把状态空间扩展为 `m × n × (k+1)`。BFS 按层推进，每层 step+1。状态 `(x, y, k)` 只 visit 一次（同 k 重复入队是浪费）。终点判断可以放在 pop 时（标准 BFS）或 push 时（提前返回省一层）。

```python
from collections import deque
from typing import List

class Solution:
    def shortestPath(self, grid: List[List[int]], k: int) -> int:
        m, n = len(grid), len(grid[0])

        if m == 1 and n == 1:
            return 0  # 起点即终点

        visited = set()
        queue = deque()
        queue.append((0, 0, k))
        cost = 1  # 下一层走完是 cost 步

        while queue:
            for _ in range(len(queue)):  # 当前层一次性出尽
                x, y, k = queue.popleft()
                for nx, ny in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]:
                    if 0 <= nx < m and 0 <= ny < n:
                        # 终点 push 时立刻返回
                        if nx == m - 1 and ny == n - 1:
                            if grid[nx][ny] == 0 or k > 0:
                                return cost
                        # 空格：state = (nx, ny, k)
                        if grid[nx][ny] == 0 and (nx, ny, k) not in visited:
                            visited.add((nx, ny, k))
                            queue.append((nx, ny, k))
                        # 障碍 + 还能消：state = (nx, ny, k-1)
                        elif grid[nx][ny] == 1 and k - 1 >= 0 and (nx, ny, k - 1) not in visited:
                            visited.add((nx, ny, k - 1))
                            queue.append((nx, ny, k - 1))
            cost += 1

        return -1
```

### 复杂度
- **Time**: `O(m · n · k)` —— 状态数 m·n·(k+1)，每个状态出队一次，4 个邻居常数操作。
- **Space**: `O(m · n · k)` —— visited 集 + 队列。

### 关键不变量 + 易错点
1. **state = (x, y, k_remaining)** 必须包含 k；只用 (x,y) 会让"低剩余 k 的劣解"屏蔽"高剩余 k 的更优解"。
2. **层级 BFS 与 step 计数**：用 `for _ in range(len(queue))` 一次性把当前层 pop 完，外层 `cost += 1`。这是 BFS 求最短步数的标准模板；用 (x,y,k,steps) 元组也行但内存更费。
3. **起点 == 终点**：m==1 && n==1 提前返回 0，否则会被 cost=1 误算成 1。
4. **终点检测时机**：在邻居生成处检测（push 时返回 `cost`），而不是 pop 时再返回 `cost+1`——这样省一层，也跟用户代码里的 `cost` 含义匹配（cost 是"走到 (nx,ny) 的步数"）。
5. **障碍剪枝条件**：必须 `k - 1 >= 0` 才能消，且 `(nx, ny, k-1)` 不在 visited 才入队；用户代码两个条件都满足。
6. **k >= m+n-3 早返回**：最优路径长度上界是 `m+n-2`，去掉起点障碍后最多 `m+n-3` 个障碍。若 k 充足，曼哈顿距离 `m+n-2` 直接返回，省一大票 BFS。这是面试加分项：

```python
if k >= m + n - 3:
    return m + n - 2
```

### 解法对比

| 方法 | 复杂度 | 适用 |
|------|--------|------|
| 朴素 BFS (visited=(x,y,k)) | O(mnk) | 默认推荐 |
| A* with heuristic = manhattan | O(mnk log) | 大网格 + 紧 k；面试少考 |
| Dijkstra w/ priority queue | O(mnk log) | k 比较少时；同 BFS 但代码长 |
| DP on (x, y, k) | O(mnk) | 网格无环时合理；这题有环（往回走可能更短）→ BFS 更稳 |

### 面试节奏
1. 澄清：障碍消除是"穿过"还是"擦除"？(穿过——即可以通行那一步)；可以走回头路吗？(可以，所以 visited 必要)
2. 给 state = (x,y,k_remaining)；解释为何 k 必须入状态。
3. 写层级 BFS；终点 push 时返回。
4. 复杂度 O(mnk)；早返回 m+n-3 优化口头讲一下。
5. 追问 A* / 双向 BFS：knowledge check 即可，不必现场改代码。

### 45 秒口播
> "状态 = (x, y, k_remaining)，BFS 按层推进。每个 (x,y,k) 只 visit 一次；空格邻居以同 k 入队，障碍邻居 k>0 时以 k-1 入队。终点 push 时返回 cost。复杂度 O(mnk)，状态空间是 m*n*(k+1)。早返回 k >= m+n-3 时直接 m+n-2。state 必须带 k 是关键——只用 (x,y) 会让低剩余 k 的差解屏蔽高剩余 k 的好解。"
"""

# ----- LC index doc updates -----
LC_INDEX_OLD_FOOTER = "32 题全部 done"
LC_INDEX_NEW_FOOTER = "32 题 + 2026-05 新增 (1 screening + 2 LC) = 35 题全部 done"
LC_INDEX_OLD_FOOTER_V2 = "33 题全部 done"  # set by previous seed (Reverse Count and Say)
LC_INDEX_NEW_FOOTER_V2 = LC_INDEX_NEW_FOOTER

LC_INDEX_OLD_REFACTORED_PATTERNS = [
    "*Last refactored: 2026-04-15.*",
    "*Last refactored: 2026-05-06 (added Pinterest screening: Reverse Count and Say).*",
]
LC_INDEX_NEW_REFACTORED = (
    "*Last refactored: 2026-05-06 (added Pinterest screening: Reverse Count and Say "
    "+ LC 426 BST-to-DLL + LC 1293 obstacles-elimination BFS).*"
)

LC_INDEX_SENTINEL_426 = "[Convert Binary Search Tree to Sorted Doubly Linked List](lc://426)"
LC_INDEX_SENTINEL_1293 = "[Shortest Path in a Grid with Obstacles Elimination](lc://1293)"

# Anchor: last row of "扩展 & Follow-up 题" table is row 10 (LC 3229).
LC_INDEX_ANCHOR = (
    "| 10 | 3229 | [Min Ops to Make Array = Target](lc://3229) | Hard "
    "| Signed diff greedy | 1526 推广：diff 换号要重置累计；正负两段分开算 "
    "| 2025-11 dump |"
)
LC_INDEX_NEW_ROWS = (
    "\n| 11 | 426 | "
    "[Convert Binary Search Tree to Sorted Doubly Linked List](lc://426) | Med "
    "| BST 中序 + prev 滚动 "
    "| 中序天然排序；`prev.right = node, node.left = prev` 滚动重接；末尾闭环 "
    "`head.left = tail; tail.right = head`；O(n)/O(h) "
    "| 2026-05 user dump |"
    "\n| 12 | 1293 | "
    "[Shortest Path in a Grid with Obstacles Elimination](lc://1293) | Hard "
    "| 状态空间 BFS "
    "| state = (x,y,k_remaining)；层级 BFS push 时返回；k>=m+n-3 早返回 m+n-2；"
    "O(mnk) "
    "| 2026-05 user dump |"
)


def merge_company_tag(raw: str | None, company: str) -> tuple[str, bool]:
    """Add `company` to JSON tag list. Returns (new_json, changed)."""
    tags = json.loads(raw) if raw else []
    if company in tags:
        return raw or "[]", False
    tags.append(company)
    return json.dumps(tags, ensure_ascii=False), True


def upsert_problem_notes(
    conn: sqlite3.Connection, *,
    pid: int,
    notes: str,
    sentinel: str,
    family: str,
    pattern: str,
    tags: list[str],
    source_marker: str,
) -> None:
    """UPSERT the per-problem fields. Idempotent via sentinel detection."""
    row = conn.execute(
        "SELECT title, leetcode_id, company_tags, notes, source FROM problems WHERE id = ?",
        (pid,),
    ).fetchone()
    if row is None:
        raise SystemExit(f"[FAIL] problems.id={pid} not found")
    title, lc_id, raw_company_tags, existing_notes, existing_source = row

    new_tags_json, tags_changed = merge_company_tag(raw_company_tags, PINTEREST)
    skip_notes = bool(existing_notes) and sentinel in existing_notes

    fields, vals = [], []
    if not skip_notes:
        fields.append("notes = ?")
        vals.append(notes)
    if tags_changed:
        fields.append("company_tags = ?")
        vals.append(new_tags_json)

    # Always set family/pattern/source/is_completed/tags (cheap, makes idempotent rerun byte-stable)
    fields += ["family = ?", "pattern = ?", "tags = ?", "is_completed = 1"]
    vals += [family, pattern, json.dumps(tags, ensure_ascii=False)]

    # Append source marker without clobbering existing source
    if existing_source and source_marker not in existing_source:
        new_source = f"{existing_source};{source_marker}"
    elif not existing_source:
        new_source = source_marker
    else:
        new_source = existing_source
    fields.append("source = ?")
    vals.append(new_source)

    vals.append(pid)
    conn.execute(f"UPDATE problems SET {', '.join(fields)} WHERE id = ?", vals)
    note_status = "[SKIP notes]" if skip_notes else "[WRITE notes]"
    tag_status = "[ADDED Pinterest]" if tags_changed else "[Pinterest already tagged]"
    print(f"  problems.id={pid} (LC {lc_id}, '{title[:40]}'): {note_status} {tag_status}")


def update_lc_index(conn: sqlite3.Connection) -> None:
    """Append rows 11+12 to the extension table; update footer/refactored stamps."""
    row = conn.execute(
        "SELECT content FROM company_documents WHERE id = ?", (LC_INDEX_DOC_ID,)
    ).fetchone()
    if row is None:
        raise SystemExit(f"[FAIL] company_documents.id={LC_INDEX_DOC_ID} missing")
    content = row[0]

    if LC_INDEX_SENTINEL_426 in content and LC_INDEX_SENTINEL_1293 in content:
        print(f"  LC index doc id={LC_INDEX_DOC_ID}: [SKIP] both LC 426 and LC 1293 already present")
        return

    if LC_INDEX_ANCHOR not in content:
        raise SystemExit(
            "[FAIL] LC index extension-table anchor row 10 (LC 3229) not found"
        )
    content = content.replace(LC_INDEX_ANCHOR, LC_INDEX_ANCHOR + LC_INDEX_NEW_ROWS, 1)

    # Footer counter (handle both pre-/post- previous seed states)
    if LC_INDEX_OLD_FOOTER_V2 in content:
        content = content.replace(LC_INDEX_OLD_FOOTER_V2, LC_INDEX_NEW_FOOTER_V2, 1)
    elif LC_INDEX_OLD_FOOTER in content:
        content = content.replace(LC_INDEX_OLD_FOOTER, LC_INDEX_NEW_FOOTER, 1)

    # Refactored stamp
    for old in LC_INDEX_OLD_REFACTORED_PATTERNS:
        if old in content:
            content = content.replace(old, LC_INDEX_NEW_REFACTORED, 1)
            break

    conn.execute(
        "UPDATE company_documents SET content = ?, updated_at = CURRENT_TIMESTAMP "
        "WHERE id = ?",
        (content, LC_INDEX_DOC_ID),
    )
    print(f"  LC index doc id={LC_INDEX_DOC_ID}: [APPEND] rows 11+12 + footer/refactored bumped")


def seed() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    try:
        conn.execute("BEGIN")
        print("=== problems ===")
        upsert_problem_notes(
            conn, pid=LC426_PROBLEM_ID, notes=LC426_NOTES,
            sentinel=LC426_NOTES_SENTINEL, family=LC426_FAMILY,
            pattern=LC426_PATTERN, tags=LC426_TAGS,
            source_marker="pinterest_2026-05",
        )
        upsert_problem_notes(
            conn, pid=LC1293_PROBLEM_ID, notes=LC1293_NOTES,
            sentinel=LC1293_NOTES_SENTINEL, family=LC1293_FAMILY,
            pattern=LC1293_PATTERN, tags=LC1293_TAGS,
            source_marker="pinterest_2026-05",
        )
        print("\n=== LC index doc ===")
        update_lc_index(conn)
        conn.execute("COMMIT")

        print("\n=== verify ===")
        for pid in (LC426_PROBLEM_ID, LC1293_PROBLEM_ID):
            r = conn.execute(
                "SELECT id, leetcode_id, company_tags, length(notes), is_completed "
                "FROM problems WHERE id = ?", (pid,),
            ).fetchone()
            print(f"  {r}")
    finally:
        conn.close()
    print("[DONE]")


if __name__ == "__main__":
    seed()
