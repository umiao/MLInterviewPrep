"""Seed Google R2 custom problem: 文件系统总大小计算.

User-provided 题解 (Discord 2026-05-07 msg 1501825987753672826,
inline ~2.5KB). Custom Google R2 problem testing tree/graph DFS plus
clarification skill: given a filesystem tree where files have a size
and directories' size = sum of children, return the total size.

The interview-realism move is the **opening clarification trio** --
strict tree vs symlinked graph? single vs repeated query? depth bound
(stack overflow risk)? -- which gates the 4-level solution evolution.

Solutions preserved verbatim:

  Level 1: cycle-detection DFS for graphs with symlinks. visited set
           guards against revisits. O(V+E) / O(V).
  Level 2: strict-tree recursion. O(N) / O(H).
  Level 3: memoization for repeated queries. Better: a one-shot
           postorder pass that fills a `total_size` field on every
           node, making subsequent queries O(1) without hashing.
  Level 4: iterative postorder via color-marking
           (`(node, processed)` tuples) to dodge stack overflow on
           deep trees.

Custom problem -- no leetcode_id, canonical key=title='文件系统总大小计算'.
family=tree, pattern=postorder-dfs, source='Google R2 2026-05',
company_tags=[Google]. tags include tree, dfs, postorder, memoization,
iterative, cycle-detection.

Per `feedback_pinterest_two_tier_notes`: per-problem note in
`problems.notes`, ProblemDrawer renders via `db://<id>`. Doc 92 R2
Coding Index extended via `seed_google_r2_coding_index_20260502.py` to
add a NEW `### Tree / Traversal` section between
`### Tree / Graph Validation` and `### BST / Tree Manipulation`.

Idempotent. Title is the canonical key. First run on missing row:
1 INSERT. Re-run on identical state: 0 writes (UNCHANGED).

Run: python scripts/seed_google_r2_filesystem_total_size_20260507.py
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

TITLE = "文件系统总大小计算"
SOURCE_LABEL = "Google R2 2026-05"
COMPANY_TAGS = ["Google"]

NOTES = """\
## 文件系统总大小计算

### 题面

给定一个文件系统的根节点, 每个节点是文件或目录:

- 文件有自己的 `size`
- 目录的 `size = 所有子节点 size 之和`

求整个文件系统的总大小。

```python
class Node:
    name: str
    size: int          # 文件的大小; 目录为 0
    children: List[Node]  # 文件为空
```

---

### 澄清问题 (开场必问)

1. **是 strict tree 还是可能有 link 形成 graph?** -- 决定要不要 cycle detection。
2. **是单次查询还是多次查询?** -- 决定要不要 cache / 预填字段。
3. **树深度可能多大?** -- 决定要不要迭代化 (Python 默认 recursion limit ~1000)。

这三连决定四档解法; 不问就埋雷。

---

### Level 1: 通用 DFS (含 cycle detection)

应对可能存在 symbolic link 的图结构。`visited` 用 set, 节点复用 id 防 hash 冲突。

```python
def total_size(root):
    visited = set()
    def dfs(node):
        if node in visited:
            return 0
        visited.add(node)
        return node.size + sum(dfs(c) for c in node.children)
    return dfs(root)
```

- 时间 $O(V + E)$
- 空间 $O(V)$ -- visited + 递归栈

### Level 2: Strict Tree 递归

确认无环后简化, 不需要 visited。

```python
def total_size(root):
    return root.size + sum(total_size(c) for c in root.children)
```

- 时间 $O(N)$
- 空间 $O(H)$ -- H 是树高

### Level 3: 加 Cache (应对多次查询)

```python
cache = {}
def total_size(node):
    if node in cache:
        return cache[node]
    result = node.size + sum(total_size(c) for c in node.children)
    cache[node] = result
    return result
```

**更优做法**: 一次后序遍历预填所有节点的 `total_size` 字段, 后续查询 O(1) 无 hash 开销。这才是面试官想听到的"优化查找"答案。

### Level 4: 迭代后序 (防爆栈)

颜色标记法 -- `(node, processed)` 二元组, 第一次入栈是 "to-visit", 第二次是 "process"。

```python
def total_size(root):
    stack = [(root, False)]
    size_map = {}
    while stack:
        node, processed = stack.pop()
        if processed:
            size_map[node] = node.size + sum(
                size_map[c] for c in node.children
            )
        else:
            stack.append((node, True))
            for c in node.children:
                stack.append((c, False))
    return size_map[root]
```

后序保证: 子节点都 processed 完, 父节点才 process -- 这是"目录 size = 子节点之和"的硬约束。

---

### 考点 & 难点速记

