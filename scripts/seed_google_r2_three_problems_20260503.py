"""Seed 3 Google R2 Coding interview problems (T-P1-718).

User's R2 interview (2026-05-03) -- 3 problems, polished to the minimal
3-section style (思路 / 代码 / 复杂度) matching the user's golden example
(LC 2337 from the same R2):

  1. Gold Chain 平分              (custom; prefix-sum + binary-search)
  2. 等值端点最大子数组和         (custom; prefix-sum + group-by-value)
  3. LC 2337. Move Pieces to Obtain a String   (string + two-pointers)

Two artefacts:
  * problems table: 3 rows. Per `feedback_pinterest_two_tier_notes`, the
    canonical home of the per-problem note is `problems.notes` -- the
    ProblemDrawer renders this when the user opens a `db://<id>` link.
  * doc 92 `[Google] R2 Coding Index` -- updated by re-running
    `seed_google_r2_coding_index_20260502.py` (which now references the 3
    new problems by title, so the order of script runs does not matter as
    long as both run).

Idempotency:
  * Matched by `title` (canonical key for custom problems per CLAUDE.md
    `Idempotent seed pattern per row type`). If a row exists, UPDATE only
    when any field differs; otherwise UNCHANGED. content_hash on `notes`
    drives the change-detection.
  * First clean run: 3 INSERTs. Second run on same content: 0 writes.

Invariant 3: this is the sole sanctioned write path for these 3 rows; no
ad-hoc SQL.

Run: python scripts/seed_google_r2_three_problems_20260503.py
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

SOURCE_LABEL = "Google R2 2026-05"
COMPANY_TAGS = ["Google"]


def _sha256(s: str) -> str:
    """Return hex sha256 of UTF-8 encoding of s."""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------
# Problem 1 -- Gold Chain 平分
# --------------------------------------------------------------------------

GOLD_CHAIN_TITLE = "Gold Chain 平分"
GOLD_CHAIN_DESCRIPTION = """\
给定数组 $a[0..n-1]$ 表示金链每节重量（正整数）。操作：

1. 移除一节 $a[i]$
2. 剩下两截按原顺序拼成 $[a[0..i-1], a[i+1..n-1]]$
3. 在拼接链上切一刀分成两段连续子数组，使两段重量相等

存在这样的 $(i, \\text{cut})$ 时 return True，否则 False。

Followup：返回所有可行的 (移除位置, 切割位置) 方案。

来源: Google R2 Coding 2026-05 真题。
"""

GOLD_CHAIN_NOTES = """\
## Gold Chain 平分

### 思路

设前缀和 $P[k] = a[0] + \\dots + a[k-1]$，$S = P[n]$。移除 $a[i]$ 后每段应为 $T = (S - a[i]) / 2$。

切割位置相对于移除点 $i$ 分两种：

- **切在 $i$ 左边**：左段 $a[0..j]$，需 $P[j+1] = T$，$j+1 \\in [1, i]$
- **切在 $i$ 右边**：左段跨过移除点，需 $P[j+1] - a[i] = T$，即 $P[j+1] = T + a[i]$，$j+1 \\in [i+2, n-1]$

权重为正所以 $P$ 严格递增，每个 target 在 $P$ 中至多一个位置，二分查找即可。

### 代码

```python
from bisect import bisect_left

def can_split(a: list[int]) -> bool:
    n, S = len(a), sum(a)
    P = [0] * (n + 1)
    for k in range(n):
        P[k + 1] = P[k] + a[k]

    def find(target: int, lo: int, hi: int) -> bool:
        idx = bisect_left(P, target, lo, hi + 1)
        return idx <= hi and P[idx] == target

    for i in range(n):
        if (S - a[i]) % 2:
            continue
        T = (S - a[i]) // 2
        if i >= 1 and find(T, 1, i):
            return True
        if i + 2 <= n - 1 and find(T + a[i], i + 2, n - 1):
            return True
    return False
```

### Followup：返回所有方案

```python
def all_splits(a: list[int]) -> list[tuple[int, int]]:
    \"\"\"返回所有 (remove_idx, cut_idx)，cut_idx 是拼接后左段最后一节在原数组中的下标。\"\"\"
    n, S = len(a), sum(a)
    P = [0] * (n + 1)
    for k in range(n):
        P[k + 1] = P[k] + a[k]

    def find(target: int, lo: int, hi: int) -> int:
        idx = bisect_left(P, target, lo, hi + 1)
        return idx if idx <= hi and P[idx] == target else -1

    res = []
    for i in range(n):
        if (S - a[i]) % 2:
            continue
        T = (S - a[i]) // 2
        if i >= 1:
            idx = find(T, 1, i)
            if idx != -1:
                res.append((i, idx - 1))
        if i + 2 <= n - 1:
            idx = find(T + a[i], i + 2, n - 1)
            if idx != -1:
                res.append((i, idx - 1))
    return res
```

