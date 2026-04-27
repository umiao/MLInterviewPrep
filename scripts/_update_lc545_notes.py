"""Idempotent: write LC 545 notes (Boundary of Binary Tree) — one-pass
flag-classified DFS with deque appendleft for the right boundary.

Run: python scripts/_update_lc545_notes.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
LC_ID = 545
PATTERN = "tree_boundary_dfs"
FAMILY = "tree_traversal"
SENTINEL = "<!-- LC545_NOTES_V1 -->"

NOTES = """<!-- LC545_NOTES_V1 -->
## 题目定位
LC 545 Boundary of Binary Tree —— **二叉树边界遍历**。逆时针返回边界节点：
**根 → 左边界（不含叶子）→ 全体叶子（左到右）→ 右边界（不含叶子，倒序）**。
难点不是写遍历，**难在精确定义"什么算左/右边界"**：
- 左边界：从根**沿左子节点优先**走下去的路径；如果某个节点没有左孩子，
  它的右孩子才"接替"成为左边界（**只剩一个孩子时单孩子接替**）。右边界对称。
- 叶子：左右子树都为空的节点（根节点是叶子的退化情况单独处理）。

## 思路（一遍 DFS + flag 分类）
关键技巧：**给每个节点一个 4 状态 flag**——`ROOT / LEFT / RIGHT / INNER`，
flag 沿着 DFS 向下传播；遇到节点时只看自己的 flag 决定丢进哪个桶。

### Flag 继承规则（最容易写错）
| 父 flag | 子位置 | 子 flag |
| --- | --- | --- |
| `ROOT` | 左子 | `LEFT` |
| `ROOT` | 右子 | `RIGHT` |
| `LEFT` | 左子 | `LEFT` |
| `LEFT` | 右子 | `LEFT` *if* 父无左子 *else* `INNER` |
| `RIGHT` | 左子 | `RIGHT` *if* 父无右子 *else* `INNER` |
| `RIGHT` | 右子 | `RIGHT` |
| `INNER` | 任意 | `INNER` |

> **"单孩子接替"规则**：左边界节点 N 如果只有右孩子（没左孩子），那么右孩子
> 继承 LEFT 身份——因为它仍然是"沿最外层左侧轮廓往下"的一部分。RIGHT 对称。

### Bucket 规则
- `flag == ROOT` 或 `LEFT`：**append 到 left_b**（前序自然顺序：根→左→…）
- `flag == RIGHT`：**appendleft 到 right_b**（前序入桶但要求倒序输出，
  deque 头插 $O(1)$，比扫完再 reverse 更优雅）
- `flag == INNER` 且是**叶子**：append 到 leaves
- 其它：跳过（INNER 非叶子节点不在边界上）

## 核心代码
```python
from collections import deque

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    ROOT, LEFT, RIGHT, INNER = 0, 1, 2, 3

    def boundaryOfBinaryTree(self, root):
        left_b, leaves = [], []
        right_b = deque()                # O(1) 头插

        def left_child_flag(cur, flag):
            if flag in (self.ROOT, self.LEFT):
                return self.LEFT
            if flag == self.RIGHT and cur.right is None:
                return self.RIGHT       # 单孩子接替
            return self.INNER

        def right_child_flag(cur, flag):
            if flag in (self.ROOT, self.RIGHT):
                return self.RIGHT
            if flag == self.LEFT and cur.left is None:
                return self.LEFT        # 单孩子接替
            return self.INNER

        def preorder(cur, flag):
            if cur is None:
                return
            if flag == self.RIGHT:
                right_b.appendleft(cur.val)
            elif flag in (self.ROOT, self.LEFT):
                left_b.append(cur.val)
            elif cur.left is None and cur.right is None:
                leaves.append(cur.val)
            preorder(cur.left, left_child_flag(cur, flag))
            preorder(cur.right, right_child_flag(cur, flag))

        preorder(root, self.ROOT)
        return left_b + leaves + list(right_b)
```

### 走查
树:
```
            1
           / \\
          2   3
         / \\   \\
        4   5   6
           / \\ / \\
          7  8 9 10
```
预期边界：`[1, 2, 4, 7, 8, 9, 10, 6, 3]`。

