"""Seed Google R2 Coding methodology note: K-th Largest Collection 方法论.

User-provided content (Discord 2026-05-05). Methodology / decision-tree note
for the 'support insert(x) + kLargest() at any time' interview class. Goes
strictly broader than LC 703 'Kth Largest Element in a Stream' (existing
problems.id=587), which only covers the fixed-k size-k-min-heap case --
this note adds k-varies (Order Statistic Tree / SortedList), bounded-range
bucket, and Followup directions (delete, streaming, distributed, multi-k).

Per `feedback_pinterest_two_tier_notes`: per-problem (here: per-class) note
lives in `problems.notes` so ProblemDrawer renders it via `db://<id>`. Title
suffix `方法论` distinguishes it from concrete LC entries; pattern
`heap-vs-bst-vs-bucket` captures the three-way decision the note teaches.

The R2 Coding Index doc 92 is updated separately by re-running
`scripts/seed_google_r2_coding_index_20260502.py`, which is extended in
the same commit to add a `### Design / Data Structure / 方法论` section
referencing this row by title.

Idempotent. Title is canonical key. Per Invariant 3 (CLAUDE.md), this
seed is the sole sanctioned write path for this row.

Run: python scripts/seed_google_r2_kth_largest_collection_20260505.py
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

SOURCE_LABEL = "Google R2 2026-05"
COMPANY_TAGS = ["Google"]

TITLE = "K-th Largest Collection 方法论"

DESCRIPTION = """\
设计一个数据结构, 支持:

- `insert(x)`: 插入一个数
- `kLargest()`: 返回当前集合的第 $k$ 大

讨论 $k$ 是否固定、insert vs query 频率、$n$ 规模、数值范围、是否支持删除等
约束如何决定数据结构选型。本笔记是面对一类 "K-th 设计题" 的方法论决策树, 不
绑定具体 LeetCode 编号; 与 LC 703 (Kth Largest in Stream, $k$ 固定) 互补,
后者是其中一格 (size-k 最小堆) 的具体落地。

来源: Google R2 Coding 2026-05 用户 Discord 2026-05-05 提供。
"""

NOTES = """\
## K-th Largest Collection 方法论

### 澄清（决定数据结构的关键）

- **$k$ 是否固定**：分水岭，决定能否用 size-$k$ heap
- **insert vs query 频率**：决定优化哪一端
- **$n$ 规模、数值范围**：有界整数可上桶
- **是否支持删除、重复值定义**：followup 防御

### 方案对比

| 方案 | insert | kLargest | 适用场景 |
|---|---|---|---|
| size-$k$ 最小堆 | $O(\\log k)$ | $O(1)$ | **$k$ 固定**，首选 |
| 无序数组 + QuickSelect | $O(1)$ | $O(n)$ avg | insert 远多于 query |
| 排序数组 / SkipList | $O(n)$ / $O(\\log n)$ | $O(1)$ | query 远多于 insert |
| 平衡 BST + 子树 size (Order Statistic Tree) | $O(\\log n)$ | $O(\\log n)$ | $k$ 变化，通用最优 |
| 桶 / 计数数组 | $O(1)$ | $O(\\text{range})$ | 数值有界且范围小 |

### 推荐写法

- **$k$ 固定** → size-$k$ min-heap：堆满后，新数 > 堆顶才替换；堆顶即第 $k$ 大
- **$k$ 变化** → Order Statistic Tree（或 `sortedcontainers.SortedList`）：每节点存子树 size，从 root 按 size 走到第 $k$ 个

### 代码

#### 方案 1: size-k 最小堆（k 固定首选）

```python
import heapq

class KthLargest:
    def __init__(self, k: int, nums: list[int]):
        self.k = k
        self.heap: list[int] = []
        for x in nums:
            self.add(x)

    def add(self, x: int) -> int:
        if len(self.heap) < self.k:
            heapq.heappush(self.heap, x)
        elif x > self.heap[0]:
            heapq.heapreplace(self.heap, x)
        return self.heap[0]   # 堆顶即第 k 大
```

`insert` $O(\\log k)$，`kLargest` $O(1)$。这就是 LC 703。

#### 方案 2: SortedList (k 变化, Python 实战首选)

```python
from sortedcontainers import SortedList

class TopK:
    def __init__(self):
        self.s = SortedList()

    def insert(self, x: int) -> None:
        self.s.add(x)                       # O(log n)

    def k_largest(self, k: int) -> int:
        return self.s[-k]                   # O(log n)
```