### 复杂度

- 时间 $O(n \\log n)$，二分 $n$ 次
- 空间 $O(n)$，前缀和数组
- 把 $P$ 存进 `value -> index` 哈希表可降到 $O(n)$
"""


# --------------------------------------------------------------------------
# Problem 2 -- 等值端点最大子数组和
# --------------------------------------------------------------------------

EQ_ENDPOINT_TITLE = "等值端点最大子数组和"
EQ_ENDPOINT_DESCRIPTION = """\
给定数组 $a[0..n-1]$（可正可负），找一对下标 $(i, j)$ 满足：

- $0 \\le i \\le j \\le n - 1$
- $a[i] = a[j]$
- $a[i] + a[i+1] + \\dots + a[j]$ 最大

返回取到最大和的 $(i, j)$。$i = j$ 合法（此时和就是 $a[i]$）。

Followup：严格 $O(1)$ 额外空间，时间复杂度可以放宽。

来源: Google R2 Coding 2026-05 真题（followup 现场未及做出，下方补完）。
"""

EQ_ENDPOINT_NOTES = """\
## 等值端点最大子数组和

### 思路

前缀和 $P[k] = \\sum_{t<k} a[t]$，则 $\\sum a[i..j] = P[j+1] - P[i]$。在 $a[i] = a[j]$ 且 $i \\le j$ 的约束下最大化 $P[j+1] - P[i]$。

按值分组：固定值 $v$，它在数组里的下标是 $p_1 < p_2 < \\dots$。在这些位置中挑 $i \\le j$ 使 $P[j+1] - P[i]$ 最大，等价于"扫到 $j$ 时取所有先前 $a[i] = v$ 中 $P[i]$ 最小的"。每个 $v$ 的最小 $P[i]$ 互不相关，一次外层扫描就够。

**边界**：先把当前位置并入 `min_prefix[v]` 再算候选，这样首次出现时 `min_prefix[v] = P[j]`，候选 $= P[j+1] - P[j] = a[j]$，正好覆盖 $i = j$ 的单元素情况。

### 代码

```python
def best_pair(a: list[int]) -> tuple[tuple[int, int], int]:
    n = len(a)
    P_j = 0
    min_prefix: dict[int, int] = {}   # v -> 最小 P[i]，其中 a[i] = v
    arg_min: dict[int, int] = {}      # v -> 对应的 i
    best_sum = float('-inf')
    best_ij = (-1, -1)

    for j in range(n):
        v = a[j]
        # 1) 先把当前位置并入（覆盖 i == j）
        if v not in min_prefix or P_j < min_prefix[v]:
            min_prefix[v] = P_j
            arg_min[v] = j
        # 2) 计算以 j 为右端点的候选
        P_j1 = P_j + a[j]
        cand = P_j1 - min_prefix[v]
        if cand > best_sum:
            best_sum = cand
            best_ij = (arg_min[v], j)
        P_j = P_j1
    return best_ij, best_sum
```

时间 $O(n)$，空间 $O(\\text{distinct values})$。

### Followup：$O(1)$ 额外空间

没有哈希表就退回双层循环：外层固定 $i$，内层 $j$ 用 `run` 累加 $a[i..j]$，遇 $a[j] = a[i]$ 时更新答案。

```python
def best_pair_o1(a: list[int]) -> tuple[tuple[int, int], int]:
    n = len(a)
    best_sum = float('-inf')
    best_ij = (-1, -1)
    for i in range(n):
        run = 0
        for j in range(i, n):
            run += a[j]
            if a[j] == a[i] and run > best_sum:
                best_sum = run
                best_ij = (i, j)
    return best_ij, best_sum
```

**为什么不能 Kadane 式"负了就丢弃"**：外层钉死了 $i$，内层中途 $run$ 变负不能重置——重置就等于换 $i$，违反外层约束。后面可能还有 $a[j] = a[i]$ 要等，所以 $run$ 必须带着负值继续走。要真做"丢弃"得改成"枚举值 $v$"：让重置后的起点仍满足 $a[\\text{起点}] = v$，时间 $O(V \\cdot n)$，空间仍 $O(1)$；值域 $V$ 小才比 $O(n^2)$ 好。

值域无界 + 严格 $O(1)$ 空间下我想不到能严格优于 $O(n^2)$ 的通用做法——排序 / 哈希都要额外空间。面试讲清 $O(n^2) / O(1)$，再补一句"值域小可改 $O(V \\cdot n)$"就到位了。

### 复杂度

