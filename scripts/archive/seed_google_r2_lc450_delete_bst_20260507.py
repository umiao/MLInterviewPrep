"""Seed Google R2 Coding problem: LC 450 Delete Node in a BST.

User-provided solution (Discord 2026-05-07 msg 1501769443758575656). The
problems row already exists (id=506, leetcode_id=450) with title 'Delete
Node in a BST' but with notes=NULL, family/pattern=NULL, and company_tags
missing 'Google'. This seed UPDATES that row in place: adds Google to
company_tags, sets family=tree pattern=bst, and writes a tight Chinese
题解 distilled from the user's structural-relink solution.

Canonical key per CLAUDE.md: leetcode_id (LC-numbered problems).

Solution flavor: "structural relink" -- recursive search; on hit, if the
node has 0/1 child return the non-null subtree, else promote the right
subtree as the new root and hang the entire left subtree under the right
subtree's leftmost descendant. Avoids the canonical "copy successor's
value then delete successor" pattern; trades off slight tree-height
inflation for cleaner code (no value mutation).

The R2 Coding Index (doc 92) is updated separately by re-running
`scripts/seed_google_r2_coding_index_20260502.py`, extended in this
commit to add the new entry under a new `### BST / Tree Manipulation`
section.

Idempotent. Per Invariant 3 (CLAUDE.md), this seed is the sole sanctioned
write path for this row's drift fields.

Run: python scripts/seed_google_r2_lc450_delete_bst_20260507.py
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

LEETCODE_ID = 450
TITLE = "Delete Node in a BST"
URL = "https://leetcode.com/problems/delete-node-in-a-bst/"
SOURCE_LABEL = "Google R2 2026-05"

# Union with existing tags (LinkedIn, Uber, Adobe were set by an earlier seed
# pass); explicit list is the idempotent canonical state.
COMPANY_TAGS = ["LinkedIn", "Uber", "Adobe", "Google"]

NOTES = """\
## LC 450. Delete Node in a BST

给一棵 BST 和一个 key, 删除值为 key 的节点 (若存在), 返回删除后仍是合法 BST 的根。

### 思路

BST 删除分两步: **找** + **删**。

#### 第一步: 递归找到目标

利用 BST 性质 (left < root < right) 二分下钻, 路径上的所有点 **不修改**, 只把"下层处理结果"挂回去:

```python
if key < root.val:
    root.left = self.deleteNode(root.left, key)
    return root
elif key > root.val:
    root.right = self.deleteNode(root.right, key)
    return root
```

> **关键**: 把"删除"语义封装成"返回新子树根", 调用方只负责把返回值再挂回 `root.left/right`。这是 BST 各种修改题 (insert / delete / split) 的统一手法。

#### 第二步: 删 -- 三种 case

找到目标后, 按 children 数量分类:

**Case 1 / 2: 0 或 1 个 child**

直接把唯一存活的子树 (或 `None`) 顶替自己即可:

```python
if root.left is None or root.right is None:
    return root.left if root.left else root.right  # 自动覆盖 0 child 情形
```

**Case 3: 2 个 child -- 结构嫁接 (structural relink)**

不复制值, 直接重连指针: 让 right 子树升任新根, 把整个 left 子树挂在 right 子树**最左叶**的左侧 (那是 right 子树里最小且 < 原 root.val 的位置, 唯一空着的 left 指针):

```python
to_insert = root.right
while to_insert.left is not None:
    to_insert = to_insert.left
to_insert.left = root.left
return root.right
```

为什么 "right 子树最左叶" 一定有空的 `left`? 因为它是当前 right 子树里最小值, 没有更小的元素能挂在它的 left 上。把 left 子树整团挂上去, 仍满足 BST 性质 (left 子树所有值 < root.val < right 子树最左叶值)。

### 完整代码

```python
class Solution:
    def deleteNode(self, root: Optional[TreeNode], key: int) -> Optional[TreeNode]:
        if root is None:
            return None
        if key < root.val:
            root.left = self.deleteNode(root.left, key)
            return root
        if key > root.val:
            root.right = self.deleteNode(root.right, key)
            return root
        # 命中
        if root.left is None or root.right is None:
            return root.left if root.left else root.right
        # 两子俱全: 把 left 整团挂到 right 最左叶下面, 返回 right
        to_insert = root.right
        while to_insert.left is not None:
            to_insert = to_insert.left
        to_insert.left = root.left
        return root.right
```

### 复杂度

- 时间: $O(h)$, $h$ 为树高。最坏退化链表 $h = N$, 平衡时 $h = \\log N$
- 空间: $O(h)$ 递归栈

### 两种主流写法对比

| 维度 | 结构嫁接 (本题解) | Successor-Copy (经典写法) |
|------|------------------|--------------------------|
| 写法 | 直接 relink 指针 | 找 in-order successor, 复制其 val 到当前节点, 然后递归删 successor |
| 代码量 | 短 | 略长 (要走两次递归) |
| 是否改值 | 否 | 是 (修改 `root.val`) |
| 树高影响 | 可能略增 (left 整团下挂) | 不变 (只换值) |
| 节点身份 | 保留原 right 子树节点 | 保留原 root 节点 (但值变了) |

