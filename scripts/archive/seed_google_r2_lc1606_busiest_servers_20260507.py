"""Seed Google R2 Coding problem: LC 1606 Find Servers That Handled Most Number of Requests.

User-provided solution (Discord 2026-05-07 msg 1501791307402838107). LC 1606
row does not exist in problems (unlike LC 450/289/1882, which were in the bulk
LC import). This seed INSERTs (or, on re-run, UPDATEs) the row by canonical
key leetcode_id=1606. Sets family='heap', pattern='circular-allocation-heap'
(distinct from LC 1882's 'two-heap-simulation' -- LC 1606's twist is the ring
allocation, solved either via SortedList + bisect-with-wraparound or via the
single-heap offset-encoding trick that converts the ring to a flat min-heap).

Solution preserves the user's two-method exposition verbatim:

  - Method 1: SortedList of free + min-heap of busy. bisect_left(target);
    if j == len(free) wrap to free[0]. Direct, third-party-lib dependent.
  - Method 2: single min-heap with encoded value `i + (idx-i) % k`. Pop top,
    `% k` to recover idx. Correctness via the sliding-window invariant: the
    heap always contains values in [i, i+k-1] when processing request i.
    Pure stdlib, shorter, but requires the invariant proof to trust.

Per `feedback_pinterest_two_tier_notes`: per-problem note in `problems.notes`,
ProblemDrawer renders via `db://<id>`. The R2 Coding Index doc 92 is updated
separately by re-running `scripts/seed_google_r2_coding_index_20260502.py`,
extended in this commit to add an LC 1606 entry under the existing
`### Heap / Simulation` section (above LC 1882 -- LC number order, also
foundational ring-allocation precedes advanced event-driven).

Idempotent. leetcode_id=1606 is the canonical key. First run on missing row:
1 INSERT. Re-run on identical state: 0 writes. Per Invariant 3 (CLAUDE.md),
this seed is the sole sanctioned write path for this row.

Run: python scripts/seed_google_r2_lc1606_busiest_servers_20260507.py
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

LEETCODE_ID = 1606
TITLE = "Find Servers That Handled Most Number of Requests"
URL = "https://leetcode.com/problems/find-servers-that-handled-most-number-of-requests/"
SOURCE_LABEL = "Google R2 2026-05"

# Fresh row -- Google is the only currently-known company tag. Later seeds may
# union in others; that union is the sibling seed's responsibility.
COMPANY_TAGS = ["Google"]

NOTES = """\
## LC 1606. Find Servers That Handled Most Number of Requests

### 题意速览

`k` 台服务器编号 `0 ~ k-1`。第 `i` 个请求在 `arrival[i]` 到达, 处理需要 `load[i]` 时间。分配规则:

- 首选 `i % k` 号服务器;
- 若忙, **顺时针**找下一个空闲的;
- 一圈都没有就丢弃。

求处理请求数最多的服务器编号。

核心瓶颈是: **怎么快速找到"≥ target 的最小空闲编号, 找不到就回卷到最小空闲编号"**。朴素 `for j in range(k)` 是 `O(k)`, n、k 都到 1e5 时必然 TLE。

下面给出两种 `O(n log k)` 写法。

---

### 方法一: `SortedList` + 堆

维护两个结构:

- `free`: 空闲服务器编号的有序集合 (`SortedList`)
- `busy`: `(endTime, idx)` 的最小堆, 到期就把 `idx` 加回 `free`

每次请求用 `bisect_left(target)` 在 `free` 上做二分; 落到末尾就回卷到 `free[0]`。

```python
from sortedcontainers import SortedList
import heapq
from typing import List

class Solution:
    def busiestServers(self, k: int, arrival: List[int], load: List[int]) -> List[int]:
        free = SortedList(range(k))
        busy = []                    # (endTime, idx)
        cnt = [0] * k

        for i, (t, l) in enumerate(zip(arrival, load)):
            while busy and busy[0][0] <= t:
                _, idx = heapq.heappop(busy)
                free.add(idx)

            if not free:
                continue

            target = i % k
            j = free.bisect_left(target)
            if j == len(free):       # 回卷
                j = 0
            idx = free[j]

            free.remove(idx)
            heapq.heappush(busy, (t + l, idx))
            cnt[idx] += 1

        mx = max(cnt)
        return [i for i, c in enumerate(cnt) if c == mx]
```

**复杂度**: 时间 `O(n log k)`, 空间 `O(k)`。

**优点**: 思路直白, 把"环形找下一个空闲"映射成"在有序集合上二分 + 回卷"。
**缺点**: 依赖第三方库 `sortedcontainers`, 竞赛环境不一定可用。

---

### 方法二: 单个最小堆 + 编码技巧

只用 `heapq`, 比上面更短。把空闲服务器入堆时, **不存编号本身, 存"它最迟会在哪个请求被首选"**:

$$
\\text{code} = i + (idx - i) \\bmod k
$$

这个值落在 `[i, i+k-1]` 区间内, 且 `code % k == idx`。**code 越小 ⇔ 顺时针离 `i%k` 越近**。