- 主解：时间 $O(n)$，空间 $O(\\text{distinct values}) \\le O(n)$
- Followup：时间 $O(n^2)$，空间 $O(1)$
"""


# --------------------------------------------------------------------------
# Problem 3 -- LC 2337
# --------------------------------------------------------------------------

LC2337_TITLE = "Move Pieces to Obtain a String"
LC2337_LEETCODE_ID = 2337
LC2337_URL = "https://leetcode.com/problems/move-pieces-to-obtain-a-string/"
LC2337_DESCRIPTION = """\
给定两个字符串 `start` 和 `target`，长度相同，仅由 `'L'`、`'R'`、`'_'` 组成：

- `'L'` 只能向左移动到相邻的 `'_'`
- `'R'` 只能向右移动到相邻的 `'_'`
- 不能跨过其他字母

判断能否通过若干次移动使 `start` 变成 `target`。

来源: Google R2 Coding 2026-05；LeetCode 2337（Medium）。
"""

LC2337_NOTES = """\
## 2337. Move Pieces to Obtain a String

### 思路

观察 L、R 的运动规则：

- L 只能向左移动，R 只能向右移动
- 两者都不能穿过对方

所以把 `start` 和 `target` 中所有非 `_` 字符按顺序抽出来，必须满足：

1. 字母序列完全相同（数量、种类、相对顺序）——谁也不能越过谁
2. 对每对相对应的字母：
   - L：在 `start` 中的下标 $i \\ge$ 在 `target` 中的下标 $j$（只能左移，所以原位置不能在目标左边）
   - R：在 `start` 中的下标 $i \\le$ 在 `target` 中的下标 $j$（只能右移）

满足以上条件即可返回 true。

### 代码

```python
class Solution:
    def canChange(self, start: str, target: str) -> bool:
        a = [(v, i) for i, v in enumerate(start)  if v != '_']
        b = [(v, i) for i, v in enumerate(target) if v != '_']
        if len(a) != len(b):
            return False
        for (c, i), (d, j) in zip(a, b):
            if c != d:                       # 字母对不上
                return False
            if c == 'L' and i < j:           # L 不能右移
                return False
            if c == 'R' and i > j:           # R 不能左移
                return False
        return True
```

### 复杂度

- 时间 $O(n)$，一次遍历提取字母及下标，再一次遍历比较
- 空间 $O(n)$，存放抽出的字母与下标
"""


# --------------------------------------------------------------------------
# Per-row spec
# --------------------------------------------------------------------------

PROBLEMS_SPEC: list[dict] = [
    {
        "title": GOLD_CHAIN_TITLE,
        "leetcode_id": None,
        "url": None,
        "difficulty": "medium",
        "tags": ["array", "prefix-sum", "binary-search"],
        "pattern": "prefix-sum",
        "family": "prefix-sum",
        "category": None,
        "source": SOURCE_LABEL,
        "company_tags": COMPANY_TAGS,
        "is_completed": 1,
        "description": GOLD_CHAIN_DESCRIPTION,
        "notes": GOLD_CHAIN_NOTES,
    },
    {
        "title": EQ_ENDPOINT_TITLE,
        "leetcode_id": None,
        "url": None,
        "difficulty": "medium",
        "tags": ["array", "prefix-sum", "hash-map"],
        "pattern": "prefix-sum",
        "family": "prefix-sum",
        "category": None,
        "source": SOURCE_LABEL,
        "company_tags": COMPANY_TAGS,
        "is_completed": 1,
        "description": EQ_ENDPOINT_DESCRIPTION,
        "notes": EQ_ENDPOINT_NOTES,
    },
    {
        "title": LC2337_TITLE,
        "leetcode_id": LC2337_LEETCODE_ID,
        "url": LC2337_URL,
        "difficulty": "medium",
        "tags": ["string", "two-pointers"],
        "pattern": "two-pointers",
        "family": "two-pointers",
        "category": None,
        "source": SOURCE_LABEL,
        "company_tags": COMPANY_TAGS,
        "is_completed": 1,
        "description": LC2337_DESCRIPTION,
        "notes": LC2337_NOTES,
    },
]


# --------------------------------------------------------------------------
# Upsert logic
# --------------------------------------------------------------------------


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
    """Insert-or-update the 3 R2 problems. Return 0 on success."""
    if not DB_PATH.exists():
        print(f"[FAIL] db missing at {DB_PATH}", file=sys.stderr)
        return 1

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.with_suffix(f".db.bak.{ts}_pre_google_r2_3p")
    shutil.copy2(DB_PATH, backup_path)
    print(f"[BACKUP] {backup_path.name}")

    with sqlite3.connect(str(DB_PATH)) as conn:
        results: list[tuple[int, str, str]] = []
        for spec in PROBLEMS_SPEC:
            pid, action = upsert_problem(conn, spec)
            results.append((pid, action, spec["title"]))
            print(f"[{action}] problems.id={pid} title={spec['title']!r}")
        conn.commit()

    print(
        "[OK] done -- next: re-run "
        "scripts/seed_google_r2_coding_index_20260502.py "
        "to refresh doc 92 index"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