| 考点 | 关键点 |
|---|---|
| 建模 | 文件系统 -> 树 / 图 |
| 遍历 | 后序 DFS (先子后父) |
| 边界 | link 成环、深度爆栈 |
| 澄清能力 | 开场问清 tree/graph、查询频次、深度 |
| 优化路径 | DFS -> cache -> 预填字段 -> 迭代 |

---

### 易错 / 边界

- **Strict tree 单次查询下, cache 不省时间** -- 每个节点本来就只访问一次, hash 反而是常数 overhead。cache 只在**多次查询**或**DAG/图**下才有意义。
- **"Cache 优化查找"的最优答案是直接挂 size 字段到节点上**, 省掉哈希开销。这是 Level 3 的 punchline。
- **迭代化解决的是栈溢出问题, 不是时间复杂度问题** -- 别把这两个目的搞混。
- **visited 用 id(node) 还是 node 对象本身?** Python 里只要 Node 没自定义 `__hash__`, 默认按 id 比较是 OK 的; 跨进程序列化 / 节点会被复制时改用 `id(node)` 更稳。
- **目录 size 是否预存?** 题面说"目录为 0"暗示**没预填**, 必须自己求和; 如果题面说"目录 size 已经是子树和", 那直接 `root.size` 就行 -- 先问清楚再写。

### 复盘 Takeaway

**优化要分清是为"时间"、"空间"还是"健壮性"** -- 三者优化手段完全不同:

- 时间优化: cache / 预填字段 (重复查询)
- 空间优化: 迭代 (栈空间) / 流式 (边读边算)
- 健壮性: cycle detection (图) / 迭代 (深度)

面试现场先问清场景, 再给对应档位的方案 -- 别上来就最复杂的, 也别只给最简单的。

### 一句话总结

文件系统总大小 = **后序 DFS 模板题 + 澄清三连**。Level 1-4 演进对应 (graph 风险) -> (单次查询) -> (多次查询) -> (深度风险), 真正考的是**先问后答**的工程素养, 不是算法。
"""


PROBLEM_SPEC: dict = {
    "leetcode_id": None,
    "title": TITLE,
    "url": None,
    "difficulty": "medium",
    "tags": [
        "tree", "dfs", "postorder", "recursion", "iterative",
        "memoization", "cycle-detection",
    ],
    "pattern": "postorder-dfs",
    "family": "tree",
    "category": None,
    "source": SOURCE_LABEL,
    "company_tags": COMPANY_TAGS,
    "is_completed": 1,
    "notes": NOTES,
}


def _select_existing_by_title(
    conn: sqlite3.Connection, title: str
) -> tuple[int, dict] | None:
    """Return (id, current_row) for the row matching title, else None."""
    row = conn.execute(
        "SELECT id, leetcode_id, title, url, difficulty, tags, pattern, family, "
        "       category, source, company_tags, is_completed, notes "
        "FROM problems WHERE title = ?",
        (title,),
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


def _merge_company_tags(current_json: str | None, target_list: list[str]) -> str:
    """Union target into existing JSON-encoded company_tags list, preserving order."""
    cur = json.loads(current_json) if current_json else []
    for tag in target_list:
        if tag not in cur:
            cur.append(tag)
    return json.dumps(cur, ensure_ascii=False)


def upsert_problem(conn: sqlite3.Connection, spec: dict) -> tuple[int, str]:
    """INSERT-or-UPDATE the problem row by title (custom problem). Return (id, action)."""
    norm = _normalize(spec)
    existing = _select_existing_by_title(conn, spec["title"])

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
    merged_company_tags = _merge_company_tags(
        current.get("company_tags"), spec["company_tags"]
    )
    fields_to_check = [
        "leetcode_id", "url", "difficulty", "tags", "pattern", "family",
        "category", "source", "is_completed", "notes",
    ]
    drift = {
        f: norm[f] for f in fields_to_check if current.get(f) != norm[f]
    }
    if current.get("company_tags") != merged_company_tags:
        drift["company_tags"] = merged_company_tags

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
    """Insert-or-update 文件系统总大小计算. Return 0 on success."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if not DB_PATH.exists():
        print(f"[FAIL] db missing at {DB_PATH}", file=sys.stderr)
        return 1

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.with_suffix(f".db.bak.{ts}_pre_filesystem_total_size")
    shutil.copy2(DB_PATH, backup_path)
    print(f"[BACKUP] {backup_path.name}")

    with sqlite3.connect(str(DB_PATH)) as conn:
        pid, action = upsert_problem(conn, PROBLEM_SPEC)
        print(f"[{action}] problem id={pid} title={TITLE!r}")
        conn.commit()

    print("[OK] done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