如果有外部引用持有节点指针 (例如另一个数据结构 cache 了节点对象), 经典写法会让原 root 的 val 突变, 嫁接法不会; 反过来如果在意平均树高, 经典写法更稳。

### 易错点 / Checklist

- [ ] `if root is None: return None` -- key 不存在时返回原树, 别忘
- [ ] 递归时一定要 `root.left = self.deleteNode(...)` 把返回值挂回去, 否则修改不生效
- [ ] 0/1 child 用 `root.left if root.left else root.right` 一行覆盖三种子情形 (左空 / 右空 / 双空)
- [ ] 嫁接法 `to_insert.left` 一定为 `None` (right 子树最左叶), 才能直接赋值不丢节点
- [ ] 不要用 `if root.left and root.right` 单独处理两子情形写出嵌套 -- 用上面的"短路 0/1 child + 余下两子"两段式更清爽
- [ ] BST 性质只用一次: 仅在"找"阶段二分下钻; "删"阶段按子树结构, 不再比较 val

### 一句话总结

BST 删除 = **递归找**(BST 性质二分) + **三 case 删**(0/1 child 直顶替, 2 child 把 left 子树挂到 right 最左叶下方); 把"删除"封装成"返回新子树根", 调用方挂回去就完事。
"""


PROBLEM_SPEC: dict = {
    "leetcode_id": LEETCODE_ID,
    "title": TITLE,
    "url": URL,
    "difficulty": "medium",
    "tags": ["tree", "bst", "recursion", "in-order-successor"],
    "pattern": "bst",
    "family": "tree",
    "category": None,
    "source": SOURCE_LABEL,
    "company_tags": COMPANY_TAGS,
    "is_completed": 1,
    "notes": NOTES,
}


def _select_existing_by_lc(
    conn: sqlite3.Connection, leetcode_id: int
) -> tuple[int, dict] | None:
    """Return (id, current_row) for the row matching leetcode_id, else None."""
    row = conn.execute(
        "SELECT id, leetcode_id, title, url, difficulty, tags, pattern, family, "
        "       category, source, company_tags, is_completed, notes "
        "FROM problems WHERE leetcode_id = ?",
        (leetcode_id,),
    ).fetchone()
    if row is None:
        return None
    keys = [
        "id", "leetcode_id", "title", "url", "difficulty", "tags", "pattern",
        "family", "category", "source", "company_tags", "is_completed", "notes",
    ]
    return int(row[0]), dict(zip(keys, row, strict=True))


def _normalize(spec: dict) -> dict:
    """Normalize spec into the comparable storage form (lists -> JSON strings)."""
    out = dict(spec)
    out["tags"] = json.dumps(spec["tags"], ensure_ascii=False)
    out["company_tags"] = json.dumps(spec["company_tags"], ensure_ascii=False)
    return out


def upsert_problem(conn: sqlite3.Connection, spec: dict) -> tuple[int, str]:
    """INSERT-or-UPDATE the problem row by leetcode_id. Return (id, action)."""
    norm = _normalize(spec)
    existing = _select_existing_by_lc(conn, spec["leetcode_id"])

    if existing is None:
        cur = conn.execute(
            "INSERT INTO problems "
            "(leetcode_id, title, url, difficulty, tags, pattern, family, "
            " category, source, company_tags, is_completed, notes, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
            "        CURRENT_TIMESTAMP)",
            (
                norm["leetcode_id"], spec["title"], norm["url"],
                norm["difficulty"], norm["tags"], norm["pattern"],
                norm["family"], norm["category"], norm["source"],
                norm["company_tags"], norm["is_completed"], norm["notes"],
            ),
        )
        return int(cur.lastrowid), "INSERTED"

    pid, current = existing
    fields_to_check = [
        "title", "url", "difficulty", "tags", "pattern", "family",
        "category", "source", "company_tags", "is_completed", "notes",
    ]
    drift = {
        f: norm[f] for f in fields_to_check if current.get(f) != norm[f]
    }
    if not drift:
        return pid, "UNCHANGED"

    set_clauses = ", ".join(f"{f} = ?" for f in drift)
    values = list(drift.values())
    values.append(pid)
    conn.execute(
        f"UPDATE problems SET {set_clauses} WHERE id = ?",
        values,
    )
    return pid, "UPDATED"


def main() -> int:
    """Insert-or-update LC 450. Return 0 on success."""
    if not DB_PATH.exists():
        print(f"[FAIL] db missing at {DB_PATH}", file=sys.stderr)
        return 1

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.with_suffix(f".db.bak.{ts}_pre_lc450_delete_bst")
    shutil.copy2(DB_PATH, backup_path)
    print(f"[BACKUP] {backup_path.name}")

    with sqlite3.connect(str(DB_PATH)) as conn:
        pid, action = upsert_problem(conn, PROBLEM_SPEC)
        print(f"[{action}] problem id={pid} leetcode_id={LEETCODE_ID} title={TITLE!r}")
        conn.commit()

    print("[OK] done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