```python
import heapq
from typing import List

class Solution:
    def busiestServers(self, k: int, arrival: List[int], load: List[int]) -> List[int]:
        free = list(range(k))        # 初始所有 server 空闲, 编号即编码
        busy = []
        cnt = [0] * k

        for i, (t, l) in enumerate(zip(arrival, load)):
            while busy and busy[0][0] <= t:
                _, idx = heapq.heappop(busy)
                heapq.heappush(free, i + (idx - i) % k)

            if free:
                idx = heapq.heappop(free) % k
                cnt[idx] += 1
                heapq.heappush(busy, (t + l, idx))

        mx = max(cnt)
        return [i for i, c in enumerate(cnt) if c == mx]
```

#### 为什么直接弹堆顶就对？

关键不变量: **处理请求 `i` 之前, free 堆里所有编码都落在窗口 `[i, i+k-1]` 内**。

简要归纳:

1. 入堆时编码 = `i + (idx-i)%k ∈ [i, i+k-1]`, 下界 ≥ `i`。
2. 窗口长度恰好是 `k`, 且每个 `idx` 在窗口内对应唯一编码, 所以堆里至多 `k` 个互不相同的值。
3. 处理完请求 `i` 后:
   - 若 `i%k` 空闲, 它的编码恰为 `i` (窗口左端), 是堆顶被弹出, 剩余 ⊂ `[i+1, i+k-1]`;
   - 若 `i%k` 忙, 堆里本就没有 `i`, 剩余仍 ⊂ `[i+1, i+k-1]`。

   两种情况下, 窗口都自动滑到 `[i+1, i+k]`, 正好接上下一个请求。

因此堆顶就是当前请求视角下"顺时针最近的空闲 server", 弹出 `% k` 还原编号即可。

#### 关于 Python 的取模

代码里 `(idx - i) % k` 在 `idx < i` 时是负数取模。Python 的 `%` 总是返回非负值, 结果落在 `[0, k-1]`, 符合需要。**移植到 C++/Java/Go 等语言要写成 `((idx - i) % k + k) % k`**, 否则会得到负的偏移量。

#### "提前被消费" 怎么办

编码代表"假设没人抢, 最迟在请求 `code` 被用"。但实际上, 如果某个请求 `j < code` 时它是堆里最小的, 就会**提前**被使用 -- 这并不破坏正确性, 因为不变量保证: 从 `j` 的视角看, 它仍然是最近的空闲 server, 本来就该被选。

**复杂度**: 时间 `O(n log k)`, 空间 `O(k)`, 纯标准库, 常数比 `SortedList` 还小。

---

### 总结

| 方法 | 代码量 | 依赖 | 备注 |
|---|---|---|---|
| `SortedList` + 堆 | 中 | `sortedcontainers` | 思路最直接 |
| 单堆 + 编码 | 短 | 仅 `heapq` | 需要理解滑窗不变量 |

工程/面试推荐方法一, 可读性最好; 竞赛或追求纯标准库写法用方法二。

### 易错点

- 方法二的 `(idx - i) % k` 在 Python 里负数取模返回非负值, 移植到 C++/Java/Go 须写 `((idx - i) % k + k) % k`, 否则得到负偏移量直接错。
- 方法一 `bisect_left(target)` 落到 `len(free)` 时要回卷到 `free[0]`, 别忘判 `j == len(free)`; 否则越界。
- 释放循环条件 `busy[0][0] <= t` 等号要包含, `endTime == arrival` 表示这台已经空了能接下一个。
- 方法二编码必须是 `i + (idx - i) % k`, 不是 `i + idx % k` 也不是 `(idx - i) % k`; 三者只有第一个能维持滑窗不变量 (下界 ≥ i + 唯一性 + `% k` 还原)。
- 朴素 `for j in range(k)` 找空闲在 `n,k=1e5` 时 `O(nk)=1e10` 必 TLE; 必须 `O(log k)` 找空闲。
- 题目要的是**处理最多请求**的 server (可能多个并列), 返回的是 idx 列表; 别只返回 `argmax(cnt)`。

### 一句话总结

环形找下一个空闲服务器: 方法一 `SortedList` + bisect 加回卷, 方法二把 idx 编码成 `i + (idx - i) % k` 后单堆 pop 即得 -- 滑窗不变量保证堆顶就是顺时针最近的空闲。
"""


PROBLEM_SPEC: dict = {
    "leetcode_id": LEETCODE_ID,
    "title": TITLE,
    "url": URL,
    "difficulty": "hard",
    "tags": ["heap", "simulation", "priority-queue", "binary-search", "circular"],
    "pattern": "circular-allocation-heap",
    "family": "heap",
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


def _merge_company_tags(current_json: str | None, target_list: list[str]) -> str:
    """Union target into existing JSON-encoded company_tags list, preserving order.

    Existing entries first (preserves their order); new entries from target appended.
    """
    cur = json.loads(current_json) if current_json else []
    for tag in target_list:
        if tag not in cur:
            cur.append(tag)
    return json.dumps(cur, ensure_ascii=False)


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
    # On UPDATE path, do NOT clobber existing company_tags -- merge instead.
    merged_company_tags = _merge_company_tags(
        current.get("company_tags"), spec["company_tags"]
    )
    fields_to_check = [
        "title", "url", "difficulty", "tags", "pattern", "family",
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
    """Insert-or-update LC 1606. Return 0 on success."""
    if not DB_PATH.exists():
        print(f"[FAIL] db missing at {DB_PATH}", file=sys.stderr)
        return 1

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.with_suffix(f".db.bak.{ts}_pre_lc1606_busiest_servers")
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
