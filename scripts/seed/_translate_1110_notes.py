# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
"""One-shot: translate LC 1110 solution notes to Chinese."""
import sqlite3

NOTES = r'''## LC 1110 - Delete Nodes And Return Forest (DFS + "is_root" Flag)

> Pinterest must-do list. See [Pinterest Prep Notes](../docs/company/pinterest/recruiter_call_prep.md#pinterest-lc-%E5%BF%85%E5%88%B7%E9%A2%98%E5%88%97%E8%A1%A8-14-%E9%A2%98)

### 题目回顾

给一棵二叉树和一个 `to_delete` 值列表。删掉这些节点后，剩下的节点形成一个森林。返回森林中每棵树的根节点列表（每棵树只列一次，根的顺序无所谓）。

### 关键观察：谁会成为森林的根？

某个节点成为森林的根 **当且仅当**：
1. 它本身不在 `to_delete` 里，且
2. 它的父节点在 `to_delete` 里（或者它本来就是原树的根）。

所以 DFS 时要向下传一个 bit 的信息："我父亲是不是被删了？"（等价于 "我是不是一个潜在的 root？"）。这就是 `is_root` flag。

### 推荐写法

```python
class Solution:
    def delNodes(self, root: "TreeNode", to_delete: list[int]) -> list["TreeNode"]:
        to_delete = set(to_delete)
        forest = []

        def dfs(node: "TreeNode | None", is_root: bool) -> "TreeNode | None":
            if node is None:
                return None
            deleted = node.val in to_delete
            if is_root and not deleted:
                forest.append(node)
            # 子节点的 is_root = 当前节点是不是被删
            node.left = dfs(node.left, deleted)
            node.right = dfs(node.right, deleted)
            # 若当前节点被删，返回 None，让父亲自动 unlink
            return None if deleted else node

        dfs(root, True)
        return forest
```

**为什么这么写干净**：
- **一次遍历**，O(n) 时间，O(h) 空间（递归栈）。
- Unlink 由返回值处理：父亲写 `node.left = dfs(...)`，如果子节点被删就自动被置为 `None`。
- `is_root` flag 同时优雅地涵盖了 "原树根" 和 "父亲被删" 两种情况。

### Code Review（对你的写法）

你的 post-order 解法是**正确的**。逻辑拆解：
1. 先递归进子树。
2. 如果当前节点在 `to_delete` 里，把它没被删的孩子 append 到 `ret`。
3. 把被删的孩子 unlink（`root.left = None` / `root.right = None`）。
4. 最后再单独检查原树根。

**有点别扭的地方**：

| Issue | 你的代码 | 推荐写法 |
|-------|---------|---------|
| 原树根特判 | 遍历结束后 `if root.val not in to_delete: ret.append(root)` | 初始调用 `is_root=True` 统一处理 |
| 两轮扫孩子 | 先判删除并 append 到 `ret`，再单独 nullify | 用 return 值一次性 unlink |
| 重复 `in to_delete` 检查 | 每个节点 4+ 次（判孩子入 ret + 判孩子 nullify） | 每节点一次 |
| 变量名 `root` 遮蔽 | 在 `traverse(root)` 内 shadow 了外层 `root`，遍历后又用外层 `root` —— 能跑但容易看混 | 内部用 `node`，外层保留 `root` |

**你的代码是 O(n) 但常数更大**（多余的 set 查找和两阶段孩子处理）。功能上没问题，但风格上比必要的更啰嗦。

### "把状态往下传" vs "在回溯时处理"

这道题展示了一个通用的递归设计原则：

- 你的版本：所有事情都**在回溯时**做（post-order）。需要在事后回头推理每个节点的父亲状态（因此需要对原树根特判）。
- 推荐版本：把状态**向下传**（`is_root` 参数），把 unlink 信息**向上返回**。只要决策依赖祖先状态，大多数树 DFS 问题用这种方式都更清晰。

如果面试中题目涉及 "父亲约束"（例如 "统计父亲满足 X 的节点数"），第一反应就该是把一个 "父亲状态" 参数往下传，而不是试图回头去看。

### 陷阱 & 边界情况

1. **`to_delete` 是 list，要转成 set**：保证 O(1) 查找。你这点做对了。
2. **原树根本身可能被删**：你用末尾的 `if root.val not in to_delete` 单独处理；推荐版本通过 `is_root=True` 统一处理。
3. **空树 (`root is None`)**：推荐版本在最上面的 None 检查处理了；你的代码最后一行 `root.val` 会 crash。小 bug：顶上加一句 `if root is None: return []`。
4. **value 唯一**：题目保证（1 <= val <= 1000 且互不相同），所以按 value 匹配是安全的。如果 value 不唯一，就得按节点 identity 匹配。

### 复杂度

- **时间**：O(n + k)，n = 树大小，k = len(to_delete)。建 set 是 O(k)；遍历是 O(n)，每次查找 O(1)。
- **空间**：O(h + k)，h = 树高（递归栈）+ set。

### 面试时的模式识别

Cue："从树中删节点，返回森林/连通分量" -> DFS 带 `is_root` flag，返回 `None` 表示 unlink。

相关题目：
- LC 814 Binary Tree Pruning（同样的 "return None to unlink" 模式）
- LC 669 Trim a BST（同样的基于返回值的 unlink，BST-aware）
- LC 1325 Delete Leaves With a Given Value（post-order 删除）

### 总结

你的解法是对的，但推荐的 `dfs(node, is_root)` + return-based unlink 明显更干净：
- 一次遍历，无需对原树根特判
- 从递归里 return `None` 让父亲自动 unlink
- 每节点一次 membership 查询，而不是 2-4 次

把推荐写法存进肌肉记忆 —— `is_root`/`is_X` 这种 "flag 往下传" 的模式能推广到很多依赖祖先状态的树 DFS 问题。
'''


def main() -> None:
    conn = sqlite3.connect("data/mle_prep.db")
    cur = conn.cursor()
    cur.execute("UPDATE problems SET notes = ? WHERE leetcode_id = 1110", (NOTES,))
    conn.commit()
    row = cur.execute("SELECT length(notes) FROM problems WHERE leetcode_id = 1110").fetchone()
    print(f"Updated. notes length = {row[0]}")
    conn.close()


if __name__ == "__main__":
    main()