| 节点 | 父 flag | 自身 flag | 入桶 |
| --- | --- | --- | --- |
| 1 | — | ROOT | left_b: [1] |
| 2 | ROOT | LEFT | left_b: [1, 2] |
| 4 | LEFT | LEFT（父 2 有左孩子，左继续走左） | left_b: [1, 2, 4] |
| 4 是叶子，但 flag=LEFT 已入 left_b（**不重复入 leaves**） |
| 5 | LEFT | INNER（父 2 有左子，5 是右子，flag 转 INNER） | INNER+叶子 ✗（5 非叶）→ skip |
| 7 | INNER | INNER；叶子 → leaves: [7] |
| 8 | INNER | INNER；叶子 → leaves: [7, 8] |
| 3 | ROOT | RIGHT | right_b 头插: [3] |
| 6 | RIGHT | RIGHT（父 3 无左子但右子是 6, 6 是 3 的右子→RIGHT） | right_b 头插: [6, 3] |
| 9 | RIGHT | INNER（父 6 有左子？没有，6 只有右子；9 是 6 的左子→**RIGHT 继承**？等等） |

修正第 9 行走查：节点 6 的 flag 是 RIGHT。看 9（6 的左子）：
`right_child_flag` 检查父=RIGHT，但 9 是父的**左子**，走的是 `left_child_flag`。
`left_child_flag(cur=6, flag=RIGHT)`：父 6 的右子是 10（不为 None）→ 不进入"单孩子接替"分支 → 返回 INNER。
所以 9 的 flag = INNER，是叶子 → leaves: [7, 8, 9]。

| 节点 | 父 flag | 自身 flag | 入桶 |
| --- | --- | --- | --- |
| 9 | RIGHT (父=6) | INNER（6 有右子 10，9 是左子→INNER）；叶子 → leaves: [7, 8, 9] |
| 10 | RIGHT (父=6) | RIGHT；叶子但 flag=RIGHT 已入 right_b（**不重复**）→ right_b: [10, 6, 3] |

最终：`left_b + leaves + right_b` = `[1, 2, 4] + [7, 8, 9] + [10, 6, 3]` =
`[1, 2, 4, 7, 8, 9, 10, 6, 3]` ✓

## 关键技巧 / 易错点

### [PITFALL] 1. 叶子节点不重复入 leaves
代码用 `elif` 链确保互斥：
```python
if flag == RIGHT:
    right_b.appendleft(cur.val)
elif flag in (ROOT, LEFT):
    left_b.append(cur.val)
elif cur.left is None and cur.right is None:    # 仅 INNER 叶子才进
    leaves.append(cur.val)
```
**写成独立 `if` 会让左边界叶子（如上例 4）同时进 left_b 和 leaves**，输出
重复元素。

### [PITFALL] 2. 单根树 / 根即叶子的退化情况
`root = [1]`：`preorder(root, ROOT)` 把 1 放进 `left_b`，递归 None 子树
直接返回。最终 `left_b + leaves + list(right_b)` = `[1] + [] + []` = `[1]`。
但**LC 题目要求根本身不能与左/右/叶子重复，所以单根答案就是 `[1]` 而不是
`[1, 1]`**——本算法天然处理。

### [PITFALL] 3. 右边界倒序：用 deque appendleft，不要先 append 再 reverse
两种都对，但 deque appendleft 是 $O(1)$，**循环里没有额外开销**；先 list
append 再 reverse 是 $O(P)$ 一次性反转——同 $O(P)$ 但需要遍历完才能反转，
**不能流式处理**。讲解时强调 deque 的常数优化是加分项。

### 其它易错点
4. **"单孩子接替"忘了对称写两次**：必须在 `left_child_flag` 和
   `right_child_flag` 各写一份。漏一边会让形如"左子树只有右孩子链"的树
   边界缺失。
5. **flag 用字符串而非 enum/常量**：string compare 慢且易拼错。本代码用
   类常量 `ROOT, LEFT, RIGHT, INNER = 0, 1, 2, 3`。Python 3.4+ 也可以
   用 `enum.IntEnum`，但常量更轻。