`SortedList` 内部是平衡 BST 风格的有序序列, 索引访问 $O(\\log n)$。手撸 OST
要给 BST 每节点带 `size` 字段, 走到第 $k$ 个; 面试讲思路就够, 真要写选
SortedList。

### Followup 方向

- **删除**：堆不擅长 → 转 BST / 双 heap + lazy deletion
- **海量流**：reservoir sampling、approximate quantile (t-digest)
- **分布式**：各节点局部 top-$k$ → merge
- **多 $k$ 同时查询**：必须用 sorted / OST，不能用 size-$k$ heap

### 复杂度速查

| 写法 | insert | kLargest | 备注 |
|---|---|---|---|
| size-$k$ heap | $O(\\log k)$ | $O(1)$ | $k$ 固定 |
| QuickSelect on array | $O(1)$ | $O(n)$ avg / $O(n^2)$ worst | 不稳, 面试少推 |
| SortedList / OST | $O(\\log n)$ | $O(\\log n)$ | $k$ 可变, 通用最优 |
| 桶 | $O(1)$ | $O(\\text{range})$ | 值域小且有界 |

### 一句话总结

先问 $k$ 是否固定: 固定 → size-$k$ heap; 变化 → SortedList / OST。其余维度
(insert/query 比、值域、删除、分布式) 是次级 tiebreaker, 大方向不会偏。
"""


PROBLEM_SPEC: dict = {
    "title": TITLE,
    "leetcode_id": None,
    "url": None,
    "difficulty": "medium",
    "tags": ["design", "heap", "ordered-set", "methodology"],
    "pattern": "heap-vs-bst-vs-bucket",
    "family": "design",
    "category": None,
    "source": SOURCE_LABEL,
    "company_tags": COMPANY_TAGS,
    "is_completed": 1,
    "description": DESCRIPTION,
    "notes": NOTES,
}


def _select_existing(
    conn: sqlite3.Connection, title: str
) -> tuple[int, dict] | None:
    """Return (id, current_row) for the row matching title, else None."""
    row = conn.execute(
        "SELECT id, leetcode_id, url, difficulty, tags, pattern, family, "
        "       category, source, company_tags, is_completed, "
        "       description, notes "
        "FROM problems WHERE title = ?",
        (title,),
    ).fetchone()
    if row is None:
        return None
    keys = [
        "id", "leetcode_id", "url", "difficulty", "tags", "pattern", "family",
        "category", "source", "company_tags", "is_completed",
        "description", "notes",
    ]
    return int(row[0]), dict(zip(keys, row, strict=True))


def _normalize(spec: dict) -> dict:
    """Normalize spec into the comparable storage form (lists -> JSON strings)."""
    out = dict(spec)
    out["tags"] = json.dumps(spec["tags"], ensure_ascii=False)
    out["company_tags"] = json.dumps(spec["company_tags"], ensure_ascii=False)
    return out


def upsert_problem(conn: sqlite3.Connection, spec: dict) -> tuple[int, str]:
    """INSERT-or-UPDATE the problem row by title. Return (id, action)."""
    norm = _normalize(spec)
    existing = _select_existing(conn, spec["title"])

    if existing is None:
        cur = conn.execute(
            "INSERT INTO problems "
            "(leetcode_id, title, url, difficulty, tags, pattern, family, "
            " category, source, company_tags, is_completed, "
            " description, notes, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
            "        CURRENT_TIMESTAMP)",
            (
                norm["leetcode_id"], spec["title"], norm["url"],
                norm["difficulty"], norm["tags"], norm["pattern"],
                norm["family"], norm["category"], norm["source"],
                norm["company_tags"], norm["is_completed"],
                norm["description"], norm["notes"],
            ),
        )
        return int(cur.lastrowid), "INSERTED"

    pid, current = existing
    fields_to_check = [
        "leetcode_id", "url", "difficulty", "tags", "pattern", "family",
        "category", "source", "company_tags", "is_completed",
        "description", "notes",
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
    """Insert-or-update the K-th Largest methodology problem. Return 0 on success."""
    if not DB_PATH.exists():
        print(f"[FAIL] db missing at {DB_PATH}", file=sys.stderr)
        return 1

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.with_suffix(f".db.bak.{ts}_pre_kth_largest_method")
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
