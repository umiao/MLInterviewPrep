"""Seed LC 3859 -- 统计包含 K 个不同整数的子数组 (双条件容斥滑窗).

User-provided solution writeup for LC 3859 (leetcode.cn weekly contest problem):
count subarrays with exactly k distinct integers AND each distinct integer
appears at least m times. Solved by inclusion-exclusion of two "atLeast"
sliding-window counts: atLeast(k, k) - atLeast(k+1, k).

Two artefacts:
  * problems table: 1 row keyed by leetcode_id=3859 (canonical key per
    CLAUDE.md `Idempotent seed pattern per row type`). Notes carry the full
    user writeup verbatim (思路 / 滑窗模板 / 代码 / 复杂度 / 命名小笔记 /
    同类题). Family + pattern = 'sliding-window'.
  * doc 92 `[Google] R2 Coding Index` -- updated by re-running
    `seed_google_r2_coding_index_20260502.py` (which now references this
    problem by leetcode_id, so order does not matter as long as both run).

Idempotency: matched by leetcode_id. UPDATE only when any field differs;
otherwise UNCHANGED. Re-running on the same content => 0 writes.

Invariant 3: this is the sole sanctioned write path for the LC 3859 row;
no ad-hoc SQL.

Run:
    python scripts/seed_google_lc3859_count_subarrays_kdistinct.py
    python scripts/seed_google_r2_coding_index_20260502.py
"""
from __future__ import annotations

import io
import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

# Windows cp1252 stdout chokes on the CJK title in our [INSERTED] log line.
# Re-wrap stdout/stderr as UTF-8 so the script runs on bare Windows shells.
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

LC_ID = 3859
TITLE = "统计包含 K 个不同整数的子数组"
URL = None  # leetcode.cn slug not confirmed; user can fill in later
SOURCE_LABEL = "Google R2 Custom Note 2026-05"
COMPANY_TAGS = ["Google"]

DESCRIPTION = """\
给定整数数组 `nums` 和两个整数 `k`、`m`，统计满足以下条件的连续子数组个数：

- 子数组中**恰好**包含 $k$ 个不同的整数
- 这 $k$ 个不同整数中的**每一个**都至少出现 $m$ 次

返回这样的子数组数量。

来源: leetcode.cn 周赛题（编号 3859）；Google R2 R2 Coding 自建扩展笔记
（同类题：LC 992 K 个不同整数的子数组、LC 2962 max 元素至少 K 次）。
"""