6. **递归栈深 = 树高**：偏斜树 O(n)，会触发 Python 默认 1000 递归深限。
   面试规模通常不到，但生产代码要 `sys.setrecursionlimit` 或改迭代版。
7. **空树 `root is None`**：`preorder` 一开始就 return，三个桶全空，返回
   `[]`。OK。
8. **flag 数据流是值传递，不是状态机**：DFS 调用栈各自持有自己的 flag
   副本，回溯天然正确——不需要"恢复 flag" 这种 backtracking 写法。

## 复杂度
- 时间：$O(n)$，每个节点常数次访问。
- 空间：$O(n)$ 三个桶 + $O(h)$ 递归栈，$h$ = 树高。

## 题目家族（树遍历 + flag-state DFS）
- **LC 199** Binary Tree Right Side View：右边界的简化版（每层最右节点），
  本题 right_b 思路的退化情形。
- **LC 257** Binary Tree Paths：根到所有叶子的路径，DFS 携带"当前路径"
  状态——和本题"携带 flag"是同款 DFS-with-state 模板。
- **LC 124** Binary Tree Maximum Path Sum：DFS 返回值携带"以当前为终点
  的最大单链和"，state-passing 的更复杂版。
- **LC 543** Diameter of Binary Tree：同款"DFS 既计算答案又返回向上的
  partial state"。
- **LC 1430** Check If a String is a Valid Sequence from Root to Leaves：
  DFS 携带"当前匹配位置"作为 state，一旦 mismatch 直接剪枝——和 LC 545
  的 INNER flag 剪枝精神一致。
- **LC 314 / 987** Binary Tree Vertical Order Traversal：另一种"按位置
  分桶"的树遍历，同样是 traversal + bucket-collect 套路。

**面试 30 秒 pitch**：
> "一遍 DFS 给每个节点四态 flag（ROOT/LEFT/RIGHT/INNER），flag 沿着递归向
> 下传播：左子优先继承左边界、右子优先继承右边界，**单孩子时由仅有的孩子
> 接替**。三个桶——LEFT 直接 append，RIGHT 用 deque appendleft 保持倒序，
> INNER 且是叶子才 append leaves。最后拼起来。$O(n)$ 时间 $O(n)$ 空间。"

## Follow-up
1. **N 叉树版本**：把"左/右子"概念推广为"最左/最右子"——递归时取 `children[0]`
   和 `children[-1]`，中间孩子全部走 INNER。flag 规则不变。
2. **去重**：如果题目改成"边界节点集合"（不要顺序），用 `set` 收集即可，
   但 LC 545 要求顺序，本算法的顺序天然正确。
3. **Morris 遍历**：理论上可以 $O(1)$ 空间，但**flag 需要传播**让 Morris
   实现极其复杂——面试不要尝试，工程上不值得。
"""


def main() -> None:
    """Rewrite LC 545 notes; idempotent via sentinel."""
    with sqlite3.connect(str(DB_PATH)) as conn:
        row = conn.execute(
            "SELECT id, notes, is_completed, family, pattern "
            "FROM problems WHERE leetcode_id = ?",
            (LC_ID,),
        ).fetchone()
        if row is None:
            raise SystemExit(f"LC {LC_ID} not in problems table")
        pid, existing_notes, _done, fam, pat = row

        if existing_notes and SENTINEL in existing_notes:
            print(f"[UNCHANGED] LC {LC_ID} id={pid} notes (sentinel present)")
            return

        fields: dict[str, str | int] = {
            "notes": NOTES,
            "is_completed": 1,
        }
        if not pat:
            fields["pattern"] = PATTERN
        if not fam:
            fields["family"] = FAMILY
        sets = ", ".join(f"{k} = ?" for k in fields)
        conn.execute(
            f"UPDATE problems SET {sets} WHERE id = ?",
            (*fields.values(), pid),
        )
        conn.commit()
        print(
            f"[UPDATED] LC {LC_ID} id={pid} "
            f"notes_len={len(NOTES)} fields={list(fields)}"
        )


if __name__ == "__main__":
    main()