NOTES = """\
## 3859. 统计包含 K 个不同整数的子数组

### 思路

**恰好难求，转成两个"至少"作差。**

设 `atLeast(minDistinct, minFreqGeM)` = 至少 `minDistinct` 个不同元素、且其中至少 `minFreqGeM` 个出现 ≥ m 次的子数组数。

$$
\\text{答案} = \\text{atLeast}(k,\\ k) - \\text{atLeast}(k+1,\\ k)
$$

**注意第二个参数都是 k，不是 k+1**：差集是"恰好 k 个不同"，此时"至少 k 个 ≥m 次"等价于"全部 ≥m 次"，正好对上题意。如果第二个参数也写成 k+1，会把"k+1 个不同但只有 k 个 ≥m 次"这种本不该计入的情况留在结果里。

### 滑窗模板（至少 + 计数）

1. **进窗**：更新 `freq` 和 `numFreqGeM`
2. **缩窗到不满足**：`while` 内只移动 `left`，**不**在里面计数
3. **`ans += left`**：写在 `while` 外。利用单调性——更长的窗口必然更满足"至少"，所以 `[0, right], …, [left-1, right]` 全部合法，一次性加 `left` 个

### 代码

```python
from collections import defaultdict

class Solution:
    def countSubarrays(self, nums: list[int], k: int, m: int) -> int:
        # 至少 minDistinct 个不同元素，且其中至少 minFreqGeM 个出现 >= m 次
        def atLeast(minDistinct: int, minFreqGeM: int) -> int:
            freq = defaultdict(int)
            numFreqGeM = 0          # 窗口中出现次数 >= m 的元素个数
            left = 0
            ans = 0

            for right, x in enumerate(nums):
                # 1. 进窗
                freq[x] += 1
                if freq[x] == m:
                    numFreqGeM += 1

                # 2. 缩窗到刚好不满足
                while len(freq) >= minDistinct and numFreqGeM >= minFreqGeM:
                    out = nums[left]
                    freq[out] -= 1
                    if freq[out] == m - 1:    # 跨过 m 这条线
                        numFreqGeM -= 1
                    if freq[out] == 0:
                        del freq[out]
                    left += 1

                # 3. 单调性：[0..left-1] 这 left 个左端点的窗口都合法
                ans += left

            return ans

        # 容斥：恰好 k 不同 = 至少 k 不同 - 至少 k+1 不同
        return atLeast(k, k) - atLeast(k + 1, k)
```

### 复杂度

- **时间**：$O(n)$。每个元素至多进窗、出窗各一次，两次 `atLeast` 调用都是 $O(n)$。
- **空间**：$O(n)$。`freq` 最多存 $n$ 个不同元素。

### 命名小笔记

| 原命名 | 改后 | 理由 |
|---|---|---|
| `counterDict` | `freq` | 字典做计数器是默认场景，`Dict` 后缀冗余 |
| `satisfiedCount` | `numFreqGeM` | 直接说明"freq ≥ m 的元素**个数**"，不易和 sat-count（满足总数）混淆 |
| `A` | `atLeast` | 单字母函数名在归档代码里基本不可读 |
| `uniqueCountReq` / `satisfiedCountReq` | `minDistinct` / `minFreqGeM` | "Req"对调用方信息量低；`min*` 和函数名 `atLeast` 语义对齐 |
| `ret` | `ans` | Python 习惯里 `ans` 表"答案"，`ret` 是 C/Java 风格 |

### 同类题（按难度递进）

- [LC 2962. 统计最大元素出现至少 K 次的子数组](https://leetcode.cn/problems/count-subarrays-where-max-element-appears-at-least-k-times/) —— 单条件入门版
- [LC 992. K 个不同整数的子数组](https://leetcode.cn/problems/subarrays-with-k-different-integers/) —— "恰好 = 至少差分"的最经典题
- 本题（LC 3859） —— 双条件容斥 + 滑窗
"""

PROBLEM_SPEC: dict = {
    "leetcode_id": LC_ID,
    "title": TITLE,
    "url": URL,
    "difficulty": "medium",
    "tags": ["array", "sliding-window", "hash-map", "inclusion-exclusion"],
    "pattern": "sliding-window",
    "family": "sliding-window",
    "category": None,
    "source": SOURCE_LABEL,
    "company_tags": COMPANY_TAGS,
    "is_completed": 1,
    "description": DESCRIPTION,
    "notes": NOTES,
}


def _select_existing(
    conn: sqlite3.Connection, leetcode_id: int
) -> tuple[int, dict] | None:
    """Return (id, current_row) for the row matching leetcode_id, else None."""
    row = conn.execute(
        "SELECT id, leetcode_id, title, url, difficulty, tags, pattern, "
        "       family, category, source, company_tags, is_completed, "
        "       description, notes "
        "FROM problems WHERE leetcode_id = ?",
        (leetcode_id,),
    ).fetchone()
    if row is None:
        return None
    keys = [
        "id", "leetcode_id", "title", "url", "difficulty", "tags", "pattern",
        "family", "category", "source", "company_tags", "is_completed",
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
    """INSERT-or-UPDATE the problem row by leetcode_id. Return (id, action)."""
    norm = _normalize(spec)
    existing = _select_existing(conn, spec["leetcode_id"])

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
        "title", "url", "difficulty", "tags", "pattern", "family",
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
    """Insert-or-update LC 3859. Return 0 on success."""
    if not DB_PATH.exists():
        print(f"[FAIL] db missing at {DB_PATH}", file=sys.stderr)
        return 1

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.with_suffix(f".db.bak.{ts}_pre_lc3859")
    shutil.copy2(DB_PATH, backup_path)
    print(f"[BACKUP] {backup_path.name}")

    with sqlite3.connect(str(DB_PATH)) as conn:
        pid, action = upsert_problem(conn, PROBLEM_SPEC)
        print(
            f"[{action}] problems.id={pid} leetcode_id={LC_ID} "
            f"title={TITLE!r}"
        )
        conn.commit()

    print(
        "[OK] done -- next: re-run "
        "scripts/seed_google_r2_coding_index_20260502.py "
        "to refresh doc 92 with the LC 3859 entry"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
